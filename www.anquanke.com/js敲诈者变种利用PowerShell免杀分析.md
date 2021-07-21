> 原文链接: https://www.anquanke.com//post/id/84421 


# js敲诈者变种利用PowerShell免杀分析


                                阅读量   
                                **89369**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t01d51359dd688d8634.png)](https://p5.ssl.qhimg.com/t01d51359dd688d8634.png)

近期360安全中心监测到出现了一种js敲诈者病毒变种，此种敲诈者利用PowerShell进行免杀，通过vt对比各大安全厂商的扫描结果，发现目前杀毒厂商对此种js敲诈者病毒的检出率特别低，本文就由360QEX引擎团队结合js，vbs和宏三种类型的脚本对PowerShell的利用方式进行详细的分析。

<br>

**0x01 js敲诈者利用PowerShell**

<br>

首次发现的此类样本是通过html格式的方式进行传播的，它的代码经过混淆加密后放在一个html文件之中，vt目前只有7家杀毒厂商报毒。

样本文件md5: 8db221c5ec335f0df1c4a47d1b219f6a

sha256: 0e1cfde86bfe427784fe9c280c09d0713ed0a47d1be552dc83fead378f671fb2

[![](https://p4.ssl.qhimg.com/t012bcf10b580158b1d.png)](https://p4.ssl.qhimg.com/t012bcf10b580158b1d.png)

图 1：样本1

[![](https://p2.ssl.qhimg.com/t01afb719e58b395cd0.png)](https://p2.ssl.qhimg.com/t01afb719e58b395cd0.png)

图 2：样本1的vt扫描结果

对此样本进行解密，然后对解密的样本再次进行扫描，发现此时只有360产品可以查杀。

样本文件md5: 50de6e9ca24342a2e24d22fb49d9b69b

sha256: [e7e7167137f5954d51bef26ee111537ee9b9aa0fff5e077b9cde92303ed4de85](https://www.virustotal.com/intelligence/search/?query=50de6e9ca24342a2e24d22fb49d9b69b#sha256)

[![](https://p2.ssl.qhimg.com/t01f6f93cc634c5e22c.png)](https://p2.ssl.qhimg.com/t01f6f93cc634c5e22c.png)

图 3：解密后样本的vt扫描结果

对解密后的样本进行格式整理，可以看到如图4所示的结果。

[![](https://p0.ssl.qhimg.com/t01d012ae829fbcdcfc.png)](https://p0.ssl.qhimg.com/t01d012ae829fbcdcfc.png)

图 4：对解密后的样本进行整理<br>

         以往常见的js敲诈者病毒，会利用windows用户的wscript.exe程序，通过此程序为js脚本提供一个可执行的宿主环境，然后进行远程文件的下载和执行。而此次所出现的敲诈者病毒发生了重大变化，它是利用windows用户的PowerShell程序，通过PowerShell完成pe文件的保存,下载和运行。

         此样本并没有经过多少刻意的混淆，但是由于之前未出现这种利用方式，所以才导致vt中查杀率很低的结果。

         为了防止用户的察觉，此病毒在PowerShell运行时对“WindowStyle”参数使用值Hidden，并且被下载的pe文件运行结束就进行删除了。

样本1类型的样本后来出现了一些新的变种，它的利用方式和代码的混淆方式均发生了一些变化。

样本文件md5: [e6e13879e55372d7b199fdf2c58b1d0b](https://www.virustotal.com/intelligence/search/?query=e6e13879e55372d7b199fdf2c58b1d0b#md5) 

sha256: [c0e3d8247ba43b904a2c21d06274616b046f23325bffb9b954eccc1529e8682e](https://www.virustotal.com/intelligence/search/?query=e6e13879e55372d7b199fdf2c58b1d0b#sha256)

[![](https://p0.ssl.qhimg.com/t0168e5edd796d19980.png)](https://p0.ssl.qhimg.com/t0168e5edd796d19980.png)

图 5：样本2的vt扫描结果

[![](https://p1.ssl.qhimg.com/t01ceea3bea4314267e.png)](https://p1.ssl.qhimg.com/t01ceea3bea4314267e.png)

图 6：样本2

此混淆样本和样本1的运行方式发生了一些变化：样本1利用Wscript.Shell对象，通过调用Run成员函数运行用户本地的PowerShell程序；而这个样本则利用shell.application对象，通过它的ShellExecute成员函数运行cmd.exe，然后再利用cmd调用PowerShell。

代码混淆方式和以往常见的混淆也发生了变化，以前的js敲诈者会通过字符拼接，数组利用，eval函数等方式进行混淆，而此样本主要通过字符的大小写变换，字符串中间添加多余的“^”符号进行混淆。

由于此样本的url还未失效，下载url中的pe文件并进行vt扫描，可得到如图7所示的扫描结果。

样本文件md5: 51bfd9f388a38378b392c4aa738f67bc

sha256: 7b989c6cf941d08eae591e486146b40c5e297b567e4883617eec770bdb42b53b

[![](https://p3.ssl.qhimg.com/t0197242620f1819e57.png)](https://p3.ssl.qhimg.com/t0197242620f1819e57.png)

图 7：pe文件vt扫描结果

****

**<br>**

**0x02 vbs敲诈者利用PowerShell**

****

样本文件md5: 7bf9f9f7a67ebadd0a687bf8f46091a7

sha256: 21e7b650d7848c4082c172338b362a4197d09775c6706286abe4baff0c6febdb

[![](https://p3.ssl.qhimg.com/t01386efd3c908e6072.png)](https://p3.ssl.qhimg.com/t01386efd3c908e6072.png)

图 8：vbs敲诈者vt扫描结果

此样本的利用方式和js敲诈者有以下地方不同：它是将PE文件内容以base64编码的方式保存到远程服务器，然后通过msxml2.xmlhttp对象将base64数据下载到注册表中，读取注册表中所下载的数据，使用base64解码数据并保持到本地，最后通过Powershell执行本地所保存的PE文件。此样本的主要代码如图9所示。

[![](https://p3.ssl.qhimg.com/t012fb1e4415068fe6b.png)](https://p3.ssl.qhimg.com/t012fb1e4415068fe6b.png)

图 9：vbs敲诈者的主要代码

****

**0x03 宏病毒敲诈者利用PowerShell**

****

样本文件md5: b7fefcf8d0dc5136c095499d8706d88f

sha256: f81128f3b9c0347f4ee5946ecf9a95a3d556e8e3a4742d01e5605f862e1d116d

[![](https://p5.ssl.qhimg.com/t0136e083ffa6b94913.png)](https://p5.ssl.qhimg.com/t0136e083ffa6b94913.png)

图 10：宏病毒的vt扫描结果

[![](https://p1.ssl.qhimg.com/t01d43dbcff77785ae4.png)](https://p1.ssl.qhimg.com/t01d43dbcff77785ae4.png)

图 11：宏病毒的主要代码

         分析此宏病毒样本可以看到，它利用PowerShell的方式和样本2极其相似，同样是调用用户的cmd.exe，然后在cmd中调用PowerShell。它选择运行PowerShell的方式不是隐藏执行而是最小化执行。

****

**<br>**

**0x04 总结**

****

加密勒索软件可以利用的传播方式越来越多，病毒的进化速度也越来越快，所利用的宿主软件也日益增多，因此用户一定要提高安全防范意识，及时安装杀毒软件。

非PE病毒查杀引擎QEX是 360安全产品中负责查杀宏病毒及vbs、js和bat等非PE样本的独有引擎，上述样本QEX引擎均已可以查杀。

0x05 Reference

WSF文件格式成为敲诈者传播新途径       [http://bobao.360.cn/learning/detail/2934.html](http://bobao.360.cn/learning/detail/2934.html)

近期js敲诈者的反查杀技巧分析           [http://bobao.360.cn/learning/detail/2827.html](http://bobao.360.cn/learning/detail/2827.html)

技术揭秘:宏病毒代码三大隐身术           [http://bobao.360.cn/learning/detail/2880.html](http://bobao.360.cn/learning/detail/2880.html)

NeutrinoEK来袭：爱拍网遭敲诈者病毒挂马  [http://bobao.360.cn/news/detail/3302.html](http://bobao.360.cn/news/detail/3302.html)
