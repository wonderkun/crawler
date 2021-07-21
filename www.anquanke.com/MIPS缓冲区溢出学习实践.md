> 原文链接: https://www.anquanke.com//post/id/158174 


# MIPS缓冲区溢出学习实践


                                阅读量   
                                **183436**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                    



## 前言

之前在学习家用路由器这本书以及看网上大佬写相关文章 的时候,总感觉有些关键细节一笔带过,有时候给我造成了很大的困扰,鉴于这个原因,我想到把自己的一些思考以及实际操作经验写出来给后来者,希望他们不要再走我走过的弯路。



## 引爆内存崩溃

首先看源代码:

```
#include &lt;stdio.h&gt;
#include &lt;sys/stat.h&gt;
#include &lt;unistd.h&gt;

void do_system(int code,char *cmd)
`{`
    char buf[255];
    //sleep(1);
    system(cmd);
`}`

void main()
`{`
    char buf[256]=`{`0`}`;
    char ch;
    int count = 0;
    unsigned int fileLen = 0;
    struct stat fileData;
    FILE *fp;

    if(0 == stat("passwd",&amp;fileData))
        fileLen = fileData.st_size;
    else
        return 1;

    if((fp = fopen("passwd","rb")) == NULL)
    `{`
        printf("Cannot open file passwd!n");
        exit(1);
    `}`


    ch=fgetc(fp);
    while(count &lt;= fileLen)
    `{`
        buf[count++] = ch;
        ch = fgetc(fp);
    `}`
    buf[--count] = 'x00';

    if(!strcmp(buf,"adminpwd"))
    `{`
        do_system(count,"ls -l");
    `}`
    else
    `{`
        printf("you have an invalid password!n");
    `}`
    fclose(fp);
`}`
```

将vuln_system.c 拷贝至对应目录下:

