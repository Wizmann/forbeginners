Date: 2018-10-16 08:00:00
Title: 多线程编程初步
Tags: 多线程, multi-thread, mutex, conditional-variable
Slug: multi-thread-programming-intro

## 前言

非常不喜欢这种“X一峰”式的文章。但是为了伟大的教育事业，还是要写一点的。

## 线程安全的定义

无论操作系统如何调度线程，无论这些线程的执行顺序如何交织。一个函数（或类）在多个线程同时访问时能表现出正确的行为，而无需调用端代码进行额外的同步或协调操作。

划重点：

* 无论如何调度
* 无需额外的同步或协调操作
* 总能表现出正确的行为

## 竞态条件（race condition）

竞态条件描述的是一个系统或者进程的输出依赖于不受控制的事件出现顺序或者出现时机。例如两个进程“同时读写”一块内存，其结果一定是不受控制的。

“同时读写”的定义包括：

* 一读一写
* 一写多读
* 多写一读
* 多写多读
* 多写

也就是说，只要包含“并发”和“写操作”两个特性，就会出现竞态条件。而“多读”一般来说是安全的。

同时也要注意，这里的读与写是物理意义上的读写，而不是逻辑意义上的。有一些函数看起来只有读操作，但其内部仍然包括了对数据的修改，这里需要注意甄别。

## Mutex - 互斥锁

互斥锁（Mutual exclusion，缩写 Mutex）是一种用于多线程编程中，防止两条线程同时对同一公共资源（比如全局变量）进行读写的机制。该目的通过将代码切片成一个一个的临界区域（critical section）达成。临界区域指的是一块对公共资源进行访问的代码。一个程序、进程、线程可以拥有多个临界区域。

应用场景如下：一段代码（甲）正在分步修改一块数据。这时，另一条线程（乙）由于一些原因被唤醒。如果乙此时去读取甲正在修改的数据，而甲碰巧还没有完成整个修改过程，这个时候这块数据的状态就处在极大的不确定状态中，读取到的数据当然也是有问题的。更严重的情况是乙也往这块地方写数据，这样的一来，后果将变得不可收拾。

因此，多个线程间共享的数据必须被保护。达到这个目的的方法，就是确保同一时间只有一个临界区域处于运行状态，而其他的临界区域，无论是读是写，都必须被挂起并且不能获得运行机会。

### 一个线程安全的计数器

```cpp
class Counter {
public:
    Counter(): value(0) {}
    int get_value() const { return value; }
    int add_value(int delta) {
        mutex.lock();
        value += delta;
        mutex.unlock();
        return value;
    }
private:
    int value;
    MutexLock mutex;
};
```

`MutexLock`一个封装了操作系统互斥锁的类，其方法有加锁`lock()`和解锁`unlock()`。

### 死锁与饥饿

死锁（Deadlock)，指的是两个以上的运算单元（线程），双方都等待对方释放资源，但是没有一方释放自身所拥有的资源。这种情况被称为死锁。

一个简单的避免死锁的方式，是在某运算单元在不能获取所需要的资源时，释放自身所占有的资源，并进行等待。

饥饿指的是一个运算单元尽管可以继续执行，但是不能获取所需要的资源，从而不能调度执行的情形。

划重点：

* 死锁：两个山羊过独木桥，谁都不退让
* 饥饿：两个人传球，第三个人没有球玩只能看着

## 条件变量（Condition Variable)

概念上，一个条件变量就是一个线程队列(queue), 其中的线程正等待某个条件变为真。当一个线程等待一个条件变量时，其它线程可以改变管程的状态，从而唤醒一个或多个正在队列中的线程。

划重点：

* 条件变量：饭熟了叫我

### 一个线程安全的生产者消费者队列

```cpp
// 在消费者把队列里的数据都读空之后
// 再次读取会挂起，直到生产者向队列中放入新的数据为止
class ConsumerProducerQueue {
public:
    ConsumerProducerQueue(): cv(mutex) {}
    
    void put(int value) {
        mutex.lock(); // 修改共享资源要加锁
        q.push(value);
        mutex.unlock(); // 修改完了要释放锁
        cv.signal(); // 告诉消费者们饭已OK了，过来咪西吧
    }
    
    int get() {
        mutex.lock();
        // 有的消费者线程在得到信号后
        // 仍然因为竞争拿不到数据
        // 所以这里需要写一个循环
        while (q.empty()) {
            cv.wait(); // wait()会释放锁，允许put(value)函数向队列中写入新的值
        }
        int res = q.front();
        q.pop();
        mutex.unlock();
        return res;
    }
private:
    queue<int> q;
    ConditionVariable cv;
    MutexLock mutex;
};
```

## 实战：线程安全的Singleton实现

```cpp
template <typename T>
class Singleton<T> {
public:
    Singleton(): instance(nullptr) {}
    
    T* get_instance() {
        if (instance != nullptr) {
            return instance;
        }
        mutex.lock();
        // 这里为什么还需要检查呢？
        // 因为在上锁之前，instance仍有可能被修改
        // 如果重复创建实例，就会产生内存泄漏
        if (instance == nullptr) {
            instance = new T();
        }
        mutex.unlock();
        return instance;
    }
private:
    Mutex mutex;
    T* instance;
};
```

## 高级话题：CAS - Compare And Swap

比较并替换（compare-and-swap, CAS）是一个用于多线程同步的原子操作。

其工作流程是：
```
def cmpxchg(val, oldval, newval):
    if val == oldval:
        val = newval
        return True
    return False
```
也就是说，只有当val等于oldval时，我们才会将val的值替换成newval。在多线程的场景下，cmpxchg用来保证多线程写的原子性。

例如，线程1和线程2都要写入val变量，但是我们需要保证只有一个线程能写成功。使用cmpxchg，能保证只有一个线程能成功的将val变量替换成新值，写失败的线程会得到False的返回值。

CAS经常用来实现无锁的数据结构，因为常规的互斥锁的每次加锁和解锁操作都需要进入内核态，造成非常大的开销。

## 扩展阅读

* [Linux多线程服务端编程 - 陈硕][1]
* [Java并发编程实战][2]
* [Operating Systems: Three Easy Pieces][3]

[1]: https://book.douban.com/subject/20471211/
[2]: https://book.douban.com/subject/10484692/
[3]: http://pages.cs.wisc.edu/~remzi/OSTEP/
