Date: 2013-12-09 15:01
Title: 使用新类型创建更人性化的代码
Tags: cpp
Slug: humanity-code-with-new-classes

## 啥？

这篇文章讨论了如何通过新建并非”必要“的新类型，来产生更人性化的C++代码。

关键词：

* RAII
* 智能指针
* 接口友好
* 模板
* 模板特化
* 依赖编译器的缺省行为


对于C++的艺术，我只是个入门者。如果文章中有什么问题，欢迎大家指出，我会及时进行修改。

## 一个友好的互斥锁

### 互斥锁的定义

> 互斥锁（英语：英语：Mutual exclusion，缩写 Mutex）是一种用于多线程编程中，防止两条线程同时对同一公共资源（比如全局变量）进行读写的机制。该目的通过将代码切片成一个一个的临界区域（critical section）达成。临界区域指的是一块对公共资源进行访问的代码，并非一种机制或是算法。一个程序、进程、线程可以拥有多个临界区域，但是并不一定会应用互斥锁。

### 如何使用互斥锁

这里只做最简单的示范。具体的使用方法和原理不在本文的讨论范围之内。

```cpp
#include <pthread.h>

class MyIntArray {
// 一个假想的数组类型，支持多线程下的Append Only操作。
public:
    MyIntArray()
    {
        _vec.clear();
        pthread_mutex_init(&_mutex, NULL);
    }
    
    int push_back(int v)
    {
        pthread_mutex_lock(&_mutex);
        //
        // 在这里做一些工作, 例如打Log，抽风等
        //
        vec.push_back(v);
        pthread_mutex_unlock(&_mutex);
        return 0;
    }
private:
    pthread_mutex_t _mutex;
    vector<int> _vec; 
};

```

代码不需要多解释，通过一个锁来保证多线程push_back函数的可重入性。

但是我们需要对代码的安全性做一些评估。

例如，我们如何处理，函数在unlock mutex之前异常结束的情况。

这并不是不可能的，例如``vec.push_back(v)``抛出了一个``std::bad_alloc``异常。或者在这之前因为一些原因，函数做出了``return -1``的行为。

也许我们在逻辑上可以接受这些错误（比如做出一些失败处理）。但是，对于因为我们没有unlock我们的同步锁，于是死锁就产生了。

这是一个极大的隐患，死锁的危害我也不用多说。

那么我们有什么方法可以避免这种局面。

### 一个新的Mutex类型

我们可以使用**析构函数**的特性来编写如下的类。

```cpp
#include <pthread.h>

class Mutex {
public:
    Mutex(explicit pthread_mutex_t* i_mutex_ptr):
            _mutex(i_mutex_ptr){}

    void lock()
    {
        pthread_mutex_lock(_mutex);
    }

    ~Mutex()
    {
        pthread_mutex_unlock(_mutex);
    }
private:
    Mutex(); // disable the empty construct funtion
    pthread_mutex_t *_mutex;
}
```

OK，如果我们使用这个类做为同步锁的管理类，那么，如果函数中出现了非预期的情况而跳出的时候。``Mutex``类就会自动调用自身的析构函数来解锁。避免了死锁的发生。

### 总结

``pthread_mutex_t``是一个类型，但是我们在这个类型之上又新建了一个新的类型来进行资源管理。以此来获得更人性化，更安全以及更可读的代码。

### 拓展阅读

* [Pthreads mutex vs Pthreads spinlock][1]

对于mutex和spinlock有一个详细的介绍，并且对比了这两种锁的性能。

* Effective C++ 条款14

以上的例子来源于此，并且做了一些简化。

## 句柄类

我们都知道，由于C++没有自动内存回收机制，所以内存操作都需要代码编写者手动完成。

这就造成了潜在的内存泄露问题 ———— 不小心手贱怎么办？

于是我们就引入了句柄类，一种使用**引用计数法**来管理内存的方法。

### 一个泛型句柄类

代码来自《C++ Primer 第4版》，有小小的格式上的改动。

```cpp
/* generic handle class: Provides pointerlike behavior. Although
access through
* an unbound Handle is checked and throws a runtime_error exception.
* The object to which the Handle points is deleted when the last
Handle goes away.
* Users should allocate new objects of type T and bind them to a
Handle.
* Once an object is bound to a Handle,, the user must not delete
that object.
*/
template <class T> class Handle {
public:
    // unbound handle
    Handle(T *p = 0): ptr(p), use(new size_t(1)) { }

    // overloaded operators to support pointer behavior
    T& operator*();
    T* operator->();
    const T& operator*() const;
    const T* operator->() const;

    // copy control: normal pointer behavior, but last Handle deletes the object
    Handle(const Handle& h): ptr(h.ptr), use(h.use) { ++*use; }

    Handle& operator=(const Handle&);
    ~Handle() { rem_ref(); }

private:
    T* ptr;
    // shared object
    size_t *use;
    // count of how many Handle spointto *ptr
    void rem_ref()
    { 
        if (--*use == 0) { delete ptr; delete use; } 
    }
};

```

