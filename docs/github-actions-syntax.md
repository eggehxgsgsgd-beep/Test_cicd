# GitHub Actions CI/CD 语法解析

这份文档专门解释 GitHub Actions YAML 的常用语法。建议和 `.github/workflows/ci.yml`、`.github/workflows/release.yml` 对照阅读。

## 1. workflow 的基本结构

一个 GitHub Actions 文件通常长这样：

```yaml
name: Python CI

on:
  push:
    branches: ["main"]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Say hello
        run: echo "hello"
```

核心结构：

```text
name -> workflow 名称
on   -> 什么时候触发
jobs -> 要执行哪些任务
```

## 2. name

```yaml
name: Python CI
```

`name` 是 workflow 的显示名称。

它会显示在 GitHub 仓库的 `Actions` 页面。

## 3. on

`on` 用来定义触发条件。

### push

```yaml
on:
  push:
    branches: ["main", "master"]
```

含义：

```text
当代码 push 到 main 或 master 时运行。
```

### pull_request

```yaml
on:
  pull_request:
    branches: ["main"]
```

含义：

```text
当有人向 main 分支发起 PR 时运行。
```

### workflow_dispatch

```yaml
on:
  workflow_dispatch:
```

含义：

```text
允许在 GitHub Actions 页面手动点击运行。
```

### push tags

```yaml
on:
  push:
    tags:
      - "v*.*.*"
```

含义：

```text
当推送 v1.0.0 这种 tag 时运行。
```

常用于 Release。

### schedule

```yaml
on:
  schedule:
    - cron: "0 2 * * *"
```

含义：

```text
每天 UTC 时间 2 点运行。
```

北京时间比 UTC 快 8 小时。

## 4. jobs

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
```

`jobs` 是任务集合。`test` 是任务 ID，可以自定义。

任务 ID 只在 YAML 内部使用，例如：

```yaml
needs: test
```

## 5. job name

```yaml
jobs:
  test:
    name: Lint and test
```

`name` 是 job 在 GitHub 页面上的显示名称。

如果不写，GitHub 会显示 job ID，比如 `test`。

## 6. runs-on

```yaml
runs-on: ubuntu-latest
```

`runs-on` 表示 job 运行在哪种机器上。

常见值：

```yaml
runs-on: ubuntu-latest
runs-on: windows-latest
runs-on: macos-latest
```

多平台打包时常用：

```yaml
runs-on: ${{ matrix.os }}
```

## 7. steps

```yaml
steps:
  - name: Check out repository
    uses: actions/checkout@v4

  - name: Run tests
    run: pytest
```

`steps` 是一个 job 里的步骤列表。

步骤按顺序执行：

```text
第一个 step 成功 -> 第二个 step 执行 -> 第三个 step 执行
```

如果某一步失败，后面的步骤默认不会继续。

## 8. name in step

```yaml
- name: Run tests
  run: pytest
```

step 里的 `name` 是这一步在日志里的显示名称。

它只是为了让日志更好读，不影响实际执行。

## 9. uses

```yaml
- uses: actions/checkout@v4
```

`uses` 表示使用别人写好的 Action。

格式：

```text
作者或组织/Action 名称@版本
```

例子：

```yaml
uses: actions/checkout@v4
uses: actions/setup-python@v5
uses: actions/upload-artifact@v4
```

解释：

- `actions`：GitHub 官方组织。
- `checkout`：Action 名称。
- `@v4`：这个 Action 的第 4 个大版本。

注意：

```text
@v4 不是 Python 版本。
@v5 也不是 Python 版本。
它们是 Action 自己的版本。
```

### actions/checkout@v4 是什么

`actions/checkout@v4` 是 GitHub 官方最常用的 Action 之一。

它的作用是：

```text
把触发当前 workflow 的仓库代码下载到 CI 机器上。
```

这一步可以理解为：

```text
git clone 仓库
+ git checkout 当前提交
```

注意，Actions 里的 `checkout` 容易和 Git 命令里的 `git checkout 分支名` 混淆。

区别是：

```text
Git 里的 checkout:
  常用于切换分支或切换到某个提交。

