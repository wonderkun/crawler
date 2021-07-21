> 原文链接: https://www.anquanke.com//post/id/96901 


# 青蛙旅行 — Unity3d类安卓游戏逆向分析初探


                                阅读量   
                                **217744**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">9</a>
                                </b>
                                                                                    



![](https://p5.ssl.qhimg.com/t0170e2c24aeca4e18f.png)

## 0x01 前言

最近一款养蛙的游戏非常火，但是语言是日文的。下载了一个汉化的，结果广告一大堆。反编译之后查看是Unity游戏，之前没接触过，就想着跟着看一下。关于这类的破解，可以在52pojie上进行搜索。有很多类似的案例。

这里主要采用的工具为dnSpy，dnSpy 是一款针对 .NET 程序的逆向工程工具。反编译和打包采用的是apktool，当然也可以直接用改之理等工具。

虽然本文以一个小游戏为实例，但这个思路值得安全渗透人员借鉴。



## 0x02 修改数据

下载app后重命名为zip文件，发现存在`assets\bin\Data\Managed`目录，那么该游戏应该为Unity游戏。

![](https://p3.ssl.qhimg.com/t01ecade972f008ef87.png)

那么需要分析的文件就是就是`Assembly-CSharp.dll`。

首先修改一下抽奖券的数量。安装游戏后，找到抽奖的地方。抽奖的时候提示券不足。

![](https://p3.ssl.qhimg.com/t01e04dab5a0f0898ba.png)

使用dnSpy打开`Assembly-CSharp.dll`文件，然后搜索字符串”足”，可以发现有两个，打开后发现是第一个。

![](https://p3.ssl.qhimg.com/t0110976b771b753b88.png)

由此可以猜测TicketStock代表抽奖券库存。

![](https://p1.ssl.qhimg.com/t010855b8212b0bd6c6.png)

ticket表示抽奖券数量。

![](https://p0.ssl.qhimg.com/t016e19f385bd67dfca.png)

当页查找ticket，发现有一个initialize方法进行初始化。我们将此处的数量改为1000.

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

快捷键Ctrl+E编辑IL指令。找到ticket变量后，将ldc.i4.0改为ldc.i4，然后将数值改为1000.

![](https://p1.ssl.qhimg.com/t01c1843cf880aeccfd.png)

确定后，发现ticket数值已经改变。

![](https://p4.ssl.qhimg.com/t016b9117a70888de6f.png)

打包后并安装apk。

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

打开抽奖界面发现数量已经改变为1000。

![](https://p5.ssl.qhimg.com/t01e0dc332fc1468136.png)

这样虽然达到了修改抽奖券的效果，但数量再大，总会被抽完的。那就换种方法，比如说抽奖的时候增加奖券，或者奖券一直不变。这里采用奖券数量固定的方法，使其不会变动。

```
if (SuperGameMaster.TicketStock() &lt; 5)

`{`

   ConfilmPanel confilm = this.ConfilmUI.GetComponent&lt;ConfilmPanel&gt;();

   confilm.OpenPanel("ふくびき券が足りません");

   confilm.ResetOnClick_Screen();

   confilm.SetOnClick_Screen(delegate

   `{`

       confilm.ClosePanel();

   `}`);

   return;

`}`
```

已知抽奖的时候奖券是从`SuperGameMaster.TicketStock()`获取的，找到该方法。令其返回值为固定的数值。

![](https://p4.ssl.qhimg.com/t017a8642b38ec4d7aa.png)

右键编辑IL指令。

![](https://p5.ssl.qhimg.com/t01b6e4f8dcb762ef6e.png)

将其值修改为9000.

![](https://p4.ssl.qhimg.com/t01d149dcf20c6d7f65.png)

然后保存后打包并重新安装。

![](https://p2.ssl.qhimg.com/t01fd31634f98fcef1e.png)

此时无论抽多少次，奖券都不再变化。

另一个就是修改三叶草的数量了。三叶草是该游戏中流行的货币，买东西都是需要该物品。同理找到`CloverPointStock()`方法。

![](https://p4.ssl.qhimg.com/t01c53a98117088f4e8.png)

将其返回值修改为8888.之后就可以随便买买买了，三叶草的数量也不会发生变化了。

![](https://p3.ssl.qhimg.com/t019e6319cfcd063f3d.jpg)

#### 0x03 汉化

然后就是进行汉化了。汉化的方法和上面的类似。首先搜索需要修改的文字。例如给小青蛙起名字的时候。直接进行字符串搜索。

![](https://p0.ssl.qhimg.com/t017acf200bf452e617.png)

然后修改为对应的中文就行了。

![](https://p5.ssl.qhimg.com/t01db6933d3b9ad1cec.png)

进入游戏查看

![](https://p0.ssl.qhimg.com/t01d0e66e2cc9749bd3.jpg)

修改其他处的文字也是这样操作即可。当然这种修改方法比较慢，还有另外一种，直接将他人汉化过的dll文件复制进来，可以快速达到汉化的目的，也没有广告的烦恼了。



## 0x04 总结

这个游戏修改起来比较简单，首先判断为该游戏为Unity3d。然后使用dnSpy来对`Assembly-CSharp.dll`文件进行修改。根据特定的字符串找到需要修改的位置，修改后进行打包签名后即可。

#### 

## 0x05 游戏攻略

> **以下内容均来自知乎**
**作者：黄小秋**
**链接：https://www.zhihu.com/question/68733553/answer/305463907**

![](https://p3.ssl.qhimg.com/t0186a270ae209c0387.gif)

### 呱是如何旅行的？

确定了地点之后，呱会开始旅行：
<li>携带物品会决定蛙**最长**能旅行多久，**6 ～ 72 小时不等。**
</li>
<li>初始体力由携带物品决定，以 100 为基数提升。<br>
**物品的具体属性参考下面的图鉴*
</li>
1. 经过图上的一条路（边）的时候，道路的地形属性和所携带的物品属性互相作用，会决定呱实际消耗的时间和体力。
1. 路上可能会遇见小伙伴，会在之后的旅行中结伴而行，从而出现在明信片中。
1. 根据路途属性，有一定概率会寄相关的明信片。
1. 当体力不支的时候，蛙必须**停下来休息 3 小时**，休息完之后体力会恢复到 100。休息时间也算作旅行时间。
<li>当到达目的**或者**旅行时间耗尽的时候，蛙就会回家。
<ol>
1. 回家时会携带三叶草和抽奖券。
1. 如果在时间耗尽前到达了**目的地**，蛙会在此基础上带回当地特产和收藏品。
*所以如果你的蛙很久都没回家，回家了也没有带土特产，可能是路途上多次体力不支，晕倒在路边。*

![](https://p3.ssl.qhimg.com/t01a1104e3cd6c0cbae.gif)

### 呱在每条路上的耗时是怎么计算的？

设：<br>![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC) 为当前道路 **耗时<br>**![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC) 为当前道路的 **地形增加耗时<br>**![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC) 为当前道路的 **地形，**![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)<br>![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC) 为携带物品数量<br>![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC) 依次为携带的第 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC) 件物品中所有具有* 普通、山地、大海、洞穴、任意地形*** 移动速度 的效果值。**

如果当前道路是 *普通 *地形，则耗时因叠加 **移动速度** 效果而减少：

![](https://www.zhihu.com/equation?tex=t_w%3D+t_%7B%5Ctext%7Bway%7D%7D%5Ctimes%5Cprod_%7Bx%3D1%7D%5E%7Bn%7D%7B%280.01%5Ctimes%28100-E_%7B%5Ctext%7BNormal%7D%7D%7B%28x%29%7D%29%29%7D%5C%5C)<br>
或者 如果当前道路是 *山地、大海、洞穴 *地形，基础耗时不变，地形增加耗时因叠加 **移动速度** 效果而减少：<br>![](https://www.zhihu.com/equation?tex=t_w%3Dt_%7B%5Ctext%7Bway%7D%7D%2Bt_%7B%5Ctext%7Bplus%7D%7D%5Ctimes%5Cprod_%7Bx%3D1%7D%5E%7Bn%7D%7B%280.01%5Ctimes%28100-E_%7Bw%7D%7B%28x%29%7D%29%29%7D%5C%5C)<br>
如果携带了 **乳蛋饼 （のびるのキッシュ）**这种 *全地形 ***移动速度** 提升的物品，则会在此基础上再次叠加 **移动速度** 效果：<br>![](https://www.zhihu.com/equation?tex=t_%7B%5Ctext%7Bfinal%7D%7D%3Dt+%5Ctimes%5Cprod_%7Bx%3D1%7D%5E%7Bn%7D%7B%280.01%5Ctimes%28100-E_%7B%5Ctext%7BAll%7D%7D%7B%28x%29%7D%29%29%7D%5C%5C)<br>
最终获得的 ![](https://www.zhihu.com/equation?tex=t_%7B%5Ctext%7Bfinal%7D%7D) 就是该条道路上的实际耗时。

### 呱离家出走了怎么办？

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

如果长时间没有准备便当，包里和桌上都没有食物，呱会愤然离家出走（どこかへ出かけています）。

这个时候在桌子上放上吃的，呱就会在 5～30 分钟内回家。

*有趣的是，离家出走也算作成就计算中的旅行次数…emmmm。*

### 道路有哪些属性？

连接不同地点之间的每条路 (edge) 都有以下几个属性
<li>
**地形**<br>
四种地形分别是 *普通、大海、山地、洞穴*
</li>
<li>
**耗时**<br>
途径这条路的体力和时间损耗，分为基础耗时和地形增加耗时<br>*呱需要跋山涉水自然会耗时久一点*
</li>
<li>
**明信片概率<br>**明信片上不同元素出现的概率<br>*据说所有的地图元素都有真实原型*
</li>
<li>
**遇见伙伴<br>**遇见特定伙伴的概率</li>
### 每件物品都有什么效果？

奉上这张吐血整理的物品效果图鉴：

![](https://p1.ssl.qhimg.com/t0134b03847e7d65d3e.jpg)

![](https://p2.ssl.qhimg.com/t019867c22a25bcfb79.jpg)

有五类不同的物品
<li>
**便当<br>**商店购买或者抽奖获得的食物</li>
<li>
**幸运符<br>**除了四叶草和可以购买的幸 (tǔ) 运 (háo) 铃之外，都要抽奖获得</li>
<li>
**道具<br>**商店购买</li>
<li>
**特产<br>**呱旅游时获得</li>
<li>
**收藏品<br>**特别的特产，通常在县府获得，无法使用</li>
属性分类
<li>
**HP**
<ul>
<li>
**最大时间（小时**）<br>
决定蛙的旅行时间</li>
<li>
**初始体力提升（%）**<br>
增加一开始*一鼓作气*能旅行的距离</li>
<li>
**随机体力提升（%）**<br>
随机额外增加体力提升的最高百分点</li><li>
**三叶草**<br>
获得三叶草数量</li>
<li>
**额外随机三叶草**<br>
随机额外获得的最大三叶草数量</li>
<li>
**抽奖券**<br>
奖券数量</li>
<li>
**物品数量增多**<br>
增加获得目的地*收藏品*的概率</li>
### 如何科学使用物品？

![](https://p3.ssl.qhimg.com/t01ceed1048ee191813.gif)

这里用几个例子来展示物品和路线结合的效果
<li>
**决定想去的地区<br>**携带的便当和抽奖获得的护身符（お守り）可以提升选择特定地区的概率。 抽奖获得的车票（きっぷ）可以**直接决定**所去到的地区。<br>**例：***想去北方，使用**北国きっぷ。***
</li>
<li>
**影响路途的距离和时间<br>**带 **最大时间 **值高的食物吃走得远，带 **体力提升** 值高的食物吃走得快耗时少。</li>
<li>
**快速通过沿途路线的地形<br>**带有地区速度加成的食物或者道具，可以增加特定地形的移动速度。<br>
不同物品的 **移动速度** 效果可以叠加，详情查看上面的解释。</li>
<li>
**匹配在道路上遇到的伙伴<br>**如果在途径会遭遇伙伴的道路，特定物品可以增加实际遭遇概率<b><br>
例：</b>*抽奖抽到的黄色ぼうろ（饼干）可以增加路途中遇到螃蟹的几率。*
</li>
### 综合运用（敲黑板！！！）

**呱想去秋田県男鹿市看灯塔**
1. 在地图上找到 秋田県（3022） 在北方。
1. 便当选择 **あさつきのピロシキ （葱饼？）**可以提升去北方的概率。
1. 携带 **青色のお守り （蓝色护身符）**可以提升去北方的概率。
1. 如果有 **北国きっぷ（北方车票？）**可以直接决定去北方，上面的便当和护身符可以换别的。
1. 通过目的地概率表发现携带各类帐篷前往 3022 目的地的概率更高。
1. 查看可能的路线发现从起始点 3000 到 3022 之间会途径很多山路。
1. 携带 **ハイテクテント （高级帐篷？）**增加山地移动速度更显著。
1. 如果还有空余，可以带上 **よつ葉（四叶草）**或者 **幸運の鈴**，提升带回物品的概率。
![](https://p1.ssl.qhimg.com/t01e222c93de7670e05.jpg)



## 0x05 参考链接

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
1. [https://paper.seebug.org/519/](https://paper.seebug.org/519/)
1. [https://www.zhihu.com/question/68733553/answer/305463907](https://www.zhihu.com/question/68733553/answer/305463907)