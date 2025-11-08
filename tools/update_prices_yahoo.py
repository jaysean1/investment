# tools/update_prices_yahoo.py
# 这个脚本用于从 Yahoo Finance 获取指定标的在指定日期的日线价格并更新 CSV；用于填充空白行或追加缺失日期。
# 本脚本不会覆盖已有的有效历史记录；它只会填充空白价格行或在文件末尾追加新日期。

import json
import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from urllib.request import urlopen, Request


YF_BASE = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=10d&includePrePost=false"

SYMBOLS = {
    "MSFT": "03_prices_all/MSFT_prices-Table 1.csv",
    "QQQ": "03_prices_all/QQQ_prices-Table 1.csv",
    "TSLA": "03_prices_all/TSLA_prices-Table 1.csv",
    "GLD": "03_prices_all/GLD_prices-Table 1.csv",
}

# 需要更新到的日期（含）
TARGET_DATES = ["2025-11-07", "2025-11-08"]


def fetch_daily_ohlcv(symbol: str) -> dict:
    """从 Yahoo Finance 抓取近 10 天的日线数据，并返回 {date: (o,h,l,c,vol)} 字典。
    - 日期为美东时区（America/New_York）下的 YYYY-MM-DD。
    """
    url = YF_BASE.format(symbol=symbol)
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=20) as resp:
        data = json.load(resp)

    result = data.get("chart", {}).get("result", [])
    if not result:
        raise RuntimeError(f"No chart data for {symbol}")
    r0 = result[0]
    ts_list = r0.get("timestamp", [])
    meta = r0.get("meta", {})
    tz_name = meta.get("timezone", "America/New_York")
    # 某些返回可能是缩写（如 EDT/EST），需要回退到具体地区名
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = ZoneInfo("America/New_York")
    quote = r0.get("indicators", {}).get("quote", [{}])[0]
    opens = quote.get("open", [])
    highs = quote.get("high", [])
    lows = quote.get("low", [])
    closes = quote.get("close", [])
    vols = quote.get("volume", [])

    out = {}
    for i, ts in enumerate(ts_list):
        # Yahoo 返回 UTC 秒时间戳；转换到美东得到交易日日期字符串
        dt = datetime.fromtimestamp(ts, tz=timezone.utc).astimezone(tz)
        date_str = dt.strftime("%Y-%m-%d")

        # 跳过缺失值（可能是 None）
        o = opens[i] if i < len(opens) else None
        h = highs[i] if i < len(highs) else None
        l = lows[i] if i < len(lows) else None
        c = closes[i] if i < len(closes) else None
        v = vols[i] if i < len(vols) else None
        if None in (o, h, l, c, v):
            continue

        out[date_str] = (float(o), float(h), float(l), float(c), int(v))
    return out


def format_price(x: float) -> str:
    # 统一保留两位小数，便于 CSV 一致性
    return f"{x:.2f}"


def update_csv(csv_path: str, records: dict) -> dict:
    """更新单个 CSV 文件：
    - 若存在形如 `YYYY-MM-DD,,,,,,,,` 的空白行，则用 records 填充
    - 若目标日期不存在，则在文件末尾追加
    返回 {date: action} 映射，action ∈ {"filled", "appended", "skipped"}
    """
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        raise

    # 建立索引：date -> (idx, cols)
    index = {}
    for i, raw in enumerate(lines):
        row = raw.strip("\n\r")
        if not row or row.startswith("Date,"):
            continue
        parts = row.split(",")
        if parts and len(parts) >= 1:
            index[parts[0]] = (i, parts)

    actions = {}

    for d in TARGET_DATES:
        if d not in records:
            actions[d] = "skipped"
            continue
        o, h, l, c, v = records[d]
        new_line = ",".join([
            d,
            format_price(o),
            format_price(h),
            format_price(l),
            format_price(c),
            str(v),
            "yahoo_api",
            "✅",
            "",
        ]) + "\n"

        if d in index:
            idx, cols = index[d]
            # 判断是否为空白占位（Open..Volume 为空）
            is_blank = False
            if len(cols) >= 6:
                is_blank = all(c == "" for c in cols[1:6])
            # 仅填充空白；已有有效数据则跳过
            if is_blank:
                lines[idx] = new_line
                actions[d] = "filled"
            else:
                actions[d] = "skipped"
        else:
            # 末尾追加
            # 确保文件最后一行有换行
            if lines and not lines[-1].endswith("\n"):
                lines[-1] = lines[-1] + "\n"
            lines.append(new_line)
            actions[d] = "appended"

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        f.writelines(lines)

    return actions


def main():
    summary = {}
    for sym, path in SYMBOLS.items():
        prices = fetch_daily_ohlcv(sym)
        actions = update_csv(path, prices)
        summary[sym] = actions

    # 输出简报
    for sym, acts in summary.items():
        print(sym, acts)


if __name__ == "__main__":
    main()
