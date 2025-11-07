# 📁 MSFT + QQQ + TSLA + GLD 投资项目结构说明（2025 统一版）

本项目用于跟踪和记录风险盘操作，包括：
- 日常盘前价格数据（来自截图与 Yahoo Finance 验证）
- 每日挂单与操作逻辑日志
- 成交流水与数据验证记录
- 实际持仓快照与汇总
- 协作与执行流程

---

## 📑 文件结构（当前版本）

| 文件名 | 类型 | 说明 |
|:--|:--|:--|
| **README.md** | Markdown | 项目说明与结构索引 |
| **CLAUDE.md** | Markdown | Claude Code 工作指南（代码库架构与操作说明） |
| **update_prices.py** | Python | 自动从 Yahoo Finance 获取价格数据并更新 CSV 文件 |
| **01_investment_objectives.md** | Markdown | 投资目标与战略：定义长期目标、资产定位、仓位框架 |
| **02_collaboration_process.md** | Markdown | 协作与执行流程：盘前输入 → 验证 → 挂单 → 成交 → 持仓 |
| **03_prices_all/** | CSV 文件夹 | **统一价格库**：四个 CSV 文件 `MSFT_prices-Table 1.csv / QQQ_prices-Table 1.csv / TSLA_prices-Table 1.csv / GLD_prices-Table 1.csv`<br>**新格式**：`Date, Open, High, Low, Close, Volume, Pre_Market_Price, Screenshot_Source, Verified_Yahoo, Notes` |
| **04_order_log.md** | Markdown | **盘前挂单与判断**（策略区间、理据、分层，倒序排列） |
| **05_transactions_all.csv** | CSV | **成交流水**：日期、操作类型、标的、数量、价格、金额、理由、风险盘余额、累计转回安全盘 |
| **06_holdings_all.csv** | CSV | **持仓汇总**：标的、当前持股数、买入加权平均成本、持仓成本合计 |

> 当前实现：
> - 价格数据使用 **CSV 格式**存储于 `03_prices_all/` 文件夹，每个标的一个独立文件
> - **新增 `Pre_Market_Price` 列**：支持晚上输入盘前价格，次日自动更新实际市场数据
> - 成交与持仓数据使用 **CSV 格式**（`05_transactions_all.csv` 和 `06_holdings_all.csv`）
> - 所有 CSV 文件包含验证状态字段（Yahoo Finance 对照）
> - **自动化脚本 `update_prices.py`**：自动从 Yahoo Finance 获取数据并验证

---

## 🔁 文件关系逻辑图

```
[01_investment_objectives.md] ──→ 战略指导
[02_collaboration_process.md] ──→ 协作与执行路径
         ↓
[03_prices_all/] ───────────────→ 盘前价格源（4 个 CSV 文件）
         ↓
[04_order_log.md] ──────────────→ 盘前策略与挂单
         ↓
[05_transactions_all.csv] ──────→ 成交流水记录
         ↓
[06_holdings_all.csv] ──────────→ 持仓汇总
```

---

## 🧠 协作说明（操作与更新）

### 每日工作流程（悉尼时间）

**晚上（盘前准备）：**
- **盘前输入**：用户提供次日盘前价格（MSFT/QQQ/TSLA/GLD）
- **记录盘前价格**：写入 `Pre_Market_Price` 列，OHLC 留空，设置 `Verified_Yahoo` 为 "pending"
- **生成初步挂单**：根据盘前价格生成分层挂单 → 追加到 `04_order_log.md`（倒序）

**次日（收盘后）：**
- **自动更新**：运行 `python3 update_prices.py` 从 Yahoo Finance 获取实际市场数据
- **填充数据**：脚本自动填充 OHLC 数据，保留 `Pre_Market_Price` 作对比
- **自动验证**：偏差 < ±0.5% → 自动更新 `Verified_Yahoo` 为 "✅"
- **对比分析**：查看盘前价格与实际收盘价的差异

**成交记录：**
- **成交**：若挂单执行 → 记录于 `05_transactions_all.csv`（包含理由与风险盘余额）
- **持仓**：根据成交流水 → 重新计算加权平均成本 → 更新 `06_holdings_all.csv`

**定期检查：**
- **周度验证**：检查所有 CSV 文件的 Yahoo Finance 验证状态
