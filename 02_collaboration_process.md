# 🟩 02_collaboration_process.md  
**协作与执行流程（Xinyi’s Execution Protocol + 数据验证）**

---

## 1️⃣ 执行核心逻辑
- 所有决策在盘前完成；  
- 不进行盘中监控；  
- 所有调整通过预挂单实现（含防御挂单 / 突破挂单）。  

---

## 2️⃣ 执行阶段结构（新版命名）

| 阶段 | 输入 | 过程 | 输出 |
|:--|:--|:--|:--|
| **盘前输入** | 四个截图（MSFT/QQQ/TSLA/GLD） | 提取价格数据 | **写入 `03_prices_all.xlsx` 对应页签** |
| **验证阶段** | Yahoo Finance 对照验证 | 偏差 < ±0.5% → 标记 ✅ | 记录于 **`05_transactions_all.xlsx / Data_Update_Log`** |
| **分析生成** | 结合历史仓位与价格区间 | 自动生成挂单区间 | 追加入 `04_order_log.md` |
| **结果记录** | 若次日成交 | 更新 **`05_transactions_all.xlsx / Transactions`** | 触发 `06_holdings_all.xlsx / Holdings_Snapshot` 刷新 |
| **持仓汇总** | 当日收盘后 | 输出当日汇总 | `06_holdings_all.xlsx / Holdings_Summary` |

---

## 3️⃣ 数据记录链（更新）

```mermaid
graph TD
A[盘前截图输入] --> B[Yahoo Finance 验证]
B --> C[03_prices_all.xlsx (MSFT/QQQ/TSLA/GLD 四页签) 更新]
C --> D[04_order_log.md 生成/更新]
D --> E[若成交 → 05_transactions_all.xlsx / Transactions]
E --> F[05_transactions_all.xlsx / Data_Update_Log 更新]
F --> G[06_holdings_all.xlsx / Holdings_Snapshot 刷新]
G --> H[06_holdings_all.xlsx / Holdings_Summary 刷新]
```

---

## 4️⃣ 命名与替换规范（统一）

- **价格库**：`03_prices_all.xlsx`（页签：`MSFT_prices / QQQ_prices / TSLA_prices / GLD_prices`）  
- **挂单日志**：`04_order_log.md`  
- **成交与验证**：`05_transactions_all.xlsx`（页签：`Transactions / Data_Update_Log`）  
- **持仓库**：`06_holdings_all.xlsx`（页签：`Holdings_Snapshot / Holdings_Summary`）  
- **文件命名**：保持 00–06 统一编号，不带 `_updated`、`_final` 等后缀。
