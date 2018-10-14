Date: 2013-12-9 23:02
Title: Codeforces Round #218 (Div. 2)不完全不正确题解
Tags: codeforces, algorithm, 算法, 题解
Slug: cf-218-div-2

### A. K-Periodic Array

将Array切片，然后按位统计某一位上1的个数C(1)和2的个数C(2)。然后在这一位上的操作数就为M = min(C(1), C(2))。

简单题

### B. Fox Dividing Cheese

傻逼才错的题，不幸中枪。

不想多说了，直接看代码吧。手贱不是病，贱起来要人命。

### C. Hamburgers

模拟 + 二分。

和CJL还讨论过这题的纯模拟做法，看了半天代码没找到问题。于是刚才用Python自己实现了一个，在代码正确的情况下，没有WA，但是T在了22组上。

所以这题最好使用二分，如果用模拟的话，需要考虑各种情况。代码见下，细节上注意就好。

### D. Vessels

这题得好好讲一下～比赛时做出来了好得意～

![Vessels][1]

题意是给出一组层层叠的容器，每一个容器都有自己的容量。然后我们向某些容器里灌水，如果水的体积超过了某个容器的容量，则剩余的水溢出到下一个容器中。最后一个容器溢出的水会落到地面上，所以忽略不计。

我们可以看出，如果某一个容器是满的，那么它就再也不会空下来，并且流经它的水全部溢出给下面的容器。

于是我们用一个数组记录当前容器注水的时候，水会流向哪个容器。

由于在初始状态下，所有容器都是空的。所以``to[i] = i``。

如果某容器由于注水满掉了，我们就把注水的指向指到``i + 1``，就有``to[i] = i + 1``。

下次在向容器i注水的时候，我们通过查询``to[i]``的值，就可以知道水的流向。

这可以转化为一个并查集问题。如果i满了，``to[i] == i + 1``。与此同时，i+1也满了，则``to[i + 1] == i + 2``。从题意我们可以看出，此时``to[i] == to[i + 1] == i + 2``。

这样我们就几乎可以把每次注水的流向的查询优化到``O(1)``。剩下的就是基本的加减法和输入输出操作了。


### E. Subway Innovation

推公式题，专治智商不够。

上一份别人的题解，我估计推不出来了。。。

![E题题解][2]

### 以下是代码

#### A

```python
(n, k) = map(int, raw_input().split())
ll = map(int, raw_input().split())

ans = 0

for i in xrange(k):
    ones = 0
    twos = 0
    for j in xrange(i, n, k):
        if ll[j] == 1:
            ones += 1
        else:
            twos += 1

    ans += min(ones, twos)

print ans

```


#### B

```python
from fractions import gcd

def avail(a):
    ans = 0
    while a % 2 == 0:
        ans += 1
        a /= 2
    while a % 3 == 0:
        ans += 1
        a /= 3
    while a % 5 == 0:
        ans += 1
        a /= 5

    if a != 1:
        return -1
    else:
        return ans


(a, b) = map(int, raw_input().split())

c = gcd(a, b)

a /= c
b /= c

av = avail(a)
gv = avail(b)

if av != -1 and gv != -1:
    print av + gv
else:
    print -1
```

#### C

