---
<%*
/* 模板版本：1.2 | 最后更新：2025-02-27 */

// 生成UUID（兼容模式）
let uuid;
try {
    uuid = crypto.randomUUID().trim();
} catch (error) {
    // 备用UUID生成方案
    uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => 
        (c === 'x' ? (Math.random()*16|0) : (Math.random()*4|0 +8)).toString(16)
    );
}

// 状态选择器
const status = await (async () => {
    // 定义带完整状态信息的选项
    const statusOptions = [
        { 
            display: "📝 草稿 | 可继续编辑", 
            value: "draft",
            hint: "初始创作阶段"
        },
        {
            display: "🚀 已发布 | 对外可见",
            value: "published",
            hint: "完成并公开的内容"
        },
        {
            display: "🗄️ 已归档 | 只读状态",
            value: "archived",
            hint: "历史文档封存"
        }
    ];

    return await tp.system.suggester(
        // 显示项数组（直接使用text字段）
        statusOptions.map(opt => `${opt.display}\n↳ ${opt.hint}`),
        // 实际值数组
        statusOptions.map(opt => opt.value),
        // 配置参数
        true,  // 启用多行
        "选择文档状态：",
        "draft"  // 默认值
    );
})();
%>

id: <% uuid %>
aliases:
  - <% uuid %>
  - <% tp.file.title %>
title: <% tp.file.title %>
created: <% tp.file.creation_date("YYYY-MM-DDTHH:mm") %>
author: hel10word
status: <% status %>
tags:
summary: <% await tp.system.prompt("请输入摘要（50字内）", "这是一段简短的摘要，描述文档的主要内容") %>
toc: true
---