> 原文链接: https://www.anquanke.com//post/id/197345 


# Seagate Central Storage RCE 0day漏洞分析


                                阅读量   
                                **1108324**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者pentest，文章来源：pentest.blog
                                <br>原文地址：[https://pentest.blog/advisory-seagate-central-storage-remote-code-execution/](https://pentest.blog/advisory-seagate-central-storage-remote-code-execution/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01ddc61426ed6d3221.png)](https://p5.ssl.qhimg.com/t01ddc61426ed6d3221.png)



## 0x00 前言

在本文中，我将与大家分享Seagate Central Storage NAS产品中存在的一些严重漏洞。

漏洞概要信息如下：

```
远程利用：是
需要认证：否
厂商URL：https://www.seagate.com/as/en/support/external-hard-drives/network-storage/seagate-central/
发现时间：2019年12月19日
```



## 0x01 技术细节

从Seagate官方[下载页面](https://www.seagate.com/as/en/support/external-hard-drives/network-storage/seagate-central/#downloads)下载最新版设备固件后，我开始ZIP固件包。ZIP文件中包含经过压缩的一个二进制文件：`Seagate-HS-update-201509160008F.img`，简单将该文件扩展名改为`tar.gz`后，我们可以成功提取出其中的[SquashFS](https://en.wikipedia.org/wiki/SquashFS)文件系统。该文件系统中包含适用于ARM架构NAS设备的管理应用程序的源代码、启动脚本以及busybox文件。

[![](https://p5.ssl.qhimg.com/t01af3d612a3611f146.png)](https://p5.ssl.qhimg.com/t01af3d612a3611f146.png)

图1. 固件更新ZIP包中的内容

使用`sudo unsquashfs -f -d /media/seagate /tmp/file.squashfs`命令挂载文件系统后，我开始分析其中包含的内容。经过简单探索后，我找到了设备管理接口对应的PHP源代码，因此可以直接转入源代码分析阶段。在分析过程中，我发现应用程序使用CodeIgniter框架开发。由于管理应用本身较为庞大，因此我重点关注的是可能存在漏洞的PHP函数。使用`find . -name "*.php" | xargs grep "&lt;function-name&gt;"`命令后，我们可以得到如下函数列表，找到比较有趣的一些输入点：

```
exec
shell_exec
system
passthru
pcntl_exec
popen
proc_open
eval
preg_replace （带有 /e 修饰符）
create_function
file_get_contents
file_put_contents
readfile
include
require
require_once
include_once
```

通过`grep`命令查找`proc_open`关键字后，我们在`./cirrus/application/helpers/mv_backend_helper.php`文件中找到了1处调用，该调用以多个动态变量作为参数。

[![](https://p1.ssl.qhimg.com/t013bc6051fd54933a6.png)](https://p1.ssl.qhimg.com/t013bc6051fd54933a6.png)

具体代码如下：

```
function mv_backend_launch($cmd, $noLog = false)
`{`
    $desc = array(
            0 =&gt; array("pipe","r"),
            1 =&gt; array("pipe","w"),
            2 =&gt; array("pipe","w")
            );
    $cwd = './';

    $process = proc_open($cmd,$desc,$pipes,$cwd);

    if(is_resource($process))
    `{`
        fclose($pipes[0]);
        $data =stream_get_contents($pipes[1]);
        fclose($pipes[1]);
        $errors=stream_get_contents($pipes[2]);
        if(strlen(trim($errors))&gt;0)
            mv_log_errors($cmd,$errors);
        fclose($pipes[2]);
        proc_close($process);

        if ( ! $noLog ) `{`
            syslog(LOG_INFO, "CMD: '$cmd', RESPONSE: '$data'");
        `}`
        return $data;
    `}`
`}`
```

追溯函数引用后，我找到了一个函数：`check_device_name`，该函数会将未经过滤的用户输入通过`$name`参数传递给`mv_backend_launch`函数。

```
public function check_device_name()
`{`
    $info = $this-&gt;get_start_info();
    $isStart = $info &amp;&amp; array_key_exists('state', $info) &amp;&amp; $info['state'] == 'start';

    if ( ! $isStart ) `{`
        mv_is_admin();
    `}`

    $name = $this-&gt;input-&gt;post("name");        
    $result = mv_backend_launch("check_netbios_name.sh $name");

    echo header('Content-type: text/xml');
    echo $result;
`}`
```

因此在这里我们找到了一个有趣的函数，并且该函数存在远程代码执行漏洞。但这里的问题在于，只有当设备状态设置为`start`时，该函数才有效，否则我们需要具备`admin`级别的访问权限才能触发该漏洞。因此我们需要找到无需身份认证就能修改设备状态的方法，或者需要进一步绕过身份身份认证，实现权限提升。为了解决该问题，我重新分析源代码，最终找到了一个更为优秀的攻击点。在分析设备状态机制时，我注意到当处于`start`状态时，设备会允许新用户注册操作，以便执行设备初始化设置。当我继续研究修改设备状态的具体逻辑时，我找到了`application/core/MV_BaseController.php`文件中的`set_start_info`函数。该函数可以通过JSON POST请求来设置设备状态，并且最为关键的是，整个过程没有任何访问控制机制！

```
public function reset_start_info()
`{`
    self::save_object_to_file(null, self::START_FILE);
    $uri = $_SERVER['REQUEST_URI'];
    $idx = strpos($uri, 'index.php');
    if ( $idx !== false ) `{`
        $uri = substr($uri, 0, $idx);
    `}`
    $uri .= 'index.php/SCSS';
    header('Content-type: text/plain');
    header("Location: ".$uri, TRUE, 302);
    exit();
`}`
```

因此，我们可以直接将设备状态修改为`start`，然后就能添加一个新的`admin`用户。设备所属的用户同样对应于Linux系统用户，因此这些用户都具备该设备的SSH访问权限。

[![](https://p4.ssl.qhimg.com/t018c93a9d5f25d5917.gif)](https://p4.ssl.qhimg.com/t018c93a9d5f25d5917.gif)



## 0x02 Metasploit模块

此时我们已经找到了多个漏洞。在漏洞利用方式上我更喜欢使用第二种方法，通过添加新的`admin`用户来建立SSH连接。考虑到Metasploit payload的兼容性，使用busybox程序来触发反向/bind shell连接是比较艰巨的一个任务。此外，除了HTTP、HTTPS、SSH、FTP等端口外，其他端口默认处于关闭状态。由于SSH默认处于启用状态，并且用户无法通过管理员接口禁用该功能，因此第二种利用方式显然更为方便。

最终利用效果可参考[此处视频](https://pentest.blog/wp-content/uploads/seagate.json)。



## 0x03 厂商反馈

向Seagate反馈该漏洞后，对方给了我们不小的打击。Seagate一开始声称“该产品主要面向个人家庭，针对个人局域网使用”，因此实际上并不存在可用的攻击面。随后我们通过[shodan.io](https://www.shodan.io/)以及[censys.io](https://censys.io/)找到了向互联网开放的一些目标设备，但似乎对方并不关心这个事实。既然我们不期望能拿到任何漏洞奖励或者积分，我们只能将研究成果公之于众。我们与厂商的讨论过程如下所示，之所以选择Bugcrowd平台，是因为Seagate只接收通过外部[Bugcrowd](https://www.seagate.com/as/en/legal-privacy/responsible-vulnerability-disclosure-policy/)表单提交的bug报告。

[![](https://p1.ssl.qhimg.com/t01dd43d9dff3ff0355.png)](https://p1.ssl.qhimg.com/t01dd43d9dff3ff0355.png)

[![](https://p0.ssl.qhimg.com/t01bbf3be1f45d6e95d.png)](https://p0.ssl.qhimg.com/t01bbf3be1f45d6e95d.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01b1f33b10915e24a2.png)
