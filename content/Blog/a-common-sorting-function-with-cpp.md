Date: 2015-04-25 11:17:01 
Title: 用C++实现一个通用的sort函数
Tags: C++, sort
Slug: a-common-sorting-function-with-cpp

## 问题

用C++实现一个尽可能通用的sort函数

## 分析

一个通用的sort函数应该包含以下要点：

* 确实可以排序(LOL)
* 可以应对C-style array和C++-style container的排序需求
* 可以应用于任意random access container
* 可以使用用户自定义的排序函数 / 仿函数 / lambda函数

## 实现

为了与std中的通用函数做区别，这里的命名规则，包括类型与函数，都在前面加了"my"以示区别。可能与标准的命名法有出入，所以仅做示例用。

### 思路

** 拷贝代码是愚蠢的行为。**

或者说，

** 对于同一钟实现，尽量使用同一份代码。 **

感谢C++ Templates，对于不同类型与需求的函数，我们可以将生成多份代码的劳动放心的交给编译器。并且，Templates的代码生成是在编译期完成的，即不会造成额外的代码膨胀（如果你姿势正确的话），也一般不会造成额外的运行时开销。

### 函数原型

我们模仿std::sort来进行开发。

```
template< class It, class Compare >
void sort(It first, It last, Compare comp );
```

### 从迭代器/指针获得元素类型

我们要处理C风格的数组与C++网络的容器。首先要从迭代器/指针`It`中获得元素类型。

```cpp
template<typename It>
struct myiter_traits {
    typedef typename It::value_type value_type;
};

template<typename T>
struct myiter_traits<T*> {
    typedef T value_type;
};
```

这个实现非常简单，不做赘述。

### 实现mysort函数

```cpp
template<typename RandomAccessor, typename FUNC>
void mysort(
        const RandomAccessor& head,
        const RandomAccessor& tail,
        FUNC cmp) 
{
    if (tail - head <= 1) {
        return;
    }
    const RandomAccessor pivot = mypartition(head, tail, cmp);

    mysort(head, pivot, cmp);
    mysort(pivot + 1, tail, cmp);
}
```

mysort函数本体并不难理解，这里重点讨论一下模板的思路。

由于迭代器不需要移动，所以声明为const reference。又由于我们需要兼容各种不同类型的排序方法（函数、仿函数、lambda、std::function等），所以不对`FUNC`类型进行限制，即所有可以被call的类型都可以做为模板参数。

### 实现mypartition函数

快速排序的灵魂就是快速划分。如果处理得当，quick sort可以视作一个稳定的排序函数；否则，一组构造（不必要精心构造）的数据就可以把quick sort变成"slow sort"。

#### 可能会上quick sort退化的数据

* 基本一致的数据     
e.g. `1, 1, 1, 1 ... 1, 1` or `1, 1, ... 2, 2, ... 3, 3`
* 有序或基本有序的数据    
e.g. `1, 2, ... 5, 6` or `6, 5, ... 2, 1`

#### 解决思路

对于有大量重复的数据，我们在处理时要注意平均分配这些重复数据。即，对于与pivot相等的数据，尽量保证一半放在左面，一半放在右面。

对于有序或基本有序的数据，我们在pivot的选择上可以使用随机、三值法等手段，保证数据的平均分配。

总的说来，quick sort的高效性，取决于partition函数的平均分配性能上。

#### 一个实现

```cpp
template<typename RandomAccessor, typename FUNC>
RandomAccessor mypartition(
        const RandomAccessor& head,
        const RandomAccessor& tail,
        FUNC cmp) 
{
    auto dis = distance(head, tail);
    RandomAccessor pivot = head + rand() % dis;
    iter_swap(pivot, head);
    pivot = head;
    
    RandomAccessor l = head;
    RandomAccessor r = tail - 1;
    int ptr = 0;
    while (l <= r) {
        while (l <= r) {
            bool lt = cmp(*l, *pivot);
            bool gt = cmp(*pivot, *l);
            bool eq = !lt && !gt;
            if (lt || (eq && ptr == 0)) {
                l++;
                ptr ^= (eq? 1: 0);
            } else {
                break;
            }
        }
        while (l <= r) {
            bool lt = cmp(*r, *pivot);
            bool gt = cmp(*pivot, *r);
            bool eq = !lt && !gt;
            if (gt || (eq && ptr == 1)) {
                r--;
                ptr ^= (eq? 1: 0);
            } else {
                break;
            }
        }
        if (l <= r) {
            swap(*l, *r);
            l++;
            r--;
        }
    }
    iter_swap(pivot, r);
    return r;
}
```

### 主函数

```cpp
int main() {
    srand(time(NULL));
    
    vector<int> vec({2, 1, 3, 0, 4, 1999});

    mysort(vec.begin(), vec.end(), less<int>());
    for (const auto& i: vec) {
        printf("%d ", i);
    }
    puts("");

    int array[] = {99, 19, 9999};
    mysort(array + 0, array + 3, 
            [](int a, int b)->bool { return a > b; });
    for (int i = 0; i < 3; i++) {
        printf("%d ", array[i]);
    }
    puts("");
    
    return 0;
}
```


