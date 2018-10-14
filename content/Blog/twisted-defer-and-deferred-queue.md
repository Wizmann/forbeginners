Date: 2016-12-10 11:34:38
Title: Twisted Defer and DeferredQueue
Tags: twisted, defer, async
Slug: twisted-defer-and-deferredqueue


## 写在最前面

这篇文章本来是想用英文写的，但是最近英文水平下降的和狗一样。还是怂一波吧。

## 写在前面

最近在用Twisted库写一个诡异的项目，具体内容暂且不在这里讨论。在写的过程中，被Twisted里面的一个重要概念 —— defer，折腾的不行。最终通过阅读twisted的部分源码，以及与代码做斗争的丰富经验，最终算是解决了问题。

本文算是使用twisted开发踩坑的一个小小总结，如果一切顺利，后面会有大菜。：）

## Twisted介绍

> Twisted is an event-driven networking engine written in Python.

Twisted是一个基于事件驱动的网络框架。那么什么是“事件驱动”呢？

事件驱动指的是将事件与事件回调绑定起来，在程序运行时根据实时的事件触发相应的响应的一种机制。

例如select/poll/epoll这些IO复用函数，在文件描述符（fd）可读/可写/出错时，会立即返回，由相应的处理函数来对新事件进行处理。事实上，twisted的事件驱动功能，正是由这些IO复用函数提供的。

但与IO复用函数不同的是，twisted中的事件可以是“更高层次的事件”，即对网络的读/写/错等基础事件进行更进一步的封装。

这里我们以`LineReceiver`为例（[API文档][1]）。`LineReceiver`是对传输层协议的二次封装，当我们读完一整行之后，就触发`lineReceived`事件，对获取的数据进行处理。

这种封装，将开发者与底层的网络交互隔离开来。利用这些“高级事件”，开发者可以将更多的精力放到程序本身逻辑的开发之中。

还有一点，正如Python语言本身的一大优点一样，Twisted现成的协议实现的非常丰富，同时在工业界也较为广泛的使用。虽然赶不上golang这种“明星语言”，但是也还是可以“自成一派”，搞点事情。

## Defer与回调

Twisted使用Defer来管理callback链，如果你写过js，就可能对被回调链（callback chains）所支配的恐惧记忆深刻。当然，Twisted的defer也并没有好到哪里去。（蛤！）

Seriously，defer允许我们使用一般的顺序型编程模型来编写回调代码。我们只需要把函数按照顺序注册到defer当中，就可以完整的实现一个回调链了。

