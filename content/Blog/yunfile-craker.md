Date: 2013-12-02 21:16
Title: Yunfile下载破解[废弃]
Tags: 创造力, Yunfile, Chrome-Extension
Slug: yunfile-cracker


## 废弃原因

因为Yunfile现在开始限IP + 无限抽风，所以插件已经废弃不用了。现在也没找到解决方法。\o<(=╯□╰=)>o

## 啥？

大家都知道``Yunfile``是做什么的咩？反正我是不知道。。。

今天下午无聊，写了一个yunfile下载的破解插件。

## 功能：

* 非会员跳过下载等待的30s（或者更长时间）

* 下载页面不会报“因长时间未操作，需要重新下载”的错误

这里感谢**luacloud**的[博文][1]，为插件的编写提供了原型。

## 具体功能实现：

### 跳过等待

在上面引用的博文里面有说，就是强制执行页面中的js，实现跳转。

还做了一个DOM修改，变成现在这种很漂漂的样子～～

![Yunfile-Craker-1][2]

### 忽略超时错误

覆盖了下载函数，跳过超时判断。

## 现有问题

在一些情况下，点击下载按钮会返回到下载页。

虽然我们不需要再等30s了，但是还是很烦。

也有我有机会修复这个问题。

### 代码

代码在[这里][3]呀～


[1]: http://www.luacloud.com/2012/crack-yunfile-network-disk-30-wait-for-restrictions.html

[2]: https://github.com/Wizmann/assets/raw/master/wizmann-tk-pic/yunfile-craker-1.png

[3]: https://github.com/Wizmann/Utils/tree/master/Chrome-extension/yunfile-cracker
