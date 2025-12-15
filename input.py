#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
input.py - Expense entry module
- Add multiple expenses with date, amount, category (notes optional)
- Store data to a CSV file (default: expenses.csv)

Usage:
  python input.py
  python input.py --file expenses.csv
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Optional, List


CSV_HEADERS = ["date", "amount", "category", "notes"]


@dataclass
class Expense:
    date: str      # YYYY-MM-DD
    amount: str    # decimal string
    category: str
    notes: str = ""


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Expense entry (input module)")
    p.add_argument(
        "--file", "-f",
        default="expenses.csv",
        help="Path to CSV file used for storage (default: expenses.csv)"
    )
    return p.parse_args()


def normalize_date(s: str) -> str:
    """
    Accept:
      - YYYY-MM-DD
      - YYYY/MM/DD
      - today / 今日
    Return normalized YYYY-MM-DD.
    """
    s = s.strip()
    if not s:
        raise ValueError("日期不可空白")

    if s.lower() in {"today", "t"} or s in {"今日", "今天"}:
        return datetime.now().strftime("%Y-%m-%d")

    s2 = s.replace("/", "-")
    try:
        dt = datetime.strptime(s2, "%Y-%m-%d")
    except ValueError as e:
        raise ValueError("日期格式錯誤，請用 YYYY-MM-DD（例如 2025-12-15）") from e

    return dt.strftime("%Y-%m-%d")


def normalize_amount(s: str) -> str:
    """
    Amount must be positive decimal number.
    Return canonical decimal string.
    """
    s = s.strip()
    if not s:
        raise ValueError("金額不可空白")
    # allow comma separators
    s2 = s.replace(",", "")
    try:
        d = Decimal(s2)
    except InvalidOperation as e:
        raise ValueError("金額格式錯誤，請輸入數字（例如 120 或 120.5）") from e

    if d <= 0:
        raise ValueError("金額必須 > 0")

    # Normalize: remove trailing zeros nicely (but keep as string)
    # quantize is tricky; just use normalized formatting
    return format(d.normalize(), "f").rstrip("0").rstrip(".") if "." in format(d.normalize(), "f") else str(d)


def normalize_category(s: str) -> str:
    s = s.strip()
    if not s:
        raise ValueError("類別不可空白")
    # keep category as user input but trimmed
    return s


def ensure_csv_has_header(path: str) -> None:
    """
    If file doesn't exist or is empty, create it with header.
    """
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        parent = os.path.dirname(os.path.abspath(path))
        if parent and not os.path.exists(parent):
            os.makedirs(parent, exist_ok=True)

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()


def append_expense(path: str, exp: Expense) -> None:
    ensure_csv_has_header(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writerow(
            {
                "date": exp.date,
                "amount": exp.amount,
                "category": exp.category,
                "notes": exp.notes,
            }
        )


def read_last_n(path: str, n: int = 5) -> List[Expense]:
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return []
    rows: List[Expense] = []
    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # tolerate missing header by checking fieldnames
        if not reader.fieldnames or any(h not in reader.fieldnames for h in CSV_HEADERS):
            return []
        for r in reader:
            rows.append(
                Expense(
                    date=(r.get("date") or "").strip(),
                    amount=(r.get("amount") or "").strip(),
                    category=(r.get("category") or "").strip(),
                    notes=(r.get("notes") or "").strip(),
                )
            )
    return rows[-n:]


def prompt_nonempty(msg: str) -> str:
    while True:
        s = input(msg).strip()
        if s:
            return s
        print("不可空白，請重試。")


def prompt_optional(msg: str) -> str:
    return input(msg).strip()


def prompt_date() -> str:
    while True:
        s = input("日期（YYYY-MM-DD；可輸入 today/今日）: ").strip()
        try:
            return normalize_date(s)
        except ValueError as e:
            print(f"錯誤：{e}")


def prompt_amount() -> str:
    while True:
        s = input("金額（>0，可小數）: ").strip()
        try:
            return normalize_amount(s)
        except ValueError as e:
            print(f"錯誤：{e}")


def prompt_category() -> str:
    while True:
        s = input("類別（例如 餐飲/交通/娛樂/日用品）: ").strip()
        try:
            return normalize_category(s)
        except ValueError as e:
            print(f"錯誤：{e}")


def print_menu() -> None:
    print("\n==============================")
    print("Expense Tracker - Input Module")
    print("==============================")
    print("1) 新增一筆支出")
    print("2) 查看最近 5 筆")
    print("3) 離開")
    print("------------------------------")


def main() -> int:
    args = parse_args()
    csv_path = args.file

    print(f"資料儲存檔：{csv_path}")
    ensure_csv_has_header(csv_path)

    while True:
        print_menu()
        choice = input("請選擇操作 (1/2/3): ").strip()

        if choice == "1":
            date = prompt_date()
            amount = prompt_amount()
            category = prompt_category()
            notes = prompt_optional("備註（可留空）: ")

            exp = Expense(date=date, amount=amount, category=category, notes=notes)
            append_expense(csv_path, exp)
            print("已新增：", exp)

        elif choice == "2":
            last = read_last_n(csv_path, 5)
            if not last:
                print("目前沒有資料（或檔案格式不正確）。")
                continue

            print("\n最近 5 筆：")
            print("-" * 60)
            for i, e in enumerate(last, 1):
                notes_part = f" | notes: {e.notes}" if e.notes else ""
                print(f"{i}. {e.date} | {e.amount} | {e.category}{notes_part}")
            print("-" * 60)

        elif choice == "3":
            print("已離開。")
            return 0

        else:
            print("輸入無效，請輸入 1 / 2 / 3。")


if __name__ == "__main__":
    raise SystemExit(main())
