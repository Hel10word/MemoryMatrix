#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import yaml
import json
import logging
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("md_normalizer")

# 获取脚本所在目录和项目根目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
# 配置文件默认路径
CONFIG_PATH = os.path.join(SCRIPT_DIR, "_config", "md_normalizer.yml")
if not os.path.exists(CONFIG_PATH):
    CONFIG_PATH = os.path.join(PROJECT_ROOT, "_scripts", "_config", "md_normalizer.yml")

# 默认配置
DEFAULT_CONFIG = {
    "punctuation_mapping": {},
    "punctuation_spacing": {"before_space": False, "after_space": False, "exceptions": {"no_space_after": [], "no_space_before": []}},
    "naming_rules": {"directories": {}, "files": {}, "attachments": {"dirname": "attachments"}},
    "metadata_rules": {"tags": {}},
    "processing_options": {"fix_punctuation": False, "fix_metadata": False, "fix_filenames": False, "report_only": True},
    "scan_directories": [],
    "exclude_directories": []
}

@dataclass
class ValidationIssue:
    """验证问题类"""
    file_path: str
    issue_type: str
    description: str
    fixable: bool
    extra_info: Dict = field(default_factory=dict)

@dataclass
class ValidationReport:
    """验证报告类"""
    issues: List[ValidationIssue] = field(default_factory=list)
    
    def add_issue(self, file_path, issue_type, description, fixable, extra_info=None):
        """添加问题到报告"""
        if extra_info is None:
            extra_info = {}
        self.issues.append(ValidationIssue(file_path, issue_type, description, fixable, extra_info))
    
    def get_issues_by_type(self):
        """按类型获取问题"""
        issues_by_type = {}
        for issue in self.issues:
            if issue.issue_type not in issues_by_type:
                issues_by_type[issue.issue_type] = []
            issues_by_type[issue.issue_type].append(issue)
        return issues_by_type
    
    def print_report(self):
        """打印验证报告"""
        if not self.issues:
            logger.info("未发现任何问题 , 文档格式已符合规范!")
            return
        
        logger.info("=== Markdown 文档规范化验证报告 ===")
        logger.info(f"总共发现 {len(self.issues)} 个问题:")
        
        issues_by_type = self.get_issues_by_type()
        for issue_type, issues in issues_by_type.items():
            logger.info(f"\n`{issue_type}`- {len(issues)} 个问题:")
            for i, issue in enumerate(issues, 1):
                logger.info(f"  {i}. {issue.description}")
                logger.info(f"     文件: {issue.file_path}")
                
                 # 对于标点符号问题，显示上下文
                if issue_type == "标点符号问题" and "context" in issue.extra_info:
                    logger.info(f"     上下文: {issue.extra_info['context']}")
                
                if issue.fixable:
                    logger.info(f"     可自动修复 : 是")
                    if "suggested_name" in issue.extra_info:
                        logger.info(f"     建议名称: {issue.extra_info['suggested_name']}")
                else:
                    logger.info(f"     可自动修复: 否")
        
        fixable_count = sum(1 for issue in self.issues if issue.fixable)
        if fixable_count > 0:
            logger.info(f"\n其中 {fixable_count} 个问题可自动修复 , 使用 --fix 选项来修复它们 .")

