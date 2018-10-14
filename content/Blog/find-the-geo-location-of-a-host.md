Date: 2014-01-24
Title: 如何判断一个网站的地理信息
Tags: 面试
Slug: find-the-geo-location-of-a-host

## 啥？

面试题：

> 有一个网站，如何判断这个网站的地理信息

## 方法

### 使用反向DNS

当我们只有网站的IP地址时，我们可以使用**反向DNS**来获得这个IP地址对应的域名。

> 反向域名解析，Reverse DNS。反向域名解析与通常的正向域名解析相反，提供IP地址到域名的对应。

我们可以使用``dig -x``来进行查询

```
$ dig -x 75.126.43.235

; <<>> DiG 9.8.1-P1 <<>> -x 75.126.43.235
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 26688
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 0

;; QUESTION SECTION:
;235.43.126.75.in-addr.arpa.	IN	PTR

;; ANSWER SECTION:
235.43.126.75.in-addr.arpa. 3518 IN	PTR	75.126.43.235-static.reverse.softlayer.com.

;; Query time: 76 msec
;; SERVER: 8.8.4.4#53(8.8.4.4)
;; WHEN: Fri Jan 24 18:15:22 2014
;; MSG SIZE  rcvd: 100
```

我们可以从接续出来的域名中，获得一些信息，例如公司名/机构名，以及``.cn``, ``.us``等有可能标识地理位置的信息。

但是，反向DNS不一定成功。

## 查询DNS LOC信息

> In the Domain Name System, a LOC record (RFC 1876) is a means for expressing geographic location information for a domain name.

所以我们可以尝试使用``dig loc``命令来查询位置信息。（不一定成功

```
$ dig loc SW1A2AA.find.me.uk

; <<>> DiG 9.8.1-P1 <<>> loc SW1A2AA.find.me.uk
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 49682
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 0

;; QUESTION SECTION:
;SW1A2AA.find.me.uk.		IN	LOC

;; ANSWER SECTION:
SW1A2AA.find.me.uk.	21600	IN	LOC	51 30 12.748 N 0 7 39.611 W 0.00m 0.00m 0.00m 0.00m

;; Query time: 1232 msec
;; SERVER: 8.8.4.4#53(8.8.4.4)
;; WHEN: Fri Jan 24 18:21:44 2014
;; MSG SIZE  rcvd: 64
``` 

## 随便看看

查看我们要调查的网站，找寻可用的线索。（囧

## 使用whois服务

http://whois.chinaz.com/sina.com

我们可以看到域名的注册信息，其中也必然透露了线索。

## traceroute与whois配合使用

可以根据包的转发状况来获得最终的地理位置

## 使用Time of day service

``telnet www.bupt.edu.cn 13``可以获得主机的当前时间，从而判断主机所在的经度。（不一定成功。。。

## 参考链接

http://www.private.org.il/IP2geo.html

http://www.ipgeo.com/