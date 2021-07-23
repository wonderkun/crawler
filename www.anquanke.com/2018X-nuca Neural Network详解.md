> 原文链接: https://www.anquanke.com//post/id/166501 


# 2018X-nuca Neural Network详解


                                阅读量   
                                **179652**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t019e726e4631d44956.png)](https://p3.ssl.qhimg.com/t019e726e4631d44956.png)



## 前言

这道题当时没有队伍解出来，我当时想是有更多的步骤在图里面，tensorboard检测不出来，或者那些其余的操作有影响，当时有个提示是并非所有节点都在图里，最后又找了一遍pbtext的文本，看到有个节点带了很多数据，名字又是precisefinal，就感觉这是精确数据，最后拿到flag。



## Neural Network

神经网络，一个完全没接触过的全新领域。先查一波资料：

<a>TensorFlow中文社区</a>

[tensorboard使用](https://blog.csdn.net/czq7511/article/details/72480149)

[Tensorflow 模型文件的使用以及格式转换](https://blog.csdn.net/loveliuzz/article/details/81383098)

tensorflow只能在python3.5和python3.6安装，踩坑就踩了好久。

搭好环境直接跑一下它的python脚本，除了有个提示外都正常，提示可以在脚本开头加段代码去掉

```
import os 
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
```

运行一下python脚本，随便输点东西进去，然后弹出错误警告。似乎是大小不对，应该32个而不是16个。看一下脚本的内容，`get_input`函数里把输入rjust了16，改成32，这样就可以跑了，输出了`Sorry, srcret wrong! Try harder?`

分析一下脚本，结合各种地方找的资料，发现他读取了一个`model.meta`文件作为图，x应该是输入tensor，y是输出tensor。把输入放进黑盒操作一波得到输出，然后跟常量final比较，要求误差在1e-8之内。

看样子重点就在于它的`model.meta`这个文件里了。用hexeditor打开，只能看到一些字符串和数据。

在查一波资料，发现了tensorboard这个东西，他能把meta文件的内容转化成图，于是根据教程，得到了这个模型的模型图。

[![](https://p5.ssl.qhimg.com/t01eda6ed3e7847b5e1.jpg)](https://p5.ssl.qhimg.com/t01eda6ed3e7847b5e1.jpg)

点进各个节点可以看到每个节点的输入(Inputs)，输出(Outputs)和操作(Operation)。于是我们找到了`In_string`和`Out_judge`。跟着`Out_judge`的操作沿着输入一步一步往前走，能找到In_string。这些个过程就是黑盒的过程了。注意其中有很多的分支是没用到的，不必理会。最终整理出正向的操作（用tensorflow的函数表示）：

```
t0 = tf.matmul(In_string, v0)
t1 = tf.add(t0, v3)
t2 = tf.sigmoid(t1)
t3 = tf.matmul(t2, v1)
t4 = tf.add(t3, v4)
t5 = tf.tanh(t4)
t6 = tf.matmul(t5, v2)
t7 = tf.add(t6, v5)
t8 = tf.sigmoid(t7)
```

matmul：矩阵相乘

sigmoid：S型生长曲线，具体可以百度

add:两个矩阵对应量相加

tanh：双曲正切

relu：正数不变，负数变为为0

这里的v0到v5都是常量。参考脚本中res的用法，可以拿到数据：

```
def gn(nm):
    return sess.run(nm + ":0", feed_dict=`{`x:[X]`}`)

In_string = gn("In_string")
v0 = gn("Variable/read")
v1 = gn("Variable_1/read")
v2 = gn("Variable_2/read")
v3 = gn("Variable_3/read")
v4 = gn("Variable_4/read")
v5 = gn("Variable_5/read")
```

为了方便调试，我们定义：

```
def gv(v):
    return sess.run(v, feed_dict=`{`x:[X]`}`)
print(gv(a0))
```

直接print(t1)并不能输出它的值。参考之前的res，要把数据喂进去run一下，会返回一个numpy的array数据类型，于是这样就可以输出了。

同时，输出np.array时默认会省略一些数据用省略号代替，且输出的精度不足。为了更直观的观看，可以添加如下代码：

```
np.set_printoptions(threshold='nan')
np.set_printoptions(precision=20)
```

有了正向的输入过程，每个函数都是有反函数的，我们似乎就可以逆向得到输入了，逆向过程如下

```
from scipy.special import logit

def invsigmoid(a):
    b= np.array([[0.0]*32])
    for i in range(32):
        b[0][i]=logit(a[0][i]) #logit为sigmoid的反函数，但是tensorflow中没有这个函数，只能借助scipy中的了 
    return b

a = np.array([[1.40895243e-01, 9.98096014e-01, 1.13422030e-02, 6.57041353e-01,
    9.97613889e-01, 9.98909625e-01, 9.92840464e-01, 9.90108787e-01,
    1.43269835e-03, 9.89027450e-01, 7.22652880e-01, 9.63670217e-01,
    6.89424259e-01, 1.76012035e-02, 9.30893743e-01, 8.61464445e-03,
    4.35839722e-01, 8.38741174e-04, 6.38429400e-02, 9.90384032e-01,
    1.09806946e-03, 1.76375112e-03, 9.37186997e-01, 8.32329340e-01,
    9.83474966e-01, 8.79308946e-01, 6.59324698e-03, 7.85916088e-05,
    2.94269115e-05, 1.97006621e-03, 9.99416387e-01, 9.99997202e-01]])
a0=invsigmoid(a)
a1=tf.subtract(a0,v5)
a2=tf.matmul(a1,tf.matrix_inverse(v2))
a3=tf.atanh(a2)
a4=tf.subtract(a3,v4)
a5=tf.matmul(a4,tf.matrix_inverse(v1))
a6=invsigmoid(gv(a5))#a5是个tensor对象，要用np.array数据类型才能使用。
a7=tf.subtract(a6,v3)
a8=tf.matmul(a7,tf.matrix_inverse(v0))
l=gv(a8).tolist()
ll=l[0]
flag=''
for i in range(len(ll)):
    ll[i]*=128
    ll[i]=round(ll[i])
    flag+=chr(ll[i])
print(flag)
```

然而出问题了。最终的a8全是naf。让我们想办法输出中间变量的值，看看哪里有问题。在每一步后面输出a的数据。调着调着发现，第二个invsigmoid出了问题，意义不明（似乎是超出定义域了）。

思考了一下，我先随便输一个数据进去，用它算的结果逆一遍，看看能不能得到原来的值，于是：

```
def trans(secret):
    return np.array([float(ord(x))/128 for x in secret])
fakeflag = "flag`{`01234567012345670123456789`}`"
X = trans(fakeflag)
sess = tf.Session()
saver = tf.train.import_meta_graph('model.meta')
saver.restore(sess, tf.train.latest_checkpoint('./'))
graph = tf.get_default_graph()
x = graph.get_tensor_by_name('In_string:0')
y = graph.get_tensor_by_name("Out_judge:0")
res = sess.run(y, feed_dict=`{`x:[X]`}`)

a0=invsigmoid(res)
a1=tf.subtract(a0,v5)
a2=tf.matmul(a1,tf.matrix_inverse(v2))
a3=tf.atanh(a2)
a4=tf.subtract(a3,v4)
a5=tf.matmul(a4,tf.matrix_inverse(v1))
a6=invsigmoid(gv(a5))#a5是个tensor对象，要用np.array数据类型才能使用。
a7=tf.subtract(a6,v3)
a8=tf.matmul(a7,tf.matrix_inverse(v0))
l=gv(a8).tolist()
ll=l[0]
flag=''
for i in range(len(ll)):
    ll[i]*=128
    ll[i]=round(ll[i])
    flag+=chr(ll[i])
print(flag)
```

到这里可以算回我的假flag，说明算法是没问题的。思前想后觉得应该是精度的问题。注意到体重final的精度是9位有效数字。我尝试把假flag得到的最终结果保留9位有效数字，再带进逆向算法中，就算不出假flag了。同时我逐步提高精度，发现要有14位以上有效数字的精度才能算出正确的输入！这让我不禁怀疑题目的正确性。找主办方交涉无果，只好重新找方向。

显然我们没办法提高数据的精度，一时间陷入了僵局。

查找资料解读meta的时候，除了用tensorboard看图形外，还发现了可以吧meta转成txt输出：

```
sess = tf.Session()
saver = tf.train.import_meta_graph('model.meta')
saver.restore(sess, tf.train.latest_checkpoint('./'))
graph = tf.get_default_graph()
tf.train.write_graph(graph, './aaa', 'train.pbtxt')
```

打开train.pbtxt，在这里可以看到所有的node，包括之前的`Variable`等。比赛时并没有太注意，只当用到的东西已经输出了。

最早看这个pbtxt的时候并没有很仔细，更多的跑去看tensorboard了。赛后重新看一下pbtxt，发现了很可疑的一段：

```
node `{`
  name: "PRECISEFINAL"
  op: "Const"
  attr `{`
    key: "dtype"
    value `{`
      type: DT_DOUBLE
    `}`
  `}`
  attr `{`
    key: "value"
    value `{`
      tensor `{`
        dtype: DT_DOUBLE
        tensor_shape `{`
          dim `{`
            size: 1
          `}`
          dim `{`
            size: 32
          `}`
        `}`
        tensor_content: "!333736633210302?3068crg360357?02\336266224:207?367s226226`{`06345?211224C366s354357?tkYQ21367357?303CE]Y305357?20705215237370256357?30344262",yW?320732534434246357?26733533635637037347?367345j354b326356?|34lv30317346?210242s3061406222?372353304254341311355?245\21401216244201?%254@J314344333?30?251364336`{`K?k24R31302X260?331361R3329261357?27U36433243375Q?#31dW265345\?265b315225o375355?22207375#q242352?H330273`}`240x357?A362214203L#354?L00207B20501`{`?32334403217123224?03222)3659333376&gt;372241322=207#`?36132424238373357?3713327!372377357?"
      `}`
    `}`
  `}`
`}`
```

这个名为`PRECISEFINAL`的node根本没见过，里面还藏有大量数据，难道这就是精确的final值？（名字都告诉你了是精确final了好吧）

把它带进脚本跑一下，flag就出了，而且直接查看它的数据可以发现它的精度是15位有效数字。

脚本：

```
import os 
import numpy as np
import tensorflow as tf
from math import isclose
from scipy.special import logit

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
np.set_printoptions(precision=20)
np.set_printoptions(threshold='nan')


def trans(secret):
    return np.array([float(ord(x))/128 for x in secret])

def gn(nm):
    a=graph.get_tensor_by_name(nm + ":0")
    return sess.run(a, feed_dict=`{`x:[X]`}`)

def gv(v):
    return sess.run(v, feed_dict=`{`x:[X]`}`)

def invsigmoid(a):
    b= np.array([[0.0]*32])
    for i in range(32):
        b[0][i]=logit(a[0][i])
    return b


fakeflag = "flag`{`01234567012345670123456789`}`"
X = trans(fakeflag)
#print(X)
sess = tf.Session()
saver = tf.train.import_meta_graph('model.meta')
saver.restore(sess, tf.train.latest_checkpoint('./'))
graph = tf.get_default_graph()
x = graph.get_tensor_by_name('In_string:0')
y = graph.get_tensor_by_name("Out_judge:0")
final = np.array([[1.40895243e-01, 9.98096014e-01, 1.13422030e-02, 6.57041353e-01,
    9.97613889e-01, 9.98909625e-01, 9.92840464e-01, 9.90108787e-01,
    1.43269835e-03, 9.89027450e-01, 7.22652880e-01, 9.63670217e-01,
    6.89424259e-01, 1.76012035e-02, 9.30893743e-01, 8.61464445e-03,
    4.35839722e-01, 8.38741174e-04, 6.38429400e-02, 9.90384032e-01,
    1.09806946e-03, 1.76375112e-03, 9.37186997e-01, 8.32329340e-01,
    9.83474966e-01, 8.79308946e-01, 6.59324698e-03, 7.85916088e-05,
    2.94269115e-05, 1.97006621e-03, 9.99416387e-01, 9.99997202e-01]])
res = sess.run(y, feed_dict=`{`x:[X]`}`)

In_string = gn("In_string")
v0 = gn("Variable/read")
v1 = gn("Variable_1/read")
v2 = gn("Variable_2/read")
v3 = gn("Variable_3/read")
v4 = gn("Variable_4/read")
v5 = gn("Variable_5/read")
precisefinal=gn("PRECISEFINAL")

a0=invsigmoid(precisefinal)
a1=tf.subtract(a0,v5)
a2=tf.matmul(a1,tf.matrix_inverse(v2))
a3=tf.atanh(a2)
a4=tf.subtract(a3,v4)
a5=tf.matmul(a4,tf.matrix_inverse(v1))
a6=invsigmoid(gv(a5))
a7=tf.subtract(a6,v3)
a8=tf.matmul(a7,tf.matrix_inverse(v0))
l=gv(a8).tolist()
ll=l[0]
flag=''
for i in range(len(ll)):
    ll[i]*=128
    ll[i]=round(ll[i])
    flag+=chr(ll[i])
print(flag)
```

最终运行脚本得到flag

[![](https://p1.ssl.qhimg.com/t01644da73fcacf3f33.png)](https://p1.ssl.qhimg.com/t01644da73fcacf3f33.png)
