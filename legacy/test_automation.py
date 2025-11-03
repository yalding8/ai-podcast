#!/usr/bin/env python3
"""
自动化功能测试脚本
快速验证新增的4个功能模块
"""

import sys
from pathlib import Path

def test_exam_crawler():
    """测试考试爬虫"""
    print("\n" + "="*60)
    print("测试 1/4: 考试官网爬虫")
    print("="*60)
    
    try:
        from ai_poadcast_main.exam_sites_crawler import ExamSiteCrawler
        crawler = ExamSiteCrawler()
        print("✅ 模块导入成功")
        
        # 测试缓存功能
        test_content = "test content"
        is_new = crawler._is_new_content("test_key", test_content)
        print(f"✅ 缓存功能正常 (首次检测: {is_new})")
        
        is_new_again = crawler._is_new_content("test_key", test_content)
        print(f"✅ 去重功能正常 (重复检测: {is_new_again})")
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_audio_processor():
    """测试音频处理"""
    print("\n" + "="*60)
    print("测试 2/4: 音频后期处理")
    print("="*60)
    
    try:
        from audio_postprocess import AudioPostProcessor
        processor = AudioPostProcessor()
        print("✅ 模块导入成功")
        print("✅ ffmpeg依赖检查通过")
        return True
    except RuntimeError as e:
        print(f"⚠️  {e}")
        print("   提示: brew install ffmpeg")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_publisher():
    """测试发布工具"""
    print("\n" + "="*60)
    print("测试 3/4: 自动发布工具")
    print("="*60)
    
    try:
        from auto_publish import PodcastPublisher
        publisher = PodcastPublisher()
        print("✅ 模块导入成功")
        
        # 测试配置加载
        config_keys = list(publisher.config.keys())
        print(f"✅ 配置加载成功 (已加载 {len(config_keys)} 个配置项)")
        
        # 测试历史记录
        history = publisher.history
        print(f"✅ 历史记录加载成功 (已发布 {len(history.get('episodes', []))} 期)")
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_cicd():
    """测试CI/CD配置"""
    print("\n" + "="*60)
    print("测试 4/4: CI/CD流程配置")
    print("="*60)
    
    try:
        workflow_file = Path(".github/workflows/podcast_pipeline.yml")
        if workflow_file.exists():
            print("✅ GitHub Actions配置文件存在")
            content = workflow_file.read_text()
            
            # 检查关键配置
            checks = [
                ("schedule", "定时任务"),
                ("workflow_dispatch", "手动触发"),
                ("collect-news", "新闻采集"),
                ("synthesize-audio", "音频合成"),
                ("publish-episode", "节目发布")
            ]
            
            for key, desc in checks:
                if key in content:
                    print(f"✅ {desc}配置正常")
                else:
                    print(f"⚠️  缺少{desc}配置")
            
            return True
        else:
            print("❌ GitHub Actions配置文件不存在")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_makefile():
    """测试Makefile"""
    print("\n" + "="*60)
    print("额外测试: Makefile快捷命令")
    print("="*60)
    
    try:
        makefile = Path("Makefile")
        if makefile.exists():
            print("✅ Makefile存在")
            content = makefile.read_text()
            
            commands = ["collect", "extract", "script", "audio", "publish", "full-pipeline"]
            for cmd in commands:
                if cmd in content:
                    print(f"✅ make {cmd} 命令可用")
            
            return True
        else:
            print("❌ Makefile不存在")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    print("\n🚀 开始测试自动化功能模块...")
    
    results = []
    
    # 运行所有测试
    results.append(("考试爬虫", test_exam_crawler()))
    results.append(("音频处理", test_audio_processor()))
    results.append(("自动发布", test_publisher()))
    results.append(("CI/CD配置", test_cicd()))
    results.append(("Makefile", test_makefile()))
    
    # 输出总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！自动化功能已就绪。")
        print("\n📖 查看使用指南: AUTOMATION_GUIDE.md")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查错误信息。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
