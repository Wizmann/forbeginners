Date: 2014-04-30 17:39
Title: Codeforces Round #242 (Div. 2) Tutorials and Solutions
Tags: codeforces, algorithm, 算法, 题解
Slug: cf-242-div-2


## A. Squats

Trun ``x => X`` or ``X => x`` to make the number of 'x' is equal to the number of 'X'.

```python
n = int(raw_input())
hamsters = [c for c in raw_input()]

sits = hamsters.count('x')
stands = hamsters.count('X')

if sits == stands:
    print 0
    print ''.join(hamsters)
else:
    if sits > stands:
        num = sits - n/2
        key = 'x'
    else:
        num = stands - n/2
        key = 'X'
    print num
    for i, c in enumerate(hamsters):
        if c == key:
            hamsters[i] = c.swapcase()
            num -= 1
        if not num:
            break
    print ''.join(hamsters)

```

## B. Megacity

Binary search.

Find the minimal radius of the circle to contain as many city as we need to form a **megacity**. But beware that you may get wrong answer if you take the lower bound of the binary search, and the answer may not exist if there no way to make a **megacity**.

```python
import math

class Point:
    def __init__(self, x, y, v):
        self.x = x 
        self.y = y
        self.v = v

def distance(a, b):
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)

def megacity(r, cities, v):
    u = 1000000 - v
    rem = 0
    for city in cities:
        if distance(Point(0, 0, 0), city) <= r:
            rem += city.v
    return rem >= u

n, v = map(int, raw_input().split())
cities = []
for i in xrange(n):
    (x, y, p) = map(int, raw_input().split())
    cities.append(Point(x, y, p))


left, right = 0, 2e6

while abs(left - right) > 1e-7:
    mid = (left + right) / 2.
    #print mid
    if megacity(mid, cities, v):
        right = mid
    else:
        left = mid

if megacity(right, cities, v):
    print right
else:
    print -1
```

## C. Magic Formulas

![Magic Formula][1]

```
U = reduce(xor, p[1...n])
V[i] = reduce(xor, map(j % i, [for j in 1...n]))
Q = U ^ reduce(xor, V[1...n])
```

First of all, we can easily get the value of ``U``.

Secondly, as ``n`` is up to ``1e6``. We have to reduce the calculation and the method will shown by code.

At last, we xor them all together to get the final result.

```cpp
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <algorithm>

using namespace std;

#define print(x) cout << x << endl
#define input(x) cin >> x

const int SIZE = 1000010;

int xorsum[SIZE];

void init()
{
    int sum = 0;
    xorsum[0] = 0;
    for (int i = 1; i < SIZE; i++) {
        sum ^= i;
        xorsum[i] = sum;
    }
}

int main()
{
    int n, Q = 0, a;
    init();
    input(n);
    for (int i = 0; i < n; i++) {
        scanf("%d", &a);
        Q ^= a;
    }

    for (int i = 1; i <= n; i++) {
        int div = (n / i) % 2;
        int rem = n % i;
        if (div) {
            Q ^= xorsum[i-1];
        }
        Q ^= xorsum[rem];
    }
    print(Q);
    return 0;
}
```

## D. Biathlon Track

Binary search again.

I calculate the wrong time complexity and get many ``TLE``s using brute force algorithm.

The idea is to fix the left-up point A, ``(ax, ay)``, and fix the y-axis of the right-buttom point B, ``(bx, by)``. And then, using binary search to get the x-axis of the B to get the nearest cost (aka "distance covering time") to the desired time ``t``.

The time complexity is ``O(logn * n^3)``. A bad ass code is below.

```cpp
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <algorithm>

using namespace std;

#define print(x) cout << x << endl
#define input(x) cin >> x

const int SIZE = 301;
const int DIRS = 4;
const int INF = 1 << 29;

typedef long long llint;

int n, m, t;
int tp, tu, td;

enum {
    NORTH, EAST, SOUTH, WEST
};

int land[SIZE][SIZE];
int costxy[4][SIZE][SIZE];

inline int move(int now, int next) {
    if (now > next) {
        return td;
    } else if (now == next) {
        return tp;
    } else {
        return tu;
    }
}
void count_time()
{
    for (int i = 0; i < m; i++) {
        for (int j = n - 2; j >= 0; j--) {
            costxy[NORTH][j][i] = costxy[NORTH][j + 1][i] + move(land[j + 1][i], land[j][i]);
        }
    }
    
    for (int i = 0; i < m; i++) {
        for (int j = 1; j < n; j++) {
            costxy[SOUTH][j][i] = costxy[SOUTH][j - 1][i] + move(land[j - 1][i], land[j][i]);
        }
    }
    
    for (int i = 0; i < n; i++) {
        for (int j = 1; j < m; j++) {
            costxy[EAST][i][j] = costxy[EAST][i][j - 1] + move(land[i][j - 1], land[i][j]);
        }
    }
    
    for (int i = 0; i < n; i++) {
        for (int j = m - 1; j >= 0; j--) {
            costxy[WEST][i][j] = costxy[WEST][i][j + 1] + move(land[i][j + 1], land[i][j]);
        }
    }
}

int get_cost(int ay, int ax, int by, int bx) 
{
    int cost = 0;
    cost += costxy[NORTH][ay][ax] - costxy[NORTH][by][ax];
    cost += costxy[SOUTH][by][bx] - costxy[SOUTH][ay][bx];
    cost += costxy[EAST][ay][bx]  - costxy[EAST][ay][ax];
    cost += costxy[WEST][by][ax]  - costxy[WEST][by][bx];
    return cost;
}

int main()
{
    freopen("input.txt", "r", stdin);
    scanf("%d%d%d", &n, &m, &t);
    scanf("%d%d%d", &tp, &tu, &td);
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            scanf("%d", &land[i][j]);
        }
    }
    count_time();

    int ans = -INF;
    int rsax, rsay, rsbx, rsby;

    for (int ay = 0; ay < n; ay++) {
    for (int ax = 0; ax < m; ax++) {
    for (int by = ay + 2; by < n; by++) {
        int lbx = ax + 2, rbx = m - 1;
        int now = lbx, step = rbx - lbx;
        while (step > 0) {
            int half = step >> 1;
            int mid = now + half;
            int cost = get_cost(ay, ax, by, mid);
            if (cost >= t) {
                step = half;
            } else {
                now = mid + 1;
                step = step - half - 1;
            }
        }
        
        for (int bx = now - 10; bx <= now + 10; bx++) {
            if (bx < lbx || bx > rbx) {
                continue;
            }
            int cost = get_cost(ay, ax, by, bx);
            // printf("%d %d %d %d => %d\n", ay, ax, by, bx, cost);
            if (abs(cost - t) < abs(ans - t)) {
                ans = cost;
                //print(ans);
                rsax = ax; rsay = ay; rsbx = bx; rsby = by;
                //printf("%d %d %d %d\n", rsay + 1, rsax + 1, rsby + 1, rsbx + 1);
            }
        }
    }
    }
    }
    printf("%d %d %d %d\n", rsay + 1, rsax + 1, rsby + 1, rsbx + 1);
    return 0;
}
```
[1]:https://github.com/Wizmann/assets/raw/master/wizmann-tk-pic/Magic-Formula.png
