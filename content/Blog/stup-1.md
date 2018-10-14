Date: 2017-04-20 23:17:45
Title: STUP - another (stupid) TCP over UDP protocol (1)
Tags: STUP, TCP, UDP, networking, protocol
Slug: stup-1

## What is STUP?

STUP is the abbreviation of "Speeded/Secure Tcp-like Udp Protocol", which means that it's another TCP over UDP protocol.

Why TCP over UDP?

TCP is a network protocol for general purpose, and it's one of the most commonly used internet protocol on this planet. It is reliable, ordered and well optimized with decades of efforts.

But, there's plenty of reasons to replace that protocol for my scenario.

* ~~Firstly, create my own network protocol is something geeky-nerdy, yep, suits me perfectly.~~

* Firstly, TCP is not "secure" (enough to bypass G\*W).    
Of course, it's not TCP's fault, because the security job is for the application layer. But "大清自有国情在", we are in urgent need for a secure network protocol to obfuscate our network packet to bypass the firewall to get access to the "free internet".     
Shado\*socks is one of the commonly used "secure" network protocol which based on socks5 proxy protocol and TCP.  But still, it has its own problem.

* Secondly, TCP performs badly on harsh transmission condition.     
Because of the flow control and congestion control, the sliding window of TCP will be cut into half when packet is lost or timeout, which is very common on a harsh network connection as the jitter is inevitable.     
It's understandble that TCP has to negotiate the sliding window size with zero knowledge to achieve intra- and inter- protocol fairness, and make a stable network. But for us, we may have enough knowledge for our network, and we may not have too many connections at the same time, so here we don't need control, we need speed. We come up with our own control mechanism - no control is best the control.

## How it works?

![](http://wizmann-pic.qiniudn.com/17-4-20/98249887-file_1492687602713_f658.png)

Our local application behavess like a socks5 proxy client, and send its data to a local adapter which will translate socks5 packet into STUP packet. The adapter doesn't need to understand the "meaning" of socks5 packets, it just take it as a byte-flow, then encapsulate the data into the STUP packet.

The local STUP client will encrypt the outgoing UDP packet. More precisely, the job of the encryption is to obfuscate the packet to bypass the detector of the G\*W. We will talk about this later.

Then the remote STUP protocol server received the encrypted packet, then it unpack the data and translate it back into the same byte-flow. After that, the socks5 server will get the message and retrieve what we want from the free internet.

In a word, STUP procotol is a secure tunnel between the socks5 client and socks5 server. This design reduces the complexity of the whole system, and make it easy to implement.

## How we implement it? (Big picture)

We use Twisted framework to implement our protocol. The good parts of twisted is it hides the details of network programming and turn everything into events. But twisted is aptly named and it is really "twisted", especially for the new comers.

We implemented our simplfied "TCP stack" with fixed-size sliding window, nagle algorithm, retry mechanism, encrypting, etc. But with the help of Python, one of my favorite programming language ... it's still a complex task to do. And it takes me a year to make it work.

I say thankya.

![](http://wizmann-pic.qiniudn.com/17-4-20/89638264-file_1492701304939_10484.png)