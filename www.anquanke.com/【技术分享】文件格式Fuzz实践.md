
# 【技术分享】文件格式Fuzz实践


                                阅读量   
                                **180598**
                            
                        |
                        
                                                                                                                                    ![](./img/85524/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



****

[![](./img/85524/t014edb6411acc64e44.png)](./img/85524/t014edb6411acc64e44.png)

作者：[o0xmuhe](http://bobao.360.cn/member/contribute?uid=32403999)

预估稿费：300RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



**0x00: 前言**

笔者整理去年的笔记的时候，发现了躺在印象笔记里的使用peach来进行文件格式fuzz的笔记，所以经过整理就有了这篇文章，希望可以对入门漏洞挖掘方面的同学有所帮助。

笔者以为文件格式fuzz应该是比较容易上手的，所以选择学习peach来学习文件格式fuzz，经过willj师傅指点，我就尝试去fuzz了某播放器，只是个尝试，虽然没啥产出，但是fuzz过程还算清晰。过程中实现了自动化的fuzz脚本，有完整的功能，就是效率堪忧-。-有待完善，整个项目就只是个toy 见笑了~

<br>

**0x01: 关于文件格式fuzz**

**简介**

文件格式fuzz简单的来说，是针对文件格式解析的fuzz，我们这里拿播放器举例子：

首先播放器支持特定的视频文件格式(flv,mp4,mov,avi,等…)，用户把想要播放的文件传给播放器之后，播放器会根据文件格式去解析这个文件，然后做出相应的处理。

那么攻击面就产生了：解析文件部分

1. 如果我传入一个畸形文件呢？

2. 如果我传入一个部分结构异常的文件呢？

3. ……

正如上面例子提到的，我们传入的文件部分结构异常，那么播放器是否还能够正常工作呢？会进入异常处理还是直接crash掉呢？那么crash可以不可以利用呢？

笔者记得最开始接触漏洞挖掘与利用的时候，第一个接触的漏洞是某播放器m3u文件的栈溢出，简单粗暴的没有对文件结构做check，导致数据处理的时候栈溢出，可以代码执行。

**工具选择**

对于工具的选择，我选择使用peach2.3.9，因为是Python编写的，有源码可以读，搞起来方便一些。

[peach](http://www.peachfuzzer.com/resources/peachcommunity/)是一款优秀的文件格式fuzz工具。

peach是基于模板变异工作的，而且开源，文档虽然不是那么多，但是自己多摸索、学习还是可以学会一些基本的用法的。我在看使用peach做文件fuzz相关的资料的时候，最开始看的《0day2》里作者给的例子，从编写pit file到fuzz跑起来；之后看了一份国际友人写[的Fuzzing with Peach – Part 1 « Flinkd!](http://www.flinkd.org/2011/07/fuzzing-with-peach-part-1/)，他这篇文章写的非常好，几乎涵盖了peach 90%的语法，仔细阅读，自己动手实践，会很快入门pit file的编写。

<br>

**0x02： pit file简介**

peach会根据提供的模板文件和对应的pit file，按照编写的pit file去解析模板文件，然后对一些结构变异，产生新文件。如果你pit file编写很详细，即粒度很小，虽然解析会慢，但fuzz的更全面。不过peach产生的样本，很多很相似，某种程度上可能在执行路径的覆盖上不太好，不过架不住量多~

这部分推荐直接参考官网、以及一些例子。官网文档很晦涩难懂，不过结合大佬的pit file，能够很快上手pit file的编写咯。

这里笔者只对基本结构介绍一下：

**DataModel**

DataModel 是用来定义数据结构的元素，我们可以在里面定义哪些结构需要进行Fuzz，哪些结构不需要进行 Fuzz。

**StateModel**

StateModel 负责管理 Fuzz 过程的执行流。

**Agents**

Agents 用来监视 Fuzz 过程中程序的行为，可以捕获程序的 crash 信息。

**Test Block**

Test Block 负责将 StateModel 和 Agents 等联系到一个单一的测试用例里。

**Run Block**

Run Block 负责定义 Fuzz 过程中哪些 Test 会被执行。这个块也会记录 Agent 产生的信息。

**支持的元素**

1. DataModel

DataModel 元素是 Peach 根元素的子节点。DataModel 定义了数据块的结构，它会声明像Number 和 String 等子元素。

2. Block

Block 是用来组合一个或者多个的其他元素，比如 Number 或者 String。

3. Choice

Choice 元素是 DataModel 或者 Block 的子元素。Choice 元素是用来指定任意一个子元素是有效的，并且之能选择其中一个。就像 C 语言里的 switch 语法。

4. String

String 元素定义一个或者双字节的字符串。

5. Number

Number 元素定义了长度为 8，16，24，32 或者 64 位的二进制数字。

6. Blob

Blob 元素是 DataModel 或者 Block 的子元素。Blob 是用来定义不明类型的数据。

7. Flags

Flags 定义了一些以位为单位的集合,，比如一些标志位。

8. Relation

Peach 允许数据间的关系建模。关系像“X 是 Y 的大小”，“X 是 Y 出现的次数”，或者“X是 Y 的偏移（以字节为单位）”。

size-of Relation

count-of Relation

When 这个关系用来决定一个元素是否用

基础内容的话，推荐参考看雪的教程[【原创】文件Fuzz教程之一：Peach语法介绍](http://bbs.pediy.com/showthread.php?t=176416)

<br>

**0x03: 文件fuzz的思路**

现在进入正题，fuzz嘛，简单的来看就是

构造输入

传给目标程序

程序状态检测(是否crash)

做log

之后根据你的log，把产生了crash的样本拿出来单独分析，看看是不是有价值-。-

所以，我的想法也很简单，就是利用peach基于我给的一个小文件，生成很多样本，然后写自动化的脚本去fuzz，并且做好异常检测的工作。

这里我们假设选取Adobe flash player sa版本，刚开始尝试就做一点简单的，选择flv文件作为fuzz的点。其实你选啥都无所谓…直接选一些播放器可能还更简单。

下面我们面临的问题就是：

1. flv文件格式

2. 根据文件格式编写pit file

3. 如何加载我的fuzz.flv文件？

4. 异常检测怎么做

下面慢慢来分析。

flv文件格式

flv文件主要分为header和body两个部分。

1.1. header部分

第1-3字节：文件标志，FLV的文件标志为固定的“FLV"，字节（0x46， 0x4C，0x56），见上面的字节序和字符序两行；

第4字节：当前文件版本，固定为1（0x01）

第5字节：此字节当前用到的只有第6，8两个bit位，分别标志当前文件是否存在音频，视频。参见上面bit序，即是第5字节的内容；

第6-9字节：此4字节共同组成一个无符号32位整数（使用大头序），表示文件从FLV Header开始到Flv Body的字节数，当前版本固定为9（0x00，0x00，0x00，0x09）

1.2 .body部分

这部分其实就是很多的tag的组合。

不过tag的种类有三种，分别是script、Audio、Video。每种tag的tag data又各不相同，详细的可以看一些文档了解。



```
-------------------------
   |  Previous Tag Size    |
   -------------------------
   |          Tag          |
   -------------------------
   |  Previous Tag Size    |
   -------------------------
   |          Tag          |
   -------------------------
   |  Previous Tag Size    |
   -------------------------
   |          Tag          |
   -------------------------
   |  Previous Tag Size    |
   -------------------------
```

一些参考的文档[flv文件格式详解](http://blog.useasp.net/archive/2016/02/28/The-flv-video-file-format-specification-version-10-1.aspx)，以及是官方的flv格式相关的文档都可以。

**1. 根据文件格式编写pit file**

了解了文件格式之后就是编写pit file了，困难的地方可能就在于tag结构，因为数目不确定，而且相互之间有联系，比如某个bit为1或者0，影响着后面的某个结构的有无。

我的做法是，我使用类似Switch case这样的结构，让peach自己去判断选择对应的结构，即我写三种tag，然后限定最大的出现次数，因为样本很小，出现的tag几百个最多了，然后peach根据模板文件的tag的标志，找到我pit file里对应的tag的结构，然后根据pit file里的结构进行变异，然后生成新的样本。

这里可以使用010 editor的二进制模板功能，可以对比你生成的样本是否正确，方便调试。

**2. 如何加载我的fuzz.flv文件？**

有了样本，下面的问题就是怎么加载样本然后播放了。

然而flash并不直接打开flv文件，而是使用swf来加载，所以我需要用as语言来编写一个swf来加载。这时候就有又一个问题：swf要编译的，即我的文件名会写死，这就相当于文件名硬编码进去了，这时候就麻烦了。

不过这个也好解决，我可以在后续的fuzz脚本中，每次单独复制一个样本到工作目录，然后重命名为swf要加载的文件的名字，然后起flash，加载swf，然后做后续的工作；完成之后，循环这个工作。这样就可以很好的解决这个问题了。

简单的来说就是：

从样本库复制一个样本——–&gt;工作目录(并重命名为fuzz.flv)——-&gt;加载fuzz.swf文件——–&gt;进入正常的fuzz流程(含异常捕获)

**3. 异常检测怎么做**

我觉得最简单的办法就是调试器了，如果你进程崩了，你的just in time debugger会启动，问你要不要调试。

所以呢，我们检测进程就可以了，如果有你设置的即时调试器，直接做log，杀了所有fuzz相关的进程，继续下一轮fuzz就好了。然而呢，这种方法缺点很明显，非常的不优雅，而且效率低的要死，不过刚开始搞嘛，凑合用咯。先跑起来，以后慢慢看着怎么搞优化。

<br>

**0x04: 编写pit file**

**1.首先是针对flv header的部分的编写**

先来看flv header的结构

第1-3字节：文件标志，FLV的文件标志为固定的“FLV"，字节（0x46， 0x4C，0x56）(pit:对应pit的话，String标签就可以了)

第4字节：当前文件版本，固定为1（0x01） (pit:这个可以直接整合到选项1中去)

第5字节：此字节当前用到的只有第6，8两个bit位，分别标志当前文件是否存在音频，视频。(pit:bit位，直接使用Flags标签咯)

第6-9字节：此4字节共同组成一个无符号32位整数（使用大头序），表示文件从FLV Header开始到Flv Body的字节数，当前版本固定为9（0x00，0x00，0x00，0x09）(pit:既然是数字，使用Number标签就好了)

那么对应的xml应该是



```
&lt;DataModel name="flvHeader"&gt;
    &lt;String name="flv_Signature" value="464C5601" valueType="hex" token="true" mutable="false"/&gt;
        &lt;Flags name="HeadFlags" size="8"&gt;
            &lt;Flag name="dummy"  position="3" size="5"/&gt;
            &lt;Flag name="audio"  position="2" size="1"/&gt;
            &lt;Flag name="dummy2" position="1" size="1"/&gt;
            &lt;Flag name="video"  position="0" size="1"/&gt;
        &lt;/Flags&gt;
    &lt;Number name="dataoffset" value="9" size="32"/&gt;
    &lt;Number name="zero" size="32"/&gt;
&lt;/DataModel&gt;
```

**2.这部分是script tag部分的编写**

首先来看script tag结构，介绍的篇幅略长，不直观，我们直接看010 editor的二进制模板：



```
UINT    type : 8;
    UINT    datasize : 24;
    UINT    timestamp : 24;
    UINT    timestamphi : 8;
    UINT    streamid : 24;
    taglen = datasize - 1;
    ...
    ...
    else if(type==18)//script
    {
        UINT fristbyte : 8;
    }
    UBYTE data[taglen];
    UINT lastsize;    //last tag size
```

那么我们对应的xml如下



```
&lt;Block name="script"&gt;
    &lt;Number name="type" size="8" signed="false" endian="big" value="18" token="true" mutable="false"/&gt;
    &lt;Number name="datasize" size="24" endian="big" signed="false"/&gt;
    &lt;Number name="timestamp" size="24" endian="big" signed="false"/&gt;
    &lt;Number name="timestampi" size="8" endian="big" signed="false"/&gt;
    &lt;Number name="streamid" size="24" endian="big" signed="false"/&gt;
    &lt;Number name="firstbyte" size="8" endian="big" signed="false"/&gt;
    &lt;Blob name="data2" lengthType="calc" length="int(self.find('datasize').getInternalValue())-1"/&gt;
    &lt;Number name="lastsize" size="32" endian="big" signed="false"/&gt;
&lt;/Block&gt;
```

**3.这部分是audio tag部分的编写**

先看一下这部分的结构

[![](./img/85524/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01efe5562ba5760018.png)

然后我们对比模板来看：



```
UINT    type : 8;
    UINT    datasize : 24;
    UINT    timestamp : 24;
    UINT    timestamphi : 8;
    UINT    streamid : 24;
    taglen = datasize - 1;
    Printf("tag length: %xn",taglen);
    if(type==8)    //audio
    {
        UINT fmt : 4;
        UINT sr : 2;
        UINT bits : 1;
        UINT channels : 1;
        if(fmt==10)
        {
            --taglen;
            UBYTE frmtype;
        }
    }
```

最后编写的xml如下



```
&lt;Block name="audio"&gt;
    &lt;Number name="type" size="8" signed="false" endian="big" value="8" token="true" mutable="false"/&gt;
    &lt;Number name="datasize1" size="24" endian="big" signed="false"/&gt;
    &lt;Number name="timestamp" size="24" endian="big" signed="false"/&gt;
    &lt;Number name="timestampi" size="8" endian="big" signed="false"/&gt;
    &lt;Number name="streamid" size="24" endian="big" signed="false"/&gt;
        &lt;Flags name="Flag3" size="8"&gt;
            &lt;Flag name="fmt" position="0" size="4"/&gt;
            &lt;Flag name="sr" position="4" size="2"/&gt;
            &lt;Flag name="bits" position="6" size="1"/&gt;
            &lt;Flag name="channels" position="7" size="1"/&gt;
        &lt;/Flags&gt;
        &lt;Block&gt;
            &lt;Relation type="when" when="int(self.find('Flag3.fmt').getInternalValue()) == 10"/&gt;
            &lt;Blob name="frmtype" length="1"/&gt;
            &lt;Blob name="data1" lengthType="calc" length="int(self.find('datasize1').getInternalValue())-2"/&gt;
        &lt;/Block&gt;
        &lt;Block&gt;
            &lt;Relation type="when" when="int(self.find('Flag3.fmt').getInternalValue()) != 10"/&gt;
            &lt;Blob name="data1" lengthType="calc" length="int(self.find('datasize1').getInternalValue())-1"/&gt;
        &lt;/Block&gt;
    &lt;Number name="lastsize" size="32" endian="big" signed="false"/&gt;
&lt;/Block&gt;
```

**4.这部分是video tag的部分的编写**

先来看一下video tag的结构

[![](./img/85524/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d4fd6b4c8ca4be40.png)

模板中的代码如下：

```
UINT    type : 8;
    UINT    datasize : 24;
    UINT    timestamp : 24;
    UINT    timestamphi : 8;
    UINT    streamid : 24;
    taglen = datasize - 1;
    Printf("tag length: %xn",taglen);
    ...
    ...
    else if(type==9)//video
    {
        UINT frmtype : 4;
        UINT codecid : 4;
        if(codecid==7)
        {
            taglen -= 4;
            UINT pkttype : 8;
            UINT compotime : 24;
        }
    }
```

我们结合两者，得到xml如下：



```
&lt;Block name="video"&gt;
    &lt;Number name="type" size="8" signed="false" endian="big" value="9" token="true" mutable="false"/&gt;
    &lt;Number name="datasize2" size="24" endian="big" signed="false"/&gt;
    &lt;Number name="timestamp" size="24" endian="big" signed="false"/&gt;
    &lt;Number name="timestampi" size="8" endian="big" signed="false"/&gt;
    &lt;Number name="streamid" size="24" endian="big" signed="false"/&gt;
    &lt;Flags name="Flag2" size="8"&gt;
        &lt;Flag name="frmtype" position="0" size="4"/&gt;
        &lt;Flag name="codecid" position="4" size="4"/&gt;
    &lt;/Flags&gt;
    &lt;Block&gt;
        &lt;Relation type="when" when="int(self.find('Flag2.codecid').getInternalValue()) == 7"/&gt;
        &lt;Blob name="pkttype" length="1"/&gt;
        &lt;Blob name="compotime" length="3"/&gt;
        &lt;Blob name="data" lengthType="calc" length="int(self.find('datasize2').getInternalValue())-5"/&gt;
    &lt;/Block&gt;
    &lt;Block&gt;
        &lt;Relation type="when" when="int(self.find('Flag2.codecid').getInternalValue()) != 7"/&gt;
        &lt;Blob name="data" lengthType="calc" length="int(self.find('datasize2').getInternalValue())-1"/&gt;
    &lt;/Block&gt;
    &lt;Number name="lastsize" size="32" endian="big" signed="false"/&gt;
&lt;/Block&gt;
```



**0x05: swf加载样本**

现在，pit file搞定了，下面就是swf了~

使用as语言编写的代码，编译后得到swf文件



```
package
{
    import flash.display.Sprite;
    import flash.net.*;
    import flash.media.*;
    import flash.utils.*;
    import flash.display.*
    import flash.events.*;
    import flash.system.fscommand;
    import flash.display3D.textures.VideoTexture;
    public class Main extends Sprite
    {
        public function Main():void
        {
            var video:Video;
            var netCon:NetConnection;
            var stream:NetStream;
            function loadVideo(url:String):Video
            {
                video = new Video();
                netCon = new NetConnection();
                netCon.connect(null);
                stream = new NetStream(netCon);
                stream.play(url);
                var client:Object = new Object();
                client.onMetaData = onMetaEvent;
                stream.client = client;
                stream.addEventListener(NetStatusEvent.NET_STATUS, netStatus);
                video.attachNetStream(stream);
                return video;
            }
            function onMetaEvent(e:Object):void
            {
            }
            function netStatus(e:NetStatusEvent):void
            {
                video.width  = stage.stageWidth;
                video.height = stage.stageHeight;
            }
            stage.addChild(loadVideo("fuzz.flv"));
        }
    }
}
```



**0x06: 自动化fuzz脚本**

我这里只使用peach生成了样本，并没有使用peach的Run Block。剩下的fuzz的工作，是我自己写脚本搞定的。

核心部分的代码如下。



```
def run(fileID):
    copyFile(fileID)
    subprocess.Popen(runCmd)
    #sleep(2)
    checkCrash()
    #sleep(1)
    clean()
```

首先会拷贝一个样本文件到工作目录



```
def copyFile(fileID):
    shutil.copyfile(fileDict.get(fileID),workDir+"fuzz.flv")
```

然后开始一轮的fuzz



```
fuzzFilename = "fuzz.swf"
programName = "flashplayer_22_sa_debug.exe"
runCmd = programName +" "+ fuzzFilename
subprocess.Popen(runCmd)
```

然后是异常检测(不优雅的方法…TAT)



```
def checkCrash():
    winDbg = "windbg.exe"
    #get process list
    try:
        processList = psutil.process_iter()
    except Exception as e:
        print e
    for p in processList:
        if(p.name == winDbg):
            print "[#]Crash Found! Writing to log now ..."
            log(fileID)
            sleep(1)
            p.kill()
        else:
            pass
```

最后就是收尾的工作了



```
def clean():
    subprocess.Popen(killProgram)#kill programName for next one 
    sleep(1)
    if(os.path.exists(workDir+"fuzz.flv")):
        os.remove(workDir+"fuzz.flv")
```



**0x07: 结束语**

我这个东西只能叫toy吧，效率低下，简单粗暴。但是过程中是学习到不少东西，之后的打算是多看一些论文，多学习一些漏洞挖掘的方法，之前尝试了结合winafl来搞，不过问题很多，有待解决…慢慢来吧，欢迎有兴趣的同学一起交流~

所有的东西我都丢github了，有啥错误欢迎各位师傅留言或者邮件o0xmuhe#gmail.com联系我 传送门在这里：[fuzz with peach](https://github.com/o0xmuhe/filefmt_fuzz_with_peach)。

<br>

**0x08: 参考**

[【原创】文件Fuzz教程之一：Peach语法介绍](http://bbs.pediy.com/showthread.php?t=176416)

[flv文件格式详解](http://blog.useasp.net/archive/2016/02/28/The-flv-video-file-format-specification-version-10-1.aspx)

[peach 文档](http://www.peachfuzzer.com/resources/peachcommunity/)

[Fuzzing with Peach – Part 1 « Flinkd!](http://www.flinkd.org/2011/07/fuzzing-with-peach-part-1/)
