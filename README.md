# Python GitHub CI/CD Demo

这是一个用于学习 GitHub CI/CD 的 Python 小项目。它包含：

- 一个简单的 Python 包：`src/cicd_demo`
- 一个命令行工具：`cicd-demo`
- 一组自动化测试：`tests`
- 一个 GitHub Actions 工作流：`.github/workflows/ci.yml`
- 一个多平台 Release 工作流：`.github/workflows/release.yml`

## 你会学到什么

1. 如何组织一个最小可运行的 Python 项目。
2. 如何用 `pytest` 写自动化测试。
3. 如何用 `ruff` 做基础代码检查。
4. 如何用 GitHub Actions 在 push 或 pull request 时自动运行 CI。
5. 如何观察 CI 失败、定位问题、修复后再次通过。

## 本地运行

先创建并激活虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

安装项目和开发依赖：

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

运行测试：

```powershell
pytest
```

运行代码检查：

```powershell
ruff check .
```

运行命令行工具：

```powershell
cicd-demo add 2 3
cicd-demo divide 10 2
cicd-demo fib 7
```

## GitHub Actions CI 如何触发

当前 CI 配置在 `.github/workflows/ci.yml` 中：

- 推送到 `main` 或 `master` 分支时触发。
- 向 `main` 或 `master` 发起 pull request 时触发。
- 也可以在 GitHub 页面手动点击 `Run workflow` 触发。

CI 会在 Python `3.10`、`3.11`、`3.12` 三个版本上执行：

1. 拉取代码。
2. 安装 Python。
3. 安装项目和开发依赖。
4. 运行 `ruff check .`。
5. 运行 `pytest`。

## GitHub Actions Release 如何触发

Release 配置在 `.github/workflows/release.yml` 中。

这个 workflow 用来模拟真实项目里常见的“打版本发布”：

- 先检查代码：运行 `ruff check .` 和 `pytest`。
- 再构建 Python 标准包：`.whl` 和 `.tar.gz`。
- 再分别在 Linux、Windows、macOS 机器上构建可执行文件。
- 最后创建 GitHub Release，并把所有产物上传到 Release 页面。

### 发布一个版本

假设你要发布 `v0.1.0`：

```powershell
git tag v0.1.0
git push origin v0.1.0
```

推送 tag 后，GitHub Actions 会自动运行 `Python Release`。

完成后打开仓库页面：

```text
GitHub 仓库 -> Releases
```

你应该能看到这些下载文件：

- `cicd_demo-0.1.0-py3-none-any.whl`
- `cicd_demo-0.1.0.tar.gz`
- `cicd-demo-linux.zip`
- `cicd-demo-windows.zip`
- `cicd-demo-macos.zip`

### 为什么要分别在不同系统打包

Python 源码可以跨平台，但 PyInstaller 生成的可执行文件通常不能跨平台。

也就是说：

- Windows 上生成 `.exe`
- Linux 上生成 Linux 可执行文件
- macOS 上生成 macOS 可执行文件

所以 Release workflow 使用了多个 runner：

```yaml
runs-on: ubuntu-latest
runs-on: windows-latest
runs-on: macos-latest
```

这就是你常见的“一个版本，多个机器下载包”。

### Release 和 CI 的关系

CI 主要回答：

```text
这次代码改动是否正确？
```

Release 主要回答：

```text
这个版本能不能打包并发布给别人下载？
```

当前 demo 的 Release 流程是：

```text
推送 tag
  -> validate 检查代码
  -> build-python-package 构建 Python 包
  -> build-executable 构建多平台可执行文件
  -> publish-release 创建 GitHub Release
```

## 学习练习

### 练习 1：让 CI 通过

1. 把代码推送到 GitHub。
2. 打开仓库页面的 `Actions` 标签。
3. 找到 `Python CI` workflow。
4. 确认所有 job 都是绿色通过。

### 练习 2：故意制造测试失败

把 `src/cicd_demo/calculator.py` 里的 `add` 改错，例如：

```python
def add(left: float, right: float) -> float:
    return left - right
```

然后提交并推送。你会看到 GitHub Actions 失败，因为 `tests/test_calculator.py` 里的测试会发现结果不对。

### 练习 3：修复失败

把 `add` 改回：

```python
def add(left: float, right: float) -> float:
    return left + right
```

再次提交并推送，CI 应该恢复通过。

## 推荐学习顺序

1. 先在本地跑通 `pytest` 和 `ruff check .`。
2. 再把项目推到 GitHub，观察 Actions 自动运行。
3. 故意改坏一处代码，看 CI 怎么报错。
4. 修复代码，再看 CI 变绿。
5. 尝试新增一个函数和一条测试，理解“代码 + 测试 + CI”的关系。
6. 创建 `v0.1.0` 这样的 tag，观察 Release 如何打包并上传多个平台产物。