[![](https://p3.ssl.qhimg.com/t01ca254ae8ccc1a7a8.png)](https://p3.ssl.qhimg.com/t01ca254ae8ccc1a7a8.png)

执行如下命令:

```
root@ricard-virtual-machine:~/my_file# /root/my_file/buildroot1/buildroot/output/host/bin/mips-linux-gcc vuln_system.c -static -o vuln_system

root@ricard-virtual-machine:~/my_file# python -c "print 'A'*600"&gt;passwd

root@ricard-virtual-machine:~/my_file# qemu-mips vuln_system
```

而后会出现错误:

[![](https://p5.ssl.qhimg.com/t01b9f9ae3b12348ecf.png)](https://p5.ssl.qhimg.com/t01b9f9ae3b12348ecf.png)

程序引发了一段故障,使用如下命令重新执行:

```
root@ricard-virtual-machine:~/my_file# qemu-mips vuln_system `python -c "print 'A'*600"`
```

[![](https://p2.ssl.qhimg.com/t014f103281fd0c96ef.png)](https://p2.ssl.qhimg.com/t014f103281fd0c96ef.png)

这里直接运行，发生崩溃就退出了;

加-g是等待调试的:

```
root@ricard-virtual-machine:~/my_file# qemu-mips -g 1234 ./vuln_system `python -c "print 'A'*600"`
```

[![](https://p4.ssl.qhimg.com/t012f8401605bc1e9ae.png)](https://p4.ssl.qhimg.com/t012f8401605bc1e9ae.png)

执行完这条指令之后,使用IDA进行附加调试:

[![](https://p3.ssl.qhimg.com/t01003060058de2ab75.png)](https://p3.ssl.qhimg.com/t01003060058de2ab75.png)

[![](https://p1.ssl.qhimg.com/t01bee0e2c486345210.png)](https://p1.ssl.qhimg.com/t01bee0e2c486345210.png)

[![](https://p0.ssl.qhimg.com/t01cfe42ab998b90609.png)](https://p0.ssl.qhimg.com/t01cfe42ab998b90609.png)

[![](https://p0.ssl.qhimg.com/t0183a88992d47544ed.png)](https://p0.ssl.qhimg.com/t0183a88992d47544ed.png)

[![](https://p4.ssl.qhimg.com/t01029c0bf9362d74dd.png)](https://p4.ssl.qhimg.com/t01029c0bf9362d74dd.png)

这里选择大端是因为这个文件是mips大端格式的;

[![](https://p4.ssl.qhimg.com/t01a87ff82c239bb022.png)](https://p4.ssl.qhimg.com/t01a87ff82c239bb022.png)

附加之后,在IDA里面按F9键(书里面写的是F5,,这是错的!)可以看到程序在试图执行0x41414141的时候崩溃了,如下图所示:

[![](https://p1.ssl.qhimg.com/t01bdfa6a9822c61f2a.png)](https://p1.ssl.qhimg.com/t01bdfa6a9822c61f2a.png)

[![](https://p4.ssl.qhimg.com/t01d27dfb4098dbc3a1.png)](https://p4.ssl.qhimg.com/t01d27dfb4098dbc3a1.png)

这是因为0x41414141将原来的返回地址给覆盖了,程序在返回的时候返回的是0x41414141这个无效地址而不是原来的地址,故会崩溃.



## 劫持流程

### <a class="reference-link" name="%E8%AE%A1%E7%AE%97%E5%81%8F%E7%A7%BB"></a>计算偏移

通过阅读vuln_system.c的源码可以知道,main函数里面，在读取完passwd这个文件之后,将passwd文件里面的所有数据存入堆栈的局部变量buf里面,而buf的大小仅为256字节,而passwd文件有600字节大小的数据写入buf,导致了缓冲区溢出;

通过静态分析发现,如果要使缓冲区溢出,并控制到堆栈中的返回地址saved_ra,需要覆盖的数据大小应该达到0x1A0-0x04即0x19c字节;作者这里运用这个公式的依据是什么呢?让我们回顾一下X86架构下的情形:

偏移不就是找buf和ra之间的偏移么,ra是存储于栈里面的(有点类似于x86里面的ret指令),buf指向栈里面,只要计算出buf的初始位置和ra之间的偏移,就可以计算出有多少个字节就可以溢出到ra了！

### <a class="reference-link" name="%E5%AF%BB%E6%89%BE%E5%81%8F%E7%A7%BB"></a>寻找偏移

[![](https://p1.ssl.qhimg.com/t01eb22152621629171.png)](https://p1.ssl.qhimg.com/t01eb22152621629171.png)

上图是主函数里面的一开始的部分,为了进一步分析出偏移,笔者将相关汇编指令誊写并注释如下:

```
addiu   $sp, -0x1D0            //sp &lt;==sp-0x1D0
                 sw      $ra, 0x1D0+var_4($sp)    //将ra里面的值存放于堆栈里面,其偏移值为0x1D0+var_4
                sw      $fp, 0x1D0+var_8($sp)        //将fp里面的值存放于堆栈里面,其偏移为0x1D0+var_8
                move    $fp, $sp                    //fp&lt;== sp

                li      $gp, 0x4291A0                //li指令:将一个立即数存放于寄存器里面
                sw      $gp, 0x1D0+var_1C0($sp)    //将gp里面的值存放于堆栈里面,其偏移为0x1D0+var_1C0
                addiu   $v0, $fp, 0x1D0+var_1A0    //v0用于存放函数函数返回值
                li      $v0, 0x100                //将立即数0x100传入v0
                move    $a2, $v1                    //MIPS架构中一般使用a0-a3作为函数的前4个参数
                move    $a1, $zero                //zero寄存器里面永远为0
                move    $a0, $v0                    //a0=v0
                la      $v0, memset                //复制memset地址至至v0中
                move    $t9, $v0                    //$t0-$t9供汇编程序使用的临时变量
                bal     memset                    //无条件转移,并且将转移指令后面的第二条地址作为返回值存放于Ra里面
                nop
```

结合源代码看,可以发现主函数里面调用的第一个函数为memset函数,貌似源代码里面没有这个函数,怎么回事,继续看,发现在调用这个函数之前是调用了3个参数的,分别用到a0,a1,和a2这几个寄存器,(在MIPS架构里面,是用a0-a3这几个寄存器来传参的)，而函数memset的原型为`void* memset(void* s,int ch,unsigned n)`，其主要功能为:在内存空间里以s为起始的地方,将开始的n个字节设为指定值;可以发现传给a2的值为v1,而传给$v1的为0x100(0x100实际上就是十进制256),分析到这里,大家应该会清晰了吧,这里在做的事情其实是内存初始化,通过这个函数将内存里面的256个字节初始化为0,而这里的内存初始地址是通过指令`addiu $v0,$fp,0x1D0+var_1A0`来确定的,显然,`0x1D0+var_1A0`就是我们要找的buf的起始偏移，到这里,我们才能确定:需要覆盖的数据大小应该为0x1D0+var_1A0-0x1D0-var_4即0x19c字节;

### <a class="reference-link" name="%E9%AA%8C%E8%AF%81"></a>验证

```
root@ricard-virtual-machine:~/my_file# python -c "print 'A'*0x19c + 'BBBB'+'CCCC'"&gt;passwd
​
root@ricard-virtual-machine:~/my_file# qemu-mips -g 1234 vuln_system
​
```

[![](https://p2.ssl.qhimg.com/t01683c16d6558b6624.png)](https://p2.ssl.qhimg.com/t01683c16d6558b6624.png)

输入指令之后,程序就会处于等待调试的状态; 而后利用IDA附加该进程(此过程在前面已经叙述过);

由于这里使用附加调试的效果不是太好,我这里使用的运行时调试的方法,读者可以参考这本书即可;

[![](https://p4.ssl.qhimg.com/t01301f1429e954798a.png)](https://p4.ssl.qhimg.com/t01301f1429e954798a.png)

在主函数结尾的地方下断点,按F9运行程序,会在0x004006CC这个地址断下:

[![](https://p5.ssl.qhimg.com/t016a63b63560acc633.png)](https://p5.ssl.qhimg.com/t016a63b63560acc633.png)

双击0x004006D0这行;来到返回地址在栈空间0x40800104(也可以利用SP+0x1D0+VAR_4得到)处,如下图 所示:

[![](https://p0.ssl.qhimg.com/t01ab72904fdd3ab820.png)](https://p0.ssl.qhimg.com/t01ab72904fdd3ab820.png)

查看HEX VIEW-1窗口,发现返回地址已经被覆盖为0x42424242,如下图所示,此时缓冲区已经被输入的数据所覆盖,并且越界后覆盖了堆栈上的其他数据;

[![](https://p0.ssl.qhimg.com/t017f54987694816973.png)](https://p0.ssl.qhimg.com/t017f54987694816973.png)

继续按F8键执行指令jr $ra,程序就会跳往0x42424242出执行,如下图所示:

[![](https://p1.ssl.qhimg.com/t01173fdd0ba9890e8b.png)](https://p1.ssl.qhimg.com/t01173fdd0ba9890e8b.png)

[![](https://p5.ssl.qhimg.com/t012cd2469d8a210059.png)](https://p5.ssl.qhimg.com/t012cd2469d8a210059.png)



## 小结

在这一节里面,主要学习的知识点是如何计算偏移达到覆盖返回地址的目的,这里总结出一个公式:

偏移=函数返回地址-缓冲区首地址;

(注:在堆栈中,一般函数返回地址处于高地址,缓冲区地址处于低地址),今天就暂时写到这里,后面有时间我会带来更多的分享.
