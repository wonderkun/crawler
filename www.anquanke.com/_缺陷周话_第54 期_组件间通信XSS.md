> 原文链接: https://www.anquanke.com//post/id/188817 


# 【缺陷周话】第54 期：组件间通信XSS


                                阅读量   
                                **665290**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t01649690fcb193fd32.jpg)](https://p4.ssl.qhimg.com/t01649690fcb193fd32.jpg)

## 1、组件间通信 XSS
- CWE ID 79: ImproperNeutralization of Input During Web Page Generation (‘Cross-site Scripting’)(http://cwe.mitre.org/data/definitions/79.html)
- CWE ID 80: Improper Neutralization of Script-Related HTML Tags in a Web Page (BasicXSS)(http://cwe.mitre.org/data/definitions/80.html)
- CWE ID 81: Improper Neutralization of Script in an Error Message Web Page (http://cwe.mitre.org/data/definitions/81.html)
- CWE ID 82: Improper Neutralization of Script in Attributes of IMG Tags in a Web Page (http://cwe.mitre.org/data/definitions/82.html)
- CWE ID 83: Improper Neutralization of Script in Attributes in a Web Page (http://cwe.mitre.org/data/definitions/83.html)


## 2、“组件间通信 XSS”的危害

javaScript 调用应用程序代码打破了传统浏览器安全模式。如果用户被WebView导航到不受信任的恶意网站，恶意页面可能会对潜在敏感应用程序数据进行访问。同样，应用程序使用HTTP加载网页而用户连接了不安全的wifi网络，则攻击者可能会将恶意内容注入页面并引发类似攻击。

从2018年1月至2019年9月，CVE中共有2条漏洞信息与其相关。漏洞如下：

<th width="160">CVE</th><th width="376">概述</th>
|------
<td width="156">CVE-2019-1677</td><td width="397">Android 版Cisco Webex Meetings 中的漏洞可能允许未经身份验证的本地攻击者对应用程序执行跨站点脚本攻击。该漏洞是由于对应用程序输入参数的验证不足所致。攻击者可以通过 Intent 将恶意请求发送到 Webex Meetings 应用程序来利用此漏洞。成功利用此漏洞可以使攻击者在 Webex Meetings 应用程序的上下文中执行脚本代码。11.7.0.236 之前的版本会受到影响。</td>
<td width="156">CVE-2018-18362</td><td width="397">适用于Android 的 Norton Password Manager（以前称为Norton IdentitySafe）可能容易受到跨站点脚本（XSS）的利用，攻击者可以将客户端脚本注入其他用户查看的网页中，也可能利用跨站点脚本漏洞潜在地绕过诸如同源策略之类的访问控制。</td>



## 3、示例代码

### 3.1 缺陷代码

[![](https://p2.ssl.qhimg.com/t01cf409054635977b8.png)](https://p2.ssl.qhimg.com/t01cf409054635977b8.png)

上述代码操作是获取 intent（intent用于解决Android应用的各项组件之间的通讯，可简单理解为消息传递工具）接收到的值作为 url 并使用 WebView 进行加载。首先第14行 Activity 加载布局文件，第15行通过 findViewById() 方法找到布局文件中对应的 WebView 控件，第16行允许 WebView 执行JavaScript 脚本。第17行 this.getIntent() 先获取到上一个 Activity 启动的intent，然后调用 getExtras() 方法得到intent所附带的额外数据，这些数据以 KEY- VALUE 的形式存在，getString(“url”) 获取到 KEY 为“url”对应的值。第18行 WebView 作为网页加载控件对指定的url进行加载。 如果 url 的值以“javascript:”开头，则接下来的 JavaScript 代码将在 WebView 中的Web 页面上下文内部执行，例如 “javascript:alert(/xss/)”会在页面中弹出一个警告消息框，破坏网页结构。

[![](https://p2.ssl.qhimg.com/t014959a8b13c1ce028.png)](https://p2.ssl.qhimg.com/t014959a8b13c1ce028.png)

图1：“组件间通信 XSS”检测示例

### 3.2 修复代码

[![](https://p4.ssl.qhimg.com/t01ee4633c7d60ccf83.png)](https://p4.ssl.qhimg.com/t01ee4633c7d60ccf83.png)

在上述修复代码中，在第19行使用 Uri.encode()对接收的url进行编码，该方法使用UTF-8编码集将给定字符串中的某些字符进行编码，避免不安全字符引起程序解析歧义，其中字母(“A-Z”,”a-z”)，数字（“0-9”），字符（“ _- !.〜’（）*”）不会被编码。

使用代码卫士对修复后的代码进行检测，可以看到已不存在“组件间通信XSS”缺陷。如图2所示：

[![](https://p0.ssl.qhimg.com/t01c919579cbe136292.png)](https://p0.ssl.qhimg.com/t01c919579cbe136292.png)

图2：修复后检测结果



## 4、如何避免“组件间通信 XSS”

（1）对用户的输入进行合理验证，对特殊字符（如&lt;、&gt;、’、”等）以及 &lt;script&gt;、 javascript 等进行过滤。

（2）采用 OWASP ESAPI 对数据输出 HTML 上下文中不同位置（HTML 标签、HTML 属性、JavaScript 脚本、CSS、URL）进行恰当的输出编码。

（3）设置 HttpOnly 属性，避免攻击者利用跨站脚本漏洞进行 Cookie 劫持攻击。在 Java EE 中，给 Cookie 添加 HttpOnly 的代码如下：

[![](https://p5.ssl.qhimg.com/t01433430823c30c574.png)](https://p5.ssl.qhimg.com/t01433430823c30c574.png)
