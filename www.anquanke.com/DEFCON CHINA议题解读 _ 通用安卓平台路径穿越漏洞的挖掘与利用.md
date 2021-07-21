> 原文链接: https://www.anquanke.com//post/id/145005 


# DEFCON CHINA议题解读 | 通用安卓平台路径穿越漏洞的挖掘与利用


                                阅读量   
                                **117117**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01ca64c97f45e16158.jpg)](https://p3.ssl.qhimg.com/t01ca64c97f45e16158.jpg)

**sd[@dmzlab](https://github.com/dmzlab)**

## 简介

在本次的defcon China上，来自于360 Alpha团队的向小波与杨文林的“几种通用的安卓平台路径穿越漏洞的挖掘与利用姿势”议题介绍相关Android通用的几种路径穿越漏洞。路径穿越漏洞轻则文件写入，文件下载等。重则造成替换关键文件造成远程命令执行等操作议题中有。



## Content Provider文件目录遍历漏洞

首先了解一下ContentProvider组件是Android四大组件之一，其核心功能是提供应用件的统一数据访问方式类似于C/S架构。其中ContentProvider提供了直接操作文件的方法这里只需重写ContentProvider中的openFile()方法即可操作文件，如果对文件路径没有进行限制就会造成路径穿越漏洞。

需要在Androidmanifest.xml中声明provider标签为**true**。

```
&lt;provider
    android:name=".SampleContentProvider"
    android:authorities="mydownloadcontentprovider"
    android:exported="true" /&gt;
```

其中authority是用于通过ContentProvider访问数据的URI权限，并且将导出为true的设置允许其他应用程序使用该内容提供者。

```
public class SampleContentProvider extends ContentProvider `{`

    @Override
    public ParcelFileDescriptor openFile(Uri uri, String mode) throws FileNotFoundException `{`
        File file = new File(Environment.getExternalStorageDirectory() +"Download/",uri.getPath());
        return ParcelFileDescriptor.open(file , ParcelFileDescriptor.READ_ONLY_MODE);
    `}`
 `}`
```

当使用adb发送如下命令就会造成Poc：`adb shell content open content://mydownloadcontentprovider/..%2f..%2f..%2f..%2f..%2fsdcard%2freadme.txt`



## 即时通讯应用程序中的目录遍历

在一些IM中都提供一些像好友发送文件的功能，但如果处理不当就会造成目录遍历。这里以CVE-2018-10067 为例通过HOOK框架修改文件为畸形文件就会只要对方点击下载即可生成到对应文件夹。

如图所示：

[![](https://p5.ssl.qhimg.com/t01c5ddbf862ce72516.jpg)](https://p5.ssl.qhimg.com/t01c5ddbf862ce72516.jpg)

还有中转式IRC网络聊天工具IRCCloud，攻击者可以强制IRC Cloud应用程序将任意文件复制到任意目录。

**主要代码如下：**

```
protected void onResume() `{` 
//...
 if (getSharedPreferences("prefs", 0).getString("session_key", "").length() &gt; 0) `{` 
//...
 this.mUri = (Uri) getIntent().getParcelableExtra("android.intent.extra.STREAM"); // getting attacker provided uri 
if (this.mUri != null) `{` 
this.mUri = MainActivity.makeTempCopy(this.mUri, this); // copying file from this uri to /data/data/com.irccloud.android/cache/
 `}`

public static Uri makeTempCopy(Uri fileUri, Context context, String original_filename) `{` // original_filename = mUri.getLastPathSegment() //... 
try `{` 
Uri out = Uri.fromFile(new File(context.getCacheDir(), original_filename)); Log.d("IRCCloud", "Copying file to " + out); 
InputStream is = IRCCloudApplication.getInstance().getApplicationContext().getContentResolver().openInputStream(fileUri);
 OutputStream os = IRCCloudApplication.getInstance().getApplicationContext().getContentResolver().openOutputStream(out);
 byte[] buffer = new byte[8192];
 while (true) `{` 
int len = is.read(buffer); 
if (len != -1) `{`
 os.write(buffer, 0, len);
 //...
```

通过`intent.putExtra("android.intent.extra.STREAM", uri);`调用 `IRCCloudApplication.getInstance().getApplicationContext().getContentResolver().openInputStream(fileUri);`会通过**openInputStream(…)**方法自动解码指定的uri。所以会访问我的符号链接文件。

这里值得注意的是，<br>**这个漏洞也允许覆盖任意文件。因此，攻击者也可以替换您的受保护文件并替代相关的历史记录。**



## 在android邮箱应用中存在目录遍历漏洞

在Android一些邮件应用中附件下载中存在目录遍历问题。如果对应用程序中的附件文件名没有路径清理，就会造成相关的目录遍历。<br>
如图Filename1是Gmail，Filename2是outlook。

[![](https://p1.ssl.qhimg.com/t01ceb531c14de64614.png)](https://p1.ssl.qhimg.com/t01ceb531c14de64614.png)

相关exp地址：

Gmail：[https://www.exploit-db.com/exploits/43189/](https://www.exploit-db.com/exploits/43189/)

Outlook:[https://www.exploit-db.com/exploits/43353/](https://www.exploit-db.com/exploits/43353/)



## Web浏览器文件中的ZIP解压缩

这里作者以CVE-2018-8084 搜狗浏览器目录遍历为例介绍如果浏览器解压下载文件时如果文件使用恶意文件名，就会存在解压时生成对于畸形文件，并且拥有重写文件的权限，如果直接在libvplayer.so文件中写入shell，就会造成远程代码执行效果。

如图：

[![](https://p2.ssl.qhimg.com/t01ced749ae22ed11b8.png)](https://p2.ssl.qhimg.com/t01ced749ae22ed11b8.png)

[![](https://p3.ssl.qhimg.com/t01032dab0a7df03e7b.png)](https://p3.ssl.qhimg.com/t01032dab0a7df03e7b.png)



## 应用热更新中造成文件目录遍历

以QQEmail的CVE-2018-5722 为例在attachPatchDex(…)方法中使用`new File(arg8,"dex").listFiles(new DexFiler())`会查找所有的dex文件进行加载。

## [![](https://p2.ssl.qhimg.com/t01696c4f1dafd69eda.png)](https://p2.ssl.qhimg.com/t01696c4f1dafd69eda.png)[![](https://p2.ssl.qhimg.com/t01696c4f1dafd69eda.png)](https://p2.ssl.qhimg.com/t01696c4f1dafd69eda.png)



## 通过修改smali造成文件目录遍历

在一些应用中一些方法中使用固定路径，对于这类应用可以进行修改**smali**文件进行目录遍历攻击。

[![](https://p3.ssl.qhimg.com/t016e93ec2d39aeecca.png)](https://p3.ssl.qhimg.com/t016e93ec2d39aeecca.png)



## 修复方案
1. 用哈希重命名或关联下载的文件
1. 规范用户可控制文件名
1. 避免读取SD卡上的重要文件
1. 检查重要文件的完整性


## 引用

[https://hackerone.com/reports/288955](https://hackerone.com/reports/288955)
