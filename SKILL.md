---
name: brand-social-media-workflow
description: 品牌社媒运营端到端六阶段工作流 —— ①资料知识库化 ②多平台声量调研（浏览器实抓）③内容矩阵规划与排期 ④分平台成稿（小红书/抖音/公众号/Instagram/TikTok/Facebook 可换）⑤配图与海报生图（后端可插拔：1XM / OpenAI / 通义万相 / 即梦，无 key 时降级为只出 prompt）⑥多语言与海外平台本地化（中/日/英）。当用户要求整理品牌资料建知识库、调研品牌或竞品社媒声量、做内容规划与排期、写平台成稿或视频脚本、生成配图海报、或把中文内容本地化成日/英海外版本时使用。End-to-end brand social media workflow: knowledge-base building, live social listening across platforms, content matrix planning, platform-specific copywriting, image/poster generation with pluggable backends, and multilingual localization (ZH/JA/EN) for Instagram/TikTok/Facebook.
---

# 品牌社媒全流程（通用版）

六阶段端到端跑通一个品牌的社媒运营。阶段可独立进入 —— 按用户手上有什么，从任意阶段切入。

```
Stage 1          Stage 2           Stage 3          Stage 4        Stage 5         Stage 6
知识库搭建   →   声量调研     →    内容矩阵规划  →   成稿撰写    →   配图/海报  →   多语言与海外延展
(资料→知识库)     (多平台实抓)       (规划/排期)      (分平台件套)    (三模式可选)    (本地化，非直译)
```

## §0 开工前：读配置（必做）

本 skill 的所有专属项都已抽离成配置。**动手前先按顺序找品牌档案与工具链配置：**

1. 当前工作目录下有没有 `brand-profile.md`（品牌档案）
2. 有没有 `config.yaml`（工具链与目标平台）
3. 都没有 → 用 AskUserQuestion 问最少的问题（一次 ≤4 个，带推荐默认项），不要上来就长篇问卷

模板见 [brand-profile.template.md](brand-profile.template.md) 与 [config.example.yaml](config.example.yaml)。
用户直接在对话里口述品牌名、品类、目标平台、目标语言也可以 —— 不必强制落盘。

### 可插拔点一览

| 维度 | 取值 | 没有配置时 |
|------|------|-----------|
| 知识库落地 | `workbuddy` / `obsidian` / `local` / `dingtalk` / `feishu` / `notion` / `none` | 默认 `workbuddy`（WorkBuddy 资料库，本机已连通） |
| 生图后端 | `1xm` / `openai` / `wanxiang` / `jimeng` / `none` | 默认 `none`（只出 prompt，不调用 API） |
| 平台组合 | `cn`（小红书/抖音/公众号）/ `global`（IG/TikTok/FB）/ 另含 4 种预设，见 [platforms.md](platforms.md) | 默认 `cn` |
| 目标语言 | `zh` / `ja` / `en` 任意组合 | 默认只做 `zh` |

**降级原则**：任何外部依赖缺失（没装 CLI、没 API key、没登录浏览器）都不阻断流程 —— 改走本地文件或只交付 prompt/文案，并**明确告诉用户哪一步降级了、降级成了什么**。绝不能因为缺 key 就整个任务失败。

## 通用规则（全阶段）

1. **大动作先确认**：Stage 1（上传范围）、Stage 3（规划周期与覆盖范围）开始前用 AskUserQuestion 确认，≤4 问，带推荐默认。
2. **来源纪律**：每个论断都能回溯到知识库或实抓数据。互动量、竞品提及、功效数据一个字都不能编。来源冲突时取平台站内最新数据，并注明分歧。
3. **交付物形态**：策略类文档出 HTML 交互报告（图表用 ECharts）；可发布文案出 Markdown；用户说"归档"时写入配置指定的知识库，写完**回读校验**。
4. **交付前自检**：HTML 报告必须在浏览器里渲染并抽查图表数据；文案必须对照知识库过事实与合规。
5. **合规红线**：功效数据、医疗宣称、认证引用必须走品牌档案里的合规条款（如第三方检测机构名不得出现在商业广告语境、必须带"效果因人而异"）。

## 阶段入口判断

