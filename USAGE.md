# 使用说明

本文档详细介绍如何使用Jinja2模板自动渲染系统。

## 目录

- [快速开始](#快速开始)
- [创建模板](#创建模板)
- [配置环境](#配置环境)
- [手动执行](#手动执行)
- [CI/CD集成](#cicd集成)
- [高级用法](#高级用法)
- [故障排除](#故障排除)

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <your-repo-url>
cd script_manage

# 安装Python依赖
pip install -r requirements.txt

# 验证安装
python scripts/render_templates.py --help
```

### 2. 创建第一个模板

在 `templates/` 目录下创建一个简单的模板文件：

```python
# templates/hello_world.py.j2
#!/usr/bin/env python3
"""
Hello World 示例 - {{ environment }} 环境
生成时间: {{ "now" | strftime("%Y-%m-%d %H:%M:%S") }}
"""

def main():
    print("Hello from {{ environment }} environment!")
    print("Debug mode: {{ debug }}")
    print("Database: {{ database.host }}:{{ database.port }}")

if __name__ == "__main__":
    main()
```

### 3. 测试渲染

```bash
# 渲染开发环境模板
python scripts/render_templates.py --branch dev

# 查看渲染结果
cat rendered/dev/hello_world_dev.py
```

## 创建模板

### 模板文件命名规则

- 模板文件必须以 `.j2` 扩展名结尾
- 建议使用描述性的文件名，如 `database_config.py.j2`
- 模板文件应放在 `templates/` 目录下

### 支持的Jinja2语法

#### 1. 变量替换

```python
# 简单变量
database_host = "{{ database.host }}"

# 嵌套变量
api_endpoint = "{{ api.base_url }}/v1"

# 带默认值的变量
timeout = {{ api.timeout | default(30) }}
```

#### 2. 条件判断

```python
{% if debug %}
DEBUG = True
LOG_LEVEL = "DEBUG"
{% else %}
DEBUG = False
LOG_LEVEL = "INFO"
{% endif %}

# 内联条件
CACHE_ENABLED = {{ "True" if cache.enabled else "False" }}
```

#### 3. 循环

```python
# 列表循环
ALLOWED_HOSTS = [
{% for host in security.cors_origins %}
    "{{ host }}",
{% endfor %}
]

# 字典循环
DATABASE_SETTINGS = {
{% for key, value in database.items() %}
    "{{ key }}": {{ value | tojson }},
{% endfor %}
}
```

#### 4. 过滤器

```python
# 字符串过滤器
app_name = "{{ database.name | upper }}"
secret_key = "{{ security.secret_key | truncate(10) }}..."

# 数字过滤器
max_connections = {{ features.max_connections | int }}

# JSON过滤器
config_data = {{ database | tojson }}

# 日期过滤器
generated_at = "{{ "now" | strftime("%Y-%m-%d %H:%M:%S") }}"
```

#### 5. 宏定义

```python
{% macro generate_connection_string(host, port, name) %}
postgresql://user:password@{{ host }}:{{ port }}/{{ name }}
{% endmacro %}

# 使用宏
DATABASE_URL = "{{ generate_connection_string(database.host, database.port, database.name) }}"
```

### 模板最佳实践

1. **添加文件头注释**：包含生成时间、环境信息等
2. **使用有意义的变量名**：便于理解和维护
3. **添加默认值**：防止变量未定义错误
4. **合理使用条件判断**：根据环境生成不同配置
5. **保持模板简洁**：避免过于复杂的逻辑

## 配置环境

### 环境配置文件结构

环境配置文件使用JSON格式，支持任意嵌套结构：

```json
{
  "database": {
    "host": "localhost",
    "port": 5432,
    "name": "myapp_dev"
  },
  "features": {
    "enable_cache": true,
    "max_users": 1000
  },
  "environment": "development",
  "debug": true
}
```

### 配置文件命名

- `envs/dev.json` - 开发环境
- `envs/sit.json` - 测试环境  
- `envs/master.json` - 生产环境

### 配置验证

系统会自动验证JSON格式的正确性。建议使用以下命令验证：

```bash
# 验证单个配置文件
python -m json.tool envs/dev.json

# 验证所有配置文件
for file in envs/*.json; do
    echo "验证 $file"
    python -m json.tool "$file" > /dev/null && echo "✓ 格式正确" || echo "✗ 格式错误"
done
```

## 手动执行

### 基本命令

```bash
# 自动模式：检测当前分支和新增文件
python scripts/render_templates.py --auto

# 渲染指定分支
python scripts/render_templates.py --branch dev

# 渲染所有分支
python scripts/render_templates.py --all

# 启用调试模式
python scripts/render_templates.py --branch dev --debug
```

### 高级选项

```bash
# 指定项目根目录
python scripts/render_templates.py --project-root /path/to/project --branch dev

# 组合使用
python scripts/render_templates.py --all --debug
```

### 输出说明

渲染成功后，文件会保存到 `rendered/<branch>/` 目录：

```
rendered/
├── dev/
│   ├── validate_config_dev.py
│   └── database_config_dev.py
├── sit/
│   ├── validate_config_sit.py
│   └── database_config_sit.py
└── master/
    ├── validate_config_master.py
    └── database_config_master.py
```

## CI/CD集成

### GitLab CI

系统已包含完整的GitLab CI配置（`.gitlab-ci.yml`），支持：

- **自动触发**：推送到指定分支且包含新增.j2文件时
- **模板验证**：检查模板语法和配置文件格式
- **渲染执行**：自动渲染并保存结果
- **手动触发**：支持手动渲染所有分支

#### 触发条件

```yaml
rules:
  - if: '$CI_COMMIT_BRANCH =~ /^(dev|sit|master)$/'
    changes:
      - "templates/**/*.j2"
    when: always
```

### GitHub Actions

系统已包含GitHub Actions配置（`.github/workflows/render.yml`），功能类似GitLab CI。

#### 手动触发

在GitHub仓库页面，进入Actions标签页，选择"Jinja2 Template Renderer"工作流，点击"Run workflow"。

### 自定义CI/CD

如果使用其他CI/CD系统，可以参考以下步骤：

1. **环境准备**：安装Python和依赖
2. **检查触发条件**：验证分支和文件变更
3. **执行渲染**：运行渲染脚本
4. **保存结果**：将渲染文件作为构建产物

## 高级用法

### 自定义过滤器

可以在渲染脚本中添加自定义Jinja2过滤器：

```python
# 在 TemplateRenderer.__init__ 中添加
def custom_filter(value):
    return value.upper().replace('_', '-')

self.jinja_env.filters['custom'] = custom_filter
```

### 条件渲染

根据环境条件决定是否渲染某些部分：

```python
{% if environment == "production" %}
# 生产环境特有配置
ENABLE_MONITORING = True
{% endif %}

{% if features.enable_cache %}
# 缓存相关配置
CACHE_CONFIG = {{ cache | tojson }}
{% endif %}
```

### 包含其他模板

```python
{% include 'common_header.j2' %}

# 主要内容
def main():
    pass

{% include 'common_footer.j2' %}
```

### 模板继承

```python
# base.py.j2
#!/usr/bin/env python3
"""
{% block header %}基础模板{% endblock %}
"""

{% block content %}
# 默认内容
{% endblock %}

# specific.py.j2
{% extends "base.py.j2" %}

{% block header %}特定模板 - {{ environment }}{% endblock %}

{% block content %}
# 特定内容
def specific_function():
    pass
{% endblock %}
```

## 故障排除

### 常见错误

#### 1. 模板语法错误

```
TemplateSyntaxError: unexpected char '}'
```

**解决方案**：检查模板中的Jinja2语法，确保大括号配对正确。

#### 2. 变量未定义

```
UndefinedError: 'database' is undefined
```

**解决方案**：检查环境配置文件中是否定义了相应变量。

#### 3. JSON格式错误

```
JSONDecodeError: Expecting ',' delimiter
```

**解决方案**：使用JSON验证工具检查配置文件格式。

#### 4. 文件权限错误

```
PermissionError: [Errno 13] Permission denied
```

**解决方案**：检查文件和目录权限，确保有写入权限。

### 调试技巧

#### 1. 启用调试模式

```bash
python scripts/render_templates.py --branch dev --debug
```

#### 2. 检查模板变量

在模板中添加调试输出：

```python
# 调试：打印所有可用变量
"""
可用变量：
{% for key in locals() %}
- {{ key }}: {{ locals()[key] }}
{% endfor %}
"""
```

#### 3. 验证配置文件

```bash
# 验证JSON格式
python -c "import json; print(json.load(open('envs/dev.json')))"

# 美化输出
python -m json.tool envs/dev.json
```

#### 4. 测试单个模板

创建简单的测试脚本：

```python
from jinja2 import Environment, FileSystemLoader
import json

# 加载环境配置
with open('envs/dev.json') as f:
    config = json.load(f)

# 创建Jinja2环境
env = Environment(loader=FileSystemLoader('templates'))

# 渲染模板
template = env.get_template('your_template.j2')
result = template.render(**config)

print(result)
```

### 性能优化

#### 1. 缓存模板

```python
# 启用模板缓存
from jinja2 import Environment, FileSystemLoader, FileSystemBytecodeCache

cache = FileSystemBytecodeCache('/tmp/jinja2_cache')
env = Environment(
    loader=FileSystemLoader('templates'),
    bytecode_cache=cache
)
```

#### 2. 并行渲染

对于大量模板，可以考虑并行处理：

```python
from concurrent.futures import ThreadPoolExecutor

def render_template_parallel(template_files, branch):
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(render_single_template, template, branch)
            for template in template_files
        ]
        results = [future.result() for future in futures]
    return results
```

### 监控和日志

#### 1. 日志配置

系统已内置完整的日志功能，可以通过以下方式查看：

```bash
# 查看详细日志
python scripts/render_templates.py --branch dev --debug 2>&1 | tee render.log
```

#### 2. 渲染统计

脚本会自动输出渲染统计信息：

```
2024-01-01 10:00:00 - INFO - 分支 dev 成功渲染 2 个模板文件
2024-01-01 10:00:00 - INFO - 总共渲染了 6 个文件
```

#### 3. CI/CD监控

在CI/CD中，可以通过构建产物和日志监控渲染状态：

- 检查 `rendered/` 目录中的文件
- 查看CI/CD日志中的渲染统计
- 设置构建失败通知

---

如有其他问题，请查看项目的README.md文件或提交Issue。