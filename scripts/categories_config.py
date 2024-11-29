"""
计算机视觉论文分类配置文件
按照技术独特性和包含关系最小化的原则排序
"""

CATEGORIES = {
    # 3D相关（最特殊的类别）
    "3DGS": [
        "gaussian splatting",
        "3d gaussian",
        "gaussian splat",
        "gaussian representation",
        "real-time rendering",
        "point-based rendering",
        "differentiable rendering",
        "neural graphics"
    ],
    "NeRF": [
        "neural radiance field",
        "nerf",
        "neural field",
        "view synthesis",
        "novel view",
        "volume rendering",
        "implicit neural representation",
        "neural scene representation",
        "radiance field",
        "continuous scene representation"
    ],
    "3D": [
        "3d reconstruction",
        "point cloud",
        "mesh reconstruction",
        "depth estimation",
        "slam",
        "structure from motion",
        "3d detection",
        "3d tracking",
        "3d pose",
        "multi-view geometry",
        "visual odometry"
    ],
    
    # 生成和创作（与3D关联较少）
    "AIGC/AI创作": [
        "text to image", "text to video", "text-to-3d", "text to speech",
        "image generation", "video generation", "content generation",
        "creative ai", "ai art", "content creation",
        "controllable generation", "multimodal generation", "ai-generated",
        "prompt", "midjourney", "stable diffusion"
    ],
    "生成模型/图像生成": [
        "gan", "generative adversarial", "diffusion", "style transfer", 
        "image synthesis", "text-to-image", "image editing", "inpainting", 
        "super resolution", "dalle"
    ],
    
    # 多模态（与生成相关但不重叠）
    "多模态/跨模态": [
        "multimodal", "vision-language", "text", "caption", "vqa",
        "visual question answering", "image captioning", "cross-modal",
        "language-vision", "text-guided", "clip", "visual grounding"
    ],
    
    # 基础视觉任务（关键词独特）
    "目标检测": [
        "detection", "detector", "yolo", "rcnn", "faster rcnn", "mask rcnn", 
        "ssd", "object detection", "pedestrian detection", "face detection"
    ],
    "图像分割": [
        "segmentation", "segment", "semantic segmentation", "instance segmentation",
        "panoptic", "mask", "boundary", "region", "pixel-wise"
    ],
    "目标识别/分类": [
        "recognition", "classification", "classifier", "identification",
        "resnet", "vit", "convnet", "cnn"
    ],
    
    # 视频和动作（时序相关）
    "视频理解": [
        "video", "temporal", "motion", "tracking", "action recognition",
        "activity recognition", "object tracking", "trajectory", "optical flow",
        "video segmentation", "video generation"
    ],
    
    # 图像处理（独立任务）
    "图像增强/恢复": [
        "enhancement", "restoration", "denoising", "deblurring", "dehaze",
        "super-resolution", "hdr", "low-light", "color", "quality",
        "image quality", "artifact"
    ],
    
    # 人物相关（特定领域）
    "人脸/人体分析": [
        "face", "facial", "pose", "human", "body", "gesture",
        "emotion", "expression", "gait", "skeleton", "keypoint",
        "human parsing", "person re-identification", "reid"
    ],
    "数字人/虚拟人": [
        "digital human", "virtual human", "avatar", "talking head",
        "face animation", "facial animation", "face reenactment", "face synthesis",
        "motion retargeting", "character animation", "virtual character",
        "digital clone", "metahuman", "face swap", "deepfake"
    ],
    
    # 学习方法（通用技术）
    "自监督/无监督学习": [
        "self-supervised", "unsupervised", "contrastive", "pretraining",
        "representation learning", "semi-supervised", "few-shot", "zero-shot",
        "transfer learning", "domain adaptation"
    ],
    
    # 网络架构（基础组件）
    "图神经网络": [
        "graph neural", "gnn", "graph convolutional", "gcn", "graph attention",
        "message passing", "graph representation"
    ],
    "注意力机制": [
        "attention", "transformer", "self-attention", "multi-head",
        "vision transformer", "swin", "focal"
    ],
    
    # 工程实践（独立任务）
    "模型优化/部署": [
        "optimization", "pruning", "quantization", "lightweight", "efficient",
        "compress", "acceleration", "distillation", "knowledge distillation",
        "nas", "neural architecture search", "mobile", "edge", "real-time"
    ],
    "异常检测": [
        "anomaly", "outlier", "defect", "novelty", "out-of-distribution",
        "change detection", "fault detection", "industrial inspection"
    ],
    
    # 其他
    "其他": []
}

CATEGORY_PROMPT = '''
你是一个专业的计算机视觉论文分类助手。请根据论文的标题和摘要，将论文分类到以下类别之一：

- 3DGS：3D高斯散射相关，包括高斯散射渲染、实时神经渲染等
- NeRF：神经辐射场相关，包括NeRF及其变体、视图合成、神经场景表示等
- 3D：传统3D视觉，包括重建、点云处理、深度估计、SLAM等
- AIGC/AI创作：AI生成内容，包括文本到图像、视频生成等
- 生成模型/图像生成：各类生成模型和图像生成技术
- 多模态/跨模态：视觉-语言交互、多模态学习等
- 目标检测：物体检测相关任务
- 图像分割：语义分割、实例分割等
- 目标识别/分类：图像分类和识别任务
- 视频理解：视频分析、动作识别等
- 图像增强/恢复：图像质量提升、去噪等
- 人脸/人体分析：人脸识别、姿态估计等
- 数字人/虚拟人：数字人生成和动画
- 自监督/无监督学习：自监督和无监督学习方法
- 图神经网络：基于图的深度学习
- 注意力机制：注意力和Transformer相关
- 模型优化/部署：模型压缩、加速等
- 异常检测：异常和缺陷检测

分类规则：
1. 优先考虑3D相关类别（3DGS > NeRF > 3D）
2. 其次考虑生成和多模态类别
3. 如果不属于任何类别，返回"其他"
4. 选择最符合论文核心技术的类别

论文标题：{title}
论文摘要：{abstract}

分类结果：'''