```cpp
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <algorithm>
#include <vector>
#include <string>

using namespace std;

#define print(x) cout << x << endl
#define input(x) cin >> x

typedef long long llint;

const int BUFFER = 128;
const int SIZE = 5;

llint need[SIZE];
llint have[SIZE];
llint cost[SIZE];
llint money;

llint calc(llint num) {
    llint res = 0;
    for (int i = 0; i < 3; i++) {
        llint t = max(0LL, num * need[i] - have[i]);
        res += t * cost[i];
    }
    return res;
}

llint solve()
{
    llint step = 10000000000000LL;
    llint now = 0;
    while (step) {
        llint half = step >> 1;
        llint mid = now + half;

        if (calc(mid) > money) {
            step = half;
        } else {
            now = mid + 1;
            step = step - half - 1;
        }
    }
    return now;
}

int main()
{
    freopen("input.txt", "r", stdin);
    char buffer[BUFFER];

    while (input(buffer)) {
        memset(need, 0, sizeof(need));
        memset(have, 0, sizeof(have));
        memset(cost, 0, sizeof(money));

        for (int i = 0; buffer[i]; i++) {
            switch (buffer[i]) {
                case 'B': need[0]++; break;
                case 'S': need[1]++; break;
                case 'C': need[2]++; break;
                default: break;
            }
        }

        for (int i = 0; i < 3; i++) {
            input(have[i]);
        }
        for (int i = 0; i < 3; i++) {
            input(cost[i]);
        }

        input(money);

        llint ans = solve() - 1;
        print(max(0LL, ans));
    }
    return 0;
}

```


#### D

```cpp
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <algorithm>
#include <vector>
#include <string>

using namespace std;

#define print(x) cout << x << endl
#define input(x) cin >> x

typedef long long llint;

const int SIZE = 200100;

int n, m;
llint cap[SIZE];
llint vessel[SIZE];

int father[SIZE];

int find_father(int x)
{
    if (father[x] == x) return x;
    else return father[x] = find_father(father[x]);
}

void pour(int pos, llint value) {
    vessel[pos] += value;
    if (vessel[pos] > cap[pos]) {
        if (pos == n - 1) {
            vessel[pos] = cap[pos];
            return;
        } else {
            llint overflow = vessel[pos] - cap[pos];
            father[pos] = find_father(pos + 1);
            vessel[pos] = cap[pos];
            pour(father[pos], overflow);
        }
    }
}

llint query(int pos)
{
    return vessel[pos];
}

int main()
{
    freopen("input.txt", "r", stdin);
    llint a, b, c;
    input(n);

    for (int i = 0; i < SIZE; i++) {
        father[i] = i;
    }

    memset(cap, 0, sizeof(cap));
    memset(vessel, 0, sizeof(vessel));

    for (int i = 0; i < n; i++) {
        input(cap[i]);
    }

    input(m);
    while (m--) {
        input(a);
        if (a == 1) {
            input(b >> c);
            pour(--b, c);
        } else {
            input(b);
            print(query(--b));
        }
    }
    
    return 0;
}
```


#### E

```cpp
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <iostream>
#include <algorithm>
#include <vector>
#include <set>

using namespace std;

#define print(x) cout << x << endl
#define input(x) cin >> x

typedef long long llint;

struct node {
    int pos, nr;
    node(){}
    node(int ipos, int inr):
            pos(ipos), nr(inr) {}

    bool operator < (const node& x) const 
    {
        return pos < x.pos;
    }
};

const int SIZE = 300008;

node station[SIZE];
llint leftsum[SIZE];

llint n, k;

int main() 
{
    input(n);
    for (int i = 0; i < n; i++) {
        input(station[i].pos);
        station[i].nr = i + 1;
    }
    input(k);
    sort(station, station + n);
    for (int i = 1; i < n; i++) {
        leftsum[i] = leftsum[i-1] + station[i].pos;
    }
    
    llint f = 0;
    for (int i = 1; i <= k; i++) {
        f += (llint)station[i].pos * i - leftsum[i-1];
    }
    
    llint res = f;
    int pos = 0;
    k--;
    for (int i = 1; i < n - k; i++) {
        f += station[i+k].pos * k;
        f -= leftsum[i+k-1] * 2;
        f += leftsum[i-1] * 2 ;
        f += station[i-1].pos * k;
        if (f < res) {
            res = f;
            pos = i;
        }
    }
    for (int i=0; i<=k; i++) {
        printf("%d ", station[pos + i].nr);
    }
    return 0;
}
```

[1]: http://wizmann-tk-pic.u.qiniudn.com/blog-cf-218-div-2-d-vessels.png
[2]: http://wizmann-tk-pic.u.qiniudn.com/blog-cf-218-div-2-e.png
