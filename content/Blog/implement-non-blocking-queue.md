Date: 2018-05-02 00:39:00
Title: 实现一个无锁消息队列
Tags: multi-thread, cas, cmpxchg
Slug: implement-non-blocking-queue

## 目标

实现一个多读多写的无锁消息队列。

## cmpxchg - 比较并替换

比较并替换（compare-and-swap, CAS）是一个用于多线程同步的原子操作。

其工作流程是：

```python
def cmpxchg(val, oldval, newval):
    if val == oldval:
        val = newval
        return True
    return False
```

也就是说，只有当`val`等于`oldval`时，我们才会将`val`的值替换成`newval`。在多线程的场景下，cmpxchg用来保证多线程写的原子性。

例如，线程1和线程2都要写入`val`变量，但是我们需要保证只有一个线程能写成功。使用cmpxchg，能保证只有一个线程能成功的将`val`变量替换成新值，写失败的线程会得到`False`的返回值。

## ACCESS_ONCE - 消除优化歧义

```cpp
#define ACCESS_ONCE(x) (*(volatile typeof(x) *)&(x))；
```

`ACCESS_ONCE`的作用是将一个指针转化成`volatile`指针，使得读取操作“真的”去读取指针的值而不被编译器优化掉。

## 实现

### 原子操作与Nullable

说到多线程，我们就不能不谈原子操作。对于一个队列来说，我们可以在其中存储任意复杂的数据结构，但是这些数据结构大部分都不支持原子操作。

同样，我们也没有一种有效的手段来标识一个值是“不存在的”。是的，我们可以自己实现一个`Nullable<T>`的模板，但是带来的额外成本就是对于任意`Nullable<T>`的赋值都要经过两步以上的中间步骤，这简直就是竞态bug产生的温床。

不过，在C++中自带着一个有着"Nullable"语意的数据结构 —— 指针。当指针为NULL时，意味着值是不存在的，而指针不为NULL时，它代表着它所指向的值。更重要的是，指针的赋值、读取、拷贝都是原子的，这给我们的代码实现提供了非常大的便利。

### 数据结构

![](https://github.com/Wizmann/assets/raw/master/wizmann-pic/18-5-1/40471673.jpg)

我们使用单链表做为基础数据结构，链表的头代表着队列的头，链表的尾对应着队列的尾。这样添加数据时，我们在TAIL节点处写入，弹出数据时从HEAD节点处弹出。

那么问题来了，在单线程下，维护头尾节点是非常容易的操作。

```python
"""
维护头节点
"""

cur = HEAD.next
HEAD.next = HEAD.next.next # 操作链表

"""
维护尾节点
"""
newnode = Node(value)
TAIL.next = newnode # 操作链表
TAIL = TAIL.next # 操作链表
```

但是在多线程环境下，维护尾节点需要对链表进行两次操作，我们很难把它做为原子的。这大概是实现无锁队列最大的难点之一。

### 框架代码

无锁队列中，`push`和`pop`两个函数是核心代码。但是我们需要先把框架代码先搭好。

```cpp
template <typename T>
class NonBlockingQueue {
public:
    NonBlockingQueue() {
        head = &dummy;
        tail = new InnerNode();
        dummy.next = tail;
    }

    void push(const T* item) {
        // pass
    }

    bool pop(T*& item) {
        // pass
    }
private:
    struct InnerNode {
        T* value_ptr;
        InnerNode* next;
    };
private:
    InnerNode dummy;
    InnerNode* head;
    InnerNode* tail;
};
```

这里的`dummy`是一个假的头节点，是为了方便节点的插入的，可以替换成一个头节点指针。`tail`是尾节点，在构造函数里，我们也将其置为一个假的尾节点，注意这里尾节点的设计，后文会再次提到。

### 出队操作

我们先从最简单的出队操作开始

```cpp
bool pop(T*& item) {
    InnerNode* cur = NULL;
    do {
        cur = ACCESS_ONCE(head->next);
        if (cur == tail) {
            return false;
        }
    } while (!__sync_bool_compare_and_swap(&(head->next), cur, cur->next));

    item = cur->value_ptr;
    // delete(cur); <- why?
    return true;
}
```

代码中的`__sync_bool_compare_and_swap`即上文所说的`cmpxchg`函数，保证了赋值的原子性。

操作过程非常简单，我们先找到位于队列头的值（HEAD节点后面的第一个）。然后使用CAS操作将其换出链表。

由于tail节点是假的尾节点，所以在`head->next == tail`时，我们认为队列为空，返回false。

这里有一点需要注意，`cur`指针在while循环外看似已经脱离了链表，可以放心的删除了。但是由于其它线程仍有可能持有该指针，所以我们并不能在这里对它进行删除操作。

在实际工程中，我们可以将其放置于一个回收队列中，待一小段时间后（如500ms），所有的线程都不持有该指针时，就可以安全的将其回收了。这里由于篇幅原因（注释：懒），就不实现了。

### 入队操作

```cpp
void push(const T* item) {
    assert (item != NULL);
    while (true) {
        if (__sync_bool_compare_and_swap(&(tail->value_ptr), NULL, item)) {
            tail->next = new InnerNode();
            tail = tail->next;
            break;
        }
    }
}
```

这里的`push`操作有一个trick，我们将`tail->value_ptr`做为“一把锁”。当`value_ptr`为空时，tail指针代表着一个“假尾节点”。当我们向尾部追加数据时，先将数据写入`value_ptr`，代表这个节点已经被“占领”。然后再向它的后面追加新的“假尾节点”，最后将指针移动过去。

这样一来，进入`if`代码块的线程一定是写入`tail->value_ptr`成功的那一个，后面的指针移动也是单线程的了。

## 感悟与可能的改进

最近确实好久不写这么底层的代码，手生的厉害，对于多线程状态的分析也不是很灵光。确实需要多努力了。本文中的代码也许还有一些问题，所以欢迎大家指正。

在写这段代码的过程中，感觉有如下需要注意的地方：

* 析构一块内存是否是安全的，会不会别的线程仍在持有这块内存的指针
* 编译器会不会给我们捣乱，比如重排指令等
* 利用CAS的特性，我们可以实现一个锁的结构，但是以哪个变量/指针做为锁可以获得最好的效果

除了用链表实现队列之外，还可以使用环型数组。感觉上来说比使用链表更优雅一点。关键在于环型数组中隐含着前驱指针和后继节点的信息，所以不需要进行复杂的内存管理工作。

完整实现请参考[链接][5]，亲测在Ubuntu 16.04下使用`g++ main.cc -lpthread`编译运行成功。（p.s. 不要加C++11标签，编不过的）

## 相关链接

* [无锁队列的实现 - 酷壳][1]
> 弱弱感觉文章里说的实现有问题

* [无锁队列的分析与设计][2]
> 弱弱感觉实现还是有问题

* [共享内存无锁队列的实现][3]
> 指出了实现上面可能踩到的坑

* [一种高效无锁内存队列的实现][4]
> 环形数组的实现

[1]: https://coolshell.cn/articles/8239.html
[2]: http://www.thinkingyu.com/articles/LockFreeQueue/
[3]: https://cloud.tencent.com/developer/article/1006241
[4]: https://cloud.tencent.com/developer/article/1071029
[5]: https://paste.ubuntu.com/p/vYD6h5sm9n/