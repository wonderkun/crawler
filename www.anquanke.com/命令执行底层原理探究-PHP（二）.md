> 原文链接: https://www.anquanke.com//post/id/226293 


# 命令执行底层原理探究-PHP（二）


                                阅读量   
                                **263256**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01065e3f9c22565868.jpg)](https://p4.ssl.qhimg.com/t01065e3f9c22565868.jpg)



## 前言

针对不同平台/语言下的命令执行是不相同的，存在很大的差异性。因此，这里对不同平台/语言下的命令执行函数进行深入的探究分析。

文章开头会对不同平台(Linux、Windows)下：终端的指令执行、语言(PHP、Java、Python)的命令执行进行介绍分析。后面，主要以PHP语言为对象，针对不同平台，对命令执行函数进行底层深入分析，这个过程包括：环境准备、PHP内核源码的编译、运行、调试、审计等，其它语言分析原理思路类似。

该系列分析文章主要分为四部分，如下：
- 第一部分：命令执行底层原理探究-PHP (一)
针对不同平台(Linux、Windows)下：终端的指令执行、语言(PHP、Java、Python)的命令执行进行介绍分析。
- 第二部分：命令执行底层原理探究-PHP (二)
主要以PHP语言为对象，针对不同平台，进行环境准备、PHP内核源码的编译、运行、调试等。
- 第三部分：命令执行底层原理探究-PHP (三)
针对Windows平台下，PHP命令执行函数的底层原理分析。
- 第四部分：命令执行底层原理探究-PHP (四)
针对Linux平台下，PHP命令执行函数的底层原理分析。

本文**《 命令执行底层原理探究-PHP (二) 》**主要讲述的是第二部分：以PHP语言为对象，针对不同平台，进行环境准备、PHP内核源码的编译、运行、调试等。



## PHP for Windows

针对Windows平台下：环境准备、PHP内核源码的编译、运行、调试等。

### <a class="reference-link" name="%E7%8E%AF%E5%A2%83%E5%87%86%E5%A4%87"></a>环境准备

环境部署情况：
- Windows (Win10 Pro)
- Visual Studio (Visual Studio Professional 2019)
- Visual Studio Code (VSCode-win32-x64-1.51.1)
- PHP Source Code (PHP 7.2.9)
- PHP Windows SDK (php-sdk-binary-tools-php-sdk-2.2.0)
- Source Insight (Source Insight 4.0)
[php官方wiki](https://wiki.php.net/internals/windows/stepbystepbuild_sdk_2)对不同php版本编译的需求如下：
- Visual C++ 14.0 (Visual Studio 2015) for **PHP 7.0** or **PHP 7.1**.
- Visual C++ 15.0 (Visual Studio 2017) for **PHP 7.2**, **PHP 7.3** or **PHP 7.4**.
- Visual C++ 16.0 (Visual Studio 2019) for **master**.
虽然官方wiki指出不同VS编译不同PHP版本，但是这里使用VS2019去编译`PHP 7.2.9`是没有问题的（兼容性）。

#### <a class="reference-link" name="Visual%20Studio"></a>Visual Studio

> Visual Studio 面向任何开发者的同类最佳工具，功能完备的 IDE，可用于编码、调试、测试和部署到任何平台。

`Visual Studio` 官网：介绍、下载

```
# 下载官网最新版 VS2019

https://visualstudio.microsoft.com/zh-hans/
```

`Visual Studio` 历史版本下载（这里无论是下载的社区版或企业版等，下载器都是一样的，在社区版下载器里面也可选择安装专业版、企业版）

```
https://visualstudio.microsoft.com/zh-hans/vs/older-downloads/
or
https://my.visualstudio.com/Downloads?q=Visual%20Studio
```

这里下载`Visual Studio Professional 2019`主要的作用为：提供开发环境，编译PHP内核。

`Visual Studio Professional 2019` 安装情况：仅安装在 Visual Studio 中进行开发所需的工具和组件捆绑包。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01374ed023bd13a340.jpg)

#### <a class="reference-link" name="Visual%20Studio%20Code"></a>Visual Studio Code

`Visual Studio Code` 常用于不同语言的项目开发、源代码编辑调试等工作。
- 官网：介绍、下载
```
https://code.visualstudio.com/
```
- 添加相应扩展：c/c++扩展、代码辅助运行扩展
```
C/C++
Code Runner
```

#### <a class="reference-link" name="PHP%20Source%20Code"></a>PHP Source Code
- PHP官方各个版本源代码下载
```
https://www.php.net/releases/
or
https://github.com/php/php-src/releases
```

这里下载的版本为：`PHP 7.2.9`

#### <a class="reference-link" name="PHP%20Windows%20SDK"></a>PHP Windows SDK

> PHP SDK is a tool kit for Windows PHP builds.

`PHP SDK` 依赖关系

```
The PHP SDK 2.2+ is compatible with PHP 7.2 and above.

The PHP SDK 2.1 is required to build PHP 7.1 or 7.0.
```

新版SDK下载地址：构建PHP7

```
https://github.com/Microsoft/php-sdk-binary-tools
```

旧版SDK下载地址：构建PHP5

```
https://windows.php.net/downloads/php-sdk/
or
https://github.com/Microsoft/php-sdk-binary-tools/tree/legacy
```

这里下载的PHP-SDK版本为`2.2.0`，下载解压并添加相应环境变量

```
xxx\php-sdk-binary-tools-php-sdk-2.2.0\bin
xxx\php-sdk-binary-tools-php-sdk-2.2.0\msys2\usr\bin
```

#### <a class="reference-link" name="Source%20Insight"></a>Source Insight

> Source Insight是一个强大的面向项目的程序开发编辑器、代码浏览器和分析器，在您工作和规划时帮助您理解代码。
- 官网：介绍、下载
```
https://www.sourceinsight.com/
```

《PHP 7底层设计与源码实现》书中有写到

> 在研究PHP7源码之前，我们首先要掌握学习源码的方法论。首先是阅读工具，本章会介绍Windows下的Source lnsight、Mac下的Understand以及Linux下的Vim+Ctags，方便读者根据自己的操作系统选择不同的阅读工具。
Windows环境下有一款功能强大的IDE:Source Insight，内置了C++代码分析功能;同时还能自动维护项目内的符号数据库，使用非常方便。

有关`Source Insight`详细参考：[【工利其器】必会工具之（一）Source Insight篇](https://www.cnblogs.com/andy-songwei/p/9965714.html)

PS：这里`Source Insight`给我的使用感觉就一个字：**强**！！！

### <a class="reference-link" name="%E6%BA%90%E7%A0%81%E7%BB%93%E6%9E%84"></a>源码结构

下面先简单介绍一下PHP源码的目录结构。
<li>根目录: /这个目录包含的东西比较多，主要包含一些说明文件以及设计方案。 其实项目中的这些README文件是非常值得阅读的例如：
<ul>
<li>
`/README.PHP4-TO-PHP5-THIN-CHANGES` 这个文件就详细列举了PHP4和PHP5的一些差异。</li>
- 还有有一个比较重要的文件`/CODING_STANDARDS`，如果要想写PHP扩展的话，这个文件一定要阅读一下，不管你个人的代码风格是什么样，怎么样使用缩进和花括号，既然来到了这样一个团体里就应该去适应这样的规范，这样在阅读代码或者别人阅读你的代码是都会更轻松。
### <a class="reference-link" name="%E6%BA%90%E7%A0%81%E7%BC%96%E8%AF%91"></a>源码编译

环境准备部分，安装`Visual Studio 2019`后，运行在开始菜单里的`Visual Studio 2019`文件夹下的`x86 Native Tools Command Prompt for VS 2019`终端。

终端运行后，进入到`PHP 7.2.9`源代码目录中进行编译配置工作：
- 生成configure配置文件
执行源代码下`buildconf.bat`生成windows下的configure文件(configure.js)

```
xxx\php-7.2.9-windows-debug&gt;buildconf.bat
Rebuilding configure.js
Now run 'configure --help'

xxx\php-7.2.9-windows-debug&gt;
```
- 查看configure支持的编译参数
```
xxx\php-7.2.9-windows-debug&gt;configure.bat --help
PHP Version: 7.2.9

Options that enable extensions and SAPI will accept 'yes' or 'no' as a
parameter. They also accept 'shared' as a synonym for 'yes' and request a
shared build of that module. Not all modules can be built as shared modules;
configure will display [shared] after the module name if can be built that
way.

  --enable-snapshot-build           Build a snapshot; turns on everything it
                                    can and ignores build errors
  --with-toolset                    Toolset to use for the compilation, give:
                                    vs, clang, icc. The only recommended and
                                    supported toolset for production use is
                                    Visual Studio. Use others at your own
                                    risk.
  --with-cygwin                     Path to cygwin utilities on your system
  --enable-object-out-dir           Alternate location for binary objects
                                    during build
  --enable-debug                    Compile with debugging symbols
  --enable-debug-pack               Release binaries with external debug
                                    symbols (--enable-debug must not be
                                    specified)
  --enable-pgi                      Generate PGO instrumented binaries
  --with-pgo                        Compile optimized binaries using training
                                    data from folder
  --disable-zts                     Thread safety
  --with-prefix                     where PHP will be installed
  --with-mp                         Tell Visual Studio use up to
                                    [n,auto,disable] processes for compilation
  --with-php-build                  Path to where you extracted the
                                    development libraries
                                    (http://wiki.php.net/internals/windows/libs).
                                    Assumes that it is a sibling of this
                                    source dir (..\deps) if not specified
  --with-extra-includes             Extra include path to use when building
                                    everything
  --with-extra-libs                 Extra library path to use when linking
                                    everything
  --with-analyzer                   Enable static analyzer. Pass vs for Visual
                                    Studio, clang for clang, cppcheck for
                                    Cppcheck, pvs for PVS-Studio
  --disable-ipv6                    Disable IPv6 support (default is turn it
                                    on if available)
  --enable-fd-setsize               Set maximum number of sockets for
                                    select(2)
  --with-snapshot-template          Path to snapshot builder template dir
  --disable-security-flags          Disable the compiler security flags
  --without-uncritical-warn-choke   Disable some uncritical warnings
  --enable-sanitizer                Enable address sanitizer extension
  --with-codegen-arch               Architecture for code generation: ia32,
                                    sse, sse2, avx, avx2
  --with-all-shared                 Force all the non obligatory extensions to
                                    be shared
  --with-config-profile             Name of the configuration profile to save
                                    this to in php-src/config.name.bat
  --disable-test-ini                Enable automatic php.ini generation. The
                                    test.ini will be put into the build dir
                                    and used to automatically load the shared
                                    extensions.
  --with-test-ini-ext-exclude       Comma separated list of shared extensions
                                    to be excluded from the test.ini
  --enable-apache2handler           Build Apache 2.x handler
  --enable-apache2-2handler         Build Apache 2.2.x handler
  --enable-apache2-4handler         Build Apache 2.4.x handler
  --disable-cgi                     Build CGI version of PHP
  --disable-cli                     Build CLI version of PHP
  --enable-crt-debug                Enable CRT memory dumps for debugging sent
                                    to STDERR
  --enable-cli-win32                Build console-less CLI version of PHP
  --enable-embed                    Embedded SAPI library
  --enable-phpdbg                   Build phpdbg
  --enable-phpdbgs                  Build phpdbg shared
  --disable-phpdbg-webhelper        Build phpdbg webhelper
  --disable-bcmath                  bc style precision math functions
  --with-bz2                        BZip2
  --disable-calendar                calendar conversion support
  --disable-com-dotnet              COM and .Net support
  --disable-ctype                   ctype
  --with-curl                       cURL support
  --with-dba                        DBA support
  --with-qdbm                       DBA: QDBM support
  --with-db                         DBA: Berkeley DB support
  --with-lmdb                       DBA: Lightning memory-mapped database
                                    support
  --with-enchant                    Enchant Support
  --enable-fileinfo                 fileinfo support
  --disable-filter                  Filter Support
  --enable-ftp                      ftp support
  --without-gd                      Bundled GD support
  --without-libwebp                 webp support
  --with-gettext                    gettext support
  --with-gmp                        Include GNU MP support.
  --disable-hash                    enable hash support
  --with-mhash                      mhash support
  --without-iconv                   iconv support
  --with-imap                       IMAP Support
  --with-interbase                  InterBase support
  --enable-intl                     Enable internationalization support
  --disable-json                    JavaScript Object Serialization support
  --with-ldap                       LDAP support
  --with-libmbfl                    use external libmbfl
  --enable-mbstring                 multibyte string functions
  --enable-mbregex                  multibyte regex support
  --disable-mbregex-backtrack       check multibyte regex backtrack
  --without-mysqlnd                 Mysql Native Client Driver
  --with-oci8                       OCI8 support
  --with-oci8-11g                   OCI8 support using Oracle 11g Instant
                                    Client
  --with-oci8-12c                   OCI8 support using Oracle Database 12c
                                    Instant Client
  --enable-odbc                     ODBC support
  --with-odbcver                    Force support for the passed ODBC version.
                                    A hex number is expected, default 0x0350.
                                    Use the special value of 0 to prevent an
                                    explicit ODBCVER to be defined.
  --disable-opcache                 whether to enable Zend OPcache support
  --disable-opcache-file            whether to enable file based caching
  --with-openssl                    OpenSSL support
  --without-pcre-jit                Enable PCRE JIT support
  --with-pgsql                      PostgreSQL support
  --with-pspell                     pspell/aspell (whatever it's called this
                                    month) support
  --without-readline                Readline support
  --disable-session                 session support
  --enable-shmop                    shmop support
  --with-snmp                       SNMP support
  --enable-sockets                  SOCKETS support
  --with-sodium                     for libsodium support
  --with-sqlite3                    SQLite 3 support
  --with-password-argon2            Argon2 support
  --with-config-file-scan-dir       Dir to check for additional php ini files
  --enable-sysvshm                  SysV Shared Memory support
  --with-tidy                       TIDY support
  --disable-tokenizer               tokenizer support
  --enable-zend-test                enable zend-test extension
  --disable-zip                     ZIP support
  --disable-zlib                    ZLIB support
  --without-libxml                  LibXML support
  --without-dom                     DOM support
  --enable-exif                     Exchangeable image information (EXIF)
                                    Support
  --with-mysqli                     MySQLi support
  --enable-pdo                      Enable PHP Data Objects support
  --with-pdo-dblib                  freetds dblib (Sybase, MS-SQL) support for
                                    PDO
  --with-pdo-mssql                  Native MS-SQL support for PDO
  --with-pdo-firebird               Firebird support for PDO
  --with-pdo-mysql                  MySQL support for PDO
  --with-pdo-oci                    Oracle OCI support for PDO
  --with-pdo-odbc                   ODBC support for PDO
  --with-pdo-pgsql                  PostgreSQL support for PDO
  --with-pdo-sqlite                 for pdo_sqlite support
  --with-pdo-sqlite-external        for pdo_sqlite support from an external
                                    dll
  --disable-phar                    disable phar support
  --enable-phar-native-ssl          enable phar with native OpenSSL support
  --without-simplexml               Simple XML support
  --enable-soap                     SOAP support
  --without-xml                     XML support
  --without-wddx                    WDDX support
  --disable-xmlreader               XMLReader support
  --with-xmlrpc                     XMLRPC-EPI support
  --disable-xmlwriter               XMLWriter support
  --with-xsl                        xsl support
  xxx\php-7.2.9-windows-debug&gt;
```
- 配置编译参数
这里的编译参数为：以Debug模式编译PHP内核源码

```
xxx\php-7.2.9-windows-debug&gt;configure.bat --disable-all --enable-cli --enable-debug
PHP Version: 7.2.9

Saving configure options to config.nice.bat
Checking for cl.exe ...  &lt;in default path&gt;
WARNING: Using unknown MSVC version 19.28.29335

  Detected compiler MSVC 19.28.29335, untested
  Detected 32-bit compiler
Checking for link.exe ...  D:\QSoftware\VS2019Professional\Professional\VC\Tools\MSVC\14.28.29333\bin\HostX86\x86
Checking for nmake.exe ...  &lt;in default path&gt;
Checking for lib.exe ...  &lt;in default path&gt;
Checking for bison.exe ...  &lt;in default path&gt;
Checking for sed.exe ...  &lt;in default path&gt;
Checking for re2c.exe ...  &lt;in default path&gt;
  Detected re2c version 1.1.1
Checking for zip.exe ...  &lt;in default path&gt;
Checking for lemon.exe ...  &lt;in default path&gt;
Checking for mc.exe ...  C:\Program Files (x86)\Windows Kits\10\bin\10.0.18362.0\x86
Checking for mt.exe ...  C:\Program Files (x86)\Windows Kits\10\bin\10.0.18362.0\x86
WARNING: Debug builds cannot be built using multi processing

Build dir: D:\QSec\Code-Audit\PHP\PHP-Source-Code\php-7.2.9-windows-debug\Debug_TS
PHP Core:  php7ts_debug.dll and php7ts_debug.lib

Checking for wspiapi.h ...  &lt;in default path&gt;
Enabling IPv6 support
Enabling SAPI sapi\cli
Checking for library edit_a.lib;edit.lib ... &lt;not found&gt;
Enabling extension ext\date
Enabling extension ext\pcre
Enabling extension ext\reflection
Enabling extension ext\spl
Checking for timelib_config.h ...  ext/date/lib
Enabling extension ext\standard

Creating build dirs...
Generating files...
Generating Makefile
Generating main/internal_functions.c
Generating main/config.w32.h
Generating phpize
Done.

Enabled extensions:
-----------------------
| Extension  | Mode   |
-----------------------
| date       | static |
| pcre       | static |
| reflection | static |
| spl        | static |
| standard   | static |
-----------------------

Enabled SAPI:
-------------
| Sapi Name |
-------------
| cli       |
-------------
------------------------------------------------
|                 |                            |
------------------------------------------------
| Build type      | Debug                      |
| Thread Safety   | Yes                        |
| Compiler        | MSVC 19.28.29335, untested |
| Architecture    | x86                        |
| Optimization    | disabled                   |
| Static analyzer | disabled                   |
------------------------------------------------
Type 'nmake' to build PHP
xxx\php-7.2.9-windows-debug&gt;
```
- 开始编译
运行`nmake`指令进行编译

```
D:\QSec\Code-Audit\PHP\PHP-Source-Code\php-7.2.9-windows-debug&gt;nmake

Microsoft (R) 程序维护实用工具 14.28.29335.0 版
版权所有 (C) Microsoft Corporation。  保留所有权利。

Recreating build dirs
        type ext\pcre\php_pcre.def &gt; D:\QSec\Code-Audit\PHP\PHP-Source-Code\php-7.2.9-windows-debug\Debug_TS\php7ts_debug.dll.def
        "C:\Program Files (x86)\Windows Kits\10\bin\10.0.18362.0\x86\mc.exe" -h win32\ -r D:\QSec\Code-Audit\PHP\PHP-Source-Code\php-7.2.9-windows-debug\Debug_TS\ -x D:\QSec\Code-Audit\PHP\PHP-Source-Code\php-7.2.9-windows-debug\Debug_TS\ win32\build\wsyslog.mc
MC: Compiling win32\build\wsyslog.mc
cl: 命令行 warning D9035 :“Gm”选项已否决，并将在将来的版本中移除
php_cli.c
cl: 命令行 warning D9035 :“Gm”选项已否决，并将在将来的版本中移除
php_cli_process_title.c
、、、、、
、、、、、
```

编译完成后，在当前源码目录生成：`Debug_TS`项目（编译后的PHP可执行文件 php.exe-&gt;32位）

```
xxx\php-7.2.9-windows-debug\Debug_TS
λ  Qftm &gt;&gt;&gt;: ls
devel/        php.exe*          php.ilk   php7ts_debug.dll*          php7ts_debug.exp  resp/   wsyslog.dbg
ext/          php.exe.manifest  php.lib   php7ts_debug.dll.def       php7ts_debug.ilk  sapi/   wsyslog.rc
main/         php.exe.res       php.pdb   php7ts_debug.dll.manifest  php7ts_debug.lib  TSRM/   Zend/
MSG00001.bin  php.exp           php-7.2.9-devel-19.28.29335-x86/  php7ts_debug.dll.res       php7ts_debug.pdb  win32/

λ  Qftm &gt;&gt;&gt;:
```

测试`Debug_TS/php.exe`

```
λ  Qftm &gt;&gt;&gt;: php.exe -v
PHP 7.2.9 (cli) (built: Dec 15 2020 14:40:17) ( ZTS MSVC 19.28.29335, untested x86 DEBUG )
Copyright (c) 1997-2018 The PHP Group
Zend Engine v3.2.0, Copyright (c) 1998-2018 Zend Technologies
```

### <a class="reference-link" name="%E6%BA%90%E7%A0%81%E8%B0%83%E8%AF%95"></a>源码调试

这里通过配置`VSCode`进行PHP内核源码的调试工作：

先用VSCode打开PHP7.2.9编译的源代码项目，然后，在源代码目录下的`Debug_TS`里，创建一个用于测试的php文件`test.php`。

```
# /Debug_TS/test.php

&lt;?php
system("whoami");
?&gt;
```

随后点击功能菜单：`Run-&gt;Start Debugging`【F5】，弹框中任意选择一个，自动生成调试配置文件`.vscode/launch.json`，修改其内容如下：

```
`{`
        "version": "0.2.0",
        "configurations": [
            `{`
                "name": "Windows PHP7.2.9 Source Code Debug",
                "type": "cppvsdbg",
                "request": "launch",
                "program": "$`{`workspaceRoot`}`/Debug_TS/php.exe",
                "args": ["$`{`file`}`"],
                "stopAtEntry": false,
                "cwd": "$`{`workspaceRoot`}`/Debug_TS/",
                "environment": [],
                "externalConsole": false
            `}`
        ]
`}`
```

PS：注意这里需要存在扩展 `C/C++`，同时这里的调试和gdb没有关系。

打开`php-7.2.9-windows-debug/sapi/cli/php_cli.c`源文件【程序执行入口文件】，定位到1200行的main函数内打上断点。【在想要调试的源代码特定位置上打上特定的断点即可】

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t013fa14026ab3e7ad1.png)

PS：虽然这里的C文件显示有问题`Problems`，但是不影响调试，准确来说这里的调试和配置C环境没有关系。

点击`Run-&gt;Start Debugging`【F5】开始调试

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01eeaceed55c676b82.png)

