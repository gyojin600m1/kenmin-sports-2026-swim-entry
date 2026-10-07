# R8 県民スポーツ大会（水泳競技）エントリー確認

令和８年度県民スポーツ大会（水泳競技）の出場選手を、選手名・地区・種目から探せるスマホ用アプリ。

- 大会：2026年10月11日（日）大和村民プール
- 公開URL：https://gyojin600m1.github.io/kenmin-sports-2026-swim-entry/
- 元データ：鹿児島県水泳連盟のプログラムPDF（2026年10月7日掲載分）
  https://www.kagoshima-swim.com/new/wp-content/uploads/2026/10/20261011_program.pdf

## できること
- 🔍 選手・地区：名前・地区名で検索（クラス・男女で絞り込み）。出場種目・時刻・組・レーンを表示
- 📋 種目検索：No.1〜48 の組・レーン表。前後の種目へ移動、地区を⭐で目立たせる
- ⏱ 競技順序：48種目の時刻・組数・人数・大会記録。大会当日は次の種目に「まもなく」

## 作り直し方（PDFが差し替わったとき）
```
python3 tools/build.py              # 連盟サイトから最新のPDFを取ってきて index.html を作る
python3 tools/build.py program.pdf  # 手元のPDFから作る
```
`pdftotext`（poppler-utils）が必要。参加者集計表の合計人数・競技順序表の組数と合わない場合は止まる。
作り直したら `main` と `gh-pages` の両方に push する。

## 公開・非公開
`gyojin600m1/swim-share-control` の「① エントリー確認を見せる」に登録して使う。
Notion「鹿児島水泳エントリー検索！随時更新！」にリンクを載せているので、⑧ で閉じる対象には入れていない。
