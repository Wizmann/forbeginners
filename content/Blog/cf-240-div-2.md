Date: 2014-04-08 14:39:11 
Title: Codeforces Round #240 (Div. 2) Tutorials and Solutions(incomplete and incorrect)
Tags: codeforces, algorithm, 算法, 题解
Slug: cf-240-div-2

## Overview

It has been months that I didn't participate in the contest on CF, now I'm back. :)

This round of contest makes me confused that the problem B and C is a little bit too twisted, if you can't catch the vital point, you will get a lot of WAs in the end.

Additionally, the problem D is too easy, just a simple DP and the time limit is too long for an unoptimized solution.

And as usual, I have no idea to the problem E. :(

## A. Mashmokh and Lights

The description is too long for a problem A, but it is as easy as it used to be.

Just decalre an array to keep the records of who is the first to turn off the light.

```python
(n, m) = map(int, raw_input().split())
bs = map(int, raw_input().split())

ts = [0 for i in xrange(n + 1)]

for b in bs:
    for i in xrange(b, n + 1):
        if not ts[i]:
            ts[i] = b

print ' '.join(map(str, ts[1:]))
```

## B. Mashmokh and Tokens

It is quite confused that Mashmokh just save the tokens for NOTHING?! I took it for granted that Mashmokh should save all the extra token for a final exchange. But I was wrong. The problem just asks for how many tokens is useless for the tokens-salary exchange everyday.

Uh, so sad. If I was Mashmokh, I just give all my tokens to my boss as the saved tokens  would never counts.

```python
n, a, b = map(int, raw_input().split())
ts = map(int, raw_input().split())

for t in ts:
    c = (t * a) % b
    print c / a,
```

## C. Mashmokh and Numbers

You need a full-time QA for this problem because some of the scenarios will lead to hours of debuging. :(

The  thought of the problem is easy enough, just print two numbers with the gcd equal to ``g`` and a sequence of squential numbers with m pairs that each pair has a gcd equals to ``1``. At last, just make sure that ``g + m == k``.

However, there are some **special** test cases.

n = 1, k = 0. 
You can pass this case if you print any positive number.                      

n = 1, k - (n / 2) + 1 <= 0. 
It will lead to "-1".

And the scenarios that the n is odd.

```python
n, k = map(int, raw_input().split())

m = n / 2
t = k - (m - 1)

if n == 1 and k == 0:
    print 19,
elif n == 1 or t <= 0:
    print -1
else:
    print t, 2 * t,
    
    idx = 1
    for i in xrange(m):
        while True:
            a, b = idx, idx + 1
            idx += 2
            if [a, b] != [t, 2 * t]:
                break;
        if i == m - 1:
            if n % 2:
                print a,
        else:
            print a, b,
```

## D. Mashmokh and ACM

A simple DP problem. The formula is quite easy.

```
dp[k][i] = sum(dp[a0][i - 1] + dp[a1][i - 1] ... dp[ai][i - 1])
(k % ai == 0)
```

The time complexity is ``m * n * (1 + 1/2 + 1/3 + ... 1/n)``, and the sum of series ``1 + 1/2 + ...`` is called harmonic number of n which approximately equals to ``ln(n)``. So the final time complexity is ``m * n * ln(n)``.

Further, we can reuse the space of dp array to gain a better CPU cache optimizism.

```cpp
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <algorithm>
#include <ctime>
#include <map>

using namespace std;

#define print(x) cout<<x<<endl
#define input(x) cin>>x

typedef long long llint;

const int SIZE = 2048;
const llint MOD = 1000000007LL;

int n, m;
llint dp[SIZE][SIZE];

int main()
{
    input(n >> m);
    memset(dp, 0, sizeof(dp));
    for (int i = 1; i <= n; i++) {
        dp[i][0] = 1;
    }
    
    for (int i = 1; i < m; i++) {
        for (int j = 1; j <= n; j++) {
           for (int k = 1; j * k < SIZE; k++) {
               dp[j * k][i] += dp[j][i - 1];
               dp[j * k][i] %= MOD;
            }
        }
    }

    llint ans = 0;
    for (int i = 1; i <= n; i++) {
        ans += dp[i][m - 1];
        ans %= MOD;
    }
    print (ans);
    return 0;
}
```
