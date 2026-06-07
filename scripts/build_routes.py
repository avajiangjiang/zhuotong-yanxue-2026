#!/usr/bin/env python3
"""从定稿 PPT 生成 routes.json 与图片资源"""
import zipfile, re, os, json
from xml.etree import ElementTree as ET

BASE = "/Users/ava/Desktop/研学项目/遂宁卓同2026年夏令营/定稿"
OUT = "/Users/ava/Desktop/路线方案"
NS_T = "{http://schemas.openxmlformats.org/drawingml/2006/main}t"

ROUTES = [
    ("yunnan", "彩云之南·研学之旅.pptx", "云南昆明", "三年级", "6天5夜", "#2d8f6f", "彩云之南·研学之旅"),
    ("xian", "走进古都西安 触摸历史脉搏.pptx", "西安", "四年级", "5天4夜", "#8b4513", "走进古都西安 触摸历史脉搏"),
    ("guizhou", "贵州·观天探地研学之旅.pptx", "贵州", "五年级", "5天4夜", "#c45c26", "贵州·观天探地研学之旅"),
    ("huhangsu", "少年怀当拏云志 研思笃学江南行.pptx", "沪杭苏", "初一年级", "7天6夜", "#1e6fa8", "少年怀当拏云志 研思笃学江南行"),
    ("nanjing", "南京研学之旅.pptx", "南京", "高一年级", "7天6夜", "#7b2d8e", "南京研学之旅"),
    ("shandong", "九年级-青烟威毕业之旅.pptx", "山东", "九年级", "6天5夜", "#0077b6", "山海之约 · 研学齐鲁"),
]

PERIODS = ("上午", "中午", "下午", "傍晚", "晚间", "晚上", "全天", "早间")
GAIN_KEYS = ("今日收获", "当日收获", "收获", "今日研学收获")
INFO_KEYS = {"住宿安排": "住宿", "交通安排": "交通", "全天行程": "行程"}
FIELD_PAIRS = {
    "交通安排": "交通", "研学主题": "主题", "研学总结": "总结",
    "课程目的地": "目的地", "火车出行": "活动", "团队破冰": "活动",
    "动车返程": "交通", "研学分享会": "活动", "研学证书颁发": "活动",
    "感恩与告别": "活动", "回到温暖的家": "活动",
}
CN_NUM = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}


def extract_slides(path):
    with zipfile.ZipFile(path) as z:
        names = sorted(
            [n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)],
            key=lambda x: int(re.search(r"slide(\d+)", x).group(1)),
        )
        out = []
        for name in names:
            root = ET.fromstring(z.read(name))
            parts = []
            for t in root.iter(NS_T):
                if t.text:
                    parts.append(t.text)
                if t.tail:
                    parts.append(t.tail)
            out.append("\n".join(x.strip() for x in parts if x and x.strip()))
        return out


def parse_day_number(lines):
    for i, line in enumerate(lines):
        m = re.match(r"^DAY\s*(\d+)\b", line, re.I)
        if m:
            return int(m.group(1)), i + 1
        if line == "DAY" and i + 1 < len(lines) and lines[i + 1].isdigit():
            return int(lines[i + 1]), i + 2
        m = re.match(r"^D(\d+)$", line)
        if m:
            return int(m.group(1)), i + 1
        m = re.match(r"^Day\s*(\d+)", line, re.I)
        if m:
            return int(m.group(1)), i + 1
        for cn, n in CN_NUM.items():
            if line == f"第{cn}天" or line.startswith(f"Day {n}") or line.startswith(f"Day {n} ·"):
                return n, i + 1
    return None, 0


def is_day_slide(text):
    if "行程总览" in text[:40] or "ITINERARY OVERVIEW" in text[:40]:
        return False
    if "7天6夜行程总览" in text[:20]:
        return False
    lines = text.split("\n")
    day, _ = parse_day_number(lines)
    return day is not None


