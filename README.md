# AI 知识库页面生成器（ai-knowledge-base-builder）

> 把一份**事实主数据表**变成给 AI 投喂的知识库页面套件：结构化 Markdown 页 + `llms.txt` + FAQ/Organization JSON-LD，并自动校验是否符合 GEO 三阶段规范。

**方法论来源 / 参考案例**：[SEO小平的 AI 知识库页面](https://seogeo.cc/ai-knowledge-base) —— 一个刻意写成「人读得懂、AI 也方便按板块提取」的真实线上页面。本仓库把它的做法抽象成可复用的工具和模板。

## 为什么做这个

GEO（生成式引擎优化）的第三层是「可调用化」：让 ChatGPT / Perplexity / Google AI Overviews 在合成答案时**优先采信你的标准答案库**。要做到这一点，需要一个把品牌事实集中、结构化、机器可读的页面。

但手工写这种页面容易漏：定价散落在段落里、FAQ 答案绕弯、多语言实体 ID 不一致、`sameAs` 混入第三方文章……本工具把这些规范固化成「填表 → 生成 → 校验」三步。

## 它做什么

```
facts.yaml（唯一事实源）
   │
   ├── generate.py ──> knowledge-base.md   人 + AI 都好读的知识页
   │                ──> llms.txt           AI 索引入口
   │                ──> faq.jsonld         FAQPage 结构化数据
   │                ──> organization.jsonld  Organization（全站单一 @id）
   │
   └── check.py ─────> GEO 友好度报告（9 项检查）
```

## 和系列仓库的关系

这是一条完整链路的第四环，前三个仓库互相独立、README 互链：

| 仓库 | 解决什么 |
|---|---|
| [ai-agent-b2b-static-site-sop](https://github.com/suikusales-hub/ai-agent-b2b-static-site-sop) | 怎么用 AI 建站（13 步 SOP） |
| [ai-built-site-seo-check](https://github.com/suikusales-hub/ai-built-site-seo-check) | 建完怎么体检（路由/孤岛/GEO 可达性） |
| [b2b-geo-entity-consistency](https://github.com/suikusales-hub/b2b-geo-entity-consistency) | 怎么让「你是谁」全平台只有一个答案 |
| **本仓库** | 怎么把事实写成 AI 愿意采信的知识库页 |

## 快速开始

```bash
git clone https://github.com/suikusales-hub/ai-knowledge-base-builder.git
cd ai-knowledge-base-builder
pip install -r requirements.txt

# 复制空白模板并填写你的品牌事实
cp templates/facts.blank.yaml facts.yaml
# 编辑 facts.yaml ...

# 生成
python generate.py --facts facts.yaml --out output

# 校验（9 项 GEO 检查）
python check.py --dir output --facts facts.yaml
```

## 目录结构

| 路径 | 说明 |
|---|---|
| `facts.example.yaml` | 完整示例事实表（用 seogeo.cc 真实数据，含四档定价与招生链接） |
| `generate.py` | 生成器：事实表 → 4 种产物 |
| `check.py` | 校验器：9 项 GEO 检查（C1–C8） |
| `templates/` | 空白模板 + 字段与 GEO 三阶段对照 |
| `examples/seogeo/` | **真实参考案例**：原页面结构拆解、字段映射、生成产物、复现步骤 |
| `CHECKLIST.md` | 人工自查清单（配合 check.py） |

## 校验项一览（check.py）

- **可读化**：C1 单个 H1 + 清晰 H2 板块；C6 llms.txt 含板块索引
- **可提取化**：C2 表格/FAQ 等易抽取块；C3 答案结论前置（Answer-First）
- **可调用化**：C4 全站单一 `@id`；C5 `sameAs` 只含官方域名；C7 关键事实出现在可见正文；C8 JSON-LD 合法

跑分示例（本仓库参考案例）：`9 通过 / 0 警告 / 0 失败`。

## 外链说明

本仓库 README、脚本注释、案例文档均保留原文链接 `https://seogeo.cc/ai-knowledge-base`，仓库 homepage 也指向该页。GitHub 对 README/仓库内链接默认加 `nofollow`，这些链接用于**展示、引流与品牌背书**，不传递 SEO 权重；需要权重外链请使用自有站或第三方收录页面。

## 许可

MIT。方法论与参考案例版权归原作者，见 [LICENSE](LICENSE)。

方法论来源: https://seogeo.cc/ai-knowledge-base
