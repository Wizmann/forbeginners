Date: 2016-10-22 23:03:36
Title: RPC - phxrpc代码阅读(7)
Tags: phxrpc, rpc
Slug: phxrpc-7

## 前言

看了这么久代码，终于我们要接近phxrpc的核心部分了。

但是出人意料的是，rpc部分并没有过多的概念和magic trick。而且因为ucontext已经被封装好了，所以在rpc里的操作，可以完全按照同步的写法来搞，开发者们不需要切换同步异步的思维模式，就可以在底层的封装之上，做自己想做的事了。

## 线程安全(?)的队列 - ThreadQueue

我不知道开发者为啥要起`ThdQueue`这样令人迷惑的名字，这种诡异的命名风格贯穿了整个代码。咋一看这个类是maintain一堆线程的，类似于线程池，但其实这个类就是一个`BlockingQueue`的实现。

之后，这个队列有三种操作，`push`、`pluck`和`break_out`。push操作不用多说，pluck对应的我们所理解的pop操作，即从队列中弹出元素（pluck这个词貌似是从grpc里面来的，那我就不吐槽了，毕竟Google爸爸）。

更令人疑惑的是`break_out`这个操作。从代码来看，像是清空队列，并且在dtor中也显式的调用了这个函数。

但是有以下的几个问题。

一，`break_out_`是一个bool变量，且在不同线程间共享，问题在于这个变量可能被cache住，直接访问可能会造成非预期的结果，可能需要`volitaile`，或者在`pluck`函数里加一个mem barrier。

二来，在析构函数中调用`break_out_`，有可能的一种情况是有其它线程还在`pluck`函数中，而`ThdQueue`对象已经被析构了，我们就需要承担这种不安全行为的后果（此处有广告：大铁棍子医院捅主任，张姐去了都说好）。

当然，如果这个函数只在结束进程时使用，其实写的糙一点也无所谓，因为毕竟线上服务是没有“退出”这种状态的。当我们要清空队列时，已经不需要对外提供服务，之后直接`kill -9`就好，不会触发多线程的坑。不过，这里我觉得应该还是要加小心。

## UThreadCaller

这个破类让我看了一小时，分析它的keepalive是怎么实现的。结果发现这个类被没有被调用。

GG。

![](https://github.com/Wizmann/assets/raw/master/wizmann-pic/16-10-22/54117736.jpg)

## 一个超级文件 - HshaServer

> 不知道为啥开发者要把这么多文件写一块，拆开不好吗？

### DataFlow

DataFlow包含了Request和Response两个Queue，还附加了入队的时间戳和一个args参数指针。

### HshaServerStat

一个统计类。会在后台新建一个线程，约每一秒打印一次统计日志。

这个类里有一个技巧，在`CallFunc()`函数中，每一秒循环一次并没有使用sleep家族的函数，也没有使用select的超时。而是使用了`condtional variable`。

`std::condition_variable::wait_for`函数，实质是就是带超时的等待。而这里，在一般状态下，是没有线程会notify的，所以wait_for函数会睡满1s。但是在退出时，会显式的notify统计线程，破坏等待状态，使统计线程退出。

`wait_for`函数的具体用法，可以参考[文档][1]。

下面的`HshaServerQos`也是一样的思路，Qos即“Quality of service”。

### Worker和WorkerPool

这两个类其实是一个和一堆的关系，不过由于这里的诡异的写法，导致一个依赖一堆，一堆调用一个。

WorkerPool是一个全局的线程池，里面有线程（废话），输入输出队列，Disipatcher和调度器。所以Worker要反过来依赖WorkerPool里面的数据。造成了很大的耦合性。

Worker从输入队列中获取信息，并且使用`dispatcher`进行CPU密集的处理（我觉得`dispatcher`这个名字起的也有问题）。之后将结果放入输出队列，由后面的`HshaServerIO::ActiveSocketFunc`驱动协程库进行之后的IO操作。

### 完成调度器 - HshaServerIO

这个类的主要作用就是补全调度器缺少的函数，并提供了一个IO的工作函数`HshaServerIO::IOFunc`。


调度器的工作流程前面已经说过了，我们现在就从更具体化的实现上来阅读一下。

`HshaServerIO :: AddAcceptedFd`，这个函数由外部调用，传入已经accept的fd，之后`HshaServerIO::HandlerAcceptedFd`将这个fd，和IO工作函数`IOFunc`一起放入调度器中进行调度。

工作函数`IOFunc`只负责将请求放入队列，而并不负责从输出队列中取出响应。这个事情由`HshaServerIO::ActiveSocketFunc`负责。

换句话说，在调度器的工作循环中，`epoll_wait`中等待的只有在进行IO的两种fd，一是读还没读完的，二是写还没写完的。

进行完CPU操作的fd，由`active_socket_func_`函数重新激活，向客户端写回响应。所以这个函数应该叫`activate_socket_with_resp_func_`更合适一些。（至少第一个单词得是个动词好不。）

后面的keepalive的处理也是非常浅显的，这里就不多说了。

### 多线程IO - HshaServerUnit和HshaServer

前面我们说了不少协程的事，但这并不代表我们不使用多线程带来的红利。或者至少在性能不符合预期的时候，用多线程来tuning一下。

HashServerUnit包装了一组线程，其中包括一个IO线程和若干CPU线程。我们在HshaServer中，还可以配置多个Unit，使得我们有多个IO线程，充分榨干CPU和IO的每一滴汗水。

由于手里也没有测试数据，也就不能更详细的来说配置服务参数的策略。但是无责任猜测，IO线程应该不超过3个。CPU线程数目应该略多于CPU核数。

### 一个独立的Acceptor

`HshaServerAcceptor`类相对比较独立，它是用来接受访问请求。是主线程的工作循环。

这里比较奇怪的是，`LoopAccept`函数设置了CPU亲和性。使得控制线程只在CPU0上运行。

```cpp
    cpu_set_t mask;
    CPU_ZERO(&mask);
    CPU_SET(0, &mask);
    pid_t thread_id = 0;
    int ret = sched_setaffinity(thread_id, sizeof(mask), &mask);
```

具体原因有待探讨，可能是和中断亲和性有关。

## 写在后面

总算囫囵吞枣的把这RPC读完了，其实这里还是有好多疑问的。但是由于phxrpc的文档实在是。。。基本算是没有吧。所以可能还要去Github上提一波Issue。

在学习过程中，真的感觉自己懂的还是太少。简直药丸。

还需要更加努力才好。

[1]:  http://en.cppreference.com/w/cpp/thread/condition_variable/wait_for
