Date: 2014-07-26 22:23:34 
Title: 简明Python魔法 - 1
Tags: python
Slug: python-magic-1

## Python中类的实现

在Python的Web框架Django中，Python类的构造特性实现了它大部分的核心功能。

当Python解释器遇到类声明时，会创建一个新的namespace ，并执行其内的所有代码，并将变量注册到这个namespace中。

举例：

```pycon
>>> class Foo(object):
...     print 'Loading...'
...     spam = 'eggs'
...     print 'Done!'
... 
Loading...
Done!
>>> f = Foo()
>>> f.spam
'eggs'
```

### 动态的实现一个类

使用type方法可以动态的代码中实现一个类，接受三个参数“类名”、“基类”、“属性”。

```pycon
>>> Bar = type('Bar', (object,), {'spam': 'eggs'})
>>> Bar.spam
'eggs'
```

### 超类改变一切

“metaprogramming”是指一种在程序运行时创建或改变代码的编程手段。``type``是一个metaclass，一个创建其它类的metaclass。

我们可以替换掉原生的``type``，使用我们自己的版本，从而控制创建类的过程。

```pycon
>>> class MetaClass(type):
...     def __init__(cls, name, bases, attrs):
...         print('Defining %s' % cls)
...         print('Name: %s' % name)
...         print('Bases: %s' % (bases,))
...         print('Attributes:')
...         for (name, value) in attrs.items():
...             print('    %s: %r' % (name, value))
...
>>> class RealClass(object, metaclass=MetaClass):
...     spam = 'eggs'
...
Defining <class '__main__.RealClass'>
Name: RealClass
Bases: (<class 'object'>,)
Attributes:
    spam: 'eggs'
    __module__: '__main__'
    __qualname__: 'RealClass'
>>> RealClass
<class '__main__.RealClass'>
```

每当一个新的类被创建时，都会触发metaclass的行为。

### 基类与超类

基类与超类一起使用可以实现类方法的复用，以及对于类创建的跟踪。


```pycon
 >>> class SubClass(RealClass):  # Notice there's no metaclass here.
...     pass
...
Defining <class '__main__.SubClass'>
Name: SubClass
Bases: (<class '__main__.RealClass'>,)
Attributes:
    __module__: '__main__'
```

在这里，超类对于``SubClass``是完全透明的，``SubClass``只需要完成自己的工作，Python会在后台料理好一切。

### 声明式语法

> This syntax (Declarative Syntax) is designed to make minimize "boilerplate" repetitive syntax and provide elegant, readable code.

声明式语法是一种把数据和逻辑分离的编程方式，面对经常变动的但是规律明显的需求，声明式编程可以解救你于水火之中。:-P

```python
class Contact(models.Model):
    """
    Contact information provided when sending messages to the owner of the site.
    """
    name = models.CharField(max_length=255)
    email = models.EmailField()
```

上面是Django的模型声明语法，简洁、明了、大气！

## 让我们一起做鸭

> Shakespeare: "If it walks like a duck and talks like a duck, it's a Duck." 

### Callables

#### \_\_call\_\_

```pycon
>>> class Multiplier(object):
...     def __init__(self, factor):
...         self.factor = factor
...     def __call__(self, value):
...         return value * self.factor
...
>>> times2 = Multiplier(2)
>>> times2(5)
10
>>> times2(10)
20
>>> times3 = Multiplier(3)
>>> times3(10)
30
```

我们可以使用callable函数来构造”有状态的函数“，以及其它可以想的到的一些黑魔法。

### Dictionaries

使用``__contains``、``__getitem__``和``__setitem__``内建函数，可以让一个类实例模拟字典的行为。

### File

实现``read``、``write``和``close``，你们就可以把我当文件来用啦。

### Iterable

```pycon
>>> class Fibonacci(object):
...     def __init__(self, count):
...         self.count = count
...     def __iter__(self):
...         a, b = 0, 1
...         for x in range(self.count):
...             if x < 2:
...                 yield x
...             else:
...                 c = a + b
...                 yield c
...                 a, b = b, c
...
>>> for x in Fibonacci(5):
...     print(x)
...
0
1
1
2
3
```

## 偏函数

