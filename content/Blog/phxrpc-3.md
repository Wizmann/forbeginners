Date: 2016-10-03 22:22:14
Title: 阻塞TCP流 - phxrpc代码阅读(3)
Tags: phxrpc, tcpip, poll, socket
Slug: phxrpc-3

## 写在前面

phxrpc的流（`stream`和`streambuf`）与网络访问其实是耦合在一起的，所以本文可以结合着第一篇笔记一起来看。虽然我非常想吐槽这种强耦合性的设计，但是我决定还是好好理解phxrpc的设计之后。。。攒一波大的：）

## BlockTcpStreamBuf

`class BlockTcpStreamBuf`继承自`BaseTcpStreamBuf`。其中重写了`precv`和`psend`两个函数，并且持有了一个文件描述符(file descriptor)：`socket_`。

`precv`和`psend`直接调用了`<sys/socket.h>`中的`recv(2)`和`send(2)`，并没有其它操作。

网络相关的操作，则由`class BlockTcpStream`来负责。`BlockTcpStreamBuf`只负责IO部分。

```cpp
if (BaseTcpUtils::SetNonBlock(sockfd, false)
        && BaseTcpUtils::SetNoDelay(sockfd, true)) {
    stream->Attach(sockfd);
} else {
    phxrpc::log(LOG_ERR, "set nonblock fail");
    error = -1;
    close(sockfd);
}
```

在`BlockTcpStream`把fd传递给`BlockTcpStreambuf`之前，需要把fd设置为`block`的。而这段代码最大的槽点就是这个`SetNonBlock`函数，和下面的`set nonblock fail`日志（想一想）。完全让人摸不到头脑，达到一脸懵逼的最高境界。

![](https://github.com/Wizmann/assets/raw/master/wizmann-pic/16-10-3/87163832.jpg)

由于`recv`和`send`函数是`block`的，所以在读取、写入缓冲区时，如果没有足够的数据可读或没有足够的空间可写，则读取写入操作会阻塞住。

## BlockTcpStream

在这里我又想吐个槽了，为啥在这里把TCP Server和Client的工作流混为一谈。我觉得至少应该从命名上区分一下，否则极容易误用。

### TCP的工作流程

![](https://github.com/Wizmann/assets/raw/master/wizmann-pic/16-10-3/92621506.jpg)

> 图片来源：UNIX网络编程卷一：套接字编程 4.2节

从图中我们可以看到，TCP的服务端与客户端的工作流程是不同的，相对来说，客户端的程序要简单一些。

`BlockTcpStream`中，客户端应用的函数只有`BlockTcpUtils::Open`，而服务端的`BlockTCPUtils::Listen`函数包括了`bind()`和`listen()`两个操作，而`accept()`则需要开发者手动调用。

### SO_REUSEADDR

在服务端的`Listen()`函数中，phxrpc使用了`SO_REUSEADDR`选项，这个选项的意在通知内核：如果端口忙，但是TCP状态位于`TIME_WAIT`时，可以重用端口。

一个套接字其实是一个`（协议，源地址，源端口，目标地址，目标端口）`五元组。`SO_REUSEADDR`意味着我们可以重用源地址和源端口。当然此时的风险在于如果该原套接字发送了一些错误的数据，此时我们的应用程序的TCP工作流就会产生错乱。但是由于TCP的实现中，通过随机的消息序号规避了这个问题，所以这里的风险可以忽略不计。

使用`SO_REUSEADDR`的好处是，在服务端程序崩溃和退出时（对于一般的服务端程序来说，崩溃和退出是没有区别的），可以立即重启，而不需要等待2MSL时间。

那么我们要问了，为什么在这里我们需要等待2MSL时间呢。

![](https://github.com/Wizmann/assets/raw/master/wizmann-pic/16-10-3/33186679.jpg)

> 图片来源：Effective TCP/IP 3.8节

TCP拆除连接使用了四次握手的机制，而主动关闭连接的一方在发送完最后一个ACK之后，需要等待2MSL的时间。这就是上面所说的，当服务器重启后，出现`Address already in use`的报错信息，需要额外等待大约1~4分钟的原因。

究其原因，TIME-WAIT状态的意图在于避免主动关闭连接的一端最后一个ACK发送失败。此时，主机1已经完全关闭，而主机2因为没有收到FIN包的ACK，处于半关闭状态。此时主机2向主机1发送的任何信息（如延迟的ACK包等）都只会收到RST，导致连接的异常关闭。

为了规避这个问题，主动关闭端需要等待2MSL时间。一个MSL是给最后的ACK包，而另外一个MSL，是为了等待被动关闭端重新发送FIN包。如果在TIME_WAIT期间收到了对端的数据包，会刷新TIME_WAIT状态的时间。

> 参考：Effective TCP/IP 3.8 3.9节

### IO复用：Poll

![](https://github.com/Wizmann/assets/raw/master/wizmann-pic/16-10-3/84501111.jpg)

> 图片来源：UNIX网络编程卷一：套接字编程 6.2节

IO复用是指内核在发现进程指定的一个或多个IO条件就绪，内核就通知进程。通常来讲，常用的IO复用函数有`select()`和`poll()`。

当`poll()`返回后，我们需要遍历其中的fd数组找到可操作的fd。

```cpp
struct pollfd {
   int   fd;         /* file descriptor */
   short events;     /* requested events */
   short revents;    /* returned events */
};
```

我们可以从`events`和`revents`获得该fd的状态，从而判别可读、可写、超时或出错。

在这里，我们并没有使用poll函数的IO复用能力，而是把它做为另一个阻塞IO调用来使用。

`BlockTcpUtils::Open`函数中，我们使用了poll，用来监视相应的（一个）fd是否可读。这样一来，我们就隐式（为什么说隐式呢，因为他们一不写文档，二不写注释，一切都是潜规则）规定了C/S交互的基本工作流程：当C/S连接建立后，Server端要先说话，Client端接收到消息之后，才可以进行下面的流程。

> Client：“不管你们信不信，是Server先动的手。”

具体为什么先用poll，再把fd设为`blocking`的，我表示二脸懵逼。在我的实验中，即使把poll删掉，测试代码也是可以work的。可能在后面的代码阅读中，这个问题可以获得解释吧。

和select一样，poll也存在被中断的情况，在phxrpc的代码里，我们给了中断“a second chance”。当poll被中断后，会重新再poll一次；如果这次再被中断，则直接返回TIMEOUT。

```cpp
// retry again for EINTR
for (int i = 0; i < 2; i++) {
    ret = ::poll(&pfd, 1, timeout_ms);
    if (-1 == ret && EINTR == errno)
        continue;
    break;
}

if (0 == ret)
    errno = ETIMEDOUT;
```

## 写在最后

由于这篇文章中的知识点比较杂，写作的顺序也是随机的。所以连贯性不是那么强。如果有什么问题，忍着点吧您就。

忍不了的话。。。那就留言交流吧~


![](https://github.com/Wizmann/assets/raw/master/wizmann-pic/16-10-3/42112021.jpg)