def parse_day_slide(text):
    lines = [l.strip() for l in text.split("\n") if l.strip() and not re.match(r"^\d{2}$", l.strip())]
    day, start = parse_day_number(lines)
    if not day:
        return None

    i = start
    title_parts = []
    while i < len(lines):
        line = lines[i]
        if line in PERIODS or "傍" in line and "晚" in line:
            break
        key = line.rstrip("：")
        if key in GAIN_KEYS or key in INFO_KEYS:
            break
        if re.match(r"^[A-Z\s&·\.]+$", line) and len(line) < 30:
            i += 1
            continue
        if line.startswith("DAY ") or re.match(r"^D\d+$", line):
            i += 1
            continue
        title_parts.append(line)
        i += 1
        if len(title_parts) >= 2:
            break

    title = " · ".join(title_parts[:2]) if title_parts else f"第{day}天"
    subtitle = title_parts[1] if len(title_parts) > 1 and "·" not in title else ""

    schedule, gains, courses, content, activities, info = [], [], [], [], [], {}
    period, buf = None, []
    section, section_buf = None, []

    def flush_period():
        nonlocal period, buf
        if period and buf:
            schedule.append(f"{period}：{''.join(buf)}")
        period, buf = None, []

    def flush_section():
        nonlocal section, section_buf
        if not section or not section_buf:
            section, section_buf = None, []
            return
        text = "".join(section_buf).strip().lstrip("：")
        if section == "gains" and text:
            gains.append(text)
        elif section == "courses" and text:
            courses.append(text)
        elif section == "content" and text:
            content.append(text)
        elif section in info and text:
            info[section] = text
        section, section_buf = None, []

    while i < len(lines):
        line = lines[i]

        if line in PERIODS or ("傍" in line and "晚" in line):
            flush_section()
            flush_period()
            period = "傍晚" if "傍" in line else line
            i += 1
            continue

        key = line.rstrip("：")
        if key in GAIN_KEYS:
            flush_period()
            flush_section()
            section = "gains"
            section_buf = []
            if "：" in line:
                rest = line.split("：", 1)[1]
                if rest:
                    section_buf.append(rest)
            i += 1
            continue

        if key in INFO_KEYS:
            flush_period()
            flush_section()
            section = INFO_KEYS[key]
            section_buf = []
            i += 1
            continue

        if key in ("课程目标", "课程内容", "学科链接", "课本链接"):
            flush_period()
            flush_section()
            section = "courses"
            section_buf = []
            if "：" in line and line.split("：", 1)[1]:
                section_buf.append(line.split("：", 1)[1])
            i += 1
            continue

        if line.startswith("• ") or line.startswith("· "):
            item = line[2:]
            if section == "gains":
                gains.append(item)
            elif section == "courses":
                courses.append(item)
            elif period:
                buf.append(item)
            else:
                content.append(item)
            i += 1
            continue

        if line in ("知识层面", "技能层面", "情感层面", "研学收获", "课程目的地"):
            flush_period()
            i += 1
            continue

        if period:
            buf.append(line)
        elif section:
            section_buf.append(line)
        i += 1

    flush_period()
    flush_section()

    # 无上午/下午结构：按字段标签或纯文本补全
    if not schedule:
        i = start
        while i < len(lines):
            line = lines[i]
            if line in FIELD_PAIRS:
                label = FIELD_PAIRS[line]
                if i + 1 < len(lines) and lines[i + 1] not in FIELD_PAIRS and lines[i + 1] not in GAIN_KEYS:
                    val = lines[i + 1]
                    if label:
                        schedule.append(f"{label}：{val}")
                    else:
                        schedule.append(val)
                    i += 2
                    continue
            if line.startswith("目的地：") or line.startswith("含") and "餐" in line:
                schedule.append(line)
            elif line.endswith("酒店") or line.endswith("酒店。"):
                info.setdefault("住宿", line)
            i += 1

    if not schedule and len(lines) > start + 2:
        body = [l for l in lines[start + len(title_parts) :] if l not in GAIN_KEYS and l.rstrip("：") not in GAIN_KEYS and l.rstrip("：") not in INFO_KEYS and l not in FIELD_PAIRS and not re.match(r"^[A-Z\s·\.]+$", l) and len(l) > 6]
        for line in body[:4]:
            if line.startswith("今日收获"):
                gains.append(line.split("：", 1)[1] if "：" in line else "")
            elif not line.startswith("DAY"):
                schedule.append(line)

    if "全天" in text and not any(s.startswith("全天：") for s in schedule):
        for line in lines:
            if line == "全天" and "迪士尼" in title:
                schedule.insert(0, f"全天：上海迪士尼乐园")
                break

    return {
        "day": day,
        "title": title,
        "subtitle": subtitle,
        "schedule": schedule,
        "courses": courses,
        "gains": gains,
        "activities": activities,
        "info": info,
        "content": content,
    }