VSCode调试窗口介绍

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t014d272f719d25884e.png)

VSCode调试快捷键介绍：对应上方调试窗口Debug动作按钮

```
- Continue/Pause   运行         F5
- Step Over        单步 步过     F10
- Step Into        单步 步入     F11
- Step Out         跳出 函数     Shift+F11
- Restart          重新 调试     Ctrl+Shift+F5
- Stop             关闭 调试     Shift+F5
```

### <a class="reference-link" name="%E6%BA%90%E7%A0%81%E6%89%A7%E8%A1%8C"></a>源码执行

#### <a class="reference-link" name="%E4%BB%BB%E5%8A%A1%E6%89%A7%E8%A1%8C"></a>任务执行

如果需要单纯执行PHP代码则需要配置`tasks.json`任务文件，初始化点击：`Terminal-&gt;Configure Tasks`进行模板文件的创建，然后选择其它命令执行模板即可

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01506f95c7c3d226f5.png)

初始任务模板内容：tasks.json

```
`{`
    // See https://go.microsoft.com/fwlink/?LinkId=733558
    // for the documentation about the tasks.json format
    "version": "2.0.0",
    "tasks": [
        `{`
            "label": "echo",
            "type": "shell",
            "command": "echo Hello"
        `}`
    ]
`}`
```

