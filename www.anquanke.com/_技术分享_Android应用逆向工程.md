> 原文链接: https://www.anquanke.com//post/id/86884 


# 【技术分享】Android应用逆向工程


                                阅读量   
                                **153431**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：offensivepentest.com
                                <br>原文地址：[https://offensivepentest.com/2017/08/26/android-application-reverse-engineering/](https://offensivepentest.com/2017/08/26/android-application-reverse-engineering/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01ee71e888c7d378da.jpg)](https://p1.ssl.qhimg.com/t01ee71e888c7d378da.jpg)



译者：[L0phTg](http://bobao.360.cn/member/contribute?uid=2722694252)

预估稿费：260RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**序**



阅读本文最好花费**45Min**~

你经常在用 Burp 拦截信息的时候很迷茫么？你经常在分析用加密的数据进行通信的App，对于需要理解它的数据而疑惑么？在本文，我将会分享很多方法来用于逆向分析APK。我们将会对目标APP采用动态和静态的分析方法。

我创建了一个简单的APP作为分析目标，它的功能只是单纯地对我们输入的数据进行验证，如果用户输入正确的话，将会在屏幕上显示“Congratulations“。

我们先看一下这个应用的源代码以便于我们一会儿能够将它与反编译后的APK代码进行比较。

```
package com.punsec.demo;

import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.util.Base64;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

import javax.crypto.SecretKey;

public class MainActivity extends AppCompatActivity `{`

    TextView result;
    EditText input;
    Button button;

    @Override
    protected void onCreate(Bundle savedInstanceState) `{`
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        input = (EditText) findViewById(R.id.input);
        result = (TextView) findViewById(R.id.result);
        button = (Button) findViewById(R.id.ok);

        button.setOnClickListener(new View.OnClickListener() `{`
            @Override
            public void onClick(View v) `{`
                String a = input.getText().toString();
                String b = getString(R.string.a);
                try `{`
                    SecretKey secretKey = Util.a(new String(Base64.decode(getString(R.string.b), Base64.DEFAULT)));
                    byte e[] = Util.a(a, secretKey);
                    String er = Base64.encodeToString(e, Base64.DEFAULT).trim();

                    if(er.equals(b)) `{`
                        result.setText(getString(R.string.d));
                    `}`else `{`
                        result.setText(getString(R.string.e));
                    `}`

                `}` catch (Exception e) `{`
//                    Log.d("EXCEPTION:", e.getMessage());
                `}`
            `}`
        `}`);
    `}`
`}`
```

这个应用使用下面的这个辅助类来执行一些重要的操作：

```
package com.punsec.demo;

import java.io.UnsupportedEncodingException;
import java.security.InvalidAlgorithmParameterException;
import java.security.InvalidKeyException;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.spec.InvalidKeySpecException;
import java.security.spec.InvalidParameterSpecException;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.NoSuchPaddingException;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;


class Util `{`
    static SecretKey a(String secret)
            throws NoSuchAlgorithmException, InvalidKeySpecException
    `{`
        MessageDigest md = MessageDigest.getInstance("MD5");
        md.update(secret.getBytes());
        byte[] digest = md.digest();
        StringBuilder sb = new StringBuilder();
        for (byte b : digest) `{`
            sb.append(String.format("%02x", (0xFF &amp; b)));
        `}`
        return new SecretKeySpec(sb.toString().substring(0,16).getBytes(), "AES");
    `}`

    static byte[] a(String message, SecretKey secret)
            throws NoSuchAlgorithmException, NoSuchPaddingException, InvalidKeyException, InvalidParameterSpecException, IllegalBlockSizeException, BadPaddingException, UnsupportedEncodingException
    `{`
        Cipher cipher = null;
        cipher = Cipher.getInstance("AES/ECB/PKCS5Padding");
        cipher.init(Cipher.ENCRYPT_MODE, secret);
        return cipher.doFinal(message.getBytes("UTF-8"));
    `}`

    static String a(byte[] cipherText, SecretKey secret)
            throws NoSuchPaddingException, NoSuchAlgorithmException, InvalidParameterSpecException, InvalidAlgorithmParameterException, InvalidKeyException, BadPaddingException, IllegalBlockSizeException, UnsupportedEncodingException
    `{`
        Cipher cipher = null;
        cipher = Cipher.getInstance("AES/ECB/PKCS5Padding");
        cipher.init(Cipher.DECRYPT_MODE, secret);
        return new String(cipher.doFinal(cipherText), "UTF-8");
    `}`
`}`
```

你可以下载已经编译好的APK From -&gt; [CrackMe](https://offensivepentest.com/downloads/CrackMe.apk)

在我们进行下一步的操作之前，先列举分析所需的背景知识:

一个已经root的安卓设备或者虚拟机（虽然并不是所有的分析方法都需要root权限，但是有一个root的设备是不错的）。

[Frida](https://www.frida.re/)

Python

[Inspeckage](https://github.com/ac-pm/Inspeckage)

[Xposed Framework](https://github.com/rovo89/Xposed)

[APKTool](https://ibotpeaches.github.io/Apktool/)

[APKStudio](https://bintray.com/vaibhavpandeyvpz/generic/apkstudio/view)

[ByteCodeViewer](http://bytecodeviewer.com/)

[Dex2Jar](https://sourceforge.net/projects/dex2jar/)

JarSigner(Java JDK)

[JD-JUI](http://jd.benow.ca/)

[Brain](https://www.askideas.com/media/36/I-Cannot-Brain-Today-I-Has-The-Dumb-Funny-Cat-Meme-Image.jpg)

我们将会使用的三种分析方法：



```
动态分析和Hooking.
二进制文件Patch（byte code修改).
静态分析和代码复制.
```



**动态/运行时环境 分析和函数Hooking:**

****

我们需要使用的分析工具: Frida, dex2jar, JD-GUI.

用 Frida分析:

到底什么是Frida ?

```
It's Greasemonkey for native apps, or, put in more technical terms, it’s a dynamic code instrumentation toolkit. It lets you inject snippets of JavaScript or your own library into native apps on Windows, macOS, Linux, iOS, Android, and QNX. Frida also provides you with some simple tools built on top of the Frida API. These can be used as-is, tweaked to your needs, or serve as examples of how to use the API.
```

用简单的术语来说，它能够被用来Hook函数调用，注入你自己的代码未来能够来修改应用本身的执行流程。我们将会使用它来通过检测和来识别不同的变量。

为了能够安装Frida，我们可以将手机开启USB调试之后用数据线连接电脑，并且在电脑端运行



```
# check adb devices whether connected or not
adb devices
# push/copy the latest frida server to phone
adb push frida-server-10.4.0-android-arm /data/local/tmp/frida
# set permissions for frida, grant SU permissions if prompted
adb shell su -c "chmod 755 /data/local/tmp/frida"
# start frida server on android device
adb shell su -c "./data/local/tmp/frida &amp;"
# install frida-python on your Windows/Mac/Linux device
pip install --user frida
```

运行了上面的命令之后，我们的Frida Server就已经运行在了我们的电脑上，让我们来检验一下，打开终端，运行python:



```
Python 2.7.10 (default, Feb  7 2017, 00:08:15)
Type "help", "copyright", "credits" or "license" for more information.
&gt;&gt;&gt; import frida
&gt;&gt;&gt; frida.get_usb_device()
Device(id="802b7421", name="LG SCH-XXXX", type='tether')
```

为了方便以后的分析，现在让我们创建一个python脚本:



```
import frida, sys, time

encrypted = None

def on_message(message, data):
    global encrypted
    try:
        if not encrypted:
          encrypted = message['payload']['encrypted']
          print('[+] Received str : ' + encrypted)
          return
    except:
        pass   
  if message['type'] == 'send':
     print('[*] `{`0`}`'.format(message['payload']))
  elif message['type'] == 'error':
    if "'encrypted' undefined" in message['description']:
          print('[!] Encrypted value not updated yet, try to rotate the device')
    else:
          print('[!] ' + message['description'])
  else:
    print message
      
jscode = open('punsec.js').read()
print('[+] Running')
process_name = 'com.punsec.demo'
device = frida.get_usb_device()
try:
    pid = device.get_process(process_name).pid
    print('[+] Process found')
except frida.ProcessNotFoundError:
    print('[+] Starting process')
    pid = device.spawn([process_name])
    device.resume(pid)
    time.sleep(1)
process = device.attach(pid)
script = process.create_script(jscode)
script.on('message', on_message)
script.load()
while True:
    time.sleep(1)
    if encrypted:
      script.post(`{`'type':'encrypted','value':encrypted`}`)
      break
sys.stdin.read()
```

让我们慢慢讲一些这些代码:

这个Encrypted变量最初是一个无类型的对象，它不久之后就会被脚本来将它更新为一个加密的值。这个 on_message 函数是一个回调函数能够被 frida 的 javascript 代码来利用，在javascript代码之中，我们将注入到我们程序的进程中来回调我们的python代码。这个回调函数能够被通过在javascript代码中的send() 函数来执行。下一个变量是jscode, 它能够将我们的js代码注入到程序的进程中。为了更方便我们阅读，js代码被写到另一个文件中。Process_name变量是我们的进程名字。我们能够通过在adb shell中运行 "ps" 命令 "pm list packages" 命令得到我们应用的进程名字。

这个 device 变量是来连接我们的USB设备(手机)的。Try except 用于处理异常(万一目标程序还没有在我们的设备上运行的话，就会产生异常)。在知道了运行程序的UID后，我们可以挂接到目标程序上，并且在目标进程上注入jscode。通过使用js的 send() 函数，脚本就会开始注册我们的回调函数。下面是 while 循环，可以看到frida实际上是有多么的强大，在这个循环中，我们检测是否encrypted变量它的类型已经不是None了，如果它的类型发生了改变，脚本的post()函数将会发送一个信息将我们的js代码注入到目标进程，并且信息将会被在js代码中的recv() 函数所处理。

在开始下一步的操作之前，我们需要对目标apk进行静态分析。我们首先要反编译apk并且将java bytecode转换为.java格式的代码来阅读。在这里，我们使用的分析工具是dex2jar。



```
$ ./d2j-dex2jar.sh CrackMe.apk
dex2jar CrackMe.apk -&gt; ./CrackMe-dex2jar.jar
```

现在让我们通过JD-GUI来分析刚才生成的CrackMe-dex2jar.jar文件

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t017af7f50a7c320927.png)

可以看到反编译后的代码与原始的java代码还是有很大的不同的。我们来分析一下不同的地方：首先可以很明显的看到资源 id由原来的R.x.x变换称为了数字格式的。

正如我们上面看到的，MainActivity只包含一个 onCreate() 函数。我们首先来看一下android应用的生命周期：  

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ac9fce0966ee766f.png)

可以看到: onCreate() 函数在app启动之后就运行。为了保持应用的实际功能，我们现在就在hook这个函数，来执行对原始函数的调用，能够获取到目前activity的上下文来得到一些字符串的值，就像下面这一行一样：

```
String str = MainActivity.this.getString(2131099669);
```

现在让我们创建punsec.js文件，来得到这些值。



```
Java.perform(function () `{`
    var MainActivity = Java.use('com.punsec.demo.MainActivity');
    MainActivity.onCreate.implementation = function(a) `{`
        this.onCreate(a);
        send(`{`"encrypted":this.getString(2131099669)`}`);
    `}`;
`}`);
```

**Java.perform() **是 frida 定义的，它的功能是：告诉frida server来运行已经包装好的js代码。** Java.use() **是一个包装器为了能够动态的加载packages到我们的目标进程中。为了下一步的需要，我们将会使用**send() **回调函数来发送数据到我们的python程序中。现在运行着的python脚本给我们返回了这样的信息：



```
$ python punsec.py
[+] Running
[+] Starting process
[+] Received str : vXrMphqS3bWfIGT811/V2Q==
```

要记住，要想**onCreate() **函数触发，必须要执行回调函数，也就是在启动进程之后，必须要让它在后台运行后再打开程序，请参考上面的Activity生命周期。

我们也看到了代码中有几个调用来执行 **Base64.decode()** 和通过数字id来得到string, 我们可能也会需要这些值，所以让我们来修改一下我们的代码



```
Java.perform(function () `{`
    var MainActivity = Java.use('com.punsec.demo.MainActivity');
    MainActivity.onCreate.implementation = function(a) `{`
        this.onCreate(a);
        send(`{`'encrypted':this.getString(2131099669)`}`);
    `}`;
    var base64 = Java.use('android.util.Base64');
    base64.decode.overload('java.lang.String', 'int').implementation = function(x, y) `{`
        send('Base64 Encoded : ' + x);
        var buf = new Buffer(base64.decode(x, y));
        send('Base64 Decoded : ' + buf.toString());
        return base64.decode(x, y);
    `}`
 
`}`);
```

再一次运行我们的python程序将会得到下面的输出:



```
$ python punsec.py
[+] Running
[+] Process found
[*] Base64 Encoded : TXlTdXBlclNlY3JldEwzM3RQYXNzdzByZA==
[*] Base64 Decoded : MySuperSecretL33tPassw0rd
```

Hmm, 似乎我们已经成功了。不要着急，现在让我们再来仔细看一下我们的反编译代码:



```
if (Base64.encodeToString(
Util.a(paramAnonymousView, 
Util.a(new String(
Base64.decode(MainActivity.this.getString(2131099683), 0)
)
)
), 
0).trim().equals(str))
```

在上面的代码中，有两次对** Util.a** 函数的调用但是都采用的不同的参数类型，我们已经hook了 **Base64.decode()** 函数，所以现在让我们用下面的代码对** Util.a() **创建一个 hook :



```
Java.perform(function () `{`
    var MainActivity = Java.use('com.punsec.demo.MainActivity');
    MainActivity.onCreate.implementation = function(a) `{`
        this.onCreate(a);
        send(`{`'encrypted':this.getString(2131099669)`}`);
    `}`;
    var base64 = Java.use('android.util.Base64');
    base64.decode.overload('java.lang.String', 'int').implementation = function(x, y) `{`
        send('Base64 Encoded : ' + x);
        var buf = new Buffer(base64.decode(x, y));
        send('Base64 Decoded : ' + buf.toString());
        return base64.decode(x, y);
    `}`
    var Util = Java.use('com.punsec.demo.Util');
    Util.a.implementation;
 
`}`);
```

运行我们的python代码，然后可以得到以下的输出:



```
$ python punsec.py
[+] Running
[+] Process found
[!] Error: a(): has more than one overload, use .overload(&lt;signature&gt;) to choose from:
.overload('java.lang.String')
.overload('java.lang.String', 'javax.crypto.SecretKey')
.overload('[B', 'javax.crypto.SecretKey')
```

这似乎出现了一点错误。看起来是我们的Util类中有函数重载(有相同的方法名称但是拥有不同的参数)。为了克服这个问题, frida提供给我们额外的方法 **overload()**，通过这个方法，我们可以显式地设置哪个方法来 override/hook。我们将会 hook **Util.a(String, SecretKey)**函数(因为它是一个负责加密的函数)来为了进行下一步分析:

 [![](https://p1.ssl.qhimg.com/t01b905ec629ffd448b.png)](https://p1.ssl.qhimg.com/t01b905ec629ffd448b.png)

但是我们怎么样才能识别出这是一个加密函数的呢？首先可以看到这个函数的返回类型是byte，很显然意味着并没有返回一个string类型，同时，本地密码初始化为1来作为第一个参数传递:

 [![](https://p4.ssl.qhimg.com/t0190069cd4e662c0b0.png)](https://p4.ssl.qhimg.com/t0190069cd4e662c0b0.png)

现在，让我们来修改我们的js代码为了能够合理地hook这个函数:



```
Java.perform(function () `{`
    var MainActivity = Java.use('com.punsec.demo.MainActivity');
    MainActivity.onCreate.implementation = function(a) `{`
        this.onCreate(a);
        send(`{`'encrypted':this.getString(2131099669)`}`);
    `}`;
    var base64 = Java.use('android.util.Base64');
    base64.decode.overload('java.lang.String', 'int').implementation = function(x, y) `{`
        send('Base64 Encoded : ' + x);
        var buf = new Buffer(base64.decode(x, y));
        send('Base64 Decoded : ' + buf.toString());
        return base64.decode(x, y);
    `}`
    var Util = Java.use('com.punsec.demo.Util');
    Util.a.overload('java.lang.String', 'javax.crypto.SecretKey').implementation = function(x, y) `{`
        send('UserInput : ' + x);
        return this.a(x,y);
    `}`
 
`}`);
```

再次运行我们的python程序，观察输出有哪些改变:



```
$ python punsec.py
[+] Running
[+] Process found
[*] Base64 Encoded : TXlTdXBlclNlY3JldEwzM3RQYXNzdzByZA==
[*] Base64 Decoded : MySuperSecretL33tPassw0rd
[*] UserInput : wrongSecretTest
```

极好的，我们现在可以拦截我们的输出了。现在我们可以发现 Util 类还有一个函数** Util.a(byte, SecretKey)** 一直没有在app中使用，通过分析可以看到这是一个解密函数。所以现在我们该如何做呢？ 加密函数已经接收到了密钥，所以我们可以在解密函数中利用，但是我们还需要第一个参数。第一个参数是一个 base64 解密的string 变量。所以让我们来修改我们的代码，为了能够在我们的 js中收到这个参数，并且过掉这个解密函数，这样的话，我们就能解密最终的Key来完成这次挑战。现在最后一次修改我们的js代码:



```
Java.perform(function () `{`
    var MainActivity = Java.use('com.punsec.demo.MainActivity');
    MainActivity.onCreate.implementation = function(a) `{`
        this.onCreate(a);
        send(`{`'encrypted':this.getString(2131099669)`}`);
    `}`;
    var base64 = Java.use('android.util.Base64');
    base64.decode.overload('java.lang.String', 'int').implementation = function(x, y) `{`
        // send('Base64 Encoded : ' + x);
        // var buf = new Buffer(base64.decode(x, y));
        // send('Base64 Decoded : ' + buf.toString());
        return base64.decode(x, y);
    `}`
    var Util = Java.use('com.punsec.demo.Util');
    Util.a.overload('java.lang.String', 'javax.crypto.SecretKey').implementation = function(x, y) `{`
        recv('encrypted', function onMessage(payload) `{` 
            encrypted = payload['value']; 
        `}`);
        cipher = base64.decode(encrypted, 0); // call the above base64 method
        secret = this.a(cipher, y); // call decrypt method
        send('Decrypted : ' + secret)
        return this.a(secret,y);
    `}`
 
`}`);
```

我们把一个 **recv() **调用放在了函数中以便于可以收到我们写的python程序中已经存储的加密string。现在解密这个已经被加密过的base64密钥并且和密钥一起发送到解密函数中。现在让我们再一次运行我们的python程序：



```
$ python punsec.py
[+] Running
[+] Process found
[!] Encrypted value not updated yet, try to rotate the device
[+] Received str : vXrMphqS3bWfIGT811/V2Q==
[*] Decrypted : knb*AS234bnm*0
```

woah, 我们得到了key。这也会覆盖掉任何的用户输入并将其替换为解密的string, 所以现在每一个用户输入都是起作用的:  

[![](https://p4.ssl.qhimg.com/t019c8ffb907a10c4f2.png)](https://p4.ssl.qhimg.com/t019c8ffb907a10c4f2.png)

现在我们不仅用实际的secret覆盖了用户输入，而且还覆盖了实际的secret phrase为了通过这个挑战。

假使我们的apk应用中没有解密函数，我们该怎么办呢？ 不必担心，我们能巧妙的将js代码插入到package中来执行解密操作并且用必要的参数覆盖这个方法，或者我们还可以用下面的python代码来解密:

```
import frida, sys, time, md5
from Crypto.Cipher import AES

encrypted = None
secretKey = None


def decrypt(encrypted, key):
  key = md5.new(key).hexdigest()[:16]
  cipher = AES.new(key)
  decrypted = cipher.decrypt(encrypted.decode('base64'))[:14]

  for i in range(1,len(encrypted.decode('base64'))/16):
    cipher = AES.new(key, AES, encodedEncrypted.decode('base64')[(i-1)*16:i*16])
    decrypted += cipher.decrypt(encodedEncrypted.decode('base64')[i*16:])[:16]

  return decrypted.strip()

def on_message(message, data):
    global encrypted, secretKey
    try:
      if not encrypted:
        encrypted = message['payload']['encrypted']
      if not secretKey:
        secretKey = message['payload']['secretKey']
    except:
      pass
    if message['type'] == 'send':
      print('[*] `{`0`}`'.format(message['payload']))
    elif message['type'] == 'error':
      if 'ReferenceError' in message['description']:
        print('[!] Rotate the device')
      else:
        print('[!] ' + message['description'])
    else:
      print message
      
jscode = open('punsec.js').read()

print('[+] Running')

process_name = 'com.punsec.demo'
device = frida.get_usb_device()

try:
    pid = device.get_process(process_name).pid
    print('[+] Process found')
except frida.ProcessNotFoundError:
    print('[+] Starting process')
    pid = device.spawn([process_name])
    device.resume(pid)
    time.sleep(1)

process = device.attach(pid)

script = process.create_script(jscode)
script.on('message', on_message)
script.load()
while True:
    time.sleep(0.2)
    if encrypted and secretKey:
      script.post(`{`'type':'encrypted','value':decrypt(encrypted, secretKey)`}`)
      break
sys.stdin.read()
```

我们更新后的js代码:



```
Java.perform(function () `{`
    var MainActivity = Java.use('com.punsec.demo.MainActivity');
    MainActivity.onCreate.implementation = function(a) `{`
        this.onCreate(a);
        send(`{`'encrypted':this.getString(2131099669)`}`);
    `}`;
    var base64 = Java.use('android.util.Base64');
    base64.decode.overload('java.lang.String', 'int').implementation = function(x, y) `{`
        var buf = new Buffer(base64.decode(x, y));
        send(`{`'secretKey': buf.toString()`}`);
        return base64.decode(x, y);
    `}`
    var Util = Java.use('com.punsec.demo.Util');
    Util.a.overload('java.lang.String', 'javax.crypto.SecretKey').implementation = function(x, y) `{`
        recv('encrypted', function onMessage(payload) `{` 
            secret = payload['value']; 
        `}`);
        send('Decrypted : ' + secret)
        return this.a(secret,y);
    `}`
 
`}`);
```

现在运行我们的python程序:



```
$ python punsec.py
[+] Running
[+] Process found
[*] `{`u'secretKey': u'MySuperSecretL33tPassw0rd'`}`
[!] Rotate the device
[*] `{`u'encrypted': u'vXrMphqS3bWfIGT811/V2Q=='`}`
[*] `{`u'secretKey': u'MySuperSecretL33tPassw0rd'`}`
[*] Decrypted : knb*AS234bnm*0
```

<br>

**用 Inspeckage 来分析**

****

我们将会使用到Inspeckage, Xposed Framework 和 ApkStudio/ByteCodeViewer.

Inspeckage – Android Package Inspector

```
Inspeckage is a tool developed to offer dynamic analysis of Android applications. By applying hooks to functions of the Android API, Inspeckage will help you understand what an Android application is doing at runtime.
```

Inspeckage可以让你来用简单的web接口进行分析。Inspeckage需要你安装Inspeckage Xposed module并且在 Xpose 框架中激活它。在你的android设备上启动Inspeckage App并且选择我们的目标应用并且在Inspeckage Webserver中浏览。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t016152e0013935706d.png) 

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t016fc220b3b7bb543d.png)

打开自动刷新开关，点击在webserver上的设置按钮并且关闭一些Actvity检测就像下面这张图一样，最后点击 start App 并且刷新页面。

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c243279b03fcd668.png)

一旦我们的App在手机上运行，就在App上输入测试的数据并点击ok按钮，然后观察Inspeckage webserver上的通知(注意要开启自动刷新):

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01dea274f9a7233536.png)

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01212b8a79fb4928c3.png)

这两张截图都显示出了我们使用了frida方法。用 Inspeckage分析是相当简单的，你可以检测app执行的文件系统Activities, SQL队列操作，在这背后使用的是和我们使用frida方法相同的概念: 在加密，文件系统，hash等操作函数上进行hook，但是在这里，我们可以执行函数hook吗? 当然了，正如你在最后一个标签上看到的，它提供了一个hook选项。但是随之而来的问题是：它不像frida那样，Inseckage没有提供对重载的方法的覆盖，现在点击hook标签并且创建一个hook来验证我们的想 法:  

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01fd1266c050933682.png)

所以现在为了能够创建一个有效的hook，我们将会使用 ByteCodeViewer 或者 APKStudio 来修改apk中的 bytecode(字节码)。下面这是我们对字节码的patch:

 [![](https://p1.ssl.qhimg.com/t010d616872d99b3e2a.png)](https://p1.ssl.qhimg.com/t010d616872d99b3e2a.png)

(注意：当打开apk的时候，取消选择"Decode Resource"，否则你将会遇到下面这些问题)



```
ERROR: 9-patch image C:UserslabuserDesktopCrackMeresdrawable-mdpi-v4abc_list_divider_mtrl_alpha.9.png malformed.
       Must have one-pixel frame that is either transparent or white.
ERROR: Failure processing PNG image C:UserslabuserDesktopCrackMeresdrawable-mdpi-v4abc_list_divider_mtrl_alpha.9.png
ERROR: 9-patch image C:UserslabuserDesktopCrackMeresdrawable-hdpi-v4abc_list_divider_mtrl_alpha.9.png malformed.
       Must have one-pixel frame that is either transparent or white.
ERROR: Failure processing PNG image C:UserslabuserDesktopCrackMeresdrawable-hdpi-v4abc_list_divider_mtrl_alpha.9.png
ERROR: 9-patch image C:UserslabuserDesktopCrackMeresdrawable-xhdpi-v4abc_list_divider_mtrl_alpha.9.png malformed.
       Must have one-pixel frame that is either transparent or white.
ERROR: Failure processing PNG image C:UserslabuserDesktopCrackMeresdrawable-xhdpi-v4abc_list_divider_mtrl_alpha.9.png
ERROR: 9-patch image C:UserslabuserDesktopCrackMeresdrawable-xxhdpi-v4abc_list_divider_mtrl_alpha.9.png malformed.
       Must have one-pixel frame that is either transparent or white.
ERROR: Failure processing PNG image C:UserslabuserDesktopCrackMeresdrawable-xxhdpi-v4abc_list_divider_mtrl_alpha.9.png
```

在上面那副截图中，可以看到第168行，我们通过识别第168行的参数类型和返回值，成功的识别出了这就是加密函数，在第197行，这个被赋值为1的变量也是我们之前看到的。我们已经把这个函数的名字改成了b ,并且解密函数名称改为c。现在为了保证我们的app可以正常运行，我们需要在MainActivity的字节码上做出相同的更新:

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01187d48b490c8a9c3.png)

现在我们的任务已经完成了，可以创建一个**keystore**来对我们的apk进行签名。



```
C:Program FilesJavajdk1.8.0_144bin&gt;keytool -genkey -v -keystore C:userslabuserDesktopmy.keystore -alias alias_na
me -keyalg RSA -keysize 2048 -validity 10000
Enter keystore password:
Re-enter new password:
What is your first and last name?
  [Unknown]:
What is the name of your organizational unit?
  [Unknown]:
What is the name of your organization?
  [Unknown]:
What is the name of your City or Locality?
  [Unknown]:
What is the name of your State or Province?
  [Unknown]:
What is the two-letter country code for this unit?
  [Unknown]:
Is CN=Unknown, OU=Unknown, O=Unknown, L=Unknown, ST=Unknown, C=Unknown correct?
  [no]:  yes
Generating 2,048 bit RSA key pair and self-signed certificate (SHA256withRSA) with a validity of 10,000 days
        for: CN=Unknown, OU=Unknown, O=Unknown, L=Unknown, ST=Unknown, C=Unknown
Enter key password for &lt;alias_name&gt;
        (RETURN if same as keystore password):
[Storing C:userslabuserDesktopmy.keystore]
C:Program FilesJavajdk1.8.0_144bin&gt;jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore C:userslabuserDesktopmy.keystore C:userslabuserDesktopCrackMe.apk alias_name
```

将已经签名的apk安装到设备上。重启Inspeckage，开始hook来验证是否我们的修改已经起作用了。

 [![](https://p1.ssl.qhimg.com/t01f474be241cc56d34.png)](https://p1.ssl.qhimg.com/t01f474be241cc56d34.png)

极好地，我们的修改是完美的，现在我们可以对目标函数**Util.b() **下hook。选择这个函数并且点击 Add hook 按钮。现在让我们点击ok按钮并且观察Inspeckage Server的通知。

 [![](https://p3.ssl.qhimg.com/t019845f392b8416f56.png)](https://p3.ssl.qhimg.com/t019845f392b8416f56.png)

我们可以看到Inspeckage已经成功地从已经hook的函数中截取到数据并且提供给我们了函数的参数和返回值。现在点击 Replace 按钮并且配置如下的选项。

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t017b0658e42a1681f6.png)

在这里我们将第一个参数传递给了我们的加密函数，这个函数拥有我们已经用frida识别出来的秘密值。无论什么时候进行输入测试(大小写敏感)，Hook都会替换数据并且传递我们提供的值，然后将Congratulations再一次显示在我们的屏幕上。

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t013e82b79efa49c4f3.png)

<br>

**二进制补丁（字节码修改）**

****

在这个方法中，我们将会使用**ApkStudio**和**Jarsigner**。 我们将会通过修改反编译的Apk，之后重新编译它来修改程序的逻辑。启动 ApkStudio并且再次加载文件( 记住要取消选择"Decode Resources"复选框)，之后在MainActivity$1.smali中定位到程序代码中进行比较的位置

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01a441e52a3a16852f.png)

我们可以在第113行看到程序会比较两个不同的值来执行检测，如果比较失败了，会显示"Umm, Try Again"。但是如果程序总是将两个相同的值进行比较会怎么样呢？在这种情况下，程序将会跳过else条件直接返回true。所以现在让我们将代码修改后重新编译并对我们的Apk进行签名，然后做测试。

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01bf2e4f8b4b680ceb.png)

再一次运行应用验证是否程序是否通过了原来的程序逻辑。

<br>

**静态分析和代码复制**

****

在这个方法中，我们将会使用**Android Studio/IntelliJ **和** ByteCodeViewer**来进行静态代码分析。



```
Static analysis
Also called static code analysis, is a method of computer program debugging that is done by examining the code without executing the program. The process provides an understanding of the code structure, and can help to ensure that the code adheres to industry standards.
```

启动 ByteCodeViewer(BCV) 并且等待它来安装依赖项。一旦安装好了之后，我们将可以直接在它里面打开apk文件。在BCV中，点击File-&gt;Add 并且选择 CrackMe.apk，然后让它完成加载这个文件。点击**View-&gt;Pane1-&gt;Procyon-&gt;java** 和**View-&gt;Pane2-&gt;Smali/Dex-&gt;Samli/Dex** 。你的界面将会看起来和下面的一样

 [![](https://p4.ssl.qhimg.com/t0169b5db07390c7fe9.png)](https://p4.ssl.qhimg.com/t0169b5db07390c7fe9.png)

在第9行，我们可以看到"final String string2 = this.this$0.getString(2131099669);"。在当前活动上下文的getString()方法，可以使用"this"，"MainActivity.this "或者"getApplicationContext() " 通过一个整数值来得到资源值。这些数字id的索引在R类中被创建，所以我们将会在R$string.class 中寻找资源id，BCV可以将内容识别为xml 文件格式。

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0127a50619a607dcac.png)

我们可以看到这个整数值被分配给a，现在我们不得不对a在strings.xml中做一个查找，你可以在BCV中通过展开**CrackMe.apk-&gt;Decoded Resources-&gt;res-&gt;values-&gt;strings.xml **。

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e55406c413cd4794.png)

有时候BCV打开文件会呈现出二进制形式而不是xml格式，对于这种情况，我们可以点击File-&gt;Save As Zip ，然后解压zip并且在编辑器中打开strings.xml。

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t015973be323327c6bd.png)

极好的，我们已经找到了这个字符串。我们将会用这个方法恢复所有的字符串并且保存它们。



```
2131099669 -&gt; a -&gt; vXrMphqS3bWfIGT811/V2Q==
2131099683 -&gt; b -&gt; TXlTdXBlclNlY3JldEwzM3RQYXNzdzByZA==
2131099685 -&gt; d -&gt; Congratulations
2131099686 -&gt; e -&gt; Umm, Try again
```

我们将会使用IntelliJ来写我们的代码来试图实现逆向原始函数的功能，通过从BCV反编译后的文件中复制代码。 当所有的代码让在一块的时候，它将会看起来像下面的代码



```
import javax.crypto.Cipher;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;
import java.security.MessageDigest;
import java.util.Base64;
class Decrypt `{`

    public static void main(String args[]) `{`
        String a = "vXrMphqS3bWfIGT811/V2Q==";
        String b = "TXlTdXBlclNlY3JldEwzM3RQYXNzdzByZA==";
        String new_b = new String(Base64.getDecoder().decode(b));

        byte[] array = Base64.getDecoder().decode(a);
        String decoded = decrypt(array, getKey(new_b));

        System.out.println("Decoded : " + decoded);
    `}`

    private static String decrypt(byte[] array, SecretKey secretKey) `{`
        String decoded = null;
        try `{`

            Cipher instance = Cipher.getInstance("AES/ECB/PKCS5Padding");
            instance.init(2, secretKey);
            decoded = new String(instance.doFinal(array), "UTF-8");
        `}`catch (Exception e) `{`
            // do something
        `}`
        return decoded;
    `}`
    
    private static SecretKey getKey(String s) `{`
        SecretKeySpec secretKeySpec = null;
        try `{`
            MessageDigest instance = MessageDigest.getInstance("MD5");
            instance.update(s.getBytes());
            byte[] digest = instance.digest();
            StringBuilder sb = new StringBuilder();
            for (int length = digest.length, i = 0; i &lt; length; ++i) `{`
                sb.append(String.format("%02x", digest[i] &amp; 0xFF));
            `}`
            secretKeySpec = new SecretKeySpec(sb.toString().substring(0, 16).getBytes(), "AES");
        `}` catch (Exception e) `{`
            // do something
        `}`
        return secretKeySpec;
    `}`
`}`
```

将文件命名为**Decrypt.java** 并保存文件。我们需要编译这个文件，然后运行它来检测我们的代码是否起作用了。



```
// create new file
$ nano Decrypt.java
// compile file
$ javac Decrypt.java
// run file
$ java Decrypt
Decoded : knb*AS234bnm*0
```

我们可以在python代码中做同样的事情，就像先前frida那样，但是有时候复制代码是更简单的，因为只需要做很小的修改就可以使它运行。

我们已经描述了所提到的所有工具和方法，现在是时候喝杯咖啡了。
