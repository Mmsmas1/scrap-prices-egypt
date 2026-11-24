#!/usr/bin/env python3
"""Reads khurda.net category pages and writes prices.json (stdlib only)."""
import re, json, sys, html, urllib.request, datetime
BASE = "https://khurda.net/"
PAGES = ["scrap-iron","scrap-sheet","scrap-cast-iron","scrap-tin","scrap-stainless-steel","scrap-copper",
         "scrap-brass","scrap-aluminum","scrap-alumetal","scrap-cans","scrap-batteries-lead","scrap-batteries",
         "scrap-appliance","scrap-electronics","scrap-plastic","scrap-carton","scrap-papers","scrap-glass","scrap-tyre"]
UA = "scrap-board-personal/1.0 (personal dashboard, runs a few times a day)"
def get(u):
    r = urllib.request.Request(u, headers={"User-Agent": UA})
    return urllib.request.urlopen(r, timeout=30).read().decode("utf-8", "replace")
def clean(s): return html.unescape(re.sub(r"<[^>]+>", " ", s)).replace("\u200f","").strip()
def num(s):
    s = s.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩٬٫", "0123456789,.")).replace(",", "")
    return float(s)
def parse_val(txt):
    m = re.match(r"\s*([\d٠-٩.,٬٫]+)\s*(?:[–-]\s*([\d٠-٩.,٬٫]+))?\s*(.*)$", txt)
    if not m: return None
    lo = num(m.group(1)); hi = num(m.group(2)) if m.group(2) else lo
    return lo, hi, m.group(3).strip()
def parse_page(slug):
    h = get(BASE + slug + "/")
    t = re.search(r'class="kh-upd">.*?<time datetime="([^"]+)"', h, re.S)
    page_upd = t.group(1) if t else None
    out = []
    for card in re.findall(r'<div class="kh-pc".*?(?=<div class="kh-pc"|<div class=\'code-block|<p class="kh-note")', h, re.S):
        name = re.search(r"<h3>(.*?)<span", card, re.S)
        if not name: continue
        chg = re.search(r'class="kh-chg[^"]*">(.*?)</span>', card, re.S)
        it = {"page": slug, "name": clean(name.group(1)), "change": clean(chg.group(1)) if chg else "", "page_updated": page_upd}
        for lab, val in re.findall(r'<div class="kh-row"><span>(.*?)</span><strong>(.*?)</strong>', card, re.S):
            lab = clean(lab); v = parse_val(clean(val))
            key = "trader" if "التاجر" in lab else "retail" if "السريح" in lab else None
            if key and v:
                it[key] = {"low": v[0], "high": v[1]}; it["unit"] = v[2]
            elif key: it[key+"_text"] = clean(val)
        out.append(it)
    return out
if __name__ == "__main__":
    items, errs = [], []
    for s in PAGES:
        try: items += parse_page(s)
        except Exception as e: errs.append(f"{s}: {e}")
    json.dump({"source": "khurda.net", "source_url": BASE, "fetched": datetime.datetime.utcnow().isoformat()+"Z",
               "errors": errs, "items": items}, open(sys.argv[1] if len(sys.argv)>1 else "raw.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(items), "items;", len(errs), "errors", errs)