修改任务模板配置文件，配置PHP执行环境

```
// tasks.json

`{`
    "version": "2.0.0",
    "tasks": [
        `{`
            "label": "Windows php7.2.9.exe x.php",
            "type": "shell",
            "command": "D:/QSec/Code-Audit/PHP/PHP-Source-Code/php-7.2.9-windows-debug/Debug_TS/php.exe",
            "args": [
                "$`{`file`}`"
            ]
        `}`
    ]
`}`
```

运行任务`Windows php7.2.9.exe x.php`来执行特定PHP程序文件

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01374664debdceda31.png)

#### <a class="reference-link" name="%E6%8F%92%E4%BB%B6%E6%89%A7%E8%A1%8C"></a>插件执行

除了上方创建任务执行程序外，还可以借助插件`code runner`更加方便的去执行程序。

`code runner`扩展自带的默认对PHP运行的配置规则如下

```
"code-runner.executorMap": `{`
     "php": "php"
`}`
```

默认配置使用的是环境变量中的php.exe去执行的，可以更改设置为自己的php.exe路径【避免与环境变量中其它的php.exe发生冲突】

点击`File-&gt;Preferences-&gt;settings-&gt;Extensions-&gt;Run Code configuration-&gt;Executor Map-&gt;Edit in settings.json`进行设置

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01de9d7546ec008cda.png)

