Date: 2016-09-29 01:28:09
Title: 定时器以及其它 - phxrpc阅读笔记(2)
Tags: RPC, STL, priority_queue, C++, phxrpc
Slug: phxrpc-2

## 写在前面

phxrpc使用了协程(ucontext)和IO复用技术(epoll)来实现网络通信。定时器在其中起到了非常重要的作用。下面我们就来分析一下phxrpc的`timer.[h|cpp]`中的代码。

## system_clock vs steady_clock

`system_clock`和`steadly_clock`都是来自`<chrono>`库，都是用来获取当前时间的。

`system_clock`用来从系统时钟获取时钟时间(wall clock time)，而`steadly_clock`获取的是时钟tick，而且保证随着时间的推移，时钟tick数不会变小。

然而实际上，在某些系统下，这两个时钟的实现是一致的。详细信息可以参考[这里][1]。

> 注：在clang++ 4.2.1, g++ 5.4 下实验，这两个时钟是不同的。所以个人认为在这里最好不要做任何无意义的假设。

## 几毫秒的安睡

```cpp
void Timer :: MsSleep(const int time_ms) {
    timespec t;
    t.tv_sec = time_ms / 1000;
    t.tv_nsec = (time_ms % 1000) * 1000000;
    int ret = 0;
    do {
        ret = ::nanosleep(&t, &t);
    } while (ret == -1 && errno == EINTR);
}
```

这里phxrpc使用了`nanosleep`实现了高精度的sleep。

注意这里的用法，由于`nanosleep`可能被信号中断，此时errno被设为`EINTR`。所以我们需要进行额外的判断。当nanosleep被信号中断时，会把剩余时间写入第二个参数指向的`timespec`变量中，之后我们再次调用`nanosleep`，就可以把剩余的时间再睡一个回笼觉了。

## 可删除优先队列

这个设计一颗赛艇啊。

对于`std::priority_queue`以及大多数手写的优先队列（又称堆，heap）。一般只有`top()`, `push()`, `pop()`这三个操作接口，如果想实现删除操作，大多数情况（为了偷懒）会把`std::priority_queue`替换为`std::set`。`std::set`的内部实现是平衡树（确切的说，红黑树），可以实现获得最大最小值，查找某个值，以及删除某个值的操作。

但是`std::priority_queue`（或者用数组或vector实现的堆）是顺序容器(sequence containers)，而`std::set`是关联容器(associative containers)。相对来说，由于cache的原因，顺序容器的性能比关联容器要好。当然我扯得有点远了。对此感兴趣的同学可以去参考《Effective STL》一书。

在这里，我们的需求是这样的：

* 堆是小根堆，按超时时间增序
* 堆中的元素是socket描述符`UThreadSocket_t`
* 根据描述符，我们可以删除堆中的任意元素

如果我们有清醒的头脑，就会认为这个需求是不好实现的。删除堆中元素并不复杂，只需要将堆中最后一个元素放到被删除元素的位置上，然后再执行一次`heap_down()`操作就可以了。问题在于我们很难确定某一个元素的具体位置。

> 想一想，堆中的数据是如何组织的。如果想找到某一个特定的值，除了遍历之外，还有没有其它的方法。

这里phxrpc使用了一种侵入式的手段，将下标写入堆中元素。然后堆外持有指针。然后在维护堆性质的时候，同步更新堆中元素，使其中保存的下标与其在堆中的下标一致。

这样我们就可以通过指针拿到相应元素的下标，删除操作也变得简单了起来。

那么侵入式堆下标有什么问题吗？一来我们对于元素的查找只能根据容器外持有的指针来进行，并不能像`std::set`那样通过比较关系来查找。二来侵入式下标需要额外的内存空间，对于小型对象会造成可观比例的overhead。同时容器内只能持有元素指针，在某种程度上会带来额外的寻址开销。

不过，这大概也是让堆支持删除的唯一方法了。

## 小小吐槽

这段代码写的，貌似耦合的太紧了一点。`class Timer`内部提供的功能有

1. 得到当前时间
2. nanosleep
3. 封装`TimerObj`类
4. 维护一个定时器堆，提供`top()`, `push()`, `pop()`, `erase()`功能，并且大多数操作都是硬编码的

至少在我看来，这并不符合“高内聚，低耦合”代码风格。

你问我为啥不给改改？

因为他们没写测试啊！

![](https://github.com/Wizmann/assets/raw/master/wizmann-pic/16-9-29/12309965.jpg)

## 补充

其实对于`class Timer`，phxrpc是有写测试的(test_timer.cpp)。但是这个代码写的就更迷了。这里再分析一下。

一开始，先创建100个timer，sleep时间随机。然后将50个timer放入`need_remove`数组中。

之后每删一个timer，就配套睡到超时时间pop一个timer。弹出超时timer后，再判断一下时间误差是否超过10ms，如果是，就报错。

这。。。

![](https://github.com/Wizmann/assets/raw/master/wizmann-pic/16-9-29/43591449.jpg)

[1]: http://stackoverflow.com/questions/13263277/difference-between-stdsystem-clock-and-stdsteady-clock
