Date: 2016-10-17 01:28:40
Title: 使用epoll驱动ucontext - phxrpc代码阅读(5)
Tags: phxrpc, ucontext, epoll
Slug: phxrpc-5


## 用pipe叫醒你 — EpollNotifier

`class EpollNotifier`类型封装了一个使用pipe传递信号的Notifier类。

`Run()`函数（其实我觉得叫Register或Activate会更好）首先声明了两个单向的pipe：`pipe_fds_`，从[文档][1]中我们可以知道`pipe_fds_[0]`是读管道，而`pipe_fds_[1]`是写管道。这里有一丁点反直觉，就是pipe拿了两个fd，但是仍旧是单工的。

![](https://github.com/Wizmann/assets/raw/master/wizmann-pic/16-10-16/2335602.jpg)

然后将读fd设为`O_NONBLOCK`以供epoll调度，最后将`Func()`函数传入`scheduler_`中。

> 这里跑个题，想起了当年我大一的时候上过的通信导论的选修课。那会我还没有沉迷代码，还是一个积极乐观好好学习的新时代大学生。自从开始写了代码，人就越来越废物了，连女朋友都找不到了。       
年轻人们啊，有饭辙干点啥都行，千万别写码啊。

`Func()`函数做的事情很简单，就是从管道里尝试poll一段数据，拿到数据后直接扔掉。因为管道里传来的数据并没有实际意义，这样设计的主要意义在于唤醒epoll。

我们可以从`Notify()`函数中看出，传入管道的是一个字符"a"。

## 调度器类 — UThreadEpollScheduler

调试器类在初始化时，声明了协程栈的大小以及调试器所调度的最大任务数。不过这个最大任务数是一个“软线”，因为在最新的Linux内核中，epoll使用动态内存管理fd，`epoll_create`中的`size`参数已经失去了作用。而后面`epoll_wait`中的`max_event`参数只是每次返回的最多event数，也就是如果我们向调度器中加入了超过限制的fd，也不会有什么恶劣的后果。（参考[epoll文档][2]和[epoll_wait文档][3]）

### 让人搞不懂的Instance函数

这个函数看起来像一个Singleton的实现，但是明明`UThreadEpollScheduler`类的构造函数是public的。也就是这个函数像是一个单例，但它又不是一个单例。

在其它的代码中，也没有调用个函数的地方，我觉得这个函数是开发者忘记删了。

![](https://github.com/Wizmann/assets/raw/master/wizmann-pic/16-10-16/85921046.jpg)

### 远古智慧 — CreateSocket

这个函数其实没啥可说的，算是对`UThreadSocket_t`构造的封装，但是这里面有一个小技巧，就是`calloc`的使用。

`calloc`的作用是向内核申请一段栈空间（和`malloc`行为一致），然后将这一段内存清0。

个人感觉这样做的目的是防止指针没有初始化带来的一系列诡异的问题。把指针清零，可以让问题在第一时间出现，方便出错时的调试。但是我觉得还是用测试覆盖这种问题已经好，因为空指针在特定的情况下，仍可能是导致诡异行为的源头。

### 跑 — Run

`Run()`函数是调度器的核心函数（当然啦），简单来说就是一个循环获取event，用适当的协程处理event。

函数的一开始，先调用`ConsumeTodoList()`函数，将列表中的协程全部激活，并hang在epoll上。

之后进入一个“死循环”，通过`epoll_wait`将有数据可读的fd取出，并调用相应的协程进行处理。这里我们看到，`epoll_wait`的超时时间是写死的4ms，并没有使用`next_timeout`给出的下次超时时间。这是因为这里支持了“active socket”，即服务器对活动连接操作，例如发送响应甚至新建一个socket。

后面的`handler_accepted_fd_func_`和`active socket`是类似的，不过这个函数是用来处理已经建立好的连接，为其分配相应的协程。

所以，由此可见，这个循环即是事件驱动的，又是轮询的。然而这两种模型，居然能写在一个函数里，真是令人印象深刻。

![](https://github.com/Wizmann/assets/raw/master/wizmann-pic/16-10-16/4157866.jpg)

下面的`DealwithTimeout`函数处理了一下超时的协程，并且更新了`next_timeout`变量。然而这个变量因为众所周知的原因，并没有什么卵用。

![](https://github.com/Wizmann/assets/raw/master/wizmann-pic/16-10-16/4157866.jpg)

## Poll来Poll去 — 一堆epoll函数的封装

### UThreadPoll(1)

`UThreadPoll`函数有两个版本，一个是poll单个socket，另外一个是poll一堆socket。我们先从单个socket的看起。

第一步是注册一个超时时间，第二步将这个socket放到epoll的监听列表上。之后调用yield，把控制权交还给主控制流。

当epoll收到相应的事件时，主控制流会将控制权交还给协程，协程将socket从epoll监听列表中移除，之后进行后面的操作。

整体的工作流可以参考下图。

![image](http://7lrx26.com1.z0.glb.clouddn.com/%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7%202016-10-16%2021.33.48.png)

### UThreadPoll(2) - 边缘触发和水平触发

epoll有两种触发模式，边缘触发(edge-trigger, ET)和水平触发(level-trigger, LT)。

简单解释一下epoll的这两种触发模式。ET意味着只要有fd可读或可写，`epoll_wait`就返回这个fd，而LT意味着当且仅当fd由“不可读变为可读”或由“不可写变为可写”时，`epoll_wait`才会返回。（这有可能出现所谓的“粘包”现象，详见[这里][4]）

> 第一次听到“粘包”这个词，我一直以为这是啥好吃的。。。

这意味着，当我们使用LT时，我们必须清理干净fd中的数据，即只要可读，就一直读；只要可写，就一直写。否则就会出现问题。

在这里，我们使用的是比较常用的ET模式。并且我们利用了ET的特性实现了“监听多个fd，返回最早响应的那一个”。

首先，我们新建了一个epoll fd（简称内部epoll），将列表中的所有socket放到里面监听。之后将这个socket fd放到`list[0]->epollfd`所对应的epoll（简称外部epoll，通常是主工作循环的那个epoll）监听列表中。

当列表中的socket有返回时，内部的epoll会返回一个`EPOLLIN`事件，外部的epoll接收到这个事件后，进行协程切换，回到当前函数中。

下一步我们`epoll_wait`内部的epoll fd，因为我们确定此时一定有可操作的fd，所以我们将`epoll_wait`的timeout参数设为0。之后我们将返回的fd的`waited_events`参数填好，最后返回操作成功的fd的数目。

这个函数比较绕，不过有一个好消息 —— 这个函数也没有被其它地方调用过。不过这种`cascaded epoll`的技巧确实是让人耳目一新。

![](https://github.com/Wizmann/assets/raw/master/wizmann-pic/16-10-16/4157866.jpg)

### 延时执行 - UThreadWait

剩下的几个函数基本都是无脑封装，顺着看一遍代码基本就知道是啥意思了。不过`UThreadWait`这个函数比较有意思，可以用来复习一下`uthread + epoll`的工作流程。

```cpp
void UThreadWait(UThreadSocket_t & socket, int timeout_ms) {
    socket.uthread_id = socket.scheduler->GetCurrUThread();
    socket.scheduler->AddTimer(&socket, timeout_ms);
    socket.scheduler->YieldTask();
    socket.scheduler->RemoveTimer(socket.timer_id);
}
```

首先，获取当前uthread的ID，当我们调用`Resume()`函数时，让代码知道我们要返回到哪个协程上面。

然后我们向调度器中添加一个定时器。之后`Yield()`，离开当前协程。

主工作循环运行到超时时间后，会在这个协程打上一个“超时”标签，然后`Resume()`切换回这个协程上来。

剩下的工作，就交由协程内部绑定的函数来进行处理。

## 写在最后

在网络编程方面，真心是一个初学者。很多用词可能不恰当，也有一些是自己生造的。大家阅读的时候，尽量以代码和更专业的术语为准。

然后因为在行文中，可能追求了过多的逗比感，对原代码调侃了几句。并没有什么恶意，如果哪里说的不对，欢迎拍砖。

![image](http://7lrx26.com1.z0.glb.clouddn.com/IMG_20161017_012107.jpg)

佛祖保佑，永无Bug。

[1]: http://man7.org/linux/man-pages/man2fpipe.2.html
[2]: http://man7.org/linux/man-pages/man2/epoll_create.2.html
[3]: http://man7.org/linux/man-pages/man2/epoll_wait.2.html
[4]: http://man7.org/linux/man-pages/man7/epoll.7.html
