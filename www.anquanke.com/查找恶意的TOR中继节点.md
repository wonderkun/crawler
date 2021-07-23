> 原文链接: https://www.anquanke.com//post/id/83160 


# 查找恶意的TOR中继节点


                                阅读量   
                                **124134**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[http://marcoramilli.blogspot.tw/2015/12/spotting-malicious-node-relays.html](http://marcoramilli.blogspot.tw/2015/12/spotting-malicious-node-relays.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t016c257d7d5ec7aa77.jpg)](https://p0.ssl.qhimg.com/t016c257d7d5ec7aa77.jpg)

        **众所周知,TOR是一种能够保护世界各地不同中继节点之间通信调度数据包的“软件”,由志愿者建立的网络进行运营。在过去的几年中,TOR已经被物理和网络攻击者广泛用于掩盖恶意操作。TOR也被视为最主要的进入暗网的方法,在暗网中,“恶意”的人可以通过黑市非法买卖东西。**

        网络里每个中继节点都能够根据自己的配置状态,决定是作为一个ExitPoint(在以下图片中用最后一台接触“Bob”的机器表示)或者只是一个中继节点(在下图中,TOR节点用“绿十字”突出显示)。如果中继节点决定成为一个ExitNode,就会向公众公开自己的IP地址,这通常是一个引起当地警方警觉的好办法。

[![](https://p2.ssl.qhimg.com/t0143acb9e1dc760b48.png)](https://p2.ssl.qhimg.com/t0143acb9e1dc760b48.png)

        过去一年中,电视节目,广播电台,youtube频道,Facebook这一类大众媒体披露出,许多黑市故意将人们引向DarkWeb,从而将他们暴露在许多新的攻击场景下。事实上新的攻击者会为了监视他们的通信流而设置退出节点或继电器节点。这种攻击可能会在许多单一的方式下发生,但最常用的今天写的这三个:

        1.DNS中毒:这个技术主要在于将与知名网站有关的DNS调用重定向到一个假的页面上, 这个假的页面包含开发工具包,可以使用户的浏览器妥协。

        2.文件修补:这个技术是改变请求的文件,在其到达目的地之前在其中添加恶意内容.这些步骤会在发给原始请求者之前直接在ExitPoint /中继节点上进行。

        3.替换证明(SSL – MITM):这个技术是用假的证书替换网站真实的证书,这样就可以解密通信流,拦截凭证和参数。

        致力于网络安全就意味着要及时意识到这样的攻击的存在,也要能够决定将在何时通过TOR中继节点。请注意,TOR不是DarkWeb中唯一的匿名网络.

        我的目标是弄清楚我的TOR流通过恶意中继节点的时间。出于这样一个原因,我决定写一个能够对DNS Poison,文件修补和SSL-MITM做出一些快速检查的python脚本。这个脚本已经存在了2年, 直到现在仍是保密状态。自从科学研究应用了我的FindMalExit.py的高级版本之后,我决定公开这个脚本。

 

**        想法**

        实际上这是一个非常简单的想法:“让我们在不通过TOR网络(或通过可靠电路)的情况下拿到证书,IP地址和文件,然后重复这个过程,直到通过所有可用的中继节点。比较结果并进行检查。”

 

**        实现**

          以下请查收我的代码。请记住这是一个不是最终的代码 (这段代码只是一个更大的项目中的第一个版本,现在由Yoroi维护)。我决定发布HTML格式的代码。****

**<br>**

```
#!/usr/bin/env python2
#========================================================================#
#               THIS IS NOT A PRODUCTION RELEASED SOFTWARE               #
#========================================================================#
# Purpose of finMaliciousRelayPoints is to proof the way it's possible to#
# discover TOR malicious Relays Points. Please do not use it in          #
# any production  environment                                            #
# Author: Marco Ramilli                                                  #
# eMail: XXXXXXXX                                                        #
# WebSite: marcoramilli.blogspot.com                                     #
# Use it at your own                                                     #
#========================================================================#
#==============================Disclaimer: ==============================#
#THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND ANY EXPRESS OR      #
#IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED          #
#WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE  #
#DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT,      #
#INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES      #
#(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR      #
#SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)      #
#HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,     #
#STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING   #
#IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE      #
#POSSIBILITY OF SUCH DAMAGE.                                             #
#========================================================================#
#-------------------------------------------------------------------------
#------------------- GENERAL SECTION -------------------------------------
#-------------------------------------------------------------------------
import StringIO
import tempfile
import time
import hashlib
import traceback
from   geoip         import  geolite2
import stem.control
TRUSTED_HOP_FINGERPRINT = '379FB450010D17078B3766C2273303C358C3A442' 
#trusted hop
SOCKS_PORT              = 9050
CONNECTION_TIMEOUT      = 30  # timeout before we give up on a circuit
#-------------------------------------------------------------------------
#---------------- File Patching Section ----------------------------------
#-------------------------------------------------------------------------
import pycurl
check_files               = `{`
                             "http://live.sysinternals.com/psexec.exe",
                             "http://live.sysinternals.com/psexec.exe",
                             "http://live.sysinternals.com/psping.exe", `}`
check_files_patch_results = []
class File_Check_Results:
    """
    Analysis Results against File Patching
    """
    def __init__(self, url, filen, filepath, exitnode, found_hash):
        self.url           = url
        self.filename      = filen
        self.filepath      = filepath
        self.exitnode      = exitnode
        self.filehash      = found_hash
#------------------------------------------------------------------------
#------------------- DNS Poison Section ---------------------------------
#------------------------------------------------------------------------
import dns.resolver
import socks
import socket
check_domain_poison_results = []
domains                     = `{`
                                 "www.youporn.com",
                                 "youporn.com",
                                 "www.torproject.org",
                                 "www.wikileaks.org",
                                 "www.i2p2.de",
                                 "torrentfreak.com",
                                 "blockchain.info",
`}`
class Domain_Poison_Check:
    """
    Analysis Results against Domain Poison
    """
    def __init__(self, domain):
        self.domain  = domain
        self.address = []
        self.path    = []
    def pushAddr(self, add):
        self.address.append(add)
    def pushPath(self, path):
        self.path = path
#-----------------------------------------------------------------------
#------------------- SSL Sltrip Section --------------------------------
#-----------------------------------------------------------------------
import OpenSSL
import ssl
check_ssl_strip_results   = []
ssl_strip_monitored_urls = `{`
                            "www.google.com",
                            "www.microsoft.com",
                            "www.apple.com",
                            "www.bbc.com",
`}`
class SSL_Strip_Check:
    """
    Analysis Result against SSL Strip
    """
    def __init__(self, domain, public_key, serial_number):
        self.domain        = domain
        self.public_key    = public_key
        self.serial_number = serial_number
#----------------------------------------------------------------------
#----------------     Starting Coding   -------------------------------
#----------------------------------------------------------------------
def sslCheckOriginal():
    """
    Download the original Certificate without TOR connection
    """
    print('[+] Populating SSL for later check')
    for url in ssl_strip_monitored_urls:
        try:
            cert = ssl.get_server_certificate((str(url), 443))
            x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
            p_k  = x509.get_pubkey()
            s_n  = x509.get_serial_number()
            print('[+] Acquired Certificate: %s' % url)
            print('    |_________&gt; serial_number %s' % s_n)
            print('    |_________&gt; public_key %s' % p_k)
            check_ssl_strip_results.append(SSL_Strip_Check(url, p_k, s_n))
        except Exception as err:
            print('[-] Error While Acquiring certificats on setup phase !')
            traceback.print_exc()
    return time.time()
def fileCheckOriginal():
    """
    Downloading file ORIGINAL without TOR
    """
    print('[+] Populating File Hasing for later check')
    for url in check_files:
        try:
            data = query(url)
            file_name = url.split("/")[-1]
            _,tmp_file = tempfile.mkstemp(prefix="exitmap_%s_" % file_name)
            with open(tmp_file, "wb") as fd:
                fd.write(data)
                print('[+] Saving File  "%s".' % tmp_file)
                check_files_patch_results.append( File_Check_Results(url, file_name, tmp_file, "NO", sha512_file(tmp_file)) )
                print('[+] First Time we see the file..')
                print('    |_________&gt; exitnode : None'       )
                print('    |_________&gt; :url:  %s' % str(url)     )
                print('    |_________&gt; :filePath:  %s' % str(tmp_file))
                print('    |_________&gt; :file Hash: %s' % str(sha512_file(tmp_file)))
        except Exception as err:
                print('[-] Error ! %s' % err)
                traceback.print_exc()
                pass
    return time.time()
def resolveOriginalDomains():
    """
        Resolving DNS For original purposes
    """
    print('[+] Populating Domain Name Resolution for later check ')
    try:
        for domain in domains:
            response = dns.resolver.query(domain)
            d = Domain_Poison_Check(domain)
            print('[+] Domain: %s' % domain)
            for record in response:
                print(' |____&gt; maps to %s.' % (record.address))
                d.pushAddr(record)
            check_domain_poison_results.append(d)
        return time.time()
    except Exception as err:
        print('[+] Exception: %s' % err)
        traceback.print_exc()
        return time.time()
def query(url):
  """
  Uses pycurl to fetch a site using the proxy on the SOCKS_PORT.
  """
  output = StringIO.StringIO()
  query = pycurl.Curl()
  query.setopt(pycurl.URL, url)
  query.setopt(pycurl.PROXY, 'localhost')
  query.setopt(pycurl.PROXYPORT, SOCKS_PORT)
  query.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)
  query.setopt(pycurl.CONNECTTIMEOUT, CONNECTION_TIMEOUT)
  query.setopt(pycurl.WRITEFUNCTION, output.write)
  try:
    query.perform()
    return output.getvalue()
  except pycurl.error as exc:
    raise ValueError("Unable to reach %s (%s)" % (url, exc))
def scan(controller, path):
  """
  Scan Tor Relays Point to find File Patching
  """
  def attach_stream(stream):
    if stream.status == 'NEW':
      try:
        controller.attach_stream(stream.id, circuit_id)
        #print('[+] New Circuit id (%s) attached and ready to be used!' % circuit_id)
      except Exception as err:
        controller.remove_event_listener(attach_stream)
        controller.reset_conf('__LeaveStreamsUnattached')
  try:
    print('[+] Creating a New TOR circuit based on path: %s' % path)
    circuit_id = controller.new_circuit(path, await_build = True)
    controller.add_event_listener(attach_stream, stem.control.EventType.STREAM)
    controller.set_conf('__LeaveStreamsUnattached', '1')  # leave stream management to us
    start_time = time.time()
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
    socket.socket = socks.socket
    ip = query('http://ip.42.pl/raw')
    if ip is not None:
        country  = geolite2.lookup( str(ip) ).country
        print('n n')
        print('[+] Performing FilePatch,  DNS Spoofing and Certificate Checking
              passing through --&gt; %s (%s) n n' % (str(ip), str(country))  )
    time_FileCheck = fileCheck(path)
    print('[+] FileCheck took: %0.2f seconds'  % ( time_FileCheck - start_time))
    #time_CertsCheck  = certsCheck(path)
    #print('[+] CertsCheck took: %0.2f seconds' % ( time_DNSCheck - start_time))
    time_DNSCheck  = dnsCheck(path)
    print('[+] DNSCheck took: %0.2f seconds'   % ( time_DNSCheck - start_time))
  except Exception as  err:
    print('[-] Circuit creation error: %s' % path)
  return time.time() - start_time
def certsCheck(path):
    """
    SSL Strip detection
    TODO: It's still a weak control. Need to collect and to compare public_key()
    """
    print('[+] Checking Certificates')
    try:
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
        socket.socket = socks.socket
        for url in ssl_strip_monitored_urls:
            cert = ssl.get_server_certificate((str(url), 443))
            x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
            p_k  = x509.get_pubkey()
            s_n  = x509.get_serial_number()
            for stored_cert in check_ssl_strip_results:
                if str(url) == str(stored_cert.domain):
                    if str(stored_cert.serial_number) != str(s_n):
                        print('[+] ALERT Found SSL Strip on uri (%s) through path %s ' % (url, path))
                        break
                    else:
                        print('[+] Certificate Check seems to be OK for %s' % url)
    except Exception as err:
        print('[-] Error: %s' % err)
        traceback.print_exc()
    socket.close()
    return time.time()
def dnsCheck(path):
    """
    DNS Poisoning Check
    """
    try:
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
        socket.socket = socks.socket
        print('[+] Checking DNS ')
        for domain in domains:
            ipv4 = socket.gethostbyname(domain)
            for p_d in check_domain_poison_results:
                if str(p_d.domain) == str(domain):
                    found = False
                    for d_ip in p_d.address:
                        if str(ipv4) == str(d_ip):
                            found = True
                            break
                    if found == False:
                        print('[+] ALERT:DNS SPOOFING FOUND: name: %s ip: %s  (path: %s )' % (domain, ipv4, path) )
                    else:
                        print('[+] Check DNS (%s) seems to be OK' % domain)
    except Exception as err:
        print('[-] Error: %s' % err)
        traceback.print_exc()
    socket.close()
    return time.time()
def fileCheck(path):
    """
    Downloading file through TOR circuits doing the hashing
    """
    print('[+] Checking For File patching ')
    for url in check_files:
        try:
            #File Rereive
            data = query(url)
            file_name = url.split("/")[-1]
            _,tmp_file = tempfile.mkstemp(prefix="exitmap_%s_" % file_name)
            with open(tmp_file, "wb") as fd:
                fd.write(data)
                for i in check_files_patch_results:
                    if str(i.url) == str(url):
                        if str(i.filehash) != str(sha512_file(tmp_file)):
                            print('[+] ALERT File Patch FOUND !')
                            print('    | exitnode : %s' % str(i.exitnode)      )
                            print('    |_________&gt; url: %s' % str(i.url)        )
                            print('    |_________&gt; filePath: %s' % str(i.filepath)   )
                            print('    |_________&gt; fileHash: %s' % str(i.filehash)   )
                            #check_files_patch_results.append( File_Check_Results(url, file_name, tmp_file, path, sha512_file(tmp_file)) )
                        else :
                            print('[+] File (%s) seems to be ok' % i.url)
                        break
        except Exception as err:
                print('[-] Error ! %s' % err)
                traceback.print_exc()
                pass
    return time.time()
def sha512_file(file_name):
    """
    Calculate SHA512 over the given file.
    """
    hash_func = hashlib.sha256()
    with open(file_name, "rb") as fd:
        hash_func.update(fd.read())
    return hash_func.hexdigest()
if __name__ == '__main__':
    start_analysis = time.time()
    print("""
  |=====================================================================|
  | Find Malicious Relay Nodes is a python script made for checking 3   |
  | unique kind of frauds such as:                                      |
  | (1) File Patching                                                   |
  | (2) DNS Poison                                                      |
  | (3) SSL Stripping (MITM SSL)                                        |
  |=====================================================================|
         """)
    print("""
  |=====================================================================|
  |                 Initialization Phase                                |
  |=====================================================================|
       """)
    dns_setup_time             = resolveOriginalDomains()
    print('[+] DNS Setup Finished: %0.2f' % (dns_setup_time - start_analysis))
    file_check_original_time   = fileCheckOriginal()
    print('[+] File Setup Finished: %0.2f' % (file_check_original_time - start_analysis))
    ssl_checking_original_time = sslCheckOriginal()
    print('[+] Acquiring Certificates  Setup Finished: %0.2f' % (ssl_checking_original_time - start_analysis))
    print("""
  |=====================================================================|
  |                 Analysis  Phase                                     |
  |=====================================================================|
          """)
    print('[+] Connecting and Fetching possible Relays ...')
    with stem.control.Controller.from_port() as controller:
      controller.authenticate()
      net_status = controller.get_network_statuses()
      for descriptor in net_status:
        try:
          fingerprint = descriptor.fingerprint
          print('[+] Selecting a New Exit Point:')
          print('[+] |_________&gt; FingerPrint: %s ' % fingerprint)
          print('[+] |_________&gt; Flags: %s ' % descriptor.flags)
          print('[+] |_________&gt; Exit_Policies: %s ' % descriptor.exit_policy)
          if 'EXIT' in (flag.upper() for flag in descriptor.flags):
              print('[+] Found Exit Point. Performing Scan through EXIT: %s' % fingerprint)
              if None == descriptor.exit_policy:
                  print('[+] No Exit Policies found ... no certs checking')
                  time_taken = scan(controller, [TRUSTED_HOP_FINGERPRINT, fingerprint])
          else:
              #print('[+] Not Exit Point found. Using it as Relay passing to TRUST Exit Point')
              pass
              #time_taken = scan(controller, [fingerprint, TRUSTED_HOP_FINGERPRINT])
          #print('[+] Finished Analysis for %s finished  =&gt; %0.2f seconds' % (fingerprint, time_taken))
        except Exception as exc:
            print('[-] Exception on  FingerPrint: %s =&gt; %s' % (fingerprint, exc))
            traceback.print_exc()
            pass
```
