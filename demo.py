#!/usr/bin/env python3
"""
Jinja2模板渲染系统演示脚本

这个脚本演示了如何使用模板渲染系统的各种功能
"""

import os
import sys
import json
from pathlib import Path

# 添加scripts目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from render_templates import TemplateRenderer


def print_banner(title: str):
    """打印标题横幅"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)


def demo_basic_usage():
    """演示基本用法"""
    print_banner("基本用法演示")
    
    # 初始化渲染器
    renderer = TemplateRenderer()
    renderer.setup_logging(debug=False)
    
    print("1. 初始化模板渲染器")
    print(f"   项目根目录: {renderer.project_root}")
    print(f"   模板目录: {renderer.templates_dir}")
    print(f"   环境配置目录: {renderer.envs_dir}")
    print(f"   输出目录: {renderer.rendered_dir}")
    print(f"   支持的分支: {', '.join(renderer.supported_branches)}")


def demo_environment_configs():
    """演示环境配置"""
    print_banner("环境配置演示")
    
    renderer = TemplateRenderer()
    renderer.setup_logging(debug=False)
    
    for branch in renderer.supported_branches:
        print(f"\n📋 {branch.upper()} 环境配置:")
        try:
            config = renderer.load_env_config(branch)
            
            # 显示主要配置项
            print(f"   环境: {config.get('environment', 'N/A')}")
            print(f"   调试模式: {config.get('debug', 'N/A')}")
            print(f"   版本: {config.get('version', 'N/A')}")
            
            # 数据库配置
            if 'database' in config:
                db = config['database']
                print(f"   数据库: {db.get('host', 'N/A')}:{db.get('port', 'N/A')}/{db.get('name', 'N/A')}")
            
            # API配置
            if 'api' in config:
                api = config['api']
                print(f"   API: {api.get('base_url', 'N/A')}")
            
            # 功能特性
            if 'features' in config:
                features = config['features']
                enabled_features = [k for k, v in features.items() if v is True]
                print(f"   启用的功能: {', '.join(enabled_features) if enabled_features else '无'}")
                
        except Exception as e:
            print(f"   ❌ 加载失败: {e}")


def demo_template_files():
    """演示模板文件"""
    print_banner("模板文件演示")
    
    renderer = TemplateRenderer()
    template_files = list(renderer.templates_dir.glob("**/*.j2"))
    
    if not template_files:
        print("❌ 没有找到模板文件")
        return
    
    print(f"📁 找到 {len(template_files)} 个模板文件:")
    
    for template_file in template_files:
        relative_path = template_file.relative_to(renderer.templates_dir)
        file_size = template_file.stat().st_size
        
        print(f"\n📄 {relative_path}")
        print(f"   大小: {file_size} 字节")
        
        # 显示文件前几行
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:5]  # 只显示前5行
                
            print("   内容预览:")
            for i, line in enumerate(lines, 1):
                preview = line.rstrip()[:60]  # 限制每行显示长度
                if len(line.rstrip()) > 60:
                    preview += "..."
                print(f"   {i:2d}: {preview}")
                
            if len(lines) == 5:
                print("      ...")
                
        except Exception as e:
            print(f"   ❌ 读取失败: {e}")


def demo_rendering_process():
    """演示渲染过程"""
    print_banner("模板渲染过程演示")
    
    renderer = TemplateRenderer()
    renderer.setup_logging(debug=False)
    
    # 选择一个分支进行演示
    demo_branch = "dev"
    print(f"🎯 演示分支: {demo_branch}")
    
    try:
        # 加载环境配置
        print(f"\n1. 加载 {demo_branch} 环境配置...")
        env_config = renderer.load_env_config(demo_branch)
        print(f"   ✅ 配置加载成功，包含 {len(env_config)} 个配置项")
        
        # 获取模板文件
        template_files = list(renderer.templates_dir.glob("**/*.j2"))
        if not template_files:
            print("   ❌ 没有找到模板文件")
            return
        
        print(f"\n2. 找到 {len(template_files)} 个模板文件")
        
        # 渲染每个模板
        print(f"\n3. 开始渲染模板...")
        for template_file in template_files:
            template_name = template_file.name
            print(f"\n   📝 渲染 {template_name}...")
            
            try:
                # 渲染模板
                rendered_content = renderer.render_template(
                    str(template_file), demo_branch, env_config
                )
                
                # 生成输出文件名
                output_filename = renderer.generate_output_filename(
                    str(template_file), demo_branch
                )
                
                print(f"      ✅ 渲染成功")
                print(f"      📄 输出文件: {output_filename}")
                print(f"      📏 内容长度: {len(rendered_content)} 字符")
                
                # 显示渲染内容的前几行
                lines = rendered_content.split('\n')[:3]
                print(f"      🔍 内容预览:")
                for line in lines:
                    preview = line[:50]
                    if len(line) > 50:
                        preview += "..."
                    print(f"         {preview}")
                
            except Exception as e:
                print(f"      ❌ 渲染失败: {e}")
        
    except Exception as e:
        print(f"❌ 演示过程出错: {e}")


def demo_output_structure():
    """演示输出结构"""
    print_banner("输出结构演示")
    
    renderer = TemplateRenderer()
    
    print("📁 预期的输出目录结构:")
    print("rendered/")
    
    for branch in renderer.supported_branches:
        print(f"├── {branch}/")
        
        # 获取模板文件并生成预期的输出文件名
        template_files = list(renderer.templates_dir.glob("**/*.j2"))
        for template_file in template_files:
            output_filename = renderer.generate_output_filename(str(template_file), branch)
            print(f"│   ├── {output_filename}")
    
    print("\n💡 提示:")
    print("   - 每个分支都有独立的输出目录")
    print("   - 输出文件名格式: <模板名>_<分支名>.py")
    print("   - 文件内容根据分支环境配置动态生成")


def demo_cli_commands():
    """演示CLI命令"""
    print_banner("CLI命令演示")
    
    print("🖥️  常用命令示例:")
    print()
    
    commands = [
        ("自动模式（推荐）", "python scripts/render_templates.py --auto"),
        ("渲染指定分支", "python scripts/render_templates.py --branch dev"),
        ("渲染所有分支", "python scripts/render_templates.py --all"),
        ("启用调试模式", "python scripts/render_templates.py --branch dev --debug"),
        ("指定项目目录", "python scripts/render_templates.py --project-root /path/to/project --branch dev"),
        ("运行测试", "python test_render.py"),
        ("查看帮助", "python scripts/render_templates.py --help"),
    ]
    
    for description, command in commands:
        print(f"📌 {description}:")
        print(f"   {command}")
        print()


def demo_ci_cd_integration():
    """演示CI/CD集成"""
    print_banner("CI/CD集成演示")
    
    print("🔄 CI/CD集成说明:")
    print()
    
    print("📋 GitLab CI (.gitlab-ci.yml):")
    print("   - 自动检测分支和新增.j2文件")
    print("   - 验证模板语法和配置文件格式")
    print("   - 执行模板渲染")
    print("   - 保存渲染结果为构建产物")
    print("   - 支持手动触发渲染所有分支")
    print()
    
    print("🐙 GitHub Actions (.github/workflows/render.yml):")
    print("   - 功能与GitLab CI类似")
    print("   - 支持工作流手动触发")
    print("   - 自动上传渲染结果为Artifacts")
    print()
    
    print("⚡ 触发条件:")
    print("   - 推送到 dev、sit、master 分支")
    print("   - 包含新增的 .j2 模板文件")
    print("   - 文件路径匹配: templates/**/*.j2")
    print()
    
    print("📊 输出产物:")
    print("   - rendered/ 目录中的所有渲染文件")
    print("   - 构建日志和渲染统计信息")
    print("   - 保留期限: 30天（GitLab CI）/ 30天（GitHub Actions）")


def main():
    """主函数"""
    print("🎭 Jinja2模板渲染系统演示")
    print("欢迎使用模板渲染系统！")
    
    # 检查项目结构
    project_root = Path(__file__).parent
    required_dirs = ["templates", "envs", "scripts"]
    missing_dirs = [d for d in required_dirs if not (project_root / d).exists()]
    
    if missing_dirs:
        print(f"\n❌ 缺少必要目录: {', '.join(missing_dirs)}")
        print("请确保项目结构完整")
        return
    
    # 运行各个演示
    demos = [
        demo_basic_usage,
        demo_environment_configs,
        demo_template_files,
        demo_rendering_process,
        demo_output_structure,
        demo_cli_commands,
        demo_ci_cd_integration,
    ]
    
    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"\n❌ 演示过程出错: {e}")
    
    # 结束语
    print_banner("演示结束")
    print("🎉 演示完成！")
    print()
    print("📚 更多信息:")
    print("   - 查看 README.md 了解项目概述")
    print("   - 查看 USAGE.md 了解详细使用说明")
    print("   - 运行 python test_render.py 进行功能测试")
    print("   - 运行 python scripts/render_templates.py --help 查看命令帮助")
    print()
    print("🚀 开始使用:")
    print("   python scripts/render_templates.py --auto")


if __name__ == "__main__":
    main()