GitHub Actions 里的 actions/checkout:
  用于把当前 workflow 需要的代码检出到临时 CI 机器上。
```

如果没有这一步，CI 机器通常是空的，后面运行这些命令就可能失败：

```yaml
run: pytest
run: ruff check .
run: python -m build
```

因为它找不到你的 `src/`、`tests/`、`pyproject.toml` 等项目文件。

## 10. run

```yaml
- name: Run tests
  run: pytest
```

`run` 表示在 CI 机器上执行 shell 命令。

多行命令：

```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    python -m pip install -e ".[dev]"
```

`|` 表示下面是多行脚本。

## 11. with

```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: "3.12"
    cache: pip
```

`with` 用来给 Action 传参数。

这里的意思是：

```text
使用 Python 3.12
开启 pip 缓存
```

不同 Action 支持的 `with` 参数不同，需要看对应 Action 文档。

## 12. env

`env` 用于设置环境变量。

workflow 级别：

```yaml
env:
  PYTHON_VERSION: "3.12"
```

job 级别：

```yaml
jobs:
  test:
    env:
      APP_ENV: test
```

step 级别：

```yaml
- name: Run command
  run: echo "$APP_ENV"
  env:
    APP_ENV: test
```

范围越小，优先级越高。

## 13. ${{ }} 表达式

`${{ }}` 是 GitHub Actions 的表达式语法。

例子：

```yaml
python-version: ${{ matrix.python-version }}
```

含义：

```text
从 matrix 里取 python-version 的值。
```

常见上下文：

```yaml
${{ github.ref }}
${{ github.sha }}
${{ github.repository }}
${{ matrix.python-version }}
${{ secrets.API_TOKEN }}
${{ env.APP_ENV }}
```

## 14. github 上下文

`github` 里保存当前 workflow 的 GitHub 信息。

常用：

```yaml
${{ github.ref }}
${{ github.sha }}
${{ github.actor }}
${{ github.repository }}
```

例子：

```yaml
if: startsWith(github.ref, 'refs/tags/')
```

含义：

```text
只有当前触发来源是 tag 时才执行。
```

## 15. secrets

```yaml
env:
  TOKEN: ${{ secrets.API_TOKEN }}
```

`secrets` 用于读取 GitHub 仓库配置里的密钥。

密钥配置位置：

```text
Repository -> Settings -> Secrets and variables -> Actions
```

不要这样写：

```yaml
env:
  TOKEN: "真实密钥"
```

真实密钥不能写进代码仓库。

## 16. strategy matrix

matrix 用于批量生成多个 job。

```yaml
strategy:
  fail-fast: false
  matrix:
    python-version: ["3.10", "3.11", "3.12"]
```

配合：

```yaml
python-version: ${{ matrix.python-version }}
```

实际效果：

```text
运行一次 Python 3.10
运行一次 Python 3.11
运行一次 Python 3.12
```

## 17. matrix include

如果每个平台需要多个字段，可以使用 `include`：

```yaml
strategy:
  matrix:
    include:
      - os: ubuntu-latest
        asset-name: linux
      - os: windows-latest
        asset-name: windows
      - os: macos-latest
        asset-name: macos
```

引用方式：

```yaml
runs-on: ${{ matrix.os }}
name: Build executable for ${{ matrix.asset-name }}
```

适合多平台打包。

## 18. fail-fast

```yaml
strategy:
  fail-fast: false
```

含义：

```text
matrix 中某一个 job 失败时，不立即取消其他 job。
```

学习和排错时建议设置为 `false`，这样能看到所有平台或所有版本的完整结果。

## 19. needs

```yaml
jobs:
  validate:
    runs-on: ubuntu-latest

  build:
    needs: validate
    runs-on: ubuntu-latest
```

`needs` 表示 job 依赖。

含义：

```text
validate 成功后，build 才运行。
```

多个依赖：

```yaml
needs:
  - build-python-package
  - build-executable
