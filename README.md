# MemoryMatrix

**MemoryMatrix** 是一个个人知识管理系统 , 采用结构化与关联式相结合的方法存储和组织知识 , 思想和灵感 . 这个数字大脑旨在捕捉思维碎片 , 构建知识网络 , 并使信息可被高效检索 , 连接和扩展 .

> 知识不是力量 , 知识的组织才是力量 .


[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

[![Powered by: Obsidian](https://img.shields.io/badge/Powered%20by-Obsidian-purple.svg)](https://github.com/obsidianmd/obsidian-releases)

[![Powered by: Excalidraw](https://img.shields.io/badge/Powered%20by-Excalidraw-CCCCFF.svg)](https://github.com/excalidraw/excalidraw)

## ✨ 核心特性

- 双向链接 : 利用 **Obsidian** 的双向链接功能构建知识网络

- 多维分类 : 一篇文章可横跨多个知识领域

- 标签系统 : 使用标签实现灵活分类和快速检索

- 知识地图 : 通过MOCs(内容地图)导航复杂知识领域

- 持续演进 : 设计支持知识体系随时间不断成长和重组

## 🔧 技术实现

- Markdown : 所有内容使用Markdown格式存储

- Obsidian : 主要知识管理工具 , 提供双向链接和图谱可视化

- Git : 版本控制和跨设备同步

- GitHub Pages : 公开展示

- GitHub Actions : 自动化发布流程

## 🧠 项目结构

``` 
MemoryMatrix/
├── _scripts/                 # 脚本文件
├── _templates/               # 文档模板
├── .obsidian/                # obsidian 相关的数据
├── Knowledge Maps/           # 知识关联与导航
│   └── [MOCs , 索引与术语表]
├── KnowledgeMatrix/          # 结构化知识主体
│   └── [按领域组织的各类知识]
├── ThoughtFragments/         # 日常思考与灵感记录
│   └── [按时间和主题组织]
├── WisdomVault/              # 有价值的知识
│   └── [有价值需要记录的内容]
├── LifeDashboard/            # 个人计划与待办事项
│   └── [个人计划与待办事项]
├── README.md                 # 仓库介绍
└── LICENSE                   # 开源协议
```


## ✒ 格式

- **Data** : yyyy-MM-dd
- **Time** : HH:mm
- **Datatime** : yyyy-MM-ddTHH:mm
- `元数据` 中所有的英文 `tags` 使用 小写字母 , 单词间通过 `-` 分隔 , 分类使用 `/`
- `文件夹` 英文使用驼峰命名 , 文件夹名称**不能有空格**
- **attachments** : 为当前目录内文章相应的 附件 文件夹 , 里面存放 文章引用的图片 与 附件
- 标点符号 : 尽量全文使用英文标点符号 , 例如 `,` `.` `:` `!` `(` `)` 等等

> 后续编写了 ./\_scripts/md_normalizer.py 脚本 , 可通过 `python /_scripts/md_normalizer.py` 命令来执行规范校验脚本 , 通过 `python _scripts\md_normalizer.py --fix` 来应用部分规范 .

## 📖 使用方法

```
# 核心元数据 (所有文档通用)
---
id: "unique-id"                    # 知识点唯一标识符
aliases: [别名1, 别名2]             # 文档的其他引用名称
related: [文档1-id, 文档2-id]       # 相关文档ID
title: "文档标题"                   # 文档的主标题
created: 2024-06-08T19:49          # 创建日期 , yyyy-MM-ddTHH:mm 格式
author: "你的名字"                  # 作者名称
categories: [主类别/子类别]          # 分类路径 , 反映目录结构
status: draft|published|archived   # 文档状态 草稿/已发布/已归档
tags: [标签1, 标签2, 标签3]          # 标签列表 , 用于搜索和过滤
summary: ""                        # 用于预览和搜索结果
toc: true                          # 是否显示目录
---



# Demo
---
id: "9fa8f1b4-a060-42b9-8286-68bedbbb8e03"
aliases:
  - "9fa8f1b4-a060-42b9-8286-68bedbbb8e03"
  - "Demo"
title: Demo
created: 2025-02-26T19:49
author: hel10word
status: draft
tags:
  - #status/draft
summary: 这是一段简短的摘要 , 描述文档的主要内容
---


# 后续使用 Templaters 插件 , 具体的模板文件在 _templates 目录中

```


## 📄 许可协议

除特别注明外 , 本知识库内容采用 [知识共享署名-非商业性使用-相同方式共享 4.0 国际许可协议](https://creativecommons.org/licenses/by-nc-sa/4.0/) 进行许可 .

---

<p align="center">构建于神经元间隙的数字思维宫殿</p>