#!/usr/bin/env python3
"""Runs scrape.py, maps khurda.net items to the dashboard ids, writes prices.json.
Fails (exit 1, keeps old prices.json) if too few items parse, so a layout change never publishes garbage."""
import json, sys, datetime, scrape
MAP = {  # dashboard id -> exact khurda.net item name
 "fe-mix":"حديد خليط","fe-top":"حديد تقيل (مسلح – مواسير – كمر)",
 "cu-red":"نحاس أحمر لامع (كابلات)","cu-yel":"نحاس أصفر",
 "al-soft":"ألمنيوم طري (حلل وطشوت)","al-hard":"ألمنيوم ناشف",
 "pb":"رصاص","bat":"بطاريات عربيات (رصاص حمضية)",
 "ss201":"استانلس 201","ss304":"استانلس 304","ss316":"استانلس 316",
 "pl":"بلاستيك صلب (أزايز وأزارة)",
 "ap-fridge":"تلاجة خردة","ap-wash":"غسالة عادي – موتور سليم","ap-motor":"مواتير عادية",
}
NOSRC = ["fe-ton","ap-wash-a","ap-stove","ap-heater","ap-ac","ap-fan","el-board","el-ram","el-cpu","el-case",
         "el-lap","el-hdd-l","el-hdd-p","el-bat","el-ph-k","el-ph-a","el-ph-b"]
items, errs = [], []
for s in scrape.PAGES:
    try: items += scrape.parse_page(s)
    except Exception as e: errs.append(f"{s}: {e}")
by = {i["name"]: i for i in items}
prices, hi, changes, dates = {}, {}, {}, []
for did, name in MAP.items():
    it = by.get(name)
    if not it or "trader" not in it: errs.append(f"missing {did} <- {name}"); continue
    prices[did] = it["trader"]["low"]
    if it["trader"]["high"] != it["trader"]["low"]: hi[did] = it["trader"]["high"]
    else: hi[did] = None
    changes[did] = it["change"]
    if it["page_updated"]: dates.append(it["page_updated"])
if len(prices) < len(MAP) - 2 or not dates:
    print("TOO MANY MISSING, not publishing:", errs); sys.exit(1)
out = {"source":"khurda.net","source_url":"https://khurda.net/","price_basis":"سعر التاجر (للكميات من 100 كيلو فأكثر)، استرشادي",
       "updated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
       "source_updated": max(dates), "prices": prices, "hi": hi, "source_status": changes,
       "no_source": NOSRC, "warnings": errs}
json.dump(out, open("prices.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok", len(prices), "prices; warnings:", errs)