class MarkdownNormalizer:
    def __init__(self, config_path=None):
        """初始化规范化工具"""
        # 设置配置文件路径
        self.config_path = config_path if config_path else CONFIG_PATH
        # 设置项目根目录
        self.project_root = PROJECT_ROOT
        # 加载配置
        self.config = DEFAULT_CONFIG.copy()
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    custom_config = yaml.safe_load(f)
                    if custom_config:
                        # 直接使用配置文件，而不是合并
                        self.config = custom_config
                        logger.info(f"已加载配置文件: {self.config_path}")
            except Exception as e:
                logger.error(f"加载配置文件失败: {e}")
                logger.info("使用默认配置")
        else:
            logger.warning(f"配置文件不存在: {self.config_path}")
            logger.info("将生成默认配置文件")
            self.save_config(self.config_path)
        
        self.report = ValidationReport()
    
    def _merge_config(self, custom_config):
        """递归合并配置"""
        def merge_dicts(original, override):
            for key, value in override.items():
                if key in original and isinstance(original[key], dict) and isinstance(value, dict):
                    merge_dicts(original[key], value)
                else:
                    original[key] = value
        
        merge_dicts(self.config, custom_config)
    
    def save_config(self, config_path):
        """保存当前配置到文件"""
        # 确保目录存在
        os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
    
    def validate_punctuation(self, content, file_path):
        """检验标点符号问题并报告，确保行号准确"""
        # 创建行号映射
        protected_ranges = []
        
        # 保护区域的函数，记录起始和结束行
        def protect_region(pattern, text, name_prefix, is_dotall=False):
            protected_content = text
            flags = re.DOTALL if is_dotall else 0
            
            for i, match in enumerate(re.finditer(pattern, text, flags)):
                start_pos = match.start()
                end_pos = match.end()
                
                # 计算区域的起始行号
                lines_before = text[:start_pos].count('\n')
                start_line = lines_before + 1
                
                # 计算区域的结束行号
                matched_text = match.group(0)
                lines_in_match = matched_text.count('\n')
                end_line = start_line + lines_in_match
                
                # 记录保护区域
                protected_ranges.append((start_line, end_line))
                
                # 创建一个占位符，保持相同的换行符数量
                placeholder = f"__{name_prefix}_{i}__" + '\n' * lines_in_match
                
                # 替换区域，但保持行号一致
                protected_content = protected_content.replace(matched_text, placeholder, 1)
            
            return protected_content
        
        # 保护各种特殊区域
        protected_content = content
        
        # 1. 首先保护 YAML 元数据块（因为它通常在文件开头）
        yaml_pattern = r'^---\s*\n.*?\n---\s*\n'
        protected_content = protect_region(yaml_pattern, protected_content, "YAML_BLOCK", True)
        
        # 2. 保护代码块
        code_block_pattern = r'```.*?```'
        protected_content = protect_region(code_block_pattern, protected_content, "CODE_BLOCK", True)
        
        # 3. 保护内联代码
        inline_code_pattern = r'`[^`\n]+`'
        protected_content = protect_region(inline_code_pattern, protected_content, "INLINE_CODE")
        
        # 4. 保护 Markdown 链接 [text](url)
        md_link_pattern = r'\[(?:[^\]\\]|\\.)*\]\((?:[^)\\]|\\.)*\)'
        protected_content = protect_region(md_link_pattern, protected_content, "MD_LINK")
        
        # 5. 保护 Obsidian 内部链接 [[link]]
        obsidian_link_pattern = r'\[\[(?:[^\]\\]|\\.)*\]\]'
        protected_content = protect_region(obsidian_link_pattern, protected_content, "OB_LINK")
        
        # 6. 保护 HTML 标签
        html_tag_pattern = r'<[^>]+>'
        protected_content = protect_region(html_tag_pattern, protected_content, "HTML_TAG")
        
        # 获取标点符号映射
        mapping = self.config["punctuation_mapping"]
        
        # 找到所有中文标点符号
        lines = protected_content.split('\n')
        has_issues = False
        
        for line_num, line in enumerate(lines, 1):
            # 检查此行是否在保护区域内
            if any(start <= line_num <= end for start, end in protected_ranges):
                continue
                
            for cn_punct, en_punct in mapping.items():
                if cn_punct in line:
                    has_issues = True
                    
                    # 找到这一行中所有此标点的位置
                    positions = [m.start() for m in re.finditer(re.escape(cn_punct), line)]
                    for pos in positions:
                        # 提取上下文，展示问题标点的位置
                        context_start = max(0, pos - 15)
                        context_end = min(len(line), pos + 15)
                        context = line[context_start:context_end]
                        
                        # 高亮问题标点
                        highlighted = context.replace(cn_punct, f"【{cn_punct}】")
                        
                        self.report.add_issue(
                            file_path,
                            "标点符号问题",
                            f"第 {line_num} 行: 发现中文标点 '{cn_punct}' (应改为 '{en_punct}')",
                            True,
                            {
                                "line_number": line_num,
                                "position": pos,
                                "context": highlighted,
                                "chinese_punct": cn_punct,
                                "english_punct": en_punct
                            }
                        )
        
        return has_issues
    
    def normalize_punctuation(self, content):
        """规范化标点符号，通过配置控制空格处理，同时保留 Markdown 特殊语法结构"""
        if not self.config["processing_options"]["fix_punctuation"]:
            return content
        
        # 保护 Markdown 特殊结构
        protected_regions = []
        
        # 1. 保护代码块
        code_block_pattern = r'```.*?```'
        code_blocks = re.finditer(code_block_pattern, content, re.DOTALL)
        for i, match in enumerate(code_blocks):
            placeholder = f"__CODE_BLOCK_{i}__"
            protected_regions.append((placeholder, match.group(0)))
            content = content.replace(match.group(0), placeholder)
        
        # 2. 保护内联代码
        inline_code_pattern = r'`[^`]+`'
        inline_codes = re.finditer(inline_code_pattern, content)
        for i, match in enumerate(inline_codes):
            placeholder = f"__INLINE_CODE_{i}__"
            protected_regions.append((placeholder, match.group(0)))
            content = content.replace(match.group(0), placeholder)
        
        # 3. 保护 Markdown 链接 [text](url)
        md_link_pattern = r'\[(?:[^\]\\]|\\.)*\]\((?:[^)\\]|\\.)*\)'
        md_links = re.finditer(md_link_pattern, content)
        for i, match in enumerate(md_links):
            placeholder = f"__MD_LINK_{i}__"
            protected_regions.append((placeholder, match.group(0)))
            content = content.replace(match.group(0), placeholder)
        
        # 4. 保护 Obsidian 内部链接 [[link]]
        obsidian_link_pattern = r'\[\[(?:[^\]\\]|\\.)*\]\]'
        obsidian_links = re.finditer(obsidian_link_pattern, content)
        for i, match in enumerate(obsidian_links):
            placeholder = f"__OB_LINK_{i}__"
            protected_regions.append((placeholder, match.group(0)))
            content = content.replace(match.group(0), placeholder)
        
        # 5. 保护 YAML 元数据块
        yaml_pattern = r'^---\s*\n.*?\n---\s*\n'
        yaml_match = re.search(yaml_pattern, content, re.DOTALL)
        if yaml_match:
            placeholder = "__YAML_BLOCK__"
            protected_regions.append((placeholder, yaml_match.group(0)))
            content = content.replace(yaml_match.group(0), placeholder)
        
        # 获取标点符号映射
        mapping = self.config["punctuation_mapping"]
        pattern = '|'.join(map(re.escape, mapping.keys()))
        
        # 获取空格规则配置
        spacing_config = self.config["punctuation_spacing"]
        before_space = spacing_config["before_space"]
        after_space = spacing_config["after_space"]
        no_space_after = spacing_config["exceptions"]["no_space_after"]
        no_space_before = spacing_config["exceptions"]["no_space_before"]
        
        def replace_func(match):
            cn_punct = match.group(0)
            en_punct = mapping[cn_punct]
            
            # 获取前后字符的上下文
            start, end = match.span()
            before = content[start-1] if start > 0 else ''
            after = content[end] if end < len(content) else ''
            
            # 检查是否在列表项中
            # 获取当前行的开始位置
            line_start = content.rfind('\n', 0, start) + 1
            current_line_prefix = content[line_start:start]
            
            # 检查是否匹配列表项格式 (-, *, +, 1., 等)
            is_list_item = re.match(r'^\s*[-*+]|\s*\d+\.\s', current_line_prefix)
            
            # 检查前面的字符是否已经是空格或特殊字符
            prefix = ''
            if before_space and before and before not in [' ', '\n', '\t', '\r'] and en_punct not in no_space_before:
                # 不在行首添加空格，且不在列表项标记后添加额外空格
                if not (is_list_item and current_line_prefix.endswith(' ')):
                    line_start = content.rfind('\n', 0, start)
                    if line_start == -1 or start - line_start > 1:
                        prefix = ' '
            
            # 检查后面的字符是否已经是空格或特殊字符
            suffix = ''
            if after_space and after and after not in [' ', '\n', '\t', '\r'] and en_punct not in no_space_after:
                suffix = ' '
            
            return prefix + en_punct + suffix
        
        # 替换标点符号
        result = re.sub(pattern, replace_func, content)
        
        # 处理可能产生的多余空格
        # 1. 替换多个连续空格为单个空格
        result = re.sub(r' {2,}', ' ', result)
        # 2. 删除行首空格
        result = re.sub(r'\n +', '\n', result)
        # 3. 删除行尾空格
        result = re.sub(r' +\n', '\n', result)
        # 4. 修复列表项后的多余空格：确保列表项后只有一个空格
        result = re.sub(r'(^\s*[-*+]|\s*\d+\.) +', r'\1 ', result, flags=re.MULTILINE)
        
        # 还原受保护的区域
        for placeholder, original in protected_regions:
            result = result.replace(placeholder, original)
        
        return result
    
    def extract_yaml_metadata(self, content):
        """从Markdown内容中提取YAML元数据"""
        yaml_pattern = r"^---\s*\n(.*?)\n---\s*\n"
        match = re.search(yaml_pattern, content, re.DOTALL)
        
        if match:
            yaml_text = match.group(1)
            try:
                metadata = yaml.safe_load(yaml_text)
                if metadata is None:
                    metadata = {}
                return metadata, match.group(0), True
            except yaml.YAMLError:
                return {}, "", False
        
        return {}, "", False
    
    def validate_filename(self, file_path):
        """验证文件名是否符合规范"""
        path = Path(file_path)
        filename = path.name
        
        # 检查文件名中是否有空格
        if self.config["naming_rules"]["files"]["no_spaces"] and " " in filename:
            self.report.add_issue(
                file_path,
                "文件命名问题",
                f"文件名 '{filename}' 包含空格",
                True,
                {"suggested_name": filename.replace(" ", "")}
            )
        
        # 检查文件名格式是否符合规范
        pattern = self.config["naming_rules"]["files"]["pattern"]
        if not re.match(pattern, filename):
            self.report.add_issue(
                file_path,
                "文件命名问题",
                f"文件名 '{filename}' 不符合规范 (应匹配模式: {pattern})",
                False
            )
        
        # 检查特殊规则
        if filename.endswith(".excalidraw"):
            excalidraw_pattern = self.config["naming_rules"]["files"]["special_rules"]["excalidraw"]["pattern"]
            if not re.match(excalidraw_pattern, filename):
                self.report.add_issue(
                    file_path,
                    "Excalidraw命名问题",
                    f"Excalidraw文件 '{filename}' 不符合命名规范",
                    False
                )
    
    def validate_directory(self, dir_path):
        """验证目录名是否符合规范"""
        path = Path(dir_path)
        dirname = path.name
        
        # 跳过根目录
        if not dirname:
            return
        
        # 跳过 attachments 目录
        if dirname == self.config["naming_rules"]["attachments"]["dirname"]:
            return
        
        # 检查目录名中是否有空格
        if self.config["naming_rules"]["directories"]["no_spaces"] and " " in dirname:
            self.report.add_issue(
                dir_path,
                "目录命名问题",
                f"目录名 '{dirname}' 包含空格",
                True,
                {"suggested_name": dirname.replace(" ", "")}
            )
        
        # 检查目录名格式是否符合规范
        pattern = self.config["naming_rules"]["directories"]["pattern"]
        if not re.match(pattern, dirname):
            self.report.add_issue(
                dir_path,
                "目录命名问题",
                f"目录名 '{dirname}' 不符合规范 (应采用驼峰命名法)",
                False
            )
    
    def validate_attachment_files(self, attachment_dir):
        """验证附件目录中的文件命名"""
        if not os.path.exists(attachment_dir):
            return
        
        for file in os.listdir(attachment_dir):
            file_path = os.path.join(attachment_dir, file)
            if os.path.isfile(file_path):
                # 检查文件名中是否有空格
                if " " in file:
                    self.report.add_issue(
                        file_path,
                        "附件命名问题",
                        f"附件文件名 '{file}' 包含空格",
                        True,
                        {"suggested_name": file.replace(" ", "")}
                    )
                
                # 检查文件名格式是否符合规范
                pattern = self.config["naming_rules"]["attachments"]["pattern"]
                if not re.match(pattern, file):
                    self.report.add_issue(
                        file_path,
                        "附件命名问题",
                        f"附件文件名 '{file}' 不符合规范",
                        False
                    )
    
    def validate_metadata_tags(self, metadata, file_path):
        """验证元数据中的标签是否符合规范"""
        if 'tags' not in metadata or not metadata['tags']:
            return
        
        tags = metadata['tags']
        if not isinstance(tags, list):
            self.report.add_issue(
                file_path,
                "元数据问题",
                "标签必须是列表格式",
                False
            )
            return
        
        tag_rules = self.config["metadata_rules"]["tags"]
        
        for tag in tags:
            # 如果需要小写
            if tag_rules["lowercase"] and any(c.isupper() for c in tag):
                self.report.add_issue(
                    file_path,
                    "元数据问题",
                    f"标签 '{tag}' 应使用小写字母",
                    True,
                    {"tag": tag, "suggested_tag": tag.lower()}
                )
            
            # 检查单词分隔符
            word_separator = tag_rules["word_separator"]
            if " " in tag:
                self.report.add_issue(
                    file_path,
                    "元数据问题",
                    f"标签 '{tag}' 中的单词应使用 '{word_separator}' 分隔，而不是空格",
                    True,
                    {"tag": tag, "suggested_tag": tag.replace(" ", word_separator)}
                )
    
    def validate_excalidraw_references(self, md_content, md_file_path):
        """验证Excalidraw引用"""
        filename = os.path.basename(md_file_path)
        
        # 如果是Excalidraw文件，检查是否在对应的md文件中被引用
        if filename.endswith(".excalidraw.md"):
            base_name = filename[:-3]  # 移除.md扩展名
            excalidraw_file = os.path.join(os.path.dirname(md_file_path), base_name)
            
            if os.path.exists(excalidraw_file):
                if not f"[[{base_name}]]" in md_content:
                    self.report.add_issue(
                        md_file_path,
                        "Excalidraw引用问题",
                        f"Excalidraw文件 '{base_name}' 在对应的Markdown文件中未被引用",
                        False
                    )
    
    def process_markdown_file(self, file_path):
        """处理单个Markdown文件，进行验证和修正"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 验证文件名
            self.validate_filename(file_path)
            
            # 提取和验证YAML元数据
            metadata, yaml_block, has_yaml = self.extract_yaml_metadata(content)
            if has_yaml:
                self.validate_metadata_tags(metadata, file_path)
            
            # 验证Excalidraw引用
            self.validate_excalidraw_references(content, file_path)
            
            # 检查附件目录
            file_dir = os.path.dirname(file_path)
            attachments_dir = os.path.join(file_dir, self.config["naming_rules"]["attachments"]["dirname"])
            if os.path.exists(attachments_dir):
                self.validate_attachment_files(attachments_dir)
                
            # 验证标点符号并生成报告
            self.validate_punctuation(content, file_path)
            
            # 规范化标点符号
            if self.config["processing_options"]["fix_punctuation"] and not self.config["processing_options"]["report_only"]:
                new_content = self.normalize_punctuation(content)
                if new_content != content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    logger.info(f"已修复标点符号: {file_path}")
        
        except Exception as e:
            logger.error(f"处理文件 {file_path} 时出错: {str(e)}")
            self.report.add_issue(
                file_path,
                "处理错误",
                f"处理时出错: {str(e)}",
                False
            )
    
    def process_directory(self, directory):
        """递归处理目录中的所有Markdown文件"""
        # 排除指定目录
        base_dir = os.path.basename(directory)
        if base_dir in self.config["exclude_directories"]:
            logger.info(f"跳过排除目录: {directory}")
            return
        
        logger.info(f"处理目录: {directory}")
        
        for root, dirs, files in os.walk(directory):
            # 过滤排除目录
            dirs[:] = [d for d in dirs if d not in self.config["exclude_directories"]]
            
            # 验证目录名
            for d in dirs:
                dir_path = os.path.join(root, d)
                self.validate_directory(dir_path)
            
            # 处理Markdown文件
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    self.process_markdown_file(file_path)
    
    def run(self, path=None):
        """运行规范化工具"""
        if path:
            path = Path(path)
            if path.is_file() and path.suffix == '.md':
                self.process_markdown_file(path)
            elif path.is_dir():
                self.process_directory(path)
            else:
                logger.error(f"错误: {path} 不是有效的Markdown文件或目录")
        else:
            # 处理配置中指定的所有目录
            for dir_name in self.config["scan_directories"]:
                dir_path = os.path.join(self.project_root, dir_name)
                if os.path.exists(dir_path):
                    self.process_directory(dir_path)
                else:
                    logger.warning(f"指定的目录不存在: {dir_path}")
        
        # 输出验证报告
        self.report.print_report()
        
        return self.report

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Markdown文档规范化工具')
    parser.add_argument('path', nargs='?', help='要处理的目录或文件路径（可选）')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--generate-config', help='生成默认配置文件')
    parser.add_argument('--fix', action='store_true', help='自动修复问题')
    args = parser.parse_args()
    
    # 生成默认配置
    if args.generate_config:
        normalizer = MarkdownNormalizer()
        normalizer.save_config(args.generate_config)
        logger.info(f"已生成默认配置文件: {args.generate_config}")
        return
    
    # 初始化工具
    normalizer = MarkdownNormalizer(args.config)
    
    # 设置处理选项
    if args.fix:
        normalizer.config["processing_options"]["report_only"] = False
    
    # 运行工具
    normalizer.run(args.path)

if __name__ == "__main__":
    main()