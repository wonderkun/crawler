> 原文链接: https://www.anquanke.com//post/id/241319 


# 从buu到红帽的图片隐写


                                阅读量   
                                **250314**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t019aff352ad1493b58.png)](https://p0.ssl.qhimg.com/t019aff352ad1493b58.png)



## 恢复黑白图片

### <a class="reference-link" name="buuoj%20%E9%9D%99%E9%9D%99%E5%90%AC%E8%BF%99%E4%B9%88%E5%A5%BD%E5%90%AC%E7%9A%84%E6%AD%8C"></a>buuoj 静静听这么好听的歌

由于网上wp只给了代码而且函数非常吓人，因此我写了一个新手版的wp。

以下是源码，注释是我自己加的。(因为不是很熟悉matlab代码因此特意详细分析了这一道题目)。代码逻辑是什么呢？非常简单。
- 先打开BGM.wav文件然后再打开img文件，通过设置一个flag值(这里是44,也可以任意修改,当flag值为5时会破坏文件头结构(不过也没什么关系，反正隐写后文件都打不开)，因此一般设置稍高一点)。
- 当拿到img的二维数组后，将其转为一维数组wi。
- 把wi数组通过for循环写入BGM.wav文件中。
加密脚本：

```
fid=fopen('BGM.wav','rb');
%此处的inf表示无穷大，表示取尽wav文件。
a=fread(fid,inf,'uchar');
%为什么这里是44?只是一个标志性数字可以当做hint使用.
n=length(a)-44;
fclose(fid);
img=imread('flag.bmp');
[row,col]=size(img);
%二维数组转换为一维数组
%388*100的二维数组img被转换为38800*1的一维数组wi
wi=img(:);
if row*col&gt;n
 error('文件太小');
end

%watermarkedaudio即为隐写文件(文件大小有限制)
watermarkedaudio=a;
%需要lsb隐写的长度
watermarklength=row*col;
%循环插入低位。不使用文件的前44个字节。
for k=1:row*col
 watermarkedaudio(44+k)=bitset(watermarkedaudio(44+k),1,wi(k));
end

figure;
subplot(2,1,1);plot(a);
subplot(2,1,2);plot(watermarkedaudio);
%将修改后的字节写入wav文件
fid = fopen('2.wav', 'wb');
fwrite(fid,watermarkedaudio,'uchar');
fclose(fid);
```

那么我们来思考一下，当我们已经成功拿到了该wav文件的加密脚本，对于解密脚本该如何编写呢？

首先读取该文件。对于标志位44我们要循环读取对应的低位数字并还原为img数组。那么要完成这个操作我们需要数组长度，也就是上面的38800。我们该如何得到宽高呢？

[![](https://p5.ssl.qhimg.com/t01b89fb1dccf090ee9.png)](https://p5.ssl.qhimg.com/t01b89fb1dccf090ee9.png)

属实是一个脑洞呢。然后需要去爆破高度值或者猜测。

这里我们就假设已经知道了宽高为388*100吧。

然后我们去读取45-38845的低位值并转换为二维数组。函数：

```
function A=convert(oi,row,col)
    %创建一个二维空数组
    A = zeros(row,col);
    for i=1:row
        for j=1:col
            A(i,j) = oi((i-1)*col+j);
        end
    end
end
```

那么现在就开始编写解密脚本吧。

```
clc;
clear;

row = 388;
col = 100;
marklength = row*col;
imgData = [0]*marklength;

wavFile = fopen('静静听这么好听的歌.wav','rb');
data = fread(wavFile,inf,'uchar');
for i=45:marklength+45
    imgData(i-44) = bitget(data(i),1);
end
%拿到一维数组后进行转换
img = convert(imgData,row,col);
imwrite(img,'flag.bmp');
imshow('flag.bmp');
title('extracted watermark');
```

[![](https://p0.ssl.qhimg.com/t010858c8b1e2f95bae.png)](https://p0.ssl.qhimg.com/t010858c8b1e2f95bae.png)

同时可以看到生成了flag.bmp文件了。

[![](https://p1.ssl.qhimg.com/t010560dc7486f006ce.png)](https://p1.ssl.qhimg.com/t010560dc7486f006ce.png)

这里保留一个疑问?我们这里输出的是一幅黑白图。那如果是一幅彩色图的话我们这种解密方法还是可以使用吗？

关键点在该语句。

```
imgData(i-44) = bitget(data(i),1);
```

我们首先将data(i)转为二进制数字然后取1位(最后一位)。那么需要考虑什么呢？若我们的wav文件中存在大量FF的hex代码时，我们是无法使用该隐写方法的。同时在此条件下我们只能写黑白图片。

[https://blog.csdn.net/zrools/article/details/50630780](https://blog.csdn.net/zrools/article/details/50630780)

### <a class="reference-link" name="%E5%BD%A9%E8%89%B2%E8%BD%AC%E9%BB%91%E7%99%BD%E5%9B%BE"></a>彩色转黑白图

对于这道题的学习不止于此。当我考虑是否能够编写出一个隐写彩色图的方法时。

编写了一个能把彩色图变为黑白图的脚本。

(调整255为其他值可以调整色度)

```
clc;
clear;

img = imread('test.png');

[row,col] = size(img);
for i=1:row
    for j=1:col
        if img(i,j)~=0
        %调整255为其他值可以调整色度
            img(i,j)=255;
        end
    end
end

imwrite(img,"test-output.bmp");
```



## 恢复RGB图片思路

matlab读取RGB图片代码。

test.png是一张420*560的彩色图片，我们用于实验。

```
[x,img] = imread('test.png');
imshow(x,img);
```

那么x和img分别是什么呢？

[![](https://p1.ssl.qhimg.com/t0104126abb4077af43.png)](https://p1.ssl.qhimg.com/t0104126abb4077af43.png)

[![](https://p1.ssl.qhimg.com/t0133a6b78096977a72.png)](https://p1.ssl.qhimg.com/t0133a6b78096977a72.png)

注意到x是420*560的,很明显这是我们的像素点，而这个数值代表着索引。

[![](https://p4.ssl.qhimg.com/t010df50a1cf58e16bc.png)](https://p4.ssl.qhimg.com/t010df50a1cf58e16bc.png)

可以看到img数组是一个256*3的数组，是RGB数组，通过x的索引对应相应的RGB值。拿到对应的RGB值后我们就能恢复我们的彩色图像了。

那么现在思路很清晰了。如果我们要进行彩色图像的隐写，只要需要两个文件。一个是索引文件，一个是RGB数组文件。突然发现红帽做过一样的题目，可能也是我这个出题思路？(可惜了，本来想出题的)。

### <a class="reference-link" name="%E7%BA%A2%E5%B8%BD%E6%9D%AF"></a>红帽杯

索引文件：data1。

[![](https://p1.ssl.qhimg.com/t019263938ec6688581.png)](https://p1.ssl.qhimg.com/t019263938ec6688581.png)

RGB数组：data2。然后我们把这里的hex代码分为三个一组为RGB值。

[![](https://p1.ssl.qhimg.com/t01bcfe66fa1ccfa5f3.png)](https://p1.ssl.qhimg.com/t01bcfe66fa1ccfa5f3.png)

网上有很多wp，这里不再说了。

至于宽高是通过质数分解得到的。共有7067个索引，因此分解为37*191。

[http://tools.jb51.net/jisuanqi/factor_calc](http://tools.jb51.net/jisuanqi/factor_calc)

以下为解密的python脚本。之前读到过一篇文章。学习图像处理时matlab十分方便，但是我们需要继续深入学习时也该深入以下python的图像处理，感触颇深。至于matlab代码可以在网上自行寻找。

```
from PIL import Image

f1 = open('data1','r')
f2 = open('data2','rb')

pic = Image.new("RGB",(37,191),(255,255,255))

pocLis = f1.read()
arrs = f2.read()

pocLis = pocLis.split(' ')

r = []
for i in range(len(arrs)//3):
    rgbTemp = arrs[i*3:i*3+3]
    RGB = rgbTemp[0],rgbTemp[1],rgbTemp[2]
    r.append((RGB))

for i in range(37):
    for j in range(191):
        rgb = r[int(pocLis[i*191+j])]
        pic.putpixel((int(i),int(j)),rgb)
        pic.save('flag.png')
```
