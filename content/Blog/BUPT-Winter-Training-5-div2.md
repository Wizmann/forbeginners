Date: 2019-02-19 23:28:00
Title: 2019 BUPT Winter Training #5 div2 题解
Tags: 题解, 水题
Slug: BUPT-Winter-Training-5-div2

[比赛链接][1]

## A - Friends (HDU 5305)

### 题意

给一张图有n个点，m条无向边。让你给每条边染成红色或黑色。使得每一个点相连的所有边中，红色边和黑色边的条数相等。

问有多少种染色方式。

### 解法

因为最多只有8个点，28条边。直接暴力搜索即可。只要代码别写（的像我一样）挫就行。

```cpp
#include <cstdio>
#include <cstring>
#include <algorithm>
#include <iostream>
#include <vector>

using namespace std;

#define print(x) cout << x << endl
#define input(x) cin >> x

class Solution {
public:
    Solution(int n_, int m_): n(n_), m(m_) {
        g = vector<vector<int> >(n);
        dp = vector<vector<int> >(n, vector<int>(n, -1));
        ans = 0;
        visit = vector<bool>(n, false);
    }

    void addEdge(int a, int b) {
        g[a].push_back(b);
        g[b].push_back(a);
    }

    int solve() {
        dfs(0);
        return ans;
    }

    void dfs(int cur) {
        int u = g[cur].size();
        visit[cur] = true;

        vector<int> bl = dp[cur];
        for (int i = 0; i < (1 << u); i++) {
            bool flag = true;
            int b = 0;
            for (int j = 0; j < u && flag; j++) {
                int p = g[cur][j];
                int v = (i & (1 << j))? 1: 0;
                b += (v == 0)? -1: 1;

                if (dp[cur][p] != -1 && dp[cur][p] != v) {
                    flag = false;
                    break;
                }
                dp[cur][p] = dp[p][cur] = v;
            }

            if (flag && b == 0) {
                flag = true;
                for (int j = 0; j < u; j++) {
                    int next = g[cur][j];
                    if (!visit[next]) {
                        dfs(next);
                        flag = false;
                        break;
                    }
                }

                for (int j = 0; j < n && flag; j++) {
                    if (j == cur) {
                        continue;
                    }
                    if (!visit[j]) {
                        dfs(j);
                        flag = false;
                        break;
                    }
                }

                if (flag) {
                    ans++;
                }
            }
            dp[cur] = bl;
        }
        visit[cur] = false;
    }
private:
    int n, m;
    int ans;
    vector<vector<int> > g;
    vector<vector<int> > dp;

    vector<bool> visit;
};

int main() {
    int T;
    input(T);
    while (T--) {
        int n, m;
        input(n >> m);

        Solution S(n, m);

        int a, b;
        for (int i = 0; i < m; i++) {
            scanf("%d%d", &a, &b);
            S.addEdge(a - 1, b - 1);
        }

        print(S.solve());
    }

    return 0;
}
```

## B - Solve this interesting problem (HDU 5323)

### 题意

假设在一颗区间为(0, n)的线段树上，有一个节点`[L, R]`。问这颗线段树是否存在，若存在，那么最小的n是多少。

### 解法

若想求n的值，我们必须将[L, R]向上推以找到根节点。

所以对于节点[L, R]，我们只有以下几种上推策略：

1. [L, R] => [L, R * 2 - L]
2. [L, R] => [L, R * 2 - L + 1]
3. [L, R] => [(L - 1) * 2 - R ,R]
4. [L, R] => [(L - 1) * 2 - R + 1, R]

由于每一次变化使得区间长度乘2，所以DFS的深度不会太深。再加上n的最大值不能超过2 * R（为什么？），直接暴搜就可以了。

> p.s. 这两题我写的代码都不太好，不要像我学。做题的时候要认真，三心二意没有训练效果。

