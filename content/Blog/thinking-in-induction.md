Date: 2014-09-26 00:10:45 
Title: 思维训练 - Thinkin' in induction
Tags: induction, binary tree, codeforces
Slug: thinking-in-induction

## 热身题 - 24Game

[原题请戳我][1]

### 题意

给你一个包含整数1...n的集合S。接下来进行n-1次操作，每次操作从集合S中选取两个数，在加、减、乘三种运算中选取一种，将结果放回再集合S。在n-1次操作完成后，集合S中只剩下一个数。求问一种取数和运算策略，使最后的结果为24。

举例：

S = [1, 2, 3, 4, 5]

我们选取(2, 5)，并进行加法运算，获得结果7。再将7放回集合S中。

此时，S = [1, 3, 4, 7]。

### 数据范围

1 <= n <= 100000

### 解答

> 建议：请思考10分钟后再来看答案

我们日常写代码，往往是为了实现一个功能或者实现一套逻辑。这时候，我们做的事一般是从零开始，然后逐步迭代，最终实现目标。

这是正常的一种思维方式，也是不错的思维。但是，在我们做题时，按部就班的思路往往会束缚我们的想法。我经常自黑说：**“做什么题都像做模拟题”**，实际上就是这样一个道理。

对于此题，如果我们从零开始思考，必然会遇到“第一次选哪两个数”、“第二次选哪两个数”这样的问题，而解决这种问题的方式大多只能有暴力搜索一种方式。而根据这题的数据规模，暴力搜索在时间和空间上都是不可能的。

当然，也有的同学善于逆向思维，但是，同样也会进入暴力搜索的死路中。

那么这题如何思考呢？ 我们不妨试试归纳法。

假设`n = k`，并且有`f(k)`，使得`f(k)=>24`。那么，易得，对于`f(k + 2)=>f(k) * ((k + 2) - (k + 1))=>24`。

此时，我们只需要找到`f(k)=>24`，就可以证明所有`f(k + 2x) => 24`。聪明的同学们必然可以手动算出`f(4) = 24`的过程，这可以证明对于所有`k >= 4`的偶数，总有`f(k) => 24`。

`f(5) => 24`略微复杂一点，但是也不在话下。这样我们的结论已经扩展到了`k >= 4`的所有整数。

又由于在`k = [1, 2, 3]`时，`f(k)`必须不能推出24。我们的结论已经推广到了所有正整数。此题得证。

## 归纳法

在Udi Manber的_Introdcution to Algorithms - A creative approach_一书中，在第二章就对数学归纳法进行了大篇幅的的讲解。而在一般的算法书中，这个位置往往是给了算法分析。

归纳法是一种“非常有力的证明方法”，可以提供一种想问题的方法，同时可以证明算法的正确性。

归纳法的基本过程如下：


>Let T be a theorem we want to prove.

>Suppose that T includes a parameter n whose value can be any natural number. 

>Instead of proving directly that T holds for all values of n, we prove the following two conditions:

> 1. T holds for n = 1
> 2. For every n > 1, if T holds for n - 1, then T holds for n

## 归纳法应用 —— 笛卡尔树

> 已知一个最大堆的中序遍历序里，要求恢复该最大堆。

或者用另外一种方法来表示，

> 给定一个数组，求一个二叉树，这个二叉树的父节点总比子节点要大，并且这棵树的中序遍历与原数组相同

如果我们从build from scratch的角度来思考这个问题，那么得出来的结论一定是O(n^2)的 —— 每次找到（子）数组的最大值，然后partition这个数组，直到构造出整棵树。

### 换一种思考方式

我们尝试用归纳法的思维去考虑这道题。假设我们已经有一棵树，这棵树满足上面所说的条件，且这棵树展开后为数组的前k项。

此时，我们想要插入第k+1项，有以下几种情况。

1. ``A[k+1] <= A[k]``，此时第k+1项会成为到第k项的右儿子，这样树展开时，第k项和第k+1项必然相联，并且也满足父节点必须比子节点大的条件。
2. ``A[k+1] > A[k]``，第k+1项必然会成为第k项的左儿子。但是我们还需要考虑，第k项的父节点比第k+1项小的情况。经过思考，我们不难发现，第k+1项的左儿子t，一定是第k项祖先节点中小于第k+1项的最大值。而第k+1项则替换掉节点t的位置。

情况一示意图：

![cond1][2]

情况二示意图：

![cond2][3]

由此一来，原本看起来复杂的思路一下子变的简单。我们可以把一个复杂的问题化归到重复的子问题上来。这样我们只需要每次解决一个问题了。

关键代码如下：

```cpp
class Solution {
    // ...
    TreeNode* do_insert(int v) { // one node at a time
        TreeNode* ptr = NULL;
        TreeNode* now = new TreeNode(v);
        while (!st.empty()) {
            ptr = st.top();
            if (ptr->value > v) {
                now->left = ptr->right;
                ptr->right=now;
                st.push(now);
                return root;
            }
            st.pop();
        }
        now->left = ptr;
        st.push(now);
        root = now;
        return root;
    }
    // ...
};
```

## 课后习题 - 最大子段乘积

这是Leetcode新加的一题，在昨天吃撑了喝醉了的情况下，勉强AC，今天看来，自己还是too young too simple啊。

> 给你一个int数组，求这个int数组的最大子段乘积。（不需要考虑溢出）

### 从零开始的想法

最大子段乘积必然是一段不含有0的子段。所以我们可以把子段分割为k段，每一段都不包含0。

对于每一个子段，要满足两个条件，一是尽量为正，二是尽量包含更多的数。

所以对于子段A[l...r]，最大乘积只能为A[m...r]或A[l...m]两种情况。所以我们维护两个指针，就可以求得最后的结果了。

不过。。。等下。。。这真特么twisted啊。。。\_(:з」∠)_

```cpp
class Solution { // a drunk moron who wrote this
public:
    int maxProduct(int A[], int n) {
        int p = 0, q = 0;
        int ans = -INF;
        int pro = 1;
        for (int i = 0; i <= n; i++) {
            if (i != n && A[i] != 0) {
                pro *= A[i];
                ans = max(pro, ans);
                q = i + 1;
            } else {
                if (i < n && A[i] == 0) {
                    ans = max(ans, 0);
                }
                while (p < q) {
                    pro /= A[p];
                    p++;
                    if (p == q) {
                        break;
                    }
                    ans = max(pro, ans);
                }
                p = q = i + 1;
            }
        }
        return ans;
    }
private:
    static const int INF = 0x3f3f3f3f;
};
```

### 用归纳法解决这个问题

让我们做一个假设，对于A[k]来说，我们已知``mini = min(A[i...k])``和``maxi = max(A[i...k])``。mini和maxi是以k结尾的子段中，乘积绝对值最大的负数/正数。所以无论乘一个负数还是一个正数，maxi和mini的值只会是``maxi * a``和``mini * a``。

那么，对于第k+1项来说，以第k+1项结尾的最大子序列必为``max(mini * A[k+1], maxi * A[k+1], A[k+1])``(mini和maxi可能为0)。

同时，我们继续维护mini和maxi两个值。此时，我们就有了一个循环的子问题。代码也就在我们的笔下了。

```python
class Solution:
    def maxProduct(self, A):
        mini, maxi = (1, 1)
        ans = -0xdeadbeef
        for a in A:
            mini *= a
            maxi *= a
            ans = max(ans, mini, maxi, a)
            mini, maxi = min(mini, maxi, a), max(mini, maxi, a)
        return ans
```

[1]: http://codeforces.com/contest/469/problem/C
[2]: data:image/png;base64,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
[3]: data:image/png;base64,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
