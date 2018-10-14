Date: 2015-02-18 00:30:24 
Title: Codeforces Round #290 (Div. 2) Tutorial
Tags: codeforces, algorithm
Slug: cf-290-div-2

## A. Fox And Snake

Implementation

```python
(n, m) = map(int, raw_input().split())

res = []

for i in xrange(n):
    if i % 2 == 0:
        res.append('#' * m)
    elif (i / 2) % 2 == 0:
        res.append('.' * (m - 1) + '#')
    else:
        res.append('#' + '.' * (m - 1))

for line in res:
    print line
```

## B. Fox And Two Dots

DFS

```
AAAA
ABCA
AAAA
```

We start at arbitrary point, and traverse the neighbour point with the same color to see if there is a circle.

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

const int SIZE = 54;

const int mx[] = {0, 1, 0, -1};
const int my[] = {-1, 0, 1, 0};

int n, m;
char g[SIZE][SIZE];
char visit[SIZE][SIZE];

bool do_dfs(int y, int x, char c, int dir) {
    if (visit[y][x]) {
        return true;
    }
    visit[y][x] = 1;
    for (int i = 0; i < 4; i++) {
        int ny = y + my[i];
        int nx = x + mx[i];
        if (nx < 0 || nx >= m 
                || ny < 0 || ny >= n 
                || g[ny][nx] != c
                || (dir != -1 && i == (dir + 2) % 4)) {
            continue;
        }
        if (do_dfs(ny, nx, c, i)) {
            return true;
        }
    }
    return false;
}

bool dfs(int y, int x) {
    char c = g[y][x];
    return do_dfs(y, x, c, -1);
}

int main() {
    input(n >> m);
    memset(g, 0, sizeof(g));
    memset(visit, 0, sizeof(visit));

    for (int i = 0; i < n; i++) {
        input(g[i]);
    }
    try {
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                if (!visit[i][j]) {
                    bool res = dfs(i, j);
                    if (res) {
                        print("Yes");
                        throw "Got it";
                    }
                }
            }
        }
        print("No");
    } catch (...) {
        // pass
    }
    return 0;
}
```

## C. Fox And Names

Topsort

This is a classic interview problem. We can find the relationship between two letters from the given name list.

But in this instance, there is no possible lexical order because the name list is invalid.

```
aaa
aa
a
```

So the algorithm can be describe in this way:

1. If the name list is invalid, there is no solution.
2. Try to find the order of the letters.
3. Topsort
4. If topsort is success, print out the new lexical order of the name list. If failed, there is no solution.


```cpp
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <algorithm>
#include <queue>

using namespace std;

#define print(x) cout << x << endl
#define input(x) cin >> x

const int SIZE = 26;

vector<string> names;
vector<int> g[SIZE];
vector<int> res;
int n;
int in[SIZE];

bool makeG() {
    for (int i = 1; i < n; i++) {
        const string& pre = names[i - 1];
        const string& now = names[i];
        
        int len = min(pre.size(), now.size());
        
        if (pre.size() > now.size() && pre.substr(0, len) == now) {
            return false;
        }

        for (int j = 0; j < len; j++) {
            if (pre[j] == now[j]) {
                continue;
            }
            int a = pre[j] - 'a';
            int b = now[j] - 'a';
            g[a].push_back(b);
            in[b]++;
            break;
        }
    }
    return true;
}

bool top_sort() {
    queue<int> q;
    int cnt = 0;
    for (int i = 0; i < SIZE; i++) {
        if (in[i] == 0) {
            q.push(i);
            cnt++;
        }
    }
    while (!q.empty()) {
        int now = q.front();
        q.pop();
        res.push_back(now);
        for (auto next: g[now]) {
            in[next]--;
            if (in[next] == 0) {
                q.push(next);
                cnt++;
            }
        }
    }
    return cnt == SIZE;
}

void print_res() {
    for (auto i: res) {
        printf("%c", 'a' + i);
    }
    puts("");
}