```cpp
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <algorithm>
#include <vector>
#include <map>

using namespace std;

#define print(x) cout << x << endl
#define input(x) cin >> x

typedef long long llint;

const llint INF = 2e9 + 2;

llint solve(llint a, llint b) {
    if (a < 0 || a > b || b > INF) {
        return INF;
    }

    // print(a << ' ' << b);

    if (a == 0) {
        return b;
    }

    llint ans = INF;
    do
    {
        // (c, d)(a, b)
        llint d = a - 1;
        llint c = 2LL * d - b;
        if (c + 1 < 0) {
            return INF;
        }
        if (c != a) {
            ans = min(ans, solve(c, b));
        }
        if (c + 1 != a) {
            ans = min(ans, solve(c + 1, b));
        }
    } while(0);

    do
    {
        // (a, b)(c, d)
        llint c = b;
        llint d = 2LL * b - a;

        if (d <= INF && d != b) {
            ans = min(ans, solve(a, d));
        }
        if (d + 1 <= INF && d + 1 != b) {
            ans = min(ans, solve(a, d + 1));
        }
    } while(0);

    return ans;
}

int main() {
    int a, b;
    while (scanf("%d%d", &a, &b) != EOF) {
        llint ans = solve(a, b);
        if (ans >= INF) {
            ans = -1;
        }
        print(ans);
    }
    return 0;
}
```

## C - Crazy Bobo (HDU 5325)

### 题意

给你一颗树，树的节点的编号由1到n，并且每一个节点有权值w[i]，并且每个节点的权值各不相同。

求一颗子树，子树包含节点的编号为u[0...m]（按权值正序排列），使得从u[i] -> u[i + 1]的路径中，除u[i + 1]之外，不包含比u[i]的权值更大的节点。

问这个子树的最大大小。

### 解法

假设我们已经有一颗符合条件的子树，若要扩展这颗子树，需要将与子树相连的，并且大于子树最大的权值的点依次加入子树中。因为新加入的点的权值最大，所以它可以合法的到达子树的任意其它一点。但是这样做的时间复杂度大概是O(n * n * logn)。

假设我们又已经有一颗子树，且子树的最大权值为w。现在我们有两个与子树相边的节点a, b，并有w[a] < w[b]。那么我们的最优策略一定是先将a点加入子树。此时，可能又会引入新的相连节点。但是无论如何，b点也一定会被加入到子树中。这就意味着，我们在搜索过程中，加入点的顺序并不重要。该进子树的点，一个也跑不了。

所以，我们可以将树中的无向边转化为有向边，使得w[a] < w[b]，有边a <- b，意为如果a点在子树中，我们一定可以将b点加入子树。然后从每个点开始进行搜索，并通过记忆化进行加速。时间复杂度为O(n)。

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

const int SIZE = 512345;

int n;
vector<int> g[SIZE];
vector<int> score;
vector<bool> visited;
vector<int> dp;

int solve(int cur) {
    if (dp[cur] != -1) {
        return dp[cur];
    }

    int cnt = 1;

    for (auto next: g[cur]) {
        cnt += solve(next);
    }

    return dp[cur] = cnt;
}

int main() {
    while (scanf("%d", &n) != EOF) {
        dp = vector<int>(n, -1);
        score.resize(n);
        visited = vector<bool>(n, false);
        for (int i = 0; i < n; i++) {
            scanf("%d", &score[i]);
            g[i].clear();
        }

        int a, b;
        for (int i = 0; i < n - 1; i++) {
            scanf("%d%d", &a, &b);
            a--;
            b--;
            if (score[a] < score[b]) {
                g[a].push_back(b);
            }
            if (score[a] > score[b]) {
                g[b].push_back(a);
            }
        }

        int ans = 0;
        for (int i = 0; i < n; i++) {
            if (visited[i]) {
                continue;
            }

            ans = max(ans, solve(i));
        }
        printf("%d\n", ans);
    }

    return 0;
}
```

## D - MZL's chemistry (HDU 5347)

真不知道为啥多校训练会出这种题。三鹿牛奶喝多了吗？

本题略。

## E - Couple doubi (HDU 4861)

### 题意

博弈。给定n和一个质数p，规定`f(i) = sum(1^i, 2^i ... (p-1)^i) % p`（这里的`^`指乘方）。

现在有f(1), f(2) ... f(n)。A和B每个人每轮取走一个数，谁取到的数的和更大，谁就是赢家；如果取到的数之和相等，就是平局。

如果两个人都使用最优策略，问A是否能必胜。

### 解法

博弈的题目，很大概率能靠SG函数或者打表找规律来解决。

先打表看一下，规律非常简单，f(i)的值只有0或p - 1两种情况，所以计算一下f(i)里中的非0项的个数即可解决。

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

int main() {
    int a, b;
    while (scanf("%d%d", &a, &b) != EOF) {
        bool flag = (a / (b - 1)) % 2;
        if (flag) {
            puts("YES");
        } else {
            puts("NO");
        }
    }
    return 0;
}
```

