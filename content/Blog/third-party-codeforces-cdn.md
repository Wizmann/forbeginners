Date: 2013-12-14
Title: 自己动手搭建第三方的Codeforces CDN
Tags: codeforces, chrome-extension, useless
Slug: third-party-codeforces-cdn

## 啥？

校园网上CF那叫一个卡。

原因是什么呢？ 因为codeforces大量的使用了ajax技术，所以引用了很多js/css文件，并且引用的位置位于页面之前。

这就造成了，我们在上CF的时候，其实页面内容已经读取出来了。但是因为js/css文件没有加载完成，所以页面还是一片空白。

## 解决方案

由于js/css/img文件都是所谓的``静态``文件，那么我们可以缓存这些文件到一个访问速度快的网络上来。

这就是CDN技术。

> CDN的全称是Content Delivery Network，即内容分发网络。其目的是通过在现有的Internet中增加一层新的网络架构，将网站的内容发布到最接近用户的网络“边缘”，使用户可以就近取得所需的内容，提高用户访问网站的响应速度

但是俄罗斯人那边没有做CDN，或者他们的CDN距离天朝实在是太远了。

所以我们只好手动缓存这些静态文件到七牛云上，使用七牛的CDN技术来加速我们的访问了。

[七牛云][1]为个人用户提供了10G存储空间和每月10G流量，这对于我们缓存一个网站的静态文件来说，已经足富裕了。根据我现在的使用状况，所有静态文件加在一起大概在3M左右，搭建这样一个免费CDN可以供十几个人使用。

## 设计架构

我们使用``CS模式``来完成这个网站加速的任务。

Server端当然就是七牛云啦。复杂的任务都交给了工程师们完成，我们只需要声明需要缓存``codeforces.com``的静态文件就可以了。

Client端使用的是Chrome-extension。Chrome-extension使用``webRequest``来“劫持”我们的流量，将其指向我们的七牛云缓存。

## Server端配置

非常简单的操作。设置一个镜像存储就可以了。

![七牛云设置][2]

然后我们记下七牛云为我们分配的域名，以备后用。

## Client端配置

这个稍微复杂一点，不过也是很轻松的。

我们新建一个开发版的chrome-extension。（由于我没有开发者账号，所以一般都是线下开发，放到github上让大家搞的。

写``manifest.json``

```json
{
    "name": "Codeforce CDN加速",
    "version": "0.1",
    "description": "个人性趣所致，不承担任何可能的风险",
    "permissions": [
        "tabs",
        "http://*.codeforces.com/*",
        "http://*.codeforces.ru/*",
        "webRequestBlocking",
        "webRequest"
    ],
    "background":  { "scripts": ["codeforces_cdn.js"] },
        "browser_action":{
        "default_title": "Codeforce CDN加速",
        "default_icon": "icon.png"
    },
    "icons":{
        "16": "icon.png",
        "48": "icon.png",
        "128":"icon.png"
    },
    "manifest_version": 2
}
```

然后写``background.js``，“劫持”发往``work.codeforces.ru``的流量。
```javascript
chrome.webRequest.onBeforeRequest.addListener(
    function(details) {
        console.log(details.url);
        if (details.url.match("http://worker.codeforces.ru")) {
            var url = details.url.replace(
                    "http://worker.codeforces.ru",
                    "http://你的七牛云域名.com");
            return {redirectUrl: url};
        }
    },
    {urls:["http://worker.codeforces.ru/*"]},
    ["blocking"]
);
```
然后安装插件，就可以完美使用了。

根据我的实验，在清空浏览器缓存的情况下。加速前需要3min的页面大概现在只需要不到10s。

## 潜在问题以及不完美的解决方案

由于我们是第三方的山寨CDN，所以当codeforces.com更新它的静态文件时，我们是不知道的。

所以我们需要一个刷新静态文件的机制。但是我们又不能监控文件改变。

最终，我想到的一个不完美的解决方案是定时刷新。

详细来说，就是每周找一个时间，清空我们的缓存。在下一次访问的时候，七牛云会自动替我们刷新所有的静态文件。

七牛云的python-sdk提供了遍历/删除文件的方案（我在里面还找到了一个小小的Bug）。我们只需要定时执行它就可以了。

于是我使用了BAE + bottle.py + niqiu-python-sdk的组合。在BAE上部署了一个bottle.py应用，然后使用``cron``定时执行刷新任务。

## 代码

Github: [戳我][3]

[1]: http://www.qiniu.com/
[2]: http://wizmann-tk-pic.u.qiniudn.com/blog-codeforces-cdn-qiniu-settings.png
[3]: https://github.com/Wizmann/codeforces-cdn
