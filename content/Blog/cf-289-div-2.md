Date: 2015-02-16 21:16:31 
Title: Codeforces Round #289 (Div. 2) Tutorial
Tags: codeforces, algorithm, 算法, 题解
Slug: cf-289-div-2

## A. Maximum in Table

Simulation. 

```python
n = int(raw_input())
g = [[1 for i in xrange(n)] for j in xrange(n)]

for i in xrange(1, n):
    for j in xrange(1, n):
        g[i][j] = g[i - 1][j] + g[i][j - 1]

print g[n - 1][n - 1]
```

## B. Painting Pebbles

Reading comperhension & Constructive.

The key point of this problem is `abs(b(i, c) - b(j, c)) <= 1`.

First of all, it's safe to paint k pebbles of every pile with the same color, when `k = min(piles)`. At this moment, every `b(i, c) - b(j, c) == 0`.

And then, we paint 1 pebbles of every pile with color `C[i]` at a time (if possible). That is, for every pile, the number of pebbles with color `C[i]` is zero or one.

If you can't paint all the pebbles with proper color, just print a "NO" here.

```python
(n, k) = map(int, raw_input().split())
ps = map(int, raw_input().split())

(mini, maxi) = min(ps), max(ps)

if maxi - mini > k:
    print 'NO'
    exit(0)

print 'YES'
for p in ps:
    r = [1 for i in xrange(mini)] + [i + 1 for i in xrange(p - mini)]
    print ' '.join(map(str, r))
```

## C. Sums of Digits

Brute force & Constructive

After reading this problem, there is one thing that we could NEVER miss is the scope of number n: `1 <= n <= 300`, which means that the max number here is no more than 40 digits and we can solve the problem with brute force.

As we know, the number in the array must be incremental, and every number should be the minimum.

Assuming we have got an array which is incremental, the last number is K. Such as:

```
K = d3 ++ d2 ++ d1 ++ d0
```

Our mission is to find a way to generate the smallest number which follow the rules:

1. the number here is greater than the previous one
2. the digit sum

Rule No.1 is not hard as it seems, if we increase any digit of the number K, the new number is of course greater. But how to satisfy the digit sum?

For example, we got a new number `K1`:

```
K1 = d3 ++ (d2 + 1) ++ d1 ++ d0
```

Here, of course, `K1 > K`. But the number `K2`:

```
K2= d3 ++ (d2 + 1) ++ 0 ++ 0
```

is smaller then `K1`, and also greater than the number `K`.

And then, we fill the lower digits with number to make the sum of the digits equal to the given one. If failed, keep on trying, such as:

```
K3 = d3 ++ (d2 + 2) ++ 0 ++ 0
```
or
```
K4 = (d3 + 1) ++ 0 ++ 0 ++ 0
```

or even

```
K5 = 1 ++ 0 ++ 0 ++ 0 ++ 0
```

```python
import sys

def do_fill(num, ptr, delta):
    for i in xrange(ptr):
        num[i] = min(9, delta)
        delta -= num[i]
    return delta == 0

def solve(num, pre):
    l = len(pre)
    i = 0

    while True:
        t = pre + [0 for j in xrange(i - l + 1)]
        while t[i] + 1 < 10:
            t[i] += 1
            for j in xrange(i):
                t[j] = 0
            delta = num - sum(t)
            if delta < 0:
                break
            if do_fill(t, i, delta):
                return t
        i += 1

if __name__ == '__main__':
    ns = map(int, sys.stdin)[1:]
    ans = [[0]]

    for num in ns:
        ans.append(solve(num, ans[-1]))

    for item in ans[1:]:
        print ''.join(map(str, item[::-1]))
```

## D. Restoring Numbers

Math

Each number of the input matrix is `(A[i] + B[i]) % MOD`. And we can get `(A[i] - A[j]) % MOD` by subtract the number on the same line.

Sometimes, the `(A[i] - A[j]) % MOD` can be both positive and negetive. And we can get the value of `MOD` here.

As a result, we can get the value of every `A[i] - A[0]`. We set A[0] to the number '0', and get the values of array A.

