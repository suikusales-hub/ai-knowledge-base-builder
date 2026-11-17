# 复现步骤与生成版说明

原文：https://seogeo.cc/ai-knowledge-base

## 用本工具重新生成这个案例

```bash
cd ai-knowledge-base-builder
python generate.py --facts examples/seogeo/facts.yaml --out /tmp/repro
python check.py --dir /tmp/repro --facts examples/seogeo/facts.yaml
```

预期：9 项检查全部 PASS，产物与 `examples/seogeo/generated/` 一致。

## generated/ 里的文件是怎么来的

`generated/` 下的四个文件是**真跑出来的**，不是手写：

```bash
python generate.py --facts examples/seogeo/facts.yaml --out examples/seogeo/generated
```

| 产物 | 来源字段 | 与线上页面的关系 |
|---|---|---|
| `knowledge-base.md` | `title/intro/sections/related_links` | 等价物：线上页面正文的重建版 |
| `llms.txt` | `sections[].id/summary` + `related_links` | 线上页面没有；这是工具补充的 AI 索引入口 |
| `faq.jsonld` | `sections[faq].blocks[faqs]` | 线上页面若已内嵌 FAQ schema，应与本文件一致 |
| `organization.jsonld` | `entity` | 线上页面的 Organization schema 应与此一致（单一 @id） |

## 生成版 vs 线上版的差异（如实说明）

1. **生成版是「提取—重建」，不是逐字复刻。** `facts.yaml` 从线上页面逆向提取核心事实，生成器按模板重建，措辞可能比原文更规整。
2. **FAQ 选了 3 条代表题。** 线上页面 FAQ 可能更多；案例里放了 3 条能体现「结论前置」写法的代表题。
3. **llms.txt / JSON-LD 是工具增量产物。** 线上页面未必原样提供这些文件——这正体现了「把人工好页面升级成机器可读套件」的价值。
4. **定价与招生信息按原文保留。** 案例包含真实四档报价与招生链接，因为原页面本就公开（用户选择保留）。

## 校验这个案例

```bash
python check.py --dir examples/seogeo/generated --facts examples/seogeo/facts.yaml
```

方法论来源: https://seogeo.cc/ai-knowledge-base
