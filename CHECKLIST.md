# AI 知识库页面 · 人工自查清单

配合 `check.py` 使用。脚本查结构，这份清单查内容与策略。
方法论来源：https://seogeo.cc/ai-knowledge-base

## 一、可读化（让爬虫和模型先读到）

- [ ] 全页只有 **1 个 H1**，且包含品牌名 + 主题
- [ ] 用 H2 切成清晰板块（是谁 / 参数 / FAQ / 方法 / 延伸阅读）
- [ ] 开头 100 字内说清「这页是给谁看的、覆盖什么」
- [ ] 有 `llms.txt`，列出每个板块的一句话摘要和锚点
- [ ] 内链指向自家官方页面，形成实体聚合，不链无关第三方

## 二、可提取化（降低模型抽取成本）

- [ ] 定价、参数、规格用**表格**，不用长段落
- [ ] FAQ 用「问句 H3 + 答案」成块，不散落在正文里
- [ ] 每条 FAQ 答案**第一句就是结论**，不以「首先/其实/众所周知」开头
- [ ] 事实用具体数字和专名，不用「很多/大概/业界领先」这类空话
- [ ] 关键结论在正文可见处写出（不能只藏在图片或 JS 里）

## 三、可调用化（让 AI 复述时不跑偏）

- [ ] `entity.name` / `legal_name` / `description` 与官网、工商、平台资料一致
- [ ] `entity.at_id` 全站唯一且稳定，多语言版本共用同一个（不带语言后缀）
- [ ] `sameAs` 只放**官方**账号和官方页面，不混入第三方文章
- [ ] 导出 `organization.jsonld` 和 `faq.jsonld`，且 JSON-LD 里的事实与可见正文一致
- [ ] 用 `python check.py --dir output --facts facts.yaml` 跑一遍，全部 PASS

## 四、发布后验证

- [ ] 把 `llms.txt` 放到站点根目录（`https://your-domain.com/llms.txt`）
- [ ] Google Search Console / Bing 提交该页，确认被抓取
- [ ] 用 ChatGPT / Perplexity 问一个 FAQ 里的问题，看是否引用你的答案
- [ ] 检查抓取工具（关 JS）下正文是否仍在（可配合 ai-built-site-seo-check 的 `geo_check.py`）

## 一键命令

```bash
python generate.py --facts facts.yaml --out output
python check.py --dir output --facts facts.yaml
```

方法论来源: https://seogeo.cc/ai-knowledge-base
