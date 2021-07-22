> 原文链接: https://www.anquanke.com//post/id/226294 


# 命令执行底层原理探究-PHP（三）


                                阅读量   
                                **139853**
                            
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

本文**《 命令执行底层原理探究-PHP (三) 》**主要讲述的是第三部分：针对Windows平台下，PHP命令执行函数的底层原理分析。



## PHP for Windows

针对Windows平台下：PHP命令执行函数的底层分析。

### <a class="reference-link" name="%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C%E5%BA%95%E5%B1%82%E5%88%86%E6%9E%90"></a>命令执行底层分析

针对命令执行函数的底层分析，这里主要采用两种手段去分析：静态审计(静态审计内核源码)、动态审计(动态调试内核源码)。

#### <a class="reference-link" name="%E9%9D%99%E6%80%81%E5%AE%A1%E8%AE%A1"></a>静态审计

PHP命令执行函数有很多

```
system
exec
passthru
shell_exec
proc_open
popen
pcntl_exec
escapeshellarg
escapeshellcmd                                              
、、、、
```

大部分命令执行函数于`ext/standard/exec.c`源码中实现

```
/* `{``{``{` proto string exec(string command [, array &amp;output [, int &amp;return_value]])
   Execute an external program */
PHP_FUNCTION(exec)
`{`
    php_exec_ex(INTERNAL_FUNCTION_PARAM_PASSTHRU, 0);
`}`
/* `}``}``}` */

/* `{``{``{` proto int system(string command [, int &amp;return_value])
   Execute an external program and display output */
PHP_FUNCTION(system)
`{`
    php_exec_ex(INTERNAL_FUNCTION_PARAM_PASSTHRU, 1);
`}`
/* `}``}``}` */

/* `{``{``{` proto void passthru(string command [, int &amp;return_value])
   Execute an external program and display raw output */
PHP_FUNCTION(passthru)
`{`
    php_exec_ex(INTERNAL_FUNCTION_PARAM_PASSTHRU, 3);
`}`
/* `}``}``}` */

/* `{``{``{` proto string shell_exec(string cmd)
   Execute command via shell and return complete output as string */
PHP_FUNCTION(shell_exec)
`{`
    FILE *in;
    char *command;
    size_t command_len;
    zend_string *ret;
    php_stream *stream;

    ZEND_PARSE_PARAMETERS_START(1, 1)
        Z_PARAM_STRING(command, command_len)
    ZEND_PARSE_PARAMETERS_END();

#ifdef PHP_WIN32
    if ((in=VCWD_POPEN(command, "rt"))==NULL) `{`
#else
    if ((in=VCWD_POPEN(command, "r"))==NULL) `{`
#endif
        php_error_docref(NULL, E_WARNING, "Unable to execute '%s'", command);
        RETURN_FALSE;
    `}`

    stream = php_stream_fopen_from_pipe(in, "rb");
    ret = php_stream_copy_to_mem(stream, PHP_STREAM_COPY_ALL, 0);
    php_stream_close(stream);

    if (ret &amp;&amp; ZSTR_LEN(ret) &gt; 0) `{`
        RETVAL_STR(ret);
    `}`
`}`
/* `}``}``}` */
```

观察上面代码部分，可以发现`system、exec、passthru`这三个命令执行函数调用函数一样，皆为`php_exec_ex()`函数，不同点只在于调用函数的第二个参数`mode`不同`0、1、3`作为标识。而`shell_exec`函数则是调用`VCWD_POPEN()`函数去实现。

下面以`system()`命令执行函数执行`whoami`指令为例：

```
system('whoami');
```

借助源码审查工具`Source Insight`【导入`php7.2.9`源码项目】进行底层函数跟踪分析

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01c4edf096f15e84d1.png)

首先找到php中system()函数声明处：`ext\standard\exec.c:263`

```
PHP_FUNCTION(system)
`{`
    php_exec_ex(INTERNAL_FUNCTION_PARAM_PASSTHRU, 1);
`}`
```

很明显system函数由`php_exec_ex()`函数实现，跟进同文件下找到`php_exec_ex()`函数实现【**在`Source Insight`下面可以使用Ctrl+鼠标左键点击定位函数位置**】：`ext\standard\exec.c:209`

