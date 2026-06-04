# 渲染引擎（FTIR 咖啡 PCA）：$env:NODE_PATH="$env:TEMP\cvs-render\node_modules"; python render.py
import os, sys, shutil, subprocess, glob
from pathlib import Path
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach()); sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
ROOT = Path(__file__).resolve().parent
RENDERS = ROOT/"renders"; RENDERS.mkdir(parents=True, exist_ok=True)
NARR = ROOT/"assets"/"narration"; RECORD = ROOT/"record.cjs"
PAGES_TIMINGS = [{"i": 1, "dur": 24}, {"i": 2, "dur": 25}, {"i": 3, "dur": 24}, {"i": 4, "dur": 28}, {"i": 5, "dur": 24}, {"i": 6, "dur": 22}, {"i": 7, "dur": 26}, {"i": 8, "dur": 21}, {"i": 9, "dur": 26}, {"i": 10, "dur": 26}, {"i": 11, "dur": 22}, {"i": 12, "dur": 26}, {"i": 13, "dur": 10}, {"i": 14, "dur": 14}]
def node_env():
    e=os.environ.copy(); e["NODE_PATH"]=os.path.join(e.get("TEMP","C:\\Temp"),"cvs-render","node_modules"); return e
def master_audio():
    print("[1/3] master audio"); m=RENDERS/"master_audio.mp3"
    if m.exists(): os.remove(m)
    pad=[]
    for p in PAGES_TIMINGS:
        i,d=p["i"],p["dur"]; src=NARR/f"page-{i:02d}.mp3"; dst=RENDERS/f"pad-{i:02d}.mp3"
        if not src.exists(): raise FileNotFoundError(src)
        if dst.exists(): os.remove(dst)
        r=subprocess.run(["ffmpeg","-y","-i",str(src),"-af","apad","-t",str(d),str(dst)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if r.returncode: print(r.stderr.decode('utf-8','ignore')); r.check_returncode()
        pad.append(dst)
    cc=RENDERS/"cc.txt"; open(cc,"w",encoding="utf-8").write("".join(f"file '{p.name}'\n" for p in pad))
    r=subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(cc),"-c","copy",str(m)],cwd=str(RENDERS),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if r.returncode: print(r.stderr.decode('utf-8','ignore')); r.check_returncode()
    for p in pad:
        try: os.remove(p)
        except: pass
    os.remove(cc); print("  ok")
def record():
    print("[2/3] record");
    for f in glob.glob(str(RENDERS/"*.webm")):
        try: os.remove(f)
        except: pass
    subprocess.run(["node",str(RECORD)],cwd=str(ROOT),env=node_env(),check=True,shell=True)
    w=glob.glob(str(RENDERS/"*.webm"))
    if not w: raise FileNotFoundError("no webm")
    t=RENDERS/"video.webm"
    if t.exists(): os.remove(t)
    shutil.move(w[0],t); print("  ok")
def mux():
    print("[3/3] mux"); f=ROOT/"final.mp4"
    if f.exists(): os.remove(f)
    r=subprocess.run(["ffmpeg","-y","-i",str(RENDERS/"video.webm"),"-i",str(RENDERS/"master_audio.mp3"),"-map","0:v","-map","1:a","-c:v","libx264","-pix_fmt","yuv420p","-crf","20","-c:a","aac","-b:a","192k","-shortest",str(f)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if r.returncode: print(r.stderr.decode('utf-8','ignore')); r.check_returncode()
    print(f"  ok -> {f}")
try:
    master_audio(); record(); mux(); print("=== DONE ftir/pca final.mp4 ===")
except Exception as e:
    print(f"[ERROR] {e}"); sys.exit(1)