def parse_goals(slides):
    for s in slides:
        if not any(k in s for k in ("知识目标", "课程目标", "COURSE OBJECTIVES", "文化基础")):
            continue
        goals = {}
        labels = {
            "知识目标": "知识", "能力目标": "能力", "情感目标": "情感", "实践目标": "实践",
            "历史人文": "历史人文", "科技探索": "科技探索", "爱国教育": "爱国教育",
            "名校体验": "名校体验", "综合素养": "综合素养", "知识": "知识", "能力": "能力",
            "情感": "情感", "态度": "态度", "文化基础": "文化基础", "自主发展": "自主发展",
        }
        current = None
        for line in s.split("\n"):
            matched = False
            for k, v in labels.items():
                if line == k or line.startswith(k + " "):
                    current = v
                    goals[current] = ""
                    matched = True
                    break
            if not matched and current and len(line) > 8:
                if goals[current]:
                    goals[current] += line
                else:
                    goals[current] = line
                current = None
        if goals:
            return goals
    return {}


def parse_highlights(slides):
    for s in slides:
        if not any(k in s for k in ("特色项目", "特色研学", "FEATURED", "六大特色", "五大特色")):
            continue
        lines = [l.strip() for l in s.split("\n") if l.strip()]
        out = []
        i = 0
        while i < len(lines):
            if re.match(r"^0?\d$", lines[i]) and i + 2 < len(lines):
                out.append({"title": lines[i + 1], "summary": lines[i + 2]})
                i += 3
            elif 4 < len(lines[i]) < 20 and i + 1 < len(lines) and len(lines[i + 1]) > 15:
                if lines[i] not in ("特色项目", "特色研学项目", "六大特色项目"):
                    out.append({"title": lines[i], "summary": lines[i + 1]})
                i += 2
            else:
                i += 1
        if out:
            return out[:6]
    return []


def parse_services(slides):
    dining = ["社会餐厅/特色餐相结合", "品尝当地特色美食", "含全程用餐"]
    lodging = ["准四星/三钻及以上酒店", "安全舒适，生活老师全程管理"]
    for s in slides:
        if "住宿" not in s and "餐饮" not in s and "生活保障" not in s:
            continue
        d, l = [], []
        mode = None
        for line in s.split("\n"):
            if "餐饮" in line:
                mode = "d"
            elif "住宿" in line and "保障" not in line:
                mode = "l"
            elif line.startswith("● ") or line.startswith("• "):
                (d if mode == "d" else l).append(line[2:])
            elif mode == "l" and len(line) > 10:
                l.append(line)
        if d:
            dining = d
        if l:
            lodging = l
        break
    return {
        "dining": dining,
        "lodging": lodging,
        "safety": [
            {"title": "专业导师团队", "desc": "研学导师+生活老师+随队医生"},
            {"title": "高师生配比", "desc": "师生比不低于1:10"},
            {"title": "交通保障", "desc": "正规旅游大巴，经验丰富司机"},
            {"title": "应急预案", "desc": "完善的安全预案"},
        ],
    }


def get_slide_image(z, slide_num):
    rels_path = f"ppt/slides/_rels/slide{slide_num}.xml.rels"
    if rels_path not in z.namelist():
        return None
    root = ET.fromstring(z.read(f"ppt/slides/slide{slide_num}.xml"))
    embed_ids = []
    for blip in root.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}blip"):
        eid = blip.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed")
        if eid:
            embed_ids.append(eid)
    rels = ET.fromstring(z.read(rels_path))
    rid_map = {r.get("Id"): r.get("Target") for r in rels if r.get("Type", "").endswith("/image")}
    best = None
    for eid in embed_ids:
        target = rid_map.get(eid)
        if not target:
            continue
        mp = "ppt/" + target.replace("../", "")
        if mp in z.namelist():
            data = z.read(mp)
            if len(data) > 1000 and (best is None or len(data) > len(best[1])):
                best = (mp, data)
    return best


