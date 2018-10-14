Date: 2014-02-04 00:10
Title: GeoHash算法
Tags: GeoHash, POI, 压缩, 索引
Slug: geo-hash-algorithm

## GeoHash

> Geohash is a latitude/longitude geocode system invented by Gustavo Niemeyer when writing the web service at geohash.org, and put into the public domain. It is a hierarchical spatial data structure which subdivides space into buckets of grid shape.

简单说，GeoHash是一个将经纬度信息编码成一个string的算法。从而便于储存、查找。

## GeoHash算法的步骤

GeoHash对经度纬度分别编码，原理是迭代做二分，进而逼近真实值。

我们以纬度举例。

由于地球纬度区间是[-90,90]，所以取区间中点``pivot``。如果某地点P的纬度大于``pivot``的值，则编码的第1位为``1``，反之为``0``。

然后缩小范围，迭代N次。得到最后的结果。

经度的范围是[-180, 180]。我们重复上面的过程，也可以得到经度编码。

最后我们把经度和纬度的编码进行交错组合，偶数位放经度，奇数位放纬度。得到最后的GeoHash编码。

例如，经纬度``(57.64911,10.40744)``可以使用base32编码为 ``u4pruydqqvj``。

## GeoHash算法的用途

由于GeoHash使用经纬度交错编码，所以我们使用某一个<b>前辍</b>，就可以划定一个经纬度范围。


![GeoHash-grid][1]

如果我们对GeoHash编码这一列进行索引加速，则可以在较快的时间内查找到某一个范围内的所有grid，进而获得POI等信息。

## GeoHash的压缩思想

GeoHash的交错编码为区间查找提供了遍历。而对经纬度的逼近编码则提供了非常好的压缩特性。

易得，一个点位于``pivot``的左右/上下的机率是相同的。所以编码的每一位的信息量都是``-logPr[s]``=>``1bit``，达到了数据压缩的下限。

又由于二分逼近的良好性能，使得压缩/解压缩的速度可以达到极限。

不过在实际应用中，POI不可能完全平均分布，所以GeoHash的压缩只是一种接近最优解的方案。但是由于二分逼近法带来的可索引性，GeoHash绝对可以称的上是一个精妙完美的设计了。

## 应用 - 拉取目标周围的POI

我们在一些LBS应用中，经常需要拉取某一点周围的POI。

假设我们将POI存储为一个``pvlist``映射。并且获得了某点的GeoHash值。那么我们怎么取得周围的POI呢？

理想状态下，“附近的POI”都是在一个以某点为圆心的圆进行查找。但是由于GeoHash划分的范围是一个矩形，所以我们使用一个``3×3``的大矩形来替代圆形范围。

其中``3×3``矩形中最中间的矩形是我们确定的那个点。

然后，我们根据给出的半径``r``确定GeoHash的精确度。使得我们的``3×3``大矩形可以包含理想的圆形范围。

于是下一步的目标就是找到某点GeoHash的**8个**临近的GeoHash。

由上文我们可以得出，GeoHash的经纬度是分别编码的。以一个``4×4``的地图为例。

这是在纬度上的划分。

![纬度][6]

可以看出，连续的``GeoHash Grid``的纬度编码也是连续的。

经度同理。

所以我们只需要``decode``我们的GeoHash编码，将``longitude``和``latitude``编码分别进行``-1/+1``的操作就可以获得**附近的POI**的GeoHash码/前辍了。

## 总结
GeoHash的三个特性，<b>可索引</b>，<b>压缩</b>，<b>便于存储</b>。

还有，好久不写文了。

## 参考资料

* [HBase in Action][2], Chpt. 8
* [深入搜索引擎][3], Chpt. 2
* [GeoHash - Wikipedia][4]
* [GeoHash核心原理解析][5]
* [python-geohash][7]

[1]: http://wizmann-tk-pic.u.qiniudn.com/blog-geohash-grid.jpg
[2]: http://book.douban.com/subject/11554138/
[3]: http://book.douban.com/subject/3729518/
[4]: http://en.wikipedia.org/wiki/Geohash
[5]: http://www.cnblogs.com/LBSer/p/3310455.html
[6]: http://wizmann-tk-pic.u.qiniudn.com/blog-geohash-latitude-grid.png
[7]: https://code.google.com/p/python-geohash/
