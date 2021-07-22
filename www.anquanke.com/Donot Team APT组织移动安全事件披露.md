> 原文链接: https://www.anquanke.com//post/id/202757 


# Donot Team APT组织移动安全事件披露


                                阅读量   
                                **324658**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p5.ssl.qhimg.com/t01d99147e3c8c39131.jpg)](https://p5.ssl.qhimg.com/t01d99147e3c8c39131.jpg)



**概述：**Donot Team是一个疑似具有南亚某国政府背景的APT组织，其主要针对巴基斯坦等南亚地区进行网络间谍活动。该APT组织除了以携带Office漏洞或者恶意宏的鱼叉邮件进行恶意代码的传播之外，还擅长伪装成系统工具、服务等应用在移动端进行传播。

该APT组织的攻击活动最早可追溯到2016年，传播的恶意软件大都具有比较完善的窃取用户隐私数据的功能，窃取的用户隐私数据包括短信、联系人、通讯录、通话记录、键盘记录、日历行程等信息。该类恶意软件运行后会请求用户开启无障碍服务并利用该项服务遍历whatapp节点获取用户聊天内容。它们会将窃取的所有数据保存在txt文件中或本地数据库中并上传至服务器。

[![](https://p1.ssl.qhimg.com/t01252f6f3802e969c6.png)](https://p1.ssl.qhimg.com/t01252f6f3802e969c6.png)

**图1-1恶意软件图标**



## 1.样本信息

**MD5**：47EFAE687575E61F94B1AD8230F03E46

**包名：**com.tencent.mm

**应用名：**SystemService

**安装图标：**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0173a735972e7e5f1e.png)



## 2.运行流程图

程序运行会根据配置文件参数的值选择进行不同操作。如果程序是首次运行，则启动主服务从服务器获取指令设置参数的值，然后根据参数的值执行相应的获取用户隐私数据的操作。

[![](https://p1.ssl.qhimg.com/t014390b97d66442299.png)](https://p1.ssl.qhimg.com/t014390b97d66442299.png)

**图1-2程序运行流程图**



## 3.行为分析

**应用首次运行请求开启可访问性服务，该项服务用于**遍历whatapp节点获取用户聊天内容。

[![](https://p4.ssl.qhimg.com/t017740ecbb1087d77a.png)](https://p4.ssl.qhimg.com/t017740ecbb1087d77a.png)

**图2-1请求开启可访问性服务**

早期恶意软件版本未对C&amp;C地址加密，更新的恶意软件版本对服务器地址进行了加密处理，增加了分析人员逆向分析难度。

[![](https://p5.ssl.qhimg.com/t0130d32e49e4c7cbcf.png)](https://p5.ssl.qhimg.com/t0130d32e49e4c7cbcf.png)

**图2-2文件对比**

解密后的服务器地址为mimestyle.xyz。程序与服务器交互，根据服务器下发的指令配置相应参数。而后根据参数的值执行相应任务。

[![](https://p4.ssl.qhimg.com/t01256b57f7039c44cf.png)](https://p4.ssl.qhimg.com/t01256b57f7039c44cf.png)

**图2-3服务端下发指令**

**指令列表:**

[![](https://p1.ssl.qhimg.com/t01e6b564cf2767f166.png)](https://p1.ssl.qhimg.com/t01e6b564cf2767f166.png)

1）获取联系人信息：

[![](https://p3.ssl.qhimg.com/dm/1024_586_/t01fc9ae72edf29fcbc.png)](https://p3.ssl.qhimg.com/dm/1024_586_/t01fc9ae72edf29fcbc.png)

**图2-4获取用户联系人信息**

[![](https://p1.ssl.qhimg.com/t01cff0414b4704380e.png)](https://p1.ssl.qhimg.com/t01cff0414b4704380e.png)

**图2-5保存用户联系人信息的txt文件**

2）获取通话记录信息：

[![](https://p0.ssl.qhimg.com/dm/1024_619_/t015d848041bcbc106e.png)](https://p0.ssl.qhimg.com/dm/1024_619_/t015d848041bcbc106e.png)

**图2-6获取通话记录信息**

[![](https://p5.ssl.qhimg.com/t01f49f0c86ab3d585d.png)](https://p5.ssl.qhimg.com/t01f49f0c86ab3d585d.png)

**图2-7保存用户通话记录的txt文件**

3）获取短信信息：

[![](https://p1.ssl.qhimg.com/dm/1024_676_/t01952a55d8a6e93f06.png)](https://p1.ssl.qhimg.com/dm/1024_676_/t01952a55d8a6e93f06.png)

**图2-8获取短信信息**

[![](https://p1.ssl.qhimg.com/t01c38058b44322a726.png)](https://p1.ssl.qhimg.com/t01c38058b44322a726.png)

**图2-9保存用户短信的txt文件**

4）获取账户信息：

[![](https://p3.ssl.qhimg.com/dm/1024_662_/t015333cf80263792c2.png)](https://p3.ssl.qhimg.com/dm/1024_662_/t015333cf80263792c2.png)

**图2-10获取用户账户信息**

5）获取外部存储器文件列表：

[![](https://p0.ssl.qhimg.com/t018895418fd4dc7489.png)](https://p0.ssl.qhimg.com/t018895418fd4dc7489.png)

**图2-11获取外部存储器文件列表**

6）获取已安装应用列表：

[![](https://p5.ssl.qhimg.com/dm/1024_609_/t0138b86bbdd7d904dd.png)](https://p5.ssl.qhimg.com/dm/1024_609_/t0138b86bbdd7d904dd.png)

**图2-12获取已安装应用列表**

7）获取日历日程事件信息：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_770_/t01eddbc56cd9479412.png)

**图2-13获取日历日程事件信息**

8）监听用户接收与发送的短信息，并获取短信内容。

[![](https://p0.ssl.qhimg.com/t018f15ecab0858253c.png)](https://p0.ssl.qhimg.com/t018f15ecab0858253c.png)

**图2-14监听短信息**

9）监听电话状态，根据不同的电话电话执行不同操作。

[![](https://p2.ssl.qhimg.com/dm/1024_366_/t01f6ea08d9a529a400.png)](https://p2.ssl.qhimg.com/dm/1024_366_/t01f6ea08d9a529a400.png)

**图2-15监听电话状态**

10）当用户手机处理监听状态时，对用户通话记录进行录音。并保存/mnt/sdcard/Android/.system路径下。

[![](https://p5.ssl.qhimg.com/dm/1024_478_/t015a9774a41110d95b.png)](https://p5.ssl.qhimg.com/dm/1024_478_/t015a9774a41110d95b.png)

**图2-16对通话记录录音**

11）通过可访问性服务监听用户操作设备事件，遍历Whatsapp的List节点并保存文本信息。这里是获取用户whatsapp聊天信息。

[![](https://p3.ssl.qhimg.com/dm/1024_580_/t01cefcc10cc909db2f.png)](https://p3.ssl.qhimg.com/dm/1024_580_/t01cefcc10cc909db2f.png)

**图2-17获取用户whatsapp聊天内容**

12）将获取的所有信息保存到.txt文件中。并写入DataOutputStream流中上传至服务器。

[![](https://p0.ssl.qhimg.com/t01a2ec34d79595d87e.png)](https://p0.ssl.qhimg.com/t01a2ec34d79595d87e.png)

**图2-17上传保存隐私数据的文件**



## 3.扩展分析

该APT组织从2016年起就持续在PC端和移动端传播恶意样本，移动端恶意样本的主体功能并未做太大改变。在恒安嘉新App全景平台态势平台上，我们发现多款该APT组织分发的恶意应用。

[![](https://p1.ssl.qhimg.com/t01b820c1814006d47a.png)](https://p1.ssl.qhimg.com/t01b820c1814006d47a.png)

**图3-1样本信息**

**样本信息：**

[![](https://p2.ssl.qhimg.com/t01aff467c48de2f52e.png)](https://p2.ssl.qhimg.com/t01aff467c48de2f52e.png)



## 4.安全建议

提升自身安全意识，当应用一开始运行便请求开启无障碍服务时，应提高警惕。

面对隐藏自身图标无法正常卸载的应用，可进入应用程序列表进行卸载。

关注“暗影安全实验室”微信公众号，我们将持续关注安全事件。
