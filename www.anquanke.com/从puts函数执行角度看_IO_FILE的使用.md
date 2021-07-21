> 原文链接: https://www.anquanke.com//post/id/242636 


# 从puts函数执行角度看_IO_FILE的使用


                                阅读量   
                                **555156**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t0195fa177b50474e1e.png)](https://p1.ssl.qhimg.com/t0195fa177b50474e1e.png)



演示调试代码

```
#include&lt;stdio.h&gt;
int main()`{`

    puts("beef");
    puts("dead");
    return 0
`}`
```

几个重要的结构体

```
struct _IO_FILE `{`
    int _flags;
    char *_IO_read_ptr; /读取时 当前指针
    char *_IO_read_end; /结束
    char *_IO_read_base;
    char *_IO_write_base;
    char *_IO_write_ptr;
    char *_IO_write_end;
    char *_IO_buf_base;
    char *_IO_buf_end;
    char *_IO_save_base;
    char *_IO_backup_base;
    char *_IO_save_end;
    struct _IO_marker *_markers;
    struct _IO_FILE *_chain;
    int _fileno;
    int _flags2;
    __off_t _old_offset;
    unsigned short _cur_column;
    signed char _vtable_offset;
    char _shortbuf[1];
    _IO_lock_t *_lock;
    __off64_t _offset;
    struct _IO_codecvt *_codecvt;
    struct _IO_wide_data *_wide_data;
    struct _IO_FILE *_freeres_list;
    void *_freeres_buf;
    size_t __pad5;
    int _mode;
    char _unused2[20];
`}` *
```

`_IO_file`处理文件时使用的一个核心结构体，同时linux预先创建了 `_fileno`为0，1，2用来表示stdin，stdout ，stderr。而puts之类输出函数通常使用stdout。

本文主要在结合gdb与对应源码的基础上重新讲述程序首次运行时对应结构体的初始化以及该结构体在何时，如何发挥作用

在进入puts函数之前，stdout内容如下

[![](https://p5.ssl.qhimg.com/t011b071f697e255d85.png)](https://p5.ssl.qhimg.com/t011b071f697e255d85.png)

简单解释一下对应的字段含义

**_flag**字段保存了魔术头和一些标志位，实际上该字段表示，在利用该时通常需要修改_flag 绕过一些检测

```
_flag=0xfbad2084--&gt; _IO_IS_FILEBUF|_IO_LINKED|_IO_NO_READS
```

0xFBAD 为magic head 0x2084对应为标志位。对应一些标志的定义如下

```
#define _IO_MAGIC 0xFBAD0000 /* Magic number */
#define _OLD_STDIO_MAGIC 0xFABC0000 /* Emulate old stdio. */
#define _IO_MAGIC_MASK 0xFFFF0000
#define _IO_USER_BUF 1 /* User owns buffer; don't delete it on close. */
#define _IO_UNBUFFERED 2
#define _IO_NO_READS 4 /* Reading not allowed */
#define _IO_NO_WRITES 8 /* Writing not allowd */
#define _IO_EOF_SEEN 0x10
#define _IO_ERR_SEEN 0x20
#define _IO_DELETE_DONT_CLOSE 0x40 /* Don't call close(_fileno) on cleanup. */
#define _IO_LINKED 0x80 /* Set if linked (using _chain) to streambuf::_list_all.*/
#define _IO_IN_BACKUP 0x100
#define _IO_LINE_BUF 0x200
#define _IO_TIED_PUT_GET 0x400 /* Set if put and get pointer logicly tied. */
#define _IO_CURRENTLY_PUTTING 0x800
#define _IO_IS_APPENDING 0x1000
#define _IO_IS_FILEBUF 0x2000
#define _IO_BAD_SEEN 0x4000
#define _IO_USER_LOCK 0x8000
```

经过延时绑定的跳转进入到puts函数主体

[![](https://p0.ssl.qhimg.com/t016db9b9d69d0c18d9.png)](https://p0.ssl.qhimg.com/t016db9b9d69d0c18d9.png)

针对puts，进行调用了如图的函数，处理传入puts的字符串的长度问题

单步调试 发现第一个函数调用 `_IO_file_xsputn`

在源代码中对应的函数为 `_IO_new_file_xsputn`

在调试时出现函数名不同的原因是因为下面这个宏

```
# define _IO_new_file_xsputn _IO_file_xsputn
```

如下

```
count = f-&gt;_IO_write_end - f-&gt;_IO_write_ptr; /* Space available. */
if ((f-&gt;_flags &amp; _IO_LINE_BUF) &amp;&amp; (f-&gt;_flags &amp; _IO_CURRENTLY_PUTTING)
```

此时`count`为0，且无法满足对标志位的判定

```
if (to_do + must_flush &gt; 0)
 `{`
      _IO_size_t block_size, do_write;
      /* Next flush the (full) buffer. */
      if (_IO_OVERFLOW (f, EOF) == EOF)
```

`_IO_OVERFLOW`

```
#define _IO_OVERFLOW(FP, CH) JUMP1 (__overflow, FP, CH)
```

对应到运行时的函数跳转为

[![](https://p3.ssl.qhimg.com/t0170df28c2ad6e8c24.png)](https://p3.ssl.qhimg.com/t0170df28c2ad6e8c24.png)

即 `_IO_new_file_overflow` ，

```
if ((f-&gt;_flags &amp; _IO_CURRENTLY_PUTTING) == 0 || f-&gt;_IO_write_base == 0)
    `{`
      /* Allocate a buffer if needed. */
      if (f-&gt;_IO_write_base == 0)
    `{`
      INTUSE(_IO_doallocbuf) (f);
      _IO_setg (f, f-&gt;_IO_buf_base, f-&gt;_IO_buf_base, f-&gt;_IO_buf_base);
    `}`
```

此时 调用`_IO_doallocbuf` 这个函数进行了对缓冲区的申请，以及填充对应字段。

实际调用 `_IO_file_doallocate`函数

在`glibc-2.3.1/libio/filedoalloc.c`

进入到该函数,进行对file_no的检查，应该是防止错误出现

```
if (fp-&gt;_fileno &gt;= 0 &amp;&amp; __builtin_expect (_IO_SYSSTAT (fp, &amp;st), 0) &gt;= 0)
```

这段代码实际执行 `_IO_file_stat`，对应调用系统调用syscall 5 获取对应文件信息 储存在stat中，而st刚好是stat64类型的数据

ps：

关于stat的系统调用，在下面的调试过程中可以体现出作用

示例：

```
int main()`{`

          struct stat m_stat;
 ►        stat("./a.txt",&amp;m_stat);

          printf("%ld\n",m_stat.st_size);
          return 0;
   10 `}`
```

调用初始化之前 对应结构体

[![](https://p0.ssl.qhimg.com/t01e9d712a03aeaaa7b.png)](https://p0.ssl.qhimg.com/t01e9d712a03aeaaa7b.png)

调用stat后

将m_stat 填充

[![](https://p4.ssl.qhimg.com/t0181e83f951a13cec0.png)](https://p4.ssl.qhimg.com/t0181e83f951a13cec0.png)

具体字段含义与本文关联性不大，辅助理解用

psend：

通过stat获取到stdout的文件信息

```
if (fp-&gt;_fileno &gt;= 0 &amp;&amp; __builtin_expect (_IO_SYSSTAT (fp, &amp;st), 0) &gt;= 0)
    `{`
      if (S_ISCHR (st.st_mode))
    `{`
      /* Possibly a tty.  */
      if (
#ifdef DEV_TTY_P
          DEV_TTY_P (&amp;st) ||
#endif
          isatty (fp-&gt;_fileno))
        fp-&gt;_flags |= _IO_LINE_BUF;
    `}`
#if _IO_HAVE_ST_BLKSIZE
      if (st.st_blksize &gt; 0)
    size = st.st_blksize;
#endif
    `}`
```

[![](https://p1.ssl.qhimg.com/t0167bc7c9e8064960f.png)](https://p1.ssl.qhimg.com/t0167bc7c9e8064960f.png)

```
st_mode = 0x2190
```

`(S_ISCHR (st.st_mode))`j宏定义展开为

```
#define    S_ISCHR(mode)     __S_ISTYPE((mode), __S_IFCHR)
#define    __S_IFCHR    0020000    /* 字符设备  */
```

在通过file_no的检查后 设置stdout 的_flag

```
fp-&gt;_flags |= _IO_LINE_BUF;
        #define _IO_LINE_BUF 0x200
```

执行后_flag改变

[![](https://p3.ssl.qhimg.com/t017f0db81b30b38bd0.png)](https://p3.ssl.qhimg.com/t017f0db81b30b38bd0.png)

然后根据获取的文件信息`st` 申请buf的空间 通过调用malloc实现

[![](https://p2.ssl.qhimg.com/t012bbbfa8de816d128.png)](https://p2.ssl.qhimg.com/t012bbbfa8de816d128.png)

size=0x400从 `size = st.st_blksize;`中取出 [![](https://p0.ssl.qhimg.com/t01fb9d1b0f8cf9ca3b.png)](https://p0.ssl.qhimg.com/t01fb9d1b0f8cf9ca3b.png)（合理)

```
# define ALLOC_BUF(_B, _S, _R) \
       do `{`                                      \
      (_B) = (char*)malloc(_S);                          \
      if ((_B) == NULL)                              \
        return (_R);                              \
       `}` while (0)
```

最后在_IO_setb中实现对buf_base与buf_end的填充 参数为malloc申请的chunk初始地址与结束地址

前

：

[![](https://p5.ssl.qhimg.com/t01812e267e2011894a.png)](https://p5.ssl.qhimg.com/t01812e267e2011894a.png)

后

：

[![](https://p5.ssl.qhimg.com/t01b7b8c4b873ce631b.png)](https://p5.ssl.qhimg.com/t01b7b8c4b873ce631b.png)

合理）

随后返回到 `_IO_file_overflow` 进行剩余指针的填充

```
if (f-&gt;_IO_read_ptr == f-&gt;_IO_buf_end)
    f-&gt;_IO_read_end = f-&gt;_IO_read_ptr = f-&gt;_IO_buf_base;
      f-&gt;_IO_write_ptr = f-&gt;_IO_read_ptr;
      f-&gt;_IO_write_base = f-&gt;_IO_write_ptr;
      f-&gt;_IO_write_end = f-&gt;_IO_buf_end;
      f-&gt;_IO_read_base = f-&gt;_IO_read_ptr = f-&gt;_IO_read_end;
        f-&gt;_flags |= _IO_CURRENTLY_PUTTING;
         if (f-&gt;_mode &lt;= 0 &amp;&amp; f-&gt;_flags &amp; (_IO_LINE_BUF+_IO_UNBUFFERED))
            f-&gt;_IO_write_end = f-&gt;_IO_write_ptr;
        #define _IO_CURRENTLY_PUTTING 0x800
```

结果如下

[![](https://p4.ssl.qhimg.com/t0114395181b15288d5.png)](https://p4.ssl.qhimg.com/t0114395181b15288d5.png)

标志位再变[![](https://p2.ssl.qhimg.com/t01779f61458ff76802.png)](https://p2.ssl.qhimg.com/t01779f61458ff76802.png)

```
if (ch == EOF)
    return _IO_new_do_write(f, f-&gt;_IO_write_base,
                f-&gt;_IO_write_ptr - f-&gt;_IO_write_base);
  if (f-&gt;_IO_write_ptr == f-&gt;_IO_buf_end ) /* Buffer is really full */
    if (_IO_do_flush (f) == EOF)
      return EOF;
  *f-&gt;_IO_write_ptr++ = ch;
  if ((f-&gt;_flags &amp; _IO_UNBUFFERED)
      || ((f-&gt;_flags &amp; _IO_LINE_BUF) &amp;&amp; ch == '\n'))
    if (_IO_new_do_write(f, f-&gt;_IO_write_base,
             f-&gt;_IO_write_ptr - f-&gt;_IO_write_base) == EOF)
      return EOF;
  return (unsigned char) ch;
```

接下来 进入 `_IO_new_do_write`，

```
_IO_new_do_write (fp, data, to_do)
     _IO_FILE *fp;
     const char *data;
     _IO_size_t to_do;
`{`
  return (to_do == 0
      || (_IO_size_t) new_do_write (fp, data, to_do) == to_do) ? 0 : EOF;
`}`
```

由于满足to_do == 0 返回到 `_IO_file_xsputn`中，

[![](https://p3.ssl.qhimg.com/t01f174e896b0802a75.png)](https://p3.ssl.qhimg.com/t01f174e896b0802a75.png)

继续运行到调用该函数，参数为stdout 以及传入字符 字符长度 buf区size

在该函数中as通过多次调用`_IO_file_overflow` 将字符写入到缓冲区中，经过第一次的执行

[![](https://p3.ssl.qhimg.com/t017ce2982f02dc019a.png)](https://p3.ssl.qhimg.com/t017ce2982f02dc019a.png)

write_ptr + 1 指向输入的末尾 ，

填充最后的结果

[![](https://p2.ssl.qhimg.com/t01e25e6df66a1c4411.png)](https://p2.ssl.qhimg.com/t01e25e6df66a1c4411.png)

完成后返回到puts函数主体 , puts调用**_overflow , 之后调用** _IO_file_overflow , 调用 _IO_do_write ,

```
_IO_new_do_write (fp, data, to_do)
     _IO_FILE *fp;
     const char *data;
     _IO_size_t to_do;
`{`
  return (to_do == 0
      || (_IO_size_t) new_do_write (fp, data, to_do) == to_do) ? 0 : EOF;
`}`
```

这次的调用进入到 new_do_write中 ，

实际调用到write的syscall，输出,

write系统调用后，在_IO_file_write中将 _IO_write_ptr 复位.

[![](https://p0.ssl.qhimg.com/t01802241ad40e53f2c.png)](https://p0.ssl.qhimg.com/t01802241ad40e53f2c.png)

在这一过程中，write并没有使用file结构体

验证代码如下：

```
int main()`{`
     write(1,"asasd",3);
  `}`
```

##### <a class="reference-link" name="%E8%B0%83%E7%94%A8%E4%B9%8B%E5%89%8D"></a>调用之前

[![](https://p0.ssl.qhimg.com/t012392521691cd75ca.png)](https://p0.ssl.qhimg.com/t012392521691cd75ca.png)

调用之后

[![](https://p3.ssl.qhimg.com/t01648153f38eef711a.png)](https://p3.ssl.qhimg.com/t01648153f38eef711a.png)

前后没有变化，说明write并没有使用该结构体，直接输出。

对puts函数整体的分析到此为止
