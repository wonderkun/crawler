> 原文链接: https://www.anquanke.com//post/id/248172 


# 程序分析理论 初实践 抽象化 CFG AST


                                阅读量   
                                **26805**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t010954cc7a0870a944.jpg)](https://p1.ssl.qhimg.com/t010954cc7a0870a944.jpg)



## 前言

不知道大家还记不记得popmaster这道题。当初出题人用了php parser实现抽象代码树从而达到程序分析目的。之前我们只讲到数据流分析所以我使用了过程间分析的原理和函数递归的思想实现程序分析。上一篇文章我们讲到了控制流分析。其中提到了抽象分析和抽象代码树以及CFG控制流图

总而言之，这一篇文章的目的是为了更好理解程序分析理论。

这篇文章的结构分为抽象化，CFG实现，AST实现。

TIPS：CFG和AST实际上只是结构而已，抽象化并不是他们所作的事情。



## 抽象化

抽象化实际上就是将代码转换机器所能识别的语言。就像之前我用正则表达式获取类名，函数名，各函数调用关系，并转换成规律性结构，再使用污点分析加上限制条件从而实现代码分析。

但是通用性不够，主要原因是使用的正则表达式太固化。很多师傅都推荐php parser实现语法分析，phpparser使用了token_get_all函数实现抽象化，实际上使用了zend的词汇扫描器。想了解可以看php parser分析这篇文章，里面写了phpparser代码逻辑和zend词汇扫描器的工作原理，虽然水平有限。

### <a class="reference-link" name="%E6%80%9D%E8%B7%AF"></a>思路

虽然每个人编写程序的习惯不同，但是只要语言是一样的，语法就肯定是一样的。我们依旧是寻找关键词将程序进行划分。和之前不同的是获取程序内部数理结构我们使用更加普适性的方法（对字数不做限制，对代码之间的空格正确分析）。

### <a class="reference-link" name="%E7%AE%80%E5%8D%95%E5%B0%9D%E8%AF%95"></a>简单尝试

我们以php语言的代码作为本文的例子。

**<a class="reference-link" name="%E8%B5%8B%E5%80%BC%E8%A1%A8%E8%BE%BE%E5%BC%8F"></a>赋值表达式**

$a=$b

以=为分界线寻找左式右式，左式必然是一个变量，形如$a。右式可能是常数，变量（以$为标记），函数（以括号为标记，括号内可能有常数可能有变量，这个括号还要和运算符的括号区分，区别是左括号前有什么，字母数字下划线则是函数，运算符则是计算式），计算式（以运算符为标记）。

特殊的会出现$a=$b=$c

我们依旧以一个等号为基准，一个等号分成两个部分，左值只能是形如$a的式子，右值如果有等号可以继续依照上述方法进一步划分。

代码实现

```
void getexpr(char *code)`{`

  bool isstart = False;

  for(i=1;;i++)`{`

​    if(skip(*(code-i)) &amp;&amp; !isstart) continue;

​    if(isalnum(*(code-i)) || isunderline(*(code-i)) || isdollar(*(code-i)))`{`

​      isstart = True;

​      left = *(code-i) + left; 

​    `}`

​    else`{`

​      break;

​    `}`

  `}`

  for(i=1;;i++)`{`

​    if(skip(*(code-i))) continue;

​    if(!isend(*(code-i)))`{`

​      right = right + *(code-i);

​    `}`

​    else break;

  `}`

  for(i=1;i&lt;len(right);i++)`{`

​    if(isyunsuanfu(substr(right,i,1)))`{`

​      getexpr(*(code+1));

​    `}`

  `}`

`}`
```

**<a class="reference-link" name="%E5%91%BD%E4%BB%A4%E5%9E%8B%E8%AF%AD%E5%8F%A5"></a>命令型语句**

如echo var_dump等等。

对于每一个函数都要特殊定义。对危险函数要进行标记。

由于数量众多，但不含有什么原理性内容，代码不在此列出，只要像之前的phpparser代码中的那样就可以了。



## CFG结构

CFG是控制流程图。表示了所有代码块之间的运行顺序和逻辑关系。每一个代码块应是在可能范围内最大的代码块。而其划分依据就是在该代码块中是否不存在从中间代码跳转到另一行代码的可能。满足这一条件的代码块应不包括函数调用，if判断，for循环等语句。所以我们在抽象化过程中，遇到特殊语法结构时，对代码进行划分，对抽象结果进行新的保存，实现CFG结构。

### <a class="reference-link" name="%E7%BB%93%E6%9E%84%E7%BC%96%E8%AF%91"></a>结构编译

**<a class="reference-link" name="function"></a>function**

function内部可能会含有其他类型的语句结构，对其内部特殊结构的分析我们转换成相应的语法结构分析，就像我们在程序分析理论中提到的(C,ρ) |= (let x = t_1 ^1 in t_2 ^2) ^l 我们进一步通过(C,ρ) |=t_1 ^1 (C,ρ) |=t_2 ^2得到最终结果

对于php的function其组成部分有标签function，函数名()，括号内可能是有参，也可能是无参。剩下的就是return返回值。

所以在正则匹配中，我们先找到function 随后是函数名（在括号前）和参数（在括号内），函数体和return（在大括号内）

我们记录函数名和参数作为该模块的基本信息，其函数体则进行进一步的分解，直到只存在赋值语句或者命令型语句，对其抽象化后保存在流程图中。

代码实现

```
void compile(*pos)`{`
    if(isskip(*pos)) pos++;
    else if(isbe(*pos))`{`
        pos++;
        q++;
    `}`
    else if(isen(*pos))`{`
        pos++;
        q--;
        if(q == p) node--;
    `}`
    else if(isalpha(*pos))`{`
        do`{`
            beef = beef + *pos;
            pos++;
        `}`while(isalpha(*pos) || isnum(*pos) || isunderline(*pos));
        if(table == 0)`{`
            if(divfind(beef) &gt; 0)`{`
                Node = new node;
                p++;
                node(q);
                table = divfind(beef);
            `}`
            else if(divfind(beef) &lt; -1)`{` 
                table = divfind(beef);
                Node = new node;
                p++;
                node(1,beef);

        `}`
        else if(table == 1)`{`
            node(1,beef);
            while(isskip(*pos))`{`
                pos++;
            `}`
            pos++;
            while(*pos != ')')`{`
                int i = 0;
                if(isend(*pos)) pos++;
                while(!isend(*pos))`{`
                    beef = beef + *pos;
                    pos++;
                `}`
                args[i] = beef;
                i++;
                beef = "";
            `}`

        `}`


        beef = "";
        pos++;
        compile(*pos);
    `}`
    else if(isnum(*pos))`{`
        do`{`
            num = num * 10 + int(*pos);
            pos++;
        `}`while(isnum(*pos));
        node(num);
        num = 0;
        pos++;
        compile(*pos);
    `}`
    else if(isdollar(*pos))`{`
        pos++;
        while(isalpha(*pos) || isnum(*pos) || isunderline(*pos))`{`
            beef = beef + *pos;
            pos++
        `}`
        node(2,beef);
        beef = "";
        pos++;
        compile(*pos);
    `}`


`}`
```

**<a class="reference-link" name="if"></a>if**

对于if语句，我们对其逻辑表达式划分到上一节代码块中，对其yes和no分支分别进行分析。我们将if以及elseif的代码块标记为-1，将else标记为0，如果没有else那么加入空node标记为0。

代码实现

```
void compile(*pos)`{`
    if(isskip(*pos)) pos++;
    else if(isbe(*pos))`{`
        pos++;
        q++;
    `}`
    else if(isen(*pos))`{`
        pos++;
        q--;
        if(q == p) node--;
    `}`
    else if(isalpha(*pos))`{`
        do`{`
            beef = beef + *pos;
            pos++;
        `}`while(isalpha(*pos) || isnum(*pos) || isunderline(*pos));
        if(table == 0)`{`
            if(divfind(beef) &gt; 0)`{`
                Node = new node;
                p++;
                node(q);
                table = divfind(beef);
            `}`
            else if(divfind(beef) &lt; -1)`{` 
                table = divfind(beef);
                Node = new node;
                p++;
                node(1,beef);
                if(divfind(beef) == -2)`{`
                    node(-1,-p);
                `}`
                else if(divfind(beef) == -3)`{`
                    while(isskip(*pos))`{`
                        pos++;
                    `}`
                    while(isalpha(*pos) || isnum(*pos) || isunderline(*pos))`{`
                        beef = beef + *pos;
                        pos++;
                    `}`
                    if(beef != "if")`{`
                        node(-1,0);
                        table = -1;
                    `}`
                    else node(-1,-p);
                `}`
            `}`            
        `}`
        else if(table == 1)`{`
            node(1,beef);
            while(isskip(*pos))`{`
                pos++;
            `}`
            pos++;
            while(*pos != ')')`{`
                int i = 0;
                if(isend(*pos)) pos++;
                while(!isend(*pos))`{`
                    beef = beef + *pos;
                    pos++;
                `}`
                con[i] = beef;
                i++;
                beef = "";
            `}`

        `}`
        else if(table == -1)`{`
            node++;
            node(-1,0);
            node++;
        `}`
        else if(table == -2 || table == -3)`{`
            while(isskip(*pos))`{`
                pos++;
            `}`
            pos++;
            while(!isend(*pos))`{`
                beef = beef + *pos;
                pos++;
            `}`
            con[0] = beef;
            beef = "";
        `}`

        beef = "";
        pos++;
        compile(*pos);
    `}`
    else if(isnum(*pos))`{`
        do`{`
            num = num * 10 + int(*pos);
            pos++;
        `}`while(isnum(*pos));
        node(num);
        num = 0;
        pos++;
        compile(*pos);
    `}`
    else if(isdollar(*pos))`{`
        pos++;
        while(isalpha(*pos) || isnum(*pos) || isunderline(*pos))`{`
            beef = beef + *pos;
            pos++
        `}`
        node(2,beef);
        beef = "";
        pos++;
        compile(*pos);
    `}`


`}`
```

**<a class="reference-link" name="for"></a>for**

我们不在意他执行多少次，只在意能不能执行，以及执行过程中是否会出现可控的变量。

代码如下

```
void compile(*pos)`{`

  if(isskip(*pos)) pos++;

  else if(isbe(*pos))`{`

​    pos++;

​    q++;

  `}`

  else if(isen(*pos))`{`

​    pos++;

​    q--;

​    if(q == p) node--;

  `}`

  else if(isalpha(*pos))`{`

​    do`{`

​      beef = beef + *pos;

​      pos++;

​    `}`while(isalpha(*pos) || isnum(*pos) || isunderline(*pos));

​    if(table == 0)`{`

​      if(divfind(beef) &gt; 0)`{`

​        Node = new node;

​        p++;

​        node(q);

​        table = divfind(beef);

​      `}`

​      else if(divfind(beef) &lt; -1)`{` 

​        table = divfind(beef);

​        Node = new node;

​        p++;

​        node(q);

​        node(1,beef);

​        if(divfind(beef) == -2)`{`

​          node(-1,-p);

​        `}`

​        else if(divfind(beef) == -3)`{`

​          while(isskip(*pos))`{`

​            pos++;

​          `}`

​          while(isalpha(*pos) || isnum(*pos) || isunderline(*pos))`{`

​            beef = beef + *pos;

​            pos++;

​          `}`

​          if(beef != "if")`{`

​            node(-1,0);

​            table = -1;

​          `}`

​          else node(-1,-p);

​        `}`

​        else if(divfind(beef) == -4)`{`  //for

​          while(isskip(*pos))`{`

​            pos++;

​          `}`

​          pos++;

​          beef = "";

​          for(int i = 0;i &lt; 3;i++)`{`

​            while(!isend(*pos))`{`

​              beef = beef + *pos;

​              pos++;

​            `}`

​            con[i] = beef;

​            beef = "";

​            pos++;

​          `}`

​        `}`

​      `}`      

​    `}`

​    else if(table == 1)`{`   //function

​      node(1,beef);

​      while(isskip(*pos))`{`

​        pos++;

​      `}`

​      pos++;

​      while(*pos != ')')`{`

​        int i = 0;

​        if(isend(*pos)) pos++;

​        while(!isend(*pos))`{`

​          beef = beef + *pos;

​          pos++;

​        `}`

​        args[i] = beef;

​        i++;

​        beef = "";

​      `}`

​      

​    `}`

​    else if(table == -1)`{`    //endif

​      node++;

​      node(-1,0);

​      node++;

​    `}`

​    else if(table == -2 || table == -3)`{`   //if elseif

​      while(isskip(*pos))`{`

​        pos++;

​      `}`

​      pos++;

​      while(!isend(*pos))`{`

​        beef = beef + *pos;

​        pos++;

​      `}`

​      con[0] = beef;

​      beef = "";

​    `}`

​    

​    



​    beef = "";

​    pos++;

​    compile(*pos);

  `}`

  else if(isnum(*pos))`{`

​    do`{`

​      num = num * 10 + int(*pos);

​      pos++;

​    `}`while(isnum(*pos));

​    node(num);

​    num = 0;

​    pos++;

​    compile(*pos);

  `}`

  else if(isdollar(*pos))`{`

​    pos++;

​    while(isalpha(*pos) || isnum(*pos) || isunderline(*pos))`{`

​      beef = beef + *pos;

​      pos++

​    `}`

​    node(2,beef);

​    beef = "";

​    pos++;

​    compile(*pos);

  `}`





`}`
```

### <a class="reference-link" name="%E5%BD%A2%E6%88%90%E7%BB%93%E6%9E%84"></a>形成结构

找到入口函数，一步一步根据文本搜索node，构成CFG。

由于我们编译部分代码从头开始执行，以函数名或者特殊结构为node名称，所以对于入口函数来说，只需要知道入口函数名即可，随后搜索node直到出现新的node为函数名。由于我们按照文本顺序进行分析，且对结构做了特殊定义，如对if else进行标记使得分支结构得以体现，所以这之间的node就是一个CFG结构。

我们使用控制流分析，所以除了入口函数以外，其他函数都属于值。所以CFG结构就是入口函数的结构。

当然，对于其他函数，我们要得到其结果，也需要进行分析，分析方法一致，使用控制流分析，将当前函数分解成CFG结构，其他函数都是值。

代码如下

```
void compile(*pos)`{`

  if(*pos == ';') return;

  string back=""; 

  if(isskip(*pos)) pos++;

  else if(isbe(*pos))`{`

​    pos++;

​    q++;

  `}`

  else if(isen(*pos))`{`

​    pos++;

​    q--;

​    if(q == p) node--;

  `}`

  else if(isequal(*pos))`{`

​    table = 3;

​    back = beef;

  `}`

  else if(isalpha(*pos))`{`

​    do`{`

​      beef = beef + *pos;

​      pos++;

​    `}`while(isalpha(*pos) || isnum(*pos) || isunderline(*pos));

​    if(table == 0)`{`

​      if(divfind(beef) == 1)`{`

​        Node = new node;

​        p++;

​        node(q);

​        table = divfind(beef);

​      `}`

​      else if(divfind(beef) == 2)`{`

​        value[] = node.return;

​      `}`

​      else if(divfind(beef) &lt; -1)`{` 

​        table = divfind(beef);

​        Node = new node;

​        p++;

​        node(q);

​        node(1,beef);

​        if(divfind(beef) == -2)`{`

​          node(-1,-p);

​        `}`

​        else if(divfind(beef) == -3)`{`

​          while(isskip(*pos))`{`

​            pos++;

​          `}`

​          while(isalpha(*pos) || isnum(*pos) || isunderline(*pos))`{`

​            beef = beef + *pos;

​            pos++;

​          `}`

​          if(beef != "if")`{`

​            node(-1,0);

​            table = -1;

​          `}`

​          else node(-1,-p);

​        `}`

​        else if(divfind(beef) == -4)`{`  //for

​          while(isskip(*pos))`{`

​            pos++;

​          `}`

​          pos++;

​          beef = "";

​          for(int i = 0;i &lt; 3;i++)`{`

​            while(!isend(*pos))`{`

​              beef = beef + *pos;

​              pos++;

​            `}`

​            con[i] = beef;

​            beef = "";

​            pos++;

​          `}`

​        `}`

​      `}`      

​    `}`

​    else if(table == 1)`{`   //function

​      node(1,beef);

​      func = func + beef;

​      while(isskip(*pos))`{`

​        pos++;

​      `}`

​      pos++;

​      beef = "";

​      while(*pos != ')')`{`

​        int i = 0;

​        if(isend(*pos)) pos++;

​        while(!isend(*pos))`{`

​          beef = beef + *pos;

​          pos++;

​        `}`

​        args[i] = beef;

​        i++;

​        beef = "";

​      `}`

​      

​    `}`

​    else if(table == 3)`{`

​      while(isskip(*pos))`{`pos++;`}`

​      if(isbool(*pos))`{`

​        pos++;

​        while(isalpha(*pos) || isnum(*pos) || isunderline(*pos) ||isdollar(*pos))`{`

​          beef = beef + *pos;

​          pos++

​        `}`

​      `}`

​      

​      int i = 0;

​      for(;strcmp(args[i],back);i++)`{`;`}`

​      strcpy(val[i],beef);



​    `}`

​    else if(table == -1)`{`    //endif

​      node++;

​      node(-1,0);

​      node++;

​    `}`

​    else if(table == -2 || table == -3)`{`   //if elseif

​      while(isskip(*pos))`{`

​        pos++;

​      `}`

​      pos++;

​      while(!isend(*pos))`{`

​        beef = beef + *pos;

​        pos++;

​      `}`

​      con[0] = beef;

​      beef = "";

​    `}`

​    

​    



​    beef = "";

​    pos++;

​    compile(*pos);

  `}`

  else if(isnum(*pos))`{`

​    do`{`

​      num = num * 10 + int(*pos);

​      pos++;

​    `}`while(isnum(*pos));

​    if(table == 3)`{`

​      int i = 0;

​      for(;strcmp(args[i],back);i++)`{`;`}`

​      strcpy(val[i],beef);

​    `}`

​    num = 0;

​    pos++;

​    compile(*pos);

  `}`

  else if(isdollar(*pos))`{`

​    pos++;

​    beef = "";

​    while(isalpha(*pos) || isnum(*pos) || isunderline(*pos))`{`

​      beef = beef + *pos;

​      pos++

​    `}`

​    node(2,beef);

​    pos++;

​    if(table == 3)`{`

​      while(isskip(*pos))`{`pos++;`}`

​      if(isequal(*pos))`{`

​        pos++;

​        compile(*pos);

​      `}`

​      if(isbool(*pos))`{`

​        pos++;

​        while(isalpha(*pos) || isnum(*pos) || isunderline(*pos) ||isdollar(*pos))`{`

​          beef = beef + *pos;

​          pos++

​        `}`

​      `}`

​      

​      int i = 0;

​      for(;strcmp(args[i],back);i++)`{`;`}`

​      strcpy(val[i],beef);

​    `}`

​    compile(*pos);

  `}`





`}`
```



## AST结构

AST结构在编译过程中和CFG一样，形成结构有其特殊性。

首先，同样是控制流分析，所以函数作为一个最大的模块，特殊结构作为独立个体。其特殊性在于对于语句的分析：CFG在意流程。AST在意语法。

我们对于每一句代码都进行类型的定义，对数据变量进行左值右值的划分，形成层层递进的树状结构。

代码如下

```
void ast(string stmt)`{`

  while(isskip(*pos)) pos++;

  while(*pos != '=')`{`

​    beef = beef + *pos;

​    pos++;

  `}`

  node.left = beef;

  pos++;

  while(*pos != ';')`{`

​    beef = beef + *pos;

​    pos++;

  `}`

  node.right = beef;

  ast(beef);



`}`



void ast(char *pos)`{`

  if(isalpha(*pos))`{`

​    while(isalpha(*pos))`{`

​      beef = beef + *pos;

​      pos++;

​    `}`

​    if(isskip(*pos) &amp;&amp; beef == "function")`{`

​      node = node.next;

​      beef = "";

​      node.type = "function";

​      while(isskip(*pos)) pos++;

​      while(isalpha(*pos) || isnum(*pos) || isunderline(*pos))`{`

​        beef = beef + *pos;

​        pos++;

​      `}`

​      node.name = beef;

​      beef = "";

​      while(isskip(*pos)) pos++;

​      pos++;

​      for(int i = 0; *pos != ')';i++)`{`

​        while(!isend(*pos))`{`

​          beef = beef + *pos;

​        `}`

​        node.args[i] = beef;

​        pos++;

​      `}`

​      beef = "";

​      while(isskip(*pos)) pos++;

​      int p = 0;

​      for(int i = 0; *pos != '`}`' || p != 0;i++)`{`

​        pos++;

​        if(*pos == '`{`') p++;

​        else if(*pos == '`}`') p--;

​        else`{`

​          ast(*pos);

​        `}`

​      `}`

​    `}`

​    else if((*pos == '(' || isskip(*pos)) &amp;&amp; beef == "for")`{`

​      node = node.next;

​      beef = "";

​      node.type = "for";

​      pos++;

​      for(int i = 0;i&lt;3;i++)`{`

​        while(!isend(*pos))`{`

​          beef = beef + *pos;

​        `}`

​        node.con[i] = beef;

​        ast(beef);

​        beef = "";

​        pos++;

​      `}`

​      ast(*pos);

​    `}`

​    else if((*pos == '(' || isskip(*pos)) &amp;&amp; beef == "if")`{`

​      node = node.next;

​      beef = "";

​      node.type = "if";

​      pos++;

​      while(!isend(*pos))`{`

​        beef = beef + *pos;

​        pos++;

​      `}`

​      node.con[0] = beef;

​      ast(beef);

​      ast(*pos);

​    `}`

​    else if((*pos == '(' || isskip(*pos)) &amp;&amp; beef == "else")`{`

​      node = node.next;

​      while(isskip(*pos)) pos++;

​      if(*pos == '`{`')`{`

​        node.type = "else";

​        pos++;

​        node.con[0] = "-1";

​      `}`

​      else if(*pos == 'i')`{`

​        while(*pos != '(') pos++;

​        while(!isend(*pos))`{`

​          beef = beef + *pos;

​          pos++;

​        `}`

​        node.com[0] = beef;

​        ast(beef);

​        ast(*pos);

​      `}`

​    `}`

  `}`

  else if(*pos == '$')`{`

​    while(*pos != ';')`{`

​      beef = beef + *pos;

​      pos++;

​    `}`

​    ast(beef);

​    ast(*pos);

  `}`

  else`{`

​    pos++;

​    return ;

  `}`





`}`
```



## 最后

我们这一次的初尝试是对之前讲过的自动机分析的原理，控制流分析的原理的一次应用。欢迎各位指教。
