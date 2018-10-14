Date: 2014-04-07 21:08:59 
Title: "alloca" vs "placement new"
Tags: cpp, memory, stack, heap, allocate, alloca, c++
Slug: alloca-vs-placement-new

## WHAT?!

For most time, we use ``malloc`` or ``new`` for memory allocation, which will get it on *heap*.

However, access memory on *heap* is not as effective as the memory on *stack*, because the heap is "free-floating region of memory". To the contrary, memory on *stack* is managed by CPU automacitally and tightly. As a result, the further of the *stack* compared to *heap* is that we can have a faster read/write speed due to the fact that *stack* memory is more likely to optimized by **CPU cache**, in addition, it only uses a single instruction to allocate or deallocate *stack* memory. Just like this.

```cpp
sub esp, 0x10; => allocate
add esp, 0x10; => deallocate
```


## alloca

The ``alloca()`` function allocates memory from the *stack*.

```cpp
int *p = (int*)alloca(sizeof(int) * size);
```

It's quite the same as the ``malloc`` way. But we shouldn't free the memory allocated on the *stack*; these memory will be automatically deallocated when you leave the function(**not the code block**).

## placement new

The placement new is one of the overloads of the ``new`` functions; this new syntax can do something as the ``alloca()`` function.

```cpp
char buffer[1024];
int *p = new(buffer) int[64];
```

The placement new can be also used in some other scenarios but won't be mentioned here.

## variable-length array
C90 and C++ both support the variable-length array which will be allocated on *stack*, and it will be deallocted whhen you leave the **clode block**, such as "if", "while", etc.

This is much simplified, but be ware if you use both variable-length array and ``alloca()`` in the same function, the deallocation of the array will also free anything more recenly allocated by alloca.

## Defects

*Stack* has its limitation. If the allocation on *stack* causes **stack overflow** error, then the behavior of the program is undefined.

Further, the variable-length array and ``alloca()`` are not included in *ANSI-C* standard and therefore could limit portability.

The Google C++ style guide encourage developers to use ``scoped_ptr`` or ``scopted_array`` instead of variable-length array and ``alloca()``.

## Some experiment

```cpp
// compile with: g++ -std=c++0x -O2 -Wall -g -o "foo.cc" "foo"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <algorithm>

using namespace std;

#define print(x) cout << x << endl
#define input(x) cin >> x

#if defined(__i386__)
static __inline__ unsigned long long rdtsc(void)
{
    unsigned long long int x;
    __asm__ volatile (".byte 0x0f, 0x31" : "=A" (x));
    return x;
}
#elif defined(__x86_64__)
static __inline__ unsigned long long rdtsc(void)
{
    unsigned hi, lo;
    __asm__ __volatile__ ("rdtsc" : "=a"(lo), "=d"(hi));
    return ( (unsigned long long)lo)|( ((unsigned long long)hi)<<32 );
}
#endif


//#define MEMORY_ON_HEAP
//#define MEMORY_ON_STACK

const int SIZE = 102400;
int *array[SIZE] = {NULL};

int main()
{
    unsigned long long start = rdtsc();
    
    #ifdef MEMORY_ON_HEAP // RDSTC: 20586280
    for (int i = 0; i < SIZE; i++) {
        array[i] = (int*)malloc(sizeof(int));
        *array[i] = i;
    }
    #endif
    
    #ifdef MEMORY_ON_STACK // RDSTC: 3660502
    for (int i = 0; i < SIZE; i++) {
        array[i] = (int*)alloca(sizeof(int));
        *array[i] = i;
    }
    #endif
    

    unsigned long long end = rdtsc();
    print(end - start);
    return 0;
}

```

You can use ``info register esp`` in gdb to inspect the *stack* pointer before and after you call the allocation function or declare a variable-length array.
