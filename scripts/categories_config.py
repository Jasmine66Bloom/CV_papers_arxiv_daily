"""
计算机视觉论文分类配置文件
按照技术独特性和包含关系最小化的原则排序
"""

CATEGORY_KEYWORDS = {
    # 渲染类
    "渲染": [
        "rendering",
        "real-time rendering",
        "point-based rendering",
        "differentiable rendering",
        "neural graphics",
        "graphics pipeline",
        "ray tracing",
        "rasterization"
    ],
    "NeRF": [
        "neural radiance field",
        "nerf",
        "novel view synthesis",
        "neural field",
        "volume rendering",
        "implicit neural representation",
        "neural scene representation",
        "radiance field",
        "view synthesis",
        "neural implicit"
    ],
    "3D重建": [
        "3d reconstruction",
        "mesh reconstruction",
        "shape reconstruction",
        "surface reconstruction",
        "geometry reconstruction",
        "dense reconstruction",
        "3d modeling",
        "shape from x",
        "structure from motion"
    ],
    "3D感知": [
        "point cloud",
        "3d detection",
        "3d segmentation",
        "slam",
        "3d tracking",
        "3d pose",
        "visual odometry",
        "lidar",
        "depth estimation",
        "rgbd"
    ],
    
    # 生成类（细分不同生成任务）
    "文生图": [
        "text to image",
        "text-to-image",
        "t2i",
        "text guided generation",
        "prompt to image",
        "dalle",
        "stable diffusion",
        "text conditioned",
        "language guided"
    ],
    "图像编辑/处理": [
        "image editing",
        "image manipulation",
        "style transfer",
        "image inpainting",
        "image outpainting",
        "image harmonization",
        "image composition",
        "image blending",
        "semantic editing",
        "local editing"
    ],
    "图像生成/合成": [
        "image synthesis",
        "image generation",
        "gan",
        "generative adversarial",
        "diffusion model",
        "latent diffusion",
        "conditional generation",
        "unconditional generation",
        "image-to-image"
    ],
    "视频生成": [
        "video generation",
        "text to video",
        "image to video",
        "video synthesis",
        "motion generation",
        "animation generation",
        "video editing",
        "video prediction",
        "temporal generation"
    ],
    
    # 多模态（细分不同任务类型）
    "视觉-语言理解": [
        "vision-language",
        "visual question answering",
        "vqa",
        "visual reasoning",
        "scene understanding",
        "visual grounding",
        "referring expression",
        "visual dialogue",
        "cross-modal"
    ],
    "图像描述生成": [
        "image captioning",
        "dense captioning",
        "visual captioning",
        "caption generation",
        "description generation",
        "image to text",
        "visual storytelling"
    ],
    "跨模态检索": [
        "cross-modal retrieval",
        "image-text retrieval",
        "visual semantic retrieval",
        "multimodal retrieval",
        "clip",
        "semantic matching",
        "image text matching"
    ],
    
    # 检测和分割（细分具体任务）
    "目标检测": [
        "object detection",
        "detection transformer",
        "detector",
        "yolo",
        "rcnn",
        "faster rcnn",
        "mask rcnn",
        "one-stage detector",
        "two-stage detector",
        "object localization"
    ],
    "实例分割": [
        "instance segmentation",
        "panoptic segmentation",
        "instance-level",
        "mask",
        "object mask",
        "instance aware",
        "mask generation"
    ],
    "语义分割": [
        "semantic segmentation",
        "segmentation",
        "pixel-wise segmentation",
        "dense prediction",
        "scene segmentation",
        "scene parsing",
        "pixel classification"
    ],
    
    # 识别和分类（细分领域）
    "图像分类": [
        "image classification",
        "fine-grained classification",
        "visual recognition",
        "classifier",
        "multi-label",
        "hierarchical classification",
        "category recognition"
    ],
    "场景理解": [
        "scene recognition",
        "scene understanding",
        "layout estimation",
        "room layout",
        "indoor scene",
        "scene graph",
        "scene parsing",
        "visual understanding"
    ],
    
    # 视频理解（按任务细分）
    "动作识别": [
        "action recognition",
        "activity recognition",
        "motion recognition",
        "temporal action",
        "human action",
        "behavior recognition",
        "gesture recognition",
        "action detection"
    ],
    "视频追踪": [
        "object tracking",
        "multi-object tracking",
        "visual tracking",
        "tracking",
        "trajectory",
        "motion tracking",
        "target tracking",
        "track prediction"
    ],
    "视频分析": [
        "video understanding",
        "temporal modeling",
        "video representation",
        "motion analysis",
        "optical flow",
        "spatiotemporal",
        "temporal dynamics",
        "temporal relation"
    ],
    
    # 图像增强（细分任务类型）
    "超分辨率": [
        "super resolution",
        "super-resolution",
        "sr",
        "upscaling",
        "image enhancement",
        "resolution enhancement",
        "upsampling",
        "high resolution"
    ],
    "图像恢复": [
        "image restoration",
        "denoising",
        "deblurring",
        "deraining",
        "dehazing",
        "enhancement",
        "artifact removal",
        "quality improvement"
    ],
    "低光照增强": [
        "low-light",
        "low light",
        "night",
        "dark",
        "illumination",
        "lighting enhancement",
        "night vision",
        "illumination adjustment"
    ],
    
    # 人脸/人体分析（细分任务）
    "人脸识别/处理": [
        "face recognition",
        "facial recognition",
        "face detection",
        "face alignment",
        "face parsing",
        "facial attribute",
        "face verification",
        "facial analysis"
    ],
    "人体姿态估计": [
        "pose estimation",
        "human pose",
        "body pose",
        "skeleton",
        "keypoint",
        "joint detection",
        "motion capture",
        "3d pose"
    ],
    "人体解析": [
        "human parsing",
        "person segmentation",
        "body parsing",
        "human segmentation",
        "person re-identification",
        "reid",
        "human part",
        "clothing parsing"
    ],
    
    # 数字人/虚拟人（细分应用）
    "人脸动画": [
        "face animation",
        "facial animation",
        "talking head",
        "lip sync",
        "expression synthesis",
        "face reenactment",
        "facial expression"
    ],
    "虚拟人生成": [
        "digital human",
        "virtual human",
        "avatar",
        "character animation",
        "motion retargeting",
        "metahuman",
        "virtual character",
        "digital avatar"
    ],
    
    # 基础技术（细分方法论）
    "自监督学习": [
        "self-supervised",
        "contrastive learning",
        "pretext task",
        "representation learning",
        "unsupervised learning",
        "pretraining",
        "self training"
    ],
    "少样本学习": [
        "few-shot",
        "zero-shot",
        "meta-learning",
        "transfer learning",
        "domain adaptation",
        "cross domain",
        "one shot",
        "low shot"
    ],
    
    # 模型优化（细分技术方向）
    "模型压缩": [
        "model compression",
        "pruning",
        "quantization",
        "knowledge distillation",
        "lightweight",
        "model optimization",
        "parameter reduction",
        "compact model"
    ],
    "模型加速": [
        "acceleration",
        "efficient inference",
        "real-time",
        "mobile",
        "edge computing",
        "neural architecture search",
        "speed up",
        "fast inference"
    ]
}