int main() {
    string name;

    input(n);
    memset(in, 0, sizeof(in));
    for (int i = 0; i < n; i++) {
        input(name);
        names.push_back(name);
    }

    if (makeG() && top_sort()) {
        print_res();
    } else {
        puts("Impossible");
    }
    return 0;
}
```

## D. Fox And Jumping

Extended Euclidean algorithm

As we might know, for every positive integer `x` and `y`:

```
ax + by = gcd(x, y)
```

Let's extend this theorem, for an array of positive integer `Xs`:

```
As * Xs = gcd(Xs)
```

(`As` is an array of constants, both positive and negative)

If `gcd(Xs)` equal to one, that is, every two number of the array is co-prime.

So, we can find a subarray that every two number is co-prime, and have the minimal cost.

As there are not too many factors in a single number, even the number here is as large as 10^9. The `gcd()` of the subarray won't have too many results, and could be stored in a single `unordered_map` here.

And,

> C++ Iterator Invalidation Rules (C++03)

> Associative containers

> [multi]{set,map}: all iterators and references unaffected

Here is the rule of C++ about the behavoir of the iterators when we try to add something into the map during the iteration. So we can just use one sigle map, and avoid the complexity of moving things between to containers.

```cpp
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <algorithm>
#include <vector>
#include <unordered_map>

using namespace std;

#define print(x) cout << x << endl
#define input(x) cin >> x

const int SIZE = 500;
const int INF = 0x3f3f3f3f;

int gcd(int a, int b) {
    if (a % b == 0) {
        return b;
    }
    return gcd(b, a % b);
}

struct Card {
    int step;
    int cost;
};

int n;

vector<Card> cards;

int main() {
    input(n);
    cards.resize(n);
    for (int i = 0; i < n; i++) {
        input(cards[i].step);
    }

    for (int i = 0; i < n; i++) {
        input(cards[i].cost);
    }

    unordered_map<int, int> mp;
    for (auto& card: cards) {
        if (mp.find(card.step) == mp.end()) {
            mp[card.step] = INF;
        }
        mp[card.step] = min(mp[card.step], card.cost);
    }

    for (int i = 0; i < n; i++) {
        int thres = mp.find(1) != mp.end()? mp[1]: INF;
        for (auto& p: mp) {
            auto step = p.first;
            auto cost = p.second;
            
            if (step != 1 && cost >= thres) {
                continue;
            }
            
            int g = gcd(step, cards[i].step);

            if (mp.find(g) == mp.end()) {
                mp[g] = INF;
            }
            
            if (g == step) {
                mp[g] = min(mp[g], cost);
            }

            mp[g] = min(mp[g], cost + cards[i].cost);
        }
    }

    if (mp.find(1) == mp.end()) {
        print("-1");
    } else {
        print(mp[1]);
    }

    return 0;
}
```

## E. Fox And Dinner

Max Flow Algorithm

As we know, every odd number must be connected to two even numbers. And, of course, one even number should be connected to two odd numbers.

We use the max flow algortihm. Every odd number have a path with 2 unit of flow to the **source** node, every even number have a path with 2 unit of flow to the **sink** node. And if the sum of one odd number and an even number is a prime, we connect them with a path with 1 unit of flow.

As the result, we have a undirected graph that every node have a degree of 2. It's easy to find out that is an **Euler circuit**. We find the circuit and print it out.

The problem is not easy as it seems. Harsh one, indeed. I used **Dinic** algorithm for the max flow. Actually, I don't like my code here.

```cpp
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <iostream>
#include <algorithm>
#include <vector>
#include <queue>
#include <stack>

using namespace std;

#define print(x) cout<<x<<endl
#define input(x) cin>>x

const int NODE = 200 + 19;
const int EDGE = NODE * NODE;
const int INF  = 0x3f3f3f3f;

struct node
{
    int st, end, flow, next;
    node(){}
    node(int ist, int iend, int iflow, int inext):
            st(ist), end(iend), flow(iflow), next(inext) {}
};

int n;
node edge[EDGE];
int head[NODE];
int ind;
int source,sink;
vector<int> nums;
vector<int> cnc[NODE];
char visit[NODE];

void addEdge(int s,int e,int f)
{
    edge[ind]=node(s,e,f,head[s]);
    head[s] = ind++;
    
    edge[ind]=node(e,s,0,head[e]);
    head[e] = ind++;
}

namespace dinic
{
    int level[NODE],curhead[NODE],Que[NODE];
    int estack[4*NODE+4*EDGE],estop;
    
