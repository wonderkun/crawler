> 原文链接: https://www.anquanke.com//post/id/159696 


# 趋势macOS全家桶隐私窃取分析


                                阅读量   
                                **222550**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01529cad615100c3c2.jpg)](https://p1.ssl.qhimg.com/t01529cad615100c3c2.jpg)

## 0x0 概述

2018.9.10，网络曝光趋势科技做的 Mac 解压缩软件会上传用户浏览器历史记录，相关资料参考：

[Additional Mac App Store apps caught stealing and uploading browser history](https://9to5mac.com/2018/09/09/additional-mac-app-store-apps-caught-stealing-and-uploading-browser-history/)

[Get rid of Open Any Files: RAR Support](https://forums.malwarebytes.com/topic/217353-get-rid-of-open-any-files-rar-support/?tab=comments#comment-1195086)

[A Deceitful ‘Doctor’ in the Mac App Store](https://objective-see.com/blog/blog_0x37.html)

[趋势全家桶](https://success.trendmicro.com/data-collection-disclosure#DrMac)所有app信息如下：<br>[![](https://p2.ssl.qhimg.com/t01b226c2345994372b.png)](https://p2.ssl.qhimg.com/t01b226c2345994372b.png)

事件曝光之后，相关产品已经从appstore下架，只剩两个wifi相关app：<br>[![](https://p1.ssl.qhimg.com/t018f60641476ef9f30.png)](https://p1.ssl.qhimg.com/t018f60641476ef9f30.png)<br>[![](https://p5.ssl.qhimg.com/t01289e784a9db7b1cd.png)](https://p5.ssl.qhimg.com/t01289e784a9db7b1cd.png)

好在此前已经安装过部分相关应用，故借此对其分析验证<br>[![](https://p3.ssl.qhimg.com/t01809f0518aed08353.png)](https://p3.ssl.qhimg.com/t01809f0518aed08353.png)



## 0x1 隐私&amp;隐私政策

### <a class="reference-link" name="0x11%20%E6%83%85%E5%86%B5%E6%B1%87%E6%80%BB"></a>0x11 情况汇总

### 最终分析结果汇总如下：[![](https://p4.ssl.qhimg.com/t01f6676d75abe38ee9.png)](https://p4.ssl.qhimg.com/t01f6676d75abe38ee9.png)<a name="0x12%20%E9%83%A8%E5%88%86%E9%9A%90%E7%A7%81%E8%8E%B7%E5%8F%96%E6%96%B9%E5%BC%8F"></a>0x12 部分隐私获取方式

趋势全家桶系列app在初次运行时都会显示相关隐私政策，并要求申请相关资源访问权限，当用户允许后即可通过sandbox相关接口来访问相关隐私数据，获取方式如下：

|隐私|获取方式&amp;路径
|------
|Safari历史记录|Library/Safari/History.db
|Chrome历史记录|Library/Application Support/Google/Chrome
|Firefox历史记录|Library/Application Support/Firefox/Profiles/%@/places.sqlite
|AppStore历史记录|Library/Containers/com.apple.appstore/Data/Library/Caches/com.apple.appstore/WebKitCache/Version 11/Blobs
|装机列表|/usr/sbin/system_profiler -xml SPApplicationsDataType

### <a class="reference-link" name="0x13%20%E8%B6%8B%E5%8A%BF%E4%BA%A7%E5%93%81%E9%9A%90%E7%A7%81%E7%AD%96%E7%95%A5"></a>0x13 趋势产品隐私策略

以下为趋势的产品隐私策略

[Privacy Policy for Trend Micro Products and Services (Effective March 2018)](https://www.trendmicro.com/en_us/about/legal/privacy-policy-product.html)

激活产品时会获取的信息，都是比较常规数据<br>[![](https://p5.ssl.qhimg.com/t01fd1647d12ee25db1.png)](https://p5.ssl.qhimg.com/t01fd1647d12ee25db1.png)

部分服务所需的数据，其实比较敏感的有访问过的URL、域名、IP等信息，和可疑邮件的收发件人及附件等，当然具体都需要看实际产品功能来判断<br>[![](https://p5.ssl.qhimg.com/t012431b78fc99aa6ab.png)](https://p5.ssl.qhimg.com/t012431b78fc99aa6ab.png)



## 0x2 详细分析

### <a class="reference-link" name="0x21%20Dr.Unarchiver"></a>0x21 Dr.Unarchiver

Dr.Unarchiver产品信息如下：<br>[![](https://p1.ssl.qhimg.com/t01f658f75d827b2720.png)](https://p1.ssl.qhimg.com/t01f658f75d827b2720.png)

通过抓包分析实际并未发现上传隐私：<br>[![](https://p1.ssl.qhimg.com/t01983d5d2105d724cf.png)](https://p1.ssl.qhimg.com/t01983d5d2105d724cf.png)

然而程序代码中却明确出现Firefox、Chrome、Safari等浏览器记录数据库文件目录字符串：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01c0c096251b7efad7.png)

通过字符串跳入代码，即读取浏览器隐私的部分代码，以下为读取chrome记录：<br>[![](https://p0.ssl.qhimg.com/t01d9a6781f17b22e46.png)](https://p0.ssl.qhimg.com/t01d9a6781f17b22e46.png)读取Safari历史记录：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t017ad3145936394282.png)

Dr.Unarchiver里读取隐私部分主要位于-[DACollector *]模块中，从模块命名可以发现，除了3个浏览器记录，同时还读取了AppStore历史记录、设备装机列表、用户信息等。<br>[![](https://p3.ssl.qhimg.com/t01bb1ccc2da5d3d6cc.png)](https://p3.ssl.qhimg.com/t01bb1ccc2da5d3d6cc.png)

获取设备装机列表方式通过执行“/usr/sbin/system_profiler -xml SPApplicationsDataType“指令来完成：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01221decb8bdd7e0e7.png)

该指令执行后获取数据如下，包含了app的安装时间、路径、证书等信息：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t010435d0b5436f28c4.png)

另外比较有意思的地方为，程序中还有照片库的字符串及相关代码<br>[![](https://p1.ssl.qhimg.com/t018ceaea440590a28c.png)](https://p1.ssl.qhimg.com/t018ceaea440590a28c.png)

获取隐私后上传地址如下：<br>[![](https://p2.ssl.qhimg.com/t0123c8f9cced324bc9.png)](https://p2.ssl.qhimg.com/t0123c8f9cced324bc9.png)

趋势官网Dr. Unarchiver产品说明里明确说明会读取浏览器记录：

[Dr. Unarchiver for Mac Data Collection Notice](https://esupport.trendmicro.com/en-us/home/pages/technical-support/1120081.aspx)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t013f360493bef414e6.png)

### <a class="reference-link" name="0x22%20Dr.%20Antivirus"></a>0x22 Dr. Antivirus

下图为Dr. Antivirus界面：<br>[![](https://p0.ssl.qhimg.com/t01150f9c30b461ae5d.png)](https://p0.ssl.qhimg.com/t01150f9c30b461ae5d.png)

Dr. Antivirus中获取信息模块与Dr. Unarchiver完全一样：<br>[![](https://p1.ssl.qhimg.com/t01eb9064a8a7782a16.png)](https://p1.ssl.qhimg.com/t01eb9064a8a7782a16.png)

但相对的，多出了post回传模块，不过Dr. Antivirus作为反病毒软件，回传装机列表也属于正常行为：<br>[![](https://p2.ssl.qhimg.com/t01059857ffec3c9253.png)](https://p2.ssl.qhimg.com/t01059857ffec3c9253.png)

通过动态抓包，可以确定Dr. Antivirus会回传设备装机列表：<br>[![](https://p2.ssl.qhimg.com/t011110122a189d7382.png)](https://p2.ssl.qhimg.com/t011110122a189d7382.png)

另外会上传一个“file.zip“包，回传路径与Dr. Unarchiver分析一致：<br>[![](https://p4.ssl.qhimg.com/t01ebe36fc2a0235808.png)](https://p4.ssl.qhimg.com/t01ebe36fc2a0235808.png)

从上传的数据包中提取出“file.zip”文件，发现已经加密：<br>[![](https://p5.ssl.qhimg.com/t01b67f31192c875a01.png)](https://p5.ssl.qhimg.com/t01b67f31192c875a01.png)

分析该部分代码，发现使用密钥为“novirus”<br>[![](https://p0.ssl.qhimg.com/t01f9fa0a74f7d103ce.png)](https://p0.ssl.qhimg.com/t01f9fa0a74f7d103ce.png)

解密后可以看见都是获取的浏览器记录和app列表等信息：<br>[![](https://p3.ssl.qhimg.com/t016a6bf25c4f391f38.png)](https://p3.ssl.qhimg.com/t016a6bf25c4f391f38.png)

如下图为chrome浏览器记录：<br>[![](https://p2.ssl.qhimg.com/t01496529d55f2f5875.png)](https://p2.ssl.qhimg.com/t01496529d55f2f5875.png)其实甚至还单独筛出了google搜索记录：<br>[![](https://p1.ssl.qhimg.com/t013fb9805f9e5ebf78.png)](https://p1.ssl.qhimg.com/t013fb9805f9e5ebf78.png)

下图为趋势官网Dr. Antivirus产品说明，里面明确申明会读取app安装历史记录、当前装机列表、浏览器记录等隐私，作为反病毒软件读取app列表能理解，但回传浏览器记录、搜索记录等隐私就过了。

[Dr. Antivirus Data Collection NoticeA](https://esupport.trendmicro.com/en-us/home/pages/technical-support/1120079.aspx)<br>[![](https://p5.ssl.qhimg.com/t01fb7e599c805e5f05.png)](https://p5.ssl.qhimg.com/t01fb7e599c805e5f05.png)

### <a class="reference-link" name="0x23%20DrCleaner"></a>0x23 DrCleaner

DrCleaner界面如下：<br>[![](https://p5.ssl.qhimg.com/t01c541862e31f95c11.png)](https://p5.ssl.qhimg.com/t01c541862e31f95c11.png)

DrCleaner获取隐私信息模块名与之前二者有所不同，但获取的隐私、方法名、代码基本一样：<br>[![](https://p0.ssl.qhimg.com/t01b658e79b3d4d8294.png)](https://p0.ssl.qhimg.com/t01b658e79b3d4d8294.png)

DrCleaner同样使用“novirus”作为zip包加密密钥：<br>[![](https://p1.ssl.qhimg.com/t0194688cbe6e4e6942.png)](https://p1.ssl.qhimg.com/t0194688cbe6e4e6942.png)

下图为趋势官网Dr. Cleaner产品说明，里面明确申明会读取浏览器记录等隐私

[Dr. Cleaner Data Collection Disclosure][https://esupport.trendmicro.com/en-us/home/pages/technical-support/1119854.aspx](https://esupport.trendmicro.com/en-us/home/pages/technical-support/1119854.aspx)<br>[![](https://p5.ssl.qhimg.com/t019f93d56d0cf7abb9.png)](https://p5.ssl.qhimg.com/t019f93d56d0cf7abb9.png)

### <a class="reference-link" name="0x24%20DrBattery"></a>0x24 DrBattery

DrBattery初次运行会要求访问用户主目录（其他程序初次运行也都会申请相关访问权限）：<br>[![](https://p4.ssl.qhimg.com/t016a1143cb473c5d95.png)](https://p4.ssl.qhimg.com/t016a1143cb473c5d95.png)

DrBattery中有着与DrCleaner完全一样命名方式的隐私获取模块：<br>[![](https://p1.ssl.qhimg.com/t015985e1a137f5be5e.png)](https://p1.ssl.qhimg.com/t015985e1a137f5be5e.png)

下图为趋势官网DrBattery产品说明，里面明确申明会读取浏览器记录等隐私

[Dr. Battery Data Collection Notice](https://esupport.trendmicro.com/en-us/home/pages/technical-support/1120080.aspx)<br>[![](https://p5.ssl.qhimg.com/t01bd8a02654c81a869.png)](https://p5.ssl.qhimg.com/t01bd8a02654c81a869.png)

### <a class="reference-link" name="0x25%20AppManager"></a>0x25 AppManager

AppManager即App Uninstall初次运行要求申请相关访问权限，该应用中未发现相关隐私获取代码：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01c67d3b25a9cc274d.png)

下图为趋势官网App Uninstall产品说明，里面未申明会读取浏览器等相关隐私

[App Uninstall Data Collection Notice](https://esupport.trendmicro.com/en-us/home/pages/technical-support/1120078.aspx)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e7cfbd29d0ff529f.png)

### <a class="reference-link" name="0x26%20%E6%B5%8B%E7%BD%91%E9%80%9F%E5%A4%A7%E5%B8%88Dr.%20WiFi"></a>0x26 测网速大师Dr. WiFi

测网速大师Dr. WiFi运行界面，该app中未发现相关隐私获取代码：<br>[![](https://p3.ssl.qhimg.com/t0159bfa96773c7c406.png)](https://p3.ssl.qhimg.com/t0159bfa96773c7c406.png)

下图为趋势官网Dr. WiFi产品说明，里面未申明会读取浏览器等相关隐私

[Dr. WiFi Data Collection Disclosure](https://esupport.trendmicro.com/en-us/home/pages/technical-support/1120035.aspx)<br>[![](https://p4.ssl.qhimg.com/t01ef359f13d414bb36.png)](https://p4.ssl.qhimg.com/t01ef359f13d414bb36.png)

### <a class="reference-link" name="0x27%20%E5%AE%B6%E5%BA%AD%E7%BD%91%E7%BB%9C%E5%8D%AB%E5%A3%ABNetwork%20Scanner"></a>0x27 家庭网络卫士Network Scanner

家庭网络卫士Network Scanner初次运行显示的隐私政策及要求申请相关访问权限，该应用中未发现相关隐私获取代码：<br>[![](https://p3.ssl.qhimg.com/t01c2f742e5d221624f.png)](https://p3.ssl.qhimg.com/t01c2f742e5d221624f.png)

下图为趋势官网Network Scanner产品说明，里面未申明会读取浏览器等相关隐私

[HouseCall for Home Networks (for Windows &amp; Mac) v1.1.7 Data Collection Notice](https://esupport.trendmicro.com/en-us/home/pages/technical-support/1119968.aspx)<br>[![](https://p4.ssl.qhimg.com/t01ba75e61a0b585001.png)](https://p4.ssl.qhimg.com/t01ba75e61a0b585001.png)



## 0x3 小结

趋势全家桶还有少数几个app并未获取到，但从以上内容基本可以确定其确实有窃取用户浏览器记录、搜索记录、装机列表等隐私的行为，虽然其在隐私政策申明了相关信息（但真有用户会去仔细阅读么）

而在[A Deceitful ‘Doctor’ in the Mac App Store](https://objective-see.com/blog/blog_0x37.html)一文中，分析的应用为“Adware Doctor”，与本文趋势全家桶并非同一证书：<br>[![](https://p0.ssl.qhimg.com/t01c865b015bd1f43ca.png)](https://p0.ssl.qhimg.com/t01c865b015bd1f43ca.png)

但二者却有诸多相同点，如获取隐私的方法名及相关代码：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01aa24aaf0db6e97b4.png)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01fa8297286b64bffe.png)

通过sandbox接口访问数据部分模块，其类名、方法名、相关代码也基本一致，故推断二者可能为同一开发者（趋势的临时工？）<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0177cf8d2d83307555.png)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01676fa880f147bbc0.png)

在溯源过程中通常会参考绝对路径里的username，但这些app中均只有“autobuild”和“jenkinsbuld”两个id，开发者对自我有一定的隐藏意识：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c762495f6b788fe2.png)<br>[![](https://p5.ssl.qhimg.com/t01d273c9ae218aec67.png)](https://p5.ssl.qhimg.com/t01d273c9ae218aec67.png)

而[Jenkins](https://jenkins.io/)更有可能为开发者使用下图中集成工具时起的id<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d2e8a0d44f5dd851.png)
