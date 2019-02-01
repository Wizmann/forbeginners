Date: 2019-02-01
Title: C++类型擦除与`std::function`性能探索
Tags: C++, modern C++, std::function
Slug: cpp-type-erasure-and-std-function

## 什么是类型擦除

对于Python这种动态类型语言来说，是不存在“类型擦除”这个概念的。Python对象的行为并不由接口定义，而是由“当前方法和属性的集合”决定。

所以，以下的代码是完全合法的：

```python
class Foo(object):
    def print(self):
        print 'foo'
        
class Bar(object):
    def print(self):
        print 'bar'
        
def do_print(obj):
    print obj.print()
    
do_print(Foo()) // print 'foo'
do_print(Bar()) // print 'bar'
```

但是对于C++这种静态类型语言来讲，我们就不能使用这种语法：

```cpp
class Foo {
public:
    void print() { cout << "foo" << endl; }
};

class Bar {
public:
    void print() { cout << "bar" << endl; }
};

void do_print(??? obj) { // <--
    obj.print();
}

do_print(Foo());
do_print(Bar());
```

熟悉C++的同学们都知道，因为`Foo`和`Bar`的类型不同，我们不能直接将不同类型的实例传入`do_print(obj)`函数。所以我们需要一种方法擦除类型信息，提供一种类型的抽象。使得实现不依赖于具体类型，而是依赖于类型抽象。

## C++中类型擦除的实现

### 简单粗暴 - `void*`

写过C语言同学们一定非常熟悉`qsort`函数的写法：

```c
// http://www.cplusplus.com/reference/cstdlib/qsort/
int compare (const void * a, const void * b) {
    return ( *(int*)a - *(int*)b );
}

int main () {
    int values[] = {1, 3, 5, 2, 4, 6};
    qsort (values, 6, sizeof(int), compare);
    for (int i=0; i<6; i++)
        printf ("%d ",values[n]);
  return 0;
}
```

这里的`compare(const void*, const void*)`函数就是C语言风格的类型擦除，可以支持不同类型的指针类型传入。但是缺陷是在函数中，我们仍然需要将已擦除的类型恢复，以读取其中的数据。

这种类型擦除方法，并不会带开额外的开销。但是这样的强制类型隐含着类型不匹配的风险，需要程序员格外注意。

### 面向对象的经典方法 - 虚函数（virtual function）

C++做为C语言的进化，引入了面向对象的理念。而多态，做为面向对象编程的一个重要特性，为我们的代码带来了更多的弹性。

对于上面的例子，我们可以使用以下的代码来实现：

```cpp
class IPrintable {
public:
    virtual void print() = 0;
};

class Foo : public IPrintable {
public:
    virtual void print() { cout << "foo" << endl; }
};

class Bar : public IPrintable {
public:
    virtual void print() { cout << "bar" << endl; }
};

void do_print(IPrintable* obj) {
    obj->print();
}

int main() {
    do_print(new Foo());
    do_print(new Bar());
    return 0;
};
```

在这里，我们使用了一个`IPrintable`基类，擦除了子类`Foo`和`Bar`的具体类型信息。也就是说，只要子类实现了基类的接口，就可以做为参数传入`do_print(obj)`中。这样的好处是我们只需要为继承同样接口的类型完成一套实现，提供了更好的封装与抽象。

但是，这种实现的问题在于虚函数的调用是有额外的开销的。需要进行一次运行时虚表的查找，才可以确定对象需要调用哪一个函数。

### 使用模板（template）

C++提供了模板，支持将类型以模板参数形式传入参数。使得我们可以以一种独立于特定类型的方式编写代码。

我们可以改写上文中的`do_print(obj)`函数，使其可以支持不同的类型：

```cpp
template <typename T>
void do_print(T obj) {
    obj.print();
}
```

这里，传入参数的类型`T`无需继承`IPrintable`接口，只要其实现了`print()`成员函数即可做为对象传入。

C++模板的类型擦除作用于编译期，可以尽早的发现风险，同时（一般来说）不影响运行时的性能。

> 注意：Java/C#的泛型(generic)语法与C++的模板非常类似，但是Java/C#的泛型是作用于运行时的。这里注意区分二者的区别。

但是模板也有其局限性。模板有隐含的接口语义，但是由于模板所使用的对象并没有共同的基类（接口），所以它不能使用一个统一的容器来储存对象。

```cpp
??? objs[] = { new Foo(), new Bar() };
```

## C++类型擦除实战 —— `std::function`

在C语言中，我们要表示一个函数对象只能使用函数本身以及函数指针。但是在C++中，我们有了更多的选择：

* 函数
* inline lambda
* 函数指针（C-style）
* 仿函数（factor class）
* `std::bind`
* `std::function`

