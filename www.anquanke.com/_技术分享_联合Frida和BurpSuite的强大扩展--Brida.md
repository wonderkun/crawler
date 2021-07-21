> 原文链接: https://www.anquanke.com//post/id/86567 


# 【技术分享】联合Frida和BurpSuite的强大扩展--Brida


                                阅读量   
                                **246784**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：安全客
                                <br>原文地址：[https://techblog.mediaservice.net/2017/07/brida-advanced-mobile-application-penetration-testing-with-frida/](https://techblog.mediaservice.net/2017/07/brida-advanced-mobile-application-penetration-testing-with-frida/)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p3.ssl.qhimg.com/t017dffa7a89adf2033.png)](https://p3.ssl.qhimg.com/t017dffa7a89adf2033.png)**



作者：[for_while](http://bobao.360.cn/member/contribute?uid=2553709124)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**插件介绍**



在测试一些应用的时候（以移动端为例），会经常发现客户端和服务端的通讯数据是加密过的，在这种情况下，我们如果想继续测试下去，就得去逆向程序中使用的加密算法，然后写程序实现它，然后在后续测试中使用它。这种方式需要耗费大量的时间和精力。而 [Brida ](https://github.com/federicodotta/Brida)这款插件的出现简直天降神器。Frida 是一款多平台的 hook框架， 其具体功能请看官网：[https://www.frida.re/](https://www.frida.re/) 。

Brida使用了 frida的功能，并且和 BurpSuite结合，可以在 BurpSuite中**直接调用目标应用程序中的加/解密函数**，而不用去逆向它，节省精力。

<br>

**插件安装**



安装 python 2.7 和 Pyro4 模块（可以使用 pip安装：pip install pyro4 ）

下载 [Brida_01.jar](https://github.com/federicodotta/Brida/releases/download/v0.1/Brida_01.jar), 并在 BurpSuite 中手动安装该 jar 包

[![](https://p2.ssl.qhimg.com/t016431e8fdd56495ce.jpg)](https://p2.ssl.qhimg.com/t016431e8fdd56495ce.jpg)



Tips：**插件安装，使用过程中出现了问题请查看插件的错误日志**

[![](https://p3.ssl.qhimg.com/t01317371f2314e8857.jpg)](https://p3.ssl.qhimg.com/t01317371f2314e8857.jpg)



**插件测试**



为了测试该插件，写了个安卓的apk, 使用 Java实现了一个 Encryption类用于对数据进行 AES加密和解密。该类的代码如下：

```
import java.security.SecureRandom;
import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;

/**
 * Created by Administrator on 2017/7/30.
 */

public class Encryption `{`
    private final static String HEX = "0123456789ABCDEF";
    private  static final String CBC_PKCS5_PADDING = "AES/CBC/PKCS5Padding";//AES是加密方式 CBC是工作模式 PKCS5Padding是填充模式
    private  static final String AES = "AES";//AES 加密
    private  static final String  SHA1PRNG="SHA1PRNG";//// SHA1PRNG 强随机种子算法, 要区别4.2以上版本的调用方法
    /*
     * 加密
     */
    public static String encrypt(String key, String cleartext) `{`
        if (cleartext.isEmpty()) `{`
            return cleartext;
        `}`
        try `{`
            byte[] result = encrypt(key, cleartext.getBytes());
            return bytesToHexString(result);
        `}` catch (Exception e) `{`
            e.printStackTrace();
        `}`
        return null;
    `}`
   /*
    * 加密
    */
    private static byte[] encrypt(String key, byte[] clear) throws Exception `{`
        byte[] raw = getRawKey(key.getBytes());
        SecretKeySpec skeySpec = new SecretKeySpec(raw, AES);
        Cipher cipher = Cipher.getInstance(CBC_PKCS5_PADDING);
        cipher.init(Cipher.ENCRYPT_MODE, skeySpec, new IvParameterSpec(new byte[cipher.getBlockSize()]));
        byte[] encrypted = cipher.doFinal(clear);
        return encrypted;
    `}`

    /*
     * 解密
     */
    public static String decrypt(String key, String encrypted) `{`
        if (encrypted.isEmpty()) `{`
            return encrypted;
        `}`
        try `{`
            byte[] enc = hexStringToBytes(encrypted);
            byte[] result = decrypt(key, enc);
            return new String(result);
        `}` catch (Exception e) `{`
            e.printStackTrace();
        `}`
        return null;
    `}`
    
     /*
     * 解密
     */
    private static byte[] decrypt(String key, byte[] encrypted) throws Exception `{`
        byte[] raw = getRawKey(key.getBytes());
        SecretKeySpec skeySpec = new SecretKeySpec(raw, AES);
        Cipher cipher = Cipher.getInstance(CBC_PKCS5_PADDING);
        cipher.init(Cipher.DECRYPT_MODE, skeySpec, new IvParameterSpec(new byte[cipher.getBlockSize()]));
        byte[] decrypted = cipher.doFinal(encrypted);
        return decrypted;
    `}`

    /**
     * Convert byte[] to hex string.这里我们可以将byte转换成int，然后利用Integer.toHexString(int)来转换成16进制字符串。
     * @param src byte[] data
     * @return hex string
     */
    public static String bytesToHexString(byte[] src)`{`
        StringBuilder stringBuilder = new StringBuilder("");
        if (src == null || src.length &lt;= 0) `{`
            return null;
        `}`
        for (int i = 0; i &lt; src.length; i++) `{`
            int v = src[i] &amp; 0xFF;
            String hv = Integer.toHexString(v);
            if (hv.length() &lt; 2) `{`
                stringBuilder.append(0);
            `}`
            stringBuilder.append(hv);
        `}`
        return stringBuilder.toString();
    `}`
    /**
     * Convert hex string to byte[]  
     * @param hexString the hex string  
     * @return byte[]
     */
    public static byte[] hexStringToBytes(String hexString) `{`
        if (hexString == null || hexString.equals("")) `{`
            return null;
        `}`
        hexString = hexString.toUpperCase();
        int length = hexString.length() / 2;
        char[] hexChars = hexString.toCharArray();
        byte[] d = new byte[length];
        for (int i = 0; i &lt; length; i++) `{`
            int pos = i * 2;
            d[i] = (byte) (charToByte(hexChars[pos]) &lt;&lt; 4 | charToByte(hexChars[pos + 1]));
        `}`
        return d;
    `}`
    /**
     * Convert char to byte  
     * @param c char  
     * @return byte
     */
    private static byte charToByte(char c) `{`
        return (byte) "0123456789ABCDEF".indexOf(c);
    `}`
        // 对密钥进行处理
    private static byte[] getRawKey(byte[] seed) throws Exception `{`
        KeyGenerator kgen = KeyGenerator.getInstance(AES);
        //for android
        SecureRandom sr = null;
        // 在4.2以上版本中，SecureRandom获取方式发生了改变
        if (android.os.Build.VERSION.SDK_INT &gt;= 17) `{`
            sr = SecureRandom.getInstance(SHA1PRNG, "Crypto");
        `}` else `{`
            sr = SecureRandom.getInstance(SHA1PRNG);
        `}`
        // for Java
        // secureRandom = SecureRandom.getInstance(SHA1PRNG);
        sr.setSeed(seed);
        kgen.init(128, sr); //256 bits or 128 bits,192bits
        //AES中128位密钥版本有10个加密循环，192比特密钥版本有12个加密循环，256比特密钥版本则有14个加密循环。
        SecretKey skey = kgen.generateKey();
        byte[] raw = skey.getEncoded();
        return raw;
    `}`

`}`
```

Encryption.encrypt(key, str) 用于对str, 使用 key进行 aes加密，Encryption.decrypt(key, str)则用于解密。他们均返回处理后的字符串。为了模拟在安全测试中的场景，我会在burp中使用 Brida插件 调用 Encryption.encrypt 进行加密， 调用Encryption.decrypt 进行解密。

正常情况下，进入插件的界面如下：

[![](https://p3.ssl.qhimg.com/t01c15eb5f71b7d5d57.jpg)](https://p3.ssl.qhimg.com/t01c15eb5f71b7d5d57.jpg)

其实最重要的就是 Frida js文件的内容了。下面给一个官方的[例子](https://github.com/federicodotta/Brida/blob/master/jsSkeleton/scriptBrida.js)

```
'use strict';
// 1 - FRIDA EXPORTS

rpc.exports = `{`

	// BE CAREFUL: Do not use uppercase characters in exported function name (automatically converted lowercase by Pyro)

	exportedfunction: function() `{`

		// Do stuff...	
		// This functions can be called from custom plugins or from Brida "Execute method" dedicated tab

	`}`,

	// Function executed when executed Brida contextual menu option 1.
	// Input is passed from Brida encoded in ASCII HEX and must be returned in ASCII HEX (because Brida will decode the output
	// from ASCII HEX). Use auxiliary functions for the conversions.
	contextcustom1: function(message) `{`
		return "6566";
	`}`,

	// Function executed when executed Brida contextual menu option 2.
	// Input is passed from Brida encoded in ASCII HEX and must be returned in ASCII HEX (because Brida will decode the output
	// from ASCII HEX). Use auxiliary functions for the conversions.
	contextcustom2: function(message) `{`
		return "6768";
	`}`,

	// Function executed when executed Brida contextual menu option 3.
	// Input is passed from Brida encoded in ASCII HEX and must be returned in ASCII HEX (because Brida will decode the output
	// from ASCII HEX). Use auxiliary functions for the conversions.
	contextcustom3: function(message) `{`
		return "6768";
	`}`,
	// Function executed when executed Brida contextual menu option 4.
	// Input is passed from Brida encoded in ASCII HEX and must be returned in ASCII HEX (because Brida will decode the output
	// from ASCII HEX). Use auxiliary functions for the conversions.
	contextcustom4: function(message) `{`
		return "6768";
	`}`

`}`

// 2 - AUXILIARY FUNCTIONS

// Convert a hex string to a byte array
function hexToBytes(hex) `{`
    for (var bytes = [], c = 0; c &lt; hex.length; c += 2)
    bytes.push(parseInt(hex.substr(c, 2), 16));
    return bytes;
`}`

// Convert a ASCII string to a hex string
function stringToHex(str) `{`
    return str.split("").map(function(c) `{`
        return ("0" + c.charCodeAt(0).toString(16)).slice(-2);
    `}`).join("");
`}`

// Convert a hex string to a ASCII string
function hexToString(hexStr) `{`
    var hex = hexStr.toString();//force conversion
    var str = '';
    for (var i = 0; i &lt; hex.length; i += 2)
        str += String.fromCharCode(parseInt(hex.substr(i, 2), 16));
    return str;
`}`
// Convert a byte array to a hex string
function bytesToHex(bytes) `{`
    for (var hex = [], i = 0; i &lt; bytes.length; i++) `{`
        hex.push((bytes[i] &gt;&gt;&gt; 4).toString(16));
        hex.push((bytes[i] &amp; 0xF).toString(16));
    `}`
    return hex.join("");
`}`

// 3 - FRIDA HOOKS (if needed)

if(ObjC.available) `{`
	// Insert here Frida interception methods, if needed 
	// (es. Bypass Pinning, save values, etc.)

`}`
```

代码中的注释写的非常清楚，我说一下我认为的重点。

**rpc.exports的每一项是一个函数， : 前面的为函数名（全部为小写），比如 contextcustom1, 后面为函数的具体内容，rpc.exports中的函数都可以被 Brida调用。**

**contextcustom1 和 contextcustom2可以在 burp中使用右键调用，不能改他们的名字**

**函数接收的参数，和返回的数据都是以 16进制编码的，所以我们使用时要先对他们进行16进制解码，然后返回的时候在进行16进制编码。在上述脚本中包含了这些转换所需的函数，方便我们进行处理。<br>**

**该脚本会被Frida注入到我们在 Brida中指定的进程中所以我们可以直接使用 Frida的 api。**

我们可以先试试，Brida能否正常运行，类似上图设置好参数，使用官方的那个js文件，以安卓为例，使用 Frida Remote.

首先我们要在 android设备上安装 Frida,安装过程可以参考这里： [http://www.jianshu.com/p/ca8381d3e094](http://www.jianshu.com/p/ca8381d3e094) 

当你使用 frida-ps -R 能出现类似下面结果的会继续

```
λ frida-ps -R                                                           
  PID  Name                                                             
-----  ---------------------------------------                          
  272  adbd                                                             
 5262  android.process.acore                                            
  841  android.process.media                                            
  181  bridgemgrd                                                       
 8430  com.android.calendar                                             
 8450  com.android.deskclock                                            
 1867  com.android.gallery3d                                            
  873  com.android.inputmethod.latin                                    
  920  com.android.launcher                                             
 8327  com.android.mms                                                  
  908  com.android.nfc                                                  
  858  com.android.phasebeam                                            
  897  com.android.phone                                                
 1020  com.android.smspush                                              
  718  com.android.systemui                                             
 1049  com.illuminate.texaspoker                                        
 1132  com.illuminate.texaspoker:xg_service_v2                          
 2174  daemonsu:0                                                       
13649  daemonsu:0:13646
```

然后 分别点击 start server 和 spawn application.然后我们在 Execute methon Tab中测试下 contextcustom2 函数

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01054679f8e1ff52d9.jpg)

他会在 Output中输出6768 ，这是16进制编码的字符串（方便调试），解码后为 gh

如果在burp中选中数据右键调用的话就会直接输出 解码后的字符串。

[![](https://p0.ssl.qhimg.com/t01508ce879712aaa93.jpg)](https://p0.ssl.qhimg.com/t01508ce879712aaa93.jpg)

这样 Brida_test 就会被替换为 gh.

上面就是官方脚本的测试。下面我们来调用 Encryption.encrypt 和 Encryption.decrypt。这其实就是frida的使用了，可以参考[官方文档](https://www.frida.re/docs/home/)。一个Tips: **使用全局变量来获取函数的返回值**。

```
var encrypt_data = "";
var decrypt_data = "";
rpc.exports = `{`
    contextcustom1: function(message) `{`
        Java.perform(function () `{`
            var Encryption = Java.use('learn.hacklh.me.MobileSafe.tools.Encryption');
            encrypt_data = stringToHex(Encryption.encrypt("just_test",hexToString(message)));
        `}`);
        return encrypt_data
    `}`,
    contextcustom2: function(message) `{`
        Java.perform(function () `{`
            var Encryption = Java.use('learn.hacklh.me.MobileSafe.tools.Encryption');
            decrypt_data = stringToHex(Encryption.decrypt("just_test",hexToString(message)));
        `}`);
        return decrypt_data
    `}`,
`}`
```

完整代码如下：

```
'use strict';

// 1 - FRIDA EXPORTS


var encrypt_data = "";
var decrypt_data = "";

rpc.exports = `{`
    
    // BE CAREFUL: Do not use uperpcase characters in exported function name (automatically converted lowercase by Pyro)
    
    exportedfunction: function() `{`
    
        // Do stuff...  
        // This functions can be called from custom plugins or from Brida "Execute method" dedicated tab

    `}`,
    
    // Function executed when executed Brida contextual menu option 1.
    // Input is passed from Brida encoded in ASCII HEX and must be returned in ASCII HEX (because Brida will decode the output
    // from ASCII HEX). Use auxiliary functions for the conversions.
    contextcustom1: function(message) `{`
        Java.perform(function () `{`
            var Encryption = Java.use('learn.hacklh.me.MobileSafe.tools.Encryption');
            encrypt_data = stringToHex(Encryption.encrypt("just_test",hexToString(message)));
        `}`);
        return encrypt_data
    `}`,
        // Function executed when executed Brida contextual menu option 2.
    // Input is passed from Brida encoded in ASCII HEX and must be returned in ASCII HEX (because Brida will decode the output
    // from ASCII HEX). Use auxiliary functions for the conversions.
    contextcustom2: function(message) `{`
        Java.perform(function () `{`
            var Encryption = Java.use('learn.hacklh.me.MobileSafe.tools.Encryption');
            decrypt_data = stringToHex(Encryption.decrypt("just_test",hexToString(message)));
        `}`);
        return decrypt_data
    `}`,
    
    // Function executed when executed Brida contextual menu option 3.
    // Input is passed from Brida encoded in ASCII HEX and must be returned in ASCII HEX (because Brida will decode the output
    // from ASCII HEX). Use auxiliary functions for the conversions.
    contextcustom3: function(message) `{`
        return "6768";
    `}`,
    
    // Function executed when executed Brida contextual menu option 4.
    // Input is passed from Brida encoded in ASCII HEX and must be returned in ASCII HEX (because Brida will decode the output
    // from ASCII HEX). Use auxiliary functions for the conversions.
    contextcustom4: function(message) `{`
        return "6768";
    `}`

`}`
// 2 - AUXILIARY FUNCTIONS
// Convert a hex string to a byte array
function hexToBytes(hex) `{`
    for (var bytes = [], c = 0; c &lt; hex.length; c += 2)
    bytes.push(parseInt(hex.substr(c, 2), 16));
    return bytes;
`}`

// Convert a ASCII string to a hex string
function stringToHex(str) `{`
    return str.split("").map(function(c) `{`
        return ("0" + c.charCodeAt(0).toString(16)).slice(-2);
    `}`).join("");  
`}`

// Convert a hex string to a ASCII string
function hexToString(hexStr) `{`
    var hex = hexStr.toString();//force conversion
    var str = '';
    for (var i = 0; i &lt; hex.length; i += 2)
        str += String.fromCharCode(parseInt(hex.substr(i, 2), 16));
    return str;
`}`

// Convert a byte array to a hex string
function bytesToHex(bytes) `{`
    for (var hex = [], i = 0; i &lt; bytes.length; i++) `{`
        hex.push((bytes[i] &gt;&gt;&gt; 4).toString(16));
        hex.push((bytes[i] &amp; 0xF).toString(16));
    `}`
    return hex.join("");
`}`
// 3 - FRIDA HOOKS (if needed)
// Insert here Frida interception methods, if needed 
// (es. Bypass Pinning, save values, etc.)
```



**测试**



首先 选中文本 ，右键调用contextcustom1对文本 使用 key为 just_test，进行AES加密。

[![](https://p5.ssl.qhimg.com/t012244dc613fb9198a.jpg)](https://p5.ssl.qhimg.com/t012244dc613fb9198a.jpg)



得到结果：f5f91a52df876b902054e4dfd94d3341

然后解密

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t015111c323dc1d2dfb.jpg)

成功解密

<br>

**总结**



使用该插件，我们在测试一些加密应用时提供另外一种节省精力的方法，我们可以直接调用应用中的方法，来对数据进行加/解密 ，而不用去逆向对应的方法。这节省了测试人员的精力。
