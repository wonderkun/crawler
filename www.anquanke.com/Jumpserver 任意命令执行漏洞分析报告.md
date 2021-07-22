> 原文链接: https://www.anquanke.com//post/id/229074 


# Jumpserver 任意命令执行漏洞分析报告


                                阅读量   
                                **155475**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t01fc80652fb181a2a1.png)](https://p0.ssl.qhimg.com/t01fc80652fb181a2a1.png)



## 漏洞简述

2021年01月18日，360CERT监测发现 `Jumpserver` 发布了 `远程命令执行漏洞` 的风险通告，漏洞等级：`高危`，漏洞评分：`8.5`。

Jumpserver中存在一处受控服务器远程任意命令执行漏洞，该漏洞由多处漏洞导致。

对此，360CERT建议广大用户好资产自查以及预防工作，以免遭受黑客攻击。

本次漏洞出现的核心问题在于
1. log文件的默认路径固定，且易知
1. 存在 log 文件读取漏洞
1. http GET 请求中存在 敏感参数被记录进 log
1. websocket通信中无用户权限验证


## 影响版本
- `&lt; v2.6.2`
- `&lt; v2.5.4`
- `&lt; v2.4.5`
- `= v1.5.9`
- `&gt;= v1.5.3`


## 漏洞详情

### 漏洞原理

#### log读取

`jumpserver` 中处理 `websocket` 的函数 `read_log_file` 中无用户权限校验，任意用户均可通过`ws` 调用该功能。

```
ws-&gt;
read_log_file
-&gt;
wait_util_log_path_exist
-&gt;
get_log_path(根据 type 调用设定好的两种函数)
-&gt;最终均调用
get_task_log_path
```

值得注意的是，read_log_file在处理文件读取是以4096bytes循环读取，直到断开websocket连接或文件读取完成。但每次读取有 0.2s 的间隔

`get_task_log_path` 中限定能够读取的文件后缀为 `.log` 且未对参数进行任何过滤。

```
rel_path = os.path.join(*task_id[:level], task_id + '.log')
```

因此可以通过目录跳转或绝对路径的方式读取到 `gunicorn.log` (gunicorn是python中实现 WSGI 的框架)

该文件等于access.log，记录了http请求（请求源IP，时间，请求方式，url，响应码等）

而由于 `jumpserver` 中存在一些特殊的接口，例如

```
api/v1/perms/asset-permissions/user/validate
```

该系列接口以 `GET` 方式处理敏感的信息（用户uuid,资源uuid）,导致这些敏感信息被记录在 `gunicorn.log` 中。

#### token 生成

`jumpserver`在处理 token 生成时使用的是

```
UserConnectionTokenApi-&gt;对应以下路由
/api/v1/authentication/connection-token/
/api/v1/users/connection-token/
```

该接口使用（用户uuid，资源uuid）进行token的生成，因此通过上述的过程从 `gunicorn.log` 中获取到相应的值皆可进行token生成。

#### 命令执行

最终因为 `jumpserver` 中以 `websocket` 的方式处理 `web_terminal` 相关功能，攻击者利用获得的（用户uuid, 资源uuid）便可通过 `websocket` 在对应的服务器上获得shell或执行命令等。

这部分功能由 `jumpserver/koko` 项目进行实现

koko中使用了 gin 框架

路由：`koko/ws/token`

```
wsGroup.Group("/token").GET("/", s.processTokenWebsocket)
```

由于 token 处理的特殊性（已完成认证），此处无法使用权限验证。并且利用token反查到对应的服务器资源和用户信息，进行命令行开启操作。

```
func (s *server) processTokenWebsocket(ctx *gin.Context) `{`
    tokenId, _ := ctx.GetQuery("target_id")
    tokenUser := service.GetTokenAsset(tokenId)
    ...
    currentUser := service.GetUserDetail(tokenUser.UserID)
    ...
    targetType := TargetTypeAsset
    targetId := strings.ToLower(tokenUser.AssetID)
    systemUserId := tokenUser.SystemUserID
    s.runTTY(ctx, currentUser, targetType, targetId, systemUserId)
`}`
```

远程未授权的攻击者通过构造特制的ws通信数据，导致攻击者利用jumpserver在其管理的服务器上执行任意命令。

### 漏洞利用

漏洞利用省略了获得 （用户uuid，资源uuid）的步骤。

[![](https://p403.ssl.qhimgs4.com/t01758761f032e1d4c3.png)](https://p403.ssl.qhimgs4.com/t01758761f032e1d4c3.png)



## 影响面分析

`https://github.com/jumpserver/installer/blob/master/compose/docker-compose-app.yml`

在`jumpserver`的官方 installer 中，默认使用的日志路径为固定的 `/opt/jumpserver/logs`

```
volumes:
      - $`{`CONFIG_DIR`}`/core/config.yml:/opt/jumpserver/config.yml
      - $`{`VOLUME_DIR`}`/core/data:/opt/jumpserver/data
      - $`{`VOLUME_DIR`}`/core/logs:/opt/jumpserver/logs
```

所以使用官方 installer 的用户最容易被攻击成功，该类用户应当尽快更新。而其他手动配置`jumpserver`的用户，应当检查是否使用了相同的路径，或常规易猜解的路径。

`https://github.com/jumpserver/Dockerfile` 而在`jumpserver`历史快速构建项目中，同样存在该问题，使用了固定路径 `/opt/jumpserver/logs`



## 时间线

2021-01-15 Jumpserver官方发布漏洞通告

2021-01-18 360CERT发布通告

2021-01-18 360CERT发布分析报告



## 参考链接

[Jumpserver受控服务器任意命令执行漏洞通告 – 360CERT](https://cert.360.cn/warning/detail?id=4f68e2896d6ac9ce8d5254c9060c8d3a)

[jumpserver/Dockerfile: Jumpserver all in one Dockerfile](https://github.com/jumpserver/Dockerfile)

[jumpserver/installer: JumpServer 安装管理包，让用户更便捷的安装、部署、更新、管理 JumpServer。](https://github.com/jumpserver/installer)

[jumpserver/jumpserver: JumpServer 是全球首款开源的堡垒机，是符合 4A 的专业运维安全审计系统。](https://github.com/jumpserver/jumpserver/tree/master)

[jumpserver/koko: KoKo是go版本的coco，新的Jumpserver ssh/ws server](https://github.com/jumpserver/koko)
