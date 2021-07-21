> 原文链接: https://www.anquanke.com//post/id/231440 


# IOT安全（二）——再探stm32


                                阅读量   
                                **125590**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01b15c68204435f7d3.jpg)](https://p5.ssl.qhimg.com/t01b15c68204435f7d3.jpg)



上一篇文章中我们实现了stm32的gpio操作，这次我们将更进一步，继续完成对题目的复现。

通过之前的学习相信大家都掌握了学习阅读官方手册的能力，在本篇中为了节约篇幅不再进行对寄存器的位、寄存器代码编写的详细说明，而是着重讲解原理和背后的知识。



## 简单的时钟树

对于任何的计算机来说，时钟都是其至关重要的一环，在任何stm32的程序启动前，都必须要进行时钟的初始化操作，好在stm32的时钟较为简单，这次我们的目标就是编写我们自己的时钟初始化函数，来替换掉stm32cube为我们生成的代码。我们先来看一下手册中给出的时钟树图：

[![](https://p0.ssl.qhimg.com/t0191f66905a3a916bc.png)](https://p0.ssl.qhimg.com/t0191f66905a3a916bc.png)

可以看到时钟树整体并不复杂，但是因为stm32提供了包括usb、dma在内的多种功能，所以会用到多种频率不同的时钟信号，因此图中有很多涉及到时钟频率缩放的部件，这是我们要关注的一个点，此外，可以看到外设部分几乎都是有sysclk进行简单变化后得到的，所以sysclk也是我们关注的重点。

从最左边开始，首先是osc_in、osc_out、osc32_in、osc32_out、mco五部分引脚，其中带osc的我们在上一篇文章中利用stm32cube自动生成过，osc代表是来自外部的晶振，晶振通过高频震荡来提供有规律的信号，也就形成了时钟信号。实际上，在芯片内部也有晶振来提供时钟信号，但由于复杂原因，芯片内部往往难以集成高频率、高精度的晶振，无法发挥芯片的全部性能，这就需要我们在外部添加高频高精度的晶振来提供时钟信号。

mco是时钟输出引脚，可以将时钟信号输出，通过配置相应的寄存器即可实现对不同时钟信号的输出。我们暂时用不到这个功能。

从osc接入就是真正的时钟源了，外部晶振带来的时钟有两种：
- HSE是高速外部时钟的简写，晶振频率可取范围为4~16MHz
- LSE是低速外部时钟的简写，一般采用32.768KHz
上面我们也说了，除了外部接入的，还有内部集成的，也是两种：
- HSI是高速内部时钟的简写，由内部RC振荡器产生，频率为8MHz，非常非常的不稳定。
- LSI是低速内部时钟的简写，同样由内部RC振荡器产生，频率大约为40KHz
[![](https://p4.ssl.qhimg.com/t011b83d324f5cd4d3f.png)](https://p4.ssl.qhimg.com/t011b83d324f5cd4d3f.png)

首先来看下半部分，对于LSI来说，它分了两条线
- IWDG（独立看门狗）的时钟源。
- 用来作为RTC（即实时时钟）的可选项，在时钟树中，梯形表示可选项，上图中可以看到RTC有三个可选项。
这里简单说一下实时时钟是个啥，它“实时”的意思是它掉电后还继续运行，不受限制，除此之外，他就是个普通的计时器。功能很简单，但它的电路很巧妙，有兴趣的同学可以查查看看，它经常被用来实现时间戳、记录当地时间等功能。

对于LSE来说，它只是作为RTC的一个可选项，除此之外，HSE也作为RTC其中一个选项，不过其频率需要除以128，将原来高频的信号，通过电气元件，成倍的降低它们的频率，最终将原来的频率降低到我们想要的大小，也就是”分频“的意思，这是整个时钟树中最常出现的部件，图中的prescaler是“预分频”的意思，就是在某个需要的信号前对其输入信号进行“分频”。

[![](https://p4.ssl.qhimg.com/t0117bf23e82c7a93f6.png)](https://p4.ssl.qhimg.com/t0117bf23e82c7a93f6.png)

再来看上半部分，首先就是pll这个概念，它的全称是锁相环倍频输出，所谓”锁相“即保持处理后的信号与原来的基准信号的相位一致，而”倍频“就是说要提高频率。从图中可以看到，HSE经过处理后到PLLXTPRE部件，然后和HSI共同组成pllsrc的候选，最终经过PLLMUL放大频率（最高可达16倍），输出pll时钟，在别的资料中往往把pll时钟和上面提到的四种时钟共同作为stm32的时钟源，但是我们可以看到，实际上pll时钟最终还是来自HSE和HSI，pll在整个时钟树中最大的作用就是拉高了信号的频率，HSE虽然名字中带有高速，但对于某些设备（比如USB）来说还是远远不够用的，所以需要pll来倍频。

再往后就是sysclk，即系统时钟，听这名字就知道它的地位，基本上所有的外设的时钟信号，都是通过sysclk的分频得到的。它同样有三个候选人，分别是HSI、pll时钟、HSE，从图中可以看到它最高可以达到72MHZ。

而下面的css是系统时钟的监视器，因为系统时钟和外设息息相关，一旦发生问题将导致整个系统的奔溃，所以设置了css，当HSE失效时（HSE毕竟是来自外部的晶振，失效的可能性要远大于HSI），它会自动让系统时钟的来源切换为HSI，从而保证系统的稳定。

[![](https://p5.ssl.qhimg.com/t010f96af06b260149b.png)](https://p5.ssl.qhimg.com/t010f96af06b260149b.png)

再向左看就到了外设部分的，usb很简单，只是经过了分频就得到了最终的信号，其余的主要有两条“线”
- AHB，全称是Advanced High performance Bus，是一种总线，有别的部件挂载在上面，它频率高速度快，因此是“高性能”的总线，有点类似计算机的北桥，主要连接高速设备，比如内存、dma等。它是支持多主设备的总线，可以有多个主模块，信息由主模块流向从模块。
- ABP，全称是Advanced Peripheral Bus，它类似计算机的南桥，性能、频率较低，连接的都是SPI，I2C等设备，可以看到，APB分为了ABP1、ABP2两个设备，这是因为它不像AHB那样支持多主模块，它的主模块就是ABP，ABP再有两个从模块ABP1、ABP2，这两个从模块分别负责不同的设备挂载。
最后来看看mco，可以看到它来源自HSE、HSI、PLL、SYSCLK，我们可以通过设置寄存器，来让它输出这四种时钟信号。

到此为止我们就梳理完了整个stm32的时钟树，千万不要忘了上一篇文章中我们说过的重要的一点：stm32的一切都离不开寄存器，时钟也是如此，查阅手册我们可以看到时钟相关的寄存器。

[![](https://p1.ssl.qhimg.com/t017079be95c2936cd1.png)](https://p1.ssl.qhimg.com/t017079be95c2936cd1.png)

RCC_CR、RCC_CFGR是其中的关键，它们是所有部件的“头头”，它们来控制诸如HSE、PLL等设备的启动与否，分频、倍频的大小，此外，APB、AHB等等都有相应的寄存器，我们需要按照前一篇文章的办法，把他们统统写出来。这里因为代码是在是太多了，所以我只放出我写的一小部分

```
#ifndef __SysInt
#define __SysInt
#define PERIPHY_BASE ((uint32_t)0x40000000)
#define ABP1PERIPHY PERIPHY_BASE
#define ABP2PERIPHY (PERIPHY_BASE + 0x10000)
#define AHBPERIPHY_BASE (PERIPHY_BASE + 0x20000)
#define RCC_BASE (AHBPERIPHY_BASE + 0x1000)
#define __IO volatile
typedef unsigned int uint32_t;
void SetClockConfig(void);
typedef struct 
`{`
    uint32_t HSION     :1;
    uint32_t HSIRDY    :1;
    uint32_t Reserved0 :1;
    uint32_t HSITRIM   :5;
    uint32_t HSICAL    :8;
    uint32_t HSEON     :1;
    uint32_t HSERDY    :1;
    uint32_t HSEBYP    :1;
    uint32_t CSSON     :1;
    uint32_t Reserved1 :4;
    uint32_t PLLON     :1;
    uint32_t PLLRDY    :1;
    uint32_t Reserved2 :6;

`}`CR_Bit;

typedef struct 
`{`
    uint32_t SW       :2;
    uint32_t SWS      :2;
    uint32_t HPRE     :4;
    uint32_t PPRE1    :3;
    uint32_t PPRE2    :3;
    uint32_t ADCPRE   :2;
    uint32_t PLLSRC   :1;
    uint32_t PLLXTPRE :1;
    uint32_t PLLMUL   :4;
    uint32_t USBPRE   :1;
    uint32_t Reverse0 :1;
    uint32_t MCO      :3;
    uint32_t Reverse1 :5;
`}`CFGR_Bit;

typedef struct 
`{`
    uint32_t LSIRDYF   : 1;
    uint32_t LSERDYF   : 1;
    uint32_t HSIRDYF   : 1;
    uint32_t HSERDYF   : 1;
    uint32_t PLLRDYF   : 1;
    uint32_t Reverse0  : 2;
    uint32_t CSSF      : 1;
    uint32_t LSIRDYIE  : 1;
    uint32_t LSERDYIE  : 1;
    uint32_t HSIRDYIE  : 1;
    uint32_t HSERDYIE  : 1;
    uint32_t PLLRDYIE  : 1;
    uint32_t Reverse1  : 3;
    uint32_t LSIRDYC   : 1;
    uint32_t LSERDYC   : 1;
    uint32_t HSIRDYC   : 1;
    uint32_t HSERDYC   : 1;
    uint32_t PLLRDYC   : 1;
    uint32_t Reverse2  : 2;
    uint32_t CSSC      : 1;
    uint32_t Reverse3  : 8;

`}`CIR_Bit;

typedef struct 
`{`
    uint32_t LSION : 1;
    uint32_t LSIRDY : 1;
    uint32_t Reverse0 : 14;    
    uint32_t Reverse1 : 8;
    uint32_t RMVF : 1;
    uint32_t Reverse2 : 1;
    uint32_t PINRSTF : 1;
    uint32_t PORRSTF : 1;
    uint32_t SFTRSTF : 1;
    uint32_t IWDGRSTF : 1;
    uint32_t WWDGRSTF : 1;
    uint32_t LPWRRSTF : 1;


`}`CSR_Bit;

typedef struct`{`
    __IO CR_Bit CR;
    __IO CFGR_Bit CFGR;
    __IO CIR_Bit CIR;
    __IO APB2RSTR_Bit APB2RSTR;
    __IO APB1RSTR_Bit APB1RSTR;
    __IO AHBENR_Bit AHBENR;
    __IO APB2ENR_Bit APB2ENR;
    __IO APB1ENR_Bit APB1ENR;
    __IO BDCR_Bit BDCR;
    __IO CSR_Bit CSR;


`}`RCC_Type;
```

大概300多行结构体定义完毕后，我们就可以开始写时钟的初始化代码了，实际上，只要明白了逻辑，这部分代码并不难写。

首先我们需要明确的第一件事：谁才是最先启动的时钟？显然外部晶振是不能担此重任的，你总不能外部晶振不启动你就不干活了对吧？所以启动的必然是HSI和LSI，只有他们干活了我们才能继续工作，通过RCC寄存器，我们首先进行HSI使能，然后要写个while循环，一直等待直到HSI准备就绪才能开始下一步，代码如下

```
//使能HSI
    RCC-&gt;CR.HSION = 1;
    //等待HSI就绪
    while(!RCC-&gt;CR.HSIRDY);
```

接着就是启动外部晶振了，和上面的操作类似，我们这里同样while循环写死。

```
//使能HSE
    RCC-&gt;CR.HSEON = 1;
    //等待HSE就绪
    while(!RCC-&gt;CR.HSERDY);
```

接下来就是对各个设备进行简单的分频、倍频设置，我们根据自己的实际情况进行调整即可，我写了详细的注释，代码如下：

```
//调整低速APB预分频(APB1)为2分频
    //调整高速APB预分频(APB2)为不分频
    //调整AHB预分频为不分频
    //调整ADC预分频为2分频
    RCC-&gt;CFGR.PPRE1  = 4;
    RCC-&gt;CFGR.PPRE2  = 0;
    RCC-&gt;CFGR.HPRE   = 0;
    RCC-&gt;CFGR.ADCPRE = 0;

    //调整PLL输入时钟源为HSE
    RCC-&gt;CFGR.PLLSRC = 1;
    //调整PLL倍频系数为9
    RCC-&gt;CFGR.PLLMUL = 7;
    //使能PLL时钟
    RCC-&gt;CR.PLLON = 1;
    //等待PLL时钟就绪
    while(!RCC-&gt;CR.PLLRDY);
    //调整SYSCLK为PLL
    RCC-&gt;CFGR.SW = 2;
    //等待SYSCLK为PLL
    while(RCC-&gt;CFGR.SWS!=2);
```

到此，我们就简单了实现了我们自己的时钟初始化，对应如下stm32cube自动生成的函数，替换即可。

```
RCC_DeInit();    //初始化RCC

RCC_HSEConfig(RCC_HSE_ON);    //设置HSE

HSEStartUpStatus = RCC_WaitForHSEStartUp();    //等待HSE就绪

RCC_HCLKConfig();    //设置AHB时钟

RCC_PCLK2Config();    //设置高速AHB时钟
RCC_PCLK1Config();    //设置低速AHB时钟

RCC_PLLConfig();        //设置PLL

RCC_PLLCmd(ENABLE);        //启用pll

while(RCC_GetFlagStatus(RCC_FLAG_PLLRDY) == RESET)      //等待PLL工作

RCC_SYSCLKConfig();        //设置系统时钟

while(RCC_GetSYSCLKSource() != 0x08)            //判断是否系统时钟源是否为PLL

RCC_APB2PeriphClockCmd()/RCC_APB1PeriphClockCmd（）                //启动外设时钟
```



## 有些复杂的中断

在题目中使用usart传输flag，但usart作为一种通信手段，它最终还是依赖于中断机制，所以我们必须得先研究明白stm32的中断机制，才能更好的学习usart的使用。对于stm32来说，由于它依赖于ARM的内核，所以它的中断机制与ARM内核息息相关，以M3内核为例：
- m3支持256个中断，而stm32在基础上进行了删减，使用了84个中断；
- m3支持256级的中断优先级，可以做到每一个中断都有一个优先级，而stm32只保留了16级
[![](https://p1.ssl.qhimg.com/t0178c69847497d7f65.png)](https://p1.ssl.qhimg.com/t0178c69847497d7f65.png)

我们在上一篇文章中，利用stm32cube自动将其中的一个GPIO引脚“进化”为了中断exti1，大概分成了三步
- 初始化exti
- 初始化NVIC
- 编写中断服务函数
第一步中的exti是外部中断的意思，在stm32的84个中断中，有64个属于外部中断，严格来说，stm32每一个GPIO引脚都可以“进化”为外部中断，但是它规定中断以组为单位，比如PA1、PB1、PC1、PD1、PE1、PF1、PG1为一个组，图中的exti1就表示这是第一组中断组，每一个组同一时间只能有一个代表出场，一旦选择了PA1，那么剩下的组员就不能再“进化”了。

所谓“进化”，实际上就是将相应的端口映射到相应的外部事件，端口出现变化就会触发对应的外部事件，进而到外部事件的中断服务程序。可以参考下图中exit的连接方式，每一组的引脚连接到一个选择器上，然后交由对应的EXTI处理

[![](https://p2.ssl.qhimg.com/t0122293e14892e44da.png)](https://p2.ssl.qhimg.com/t0122293e14892e44da.png)

第二步是初始化NVIC，NVIC是嵌套向量中断控制器的意思，他是所有中断的归属，不管是上面的exti还是usart、usb等等最终都是NVIC，然后由NVIC传递给cpu处理，最后通过flash中断向量表确定对应中断对应的函数地址，跳转到对应的中断处理函数。NVIC提供了 43个中断通道（通道以提前分配好，比如exti1就是第7个通道，查阅手册即可），个中断通道都具备自己的中断优先级控制字节PRI_n，每4个通道的8位中断优先级控制字构成一个32位的优先级寄存器，通过设置寄存器即可改变对应的中断优先级，当有两个以上的中断到来时，NVIC会根据中断的优先级进行抉择。

但实际上，stm32虽然每个通道提供了8位中断优先级，但由于它本身只支持16种优先级，所以只有高4位是有效的，而高4位也颇有讲究，分为了抢占式优先级和响应优先级，高位为抢占式优先级，低位为响应式优先级（可以任意位数，比如1和3、2和2、4和0），他们的关系有点复杂：
- 具有高抢占式优先级的中断可以在具有低抢占式优先级的中断处理过程中被响应，也就是实现了中断嵌套。
- 同样的抢占优先级的中断如果同时到来，就根据响应优先级判断，实现了中断的判优
自动生成的代码如下：

```
NVIC_InitTypeDefNVIC_InitStructure;
NVIC_PriorityGroupConfig(NVIC_PriorityGroup_2);           //选择中断分组2
NVIC_InitStructure.NVIC_IRQChannel= EXTI1_IRQChannel;     //选择exti1
NVIC_InitStructure.NVIC_IRQChannelPreemptionPriority= 0; //抢占式中断优先级设置为0
NVIC_InitStructure.NVIC_IRQChannelSubPriority= 0;        //响应式中断优先级设置为0
NVIC_InitStructure.NVIC_IRQChannelCmd=ENABLE;            //使能中断
```

第三步是编写中断服务函数，这一步就没啥好说的了，写就完事了，唯一要注意的是，由于中断通道中EXTI0 – EXTI4这5个外部中断在不同的通道中，所以有着自己的单独的中断响应函数，EXTI5-9共用一个通道，也就只有一个中断响应函数，EXTI10-15也是共用一个中断响应函数。

```
1 void GPIO_EXTILineConfig(uint8_t GPIO_PortSource, uint8_t GPIO_PinSource)
 2 `{`
 3   uint32_t tmp = 0x00;
 4   /* Check the parameters */
 5   assert_param(IS_GPIO_EXTI_PORT_SOURCE(GPIO_PortSource));                //assert_param是对参数进行有效性检查
 6   assert_param(IS_GPIO_PIN_SOURCE(GPIO_PinSource));
 7   
 8   tmp = ((uint32_t)0x0F) &lt;&lt; (0x04 * (GPIO_PinSource &amp; (uint8_t)0x03));
 9   AFIO-&gt;EXTICR[GPIO_PinSource &gt;&gt; 0x02] &amp;= ~tmp;
10   AFIO-&gt;EXTICR[GPIO_PinSource &gt;&gt; 0x02] |= (((uint32_t)GPIO_PortSource) &lt;&lt; (0x04 * (GPIO_PinSource &amp; (uint8_t)0x03)));
11 `}`
```

上述自动生成的代码是将PD11,PD12映射到外部事件上，9、10行是关键，通过与或操作，将寄存器的值改为对应的值，进而实现目的，如果你已经按上一篇文章中所说的将GPIO及中断的寄存器全部写作结构体的话，只需要查看手册将相应的结构体赋值即可。

上述中断都是exti的内容，除了exti，还有usart等一堆的中断，这些中断不需要和外部事件映射即可使用，也就是改写了第一步，首先打开对应中断的，再交由NVIC，最终跳转至对应的处理函数。

[![](https://p5.ssl.qhimg.com/t014f45de8038e58198.png)](https://p5.ssl.qhimg.com/t014f45de8038e58198.png)

usart原理或许有些复杂，但单纯去写一个带有usart的代码却非常容易，这里我们就不再使用寄存器做操作了，我们直接采用中断的库函数来进行操作。我们在stm32cube中开启usart功能，生成的代码中会添加usart库，里面提供了数据发送、数据接收等功能，这些不是我们本节的重点，主要先来看看中断部分

```
HAL_UART_TxHalfCpltCallback();    //一半数据发送完成后的回调函数。

HAL_UART_TxCpltCallback();    //全部数据发送完成后的回调函数

HAL_UART_RxHalfCpltCallback();    //一半数据接收完成后的回调函数。

HAL_UART_RxCpltCallback();    //全部数据接收完成后的回调函数

HAL_UART_ErrorCallback();        //传输过程中出现错误时的回调函数。
```

我们只需要编写这些回调函数即可实现对应的功能，其他的诸如usb、dma等等也是类似，用起来相当方便。



## 小结

到此我们已经实现了题目中大部分内容，最后就是usart的数据传输了，下一篇文章中我们将重点讨论usart的原理与使用，并以usart为出发点，再来看看其他stm32有趣的地方
