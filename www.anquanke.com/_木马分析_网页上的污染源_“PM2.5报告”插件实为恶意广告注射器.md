> 原文链接: https://www.anquanke.com//post/id/86853 


# 【木马分析】网页上的污染源：“PM2.5报告”插件实为恶意广告注射器


                                阅读量   
                                **89110**
                            
                        |
                        
                                                                                    



**[![](https://p2.ssl.qhimg.com/t014bf6e0dc5045dab8.png)](https://p2.ssl.qhimg.com/t014bf6e0dc5045dab8.png)**

**<br>**

**前言**

**网站通过投放广告来获得收入，这本无可厚非。但是大家有没有想过，这些页面广告真的都是网站自己投放的么？其实并不一定，360互联网安全中心近日就发现了这样一款恶意软件，它会向用户正常访问的网页中插入各种低俗甚至是欺诈类的广告。**

该恶意软件主体会伪装成“PM2.5报告”程序，被安装后静默向Chrome内核浏览器安装扩展、向IE浏览器安装BHO插件进而插入广告。相较于我们在2015年发布的分析报告《“国产”广告注射器分析：以比价名义强插各大网站》中所提及的恶意软件，该软件可谓有过之而无不及。

“PM2.5报告”恶意程序流程简图：

[![](https://p4.ssl.qhimg.com/t01694286022254d508.png)](https://p4.ssl.qhimg.com/t01694286022254d508.png)

<br>

**软件主体**

该软件的主体安装程序会主动检测当前运行环境，若检测到自身正被调试，则主动结束进程。

[![](https://p4.ssl.qhimg.com/t013eb62fc5ba881093.png)](https://p4.ssl.qhimg.com/t013eb62fc5ba881093.png)

**BHO插件**

BHO(Browser Helper Object)，即浏览器辅助对象，是作为IE浏览器的插件被使用的。而恶意软件主体程序被安装后，便会同时向IE浏览器中插入一个名为“Cyynb Breath”的BHO插件：

[![](https://p4.ssl.qhimg.com/t0162b97db5e2fc7c25.png)](https://p4.ssl.qhimg.com/t0162b97db5e2fc7c25.png)

该插件会云控获取的配置文件skin2.zip(GifBag.edb、PngBag.edb)，可以看到其对哪些网站进行注入广告都由云端规则控制

[![](https://p1.ssl.qhimg.com/t01cca06ab1c559a1f3.png)](https://p1.ssl.qhimg.com/t01cca06ab1c559a1f3.png)

之后读取GifBag.edb、PngBag.edb两个文件的内容：

[![](https://p1.ssl.qhimg.com/t01bce0b9e757332cab.png)](https://p1.ssl.qhimg.com/t01bce0b9e757332cab.png)

其中PngBag.edb为该插件在插入广告时要避开的网站或ID，内容如下：

[![](https://p4.ssl.qhimg.com/t010befa3331a03fdf8.png)](https://p4.ssl.qhimg.com/t010befa3331a03fdf8.png)

而GifBag.edb文件中则是用于插广告的代码：

[![](https://p2.ssl.qhimg.com/t01bb125a854320fe2b.png)](https://p2.ssl.qhimg.com/t01bb125a854320fe2b.png)

GifBag.edb中含带有需要插广告网站的完整列表，如下：

[![](https://p3.ssl.qhimg.com/t01b9107d1ff36ed09c.png)](https://p3.ssl.qhimg.com/t01b9107d1ff36ed09c.png)

**Chrome浏览器扩展**

软件主体一旦发现Chrome浏览器（或使用Chrome内核的相关浏览器），则释放crx程序（ChRome eXtension，即Chrome浏览器扩展程序）:

[![](https://p3.ssl.qhimg.com/t019f1d0f8267c05510.png)](https://p3.ssl.qhimg.com/t019f1d0f8267c05510.png)

图标如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t012e08b48b1ce7a1c9.png)

该扩展会修改用户打开的页面内容，向页面中插入其广告js代码：

[![](https://p3.ssl.qhimg.com/t01b170d53bbde24581.png)](https://p3.ssl.qhimg.com/t01b170d53bbde24581.png)

通过查看被插入的js脚本，同样可以看到其广告推广行为同BHO插件一样，也是针对特定网站的。而通过插入云端js脚本来控制用户网页浏览的优点也很明显：一方面云端脚本的内容方便随时修改，使用起来比较灵活；另一方面对于普通用户来说基本毫无感知，难以察觉。

被插入广告网站列表中囊括了网易、QQ空间、凤凰网、搜狐等36个网站的所有包含.htm、.asp、.shtm后缀的网页页面。

[![](https://p0.ssl.qhimg.com/t01444d2a1ca0fd829f.png)](https://p0.ssl.qhimg.com/t01444d2a1ca0fd829f.png)

而类似的，该广告脚本也含有一个白名单列表，即遇到以下这些网站，广告脚本是不工作的。其中包括各类政府网站、淘宝网、人民网、12306、百度等。

[![](https://p0.ssl.qhimg.com/t01ab9f8029b72aff38.png)](https://p0.ssl.qhimg.com/t01ab9f8029b72aff38.png)

插入广告相关代码还通过设置/读取Cookie的方式，实现同一网站30分钟内再次打开不再出现广告。

[![](https://p5.ssl.qhimg.com/t01fa4acbc849f8bc20.png)](https://p5.ssl.qhimg.com/t01fa4acbc849f8bc20.png)

并且其中还含有对广告展示的数量统计：

[![](https://p2.ssl.qhimg.com/t01ee39bb577246b888.png)](https://p2.ssl.qhimg.com/t01ee39bb577246b888.png)

**浏览器被插入广告实测效果**

网易（Chrome内核浏览器）：

[![](https://p5.ssl.qhimg.com/t01818e1eb0c9546ac4.png)](https://p5.ssl.qhimg.com/t01818e1eb0c9546ac4.png)

新浪网（Chrome内核浏览器）：

[![](https://p5.ssl.qhimg.com/t01b79e2fc8ecb5987b.png)](https://p5.ssl.qhimg.com/t01b79e2fc8ecb5987b.png)

网易（IE浏览器）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0106068a167a70f358.png)

腾讯网（IE浏览器）：

[![](https://p5.ssl.qhimg.com/t01df4eb20863d22392.png)](https://p5.ssl.qhimg.com/t01df4eb20863d22392.png)

唯品会（IE浏览器）：

[![](https://p1.ssl.qhimg.com/t013e1d07030c99a0ea.png)](https://p1.ssl.qhimg.com/t013e1d07030c99a0ea.png)

58同城（IE浏览器）：

[![](https://p0.ssl.qhimg.com/t017372b63ad542dac7.png)](https://p0.ssl.qhimg.com/t017372b63ad542dac7.png)

我们随手点开其中的一些广告，弹出的都是类似这中诈骗或博彩的内容：

[![](https://p3.ssl.qhimg.com/t01e7cf73f47ae3fdd0.png)](https://p3.ssl.qhimg.com/t01e7cf73f47ae3fdd0.png)



[![](https://p3.ssl.qhimg.com/t016df27a237872ee15.png)](https://p3.ssl.qhimg.com/t016df27a237872ee15.png)

<br>

**传播情况**

通过对该恶意的监控，该程序主要通过某知名在线视频软件的升级捆绑安装，以及外挂辅助程序的捆绑推广，累积有近百万用户被安装该恶意程序。

[![](https://p2.ssl.qhimg.com/t01892354b95ce83b77.png)](https://p2.ssl.qhimg.com/t01892354b95ce83b77.png)

对于此类广告注入行为，普通用户基本毫无感知。由于这些程序会隐藏于浏览器和网站之间，悄悄的修改网站代码，导致用户难以识别广告的真实性。往往是用户在访问正规官网时看见页面展示此类广告，很可能将其误认为是来自于官网推荐，因此对广告的安全性不加怀疑。而此类广告极有可能会将用户诱导向钓鱼网站或存在风险的网站，使用户遭受账号隐私泄露及财产损失的风险。

<br>

**在此360提醒广大用户**

1、如果发现访问知名网站网页出现低俗、欺诈等异常广告时，说明你电脑浏览器可能被劫持了，应及时检查清理不可信的浏览器扩展。

2、请谨慎使用来路不明的浏览器扩展程序，建议使用能自动禁用来路不明浏览器扩展的浏览器程序如360安全浏览器；

3、定期使用360安全卫士等安全软件扫描插件，发现恶意插件及时清除。