def extract_images(slug, path, days, slides):
    img_dir = os.path.join(OUT, "assets/images", slug)
    os.makedirs(img_dir, exist_ok=True)
    for f in os.listdir(img_dir):
        os.remove(os.path.join(img_dir, f))

    day_images, cover = {}, None
    with zipfile.ZipFile(path) as z:
        media_pool = [(n, z.read(n)) for n in sorted(x for x in z.namelist() if x.startswith("ppt/media/") and not x.endswith("/")) if len(z.read(n)) > 1000]
        # fix double read
        media_pool = []
        for n in sorted(x for x in z.namelist() if x.startswith("ppt/media/") and not x.endswith("/")):
            data = z.read(n)
            if len(data) > 1000:
                media_pool.append((n, data))

        c = get_slide_image(z, 1) or get_slide_image(z, 4) or (media_pool[0] if media_pool else None)
        if c:
            ext = os.path.splitext(c[0])[1] or ".png"
            cover = f"assets/images/{slug}/cover{ext}"
            with open(os.path.join(OUT, cover), "wb") as f:
                f.write(c[1])

        for idx, slide_text in enumerate(slides, 1):
            if not is_day_slide(slide_text):
                continue
            day = parse_day_number(slide_text.split("\n"))[0]
            img = get_slide_image(z, idx)
            if img and day:
                ext = os.path.splitext(img[0])[1] or ".png"
                rel = f"assets/images/{slug}/day-{day:02d}{ext}"
                with open(os.path.join(OUT, rel), "wb") as f:
                    f.write(img[1])
                day_images[day] = rel

    max_day = max(d["day"] for d in days) if days else 0
    pi = 0
    for d in range(1, max_day + 1):
        if d not in day_images and media_pool:
            mp, data = media_pool[pi % len(media_pool)]
            ext = os.path.splitext(mp)[1] or ".png"
            rel = f"assets/images/{slug}/day-{d:02d}{ext}"
            with open(os.path.join(OUT, rel), "wb") as f:
                f.write(data)
            day_images[d] = rel
            pi += 1

    for day in days:
        day["image"] = day_images.get(day["day"])

    images = ([cover] if cover else []) + [day_images[k] for k in sorted(day_images) if day_images[k] != cover]
    return cover, images


def build_route(cfg):
    slug, fname, dest, grade, duration, color, display_title = cfg
    path = os.path.join(BASE, fname)
    slides = extract_slides(path)

    dest_desc, dest_title = "", dest
    for s in slides[2:7]:
        if any(k in s for k in ("概览", "OVERVIEW", "城市")):
            lines = [l for l in s.split("\n") if len(l) > 15]
            if lines:
                dest_desc = lines[0][:500]
            for l in s.split("\n"):
                if "·" in l and len(l) < 40:
                    dest_title = l
                    break
            break

    days = []
    seen = {}
    for s in slides:
        if not is_day_slide(s):
            continue
        d = parse_day_slide(s)
        if d and (d["schedule"] or d["gains"] or d["courses"]):
            seen[d["day"]] = d
    days = [seen[k] for k in sorted(seen)]

    cover, images = extract_images(slug, path, days, slides)

    return {
        "id": slug,
        "title": display_title,
        "tagline": "遂宁卓同集团2026夏季研学营",
        "destination": dest,
        "destinationTitle": dest_title,
        "destinationDesc": dest_desc or f"走进{dest}，开启精彩研学之旅。",
        "badges": [duration, grade],
        "grade": grade,
        "duration": duration,
        "color": color,
        "cover": cover,
        "images": images,
        "goals": parse_goals(slides),
        "highlights": parse_highlights(slides),
        "days": days,
        "services": parse_services(slides),
        "cta": f"{dest.split('·')[0]}，等你出发",
    }


def main():
    grade_order = {"三年级": 3, "四年级": 4, "五年级": 5, "六年级": 6, "初一年级": 6.5, "七年级": 7, "八年级": 8, "九年级": 9, "高一年级": 10}
    routes = [build_route(cfg) for cfg in ROUTES]
    routes.sort(key=lambda r: grade_order.get(r["grade"], 99))

    data = {"brand": "遂宁卓同集团2026夏季研学营", "contactPhone": "请咨询学校研学负责人", "routes": routes}
    os.makedirs(os.path.join(OUT, "data"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "js"), exist_ok=True)
    with open(os.path.join(OUT, "data/routes.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with open(os.path.join(OUT, "js/data.js"), "w", encoding="utf-8") as f:
        f.write("window.ROUTES_DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n")

    for r in routes:
        print(f"{r['id']}: {r['title']} | {len(r['days'])} days")
        d1 = r["days"][0]
        print(f"  D1 schedule={len(d1['schedule'])} gains={len(d1['gains'])}")


if __name__ == "__main__":
    main()
