Date: 2017-05-08 22:15:58
Title: STUP - the Implementation (3)
Tags: STUP, TCP, UDP, networking, protocol
Slug: stup-3

## throughput and window size

The wisdom of STUP protocol is all about the window size. The throughput of a TCP communication is limited by two windows: the congestion window and the receive window. The congestion window can determine how many bytes that can be send a simple piece of time, and the receive window indicates the capacity of the receiver to process data.

Both windows influence the throughput of our connection. As the size of receive window is already set after 3-way handshake process, the congestion window is the critical influence. But why?

TCP use congestion control to achieve high performance (really?) and avoid congestion collapse. But here in STUP, we have different situations.

Firstly, we need real high performance. We don't want the window size cut into half when there is a lost / timeout packet, which is very normal in our "long thin pipe". Secondly, STUP is not a protocol for general usage, by the initial  design, it should be used in an exclusive, non-production environment. So we don't need to care about our neighbors, we can just use up a reserved, reasonable bandwidth.

However, be aware of the number in `Config.py`. Our router was down once because of a wrong configuration. :)

## other mechanisms and algorithms in STUP

* Keep Alive
* Nagle algorithm
* Piggybacking
* Fast retransmission

These features are copied from TCP protocol and absolutely a cliché to have a discuss here. If you have any problem about these, just look it up in Wikipedia.

## twisted Twisted Framework

STUP protocol takes me about a whole year to do the development work (and it's not finished yet). But for more than half of the time, I was struggling with the Twisted framework. For people who want to learn more about Twisted Framework, you can read the [official manual][1] or look through [this blog][2] for a quick start.

What a pun!

## future of STUP

Since STUP protocol is written in Python, one of the main problem is the performance. As a result, I'm planning to rewrite this with C++ (and golang, perhaps) to gain a better performance. I call it: STUPP (STUP in cpp).

In STUPP, several features are to be added:

* Selective ACK
* Monotonic strictly increasing sequence number to prevent replay attacks
* Multiple socks5 connections share a single STUP connection

## the end

> You weren't rejected, you were betrayed.
>
> _the Newsroom_, S01E09


<iframe width="560" height="315" src="https://www.youtube.com/embed/j6KlNNEw9dg?ecver=1" frameborder="0" allowfullscreen></iframe>

[1]: http://twistedmatrix.com/trac/wiki/Documentation
[2]: http://wizmann.tk/twisted-defer-and-deferredqueue.html