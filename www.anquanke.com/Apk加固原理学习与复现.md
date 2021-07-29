> 原文链接: https://www.anquanke.com//post/id/247644 


# Apk加固原理学习与复现


                                阅读量   
                                **22938**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                    



[![](https://p1.ssl.qhimg.com/t01353a2db33ca1c06d.jpg)](https://p1.ssl.qhimg.com/t01353a2db33ca1c06d.jpg)



## 前言

针对当下反编译技术的逐步发展，加固技术也在与之对抗中发展，本文旨在对最简单的加固方式和加固的原理做一个介绍，并且对代码做一个复现。



## 加固原理图解：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0104e98fdc5120a957.png)

如上图，对于得到的源apk，由于其中的保留信息较为完善，所以会很容易被反编译，利用GDA、JEB配合IDA等工具，可以轻松的得到程序里面的重要信息，为了保护这些信息，我们一般会对其进行加固，简而言之就是在程序外面再套一个壳子来将源程序保护起来，就像鸡蛋壳保护着鸡蛋、乌龟壳保护着乌龟一样。当然这其中也有着鸡蛋壳容易打碎，乌龟壳不易打碎的说法，在这里只做加固的原理的学习，至于加固之后的保护性强不强、容不容易被破坏，本文暂不做研究。<br>
在上图中，简易的描述了加固的原理，首先我们会拿到一个需要加固的源apk文件，然后需要加固这个源apk，我们就会写一个对应的壳程序，然后我们需要将两个apk合并，为了让程序能够正常运行，我们就需要将源apk文件和壳程序的dex文件进行合并，然后用合并之后的dex文件将可程序的dex文件替换掉，这样我们的壳程序就会照成运行。<br>
既然需要这样做，就会有些问题出现：<br>
如何将源apk和壳程序的dex文件合并？<br>
源apk外面套着壳程序的dex文件，那么怎么让这个app运行之后执行源apk里面的代码，而不是只执行壳程序的代码——即不能改变源apk的执行逻辑？<br>
针对上述问题，我们先做一个前置知识的学习。



## 前置知识

### <a class="reference-link" name="Dex%E6%96%87%E4%BB%B6"></a>Dex文件

#### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AFDex%E6%96%87%E4%BB%B6"></a>什么是Dex文件

我们都知道apk的本质是一个压缩包，当我们直接将.apk的后缀改为.zip的时候，是可以直接解压出里面的文件的(甚至有些压缩软件可以直接解压.apk文件，例如bindizip)。那么app为什么能在手机中运行呢，靠的就是.dex文件，在Windows端的可执行文件是.exe文件，JVM的可执行文件是.class文件，那么在Android中的dalvik或art虚拟机上运行的可执行文件就是.dex文件。<br>
Dex文件结构<br>
首先是Dex文件结构的源代码：[http://androidxref.com/9.0.0_r3/xref/dalvik/libdex/DexFile.h](http://androidxref.com/9.0.0_r3/xref/dalvik/libdex/DexFile.h)<br>
首先来看一下看雪神图，出自非虫，在图中对Dex结构做了十分详细的定义。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01035749ecc6e28823.png)

接下来我们借助010Editor对随意一个Dex文件做一个解析。

[![](https://p0.ssl.qhimg.com/t0101f7078ba6790594.png)](https://p0.ssl.qhimg.com/t0101f7078ba6790594.png)

根据上面两个图我们发现，dex大致可以分为以下几个part：

[![](https://p0.ssl.qhimg.com/t016933edeb70a84fb2.png)](https://p0.ssl.qhimg.com/t016933edeb70a84fb2.png)

header : DEX 文件头，记录了一些当前文件的信息以及其他数据结构在文件中的偏移量<br>
string_ids : 字符串的偏移量<br>
type_ids : 类型信息的偏移量<br>
proto_ids : 方法声明的偏移量<br>
field_ids : 字段信息的偏移量<br>
method_ids : 方法信息（所在类，方法声明以及方法名）的偏移量<br>
class_def : 类信息的偏移量<br>
data : ： 数据区<br>
link_data : 静态链接数据区<br>
由于本文主题是apk加固，所以详细的Dex信息查看另一篇文章：[https://www.yuque.com/u2172011/abm9ei/gx5btd](https://www.yuque.com/u2172011/abm9ei/gx5btd)<br>
我们这里详细看一下dex header部分的值(图中uint表示无符号的int，即无符号4个字节的意思)，下图是010Editor中的效果，附上后一张图对每个字段做了解释：

[![](https://p4.ssl.qhimg.com/t013f441b1106ed94a2.png)](https://p4.ssl.qhimg.com/t013f441b1106ed94a2.png)

[![](https://p5.ssl.qhimg.com/t015e086b9565aede93.png)](https://p5.ssl.qhimg.com/t015e086b9565aede93.png)

在上图中，我把三个字段标出来了：<br>
checksum ：文件校验码 ，运用Adler32算法计算出来的一个值，用来校验文件是否被损坏 。<br>
signature ：使用 SHA-1 算法 hash 除去 magic ,checksum 和 signature 外余下的所有文件区域 ，用于唯一识别本文件 。<br>
file_size：Dex 文件的大小 。<br>
为什么标出这三个字段呢，因为当我们的源apk和壳程序的dex合并生成新的dex之后，这三个值肯定会发生改变，因为他们都是检验文件是否被改变的值，而在程序安装的时候会检验这些值是否正确，为了让程序正常运行，我们在将壳dex和源apk合并成dex之后，也要将新的dex的这三个值修改为正确的值。所有我们的新的dex结构就如下图这样(最后要加上源程序的apk的大小，当程序运行起来的时候壳程序会把源程序重新分离出来让他自己运行，这样才能确保程序的运行逻辑不被改变，分离源apk的时候就需要知道apk的大小才能完成分离)：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t013ca620f6b3cf4cf8.png)

### <a class="reference-link" name="%E5%8A%A8%E6%80%81%E5%8A%A0%E8%BD%BD%E6%9C%BA%E5%88%B6"></a>动态加载机制

为了避免篇幅过长，对于动态加载机制的详细过程，可以参考我的另一篇文章：[https://www.yuque.com/u2172011/abm9ei/fhf6fv](https://www.yuque.com/u2172011/abm9ei/fhf6fv)



## Apk加固原理

关于上述的两个问题，第一个：如何将源apk和壳程序的dex文件合并？<br>
我们已经找到答案了，即为Dex文件结构中最后一张图所示，需要改变checksum、signature、file_size值，并且需要在合并完最后加上加密的源程序的Apk大小。<br>
那么对于第二个问题：如何做到不改变源程序的逻辑？<br>
这就涉及到另一个技术：免安装运行程序<br>
因为我们知道我们的apk在运行之前是需要安装在手机上的，那么如果我们的源apk外面套上一个壳程序，安装的时候加载的就是壳程序的内容，那Android如何识别到源apk里面程序呢，这就涉及到一个apk没有安装是怎么运行的。<br>
要安装并运行apk，实际上就是加载里面的类并且运行类当中的方法的过程，既然如此，那就又回到了类加载的问题，我们安装的是壳程序的apk，那么加载的时候肯定是加载壳程序类，然后在壳程序当中我们做了把源apk分离出来的操作，但是分离出来的apk并不会重新被加载，因为加载的过程在壳程序安装运行的时候已经运行过了，所以不会运行第二次，那我们就需要自己去加载源apk中的类，我们知道PathClassLoader是一个应用的默认加载器(而且它只能加载data/app/xxx.apk的文件)，但是我们自己去加载类的时候一般使用DexClassLoader加载器，所以开始的时候，每个人都会很容易想到使用DexClassLoader来加载Activity获取到class对象，再使用Intent启动。但是实际上并不是想象的这么简单。因为Android中的四大组件都有一个特点就是他们有自己的启动流程和生命周期，我们使用DexClassLoader加载进来的Activity是不会涉及到任何启动流程和生命周期的概念，说白了，他就是一个普普通通的类。所以启动肯定会出错。<br>
所以我们这里就需要使用其他方式，只要让加载进来的Activity有启动流程和生命周期就行了，所以这里需要看一下一个Activity的启动过程，当然由于篇幅问题，这里不会详细介绍一个Activity启动过程的。可以将使用的DexClassLoader加载器绑定到系统加载Activity的类加载器上，这个是最重要的突破点。下面我们就来通过源码看看如何找到加载Activity的类加载器。<br>
ActivityThread.java

```
// set of instantiated backup agents, keyed by package name
    final ArrayMap&lt;String, BackupAgent&gt; mBackupAgents = new ArrayMap&lt;String, BackupAgent&gt;();
    /** Reference to singleton `{`@link ActivityThread`}` */
    private static volatile ActivityThread sCurrentActivityThread;
    Instrumentation mInstrumentation;
    String mInstrumentationPackageName = null;
    String mInstrumentationAppDir = null;
    String[] mInstrumentationSplitAppDirs = null;
    String mInstrumentationLibDir = null;
    String mInstrumentedAppDir = null;
    String[] mInstrumentedSplitAppDirs = null;
    String mInstrumentedLibDir = null;
    boolean mSystemThread = false;
    boolean mJitEnabled = false;
    boolean mSomeActivitiesChanged = false;

    // These can be accessed by multiple threads; mPackages is the lock.
    // XXX For now we keep around information about all packages we have
    // seen, not removing entries from this map.
    // NOTE: The activity and window managers need to call in to
    // ActivityThread to do things like update resource configurations,
    // which means this lock gets held while the activity and window managers
    // holds their own lock.  Thus you MUST NEVER call back into the activity manager
    // or window manager or anything that depends on them while holding this lock.
    // These LoadedApk are only valid for the userId that we're running as.
    final ArrayMap&lt;String, WeakReference&lt;LoadedApk&gt;&gt; mPackages
            = new ArrayMap&lt;String, WeakReference&lt;LoadedApk&gt;&gt;();
    final ArrayMap&lt;String, WeakReference&lt;LoadedApk&gt;&gt; mResourcePackages
            = new ArrayMap&lt;String, WeakReference&lt;LoadedApk&gt;&gt;();
    final ArrayList&lt;ActivityClientRecord&gt; mRelaunchingActivities
            = new ArrayList&lt;ActivityClientRecord&gt;();
    Configuration mPendingConfiguration = null;
```

我们看到ActivityThread类中有一个自己的static对象，然后还有一个ArrayMap存放Apk包名和LoadedApk映射关系的数据结构。LoadedApk.java是加载Activity的时候一个很重要的类，这个类是负责加载一个Apk程序的，我们可以看一下它的源码：<br>
LoadedApk.java

```
static final String TAG = "LoadedApk";
static final boolean DEBUG = false;

@UnsupportedAppUsage
private final ActivityThread mActivityThread;
@UnsupportedAppUsage
final String mPackageName;
@UnsupportedAppUsage
private ApplicationInfo mApplicationInfo;
@UnsupportedAppUsage
private String mAppDir;
@UnsupportedAppUsage
private String mResDir;
private String[] mOverlayDirs;
@UnsupportedAppUsage
private String mDataDir;
@UnsupportedAppUsage(maxTargetSdk = Build.VERSION_CODES.R, trackingBug = 170729553)
private String mLibDir;
@UnsupportedAppUsage(maxTargetSdk = Build.VERSION_CODES.P, trackingBug = 115609023)
private File mDataDirFile;
private File mDeviceProtectedDataDirFile;
private File mCredentialProtectedDataDirFile;
@UnsupportedAppUsage
private final ClassLoader mBaseClassLoader;
private ClassLoader mDefaultClassLoader;
private final boolean mSecurityViolation;
private final boolean mIncludeCode;
private final boolean mRegisterPackage;
@UnsupportedAppUsage
private final DisplayAdjustments mDisplayAdjustments = new DisplayAdjustments();
/** WARNING: This may change. Don't hold external references to it. */
@UnsupportedAppUsage
Resources mResources;
@UnsupportedAppUsage
private ClassLoader mClassLoader;
@UnsupportedAppUsage
private Application mApplication;

private String[] mSplitNames;
private String[] mSplitAppDirs;
@UnsupportedAppUsage
private String[] mSplitResDirs;
private String[] mSplitClassLoaderNames;

@UnsupportedAppUsage
private final ArrayMap&lt;Context, ArrayMap&lt;BroadcastReceiver, ReceiverDispatcher&gt;&gt; mReceivers
    = new ArrayMap&lt;&gt;();
private final ArrayMap&lt;Context, ArrayMap&lt;BroadcastReceiver, LoadedApk.ReceiverDispatcher&gt;&gt; mUnregisteredReceivers
    = new ArrayMap&lt;&gt;();
@UnsupportedAppUsage(maxTargetSdk = Build.VERSION_CODES.P, trackingBug = 115609023)
private final ArrayMap&lt;Context, ArrayMap&lt;ServiceConnection, LoadedApk.ServiceDispatcher&gt;&gt; mServices
    = new ArrayMap&lt;&gt;();
private final ArrayMap&lt;Context, ArrayMap&lt;ServiceConnection, LoadedApk.ServiceDispatcher&gt;&gt; mUnboundServices
    = new ArrayMap&lt;&gt;();
private AppComponentFactory mAppComponentFactory;

Application getApplication() `{`
    return mApplication;
`}`
```

我们可以看到它内部有一个mClassLoader变量，就是负责加载一个Apk程序的，所以只要通过反射获取到这个类加载器就可以加载我们壳程序解密出来的源apk了。



## 代码复现

### <a class="reference-link" name="%E6%BA%90apk"></a>源apk

MainActivity.java：

```
public class MainActivity extends Activity `{`

    @Override
    protected void onCreate(Bundle savedInstanceState) `{`
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        /*TextView textView = findViewById(R.id.text);
        textView.setText(this.toString());
        textView.setTextSize(22);
        textView.setGravity(Gravity.CENTER);*/
        Log.i("Source", String.valueOf(getClass()));
        Log.i("Source", "Source app: MainActivity is onCreate" + this);
    `}`
`}`
```

MyApplication.java：

```
public class MyApplication extends Application `{`
    @Override
    public void onCreate() `{`
        super.onCreate();
        Log.i("Source", "Source app:MyApplication is onCreate" + this);
    `}`
`}`
```

创建了一个application，在后面我们会用到他。

### <a class="reference-link" name="%E5%90%88%E5%B9%B6%E7%A8%8B%E5%BA%8F"></a>合并程序

该程序的作用将源apk和壳程序的dex文件合并成一个新的dex。所以也就是一个java项目，源代码如下：

```
import java.io.*;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.zip.Adler32;

public class ShellTool `{`
    public static void main(String[] args) `{`
        try `{`
            // 需要加壳的源APK  ，以二进制形式读出，并进行加密处理
            File srcApkFile = new File("files/SourceAPP.apk");
            System.out.println("apk size:" + srcApkFile.length());
            // 将源apk以二进制的形式进行读取到一个byte[]中，并且用encrpt()加密函数对其进行加密，然后保存在一个byte[]中
            byte[] enSrcApkArray = encrpt(readFileBytes(srcApkFile));

            // 需要解壳的dex，痛殴贵阳以二进制形式读出dex
            File unShellDexFile = new File("files/Pack.dex");
            byte[] unShellDexArray = readFileBytes(unShellDexFile);

            // 将源APK长度和壳程序的DEX长度相加并加上存放源APK大小的四位得到新dex的总长度，最后四位存放着源apk的长度
            int enSrcApkLen = enSrcApkArray.length;
            int unShellDexLen = unShellDexArray.length;
            int totalLen = enSrcApkLen + unShellDexLen + 4;

            // 依次将解壳DEX，加密后的源APK，加密后的源APK大小，拼接出新的Dex，注意顺序不能反
            byte[] newdex = new byte[totalLen];
            System.arraycopy(unShellDexArray, 0, newdex, 0, unShellDexLen);
            System.arraycopy(enSrcApkArray, 0, newdex, unShellDexLen, enSrcApkLen);
            System.arraycopy(intToByte(enSrcApkLen), 0, newdex, totalLen - 4, 4);


            // 修改DEX file_size文件头
            fixFileSizeHeader(newdex);
            // 修改DEX SHA1 文件头
            fixSHA1Header(newdex);
            // 修改DEX CheckSum文件头
            fixCheckSumHeader(newdex);

            // 写入新Dex
            // 新建一个File
            String str = "files/classes.dex";
            File file = new File(str);
            if (!file.exists()) `{`
                file.createNewFile();
            `}`
            // 将新的dex文件写入classes.dex中
            FileOutputStream localFileOutputStream = new FileOutputStream(str);
            localFileOutputStream.write(newdex);
            localFileOutputStream.flush();
            localFileOutputStream.close();


        `}` catch (Exception e) `{`
            e.printStackTrace();
        `}`
    `}`

    // 可以添加自己的加密方法
    private static byte[] encrpt(byte[] srcdata) `{`
        for (int i = 0; i &lt; srcdata.length; i++) `{`
            // 这里采用简单的apk的每个byte和0xFF异或一下
            srcdata[i] = (byte) (0xFF ^ srcdata[i]);
        `}`
        return srcdata;
    `}`

    /**
     * 修改dex头，CheckSum 校验码
     *
     * @param dexBytes
     */
    private static void fixCheckSumHeader(byte[] dexBytes) `{`
        Adler32 adler = new Adler32();
        // 从12到文件末尾计算校验码
        // 前8位是magic魔术符
        // 8到12位就是这个计算出来的结果CheckSum，这两着不参与计算
        adler.update(dexBytes, 12, dexBytes.length - 12);
        long value = adler.getValue();
        int va = (int) value;
        byte[] newcs = intToByte(va);
        //高位在前，低位在前掉个个
        byte[] recs = new byte[4];
        for (int i = 0; i &lt; 4; i++) `{`
            recs[i] = newcs[newcs.length - 1 - i];
            System.out.println(Integer.toHexString(newcs[i]));
        `}`
        System.arraycopy(recs, 0, dexBytes, 8, 4);//效验码赋值（8-12）
        System.out.println(Long.toHexString(value));
        System.out.println();
    `}`


    /**
     * int 转byte[]
     *
     * @param number
     * @return
     */
    public static byte[] intToByte(int number) `{`
        byte[] b = new byte[4];
        for (int i = 3; i &gt;= 0; i--) `{`
            b[i] = (byte) (number % 256);
            number &gt;&gt;= 8;
        `}`
        return b;
    `}`

    /**
     * 修改dex头 sha1值
     *
     * @param dexBytes
     * @throws NoSuchAlgorithmException
     */
    private static void fixSHA1Header(byte[] dexBytes)
            throws NoSuchAlgorithmException `{`
        MessageDigest md = MessageDigest.getInstance("SHA-1");
        md.update(dexBytes, 32, dexBytes.length - 32);// 从32为到结束计算sha--1，与上述同理，前32位不参与计算
        byte[] newdt = md.digest();
        System.arraycopy(newdt, 0, dexBytes, 12, 20);//修改sha-1值（12-31）
        //输出sha-1值，可有可无
        String hexstr = "";
        for (int i = 0; i &lt; newdt.length; i++) `{`
            hexstr += Integer.toString((newdt[i] &amp; 0xff) + 0x100, 16)
                    .substring(1);
        `}`
        System.out.println(hexstr);
    `}`

    /**
     * 修改dex头 file_size值
     *
     * @param dexBytes
     */
    private static void fixFileSizeHeader(byte[] dexBytes) `{`
        //新文件长度
        byte[] newfs = intToByte(dexBytes.length);
        System.out.println(Integer.toHexString(dexBytes.length));
        byte[] refs = new byte[4];
        //高位在前，低位在前掉个个
        for (int i = 0; i &lt; 4; i++) `{`
            refs[i] = newfs[newfs.length - 1 - i];
            System.out.println(Integer.toHexString(newfs[i]));
        `}`
        System.arraycopy(refs, 0, dexBytes, 32, 4);//修改（32-35）
    `}`

    /**
     * 以二进制读出文件内容
     *
     * @param file
     * @return
     * @throws IOException
     */
    private static byte[] readFileBytes(File file) throws IOException `{`
        byte[] arrayOfByte = new byte[1024];
        ByteArrayOutputStream localByteArrayOutputStream = new ByteArrayOutputStream();
        FileInputStream fis = new FileInputStream(file);
        while (true) `{`
            int i = fis.read(arrayOfByte);
            if (i != -1) `{`
                localByteArrayOutputStream.write(arrayOfByte, 0, i);
            `}` else `{`
                return localByteArrayOutputStream.toByteArray();
            `}`
        `}`
    `}`
`}`
```

[![](https://p0.ssl.qhimg.com/t0128d8b8b56d1865c7.png)](https://p0.ssl.qhimg.com/t0128d8b8b56d1865c7.png)

将源程序的apk和壳程序的dex文件放在file文件夹下，然后运行，就会生成新的classes.dex文件，这就是合并之后的dex。

### <a class="reference-link" name="%E5%A3%B3%E7%A8%8B%E5%BA%8F"></a>壳程序

目录结构：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0150f67696d27d4728.png)

ProxyApplication.java：代理程序，执行壳程序的主要逻辑。

```
public class ProxyApplication extends Application `{`
    private static final String appkey = "APPLICATION_CLASS_NAME";
    private String apkFileName;
    private String odexPath;
    private String libPath;

    // 这是context赋值
    @Override
    protected void attachBaseContext(Context base) `{`
        super.attachBaseContext(base);
        try `{`
            // 创建两个文件夹payload_odex、payload_lib，私有的，可写的文件目录
            File odex = this.getDir("payload_odex", MODE_PRIVATE);
            File libs = this.getDir("payload_lib", MODE_PRIVATE);
            odexPath = odex.getAbsolutePath();
            libPath = libs.getAbsolutePath();
            apkFileName = odex.getAbsolutePath() + "/payload.apk";
            Log.i("demo", "odexPath:" + odexPath);
            Log.i("demo", "libPath:" + libPath);
            File dexFile = new File(apkFileName);
            if (!dexFile.exists()) `{`
                dexFile.createNewFile();  //在payload_odex文件夹内，创建payload.apk
                // 读取程序classes.dex文件
                byte[] dexdata = this.readDexFileFromApk();

                // 分离出解壳后的apk文件已用于动态加载
                this.splitPayLoadFromDex(dexdata);
            `}`
            Log.i("demo", "apk size:" + dexFile.length());
            // 配置动态加载环境
            Object currentActivityThread = RefInvoke.invokeStaticMethod(
                    "android.app.ActivityThread", "currentActivityThread",
                    new Class[]`{``}`, new Object[]`{``}`);//获取主线程对象
            String packageName = this.getPackageName();//当前apk的包名
            Log.i("demo", "packageName:" + packageName);
            ArrayMap mPackages = null;
            if (android.os.Build.VERSION.SDK_INT &gt;= android.os.Build.VERSION_CODES.KITKAT) `{`
                mPackages = (ArrayMap) RefInvoke.getFieldOjbect(
                        "android.app.ActivityThread", currentActivityThread,
                        "mPackages");
            `}`
            WeakReference wr = (WeakReference) mPackages.get(packageName);
            // 创建被加壳apk的DexClassLoader对象  加载apk内的类和本地代码（c/c++代码）
            DexClassLoader dLoader = new DexClassLoader(apkFileName, odexPath,
                    libPath, (ClassLoader) RefInvoke.getFieldOjbect(
                    "android.app.LoadedApk", wr.get(), "mClassLoader"));
            //把当前进程的mClassLoader设置成了被加壳apk的DexClassLoader
            RefInvoke.setFieldOjbect("android.app.LoadedApk", "mClassLoader",
                    wr.get(), dLoader);

            Log.i("demo", "classloader:" + dLoader);

            try `{`
                Object actObj = dLoader.loadClass("com.zero.sourceapp.MainActivity");
                Log.i("demo", "actObj:" + actObj);
            `}` catch (Exception e) `{`
                Log.i("demo", "activity:" + Log.getStackTraceString(e));
            `}`


        `}` catch (Exception e) `{`
            Log.i("demo", "error:" + Log.getStackTraceString(e));
            e.printStackTrace();
        `}`
    `}`

    @Override
    public void onCreate() `{`
        super.onCreate();
        `{`
            // 加载资源
            loadResources(apkFileName);
            Log.i("demo", "onCreate");
            // 如果源应用配置有Appliction对象，则替换为源应用Applicaiton，以便不影响源程序逻辑。
            String appClassName = null;
            try `{`
                ApplicationInfo ai = this.getPackageManager()
                        .getApplicationInfo(this.getPackageName(),
                                PackageManager.GET_META_DATA);
                Bundle bundle = ai.metaData;
                if (bundle != null &amp;&amp; bundle.containsKey(appkey)) `{`
                    appClassName = bundle.getString(appkey); // className 是配置在xml文件中的。
                    Log.i("demo", "application class name:" + appClassName);
                `}` else `{`
                    Log.i("demo", "have no application class name");
                    return;
                `}`
            `}` catch (PackageManager.NameNotFoundException e) `{`
                Log.i("demo", "error:" + Log.getStackTraceString(e));
                e.printStackTrace();
            `}`
            //有值的话调用该Applicaiton
            Object currentActivityThread = RefInvoke.invokeStaticMethod(
                    "android.app.ActivityThread", "currentActivityThread",
                    new Class[]`{``}`, new Object[]`{``}`);
            Object mBoundApplication = RefInvoke.getFieldOjbect(
                    "android.app.ActivityThread", currentActivityThread,
                    "mBoundApplication");
            Object loadedApkInfo = RefInvoke.getFieldOjbect(
                    "android.app.ActivityThread$AppBindData",
                    mBoundApplication, "info");
            //把当前进程的mApplication 设置成了null
            RefInvoke.setFieldOjbect("android.app.LoadedApk", "mApplication",
                    loadedApkInfo, null);
            Object oldApplication = RefInvoke.getFieldOjbect(
                    "android.app.ActivityThread", currentActivityThread,
                    "mInitialApplication");
            ArrayList&lt;Application&gt; mAllApplications = (ArrayList&lt;Application&gt;) RefInvoke
                    .getFieldOjbect("android.app.ActivityThread",
                            currentActivityThread, "mAllApplications");
            mAllApplications.remove(oldApplication); // 删除oldApplication

            ApplicationInfo appinfo_In_LoadedApk = (ApplicationInfo) RefInvoke
                    .getFieldOjbect("android.app.LoadedApk", loadedApkInfo,
                            "mApplicationInfo");
            ApplicationInfo appinfo_In_AppBindData = (ApplicationInfo) RefInvoke
                    .getFieldOjbect("android.app.ActivityThread$AppBindData",
                            mBoundApplication, "appInfo");
            appinfo_In_LoadedApk.className = appClassName;
            appinfo_In_AppBindData.className = appClassName;
            Application app = (Application) RefInvoke.invokeMethod(
                    "android.app.LoadedApk", "makeApplication", loadedApkInfo,
                    new Class[]`{`boolean.class, Instrumentation.class`}`,
                    new Object[]`{`false, null`}`); // 执行 makeApplication（false,null）
            RefInvoke.setFieldOjbect("android.app.ActivityThread",
                    "mInitialApplication", currentActivityThread, app);

            ArrayMap mProviderMap = null;
            if (Build.VERSION.SDK_INT &gt;= Build.VERSION_CODES.KITKAT) `{`
                mProviderMap = (ArrayMap) RefInvoke.getFieldOjbect(
                        "android.app.ActivityThread", currentActivityThread,
                        "mProviderMap");
            `}`
            Iterator it = mProviderMap.values().iterator();
            while (it.hasNext()) `{`
                Object providerClientRecord = it.next();
                Object localProvider = RefInvoke.getFieldOjbect(
                        "android.app.ActivityThread$ProviderClientRecord",
                        providerClientRecord, "mLocalProvider");
                RefInvoke.setFieldOjbect("android.content.ContentProvider",
                        "mContext", localProvider, app);
            `}`

            Log.i("demo", "app:" + app);
            app.onCreate();
        `}`
    `}`

    /**
     * 释放被加壳的apk文件，so文件
     *
     * @param apkdata
     * @throws IOException
     */
    private void splitPayLoadFromDex(byte[] apkdata) throws IOException `{`
        int ablen = apkdata.length;
        //取被加壳apk的长度   这里的长度取值，对应加壳时长度的赋值都可以做些简化
        byte[] dexlen = new byte[4];
        System.arraycopy(apkdata, ablen - 4, dexlen, 0, 4);
        ByteArrayInputStream bais = new ByteArrayInputStream(dexlen);
        DataInputStream in = new DataInputStream(bais);
        int readInt = in.readInt();
        System.out.println(Integer.toHexString(readInt));
        byte[] newdex = new byte[readInt];
        //把被加壳的源程序apk内容拷贝到newdex中
        System.arraycopy(apkdata, ablen - 4 - readInt, newdex, 0, readInt);
        //这里应该加上对于apk的解密操作，若加壳是加密处理的话

        // 对源程序Apk进行解密
        newdex = decrypt(newdex);

        // 写入apk文件
        File file = new File(apkFileName);
        try `{`
            FileOutputStream localFileOutputStream = new FileOutputStream(file);
            localFileOutputStream.write(newdex);
            localFileOutputStream.close();
        `}` catch (IOException localIOException) `{`
            throw new RuntimeException(localIOException);
        `}`

        // 分析被加壳的apk文件
        ZipInputStream localZipInputStream = new ZipInputStream(
                new BufferedInputStream(new FileInputStream(file)));
        while (true) `{`
            ZipEntry localZipEntry = localZipInputStream.getNextEntry(); // 这个也遍历子目录
            if (localZipEntry == null) `{`
                localZipInputStream.close();
                break;
            `}`
            // 取出被加壳apk用到的so文件，放到libPath中（data/data/包名/payload_lib)
            String name = localZipEntry.getName();
            if (name.startsWith("lib/") &amp;&amp; name.endsWith(".so")) `{`
                File storeFile = new File(libPath + "/"
                        + name.substring(name.lastIndexOf('/')));
                storeFile.createNewFile();
                FileOutputStream fos = new FileOutputStream(storeFile);
                byte[] arrayOfByte = new byte[1024];
                while (true) `{`
                    int i = localZipInputStream.read(arrayOfByte);
                    if (i == -1)
                        break;
                    fos.write(arrayOfByte, 0, i);
                `}`
                fos.flush();
                fos.close();
            `}`
            localZipInputStream.closeEntry();
        `}`
        localZipInputStream.close();
    `}`

    /**
     * 从apk包里面获取dex文件内容（byte）
     *
     * @return
     * @throws IOException
     */
    private byte[] readDexFileFromApk() throws IOException `{`
        ByteArrayOutputStream dexByteArrayOutputStream = new ByteArrayOutputStream();
        ZipInputStream localZipInputStream = new ZipInputStream(
                new BufferedInputStream(new FileInputStream(
                        this.getApplicationInfo().sourceDir)));
        while (true) `{`
            ZipEntry localZipEntry = localZipInputStream.getNextEntry();
            if (localZipEntry == null) `{`
                localZipInputStream.close();
                break;
            `}`
            if (localZipEntry.getName().equals("classes.dex")) `{`
                byte[] arrayOfByte = new byte[1024];
                while (true) `{`
                    int i = localZipInputStream.read(arrayOfByte);
                    if (i == -1)
                        break;
                    dexByteArrayOutputStream.write(arrayOfByte, 0, i);
                `}`
            `}`
            localZipInputStream.closeEntry();
        `}`
        localZipInputStream.close();
        return dexByteArrayOutputStream.toByteArray();
    `}`


    //直接返回数据，读者可以添加自己解密方法
    private byte[] decrypt(byte[] srcdata) `{`
        for (int i = 0; i &lt; srcdata.length; i++) `{`
            srcdata[i] = (byte) (0xFF ^ srcdata[i]);
        `}`
        return srcdata;
    `}`


    //以下是加载资源
    protected AssetManager mAssetManager;//资源管理器
    protected Resources mResources;//资源
    protected Resources.Theme mTheme;//主题

    protected void loadResources(String dexPath) `{`
        try `{`
            AssetManager assetManager = AssetManager.class.newInstance();
            Method addAssetPath = assetManager.getClass().getMethod("addAssetPath", String.class);
            addAssetPath.invoke(assetManager, dexPath);
            mAssetManager = assetManager;
        `}` catch (Exception e) `{`
            Log.i("inject", "loadResource error:" + Log.getStackTraceString(e));
            e.printStackTrace();
        `}`
        Resources superRes = super.getResources();
        superRes.getDisplayMetrics();
        superRes.getConfiguration();
        mResources = new Resources(mAssetManager, superRes.getDisplayMetrics(), superRes.getConfiguration());
        mTheme = mResources.newTheme();
        mTheme.setTo(super.getTheme());
    `}`

    @Override
    public AssetManager getAssets() `{`
        return mAssetManager == null ? super.getAssets() : mAssetManager;
    `}`

    @Override
    public Resources getResources() `{`
        return mResources == null ? super.getResources() : mResources;
    `}`

    @Override
    public Resources.Theme getTheme() `{`
        return mTheme == null ? super.getTheme() : mTheme;
    `}`

`}`
```

RefInvoke.java：反射工具类

```
public class RefInvoke `{`
    /**
     * 反射执行类的静态函数(public)
     *
     * @param class_name  类名
     * @param method_name 函数名
     * @param pareTyple   函数的参数类型
     * @param pareVaules  调用函数时传入的参数
     * @return
     */
    public static Object invokeStaticMethod(String class_name, String method_name, Class[] pareTyple, Object[] pareVaules) `{`

        try `{`
            Class obj_class = Class.forName(class_name);
            Method method = obj_class.getMethod(method_name, pareTyple);
            return method.invoke(null, pareVaules);
        `}` catch (SecurityException e) `{`
            // TODO Auto-generated catch block
            e.printStackTrace();
        `}` catch (IllegalArgumentException e) `{`
            // TODO Auto-generated catch block
            e.printStackTrace();
        `}` catch (IllegalAccessException e) `{`
            // TODO Auto-generated catch block
            e.printStackTrace();
        `}` catch (NoSuchMethodException e) `{`
            // TODO Auto-generated catch block
            e.printStackTrace();
        `}` catch (InvocationTargetException e) `{`
            // TODO Auto-generated catch block
            e.printStackTrace();
        `}` catch (ClassNotFoundException e) `{`
            // TODO Auto-generated catch block
            e.printStackTrace();
        `}`
        return null;

    `}`

    /**
     * 反射执行类的函数（public）
     *
     * @param class_name
     * @param method_name
     * @param obj
     * @param pareTyple
     * @param pareVaules
     * @return
     */
    public static Object invokeMethod(String class_name, String method_name, Object obj, Class[] pareTyple, Object[] pareVaules) `{`

        try `{`
            Class obj_class = Class.forName(class_name);
            Method method = obj_class.getMethod(method_name, pareTyple);
            return method.invoke(obj, pareVaules);
        `}` catch (SecurityException e) `{`
            // TODO Auto-generated catch block
            e.printStackTrace();
        `}` catch (IllegalArgumentException e) `{`
            // TODO Auto-generated catch block
            e.printStackTrace();
        `}` catch (IllegalAccessException e) `{`
            // TODO Auto-generated catch block
            e.printStackTrace();
        `}` catch (NoSuchMethodException e) `{`
            // TODO Auto-generated catch block
            e.printStackTrace();
        `}` catch (InvocationTargetException e) `{`
            // TODO Auto-generated catch block
            e.printStackTrace();
        `}` catch (ClassNotFoundException e) `{`
            // TODO Auto-generated catch block
            e.printStackTrace();
        `}`
        return null;

    `}`

    /**
     * 反射得到类的属性（包括私有和保护）
     *
     * @param class_name
     * @param obj
     * @param filedName
     * @return
     */
    public static Object getFieldOjbect(String class_name, Object obj, String filedName) `{`
        try `{`
            Class obj_class = Class.forName(class_name);
            Field field = obj_class.getDeclaredField(filedName);
            field.setAccessible(true);
            return field.get(obj);
        `}` catch (SecurityException e) `{`
            // TODO Auto-generated catch block
            e.printStackTrace();
        `}` catch (NoSuchFieldException e) `{`
            // TODO Auto-generated catch block
            e.printStackTrace();
        `}` catch (IllegalArgumentException e) `{`
            // TODO Auto-generated catch block
            e.printStackTrace();
        `}` catch (IllegalAccessException e) `{`
            // TODO Auto-generated catch block
            e.printStackTrace();
        `}` catch (ClassNotFoundException e) `{`
            // TODO Auto-generated catch block
            e.printStackTrace();
        `}`
        return null;

    `}`

    /**
     * 反射得到类的静态属性（包括私有和保护）
     *
     * @param class_name
     * @param filedName
     * @return
     */
    public static Object getStaticFieldOjbect(String class_name, String filedName) `{`

        try `{`
            Class obj_class = Class.forName(class_name);
            Field field = obj_class.getDeclaredField(filedName);
            field.setAccessible(true);
            return field.get(null);
        `}` catch (SecurityException e) `{`
            // TODO Auto-generated catch block
            e.printStackTrace();
        `}` catch (NoSuchFieldException e) `{`
            // TODO Auto-generated catch block
            e.printStackTrace();
        `}` catch (IllegalArgumentException e) `{`
            // TODO Auto-generated catch block
            e.printStackTrace();
        `}` catch (IllegalAccessException e) `{`
            // TODO Auto-generated catch block
            e.printStackTrace();
        `}` catch (ClassNotFoundException e) `{`
            // TODO Auto-generated catch block
            e.printStackTrace();
        `}`
        return null;

    `}`

    /**
     * 设置类的属性（包括私有和保护）
     *
     * @param classname
     * @param filedName
     * @param obj
     * @param filedVaule
     */
    public static void setFieldOjbect(String classname, String filedName, Object obj, Object filedVaule) `{`
        try `{`
            Class obj_class = Class.forName(classname);
            Field field = obj_class.getDeclaredField(filedName);
            field.setAccessible(true);
            field.set(obj, filedVaule);
        `}` catch (SecurityException e) `{`
            // TODO Auto-generated catch block
            e.printStackTrace();
        `}` catch (NoSuchFieldException e) `{`
            // TODO Auto-generated catch block
            e.printStackTrace();
        `}` catch (IllegalArgumentException e) `{`
            // TODO Auto-generated catch block
            e.printStackTrace();
        `}` catch (IllegalAccessException e) `{`
            // TODO Auto-generated catch block
            e.printStackTrace();
        `}` catch (ClassNotFoundException e) `{`
            // TODO Auto-generated catch block
            e.printStackTrace();
        `}`
    `}`

    /**
     * 设置类的静态属性（包括私有和保护）
     *
     * @param class_name
     * @param filedName
     * @param filedVaule
     */
    public static void setStaticOjbect(String class_name, String filedName, Object filedVaule) `{`
        try `{`
            Class obj_class = Class.forName(class_name);
            Field field = obj_class.getDeclaredField(filedName);
            field.setAccessible(true);
            field.set(null, filedVaule);
        `}` catch (SecurityException e) `{`
            // TODO Auto-generated catch block
            e.printStackTrace();
        `}` catch (NoSuchFieldException e) `{`
            // TODO Auto-generated catch block
            e.printStackTrace();
        `}` catch (IllegalArgumentException e) `{`
            // TODO Auto-generated catch block
            e.printStackTrace();
        `}` catch (IllegalAccessException e) `{`
            // TODO Auto-generated catch block
            e.printStackTrace();
        `}` catch (ClassNotFoundException e) `{`
            // TODO Auto-generated catch block
            e.printStackTrace();
        `}`
    `}`

`}`
```

AndroidMenifest.xml

```
&lt;?xml version="1.0" encoding="utf-8"?&gt;
&lt;manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.zero.shellapp"&gt;

    &lt;application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.ShellApp"
        android:name="com.zero.shellapp.ProxyApplication"&gt;
        &lt;meta-data android:name="APPLICATION_CLASS_NAME" android:value="com.zero.sourceapp.MyApplication"/&gt;
        &lt;activity android:name="com.zero.sourceapp.MainActivity"&gt;
            &lt;intent-filter&gt;
                &lt;action android:name="android.intent.action.MAIN" /&gt;

                &lt;category android:name="android.intent.category.LAUNCHER" /&gt;
            &lt;/intent-filter&gt;
        &lt;/activity&gt;
    &lt;/application&gt;

&lt;/manifest&gt;
```

接下来对这个壳程序做一个详细的解释。<br>
首先是对分离源apk的时机的选择，就是在脱壳程序还没有运行起来的时候，来加载源程序的Apk，执行他的onCreate方法，那么这个时机不能太晚，不然的话，就是运行脱壳程序，而不是源程序了。查看源码我们知道。Application中有一个方法：attachBaseContext这个方法，他在Application的onCreate方法执行前就会执行了，那么我们的工作就需要在这里进行。<br>
在attachBaseContext中，我们先创建两个文件夹，用来存放分离出来的dex和lib库文件并把分离出来的apk写入payload.apk中，这些目录都要求有可写权限。

[![](https://p3.ssl.qhimg.com/t01953fea72580cba5e.png)](https://p3.ssl.qhimg.com/t01953fea72580cba5e.png)

从整个apk中获取dex文件

[![](https://p2.ssl.qhimg.com/t0111828e60c7646e6e.png)](https://p2.ssl.qhimg.com/t0111828e60c7646e6e.png)

从上述的dex文件中分离出源apk文件：先将我们保存在最后四个字节的源apk的大小读出来赋值给dexlen，然后通过I/O函数，从dex文件最后往前选dexlen大小个byte放在newdex里面，这个就是我们读到的源apk，然后就需要对其解密，保证其正常运行，然后需要分析这个apk，如果有的话，把里面的lib库文件取出来单独保存，方便其运行。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t012d1b80d0150fc5d6.png)

解密源apk，和加密的函数对应即可

[![](https://p1.ssl.qhimg.com/t01fbd51ce771a132d0.png)](https://p1.ssl.qhimg.com/t01fbd51ce771a132d0.png)

得到源apk之后，我们接下来的任务就是让他跑起来，我们在前面提到如果要让activity具有完整的生命周期，就需要去替换LoadedApk中的mClassLoader，这里就需要用到反射的技术，通过查看源码，首先我们反射ActivityThread类可以发现currentActivityThread()函数会返回一个静态的ActivityThread类对象，我们就反射获取该对象，然后运用该对象去得到ActivityThread类中的属性mPackages，然后获得当前包名，然后利用包名去获得LoadedApk中的mClassLoader，用这个类加载器作为parent创建一个DexClassLoader，然后用自己创建的DexClassLoader替换掉系统中的mClassLoader(由于ArrayMap是高版本Android引入的，低版本没有，所以代码里做了版本判断)。

```
private static volatile ActivityThread sCurrentActivityThread;
public static ActivityThread currentActivityThread() `{`
        return sCurrentActivityThread;
    `}`
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016d6626166aa109e5.png)

我们已经获得了加载源程序的类加载器，然后由于源apk中有自定义application，所以我们在onCreate()方法中要找到源程序的application，让他运行起来才可以。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01193b8f3c395634a3.png)

先从AndroidMenifest.xml中获取application值(源apk的application和activity要在AndroidMenifest.xml里注册)，获取到如果有的话就需要替换系统的application为源apk中的的application。<br>
首先我们还是要获得ActivityThread对象，然后运用反射获得他的内部类AppBindData的对象，然后获得AppBindData当中的LoadedApk属性值Info。

```
static final class AppBindData `{`
        LoadedApk info;
        String processName;
        ApplicationInfo appInfo;
        List&lt;ProviderInfo&gt; providers;
        ComponentName instrumentationName;
        Bundle instrumentationArgs;
        IInstrumentationWatcher instrumentationWatcher;
        IUiAutomationConnection instrumentationUiAutomationConnection;
        int debugMode;
        boolean enableBinderTracking;
        boolean trackAllocation;
        boolean restrictedBackupMode;
        boolean persistent;
        Configuration config;
        CompatibilityInfo compatInfo;

        /** Initial values for `{`@link Profiler`}`. */
        ProfilerInfo initProfilerInfo;

        public String toString() `{`
            return "AppBindData`{`appInfo=" + appInfo + "`}`";
        `}`
    `}`
```

[![](https://p3.ssl.qhimg.com/t017459a183a85b04cc.png)](https://p3.ssl.qhimg.com/t017459a183a85b04cc.png)

查看android.app.LoadedApk源代码，发现创建Application的makeApplication方法，如果缓存mApplication不为空，则直接返回。mApplication为空时，则创建RealApplication，并且执行相关的回调。创建RealApplication时，类名是从mApplicationInfo.className中获取。添加新创建RealApplication到mActivityThread.mAllApplications。赋值给缓存mApplication。所以我们在调用makeApplication之前，需要将mApplication置为null，否则会直接返回ProxyApplication的实例。<br>
所以在我们的代码中，通过ActivityThread实例，获得LoadedApk实例。为了使makeApplication顺利执行，先设置mApplication为null。移除mAllApplications中ProxyApplication的实例。LoadedApk中mApplicationInfo和AppBindData中appInfo都是ApplicationInfo类型，需要分别替换className字段的值为RealApplication的实际类全名。之后，反射调用系统的makeApplication()，这样就完成了替换。<br>
通过阅读系统的源代码，可以很容易的知道，Application和ContentProvider的初始化顺序是：Application.attachBaseContext -&gt; ContentProvider.onCreate -&gt; Application.onCreate<br>
所以最后我们话需要通过反射去修改mContext的值，程序才可以正常运行。<br>
最后是资源管理问题：通过阅读源码可以发现，资源是由AssetManager管理的，所以我们只需要在addAssetPath方法中，将资源加载的路径改为源apk的路径即可。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012f7812e4c1fd8aa5.png)



## 复现结果

源程序运行的结果：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0117c0443f2d52bb74.png)

加固后程序运行结果：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0128f796c9c8f32f88.png)

我们可以发现加固之后的程序还是可以照常运行的。<br>
接下来哦我们看一下反编译的结果：<br>
源程序：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0170a43555c45fe76d.png)

加固之后的程序：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t017b163a1595819855.png)

通过对比，我们发现加固之后只会反编译出壳程序的代码，不会反编译出源apk的代码。
