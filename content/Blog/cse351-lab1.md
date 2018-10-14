Date: 2013-11-27
Title: CSE351 - Lab 1: Manipulating Bits Using C
Tags: CSE351, 公开课
Slug: cse351-lab1

今天做了CSE351 - Lab1，深深的感觉国外的计算机教学爆了我校一条街。

以上是前言。

---

### bitAnd & bitOr

德摩根定理的应用

```cpp
/* 
 * bitAnd - x&y using only ~ and | 
 *   Example: bitAnd(6, 5) = 4
 *   Legal ops: ~ |
 *   Max ops: 8
 *   Rating: 1
 */
int bitAnd(int x, int y) {
  return ~(~x | ~y);
```
```cpp
/* 
 * bitOr - x|y using only ~ and & 
 *   Example: bitOr(6, 5) = 7
 *   Legal ops: ~ &
 *   Max ops: 8
 *   Rating: 1
 */
int bitOr(int x, int y) {
  return ~(~x & ~y);
}
```

### isTmax


因为

``Tmax == INT_MAX == 0x7fff ffff``

=> ``INT_MAX + INT_MAX + 2 == 0``

又因为``-1 == 0xffff ffff``

=> ``-1 + -1 + 2 = 0``

于是我们还要加一条判断是否是-1的逻辑。

```cpp
/*
 * isTmax - returns 1 if x is the maximum, two's complement number,
 *     and 0 otherwise 
 *   Legal ops: ! ~ & ^ | +
 *   Max ops: 10
 *   Rating: 1
 */
int isTmax(int x) {
  return !((x + x + 2) | !(~x));
}
```
### isZero

```cpp
/*
 * isZero - returns 1 if x == 0, and 0 otherwise 
 *   Examples: isZero(5) = 0, isZero(0) = 1
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 2
 *   Rating: 1
 */
int isZero(int x) {
  return !x;
}
```

### fitsBits

```cpp
/* 
 * fitsBits - return 1 if x can be represented as an 
 *  n-bit, two's complement integer.
 *   1 <= n <= 32
 *   Examples: fitsBits(5,3) = 0, fitsBits(-4,3) = 1
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 15
 *   Rating: 2
 */
int fitsBits(int x, int n) {
    int shift = 32 + (~n + 1); // equal to 32 - n
    return !(((x << shift) >> shift) ^ x);
}
```

### getByte
```cpp
/* 
 * getByte - Extract byte n from word x
 *   Bytes numbered from 0 (LSB) to 3 (MSB)
 *   Examples: getByte(0x12345678,1) = 0x56
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 6
 *   Rating: 2
 */
int getByte(int x, int n) {
    return ((x & (0xFF<<(n << 3))) >> (n << 3)) & 0xFF;
}
```

### isNegative
找到符号位

```cpp
/* 
 * isNegative - return 1 if x < 0, return 0 otherwise 
 *   Example: isNegative(-1) = 1.
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 6
 *   Rating: 2
 */
int isNegative(int x) {
    return !!(x & (1 << 31));
}
```

### addOK
如果a和b同号，且a + b与a异号，则不可以加

```cpp
/* 
 * addOK - Determine if can compute x+y without overflow
 *   Example: addOK(0x80000000,0x80000000) = 0,
 *            addOK(0x80000000,0x70000000) = 1, 
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 20
 *   Rating: 3
 */
int addOK(int x, int y) {
    int sum = ((x + y) >> 31) & 1;
    int sx = (x >> 31) & 1;
    int sy = (y >> 31) & 1;
    return  !((!(sx ^ sy)) & (sx ^ sum));
}
```

### isGreater

```cpp
/* 
 * isGreater - if x > y  then return 1, else return 0 
 *   Example: isGreater(4,5) = 0, isGreater(5,4) = 1
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 24
 *   Rating: 3
 */
int isGreater(int x, int y) {
    int sx = (x >> 31) & 1;
    int sy = (y >> 31) & 1;
    int x_minus_y = (x + 1 + ~y);
    int sminus = (((x_minus_y) >> 31) & 1) | !(0 ^ x_minus_y);
    return (!(sx ^ sy) & !sminus) | ((sx ^ sy) & !sx);
}
```
### replaceByte

```cpp
/* 
 * replaceByte(x,n,c) - Replace byte n in x with c
 *   Bytes numbered from 0 (LSB) to 3 (MSB)
 *   Examples: replaceByte(0x12345678,1,0xab) = 0x1234ab78
 *   You can assume 0 <= n <= 3 and 0 <= c <= 255
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 10
 *   Rating: 3
 */
int replaceByte(int x, int n, int c) {
  return (x & (~0 ^ 0xFF << (n << 3))) | (c << (n << 3));
}
```

### rotateLeft

```cpp
/* 
 * rotateLeft - Rotate x to the left by n
 *   Can assume that 0 <= n <= 31
 *   Examples: rotateLeft(0x87654321,4) = 0x76543218
 *   Legal ops: ~ & ^ | + << >>
 *   Max ops: 25
 *   Rating: 3 
 */
int rotateLeft(int x, int n) {
    int mask = ((1 << n) + 1 + ~1) << (33 + ~n);
    int t = ((x & mask) >> (33 + ~n)) & ((1 << n) + 1 + ~1);
    return (x << n) | t;
}
```

### bitCount

这个是从[stackoverflow][1]上找来的答案，很厉害，不过还没看明白为啥。

```cpp
/*
 * bitCount - returns count of number of 1's in word
 *   Examples: bitCount(5) = 2, bitCount(7) = 3
 *   Legal ops: ! ~ & ^ | + << >>
 *   Max ops: 40
 *   Rating: 4
 */
int bitCount(int x) {
    int c = 0;
    c = (x & 0x55555555) + ((x >> 1) & 0x55555555);
    c = (c & 0x33333333) + ((c >> 2) & 0x33333333);
    c = (c & 0x0F0F0F0F) + ((c >> 4) & 0x0F0F0F0F);
    c = (c & 0x00FF00FF) + ((c >> 8) & 0x00FF00FF);
    c = (c & 0x0000FFFF) + ((c >> 16)& 0x0000FFFF);
    return c;
}
```

### isNonZero

``(~x + 1) == -x``

=> ``x | -x``的符号位为负

对于特殊数据``INT_MIN``也可以处理
```cpp
/* 
 * isNonZero - Check whether x is nonzero using
 *              the legal operators except !
 *   Examples: isNonZero(3) = 1, isNonZero(0) = 0
 *   Legal ops: ~ & ^ | + << >>
 *   Max ops: 10
 *   Rating: 4 
 */
int isNonZero(int x) {
    return ((x | (~x + 1)) >> 31) & 1;
}
```


[1]: http://stackoverflow.com/a/3815253/2927439
