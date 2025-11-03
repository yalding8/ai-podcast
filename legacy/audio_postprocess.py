#!/usr/bin/env python3
"""
音频后期处理工具
支持音量标准化、降噪、添加片头片尾、音乐混音等
"""

import subprocess
from pathlib import Path
from typing import Optional
import json

class AudioPostProcessor:
    def __init__(self):
        self.check_dependencies()
    
    def check_dependencies(self):
        """检查ffmpeg是否安装"""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("需要安装ffmpeg: brew install ffmpeg")
    
    def normalize_volume(self, input_file: str, output_file: str, target_db: float = -16.0):
        """音量标准化（响度标准化）"""
        print(f"🔊 标准化音量: {input_file}")
        cmd = [
            'ffmpeg', '-i', input_file,
            '-af', f'loudnorm=I={target_db}:TP=-1.5:LRA=11',
            '-ar', '44100',
            '-y', output_file
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✅ 已保存: {output_file}")
    
    def add_intro_outro(self, 
                        main_audio: str, 
                        output_file: str,
                        intro_audio: Optional[str] = None,
                        outro_audio: Optional[str] = None):
        """添加片头片尾"""
        print(f"🎬 添加片头片尾: {main_audio}")
        
        # 创建拼接列表
        concat_list = []
        if intro_audio and Path(intro_audio).exists():
            concat_list.append(f"file '{intro_audio}'")
        concat_list.append(f"file '{main_audio}'")
        if outro_audio and Path(outro_audio).exists():
            concat_list.append(f"file '{outro_audio}'")
        
        # 写入临时文件
        concat_file = Path(output_file).parent / "concat_list.txt"
        concat_file.write_text('\n'.join(concat_list))
        
        # 拼接音频
        cmd = [
            'ffmpeg', '-f', 'concat', '-safe', '0',
            '-i', str(concat_file),
            '-c', 'copy',
            '-y', output_file
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        concat_file.unlink()
        print(f"✅ 已保存: {output_file}")
    
    def add_background_music(self,
                            voice_file: str,
                            music_file: str,
                            output_file: str,
                            music_volume: float = 0.1):
        """添加背景音乐"""
        print(f"🎵 添加背景音乐: {voice_file}")
        cmd = [
            'ffmpeg',
            '-i', voice_file,
            '-i', music_file,
            '-filter_complex',
            f'[1:a]volume={music_volume}[music];[0:a][music]amix=inputs=2:duration=first',
            '-y', output_file
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✅ 已保存: {output_file}")
    
    def reduce_noise(self, input_file: str, output_file: str):
        """降噪处理（简单高通滤波）"""
        print(f"🔇 降噪处理: {input_file}")
        cmd = [
            'ffmpeg', '-i', input_file,
            '-af', 'highpass=f=200,lowpass=f=3000',
            '-y', output_file
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✅ 已保存: {output_file}")
    
    def convert_format(self, input_file: str, output_file: str, bitrate: str = '128k'):
        """格式转换"""
        print(f"🔄 转换格式: {input_file} -> {output_file}")
        cmd = [
            'ffmpeg', '-i', input_file,
            '-b:a', bitrate,
            '-y', output_file
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✅ 已保存: {output_file}")
    
    def full_pipeline(self,
                     input_file: str,
                     output_file: str,
                     intro_audio: Optional[str] = None,
                     outro_audio: Optional[str] = None,
                     music_file: Optional[str] = None,
                     music_volume: float = 0.1):
        """完整后期处理流程"""
        print("\n🎬 开始音频后期处理流程...")
        
        temp_dir = Path(output_file).parent / "temp"
        temp_dir.mkdir(exist_ok=True)
        
        current_file = input_file
        
        # 1. 音量标准化
        normalized = temp_dir / "01_normalized.mp3"
        self.normalize_volume(current_file, str(normalized))
        current_file = str(normalized)
        
        # 2. 添加背景音乐（如果有）
        if music_file and Path(music_file).exists():
            with_music = temp_dir / "02_with_music.mp3"
            self.add_background_music(current_file, music_file, str(with_music), music_volume)
            current_file = str(with_music)
        
        # 3. 添加片头片尾（如果有）
        if intro_audio or outro_audio:
            with_intro_outro = temp_dir / "03_with_intro_outro.mp3"
            self.add_intro_outro(current_file, str(with_intro_outro), intro_audio, outro_audio)
            current_file = str(with_intro_outro)
        
        # 4. 最终输出
        self.convert_format(current_file, output_file, bitrate='192k')
        
        # 清理临时文件
        import shutil
        shutil.rmtree(temp_dir)
        
        print(f"\n✅ 后期处理完成: {output_file}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='音频后期处理工具')
    parser.add_argument('--input', required=True, help='输入音频文件')
    parser.add_argument('--output', required=True, help='输出音频文件')
    parser.add_argument('--intro', help='片头音频')
    parser.add_argument('--outro', help='片尾音频')
    parser.add_argument('--music', help='背景音乐')
    parser.add_argument('--music-volume', type=float, default=0.1, help='背景音乐音量(0-1)')
    parser.add_argument('--normalize-only', action='store_true', help='仅标准化音量')
    
    args = parser.parse_args()
    
    processor = AudioPostProcessor()
    
    if args.normalize_only:
        processor.normalize_volume(args.input, args.output)
    else:
        processor.full_pipeline(
            args.input,
            args.output,
            intro_audio=args.intro,
            outro_audio=args.outro,
            music_file=args.music,
            music_volume=args.music_volume
        )

if __name__ == "__main__":
    main()
