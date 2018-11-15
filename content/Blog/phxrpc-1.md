Date: 2016-09-28 22:35:55
Title: 自定义你的stream buffer - phxrpc阅读笔记(1)
Tags: System Design, RPC, streambuf, C++, phxrpc
Slug: phxrpc-1

## 写在前面

[phxrpc](https://github.com/tencent-wechat/phxrpc)是微信团队开源的一个轻量级RPC框架。

我对RPC这些东西了解不多，看到phxrpc的代码相对简单，而且还在初步开发阶段（在本文写作时，版本号是0.8）。所以想读一读，提高一下姿势水平。

就是这样。

## 自定义stream buffer

`network/socket_stream_base.[h|cpp]`中的`class BaseTcpStreamBuf`继承了`std::streambuf`，自定义了一个流缓冲区，用于接收/发送TCP数据包。

这个用法比较新颖（或者是我见识少），网上的资料也不多。这里翻译一篇[介绍文章](http://www.mr-edd.co.uk/blog/beginners_guide_streambuf)，学习一下新姿势。

## A beginner's guide to writing a custom stream buffer

流(streams)是STL中提供的一个重要的抽象概念。著名的“Hello world”程序，便是使用了std::cout将字符串写入标准输出流(stdout)。

流当然可以做比cin/cout更有意思的事。这篇文章我们会研究如何扩展C\++流，来实现自定义的流缓冲区(stream buffer)。p.s. 建议本文的读者至少要有基础的C\++知识。

C++标准库为磁盘文件操作提供了基础的接口，如`std::fstream`，`std::ifstream`和`std::ofstream`。我们还有`stringstream`，可以像流一样操作字符串。
```cpp
std::ostringstream oss;
oss << "Hello, world!\\n";
oss << 123 << '\\n';
std::string s = oss.str();
```

相似的，我们可以从`std::istringstream`中使用`>>`操作符读取数据。

Boost库中的`lexical_cast`正是使用了这种机制，让用户可以使用统一的方式将一个对象(object)转换为字符串表示。
```cpp
using boost::lexical_cast;
using std::string;

int x = 5;
string s = lexical_cast<string>(x);
assert(s == "5");
```
流缓冲区有着很强的灵活性，可以满足不同的“缓冲并传输字符（串）”需求，比如文件操作、字符串操作、命令行(Console)操作等。我们可以从网络、闪存(Flash memory)等不同设备，使用同样的接口获取流式字符串。“流缓冲区”与“流”是正交的，所以我们可以自由的交换、更改(swap and change)流所使用的缓冲区，或者将其重定向到其它地方。我认为C++中的流，正是“策略模式”(strategy design pattern)的一个良好范例。

比如，我们可以重定向标准日志流`std::clog`到一个字符串流：

```cpp
#include <iostream>
#include <iomanip>
#include <string>
#include <sstream>

int main()
{
    std::ostringstream oss;

    // Make clog use the buffer from oss
    std::streambuf *former_buff =
        std::clog.rdbuf(oss.rdbuf());

    std::clog << "This will appear in oss!" << std::flush;

    std::cout << oss.str() << '\\n';

    // Give clog back its previous buffer
    std::clog.rdbuf(former_buff);

    return 0;
}
```
不过，自定义一个流缓冲区却是有一点tricky，或者说有一点吓人，尤其是当你第一次尝试的时候。所以本文意在提供一些流缓冲的实现范例。

首先我们来看一下流缓冲区的一些基本概念。所有的流缓冲区继承自`std::streambuf`，并且需要覆盖一些虚函数来实现自定义功能。`std::streambuf`是“顺序读取设备”的一个抽象，即我们可以从中顺序的读取字符序列。在特定的场景下，我们可以重填(re-fill)、冲洗(flush)以及清空(empty)一个缓冲区。

当我们向一个`ostream`中插入数据时，数据将会被写入缓冲区中的一个数组。当数组上溢(overflow)时，数组中的数据将会被冲洗(flush)到目标接受者，之后这个数组的状态将会重置，以便存储后续的字符。

当我们从一个`istream`中获取数据时，数据从缓冲区的数组中读出。当数组下溢时(underflow)，没有数据可读，我们会从数据源重新拉取信息来填充缓冲区，之后这个数组的状态也将被重置。

我们使用6个指针，来维护缓冲区的内部状态。输入和输出缓冲各使用3个指针。

### 维护输出缓冲区的状态

* put base pointer     
输出基指针，用来指定缓冲区内部数组的第一个元素。可以使用`std::streambuf::pbase()`来获取

* put pointer     
输出指针，用来指向内部数组下一个写入的地址。可以使用`std::streambuf::pptr()`来获取

* end put pointer     
输出哨兵指针，指向内部数组最后一个再后面一个(one-past-the-last-element)的地址（译注：类似`std::vector::end()`）。可以使用`std::streambuf:epptr()`来获取

![](http://i1.piimg.com/567571/630a89fe635e1635.png)

一般来说，基指针和哨兵指针不会改变，在使用时，以输出指针维护内部状态。

### 维护输入缓冲区的状态

输入缓冲区和状态维护和输出缓冲区类似，我们有：

* end back pointer    
输入基指针，指向缓冲区数组内的最后一个字符。可以使用`std::streambuf::eback()`来获取
* get pointer     
输入指针，指向缓冲区下一个读取的字符地址。可以使用`std::streambuf::gptr()`来获取
* end get pointer      
输入哨兵指针，批号向内部数组最后一个再后面一个(one-past-the-last-element)的地址。可以使用`std::streambuf::egptr()`来获取

![](https://github.com/Wizmann/assets/raw/master/wizmann-pic/16-9-27/33500590.jpg)

同样，基指针和哨兵指针在流缓冲区的生命周期中也不会改变。

由于输入缓冲区要支持`putback()`操作，即将读出的字符重新放回缓冲区，所以输入缓冲区比输出缓冲区更复杂一点。通常来说，`putback()`操作支持放回一个字符即可。

一个`std::streambuf`可以同时支持输入输出两种操作，所以我们不需要我分别实现`std::istreambuf`和`std::ostreambuf`。`std::fstream`是一个良好的例子。但是，实现一个全功能的缓冲区相对更复杂一些，所以我就不趟浑水啦~ ：）

同时，流缓冲区也可以支持宽字符(wide character)。`std::streambuf`是`std::basic_streambuf<char>`的别名，如果你需要宽字符流缓冲区，可以使用`std::basic_streambuf<wchar_t>`。

### 例1：文件缓冲区 —— 与C代码集成

假设我们需要调用一个历史悠久的库，一个文件操作函数会返回给一个`FILE*`指针，但是我们想用C++的流接口来读写数据。我们先从读文件开始，用`std::istream`包装`FILE*`的读操作。

```cpp
#include <streambuf>
#include <vector>
#include <cstdlib>
#include <cstdio>

class FILE_buffer : public std::streambuf
{
    public:
        explicit FILE_buffer(FILE *fptr, std::size_t buff_sz = 256, std::size_t put_back = 8);

    private:
        // overrides base class underflow()
        int_type underflow();

        // copy ctor and assignment not implemented;
        // copying not allowed
        FILE_buffer(const FILE_buffer &);
        FILE_buffer &operator= (const FILE_buffer &);

    private:
        FILE *fptr_;
        const std::size_t put_back_;
        std::vector<char> buffer_;
};
```

由于功能简单，我们只需要实现构造函数以及`underflow`接口就可以实现我们的功能。

构造函数指定了读取文件的`FILE*`指针，以及内部缓冲数组的大小。数组大小由两个参数决定：
* put-back area size         
* buffer size

我们使用`std::vector<char>`做为缓冲区域。`put_back_`变量用于存储"put-back"区域的大小。

以下是构造函数的实现：

```cpp
using std::size_t;

FILE_buffer::FILE_buffer(FILE *fptr, size_t buff_sz, size_t put_back) :
    fptr_(fptr),
    put_back_(std::max(put_back, size_t(1))),
    buffer_(std::max(buff_sz, put_back_) + put_back_)
{
    char *end = &buffer_.front() + buffer_.size();
    setg(end, end, end);
}
```

在初始化列表中，我们将缓冲区的常量进行赋值。之后使用`std::streambuf::setg()`来初始化输出缓冲区。

`setg()`的三个参数分别代表`eback()`，`gptr()`，`egptr()`三个内部指针的值。一开始，我们将它们都指向同一个地址。表明buffer是空的，在下一次读取时，会重新填充缓冲区。

`underflow()`会返回数据源中当前的字符。一般来说，会返回buffer中的下一个可用字符。然后当buffer为空时，`underflow()`应该重新填充缓冲区数组，在本例中，即从`FILE*`中读取字符。当缓冲区重填后，我们需要再次调用`setg()`更新流缓冲区的状态。

当数据源中的数据读完(depleted)后，`underflow()`会返回一个`traits_type::eof()`。这里要注意，`underflow()`的返回值是`int_type`，这个值足够装下`eof()`，同时也足够装下任何的字符。

```cpp
std::streambuf::int_type FILE_buffer::underflow()
{
    if (gptr() < egptr()) // buffer not exhausted
        return traits_type::to_int_type(*gptr());

    char *base = &buffer_.front();
    char *start = base;

    if (eback() == base) // true when this isn't the first fill
    {
        // Make arrangements for putback characters
        std::memmove(base, egptr() - put_back_, put_back_);
        start += put_back_;
    }

    // start is now the start of the buffer, proper.
    // Read from fptr_ in to the provided buffer
    size_t n = std::fread(start, 1, buffer_.size() - (start - base), fptr_);
    if (n == 0)
        return traits_type::eof();

    // Set buffer pointers
    setg(base, start, start + n);

    return traits_type::to_int_type(*gptr());
}
```
函数的第一行，首先判断buffer是否耗尽。如果否，则返回当前字符，即`*gptr()`。如果是，则进行重填(re-fill)操作。

回想一下我们在构造函数中的实现，三个状态指针全都指向缓冲区的末尾。如果我们调用`underflow()`时，发现状态指针并非如此，则说明缓冲区已经被填充了至少一次。

现在我们考虑重填操作，我们`memmove`最后`put_back_`个字符到buffer的末尾，用做"put-back area"。（我们不用`memcopy`因为我们的buffer比较小，`memmove()的效率会更高一些）

> 译注：实际上，`memcopy`与`memmove`各有所长。`memcopy`不需要判断内存overlap的情况，即如果源区间与目标区间有重叠，那么得到的结果会是错的。而`memmove`由于是移动语义，所以在移动步长较小时，可以只操作cache。所以二者各有所长，要根据具体情况判断优劣。Stackoverflow上有更详细的[讨论][1]

我们处理完"put-back area"之后，就可以使用`fread()`函数来重填缓冲区了。如果读不到数据，则意味着文件已经读到了结尾（当然这是一种简化情况，但在现实中99.9%的读取失败都是因为文件结束）。

在`fread()`成功读取数据之后，我们通知streambuf更新内部的三个状态指针。之后返回buffer当前的指针。

这就是我们的流缓冲区的基本实现，希望这并不是太难。当然我们还可以添加更多的功能。特别的是我们可以在缓冲区里面进行查找。如果你想实现它的话，可以试试重写`std::streambuf::seekoff()`和`std::streambuf::seekpos`虚成员函数。

我们也可以实现写缓冲区。不过，在你们读完第三个例子之后，你们就可以轻松愉快的实现自己的版本了，不骗你。

### 例2：读取内存中的数组

本例中，我们要使用`std::istream`包装内存中的一个只读数组，并且格式化的进行读入。这个例子和上一个例子有一点不同的是，我们并不需要一个真正的缓冲数组，从源数组一次性读取就好了。

想象中的实现是这个样式儿的：

```cpp
class char_array_buffer : public std::streambuf
{
    public:
        char_array_buffer(const char *begin, const char *end)
        {
            setg(begin, begin, end);
        }

        int_type underflow()
        {
            return  gptr() == egptr() ?
                    traits_type::eof() :
                    traits_type::to_int_type(*gptr());
        }
};
```

但是，这并没有什么卵用。因为`setg()`函数只接受非常量(non-const)指针参数。这显而易见，如果一个缓冲区不可写，我们就不能提供"put-back"功能。所以我们要动一动手脚，重新实现一下这个类。

```cpp
#include <streambuf>

class char_array_buffer : public std::streambuf
{
    public:
        char_array_buffer(const char *begin, const char *end);
        explicit char_array_buffer(const char *str);

    private:
        int_type underflow();
        int_type uflow();
        int_type pbackfail(int_type ch);
        std::streamsize showmanyc();

        // copy ctor and assignment not implemented;
        // copying not allowed
        char_array_buffer(const char_array_buffer &);
        char_array_buffer &operator= (const char_array_buffer &);

    private:
        const char * const begin_;
        const char * const end_;
        const char * current_;
};
```

在这个版本中，我们重写了几个私有函数，这些函数都是从`std::streambuf`继承而来。

第一个构造函数需要用户指定起止指针，而第二个构造函数只需要指定起始指针，之后我们会调用`std::strlen()`来判断字符串的大小。

我们使用`uflow()`, `pbackfail()`和`showmanyc()`来维护缓冲区内部的状态，而不是调用`setg()`，因为buffer并不可写。

在这个版本中，我们要手动维护`eback`, `gptr`, `egptr`三个指针。在构造函数中，我们将对其进行赋值。

```cpp
#include "char_array_buffer.hpp"

#include <functional>
#include <cassert>
#include <cstring>

char_array_buffer::char_array_buffer(const char *begin, const char *end) :
    begin_(begin),
    end_(end),
    current_(begin_)
{
    assert(std::less_equal<const char *>()(begin_, end_));
}

char_array_buffer::char_array_buffer(const char *str) :
    begin_(str),
    end_(begin_ + std::strlen(str)),
    current_(begin_)
{
}
```

之前我们使用`underflow()`来获取当前字符，但这次我们需要使用`uflow()`。因为`uflow()`需要同时执行两步操作，一是获取当前字符，二是让`gptr()`前进一步。但是又因为缓冲区由我们手动管理，`std::streambuf`并不能正确的执行管理操作。所以我们需要重写`uflow()`而不是`underflow()`。

```
char_array_buffer::int_type char_array_buffer::uflow()
{
    if (current_ == end_)
        return traits_type::eof();

    return traits_type::to_int_type(*current_++);
}
```

下一步我们还要实现`pbackfail()`。当我们调用`std::istream::unget()`或`std::istream::putback(ch)`时，我们会把已经读出的数据写回数组中。但是由于数组是只读的，所以我们只能模拟这种操作。

在默认的实现中`pbackfail()`只会返回`traits_type::eof()`，而在我们的版本中，如果写回成功，将会返回写回的字符，不成功返回eof。

```cpp
char_array_buffer::int_type char_array_buffer::pbackfail(int_type ch)
{
    if (current_ == begin_ || (ch != traits_type::eof() && ch != current_[-1]))
        return traits_type::eof();

    return traits_type::to_int_type(*--current_);
}
```

在`FILE_buffer`中，我们也可以考虑重写`pbackfail()`，来提供反向查找以及（用前面的数据）重填buffer的功能。

最后一个重写的函数是`showmanyc()`，这个函数被`std::streambuf::in_avail()`调用，以判断当前有多少个字符可以返回。由于我们接管了状态指针，所以这个函数也要我们自己来实现啊。（译者：为什么要给自己找麻烦。。。）

```cpp
std::streamsize char_array_buffer::showmanyc()
{
    assert(std::less_equal<const char *>()(current_, end_));
    return end_ - current_;
}
```

由此可见，本例中的buffer比前面的要复杂一点点。这是因为我们接管了状态维护的工作。这使得我们更好的理解了`std::streambuf`内部是如何工作的。

### 例3：句首变大写的缓冲区

本例中我们将要实现一个将句首字符变大写的buffer。当然我们只考虑最基本的情况，移植到不同的区域和语言，其实是很琐碎的事情。（译者：文字编码坑的亲妈都不认了）

```cpp
#include <streambuf>
#include <iosfwd>
#include <cstdlib>
#include <vector>

class caps_buffer : public std::streambuf
{
    public:
        explicit caps_buffer(std::ostream &sink, std::size_t buff_sz = 256);

    protected:
        bool do_caps_and_flush();

    private:
        int_type overflow(int_type ch);
        int sync();

        // copy ctor and assignment not implemented;
        // copying not allowed
        caps_buffer(const caps_buffer &);
        caps_buffer &operator= (const caps_buffer &);

    private:
        bool cap_next_;
        std::ostream &sink_;
        std::vector<char> buffer_;
};
```

这里我们需要重写`overflow()`和`sync()`函数。`overflow()`在输入缓冲区满的时候被调用，并且在成功时返回任意非eof的值。

`sync()`的作用是把当前的buffer写入目标，即使当前buffer并未填满。`std::flush()`会调用`sync()`函数，当失败时返回-1。

我们编写一个辅助函数`do_caps_and_flush()`，用来将小写变大写，并写入`sink_`输出流。我们再声明一个哨兵变量`cap_next_`来标识下一个字符是否需要小写变大写。

```cpp
#include "caps_buffer.hpp"

#include <cctype>
#include <ostream>
#include <functional>
#include <cassert>

caps_buffer::caps_buffer(std::ostream &sink, std::size_t buff_sz) :
    cap_next_(true),
    sink_(sink),
    buffer_(buff_sz + 1)
{
    sink_.clear();
    char *base = &buffer_.front();
    setp(base, base + buffer_.size() - 1); // -1 to make overflow() easier
}
```

`buffer_`的最小可能大小是1，同时我们也只需要维护两个指针，因为这里不需要像输入缓冲区一样的维护"put-back area"。

我们把`buffer_`的大小设成`buff_sz + 1`，这样是为了`overflow()`被调用时，我们有一个额外的空间存储当前的字符。最后将缓冲区数组和最后一个字符一起刷新到`ostream`中。


```cpp
caps_buffer::int_type caps_buffer::overflow(int_type ch)
{
    if (sink_ && ch != traits_type::eof())
    {
        assert(std::less_equal<char *>()(pptr(), epptr()));
        *pptr() = ch;
        pbump(1);
        if (do_caps_and_flush())
            return ch;
    }

    return traits_type::eof();
}
```

第一步是把ch写入`buffer_`，并且使用`pbump(1)`将`pptr()`向前移一位。之后调用`do_caps_and_flush()`做一些脏活，之后返回一个字符声明调用成功。

`sync()`的实现也非常简单:

```cpp
int caps_buffer::sync()
{
	return do_caps_and_flush() ? 0 : -1;
}
```

我们再看一看`do_caps_and_flush()`函数
```cpp
bool caps_buffer::do_caps_and_flush()
{
    for (char *p = pbase(), *e = pptr(); p != e; ++p)
    {
        if (*p == '.')
            cap_next_ = true;
        else if (std::isalpha(*p))
        {
            if (cap_next_)
                *p = std::toupper(*p);

            cap_next_ = false;
        }
    }
    std::ptrdiff_t n = pptr() - pbase();
    pbump(-n);

    return sink_.write(pbase(), n);
}
```

对于本例来说，内部的缓冲区并非必要，我们可以一个字符一个字符把数据发到`sink`中。但是我的观点是一个内部buffer仍有其用处。

### 介绍 Boost IOStreams 库

如果你是流缓冲区的新手，希望你已经对它有一点点了解了。本文中的例子都非常基础，但是你可以用它们做更多有意思的事情。但是当我实现更复杂的流缓冲区时，问题的复杂度却上升的很快。这时我发现了`Boost IOStreams`库，它为更复杂的缓冲区和流提供了必要的框架支持。

它允许你解耦数据源，数据输出，过滤器以及其它一些概念。在我们的最后一个例子中，我们硬编码数据输出到`std::ostream`中。如果我们要输出到一个没有流接口的类呢？`Boost IOStreams`库提供了更多的灵活性，将一坨紧耦合的代码分解成独立的抽象概念。


### 扩展阅读

* The C++ Standard Library by Nicolai M. Josuttis
* The C++ Standard, BS ISO/IEC 14882:2003 (Second Edition)
* [Dinkum Compleat Reference online][2]

[1]: http://stackoverflow.com/questions/28623895/why-is-memmove-faster-than-memcpy
[2]: http://www.dinkumware.com/manuals/
