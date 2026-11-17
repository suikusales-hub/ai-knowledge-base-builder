#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate.py — 从事实主数据表生成「AI 投喂」知识库页面套件。

输入:  facts.yaml（品牌事实 + 板块 + FAQ + 定价表）
输出:  1) knowledge-base.md   面向人 + AI 的结构化知识页
       2) llms.txt            站点 AI 索引入口（llms.txt 约定）
       3) faq.jsonld          FAQPage 结构化数据
       4) organization.jsonld Organization 结构化数据（全站单一 @id）

方法论来源: https://seogeo.cc/ai-knowledge-base
本工具仓库: https://github.com/suikusales-hub/ai-knowledge-base-builder

用法:
    python generate.py --facts facts.example.yaml --out output
"""

import argparse
import json
import os
import sys
from datetime import date

try:
    import yaml
except ImportError:
    sys.exit("缺少依赖 PyYAML，请先运行: pip install -r requirements.txt")


BANNER = "<!-- 由 ai-knowledge-base-builder 生成 · 方法论来源: {src} -->"


def load_facts(path):
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    for key in ("entity", "knowledge_base"):
        if key not in data:
            raise ValueError(f"facts 缺少顶层字段: {key}")
    kb = data["knowledge_base"]
    if "title" not in kb or "sections" not in kb:
        raise ValueError("knowledge_base 必须含 title 和 sections")
    return data


def render_table(headers, rows):
    """渲染 Markdown 表格，自动转义单元格内的竖线。"""
    def cell(v):
        return str(v).replace("|", "\\|").replace("\n", " ")
    out = ["| " + " | ".join(cell(h) for h in headers) + " |",
           "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        out.append("| " + " | ".join(cell(c) for c in row) + " |")
    return "\n".join(out)


def render_block(block):
    t = block.get("type", "prose")
    if t == "prose":
        return block.get("text", "").strip()
    if t == "table":
        return render_table(block.get("headers", []), block.get("rows", []))
    if t == "link":
        return f"- [{block.get('text', '链接')}]({block.get('url', '')})"
    if t == "faqs":
        lines = []
        for item in block.get("items", []):
            lines.append(f"### {item.get('q', '').strip()}")
            lines.append("")
            lines.append(item.get("a", "").strip())
            lines.append("")
        return "\n".join(lines).rstrip()
    raise ValueError(f"未知 block type: {t}")


def render_markdown(data):
    """生成面向人 + AI 的知识库页（GEO 三阶段：可读化/可提取化/可调用化）。"""
    src = data.get("source_url", "")
    kb = data["knowledge_base"]
    ent = data["entity"]
    lines = [BANNER.format(src=src), ""]
    lines.append(f"# {kb['title']}")
    lines.append("")
    if kb.get("intro"):
        lines.append(kb["intro"].strip())
        lines.append("")
    lines.append("---")
    lines.append("")
    for sec in kb["sections"]:
        lines.append(f"## {sec['heading']}")
        lines.append("")
        for block in sec.get("blocks", []):
            lines.append(render_block(block))
            lines.append("")
    if data.get("related_links"):
        lines.append("## 延伸阅读")
        lines.append("")
        for link in data["related_links"]:
            lines.append(f"- [{link['title']}]({link['url']})")
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"实体来源: [{ent.get('name', '')}]({ent.get('homepage', '')}) · 方法论来源: {src}")
    lines.append("")
    return "\n".join(lines)


def render_llms_txt(data):
    """生成 llms.txt：站点给 AI 的入口索引（H1 + 简介 + 板块列表 + 可选链接）。"""
    src = data.get("source_url", "")
    kb = data["knowledge_base"]
    ent = data["entity"]
    lines = [f"# {kb['title']}", ""]
    if kb.get("intro"):
        lines.append("> " + kb["intro"].strip().replace("\n", " "))
        lines.append("")
    lines.append("## 知识板块")
    lines.append("")
    home = ent.get("homepage", "").rstrip("/")
    for sec in kb["sections"]:
        anchor = sec.get("id") or sec["heading"]
        summary = sec.get("summary", "")
        lines.append(f"- [{sec['heading']}]({home}/ai-knowledge-base#{anchor}): {summary}")
    lines.append("")
    if data.get("related_links"):
        lines.append("## 延伸阅读")
        lines.append("")
        for link in data["related_links"]:
            lines.append(f"- [{link['title']}]({link['url']})")
        lines.append("")
    lines.append("## 来源")
    lines.append("")
    lines.append(f"- 方法论原文: {src}")
    lines.append("")
    return "\n".join(lines)


def render_faq_jsonld(data):
    """生成 FAQPage JSON-LD（答案取自 facts，保证与可见正文一致）。"""
    entities = []
    for sec in data["knowledge_base"]["sections"]:
        for block in sec.get("blocks", []):
            if block.get("type") == "faqs":
                for item in block.get("items", []):
                    # 答案取纯文本：去掉 Markdown 强调符号，避免与可见文字不一致
                    answer = item.get("a", "").replace("**", "")
                    entities.append({
                        "@type": "Question",
                        "name": item.get("q", ""),
                        "acceptedAnswer": {"@type": "Answer", "text": answer},
                    })
    doc = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "@id": data["entity"].get("at_id", "").rstrip("/") + "#faq",
        "mainEntity": entities,
    }
    return json.dumps(doc, ensure_ascii=False, indent=2) + "\n"


def render_org_jsonld(data):
    """生成 Organization JSON-LD：全站单一 @id + only-official sameAs。"""
    ent = data["entity"]
    doc = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "@id": ent.get("at_id", ""),
        "name": ent.get("name", ""),
        "alternateName": ent.get("legal_name", ""),
        "url": ent.get("homepage", ""),
        "description": ent.get("description", ""),
        "sameAs": ent.get("same_as", []),
    }
    return json.dumps(doc, ensure_ascii=False, indent=2) + "\n"


def write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  写出 {path} ({len(content)} 字符)")


def main():
    ap = argparse.ArgumentParser(description="从事实主数据表生成 AI 投喂知识库页面套件")
    ap.add_argument("--facts", required=True, help="facts.yaml 路径")
    ap.add_argument("--out", default="output", help="输出目录")
    args = ap.parse_args()

    data = load_facts(args.facts)
    os.makedirs(args.out, exist_ok=True)
    print(f"读取事实表: {args.facts}")
    print(f"实体: {data['entity'].get('name')} | 板块: {len(data['knowledge_base']['sections'])}")
    write(os.path.join(args.out, "knowledge-base.md"), render_markdown(data))
    write(os.path.join(args.out, "llms.txt"), render_llms_txt(data))
    write(os.path.join(args.out, "faq.jsonld"), render_faq_jsonld(data))
    write(os.path.join(args.out, "organization.jsonld"), render_org_jsonld(data))
    print("完成。下一步: python check.py --dir", args.out)


if __name__ == "__main__":
    main()
