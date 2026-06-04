# Edge-TTS 生成 14 段旁白（FTIR 咖啡 PCA 教學影片）
# 執行：python generate_narration.py
import asyncio, edge_tts
from pathlib import Path

OUT = Path(__file__).parent / "assets" / "narration"
OUT.mkdir(parents=True, exist_ok=True)
VOICE, RATE, PITCH = "zh-TW-YunJheNeural", "-10%", "-2Hz"

SCRIPT = [
    (1,  "傅立葉轉換紅外光譜，FTIR，是食品分析裡最快速的化學掃描儀。它能把一支咖啡，變成二百八十六個波數的吸收指紋。但這二百八十六個數字，我們要怎麼讀懂？這個系列，就從主成分分析 PCA 開始。"),
    (2,  "在食品分析裡，FTIR 常這樣用。把咖啡粉放進儀器，紅外光掃過，每一個分子鍵在特定波數吸收能量，最後整理成一條曲線：橫軸是波數，單位 cm⁻¹，縱軸是吸收值。今天的資料，五十六支即溶咖啡，就是這樣來的。"),
    (3,  "這是 Mendeley Data 公開的即溶咖啡 FTIR 資料：五十六支，包含二十九支 Arabica 和二十七支 Robusta。每一條折線，就是一支咖啡的光譜指紋。問題來了：每支咖啡，是二百八十六維空間裡的一個點，人眼根本看不出哪些像、哪些不像。"),
    (4,  "分析前要先整理。DRIFT 模式量到的光譜，有基線飄移和散射效應，同一支咖啡不同批次量就可能偏移。SNV，標準正常變量法，先算出每條光譜的平均和標準差，把每一點都標準化，讓所有光譜站在同一基線上。這一步，是 DRIFT 分析的標準作法。"),
    (5,  "主成分分析的想法很直覺。把所有咖啡，想成一團散開的點。PCA 要找出這團點最分散的方向，當作第一主成分 PC1；再找一個跟它垂直、第二分散的方向，當作 PC2。新的座標軸，永遠對準資訊最多的方向。"),
    (6,  "用數學講，PCA 把資料矩陣 X，拆成分數 T，乘上負荷量 P 的轉置。分數，是每支咖啡在新座標上的位置；負荷量，告訴我們每一個波數，怎麼組成這些新方向。一個看樣本，一個看波數的貢獻。"),
    (7,  "要保留幾個主成分？看陡坡圖。FTIR 光譜中相鄰波數高度相關，所以資訊很集中：PC1 就佔了百分之四十四點五，前兩個加起來百分之六十七點六，前三個達百分之七十六點三。光是前兩個主成分，就已經掌握了最重要的品種結構。"),
    (8,  "把每支咖啡畫在 PC1、PC2 上，神奇的事發生了：PCA 從頭到尾，都不知道品種，兩種咖啡卻自己依品種聚在一起，Arabica 一群、Robusta 另一群，主要靠 PC2 區分。結構，自己浮現了。"),
    (9,  "那是哪些波段，讓品種分開？看負荷量。PC1 貢獻最大的波段，集中在 1714、1710、1706 cm⁻¹，這是羰基和脂質 C=O 的伸縮振動區。Arabica 和 Robusta 的脂質組成不同，紅外光譜把這個差異翻譯出來了。"),
    (10, "為什麼要用這個範圍？中紅外的 810 到 1911 波數，是所謂的指紋區。就像人的指紋，每一種食品在這個範圍的吸收模式，都是獨一無二的。它包含了 C–O、C–C、C–N 等骨架振動，任何微小的化學差異，都會留下痕跡。"),
    (11, "要記得，PCA 是非監督式的：它只看光譜本身，不需要任何標準答案。它擅長探索、分群、找異常；但它不會直接告訴你，這支咖啡是 Arabica 還是 Robusta。那，是下一支影片的任務。"),
    (12, "把流程串起來：FTIR 光譜，先做 SNV 散射校正，再用 PCA，拆成分數、負荷量、和陡坡圖。分數看分群和品種結構、負荷量看哪個波段在貢獻、陡坡圖決定要保留幾個主成分。這就是用 PCA 探索咖啡 FTIR 資料的完整地圖。"),
    (13, "一句話帶走：PCA，把二百八十六個波數，壓縮成幾個你看得懂的方向。"),
    (14, "PCA 讓我們看見了品種的影子。但要真正建立一個，能鑑別 Arabica 和 Robusta 的模型，就要用到下一支影片的主角，PLS-DA。"),
]

async def synth(i, text):
    out = OUT / f"page-{i:02d}.mp3"
    await edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH).save(str(out))
    print(f"OK page-{i:02d}.mp3")

async def main():
    for i, t in SCRIPT:
        for r in range(3):
            try: await synth(i, t); break
            except Exception as e:
                print(f"retry {i} ({r+1}): {e}"); await asyncio.sleep(2)
    print("All done.")

if __name__ == "__main__":
    asyncio.run(main())
