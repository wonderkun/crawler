> 原文链接: https://www.anquanke.com//post/id/209754 


# cpython历史漏洞分析及其fuzzer编写


                                阅读量   
                                **163958**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01d9b313be7e0af9f7.png)](https://p3.ssl.qhimg.com/t01d9b313be7e0af9f7.png)



## 历史漏洞分析

主要历史漏洞来源于[cpython hackerone](https://hackerone.com/ibb-python/hacktivity)<br>
这篇文章首先分析三个`cpython`历史漏洞，在我们简单熟悉了`cpython`的源码结构以后，再来编写一个`fuzzer`，其实算是添加`fuzzer`

### <a class="reference-link" name="Integer%20overflow%20in%20_json_encode_unicode"></a>Integer overflow in _json_encode_unicode

调试环境

```
kali x86
GNU gdb (Debian 9.2-1) 9.2
gcc (Debian 9.3.0-13) 9.3.0
```

漏洞官方[issue](https://bugs.python.org/issue24522)

找到最近的一个未修复漏洞的`commit`

```
➜  cpython git:(master) git log --grep="prevent integer overflow"

commit bdaeb7d237462a629e6c85001317faa85f94a0c6
Author: Victor Stinner &lt;victor.stinner@gmail.com&gt;
Date:   Mon Oct 16 08:44:31 2017 -0700

    bpo-31773: _PyTime_GetPerfCounter() uses _PyTime_t (GH-3983)

    * Rewrite win_perf_counter() to only use integers internally.
    * Add _PyTime_MulDiv() which compute "ticks * mul / div"
      in two parts (int part and remaining) to prevent integer overflow.
    * Clock frequency is checked at initialization for integer overflow.
    * Enhance also pymonotonic() to reduce the precision loss on macOS
      (mach_absolute_time() clock).

commit 7b78d4364da086baf77202e6e9f6839128a366ff
Author: Benjamin Peterson &lt;benjamin@python.org&gt;
Date:   Sat Jun 27 15:01:51 2015 -0500

    prevent integer overflow in escape_unicode (closes #24522)

➜  cpython git:(master) git checkout -f 7b78d4364da086baf77202e6e9f6839128a366ff
➜  cpython git:(7b78d4364d) git log

commit 7b78d4364da086baf77202e6e9f6839128a366ff (HEAD)
Author: Benjamin Peterson &lt;benjamin@python.org&gt;
Date:   Sat Jun 27 15:01:51 2015 -0500

    prevent integer overflow in escape_unicode (closes #24522)

commit 758d60baaa3c041d0982c84d514719ab197bd6ed //  未修复
Merge: 7763c68dcd acac1e0e3b
Author: Benjamin Peterson &lt;benjamin@python.org&gt;
Date:   Sat Jun 27 14:26:21 2015 -0500

    merge 3.4

commit acac1e0e3bf564fbad2107d8f50d7e9c42e5ef22
Merge: ff0f322edb dac3ab84c7
Author: Benjamin Peterson &lt;benjamin@python.org&gt;
Date:   Sat Jun 27 14:26:15 2015 -0500

    merge 3.3

commit dac3ab84c73eb99265f0cf4863897c8e8302dbfd
Author: Benjamin Peterson &lt;benjamin@python.org&gt;
Date:   Sat Jun 27 14:25:50 2015 -0500
...
➜  cpython git:(7b78d4364d) git checkout -f 758d60baaa3c041d0982c84d514719ab197bd6ed
Previous HEAD position was 7b78d4364d prevent integer overflow in escape_unicode (closes #24522)
HEAD is now at 758d60baaa merge 3.4
```

确定漏洞复现`commit: 758d60baaa3c041d0982c84d514719ab197bd6ed`<br>
使用`gcc`编译该`commit`代码

```
➜  cpython git:(7b78d4364d) export ASAN_OPTIONS=exitcode=0 # clang -fsantize=address 发生错误时不退出
➜  cpython git:(7b78d4364d) CC="gcc -g -fsanitize=address" ./configure --disable-ipv6
➜  cpython git:(7b78d4364d) make
➜  cpython git:(758d60baaa) ./python --version
Python 3.5.0b2+
```

使用的`poc.py`

```
import json

sp = "x13"*715827883 #((2**32)/6 + 1)
json.dumps([sp], ensure_ascii=False)
```

使用`gdb`调试

```
(gdb) b Modules/_json.c:265
No source file named Modules/_json.c.
Make breakpoint pending on future shared library load? (y or [n]) y
Breakpoint 1 (Modules/_json.c:265) pending.
(gdb) r poc.py
Starting program: /root/cpython/python poc.py
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/lib/i386-linux-gnu/libthread_db.so.1".

Breakpoint 1, escape_unicode (pystr=0x85c54800) at /root/cpython/Modules/_json.c:265
265        rval = PyUnicode_New(output_size, maxchar);
(gdb) p output_size
$1 = &lt;optimized out&gt;
(gdb) c
Continuing.

Program received signal SIGSEGV, Segmentation fault.
0xb6028131 in escape_unicode (pystr=0x85c54800) at /root/cpython/Modules/_json.c:302
302            ENCODE_OUTPUT;
```

可以发现程序确实是崩溃了，但是我们没有看到`output_size`的值，为了观察其值，我们将`Makefile`中的`-O3`优化改为`-O0`,重新编译，再次使用`gdb`调试

```
(gdb) b Modules/_json.c:265
No source file named Modules/_json.c.
Make breakpoint pending on future shared library load? (y or [n]) y
Breakpoint 1 (Modules/_json.c:265) pending.
(gdb) r poc.py
Starting program: /root/cpython/python poc.py
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/lib/i386-linux-gnu/libthread_db.so.1".

Breakpoint 1, escape_unicode (pystr=0x85c54800) at /root/cpython/Modules/_json.c:265
265        rval = PyUnicode_New(output_size, maxchar);

(gdb) p input_chars
$1 = 715827883

(gdb) p output_size
$2 = 4 &lt;== 整数溢出
```

来分析一下溢出原因，溢出出现在`_json.c:escape_unicode`函数中

```
maxchar = PyUnicode_MAX_CHAR_VALUE(pystr);
input_chars = PyUnicode_GET_LENGTH(pystr);
input = PyUnicode_DATA(pystr);
kind = PyUnicode_KIND(pystr);

/* Compute the output size */
for (i = 0, output_size = 2; i &lt; input_chars; i++) `{`
    Py_UCS4 c = PyUnicode_READ(kind, input, i);
    switch (c) `{`
    case '\': case '"': case 'b': case 'f':
    case 'n': case 'r': case 't':
        output_size += 2;
        break;
    default:
        if (c &lt;= 0x1f)
            output_size += 6; // 溢出，最后始终没有检测output_size的值，直接带入下面的New
        else
            output_size++;
    `}`
`}`

rval = PyUnicode_New(output_size, maxchar);

```

修复

```
maxchar = PyUnicode_MAX_CHAR_VALUE(pystr);
input_chars = PyUnicode_GET_LENGTH(pystr);
input = PyUnicode_DATA(pystr);
kind = PyUnicode_KIND(pystr);

/* Compute the output size */
for (i = 0, output_size = 2; i &lt; input_chars; i++) `{`
    Py_UCS4 c = PyUnicode_READ(kind, input, i);
    Py_ssize_t d;
    switch (c) `{`
    case '\': case '"': case 'b': case 'f':
    case 'n': case 'r': case 't':
        d = 2;
        break;
    default:
        if (c &lt;= 0x1f)
            d = 6;
        else
            d = 1;
    `}`
    if (output_size &gt; PY_SSIZE_T_MAX - d) `{` // 每次都需要做溢出判断
        PyErr_SetString(PyExc_OverflowError, "string is too long to escape");
        return NULL;
    `}`
    output_size += d;
`}`

rval = PyUnicode_New(output_size, maxchar);

```

### <a class="reference-link" name="Integer%20overflow%20in%20_pickle.c"></a>Integer overflow in _pickle.c

漏洞官方[issue](https://bugs.python.org/issue24521)<br>
利用上面的方法找到最近的未修复`commit:614bfcc953141cfdd38606f87a09d39f17367fa3`

`poc.py`

```
import pickle
pickle.loads(b'I1nrx00x00x00x20x2e')
```

编译之后直接利用`gdb`调试`poc`(编译不使用`-fsanitize`选项)

```
(gdb) r poc.py
Starting program: /root/cpython/python poc.py
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/lib/i386-linux-gnu/libthread_db.so.1".

Program received signal SIGSEGV, Segmentation fault.
0xb7875252 in _Unpickler_ResizeMemoList (self=0xb789c2fc, new_size=1073741824) at /root/cpython/Modules/_pickle.c:1069
1069            self-&gt;memo[i] = NULL;
(gdb) bt
#0  0xb7875252 in _Unpickler_ResizeMemoList (self=0xb789c2fc, new_size=1073741824) at /root/cpython/Modules/_pickle.c:1069
#1  0xb78752da in _Unpickler_MemoPut (self=0xb789c2fc, idx=536870912, value=0x664540 &lt;small_ints+96&gt;) at /root/cpython/Modules/_pickle.c:1092
#2  0xb787d75e in load_long_binput (self=0xb789c2fc) at /root/cpython/Modules/_pickle.c:5028
#3  0xb787e6bd in load (self=0xb789c2fc) at /root/cpython/Modules/_pickle.c:5409
#4  0xb78802e4 in pickle_loads (self=0xb78cb50c, args=0xb7931eac, kwds=0x0) at /root/cpython/Modules/_pickle.c:6336
#5  0x00569701 in PyCFunction_Call (func=0xb789d92c, arg=0xb7931eac, kw=0x0) at Objects/methodobject.c:84
#6  0x0048f744 in call_function (pp_stack=0xbfffeb80, oparg=1) at Python/ceval.c:4066
#7  0x0048b279 in PyEval_EvalFrameEx (f=0xb79b584c, throwflag=0) at Python/ceval.c:2679
#8  0x0048dc95 in PyEval_EvalCodeEx (_co=0xb79355c0, globals=0xb797666c, locals=0xb797666c, args=0x0, argcount=0, kws=0x0, kwcount=0, defs=0x0, defcount=0,
    kwdefs=0x0, closure=0x0) at Python/ceval.c:3436
#9  0x00482287 in PyEval_EvalCode (co=0xb79355c0, globals=0xb797666c, locals=0xb797666c) at Python/ceval.c:771
#10 0x004b464a in run_mod (mod=0x701b50, filename=0xb799bd98 "poc.py", globals=0xb797666c, locals=0xb797666c, flags=0xbffff478, arena=0x6aab10)
    at Python/pythonrun.c:1996
#11 0x004b44ba in PyRun_FileExFlags (fp=0x6f3e80, filename=0xb799bd98 "poc.py", start=257, globals=0xb797666c, locals=0xb797666c, closeit=1,
    flags=0xbffff478) at Python/pythonrun.c:1952
#12 0x004b3048 in PyRun_SimpleFileExFlags (fp=0x6f3e80, filename=0xb799bd98 "poc.py", closeit=1, flags=0xbffff478) at Python/pythonrun.c:1452
#13 0x004b251c in PyRun_AnyFileExFlags (fp=0x6f3e80, filename=0xb799bd98 "poc.py", closeit=1, flags=0xbffff478) at Python/pythonrun.c:1174
#14 0x004ccdc2 in run_file (fp=0x6f3e80, filename=0x6697d0 L"poc.py", p_cf=0xbffff478) at Modules/main.c:307
#15 0x004cd8e0 in Py_Main (argc=2, argv=0x6661a0) at Modules/main.c:744
#16 0x0042569a in main (argc=2, argv=0xbffff5d4) at ./Modules/python.c:62

(gdb) x/10x self-&gt;memo
0x6af900:    0x00000000    0x00000000    0x00000000    0x00000081
0x6af910:    0x006d2da8    0xb7e8e778    0x00000000    0x00000000
0x6af920:    0x00000000    0x00000000

(gdb) x/10x self-&gt;memo+i
0x73d000:    Cannot access memory at address 0x73d000

(gdb) p new_size
$3 = 1073741824

(gdb) p/x new_size
$4 = 0x40000000

(gdb) p PY_SSIZE_T_MAX
No symbol "PY_SSIZE_T_MAX" in current context.

(gdb) p new_size * sizeof(PyObject *)
$5 = 0 &lt;== 溢出

(gdb) p sizeof(PyObject *)
$6 = 4

(gdb) p memo
$7 = (PyObject **) 0x6af900

(gdb) p *memo
$8 = (PyObject *) 0x0

(gdb) p self-&gt;memo_size
$9 = 32
```

可以发现由于整数溢出，已经导致了一个越界写的漏洞。<br>
根据其调用栈，我们来一步一步分析其溢出的原因<br>
来看一下最后出错函数

```
static int
_Unpickler_ResizeMemoList(UnpicklerObject *self, Py_ssize_t new_size)
`{`
    Py_ssize_t i;
    PyObject **memo;

    assert(new_size &gt; self-&gt;memo_size);

    memo = PyMem_REALLOC(self-&gt;memo, new_size * sizeof(PyObject *));
    if (memo == NULL) `{`
        PyErr_NoMemory();
        return -1;
    `}`
    self-&gt;memo = memo;
    for (i = self-&gt;memo_size; i &lt; new_size; i++)
        self-&gt;memo[i] = NULL;
    self-&gt;memo_size = new_size;
    return 0;
`}`
```

根据`gdb`调试显示，由于溢出导致`new_size * sizeof(PyObject *)`数值为`0`，当其为`0`时传入

```
#define PyMem_REALLOC(p, n)    ((size_t)(n) &gt; (size_t)PY_SSIZE_T_MAX  ? NULL 
                : realloc((p), (n) ? (n) : 1))
```

也就是`realloc(p, 1)`，执行成功，接下来就会造成越界写

```
self-&gt;memo[i] = NULL; // 越界写
```

继续回溯，看看`new_size`如何得到

```
static int
_Unpickler_MemoPut(UnpicklerObject *self, Py_ssize_t idx, PyObject *value)
`{`
    PyObject *old_item;

    if (idx &gt;= self-&gt;memo_size) `{` // 条件成立直接*2分配空间
        if (_Unpickler_ResizeMemoList(self, idx * 2) &lt; 0)
            return -1;
        assert(idx &lt; self-&gt;memo_size);
    `}`
    Py_INCREF(value);
    old_item = self-&gt;memo[idx];
    self-&gt;memo[idx] = value;
    Py_XDECREF(old_item);
    return 0;
`}`
```

再次回溯，寻找`idx`的来源

```
static int
load_long_binput(UnpicklerObject *self)
`{`
    PyObject *value;
    Py_ssize_t idx;
    char *s;

    if (_Unpickler_Read(self, &amp;s, 4) &lt; 0)
        return -1;

    if (Py_SIZE(self-&gt;stack) &lt;= 0)
        return stack_underflow();
    value = self-&gt;stack-&gt;data[Py_SIZE(self-&gt;stack) - 1];

    idx = calc_binsize(s, 4);
    if (idx &lt; 0) `{`
        PyErr_SetString(PyExc_ValueError,
                        "negative LONG_BINPUT argument");
        return -1;
    `}`

    return _Unpickler_MemoPut(self, idx, value);
`}`
```

查看`calc_binsize`函数

```
static Py_ssize_t
calc_binsize(char *bytes, int size)
`{`
    unsigned char *s = (unsigned char *)bytes;
    size_t x = 0;

    assert(size == 4);

    x =  (size_t) s[0];
    x |= (size_t) s[1] &lt;&lt; 8;
    x |= (size_t) s[2] &lt;&lt; 16;
    x |= (size_t) s[3] &lt;&lt; 24;

    if (x &gt; PY_SSIZE_T_MAX)
        return -1;
    else
        return (Py_ssize_t) x;
`}`
```

其最终来源于我们的输入值，所以通过修改我们的输入值，可以成功导致基于堆的越界写

修复

```
#define PyMem_RESIZE(p, type, n) 
  ( (p) = ((size_t)(n) &gt; PY_SSIZE_T_MAX / sizeof(type)) ? NULL :    
    (type *) PyMem_REALLOC((p), (n) * sizeof(type)) //  如果为0，直接失败
```

### <a class="reference-link" name="int%20and%20float%20constructing%20from%20non%20NUL-terminated%20buffer"></a>int and float constructing from non NUL-terminated buffer

找到未修复`commit:9ad0aae6566311c6982a20955381cda5a2954519`<br>
官方[issues](https://bugs.python.org/issue24802)

这个issue我找到了`commit`，搭建了环境，但是没有复现成功，最主要的是，对我们寻找`fuzz`方面没有太大帮助，但是对我们理解字符串转换的危害还是很有帮助的，所以我们从原理上来跟一下源码<br>
那就通过`issue`中提到的代码，从理论上来复现一下

`poc.py`

```
import array
float(array.array("B",b"A"*0x10))
```

调用栈

```
STACK_TEXT:  
0080f328 651ac6e9 ffffffff 000000c8 00000000 python35!unicode_fromformat_write_cstr+0x10
0080f384 651ac955 0080f39c 090a2fe8 65321778 python35!unicode_fromformat_arg+0x409
0080f3d8 651f1a1a 65321778 0080f404 090a2fe8 python35!PyUnicode_FromFormatV+0x65
0080f3f4 652070a9 6536bd38 65321778 090a2fe8 python35!PyErr_Format+0x1a
0080f42c 6516be70 090a2fe8 0080f484 00000000 python35!PyOS_string_to_double+0xa9
0080f4f4 6514808b 06116b00 6536d658 6536d658 python35!PyFloat_FromString+0x100
0080f554 6516e6e2 06116b00 06116b00 06116b00 python35!PyNumber_Float+0xcb
...
```

直接看代码，首先是`floatobject.c`中的`PyFloat_FromString`

```
PyObject *
PyFloat_FromString(PyObject *v)
`{`
    const char *s, *last, *end;
    double x;
    PyObject *s_buffer = NULL;
    Py_ssize_t len;
    Py_buffer view = `{`NULL, NULL`}`;
    PyObject *result = NULL;

    if (PyUnicode_Check(v)) `{`
        s_buffer = _PyUnicode_TransformDecimalAndSpaceToASCII(v);
        if (s_buffer == NULL)
            return NULL;
        s = PyUnicode_AsUTF8AndSize(s_buffer, &amp;len);
        if (s == NULL) `{`
            Py_DECREF(s_buffer);
            return NULL;
        `}`
    `}`
    else if (PyObject_GetBuffer(v, &amp;view, PyBUF_SIMPLE) == 0) `{`
        s = (const char *)view.buf;    &lt;&lt;&lt;&lt;&lt; 确定s的数据
        len = view.len;
    `}`
    else `{`
        PyErr_Format(PyExc_TypeError,
            "float() argument must be a string or a number, not '%.200s'",
            Py_TYPE(v)-&gt;tp_name);
        return NULL;
    `}`
    last = s + len;
    /* strip space */
    while (s &lt; last &amp;&amp; Py_ISSPACE(*s))
        s++;
    while (s &lt; last - 1 &amp;&amp; Py_ISSPACE(last[-1]))
        last--;
    /* We don't care about overflow or underflow.  If the platform
     * supports them, infinities and signed zeroes (on underflow) are
     * fine. */
    x = PyOS_string_to_double(s, (char **)&amp;end, NULL);
    ...
`}`
```

跟进`PyOS_string_to_double`

```
if (errno == ENOMEM) `{`
        PyErr_NoMemory();
        fail_pos = (char *)s;
    `}`
else if (!endptr &amp;&amp; (fail_pos == s || *fail_pos != ''))
    PyErr_Format(PyExc_ValueError,
                    "could not convert string to float: "
                    "%.200s", s);
else if (fail_pos == s)
    PyErr_Format(PyExc_ValueError,
                    "could not convert string to float: "
                    "%.200s", s);
else if (errno == ERANGE &amp;&amp; fabs(x) &gt;= 1.0 &amp;&amp; overflow_exception)
    PyErr_Format(overflow_exception,
                    "value too large to convert to float: "
                    "%.200s", s);
else
    result = x;

```

跟进`PyErr_Format`函数

```
PyObject *
PyErr_Format(PyObject *exception, const char *format, ...)
`{`
    va_list vargs;
    PyObject* string;

#ifdef HAVE_STDARG_PROTOTYPES
    va_start(vargs, format);
#else
    va_start(vargs);
#endif

#ifdef Py_DEBUG
    /* in debug mode, PyEval_EvalFrameEx() fails with an assertion error
       if an exception is set when it is called */
    PyErr_Clear();
#endif

    string = PyUnicode_FromFormatV(format, vargs);
    PyErr_SetObject(exception, string);
    Py_XDECREF(string);
    va_end(vargs);
    return NULL;
`}`
```

继续跟进`PyUnicode_FromFormatV`

```
yObject *
PyUnicode_FromFormatV(const char *format, va_list vargs)
`{`
    va_list vargs2;
    const char *f;
    _PyUnicodeWriter writer;

    _PyUnicodeWriter_Init(&amp;writer);
    writer.min_length = strlen(format) + 100;
    writer.overallocate = 1;

    /* va_list may be an array (of 1 item) on some platforms (ex: AMD64).
       Copy it to be able to pass a reference to a subfunction. */
    Py_VA_COPY(vargs2, vargs);

    for (f = format; *f; ) `{`
        if (*f == '%') `{`
            f = unicode_fromformat_arg(&amp;writer, f, &amp;vargs2);
            if (f == NULL)
                goto fail;
        `}`
    ...
```

根据调用栈跟进`unicode_fromformat_arg`<br>
由于`format`是由`%s`构成，所以我们只看`s`部分

```
unicode_fromformat_arg

...
case 's':
    `{`
        /* UTF-8 */
        const char *s = va_arg(*vargs, const char*);
        if (unicode_fromformat_write_cstr(writer, s, width, precision) &lt; 0)
            return NULL;
        break;
    `}`
...
```

利用`va_arg`直接读取了参数，并将指针`s`指向该地址，继续跟进`unicode_fromformat_write_cstr`

```
static int
unicode_fromformat_write_cstr(_PyUnicodeWriter *writer, const char *str,
                              Py_ssize_t width, Py_ssize_t precision)
`{`
    /* UTF-8 */
    Py_ssize_t length;
    PyObject *unicode;
    int res;

    length = strlen(str); 
    if (precision != -1)
        length = Py_MIN(length, precision);
    unicode = PyUnicode_DecodeUTF8Stateful(str, length, "replace", NULL);
    if (unicode == NULL)
        return -1;

    res = unicode_fromformat_write_str(writer, unicode, width, -1);
    Py_DECREF(unicode);
    return res;
`}`
```

直接利用`strlen`计算上面的参数长度，如果`str`不是一个以``结尾的字符串，那么接下来利用长度访问该地址的数据将会出现越界读写的问题

该漏洞主要原因来源于`floatobject.c`中的代码，`%s`的数据由强制转换而来

```
else if (PyObject_GetBuffer(v, &amp;view, PyBUF_SIMPLE) == 0) `{`
        s = (const char *)view.buf;    &lt;&lt;&lt;&lt;&lt; 强制转换
        len = view.len;
    `}`
```

提醒我们，在做强制转换时，要注意检查是否可以转换，转换后会不会造成漏洞



## fuzzer编写

上文我们已经分析完`cpython`的三个漏洞了，对`cpython`有了一定的了解，那么我们就开始编写`cpython`的`fuzzer`代码。<br>
在编写前，我们来看看`cpython`自己有没有`fuzz`测试模块，简单搜索一下，发现在`Modules/_xxtestfuzz/`目录下存在`fuzz`代码，这就好办了，我们直接在此基础上添加我们想要测试的模块的fuzz代码就行

首先阅读一下`fuzz.c`大概的代码逻辑就会发现，如果想要添加模块的`fuzz`代码，还是很简单的<br>
主要需要修改的就两个部分，拿`struck.unpack`来举例子

第一步，初始化

```
PyObject* struct_unpack_method = NULL;
PyObject* struct_error = NULL;
/* Called by LLVMFuzzerTestOneInput for initialization */
static int init_struct_unpack() `{`
    /* Import struct.unpack */
    PyObject* struct_module = PyImport_ImportModule("struct"); // 导出模块
    if (struct_module == NULL) `{`
        return 0;
    `}`
    struct_error = PyObject_GetAttrString(struct_module, "error"); // 导出所有的错误对象
    if (struct_error == NULL) `{`
        return 0;
    `}`
    struct_unpack_method = PyObject_GetAttrString(struct_module, "unpack"); // 得到unpack函数
    return struct_unpack_method != NULL;
`}`
```

第二步，调用需要`fuzz`的函数，并过滤一些不必要的错误

```
/* Fuzz struct.unpack(x, y) */
static int fuzz_struct_unpack(const char* data, size_t size) `{`
    /* Everything up to the first null byte is considered the
       format. Everything after is the buffer */
    const char* first_null = memchr(data, '', size);
    if (first_null == NULL) `{`
        return 0;
    `}`

    size_t format_length = first_null - data;
    size_t buffer_length = size - format_length - 1;

    PyObject* pattern = PyBytes_FromStringAndSize(data, format_length);
    if (pattern == NULL) `{`
        return 0;
    `}`
    PyObject* buffer = PyBytes_FromStringAndSize(first_null + 1, buffer_length);
    if (buffer == NULL) `{`
        Py_DECREF(pattern);
        return 0;
    `}`

    PyObject* unpacked = PyObject_CallFunctionObjArgs(
        struct_unpack_method, pattern, buffer, NULL); // 调用函数
    /* Ignore any overflow errors, these are easily triggered accidentally */
    if (unpacked == NULL &amp;&amp; PyErr_ExceptionMatches(PyExc_OverflowError)) `{` // 过滤不必要的错误
        PyErr_Clear();
    `}`
    /* The pascal format string will throw a negative size when passing 0
       like: struct.unpack('0p', b'') */
    if (unpacked == NULL &amp;&amp; PyErr_ExceptionMatches(PyExc_SystemError)) `{`
        PyErr_Clear();
    `}`
    /* Ignore any struct.error exceptions, these can be caused by invalid
       formats or incomplete buffers both of which are common. */
    if (unpacked == NULL &amp;&amp; PyErr_ExceptionMatches(struct_error)) `{`
        PyErr_Clear();
    `}`

    Py_XDECREF(unpacked);
    Py_DECREF(pattern);
    Py_DECREF(buffer);
    return 0;
`}`

```

再添加一下`libfuzzer`调用代码

```
#if !defined(_Py_FUZZ_ONE) || defined(_Py_FUZZ_fuzz_struct_unpack)
    static int STRUCT_UNPACK_INITIALIZED = 0;
    if (!STRUCT_UNPACK_INITIALIZED &amp;&amp; !init_struct_unpack()) `{`
        PyErr_Print();
        abort();
    `}` else `{`
        STRUCT_UNPACK_INITIALIZED = 1;
    `}`
    rv |= _run_fuzz(data, size, fuzz_struct_unpack);
#endif
```

整个过程完事

这里其实比较麻烦的是过滤错误信息，因为你不一定能知道你要`fuzz`的模块的所有错误信息，很有可能过滤不全，在fuzz的时候会出错，导致需要重新添加过滤条件，再重新开启fuzz，整个过程，我也没有很好的办法，就是不停的试错，最后把无关的错误信息都过滤，下面就会遇到这样的问题

我们上面分析的第一个漏洞`json`已经存在`fuzz`模块了，那么我们就添加第二个`pickle`模块的`fuzz`代码

首先初始化

```
PyObject* pickle_loads_method = NULL;

/* Called by LLVMFuzzerTestOneInput for initialization */
static int init_pickle_loads() `{`
    /* Import struct.unpack */
    PyObject* pickle_module = PyImport_ImportModule("pickle");
    if (pickle_module == NULL) `{`
        return 0;
    `}`
    pickle_loads_method = PyObject_GetAttrString(pickle_module, "loads");
    return pickle_loads_method != NULL;
`}`
```

`pickle`本身的错误对象，我们需要到`_pickle.c`里面去找，在该文件的最后我们找到了添加错误对象的代码

```
PyMODINIT_FUNC
PyInit__pickle(void)
`{`
    PyObject *m;
    PickleState *st;

    m = PyState_FindModule(&amp;_picklemodule);
    if (m) `{`
        Py_INCREF(m);
        return m;
    `}`

    if (PyType_Ready(&amp;Pdata_Type) &lt; 0)
        return NULL;
    if (PyType_Ready(&amp;PicklerMemoProxyType) &lt; 0)
        return NULL;
    if (PyType_Ready(&amp;UnpicklerMemoProxyType) &lt; 0)
        return NULL;

    /* Create the module and add the functions. */
    m = PyModule_Create(&amp;_picklemodule);
    if (m == NULL)
        return NULL;

    /* Add types */
    if (PyModule_AddType(m, &amp;Pickler_Type) &lt; 0) `{`
        return NULL;
    `}`
    if (PyModule_AddType(m, &amp;Unpickler_Type) &lt; 0) `{`
        return NULL;
    `}`
    if (PyModule_AddType(m, &amp;PyPickleBuffer_Type) &lt; 0) `{`
        return NULL;
    `}`

    st = _Pickle_GetState(m);

    /* Initialize the exceptions. */
    st-&gt;PickleError = PyErr_NewException("_pickle.PickleError", NULL, NULL); // 添加第一个错误对象
    if (st-&gt;PickleError == NULL)
        return NULL;
    st-&gt;PicklingError = 
        PyErr_NewException("_pickle.PicklingError", st-&gt;PickleError, NULL)  // 添加第二个错误对象;
    if (st-&gt;PicklingError == NULL)
        return NULL;
    st-&gt;UnpicklingError = 
        PyErr_NewException("_pickle.UnpicklingError", st-&gt;PickleError, NULL); // 添加第三个错误对象
    if (st-&gt;UnpicklingError == NULL)
        return NULL;

    Py_INCREF(st-&gt;PickleError);
    if (PyModule_AddObject(m, "PickleError", st-&gt;PickleError) &lt; 0)
        return NULL;
    Py_INCREF(st-&gt;PicklingError);
    if (PyModule_AddObject(m, "PicklingError", st-&gt;PicklingError) &lt; 0)
        return NULL;
    Py_INCREF(st-&gt;UnpicklingError);
    if (PyModule_AddObject(m, "UnpicklingError", st-&gt;UnpicklingError) &lt; 0)
        return NULL;

    if (_Pickle_InitState(st) &lt; 0)
        return NULL;
    return m;
`}`
```

进一步完善初始化代码

```
PyObject* pickle_loads_method = NULL;
PyObject* pickle_error = NULL;
PyObject* pickling_error = NULL;
PyObject* unpickling_error = NULL;

/* Called by LLVMFuzzerTestOneInput for initialization */
static int init_pickle_loads() `{`
    /* Import struct.unpack */
    PyObject* pickle_module = PyImport_ImportModule("pickle");
    if (pickle_module == NULL) `{`
        return 0;
    `}`
    // 获取pickle所有error对象
    pickle_error = PyObject_GetAttrString(pickle_module, "PickleError");
    if (pickle_error == NULL) `{`
        return 0;
    `}`
    pickling_error = PyObject_GetAttrString(pickle_module, "PicklingError");
    if (pickling_error == NULL) `{`
        return 0;
    `}`
    unpickling_error = PyObject_GetAttrString(pickle_module, "UnpicklingError");
    if (unpickling_error == NULL) `{`
        return 0;
    `}`
    pickle_loads_method = PyObject_GetAttrString(pickle_module, "loads");
    return pickle_loads_method != NULL;
`}`
```

继续编写调用代码

```
#define MAX_PICKLE_TEST_SIZE 0x10000
static int fuzz_pickle_loads(const char* data, size_t size) `{`
    if (size &gt; MAX_PICKLE_TEST_SIZE) `{`
        return 0;
    `}`
    PyObject* input_bytes = PyBytes_FromStringAndSize(data, size);
    if (input_bytes == NULL) `{`
        return 0;
    `}`
    PyObject* parsed = PyObject_CallOneArg(pickle_loads_method, input_bytes);
    // 将可能会遇到的各种error加进来。进行忽略
    if (parsed == NULL &amp;&amp; // 这里的错误过滤信息，需要一步一步测试，这是我测试的完整列表
            (PyErr_ExceptionMatches(PyExc_ValueError) ||
            PyErr_ExceptionMatches(PyExc_AttributeError) ||
            PyErr_ExceptionMatches(PyExc_KeyError) ||
            PyErr_ExceptionMatches(PyExc_TypeError) ||
            PyErr_ExceptionMatches(PyExc_OverflowError) ||
            PyErr_ExceptionMatches(PyExc_EOFError) ||
            PyErr_ExceptionMatches(PyExc_MemoryError) ||
            PyErr_ExceptionMatches(PyExc_ModuleNotFoundError) ||
            PyErr_ExceptionMatches(PyExc_IndexError) ||
            PyErr_ExceptionMatches(PyExc_UnicodeDecodeError))) 
    `{`
        PyErr_Clear();
    `}`

    // pickle自身error进行忽略
    if (parsed == NULL &amp;&amp; (
           PyErr_ExceptionMatches(pickle_error) ||
           PyErr_ExceptionMatches(pickling_error) ||
           PyErr_ExceptionMatches(unpickling_error)
    ))
    `{`
        PyErr_Clear();
    `}`
    Py_DECREF(input_bytes);
    Py_XDECREF(parsed);
    return 0;
`}`
```

添加`libfuzzer`调用代码

```
#if !defined(_Py_FUZZ_ONE) || defined(_Py_FUZZ_fuzz_pickle_loads)
    static int PICKLE_LOADS_INITIALIZED = 0;
    if (!PICKLE_LOADS_INITIALIZED &amp;&amp; !init_pickle_loads()) `{`
        PyErr_Print();
        abort();
    `}` else `{`
        PICKLE_LOADS_INITIALIZED = 1;
    `}`

    rv |= _run_fuzz(data, size, fuzz_pickle_loads);
#endif
```

这里需要有一点注意的，如果我们直接利用上面的编译，可以使用，但是很快`fuzz_pickle_loads`就会退出，<br>
退出的原因在于`libfuzzer`会有内存限制，即使提高了`libfuzzer`的内存使用量，但随着我们测试的深入，依然会因为内存不足<br>
导致出问题，这个问题困扰了我很久，在不断试错，不断调试后发现最后通过修改`cpython`的源码解决

具体修改`Includepyport.h`里面的代码

```
#define PY_SSIZE_T_MAX ((Py_ssize_t)(((size_t)-1)&gt;&gt;1))
```

修改为

```
#define PY_SSIZE_T_MAX 838860800  // 100MB 100 * 1024 * 1024 * 8
```

这样就解决了`libfuzzer`内存限制，导致`fuzz`不断失败的问题<br>
修改完后，可能`cpython`某些模块会因为内存过小导致编译失败，这里可以略过，只要我们的`fuzzer`程序能跑起来就行

整个过程折腾了我两天的时间，各种编译和运行错误，最后成功执行

```
tmux new -s fuzz_pickle ./out/fuzz_pickle_loads -jobs=60 -workers=6
```

我用六个线程，大概跑了一周的时间，没有发现任何`crash`，果然这种顶级开源项目相对来说代码质量还是不错的。有兴趣的可以自己跑一下，万一跑出来漏洞了呢 🙂



## 总结

最近大部分时间都是在看开源软件的漏洞，比如网络组件，开源语言等等，开源软件的好处就是我们可以直接根据`commit`，定位到漏洞，了解其漏洞原理和修复方法，之后就是不断分析其中的漏洞，然后想办法能不能自己编写一个`fuzzer`把这些漏洞跑出来，整个过程不断提高自己编写`fuzzer`的能力和分析漏洞的能力。

这类文章我应该会有一个开源漏洞`fuzz`系列，这个是第一篇，感兴趣的话可以关注一下我的[博客](https://github.com/xinali/articles/issues)
