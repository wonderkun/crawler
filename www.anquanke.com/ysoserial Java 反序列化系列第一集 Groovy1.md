
# ysoserial Java 反序列化系列第一集 Groovy1


                                阅读量   
                                **640133**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](./img/202730/t0103a36c67bd1775a3.png)](./img/202730/t0103a36c67bd1775a3.png)



## ysoserial简介

ysoserial是一款在Github开源的知名java 反序列化利用工具，里面集合了各种java反序列化payload；

由于其中部分payload使用到的低版本JDK中的类，所以建议自己私下分析学习时使用低版本JDK JDK版本建议在1.7u21以下。

此篇文章为java反序列化系列文章的第一篇，后续会以ysoserial这款工具为中心，挨个的去分析其中的反序列化payload和gadget，讲完该工具后会继续对工具中没有的java 反序列化漏洞进行讲解，例如 FastJson JackSon，WebLogic等等，并将这些漏洞的exp加入到ysoserial中然后共享和大家一起学习交流。

源码下载地址

[https://codeload.github.com/frohoff/ysoserial/zip/master](https://codeload.github.com/frohoff/ysoserial/zip/master)

jar包下载地址

[https://jitpack.io/com/github/frohoff/ysoserial/master-30099844c6-1/ysoserial-master-30099844c6-1.jar](https://jitpack.io/com/github/frohoff/ysoserial/master-30099844c6-1/ysoserial-master-30099844c6-1.jar)



## 源码深度解析

我们首先看一下该payload的整个源码

[![](./img/202730/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0169d1ddf58636fd2f.png)

代码量其实很少，但是调用了一些别的类中的方法，看起来可能不是太直观，我将调用方法中所做的操作都写到一个类的main方法中这样看起来应该会更好理解一些。

先写一个简化版的可以执行代码的Demo

[![](./img/202730/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0160c22f8a3dca10ab.png)

直接运行的话会执行我们预先设定好的命令，调用计算器

[![](./img/202730/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0198adbdc70b4a7a21.png)

但是这短短几行代码里我们并没有调用Runtime对象的exec方法亦或着ProcessBuilder对象的star方法来执行命令，我们仅仅调用了一个Map对象的entrySet()方法，怎么就可以执行命令了呢？

对java有些许了解的同学应该熟悉Map.Entry是Map里面的一个接口，主要用途是来表示Map对象中的一个映射项也就是一个&lt;key,value&gt; 并提供了以下五个方法,通常我们会使用map.entrySet().iterator()，方法得到一个Iterator对象从而对Map中的Entry对象进行遍历，那为何一个获取遍历对象的操作会导致代码执行呢？这里就涉及到这个Map对象究竟是哪一个实现了Map接口的类来实例化的。

[![](./img/202730/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t014343b738b2b049c2.png)

首先我们先来看看这个map变量里面保存的是什么

[![](./img/202730/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t019e96c912885db3e9.png)

居然是一个代理对象，这里就要涉及到java的一个知识点，就是所谓的动态代理。动态代理其实不难理解，可以写个简单的例子,以下是这个例子的代码。

[![](./img/202730/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t010cc73a1bb6cd15ae.png)

我们可以看到我们写了一个Son类继承了Father接口，然后在Test3类中的main方法中被实例化，接下来我们通过Proxy的newProxyInstance方法生成了一个Son对象的代理，我们传递了三个参数进去，Son类的类加载器和实现的接口，这里注意被代理的对像是一定要实现至少一个接口的，因为实例化的代理类本身是继承了Proxy类，所以只能通过实现被代理类接口的形式来实例化。最后我们通过匿名内部类的形式传入了一个InvocationHandler对象，InvocationHandler是一个接口，该接口中只有一个方法就是invoke方法，所以我们一定要重写该方法。

然后我们看执行结果

[![](./img/202730/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0138138c2423b431d8.png)

可以看到，我们调用Son对象本身和Son的代理对象所执行的结果是不同的，因为代理对象在执行被代理对象的任意方法时，会首先执行我们之前重写的InvocationHandler的invoke方法。同时会传入三个参数，第一个参数是代理对象本身，第二个参数是你要执行的方法的方法名，第三个参数是你要执行的该方法时要传递的参数。关键点在于什么？在于无论你调用代理对象的那一个方法，都一定要先执行这个Invoke方法。

然后返回到我们之前的payload中我们可以看到我们使用Proxy.newProxyInstance方法生成了一个代理对象，然后将其强转成了一个Map对象然后调用了entrySet方法。

[![](./img/202730/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t013d79c85f7dadccad.png)

接下来我们先记住我们payload所用到的两个类也就是所谓的gadget

[![](./img/202730/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t018de83a5e844b5f3d.png)

是位于org.codehaus.groovy.runtime包下的ConvertedClosure和MethodClosure。

接下来我们就来一步一步的调试分析

[![](./img/202730/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012c95e61c5c50fa2d.png)

首先我们生成一个MethodClosure对象并将我们要执行的命令和和一个值为“execute”的字符串传递进去我们跟进

[![](./img/202730/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01572b79c05f6358ce.png)

可以看到我们将要执行的命令传给了MethodClosure的父类来处理，将“execute”赋值给了MethodClosure.method属性。然后紧接着跟到Closure的构造方法中看到命令被赋值给了Closure.owner和Closure.delegate属性，之所以讲这些赋值过程是因为后面都会用得到。[![](./img/202730/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t015ca86be60f999d7d.png)

接下来payload中又实例化了另一个对象并将刚才实例化的MethodClosure对象和一个字符串常量“entrySet”传入，我们同样继续跟进。[![](./img/202730/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01742d9098cee2900f.png)

字符串常量被赋值给ConvertedClosure.methodName属性

[![](./img/202730/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0112ad285497b82ac1.png)

MethodClosure对象赋值给父类的的ConversionHandler.delegate属性

[![](./img/202730/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t012b6ee0aebecbd1c1.png)

接下这两步就是生成一个Class类型的Arry数组因为Proxy.newProxyInstance方法第二个参数是动态代理类要实现的接口要以数组的形式传入。所以我们生成了一个Class数组并在其中存入我要实现的接口也就是Map.calss

[![](./img/202730/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01a9a7ac9b82660619.png)

接下来就是生成动态代理对象的过程了，这个在前面已经介绍过了，Proxy.newProxyInstance方法传递的第二个参数是代理类所要实现的接口，里面只有一个Map.class所以生成的代理对象是实现了Map接口里所有方法的，所以才可以将其强转成Map类型并调用entrySet方法

[![](./img/202730/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01cc7774e2b4943f08.png)

之前我们也说了动态代理的一大特点就是不论你调用代理对象的哪一个方法其实执行的都是我们创建代理对象时所传入的InvocationHandler对象中我们所重写的Invoke方法。这里传入的InvocationHandler对象就是我们之前实例化的ConvertedClosure我们看一下该类的继承关系

[![](./img/202730/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0127d921a8fe7e271d.png)

可以看到ConvertedClosure类的继承关系中其父类ConversionHandler实现了InvocationHandler并重写了Invoke方法，所以我们由此可知当我们调用代理对象map.entrySet方法时实际上执行的是ConversionHandler.Invoke方法。我们跟进方法继续分析。

[![](./img/202730/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0173a7756699c43364.png)

紧接着由调用了invokeCustom方法，该方法在ConversionHandler中是一个抽象方法，所以调用的是其子类重写的ConvertedClosure.invokeCustom方法。

[![](./img/202730/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01097da1c13fe0d8b2.png)

之前我们创建ConvertedClosure对象时为methodName属性赋了值“entrySet”此时我们调用的是代理对象的entrySet方法，自然传递进来method的值也是“entrySet”符合判断。

接下来的getDelegate()是其父类的方法也就是ConversionHandler.getDelegate()

[![](./img/202730/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a794b75a97cf270b.png)

返回一个MethodClosure对象也就是并将其强转成Closure，然后调用Closure.call()方法

[![](./img/202730/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f76b1e357e53d698.png)

紧接着调用Closure的父类GroovyObjectSupport.getMetaClass()方法返回一个MetaClassImpl对象并调用MetaClassImpl.invokeMethod()方法

步入跟进该方法

```
MetaMethod method = null;
......
   if (method==null) {
            method = getMethodWithCaching(sender, methodName, arguments, isCallToSuper);
        }
......
    final boolean isClosure = object instanceof Closure;
        if (isClosure) {
            final Closure closure = (Closure) object;

            final Object owner = closure.getOwner();

            if (CLOSURE_CALL_METHOD.equals(methodName) || CLOSURE_DO_CALL_METHOD.equals(methodName)) {
                final Class objectClass = object.getClass();
                if (objectClass == MethodClosure.class) {
                    final MethodClosure mc = (MethodClosure) object;
                    methodName = mc.getMethod();
                    final Class ownerClass = owner instanceof Class ? (Class) owner : owner.getClass();
                    final MetaClass ownerMetaClass = registry.getMetaClass(ownerClass);
                    return ownerMetaClass.invokeMethod(ownerClass, owner, methodName, arguments, false, false);
```

该方法代码过多先截取关键代码，首先创建一个Method类型的变量并为其赋值，然后我们通过判断传入的Object是否是Closure的子类，由截图可以看出Object里存储的是一个MethodClosure对象，所以判断的结果是true 接下来就走第一条判断成功执行的代码。

[![](./img/202730/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ac4017e1fccb2b34.png)

接下来执行的就是将Object强转为Closure类型，接下来取出我们一开始我们在创建MethodClosure对象时存入的要执行的命令。

[![](./img/202730/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a47f596a43c58ff8.png)

接下来就一路执行到return ownerMetaClass.invokeMethod()

[![](./img/202730/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0162c476a342a389c4.png)

我们看到这个ownerMetaClass其实还是一个MetaClassImpl对象也就是说这里其实是一个递归调用。

[![](./img/202730/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t018947d41bf6d5b802.png)

以下是递归调用的执行路径可以看到在if (isClosure)这里判断失败了，所以不再执行刚才的代码改为执行method.doMethodInvoke()

```
MetaMethod method = null;
......
if (method == null)
     method = tryListParamMetaMethod(sender, methodName, isCallToSuper, arguments);
......
final boolean isClosure = object instanceof Closure;
if (isClosure) {
  ......
}
if (method != null) {
      return method.doMethodInvoke(object, arguments);
   } 
......
```

我们看到method变量里存储的是一个叫dgm的对象

[![](./img/202730/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01423e161bb267a36b.png)

以下是传入method.doMethodInvoke() 的两个参数里面所存储的值

[![](./img/202730/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011f03412e22f094f1.png)

[![](./img/202730/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0195b738f2dfef2198.png)

我们要执行的命令被传进了ProcessGroovyMethods.execute((String)var1)方法中，继续跟进。

[![](./img/202730/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0169bf95826e2b4ac5.png)

至此通过调用Map.entrySet()方法就能导致代码执行的原理水落石出。

[![](./img/202730/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01264a806926f5d5a4.png)

以上就是ysoserial的payload中的Groovy的gadget介绍。接下来要讲的就是反序列化漏洞中的反序列化如何配和Groovy1的gadget来远程代码执行的。

我们来看ysoserial Groovy1所执行的全部代码。我们可以看到在第34行代码以前，执行的代码和我们之前看到的简化版的代码执行Demo是一样的。

[![](./img/202730/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01010ef6e676b2a8bb.png)

我们看到我们通过反射先是拿到了AnnotationInvocationHandler此类的Class对象，然后在通过该Class对象以反射的形式拿到了它的构造方法，并最终通过该构造方法反射并传入两个参数一个是Override.class一个常见的注解类对象。而另一个就是我们之前所分析的可以通过调用Map.entrySet()方法可以造成代码执行的Map对象。

[![](./img/202730/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0185ee2a782237d64f.png)

为什么我们要如此的费力通过反射形式来生成一个AnnotationInvocationHandler对象呢？由以下截图可知。因为该类的构造方法和该类本身都不是public修饰的，所以我们没法通过new一个对象的形式来创建AnnotationInvocationHandler对象

[![](./img/202730/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t012f2d66ee668c8921.png)

之前已经简单介绍过了什么是反序列化，JDK序列化/反序列化。如果反序列化的类里有readObject方法，那么就一定会调用该方法。这就给了我们一个可趁之机，我们观察一下AnnotationInvocationHandler对象中都执行了些什么。

```
private void readObject(java.io.ObjectInputStream s)
throws java.io.IOException, ClassNotFoundException {
s.defaultReadObject();
// Check to make sure that types have not evolved incompatibly
AnnotationType annotationType = null;
try {
    annotationType = AnnotationType.getInstance(type);
} catch (IllegalArgumentException e) {
    // Class is no longer an annotation type; time to punch out
    throw new java.io.InvalidObjectException("Non-annotation type in annotation serial stream");
}
Map&lt;String, Class&lt;?&gt;&gt; memberTypes = annotationType.memberTypes();
// If there are annotation members without values, that
// situation is handled by the invoke method.
for (Map.Entry&lt;String, Object&gt; memberValue : memberValues.entrySet()) {
    String name = memberValue.getKey();
    Class&lt;?&gt; memberType = memberTypes.get(name);
    if (memberType != null) {  // i.e. member still exists
        Object value = memberValue.getValue();
        if (!(memberType.isInstance(value) ||
                value instanceof ExceptionProxy)) {
            memberValue.setValue(
                    new AnnotationTypeMismatchExceptionProxy(
                            value.getClass() + "[" + value + "]").setMember(
                            annotationType.members().get(name)));
        }
    }
}
}
```

我们在这段代码里看到了一个熟悉的影子，在readObject方法里有一个foreach循环,里面有一个名字叫memberValues的变量调用的entrySet()，也就是说，如果这个memberValues里面存储的是我们之前构造好的那个实现了Map接口的代理对象的话，那就意味着这里就像一个炸弹的引爆点一样，会瞬间执行我们刚才所分析的代码执行路径，并最终执行我们提前包装好的代码。

好，那接下来的问题是这个变量我们可以控制么？如果该变量不接受外部传入的参数那么这个点就变的毫无价值。但是我们通过分析惊喜的发现，memberValues是一个全局变量，接受的恰好就是我们精心构造的那个可以执行代码的代理对象。

[![](./img/202730/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t018c957553bff83236.png)

AnnotationInvocationHandler对我们来说就是一个反序列化的入口点，就像是一个引爆器一样。而我们封装好的那个代理对象就是炸弹，在AnnotationInvocationHandler进行序列化时被封装了进去作为AnnotationInvocationHandler对象一个被序列化的属性存在着，等到AnnotationInvocationHandler对象被反序列化时，就瞬间爆炸，一系列的嵌套调用瞬间到达执行Runtime.getRuntime().exec()的位置

我们以上所介绍的AnnotationInvocationHandler是低版本的JDK中的，我所使用的是1.7.0_21这个版本来做的演示，但是经过验证高版本的JDK中的AnnotationInvocationHandler这个类虽然经过了修改但是仍然存在这个问题，还是可以触发我们的gadget以下是JDK1.8.0._211版本的AnnotationInvocationHandler类的readObject方法的源码

```
private void readObject(ObjectInputStream var1) throws IOException, ClassNotFoundException {
        GetField var2 = var1.readFields();
        Class var3 = (Class)var2.get("type", (Object)null);
        Map var4 = (Map)var2.get("memberValues", (Object)null);
        AnnotationType var5 = null;

        try {
            var5 = AnnotationType.getInstance(var3);
        } catch (IllegalArgumentException var13) {
            throw new InvalidObjectException("Non-annotation type in annotation serial stream");
        }

        Map var6 = var5.memberTypes();
        LinkedHashMap var7 = new LinkedHashMap();

        String var10;
        Object var11;
        for(Iterator var8 = var4.entrySet().iterator(); var8.hasNext(); var7.put(var10, var11)) {
            Entry var9 = (Entry)var8.next();
            var10 = (String)var9.getKey();
            var11 = null;
            Class var12 = (Class)var6.get(var10);
            if (var12 != null) {
                var11 = var9.getValue();
                if (!var12.isInstance(var11) &amp;&amp; !(var11 instanceof ExceptionProxy)) {
                    var11 = (new AnnotationTypeMismatchExceptionProxy(var11.getClass() + "[" + var11 + "]")).setMember((Method)var5.members().get(var10));
                }
            }
        }
```

可以看到出发点仍然在foreach循环的条件里面，只不过是获取构造好的动态代理对象的方式发生了一点变化，但是仍然不会影响我们使用。

至此ysoserial Java 反序列化系列第一集 Groovy1原理分析结束



## 总结

其实网上反序列化的文章有很多，但是不知为何大家讲解反序列化漏洞时都是用CC链也就是Apache.CommonsCollections来进行举例，平心而论笔者觉得这个利用链一开始没接触过反序列化的同学直接理解还有一定的难度的，难在整个CC链的调用看上去略微复杂，并不是难在反序列化的部分。所笔者挑了一个个人觉得调用链比较清晰明了的Groovy来进行java 反序列化分析的第一篇文章，来帮助大家能更快速的了解java 反序列化漏洞。虽然Groovy1这个gadget在实际生产环境中碰的的概率可能少之又少，但是作为一个反序列化入门学习的例子笔者个人觉得还是比较适合的。
