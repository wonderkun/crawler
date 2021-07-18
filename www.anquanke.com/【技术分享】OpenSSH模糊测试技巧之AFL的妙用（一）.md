
# 【技术分享】OpenSSH模糊测试技巧之AFL的妙用（一）


                                阅读量   
                                **172580**
                            
                        |
                        
                                                                                                                                    ![](./img/85826/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：blogspot.fr
                                <br>原文地址：[http://vegardno.blogspot.fr/2017/03/fuzzing-openssh-daemon-using-afl.html](http://vegardno.blogspot.fr/2017/03/fuzzing-openssh-daemon-using-afl.html)

译文仅供参考，具体内容表达以及含义原文为准

**[![](./img/85826/t015350c1dacc216f25.jpg)](./img/85826/t015350c1dacc216f25.jpg)**



翻译：[阿诺斯基](http://bobao.360.cn/member/contribute?uid=2826612711)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**前言**

[American Fuzzy Lop](http://lcamtuf.coredump.cx/afl/)（AFL）是一个很不错的模糊测试工具。如果你想进阶它的高级用法，你需要做一些额外的设置和调整，但是在大多情况下它的功能只是开箱即用的。

在这篇文章中，我将详细介绍开始使用该工具Fuzz OpenSSH守护进程（sshd）的一些步骤，并给出一些模糊测试技巧，以帮助你更快地获得测试结果。

AFL的主页中已经在其“奖杯案例”页面中显示了4个OpenSSH的Bug;这些都是由HannoBöck发现的，他在模糊测试过程中使用了类似于由Jonathan Foote提出的如何使用AFL模糊测试服务器的方法。

我采取了一个稍微不同的方法，而且我认为这种方法更为简单：不需要拦截系统调用来伪造网络活动，我们只需要将OpenSSH的守护进程运行在“inetd模式”。 inet守护进程在现代Linux发行版上不再被使用，此进程会设置监听的网络套接字，并启动一个新进程来处理每个新传入的网络连接。 之后，inetd会将网络套接字数据作为stdin / stdout传递给目标程序。因此，当sshd以inet模式启动时，它通过stdin / stdout与单个客户端进行通信，这正是我们使用AFL进行模糊测试所需要的。

<br>

**配置和构建AFL**

如果你刚刚开始使用AFL，你可能只需在顶级AFL目录中输入make来编译所有内容，它就可以工作了。但是，我想使用一些更高级的功能，特别是我想编译sshd使用基于LLVM的仪器（这比AFL使用默认情况下“由sed组装转换”稍快）。使用LLVM还允许我们将目标程序的“fork point”从刚刚进入main（）之前移动到任意位置（在AFL中称为“延迟forkserver模式”）;这意味着我们可以跳过OpenSSH中的一些设置操作，最明显的是读/解析配置和加载私钥。

使用LLVM模式的大多数步骤在AFL的llvm_mode / README.llvm中有详细说明。在Ubuntu上，您应该安装clang和llvm软件包，然后从顶层AFL目录运行make -C llvm_mode，这很简单。你应该得到一个称为afl-clang-fast的二进制，这是我们将要用来编译sshd。

<br>

**配置和构建OpenSSH**

由于我用的是Linux，所以我使用的是OpenSSH的“便携式”版本，这样可以很方便地使用git（相对于仍然使用CVS 的OpenBSD版本来说）。从Git克隆到本地

```
git://anongit.mindrot.org/openssh.git
```

运行autoreconf生成configure脚本。下面是我运行的配置脚本：



```
./configure 
    CC="$PWD/afl-2.39b/afl-clang-fast" 
    CFLAGS="-g -O3" 
    --prefix=$PWD/install 
    --with-privsep-path=$PWD/var-empty 
    --with-sandbox=no 
--with-privsep-user=vegard
```

很显然你需要传递afl-clang-fast的正确路径。我还在当前（OpenSSH根目录）目录中创建了两个目录，install和var-empty。这是为了使我们在运行make install命令时不需要root权限（虽然var-empty需要700模式并且所有者为root），并且没有冒着破坏任何系统文件的风险（这将是非常糟糕的事情，因为我们稍后要禁用登陆认证和加密！）。我们有必要运行make install命令，即使我们不从安装目录运行sshd。这是因为运行sshd需要一些私钥，我新建的目录就是sshd寻找私钥的地方。

如果一切顺利，运行make命令后应该会显示AFL的banner信息并作为OpenSSH编译完成的标志。

你可能需要一些额外的库（Ubuntu上的zlib1g-dev和libssl-dev），以便构建成功。

运行make install将sshd安装到install /子目录（再次确认，请不要以root身份运行）。

我们将重建几次OpenSSH，因为我们需要对它应用一些补丁，但这给了你构建的基本要素。我注意到的一个特别坑爹的事情是，当你运行make命令时，OpenSSH并不能检测到源代码的更改（因此你的更改可能实际上不会变成二进制文件）。由于这个坑爹的原因，我习惯了在重新编译任何东西之前总是会运行一次make clean。

<br>

**运行sshd**

当我们可以在AFL下运行sshd之前，我们需要确定如何正确的使用所有的标志和选项来调用它。这是我使用的命令和参数：

```
./sshd -d -e -p 2200 -r -f sshd_config -i
```

下面是每个参数选项的意思：



```
-d“调试模式”。保持fork的守护程序，使它只接受一个单一的连接，并阻止它自己后台运行。所有这些有用的东西，都是我们需要的。
-e该选项会打印日志到stderr而不是syslog;这个选项首先防止了我们的模糊测试实例中的调试消息破坏你的系统日志，并且还提升了打印日志的速度。
-p 2200 要监听的TCP端口号。这在inetd模式（-i）中没有真正使用，但是当我们想要生成我们的第一个输入测试用例时，此选项就很有用。
-r这个选项没有详细的说明文档（或者至少在我的手册页中没有找到），但是你可以在源代码中找到该选项的意思，希望这能解释它的作用：阻止sshd重新执行自身。我认为这是一个安全的功能，因为它允许进程将自己与原始环境隔离。在我们的测试例子中，这个功能使得不必要事情变得复杂和缓慢，所以我们需要通过传递-r参数禁用此功能。
-f sshd_config 使用当前目录中的sshd_config配置文件。此参数只是允许我们以后自己定制配置，而不必重新安装SSH或不确定它真正是从哪个位置加载了配置文件。
-i“Inetd模式”。如前所述，inetd模式将使服务器在stdin / stdout上处理单个连接，这是AFL对SSH进行模糊测试的完美选择（因为它会默认在程序的stdin上编写测试用例）。
```

继续并运行上述命令。它应该会打印出如下结果：



```
$ ./sshd -d -e -p 2200 -r -f sshd_config -i
debug1: sshd version OpenSSH_7.4, OpenSSL 1.0.2g  1 Mar 2016
debug1: private host key #0: ssh-rsa SHA256:f9xyp3dC+9jCajEBOdhjVRAhxp4RU0amQoj0QJAI9J0
debug1: private host key #1: ssh-dss SHA256:sGRlJclqfI2z63JzwjNlHtCmT4D1WkfPmW3Zdof7SGw
debug1: private host key #2: ecdsa-sha2-nistp256 SHA256:02NDjij34MUhDnifUDVESUdJ14jbzkusoerBq1ghS0s
debug1: private host key #3: ssh-ed25519 SHA256:RsHu96ANXZ+Rk3KL8VUu1DBzxwfZAPF9AxhVANkekNE
debug1: setgroups() failed: Operation not permitted
debug1: inetd sockets after dupping: 3, 4
Connection from UNKNOWN port 65535 on UNKNOWN port 65535
SSH-2.0-OpenSSH_7.4
```

如果你在上述命令执行的控制台中键入一些垃圾字符，然后按回车，它可能会给你输出“协议不匹配”的提示，然后退出。 这说明程序已经正常工作了！

<br>

**检测程序崩溃/禁用特权分离模式**

我遇到的第一个障碍是，我看到在我的系统日志中sshd崩溃了，但是AFL并没有及时的检测到程序崩溃：



```
[726976.333225] sshd[29691]: segfault at 0 ip 000055d3f3139890 sp 00007fff21faa268 error 4 in sshd[55d3f30ca000+bf000]
[726984.822798] sshd[29702]: segfault at 4 ip 00007f503b4f3435 sp 00007fff84c05248 error 4 in libc-2.23.so[7f503b3a6000+1bf000]
```

问题是，OpenSSH带有一个“特权分离模式”，它fork了子进程并运行子进程中的大部分代码。如果子进行出现了segfault错误，父进行仍然会正常退出，因此它隐藏了AFL的segfault错误信息（它只是直接的观察父进程的活动）。

在版本7.4和更早的版本中，可以通过在命令行中将“UsePrivilegeSeparation no”添加到sshd_config配置文件或传递-o UsePrivilegeSeaparation = no来轻松的禁用特权分离模式。

不幸的是，看起来OpenSSH的开发人员正在删除版本7.5及更高版本中“禁用权限分离模式”的功能。这不是什么大问题，OpenSSH的维护者Damien Miller在Twitter上写道：“基础设施（译者注：他指的是源代码）就在那里，只需要改变一行代码就可以关闭权限分离模式。所以你可能需要潜入到sshd.c文件中以便在将来禁用掉权限分离模式。

<br>

**减少随机性**

OpenSSH在握手期间使用了随机串，以防止“重放攻击”，在此过程中你可以记录某人的（加密的）SSH会话数据，然后你需要再次将相同的数据提供给服务器以便再次进行身份验证。当使用随机串时，服务器和客户端将计算一组新的密钥，从而阻止了重放攻击。

在我们的模糊测试例子中，我们明确想要能够重放流量并连续两次获得相同的结果;否则，模糊器将不能从单个连接尝试中获得任何有用的数据（因为它发现的测试用例不能用于进一步的模糊测试）。

还有一种可能性，即随机性在与握手无关的其他代码路径中引入了可变性，但我并不知道。在任何情况下，我们可以轻松的禁用随机串生成器。在我的系统上，注意configure那一行上面的代码，所有或大多数随机串似乎都来自于openbsd-compat / arc4random.c中的arc4random_buf()函数，所以为了使随机串可预测，我们可以应用下面这个补丁：



```
diff --git openbsd-compat/arc4random.c openbsd-compat/arc4random.c
--- openbsd-compat/arc4random.c
+++ openbsd-compat/arc4random.c
@@ -242,7 +242,7 @@ void
 arc4random_buf(void *buf, size_t n)
 {
        _ARC4_LOCK();
-       _rs_random_buf(buf, n);
+       memset(buf, 0, n);
        _ARC4_UNLOCK();
 }
 # endif /* !HAVE_ARC4RANDOM_BUF */
```

测试这个补丁是否有效的一种方法是尝试捕获SSH会话的数据包，并查看它是否可以成功重放。为了创建我们的第一个输入测试用例，我们将不得不这样做，所以如果你想看看具体如何操作，请跳过下面的内容。在任何情况下，AFL也会告诉我们使用其“稳定性”指标来判断关于随机串的一些东西是否真正关闭了（&gt; 95％表示稳定性是好的，&lt;90％表示某些东西是关闭的，需要修复）。

<br>

**增加覆盖面**

**禁用消息CRC**

在模糊测试时，我们真的希望尽可能多的禁用校验和的检查，正如Damin Miller在twitter上写道：“fuzz的过程中通常也想要更改其他代码，如忽略MAC（消息认证码）或签名校验失败，以便能做更多的事情。这听起来有点奇怪，但实际上是完全有道理的：在真正的攻击场景中，我们可以修复CRC和其他校验和检查，以匹配程序所期望的结果。

如果我们不禁用校验和（我们不试图解决它们），那么fuzzer的测试进展会变得低效。在校验和保护区域中的单比特翻转中将仅使得校验和测试失败，并且不允许fuzzer继续进行下去。

我们当然可以在将数据传递到SSH服务器之前修复校验和，但是这种做法比较缓慢，复杂。最好在服务器中禁用校验和测试，然后尝试修复它，如果我们发现一个可能会导致已修改的服务器崩溃的测试用例。

我们可以禁用的第一个是数据包的CRC测试：



```
diff --git a/packet.c b/packet.c
--- a/packet.c
+++ b/packet.c
@@ -1635,7 +1635,7 @@ ssh_packet_read_poll1(struct ssh *ssh, u_char *typep)
        cp = sshbuf_ptr(state-&gt;incoming_packet) + len - 4;
        stored_checksum = PEEK_U32(cp);
-       if (checksum != stored_checksum) {
+       if (0 &amp;&amp; checksum != stored_checksum) {
                error("Corrupted check bytes on input");
                if ((r = sshpkt_disconnect(ssh, "connection corrupted")) != 0 ||
                    (r = ssh_packet_write_wait(ssh)) != 0)
```

据我所知，这是一个简单的（非加密）完整性检查逻辑，只是作为一个针对比特位翻转或不正确编码的数据的健康检查。

**禁用MAC**

我们还可以禁用消息认证码（MAC），这是一个等效于校验和的加密操作，同样也可以保证消息来自于预期的发送方：



```
diff --git mac.c mac.c 
index 5ba7fae1..ced66fe6 100644 
--- mac.c 
+++ mac.c 
@@ -229,8 +229,10 @@ mac_check(struct sshmac *mac, u_int32_t seqno,         if ((r = mac_compute(mac, seqno, data, dlen,             
ourmac, sizeof(ourmac))) != 0)                 
return r; 
+#if 0         
if (timingsafe_bcmp(ourmac, theirmac, mac-&gt;mac_len) != 0)                 return SSH_ERR_MAC_INVALID; 
+#endif         
return 0;  
}
```

我们在做这些更改时必须非常小心。我们想要尽可能地保持程序代码的原始行为，在某种意义上，我们必须非常小心，不要引入我们自己的错误。例如，我们必须非常确定，我们不会粗心的跳过检查数据包是否足够大的测试，在数据包的第一位会包含校验和。如果我们不小心跳过了这个测试，有可能被模糊测试的程序将尝试访问超过缓冲区结尾的内存，这是原始程序中不存在的错误。

这也是一个不会提交可以导致程序崩溃的测试用例给开发人员的不错的理由，除非你可以证明他们确实也导致了一个完全未经修改的程序崩溃。

**禁用加密**

这是我们可以做的最后一件事，如果你只想对未加密的初始握手协议和密钥交换过程进行模糊测试，那你需要完全禁用加密。

这样做的原因与禁用校验和和MAC的原因是完全一样的，即如果它必须使用加密数据进行工作，则fuzzer将不具有对自身协议进行模糊的能力和希望（因为操作加密数据很大程度上只会导致它被解密为随机或垃圾的数据）。

只需要简单的操作就可以做出改变，因为OpenSSH已经具备了一个伪密码，只是传递数据而实际不会进行加密或解密操作。我们需要做的是使其可用作能够在客户端和服务器之间协商的密码。为此，我们可以使用下面这个补丁：



```
diff --git a/cipher.c b/cipher.c
index 2def333..64cdadf 100644
--- a/cipher.c
+++ b/cipher.c
@@ -95,7 +95,7 @@ static const struct sshcipher ciphers[] = {
 # endif /* OPENSSL_NO_BF */
 #endif /* WITH_SSH1 */
 #ifdef WITH_OPENSSL
-       { "none",       SSH_CIPHER_NONE, 8, 0, 0, 0, 0, 0, EVP_enc_null },
+       { "none",       SSH_CIPHER_SSH2, 8, 0, 0, 0, 0, 0, EVP_enc_null },
        { "3des-cbc",   SSH_CIPHER_SSH2, 8, 24, 0, 0, 0, 1, EVP_des_ede3_cbc },
 # ifndef OPENSSL_NO_BF
        { "blowfish-cbc",
```

要默认使用此密码，只需在你的sshd_config配置文件中添加“Ciphers none”。 当然，客户端并不直接支持这种配置，所以如果你要做任何测试连接，你必须使用上面的cipher.c补丁编译的ssh二进制程序。

如果你喜欢使用不同的默认密码，那么你可能必须从客户端传递 -o Ciphers = none 参数。可以使用strace或wireshark来验证在明文中超出初始协议设置发生的事情。
