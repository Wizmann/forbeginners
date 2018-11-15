Date: 2015-04-25 00:54:08 
Title: Beauty-of-Programming 2015 Qualification Round Tutorial
Tags: algorithm, 算法, 题解, Microsoft
Slug: beauty-of-programming-2015-qualification-round

## A. 2月29日 (Feb. 29th)

### Description

Given a starting date and an ending date. Count how many Feb. 29th are between the given dates.

### Solution

The easiest way, of course, the brute force, which is quite simple with Python using the `datetime` lib.

However, it's not an effective way for the problem.

Let simplify the problem. "How many Feb. 29th from year A to year B?" Actually, it't not a hard one. But there is a pitfall. Loot at this.

```python
yearA = 2001
yearB = 2017

cnt = 0
cnt += (yearB - yearA) / 4
cnt -= (yearB - yearA) / 100
cnt += (yearB - yearA) + 400

print cnt
```

Seems OK, but a little bit weird, right? But, opps, it absolutely wrong.

For example,

```
2001 -> 2002 -> 2003 -> @2004@ -> 2005   (year = 5, lear_year = 1)
@2000@ -> 2001 -> 2002 -> 2003 -> @2004@ (year = 5, leap_year = 2)
```

The right way is using a `ceil` way to adjust yearA to the nearest greater leap year.

And then we deal with other details to make everything right.

```cpp
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <cmath>

using namespace std;

#define print(x) cout << x << endl
#define input(x) cin >> x 

typedef long long llint;

string months[] = {"January", 
        "February", 
        "March", 
        "April", 
        "May", 
        "June", 
        "July", 
        "August", 
        "September", 
        "October", 
        "November" , 
        "December"};
        
struct Date {
    llint yy, mm, dd;
    
    Date() {}
    Date(llint iyy, string imm, llint idd): yy(iyy), dd(idd) {
        for (int i = 0; i < 12; i++) {
            if (imm == months[i]) {
                mm = i + 1;
            }
        }
    }
};

llint year_diff(llint a, llint b) {
    if (a >= b) {
        return 0;
    }
    llint ans = 0;
    llint aa = (a + 3) / 4 * 4;
    llint bb = (b / 4) * 4;
    if (aa <= bb) {
        ans += (bb - aa) / 4 + 1;
    }
    
    aa = (a + 99) / 100 * 100;
    bb = (b / 100) * 100;
    
    if (aa <= bb) {
        ans -= (bb - aa) / 100 + 1;
    }
    
    aa = (a + 399) / 400 * 400;
    bb = (b / 400) * 400;
    if (aa <= bb) {
        ans += (bb - aa) / 400 + 1;
    }
    
    return ans;
}

bool is_leap(const Date& d) {
    return (d.yy % 4 == 0 && d.yy % 100 != 0) || (d.yy % 400 == 0);
}

llint solve(const Date& da, const Date& db) {
    llint ans = 0;
    ans += year_diff(da.yy + 1, db.yy - 1);
    
    if (da.yy < db.yy && is_leap(da) && da.mm < 3) {
        ans++;
    }
    
    if (da.yy < db.yy && is_leap(db) && (db.mm >= 3 || (db.mm == 2 && db.dd == 29))) {
        ans++;
    }
    
    if (da.yy == db.yy && is_leap(da) && da.mm < 3 && (db.mm >= 3 || (db.mm == 2 && db.dd == 29))) {
        ans++;
    }
    
    return ans;
}

int main() {
    int T;
    string mm, temp;
    int yy, dd, cas = 1;
    input(T);
    while (T--) {
        Date a, b;
        input(mm >> dd >> temp >> yy);
        a = Date(yy, mm, dd);
        input(mm >> dd >> temp >> yy);
        b = Date(yy, mm, dd);
        printf("Case #%d: %lld\n", cas++, solve(a, b));
    }
    return 0;
}
```

## B. 回文字符序列(Palindrome Subsequences)

### Description

Given a string, try to count how many subsequences there are palindromes.

For example, for the string "aba", the palindrome subsequences are: "a", "a", "aa", "b", "aba".

### Solution

Let's simplify the problem. (Of course, the simple one always comes the first.)

> How many substring there are palindromes?

This one is a more populare problem which can be solved with an `O(n^2)` DP algorithm.

```
dp[i][j] = (str[i] == str[j] && dp[i - 1][j - 1])
```

If `dp[i][j]` equals to one, it means that the substring `str[i:j + 1]` is a palindrome, vice versa.

For this problem, things are quite similar. If there are some palindrome subsequences at `str[i - 1: j]`, and at the same time `str[i] == str[j]`, that is, there must be one or more palindrome subsequences at `str[i:j + 1]` and these subsequences contain `str[i]` and `str[j]`.

That is the basic idea of the problem, and the DP formula is like this. You can consider why.

```python
if (str[i] != str[j]):
    dp[i][j] = dp[i][j - 1] + dp[i + 1][j] - dp[i + 1][j - 1]
else:
    dp[i][j] = dp[i][j - 1] + dp[i + 1][j] + 1
```

Be ware, the result need to be module by 100007. As we have minus in the DP formula, don't forget there are possibility that `dp[i][j] < 0`.

```cpp
// This is actually the solution for HDU 4632, which is similar to this problem.
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

const int SIZE = 1234;
const int MOD = 10007;

int n;
int dp[SIZE][SIZE];
string word;

int do_mod(int value) {
    return ((value % MOD) + MOD) % MOD;
}

int solve() {
    memset(dp, 0, sizeof(dp));
    for (int i = 0; i < n; i++) {
        dp[i][i] = 1;
    }
    for (int i = 1; i < n; i++) {
        for (int j = 0; i + j < n; j++) {
            int l = j;
            int r = i + j;
            if (word[l] == word[r]) {
                dp[l][r] = do_mod(
                    dp[l][r - 1] + dp[l + 1][r] + 1);
            } else {
                dp[l][r] = do_mod(
                    dp[l][r - 1] + dp[l + 1][r] - dp[l + 1][r - 1]);
            }
        }
    }
    return dp[0][n - 1];
}

int main() {
    int T, cas = 1;
    input(T);
    while (T--) {
        input(word);
        n = word.size();
        printf("Case %d: %d\n", cas++, solve() % MOD);
    }
    return 0;
}
```

## C.基站选址(Base Station Locationing)

### Description

Given a N × M grid which contain A user and B communications companies, and **one single** base station.

The cost of communication between users and base station is defined as the square of the Euclidean distance.

The cost for the companies to maintain the base station is defined as the minimal Manhattan distance between the station and all the communications companies.

### Solution

All we have to do is to find the minimal distance with that formula.

![Alt text](https://github.com/Wizmann/assets/raw/master/wizmann-pic/611be1334aab00954c56e31af0bc0cc4)

It's easy to see that we can deal with the x-axis and y-axis separately

![Alt text](https://github.com/Wizmann/assets/raw/master/wizmann-pic/2bffa65945d689235e602935d782256b).

We can learn something from the quadratic equation like formula. And of course, we minimum value is near `sum(xa[i]) / A`. This is same with the y-axis. As a result, we can check the grid near `<sum(xa[i]) / A, sum(ya[i]) / A>`, to see if there is a minimum cost for the communication.

I don't want to write the code here because it's easy if you know the basis of the algorithm and it's too late now. I'm gonna to have a diet pepsi, and say good night for all you guys.

Lazy guy, indeed. :)
