> 原文链接: https://www.anquanke.com//post/id/172076 


# 针对过时的RNG随机数发生器的有效状态恢复攻击


                                阅读量   
                                **284394**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01591604abf01975a0.png)](https://p3.ssl.qhimg.com/t01591604abf01975a0.png)



> 作者：CryptoPentest

“Practical state recovery attacks against legacy RNG implementations”由Shaanan N. Cohney, Matthew D. Green, Nadia Heninger三位研究员发表于CCS2018会议上。论文中，作者对数百种经FIPS 140-2认证的应用ANSI X9.31随机数发生器的公开产品进行了系统研究，发现其中12个产品中使用了静态硬编码密钥，攻击者可从源代码或二进制文件中获取该密钥。 为了证明这种攻击的实用性，作者对应用FortiOS v4的 FortiGate VPN网关实施完全被动解密攻击，可在几秒钟内恢复私钥。 研究者使用主动扫描在Internet上测量此漏洞的普遍程度，并展示 状态恢复和完全私钥恢复普遍存在。 作者的工作突出显示出验证和认证过程未能在多大程度上提供适度的安全保障。论文中，作者并没有对固件逆向、/dev/uramdom实现、及攻击代码实现等具体细节做详细阐述。笔者复现了随机数生成器代码及部分攻击过程，并将扩展介绍该攻击的技术细节。



## 一、ANSI X9.17/31随机数生成标准

随机数生成是加密系统的重要组成部分。近年来，已发现许多密码系统的随机数生成器存在缺陷或被恶意植入后门。例如，Edward Snowden泄漏的文件表明NIST Dual EC DRBG标准可能设计有后门。2015年，Juniper公司透露他们的ScreenOS系列VPN设备已被修改为包含一组恶意的双EC参数，可导致VPN会话被动解密。

ANSI X9.17“金融机构密钥管理（批发）”标准由ANSI-American National Standards Institute（美国国家标准学会）于1985年首次发布，为金融行业的加密密钥生成和分发定义了一个自愿的互操作性标准。 该标准在附录C中包括伪随机数发生器（PRG），作为生成密钥素材的建议方法。 此生成器使用分组密码（在原始描述中为DES）从当前状态生成输出，并使用当前时间更新状态。

在接下来的三十年中，相同的PRG设计出现在美国政府的加密标准中，偶尔会更新新的分组密码。 1992年，ANSI X9.17-1985标准的一个子集作为FIPS标准FIPS-171被采用。FIPS-171规定“只有NIST认可的密钥生成算法（例如，ANSI X9.17附录C中定义的技术）才能使用。 1994年采用的FIPS 140-1规定模块应使用FIPS认可的密钥生成算法; FIPS 186-1是1998年采用的DSA标准的原始版本，它将X9.17 PRG列为生成私钥的批准方法。1998年的ANSI X9.31标准（作为X9.17 PRG的变体）使用双密钥3DES作为分组密码;此变体作为批准的随机数生成器包含在其他标准中，例如2004年的FIPS 186-2。NIST使用三密钥的3DES和AES作为分组密码[39]发布了此设计的扩展，正式包含在FIPS中140-2 2005年批准的随机数生成算法列表。

[![](https://p5.ssl.qhimg.com/t019d9f352e7941c806.png)](https://p5.ssl.qhimg.com/t019d9f352e7941c806.png)

ede**X(Y)表示通过DEA(Data Encryption Algorithm)算法，应用密钥**K加密，其中*K保密，但ANSI X9.31 PRG设计的NIST文档没有指定如何生成密码密钥；

V是64比特种子，同样保密；

DT是日期/时间向量，每次调用更新；

I为中间值；

64比特R生成方法如下：

```
I=ede*K(DT)
R=ede*K(I^V)    #R通过级连生成连续的随机数
V=ede*K(R^I)    #下一轮V生成方法
```



## 二、随机数状态恢复攻击

随机数生成算法详细描述如下：

K是在初始化时以某种方式生成的对称加密算法（如3DES、AES）加密密钥。随机数迭代 生成过程如下：

```
Ti = EK(current timestamp)
output[i] = EK(Ti ⊕ seed[i])
seed[i + 1] = EK(Ti ⊕ output[i])
```

直接密码分析攻击这个生成器需要对 AES（或者正在使用其它分组密码）。

当K不保密时，随机数发生器就变得十分脆弱。已知K的攻击者可以使用两个连续的输出块并猜测时间戳来恢复当前状态。单个输出块不会唯一地标识状态，但两个块几乎肯定会。中间相遇攻击算法如下：

```
seed[i + 1] = EK(output[i] ⊕ Ti)
seed[i + 1] = DK(output[i + 1]) ⊕ Ti+1
```

攻击者尝试Ti的所有可能值，并形成一个可能的种子[i + 1]值的排序列表。然后他尝试Ti + 1的所有可能值，并形成另一个可能的种子[i + 1]值的排序列表。正确的种子[i + 1]值是两个列表中出现的值。

如果只是大致知道时间戳，可以在一定范围内暴破它们，直到我们找到一对产生相等或者应用中间相遇的攻击。 如果只知道分组的部分值，则可以重新排列加密和解密，并验证块的已知部分的相等性。 一旦知道时间戳T1和T2，下一个种子就是：

```
seed[i+2] = EK(output[i + 1]  ⊕ Ti+1) 
#通过猜测下一个current timestamp，验证output[i+2]，确定确定的随机数
Ti+2 = EK(current timestamp)
output[i+2] = EK(Ti+2  ⊕ seed[i+2])
```

其中Ti+2由下一时刻的系统时间唯一确定，可通过有限穷尽，验证随机数生成的正确性。



## 三、随机数生成算法实现与攻击验证

```
#include &lt;openssl/des.h&gt;
#include &lt;openssl/rand.h&gt;
#include &lt;openssl/err.h&gt;
#include &lt;sys/time.h&gt;
#include &lt;assert.h&gt;
#include &lt;unistd.h&gt;
#include &lt;string.h&gt;

#define FIPS_RAND_SIZE_T size_t
#define SEED_SIZE    8

static unsigned char seed[SEED_SIZE];
static FIPS_RAND_SIZE_T n_seed;
static FIPS_RAND_SIZE_T o_seed;
static DES_cblock key1;
static DES_cblock key2;
static DES_key_schedule ks1,ks2;
static int key_set;
static int key_init;
static int test_mode;
static unsigned char test_faketime[8];
static int second;

void FIPS_set_prng_key(const unsigned char k1[8],const unsigned char k2[8]);
void FIPS_rand_seed(const void *buf, FIPS_RAND_SIZE_T num);
static void FIPS_rand_cleanup(void);
static int FIPS_rand_bytes(unsigned char *buf, FIPS_RAND_SIZE_T num);
static void dump(const unsigned char *b,int n);

void FIPS_test_mode(int test,const unsigned char faketime[8])
`{`
    test_mode=test;
    if(!test_mode)
    return;
    memcpy(test_faketime,faketime,sizeof test_faketime);
`}`

void FIPS_set_prng_key(const unsigned char k1[8],const unsigned char k2[8])
`{`
    memcpy(&amp;key1,k1,sizeof key1);
    memcpy(&amp;key2,k2,sizeof key2);
    key_set=1;
    second=0;
`}`

// struct timeval `{`
//     time_t      tv_sec;      seconds 
//     suseconds_t tv_usec;    /* microseconds */
// `}`;

static void FIPS_gettime(unsigned char buf[8])
`{`
    if(test_mode)
    `{`
        memcpy(buf,test_faketime,sizeof test_faketime);
        return;
    `}`
    struct timeval tv;

    gettimeofday(&amp;tv,NULL);
    buf[0] = (unsigned char) (tv.tv_sec &amp; 0xff);
    buf[1] = (unsigned char) ((tv.tv_sec &gt;&gt; 8) &amp; 0xff);
    buf[2] = (unsigned char) ((tv.tv_sec &gt;&gt; 16) &amp; 0xff);
    buf[3] = (unsigned char) ((tv.tv_sec &gt;&gt; 24) &amp; 0xff);
    buf[4] = (unsigned char) (tv.tv_usec &amp; 0xff);
    buf[5] = (unsigned char) ((tv.tv_usec &gt;&gt; 8) &amp; 0xff);
    buf[6] = (unsigned char) ((tv.tv_usec &gt;&gt; 16) &amp; 0xff);
    buf[7] = (unsigned char) ((tv.tv_usec &gt;&gt; 24) &amp; 0xff);
`}`

static void FIPS_rand_encrypt(unsigned char *out,const unsigned char *in)
`{`
    DES_ecb2_encrypt(in,out,&amp;ks1,&amp;ks2,1);
`}`

static void FIPS_rand_cleanup(void)
`{`
    OPENSSL_cleanse(seed,sizeof seed);
    n_seed=0;
    o_seed=0;
    key_init=0;
`}`

void FIPS_rand_seed(const void *buf_, FIPS_RAND_SIZE_T num)
`{`
    const char *buf=buf_;
    FIPS_RAND_SIZE_T n;

    /* If the key hasn't been set, we can't seed! */
    if(!key_set)
    return;

    if(!key_init)
    `{`
        key_init=1;
        DES_set_key(&amp;key1,&amp;ks1);
        DES_set_key(&amp;key2,&amp;ks2);
    `}`

    /*
     * This algorithm only uses 64 bits of seed, so ensure that we use
     * the most recent 64 bits.
     */
    for(n=0 ; n &lt; num ; )
    `{`
        FIPS_RAND_SIZE_T t=num-n;

        if(o_seed+t &gt; sizeof seed)
            t=sizeof seed-o_seed;
        memcpy(seed+o_seed,buf+n,t);
        n+=t;
        o_seed+=t;
        if(o_seed == sizeof seed)
            o_seed=0;
        if(n_seed &lt; sizeof seed)
            n_seed+=t;
    `}`
`}`

static int FIPS_rand_bytes(unsigned char *buf,FIPS_RAND_SIZE_T num)
`{`
    FIPS_RAND_SIZE_T n;
    unsigned char timeseed[8];
    unsigned char intermediate[SEED_SIZE];
    unsigned char output[SEED_SIZE];
    static unsigned char previous[SEED_SIZE];

    if(n_seed &lt; sizeof seed)
    `{`
        printf("n_seed&lt;sizeof(seed)!n");
        return 0;
    `}`

    for(n=0 ; n &lt; num ; )
    `{`
        unsigned char t[SEED_SIZE];
        FIPS_RAND_SIZE_T l;

        /* ANS X9.31 A.2.4:    I = ede*K(DT)
               timeseed == DT
               intermediate == I
        */
        FIPS_gettime(timeseed);

        printf("time: ");
        dump(timeseed,8);
        putchar('t');
        printf("seed1: ");
        dump(seed,8);
        putchar('t');

        FIPS_rand_encrypt(intermediate,timeseed);

        printf("I: ");
        dump(intermediate,8);
        putchar('t');

        /* ANS X9.31 A.2.4:     R = ede*K(I^V)
               intermediate == I
               seed == V
               output == R
        */
        for(l=0 ; l &lt; sizeof t ; ++l)
            t[l]=intermediate[l]^seed[l];
        FIPS_rand_encrypt(output,t);

        printf("rand: ");
        dump(output,8);
        putchar('t');

        /* ANS X9.31 A.2.4:     V = ede*K(R^I)
               output == R
               intermediate == I
               seed == V
        */
        for(l=0 ; l &lt; sizeof t ; ++l)
            t[l]=output[l]^intermediate[l];
        FIPS_rand_encrypt(seed,t);

        printf("seed2: ");
        dump(seed,8);
        putchar('n');

        if(second &amp;&amp; !memcmp(output,previous,sizeof previous))
        `{`
            printf("output is the same with the previous!n");
            return 0;
        `}`
        memcpy(previous,output,sizeof previous);
        second=1;

        /* Successive values of R may be concatenated to produce a
           pseudo random number of the desired length */ 
        l=SEED_SIZE &lt; num-n ? SEED_SIZE : num-n;
        memcpy(buf+n,output,l);
        n+=l;
    `}`
    return 1;
`}`

typedef struct
`{`
    DES_cblock keys[2];
    const unsigned char time[8];
    const unsigned char seed[8];
    const unsigned char block1[8];
    const unsigned char block100[8];
`}` PRNGtest;

/* FIXME: these test vectors are made up! */
static PRNGtest t1=
    `{`
    `{` `{` 0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07 `}`,  //key
      `{` 0x08,0x09,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f `}`,
    `}`,
    `{` 0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00 `}`,  //fake_time
    `{` 0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00 `}`,  //seed
    `{` 0x33,0xc3,0xdf,0xfe,0x60,0x60,0x49,0x9e `}`,
    `{` 0xcd,0x2b,0x41,0xaf,0x80,0x51,0x37,0xd8 `}`
    `}`;
static PRNGtest t2=
    `{`
    `{` `{` 0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff `}`,
      `{` 0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff `}` `}`,
    `{` 0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff `}`,
    `{` 0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff `}`,
    `{` 0x65,0xf1,0xa4,0x07,0x42,0x38,0xd5,0x25 `}`,
    `{` 0xbb,0x75,0x84,0x20,0x7a,0x44,0xf0,0xa0 `}`
    `}`;

static void dump(const unsigned char *b,int n)
`{`
    while(n-- &gt; 0)
    `{`
        printf(" %02x",*b++);
    `}`
`}`

static void compare(const unsigned char *result,const unsigned char *expected, int n)
`{`
    int i;

    for(i=0 ; i &lt; n ; ++i)
        if(result[i] != expected[i])
        `{`
            puts("Random test failed, got:");
            dump(result,8);
            puts("n               expected:");
            dump(expected,8);
            putchar('n');
            exit(1);
        `}`
`}`

static void run_test(const PRNGtest *t)
`{`
    unsigned char buf[8];
    int n;

    FIPS_set_prng_key(t-&gt;keys[0],t-&gt;keys[1]);
    FIPS_test_mode(1,t-&gt;time);
    FIPS_rand_seed(t-&gt;seed,sizeof t-&gt;seed);

    if(FIPS_rand_bytes(buf,8) &lt;= 0)
    `{`
        printf("FIPS_rand_bytes error!n");
        exit(2);
    `}`
    compare(buf,t-&gt;block1,8);
    for(n=0 ; n &lt; 99 ; ++n)
    if(FIPS_rand_bytes(buf,8) &lt;= 0)
    `{`
        printf("FIPS_rand_bytes error!n");
        exit(2);
    `}`
    compare(buf,t-&gt;block100,8);
    FIPS_test_mode(0,NULL);
    //FIPS_rand_cleanup();
`}`

void gen_rand(const PRNGtest *t)
`{`
   unsigned char buf[8];
    int n;

    FIPS_set_prng_key(t-&gt;keys[0],t-&gt;keys[1]);
    FIPS_rand_seed(t-&gt;seed,sizeof t-&gt;seed);

    for(n=0 ; n &lt; 8 ; ++n)
    `{`
        if(FIPS_rand_bytes(buf,8) &lt;= 0)
        `{`
            printf("FIPS_rand_bytes error!n");
            exit(2);
        `}`
    `}`
`}`

int main()
`{`
    // test where the code runs as expected
    //time is fixed = fake_time; encryption is fixed
    run_test(&amp;t1);
    run_test(&amp;t2);
    //encryption is fixed; time is current time
    gen_rand(&amp;t1);
    FIPS_rand_cleanup();    
`}`
```

代码采用C语言编写，8组测试输出结果如下：

```
time:  0d 08 71 5c 97 11 0c 00  seed1:  00 00 00 00 00 00 00 00 I:  bc 8a 0e 0a 20 5f 7e d8     rand:  34 b5 11 d5 bf 60 bc be  seed2:  f8 22 91 7a 9b a0 77 8e
time:  0d 08 71 5c e4 11 0c 00  seed1:  f8 22 91 7a 9b a0 77 8e I:  46 2d 1b 9f dc 05 6d 68     rand:  fa 45 71 c0 54 86 43 d6  seed2:  fa 22 29 55 fb fc 41 7e
time:  0d 08 71 5c ef 11 0c 00  seed1:  fa 22 29 55 fb fc 41 7e I:  bf c0 f2 6e 71 f1 82 c6     rand:  cd 5a a2 0a 47 77 31 28  seed2:  e4 fb 5a 3d 8e 9c ad c3
time:  0d 08 71 5c 12 12 0c 00  seed1:  e4 fb 5a 3d 8e 9c ad c3 I:  96 21 5f 5e b5 7b 26 4c     rand:  1a 51 52 70 54 fc 3c fd  seed2:  14 58 9b ba 46 db 10 5e
time:  0d 08 71 5c 1b 12 0c 00  seed1:  14 58 9b ba 46 db 10 5e I:  57 cc aa 31 27 0b 2d c1     rand:  43 13 3a 1f c5 3f c2 13  seed2:  50 68 a1 83 8d 62 6c 66
time:  0d 08 71 5c 22 12 0c 00  seed1:  50 68 a1 83 8d 62 6c 66 I:  98 86 5e 21 28 a4 49 1b     rand:  ac 5d c6 12 6f 74 be c9  seed2:  b9 66 32 e0 19 aa 09 a6
time:  0d 08 71 5c 2a 12 0c 00  seed1:  b9 66 32 e0 19 aa 09 a6 I:  ea dc 46 98 0f 49 bc 72     rand:  32 e0 53 ec b9 3d 36 0c  seed2:  44 66 1e ca 58 e5 2c 20
time:  0d 08 71 5c 31 12 0c 00  seed1:  44 66 1e ca 58 e5 2c 20 I:  f4 ec 47 d5 a3 48 41 f0     rand:  00 00 e2 58 e2 34 2f cb  seed2:  37 49 0d 63 08 b1 18 0b
```

时间共64位，小端存储，多次调用仅在微秒时间内发生变化。seed2和下一轮seed1相同。

攻击验证算法代码如下：

```
#include &lt;openssl/des.h&gt;
#include &lt;openssl/rand.h&gt;
#include &lt;openssl/err.h&gt;
#include &lt;sys/time.h&gt;
#include &lt;assert.h&gt;
#include &lt;unistd.h&gt;
#include &lt;string.h&gt;
#include &lt;stdio.h&gt;

static DES_cblock key1;
static DES_cblock key2;
static DES_key_schedule ks1,ks2;

DES_cblock keys[2]=
`{`
    `{` 0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07 `}`, 
    `{` 0x08,0x09,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f `}`
`}`;

void dump(const unsigned char *b,int n);
void FIPS_set_prng_key(const unsigned char k1[8],const unsigned char k2[8]);
void xor_vectors(unsigned char *in1, unsigned char *in2,
            unsigned char *out, unsigned int size);
static void FIPS_rand_encrypt(unsigned char *out,const unsigned char *in);
static void FIPS_rand_decrypt(unsigned char *out,const unsigned char *in);
int compare_seed(unsigned char *rand1 ,unsigned char *time_buf1, unsigned char *rand2, unsigned char *time_buf2);


void dump(const unsigned char *b,int n)
`{`
    while(n-- &gt; 0)
    `{`
        printf(" %02x",*b++);
    `}`
    putchar('n');
`}`

void FIPS_set_prng_key(const unsigned char k1[8],const unsigned char k2[8])
`{`
    memcpy(&amp;key1,k1,sizeof key1);
    memcpy(&amp;key2,k2,sizeof key2);
    DES_set_key(&amp;key1,&amp;ks1);
    DES_set_key(&amp;key2,&amp;ks2);
`}`

void xor_vectors(unsigned char *in1, unsigned char *in2,
            unsigned char *out, unsigned int size)
`{`
    int i;

    for (i = 0; i &lt; size; i++)
        out[i] = in1[i] ^ in2[i];
`}`

static void FIPS_rand_encrypt(unsigned char *out,const unsigned char *in)
`{`
    DES_ecb2_encrypt(in,out,&amp;ks1,&amp;ks2,1);
`}`

static void FIPS_rand_decrypt(unsigned char *out,const unsigned char *in)
`{`
    DES_ecb2_encrypt(in,out,&amp;ks1,&amp;ks2,0);
`}`

int compare_seed(unsigned char *rand1 ,unsigned char *time_buf1, unsigned char *rand2, unsigned char *time_buf2)
`{`
    unsigned char in1[8], out2[8];
    unsigned char seed1[8], seed2[8];
    unsigned char T1[8], T2[8];
    int i;

    /*
    Ti=Ek(time_buf_i)
    seed[i+1]=Ek(rand[i]^Ti)
    */
    FIPS_set_prng_key(keys[0],keys[1]);
    FIPS_rand_encrypt(T1,time_buf1);
    xor_vectors(rand1,T1,in1,8);
    FIPS_rand_encrypt(seed1,in1);
    dump(seed1,8);

    /*
    Ti+1=Ek(time_buf_i+1)
    seed[i+1]=Dk(rand[i+1])^Ti+1
    */
    FIPS_rand_encrypt(T2,time_buf2);
    FIPS_rand_decrypt(out2,rand2);
    xor_vectors(out2,T2,seed2,8);
    dump(seed2,8);

    if(memcmp(seed1,seed2,8)==0)
        return 1;
    return 0;
`}`

int main()
`{`
    unsigned char rand1[]=`{`0xfa,0x45,0x71,0xc0,0x54,0x86,0x43,0xd6`}`;
    unsigned char time_buf1[]=`{`0x0d,0x08,0x71,0x5c,0xe4,0x11,0x0c,0x00`}`;
    unsigned char rand2[]=`{`0xcd,0x5a,0xa2,0x0a,0x47,0x77,0x31,0x28`}`;
    unsigned char time_buf2[]=`{`0x0d,0x08,0x71,0x5c,0xef,0x11,0x0c,0x00`}`;

    int ret=compare_seed(rand1,time_buf1,rand2,time_buf2);
    if(ret)
        printf("mached!n");
    else
        printf("mismached!n");
`}`
```

利用测试输出的连续两组随机数及确定的时间，验证攻击算法的正确性。实验表明，验证算法正确。



## 四、存在随机数漏洞的产品攻击

X9.31随机数发生器的NIST设计描述没有规定如何生成或存储分组密码密钥。 但是，希望获得FIPS认证的供应商需要制作详细的公共“安全政策”文档，描述其加密实施和密钥管理程序。 论文对针对X9.31 PRG认证的产品的安全策略进行了系统研究，以了解有多少供应商公开记录了潜在的硬编码密钥漏洞。 作者从NIST网站获得了认证设备清单。统计结果如下：

[![](https://p4.ssl.qhimg.com/t0122a9e177240b838a.png)](https://p4.ssl.qhimg.com/t0122a9e177240b838a.png)

不安全设备的文档表明AES密钥静态存储在固件或闪存中，并在运行时加载到PRG中。共有12家供应商，涉及40个产品线。其中包括Cisco、Fortinet等大厂商。

[![](https://p4.ssl.qhimg.com/t01c57c41dc8fab3f4d.png)](https://p4.ssl.qhimg.com/t01c57c41dc8fab3f4d.png)

FortiOS 4.3的FIPS认证表明X9.31密钥是“在模块外部生成的”。作者对两个版本的FortiOS进行了逆向工程，发现他们使用相同的硬编码密钥进行X9.31实现，然后将其用作操作系统的随机数生成器。

FortiOSv4是Fortigate网络设备的嵌入式操作系统。两个镜像分别来自FortiGate 100D防火墙的固件和运行相同版本操作系统的“虚拟设备”（VM）FortiOS是一种GNU/Linux变种，具有定制的shell，其内核模块实现了硬件接口和加密功能。 内核是Linux 2.4.37。通过binwalk即可实现固件镜像解压，并对其操作系统加载。FortiOS通过导出Linux字符设备模块，在内核中实现X9.31随机数发生器。 在引导时，init进程加载模块并将/dev/urandom替换为与X9.31字符设备对应的文件系统节点。PRG实现使用对do_gettimeofday（）的调用生成时间戳，并生成包含64位时间到最接近的微秒的struct timeval。 此结构将两次复制到缓冲区中，以形成X9.31生成器的完整128位时间戳。作者对提供X9.31实现的内核模块进行了逆向工程，并找到了用于PRG的硬编码AES密钥。

### <a class="reference-link" name="%EF%BC%88%E4%B8%80%EF%BC%89HTTPS%E6%94%BB%E5%87%BB"></a>（一）HTTPS攻击

FortiOS v4使用OpenSSL实现TLS。 初始化库时，它将随机数生成方法设置为系统PRG，即X9.31实现。

TLS服务器hello random包含一个四字节时间戳，后跟两个X9.31 PRG输出的原始块，截断为28字节，允许状态恢复攻击。 但是，TLS DH密钥交换实现方式为临时静态Diffie-Hellman，每次重启后生成直至关机，不容易对服务器直接密钥恢复攻击。

### <a class="reference-link" name="%EF%BC%88%E4%BA%8C%EF%BC%89IPSec%E6%94%BB%E5%87%BB"></a>（二）IPSec攻击

IKE守护程序基于raccoon2项目侦察，使用GNU MP库编译。守护进程使用的所有随机数都是通过/dev/urandom生成，因此使用X9.31模块。

在IKEv1实现中，PRG输出的第一个分组用于生成IKEv1 cookie，方法是将其与IP地址，端口，内存地址以及时间一起散列，以秒为单位。在IKEv2实现中，SPI字段（相当于IKEv1 cookie）是PRG输出的八个原始字节。在IKEv1和IKEv2中，下一个PRG输出分组用于生成握手Random，其长度为16个字节。对于与1024位Oakley Group 2 prime进行Diffie-Hellman密钥交换的情况，FortiOS v4使用来自PRG的两个连续块生成指数。在虚拟设备的实现中，随机字节直接读入Diffie-Hellman指数而不进行修改。



## 四、Fortinet特定版本产品的在线探测

作者使用ZMap在在互联网空间内扫描TCP 443端口（HTTPS）和 UDP 500端口（IKE）。通过IKE协议中的Vendor ID信息，即可确定VPN类型。HTTPS扫描中，一方面可通过证书common name字段判断设备厂商信息。进一步可通过ETAG判断设备指纹信息。方程式组织泄露的文件中注明了ETAG及其对应版本的详细信息，可作为版本探测的参考。而在现实攻击中，还可通过telnet和SSH协议的flag信息判断Fortinet的产品。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t012675ac48bd64962f.png)

Fortigate防火墙证书信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a189f63610c8c5c1.png)

方程式组织泄露文件EGBL.config

下面重点对ETAG的作用进阐述。

HTTP协议规格说明定义ETag为“被请求变量的实体值”。另一种说法是，ETag是一个可以与Web资源关联的记号（token）。典型的Web资源可以一个Web页，但也可能是JSON或XML文档。服务器单独负责判断记号是什么及其含义，并在HTTP响应头中将其传送到客户端，以下是服务器端返回的格式：`ETag:"50b1c1d4f775c61:df3"`。客户端的查询更新格式是这样的：`If-None-Match : W / "50b1c1d4f775c61:df3"`如果ETag没改变，则返回状态304然后不返回，这也和Last-Modified一样。测试Etag主要在断点下载时比较有用。利用ETAG，可以作为服务器版本的特定指纹信息。针对FortiGate防火墙扫描返回的信息如下。

[![](https://p5.ssl.qhimg.com/t01101d7b4112ada6e7.png)](https://p5.ssl.qhimg.com/t01101d7b4112ada6e7.png)
