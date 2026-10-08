#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
知识库预处理：把 00-05 编号的模块文档，按落地目标转成对应格式。
纯标准库实现，无需 pip install。

用法:
  python build_kb.py --src ./kb-src --target obsidian  --out "<vault>/品牌/XX" --brand "XX" --alias "错写1"
  python build_kb.py --src ./kb-src --target workbuddy --out ./kb
  python build_kb.py --src ./kb-src --target local     --out ./kb
  python build_kb.py --src ./kb-src --target workbuddy --out ./kb --check-only   # 只体检不输出

各目标做了什么:
  obsidian  : 加 YAML frontmatter（title / aliases / tags / created）
              把正文里对其他文档的纯文本引用转成 [[双链]]
  workbuddy : 保证纯 Markdown —— 剥掉 frontmatter；组件标签由体检拦截报错（不静默改写内容）
              额外生成 _manifest.json（按编号排序 + 文件夹名，供 create_folder + create_doc 逐个建节点）
  local     : 原样复制

体检项（--check-only 或每次构建都会跑）:
  - workbuddy: 正文不得含 WorkBuddy 组件标签（Paragraph/Callout/Table/Mermaid 等），会被 create_doc.py 拒绝
  - obsidian : 正文不得含 {{ }}，会撞 Obsidian 模板语法
  - 通用      : 必须有 00 总览；编号不得断档或重复
