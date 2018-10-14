Date: 2013-11-28
Title: Linux内核中的少锁链表
Tags: linux, lock-less, 链表, 并发编程
Slug: linux-lockless-llist

# 前言

最近在stackexchange上看到一个问答，讨论我们常用的数据结构与算法在实际工程中的应用。([戳我][1])

我打算借助这个问答中的内容，以我比较熟悉的数据结构与算法为索引来阅读开源代码。

# 正文

## Talk is cheap

> Lock-less NULL terminated single linked list

[linux-2.6/include/linux/llist.h][2]

[linux-2.6/lib/llist.c][3]

## 知识准备

### volatile

> volatile关键字声明的变量或对象通常拥有和优化和（或）多线程相关的特殊属性。

> 通常，volatile关键字用来阻止（伪）编译器对那些它认为变量的值不能“被代码本身”改变的代码上执行任何优化。 

> 如果不使用volatile关键字，编译器将假设当前程序是系统中唯一能改变这个值部分。 为了阻止编译器像上面那样优化代码，需要使用volatile关键字。

> From: http://zh.wikipedia.org/wiki/Volatile%E5%8F%98%E9%87%8F

### typeof

> Another way to refer to the type of an expression is with typeof. The syntax of using of this keyword looks like sizeof, but the construct acts semantically like a type name defined with typedef. 

>From: http://gcc.gnu.org/onlinedocs/gcc/Typeof.html

``typeof``和``sizeof``类似，sizeof求的是变量/类型的大小，而typeof是求变量/类型的**数据类型**。

typeof在#define中的应用很多，例如：

```cpp
#define max(a,b) \
   ({ typeof (a) _a = (a); \
       typeof (b) _b = (b); \
     _a > _b ? _a : _b; })
```
``typeof(a)``获得了``a``的类型，声明了一个同类型的``_a``变量。

p.s. 上面是一个安全的用``#define``实现的``max``函数。

### ACCESS_ONCE

```cpp
#define ACCESS_ONCE(x) (*(volatile typeof(x) *)&(x))；
```
``ACCESS_ONCE``使用了一个类型转换，使用``volatile``修饰 ``x``。避免编译器优化带来的潜在岐义。

### cmpxchg

> compare-and-swap (CAS) is an atomic instruction used in multithreading to achieve synchronization. 

> It compares the contents of a memory location to a given value and, only if they are the same, modifies the contents of that memory location to a given new value. 

> This is done as a single atomic operation. The atomicity guarantees that the new value is calculated based on up-to-date information; if the value had been updated by another thread in the meantime, the write would fail. 

> The result of the operation must indicate whether it performed the substitution; this can be done either with a simple Boolean response (this variant is often called compare-and-set), or by returning the value read from the memory location (not the value written to it).

> ...

> In the x86 (since 80486) and Itanium architectures this is implemented as the compare and exchange (CMPXCHG) instruction, though here the LOCK prefix should be there to make it really atomic.

> From: http://en.wikipedia.org/wiki/Compare-and-swap

``cmpxchg``是在Intel平台上``atomic compare-and-swap``操作的实现。

``cmpxchg``还被用来实现``spinlock``，[戳我][4]。

## Show me the code

### 数据类型

```c
struct llist_head {
        struct llist_node *first;
};

struct llist_node {
        struct llist_node *next;
};
```

一个简单的类型包裹。

``llist_head``是链表头，而``llist_node``是链表中**链**的部分。
### 初始化

```c
#define LLIST_HEAD_INIT(name)        { NULL }
#define LLIST_HEAD(name)        struct llist_head name = LLIST_HEAD_INIT(name)

/**
 * init_llist_head - initialize lock-less list head
 * @head:        the head for your lock-less list
 */
static inline void init_llist_head(struct llist_head *list)
{
        list->first = NULL;
}
```

### 链表的遍历

#### llist_entry

```c
/**
 * llist_entry - get the struct of this entry
 * @ptr:        the &struct llist_node pointer.
 * @type:        the type of the struct this is embedded in.
 * @member:        the name of the llist_node within the struct.
 */
#define llist_entry(ptr, type, member)                \
        container_of(ptr, type, member)
```

声明一个链表时，我们需要把``llist_node``包含在链表节点中，``llist_head``是链表头。

``llist_entry``是从链表节点中的``llist_node``成员变量获得链表节点的地址。

``llist_entry``宏是从``container_of``宏继承而来的。

