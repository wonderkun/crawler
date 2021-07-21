> 原文链接: https://www.anquanke.com//post/id/238360 


# 微软轻量级工具Sysmon新功能剪切板Change事件


                                阅读量   
                                **109476**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t0137f9ad6730b4c509.jpg)](https://p1.ssl.qhimg.com/t0137f9ad6730b4c509.jpg)



Sysmon的最新版本增加一个事件id： 24 剪切板事件，sysmon的官网描述如下<br>[https://docs.microsoft.com/en-us/sysinternals/downloads/sysmon](https://docs.microsoft.com/en-us/sysinternals/downloads/sysmon)

[![](https://p0.ssl.qhimg.com/t014f52488e256a3372.png)](https://p0.ssl.qhimg.com/t014f52488e256a3372.png)

如果要开启这个功能可以进行简单的配置文件，内容如下:

[![](https://p4.ssl.qhimg.com/t01a22d6ab06cea31d0.png)](https://p4.ssl.qhimg.com/t01a22d6ab06cea31d0.png)

`&lt;EventFiltering&gt;`<br>`&lt;!-- Log all drivers except if the signature --&gt;`<br>`&lt;!-- contains Microsoft or Windows --&gt;`<br>`&lt;!-- Do not log process termination --&gt;`<br>`&lt;ClipboardChange onmatch="exclude" /&gt;`<br>`&lt;/EventFiltering&gt;`

输入命令行：

**Sysmon64.exe -c “new 1.xml” ** 打开更新规则

[![](https://p2.ssl.qhimg.com/t0105aa2548876b4e20.png)](https://p2.ssl.qhimg.com/t0105aa2548876b4e20.png)

然后我们打开windows事件日志记录就可以看到剪切板的记录事件了,事件id值是24

[![](https://p2.ssl.qhimg.com/t016e4009897e02924e.png)](https://p2.ssl.qhimg.com/t016e4009897e02924e.png)

查看详细信息

[![](https://p3.ssl.qhimg.com/t0108768fefc0834d9a.png)](https://p3.ssl.qhimg.com/t0108768fefc0834d9a.png)

SYSMONSCHEMA.XML描述该事件的进程参数

[![](https://p3.ssl.qhimg.com/t01250a02b0597a68fe.png)](https://p3.ssl.qhimg.com/t01250a02b0597a68fe.png)

多两条参数配置信息

`&lt;option switch="z" name="ClipboardInstance" argument="required" noconfig="true" exclusive="true" /&gt;`<br>`&lt;option name="CaptureClipboard" argument="none" /&gt;`

SYSMONSCHEMA.XML描述该事件规则上报结构<br>`&lt;event name="SYSMONEVENT_CLIPBOARD" value="24" level="Informational" template="Clipboard changed" rulename="ClipboardChange" version="5"&gt;`<br>`&lt;data name="RuleName" inType="win:UnicodeString" outType="xs:string" /&gt;`<br>`&lt;data name="UtcTime" inType="win:UnicodeString" outType="xs:string" /&gt;`<br>`&lt;data name="ProcessGuid" inType="win:GUID" /&gt;`<br>`&lt;data name="ProcessId" inType="win:UInt32" outType="win:PID" /&gt;`<br>`&lt;data name="Image" inType="win:UnicodeString" outType="xs:string" /&gt;`<br>`&lt;data name="Session" inType="win:UInt32" /&gt;`<br>`&lt;data name="ClientInfo" inType="win:UnicodeString" outType="xs:string" /&gt;`<br>`&lt;data name="Hashes" inType="win:UnicodeString" outType="xs:string" /&gt;`<br>`&lt;data name="Archived" inType="win:UnicodeString" outType="xs:string" /&gt;`<br>`&lt;/event&gt;`

上报事件id: 24, 事件字段：UtcTime、ProcessGuid、ProcessId、Image、Session、Hashes、ClientInfo

了解了该事件的大概的情况的后，我们就要开始分析sysmon监测该事件的原理方法。

## 1. 开关打开剪切板开关后就会运行Start函数

[![](https://p5.ssl.qhimg.com/t01edd2eae1fb4f5cf3.png)](https://p5.ssl.qhimg.com/t01edd2eae1fb4f5cf3.png)



## 2. StartClipboardListening

### **<a class="reference-link" name="%EF%BC%881%EF%BC%89%E5%85%88%E8%8E%B7%E5%8F%96%E4%B8%A4%E4%B8%AA%E4%B8%8E%E5%89%AA%E5%88%87%E6%9D%BF%E7%9B%91%E6%8E%A7%E7%9B%B8%E5%85%B3%E7%9A%84%E5%87%BD%E6%95%B0AddClipboardFormatListener%E3%80%81RemoveClipboardFormatListener%E7%9A%84%E5%87%BD%E6%95%B0%E5%9C%B0%E5%9D%80"></a>（1）先获取两个与剪切板监控相关的函数AddClipboardFormatListener、RemoveClipboardFormatListener的函数地址**

[![](https://p4.ssl.qhimg.com/t0126e59af83b4fdad7.png)](https://p4.ssl.qhimg.com/t0126e59af83b4fdad7.png)

### <a class="reference-link" name="%EF%BC%882%EF%BC%89%E5%88%9B%E5%BB%BA%E4%B8%80%E4%B8%AA%E7%AA%97%E5%8F%A3%E6%9D%A5%E7%9B%91%E6%8E%A7%E5%89%AA%E5%88%87%E6%9D%BF"></a>**（2）创建一个窗口来监控剪切板**

窗口的类名: L”smclip”;<br>
窗口函数WinMonitorClipBoard

[![](https://p4.ssl.qhimg.com/t013260671ccbf2e24e.png)](https://p4.ssl.qhimg.com/t013260671ccbf2e24e.png)

### **<a class="reference-link" name="%EF%BC%883%EF%BC%89%E7%AA%97%E5%8F%A3%E5%9B%9E%E8%B0%83%E5%87%BD%E6%95%B0WinMonitorClipBoard%E7%9A%84%E9%80%BB%E8%BE%91"></a>（3）窗口回调函数WinMonitorClipBoard的逻辑**

**<a class="reference-link" name="1&gt;%20WM_CREATE%E6%B6%88%E6%81%AF"></a>1&gt; WM_CREATE消息**

[![](https://p3.ssl.qhimg.com/t0148cbbce34e2b54cc.png)](https://p3.ssl.qhimg.com/t0148cbbce34e2b54cc.png)

WM_CREATE是窗口的创建消息，sysmon在WM_CREATE的时候会调用AddClipboardFormatListener(HWND),该函数的作用是指定哪个窗口有资格去捕捉剪贴板内容更新的消息。然后调用hWndNewNext = SetClipboardViewer(a1); SetClipboardViewer()也是监控剪切板事件的设置函数，把当前窗口假如的监控队列里。

**<a class="reference-link" name="2&gt;%20WM_DRAWCLIPBOARD%20%E5%89%AA%E5%88%87%E6%9D%BF%E5%86%85%E5%AE%B9%E5%8F%98%E5%8C%96%E4%BA%8B%E4%BB%B6"></a>2&gt; WM_DRAWCLIPBOARD 剪切板内容变化事件**

当发生这个消息的时候，sysmon 就回调用GetClipboardSequenceNumber函数获取当前窗体在剪切板链下的序列号,调用GetPriorityClipboardFormat获取在一个列表下某个索引的剪切板格式

[![](https://p1.ssl.qhimg.com/t01ba5a39cb59deb36e.png)](https://p1.ssl.qhimg.com/t01ba5a39cb59deb36e.png)

它要获取的是三种格式： CF_TEXT 、 CF_WAVE 、CF_OEMTEXT<br>
接下来就尝试打开剪切板并且获取剪切板里的数据

[![](https://p3.ssl.qhimg.com/t0152d6471f01456d35.png)](https://p3.ssl.qhimg.com/t0152d6471f01456d35.png)

获要获取的就是上述三种格式的数据，获取数据后就计算数据的hash。<br>
为了补充信息，sysmon还会通过GetClipboardOwner获取当前剪切板改变的窗口句柄，然后通过GetWindowThreadProcessId函数获取该窗口的线程以及进程。

[![](https://p3.ssl.qhimg.com/t010ddb3eaf7e05c39e.png)](https://p3.ssl.qhimg.com/t010ddb3eaf7e05c39e.png)

<a class="reference-link" name="3&gt;%20WM_CHANGECBCHAIN%20%E7%9B%91%E6%8E%A7%E9%93%BE%E6%94%B9%E5%8F%98%E7%9A%84%E6%B6%88%E6%81%AF"></a>**3&gt; WM_CHANGECBCHAIN 监控链改变的消息**

这个消息是当有新的监控程序加入或移出，那么就会给这个链表中每个程序发送一个消息WM_CHANGECBCHAIN, sysmon遇到有这个发生的时候会判断是否是自己的消息被移除,了,就把自己再加回来了。

**<a class="reference-link" name="4&gt;%20WM_CLIPBOARDUPDATE%20%E5%89%AA%E5%88%87%E6%9D%BF%E6%9B%B4%E6%96%B0%E6%B6%88%E6%81%AF"></a>4&gt; WM_CLIPBOARDUPDATE 剪切板更新消息**

这个消息是AddClipboardFormatListener消息带来的，Sysmon的处理逻辑与WM_DRAWCLIPBOARD一样。

**<a class="reference-link" name="5&gt;%20WM_QUIT%20%E9%80%80%E5%87%BA%E6%B6%88%E6%81%AF"></a>5&gt; WM_QUIT 退出消息**

[![](https://p0.ssl.qhimg.com/t019cc9aed2a3115d09.png)](https://p0.ssl.qhimg.com/t019cc9aed2a3115d09.png)

退出就销毁当前监控。

sysmon的监控逻辑就这么简单，下面可以自己尝试写一个demo，可以建立一个MFC的窗口程序，窗口初始化的时候调用AddClipboardFormatListener

[![](https://p3.ssl.qhimg.com/t01cf282c3d4be47b30.png)](https://p3.ssl.qhimg.com/t01cf282c3d4be47b30.png)

窗体里继承映射WM_DRAWCLIPBOARD 和 消息

`afx_msg void OnDrawClipboard();`<br>`afx_msg void OnClipboardUpdate();`

`BEGIN_MESSAGE_MAP(CForbidCapDlg, CDialogEx)`<br>`ON_WM_DRAWCLIPBOARD()`<br>`ON_WM_CLIPBOARDUPDATE()`<br>`END_MESSAGE_MAP()`

当我在其他进程鼠标右键复制操作一下，监控程序就会进入OnClipboardUpdate

[![](https://p5.ssl.qhimg.com/t010570f388dc8e9d43.png)](https://p5.ssl.qhimg.com/t010570f388dc8e9d43.png)

Demo实例成功，至此，这篇文章就分析到这里，剪切板的监控就这么简单，大家有兴趣可以自行研究的更深入。
