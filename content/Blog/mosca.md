Date: 2016-11-11 22:04:13
Title: Mosca源码阅读
Tags: mosca, mq, message queue
Slug: mosca

## 先在前面

最近心血来潮看了看一个比较有名的开源MQTT broker —— Mosca。不读不知道，读完才恍然大悟 —— 这是啥破玩意（哈哈）。

由于我是nodejs的超级初学者，所以本文会比较浅显，并且只关注big picture，不陷入细节。

这里先规定几个缩写，让后面行文时少打一点字：

* MQ - MessageQueue
* Asco - Ascoltatori

## Ascoltatori - 听者

Ascoltatori是一个意大利语单词，翻译成英文就是listener。

> 这里严重吐槽作者取名字的方式，mosca这种短小的外语单词我们是可以接受的，你说ascoltatori这么长的意大利语单词，你让我们怎么记。      
差评，退款，邮费也要退！

Asco模块的作用是提供一个一致的MQ的抽象，供上层broker使用。

这里我们只分析基于Redis的实现，原因是Redis我相对比较熟悉，功能也比较简单。

### 接口分析

`RedisAscoltatore`有三个半接口：

* subscribe
* unsubscribe
* publish

剩下的那半个是模块的构造函数。接下来我们分别分析接口的功能及其实现。

### Subscribe接口

`this._sub`是`RedisAscoltatore`用来subscribe的连接。首先我们要向MQ订阅指定的topic。

之后我们要在本地维护一个`topic`到`callback`s的映射关系。因为Mosca是一个broker，需要将end user订阅的topic的内容完整的发送到用户那里去，每一个用户在Asco里，用一个callback函数来代表。

用户可以订阅一个特定的topic，也可以使用一个pattern来订阅一系列的topic。


![](http://wizmann-pic.qiniudn.com/public/16-11-10/27730251.jpg)

从图中我们可以看出，右上方的client订阅了`h?llo`（相当于regex中的`h.llo`）。右下方的client订阅了`h[abcde]llo`。而左边的client向`hello` topic发布了一个消息。此时右边的两个client都收到了这条消息，其中pmessage代表这条消息是有pattern的，第二个参数代表了client订阅的pattern topic，而第三个参数代表了这条消息的实际topic，最后一个参数是消息的正文。

所以我们在维护topic-client列表时，只需要维护pattern topic（没有pattern的topic可以视做只匹配当前topic的patter）。当有消息到来时，我们使用pattern topic映射到clients，之后再进行下一步操作。

这里Asco使用了一个叫做[`qlobber`][1]的库，它使用Trie树对topic进行匹配。我们在上文已经说到，Asco是一个统一化的MQ抽象层，所以在不同的MQ中所使用的不同的pattern，我们都需要将其统一成同一种语法进行匹配。而qlobber，在Asco中被封装成`RedisAscoltatore`，就是用来统一不同的语法的。


### Unsubscribe接口

有订阅就有退订，这个接口与上面的是对应的关系。我们只需要将订阅的顺序反过来做一遍就可以了。这个函数相对简单，就不多说了。

### Publish接口

这里的publish，代表是用户的publish的操作。用户数据在“去MQ特色化”之后，会经由`this._client`发布到相应的redis服务。最后调用用户的callback。

这里再吐一个槽，为啥订阅连接叫`this._sub`，发布连接叫`this._client`。难道你不造pub/sub才是真正的对应吗？

### 构造函数

构造函数虽然说是“半个接口”，但是代码量和重要性，却高于上面的接口。因为redis的pub/sub模型是单工的，需要两个连接才可以完成。所以两条连接需要单独初始化。

#### this._startPub

我们先从简单的开始。

这个太简单了，没的可说。就是拉一条电话线，成功了之后改一下状态。

没了。

#### this._startSub

这个比pub要复杂一点。首先，我们还是要拉一条到redis的电话线（连接）。之后注册消息到来时的回调。

我们来看一看这个回调是怎样的流程。

首先还是“去MQ特色化”，将Redis的pattern语法化归成Asco的内部语法。再通过pattern取出相应的callbacks，将消息通过callbacks传递给相应的用户。

这里补充一下，`(sub, topic, payload)`三个参数如果命名为`(pattern, topic, payload)`其实会更清晰。

这个类其实原理上并不复杂，但是由于其需要将不同MQ的pattern转换为统一的语法，所以在中间加了一层，导致复杂性的提升。如果我们只做一个专用的broker，代码其实可以写的更明朗的。

## Mosca - 苍蝇

与Mosquito相对，Mosca是苍蝇的意思。Mosca是Asco的上层封装，与其一起组成了一个MQTT broker，与end user直接交互。

MQ的单一职责是负责消息的发布/订阅，Mosca在其上添加了：

1. 在线离线状态检测
2. 离线消息的支持
3. 客户端持久化
4. 一些权限检测接口

在这里，我们从Mosca的工作流程出发，主要关注离线消息和客户端持久化这两个broker中非常重要的特性。

### 持久化

这里我们还是只看Redis的实现。其实Redis并不是真正的持久化，不过who cares。

这里的持久化就包括了离线消息和客户端持久化两个概念。

离线消息使用`packet:{client_id}`为key进行保存，当用户离线时，broker会将消息先保存在redis中，当用户重新上线时，就将保存好的消息一口气推送过去。

客户端持久化稍微复杂一点。客户端在broker中的状态是其订阅的topic，一般情况下，broker会一直保存用户所订阅的topic，以便保存用户的离线信息。当broker掉电或重启时，我们需要从持久化层将用户的状态重新load到内存。此时，我们使用`client:sub:{client_id}`为key进行保存。

### 整体工作流程

在Mosca启动时，先会注册一些事件，比如“用户登录”，“用户下线”，“用户订阅”等。这些消息由配置文件决定是否下发。

这种设计是为了方便broker的scale out，我们可以在一个MQ上面部署多个broker，这些broker通过MQ的`$SYS`信道进行通信。

当Mosca启动完成后，我们像上面一样，重点关注broker的三个重要事件：

* subscribe
* publish
* unsubscribe

这些事件理论上是Asco的封装，添加了权限控制接口、更复杂的事件，当然还有持久化的支持。例如`subscribe`事件，除了调用Asco之外，还将用户的这次订阅记录在了持久层里。

`publish`事件则是先将数据包存放在持久层，再调用Asco的publish函数。`unsubscribe`也是同样的道理。

### 补一张结构图

![](http://wizmann-pic.qiniudn.com/public/16-11-11/55787779.jpg)

### Mosca的可扩展性

根据我浅薄的理解，Mosca是可以支持scale out的。也就是我们可以在同一个MQ（或同一个MQ抽象）上部署多个Mosca，以服务更多的用户。但是一个用户必须严格对应一个shard，否则会出现消息的重复。这个问题可以在Client端解决，但是不应该是一种常态，只应该在用户迁移或者比较大的系统变动的时候才出现。

由于Mosca的持久化层是以Client为Key的，所以不支持多MQ的模式。MQ的扩展需要由MQ自己来完成，对外提供一个统一的抽象即可。不过这种功能，并不被所有MQ所支持。

## Disclaimer

真是nodejs小白以及MQ小白，上面说的哪里不对，请帮忙提出来。强烈建议不要以本文中的任何观点不加测试的应用到生产环境当中去。

[1]: https://github.com/davedoesdev/qlobber
