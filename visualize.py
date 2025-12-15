# visualize.py
# Pretty donut pie chart with icons (B同學)

from __future__ import annotations
import argparse, csv, os
from collections import defaultdict
import matplotlib as mpl
import matplotlib.pyplot as plt

# Emoji icons (customize as you like)
ICON_MAP = {
    "food": "🍔",
    "transport": "🚗",
    "rent": "🏠",
    "shopping": "🛍️",
    "entertainment": "🎮",
    "study": "📚",
    "medical": "🩺",
    "utilities": "💡",
    "coffee": "☕",
    "other": "🧾",
}

def iconize(cat: str) -> str:
    key = (cat or "").strip().lower()
    icon = ICON_MAP.get(key, "")
    return f"{icon} {cat}" if icon else cat

def parse_amount(raw: str) -> float:
    s = (raw or "").strip().replace(",", "")
    if not s:
        raise ValueError("amount is empty")
    return float(s)

def read_csv_totals(path: str) -> dict[str, float]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Input not found: {path}")

    totals = defaultdict(float)
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        if not r.fieldnames:
            raise ValueError("CSV has no header row.")
        cols = {c.lower().strip(): c for c in r.fieldnames}
        if "category" not in cols or "amount" not in cols:
            raise ValueError(f"CSV must contain 'category' and 'amount'. Found: {r.fieldnames}")

        cat_col, amt_col = cols["category"], cols["amount"]
        for i, row in enumerate(r, start=2):
            cat = (row.get(cat_col) or "").strip()
            if not cat:
                continue
            amt = parse_amount(row.get(amt_col))
            totals[cat] += amt

    totals = {k: v for k, v in totals.items() if abs(v) > 1e-12}
    if not totals:
        raise ValueError("No valid expense data found.")
    return totals

def group_small(totals: dict[str, float], min_ratio: float = 0.03, other_name: str = "Other") -> dict[str, float]:
    total = sum(totals.values())
    if total == 0:
        return totals

    big = {}
    other_sum = 0.0
    for k, v in sorted(totals.items(), key=lambda x: x[1], reverse=True):
        if abs(v) / abs(total) < min_ratio:
            other_sum += v
        else:
            big[k] = v
    if abs(other_sum) > 1e-12:
        big[other_name] = big.get(other_name, 0.0) + other_sum
    return big

def make_pretty_donut(totals: dict[str, float], title: str, output: str, show: bool, min_ratio: float):
    # Better emoji support on Windows
    mpl.rcParams["font.family"] = ["Segoe UI Emoji", "Segoe UI", "DejaVu Sans"]

    totals = group_small(totals, min_ratio=min_ratio, other_name="Other")

    items = sorted(totals.items(), key=lambda x: x[1], reverse=True)
    labels_raw = [k for k, _ in items]
    labels = [iconize(k) for k, _ in items]
    values = [v for _, v in items]
    total = sum(values)

    def autopct(pct: float) -> str:
        if pct < 4:      # 太小就不塞字，畫面乾淨
            return ""
        amt = pct / 100.0 * total
        return f"{pct:.1f}%\n{amt:,.0f}"

    fig = plt.figure(figsize=(11, 6.2), dpi=180)  # 版面偏寬，legend 放右側很好看
    ax = plt.gca()

    wedges, _, autotexts = ax.pie(
        values,
        labels=None,                 # label 放 legend，圓上不要太擠
        startangle=90,
        counterclock=False,
        autopct=autopct,
        pctdistance=0.78,
        wedgeprops={"linewidth": 1.2, "edgecolor": "white"},
        textprops={"fontsize": 10},
    )

    # Donut hole
    centre = plt.Circle((0, 0), 0.55, fc="white")
    ax.add_artist(centre)

    # 中央顯示總支出
    ax.text(0, 0.03, "Total", ha="center", va="center", fontsize=11)
    ax.text(0, -0.08, f"{total:,.0f}", ha="center", va="center", fontsize=16, fontweight="bold")

    # 右側 legend：分類 + 金額 + 百分比
    legend_lines = []
    for cat, val in zip(labels_raw, values):
        pct = (val / total * 100) if total else 0
        legend_lines.append(f"{iconize(cat)}  —  {val:,.0f}  ({pct:.1f}%)")

    ax.legend(
        wedges,
        legend_lines,
        title="Categories",
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        frameon=False,
        fontsize=10,
        title_fontsize=11,
    )

    ax.set_title(title, fontsize=16, pad=12)
    ax.axis("equal")

    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    plt.tight_layout()
    plt.savefig(output, bbox_inches="tight")
    print(f"[OK] Saved: {output}")

    if show:
        plt.show()
    plt.close()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", "-i", required=True, help="CSV path (needs columns: category, amount)")
    ap.add_argument("--output", "-o", default="output/pie.png", help="Output image path")
    ap.add_argument("--title", default="Spending by Category")
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--min-ratio", type=float, default=0.03, help="Group tiny slices into Other (e.g. 0.03 = 3%)")
    args = ap.parse_args()

    totals = read_csv_totals(args.input)
    make_pretty_donut(totals, args.title, args.output, args.show, args.min_ratio)

if __name__ == "__main__":
    main()
