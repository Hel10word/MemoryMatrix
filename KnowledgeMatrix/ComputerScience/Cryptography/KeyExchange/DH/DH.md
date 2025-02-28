---
id: 2878089c-972a-4d10-89b8-15f86e3b5455
aliases:
  - 2878089c-972a-4d10-89b8-15f86e3b5455
  - DH
title: DH
created: 2025-02-28T16:49
author: hel10word
status: published
tags:
  - dh
  - cryptography
summary: 这是一段简短的摘要，描述文档的主要内容
---
# DH



#### 概述

[DH](https://en.wikipedia.org/wiki/Diffie%E2%80%93Hellman_key_exchange) (Diffie-Hellman) , 该算法主要用来实现**安全的**密钥交换 , 它可以做到在通讯双方在完全没有对方任何预先信息的条件下 , 通过不安全的信道 , 创建一个双方共享的私有密钥 . 

DH 算法缺点：**本身不支持认证** . 常与 ([RSA](../RSA/RSA.md) , DSA , ECDSA) 等配合——靠签名算法来帮忙进行身份验证 , 当 DH 算法与 [RSA](../RSA/RSA.md) 配合使用 , 也成为“DH-RSA” . 



#### 算法步骤

1.  通讯双方 (张三、李四) 需要先约定好两个对外公开的参数：一个素数 `p` 作为模数 , 一个素数 `g` 作为基数 . 
2.  张三 , 需要想好一个自然数 `a` 作为私钥 (**不能公开**)  , 然后计算  $A=g^{a}\ mod\ p$  作为自己的公钥 (**可以公开**)  . 
3.  李四 , 需要想好一个自然数 `b` 作为私钥 (**不能公开**)  , 然后计算  $B=g^{b}\ mod\ p$  作为自己的公钥 (**可以公开**)  . 
4.  张三和李四互相交换各自的公钥 A、B , 然后张三计算出  $K=B^{a}\ mod\ p$  , 李四计算出  $K=A^{b}\ mod\ p$  . 




#### 实例验证

```python
# 张三 
p = 97
g = 3
a = 6
# 并将 p、g 发送给 李四

# 李四
p = 97
g = 3
b = 21

# 张三计算出自己的 公钥 A 发送给 李四
A = (g**a) % p = 50

#李四计算自己的 公钥 B 发送给 张三
B = (g**b) % p = 79


# 此时 张三拥有的信息  (p、g、a、A、B)    李四拥有的信息  (p、g、b、B、A)    网络中公开的信息   (p、g、A、B) 

# 张三 计算本次会话的 密钥 
print((B**a) % p)  # 此处输出 47

# 李四 计算本次会话的 密钥
print((A**b) % p)  # 此处输出 47
```



*该算法保证了一下几点*

-   张三和李四计算出来的 `K` 必定是一致的 . 
-   张三和李四都无法根据 已知 的数 , 推算出对方的私钥 . 
-   就算有偷窥者 , 虽然能看到 `p`、`q`、`A`、`B` 但也无法推算出 `a` 与 `b` ,自然也就无法推算出 `K` . 



#### 算法证明

1. DH 算法证明的公式 :     $(g^{a}\ mod\ p)^{b}\ mod\ p = g^{a\cdot b}\ mod \ p$




2. 根据 模运算 乘法法则 :    $(a\cdot b)\ mod\ p= (a\ mod\ p\cdot b\ mod\ p)\ mod \ p$




3. 公式证明：

$$
\begin{aligned}
    g^{a \cdot b}\ \text{mod}\ p &= (\underset{b个}{\underbrace{g^{a}\cdot g^{a}\cdots \ g^{a}}})\ \text{mod}\ p \\
    &= (\underset{b个}{\underbrace{g^{a}\ \text{mod}\ p\ \cdot g^{a}\ \text{mod}\ p\ \cdots \ g^{a}\ \text{mod}\ p}})\ \text{mod}\ p \\
    &= (g^{a}\ \text{mod}\ p)^{b}\ \text{mod}\ p
\end{aligned}
$$



1. 算法验证：

$$
\begin{aligned}
    K &= B^{a}\ \text{mod}\ p = A^{b}\ \text{mod}\ p \\
    &= (g^{b}\ \text{mod}\ p)^{a}\ \text{mod}\ p = (g^{a}\ \text{mod}\ p)^{b}\ \text{mod}\ p \\
    &= g^{b\cdot a}\ \text{mod}\ p = g^{a\cdot b}\ \text{mod}\ p
\end{aligned}
$$





> 日常中 , 使用 DH 算法 , 都是结合其他签名算法 ([RSA](../RSA/RSA.md)、DSA、ECDSA) 等来配合使用 , 弥补 DH 不支持认证的缺点 . 
>
>    (1) 、服务端把  (p、g、服务端生成的公钥S) 使用签名算法进行签名 , 并将签名以及上述信息合并发送给客户端 . 
>
>    (2) 、客户端收到后对签名进行验证 , 并根据随机数 c 计算出公钥 C , 并发送给服务端 . 
>
>    (3) 、双方根据 上述算法计算出 当前会话密钥 K . 



#### 如何防范偷窥  (嗅探) 

偷窥者可以通过嗅探等技术 , 得到相关参数 (模数 p、基数 g、以及双方的公钥)  , 但是无法推算出双方的私钥 , 也无法推算出双方的会话密钥 (K)  , 这点是由 DH 算法在数学上保证的 . 



#### 如何防范篡改  (假冒身份) 

-   攻击方式1
    
    -   攻击者可以通过 篡改 服务端数据 . 但这些信息已经进行过数字签名 , 被篡改后会被客户端发现 . 
-   攻击方式2
    
    -   攻击者可以篡改客户端公钥 , 这一步没有签名 , 服务端收到数据后不会发现被篡改 . 但是 , 攻击者篡改后会导致客户端生成的会话密钥与服务端不一致 , 在后续的通讯步骤中会发现这一点 , 导致通讯被终止 . 
    
    

#### DH 的变种 —— 基于 椭圆曲线 的ECDH

DH 算法有一个变种 ECDH (Elliptic Curve Diffie-Hellman) , 它与 DH 类似 , 区别在于 DH 算法依赖的是——求解**离散对数问题**的困难 ; ECDH 算法依赖的是——求解**椭圆曲线离散对数问题**的困难 . 



#### 其他

为了对抗“回溯性破解” , 可以强制要求双方每次都生成**随机的**私钥 . 而且每次生成的两个私钥用完就丢弃 (销毁)  . 如此一来 , 攻击者就难以破解过往的历史数据 . DH 算法经过如此改良之后叫做 DHE (追加的字母 E 表示ephemeral)  . 与 DH 类似 , ECDH 也可以做类似的改良 , 变成 ECDHE , 以对抗“回溯破解” . 
















---
可使用 [![](https://img.shields.io/badge/Excalidraw-CCCCFF?style=for-the-badge&logo=excalidraw&logoColor=333&logoWidth=20&labelColor=CCCCFF)](https://excalidraw.com/) 工具打开本文的 [原型图文件](attachments/excalidraw.excalidraw)