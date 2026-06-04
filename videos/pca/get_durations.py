# 量測旁白時長，輸出 PAGES（FTIR 咖啡 PCA · 14 頁）
import sys, subprocess, json
from pathlib import Path
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

NARR = Path(__file__).resolve().parent / "assets" / "narration"
SUBTITLES = [
    "FTIR 把咖啡變成 286 個波數的吸收指紋",
    "FTIR 掃描咖啡粉，生成波數 vs 吸收值曲線",
    "每支咖啡是 286 維的一點，眼睛看不出來",
    "SNV 消除散射基線，光譜站上同一起跑點",
    "PC1＝最大分散方向，PC2 與它垂直",
    "X ≈ T·Pᵀ：分數看樣本，負荷量看波數",
    "PC1=44.5%，前 2 個累積 67.6% 就夠",
    "PCA 不看品種，咖啡卻依品種自動分群",
    "1714 / 1710 / 1706 cm⁻¹ = 羰基脂質 C=O 振動區",
    "810–1911 cm⁻¹ 指紋區：食品獨特的化學簽名",
    "PCA 非監督：探索分群找異常，不做鑑別",
    "光譜 → SNV → PCA → 分數 / 負荷量 / 陡坡",
    "PCA：把 286 個波數，壓縮成看得懂的方向",
    "下一支：PLS-DA，從光譜指紋鑑別品種",
]
def dur(p):
    r = subprocess.run(["ffprobe","-v","quiet","-print_format","json","-show_format",str(p)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    return float(json.loads(r.stdout.decode())["format"]["duration"])
def main():
    PAGES, total = [], 0
    for i in range(1,15):
        p = NARR/f"page-{i:02d}.mp3"
        if not p.exists(): print(f"missing {p.name}"); return
        d = dur(p); pd = int(round(d+2.5)); total += pd
        PAGES.append(f'  {{ i: {i}, dur: {pd}, sub: "{SUBTITLES[i-1]}" }}')
        print(f"page-{i:02d}: voice={d:.2f}s -> {pd}s")
    print("\nconst PAGES = [\n"+",\n".join(PAGES)+"\n];")
    print("\nPAGES_TIMINGS = ["+", ".join(f'{{"i": {i+1}, "dur": {int(x.split("dur: ")[1].split(",")[0])}}}' for i,x in enumerate(PAGES))+"]")
    print(f"\nTOTAL = {total}s   (record waitForTimeout = {total*1000+800} ms)")
if __name__=="__main__": main()
