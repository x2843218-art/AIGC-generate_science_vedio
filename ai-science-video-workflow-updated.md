---
name: ai-science-video-workflow
description: 生成科技纪录片 / 教学讲解类 AI 视频的标准工作流，适用于量子计算、材料科学、AI、SDK 教程、技术科普等主题。强调从中文脚本出发，先拆分镜与旁白，再用 Seedance / 即梦 / 视频生成 API 批量生成 5 秒或 15 秒视频片段，最后通过 FFmpeg 拼接、配音、字幕与质检，形成完整连续视频。当用户需要把技术脚本、科普文案、教程内容或 PPT 式材料转成可执行的视频制作方案、视频 prompts、分镜表、旁白、批量生成脚本或最终成片工作流时使用。
---

# AI Science Video Workflow

生成一套适合科技纪录片、技术讲解和教程视频的 AI 视频制作流程。整体思路是：**先把脚本拆成稳定的短镜头，再分别生成视频片段，用 FFmpeg 拼接成完整章节，最后使用剪映加字幕配音以及调整视频呈现效果**。不要直接要求模型一次生成长视频，也不要只用图片动画代替真正的视频生成。

本工作流主要复用之前成功操作中的方法：

- 用 Codex / ChatGPT 负责脚本整理、分镜拆解、视频 prompt 生成、文件结构规划和自动化脚本。
- 用 Seedance / 即梦 / 火山视频生成 API 负责每个短片段的视频画面生成。
- 用 FFmpeg 负责视频片段拼接、音频合成、和格式统一。
- 用 剪映 制作字幕、旁白配音和配背景音乐。
- 用人工质检处理字幕错误、画面跑偏、专业术语错误和镜头不连贯问题。

## 工作流

### 1. 明确视频目标

开始制作前，先对齐以下信息：

- 视频主题是什么。
- 视频受众是谁，是领导汇报、公司宣传、技术科普，还是教学培训。
- 视频总时长是多少。
- 每章时长是多少。（这一条根据实操经验，可以先根据大概的时长 修改旁白文本内容，把其放进剪映，看看具体时长，再来决定每个章节的时长）
- 是否需要中文旁白、中文字幕、英文关键词或双语字幕。
- 风格是科技纪录片、教学教程、发布会视觉、实验室写实，还是概念动画。
- 是否已经有完整脚本、PPT、参考视频、参考 prompt 或成功片段。

将目标改写成 2–4 条清晰产出，例如：

- 完成一支 60 秒的科技纪录片式章节视频。
- 每 5 秒为一个镜头片段，共 12 个片段。
- 每个片段提供中文画面说明、视频 prompt、旁白文本和转场建议。
- 最终通过 FFmpeg 拼接为一个完整 MP4。

技术事实不确定时，优先依据用户提供的脚本，不自行补写专业结论。

### 2. 统一视觉风格

同一章节内所有 prompt 要保持统一视觉语言。推荐使用以下风格锚点：

```text
真实科技纪录片
高端工业摄影
电影级光影
冷蓝、银白、深黑、少量金色高光
轻微胶片颗粒
真实物理运动
高级科学可视化
实验室、晶格、粒子、数据流、能量景观
```

避免以下问题：

- 每个镜头风格差异过大。
- 出现大量不可控文字。
- 把复杂公式直接放进视频画面。
- 画面像 PPT 动画而不是真实视频。
- 科学图示画错、结构错、符号错。
- 镜头只是一张图轻微缩放，没有真实动态。

复杂科学图可以后期单独用 PPT / After Effects / Manim / 原生 Shape 做，再叠加到视频中，不强行让视频模型生成准确公式。

### 3. 准备项目文件

在用户指定目录中建立如下结构：

```text
项目/video/
├── deomo_standard.py
├── README.md
├── script.md
├── storyboard.md
├── prompts/
│   └── chapter01/
│       └── chapter01.json
├── voiceover.md
├── subtitles.srt
├── assets/
│   ├── references/
│   ├── images/
│   └── audio/
├── outputs/
│   ├── shots/
│   │   ├── shot001.mp4
│   │   ├── shot002.mp4
│   │   └── ...
│   └── chapter01.mp4
└── scripts/
    ├── generate_chapter.py
    ├── merge_chapter.py
    └── burn_subtitles.py
```

命名规则：

