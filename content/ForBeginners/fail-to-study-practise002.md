Date: 2019-10-06 00:00:00
Title: 不好好学习，只能。。。 [Practise002]
Tags: 题解, 水题
Slug: fail-to-study-practise002

## 题目列表

* CodeForces 334A - Candy Bags
* CodeForces 59A - Word
* CodeForces 295A - Greg and Array
* CodeForces 478C - Table Decorations
* CodeForces 369C - Valera and Elections
* CodeForces 372B - Counting Rectangles is Fun
* CodeForces 463C - Gargari and Bishops
* CodeForces 546D - Soldier and Number Game

VJudge比赛：https://vjudge.net/contest/331975

平均难度：Codeforces Div2 中档题

## 背景（瞎说两句）

最近在找题训练，发现了A2OJ的一个CF Ladder。

本着不为难自己的原则，选了一个和自己水平比较相配的[版本][1]。等把这里面的题做完了，可能会试试更难的吧。

训练目标：

1. 用比赛状态专心做题
2. 尽量1A

## CodeForces 334A - Candy Bags

给你一堆数`[1,2,3...n^2]`，问怎么把这些数平均分给n个人，使得这n个人拿到的数字之和相等。n一定是偶数。

我们可以先将`[1...n]`分配给1...n个人，然后再把`[n + 1 ... 2 * n]`分配给n...1。这样一来n个人拿到的数之和就是相等的。

继续用这种方法把剩下的数都分配完即可。

结果：[1A][2]

## CodeForces 59A - Word

水题。把字符串根据大写占多数或小写占多数，转成全大写或者全小写。如果相等转小写。

结果：[1A][3]

## CodeForces 295A - Greg and Array

给你一个数组`A[n]`。有n个操作`f(l, r, d)`，意为在数组`A[l...r]`都加上d。

然后再执行m次操作`g(x, y)`。意为将编号x...y的操作执行一次。

问在m次操作之后的数组的值是多少。

解法是两次前辍和，没有难度。

结果：[1A][4]

## CodeForces 478C - Table Decorations

给你r,g,b个红、绿、蓝色气球。每装饰一个桌子一定要使用两种及以上颜色的气球。问最多能装饰多少张桌子。

假设r > g > b。

首先先考虑某一种颜色特别多的情况，即`r >= 2 * (g + b)`。易得，此时最多只能有`g + b`张桌子被装饰。

然后，我的想法是，如果r,g,b三种气球个数相等，那么必然要使用<r,g,b>三种不同的颜色来进行装饰。所以我们设使用三种不同颜色的桌子共有x桌，其它的桌子使用两种颜色。列方程`r - x >= 2 * (g - x + b - x)`可求得x，再用x求最后的结果。

其实我的代码没考虑那么多，用了暴力对拍没问题就交了。。。

网上也有题解是暴力找规律的。除了第一种情况之外，答案为(r + b + g) / 3。

结果：[1A][5]

## CodeForces 369C - Valera and Elections

给一棵以1...n为节点的树，以1为根。树上有一些边是坏掉的。选择节点k，就可以修复1到k的路径上的所有边。

求最小的节点集，使得所有的坏边全部被修复。

一道简单的DFS。如果一个节点下面没有坏边的话，我们就选择这个节点进入节点集。处理好一些特殊情况即可。

结果：[3A][6]

WA点：

1. 如果没有坏边，那么只需输出0即可
2. Python的DFS有递归层数限制，还有栈大小限制，需要开栈外挂。详见代码。

## CodeForces 372B - Counting Rectangles is Fun

DP + 计数。应该是一个挺经典的模型。

详见[这篇文章][9]。

结果：[并没有做出来][10]

## CodeForces 463C - Gargari and Bishops

一个国际象棋棋盘上，“象（bishop）”可以向对角线（左上右下，右上左下）方向行走。

给定一个棋盘，棋盘格子各有一个权值，象可以获得其所在两条对角线上的格子的权值和。

问，棋盘上有两个象，这两个象的可达格子不能重复，问这两个象能获得的最大权值和是多少。

首先，由于奇偶性不同，我们可以构造两个不同的象的集合。然后再两两配对，找到最大权值和的位置。

结果：[3A][7]

WA点：

1. 没有处理最大权值和为0的情况
2. 没有使用Pypy，超时了。

## CodeForces 546D - Soldier and Number Game

求a!/b!有多少个质因子。

用筛法做简单计数即可。

结果：[2A][8]

WA点：

1. cin/cout超时。不要使用std::endl。优化方法见代码。

[1]: https://a2oj.com/ladder?ID=16&My=true
[2]: https://github.com/Wizmann/ACM-ICPC/blob/master/Codeforces/Codeforces%20Round%20%23194%20(Div.%202)/334A.py
[3]: https://github.com/Wizmann/ACM-ICPC/blob/master/Codeforces/Codeforces%20Beta%20Round%20%2355%20(Div.%202)/59A.py
[4]: https://github.com/Wizmann/ACM-ICPC/blob/master/Codeforces/Codeforces%20Round%20%23179%20(Div.%201)/295A.cc
[5]: https://github.com/Wizmann/ACM-ICPC/blob/master/Codeforces/Codeforces%20Round%20%23273%20(Div.%202)/478C.py
[6]: https://github.com/Wizmann/ACM-ICPC/blob/master/Codeforces/Codeforces%20Round%20%23216%20(Div.%202)/369C.py
[7]: https://github.com/Wizmann/ACM-ICPC/blob/master/Codeforces/Codeforces%20Round%20%23264%20(Div.%202)/463C.py
[8]: https://github.com/Wizmann/ACM-ICPC/blob/master/Codeforces/Codeforces%20Round%20%23304%20(Div.%202)/546D.cc
[9]: https://blog.csdn.net/u013912596/article/details/38796089
[10]: https://github.com/Wizmann/ACM-ICPC/blob/master/Codeforces/Codeforces%20Round%20%23219%20(Div.%201)/372B.cc