![](http://wizmann-pic.qiniudn.com/public/16-12-9/90670835.jpg)

本文不会对defer进行过多讲解，如果想要了解更多的话，可以参考twisted的[官方文档][2]。

defer做为一个回调链的抽象，有一个非常重要的性质，就是你不fire它，它是不会调用它的callbacks的。正像俗话说的一样：

> 事不说不知，木不钻不透，砂锅不打一辈子不漏

又有人说过（异步发卡）：

> A: There's something between us.     
> B: What is it?      
> A: An unfired defer.

如果你想激活defer中的callbacks，就需要手动的fire它。那么什么时候来fire它呢？当然是在需要的时候啦。

### 一个典型的defer使用场景 - txmongo

txmongo是一个异步的mongodb python sdk。而我们常用的pymongo库则是同步的，所有的请求都要同步等待数据库返回结果。

由于是异步的sdk，所以在同一时间，txmongo会同时持有多个mongodb连接（连接池）。并且由于我们不能预测mongodb的响应时间，所以需要在收到mongodb响应后，启动相应的回调函数，以触发更高级别的消息事件。

```python
# txmongo/protocol.py#L368
def handle_REPLY(self, request):
    if request.response_to in self.__deferreds:
        df = self.__deferreds.pop(request.response_to)
        if request.response_flags & REPLY_QUERY_FAILURE:
            # some error handling code
        else:
            df.callback(request)
```

我们从这段代码中看出，当txmongo收到响应后，会先从`self.__deferreds`字典中取出相应的defer，之后使用`request`做为参数，启动defer中的callbacks，将查到的数据返回给调用者。

### 新手会遇到的defer坑 —— 测试

做为一个马上就要步入中年的程序员，我最大的一个优点就是不相信自己（汗）。所以在开发时会及时写单元测试来尽可能保证代码的正确性。于是在开发的很早就踩到了defer的坑，包括：

1. 测试hang住
2. 测试通过，但是报错"reactor was unclean"
3. 由于回调没有执行，测试挂掉

坑1比较好解决，defer没有callback，hang住了只能怪自己。不过查哪里hang住了会比较麻烦，最直接的方法是多打log，从log里很容易就知道哪里有问题。

坑2和坑3都属于我们使用defer的姿势不对。defer是“延时”的，我们不能像调用函数一样的直接调用，测试代码需要defer执行完最后一个callback函数后再继续执行。那么我们需要把测试代码也写成callbacks，然后附在需要测试的defer后面吗？

答案是否定的，twisted为我们提供了一个神奇的工具`@defer.inlineCallbacks`。这个装饰器可以用于开发环境与测试环境。我们可以使用yield等待defer执行完成，并且可以获得defer的返回值。这类似于C#的async/await语法，使用起来非常方便。

所以在我们的测试当中如果使用了defer，就需要将测试case使用`inlineCallbacks`装饰起来，在等待defer时，需要使用yield语法，等待异步代码的执行。在case的最后，将不需要的defer cancel掉即可。

## DeferredQueue与循环

Queue的一个重要用法就是循环。包括线程/进程通信的Queue，BFS中使用的Queue，都是需要循环读取数据。

DeferredQueue是Twisted中通信的一个重要数据结构，其使用方法和一般的Queue从逻辑上是一样的，接口也只有两个：`put`和`get`。

DeferredQueue之所以有一个Deferred前辍，是因为它的get函数返回的是一个defer。我们可以在这个defer上绑定callbacks，即有数据可读时，触发相应的回调函数。

所以我们很容易就把代码写成了这样：
```python
q = defer.DeferredQueue()

def get_and_print(item):
    print item
    q.get().addCallback(get_and_print)

q.get().addCallback(get_and_print)

for i in xrange(100):
    q.put(i)
```

一眼看上去，这个代码没有什么问题，我们会循环的从队列中获取数据并打印。但实际上，这段代码有一个神奇的坑。

说一下这个坑是怎么发现的吧，我把代码写的差不多之后，就想跑benchmark来测性能。然后发现CPython的性能一般，就想试试pypy。然后却怎么也得不到正确的结果，最后发现是因为DeferredQueue引发了递归过深的异常。但是为什么CPython没有这个问题呢。原因在于CPython的递归栈是按深度算的，而pypy的递归栈是按大小算的，但是这两个参数的标量是一样的，所以pypy的递归栈就远小于CPython的。这才暴露了这个问题。不过单纯的扩栈也是不合理的，因为我们很难估计极端情况，并且Python的递归性能非常差。

感兴趣的同学可以去参考[源码][3]，这里就直接说结论了。当队列中有元素时，`q.get().addCallback(get_and_print)`会直接调用`get_and_print`函数本身，如果队列中的元素非常多，那么我们就有递归过深的危险了。

解决方案也很简单，与其让Twisted把我们的循环写成递归，还不如我们自己实现Queue的循环。至于方法，看看DeferredQueue的内部实现就清楚了，然后我们就发现了另外一个坑。

## DeferredQueue与性能

我啥都不说，就贴一行[代码][4]：

```python
return succeed(self.pending.pop(0))
```

您这就是在逗我。

![](http://wizmann-pic.qiniudn.com/public/16-12-9/36902015.jpg)

再贴个性能对比，使用`list.pop(0)`弹出10^5个数据需要2.23s，而使用`deque.popleft()`只需要0.12s。

不要功能实现了就不管性能了嘛同学。

[1]: http://twistedmatrix.com/documents/current/api/twisted.protocols.basic.LineReceiver.html
[2]: https://twistedmatrix.com/documents/current/core/howto/defer.html
[3]: https://github.com/twisted/twisted/blob/twisted-16.5.0/src/twisted/internet/defer.py#L1600
[4]: https://github.com/twisted/twisted/blob/twisted-16.5.0/src/twisted/internet/defer.py#L1665