```
static void php_exec_ex(INTERNAL_FUNCTION_PARAMETERS, int mode) /* `{``{``{` */
`{`
    char *cmd;
    size_t cmd_len;
    zval *ret_code=NULL, *ret_array=NULL;
    int ret;

    ZEND_PARSE_PARAMETERS_START(1, (mode ? 2 : 3))
        Z_PARAM_STRING(cmd, cmd_len)
        Z_PARAM_OPTIONAL
        if (!mode) `{`
            Z_PARAM_ZVAL_DEREF(ret_array)
        `}`
        Z_PARAM_ZVAL_DEREF(ret_code)
    ZEND_PARSE_PARAMETERS_END_EX(RETURN_FALSE);

    if (!cmd_len) `{`
        php_error_docref(NULL, E_WARNING, "Cannot execute a blank command");
        RETURN_FALSE;
    `}`
    if (strlen(cmd) != cmd_len) `{`
        php_error_docref(NULL, E_WARNING, "NULL byte detected. Possible attack");
        RETURN_FALSE;
    `}`

    if (!ret_array) `{`
        ret = php_exec(mode, cmd, NULL, return_value);
    `}` else `{`
        if (Z_TYPE_P(ret_array) != IS_ARRAY) `{`
            zval_ptr_dtor(ret_array);
            array_init(ret_array);
        `}` else if (Z_REFCOUNT_P(ret_array) &gt; 1) `{`
            zval_ptr_dtor(ret_array);
            ZVAL_ARR(ret_array, zend_array_dup(Z_ARR_P(ret_array)));
        `}`
        ret = php_exec(2, cmd, ret_array, return_value);
    `}`
    if (ret_code) `{`
        zval_ptr_dtor(ret_code);
        ZVAL_LONG(ret_code, ret);
    `}`
`}`
/* `}``}``}` */
```

阅读`php_exec_ex()`函数实现，会对cmd参数进行初始化处理，然后调用`php_exec(mode, cmd, NULL, return_value)`函数，mode为不同执行函数标识、cmd为指令参数。

跟踪`php_exec()`函数调用：`ext\standard\exec.c:97`

```
/* `{``{``{` php_exec
 * If type==0, only last line of output is returned (exec)
 * If type==1, all lines will be printed and last lined returned (system)
 * If type==2, all lines will be saved to given array (exec with &amp;$array)
 * If type==3, output will be printed binary, no lines will be saved or returned (passthru)
 *
 */
PHPAPI int php_exec(int type, char *cmd, zval *array, zval *return_value)
`{`
    FILE *fp;
    char *buf;
    size_t l = 0;
    int pclose_return;
    char *b, *d=NULL;
    php_stream *stream;
    size_t buflen, bufl = 0;
#if PHP_SIGCHILD
    void (*sig_handler)() = NULL;
#endif

#if PHP_SIGCHILD
    sig_handler = signal (SIGCHLD, SIG_DFL);
#endif

#ifdef PHP_WIN32
    fp = VCWD_POPEN(cmd, "rb");
#else
    fp = VCWD_POPEN(cmd, "r");
#endif
    if (!fp) `{`
        php_error_docref(NULL, E_WARNING, "Unable to fork [%s]", cmd);
        goto err;
    `}`

    stream = php_stream_fopen_from_pipe(fp, "rb");

    buf = (char *) emalloc(EXEC_INPUT_BUF);
    buflen = EXEC_INPUT_BUF;

    if (type != 3) `{`
        b = buf;

        while (php_stream_get_line(stream, b, EXEC_INPUT_BUF, &amp;bufl)) `{`
            /* no new line found, let's read some more */
            if (b[bufl - 1] != '\n' &amp;&amp; !php_stream_eof(stream)) `{`
                if (buflen &lt; (bufl + (b - buf) + EXEC_INPUT_BUF)) `{`
                    bufl += b - buf;
                    buflen = bufl + EXEC_INPUT_BUF;
                    buf = erealloc(buf, buflen);
                    b = buf + bufl;
                `}` else `{`
                    b += bufl;
                `}`
                continue;
            `}` else if (b != buf) `{`
                bufl += b - buf;
            `}`

            if (type == 1) `{`
                PHPWRITE(buf, bufl);
                if (php_output_get_level() &lt; 1) `{`
                    sapi_flush();
                `}`
            `}` else if (type == 2) `{`
                /* strip trailing whitespaces */
                l = bufl;
                while (l-- &gt; 0 &amp;&amp; isspace(((unsigned char *)buf)[l]));
                if (l != (bufl - 1)) `{`
                    bufl = l + 1;
                    buf[bufl] = '\0';
                `}`
                add_next_index_stringl(array, buf, bufl);
            `}`
            b = buf;
        `}`
        if (bufl) `{`
            /* strip trailing whitespaces if we have not done so already */
            if ((type == 2 &amp;&amp; buf != b) || type != 2) `{`
                l = bufl;
                while (l-- &gt; 0 &amp;&amp; isspace(((unsigned char *)buf)[l]));
                if (l != (bufl - 1)) `{`
                    bufl = l + 1;
                    buf[bufl] = '\0';
                `}`
                if (type == 2) `{`
                    add_next_index_stringl(array, buf, bufl);
                `}`
            `}`

            /* Return last line from the shell command */
            RETVAL_STRINGL(buf, bufl);
        `}` else `{` /* should return NULL, but for BC we return "" */
            RETVAL_EMPTY_STRING();
        `}`
    `}` else `{`
        while((bufl = php_stream_read(stream, buf, EXEC_INPUT_BUF)) &gt; 0) `{`
            PHPWRITE(buf, bufl);
        `}`
    `}`

    pclose_return = php_stream_close(stream);
    efree(buf);

done:
#if PHP_SIGCHILD
    if (sig_handler) `{`
        signal(SIGCHLD, sig_handler);
    `}`
#endif
    if (d) `{`
        efree(d);
    `}`
    return pclose_return;
err:
    pclose_return = -1;
    goto done;
`}`
/* `}``}``}` */
```

