Date: 2013-12-28 14:42
Title: How to "Rotate Image"?
Tags: Leetcode, algorithm, 思维
Slug: how-to-rotate-image-leetcode

## 啥？
原题[戳我][1]

> Rotate Image

> You are given an n x n 2D matrix representing an image.

> Rotate the image by 90 degrees (clockwise).

>Follow up:

>Could you do this in-place?

示意图如下：

![rotate-image][2]

当然，矩阵中的数字**不一定**是规律的。

## 为什么要提出这个问题

自觉是一个**不聪明**的人（双低。。。<(=＠_＠;=)?>）。

别人一下子就想明白的事，在我这里要计算好几个来回。

所以努力想找到一个思维方法去弥补这个不足。

就以这题为例，如何使用简单、直接的方法，迅速正确的找出变化的映射规律。

## 初步思路

由于不可以使用**额外的空间**。所以必须找到一个坐标映射``f(x, y) => (next_x, next_y)``。

这样，我们就可以通过循环来``swap``矩阵中的元素。

## 遇到问题

如何确定映射``f(x, y)``？

由于我的思维不能支持我在头脑中形成正确的公式。

于是我想到，因为我们要求的变换是在二维矩阵中的简单移位。所以我们可以做出如下一个方程。

``f(x, y) = (ax + by + c, dx + ey + f)``

然后找出特殊点，代入方程中，求出``a``到``f``各自代表的值。

于是求出映射``f(x, y) => (y, n - x)``。

即可以分解为：``reverse_X(Matrix.T)``

## 思考方式

以上的方法是我失败了N次之后才想到的。（弱。。。）

于是我又有了进一步的思考。

这样的思考方式是不是最佳的。如果大家遇到这样的问题，会用什么巧妙的方法去思考，去优雅的解决问题。

不过要记得我们的条件

* 矩阵顺时针旋转90度
* in-place变换，不得使用额外的空间

欢迎大家提出自己的看法。代码请贴到[gist][3]或[hpaste][4]等网站上，不要把代码直接写到评论中，我会及时update本文，展示大家的想法。

[1]: http://oj.leetcode.com/problems/rotate-image/
[2]: https://github.com/Wizmann/assets/raw/master/wizmann-tk-pic/blog-rotate-image-leetcode.png
[3]: https://gist.github.com/
[4]: http://lpaste.net/

