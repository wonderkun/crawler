> 原文链接: https://www.anquanke.com//post/id/82387 


# 【HackPwn2015】九阳智能豆浆机破解细节分析


                                阅读量   
                                **113891**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t01082b35daeaf1a83d.png)](https://p2.ssl.qhimg.com/t01082b35daeaf1a83d.png)



九阳DJ08B-D667SG豆浆机是一款智能豆浆机,可以通过配置WIFI连入互联网,用户可以通过“九阳云家电”手机app对豆浆机进行远程控制,实现远程开启、关闭豆浆机等功能。

## 0x01分析工作流程

在对豆浆机初步使用和分析之后,我们推测其工作流程如下图所示:



[![](https://p3.ssl.qhimg.com/t013ae1cc46ca2e38c9.png)](https://p3.ssl.qhimg.com/t013ae1cc46ca2e38c9.png)



当豆浆机和手机不在同一局域网环境内时,豆浆机和云端保持连接,手机通过app向云端发送控制指令,云端收到指令后会向豆浆机发送启动指令。

当豆浆机和手机在同一局域网环境内时,手机直接向豆浆机发送指令。

### 分析攻击点

通过流程分析,发现设备一般处于无线路由器的内网中,想直接发送指令比较困难,而控制云端直接发送指令难度较大,所以要想对设备进行批量劫持,最快速有效的途径就是在移动设备到云端的通信中进行劫持攻击。

## 0x02漏洞挖掘

将设备和手机连入不同的wifi环境内,在app中点击启动快速豆浆,使用wireshark抓包分析。发现手机给云端发送的数据包并没有加密,通过对数据包尝试重放,发现豆浆机仍然可以启动,表明没有防重放机制。



[![](https://p2.ssl.qhimg.com/t017f48fb1305b2de36.png)](https://p2.ssl.qhimg.com/t017f48fb1305b2de36.png)



通过分析发现,在远程启动豆浆机的过程中,手机向云端共推送了三个数据包,我们抓取了两台不同豆浆机的控制指令,分析其中的不同以及可能进行劫持的地方。

手机向云端发送的启动两台不同豆浆机的命令的16进制数据包格式如下:

**豆浆机一:**

bb00000100078bdcbfc30e4d47822cd7086159df8a0037010001eea00030078bdcbfc30e4d47822cd7086159df8a974d13172a5b4e6e9bf8da0c13a7cae900000000000000000000000000000000

cc00000100000b00000100b0000400020000

cc00000100000700000100b20000

**豆浆机二:**

bb000001001e386b143bcc45738d782eededcf0bcb0027010002ee0000201e386b143bcc45738d782eededcf0bcbb724f10d9b99490a927031b41aac4de100000000000000000000000000000000

cc00000100000b00000100b0000400020000

cc00000100000700000100b20000

通过分析发现,手机向云端发送的用于控制两个设备的数据包仅有两处不同(标红位置),并且是一模一样的32位字符串。那么这个32位的字符串是什么呢?

通过继续对数据包的搜索分析,发现在手机打开app时有如下的http请求:



[![](https://p5.ssl.qhimg.com/t014d8546957b684fbe.png)](https://p5.ssl.qhimg.com/t014d8546957b684fbe.png)



在http请求返回包中的did参数中我们找到了这个字符串,根据参数的命名猜测,did这个参数的大意应该是deviceid,也就是设备id的意思。于是我们推测,在启动豆浆机的过程中,九阳没有做有效的身份认证,只需要知道设备的deviceid便可以直接启动豆浆机。

那么我们要如何获取别人的did呢?通过观察http请求时的参数,发现did是根据sessionkey获取的,请求如下:

http://xxx.joyoung.com/ia/appapi/userdev?param=`{`"sessionkey":"bcaaef7a1b554039b741391946xxxxxx","op_action":"query"`}`

sessionkey是九阳分配给用户的身份认证信息,sessionkey一旦生成是不会改变的,拥有了用户的sessionkey我们不仅可以获取到用户的各种信息,还可以对用户的账户资料、头像等进行更改。

我们继续搜索数据包,发现sessionkey是这样获取的。



[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t010c737712be007cb4.png)



http://xxx.joyoung.com/ia/appapi/user?param=`{`"op_action":"regTempUser","mob_data":`{`"mobile_id":"866251020xxxxxx"`}``}`

发现是根据一个叫做mobile_id的参数来获取的sessionkey,那么这个mobile_id又是什么呢?通过逆向apk,我们从源代码中分析出,这个mobile_id其实就是手机的imei串号。



[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015e73e40c13932954.png)





[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t017e76c6e8158e10fc.png)



总结我们刚才的分析,我们整理出了这样的攻击思路:

通过imei串号获取用户sessionkey→通过sessionkey获取设备id→通过设备id直接控制设备。

## 0x03漏洞利用

编写一个python脚本遍历获取设备id:



[![](https://p4.ssl.qhimg.com/t014f2a190f8ad7058e.png)](https://p4.ssl.qhimg.com/t014f2a190f8ad7058e.png)



经过一段时间后,我们通过遍历获得到了一批did。



[![](https://p1.ssl.qhimg.com/t017316a4bb581e5ffd.png)](https://p1.ssl.qhimg.com/t017316a4bb581e5ffd.png)



当我们拿到了这一批设备id之后,可以直接向云端发包来批量启动和控制豆浆机。想想还有点小激动呢~

## 0x04总结

总结起来,九阳这款豆浆机还是暴露出了诸多当前智能硬件厂商普遍存在的安全问题:

1.敏感数据在传输中没有进行任何加密,导致黑客可轻易获取控制指令、设备id等明文信息。

2.对于设备控制没有做有效的身份认证,只是将设备id等单一因素作为身份鉴权标识,导致黑客可以通过伪造、遍历等手段轻易控制其他设备。

3.云平台上存在传统的web方面的漏洞,导致攻击者可以越权获取到其他用户的设备信息。之前九阳的云平台还曝出过多个sql注入等高风险的web安全漏洞,这也是当前诸多智能硬件厂商普遍存在的安全问题。