## F - Inversion (HDU 4911)

### 题意

给你一个数组，然后允许最多k次swap相邻两个元素的操作。

问重排后的数组的最小逆序数。

### 解法

每一次swap操作最多可以减小1的逆序数。所以我们用归并排序求出数组的逆序数m，结果就是max(0, m - k)。

这里的坑是逆序数可能爆int。

```cpp
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <algorithm>
#include <vector>
#include <cassert>

using namespace std;

#define print(x) cout << x << endl
#define input(x) cin >> x

typedef long long llint;

const int SIZE = 123456;

llint inversion(int nums[], int l, int r) {
    if (r == l + 1) {
        return 0;
    }
    llint ans = 0;
    int n = r - l;

    int m = l + n / 2;

    ans += inversion(nums, l, m);
    ans += inversion(nums, m, r);

    vector<int> tmp;
    tmp.reserve(n);

    int pl = l;
    int pr = m;

    while (pl < m && pr < r) {
        if (nums[pl] <= nums[pr]) {
            tmp.push_back(nums[pl]);
            pl++;
        } else {
            ans += m - pl;
            tmp.push_back(nums[pr]);
            pr++;
        }
    }

    while (pl < m) {
        tmp.push_back(nums[pl]);
        pl++;
    }

    while (pr < r) {
        tmp.push_back(nums[pr]);
        pr++;
    }

    assert(tmp.size() == n);
    for (int i = 0; i < n; i++) {
        nums[l + i] = tmp[i];
    }
    
    return ans;
}

int A[SIZE];

int main() {
    int n, m;
    while (input(n >> m)) {
        for (int i = 0; i < n; i++) {
            scanf("%d", &A[i]);
        }
        llint res = max(0LL, inversion(A, 0, n) - m);
        printf("%lld\n", res);
    }

    return 0;
}
```


## G - The path (HDU 5385)

### 题意

给你一个有向图，d(i)表示从点1到点i的最短路，并且规定d(1)=0。

让你给图中的每一个点都赋一个值为[1, n]（闭区间）的边权，使得:

1. 存在一个x (2 <= x < n)，有d(1) < d(2) < d(3) ... < d(x) > d(x + 1) ... > d(n)
2. 或者d(1) < d(2) < d(3) ... d(n)

题目保证一定有解。

### 解法

因为题目保证一定有解，所以假设有一个子图，包含着点[1...l]和点[r...n]，并且符合题目中的条件。

那么与这个子图相邻的，一定会有点l+1或者点r+1，否则我们就不能扩展这个子图使其仍然符合条件。

此时，我们访问各个节点的顺序一定有

1. d(1) < d(2) < d(3) ...
2. d(n) < d(n - 1) < d(n - 2) ...

所以x是哪个节点并不重要，只要我们顺序的加入节点，并以加入节点的顺序作为d(i)值排序的顺序，就一定能符合条件。

我们使用dt[i]记录访问每一个点的顺序，那么点a到点b的边权就等于abs(dt[a] - dt[b])。

