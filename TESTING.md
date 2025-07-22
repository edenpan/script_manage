# 测试指南

本文档介绍如何在GitHub上和本地环境中运行测试。

## 📋 目录

- [GitHub Actions 测试](#github-actions-测试)
- [本地测试](#本地测试)
- [测试类型](#测试类型)
- [测试配置](#测试配置)
- [故障排除](#故障排除)

## 🚀 GitHub Actions 测试

### 自动触发测试

测试会在以下情况下自动运行：

1. **推送代码** 到 `dev`、`sit`、`master`、`main` 分支
2. **创建 Pull Request** 到这些分支
3. **手动触发** (通过 GitHub Actions 页面)

### 测试工作流

我们有两个主要的 GitHub Actions 工作流：

#### 1. 渲染工作流 (`.github/workflows/render.yml`)
- **触发条件**: 推送到 `dev`、`sit`、`master` 分支，或模板文件变更
- **功能**: 
  - 验证模板语法
  - 渲染模板文件
  - 生成配置文件
  - 上传渲染结果

#### 2. 测试工作流 (`.github/workflows/test.yml`)
- **触发条件**: 推送代码或创建 PR
- **包含的测试**:
  - **单元测试**: 运行 `test_render.py`
  - **集成测试**: 测试每个分支的渲染功能
  - **性能测试**: 测试渲染性能和耗时
  - **代码质量检查**: Python语法检查

### 手动触发测试

1. 进入 GitHub 仓库页面
2. 点击 **Actions** 标签
3. 选择要运行的工作流
4. 点击 **Run workflow** 按钮

### 查看测试结果

1. 在 **Actions** 页面查看工作流运行状态
2. 点击具体的运行记录查看详细日志
3. 下载测试产生的 artifacts (渲染文件)

## 🖥️ 本地测试

### 快速开始

使用我们提供的测试脚本：

```bash
# 运行所有测试
./run_tests.sh

# 只运行基础测试
./run_tests.sh --basic

# 只运行语法检查
./run_tests.sh --syntax

# 查看帮助
./run_tests.sh --help
```

### 手动运行测试

#### 1. 安装依赖
```bash
pip install -r requirements.txt
```

#### 2. 运行单元测试
```bash
python test_render.py
```

#### 3. 运行特定分支的渲染测试
```bash
python scripts/render_templates.py --branch dev --debug
python scripts/render_templates.py --branch sit --debug
python scripts/render_templates.py --branch master --debug
```

#### 4. 运行所有分支的渲染测试
```bash
python scripts/render_templates.py --all --debug
```

#### 5. 语法检查
```bash
python -m py_compile test_render.py
python -m py_compile scripts/render_templates.py
```

## 🧪 测试类型

### 1. 单元测试
- **文件**: `test_render.py`
- **测试内容**:
  - 环境配置文件加载
  - 模板语法验证
  - 模板渲染功能
  - 输出文件生成
  - 文件名生成规则
  - 错误处理机制

### 2. 集成测试
- **测试内容**:
  - 完整的渲染流程
  - 多分支渲染
  - 生成文件的语法验证
  - 文件输出验证

### 3. 性能测试
- **测试内容**:
  - 渲染耗时统计
  - 文件生成数量统计
  - 性能基准检查

### 4. 代码质量测试
- **测试内容**:
  - Python语法检查
  - 项目结构验证
  - 配置文件格式验证

## ⚙️ 测试配置

### 环境要求
- Python 3.9+
- 依赖包: `jinja2`, `jsonschema`

### 测试文件结构
```
.
├── .github/workflows/
│   ├── render.yml          # 渲染工作流
│   └── test.yml           # 测试工作流
├── test_render.py         # 主测试文件
├── run_tests.sh          # 本地测试脚本
├── pytest.ini           # pytest配置
└── TESTING.md           # 本文档
```

### 测试数据
- **环境配置**: `envs/dev.json`, `envs/sit.json`, `envs/master.json`
- **模板文件**: `templates/*.j2`
- **渲染输出**: `rendered/*/`

## 🔧 故障排除

### 常见问题

#### 1. 测试失败: "环境配置文件不存在"
**解决方案**: 确保 `envs/` 目录下有对应分支的 JSON 配置文件
```bash
ls envs/
# 应该看到: dev.json, sit.json, master.json
```

#### 2. 测试失败: "模板语法错误"
**解决方案**: 检查 `templates/` 目录下的 `.j2` 文件语法
```bash
# 手动验证模板语法
python -c "
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('your_template.j2')
print('模板语法正确')
"
```

#### 3. 测试失败: "依赖包缺失"
**解决方案**: 安装所需依赖
```bash
pip install -r requirements.txt
```

#### 4. GitHub Actions 测试失败
**解决方案**: 
1. 检查 Actions 页面的详细日志
2. 确保所有必要文件都已提交
3. 检查分支名是否正确
4. 验证配置文件格式

### 调试技巧

#### 1. 启用调试模式
```bash
python scripts/render_templates.py --debug
```

#### 2. 查看详细测试输出
```bash
python test_render.py 2>&1 | tee test_output.log
```

#### 3. 检查生成的文件
```bash
find rendered -name "*.py" -exec python -m py_compile {} \;
```

## 📊 测试报告

### 本地测试报告
运行测试后会显示：
- ✅ 通过的测试数量
- ❌ 失败的测试详情
- 📊 性能统计信息
- 📁 生成文件统计

### GitHub Actions 报告
- 工作流运行状态
- 各个步骤的执行结果
- 测试 artifacts 下载
- 性能指标统计

## 🎯 最佳实践

1. **提交前测试**: 在推送代码前先在本地运行测试
2. **增量测试**: 只测试修改相关的部分
3. **定期清理**: 使用 `./run_tests.sh --cleanup` 清理测试文件
4. **监控性能**: 关注测试耗时，及时优化慢速测试
5. **查看日志**: 测试失败时仔细查看详细日志

## 📞 获取帮助

如果遇到测试问题：

1. 查看本文档的故障排除部分
2. 检查 GitHub Actions 的详细日志
3. 运行 `./run_tests.sh --help` 查看本地测试选项
4. 检查项目的 `README.md` 和 `USAGE.md` 文档

---

**提示**: 保持测试文件和配置的更新，确保测试能够准确反映项目的当前状态。