```python
(n, m) = map(int, raw_input().split())

mat = [map(int, raw_input().split()) for i in xrange(n)]

mod = -1
diffs = [0 for i in xrange(m)]

for i in xrange(1, m):
    diff = set([
        mat[j][i] - mat[j][0] for j in xrange(n)
    ])

    if len(diff) == 1:
        diffs[i] = list(diff)[0]
        continue

    if len(diff) != 2:
        print 'NO'
        exit(0)

    a, b = diff

    if mod == -1:
        mod = abs(a - b)
    elif mod != abs(a -b):
        print 'NO'
        exit(0)

    diffs[i] = max(a, b)

As = [0 for i in xrange(n)]
Bs = [0] + diffs[1:]

Bs = map(lambda x: x - min(Bs), Bs)

for i in xrange(n):
    As[i] = mat[i][0] - Bs[0]

if mod == -1:
    mod = (10 ** 18) - 1

for i in xrange(n):
    for j in xrange(m):
        if mat[i][j] != (As[i] + Bs[j]) % mod:
            print 'NO'
            exit(0)

print 'YES'
print mod
print ' '.join(map(str, As))
print ' '.join(map(str, Bs))
```

## E. Pretty Song

Math & Thinkin' in reverse

It's hard to get the answer by brute force because the scope of this problem is too large.

Try to think in reverse. It's hard to calculate all the value of the substrings, but why don't we find a way to get the value that every vowel contributes to the final result?

For example, string "AAA". The first "A" will add `1 + 1/2 + 1/3` to the final result. And the second "A", `1 + 1/2 + 1/2 + 1/3`. And the last "A", `1 + 1/2 + 1/3`.

We can make a table here for a 4-length string.

![Alt text][2]

We can easily find the pattern here. (Of course we can prove it.) And the code is right here.

(But you can always find a [harder way][1] to sovle it. LOL. But I have to say that **pypy** is awesome!)

```python
# pypy: 171ms
# python2: 467ms
VOWELS = list('AEIOUY')
N = 500010

ds = [0 for i in xrange(N)]

for i in xrange(1, N):
    ds[i] = ds[i - 1] + 1.0 / i

S = raw_input()
n = len(S)
d = 0
ans = 0

for i, c in enumerate(S):
    d += ds[n - i] - ds[i]
    if c in VOWELS:
        ans += d

print ans
```

pypy is about 3~5 times faster than the original python interpreter, and this is the very useful tool to help us with the algorithm problems.

## F. Progress Monitoring

DP

This problem is about the pre-order traversal with a tree. There are multiple situations of the output string given in the problem.

```

  a    | b c d |         | e f g h i j |
  ^        ^                    ^
father  children   siblings & siblings children
```
or 

```

  a    | b c d e f |         | g h i j |
  ^          ^                    ^
father   children    siblings & siblings children
```

But be aware, if `x < a`, `a` and `x` can't be siblings. 

`dp[i][j]` stands for the number of permutations of the subtree. whose pre-order traversal is right match the `s[i...j]`, the substring of the given traversal path.

```python
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <algorithm>
#include <vector>

using namespace std;

#define print(x) cout << x << endl
#define input(x) cin >> x

typedef long long llint;

const llint MOD = 1000000000 + 7;
const int SIZE = 555;

llint dp[SIZE][SIZE];
int n;
vector<int> outvec;

void solve() {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j + i < n; j++) {
            int l = j, r = j + i;
            if (l == r) {
                dp[l][r] = 1;
                continue;
            }
            if (outvec[l + 1] > outvec[l]) {
                dp[l][r] += dp[l + 1][r]; // <l + 1 ... r> are siblings
                dp[l][r] %= MOD;
            }
            dp[l][r] += dp[l + 1][r]; // <l + 1 .. r> are child nodes
            dp[l][r] %= MOD;

            for (int k = l + 2; k <= r; k++) {
                if (outvec[k] > outvec[l]) {
                    llint child   = dp[l + 1][k - 1];
                    llint sibling = dp[k][r];
                    dp[l][r] = (dp[l][r] + child * sibling) % MOD;
                }
            }
        }
    }
}

int main() {
    int x;
    input(n);
    if (n == 1) {
        print(1);
        exit(0);
    }
    memset(dp, 0, sizeof(dp));
    for (int i = 0; i < n; i++) {
        input(x);
        outvec.push_back(x);
    }
    solve();
    print(dp[1][n - 1] % MOD);
    return 0;
}
```

[1]: http://codeforces.com/contest/509/submission/9862199
[2]: data:image/png;base64,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
