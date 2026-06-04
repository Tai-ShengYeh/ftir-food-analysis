# Edge-TTS 生成 13 段旁白（FTIR 咖啡 PLS-DA 教學影片）
import asyncio, edge_tts
from pathlib import Path
OUT = Path(__file__).parent / "assets" / "narration"; OUT.mkdir(parents=True, exist_ok=True)
VOICE, RATE, PITCH = "zh-TW-YunJheNeural", "-10%", "-2Hz"
SCRIPT = [
    (1,  "上一支影片，PCA 讓我們看見咖啡依品種分群。但它從不替我們做決定。這一支，我們要更進一步：給模型看過品種標籤，讓它學會鑑別 Arabica 和 Robusta。這，就是 PLS-DA。"),
    (2,  "差別在哪？PCA 是非監督的，它只看光譜、不看答案，所以它發現了品種，卻不是為了品種而分。PLS-DA 不一樣：我們把品種標籤交給它，要它找出最能分開 Arabica 和 Robusta 的方向。從探索，變成有目標的鑑別。"),
    (3,  "用一張圖看懂。同一批咖啡光譜，PCA 的方向，追的是整體最大的分散；PLS-DA 的方向，會轉過去，對齊 Arabica 和 Robusta 之間的分界。它犧牲一點總變異，換來的，是更乾淨的品種分類。"),
    (4,  "數學上，PLS-DA 先把品種變成數字標籤：Arabica 是 1，Robusta 是 0。再找一組權重 w，讓光譜的投影，和類別之間的共變異最大。這些新方向，叫潛在變量 LV。它和主成分一樣是壓縮，但壓縮的目標，是分類。"),
    (5,  "我們把二十九支 Arabica 和二十七支 Robusta，畫在 PLS-DA 的潛在變量上。光是第一條軸 LV1，就乾淨地把兩個品種左右分開。這，就是監督式的威力：模型知道你要問什麼，它就衝著那個方向去找。"),
    (6,  "但這裡有個陷阱。如果用同一批咖啡，又訓練、又評分，模型等於先看過答案，分數會虛高。所以我們用交叉驗證：把五十六支咖啡分成五份，每次留一份當測試、其餘拿來訓練，輪流五次。這樣算出來的準確率，才誠實。"),
    (7,  "那要用幾個潛在變量？看這條交叉驗證曲線。只用一個 LV，準確率就有百分之九十八點二；到兩個，達到百分之百。再加更多呢？不會更好，只會讓模型開始硬背雜訊，這就是過度擬合。原則是：停在夠用的地方。"),
    (8,  "把交叉驗證的預測，攤成一張混淆矩陣。對角線上，二十九支 Arabica 全對，二十七支 Robusta 也全對，沒有一支認錯。在誠實的驗證下，這兩個品種，可以從 FTIR 光譜被完美區分。"),
    (9,  "模型靠什麼分？看 PLS-DA 的回歸係數。排在最前面的，是 1007、957、903 波數，這個區域是醣類的 C–O 鍵伸縮振動。Arabica 和 Robusta 的咖啡因、綠原酸、碳水化合物組成不同，這些差異全都落在這個波段。模型挑出來的，是真正有意義的咖啡化學。"),
    (10, "把品種換成別的標籤，同一套 PLS-DA，就是食品真偽鑑別的主力工具：判斷咖啡有沒有摻入廉價 Robusta、蜂蜜有沒有摻糖、橄欖油的產地。FTIR 給指紋；PLS-DA 給答案。"),
    (11, "最後，把兩支影片連起來。同樣的 FTIR 光譜、同樣的 SNV 前處理，分成兩條路：想探索、找結構，用 PCA，非監督；想鑑別、做決定，用 PLS-DA，監督。先探索，再建模，這就是食品 FTIR 分析的完整地圖。"),
    (12, "一句話帶走：PLS-DA，讓 FTIR 光譜指紋，直接說出，這，是 Arabica，還是 Robusta。"),
    (13, "看完概念，下一步，就是打開 Orange Data Mining，不用寫一行程式，親手把這整套 PCA 和 PLS-DA 拉一遍。我們，課堂見。"),
]
async def synth(i,t):
    await edge_tts.Communicate(t,VOICE,rate=RATE,pitch=PITCH).save(str(OUT/f"page-{i:02d}.mp3")); print(f"OK page-{i:02d}.mp3")
async def main():
    for i,t in SCRIPT:
        for r in range(3):
            try: await synth(i,t); break
            except Exception as e: print(f"retry {i}: {e}"); await asyncio.sleep(2)
    print("All done.")
asyncio.run(main())
