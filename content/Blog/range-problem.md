Date: 2018-02-20 22:59:47
Title: 一种区间交问题的奇怪姿势
Tags: algorithm, leetcode, C++
Slug: range-problem

## 我们要解决什么问题

区间交问题，是我们在做题中经常遇到的问题。

例如，[Insert Interval][1]一题，就是比较直白的区间交问题：

> 给定一系列的整数区间，再插入一个新的区间，问合并后的整数区间是什么

类似的还有[Merge Intervals][5]：

> 给定一系列可能有重叠的整数区间，求合并后的整数区间


另一种区间交问题的描述是时间区间相关的问题，如[Time Intersection][2]:

> 给定用户A和用户B的在线时间区间，问两人同时在线的时间区间

又如经典的会议室安排问题[Meeting Rooms][3]和[Meeting Rooms II][4]:

> 给定N个会议的时间区间，问一个人能否参加所有的会议

以及

> 给定N个会议的时间区间，问最少需要多少个会议室

还有系统设计与API设计包装后的算法题[Range Module][6]。归根结底，都是整数区间问题的变形或者包装。

## 传统解法

对于这类区间问题，传统的解法是将区间使用顺序容器（如`vector`）保存，在查询和修改时，使用“排序+遍历”或者“排序+二分”。

这种解决在一定程度上是区间问题的通解，但是这样做也有它的问题。

一来区间问题有很多对区间序列进行随机增加、删除，这样的操作对于顺序容器是非常不友好的。

二来对于使用“起点”或“终点”排序的区间，二分查找需要处理很多重复值，在某些情况下会发生复杂度的退化。

那么我们如何优化我们的实现来解决以上的问题呢？

## 使用`std::set<Interval>`

我们以[Merge Intervals][5]一题为例。只要两个区间有交集，无论是哪一种形式的相交，那么我们就需要把这两个区间合并。

