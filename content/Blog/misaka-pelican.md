Date: 2014-01-09 14:55
Title: 用Misaka做为pelican的Markdown解析器
Tags: markdown, misaka, pelican, 糙快猛, metadata
Slug: misaka-pelican


## 为啥？

Pelican内置[python-markdown][1]做为默认解析器，用来将用户的``Markdown``格式的文章转为网页格式展示。

**然而**，``python-markdown``模块的解析逻辑有严重的Bug。例如一个``未标明语言的代码块``会被标出很多莫名奇妙的错误；还有``C++``中的指针符号``*``会被解析为斜体的符号``*SomeText*``，在代码块中会产生大量和语法高亮无关的斜体字。

在网上寻找了很久的答案，终于找到了一篇[日文博客][2]，其中讲到了使用[misaka][3]来替换``python-markdown``来解析日志。

## 两难的Metadata

我使用了上文提到的日志中的方法来替换解析器，效果拔群，日志中的解析问题完全解决了。但是日志中的``Metadata``并没有被隐藏，而是显示在了日志的最前面，非常影响心情（强迫症？）。

于是我分析了解析模块的代码。原来的解析模块使用了``python-markdown``的一个处理``Metadata``的[扩展][4]，用来解析``Metadata``，并从正文中删除这一部分。

但是``Misaka``并不支持这种语法，同时也没有处理``Metadata``的插件。

于是我想可不可以把这两种``Markdown``解析器的长处合并一下，从而实现最终的目标。

## 小小的改动
编辑``pelican``的``readers.py``文件。

（我是直接改的``/usr/local/lib/python2.7/dist-packages/pelican``下的文件，不太优雅，不过这个改动也是非常Dirty的，只是用来解决问题）

首先引用``Misaka``

```python
try:
    from markdown import Markdown
    import misaka
    import pygments
except ImportError:
    Markdown = False  # NOQA
```

再修改``class MarkdownReader``，改变解析逻辑

```python
    def read(self, source_path):
        """Parse content and metadata of markdown files"""

        #提取Metadata
        self._md = Markdown(extensions=self.extensions)
        with pelican_open(source_path) as text:
            content = self._md.convert(text)

        metadata = self._parse_metadata(self._md.Meta)

        #自定义Misaka解析器
        renderer = self.BleepRenderer()
        misaka_md = misaka.Markdown(renderer,
            extensions=misaka.EXT_FENCED_CODE | misaka.EXT_NO_INTRA_EMPHASIS)
        misaka_content = misaka_md.render(text)

        return misaka_content, metadata
```

然后我们写一个自定义的``Misaka``解析器，用来去除``Metadata``信息

这段代码是基于上文说的那篇日志和``Misaka``的官方文档，有问题的话可以去查阅。

```python
class BleepRenderer(misaka.HtmlRenderer, misaka.SmartyPants):
    #预处理函数
    def preprocess(self, text):
        #使用一个FakeClass来骗过对象元素的检查
        #同时我们只是删除Metadata，并不使用它，所以这样的修改是可以接受的
        class FakeClass(object):
            def __init__(self):
                self.Meta = None
        #调用Markdown的插件来处理Metadata
        import markdown
        mp = markdown.extensions.meta.MetaPreprocessor()
        mp.markdown = FakeClass()
        lines = mp.run(text.split('\n'))
        return '\n'.join(lines)
    
    #告诉Misaka如何处理代码，使用pygments进行高亮处理
    def block_code(self, text, lang):
        if not lang:
            return '\n<pre><code>%s</code></pre>\n' % escape(text.strip())
        lexer = pygments.lexers.get_lexer_by_name(lang, stripall=True)
        formatter = pygments.formatters.HtmlFormatter()
        return pygments.highlight(text, lexer, formatter)
```

## 结语

这个修改真TMD**糙快猛**啊！

## 文件下载

修改好的``readers.py``文件：
[戳我][5]



[1]: http://pythonhosted.org/Markdown/
[2]: http://qiita.com/5t111111/items/4614b207f3942d05e55c
[3]: http://misaka.61924.nl/
[4]: https://github.com/waylan/Python-Markdown/blob/master/markdown/extensions/meta.py
[5]: https://s.yunio.com/_Lt!Lb