```c
/**
 * container_of - cast a member of a structure out to the containing structure
 * @ptr:        the pointer to the member.
 * @type:        the type of the container struct this is embedded in.
 * @member:        the name of the member within the struct.
 *
 */
#define container_of(ptr, type, member) ({                        \
        const typeof( ((type *)0)->member ) *__mptr = (ptr);        \
        (type *)( (char *)__mptr - offsetof(type,member) );})
```

具体原理可以小小参考一下[这里][5]。

#### for_each

##### llist_for_each

```c
/**
 * llist_for_each - iterate over some deleted entries of a lock-less list
 * @pos:        the &struct llist_node to use as a loop cursor
 * @node:        the first entry of deleted list entries
 *
 * In general, some entries of the lock-less list can be traversed
 * safely only after being deleted from list, so start with an entry
 * instead of list head.
 *
 * If being used on entries deleted from lock-less list directly, the
 * traverse order is from the newest to the oldest added entry.  If
 * you want to traverse from the oldest to the newest, you must
 * reverse the order by yourself before traversing.
 */
#define llist_for_each(pos, node)                        \
        for ((pos) = (node); pos; (pos) = (pos)->next)
```

一个``for循环``。简单的宏。

##### llist_for_each_entry

```c
/**
 * llist_for_each_entry - iterate over some deleted entries of lock-less list of given type
 * @pos:        the type * to use as a loop cursor.
 * @node:        the fist entry of deleted list entries.
 * @member:        the name of the llist_node with the struct.
 *
 * In general, some entries of the lock-less list can be traversed
 * safely only after being removed from list, so start with an entry
 * instead of list head.
 *
 * If being used on entries deleted from lock-less list directly, the
 * traverse order is from the newest to the oldest added entry.  If
 * you want to traverse from the oldest to the newest, you must
 * reverse the order by yourself before traversing.
 */
#define llist_for_each_entry(pos, node, member)                                \
        for ((pos) = llist_entry((node), typeof(*(pos)), member);        \
             &(pos)->member != NULL;                                        \
             (pos) = llist_entry((pos)->member.next, typeof(*(pos)), member))
```

遍历链表的类。
用伪代码来表述一下就是。

```
for ((pos) = 链表节点;
        &(pos)->next指针 != NULL; 
        (pos) = 链表下一个节点) {
    // 遍历操作
    pos.foo = bar;
}
```


##### llist_for_each_entry_safe

```c
/**
 * llist_for_each_entry_safe - iterate over some deleted entries of lock-less list of given type
 *                               safe against removal of list entry
 * @pos:        the type * to use as a loop cursor.
 * @n:                another type * to use as temporary storage
 * @node:        the first entry of deleted list entries.
 * @member:        the name of the llist_node with the struct.
 *
 * In general, some entries of the lock-less list can be traversed
 * safely only after being removed from list, so start with an entry
 * instead of list head.
 *
 * If being used on entries deleted from lock-less list directly, the
 * traverse order is from the newest to the oldest added entry.  If
 * you want to traverse from the oldest to the newest, you must
 * reverse the order by yourself before traversing.
 */
#define llist_for_each_entry_safe(pos, n, node, member)                               \
        for (pos = llist_entry((node), typeof(*pos), member);                       \
             &pos->member != NULL &&                                               \
                (n = llist_entry(pos->member.next, typeof(*n), member), true); \
             pos = n)
```


``safe``表示单链表中的节点有可能被增加/删除。


使用``(n = llist_entry(pos->member.next, typeof(*n), member), true)``可以保持遍历的安全性。


###### llist_next
```c
static inline struct llist_node *llist_next(struct llist_node *node)
{
        return node->next;
}
```

### 链表元素的操作

##### llist_add_batch

```c
/**
 * llist_add_batch - add several linked entries in batch
 * @new_first:        first entry in batch to be added
 * @new_last:        last entry in batch to be added
 * @head:        the head for your lock-less list
 *
 * Return whether list is empty before adding.
 */
bool llist_add_batch(struct llist_node *new_first, struct llist_node *new_last,
                     struct llist_head *head)
{
        struct llist_node *first;

        do {
                new_last->next = first = ACCESS_ONCE(head->first);
        } while (cmpxchg(&head->first, first, new_first) != first);

        return !first;
}
```

批量增加命令，使用``cmpxchg``保持线程安全。


##### llist_add

```c
/**
 * llist_add - add a new entry
 * @new:        new entry to be added
 * @head:        the head for your lock-less list
 *
 * Returns true if the list was empty prior to adding this entry.
 */
static inline bool llist_add(struct llist_node *new, struct llist_head *head)
{
        return llist_add_batch(new, new, head);
}
```

##### llist_empty

