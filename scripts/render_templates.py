#!/usr/bin/env python3
"""
Jinja2模板自动渲染脚本

功能：
1. 检测Git提交中新增的.j2模板文件
2. 根据分支名加载对应的环境配置
3. 渲染模板并生成Python文件
4. 支持手动和自动执行模式
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

import git
from jinja2 import Environment, FileSystemLoader, TemplateNotFound


class TemplateRenderer:
    """Jinja2模板渲染器"""
    
    def __init__(self, project_root: str = None):
        """初始化渲染器
        
        Args:
            project_root: 项目根目录路径，默认为当前脚本的上级目录
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent
        
        self.project_root = Path(project_root)
        self.templates_dir = self.project_root / "templates"
        self.envs_dir = self.project_root / "envs"
        self.rendered_dir = self.project_root / "rendered"
        
        # 支持的分支列表
        self.supported_branches = ["dev", "sit", "master"]
        
        # 初始化Jinja2环境
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # 添加自定义过滤器
        self._add_custom_filters()
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
    
    def _add_custom_filters(self):
        """添加自定义Jinja2过滤器"""
        def strftime_filter(value, format_string="%Y-%m-%d %H:%M:%S"):
            """日期时间格式化过滤器"""
            if value == "now":
                return datetime.now().strftime(format_string)
            elif isinstance(value, datetime):
                return value.strftime(format_string)
            else:
                return str(value)
        
        # 注册过滤器
        self.jinja_env.filters['strftime'] = strftime_filter
    
    def setup_logging(self, debug: bool = False):
        """设置日志配置"""
        level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def get_current_branch(self) -> str:
        """获取当前Git分支名"""
        try:
            repo = git.Repo(self.project_root)
            return repo.active_branch.name
        except Exception as e:
            self.logger.error(f"获取当前分支失败: {e}")
            return ""
    
    def get_added_j2_files(self) -> List[str]:
        """获取最近提交中新增的.j2文件列表"""
        try:
            repo = git.Repo(self.project_root)
            
            # 获取最近一次提交的差异
            if len(list(repo.iter_commits())) < 2:
                # 如果只有一次提交，比较与空树的差异
                diff = repo.head.commit.diff(None)
            else:
                # 比较最近两次提交
                diff = repo.head.commit.diff('HEAD~1')
            
            added_j2_files = []
            for item in diff:
                # 检查是否为新增文件且为.j2文件
                if item.change_type == 'A' and item.a_path.endswith('.j2'):
                    # 确保文件在templates目录下
                    if item.a_path.startswith('templates/'):
                        added_j2_files.append(item.a_path)
            
            self.logger.info(f"检测到新增的.j2文件: {added_j2_files}")
            return added_j2_files
            
        except Exception as e:
            self.logger.error(f"获取新增.j2文件失败: {e}")
            return []
    
    def load_env_config(self, branch: str) -> Dict[str, Any]:
        """加载指定分支的环境配置
        
        Args:
            branch: 分支名
            
        Returns:
            环境配置字典
        """
        config_file = self.envs_dir / f"{branch}.json"
        
        if not config_file.exists():
            raise FileNotFoundError(f"环境配置文件不存在: {config_file}")
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.logger.debug(f"成功加载 {branch} 环境配置")
            return config
            
        except json.JSONDecodeError as e:
            raise ValueError(f"环境配置文件格式错误 {config_file}: {e}")
    
    def generate_output_filename(self, template_path: str, branch: str) -> str:
        """生成输出文件名
        
        Args:
            template_path: 模板文件路径 (如: templates/validate_config.py.j2)
            branch: 分支名
            
        Returns:
            输出文件名 (如: validate_config_dev.py)
        """
        # 获取模板文件名（去掉路径和.j2扩展名）
        template_file = Path(template_path).name  # 获取文件名: validate_config.py.j2
        
        # 去掉.j2扩展名
        if template_file.endswith('.j2'):
            template_file = template_file[:-3]  # 去掉.j2: validate_config.py
        
        # 如果文件名以.py结尾，去掉.py然后加上分支名再加.py
        if template_file.endswith('.py'):
            base_name = template_file[:-3]  # 去掉.py: validate_config
            output_filename = f"{base_name}_{branch}.py"
        else:
            # 如果不是.py文件，直接加上分支名和.py
            output_filename = f"{template_file}_{branch}.py"
        
        return output_filename
    
    def render_template(self, template_path: str, branch: str, env_config: Dict[str, Any]) -> str:
        """渲染单个模板
        
        Args:
            template_path: 模板文件路径
            branch: 分支名
            env_config: 环境配置
            
        Returns:
            渲染后的内容
        """
        try:
            # 获取相对于templates目录的模板路径
            relative_path = str(Path(template_path).relative_to(self.templates_dir))
            
            # 加载模板
            template = self.jinja_env.get_template(relative_path)
            
            # 渲染模板
            rendered_content = template.render(**env_config)
            
            self.logger.debug(f"成功渲染模板: {template_path}")
            return rendered_content
            
        except TemplateNotFound:
            raise FileNotFoundError(f"模板文件不存在: {template_path}")
        except Exception as e:
            raise RuntimeError(f"渲染模板失败 {template_path}: {e}")
    
    def save_rendered_file(self, content: str, output_path: Path):
        """保存渲染后的文件
        
        Args:
            content: 渲染后的内容
            output_path: 输出文件路径
        """
        # 确保输出目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.logger.info(f"已保存渲染文件: {output_path}")
    
    def render_templates_for_branch(self, branch: str, template_files: List[str] = None) -> int:
        """为指定分支渲染模板
        
        Args:
            branch: 分支名
            template_files: 要渲染的模板文件列表，如果为None则渲染所有模板
            
        Returns:
            成功渲染的文件数量
        """
        if branch not in self.supported_branches:
            self.logger.warning(f"不支持的分支: {branch}")
            return 0
        
        try:
            # 加载环境配置
            env_config = self.load_env_config(branch)
            
            # 确定要渲染的模板文件
            if template_files is None:
                # 渲染所有模板文件
                template_files = list(self.templates_dir.glob("**/*.j2"))
                template_files = [str(f) for f in template_files]
            
            if not template_files:
                self.logger.info(f"没有找到需要渲染的模板文件")
                return 0
            
            rendered_count = 0
            
            for template_path in template_files:
                try:
                    # 渲染模板
                    rendered_content = self.render_template(template_path, branch, env_config)
                    
                    # 生成输出文件名
                    output_filename = self.generate_output_filename(template_path, branch)
                    output_path = self.rendered_dir / branch / output_filename
                    
                    # 保存渲染后的文件
                    self.save_rendered_file(rendered_content, output_path)
                    
                    rendered_count += 1
                    
                except Exception as e:
                    self.logger.error(f"渲染模板失败 {template_path}: {e}")
                    continue
            
            self.logger.info(f"分支 {branch} 成功渲染 {rendered_count} 个模板文件")
            return rendered_count
            
        except Exception as e:
            self.logger.error(f"为分支 {branch} 渲染模板失败: {e}")
            return 0
    
    def auto_render(self) -> bool:
        """自动渲染模式：检测当前分支和新增的模板文件"""
        # 获取当前分支
        current_branch = self.get_current_branch()
        
        if not current_branch:
            self.logger.error("无法获取当前分支")
            return False
        
        if current_branch not in self.supported_branches:
            self.logger.info(f"当前分支 {current_branch} 不在支持列表中，跳过渲染")
            return True
        
        # 获取新增的.j2文件
        added_j2_files = self.get_added_j2_files()
        
        if not added_j2_files:
            self.logger.info("没有检测到新增的.j2文件，跳过渲染")
            return True
        
        # 渲染新增的模板文件
        rendered_count = self.render_templates_for_branch(current_branch, added_j2_files)
        
        return rendered_count > 0
    
    def render_all_branches(self) -> bool:
        """渲染所有支持分支的模板"""
        total_rendered = 0
        
        for branch in self.supported_branches:
            try:
                rendered_count = self.render_templates_for_branch(branch)
                total_rendered += rendered_count
            except Exception as e:
                self.logger.error(f"渲染分支 {branch} 失败: {e}")
                continue
        
        self.logger.info(f"总共渲染了 {total_rendered} 个文件")
        return total_rendered > 0


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Jinja2模板自动渲染脚本")
    parser.add_argument(
        "--branch", 
        type=str, 
        help="指定要渲染的分支名 (dev/sit/master)"
    )
    parser.add_argument(
        "--all", 
        action="store_true", 
        help="渲染所有支持分支的模板"
    )
    parser.add_argument(
        "--auto", 
        action="store_true", 
        help="自动模式：检测当前分支和新增的.j2文件"
    )
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="启用调试模式"
    )
    parser.add_argument(
        "--project-root", 
        type=str, 
        help="项目根目录路径"
    )
    
    args = parser.parse_args()
    
    # 初始化渲染器
    renderer = TemplateRenderer(args.project_root)
    renderer.setup_logging(args.debug)
    
    try:
        if args.all:
            # 渲染所有分支
            success = renderer.render_all_branches()
        elif args.branch:
            # 渲染指定分支
            rendered_count = renderer.render_templates_for_branch(args.branch)
            success = rendered_count > 0
        else:
            # 默认自动模式
            success = renderer.auto_render()
        
        if success:
            renderer.logger.info("模板渲染完成")
            sys.exit(0)
        else:
            renderer.logger.error("模板渲染失败")
            sys.exit(1)
            
    except Exception as e:
        renderer.logger.error(f"执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()