# brand-social-media-workflow

品牌社媒运营端到端六阶段工作流 skill —— 通用版。

把品牌资料变成知识库，把声量调研变成内容规划，把规划变成分平台成稿，把成稿变成配图海报，
再把中文内容本地化到日/英海外市场。**全链路可插拔**：知识库落地位置、生图后端、平台组合、目标语言都能换。

> 🗳️ 这个 skill 是我们参加 **千问办公 AI 生产力大赛** 的作品。
> 如果它对你有用，[帮我们投一票](https://cydqr2t5.qwenwork.host/works/FINST-8UE660B1K3K9I7YYGXBLUD8WGRCM3XI42KJUMB7E) —— 大概 30 秒，非常感谢。

## 六阶段

```
Stage 1          Stage 2           Stage 3          Stage 4        Stage 5         Stage 6
知识库搭建   →   声量调研     →    内容矩阵规划  →   成稿撰写    →   配图/海报  →   多语言与海外延展
```

阶段解耦 —— 手上有哪一步的材料，就从哪一步进。

## 安装

### 从 GitHub 安装（推荐）

直接 clone 到你的 skills 目录，目录名就是 skill 名，clone 完即可用：

```bash
# WorkBuddy（用户级）
git clone git@github.com:<你的用户名>/brand-social-media-workflow.git \
  ~/.workbuddy/skills/brand-social-media-workflow

# Claude Code
git clone git@github.com:<你的用户名>/brand-social-media-workflow.git \
  ~/.claude/skills/brand-social-media-workflow
```

更新：`cd` 进去 `git pull` 即可。

### 手动安装

把整个 `brand-social-media-workflow/` 文件夹放进 skills 目录：

| 工具 | 位置 |
|------|------|
| WorkBuddy（用户级） | `~/.workbuddy/skills/` |
| WorkBuddy（项目级） | `<项目>/.workbuddy/skills/` |
| Claude Code | `~/.claude/skills/` 或 `<项目>/.claude/skills/` |
| CodeBuddy | `~/.codebuddy/skills/` |

目录结构必须是 `<skills>/brand-social-media-workflow/SKILL.md`。

### 其他 Agent 工具

`SKILL.md` 用标准 `name` / `description` frontmatter，任何支持 agent skills 规范的工具都能直接读。
不支持 skill 规范的工具，直接把 `SKILL.md` 的内容喂给 agent 作为系统提示也一样有效。

## 依赖

**核心流程零依赖。** 全部阶段都能在没有外部服务的情况下跑完：

| 能力 | 需要什么 | 没有时 |
|------|---------|-------|
| 知识库落地（WorkBuddy 资料库） | WorkBuddy 的 `library` skill | 降级为本地目录 |
| 知识库落地（Obsidian） | 一个 vault 路径 | 降级为本地目录 |
| 声量调研 | 一个能登录目标平台的浏览器 | 改用公开页面 + 用户提供的数据，并标注数据边界 |
| 生图 | 任意 OpenAI 兼容生图 API 的 key | `--backend none` 只出 prompt，贴到任意生图工具用 |
| Mode A 叠字 | Python + Pillow（`pip install pillow`） | 退回 Mode B/C 直出 |
| PDF/docx 解析 | `pip install pdfplumber pymupdf python-docx openpyxl` | 让用户提供可复制文本 |

生图后端可选：`1xm`（gpt-image-2，国内可用）/ `openai` / `通义万相` / `即梦` / 任意 OpenAI 兼容端点。

## 配置

三步，都可在对话里口头完成：

1. **`brand-profile.md`** —— 复制 `brand-profile.template.md` 填写品牌基础、视觉规范、合规红线、素材位置。只填真有的，其余留空，agent 会在用到时单独问。
2. **`config.yaml`** —— 复制 `config.example.yaml`，指定知识库落地位置、生图后端、平台组合、目标语言。
3. **环境变量** —— 只在用生图 API 时需要：`IMAGE_API_KEY`，可选 `IMAGE_BACKEND` / `IMAGE_BASE_URL` / `IMAGE_MODEL`。

不落盘也行 —— 直接在对话里说"知识库放本地、用 1XM 生图、做小红书+抖音+公众号、出中日双语版"。

## 目录

```
SKILL.md                      主文件（六阶段总览 + 通用规则 + 入口判断）
reference.md                  各阶段细则（读/抓/规划/写/生图/本地化的全部方法论）
platforms.md                  平台规格库（12 个平台的尺寸、件套、标签、审核严格度）
poster-templates.md           Stage 5 填空式 prompt 骨架 + 模式选择 + QA 清单
brand-profile.template.md     品牌档案模板
config.example.yaml           工具链与目标配置示例
examples/prompts.md           各阶段触发词模板
scripts/gen_image.py          多后端生图（纯标准库，无需 pip）
scripts/overlay_text.py       Mode A 后期叠字（需 pillow）
scripts/build_kb.py           知识库按落地目标预处理（纯标准库）
```

## 知识库落地目标

| target | 落哪里 | 特点 |
|--------|--------|------|
| `workbuddy` | WorkBuddy 资料库（默认） | 建文件夹节点 + doc 节点，落地后可直接语义检索问答 |
| `obsidian` | Obsidian vault | YAML frontmatter + `[[双链]]` + 标签；品牌名错写变体写进 `aliases` |
| `local` | 本地 Markdown 目录 | 零依赖 |
| `dingtalk` | 钉钉知识库 + 钉盘 | 需 dws CLI 且已登录 |
| `feishu` / `notion` | 对应平台 | 需连接器 |
| `none` | 不归档 | 文档留在工作目录 |

换目标只需改 `config.yaml` 里的一行，或直接在对话里说"知识库放 Obsidian / 放 WorkBuddy 资料库"。
`scripts/build_kb.py` 负责把同一份 00-05 文档预处理成目标格式，落地动作见 `reference.md §1.3`。

## 脚本用法

```bash
# 生图（文生图）
python scripts/gen_image.py "prompt" out.png 1024x1536

# 生图（参考图编辑，保持产品外观；--ref 可重复）
python scripts/gen_image.py --ref product.jpg --ref model.jpg "prompt" out.png 1024x1536

# 无 key 只出 prompt
python scripts/gen_image.py --backend none --save-prompt p.txt "prompt" out.png 1024x1536

# Mode A 叠字
python scripts/overlay_text.py overlay.json          # 见脚本头部注释的 JSON 格式
python scripts/overlay_text.py overlay.json --preview # 只看布局不写文件

# 知识库按目标预处理
python scripts/build_kb.py --src ./kb-src --target obsidian \
  --out "<vault>/品牌/XX" --brand "XX" --alias "错写1"
python scripts/build_kb.py --src ./kb-src --target workbuddy --out ./kb --brand "XX"
python scripts/build_kb.py --src ./kb-src --target workbuddy --out ./kb --check-only
```

**尺寸提醒**：宽高须为 16 的倍数，`1080` 不满足。竖版用 `1024x1536` 或 `1088x1920`，3:4 用 `1088x1440`。

## 从这个版本改了什么

通用版从一份真实跑通的品牌社媒 skill 脱胎而来，主要做了三件事：

1. **去品牌化** —— 品牌名、品类、合规案例、平台账号全部抽成 `brand-profile.md` 里的配置项，方法论保留、专属结论剥离。
2. **工具链可插拔** —— 知识库落地（WorkBuddy 资料库/Obsidian/本地/钉钉/飞书/Notion）与生图后端（1XM/OpenAI/通义/即梦/任意兼容端点）成为配置，全部带降级路径，缺依赖不阻断流程。
3. **平台可换** —— 从写死"小红书/抖音/公众号"扩成 12 平台规格库 + 6 种组合预设，加上海外组（Instagram/TikTok/Facebook/LinkedIn/Shorts/X）。

保留了原版最有价值的部分：真实踩过的坑（网盘配额是组织共享、指数服务滞后数月、1080 不是 16 的倍数、
模型无法加载指定字体、指令语言与渲染语言必须分开）、强制模式选择的流程约束、成套海报的四项统一规范、
以及日文"本地化而非直译"的具体规则。

## 关于我们

我们是一支做中日跨境内容的团队。这个 skill 不是玩具，是我们自己每天在跑的流程 ——
把它开源，是因为"能跑通的方法论"比"好看的演示"更有说服力。

如果你的团队也想把 AI 真正用起来，我们提供两件事：

- **企业 AI 落地陪跑** —— 从流程诊断、工具选型到工作流搭建，陪你的团队把 AI 落到具体业务里，而不是停在"试了几个工具"
- **社媒代运营** —— 品牌社媒全流程托管，含面向日本市场的本地化内容生产

合作咨询：开 issue，或在 GitHub 上私信 [@kazuyakame-rgb](https://github.com/kazuyakame-rgb)。

## License

MIT —— 随便用、随便改、随便传。