![](http://wizmann-pic.qiniudn.com/18-2-20/85403056.jpg)

所以，我们只需要能高效的判断两个区间**是否相交**，就可以解决这个问题了。

但是在这里，我们反其道而行之，先来讨论一下**不相交**的情况。对于两个不相交的区间`A`和`B`，只存在两种情况，一是`A`在`B`左面，二是`A`在`B`右面。

![](http://wizmann-pic.qiniudn.com/18-2-20/87075632.jpg)

我们可以把区间的左右关系看成不相交区间的顺序关系，即：

* 如果区间`A`在区间`B`的“左边”，我们说`A < B`
* 如果区间`A`在区间`B`的“右边”，我们说`A > B`

所以，根据不相交区间的性质，我们可以很自然的将它们存储在`std::set<Interval>`当中。这样我们就可以在`O(logN)`时间进行查找、随机插入与随机删除。

那么，回到最开始判断区间**是否相交**的问题。对于相交的区间`A`和`B`，非常明显，`A < B`与`A > B`都是不成立的。在`std::set<Interval>`中，这种关系被判定为**相等**。

虽然这种**相等**关系是不符合常规逻辑的，但是却非常实用。如果两个区间有“大小”关系，我们可以知道区间的相对位置。而如果两个区间“相等”，则我们可以知道两个区间一定相交。更重要的是，在这类题目中，两个相交的区间是不能同时存在的。这与`std::set<Interval>`中元素的唯一性相呼应。

所以，在使用`std::set<Interval>`来存储区间时，我们可以使用如下的性质：

* 使用`find()`函数来查找相交区间。这里要注意，相交的区间可能有多个
* 使用`insert()`来插入区间。这里要注意，先要判断是否有区间与新插入的区间相交
* 使用`erase()`来删除区间。

## 实战 - Merge Intervals

> 在Merge Intervals一题中使用std::set<Interval>并不是最优的解法。这里只做举例。

题目链接：[Merge Intervals][5]

```cpp
/**
 * Definition for an interval.
 * struct Interval {
 *     int start;
 *     int end;
 *     Interval() : start(0), end(0) {}
 *     Interval(int s, int e) : start(s), end(e) {}
 * };
 */

// overload the comparator for std::set
bool operator < (const Interval& i1, const Interval& i2) {
    return i1.end < i2.start;
}

class Solution {
public:
    vector<Interval> merge(vector<Interval>& intervals) {
        set<Interval> st;
        for (auto interval: intervals) {
            // merge intervals which are overlaped
            while (true) {
                auto iter = st.find(interval);
                if (iter == st.end()) {
                    break;
                };
                interval = {
                    min(interval.start, iter->start),
                    max(interval.end, iter->end)
                };
                st.erase(iter);
            }
            
            // add the new interval to std::set
            st.insert(interval);
        }
        
        // copy the intervals to a vector
        vector<Interval> result;
        copy(st.begin(), st.end(), back_inserter(result));
        return result;
    }
};
```

上面的代码中，`std::set<Interval>`中存储了已经合并好的区间。当加入新的区间时，我们会先判断新区间是否与已有区间相关，如果相交，则进行合并。

## 实战 - Range Module

题目链接：[Range Module][6]

> 题意：     
设计一个类，提供三个接口：        <br><br>
接口1：`void addRange(int left, int right)`     
将区间`[left, right - 1]`加入区间集合 <br><br>
接口2：`bool queryRange(int left, int right)`     
查询是否已有区间与区间`[left, right - 1]`相交 <br><br>
接口3：`void removeRange(int left, int right)`
移除已有区间内，位于`[left, right - 1]`范围内的所有数

这个题目看似可以完全套用我们上面讲到的`std::set<Interval>`的实现，但是这里有几个暗坑需要注意。

首先我们来看接口3，这里的删除并不是删除区间，而是删除整数，所以我们可以使用`find()`函数，但是与之前的合并操作不同，我们在这里要删除区间中的一部分。

在删除整数操作进行完之后，会引入一个新问题，这就是一些连续的整数区间，会在`std::set<Interval>`中表现为独立的多个区间。例如，区间`[1, 5]`，在删除了`[2, 3]`之后，会形成两个区间`[1, 1]` 和 `[4, 5]`。我们再把区间`[2, 3]`加回来，如果不进行特殊操作，就会产生三个不相交但连续的区间`[1, 1]`、`[2, 3]`和`[4, 5]`。所以我们在插入区间时，要多做一步区间合并的操作。

具体的实现为：

1. 在插入区间`[l, r]`之前，先查找是不存在区间包含`[l - 1, l - 1]`或`[r + 1, r + 1]`。如果有，则先将已有的相邻区间合并的新区间里
2. 将新的区间进行合并操作，插入`std::set<Interval>`

正确性证明：

* 已知1：空区间集合不包含**不相交但连续的区间**
* 已知2：只有插入操作会产生**不相交但连续的区间**
* 归纳假设：我们保证在任何插入新区间的操作之前，`std::set<Interval>`中均不包含**不相交但连续的区间**。
* 证明：<br>
如果区间集合内不包含**不相交但连续的区间**，那么对于新加区间，我们只需要尝试合并其近邻区间`[l - 1, l - 1]`和`[r + 1, r + 1]`，就不会产生**不相交但连续的区间**。

代码实现如下：

```cpp
struct MyInterval {
    int left, right;
    
    bool operator < (const MyInterval& other) const {
        return this->right < other.left;
    }
};

class RangeModule {
public:
    RangeModule() {
        // pass
    }
    
    void addRange(int left, int right) {
        right -= 1;
        
        MyInterval ll = {left - 1, left - 1};
        auto liter = st.find(ll);
        if (liter != st.end()) {
            left = liter->left;
        }
        
        MyInterval rr = {right + 1, right + 1};
        auto riter = st.find(rr);
        if (riter != st.end()) {
            right = riter->right;
        }
        
        doAddRange(left, right);
    }
    
    void doAddRange(int left, int right) {
        MyInterval newInterval = {left, right};
        while (true) {
            auto iter = st.find(newInterval);
            if (iter == st.end()) {
                break;
            }
            newInterval.left = min(newInterval.left, iter->left);
            newInterval.right = max(newInterval.right, iter->right);
            st.erase(iter);
        }
        st.insert(newInterval);
    }
    
    bool queryRange(int left, int right) {        
        right -= 1;
        MyInterval interval = {left, right};
        auto iter = st.find(interval);
        if (iter == st.end()) {
            return false;
        }
        
        return iter->left <= left && right <= iter->right;
    }
    
    void removeRange(int left, int right) {
        right -= 1;
        MyInterval newInterval = {left, right};

        while (true) {
            auto iter = st.find(newInterval);
            if (iter == st.end()) {
                break;
            }
            auto cur = *iter;
            st.erase(iter);
            
            if (cur.left < newInterval.left) {
                st.insert({cur.left, newInterval.left - 1});
            }
            if (cur.right > newInterval.right) {
                st.insert({newInterval.right + 1, cur.right});
            }
        }
    }
private:
    set<MyInterval> st;
};
```


[1]: https://leetcode.com/problems/insert-interval/description/
[2]: http://lintcode.com/en/problem/time-intersection/
[3]: https://segmentfault.com/a/1190000003894670
[4]: http://www.cnblogs.com/grandyang/p/5244720.html
[5]: https://leetcode.com/problems/merge-intervals/description/
[6]: https://leetcode.com/problems/range-module/description/