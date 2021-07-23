> 原文链接: https://www.anquanke.com//post/id/86992 


# 【技术分享】ChromeOS基于eCryptfs的用户数据安全保护机制


                                阅读量   
                                **104218**
                            
                        |
                        
                                                                                    



**[![](https://p3.ssl.qhimg.com/t01ea06fa72a18b3a60.jpg)](https://p3.ssl.qhimg.com/t01ea06fa72a18b3a60.jpg)**



作者：[suezi@冰刃实验室](http://bobao.360.cn/member/contribute?uid=2911023682)

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

** **

**概述**

**Chromebook**的使用场景模式是允许多人分享使用同一台设备，但是同时也要保护每个用户数据的私密性，使得每个使用者都不允许访问到对方的隐私数据，包括：账户信息、浏览历史记录和cache、安装的应用程序、下载的内容以及用户自主在本地产生的文本、图片、视频等。本文试图从较高的角度阐述ChromeOS是如何通过**eCryptfs**机制保护用户数据隐私。

** **

**eCryptfs简介**

eCryptfs在**Linux kernel 2.6.19**由IBM公司的Halcrow，Thompson等人引入，在Cryptfs的基础上实现，用于企业级的文件系统加密，支持文件名和文件内容的加密。本质上eCryptfs 就像是一个内核版本的 Pretty Good Privacy（PGP）服务，插在 VFS和下层物理文件系统之间，充当一个“过滤器”的角色。用户应用程序对加密文件的写请求，经系统调用层到达 VFS 层，VFS 转给 eCryptfs 文件系统组件处理，处理完毕后，再转给下层物理文件系统；读请求流程则相反。

eCryptfs 的设计受到**OpenPGP**规范的影响，核心思想：eCryptfs通过一种对称密钥加密算法来加密文件的内容或文件名，如AES-128，密钥 FEK（File Encryption Key）随机产生。而FEK通过用户口令或者公钥进行保护，加密后的FEK称EFEK（Encrypted File Encryption Key），口令/公钥称为 FEFEK（File Encryption Key Encryption Key）。在保存文件时，将包含有EFEK、加密算法等信息的元数据（metadata）放置在文件的头部或者xattr扩展属性里（本文默认以前者做为讲解），打开文件前再解析metadata。

[![](https://p5.ssl.qhimg.com/t0135efa854e8e5ba62.png)](https://p5.ssl.qhimg.com/t0135efa854e8e5ba62.png)

图一 eCryptfs的系统架构

eCryptfs的系统架构如图一所示，eCryptfs堆叠在EXT4文件系统之上，工作时需要用户程序和内核同时配合，用户程序主要负责获取密钥并通过(add_key/keyctl/request_key)系统调用传送到内核的keyring，当某个应用程序发起对文件的读写操作前，由eCryptfs对其进行加/解密，加/解密的过程中需要调用Kernel的Crypto API（AES/DES etc）来完成。以对目录eCryptfs-test进行加密为例，为方便起见，在Ubuntu系统下测试eCryptfs的建立流程，如图二所示，通过mount指令发起eCryptfs的建立流程，然后在用户应用程序eCryptfs-utils的辅助下输入用于加密FEK的用户口令及选择加密算法等，完成挂载后意味着已经开始对测试目录eCryptfs-test的所有内容进行加密处理。测试中在eCryptfs-test目录下增加需要加密的文件或目录的内容，当用户umount退出对eCryptfs-test目录的挂载后再次查看该目录时，发现包括文件名和文件内容都进行了加密，如图三所示。

[![](https://p0.ssl.qhimg.com/t012ef7d5bc7a9b0c8a.png)](https://p0.ssl.qhimg.com/t012ef7d5bc7a9b0c8a.png)

图二 eCryptfs使用时的建立流程

[![](https://p4.ssl.qhimg.com/t0136bd55e4b7e5c9b3.png)](https://p4.ssl.qhimg.com/t0136bd55e4b7e5c9b3.png)

图三 eCryptfs加密后的文件

[![](https://p3.ssl.qhimg.com/t0157e14afb193a442e.png)](https://p3.ssl.qhimg.com/t0157e14afb193a442e.png)

图四 eCryptfs对文件的加解密流程

实现上，eCryptfs对数据的加/解密流程如图四所示，对称密钥加密算法以块为单位进行加密/解密，如AES-128。eCryptfs 将加密文件分成多个逻辑块，称为 extent，extent 的大小可调，但是不能大于实际物理页，默认值等于物理页的大小，如32位的系统下是 4096 字节。加密文件的头部存放元数据，包括元数据长度、标志位、旗标、EFEK及相应的signature，目前元数据的最小长度为 8192 字节。加/解密开始前，首先解密FEKEK取出FEK。当读入一个 extent 中的任何部分的密文时，整个 extent 被读入 Page Cache，通过 Kernel Crypto API 进行解密；当 extent 中的任何部分的明文数据被写回磁盘时，需要加密并写回整个 extent。

** **

**eCryptfs详述**

eCryptfs在内核中的实现代码位于kernel/fs/ecryptfs，下面以eCryptfs使用到的关键数据结构、eCryptfs init、eCryptfs mount、file creat、file open、file read、file write的顺序分别介绍eCryptfs是如何工作。另外，eCryptfs还实现了/dev/ecryptfs的misc设备，用于内核与应用程序间的消息传递，如密钥请求与响应，属于非必选项，因此这里不对其进行介绍。

** **

**eCryptfs相关的数据结构**

eCryptfs关键的数据结构包括eCryptfs 文件系统相关file、dentry、inode、superblock、file_system_type描述、auth token认证令牌描述、eCryptfs加密信息描述等。

eCryptfs文件系统相关的数据结构如清单一所示，下文将会重点介绍file_system_type中的mount函数，即ecryptfs_mount。

**清单一 eCryptfs文件系统相关的数据结构**

```
/* ecryptfs file_system_type */
static struct file_system_type ecryptfs_fs_type = `{`
.owner = THIS_MODULE,
.name = "ecryptfs",
.mount = ecryptfs_mount,
.kill_sb = ecryptfs_kill_block_super,
.fs_flags = 0
`}`;
/* superblock private data. */
struct ecryptfs_sb_info `{`
struct super_block *wsi_sb;
struct ecryptfs_mount_crypt_stat mount_crypt_stat;
struct backing_dev_info bdi;
`}`;
/* inode private data. */
struct ecryptfs_inode_info `{`
struct inode vfs_inode;
struct inode *wii_inode;
struct mutex lower_file_mutex;
atomic_t lower_file_count;
struct file *lower_file;
struct ecryptfs_crypt_stat crypt_stat;
`}`;
/* dentry private data. Each dentry must keep track of a lower vfsmount too. */
struct ecryptfs_dentry_info `{`
struct path lower_path;
union `{`
struct ecryptfs_crypt_stat *crypt_stat;
struct rcu_head rcu;
`}`;
`}`;
/* file private data. */
struct ecryptfs_file_info `{`
struct file *wfi_file;
struct ecryptfs_crypt_stat *crypt_stat;
`}`;
```

eCryptfs支持对文件名（包括目录名）进行加密，因此特意使用了struct ecryptfs_filename的结构封装文件名，如清单二所示。

**清单二 文件名的数据结构**

```
struct ecryptfs_filename `{`
struct list_head crypt_stat_list;
u32 flags;
u32 seq_no;
char *filename;
char *encrypted_filename;
size_t filename_size;
size_t encrypted_filename_size;
char fnek_sig[ECRYPTFS_SIG_SIZE_HEX];
char dentry_name[ECRYPTFS_ENCRYPTED_DENTRY_NAME_LEN + 1];
`}`;
```

struct ecryptfs_auth_tok用于记录认证令牌信息，包括用户口令和非对称加密两种类型，每种类型都包含有密钥的签名，用户口令类型还包含有算法类型和加盐值等，如清单三所示。为了方便管理，使用时统一将其保存在struct ecryptfs_auth_tok_list_item链表中。

**清单三 认证令牌信息的数据结构**

```
struct ecryptfs_auth_tok `{`
u16 version; /* 8-bit major and 8-bit minor */
u16 token_type;
u32 flags;
struct ecryptfs_session_key session_key;
u8 reserved[32];
union `{`
struct ecryptfs_password password;  //用户口令类型
struct ecryptfs_private_key private_key; //非对称加密类型
`}` token;
`}`
struct ecryptfs_password `{`
u32 password_bytes;
s32 hash_algo;
u32 hash_iterations;
u32 session_key_encryption_key_bytes;
u32 flags;
/* Iterated-hash concatenation of salt and passphrase */
u8 session_key_encryption_key[ECRYPTFS_MAX_KEY_BYTES];
u8 signature[ECRYPTFS_PASSWORD_SIG_SIZE + 1];
/* Always in expanded hex */
u8 salt[ECRYPTFS_SALT_SIZE];
`}`;
struct ecryptfs_private_key `{`
u32 key_size;
u32 data_len;
u8 signature[ECRYPTFS_PASSWORD_SIG_SIZE + 1];
char pki_type[ECRYPTFS_MAX_PKI_NAME_BYTES + 1];
u8 data[];
`}`;
```

eCryptfs在mount时会传入全局加解密用到密钥、算法相关数据，并将其保存在struct ecryptfs_mount_crypt_stat，如清单四所示

**清单四 mount时传入的密钥相关数据结构**



```
struct ecryptfs_mount_crypt_stat `{`
u32 flags;
struct list_head global_auth_tok_list;
struct mutex global_auth_tok_list_mutex;
size_t global_default_cipher_key_size;
size_t global_default_fn_cipher_key_bytes;
unsigned char global_default_cipher_name[ECRYPTFS_MAX_CIPHER_NAME_SIZE + 1];
unsigned char global_default_fn_cipher_name[
ECRYPTFS_MAX_CIPHER_NAME_SIZE + 1];
char global_default_fnek_sig[ECRYPTFS_SIG_SIZE_HEX + 1];
`}`;
```

eCryptfs读写文件时首先需要进行加/解密，此时使用的密钥相关数据保存在struct ecryptfs_crypt_stat结构中，其具体数值在open时初始化，部分从mount时的ecryptfs_mount_crypt_stat复制过来，部分从分析加密文件的metadata获取，该数据结构比较关键，贯穿eCryptfs的文件open、read、write、close等流程，如清单五所示。

**清单五 ecryptfs_crypt_stat数据结构**

```
struct ecryptfs_crypt_stat `{`
u32 flags;
unsigned int file_version;
size_t iv_bytes;
size_t metadata_size;
size_t extent_size; /* Data extent size; default is 4096 */
size_t key_size;
size_t extent_shift;
unsigned int extent_mask;
struct ecryptfs_mount_crypt_stat *mount_crypt_stat;
struct crypto_ablkcipher *tfm;
struct crypto_hash *hash_tfm; /* Crypto context for generating
       * the initialization vectors */
unsigned char cipher[ECRYPTFS_MAX_CIPHER_NAME_SIZE + 1];
unsigned char key[ECRYPTFS_MAX_KEY_BYTES];
unsigned char root_iv[ECRYPTFS_MAX_IV_BYTES];
struct list_head keysig_list;
struct mutex keysig_list_mutex;
struct mutex cs_tfm_mutex;
struct mutex cs_hash_tfm_mutex;
struct mutex cs_mutex;
`}`;
```



**eCryptfs init过程**

使用eCryptfs前，首先需要通过内核的配置选项“CONFIG_ECRYPT_FS=y”使能eCryptfs，因为加解密时使用到内核的crypto和keystore接口，所以要确保“CONFIG_CRYPTO=y”，“CONFIG_KEYS=y”，“CONFIG_ENCRYPTED_KEYS=y”，同时使能相应的加解密算法，如AES等。重新编译内核启动后会自动注册eCryptfs，其init的代码如清单六所示。

**清单六 eCryptfs init过程**



```
static int __init ecryptfs_init(void)
`{`
int rc;
//eCryptfs的extent size不能大于page size
if (ECRYPTFS_DEFAULT_EXTENT_SIZE &gt; PAGE_CACHE_SIZE) `{`
rc = -EINVAL;  ecryptfs_printk(KERN_ERR，…); goto out;
`}`
/*为上文列举到的eCryptfs重要的数据结构对象申请内存，如eCryptfs的auth token、superblock、inode、dentry、file、key等*/
rc = ecryptfs_init_kmem_caches(); 
…
 //建立sysfs接口，该接口中的version各bit分别代表eCryptfs支持的能力和属性
rc = do_sysfs_registration(); 
…
//建立kthread，为后续eCryptfs读写lower file时能借助内核函数得到rw的权限
rc = ecryptfs_init_kthread();
…
//在chromeos中该函数为空，直接返回0
rc = ecryptfs_init_messaging();
…
//初始化kernel crypto
rc = ecryptfs_init_crypto();
…
//注册eCryptfs文件系统
rc = register_filesystem(&amp;ecryptfs_fs_type);
…
return rc;
`}`
```



**eCryptfs mount过程**

在使能了eCryptfs的内核，当用户在应用层下发“mount –t ecryptfs src dst options”指令时触发执行上文清单一中的ecryptfs_mount函数进行文件系统的挂载安装并初始化auth token，成功执行后完成对src目录的eCryptfs属性的指定，eCryptfs开始正常工作，此后任何在src目录下新建的文件都会被自动加密处理，若之前该目录已有加密文件，此时会被自动解密。

ecryptfs_mount涉及的代码比较多，篇幅有限，化繁为简，函数调用关系如图五所示。

[![](https://p2.ssl.qhimg.com/t0145b4b226f81e5689.png)](https://p2.ssl.qhimg.com/t0145b4b226f81e5689.png)

图五 eCryptfs mount的函数调用关系图

从图五可看到mount时首先利用函数ecryptfs_parse_options()对传入的option参数做解析，完成了如下事项：

1.    调用函数ecryptfs_init_mount_crypt_stat()初始化用于保存auth token相关的 struct ecryptfs_mount_crypt_stat 对象；

2.    调用函数ecryptfs_add_global_auth_tok()将从option传入的分别用于FEK和FNEK（File Name Encryption Key，用于文件名加解密）的auth token的signature保存到struct ecryptfs_mount_crypt_stat 对象；

3.    分析option传入参数，初始化struct ecryptfs_mount_crypt_stat 对象的成员，如global_default_cipher_name、global_default_cipher_key_size、flags、global_default_fnek_sig、global_default_fn_cipher_name、global_default_fn_cipher_key_bytes等；

4.    调用函数ecryptfs_add_new_key_tfm()针对FEK和FNEK的加密算法分别初始化相应的kernel crypto tfm接口；

5.    调用函数ecryptfs_init_global_auth_toks()将解析option后得到key sign做为参数利用keyring的request_key接口获取上层应用传入的auth token，并将auth token添加入struct ecryptfs_mount_crypt_stat 的全局链表中，供后续使用。

接着为eCryptfs创建superblock对象并初始化，具体如下：

通过函数sget()创建eCryptfs类型的superblock；

调用bdi_setup_and_register()函数为eCryptfs的ecryptfs_sb_info 对象初始化及注册数据的回写设备bdi；

初始化eCryptfs superblock对象的各成员，如s_fs_info、s_bdi、s_op、s_d_op等；

然后获取当前挂载点的path并判断是否已经是eCryptfs，同时对执行者的权限做出判断；

再通过ecryptfs_set_superblock_lower()函数将eCryptfs的superblock和当前挂载点上底层文件系统对应的VFS superblock产生映射关系；

根据传入的mount option参数及VFS映射点superblock的值初始化eCryptfs superblock对象flag成员，如关键的MS_RDONLY属性；

根据VFS映射点superblock的值初始化eCryptfs superblock对象的其他成员 ，如s_maxbytes、s_blocksize、s_stack_depth；

最后设置superblock对象的s_magic为ECRYPTFS_SUPER_MAGIC。这可看出eCryptfs在Linux kernel的系统架构中，其依赖于VFS并处于VFS之下层，实际文件系统之上层。

下一步到创建eCryptfs的inode并初始化，相应工作通过函数ecryptfs_get_inode()完成，具体包括：

首先获取当前挂载点对应的VFS的inode；

然后调用函数iget5_locked()在挂载的fs中获取或创建一个eCryptfs的inode，并将该inode与挂载点对应的VFS的inode建立映射关系，与superblock类似，eCryptfs的inode对象的部分初始值从其映射的VFS inode中拷贝，inode operation由函数ecryptfs_inode_set()发起初始化，根据inode是符号链接还是目录文件还是普通文件分别进行不同的i_op 赋值，如ecryptfs_symlink_iops/ecryptfs_dir_iops/ecryptfs_main_iops；

同时对i_fop file_operations进行赋值，如ecryptfs_dir_fops/ecryptfs_main_fops 。

然后调用d_make_root()函数为之前创建的superblock设置eCryptfs的根目录s_root。

最后通过ecryptfs_set_dentry_private()函数为eCryptfs设置dentry。

** **

**加密文件creat过程**

creat过程特指应用层通过creat系统调用创建一个新的加密文件的流程。以应用程序通过creat()函数在以eCryptfs挂载的目录下创建加密文件为例，其函数调用流程如图六所示，creat()通过系统调用进入VFS，后经过层层函数调用，最终调用到eCryptfs层的ecryptfs_create()函数，该部分不属于eCryptfs的重点，不详述。

[![](https://p1.ssl.qhimg.com/t01f29067652520d956.png)](https://p1.ssl.qhimg.com/t01f29067652520d956.png)

图六 create经由VFS调用ecryptfs_create的流程

[![](https://p4.ssl.qhimg.com/t016b811bcd8d0d3e52.png)](https://p4.ssl.qhimg.com/t016b811bcd8d0d3e52.png)

图七 eCryptfs创建加密文件的函数调用过程

eCryptfs层通过ecryptfs_create() 函数完成最终的加密文件的创建，关键代码的调用流程如图七所示，以代码做为视图，分为三大步骤：

一、通过ecryptfs_do_create()函数创建eCryptfs 文件的inode并初始化；

二、通过函数ecryptfs_initialize_file()将新创建的文件初始化成eCryptfs加密文件的格式，添加入诸如加密算法、密钥信息等，为后续的读写操作初始化好crypto接口；

三、通过d_instantiate()函数将步骤一生成的inode信息初始化相应的dentry。具体如下：

**一．为新文件创建inode**

首先借助ecryptfs_dentry_to_lower()函数根据eCryptfs和底层文件系统（在chromeos里就是ext4）的映射关系获取到底层文件系统的dentry值。然后调用vfs_create()函数在底层文件系统上创建inode，紧接着利用__ecryptfs_get_inode()函数创建eCryptfs的inode 对象并初始化以及建立其与底层文件系统inode间的映射关系，之后通过fsstack_copy_attr_times()、fsstack_copy_inode_size()函数利用底层文件系统的inode对象的值初始化eCryptfs inode的相应值。

**二．初始化eCryptfs新文件**

经过步骤一完成了在底层文件系统上新建了文件，现在通过函数ecryptfs_initialize_file()将该文件设置成eCryptfs加密文件的格式。

1.    ecryptfs_new_file_context()函数完成初始化文件的context，主要包括加密算法cipher、auth token、生成针对文件加密的随机密钥等，这里使用的关键数据结构是struct ecryptfs_crypt_stat，具体如清单五所示，初始化文件的context基本可以看成是初始化struct ecryptfs_crypt_stat对象，该对象的cipher、auth token、key sign等值从mount eCryptfs传入的option并保存在struct ecryptfs_mount_crypt_stat （详见清单四）对象中获取。具体是：

首先由ecryptfs_set_default_crypt_stat_vals()函数完成flags、extent_size、metadata_size、cipher、key_size、file_version、mount_crypt_stat等ecryptfs_crypt_stat对象的缺省值设置；

然后再通过ecryptfs_copy_mount_wide_flags_to_inode_flags()函数根据mount时设置的ecryptfs_mount_crypt_stat的flags重新设置ecryptfs_crypt_stat对象flags；

接着由ecryptfs_copy_mount_wide_sigs_to_inode_sigs()函数将mount时保存的key sign赋值给ecryptfs_crypt_stat对象的keysig_list中的节点对象中的keysig；

然后继续将ecryptfs_mount_crypt_stat的cipher、key_size等值赋给ecryptfs_crypt_stat对象中的相应值；再调用函数ecryptfs_generate_new_key()生成key并保存到ecryptfs_crypt_stat对象的key；最后通过ecryptfs_init_crypt_ctx()函数完成kernel crypto context的初始化，如tfm，为后续的写操作时的加密做好准备。

2.    ecryptfs_get_lower_file()通过调用底层文件系统的接口打开文件，需要注意的是ecryptfs_privileged_open()，该函数唤醒了上文清单六提到kthread，借助该内核线程，eCryptfs巧妙避开了底层文件的读写权限的限制。

3.    ecryptfs_write_metadata()完成关键的写入eCryptfs文件格式到新创建的文件中。

关键函数ecryptfs_write_headers_virt()的代码如清单七所示，eCryptfs保存格式如清单七的注释（也可参考上文的图四），其格式传承自OpenPGP，最后在ecryptfs_generate_key_packet_set()完成EFEK的生成，并根据token_type的类型是ECRYPTFS_PASSWORD还是ECRYPTFS_PRIVATE_KEY生成不同的OpenPGP的Tag，之后保存到eCryptfs文件头部bytes 26开始的地方。这里以ECRYPTFS_PASSWORD为例，因此bytes 26地址起存放的内容是Tag3和Tag11，对应着EFEK和Key sign。否则保存的是Tag1，即EFEK。Tag3或Tag1的具体定义详见OpenPGP的描述文档RFC2440.<br>
之后将生成的eCryptfs文件的头部数据保存到底层文件系统中，该工作由ecryptfs_write_metadata_to_contents()完成。

4.    最后通过ecryptfs_put_lower_file()将文件改动的所有脏数据回写入磁盘。

**三．通过d_instantiate()函数将步骤一生成的inode信息初始化相应的dentry方便后续的读写操作**

**清单七 写入eCryptfs格式文件的关键函数**

```
/* Format version: 1
*   Header Extent:
 *     Octets 0-7:        Unencrypted file size (big-endian)
 *     Octets 8-15:       eCryptfs special marker
 *     Octets 16-19:      Flags
 *      Octet 16:         File format version number (between 0 and 255)
 *      Octets 17-18:     Reserved
 *      Octet 19:         Bit 1 (lsb): Reserved
 *                        Bit 2: Encrypted?
 *                        Bits 3-8: Reserved
 *     Octets 20-23:      Header extent size (big-endian)
 *     Octets 24-25:      Number of header extents at front of file (big-endian)
 *     Octet  26:        Begin RFC 2440 authentication token packet set
 *   Data Extent 0:        Lower data (CBC encrypted)
 *   Data Extent 1:        Lower data (CBC encrypted)
 *   ...
*/
static int ecryptfs_write_headers_virt(char *page_virt, size_t max,
       size_t *size,
       struct ecryptfs_crypt_stat *crypt_stat,
       struct dentry *ecryptfs_dentry)
`{`
int rc;
size_t written;
size_t offset;
offset = ECRYPTFS_FILE_SIZE_BYTES;
write_ecryptfs_marker((page_virt + offset), &amp;written);
offset += written;
ecryptfs_write_crypt_stat_flags((page_virt + offset), crypt_stat,
&amp;written);
offset += written;
ecryptfs_write_header_metadata((page_virt + offset), crypt_stat,
       &amp;written);
offset += written;
rc = ecryptfs_generate_key_packet_set((page_virt + offset), crypt_stat,
      ecryptfs_dentry, &amp;written,
      max - offset);
…
return rc;
`}`
```



**加密文件open过程**

这里open过程主要指通过open系统调用打开一个已存在的加密文件的流程。当应用程序在已完成eCryptfs挂载的目录下open一个已存在的加密文件时（这里以普通文件为例），其系统调用流程如图八所示，经由层层调用后进入ecryptfs_open()函数，由其完成加密文件的metadata分析，然后取出EFEK并使用kernel crypto解密得到FEK。另外在文中”create过程”分析时，着重介绍了创建eCryptfs格式文件的过程，省略了在完成lookup_open()函数调用后的vfs_open()的分析，它与这里介绍的vfs_open()流程是一样的。需要特别指出的是在do_dentry_open函数里初始化了struct file的f_mapping成员，让其指向inode-&gt;i_mapping；而在上图五的inode的创建函数ecryptfs_inode_set中存在”inode-&gt;i_mapping-&gt;a_ops = &amp;ecryptfs_aops”的赋值语句，这为后续的加密文件的页读写时使用的关键对象struct address_space_operations a_ops做好了初始化。

下面重点介绍ecryptfs_open()函数，其主要的函数调用关系如图九所示。eCryptfs支持Tag3和Tag1的形式保存EFEK，这里的分析默认是采用了Tag3的方式。

[![](https://p3.ssl.qhimg.com/t018055c01773b37b4f.png)](https://p3.ssl.qhimg.com/t018055c01773b37b4f.png)

图八 create经由VFS调用ecryptfs_create的流程

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01a3bab564195b3525.png)

图九 eCryptfs创建加密文件的函数调用过程

ecryptfs_open()函数的完成的主要功能包括读取底层文件，分析其文件头部的metadata，取出关键的EFEK及key sign，之后根据key sign从ecryptfs_mount_crypt_stat对象中匹配到相应的auth token，再调用kernel crypto解密EFEK得到FEK，最后将FEK保存到ecryptfs_crypt_stat的key成员中，完成ecryptfs_crypt_stat对象的初始化，供后续的文件加解密使用。具体如下：

1.    ecryptfs_set_file_private()巧妙的将struct ecryptfs_file_info保存到struct file的private_data中，完成VFS和eCryptfs之间的链式表达及映射；

2.    ecryptfs_get_lower_file()借助kthread 内核线程巧妙的获取到底层文件的RW权限；

3.    ecryptfs_set_file_lower()完成struct ecryptfs_file_info的wfi_file和底层文件系统文件lower_file之间的映射；

4.    read_or_initialize_metadata()完成了ecryptfs_open的大部分功能，首先通过ecryptfs_copy_mount_wide_flags_to_inode_flags()从文件对应的ecryptfs_mount_crypt_stat中拷贝flags对ecryptfs_crypt_stat的flags进行初始化；之后使用函数ecryptfs_read_lower()读取文件的头部数据，紧接着利用ecryptfs_read_headers_virt()进行数据分析和处理，包括：

1) 利用ecryptfs_set_default_sizes()初始化ecryptfs_crypt_stat对象的extent_size、iv_bytes、metadata_size等成员的默认值;

2) 使用ecryptfs_validate_marker()校验文件的marker标记值是否符合eCryptfs文件格式；

3) 通过ecryptfs_process_flags()取出文件metadata保存的flag并修正ecryptfs_crypt_stat对象成员flags的值,同时初始化对象成员file_version；

4) 在parse_header_metadata()分析文件的metadata的大小并保存到ecryptfs_crypt_stat对象成员metadata_size；

5) 通过ecryptfs_parse_packet_set()解析Tag3和Tag11的OpenPGP格式包，获取EFEK及key sign，后根据key sign匹配到auth token，再调用kernel crypto解密EFEK得到FEK。对应的代码实现逻辑是：

parse_tag_3_packet()解析Tag3，获取EFEK和cipher，同时将cipher保存到ecryptfs_crypt_stat对象成员cipher；

parse_tag_11_packet()解析出key sign，保存到auth_tok_list链表中；

ecryptfs_get_auth_tok_sig()从auth_tok_list链表中获取到key sign；

然后通过ecryptfs_find_auth_tok_for_sig()根据key sign从ecryptfs_mount_crypt_stat对象中匹配到相应的auth token；

再利用decrypt_passphrase_encrypted_session_key()使用分析得到的auth token、cipher解密出FEK，并将其保存在ecryptfs_crypt_stat的key成员；

之后在ecryptfs_compute_root_iv()函数里初始化ecryptfs_crypt_stat的root_iv成员，在ecryptfs_init_crypt_ctx()函数里初始化ecryptfs_crypt_stat的kernel crypto接口tfm。至此，ecryptfs_crypt_stat对象初始化完毕，后续文件在读写操作时使用到的加解密所需的所有信息均在该对象中获取。

** **

**加密文件read过程**

read过程指应用程序通过read()函数在eCryptfs挂载的目录下读取文件的过程。因为挂载点在挂载eCryptfs之前可能已经存在文件，这些已存在的文件属于非加密文件，只有在完成eCryptfs挂载后的文件才自动保存成eCryptfs格式的加密文件，所以读取文件时需要区分文件是否属于加密文件。从应用程序发起read()操作到eCryptfs层响应的函数调用关系流程图如十所示，读取时采用page read的机制，涉及到page cache的问题，图中以首次读取文件，即文件内容还没有被读取到page cache的情况为示例。

自ecryptfs_read_update_atime()起进入到eCryptfs层，由此函数完成从底层文件系统中读取出文件内容，若是加密文件则利用kernel crypto和open时初始化好的ecryptfs_crypt_stat对象完成内容的解密，之后将解密后的文件内容拷贝到上层应用程序，同时更新文件的访问时间，其中touch_atime()完成文件的访问时间的更新；

generic_file_read_iter()函数调用内核函数do_generic_file_read()，完成内存页的申请，并借助mapping-&gt;a_ops-&gt;readpage()调用真正干活的主力ecryptfs_readpage()来完成解密工作，最后通过copy_page_to_iter()将解密后的文件内容拷贝到应用程序。到了关键的解密阶段，描述再多也不如代码来的直观，ecryptfs_readpage()的核心代码如清单八、九、十所示。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01326d7c58c0db5b5f.png)

图十 create经由VFS调用ecryptfs_create的流程

**清单八 ecryptfs_readpage()关键代码**

```
static int ecryptfs_readpage(struct file *file, struct page *page)
`{`
struct ecryptfs_crypt_stat *crypt_stat =
&amp;ecryptfs_inode_to_private(page-&gt;mapping-&gt;host)-&gt;crypt_stat;
int rc = 0;
if (!crypt_stat || !(crypt_stat-&gt;flags &amp; ECRYPTFS_ENCRYPTED)) `{`
 
//读取非加密文件
rc = ecryptfs_read_lower_page_segment(page, page-&gt;index, 0,
      PAGE_CACHE_SIZE,
      page-&gt;mapping-&gt;host);
`}` else if (crypt_stat-&gt;flags &amp; ECRYPTFS_VIEW_AS_ENCRYPTED) `{`
//直接读取密文给上层，此时应用程序读到的是一堆乱码
if (crypt_stat-&gt;flags &amp; ECRYPTFS_METADATA_IN_XATTR) `{`
rc = ecryptfs_copy_up_encrypted_with_header(page, crypt_stat);
…
`}` else `{`
rc = ecryptfs_read_lower_page_segment(
page, page-&gt;index, 0, PAGE_CACHE_SIZE,
page-&gt;mapping-&gt;host);
…
`}`
`}` else `{`
//读取密文并调用kernel crypto解密
rc = ecryptfs_decrypt_page(page);
…
`}`
…
return rc;
`}`
```

**清单九 ecryptfs_decrypt_page()核心代码**

```
int ecryptfs_decrypt_page(struct page *page)
`{`
…
ecryptfs_inode = page-&gt;mapping-&gt;host;
//获取包含有FEK、cipher、crypto context tfm信息的ecryptfs_crypt_stat
crypt_stat = &amp;(ecryptfs_inode_to_private(ecryptfs_inode)-&gt;crypt_stat);
//计算加密文件内容在底层文件中的偏移
lower_offset = lower_offset_for_page(crypt_stat, page);
page_virt = kmap(page);
//利用底层文件系统的接口读取出加密文件的内容
rc = ecryptfs_read_lower(page_virt, lower_offset, PAGE_CACHE_SIZE, ecryptfs_inode);
kunmap(page);
    …
for (extent_offset = 0;
     extent_offset &lt; (PAGE_CACHE_SIZE / crypt_stat-&gt;extent_size);
     extent_offset++) `{`
//解密文件内容
rc = crypt_extent(crypt_stat, page, page,
  extent_offset, DECRYPT);
…
`}`
…
`}`
```

**清单十 crypt_extent()核心加解密函数的关键代码**

```
static int crypt_extent(struct ecryptfs_crypt_stat *crypt_stat,
struct page *dst_page,
struct page *src_page,
unsigned long extent_offset, int op)
`{`
//op 指示时利用该函数进行加密还是解密功能
pgoff_t page_index = op == ENCRYPT ? src_page-&gt;index : dst_page-&gt;index;
loff_t extent_base;
char extent_iv[ECRYPTFS_MAX_IV_BYTES];
struct scatterlist src_sg, dst_sg;
size_t extent_size = crypt_stat-&gt;extent_size;
int rc;
extent_base = (((loff_t)page_index) * (PAGE_CACHE_SIZE / extent_size));
rc = ecryptfs_derive_iv(extent_iv, crypt_stat,
(extent_base + extent_offset));
…
sg_init_table(&amp;src_sg, 1);
sg_init_table(&amp;dst_sg, 1);
sg_set_page(&amp;src_sg, src_page, extent_size,
    extent_offset * extent_size);
sg_set_page(&amp;dst_sg, dst_page, extent_size,
    extent_offset * extent_size);
//调用kernel crypto API进行加解密
rc = crypt_scatterlist(crypt_stat, &amp;dst_sg, &amp;src_sg, extent_size, extent_iv, op);
…
return rc;
`}`
```

理顺了mount、open的流程，知道FEK、cipher、kernel crypto context的值及存放位置，同时了解了加密文件的格式，解密的过程显得比较简单，感兴趣的同学可以继续查看crypt_scatterlist()的代码，该函数纯粹是调用kernel crypto API进行加解密的过程，跟eCryptfs已经没有关系。

** **

**加密文件write过程**

eCryptfs文件write的流程跟read类似，在写入lower file前先通过ecryptfs_writepage()函数进行文件内容的加密，这里不再详述。

** **

**ChromeOS使用eCryptfs的方法及流程**

Chromeos在保护用户数据隐私方面可谓不遗余力，首先在系统分区上专门开辟出专用于存储用户数据的stateful partition，当用户进行正常和开发者模式切换时，该分区的数据将会被自动擦除；其次该stateful partition的绝大部分数据采用dm-crypt进行加密，在系统启动时用户登录前由mount-encrypted完成解密到/mnt/stateful_partition/encrypted，另外完成以下几个mount工作：

将/Chromeos/mnt/stateful_partition/home bind mount 到/home；

将/mnt/stateful_partition/encrypted/var bind mount到/var目录；

将/mnt/stateful_partition/encrypted/chromos bind mount 到/home/chronos。

最后在用户登录时发起对该用户私有数据的eCryptfs加解密的流程，具体工作由cryptohomed守护进程负责完成，eCryptfs加密文件存放在/home/.shadow/[salted_hash_of_username]/vault目录下，感兴趣的读者可通过ecryptfs-stat命令查看其文件状态和格式，mount点在/home/.shadow/[salted_hash_of_username]/mount，之后对/home/.shadow/[salted_hash_of_username]/mount下的user和root建立bind mount点，方便用户使用。

如将/home/.shadow/[salted_hash_of_username]/mount/user bind mount到/home/user/[salted_hash_of_username]和/home/chronos/u-[salted_hash_of_username] ；

将/home/.shadow/[salted_hash_of_username]/mount/root bind mount到/home/root/[salted_hash_of_username]。

用户在存取数据时一般是对目录/home/chronos/u-[salted_hash_of_username]进行操作。

eCryptfs在Chromeos中的应用架构如图十所示。系统启动后开启cryptohomed的守护进程，由该进程来响应eCryptfs的挂载和卸载等，进程间采用D-Bus的方式进行通信，cryptohome应用程序主用于封装用户的动作命令，后通过D-Bus向cryptohomed发起请求。如可通过cryptohome命令”cryptohome -–action=mount -–user=[account_id]”来发起eCryptfs的挂载；通过命令”cryptohome -–action=unmount”卸载eCryptfs的挂载，执行成功此命令后，用户的所有个人数据将无法访问，如用户先前下载的文件内容不可见、安装的应用程序不可使用，/home/.shadow/[salted_hash_of_username]/mount内容为空。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c5c544450c1461a8.png)

图十一 eCryptfs在Chromeos中的架构图

cryptohomed特色的mount流程如下：

1.    cryptohomed在D-Bus上接收到持（包含用户名和密码）有效用户证书的mount请求，当然D-Bus请求也是有权限控制的；

2.    假如是用户首次登陆，将进行：

a.建立/home/.shadow/[salted_hash_of_username]目录，采用SHA1算法和系统的salt对用户名进行加密，生成salted_hash_of_username，简称s_h_o_u;

b.生成vault keyset /home/.shadow/[salted_hash_of_username]/master.0和/home/.shadow/[salted_hash_of_username]/master.0.sum。 master.0加密存储了包含有FEK和FNEK的内容以及非敏感信息如salt、password rounds等；master.0.sum是对master.0文件内容的校验和。

3.    采用通过mount请求传入的用户证书解密keyset。当TPM可用时优先采用TPM解密，否则采用Scrypt库，当TPM可用后再自动切换回使用TPM。cryptohome使用TPM仅仅是为了存储密钥，由TPM封存的密钥仅能被TPM自身使用，这可用缓解密钥被暴力破解，增强保护用户隐私数据的安全。TPM的首次初始化由cryptohomed完成。这里默认TPM可正常使用，其解密机制如下图十二所示，其中：

**UP**：User Passkey，用户登录口令

**EVKK**：Ecrypted vault keyset key，保存在master.0中的”tpm_key”字段

**IEVKK**：Intermediate vault keyset key，解密过程生成的中间文件，属于EVKK的解密后产物，也是RSA解密的输入密文

**TPM_CHK**: TPM-wrapped system-wide Cryptohome key，保存在/home/.shadow/cryptohome.key，TPM init时加载到TPM

**VKK**：Vault keyset key

**VK**：Vault Keyset，包含FEK和FNEK

**EVK**：Encrypted vault keyset，保存在master.0里”wrapped_keyset”字段

图十二中的UP（由发起mount的D-Bus请求中通过key参数传入）做为一个AES key用于解密EVKK，解密后得到的IEVKK；然后将IEVKK做为RSA的密文送入TPM，使用TPM_CHK做为密钥进行解密，解密后得到VKK；最后生成的VKK是一个AES key，用于解密master.0里的EVK，得到包含有FEK和FNEK明文的VK。经过三层解密，终于拿到关键的FEK，那么问题来了，Chromeos的FEK的保存及解密流程与上文介绍的eCryptfs时不一致，FEK不应该是open时从加密文件的头部metadata里的EFEK中解密出来的么？不过一次解密出FEK，全局使用，效率的确比每次读取文件时解析FEK高很多，之后通过key的系统调用将key传入内核的keyring，使用时通过key sign匹配。最后跟上文所述实属异曲同工。

4.    通过mount系统调用传入option完成挂载。该部分与正常的Linux做法一致，在mount的option里传入关键的cipher、key sign、key bytes等信息。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t018644839e78ddcedc.png)

图十二 TPM解密VK的流程

** **

**结语**

ecryptfs建立在系统安全可信的基础上，保护用户数据的安全，核心基础组件是加密密钥，若在内核被攻破后密钥被通过某些手段窃取，ecryptfs的安全性将同样被攻破。另外page cache中加密文件的明文页有可能被交换到swap区，在chromeos中已经禁用了swap，因此不会产生影响，但是其他版本的Linux系统需要注意该问题。

eCryptfs首次实现到现在已经十年有余，直到近几年才在chromeos和Ubuntu上使用，个人认为除了之前人们的安全意识不如现在强烈外，更重要的是随着处理器性能的增强，eCryptfs加解密引起的文件读写性能下降的问题已经得到缓解。但实际的性能损耗如何，有待继续研究。或许出于性能的原因，年初的时候Google在chromeos实现了基于ext4 crypto的 dircrypto，用于实现跟eCryptfs同样的功能，目前chromeos同时支持eCryptfs和dircrypto，但在60版本后优先采用dircrypto技术，相关技术在另外的文章中进行介绍。

最后，文中必有未及细看而自以为是的东西，望大家能够去伪存真，更求不吝赐教。

** **

**参考资料**

[企业级加密文件系统 eCryptfs 详解](https://www.ibm.com/developerworks/cn/linux/l-cn-ecryptfs/)

[eCryptfs: a Stacked Cryptographic Filesystem](http://www.linuxjournal.com/article/9400)

[Linux kernel-V4.4.79 sourcecode](https://chromium.googlesource.com/chromiumos/third_party/kernel/+/v4.4.79)

[chromiumos platform-9653 sourcecode](https://chromium.googlesource.com/chromiumos/)
