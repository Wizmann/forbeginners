Date: 2013-12-29 20:23
Title: Codeforces 3C - Tic-tac-toe
Tags: codeforces, algorithm, 算法, 设计模式
Slug: cf-3c-tic-tac-toe


## 啥？
[Tic-tac-toe][1]是我很久之前在CF上做的一道题。非常考细心的模拟题。

最近有同学和我讨论过类似的问题。于是拿出来重新做一遍。练练手。

## 原题做法
没有任何“算法”成分。纯模拟。

又由于数据量实在是太小（3 × 3的矩阵），所以只要是思路正确。代码怎么写都能过。

于是在这里就不赘述。手快的众位10分钟切此题无压力。

## What's new?
如果我们扩展一下这个问题。如果让你设计一个Tic-tac-toe的对战系统（人机对战、人人对战等），你将如何设计？

## the STATE pattern
我们可以看出，这个对战系统其实可以用一个状态机来表示。

![https://github.com/Wizmann/assets/raw/master/wizmann-tk-pic/blog-tick-tac-toe.png][2]

于是我们的对战系统也可以写成一个状态机的模式。

## show me the CODE

首先我们声明一个``State``接口类型。

由于Tic-tac-toe游戏只有两种操作类型：``P1 move``和``P2 move``。

所以我们的接口就很简单。

```cpp
class State {
public:
    State(){}
    int set_game(Game* igame) {
        game = igame;
        return 0;
    }
    virtual int first(int x, int y) = 0;
    virtual int second(int x, int y) = 0;
    virtual void show_state() = 0;
    virtual ~State(){}
protected:
    Game *game;
private:
    State(const State&);
};
```

那么``FirstState``的实现如下：

```cpp
class FirstState: public State {
public:
    virtual int first(int x, int y);
    virtual int second(int x, int y);
    virtual void show_state() {
        print("FirstState");
    }
};

int FirstState::first(int x, int y) {
    int res = game -> make_move(x, y, FIRST);
    if (res == ILLEGAL) {
        game -> set_state(ILLEGAL);
        return ILLEGAL;
    }
    int next = game -> next();
    switch(next) {
        case SECOND:
            game -> set_state(SECOND);
            break;
        case FIRST_WIN:
            game -> set_state(FIRST_WIN);
            break;
        case DRAW:
            game -> set_state(DRAW);
            break;
        default:
            game -> set_state(ILLEGAL);
            break;
    }
    return 0;
}

int FirstState::second(int x, int y) {
    // P2不能操作
    return ILLEGAL;
}
```

同理，``SecondState``的实现：

```cpp
class SecondState: public State {
public:
    virtual int first(int x, int y); 
    virtual int second(int x, int y);
    
    virtual void show_state() {
        print("SecondState");
    }
};

int SecondState::first(int x, int y) {
    // P1不能操作
    return ILLEGAL;
}

int SecondState::second(int x, int y) {
    int res = game -> make_move(x, y, SECOND);
    if (res == ILLEGAL) {
        return ILLEGAL;
    }
    
    int next = game -> next();
    switch(next) {
        case FIRST:
            game -> set_state(FIRST);
            break;
        case SECOND_WIN:
            game -> set_state(SECOND_WIN);
            break;
        case DRAW:
            game -> set_state(DRAW);
            break;
        default:
            game -> set_state(ILLEGAL);
    }
    return 0;
}
```

对于结束状态，因为所有的操作都是非法的。我们可以如下实现：

```cpp
class EndState: public State {
public:
    virtual int first(int x, int y) {
        return ILLEGAL;
    }
    virtual int second(int x,int y) {
        return ILLEGAL;
    }
};

class FirstWinState:  public EndState {
    virtual void show_state() {
        print("FirstWinState");
    }
};
class SecondWinState: public EndState {
    virtual void show_state() {
        print("SecondWinState");
    }
};
class DrawState:      public EndState {
    virtual void show_state() {
        print("DrawState");
    }
};
class IllegalState:   public EndState {
    virtual void show_state() {
        print("IllegalState");
    }
};
```

到这里，状态机里的所有状态我们都已经声明好了。

于是我们开始实现``Game``类。因为是示例代码，所以有的函数都内联了。

```cpp
class Game {
public:
    Game();
    int set_state(int next_state);
    int get_state();
    int make_move(int x, int y, int player);
    int next();
    int first(int x, int y) {
        return state_ptr -> first(x, y);
    }
    int second(int x, int y) {
        return state_ptr -> second(x, y);
    }
private:
    int state;
    State* state_ptr;
    char board[3][3];
    
    FirstState      firststate;
    SecondState     secondstate;
    FirstWinState   firstwinstate ;
    SecondWinState  secondwinstate;
    DrawState       drawstate;
    IllegalState    illegalstate;
};

Game::Game()
{
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            board[i][j] = '.';
        }
    }
    firststate    .set_game((Game*)this);
    secondstate   .set_game((Game*)this);
    firstwinstate .set_game((Game*)this); 
    secondwinstate.set_game((Game*)this);
    drawstate     .set_game((Game*)this);
    illegalstate  .set_game((Game*)this);
    
    // 在开始的时候，要P1先手
    set_state(FIRST);
}

int Game::set_state(int next_state)
{
    state = next_state;
    switch(next_state) {
        case(DRAW):
            state_ptr = &drawstate;
            break;
        case(FIRST):
            state_ptr = &firststate;
            break;
        case(SECOND):
            state_ptr = &secondstate;
            break;
        case(FIRST_WIN):
            state_ptr = &firstwinstate;
            break;
        case(SECOND_WIN):
            state_ptr = &secondwinstate;
            break;
        default:
        case(ILLEGAL):
            state_ptr = &illegalstate;
            break;
    }
    return 0;
}

int Game::get_state() {
    state_ptr ->show_state();
    return state;
}

int Game::make_move(int x, int y, int player) {
    char c;
    switch(player) {
        case FIRST:
            c = 'X';
            break;
        case SECOND:
            c = '0';
            break;
        default:
            return ILLEGAL;
            break;
    }
    if (board[y][x] != '.') {
        return ILLEGAL;
    }
    board[y][x] = c;
    return 0;
}

int Game::next() {
    return judge(board);
}

// 这个函数写的太屎了，不忍直视
void check_win(char board[3][3], int& a_cnt, int& b_cnt)
{
    a_cnt = b_cnt = 0;
    for (int i = 0; i < 3; i++) {
        char type = board[i][0];
        int cnt = 0;
        for (int j = 0; j < 3; j++) {
            if (board[i][j] == type) {
                cnt++;
            } else {
                break;
            }
        }
        
        if (cnt == 3) {
            if (type == 'X') a_cnt++;
            else if (type == '0') b_cnt++;
        }
    }
    
    for (int i = 0; i < 3; i++) {
        char type = board[0][i];
        int cnt = 0;
        for (int j = 0; j < 3; j++) {
            if (board[j][i] == type) {
                cnt++;
            } else {
                break;
            }
        }
        
        if (cnt == 3) {
            if (type == 'X') a_cnt++;
            else if (type == '0') b_cnt++;
        }
    }
    
    do {
        char type = board[0][0];
        int cnt = 0;
        for (int i = 0; i < 3; i++) {
            if (board[i][i] == type) {
                cnt++;
            } else {
                break;
            }
        }
        if (cnt == 3) {
            if (type == 'X') a_cnt++;
            else if (type == '0') b_cnt++;
        }
    } while(0);
        
    do {
        char type = board[0][2];
        int cnt = 0;
        for (int i = 0; i < 3; i++) {
            if (board[2 - i][i] == type) {
                cnt++;
            } else {
                break;
            }
        }
        if (cnt == 3) {
            if (type == 'X') a_cnt++;
            else if (type == '0') b_cnt++;
        }
    } while(0);
}

// 同上。。。模拟题就是那么恶心。。。_(:з」∠)_
// 也许我会有机会重构一下。。。
int judge(char board[3][3])
{
    int next = -1;
    int a_cnt = 0, b_cnt = 0;
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            if (board[i][j] == 'X') a_cnt++;
            else if (board[i][j] == '0') b_cnt++;
        }
    }
    if (a_cnt < b_cnt || a_cnt - b_cnt > 1) {
        return ILLEGAL;
    }

    if (a_cnt + b_cnt == 9) {
        // PASS
    } else if (a_cnt == b_cnt) {
        next = 1;
    } else {
        next = 2;
    }

    a_cnt = b_cnt = 0;
    check_win(board, a_cnt, b_cnt);

    if (a_cnt == 0 && b_cnt == 0) {
        //nobody wins and the board is full
        switch(next) {
            case -1:
                return DRAW;
            case 1:
                return FIRST;
            case 2:
                return SECOND;
        }
    } else if (b_cnt && a_cnt) {
        return ILLEGAL;
    } else if (b_cnt && !a_cnt) {
        if (next == 2) {
            return ILLEGAL;
        } else {
            return SECOND_WIN;
        }
    } else if (a_cnt && !b_cnt) {
        if (next == 1) {
            return ILLEGAL;
        } else {
            return FIRST_WIN;
        }
    } else {
        // NO ELSE HERE;
    }

    return next == 1? FIRST : SECOND;
}

```

最后补上我们的常量声明：

```cpp
const int ILLEGAL = -1;
const int DRAW = 0;
const int FIRST = 1;
const int SECOND = 2;
const int FIRST_WIN = 100;
const int SECOND_WIN = 200;
```

## how it works

> 状态模式： 允许对象在内部状态改变时改变它的行为，对象看起来好象修改了它的类   

``class Game``中的``state_ptr``指针标示了当然自动机的状态。从``class Game``调用``first``和``second``函数的行为被委托给了当前的``State``，产生了不同的动作。

## 为什么要这么写

从上面的代码可以看出，除了那两个写的像屎一样的函数，我们写了好多看起来**无用**的代码。如果用别的方法，我们也许在200行之内就可以完成现有的功能。

但是。。。

> 世界上唯一不变的，就是一切都在变

使用**状态模式**，我们可以轻松的扩展现有的状态。并且，对于类的内部动作有一个良好的封装。

这样，用户在使用我们的状态机时只需要根据需要改变它的状态，并不需要知道它是如何变化的。

例如，[《领域特定语言》][3]一书中，就有使用状态模式构建易于被领域专家理解和使用的DSL。

（p.s. DSL我了解不多，如果理解有偏差，请谅解）

## 参考资料

* [Codeforces 3C - Tic-tac-toe][1]
* [Head First 设计模式][4]

## 代码下载
[云诺网盘 - 戳我][5]

[1]: http://codeforces.com/problemset/problem/3/C
[2]: https://github.com/Wizmann/assets/raw/master/wizmann-tk-pic/blog-tick-tac-toe.png
[3]: http://book.douban.com/subject/21964984/
[4]: http://book.douban.com/subject/2243615/
[5]: https://s.yunio.com/voeWtA
