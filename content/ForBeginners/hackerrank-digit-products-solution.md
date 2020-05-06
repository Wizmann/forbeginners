Date: 2020-03-21
Title: [HackerRank] Digit Products - Solution
Tags: algorithm, hackerrank, solution
Slug: hackerrank-digit-products-solution

> 最近实在没什么可写的，只好写个题解来水一下。

## Description

Link: [Click me!][1]

We define a function `D(x)` which equals to the digit products of an integer of base 10.

For example:

```
D(0) == 0
D(123) == 1 * 2 * 3 == 6
D(234) == 2 * 3 * 4 == 24
D(104) == 1 * 0 * 4 == 0
```

Given the range `[A, B]`, and we want to know how many numbers `x` in the range satisfies `D(x) == K`.

Data constraints:

* T <= 10000
* 1 <= A <= B <= 10^100
* 1 <= K <= 10^18

## Solution

Because the range could be very large, it means the brute-force way is not feasible.

We mark the number of `D(x) == K` in range `[A, B]` as `f(A, B)`. So it's easy to know that `f(A, B) = f(0, B) - f(0, A - 1)`. We can mark `f(0, A)` as `F(A)`.

So, the problem has turn into getting the value of `F(A)`. Here we use `A = 233` as an example. For those numbers in one digit (0~9) and two digits (10~99), we can arbitrary enumerate all the possible combination of digits to get the answer. 

But for the numbers with 3 digits, we have to make sure that the number we get is less or equal than `A`. And right after the higher digits is less than the higher digits of `A`, we can do the enumerating job. 

For example, if we have the prefix of "1xy", we can set digit `x` and `y` to any value, and the value of the number is definitely less than `A`. But if the prefix is "2xy", we have to make sure that `x <= 3`.

> This idea is coming from digit DP, if you doesn't familiar with it, please refer [link1][2] and [link2][3].

And the next step for make the enumerating more efficient. We divide this for 3 different parts:

1. for digits [5, 7, 9], we can put them anywhere we want
2. for digits [2, 3, 4, 6, 8, 9], they are the factors of 2 and 3
3. for any other digits left, we fill it with 1

For scenario 1, we can calculate the answer by the number of permutation formula. For scenario 2 and 3, we can use DFS. And the number of digits is at most 100 and the number of factor 2 and 3 could at most 60. It means we can pre-process all the reseult of the DFS to accerlate our code.

So, the code have different parts. And we'd better add tests for them to make sure it works as expected.

The first part is to find `A - 1`. As the number `A` is very large and can only be represent in string. We have to implement a function to do that job:

```cpp
// this code is a piece of trash, but it works anyway
string minus_one(std::string a) {
    if (a == "1") {
        return "0";
    }
    int n = a.size();
    for (int i = 0; i < n; i++) {
        a[i] -= '0';
    }
    int g = -1;
    for (int i = n - 1; i >= 0; i--) {
        int u = int(a[i]) + g;
        g = 0;
        if (u < 0) {
            u += 10;
            g = -1;
        }
        a[i] = u;
    }
    int l = 0;
    while (a[l] == 0) {
        l++;
    }

    string res;
    for (/* pass */; l < n; l++) {
        res += '0' + a[l];
    }
    // cout << res << endl;
    return res;
}

/* 
    assert(minus_one("100") == "99");
    assert(minus_one("10000") == "9999");
    assert(minus_one("10001") == "10000");
    assert(minus_one("36") == "35");
*/
```

The second part is to enumerate the valid combination of digits:

```cpp
// pre-process this at the very begining of our code
llint DFS2[N][N][N];

// the factorial of x
llint AA[N];
// `1 / AA[x]`, calculated by "Fermat's little theorem"
llint INV[N];

llint A(int n, int m) {
    if (m > n) {
        return 0;
    }
    return AA[n] * INV[n - m] % MOD;
}

// n : the number of digits
// c2 : the number of factor 2
// c3 : the number of factor 3
llint dfs2(int n, int c2, int c3) {
    if (n < c2 / 3 + c3 / 2) {
        return 0;
    }
    assert(n >= 0);
    if (n == 0) {
        return (c2 == 0 && c3 == 0)? 1: 0;
    }
    if (c2 < 0 || c3 < 0) {
        return 0;
    }
    if (DFS2[n][c2][c3] != -1) {
        return DFS2[n][c2][c3];
    }
    llint res = 0;
    res = (res + dfs2(n - 1, c2, c3)) % MOD;        // 1
    res = (res + dfs2(n - 1, c2 - 1, c3)) % MOD;    // 2
    res = (res + dfs2(n - 1, c2, c3 - 1)) % MOD;    // 3
    res = (res + dfs2(n - 1, c2 - 2, c3)) % MOD;    // 4
    res = (res + dfs2(n - 1, c2 - 1, c3 - 1)) % MOD;// 6
    res = (res + dfs2(n - 1, c2 - 3, c3)) % MOD;    // 8
    res = (res + dfs2(n - 1, c2, c3 - 2)) % MOD;    // 9
    return DFS2[n][c2][c3] = res;
}

llint solve2(int n, int c2, int c3) {
    return DFS2[n][c2][c3];
}

// n : the number of digits
// k[i] : the number of factor `i`
llint calc(int n, const vector<int>& k) {
    // cout << "calc: " << n << ' ' << k << endl;
    int tot = accumulate(k.begin(), k.end(), 0);
    if (n == 0) {
        return tot == 0? 1: 0;
    }
    tot -= k[2] + k[3];
    
    // number of permutation formula
    llint res = A(n, tot);
    for (int i = 4; i < 10; i++) {
        res = (res * INV[k[i]]) % MOD; 
    }

    // dfs part
    if (n >= tot) {
        res = res * solve2(n - tot, k[2], k[3]) % MOD;
    }
    return res;
}

/*
    assert(calc(5, {0, 0, 2, 3, 0, 1, 0, 1, 0, 0}) == 300);
    assert(solve2(1, 1, 1) == 1);
*/
```

