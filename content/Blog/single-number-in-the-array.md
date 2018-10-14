Date: 2014-08-05 23:07:02 
Title: Single Number Problem
Tags: 算法, leetcode, algorithm
Slug: single-number-in-the-array


## Introduction

There are a lot of interview problem based on the 1D-array, which is the one of the easiest "data structure".

But the problem about that simple data structure might not be that simple. Here is the summary of the problem about 1D-array.

Of course, most of them come from Leetcode.


## All Twice Excpet One

> Given an array of integers, every element appears twice except for one. Find that single one.

This [problem][1] is the very basic one. So I just paste my code here. If you are confused with the ``xor`` operator， you might have to review the knowledge of **bit manipulation** carefully.

```python
class Solution:
    # @param A, a list of integer
    # @return an integer
    def singleNumber(self, A):
        return reduce(lambda x, y: x ^ y, A)
```

Time complexity: O(n)

## All Once Except One
> Given an array of N integers, which are in the scope of [1...N - 1]. Every element in the array appears once except one. Find that number.

This one is simple enough. But it looks a "hard" problem because we can solve this by using the previously "xor".

It's easy for us to calcuate the summary of the array [1...N - 1], and easy enough to calculate the summay of the given array as well. And the answer is the diffrence of the two summary.

```python
class Solution:
    # @param A, a list of integer
    # @return an integer
    def singleInteger(self, A):
        n = len(A)
        return sum(A) - sum(range(n))
```

Time complexity: O(n)

p.s. ``xor(A) ^ xor(range(n))`` is better if we have a large N that might overflow when we add all the elements.

> Given an array of integers, every element appears once except for one which appears twice. Find that special number.

This problem is harder because all numbers in the array is arbitrary. And it seems hard to find any rules and patterns in the array.

I don't know there is an algorithm which is O(1) space and O(n) time complexity. Tackle it with a hash set may be the best solution, which takes O(n) space and O(n) time complexity.

## All three times except one

> Given an array of integers, every element appears three times except for one. Find that single one.

To slove [this problem][2], just using an array of size 32 to keep track on the total count of the ith bit.

And a tricky solution to reduce the memory usage is use three integers to indicate the remainder of 3 of the total count of the bits.

```cpp
int singleNumber(int A[], int n) {
    int ones = 0, twos = 0, threes = 0;
    for (int i = 0; i < n; i++) {
        twos |= ones & A[i];
        ones ^= A[i];
        threes = ones & twos;
        ones &= ~threes;
        twos &= ~threes;
    }
    return ones;
}
```
## All twice except two

> Given an array of integers, every element appears twice except for two. Find that two numbers.

```
xor(array) = 0 ^ a ^ b
```

[This problem][3] is an update of "All twice except one". It's easy to prove that if there is an "1" in the bits of xor(array), it indicates that a and b are diffrent on that bit. We can separate the whole array by that bit, and then we can get two arrays which each contains a single "single number".

### Once, twice, three times a lady

> Given an array of integers, some of the numbers appear once, and some appear twice, and the others appear three times. Please find the number which appear three times.

Of course, hash map is a panacea, with O(n) space and O(n) time.

And there is another way to solve [this problem][4] with O(1) space and O(n) time. But it has its limitation -- integer overflow. If the max number of this array is too large, it can't be done.

```python
from random import randint
from collections import Counter

N = 100

ns = [randint(0, N - 1) for i in xrange(N)]
counter = Counter(ns)

for i in xrange(len(ns)):
    num = ns[i] % N
    ns[num] += N

d = {}
for i in xrange(len(ns)):
    cnt = ns[i] / N
    if cnt:
        d[i] = cnt
        
print d == dict(counter)
```

Considering the number ``ns[i]`` with the index ``i`` and with the value ``val``. We make ``ns[i] = count(i) * MAX + val``. By that, we can get the count of number ``i`` by ``ns[i] / MAX``, and get the value of ``ns[i]`` by ``ns[i] % MAX``.

And it's the same to find the "missing number of an array of [1 ... n]`` or something like that.

## Summarize

### Hash Map is PANACEA

Almost every problem on the array which want you to detect a single / two / or more "special" number can be tackled by the Hash Map. Easy and fast.

But for almost every problem, a hash map may no the very **BEST** solution.

### Bit Map takes less memory

An update for the hash map is the bit map. It takes less memory, but can storage less infomation, 0 or 1. Further, you can treat several bits as one to put more information in it.

By its very nature, bit map is the same with hash map.

### More powerful tool: Bloomfilter

Bloomfilter is a powerful algorithm / data structure which is used to slove the "in / not in" problem, and takes less memory than hash map, and can do better than bit map if the data is sparse and random.

But it can't keep way the **randomizing error** called **false positive**, and if you can put up with that error and want to reduce your memory usage, try that.

I didn't mention this in my passage, but you can find some information on this [wikipedia page][5]. It's easy.

### xor and bits manipulation

xor is a good way to solve the "only one appear once" problem. And xor manipulate will never cause overflow which will ruin your whole program.

### just calculate the sum of the array

Somethimes we just forget the simplest way to deal with a "hard problem".

For example, once I was asked "give you three integers (a, b, c), and calculate how many (x, y, z) is possible to make ax + by + cz == R".

I'm glad because it is so much like a "3-Sum" problem, and I solve it fast. But the interver told me it's not the best solution. (You know how to deal with 3-sum, right?)

I thought for a while, and give up at last. And the interver told me that the solution is to enumerate (x, y) and get z by this formula.

```
z = (R - ax - by) / c
p.s. must be exact division
```

It's a better and much easier solution, right? It was a shame for me not came up with that idea.

So, don't forget the simple way, it may be the very best solution.

### attach some information to some numbers

It useful if the length of the array (L) and the max value of the array (M). If M * L <= MAX_INT, you can storge the counter of number i in the array[i] by ``array[i] = array[i] + counter * M``.

It's a useful way to implement a counter in the array. And it will be a big plus for you in the interview.

[1]: https://oj.leetcode.com/problems/single-number/
[2]: https://oj.leetcode.com/problems/single-number-ii/
[3]: http://www.v2ex.com/t/94742
[4]: http://www.ituring.com.cn/article/56179
[5]: http://en.wikipedia.org/wiki/Bloom_filter
