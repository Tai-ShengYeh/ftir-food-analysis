import sys, subprocess, json
from pathlib import Path
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach()); sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
NARR = Path(__file__).resolve().parent / "assets" / "narration"
SUBTITLES = [
    "PLS-DA：讓模型學會鑑別 Arabica vs Robusta",
    "PCA 不看答案，PLS-DA 衝著答案去",
    "PLS-DA 把軸轉去對齊 Arabica / Robusta 分界",
    "找潛在變量 LV，最大化光譜與品種共變異",
    "LV1 乾淨地分開 Arabica 與 Robusta",
    "交叉驗證：訓練與測試分開才誠實",
    "1 LV 已 98.2%，2 LV 就 100%，夠用就好",
    "對角線全中，56 支咖啡完美鑑別",
    "1007 / 957 / 903 cm⁻¹ = 醣類 C–O 區，化學有意義",
    "品種、摻偽、產地——都靠 PLS-DA",
    "先用 PCA 探索，再用 PLS-DA 鑑別",
    "PLS-DA：讓 FTIR 指紋說出這是哪個品種",
    "接下來：用 Orange 親手做一次",
]
def dur(p):
    r=subprocess.run(["ffprobe","-v","quiet","-print_format","json","-show_format",str(p)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    return float(json.loads(r.stdout.decode())["format"]["duration"])
PAGES,total=[],0
for i in range(1,14):
    p=NARR/f"page-{i:02d}.mp3"
    if not p.exists(): print(f"missing {p.name}"); sys.exit()
    d=dur(p); pd=int(round(d+2.5)); total+=pd
    PAGES.append(f'  {{ i: {i}, dur: {pd}, sub: "{SUBTITLES[i-1]}" }}')
    print(f"page-{i:02d}: {d:.2f}s -> {pd}s")
print("\nconst PAGES = [\n"+",\n".join(PAGES)+"\n];")
print("\nPAGES_TIMINGS = ["+", ".join(f'{{"i": {i+1}, "dur": {int(x.split("dur: ")[1].split(",")[0])}}}' for i,x in enumerate(PAGES))+"]")
print(f"\nTOTAL = {total}s   (record waitForTimeout = {total*1000+800} ms)")
