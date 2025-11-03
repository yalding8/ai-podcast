#!/usr/bin/env python3
"""
自动发布工具
支持发布到小宇宙、喜马拉雅、Apple Podcasts等平台
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import hashlib

class PodcastPublisher:
    def __init__(self, config_file: str = ".env"):
        self.config = self._load_config(config_file)
        self.publish_log = Path("ai_poadcast_main/publish_log.json")
        self.history = self._load_history()
    
    def _load_config(self, config_file: str) -> Dict:
        """加载配置"""
        config = {}
        if Path(config_file).exists():
            with open(config_file) as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        config[key] = value.strip('"').strip("'")
        return config
    
    def _load_history(self) -> Dict:
        """加载发布历史"""
        if self.publish_log.exists():
            return json.loads(self.publish_log.read_text())
        return {"episodes": []}
    
    def _save_history(self):
        """保存发布历史"""
        self.publish_log.write_text(json.dumps(self.history, indent=2, ensure_ascii=False))
    
    def _get_file_hash(self, file_path: str) -> str:
        """计算文件哈希"""
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def publish_to_xiaoyuzhou(self, 
                              audio_file: str,
                              title: str,
                              description: str,
                              cover_image: Optional[str] = None) -> bool:
        """发布到小宇宙（需要API密钥）"""
        print(f"📡 发布到小宇宙: {title}")
        
        api_key = self.config.get('XIAOYUZHOU_API_KEY')
        if not api_key:
            print("⚠️  未配置小宇宙API密钥")
            return False
        
        # 小宇宙API调用（示例）
        # 实际API需要根据小宇宙官方文档调整
        try:
            url = "https://api.xiaoyuzhoufm.com/v1/episodes"
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            # 上传音频文件
            with open(audio_file, 'rb') as f:
                files = {'audio': f}
                upload_resp = requests.post(
                    f"{url}/upload",
                    headers=headers,
                    files=files,
                    timeout=300
                )
                audio_url = upload_resp.json().get('url')
            
            # 创建节目
            data = {
                'title': title,
                'description': description,
                'audio_url': audio_url,
                'cover_image': cover_image
            }
            
            resp = requests.post(url, headers=headers, json=data, timeout=30)
            resp.raise_for_status()
            
            print(f"✅ 小宇宙发布成功")
            return True
            
        except Exception as e:
            print(f"❌ 小宇宙发布失败: {e}")
            return False
    
    def publish_to_ximalaya(self,
                           audio_file: str,
                           title: str,
                           description: str) -> bool:
        """发布到喜马拉雅（需要API密钥）"""
        print(f"📡 发布到喜马拉雅: {title}")
        
        api_key = self.config.get('XIMALAYA_API_KEY')
        if not api_key:
            print("⚠️  未配置喜马拉雅API密钥")
            return False
        
        try:
            # 喜马拉雅开放平台API
            url = "https://api.ximalaya.com/openapi-gateway-app/v1/upload"
            
            # 实际实现需要根据喜马拉雅官方文档
            print("⚠️  喜马拉雅API需要根据官方文档实现")
            return False
            
        except Exception as e:
            print(f"❌ 喜马拉雅发布失败: {e}")
            return False
    
    def generate_rss_feed(self,
                         audio_file: str,
                         title: str,
                         description: str,
                         episode_number: int,
                         pub_date: Optional[str] = None) -> str:
        """生成RSS Feed（用于Apple Podcasts等）"""
        print(f"📝 生成RSS Feed: {title}")
        
        if not pub_date:
            pub_date = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')
        
        # 读取现有RSS或创建新的
        rss_file = Path("audio_exports/podcast_feed.xml")
        
        if rss_file.exists():
            rss_content = rss_file.read_text()
        else:
            rss_content = self._create_rss_template()
        
        # 添加新节目
        episode_xml = f"""
    <item>
      <title>{title}</title>
      <description>{description}</description>
      <enclosure url="{self._get_audio_url(audio_file)}" type="audio/mpeg"/>
      <guid>{self._get_file_hash(audio_file)}</guid>
      <pubDate>{pub_date}</pubDate>
      <itunes:episode>{episode_number}</itunes:episode>
      <itunes:duration>{self._get_audio_duration(audio_file)}</itunes:duration>
    </item>
"""
        
        # 插入到RSS中
        rss_content = rss_content.replace('</channel>', f'{episode_xml}\n  </channel>')
        rss_file.write_text(rss_content)
        
        print(f"✅ RSS Feed已更新: {rss_file}")
        return str(rss_file)
    
    def _create_rss_template(self) -> str:
        """创建RSS模板"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>异乡早咖啡</title>
    <description>国际教育资讯播客</description>
    <language>zh-cn</language>
    <link>https://your-podcast-website.com</link>
    <itunes:author>大刘</itunes:author>
    <itunes:category text="Education"/>
  </channel>
</rss>"""
    
    def _get_audio_url(self, audio_file: str) -> str:
        """获取音频URL（需要配置CDN或服务器）"""
        base_url = self.config.get('AUDIO_BASE_URL', 'https://your-cdn.com/audio')
        filename = Path(audio_file).name
        return f"{base_url}/{filename}"
    
    def _get_audio_duration(self, audio_file: str) -> str:
        """获取音频时长"""
        try:
            import subprocess
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 
                 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
                 audio_file],
                capture_output=True,
                text=True
            )
            duration = float(result.stdout.strip())
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            return f"{minutes:02d}:{seconds:02d}"
        except:
            return "00:00"
    
    def publish_episode(self,
                       audio_file: str,
                       title: str,
                       description: str,
                       platforms: list = ['rss'],
                       cover_image: Optional[str] = None):
        """发布节目到多个平台"""
        print(f"\n🚀 开始发布节目: {title}")
        print(f"   音频文件: {audio_file}")
        print(f"   目标平台: {', '.join(platforms)}")
        
        results = {}
        episode_number = len(self.history['episodes']) + 1
        
        for platform in platforms:
            if platform == 'xiaoyuzhou':
                results[platform] = self.publish_to_xiaoyuzhou(
                    audio_file, title, description, cover_image
                )
            elif platform == 'ximalaya':
                results[platform] = self.publish_to_ximalaya(
                    audio_file, title, description
                )
            elif platform == 'rss':
                rss_file = self.generate_rss_feed(
                    audio_file, title, description, episode_number
                )
                results[platform] = True
        
        # 记录发布历史
        self.history['episodes'].append({
            'episode_number': episode_number,
            'title': title,
            'audio_file': audio_file,
            'platforms': results,
            'published_at': datetime.now().isoformat()
        })
        self._save_history()
        
        print(f"\n✅ 发布完成")
        print(f"   成功: {sum(1 for v in results.values() if v)}/{len(results)}")
        
        return results

def main():
    import argparse
    parser = argparse.ArgumentParser(description='播客自动发布工具')
    parser.add_argument('--audio', required=True, help='音频文件路径')
    parser.add_argument('--title', required=True, help='节目标题')
    parser.add_argument('--description', required=True, help='节目描述')
    parser.add_argument('--platforms', nargs='+', default=['rss'],
                       choices=['xiaoyuzhou', 'ximalaya', 'rss'],
                       help='发布平台')
    parser.add_argument('--cover', help='封面图片')
    
    args = parser.parse_args()
    
    publisher = PodcastPublisher()
    publisher.publish_episode(
        args.audio,
        args.title,
        args.description,
        platforms=args.platforms,
        cover_image=args.cover
    )

if __name__ == "__main__":
    main()
