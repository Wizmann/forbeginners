Date: 2013-12-25 19:05
Title: Codeforces Round #221 (Div. 2)不完全不正确题解
Tags: codeforces, algorithm, 算法, 题解
Slug: cf-221-div-2

## A. Lever

水题，杠杆原理。

用``^``把字符串分割开。然后分别计算两边的重量即可。

```python
#Result: Dec 24, 2013 6:04:41 PM    Wizmann  A - Lever   Python 2   Accepted     312 ms  4200 KB
def calc(ss):
    res = 0
    p = 1
    for item in ss:
        if item != '=':
            t = int(item)
            res += t * p
        p += 1
    return res

s = raw_input()

(a, b) = s.split('^')

left = calc(a[::-1])
right = calc(b)

if left == right:
    print 'balance'
elif left > right:
    print 'left'
else:
    print 'right'
```

## B. I.O.U.

水题，算出每个人负债和贷出（这个词的现学的~）的绝对值差。

然后再求和除2。

```python
#Result: Dec 24, 2013 6:12:53 PM    Wizmann  B - I.O.U.  Python 2   Accepted     46 ms   0 KB
(n, m) = map(int, raw_input().split())
inv = [0 for i in xrange(n + 5)]
outv = [0 for i in xrange(n + 5)]

for i in xrange(m):
    (a, b, c) = map(int, raw_input().split())
    outv[a] += c
    inv[b] += c

res = 0
for i in xrange(n + 5):
    res += abs(inv[i] - outv[i])

while res % 2 != 0:
    #Trick，如果res % 2 != 0的话，我的算法就是完全错误的
    #此时返回TLE而不是WA
    pass

print res / 2
```

## C. Divisible by Seven

脑筋急转弯。

通过打表，我们可以看出。``permutation(1, 6, 8, 9) % 7 == [0 ... 6]``。

由此我们就可以看出，无论其它数字排列如何，只要在其后面补上``1, 6, 8, 9``的一个排列。就可以使其模7得0。

对于只有``1，6, 8, 9``和很多``0``的情况。我们就把``0``放在``1, 6，8，9``后面。

代码比较乱。不过思路很明显:)

```cpp
//Result: Dec 24, 2013 7:48:42 PM   Wizmann  C - Divisible by Seven  GNU C++    Accepted     140 ms  1000 KB
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <algorithm>
#include <vector>
#include <stack>

using namespace std;

#define print(x) cout << x << endl
#define input(x) cin >> x

const int SIZE = 1001000;

int g[12];
char buffer[SIZE];

int main()
{
    freopen("input.txt", "r", stdin);
    while (scanf("%s", buffer) != EOF) {
        memset(g, 0, sizeof(g));
        int all = 0;
        for (int i = 0; buffer[i]; i++) {
            int t = buffer[i] - '0';
            g[t]++;
            all++;
        }
        g[1]--;
        g[6]--;
        g[8]--;
        g[9]--;
        
        all -= 4;
        
        if (all == g[0]) {
            printf("1869");
            for (int i = 0; i < all; i++) {
                printf("0");
            }
            puts("");
        } else {
            int mod = 0;
            for (int i = 1; i <= 10; i++) {
                int ii = i % 10;
                for (int j = 0; j < g[ii]; j++) {
                    printf("%d", ii);
                    mod = mod * 10 + ii;
                    mod %= 7;
                }
            }
            mod *= 10000;
            mod %= 7;
            mod = (7 - mod)% 7;
            switch(mod) {
                case 0:
                    printf("1869");
                    break;
                case 1:
                    printf("6819");
                    break;
                case 2:
                    printf("6918");
                    break;
                case 3:
                    printf("6891");
                    break;
                case 4:
                    printf("8691");
                    break;
                case 5:
                    printf("1986");
                    break;
                case 6:
                    printf("8196");
                    break;
            }
            puts("");
        }
    }
    return 0;
}
```

## D. Maximum Submatrix 2

其实这题也应该是水题。

给你一个``0/1``矩阵，可以做行交换，让你求出交换后能获得的最大由``1``组成的子阵。

这个题和两个题很相似，一个是经典的``最大子阵和``问题，另一个是不太经典的``直方图中最大矩形``问题。

我们可以看出，因为只有行变换，所以对列上的``0/1``分布没有任何影响。于是我们可以处理出以某列为基准时，某行的最大子阵。

![子阵][1]

如图所示，我们计算到第二列的时候。可以处理出每一行的最大子阵。由于我们可以进行行变换，于是我们将每行的最大子阵进行排序。然后遍历求出当前的最大子阵，从而得出答案。

代码简单。不过有性能问题。没有充分使用cache，不过100+ms就过了，懒得优化了。

