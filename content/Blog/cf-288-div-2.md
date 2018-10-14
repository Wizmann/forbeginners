Date: 2015-02-16 21:16:30 
Title: Codeforces Round #288 (Div. 2) 
Tags: codeforces, algorithm, 算法, 题解
Slug: cf-288-div-2

## A. Pasha and Pixels

Brute force.

There are multiple ways to form a 2*2 square at one single step.

![Alt text](http://wizmann-pic.qiniudn.com/6fb53c51539b47559cf0d122a832cf63)

So at every step, we have to check the neighbours of pixel that is colored black.

```cpp
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <vector>

using namespace std;

#define print(x) cout << x << endl
#define input(x) cin >> x

const int SIZE = 1024 + 123;

const int mx[] = {0, 1, 0, 1};
const int my[] = {0, 0, 1, 1};
const int MOVE = 4;

int mp[SIZE][SIZE];
int n, m, k;

bool isBlackBlock(int y, int x) {
    int cnt = 0;
    for (int i = 0; i < MOVE; i++) {
        int ny = y + my[i];
        int nx = x + mx[i];

        if (ny >= 0 && ny < n
                && nx >= 0 && nx < m
                && mp[ny][nx]) {
            cnt++;
        }
    }
    return cnt == MOVE;
}


int main() {
    int y, x;
    input(n >> m >> k);
    memset(mp, 0, sizeof(mp));
    int ans = 0;
    for (int i = 0; i < k; i++) {
        input(y >> x);
        x--; y--;
        mp[y][x] = 1;
        bool flag = false;
        for (int j = 0; j < MOVE; j++) {
            flag |= isBlackBlock(y - my[j], x - mx[j]);
        }
        if (flag) {
            ans = i + 1;
            break;
        }
    }
    print(ans);
    return 0;
}
```

## B. Anton and currency you all know

At first, you have to understand the questions accurately.

The exchange rate is **an odd number**. And your mission is swap one digit with another, to make it the maximum even number.

Because if the exchange rate is an even number, it will lead to a more sophisticated problem.

The intuitive thought is that we can swap the hightest even digit with the last digit. However, for this case "92291", you may swap the second digit "2" and the last digit "1". But "91292" is not the largest number, "92192" is.

So, ther are two scenario. First is the final answer is greater than the ordinary one. Just find out the **first even digit that is less than the last digit**. Second is the final answer is less than the given one. If we want to make it the largest one, we have to find the **lowest even digit and then swap**.

We can make it by loop twice. But there is a way to find the final answer in one single iteration.

```cpp
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>

using namespace std;

#define print(x) cout << x << endl
#define input(x) cin >> x

const int SIZE = 123456;

char number[SIZE];

int main() {
    scanf("%s", number);
    int len = strlen(number);
    int p = -1, q = number[len - 1] - '0';
    
    for (int i = len - 2; i >= 0; i--) {
        int u = number[i] - '0';
        if (u % 2) {
            continue;
        }
        if (p == -1 || q > u) {
            p = i;
        }
    }

    if (p == -1) {
        print(-1);
    } else {
        swap(number[p], number[len - 1]);
        print(number);
    }

    return 0;
}
```

## C. Anya and Ghosts

The background of this problem is quite twisted.

First of all, we have to find out in which scenario there is no way to defence against the ghost.

![Alt text](http://wizmann-pic.qiniudn.com/833368d068c6dc956b62d9babf01c3b6)

It's easy to find out in that diagram above that if the duration of the candle is less than the number of candles which is needed.

So, before the ghost comes, we have to light up the candles. If we want to have K candles in one second, we have to light it up at second (T - 1) (T - 2) ... (T - K).

```python
import sys

(m, t, r) = map(int, raw_input().split())
ghosts = map(int, raw_input().split())

# impossible
if t < r:
    print -1
    sys.exit(0)

ans = 0
candles = [-1 for i in xrange(r)]

for ghost in ghosts:
    delay = 0
    for i in xrange(r):
        if candles[i] < ghost:
            candles[i] = ghost + t - 1 - delay
            delay += 1
            ans += 1

print ans
```

## D. Tanya and Password

Tanya cut the password into three-letter continuous substrings. Our mission is to re-assemble these substrings.

For example,

```
Password: fuckme
Substrings: fuc, uck, ckm, kme
```

It's not hard to find out that the problem is not about the "string" but the "graph". But how to convert the string and substrings into a graph.

At the every beginning, we regard the substrings as vertexes, every two substrings which could be connected has an edge between them.


![Alt text](http://wizmann-pic.qiniudn.com/bbc690924ece17dde46fd5d23188bf5d)

In this scenario, all we have to do is find a path that visit all the vertexes. This path is called **Hamilton path**. The algorithm to find a hamilton path in a graph is quite slow with O(2 ** N) time complexity. We have to find another way.

Similar to hamilton path, the eular path is a path that visit all the edges of the graph. And this inspires us to make the strings to another graph, and the eular path will be the final answer with the complete password.

![Alt text](http://wizmann-pic.qiniudn.com/bd69ddd562d6b4b4cde4e3a461a8706e)

```cpp
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <algorithm>
#include <vector>
#include <string>
#include <set>

using namespace std;

#define print(x) cout << x << endl
#define input(x) cin >> x
#define err(x)   cerr << x << endl

const int BASE = 64;
const int SIZE = 64 * 64;

int g[SIZE][SIZE];
int iter[SIZE];
int father[SIZE];
int indeg[SIZE], outdeg[SIZE];
int n;
vector<int> ans;

int get_value(char c) {
    if ('a' <= c && c <= 'z') {
        return c - 'a';
    }
    if ('A' <= c && c <= 'Z') {
        return c - 'A' + 26;
    }
    if ('0' <= c && c <= '9') {
        return c - '0' + 52;
    }
    err("get_value_err:" << ' ' << c);
    return -1;
}

int get_char(int v) {
    if (0 <= v && v <= 25) {
        return 'a' + v;
    }
    if (26 <= v && v <= 51) {
        return 'A' + v - 26;
    }
    if (52 <= v && v <= 61) {
        return '0' + v - 52;
    }
    err("get_char_err" << ' ' << v);
    return -1;
}

int get_id(char a, char b) {
    int ia = get_value(a);
    int ib = get_value(b);
    return ia * BASE + ib;
}

void add_edge(const string& node_str) {
    int a = get_id(node_str[0], node_str[1]);
    int b = get_id(node_str[1], node_str[2]);
    g[a][b]++;
    outdeg[a]++;
    indeg[b]++;
}

int get_father(int x) {
    if (father[x] == x) {
        return x;
    }
    return father[x] = get_father(father[x]);
}

bool is_connected() {
    for (int i = 0; i < SIZE; i++) {
        father[i] = i;
    }
    
    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            if (g[i][j]) {
                father[get_father(i)] = get_father(j);
            }
        }
    }
    set<int> st;
    for (int i = 0; i < SIZE; i++) {
        if (!indeg[i] && !outdeg[i]) {
            continue;
        }
        st.insert(get_father(i));
    }
    return st.size() == 1U;
}

int get_start_point() {
    if (!is_connected()) {
        return -1;
    }
    int a = 0;
    int b = 0;
    int c = 0;
    int res = -1;
    for (int i = 0; i < SIZE; i++) {
        if (outdeg[i] == indeg[i] + 1) {
            a++;
            res = i;
        }
        if (outdeg[i] == indeg[i] - 1) {
            c++;
        }
        if (outdeg[i] == indeg[i]) {
            b++;
        }
    }
    if (a == 1 && b == SIZE - 2 && c == 1) {
        return res;
    }
    if (a == 0 && b == SIZE) {
        return 0;
    }
    return -1;
}

void dfs(int p) {
    for (int i = iter[p]; i < SIZE; i++) {
        if (g[p][i]) {
            g[p][i]--;
            dfs(i);
        }
        iter[p]++;
    }
    ans.push_back(p);
}

void show_path(int st) {
    string res;

    for (auto u: ans) {
        u %= BASE;
        char c = get_char(u);
        res += c;
    }
    char a = get_char(st / BASE);
    res += a;
    reverse(res.begin(), res.end());
    print(res);
}

int main() {
    input(n);
    string node_str;
    for (int i = 0; i < n; i++) {
        input(node_str);
        add_edge(node_str);
    }
    int u = get_start_point();
    if (u == -1) {
        print("NO");
    } else {
        print("YES");
        if (u == 0) {
            u = get_id(node_str[0], node_str[1]);
        }
        dfs(u);
        show_path(u);
    }
    return 0;
}
```

## E. Arthur and Brackets

DP + Greedy

For this problem, be ware that the position of the right bracket is not the absolute position but the relative position. And according to the common sense, there will only be complete brackets between one left bracket and one right bracket.

For example,

```
RIGHT: *(* ()(()) *)*
WRONG: *(* ((((() *)*
```

So, it's OK to close the bracket if possible. And this is the key to solve to problem.

```python
n = int(raw_input())
brackets = [tuple(map(int, raw_input().split())) for i in xrange(n)]

res = ''
ptr = 0

INF = 0xcafebabe
st = []

for (l, r) in brackets:
    res += '('
    st.append((ptr + l, ptr + r))
    ptr += 1
    while st:
        (pre_l, pre_r) = st[-1]
        if pre_l <= ptr <= pre_r:
            res += ')'
            ptr += 1
            st.pop()
        else:
            break

if st:
    print 'IMPOSSIBLE'
else:
    print res
```