- 单条测试脚本保留为 `deomo_standard.py`。
- 批量生成脚本命名为 `scripts/generate_chapter.py`。
- 拼接脚本命名为 `scripts/merge_chapter.py`。
- 每章 prompt 文件保存为 `prompts/chapterXX/chapterXX.json`。
- 镜头视频统一命名为 `shot001.mp4`、`shot002.mp4`。
- 每章最终输出命名为 `chapter01.mp4`。
- 旁白保存为 `voiceover.md` 和最终音频文件。

### 4. 整理输入脚本

把用户提供的原始脚本整理成统一格式：

```text
章节标题：
章节目标：
总时长：
旁白全文：
画面内容：
关键词：
必须出现的科学概念：
不能出现的画面：
参考风格：
```

如果脚本较长，先按语义拆分为段落，再按时间拆成镜头。不要直接把一整段旁白塞进一个 prompt。

对于科技类视频，必须保留原始专业概念，例如：

- 材料发现
- 量子计算
- Ising 模型
- QUBO
- 能量景观
- 原子、电子、晶格
- 实验室、超级计算、数据、材料结构

如果某个概念比较抽象，要优先转化成可视化隐喻，而不是只堆文字。

### 5. 拆分镜头

根据视频总时长和视频模型能力拆分镜头：

- Seedance / 即梦常用方式：每个镜头 5 秒或 15 秒。
- 60 秒章节：推荐 12 个 5 秒片段，或者 4 个 15 秒片段。
- 90 秒章节：推荐 18 个 5 秒片段，或者 6 个 15 秒片段。
- 专业科普视频优先使用 5 秒片段，因为更容易控制画面准确性和节奏。
- 情绪铺垫、宏大场景、过渡镜头可以使用 15 秒片段。

每个镜头必须包含：

```text
镜头编号：
时间段：
旁白对应句：
画面目标：
画面内容：
镜头运动：
视觉风格：
生成 prompt：
负面 prompt：
转场方式：
质检重点：
```

镜头之间要形成连续叙事，不要每个 prompt 都像独立海报。

### 6. 生成视频 Prompts

视频 prompt 可以使用中文或英文。对于 Seedance / 即梦中文场景，中文 prompt 的可控性较好，prompt 要写成“视频画面描述”，而不是只写抽象指令。

每条 prompt 应包含：

- 主体：画面中最重要的对象。
- 场景：实验室、数据中心、原子尺度、宇宙空间、材料晶格等。
- 动作：镜头推进、旋转、扫描、粒子流动、数据浮现。
- 风格：真实科技纪录片、高端工业摄影、电影级光影。
- 画质：高清、真实光照、体积光、轻微胶片颗粒。
- 镜头语言：微距、广角、长焦、缓慢推近、横向跟拍、环绕拍摄。
- 色彩：冷蓝、银白、深黑、少量金色高光。
- 限制：避免文字、水印、错误公式、错误科学结构和 PPT 式画面。

推荐 prompt 结构：

```text
[主体与场景]，[动作和镜头运动]，[科学可视化元素]，[视觉风格]，[光影和色彩]，[画质与质感]，[避免事项]
```

示例：

```text
冷暗实验室中，一组发光原子晶格从黑色背景中缓慢浮现，电子以柔和蓝色光轨在原子之间流动。镜头使用60毫米微距缓慢推近，晶格边缘有细微景深虚化，周围漂浮少量粒子和数据光点。整体呈现真实科技纪录片质感，高端工业摄影，冷蓝与银白色调，电影级体积光，轻微胶片颗粒，避免文字、水印和错误公式。
```

视频模型提示词最好明确主体、动作、环境、光线、风格和镜头运动；很多视频生成文档也建议把 prompt 写成“视频画面描述”，而不是只给模型下命令。参考：Amazon Nova Reel prompting best practices。

### 7. 生成 chapterXX.json

`chapterXX.json` 推荐结构：