- 给了品牌原始资料文件夹 → **Stage 1**
- 有品牌，想知道它的社媒声量 / 竞品格局 → **Stage 2**
- 有调研结论或品牌资产，要做内容规划 → **Stage 3**
- 有规划/选题，要可发布的成稿 → **Stage 4**
- 有成稿，要配图 → **Stage 5**
- 有中文素材（文档/文案/脚本/海报），要 中/日/英 版本或海外平台适配 → **Stage 6**

各阶段细则在 [reference.md](reference.md)，执行前先读对应章节。

## 关键技术备注（真实跑通过的经验）

- **知识库写入**：目标为 `dingtalk` 时先读对应 CLI 的 skill 文档。已知坑：`wiki space create --desc` 长度限制很紧（50 字符级，不是 500）；批量上传必须**前台执行**（后台跑会丢 hook 结果）；网盘配额常是组织级共享，报"空间不足"时先查 `quota` 和账号下的多组织，可能是**另一个组织**满了。
- **社媒抓取**：浏览器实抓远好于数据中心的指数服务 —— 后者普遍滞后数月。各平台选择器与 URL 规律见 [reference.md §2](reference.md)。
- **生图**：优先用异步任务接口（创建 + 轮询），同步接口大图易超时。**永远不要让模型在图里生成中文正文** —— 留白，后期叠字。

## 工具脚本

`scripts/gen_image.py` —— 多后端生图（异步任务 + 轮询 + 下载）。支持 `1xm` / `openai` 及任意 OpenAI 兼容端点；`--backend none` 只打印 prompt。

```bash
# 文生图
python scripts/gen_image.py "prompt text" output.png 1024x1536
# 参考图编辑（保持产品外观）
python scripts/gen_image.py --ref product.jpg --ref model.jpg "prompt" output.png 1024x1536
# 换后端 / 只出 prompt 不调用
python scripts/gen_image.py --backend openai "prompt" out.png 1024x1024
python scripts/gen_image.py --backend none "prompt" out.png 1024x1536
```

`scripts/overlay_text.py` —— **Mode A** 后期叠字（PIL）：把文字、logo 精确压到留白底图上，中文零错字。JSON 配置驱动。

```bash
python scripts/overlay_text.py overlay.json
```

`scripts/build_kb.py` —— 知识库**按落地目标预处理**：把 00-05 编号的模块文档转成目标格式（Obsidian 加 frontmatter 与双链索引；WorkBuddy 出纯 Markdown + 建库清单），一次生成、直接导入。

```bash
python scripts/build_kb.py --src ./kb-src --target obsidian --out ./kb --brand "品牌名"
python scripts/build_kb.py --src ./kb-src --target workbuddy --out ./kb
```

## 阶段速览

### Stage 1 · 知识库搭建
读品牌资料（PDF 有文本层用 pdfplumber；纯图 PDF 用 PyMuPDF 渲染成图再目视读取；docx 用 python-docx；xlsx 用 openpyxl），提炼成 6-8 个模块文档 + 按配置写入知识库 + 原始文件归档，写完回读校验。
落地目标支持 **WorkBuddy 资料库**（建文件夹 + doc 节点，落地后可直接语义检索问答）、**Obsidian**（frontmatter + `[[双链]]` + 标签）、**本地目录**、钉钉/飞书/Notion。细则：[reference.md §1](reference.md)。

### Stage 2 · 声量调研
在登录态浏览器里实抓目标平台搜索结果（品牌词 + 品类词）。统计品牌占位、竞品标题级提及、矩阵号投放痕迹、官方号数据。产出 HTML 报告：KPI 卡片 + 构成堆叠图 + 竞品提及排行。**铁律**：指数类服务滞后严重，"零声量"结论必须实抓复核后再下。细则：[reference.md §2](reference.md)。

### Stage 3 · 内容矩阵规划
按调研结论分派平台角色（有存量的平台=收割，零存量的=冷启动）。产出：账号人设、4-5 条内容支柱及各平台配比、首月排到选题标题级、全年季度框架、分平台标签/SEO 策略（含品牌名错写变体）、KPI 基线。细则：[reference.md §3](reference.md)。

### Stage 4 · 成稿撰写
**先定平台，再定件套** —— 绝不交付一套通用格式。每条平台的交付件套、文案结构、尺寸、标签策略见 [platforms.md](platforms.md)：

