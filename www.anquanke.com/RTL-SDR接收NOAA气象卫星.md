> 原文链接: https://www.anquanke.com//post/id/219071 


# RTL-SDR接收NOAA气象卫星


                                阅读量   
                                **268587**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01b8a1d428f3e2405c.jpg)](https://p5.ssl.qhimg.com/t01b8a1d428f3e2405c.jpg)



## 前记

在很早之前，就有写关于NOAA气象卫星的想法，但是中途因为事情比较多(其实就是比较懒)，所以这篇文章现在才发布出来。在操作的时候，也看过网上的一些文章，总结了一下经验，发现在我们实验过程中，对出现的一些问题并没有进行太多分析讲解，所以本文将会深入浅出地对操作流程以及过程中可能出现的问题进行讲解，希望能够对大家有所帮助。



## NOAA卫星

NOAA卫星是美国国家海洋大气局的第三代实用气象观测卫星，第一代称为“泰罗斯”（TIROS)系列（1960-1965年），第二代称为“艾托斯”（ITOS)/NOAA系列（1970-1976年），其后运行的第三代称为TIROS—N/NOAA系列。其轨道是接近正圆的太阳同步轨道，轨道高度为870千米和833千米，轨道倾角为98.9°和98.7°，周期为101.4分钟。NOAA的应用目的是日常的气象业务，平时有两颗卫星运行。由于一颗卫星可以每天至少可以对地面同一地区进行两次观测，所以两颗卫星就可以进行四次以上的观测。



## 实验环境

软件:<br>
WXtoimg<br>
Orbitron<br>
SDRSharp<br>
Tracking DDE插件

硬件:<br>
RTL2382U<br>
八木天线



## 插件安装

在实验之前，我们需要给SDRSharp安装DDE插件，因为在平常实验的时候并不能使用寻星仪等专业设备，又因为卫星高度、仰角等因素导致的多普勒效应的因素，所以我们需要对卫星的频率进行不断调整以达到最好的接收效果。

那么什么是多普勒频移？<br>
多普勒效应造成的发射和接收的频率之差称为多普勒频移。它揭声波的多普勒效应引起的多普勒频移声波的多普勒效应引起的多普勒频移示了波的属性在运动中发生变化的规律。

多普勒频移及信号幅度的变化等。当火车迎面驶来时，鸣笛声的波长被压缩，频率变高，因而声音听起来纤细。当火车远离时，声音波长就被拉长，频率变低，从而使得声音听起来雄浑。

**DDE插件安装**<br>
将NDde.dll、SDRSharp.DDETracker.dll、SDRSharp.PluginsCom.dll、SDRSharpDriverDDE.exe复制到SDRSharp安装目录下。<br>
然后如下图所示，在SDRSharp中添加代码，作用是在操作页面添加插件选项。