```json
[
  {
    "shot_id": "shot001",
    "scene": "Chapter 01 / Scene 01 - 人类材料文明的起点",
    "duration": 5,
    "prompt": "远古森林夜晚，黑暗中一双人类手掌不断摩擦木材，火星从材料接触处产生并飞向空中，篝火逐渐燃起，周围散落石器和原始工具。24毫米广角低角度镜头缓慢推进，捕捉火焰、岩石纹理和手部运动，橙红火光照亮深黑环境，真实历史纪录片摄影，高端电影级光影，轻微胶片颗粒。镜头最后让一颗明亮火星占据画面中心，向下一镜头过渡。",
    "audio_prompt": "真实场景音效：木材摩擦声、树枝断裂声、火星爆裂声、篝火燃烧声、夜晚森林环境声。不要生成背景音乐，不要生成旁白，不要生成人声解说。",
    "notes": "表现材料改变文明的起点，不加入神秘元素，保持真实人类早期技术场景。",
    "previous_connection": "无上一镜头，作为章节开场，从文明起源进入材料主题。",
    "next_connection": "中心火星继续飞行，转化为古代冶炼炉中的金属火花。"
  }
]
```

要求：

- 一个对象对应一个视频片段。
- `prompt` 用中文画面描述。
- `duration` 明确写 5 或 15。
- `notes` 写明叙事目的和科学准确性提醒。
- 不要把所有镜头写成同一个抽象场景。
- 不要在 prompt 末尾添加 `--duration`、`--watermark`、`--camerafixed` 等网页端参数。

### 7.1 通俗脚本转 Seedance JSON Prompt 的元指令

当需要把通俗中文脚本转成 `prompts/chapterXX/chapterXX.json` 时，可以使用以下元指令 Prompt。它的作用是让 AI / Codex 自动把普通脚本改写成 Seedance、Kling、Runway、Veo 等视频大模型可读取的分镜 JSON。

```text
你是一名顶级 AI 科技纪录片导演、电影分镜师和视频生成 Prompt 工程师。

你的任务是：把我提供的通俗中文脚本，改写成适合 Seedance 视频大模型生成的分镜 Prompt，并输出为严格 JSON 数组格式。

注意：
你不是生成一组互相独立的视频片段，而是在设计一部完整纪录片。
每个 shot 需要单独成立，同时必须考虑与前后 shot 的视觉连续性、情绪递进和镜头衔接。

重要目标：
1. 不要生成 HTML、CSS、JS、PPT 页面、网页动画或普通文字分镜。
2. 你要把脚本拆成多个真实视频镜头 shot。
3. 每个 shot 的时长默认 5 秒。
4. 每个 shot 必须像真实纪录片镜头，而不是 PPT 动画。
5. 输出内容要能直接放进 prompts/chapterXX/chapterXX.json，被 Python 脚本读取生成视频。

输出格式必须是严格 JSON 数组，不要写解释文字，不要写 markdown，不要加代码块标记。

每个对象必须包含以下字段：
- shot_id：格式为 shot001、shot002、shot003……
- scene：格式为 Chapter XX / Scene XX - 场景名称
- duration：默认填 5
- prompt：视频生成提示词
- audio_prompt: 声音设计
- notes：科学准确性、叙事目的或避免事项
- previous_connection: 本镜头承接上一镜头什么元素
- next_connection: 本镜头结束给下一镜头留下什么元素

镜头连续性设计:
- 每个 shot 必须考虑：
1. 上一个 shot 如何自然进入当前 shot
2. 当前 shot 如何结束并引导下一个 shot
3. 两个镜头之间使用什么视觉元素连接？
4.整个章节的视觉语言、色彩、摄影风格保持统一
Seedance 视频模型无法真正理解 previous_connection  和 next_connection 字段，因此必须把镜头衔接逻辑直接写入 prompt 内。
- 每个 prompt 必须包含：
1. 当前镜头开始时承接上一镜头的视觉元素
2. 当前镜头主体动作
3. 镜头运动过程
4. 当前镜头结束时留下可供下一镜头继承的视觉元素
- 优先使用以下连续方式：
A. 视觉元素匹配转场
例如：
shot001:
火星飞溅的火花逐渐形成晶格光点
shot002:
晶格光点进入硅片内部，变成电子流
B. 运动方向连续
例如：
shot001:
镜头向右快速横移
shot002:
继续沿同方向进入服务器机房
C. 颜色连续
例如：
shot001:
火焰橙色逐渐转为金属黄色
shot002:
黄色光线转化为芯片蓝色冷光
D. 微观尺度连续
例如：
宏观材料
↓
金属表面
↓
晶格结构
↓
原子排列
↓
电子云
E. 空间连续
例如：
实验室屏幕
↓
进入屏幕内部的数据空间
↓
进入材料模拟世界
- 每个镜头的 prompt 中必须包含合理的结尾动作，让下一镜头可以自然接入。

声音设计要求:如果开启 generate_audio：
1. 只生成与画面匹配的环境音效：
- 机械声
- 实验设备声
- 自然环境声
- 材料加工声
- 科学仪器运行声
2. 禁止生成：
- 背景音乐
- 史诗配乐
- 情绪音乐
- 旁白
- 解说声音
3. 声音风格：
真实纪录片现场收音，
自然、克制、符合物理规律。

prompt 写作要求：
1. 用中文写。
2. 不要只概括“展示某某内容”，要写成可生成视频的画面。
3. 每个 prompt 必须包含：
   - 画面主体
   - 场景环境
   - 具体动作
   - 镜头运动
   - 镜头焦段或拍摄方式
   - 光线与色彩
   - 纪录片质感
   - 科学可视化细节
4. 镜头语言要具体，例如：
   - 24毫米广角
   - 35毫米手持纪录片镜头
   - 50毫米标准镜头
   - 60毫米微距
   - 85毫米长焦压缩
   - 低角度推进
   - 缓慢推近
   - 快速拉远
   - 横向跟拍
   - 俯冲穿越
   - 环绕拍摄
   - 匹配剪辑
5. 视觉风格保持统一：
   - 真实科技纪录片
   - 高端工业摄影
   - 电影级光影
   - 冷蓝、银白、深黑、少量金色高光
   - 轻微胶片颗粒
   - 真实物理运动
   - 高级科学可视化
6. 避免让画面变成：
   - PPT
   - 幻灯片
   - 网页动画
   - 扁平信息图
   - 卡通
   - 童话化
   - 过度科幻
   - 大量文字
   - 错误公式
   - 错误化学式
   - 随意出现具体数字
7. 如果脚本中有专业概念，要用视觉隐喻表达，但不能扭曲科学含义。
8. 如果涉及科学准确性，要在 notes 中提醒：
   - 不要绝对化
   - 不要说传统方法完全无效
   - 不要把 AI 描绘成完全无用
   - 不要把量子表现成魔法
9. 每个 shot 只表现一个核心信息，不要把太多内容塞进一个镜头。
10. 每个 shot 的 prompt 末尾必须包含：- 当前镜头如何结束 - 下一镜头可以继承的视觉元素
11. 一个 60 秒章节通常拆成 10–12 个 shot；一个 90 秒章节通常拆成 15–18 个 shot。
12. 每个 prompt 控制在 120–220 个中文字符左右，但画面信息必须完整。
13. 不要在 prompt 末尾添加 --duration、--watermark、--camerafixed 等参数，除非我明确要求。
14. 声音要求：生成真实场景音效（SFX），不生成背景音乐（BGM），不生成旁白。

使用方式：

```text
[粘贴上面的元指令]

