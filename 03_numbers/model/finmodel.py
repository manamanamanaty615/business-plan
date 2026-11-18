# リクスワ 月次財務モデル（2027/1〜2032/3）
# 前提の説明は 03_numbers/assumptions.md、拡大の選択肢は 03_numbers/expansion-strategy.md。
# 実行：python3 -E 03_numbers/model/export.py（financials*.csv・headcount.csv・expansion-scenarios.csv を出力）
import math, copy

P = dict(
    store_per_co=2.0,                 # 1社あたり店舗数【推測】
    co_2709=100, co_2803=300,         # GTM 基準（社、純数）
    guide_peak=14000, guide_ramp=12,  # Indeed Plus 営業経由の月間案内数（ピーク）と立ち上げ月数
    reach=0.6,                        # 案内到達率（各業種の店舗数×60% が上限）
    churn_store=0.05, churn_mau=0.10,
    pay_rate=0.60, posts=0.3, price_post=40000,
    mau_per_store=30, mau_ramp=12, indeed_per_store=30,
    clicks=0.9, cpc=150, fee=0.20,
    hire_per_click=225000/(15000000*12),  # 旧計画シリーズCの比率【推測】
    cpa_early=230, cpa_late=128, cac=8000, cac_rival=30000, own_cap=2600,
    cdn=0.05, views=30, ai_review=15, ai_edit=100,
    sns_ad_month=0.5,
    cs_ratio_early=500, cs_ratio_late=2000, sales_ratio=2000,
    oh_rate=0.15, oh_fixed_year=3,
)
# 業種（母集団 100 万店を求人件数の比率で按分【推測】）
SEG = {
    'all':       dict(name='全業種（業種を区別しない）', U=1_000_000, a=0.35, start='PF', recruit=True, channel='indeed'),
    'food_juku': dict(name='飲食・学習塾', U=1_000_000*0.251, a=0.35, start='PF', recruit=True, channel='indeed'),
    'other_fit': dict(name='動画が向くその他の業種', U=1_000_000*0.144, a=0.35, start='MIG0', recruit=True, channel='indeed'),
    'non_fit':   dict(name='動画が向きにくい業種', U=1_000_000*0.605, a=0.15, start='2030/4', recruit=True, channel='indeed'),
    'rival':     dict(name='他社媒体だけを使う店舗', U=156_000/0.6, a=0.175, start='MIG0', recruit=False, channel='own'),
}
BASE_SEGS = ['food_juku', 'other_fit', 'rival']   # 正本＝推奨案 R1（2026-11-16 決定）
UNIT = {'プロダクト・エンジニアリング':16,'デザイン・動画クリエイティブ':12,'事業開発・企画':14,'データ・AI':15,'店舗開拓・法人営業':11,
        '動画審査・カスタマーサクセス':9,'法務・コーポレート':15,'経営管理':17,'広告営業':12,'SNS・チャンネル運用':12}
FIXED = {
 '2次選考':{'事業開発・企画':5}, '最終選考・準備':{'事業開発・企画':5},
 'MVP':{'プロダクト・エンジニアリング':5,'デザイン・動画クリエイティブ':2,'事業開発・企画':5,'データ・AI':1,'SNS・チャンネル運用':2},
 'シード':{'プロダクト・エンジニアリング':7,'デザイン・動画クリエイティブ':2,'事業開発・企画':5,'データ・AI':2,'SNS・チャンネル運用':2},
 'アーリー':{'プロダクト・エンジニアリング':9,'デザイン・動画クリエイティブ':3,'事業開発・企画':5,'データ・AI':2,'法務・コーポレート':1,'SNS・チャンネル運用':2},
 'シリーズA':{'プロダクト・エンジニアリング':11,'デザイン・動画クリエイティブ':3,'事業開発・企画':5,'データ・AI':3,'法務・コーポレート':2,'経営管理':1,'SNS・チャンネル運用':2},
 'シリーズB':{'プロダクト・エンジニアリング':12,'デザイン・動画クリエイティブ':3,'事業開発・企画':5,'データ・AI':3,'法務・コーポレート':2,'経営管理':2,'広告営業':2,'SNS・チャンネル運用':2},
 'シリーズC':{'プロダクト・エンジニアリング':13,'デザイン・動画クリエイティブ':4,'事業開発・企画':5,'データ・AI':4,'法務・コーポレート':2,'経営管理':3,'広告営業':3,'SNS・チャンネル運用':2},
}
DEV = {'2次選考':1,'最終選考・準備':1,'MVP':61,'シード':336,'アーリー':864,'シリーズA':932,'シリーズB':439,'シリーズC':627}  # 百万円/年

def months():
    y, m = 2027, 1
    while (y, m) <= (2032, 3):
        yield y, m
        m += 1
        if m > 12: y, m = y + 1, 1
