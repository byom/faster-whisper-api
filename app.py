from flask import Flask, request, jsonify, send_file
from faster_whisper import WhisperModel
import os
import uuid
import gc
import torch
from collections import namedtuple
from typing import List, Iterator
SegmentTuple = namedtuple('SegmentTuple', ['start', 'end', 'text'])

app = Flask(__name__)

# 模型配置
MODEL_SIZE = "large-v2"
COMPUTE_TYPE = "int8_float16" # or "float16" for better accuracy
DEVICE = "cuda"

# 上传文件目录
UPLOAD_FOLDER = "./whisper_service"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def format_timestamp(seconds):
    """将秒转换为SRT时间戳格式 (HH:MM:SS,ms)"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def split_long_segments(transcribe_result: Iterator, max_duration: int = 8) -> List:
    """
    Splits long subtitle segments from Whisper's result into smaller chunks.

    Args:
        transcribe_result: The raw result from model.transcribe().
        max_duration: The maximum duration (in seconds) for each subtitle segment.

    Returns:
        A new list of segments, where all segments adhere to the max_duration.
    """
    new_segments = []
    original_segments = list(transcribe_result)

    for segment in original_segments:
        # If the segment has no word timestamps or is already short enough, add it as is
        # CORRECTED: Use attribute access (segment.words) instead of dict access (segment['words'])
        if not segment.words or (segment.end - segment.start) <= max_duration:
            new_segments.append(segment)
            continue

        # If the segment is too long, split it based on word timestamps
        current_sub_segment_start_time = segment.start
        current_sub_segment_text = ""
        words_in_sub_segment = []

        # CORRECTED: Iterate through segment.words
        for word in segment.words:
            # CORRECTED: Use attribute access for word data (word.end, word.start, word.word)
            word_start, word_end, word_text = word.start, word.end, word.word

            # If adding the current word would exceed the max duration, finalize the current sub-segment
            if word_end is not None and (word_end - current_sub_segment_start_time > max_duration):
                if words_in_sub_segment:
                    # Create a new segment and add it to our list
                    # CORRECTED: Create a SegmentTuple object instead of a dictionary
                    # to maintain attribute access (.start, .end, .text)
                    last_word_end = words_in_sub_segment[-1].end
                    new_segments.append(SegmentTuple(
                        start=current_sub_segment_start_time,
                        end=last_word_end,
                        text=current_sub_segment_text.strip()
                    ))

                # Start a new sub-segment with the current word
                current_sub_segment_start_time = word_start
                current_sub_segment_text = word_text
                words_in_sub_segment = [word]
            else:
                # Otherwise, continue adding words to the current sub-segment
                current_sub_segment_text += word_text
                words_in_sub_segment.append(word)

        # Add the final sub-segment after the loop finishes
        if words_in_sub_segment:
            last_word_end = words_in_sub_segment[-1].end
            # CORRECTED: Also create a SegmentTuple for the last part
            new_segments.append(SegmentTuple(
                start=current_sub_segment_start_time,
                end=last_word_end,
                text=current_sub_segment_text.strip()
            ))

    return new_segments

@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # 保存上传的音频文件
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    srt_path = filepath.rsplit('.', 1)[0] + ".srt"
    model = None
    
    try:
        # 1. 按需加载模型
        print(f"Loading model '{MODEL_SIZE}'...")
        model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)
        
        # 2. 处理音频并生成SRT
        print(f"Transcribing file: {filepath}")
        segments, info = model.transcribe(filepath, beam_size=5, word_timestamps=True, vad_filter=True)

        # 3. 裁切过大分段
        # segments = split_long_segments(segments, max_duration=6)

        print(f"Detected language '{info.language}' with probability {info.language_probability}")

        with open(srt_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(segments, start=1):
                start_time = format_timestamp(segment.start)
                end_time = format_timestamp(segment.end)
                text = segment.text.strip()
                f.write(f"{i}\n{start_time} --> {end_time}\n{text}\n\n")
        
        print(f"SRT file generated: {srt_path}")
        return send_file(srt_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        # 3. 释放模型以清理内存
        if model is not None:
            del model
            gc.collect()
            if DEVICE == "cuda":
                torch.cuda.empty_cache()
            print("Model released from memory.")
        
        # 清理临时文件
        if os.path.exists(filepath):
            os.remove(filepath)
        # srt_path 在成功时由 send_file 处理，但在出错时可能需要清理
        if os.path.exists(srt_path) and not request.environ.get('werkzeug.request'):
             os.remove(srt_path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