脚本：
第一章节：材料发展的困境——为什么材料发现变慢了？
……
```

### 7.2 Seedance Prompt 清洗规则

在提交给 Seedance / 即梦 / 火山视频生成 API 前，需要对 `prompts/chapterXX/chapterXX.json` 进行清洗，避免把网页端参数或英文负面词直接传入 API。

对每个 shot 执行以下规则：

- 不修改 `shot_id`。
- 不修改 `scene`。
- `duration` 字段保留为 `5`。
- 删除每个 `prompt` 末尾的网页端参数，例如：
  - `--duration`
  - `--camerafixed`
  - `--watermark`
- 删除英文 negative prompt，例如：
  - `no slideshow`
  - `no PowerPoint`
  - `no static image`
  - `no flat animation`
- 保留纯中文画面描述。
- 不要把负面提示词混在中文画面描述里。
- 如果需要限制画面风格，应该用自然中文写入画面描述，例如：`画面应具有真实纪录片质感，避免幻灯片式静态画面。`

清洗前示例：

```json
{
  "shot_id": "shot001",
  "scene": "Chapter 01 / Scene 01",
  "duration": 5,
  "prompt": "火星微距开场，画面从暖橙火光过渡到冷蓝硅片反光。no slideshow, no PowerPoint --duration 5 --camerafixed false --watermark false"
}
```

清洗后示例：

```json
{
  "shot_id": "shot001",
  "scene": "Chapter 01 / Scene 01",
  "duration": 5,
  "prompt": "火星微距开场，画面从暖橙火光过渡到冷蓝硅片反光，真实纪录片质感，高端工业摄影，轻微胶片颗粒，真实物理运动。"
}
```

### 8. 调用视频生成 API

如果使用 Seedance / 即梦 / 火山视频 API，通常流程是：

1. 准备 API Key。
2. 读取 `prompts/chapterXX/chapterXX.json`。
3. 对每条 prompt 发起视频生成任务。
4. 轮询任务状态。
5. 下载生成视频到 `outputs/shots/`。
6. 失败任务自动重试或记录到 `failed_clips.json`。
7. 人工检查不合格镜头，重新生成。

注意：

- Seedance 视频生成和火山 TTS 是两个不同能力。
- 视频生成通常按时长、分辨率和模型计费。
- 生成前先用 1–2 个镜头测试风格，不要一次性生成整章。
- 如果已经有成功 prompt，应优先复用其句式、镜头语言和风格锚点。
- 对专业内容，宁愿多拆镜头，也不要让一个 prompt 承担太多信息。

### 8.1 当前已跑通的 Seedance 批量生成流程

在单条测试脚本 `deomo_standard.py` 跑通后，项目进一步整理成了批量生成第一章节视频的工程化流程。

当前项目中主要包含：

```text
deomo_standard.py                  # 单条 Seedance 视频生成测试脚本
prompts/chapter01/chapter01.json  # 第一章节 12 个镜头的 prompt 文件
scripts/generate_chapter.py       # 批量生成镜头视频脚本
scripts/merge_chapter.py          # 使用 FFmpeg 拼接章节视频脚本
outputs/shots/                    # 保存 shot001.mp4 到 shot012.mp4
outputs/chapter01.mp4             # 第一章节最终拼接视频
README.md                         # 项目运行说明
```

整体流程为：

```text
chapter01.json
  ↓
