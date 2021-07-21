> 原文链接: https://www.anquanke.com//post/id/228880 


# INCASEFORMAT蠕虫病毒网络传播风险通告


                                阅读量   
                                **194045**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t0140965fcfbb220708.png)](https://p5.ssl.qhimg.com/t0140965fcfbb220708.png)



## 0x01 背景

1月13日，360安全大脑检测到蠕虫病毒incaseformat大范围爆发并进行了预警，此次病毒爆发涉及政府、医疗、教育、运营商等多个行业，该病毒在感染用户机器后会通过U盘自我复制感染到其他电脑，最终导致电脑中非系统分区的磁盘文件被删除，给用户造成极大损失。由于被删除文件分区根目录下均存在名为incaseformat.log的空文件，因此网络上将此病毒命名为incaseformat。

Incaseformat蠕虫病毒爆发后，部分安全厂商对incaseformat病毒的传播途径及安全评估进行了误判，错误评估该蠕虫病毒不具有网络传播性，因此360对该蠕虫的真实网络传播风险进行分析通告，希望各行业用户能够正确认识该蠕虫病毒的安全风险，有效防御此类蠕虫病毒的攻击。



## 0x02 风险通告

经360安全大脑的全网遥测分析研判发现，该蠕虫病毒默认通过U盘等存储设备、网络文件共享的本地文件传播方式以外，还有一部分经由网络进行传播。

由于该蠕虫病毒带有破坏性质的传播方法，污染了大量用户的私有数据资料文件夹，导致病毒被用户误打包为ZIP、RAR等压缩包文件，通过邮件附件、网盘共享和IM通信软件等渠道对该病毒进行了各种形式的二次网络传播。传播方式占比情况如下：

[![](https://p403.ssl.qhimgs4.com/t01856ef380fa9a9627.png)](https://p403.ssl.qhimgs4.com/t01856ef380fa9a9627.png)



## 0x03 风险分析

### 潜伏发作风险

incaseformat蠕虫病毒默认具有“潜伏发作”的特性，每隔20秒检测一次当前的时间，如果当年大于2009年，月份大于3月，日期为1号、10号、21号、29号时，病毒便会删除磁盘文件。

该蠕虫家族的部分病毒潜伏时间存在异常情况，由于时间戳转换函数的变量值被进行了人为篡改，在程序计算时间的代码中，用于表示一天的毫秒数的变量值与实际不符（正确的值为0x5265C00，程序中的值为0x5A75CC4），从而导致病毒一直处于潜伏状态，直至延期到2021年1月13日发作。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p403.ssl.qhimgs4.com/t017aa2c4c11da68f7c.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p403.ssl.qhimgs4.com/t01287b4b8d34408af2.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p403.ssl.qhimgs4.com/t01675408ff12bea4c4.png)

### 污染文件风险

该蠕虫病毒传播方式十分狡猾，在进行自我复制时，会将存储设备根目录下的正常目录隐藏，将自身复制为正常目录名的EXE可执行文件，同时EXE文件后缀名也设置为隐藏，最终将自身伪装为文件夹。这种破坏性的传播方式导致用户大量私有文件资料被悄悄替换，在无防备情况下误打包或被污染进行了二次网络传播。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p403.ssl.qhimgs4.com/t01cbb97d72b548afc4.png)



## 0x04 排查建议

1、主机排查

排查主机Windows目录下是否存在图标为文件夹、文件名为tsay.exe、ttry.exe的可疑文件，若存在该文件及时删除。

2、U盘等存储设备排查

排查U盘等存储设备内是否存在图标为文件夹，但后缀名为exe的可疑文件，若存在该文件及时删除。

3.使用安全软件排查



## 0x05 产品侧解决方案

### 360安全分析响应平台

360安全大脑的安全分析响应平台通过网络流量检测、多传感器数据融合关联分析手段，对该类漏洞的利用进行实时检测和阻断，请用户联系相关产品区域负责人或(shaoyulong#360.cn)获取对应产品。

[![](https://p403.ssl.qhimgs4.com/t01cf89977f13be2eff.jpeg)](https://p403.ssl.qhimgs4.com/t01cf89977f13be2eff.jpeg)

### 360安全卫士个人版

针对本次安全事件，用户可以通过安装360安全卫士并进行全盘杀毒来维护计算机安全。360CERT建议广大用户使用360安全卫士定期对设备进行安全检测，以做好资产自查以及防护工作。

[![](https://p403.ssl.qhimgs4.com/t0171f9ef7013bfdda9.png)](https://p403.ssl.qhimgs4.com/t0171f9ef7013bfdda9.png)

### 360安全卫士团队版

针对本次安全事件，用户可以通过安装360安全卫士并进行全盘杀毒来维护计算机安全。360CERT建议广大用户使用360安全卫士定期对设备进行安全检测，以做好资产自查以及防护工作。

[![](https://p403.ssl.qhimgs4.com/t010390805f5f3b4417.png)](https://p403.ssl.qhimgs4.com/t010390805f5f3b4417.png)



## 0x06 附录

### IOC

注: INCASEFORMAT蠕虫同源样本量巨大，更多情报请咨询360情报云（ti.360.cn）。

```
4b982fe1558576b420589faa9d55e81a 
1071D6D497A10CEF44DB396C07CCDE65
002b05c3716262903cc6357e3a55d709
002c8cd04e44b21795e5730c528db65a
002d8439774cd7ae6652c8d8d8d480a5
002f850a311f325aa927f4145b7a67d6
002fb700dfe9da609fa82038c42ecc0f
002ff5a6256e0782a3b47f8a2a8caceb
003b91b926b152440361b577009c8c6b
003c70cd7e9118b3f776feff13eae888
003c143ebd45e51f999b2bd131b1a758
003d92f6399727a9ce002ddbcf82abad
003fe32e70b94a1a08b0c3ca90f792fc
0004dd064895ececb8cfa80ffac5194c
000c420538d054697a8dfa77f332a60c
000fc50f065553832628b7b87327d05f
001a7bc11a1bdbbeba65a57e274bad2e
001aa3980b8dce0cf4ea765717bd9899
001da7ea01c9dae31ea6a4478daa9b50
001dad02d20639885c6e3b263efe6e1f
001ef3049c7eddeae45937b1c1f155e1
002ad24d5a4d07b7f115797123bb735e
…..
```

YARA

```
rule incaseformat
`{`
    meta:
        description = "description"
        author = "author"
        date = "2021-01-15"
        reference = "reference"
        hash = "4b982fe1558576b420589faa9d55e81a"
    strings:
        $string1 = "C:\\windows\\ttry.exe"
        $string2 = "C:\\windows\\tsay.exe"
        $string3 = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\RunOnce"
        $timestamp = `{`c4 5c a7 05`}`
    condition:
        uint16(0) == 0x5a4d and all of them
`}`
```
