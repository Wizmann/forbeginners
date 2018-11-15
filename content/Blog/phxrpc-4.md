Date: 2016-10-13 23:45:24
Title: ucontext - phxrpc代码阅读(4)
Tags: phxrpc, ucontext, 协程
Slug: phxrpc-4


## 写在前面

国庆假期过半，phxrpc的代码阅读大概要小小告一段落啦。因为这两天还要读工作相关的代码，以及最后几天还有一次短途旅行。

所以非阻塞TCP流可能要留到下一篇了，这一篇只涉及非阻塞TCP流使用到的ucontext协程库，及其使用的一些框架代码。

> 161013更新：这点破东西写到今天才写完，GG。

## 什么是ucontext

> "Subroutines are special cases of ... coroutines." –Donald Knuth.

首先我们来看一下，什么是线程。线程是进程内一条执行流的状态，包含了硬件状态（硬件计数器，寄存器，条件码等）和堆栈中的数据。

线程通常只有一个入口和一个出口。当线程返回时，线程的生命周期也结束了。所以，通常线程的执行由内核调度。

协程的定义与线程类似，也是硬件状态+堆栈的状态组合。但是与线程不同的是，协程可以有多个出口。可以通过yield来暂停自己，调用其它协程。再次启动时，会从上次挂起的地方继续运行。

## phxrpc中的ucontext

phxrpc提供了system和boost两种ucontext的实现，所以提供了一个`uthread_context_base`的基类。其实在这里我是有一点怀疑虚函数的性能的，不过好在协程的切换以及网络IO操作还是比较耗性能的，所以虚函数多出来的几次内存寻址也并非不能接受。

在这篇文章中，我们只看`uthread_context_system`这个使用系统ucontext库的实现。

### 协程上下文：`UThreadContext`

这个类是协程上下文的虚基类，所以代码很少。并且也没有什么好解释的。

`void Make(UThreadFunc_t func, void * args)`函数是`makecontext()`的封装。

`bool Resume()`和`bool Yield()`是`swapcontext`的封装。

个人感觉这个类拆分成一个工厂类（传入一个Create仿函数）和一个上下文基类会更清楚一点。

### 使用系统ucontext库的协程上下文：`UThreadContextSystem`

在phxrpc的文档中，说明使用系统原生的ucontext库的性能要差于boost版本的。但是从数据上来看微乎其微，所以我们先从这个版本看起，力求举一反三。

`UThreadContextSystem`在构造函数中传入了协程栈大小，协程要执行的函数（及参数），协程执行后的回调，以及调试用的`need_stack_protect` flag。

每一个上下文对象都维护了两个context，`main_context`用来表示主程序执行流的上下文，而`context_`则用来表示协程的上下文。

`main_context`是`static thread_local`修饰的，也就意味着这个静态变量在每一个线程中有且只有一个。执行在同一个线程上的不同协程，都会切换/被切换到这个上下文上。

在`Resume()`函数中，我们激活协程上下文，并将主程序执行流的上下文保存在`main_context`上。

在`Yield()`函数中，我们将主程序执行流的上下文激活，将协程上下文保存回`context_`中。

这里的`UThreadFuncWrapper()`值得我们特别关注。这个函数包装了我们的工作函数`uc->func_`，并且将`this`指针传进去。

传入指针时，这里使用了一个技巧。首先我们将指针强转为`uintptr_t`，这个是编译器内置的一个`typeof`，意在将指针类型无损失的转为整型。之后，将一个`uintptr_t`拆为两个`uint32_t`。最后，在wrapper函数中，将这两个`uint32_t`拼回成一个指针类型。

初看这段代码，我们就有这样的疑问：“这特么不是有病么？” 但是，折腾自然有折腾的道理。

>  When this context is later activated (using setcontext(3) or swapcontext()) the function func is called, and passed the series of integer (int) arguments that follow argc; the caller must specify the number of these arguments in argc.

从官方的文档中我们可以看到，用在`setcontext`中的函数，只支持int类型的参数，并且需要我们显式声明参数的数目。这里一定要小心，因为变长参数列表并不能有很强的编译期检查支持，搞出UB或core dump来就非常难查。

### ucontext中使用的栈内存：`UThreadStackMemory`

ucontext协程是在同一个线程执行多个上下文，所以就要配备多个栈空间。这里的栈大小我们是可以手动管理的，所以我们可以根据程序的实际情况来调整栈大小，以节省内存使用。

内存的申请并不是使用`malloc`或者`new`这种比较高层次的内存操作函数，而是使用的`mmap`。这样的好处是我们可以使用参数控制申请出的内存的权限。

栈内存有两种模式，保护和非保护。保护模式用于调试，会在正常栈内存的两端，各申请一个页大小的保护内存。正常栈内存的权限是读写：`PROT_READ | PROT_WRITE`，而保护内存的权限是禁止访问：`PROT_NONE`，也就是说，任何试图访问这块内存的请求，都会触发段错误。

在非保护的运行模式下，栈内存还会使用`MAP_ANONYMOUS | MAP_PRIVATE`还进行保护。`MAP_ANONYMOUS`表明这段内存是匿名的，即不占用fd，也无需进行写回操作，使mmap的行为类似于malloc。`MAP_PRIVATE`意为这段内存不会被其它进程访问，可以使用私有的写时复制映射。（虽然没找到相关资料，但是感觉这两个配置牺牲了可调试性来获取更好的性能）

### ucontext的运行时：`UThreadRuntime`

这个类其实很简单，但是由于代码的命名过于意识流，所以很容易把人绕晕。

一个`UThreadRuntime`代表着一个线程中运行着的N个ucontext上下文。上下文信息保存在`std::vector<ContextSlot> context_list_`中。

slot是可以复用的，`first_done_item_`记录着已执行完的context的下标，然后slot中的`next_done_item`记录着下一个执行完的context的下标。简而言之，这就是类似一个“脏池”的设计。不过这个命名啊，一点都不赛艇。

剩下的代码基本就是`UThreadContext`的无脑封装了。需要哪个协程开始工作就`Resume`哪个协程，需要暂停就调用`Yield`。结束后，调用回调函数，把运行完的协程往脏池一扔，完活。

## 写在最后

上面我们分析了phxrpc对ucontext协程库的封装，下一篇，我们就来正式看一看ucontext是如何与IO多路复用的技术连接在一起的。

最后上几张皂片：

![](https://github.com/Wizmann/assets/raw/master/wizmann-pic/16-10-13/31415098.jpg)

![](https://github.com/Wizmann/assets/raw/master/wizmann-pic/16-10-13/1208386.jpg)

![](https://github.com/Wizmann/assets/raw/master/wizmann-pic/16-10-13/97556242.jpg)

![](https://github.com/Wizmann/assets/raw/master/wizmann-pic/16-10-13/44196833.jpg)

![](https://github.com/Wizmann/assets/raw/master/wizmann-pic/16-10-13/20763058.jpg)
