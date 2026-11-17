#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check.py — 校验「AI 投喂」知识库页是否符合 GEO 三阶段规范。

检查项（对应文章方法论）：
  可读化   C1 有 H1、有清晰的 H2 板块
  可提取化 C2 含表格/FAQ 等易抽取块；C3 FAQ 答案结论前置（Answer-First）
  可调用化 C4 Organization @id 全站单一且稳定；C5 sameAs 只含官方域名
            C6 llms.txt 存在且含板块索引；C7 事实（定价/名称）出现在可见正文
            C8 JSON-LD 可解析

方法论来源: https://seogeo.cc/ai-knowledge-base
用法:
    python check.py --dir output
    python check.py --dir output --facts facts.example.yaml
"""

import argparse
import json
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("缺少依赖 PyYAML，请先运行: pip install -r requirements.txt")


PASS, FAIL, WARN = "PASS", "FAIL", "WARN"
results = []


def record(code, status, msg):
    results.append((code, status, msg))
    mark = {PASS: "[OK]  ", FAIL: "[FAIL]", WARN: "[WARN]"}[status]
    print(f"{mark} {code} {msg}")


def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def check_markdown(md):
    h1 = re.findall(r"^# (.+)$", md, re.M)
    h2 = re.findall(r"^## (.+)$", md, re.M)
    if len(h1) == 1:
        record("C1a", PASS, f"H1 唯一: {h1[0][:40]}")
    else:
        record("C1a", FAIL if not h1 else WARN, f"H1 数量 = {len(h1)}（应为 1）")
    if len(h2) >= 3:
        record("C1b", PASS, f"板块 H2 共 {len(h2)} 个: {', '.join(h[:14] for h in h2[:5])}")
    else:
        record("C1b", WARN, f"板块 H2 仅 {len(h2)} 个，建议拆分成更多板块")

    tables = len(re.findall(r"^\|.*\|$", md, re.M))
    faq_heads = len(re.findall(r"^### .*\?$|^### .*？$", md, re.M))
    if tables >= 3 or faq_heads >= 1:
        record("C2", PASS, f"含易抽取块: 表格行 {tables} / FAQ 问 {faq_heads}")
    else:
        record("C2", WARN, "表格与 FAQ 块偏少，模型抽取成本高")

    # Answer-First：答案段首句不应以「首先/其实/众所周知」等拖沓词开头
    delay_words = ("首先", "其实", "众所周知", "这个问题", "那么", "well", "actually")
    answers = re.findall(r"^### ([^\n]*[?？])\n+([^\n]+)", md, re.M)
    bad = []
    for q, a in answers:
        first = a.strip().lstrip("*#>- ").split("。")[0][:30]
        if any(first.startswith(w) for w in delay_words):
            bad.append(q[:24])
    if answers and not bad:
        record("C3", PASS, f"{len(answers)} 条 FAQ 均结论前置（Answer-First）")
    elif bad:
        record("C3", WARN, f"{len(bad)} 条 FAQ 答案未结论前置: {', '.join(bad)}")
    else:
        record("C3", WARN, "未识别到 FAQ 问答块")
    return md


def check_llms(llms):
    if not llms.strip().startswith("# "):
        record("C6", FAIL, "llms.txt 缺少 H1 开头")
        return
    has_index = "## 知识板块" in llms or "## Sections" in llms
    links = len(re.findall(r"^- \[.+\]\(.+\)", llms, re.M))
    if has_index and links >= 2:
        record("C6", PASS, f"llms.txt 合规: 板块索引 + {links} 条链接")
    else:
        record("C6", FAIL, "llms.txt 缺少板块索引或链接列表")


def check_jsonld(dirpath):
    org_path = os.path.join(dirpath, "organization.jsonld")
    faq_path = os.path.join(dirpath, "faq.jsonld")
    if os.path.exists(org_path):
        try:
            org = json.loads(read(org_path))
            at_id = org.get("@id", "")
            if at_id:
                record("C4", PASS, f"Organization @id = {at_id}")
            else:
                record("C4", FAIL, "Organization 缺少 @id")
            same_as = org.get("sameAs", [])
            official = org.get("url", "")
            domain = re.sub(r"^https?://(www\.)?", "", official).split("/")[0]
            mixed = [s for s in same_as if domain and domain not in s]
            if not mixed:
                record("C5", PASS, f"sameAs 全部为官方域名 ({domain})，共 {len(same_as)} 条")
            else:
                record("C5", WARN, f"sameAs 含非官方域名 {len(mixed)} 条: {mixed[:2]}")
        except json.JSONDecodeError as e:
            record("C8", FAIL, f"organization.jsonld 解析失败: {e}")
    else:
        record("C4", WARN, "未找到 organization.jsonld，跳过 @id 检查")

    if os.path.exists(faq_path):
        try:
            faq = json.loads(read(faq_path))
            n = len(faq.get("mainEntity", []))
            record("C8", PASS, f"FAQ JSON-LD 合法，含 {n} 个 Question")
        except json.JSONDecodeError as e:
            record("C8", FAIL, f"faq.jsonld 解析失败: {e}")
    else:
        record("C8", WARN, "未找到 faq.jsonld")


def check_facts_in_body(md, facts_path):
    with open(facts_path, "r", encoding="utf-8") as f:
        facts = yaml.safe_load(f)
    ent = facts.get("entity", {})
    missing = []
    for key in ("name", "legal_name"):
        v = ent.get(key)
        if v and v not in md:
            missing.append(f"{key}={v}")
    # 定价数字：从 facts 的表格中抽取金额，核对是否出现在正文
    amounts = set()
    for sec in facts.get("knowledge_base", {}).get("sections", []):
        for block in sec.get("blocks", []):
            if block.get("type") == "table":
                for row in block.get("rows", []):
                    for cell in row:
                        for m in re.findall(r"¥[\d,]+", str(cell)):
                            amounts.add(m)
    for a in amounts:
        if a not in md:
            missing.append(f"定价 {a}")
    if not missing:
        record("C7", PASS, f"关键事实均出现在可见正文（{len(amounts)} 个金额 + 实体名）")
    else:
        record("C7", WARN, f"以下事实未在正文出现: {', '.join(missing)}")


def main():
    ap = argparse.ArgumentParser(description="校验 AI 投喂知识库页的 GEO 友好度")
    ap.add_argument("--dir", default="output", help="生成产物目录")
    ap.add_argument("--facts", help="可选：原始 facts.yaml，用于核对事实是否出现在正文")
    args = ap.parse_args()

    print(f"校验目录: {args.dir}\n")
    md_path = os.path.join(args.dir, "knowledge-base.md")
    llms_path = os.path.join(args.dir, "llms.txt")
    if not os.path.exists(md_path):
        sys.exit(f"未找到 {md_path}，请先运行 generate.py")

    check_markdown(read(md_path))
    if os.path.exists(llms_path):
        check_llms(read(llms_path))
    else:
        record("C6", FAIL, "缺少 llms.txt")
    check_jsonld(args.dir)
    if args.facts:
        check_facts_in_body(read(md_path), args.facts)

    fails = sum(1 for _, s, _ in results if s == FAIL)
    warns = sum(1 for _, s, _ in results if s == WARN)
    passes = sum(1 for _, s, _ in results if s == PASS)
    print(f"\n汇总: {passes} 通过 / {warns} 警告 / {fails} 失败")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