审计`int php_exec(int type, char *cmd, zval *array, zval *return_value)`函数代码，发现函数内部会首先调用`VCWD_POPEN()`函数去处理`cmd`指令【**在这里不难发现该部分函数`VCWD_POPEN()`调用同`shell_exec()`可执行函数实现原理相同，也就说明`system、exec、passthru、shell_exec`这类命令执行函数原理相同，底层都调用了相同函数`VCWD_POPEN()`去执行系统指令**】。

这里的`VCWD_POPEN()`函数调用会通过相应的平台去执行：PHP_WIN32为Windows平台、另一个为`Unix`平台

```
#ifdef PHP_WIN32
    fp = VCWD_POPEN(cmd, "rb");
#else
    fp = VCWD_POPEN(cmd, "r");
#endif
```

进入`VCWD_POPEN(cmd, "rb")`函数： `Zend\zend_virtual_cwd.h:269`

```
#define VCWD_POPEN(command, type) virtual_popen(command, type)
```

由于`VCWD_POPEN`函数为`virtual_popen`实现，直接进入`virtual_popen()`函数实现：`Zend\zend_virtual_cwd.c:1831`

```
#ifdef ZEND_WIN32
CWD_API FILE *virtual_popen(const char *command, const char *type) /* `{``{``{` */
`{`
    return popen_ex(command, type, CWDG(cwd).cwd, NULL);
`}`
/* `}``}``}` */
#else /* Unix */
CWD_API FILE *virtual_popen(const char *command, const char *type) /* `{``{``{` */
`{`
    size_t command_length;
    int dir_length, extra = 0;
    char *command_line;
    char *ptr, *dir;
    FILE *retval;

    command_length = strlen(command);

    dir_length = CWDG(cwd).cwd_length;
    dir = CWDG(cwd).cwd;
    while (dir_length &gt; 0) `{`
        if (*dir == '\'') extra+=3;
        dir++;
        dir_length--;
    `}`
    dir_length = CWDG(cwd).cwd_length;
    dir = CWDG(cwd).cwd;

    ptr = command_line = (char *) emalloc(command_length + sizeof("cd '' ; ") + dir_length + extra+1+1);
    memcpy(ptr, "cd ", sizeof("cd ")-1);
    ptr += sizeof("cd ")-1;

    if (CWDG(cwd).cwd_length == 0) `{`
        *ptr++ = DEFAULT_SLASH;
    `}` else `{`
        *ptr++ = '\'';
        while (dir_length &gt; 0) `{`
            switch (*dir) `{`
            case '\'':
                *ptr++ = '\'';
                *ptr++ = '\\';
                *ptr++ = '\'';
                /* fall-through */
            default:
                *ptr++ = *dir;
            `}`
            dir++;
            dir_length--;
        `}`
        *ptr++ = '\'';
    `}`

    *ptr++ = ' ';
    *ptr++ = ';';
    *ptr++ = ' ';

    memcpy(ptr, command, command_length+1);
    retval = popen(command_line, type);

    efree(command_line);
    return retval;
`}`
/* `}``}``}` */
#endif
```

