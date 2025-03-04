---
id: 8fc0d56c-ee9d-490c-8d83-98ef5f7523d8
aliases:
  - 8fc0d56c-ee9d-490c-8d83-98ef5f7523d8
  - RSA
title: RSA
created: 2025-02-28T16:50
author: hel10word
status: published
tags:
  - status/published
  - rsa
  - cryptography
summary: 这是一段简短的摘要，描述文档的主要内容
---
# RSA



#### 概述

[RSA](https://en.wikipedia.org/wiki/RSA_(cryptosystem)) (Rivest–Shamir–Adleman) , 大概是 SSL 最古老的密钥协商方式——早期的 SSL只支持一种密钥协商机制 , 那就是它!!非对称加密算法的特定是——加密和解密使用**不同的**密钥 . 并且非对称加密算法既可以用来做“**加密、解密**” , 还可以用来做”**数字签名**“ . 



#### 算法步骤

| 步骤 | 说明                         | 描述 |
| ---- | ---------------------------- | ---- |
| 1    | 选择一对不相等且足够大的**素数** | $p,q$ |
| 2    | 计算 `p`、`q` 的乘积         | $n=p\cdot q$ |
| 3    | 计算 n 的欧拉函数            | $\varphi(n)=(p-1)\cdot (q-1)$ |
| 4    | 选一个与   $\varphi(n)$  互质的整数 `e` | $1<e<\varphi(n)$ |
| 5    | 计算出 `e` 对于  $\varphi(n)$   的模反元素 `d` | $d\cdot e\ mod\ \varphi(n)=1$ |
| 6    | 公钥 | $KU=(e,n)$ |
| 7    | 私钥 | $KR=(d,n)$ |
| * | 使用公钥对明文 M 进行 **加密** | $M^{e}\ mod\ n = C$ |
| * | 使用私钥对密文 C 进行 **解密** | $C^{d}\ mod\ n = M$ |

-   $\varphi(n)$   : **欧拉函数** 是小于 `n` 的正整数中与 `n` 互质的数的数目 . 
    -   特性一 : 如果 `n` 为素数 , 则 $\varphi(n) = n-1$
    -   特性二 : 如果 `n` 可以分解成 2 个互质的整数之积 , 那么 n 的欧拉函数等于这两个因子的欧拉函数之积 . 
        -   若 `p`、`q` 互质 , 则有 : $\varphi(p\cdot q)=\varphi(p)\cdot \varphi(q)$
-   $ba\equiv 1(\ mod\ n)$ : **模反元素** 如果两个正整数 `a` 和 `n` 互质 , 那么一定可以找到 整数 `b`  , 使得 `b·a-1` 被 `n` 整除 . 则 `b` 就叫做 `a` 对于 `n` 的模方元素 . 
    -   也就是说有 : $({\color{Red} b}\cdot a)-1=K\cdot n$
    -   也可以记作 : ${\color{Red} b}\cdot a\ mod\ n=1$
        -   本步骤中进行相应参数的映射 :  ${\color{Red} b} => d\ ,\ a => e\ ,\ n => \varphi(n)$
        -   $(d\cdot e)-1=K\cdot \varphi(n)$
        -   $d\cdot e\ mod\ \varphi(n)=1$



#### 实例验证

```python
# server
p = 61
q = 53
n = 61*53 = 3233
φ(n) = φ(61*53) = 60*52 = 3120
# 取一个整数 e , 1 < e < 3120
e = 17
# 取 e 对于 φ(n) 的模方元素 , 17*d = K*3120 + 1 
d = 2753
# 共钥
KU = (17,3233)
# 私钥
KR = (2753,3233)

# 若明文 M = 65
(65**17)%3233 = 2790
# 加密得 密文 C = 2790
(2790**2753)%3233 = 65
```


#### 算法证明

1. 根据 加密  : $M^{e}\ mod\ n = C$      解密 : $C^{d}\ mod\ n = M$ ；因此我们只需要证明  $C^{d}\ mod\ n - M = 0$


2. 公式推导：

$$
\begin{aligned}
C^{d}\ \text{mod}\ n - M &= (M^{e}\ \text{mod}\ n)^{d}\ \text{mod}\ n -M \\
&= M^{e\cdot d}\ \text{mod}\ n -M \\
&= M^{K\cdot \varphi(n) + 1}\ \text{mod}\ n -M \\
&= M\cdot (M^{\varphi(n)})^{K}\ \text{mod}\ n -M \\
&= M\cdot (M^{\varphi(n)\cdot K}-1)\ \text{mod}\ n
\end{aligned}
$$


3.  这儿需要引入一个 [欧拉定理](https://en.wikipedia.org/wiki/Euler%27s_totient_function)  : 若 `n`,`a` 为正整数 , 且 `n`,`a` 互质 , 则有   $a^{\varphi(n)}\equiv 1\ (mod\ n)$   , 也可写成    $a^{\varphi(n)}\ mod\ n=1$
    1.  若 `a` 与 `n` 互质 , 且相差很大的时候 , 该公式也可以看作   $a^{\varphi(n)} = 1$  
    2.  根据欧拉定理衍生 , 若 `p` 为 素数 , 则根据 **欧拉函数** 可知 $\varphi(p) = p-1$  , 则有 [费马小定理](https://en.wikipedia.org/wiki/Fermat%27s_little_theorem)  : $a^{p-1}\equiv 1\ (mod\ p)$


4. 当 `M` 与 `n`  **互质**的时候  , 由于 `M` 比 `n` 小 , 因此可看作  $M\cdot (M^{\varphi(n)\cdot K}-1)\ mod\ n= M\cdot (1^{K}-1)\ mod\ n = 0$   [Proof using Euler's theorem](https://en.wikipedia.org/wiki/RSA_(cryptosystem)#cite_note-25)  , 推导证明成立 . 


5.  当 `M` 与 `n` **不互质**的时候 , 由于 `M` 比 `n` 小 , 且 `n` 的因子只有 {1 , q , p , n} 四个 , 则一定有正整数 (`H` 或 `Z`) 满足  $M=H\cdot p$ 或者 $M=Z\cdot q$  . 
    1.  假设 $M=H\cdot p$    , 由于 $M<n=p\cdot q$    , 则有  $H<q$ , 也有 M 与 q 互质 .
    2.  根据 费马小定理 可得  : $M^{q-1}\equiv 1\ mod\ q$
    3.  因为 M 与 q 互质 , 则 M **整数倍次方**也与 q 互质 , 即  $M^{K\cdot (p-1)}$  依然与  q   互质
    4.  则有 : $(M^{K\cdot (p-1)})^{(q-1)}\equiv 1\ mod\ q \equiv M^{K\cdot (p-1)\cdot (q-1)}$
    5.  上述推导也可写成  : $M^{K\cdot (p-1)\cdot (q-1)} -1 =M^{K\cdot \varphi(n)}-1= Y\cdot q$
    6.  将 1 与 5 推导 带入 公式中 :  $H\cdot p\cdot (Y\cdot q)mod\ n = H\cdot Y\cdot p\cdot q\ mod\ n = 0$
    7.  推导证明成立 . 




>   日常中 , 使用 RSA 算法 , 多数是搭配CA证书机制来作为交换密钥使用 . 
>
>    (1) 、服务端发送 CA 证书给客户端
>
>    (2) 、客户端收到 CA 证书后进行验证 , 并从证书中取出公钥 , 然后随机生成一个 密钥 K , 使用公钥加密得到 K\` , 并发送给服务端
>
>    (3) 、服务端收到 k\` 后用自己的私钥解密得到 k
>
>    (4) 、双方都得到了密钥 k  , 协商完成 . 



日常 CA 证书中的公钥 , 是需要使用 [ASN.1](https://en.wikipedia.org/wiki/ASN.1) 规范来进行编码的 . 

目前报道2009年12月12日为止 , 已经分解的最大整数 (232个十进制位 , 768个二进制位)  . 比它更大的因数分解 , 还没有被报道过 , 因此目前被破解的最长RSA密钥就是768位 . 




#### 如何防范偷窥  (嗅探) 

-   攻击方式1
    -   攻击者虽然可以监视网络流量拿到公钥 , 但是无法通过公钥推算出私钥 (这一点由于 RSA 算法保证) 
-   攻击方式2
    -   攻击者虽然可以监视网络流量拿到 K\` , 但是攻击者没有私钥 , 无法解密 K\` , 也就无法得到 K . 



#### 如何防范篡改  (假冒身份) 

-   攻击方式1
    -   如果攻击者在  (1)  篡改了数据 , 伪造了证书 , 那么客户端会在  (2)  发现 (这点由 CA 证书认证体系保证) 
-   攻击方式2
    -   如果攻击者在  (2) 篡改了数据 , 伪造了 K\` , 服务端使用私钥解密失败 (这点由 RSA 算法保证) 便会发现被攻击了









---
