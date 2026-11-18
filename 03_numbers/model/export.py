# finmodel.py の結果を 03_numbers の CSV に書き出す
import csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import finmodel as f
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + '/'
rows = f.run()
def r1(v):
    v = round(v, 1); return str(int(v)) if v == int(v) else str(v)
INT = ('案内数','新規店舗','解約店舗','利用店舗数','うち他社顧客の店舗','有料店舗数_掲載','自社MAU','新規獲得MAU','Indeed上の視聴者','制作本数','採用決定数','人員')
keys = [k for k in rows[0] if k != 'hc']
with open(OUT+'financials_monthly.csv','w',encoding='utf-8',newline='') as fh:
    w = csv.writer(fh, lineterminator='\n'); w.writerow(keys)
    for r in rows:
        w.writerow([r[k] if isinstance(r[k], str) else (f'{r[k]:.3f}' if k == '移行率' else (str(round(r[k])) if k in INT else f'{r[k]:.2f}')) for k in keys])
FYS = [('FY2026','2次選考・最終選考(2027/1〜3)'),('FY2027','MVP・シード(2027/4〜2028/3)'),('FY2028','アーリー(2028/4〜2029/3)'),
       ('FY2029','シリーズA(2029/4〜2030/3)'),('FY2030','シリーズB(2030/4〜2031/3)'),('FY2031','シリーズC(2031/4〜2032/3)')]
by = {fy: [r for r in rows if r['会計年度'] == fy] for fy, _ in FYS}
SRC = 'financials_monthly.csv(model/finmodel.py)から集計。前提は assumptions.md'
stock = [('期末利用店舗数','店','利用店舗数'),('うち他社媒体の顧客','店','うち他社顧客の店舗'),('期末有料店舗数(掲載課金)','店','有料店舗数_掲載'),
         ('期末自社MAU','万人','自社MAU'),('期末Indeed上の視聴者','万人','Indeed上の視聴者'),('期末人員','人','人員')]
flow = [('採用決定数(自社・Indeed経由)','件','採用決定数'),('新規店舗数','店','新規店舗'),('解約店舗数','店','解約店舗'),('新規獲得MAU','万人','新規獲得MAU'),
        ('売上_掲載課金','百万円','売上_掲載課金'),('売上_クリック課金','百万円','売上_クリック課金'),('売上合計','百万円','売上合計'),('うち他社媒体の顧客の売上','百万円','うち他社顧客の売上'),
        ('人件費','百万円','人件費'),('求職者獲得費','百万円','求職者獲得費'),('店舗獲得費','百万円','店舗獲得費'),('SNS広告費','百万円','SNS広告費'),
        ('開発費(外注+SaaS)','百万円','開発費'),('動画配信・CDN費','百万円','動画配信CDN費'),('AI処理費(審査+編集)','百万円','AI処理費'),
        ('IndeedPLUS配信基盤利用料','百万円','IndeedPLUS利用料'),('間接費配賦','百万円','間接費配賦'),('費用計','百万円','費用計'),('営業利益','百万円','営業利益')]
def cell(v, u):
    if u == '万人': return r1(v/1e4)
    if u in ('店','件','人'): return str(round(v))
    return r1(v)
with open(OUT+'financials.csv','w',encoding='utf-8',newline='') as fh:
    w = csv.writer(fh, lineterminator='\n'); w.writerow(['項目','単位']+[f'{a} {b}' for a, b in FYS]+['出典'])
    for lab, u, k in stock: w.writerow([lab, u]+[cell(by[fy][-1][k], u) for fy, _ in FYS]+['年度末(3月)の値。'+SRC])
    for lab, u, k in flow: w.writerow([lab, u]+[cell(sum(x[k] for x in by[fy]), u) for fy, _ in FYS]+['年度の合計。'+SRC])
    w.writerow(['年度末の売上(年換算)','百万円']+[r1(by[fy][-1]['売上合計']*12) for fy, _ in FYS]+['年度末(3月)の月次売上×12(参考)'])
    w.writerow(['年度末の営業利益(年換算)','百万円']+[r1(by[fy][-1]['営業利益']*12) for fy, _ in FYS]+['同上'])
    w.writerow(['累積損益(年度末)','百万円']+[r1(by[fy][-1]['累積損益']) for fy, _ in FYS]+['月次の営業利益の累計(2027/1から)。'+SRC])
