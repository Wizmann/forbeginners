Date: 2015-04-12 
Title: GCJ Qualification Round 2015 题解
Tags: GCJ, algorithm, 算法, 题解, google
Slug: gcj-qualification-round-2015-tutorial

## 前言

这篇日志用中文写是因为想省点时间打游戏。。。（请鄙视我吧。。。

## A. Standing Ovation

### 题意

这是一个骗掌声的故事。

当演出结束后，观众们要站起来鼓掌。但是有些观众比较羞涩，只有在k个人站起来鼓掌后才会故障。

你的目标是在观众中安插一些卧底领掌，让所有观众都站起来鼓掌。（臭不要脸）

求最少的卧底数。

### 数据规模

> 抛开数据规模谈解题，都是TM耍流氓。 —— Wizmann

100组数据。

小数据集，观众羞涩值的范围：0 ≤ Smax ≤ 6.

大数据集，观众羞涩值的范围：0 ≤ Smax ≤ 1000.

### 解题

本题比较简单。有两种方法，一是暴力枚举，因为大数据集中，观众羞涩值最大只为1000,即最大安插卧底数不超过1000。(当然，二分也可以，不过对于1000的数据集，真心没啥必要。)

二是O(N)的一个遍历，在观众羞涩的不想鼓掌时，安插相应数量的卧底。

本题推荐方法一。因为个人感觉，在编程竞赛中，在时限和空间允许的情况下，尽量让方法简单化。这样不容易出错。但是在要体现逼格的时候，尽量“优化”你的代码，提升思考复杂度来换取尽可能多的优化。

```python
def solve():
    (n, aud) = raw_input().split()
    n = int(n)
    aud = map(int, aud)
    stand = aud[0]
    res = 0
    for i in xrange(1, n + 1):
        u = aud[i]
        if not u:
            continue
        if i > stand:
            res += i - stand
            stand = i
        stand += u
    return res

T = int(raw_input())

for i in xrange(T):
    print 'Case #%d: %d' % (i + 1, solve())
```

## B. Infinite House of Pancakes

### 题意

在一个宴会厅中（想到了“米阿的宴会厅”)，有无限的客人，但是只有有限的煎饼。你的目标是让所有客人尽可能快的吃完所有的煎饼。

每个客人在一个单位时间只能吃一块煎饼。你也可以在一个单位时间内，调整一个客人的煎饼，即把他的煎饼给别人。

求所有客人吃完所有煎饼的时间。

> 'Here comes Mia, daughter of none!'    
-- _The Dark Tower V: Wolves of the Calla_

### 数据规模

100组测试数据。

D为有煎饼的客人的数目。Pi为客人拥有煎饼的最大值。

小数据：    
1 ≤ D ≤ 6.   
1 ≤ Pi ≤ 9.

大数据：    
1 ≤ D ≤ 1000.   
1 ≤ Pi ≤ 1000.

### 解题

一开始想用二分做。但是这道题并不能满足二分的条件。因为无论是二分时间还是二分最大煎饼数，客人都可以吃完煎饼，这样的二分是没有意义的。

换个思路，在吃煎饼前，我们可以对所有客人的煎饼数进行调整。又由于客人的数目是无限多的，所以我们的调整就是**把煎饼送给没有煎饼的客人**。调整的目标是**让煎饼数尽量平均**（“尽量”和“尽可能”是不同的，“尽量”的范围更宽范一些）。

于是，我们尝试枚举“调整后的最大煎饼数量”。通过枚举这个值，我们可以很容易得到“调整煎饼时间 + 吃煎饼时间”。又由于数据规模比较小，搞起来不是很困难。

```cpp
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <algorithm>
#include <vector>
#include <set>

using namespace std;

#define print(x) cout << x << endl
#define input(x) cin >> x

const int SIZE = 1024 + 233;

int n;
vector<int> vec;

int main() {
    int T, a, cas = 1;
    input(T);

    while (T--) {
        input(n);
        vec.clear();
        for (int i = 0; i < n; i++) {
            input(a);
            vec.push_back(a);
        }

        int ans = SIZE * 233;
        for (int i = 1; i <= SIZE; i++) {
            int step = 0;
            int maxi = 0;
            for (const auto& num: vec) {
                if (num > i) {
                    step += num % i? num / i: num / i - 1;
                    maxi = i;
                } else {
                    maxi = max(maxi, num);
                }
            }
            ans = min(ans, step + maxi);
        }
            
                
        printf("Case #%d: %d\n", cas++, ans);
    }
    return 0;
}
```

## C. Dijkstra

### 题意

给你一个代数系统（可以这么说吧），包括“1, i, j, k”。

已知它们的运算规律。

