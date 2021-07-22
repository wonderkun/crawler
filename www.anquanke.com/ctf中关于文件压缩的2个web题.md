> 原文链接: https://www.anquanke.com//post/id/246722 


# ctf中关于文件压缩的2个web题


                                阅读量   
                                **276377**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t01bdc831b2c1ce0e3c.png)](https://p1.ssl.qhimg.com/t01bdc831b2c1ce0e3c.png)



## [CSCCTF 2019 Final]ZlipperyStillAlive

<a class="reference-link" name="%E9%A2%98%E7%9B%AE%E4%B8%8B%E8%BD%BD%E9%93%BE%E6%8E%A5"></a>题目下载链接

[https://github.com/sturmisch/cscctf-problem/tree/master/2019/final/web/zlippery-still-alive](https://github.com/sturmisch/cscctf-problem/tree/master/2019/final/web/zlippery-still-alive)

<a class="reference-link" name="%E8%BF%99%E4%B8%AA%E9%A2%98%E7%BD%91%E4%B8%8A%E6%B2%A1%E6%9C%89%E6%89%BE%E5%88%B0%E5%85%B7%E4%BD%93%E7%BB%86%E8%8A%82%E7%9A%84wp%EF%BC%8C%E8%80%8C%E4%B8%94%E5%85%B3%E4%BA%8Ego%E7%9A%84web%E9%A2%98%E6%AF%94%E8%BE%83%E5%B0%91%EF%BC%8C%E8%BF%99%E9%87%8C%E8%AE%B0%E5%BD%95%E4%B8%80%E4%B8%8B%EF%BC%8C%E7%9C%8B%E7%9C%8B%E9%A2%98%E7%9B%AE"></a>这个题网上没有找到具体细节的wp，而且关于go的web题比较少，这里记录一下，看看题目

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016ed321b1828fa566.jpg)

<a class="reference-link" name="%E7%9C%8B%E7%9C%8B%E6%BA%90%E7%A0%81%EF%BC%8C%E5%8F%91%E7%8E%B0%E6%9C%892%E4%B8%AA%E8%B7%AF%E7%94%B1%EF%BC%8Cget%E8%AF%B7%E6%B1%82%E7%9A%84%E6%A0%B9%E7%9B%AE%E5%BD%95%EF%BC%8C%E5%92%8Cpost%E8%AF%B7%E6%B1%82%E7%9A%84upload"></a>看看源码，发现有2个路由，get请求的根目录，和post请求的upload

[![](https://p3.ssl.qhimg.com/t01e59971170e3658fc.jpg)](https://p3.ssl.qhimg.com/t01e59971170e3658fc.jpg)

<a class="reference-link" name="%E5%85%88%E6%9D%A5%E7%9C%8B%E7%9C%8Bget%E8%AF%B7%E6%B1%82/%E7%9A%84%E4%BB%A3%E7%A0%81%E5%90%A7%EF%BC%8C%E5%8F%91%E7%8E%B0%E8%B0%83%E7%94%A8%E4%BA%86getServerTime%E8%BF%99%E4%B8%AA%E5%87%BD%E6%95%B0%EF%BC%8C%E7%9C%8B%E7%9C%8B%E8%BF%99%E4%B8%AA%E5%87%BD%E6%95%B0%EF%BC%8C%E5%8F%91%E7%8E%B0%E6%89%A7%E8%A1%8C%E4%BA%86%E4%B8%80%E4%B8%AA%E5%8F%ABtime.sh%E7%9A%84%E8%84%9A%E6%9C%AC%EF%BC%8C%E6%89%80%E4%BB%A5%E5%A6%82%E6%9E%9C%E6%88%91%E4%BB%AC%E5%8F%AF%E4%BB%A5%E8%A6%86%E5%86%99%E8%BF%99%E4%B8%AA%E6%96%87%E4%BB%B6%EF%BC%8C%E9%82%A3%E5%B0%B1%E5%8F%AF%E4%BB%A5%E8%BE%BE%E5%88%B0%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C%EF%BC%8C%E6%89%80%E4%BB%A5%E5%8F%AF%E4%BB%A5%E7%A1%AE%E5%AE%9A%E7%9B%AE%E6%A0%87"></a>先来看看get请求/的代码吧，发现调用了getServerTime这个函数，看看这个函数，发现执行了一个叫time.sh的脚本，所以如果我们可以覆写这个文件，那就可以达到命令执行，所以可以确定目标

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t017b55a89463d9cea6.jpg)

<a class="reference-link" name="%E7%9C%8B%E7%9C%8Bupload%E8%BF%99%E4%B8%AA%E8%B7%AF%E7%94%B1%EF%BC%8C%E5%8F%91%E7%8E%B0%E5%85%81%E8%AE%B8%E4%B8%8A%E4%BC%A0rar%E5%92%8Cpng%E5%92%8Cjpg%E6%96%87%E4%BB%B6%EF%BC%8C%E9%87%8D%E7%82%B9%E6%94%BE%E5%9C%A8rar%EF%BC%8C%E5%A6%82%E6%9E%9C%E5%90%8E%E7%BC%80%E5%90%8D%E4%B8%BArar%E5%B0%B1%E4%BC%9A%E8%B0%83%E7%94%A8extract%E8%BF%99%E4%B8%AA%E5%87%BD%E6%95%B0%E6%8A%8Arar%E6%96%87%E4%BB%B6%E8%A7%A3%E5%8E%8B"></a>看看upload这个路由，发现允许上传rar和png和jpg文件，重点放在rar，如果后缀名为rar就会调用extract这个函数把rar文件解压

[![](https://p0.ssl.qhimg.com/t01ec2479d73369bd86.jpg)](https://p0.ssl.qhimg.com/t01ec2479d73369bd86.jpg)

[![](https://p3.ssl.qhimg.com/t01716a4fb914839e53.jpg)](https://p3.ssl.qhimg.com/t01716a4fb914839e53.jpg)

<a class="reference-link" name="google%E6%9F%A5%E8%AF%A2%E4%BA%86%E4%B8%80%E4%B8%8B%E7%9B%B8%E5%85%B3%E4%BB%A3%E7%A0%81%EF%BC%8C%E5%8F%91%E7%8E%B0%E6%9C%89%E4%B8%AAzip%E7%9A%84slip%E6%BC%8F%E6%B4%9E"></a>google查询了一下相关代码，发现有个zip的slip漏洞

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e53a6c41b1661ddc.jpg)

<a class="reference-link" name="%E5%85%B7%E4%BD%93%E6%90%9C%E7%B4%A2%E8%BF%99%E4%B8%AA%E6%BC%8F%E6%B4%9E%EF%BC%8C%E5%8F%91%E7%8E%B0go%E4%B9%9F%E5%8F%97%E5%BD%B1%E5%93%8D%EF%BC%8C%E5%B9%B6%E4%B8%94rar%E7%AD%89%E5%A4%9A%E7%A7%8D%E5%8E%8B%E7%BC%A9%E6%96%87%E4%BB%B6%E5%8F%97%E5%BD%B1%E5%93%8D%EF%BC%8C%E7%BD%91%E4%B8%8A%E6%9C%89%E7%8E%B0%E6%88%90%E7%9A%84zip%E5%8E%8B%E7%BC%A9%E7%9A%84%E6%9E%84%E9%80%A0%E8%84%9A%E6%9C%AC%EF%BC%8C%E4%BD%86%E6%98%AF%E6%B2%A1%E6%9C%89rar%E7%9A%84%EF%BC%8C%E4%B8%8B%E4%B8%80%E4%B8%AA%E7%9B%AE%E6%A0%87%E5%B0%B1%E6%98%AF%E8%A6%81%E6%90%9E%E6%B8%85%E6%A5%9Arar%E7%9A%84%E4%B8%80%E4%BA%9B%E6%A0%BC%E5%BC%8F%EF%BC%8C%E4%BD%86%E6%98%AFrar%E7%9A%84%E6%96%87%E4%BB%B6%E5%8E%8B%E7%BC%A9%E6%98%AF%E4%B8%8D%E5%BC%80%E6%BA%90%E7%9A%84%EF%BC%8C%E4%BD%86%E6%98%AF%E6%88%91%E4%BB%AC%E5%8F%AF%E4%BB%A5%E4%BB%8Ego%E4%BB%A3%E7%A0%81%E7%9A%84%E4%B8%80%E4%BA%9B%E9%AA%8C%E8%AF%81%E9%87%8C%E9%9D%A2%E8%BF%9B%E8%A1%8C%E7%AA%81%E7%A0%B4"></a>具体搜索这个漏洞，发现go也受影响，并且rar等多种压缩文件受影响，网上有现成的zip压缩的构造脚本，但是没有rar的，下一个目标就是要搞清楚rar的一些格式，但是rar的文件压缩是不开源的，但是我们可以从go代码的一些验证里面进行突破

[![](https://p5.ssl.qhimg.com/t01509f57994123daab.jpg)](https://p5.ssl.qhimg.com/t01509f57994123daab.jpg)

<a class="reference-link" name="linux%E5%92%8Cwindow%E9%83%BD%E4%B8%8D%E5%8F%AF%E4%BB%A5%E4%BB%A5/%E4%B8%BA%E6%96%87%E4%BB%B6%E5%90%8D%EF%BC%8C%E6%89%80%E4%BB%A5%E5%85%88%E5%9C%A8%E6%96%87%E4%BB%B6%E9%87%8C%E9%9D%A2%E5%86%99%E4%B8%8A%E8%AF%BB%E5%8F%96flag%E7%9A%84%E4%BB%A3%E7%A0%81%EF%BC%8C%E7%84%B6%E5%90%8E%E5%8E%8B%E7%BC%A9%E4%B8%BArar%E6%96%87%E4%BB%B6"></a>linux和window都不可以以/为文件名，所以先在文件里面写上读取flag的代码，然后压缩为rar文件

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f1b3fe85a798d448.jpg)

<a class="reference-link" name="%E7%94%A8winhex%E6%89%93%E5%BC%80%E6%8A%8A2%E6%94%B9%E6%88%90/"></a>用winhex打开把2改成/

[![](https://p5.ssl.qhimg.com/t01fd386cd622ca4208.jpg)](https://p5.ssl.qhimg.com/t01fd386cd622ca4208.jpg)

<a class="reference-link" name="%E4%B8%8A%E4%BC%A0%E6%96%87%E4%BB%B6%E5%90%8E%E5%8F%91%E7%8E%B0%E4%BA%86%E6%8A%A5%E9%94%99bad%20header%20crc"></a>上传文件后发现了报错bad header crc

[![](https://p0.ssl.qhimg.com/t01aae215ad5a098e74.jpg)](https://p0.ssl.qhimg.com/t01aae215ad5a098e74.jpg)

<a class="reference-link" name="%E5%8F%82%E8%80%83%E6%BA%90%E7%A0%81%E5%8F%91%E7%8E%B0%E8%B0%83%E7%94%A8%E4%BA%86%E8%BF%99%E4%B8%AArardecode%E8%BF%99%E4%B8%AA%E5%BA%93"></a>参考源码发现调用了这个rardecode这个库

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014845ff1baec32d82.jpg)

<a class="reference-link" name="%E6%89%80%E4%BB%A5%E7%BB%A7%E7%BB%AD%E8%B7%9F%E8%B8%AA%E8%BF%99%E4%B8%AA%E5%BA%93%EF%BC%8C%E7%84%B6%E5%90%8E%E6%90%9C%E7%B4%A2%E8%BF%99%E4%B8%AA%E6%8A%A5%E9%94%99%E7%9A%84%E5%AD%97%E7%AC%A6%E4%B8%B2%E5%8F%91%E7%8E%B0%E4%BA%86%E4%BD%8D%E7%BD%AE"></a>所以继续跟踪这个库，然后搜索这个报错的字符串发现了位置

[![](https://p5.ssl.qhimg.com/t014614d88d22dd6043.jpg)](https://p5.ssl.qhimg.com/t014614d88d22dd6043.jpg)

<a class="reference-link" name="%E5%9C%A8%E7%9C%8B%E7%9C%8B%E5%93%AA%E9%87%8C%E8%B0%83%E7%94%A8%E4%BA%86%E8%BF%99%E4%B8%AA%E9%94%99%E8%AF%AF"></a>在看看哪里调用了这个错误

[![](https://p3.ssl.qhimg.com/t01905f8d6ae365ff85.jpg)](https://p3.ssl.qhimg.com/t01905f8d6ae365ff85.jpg)

<a class="reference-link" name="%E8%BF%99%E9%87%8C%E5%88%A4%E6%96%AD%E4%BA%86crc%E7%9A%84%E5%80%BC%EF%BC%8C%E5%A6%82%E6%9E%9C%E4%B8%8D%E7%AD%89%E4%BA%8E%EF%BC%8C%E5%B0%B1%E6%8A%A5%E9%94%99%EF%BC%8C%E6%89%80%E4%BB%A5%E6%88%91%E4%BB%AC%E7%9A%84%E7%9B%AE%E6%A0%87%E5%B0%B1%E6%98%AF%E7%BB%95%E8%BF%87%E8%BF%99%E4%B8%AA%EF%BC%8C%E4%BD%86%E6%98%AF%E5%85%B7%E4%BD%93%E4%B8%8D%E7%9F%A5%E9%81%93%E4%BB%96%E6%98%AF%E8%AE%A1%E7%AE%97%E7%9A%84%E5%93%AA%E9%87%8C%E7%9A%84crc%E5%80%BC%EF%BC%8C%E6%89%80%E4%BB%A5%E6%88%91%E4%BB%AC%E4%B8%80%E4%BC%9A%E5%86%99%E8%84%9A%E6%9C%AC%E7%88%86%E7%A0%B4"></a>这里判断了crc的值，如果不等于，就报错，所以我们的目标就是绕过这个，但是具体不知道他是计算的哪里的crc值，所以我们一会写脚本爆破

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ac94f9579177d031.jpg)

<a class="reference-link" name="%E6%88%91%E4%BB%AC%E5%9C%A8%E5%88%9B%E5%BB%BA%E4%B8%80%E4%B8%AA..1..1time.sh%E7%9A%84%E6%96%87%E4%BB%B6%EF%BC%8C%E5%B9%B6%E4%B8%94%E5%8E%8B%E7%BC%A9%E4%B8%BArar%E6%96%87%E4%BB%B6%EF%BC%8C%E5%AF%B92%E4%B8%AA%E6%96%87%E4%BB%B6%E8%BF%9B%E8%A1%8C%E5%AF%B9%E6%AF%94"></a>我们在创建一个..1..1time.sh的文件，并且压缩为rar文件，对2个文件进行对比

[![](https://p5.ssl.qhimg.com/t01772d3b7f80dc355c.jpg)](https://p5.ssl.qhimg.com/t01772d3b7f80dc355c.jpg)

<a class="reference-link" name="%E5%8F%91%E7%8E%B0%E5%B0%B1%E5%8F%AA%E6%9C%89%E8%BF%99%E4%B8%AA4%E4%B8%AA%E5%AD%97%E8%8A%82%E4%B8%8D%E5%90%8C%EF%BC%8C%E4%BD%86%E6%98%AF%E6%88%91%E4%BB%AC%E4%B8%8D%E7%9F%A5%E9%81%93%E4%BB%96%E6%98%AF%E8%AE%A1%E7%AE%97%E7%9A%84%E5%93%AA%E4%BA%9B%E5%AD%97%E7%AC%A6%E4%B8%B2%E7%9A%84crc32%E7%9A%84%E5%80%BC%EF%BC%8C%E6%89%80%E4%BB%A5%E5%86%99%E8%84%9A%E6%9C%AC%E7%88%86%E7%A0%B4"></a>发现就只有这个4个字节不同，但是我们不知道他是计算的哪些字符串的crc32的值，所以写脚本爆破

[![](https://p2.ssl.qhimg.com/t01eecef0c29a93467c.jpg)](https://p2.ssl.qhimg.com/t01eecef0c29a93467c.jpg)

<a class="reference-link" name="%E8%BF%99%E9%87%8C%E7%9A%8416%E8%BF%9B%E5%88%B6%E7%9B%B4%E6%8E%A5%E9%87%8Dwinhex%E9%87%8C%E9%9D%A2%E5%A4%8D%E5%88%B6%E5%B0%B1%E8%A1%8C"></a>这里的16进制直接重winhex里面复制就行

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0186f87968b707deba.jpg)

```
import binascii
from zlib import crc32
s='526172211A0701003392B5E50A01050600050101808000C1CCD15B2902030B900004900020E57A05988000000D2E2E312E2E3174696D652E73680A0302A5263B1FFA2BD601746163202F6574632F7370617274616E1D77565103050400'
for x in range(len(binascii.a2b_hex(s))):
    for y in range(x+1,len(binascii.a2b_hex(s))):
        if '5b' in hex(crc32(binascii.a2b_hex(s)[x:y])) and 'c1' in hex(crc32(binascii.a2b_hex(s)[x:y])):
            print(x,y,hex(crc32(binascii.a2b_hex(s)[x:y])))
```

<a class="reference-link" name="%E7%88%86%E7%A0%B4%E5%87%BA%E6%9D%A5%E5%8F%91%E7%8E%B0%E6%98%AF%E7%AC%AC27%E4%BD%8D%E5%88%B0%E7%AC%AC69%E4%BD%8D"></a>爆破出来发现是第27位到第69位

[![](https://p5.ssl.qhimg.com/t015f2d24dfa5e4f92f.jpg)](https://p5.ssl.qhimg.com/t015f2d24dfa5e4f92f.jpg)

<a class="reference-link" name="%E6%89%80%E4%BB%A5%E5%8F%96%E5%87%BA%E7%AC%AC27%E5%88%B0%E7%AC%AC69%EF%BC%8C%E7%84%B6%E5%90%8E%E4%BF%AE%E6%94%B9%E5%86%85%E5%AE%B9%E8%AE%A1%E7%AE%97crc32%E7%9A%84%E5%80%BC%EF%BC%8C%E4%BF%AE%E6%94%B9%E6%88%90%E8%AE%A1%E7%AE%97%E5%87%BA%E6%9D%A5%E7%9A%84%E5%80%BC"></a>所以取出第27到第69，然后修改内容计算crc32的值，修改成计算出来的值

[![](https://p3.ssl.qhimg.com/t0126569b30ab831a84.jpg)](https://p3.ssl.qhimg.com/t0126569b30ab831a84.jpg)

<a class="reference-link" name="%E7%84%B6%E5%90%8E%E4%B8%8A%E4%BC%A0"></a>然后上传

[![](https://p2.ssl.qhimg.com/t01ba8a5abf366f222d.jpg)](https://p2.ssl.qhimg.com/t01ba8a5abf366f222d.jpg)

<a class="reference-link" name="%E5%9B%9E%E5%9C%B0%E5%BC%80%E5%A7%8B%E7%95%8C%E9%9D%A2%E5%88%B7%E6%96%B0%E5%B0%B1%E4%BC%9A%E6%89%A7%E8%A1%8C%E9%82%A3%E4%B8%AA%E8%A6%86%E5%86%99%E7%9A%84time.sh%E7%9A%84%E8%84%9A%E6%9C%AC"></a>回地开始界面刷新就会执行那个覆写的time.sh的脚本

[![](https://p5.ssl.qhimg.com/t01e89bcd4219d8c6bc.jpg)](https://p5.ssl.qhimg.com/t01e89bcd4219d8c6bc.jpg)



## tctf2021的1linephp

题目的代码很简单，可惜这个phpinfo是个静态的phpinfo.html，不然可以尝试一下临时缓存文件的利用，所以只有通过session的文件上传包含了。题目是有zip拓展的(通过phpinfo.html可以发现)，结合之前的文件包含的学习总结，可以知道后缀名限制时可以用`zip://t.zip#t.php`和`phar://a.phar/a.php`，但是phar的文件包含的条件比较苛刻，第一个就是文件必须有后缀名，但是我们通过session构造上传的文件是没有后缀名的，所以就得想办法利用zip了

```
&lt;?php
($_=@$_GET['yxxx'].'.php') &amp;&amp; @substr(file($_)[0],0,6) === '@&lt;?php' ? include($_) : highlight_file(__FILE__) &amp;&amp; include('phpinfo.html');
```

<a class="reference-link" name="%E5%80%9F%E7%94%A8%E7%BB%B4%E5%9F%BA%E7%99%BE%E7%A7%91%E4%B8%8A%E9%9D%A2zip%E6%96%87%E4%BB%B6%E4%B8%BA%E5%8D%95%E6%96%87%E4%BB%B6%E6%97%B6%E7%9A%84%E7%BB%93%E6%9E%84%E5%9B%BE%EF%BC%8C%E5%8F%AF%E4%BB%A5%E6%98%8E%E6%98%BE%E7%9A%84%E7%9C%8B%E5%88%B0%E5%89%8D26%E5%AD%97%E8%8A%82%E5%9F%BA%E6%9C%AC%E4%B8%8A%E6%98%AF%E4%B8%80%E4%BA%9B%E5%9F%BA%E7%A1%80%E4%BF%A1%E6%81%AF%EF%BC%8C%E4%B8%80%E8%88%AC%E6%98%AF%E7%94%A8%E4%BA%8E%E6%A0%A1%E9%AA%8C%E7%94%A8%E7%9A%84"></a>借用维基百科上面zip文件为单文件时的结构图，可以明显的看到前26字节基本上是一些基础信息，一般是用于校验用的

[![](https://p1.ssl.qhimg.com/t01f857e12ff3924e39.png)](https://p1.ssl.qhimg.com/t01f857e12ff3924e39.png)

先看看php的文档上面正常打开zip文件的操作，先是选择了`ZipArchive::CHECKCONS`的模式进行了检查，检查通过后就用`stream_get_contents`读取了文件内容，最后进行了crc的校验

[![](https://p0.ssl.qhimg.com/t01297fe7064feed5c6.png)](https://p0.ssl.qhimg.com/t01297fe7064feed5c6.png)

<a class="reference-link" name="%E6%9D%A5%E7%9C%8B%E7%9C%8B%E5%BA%95%E5%B1%82ZipArchive%E7%9A%84open%E6%96%B9%E6%B3%95%EF%BC%8C%E6%8E%A5%E5%8F%972%E4%B8%AA%E5%8F%82%E6%95%B0%EF%BC%8C%E7%AC%AC%E4%BA%8C%E4%B8%AAflags%E5%B0%B1%E6%98%AF%E6%89%93%E5%BC%80%E6%97%B6%E5%90%AF%E7%94%A8%E7%9A%84%E6%A8%A1%E5%BC%8F"></a>来看看底层ZipArchive的open方法，接受2个参数，第二个flags就是打开时启用的模式

[![](https://p5.ssl.qhimg.com/t019e598deefb09a746.png)](https://p5.ssl.qhimg.com/t019e598deefb09a746.png)

那么`ZipArchive::CHECKCONS`其实就是`ZIP_CHECKCONS`，`ZIP_CHECKCONS`是什么就可以看看libzip里面的声明了

[![](https://p5.ssl.qhimg.com/t017593fbb33ca781e9.png)](https://p5.ssl.qhimg.com/t017593fbb33ca781e9.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e1ee5fb8d57439d6.png)

然后看看官网的libzip的说明，也就是说如果是`ZIP_CHECKCONS`的模式打开才会进行魔数这些东西的检查，结合之前维基百科的zip单文件压缩结构图，真正对读取文件起作用的就是第26个字节后关于文件的描述

[![](https://p1.ssl.qhimg.com/t0105c10120546c3e99.png)](https://p1.ssl.qhimg.com/t0105c10120546c3e99.png)

然后我们看看php底层通过数据流打开时的代码，可以发现php通过zip的数据流打开时是没有进行验证的，就直接调用了`zip_open`函数，但是打开的方式是`ZIP_CREATE`，这个模式是不会检测文件的，然后通过`zip_fopen`打开要读取的zip文件

`php_stream_zip_opener`

[![](https://p2.ssl.qhimg.com/t01ecc52b9c7291a588.png)](https://p2.ssl.qhimg.com/t01ecc52b9c7291a588.png)

然后看看libzip的源码的`zip_open`怎么写的吧，`zip_open_from_source`函数就是针对我们传入的模式进行创建数据流

[![](https://p4.ssl.qhimg.com/t013ee67c214eea5e73.png)](https://p4.ssl.qhimg.com/t013ee67c214eea5e73.png)

<a class="reference-link" name="%E7%9B%B4%E6%8E%A5%E7%9C%8B%E7%9C%8B%E5%87%BD%E6%95%B0%E8%B0%83%E7%94%A8%E9%93%BE%E5%88%B0%E5%85%B3%E9%94%AE%E5%9C%B0%E6%96%B9%E5%90%A7"></a>直接看看函数调用链到关键地方吧

[![](https://p4.ssl.qhimg.com/t0117eeb0333ffa3207.png)](https://p4.ssl.qhimg.com/t0117eeb0333ffa3207.png)

[![](https://p5.ssl.qhimg.com/t0134dd3bbf29dac96c.png)](https://p5.ssl.qhimg.com/t0134dd3bbf29dac96c.png)

&lt;a name=”这里是对魔数进行了检测匹配的，但是匹配的是`504b0506`，而没有匹配的文件头” class=”reference-link”&gt;这里是对魔数进行了检测匹配的，但是匹配的是`504b0506`，而没有匹配的文件头

[![](https://p2.ssl.qhimg.com/t01570d1fe63a888746.png)](https://p2.ssl.qhimg.com/t01570d1fe63a888746.png)

但是如果是`ZIP_CHECKCONS`模式就会进入`_zip_checkcons`，这个函数就是zip的格式检查函数，所以可以通过`ZIP_CREATE`的模式打开的就不会进入`_zip_checkcons`

[![](https://p4.ssl.qhimg.com/t01416ac17e9d2bacec.png)](https://p4.ssl.qhimg.com/t01416ac17e9d2bacec.png)

<a class="reference-link" name="%E5%8F%AF%E4%BB%A5%E7%9C%8B%E7%9C%8B%E4%BB%96%E6%A3%80%E6%9F%A5%E7%9A%84%E4%B8%BB%E8%A6%81%E5%86%85%E5%AE%B9"></a>可以看看他检查的主要内容

[![](https://p0.ssl.qhimg.com/t017f0844bdcf648f59.png)](https://p0.ssl.qhimg.com/t017f0844bdcf648f59.png)

[![](https://p2.ssl.qhimg.com/t01a80a851ee9e67349.png)](https://p2.ssl.qhimg.com/t01a80a851ee9e67349.png)

<a class="reference-link" name="%E6%89%80%E4%BB%A5%E6%88%91%E4%BB%AC%E7%9B%AE%E6%A0%87%E5%B0%B1%E5%BE%88%E6%98%8E%E7%A1%AE%E4%BA%86%EF%BC%8C%E5%8F%AA%E8%A6%81%E8%AF%BB%E5%8F%96%E6%96%87%E4%BB%B6%E7%9A%84%E5%85%B3%E9%94%AE%E4%BD%8D%E7%BD%AE%E5%81%8F%E7%A7%BB%E4%B8%8D%E5%8F%98%EF%BC%8C%E9%82%A3%E4%B9%88%E5%B0%B1%E5%8F%AF%E4%BB%A5%E6%88%90%E5%8A%9F%E8%AF%BB%E5%8F%96%E6%96%87%E4%BB%B6%EF%BC%8C%E6%89%80%E4%BB%A5%E5%8F%AA%E9%9C%80%E8%A6%81%E5%88%A0%E9%99%A4%E6%9E%84%E9%80%A0%E7%9A%84zip%E7%9A%84%E5%8D%95%E6%96%87%E4%BB%B6%E7%9A%84%E5%89%8D16%E5%AD%97%E8%8A%82%EF%BC%8C%E5%9C%A8%E9%85%8D%E5%90%88zip%E5%8D%8F%E8%AE%AE%E8%BF%9B%E8%A1%8C%E5%8C%85%E5%90%AB%E5%B0%B1%E8%A1%8C"></a>所以我们目标就很明确了，只要读取文件的关键位置偏移不变，那么就可以成功读取文件，所以只需要删除构造的zip的单文件的前16字节，在配合zip协议进行包含就行

[![](https://p3.ssl.qhimg.com/t01c4fcbf534d693ef0.png)](https://p3.ssl.qhimg.com/t01c4fcbf534d693ef0.png)

[![](https://p3.ssl.qhimg.com/t01f5e0b3d120d34756.png)](https://p3.ssl.qhimg.com/t01f5e0b3d120d34756.png)

<a class="reference-link" name="%E7%84%B6%E5%90%8E%E9%80%9A%E8%BF%87bp%E8%BF%9B%E8%A1%8C%E6%9D%A1%E4%BB%B6%E7%AB%9E%E4%BA%89%EF%BC%8C%E5%8C%85%E5%90%ABsession%E7%9A%84%E4%B8%B4%E6%97%B6%E6%96%87%E4%BB%B6%E5%90%8E%E5%86%99%E5%85%A5%E4%B8%80%E5%8F%A5%E8%AF%9D%EF%BC%8C%E5%BE%97%E5%88%B0flag"></a>然后通过bp进行条件竞争，包含session的临时文件后写入一句话，得到flag

[![](https://p2.ssl.qhimg.com/t01e10cfebd94698b3d.png)](https://p2.ssl.qhimg.com/t01e10cfebd94698b3d.png)

[![](https://p4.ssl.qhimg.com/t017a77d9a277a40086.png)](https://p4.ssl.qhimg.com/t017a77d9a277a40086.png)

[![](https://p3.ssl.qhimg.com/t01ab7e344508331b80.png)](https://p3.ssl.qhimg.com/t01ab7e344508331b80.png)

[![](https://p5.ssl.qhimg.com/t013fdcab3bf14ce53e.png)](https://p5.ssl.qhimg.com/t013fdcab3bf14ce53e.png)