def idx(y, m): return (y - 2027) * 12 + (m - 1)
MVP0, PF, PAY, MIG0, MIG1 = idx(2027,4), idx(2028,4), idx(2028,10), idx(2029,4), idx(2031,3)
START = {'PF': PF, 'MIG0': MIG0, '2030/4': idx(2030,4)}
def stage(y, m):
    i = idx(y, m)
    for lim, name in [(idx(2027,1),'2次選考'),(idx(2027,3),'最終選考・準備'),(idx(2027,9),'MVP'),(idx(2028,3),'シード'),(idx(2029,3),'アーリー'),(idx(2030,3),'シリーズA'),(idx(2031,3),'シリーズB')]:
        if i <= lim: return name
    return 'シリーズC'
def FY(y, m): return y if m >= 4 else y - 1

def run(P=P, segs=BASE_SEGS, billing='A'):
    """billing: A＝無料→2028/10 掲載課金→2029/4〜2031/3 クリック課金へ移行（決定済み）
                B＝2028/4 から掲載課金、C＝2028/4 から自社 MAU をクリック課金"""
    st = {k: dict(stores=0.0) for k in segs}
    act_mult = {'A': 1.0, 'B': 0.30/0.35, 'C': 0.45/0.35}[billing]
    pay0 = PAY if billing == 'A' else PF
    rows = []; mau = 0.0; cum = 0.0
    for y, m in months():
        i = idx(y, m); sg = stage(y, m)
        new_tot = lost_tot = new_rival = guide_tot = 0.0
        if MVP0 <= i < PF:
            k = i - MVP0 + 1
            co = P['co_2709']*k/6 if k <= 6 else P['co_2709'] + (P['co_2803']-P['co_2709'])*(k-6)/6
            s0 = co * P['store_per_co']; k0 = segs[0]
            new_tot = s0 - st[k0]['stores']; st[k0]['stores'] = s0
        elif i >= PF:
            G = P['guide_peak'] * min(1, (i-PF+1)/P['guide_ramp'])
            pools = {k: max(0, P['reach']*SEG[k]['U'] - st[k]['stores']) for k in segs
                     if SEG[k]['channel'] == 'indeed' and i >= START[SEG[k]['start']]}
            tot = sum(pools.values())
            for k in segs:
                d = SEG[k]
                if i < START[d['start']]: continue
                g = (G*pools[k]/tot if tot > 0 else 0) if d['channel'] == 'indeed' else P['own_cap']
                sat = max(0, 1 - st[k]['stores']/(P['reach']*d['U']))
                new = g * d['a'] * act_mult * sat; lost = st[k]['stores'] * P['churn_store']
                st[k]['stores'] += new - lost
                new_tot += new; lost_tot += lost; guide_tot += g
                if not d['recruit']: new_rival += new
        stores = sum(v['stores'] for v in st.values())
        rival = sum(st[k]['stores'] for k in segs if not SEG[k]['recruit'])
        s_mig = 0 if i < MIG0 else min(1, (i-MIG0+1)/(MIG1-MIG0+1))
        s_own = 1 if (billing == 'C' and i >= PF) else s_mig
        paying = stores * P['pay_rate'] if (i >= pay0 and billing != 'C') else 0
        pm = mau
        mau = 0 if i < PF else stores * P['mau_per_store'] * min(1, (i-PF+1)/P['mau_ramp'])
        mau_new = max(0, mau - pm*(1-P['churn_mau'])) if i >= PF else 0
        indeed = stores * P['indeed_per_store'] * s_mig
        hires = (mau + indeed) * P['clicks'] * P['hire_per_click']
        rev_post = paying * (1-s_own) * P['posts'] * P['price_post'] / 1e6
        rev_click = (mau*s_own + indeed) * P['clicks'] * P['cpc'] / 1e6
        hc = dict(FIXED[sg])
        if i >= MVP0: hc['動画審査・カスタマーサクセス'] = math.ceil(stores/(P['cs_ratio_early'] if i < PF else P['cs_ratio_late']))
        if i >= PF: hc['店舗開拓・法人営業'] = math.ceil(new_tot*12/P['sales_ratio'])
        labor = sum(UNIT[k]*v for k, v in hc.items()) / 12
        cpa = P['cpa_early'] if i < MIG0 else P['cpa_late']
        acq_seek = mau_new * cpa / 1e6
        acq_store = ((new_tot-new_rival)*P['cac'] + new_rival*P['cac_rival'])/1e6 if i >= PF else 0
        sns = P['sns_ad_month'] if i >= MVP0 else 0
        dev = DEV[sg] / 12
        cdn = (mau + indeed) * P['views'] * P['cdn'] / 1e6
        ai = stores * P['posts'] * (P['ai_review'] + P['ai_edit']) / 1e6
        rev = rev_post + rev_click; fee = rev_click * P['fee']
        oh = labor * P['oh_rate'] + P['oh_fixed_year']/12
        cost = labor + acq_seek + acq_store + sns + dev + cdn + ai + fee + oh
        prof = rev - cost; cum += prof
        rows.append(dict(年月=f'{y}/{m:02d}', 会計年度=f'FY{FY(y,m)}', ステージ=sg, 案内数=guide_tot, 新規店舗=new_tot, 解約店舗=lost_tot,
            利用店舗数=stores, うち他社顧客の店舗=rival, 有料店舗数_掲載=paying*(1-s_own), 移行率=s_mig, 自社MAU=mau, 新規獲得MAU=mau_new,
            Indeed上の視聴者=indeed, 制作本数=stores*P['posts'], 採用決定数=hires, 人員=sum(hc.values()),
            売上_掲載課金=rev_post, 売上_クリック課金=rev_click, 売上合計=rev, うち他社顧客の売上=rev*(rival/stores if stores else 0),
            人件費=labor, 求職者獲得費=acq_seek, 店舗獲得費=acq_store, SNS広告費=sns, 開発費=dev, 動画配信CDN費=cdn, AI処理費=ai,
            IndeedPLUS利用料=fee, 間接費配賦=oh, 費用計=cost, 営業利益=prof, 累積損益=cum, hc=hc))
    return rows

