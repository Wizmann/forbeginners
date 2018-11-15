Date: 2017-01-22 22:52:28 
Title: Parallel patterns in C#
Tags: csharp, parallel, thread, async
Slug: parallel-in-csharp

## 写在前面

与C/C++所使用的，传统的基于线程的并行模式不同，C#实现了丰富的并发编程模型，其中以异步模型最为流行。

本文中我们重点讨论C#在发展过程中出现的几种异步编程模型：

* Async Programming Model（APM）
* Event-based Async Pattern (EAP)
* Task-based Async Pattern（TAP）
* async/await语法糖

## 异步编程入门

同步模式是最常见，也是最被人熟知的编程模型，每一个任务按顺序执行，前一个任务执行完之后才会执行下一个任务。

异步编程和同步编程不同，程序的执行流程是由“事件”所驱动的。异步编程有两种实现方式，回调与future模式。

回调函数在Javascript中被大量使用，相信大家也都不会陌生。但是大量的回调函数会让代码失去可读性，陷入“Callback hell”。

Promise模式是回调函数的一种“包装”。我们使用一个占位符来表示“未来”将会产生的一个异步处理结果。

这个占位符在不同的语言/框架里面有不同的名字，其定义也不尽相同：

* Task - C#
* Deferred - Python Twisted
* Promise - Javascript

在任务结束后，会触发绑定在这个占位符上定义的回调函数，继续预定义好的逻辑。

举个例子，同步模型就是你：

宅家想吃饭 -> 下楼买饭 -> 上楼 -> 吃饭 -> 打游戏看漂亮小姐姐。

而异步模型呢，就是：

宅家想吃饭 -> 手机叫外卖 -> 拿到了外卖定单（拿到占位符 或 注册回调）-> 打游戏看漂亮小姐姐 -> 外卖小哥把饭送上门（启动回调） -> 吃饭 -> 继续打游戏看漂亮小姐姐。

虽然从上面看，异步模型比同步模型要复杂一些。但是它却节省了耗时的“上下楼买饭”的时间，让你可以分配更多的时间用来看漂亮小姐姐。这和我们写程序时的思路是一致的，节省动辄十几几十毫秒耗时的IO时间，将更多的时间用在CPU上。

## Thread Based Parallel

基于线程的并发模型是比较传统的并发模型了，基本上所有的现代编程语言都会支持。C#中Thread的用法与Java类似，这里就不做展开。

与此同时，C#还支持Thread pool，用来运行"long-running processor-bound tasks"。

直接操作线程也许是中年程序员的必修课，但是手动管理线程会给程序带来额外的负担。所以各种模型与框架应运而生，试图降低并发编程的复杂度。

## Async Programming Model (APM)

在我们熟悉的async/await语法糖出现之前，C#中使用APM来表示异步操作。虽然这是一种上古时期的回调模式语法，但是现在有很多库仍旧支持这种风格。如Azure Storage SDK中的`CloudTable.BeginExecute`等一系列函数。

下面是一个简单的使用APM模式的代码范例：

```cs
using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.Remoting.Messaging;
using System.Runtime.Remoting.Proxies;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace ConsoleApplication6
{
    class Program
    {
        public delegate int AsyncInvoke();

        static void Main(string[] args)
        {
            var SI = new AsyncInvoke(MyCall);
            var ar = SI.BeginInvoke(MyCallback, null);

            Console.WriteLine("Main()");
            while (!ar.AsyncWaitHandle.WaitOne(1000))
            {
                Console.WriteLine("Main() waiting...");
            }
            Console.WriteLine("Main() done");

            Console.ReadLine();
        }

        static int MyCall()
        {
            for (int i = 0; i < 5; i++)
            {
                Console.WriteLine("running...");
                Thread.Sleep(500);
            }
            Console.WriteLine("done");
            return 42;
        }

        static void MyCallback(IAsyncResult iResult)
        {
            var result = iResult as AsyncResult;
            var si = (AsyncInvoke) result.AsyncDelegate;
            int ret = si.EndInvoke(result);
            Console.WriteLine(ret);
        }
    }
}
```

运行结果如下：

