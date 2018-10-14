Date: 2015-08-01
Title: Code Golf - Heapify
Tags: code golf
Slug: code-golf-heapify

```cpp
void heapify(vector<int>& vec) {
    int n = vec.size();
    for (int a = 0, b = 1; b - 1 < n; a = b, b <<= 1) {
        nth_element(vec.begin() + a, vec.begin() + b, vec.end());
    }
}
```

You can implement a "heapify" by only four lines of code. And the time complexity is `O(n)`.

Fancy, right? :)
