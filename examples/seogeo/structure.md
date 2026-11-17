# 原页面结构 → facts.yaml 字段映射

原文：https://seogeo.cc/ai-knowledge-base

## 拆解总览

真实页面从上到下是 5 个板块，全部被映射进本工具的数据模型：

| 线上页面板块 | 页面里的形态 | facts.yaml 对应字段 | GEO 阶段 |
|---|---|---|---|
| 标题 + 开场说明 | H1 + 一段导语 | `knowledge_base.title` / `intro` | 可读化 |
| 「是谁 / 全年陪跑课」 | H2 + 四档定价表 | `sections[who, course]` 的 `prose` / `table` / `link` | 可提取化 |
| 常见问题解答 | H3 问句 + 结论前置答案 | `sections[faq].blocks[faqs]` | 可提取化 |
| GEO 三阶段怎么做 | H2 + 三行对照表 | `sections[geo].blocks[table]` | 可提取化 |
| 延伸阅读 | 15+ 条站内链接 | `related_links` | 可读化 / 实体聚合 |

## 关键设计点（为什么这样写 AI 好提取）

### 1. 事实集中在一页，而不是散在 15 篇文章里
延伸阅读有 15+ 条链接，但「我是谁 / 我怎么收费 / 我的方法是什么」这些**核心事实**全部写在当前页。AI 抓这一页就能拿到完整答案，不用跨页拼凑。
→ 工具里对应：`entity` + `knowledge_base` 是单一数据源。

### 2. 定价用表格，不用段落
四档课程（¥9,999 / ¥13,000 / ¥15,000 / ¥17,000）用「方案 / 定价 / 月均 / 人群 / 权益」五列表格呈现。表格是模型抽取成本最低的结构。
→ 工具里对应：`blocks[].type: table`，生成 Markdown 表格 + 可被读取为结构化数据。

### 3. FAQ 答案第一句就是结论
例：「工厂不懂营销、只懂工艺，能学 GEO 吗？」→ 答案开头是「**能**，而且工厂往往更有别人抄不走的原料……」。不绕弯、不铺垫。
→ 工具里对应：`blocks[].type: faqs`，答案首句结论前置，`check.py` C3 会校验；同时导出 FAQPage JSON-LD。

### 4. 全站一个实体，延伸阅读只链自家
所有延伸阅读都指向 `seogeo.cc` 自家页面，强化实体聚合；没有混入无关的第三方站点。
→ 工具里对应：`related_links` + `entity.same_as` 只放官方域名，`check.py` C5 校验。

### 5. 抽象层：把「三阶段」写成模板方法
原页面把 GEO 拆成「可读化 / 可提取化 / 可调用化」，本工具直接把这三层做成校验项：

- 可读化 → C1（H1 唯一、H2 板块）、C6（llms.txt 索引）
- 可提取化 → C2（表格/FAQ 块）、C3（Answer-First）
- 可调用化 → C4（单一 @id）、C5（sameAs 官方）、C7（事实在正文）、C8（JSON-LD 合法）

## 复现

见 `reproduce.md`。原始事实数据在 `facts.yaml`，生成结果在 `generated/`。

方法论来源: https://seogeo.cc/ai-knowledge-base