不难发现，针对`virtual_popen()`函数实现，也存在于不同平台，这里主要分析Windows平台，针对Unix平台在下面`PHP for Linux`部分会详细讲述。

针对`Windows`平台，`virtual_popen()`函数实现非常简单，直接调用`popen_ex()`函数进行返回。

进入`popen_ex()`函数实现：`TSRM\tsrm_win32.c:473`

```
TSRM_API FILE *popen_ex(const char *command, const char *type, const char *cwd, char *env)
`{`/*`{``{``{`*/
    FILE *stream = NULL;
    int fno, type_len, read, mode;
    STARTUPINFOW startup;
    PROCESS_INFORMATION process;
    SECURITY_ATTRIBUTES security;
    HANDLE in, out;
    DWORD dwCreateFlags = 0;
    BOOL res;
    process_pair *proc;
    char *cmd = NULL;
    wchar_t *cmdw = NULL, *cwdw = NULL, *envw = NULL;
    int i;
    char *ptype = (char *)type;
    HANDLE thread_token = NULL;
    HANDLE token_user = NULL;
    BOOL asuser = TRUE;

    if (!type) `{`
        return NULL;
    `}`

    /*The following two checks can be removed once we drop XP support */
    type_len = (int)strlen(type);
    if (type_len &lt;1 || type_len &gt; 2) `{`
        return NULL;
    `}`

    for (i=0; i &lt; type_len; i++) `{`
        if (!(*ptype == 'r' || *ptype == 'w' || *ptype == 'b' || *ptype == 't')) `{`
            return NULL;
        `}`
        ptype++;
    `}`

    cmd = (char*)malloc(strlen(command)+strlen(TWG(comspec))+sizeof(" /c ")+2);
    if (!cmd) `{`
        return NULL;
    `}`

    sprintf(cmd, "%s /c \"%s\"", TWG(comspec), command);
    cmdw = php_win32_cp_any_to_w(cmd);
    if (!cmdw) `{`
        free(cmd);
        return NULL;
    `}`

    if (cwd) `{`
        cwdw = php_win32_ioutil_any_to_w(cwd);
        if (!cwdw) `{`
            free(cmd);
            free(cmdw);
            return NULL;
        `}`
    `}`

    security.nLength                = sizeof(SECURITY_ATTRIBUTES);
    security.bInheritHandle            = TRUE;
    security.lpSecurityDescriptor    = NULL;

    if (!type_len || !CreatePipe(&amp;in, &amp;out, &amp;security, 2048L)) `{`
        free(cmdw);
        free(cwdw);
        free(cmd);
        return NULL;
    `}`

    memset(&amp;startup, 0, sizeof(STARTUPINFOW));
    memset(&amp;process, 0, sizeof(PROCESS_INFORMATION));

    startup.cb            = sizeof(STARTUPINFOW);
    startup.dwFlags        = STARTF_USESTDHANDLES;
    startup.hStdError    = GetStdHandle(STD_ERROR_HANDLE);

    read = (type[0] == 'r') ? TRUE : FALSE;
    mode = ((type_len == 2) &amp;&amp; (type[1] == 'b')) ? O_BINARY : O_TEXT;

    if (read) `{`
        in = dupHandle(in, FALSE);
        startup.hStdInput  = GetStdHandle(STD_INPUT_HANDLE);
        startup.hStdOutput = out;
    `}` else `{`
        out = dupHandle(out, FALSE);
        startup.hStdInput  = in;
        startup.hStdOutput = GetStdHandle(STD_OUTPUT_HANDLE);
    `}`

    dwCreateFlags = NORMAL_PRIORITY_CLASS;
    if (strcmp(sapi_module.name, "cli") != 0) `{`
        dwCreateFlags |= CREATE_NO_WINDOW;
    `}`

    /* Get a token with the impersonated user. */
    if(OpenThreadToken(GetCurrentThread(), TOKEN_ALL_ACCESS, TRUE, &amp;thread_token)) `{`
        DuplicateTokenEx(thread_token, MAXIMUM_ALLOWED, &amp;security, SecurityImpersonation, TokenPrimary, &amp;token_user);
    `}` else `{`
        DWORD err = GetLastError();
        if (err == ERROR_NO_TOKEN) `{`
            asuser = FALSE;
        `}`
    `}`

    envw = php_win32_cp_env_any_to_w(env);
    if (envw) `{`
        dwCreateFlags |= CREATE_UNICODE_ENVIRONMENT;
    `}` else `{`
        if (env) `{`
            free(cmd);
            free(cmdw);
            free(cwdw);
            return NULL;
        `}`
    `}`

    if (asuser) `{`
        res = CreateProcessAsUserW(token_user, NULL, cmdw, &amp;security, &amp;security, security.bInheritHandle, dwCreateFlags, envw, cwdw, &amp;startup, &amp;process);
        CloseHandle(token_user);
    `}` else `{`
        res = CreateProcessW(NULL, cmdw, &amp;security, &amp;security, security.bInheritHandle, dwCreateFlags, envw, cwdw, &amp;startup, &amp;process);
    `}`
    free(cmd);
    free(cmdw);
    free(cwdw);
    free(envw);

    if (!res) `{`
        return NULL;
    `}`

    CloseHandle(process.hThread);
    proc = process_get(NULL);

    if (read) `{`
        fno = _open_osfhandle((tsrm_intptr_t)in, _O_RDONLY | mode);
        CloseHandle(out);
    `}` else `{`
        fno = _open_osfhandle((tsrm_intptr_t)out, _O_WRONLY | mode);
        CloseHandle(in);
    `}`

    stream = _fdopen(fno, type);
    proc-&gt;prochnd = process.hProcess;
    proc-&gt;stream = stream;
    return stream;
`}`/*`}``}``}`*/
```

