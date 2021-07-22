> 原文链接: https://www.anquanke.com//post/id/170725 


# Chrome扩展在持久化中的应用


                                阅读量   
                                **145531**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者specterops，文章来源：posts.specterops.io
                                <br>原文地址：[https://posts.specterops.io/no-place-like-chrome-122e500e421f](https://posts.specterops.io/no-place-like-chrome-122e500e421f)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t011cd97983f0390ef4.png)](https://p0.ssl.qhimg.com/t011cd97983f0390ef4.png)



## 一、前言

[2009](https://googleblog.blogspot.com/2009/12/google-chrome-for-holidays-mac-linux.html)年12月，Chrome正式推出了扩展程序（extension），使用HTML、JavaScript以及CSS来扩展Chrome的功能。扩展可以使用Chrome API来阻止广告（ad）、改变浏览器UI、管理cookie，甚至能与桌面应用配合使用。用户可以在扩展安装过程中授予扩展一些权限，限制扩展行为。Chrome扩展可以使用许多原生API，因此也是隐藏恶意代码的潜在目标。随着EDR（端点检测与响应）产品的兴起以及macOS、Windows 10新引入的安全功能，端点安全性也得到了不少提升。然而对于macOS上的恶意Chrome扩展，现在仍然缺乏较好的检测机制。因此，Chrome扩展已经成为一种非常诱人的入侵及持久化载荷。本文介绍了macOS上利用Chrome扩展实现的一种载荷投递机制，介绍了自动更新功能在攻击过程中的应用，也介绍了使用[Apfell](https://github.com/its-a-feature/Apfell)的一个实际攻击样例，最后提出了一些基本但实际可操作的检测指南。



## 二、载荷投递

在macOS上，我们可以使用一些方法来合法地安装扩展程序。Google要求开发者通过web商店来投放扩展程序。[最近](https://blog.chromium.org/2018/06/improving-extension-transparency-for.html)Google修改了相关政策，导致用户无法从第三方网站安装扩展。攻击者虽然可以[继续](https://www.tripwire.com/state-of-security/security-data-protection/malicious-chrome-extension-which-sloppily-spied-on-academics-believed-to-originate-from-north-korea/)在web商店上托管扩展程序，但这个策略的推出的确限制了不少潜在风险。此外，我们在macOS上也可以使用移动配置描述文件（mobile configuration profile，`.mobileconfig`文件）来安装扩展。配置描述文件是macOS及iOS上的一种机制，可以用来管理各种设置，如壁纸、应用（如Google Chrome）等。用户可以通过鼠标双击或者在命令行中通过[profiles](http://krypted.com/mac-os-x/use-profiles-command-high-sierra/)命令来安装描述文件。移动配置描述文件采用XML格式并遵循相对简单的格式。为了创建移动配置描述文件，我们需要输入PayloadUUID、应用程序ID以及更新url（下文会介绍这一点）。如果想了解配置描述文件的更多信息，大家可以参考这两篇文章（[1](http://docs.jamf.com/9.97/casper-suite/administrator-guide/macOS_Configuration_Profiles.html)、[2](https://developer.apple.com/business/documentation/Configuration-Profile-Reference.pdf)），也可以参考[这个](https://gist.github.com/xorrior/8ee611d4f91b91f03ec16bed1324be56)模板文件。在配置文件中，`ExtensionInstallSources`键指定了URL值，表示可以从哪些源安装扩展。在URL的协议、主机以及URI字段中我们都可以使用通配符。`ExtensionInstallForceList`值表示可以未经用户同意就能安装且无法卸载的扩展列表。`PayloadRemovalDisallowed`键可以阻止非管理员用户卸载该描述文件。大家可以参考[此处](https://www.chromium.org/administrators/policy-list-3)资料了解可用来管理扩展及Google Chrome其他设置的一些键值。配置描述文件可以用来管理macOS的各种设置，我们可进一步深入分析，研究其在攻击场景中的应用。

关于配置描述文件有一点非常有趣，这些配置文件可以通过电子邮件来发送，并且[Gatekeeper](https://support.apple.com/en-us/HT202491)不会向终端用户提示任何警告（Gatekeeper是MacOS的代码签名强制验证工具）。然而系统将弹出一个提示窗口，请求用户确认安装描述文件。

[![](https://p1.ssl.qhimg.com/t0151c3471614b06b41.png)](https://p1.ssl.qhimg.com/t0151c3471614b06b41.png)

如果描述文件未经签名，则用户在输入管理员凭据前，会看到第二个弹出窗口：

[![](https://p5.ssl.qhimg.com/t010fa452fe5ff268a0.png)](https://p5.ssl.qhimg.com/t010fa452fe5ff268a0.png)

然而在安装经过签名的描述文件时，操作系统只会在安装过程中弹出一次窗口，然后就需要输入管理员密码。安装完毕后，我们可以在`Profiles`配置面板中查看描述文件的内容。如果描述文件未经签名，则会以红色高亮标出。

[![](https://p4.ssl.qhimg.com/t0133fa79532ff433fe.png)](https://p4.ssl.qhimg.com/t0133fa79532ff433fe.png)

现在我们已经为Chrome设置了扩展策略，当用户打开该应用时，就会向描述文件中设置的更新URL发出一系列web请求。更新URL应当指向一个manifest更新文件，其中指定了扩展文件(`.crx`文件)的应用ID以及URL。这里大家可以查阅官方提供的[autoupdate](https://developer.chrome.com/apps/autoupdate)文档，了解manifest示例文件。随后，Chrome会下载扩展，将其保存到`~/Library/Application Support/Google/Chrome/Default/Extensions/APPID`路径中。此时该扩展已经被载入浏览器中并成功执行。需要注意的是，在整个过程中，配置描述文件是唯一涉及到用户交互的一个环节。同样，在Windows上我们也可以修改注册表来悄悄安装扩展程序（可参考[此处](https://stackoverflow.com/questions/16056498/silent-install-of-chrome-extension-using-registry)资料）。然而如果安装源为第三方网站，Chrome只允许[**inline**](https://developer.chrome.com/webstore/inline_installation)安装模式。这种安装模式需要用户浏览第三方网站，网站需要将用户重定向到Chrome Web Store，最终完成安装过程。



## 三、自动更新

为了便于bug修复及安装安全更新，扩展可以支持自动更新。当扩展托管于Chrome Web商店时，Google就会接管扩展的更新过程。开发者只需要上传新版扩展，几个小时后，浏览器就会通过Web Store更新插件。如果扩展托管在Web Store之外，开发者可以具备更多的控制权。Chrome会使用`manifest.json`文件中的更新url来定期检查版本更新。在这个过程中，Chrome会读取manifest更新文件内容，将manifest中的版本信息与扩展的版本信息作比较。如果manifest版本更高，则浏览器会下载并安装新版扩展（大家可以参考[此处](https://gist.github.com/xorrior/c383baf3e626408e2c2eb4902798ea90)了解典型的manifest更新文件）。manifest更新文件采用XML格式，包含`APPID`以及指向`.crx`文件的一个`URL`。对攻击者而言，自动更新始终是一个非常不错的机制。如下两图所示，恶意扩展使用一个域名用来正常的C2通信，使用另一个域名来托管manifest更新文件以及扩展文件。设想一下，假如应急响应团队将某个C2域名标记为恶意域名，阻止与该域名的所有通信流量（1），然而与更新URL的通信流量仍然畅通无阻（2 &amp; 3）。攻击者可以更新manifest版本，修改C2域名（4）、更新URL，设置能修改扩展的某些核心代码。经过一段时间后，Google Chrome就会向更新URL发起请求，加载带有新版C2域名的新版扩展。

[![](https://p3.ssl.qhimg.com/t01d8d087a103668869.png)](https://p3.ssl.qhimg.com/t01d8d087a103668869.png)

[![](https://p3.ssl.qhimg.com/t0137d5034075f9e27b.png)](https://p3.ssl.qhimg.com/t0137d5034075f9e27b.png)

此外，如果攻击者失去了扩展的控制权，或者扩展出现崩溃，那么就可以通过更新版本来触发扩展执行。一旦扩展仍然安装在浏览器中，Chrome就会继续尝试并检查版本更新。如果只更新了manifest版本，Chrome就会重新安装并执行扩展。在下文中，我们将介绍如何使用一个PoC Chrome扩展，并使用Apfell来管理C2服务器。



## 四、恶意扩展

Apfell是一个后利用（post-exploitation）框架，采用定制化和模块化设计思路。该框架默认情况下针对的是macOS平台，但用户可以创建针对其他平台的C2 profile（策略）。对于恶意Chrome扩展来说，Apfell是一个理想的框架。接下来我们看一下如何配置自定义的C2 profile、生成攻击载荷。

1、在初始化配置方面，大家可以参考[此处](https://github.com/its-a-feature/Apfell)的apfell文档。启动apfell服务器后，我们可以注册一个新用户，将自己设置为管理员（admin）。接下来，我们需要将[apfell-chrome-ext-payload](https://github.com/xorrior/apfell-chrome-ext-payload)以及[apfell-chrome-extension-c2server](https://github.com/xorrior/apfell-chrome-extension-c2server)工程clone到apfell服务器上。

2、转到`manage operations -&gt; payload management`页面，该页面中定义了`apfell-jxa`以及`linfell`载荷。每个载荷都定义了几条命令，我们可以在控制台中修改这些命令，然后在agent中（这里指的是`apfell-jxa`以及`linfell`）更新这些命令。在载荷页面左下角有一个“import”按钮，我们可以使用json文件导入自定义载荷以及每条命令。为了节约大家时间，我提供了一个[文件](https://gist.github.com/xorrior/e1d5b1efb59d27f30ea808fab4400df1)，大家可以直接导入，创建载荷。如果成功导入，我们可以看到名为`chrome-extension`的一类新载荷，其中包含一些可操作命令。

[![](https://p4.ssl.qhimg.com/t01c48511096672975b.png)](https://p4.ssl.qhimg.com/t01c48511096672975b.png)

3、现在我们在apfell服务器上打开一个终端会话，转到`apfell-chrome-extension-c2server`项目。运行`install.sh`脚本安装golang并编译服务端程序，然后验证`server`程序已编译成功，并且位于`$HOME/go/src/apfell-chrome-extension-c2server`目录中。

4、转到`Manage Operations -&gt; C2 Profiles`，点击页面左下角的`Register C2 profile`按钮。这里我们需要输入profile的名称、描述以及支持的载荷。我们还需要上传与扩展程序对应的C2服务器程序（`$HOME/go/src/apfell-chrome-extension-c2server/server`）以及C2客户端代码（`./apfell-chrome-ext-payload/apfell/c2profiles/chrome-extension.js`）。

[![](https://p5.ssl.qhimg.com/t015e7bf4e564e728e6.png)](https://p5.ssl.qhimg.com/t015e7bf4e564e728e6.png)

5、一旦profile提交成功，页面就会自动更新，显示新加入的profile。

6、回到apfell服务器上的终端会话，编辑`c2config.json`文件，根据需要设置相关选项。

[![](https://p2.ssl.qhimg.com/t01f26c1abd05866818.png)](https://p2.ssl.qhimg.com/t01f26c1abd05866818.png)

7、将`c2config.json`拷贝到`apfell/app/c2profiles/default/chrome-extension/`目录中。将服务器程序重命名为`&lt;c2profilename&gt;_server`，我们需要执行该操作才能在apfell UI中启动C2服务器。现在我们可以在apfell中启动C2服务器。

[![](https://p0.ssl.qhimg.com/t01ee423a9ceeae8109.png)](https://p0.ssl.qhimg.com/t01ee423a9ceeae8109.png)

8、转到`Create Components -&gt; Create Base Payload`。在C2 profile和载荷类型中选择`chrome-extension`，填入所需的参数（主机名、端口、端点、SSL以及间隔时间），输入所需的文件名然后点击提交按钮。如果一切顺利，页面顶部就会显示一则成功消息。

[![](https://p1.ssl.qhimg.com/t0167dcadd0d46f6ab3.png)](https://p1.ssl.qhimg.com/t0167dcadd0d46f6ab3.png)

9、转到`Manage Operations -&gt; Payload Management`下载载荷。现在我们已成功构造扩展程序载荷以及C2 profile，我们可以导出这些载荷，以便后续使用。

10、将载荷的所有代码拷贝粘贴至chrome扩展项目文件中（`./apfell-chrome-ext-payload/apfell/extension-skeleton/src/bg/main.js`）。编辑`extension-skeleton`目录中的`manifest.json`文件，替换其中所有的`*_REPLACE`值。如果我们没有使用自动更新功能，可以不设置`update_url`值。

[![](https://p2.ssl.qhimg.com/t01706153160fc2f5a4.png)](https://p2.ssl.qhimg.com/t01706153160fc2f5a4.png)

11、打开Google Chrome，点击`More -&gt; More Tools -&gt; Extensions`，然后切换到开发者模式。点击`pack extension`，然后选择`apfell-chrome-ext-payload`项目中的`extension-skeleton`目录。再次点击`pack extension`，然后Chrome就会生成带有私钥的`.crx`文件。需要注意的是，我们需要保存好私钥，才能更新扩展。

12、我们需要知道的最后一个信息就是应用ID。不幸的是，获取该信息的唯一方法就是安装扩展，然后记录下扩展页面上显示的ID值。我们可以将扩展文件（`.crx`）拖放到扩展页面进行安装。

[![](https://p1.ssl.qhimg.com/t01a0c90287780d4d0e.png)](https://p1.ssl.qhimg.com/t01a0c90287780d4d0e.png)

13、现在我们已经获取创建移动配置文件所需的信息，可以托管manifest更新文件以及crx文件。我们需要在manifest更新文件中加入应用ID以及指向crx文件的url，然后在[移动配置示例文件](https://gist.github.com/xorrior/8ee611d4f91b91f03ec16bed1324be56)中添加应用id及`update_url`。此外，我们还需要填入两个不同的UUID值。

[![](https://p3.ssl.qhimg.com/t013bbcc37690bd9670.png)](https://p3.ssl.qhimg.com/t013bbcc37690bd9670.png)

[![](https://p5.ssl.qhimg.com/t01d4b91b5c7d2ec1e9.png)](https://p5.ssl.qhimg.com/t01d4b91b5c7d2ec1e9.png)

14、现在我们已配置完毕。如果一切配置正常，那么安装移动配置描述文件后就可以静默安装扩展程序，也能在apfell的回调页面中添加一个新的回调（callback）。大家可以参考前面的“载荷投递”内容了解如何安装profile。

[![](https://p1.ssl.qhimg.com/t019191cec19feec652.png)](https://p1.ssl.qhimg.com/t019191cec19feec652.png)

大家可以参考[此处](https://vimeo.com/316165337)视频观看如何通过移动配置描述文件安装恶意chrome扩展程序。



## 五、检测方法

在前文中，我们简单介绍了投递chrome扩展的一种机制，可以通过移动配置描述文件实现扩展的静默及隐蔽安装。从防御角度来看，检测这类投递机制应该重点关注`profiles`命令及相关参数。这种检测机制对已经获得受害主机访问权限的攻击者而言非常有效。作为参考，这里给出安装profile的示例命令：`profiles install -type=configuration -path=/path/to/profile.mobileconfig`。

相应的`osquery`规则类似于：`SELECT * FROM process_events WHERE cmdline=’%profiles install%’;`。对于企业环境来说这可能不是最佳答案，但的确行之有效。另外还要注意一点，`osquery`现在已经包含了一个chrome扩展[表](https://osquery.io/schema/3.3.2#chrome_extensions)。此外，当用户通过UI安装profile时，`MCXCompositor`进程会将一个二进制plist写入`/Library/Managed Preferences/username/`目录中。这个plist文件是移动配置描述文件的一个副本，文件名由配置描述文件中的`PayloadType`键值决定。

[![](https://p2.ssl.qhimg.com/t014fea7a696d174029.png)](https://p2.ssl.qhimg.com/t014fea7a696d174029.png)

可能还有其他数据来源，能够更加可靠地检测使用移动配置描述文件的攻击技术，这里我们抛砖引玉，希望大家继续研究。

在获得初始访问权限及持久化方面，我们可以考虑使用Google Chrome扩展程序。红队人员及安全研究人员可以进一步研究Chrome API，了解更多可用功能。
