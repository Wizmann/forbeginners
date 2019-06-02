Date: 2019-06-02 17:24
Title: [kuangbin带你飞]专题二十一 概率&期望【上】
Tags: 题解, 概率, 期望
Slug: kuangbin-21-probability-and-expectation-1

## A - LightOJ 1027 [A Dangerous Maze]

### Description

题目：[A Dangerous Maze][1]

现在你身处一个迷宫，你的面前有n个门`d[0...n]`，你会等概率的随机打开一个门`i`。

如果`d[i] > 0`，你会花`d[i]`时间走出迷宫。如果`d[i] < 0`，你会花`abs(d[i])`的时间回到原处。

问你走出迷宫的数学期望是多少？

### Solution

设最终走出迷宫的数学期望为`E`。

正数门的个数为`N0`，选中标号为正数的门的概率为`P0`，正数门的标号之和为`Sum0`，平均值为`Ave0`。

与此对应的负数门的个数为`N0`，选中概率`P1`，标号之和`Sum1`，平均值`Ave1`。

我们可以列出等式：

```math
 E = P_{0} Ave_{0} + P_{1} (Ave_{1} + E)
```

* 如果我们选中了正数门，那么会消耗`Ave0`的时间，并且走出迷宫。
* 如果我们选中的负数门，那么会消耗`Ave1`的时间，回到原地，需要期望为`E`时间才能走出迷宫。

接下来我们进行等式的进行一步推导，得到：

```math
E = \frac{Sum_{0} + Sum_{1}}{N_{0}}
```

最后使用分数化简就可以得到最终答案。

代码： [LightOJ/1027.cc][2]

## B - LightOJ 1030 [Discovering Gold]

### Description

题目：[Discovering Gold][3]

给定一个长为N的数组，每个格子里面都有一定数量的金子。

现在你从位置1开始，每轮投骰子向前随机走1~6步，直到走到N点为止。如果你的随机数让你走出了数组，则你需要重新扔骰子。你可以获得每轮起始点和终点的金子。

问你获得金子数量的期望。

### Solution

本题可以用DP来做，但是一定注意DP的顺序。由于到达数组每一个点的概率不同，所以我们不能由`dp[i - k]`等概率的推出`dp[i]`。我们选择从`dp[i + k]`推出`dp[i]`。

设`dp[i]`为从点i到点n所需要步数的期望。`P`代表从`i`到`i+k`的概率。

```math
dp[i] = \sum{dp[i + k] * P}
```

代码：[LightOJ/1030.cc][4]

## C - LightOJ 1038 Race to 1 Again

题目：[Race to 1 Again][5]

### Description

给一个数N，每一步都可以将N整除，直到除到1为止。

问步数的期望。

### Solution

非常简单的DP，由于数据规模不大，可以直接在DFS的过程中求约数。

`P`代表数字`i`约数个数的倒数。


```math
dp[i] = \sum{dp[i / k] * P} \quad \mid \quad  i \bmod k == 0
```

代码：[LightOJ/1038.cc][6]

## D - LightOJ 1079 Just another Robbery 

题目：[Just another Robbery][7]

### Description

劫匪想打劫银行，但是希望被抓的概率不大于p。

有n个银行，给定打劫银行`i`的收益`m[i]`和被抓的概率`q[i]`。

问最多能打劫几个银行，使得收益最大。

### Solution

由于银行的个数`n`和抢银行的收益`m[i]`的乘积最大才10000。所以可以用`dp[k]`表示抢银行的总收益为`k`时被抓的概率。

```math
dp[k + m_{i}] = \min(dp[k + m_{i}], 1 - (1 - dp[k])(1 - q_{i}))
```

代码：[LightOJ/1079.cc][8]

## E - LightOJ 1104 Birthday Paradox

题目：[Birthday Paradox][9]

### Description

给定一年有n天，求最小的m，使m个人当中有两个人的生日相同的概率超过0.5。

### Solution

生日悖论问题。

```math

P = 1 \times \frac{n - 1}{n} \times \frac{n - 2}{n} \dotsb \frac{n - m + 1}{n}

```

因为n比较大以及数据组数比较多，所以我们可以预处理出所有的结果。

不过直接算也能过。

代码：[LightOJ/1104.cc][10]

## F- LightOJ 1151 Snakes and Ladders

题目：[Snakes and Ladders][11]

### Description

10x10的棋盘上，顺序标号1\~100。从点1开始，随机扔骰子前进1\~6步。走到点100时（包括走出点100），游戏结束。

棋盘上有梯子和蛇，踩到梯子会向前传送，踩到蛇会向后传送。

问给定棋盘，从1走到100所需要步数的期望。

### Solution

高斯消元模板题。

对于没有梯子或蛇的格子`i`，有：

```math

E_{i} = \frac{E_{i + 1} + E_{i + 2} + \dotsb + E_{i + 6}}{6} + 1 

```

对于有梯子或蛇的格子`i`，如果其终点为格子`j`，有：

```math
E_{i} = E_{j}
```

我们联立方程组，然后使用高斯消元即可求解。

代码：[LightOJ/1151.cc][12]

## G - LightOJ 1248 Dice (III) 

题目：[Dice (III)][13]

### Description

给定一个N面的骰子，问N面至少都能投出一次的数学期望。

### Solution

我们可以列出期望的方程，设我们已经投出了`i`面，还有`n - i`面没有投出，`dp[i]`代表还需要投的次数的期望。此时有：

```math

dp[i] = \frac{i}{n} \times dp[i] + \frac{n - i}{n} \times dp[i + 1] + 1

\Downarrow

dp[i] = dp[i + 1] + \frac{n}{n - i}

```

代码：[LightOJ/1248.cc][14]


[1]: https://vjudge.net/problem/LightOJ-1027
[2]: https://github.com/Wizmann/ACM-ICPC/blob/master/LightOJ/1027.cc
[3]: https://vjudge.net/problem/LightOJ-1030
[4]: https://github.com/Wizmann/ACM-ICPC/blob/master/LightOJ/1030.cc
[5]: https://vjudge.net/problem/LightOJ-1038
[6]: https://github.com/Wizmann/ACM-ICPC/blob/master/LightOJ/1038.cc
[7]: https://vjudge.net/problem/LightOJ-1079
[8]: https://github.com/Wizmann/ACM-ICPC/blob/master/LightOJ/1079.cc
[9]: https://vjudge.net/problem/LightOJ-1104
[10]: https://github.com/Wizmann/ACM-ICPC/blob/master/LightOJ/1104.cc
[11]: https://vjudge.net/problem/LightOJ-1151
[12]: https://github.com/Wizmann/ACM-ICPC/blob/master/LightOJ/1151.cc
[13]: https://vjudge.net/problem/LightOJ-1248
[14]: https://github.com/Wizmann/ACM-ICPC/blob/master/LightOJ/1248.cc
