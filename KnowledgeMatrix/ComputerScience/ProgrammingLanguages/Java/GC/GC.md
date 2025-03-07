---
id: 2d1d02dc-2ecd-452c-83dd-1ec3627127ae
aliases:
  - 2d1d02dc-2ecd-452c-83dd-1ec3627127ae
  - GC
title: GC
created: 2025-03-04T19:51
author: hel10word
status: draft
tags:
  - status/draft
  - domain/programming
  - gc
  - java
summary: 这是一段简短的摘要 , 描述文档的主要内容
---

# GC

| 收集器                | 作用区域 | 采用算法        | 运行方式 | 适用场景                           |
| ------------------ | ---- | ----------- | ---- | ------------------------------ |
| Serial New         | 新生代  | 复制          | 单线程  | 在单核CPU的情况下 , 性能较高              |
| ParNew             | 新生代  | 复制          | 多线程  | Serial New的多线程版本 , 适合多核CPU的情况下 |
| Parallel Scanvenge | 新生代  | 复制          | 单线程  | 多线程收集 , 多核环境下效率要比serial高       |
| Serial Old         | 老年代  | 标记-整理       | 多线程  | 在单核CPU的情况下 , 性能较高              |
| CMS                | 老年代  | 标记清除法+标记整理法 | 多线程  | 以提高系统的吞吐量为主                    |
| Parallel Old       | 老年代  | 标记-整理       | 多线程  | 和ParNew一样 , 但是无法和CMS一起工作       |
| G1                 | 通用   | 复制          | 多线程  | 以降低STW的时间为主                    |

## GC日志的查看

```java
// Jdk1.8 hotspot虚拟机 VM 参数：-Xmx30M -Xms30M -XX:+PrintGCDetails
// 参数解释： -Xmx 最大堆大小 -Xms 最小堆大小 --XX打印 GC 细节

private static final int _1MB = 1024 * 1024;
public static void main(String[] args) {
	byte[] buffer1 = new byte[_1MB * 2];
	byte[] buffer2 = new byte[_1MB * 2];
	byte[] buffer3 = new byte[_1MB * 2];
	System.gc();
}
/**
* 打印日志
* [GC (System.gc()) [PSYoungGen: 8180K->824K(9216K)] 8180K->6976K(29696K), 0.0032798 secs] [Times: user=0.00 sys=0.00, real=0.00 secs] 
* [Full GC (System.gc()) [PSYoungGen: 824K->0K(9216K)] [ParOldGen: 6152K->6766K(20480K)] 6976K->6766K(29696K), [Metaspace: 3274K->3274K(1056768K)], 0.0045226 secs] [Times: user=0.00 sys=0.00, real=0.00 secs] 
* Heap
*  PSYoungGen      total 9216K, used 166K [0x00000000ff600000, 0x0000000100000000, 0x0000000100000000)
*   eden space 8192K, 2% used [0x00000000ff600000,0x00000000ff629820,0x00000000ffe00000)
*   from space 1024K, 0% used [0x00000000ffe00000,0x00000000ffe00000,0x00000000fff00000)
*   to   space 1024K, 0% used [0x00000000fff00000,0x00000000fff00000,0x0000000100000000)
*  ParOldGen       total 20480K, used 6766K [0x00000000fe200000, 0x00000000ff600000, 0x00000000ff600000)
*   object space 20480K, 33% used [0x00000000fe200000,0x00000000fe89b930,0x00000000ff600000)
*  Metaspace       used 3286K, capacity 4496K, committed 4864K, reserved 1056768K
*   class space    used 357K, capacity 388K, committed 512K, reserved 1048576K
*/
```

### 相关解释

> \[GC (System.gc()) \[PSYoungGen: 8180K->824K(9216K)\] 8180K->6976K(29696K), 0.0032798 secs\] \[Times: user=0.00 sys=0.00, real=0.00 secs\] 

第一行中的 GC 代表部分 GC 可能是只收集了新生代 , 后面的 `System.gc()` 则代表此次 GC 的调用方式 , 如果是空间不足的话 这里会显示 **Allocation Failure** , 然后 \[\]中括号括起来的部分是此次GC清理的区域 , 可以看到是 PSYoungGen , 代表此次清理的是 Gen 区 , 8180K->824K(9216K) 则是代表**清理前**是8180K , **清理后**是824K , 总共9216K , 中括号之外的则是代表 总内存清理前大小->总内存清理后大小(总内存大小) , 再之后的 0.0032798 secs 则是代表GC花费的时间 .

> \[Full GC (System.gc()) \[PSYoungGen: 824K->0K(9216K)\] \[ParOldGen: 6152K->6766K(20480K)\] 6976K->6766K(29696K), \[Metaspace: 3274K->3274K(1056768K)\], 0.0045226 secs\] \[Times: user=0.00 sys=0.00, real=0.00 secs\]

第一行中的 Full GC 代表该 GC 收集了所有的区域 (包括新生代 , 老年代 , 元空间) , 其他的和上面讲的一样 , 就不多在叙述 , 但是需要注意的是 , Full GC 一定会导致 STW .

`PSYoungGen` 代表新生代用的是 Px 收集器 ParOldGen 代表老年代用的是 下 收集器 当我把最大最小堆设置为 30M 后可以发现 , 默认情况下新生代与老年代的**空间比例**是 **1:2** 所以可以看到 新生代 是 10M , 而老年代则是 20M . 当然 , 我这里明明显示的是 9216K=9M , 我却说的10M , 这不是睁着眼睛说瞎话么 ? 

这前面讲过 , 这里再复习一下 新生代中又被划分为 eden 区和两个 survivor 区 , 默认这三个区的比例是 8:1:1 , 每次是会使用 eden 和其中一个 survivor 区 , 所以这里显示的才是 9M .








---
可使用 [![](https://img.shields.io/badge/Excalidraw-CCCCFF?style=for-the-badge&logo=excalidraw&logoColor=333&logoWidth=20&labelColor=CCCCFF)](https://excalidraw.com/) 工具打开本文的 [原型图文件](../KnowledgeMatrix/ComputerScience/Network/网络数据包封装与传输/attachments/excalidraw.excalidraw)




