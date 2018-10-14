Date: 2014-09-17 00:46:16 
Title: 最小表示法及其证明
Tags: string, 字符串, 最小表示法, algorithm
Slug: minimal-round-string


## 问题

> 对于一个字符串S，求S的循环的同构字符串S’中字典序最小的一个。

我们举例说明，字符串"abcd"的循环同构字符串有：``["abcd", "bcda", "cdab", "dabc"]``。

题目的目标是求这些字符串中字典序最小的那个。

## 暴力解法

暴力解法非常直观，直接枚举字符串的起点，然后找到构成最小字符串的那一个。

代码就不在这里写了。

## 最小表示法

最小表示法是解决同构字符串最小表示的巧妙算法。

其算法描述如下：

```
令i=0,j=1
如果S[i] > S[j] i=j, j=i+1
如果S[i] < S[j] j++
如果S[i] == S[j] 设指针k，分别从i和j位置向下比较，直到S[i] != S[j]
         如果S[i+k] > S[j+k] i=j,j=i+1
         否则j = j + k + 1
返回i
```

初看这个算法，一般都会一头雾水：这TMD是嘛玩意儿？

但是我们可以经过证明，来证实它的正确性。

### 最小表示法的正确性证明

首先，``S = S ++ S``

设``i < j``，且``S[i] < S[i + 1 ... j - 1]``。

并且以i为起点的字符串为``RS[i]``，以j为起点的字符串为``RS[j]``。

且``RS[i]``为``RS[0...i-1]``字典序最小的。

```
RS[i] = S[i...i+k] ++ S[i+k+1 ... i+n-1]
RS[j] = S[j...j+k] ++ S[j+k+1 ... j+n-1]
```

以上为我们的子问题。

``i = 0, j = 1``时，子问题即成立。

#### 情况0

易得。

当``S[i] < S[j]``时，``j++``。

当``S[i] > S[j]``时，``i = j; j++``。

#### 情况1

``S[i+k+1 ... i+n-1] == S[j+k+1 ... j+n-1]``。

此时易得，字符串S是由一个长度为k的子串循环复制生成。所有的同构子串只有``RS[i ... j-1]``这k个，又由于``RS[i + 1 ... j - 1]``的所有字符串都字典序大于``RS[i]``。所以i即为最后的答案。

#### 情况2

``S[i+k+1 ... i+n-1] > S[j+k+1 ... j+n-1]``，那么此时``RS[i] > RS[j]``。

由于``S[i...i+k] == S[j...j+k]``，且这两个前辍中，只有``S[i] == S[j]``字典序最小。

所以i指向j点，保持最小性质。而j则指向``j + k + 1``。

保持i < j，且S[i] <= S[j]的性质。使问题回到我们归纳的子问题上来。

#### 情况3

``S[i+k+1 ... i+n-1] < S[j+k+1 ... j+n-1]``，那么此时``RS[i] < RS[j]``。

由于``S[i...i+k] == S[j...j+k]``，且这两个前辍中，只有``S[i] == S[j]``字典序最小。

所以i不变，保持最小性质。而j指向``j + k + 1``。

保持i < j，且S[i] <= S[j]的性质。使问题回到我们归纳的子问题上来。

## 代码

```cpp
// Result: wizmann	1509	Accepted	272K	16MS	C++	1247B	2014-09-17 00:44:22
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <algorithm>
#include <string>

using namespace std;

#define print(x) cout << x << endl
#define input(x) cin >> x

const int SIZE = 12345;

char instr[SIZE];

int solve(const char* str, int n)
{
    if (n <= 1) {
        return 0;
    }

    int p = 0, q = 1;
    while (p < n && q < n) {
        if (str[p] < str[q]) {
            q++;
        } else if (str[p] > str[q]) {
            p = q;
            q++;
        } else {
            int i, l = p, r = q;
            for (i = 0; i < n; i++) {
                int ll = l % n, rr = r % n;
                if (str[ll] < str[rr]) {
                    q = r;
                    break;
                } else if (str[ll] > str[rr]) {
                    p = q;
                    q = rr;
                    break;
                }
                l++; r++;
            }
            if (i == n) {
                break;
            }
        }
    }
    return p;
}

int main()
{
    int T;
    input(T);
    while (T--) {
        scanf("%s", instr);
        int u = solve(instr, strlen(instr));
        printf("%d\n", ++u);
    }
    return 0;
}
```

## 后记

* 证明的逻辑性不好，但是应该是对的。只是语言表达上问题很大。
* 有一个好的子问题假设会大大提升做题效率啊！

## 参考链接

* [理解字符串循环同构的最小表示法](http://blog.csdn.net/cclsoft/article/details/5467743)
