#!/usr/bin/env python3
import sys, json, collections, pathlib

if len(sys.argv) < 2:
    print("Usage: count_metadata_years.py <jsonl-file> [...]")
    sys.exit(2)

for path in sys.argv[1:]:
    p = pathlib.Path(path)
    if not p.exists():
        print(f"missing:\t{path}")
        continue
    counts = collections.Counter()
    total = 0
    with p.open('r', encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception as e:
                continue
            total += 1
            # prefer ro_date then issue_date then date
            for key in ('ro_date','issue_date','date','crawl_date'):
                if key in obj:
                    val = obj[key]
                    break
            else:
                val = None
            year = 'unknown'
            if val:
                year = str(val)[:4]
            counts[year] += 1
    print(f"{path}\ttotal={total}")
    for year, cnt in sorted(counts.items(), reverse=True):
        print(f"{path}\t{year}\t{cnt}")
    print()
