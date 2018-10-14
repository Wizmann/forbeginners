Date: 2014-11-17 00:25:42 
Title: 类型-长度-值（TLV）协议
Tags: TLV, protocol, network, protobuf, flatbuffer
Slug: tlv-protocol

在数据通信协议中，可选的信息或字段通常使用type-length-value（a.k.a TLV）元素来进行编码。

* Type - 类型

用来标示字段类型的值，通常是一个二进制值或简单的字母

* Length - 长度

字段长度，单位通常为Byte

* Value - 值

一个变长的比特数组用来存储这个字段的值

## 优势

* TLV序列方便遍历查找
* 新的字段可以无痛的加入现有的协议中。解析的时候，对于未知的字段，可以轻松的跳过。这点与XML类似
* TLV元素的顺序可以是随意的
* TLV元素通常使用二进制存储，可以使解析速度加快并且使数据更小
* TLV可以与XML数据相互转换，易于人类阅读

## 例子

在这里，我们以protobuf的可选和变长字段为例。

### field_number ++ wire_type

每一个protobuf的字段在传输时，都会加上``field_number``和``wire_type``这两个值，这两个值组成这个字段的key。

```
key = (field_number << 3) | wire_type
```

``field_number``标明了字段的编号，方便协议向前向后的兼容。而``wire_type``标明字段的类型，方便解析程序使用相应的方法来进行反序列化。

### Varint 变长整型

对于一个变长整型字段，protobuf中使用Type(0)来标示，而长度并没有显式的标出。

Varint的值使用如下编码方法：

* Varint使用分段存储方法，每个Byte为一段
* Varint每段的第一个字节是标示位，如果这一位是1，则下一个Byte也是这个数的一部分，如果这一位是0，则在这个Byte是这个Varint的最后一个Byte

### String 变长字符串

字符串被标示为Type(2)，长度使用Varint类型显式标出。

一个string在protobuf中被编码为：

```
encoded_string = key ++ length ++ string
```

## 其它方法

TLV同样也可以表示tag-length value，例如HTTP、FTP、POP3等协议都是使用这种基于可读文本的"Field: Value"协议。这样设计的原因大概是由于在“上古时代”，互联网速度远小于CPU处理的速率（现在更应该是**远远小于**，CPU已经爆了IO一条街了），设计一些更可读的协议对人类来说确实比较方便。

而TCP/IP核心协议都使用的定长不可变的协议，这样可以使编码、解析速率达到最快。

对于XML和json这种奇行种，我们就不说了吧 :)

## 参考链接

* [Type-length-value][1]
* [Google Protocol Buffers 编码(Encoding)][2]
* [破解节操的下限][3]

[1]: http://en.wikipedia.org/wiki/Type-length-value
[2]: http://www.cnblogs.com/shitouer/archive/2013/04/12/google-protocol-buffers-encoding.html
[3]: http://wizmann.tk/moujiecao.html
