Date: 2014-09-21
Title: FlatBuffer代码阅读 - 1
Tags: flatbuffer
Slug: read-flatbuffer-1


## FlatBuffer白皮书

Flatbuffer是一个全新的序列化库。

### 动机

在远古时代，程序性能基本取决于你的指令和循环运行的有多快。但是，在如今的计算机上，计算组件的速度已经远远超过存储组件的速度。如果你想让你的程序飞起来，最重要的就是优化你的内存使用。例如，用多少内存，怎样布局内存，如何分配内存，何时拷贝内存等。

序列化是在程序中非常常见的一种操作，并且通常是程序性能低下的主要原因。一是由于序列化需要额外的临时空间去解析和表示数据，二是由于不优雅的内存分配模式和局部性。

如果一个序列化框架可以不使用额外的对象，没有额外的内存分配，没有内存拷贝，良好的数据局部性，这正是太好不过。不过当下的很多框架通常不能满足以上的条件，因为它们需要向前/向后兼容，需要兼容不同的平台，例如大端/小端和内存对齐都是需要进行兼容性处理的。

FlatBuffer可以做到以上的一切。

Flatbuffer尤其适合移动设备（内存容量和带宽比桌面设备的要低不少），以及需要高性能的应用：游戏。

### FlatBuffers

#### 总述

Flatbuffer是一个二进制的buffer。Flatbuffer可以包含嵌套对象如struct、table、vector等并使用偏移量来进行寻址，这样一来，我们就可以像遍历基于指针的结构一样，对flatbuffer元素进行in-place的遍历。
Flatbuffer使用严格的字节对齐和字节顺序（通常是小端）以保证可以跨平台使用。

另外，像table这样的对象，Flatbuffer提供了向前/向后的兼容性，和通用的可选属性，以支持多变的数据格式。

#### Tables

Tables是FlatBuffer的基石，因为数据格式的变化对于很多应用来说，是非常正常的事。

通常情况下，一般的序列化框架都是在parsing的过程中，透明的处理数据格式的变化的。但是FlatBuffer没有parsing的过程。

Tables使用vtable来对数据进行非直接的读取。每一个table都有一个vtable（可以在同类型的tables中进行共享，类似C++类的虚表），vtable中包含字段的信息。同时，vtable也许也指明哪一些字段在当前的数据中是不存在的，这些字段会返回一个默认值。

Tables只需要很少的空间（因为vtables占用空间很少，并且是共享的），尽管在访问数据时有一些开销，但是提供了极大的可伸缩性，Tables甚至比等价的结构占用内存更小，因为当字段等于默认值时，我们没有必要为其分配空间。

FlatBuffers额外提供了“裸”结构，这些字段不能向前/向后兼容，但是这样可以减少它们的内存占用。这种字段对于不经常变化的元素非常有用，比如坐标对和RGBA颜色信息。

#### Schema

Schema减少了一些通用性（在没有schema的情况下，你不能读取其中的数据），但是它也有很多优点：

* 大部分数据格式信息可以被生成为代码，减少在buffer中存储数据格式的时间/空间开销。
* 强类型的数据定义意味着更少的运行时错误检查和处理。
* Schema使得在读取buffer前不进行解析。

FlatBuffer的schema格式和他大哥ProtoBuf类似，并且通常情况下可以被C风格的编程语言所读取。当然，我们也对其proto格式进行了优化。

* 弃用手动为字段添加ID。这样一来，对于数据格式的变动，一来会出现手动找寻一个空位(slot)的情况；二是会出现对于弃用字段，由于向前/向后兼容的原因不敢真正的删除，如果你幻想可以复用字段，你就给自己挖了一个更大的坑。
* tables和structs是不同的。tables的字段是可选的，而structs的字段是必须的。
* 原生的vector支持，取代``repeated``关键字。这样无需遍历就可以知道vector的长度。这样可以让数据的表示更加紧凑。
* 原生的union类型支持。避免使用一系列的optional字段而造成的冗长的手动检查。
* 允许为标量设初值，无需处理可选字段。
* Parser可以统一的处理schema和JSON表示的数据定义。

## Benchmark

<table class="table-bordered table-hover">
<tbody>
<tr>
<th></th><th>FlatBuffers (binary) </th><th>Protocol Buffers LITE </th><th>Rapid JSON </th><th>FlatBuffers (JSON) </th><th>pugixml  </th></tr>
<tr>
<td>Decode + Traverse + Dealloc (1 million times, seconds) </td><td>0.08 </td><td>302 </td><td>583 </td><td>105 </td><td>196 </td></tr>
<tr>
<td>Decode / Traverse / Dealloc (breakdown) </td><td>0 / 0.08 / 0 </td><td>220 / 0.15 / 81 </td><td>294 / 0.9 / 287 </td><td>70 / 0.08 / 35 </td><td>41 / 3.9 / 150 </td></tr>
<tr>
<td>Encode (1 million times, seconds) </td><td>3.2 </td><td>185 </td><td>650 </td><td>169 </td><td>273 </td></tr>
<tr>
<td>Wire format size (normal / zlib, bytes) </td><td>344 / 220 </td><td>228 / 174 </td><td>1475 / 322 </td><td>1029 / 298 </td><td>1137 / 341 </td></tr>
<tr>
<td>Memory needed to store decoded wire (bytes / blocks) </td><td>0 / 0 </td><td>760 / 20 </td><td>65689 / 4 </td><td>328 / 1 </td><td>34194 / 3 </td></tr>
<tr>
<td>Transient memory allocated during decode (KB) </td><td>0 </td><td>1 </td><td>131 </td><td>4 </td><td>34 </td></tr>
<tr>
<td>Generated source code size (KB) </td><td>4 </td><td>61 </td><td>0 </td><td>4 </td><td>0 </td></tr>
<tr>
<td>Field access in handwritten traversal code </td><td>typed accessors </td><td>typed accessors </td><td>manual error checking </td><td>typed accessors </td><td>manual error checking </td></tr>
<tr>
<td>Library source code (KB) </td><td>15 </td><td>some subset of 3800 </td><td>87 </td><td>43 </td><td>327 </td></tr>
</tbody>
</table>
