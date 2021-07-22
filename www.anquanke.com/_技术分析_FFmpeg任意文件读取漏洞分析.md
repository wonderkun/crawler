> 原文链接: https://www.anquanke.com//post/id/86337 


# 【技术分析】FFmpeg任意文件读取漏洞分析


                                阅读量   
                                **177197**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p1.ssl.qhimg.com/t0197a437b638b91223.png)](https://p1.ssl.qhimg.com/t0197a437b638b91223.png)



360 Vulpecker团队隶属360信息安全部，致力于Android应用和系统层漏洞挖掘。我们在拿到样本后第一时间对样本进行了跟踪分析，并紧急排查了内部产品，已经推动产品进行修复。



**漏洞分析**



漏洞最初是由neex提交到HackerOne平台，并最终获得了1000$的奖励，原文链接为 [https://hackerone.com/reports/226756](https://hackerone.com/reports/226756)  。根据作者所述，该漏洞利用了FFmpeg可以处理HLS播放列表的特性，而播放列表可以引用外部文件。通过在AVI文件中添加自定义的包含本地文件引用的HLS播放列表，可以触发该漏洞并在该文件播放过程中显示本地文件的内容。

 [![](https://p3.ssl.qhimg.com/t0131ac9b7fa5f16840.png)](https://p3.ssl.qhimg.com/t0131ac9b7fa5f16840.png)

随后，Corben Douglas根据neex的报告，实现了该漏洞POC利用。整个复现过程如下所示：

 [![](https://p1.ssl.qhimg.com/t01b9d07b3eb428c5c1.png)](https://p1.ssl.qhimg.com/t01b9d07b3eb428c5c1.png)

笔者随后对生成的avi文件进行分析发现，在HLS的播放列表中，该文件通过#EXT-X-BYTERANGE控制文件的偏移地址，并在随后的空行中指定文件的URI地址。通过不断递增文件的偏移地址，该文件可以实现对本地文件的遍历显示播放。

 [![](https://p1.ssl.qhimg.com/t01636c33be9823ba53.png)](https://p1.ssl.qhimg.com/t01636c33be9823ba53.png)

通过将该AVI视频文件上传到各大视频网站中，即可在该视频播放时显示服务器端本地的隐私数据，造成本地敏感数据的泄露。同时，M3U播放列表中的URI可以改为http协议，造成SSRF攻击。

当前，该漏洞仅是在上传服务器中实现漏洞利用的。笔者在移动端实现了该漏洞利用，并可成功显示了设备中的文件内容。

[![](https://p4.ssl.qhimg.com/t01011d52254a5b051f.png)](https://p4.ssl.qhimg.com/t01011d52254a5b051f.png) 

不同于PC端的情况，在Android和iOS系统中均有沙箱机制的存在，极大的限制了该漏洞的危害程度。对于Android，该漏洞仅能读取沙箱目录下的文件内容和SD卡上的内容。

由于FFmpeg是开源的且跨平台，该漏洞影响范围还是挺大的。经测试，移动端还有许多使用了FFmpeg的产品受该漏洞的影响。目前，官方已经发布了patch补丁，通过过滤文件后缀名来阻止该漏洞的产生。

 [![](https://p3.ssl.qhimg.com/t0149897129bb40a9d0.png)](https://p3.ssl.qhimg.com/t0149897129bb40a9d0.png)



**漏洞补丁**



[](https://git.ffmpeg.org/gitweb/ffmpeg.git/commitdiff/189ff4219644532bdfa7bab28dfedaee4d6d4021?hp=c0702ab8301844c1eb11dedb78a0bce79693dec7)[](https://git.ffmpeg.org/gitweb/ffmpeg.git/patch/189ff4219644532bdfa7bab28dfedaee4d6d4021?hp=c0702ab8301844c1eb11dedb78a0bce79693dec7)

[https://git.ffmpeg.org/gitweb/ffmpeg.git/patch/189ff4219644532bdfa7bab28dfedaee4d6d4021?hp=c0702ab8301844c1eb11dedb78a0bce79693dec7](https://git.ffmpeg.org/gitweb/ffmpeg.git/patch/189ff4219644532bdfa7bab28dfedaee4d6d4021?hp=c0702ab8301844c1eb11dedb78a0bce79693dec7)

<br>

**参考地址**



[https://hackerone.com/reports/226756](https://hackerone.com/reports/226756)  

[https://hackerone.com/reports/242831](https://hackerone.com/reports/242831) 

[https://github.com/neex/ffmpeg-avi-m3u-xbin/blob/master/gen_xbin_avi.py](https://github.com/neex/ffmpeg-avi-m3u-xbin/blob/master/gen_xbin_avi.py) 




