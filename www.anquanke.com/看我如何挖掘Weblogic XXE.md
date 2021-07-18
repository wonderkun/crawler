
# 看我如何挖掘Weblogic XXE


                                阅读量   
                                **741271**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](./img/199703/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/199703/t011d12592d05b006bb.png)](./img/199703/t011d12592d05b006bb.png)



## 1、目标选择

去年暑期在tx某实验室实习，leader给的任务就是挖掘web服务器漏洞，最近研究weblogic服务器内容比较多，遂选择它了。



## 2、研究方向

当时weblogic爆出的最新的洞是2725那个RCE，想着能否找个RCE出来，看weblogic补丁历史，RCE思路有俩个：1、是寻找新的gadgets。2、weblogic支持的协议比较多，可能存在反序列化RCE的问题。第一个思路挖掘有点难，所以选择了第二个方向，审计基于RMI的JMX服务，weblogic默认会注册一些MBean，如果这些MBean中存在危险代码，外部还可以访问，第一个思路就是审计weblogic中默认注册的MBean中的代码，是否存在危险代码。第二个思路就是像上面weblogic默认注册的MBean对象篡改它的参数为gadget,如果存在JEP 290这样的防御机制，可以通过Asap hook bypass。然而当写出hook bypass工具时，实际问题来了想操纵MBean，前提需要知道管理员的用户名和密码，即使RCE危害也不大。（当时看到了rmi-iiop协议，没深入研究，后面就有人在这块曝洞了。。。



## 3、柳暗花明

工作陷入僵局，想着RCE是不可能了，挖掘XXE看看能挖到不。当时爆出反序列化XXE的CVE:CVE-2019-2647、CVE-2019-2648、CVE-2019-2649、CVE-2019-2650，直接感觉还有XXE，人工审计太麻烦了，写一款辅助审计的工具。工具思路比较简单就是正则匹配XML解析的库和实现了序列化接口的类都打印出来，人工审计反序列操作有没有问题就可以了。第一个问题weblogic的jar包都是字节码文件需要还原成XXX.java。可以通过jd-gui来还原。下面把源码给出来：

```
package Search;

import java.io.*;
import java.net.URL;
import java.util.regex.Pattern;

public class JarFileReader {
    public static void Test(String jarName,String classname) throws IOException {
        URL url1 = new URL("jar:file:"+jarName.replaceAll("\\","/")+"!"+classname);
        URL url2 = new URL("jar:file:"+jarName.replaceAll("\\","/")+"!"+classname);
// 标准输入流
        try {
            InputStream is1 = url1.openStream();
            InputStream is2 = url2.openStream();
            if (processEvilPackage(is1)&amp;&amp;processReadObject(is2)) {
                System.out.println(classname + "       this class maybe have XXE!!!!!!!!!");
            }
        }catch (Exception e)
        {
            System.out.println(classname + "  java.io.FileNotFoundException");
        }
    }

    private static boolean processEvilPackage(InputStream input) throws IOException {
        InputStreamReader isr = new InputStreamReader(input);
        BufferedReader reader = new BufferedReader(isr);
        String line;
        //遍历查找库
        while ((line = reader.readLine()) != null) {
//            System.out.println(line);
              if (SearchEvilPackage(line))
              {
                    return true;
              }
        }
        reader.close();
        return false;
    }
    private static boolean processReadObject(InputStream input) throws IOException {
        InputStreamReader isr = new InputStreamReader(input);
        BufferedReader reader = new BufferedReader(isr);
        String line;
        //遍历查找库
        while ((line = reader.readLine()) != null) {
//            System.out.println(line);
            if (SearchReadObject(line))
            {
                return true;
            }
        }
        reader.close();
        return false;
    }
    private static boolean SearchEvilPackage(String line)
    {
        //表达式
        String XXE_Regex = ".*javax.xml.parsers.DocumentBuilderFactory.*|.*javax.xml.parsers.SAXParser.*|.*javax.xml.transform.TransformerFactory.*|.*javax.xml.validation.Validator.*|.*javax.xml.validation.SchemaFactory.*|.*javax.xml.transform.sax.SAXValidator.*|.*javax.xml.transform.sax.SAXSource.*|.*org.xml.sax.XMLReader.*|.*org.xml.sax.helpers.XMLReaderFactory.*|.*org.dom4j.io.SAXReader.*|.*org.jdom.input.SAXBuilder.*|.*org.jdom2.input.SAXBuilder.*|.*javax.xml.bind.Unmarshaller.*|.*javax.xml.xpath.XpathExpression.*|.*javax.xml.stream.XMLStreamReader.*|.*org.apache.commons.digester3.Digester.*|.*javax.xml.transform.stream.StreamSource.*|.*javax.xml.parsers.SAXParserFactory.*|.*javax.xml.ws.EndpointReference.*";
        boolean b = Pattern.matches(XXE_Regex, line);
        if(b){
            return true;
        }else
        {
            return false;
        }
    }
    private static boolean SearchReadObject(String line)
    {
        //表达式
        String Ser_Regex = ".*Externalizable.*|.*Serializable.*|.*readObject.*|.*readExternal.*";
        boolean b = Pattern.matches(Ser_Regex, line);
        if(b){
            return true;
        }else
        {
            return false;
        }
    }
}
```

