Date: 2014-06-12 17:42:51 
Title: A simple problem - World at War
Tags: algorithm, interview, graph
Slug: world-at-war

## Background

> This problem is from the book "[Algorithm 4th edition][1]" (Exersise 4.1.10)

There are N cities and M undirected roads between those cities. People can travel to any city along the roads.

One day, a war breaks out. Our cities are under attack! As we can't defend all these N cities, the commander wants you to find the least important city, which means that if this city fell to the enemy, the traffic among other cities would not be affected.

If there are multiple answers, print any one of them. If there's no that kind of city, print -1.

![world-at-war][2]

## The spanning tree of a graph

> It is a spanning tree of a graph G if it spans G (that is, it includes every vertex of G) and is a subgraph of G (every edge in the tree belongs to G). 
> -- wikipedia

![spanning-tree][3]

For example, there is a spanning tree of a graph. These nodes in green is leaf node. So it is easy to know that if we remove a leaf node, the graph won't be affect. The rest of the graph (and the spanning tree) are still connected.

So the answer is here.

## How to generate a spanning tree

There are multiple ways to generate a spanning three of a undirected graph. The most famous algorithm is **prim**, which will generate a MST(minimum spanning tree) with O(n**2) time complexity.

However, MST is not needed in this scenario, because an arbitrary spanning tree is enough to find one of the leaf nodes.

Depth first search (a.k.a DFS) is one of the simplest way to generate the spanning tree. We just start from arbitrary node of the graph, and search through the graph until it comes to a dead-end -- the leaf node. Then print the answer.

Problem solved.

## Show me the code

```cpp
class Solution {
public:
    int least_important_city(vector<vector<int> > g) {
        if (g.size() == 0) {
            return -1;
        }
        int n = g.size();
        
        vector<bool> visit;
        visit.resize(n);
        fill(visit.begin(), visit.end(), false);
        
        int now = 0;
        while (true) {
            bool flag = false;
            visit[now] = true;
            for (auto iter = g[now].begin(); 
                    iter != g[now].end(); 
                    ++iter) {
                int next = *iter;
                if (!visit[next]) {
                    now = next;
                    flag = true;
                    break;
                }
            }
            if (!flag) {
                break;
            }
        }
        return now;
    }
};
```

  [1]: http://book.douban.com/subject/19952400/
  [2]: https://github.com/Wizmann/assets/raw/master/wizmann-tk-pic/blog-world-at-war.png
  [3]: https://github.com/Wizmann/assets/raw/master/wizmann-tk-pic/blog-spanning-tree.png