```cpp
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <algorithm>
#include <vector>
#include <stack>

using namespace std;

#define print(x) cout << x << endl
#define input(x) cin >> x

const int SIZE = 5120;

int g[SIZE][SIZE];
char buffer[SIZE];
int n, m;
stack<int> st;

int main()
{
    freopen("input.txt", "r", stdin);
    
    while (input(n >> m)) {
        memset(g, 0, sizeof(g));
        memset(buffer, 0, sizeof(buffer));
        st = stack<int>();

        for (int i = 0; i < n; i++) {
            scanf("%s", buffer);
            int p = 0;
            for (int j = m - 1; j >= 0; j--) {
                buffer[j] -= '0';
                if (buffer[j] == 1) {
                    p++;
                } else {
                    p = 0;
                }
                g[i][j] = p;
            }
        }

        int ans = 0;
        for (int i = 0; i < m; i++) {
            vector<int> vec;
            for (int j = 0; j < n; j++) {
                vec.push_back(g[j][i]);
            }
            sort(vec.begin(), vec.end());

            int t = 0;
            for (int j = 0; j < n; j++) {
                t = max(t, vec[j] * (n - j));
            }

            ans = max(ans, t);
        }
        print(ans);
    }
    return 0;
}
```

## E. Circling Round Treasures

赛后学习来的代码。状压DP。

题目描述超级复杂，其实在题目中已经暗示了做法。

不过以这个代码复杂程度，比赛时能做出来也是比较牛的人了。

不想赘述解法了，只说一个关键点：

> Let's draw a ray that starts from point p and does not intersect other points of the table (such ray must exist).

> Let's count the number of segments of the polyline that intersect the painted ray. If this number is odd, we assume that point p (and consequently, the table cell) lie inside the polyline (path). Otherwise, we assume that it lies outside.

题目中给出了判断一个宝藏是否在路径中的一个判断算法。即判断点是否在多边形中的经典射线法。

我们可以记录某一步是否在某个宝藏的``射线``上。而射线的方向则可以自定。代码中的射线方向是``+x``方向。如果某一条边经过了这条射线，则修改当前状态。

```cpp
//Result: Dec 25, 2013 2:22:27 PM   Wizmann  E - Circling Round Treasures    GNU C++    Accepted    31 ms   1400 KB
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <algorithm>
#include <stack>
#include <queue>
#include <vector>

using namespace std;

#define print(x) cout << x << endl
#define input(x) cin >> x

const int mx[] = {1, 0, -1, 0};
const int my[] = {0, 1, 0, -1};

const int SIZE = 30;
const int GOLD = 8;

struct point {
    int x, y;
    point(){}
    point(int ix, int iy): x(ix), y(iy){}
};

struct node {
    point p;
    int status;
    
    node(){}
    node(int ix, int iy, int istatus): p(ix, iy), status(istatus) {};
};

int n,m;
int gold, bomb;
char maze[SIZE][SIZE];
int status[SIZE][SIZE];
char visit[SIZE][SIZE][1 << GOLD];
int step[SIZE][SIZE][1 << GOLD];
int sum[1 << GOLD];
int v[SIZE];

point st;

void bfs()
{
    queue<node> q;
    visit[st.y][st.x][0] = 1;
    q.push(node(st.x, st.y, 0));
    
    while (!q.empty()) {
        node now = q.front();
        q.pop();
        int x = now.p.x, y = now.p.y, nowst = now.status;
        
        for (int i = 0; i < 4; i++) {
            int nx = x + mx[i], ny = y + my[i];
            
            if (nx < 0 || nx == m || 
                    ny < 0 || ny == n || 
                    maze[ny][nx] != '.') continue;
            
            int nst = nowst;
            
            if (my[i] == 1) nst ^= status[ny][nx];
            else if (my[i] == -1) nst ^= status[y][x];
            
            if (visit[ny][nx][nst]) {
                continue;
            }
            
            visit[ny][nx][nst] = 1;
            q.push(node(nx, ny, nst));
            
            step[ny][nx][nst] = step[y][x][nowst] + 1;
        }
    }
}

int main()
{
    freopen("input.txt", "r", stdin);
    input(n >> m);
    gold = bomb = 0;
    for (int i = 0; i < n; i++) {
        scanf("%s", maze[i]);
        for (int j = 0; j < m; j++) {
            if (maze[i][j] == 'S') {
                st = point(j, i);
                maze[i][j] = '.';
            } else if (isdigit(maze[i][j])) {
                gold++;
                int nr = maze[i][j] - '1';
                for (int k = j + 1; k < m; k++)
                    status[i][k] |= 1 << nr;
            }
        }
    }
    for (int i = 0; i < gold; i++) {
        input(v[i]);
    }
    for (int i = 0; i < (1 << gold); i++) {
        for (int j = 0; j < gold; j++) {
            if (i & (1 << j)) sum[i] += v[j];
        }
    }
    
    bomb = gold;
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            if (maze[i][j] == 'B') {
                for (int k = j + 1; k < m; k++) {
                    status[i][k] |= 1 << bomb;
                }
                bomb++;
            }
        }
    }
    bfs();
    int ans = 0;
    for (int i = 0; i < (1 << gold); i++) {
        if (visit[st.y][st.x][i]) {
            ans = max(ans, sum[i] - step[st.y][st.x][i]);
        }
    }
    print(ans);
    return 0;
}
```
## 最后，炫耀一下

![rank][2]

[1]: http://wizmann-tk-pic.u.qiniudn.com/blog-cf221-div2-d.png
[2]: http://wizmann-tk-pic.u.qiniudn.com/blog-cf221-div2-rank.png