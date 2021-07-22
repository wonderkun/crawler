> 原文链接: https://www.anquanke.com//post/id/84541 


# 【WriteUp】labyrenth CTF windows track挑战（下）


                                阅读量   
                                **72686**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t0126a05cb6036cec89.jpg)](https://p3.ssl.qhimg.com/t0126a05cb6036cec89.jpg)

**文件: RGB.exe**

**SHA256**:F52983C900851B605A236D62C38BC2BC6232CA1220A23E447901D029D5357F88

**加壳：**无

**体系结构: **32Bit

**使用工具:** exeinfo,Reflector

**代码&amp;二进制文件：**https://github.com/jmprsp/labyrenth/tree/master/Window-Challenge-5

**说明：**这种挑战是以 C# 语言编写的。只有找出正确的RGB 值才能获得标记，只有对代码进行反编译和分析才能得到RGB 值。

 

[![](https://p5.ssl.qhimg.com/t0109968c6aa0f201f9.png)](https://p5.ssl.qhimg.com/t0109968c6aa0f201f9.png)



  如图所示，我们知道这是一个 C# 程序。

 

[![](https://p0.ssl.qhimg.com/t01ef58b7480230ce7f.png)](https://p0.ssl.qhimg.com/t01ef58b7480230ce7f.png)



  使用像是反射器这样的反编译工具，我们可以很容易得到反编译的源代码。我在github中放置了源代码。

 

[![](https://p4.ssl.qhimg.com/t01062e6ae4d13d9ce6.png)](https://p4.ssl.qhimg.com/t01062e6ae4d13d9ce6.png)



  对源代码进行分析的时候我们会在 frmMain.cs 中遇到上图所示的函数。看起来我们需要一些暴力破解来获取正确的 RGB 密钥。

 

[![](https://p3.ssl.qhimg.com/t0196564c938a18c487.png)](https://p3.ssl.qhimg.com/t0196564c938a18c487.png)



  运行上面的脚本，我们能够得到正确的 RGB 来解决所面临的挑战。

 

[![](https://p2.ssl.qhimg.com/t011419e207f4bea3df.png)](https://p2.ssl.qhimg.com/t011419e207f4bea3df.png)



标记: PAN`{`l4byr1n7h_s4yz_x0r1s_4m4z1ng`}`

<br style="text-indent:2em;text-align:left">

**文件: Ambrosius.exe**

**SHA256:**54CB91340DBC073FB303A7D920E26AA1D64F9EE883D6AAE55961A76D5AFF91F4

**加壳：**无

**体系结构: **32Bit

**使用工具:** exeinfo, IDA Pro

**代码&amp;二进制文件:** [https://github.com/jmprsp/labyrenth/tree/master/Window-Challenge-6](https://github.com/jmprsp/labyrenth/tree/master/Window-Challenge-6)

**说明：**这种挑战是用 C语言编写的，目标是要找到正确的密码，这样解密的字符串将以"PAN`{`?????"开头。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01b8af68bd79b7f419.png)

 

  IDA Pro 的字符串列表和导入列表中没有显示任何调查结果。

  滚动浏览代码，第一眼看到的就是对于PAN`{`的检查，也许我们能从这里下手。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t013c88f64413e1449a.png)

 

  向上追踪，我们可以假设传入解密函数 (0x401425)的是长度为11位的密码。向上进一步分析，我们可以看到密码是怎样形成的。



[![](https://p0.ssl.qhimg.com/t01804cd5e84b0c002d.png)](https://p0.ssl.qhimg.com/t01804cd5e84b0c002d.png)





 <br>

  以下是建立密码字符串的说明。

注︰ 挑战使用外壳代码的方法是从系统中获取数值或是调用函数。

[![](https://p3.ssl.qhimg.com/t01485b010e7282e802.png)](https://p3.ssl.qhimg.com/t01485b010e7282e802.png)

  从上图中，我们知道密码有 4个 固定的 11 个字符值，其余 7 个字符可以是随意的。

  我应对这一挑战最懒的办法是使用 python 调试脚本，打破 @ 0x00401425 。一旦程序破损，python 脚本应使用我们生成的密码覆盖原始密码。

  要检查是否我们有了正确的密码，放置另一个断点 @0x0040143B （请参阅图 2）。如果我们点击此断点，那就意味着我们已经找到了正确的密码。

  我用 php 来生成可能的密码列表，并将其放置到 python 脚本 （请参阅 GrayHat Python） 测试可执行文件的密码。这种方法绝对不是解决所面临挑战最快的方式，但这是最懒的方法。



 

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01c8437b4879782b2c.png)



  对于 python 调试脚本，我用的是"Grayhat Python"给予的样本。如果它已经找到了正确的密码，我只要使用注入的脚本来生成密码和检测就可以了。



[![](https://p5.ssl.qhimg.com/t01187989c9de639724.png)](https://p5.ssl.qhimg.com/t01187989c9de639724.png)

 

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014ba421ec1501d372.png)

 

  可能这不是解决挑战最简洁的办法，但是的确是有用的！

<br>

标记: PAN`{`th0se_puPP3ts_creeped_m3_out_and_I_h4d_NIGHTMARES`}`



<br style="text-indent:2em;text-align:left">
