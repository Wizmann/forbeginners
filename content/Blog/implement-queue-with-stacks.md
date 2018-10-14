Date: 2014-05-20 13:23:03 
Title: How to implement a queue with stack(s)?
Tags: algorithm, stack, queue
Slug: implement-queue-with-stacks

This problem is from the book [_Algorithms, 4th Edition_][1].

> Queue with three stacks. Implement a queue with three stacks so that each queue operation takes a constant (worst-case) number of stack operations. 
>
> Warning : high degree of difficulty.

When I search the Internet to find a solution, I find varieties of this problem, such as "implement a queue with ONE stack", "implement a queue with TWO stack", etc.

It is fun, indeed. I spent the whole morning to finding the solution of these problems. So, let's rock.

## Build a test environment

I choose python as a programming language. 

So firstly, I implement an **ABstract Class**(ABC) of a queue as the template of all classes of queue, called ``QueueTpl``.

```python
import abc

class QueueTpl(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self):
        pass
    
    @abc.abstractmethod
    def clear(self):
        pass
        
    @abc.abstractmethod
    def push(self, value):
        pass
    
    @abc.abstractmethod
    def pop(self, value):
        pass
```

Secondly, I write an **Adapter** for ``Queue.Queue()`` class of python, called ``QueueAdapter``, to make it returns ``None`` when we get items from an empty instance.
And we use ``put_nowait`` and ``get_nowait`` to speed up because there's no need to get the guarantee of **thread safe**.

```python
import Queue

class QueueAdapter(QueueTpl):
    def __init__(self):
        self.clear()
        
    def clear(self):
        self.q = Queue.Queue()
    
    def push(self, value):
        self.q.put_nowait(value)
    
    def pop(self):
        if self.q.empty():
            return None
        return self.q.get_nowait()
```

At last, use ``python unittest`` to verify my solution.

```python
class TestStQueue(unittest.TestCase):
    def test_push_and_pop(self):
        sq = QueueAdapter()
        sq.push(1)
        self.assertEqual(sq.pop(), 1)
        self.assertFalse(sq.pop())
        
        for i in xrange(10):
            sq.push(i)
        for i in xrange(10):
            self.assertEqual(sq.pop(), i)

        self.assertFalse(sq.pop())
    
    def get_rand_command(self):
        cmd = random.choice(['push', 'pop'])
        value = random.randint(0, 1 << 31)
        return cmd, value
    
    def test_brute_force(self):
        step = 10000
        qs = [QueueAdapter(), StQueue3(), StQueue2(), StQueue1()]
        
        for i in xrange(step):
            a, b = self.get_rand_command()
            if a == 'push':
                map(lambda q: q.push(b), qs)
            else:
                rs = map(lambda q: q.pop(), qs)
                self.assertTrue(all(x == rs[0] for x in rs))
```

## Implement a queue with ONE stack

It's said that it's an interview problem of Microsoft.(gossip, perhaps)

The problem asks us to implement a queue with ONLY ONE stack. It seems hard, but it is actually an easy problem.

The ``push`` function is easy, just push the value into the stack. And the ``pop`` function is a little bit hard, but we can do it with recursion to get the first element of the "queue", and put every items else in their origin order in the stack.

The code is short, too.

```python
class StQueue1(QueueTpl):
    def __init__(self):
        self.clear()
    
    def clear(self):
        self.a = []
        
    def push(self, value):
        self.a.append(value)
    
    def pop(self):
        if not self.a:
            return None
            
        if len(self.a) == 1:
            return self.a.pop()
        else:
            v = self.a.pop()
            res = self.pop()
            self.a.append(v)
            return res
```

The time complexity of a ``push`` is O(1) with no extra memory space; a ``pop`` is takes O(n) of time, and O(n) extra memory space in the **stack area**(not the stack).

## Implement a queue with TWO stacks

This problem is so classic and so popular, so I just paste my solution here as everyone knows the answer.

```python
class StQueue2(QueueTpl):
    def __init__(self):
        self.clear()
    
    def clear(self):
        self.a = []
        self.b = []
    
    def push(self, value):
        self.b.append(value)
    
    def pop(self):
        if not self.a:
            while self.b:
                self.a.append(self.b.pop())
        if not self.a:
            return None
        return self.a.pop()
```

## Implement a queue with THREE stacks

As it is said in the book, it's a hard problem. And here is a [discuss][2] in the Stackoverflow where I find this [solution][3].

```
| | | |3| | | |
| | | |_| | | |
| | |_____| | |
| |         | |
| |   |2|   | |
| |   |_|   | |
| |_________| |
|             |
|     |1|     |
|     |_|     |
|_____________|
```

This solution uses nested stacks to perform as a **linked-list**, and use the **linked-list** to perform as a queue.

A queue of "1, 2, 3" looks like this:

```python
[1, 
    [2,
        [3]
    ]
],
```

We use three stack pointers ``stack_a`` ``stack_b`` and ``stack_c``, ``stack_a`` points to the stack which stores the nested stacks, and ``stack_b`` is a pointer to the last stack the nested stack, ``stack_c`` as a temporary stack pointer.

So, ``push`` function is just push the new value in the last stack in the stack which is pointed by pointer ``stack_b``, and then push a new stack in ``stack_b`` and make ``stack_b`` to point to the new stack. (complicated, \<(=*/ω＼*=)>)

The ``pop`` function is to get the first element of the nested stack, just get the first element, and make ``stack_a`` point to the rest of the data.

This code is easy but may hard to understand.

```python
class StQueue3(QueueTpl):
    def __init__(self):
        self.clear()
        
    def clear(self):
        self.a = []
        self.b = self.a
        self.c = None
    
    def push(self, value):
        self.c = [value]
        self.b.append(self.c)
        self.c = []
        self.b.append(self.c)
        self.b = self.c
    
    def pop(self):
        if len(self.a) == 0:
            return None
        self.c = self.a.pop()
        self.a = self.a.pop()
        res = self.a.pop()
        self.a = self.c
        return res
```

## The main function

```python
if __name__ == '__main__':
    unittest.main()
```

## To sum up

![summarize][4]

[1]: http://book.douban.com/subject/19952400/
[2]: http://stackoverflow.com/questions/5538192/how-to-implement-a-queue-with-three-stacks
[3]: http://stackoverflow.com/a/5568094/2927439
[4]: http://wizmann-tk-pic.u.qiniudn.com/blog-queue-with-stack-summary.jpg
