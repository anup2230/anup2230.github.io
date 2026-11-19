"""Refresh lighting.json from BOMA/Chicago's Illuminate Chicago program.

BOMA/Chicago coordinates the colors of the downtown skyline and lists the upcoming
requests on its site. This script reads that list, turns each entry into
{start, end, cause, colors}, merges it with what lighting.json already holds, and
drops entries that ended more than a year ago. The page reads lighting.json to pick
tonight's colors and falls back to its built-in calendar for anything missing.
"""
import datetime as dt
import html
import json
import re
import sys
import urllib.request

SOURCE = "https://www.bomachicago.org/illuminate-chicago-lighting-program/"
OUT = "lighting.json"

MONTHS = {m: i for i, m in enumerate(
    "january february march april may june july august september october november december".split(), 1)}
MONTHS.update({k[:3]: v for k, v in list(MONTHS.items())})
MONTHS["sept"] = 9

# Color words BOMA uses, mapped to the hex the page draws with.
COLORS = [
    ("chicago flag blue", "#B3DDF2"), ("chicago star red", "#E4243B"), ("light blue", "#B3DDF2"),
    ("navy", "#1F3A93"), ("turquoise", "#2EC4C9"), ("teal", "#1FB5AD"), ("purple", "#9B4DFF"),
    ("lavender", "#B58CFF"), ("pink", "#FF6FB5"), ("magenta", "#E040A0"), ("red", "#E4243B"),
    ("maroon", "#8C1D3B"), ("orange", "#FF8A2A"), ("gold", "#F2B632"), ("yellow", "#FFD21F"),
    ("lime", "#9BE24A"), ("green", "#2FBF5B"), ("blue", "#2C6BFF"), ("white", "#F6F8FC"),
    ("silver", "#C9D0DA"), ("black", "#3A3F4C"),
]
RAINBOW = ["#E40303", "#FF8C00", "#FFED00", "#008026", "#004DFF", "#750787"]


def colors_from(text):
    t = text.lower()
    if "rainbow" in t:
        return RAINBOW
    found = []
    for word, hexv in COLORS:
        for m in re.finditer(r"\b" + re.escape(word) + r"\b", t):
            found.append((m.start(), hexv))
            t = t[:m.start()] + " " * len(word) + t[m.end():]  # stop "blue" re-matching inside "light blue"
    return [h for _, h in sorted(found)]


def parse_dates(text, today):
    """Handle 'November 14-20', 'December 14 - January 3', 'September 30, 2026',
    'October 16 - November 2, 2026', 'May 1, 2024 - May 6, 2024' and 'Month of June 2024'."""
    t = re.sub(r"\(.*?\)", "", text).replace("–", "-").replace("—", "-").strip()
    m = re.match(r"month of (\w+)\s*(\d{4})?", t, re.I)
    if m and m.group(1).lower() in MONTHS:
        mo = MONTHS[m.group(1).lower()]
        y = int(m.group(2)) if m.group(2) else today.year
        end = (dt.date(y, mo % 12 + 1, 1) if mo < 12 else dt.date(y + 1, 1, 1)) - dt.timedelta(days=1)
        return dt.date(y, mo, 1), end
    tok = r"([A-Za-z]+)\.?\s+(\d{1,2})(?:st|nd|rd|th)?(?:,\s*(\d{4}))?"
    m = re.match(tok + r"\s*(?:-\s*(?:" + tok + r"|(\d{1,2})(?:,\s*(\d{4}))?))?", t)
    if not m or m.group(1).lower() not in MONTHS:
        return None
    m1, d1, y1 = MONTHS[m.group(1).lower()], int(m.group(2)), m.group(3)
    if m.group(4) and m.group(4).lower() in MONTHS:
        m2, d2, y2 = MONTHS[m.group(4).lower()], int(m.group(5)), m.group(6)
    elif m.group(7):
        m2, d2, y2 = m1, int(m.group(7)), m.group(8)
    else:
        m2, d2, y2 = m1, d1, y1
    y2 = int(y2) if y2 else (int(y1) if y1 else None)
    y1 = int(y1) if y1 else None
    if y1 is None and y2 is not None:
        y1 = y2 - 1 if (m1, d1) > (m2, d2) else y2
    if y1 is None:  # no year given: the next time this range comes around
        y1 = today.year
        if dt.date(y1, m2, d2) < today - dt.timedelta(days=7) and (m1, d1) <= (m2, d2):
            y1 += 1
        y2 = y1 + 1 if (m1, d1) > (m2, d2) else y1
    try:
        return dt.date(y1, m1, d1), dt.date(y2, m2, d2)
    except ValueError:
        return None


def text_lines(page):
    page = re.sub(r"(?is)<(script|style|noscript).*?</\1>", " ", page)
    page = re.sub(r"(?i)<br\s*/?>|</(p|div|li|h\d|tr)>", "\n", page)
    page = html.unescape(re.sub(r"<[^>]+>", " ", page))
    return [re.sub(r"\s+", " ", l).strip() for l in page.splitlines() if l.strip()]


def scrape(page, today):
    lines = text_lines(page)
    entries = []
    for i, line in enumerate(lines):
        m = re.match(r"dates?\s*:\s*(.+)", line, re.I)
        if not m:
            continue
        dates = parse_dates(m.group(1), today)
        # the cause is the nearest line above that isn't a field like "Sponsor:"
        cause = next((lines[j] for j in range(i - 1, max(i - 4, -1), -1)
                      if not re.match(r"(sponsor|colou?rs?|phrase|contact|website|dates?)\s*:", lines[j], re.I)), None)
        colors_line = next((lines[j] for j in range(i + 1, min(i + 5, len(lines)))
                            if re.match(r"colou?rs?\s*:", lines[j], re.I)), None)
        if not dates or not cause or not colors_line:
            continue
        cols = colors_from(colors_line.split(":", 1)[1])
        if not cols:
            continue
        entries.append({"start": dates[0].isoformat(), "end": dates[1].isoformat(),
                        "cause": cause, "colors": cols})
    return entries


def main():
    today = dt.date.today()
    req = urllib.request.Request(SOURCE, headers={"User-Agent": "anup2230.github.io skyline sync"})
    page = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    fresh = scrape(page, today)
    if not fresh:
        print("No entries found on BOMA's page; leaving lighting.json unchanged.")
        return 0
    try:
        old = json.load(open(OUT))
    except (OSError, ValueError):
        old = []
    keep = {(e["start"], e["cause"]): e for e in old
            if dt.date.fromisoformat(e["end"]) >= today - dt.timedelta(days=365)}
    for e in fresh:
        keep[(e["start"], e["cause"])] = e
    merged = sorted(keep.values(), key=lambda e: (e["start"], e["end"]))
    with open(OUT, "w") as f:
        json.dump(merged, f, indent=1)
        f.write("\n")
    print(f"{len(fresh)} entries from BOMA, {len(merged)} in lighting.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
