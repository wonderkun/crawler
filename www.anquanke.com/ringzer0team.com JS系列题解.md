> 原文链接: https://www.anquanke.com//post/id/97730 


# ringzer0team.com JS系列题解


                                阅读量   
                                **152161**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t0135e6c96a9c050258.jpg)](https://p0.ssl.qhimg.com/t0135e6c96a9c050258.jpg)

## 前言

ringzer0team.com是一个在线的CTF挑战平台，其中包含了前后端、逆向、编程、隐写、查证等多方面的题目，此次所写的writeup针对其中JavaScript系列题所做。



## 题解

## Client side validation is so secure?

### <a class="reference-link" name="%E9%A2%84%E8%A7%88"></a>预览

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01cbb570d89e77562c.png)

### <a class="reference-link" name="%E8%A7%A3%E9%A2%98%E8%BF%87%E7%A8%8B"></a>解题过程

映入眼帘的是一个登陆框，随意输入账号密码可看到`Wrong password sorry.`的提示，且未有流量产生，由此可知是通过js判断账号密码的，并未向服务器发送查询请求。<br>
因此我们拦截鼠标点击事件，为了避免jQuery之类的js影响，我们将jQuery和其他不必要的js文件加入blackbox，然后重新测试登陆。<br>
点击后程序断在了这一块。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d888a3a354267a6f.png)

```
// Look's like weak JavaScript auth script :)
$(".c_submit").click(function(event) `{`
    event.preventDefault()
    var u = $("#cuser").val();
    var p = $("#cpass").val();
    if(u == "admin" &amp;&amp; p == String.fromCharCode(74,97,118,97,83,99,114,105,112,116,73,115,83,101,99,117,114,101)) `{`
        if(document.location.href.indexOf("?p=") == -1) `{`   
            document.location = document.location.href + "?p=" + p;
        `}`
    `}` else `{`
        $("#cresponse").html("&lt;div class='alert alert-danger'&gt;Wrong password sorry.&lt;/div&gt;");
    `}`
`}`);
```

我们可以看到，其中有一条判断语句，正是其分支产生了错误提示：

```
if(u == "admin" &amp;&amp; p == String.fromCharCode(74,97,118,97,83,99,114,105,112,116,73,115,83,101,99,117,114,101))
```

其中u来自id为cuser的文本框，p来自id为cpass的文本框，我们运行一下，即可得到密码：

