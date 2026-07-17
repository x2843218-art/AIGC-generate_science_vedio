# Seedance 批量视频生成项目

本项目用于把第一章节的分镜 prompt 批量提交到火山方舟 Ark / Seedance，生成 n 个镜头视频，并通过 FFmpeg 拼接成完整的 `chapter01.mp4`。当前脚本已经跑通，文档只说明现有流程与文件职责。

## 项目结构

```text
QUANTUN-DOCUMENT/
├── demo_standard.py
├── scripts/
│   ├── generate_chapter.py
│   └── merge_chapter.py
├── prompts/
│   └── chapter01/
│       └── chapter01.json
└── outputs/
    ├── shots/
    │   ├── shot001.mp4
    │   ├── shot002.mp4
    │   └── ...
    └── chapter01.mp4
```

核心文件说明：

- `demo_standard.py`：单条 Seedance 测试脚本，用于验证 API Key、模型调用、任务创建和轮询是否正常。
- `scripts/generate_chapter.py`：批量生成镜头视频脚本，会读取章节分镜 prompt，为每个 shot 创建 Seedance 任务，并下载生成结果。
- `prompts/chapter01/chapter01.json`：第一章节分镜 prompt 文件，按 shot 组织镜头编号、时长、画面 prompt 和备注。
- `outputs/shots/`：批量生成后的镜头视频目录，用于保存 `shot001.mp4` 到 `shotXXX.mp4`。
- `scripts/merge_chapter.py`：调用 FFmpeg，把 `outputs/shots/` 下的 n 个镜头按顺序拼接成第一章节视频。
- `outputs/chapter01.mp4`：第一章节最终拼接输出，可用于汇报预览或继续叠加配音、字幕等后期流程。

## 环境准备

建议在 `QUANTUN-DOCUMENT` 目录下运行所有命令：

```powershell
cd C:\codex_project\codex_science_vedio\QUANTUN-DOCUMENT
```

### 1. 设置 ARK_API_KEY

PowerShell 临时设置：

```powershell
$env:ARK_API_KEY="your_ark_api_key"
```

macOS / Linux shell：

```bash
export ARK_API_KEY="your_ark_api_key"
```

注意：以上方式只对当前终端窗口生效。重新打开终端后，需要重新设置，或配置到系统环境变量中。

### 2. 安装 Python 依赖

项目调用的是火山方舟 Ark SDK：

```bash
pip install "volcengine-python-sdk[ark]"
```

如果本地已经能运行 `demo_standard.py`，说明当前 Python 环境基本可用，可以继续沿用。

### 3. 安装 FFmpeg

拼接章节时需要 FFmpeg。确认是否可用：

```bash
ffmpeg -version
```

如果命令不可用，可以安装 FFmpeg 并加入 PATH，或在运行 `merge_chapter.py` 时通过 `--ffmpeg` 传入 `ffmpeg.exe` 的完整路径。

## 运行流程

### 1. 单条测试

先用单条脚本验证 Seedance 调用链路：

```bash
python demo_standard.py
```

该脚本会提交一条固定 prompt，打印任务 ID，并轮询任务状态。看到 `succeeded` 说明 API Key、SDK、模型调用和网络访问都正常。

### 2. 批量生成第一章节镜头

执行：

```bash
python scripts/generate_chapter.py
```

默认读取：

```text
prompts/chapter01/chapter01.json
```

默认输出：

```text
outputs/shots/shot001.mp4
outputs/shots/shot002.mp4
...
outputs/shots/shotXXX.mp4
```

脚本会按分镜顺序逐条创建 Seedance 任务，等待任务完成后下载视频。每个镜头保存为对应的 `shotXXX.mp4` 文件。

如需显式指定输入和输出目录：

```bash
python scripts/generate_chapter.py --prompt-dir prompts/chapter01 --output-dir outputs/shots
```

### 3. 拼接第一章节

确认 `outputs/shots/` 中已经存在 `shot001.mp4` 到 `shot012.mp4` 后，执行：

```bash
python scripts/merge_chapter.py
```

默认输出：

```text
outputs/chapter01.mp4
```

如果 FFmpeg 不在 PATH 中，可以这样指定：

```bash
python scripts/merge_chapter.py --ffmpeg C:\path\to\ffmpeg.exe
```

## 常见问题排查

### ARK_API_KEY is not set

说明当前终端没有读取到 `ARK_API_KEY`。在同一个终端窗口中重新执行：

```powershell
$env:ARK_API_KEY="your_ark_api_key"
```

然后再运行脚本。

### SDK 导入失败

如果看到 `ModuleNotFoundError: No module named 'volcenginesdkarkruntime'`，说明依赖没有安装到当前 Python 环境。执行：

```bash
pip install "volcengine-python-sdk[ark]"
```

如果电脑中有多个 Python 版本，需要确认 `python` 和 `pip` 指向同一个环境。

### Seedance 任务失败

如果任务状态变为 `failed`，先查看脚本打印的错误信息。常见原因包括 API Key 无效、账户权限不足、模型名不可用、prompt 参数不符合平台要求，或平台侧任务临时失败。

建议先运行 `python demo_standard.py` 做最小化验证，再回到批量脚本定位是哪一个 shot 失败。

### 下载视频失败

批量脚本会从任务结果中解析视频 URL 并下载到 `outputs/shots/`。如果下载失败，可能是网络连接、URL 过期或任务结果未返回视频地址。可以重新运行失败的镜头，或检查控制台中对应 shot 的任务结果。

### FFmpeg 找不到

如果拼接时报 `Cannot find ffmpeg executable`，说明系统 PATH 中没有 FFmpeg。可以把 FFmpeg 加入 PATH，或使用：

```bash
python scripts/merge_chapter.py --ffmpeg C:\path\to\ffmpeg.exe
```

### 拼接时报缺少 shot 文件

`scripts/merge_chapter.py` 默认要求 `outputs/shots/shot001.mp4` 到 `outputs/shots/shot012.mp4` 都存在。若报缺失文件，先检查批量生成是否全部完成，再补生成缺失的镜头。

### chapter01.mp4 没有更新

确认拼接命令是否成功结束，并检查输出路径是否仍为默认的 `outputs/chapter01.mp4`。如果使用了 `--output` 参数，最终文件会保存到指定路径。

## 当前已跑通产物

当前项目中已经存在：

- `outputs/shots/shot001.mp4` 到 `outputs/shots/shotXXX.mp4`
- `outputs/chapter01.mp4`

这说明第一章节已经完成了从分镜 prompt、Seedance 批量生成、镜头下载到 FFmpeg 拼接的主流程。
