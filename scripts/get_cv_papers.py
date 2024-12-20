import arxiv
from datetime import datetime, timedelta
from collections import defaultdict
import re
from chatglm_helper import ChatGLMHelper
import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any
import time

# 查询参数设置
QUERY_DAYS_AGO = 1          # 查询几天前的论文，0=今天，1=昨天，2=前天
MAX_RESULTS = 300           # 最大返回论文数量
MAX_WORKERS = 5            # 并行处理的最大线程数

def extract_github_link(text, paper_url=None):
    """从文本中提取GitHub链接，如果没有找到则尝试从Papers With Code获取
    
    Args:
        text: 要搜索的文本
        paper_url: 论文的ArXiv URL（用于Papers With Code API）
    
    Returns:
        str: GitHub链接或None
    """
    # GitHub链接模式
    github_patterns = [
        r'https?://github\.com/[a-zA-Z0-9-]+/[a-zA-Z0-9-_.]+',
        r'github\.com/[a-zA-Z0-9-]+/[a-zA-Z0-9-_.]+',
    ]
    
    # 首先尝试从文本中提取
    for pattern in github_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            url = match.group(0)
            if not url.startswith('http'):
                url = 'https://' + url
            return url
    
    # 如果没有找到，并且提供了论文URL，尝试从Papers With Code获取
    if paper_url:
        arxiv_id = extract_arxiv_id(paper_url)
        if arxiv_id:
            code_link = get_arxiv_code_link(arxiv_id)
            if code_link:
                return code_link
    
    return 'None'

def get_arxiv_code_link(paper_id):
    """从 Papers With Code API 获取论文代码链接
    
    Args:
        paper_id: ArXiv ID (e.g., "2311.12296" from "http://arxiv.org/abs/2311.12296")
    
    Returns:
        str: GitHub链接，如果没有找到则返回None
    """
    try:
        # 构建API URL
        api_url = f"https://arxiv.paperswithcode.com/api/v0/papers/{paper_id}"
        
        # 发送请求
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # 检查是否有代码链接
            if data.get("repository_urls"):
                # 优先选择GitHub链接
                for url in data["repository_urls"]:
                    if "github.com" in url.lower():
                        return url
                # 如果没有GitHub链接，返回第一个代码链接
                return data["repository_urls"][0]
                
        return None
        
    except Exception as e:
        print(f"获取Papers With Code链接时出错: {str(e)}")
        return None

