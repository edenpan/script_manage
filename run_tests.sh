#!/bin/bash

# 测试运行脚本
# 用于在本地环境中运行各种测试

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查Python环境
check_python() {
    print_info "检查Python环境..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安装"
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2)
    print_success "Python版本: $python_version"
}

# 安装依赖
install_dependencies() {
    print_info "安装依赖..."
    
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
        print_success "依赖安装完成"
    else
        print_warning "requirements.txt 不存在，跳过依赖安装"
    fi
}

# 运行基础测试
run_basic_tests() {
    print_info "运行基础测试..."
    
    if [ -f "test_render.py" ]; then
        python3 test_render.py
        print_success "基础测试完成"
    else
        print_error "test_render.py 不存在"
        exit 1
    fi
}

# 运行语法检查
run_syntax_check() {
    print_info "运行语法检查..."
    
    # 检查主要Python文件
    files_to_check=(
        "test_render.py"
        "scripts/render_templates.py"
        "validate_yaml.py"
        "demo.py"
    )
    
    for file in "${files_to_check[@]}"; do
        if [ -f "$file" ]; then
            python3 -m py_compile "$file"
            print_success "$file 语法正确"
        else
            print_warning "$file 不存在，跳过检查"
        fi
    done
}

# 运行集成测试
run_integration_tests() {
    print_info "运行集成测试..."
    
    branches=("dev" "sit" "master")
    
    for branch in "${branches[@]}"; do
        print_info "测试分支: $branch"
        
        if [ -f "envs/${branch}.json" ]; then
            python3 scripts/render_templates.py --branch "$branch" --debug
            
            if [ -d "rendered/$branch" ]; then
                file_count=$(find "rendered/$branch" -name "*.py" | wc -l)
                print_success "分支 $branch 生成了 $file_count 个文件"
            else
                print_error "分支 $branch 没有生成文件"
            fi
        else
            print_warning "环境配置文件 envs/${branch}.json 不存在"
        fi
    done
}

# 运行性能测试
run_performance_tests() {
    print_info "运行性能测试..."
    
    start_time=$(date +%s)
    
    # 渲染所有分支
    python3 scripts/render_templates.py --all --debug
    
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    print_success "渲染完成，耗时: ${duration} 秒"
    
    # 统计文件
    total_files=0
    for branch in dev sit master; do
        if [ -d "rendered/$branch" ]; then
            count=$(find "rendered/$branch" -name "*.py" | wc -l)
            print_info "分支 $branch: $count 个文件"
            total_files=$((total_files + count))
        fi
    done
    
    print_success "总计生成文件: $total_files 个"
    
    if [ $duration -gt 30 ]; then
        print_warning "渲染时间超过30秒，可能存在性能问题"
    else
        print_success "渲染性能良好"
    fi
}

# 清理测试文件
cleanup() {
    print_info "清理测试文件..."
    
    if [ -d "rendered" ]; then
        rm -rf rendered
        print_success "清理完成"
    else
        print_info "没有需要清理的文件"
    fi
}

# 显示帮助信息
show_help() {
    echo "测试运行脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help          显示帮助信息"
    echo "  -b, --basic         只运行基础测试"
    echo "  -s, --syntax        只运行语法检查"
    echo "  -i, --integration   只运行集成测试"
    echo "  -p, --performance   只运行性能测试"
    echo "  -c, --cleanup       清理测试文件"
    echo "  -a, --all           运行所有测试 (默认)"
    echo ""
    echo "示例:"
    echo "  $0                  # 运行所有测试"
    echo "  $0 -b               # 只运行基础测试"
    echo "  $0 -c               # 清理测试文件"
}

# 主函数
main() {
    echo "🚀 模板渲染系统测试脚本"
    echo "=========================="
    
    case "${1:-all}" in
        -h|--help)
            show_help
            exit 0
            ;;
        -b|--basic)
            check_python
            install_dependencies
            run_basic_tests
            ;;
        -s|--syntax)
            check_python
            run_syntax_check
            ;;
        -i|--integration)
            check_python
            install_dependencies
            run_integration_tests
            ;;
        -p|--performance)
            check_python
            install_dependencies
            run_performance_tests
            ;;
        -c|--cleanup)
            cleanup
            ;;
        -a|--all|all)
            check_python
            install_dependencies
            run_syntax_check
            run_basic_tests
            run_integration_tests
            run_performance_tests
            ;;
        *)
            print_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
    
    print_success "测试完成！"
}

# 运行主函数
main "$@"