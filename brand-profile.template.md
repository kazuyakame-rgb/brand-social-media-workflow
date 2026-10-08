# 品牌档案模板

复制为 `brand-profile.md` 放在工作目录（或知识库根目录）填写。**填一次，六个阶段全部复用** —— 不填的部分留空即可，agent 会在用到时单独问你，不要为了填满而编造。

> 填写原则：**只写真有的**。功效数据、认证、检测机构名必须来自手上的真实资料，不能凭印象。

---

## 1. 品牌基础

```yaml
brand_name:            # 中文品牌名
brand_name_ja:         # 日文市场写法（当地已注册的，没有就留空，Stage 6 会提醒你确认）
brand_name_en:         # 英文市场写法
brand_name_variants:   # 常见错写/别称，用于 SEO 与舆情监控，例：[XXX, XXX]
category:              # 品类词，例：家用美容仪 / 宠物清洁电器 / 功能性食品
category_words:        # 用户真实会搜的品类关键词（Stage 2 用），例：[超声美容仪, 家用提拉]
one_line_positioning:  # 一句话定位
```

## 2. 产品与技术

```yaml
products:              # 主推品列表：名称 / 一句话卖点 / 核心技术
core_tech:             # 核心技术名词（对外统一口径，不得自造）
usage:                 # 用法与频次
contraindications:     # 禁忌人群（合规必填，成稿必须带）
```

## 3. 视觉规范（Stage 5 直接用）

```yaml
palette:
  background:          # 背景色，例：暖钛灰渐变 #E8E6E1 → #F5F3EF
  product:             # 产品主色，例：暖香槟金（务必注明"勿偏银"这类易漂移点）
  title:               # 标题色
  accent:              # 点缀色
  forbidden:           # 禁用色，例：高饱和促销色
font:
  cn:                  # 中文字体，例：阿里巴巴普惠体 / 现代几何无衬线
  ja:                  # 日文字体，例：Yu Gothic
  en:                  # 英文无衬线
logo:
  file:                # logo 文件路径（浅底用 / 深底用两份）
  slot:                # 固定位置，例：左上角
  rule:                # 例：只出现一次，不改色不变形，中文副标可保留
visual_motif:          # 品牌专属视觉意象，例：水分子 / 声波 / 光粒子
style_keywords:        # 调性关键词，例：极简高级、科研循证、留白充足、柔和影棚光
```

## 4. 合规红线（Stage 4/5/6 硬闸门）

```yaml
allowed_claims:        # 允许的表述口径
forbidden_claims:      # 禁止的表述，例：治疗承诺、绝对化用语
data_usage_rule:       # 例：第三方检测机构名不得出现在商业广告语境
required_disclaimer:   # 例：实际效果因人而异
market_specific:
  jp:                  # 例：薬機法，避免治疗类/抗皱医疗宣称
  us:                  # 例：FTC，每项客观宣称需有依据
  eu:                  # 例：化妆品/器械法规，功效证据更严
```

## 5. 参考素材清单（Stage 5 用）

```yaml
assets:
  product_shots:       # 产品多角度图路径
  model_shots:         # 模特持产品图路径
  texture_shots:       # 细节/质地图
  source:              # 素材来源位置（本地目录 / 网盘链接 / 需下载的远程地址）
```

## 6. 竞品与差异化（Stage 2/3 用，可后补）

```yaml
competitors:           # 直接竞品（用当地市场惯用写法）
differentiators:       # 差异化点，每条注明依据文档
```

---

## 最小可用版

只有五分钟的话，至少填这四项，其余让 agent 从资料里提炼：

1. `brand_name` + `category`
2. `palette`（4 个色）与 `logo.file`
3. `forbidden_claims` + `required_disclaimer`
4. `assets` 里产品图的路径
