Date: 2019-02-04 18:27:00
Title: 2019 BUPT Winter Training #3 div2 题解
Tags: 题解, 水题
Slug: BUPT-Winter-Training-3-div2

## 写在前面

做为一个年近半百的中年人，还能厚着脸皮蹭学弟学妹们的训练赛。真是开心啊。

## A - Constellation （CF 618C）

### 题意

在二维平面上给定一堆整数点，求任意一个三角形，使得三角形内以及其边上，不包含其它的点。

### 解法

我们先从一条边想起。选定任意一个点，从这个点引出的**最短边**上，一定不包含其它的点。（非常直观）

与这个思路类似，选定这条边之后，从这个边引出的面积最小的三角形，一定也不包含除三角形三点以外的其它点。

求三角形面积可以使用向量的叉积。

### 代码

```cpp
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <algorithm>
#include <map>
#include <vector>

using namespace std;

#define print(x) cout << x << endl
#define input(x) cin >> x

typedef long long llint;

const llint INF = 0x3f3f3f3f3f3f3f3fLL;

struct Point {
    int x, y;
};

int n;
vector<pair<int, int> > points;

int main() {
    input(n);
    points.reserve(n);
    for (int i = 0; i < n; i++) {
        int x, y;
        scanf("%d%d", &x, &y);
        points.push_back({x, y});
    }

    int p1 = -1;
    llint d1 = INF;

    for (int i = 1; i < n; i++) {
        llint dx = points[0].first - points[i].first;
        llint dy = points[0].second - points[i].second;

        llint dis = dx * dx + dy * dy;

        if (dis < d1) {
            d1 = dis;
            p1 = i;
        }
    }

    int p2 = -1;
    llint d2 = INF;
    for (int i = 1; i < n; i++) {
        if (i == p1) {
            continue;
        }

        llint dx1 = points[0].first - points[p1].first;
        llint dy1 = points[0].second - points[p1].second;

        llint dx2 = points[0].first - points[i].first;
        llint dy2 = points[0].second - points[i].second;

        llint xmult = abs(dx1 * dy2 - dy1 * dx2);

        if (xmult != 0 && xmult < d2) {
            p2 = i;
            d2 = xmult;
        }
    }

    print(1 << ' ' << p1 + 1 << ' ' << p2 + 1);

    return 0;
}
```

## B - Wet Shark and Flowers （CF 621C）

### 题意

有一个头尾相接的整数数组，数组中的每个数都在一个给定的范围之内随机选取。如果相邻的两个整数的乘积可以被`p`整除，就可以获得2000分。求给定数组得分的期望。

### 解法

对于数组中的数来说，得分的期望与其临近的数相关，而当前的数字与相邻的数字在概率上是独立的。所以我们只需要遍历数组，找到相邻数字的得分期望即可。

### 代码

```python
(n, p) = map(int, raw_input().split())
xs = []

for i in xrange(n):
    l, r = map(int, raw_input().split())
    m = r - l + 1

    l = l if l % p == 0 else (l / p + 1) * p

    if l > r:
        xs.append((1.0, 0))
    else:
        u = (r - l) / p + 1
        pp = 1.0 * u / m
        xs.append((1 - pp, pp))

res = 0
for i in xrange(n):
    p, q = (i - 1 + n) % n, (i + 1) % n
    res += 2000 * xs[i][1] + 2000 * xs[p][1] * xs[i][0]
print res
```

## C - Wet Shark and Odd and Even （CF 621A）

### 题意

给定一个正整数数组，求这个数组的一个子数组，使得子数组的和最大，且为一个偶数。

### 解法

如果数组之和为偶数，那它一定是最终答案。如果数组之和为奇数，则找到数组中最小的奇数，减去其值即可。

### 代码

```python
n = int(raw_input())
ns = map(int, raw_input().split())

s = sum(ns)

if s % 2 == 0:
    print s
else:
    res = 0
    for num in ns:
        if (s - num) % 2 == 0:
            res = max(res, s - num)
    print res
```

## D - Graph and String (CF 624C)

### 题意

假设我们有一个图，图中的节点被标记为`a,b,c`三个字母中的一个。如果两个节点的标记相同，或者标记相邻（如`<a, b>`和`<b, c>`），则两个节点之间一定有一条边。我们称这样的图为“合法图”。

现在给定一张图，问这张图是否合法。如果是，给出任意一个可行解。

### 解法

本题可以从标记为`b`的节点入手。如果一个节点被标记为`b`，那么它一定和图中任意其它节点都有一条边。然后我们再把其它不相连的节点分别标记为`a`和`c`。

