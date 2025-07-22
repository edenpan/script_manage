# GitHub Actions 测试指南

## 🎯 测试目标

现在你有了新的模板文件，可以测试GitHub Actions的渲染工作流了！

## 📁 新增的测试文件

我为你创建了以下新的模板文件：

1. **`templates/api_client.py.j2`** - API客户端配置模板
2. **`templates/logging_config.py.j2`** - 日志配置模板

这些文件会根据不同环境生成对应的配置文件。

## 🚀 如何触发GitHub Actions测试

### 方法1: 推送模板文件变更（推荐）

```bash
# 1. 添加新文件到Git
git add templates/api_client.py.j2
git add templates/logging_config.py.j2

# 2. 添加更新的环境配置文件
git add envs/dev.json
git add envs/sit.json  
git add envs/master.json

# 3. 提交变更
git commit -m "添加API客户端和日志配置模板

- 新增 api_client.py.j2 模板
- 新增 logging_config.py.j2 模板  
- 更新环境配置文件以支持新模板
- 添加API认证和日志配置选项"

# 4. 推送到sit分支（或其他分支）
git push origin sit
```

### 方法2: 手动触发工作流

1. 进入GitHub仓库页面
2. 点击 **Actions** 标签
3. 选择 **"Jinja2 Template Renderer"** 工作流
4. 点击 **"Run workflow"** 按钮
5. 选择分支并点击运行

## 📊 期望的测试结果

### 渲染工作流应该：

1. ✅ **验证模板语法** - 检查所有 `.j2` 文件语法正确
2. ✅ **渲染模板** - 为当前分支生成配置文件
3. ✅ **生成文件** - 在 `rendered/分支名/` 目录下创建：
   - `api_client_分支名.py`
   - `logging_config_分支名.py`
   - `database_config_分支名.py`
   - `validate_config_分支名.py`

### 测试工作流应该：

1. ✅ **单元测试** - 运行 `test_render.py`
2. ✅ **集成测试** - 测试每个分支的渲染
3. ✅ **性能测试** - 统计渲染时间和文件数量

## 🔍 如何查看测试结果

### 在GitHub Actions页面：

1. **工作流状态** - 绿色✅表示成功，红色❌表示失败
2. **详细日志** - 点击具体的运行记录查看详细输出
3. **Artifacts** - 下载生成的渲染文件

### 预期的日志输出：

```
✅ 模板语法验证通过
✅ 环境配置加载成功
✅ 模板渲染完成
📁 生成文件统计:
   - sit分支: 4个文件
   - api_client_sit.py
   - logging_config_sit.py  
   - database_config_sit.py
   - validate_config_sit.py
```

## 🐛 故障排除

### 如果工作流没有触发：

1. **检查分支名** - 确保推送到 `dev`、`sit`、`master` 分支
2. **检查文件路径** - 确保模板文件在 `templates/` 目录下
3. **检查文件扩展名** - 确保模板文件以 `.j2` 结尾

### 如果渲染失败：

1. **检查模板语法** - 使用本地测试验证模板语法
2. **检查环境配置** - 确保JSON文件格式正确
3. **查看详细日志** - 在GitHub Actions页面查看错误信息

## 🧪 本地测试验证

在推送前，你可以先在本地测试：

```bash
# 测试特定分支
./venv/bin/python scripts/render_templates.py --branch sit --debug

# 运行完整测试套件
./venv/bin/python test_render.py

# 或使用测试脚本
./run_tests.sh --integration
```

## 📈 成功指标

测试成功的标志：

- ✅ 所有GitHub Actions工作流显示绿色
- ✅ 生成了预期数量的配置文件
- ✅ 渲染的文件包含正确的环境特定配置
- ✅ 没有语法错误或运行时错误

现在你可以推送这些新文件到GitHub，观察Actions的运行情况了！