NOTE = {'動画審査・カスタマーサクセス':'利用店舗数÷500(2028/3まで)・÷2,000(2028/4から)の切り上げ(issues.md C-6・D-3)',
        '店舗開拓・法人営業':'年間新規店舗数÷2,000の切り上げ。2028/3までは起案チームが直接営業(issues.md C-6・D-5)',
        'SNS・チャンネル運用':'MVPから2名(issues.md D-4)。単価はデザイン職と同じ【推測】','事業開発・企画':'起案チーム5名を下限(issues.md A-9)'}
with open(OUT+'headcount.csv','w',encoding='utf-8',newline='') as fh:
    w = csv.writer(fh, lineterminator='\n'); w.writerow(['職種','年間単価(百万円/人)']+[f'{a} {b}' for a, b in FYS]+['出典'])
    for ro in f.UNIT:
        w.writerow([ro, f.UNIT[ro]]+[str(by[fy][-1]['hc'].get(ro, 0)) for fy, _ in FYS]+[NOTE.get(ro,'ステージ別の人数はリクルートスワイプ_コスト試算表_v1.xlsx 01人件費内訳(ステージを新スケジュールに読み替え)')])
    w.writerow(['合計','']+[str(by[fy][-1]['人員']) for fy, _ in FYS]+['年度末(3月)の人数'])
    w.writerow(['人件費計(百万円)','']+[r1(sum(x['人件費'] for x in by[fy])) for fy, _ in FYS]+['年度の合計(financials.csv の人件費と同じ)'])
FY5 = ['FY2027','FY2028','FY2029','FY2030','FY2031']
with open(OUT+'expansion-scenarios.csv','w',encoding='utf-8',newline='') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(['コード','選択肢','C年度売上(百万円)','C年度営業利益(百万円)','うち他社顧客の売上(百万円)','ピーク資金需要(百万円)','ピーク月','累積黒字化','2032/3利用店舗','うち他社顧客の店舗','2032/3自社MAU(万人)','C年度採用決定数','2032/3人員']
               +[f'{x}売上' for x in FY5]+[f'{x}営業利益' for x in FY5]+[f'{x}末店舗' for x in FY5])
    for code, name, segs, b in f.SCENARIOS:
        s = f.summary(f.run(segs=segs, billing=b))
        w.writerow([code, name, r1(s['c_rev']), r1(s['c_prof']), r1(s['c_rev_rival']), r1(-s['peak']), s['peak_m'], s['cum_be'], round(s['stores']), round(s['rival']),
                    r1(s['mau']/1e4), round(s['hires']), s['people']]+[r1(s['fy'][x]['rev']) for x in FY5]+[r1(s['fy'][x]['prof']) for x in FY5]+[round(s['fy'][x]['stores']) for x in FY5])
with open(OUT+'sensitivity.csv','w',encoding='utf-8',newline='') as fh:
    w = csv.writer(fh, lineterminator='\n'); w.writerow(['変えた前提','値','C年度売上(百万円)','C年度営業利益(百万円)','ピーク資金需要(百万円)','累積黒字化'])
    for lab, v, s in f.sensitivity(): w.writerow([lab, v, r1(s['c_rev']), r1(s['c_prof']), r1(-s['peak']), s['cum_be']])
s = f.summary(rows)
print({k: (round(v, 1) if isinstance(v, float) else v) for k, v in s.items() if k != 'fy'})
print({k: {kk: round(vv) for kk, vv in v.items()} for k, v in s['fy'].items()})