但是注意，我们做完标记之后的图不一定是合法的。此时我们会再进行一次检查，如果合法则输出解。不合法则输出`No`。

### 代码

```python
(n, m) = map(int, raw_input().split())

g = [[0 for i in xrange(n)] for i in xrange(n)]
for i in xrange(m):
    (a, b) = map(int, raw_input().split())
    a -= 1
    b -= 1
    g[a][b] = 1
    g[b][a] = 1

mark = ['' for i in xrange(n)]

def solve1(cur):
    for i in xrange(n):
        if mark[i]:
            continue
        if i == cur or g[cur][i]:
            mark[i] = 'a'
        else:
            mark[i] = 'c'

def check():
    for i in xrange(n):
        for j in xrange(n):
            if i == j:
                continue
            if mark[i] == mark[j] and g[i][j] == 0:
                return False
            if abs(ord(mark[i]) - ord(mark[j])) == 1 and g[i][j] == 0:
                return False
            if abs(ord(mark[i]) - ord(mark[j])) > 1 and g[i][j] == 1:
                return False
    return True


for i in xrange(n):
    if sum(g[i]) == n - 1:
        mark[i] = 'b'

flag = True
for i in xrange(n):
    if mark[i] == '':
        flag = solve1(i)
        break
if check():
    print 'Yes'
    print ''.join(mark)
else:
    print 'No'
```

## E - Array GCD （CF 624D）

### 题意

给定一个整数数组，规定两种操作：

1. 删除最多一个连续的子数组，每删除一个数字的代价为`a`。但是不能把数组删空。
2. 修改任意多的数字，但是最多只能加1或者减1，每修改一个数字的代价为`b`。

问在操作过后，若想使剩下的数组的GCD不为1，所需要付出的最小代价是多少。

### 解法

我们从结果反推过程。对于一个合法答案来说，一定只包含（修改后的）数组的前缀`A[0...l]`**与/或**（修改后的）数组后缀`A[r...n-1]`。所以合法答案中的GCD，一定是前缀或后缀的一个质因子。并且质因子的个数不会超过20（思考：为什么？）

我们枚举这些质因子p。首先求出维护GCD=p的前辍所需要的代价。这里的代价，指的是修改`A[0...l]`**加上**删除`A[l + 1...n - 1]`的代价。记录这些值，然后加上一个最小前辍优化。

然后再求出维护GCD=p的后辍需要的代价。这里代价，指的是修改`B[r...n - 1]`的代价，**减去**删除`B[r...n - 1]`的代价。这是因为，在前缀的计算中，我们多减去了后缀的部分。后缀的值与前面的最小前缀进行加和，求出全局最小值即可。

### 代码

> 略挫，仅供参考。

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

typedef long long llint;

const int N = 1000007;
const int M = 22;
const llint INF = 0x3f3f3f3f3f3f3f3f;

int n, A, B;
vector<int> ns;
vector<int> primes;

llint dp[N][M];

void get_primes(int num, set<int>& st) {
    if (num <= 1) {
        return;
    }

    if (num % 2 == 0) {
        st.insert(2);
        num /= 2;
    }
    for (llint i = 3; i * i <= num; i += 2) {
        if (num % i == 0) {
            st.insert(i);
        }
        while (num % i == 0) {
            num /= i;
        }
    }

    if (num != 1) {
        st.insert(num);
    }
}

llint solve() {
    memset(dp, INF, sizeof(dp));
    llint ans = INF;

    for (int i = 0; i < primes.size(); i++) {
        llint delta = 1LL * A * n;
        for (int j = 0; j < n; j++) {
            llint mincost = INF;
            for (int k = -1; k <= 1; k++) {
                int u = ns[j] + k;
                llint cost = 1LL * abs(k) * B - A;

                if (u % primes[i] == 0) {
                    mincost = min(mincost, cost);
                }
            }
            if (mincost == INF) {
                break;
            }
            delta += mincost;
            dp[j][i] = delta;
            ans = min(ans, delta);
        }
    }

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < primes.size(); j++) {
            // printf("%lld ", dp[i][j]);
            if (i - 1 >= 0) {
                dp[i][j] = min(dp[i][j], dp[i - 1][j]);
            }
        }
        // puts("");
    }
    // print(ans);

    for (int i = 0; i < primes.size(); i++) {
        llint delta = 0;
        for (int j = n - 1; j >= 0; j--) {
            llint mincost = INF;
            for (int k = -1; k <= 1; k++) {
                int u = ns[j] + k;
                llint cost = 1LL * abs(k) * B - A;

                if (u % primes[i] == 0) {
                    mincost = min(mincost, cost);
                }
            }
            if (mincost == INF) {
                break;
            }
            delta += mincost;
            // print(i << ' ' << j << ' ' << delta);
            if (j - 1 >= 0) {
                ans = min(ans, delta + dp[j - 1][i]);
            }
        }
    }

    return ans;
}