偏函数和函数式编程中的”柯里化“一样，都是通过填充函数中的一部分参数，从而实现一个新的函数。

```pycon
>>> import functools
>>> def add(a, b):
...     return a + b
...
>>> add(4, 2)
6
>>> plus3 = functools.partial(add, 3)
>>> plus5 = functools.partial(add, 5)
>>> plus3(4)
7
>>> plus3(7)
10
>>> plus5(10)
15
```

## 描述符

描述符用来存取类属性，并且可以提供如下的便利：

* 从复杂的对象中取出数据，例如数据库或是配置文件
* 把一个简单的值传入一个复杂对象中
* 对存取的值进行自定义操作
* 把值转化为易于写入数据库中的类型

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

### 实现

覆写类的``__get__``和``__set__``函数就可以实现类的描述符。

## 实践：一个简单的UnitTest框架

### 设计思路

对于每一个Case，只需要声明一个类。在类中声明要测试的函数以及测试的Input和预期Output。之后框架可以运行所有测试用例，并输出结果。

### 接口设计

```python
import PyUnitTest
from PyUnitTest import BaseCase

def func1(a, b):
    return a + b

def func2(a, b):
    return a * b


class TestFunc1(BaseCase):
    FUNC = func1
    INPUT = [{'a': 1, 'b': 2},
             {'a': 2, 'b': 3},
             {'a': 3, 'b': 4}]
    OUTPUT = [3, 5, 8]

class TestFunc2(BaseCase):
    FUNC = func2
    INPUT = [{'a': 1, 'b': 2},
             {'a': 2, 'b': 3},
             {'a': 3, 'b': 4}]
    OUTPUT = [2, 8, 12]

if __name__ == '__main__':
    PyUnitTest.run_all_test()
```

在Case中，使用``FUNC``标明函数，使用``INPUT``和``OUTPUT``标明预期输入输出。

使用``PyUnitTest.run_all_test()``自动运行所有用例。

### CaseContainer

``Case``类获得``Case``名，待测试函数名，输入和输出数据。

并且实现``run()``方法，运行测试用例。

使用``assert``方法保证用例的正确性。

```python
class Case(object):
    def __init__(self, name, attrs):
        self.name = name
        self.in_data = attrs.get('INPUT', None)
        self.out_data = attrs.get('OUTPUT', None)
        self.func = attrs.get('FUNC', None)

        assert(self.in_data)
        assert(self.out_data)
        assert(self.func)
        assert(len(self.in_data) == len(self.out_data))

    def run(self):
        print 'running case: %s ...' % self.name
        data_pair = zip(self.in_data, self.out_data)

        cnt = 0
        ok = 0
        for data_in, data_out in data_pair:
            res = self.func(**data_in)
            cnt += 1
            if data_out == res:
                ok += 1
                print '[PASS %d]...' % cnt
            else:
                print '[FAILED %d]...' % cnt
                print 'INPUT:', repr(data_in)
                print 'OUTPUT:', repr(res)
                print 'EXPECT:', repr(data_out)
        print 'finish case: %s (%d / %d) ...' % (self.name, ok, cnt)
        print '-' * 20
```

CaseContainer类实现了Case的收集。

```python
class CaseContainer(object):
    cases = []
    @classmethod
    def append(self, case):
        self.cases.append(case)
```

### 超类与基类

```python
from CaseContainer import Case, CaseContainer

class MetaCase(type):
    def __init__(cls, name, bases, attrs):
        if name == 'BaseCase':
            return
        
        case = Case(name, attrs)
        CaseContainer.append(case)

class BaseCase(object):
    __metaclass__ = MetaCase
    pass

def run_all_test():
    for case in CaseContainer.cases:
        case.run()
```

超类中，声明Case的收集逻辑。而基类中的``__metaclass__``使所有Case子类的超类皆为``MetaCase``。

最后的``run_all_test``可以批处理所有的test case。

### 后续

这个小的单元测试框架并不完善，只是实现了最基本的测试功能。并且也没有完全应用上面所提到的所有Python的魔法特性。所以后续如果有时间和精力，应该继续完善吧。

## 参考

* [Pro Django](http://book.douban.com/subject/24806569/)
