# Jinja2 模板自动渲染系统

这是一个基于Git提交触发的Jinja2模板自动渲染系统，当向特定分支提交包含新增.j2模板文件时，会自动根据分支环境渲染模板并生成对应的Python文件。

## 功能特性

✅ **智能触发**: 仅在提交到指定分支（dev、sit、master）且包含新增.j2文件时触发  
✅ **环境感知**: 根据分支名自动加载对应的环境变量文件  
✅ **灵活渲染**: 使用Jinja2引擎，支持复杂的模板逻辑  
✅ **规范输出**: 自动生成规范命名的渲染文件  
✅ **CI/CD集成**: 支持GitLab CI和GitHub Actions  

## 项目结构

```
.
├── templates/              # 模板文件目录
│   └── *.j2               # Jinja2模板文件
├── envs/                  # 环境配置目录
│   ├── dev.json          # 开发环境配置
│   ├── sit.json          # 测试环境配置
│   └── master.json       # 生产环境配置
├── rendered/              # 渲染输出目录
│   ├── dev/              # 开发环境渲染结果
│   ├── sit/              # 测试环境渲染结果
│   └── master/           # 生产环境渲染结果
├── scripts/               # 脚本目录
│   └── render_templates.py  # 模板渲染脚本
├── .gitlab-ci.yml        # GitLab CI配置
├── .github/              # GitHub Actions配置
│   └── workflows/
│       └── render.yml
└── requirements.txt      # Python依赖
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 创建模板文件

在 `templates/` 目录下创建 `.j2` 模板文件，例如：

```python
# templates/validate_config.py.j2
def validate_config():
    database_url = "{{ database.url }}"
    api_key = "{{ api.key }}"
    debug_mode = {{ debug | lower }}
    
    print(f"Database URL: {database_url}")
    print(f"API Key: {api_key}")
    print(f"Debug Mode: {debug_mode}")
```

### 3. 配置环境变量

在 `envs/` 目录下创建对应分支的配置文件：

```json
// envs/dev.json
{
    "database": {
        "url": "postgresql://localhost:5432/myapp_dev"
    },
    "api": {
        "key": "dev-api-key-12345"
    },
    "debug": true
}
```

### 4. 提交代码

当你向 `dev`、`sit` 或 `master` 分支提交包含新增 `.j2` 文件的代码时，系统会自动：

1. 检测新增的模板文件
2. 根据分支名加载对应的环境配置
3. 渲染模板并生成Python文件
4. 将结果保存到 `rendered/<branch>/` 目录

## 手动执行

你也可以手动运行渲染脚本：

```bash
# 渲染指定分支的模板
python scripts/render_templates.py --branch dev

# 渲染所有分支的模板
python scripts/render_templates.py --all
```

## 配置说明

### 环境配置文件格式

环境配置文件使用JSON格式，支持嵌套结构：

```json
{
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "myapp"
    },
    "features": {
        "enable_cache": true,
        "max_connections": 100
    }
}
```

### 模板语法

支持完整的Jinja2语法：

```python
# 变量替换
database_host = "{{ database.host }}"

# 条件判断
{% if features.enable_cache %}
CACHE_ENABLED = True
{% else %}
CACHE_ENABLED = False
{% endif %}

# 循环
ALLOWED_HOSTS = [
{% for host in allowed_hosts %}
    "{{ host }}",
{% endfor %}
]
```

## CI/CD集成

### GitLab CI

项目已包含 `.gitlab-ci.yml` 配置文件，会在以下情况自动触发：

- 推送到 `dev`、`sit`、`master` 分支
- 包含新增的 `.j2` 文件

### GitHub Actions

项目已包含 GitHub Actions 配置文件，触发条件相同。

## 故障排除

### 常见问题

1. **模板渲染失败**: 检查环境配置文件是否存在且格式正确
2. **变量未找到**: 确认模板中使用的变量在环境配置中已定义
3. **权限问题**: 确保CI/CD有足够权限创建和提交文件

### 调试模式

启用调试模式查看详细日志：

```bash
python scripts/render_templates.py --branch dev --debug