- **小红书**：笔记五件套（3 个备选标题 / 正文 / 配图方案 3 张 / 标签组 / 评论区预埋问答）
- **抖音**：视频脚本六件套（钩子标题 / 分镜脚本表 / 口播全文 / 拍摄素材清单 / BGM 节奏 / 标签组）
- **公众号**：长图文（标题 / 1500-3000 字正文 / 配图 brief / 排版说明 / 合规脚注）
- **Instagram / TikTok / Facebook**：见 platforms.md 海外组

标题必须嵌真实搜索词；所有论断锚定知识库；不造概念；交付前过合规闸门。

### Stage 5 · 配图与海报
**强制第一步：选模式**。用户说"生图/做海报/出封面"时，**不许**直接跳到写 prompt 或生成 —— 先用 AskUserQuestion 让用户选模式（讲清取舍、标推荐项），再按选中模式写 prompt，再生成。用户本轮已点名模式才跳过提问。

- **Mode A（打底 + PIL 叠字，中文零错字）**：edit 模式生成**无文字**底图 + 留白区，再用 `overlay_text.py` 压中文与 logo。像素级精确，改字秒级。适合长文案/密集信息/客户定稿。
- **Mode B（一句话直出 · 固定排版）**：单次 edit 调用，传入产品 + logo 参考图，prompt 里写明完整排版规格。快，版式可控，出图后必须放大核字。
- **Mode C（一句话直出 · 自由排版）**：只给素材 + 文字 + 调性，构图交给模型 —— 设计感最强、最像专业平面作品；出 n=2~3 挑一张。同样必须核字。注意模型**无法加载指定字体文件**，只能近似。

写 prompt 前**必须先看真实产品参考图**（别凭想象描述外观）。**成套海报（封面 + 内页）必须锁死四项统一规范 —— logo 位置、字体、配色、风格，每张 prompt 都写一遍，并把已完成封面作为内页的风格参考图传入**。可直接套用的 prompt 骨架、模式选择清单、出图前 QA 清单在 [poster-templates.md](poster-templates.md)。

### Stage 6 · 多语言与海外平台延展
把中文素材（知识库文档、文案、视频脚本、海报）做成 中/日/英 版本并适配目标海外平台。这是**本地化，不是翻译**：

- **日文 = 母语级润色，绝不直译**：用市场惯用词，不搬运中文隐喻，修饰语前置，用名词短语压缩 20-30%，品牌名用当地已注册的写法。**日文版压缩，中文版信息密度保持不变。**
- **英文 = 地道营销语 + 平台语态**；按语言换字体栈（日文 Yu Gothic / Noto Sans JP）。
- **分平台适配**：TikTok/Reels = 钩子前置 ≤60s + 屏显文字；Instagram = caption 前 125 字符放钩子 + 标签走首评 + 4:5/9:16；Facebook = 可承载长叙事 + 可点链接。
- **分市场合规是硬闸门**：功效类宣称在不同市场监管差异极大（日本薬機法、美国 FTC、欧盟化妆品/器械法规），按目标市场软化或重构表述，免责声明一并翻译。
- **一致性核对**：跨语言标题数必须对应卡/表数量；同词异义要显式消歧；不留中文生造词；所有本地化文字重新通读。

细则：[reference.md §6](reference.md)。

## 示例

| 用户说 | 进入 |
|--------|------|
| "帮我把这个文件夹的品牌资料整理成知识库（放到 WorkBuddy 资料库 / Obsidian）" | Stage 1（先问：文档结构、上传范围） |
| "问它一个问题" / "基于知识库回答……" | 已在库里的内容走语义检索问答（`rag_search.py`） |
| "调研一下我的品牌在小红书抖音公众号的声量" | Stage 2（品牌词 + 品类词实抓，HTML 报告） |
| "基于调研做个三平台内容规划" | Stage 3（先问：周期、纯官号还是含达人） |
| "把这个选题扩写成小红书笔记" | Stage 4（五件套） |
| "给我这三张配图的生图 prompt，我有产品图和模特图" | Stage 5（先问模式） |
| "把这条笔记/脚本/海报做成日文+英文版，发 Instagram 和 TikTok" | Stage 6（本地化 + 平台规范 + 合规 + 一致性核对） |

更多可直接改用的触发词模板见 [examples/prompts.md](examples/prompts.md)。
