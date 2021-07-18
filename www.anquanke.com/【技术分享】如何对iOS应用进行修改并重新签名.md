
# 【技术分享】如何对iOS应用进行修改并重新签名


                                阅读量   
                                **217178**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](./img/85525/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：vantagepoint.sg
                                <br>原文地址：[http://www.vantagepoint.sg/blog/85-patching-and-re-signing-ios-apps](http://www.vantagepoint.sg/blog/85-patching-and-re-signing-ios-apps)

译文仅供参考，具体内容表达以及含义原文为准

****

[![](./img/85525/t01f3d1f2f44cd8cb59.jpg)](./img/85525/t01f3d1f2f44cd8cb59.jpg)

作者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



**前言**

在某些场景下，你可能需要在没越狱的iOS设备上运行修改过的iOS应用，特别是当手上已越狱的iPhone突然变砖，只能被迫升级到非越狱版本的iOS系统时，这种需求显得更加迫切。再如，你需要使用这项技术来动态分析测试应用程序，或者你可能需要使用GPS欺骗手段来绕过Pokemon的锁区限制，在非洲地区捕捉宠物小精灵，而又不想承担越狱带来的安全风险。无论是哪种情况，你都可以使用本文介绍的方法对某个经过修改的应用重新签名并在自己的设备上成功运行。需要注意的是，这种技术仅在应用程序不是经过FairPlay加密（即从应用商店上下载）时才能正常工作。

由于Apple采用了较为复杂的配置及代码签名系统，在iOS系统上对程序进行重新签名会比想象中困难得多。只有使用正确的配置文件以及完全正确的代码签名头，iOS系统才会允许应用程序正常运行。这使得你需要熟知许多概念：如不同类型的证书、BundleID、应用ID、团队ID，以及如何使用Apple的编译工具将这些东西结合在一起。简而言之，要想让不经过默认方法（即XCode环境）编译生成的程序在iOS上正确运行将会是一个困难重重的过程。

我们在本文中使用的工具集包括[optool](https://github.com/alexzielenski/optool)、Apple的编译环境以及一些shell命令。我们所使用的方法灵感来自于Vincent Tan的[Swizzler项目](https://github.com/vtky/Swizzler2/wiki)。此外，[NCC工作组](https://www.nccgroup.trust/au/about-us/newsroom-and-events/blogs/2016/october/ios-instrumentation-without-jailbreak/)采用其他工具集也完成了同样的工作。

要复现下文列出的步骤，请从OWASP Mobile Testing Guide软件仓库中下载[UnCrackable Ios App Level 1](https://github.com/OWASP/owasp-mstg/tree/master/OMTG-Files/02_Crackmes/02_iOS/UnCrackable_Level1)这个示例应用，我们的目标是修改UnCrackable这个应用，使它在启动时加载FridaGadget.dylib，以便后续可以用[Frida](https://github.com/frida/)来加载该应用进行测试。

<br>

**获取开发者配置文件（Provisioning Profile）及证书**



开发者配置文件是由Apple签名的一个plist文件，它将开发者的代码签名证书列入一个或多个设备的白名单中。话句话说，Apple通过这种方式显式允许开发者的应用程序在某些设备的上下文环境中运行（如对特定设备进行调试）。配置文件还列出了应用程序所能获得的权限信息。代码签名证书包含了开发者在对应用进行签名时所用到的私钥。

**1）使用iOS开发者账号时**

如果你之前使用Xcode开发和部署过iOS应用，你已经获得了一个代码签名证书。你可以使用security工具列出你现有的签名身份码：

```
$ security find-identity -p codesigning -v
1) 61FA3547E0AF42A11E233F6A2B255E6B6AF262CE "iPhone Distribution: Vantage Point Security Pte. Ltd."
2) 8004380F331DCA22CC1B47FB1A805890AE41C938 "iPhone Developer: Bernhard Müller (RV852WND79)"
```

已经注册的开发者可以从Apple开发者门户上获取配置文件。首先你需要创建一个新的App ID，之后发起一个配置文件请求，以便该App ID能在你的设备上运行。要是只是想对应用进行重新打包，那么选择哪个App ID并不重要，你甚至可以重复使用之前使用过的App ID。关键点在于你需要一个正确匹配的配置文件，因为需要将调试器附加到应用上进行工作，请确保你创建的是一个开发配置文件（development provisioning profile）而不是分发配置文件（distribution profile）。

在下文的shell命令中，我使用了自己的签名身份，该签名身份与我公司的开发团队相关联。我创建了名为“sg.vp.repackaged”的app-id，以及一个名为“AwesomeRepackaging”的配置文件，生成了一个名为“AwesomeRepackaging.mobileprovision”的文件，请你在实际操作时将这些字段替换为你自己的文件名。

**2）使用普通iTunes账号时**

幸运的是，即便你不是付费开发者，Apple也会给你发放一个免费的开发配置文件。你可以使用自己的Apple账户，通过Xcode环境获得该配置文件——只需要创建一个空的iOS工程，并从应用容器中提取embedded.mobileprovision即可。[NCC博客](https://www.nccgroup.trust/au/about-us/newsroom-and-events/blogs/2016/october/ios-instrumentation-without-jailbreak/)对整个过程进行了详细描述。

获取到配置文件后，你可以使用security工具检查其内容。除了证书及设备信息外，你还可以从配置文件中找到应用所被赋予的运行权限。这些信息在后续的代码签名工作中都需要用到，因此你需要将它们提取到单独的plist文件中，如下所示。

```
$ security cms -D -i AwesomeRepackaging.mobileprovision &gt; profile.plist
$ /usr/libexec/PlistBuddy -x -c 'Print :Entitlements' profile.plist &gt; entitlements.plist
$ cat entitlements.plist
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"&gt;
&lt;plist version="1.0"&gt;
&lt;dict&gt;
&lt;key&gt;application-identifier&lt;/key&gt;
&lt;string&gt;LRUD9L355Y.sg.vantagepoint.repackage&lt;/string&gt;
&lt;key&gt;com.apple.developer.team-identifier&lt;/key&gt;
&lt;string&gt;LRUD9L355Y&lt;/string&gt;
&lt;key&gt;get-task-allow&lt;/key&gt;
&lt;true/&gt;
&lt;key&gt;keychain-access-groups&lt;/key&gt;
&lt;array&gt;
&lt;string&gt;LRUD9L355Y.*&lt;/string&gt;
&lt;/array&gt;
&lt;/dict&gt;
&lt;/plist&gt;
```

你还需要检查一下生成的plist文件，看文件内容是否正确生成。

其中，应用标识（App ID）是由Team ID（LRUD9L355Y）以及Bundle ID（sg.vantagepoint.repackage）组合而成。此配置文件仅对使用该App ID的应用有效。 “get-task-allow” 键值也十分重要，当该键值设为“true”时，其他进程（如调试服务器）可以被允许附加到该应用程序上，因此，在分发配置文件中，需要将该键值设置为“false”。

<br>

**其他的准备措施**

要想让我们的应用在启动时加载一个附加库，我们使用某些方法将一个附加加载命令插入到主执行文件的Mach-O头中。我们使用optool来自动化完成这个步骤：

```
$ git clone https://github.com/alexzielenski/optool.git
$ cd optool/
$ git submodule update --init --recursive
```

不使用Xcode的情况下，我们可以使用[ios-deploy工具](https://github.com/phonegap/ios-deploy)来完成应用的部署及调试。

```
git clone https://github.com/phonegap/ios-deploy.git
cd ios-deploy/
git submodule update --init --recursive
```

你需要FridaGadget.dylib完成本文示例。

```
$ curl -O https://build.frida.re/frida/ios/lib/FridaGadget.dylib
```

除了上述工具，我们还将使用OS X及XCode附带的标准工具集，请确保你的环境中已安装Xcode命令行开发者工具。

<br>

**应用的修改、重新打包和重新签名**



IPA文件其实就是ZIP文件，因此我们可以解压ipa包，将FridaGadget.dylib拷贝至app目录，之后使用optool将load命令添加到“UnCrackable Level 1”这个应用中。

```
$ unzip UnCrackable_Level1.ipa
$ cp FridaGadget.dylib Payload/UnCrackable Level 1.app/
$ optool install -c load -p "@executable_path/FridaGadget.dylib" -t Payload/UnCrackable Level 1.app/UnCrackable Level 1
Found FAT Header
Found thin header...
Found thin header...
Inserting a LC_LOAD_DYLIB command for architecture: arm
Successfully inserted a LC_LOAD_DYLIB command for arm
Inserting a LC_LOAD_DYLIB command for architecture: arm64
Successfully inserted a LC_LOAD_DYLIB command for arm64
Writing executable to Payload/UnCrackable Level 1.app/UnCrackable Level 1...
```

上述操作肯定会使主执行文件的代码签名无效，因此应用不能在非越狱设备上运行。你需要替换其中的配置文件，使用配置文件中列出的证书对主执行文件及FridaGadget.dylib进行签名。

首先，我们向包中添加自己的配置文件：

```
$ cp AwesomeRepackaging.mobileprovision Payload/UnCrackable Level 1.app/embedded.mobileprovision
```

接下来，我们要确保Info.plist中的BundleID与配置文件中的BundleID一致。Codesign在签名过程中会从Info.plist中读取BundleID信息，两者如果不一致将会导致应用签名无效。

```
$ /usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier sg.vantagepoint.repackage" Payload/UnCrackable Level 1.app/Info.plist
```

最后，我们使用codesign工具来对修改过的应用重新签名/

```
$ rm -rf Payload/F/_CodeSignature
$ /usr/bin/codesign --force --sign 8004380F331DCA22CC1B47FB1A805890AE41C938 Payload/UnCrackable Level 1.app/FridaGadget.dylib
Payload/UnCrackable Level 1.app/FridaGadget.dylib: replacing existing signature
$ /usr/bin/codesign --force --sign 8004380F331DCA22CC1B47FB1A805890AE41C938 --entitlements entitlements.plist Payload/UnCrackable Level 1.app/UnCrackable Level 1
Payload/UnCrackable Level 1.app/UnCrackable Level 1: replacing existing signature
```

**<br>**

**安装及运行修改后的应用**

一切准备就绪，你可以使用以下命令在设备上部署和运行经过修改后的应用。

```
$ ios-deploy --debug --bundle Payload/UnCrackable Level 1.app/
```

如果一切顺利，应用应该可以在附加IIdb的调试模式下在设备上启动运行。Frida应该也可以正确加载到应用中运行，你可以使用frida-ps命令验证这一点：

```
$ frida-ps -U
PID Name
--- ------
499 Gadget
```

现在你可以使用Frida正常测试应用程序了。

<br>

**故障排除**



如果你在进行上述操作时发生错误，你可以检查一下配置文件和代码签名头是否正确匹配，通常的错误都是因为两者不匹配导致的。这种情况下你可以参考Apple的[官方文档](https://developer.apple.com/library/content/documentation/IDEs/Conceptual/AppDistributionGuide/MaintainingProfiles/MaintainingProfiles.html)，了解整个系统的工作原理。另外，Apple的[故障排除页面](http://https//developer.apple.com/library/content/technotes/tn2415/_index.html)也是一个不错的参考资料。
