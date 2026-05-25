# 常用 GitHub CI/CD 指南

这份文档用于快速理解和编写常见的 GitHub Actions CI/CD 流程。它以 Python 项目为例，但大部分思路也适用于 Node.js、Go、Java、Rust 等项目。

## 1. CI/CD 是什么

CI 是 Continuous Integration，持续集成。

它主要解决：

- 每次提交代码后，自动安装依赖。
- 自动运行代码检查。
- 自动运行测试。
- 自动发现代码是否破坏了项目。

CD 是 Continuous Delivery 或 Continuous Deployment，持续交付或持续部署。

它主要解决：

- CI 通过后自动构建产物。
- 自动发布 Release。
- 自动上传包到 PyPI、npm、Docker Registry 等平台。
- 自动部署到服务器、云平台或 Kubernetes。

常见流程是：

```text
开发者 push 代码
  -> GitHub Actions 自动运行 CI
  -> lint 和 test 通过
  -> 合并到 main
  -> 打 tag
  -> 自动构建并发布 Release
```

## 2. GitHub Actions 文件放在哪里

GitHub Actions 的配置文件必须放在：

```text
.github/workflows/
```

常见命名：

```text
.github/workflows/ci.yml
.github/workflows/release.yml
.github/workflows/deploy.yml
```

文件名可以自定义，但必须是 `.yml` 或 `.yaml`。

## 3. 最小 CI 示例

```yaml
name: Python CI

on:
  push:
    branches: ["main"]
  pull_request:
    branches: ["main"]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          python -m pip install -e ".[dev]"

      - name: Run lint
        run: ruff check .

      - name: Run tests
        run: pytest
```

这个 workflow 会在 push、pull request、手动触发时运行。

这里的第一步很常见：

```yaml
- name: Check out repository
  uses: actions/checkout@v4
```

在 GitHub Actions 里，`checkout` 不是让你手动切换分支，而是把触发 workflow 的那份仓库代码下载到 CI 机器上。

它可以理解为：

```text
git clone 仓库
+ git checkout 当前触发 CI 的提交
```

如果是 push 触发，它会检出这次 push 后的提交；如果是 pull request 触发，它会检出 PR 对应的代码。没有这一步，后面的 `pytest`、`ruff check .` 通常会找不到项目文件。

## 4. 常见触发方式

### push 触发

```yaml
on:
  push:
    branches: ["main", "master"]
```

表示推送到 `main` 或 `master` 时运行。

### pull request 触发

```yaml
on:
  pull_request:
    branches: ["main"]
```

表示向 `main` 提交 PR 时运行。团队项目里最常用。

### 手动触发

```yaml
on:
  workflow_dispatch:
```

表示可以在 GitHub Actions 页面点击 `Run workflow` 手动运行。

### tag 触发

```yaml
on:
  push:
    tags:
      - "v*.*.*"
```

表示推送 `v1.0.0`、`v2.3.4` 这样的 tag 时运行。常用于发布 Release。

### 定时触发

```yaml
on:
  schedule:
    - cron: "0 2 * * *"
```

表示每天 UTC 时间 2 点运行。注意 GitHub Actions 的 cron 使用 UTC 时间，不是北京时间。

## 5. 常用 job 类型

### lint

lint 用于检查代码风格和潜在问题。

Python 常见工具：

```yaml
- name: Run lint
  run: ruff check .
```

### test

test 用于运行自动化测试。

```yaml
- name: Run tests
  run: pytest
```

### build

build 用于构建产物。

Python 标准包：

```yaml
- name: Build Python package
  run: |
    python -m pip install build
    python -m build
```

PyInstaller 可执行文件：

```yaml
- name: Build executable
  run: pyinstaller --onefile --name cicd-demo src/cicd_demo/cli.py
```

### release

release 用于创建 GitHub Release 并上传文件。

```yaml
- name: Create GitHub Release
  uses: softprops/action-gh-release@v2
  with:
    generate_release_notes: true
    files: dist/*
```

## 6. 多 Python 版本测试

如果项目要支持多个 Python 版本，可以使用 matrix：

```yaml
strategy:
  fail-fast: false
  matrix:
    python-version: ["3.10", "3.11", "3.12"]
```

然后这样引用：

```yaml
python-version: ${{ matrix.python-version }}
```

实际会运行 3 个 job：

```text
Python 3.10
Python 3.11
Python 3.12
```

适合开源库、SDK、长期维护项目。

## 7. 多平台打包

如果要分别给 Windows、Linux、macOS 打包，可以使用 matrix：

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

