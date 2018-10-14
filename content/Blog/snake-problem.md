Date: 2014-10-20 09:11:27 
Title: Snake Problem
Tags: binary indexed tree, algorithm, geometric
Slug: snake-problem


## 题目

在一个平面上，有n+m条蛇，其中n条蛇沿水平方向（y轴方向）移动，m条蛇沿竖直方向（x轴方向）移动。

现给出这些蛇头和尾所在的坐标点，求出这n+m条蛇在此时共有多少个交点。在同一个方向移动的蛇不会有交点。

如图所示，n = 5, m = 4，这些蛇一共有5个交点。

![Alt text][2]

## 分析

对于此题，最简单直接的方法就是枚举蛇两两之间的关系，这种算法的时间复杂度为O(n^2)。

当然，我们不能满足于这种暴力的解法。那么，有没有更优美的方法呢？

![Alt text][3]

对于这一条在y轴方向上的（红）蛇来说，它与x轴方向上的（黑）蛇共有三个交点。那么，也就意味着，问题的关键在于，我们如何快速确定某一条红蛇（或黑蛇）与其它蛇一共有多少个交点。

我们可以做出如下假设，我们知道当x = k时，所有在平面上的蛇的位置。根据这个假设，我们可以使用区间求和的算法来确定竖直位置上的蛇会有多少个焦点。

假设我们从x = 0到x = MAX_X方向进行扫描，每条蛇在扫描时，都有且只有两种状态：

1. 扫描线第一次经过蛇的某端点
2. 扫描线第二次经过蛇的另一个端点（废话！）

这两个状态分别意味着某一条黑蛇在x = k时是否存在。我们维护一个数组，数组中第u个元素代表y = u的黑蛇是否在x = k时存在。

这个时候，当我们查询一条x = [v, w]位置的红蛇共有多少个交点时，只需要计算数组中[v ... w]元素的和。而使用树状数组(Binary Indexed Tree, BIT)，每次这样的查询只需要O(logN)时间。

所以，总的时间复杂度为O(N * logN)，比O(N^2)的算法优化了很多。

## 代码

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

const int SIZE = 1024;

inline int lowbit(int x) { return x & (-x); }

struct BITree {
    int _tree[SIZE];
    void init() {
        memset(_tree, 0, sizeof(_tree));
    }
    void add(int x, int p) {
        while (p < SIZE) {
            _tree[p] += x;
            p += lowbit(p);
        }
    }
    int sum(int p) {
        int res = 0;
        while (p > 0) {
            res += _tree[p];
            p -= lowbit(p);
        }
        return res;
    }
    int sum(int a, int b) {
        return sum(b) - sum(a - 1);
    }
};

struct Point { int x, y; };
struct Snake { Point start, end; };

class Solution { // manual tested
public:
    int count_intersection(const vector<Snake>& xsnakes,
            const vector<Snake>& ysnakes) {
        int ans = 0;
        _tree.init();
        vector<Mark> vec;
        for (auto s: xsnakes) {
            vec.push_back(Mark({s.start.x, 1, s.start.y}));
            vec.push_back(Mark({s.end.x,  -1, s.end.y}));
        }
        int p = 0;
        for (auto s: ysnakes) {
            vec.push_back(Mark({s.start.x, 0, p++}));
        }
        sort(vec.begin(), vec.end());
        for (auto mark: vec) {
            if (mark.type == 1) {
                _tree.add(1, mark.val);
            } else if (mark.type == -1) {
                _tree.add(-1, mark.val);
            } else {
                p = mark.val;
                int a = ysnakes[p].start.y;
                int b = ysnakes[p].end.y;
                ans += _tree.sum(a, b);
            }
        }
        return ans;
    }
private:
    struct Mark {
        int pos, type, val;
        friend bool operator < (const Mark& a, const Mark& b) {
            return a.pos < b.pos;
        }
    };
    BITree _tree;
};

int main() {
    vector<Snake> xsnakes({
        Snake({ Point({1, 2}), Point({5, 2}) })
    });
    vector<Snake> ysnakes({
        Snake({ Point({2, 1}), Point({2, 3}) }),
        Snake({ Point({3, 1}), Point({3, 3}) })
    });
    Solution S;
    print(S.count_intersection(xsnakes, ysnakes));
    return 0;
}
```

## 题目来源

《算法引论》

## 扩展题目

POJ-2482 [Stars in Your Window][1]

[1]: http://poj.org/problem?id=2482
[2]: data:image/png;base64,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
[3]:data:image/png;base64,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