![](https://github.com/Wizmann/assets/raw/master/wizmann-pic/17-1-19/26234044-file_1484828912411_150f3.gif)

我们可以看到：
1. 我们将`MyCall()`“包装”在一个`delegate`中，然后调用`BeginInvoke`函数实现异步执行。这个delegate的执行不会阻塞main thread。
2. 一个异步执行的`delegate`可以有一个回调，这个回调在delegate执行完后被触发。
3. 我们可以"long-polling"等待一个异步调用执行完。这里的“执行完”不包括条目2提到的回调（小心race condition！）。
4. 异步执行的结果可以通过`delegate.EndInvoke(IAsyncResult)`函数获取到异步调用的结果。
5. 由条目3我们可以知道，在callback函数中获取异步调用的结果是最合适的。

所以APM风格的代码写起来非常像javascript中的回调写法，如果逻辑复杂的话，维护起来会是一个大坑。

## Event Asynchronous Pattern (EAP)

EAP是回调函数的另一种封装。

我们来看下面的代码：

```cs
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace ConsoleApplication2
{
    class StringEventArgs : EventArgs
    {
        public string Content { get; set; }
    }
    
    class Solution
    {
        private event EventHandler<StringEventArgs> _eventHandler;

        public Solution()
        {
            _eventHandler += Handle1;
            _eventHandler += Handle2;
        }

        public void Run()
        {
            _eventHandler?.Invoke(this, new StringEventArgs()
            {
                Content = "123"
            });
        }

        void Handle1(object sender, StringEventArgs args)
        {
            Console.WriteLine("Handle1 " + args.Content);
            Thread.Sleep(1000);
        }
        void Handle2(object sender, StringEventArgs args)
        {
            Console.WriteLine("Handle2 " + args.Content);
            Thread.Sleep(1000);
        }
    }
    class Program
    {
        static void Main(string[] args)
        {
            Solution sol = new Solution();
            sol.Run();
            Console.WriteLine("Done");
            Console.ReadLine();
        }
    }
}

```

运行结果如下：

![](https://github.com/Wizmann/assets/raw/master/wizmann-pic/17-1-20/46892581-file_1484911655343_68ae.gif)

我们可以看出，所有的函数都执行在同一个线程上。并且`Handle1`和`Handle2`顺序执行。

在实际工程中，我们fire event的代码可以在不同的线程，之后`EventHandler`，也就是callback函数会被调用。

Event同时支持`BeginInvoke`和`EndInvoke`函数，也就意味着我们可以异步的fire相应的回调。但是注意此时我们只能注册唯一的回调，因为`BeginInvoke`只能有一个目标回调（原理：在同一时间同一线程只能有一个函数调用）。

## Task Asynchronous Pattern (TAP)

在.NET 4.0（现在已经到6.0了哦），C#引入了TPL，Task Parallel Library。Task的目标是统一C#中的不同异步编程风格。

TPL中的Task非常像JS中的promise和twisted中的deferred，是“未来会完成的操作的结果”的占位符。

我们来看一段简单代码：

```cs
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace ConsoleApplication3
{
    class Program
    {
        static void Main(string[] args)
        {
            Task t = Task.Run(() =>
            {
                Console.WriteLine("Task start");
                Thread.Sleep(2000);
                Console.WriteLine("Task end");
            });

            while (!t.IsCompleted)
            {
                Console.WriteLine("Main(): Task is running...");
                Thread.Sleep(1000);
            }

            Console.WriteLine("Done");
            Console.ReadLine();
        }
    }
}
```

这段代码我们前面提到的APM和EAP风格的代码有明显的不同，TAP更易读，并且保持了控制流的完整性。不像APM需要在`EndInvoke`函数中获取返回值以及进行后续操作，也不像EAP一样需要根据不同的event声明不同的回调。

Task也可能“串起来”，实现多级回调的机制。

```cs
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ConsoleApplication4
{
    class Program
    {
        static void Main(string[] args)
        {
            var t0 = Task.Run(() => 0);
            var t1 = t0.ContinueWith((antecedent) =>
            {
                Console.WriteLine(antecedent.Result);
                return antecedent.Result + 1;
            });
            var t2 = t1.ContinueWith((antecedent) =>
            {
                Console.WriteLine(antecedent.Result);
                return antecedent.Result + 1;
            });
            var t3 = t2.ContinueWith((antecedent) =>
            {
                Console.WriteLine(antecedent.Result);
                return antecedent.Result + 1;
            });

            Console.ReadLine();
        }
    }
}
```

当然我们还可以把回调写成一棵树状结构，然后一层一层的执行，不过生命是如此宝贵，我们并没有充分的理由要这么做。

## async/await语法糖

async/await语法糖在C# 5.0中被引入，其目的是为了避免回调带来的代码复杂度。就像Twisted中的`@inlineCallbacks`一样，省去了defer复杂的回调链。

`await`中有一个"wait"，说明这是一个“等待”操作。它等待的是相应的Task执行完成。

我们来看一段代码：

```cs
private async void DumpWebPageAsync(string uri)
{
    WebClient webClient = new WebClient();
    string page = await webClient.DownloadStringTaskAsync(uri);
    Console.WriteLine(page);
}
```

当代码执行到`await`一行时，当前函数会主动放弃当前的控制流。当使用`await`修饰的Task完成后，当前函数会从之前中断的地方继续执行。

这样做的好处是我们可以写出和同步版本非常相似的异步代码，只需要在必须的地方加上`await`关键字，提醒编译器这里是一个异步函数，需要额外的处理逻辑，但这一切都是对开发者透明的。

### async/await干了什么

想弄清楚async/await到底干了什么，首先我们要想明白线程到底是什么、干了什么。

线程是进程内一条执行流的状态，其中包括了硬件状态（IP、Registers等）以及堆栈（栈上的局部变量和堆上的进程级内存）。那么如果我们想实现挂起/启动（Hibernating and Resuming），那么我们就要有一个机制来保存当前线程的运行状态。

所以当你写下了async/await关键字后，编译器在后面帮助你生成了状态保存和恢复运行上下文的代码。

### async/await到底干了什么

想像我们有一个复杂的async函数，里面有很多个await调用，那就意味着这个函数中会有多次挂起/继续操作。同时我们还要维护这个函数的状态。如果我们是这个语法糖的设计者，我们会选择怎么样的手段来处理这个问题呢？

是的，状态机。async/await避免了代码的碎片化，它的解决方案并不是消灭了回调函数和Continuation Tasks，而是使用工具（编译器）来帮助人类进行重复劳动。当async函数从挂起中恢复时，会调用`MoveNext`函数（相信看过async函数那一长串的traceback的同学肯定对这个函数非常眼熟），`MoveNext`函数会在async函数第一次被调用以及从挂起中恢复时被调用。状态机保存了当前函数的执行状态，当`MoveNext`函数被调用时，会根据当前状态来判断接下来执行什么代码。

### asycn/await到底TMD干了什么

由于async/awaic语法糖是在编译期才被翻译成相应的程序代码，所以我们只能使用IL反编译器来窥探编译器到底做了怎样的处理与优化。不过反编译器你懂得，生成的代码基本没法看，讲解起来也会非常晦涩。

幸好在99%的情况下，我们并不需要知道async/await是怎样被展开的。如果你确实对这个问题感兴趣，可以参考这篇文章：[Async Await and the Generated StateMachine][1]。

## 几个常见的坑

### await 与 锁

由于await会中断当前函数在当前线程的执行流，并且可能在恢复时，被指派到另外的线程。所以对await加锁明显是多此一举的。并且如果操作不当，还会造成死锁。

所以我们应该把await放到加锁的区域外。

```cs
lock (sync)
{    
    // Prepare for async operation
}

int myNum = await AlexsMethodAsync();

lock (sync)
{    
    // Use result of async operation
}
```

### "There is an ... unfired Task between us"

一个async函数如果返回的是Task，那么它返回的一定是一个hot task，即已经被启动了的Task。

并且await只可能等待一个启动了的Task，否则await操作将会hang住，破坏程序既定的执行流。

### 使用TPL (Task parallel library)

> Async methods are synchronous util needed.

如果我们想同时执行几个异步操作，使用for来遍历执行可不是一个好主意。因为这样函数执行流仍然是顺序执行相应的函数。

TPL提供了`WhenAll`、`WhenAny`等函数，让我们可以有弹性的并发执行Task。

当然我们还可以使用PLINQ，不过这就是另外一个话题了。

## 参考链接

* [Async Await and the Generated StateMachine][1]
* [Async Interop with IAsyncResult][2]
* [Event-based Asynchronous Pattern Overview][3]
* [Async in C# 5.0][4]
* [Essential C# 6.0][5] Cpt18

[1]: https://www.codeproject.com/Articles/535635/Async-Await-and-the-Generated-StateMachine
[2]: http://blog.stephencleary.com/2012/07/async-interop-with-iasyncresult.html
[3]: https://msdn.microsoft.com/en-us/library/wewwczdw(v=vs.110).aspx
[4]: https://www.safaribooksonline.com/library/view/async-in-c/9781449337155/
[5]: https://www.safaribooksonline.com/library/view/essential-c-60/9780134176147/