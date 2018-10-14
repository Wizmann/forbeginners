Date: 2013-11-25
Title: 使用pip和virtuanenv
Tags: python
Slug: using-pip-and-virtualenv

让我们从一个无聊的小段子开始。

> "What’s pip?"

> "A python package manager"

> "How do I install it?"

> "easy_install pip"

> "What’s easy_install?"

> "A python package manager"

pip和easy_install都是python的包管理工具，类似于ruby的gem以及nodejs的npm。

而pip是easy_install的升级版，在这个[页面][1]中提到了pip对于easy_install的升级。其中提到了一点非常重要。

> pip is complementary with virtualenv, and it is encouraged that you use virtualenv to isolate your installation.

如果有同学不熟悉virtualenv，这里是一个小小的介绍。（以下翻译来自：[戳我][2]）

> virtualenv 是一个创建隔离的Python环境的工具。

> virtualenv要解决的根本问题是库的版本和依赖，以及权限问题。假设你有一个程序，需要LibFoo的版本1，而另一个程序需要版本2，如何同时使用两个应用程序呢？如果将所有的库都安装在 /usr/lib/python2.7/site-packages（或者你的系统的标准包安装路径），非常容易出现将不该升级的库升级的问题。

> 另外，在一台共享的机器上，如果没有全局的 site-packages 目录的权限（例如一个共享的主机），如何安装Python库呢？

> 在这些情况下，就是该用到virtualenv的地方。它能够创建一个自己的安装目录，形成一个独立的环境，不会影响其他的virtualenv环境，甚至可以不受全局的site-packages当中安装的包的影响


由于virtualenv的以上优点。我们使用pip与virtualenv配合，可以很轻松保证线上线下运行环境一致，实现自动化部署。

举一个例子。

在线下开发时，我们使用``virtualenv env``创建一个Python虚拟环境。并使用``source env/bin/activate``激活。

然后我们可以在这个虚拟环境中安装我们需要的包。此时我们的环境与全局完全隔离，所有Python运行环境只以来于现有的虚拟环境。

在部署服务时，拷贝整个虚拟环境必然是不明智的选择。我们使用``pip freeze > requirements.txt``将本环境的依赖写入``requirements.txt``文件。

然后在线上新建``env_online``，激活之。并调用``pip install -r requirements.txt``，此时线上服务器会下载所有依赖包。在安装结束后，我们就克隆了线下的环境。

当然，如果线上服务器没有连接外网。我们可以使用离线方法安装需要的包。

``pip bundle env.pybundle -r requirements.txt``会重新下载所有依赖的包，并写入``env.pybundle``。然后我们将其上传到线上，使用``pip install env.pybundle``安装即可。


以上是pip和virtualenv配合使用一些技巧。参考自：[戳我][3]。

[1]: http://www.pip-installer.org/en/1.0.2/#pip-compared-to-easy-install
[2]: http://blogs.360.cn/blog/how-360-uses-python-1-virtualenv/
[3]: http://blog.csdn.net/tulip527/article/details/8478093
