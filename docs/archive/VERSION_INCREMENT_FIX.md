# 脚本版本号自动递增修复

## 问题描述

之前运行 `make full-pipeline` 时，如果脚本文件已存在会报错：

```
❌ 写入失败：目标文件已存在：脚本输出/2025-11-03/episode_2025-11-03_v1.md（使用 --overwrite 覆盖）
make: *** [full-pipeline] Error 1
```

## 解决方案

修改了 `generate_stage3_script.py`，实现**自动版本号递增**功能。

### 修改内容

**文件**: `ai_poadcast_main/generate_stage3_script.py`

**修改函数**: `resolve_output_path()`

```python
def resolve_output_path(episode_date: str, output: Optional[str], overwrite: bool) -> Path:
    if output:
        return Path(output)
    
    target_dir = STAGE3_OUTPUT_DIR / episode_date
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # 如果不覆盖，自动找下一个可用版本号
    if not overwrite:
        version = 1
        while True:
            path = target_dir / f"episode_{episode_date}_v{version}.md"
            if not path.exists():
                return path
            version += 1
            if version > 99:  # 防止无限循环
                raise RuntimeError(f"版本号超过99，请检查目录：{target_dir}")
    
    return target_dir / f"episode_{episode_date}_v1.md"
```

## 工作原理

### 默认模式（不覆盖）
1. 检查 `episode_2025-11-03_v1.md` 是否存在
2. 如果存在，检查 `v2.md`
3. 如果 `v2.md` 也存在，检查 `v3.md`
4. 以此类推，直到找到不存在的版本号
5. 最多支持到 `v99`

### 覆盖模式（--overwrite）
- 直接覆盖 `v1.md`
- 需要显式指定 `--overwrite` 参数

## 使用示例

### 场景1：首次生成（推荐）
```bash
python ai_poadcast_main/generate_stage3_script.py --date 2025-11-03
# 输出: ✅ 已生成脚本：脚本输出/2025-11-03/episode_2025-11-03_v1.md
```

### 场景2：再次生成（自动递增）
```bash
python ai_poadcast_main/generate_stage3_script.py --date 2025-11-03
# 输出: ✅ 已生成脚本：脚本输出/2025-11-03/episode_2025-11-03_v2.md
```

### 场景3：第三次生成
```bash
python ai_poadcast_main/generate_stage3_script.py --date 2025-11-03
# 输出: ✅ 已生成脚本：脚本输出/2025-11-03/episode_2025-11-03_v3.md
```

### 场景4：强制覆盖v1
```bash
python ai_poadcast_main/generate_stage3_script.py --date 2025-11-03 --overwrite
# 输出: ✅ 已生成脚本：脚本输出/2025-11-03/episode_2025-11-03_v1.md（覆盖）
```

## 测试验证

运行测试脚本：
```bash
python test_version_increment.py
```

**测试结果**:
```
测试日期: 2025-11-03
输出目录: 脚本输出/2025-11-03/

现有文件 (1个):
  - episode_2025-11-03_v1.md

测试自动递增:
  下一个版本: episode_2025-11-03_v2.md
  完整路径: 脚本输出/2025-11-03/episode_2025-11-03_v2.md

测试覆盖模式:
  覆盖路径: episode_2025-11-03_v1.md

✅ 测试完成！
```

## 工作流集成

### Makefile 更新
移除了警告信息，因为现在可以安全地重复运行：

```makefile
full-pipeline:
	@echo "🚀 启动完整流水线..."
	python ai_poadcast_main/daily_workflow.py
	@$(MAKE) audio
	@$(MAKE) postprocess
	@$(MAKE) publish
```

### daily_workflow.py
无需修改，自动继承新功能。

## 优点

1. ✅ **无需手动管理版本号** - 自动递增
2. ✅ **保留历史版本** - 不会意外覆盖
3. ✅ **支持多次迭代** - 可以生成多个版本对比
4. ✅ **防止数据丢失** - 默认不覆盖
5. ✅ **向后兼容** - 仍支持 `--overwrite` 参数

## 版本管理建议

### 推荐工作流
1. 首次生成 → `v1.md`
2. 修改Prompt后重新生成 → `v2.md`
3. 再次调整后生成 → `v3.md`
4. 确定最终版本后，重命名为 `episode_2025-11-03_final.md`

### 清理旧版本
```bash
# 保留最新版本，删除旧版本
cd 脚本输出/2025-11-03/
ls -t episode_*.md | tail -n +2 | xargs rm

# 或者只保留 final 版本
rm episode_*_v*.md
```

## 注意事项

1. **版本号上限**: 最多支持到 v99，超过会报错
2. **文件命名**: 必须遵循 `episode_YYYY-MM-DD_vN.md` 格式
3. **目录结构**: 自动创建 `脚本输出/YYYY-MM-DD/` 目录
4. **覆盖模式**: 使用 `--overwrite` 时总是覆盖 v1.md

## 相关文件

- `ai_poadcast_main/generate_stage3_script.py` - 主脚本
- `test_version_increment.py` - 测试脚本
- `Makefile` - 工作流集成
- `ai_poadcast_main/daily_workflow.py` - 日常工作流

---

**修复日期**: 2025-11-03  
**测试状态**: ✅ 已通过测试  
**影响范围**: Stage 3 脚本生成流程
