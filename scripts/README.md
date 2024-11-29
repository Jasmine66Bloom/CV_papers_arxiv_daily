# ArXiv CV Papers Daily Update

An automated system for fetching, analyzing, and organizing the latest computer vision research papers from ArXiv with AI-powered classification capabilities.

## Features

- **Automated Paper Retrieval**: Automatically fetches the latest CV papers from ArXiv
- **AI-Powered Analysis**: Uses ChatGLM for intelligent paper categorization and analysis
- **Bilingual Support**: Provides paper titles in both English and Chinese
- **Code Link Detection**: Automatically extracts GitHub repository links
- **Organized Output**: Generates well-structured Markdown reports
- **Parallel Processing**: Utilizes multi-threading for improved efficiency
- **Smart Categorization**: Classifies papers into specific research areas

## Project Structure

```
CascadeProjects/
├── scripts/           # Script files
│   ├── get_cv_papers.py     # Main program
│   ├── chatglm_helper.py    # ChatGLM API helper
│   └── requirements.txt     # Dependencies
├── data/              # Table-format paper information
│   └── YYYY-MM/
│       └── YYYY-MM-DD.md
└── local/             # Detailed paper information
    └── YYYY-MM/
        └── YYYY-MM-DD.md
```

## Requirements

- Python 3.x
- Dependencies listed in `requirements.txt`
- ChatGLM API key
- Stable internet connection

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Configure ChatGLM API key

## Configuration

Key parameters in `get_cv_papers.py`:
- `QUERY_DAYS_AGO`: Days to look back (0=today, 1=yesterday)
- `MAX_RESULTS`: Maximum number of papers to retrieve
- `MAX_WORKERS`: Maximum parallel processing threads

## Usage

Run the main script:
```bash
python get_cv_papers.py
```

### Output Files

The script generates two types of Markdown files:

1. Table Format (`data/YYYY-MM/YYYY-MM-DD.md`):
   - Basic paper information
   - Categorized by research areas
   - Concise tabular format

2. Detailed Format (`local/YYYY-MM/YYYY-MM-DD.md`):
   - Comprehensive paper details
   - AI-generated analysis
   - Core contributions
   - Code links

## Research Categories

Current supported research areas:
1. 3DGS (3D Gaussian Splatting)
2. NeRF (Neural Radiance Fields)
3. 3D Vision and Reconstruction
4. Image Generation and Editing
5. Multimodal Learning
6. Object Detection and Segmentation
7. Video Understanding and Processing
8. Human Pose and Action
9. Others

## Automated Deployment

Set up daily automatic runs using crontab:
```bash
# Edit crontab
crontab -e

# Add this line to run at 9 AM daily
0 9 * * * cd /path/to/CascadeProjects/scripts && python get_cv_papers.py
```

## Error Handling

The script includes:
- ArXiv API rate limit handling
- Network error recovery
- Parallel processing error handling
- File system error handling

## Security Notes

- Store API keys securely
- Monitor API usage
- Keep dependencies updated
- Use virtual environments

## Future Improvements

- Enhanced error recovery
- More research categories
- Better code link detection
- Interactive web interface
- Multi-language support
- Advanced paper filtering

---

# ArXiv CV 论文每日更新

这是一个自动获取、分析和整理 ArXiv 计算机视觉（CV）领域最新论文的系统，具有 AI 驱动的分类功能。

## 功能特点

- **自动论文获取**：自动从 ArXiv 获取最新 CV 论文
- **AI 驱动分析**：使用 ChatGLM 进行智能论文分类和分析
- **双语支持**：提供中英文论文标题
- **代码链接检测**：自动提取 GitHub 仓库链接
- **结构化输出**：生成结构良好的 Markdown 报告
- **并行处理**：使用多线程提高效率
- **智能分类**：将论文分类到特定研究领域

## 项目结构

```
CascadeProjects/
├── scripts/           # 脚本文件
│   ├── get_cv_papers.py     # 主程序
│   ├── chatglm_helper.py    # ChatGLM API 助手
│   └── requirements.txt     # 依赖项
├── data/              # 表格格式论文信息
│   └── YYYY-MM/
│       └── YYYY-MM-DD.md
└── local/             # 详细格式论文信息
    └── YYYY-MM/
        └── YYYY-MM-DD.md
```

## 系统要求

- Python 3.x
- requirements.txt 中列出的依赖项
- ChatGLM API 密钥
- 稳定的网络连接

## 安装方法

1. 克隆仓库
2. 安装依赖：
```bash
pip install -r requirements.txt
```
3. 配置 ChatGLM API 密钥

## 配置说明

主要参数（在 get_cv_papers.py 中）：
- `QUERY_DAYS_AGO`：查询几天前的论文（0=今天，1=昨天）
- `MAX_RESULTS`：最大返回论文数量
- `MAX_WORKERS`：并行处理的最大线程数

## 使用方法

运行主脚本：
```bash
python get_cv_papers.py
```

### 输出文件

脚本生成两种格式的 Markdown 文件：

1. 表格格式（data/YYYY-MM/YYYY-MM-DD.md）：
   - 基本论文信息
   - 按研究方向分类
   - 简洁的表格形式

2. 详细格式（local/YYYY-MM/YYYY-MM-DD.md）：
   - 完整论文详情
   - AI 生成的分析
   - 核心贡献
   - 代码链接

## 研究类别

当前支持的研究方向：
1. 3DGS (3D 高斯散射)
2. NeRF (神经辐射场)
3. 3D 视觉与重建
4. 图像生成与编辑
5. 多模态学习
6. 目标检测与分割
7. 视频理解与处理
8. 人体姿态与动作
9. 其他

## 自动化部署

使用 crontab 设置每日自动运行：
```bash
# 编辑 crontab
crontab -e

# 添加以下行（每天早上9点运行）
0 9 * * * cd /path/to/CascadeProjects/scripts && python get_cv_papers.py
```

## 错误处理

脚本包含以下错误处理机制：
- ArXiv API 速率限制处理
- 网络错误恢复
- 并行处理错误处理
- 文件系统错误处理

## 安全注意事项

- 安全存储 API 密钥
- 监控 API 使用情况
- 保持依赖项更新
- 使用虚拟环境

## 未来改进

- 增强错误恢复能力
- 增加研究类别
- 改进代码链接检测
- 交互式网页界面
- 多语言支持
- 高级论文筛选
