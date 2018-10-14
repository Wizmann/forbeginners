Date: 2015-07-26 22:48:33
Title: Using Set Cover to Optimize a Large-Scale Low Latency Distributed Graph
Tags: System Design, Linkedin, Social Network
Slug: using-set-cover-algorithm-to-optimize-a-large-scale-low-latency-distributed-graph

## Background

Linkedin (or other social networks, such as Facebook and G+) use the "social graph information" to show the social relationship between you and other members.

Such as, "You and Mr.Obama share 10 mutual friends" or "You have 1,000 second-degree connections".

This feature is very common for a social network. But where does it come from?

## Basic API for Social Graph Information

The information about a social relationship can be get from three basic APIs.

* Get Connections
"Who does member X know?"
* Get Shared Connections
"Who do I know in common with member Y?"
* Get Graph Distance
"What the graph distance between member Z and me?"

## Main Components for the System

![](http://wizmann-pic.qiniudn.com/15-7-25/59618247.jpg)

* Graph Database (Graph DB)
* Distributed Network Cache (NCS)
* Graph APIs

## Basic Algorithm for Social Graph

Because the problems of social graph share the same essence. Here we just talk about the "Graph Distance" problem.

![](http://wizmann-pic.qiniudn.com/15-7-25/24130302.jpg)

The _Graph DB_ stores all the relationship of the members. When we ask for the information of _second degree creation_,

* Firstly, the web server communicate with GraphDB to get all the 1st degree connections
* Secondly, web server communicate to GraphDB again to get all the 2nd degree connections
* At last, the web server will merge all the results from the GraphDB to make it sorted and unique.

To make the retrieval more effectively, we add a cache level called _NCS_ to cache the result we get from the GraphDB.

## The Disadvantages of the Basic Algorithm

As we know, for a distributed system, there are shards, replica and load balancer to handle large amount of data and queries.

Consider this scenario.

![](http://wizmann-pic.qiniudn.com/15-7-25/4544395.jpg)

Two queries are both ask for the data from shard 1 and shard 2.

The first query (the green one) has to communicate with the database twice, and then do the merging to get the final results.

And the second query (the red one) only has to talk to database once. And no de-duplicate is needed, because there's definitely no duplicate data in one single node of the database.

We can make a conclusion that if we have a **wise** load balancer, we can optimize our retrieval logic remarkably.

## Set Cover Problem

> Given a set of elements \{1,2,...,m\} (called the universe) and a set S of n sets whose union equals the universe, the set cover problem is to identify the smallest subset of S whose union equals the universe. (Wikipedia)

This problem is similar to ours. The optimal algorithm for a load balancer is to find the minimal subsets of all sets which union equals to the ones that asked by the query input.

It seems that we find the key to our problem. But this is NP-complete. There is no effective way to find the optimal solution.

However, in practice, a greedy algorithm will actually do the trick. The rule of the greedy algorithm is to find the set which contains largest number uncovered elements.

![](http://wizmann-pic.qiniudn.com/15-7-26/80102455.jpg)

## Conclusion

We finally find out that the social information and the relationship graph is **not that difficult**. The basic concepts are quite easy. And the main work for the whole system is to use the cache to reduce the amount of calculation on the fly.

![](http://wizmann-pic.qiniudn.com/15-7-26/65691084.jpg)

## Reference

This post is mainly based on this [video](https://www.usenix.org/conference/hotcloud13/workshop-program/presentations/wang).

[Slides](https://www.usenix.org/sites/default/files/conference/protected-files/wang_hotcloud13_slides.pdf)

Special thanks to Linkedin for the sharing. :)
