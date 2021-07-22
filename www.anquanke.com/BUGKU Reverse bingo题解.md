> 原文链接: https://www.anquanke.com//post/id/227393 


# BUGKU Reverse bingo题解


                                阅读量   
                                **139593**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t010c74ceac2c101329.jpg)](https://p0.ssl.qhimg.com/t010c74ceac2c101329.jpg)



题目下载后得到一张图片

[![](https://p4.ssl.qhimg.com/t01bbf81cc3eb5473f3.png)](https://p4.ssl.qhimg.com/t01bbf81cc3eb5473f3.png)

刚开始的时候没看分类，以为是 MISC 题，然后找了半天隐写内容，都没做找到，但是这个文件这么大，肯定是有问题。

然后又仔细找了一下，结果发现了这样一段内容，

[![](https://p1.ssl.qhimg.com/t01c145ea986558b7e9.png)](https://p1.ssl.qhimg.com/t01c145ea986558b7e9.png)

看上去内容好像是 EXE 程序中才会有的，于是看了一下分类，好家伙，原来是 re 题。

百度了一下 png 文件尾

PNG (png)，

文件头：89504E47 文件尾：AE 42 60 82

搜索 AE 42 60 82

[![](https://p2.ssl.qhimg.com/t016573615177231bfe.png)](https://p2.ssl.qhimg.com/t016573615177231bfe.png)

这不就是熟悉的 MZ 文件头吗，用 010 Editor 提取出这一段内容。

并重命名为 bingo.exe

[![](https://p4.ssl.qhimg.com/t01efb594d7dd954b75.png)](https://p4.ssl.qhimg.com/t01efb594d7dd954b75.png)

结果报错了，随便找了一个 exe 文件，比对文件内容是否确实，发生少了 PE 文件头标识。

[![](https://p1.ssl.qhimg.com/t0183bf1f5de771bba6.png)](https://p1.ssl.qhimg.com/t0183bf1f5de771bba6.png)

补上这一段内容。

[![](https://p5.ssl.qhimg.com/t01e94102ed3b94b2b5.png)](https://p5.ssl.qhimg.com/t01e94102ed3b94b2b5.png)

数据补上后直接打开运行，发现可以显示黑框，但是运行后直接退出，于是打开 IDA 分析一下

[![](https://p4.ssl.qhimg.com/t019334738fe2b8a146.png)](https://p4.ssl.qhimg.com/t019334738fe2b8a146.png)

ida 打开后似乎认不出来文件的其他内容，动态调试后发现这一段内容会出现异常的情况。

```
pusha
mov     ecx, 3E000h
mov     ebx, 1000h
mov     ebx, 400000h
add     ebx, edx
xor     byte ptr [ebx], 22h
inc     ebx
popa
jmp     loc_408BE0
```

原因是 edx 的内容也是 400xxxh，相加之后到了 800xxx，超出了范围。<br>
这里不知道是作者预期还是怎么的，反正应该是这个解密函数出现了问题。

但是看到这里应该就是一个 xor 解密 (xor 0x22)，所以直接在外部解密吧。

编写解密脚本：

```
#define MAXKEY 5000
#define MAXFILE 1000
#include &lt;cstdio&gt;
#include &lt;cstring&gt;
using namespace std;
int main()
`{`
    char xor_key[MAXKEY], file_dir[MAXFILE];
    char* buf;
    //printf("xor key: ");
    //scanf("%s", xor_key);
    xor_key[0] = 0x22;
    xor_key[1] = 0;
    printf("file: ");
    scanf("%s", file_dir);
    FILE* fp = fopen(file_dir, "rb");
    strcat(file_dir, ".xor");
    FILE* fpw = fopen(file_dir, "wb+");
    if (fp &amp;&amp; fpw)
    `{`
        fseek(fp, 0, SEEK_END);
        size_t size = ftell(fp);
        fseek(fp, 0, SEEK_SET);
        buf = new char[size];
        fread(buf, sizeof(char), size, fp);
        for (size_t i = 0, keySize = strlen(xor_key); i &lt; size; i++)
            buf[i] ^= xor_key[i % keySize];
        fwrite(buf, sizeof(char), size, fpw);
    `}`
    if (fp) fclose(fp);
    if (fpw) fclose(fpw);
    return 0;
`}`
```

解密文件后，得到文件**bingo.exe.xor**，观察文件信息，发现实际上只有**.text**段进行了异或加密，其他内容都没有加密。<br>
从文件中大量的 0x22 内容也可以看出来 (因为 0x00 ^ 0x22 = 0x22)

[![](https://p3.ssl.qhimg.com/t01fc54665d4b549c87.png)](https://p3.ssl.qhimg.com/t01fc54665d4b549c87.png)

从 0xCC 就可以知道，应该是解密对了，因为 0xCC 对应的是 INT3 断点，也就是当段未初始化的时候，vs debug 模式下会赋值的内容。vs 中的烫烫烫也是这么来的。

替换.text 段的内容。

[![](https://p0.ssl.qhimg.com/t0144cc95b34903673a.png)](https://p0.ssl.qhimg.com/t0144cc95b34903673a.png)

替换后得到的 exe 程序，直接运行当然还是不可以的，但是可以放到 ida 中解析各个函数了。

但是没有任何的符号信息，难以阅读。所以我还是打算调整程序让其可以正常运行。

打开 ida 后，定位到 start 处

[![](https://p0.ssl.qhimg.com/t01f6546d2f50cf19e8.png)](https://p0.ssl.qhimg.com/t01f6546d2f50cf19e8.png)

直接用 Keypatch（ida 插件）进行修改，让其直接跳到程序真正的入口点 (jmp sub_408BE0)。

[![](https://p2.ssl.qhimg.com/t0170bd8a3a4000dcca.png)](https://p2.ssl.qhimg.com/t0170bd8a3a4000dcca.png)

修改后进行保存

[![](https://p0.ssl.qhimg.com/t01753c697b3c0e544c.png)](https://p0.ssl.qhimg.com/t01753c697b3c0e544c.png)

发现程序以及可以成功运行。

重新载入后发现，接下来发现程序的符号信息就有了。

[![](https://p2.ssl.qhimg.com/t01b6dc70bb4955e3f4.png)](https://p2.ssl.qhimg.com/t01b6dc70bb4955e3f4.png)

可以看出，程序对输入内容进行加密后与程序中 off_443DC0 (zaciWjV!Xm [_XSqeThmegndq) 进行比对。

[![](https://p5.ssl.qhimg.com/t01c711334cc5611d1a.png)](https://p5.ssl.qhimg.com/t01c711334cc5611d1a.png)

这里的加密方法就是对你输入值 (c) 进行平方，然后再加上一个参数 (b)，最后解出来 a。

满足关系式: a^2 + b^2 = c^2。

本来以为直接解密就好了，没想到这里还有一个函数_strrev (v6);

他的作用是把字符串信息倒置，所以最后显示的顺序也会变换。

由于这里 sqrt 还有个精度问题，我这里就不进行逆运算了，也就是

c = sqrt(a^2 + b^2)

直接编写程序爆破 c 的内容。

解密程序

```
#include &lt;cstdio&gt;
#include &lt;algorithm&gt;
#include &lt;string.h&gt;
using namespace std;
int main()
`{`
    char s[] = "zaciWjV!Xm[_XSqeThmegndq";
    char e[] = "                        ";
    char* v6 = (char*)operator new(strlen(s) + 1);
    memset(v6, 0, strlen(s) + 1);
    for (int i = 0; i &lt; strlen(s); i++)
    `{`
        v6[i] = 'a' + i;
        _strrev(v6);
    `}`
    for (int i = 0; i &lt; strlen(s); i++) e[v6[i] - 'a'] = s[i];
    printf("%s\n", v6);
    printf("%s\n", e);
    int a2 = 0x34;
    for (int i = 0; i &lt; strlen(s); ++i)
    `{`
        for (char t = 1; t &lt; 0xFF; t++)
        `{`
            int v2 = (signed __int64)pow((double)a2, 2.0);
            signed int v3 = (unsigned __int64)(signed __int64)pow((double)t, 2.0);
            v3 -= v2;
            v6[i] = (signed __int64)(sqrt((double)v3) + 0.5);
            if (v6[i] == e[i])
            `{`
                printf("%c", t);
                break;
            `}`
        `}`
        --a2;
    `}`
    return 0;
`}`
```

运行后可以得到：flag `{`woc_6p_tql_moshifu`}`
