import os
import subprocess
import sys
from pathlib import Path
from textwrap import wrap
import shutil

# 目录与文件配置
SCRIPT_PATH = Path(__file__).resolve()
ROOT_DIR = None
for parent in SCRIPT_PATH.parents:
    if parent.name == "AI POADCAST":
        ROOT_DIR = parent
        break
if ROOT_DIR is None:
    sys.exit("未找到项目根目录（AI POADCAST）。请检查脚本所在路径。")

STEP = 420  # 每段字符长度，可按需调整
INPUT_FILE = ROOT_DIR / "script.txt"
CHUNK_DIR = ROOT_DIR / "script_chunks"
PARTS_DIR = ROOT_DIR / "audio_parts"
OUTPUT_WAV = ROOT_DIR / "podcast_episode.wav"
MAKE_MP3 = False
OUTPUT_MP3 = ROOT_DIR / "podcast_episode.mp3" if MAKE_MP3 else None

APP_ID = os.environ.get("OPEN_SPEECH_APPID")
TOKEN = os.environ.get("OPEN_SPEECH_TOKEN")
VOICE = os.environ.get("OPEN_SPEECH_VOICE", "zh_female_cancan_mars_bigtts")

DEMO_SCRIPT = ROOT_DIR / "vendor/volcengine_ws_demo/examples/volcengine/binary.py"
PYTHON = ROOT_DIR / ".venv/bin/python"
PYTHONPATH = ROOT_DIR / "vendor/volcengine_ws_demo"

if not INPUT_FILE.exists():
    sys.exit(f"未找到脚本文件：{INPUT_FILE}")
if not (APP_ID and TOKEN):
    sys.exit("请先 export OPEN_SPEECH_APPID 和 OPEN_SPEECH_TOKEN。")

# 1. 拆分脚本
text = INPUT_FILE.read_text(encoding="utf-8").strip()
chunks = wrap(text, STEP)

if CHUNK_DIR.exists():
    shutil.rmtree(CHUNK_DIR)
if PARTS_DIR.exists():
    shutil.rmtree(PARTS_DIR)
CHUNK_DIR.mkdir()
PARTS_DIR.mkdir()

for idx, chunk in enumerate(chunks, 1):
    (CHUNK_DIR / f"chunk_{idx:02d}.txt").write_text(chunk, encoding="utf-8")

# 2. 逐段调用 demo
for file in sorted(CHUNK_DIR.glob("chunk_*.txt")):
    base = file.stem
    cmd = [
        str(PYTHON),
        str(DEMO_SCRIPT),
        "--appid", APP_ID,
        "--access_token", TOKEN,
        "--voice_type", VOICE,
        "--text", Path(file).read_text(encoding="utf-8").replace("\n", " "),
    ]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PYTHONPATH)
    print(f"[INFO] 合成 {file.name} ...")
    subprocess.run(cmd, env=env, check=True)

    demo_output = Path(f"{VOICE}.wav")
    if not demo_output.exists():
        raise FileNotFoundError(f"未找到 demo 输出 {demo_output}")
    demo_output.rename(PARTS_DIR / f"{base}.wav")

# 3. 使用 ffmpeg 拼接
concat_list = "\n".join(
    f"file '{(PARTS_DIR / f).resolve()}'" for f in sorted(f.name for f in PARTS_DIR.glob("*.wav"))
)
concat_file = PARTS_DIR / "concat.txt"
concat_file.write_text(concat_list, encoding="utf-8")

subprocess.run(
    ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
     "-c", "copy", str(OUTPUT_WAV)],
    check=True,
)
print(f"[INFO] 合并完成：{OUTPUT_WAV}")

# 若需要 MP3，可转换
if OUTPUT_MP3:
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(OUTPUT_WAV),
         "-ar", "44100", "-ac", "2", "-b:a", "192k", str(OUTPUT_MP3)],
        check=True,
    )
    print(f"[INFO] 已生成 MP3：{OUTPUT_MP3}")