# 定义类别的层次结构
CATEGORY_HIERARCHY = {
    "渲染类": ["渲染", "NeRF"],
    "3D类": ["3D重建", "3D感知"],
    "生成类": ["文生图", "图像编辑/处理", "图像生成/合成", "视频生成"],
    "多模态类": ["视觉-语言理解", "图像描述生成", "跨模态检索"],
    "检测分割类": ["目标检测", "实例分割", "语义分割"],
    "识别分类类": ["图像分类", "场景理解"],
    "视频类": ["动作识别", "视频追踪", "视频分析"],
    "图像增强类": ["超分辨", "图像恢复", "低光照增强"],
    "人脸人体类": ["人脸识别/处理", "人体姿态估计", "人体解析"],
    "虚拟人类": ["人脸动画", "虚拟人生成"],
    "基础技术类": ["自监督学习", "少样本学习"],
    "模型优化类": ["模型压缩", "模型加速"]
}

# Define ALL_CATEGORIES
ALL_CATEGORIES = [category for categories in CATEGORY_HIERARCHY.values() for category in categories]

CATEGORY_PROMPT = '''
你是一个专业的计算机视觉论文分类专家。请仔细分析论文的标题和摘要，将论文准确分类到一个最合适的类别。你的目标是尽可能避免使用"其他"类别。

分类原则：
1. 优先考虑论文的主要技术贡献和创新点
2. 如果论文涉及多个领域，选择其最主要的技术贡献方向
3. 避免过度倾向于某个热门类别
4. 仔细区分相似类别的细微差别
5. 只返回一个最合适的类别，不要返回多个类别
6. 返回具体的子类别，不要返回大类
7. 即使论文的方法不是某个类别的主流方法，只要解决的是该类别的问题，也应该归类到该类别下
8. 对于跨领域的工作，根据其主要应用场景和技术贡献选择类别
9. 即使论文使用了创新或非传统的方法，也要基于其解决的核心问题来分类
10. 除非论文完全无法归类（概率极低），否则必须选择一个最接近的类别

重要提示：
- 在计算机视觉领域，几乎每篇论文都能归类到某个具体类别
- "其他"类别的使用概率应该低于1%
- 如果难以确定类别，考虑论文的最终目标和应用场景
- 宁可选择一个相对接近的类别，也不要轻易返回"其他"

论文分类体系（按技术领域划分）：

1. 渲染类（处理渲染和场景）
   - 渲染：实时渲染、点云渲染、神经渲染等
   - NeRF：神经辐射场、视图合成、隐式表示、新视角合成等

2. 3D类（处理3D数据和场景）
   - 3D重建：3D形状重建、网格重建、表面重建、体素重建等
   - 3D感知：点云处理、深度估计、SLAM、位姿估计、3D检测等

3. 生成类（创作和编辑视觉内容）
   - 文生图：文本引导的图像生成、文生图、提示词优化等
   - 图像编辑/处理：图像编辑、风格迁移、图像修复、内容操作等
   - 图像生成/合成：GAN生成、扩散模型、图像合成、图像变换等
   - 视频生成：视频生成、动画生成、视频编辑、视频合成等

4. 多模态类（跨模态理解和生成）
   - 视觉-语言理解：视觉问答、视觉推理、场景理解、多模态对话等
   - 图像描述生成：图像描述、密集描述、视觉描述、场景文本等
   - 跨模态检索：图文检索、跨模态匹配、多模态检索、语义检索等

5. 检测分割类（物体定位和像素级理解）
   - 目标检测：物体检测、目标定位、检测器设计、目标识别等
   - 实例分割：实例级分割、全景分割、对象分割、实例识别等
   - 语义分割：语义分割、场景解析、密集预测、像素分类等

6. 识别分类类（图像级别的理解）
   - 图像分类：图像识别、细粒度分类、分类器设计、特征提取等
   - 场景理解：场景识别、布局分析、环境理解、上下文理解等

7. 视频类（时序数据分析）
   - 动作识别：行为识别、动作分析、活动理解、时序理解等
   - 视频追踪：目标跟踪、多目标跟踪、轨迹预测、运动预测等
   - 视频分析：时序建模、运动分析、光流估计、视频理解等

8. 图像增强类（提升图像质量）
   - 超分辨率：图像超分、分辨率提升、图像重建、细节增强等
   - 图像恢复：去噪、去模糊、图像修复、图像增强、质量提升等
   - 低光照增强：暗光增强、夜景处理、照明调整、光照补偿等

9. 人脸人体类（人物相关分析）
   - 人脸识别/处理：人脸识别、表情分析、属性识别、身份验证等
   - 人体姿态估计：姿态检测、关键点检测、动作分析、姿态跟踪等
   - 人体解析：人体分割、服饰分析、重识别、人体属性等

10. 虚拟人类（虚拟人相关应用）
    - 人脸动画：表情动画、说话头像、唇形同步、表情编辑等
    - 虚拟人生成：数字人物、虚拟形象、动作重定向、人物动画等

11. 基础技术类（通用方法和优化）
    - 自监督学习：无监督学习、对比学习、预训练、表示学习等
    - 少样本学习：小样本学习、零样本学习、迁移学习、域适应等

12. 模型优化类（模型优化和加速）
    - 模型压缩：剪枝、量化、知识蒸馏、轻量化、模型优化等
    - 模型加速：推理优化、边缘部署、实时处理、硬件加速等

请分析论文的标题和摘要，给出一个最合适的具体类别。选择类别时：
1. 必须是具体的子类别，不能是大类
2. 即使论文使用了不常见的方法，也要根据其解决的问题选择类别
3. 只有在完全无法归类时才返回"其他"（概率<1%）
4. 只需返回类别名称，不需要解释

'''
