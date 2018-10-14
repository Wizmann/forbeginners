Date: 2014-07-20 00:18
Title: CPU cache引发的性能血案
Tags: cpu, cache, profile, valgrind, cachegrind
Slug: cpu-cache-miss

在__[为什么转置一个512x512的矩阵，会比513x513的矩阵慢很多？][1]__一文中，作者引用了一个矩阵转置的例子，来讲解由于CPU cache的失效而带来的性能损失。

上面的文章对问题的解释与讨论都非常的透彻。我的这篇文章只是对上面文章的一篇读后感和实验报告。就酱。

## CPU cache 之 组相联

![组相联](http://wizmann-tk-pic.u.qiniudn.com/blog-cpu-cache-2-way-set-assosiate.jpg)

组相联的实现和原理不必再赘述了。我想讨论的是，如何在编程中优化CPU的cache性能。

## 查看CPU信息

我的系统是Ubuntu 12.04，CPU是i5-3230M。（屌丝机 :D)

```
wizmann@Wichmann:~$ ls /sys/devices/system/cpu/cpu0/cache/index0/
coherency_line_size  physical_line_partition  size
level                shared_cpu_list          type
number_of_sets       shared_cpu_map           ways_of_associativity
```

使用cat命令查看文件内容，可以获得CPU L1 cache的一些信息。

<table class="table table-striped-white table-bordered">
<thead>
<tr>
 <th>Key</th>
 <th>Value</th>
</tr>
</thead>
<tbody><tr>
 <td>level</td>
 <td>1</td>
</tr>
<tr>
 <td>size</td>
 <td>32K</td>
</tr>
<tr>
 <td>ways_of_associativity</td>
 <td>8</td>
</tr>
<tr>
 <td>type</td>
 <td>Data</td>
</tr>
<tr>
 <td>number_of_sets</td>
 <td>64</td>
</tr>
</tbody></table>

以上可知，CPU L1 cache有64组，每组有8个cache line。是**8位组相联**的Cache类型。

## 分析缓存失效率

对于以上问题，我们可以手工计算，也可以使用程序模拟Cache的失效率。

同时，Valgrind为我们提供了cachegrind工具来分析cache的失效。

```
wizmann@Wichmann:/tmp$ valgrind --tool=cachegrind --D1=32768,2,16 ./test
==14282== Cachegrind, a cache and branch-prediction profiler
==14282== Copyright (C) 2002-2011, and GNU GPL'd, by Nicholas Nethercote et al.
==14282== Using Valgrind-3.7.0 and LibVEX; rerun with -h for copyright info
==14282== Command: ./test
==14282== 
--14282-- warning: L3 cache found, using its data for the LL simulation.
Average for a matrix of 257: 1875==14282== 
==14282== I   refs:      18,708,198
==14282== I1  misses:         1,404
==14282== LLi misses:         1,355
==14282== I1  miss rate:       0.00%
==14282== LLi miss rate:       0.00%
==14282== 
==14282== D   refs:       8,936,548  (4,543,346 rd   + 4,393,202 wr)
==14282== D1  misses:     1,107,687  (1,086,263 rd   +    21,424 wr)
==14282== LLd misses:        10,502  (    5,179 rd   +     5,323 wr)
==14282== D1  miss rate:       12.3% (     23.9%     +       0.4%  )
==14282== LLd miss rate:        0.1% (      0.1%     +       0.1%  )
==14282== 
==14282== LL refs:        1,109,091  (1,087,667 rd   +    21,424 wr)
==14282== LL misses:         11,857  (    6,534 rd   +     5,323 wr)
==14282== LL miss rate:         0.0% (      0.0%     +       0.1%  )

```

其中I1代表指令1级缓存，D1代表数据1级缓存，而LL代表二级或三级缓存。

上面的输出也许过于复杂，我们在下面列表分析。

### 测试环境

只讨论L1的情况，L1大小32768 Bytes，2路组相联，每个cache line有16 Bytes。