插件运行效果

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0105052dea448307d9.png)

### <a class="reference-link" name="%E7%96%91%E9%9A%BE%E6%9D%82%E7%97%87"></a>疑难杂症

针对调试编译的源码所要注意的问题，由于在编译期间会对源代码的路径等信息进行配置，写入编译后的`Debug_TS\php.exe`以及`Debug_TS\resp\*`等文件中，使得其可以协助我们进行源代码的调试工作。但是，这里就会出现一个问题：如果以后对源码的路径进行了任何改动都会导致对源代码调试出错。

`Debug_TS\php.exe`中有关PHP源代码路径信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d3492157deeebd05.png)

`Debug_TS\resp\*`中有关PHP源代码路径信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01790e7a011837176b.png)

这里如果对路径稍作修改则会调试出错(找不到源码文件)：`php-7.2.9-windows-debug` ==&gt; `php-7.2.9-windows-debugs`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t017ba62e9489131d57.png)



## PHP for Linux

针对Linux平台下：环境准备、PHP内核源码的编译、运行、调试等。

### <a class="reference-link" name="%E7%8E%AF%E5%A2%83%E5%87%86%E5%A4%87"></a>环境准备

环境部署情况：
- Linux (kali-linux-2020.4-amd64)
- Visual Studio Code (code-stable-x64-1605051992)
- PHP Source Code (PHP 7.2.9)
- Make (GNU Make 4.3 Built for x86_64-pc-linux-gnu)
- GDB (GNU gdb (Debian 10.1-1+b1) 10.1)
- Source Insight (Windows Source Insight 4.0)
#### <a class="reference-link" name="Visual%20Studio%20Code"></a>Visual Studio Code