从`TSRM\tsrm_win32.c`文件不难发现，由`virtual_popen()`函数不同平台到`popen_ex()`函数可知，`virtual_popen()`函数是作为不同平台的分割点，此时的调用链已经到了仅和windows平台有联系。

接着对`*popen_ex()`函数进行分析，参数：`command`为指令参数、`cwd`为当前工作目录、`env`为环境变量信息。

为cmd变量动态分配空间：这里不得不说把cmd变量的空间分配的刚刚好

```
cmd = (char*)malloc(strlen(command)+strlen(TWG(comspec))+sizeof(" /c ")+2);
```

分配空间后，为cmd变量赋值

```
sprintf(cmd, "%s /c \"%s\"", TWG(comspec), command);

=&gt; cmd = "cmd.exe /c whoami"
```

这部分其实在PHP官方手册的[可执行函数](https://www.php.net/function.exec)中也有说明

[![](https://p4.ssl.qhimg.com/t01822f031588631cbf.png)](https://p4.ssl.qhimg.com/t01822f031588631cbf.png)

到这里也就会发现`system、exec、passthru、shell_exec`这类命令执行函数底层都会调用系统终端`cmd.exe`来执行传入的指令参数。那么既然会调用系统cmd，就要将cmd进程启动起来。

继续向后分析`*popen_ex()`函数，会找到相关Windows系统API来启动`cmd.exe`进程，然后由cmd进程执行指令参数(内部|外部指令)。

```
if (asuser) `{`
        res = CreateProcessAsUserW(token_user, NULL, cmdw, &amp;security, &amp;security, security.bInheritHandle, dwCreateFlags, envw, cwdw, &amp;startup, &amp;process);
        CloseHandle(token_user);
    `}` else `{`
        res = CreateProcessW(NULL, cmdw, &amp;security, &amp;security, security.bInheritHandle, dwCreateFlags, envw, cwdw, &amp;startup, &amp;process);
    `}`
```

> 在 Windows 平台上，创建进程有 `WinExec`，`system`，`_spawn/_wspawn`，`CreateProcess`，`ShellExecute` 等多种途径，但上述函数基本上还是由 `CreateProcess Family` 封装的。在 Windows 使用 `C/C++` 创建进程应当优先使用 `CreateProcess`，`CreateProcess`有三个变体，主要是为了支持以其他权限启动进程， `CreateProcess` 及其变体如下：

<th style="text-align: left;">Function</th><th style="text-align: left;">Feature</th><th style="text-align: left;">Details</th>
|------
<td style="text-align: left;">CreateProcessW/A</td><td style="text-align: left;">创建常规进程，权限继承父进程权限</td><td style="text-align: left;"></td>
<td style="text-align: left;">CreateProcessAsUserW/A</td><td style="text-align: left;">使用主 Token 创建进程，子进程权限与 Token 限定一致</td><td style="text-align: left;">必须开启 `SE_INCREASE_QUOTA_NAME`</td>
<td style="text-align: left;">CreateProcessWithTokenW</td><td style="text-align: left;">使用主 Token 创建进程，子进程权限与 Token 限定一致</td><td style="text-align: left;">必须开启 `SE_IMPERSONATE_NAME`</td>
<td style="text-align: left;">CreateProcessWithLogonW/A</td><td style="text-align: left;">使用指定用户凭据启动进程</td>

PS：有关Windows系统API的调用情况，一般编程语言启动某个可执行程序的进程，都会调用`CreateProcessW`系统API，而不使用`CreateProcessAsUserW`系统API。同时在cmd终端进程下，启动外部指令程序所调用的系统API一般为`CreateProcessInternalW`。

接着将进程运行的结果信息以流的形式返回，最终完成PHP命令执行函数的整个调用过程。

```
if (read) `{`
        fno = _open_osfhandle((tsrm_intptr_t)in, _O_RDONLY | mode);
        CloseHandle(out);
    `}` else `{`
        fno = _open_osfhandle((tsrm_intptr_t)out, _O_WRONLY | mode);
        CloseHandle(in);
    `}`

    stream = _fdopen(fno, type);
    proc-&gt;prochnd = process.hProcess;
    proc-&gt;stream = stream;
    return stream;
```

同理，按照上述整个审计思路，可整理出PHP常见命令执行函数在Windows平台下的底层调用链

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01eaaa514101083234.png)

#### <a class="reference-link" name="%E5%8A%A8%E6%80%81%E5%AE%A1%E8%AE%A1"></a>动态审计

有了上面`静态审计`部分的分析，后续进行动态调试会很方便。这里同样以`system()`函数执行`whoami`指令为例来进行动态调试，其它函数调试原理类似。

```
// test.php

&lt;?php
system("whoami");
?&gt;
```

在`ext/standard/exec.c:265`中对system()函数实现入口处下断点，F5启动调试，运行至断点处

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a26a3b11ad810021.png)

F11步入函数`php_exec_ex(INTERNAL_FUNCTION_PARAM_PASSTHRU, 1)`内部：`ext\standard\exec.c:209`

`php_exec_ex()`对cmd参数初始化处理后调用`php_exec(mode, cmd, NULL, return_value)`函数

[![](https://p2.ssl.qhimg.com/t01a3f6b42bb97fa7cb.png)](https://p2.ssl.qhimg.com/t01a3f6b42bb97fa7cb.png)

F11步入`php_exec()`函数：`ext\standard\exec.c:97`，`php_exec()`函数会传入cmd指令调用`VCWD_POPEN()`函数

[![](https://p2.ssl.qhimg.com/t01a72f0c181bae557d.png)](https://p2.ssl.qhimg.com/t01a72f0c181bae557d.png)

F11步入`VCWD_POPEN()`函数实现：

```
#define VCWD_POPEN(command, type) virtual_popen(command, type)

Zend\zend_virtual_cwd.h:269
```

由于`VCWD_POPEN`函数为`virtual_popen`实现，直接进入`virtual_popen()`函数实现：`Zend\zend_virtual_cwd.c:1831`

[![](https://p1.ssl.qhimg.com/t01ce03a73c3b0794ec.png)](https://p1.ssl.qhimg.com/t01ce03a73c3b0794ec.png)

`virtual_popen()`函数将cmd指令、当前工作空间等参数传给`popen_ex(command, type, CWDG(cwd).cwd, NULL)`函数执行返回。

F11步入`popen_ex()`函数实现：`TSRM\tsrm_win32.c:473`

[![](https://p5.ssl.qhimg.com/t0172ac4717fb580cbc.png)](https://p5.ssl.qhimg.com/t0172ac4717fb580cbc.png)

跟进`popen_ex()`函数，对cmd进行动态分配空间及赋值

[![](https://p1.ssl.qhimg.com/t018cdaa462e8998a75.png)](https://p1.ssl.qhimg.com/t018cdaa462e8998a75.png)

从cmd赋值的结果上来看，命令执行函数执行命令由底层调用cmd.exe来执行相应系统指令(内部|外部)。

后续调用`CreateProcessW()`系统API来启动cmd.exe进程，执行相应的指令即可。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011831d76d6e24f2d0.png)

查看函数之间的调用栈

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a49c169bfb905256.png)

如果单纯的是想知道某个命令执行函数是否调用cmd.exe终端去执行系统指令的话，可以在php脚本里面写一个循环，然后观察进程创建情况即可：简单、粗暴。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01e2adb2d908cfa657.png)



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