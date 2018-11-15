Date: 2014-07-19 11:00:38 
Title: 玩玩算法题1：Sherlock and Queries
Tags: algorithm, interview
Slug: interview-problem-1-sherlock-and-queries

## 题目大意

给你三个数组:A[N], B[M], C[M]。让你按如下pseudo-code给出的规则计算，求出最终A[N]每一项的值。

```
for i = 1 to M do
    for j = 1 to N do
        if j % B[i] == 0 then
            A[j] = A[j] * C[i]
        endif
    end do
end do
```

## 数据范围

1≤ N,M ≤ 10^5 

1 ≤ B[i] ≤ N 

1 ≤ A[i],C[i] ≤10^5

## Brute-Force解法

暴力解法就是题目中给出的范例，时间复杂度为O(M * N)。那么有没有更优化的解法。

## 筛法

从``j % B[i] == 0``这个关系我们可以很容易的联想到[筛法][1]，我们不必要从1到N每次去尝试是否可以被B[i]整除，而是直接在数组A的第``B[i], B[i] * 2 ... B[i] * k``项上直接乘上C[i]。

此时，我们的时间复杂度为O(k)，k = sum(N / B[i])

如果数组B中的值两两不等。那么k的最大值就是调和级数``N + N / 2 + N / 3 + ... + N / N``，其值约为``N * lnN``。

但是如果数组B中的值有大量相等，并且值非常小（如1或2等），那么此时的时间复杂度仍然会退化到O(N * M)。

## 让我们再优化一小下

在上文我们分析到，如果数组B中的值有大量相等时，程序的时间复杂度会严重退化。那么我们的优化方法是什么呢？

从上面的pseudo-code我们可以看出，如果B[i] == B[i']，那么它们会对A的同一项进行操作，于是我们就把有着相同值的B[i]合并在一起，而操作数C[i]累乘。此时，我们的时间复杂度就会接近于最优值O(N * lnN)。

## Show me the code

```cpp
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <algorithm>

using namespace std;

#define print(x) cout << x << endl
#define input(x) cin >> x

typedef long long llint;

const int SIZE = 100010;
const int MOD = 1000000007;

struct node {
    int vb, vc;

    friend bool operator < (const node& a, const node& b) {
        return a.vb < b.vb;
    }
};

node nodes[SIZE];

int A[SIZE];


int n, m;

void solve()
{
    llint g = 1;
    int pre = -1;
    for (int i = 1; i <= m + 1; i++) {
        if (nodes[i].vb == pre) {
            g *= nodes[i].vc;
            g %= MOD;
        }
        if (nodes[i].vb != pre || i == m + 1) {
            int b = pre;
            for (int j = 1; b * j <= n && b != -1; j++) {
                int pa = b * j;
                A[pa] = llint(A[pa]) * g % MOD;
            }
            g = nodes[i].vc;
            pre = nodes[i].vb;
        }
    }
}


int main() 
{
    input(n >> m);
    for (int i = 1; i <= n; i++) {
        scanf("%d", &A[i]);
    }
    for (int i = 1; i <= m; i++) {
        scanf("%d", &(nodes[i].vb));
    }
    for (int i = 1; i <= m; i++) {
        scanf("%d", &(nodes[i].vc));
    }
    sort(nodes + 1, nodes + m + 1);
    solve();
    for (int i = 1; i <= n; i++) {
        printf("%d ", A[i] % MOD);
    }
    puts("");
    return 0;
}
```

## 关键点

* 是否了解筛法，并且可以从题目的提示中联想到筛法
* 是否了解调和级数估计时间复杂度的方法
* 是否了解算法的best-case和worst-case
* 是否可以了解算法的瓶颈，并优化自己的算法

## 算法分析用到的一些近似公式

![cheetsheet][2]

* 本图来自《算法 第四版》

## 原题链接

[戳我么么哒][3]


  [1]: https://zh.wikipedia.org/zh-cn/%E5%9F%83%E6%8B%89%E6%89%98%E6%96%AF%E7%89%B9%E5%B0%BC%E7%AD%9B%E6%B3%95
  [2]: https://github.com/Wizmann/assets/raw/master/wizmann-tk-pic/book-algorithm-approximate-functions.png
  [3]: https://www.hackerrank.com/challenges/sherlock-and-queries
