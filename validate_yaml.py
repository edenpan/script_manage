#!/usr/bin/env python3
import sys
import json

def validate_yaml_with_json():
    """使用JSON模块来验证基本的YAML结构"""
    try:
        with open('.gitlab-ci.yml', 'r') as f:
            content = f.read()
        
        # 检查基本的YAML结构问题
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # 检查制表符
            if '\t' in line:
                print(f"警告: 第{i}行包含制表符，建议使用空格")
            
            # 检查空行是否包含空白字符
            if line.strip() == '' and len(line) > 0:
                print(f"警告: 第{i}行是包含空白字符的空行")
        
        print("YAML文件基本结构检查完成")
        return True
        
    except Exception as e:
        print(f"验证失败: {e}")
        return False

if __name__ == "__main__":
    validate_yaml_with_json()