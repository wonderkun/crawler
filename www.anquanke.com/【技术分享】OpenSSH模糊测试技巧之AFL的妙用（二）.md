
# 【技术分享】OpenSSH模糊测试技巧之AFL的妙用（二）


                                阅读量   
                                **147005**
                            
                        |
                        
                                                                                                                                    ![](./img/85862/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：vegardno.blogspot.fr
                                <br>原文地址：[http://vegardno.blogspot.fr/2017/03/fuzzing-openssh-daemon-using-afl.html](http://vegardno.blogspot.fr/2017/03/fuzzing-openssh-daemon-using-afl.html)

译文仅供参考，具体内容表达以及含义原文为准

[](http://mailto:http://lcamtuf.coredump.cx/afl/)

[![](./img/85862/t01793b3bf98c2aa980.jpg)](http://p4.qhimg.com/t015350c1dacc216f25.jpg)



翻译：[阿诺斯基](http://bobao.360.cn/member/contribute?uid=2826612711)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**传送门**

[**【技术分享】OpenSSH模糊测试技巧之AFL的妙用（一） **](http://bobao.360.cn/learning/detail/3682.html)



[American Fuzzy Lop](http://mailto:http://lcamtuf.coredump.cx/afl/)（AFL）是一个很不错的模糊测试工具。如果你想进阶它的高级用法，你需要做一些额外的设置和调整，但是在大多情况下它的功能只是开箱即用的。

在这篇文章中，我将详细介绍开始使用OpenSSH守护进程（sshd）的一些步骤，并给出一些模糊测试技巧，以帮助你更快地获得测试结果。

AFL的主页中已经在其“奖杯案例”页面中显示了4个OpenSSH的Bug;这些都是由HannoBöck发现的，他在模糊测试过程中使用了类似于由Jonathan Foote提出的如何使用AFL模糊测试服务器的方法。

我采取了一个稍微不同的方法，而且我认为这种方法更为简单：不需要拦截系统调用来伪造网络活动，我们只需要将OpenSSH的守护进程运行在“inetd模式”。 inet守护进程在现代Linux发行版上不再被使用，此进程会设置监听的网络套接字，并启动一个新进程来处理每个新传入的网络连接。 之后，inetd会将网络套接字数据作为stdin/stdout传递给目标程序。因此，当sshd以inet模式启动时，它通过stdin/stdout与单个客户端进行通信，这正是我们使用AFL进行模糊测试所需要的。

<br>

**加快模糊测试速度**

**afl-clang-fast 或 LLVM的“延迟forkserver模式”**

我上面提到，使用afl-clang-fast（即AFL的LLVM延迟forkserver模式）允许我们移动“fork point”来跳过一些sshd初始化的步骤，这对于我们抛出的每个单一测试用例都是相同的。

为了长久的进行模糊测试，我们需要在程序的正确的位置中调用__AFL_INIT()函数，将那些不依赖于特定输入的东西放到这个函数之前，并将测试用例特定的处理过程放在这个函数之后。我使用了下面这个补丁：



```
diff --git a/sshd.c b/sshd.c
--- a/sshd.c
+++ b/sshd.c
@@ -1840,6 +1840,8 @@ main(int ac, char **av)
        /* ignore SIGPIPE */
        signal(SIGPIPE, SIG_IGN);
+       __AFL_INIT();
+
        /* Get a connection, either from inetd or a listening TCP socket */
        if (inetd_flag) {
                server_accept_inetd(&amp;sock_in, &amp;sock_out);
```

AFL应该能够自动检测到你不再希望每次都从main()函数的顶部开始执行程序。然而，只做了上面的那个补丁后，我得到下面这个可怕的错误消息：

嗯，看起来在我们可以与注入的代码完成握手之前，要处理的二进制程序就终止掉了。也许模糊器还有一个比较可怕的bug需要处理。 Poke &lt;lcamtuf@coredump.cx&gt;用于故障排除提示。

所以，显然在这里有一些AFL魔术代码使fuzzer和被模糊测试的程序进行通信。在afl-fuzz.c中查看了一下后，我发现了FORKSRV_FD，它是一个文件描述符，用于指向此目标的管道。其值为198（管道的另一端为199）。

为了试图弄清楚出了什么问题，我在strace下运行了afl-fuzz，它显示文件描述符198和199被sshd关闭了。在挖掘了更多的信息后，我发现了closefrom（）函数的调用，这是一个关闭开始时给定的数字的所有继承（和假设未使用过的）的文件描述符的函数。不过，这种代码处在程序的起始位置的原因可能是为了减少攻击面，以防止攻击者能够控制进程。但无论如何，保护这些特殊的文件描述符的解决方案应该是使用如下这样的补丁：



```
diff --git openbsd-compat/bsd-closefrom.c openbsd-compat/bsd-closefrom.c
--- openbsd-compat/bsd-closefrom.c
+++ openbsd-compat/bsd-closefrom.c
@@ -81,7 +81,7 @@ closefrom(int lowfd)
        while ((dent = readdir(dirp)) != NULL) {
            fd = strtol(dent-&gt;d_name, &amp;endp, 10);
            if (dent-&gt;d_name != endp &amp;&amp; *endp == '' &amp;&amp;
-               fd &gt;= 0 &amp;&amp; fd &lt; INT_MAX &amp;&amp; fd &gt;= lowfd &amp;&amp; fd != dirfd(dirp))
+               fd &gt;= 0 &amp;&amp; fd &lt; INT_MAX &amp;&amp; fd &gt;= lowfd &amp;&amp; fd != dirfd(dirp) &amp;&amp; fd != 198 &amp;&amp; fd != 199)
                (void) close((int) fd);
        }
        (void) closedir(dirp);
```

**跳过高大上的DH /曲线计算和密钥导出操作**

在这一点上来说，我仍然不满意fuzzer的执行速度：有些测试程序低至10 exec /秒，确实很慢。

我试图使用 -pg（gprof）编译sshd并尝试找出耗时的原因，但是要让它正确的工作会遇到很多麻烦：首先，sshd通过cleanup_exit()函数使用_exit(255)退出。这不是一个“正常”的退出，所以gmon.out文件（包含配置文件数据）根本就没有写如数据。可以应用一个源补丁来修复它，但是sshd会抛给你一个“拒绝访问”的错误，因为它试图打开该文件进行写入。现在的问题是sshd有一个chdir("/")，这意味着它试图将配置文件数据写入无法访问的目录。解决方案很简单，只需在调用exit()之前将另一个chdir()添加到可写的位置。即使这样，这个配置文件对我来说也完全是空的。也许这是另一个特权分离的事情。在任何情况下，我决定只使用valgrind及其“cachegrind”工具来获取配置文件。使用这种方式更容易一些，拿到我所需要的数据，而无需遇到重新配置，修补和重新编译的麻烦。

该配置文件显示了一个非常特殊的热点，来自两个不同的位置：椭圆曲线点乘法。

我真的不太了解椭圆曲线加密，但显然，这种计算看起来相当“高大上”。但是，我们真的不需要处理它;我们可以假设服务器和客户端之间的密钥交换成功。类似于我们如何通过跳过消息CRC检查和用伪密码替换加密来增加覆盖面，我们可以简单地跳过“高大上”的操作并假设它们总是成功的。这是一个折衷的方案;我们不再模糊测试所有的验证步骤，但允许模糊测试器更专注于协议解析本身。我应用了如下这个补丁：



```
diff --git kexc25519.c kexc25519.c
--- kexc25519.c
+++ kexc25519.c
@@ -68,10 +68,13 @@ kexc25519_shared_key(const u_char key[CURVE25519_SIZE],
        /* Check for all-zero public key */
        explicit_bzero(shared_key, CURVE25519_SIZE);
+#if 0
        if (timingsafe_bcmp(pub, shared_key, CURVE25519_SIZE) == 0)
                return SSH_ERR_KEY_INVALID_EC_VALUE;
        crypto_scalarmult_curve25519(shared_key, key, pub);
+#endif
+
 #ifdef DEBUG_KEXECDH
        dump_digest("shared secret", shared_key, CURVE25519_SIZE);
 #endif
diff --git kexc25519s.c kexc25519s.c
--- kexc25519s.c
+++ kexc25519s.c
@@ -67,7 +67,12 @@ input_kex_c25519_init(int type, u_int32_t seq, void *ctxt)
        int r;
        /* generate private key */
+#if 0
        kexc25519_keygen(server_key, server_pubkey);
+#else
+       explicit_bzero(server_key, sizeof(server_key));
+       explicit_bzero(server_pubkey, sizeof(server_pubkey));
+#endif
 #ifdef DEBUG_KEXECDH
        dump_digest("server private key:", server_key, sizeof(server_key));
 #endif
```

有了这个补丁，每秒的执行速度可以达到每个核心2,000，这是一个来进行模糊测试非常好的运行速度。

（编辑于2017-03-25：事实证明，这个补丁并不是很好，因为它导致稍后的密钥有效性检查失败（在input_kex_dh_init()中的dh_pub_is_valid()）。 我们可能让dh_pub_is_valid()函数总是返回了true，但是问题来了，反过来返回false又会使别的事情失败。）

<br>

**创建第一个输入测试用例**

在我们开始模糊测试之前，我们必须创建几个输入测试用例。 实际上，一个测试用例的就足以开始工作了，但如果你知道如何在服务器上用不同的代码路径创建不同的测试用例，这可能有助于启动模糊测试进程。 我可以想到以下几种可能：

ssh -A用于ssh代理转发

ssh -R启用任意端口转发

ssh -Y启用X11转发

scp传输文件

使用密码对比.pubkey的身份验证

我创建第一个测试用例的方式是使用strace记录从客户端到服务器的流量。 启动不带-i参数的服务器：



```
./sshd -d -e -p 2200 -r -f sshd_config
[...]
Server listening on :: port 2200.
```

然后在strace下启动一个客户端（使用刚刚编译的ssh二进制文件）：

```
$ strace -e trace=write -o strace.log -f -s 8192 ./ssh -c none -p 2200 localhost
```

执行后，应该会提示你进行登录（如果没有，你可能必须使用用户，密钥和密码，直到你成功登录到你刚刚启动的服务器）。

strace日志的前几行应该看起来像这样：



```
2945  write(3, "SSH-2.0-OpenSSH_7.4rn", 21) = 21
2945  write(3, "4|524010curve25519-sha256,curve25519-sha256@libssh.org,ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521,diffie-hellman-group-exchange-sha256,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512,diffie-hellman-group-exchange-sha1,diffie-hellman-group14-sha256,diffie-hellman-group14-sha1,ext-info-c1"ecdsa-sha2-nistp256-cert-v01@openssh.com,ecdsa-sha2-nistp384-cert-v01@openssh.com,ecdsa-sha2-nistp521-cert-v01@openssh.com,ecdsa-sha2-nistp256,ecdsa-sha2-nistp384,ecdsa-sha2-nistp521,ssh-ed25519-cert-v01@openssh.com,ssh-rsa-cert-v01@openssh.com,ssh-ed25519,rsa-sha2-512,rsa-sha2-256,ssh-rsa4none4none325umac-64-etm@openssh.com,umac-128-etm@openssh.com,hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com,hmac-sha1-etm@openssh.com,umac-64@openssh.com,umac-128@openssh.com,hmac-sha2-256,hmac-sha2-512,hmac-sha1325umac-64-etm@openssh.com,umac-128-etm@openssh.com,hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com,hmac-sha1-etm@openssh.com,umac-64@openssh.com,umac-128@openssh.com,hmac-sha2-256,hmac-sha2-512,hmac-sha132none,zlib@openssh.com,zlib32none,zlib@openssh.com,zlib", 1152) = 1152
```

我们在这里看到客户端正通过文件描述符3进行通信。你将必须删除在其他文件描述符上发生的所有写入操作。然后将这些字符串粘贴到Python脚本中，如：



```
import sys
for x in [
    "SSH-2.0-OpenSSH_7.4rn"
    "4..."
    ...
]:
sys.stdout.write(x)
```

当你运行这个脚本后，它会完美的打印出客户端发送到stdout的每一个字节。 只需将它重定向到一个文件。 该文件将是你的第一个输入测试用例。

你可以通过将相同的数据再次传递到服务器来执行测试运行（不使用AFL）（这次使用-i）：

```
./sshd -d -e -p 2200 -r -f sshd_config -i &lt; testcase 2&gt;&amp;1 &gt; /dev/null
```

希望它将显示你的测试用例重放能够成功的进行登录。

在启动模糊测试器之前，你还可以使用afl-analyze来仔细检查sshd是否正常工作：

```
~/afl-2.39b/afl-analyze -i testcase -- ./sshd -d -e -p 2200 -r -f sshd_config –i
```

运行此命令可能需要几秒钟的时间，但最终应该会显示一个文件的映射和每个字节的意思。 如果有太多的红色，那么者意味着你不能禁用校验和/加密（也许你必须要clean和重建一次？）。 你可能还会看到其他错误，包括AFL没有检测到任何工具（你是否使用afl-clang-fast编译了sshd？）。 这是一般性的AFL故障排除，所以我建议你检查AFL的文档。

<br>

**创建OpenSSH字典**

我为OpenSSH创建了一个AFL“字典”，它基本上只是一个字符串列表，对程序进行模糊测测试处理有特殊的意义。 我只是通过运行ssh -Q密码找到了这些字符串，允许模糊测试器使用这些字符串，而不必一次就找到它们（这是不可能发生的机会）。



```
s0="3des-cbc"
s1="aes128-cbc"
s2="aes128-ctr"
s3="aes128-gcm@openssh.com"
s4="aes192-cbc"
s5="aes192-ctr"
s6="aes256-cbc"
s7="aes256-ctr"
s8="aes256-gcm@openssh.com"
s9="arcfour"
s10="arcfour128"
s11="arcfour256"
s12="blowfish-cbc"
s13="cast128-cbc"
s14="chacha20-poly1305@openssh.com"
s15="curve25519-sha256@libssh.org"
s16="diffie-hellman-group14-sha1"
s17="diffie-hellman-group1-sha1"
s18="diffie-hellman-group-exchange-sha1"
s19="diffie-hellman-group-exchange-sha256"
s20="ecdh-sha2-nistp256"
s21="ecdh-sha2-nistp384"
s22="ecdh-sha2-nistp521"
s23="ecdsa-sha2-nistp256"
s24="ecdsa-sha2-nistp256-cert-v01@openssh.com"
s25="ecdsa-sha2-nistp384"
s26="ecdsa-sha2-nistp384-cert-v01@openssh.com"
s27="ecdsa-sha2-nistp521"
s28="ecdsa-sha2-nistp521-cert-v01@openssh.com"
s29="hmac-md5"
s30="hmac-md5-96"
s31="hmac-md5-96-etm@openssh.com"
s32="hmac-md5-etm@openssh.com"
s33="hmac-ripemd160"
s34="hmac-ripemd160-etm@openssh.com"
s35="hmac-ripemd160@openssh.com"
s36="hmac-sha1"
s37="hmac-sha1-96"
s38="hmac-sha1-96-etm@openssh.com"
s39="hmac-sha1-etm@openssh.com"
s40="hmac-sha2-256"
s41="hmac-sha2-256-etm@openssh.com"
s42="hmac-sha2-512"
s43="hmac-sha2-512-etm@openssh.com"
s44="rijndael-cbc@lysator.liu.se"
s45="ssh-dss"
s46="ssh-dss-cert-v01@openssh.com"
s47="ssh-ed25519"
s48="ssh-ed25519-cert-v01@openssh.com"
s49="ssh-rsa"
s50="ssh-rsa-cert-v01@openssh.com"
s51="umac-128-etm@openssh.com"
s52="umac-128@openssh.com"
s53="umac-64-etm@openssh.com"
s54="umac-64@openssh.com"
```

将这些字符串保存为openssh.dict; 并使用-x选项将文件名传递给afl-fuzz。

<br>

**运行AFL**

哇，终于是开始进行模糊测试的时候了！

首先，创建两个目录，输入和输出。 将初始测试用例放在输入目录中。 然后，对于输出目录，我们将使用一些加快模糊测试过程，并保持AFL持续输出的技巧：在输出文件夹中挂载一个tmpfs RAM磁盘：

```
sudo mount -t tmpfs none output/
```

当然，如果你关机（或系统崩溃）而你没有将数据复制出这个目录，那它会消失，所以你应该每隔一段时间就做一次备份。 我个人只是使用一个bash单线程脚本每隔几个小时就把数据复制到真正的磁盘文件系统。

要启动单个fuzzer，你可以使用下面的命令：

```
~/afl-2.39b/afl-fuzz -x sshd.dict -i input -o output -M 0 -- ./sshd -d -e -p 2100 -r -f sshd_config -i
```

再次提醒，请参阅AFL的文档查看如何做并行的fuzzing。 这里我只是有一个简单的bash脚本，在不同的终端窗口中启动了而已（-M或-S选项的值不同）。

希望你执行后应该看到如下的内容：

[![](./img/85862/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01cbf482e937f8e2f7.png)

<br>

**发现崩溃**

在大约一天的模糊测试（即使在禁用加密之前）中，我在密钥交换期间发现了两个NULL指针间接引用。幸运的是，这些崩溃在实践中没有害处，因为OpenSSH有特权分离代码，所以我们最多会崩溃一个没有特权的子进程，并在系统日志中留下一个可怕的segfault消息。在CVS中的修复的方法在这：

[http://cvsweb.openbsd.org/cgi-bin/cvsweb/src/usr.bin/ssh/kex.c?rev=1.131&amp;content-type=text/x-cvsweb-markup](http://cvsweb.openbsd.org/cgi-bin/cvsweb/src/usr.bin/ssh/kex.c?rev=1.131&amp;content-type=text/x-cvsweb-markup)  。

<br>

**结论**

除了两个无害的NULL指针间接引用外，还没有发现别的问题，这似乎表明OpenSSH是相当鲁棒的（这很好！）。

我希望我在本文里所使用的一些技术和补丁能帮助更多的人一起进行OpenSSH的模糊测试。

这里做的其他事情包括使用ASAN或通过valgrind运行语料库做一些模糊测试，一旦你已经有一个大小不错的语料库，可能不使用这两个工具会更容易一些，因为ASAN和valgrind在性能上略差。

看看./configure选项也是非常有用的，配置的构建更像一个典型的发行版的构建;我没有做任何事情，除非让它在最小的环境中构建。

关于如何扩大覆盖面或使OpenSSH的模糊测试跑，如果你有其他想法的更快可以在评论区告诉我！

<br>

**致谢**

我想感谢Oracle（我的雇主）提供了硬件让我并行运行大量的AFL实例:-)

<br>



**传送门**

[**【技术分享】OpenSSH模糊测试技巧之AFL的妙用（一） **](http://bobao.360.cn/learning/detail/3682.html)

<br>
