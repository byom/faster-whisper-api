# Faster-Whisper SRT 生成服务

本项目是一个基于 Flask 和 `faster-whisper` 的简单 Web 服务，用于将上传的音频文件转录为 SRT 字幕文件。

## 特性

- **高性能**: 使用 `faster-whisper` 库，比 OpenAI 的 whisper 更快、内存占用更少。
- **按需加载**: 仅在处理请求时加载模型，处理完毕后立即释放，有效降低闲置时的 GPU 显存/内存占用。
- **SRT 格式输出**: 直接返回行业标准的 `.srt` 字幕文件。
- **易于部署**: 简单的 Python 和 Flask 应用，依赖清晰。

## 安装指南

### 1. 环境要求

- Python 3.8+
- NVIDIA GPU (推荐, 用于 CUDA 加速)
- [CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit-archive) (版本需与 PyTorch 和 CTranslate2 兼容, 例如 11.8 或 12.1)
- [cuDNN](https://developer.nvidia.com/cudnn)

### 2. 创建虚拟环境 (推荐)

在项目根目录下，使用 `venv` 创建一个独立的 Python 环境。

```cmd
:: 1. 创建名为 venv 的虚拟环境
python -m venv venv

:: 2. 激活虚拟环境
.\venv\Scripts\activate
```

激活后，你的命令行提示符前会显示 `(venv)`。

### 3. 安装依赖

在**已激活的虚拟环境**中，通过 pip 安装所需的 Python 包。

```bash
pip install Flask
pip install faster-whisper
pip install requests
pip install torch torchaudio torchvision --index-url https://download.pytorch.org/whl/cu118

### 4. 运行服务

在项目根目录下（确保虚拟环境已激活）运行以下命令启动服务：

```bash
python app.py
```

服务将启动在 `http://0.0.0.0:5000`。

## 如何使用

### 使用 `curl` 的示例 (Windows)

打开一个新的终端，执行以下命令。请将 `path\to\your\audio.mp3` 替换为您自己的音频文件路径。

```cmd
curl -X POST -F "file=@path\to\your\audio.mp3" http://127.0.0.1:5000/transcribe -o output.srt
```

### 使用 Python 测试脚本

1.  **准备音频文件**: 将一个名为 `1.mp3` 的音频文件放置在项目根目录下的 `.whisper_service` 文件夹中。如果该文件夹不存在，请手动创建。最终文件路径应为 `.\whisper_service\1.mp3`。

2.  **创建测试脚本**: 在项目根目录下创建一个名为 `test_client.py` 的文件，并将以下内容复制进去。

3.  **运行测试**: 确保 `app.py` 服务正在运行，然后打开一个新的终端（如果需要，也请激活虚拟环境），运行测试脚本：

    ```bash
    python test_client.py
    ```

    脚本执行成功后，会在项目根目录下生成一个 `1.srt` 文件，其中包含转录的字幕。