```
package Search;

import java.io.File;
import java.util.Enumeration;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;
import java.util.regex.Pattern;

public class SearchClassInJar {
    private String className;
    private String className_temp;
    private String className_final;
    private String jarDir;
    private Integer totalNum =  0;
    public SearchClassInJar(String className,String jarDir) {
        this.className = className;
        this.jarDir = jarDir;
    }
    //将jar中的类文件路径形式改为包路径形式
    protected String getClassName(ZipEntry entry) {
        StringBuffer className = new StringBuffer(entry.getName().replace('/','.'));
        return className.toString();
    }
    // 从jar从搜索目标类
    public void searchClass(boolean recurse) {
        searchDir(this.jarDir, recurse);
        System.out.println(String.format("[!] Find %s classes",this.totalNum));
        System.out.println();
    }
    //递归搜索目录和子目录下所有jar和zip文件
    protected void searchDir(String dir, boolean recurse) {
        try {
            File d = new File(dir);
            if (!d.isDirectory()) {
                return;
            }
            File[] files = d.listFiles();
            for (int i = 0; i &lt; files.length; i++) {
                if (recurse &amp;&amp; files[i].isDirectory()) {
                    searchDir(files[i].getAbsolutePath(), true);
                } else {
                    String filename = files[i].getAbsolutePath();
                    if (filename.endsWith(".jar")||filename.endsWith(".zip")) {
                        System.out.println("---------------------扫描"+filename+"中----------------------------");
                        ZipFile zip = new ZipFile(filename);
                        Enumeration entries = zip.entries();
                        while (entries.hasMoreElements()) {
                            ZipEntry entry = (ZipEntry) entries.nextElement();
                            String thisClassName = getClassName(entry);
                            if (wildcardEquals(this.className.toLowerCase(),thisClassName.toLowerCase()) || wildcardEquals(this.className.toLowerCase() + ".class",thisClassName.toLowerCase())) {
                                JarFileReader jarFileReader = new JarFileReader();
                                className_temp = "/"+thisClassName.replaceAll("\.","/");
                                className_final = className_temp.substring(0,className_temp.length()-5)+".java";
                                jarFileReader.Test(filename,className_final);
                                totalNum++;
                            }
                        }
                    }
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    //通配符匹配
    private boolean wildcardEquals(String wildcard, String str) {
        String regRule = WildcardToReg(wildcard);
        return Pattern.compile(regRule).matcher(str).matches();
    }
    //将通配符转换为正则表达式
    private static String WildcardToReg(String path) {
        char[] chars = path.toCharArray();
        int len = chars.length;
        StringBuilder sb = new StringBuilder();
        boolean preX = false;
        for(int i=0;i&lt;len;i++){
            if (chars[i] == '*'){
                if (preX){
                    sb.append(".*");
                    preX = false;
                }else if(i+1 == len){
                    sb.append("[^/]*");
                }else{
                    preX = true;
                    continue;
                }
            }else{
                if (preX){
                    sb.append("[^/]*");
                    preX = false;
                }
                if (chars[i] == '?'){
                    sb.append('.');
                }else{
                    sb.append(chars[i]);
                }
            }
        }
        return sb.toString();
    }
    public static void main(String args[]) {
        SearchClassInJar scij = new SearchClassInJar(args[0],args[1]);
        //args[0]写 *.java
        //args[1]写 C:UsersxxxxxDesktopctf-toolsjd-guiweblogic（反编译好的weblogic.jar路径）
        scij.searchClass(true);
    }
}
```

看下扫描结果，CVE-2019-2647、CVE-2019-2648、CVE-2019-2649、CVE-2019-2650这几类都匹配出来了，还额外找到EJBTaglibDescriptor这个类在反序列化时也存在XXE。POC构造看：[https://paper.seebug.org/1067/](https://paper.seebug.org/1067/)

[![](./img/199703/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t018cb6ec042ab2cf7a.jpg)



## 4、漏洞分析

提交这个洞后，orcle那边说撞洞了，后来把正则改了改，又找到了一个本地触发的XXE有点小鸡肋，算是混个CVE吧。<br>
扫出这个类。

/com/octetstring/vde/schema/InitSchema.java<br>
触发漏洞是在启动weblogic服务时，在”D:weblogic10wlserver_10.3serverlibschema.core.xml”文件写入

[![](./img/199703/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0157fde9767f2ded26.jpg)

触发漏洞位置

[![](./img/199703/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t015b4d57c5fde1171d.jpg)

schema.core.xml是写死的

[![](./img/199703/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0157297a7c8ebefd21.jpg)

调用栈：

[![](./img/199703/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t017455440f14ac7970.jpg)

[![](./img/199703/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0165ab0e8f23a31832.jpg)