valgrind测试命令为：

```
wizmann@Wichmann:/tmp$ valgrind --tool=cachegrind --D1=32768,2,16 ./test
```

### 测试程序

```cpp
#define SAMPLES 64
#define MATSIZE 256

#include <time.h>
#include <iostream>
int mat[MATSIZE][MATSIZE];

void transpose()
{
   for ( int i = 0 ; i < MATSIZE ; i++ )
   for ( int j = 0 ; j < i ; j++ )
   {
       int aux = mat[i][j];
       mat[i][j] = mat[j][i];
       mat[j][i] = aux;
   }
}

int main()
{
   //initialize matrix
   for ( int i = 0 ; i < MATSIZE ; i++ )
   for ( int j = 0 ; j < MATSIZE ; j++ )
       mat[i][j] = i+j;

   int t = clock();
   for ( int i = 0 ; i < SAMPLES ; i++ )
       transpose();
   int elapsed = clock() - t;

   std::cout << "Average for a matrix of " << MATSIZE << ": " << elapsed / SAMPLES;
   return 0;
}
```

### 测试结果

<table class="table table-striped-white table-bordered">
<thead>
<tr>
 <th>-</th>
 <th>MATSIZE = 256</th>
 <th>MATSIZE = 256 + 1</th>
</tr>
</thead>
<tbody><tr>
 <td>运行时间 (g++ O2) 1024次</td>
 <td>78ms</td>
 <td>39ms</td>
</tr>
<tr>
 <td>D1 Miss</td>
 <td>2,621,967</td>
 <td>1,107,687</td>
</tr>
<tr>
 <td>D1 Miss Rate</td>
 <td>29.5%</td>
 <td>12.3%</td>
</tr>
</tbody></table>


由此可见，Cache的Miss Rate基本决定了程序的运行速度，运行时间比例和D1 MISS RATE的比例基本一致。

* 注：本机环境与cachegrind参数是不一致的，在本机上由于cache较大，且采用8位组相联，所以D1 cache miss较少，差异主要体现在LLd Miss Rate上。

## 实际意义

如果程序对一段内存进行顺序读取的时候，以上的缓存失效问题有可能会显现出来。但是缓存失效只是程序性能问题的一个可能的原因，应该在对程序进行profile之后再做结论。

## 其它profile工具

我的提问：__[有没有什么方法可以对CPU cache失效进行计数？][2]__中，各位答主还提供了以下几种工具：

* perf (linux)
* [Tiptop][3]
* qemu
* visual studio的cpu counter
* intel performance counter monitor
* vtunes

profile的方法很多，选一个易用性与正确性达到平衡就可以。反正我是哪个也不会\_(:з」∠)_

## 参考链接

* [cache映射功能、命中率计算][4]
* [使用valgrind检查cache命中率，提高程序性能][5]
* [Cachegrind: a cache and branch-prediction profiler][6] （官方文档）
* [使用 Cachegrind 简要概述缓存使用][7]
* [Cachegrind: a cache-miss profiler][8]
* [Perf -- Linux下的系统性能调优工具，第 1 部分][9]
* [7个示例科普CPU Cache（扩展阅读）][10]

[1]: http://evol128.is-programmer.com/posts/35453.html
[2]: http://www.zhihu.com/question/24540567/noti-answers?group_id=564624072
[3]: http://tiptop.gforge.inria.fr/
[4]: http://yoursunny.com/study/EI209/?topic=cache
[5]: http://blog.focus-linux.net/?p=391
[6]: http://valgrind.org/docs/manual/cg-manual.html
[7]: https://access.redhat.com/documentation/zh-CN/Red_Hat_Enterprise_Linux/6/html/Performance_Tuning_Guide/ch05s03s02.html
[8]: http://wwwcdf.pd.infn.it/valgrind/cg_main.html
[9]: http://www.ibm.com/developerworks/cn/linux/l-cn-perf
[10]: http://coolshell.cn/articles/10249.html
