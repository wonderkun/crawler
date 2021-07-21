> 原文链接: https://www.anquanke.com//post/id/218405 


# 微软轻量级系统监控工具sysmon原理与实现完全分析（续篇）


                                阅读量   
                                **236942**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01f85cacd3d6547ad0.jpg)](https://p3.ssl.qhimg.com/t01f85cacd3d6547ad0.jpg)



前两次我们分别讲了sysmon的ring3与ring0的实现原理，但是当初使用的版本的是8.X的版本，最新的版本10.X的sysmon功能有所增加，经过分析代码上也有变化。比如增加DNS得功能，这个功能实现也很简单，就是ETW里获取Microsoft-Windows-DNS-Client得数据，但是本篇不讲这个，本续篇主要讲内核里的事件结构。

所有的内核里上报的事件开头基本都是

```
ReportSize
ReportType
struct _Report_Common_Header
`{`
ULONG ReportType;
ULONG ReportSize;
`}`;
```

下面具体讲解每个事件的结构
<li>FileCreate<br>
下图是文件上报事件，除了上报上诉三个字段外，还有<strong>ProcessPid<br>
、EventCreateTime， FileCreateTime、<br>
hashVlaue算法id，hashvalue</strong>、三组进程相关的数据用户UserSid、进程**ImageFileName、文件名FileName**<br>
可以看到内核里上报出来的事件类型是根据是否计算hash来判断，分别是10 、11[![](https://p1.ssl.qhimg.com/t0193291990873b720c.png)](https://p1.ssl.qhimg.com/t0193291990873b720c.png)
</li>
<code>struct _Report_File<br>
`{`<br>
Common_Header Header;<br>
CHAR data[16];<br>
ULONG ProcessPid;<br>
ULONG ParentPid;<br>
LARGE_INTEGER CreateTime;<br>
LARGE_INTEGER FileCreateTime;<br>
ULONG HashingalgorithmRulev;<br>
CHAR FileHash[84];<br>
ULONG DataLength[4];<br>
CHAR Data2[1];<br>
`}`;</code>
<li>设置文件属性时间改变事件<br>
内核出来的事件Type 值是2[![](https://p0.ssl.qhimg.com/t0168ef35fab29efd6b.png)](https://p0.ssl.qhimg.com/t0168ef35fab29efd6b.png)
</li>
结构体与FileCreate稍微有些不同，少了文件hash的计算的步骤，但是多了一个设置文件改变的时间。

<code>struct _Report_File_SetAttrubute<br>
`{`<br>
Common_Header Header;<br>
CHAR data[16];<br>
ULONG ProcessPid;<br>
ULONG ParentPid;<br>
LARGE_INTEGER CreateTime;<br>
LARGE_INTEGER FileTime;<br>
LARGE_INTEGER FileCreateTime;<br>
ULONG DataLength[4];<br>
CHAR Data2[1];<br>
`}`;</code>
<li>进程创建事件<br>
进程创建上报事件内核的事件Type值是4或者1[![](https://p2.ssl.qhimg.com/t016ae036ca872e97ac.png)](https://p2.ssl.qhimg.com/t016ae036ca872e97ac.png)
</li>
他的结构体如下（具体不在讲解，名字字面意思都能看懂）

```
struct _Report_Process
`{`
Report_Common_Header Header;
CHAR data[16];
ULONG ProcessPid;
ULONG ParentPid;
ULONG SessionId;
ULONG UserSid;
LARGE_INTEGER CreateTime;
LUID AuthenticationId;
ULONG TokenIsAppContainer;
LUID TokenId;
ULONG HashingalgorithmRule;
DWORD DataChunkLength[6];
CHAR Data[1];
`}`;
```
<li>进程退出事件<br>
进程退出事件内核的Type值是3[![](https://p2.ssl.qhimg.com/t0191fa4e5079907a2f.png)](https://p2.ssl.qhimg.com/t0191fa4e5079907a2f.png)
</li>
<code>struct _Report_Process_Create<br>
`{`<br>
Report_Common_Header Header;<br>
CHAR data[16];<br>
ULONG ProcessPid;<br>
ULONG ParentPid;<br>
LARGE_INTEGER CreateTime;<br>
ULONG SidLength;<br>
ULONG XXXXXXX;<br>
SID UserSid;<br>
CHAR Data[1];<br>
`}`;</code><br>
可以看到数据有进程id、 父进程id、事件创建时间、UserSid
1. 线程创建事件
内核里的事件类型是7

[![](https://p2.ssl.qhimg.com/t010b27a2ae2af977c3.png)](https://p2.ssl.qhimg.com/t010b27a2ae2af977c3.png)

[![](https://p0.ssl.qhimg.com/t0143d881c293fe5aeb.png)](https://p0.ssl.qhimg.com/t0143d881c293fe5aeb.png)

结构体如下<br><code>struct _ Report_Process_Thread<br>
`{`<br>
Report_Common_Header Header;<br>
CHAR data[16];<br>
LARGE_INTEGER CreateTime;<br>
ULONG ThreadOwnerPidv;<br>
ULONG ThreadId;<br>
ULONG ThreadAddress;<br>
ULONG OpenProcessPid;<br>
WCHAR DllInfo[261];<br>
WCHAR DllExportInfo[261];<br>
`}`;</code>

DllInfo是指线程所在的模块名，DllExportInfo是该模块的导出表信息
<li>OpenProcess事件<br>
内核事件类型是： 9[![](https://p0.ssl.qhimg.com/t0118574f1ddf78d724.png)](https://p0.ssl.qhimg.com/t0118574f1ddf78d724.png)[![](https://p1.ssl.qhimg.com/t01eed730934ae1906f.png)](https://p1.ssl.qhimg.com/t01eed730934ae1906f.png)
</li>
结构体定义如下：<br><code>struct _ Report_OpenProcess<br>
`{`<br>
Report_Common_Header Header;<br>
CHAR data[16];<br>
ULONG ProcessId;<br>
ULONG MyThreadId;<br>
ULONG OpenPrcesid;<br>
ULONG AccessMask;<br>
LARGE_INTEGER CreateTime;<br>
ULONG StatckTrackInfoSize;<br>
ULONG DataLength[3];<br>
CHAR Data[1];<br>
`}`;</code>
<li>注册表事件<br>
进程注册表操作事件的Type值是12[![](https://p3.ssl.qhimg.com/t018955ffa4d0c7981e.png)](https://p3.ssl.qhimg.com/t018955ffa4d0c7981e.png)
</li>
```
结构体如下：
```

<code>struct _Report_Process_Registry<br>
`{`<br>
Report_Common_Header Header;<br>
CHAR data[16];<br>
ULONG OperateEventType;<br>
ULONG ParentPid;<br>
LARGE_INTEGER CreateTime;<br>
ULONG ProcessPid;<br>
ULOG DataLenth[5];<br>
CHAR Data[1];<br>
`}`;</code>

这里要说明的是附加数据段有5个数据<br><strong>UserSid<br>
RegistryOperateName</strong><br><strong>进程名带参数<br>
KeyName<br>
ValueName</strong>

其中RegistryOperateName的值是根据OperateEventType的值从下面的数组中选取<br><code>g_RegistryTypeName dd offset aUnknownEventTy<br>
.rdata:100134D8                                         ; DATA XREF: SysmonCreateRegistryReportInfo+15E↑r<br>
.rdata:100134D8                                         ; "Unknown Event type"<br>
.rdata:100134DC                 dd offset aCreatekey    ; "CreateKey"<br>
.rdata:100134E0                 dd offset aDeletekey    ; "DeleteKey"<br>
.rdata:100134E4                 dd offset aRenamekey    ; "RenameKey"<br>
.rdata:100134E8                 dd offset aCreatevalue  ; "CreateValue"<br>
.rdata:100134EC                 dd offset aDeletevalue  ; "DeleteValue"<br>
.rdata:100134F0                 dd offset aRenamevalue  ; "RenameValue"<br>
.rdata:100134F4                 dd offset aSetvalue     ; "SetValue"<br>
.rdata:100134F8 dword_100134F8  dd 100010h              ; DATA XREF: Regist</code>

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f34405ba78d670d8.png)
<li>命名管道事件<br>
内核的事件的Type的值是：13[![](https://p2.ssl.qhimg.com/t0134b3ce8b08149c1a.png)](https://p2.ssl.qhimg.com/t0134b3ce8b08149c1a.png)
</li>
结构体如下：<br><code>struct _Report_Process_NameedPipe<br>
`{`<br>
Report_Common_Header Header;<br>
CHAR data[16];<br>
ULONG NamedPipeType;<br>
ULONG ParentPid;<br>
LARGE_INTEGER CreateTime;<br>
ULONG ProcessPid;<br>
DWORD DataChunkLength[3];<br>
CHAR Data[1];<br>
`}`;</code>

在data块里会输出： NamePipeFileName 和ImageFileName 两个数据
<li>上报错误信息事件<br>
内核的事件Type值是：6[![](https://p1.ssl.qhimg.com/t018a37c47d8ddb2f46.png)](https://p1.ssl.qhimg.com/t018a37c47d8ddb2f46.png)<br>
结构体定义：<br><code>struct _ _Report_Event_Error<br>
`{`<br>
Report_Common_Header Header;<br>
CHAR data[16];<br>
ULONG ErrorDataLength[2];<br>
CHAR Data[1];<br>
`}`;</code><br>
Data信息里会输出两个错误信息的字符串，如：<br>[![](https://p0.ssl.qhimg.com/t01be1caef1468ab374.png)](https://p0.ssl.qhimg.com/t01be1caef1468ab374.png)
</li>
下面我做一个小实验，以进程信息为例子，向sysomn的驱动发送IO控制码0xXXX0000X（我打码屏蔽了，希望读者自己去发现，不要做伸手党）

```
LARGE_INTEGER Request;
Request.LowPart		= GetCurrentProcessId();
Request.HighPart	= FALSE;
BYTE	OutBuffer[4002] = `{` 0 `}`;
ULONG	BytesReturned = 0;
if ( SUCCEEDED( DeviceIoControl(
			hObjectDrv,
			SYSMON_REQUEST_PROCESS_INFO,
			&amp;Request,
			8,
			OutBuffer,
			sizeof(OutBuffer),
			&amp;BytesReturned, 0 ) ) )
`{`
	if ( BytesReturned )
	`{`
		Report_Process* pSysmon_Report_Process = (_Report_Process *)
							 &amp;OutBuffer[0];

		if ( pSysmon_Report_Process-&gt;Header.ReportSize )
		`{`
			CheckServiceOk = TRUE;
		`}`
	`}`
`}`

CloseHandle( hObjectDrv );
```

看结果：

[![](https://p4.ssl.qhimg.com/t01c07e789db4f27b46.png)](https://p4.ssl.qhimg.com/t01c07e789db4f27b46.png)

可以看到结构体上的值都是对的，然后6个DataChunkLenggth都有值，我们在去看下面的Data内存

[![](https://p4.ssl.qhimg.com/t01aef74c7ccce188c6.png)](https://p4.ssl.qhimg.com/t01aef74c7ccce188c6.png)

今天的续篇就此结束，sysmon还是可以挖掘很多很实用得东西，比如每个事件里得ProcessGuid 并不是随机生成得，而是有一定算法得，具体读者可以自行研究发现。
