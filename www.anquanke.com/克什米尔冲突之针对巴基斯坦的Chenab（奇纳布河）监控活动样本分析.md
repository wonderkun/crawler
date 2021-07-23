> 原文链接: https://www.anquanke.com//post/id/189444 


# 克什米尔冲突之针对巴基斯坦的Chenab（奇纳布河）监控活动样本分析


                                阅读量   
                                **733640**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t015fe49c507681c71a.jpg)](https://p3.ssl.qhimg.com/t015fe49c507681c71a.jpg)



## 背景

印巴冲突历来已久，其归根到底是克什米尔问题，克什米尔争端是指印度和巴基斯坦对查谟和克什米尔地区主权纷争而引发的一系列问题，克什米尔争端是英殖民主义在1947年撤出印度时留下的。

2019年10月5日，印控克什米尔地区政府办公室遭到手榴弹袭击，目前已造成至少14人受伤，再次加剧当地紧张气氛。6日，数千名巴控克什米尔地区民众开始聚集在印巴实际控制区分界线附近，抗议印控克什米尔地区被封锁。巴基斯坦总理伊姆兰·汗随后在社交平台上表示，希望民众不要越线，任何对印控克什米尔地区的人道主义援助，都会“被印度利用”。

自8月5日印度政府宣布取消宪法赋予印控克什米尔地区的特殊地位后,印巴局势骤然升级。取消特殊地位意味着印控克什米尔地区曾享有的自治权不复存在,而印度宪法将完全适用于这里。印度还封锁了印控克什米尔大部分地区,切断当地对外通讯,包括手机、互联网和固线电话,并增派军队到边界地区。这一单方面改变克什米尔现状的做法立即招来巴基斯坦强烈反弹,巴方随即决定降低与印度的外交关系级别,并中断双边贸易。

而近日，奇安信病毒响应中心捕捉到了一起极具目的性的安卓APK攻击，经过研判发现其攻击目标疑似为巴基斯坦。此次攻击事件涉及的样本乌尔都翻译为“河边” ，联系到奇纳布河（Chenab River）流域发生过印巴水资源争议，根据1960年9月达成《印度河水协定》。根据协定，奇纳河、印度河及杰赫勒姆河划归巴基斯坦。奇纳布河（Chenab River）上游经过经克什米尔查谟（Jammu）地区，目前是巴基斯坦控制区域。有理由相信在8月5日之后，各方在地区的监控会加强，这次针对奇纳布河（Chenab River）上游的监控活动，我们正式命名为Chenab。

[![](https://p4.ssl.qhimg.com/t012cc03bff84ad8d87.png)](https://p4.ssl.qhimg.com/t012cc03bff84ad8d87.png)



## 诱饵分析

这次捕获到的apk样本名为“ندائےحق”(乌尔都语：河边)，大家都知道乌尔都语为巴基斯坦的国语，通过伪装为正常应用(恶意样本加载正常应用)来实现全面监控的作用，能实时捕捉到巴基斯坦国内最新动态。“河边”代号可能是基于历史与地理位置，奇纳布河（Chenab River）存在争议，奇纳布河（Chenab River）上游又经过克什米尔地区，使人不得不去联想到印巴克什米尔冲突，近年来在“克什米尔”地区的冲突也是愈演愈烈。

通过关联样本分析发现，此框架下适用任何针对任何app进行伪装，在关联样本中发现疑似针对巴基斯坦来伪装相关应用，具有很强的针对性，疑似印度针对巴基斯坦近期制定了监控计划。

诱饵APP图标：           正常APP图标：

[![](https://p4.ssl.qhimg.com/t014fcb952f3fca6ebe.png)](https://p4.ssl.qhimg.com/t014fcb952f3fca6ebe.png)     [![](https://p3.ssl.qhimg.com/t01bf707c1a13629994.png)](https://p3.ssl.qhimg.com/t01bf707c1a13629994.png)



样本运行截图：

[![](https://p4.ssl.qhimg.com/t013eb6049cd312a784.png)](https://p4.ssl.qhimg.com/t013eb6049cd312a784.png)

样本申请的权限：

[![](https://p2.ssl.qhimg.com/t011495e232185bfcf7.png)](https://p2.ssl.qhimg.com/t011495e232185bfcf7.png)



## 样本分析

### 样本概况
<td style="width: 84.8pt;" valign="top">文件名称</td><td style="width: 298.8pt;" valign="top">29E94BC62CBFA221A051E07E23588016.apk</td>
<td style="width: 84.8pt;" valign="top">软件名称</td><td style="width: 298.8pt;" valign="top">ندائےحق</td>
<td style="width: 84.8pt;" valign="top">软件名称翻译</td><td style="width: 298.8pt;" valign="top">河边</td>
<td style="width: 84.8pt;" valign="top">软件包名</td><td style="width: 298.8pt;" valign="top">com.gellery.services</td>
<td style="width: 84.8pt;" valign="top">安装图标</td><td style="width: 298.8pt;" valign="top">[![](https://p3.ssl.qhimg.com/t01f2ca4a7099644df8.png)](https://p3.ssl.qhimg.com/t01f2ca4a7099644df8.png)</td>

### 样本行为描述

此次捕捉的针对阿拉伯国家的恶意样本，通过释放加载正常的应用程序，

隐藏自身图标来实现隐藏自身，让用户误以为安装并更新了一个正常的应用程序。此恶意程序在后台运行时，则会通过远程服务器下发指令(总计56个指令)来实现对用户进行全方位的监控。其恶意操作有：上传短信信息、上传联系人信息、上传电话记录、屏蔽短信、监听手机状态、开启GPS、远程拍照等操作。

远控指令列表：
<td style="width: 90.45pt;" valign="top">网络指令</td><td style="width: 212.65pt;" valign="top">功能</td>
<td style="width: 90.45pt;" valign="top">msurc</td><td style="width: 212.65pt;" valign="top">设置音频源的值</td>
<td style="width: 90.45pt;" valign="top">udlt</td><td style="width: 212.65pt;" valign="top">更新配置信息并关闭远程连接</td>
<td style="width: 90.45pt;" valign="top">nofia</td><td style="width: 212.65pt;" valign="top">预留</td>
<td style="width: 90.45pt;" valign="top">setscrn</td><td style="width: 212.65pt;" valign="top">开启截屏</td>
<td style="width: 90.45pt;" valign="top">nofid</td><td style="width: 212.65pt;" valign="top">结束前台服务时删除通知</td>
<td style="width: 90.45pt;" valign="top">uclntn</td><td style="width: 212.65pt;" valign="top">设置用户ID并更新设置</td>
<td style="width: 90.45pt;" valign="top">setnoti</td><td style="width: 212.65pt;" valign="top">开启通知服务</td>
<td style="width: 90.45pt;" valign="top">setgpse</td><td style="width: 212.65pt;" valign="top">开启GPS</td>
<td style="width: 90.45pt;" valign="top">info</td><td style="width: 212.65pt;" valign="top">获取设备基本信息及配置信息</td>
<td style="width: 90.45pt;" valign="top">dirs/fldr</td><td style="width: 212.65pt;" valign="top">获取SD卡根目录信息</td>
<td style="width: 90.45pt;" valign="top">fles</td><td style="width: 212.65pt;" valign="top">获取指定目录下文件信息</td>
<td style="width: 90.45pt;" valign="top">ffldr</td><td style="width: 212.65pt;" valign="top">获取指定目录下的文件及目录信息</td>
<td style="width: 90.45pt;" valign="top">filsz</td><td style="width: 212.65pt;" valign="top">获取文件信息</td>
<td style="width: 90.45pt;" valign="top">notify</td><td style="width: 212.65pt;" valign="top">获取_HAENTIFI</td>
<td style="width: 90.45pt;" valign="top">file/afile</td><td style="width: 212.65pt;" valign="top">获取文件数据</td>
<td style="width: 90.45pt;" valign="top">thumb</td><td style="width: 212.65pt;" valign="top">获取图片</td>
<td style="width: 90.45pt;" valign="top">cnls</td><td style="width: 212.65pt;" valign="top">设置isCancl的值</td>
<td style="width: 90.45pt;" valign="top">delnotif</td><td style="width: 212.65pt;" valign="top">删除_HAENTIFI文件</td>
<td style="width: 90.45pt;" valign="top">unsnotif</td><td style="width: 212.65pt;" valign="top">注销通知服务</td>
<td style="width: 90.45pt;" valign="top">setnotif</td><td style="width: 212.65pt;" valign="top">注册通知服务</td>
<td style="width: 90.45pt;" valign="top">delt</td><td style="width: 212.65pt;" valign="top">删除文件</td>
<td style="width: 90.45pt;" valign="top">dowf</td><td style="width: 212.65pt;" valign="top">下载指定文件</td>
<td style="width: 90.45pt;" valign="top">capbcam</td><td style="width: 212.65pt;" valign="top">后置摄像头拍照并保存</td>
<td style="width: 90.45pt;" valign="top">capfcam</td><td style="width: 212.65pt;" valign="top">前置摄像头拍照并保存</td>
<td style="width: 90.45pt;" valign="top">capscrn</td><td style="width: 212.65pt;" valign="top">开启截屏</td>
<td style="width: 90.45pt;" valign="top">capscrns</td><td style="width: 212.65pt;" valign="top">开启连续截屏</td>
<td style="width: 90.45pt;" valign="top">scresize</td><td style="width: 212.65pt;" valign="top">设置屏幕大小</td>
<td style="width: 90.45pt;" valign="top">scrtops</td><td style="width: 212.65pt;" valign="top">发送广播</td>
<td style="width: 90.45pt;" valign="top">supdat</td><td style="width: 212.65pt;" valign="top">安装并运行指定的apk</td>
<td style="width: 90.45pt;" valign="top">runf</td><td style="width: 212.65pt;" valign="top">启动指定的应用</td>
<td style="width: 90.45pt;" valign="top">listf</td><td style="width: 212.65pt;" valign="top">向服务器回传文件数据</td>
<td style="width: 90.45pt;" valign="top">procl</td><td style="width: 212.65pt;" valign="top">向服务器回传运行程序列表信息</td>
<td style="width: 90.45pt;" valign="top">endpo</td><td style="width: 212.65pt;" valign="top">关闭指定应用的进程</td>
<td style="width: 90.45pt;" valign="top">calsre</td><td style="width: 212.65pt;" valign="top">设置电话记录的配置信息</td>
<td style="width: 90.45pt;" valign="top">recpth</td><td style="width: 212.65pt;" valign="top">上传_HAATNECS_</td>
<td style="width: 90.45pt;" valign="top">calstp</td><td style="width: 212.65pt;" valign="top">设置电话记录的配置为false</td>
<td style="width: 90.45pt;" valign="top">stsre</td><td style="width: 212.65pt;" valign="top">开启录音</td>
<td style="width: 90.45pt;" valign="top">stpre</td><td style="width: 212.65pt;" valign="top">停止录音</td>
<td style="width: 90.45pt;" valign="top">conta</td><td style="width: 212.65pt;" valign="top">获取联系人信息</td>
<td style="width: 90.45pt;" valign="top">clogs</td><td style="width: 212.65pt;" valign="top">上传电话记录</td>
<td style="width: 90.45pt;" valign="top">vibr\vibrate</td><td style="width: 212.65pt;" valign="top">设置手机震动参数</td>
<td style="width: 90.45pt;" valign="top">stoast</td><td style="width: 212.65pt;" valign="top">显示指定的通知信息</td>
<td style="width: 90.45pt;" valign="top">gcall</td><td style="width: 212.65pt;" valign="top">拨打指定号码</td>
<td style="width: 90.45pt;" valign="top">sesms</td><td style="width: 212.65pt;" valign="top">向指定号码发送短信</td>
<td style="width: 90.45pt;" valign="top">lntwok</td><td style="width: 212.65pt;" valign="top">上传本地网络信息</td>
<td style="width: 90.45pt;" valign="top">lgps</td><td style="width: 212.65pt;" valign="top">开启GPS并进行上传</td>
<td style="width: 90.45pt;" valign="top">clping</td><td style="width: 212.65pt;" valign="top">上传ping</td>
<td style="width: 90.45pt;" valign="top">smslg</td><td style="width: 212.65pt;" valign="top">上传短信信息</td>
<td style="width: 90.45pt;" valign="top">delth</td><td style="width: 212.65pt;" valign="top">删除_HAETALOG_</td>
<td style="width: 90.45pt;" valign="top">smsmon</td><td style="width: 212.65pt;" valign="top">注册屏蔽短信服务</td>
<td style="width: 90.45pt;" valign="top">smsmons</td><td style="width: 212.65pt;" valign="top">注销屏蔽短信服务</td>
<td style="width: 90.45pt;" valign="top">camoni</td><td style="width: 212.65pt;" valign="top">注册电话状态监听服务</td>
<td style="width: 90.45pt;" valign="top">camonis</td><td style="width: 212.65pt;" valign="top">注销电话状态监听服务</td>

### 详细代码分析

1、“黑加白”实现隐藏自身

恶意样本运行后会直接从raw目录下释放myapps并保存为myapps.apk,同时会运行此正常的apk应用。

[![](https://p4.ssl.qhimg.com/t0193b67d7edd3aa1b1.png)](https://p4.ssl.qhimg.com/t0193b67d7edd3aa1b1.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t018429710b0e99b72f.png)

当运行了真实的正常apk后，则会隐藏恶意程序自身图标，在后台进行远控操作，这样呈现给用户的效果是安装了一个正常的应用程序

[![](https://p2.ssl.qhimg.com/t01ce3addeceff2216e.png)](https://p2.ssl.qhimg.com/t01ce3addeceff2216e.png)

2、通过实时更新配置文件，来灵活切换远控服务器

连接远程服务器后，则可通过网络发送指令数据包进行远程控制操作。

远程服务器的IP端口信息:

服务器：173.249.50.34 和 shareboxs.net

端口：12182

[![](https://p4.ssl.qhimg.com/t015e7a9dd8b9e76374.png)](https://p4.ssl.qhimg.com/t015e7a9dd8b9e76374.png)

通过配置信息来决定是否连接ip或者域名：

[![](https://p5.ssl.qhimg.com/t01ac1094ebcb55377f.png)](https://p5.ssl.qhimg.com/t01ac1094ebcb55377f.png)

3、网络远控指令

指令msurc：设置音频源的值

[![](https://p3.ssl.qhimg.com/t014c833ecac510bd2d.png)](https://p3.ssl.qhimg.com/t014c833ecac510bd2d.png)

指令udlt: 更新配置信息并关闭远程连接

[![](https://p5.ssl.qhimg.com/t0120efc8e7453d53c6.png)](https://p5.ssl.qhimg.com/t0120efc8e7453d53c6.png)

[![](https://p0.ssl.qhimg.com/t015a245c1fbfb5fe03.png)](https://p0.ssl.qhimg.com/t015a245c1fbfb5fe03.png)

指令setscrn：开启截屏

[![](https://p5.ssl.qhimg.com/t018d84de33d1b15ef5.png)](https://p5.ssl.qhimg.com/t018d84de33d1b15ef5.png)

[![](https://p3.ssl.qhimg.com/t019d62e9b272553c5b.png)](https://p3.ssl.qhimg.com/t019d62e9b272553c5b.png)

指令nofid：结束前台服务时删除通知

[![](https://p2.ssl.qhimg.com/t019bb7ac24ef9a1dda.png)](https://p2.ssl.qhimg.com/t019bb7ac24ef9a1dda.png)

指令uclntn：设置用户ID并更新设置

[![](https://p4.ssl.qhimg.com/t01c4464e16e26ea11d.png)](https://p4.ssl.qhimg.com/t01c4464e16e26ea11d.png)

指令setnoti: 开启通知服务

[![](https://p1.ssl.qhimg.com/t01cb524c41b9e6011d.png)](https://p1.ssl.qhimg.com/t01cb524c41b9e6011d.png)

[![](https://p0.ssl.qhimg.com/t01590f7cb8b302feaa.png)](https://p0.ssl.qhimg.com/t01590f7cb8b302feaa.png)

指令setgpse:开启GPS

[![](https://p5.ssl.qhimg.com/t01bed518f09e369c2c.png)](https://p5.ssl.qhimg.com/t01bed518f09e369c2c.png)

[![](https://p4.ssl.qhimg.com/t01088c54d36872a2f6.png)](https://p4.ssl.qhimg.com/t01088c54d36872a2f6.png)

指令info：获取设备基本信息及配置信息

[![](https://p0.ssl.qhimg.com/t01bd50e5daeb8c122d.png)](https://p0.ssl.qhimg.com/t01bd50e5daeb8c122d.png)

[![](https://p3.ssl.qhimg.com/t01469e5227cb865db7.png)](https://p3.ssl.qhimg.com/t01469e5227cb865db7.png)

指令dirs和指令fldr: 获取SD卡根目录信息

[![](https://p5.ssl.qhimg.com/t01c6d95d2859b8128e.png)](https://p5.ssl.qhimg.com/t01c6d95d2859b8128e.png)

指令fles: 获取指定目录下文件信息

[![](https://p5.ssl.qhimg.com/t01b5df4fc17eef9eed.png)](https://p5.ssl.qhimg.com/t01b5df4fc17eef9eed.png)

指令ffldr：获取指定目录下的文件及目录信息

[![](https://p0.ssl.qhimg.com/t01bd759e984c8cdeb6.png)](https://p0.ssl.qhimg.com/t01bd759e984c8cdeb6.png)

指令filsz: 获取文件信息

[![](https://p2.ssl.qhimg.com/t012fbb7aa1e5e2455e.png)](https://p2.ssl.qhimg.com/t012fbb7aa1e5e2455e.png)

指令notifi: 获取_HAENTIFI信息

[![](https://p3.ssl.qhimg.com/t01cb357e2e4c7bddf0.png)](https://p3.ssl.qhimg.com/t01cb357e2e4c7bddf0.png)

指令file和afile：获取文件数据

[![](https://p4.ssl.qhimg.com/t0155e107d774907d31.png)](https://p4.ssl.qhimg.com/t0155e107d774907d31.png)

指令thumb:获取图片

[![](https://p4.ssl.qhimg.com/t01551cb1bc1ccb4132.png)](https://p4.ssl.qhimg.com/t01551cb1bc1ccb4132.png)

指令cnls: 设置isCancl的值

[![](https://p0.ssl.qhimg.com/t01054ed9ff46c62a82.png)](https://p0.ssl.qhimg.com/t01054ed9ff46c62a82.png)

指令delnotif: 删除_HAENTIFI

[![](https://p5.ssl.qhimg.com/t01004d033f587ed22f.png)](https://p5.ssl.qhimg.com/t01004d033f587ed22f.png)

指令unsnotif: 注销通知服务

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011a300cb275e9b1b0.png)

指令setnotif: 注册通知服务

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t013ef9637d1447d741.png)

指令delt：删除文件

[![](https://p5.ssl.qhimg.com/t0129e93b59cce7656a.png)](https://p5.ssl.qhimg.com/t0129e93b59cce7656a.png)

指令dowf：下载指定文件

[![](https://p0.ssl.qhimg.com/t0132e85203349c191b.png)](https://p0.ssl.qhimg.com/t0132e85203349c191b.png)

指令capbcam：后置摄像头拍照并保存

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t014e2bdefd93cad474.png)

指令capfcam：后置摄像头拍照并保存

[![](https://p1.ssl.qhimg.com/t0150aaa92c2b4d933b.png)](https://p1.ssl.qhimg.com/t0150aaa92c2b4d933b.png)

指令capscrn：开启截屏

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0124bc79b69565e714.png)

指令capscrn：开启连续截屏

[![](https://p5.ssl.qhimg.com/t01d7ede6a86268cf6b.png)](https://p5.ssl.qhimg.com/t01d7ede6a86268cf6b.png)

指令scresize:设置屏幕大小

[![](https://p0.ssl.qhimg.com/t01ab3792701367bb13.png)](https://p0.ssl.qhimg.com/t01ab3792701367bb13.png)

指令scrtops:发送广播

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018ffae8cd84fa44d6.png)

指令supdat:安装并运行指定的apk

[![](https://p2.ssl.qhimg.com/t01fcee978bda14f937.png)](https://p2.ssl.qhimg.com/t01fcee978bda14f937.png)

指令runf: 启动指定的应用

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016db8a0a638765257.png)

指令listf: 向服务器回传文件数据

[![](https://p3.ssl.qhimg.com/t012c87e14da14b605b.png)](https://p3.ssl.qhimg.com/t012c87e14da14b605b.png)

指令procl: 向服务器回传运行程序列表信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e681f53714d43b45.png)

指令endpo: 关闭指定应用的进程

[![](https://p3.ssl.qhimg.com/t01aad4409fad32a3dd.png)](https://p3.ssl.qhimg.com/t01aad4409fad32a3dd.png)

指令calsre: 设置电话记录的配置信息

[![](https://p4.ssl.qhimg.com/t018f15219a8edd1730.png)](https://p4.ssl.qhimg.com/t018f15219a8edd1730.png)

指令recpth: 上传_HAATNECS_

[![](https://p4.ssl.qhimg.com/t01dfec5c733e23ae87.png)](https://p4.ssl.qhimg.com/t01dfec5c733e23ae87.png)

指令calstp: 设置电话记录的配置为false

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0127360a17a689fa71.png)

指令stsre：开启录音

[![](https://p2.ssl.qhimg.com/t01f89c556ae70c58b9.png)](https://p2.ssl.qhimg.com/t01f89c556ae70c58b9.png)

指令stpre：停止录音

[![](https://p5.ssl.qhimg.com/t011f0745de290d7f1a.png)](https://p5.ssl.qhimg.com/t011f0745de290d7f1a.png)

指令conta：获取联系人信息

[![](https://p3.ssl.qhimg.com/t01d93604effe06f8b1.png)](https://p3.ssl.qhimg.com/t01d93604effe06f8b1.png)

指令clogs:上传电话记录

[![](https://p3.ssl.qhimg.com/t01a4b4ab110ad6e502.png)](https://p3.ssl.qhimg.com/t01a4b4ab110ad6e502.png)

指令vibr\vibrate:设置手机震动参数

[![](https://p1.ssl.qhimg.com/t0141f74392cab835b3.png)](https://p1.ssl.qhimg.com/t0141f74392cab835b3.png)

指令stoast：显示指定的通知信息

[![](https://p1.ssl.qhimg.com/t01473bd83caecbd9f0.png)](https://p1.ssl.qhimg.com/t01473bd83caecbd9f0.png)

指令gcall：拨打指定号码

[![](https://p4.ssl.qhimg.com/t012f5c19d9ee49d1fd.png)](https://p4.ssl.qhimg.com/t012f5c19d9ee49d1fd.png)

指令sesms：向指定号码发送短信

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t018d802c896e2b9a80.png)

指令lntwok：上传本地网络信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01c8b3e3b319955157.png)

指令lgps:开启GPS并进行上传

[![](https://p2.ssl.qhimg.com/t015858f61cae128f5f.png)](https://p2.ssl.qhimg.com/t015858f61cae128f5f.png)

指令clping:上传ping

[![](https://p2.ssl.qhimg.com/t011e11c1320115d6c9.png)](https://p2.ssl.qhimg.com/t011e11c1320115d6c9.png)

指令smslg:上传短信信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t010101b76ee28664d7.png)

指令delth:删除_HAETALOG_

[![](https://p1.ssl.qhimg.com/t019fae27db337d30c7.png)](https://p1.ssl.qhimg.com/t019fae27db337d30c7.png)

指令smsmon:注册屏蔽短信服务

[![](https://p4.ssl.qhimg.com/t015758115e92dc4b5f.png)](https://p4.ssl.qhimg.com/t015758115e92dc4b5f.png)

指令smsmons:注销屏蔽短信服务

[![](https://p4.ssl.qhimg.com/t010351727684f64335.png)](https://p4.ssl.qhimg.com/t010351727684f64335.png)

指令camoni:注册电话状态监听服务

[![](https://p0.ssl.qhimg.com/t0191544b990029d793.png)](https://p0.ssl.qhimg.com/t0191544b990029d793.png)

指令camonis:注销电话状态监听服务

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t015a24a643cc15f83e.png)



## 同源分析

通过关联样本发现了使用同一框架的恶意程序，其核心功能代码大同小异（或减少功能），其主要的核心架构就是通过从res\raw\目录下释放myapps/myappes/myapp.apk(正常应用)然后安装运行，同时伪装恶意程序以隐藏图标的方式在后台一直运行监控获取用户信息。

[![](https://p4.ssl.qhimg.com/t014233dec149e35b28.png)](https://p4.ssl.qhimg.com/t014233dec149e35b28.png)

其利用框架为：

[![](https://p4.ssl.qhimg.com/t01dc98c235c12e7db4.png)](https://p4.ssl.qhimg.com/t01dc98c235c12e7db4.png)



## 总结

印巴冲突无疑是近年来比较火热的话题之一，本文中疑似针对巴基斯坦的apk样本监控分析，无疑是印巴交锋中的网络战争，谁能先获取对方的最新动向则能及时作出相对应的策略。如果网络战争失利了，无疑于失去先机。

奇安信病毒响应中心将持续对最新的恶意安卓APK攻击活动进行及时分析与更新，目前奇安信全系产品均可对此攻击活动进行报警。



## IOC

文件Hash：

29e94bc62cbfa221a051e07e23588016

aefaf256916cb229c42ffeb1bca18c39

3588b1efda1863a3a10e8230005d877d

f68617671f1a830648b93350e670f698

1095580e4bece45ce5aaefca6125e6e4

C2地址：

173.249.50.34:12182

shareboxs.net:12182