def extract_arxiv_id(url):
    """从ArXiv URL中提取论文ID
    
    Args:
        url: ArXiv论文URL
    
    Returns:
        str: 论文ID
    """
    # 处理不同格式的ArXiv URL
    patterns = [
        r"arxiv\.org/abs/(\d+\.\d+)",
        r"arxiv\.org/pdf/(\d+\.\d+)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def df_to_markdown_table(papers_by_category: dict, target_date) -> str:
    """生成表格形式的Markdown内容"""
    markdown = ""
    
    # 过滤掉没有论文的类别
    active_categories = {k: v for k, v in papers_by_category.items() if v}
    
    if not active_categories:
        return "今天没有相关论文。"
    
    # 表格列标题
    headers = ['发布日期', '英文标题', '中文标题', '作者', 'PDF链接', '代码链接']
    
    # 为每个有论文的类别创建表格
    for category, papers in sorted(((k, v) for k, v in active_categories.items() if k != "其他")):
        # 添加类别标题
        markdown += f"\n## {category}\n\n"
        
        # 创建表格头
        markdown += "|" + "|".join(headers) + "|\n"
        markdown += "|" + "|".join(["---"] * len(headers)) + "|\n"
        
        # 添加论文
        for paper in papers:
            # 使用目标日期作为发布日期
            pub_date = target_date.strftime('%Y-%m-%d')
            
            # 准备每个字段的值
            values = [
                pub_date,
                paper['title'],
                paper['title_cn'],
                paper['authors'],  # 已经是格式化好的字符串
                f"<{paper['pdf_url']}>",
                f"<{paper['github_link']}>" if paper['github_link'] != 'None' else 'None'
            ]
            
            # 处理特殊字符
            values = [str(v).replace('\n', ' ').replace('|', '&#124;') for v in values]
            
            # 添加到表格
            markdown += "|" + "|".join(values) + "|\n"
        
        # 在每个表格后添加空行
        markdown += "\n"
    
    # 处理"其他"类别
    if "其他" in active_categories:
        # 添加类别标题
        markdown += f"\n## 其他\n\n"
        
        # 创建表格头
        markdown += "|" + "|".join(headers) + "|\n"
        markdown += "|" + "|".join(["---"] * len(headers)) + "|\n"
        
        # 添加论文
        for paper in active_categories["其他"]:
            # 使用目标日期作为发布日期
            pub_date = target_date.strftime('%Y-%m-%d')
            
            # 准备每个字段的值
            values = [
                pub_date,
                paper['title'],
                paper['title_cn'],
                paper['authors'],  # 已经是格式化好的字符串
                f"<{paper['pdf_url']}>",
                f"<{paper['github_link']}>" if paper['github_link'] != 'None' else 'None'
            ]
            
            # 处理特殊字符
            values = [str(v).replace('\n', ' ').replace('|', '&#124;') for v in values]
            
            # 添加到表格
            markdown += "|" + "|".join(values) + "|\n"
        
        # 在每个表格后添加空行
        markdown += "\n"
    
    return markdown

def df_to_markdown_detailed(papers_by_category: dict, target_date) -> str:
    """生成详细格式的Markdown内容"""
    markdown = ""
    
    # 过滤掉没有论文的类别
    active_categories = {k: v for k, v in papers_by_category.items() if v}
    
    if not active_categories:
        return "今天没有相关论文。"
    
    # 为每个有论文的类别创建详细内容
    for category, papers in sorted(((k, v) for k, v in active_categories.items() if k != "其他")):
        # 添加类别标题
        markdown += f"## **{category}**\n"
        markdown += "\n"
        
        # 添加论文
        for idx, paper in enumerate(papers, 1):
            markdown += f'**index:** {idx}<br />\n'
            markdown += f'**Date:** {target_date.strftime("%Y-%m-%d")}<br />\n'
            markdown += f'**Title:** {paper["title"]}<br />\n'
            markdown += f'**Title_cn:** {paper["title_cn"]}<br />\n'
            markdown += f'**Authors:** {paper["authors"]}<br />\n'  # 已经是格式化好的字符串
            markdown += f'**PDF:** <{paper["pdf_url"]}><br />\n'
            
            if paper["github_link"] != 'None':
                markdown += f'**Code:** <{paper["github_link"]}><br />\n'
            else:
                markdown += '**Code:** None<br />\n'
            
            if "核心贡献" in paper:
                markdown += f'**Core Contribution:** {paper["核心贡献"]}<br />\n'
            if "核心问题" in paper:
                markdown += f'**Core Problem:** {paper["核心问题"]}<br />\n'
            
            markdown += "\n"
        
        markdown += "\n"
    
    # 处理"其他"类别
    if "其他" in active_categories:
        markdown += f"## **其他**\n"
        markdown += "\n"
        
        for idx, paper in enumerate(active_categories["其他"], 1):
            markdown += f'**index:** {idx}<br />\n'
            markdown += f'**Date:** {target_date.strftime("%Y-%m-%d")}<br />\n'
            markdown += f'**Title:** {paper["title"]}<br />\n'
            markdown += f'**Title_cn:** {paper["title_cn"]}<br />\n'
            markdown += f'**Authors:** {paper["authors"]}<br />\n'  # 已经是格式化好的字符串
            markdown += f'**PDF:** <{paper["pdf_url"]}><br />\n'
            
            if paper["github_link"] != 'None':
                markdown += f'**Code:** <{paper["github_link"]}><br />\n'
            else:
                markdown += '**Code:** None<br />\n'
            
            if "核心贡献" in paper:
                markdown += f'**Core Contribution:** {paper["核心贡献"]}<br />\n'
            if "核心问题" in paper:
                markdown += f'**Core Problem:** {paper["核心问题"]}<br />\n'
            
            markdown += "\n"
    
    return markdown

def save_papers_to_markdown(papers_by_category: dict, target_date):
    """保存论文信息到Markdown文件"""
    # 使用目标日期作为文件名
    filename = target_date.strftime("%Y-%m-%d") + ".md"
    year_month = target_date.strftime("%Y-%m")
    
    # 获取当前文件所在目录(scripts)的父级路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    
    # 设置基础目录，与scripts同级
    data_base = os.path.join(parent_dir, 'data')
    local_base = os.path.join(parent_dir, 'local')
    
    # 创建年月子目录
    data_year_month = os.path.join(data_base, year_month)
    local_year_month = os.path.join(local_base, year_month)
    
    # 创建所需的目录结构
    os.makedirs(data_year_month, exist_ok=True)
    os.makedirs(local_year_month, exist_ok=True)
    
    # 生成完整的文件路径
    table_filepath = os.path.join(data_year_month, filename)
    detailed_filepath = os.path.join(local_year_month, filename)
    
    # 生成标题
    title = f"## [UPDATED!] **{target_date.strftime('%Y-%m-%d')}** (Update Time)\n\n"
    
    # 保存表格格式的markdown文件到data/年-月目录
    with open(table_filepath, 'w', encoding='utf-8') as f:
        f.write(title)
        f.write(df_to_markdown_table(papers_by_category, target_date))
    
    # 保存详细格式的markdown文件到local/年-月目录
    with open(detailed_filepath, 'w', encoding='utf-8') as f:
        f.write(title)
        f.write(df_to_markdown_detailed(papers_by_category, target_date))
    
    print(f"\n表格格式文件已保存到: {table_filepath}")
    print(f"详细格式文件已保存到: {detailed_filepath}")

def process_paper(paper, glm_helper, target_date) -> Dict[str, Any]:
    """处理单篇论文的所有分析任务
    
    Args:
        paper: ArXiv论文对象
        glm_helper: ChatGLM助手实例
        target_date: 目标日期
    
    Returns:
        Dict: 包含论文信息的字典，如果论文不符合日期要求则返回None
    """
    # 检查发布日期和更新日期
    paper_published_date = paper.published.date()
    paper_updated_date = paper.updated.date()
    if paper_published_date != target_date and paper_updated_date != target_date:
        return None
        
    # 提取基本信息
    title = paper.title
    author_list = list(paper.authors)
    authors = ', '.join(author.name for author in (author_list[:8] if len(author_list) > 8 else author_list))
    abstract = paper.summary
    paper_url = paper.entry_id
    pdf_url = paper.pdf_url if hasattr(paper, 'pdf_url') else None
    
    # 并行执行耗时任务
    with ThreadPoolExecutor(max_workers=3) as executor:
        # 提交所有任务
        github_future = executor.submit(extract_github_link, abstract, paper_url)
        analysis_future = executor.submit(glm_helper.analyze_paper_contribution, title, abstract)
        category_future = executor.submit(glm_helper.categorize_paper, title, abstract)
        
        # 获取结果
        github_link = github_future.result()
        analysis_result = analysis_future.result()
        category = category_future.result()
    
    return {
        'title': title,
        'title_cn': glm_helper.translate_title(title),
        'authors': authors,
        'abstract': abstract,
        'paper_url': paper_url,
        'pdf_url': pdf_url,
        'github_link': github_link,
        'analysis_result': analysis_result,
        'category': category
    }

def get_cv_papers():
    """获取CV领域论文并保存为Markdown"""
    start_time = time.time()
    
    # 初始化ChatGLM助手
    glm_helper = ChatGLMHelper()
    
    # 计算目标日期（仅用于显示）
    target_date = datetime.now() - timedelta(days=QUERY_DAYS_AGO)
    target_date = target_date.date()
    
    # 构建查询条件
    query = 'cat:cs.CV'  # 只保留分类条件
    
    print(f"\n=== 查询配置 ===")
    print(f"目标日期: {target_date.strftime('%Y-%m-%d')} ({QUERY_DAYS_AGO} 天前)")
    print(f"最大结果数: {MAX_RESULTS}")
    print(f"最大并行线程数: {MAX_WORKERS}")
    print(f"查询条件: {query}")
    
    # 获取论文列表
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=MAX_RESULTS,
        sort_by=arxiv.SortCriterion.LastUpdatedDate,
        sort_order=arxiv.SortOrder.Descending
    )
    
    # 初始化类别字典
    papers_by_category = defaultdict(list)
    total_papers = 0
    
    print("\n开始处理论文...")
    
    try:
        # 获取所有结果并转换为列表
        results = list(client.results(search))
        
        if not results:
            print("\n未找到CV论文。")
            print("可能的原因：")
            print("1. ArXiv API 暂时不可用")
            print("2. 网络连接问题")
            print("\n建议：")
            print("- 检查网络连接")
            print("- 稍后重试")
            return
        
        print(f"\n找到 {len(results)} 篇论文，开始并行处理...")
        
        # 使用线程池并行处理论文
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # 提交所有论文处理任务
            future_to_paper = {
                executor.submit(process_paper, paper, glm_helper, target_date): paper 
                for paper in results
            }
            
            # 收集处理结果
            for future in as_completed(future_to_paper):
                paper_info = future.result()
                if paper_info:  # 如果论文符合日期要求
                    total_papers += 1
                    category = paper_info['category']
                    papers_by_category[category].append(paper_info)
                    print(f"已处理: {total_papers} 篇 (分类: {category})")
        
        process_time = time.time() - start_time
        print(f"\n论文处理完成，共找到 {total_papers} 篇符合日期的论文")
        print(f"总处理时间: {process_time:.2f} 秒")
        print(f"平均每篇论文处理时间: {process_time/total_papers:.2f} 秒" if total_papers > 0 else "")
        
        if total_papers > 0:
            # 保存markdown文件
            save_papers_to_markdown(papers_by_category, target_date)
        else:
            print(f"\n未找到 {target_date.strftime('%Y-%m-%d')} 的CV论文。")
        
    except Exception as e:
        print(f"\n处理论文时出错: {str(e)}")
        print("请检查网络连接并稍后重试")
        return

if __name__ == "__main__":
    # 直接运行查询
    get_cv_papers()