generate_chapter.py 逐个读取 shot prompt
  ↓
调用 Seedance API 生成视频任务
  ↓
轮询任务状态
  ↓
下载生成结果到 outputs/shots/
  ↓
merge_chapter.py 调用 FFmpeg
  ↓
拼接得到 outputs/chapter01.mp4
```

这个流程相比手动生成视频片段，优势在于可以复用同一套脚本批量生成不同章节。后续如果继续制作第二章、第三章，只需要新增对应的 prompt JSON 文件，并复用批量生成和拼接脚本。

批量生成脚本应遵守以下规则：

- 保留官方火山方舟 SDK：`from volcenginesdkarkruntime import Ark`。
- API Key 从环境变量 `ARK_API_KEY` 读取，不写死在代码中。
- 使用模型：`doubao-seedance-2-0-260128`。
- 逐个调用 `client.content_generation.tasks.create`。
- 每个任务创建后轮询状态，直到 `succeeded` 或 `failed`。
- 成功后从返回结果中找到视频 URL。
- 下载视频到 `outputs/shots/`。
- 文件名使用 `shot_id`，例如 `shot001.mp4`。
- 每个镜头之间等待 2 秒，避免请求过快。
- 失败任务不要直接覆盖，应记录失败信息，方便单独重试。

### 9. FFmpeg 拼接

生成所有视频片段后，先统一规格，再拼接。

推荐统一参数：

- 分辨率：1920×1080
- 帧率：30fps
- 编码：H.264
- 音频：AAC
- 像素格式：yuv420p

拼接列表示例：

```text
file 'C:/project/video/outputs/shots/shot001.mp4'
file 'C:/project/video/outputs/shots/shot002.mp4'
file 'C:/project/video/outputs/shots/shot003.mp4'
```

FFmpeg 拼接命令示例：

```bash
ffmpeg -y -f concat -safe 0 -i chapter01_concat.txt -c copy chapter01_no_audio.mp4
```

如果片段编码不一致，先转码再拼接：

```bash
ffmpeg -y -i shot001.mp4 -vf "scale=1920:1080,fps=30" -c:v libx264 -pix_fmt yuv420p -c:a aac shot001_norm.mp4
```

合成旁白：

```bash
ffmpeg -y -i chapter01_no_audio.mp4 -i voiceover.mp3 -c:v copy -c:a aac -shortest chapter01_with_voice.mp4
```

烧录字幕：

```bash
ffmpeg -y -i chapter01_with_voice.mp4 -vf "subtitles=subtitles.srt" -c:a copy chapter01_final.mp4
```

Windows 路径中如果有空格或中文，必须加引号。

### 9.1 使用 merge_chapter.py 拼接章节

生成所有镜头视频后，使用 `scripts/merge_chapter.py` 调用 FFmpeg，将 `outputs/shots/` 中的镜头按顺序拼接为完整章节视频。

第一章节默认拼接以下文件：

```text
outputs/shots/shot001.mp4
outputs/shots/shot002.mp4
outputs/shots/shot003.mp4
outputs/shots/shot004.mp4
outputs/shots/shot005.mp4
outputs/shots/shot006.mp4
outputs/shots/shot007.mp4
outputs/shots/shot008.mp4
outputs/shots/shot009.mp4
outputs/shots/shot010.mp4
outputs/shots/shot011.mp4
outputs/shots/shot012.mp4
```

输出文件为：

```text
outputs/chapter01.mp4
```

拼接前应检查：

- 12 个镜头文件都存在。
- 每个文件大小大于 0。
- 文件名与 `shot_id` 一致。
- 视频格式可以被 FFmpeg 正常读取。
- 如果视频编码、分辨率或帧率不一致，应先统一转码，再进行拼接。

推荐运行方式：

```bash
python scripts/merge_chapter.py
```

`merge_chapter.py` 应自动生成 FFmpeg concat 列表文件，然后执行拼接命令。不要手动一个个拖进剪辑软件，除非需要人工精修转场。

### 10. 字幕处理

字幕不要完全依赖视频模型自动生成，因为 AI 视频模型很容易生成错字、乱码或伪文字。

推荐流程：

1. 使用旁白文案作为字幕源。
2. 用剪映生成对应字幕。
3. 人工检查专业词汇。
4. 字幕样式保持简洁，不遮挡科学画面。

字幕原则：

- 每条字幕不超过两行。
- 每行不宜过长。
- 专业名词保持统一。
- 不要让视频模型在画面中直接生成中文文字。
- 标题和关键词可以后期用剪辑软件或 FFmpeg 单独叠加。

### 11. 旁白与配音

Seedance 视频生成和 TTS 配音是两个不同环节。不要把“视频生成 API”误认为一定能直接完成高质量旁白。

推荐流程：

1. 先根据章节脚本拆出逐镜头旁白。
2. 每个 5 秒镜头控制在 15–25 个中文字左右。
3. 每个 15 秒镜头控制在 45–70 个中文字左右。
4. 使用火山 TTS、剪映生成完整旁白音频（剪映里可使用播音旁白）。
5. 如果 TTS 与画面节奏不匹配，优先调整旁白，不要强行拉伸视频（为不影响观看体验，画面倍速极限为0.6）。

旁白要求：

- 中文自然、像纪录片解说，不要像论文摘要。
- 每句话只讲一个核心点。
- 少用过长定语。
- 专业术语后尽量给一句直觉解释。
- 重要概念可以用画面辅助，不必全部塞进旁白。

### 12. 质检与返工

每个片段生成后都要质检，不要等整章拼完才检查。

质检维度：

- 视频是否需要配背景音乐。
- 画面是否符合脚本。
- 是否出现乱码文字。
- 是否出现错误公式或错误科学结构。
- 是否有水印、logo 或奇怪字幕。
- 人物手部、脸部是否畸形。
- 镜头是否真的有运动。
- 与前后镜头是否能衔接。
- 色彩和风格是否统一。
- 旁白时长是否匹配。
- 字幕是否准确。
- 数学公式是否正确。

常见问题与处理方式：

| 问题 | 处理方式 |
|---|---|
| 画面像 PPT | prompt 增加真实镜头运动、微距、跟拍、景深、体积光 |
| 文字乱码 | prompt 明确避免大面积文字；文字后期添加 |
| 科学结构错误 | 改成抽象科学可视化，或后期叠加准确图示 |
| 镜头不连贯 | 给每个 prompt 加上一致的视觉锚点和转场描述 |
| 旁白太长 | 先删旁白，再考虑延长镜头 |
| 视频片段规格不一致 | 统一转码后再拼接 |
| API 生成失败 | 记录失败任务，单独重试 |

### 12.1 README.md 运行说明

项目根目录需要保留 `README.md`，用于说明如何从 prompt 文件批量生成视频片段，并拼接成完整章节。

README 至少应包含：

1. 项目用途  
   说明本项目用于根据 `prompts/chapter01/chapter01.json` 批量生成 Seedance 视频片段，并用 FFmpeg 拼接为完整章节视频。

2. API Key 设置方式  
   API Key 必须从环境变量 `ARK_API_KEY` 读取，不能写死在代码中。

   Windows PowerShell：

   ```powershell
   $env:ARK_API_KEY="你的 API Key"
   ```

   macOS / Linux：

   ```bash
   export ARK_API_KEY="你的 API Key"
   ```

3. 依赖安装方式

   ```bash
   pip install volcenginesdkarkruntime requests
   ```

   同时需要本地安装 FFmpeg，并确认命令行可用：

   ```bash
   ffmpeg -version
   ```

4. 单条测试方式

   ```bash
   python demo_standard.py
   ```

5. 批量生成第一章节镜头

   ```bash
   python scripts/generate_chapter.py
   ```

6. 拼接第一章节视频

   ```bash
   python scripts/merge_chapter.py
   ```

7. 输出结果说明

   ```text
   outputs/shots/shot001.mp4 到 shot012.mp4
   outputs/chapter01.mp4
   ```

8. 常见问题排查  
   包括 API Key 未设置、依赖未安装、FFmpeg 不可用、某个 shot 生成失败、视频文件缺失等。

### 13. 最终交付

默认交付以下文件：

```text
outputs/
├── shots/
│   ├── shot001.mp4
│   ├── shot002.mp4
│   └── ...
├── chapter01.mp4
├── chapter01_with_voice.mp4
├── chapter01_final.mp4
├── prompts.json 或 prompts/chapter01/chapter01.json
├── storyboard.md
├── voiceover.md
├── subtitles.srt
└── failed_clips.json
```

如果是完整项目，还应交付：

- `script.md`：完整视频脚本。
- `storyboard.md`：逐镜头分镜。
- `prompts/chapterXX/chapterXX.json`：可批量生成视频的 prompt。
- `voiceover.md`：旁白稿。
- `subtitles.srt`：字幕文件。
- `demo_standard.py`：单条测试脚本。
- `scripts/generate_chapter.py`：批量生成脚本。
- `scripts/merge_chapter.py`：拼接脚本。
- `README.md`：运行说明。
- `outputs/chapterXX.mp4`：最终章节成片。

## 推荐制作顺序

```text
原始脚本
  ↓
