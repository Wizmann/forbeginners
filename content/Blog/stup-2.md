Date: 2017-05-04 00:53:03
Title: STUP - Packet Structure and State Machine (2)
Tags: STUP, TCP, UDP, networking, protocol
Slug: stup-2

## STUP Packet Structure

### Brief Introduction of TCP & UDP Packet Structure

![](http://wizmann-pic.qiniudn.com/17-4-24/73808256-file_1493006773118_a335.png)

STUP pretend itself as a protocol at the Transmission Layer, but actually it's absolutely an Application Layer protocol. So before we start, I'd like to recall some knowledge of two important Transmission Layer protocol: TCP & UDP.

It is well known that TCP is a "connection-oriented", "reliable", "ordered". To make an analogy (a little bit inappropriate), TCP is like a phone call (good cell signal strength):

1. you are keeping a connection
2. your words and sentences are well-received and well-ordered

As a result, each TCP packet has a unique and ordered sequence number, and your partner has to reply an "ACK" (short of "ACKnowledgement") when it receive a packet. And it has to keep a connection and control the flow, a lot of control header is added to the header, so as the "window size".

In a word, TCP is a heavy-weight protocol which offers high reliability. But the performance is highly depend on the network condition.

UDP is on the other way around, it's "connectionless", "unreliable" and "unordered". To make another analogy, UDP is like a SMS message:

1. there is no connection
2. there is no guarantee that your partner will receive the message
3. there is no guarantee of the order of messages, espiecially on a bad network

UDP is a lightweight protocol who doesn't care about the connection and reliability, it just does it best to serve. And, of course, the performance is better than TCP.

### STUP Packet Structure & Why?

As I mentioned before, the only problem for me in TCP is the flow control. But that part is deep in the kernel, it is unnecessarily complicated to hack the kernel, a user application is good enough here for me.

So, I build STUP over UDP to make everything simple. Firstly, UDP is a commonly used and well-known protocol, we can take advantages of existing infrastructure, framwork and libs. Secondly, UDP is lightweighted protocol, the overhead to build a new protocol over it is almost nothing. 

![](http://wizmann-pic.qiniudn.com/17-5-2/38201062-file_1493708415970_dc40.png)

The chart above shows STUP packet structure. And the bits in green are plain-text and the others in red are encrypted.

* Random IV (16bits): plain text, used to assemble the encrypt key
* Version (3 bits): for compatibility use, currently is "000"
* Nonce (6 bits): indicate the length of random trail padding data, used for data confusion
* URG (1 bit): urgent flag, internal use
* LIV (1 bit): keep-alive flag
* ACK (1 bit): acknowledgement flag
* PSH (1 bit): temporarily prohibit nagle algorithm for this packet
* RST (1 bit): reset flag
* SYN (1 bit): sync flag
* FIN (1 bit): finalize flag
* Seq number (32 bits): same as TCP
* Ack number (32 bits): same as TCP

The structure of STUP packet is quite similar to TCP packet, because we are imitating TCP, literally.

### Data obfuscation of STUP packets

One of the most important part of STUP protocol is obfuscation. We try to hide our intend of the network traffic to bypass the G*W. Except obfuscate the data, we also need to hide some patterns, for example, the handshack process, ack mechanism, etc.

The first step is encryption, of course. It can help us the hide the feature inside data, for example, the pattern of a HTTP request can be easily detected. We use AES-ECB to encrypt the content of our packet.

But why AES-ECB? There are a lot of saying on the internet that AES-ECB sucks, because it leaks plaintext data patterns. 

![](http://wizmann-pic.qiniudn.com/17-5-2/19737252-file_1493708926479_15add.png)

It is because we ecrypt the STUP packet **as a whole**, it means there is no way to get the sequence number to order the packets before we decrypt it. As a solution, we add a "random IV" as a plain text in the STUP header. So the key to ecrypt is a combination of 48 bits pre-defined key and 16 bits random key. It might lead to a risk of small key space, but actually it's more than enough to keep out traffic safe as we are not VIP who worth a brute force hacking.

And still, there is another problem that we can't hide the length information of our packet with a symmetric encryption. The solution is to append random padding bytes at the tail of every packets for data obfuscation, and use the `nonce` field to mark the length of the paddings, then enrypt it. When receiver get the packets, firstly decrypt the packet, then drop the useless padding bytes and get the real data.

## STUP State Machine

![](http://wizmann-pic.qiniudn.com/17-4-24/70104484-file_1493025532333_338c.png)

STUP state machine is also a simplify TCP state machine. And, in essence, they behave exactly the same. 

## What's next?

In next blog (maybe the last one for STUP series), we will talk about some details about the implementation, and future plan for this protocol.

[1]: https://crypto.stackexchange.com/questions/20941/why-shouldnt-i-use-ecb-encryption
[2]: https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation