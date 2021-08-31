> 原文链接: https://www.anquanke.com//post/id/249258 


# UIUCTF2021 Tablet（iPadOS Forensics）


                                阅读量   
                                **20918**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t0173d6cf7797e15b96.jpg)](https://p0.ssl.qhimg.com/t0173d6cf7797e15b96.jpg)



## Tablet1

> <p>Red has been acting very sus lately… so I took a backup of their tablet to see if they are hiding something!<br>
It looks like Red has been exfiltrating sensitive data bound for Mira HQ to their own private server. We need to access that server and contain the leak.</p>

### <a class="reference-link" name="%E7%A7%81%E9%92%A5"></a>私钥

```
grep  -r "ssh" ./
```

搜索到webssh.db后，利用DB Browser打开db文件。

[![](https://p2.ssl.qhimg.com/t01075f201d4b40c3f8.png)](https://p2.ssl.qhimg.com/t01075f201d4b40c3f8.png)

导出私钥为`ssl.txt`。

一开始以为还要去找密码，其实`********`这就是密码了。利用一下命令把openssl private key 解密一下。

```
ssh-keygen -p -N "" -m pem -f ssh.txt
```

得到rsa 密钥，我们现在可以去连接服务器了。

当然也可以直接用以下这条命令

```
ssh -p 42069 -i id_rsa red.cha1.uiuc.tf
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0101ea62eabef1c03d.png)

在这里我使用xshell进行连接

一开始以为是ssh连接服务器，这个服务器肯定不会允许搞破坏，应该是连不上的。

[![](https://p1.ssl.qhimg.com/t01f6966eaf98bcb9b5.png)](https://p1.ssl.qhimg.com/t01f6966eaf98bcb9b5.png)

**<a class="reference-link" name="sftp"></a>sftp**

提示我们利用sftp进行连接，我们修改连接方式，可以看到我们已经连接到服务器上了。

[![](https://p2.ssl.qhimg.com/t01e650558abbbca6be.png)](https://p2.ssl.qhimg.com/t01e650558abbbca6be.png)

ls，查看当前目录下的文件和权限。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t018d84b9746df0f017.png)

get，下载.bash_history文件

[![](https://p1.ssl.qhimg.com/t01729a513de6cc90a8.png)](https://p1.ssl.qhimg.com/t01729a513de6cc90a8.png)

```
mv /srv/exfiltrated "/srv/..."
```

提示我们到`/srv/...`目录下。

[![](https://p2.ssl.qhimg.com/t01ca6ef899c62a5ce2.png)](https://p2.ssl.qhimg.com/t01ca6ef899c62a5ce2.png)

发现一张图片，get下来，就是flag

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0174504cd03976629f.png)

```
uiuctf`{`upload_task_only_takes_9_seconds_0bf79b`}`
```



## Tablet2

> Wait… there are TWO impostors?! Red must have been in contact with the other impostor. See if you can find out what they are plotting.

### <a class="reference-link" name="bash_history"></a>bash_history

在`/var/root/`目录下找到了`.bash_history`,内容为以下部分

```
ls
exit
tar --version
exit

find ./ -iname *hammerandchisel* -type d 2&gt;/dev/null
cd 0CE5D539-F72A-4C22-BADF-A02CE5A50D2E/
ls
cd Library/
ls
cd Caches/
ls
cd com.hammerandchisel.discord/
ls
rm -rf *
ls
cd ..
ls
ls
cd com.hammerandchisel.discord/
ls
exit
cd ../mobile/Containers/Data/Application/AA7DB282-D12B-4FB1-8DD2-F5FEF3E3198B/Library/Application\ Support/
rm webssh.db 
exit
```

需要关注的为以下两个命令，第二个命令是我们刚刚找到的`webssh.db`，

```
find ./ -iname *hammerandchisel* -type d 2&gt;/dev/null

cd com.hammerandchisel.discord/
ls
rm -rf *

cd com.hammerandchisel.discord/
ls

cd ../mobile/Containers/Data/Application/AA7DB282-D12B-4FB1-8DD2-F5FEF3E3198B/Library/Application\ Support/
rm webssh.db
```

**<a class="reference-link" name="find"></a>find**

通过google得到这是`discorder`，我们考虑题目描述说的接触为`discorder`。

[![](https://p1.ssl.qhimg.com/t01eae5e8c2dc8d9af5.png)](https://p1.ssl.qhimg.com/t01eae5e8c2dc8d9af5.png)

```
find ./ -iname *hammerandchisel*
```

[![](https://p0.ssl.qhimg.com/t0189eb6f3dede04ae8.png)](https://p0.ssl.qhimg.com/t0189eb6f3dede04ae8.png)

找到文件`****.plist`

[![](https://p0.ssl.qhimg.com/t01172de64c16d73138.png)](https://p0.ssl.qhimg.com/t01172de64c16d73138.png)

我们在这里看到了`BlueAmogus`，猜测为碰头的第二的人。但是我没有证据。

**<a class="reference-link" name="ktx"></a>ktx**

我们在这个文件夹找到了很多的ktx文件，为什们bash中需要删除它们呢？我们尝试着去打开这些文件。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01696dc15cc721b7c4.png)

这是一个压缩过的纹理图片，我们在windows下需要对应的工具转换该文件，或者在mac下可以直接查看ktx文件。

```
ios_ktx2png.exe *****.ktx
```

[KTX 纹理压缩 | Egret Engine](https://docs.egret.com/engine/docs/2dRender/bitmapTexture/ktx)

[![](https://p2.ssl.qhimg.com/t015eda89dcb131af53.png)](https://p2.ssl.qhimg.com/t015eda89dcb131af53.png)

从这张图，我们得到线索，一是encrypted note，二是password。

**<a class="reference-link" name="Cache.db"></a>Cache.db**

我们继续跟进之前的`bash_history`，找到对应的文件夹

[![](https://p3.ssl.qhimg.com/t0170c941367c94e60b.png)](https://p3.ssl.qhimg.com/t0170c941367c94e60b.png)

打开`Cache.db`文件，慢慢看信息，发现了之前图片中被黑色覆盖的密码以及之前没看全的消息。

```
The password is ||su5Syb@k4||su5Syb@k4White is onto me... they kept calling me out last meetingI'll deal with them, you just make sure this next sabotage goes to planI sent you an encrypted note with all the details

```

[![](https://p1.ssl.qhimg.com/t011662408fe93face9.png)](https://p1.ssl.qhimg.com/t011662408fe93face9.png)

那么现在，我们只需要去找到Blue发送给Red的note，并进行解密即可。那么note在哪里找呢？我也无法猜测到。而当我使用如下命令时，我看到了一个很符合的`oneNote`

```
grep -r "note" ./
```

[![](https://p5.ssl.qhimg.com/t0120ecb511bc4c6ed5.png)](https://p5.ssl.qhimg.com/t0120ecb511bc4c6ed5.png)

在对应的文件夹中我们可以知道两个数据库文件。

[![](https://p5.ssl.qhimg.com/t012d57e9587eea817d.png)](https://p5.ssl.qhimg.com/t012d57e9587eea817d.png)

我们可以在Records.db中发现recordData，导出为文件后找到了EncryptionInfo

[![](https://p3.ssl.qhimg.com/t01c81ad30aa27bb61b.png)](https://p3.ssl.qhimg.com/t01c81ad30aa27bb61b.png)

[![](https://p2.ssl.qhimg.com/t018c043af844af026b.png)](https://p2.ssl.qhimg.com/t018c043af844af026b.png)

接下来就该思考如何使用该密钥进行解密。

无法解密，当然，我们是找错了note文本。最后我们通过搜索encrypt找到了这个文件夹，可以看到EndToEndEncryption~~大概率就是出题人设置的文件夹。~~这是端到端加密，很多文件夹都有这样的一个子文件夹，并不是出题人的设置。

[![](https://p4.ssl.qhimg.com/t01612eb866c60e49eb.png)](https://p4.ssl.qhimg.com/t01612eb866c60e49eb.png)

[![](https://p4.ssl.qhimg.com/t01d5b4091a465782db.png)](https://p4.ssl.qhimg.com/t01d5b4091a465782db.png)

我们通过备忘录来打开里面的`com.apple.notes.analytics.plist`文件。但是似乎不需要密码。

[![](https://p0.ssl.qhimg.com/t011b90a44305eea180.png)](https://p0.ssl.qhimg.com/t011b90a44305eea180.png)

说明我们找到的并不是最后真正加密的文件。我们返回上级目录。

[![](https://p5.ssl.qhimg.com/t01cf0c8b9645a821e1.png)](https://p5.ssl.qhimg.com/t01cf0c8b9645a821e1.png)

在这里找到了一个mobilenotes.plist，可惜也不是这个。我们继续返回上级目录

**<a class="reference-link" name="NoteStore.sqlite"></a>NoteStore.sqlite**

那么最后我们该如何去寻找加密的note呢？以下命令就可以找到对应的note存储的数据库。然后我们就需要利用密码去解密。

```
sudo find ./ -type f -name NoteStore.sqlitesudo find ./ -type f -name NoteStore.db
```

[![](https://p1.ssl.qhimg.com/t01aab509e112f251c8.png)](https://p1.ssl.qhimg.com/t01aab509e112f251c8.png)

在github上面找到了一个ruby的项目，可以对已知密码的note可以进行解密。

<a class="reference-link" name="apple_cloud_note_parser"></a>**apple_cloud_note_parser**

在安装时，最可能出现的问题是在openssl上面。

[https://stackoverflow.com/questions/66376203/failed-to-build-gem-native-extension-when-installing-openssl](https://stackoverflow.com/questions/66376203/failed-to-build-gem-native-extension-when-installing-openssl)

```
log_info "Upgrading and linking OpenSSL ..."  brew install openssl  brew link openssl --force
```

得到报错信息后，把解决方案进行执行即可顺利安装apple_cloud_note_parser

```
echo "su5Syb@k4" &gt; password.txtruby notes_cloud_ripper.rb -f NoteStore.sqlite -w password.txt
```

[![](https://p0.ssl.qhimg.com/t013f8d551244051db2.png)](https://p0.ssl.qhimg.com/t013f8d551244051db2.png)

**<a class="reference-link" name="tips"></a>tips**

以下为代码执行流程

[![](https://p3.ssl.qhimg.com/t0108a1fb94d385b7e7.png)](https://p3.ssl.qhimg.com/t0108a1fb94d385b7e7.png)

[![](https://p0.ssl.qhimg.com/t01048fd7bd7538894f.png)](https://p0.ssl.qhimg.com/t01048fd7bd7538894f.png)

[![](https://p1.ssl.qhimg.com/t0141bb1def4c201c18.png)](https://p1.ssl.qhimg.com/t0141bb1def4c201c18.png)

generate_key_encrypting_key

[![](https://p5.ssl.qhimg.com/t0120d0c66d184a3e19.png)](https://p5.ssl.qhimg.com/t0120d0c66d184a3e19.png)

aes_key_unwrap

[![](https://p1.ssl.qhimg.com/t010ba9a1e5efd67420.png)](https://p1.ssl.qhimg.com/t010ba9a1e5efd67420.png)

本文所用文件已分享<br>
链接: [https://pan.baidu.com/s/1VLg805GD-eTHzEPLdGDAZA](https://pan.baidu.com/s/1VLg805GD-eTHzEPLdGDAZA) 提取码: alh5