```c
/**
 * llist_empty - tests whether a lock-less list is empty
 * @head:        the list to test
 *
 * Not guaranteed to be accurate or up to date.  Just a quick way to
 * test whether the list is empty without deleting something from the
 * list.
 */
static inline bool llist_empty(const struct llist_head *head)
{
        return ACCESS_ONCE(head->first) == NULL;
}
```
使用``ACCESS_ONCE``避免编译器优化，保持线程安全性。

##### llist_del_all

```c
/**
 * llist_del_all - delete all entries from lock-less list
 * @head:        the head of lock-less list to delete all entries
 *
 * If list is empty, return NULL, otherwise, delete all entries and
 * return the pointer to the first entry.  The order of entries
 * deleted is from the newest to the oldest added one.
 */
static inline struct llist_node *llist_del_all(struct llist_head *head)
{
        return xchg(&head->first, NULL);
}
```

##### llist_del_first

```c
/**
 * llist_del_first - delete the first entry of lock-less list
 * @head:        the head for your lock-less list
 *
 * If list is empty, return NULL, otherwise, return the first entry
 * deleted, this is the newest added one.
 *
 * Only one llist_del_first user can be used simultaneously with
 * multiple llist_add users without lock.  Because otherwise
 * llist_del_first, llist_add, llist_add (or llist_del_all, llist_add,
 * llist_add) sequence in another user may change @head->first->next,
 * but keep @head->first.  If multiple consumers are needed, please
 * use llist_del_all or use lock between consumers.
 */
struct llist_node *llist_del_first(struct llist_head *head)
{
        struct llist_node *entry, *old_entry, *next;

        entry = head->first;
        for (;;) {
                if (entry == NULL)
                        return NULL;
                old_entry = entry;
                next = entry->next;
                entry = cmpxchg(&head->first, old_entry, next);
                if (entry == old_entry)
                        break;
        }

        return entry;
}
```
删除第一个值。同样的无锁操作。

##### llist_reverse_order

```c
/**
 * llist_reverse_order - reverse order of a llist chain
 * @head:        first item of the list to be reversed
 *
 * Reverse the order of a chain of llist entries and return the
 * new first entry.
 */
struct llist_node *llist_reverse_order(struct llist_node *head)
{
        struct llist_node *new_head = NULL;

        while (head) {
                struct llist_node *tmp = head;
                head = head->next;
                tmp->next = new_head;
                new_head = tmp;
        }

        return new_head;
}
EXPORT_SYMBOL_GPL(llist_reverse_order);
```

如何反转一个单链表

## 少锁链表是如何实现的

### add函数中的原子操作

```c
do {
    new_last->next = first = ACCESS_ONCE(head->first);
} while (cmpxchg(&head->first, first, new_first) != first);
```

其中``cmpxchg``的性质类似于锁。保证赋值是成功的且是是原子的。

### del_first中的原子操作

```c
entry = cmpxchg(&head->first, old_entry, next);
```

### del_all中的原子操作
```c
return xchg(&head->first, NULL);
```

### 少锁链表如何处理并发

在llist.h中有如下的注释表明如果两种操作并发执行，是否需要加额外的锁。

```
 /*
 *           |   add    | del_first |  del_all
 * add       |    -     |     -     |     -
 * del_first |          |     L     |     L
 * del_all   |          |           |     -
 */
```

``add``操作和头指针没有关系，所以它可以和其它操作并行。
``del_first``依赖于``list->first->next``在操作时不变化。
而``del_all``只对``list->first``的指针进行操作。所以是可以并行的。

### 少锁链表如何处理遍历

```c
/*
 * The list entries deleted via llist_del_all can be traversed with
 * traversing function such as llist_for_each etc.  But the list
 * entries can not be traversed safely before deleted from the list.
 * The order of deleted entries is from the newest to the oldest added
 * one.  If you want to traverse from the oldest to the newest, you
 * must reverse the order by yourself before traversing.
 */
```

大概意思是说只有从列表上删除下来的元素才可以安全的遍历。（这点理解的不深入）


## 后记

本来是想把这llist的代码看明白的。但是，大概只看懂了60%。。。

以后如果有新的想法，看到了新的东西，也许会有不少有用的update吧。。

[1]: http://cstheory.stackexchange.com/questions/19759/core-algorithms-deployed/19773#19773
[2]: https://github.com/mirrors/linux-2.6/blob/master/include/linux/llist.h
[3]: https://github.com/mirrors/linux-2.6/blob/master/lib/llist.c
[4]: http://stackoverflow.com/questions/6935442/x86-spinlock-using-cmpxchg
[5]: http://hi.baidu.com/holinux/item/af2e32c9dcbd3953ac00ef49
