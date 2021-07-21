> 原文链接: https://www.anquanke.com//post/id/86630 


# 【木马分析】天眼实验室权威发布：XShell后门DNS Tunnel编码分析


                                阅读量   
                                **167906**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t01c58ba5a203f438e4.png)](https://p0.ssl.qhimg.com/t01c58ba5a203f438e4.png)

XShellGhost通过DNS Tunnel把打点的数据传上去，分析了下编码算法，对数据进行了解密。

<br>

**编码分析**

****

DNS Tunnel的编码算法是先经过下图的算法1编码;如图：

 [![](https://p4.ssl.qhimg.com/t0147544ec1fb1060b9.png)](https://p4.ssl.qhimg.com/t0147544ec1fb1060b9.png)

待编码的数据单字节和一个每4次运算一次的DWORD常量的1,2,3,4字节进行单字节运算来编码，如下：

 [![](https://p1.ssl.qhimg.com/t01f11c492bddd981ea.png)](https://p1.ssl.qhimg.com/t01f11c492bddd981ea.png)

算法1编码后的数据如下：

 [![](https://p5.ssl.qhimg.com/t01496dd1594c8b0c94.png)](https://p5.ssl.qhimg.com/t01496dd1594c8b0c94.png)

然后把结果转换成可见的字符转换方法是通过每个字节的高位加‘j’低位加‘a’，把1个字节拆分成2个字节的可见字符，这样就浪费了一个字节：

 [![](https://p3.ssl.qhimg.com/t01c7e77e77c9ec706f.png)](https://p3.ssl.qhimg.com/t01c7e77e77c9ec706f.png)

解密算法是加密算法的逆运算，解密算法流程如下图：

 [![](https://p5.ssl.qhimg.com/t01e082b298c7dc4203.png)](https://p5.ssl.qhimg.com/t01e082b298c7dc4203.png)

解密的单条数据的HEX如下：

 [![](https://p2.ssl.qhimg.com/t01a1fa656966ae5f3f.png)](https://p2.ssl.qhimg.com/t01a1fa656966ae5f3f.png)

根据网上的一些公开的流量数据，

 [![](https://p1.ssl.qhimg.com/t01e238770ea0014488.png)](https://p1.ssl.qhimg.com/t01e238770ea0014488.png)

解密出的一些上传的数据：

 [![](https://p5.ssl.qhimg.com/t010682a63acbc3ed8b.png)](https://p5.ssl.qhimg.com/t010682a63acbc3ed8b.png)

解密代码如下：

```
int DecodeSecond(int a1, unsigned char* a2, int a3, int a4, unsigned char* szOut)
`{`
	char v4; // cl@1
	int v5; // esi@1
	unsigned char* v6; // edi@2
	byte v7[1024]= `{`0`}`; // eax@11
	char v8; // dl@11
	int v10; // [sp+4h] [bp-10h]@1
	int v11; // [sp+8h] [bp-Ch]@1
	int v12; // [sp+Ch] [bp-8h]@1
	int v13; // [sp+10h] [bp-4h]@1
	v4 = 0;
	v5 = 0;
	v10 = a1;
	v11 = a1;
	v12 = a1;
	v13 = a1;
	int i = 0;
	if ( a3 &gt; 0 )
	`{`
		v6 = a2 - a4;
		do
		`{`
			if ( v5 &amp; 3 )
			`{`
				switch ( v5 &amp; 3 )
				`{`
				case 1:
					v11 = 0xBFD7681A - 0x7DB1F70F * v11;
					v4 = (*((byte *)&amp;v11  + 2) ^ (*((byte *)&amp;v11 + 1)
						+ (*((byte *)&amp;v11) ^ v4)))
						- *((byte *)&amp;v11 + 3);
					v8 = v4 ^ *(byte *)(v6 + v5++ + a4);
					v7[i] = v8;
					i++;
					break;
				case 2:
					v12 = 0xE03A30FA - 0x3035D0D6 * v12;
					v4 = (*((byte *)&amp;v12  + 2) ^ (*((byte *)&amp;v12 + 1)
						+ (*((byte *)&amp;v12) ^ v4)))
						- *((byte *)&amp;v12 + 3);
					v8 = v4 ^ *(byte *)(v6 + v5++ + a4);
					v7[i] = v8;
					i++;
					break;
				case 3:
					v13 = 0xB1BF5581 - 0x11C208F * v13;
					v4 = (*((byte *)&amp;v13  + 2) ^ (*((byte *)&amp;v13 + 1)
						+ (*((byte *)&amp;v13) ^ v4)))
						- *((byte *)&amp;v13 + 3);
					v8 = v4 ^ *(byte *)(v6 + v5++ + a4);
					v7[i] = v8;
					i++;
					break;
				`}`
			`}`
			else
			`{`	
			        v10 = 0x9F248E8A - 0x2F8FCE7E * v10;
				v4 = (*((byte *)&amp;v10 + 2) ^ (*((byte *)&amp;v10 + 1)
					+ (*((byte *)&amp;v10 ) ^ v4)))
					- *((byte *)&amp;v10 + 3);
				v8 = v4 ^ *(byte *)(v6 + v5++ + a4);
				v7[i] = v8;
				i++;
			`}`
		`}`
		while ( v5 &lt; a3 );
		memcpy(szOut, v7, a3);
	`}`
	return 0;
`}`		

void DecodeFirst(unsigned char* szText)
`{`
	int iLength = strlen((char*)szText);
	int iSubLength = iLength/2;
	unsigned char* szXXX = new unsigned char[iSubLength+1];
	memset(szXXX, 0, iSubLength+1);
	for (int i=0; i&lt;iSubLength; i++)
	`{`
		unsigned char One = szText[2*i] - 'a';
		unsigned char Two = szText[2*i+1] -'j';
		unsigned char Total = One+Two*16;
		szXXX[i] = Total;
	`}`
	unsigned char* szOutData = new unsigned char[iSubLength+1];
	memset(szOutData, 0, iSubLength+1);
	DecodeSecond(0, szXXX, iSubLength, 0, szOutData);

	printf(" --------------------Decode Data--------------------------------rn");
	hexdump(szOutData, iSubLength); 
	delete [] szOutData;
	return;
`}`

void hexdump(void *pAddressIn, long  lSize)
`{`
	char szBuf[100];
	long lIndent = 1;
	long lOutLen, lIndex, lIndex2, lOutLen2;
	long lRelPos;
	struct `{` char *pData; unsigned long lSize; `}` buf;
	unsigned char *pTmp,ucTmp;
	unsigned char *pAddress = (unsigned char *)pAddressIn;
	buf.pData   = (char *)pAddress;
	buf.lSize   = lSize;
	while (buf.lSize &gt; 0)
	`{`
		pTmp     = (unsigned char *)buf.pData;
		lOutLen  = (int)buf.lSize;
		if (lOutLen &gt; 16)
			lOutLen = 16;
		sprintf(szBuf, " |                            "
			"                      "
			"    %08lX", pTmp-pAddress);
		lOutLen2 = lOutLen;
		for(lIndex = 1+lIndent, lIndex2 = 53-15+lIndent, lRelPos = 0;
			lOutLen2;
			lOutLen2--, lIndex += 2, lIndex2++
			)
		`{`
			ucTmp = *pTmp++;
			sprintf(szBuf + lIndex, "%02X ", (unsigned short)ucTmp);
			if(!isprint(ucTmp))  ucTmp = '.'; // nonprintable char
			szBuf[lIndex2] = ucTmp;
			if (!(++lRelPos &amp; 3))     // extra blank after 4 bytes
			`{`  lIndex++; szBuf[lIndex+2] = ' '; `}`
		`}`
		if (!(lRelPos &amp; 3)) lIndex--;
		szBuf[lIndex  ]   = '|';
		szBuf[lIndex+1]   = ' ';
		printf("%sn", szBuf);
		buf.pData   += lOutLen;
		buf.lSize   -= lOutLen;
	`}`
`}`
```

**<br>**

**解密工具**

****

链接：[http://pan.baidu.com/s/1gfy4ImZ](http://pan.baidu.com/s/1gfy4ImZ)

密码：vugv

<br>

**参考链接**

****

[http://bobao.360.cn/news/detail/4263.html](http://bobao.360.cn/news/detail/4263.html)
