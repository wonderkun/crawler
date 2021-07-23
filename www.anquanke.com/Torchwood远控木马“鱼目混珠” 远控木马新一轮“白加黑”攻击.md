> 原文链接: https://www.anquanke.com//post/id/186768 


# Torchwood远控木马“鱼目混珠” 远控木马新一轮“白加黑”攻击


                                阅读量   
                                **422824**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                    



[![](https://p3.ssl.qhimg.com/t018a2875b87dd2ea2e.png)](https://p3.ssl.qhimg.com/t018a2875b87dd2ea2e.png)



近期，360安全大脑监测到大量远控木马的传播，经过深度分析，发现该木马是“Torchwood”远控木马的新变种。曾经该木马通过下载网站、钓鱼邮件和QQ群等方式传播，都已被360安全大脑全面查杀，而最近的更新则有卷土重来的迹象。

这一次该木马再度延用“CHM钓鱼攻击”的传播方式，并配合极具迷惑性的标题，诱导用户打开木马文件，使其在不知不觉中遭受攻击。广大用户不必过分担心，目前360安全大脑已全面拦截该木马的攻击，建议用户及时下载安装360安全卫士保护电脑隐私及数据安全。



## CHM文件“鱼目混珠”潜入系统，“白加黑”作案手法屡试不爽

什么是CHM文件呢？大家不要觉得CHM文件很“冷门”，它是经过压缩的各类资源的集合，日常中支持图片、音频、视频、Flash、脚本等内容，因为方便好用、形式多样，也可算是文件格式界里的“经济适用款”，越来越多的电子书、说明文档都采用了CHM格式。在大多数人的印象中，CHM类型文件是“无公害”文档文件，但只要加以利用便可以“鱼目混珠”潜入系统躲过杀毒软件，并发起隐秘攻击。事实上，360安全大脑监测到的多起攻击事件中，都可以看到 CHM 文件的影子，这类手法也被业界形象地称为“白加黑”攻击。

历史手法，又在重演。本轮攻击中，360安全大脑发现木马作者再次利用了CHM文件，再配上能够引起用户兴趣的敏感标题，然后通过下载网站、钓鱼邮件和QQ群等渠道传播，最终诱导用户打开木马文件，达到控制用户电脑，盗取帐号密码及重要资料等目的。

[![](https://p4.ssl.qhimg.com/t01abffc5c1e3790090.png)](https://p4.ssl.qhimg.com/t01abffc5c1e3790090.png)

与“钱财”等有关的诱惑性标题

360安全大脑对该CHM文件进一步溯源分析，发现Torchwood远控木马的攻击核心是加入了具有云控功能的HTML脚本。当用户运行虚假的CHM文件后，“精心乔装”的虚假网页访问404图片便会自动弹出，与此同时，潜伏在系统后台已久的攻击程序也同时悄然运行。

[![](https://p2.ssl.qhimg.com/t018e808184ff4a90cc.png)](https://p2.ssl.qhimg.com/t018e808184ff4a90cc.png)

360安全大脑对该混淆代码分析，发现其攻击流程如下：

1、利用certutil.exe 下载一张网站访问404的截图run.jpg，用来欺骗用户。

[![](https://p4.ssl.qhimg.com/t0138d497652cc741bb.png)](https://p4.ssl.qhimg.com/t0138d497652cc741bb.png)

2、利用certutil.exe 下载压缩后的攻击模块temp1.jpg。

[![](https://p1.ssl.qhimg.com/t019375842a46ed71c4.png)](https://p1.ssl.qhimg.com/t019375842a46ed71c4.png)

3、利用certutil.exe 下载解压用的WinRar工具helloworld.jpg。

[![](https://p3.ssl.qhimg.com/t01293db62ca95575f9.png)](https://p3.ssl.qhimg.com/t01293db62ca95575f9.png)

4、运行WinRar工具，用来解压攻击模块，密码为“Tatoo”。

[![](https://p4.ssl.qhimg.com/t014b531ef59c1480da.png)](https://p4.ssl.qhimg.com/t014b531ef59c1480da.png)

5、前端利用欺骗性图片迷惑用户，背后则偷偷运行攻击程序。

整个过程大致如下，完成下载和解压工作后，木马就会进入攻击流程。

[![](https://p0.ssl.qhimg.com/t01a15b4ae9e2695bf3.png)](https://p0.ssl.qhimg.com/t01a15b4ae9e2695bf3.png)

具体的攻击代码流程如下：

1、首先木马作者会启动Perflog.exe文件，该文件是罗技的键鼠管理程序，属于被白利用的正常程序。

[![](https://p5.ssl.qhimg.com/t0168a940e82863cb5c.png)](https://p5.ssl.qhimg.com/t0168a940e82863cb5c.png)

2、Perflog.exe会加载黑模块logidpp.dll，这是木马作者经常使用的“白加黑“手法。

[![](https://p3.ssl.qhimg.com/t01f137a9c38946dd97.png)](https://p3.ssl.qhimg.com/t01f137a9c38946dd97.png)

3、logidpp.dll是一个PELoader程序，它的任务是在内存中解密bugrpt.log文件，并在内存中加载运行此恶意模块。

[![](https://p5.ssl.qhimg.com/t019228730a072e37c5.png)](https://p5.ssl.qhimg.com/t019228730a072e37c5.png)

4、调用恶意模块的导出函数“Torchwood“，执行远控代码流程。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014a3cf6c90dc9255c.png)

值得一提的是，此类木马是一个具有下载和内存执行功能的程序，并且可以通过云控的方式运行任意代码。这里，我们主要分析的是其传播远控程序对受害目标进行攻击的过程，可以看到该木马还包含一系列自我保护的功能，以达到长久驻留的目的。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0130981532cd77bab4.png)

（添加注册表，长期驻留）

[![](https://p1.ssl.qhimg.com/t014edd30f483d8fd69.png)](https://p1.ssl.qhimg.com/t014edd30f483d8fd69.png)

（远控功能）

[![](https://p0.ssl.qhimg.com/t01b37c8c0bb0be2d41.png)](https://p0.ssl.qhimg.com/t01b37c8c0bb0be2d41.png)

（内置的安全软件检测列表）

Torchwood 远控木马前有针对杀毒软件的检测躲避大招加持，后有任意代码执行的远控攻击技能傍身，本轮攻击可谓来势汹汹，但360安全大脑通过多种技术手段防御和发现最新木马病毒，且已率先实现对该类木马的查杀，为避免此类攻击的感染态势进一步扩大， 360安全大脑建议：

1、建议广大用户前往weishi.360.cn，及时下载安装360安全卫士，能有效拦截该木马的攻击，保护个人信息及财产安全；

2、使用360软件管家下载软件。360软件管家收录万款正版绿色软件，经过360安全大脑白名单检测，下载、安装、升级，更安全。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0130c0ef9bc888186c.png)

### 附录IOC

[![](https://p4.ssl.qhimg.com/t01e1b948d8c27d9e18.png)](https://p4.ssl.qhimg.com/t01e1b948d8c27d9e18.png)
