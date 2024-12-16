"""ChatGLM助手：用于论文标题翻译和分类"""
from zhipuai import ZhipuAI
import os
import json
from typing import Tuple, List
import time
import re
from collections import defaultdict
import categories_config

class ChatGLMHelper:
    def __init__(self):
        """初始化ChatGLM客户端"""
        api_key = '1e8f0dd1b174e7b06bb3bce603856f62.qY4xvp6L8wEOJlRN'
        if not api_key:
            raise ValueError("请设置环境变量 ZHIPUAI_API_KEY")
        self.client = ZhipuAI(api_key=api_key)

    def translate_title(self, title: str, abstract: str) -> str:
        """
        使用ChatGLM翻译论文标题
        Args:
            title: 论文英文标题
            abstract: 论文摘要，用于提供上下文
        Returns:
            str: 中文标题
        """
        max_retries = 3
        retry_delay = 2  # 重试延迟秒数

        prompt = f"""请将以下计算机视觉领域学术论文的标题翻译成中文。
请注意：
1. 保持专业术语的准确性
2. 保留原文中的缩写和专有名词
3. 翻译要简洁明了
4. 只需要返回翻译结果，不要有任何解释或额外内容

论文标题：{title}

中文标题："""

        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="glm-4-flash",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=200,
                    top_p=0.7,
                )
                translation = response.choices[0].message.content.strip()
                # 确保返回的是中文
                if any('\u4e00' <= char <= '\u9fff' for char in translation):
                    return translation
                else:
                    print(f"警告：第{attempt + 1}次翻译未返回中文结果，重试中...")
            except Exception as e:
                print(f"翻译出错 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                continue
        
        return f"[翻译失败] {title}"

    def clean_json_string(self, text: str) -> str:
        """清理并提取JSON字符串"""
        # 移除可能的markdown代码块标记
        if '```' in text:
            # 提取代码块内容
            pattern = r'```(?:json)?(.*?)```'
            matches = re.findall(pattern, text, re.DOTALL)
            if matches:
                text = matches[0]
        
        # 移除所有空行和前后空白
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = ''.join(lines)
        
        # 尝试找到JSON对象的开始和结束
        start = text.find('{')
        end = text.rfind('}')
        
        if start != -1 and end != -1:
            text = text[start:end+1]
        
        # 替换单引号为双引号
        text = text.replace("'", '"')
        
        return text

    def get_category_by_keywords(self, title: str, abstract: str) -> Tuple[str, float]:
        """通过关键词匹配进行分类
        
        Args:
            title: 论文标题
            abstract: 论文摘要
            
        Returns:
            Tuple[str, float]: (类别名称, 置信度)
        """
        # 将标题和摘要转换为小写
        title_lower = title.lower()
        abstract_lower = abstract.lower()
        
        # 记录每个类别的匹配分数
        category_scores = defaultdict(float)
        
        # 遍历所有类别和关键词
        for category, keywords in categories_config.CATEGORY_KEYWORDS.items():
            score = 0.0
            matched_keywords = set()  # 避免重复计算
            
            for keyword in keywords:
                keyword_lower = keyword.lower()
                if keyword not in matched_keywords:
                    # 标题完全匹配权重最高
                    if keyword_lower in title_lower:
                        score += 5.0
                        matched_keywords.add(keyword)
                    # 标题部分匹配权重次之
                    elif any(kw in title_lower for kw in keyword_lower.split()):
                        score += 3.0
                        matched_keywords.add(keyword)
                    # 摘要开头匹配
                    elif keyword_lower in abstract_lower[:200]:
                        score += 2.0
                        matched_keywords.add(keyword)
                    # 摘要其他位置匹配
                    elif keyword_lower in abstract_lower:
                        score += 1.0
                        matched_keywords.add(keyword)
            
            if score > 0:
                # 根据匹配的关键词数量和位置调整分数
                if len(matched_keywords) >= 2:
                    score *= 1.3  # 多个关键词匹配时提升分数
                elif len(matched_keywords) >= 3:
                    score *= 1.5  # 更多关键词匹配时进一步提升
                
                # 如果标题中包含类别名称，额外加分
                if category.lower() in title_lower:
                    score *= 1.2
                
                category_scores[category] = score
        
        # 找出得分最高的类别
        if category_scores:
            # 获取前两个得分最高的类别
            sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
            best_category = sorted_categories[0]
            
            # 如果最高分显著高于第二高分，增加置信度
            if len(sorted_categories) > 1:
                second_best = sorted_categories[1]
                if best_category[1] >= second_best[1] * 1.5:  # 最高分至少比第二高分高50%
                    return best_category
                
            # 否则使用原始阈值
            if best_category[1] >= 2.0:
                return best_category
        
        return "其他", 0.0

    def classify_paper(self, title: str, abstract: str) -> str:
        """对论文进行分类
        
        Args:
            title: 论文标题
            abstract: 论文摘要
            
        Returns:
            str: 论文类别
        """
        try:
            # 先尝试使用关键词匹配
            keyword_category, confidence = self.get_category_by_keywords(title, abstract)
            if keyword_category != "其他" and confidence >= 2.0:
                return keyword_category
            
            # 构建分类提示词，强调分类准确性
            prompt = f"{categories_config.CATEGORY_PROMPT}\n\n论文标题：{title}\n摘要：{abstract}\n\n注意：\n1. 请仔细分析论文的核心技术和主要贡献\n2. 选择最能体现论文主要工作的类别\n3. 如果论文跨多个领域，选择最核心的一个\n4. 只有在完全无法确定时才返回'其他'"
            
            # 调用 ChatGLM 进行分类
            response = self.client.chat.completions.create(
                model="glm-4-flash",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=50,
                top_p=0.7,
            )
            
            # 获取分类结果
            category = response.choices[0].message.content.strip()
            
            # 验证返回的类别是否在预定义类别中
            if category in categories_config.ALL_CATEGORIES:
                # 如果ChatGLM返回的类别与关键词匹配的类别不同，且都不是"其他"
                if keyword_category != "其他" and category != keyword_category:
                    # 进行第二次确认
                    confirm_prompt = f"{prompt}\n\n系统发现这篇论文可能属于'{keyword_category}'类别，请再次确认最合适的分类。"
                    response = self.client.chat.completions.create(
                        model="glm-4-flash",
                        messages=[{"role": "user", "content": confirm_prompt}],
                        temperature=0.1,
                        max_tokens=50,
                        top_p=0.7,
                    )
                    final_category = response.choices[0].message.content.strip()
                    if final_category in categories_config.ALL_CATEGORIES:
                        return final_category
                
                return category
            
            # 如果返回的类别不在预定义类别中，使用关键词匹配的结果
            if keyword_category != "其他":
                return keyword_category
            
            return "其他"
                
        except Exception as e:
            print(f"ChatGLM 分类出错: {str(e)}")
            # 发生错误时，如果关键词匹配有结果就返回
            if keyword_category != "其他":
                return keyword_category
            return "其他"

    def categorize_paper(self, title: str, abstract: str) -> str:
        """使用ChatGLM对论文进行分类
        
        Args:
            title: 论文标题
            abstract: 论文摘要
        
        Returns:
            str: 论文类别
        """
        # 构建提示词
        prompt = f"{categories_config.CATEGORY_PROMPT}\n\n论文标题：{title}\n摘要：{abstract}\n\n注意：请尽量根据论文解决的核心问题确定一个具体类别。只有在完全无法确定时才返回'其他'。"
        
        # 尝试最多3次分类
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                # 获取ChatGLM的分类结果
                response = self.client.chat.completions.create(
                    model="glm-4-flash",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=200,
                    top_p=0.7,
                )
                category = response.choices[0].message.content.strip()
                
                # 验证返回的类别是否有效
                if category in categories_config.ALL_CATEGORIES:
                    return category
                
                # 如果ChatGLM返回无效类别，尝试使用关键词匹配
                keyword_category, confidence = self.get_category_by_keywords(title, abstract)
                if keyword_category != "其他":
                    return keyword_category
                
            except Exception as e:
                if attempt == max_attempts - 1:
                    print(f"Error in categorization after {max_attempts} attempts: {e}")
                    # 最后尝试使用关键词匹配
                    keyword_category, confidence = self.get_category_by_keywords(title, abstract)
                    if keyword_category != "其他":
                        return keyword_category
                continue
        
        return "其他"

    def analyze_paper_contribution(self, title: str, abstract: str) -> dict:
        """分析论文的核心贡献和解决的问题
    
        Args:
            title: 论文标题
            abstract: 论文摘要
    
        Returns:
            dict: 包含分析结果的字典
        """
        prompt = f"""请分析以下计算机视觉论文的核心贡献。
    
论文标题：{title}
论文摘要：{abstract}

请用中文简要总结：
1. 这篇论文解决了什么问题
2. 提出了什么方法或创新点
3. 取得了什么效果

请用简洁的语言描述，避免技术细节。
"""
        try:
            response = self.client.chat.completions.create(
                model="glm-4-flash",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500,
                top_p=0.7,
            )
            
            analysis = response.choices[0].message.content.strip()
            return {
                "核心贡献": analysis
            }
            
        except Exception as e:
            print(f"分析论文贡献时出错: {str(e)}")
            return {
                "核心贡献": "分析失败"
            }

    def translate_title(self, title: str) -> str:
        """将论文标题翻译为中文
    
        Args:
            title: 英文标题
    
        Returns:
            str: 中文标题
        """
        prompt = f"""请将以下计算机视觉论文的标题翻译成中文，保持专业性和准确性：

{title}

只返回翻译结果，不需要解释。"""

        try:
            response = self.client.chat.completions.create(
                model="glm-4-flash",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=200,
                top_p=0.7,
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"翻译标题时出错: {str(e)}")
            return title  # 如果翻译失败，返回原标题