上面的这些对象，我们可以统称为可调用（callable）对象。也就是说，我们可以使用类似`f(obj)`的语法，以函数形式调用这些对象。

思考以下的场景：我们想要实现一个回调函数。这个函数是用户定义的，可以是以上可调用对象的任意一种。那么我们应该用什么类型来表示这个回调函数对象呢？

是的，答案就是`std::function`。C++中的`std::function`为我们提供了对可调用对象的抽象。我们可以使用`std::function`封装可调用对象，从而擦除其类型信息，使用统一的方法对其进行调用。

请参考以下代码：

```cpp
// http://www.cplusplus.com/reference/functional/function/function/
#include <iostream>     // std::cout
#include <functional>   // std::function, std::negate

// a function:
int half(int x) {return x/2;}

// a function object class:
struct third_t {
  int operator()(int x) {return x/3;}
};

// a class with data members:
struct MyValue {
  int value;
  int fifth() {return value/5;}
};

int main () {
  std::function<int(int)> fn1 = half;                    // function
  std::function<int(int)> fn2 = &half;                   // function pointer
  std::function<int(int)> fn3 = third_t();               // function object
  std::function<int(int)> fn4 = [](int x){return x/4;};  // lambda expression
  std::function<int(int)> fn5 = std::negate<int>();      // standard function object

  std::cout << "fn1(60): " << fn1(60) << '\n';
  std::cout << "fn2(60): " << fn2(60) << '\n';
  std::cout << "fn3(60): " << fn3(60) << '\n';
  std::cout << "fn4(60): " << fn4(60) << '\n';
  std::cout << "fn5(60): " << fn5(60) << '\n';

  // stuff with members:
  std::function<int(MyValue&)> value = &MyValue::value;  // pointer to data member
  std::function<int(MyValue&)> fifth = &MyValue::fifth;  // pointer to member function

  MyValue sixty {60};

  std::cout << "value(sixty): " << value(sixty) << '\n';
  std::cout << "fifth(sixty): " << fifth(sixty) << '\n';

  return 0;
}
```

### `std::function`的缺陷

`std::function`的类型擦除功能异常强大，几乎可以封装所有的可调用类型。但是，语法上面的便利却会带来了性能上的损失。

从[benchmark][1]结果上我们可以看出，在`O2`的优化参数下，函数调用（包括函数、函数模板和仿函数）、函数指针和lambda的性能相仿。而虚函数大概需要花费5倍左右的时间，而`std::function`则需要花费6倍以上的时间。对于一个会被经常调用到的函数，带来的额外的性能开销是不可以忽略的。

|        method          |  Linux (Azure VM, E5-2673 v3, -O0)  |    Linux (Azure VM, E5-2673 v3, -O2)  |
|------------------------|-----------------------------------:|---------------------------------------:|
|    Function            |                           12.4s    |                                1.2s    |
|    Function Ptr        |                           13.5s    |                                1.2s    |
|    Inline Lambda       |                           12.7s    |                                1.2s    |
|    Virtual Function    |                           14.1s    |                                6.3s    |
|    std::function       |                           77.3s    |                                7.2s    |

究其原因，是由于`std::function`的模板参数中只提供了参数类型和返回值类型，所以为了进行类型擦除，其中内置了一个虚函数。所以一次`std::function`调用会引发隐式的多次函数调用，其中还包含着一次虚函数的调用。所以性能下降也就不难解释了。

### 解决方案

可以确定的是，除非必要，不要使用`std::function`。

例如，在`std::sort`中，我们使用模板传入可调用类型，这样就可以避免`std::function`的额外开销：

```cpp
template< class RandomIt, class Compare >
void sort( RandomIt first, RandomIt last, Compare comp );
```

又例如我们可以避免使用不同的可调用类型来规避类型擦除，如统一使用函数指针。在C++14之后，inline lambda也可以表示为函数指针，所以我们也可以通过闭包来封装其它的可调用对象了。

当然，也可以自己造个[轮子][4]，这就又是另一个故事了。

## 写在最后

新的C++规范给我们带来了很多的语法糖。对于传统C++程序员来说，好处在于我们可以写出更舒服的，更符合直觉的代码，但缺点是我们需要了解更多语言背后的东西。所以对于自己不熟悉的新式语法，无论看起来多么诱人，也需要多加谨慎。

## 参考链接

* [Benchmark for "function pointer", "virtual function" and "std::function"][1]
* [C++ Core Guidelines: Type Erasure][2]
* [C++ 'Type Erasure' Explained][3]

[1]: https://gist.github.com/Wizmann/30073037f31d796efd6f42798dd85aee
[2]: http://www.modernescpp.com/index.php/c-core-guidelines-type-erasure
[3]: http://davekilian.com/cpp-type-erasure.html
[4]: https://codereview.stackexchange.com/questions/14730/impossibly-fast-delegate-in-c11
