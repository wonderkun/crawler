> 原文链接: https://www.anquanke.com//post/id/230082 


# 使用动静结合的分析方式检测供应链攻击中的0 day


                                阅读量   
                                **141464**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者ajinabraham，文章来源：ajinabraham.com
                                <br>原文地址：[https://ajinabraham.com/blog/detecting-zero-days-in-software-supply-chain-with-static-and-dynamic-analysis﻿](https://ajinabraham.com/blog/detecting-zero-days-in-software-supply-chain-with-static-and-dynamic-analysis%EF%BB%BF)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t015e878453e7e6d3e8.jpg)](https://p5.ssl.qhimg.com/t015e878453e7e6d3e8.jpg)



## 写在前面的话

在这篇文章中，我们将跟大家分享一些关于如何在软件供应链中检测0 day漏洞的想法，我们的方法可以在这些0 day漏洞被常见软件分析分析（SCA）或依赖检查工具标记之前发现它们。除此之外，我们还会跟大家分享基于静态分析和动态分析技术来检测恶意行为的PoC概念验证代码。我们的PoC可以在恶意组件在CI/CD管道中构建之前，使用对第三方依赖项的静态和动态分析技术检测到恶意行为。



## 技术背景

最近SolarWinds的“悲剧”向我们展示了拥有成熟可靠安全程序的科技巨头是如何成为软件供应链攻击的目标的。供应链攻击的范围很广，但我将重点讨论涉及代码和数据的应用程序安全方面。随着DevOps的成熟，我们看到许多代码都是从CI/CD解决方案中自动构建和发布的，这些解决方案包括内部部署和SaaS。我们现在大部分的工作都放在保护运行这些代码的生产系统上，但或多或少地忽略了构建系统的重要性，有的时候我们甚至还会把责任推给服务提供商。在构建管道中，我们使用了能够执行软件组成分析（SCA）或依赖检测的安全工具来检测过期的、废弃的和已知存在漏洞的软件包。在OWASP中还有一个专门针对此类漏洞的分类，即A9:2017-使用包含已知漏洞的组件。

但是，那些包含未知漏洞的软件包呢？那些最近被植入后门的软件包呢？或者那些包含0 day漏洞的软件包呢？目前绝大多数的工具都是通过检测软件包，并跟保存了已知漏洞的数据库数据进行对比，这样一来，我们的安全性将取决于数据库的更新程度。对于0 day漏洞来说，由于有些数据库是在信息公开后才更新的，那么这种方式对于防御这种安全风险来说就已经太晚了。在这篇文章中，我们将讨论如何在第三方依赖或恶意软件包中主动检测此前未知的恶意行为的方法。



## CI/CD管道中的恶意包

构建系统通常是在构建、部署或发布资产的过程中动态创建和销毁的。当构建系统尝试去设置/安装一个由攻击者控制的恶意软件包时，攻击者便有机可乘了。

如果在构建过程中不小心安装了恶意软件包，那么攻击者就可以在构建系统的上下文中执行以下某些活动：

1、窃取代码和任何硬编码的敏感数据。<br>
2、在将代码部署到生产环境后使用已在代码中植入的后门。<br>
3、窃取CPU、RAM等计算资源，用于加密货币挖矿等活动。<br>
4、窃取环境变量、敏感文件、凭据、证书等。<br>
5、使用收集的数据执行横向移动/渗透和权限提升。

由于我们无法在这一篇文章中涵盖所有的相关内容，因此在这里我将主要讨论环境变量方面的东西。下面给出的代码仅供PoC概念验证参考，暂时还不适用于真实的生产场景。

窃取环境变量

这里讨论的思想适用于跨平台的不同编程语言，但是共享的示例将主要针对Python包。我创建了一个名为【poc-rogue】的恶意Python包，当用户尝试安装这个恶意包时，它将尝试各种方法来窃取环境变量并将数据发送到localhost:1337。接下来，我们一起看看这个Python程序使用了哪些方法来获取环境变量。

使用Python API-os.environ：

`return os.environ`

运行env命令：

`subprocess.check_output(['env'])`

运行shell的内置set命令：

`subprocess.check_output(['sh', '-c', 'set'])`

从proc psudo文件系统读取environ（/proc/&lt;pid&gt;/environ）：

<code>loc = Path('/proc') / str(os.getpid()) / 'environ'<br>
return loc.read_text()</code>

读取可能包含环境变量的文件：

<code>data = []<br>
commons = `{`<br>
'/etc/environment', '/etc/profile', '/etc/bashrc',<br>
'~/.bash_profile', '~/.bashrc', '~/.profile',<br>
'~/.cshrc', '~/.zshrc', '~/.tcshrc',<br>
`}`<br>
for i in commons:<br>
env = Path(i).expanduser().read_text()<br>
data.append(env)</code>

从libc.so共享库中访问environ指针：

<code>libc = ctypes.CDLL(None)<br>
environ = ctypes.POINTER(ctypes.c_char_p).in_dll(libc, 'environ')</code>

这些是访问环境变量的一些常用方法。也有其他可用的方法，但为了简单起见，我们使用这些方法来进行演示。



## 使用静态分析检测恶意Python包

现在，我们将使用静态分析技术来检测恶意软件包。我们将使用semgrep进行静态分析，这里使用的所有代码都可以在【package_scan代码库】中找到。下面给出的是检测环境变量访问的semgrep静态分析规则：

```
rules:
  - id: env-set
    patterns:
      - pattern-either:
          - pattern: |
              subprocess.check_output([..., "=~/env|set/", ...])
          - pattern: |
              subprocess.run([..., "=~/env|set/", ...])
          - pattern: |
              subprocess.Popen([..., "=~/env|set/", ...])
    message: |
      Reading from env or set commands
    severity: ERROR
    languages:
      - python
  - id: python-os-environ
    patterns:
      - pattern-not-inside: os.environ.get(...)
      - pattern-not-inside: os.environ[...]
      - pattern-either:
          - pattern: |
              os.environ
    message: |
      Reading from python's os.environ()
    severity: ERROR
    languages:
      - python
  - id: python-proc-fs
    patterns:
      - pattern-either:
          - pattern: |
              pathlib.Path('/proc') / ... / 'environ'
    message: |
      Reading python /proc/&lt;pid&gt;/environ
    severity: ERROR
    languages:
      - python
  - id: environ-files
    patterns:
      - pattern-inside: |
          $X = `{`..., "=~/\/etc\/environment|\/etc\/profile|\/etc\/bashrc|~\/.bash_profile|~\/.bashrc|~\/.profile|~\/.cshrc|~\/.zshrc|~\/.tcshrc/", ...`}`
          ...
      - pattern-either:
          - pattern: |
              Path(...)
          - pattern: |
              open(...)
    message: |
      Reading from sensitve files that contain environment variables
    severity: ERROR
    languages:
      - python
  - id: libc-environ
    patterns:
      - pattern-either:
          - pattern: |
              $LIB = ctypes.CDLL(...)
              ...
              $Y.in_dll($LIB, 'environ')
    message: |
      Reading from libc.environ
    severity: ERROR
    languages:
      - python
```

Semgrep规则语法非常容易理解，因为它使用编程语言的语法来定义规则。为了更好地理解semgrep语法，请参考https://semgrep.dev/docs/。package_scan库提供了一个requirements.txt文件，其中定义了我们需要进行静态分析的软件包。

```
rsa&gt;=4.7
biplist&gt;=1.0.3
bs4&gt;=0.0.1
colorlog&gt;=4.7.2
shelljob&gt;=0.6
-e git://github.com/ajinabraham/poc-rogue.git#egg=rogue
```

除了其他Python包，我们的poc-rogue包也在这个列表之中。接下来，我们将使用static_analysis.py这个Python脚本来执行静态分析：

[![](https://p3.ssl.qhimg.com/t0130edb1a36bcb92af.png)](https://p3.ssl.qhimg.com/t0130edb1a36bcb92af.png)

很好，我们只看到了我们poc-rogue包中被标记的问题。这个Python脚本将会下载requirements.txt中定义的所有依赖以及子依赖，并使用我们提供的规则集对代码运行semgrep。静态分析可以帮助我们轻松地检测比较明显的安全问题，但是静态分析在处理经过模糊处理的代码时有其局限性，而且也有不同的代码和API组合来实现相同的逻辑。因此，如果想要针对所有情况来编写检测规则的话，可行性不高，而且也不适用于大规模分析的场景。因此，我们还需要使用到动态分析来更准确地实现我们的检测目标。



## 使用动态分析检测恶意软件包

针对动态分析，我们可以使用syscall（系统调用），因为它们在底层工作，并且与Python和Node.js之类的高级编程语言无关。有多种方法可以跟踪系统调用，比如使用扩展的Berkeley包过滤器（eBPF）探测、使用seccomp bpf过滤器（使用BPF）、使用ptrace API等。为了演示方便，我们使用strace实用工具和—seccomp-bpf选项来收集系统调用和ptrace API来深入检查执行参数。接下来，让我们试着理解系统调用如何帮助我们进行动态分析。如果我们深入分析过恶意代码的话，我们会看到其中有的代码会生成系统调用。

### 执行命令

下面的恶意代码可以执行特定的命令来收集环境变量：

<code>$ strace -f -e trace=execve -o strace python -c 'import subprocess;subprocess.call(["env"])'<br>
$ cat strace<br>
431765 execve("/home/ajin/package_scan/venv/bin/python", ["python", "-c", "import subprocess;subprocess.cal"...], 0x7ffee0ac8c48 /* 28 vars */) = 0<br>
431766 execve("/home/ajin/package_scan/venv/bin/env", ["env"], 0x7fff8fa0b308 /* 28 vars */) = -1 ENOENT (No such file or directory)<br>
431766 execve("/home/ajin/.local/bin/env", ["env"], 0x7fff8fa0b308 /* 28 vars */) = -1 ENOENT (No such file or directory)<br>
431766 execve("/usr/local/sbin/env", ["env"], 0x7fff8fa0b308 /* 28 vars */) = -1 ENOENT (No such file or directory)<br>
431766 execve("/usr/local/bin/env", ["env"], 0x7fff8fa0b308 /* 28 vars */) = -1 ENOENT (No such file or directory)<br>
431766 execve("/usr/sbin/env", ["env"], 0x7fff8fa0b308 /* 28 vars */) = -1 ENOENT (No such file or directory)<br>
431766 execve("/usr/bin/env", ["env"], 0x7fff8fa0b308 /* 28 vars */) = 0<br>
431766 +++ exited with 0 +++<br>
431765 --- SIGCHLD `{`si_signo=SIGCHLD, si_code=CLD_EXITED, si_pid=431766, si_uid=1000, si_status=0, si_utime=0, si_stime=0`}` ---<br>
431765 +++ exited with 0 +++</code>

我稍后会解释strace参数，但现在，无论我们使用那个Python API来执行命令，它最终都会涉及到execve()。

### <a class="reference-link" name="%E6%89%93%E5%BC%80%E6%96%87%E4%BB%B6"></a>打开文件

读取包含环境变量的敏感文件：

<code>strace -f -e trace=open,openat -o strace python -c 'from pathlib import Path; Path("~/.bashrc").expanduser().read_text()'<br>
$ cat strace | grep bashrc<br>
432709 openat(AT_FDCWD, "/home/ajin/.bashrc", O_RDONLY|O_CLOEXEC) = 3</code>

任何通过标准Python API实现文件打开的操作都是由内核中的系统调用openat()或open()处理的。

### <a class="reference-link" name="%E7%BD%91%E7%BB%9C%E8%BF%9E%E6%8E%A5"></a>网络连接

另一个使用系统调用的例子就是识别攻击者用于提取数据的出站网络连接：

<code>$ strace -f -e trace=connect -o strace python -c 'import urllib.request;urllib.request.urlopen("http://python.org/")'<br>
$ cat strace | grep 'htons(80)'<br>
435764 connect(3, `{`sa_family=AF_INET, sin_port=htons(80), sin_addr=inet_addr("45.55.99.72")`}`, 16) = 0</code>

上面的代码会连接到python.org，并且使用了connect()系统调用。

### <a class="reference-link" name="%E5%AE%9E%E7%8E%B0%E5%8A%A8%E6%80%81%E5%88%86%E6%9E%90"></a>实现动态分析

这样一来，我们就可以使用strace捕获安装包时所使用的所有敏感系统调用，并查找对应于恶意行为的模式。对于动态分析，我们可以使用strace命令：

`strace -s 2000 -fqqe trace=openat,execve,connect --seccomp-bpf &lt;cmd&gt;`

这里的&lt;cmd&gt;可以是pip install &lt;package_name&gt;、npm install &lt;pkg_name&gt;，或任何其他能够执行软件包安装的命令。

此时，我们可以执行dynamic_analysis.py这个Python脚本对requirments.txt file中提到的软件包执行动态分析。请注意，我们在安装包时和实际使用包之前执行动态分析。在本地运行这个PoC脚本是没问题的，但如果在现实场景中执行动态分析的话，最好是在一台隔离环境下的虚拟机系统中进行操作。

[![](https://p4.ssl.qhimg.com/t01c859a71fffddf51b.png)](https://p4.ssl.qhimg.com/t01c859a71fffddf51b.png)

我们可以看到，我们的poc-rogue包在安装过程中执行了某些恶意操作，并且使用strace和动态分析技术检测到了这种行为。



## 总结

我们需要在构建系统中实施适当的安全控制和流程，就像我们在生产环境中所做的那样。这些自动构建系统中可用的凭据没有启用双因素身份验证，使它们成为攻击者有利可图的目标。大多数真实世界的攻击并不总是复杂的，而是一些简单的黑客攻击，目标是您环境中最薄弱的环节。