runs-on: ${{ matrix.os }}
```

PyInstaller 通常不能跨平台打包，所以要在对应系统上生成对应系统的可执行文件：

```text
Windows runner -> cicd-demo.exe
Linux runner   -> cicd-demo
macOS runner   -> cicd-demo
```

## 8. job 之间的依赖

使用 `needs` 控制 job 顺序：

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploy"
```

含义：

```text
test 成功后，deploy 才会运行。
```

如果 `test` 失败，`deploy` 默认不会运行。

## 9. artifact 和 release asset

artifact 是 workflow 运行过程中的临时产物。

```yaml
- name: Upload artifact
  uses: actions/upload-artifact@v4
  with:
    name: app
    path: dist/*
```

Release asset 是 GitHub Release 页面里的正式下载文件。

```yaml
- name: Download artifacts
  uses: actions/download-artifact@v4
  with:
    path: release-assets

- name: Create GitHub Release
  uses: softprops/action-gh-release@v2
  with:
    files: release-assets/**/*
```

简单理解：

```text
artifact = workflow 内部临时保存
release asset = 用户在 Release 页面下载
```

## 10. secrets 的使用

部署或发布时经常需要密钥，例如：

- 服务器 SSH key
- Docker token
- PyPI token
- 云平台 API key

不要把密钥写进代码。应该放在：

```text
Repository -> Settings -> Secrets and variables -> Actions
```

使用方式：

```yaml
env:
  API_TOKEN: ${{ secrets.API_TOKEN }}
```

或者：

```yaml
- name: Publish package
  run: python -m twine upload dist/*
  env:
    TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
```

## 11. permissions 权限

有些操作需要显式授权，比如创建 Release：

```yaml
permissions:
  contents: write
```

常见权限：

- `contents: read`：读取仓库内容。
- `contents: write`：写入仓库内容，比如创建 Release。
- `packages: write`：发布 GitHub Packages。
- `id-token: write`：用于 OIDC 云平台登录。

原则是只给需要的最小权限。

## 12. 分支保护

CI 本身不会阻止你 push。

但是仓库可以设置分支保护：

```text
Repository -> Settings -> Branches -> Branch protection rules
```

常见规则：

- 禁止直接 push 到 `main`。
- 必须通过 Pull Request 合并。
- 必须 CI 通过才能合并。
- 必须至少一个人 review。

团队协作时推荐打开：

```text
Require status checks to pass before merging
```

## 13. 常见项目 CI/CD 模板

### Python 库项目

```text
push / pull_request
  -> lint
  -> test
  -> build wheel
```

tag 发布：

```text
push tag
  -> test
  -> build wheel
  -> publish GitHub Release
  -> optionally publish PyPI
```

### Web 项目

```text
push / pull_request
  -> install dependencies
  -> lint
  -> test
  -> build frontend
```

main 分支部署：

```text
push main
  -> build
  -> deploy to server / Vercel / Netlify / cloud
```

### Docker 项目

```text
push main
  -> test
  -> docker build
  -> docker push
```

### 多平台桌面/CLI 工具

```text
push tag
  -> test
  -> build on windows-latest
  -> build on ubuntu-latest
  -> build on macos-latest
  -> upload all files to Release
```

## 14. 常见错误排查

### job 没有触发

检查：

- workflow 文件是否在 `.github/workflows/`。
- YAML 语法是否正确。
- 当前分支是否匹配 `branches`。
- tag 名是否匹配 `v*.*.*`。
- Actions 是否被仓库禁用。

### 找不到命令

例如：

```text
pytest: command not found
```

通常是依赖没安装。需要添加：

```yaml
- name: Install dependencies
  run: python -m pip install -e ".[dev]"
```

### 找不到代码

通常是忘了 checkout：

```yaml
- uses: actions/checkout@v4
```

注意这里的 `checkout` 容易和 Git 命令里的“切换分支”混淆。在 Actions 里你可以先把它理解为“把当前仓库代码准备到 CI 机器上”。CI 机器一开始是空的，不会自动带着你的 `src/`、`tests/`、`pyproject.toml`。

### Release 上传失败

检查：

```yaml
permissions:
  contents: write
```

以及 workflow 是否由 tag 触发。

### billing issue

如果看到：

```text
The job was not started because your account is locked due to a billing issue.
```

说明 job 没有开始运行，不是代码问题。需要检查 GitHub 账号或组织的 Billing 设置。

## 15. 推荐学习路线

1. 先写一个最小 CI，只跑 `pytest`。
2. 再加 `ruff check .`。
3. 再加 matrix，测试多个 Python 版本。
4. 再加 tag 触发的 Release。
5. 再学 artifact 和 Release asset。
6. 再学 secrets、permissions、分支保护。
7. 最后学习部署到服务器、Docker 或云平台。