def summary(rows):
    c = [r for r in rows if r['会計年度'] == 'FY2031']; peak = min(r['累積損益'] for r in rows)
    fy = {}
    for f in ['FY2027','FY2028','FY2029','FY2030','FY2031']:
        rr = [r for r in rows if r['会計年度'] == f]
        fy[f] = dict(rev=sum(r['売上合計'] for r in rr), prof=sum(r['営業利益'] for r in rr), stores=rr[-1]['利用店舗数'])
    return dict(c_rev=fy['FY2031']['rev'], c_prof=fy['FY2031']['prof'], c_rev_rival=sum(r['うち他社顧客の売上'] for r in c),
        peak=peak, peak_m=[r['年月'] for r in rows if r['累積損益'] == peak][0],
        first_profit=next((r['年月'] for r in rows if r['営業利益'] > 0), 'なし'),
        cum_be=next((r['年月'] for r in rows[1:] if r['累積損益'] > 0), 'なし'),
        stores=rows[-1]['利用店舗数'], rival=rows[-1]['うち他社顧客の店舗'], mau=rows[-1]['自社MAU'], indeed=rows[-1]['Indeed上の視聴者'],
        hires=sum(r['採用決定数'] for r in c), people=rows[-1]['人員'], rr_rev=rows[-1]['売上合計']*12, rr_prof=rows[-1]['営業利益']*12, fy=fy)

SCENARIOS = [
    ('R1', '正本・推奨案：飲食・学習塾＋動画が向く業種＋他社媒体の顧客', BASE_SEGS, 'A'),
    ('S0', '旧正本（2026-11-15版）：全業種を一律に扱う', ['all'], 'A'),
    ('I1', '業種：飲食・学習塾だけ', ['food_juku'], 'A'),
    ('I2', '業種：＋動画が向くその他の業種（2029/4〜）', ['food_juku','other_fit'], 'A'),
    ('I3', '業種：＋動画が向きにくい業種まで（2030/4〜）', ['food_juku','other_fit','non_fit'], 'A'),
    ('B1', '課金：I2で、掲載課金を自社PF公開と同時に（2028/4〜）', ['food_juku','other_fit'], 'B'),
    ('C1', '課金：I2で、クリック課金を自社PF公開から（2028/4〜）', ['food_juku','other_fit'], 'C'),
]
SENS = [('クリック単価','cpc',[100,200]),('月間クリック数','clicks',[0.45,1.5]),('Indeed 利用料率','fee',[0.30,0.10]),('店舗の月次解約率','churn_store',[0.07,0.03]),
        ('月間案内数（ピーク）','guide_peak',[7000,28000]),('1店舗あたりの視聴者（自社・Indeed 各）','mau_per_store',[15,60]),('掲載課金の単価','price_post',[20000,10000]),
        ('有料転換率','pay_rate',[0.30,0.80]),('他社顧客の CAC','cac_rival',[60000,15000]),('1社あたり店舗数','store_per_co',[1,3])]
def sensitivity():
    out = []
    for lab, k, vals in SENS:
        for v in vals:
            Q = copy.deepcopy(P); Q[k] = v
            if k == 'mau_per_store': Q['indeed_per_store'] = v
            out.append((lab, v, summary(run(Q))))
    return out
