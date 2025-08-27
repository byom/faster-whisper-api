import requests
import os

# API 服务器的地址
API_URL = "http://127.0.0.1:5000/transcribe"

# 要上传的音频文件路径 (相对于脚本所在位置)
# 在 Windows 上使用 os.path.join 来确保路径分隔符正确
AUDIO_FILE_PATH = os.path.join("whisper_service", "test.mp3")

# 输出的 SRT 文件名
OUTPUT_SRT_PATH = "1.srt"

def test_transcribe():
    """
    发送音频文件到 /transcribe 端点并保存返回的 SRT 文件。
    """
    if not os.path.exists(AUDIO_FILE_PATH):
        print(f"错误: 测试音频文件未找到，请将 'test.mp3' 放置在 '{os.path.dirname(AUDIO_FILE_PATH)}' 目录下。")
        return

    try:
        # 以二进制读取模式打开文件
        with open(AUDIO_FILE_PATH, "rb") as audio_file:
            # 'files' 参数的格式是 {'name': (filename, file_object, content_type)}
            files = {"file": (os.path.basename(AUDIO_FILE_PATH), audio_file, "audio/mpeg")}
            
            print(f"正在上传 '{AUDIO_FILE_PATH}' 到 {API_URL}...")
            response = requests.post(API_URL, files=files)

            # 检查请求是否成功
            if response.status_code == 200:
                # 将响应内容写入 SRT 文件
                with open(OUTPUT_SRT_PATH, "wb") as srt_file:
                    srt_file.write(response.content)
                print(f"成功！转录结果已保存到 '{OUTPUT_SRT_PATH}'。")
            else:
                # 打印错误信息
                print(f"请求失败，状态码: {response.status_code}")
                print("服务器返回的错误信息:", response.json())

    except requests.exceptions.RequestException as e:
        print(f"请求时发生网络错误: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")

if __name__ == "__main__":
    test_transcribe()