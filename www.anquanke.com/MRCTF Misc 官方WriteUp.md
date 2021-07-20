> 原文链接: https://www.anquanke.com//post/id/237901 


# MRCTF Misc 官方WriteUp


                                阅读量   
                                **124044**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t01858976994a7e1fcd.jpg)](https://p1.ssl.qhimg.com/t01858976994a7e1fcd.jpg)



## Real Checkin

在 QQ 群中 [@bot](https://github.com/bot) checkin 得到一串 Base64，其中有零宽字符隐写<br>
使用 [https://github.com/offdev/zwsp-steg-js](https://github.com/offdev/zwsp-steg-js) 的工具可以得到 `ECB QQID 0RPADDING`<br>
提示为 ECB 模式，QQ 号为密钥，密钥填充方式为在最后加 `\0`<br>
使用 CyberChef 来 AES 解密，把 QQ 号当作 hex，并在最后加 `\0`，即可解出 flag



## 0&amp;1 check_in

这题本意是给校内同级出的，结果没人做出。只有一个学长做出来了。<br>
这题来源于数字逻辑的实验<br>
利用 Quartus 看到 vmf 然后一路搜索就行。<br>
就可以找到 Quartus 了。<br>
可以自己生成一份 vmf 文件，发现给出的删掉了注释和一个 HEADER<br>
补一个 HEADER 就可以正常打开了。<br>
然后这个波形图是一个 3-8 译码器<br>
挨个对应就可以解出了<br>
24 个 01 对应一个汉字——爬<br>
MRCTF`{`爬`}`



## plane

打开 StegSolve 查看不同 plane 下的图片，发现 `BluePlane7` 有异样，形成了鲜明的行分层

[![](https://p4.ssl.qhimg.com/t01641e5cc0654b05c5.png)](https://p4.ssl.qhimg.com/t01641e5cc0654b05c5.png)

每个分层为 8 行，可以联想到是一种字符编码的映射，只要找到对应的 0 和 1 就能成功解码

`BluePlane7` 是用 `plane:2z-255=0` 将整个(R,G,B)给分开，上为白点，下为黑点。经过一次尝试，发现不能成功解码，说明是一个近似 `plane:2z-255=0`，但不完全相同的 plane

而题目名字 `(153, 15, 120),(51, 104, 132),(229, 38, 115).png` 也描述了一个 `plane:721x-402y+9110z-1197483=0`，通过这个 plane 将整个色素域给分开，上为白点，下为黑点

```
from PIL import Image
from random import randint
import base64

def minus(a, b):
    l = len(a)
    v = []
    for i in range(l):
        v.append(a[i] - b[i])
    return v
def rp(k):
    while 1:
        r = [randint(0, 0x100), randint(0, 0x100), randint(0, 0x100)]
        ra = minus(r, a)
        if face(ra, vec) == k:
            return tuple(r)
def judge(v):
    va = minus(v, a)
    return face(va, vec)==1
def p2vec(a, b, c):
    ba = minus(b, a)
    ca = minus(c, a)
    v = [0, 0, 0]
    for i in range(3):
        v[i] = ba[i-2]*ca[i-1] - ba[i-1]*ca[i-2]
    return v
def face(a, b):
    ans = 0
    for i in range(3):
        ans += a[i] * b[i]
    if ans &gt; 0:
        return 1
    elif ans == 0:
        return -1
    else:
        return 0

global vec
global a
a = (153, 15, 120)
b = (51, 104, 132)
c = (229, 38, 115)
vec = p2vec(a, b, c)
print vec
flag = ''

im = Image.open('(153, 15, 120),(51, 104, 132),(229, 38, 115).png')
pim = im.load()

for i in range(400):
    for j in range(50):
        ch = 0
        for k in range(8):
            if judge(pim[i,j*8+k]) == 1:
                ch |= 1 &lt;&lt; k
        flag += chr(ch)
flag = flag.strip('a')
while 1:
    try:
        flag = base64.b64decode(flag)
    except:
        break
print flag
```

解码后发现是个 base64 字符串，解码即可



## My Secret

流量包里可以看到有 TCP 和 USB 流量<br>
用 tshark 命令把 USB 流量全部 dump 下来

```
tshark -r data.pcapng -T fields -e usb.capdata &gt; usb.txt
```

hex 解一下码<br>
可以在里面找到 v2rayN 的配置文件<br>
其中最重要的是这一串：

```
"tag": "proxy",
"protocol": "shadowsocks",
"settings": `{`
"servers": [
  `{`
    "address": "47.94.202.168",
    "method": "aes-256-gcm",
    "ota": false,
    "password": "db6c73af3d8585c",
    "port": 8888,
    "level": 1
  `}`
]
```

可以推断出 TCP 流量是用 Shadowsocks 传输的<br>
而且服务器 IP、密码和加密方式也已经给出

在 [https://github.com/shadowsocks/shadowsocks/tree/master](https://github.com/shadowsocks/shadowsocks/tree/master) 可以找到 Shadowsocks 3.0.0 的源代码（以下的版本不支持 aes-256-gcm 模式）<br>
把源码下载下来，在 shadowsocks/cryptor.py 的 Cryptor 类里可以找到解密函数：

[![](https://p1.ssl.qhimg.com/t0182cea6dea8f981e2.jpg)](https://p1.ssl.qhimg.com/t0182cea6dea8f981e2.jpg)

把服务器传给客户端的 TCP 流量 dump 下来，存储在 tcp.txt 中<br>
把 Shadowsocks 安装好<br>
然后调用解密函数即可：

```
from shadowsocks import cryptor

with open('tcp.txt', 'rb') as f:
    encrypted_data = f.read()
c = cryptor.Cryptor('db6c73af3d8585c', 'aes-256-gcm')
data = c.decrypt(encrypted_data)

with open('tcp2.txt', 'wb') as f:
    f.write(data)
```

可以找到 RAR 压缩包，里面是 2500 块不规则的拼图，并且顺序也被打乱<br>
首先就是先找到拼图原本的顺序

使用 exiftool 看以下图片的 exif，可以发现每个图片都有经纬度<br>
经纬度均为南纬和东经，且经度和纬度都是从 0 度到 49 度

稍微想象一下，就能明白经纬度代表的是坐标<br>
经度是 x 轴坐标，纬度是 y 轴坐标，且拼图的左上角是原点

写脚本来给拼图重命名：

```
import os
import piexif
from PIL import Image

file = os.listdir('jigsaw')

def calc_file(x, y):
    num = str(y * 50 + x).zfill(4)
    return f'jigsaw/`{`num`}`.png'

for i in file:
    img = Image.open(f'jigsaw/`{`i`}`')
    exif_dict = piexif.load(img.info['exif'])
    img.close()
    latitude = exif_dict['GPS'][piexif.GPSIFD.GPSLatitude]
    longtitude = exif_dict['GPS'][piexif.GPSIFD.GPSLongitude]
    y = latitude[0][0]
    x = longtitude[0][0]
    file = calc_file(x, y)
    os.rename(f'jigsaw/`{`i`}`', file)
```

顺序已经找回，下面就是拼图了<br>
每个图片的大小为 100×100<br>
锯齿的大小为 20×20<br>
所以原图片的大小为 60×60

这里我写了一个比较复杂的拼图脚本，但好在比较容易想出来<br>
（而且容易根据构造拼图时写的脚本改出来）

```
from PIL import Image
from tqdm import tqdm

x_sum = 50
y_sum = 50
ori_width = 60
ori_height = 60
jigsaw_width = 20

width = ori_width + jigsaw_width * 2
height = ori_height + jigsaw_width * 2

def calc_file(x, y):
    num = str(y * x_sum + x).zfill(4)
    return f'jigsaw/`{`num`}`.png'

def check_info(file):
    img_info = [0, 0, 0, 0]
    img = Image.open(file)
    pix_out1 = img.getpixel((width // 2, 0))[3]
    pix_out2 = img.getpixel((width - 1, height // 2))[3]
    pix_out3 = img.getpixel((width // 2, height - 1))[3]
    pix_out4 = img.getpixel((0, height // 2))[3]
    pix_out = [pix_out1, pix_out2, pix_out3, pix_out4]
    pix_in1 = img.getpixel((width // 2, jigsaw_width))[3]
    pix_in2 = img.getpixel((width - jigsaw_width - 1, height // 2))[3]
    pix_in3 = img.getpixel((width // 2, height - jigsaw_width - 1))[3]
    pix_in4 = img.getpixel((jigsaw_width, height // 2))[3]
    pix_in = [pix_in1, pix_in2, pix_in3, pix_in4]
    for i in range(4):
        if pix_out[i] == 0 and pix_in[i] == 0:
            img_info[i] = -1
        elif pix_out[i] != 0 and pix_in[i] != 0:
            img_info[i] = 1
        elif pix_out[i] == 0 and pix_in[i] != 0:
            img_info[i] = 0
        else:
            raise Exception("Invalid jigsaw!", file)
    return img_info

def init_table():
    info_table = []
    for y in range(y_sum):
        row_info = []
        for x in range(x_sum):
            file = calc_file(x, y)
            img_info = check_info(file)
            row_info.append(img_info)
        info_table.append(row_info)
    return info_table

def cut(direction, file):
    if direction == 0:
        left_top_x = (ori_width - jigsaw_width) // 2 + jigsaw_width
        left_top_y = 0
    elif direction == 1:
        left_top_x = ori_width + jigsaw_width
        left_top_y = (ori_height - jigsaw_width) // 2 + jigsaw_width
    elif direction == 2:
        left_top_x = (ori_width - jigsaw_width) // 2 + jigsaw_width
        left_top_y = ori_height + jigsaw_width
    elif direction == 3:
        left_top_x = 0
        left_top_y = (ori_height - jigsaw_width) // 2 + jigsaw_width

    right_bottom_x = left_top_x + jigsaw_width
    right_bottom_y = left_top_y + jigsaw_width
    img = Image.open(file)
    cut_img = img.crop((left_top_x, left_top_y, right_bottom_x, right_bottom_y))
    blank_img = Image.new('RGBA', (jigsaw_width, jigsaw_width), (0, 0, 0, 0))
    img.paste(blank_img, (left_top_x, left_top_y))
    img.save(file)
    return cut_img

def paste(direction, file, cut_img):
    if direction == 0:
        left_top_x = (ori_width - jigsaw_width) // 2 + jigsaw_width
        left_top_y = jigsaw_width
    elif direction == 1:
        left_top_x = ori_width
        left_top_y = (ori_height - jigsaw_width) // 2 + jigsaw_width
    elif direction == 2:
        left_top_x = (ori_width - jigsaw_width) // 2 + jigsaw_width
        left_top_y = ori_height
    elif direction == 3:
        left_top_x = jigsaw_width
        left_top_y = (ori_height - jigsaw_width) // 2 + jigsaw_width

    img = Image.open(file)
    img.paste(cut_img, (left_top_x, left_top_y))
    img.save(file)

def recover_jigsaw(info_table):
    for y in tqdm(range(y_sum)):
        for x in range(x_sum):
            img_info = info_table[y][x]
            for direction in range(4):
                if img_info[direction] != 'free':
                    file = calc_file(x, y)

                    if direction == 0:
                        x2 = x
                        y2 = y - 1
                        file2 = calc_file(x2, y2)
                        direction2 = 2
                    elif direction == 1:
                        x2 = x + 1
                        y2 = y
                        file2 = calc_file(x2, y2)
                        direction2 = 3
                    elif direction == 2:
                        x2 = x
                        y2 = y + 1
                        file2 = calc_file(x2, y2)
                        direction2 = 0
                    elif direction == 3:
                        x2 = x - 1
                        y2 = y
                        file2 = calc_file(x2, y2)
                        direction2 = 1

                    if img_info[direction] == 1:
                        cut_img = cut(direction, file)
                        paste(direction2, file2, cut_img)
                    elif img_info[direction] == -1:
                        cut_img = cut(direction2, file2)
                        paste(direction, file, cut_img)
                    info_table[y2][x2][direction2] = 'free'
                    img_info[direction] = 'free'

def remove_border(file):
    img = Image.open(file)
    new_img = img.crop((jigsaw_width, jigsaw_width, width - jigsaw_width, height - jigsaw_width))
    new_img.save(file)

if __name__ == '__main__':
    info_table = init_table()
    recover_jigsaw(info_table)
    for i in range(x_sum * y_sum):
        file = 'jigsaw/' + str(i).zfill(4) + '.png'
        remove_border(file)
```

还原之后用 montage 命令把 2500 张拼到一起

```
montage jigsaw/*.png -tile 50x50 -geometry 60x60+0+0 out.png
```

然后扫二维码得到 flag



## SeeAndFindMe

本题涉及到目前 CPython 的安全漏洞，详情请看 issue track，由于漏洞尚未修复，此处就暂不给出本题做法