int main() {
    input(n >> A >> B);
    ns.resize(n);
    for (int i = 0; i < n; i++) {
        scanf("%d", &ns[i]);
    }

    set<int> st;
    get_primes(ns[0], st);
    get_primes(ns[n - 1], st);
    get_primes(ns[0] - 1, st);
    get_primes(ns[n - 1] - 1, st);
    get_primes(ns[0] + 1, st);
    get_primes(ns[n - 1] + 1, st);

    primes.reserve(st.size());
    for (auto num: st) {
        primes.push_back(num);
    }

    llint ans = INF;

    ans = min(ans, solve());
    reverse(ns.begin(), ns.end());
    ans = min(ans, solve());

    print(ans);

    return 0;
}
```

## F - Queries about less or equal elements （CF 600B）

### 题意

求数组B中有多少个数小于等于A[i]。

二分随便搞。解略。

## G - Area of Two Circles' Intersection （CF 600D)

### 题意

给定两个圆，求两个圆相交面积的大小。

### 解法

> 做计算几何的最好方法，就是不做计算几何。因为精度太TM烦人了。  —— 介四·窝硕德

题目看上去非常简单，就是求两个弓形的面积之和。这属于高中数学的知识范畴，这里不在赘述。

但是本题的问题在于给定圆的面积太大，我们在进行计算时（尤其是三角函数），容易丢失精度，导致WA。`

本题的很多解法都使用了`long double`，`acosl`等高精度浮点数函数。但是这里介绍另外一种解法。

数学好的同学们都知道，三角函数可以通过泰勒公式来计算，而开方可以通过牛顿法来解决。这两个算法都只使用了加减乘除的基本运算，所以几乎不会丢失精度。

在Python语言中，我们有`Decimal`类，可以存储高精度的整数与浮点数。并且在现在的比赛中，越来越多的有支持Python。所以可以备一份模板防身，避免被卡姿势和精度。

### 代码

```python
import sys
import math
from decimal import *

def sqrt(v):
    a = Decimal(0)
    b = v
    while a != b:
        a = b
        b = (a+v/a)/TWO
    return a

TWO = Decimal(2)
S = 1/sqrt(Decimal(2))
getcontext().prec = 50
PI = Decimal(math.pi)

def taylor_acos(v):
    return PI/2 - taylor_asin(v)

def taylor_asin(v):
    curr = v
    vsq = v**2
    ans = v
    coef = Decimal(1.)
    for i in xrange(3, 101, 2):
        curr *= vsq
        coef = coef * (i-2) / (i-1)
        ans += curr * coef / i
    return ans


def acos(v):
    if v <= S:
        return Decimal(taylor_acos(v))
    return Decimal(taylor_asin(sqrt(1-v**2)))


class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

def point_dis(p1, p2):
    return sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

def get_area(l1, l2, l3):
    s = (l1 + l2 + l3) / Decimal(2.0)
    return sqrt(s * (s - l1) * (s - l2) * (s - l3))


(x1, y1, r1) = map(int, raw_input().split())
(x2, y2, r2) = map(int, raw_input().split())

c1 = Point(x1, y1)
c2 = Point(x2, y2)

dis = point_dis(c1, c2)

if dis >= r1 + r2:
    print 0.0
    sys.exit(0)
if dis == 0:
    print PI * (min(r1, r2) ** 2)
    sys.exit(0)

if min(r1, r2) + dis <= max(r1, r2):
    print PI * (min(r1, r2) ** 2)
    sys.exit(0)

r1, r2, dis = map(Decimal, [r1, r2, dis])

a1 = acos((r1 * r1 + dis * dis - r2 * r2) / (2 * r1 * dis)) * 2
a2 = acos((r2 * r2 + dis * dis - r1 * r1) / (2 * r2 * dis)) * 2

s1 = PI * r1 * r1 * (2 * PI - a1) / (2 * PI)
s2 = PI * r2 * r2 * (2 * PI - a2) / (2 * PI)

s3 = 2 * get_area(r1, r2, dis)

print PI * r1 * r1 + PI * r2 * r2 - s1 - s2 - s3
```

## H - Order Book （CF 527B）

### 题意

很绕。简单来说就是个排序问题。

解略。
