Date: 2014-07-27 14:23:10 
Title: 简明Python魔法 - 2
Tags: python
Slug: python-magic-2

## 再说描述符 - Descriptor

### 最简单的描述符

覆写类的``__get__``和``__setter__``函数就可以实现一个简单的描述符。对某个类型实例的读写进行额外的控制。

```pycon
>>> import datetime
>>> class CurrentDate(object):
...     def __get__(self, instance, owner):
...         return datetime.date.today()
...     def __set__(self, instance, value):
...         raise NotImplementedError("Can't change the current date.")
...
>>> class Example(object):
...     date = CurrentDate()
...
>>> e = Example()
>>> e.date
datetime.date(2008, 11, 24)
>>> e.date = datetime.date.today()
Traceback (most recent call last):
  ...
NotImplementedError: Can't change the current date.
```

### 类属性描述符

```python
class MyClass (object):
    __var = None

    def _set_var (self, value):
        type (self).__var = value

    def _get_var (self):
        return self.__var

    var = property (_get_var, _set_var)

a = MyClass ()
b = MyClass ()
a.var = "foo"
print b.var

```

我们可以使用上面的方法，包装一个类属性描述符。对类属性进行操作。

### 对资源进行封装

在Django中，可以使用pickle在数据库中存储一些序列化信息，如列表、字典等（这些字段都不是原子的）。

我们可以选择继承``models.TextField``来实现我们的``PickleField``。

```python
class PickleField(models.TextField):
    def pickle(self, obj):
        return pickle.dumps(obj)
    
    def unpickle(self, data):
        return pickle.loads(str(data))
    
    def get_attname(self):
        return '%s_pickled' % self.name
    
    def get_db_prep_lookup(self, lookup_type, value):
        '''
        禁止使用pickled字段进行查询
        '''
        raise ValueError("Con't make comparisons against pickled data.")
```

以上实现的是最简单的PickleField，用户在使用这个类型的字段时，需要手动对数据进行pickle/unpickle。

我们使用property，实现一个PickleDescriptor描述符：

```python
class PickleDescriptor(property):
    def __init__(self, field):
        self.field = field
 
    def __get__(self, instance, owner):
        if instance is None:
           return self
 
        if self.field.name not in instance.__dict__:
           # The object hasn't been created yet, so unpickle the data
           raw_data = getattr(instance, self.field.attname)
           instance.__dict__[self.field.name] = self.field.unpickle(raw_data)
 
        return instance.__dict__[self.field.name]
 
    def __set__(self, instance, value):
        instance.__dict__[self.field.name] = value
        setattr(instance, self.field.attname, self.field.pickle(value))
```

这个描述符的作用是封装PickleField的get/set操作。对于get，当字段未被反序列化时，调用unpickled，其它时候直接读取字段。对于set，则是同时更新字段以及pickled字段。实现了一个类似cache的机制。

最后，我们再为``PickleField``加上一个``contribute_to_class``回调。

```python
    def contribute_to_class(self, cls, name):
        super(PickleField, self).contribute_to_class(cls, name)
        setattr(cls, name, PickleDescriptor(self))
```

当这个字段被加入数据模型的时候，自动把对字段的字义替换为该描述符。（太漂亮！）

## 后记

在做毕设的时候，提前读了_Pro Django_一书，真心让我少走了不少弯路。在导师最后一天改需求的时候，还可以从容不迫的见招拆招。这真的得感谢Python超强的弹性，以及Django完美的设计哲学。

_Pro Django_的部分到这里基本就结束了，此书后面的章节大都是Django相关的，对于Python的讲解被淡化了。

本系列后面的文章还是会从声明式编程以及类DSL编程的角度出发，对于Python的魔法进行学习。

## 参考

* [Pro Django](http://book.douban.com/subject/3086812/)
