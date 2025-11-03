"""Prompt构建器"""

from datetime import date
from typing import List


class PromptBuilder:
    """Stage 3 Prompt构建器"""
    
    def build(self, summaries: List[dict], episode_date: date) -> str:
        """构建播客脚本生成Prompt"""
        # 从prepare_stage3_prompt.py迁移逻辑
        pass