[![](https://p0.ssl.qhimg.com/t0115a370422759b2da.png)](https://p0.ssl.qhimg.com/t0115a370422759b2da.png)<br>`&lt;add key="DDE Tracking Client"  value="SDRSharp.DDETracker.DdeTrackingPlugin,SDRSharp.DDETracker" /&gt;`

然后打开Orbitron

[![](https://p4.ssl.qhimg.com/t01c3e1f0f078be7e76.png)](https://p4.ssl.qhimg.com/t01c3e1f0f078be7e76.png)

点击旋转器/电台选项，然后选择驱动程序为MyDDE，第一次会提示找不到插件程序，这时我们只需要根据提示到刚刚复制到的目录下选择SDRSharpDriverDDE.exe即可。点击驱动选择窗口右侧按钮即可使用。

[![](https://p3.ssl.qhimg.com/t0115dd1ebea8a1d585.png)](https://p3.ssl.qhimg.com/t0115dd1ebea8a1d585.png)

再次打开SDRSharp，发现左侧选项框已经出现了我们刚刚添加的插件，这时还没有安装成功，我们需要点击箭头所指处进行配置。

[![](https://p4.ssl.qhimg.com/t01acba2ccb9cd4f75f.jpg)](https://p4.ssl.qhimg.com/t01acba2ccb9cd4f75f.jpg)

点击ADD按钮，在Satallite name框中输入卫星名称，右侧框内则按照上图进行输入，什么？看不清？放大浏览器。

这时回到Orbitron，更新一下星历，如何更新就不多赘述，继续正题。为了方便大家下载，DDE插件在网上比较难找，我已经上传至github有兴趣的小伙伴可以自行下载。

DDE插件地址：

`https://github.com/wikiZ/DDE`



## 实验步骤

现在言归正传，配置好插件后，我们使用馈线连接好八木天线以及SDR设备，有条件的小伙伴可以加一个LNA效果更佳。设置好后，连接至我们的主机，使用Orbitron等寻星软件提前预测卫星过境时间，开启SDRSharp，调整频率至过境范围，值得注意的是NOAA系列卫星并不止一个，不同的卫星频率不尽相同。

初次打开WXtoimg软件，会提示输入经纬度所在地城市信息，这里我们按照自己所在的城市填写即可。如下图：

[![](https://p5.ssl.qhimg.com/t01ea8d537223194db0.png)](https://p5.ssl.qhimg.com/t01ea8d537223194db0.png)

如果提示没有输入的所在城市，那么在下面lat、lon自定义经纬度即可。设置后，如果以后想要再次调整位置信息，也可以在Options-&gt;Ground Station Location设置。

[![](https://p1.ssl.qhimg.com/t011bc1547f44f36a25.png)](https://p1.ssl.qhimg.com/t011bc1547f44f36a25.png)

然后再Options-&gt;Recording Options中对声音输入进行选择，可以看到选项soundcard中我们选择的是CABLE虚拟声卡，关于虚拟声卡的安装配置这里不多赘述，可以自行百度。在下载好虚拟声卡将这里选择为CABLE。。。即可。当然也可以有外放声卡，但是虚拟声卡录制时不会掺杂一些环境杂音，保证了接收时的音频质量。

在File-&gt;Update Keplers中更新一下开普勒，这里注意最好定期更新，保证卫星信息是准确的，在File-&gt;Satellite Pass List中查看卫星的过境时间。当然强大的Orbitron也可以进行追星并实时查看卫星图形化位置。

[![](https://p2.ssl.qhimg.com/t014428f1b7d390cffd.png)](https://p2.ssl.qhimg.com/t014428f1b7d390cffd.png)

到了最后一步，点击File-&gt;Record。

[![](https://p0.ssl.qhimg.com/t01ce3e795323aca80a.png)](https://p0.ssl.qhimg.com/t01ce3e795323aca80a.png)

记得勾选Create image(s)选项生成图片，然后点击Auto Record静静等待卫星过境吧，当然这款软件最智能的一点就在于他可以动态的获取卫星过境信息自动解码，

[![](https://p1.ssl.qhimg.com/t0137984ed2e811889e.png)](https://p1.ssl.qhimg.com/t0137984ed2e811889e.png)

可以看到在软件的最下面有准备接收的卫星信息，录制时间以及频率，这时就需要打开SDRSharp提前接收了。

[![](https://p3.ssl.qhimg.com/t01b4dcf1a1017cc457.png)](https://p3.ssl.qhimg.com/t01b4dcf1a1017cc457.png)

注意，一定要勾选这个Scheduler要不然不能实现与Orbitron的联动。

然后调整频率至137.9125MHZ，将音量调节至最大。静静等待吧。

卫星到来后，我们能明显观察到瀑布图的能量波动，以及频率跳动，也可以看到左侧我们设置的DDE插件出现了红色标语，那就说明以及成功与Orbitron联动，也可以观察到上面的频率在不断的变化。这时的频率就是接收NOAA卫星最佳频率。

[![](https://p2.ssl.qhimg.com/t019e2c63aade75a84a.png)](https://p2.ssl.qhimg.com/t019e2c63aade75a84a.png)

另一边我们看到WXtoimg也正在进行接收并解码。

[![](https://p0.ssl.qhimg.com/t01246d16a73ac84cbe.png)](https://p0.ssl.qhimg.com/t01246d16a73ac84cbe.png)

可以看到上图右下角测vol处是绿色的，数值为57.1，这说明音频的质量不错，一般数值在40以上就可以。蓝色的进度条则是解码的进度，下面的信息也可以看到卫星的仰角以及剩余接收时间等。在录制结束后软件会自动进行解码并将效果图保存。在saved images即可查看，如果想要解码为高清图，应点击选项Enhancements MSA multispectral即可。

最后效果如下：

[![](https://p0.ssl.qhimg.com/t01a9f72c167fe2645f.png)](https://p0.ssl.qhimg.com/t01a9f72c167fe2645f.png)

[![](https://p5.ssl.qhimg.com/t01cca362ab39ec3531.jpg)](https://p5.ssl.qhimg.com/t01cca362ab39ec3531.jpg)

[![](https://p0.ssl.qhimg.com/t01ca8010191d37fcc7.jpg)](https://p0.ssl.qhimg.com/t01ca8010191d37fcc7.jpg)

[![](https://p5.ssl.qhimg.com/t01120f20e7405a03f5.jpg)](https://p5.ssl.qhimg.com/t01120f20e7405a03f5.jpg)



## 问题总结

因为在市区，附近干扰较强导致卫星信号质量并不是很好，所以没有录制出高清云图。所以以下对在实验中可能出现的问题进行总结。

1、首先，一定有很多小伙伴使用hackrf设备，这里说明hackrf本身是一个很好的设备，但是在这里他的灵敏度委实是一个硬伤，这一点使用低廉的RTL系列的电视棒接收时也能明显感受灵敏度的差异，所以不建议在接收云图时使用。

2、再就是淘宝上的一款小环天线，那也是一款很不错的天线，但是并不适用在我们所要做的实验，他在接收短波时效果很好，但是接收NOAA卫星时效果不佳。

3、这里最推荐大家使用的是四臂螺旋天线，我认为这是接收卫星信号时的首选，在咸鱼就有，当然也可以自己制作，但是比较麻烦，不建议新人去做。其次就是八木天线，在接收时也要比一些SDR设备附赠的天线效果好得多。

4、注意馈线过长也会导致接收信号的质量。<br>
5、一定要耐心操作，因为在实验过程中，确实有很多容易疏忽的地方。<br>
6、懒得自己配置插件的小伙伴可以下载搭好的环境，但还是建议自己配置一遍试试。

`https://github.com/wikiZ/SDRSharpQPSK`



## METEOR M2卫星

其实能够接收的气象卫星并不止NOAA，比如METEOR M2、日本的GMS系列都是很好的选择，相比于NOAA，METEOR M2卫星的过境频率就少的可怜了，大概只有每天的早晨7、8点时卫星高度以及各方面都适合接收。这里就不再单独讲解，感兴趣的小伙伴可以看以下文章了解。

`bilibili.com/read/cv2527746/`



## 后记

那么我们本次的文章就先到这里，这里想要说的是WXToimg已经好几年没有更新过了，所以存在很多bug比如接收不到彩色图等等，这里推荐小伙伴可以去看看NOAA-APT等等解码软件，当然包括SDRSharp这些软件都不是固定的，仍然可以根据实际情况进行选择。像接收软件在linux中gqrx也是不错的选择，至于之前提过的接LNA，我觉得并不是必要的，所以还是应该贴合具体环境配置。有任何问题欢迎留言。

**最后祝大家心想事成，美梦成真！**
