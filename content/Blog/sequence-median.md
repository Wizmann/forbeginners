Date: 2014-12-14 16:51:50 
Title: Sequence Median
Tags: quick sort, median, partition, priority queue
Slug: sequence-median

## Description

Given a sequence of integer numbers, try to find the median of the sequence.

### Extending

* Make sure your code can get the right answer in any conditions
* Make sure your code work effectively on some special kinds of sequence. For example, ordered sequence or a nearly ordered one, a sequence with few unique items.
* If the memory is not large enough for all the elements in the sequence, how can we implement this algorithm?
* If it's not a sequence, but a data stream. How can we find the median?

## Solution

Finding the median is quite similar to finding the kth element.

The basic solution to find the kth element is to sort the sequence first, and then find the kth. It'll get the right answer, of course, but the time complexity is O(n * logn), which is not the optimized one.

There is a vintage algorithm to get the kth_element.

```cpp
int partition(int array[], int st, int end) {
    int pivot = array[st];
    int l = st, r = end - 1;
    while (l <= r) {
        while (l <= r && array[l] <= pivot) {
            l++;
        }
        while (l <= r && array[r] > pivot) {
            r--;
        }
        if (l <= r) {
            swap(array[l++], array[r--]);
        }
    }
    swap(array[st], array[r]);
    return r;
}

int kth_element(int array[], int n, int k) {
    return kth_element(array, 0, n, k);
}

int kth_element(int array[], int st, int end, int k) {
    int pivot_idx = partition(array, st, end);
    if (pivot_idx - st + 1 == k) {
        return array[pivot_idx];
    }
    if (pivot_idx - st >= k) {
        return kth_element(array, st, pivot_idx, k);
    } else {
        return kth_element(array, pivot_idx + 1, end, k - (pivot_idx - st) - 1);
    }
}

double find_median(int array[], int n) {
    if (n & 1) {
        return 1.0 * kth_element(array, n, n / 2 + 1);
    } else {
        int a = kth_element(array, n, n / 2 - 1);
        int b = kth_element(array, n, n / 2);
        return 0.5 * (a + b);
    }
```

The time complexity of the algorithm is O(N). It works well in most conditions. But there is a potential error in the code, can you find it?

```cpp
return 0.5 * (a + b);
```

If ``a + b`` is greater than INT_MAX, it will overflow, and make a mess to your code. The right way is：

```cpp
return 0.5 * a + 0.5 * b;
```

There is another problem in the code. If the sequence is already ordered, the algorithm will take O(N^2) time, and can't work effectively as what we design. It is because the pivot is the very first element of the sequence (or the sub-sequence), if the sequence is ordered, we will partition the sequence into this:

```
nil ++ pivot ++ [elements]
```

The solution is to use the random pivot. And we will modify the code here.

```cpp
int partition(int array[], int st, int end) {
    if (st == end) {
        return st;
    }
    int pivot_idx = st + random() % (end - st);
    int pivot = array[pivot_idx];
    swap(array[st], array[pivot_idx]);
    
    int l = st, r = end - 1;
    while (l <= r) {
        while (l <= r && array[l] <= pivot) {
            l++;
        }
        while (l <= r && array[r] > pivot) {
            r--;
        }
        if (l <= r) {
            swap(array[l++], array[r--]);
        }
    }
    swap(array[st], array[r]);
    return r;
}
```

This code will perform well for the ordered / nearly ordered data. But there is another "however", what if there are few unique elements in the sequence?

For example, the sequence `[1, 1, 1, 1, 1, 1, 1]`. If we deal this sequence by the previous algorithms, it also takes O(N) time, because we can just separate the sequence into this:

```
[elements] + pivot + nil
```

This scenario is similar as the previous one. So we have to come up a new way to cope with it.

```cpp
int partition(int array[], int st, int end) {
    if (end - st <= 1) {
        return st;
    }
    int pivot_idx = st + rand() % (end - st);
    swap(array[st], array[pivot_idx]);
    int pivot = array[st];
    
    int l = st, r = end - 1;
    int flag = 0;
    while (l <= r) {
        // <- rewrite zone
        while (l <= r && array[l] <= pivot) {
            if (array[l] == pivot && flag == 0) {
                flag ^= 1;
            } else if (array[l] == pivot) {
                break;
            }
            l++;
        }
        while (l <= r && array[r] >= pivot) {
            if (array[r] == pivot && flag == 1) {
                flag ^= 1;
            } else if (array[r] == pivot) {
                break;
            }
            r--;
        }
        // <- end of rewrite zone
        if (l <= r) {
            swap(array[l++], array[r--]);
        }
    }
    swap(array[st], array[r]);
    return r;
}
```

This code could put the same number into left part and right part by half.

With all these optimization, you can get an **Accepted** in the problem [POJ-2623][1]. But be ware, the function to initizalize of random number, `srand(time(NULL))`, is disallowed when using the G++ compiler, please choose C++ instead.

There's always something next, if we don't have enough memory to storage all the data in the sequence. We will use a heap to find the kth_element, and that will save half of the memory space. But the time complexity is O(n * logn) here.

```cpp
// This is a bad code :)
int main() {
    int n;
    long long x;
    input(n);
    int k = n / 2 + 1;
    priority_queue<long long> pq;
    for (int i = 0; i < n; i++) {
        scanf("%lld", &x);
        pq.push(x);
        if ((int)pq.size() > k) {
            pq.pop();
        }
    }
    if (n & 1) {
        printf("%.1f\n", 1. * pq.top());
    } else {
        long long a = pq.top();
        pq.pop();
        long long b = pq.top();
        printf("%.1f\n", double(a + b) / 2.);
    }
    return 0;
}
```

Okay, there is the last problem: what if the sequence is a stream that you have to find the median whenver a new number comes in? The solution is using two heaps. The max heap storages the numbers which less than the median, and the min heap storages the numbers which greater than the median.

```cpp
template<typename T>
class MaxHeap: public priority_queue<T> {};

template<typename T>
class MinHeap: public priority_queue<T, vector<T>, greater<T> > {};

class MedianStream {
public:
    void add(int u) {
        if (_max_heap.empty() || u <= _max_heap.top()) {
            _max_heap.push(u);
        } else {
            _min_heap.push(u);
        }
        do_adjust();
        _size++;
    }
    double get_median() {
        if (_size & 1) {
            return 1.0 * _max_heap.top();
        } else {
            int a = _max_heap.top();
            int b = _min_heap.top();
            return 0.5 * a + 0.5 * b;
        }
    }
private:
    void do_adjust() {
        while (_max_heap.size() > _min_heap.size() + 1) {
            _min_heap.push(_max_heap.top());
            _max_heap.pop();
        }
        while (_min_heap.size() > _max_heap.size()) {
            _max_heap.push(_min_heap.top());
            _min_heap.pop();
        }
    }
private:
    size_t _size;
    MaxHeap<int> _max_heap;
    MinHeap<int> _min_heap;
};
```

[1]: http://poj.org/problem?id=2623
