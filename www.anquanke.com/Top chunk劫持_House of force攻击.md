> 原文链接: https://www.anquanke.com//post/id/175630 


# Top chunk劫持：House of force攻击


                                阅读量   
                                **294362**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01ffc345703044cbd2.jpg)](https://p4.ssl.qhimg.com/t01ffc345703044cbd2.jpg)



## 一、序言

这篇文章我们一起继续堆漏洞的学习。之前的文章已经阐述了unsorted bin、fastbin、tcache的漏洞利用，这篇文章我们来讲一个top chunk的漏洞利用手段。

由于没有找到较新的题目，我们就暂且用2016 bctf bcloud这道比较老的题目为例进行讲解。



## 二、top chunk的分割机制与利用点

众所周知，top chunk的作用是作为后备堆空间，在各bin中没有chunk可提供时，分割出一个chunk提供给用户。那么这个分割过程是怎样的呢？我们来参照一份源码：

首先是libc会检查用户申请的大小，top chunk是否能给的起，如果给得起，就由top chunk的head处，以用户申请大小所匹配的chunk大小为偏移量，将top chunk的位置推到新的位置，而原来的top chunk head处就作为新的堆块被分配给用户了：试想，如果我们能控制top chunk在这个过程中推到任意位置，也就是说，如果我们能控制用户申请的大小为任意值，我们就能将top chunk劫持到任意内存地址，然后就可以控制目标内存。

众所周知，pwn中劫持内存常常劫持的是malloc_hook、got表等指针，与堆空间中的top chunk相距甚远，远到所需要申请的size必定超出top chunk现有的大小（甚至有时劫持目标内存地址低于top chunk，我们需要申请负数大小的堆，转成unsigned int后会变成非常大的数），便无法通过上述源码中的大小检查，怎么破呢？

观察源码可见：大小检查时用的数据类型是unsigned int，马上就可以想到，如果能通过某些漏洞（比如溢出）将top chunk的size字段篡改成-1，那么在做这个检查时，size就变成了无符号整数中最大的值，这样一来，不管用户申请多大的堆空间，管够！

此外，虽然此处的检查中，用户申请的大小也被当做无符号整型对待，但是在后面推top chunk的时候是作为int对待的，因此如果劫持目标内存地址比top chunk低，我们申请负数大小的内存是可以劫持过去的！

这样一来，打top chunk的思路就出来了：篡改top chunk的size为-1，然后劫持到任意内存

**这种攻击手段成为House of force（hof），能够进行hof攻击需要满足两个条件：**
1. **用户能够篡改top chunk的size字段（篡改为负数或很大值）**
1. **用户可以申请任意大小的堆内存（包括负数）**


## 三、计算劫持偏移量的注意点

首先劫持目标地址应该做为用户区而不是堆块的头部（因为你要写啊！），第二点是top chunk推的时候应该推到劫持目标地址对应堆块的头部，这个长度不等于你所申请的长度，而等于你所申请的长度加上size_head。

基于以上两点，我们的计算过程应当是：首先确定劫持目标内存地址，然后将此处看作堆块用户区算出其头部地址，然后用这个头部地址减去top chunk head地址得到一个offset，然后实现劫持需要申请的用户区大小即为offset – size_head（若涉及到重用对齐什么的自己按这个原则分析即可）。



## 四、bctf 2016-bcloud逆向分析与漏洞挖掘

题目文件网上不难找到，此处就不提供了咕咕咕~

### 0x00.预备工作：

首先看保护：

可见程序是32位的，没开pie、relro也没全开（疯狂暗示可以打got表了）

然后看libc版本：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://ma9p13.files.wordpress.com/2019/03/1-1.jpg)

很明显，libc2.23，但是有一点很奇怪，感觉出题人对libc文件动过手脚，虽然system的偏移与笔者自己libc2.23系统是完全一样的，然而ida里搜字符串却找不到”/bin/sh”，我们暂且认为是出题人想让我们自己构造吧，影响不大。

### 0x01.逆向分析与漏洞挖掘：

（部分函数名、变量名已经笔者重命名）

### 1、main函数：

[![](https://ma9p13.files.wordpress.com/2019/03/2-1.jpg)](https://ma9p13.files.wordpress.com/2019/03/2-1.jpg)

### 2、register函数：

[![](https://ma9p13.files.wordpress.com/2019/03/3-1.jpg)](https://ma9p13.files.wordpress.com/2019/03/3-1.jpg)

### 2.1、reg_name函数：

[![](https://ma9p13.files.wordpress.com/2019/03/4-1.jpg)](https://ma9p13.files.wordpress.com/2019/03/4-1.jpg)

### 2.1.1、name_input函数：

[![](https://ma9p13.files.wordpress.com/2019/03/5-1.jpg)](https://ma9p13.files.wordpress.com/2019/03/5-1.jpg)

到这里先停一下，我们看到在name_input函数中，用户申请的整个长度全部读入了值，这是明显的字符串无截断漏洞的特征，常用于内存泄露甚至间接引发溢出；此外，在申请长度全部读入的情况下，最后的*(i + a1)会造成off by one；通常见到漏洞我们都是喜悦的，然而有时并非如此，比如这个off by one，不但对我们漏洞利用没有起到任何好作用，而且还成为了我们的阻碍，后面分析exp的过程中我们将体会到！

现在确定了此处有字符串截断缺失，那么再看外层的reg_name函数，执行完name_input后通过leak_echo函数打印了欢迎信息：

### 2.1.2、leak_echo函数：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://ma9p13.files.wordpress.com/2019/03/6-1.jpg)

之前输入的name字符串存在的截断缺失在这里就可以利用了，在外层reg_name函数中，name字符串就是栈变量s，而s和分配的堆块指针v2相邻，恰好隔了0x40的偏移，因此只要我们在输入name的时候输入0x40个A，此处就可以通过printf泄露v2指针的值，即泄露了堆地址；此外，name_input函数中最后的置零没有影响，虽然起初的置零会把v2覆盖为零，但是malloc是在此之后的。

### 2.2、reg_orghost函数：

[![](https://ma9p13.files.wordpress.com/2019/03/7-1.jpg)](https://ma9p13.files.wordpress.com/2019/03/7-1.jpg)

这里又调用了name_input那个函数来读入内容，我们看看会造成什么漏洞：

首先确定name_input里最后的置零在这里也没有不良影响，因为malloc是在此之后的。

然后受name_input影响而缺失截断的字符串是栈上的s和v3，现在我们看第20行的strcpy，由于&amp;s处的字符串缺失截断符号，我们输入0x40个A后就紧接上了栈上的v2，v2是堆指针，四个字节大概率都不为截断值，因此strcpy的拷贝不会停下，再继续往下就到了栈上的v3了，也就是另外一个我们输入的字符串，因此会继续拷贝v3这个字符串中的内容。那么拷贝到了哪呢？拷贝目标内存是v2，也就是malloc到的一个chunk，由于v2分配的最晚（此前又没有free，所有bin均空），因此v2所指的这个chunk正是与top chunk相邻的，因此这里的拷贝把0x40的垃圾数据拷贝满这个chunk后，再拷贝就会覆盖到top chunk的头部了：v2的值四字节填上了top chunk的presize，v3字符串的前四个字节则会覆盖掉top chunk的size字段，由于v3字符串的内容是由我们随意控制的，我们就**能够将top chunk的size字段篡改为FF FF FF FF，即-1**，实现了House of force攻击的第一步！

### 3.new函数：

[![](https://ma9p13.files.wordpress.com/2019/03/8-1.jpg)](https://ma9p13.files.wordpress.com/2019/03/8-1.jpg)

很明显：lenth值是由我们任意控制的，即使输入负数也没有相应的检查，这就满足了House of force攻击的第二个条件：**用户可以申请任意大小的堆空间**！malloc那里有个+4，写exp的时候别忘了。

注意！这里又调用了name_input函数！里面存在的那个off by one真的烦！待会分析exp，大家好好体会！

### 4.show函数：

骗人的啥都没有，大家自己看吧。

### 5.edit函数：

[![](https://ma9p13.files.wordpress.com/2019/03/9-1.jpg)](https://ma9p13.files.wordpress.com/2019/03/9-1.jpg)

无甚可说，自行审。

### 6.delet函数：

[![](https://ma9p13.files.wordpress.com/2019/03/10-2.jpg)](https://ma9p13.files.wordpress.com/2019/03/10-2.jpg)

正常释放，没啥好说的。

### 7.syn函数：

也是糊弄人的，没啥用。



## 五、漏洞利用与exploit开发

经过上面的分析我们已经知道存在HOF漏洞，我们可以较轻松的劫持top chunk到任意位置并分配到任意地址内存，因此get shell最好的选择莫过于攻击GOT表，劫持到system函数。

应运而生的需求便是泄露libc_base了，我们刚才也看到了，show函数里啥都没有是糊弄人的，因此我们无奈之下只能先通过HOF劫持某个库函数的GOT表到有打印功能的函数，比如puts啦、printf啦、甚至是该程序中的leak_echo函数，由于泄露libc_base前puts、printf的地址我们不得而知，因此我们在此选择leak_echo函数。

那么leak_echo的参数就是我们想要泄露的某个函数的got表地址即可。

这里的“某个函数”的选取需要注意一下，比如read就不能选，因为逆一下libc文件就会发现read在libc中偏移量的最低字节是00，因此实际地址最低字节也是00，leak_echo中的printf会截断打印无法完成泄露，在此我们选printf_got下手。

那怎么把printf_got地址作为参数传进去呢？我们观察new函数的代码就可以注意到：lenth作为malloc的参数，其值是可以随意设置的，如果我们通过HOF将malloc_got篡改为leak_echo的地址，输入lenth的时候再将lenth + 4设置为printf_got的地址，那么在调用malloc(lenth + 4)时实际执行的则是leak_echo(printf_got)，但是这里伴随的问题也来了：got表中malloc下面紧跟着puts，而之前分析过name_input函数里的off by one会破坏puts_got的最低字节，而在整个操作过程中所调用的函数又会执行到puts，那puts_got既然被破坏就很有可能导致程序崩溃，笔者自己想了个办法，就是把puts_got索性一起改了，改成printf_plt，因为在没有格式化代换时他俩几乎就是一样的，但是got表中puts后面紧跟的__gmon_start__又被off by one破坏了，幸好破坏它不影响什么。

笔者按照这个思路继续尝试，又发现了问题：malloc被篡改成leak_echo后，返回值变成了puts的返回值（读者去看源码就知道了），即打印的字符个数，但是问题来了，puts函数没崩，但是也没成功打印，那返回值到底会是啥呢？如果是0，那完了，根据源码就直接exit(-1)了；那若侥幸不是0，大概率返回的数如果作为地址的话对应的也极可能不是个可写的内存空间，那么进到name_input中以后第一次执行完read后不管是不是’n’，都会在这个大概率不可写的地址处强行写东西，便直接段错误搞崩了，于是笔者灵机一动：如果我让name_input中的read函数第一次执行就返回0呢？只要传进个eof就行了，然后就会执行exit(-1)，exit的got表位置又紧跟着__gmon_start__，好，那一不做二不休我们干脆在当初篡改malloc_got的时候一起把exit也劫持了，劫持到new函数中name_input的后面就好了！且慢还要注意一个问题，new中实际分配的大小是lenth + 4，按我们这个搞法，从malloc到exit是四个got表，再加上4，再考虑上堆块重用，那搞完后top chunk head就指向got中的下面紧跟着的__libc_start_main了，而top chunk的size字段则会破坏setvbuf_got，所幸没有影响到还会调用到的函数，虚惊一场！等一下，还有，malloc_got作为堆块用户区了，那么此堆块的头部位置也对应了一些函数的got表，可能也会被破坏，去查看发现是__stack_chk_fail和strcpy，后续不会调用，忽略即可，刺激！

多么神奇的思路！然而人算不如天算，笔者高兴了没几分钟就发现：exit劫持到new函数的后面那部分时，由于是直接强行劫持过去的，并没有正常函数调用开头保存ebp、更新ebp的步骤，ebp还是name_input里的ebp，堆栈不平衡，很有可能就直接崩了；退一万步讲，即使没崩：exit劫持出去以后再执行几步就要retn，retn到哪？到exit后面，也就是又滚回了name_input里面，然后又会继续执行到大概率引发段错误的写操作。这么一来就知道，按这思路想利用起来难于上青天。那么exit就不能劫持到new函数中的后半部分了，我们起码最好劫持到一个完整函数的开头保证堆栈平衡；那么先想想现在泄露了printf_got，算出了libc基址，得到了system地址，下一步要做的就是劫持某个函数指向system然后想办法传’/bin/sh’拿shell.

如果我们将exit劫持到edit函数呢？edit函数的写操作给了我们一次珍贵的劫持某函数got表的机会，或许我们有希望从中get shell，但是我们必须清楚的认识到一个现实：那就是我们必须在edit函数retn之前get shell，如果在edit函数retn之前我们不能get shell，那一旦retn回name_input函数，就会执行引发段错误的写操作，程序崩掉！

那我们首先看看我们能够劫持的函数got表有哪些：只有malloc、puts、exit，而在edit函数retn前能够被调用的函数只有puts了（只有puts在edit中的name_input函数后面调用，而name_input函数就是edit中进行这个篡改写操作的），然而puts的参数并不是”/bin/sh”，因此我们将puts篡改为system地址是行不通的，那唯一的希望就是onegadget了！然而文章前面也向大家提到了，这个题目提供的libc做了手脚，不是原版的libc2.23，里面没有”/bin/sh”字符串，也就没有onegadget，那么如果我们是在实际打CTF比赛，有两种可能性：一、远程主机上运行的linux系统用的是原版的完整的libc2.23，只是提供给选手的libc文件做了手脚而已    二、远程主机上的libc就是这么个做了手脚的libc。如果是在比赛中走投无路，只能碰运气试一试了，有很大可能是会成功的！因此我们就用自己的libc2.23的库文件来尝试：

然而问题又来了：打payload的时候怎么能直接只传一个eof过去？这个问题令笔者彻底自闭了，笔者尝试了send空字符串，然而并不好使，又在网上查到手输ctrl+D表示eof，笔者于是尝试使用r.interactive()切入交互模式之后，手打ctrl + d，结果却并不如人意：

首先如果不用通过exp脚本，而是直接运行原程序，然后attach进程下断点于call exit，read时直接手输ctrl + d，调试器是可以成功在断点处断下的，继续运行也能正常exit退出：

[![](https://ma9p13.files.wordpress.com/2019/03/11-2.jpg)](https://ma9p13.files.wordpress.com/2019/03/11-2.jpg)

然而如果在exp脚本中运行，在r.interactive()之后手输ctrl + d，虽然call exit处的断点也能断下，但是却报错了，n继续运行时也报错崩掉了：

[![](https://ma9p13.files.wordpress.com/2019/03/12-2.jpg)](https://ma9p13.files.wordpress.com/2019/03/12-2.jpg)

[![](https://ma9p13.files.wordpress.com/2019/03/13-1.jpg)](https://ma9p13.files.wordpress.com/2019/03/13-1.jpg)

笔者感觉这种办法可能已经很接近答案了、也可能这个操作是根本无法完成的，我问过H4lo师傅，他的看法是eof是由服务器端来添加上的，如果是这样的话那估计这种思路就没法实现了，总之由于时间和精力原因，笔者最终没有尝试出来，如果有大佬能继续鄙人的这个思路解决这个问题做出来，跪求评论区分享一下做法！Orz！！下面给出作者按照这个思路写的exp（exp到泄露libc_base的部分全都是成功的）：

[![](https://ma9p13.files.wordpress.com/2019/03/14-4.jpg)](https://ma9p13.files.wordpress.com/2019/03/14-4.jpg)

按思路运行到这里就应该手输ctrl + d了，可以看到泄露地址是正确的。

### 换思路：

以上思路行不通，我们还是换思路吧。

首先我们还是要泄露内存，没有自带的打印功能，我们还是得篡改某个库函数got表为leak_echo函数，而且这个被篡改的库函数的参数我们还得能控制，而篡改malloc_got的下场上面我们已经见识过了，那么在仅有的这几个可怜的libc函数中，有可能我们能控制其参数的也就只有free函数了，它在delet函数中：

可见free如果被劫持，执行完了以后就直接return了，不会有像new函数中那么多破事儿，而且其参数是ptr，也就是idx_table_bss[idx]，也就是说如果我们能控制idx_table_bss[idx]的值，就可以控制参数了，显然正常情况下这个值不能由我们控制，必须通过hof劫持idx_table_bss才行；另一边，如何篡改free_got呢？巧了，如果我们控制了idx_table_bss，那么在执行edit的时候，不就想写哪就写哪了吗！一举两得，思路正是hof劫持idx_table_bss！

我们将idx_table_bss的前几项依次部署为：
- Free_got
- Printf_got
- &amp;idx_table_bss[3]
- “/bin”
- “/shx00”
我们则可以先edit(0)将free_got篡改为leak_echo函数，然后delet(1)将以idx_table_bss[1]即printf_got为free（现已为leak_echo）的参数，调用leak_echo泄露出printf地址并进一步计算出system_addr，再重复第一步的edit(0)将free_got再篡改为system地址，然后再执行delet(2)，将以&amp;idx_table_bss[3]即”/bin/shx00″字符串的地址为free（现已为system）的参数，调用system拿到shell！

注意：第一次new的时候我们是把top chunk劫持到了idx_table_bss，此时lenth_table_bss[0]处就已经被赋值了，我们第二次new的时候才来向idx_table_bss写内容部署如上，此时写入的部署内容的长度是被写入到lenth_table_bss[1]的，但是我们edit(0)的时候用的却是lenth_table_bss[0]记录的长度，也就是当初hof时输入的负数值，因此传入edit中name_input函数的lenth参数由于是负数便不进for循环，也便没能正常read我们的部署内容，因此此处实际应当edit(1)才是，edit(1)时用的是lenth_table_bss[1]，这个长度值没毛病，所以对应的，我们idx_table_bss前几项的部署内容应该是：
- p32(0)
- Free_got
- Printf_got
- &amp;idx_table_bss[3]
- “/bin”
- “/shx00”
对应操作步骤也相应变成了：edit(1)，delet(2)，再edit(1)，然后再delet(3)get shell。

给出exp：

注意我们edit函数的payload末尾加上了’n’，这是必要的，因为payload长度比lenth_table_bss中对应的长度短，必须用’n’来结束读入，否则会一直等输入。

另外一种相似的思路是，hof劫持到lenth_table_bss，多写点字节就到了idx_table_bss了，一样可以篡改，然后就可以顺便把lenth_table_bss[0]改为4，这样就可以使用上面第一种内存部署了，而且不用加’n’，不过这样要多费点时间计算偏移，我们也给出相应exp：

最后，还有一个稍不同的思路值得一提，唯一的不同就在于篡改free_got泄露内存时，我们不篡改为leak_echo函数，而是篡改到puts_plt（或printf_got），然而事情没有这么简单，比如说劫持到puts_plt吧，那我们泄露时就直接：

看似顺理成章，然而这样对吗？如果你这样改发现是调不通的，因为我们看exp中delet函数的定义用的是r.recvuntil(“Input the id:”)，而原程序中是用的puts来打印”Input the id:”的，当用delet中的recvuntil的时候实际上还有一个换行符没接到！！因此exp就会卡在那儿！照原来劫持到leak_echo的情况，我们有个r.recvuntil(‘Hey ‘)可以继续执行下去，可是劫持到puts_plt的话就必须在r.recv(4)之前来个r.recvline()来冲掉那个换行符：



## 六、总结与心得
1. pwn选手的脑子应该有灵性，应该尤其懂得剑走偏锋，也要考虑周全面面俱到，一个思路走不通要学会换思路，exp开发要注意微妙的耦合效应！
1. 有时候看到某些漏洞不要急着开心，有可能看起来是漏洞，其实是个坑！比如此例中的off by one。
1. 由于plt表的本质是个jmp，所以从抽象的角度看劫持到plt和劫持到真正的函数地址是等价的，但是注意目标plt对应的got表可不能被破坏啊。
最后希望过路的大佬们如果有对前面所提EOF的问题有解决方法的，有劳评论区分享一下Orz~~
