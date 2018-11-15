Date: 2017-07-26
Title: Metaprogramming in .NET 读书笔记 - 1
Tags: Metaprogramming, .NET, C#
Slug: metaprogramming-in-dotnet-1

## 什么是 Metaprogramming (元编程)

![](https://github.com/Wizmann/assets/raw/master/wizmann-pic/17-2-15/1418894-file_1487139497158_1868c.jpg)

元编程从字面上理解就是“能处理程序的程序”。

这里的“处理”，有两个意思。

一是“编写”、“生成”，最经典例子就是编译器，它将我们的所编写的高级语言翻译成机器代码。编译器就像建筑工人，将“蓝图”（高级语言）转化成“高楼大厦”（机器语言）。还有一个我们经常用到的就是“宏”(Macro)。我们可以在代码中使用预先编写好的宏，在编译期，宏会被自动展开成相应的代码。这样的好处是用机器带替人类劳动。

“处理”的另外一个意思就是“处理自己”，元编程让程序在运行时了解自己的状态，并动态的扩展并执行的相应逻辑。

当然，最高级的“处理”就是能完全代替人脑的人工智能。如果那一天到来，我们就距离生活在Matrix里不远了。

## 元编程的实现

元编程主要实现在编译期前后以及运行时。

元编程主要依赖于以下技术：

* 代码生成(code generation)
* 反射(reflection)
* 汇编重写(assembly rewriting)
* 表达式(expression)
* 代码分析(code analysis)

## 代码生成(code generation)

> “拳有定势，而用时则无定势。然当其用也，变无定势，而实不失势”

虽然写代码是一项创造性工作，但是这不意味着对于每一个项目，我们都要从零开始。在软件工程的发展过程中，前人已经为我们总结了一些常用的“最佳实践”(best practise)。在我们的开发工程中，灵活恰当的应用这些“定势”，会大大简化我们的工作，降低人力成本。

“定势”意味着“重复”。而重复工作往往是复杂而易出错的，所以有人提出了DRY原则：Don't Repeat Yourself。代码生成工具则是这个问题的一种解决方案。

对于灵活多变而又遵从定势的代码，使用代码生成可以提高开发速度，降低学习成本和维护成本，使代码维护同一种抽象方法，遵从预先确定的模式，也更方便管理。

### 举一个例子

在C++里，我们可以这样实现一个`max(a, b)`函数：

```cpp
#define max(a, b) ((a) > (b)? (a): (b))
```

当然，有经验的老司机都知道这样写的问题。那么我们换一种方法：

```cpp
template<typename T>
const T& max(const T& a, const T& b) {
    return a > b? a: b;
}
```

这看起来不错，但是在C#里，我们并不能这么做。

比如，我们强行套用C++的语法：

```cs
public T MyMax<T>(T a, T b)
{
    return a > b ? a : b;
}
```

这样的代码会报编译错误，因为不是所有的类型都支持`>`比较操作。进一步说，C++的template展开是编译时进行的，根据不同的模板参数生成不同版本的代码，运行时的逻辑是确定的。而C#的泛型在运行时仍是“泛型”的，所以在编译时，C#编译器需要知道更多的信息来保证运行时的类型安全(type-safe)。

所以我们要给`<T>`加一个限制。一般来说，C#中可以继承`IComparable<T>`接口来实现"比较"(compare)操作。

```cs
public T MyMax<T>(T a, T b) where T: IComparable<T>
{
    return a.CompareTo(b) > 0 ? a : b;
}
```

这样似乎解决了问题，对于实现了`IComparable<T>`接口的类，我们可以使用`MyMax<T>`来取两个元素的最大值。但是，对于只实现了`IComparable`的类，我们仍不能使用`MyMax<T>`函数。

我们可以实现两个不同版本的`MyMax<T>`函数，来匹配`IComparable`和`IComparable<T>`两个不同的接口。但是，我们无法预知一切，假如上游团队使用了一个私有的比较接口，或者直接硬编码了`CompareTo(other)`函数。那么我们该怎么办呢？

### 代码生成的优点

利用代码生成，我们就可以突破编程语言对我们的限制。在上面的例子中，我们可以穷举可能被比较的类型，生成相应的函数重载，实现相应的功能。

当然，我们可以使用语言的一些动态特性来绕过限制，但是动态特性带来的性能损失是不可忽略的。

同时，代码生成可以轻松的生成大段的重复性逻辑代码，比如数据表查询，业务流程等。这是代码生成的不可替代的特长。

### T4模板引擎

T4的全称是“Text Template Transformation Toolkit”。是微软出品的基于模板的文本生成框架，最早在VS2008中被引入。

T4可以使用不同的语言来进行编码，包括C#, VB, F#等，目标格式没有限制。

对于模板引擎，这里就不做过多展开。另外，我最喜欢的引擎是Jinja2。（

### CodeDOM

通常意义上的DOM是用来描述浏览器中展示的元素。CodeDOM和DOM定义类似，是用来描述代码中的结构的。

CodeDOM比一般的模板引擎要更严谨，同时是语言无关的，即支持将一份CodeDOM生成为不同的语言。同时，还支持在运行时动态的生成代码。

CodeDOM的应用很广泛，例如.NET中的表达式树(expression tree，后会中会提到)，以及前文中提到的T4。

下面是一个例子：
```cs
using System;
using System.CodeDom;
using System.CodeDom.Compiler;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.CSharp;
using Microsoft.VisualBasic;

namespace ConsoleApplication5
{
    class Program
    {
        static void Main(string[] args)
        {
            CodeCompileUnit lUnit = new CodeCompileUnit();

            CodeNamespace lNamespace = new CodeNamespace("MyNamespace");
            lNamespace.Imports.Add(new CodeNamespaceImport("System"));
            lNamespace.Imports.Add(new CodeNamespaceImport("System.IO"));
            lUnit.Namespaces.Add(lNamespace);

            CodeTypeDeclaration lClass = new CodeTypeDeclaration("MyClass");
            CodeMethodInvokeExpression lExpression = new CodeMethodInvokeExpression(
                new CodeTypeReferenceExpression("Console"), "WriteLine", new CodePrimitiveExpression("hello world !"));
            lNamespace.Types.Add(lClass);

            CodeEntryPointMethod lMain = new CodeEntryPointMethod();
            lMain.Statements.Add(lExpression);
            lClass.Members.Add(lMain);

            string lDesktopPath = Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory) + @"\";
            CodeGeneratorOptions lOptions = new CodeGeneratorOptions();
            lOptions.IndentString = "    ";
            lOptions.BlankLinesBetweenMembers = true;

            // generate a C# source code file
            CSharpCodeProvider lCSharpCodeProvider = new CSharpCodeProvider();
            using (StreamWriter lStreamWriter = new StreamWriter(lDesktopPath + "HelloWorld.cs", false))
            {
                lCSharpCodeProvider.GenerateCodeFromCompileUnit(lUnit, lStreamWriter, lOptions);
            }

            // generate a VB source code file
            VBCodeProvider lVBCodeProvider = new VBCodeProvider();
            using (StreamWriter lStreamWriter = new StreamWriter(lDesktopPath + "HelloWorld.vb", false))
            {
                lVBCodeProvider.GenerateCodeFromCompileUnit(lUnit, lStreamWriter, lOptions);
            }
        }
    }
}
```

生成的C#代码如下：

```cs
namespace MyNamespace {
    using System;
    using System.IO;
    
    
    public class MyClass {
        
        public static void Main() {
            Console.WriteLine("hello world !");
        }
    }
}
```

生成的VB代码如下：

```vb
Option Strict Off
Option Explicit On

Imports System
Imports System.IO

Namespace MyNamespace
    
    Public Class [MyClass]
        
        Public Shared Sub Main()
            Console.WriteLine("hello world !")
        End Sub
    End Class
End Namespace

```

我们可以看出，与模板引擎相比，CodeDOM更复杂，也更不直观。但是由于它的语言无关性，非常适合用来生成一些工具代码，比如SDK等。

## What's next?

由于.NET元编程是一个比较大的话题，所以读书笔记写会做成一个小系列一篇一篇发出。

下一篇我们会更进步，讨论IL级别的代码生成。


## 一些测试代码

* [`max(a, b)` function with template in C++][1]
* [Generate code with CodeDOM][4]

## 参考链接

* [How do C# generics compare to C++ templates?][2]
* [What is type safety?][3]
* [Reflection (part 5, professional), CodeDOM (& lambda expression tree)][5]

[1]: http://code.wizmann.tk/Home/Code?guid=81cb583a-2498-4f2a-8eff-b17a1af9b5e5
[2]: https://blogs.msdn.microsoft.com/csharpfaq/2004/03/12/how-do-c-generics-compare-to-c-templates/
[3]: http://www.pl-enthusiast.net/2014/08/05/type-safety/
[4]: http://code.wizmann.tk/Home/Code?guid=1a30e464-c08c-45bd-b9ca-da2675de19df
[5]: https://csharphardcoreprogramming.wordpress.com/tag/codedom/