The third part is the "digit DP":

```cpp
vector<pair<int, int> > factors[10];

// digit DP
llint dfs(int cur, int n, const string& s, vector<int> k, bool lt) {
    if (cur == n) {
        auto ksum = accumulate(k.begin(), k.end(), 0);
        return ksum == 0? 1: 0;
    }
    llint res = 0;
    for (int i = 1; i <= 9; i++) {
        auto kk = k;
        bool flag = true;
        for (auto p : factors[i]) {
            kk[p.first] -= p.second;
            if (kk[p.first] < 0) {
                flag = false;
                break;
            }
        }
        if (!flag) {
            continue;
        }

        if (lt) {
            res = (res + calc(n - cur - 1, kk)) % MOD;
        } else {
            if (i == s[cur]) {
                res = (res + dfs(cur + 1, n, s, kk, false)) % MOD;
            } else if (i < s[cur]) {
                res = (res + calc(n - cur - 1, kk)) % MOD;
            }
        }
    }
    return res;
}

// s : the number of F(A)
// k : the number k described in the problem description
llint do_solve(string s, llint k) {
    if (s == "0") {
        return 0;
    }
    int n = s.size();
    for (int i = 0; i < n; i++) {
        s[i] -= '0';
    }
    vector<int> ks(10, 0);
    // factorization
    for (int i = 2; i < 10; i++) {
        while (k % i == 0) {
            ks[i]++;
            k /= i;
        }
    }
    if (k != 1) {
        return 0;
    }
    llint res = 0;
    for (int i = 1; i < n; i++) {
        res = (res + calc(n - i, ks)) % MOD;
    }
    res = (res + dfs(0, n, s, ks, false)) % MOD;

    return res;
}

/*
    assert(do_solve("666", 66) == 0); 
    assert(do_solve("666", 12) == 19); 
    assert(do_solve("66666", 12) == 125); 
    assert(do_solve("666666", 16) == 226); 
    assert(do_solve("66666666", 8) == 329); 
    assert(do_solve("20", 3) == 2); // 3, 13
    assert(do_solve("0", 3) == 0);
    assert(do_solve("9", 3) == 1);
    assert(solve("10", "10000000", 3780) == 15540);
    assert(solve("10", "1000000", 40) == 364);
*/
```

And the last step is to finish the pre-processing code.

```cpp
void init() {
    factors[2] = { { 2, 1 } };
    factors[3] = { { 3, 1 } };
    factors[4] = { { 2, 2 } };
    factors[5] = { { 5, 1 } };
    factors[6] = { { 2, 1 }, {3, 1} };
    factors[7] = { { 7, 1 } };
    factors[8] = { { 2, 3 } };
    factors[9] = { { 3, 2 } };

    AA[0] = 1;
    for (int i = 1; i < N; i++) {
        AA[i] = AA[i - 1] * i % MOD;
    }
    for (int i = 0; i < N; i++) {
        INV[i] = mypow(AA[i], MOD - 2);
    }

    memset(DFS2, -1, sizeof(DFS2));
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            for (int k = 0; k < N; k++) {
                DFS2[i][j][k] = dfs2(i, j, k);
            }
        }
    }
}
```

You can find the full code [here][4].

[1]: https://www.hackerrank.com/challenges/digit-products/problem
[2]: https://leetcode.com/problems/number-of-digit-one
[3]: https://leetcode.com/problems/numbers-at-most-n-given-digit-set
[4]: https://github.com/Wizmann/ACM-ICPC/tree/master/HackerRank/Mathematics/Combinatorics