我们从代码中可以看到，Handle类中使用了``size_t *use``用来对于对象进行引用计数。如果计数为0，则Handle类会删除自身。也许我们会忘记释放内存，但是编译器会帮你管理好你的对象的。

### 句柄类的另一个优点

句柄类的另一个优点是可以降低文件间的编译依存关系。

句柄类可以将接口从实现中分离，从而分离编译依赖。

例如，我们有一个``Person``类，又声明了``PersonImpl``句柄类。

则我们如果修改了``Person``类的实现部分，并且保持接口部分不变。则我们只需要重新编译含入``Person``类的文件。含入``PersonImpl``类的文件不需要重新编译。

### shared_ptr

shared_ptr是boost中引入的新类型，原理和句柄类类似，但是加入了如下特性。

* 线程安全
* 支持自定义析构操作（删除器）
* 有现成的库为啥不用

在《Effective C++》一书中，作者对于``shared_ptr``大为推崇，用了很大篇幅来介绍它的用法，在这里就不赘述了。

### 潜在问题

有失有得，我们在一定程度上提升了内存安全性的同时，我们也必须付出一定的代价。

* 内存性能问题

我们的一个句柄类或智能指针中，不仅有我们的对象指针，而且还保存着引用计数。如果我们处于内存敏感的场景，那么我们必须认真的考虑收益和代价。

* 计算性能问题

如果我们的句柄类需要线程安全性，那么我们也必须要付出相应的时间上的代价。

### 拓展阅读

* 《Effective C++》第三章 资源管理

* 《C++ Primer第四版》 16.5 一个泛型句柄类

## 防止接口误用

Python有一个非常好的特性（也许别的语言也有）。例如：

```python
def pass_date(year, month, day):
    pass

def foo:
    pass_date(year=1234, month=5, day=6)
```

在函数的调用中，可以明确形参与实参的对应关系。这就可以从很大程度上解决了接口误用的问题。

而在C++中，我们可以使用新建类型来解决这个问题。

还以``pass_date``这个函数为例。

```cpp
struct Year {
    explicit int year;
};

struct Month {
    explicit int month;
};

struct Day {
    explicit int day;
};

class Date {
public:
    void pass_date(Year year, Month month, Day day) {
        // pass
    }
};

void foo()
{
    Date date;

    date.psss_date(Year(1234), Month(5), Day(6));
}

```

## 偏特化类中的成员函数

这个方法来源于stackoverflow上的一个[问题][2]。

我比较推崇下面这个答案，虽然它不是被顶的最多的那个。

```cpp
template <typename Group, int p>
struct ApplyNorm
{
    static Group apply(Group x, Group y, Group z)
    { return pow( pow(x, p) + pow(y, p) + pow(z, p), (1.0 / p) ); }
};

// Here specialize for 2
template <typename Group>
struct ApplyNorm<Group, 2>
{
    static Group apply(Group x, Group y, Group z)
    { 
        std::cout << "spec: " << std::endl;
        return sqrt( x * x + y * y + z * z ); 
    }
};


template<typename Group>
struct Vector3D {
    Group x, y, z;
    Vector3D(Group x, Group y, Group z) : x(x), y(y), z(z) {
    }
    template<int p> Group Norm() const;
};

template<typename Group> template<int p> 
Group Vector3D<Group>::Norm() const {
    return ApplyNorm<Group, p>::apply(x, y, z); // use the helper...
}

int main() {
    // your code goes here
    Vector3D<double> v(1., 2., 3.);
    std::cout << v.Norm<1>() << std::endl;
    std::cout << v.Norm<2>() << std::endl;
    return 0;
}
```

它使用一个新类``ApplyNorm``实现了类成员函数的偏特化。

### 拓展阅读

《C++ Primer第4版》 16.6 模板特化


[1]: http://www.searchtb.com/2011/01/pthreads-mutex-vs-pthread-spinlock.html 

[2]: http://stackoverflow.com/questions/20147821/c-how-to-partial-specialization-a-template-function-in-a-template-class
