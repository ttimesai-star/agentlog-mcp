"""Generate the Agensi listing logo (512x512): a chain of steps with one red broken link."""
from PIL import Image, ImageDraw, ImageFont
import os

S = 512
img = Image.new("RGB", (S, S), "#0f172a")
d = ImageDraw.Draw(img)
try:
    f_big = ImageFont.truetype("arialbd.ttf", 54)
    f_small = ImageFont.truetype("arialbd.ttf", 40)
except OSError:
    f_big = f_small = ImageFont.load_default()

boxes = 4
w, gap = 78, 30
total = boxes * w + (boxes - 1) * gap
x0 = (S - total) // 2
y0 = 190
for i in range(boxes):
    x = x0 + i * (w + gap)
    broken = i == 2
    col = "#ef4444" if broken else "#22c55e"
    d.rounded_rectangle([x, y0, x + w, y0 + w], radius=14, outline=col, width=7, fill="#111c33")
    t = str(i)
    tw = d.textlength(t, font=f_big)
    d.text((x + (w - tw) / 2, y0 + 8), t, fill=col, font=f_big)
    if i < boxes - 1:
        lx = x + w
        c = "#ef4444" if i == 1 else "#22c55e"
        d.line([lx + 2, y0 + w // 2, lx + gap - 2, y0 + w // 2], fill=c, width=7)

title = "AGENT"
t2 = "ACTION LOG"
d.text(((S - d.textlength(title, font=f_small)) / 2, 70), title, fill="#e2e8f0", font=f_small)
d.text(((S - d.textlength(t2, font=f_small)) / 2, 112), t2, fill="#e2e8f0", font=f_small)
sub = "signed. chained. verified."
try:
    f3 = ImageFont.truetype("arial.ttf", 28)
except OSError:
    f3 = ImageFont.load_default()
d.text(((S - d.textlength(sub, font=f3)) / 2, 330), sub, fill="#94a3b8", font=f3)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agentlog_logo_512.png")
img.save(out)
print(out, img.size)
