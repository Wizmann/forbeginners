Date: 2014-08-08 01:25:54 
Title: System Design - 最热门的IP地址
Tags: interview, system-design
Slug: hottest-ip-address

## 写在前面

问题是非常流行的，也确实流行了一阵的system-design问题。在[知乎][1]上再次被人提起。然后我非常欣赏[陈硕的回答][2]。所以要写一篇文章，记下自己的感想。

## 问题

海量数据算法:如何从超过10G的记录IP地址的日志中，较快的找出登录次数最多的一个IP？

## 银弹？

面对这种system-design问题，尤其是这种，**非高并发、非实时**的问题，很多人会采用_map-reduce_ —— 解决system-design问题的银弹。

我对map-reduce的理解非常肤浅，但是可以解释一下大概的流程。

1. 将日志进行分片。把hash(ip)相同的ip地址分到同一个片中。（注：这里的hash并不是签名函数，只是一个分片标示）
2. 分片后的日志的大小会小很多，可以方便的进行排序，记数。
3. 然后再从各个片中，统计出最热门的IP地址。（或TopK的IP地址）

如果不满意我的答案的话，推荐[Mining of Massive Datasets][3]一书，其中对map-reduce算法做一番不错的介绍。

## 正确的分析姿势

### 业务实体

> 业务实体拥有四种主要的组件： 信息模型、生命周期模型、访问策略以及通知。 

换句话说，业务实体就是题目中提到的“名词”。

在本题中，业务实体有：

* IP地址（默认为ipv4）
* 最热门IP地址

### 业务应用

业务应用指的是当前场景的**特殊**应用，以及业务实体的关联关系。

在本问题中，业务应用指的是：

* 找到**最热门**的IP地址
* 大数据量，10G的日志文件 —— 不方便在内存中进行操作
（在动辙上百G的服务器面前，10G的数据量真是弱爆了^_^)

### 物理

物理指的是数据的物理模型，包括数据结构、数据库表等。

在本题中，指的是对IP地址存储和记数的数据结构。

### 让我们做一下分析

本题中，业务实体的特点是：

* IPv4可以由一个uint32_t来表示
* ip地址是稀疏的
    * 大部分ip地址的访问次数非常少（长尾）
    * 很多ip地址是保留地址，所以不可能出现在日志中

业务应用的特点是：

* “最热门”表示要求得精确解，而不是满意解
* 内存限制

应用的物理结构的特点是： 支持存储与记数

## 无代码无真相

```cpp
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <vector>

static_assert(sizeof(void*) == 8, "64-bit only.");

std::vector<uint8_t> counts_;
struct IPcount
{
  uint32_t ip;
  uint32_t count;
  bool operator<(IPcount rhs) const
  { return ip < rhs.ip; }
};
std::vector<IPcount> overflows_;

IPcount top;

void addOverflow(uint32_t ip)
{
  IPcount newItem = { ip, 256 };
  auto it = std::lower_bound(overflows_.begin(), overflows_.end(), newItem);
  if (it != overflows_.end() && it->ip == ip)
  {
    it->count++;
    assert(it->count != 0 && "you need larger count variable");
    newItem.count = it->count;
  }
  else
  {
    overflows_.insert(it, newItem);
  }
  if (newItem.count > top.count)
    top = newItem;
}

void add(uint32_t ip)
{
  if (counts_[ip] == 255)
  {
    addOverflow(ip);
  }
  else
  {
    counts_[ip]++;
    if (counts_[ip] > top.count)
    {
      top.ip = ip;
      top.count = counts_[ip];
    }
  }
}

uint32_t getMostFrequenntIP()
{
  return top.ip;
}

int main()
{
  assert(counts_.max_size() > 0xFFFFFFFFUL);
  counts_.resize(1L << 32);
  printf("%zd\n", counts_.size());

  add(0x1);
  add(0x2);
  add(0x2);
  for (size_t i = 0; i < (1L << 32)-1; ++i)
    add(0x3);
  printf("%08x %u\n", top.ip, top.count);
}
```

### 从代码说开来

这段代码不算最漂亮，有几个小槽点，但也算是非常优雅的。

从思路上说，这段代码注意到了我们刚才分析到的，这个问题的业务特点。

1. ipv4地址可以存在uint32_t中，无需存储字符串
2. ip地址是稀疏的，所以使用一层uint_8进行哈希记数，对于少数的热门ip再进行uint32_t计数
（同时考虑了ip地址的稀疏性以及内存的限制，并且对内存的优雅使用，可以提高缓存的命中率，提高效率）
3. 使用精确计数，获得正确解

### 代码留给我们的思考题

> 练习：找出 worse case，让运行时间长达几分钟甚至十几分钟，然后提出并实施改进措施

由于我们拿不出real world中的data，所以很多分析都是纸上谈兵，不过一切的实践也都是从纸上谈兵开始。

* 题目中的``std::vector<IPcount> overflows_;``使用``unordered_map``更好，减少查找的时间（O(logN) => O(1)），并且减少插入的时间（O(N) => O(1)）
* ``std::vector<uint8_t> counts_;``可以在适当的情况调整为``uint16_t``，可以减少哈希节点生成对于内存的频繁申请。

## 后记

题目中的分析有很多是“执果索因”的成果，毕竟反推比正推要更容易一点。

想要从反推提升为正推，真的需要良好的发散思维以及敏锐的洞察力。因为面试时，没人会把题目帮你写在纸上。

话说，我才知道ipv6是128位的。那么当题目中的ip地址为ipv6时，又会有什么好方法呢？

## 参考链接

* [介绍：业务实体和业务实体定义语言][4]

[1]: http://www.zhihu.com/question/19805967
[2]: http://zhi.hu/3gJb
[3]: http://book.douban.com/subject/19934150/
[4]: http://www.infoq.com/cn/news/2010/05/BEDL


