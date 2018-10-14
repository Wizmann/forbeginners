Date: 2013-11-29
Title: 機器學習基石 - PLA算法初步
Tags: 公开课, 分类器
Slug: ml-foundations-pla

## 什么是PLA算法

PLA = Perceptrons Learning Alogrithm


WikiPedia上有一个大概的历史背景介绍。

> 感知机（英语：Perceptron）是Frank Rosenblatt在1957年就职于Cornell航空实验室(Cornell Aeronautical Laboratory)时所发明的一种人工神经网络。它可以被视为一种最简单形式的前馈式人工神经网络，是一种二元线性分类器。


## PLA算法的原理

![感知机示意图][1]

> 对于每种输入值(1 - D)，我们计算一个权重。当前神经元的总激发值(a)就等于每种输入值(x)乘以权重(w)之和。

由此我们就可以推导出公式如下。

![neuron sum][2]

我们可以为这个“神经元”的激发值设定一个阈值``threshold``。

如果 ``a > threshold``，则判定输入为正例。
如果 ``a < threshold``，则判定输入为负例。
对于 ``a == threshold``的情况，认为是特殊情况，不予考虑。

所以，我们的感知器分类器就可以得到以下式子。

![perceptron-formula-2][3]

我们在数据向量中加入了阈值，并把式子统一成向量积的形式。

## PLA算法的错误修正

PLA算法是_错误驱动_的算法。

> 当我们训练这个算法时，只要输出值是正确的，这个算法就不会进行任何数据的调整。反之，当输出值与实际值异号，这个算法就会自动调整参数的比重。

![错误修正][4]

我们先取一个随机向量``W``，与现有的数据``X[i]``做点乘，取得结果的符号。

如果符号符合我们的预期的话，则``continue``。
否则就要对``W``进行修正。

修正的方式是``W += y * X[i]``，每一次修正都是减少现有向量``W``与向量``y * X[i]``的夹角，从而调整答案的正确性。

## Naive PLA 与 Pocket PLA

### Naive PLA

Naive PLA算法的思想很简单。一直修正向量``W``，直到向量``W``满足所有数据为止。

代码如下：

```python
from numpy import *

def naive_pla(datas):
    w = datas[0][0]
    iteration = 0
    while True:
        iteration += 1
        false_data = 0

        for data in datas:
            t = dot(w, data[0])
            if sign(data[1]) != sign(t):
                error = data[1]  
                false_data += 1
                w += error * data[0]
        print 'iter%d (%d / %d)' % (iteration, false_data, len(datas))
        if not false_data:
            break
    return w
```

### Pocket PLA

Naive PLA的一大问题就是如果数据有杂音，不能完美的分类的话，算法就不会中止。

所以，对于有杂音的数据，我们只能期望找到错误最少的结果。然后这是一个``NP Hard``问题。

Pocket PLA一个贪心的近似算法。和Naive PLA算法类似。

变顺序迭代为随机迭代，如果找出错误，则修正结果。在修正过程中，记录犯错误最少的向量。

代码如下：

```python
import numpy as np

def pocket_pla(datas, limit):
    ###############
    def _calc_false(vec):
        res = 0
        for data in datas:
            t = np.dot(vec, data[0])
            if np.sign(data[1]) != np.sign(t):
                res += 1
        return res
    ###############
    w = np.random.rand(5)
    least_false = _calc_false(w)
    res = w
    
    for i in xrange(limit):
        data = random.choice(datas)
        t = np.dot(w, data[0])
        if np.sign(data[1]) != np.sign(t):
            t = w + data[1] * data[0]
            t_false = _calc_false(t)
            
            w = t
            
            if t_false <= least_false:
                least_false = t_false
                res = t
    return res, least_false
```

## 参考链接

本文主要参考了[机器学习入门 - 感知器 (Perceptron)][5]和Wikipedia上面[感知机][6]的词条。

以及[機器學習基石 (Machine Learning Foundations)][7]公开课的幻灯片。

## Updated

2013-12-8

修改了pocket-pla算法，提升了效率和准确性。

参考了[课程论坛][8]的讨论。并且感谢Li Tianyi同学指出我的问题。


  [1]: http://wizmann-tk-pic.u.qiniudn.com/blog-perceptron-Ncell.png
  [2]: http://wizmann-tk-pic.u.qiniudn.com/blog-perceptron-formula-1.jpg
  [3]: http://wizmann-tk-pic.u.qiniudn.com/blog-perceptron-formula-2.png
  [4]: http://wizmann-tk-pic.u.qiniudn.com/blog-perceptron-update.png
  [5]: http://shaoxiongjiang.com/2013/03/%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0%E5%85%A5%E9%97%A8-%E6%84%9F%E7%9F%A5%E5%99%A8-perceptron/
  [6]: http://zh.wikipedia.org/wiki/%E6%84%9F%E7%9F%A5%E5%99%A8
  [7]: https://class.coursera.org/ntumlone-001/class
  [8]: https://class.coursera.org/ntumlone-001/forum/thread?thread_id=116#post-632