"""
import os, re, sys, json, shutil, argparse, datetime

COMPONENT_TAGS = ["Paragraph", "Callout", "Table", "Mermaid", "Heading", "BulletList",
                  "OrderedList", "Quote", "Divider", "Code", "TodoList", "Image"]
TITLE_RE = re.compile(r"^\s*(\d{2})\s*[-_ ]\s*(.+?)\s*$")


def read_docs(src):
    """按编号读取 src 下的 .md，返回 [(num, title, body)]。"""
    docs = []
    for fn in sorted(os.listdir(src)):
        if not fn.lower().endswith(".md"):
            continue
        m = TITLE_RE.match(os.path.splitext(fn)[0])
        title = os.path.splitext(fn)[0]
        num = m.group(1) if m else "99"
        with open(os.path.join(src, fn), encoding="utf-8") as f:
            docs.append((num, title, f.read()))
    docs.sort(key=lambda d: (d[0], d[1]))
    return docs


def split_frontmatter(body):
    """返回 (frontmatter_dict, 正文)。没有 frontmatter 则返回 ({}, 原文)。"""
    if not body.startswith("---"):
        return {}, body
    end = body.find("\n---", 3)
    if end == -1:
        return {}, body
    head, rest = body[3:end], body[end + 4:]
    fm = {}
    for line in head.splitlines():
        if ":" in line and not line.strip().startswith("-"):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip("[]").strip()
    return fm, rest.lstrip("\n")


def build_obsidian(docs, brand, tags, aliases, out):
    today = datetime.date.today().isoformat()
    titles = [t for _, t, _ in docs]
    all_alias = [brand] + list(aliases) if brand else list(aliases)
    made = []

    for num, title, body in docs:
        fm, text = split_frontmatter(body)

        # 纯文本引用 → [[双链]]（跳过已在双链里的）
        for other in titles:
            if other == title:
                continue
            text = re.sub(r"(?<!\[\[)(?<!\[)" + re.escape(other) + r"(?!\]\])",
                          f"[[{other}]]", text)
        text = re.sub(r"\[\[\[\[(.+?)\]\]\]\]", r"[[\1]]", text)  # 防重复包裹

        lines = ["---", f"title: {title}"]
        if all_alias:
            lines.append("aliases: [" + ", ".join(all_alias) + "]")
        tag_list = list(tags) + ([f"品牌/{brand}"] if brand else [])
        if tag_list:
            lines.append("tags:")
            lines += [f"  - {t}" for t in tag_list]
        lines += [f"created: {today}", "---", ""]
        content = "\n".join(lines) + text
        _write(os.path.join(out, title + ".md"), content)
        made.append(title)
    return made


def build_workbuddy(docs, out, folder_title):
    """纯 Markdown：剥 frontmatter。输出 _manifest.json。"""
    made = []
    for num, title, body in docs:
        _, text = split_frontmatter(body)
        _write(os.path.join(out, title + ".md"), text.strip() + "\n")
        made.append(title)

    manifest = {"folder_title": folder_title,
                "docs": [{"title": t, "file": t + ".md"} for t in made]}
    _write(os.path.join(out, "_manifest.json"),
           json.dumps(manifest, ensure_ascii=False, indent=2))
    return made


def build_local(docs, out):
    made = []
    for num, title, body in docs:
        _write(os.path.join(out, title + ".md"), body)
        made.append(title)
    return made


def _write(path, content):
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def check(docs, target):
    """返回 [(级别, 问题)]；ERROR 会中断构建。"""
    issues = []
    nums = [n for n, _, _ in docs]
    if not any(n == "00" for n in nums):
        issues.append(("WARN", "缺少 00 总览（后续阶段的文档索引会无处挂载）"))
    if len(set(nums)) != len(nums):
        issues.append(("WARN", "存在重复编号，落地顺序可能错乱"))
    for n, t, b in docs:
        if target == "workbuddy":
            hit = [c for c in COMPONENT_TAGS if re.search(rf"</?{c}[^>]*>", b)]
            if hit:
                issues.append(("ERROR", f"{t}: 含 WorkBuddy 组件标签 {hit}，create_doc.py 会拒绝提交"))
        if target == "obsidian" and "{{" in b:
            issues.append(("ERROR", f"{t}: 含 {{{{ }}}}，会撞 Obsidian 模板语法"))
        if not b.strip():
            issues.append(("WARN", f"{t}: 正文为空"))
    return issues


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--src", required=True, help="源目录（含 00-05 编号的 .md）")
    ap.add_argument("--target", required=True,
                    choices=["obsidian", "workbuddy", "local"])
    ap.add_argument("--out", required=True, help="输出目录")
    ap.add_argument("--brand", default="", help="品牌名（写进 tags/aliases/文件夹名）")
    ap.add_argument("--tag", action="append", default=[], help="额外标签，可重复")
    ap.add_argument("--alias", action="append", default=[], help="别名/错写变体，可重复")
    ap.add_argument("--folder-title", default="",
                    help="WorkBuddy 知识库文件夹名；留空则用 '<品牌名>知识库'")
    ap.add_argument("--check-only", action="store_true", help="只体检不输出")
    a = ap.parse_args()

    if not os.path.isdir(a.src):
        sys.exit(f"源目录不存在: {a.src}")
    docs = read_docs(a.src)
    if not docs:
        sys.exit(f"源目录下没有 .md 文件: {a.src}")

    print(f"读取 {len(docs)} 篇：")
    for n, t, _ in docs:
        print(f"  [{n}] {t}")

    issues = check(docs, a.target)
    for lvl, msg in issues:
        print(f"{lvl}: {msg}")
    if any(l == "ERROR" for l, _ in issues):
        sys.exit("体检未通过，已中止（先修上面的 ERROR）")
    if a.check_only:
        print("体检通过。")
        return 0

    if os.path.exists(a.out) and os.path.isdir(a.out) and os.listdir(a.out):
        print(f"注意：输出目录非空，将覆盖同名文件 -> {a.out}")

    if a.target == "obsidian":
        made = build_obsidian(docs, a.brand, a.tag or ["品牌知识库"], a.alias, a.out)
    elif a.target == "workbuddy":
        folder = a.folder_title or (f"{a.brand}知识库" if a.brand else "品牌知识库")
        made = build_workbuddy(docs, a.out, folder)
    else:
        made = build_local(docs, a.out)

    # 原始资料一并带走
    raw_src = os.path.join(a.src, "raw")
    if os.path.isdir(raw_src):
        shutil.copytree(raw_src, os.path.join(a.out, "raw"), dirs_exist_ok=True)
        print("原始资料: raw/ 已复制")

    print(f"\n已生成 {len(made)} 篇 -> {a.out}")
    if a.target == "workbuddy":
        print("下一步：create_folder 建目录 → 按 _manifest.json 顺序 create_doc（--parent-id 挂进去）")
    elif a.target == "obsidian":
        print("下一步：在 Obsidian 打开该目录；aliases 里已含品牌名错写变体，搜错写也能命中")
    return 0


if __name__ == "__main__":
    sys.exit(main())
