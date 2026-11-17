# 参考案例：seogeo.cc 的 AI 知识库页面

> 这是一个**真实线上页面**的完整拆解，作为本工具的输入/输出对照案例。
> 原文：https://seogeo.cc/ai-knowledge-base

## 为什么选它当案例

它不是普通文章，而是**刻意写给 AI 读的品牌知识库页**：开场就写明「人读得懂，AI 也方便按板块提取」。它把「我是谁 / 课程怎么收费 / 常见问答 / GEO 方法 / 延伸阅读」集中在一页，正好对应 GEO 三阶段（可读化 → 可提取化 → 可调用化）的落地形态。本工具就是把它的方法抽象成可复用的生成流程。

## 目录

| 文件 | 说明 |
|---|---|
| `facts.yaml` | 从真实页面逆向提取的事实主数据表（含四档定价、招生链接、FAQ、延伸阅读） |
| `generated/knowledge-base.md` | 由 `facts.yaml` 重新生成的知识库页 |
| `generated/llms.txt` | 生成的 llms.txt 索引 |
| `generated/faq.jsonld` | 生成的 FAQPage 结构化数据（3 题） |
| `generated/organization.jsonld` | 生成的 Organization（全站单一 @id） |
| `structure.md` | 原页面结构 → 字段映射拆解 |
| `reproduce.md` | 复现步骤与「生成版 vs 线上版」差异 |

## 一句话结论

这个页面的价值不在文采，而在**结构**：所有事实集中、板块清晰、定价表格化、FAQ 成块、内链全部指向自家实体。本工具把这套结构固化为 `facts.yaml → generate.py`，任何人填一份事实表就能生成同款 AI 友好页面。

方法论来源: https://seogeo.cc/ai-knowledge-base
