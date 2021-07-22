> 原文链接: https://www.anquanke.com//post/id/244704 


# 从popmaster理解程序分析理论部分内容


                                阅读量   
                                **133679**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t0179dd5304dc6253d4.png)](https://p0.ssl.qhimg.com/t0179dd5304dc6253d4.png)



## 前言：

本人水平有限，如有错误，欢迎指点

看到作者的出题思路是抽象代码树和污点分析，因为之前发了几篇程序分析理论的文章但是一直没有实践，所以拿这道题自己实践一下。

污点分析在第一篇程序设计分析理论中，我写的是语义分析，但在后面的文章中还没有正式出现。关于抽象代码树，要在后面的抽象解释才提到。

过程间分析的内容还没有发出来，可以先看这篇文章帮助理解后面的过程间分析

我们已经介绍的只是数据流分析的部分内容，所以这篇文章首先会是根据数据流分析的过程间分析编写一个遍历以入口函数为起点的所有路径的脚本实现代码分析。

最后我们还会看一看出题人的exp。



## 编程思路

这一道题是一个单输入多输出的问题，根据之前流的理论，我们应该从输入开始分析。同时这道题是函数的跳转，所以我们选择过程间分析。根据上下文敏感的想法，我们在分支处应该是调用函数，主函数暂停，执行调用函数，调用函数退出的状态是主函数重新开始的状态。基于这一理论，我们定义一个函数，当出现分支时继续调用自身函数，未出现分支时，如果依旧是过程函数，还是调用自身，如果是eval输出函数 ，那么结束并输出pop链

除此之外，不少师傅在比赛时，选择从eval开始判断，先寻找不覆盖变量的eval，再往上找。是使用了逆流分析的方法， 在之前的文章里，我们提到逆流分析一般是多输入单输出的情况，为什么这里单输入多输出会使用逆流分析呢，主要是只需要找到一条链，多输出转换成了单输出，把这道题变成了单输入单输出的问题。当然，这并不意味着多输出的程序不能用逆流分析的方法。只是缺少了一些过程间分析的内容。



## 编写过程

类，函数，变量

函数有过程的函数和结束的eval函数

变量就是每一次要赋值的类名

这一个程序主要是跳转比较多，每一个具体执行没有太多需要注意的安全问题，要结合过程间分析编写代码。

我们之前提到过程间分析需要记录跳转前跳转后状态。在这里主要是记录上一个类和下一个类是哪个的问题。这个时候想到树结构能够记录上下同时满足多个分支。

在众多树结构中，我们想到结构归纳法帮助我们简化逻辑，在这个程序中最小单元是函数，我们用函数当作树状图的元素。我们记录每一个函数属于哪个类便于变量赋值，把函数是eval的当作终点。

对于一个形如

```
class Un9h32`{`
    public $msePmc1;
    public function NndvxI($HeqXE)`{`
        for($i = 0; $i &lt; 35; $i ++)`{`
            $aKMhTe= $HeqXE;
        `}`
        if(method_exists($this-&gt;msePmc1, 'T0bEwD')) $this-&gt;msePmc1-&gt;T0bEwD($HeqXE);
        if(method_exists($this-&gt;msePmc1, 'CdFIxA')) $this-&gt;msePmc1-&gt;CdFIxA($HeqXE);

`}`
public function gQLRqZ($cMmLT)`{`
    eval($cMmLT);

`}`

`}`
```

的类，我们需要记录类名，函数，函数指向的函数/eval

1.

我们要让python读取class后面的内容直到`{` 记录为类名

public $直到 ; 记录为变量名

public function 直到 ( 记录为函数名

$this-&gt;xxx-&gt; 直到( 记录为下一个函数名

封装成一个以函数名为主键的表，

先是一个类的封装

因为不会字符匹配所以仅仅通过位置获取，通用性差，后面再修改

代码如下

```
#coding=utf-8
import os, sys, re

i = 1
j = 1

class func:
    class_name = ''      #类名
    cur_function = ''     #当前函数名
    next_function = []    #下一个函数名
    var = ''         #变量名
    bool_cur = False     #是否是eval
    bool_next = False   #下一个函数是否多个    

​    

with open('asd.php') as file:
    for content in file:
        if 'class' in content:
            class_name = content[6:12]
        if 'public $' in content:
            var_name = content[12:19]
        if 'public function' in content:
            f = func()
            f.cur_function = content[20:26]
            f.class_name = class_name
            f.var = var_name 
            i = i + 1
            j = 1
        if 'eval' in content:
            f.bool_cur = True
        if 'method_exists' in content:
            f.next_function.append(content[62:68])
            if j&gt;1 :
                f.bool_next = True
            j = j + 1
print(f.class_name)
print(f.cur_function)
print(f.var)
print(f.bool_next)
print(f.bool_cur)
print(f.next_function[1])
```

拓展到多个类

由于树状结构本人不会，所以用写一个文件的方式构造树结构

```
#coding=utf-8
import os, sys, re

i = 1
j = 1
m = 1


class func:
    class_name = ''      #类名
    cur_function = ''     #当前函数名
    next_function = []    #下一个函数名
    var = ''         #变量名
    bool_cur = False     #是否是eval
    bool_next = False   #下一个函数是否多个



w_file=open('tree.txt','w')

#读取记录    

with open('asd.php') as file:
    for content in file:
        if 'class' in content:
            class_name = content[6:12]
        if 'public $' in content:
            var_name = content[12:19]
        if 'public function' in content:
            if i &gt; 1 :
                w_file.write(f.cur_function)
                w_file.write('\n    class_name ')
                w_file.write(f.class_name)
                while j &gt; m:
                    w_file.write('\n      f ')
                    w_file.write(f.next_function[m-1])
                    m = m + 1

​            w_file.write('\n    var ')    
​            w_file.write(f.var)
​            w_file.write('\n    bool_cur ')
​            w_file.write(str(f.bool_cur))
​            w_file.write('\n    bool_next ')
​            w_file.write(str(f.bool_next))
​            w_file.write('\n')


​            
​            f = func()
​            f.cur_function = content[20:26]
​            f.class_name = class_name
​            f.var = var_name 
​            i = i + 1
​            

​    if 'eval' in content:
​        f.bool_cur = True
​    if 'method_exists' in content:
​        f.next_function.append(content[62:68])
​        if j&gt;1 :
​            f.bool_next = True
​        j = j + 1
```

处理数据，使数据成为链状结构。

定义函数

```
#处理数据

def paixu(content,keyword):    
    pre_content = content + keyword +'--&gt;'
    position = tree_content.find(keyword)
    key_position = tree_content.find('f ',position)
    keyword = tree_content[key_position+2:key_position+8]             
    post_next = tree_content.find('bool_next',position)
    num = tree_content[post_next+10:post_next+11]
    num = int(num)
    while num &gt;= 1:
        paixu(pre_content,keyword)
        key_position = tree_content.find('f ',key_position+1)
        keyword = tree_content[key_position+2:key_position+8]
        num = num - 1
    post_cur = tree_content.find('bool_cur',position)
    current = tree_content[post_cur+9:post_cur+10]
    current = int(current)
    print(pre_content)
    if current == 1:
        w_file.write(pre_content+'\n')
        print(pre_content+'\n')
```

但是python递归深度有限制，同时可能会导致栈溢出

仅仅针对这一道题，我们限制链的长度，先找到一条能够到eval的链

```
t = 0

#处理数据

def paixu(content,keyword,t):    
    pre_content = content + keyword +'--&gt;'
    if t &gt; 30:
        print(pre_content)
        r_file.write(pre_content+'\n')
        return 0

position = tree_content.find(keyword)
key_position = tree_content.find('f ',position)
keyword = tree_content[key_position+2:key_position+8]             
post_next = tree_content.find('bool_next',position)
num = tree_content[post_next+10:post_next+11]
num = int(num)
while num &gt;= 1:
    t = t + 1
    paixu(pre_content,keyword,t)
    key_position = tree_content.find('f ',key_position+1)
    keyword = tree_content[key_position+2:key_position+8]
    num = num - 1
post_cur = tree_content.find('bool_cur',position)
current = tree_content[post_cur+9:post_cur+10]
current = int(current)    
if current == 1:
    print(pre_content)
    r_file.write('\n')
    r_file.write(pre_content+'\n')
    r_file.write('\n')
    return 0
```

3.

从入口开始找路径

```
#coding=utf-8
import os, sys, re

sys.setrecursionlimit(3000)

class func:
    class_name = ''      #类名
    cur_function = ''     #当前函数名
    next_function = []    #下一个函数名
    var = ''         #变量名
    bool_cur = 0     #是否是eval
    bool_next = 0   #下一个函数是否多个





#读取记录    
def read():
    i = 1
    j = 0
    m = 1
    k = 0
    w_file=open('tree.txt','w')
    with open('class.php') as file:
        for content in file:
            if 'class' in content:
                class_name = content[6:12]
            if 'public $' in content:
                var_name = content[12:19]
            if 'public function' in content:
                if i &gt; 1 :
                    w_file.write('cur ')
                    w_file.write(f.cur_function)
                    w_file.write('\n    class_name ')
                    w_file.write(f.class_name)
                    while j &gt;= m:
                        w_file.write('\n      f ')
                        w_file.write(f.next_function[m-1])
                        m = m + 1

​                w_file.write('\n    var ')    
​                w_file.write(f.var)
​                w_file.write('\n    bool_cur ')
​                w_file.write(str(f.bool_cur))
​                w_file.write('\n    bool_next ')
​                w_file.write(str(f.bool_next))
​                w_file.write('\n')

​            k = 0
​            f = func()
​            f.cur_function = content[20:26]
​            f.class_name = class_name
​            f.var = var_name 
​            i = i + 1
​            
​        if 'eval' in content:
​            f.bool_cur = 1
​        if 'method_exists' in content:
​            f.next_function.append(content[62:68])
​            j = j + 1
​            k = k + 1
​            f.bool_next = k
​        else:
​            if '$this-&gt;' in content:
​                next_position = content.find('$this-&gt;')
​                true = content.find('-&gt;',next_position+7)
​                if true != -1:
​                    f.next_function.append(content[next_position+16:next_position+22])
​                    j = j + 1
​                    k = k + 1
​                    f.bool_next = k


t = 0

#处理数据

def paixu(content,keyword,t):    
    position = tree_content.find('cur '+keyword)
    pre_content = content + keyword +'--&gt;'
    post_cur = tree_content.find('bool_cur',position)
    current = tree_content[post_cur+9:post_cur+10]
    current = int(current)
    if current == 1:
        print('yes  '+pre_content)
        r_file.write('yes  ')
        r_file.write(pre_content+'\n')
        r_file.write('\n')
        return 0
    if t &gt; 30:
        print('no  '+pre_content)
        r_file.write(pre_content+'no\n')
        return 0

key_position = tree_content.find('f ',position)
keyword = tree_content[key_position+2:key_position+8]             
post_next = tree_content.find('bool_next',position)
num = tree_content[post_next+10:post_next+11]
num = int(num)
while num &gt;= 1:
    t = t + 1
    paixu(pre_content,keyword,t)
    key_position = tree_content.find('f ',key_position+1)
    keyword = tree_content[key_position+2:key_position+8]
    num = num - 1
    t = t - 1


​    


​    
content = ''

\#read()

r_file=open('result.txt','w')
with open('tree.txt') as w_file :
    keyword = 'qZ5gIM'
    tree_content = w_file.read()
    position = tree_content.find(keyword)    
    content = keyword + '--&gt;'
    key_position = tree_content.find('f ',position)
    keyword = tree_content[key_position+2:key_position+8]
    post_next = tree_content.find('bool_next',position)
    num = tree_content[post_next+10:post_next+11]
    num = int(num)
    while num &gt;= 1:
        t = t + 1
        paixu(content,keyword,t)
        key_position = tree_content.find('f ',key_position+1)
        keyword = tree_content[key_position+2:key_position+8]
        num = num - 1
```

4.

验证可行

要把有覆盖变量的eval去除掉

我们将read 读取eval 的语句改成

```
if ‘eval’ in content:
f.bool_cur = 1
if ‘=\’’ in content[:-1]:
f.bool_cur = -1
```

到这一步已经可以完成pop链查找

但是我比较好奇是不是有一条没有拼接的链

所以继续加限制

```
#coding=utf-8
import os, sys, re ,linecache

sys.setrecursionlimit(3000)

class func:
    class_name = ''      #类名
    cur_function = ''     #当前函数名
    next_function = []    #下一个函数名
    var = ''         #变量名
    bool_cur = 0     #是否是eval
    bool_next = 0   #下一个函数是否多个
    token = 0





#读取记录    
def read():
    token = ''
    i = 1
    j = 0
    m = 1
    k = 0
    last_last_last_content = ''
    last_last_content = ''
    last_content = ''
    now_content = ''
    w_file=open('tree.txt','w')
    with open('class.php') as file:
        for content in file:
            last_last_last_content = last_last_content
            last_last_content = last_content
            last_content = now_content
            now_content = content
            if 'class' in content:
                class_name = content[6:12]
            if 'public $' in content:
                var_name = content[12:19]
            if 'public function' in content:
                if i &gt; 1 :
                    w_file.write('cur ')
                    w_file.write(f.cur_function)
                    w_file.write('\n    class_name ')
                    w_file.write(f.class_name)
                    while j &gt;= m:
                        w_file.write('\n      f ')
                        w_file.write(f.next_function[m-1])
                        m = m + 1

                    w_file.write('\n    var ')    
                    w_file.write(f.var)
                    w_file.write('\n    bool_cur ')
                    w_file.write(str(f.bool_cur))
                    w_file.write('\n    bool_next ')
                    w_file.write(str(f.bool_next))
                    w_file.write('\n    token ')
                    w_file.write(str(f.token))
                    w_file.write('\n')

                k = 0
                f = func()    
                f.cur_function = content[20:26]
                token = ''
                f.class_name = class_name
                f.var = var_name 
                i = i + 1

            if 'eval' in content:
                f.bool_cur = 1
                if '=\'' in last_content:
                    f.bool_cur = 2
                if '.\'' in last_last_content:
                    num_content = last_last_last_content
                    if '&gt;' in last_last_last_content:
                        num1_before_position = num_content.find('if(')
                        num1_after_position = num_content.find('&gt;')
                        num2_after_position = num_content.find(')')
                        num1 = num_content[num1_before_position+3:num1_after_position]
                        num1 = int(num1)
                        num2 = num_content[num1_after_position+1:num2_after_position]
                        num2 = int(num2)
                        if num1 &gt; num2:
                            f.bool_cur = 2    

            if 'method_exists' in content:
                f.next_function.append(content[62:68])
                j = j + 1
                k = k + 1
                f.bool_next = k
                if '=\'' in last_content:
                    f.token = 1
                if '.\'' in last_last_content:
                    num_content = last_last_last_content
                    if '&gt;' in last_last_last_content:
                        num1_before_position = num_content.find('if(')
                        num1_after_position = num_content.find('&gt;')
                        num2_after_position = num_content.find(')')
                        num1 = num_content[num1_before_position+3:num1_after_position]
                        num1 = int(num1)
                        num2 = num_content[num1_after_position+1:num2_after_position]
                        num2 = int(num2)
                        if num1 &gt; num2:
                            f.token = 1    
            else:
                if '$this-&gt;' in content:
                    next_position = content.find('$this-&gt;')
                    true = content.find('-&gt;',next_position+7)
                    if true != -1:
                        f.next_function.append(content[next_position+16:next_position+22])
                        j = j + 1
                        k = k + 1
                        f.bool_next = k
                    if '=\'' in last_content:
                        f.token = 1
                    if '.\'' in last_last_content:
                        num_content = last_last_last_content
                        if '&gt;' in last_last_last_content:
                            num1_before_position = num_content.find('if(')
                            num1_after_position = num_content.find('&gt;')
                            num2_after_position = num_content.find(')')
                            num1 = num_content[num1_before_position+3:num1_after_position]
                            num1 = int(num1)
                            num2 = num_content[num1_after_position+1:num2_after_position]
                            num2 = int(num2)
                            if num1 &gt; num2:
                                f.token = 1        

t = 0

#处理数据

def paixu(content,keyword,t):    
    position = tree_content.find('cur '+keyword)
    token_position = tree_content.find('token ',position)
    token = tree_content[token_position+6:token_position+7]
    token = int(token)
    if token == 1:
        return 0
    pre_content = content + keyword +'--&gt;'
    post_cur = tree_content.find('bool_cur',position)
    current = tree_content[post_cur+9:post_cur+10]
    current = int(current)
    if current == 2:
        return 0
    if current == 1:
        print('yes  '+pre_content)
        r_file.write('yes  ')
        r_file.write(pre_content+'\n')
        r_file.write('\n')
        return 0
    if t &gt; 30:
        print('no  '+pre_content)
        r_file.write(pre_content+'no\n')
        return 0


    key_position = tree_content.find('f ',position)
    keyword = tree_content[key_position+2:key_position+8]             
    post_next = tree_content.find('bool_next',position)
    num = tree_content[post_next+10:post_next+11]
    num = int(num)
    while num &gt;= 1:
        t = t + 1
        paixu(pre_content,keyword,t)
        key_position = tree_content.find('f ',key_position+1)
        keyword = tree_content[key_position+2:key_position+8]
        num = num - 1
        t = t - 1


​    


​    
content = ''

# read()

r_file=open('result.txt','w')
with open('tree.txt') as w_file :
    keyword = 'qZ5gIM'
    tree_content = w_file.read()
    position = tree_content.find(keyword)    
    content = keyword + '--&gt;'
    key_position = tree_content.find('f ',position)
    keyword = tree_content[key_position+2:key_position+8]
    post_next = tree_content.find('bool_next',position)
    num = tree_content[post_next+10:post_next+11]
    num = int(num)
    while num &gt;= 1:
        t = t + 1
        paixu(content,keyword,t)
        key_position = tree_content.find('f ',key_position+1)
        keyword = tree_content[key_position+2:key_position+8]
        num = num - 1
```

我将所有有拼接的数据全部过滤，最后结果是没有，可能是我代码还有问题，也有可能本身就是希望过滤拼接字符来实现pop链



## 出题人exp

接下来我们看看一下出题人的exp，笔者学历尚浅，只是粗浅看看而已。

大家可以去看[https://www.anquanke.com/post/id/244153](https://www.anquanke.com/post/id/244153)，这是出题人写的出题思路，exp的链接也在文章中

### <a class="reference-link" name="main.php"></a>main.php

get_ast是获取抽象代码树

deal_class是处理类的函数 如果是声明变量的类名当作变量处理，如果是方法的类名当作函数

get_func_call_map是获取函数调用关系，包括调用和被调用

get_func_tag是判断函数是否是敏感函数

get_CFG 处理上下文敏感的函数

function_node查找函数所在节点

get_path是遍历路径

deal_block处理代码块，判断其中变量是否被污染

run_CFG 模拟跳转流程

run_path模拟代码执行过程

main函数流程：

先看有没有危险函数，对危险函数的参数判断有没有被污染，然后遍历路径看看有没有调用可控参数的危险函数的路径。

### <a class="reference-link" name="config.php"></a>config.php

config.php是对一些输入输出进行分类，标记用途和是否可能存在安全问题。同时对某些安全问题所需要用到的方法进行整理。

### <a class="reference-link" name="class.php"></a>class.php

class.php是对类进行定义：

func_call_info 是关于调用函数的语句的类，记录了调用函数的语句的标签

func_path_info 记录执行完整程序所调用的全部函数和变量

func_call_map既记录函数调用关系又标记函数是否敏感

relation是记录调用关系和调用条件的类

CFG_class 是记录上下文数据的类

function.php是处理函数参数是否是用户可控的

visiter.php是各种情况的遍历器，记录进入节点前状态，退出节点时状态，将进入节点前状态转换成进入节点的状态，将退出节点时状态转换成原进程继续的状态。

在我的理解里，visiter的各种定义应该都可以归纳成下面的式子

init(p) = l_n

final(p) = `{`l_x`}`

blocks(p) = `{`is^l_n,end^l_x`}` ∪ blocks(S)

labels(p) = `{`l_n,l_x`}` ∪ labels(S)

flow(p) = `{`(l_n,init(S))`}` ∪ flow(S) ∪ `{`(l,l_x) | l ∈ final(S) `}`

也就是过程间分析的理论原型

语义分析部分应该是使用了基于方法的分析，将特殊结构单独分析，在最后组合起来。

**其他部分不妄加评论，以上内容如有错误，欢迎指点。exp分析如和原作者有冲突，一切以原作者为准。**



## 总结

我的代码主要是用了基于语句的分析，就是遍历所有情况，每次遍历判断是否危险，出题人的代码基于方法，更加高级。

其他的关于过程间分析的上下文敏感原理是一样的，就是我的代码水平更差，记录方式没有通用性。

对于危险函数或者污染参数肯定是出题人的代码更加完善。我的代码没有通用性。

希望这篇文章能够帮助各位理解之前的程序分析理论。笔者水平有限，如有错误，欢迎指点。

**作者：DR[@03](https://github.com/03)@星盟**