    int BFS()
    {
        memset(level,-1,sizeof(level));
        Que[0]=source;
        level[source]=0;
        for(int fr=0,tail=1;fr!=tail;fr=(fr+1)%NODE)
        {
            int cur=Que[fr];
            for(int e=head[cur];e!=-1;e=edge[e].next)
            {
                int next=edge[e].end;
                if(edge[e].flow && level[next] == -1)
                {
                    Que[tail]=next;
                    level[next]=level[cur]+1;
                    tail=(tail+1)%NODE;
                }
            }
        }
        return level[sink]!=-1;
    }
    
    int DFS()
    {
        int indptr,minf,e;
        int res=0;
        int cur=source;                                                   
        estop=0;
        memcpy(curhead,head,sizeof(head));  
        while(estop>=0)
        {            
            if(cur==sink)
            {                                      
                minf=INF;
                for(int i=estop-1;i>=0;i--)
                {
                    e=estack[i];
                    if(edge[e].flow<=minf)
                    {
                        minf=edge[e].flow;
                        indptr=i;
                    }
                }
                res+=minf;                                   

                for(int i=estop-1;i>=0;i--)
                {               
                    e=estack[i];
                    edge[e].flow-=minf;
                    edge[e^1].flow+=minf;
                }
                estop=indptr;                                    
                cur=edge[estack[estop]].st;          
            }
            for(e=curhead[cur];e!=-1;e=edge[e].next)
            {  
                curhead[cur]=e;
                int next=edge[e].end;
                if(edge[e].flow && level[next]==level[cur]+1)
                {
                    estack[estop++]=e;
                    cur=next;
                    break;
                }
            }
            if(e==-1)
            {                                           
                estop--;
                level[cur]=-2;                                    
                cur=edge[estack[estop]].st;               
            }
        }
        return res;
    }
}

void init()
{
    ind=0;
    memset(head,-1,sizeof(head));
    memset(visit, 0, sizeof(visit));
}

void dfs(int p, vector<int>& res) {
    res.push_back(p);
    visit[p] = 1;
    for (auto& u: cnc[p]) {
        if (visit[u]) {
            continue;
        }
        dfs(u, res);
    }
}
        
void show_res() {
    for (int i = 0; i < EDGE; i++) {
        if (edge[i].flow == 0) {
            int a = edge[i].st;
            int b = edge[i].end;
            
            if (a == source || b == source || a == sink || b == sink) {
                continue;
            }
            
            if (nums[a - 1] % 2 == 1 && nums[b - 1] % 2 == 0) {
                cnc[a].push_back(b);
                cnc[b].push_back(a);
            }
        }
    }
    /*
    for (int i = 1; i <= n; i++) {
        printf("%d -> ", i);
        for (auto& item: cnc[i]) {
            printf("%d ", item);
        }
        puts("");
    }
    puts("---");
    */
    vector<vector<int> > res;
    for (int i = 1; i <= n; i++) {
        if (visit[i]) {
            continue;
        }
        vector<int> tmp;
        dfs(i, tmp);
        res.push_back(tmp);
    }
    print(res.size());
    for (const auto& vec: res) {
        printf("%d", (int)vec.size());
        for (const auto& i: vec) {
            printf(" %d", i);
        }
        puts("");
    }
}

bool isPrime(int u) {
    if (u % 2 == 0) {
        return false;
    }
    int v = sqrt(u) + 1;
    for (int i = 3; i <= v; i += 2) {
        if (u % i == 0) {
            return false;
        }
    }
    return true;
}

int main()
{
    freopen("E.txt", "r", stdin);
    int x;
    input(n);
    init();
    
    source = 0;
    sink = n + 1;
    
    for (int i = 1; i <= n; i++) {
        input(x);
        nums.push_back(x);
    }
    
    for (int i = 1; i <= n; i++) {
        if (nums[i - 1] % 2 == 0) {
            continue;
        }
        for (int j = 1; j <= n; j++) {
            if (nums[j - 1] % 2 != 0) {
                continue;
            }
            if (isPrime(nums[i - 1] + nums[j - 1])) {
                addEdge(i, j, 1);
            }
        }
    }
    
    for (int i = 1; i <= n; i++) {
        int u = nums[i - 1];
        if (u % 2 == 1) {
            addEdge(source, i, 2);
        } else {
            addEdge(i, sink, 2);
        }
    }

    int res = 0;
    while(dinic::BFS()) {
        res+=dinic::DFS();
    }
    
    if (res != n) {
        puts("Impossible");
    } else {
        show_res();
    }
    
    return 0;
}
```