使用元指令生成 chapterXX.json
  ↓
清洗 prompt 参数
  ↓
测试 1–2 个镜头
  ↓
调整风格锚点
  ↓
运行 generate_chapter.py 批量生成视频片段
  ↓
人工质检
  ↓
重新生成失败片段
  ↓
运行 merge_chapter.py 调用 FFmpeg 拼接
  ↓
生成字幕和配音
  ↓
配背景音乐(声音参数-7.0)
  ↓
最终导出
```

## 适用场景

本工作流适用于：

- 量子计算科普视频。
- 材料科学纪录片。
- AI 技术讲解视频。
- SDK 上手教程视频。
- 公司技术展示视频。
- 教学案例动画。
- 科研概念解释视频。
- PPT 内容转视频。
- 领导汇报用 AI 视频样片。

不适合直接用于：

- 要求完全科学精确的动态图表。
- 需要大量真实实验数据可视化的视频。
- 需要可控角色连续表演的剧情片。
- 需要一次性生成 3–5 分钟完整连续镜头的视频。
- 公式、代码、表格特别多的教程视频。

这些内容应拆分为“AI 视频背景 + 后期准确叠加”的方式制作。


## 核心原则

1. 先写清楚脚本，再生成画面。
2. 先短镜头测试，再批量生成。
3. 一个镜头只表达一个核心意思。
4. 专业文字、公式和字幕后期添加，不交给视频模型直接生成。
5. Seedance 负责视频画面，TTS 负责旁白，FFmpeg 负责拼接。
6. Prompt 要保持统一风格锚点，避免每个镜头像不同项目。
7. 复杂科学内容宁愿抽象可视化，也不要生成错误细节。
8. 所有片段必须统一规格后再拼接。
9. 最终视频质量取决于“分镜控制 + prompt 稳定 + 人工质检 + 后期合成”。
10. 不要追求一次生成完整长视频，成功方法是短片段流水线。
