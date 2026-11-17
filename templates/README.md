# 模板目录 / Templates

## 快速开始

```bash
cp templates/facts.blank.yaml facts.yaml
# 编辑 facts.yaml，填入你的品牌事实
python generate.py --facts facts.yaml --out output
python check.py --dir output --facts facts.yaml
```

## 文件说明

- `facts.blank.yaml` —— 空白事实主数据表骨架。这是你唯一需要手工填的文件。

## 字段与 GEO 三阶段的对应

| 字段 | 对应阶段 | 作用 |
|---|---|---|
| `entity.name` / `legal_name` / `description` | 可调用化 | 稳定品牌事实，AI 复述不漂移 |
| `entity.at_id` | 可调用化 | 全站单一实体 ID，所有语言共用 |
| `entity.same_as` | 可调用化 | 只放官方账号，帮 AI 消歧 |
| `knowledge_base.title` / `intro` | 可读化 | 单个 H1 + 开局结论 |
| `sections[].heading` / `summary` | 可读化 | 清晰 H2 板块 + llms.txt 索引 |
| `blocks[].type: table` | 可提取化 | 参数/定价表格化，降低抽取成本 |
| `blocks[].type: faqs` | 可提取化 | FAQ 成块，答案结论前置，导出 JSON-LD |
| `related_links` | 可读化 | 官方内链网，利于抓取与实体聚合 |

## 填写规则

1. **一个页面只讲一个实体**：`entity` 是唯一数据源，别在正文里写与之冲突的事实。
2. **价格/参数用 table**，不要用长段落——表格是模型最容易抽取的结构。
3. **FAQ 答案第一句就给结论**，`check.py` 的 C3 会检查是否以拖沓词开头。
4. **sameAs 只放官方域名**，混进第三方文章会让实体消歧失败（C5 会告警）。
5. **@id 全站唯一且稳定**，不要带 `?lang=` 或语言后缀，多语言版本共用一个。

方法论来源: https://seogeo.cc/ai-knowledge-base