`Visual Studio Code` 常用于不同语言的项目开发、源代码编辑调试等工作。
- 官网：介绍、下载
```
https://code.visualstudio.com/
```

下载deb免安装版本类别，之后解压并配置环境变量

```
# 下载解压
tar -zxvf code-stable-x64-1605051992.tar.gz

# 配置环境变量
vim ~/.bashrc
export PATH="/mnt/hgfs/QSec/Pentest/Red-Team/神兵利器/Windows/VSCode/VSCode-linux-x64:$PATH"

# 启动文件重命名
cd VSCode-linux-x64
mv code vscode
```

测试使用

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0160e3f4c3003c0093.png)
- 添加相应扩展：c/c++扩展、代码辅助运行扩展
```
C/C++
Code Runner
```

#### <a class="reference-link" name="PHP%20Source%20Code"></a>PHP Source Code
- PHP官方各个版本源代码下载
```
https://www.php.net/releases/
or
https://github.com/php/php-src/releases
```

这里下载的版本为：`PHP 7.2.9`

#### <a class="reference-link" name="Make"></a>Make

代码变成可执行文件，叫做编译(compile)，同C编译型语言，由c代码编译生成可执行文件(PE、ELF)；先编译这个，还是先编译那个（即编译的安排），叫做[构建](http://en.wikipedia.org/wiki/Software_build)（build）。

[Make](http://en.wikipedia.org/wiki/Make_(software))是最常用的构建工具，诞生于1977年，主要用于C语言的项目。但是实际上 ，任何只要某个文件有变化，就要重新构建的项目，都可以用Make构建。

有关Make资料可参考：[《Makefile文件教程》](https://gist.github.com/isaacs/62a2d1825d04437c6f08)、[《GNU Make手册》](https://www.gnu.org/software/make/manual/make.html)、[《Make 命令教程》](https://www.w3cschool.cn/mexvtg/)

```
┌──(root💀toor)-[~/桌面]
└─# make -v 
GNU Make 4.3
为 x86_64-pc-linux-gnu 编译
Copyright (C) 1988-2020 Free Software Foundation, Inc.
许可证：GPLv3+：GNU 通用公共许可证第 3 版或更新版本&lt;http://gnu.org/licenses/gpl.html&gt;。
本软件是自由软件：您可以自由修改和重新发布它。
在法律允许的范围内没有其他保证。

┌──(root💀toor)-[~/桌面]
└─#
```

#### <a class="reference-link" name="GDB"></a>GDB

**<a class="reference-link" name="%E5%9F%BA%E7%A1%80%E4%BB%8B%E7%BB%8D"></a>基础介绍**

GDB是一个由GNU开源组织发布的、UNIX/LINUX操作系统下的、基于命令行的、功能强大的程序调试工具。 它使您可以查看一个程序正在执行时的状态或该程序崩溃时正在执行的操作。

官方：介绍、Wiki
- [GDB: The GNU Project Debugger](http://www.gnu.org/software/gdb)
- [Welcome to the GDB Wiki](https://sourceware.org/gdb/wiki/)
支持语言：

```
Ada
Assembly
C
C++
D
Fortran
Go
Objective-C
OpenCL
Modula-2
Pascal
Rust
```

查看GDB调试窗口布局

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01dd692460bf3d02c2.png)

**<a class="reference-link" name="%E5%91%BD%E4%BB%A4%E5%88%97%E8%A1%A8"></a>命令列表**
- Tab键两次补全显示所有指令
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b8a92b41b645a23c.png)
- help all 显示所有指令（带注解）
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t016fb3ade828c93729.png)

<a class="reference-link" name="%E5%91%BD%E4%BB%A4%E8%AF%A6%E8%A7%A3"></a>**命令详解**

通过GDB帮助手册总结以下常用调试指令：

**《调试程序》**
- gdb binary_file_path：使用gdb载入binary_file_path指定的程序进行调试。
- gdb —pid PID：使用gdb attach到指定pid的进程进行调试。
- gdb $ file binary_file_path：在gdb中载入binary_file_path指定的程序进行调试。
**《帮助指令》**
- help command：查看gdb下command指令的帮助信息。
**《运行指令》**
- start：运行被调试的程序，断在程序入口-main函数，可带参数。
- run（简写 r）: 运行被调试的程序。 如果此前没有下过断点，则执行完整个程序；如果有断点，则程序暂停在第一个可用断点处，等待用户输入下一步命令。
- continue（简写 c） : 继续执行，到下一个断点停止（或运行结束）
- next（简写 n） : **C语言级的断点定位**。相当于其它调试器中的“**Step Over (单步跟踪)**”。单步跟踪程序，当遇到函数调用时，也不进入此函数体；此命令同 step 的主要区别是，step 遇到用户自定义的函数，将步进到函数中去运行，而 next 则直接调用函数，不会进入到函数体内。
- step （简写 s）：**C语言级的断点定位**。相当于其它调试器中的“**Step Into (单步跟踪进入)**”。单步调试如果有函数调用，则进入函数；与命令n不同，n是不进入调用的函数体。【**前提： s会进入C函数内部，但是不会进入没有定位信息的函数（比如没有加-g编译的代码，因为其没有C代码的行数标记，没办法定位）。（比如：调试编译PHP内核源码，然后调试php代码底层实现，跟踪到了libc函数后，由于libc没有标记信息，导致s或n之后直接打印输出完成程序的调试）**】
- nexti（简写 ni）：Next one instruction exactly。**汇编级别的断点定位**。作用和next指令相同，只是单步跟踪汇编代码，碰到call调用，不会进入汇编函数体。
- stepi（简写 si）：Step one instruction exactly。**汇编级别的断点定位**。作用和step指令相同，只是单步跟踪汇编代码，碰到call调用，会进入汇编函数体。【**前提：当要进入没有调试信息的库函数调试的时候，用si是唯一的方法。当进入有调试信息的函数，用si和s都可以进入函数体，但是他们不同，si是定位到汇编级别的第一个语句，但是s是进入到C级别的第一个语句。**】
- until（简写 u）：**跳出当前循环**。当你厌倦了在一个循环体内单步跟踪时，这个命令可以运行程序直到退出循环体。
- until n（简写 u n）：运行至第n行，不仅仅用来跳出循环。
- finish：**跳出当前函数**。运行程序，直到当前函数完成返回，并打印函数返回时的堆栈地址和返回值及参数值等信息。
- return：**跳出当前函数**。忽略之后的语句，强制函数返回。
- call function(arg)：调用程序中可见的函数，并传递“参数”，如：call gdb_test(55)。
- quit（简写 q）：退出GDB调试环境。
**《断点指令》**
<li>break, brea, bre, br, b：**设置断点**。break设置断点对象包括：行号、函数、地址等。
<ul>
- break n（简写 b n）：在第n行处设置断点（可以带上代码路径和代码名称：b OAGUPDATE.cpp:578）
- break function（简写 b function）：在函数function()的入口处设置断点，如：break cb_button。
- break **function（简写 b **function）：将断点设置在“由编译器生成的prolog代码处”。
- break **address（简写 b **address）：在指定地址下断点（地址必须是可执行代码段）- catch fork、vfork、exec：捕捉新创建的进程事件，对新进程继续调试。
- catch syscall \&lt;names|SyscallNumbers\&gt;：捕捉系统调用事件。（比如：创建新的进程事件，在libc中由execve()函数调用内核入口`{`系统调用号对应的系统内核调用函数`}`进行创建）（catch syscall execve）（捕捉execve()系统调用事件）（catch syscall 59）- disable index：使第index个断点失效。
- disable breakpoints：使所有断点失效。- enable index：使第index个断点生效。
- enable breakpoints：使所有断点生效。- watch expression：当表达式被写入，并且值被改变时中断。
- rwatch expression：当表达式被读时中断。
- awatch expression：当表达式被读或写时中断。- delete index（简写 d index）：删除指定断点（index可使用info b查看）。
- delete breakpoints（简写 d breakpoints）：删除所有断点，包括 断点、捕捉点、观察点。
**《文件指令》**
<li>list、l：**源代码显示**。
<ul>
- list（简写l）：列出当前程序执行处的源代码，默认每次显示10行。- list function（简写l function）：将显示当前文件“函数名”所在函数的源代码，如：list main。- list（简写l）：不带参数，将接着上一次 list 命令的，输出下边的内容。
**《数据指令》**
<li>print、inspect、p：打印表达式的值。
<ul>
- print expression（简写 p expression）：其中“表达式”可以是任何当前正在被测试程序的有效表达式，比如当前正在调试C语言的程序，那么“表达式”可以是任何C语言的有效表达式，包括数字，变量甚至是函数调用。- print ++a（简写 p ++a）：将把 a 中的值加1，并显示出来。- print gdb_test(22)（简写 p gdb_test(22)）：将以整数22作为参数调用 gdb_test() 函数。- print **argv[@70](https://github.com/70)（简写 p **argv[@70](https://github.com/70)）：打印指针argv的值以数组形式显示。- display expression：在单步运行时将非常有用，使用display命令设置一个表达式后，它将在每次单步进行指令后，紧接着输出被设置的表达式及值。如：display a。（**在当前设置的文件或程序上下文中，相当于实时跟踪被设置的表达式的变化情况，每单步执行调试一次程序，都会执行显示一次display设置的表达式的结果**）。
- info display（简写 i display）：查看display设置要查询的表达式列表信息。
- delete display n（简写 d diplay n）：删除display设置要查询的第n个表达式。
- delete display（简写 d display）： 删除所有display设置要查询的表达式。- x/x 0x7fffffffdfc8：显示地址0x7fffffffdfc8（指针）指向的地址。
- x/x $rsi：显示寄存器$rsi指向的地址。
- x/74s 0x7fffffffe307：以字符串形式打印地址0x7fffffffe307所存储的74个数据(数组长度74)。
- x/10i 0x7fffffffe307：打印地址0x7fffffffe307处的10条汇编指令。
**《状态指令》**
- info program（简写 i program）：查看程序是否在运行，进程号，被暂停的原因等。
- backtrace, where, bt, info stack, i stack, i s：显示当前上下文堆栈调用情况（常用于回溯跟踪，pwndbg可直接在工作窗口显示）
- thread apply all bt：查看所用线程堆栈调用信息。
- info locals（简写 i locals）：显示当前堆栈页的所有变量。
- info functions sefunction：查询函数sefunction的信息（函数定义实现的位置信息：文件、行号、代码）。
- stack n: 显示n个单元的栈信息。
**《扩展指令》**
- peda/pwndbg：查看可用命令（使用对应插件时使用）
<a class="reference-link" name="%E6%8F%92%E4%BB%B6%E8%BE%85%E5%8A%A9"></a>**插件辅助**

GDB调试常用插件：peda、pwndbg、gef，每次启动GDB只能加载一个插件，针对多个插件的处理可以写一个启动选择脚本或者在gdb的配置文件中手动生效某个插件（看个人习惯）。

**peda**
- 安装
```
git clone https://github.com/longld/peda.git ~/peda
echo "source ~/peda/peda.py" &gt;&gt; ~/.gdbinit
```
- 关闭peda插件因每次启动使用而自动生成session文件
在peda目录下，`cd lib`进入`lib`目录，在config.py里找到autosave选项，然后找到on这个词，改成off，即可关闭。

[![](https://p5.ssl.qhimg.com/t01ba89766b793baa1d.png)](https://p5.ssl.qhimg.com/t01ba89766b793baa1d.png)

**pwndbg**
- 安装
```
git clone https://github.com/pwndbg/pwndbg
cd pwndbg
./setup.sh
```

**gef**
- 安装
```
$ wget -O ~/gdbinit-gef.py --no-check-certificate http://gef.blah.cat/py
$ echo source ~/gdbinit-gef.py &gt;&gt; ~/.gdbinit
```

#### <a class="reference-link" name="Glibc"></a>Glibc

**1、基础介绍**

`GNU C`库项目提供了`GNU`系统和`GNU/Linux`系统以及使用Linux作为内核的许多其他系统的核心库。这些库提供了关键的API，包括ISO C11，POSIX.1-2008，BSD，特定于操作系统的API等。

官方：介绍、Wiki
- [The GNU C Library (glibc)](http://www.gnu.org/software/libc/)
- [Glibc Wiki](https://sourceware.org/glibc/wiki/HomePage)
**2、系统查看**
- 查看系统信息：GNU/Linux
```
→ Qftm :/# uname -a
Linux toor 5.9.0-kali1-amd64 #1 SMP Debian 5.9.1-1kali2 (2020-10-29) x86_64 GNU/Linux
 → Qftm :/#
```
- Debian下查看共享链接库
查看共享链接库版本信息

```
→ Qftm :~/Desktop# dpkg -l libc6 
Desired=Unknown/Install/Remove/Purge/Hold
| Status=Not/Inst/Conf-files/Unpacked/halF-conf/Half-inst/trig-aWait/Trig-pend
|/ Err?=(none)/Reinst-required (Status,Err: uppercase=bad)
||/ Name           Version      Architecture Description
+++-==============-============-============-=================================
ii  libc6:amd64    2.31-5       amd64        GNU C Library: Shared libraries
 → Qftm :~/Desktop#
```

编写简单的C程序来查看系统的动态链接库位置

```
#include&lt;stdio.h&gt;
int main()`{`
    printf("Hello World!\n");
    return 0;
`}`
```

编译运行

```
→ Qftm ← :~/桌面# gcc te.c -o te
 → Qftm ← :~/桌面# ./te
Hello World!
 → Qftm ← :~/桌面#
```

查看系统的动态链接库位置

```
→ Qftm ← :~/桌面# ldd te
    linux-vdso.so.1 (0x00007ffee03a7000)
    libc.so.6 =&gt; /lib/x86_64-linux-gnu/libc.so.6 (0x00007fc1bf9b2000)
    /lib64/ld-linux-x86-64.so.2 (0x00007fc1bfb8d000)
 → Qftm ← :~/桌面#
```

**3、在线源码**

woboq提供的项目，可以在线查看glibc源代码

```
https://code.woboq.org/userspace/glibc/
```

**4、源码下载**

各版本glibc源码下载地址

```
官方镜像仓库：http://ftp.gnu.org/gnu/glibc/

华中科技大学镜像仓库：http://mirror.hust.edu.cn/gnu/glibc/
```

由于测试系统Glibc版本为2.31，所以这里下载`glibc-2.31`源代码项目，后续底层审计分析需要用到。

#### <a class="reference-link" name="Source%20Insigh"></a>Source Insigh

在Windows平台使用`Source Insight 4`进行PHP内核源码的审计工作，具体参考上述`PHP for Windows`部分介绍。

### <a class="reference-link" name="%E6%BA%90%E7%A0%81%E7%BC%96%E8%AF%91"></a>源码编译

进入php7.2.9源码项目中，先构建生成`configure`文件：默认官方下载的源码项目中包含`configure`，这里为了避免出现不必要的错误，采取强制重新生成`configure`文件。

```
~/php-7.2.9-linux-debug# ./buildconf --force
```

生成configure脚本文件后，就可以开始编译了。为了调式PHP源码，这里同`PHP for Windows`部分，编译disable所有的扩展（除了一些必须包含的），使用下面的命令来完成编译安装的工作，安装的路径为`/mnt/hgfs/QSec/Code-Audit/PHP/PHP-Source-Code/php-7.2.9-linux-debug/Debug`：

```
~/php-7.2.9-linux-debug# ./configure --disable-all --enable-debug --prefix=/mnt/hgfs/QSec/Code-Audit/PHP/PHP-Source-Code/php-7.2.9-linux-debug/Debug
............
~/php-7.2.9-linux-debug# make -j4
............
~/php-7.2.9-linux-debug# make install
............
```

注意这里的`prefix`的参数必须为绝对路径，所以不能写成`./Debug`这类形式。需要注意一下，这里是以调试模式在编译PHP内核源码，所以需要设置一下`prefix`参数，不然PHP会被安装到系统默认路径中，影响后续的调试。另外两个编译参数，一个是`--disable-all`，这个表示禁止安装所有扩展（除了一个必须安装的），另外一个就是`--enable-debug`，这个选项表示以debug模式编译PHP源码，相当于`gcc`的`-g`选项编译c代码，它会把调试信息编译进最终的二进制程序中以方便对程序的调试。

上面的命令`make -jN`，N表示你的CPU数量（或者是CPU核心的数量），设置了这个参数后就可以使用多个CPU进行并行编译，这可以提高编译效率。

编译完成后，最终用于调式的PHP二进制可执行程序会安装在`./Debug`这个文件夹中。

查看编译的php.exe

```
→ Qftm :/mnt/hgfs/QSec/Code-Audit/PHP/PHP-Source-Code/php-7.2.9-linux-debug/Debug/bin# ./php -v
PHP 7.2.9 (cli) (built: Nov 20 2020 01:34:01) ( NTS DEBUG )
Copyright (c) 1997-2018 The PHP Group
Zend Engine v3.2.0, Copyright (c) 1998-2018 Zend Technologies
 → Qftm :/mnt/hgfs/QSec/Code-Audit/PHP/PHP-Source-Code/php-7.2.9-linux-debug/Debug/bin#
```

### <a class="reference-link" name="%E6%BA%90%E7%A0%81%E8%B0%83%E8%AF%95"></a>源码调试

#### <a class="reference-link" name="Visual%20Studio%20Code"></a>Visual Studio Code

同`PHP for Windows-&gt;源码调试`创建相应的`launch.json`调试配置文件，修改配置如下

```
`{`
    "version": "0.2.0",
    "configurations": [
        `{`
            "name": "Linux PHP7.2.9 Source Code Debug",
            "type": "cppdbg",
            "request": "launch",
            "program": "$`{`workspaceRoot`}`/Debug/bin/php",
            "args": ["$`{`file`}`"],
            "stopAtEntry": false,
            "cwd": "$`{`workspaceRoot`}`/Debug/bin",
            "environment": [],
            "externalConsole": false,
            "MIMode": "gdb",
            "miDebuggerPath": "/bin/gdb",
            "setupCommands": [
                `{`
                    "description": "Enable pretty-printing for gdb",
                    "text": "-enable-pretty-printing",
                    "ignoreFailures": true
                `}`
            ]
        `}`
    ]
`}`
```

PS：注意这里需要存在扩展 `C/C++`。

打开`php-7.2.9-linux-debug/sapi/cli/php_cli.c`源文件，定位到1200行的main函数内打上断点。【在想要调试的源代码特定位置上打上特定的断点即可】

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0105842df79a90ba53.png)

#### <a class="reference-link" name="GDB"></a>GDB

进入编译好的PHP可执行文件目录下

```
$ cd Debug/bin
```

加载待调式的PHP文件

```
# gdb --args ./php -f test1.php      

GNU gdb (Debian 10.1-1+b1) 10.1
Copyright (C) 2020 Free Software Foundation, Inc.                                                                                                                              
License GPLv3+: GNU GPL version 3 or later &lt;http://gnu.org/licenses/gpl.html&gt;
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
Type "show copying" and "show warranty" for details.
This GDB was configured as "x86_64-linux-gnu".
Type "show configuration" for configuration details.
For bug reporting instructions, please see:
&lt;https://www.gnu.org/software/gdb/bugs/&gt;.
Find the GDB manual and other documentation resources online at:
    &lt;http://www.gnu.org/software/gdb/documentation/&gt;.

For help, type "help".
Type "apropos word" to search for commands related to "word"...
pwndbg: loaded 188 commands. Type pwndbg [filter] for a list.
pwndbg: created $rebase, $ida gdb functions (can be used with print/break)
Reading symbols from ./php...
pwndbg&gt;
```

对程序入口函数下断点，并查看断点信息

```
pwndbg&gt; b main
Breakpoint 1 at 0x46430e: file /mnt/hgfs/QSec/Code-Audit/PHP/PHP-Source-Code/php-7.2.9-linux-debug/sapi/cli/php_cli.c, line 1216.
pwndbg&gt; i b
Num     Type           Disp Enb Address            What
1       breakpoint     keep y   0x000000000046430e in main at /mnt/hgfs/QSec/Code-Audit/PHP/PHP-Source-Code/php-7.2.9-linux-debug/sapi/cli/php_cli.c:1216
pwndbg&gt;
```

运行至断点处

```
pwndbg&gt; r
```

单步调式：n、ni、s、si

```
pwndbg&gt; n
```

### <a class="reference-link" name="%E6%BA%90%E7%A0%81%E6%89%A7%E8%A1%8C"></a>源码执行

#### <a class="reference-link" name="%E4%BB%BB%E5%8A%A1%E6%89%A7%E8%A1%8C"></a>任务执行

同`PHP for Windows-&gt;源码执行-&gt;任务执行`创建相应的tasks.json任务文件，修改配置如下

```
// tasks.json

`{`
    "version": "2.0.0",
    "tasks": [
        `{`
            "label": "Linux php",
            "type": "shell",
            "command": "/mnt/hgfs/QSec/Code-Audit/PHP/PHP-Source-Code/php-7.2.9-linux-debug/Debug/bin/php",
            "args": [
                "$`{`file`}`"
            ]
        `}`
    ]
`}`
```

任务执行效果

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t013c446b607e6b55ad.png)

#### <a class="reference-link" name="%E6%8F%92%E4%BB%B6%E6%89%A7%E8%A1%8C"></a>插件执行

除了上方创建任务执行程序外，还可以借助插件`code runner`更加方便的去执行程序

`code runner`自带的默认对PHP运行的配置规则如下

```
"code-runner.executorMap": `{`
     "php": "php"
`}`
```

默认配置使用的是环境变量中的php去执行的，可以更改设置为自己的php路径【避免与环境变量中其它的php发生冲突】

点击`settings-&gt;Extensions-&gt;Run Code configuration-&gt;Executor Map-&gt;Edit in settings.json`进行设置

[![](https://p5.ssl.qhimg.com/t01c7c90381793dbd4c.png)](https://p5.ssl.qhimg.com/t01c7c90381793dbd4c.png)

插件运行效果

[![](https://p5.ssl.qhimg.com/t01a6dcf0685bbe8f32.png)](https://p5.ssl.qhimg.com/t01a6dcf0685bbe8f32.png)



## 参考链接
- [Build your own PHP on Windows](https://wiki.php.net/internals/windows/stepbystepbuild_sdk_2)
- [Visual Studio docs](https://visualstudio.microsoft.com/zh-hans/vs/)
- [Visual Studio Code docs](https://code.visualstudio.com/docs)
- [《PHP 7底层设计与源码实现+PHP7内核剖析》](https://item.jd.com/28435383700.html)
- [深入理解 PHP 内核](https://www.bookstack.cn/books/php-internals)
- [WINDOWS下用VSCODE调试PHP7源代码](https://www.jianshu.com/p/29bc0443b586)
- [调式PHP源码](https://gywbd.github.io/posts/2016/2/debug-php-source-code.html)
- [用vscode调试php源码](https://blog.csdn.net/Dont_talk/article/details/107719466)
- [GDB: The GNU Project Debugger](http://www.gnu.org/software/gdb)
- [CreateProcessW function](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw)
- [命令注入成因小谈](https://xz.aliyun.com/t/6542)
- [浅谈从PHP内核层面防范PHP WebShell](https://paper.seebug.org/papers/old_sebug_paper/pst_WebZine/pst_WebZine_0x05/0x07_%E6%B5%85%E8%B0%88%E4%BB%8EPHP%E5%86%85%E6%A0%B8%E5%B1%82%E9%9D%A2%E9%98%B2%E8%8C%83PHP_WebShell.html)
- [Program execution Functions](https://www.php.net/manual/en/ref.exec.php)
- [linux系统调用](http://huhaipeng.top/2019/04/20/linux%E7%B3%BB%E7%BB%9F%E8%B0%83%E7%94%A8/)
- [system calls](https://fedora.juszkiewicz.com.pl/syscalls.html)