\# 作業二：支出紀錄系統（Version Control Practice）



本專案為「軟體工程導論」作業二，目的在於透過實作一個簡易的 \*\*支出紀錄系統\*\*，實際練習 \*\*Git 分支開發與合併（branch / merge）的協作流程\*\*。



系統分為兩個模組：

\- \*\*輸入模組（Input Module）\*\*：用來輸入並儲存支出資料

\- \*\*視覺化模組（Visualization Module）\*\*：讀取儲存的資料並依分類產生圓餅圖



---



\## 專案架構

assignment2/

├─ input.py          # 支出輸入模組（A 同學）

├─ visualize.py      # 支出視覺化模組（B 同學）

├─ expenses.csv      # 支出資料（由 input.py 產生）

├─ README.md

└─ output/

&nbsp;  └─ pie.png        # 圓餅圖範例輸出



執行環境需求:Python 3.9 以上

套件需求：matplotlib

安裝套件指令：pip install matplotlib



使用方式說明

一、執行輸入模組（新增支出資料）python input.py

預設會將資料儲存在 expenses.csv。

若要指定其他檔案名稱：python input.py --file expenses.csv



每筆支出包含以下欄位：

日期（YYYY-MM-DD，或可輸入 today / 今日）

金額

類別

備註（可選）

資料會自動寫入 CSV 檔案。



二、執行視覺化模組（產生圓餅圖）

當 expenses.csv 中已有資料後，執行：python visualize.py --input expenses.csv

常用參數範例如下：

python visualize.py \\

&nbsp; --input expenses.csv \\

&nbsp; --output output/pie.png \\

&nbsp; --title "支出分類圓餅圖" \\

&nbsp; --show \\

&nbsp; --min-ratio 0.03