![Alt text](http://wizmann-pic.qiniudn.com/ba89abba98064a7e42e52e9e5b2de57f)

现在，有一个包含"i, j, k"的连乘式。它是由一段连乘式重复X遍得出的。

问，能否把它转化为`i * j * k`的形式。

### 数据规模

测试组数： 1 ≤ T ≤ 100.     
给出的连乘式长度： 1 ≤ L ≤ 10000.     


连乘式的重复次数为X。

小数据集：    
1 ≤ X ≤ 10000.     
1 ≤ L * X ≤ 10000.     

大数据集：   
1 ≤ X ≤ 10^12.    
1 ≤ L * X ≤ 10^16.    

### 解题

题中给出了乘法的规律。我们不难从中推测出除法的规律。

假设我们已经把连乘式转化为`i * j`的形式，那么我们只需要把剩下的部分转化为数字`k`，即可满足题意。

我们可以去思考转化的过程，当然，也可以逆向思考，去思考转化后的结果。

我们知道，`i * j * k == -1`，当我们把前辍转化为`i * j`的形式后，如果判断整个连乘式的结果为`-1`，此时，我们可以断定，该连乘式可以转化为`i * j * k`的形式。

i与j的转化是类似的。

所以整个算法的时间复杂度为O(N)。

但是，O(N)的算法是无法通过大数据集的。因为，连乘式是循环的，总长度可能会非常长。

我们继续使用同样的思路。如果我们有了i和j，当整体连乘式之积为`-1`时，即断定满足条件。这里，我们使用快速幂算法，直接计算循环节的乘积。复杂度为`O(L) + O(logX)`。

对于i和j，我们可以这样考虑。循环节之积只有以下几种可能：`±1, ±i, ±j, ±k`。

![the table](http://wizmann-pic.qiniudn.com/252e0e81143f2dd5cb6e01e1e69d0709)

我们可以看出，对于`1, i, j, k`，乘法都是有一个循环节的。这里不需要定量分析，我们可以直接断定，如果在一定的循环节中，不能把算式转化为`i * j`的形式，那么就不可能转化。

所以，代码如下：

```cpp
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <algorithm>
#include <vector>

using namespace std;

#define print(x) cout << x << endl
#define input(x) cin >> x
#define error(x) cerr << x << endl

const int SIZE = 12345;

enum {
    ONE = 1,
    II  = 2,
    JJ  = 3,
    KK  = 4
};

int trans[5][5] = {
    {0, 0,   0,    0,   0},
    {0, ONE, II,   JJ,  KK},
    {0, II,  -ONE, KK, -JJ},
    {0, JJ,  -KK, -ONE, II},
    {0, KK,  JJ,  -II, -ONE}
};

int conv(char c) {
    switch (c) {
        case '1': return ONE;
        case 'i': return II;
        case 'j': return JJ;
        case 'k': return KK;
    }
    return -1;
}

struct Number {
    int sign;
    int value;

    Number() {}
    Number(char c) {
        sign = 1;
        value = conv(c);
    }
    Number(int isign, int ivalue): sign(isign), value(ivalue){}

    Number operator * (const Number& num) {
        int a = num.sign * sign;
        int b = trans[value][num.value];
        if (b < 0) {
            a *= -1;
            b = abs(b);
        }
        return Number{a, b};
    }
};

string _word;
string word;

long long L, X;

bool get_whole() {
    Number num('1');
    for (auto& c: _word) {
        num = num * Number(c);
    }
    Number ans('1');
    
    long long x = X;
    while (x) {
        if (x & 1) {
            ans = ans * num;
        }
        num = num * num;
        x >>= 1;
    }
    return ans.sign == -1 and ans.value == ONE;
}

int main() {
    int T, cas = 1;
    input(T);
    while (T--) {
        input(L >> X);
        input(_word);
        word = "";
        for (int i = 0; i < min(X, 19LL); i++) {
            word += _word;
        }
        
        Number num('1');
        
        bool ii = false;
        bool jj = false;
        bool kk = get_whole();
        
        int n = word.size();
        
        for (int i = 0; i < n - 1; i++) {
            num = num * word[i];
            
            if (num.sign == 1 && num.value == II) {
                ii = true;
            }else if (ii && num.sign == 1 && num.value == KK) {
                jj = true;
                break;
            }
        }
        kk = (kk && ii && jj);
        printf("Case #%d: ", cas++);
        puts(kk? "YES": "NO");
    }
    return 0;
}
```

`19`是一个magic number。还有，小心<del>Dandelo</del>数据超int。

![Alt text](http://wizmann-pic.qiniudn.com/625c5bb804b76545978bcb11310099a6)

## D. Ominous Omino

充满玄学的一题。网上看到的最精彩的题解是人工模拟出了所有可能。

我觉得像我这种内存小的人，估计是想不出来的。

貌似也有人用模拟。。。我觉得。。。可能会有更优雅的方法。。。

题解在[这里][1]，真心是给跪了。

[1]: http://www.huangwenchao.com.cn/2015/04/gcj-2015-qual-d.html
