Date: 2014-01-18 14:47
Title: Codeforces Round #223 (Div. 2) 不完全不正确题解
Tags: codeforces, algorithm, 算法, 题解
Slug: cf-223-div-2

由于大号已经进Div. 1了，所以接下来的几场Div. 2都是用小号做的。

等有实力切D题了，再去打一区。（弱

事情一直很多，所以题解落后了好久才发。

## A. Sereja and Dima

纯模拟，Python随便搞

```python
n = int(raw_input())
pokers = map(int, raw_input().split())

v = [0, 0]
p = 0

for i in xrange(n):
    if pokers[0] > pokers[-1]:
        v[p] += pokers[0]
        del pokers[0]
    else:
        v[p] += pokers[-1]
        del pokers[-1]
    p ^= 1

print v[0], v[1]
```

## B. Sereja and Stairs

题目要求实现一个数组，使前一半为递增，后一半为递减。

``a[1] < a[2] < ... < a[i - 1] < a[i] > a[i + 1] > ... > a[n -  1] > a[n]``

所以我们观察到，某一个数``x``在数组``a``中最多可以出现两次，其中一次在左边的序列，一次在右边的序列。

所以我们就对给出的数组``s``进行一次统计，找出每一个数出现的次数。

并分别讨论出现一次和出现两次的情况。

```python
SIZE = 5120

n = int(raw_input())
cards = map(int, raw_input().split())

cnt = [0 for i in xrange(SIZE)]

maxi = max(cards)
for item in cards:
    cnt[item] += 1

left = []
right = []
for i in xrange(maxi):
    if cnt[i] == 1:
        left.append(i)
    elif cnt[i] > 1:
        left.append(i)
        right.append(i)
left.sort()
right.sort(reverse=True)

ans = left + [maxi] + right
print len(ans)
print ' '.join(map(str, ans))
```

## C. Sereja and Prefixes

给定一个空序列``A``，然后这个序列上可以有两种操作。

一是``A.push_back(x)``，二是``A.push_back_batch(A[0]...A[i])``。

由于操作的次数是``10^5``，于是我们将序列``A``存成一个如下的形式。

``a -> b -> c -> copy(0...i) -> d -> copy(0 ... j)``

我们可以看出，如果询问的位置``pos``是一个数，则我们可以直接返回结果。如果询问的位置``pos``位于一个``copy``块里面，那么这个数一定会在``A[0...i]``中出现，则我们可以处理``pos`` -> ``pos'``，使``pos'``位于``A[0...i]``区间内。如此循环，直到``pos``是一个数为止。

然后这题用的算法貌似不是最快的，但是我觉得是最好理解的一种。

使用一个大根堆循环取``query``中最大的值，然后进行处理。

```cpp
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <algorithm>
#include <iostream>
#include <string>
#include <vector>
#include <queue>
#include <map>

using namespace std;

#define print(x) cout << x << endl
#define input(x) cin >> x

typedef long long llint;

const int SIZE = 100010;

struct node {
    llint st, end;
    llint prefix, rep;

    node(llint ist, llint pre, llint r) {
        st = ist;
        end = st + pre * r - 1;
        prefix = pre;
        rep = r;
    }

    node(llint ist, llint v) {
        st = end = ist;
        prefix = v;
        rep = -1;
    }

    node(){}

    bool is_value() {
        return rep == -1;
    }

    llint value() {
        return prefix;
    }
    
    bool contains(llint v) {
        return st <= v && v <= end;
    }
};

struct query {
    llint v, q;
    query(){}
    query(llint iv, llint iq): v(iv), q(iq){}
    
    friend bool operator < (const query& a, const query& b) {
        return a.v < b.v;
    }
};

priority_queue<query> pq;
int n, m;
vector<node> vec;
map<llint, llint> mp;
llint ask[SIZE];

void solve()
{
    int ptr = vec.size() - 1;
    while (!pq.empty()) {
        query nn = pq.top();
        llint now = nn.v;
        llint q = nn.q;
        pq.pop();

        while (!vec[ptr].contains(now)) {
            ptr--;
        }

        if (vec[ptr].is_value()) {
            mp[q] = vec[ptr].value();
        } else {
            llint delta = now - vec[ptr].st;
            delta %= vec[ptr].prefix;
            pq.push(query(delta + 1, q));
        }
    }
}

int main()
{
    llint a, b, c;
    input(n);
    llint st = 1;
    for (int i = 0; i < n; i++) {
        input(a);
        if (a == 1) {
            input(b);
            vec.push_back(node(st, b));
            st++;
        } else {
            input(b >> c);
            vec.push_back(node(st, b, c));
            st = (--vec.end()) -> end + 1;
        }
    }
    input(m);
    for (int i = 0; i < m; i++) {
        input(a);
        ask[i] = a;
        pq.push(query(a, a));
    }
    solve();
    for (int i = 0; i < m; i++) {
        if (i) printf(" ");
        printf("%lld", mp[ask[i]]);
    }
    puts("");

    return 0;
}
```

