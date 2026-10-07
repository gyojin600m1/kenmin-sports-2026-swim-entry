"""プログラムPDFから index.html を作り直す。

使い方（リポジトリのいちばん上で）:
    python3 tools/build.py              # 連盟サイトから最新のPDFを取ってきて作る
    python3 tools/build.py program.pdf  # 手元のPDFから作る

必要なもの: pdftotext（poppler-utils）
"""
import json, os, re, subprocess, sys, tempfile, urllib.request
from collections import Counter

PDF_URL = 'https://www.kagoshima-swim.com/new/wp-content/uploads/2026/10/20261011_program.pdf'
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

HDR = re.compile(r'No\.\s*(\d+)\s+(男子|女子)\s+(\d+m)\s+(\S+)')
CLS = re.compile(r'^\s*(成年|\d+歳以上)\s+(\d{1,2}:\d{2})')
REC = re.compile(r'大会\s+(\d+\.\d+)')
HEAT = re.compile(r'^\s*([１２３４1-4])組')
LANE = re.compile(r'^\s*([1-7])\.\s*(.*?)\s*\(\s*([^\s)]*)\s*\)\s*(\S*)')
ORDER = re.compile(r'(\d+)\s+(成年|\d+歳以上)\s+(男子|女子)\s+(\d+m)\s+(\S+)\s+(\d)\s+(\d+:\d+)')
TOTAL = re.compile(r'合\s*計\s+(\d+)\s+(\d+)\s+(\d+)')
Z2H = str.maketrans('１２３４', '1234')


def pdftotext(pdf, *args):
    return subprocess.run(['pdftotext', '-layout', *args, pdf, '-'], check=True,
                          capture_output=True, text=True).stdout


def main():
    if len(sys.argv) > 1:
        pdf = sys.argv[1]
    else:
        pdf = os.path.join(tempfile.mkdtemp(), 'program.pdf')
        urllib.request.urlretrieve(PDF_URL, pdf)

    whole = pdftotext(pdf)
    pages = int(re.search(r'Pages:\s+(\d+)', subprocess.run(
        ['pdfinfo', pdf], check=True, capture_output=True, text=True).stdout).group(1))

    # 競技順序表（組数・時刻）
    order = {}
    for m in ORDER.finditer(whole):
        order[int(m.group(1))] = dict(cls=m.group(2), sex=m.group(3), di=m.group(4), st=m.group(5),
                                      heats=int(m.group(6)), time=m.group(7))
    assert order and sorted(order) == list(range(1, max(order) + 1)), sorted(order)

    # スタートリスト: 各ページを左右の段に分けて、左段→右段の順に読む
    rows, recs = [], {}
    ev, heat = None, 1
    for p in range(1, pages + 1):
        for x in (0, 298):
            col = pdftotext(pdf, '-f', str(p), '-l', str(p), '-x', str(x), '-y', '0', '-W', '298', '-H', '842')
            for line in col.splitlines():
                m = HDR.search(line)
                if m:
                    ev = int(m.group(1))
                    heat = 1
                    continue
                m = REC.search(line)
                if m and ev and ev not in recs:
                    recs[ev] = m.group(1)
                if CLS.match(line):
                    continue
                m = HEAT.match(line)
                if m:
                    heat = int(m.group(1).translate(Z2H))
                m = LANE.match(HEAT.sub('', line))
                if m and m.group(2) and ev:
                    o = order[ev]
                    grade = m.group(4) if re.fullmatch(r'[大高中小]\d', m.group(4) or '') else ''
                    rows.append(dict(no=ev, heat=heat, lane=int(m.group(1)),
                                     name=re.sub(r'\s+', ' ', m.group(2)).strip(), team=m.group(3),
                                     grade=grade, open='OPEN' in line, sex=o['sex'], cls=o['cls']))

    # 確かめ: 参加者集計表の合計・組数・レーンの重なり
    total = TOTAL.search(whole)
    if total:
        male, female, both = map(int, total.groups())
        assert len(rows) == both, (len(rows), both)
        assert sum(r['sex'] == '女子' for r in rows) == female
    for n, o in order.items():
        hs = {r['heat'] for r in rows if r['no'] == n}
        assert hs == set(range(1, o['heats'] + 1)), (n, hs, o['heats'])
    dup = [k for k, c in Counter((r['no'], r['heat'], r['lane']) for r in rows).items() if c > 1]
    assert not dup, dup

    prog = [[n, o['cls'], o['sex'], o['di'], o['st'], o['time'], o['heats'], recs.get(n, '')]
            for n, o in sorted(order.items())]
    people = {}
    for r in sorted(rows, key=lambda r: (r['no'], r['heat'], r['lane'])):
        o = order[r['no']]
        key = (r['name'], r['team'])
        if key not in people:
            people[key] = [len(people) + 1, r['name'], '', r['team'], r['team'], r['grade'], r['cls'],
                           '女' if r['sex'] == '女子' else '', []]
        people[key][8].append([o['st'], o['di'], '', r['no'], r['heat'], r['lane'], 1 if r['open'] else 0])

    html = open(os.path.join(HERE, 'template.html'), encoding='utf-8').read()
    html = html.replace('DATA_PLACEHOLDER', json.dumps(list(people.values()), ensure_ascii=False, separators=(',', ':')))
    html = html.replace('PROG_PLACEHOLDER', json.dumps(prog, ensure_ascii=False, separators=(',', ':')))
    open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(html)
    print(f'index.html を作りました: {len(people)}名 / {len(rows)}件 / {len(prog)}種目 / 大会記録{len(recs)}件')
    print('地区別:', dict(Counter(r['team'] for r in rows).most_common()))


if __name__ == '__main__':
    main()