```

## 20. if

```yaml
if: startsWith(github.ref, 'refs/tags/')
```

`if` 用于控制 job 或 step 是否执行。

常见例子：

```yaml
if: github.ref == 'refs/heads/main'
```

表示只在 `main` 分支执行。

```yaml
if: startsWith(github.ref, 'refs/tags/')
```

表示只在 tag 触发时执行。

```yaml
if: always()
```

表示前面即使失败，也尝试执行。

## 21. permissions

```yaml
permissions:
  contents: write
```

`permissions` 用于设置 `GITHUB_TOKEN` 权限。

创建 Release 时通常需要：

```yaml
permissions:
  contents: write
```

只读仓库代码时：

```yaml
permissions:
  contents: read
```

原则：

```text
需要什么权限，就只给什么权限。
```

## 22. shell

```yaml
- name: Smoke test executable
  shell: pwsh
  run: |
    $output = ./dist/cicd-demo.exe fib 7
    if ($output -ne "13") {
      throw "Unexpected output"
    }
```

`shell` 指定用什么 shell 执行命令。

常见：

```yaml
shell: bash
shell: pwsh
shell: cmd
```

跨 Windows、Linux、macOS 写脚本时，`pwsh` 有时更统一，因为 GitHub runner 都支持 PowerShell。

## 23. path

很多 Action 需要 `path` 指定文件位置。

上传 artifact：

```yaml
with:
  name: python-package
  path: dist/*
```

下载 artifact：

```yaml
with:
  path: release-assets
```

支持通配符：

```yaml
path: release-assets/**/*
```

## 24. artifact 相关语法

上传：

```yaml
- name: Upload artifact
  uses: actions/upload-artifact@v4
  with:
    name: app
    path: dist/*
```

下载：

```yaml
- name: Download artifact
  uses: actions/download-artifact@v4
  with:
    path: release-assets
```

多个 job 之间传文件时，经常用 artifact。

## 25. Release 相关语法

```yaml
- name: Create GitHub Release
  uses: softprops/action-gh-release@v2
  with:
    generate_release_notes: true
    files: release-assets/**/*
```

含义：

- `generate_release_notes: true`：自动根据提交记录生成 Release notes。
- `files`：上传哪些文件到 Release。

通常配合 tag 使用：

```yaml
on:
  push:
    tags:
      - "v*.*.*"
```

## 26. YAML 缩进规则

GitHub Actions 使用 YAML，缩进非常重要。

正确：

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
```

错误：

```yaml
jobs:
test:
runs-on: ubuntu-latest
```

建议：

```text
统一使用 2 个空格缩进，不要使用 Tab。
```

## 27. 数组写法

单行数组：

```yaml
branches: ["main", "master"]
```

多行数组：

```yaml
branches:
  - main
  - master
```

两种都可以。

## 28. 多行命令

```yaml
run: |
  python -m pip install --upgrade pip
  python -m pip install -e ".[dev]"
  pytest
```

`|` 表示保留换行，适合写多行脚本。

## 29. 注释

```yaml
# This is a comment
name: Python CI
```

注释用 `#`。

建议只给关键逻辑写注释，不要每一行都注释。

## 30. 常见完整结构速查

```yaml
name: Example

on:
  push:
    branches: ["main"]
  workflow_dispatch:

permissions:
  contents: read

jobs:
  test:
    name: Run tests
    runs-on: ubuntu-latest

    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.11", "3.12"]

    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          python -m pip install -e ".[dev]"

      - name: Run tests
        run: pytest
```

## 31. 读 workflow 的顺序

看到一个陌生 workflow 时，建议按这个顺序读：

1. 看 `name`，知道它是 CI、Release 还是 Deploy。
2. 看 `on`，知道什么时候触发。
3. 看 `jobs`，知道有几个任务。
4. 看 `runs-on`，知道在哪种系统上跑。
5. 看 `needs`，知道任务顺序。
6. 看 `steps`，逐步理解每个命令。
7. 看 `uses`，确认用了哪些现成 Action。
8. 看 `run`，理解真正执行的命令。
9. 看 `if`，确认哪些条件下才执行。
10. 看 `permissions` 和 `secrets`，确认是否涉及发布或部署。
