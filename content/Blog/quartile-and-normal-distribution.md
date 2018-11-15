Date: 2014-03-09 22:44:15
Title: Quartile and Normal Distribution
Tags: quartile, normal-distribution
Slug: quartile-and-normal-distribution

## What is Quartile?

Quartile is a concept of descriptive statics. The quartiles of a ranked data set are the three points that divide the data set into four equal groups, each group comprising a quarter of data.

## Definitions

### first quartile (Q1)

First quartile, also known as lower quartile, splits off the lowest 25% of data.

### second quartile (Q2)

Second quartile is the median of the data set, cuts data set in half.

### third quartile (Q3)

Third quartile, known as upper quartile, splits off the highest 25% data.

The different between *Q1* and *Q3* is called the InterQuartile Range(IQR).

## Box-and-Whisker-plot and Quartile

A box-and-whisker-plot is a convenient way of graphically depicting groups of numerical data through their quartiles.

The buttom and top of the box is always Q1 and Q3, and the band in the box is always Q2(the median). And the ends of the whiskers can be presented in several different ways.

## Tukey Boxplot

Tukey boxplot defines two type of whiskers, which are called *inner fence* and *outer fence*. The value of *inner fence* is ``Q1 - 1.5 * IQR`` and ``Q3 + 1.5 * IQR``. At the same time, the value of *outer fence* is ``Q1 + 3 * IQR`` and ``Q3 + 3 * IQR``.

The data outside the fence is called the *suspected outliers* and *outliners*.

If the data happens to be normally distributed, ``IQR = 1.35σ``. It means that only 0.52% of the set of data should be out of the *inner fence* and  hardly any of the data should be out of the *outer fence*. As a result, if a data is considered as a *outliners*, it is largely an exception.

![Boxplot and Normal Distribution](https://github.com/Wizmann/assets/raw/master/wizmann-tk-pic/Boxplot.png)

## Reference

* [Box plot - Wikipedia](https://en.wikipedia.org/wiki/Boxplot)
* [Box Plot: Display of Distribution](http://www.physics.csbsju.edu/stats/box2.html)
* [Tables for statistical distributions](http://www.wasu.com.cn/fwyzc/wasubzhzl/201207/P020140102519718744101.pdf)