```cpp
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <algorithm>
#include <vector>
#include <set>
#include <cassert>

using namespace std;

#define print(x) cout << x << endl
#define input(x) cin >> x

const int SIZE = 312345;

int n, m;
vector<int> g[SIZE];
vector<pair<int, int> > edges;
vector<int> dt;

void solve() {
    int l = 1;
    int r = n;
    set<int> st;
    st.insert(1);

    int step = 0;
    while (!st.empty()) {
        int cur = -1;
        if (l == *st.begin()) {
            cur = l;
            l++;
            st.erase(st.begin());
        } else if (r == *st.rbegin()) {
            cur = r;
            r--;
            st.erase(--st.end());
        } else {
            assert(false);
        }
        
        dt[cur] = step++;

        for (int i = 0; i < g[cur].size(); i++) {
            int next = g[cur][i];
            if (l <= next && next <= r) {
                st.insert(next);
            }
        }
    }
}

int main() {
    int T;
    input(T);

    while (T--) {
        scanf("%d%d", &n, &m);

        for (int i = 0; i < SIZE; i++) {
            g[i].clear();
        }
        edges.clear();
        dt = vector<int>(n + 1, 0);

        int a, b;
        for (int i = 0; i < m; i++) {
            scanf("%d%d", &a, &b);
            g[a].push_back(b);
            edges.push_back({a, b});
        }
        
        solve();
        for (int i = 0; i < m; i++) {
            a = edges[i].first;
            b = edges[i].second;

            printf("%d\n", a != b? abs(dt[a] - dt[b]): n);
        }
    }

    return 0;
}
```

## H - Cake (HDU 5355)

## 题意

有m个人，分n个蛋糕。n个蛋糕的大小分别为1...n。

问怎么分能让这m个人分到的蛋糕大小总和一样。

1 <= n <= 1e5，2 <= m <= 10

## 题解

如果不看数据范围的话，这题就是个暴力搜索。但是由于n非常大，所以我们只能先试图缩小数据规模。

类似于等差数列求和的做法，我们可以使用头尾相加的做法构造k * m个相等的组合。然后再将[1 ... n - k * m]范围内的数字使用DFS搜索出一种排列组合，使其能平均分给m个人。

那么现在有两个问题：

1. 这种做法一定是正确的吗？
2. k * m的值取多少比较合适？

这两个问题我都没有得出答案。网上的题解以及官方题解都没有给出证明。所以我就只好假设这么做是可以的了。（分奴嘴脸）

根据试验，n - k * m > 2 * m的时候是可以AC的。

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

const int SIZE = 11;

vector<int> g[SIZE];
vector<llint> sum;
vector<bool> visit;
int n, m;

bool dfs(int cur, llint l, llint r, llint ave) {
    if (cur >= m) {
        return true;
    }

    r = min(r, ave - sum[cur]);

    for (int i = r; i >= l; i--) {
        if (visit[i]) {
            continue;
        }
        visit[i] = true;
        if (sum[cur] + i == ave) {
            sum[cur] += i;
            g[cur].push_back(i);
            return dfs(cur + 1, 1, n, ave);
        } else {
            sum[cur] += i;
            g[cur].push_back(i);

            bool res = dfs(cur, l, i - 1, ave);
            if (res) {
                return true;
            }

            sum[cur] -= i;
            g[cur].pop_back();
        }
        visit[i] = false;
    }
    return false;
}

bool solve() {
    llint tot = (1LL + n) * n / 2;
    if (tot % m != 0) {
        return false;
    }
    llint ave = tot / m;

    int u = n / 2 / m;
    if (u && n - (u * 2 * m) < 2 * m) {
        u--;
    }

    int l = n - u * m * 2 + 1;
    int r = n;
    for (int i = 0; i < m; i++) {
        for (int j = 0; j < u; j++) {
            g[i].push_back(l);
            g[i].push_back(r);
            sum[i] += l + r;
            l += 1;
            r -= 1;
        }
    }

    n = n - u * m * 2;
    visit = vector<bool>(n + 1, false);
    return dfs(0, 1, n, ave);
}

int main() {
    int T;
    input(T);
    while (T--) {
        scanf("%d%d", &n, &m);
        for (int i = 0; i < SIZE; i++) {
            g[i].clear();
        }
        sum = vector<llint>(m, 0);

        bool res = solve();
        if (res) {
            puts("YES");
            for (int i = 0; i < m; i++) {
                printf("%d", g[i].size());
                for (int j = 0; j < g[i].size(); j++) {
                    printf(" %d", g[i][j]);
                }
                puts("");
            }
        } else {
            puts("NO");
        }
    }
    return 0;
}
```


[1]: https://vjudge.net/contest/283313#overview
