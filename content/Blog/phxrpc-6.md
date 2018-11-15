Date: 2016-10-19 00:03:12
Title: 非阻塞TCP流和HttpClient - phxrpc代码阅读(6)
Tags: phxrpc
Slug: phxrpc-6

## 写在前面

其实这点东西有点鸡肋。因为TCP流在前面已经讲过，难点在于“流”和“流缓冲区”部分。而HttpClient只是TCP流的一个应用，代码不多，且重点在于HTTP协议的调教上面。

不过因为前面有写阻塞TCP流，还是前后呼应，把非阻塞TCP流也小小的讲解一下。顺便饶一段HttpClient的讲解，算是充实一下内容吧。

## 非阻塞TCP流缓冲区 - `UThreadTcpStreamBuf`

这个其实没啥可讲的，传入一个`socket`，然后读写分别调用`UThreadRecv`和`UThreadSend`，IO复用和协程切换的复杂操作都被封装在里面了。剩下的操作都由基类函数来解决。

## 非阻塞TCP流 - `UThreadTcpStream`

> 确实没啥可说的，你们自己去读代码吧。。。

非阻塞TCP流和阻塞TCP流的区别是~~它不阻塞~~，在阻塞TCP流中，我们传入的是一个TCP流，而非阻塞TCP流传入的是一个协程调度器和一个TCP流。

这个很好理解，一个阻塞流自然会占满一个线程的IO和CPU —— 在阻塞流IO读写时，CPU空闲；在CPU忙时，IO空闲。

而非阻塞流会将自己IO wait的时间托管给epoll，把剩下的时间用于CPU计算（和一些overhead上）。所以一个线程可以handle多个socket，协程调度器就是必须的了。之后的读写操作就交由我们前面讨论过的epoll和ucontext协程来共同完成了。

## HttpClient

其实这里分析HttpClient的意义不是很大，因为Http毕竟是一个成熟的协议，然后相应的设置含义虽然明确，但是放到相应的上下文中分析比较好。

这篇博文[《HTTP协议头部与Keep-Alive模式详解》][1]中有一部分背景知识，感兴趣的同学可以简单了解一下。

### 在HttpDispatcher中使用的一个小技巧

在`http_dispatcher.h`文件中，作者使用了一个比较新奇的技巧：“[Function Pointers to Member Functions][2]”。

我们来看代码：

```
typedef int (Dispatcher::*URIFunc_t)(const HttpRequest & request, HttpResponse * response);
```

这行代码的意思是，为一个参数为`(const HttpRequest&, HttpResponse*)`且返回值为`int`的函数声明一个别名`URIFunc_t`，并且这个函数，一定是`Dispatcher`类的成员函数。

到目前为止，一切都还是正常的样子，语法也是我们常见的类型。但是下面这种写法，确实是我第一次见。

```
if (uri_func_map_.end() != iter) {
    ret = (dispatcher_.*iter->second)(request, response);
}
```

这里的`(dispatcher_.*iter->second)`，`iter->second`是从map中拿出来的，在`dispatcher_`对象中的成员函数的指针。我们使用星号解引用，再把它和`dispatcher_`对象拼接在一起，像正常调用成员函数一样调用就可以了。

## 貌似写的有点少，再饶一段吧 - epoll测试服务端/客户端

我们翻篇回到`network`文件夹下面，看一下`test_epoll_[server|client].[h|cpp]`文件。

### epoll测试客户端

首先，我们读取命令行参数，新建一个调度器，由参数决定调度器的woker协程数量。之后新建`UThreadEpollArgs_t`，把调度器指针塞进去。再之后把`echoclient`工作函数和`args`参数放由调度器中进行调度。

接下来我们看看工作函数`echoclient`。

工作函数的第一步是申请一个socket fd：

```
int fd = ::socket(AF_INET, SOCK_STREAM, IPPROTO_IP);
```
这里我解释一下最后一个参数`IPPROTO_IP`：


> In the in.h file, the comment says: Dummy protocol for TCP.      
This constant has the value 0. It's actually an automatic choice depending on socket type and family.      
If you use it, and if the socket type is SOCK_STREAM and the family is AF_INET, then the protocol will automatically be TCP (exactly the same as if you'd used IPPROTO_TCP). Buf if you use IPPROTO_IP together with AF_INET and SOCK_RAW, you will have an error, because the kernel cannot choose a protocol automatically in this case.

这个参数的意义是告诉内核，如果只有一个选项的话，你特么爱用哪个协议就用哪个吧。所以有一些时候，我们会直接把最后一个参数写成0，这就是`IPPROTO_IP`宏的字面值。

更多信息，可以参考这个[问题][3]。

后面的流程非常简单，先接收server发来的欢迎信息，之后ping pong十次，发送“quit”包后结束协程。

### epoll测试服务端

服务端和客户端区别不大，主要区别在于客户端在一开始只有一个协程。之后在accept连接时，会主动新建工作协程。

这里解释一下`listen(fd, backlog)`函数的第二个参数`backlog`：

backlog意为内核为相应套接字排队的最大连接个数。内核为任何一个给定的监听套接字维护两个队列：

* 未完成连接队列(incomplete connection queue)          
已由某个客户发出并到达服务器，而服务器正在等待完成相应的TCP三路握手过程。这些套接字处于SYN_RCVD状态
* 已完成连接队列(completed connection queue)       
每个已完成TCP三路握手过程的客户对应其中一项。这些套接字处于ESTABLISHED状态

当队列满时，TCP会忽略改分节，但是不发送RST。服务端会期望客户端重发SYN，采用正常的重传机制来处理


队列的真实大小往往比设定backlog值要大一些（~1.5倍）

我们继续看工作函数`echoaccept`。第一步是新建一个`UThreadSocket_t`对象，用来监听accept事件。当有新的连接进入时，我们就将新的连接，以及连接所用的工作函数`echoserver`加入到调度器中。

`echoserver`函数首先发送一个欢迎信息，之后就和客户端打起乒乓球来，直到客户端发来quit，就结束这个工作协程。

其实这里有一个问题，如果发生了一个字符串拆成两半发的现象，比如第一个包是“blahblahquitq”，之后一个包是“uit”，那么这个协程永远就不会停止了。由于TCP是一个流协议，我们不能保证每一次recv回来的信息都是一个完整的“包”。不做不必要的假设，不给自己找麻烦。

不过因为这里ping pong的消息都比较短，可以强行认为每一个包都包含着一个完整的字符串。当然，这种假设也是无意义的。所以我们要留意phxrpc在真正的生产环境，是怎样处理这种“粘包”的问题的。

## 写在最后

上一张女神的图：

![](https://github.com/Wizmann/assets/raw/master/wizmann-pic/16-10-19/89151689.jpg)

没啦~

[1]: https://www.byvoid.com/blog/http-keep-alive-header
[2]: http://tipsandtricks.runicsoft.com/Cpp/MemberFunctionPointers.html
[3]: http://stackoverflow.com/questions/24590818/what-is-the-difference-between-ipproto-ip-and-ipproto-raw
