#!/usr/bin/env python3
"""
模板渲染系统测试脚本

用于验证模板渲染功能是否正常工作
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

# 添加scripts目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from render_templates import TemplateRenderer


class RenderTester:
    """渲染测试器"""
    
    def __init__(self):
        """初始化测试器"""
        self.project_root = Path(__file__).parent
        self.renderer = TemplateRenderer(str(self.project_root))
        self.renderer.setup_logging(debug=True)
        self.test_results = []
    
    def test_environment_configs(self) -> bool:
        """测试环境配置文件"""
        print("🧪 测试环境配置文件...")
        
        success = True
        for branch in self.renderer.supported_branches:
            try:
                config = self.renderer.load_env_config(branch)
                print(f"  ✅ {branch}.json 加载成功")
                
                # 验证必要字段
                required_fields = ["database", "api", "environment", "debug"]
                for field in required_fields:
                    if field not in config:
                        print(f"  ❌ {branch}.json 缺少必要字段: {field}")
                        success = False
                    else:
                        print(f"    ✓ 字段 {field} 存在")
                        
            except Exception as e:
                print(f"  ❌ {branch}.json 加载失败: {e}")
                success = False
        
        self.test_results.append(("环境配置测试", success))
        return success
    
    def test_template_syntax(self) -> bool:
        """测试模板语法"""
        print("\n🧪 测试模板语法...")
        
        success = True
        template_files = list(self.renderer.templates_dir.glob("**/*.j2"))
        
        if not template_files:
            print("  ⚠️  没有找到模板文件")
            self.test_results.append(("模板语法测试", False))
            return False
        
        for template_file in template_files:
            try:
                # 获取相对路径
                relative_path = str(template_file.relative_to(self.renderer.templates_dir))
                
                # 尝试加载模板
                template = self.renderer.jinja_env.get_template(relative_path)
                print(f"  ✅ {relative_path} 语法正确")
                
            except Exception as e:
                print(f"  ❌ {relative_path} 语法错误: {e}")
                success = False
        
        self.test_results.append(("模板语法测试", success))
        return success
    
    def test_template_rendering(self) -> bool:
        """测试模板渲染"""
        print("\n🧪 测试模板渲染...")
        
        success = True
        template_files = list(self.renderer.templates_dir.glob("**/*.j2"))
        
        for branch in self.renderer.supported_branches:
            print(f"\n  测试分支: {branch}")
            
            try:
                # 加载环境配置
                env_config = self.renderer.load_env_config(branch)
                
                for template_file in template_files:
                    try:
                        # 渲染模板
                        rendered_content = self.renderer.render_template(
                            str(template_file), branch, env_config
                        )
                        
                        # 检查渲染结果
                        if rendered_content and len(rendered_content.strip()) > 0:
                            template_name = template_file.name
                            print(f"    ✅ {template_name} 渲染成功")
                        else:
                            print(f"    ❌ {template_name} 渲染结果为空")
                            success = False
                            
                    except Exception as e:
                        print(f"    ❌ {template_file.name} 渲染失败: {e}")
                        success = False
                        
            except Exception as e:
                print(f"  ❌ 分支 {branch} 测试失败: {e}")
                success = False
        
        self.test_results.append(("模板渲染测试", success))
        return success
    
    def test_output_generation(self) -> bool:
        """测试输出文件生成"""
        print("\n🧪 测试输出文件生成...")
        
        success = True
        
        # 创建临时目录用于测试
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_renderer = TemplateRenderer()
            temp_renderer.rendered_dir = Path(temp_dir)
            temp_renderer.setup_logging(debug=False)
            
            # 测试每个分支
            for branch in self.renderer.supported_branches:
                try:
                    rendered_count = temp_renderer.render_templates_for_branch(branch)
                    
                    if rendered_count > 0:
                        print(f"  ✅ 分支 {branch} 生成了 {rendered_count} 个文件")
                        
                        # 检查文件是否存在
                        branch_dir = temp_renderer.rendered_dir / branch
                        if branch_dir.exists():
                            files = list(branch_dir.glob("*.py"))
                            print(f"    生成的文件: {[f.name for f in files]}")
                        else:
                            print(f"    ❌ 输出目录不存在: {branch_dir}")
                            success = False
                    else:
                        print(f"  ❌ 分支 {branch} 没有生成文件")
                        success = False
                        
                except Exception as e:
                    print(f"  ❌ 分支 {branch} 文件生成失败: {e}")
                    success = False
        
        self.test_results.append(("输出文件生成测试", success))
        return success
    
    def test_filename_generation(self) -> bool:
        """测试文件名生成规则"""
        print("\n🧪 测试文件名生成规则...")
        
        success = True
        test_cases = [
            ("templates/validate_config.py.j2", "dev", "validate_config_dev.py"),
            ("templates/database_config.py.j2", "sit", "database_config_sit.py"),
            ("templates/api_client.py.j2", "master", "api_client_master.py"),
        ]
        
        for template_path, branch, expected_filename in test_cases:
            try:
                actual_filename = self.renderer.generate_output_filename(template_path, branch)
                
                if actual_filename == expected_filename:
                    print(f"  ✅ {template_path} -> {actual_filename}")
                else:
                    print(f"  ❌ {template_path} -> 期望: {expected_filename}, 实际: {actual_filename}")
                    success = False
                    
            except Exception as e:
                print(f"  ❌ 文件名生成失败 {template_path}: {e}")
                success = False
        
        self.test_results.append(("文件名生成测试", success))
        return success
    
    def test_error_handling(self) -> bool:
        """测试错误处理"""
        print("\n🧪 测试错误处理...")
        
        success = True
        
        # 测试不存在的分支
        try:
            self.renderer.load_env_config("nonexistent")
            print("  ❌ 应该抛出异常但没有")
            success = False
        except FileNotFoundError:
            print("  ✅ 正确处理不存在的环境配置")
        except Exception as e:
            print(f"  ❌ 意外的异常类型: {e}")
            success = False
        
        # 测试不存在的模板
        try:
            env_config = self.renderer.load_env_config("dev")
            self.renderer.render_template("nonexistent.j2", "dev", env_config)
            print("  ❌ 应该抛出异常但没有")
            success = False
        except FileNotFoundError:
            print("  ✅ 正确处理不存在的模板文件")
        except Exception as e:
            print(f"  ❌ 意外的异常类型: {e}")
            success = False
        
        self.test_results.append(("错误处理测试", success))
        return success
    
    def run_all_tests(self) -> bool:
        """运行所有测试"""
        print("🚀 开始运行模板渲染系统测试\n")
        
        tests = [
            self.test_environment_configs,
            self.test_template_syntax,
            self.test_template_rendering,
            self.test_output_generation,
            self.test_filename_generation,
            self.test_error_handling,
        ]
        
        all_passed = True
        for test in tests:
            try:
                result = test()
                all_passed = all_passed and result
            except Exception as e:
                print(f"  ❌ 测试执行异常: {e}")
                all_passed = False
        
        return all_passed
    
    def print_summary(self):
        """打印测试摘要"""
        print("\n" + "="*60)
        print("测试结果摘要")
        print("="*60)
        
        passed = 0
        total = len(self.test_results)
        
        for test_name, result in self.test_results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\n总计: {passed}/{total} 个测试通过")
        
        if passed == total:
            print("🎉 所有测试都通过了！")
            return True
        else:
            print("⚠️  有测试失败，请检查上述错误信息")
            return False


def main():
    """主函数"""
    tester = RenderTester()
    
    # 运行所有测试
    all_passed = tester.run_all_tests()
    
    # 打印摘要
    success = tester.print_summary()
    
    # 返回适当的退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()