# GitHub Actions 到 GitLab CI/CD 迁移指南

本文档说明如何将现有的 GitHub Actions workflows 转换为 GitLab CI/CD pipelines。

## 转换概览

我们将以下 GitHub Actions workflows 转换为 GitLab CI/CD：

- `.github/workflows/test.yml` - 运行测试
- `.github/workflows/render.yml` - Jinja2 模板渲染

## 转换后的文件

### 1. `.gitlab-ci-comprehensive.yml` - 完整功能版本

这是一个功能完整的 GitLab CI/CD 配置，包含：

- **验证阶段** (`validate`): 验证模板语法和JSON配置
- **测试阶段** (`test`): 单元测试
- **集成测试阶段** (`integration-test`): 并行测试多个分支
- **性能测试阶段** (`performance-test`): 性能基准测试
- **渲染阶段** (`render`): 模板渲染
- **通知阶段** (`notify`): 结果通知

### 2. `.gitlab-ci-simple.yml` - 简化版本

这是一个简化的配置，包含核心功能：

- **测试阶段** (`test`): 基础测试和验证
- **渲染阶段** (`render`): 模板渲染
- **部署阶段** (`deploy`): 可选的部署步骤

## 主要转换对照

### 触发条件

| GitHub Actions | GitLab CI/CD |
|----------------|--------------|
| `on.push.branches` | `rules.if: $CI_PIPELINE_SOURCE == "push"` |
| `on.pull_request` | `rules.if: $CI_PIPELINE_SOURCE == "merge_request_event"` |
| `workflow_dispatch` | `rules.if: $CI_PIPELINE_SOURCE == "web"` |
| `on.push.paths` | `rules.changes` |

### 环境变量

| GitHub Actions | GitLab CI/CD |
|----------------|--------------|
| `env.PYTHON_VERSION` | `variables.PYTHON_VERSION` |
| `${{ env.PYTHON_VERSION }}` | `${PYTHON_VERSION}` |
| `${GITHUB_REF#refs/heads/}` | `$CI_COMMIT_REF_NAME` |
| `$GITHUB_SHA` | `$CI_COMMIT_SHA` |

### 作业依赖

| GitHub Actions | GitLab CI/CD |
|----------------|--------------|
| `needs: test` | `needs: ["test"]` |
| `runs-on: ubuntu-latest` | `image: python:3.9` |

### 条件执行

| GitHub Actions | GitLab CI/CD |
|----------------|--------------|
| `if: always()` | `when: always` |
| `if: success()` | `when: on_success` (默认) |
| `if: failure()` | `when: on_failure` |

### 矩阵构建

| GitHub Actions | GitLab CI/CD |
|----------------|--------------|
| `strategy.matrix` | `parallel.matrix` |

### 工件上传

| GitHub Actions | GitLab CI/CD |
|----------------|--------------|
| `actions/upload-artifact@v4` | `artifacts` |
| `retention-days: 7` | `expire_in: 7 days` |

## 使用方法

### 1. 选择配置文件

根据项目需求选择合适的配置：

- **完整功能**: 重命名 `.gitlab-ci-comprehensive.yml` 为 `.gitlab-ci.yml`
- **简化版本**: 重命名 `.gitlab-ci-simple.yml` 为 `.gitlab-ci.yml`

```bash
# 使用完整版本
cp .gitlab-ci-comprehensive.yml .gitlab-ci.yml

# 或使用简化版本
cp .gitlab-ci-simple.yml .gitlab-ci.yml
```

### 2. 配置 GitLab Runner

确保 GitLab Runner 已正确配置，支持 Docker 执行器。

### 3. 设置项目变量（可选）

在 GitLab 项目设置中添加以下变量：

- `PYTHON_VERSION`: Python 版本（默认: 3.9）
- `RENDER_ALL`: 是否渲染所有分支（手动触发时使用）

### 4. 触发 Pipeline

Pipeline 会在以下情况自动触发：

- 推送到 `dev`、`sit`、`master` 分支
- 创建 Merge Request
- 手动触发（Web UI）
- 模板文件 (`templates/**/*.j2`) 或配置文件 (`envs/*.json`) 变更

## 功能特性

### 缓存优化

```yaml
cache:
  paths:
    - .cache/pip/
    - venv/
```

### 并行执行

集成测试支持并行执行多个分支：

```yaml
parallel:
  matrix:
    - BRANCH: [dev, sit, master]
```

### 工件管理

渲染结果会自动保存为工件：

```yaml
artifacts:
  name: "rendered-$CI_COMMIT_REF_NAME-$CI_COMMIT_SHORT_SHA"
  paths:
    - rendered/
  expire_in: 30 days
```

### 条件执行

不同的触发条件执行不同的任务：

```yaml
rules:
  - if: $CI_PIPELINE_SOURCE == "push" && $CI_COMMIT_REF_NAME == "master"
  - if: $CI_PIPELINE_SOURCE == "web"
    when: manual
```

## 注意事项

1. **Docker 镜像**: 使用官方 Python 镜像，确保版本一致性
2. **权限设置**: 确保 GitLab Runner 有足够权限执行所需操作
3. **资源限制**: 根据项目规模调整 Runner 资源配置
4. **安全考虑**: 敏感信息使用 GitLab 项目变量管理

## 故障排除

### 常见问题

1. **Pipeline 不触发**: 检查 `rules` 配置和分支名称
2. **依赖安装失败**: 检查 `requirements.txt` 和网络连接
3. **权限错误**: 检查 GitLab Runner 权限设置
4. **工件上传失败**: 检查磁盘空间和路径配置

### 调试技巧

1. 使用 `echo` 命令输出调试信息
2. 检查 `$CI_*` 环境变量值
3. 使用 `when: manual` 进行手动调试
4. 查看 GitLab CI/CD 日志详细信息

## 进一步优化

1. **多阶段构建**: 使用 Docker 多阶段构建优化镜像大小
2. **自定义镜像**: 创建包含所需依赖的自定义镜像
3. **并行优化**: 进一步优化并行执行策略
4. **通知集成**: 集成 Slack、邮件等通知服务

## 总结

通过以上转换，我们成功将 GitHub Actions workflows 迁移到 GitLab CI/CD，保持了原有功能的同时，利用了 GitLab CI/CD 的特性进行了优化。选择合适的配置文件并根据项目需求进行调整即可开始使用。