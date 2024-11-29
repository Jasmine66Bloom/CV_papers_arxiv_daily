"""ChatGLM助手：用于论文标题翻译和分类"""
from zhipuai import ZhipuAI
import os
import json
from typing import Tuple, List
import time
import re

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
        """通过关键词匹配进行分类"""
        # 将标题和摘要转换为小写以进行不区分大小写的匹配
        text = (title + " " + abstract).lower()
        
        # 定义每个类别的关键词
        keywords = {
            "3DGS": [
                "gaussian splat", "3d gaussian", "gaussian splatting", 
                "3d scene", "point cloud", "neural point"
            ],
            "NeRF": [
                "nerf", "neural radiance field", "neural radiation field",
                "radiance field", "novel view", "view synthesis"
            ],
            "3D视觉与重建": [
                "3d reconstruction", "point cloud", "depth estimation",
                "3d detection", "3d object", "3d scene", "mesh", "voxel"
            ],
            "图像生成与编辑": [
                "gan", "diffusion", "generative", "synthesis", "style transfer",
                "image editing", "text-to-image", "image generation"
            ],
            "多模态学习": [
                "multimodal", "multi-modal", "vision-language", "text-image",
                "cross-modal", "visual-language", "vlm", "llm"
            ],
            "目标检测与分割": [
                "detection", "segmentation", "object detection", 
                "semantic segmentation", "instance segmentation"
            ],
            "视频理解与处理": [
                "video", "temporal", "motion", "frame", "clip", 
                "video understanding", "action recognition"
            ],
            "人体姿态与动作": [
                "pose", "human pose", "body", "skeleton", "action",
                "motion capture", "human motion", "gesture"
            ]
        }
        
        # 计算每个类别的匹配分数
        category_scores = {}
        for category, words in keywords.items():
            score = sum(1 for word in words if word in text)
            if score > 0:
                confidence = min(0.9, 0.5 + score * 0.1)  # 最高置信度为0.9
                category_scores[category] = (score, confidence)
        
        # 如果找到匹配的类别，返回得分最高的
        if category_scores:
            best_category = max(category_scores.items(), key=lambda x: x[1][0])
            return best_category[0], best_category[1][1]
        
        return None, 0.0

    def categorize_paper(self, title, abstract):
        """使用ChatGLM对论文进行分类
        
        Args:
            title: 论文标题
            abstract: 论文摘要
        
        Returns:
            str: 论文类别
        """
        # 构建 prompt
        prompt = f"""你是一个专业的计算机视觉论文分类助手。请分析以下论文的标题和摘要，
将其分类到最合适的类别中。只返回类别名称，不需要解释。

可选类别：
- 3DGS（3D Gaussian Splatting相关）
- NeRF（神经辐射场相关）
- 3D视觉与重建（3D视觉、重建、点云等）
- 图像生成与编辑（图像生成、编辑、风格迁移等）
- 多模态学习（多模态、跨模态学习等）
- 目标检测与分割（目标检测、分割、追踪等）
- 视频理解与处理（视频分析、理解、生成等）
- 人体姿态与动作（人体姿态估计、动作识别等）
- 其他（其他CV相关研究）

论文标题：{title}
论文摘要：{abstract}

请根据论文的核心贡献和主要方法进行分类。如果一篇论文涉及多个类别，请选择最主要的一个。
只返回类别名称，例如"3DGS"或"NeRF"等。"""

        try:
            # 调用ChatGLM API
            response = self.client.chat.completions.create(
                model="glm-4-flash",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # 使用较低的温度以获得更确定的答案
                max_tokens=200,
                top_p=0.7,
            )
            
            # 获取分类结果
            category = response.choices[0].message.content.strip()
            
            # 确保返回的类别是有效的
            valid_categories = [
                "3DGS", "NeRF", "3D视觉与重建", "图像生成与编辑", 
                "多模态学习", "目标检测与分割", "视频理解与处理", 
                "人体姿态与动作", "其他"
            ]
            
            # 如果返回的类别不在列表中，尝试模糊匹配最相似的类别
            if category not in valid_categories:
                # 对于一些常见的变体进行标准化
                category_mapping = {
                    "3D高斯": "3DGS",
                    "高斯散射": "3DGS",
                    "神经辐射场": "NeRF",
                    "NeRF相关": "NeRF",
                    "三维视觉": "3D视觉与重建",
                    "3D重建": "3D视觉与重建",
                    "图像生成": "图像生成与编辑",
                    "图像编辑": "图像生成与编辑",
                    "多模态": "多模态学习",
                    "目标检测": "目标检测与分割",
                    "实例分割": "目标检测与分割",
                    "视频处理": "视频理解与处理",
                    "视频分析": "视频理解与处理",
                    "人体姿态": "人体姿态与动作",
                    "动作识别": "人体姿态与动作"
                }
                
                # 尝试从映射中获取标准类别
                category = category_mapping.get(category, "其他")
            
            return category
            
        except Exception as e:
            print(f"分类过程出错: {str(e)}")
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