## D. Sereja and Tree

暴力乱搞，因为树的高度只有7000，所以怎么搞都大概能过。但是为什么做的人好少。

可能是题目表述的不太好吧。

```cpp
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <algorithm>
#include <iostream>
#include <string>
#include <vector>
#include <queue>
#include <map>
#include <stack>
#include <set>

using namespace std;

#define print(x) cout << x << endl
#define input(x) cin >> x

typedef long long llint;

const int SIZE = 7010;
const int LINE = 501000;

struct node {
    int l, r;
    int val;

    node(){}
    node(int il, int ir, int ival): l(il), r(ir), val(ival) {}
};

int n, m;
int ls[LINE], rs[LINE];
vector<node> ins[SIZE];

bool intersect(int a, int b, int c, int d) {
    if (b < c || a > d) return false;
    return true;
}

void init()
{
    ls[1] = 1;
    rs[1] = 2;
    int cnt, p = 3;
    for (int i = 2; i < LINE; i++) {
        if ((1 << cnt) == i) {
            cnt++;
            ls[i] = p++;
            rs[i] = p++;
        } else {
            ls[i] = -1;
            rs[i] = p++;
        }
    }
}

int query(int a, int b) {
    set<int> s;
    int ll = b, rr = b;
    for (int level = a; level <= n; level++) {
        for (int i = 0; i < (int)ins[level].size(); i++) {
            if (intersect(ll, rr, ins[level][i].l, ins[level][i].r)) {
                s.insert(ins[level][i].val);
            }
        }
        ll = ls[ll] == -1? rs[ll]: ls[ll];
        rr = rs[rr];
    }
    return s.size();
}

int main()
{
    int tp;
    int l, r;
    int a, b;
    init();
    input(n >> m);
    while (m--) {
        input(tp);
        if (tp == 1) {
            input(a >> l >> r >> b);
            ins[a].push_back(node(l, r, b));
        } else {
            input(a >> b);
            print(query(a, b));
        }
    }
    return 0;
}
```

## E. Sereja and Brackets

不出意外的又看错题了。。。\_(:з」∠)_

最长的括号区间居然是可以在中间删除一些括号的区间。这样题目就变成了一道比较简单的``离线化+树状数组``了。

代码如下：

```cpp
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <algorithm>
#include <iostream>
#include <string>
#include <vector>
#include <queue>
#include <map>
#include <stack>

using namespace std;

#define print(x) cout << x << endl
#define input(x) cin >> x

typedef long long llint;

const int SIZE = 1000100;

struct ppair {
    int l, r;
    int id;
    
    ppair(){}
    ppair(int il, int ir, int iid): l(il), r(ir), id(iid) {}
    
    friend bool operator < (const ppair& a, const ppair& b) {
        return a.r < b.r;
    }
};

inline int lowbit(int x)
{
    return x&(-x);
}

struct BIT//点更新，区间查询
{
    int baum[SIZE];
    inline void init()
    {
        memset(baum,0,sizeof(baum));
    }
    void add(int x,int val)
    {
        while(x<SIZE)
        {
            baum[x]+=val;
            x+=lowbit(x);
        }
    }
    int sum(int x)
    {
        int res=0;
        while(x>0)
        {
            res+=baum[x];
            x-=lowbit(x);
        }
        return res;
    }
    int sum(int a,int b)//查询区间和
    {
        return sum(b)-sum(a-1);
    }
};

int q;
char ss[SIZE];
vector<ppair> match;
vector<ppair> query;
vector<int> ans;

void preload()
{
    stack<int> st;
    for (int i = 0; ss[i]; i++) {
        char c = ss[i];
        if (c == '(') {
            st.push(i);
        } else if (c == ')' && !st.empty()) {
            int now = st.top();
            st.pop();
            match.push_back(ppair(now + 1, i + 1, -1));
        }
    }
}

void solve()
{
    sort(match.begin(), match.end());
    sort(query.begin(), query.end());
    ans.resize(query.size());
    BIT bit;
    bit.init();
    
    int p = 0;
    for (int i = 0; i < (int)query.size(); i++) {
        while (p < (int)match.size() && match[p].r <= query[i].r) {
            bit.add(match[p].l, 1);
            p++;
        }
        
        ans[query[i].id] = bit.sum(query[i].l, query[i].r);
    }
}    

int main()
{
    int a, b;
    scanf("%s", ss);
    preload();

    input(q);
    for (int i = 0; i < q; i++) {
        input(a >> b);
        query.push_back(ppair(a, b, i));
    }
    solve();
    for (auto iter = ans.begin(); iter != ans.end(); ++iter) {
        print(*iter * 2);
    }
    return 0;
}
```