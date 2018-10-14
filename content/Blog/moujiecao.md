Date: 2014-02-25
Title: 破解节操的下限
Tags: crack, android, app, chrome-extension, protobuf, angularjs
Slug: moujiecao

## 啥？

![节操精选](http://wizmann-tk-pic.u.qiniudn.com/blog-jiecao-icon.png)

[节操精选](http://jiecao.fm/)是一个**没有下限**的文字图片聚合类移动应用，现在支持Android/iOS移动平台。

![界面](http://wizmann-tk-pic.u.qiniudn.com/blog-jiecao-ui.png)

本人是一个非常懒的人，有电脑就不想碰手机。。。于是萌生了一个在PC端使用这个应用的想法。。。

## HowTo

从界面上我们可以看出，这个App的逻辑其实比较简单。重要的部分有如下几个：

* 获取CS通信协议**（最重要）**

* 频道间切换（精选 - 热门 - 音频- 阅读）

* 展示某一条精选

* 在某一条精选中播放语音

## 获取通信协议

节操还是非常良心的！并没有在后台数据通信中进行任何加密的措施。

抓包工具我使用的是在Windows环境下的[Fiddler](http://www.telerik.com/fiddler)。

这个工具可以建立一个HTTP代理，手机通过代理上网，在电脑上就可以截获所有的数据包进行分析。

在Linux下，可以使用TinyProxy + Wireshark进行抓包，不过配置小麻烦。不过我一直是在Windows下抓包，然后在Linux下做分析和开发的。=。=。。。

图就不上了，如果大家有兴趣自己来搞的话，可以抓来试试。

简而言之，我们从HTTP包中的``Content-type``字段中，发现了我们想要的信息 —— ``application/xprotobuf``。

我去！真良心～

### Protobuf简介

> Protocol Buffers are a way of encoding structured data in an efficient yet extensible format. Google uses Protocol Buffers for almost all of its internal RPC protocols and file formats.

简而言之，Protobuf是一个用于数据传输的DSL（Domain Specific Language）。Protobuf提供了一个编译器，开发者只需要声明需要传输的数据字义，就可以自动编译出适用多种语言的传输代码。

Protobuf官方支持C++, Java, 和 Python。第三方开发者还提供了更多语言的支持。在我的开发中，我使用了``dcodeIO-ProtoBuf.js``，一个开源的JS的Protobuf库，有兴趣的话可以从Github中获取。

```
message Person {
  required int32 id = 1;
  required string name = 2;
  optional string email = 3;
}
```

### 破解Protobuf报文

破解Protobuf报文其实就是用``明文攻击``获取Protobuf的传输数据定义。然后我们生成接受这个报文的Protobuf代码，就可以解析相应的报文了。

有两种方法，一种简单的，一种难的。

我们当然要从逼格高的困难方法开始讲。

#### A hard way to crack protobuf

重点参考：[Google Protocol Buffers 编码(Encoding)](http://www.cnblogs.com/shitouer/archive/2013/04/12/google-protocol-buffers-encoding.html)

其思想就是找到Protobuf的编码规律，然后一个字段一个字段的反推，从而找到完整的数据定义。

同时，Protobuf又有一个很好的兼容性，即如果我们的数据定义是原数据定义的子集，同样可以解析出子集中的所有字段。

所以我们只需要找到重要的几个字段来搞就可以了。破解过程比较无趣，一个位一个位的检查，无脑推。

#### An easy way to crack protobuf

因为我们可以轻松的搞到节操的Apk包，又由于Apk包是可以**反编译**的！

于是我们就可以直接看代码获得Protobuf的数据定义。

这个才叫真无脑。

反编译我使用的是[dex2jar](https://code.google.com/p/dex2jar/)和[jdgui](http://jd.benow.ca/)。

虽然这两个工具都有其局限性，但是搞这个一个App还是轻轻松松。

于是我们就获得了一个完整的数据定义。但是由于还是要给[美丽的CEO姐姐](http://weibo.com/121100059)一点面子的～

所以就不公开了～上一个高清有码大图～

![protobuf](http://wizmann-tk-pic.u.qiniudn.com/blog-jiecao-protobuf.png)


## 关于开发

无图无JJ，先上一张效果图。

由于是个人开发，所以界面比较粗糙。如果有前端神牛，可以做出更炫的效果。

还有一个原因是手机的dpi比电脑屏幕的要高一些（用retina屏幕的土豪们退散），所以同样大小的“窗口”，电脑的显示会粗糙很多。

![节操App](http://wizmann-tk-pic.u.qiniudn.com/blog-jiecao-app-ui.png)

### 应用载体

由于拉取数据的操作是HTTP POST。因为浏览器的安全策略，我们不能跨域POST。所以我使用了Chrome浏览器中的App插件。

Chrome为App插件提供了相对宽松的安全策略，我们可以跨域POST，可以获得图像，可以修改一个webview里面的代码。。。

更重要的是，我们可以把一个ChromeApp基本视为一个本地应用，放到桌面上或者启动栏上。

![启动器](http://wizmann-tk-pic.u.qiniudn.com/blog-jiecao-chrome-app-launcher.png)

我用的是Xubuntu，在其它系统上，如Win、MacOS以及其它不同的Linux发行版，也可以达到类似的效果。

### 总体规划

从上面我们可以看出来，这一个页面主要分为三部分。

第一个是Logo，一个``<img>``标签。

第二个是一个按钮组，用来切换下面的内容列表的内容。

第三个是内容列表，列表中的每一个元素都对应着一篇节操文章。

于是，我选用了MVC模式来解决界面问题。

* M - Model
每一个节操文章，其中有``icon``, ``title``, ``channel``, ``subcribe_num``几个字段。

* V - View
前端展示

* C - Control
控制器，切换频道、刷新以及下一页等与服务器端交互的功能。

说到前端MVC，我们就不能不说到一个JS框架 —— AngularJS。

#### AngularJS

![AngularJS](http://wizmann-tk-pic.u.qiniudn.com/AngularJS-large.png)

> AngularJS是一款开源 JavaScript函式库，由Google维护，用来协助单一页面应用程式运行的。它的目标是透过MVC模式 (MVC) 功能增强基于浏览器的应用，使开发和测试变得更加容易。

AngularJS是一个设计非常巧妙的JS框架。由于我是前端文盲，所以只使用了其中最基础的部分。

在AngularJS上面我也不想多说什么，因为比较菜。大家可以参考AngularJS的文档以及Chrome Extension的文档。Chrome Extension官方给出的范例都有Javascript/AngularJS两个版本，非常值得学习。（亲儿子就是不一样 ^_^)

### 前端框架

上面说过了用做前端JS框架的AngularJS。

这里再说一个我使用的前端CSS框架 —— Bootstrap3。

同样，这个也不用多说，因为在开发者中，Bootstrap2/3已经非常流行了，可以极大的降低前端开发的门槛。

### 展示逻辑

我们已经讨论过首页的展示逻辑。当用户点击首页的一条记录时，我们就要为用户展现一篇节操文章。

节操文章分为两种，一是图片，二是音频。

由于上面说过的dpi差异的原因，我们使用一个相对比较大的新窗口来做展现。于是我们使用``webview``来展示服务器端的新页面。

此时遇到了一个问题，由于服务器端的页面中没有对声音做支持。移动端App中的声音地址是使用Protobuf传输，然后在本地播放的。但是在我们的场景下，获得声音的窗口与展示页面的窗口不是同一个。

对于这个问题的解决方案，我们有两个：

#### 使用回调函数传入参数

``chrome.app.window.create``中可以使用回调函数，传入音频地址。然后新窗口使用``<audio>``标签进行播放。

#### JS注入

由于良心的节操大大的好，在页面中提供了音频的播放地址。

所以我们可以向webview里直接注入一段代码。先是创建一个不可见的``<audio>``标签，然后加入一段js，播放本页面的音频。

## 未来开发打算

节操的页面展示是检查``User-agent``的，对于PC端的页面，所有的推荐链接都是无效的。

如果有可能的话，可以修改``webview``的``User-agent``为Android设备，这样就能有更好的用户体验。

还有前端确实也是比较丑。。。<del>但是你来咬我呀～</del>

最后是我没有Visa卡，所以没法发布这个App。。。所以乃们哪个土豪有开发者账号的，可以把这个App搞走再开发做个发布。也是比较好的～

## 更多的废话

我原来和同学讨论过，有没有可能开发出一个叫``AVM``的东西，把Android应用迁移到PC端来用，这样Linux就不至于什么应用都没有了。但是现在我还没有看到除了超低效率的虚拟机之外的其它解法。

不过Google正在试验一种叫[NaCl](https://developers.google.com/native-client/dev/)的技术，支持一个轻量的虚拟机，运行一个本地应用并能与前端展现交互。

我想，如果有一天，NaCl能统一Android与Chrome平台，成为了智能终端开发的主流，那么平台与平台之间的差异就更小了吧。。。