[![](https://p0.ssl.qhimg.com/t01056fe4d19edc983a.png)](https://p0.ssl.qhimg.com/t01056fe4d19edc983a.png)

提交即可得到flag<br>[Link](https://ringzer0team.com/challenges/27)



## Is hashing more secure?

### <a class="reference-link" name="%E9%A2%84%E8%A7%88"></a>预览

### [![](https://p3.ssl.qhimg.com/t01113ac6377648e751.png)](https://p3.ssl.qhimg.com/t01113ac6377648e751.png)解题过程

同样的，我们设置click事件断点，获取到相关验证代码如下：

```
// Look's like weak JavaScript auth script :)
$(".c_submit").click(function(event) `{`
    event.preventDefault();
    var p = $("#cpass").val();
    if(Sha1.hash(p) == "b89356ff6151527e89c4f3e3d30c8e6586c63962") `{`
        if(document.location.href.indexOf("?p=") == -1) `{`   
            document.location = document.location.href + "?p=" + p;
        `}`
    `}` else `{`
        $("#cresponse").html("&lt;div class='alert alert-danger'&gt;Wrong password sorry.&lt;/div&gt;");
    `}`
`}`);
```

很显然，我们只要让`Sha1.hash(p) == "b89356ff6151527e89c4f3e3d30c8e6586c63962"`一句成立即可，查相关解密站点可知其明文为`adminz`，提交即可得到flag<br>[Link](https://ringzer0team.com/challenges/30)



## Then obfuscation is more secure?

### <a class="reference-link" name="%E9%A2%84%E8%A7%88"></a>预览

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01c9da1c1a226c5aa1.png)

### <a class="reference-link" name="%E8%A7%A3%E9%A2%98%E8%BF%87%E7%A8%8B"></a>解题过程

设置断点后，程序停在了第83行，js代码被压缩成一行，格式化后如下

```
var _0xc360 = ["x76x61x6C", "x23x63x70x61x73x73", "x61x6Cx6Bx33", "x30x32x6Cx31", "x3Fx70x3D", "x69x6Ex64x65x78x4Fx66", "x68x72x65x66", "x6Cx6Fx63x61x74x69x6Fx6E", "x3Cx64x69x76x20x63x6Cx61x73x73x3Dx27x65x72x72x6Fx72x27x3Ex57x72x6Fx6Ex67x20x70x61x73x73x77x6Fx72x64x20x73x6Fx72x72x79x2Ex3Cx2Fx64x69x76x3E", "x68x74x6Dx6C", "x23x63x72x65x73x70x6Fx6Ex73x65", "x63x6Cx69x63x6B", "x2Ex63x5Fx73x75x62x6Dx69x74"];
$(_0xc360[12])[_0xc360[11]](function () `{`
    var _0xf382x1 = $(_0xc360[1])[_0xc360[0]]();
    var _0xf382x2 = _0xc360[2];
    if (_0xf382x1 == _0xc360[3] + _0xf382x2) `{`
        if (document[_0xc360[7]][_0xc360[6]][_0xc360[5]](_0xc360[4]) == -1) `{`
            document[_0xc360[7]] = document[_0xc360[7]][_0xc360[6]] + _0xc360[4] + _0xf382x1;
        `}`;
    `}` else `{`
        $(_0xc360[10])[_0xc360[9]](_0xc360[8]);
    `}`;
`}`);
```

程序使用了大量的编码进行混淆，不过与前两题相同，在第5行有一个明显的判断语句，我们在第五行的位置设置断点，运行查看一下变量。

[![](https://p4.ssl.qhimg.com/t01aacfcd46d0e5de96.png)](https://p4.ssl.qhimg.com/t01aacfcd46d0e5de96.png)

可以看到，实际上就是判断输入的值与`02l1alk3`是否相同，将`02l1alk3`作为密码输入，提交即可得到flag<br>[Link](https://ringzer0team.com/challenges/31)



## Why not?

### <a class="reference-link" name="%E9%A2%84%E8%A7%88"></a>预览

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t014b5f331814767156.png)

### <a class="reference-link" name="%E8%A7%A3%E9%A2%98%E8%BF%87%E7%A8%8B"></a>解题过程

拦截到验证代码如下

```
// Look's like weak JavaScript auth script :)
$(".c_submit").click(function(event) `{`
    event.preventDefault();
    var k = new Array(176,214,205,246,264,255,227,237,242,244,265,270,283);
    var u = $("#cuser").val();
    var p = $("#cpass").val();
    var t = true;

    if(u == "administrator") `{`
        for(i = 0; i &lt; u.length; i++) `{`
            if((u.charCodeAt(i) + p.charCodeAt(i) + i * 10) != k[i]) `{`
                $("#cresponse").html("&lt;div class='alert alert-danger'&gt;Wrong password sorry.&lt;/div&gt;");
                t = false;
                break;
            `}`
        `}`
    `}` else `{`
        $("#cresponse").html("&lt;div class='alert alert-danger'&gt;Wrong password sorry.&lt;/div&gt;");
        t = false;
    `}`
    if(t) `{`
        if(document.location.href.indexOf("?p=") == -1) `{`
            document.location = document.location.href + "?p=" + p;
               `}`
    `}`
`}`);
```

显然，我们要使`u == "administrator"`为真且`(u.charCodeAt(i) + p.charCodeAt(i) + i * 10) != k[i]`为假，则用户名为`administrator`，至于密码，则是要求用户名的ascii和密码的ascii相加，再加上位权，与k对应值相等，根据判断代码，有解密代码如下

```
var u = "administrator", z = "", k = new Array(176,214,205,246,264,255,227,237,242,244,265,270,283);
for(i = 0; i &lt; u.length; i++) `{`
    z += String.fromCharCode(k[i] - i * 10 - u.charCodeAt(i));
`}`
console.log(z);
```

运行代码得到密码，提交即可得到flag<br>[Link](https://ringzer0team.com/challenges/34)



## Valid key required

### <a class="reference-link" name="%E9%A2%84%E8%A7%88"></a>预览

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0150fd1bc403ddb27f.png)

### <a class="reference-link" name="%E8%A7%A3%E9%A2%98%E8%BF%87%E7%A8%8B"></a>解题过程

设置断点

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0167767d586b98f159.jpg)

点击提交后，程序断在了这里

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01aae5b5a7663852d8.jpg)

跟进去之后方法如下

```
function validatekey()
`{`
    e = false;
    var _strKey = "";
    try `{`
        _strKey = document.getElementById("key").value;
        var a = _strKey.split("-");
        if(a.length !== 5)
            e = true;

        var o=a.map(genFunc).reduceRight(callback, new (genFunc(a[4]))(Function));

        if(!equal(o,ref))
            e = true;

    `}`catch(e)`{`
        e = true;
    `}`

    if(!e) `{`
        if(document.location.href.indexOf("?p=") == -1) `{`
            document.location = document.location.href + "?p=" + _strKey;
           `}`
    `}` else `{`
        $("#cresponse").html("&lt;div class='alert alert-danger'&gt;Wrong password sorry.&lt;/div&gt;");
    `}`   
`}`
```

输入的字串由`-`进行分割为数组，要求分割后的数组长度为5，随后使用`genFunc`方法映射。我们跟进`genFunc`方法

```
function genFunc(_part) `{`
    if(!_part || !(_part.length) || _part.length !== 4)
        return function() `{``}`;

    return new Function(_part.substring(1,3), "this." + _part[3] + "=" + _part.slice(1,3) + "+" + (fn(function(y)`{`return y&lt;=57`}`)(_part.charCodeAt(0)) ?  _part[0] : "'"+ _part[0] + "'"));
`}`
```

`genFunc`方法要求满足传入参数不为空且长度为4，否则返回一个空的方法。<br>
这表示，key为`xxxx-xxxx-xxxx-xxxx-xxxx`这样一串序列。<br>
同时使用黑盒和白盒审计的方式往往能加快解决问题的效率，我们经过测试，发现最终只是将输入序列字串的位置进行了更改，那么我们就不再继续分析具体算法了。<br>
输入`abcd-efgh-ijkl-mnop-qrst`，然后将断点设在`if(!equal(o,ref))`这里，重新点击提交，单步进入。<br>
跟进equal方法之后，可以看到chrome打印出了传入的o和o1两个参数，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01cd60777cd3bc7ead.jpg)

那么我们直接将被处理过后的字串复制出来，按位置替换后即可得到密码。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f759665ac539d662.jpg)

提交即可得到flag<br>[Link](https://ringzer0team.com/challenges/58)



## Most Secure Crypto Algo

### <a class="reference-link" name="%E9%A2%84%E8%A7%88"></a>预览

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0164b7f26d8fe2a6d4.png)

### <a class="reference-link" name="%E8%A7%A3%E9%A2%98%E8%BF%87%E7%A8%8B"></a>解题过程

设置click断点后，程序停在了这一块

```
$(".c_submit").click(function(event) `{`
    event.preventDefault();
    var k = CryptoJS.SHA256("x93x39x02x49x83x02x82xf3x23xf8xd3x13x37");
    var u = $("#cuser").val();
    var p = $("#cpass").val();
    var t = true;

    if(u == "x68x34x78x30x72") `{`
        if(!CryptoJS.AES.encrypt(p, CryptoJS.enc.Hex.parse(k.toString().substring(0,32)), `{` iv: CryptoJS.enc.Hex.parse(k.toString().substring(32,64)) `}`) == "ob1xQz5ms9hRkPTx+ZHbVg==") `{`
            t = false;
        `}`
    `}` else `{`
        $("#cresponse").html("&lt;div class='alert alert-danger'&gt;Wrong password sorry.&lt;/div&gt;");
        t = false;
    `}`
    if(t) `{`
        if(document.location.href.indexOf("?p=") == -1) `{`
            document.location = document.location.href + "?p=" + p;
               `}`
    `}`
`}`);
```

代码将指定字符串用sha256计算一遍，赋值给k，然后进入判断用户名。<br>
我们将代码段选中运行一下

[![](https://p0.ssl.qhimg.com/t0152ab9552618b24b3.jpg)](https://p0.ssl.qhimg.com/t0152ab9552618b24b3.jpg)

返回值为`h4x0r`，也就是说要求用户名为`h4x0r`。<br>
然后将密码部分使用AES进行加密，将运算结果与`ob1xQz5ms9hRkPTx+ZHbVg==`进行比较。<br>
加密流程大致如下
- p作为参数1(消息)
- k转为字符串→取其前32位→使用`CryptoJS.enc.Hex.parse`方法处理，作为参数2(密钥)
- k转为字符串→取第33-64位→使用`CryptoJS.enc.Hex.parse`方法处理，作为参数3(密钥向量)
- 使用以上参数进行AES加密
根据以上信息，我们得到了密文，密钥，密钥向量，四者得到三者，则可得到明文。<br>
我们使用`CryptoJS`自带的解密方法进行解密

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b32634437e728466.jpg)

运行结果为HEX编码，解码提交即可得到flag<br>[Link](https://ringzer0team.com/challenges/67)



## Why not be more secure?

### <a class="reference-link" name="%E9%A2%84%E8%A7%88"></a>预览

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0189b377207f3022d9.png)

### <a class="reference-link" name="%E8%A7%A3%E9%A2%98%E8%BF%87%E7%A8%8B"></a>解题过程

关键代码如下

```
// Look's like weak JavaScript auth script :)
$(".c_submit").click(function(event) `{`
    event.preventDefault();
    var u = $("#cpass").val();
    var k = $("#cuser").val();
    var func = "x2Bx09x4Ax03x49x0Fx0Ex14x15x1Ax00x10x3Fx1Ax71x5Cx5Bx5Bx00x1Ax16x38x06x46x66x5Ax55x30x0Ax03x1Dx08x50x5Fx51x15x6Bx4Fx19x56x00x54x1Bx50x58x21x1Ax0Fx13x07x46x1Dx58x58x21x0Ex16x1Fx06x5Cx1Dx5Cx45x27x09x4Cx1Fx07x56x56x4Cx78x24x47x40x49x19x0Fx11x1Dx17x7Fx52x42x5Bx58x1Bx13x4Fx17x26x00x01x03x04x57x5Dx40x19x2Ex00x01x17x1Dx5Bx5Cx5Ax17x7Fx4Fx06x19x0Ax47x5Ex51x59x36x41x0Ex19x0Ax53x47x5Dx58x2Cx41x0Ax04x0Cx54x13x1Fx17x60x50x12x4Bx4Bx12x18x14x42x79x4Fx1Fx56x14x12x56x58x44x27x4Fx19x56x49x16x1Bx16x14x21x1Dx07x05x19x5Dx5Dx47x52x60x46x4Cx1Ex1Dx5Fx5Fx1Cx15x7Ex0Bx0Bx00x49x51x5Fx55x44x31x52x45x13x1Bx40x5Cx46x10x7Cx38x10x19x07x55x13x44x56x31x1Cx15x19x1Bx56x13x47x58x30x1Dx1Bx58x55x1Dx57x5Dx41x7Cx4Dx4Bx4Dx49x4F";
    buf = "";
    if(k.length == 9) `{`
        for(i = 0, j = 0; i &lt; func.length; i++) `{`
            c = parseInt(func.charCodeAt(i));
            c = c ^ k.charCodeAt(j);
            if(++j == k.length) `{`
                j = 0;
            `}`
            buf += eval('"' + a(x(c)) + '"');
        `}`
        eval(buf);
    `}` else `{`
        $("#cresponse").html("&lt;div class='alert alert-danger'&gt;Wrong password sorry.&lt;/div&gt;");
    `}`
`}`);

function a(h) `{`
    if(h.length != 2) `{`
        h = "x30" + h;
    `}`
    return "x5cx78" + h;
`}`

function x(d) `{`
    if(d &lt; 0) `{`
        d = 0xFFFFFFFF + d + 1;
    `}`
    return d.toString(16).toUpperCase();
`}`
```

可以看到，我们输入的密码，也就是变量u，实际上并没有被用上，目前真正参与计算的是用户名。<br>
当用户名长度为9时，其将用户名与预定义的一串字符进行系列运算，从而得到一个新字符串，然后将得到的字符串看作js代码执行。<br>
我们继续向下看。

```
for(i = 0, j = 0; i &lt; func.length; i++) `{`
    c = parseInt(func.charCodeAt(i));
    c = c ^ k.charCodeAt(j);
    if(++j == k.length) `{`
        j = 0;
    `}`
    buf += eval('"' + a(x(c)) + '"');
`}`
```

以k为密码，将func字符串进行xor运算。<br>
将运算得到的字符带入x方法中，将该返回值再带入到a方法中。<br>
我们跟进看x方法。

```
function x(d) `{`
    if(d &lt; 0) `{`
        d = 0xFFFFFFFF + d + 1;
    `}`
    return d.toString(16).toUpperCase();
`}`
```

显然`d&lt;0`不太可能成立，x方法将传入值转为16进制，然后返回，我们再跟进a方法。

```
function a(h) `{`
    if(h.length != 2) `{`
        h = "x30" + h;
    `}`
    return "x5cx78" + h;
`}`
```

也就是说，当传入参数小于两个字符时，将在其前方填充`"x30"`即字符`0`，随后统一填充`"x5cx78"`即`x`，将该值返回，因此，实际上返回值也就是`x11` `x01` 之类。<br>
而buf为用户名k与预定义字符串func进行异或运算所产生的明文，实际上是一串js代码。由于js代码属于文本，可读性非常高，由此可大范围缩减密码的范围。<br>
对于异或运算，令`a ^ b = c`，则有`a ^ c = b`。<br>
我们目前知道func，而不知道真实buf和k。<br>
由于buf是js代码，因此我们可以里面的关键字，如function，对于这题，按照前几题的代码看来，那么或许存在如`document.location`之类用于跳转的代码。<br>
基于这种想法，我们可以写个代码跑一下密码。<br>
如果字符串`document.location = document.location.href`存在，我们应该可以跑出错序密码，然后可以手动进行调整。<br>
测试代码如下

```
var func = "x2Bx09x4Ax03x49x0Fx0Ex14x15x1Ax00x10x3Fx1Ax71x5Cx5Bx5Bx00x1Ax16x38x06x46x66x5Ax55x30x0Ax03x1Dx08x50x5Fx51x15x6Bx4Fx19x56x00x54x1Bx50x58x21x1Ax0Fx13x07x46x1Dx58x58x21x0Ex16x1Fx06x5Cx1Dx5Cx45x27x09x4Cx1Fx07x56x56x4Cx78x24x47x40x49x19x0Fx11x1Dx17x7Fx52x42x5Bx58x1Bx13x4Fx17x26x00x01x03x04x57x5Dx40x19x2Ex00x01x17x1Dx5Bx5Cx5Ax17x7Fx4Fx06x19x0Ax47x5Ex51x59x36x41x0Ex19x0Ax53x47x5Dx58x2Cx41x0Ax04x0Cx54x13x1Fx17x60x50x12x4Bx4Bx12x18x14x42x79x4Fx1Fx56x14x12x56x58x44x27x4Fx19x56x49x16x1Bx16x14x21x1Dx07x05x19x5Dx5Dx47x52x60x46x4Cx1Ex1Dx5Fx5Fx1Cx15x7Ex0Bx0Bx00x49x51x5Fx55x44x31x52x45x13x1Bx40x5Cx46x10x7Cx38x10x19x07x55x13x44x56x31x1Cx15x19x1Bx56x13x47x58x30x1Dx1Bx58x55x1Dx57x5Dx41x7Cx4Dx4Bx4Dx49x4F";
var a = "document.";
var b = "location ";
var c = "= documen";
for(var n = 9; n &lt;= 126;)`{`
    for(var l = 0; l &lt; func.length; l++ )`{`
        if (l + 18 &lt; func.length) `{`
            for(var t = 0; t &lt; 9; t++)`{`
                var flag = 0;
                if (String.fromCharCode(func[l].charCodeAt() ^ n ) === a[t]) `{`
                    if (String.fromCharCode(func[l + 9].charCodeAt() ^ n ) === b[t]
                        &amp;&amp; String.fromCharCode(func[l + 18].charCodeAt() ^ n ) === c[t]
                        ) `{`
                        if (flag === 0) `{`
                            console.log(n + "---" + String.fromCharCode(n) + "||\x" + func[l].charCodeAt().toString(16) + "---" + a[t] + "&lt;==&gt;" + b[t]);
                        `}`
                    `}`
                `}`
            `}`
        `}`
    `}`
    if (n === 9) `{`
        n = 32;
    `}`else`{`
        n++;
    `}`
`}`
```

运行结果如下所示

[![](https://p0.ssl.qhimg.com/t01306f6f9516381b88.png)](https://p0.ssl.qhimg.com/t01306f6f9516381b88.png)

由此，我们可以知道`document.`所对应的密钥为`Bobvi2347`。而xor加密是使用密钥循环进行加密的，因此无法直接判断密文开头所对应的密钥是否是`B`，我们需要进一步进行计算。<br>
根据计算结果可知，`document.`中的`d`所对应的密文的编码为`x26`，在密文中可找到对应的值

[![](https://p3.ssl.qhimg.com/t01db88ff21fb459263.png)](https://p3.ssl.qhimg.com/t01db88ff21fb459263.png)

通过计算可知，`x26`前面的字符长度为90，刚好是9的倍数，也就是说循环加密到`d`的时候刚好使用了密钥的第一个字符进行加密，则`Bobvi2347`这个顺序是对的。<br>
将用户名改为该值，在`eval(buf);`处下断点，继续运行，可观察到buf如下

```
"if(u == "XorIsCoolButNotUnbreakable") `{` if(document.location.href.indexOf("?p=") == -1) `{` document.location = document.location.href + "?p=" + u; `}` `}` else `{`  $("#cresponse").html("&lt;div class='error'&gt;Wrong password sorry.&lt;/div&gt;"); `}`"

```

由此拿到密码，提交拿到flag<br>[Link](https://ringzer0team.com/challenges/46)



## WTF Lol!

### <a class="reference-link" name="%E9%A2%84%E8%A7%88"></a>预览

[![](https://p4.ssl.qhimg.com/t0152b1bdca702fd515.png)](https://p4.ssl.qhimg.com/t0152b1bdca702fd515.png)

### <a class="reference-link" name="%E8%A7%A3%E9%A2%98%E8%BF%87%E7%A8%8B"></a>解题过程

输入密码，拦截点击事件，程序先断在了这块

```
function btn_click(value) `{`
    try `{`
        if (check_password(document.getElementById('pwd').value)) `{`
            alert('That's the flag !');
            return;
        `}`
    `}` catch(e) `{``}`

    alert('Nope !');
`}`

```

跟进check_password方法

```
function check_password(password) `{`
    var stack = "qwertyuiopasdfghjklzxcvbnm".split("");
    var tmp = `{`
        "t" : 9, "h" : 6, "e" : 5,
        "f" : 1, "l" : 2, "a" : 3, "g" : 4,
        "i" : 7, "s" : 8, 
        "j" : 10, "u" : 11, "m" : 12, "p" : 13,
        "b" : 14, "r" : 15, "o" : 16, "w" : 17, "n" : 18,
        "c" : 19, "d" : 20, "j" : 21, "k" : 22, "q" : 23,
        "v" : 24, "x" : 25, "z" : 26
    `}`;

    var i = 2;

    var a1 = Number.prototype.valueOf;
    var a2 = Number.prototype.toString;
    var a3 = Array.prototype.valueOf;
    var a4 = Array.prototype.toString;
    var a5 = Object.prototype.valueOf;
    var a6 = Object.prototype.toString;

    function f1() `{` return stack[ i++ % stack.length ].charCodeAt(0); `}`
    function f2() `{` i += 3; return stack.pop(); `}`
    function f3() `{`
        for (k in this) `{`
            if (this.hasOwnProperty(k)) `{`
                i += stack.indexOf(this[k][0]);
                stack.push(this[k]);
            `}`
        `}`
        return String.fromCharCode(new Number(stack[ i % stack.length ].charCodeAt(0)));
    `}`

    Number.prototype.valueOf = Number.prototype.toString = f1;
    Array.prototype.valueOf  = Array.prototype.toString  = f2;
    Object.prototype.valueOf = Object.prototype.toString = f3;

    var a  = (tmp[ [] ] * tmp[ [] ] * 1337 + tmp[ "" + `{` "wtf": password[1] `}` ]) / (tmp[ "" + `{` "wtf": password[0] `}` ] - tmp[ [] ]);
    var b  = (tmp[ [] ] * tmp[ [] ] * 7331 + tmp[ "" + `{` "lol": "o" `}` ]) / (tmp[ "" + `{` "wtf": password[1] `}` ] - tmp[ [] ]);
    var c  = (tmp[ [] ] * tmp[ [] ] * 1111 + tmp[ "" + `{` "wtf": password[3] `}` ]) / (tmp[ "" + `{` "lol": password[2] `}` ] - tmp[ [] ]);
    var d  = (tmp[ [] ] * tmp[ [] ] * 3333 + tmp[ "" + `{` "wtf": "g" `}` ]) / (tmp[ "" + `{` "wtf": password[3] `}` ] - tmp[ [] ]);
    var e  = (tmp[ [] ] * tmp[ [] ] * 7777 + tmp[ "" + `{` "wtf": "a" `}` ]) / (tmp[ "" + `{` "wtf": password[7] `}` ] - tmp[ [] ]);
    var f  = (tmp[ [] ] * tmp[ [] ] * 2222 + tmp[ "" + `{` "wtf": password[7] `}` ]) / (tmp[ "" + `{` "lol": password[5] `}` ] - tmp[ [] ]);
    var g  = (tmp[ [] ] * tmp[ [] ] * 6666 + tmp[ "" + `{` "lol": password[4] `}` ]) / (tmp[ "" + `{` "wtf": password[6] `}` ] - tmp[ [] ]);
    var h  = (tmp[ [] ] * tmp[ [] ] * 1234 + tmp[ "" + `{` "wtf": "a" `}` ]) / (tmp[ "" + `{` "wtf": password[4] `}` ] - tmp[ [] ]);
    var ii = (tmp[ [] ] * tmp[ [] ] * 2345 + tmp[ "" + `{` "wtf": "h" `}` ]) / (tmp[ "" + `{` "wtf": password[9] `}` ] - tmp[ [] ]);
    var j  = (tmp[ [] ] * tmp[ [] ] * 3456 + tmp[ "" + `{` "wtf": password[9] `}` ]) / (tmp[ "" + `{` "lol": password[8] `}` ] - tmp[ [] ]);
    var kk = (tmp[ [] ] * tmp[ [] ] * 4567 + tmp[ "" + `{` "lol": password[11] `}` ]) / (tmp[ "" + `{` "wtf": password[10] `}` ] - tmp[ [] ]);
    var l  = (tmp[ [] ] * tmp[ [] ] * 9999 + tmp[ "" + `{` "wtf": "o" `}` ]) / (tmp[ "" + `{` "wtf": password[11] `}` ] - tmp[ [] ]);

    Number.prototype.valueOf   = a1;
    Number.prototype.toString  = a2;
    Array.prototype.valueOf    = a3;
    Array.prototype.toString   = a4;
    Object.prototype.valueOf   = a5;
    Object.prototype.toString  = a6;

    var m = a === b &amp;&amp; b === c &amp;&amp; c === d &amp;&amp; d === e &amp;&amp; e === f &amp;&amp; f === g &amp;&amp; g === h &amp;&amp; h === ii &amp;&amp; ii === j &amp;&amp; j === kk &amp;&amp; kk === l;
    var n = password[0] != password[1] &amp;&amp; password[2] != password[3] &amp;&amp; password[4] != password[5]  &amp;&amp; password[6] != password[7]  &amp;&amp; password[8] != password[9] &amp;&amp; password[10] != password[11]

    return m &amp;&amp; n;
`}`
```

这道题替换了`Number Array Object`这几个对象类型自带的`valueOf toString`方法，而开发者工具的调试正是使用了这些方法，因此在使用调试时查看变量值、设置断点、代码测试，都会导致其中关键值`i`的改变。<br>
而这道题又要求计算出一个值，使得其中的`a b c d e f g h ii j kk l`完全相等。<br>
但是在另一方面，我们注意到，在计算完毕之后，对象的方法又被还原回来了。因此我们可以将其计算部分的代码段看作黑盒，然后进行猜解，只要不动方法被改过的那部分代码就可以了。<br>
由于算力问题，爆破12位字符是不现实的，但是由于判断的时候，是先判断a===b，如果通过，则判断b===c，否则直接返回false，由此，我们可以进行逐位猜解，最大限度的减少算力浪费。<br>
测试代码如下。

```
function check_password(password) `{`
    var stack = "qwertyuiopasdfghjklzxcvbnm".split("");
    var tmp = `{`
        "t" : 9, "h" : 6, "e" : 5,
        "f" : 1, "l" : 2, "a" : 3, "g" : 4,
        "i" : 7, "s" : 8, 
        "j" : 10, "u" : 11, "m" : 12, "p" : 13,
        "b" : 14, "r" : 15, "o" : 16, "w" : 17, "n" : 18,
        "c" : 19, "d" : 20, "j" : 21, "k" : 22, "q" : 23, 
        "v" : 24, "x" : 25, "z" : 26
    `}`;

    var i = 2;

    var a1 = Number.prototype.valueOf;
    var a2 = Number.prototype.toString;
    var a3 = Array.prototype.valueOf;
    var a4 = Array.prototype.toString;
    var a5 = Object.prototype.valueOf;
    var a6 = Object.prototype.toString;

    function f1() `{`
        return stack[ i++ % stack.length ].charCodeAt(0); 
    `}`
    function f2() `{`
        i += 3; return stack.pop();
    `}`
    function f3() `{`
        for (k in this) `{`
            if (this.hasOwnProperty(k)) `{`
                i += stack.indexOf(this[k][0]);
                stack.push(this[k]);
            `}`
        `}`
        return String.fromCharCode(new Number(stack[ i % stack.length ].charCodeAt(0)));
    `}`

    Number.prototype.valueOf = Number.prototype.toString = f1;
    Array.prototype.valueOf  = Array.prototype.toString  = f2;
    Object.prototype.valueOf = Object.prototype.toString = f3;
    var a  = (tmp[ [] ] * tmp[ [] ] * 1337 + tmp[ "" + `{` "wtf": password[1] `}` ]) / (tmp[ "" + `{` "wtf": password[0] `}` ] - tmp[ [] ]);
    // 确定第0位
    var b  = (tmp[ [] ] * tmp[ [] ] * 7331 + tmp[ "" + `{` "lol": "o" `}` ]) / (tmp[ "" + `{` "wtf": password[1] `}` ] - tmp[ [] ]);
    // 确定第1位
    var c  = (tmp[ [] ] * tmp[ [] ] * 1111 + tmp[ "" + `{` "wtf": password[3] `}` ]) / (tmp[ "" + `{` "lol": password[2] `}` ] - tmp[ [] ]);
    // 确定第2位
    var d  = (tmp[ [] ] * tmp[ [] ] * 3333 + tmp[ "" + `{` "wtf": "g" `}` ]) / (tmp[ "" + `{` "wtf": password[3] `}` ] - tmp[ [] ]);
    // 确定第3位
    var e  = (tmp[ [] ] * tmp[ [] ] * 7777 + tmp[ "" + `{` "wtf": "a" `}` ]) / (tmp[ "" + `{` "wtf": password[7] `}` ] - tmp[ [] ]);
    // 限制第7位
    var f  = (tmp[ [] ] * tmp[ [] ] * 2222 + tmp[ "" + `{` "wtf": password[7] `}` ]) / (tmp[ "" + `{` "lol": password[5] `}` ] - tmp[ [] ]);
    // 确定第7位，确定第5位
    var g  = (tmp[ [] ] * tmp[ [] ] * 6666 + tmp[ "" + `{` "lol": password[4] `}` ]) / (tmp[ "" + `{` "wtf": password[6] `}` ] - tmp[ [] ]);
    // 限制第4位，限制第6位
    var h  = (tmp[ [] ] * tmp[ [] ] * 1234 + tmp[ "" + `{` "wtf": "a" `}` ]) / (tmp[ "" + `{` "wtf": password[4] `}` ] - tmp[ [] ]);
    // 确定第4位，从而确定第6位
    var ii = (tmp[ [] ] * tmp[ [] ] * 2345 + tmp[ "" + `{` "wtf": "h" `}` ]) / (tmp[ "" + `{` "wtf": password[9] `}` ] - tmp[ [] ]);
    // 限制第9位
    var j  = (tmp[ [] ] * tmp[ [] ] * 3456 + tmp[ "" + `{` "wtf": password[9] `}` ]) / (tmp[ "" + `{` "lol": password[8] `}` ] - tmp[ [] ]);
    // 确定第8 9位
    var kk = (tmp[ [] ] * tmp[ [] ] * 4567 + tmp[ "" + `{` "lol": password[11] `}` ]) / (tmp[ "" + `{` "wtf": password[10] `}` ] - tmp[ [] ]);
    // 限制10 11位
    var l  = (tmp[ [] ] * tmp[ [] ] * 9999 + tmp[ "" + `{` "wtf": "o" `}` ]) / (tmp[ "" + `{` "wtf": password[11] `}` ] - tmp[ [] ]);
    // 确定11位，从而确定10位
    // 0 1 2 3 7 5 4 6 9 8 11 10

    Number.prototype.valueOf   = a1;
    Number.prototype.toString  = a2;
    Array.prototype.valueOf    = a3;
    Array.prototype.toString   = a4;
    Object.prototype.valueOf   = a5;
    Object.prototype.toString  = a6;

    if (a !== b) `{`
        return '0-a-b';
    `}` else if (b !== c) `{`
        return '1-b-c';
    `}` else if (c !== d) `{`
        return '2-c-d';
    `}` else if (d !== e) `{`
        return '3-d-e';
    `}` else if (e !== f) `{`
        return '4-e-f';
    `}` else if (f !== g) `{`
        return '5-f-g';
    `}` else if (g !== h) `{`
        return '6-g-h';
    `}` else if (h !== ii) `{`
        return '7-h-ii';
    `}` else if (ii !== j) `{`
        return '8-ii-j';
    `}` else if (j !== kk) `{`
        return '9-j-k';
    `}` else if (kk !== l) `{`
        return '10-kk-l';
    `}` else `{`
        console.log(password);
        return true;
    `}`
`}`

var flag = new Array(12);
for (flag[0] = 32; result !== true &amp;&amp; flag[0] &lt;= 127; flag[0]++) `{`
    for (flag[1] = 32; result !== true &amp;&amp; flag[1] &lt;= 127; flag[1]++) `{`
        for (flag[2] = 32; flag[1] != flag[0] &amp;&amp; result !== true &amp;&amp; flag[2] &lt;= 127; flag[2]++) `{`
            for (flag[3] = 32; flag[2] != flag[1] &amp;&amp; result !== true &amp;&amp; flag[3] &lt;= 127; flag[3]++) `{`
                for (flag[7] = 32; flag[3] != flag[2] &amp;&amp; result !== true &amp;&amp; flag[7] &lt;= 127 &amp;&amp; flag[1] &lt;= 127 &amp;&amp; flag[3] &lt;= 127 ; flag[7]++) `{`
                    for (flag[5] = 32; result !== true &amp;&amp; flag[5] &lt;= 127 &amp;&amp; flag[1] &lt;= 127 &amp;&amp; flag[2] &lt;= 127 &amp;&amp; flag[3] &lt;= 127 &amp;&amp; flag[7] &lt;= 127; flag[5]++) `{`
                        for (flag[6] = 32; result !== true &amp;&amp; flag[6] &lt;= 127 &amp;&amp; flag[1] &lt;= 127 &amp;&amp; flag[2] &lt;= 127 &amp;&amp; flag[3] &lt;= 127 &amp;&amp; flag[7] &lt;= 127; flag[6]++) `{`
                            for (flag[4] = 32; flag[7] != flag[6] &amp;&amp; flag[5] != flag[6] &amp;&amp; result !== true &amp;&amp; flag[4] &lt;= 127 &amp;&amp; flag[1] &lt;= 127 &amp;&amp; flag[2] &lt;= 127 &amp;&amp; flag[3] &lt;= 127 &amp;&amp; flag[7] &lt;= 127; flag[4]++) `{`
                                for (flag[9] = 32; flag[5] != flag[4] &amp;&amp; flag[3] != flag[4] &amp;&amp; result !== true &amp;&amp; flag[9] &lt;= 127 &amp;&amp; flag[1] &lt;= 127 &amp;&amp; flag[2] &lt;= 127 &amp;&amp; flag[3] &lt;= 127 &amp;&amp; flag[7] &lt;= 127; flag[9]++) `{`
                                    for (flag[8] = 32; result !== true &amp;&amp; flag[8] &lt;= 127 &amp;&amp; flag[1] &lt;= 127 &amp;&amp; flag[2] &lt;= 127 &amp;&amp; flag[3] &lt;= 127 &amp;&amp; flag[7] &lt;= 127 &amp;&amp; flag[9] &lt;= 127; flag[8]++) `{`
                                        for (flag[11] = 32; flag[9] != flag[8] &amp;&amp; flag[8] != flag[7] &amp;&amp; result !== true &amp;&amp; flag[11] &lt;= 127 &amp;&amp; flag[1] &lt;= 127 &amp;&amp; flag[2] &lt;= 127 &amp;&amp; flag[3] &lt;= 127 &amp;&amp; flag[7] &lt;= 127 &amp;&amp; flag[9] &lt;= 127; flag[11]++) `{`
                                            for (flag[10] = 32; result !== true &amp;&amp; flag[10] &lt;= 127 &amp;&amp; flag[4] &lt;= 127 &amp;&amp; flag[1] &lt;= 127 &amp;&amp; flag[2] &lt;= 127 &amp;&amp; flag[3] &lt;= 127 &amp;&amp; flag[7] &lt;= 127 &amp;&amp; flag[9] &lt;= 127; flag[10]++) `{`
                                                if (flag[10] != flag[11] &amp;&amp; flag[10] != flag[9]) `{`
                                                    var result = check_password(String.fromCharCode(flag[0], flag[1], flag[2], flag[3], flag[4], flag[5], flag[6], flag[7], flag[8], flag[9], flag[10], flag[11]));
                                                    switch (result) `{`
                                                        case '0-a-b':flag[1]++;break;
                                                        case '1-b-c':flag[3]++;break;
                                                        case '2-c-d':flag[3]++;break;
                                                        case '3-d-e':flag[7]++;break;
                                                        case '4-e-f':flag[5]++;break;
                                                        case '5-f-g':flag[4]++;break;
                                                        case '6-g-h':flag[4]++;break;
                                                        case '7-h-ii':flag[9]++;break;
                                                        case '8-ii-j':flag[8]++;break;
                                                        case '9-j-k':flag[10]++;break;
                                                        default:
                                                        if (result === true) `{`
                                                            console.log(result);
                                                            console.log("find the flag!");
                                                        `}`
                                                    `}`
                                                `}`
                                            `}`
                                        `}`
                                    `}`
                                `}`
                            `}`
                        `}`
                    `}`
                `}`
            `}`
        `}`
    `}`
`}`
```

运行后可得到密码，提交拿到flag<br>[Link](https://ringzer0team.com/challenges/213)



## Beauty and the beast

### <a class="reference-link" name="%E9%A2%84%E8%A7%88"></a>预览

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0192986f0de981a0bc.png)

### <a class="reference-link" name="%E8%A7%A3%E9%A2%98%E8%BF%87%E7%A8%8B"></a>解题过程

打开开发者工具，发现直接被`debugger`断下，无法跳出，因此我们通过源代码寻找js代码

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c5d8108d941d0831.png)

在其他空白页面开启F12调试，新建代码片段，记为true_orgin，然后运行片段。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0134cca8e579c391d8.png)

可以发现直接被`debugger`断下。查看调用栈，找到前两个`debugger`。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t010b7a0b815d9bc3ea.png)

```
try `{`
    (function R7(O) `{`
        if ((i[2] + (O / O))[i[3]] !== 1 || O % 20 === 0) `{`
            (function() `{``}`
            ).constructor(i[37])();    //i[37]值为debugger
        `}` else `{`
            debugger ;
        `}`
        R7(++O);
    `}`(0))
`}` catch (O) `{``}`
```

可以看出这段代码就是为了调试时永远进入`debugger`的。注释掉相关语句重新运行，发现console报错。

```
true_orgin:402 Uncaught TypeError: Cannot read property 'b4O' of undefined
    at Function.c8i.k4O (&lt;anonymous&gt;:402:24)
    at &lt;anonymous&gt;:405:21
```

为了分析原因，我们先将原始代码再复制为另一段js片段，记为the_true_orgin，分析是否是原始代码有问题，并Ctrl+F8禁用断点，重新运行，发现报错不同。

```
the_true_orgin:1 Uncaught ReferenceError: module is not defined
    at &lt;anonymous&gt;:1:26508
    at &lt;anonymous&gt;:1:27781
```

前一个提示的是`c8i.k4O`方法不存在，在代码格式化后的第402行，后一个的报错点则是第634行，显然原始代码中`c8i.k4O`方法是存在的，由此基本确定是对代码的改动导致的报错。<br>
跟踪查看`c8i`定义

```
var c8i = (function B(t, n) `{`
        var E = ''
      , D = decodeURIComponent(/* 此处省略1k多密文字符 */);
    for (var o = 0, Z = 0; o &lt; D["length"]; o++,
    Z++) `{`
        if (Z === n["length"]) `{`
            Z = 0;
        `}`
        E += String["fromCharCode"](D["charCodeAt"](o) ^ n["charCodeAt"](Z));    //xor解密
    `}`
    var i = E.split('&lt;,&gt;');
    // 此处省略两百多行代码
    `}`
)(decodeURIComponent(/* 此处省略1W多个密文字符 */), "htq8Ure6eWWrIzyfUZbwXF60zbDctikoSyNkrYoSSTj1EE6O");
```

程序先定义`B`方法，然后将密文和密码传入`B`方法，而`c8i`获取到的是其运行后的返回值。<br>
持续跟进，可以发现代码里使用了大量的异常捕获来保证程序的继续运行。而`B`方法最终在199行有如下代码，决定了`c8i`的值。

```
try `{`
    var x = 0
      , U = 23
      , l = [];
    l[x] = y[i[0]](Z7(y[i[1]] + i[2])) + i[2];
    var i7 = l[x][i[3]];
    for (var o = t[i[3]] - 1, Z = 0; o &gt;= 0; o--,
    Z++) `{`
        if (Z === i7) `{`
            Z = 0;
            if (++x === U) `{`
                x = 0;
            `}`
            if (l[i[3]] &lt; U) `{`
                l[x] = y[i[0]](l[x - 1], l[x - 1]) + i[2];
            `}`
            i7 = l[x][i[3]];
        `}`
        w = String[i[4]](t[i[5]](o) ^ l[x][i[5]](Z)) + w;
    `}`
    var V = (0,
    eval)(w);
    if (typeof V === i[6]) `{`
        for (var h in V) `{`
            if (V[i[7]](h) &amp;&amp; typeof V[h] === i[8]) `{`
                V[h][i[9]] = V[h][i[10]] = function() `{`
                    return i[2];
                `}`
                ;
            `}`
        `}`
    `}`
    (function x7(O) `{`
        if (typeof O === i[6]) `{`
            for (var p in O) `{`
                if (O[i[7]](p)) `{`
                    if (typeof O[p] === i[8]) `{`
                        O[p][i[9]] = O[p][i[10]] = function() `{`
                            return i[2];
                        `}`
                        ;
                    `}` else if (typeof O[p] === i[6]) `{`
                        x7(O[p]);
                    `}`
                `}`
            `}`
        `}`
    `}`
    )(V);
    if (typeof V !== i[11])
        V[i[9]] = V[i[10]] = function() `{`
            return i[2];
        `}`
        ;
    return V;
`}` catch (O) `{`
    return function() `{``}`
    ;
`}`
```

我们将断点设在`var V = (0,eval)(w);`一句，在Watch区域监视w和c8i，然后重新运行代码，断在了第219行，可以看到w是一串乱码。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01360c838f6d0cfd45.png)

因此`eval`语句报错。<br>
上面这段代码使用了大量的变量用以混淆，实际上其流程是：获取到自身方法B的代码，并参与运算，得到一个w，然后运行w并捕获异常，若无异常，程序向下执行，最终返回对象V，若发生异常，则会导致返回一个空方法，导致`c8i`为空，从而使得后续代码调用`c8i`相关方法失败，显然这就是上面console报错的原因了。<br>
即，对原始代码的修改，如格式化、注释，都将导致`c8i`为空，但如果不修改，其代码片段开头的`debugger`将导致代码持续断在代码开头，无法向下运行，即使禁用断点，也会导致后面无法使用断点进行动态分析，从而增加分析的难度。<br>
为了解决这个问题，我们可以在格式化后的代码中注入原始代码字符串，由于代码原本是获取到自身代码，并转为字符串，因此我们只要将其替换为原始代码字符串即可。<br>
或者采用另外一种方法，即从开发者工具的代码虚拟机中调出`c8i`。<br>
由于未分析完全，第一种方法由于不知名的原因导致失败，我们采用了第二种方式。<br>
同样的，禁用断点，运行原始代码，esc调出console，查看`c8i`，点开其中任一方法，查看其定义。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0193178c3c5b4c92d0.png)

进入定位B7的定义代码片段

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01afd30f052388658d.png)

成功在代码虚拟机里找到了`c8i`的完整定义。删除其中的`debugger`相关代码，并用该定义替换原先代码中`c8i`的定义。<br>
运行后也报了`module`的错，说明成功了。<br>
接下来修复`module`报错。<br>
定位代码为

```
if (typeof module !== y &amp;&amp; module[k]) `{`
```

根据上下文可判断其为flash相关代码，因此我在[GitHub](https://github.com/hotmit/django-lazifier/blob/83a1e54581758cee05cbaaa664fa6a3c49456760/django_lazifier/utils/static/lazifier/js/js-utils/js-utils.js)寻找了相关代码作为参考。<br>
向上查找y的定义`y = c8i.X4O("d8d8") ? "ShockwaveFlash.ShockwaveFlash" : 'undefined'`，修改为`undefined`<br>
修改后运行，错误如下

```
true_orgin:515 Uncaught TypeError: p[A] is not a function
    at v (&lt;anonymous&gt;:515:19)
    at &lt;anonymous&gt;:519:13
    at &lt;anonymous&gt;:521:6
    at &lt;anonymous&gt;:597:2
```

定位代码如下

```
g[p[A](K)] = O;    //即g.toBase64URI.activeXDetectRules(0)
```

查找A的定义`A = c8i.n4O("4a") ? "activeXDetectRules" : "charAt"`，修改为`charAt`

```
g[p.charAt(K)] = O;
```

再次运行，错误如下

```
true_orgin:1247 Uncaught TypeError: Cannot set property 'calculate' of undefined
    at &lt;anonymous&gt;:1247:31
```

定位到1247行的31列，其设置了`Challenge`对象的方法，根据提示可以看出是`Challenge`的`prototype`不存在导致的

```
Challenge.prototype.calculate = function() `{`
```

跳转到`Challenge`的定义处

```
var Challenge = c8i.k4O("b6d3") ? function(O) `{`
    this[c8i.X7O] = c8i.a4O("7a") ? O : "re_utob";
    this[c8i.y8O] = c8i.r4O("73") ? '-' : Base64;
`}`
: "version";
```

显然由于字符串不存在`prototype`属性从而报错，这里经过了一个三元运算，未被选择的正是正确代码段，我们将其更正为方法。<br>
再次运行，错误如下

```
true_orgin:1247 Uncaught TypeError: this[c8i.y8O][c8i.n8O] is not a function
    at Challenge.calculate (&lt;anonymous&gt;:1247:43)
    at &lt;anonymous&gt;:1312:15
```

定位后确定是`calculate`方法有问题，格式化后代码如下

```
Challenge.prototype.calculate = function() `{`
    this["data"] = this["instance"]["encode"](this["data"]);
    return this;
`}`
```

向上查找，依然是`Challenge`方法有问题，`Challenge.instance.encode`方法不存在，修正后如下

```
var Challenge = function(O) `{`
    this["data"] = O;
    this["instance"] = Base64;
`}`;
```

回过头看`calculate`的代码，大意是将`data`属性编码用base64，但由于Base64并未定义，相关代码需要修正，因此我们在相关调用编码的代码部分，手动赋值编码后的字符串。<br>
另外为了避免由于Base64未定义导致的报错，将`this["instance"] = Base64;`改成`this["instance"] = "Base64";`。<br>
由于`calculate`方法无法使用，因此将断点设在`calculate`。

[![](https://p0.ssl.qhimg.com/t0122917fbb4f50ca38.png)](https://p0.ssl.qhimg.com/t0122917fbb4f50ca38.png)

根据调用栈定位调用处，调用处代码美化后如下

```
dummy["calculate"]()["secondRound"](versioncheck);
```

跟进查看dummy定义

```
var dummy = new Challenge(navigator["userAgent"])
  , versioncheck = FlashDetect["installed"];
```

可以看到，其`data`属性即浏览器User-Agent，同时检测了Flash插件的安装情况。<br>
为避免不必要的麻烦，此处我们替换`navigator["userAgent"]`为准确UA字符串，同时开启chrome默认关闭的flash。<br>
至此，`dummy`对象的data属性保存了UA，并将`data`进行base64编码。<br>
继续跟进`secondRound`方法。

```
Challenge.prototype.secondRound = function(O) `{`
    var p = "b64";
    this["data"] = O + this[p](this["data"]);
    this["data"] = this[p](this["data"]);
`}`
```

我们再查找一下`b64`的定义

```
Challenge.prototype.b64 = function(O) `{`
    return this["instance"]["data"](O);
`}`
```

可以知道，其大意是返回data属性编码后的字串。<br>
则`secondRound`方法流程为：将`data`编码，再加入flash版本，再编码，替换`data`。<br>
完成后代码向下执行。

```
var versioncheck = dummy["get"](), kj4kjhkj43w980 = "error.js";
```

其中`get`方法用于获取到`data`属性值。<br>
此时`versioncheck`为编码后的Flash版本和UA，代码向下执行。

```
if (dummy["checkFirst"](versioncheck)) `{`
    kj4kjhkj43w980 = CryptoJS["SHA1"](dummy["lkslkj5lkj"]());
`}`
```

其中`lkslkj5lkj`方法获取到的是浏览器UA。<br>
跟进`checkFirst`

```
Challenge.prototype.checkFirst = function(O) `{`
    var p = "U2hvY2t3YXZlIEZsYXNoIDIwLjAgcjBWRmM1Tm1GWGVITlpVemd4VEdwQlowdEdaSEJpYlZKMlpETk5aMVJzVVdkT2FUUjRUM2xDV0ZReFl6Sk9RMnRuVVZoQ2QySkhWbGhhVjBwTVlWaFJkazVVVFROTWFrMHlTVU5vVEZOR1VrNVVRM2RuWWtkc2NscFRRa2hhVjA1eVlubHJaMUV5YUhsaU1qRnNUSHBSTTB4cVFYVk5hbFY1VG1rME5FMURRbFJaVjFwb1kyMXJkazVVVFROTWFrMHk="
      , N = "E5";
    if (c8i[N](O, p)) `{`
        return c8i.e8O;
    `}`
    return c8i.j7O;
`}`
```

其中`c8i.E5`方法起到判断相等的作用。<br>
我们将p解码几次，即可得到要求的版本

```
Shockwave Flash 20.0 r0
```

和

```
Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36
```

随后将UA用sha1计算，这里我们将其替换为所需的UA字串。

```
kj4kjhkj43w980 = CryptoJS["SHA1"]("Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36");
```

代码向下执行

```
var suffix = new Array();
suffix[c8i.q3] = parseInt(dummy["doGet"](c8i.b3));
suffix[c8i.Q3] = parseInt(dummy["doGet"](c8i.h8O));
suffix[c8i.W3] = dummy["doGet"](c8i.S8O);
suffix[c8i.u3] = dummy["doGet"](c8i.X9);
suffix[c8i.E3] = dummy["doGet"](c8i.s3);
c8i[c8i.u9]();
suffix[5] = suffix[5]["toString"]();
if (c8i["U5"](suffix[5]["length"], 6) &amp;&amp; c8i["p3"](CryptoJS["SHA1"](suffix[5]), "be084fcf0f18867dd613af99c8cff52bdfa6037f")) `{`
    kj4kjhkj43w980 += suffix[5] + ".js";
`}`
```

方法`U5`和`p3`用于判断相等，`doGet`方法用于获取url中指定参数的值。<br>
这里`suffix[5]`由`suffix[c8i.q3] suffix[c8i.Q3] suffix[c8i.W3] suffix[c8i.u3] suffix[c8i.E3]`计算得出，我们不再从url加入查询语句，直接为`suffix[5]`赋所需的值。

```
if (c8i["U5"](suffix[5]["length"], 6) &amp;&amp; c8i["p3"](CryptoJS["SHA1"](suffix[5]), "be084fcf0f18867dd613af99c8cff52bdfa6037f"))
```

由该判断语句可知，`suffix[5]`长度理应为6，且SHA1计算值为`be084fcf0f18867dd613af99c8cff52bdfa6037f`，根据上方相应代码，我们还可得知，`suffix[5]`为数字，根据以上提示，我们可以写出爆破算法，寻找该六位的数字，或者到相关解密站点进行解密。<br>
解得明文为124341。<br>
判断成功后，引入了变量`kj4kjhkj43w980`所代表的js文件。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0154eb290e30213ff4.png)

代码段先定义了一个`r9i`对象，随后定义了相关方法。<br>
我们查看最后的判断分支。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t010527b19a59794021.png)

`!error`和`alert alert-success`提示我们上面是正确的分支。<br>
试着调试运算开始处的代码：

```
var flag = r9i.u4("25") ? r9i.D : '%20'
  , data = r9i.L4("141d") ? r9i.d : "No FLAG for you"
  , error = r9i.l4("58a3") ? "nKUp5vr4JC7zsxR3pI2dS7J" : r9i.f;
```

我们通过查看当前值可以发现，此时`data`赋值为`"No FLAG for you"`，`error`赋值为`"nKUp5vr4JC7zsxR3pI2dS7J"`，由此将导致无法进入正确分支，因此我们需要修改代码。<br>
根据`data`和`error`的提示，我们将flag的赋值也进行修正，然后继续向下执行

```
if (r9i["g"](aslkddalkj3("klsdslk2"), "Beast")) `{`    //如果url中参数klsdslk2值为Beast的话，进入这条分支
    var lkejtlkjw = r9i.J4("dd") ? "lkfejskl4kjlkfejskl4kjlkjtrlkfejskl4kjlkjtrlkfejskl4kjlkjtrlkfejskl4kjlkjtrlkfejskl4kjlkjtrlkfejskl4kjlkjtrlkfejskl4kjlkjtrlkfejskl4kjlkjtrlkfejskl4kjlkjtrlkfejskl4kjlkjtrlkfejskl4kjlkjtrlkfejskl4kjlkjtrlkfejskl4kjlkjtrlkfejskl4kjlkjtrlkfejskl4kjlkjtrlkfejskl4kjlkjtrlkfejskl4kjlkjtrlkfejskl4kjlkjtrlkfejskl4kjlkjtrlkfejskl4kjlkjtrlkfejskl4kjlkjtrlkfejskl4kjlkjtrlkfejskl4kjlkjtrlkfejskl4kjlkjtrlkfejskl4kjlkjtrlkfejskl4kjlkjtrlkfejskl4kjlkjtrlkfejskl4kjlkjtrlkfejskl4kjlkjtrlkfejskl4kjlkjtrlkfejskl4kjlkjtrlkfejskl4kjlkjtrlkjtr" : sdflkdsflklkjfddddd(r9i.o);
    data += r9i.I4("b71") ? r9i.S : "lkasdlkdsa";
`}` else `{`
    var t = r9i.v4("bc") ? function(i) `{`
        data = r9i.S4("c8dc") ? i : "flag";
    `}`
    : ""
      , M = r9i.O4("13d") ? function(i) `{`
        error = i;
    `}`
    : "lkasdlkdsa";
    t(r9i.O);
    M(r9i.Q);
`}`
```

当url中参数`klsdslk2`值为`Beast`时，可进入上方分支，考虑到标题为`Beauty and the beast`，因此上方可能是正确代码段。此处url相关参数不参与任何计算，因此我们直接将其判断语句修改为true，进入上方语句。<br>
最后再根据报错和题目提示，改几处三元运算的赋值，即可拿到FLAG。<br>
最后在原页面运行相关代码段，可以看到flag被揭开的效果，呼应了次标题中的`reveal the flag`。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01ea4df5e245d7a303.png)

[Link](https://ringzer0team.com/challenges/211)
