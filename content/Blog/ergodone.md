Date: 2016-10-05 21:38:58
Title: 打造你的专属键盘 — ErgoDone
Tags: ot, ergodone, keyboard
Slug: ergodone

## 写在前面

> 低能预警：这是最没有技术含量的一篇博客，无关人员可以撤离。

> 部分图片来自网络，侵删

这个十一假期，亲手DIY了一把键盘。当然，我只搞定了焊接部分，把不同的组件拼在了一起。

在焊接的过程中，也学习到了一些新知识。写在这里，记录下来。


## ErgoDone介绍

ErgoDone是著名开源硬件ErgoDox的中国特色版本，精简了一些硬件以控制成本。总体价格在500RMB左右，是工薪阶级装逼界的一颗新星。

Ergodox的一个版本：
![](http://wizmann-pic.qiniudn.com/16-10-2/41980975.jpg)

ErgoDone明显就屌丝了许多：

![](http://wizmann-pic.qiniudn.com/16-10-5/28663395.jpg)

## 键盘主控

![](http://wizmann-pic.qiniudn.com/16-10-2/32662639.jpg)

ErgoDone使用了Arduino pro micro做为主控，基中使用了mega32u4做为芯片，提供了模拟USB输入设备的相关函数（包括键盘、鼠标）。网上有许多现成的范例，用这款芯片（以及另一版使用mega32u4的Arduino开发版，Arduino Leonardo）制作体感鼠标（搭配陀螺仪）、游戏摇杆（搭配相关硬件）以及各种专用输入设备。

Arduino pro micro淘宝价不到20块钱，相对来说算是非常超值了。

## 焊接

由于本人算是菜的抠脚的业余选手，在这个键盘上的主要工作就是焊接。然而，就在焊接这样一件相对简单的工作上，我也是踩了不少坑。

### MiniUSB转MicroUSB

在ErgoDone的设计中，整块键盘的供电，都是通过MiniUSB线来完成的。然而，pro micro的接口是MicroUSB的，这里我们需要一个转换工作。

![](http://wizmann-pic.qiniudn.com/16-10-2/388124.jpg)

MiniUSB，俗称T口USB。其中有五颗线，代表供电，D+，D-，ID与接地。

MicroUSB就是现在市面上绝大多数安卓手机的充电/数据接口。其中的线序与MiniUSB中的类似，只是多数情况下，我们不使用ID线。

在焊接键盘的过程中，我们需要完成一个自制MicroUSB接口，把导线连接到MicroUSB头上去。这个任务相对难度高一些，不过我们也有偷懒的方式。

因为MicroUSB线实在过于流行，现在无论谁手里都会有那么两三条。那么我们可以拆掉手机充电线的MicroUSB公头，把其中的线引出来，连到应该连的位置上，就可以正常的使用了。

如果你的MicroUSB线是良心厂家出产的话，其中会有四颗线：红绿白黑。

* 红：供电，5V
* 绿：Data+
* 白：Data-
* 黑：接地

在ErgoDone这里，我们不需要接地线也可以正常工作。然后在焊接的时候要注意线不要留的过长，否则会很难看（不要问我为什么知道）。

### 一些打磨工作

ErgoDone的两片键盘是通过3.5mm的音频线连接的，然后音频接口不出意料的比外壳预留的接口要厚一些。所以一些打磨工作是必须的。

这里推荐打磨神器 —— 磨刀石。好的磨刀石有粗细两面，方便控制粒度，同时打磨的效率也比较高。如果真的啥都没有，可以强行试一波指甲钳上面的小挫。

### 卫星轴的安装

可以参考[这篇帖子](http://tieba.baidu.com/p/3703634467)，上面已经说的很好了，我就不重复了。记得重要的一点是要把钢丝入扣，否则可能会卡键什么的。情况允许，还可以加一点润滑脂，让摩擦力小一点。

### 焊轴

焊轴相对是最简单的一步了，因为焊点的距离足够远，而且也足够大。只是注意别在焊盘上停留太多时间，把焊盘弄掉了就好。

### 飞线与TDD

这两个放在一起写的原因是因为这两个技术都需要一样工具 —— 万用表。当然这里只是用来测连通性的，所以如果你愿意折腾，自己用发光二级管自己搞一把也不是不可以。

如果我们操作不当，不小心把焊盘搞下来了，有什么方法可以补救呢。答案是飞线，就是不借助电路板上的电路，而是显式的用导线来导通某两个或多个管脚。

ErgoDone由于是对称的两块，所以在焊崩了之后，可以依样找一个可用的焊盘来找可以飞线的焊点。如果手里只有一块板子而且情况不允许的话，就只好在焊之前，尤其是比较高难度的操作之前，先留好plan B，想想万一搞砸了有没有回滚方案（蛤）。

TDD，又称测试驱动开发。就是在焊完一部分之后，立刻进行测试。比如集成电路或者主控，在焊完之后，一定要用万用表确认一下是不是有相临管脚短路的情况。在二极管焊完之后，用镊子测试一下是否可以触发相应的按键。

一个半成品：

![](http://wizmann-pic.qiniudn.com/16-10-2/35993621.jpg)

## 对键盘编程

这种DIY键盘的一大好处就是可以自定义配列，通过Fn键做一些很fancy的事情。比如触发组合键，或者是录制一些宏。对于程序员和一些游戏玩家来说，这个功能是非常吸引人的。

### 我的配列

默认层：http://www.keyboard-layout-editor.com/#/gists/a9278a768f78adf9d7b019b883678390

![](http://wizmann-pic.qiniudn.com/16-10-5/11486899.jpg)

Fn层：http://www.keyboard-layout-editor.com/#/gists/79ad8e6c4ac70cfad1ed400355e960a7

右手的那堆Fn对应着0~9上面的符号

![](http://wizmann-pic.qiniudn.com/16-10-5/90976851.jpg)

Vim层：http://www.keyboard-layout-editor.com/#/gists/950dc52b3b27c24601661f2fd43a6d69

模仿vim/bash映射了一些快捷键

![](http://wizmann-pic.qiniudn.com/16-10-5/92544582.jpg)

魔改层：http://www.keyboard-layout-editor.com/#/gists/8bb13d2439c542a06d99e17fca3a234b

用来魔改/创造一些不存在的键位和组合

![](http://wizmann-pic.qiniudn.com/16-10-5/28220231.jpg)

食指多出来的四个键分别对应着四种括号`<>(){}[]`。在编程中会比较常用到。

### 魔改举例

在食指的扩充键位中，我设计了一个不存在的键位组合：`<(`和`>)`。即在默认状态下，输入`()`；在Shift状态下，输入`<>`。这种设计并没有直接的解决方案。对于圆括号的输入，我们可以使用组合键宏。而Shift输入尖括号，则需要一些技巧。

幸好之前已经有人提出并解决了[类似的问题](https://github.com/tmk/tmk_keyboard/wiki/FAQ-Keymap#esc-and--on-a-key)。简而言之，就是将Shift改成“Fn+Shift”，在按下Shift的同时，切换到一个新的层上。新的层上，我们可以用组合键宏输入尖括号。而剩下的键位，我们将其设置为透明。当你按下其它的键时，与平时按下Shift没有区别。

## 最终的代码

```cpp
// Generated by TKG at 2016-10-05 22:35:43

#include "keymap_common.h"

#define KEYMAP_TKG( \
    K0A, K0B, K0C, K0D, K0E, K0F, K0G, K0H, K0I, K0J, K0K, K0L, K0M, K0N, \
    K1A, K1B, K1C, K1D, K1E, K1F, K1G, K1H, K1I, K1J, K1K, K1L, K1M, K1N, \
    K2A, K2B, K2C, K2D, K2E, K2F,           K2I, K2J, K2K, K2L, K2M, K2N, \
    K3A, K3B, K3C, K3D, K3E, K3F, K3G, K3H, K3I, K3J, K3K, K3L, K3M, K3N, \
    K4A, K4B, K4C, K4D, K4E,                     K4J, K4K, K4L, K4M, K4N, \
         K5B, K5C, K5D, K5E, K5F, K5G, K5H, K5I, K5J, K5K, K5L, K5M  \
) { \
    { KC_##K0A, KC_##K0B, KC_##K0C, KC_##K0D, KC_##K0E, KC_##K0F, KC_##K0G, KC_##K0H, KC_##K0I, KC_##K0J, KC_##K0K, KC_##K0L, KC_##K0M, KC_##K0N }, \
    { KC_##K1A, KC_##K1B, KC_##K1C, KC_##K1D, KC_##K1E, KC_##K1F, KC_##K1G, KC_##K1H, KC_##K1I, KC_##K1J, KC_##K1K, KC_##K1L, KC_##K1M, KC_##K1N }, \
    { KC_##K2A, KC_##K2B, KC_##K2C, KC_##K2D, KC_##K2E, KC_##K2F, KC_NO,    KC_NO,    KC_##K2I, KC_##K2J, KC_##K2K, KC_##K2L, KC_##K2M, KC_##K2N }, \
    { KC_##K3A, KC_##K3B, KC_##K3C, KC_##K3D, KC_##K3E, KC_##K3F, KC_##K3G, KC_##K3H, KC_##K3I, KC_##K3J, KC_##K3K, KC_##K3L, KC_##K3M, KC_##K3N }, \
    { KC_##K4A, KC_##K4B, KC_##K4C, KC_##K4D, KC_##K4E, KC_NO,    KC_NO,    KC_NO,    KC_NO,    KC_##K4J, KC_##K4K, KC_##K4L, KC_##K4M, KC_##K4N }, \
    { KC_NO,    KC_##K5B, KC_##K5C, KC_##K5D, KC_##K5E, KC_##K5F, KC_##K5G, KC_##K5H, KC_##K5I, KC_##K5J, KC_##K5K, KC_##K5L, KC_##K5M, KC_NO    }  \
}

#ifdef KEYMAP_SECTION_ENABLE
const uint8_t keymaps[][MATRIX_ROWS][MATRIX_COLS] __attribute__ ((section (".keymap.keymaps"))) = {
#else
const uint8_t keymaps[][MATRIX_ROWS][MATRIX_COLS] PROGMEM = {
#endif
    [0] = KEYMAP_TKG(
        GRV, 1,   2,   3,   4,   5,   HOME,END, 6,   7,   8,   9,   0,   BSPC, \
        TAB, Q,   W,   E,   R,   T,   LBRC,RBRC,Y,   U,   I,   O,   P,   BSLS, \
        ESC, A,   S,   D,   F,   G,             H,   J,   K,   L,   SCLN,QUOT, \
        FN3, Z,   X,   C,   V,   B,   FN7, FN8, N,   M,   COMM,DOT, SLSH,FN3,  \
        LCTL,LGUI,LALT,FN11,DEL,                     MINS,EQL, F10, F11, F12,  \
             LCTL,FN2, SPC, FN4, PSCR,CAPS,FN6, PAUS,FN5, ENT, FN1, LGUI),
    [1] = KEYMAP_TKG(
        TRNS,F1,  F2,  F3,  F4,  F5,  TRNS,TRNS,F6,  F7,  F8,  F9,  F10, DEL,  \
        TRNS,1,   2,   3,   4,   5,   TRNS,TRNS,FN21,FN22,FN23,FN24,FN25,TRNS, \
        TRNS,6,   7,   8,   9,   0,             FN26,FN27,FN28,FN29,FN30,TRNS, \
        TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS, \
        TRNS,TRNS,TRNS,TRNS,TRNS,                    VOLU,VOLD,MPRV,MPLY,MNXT, \
             TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS),
    [2] = KEYMAP_TKG(
        TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS, \
        TRNS,TRNS,TRNS,END, TRNS,TRNS,TRNS,TRNS,TRNS,PGUP,INS, TRNS,TRNS,TRNS, \
        TRNS,HOME,TRNS,PGDN,TRNS,TRNS,          LEFT,DOWN,UP,  RGHT,TRNS,TRNS, \
        TRNS,TRNS,DEL, TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,FIND,TRNS, \
        TRNS,TRNS,TRNS,TRNS,TRNS,                    TRNS,TRNS,TRNS,TRNS,TRNS, \
             TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS),
    [3] = KEYMAP_TKG(
        TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS, \
        TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS, \
        TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,          TRNS,TRNS,TRNS,TRNS,TRNS,TRNS, \
        TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,FN9, FN10,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS, \
        TRNS,TRNS,TRNS,TRNS,TRNS,                    TRNS,TRNS,TRNS,TRNS,TRNS, \
             TRNS,TRNS,BSPC,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS,TRNS),
};

#ifdef KEYMAP_SECTION_ENABLE
const uint16_t fn_actions[] __attribute__ ((section (".keymap.fn_actions"))) = {
#else
const uint16_t fn_actions[] PROGMEM = {
#endif
    [1] = ACTION_LAYER_MOMENTARY(1),
    [2] = ACTION_LAYER_MOMENTARY(2),
    [3] = ACTION_LAYER_MODS(3, MOD_LSFT),
    [4] = ACTION_MODS_KEY(MOD_LGUI, KC_SPACE),
    [5] = ACTION_MODS_KEY(MOD_LGUI, KC_TAB),
    [6] = ACTION_LAYER_TOGGLE(1),
    [7] = ACTION_MODS_KEY(MOD_LSFT, KC_9),
    [8] = ACTION_MODS_KEY(MOD_LSFT, KC_0),
    [9] = ACTION_MODS_KEY(MOD_LSFT, KC_COMMA),
    [10] = ACTION_MODS_KEY(MOD_LSFT, KC_DOT),
    [11] = ACTION_MODS(MOD_LCTL | MOD_LSFT | MOD_LALT | MOD_LGUI),
    [21] = ACTION_MODS_KEY(MOD_LSFT, KC_1),
    [22] = ACTION_MODS_KEY(MOD_LSFT, KC_2),
    [23] = ACTION_MODS_KEY(MOD_LSFT, KC_3),
    [24] = ACTION_MODS_KEY(MOD_LSFT, KC_4),
    [25] = ACTION_MODS_KEY(MOD_LSFT, KC_5),
    [26] = ACTION_MODS_KEY(MOD_LSFT, KC_6),
    [27] = ACTION_MODS_KEY(MOD_LSFT, KC_7),
    [28] = ACTION_MODS_KEY(MOD_LSFT, KC_8),
    [29] = ACTION_MODS_KEY(MOD_LSFT, KC_9),
    [30] = ACTION_MODS_KEY(MOD_LSFT, KC_0),
};
```

## 成本统计

* PCB板 + 外壳 = 220 RMB （已加邮费）
* 轴 + 平衡栏 + 灯 = 100 RMB （包邮）
* 键帽 = 119RMB （包邮）
* 合计：440RMB

总的看来，这个复刻版本，比国外动辄上百刀的版本更有吸引力。不过高大上程度还是略逊一筹。

ErgoDone，让你重新定（学）义（习）打字。