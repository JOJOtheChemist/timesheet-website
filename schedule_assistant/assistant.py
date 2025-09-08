#!/usr/bin/env python3

import sys
import json
import re
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from difflib import SequenceMatcher

MCP_HTTP_URL = "http://127.0.0.1:8001/api/mcp"

# -----------------------------
# Utilities
# -----------------------------

def post_mcp(method: str, params: Dict[str, Any]) -> Dict[str, Any]:
    payload = {
        "jsonrpc": "2.0",
        "id": f"assistant_{int(datetime.now().timestamp())}",
        "method": method,
        "params": params,
    }
    response = requests.post(MCP_HTTP_URL, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def mcp_tools_call(name: str, arguments: Dict[str, Any]) -> Any:
    """Call MCP tools/call and return parsed JSON content."""
    result = post_mcp("tools/call", {"name": name, "arguments": arguments})
    content = result.get("result", {}).get("content") or result.get("result", {}).get("contents")
    if not content:
        return None
    item = content[0]
    text = item.get("text") or item.get("value")
    try:
        return json.loads(text)
    except Exception:
        return text


def get_all_projects() -> List[Dict[str, Any]]:
    data = mcp_tools_call("get_projects", {})
    return data or []


def get_schedule_for_date(date_str: str) -> List[Dict[str, Any]]:
    data = mcp_tools_call("get_schedule", {"date": date_str})
    return data or []


def create_schedule_row(schedule_date: str, time_slot: str, planned_subtask_id: Optional[int] = None,
                        planned_notes: Optional[str] = None, actual_subtask_id: Optional[int] = None,
                        actual_notes: Optional[str] = None, mood: Optional[str] = None) -> Dict[str, Any]:
    args = {
        "schedule_date": schedule_date,
        "time_slot": time_slot,
        "planned_subtask_id": planned_subtask_id,
        "planned_notes": planned_notes,
        "actual_subtask_id": actual_subtask_id,
        "actual_notes": actual_notes,
        "mood": mood,
    }
    return mcp_tools_call("create_schedule", args) or {}


def best_match_subtask(projects: List[Dict[str, Any]], query: str) -> Optional[Tuple[int, str]]:
    """Return (subtask_id, subtask_name) with best similarity to query."""
    best_score = 0.0
    best_pair: Optional[Tuple[int, str]] = None
    query_norm = query.lower()

    synonyms = {
        "agent": ["agent", "智能体", "代理", "大模型智能体", "智能代理"],
        "后端开发": ["后端开发", "后端", "服务端", "server", "backend", "api", "数据库", "数据库设计"],
        "睡觉": ["睡觉", "睡", "休息", "sleep"],
        "起床": ["起床", "醒来", "wake"],
    }
    # Expand query with synonyms to improve matching
    expanded_queries = [query_norm]
    for key, words in synonyms.items():
        if any(w in query_norm for w in words):
            expanded_queries.extend(words)

    for category in projects:
        for project in category.get("projects", []):
            for st in project.get("subtasks", []):
                name = str(st.get("name", ""))
                name_norm = name.lower()
                for eq in expanded_queries:
                    score = SequenceMatcher(None, eq, name_norm).ratio()
                    if score > best_score:
                        best_score = score
                        best_pair = (int(st.get("id")), name)
    return best_pair


def parse_datetime_phrase(text: str, now: Optional[datetime] = None) -> List[Tuple[str, datetime]]:
    """Parse simple Chinese date-time phrases, returns list of (label, datetime).
    Recognizes: 今天/昨晚/昨天/明天 + HH点[半]. Labels may include keywords like '睡觉','起床'.
    """
    if now is None:
        now = datetime.now()

    # Normalize text
    t = text.replace("，", ",").replace("、", ",").replace("。", ",")

    results: List[Tuple[str, datetime]] = []
    parts = [p.strip() for p in t.split(",") if p.strip()]

    def base_date(token: str) -> datetime:
        if token.startswith("今天") or token.startswith("今早") or token.startswith("今日"):
            return now
        if token.startswith("昨晚") or token.startswith("昨天") or token.startswith("昨夜"):
            return now - timedelta(days=1)
        if token.startswith("明天") or token.startswith("明早"):
            return now + timedelta(days=1)
        return now

    time_pat = re.compile(r"(?P<h>\d{1,2})点(?P<half>半)?")

    for p in parts:
        bd = base_date(p)
        m = time_pat.search(p)
        if m:
            hour = int(m.group("h"))
            minute = 30 if m.group("half") else 0
            dt = bd.replace(hour=hour, minute=minute, second=0, microsecond=0)
            label = ""
            if "睡" in p:
                label = "睡觉"
            elif "起床" in p or "醒" in p:
                label = "起床"
            else:
                # if it mentions study/research/agent
                if any(k in p for k in ["研究", "学习", "agent", "智能体", "后端", "开发"]):
                    label = "计划"
            results.append((label, dt))
        else:
            # notes without explicit time
            if "睡" in p:
                results.append(("睡觉", bd))
            elif "起床" in p or "醒" in p:
                results.append(("起床", bd))
            elif any(k in p for k in ["研究", "学习", "agent", "智能体", "后端", "开发"]):
                results.append(("计划", bd))
    return results


def generate_half_hour_slots(start_dt: datetime, end_dt: datetime) -> List[str]:
    slots: List[str] = []
    cur = start_dt
    while cur < end_dt:
        slots.append(cur.strftime("%H:%M"))
        cur += timedelta(minutes=30)
    return slots


# -----------------------------
# ReAct agent
# -----------------------------

def react_handle(text: str, dry_run: bool = False) -> None:
    now = datetime.now()
    print(f"Thought: Received input -> {text}")

    # Step 1: Understand intents and time points
    print("Thought: Parse time phrases and intents")
    events = parse_datetime_phrase(text, now=now)
    for label, dt in events:
        print(f"Observation: {label or '未知'} @ {dt.strftime('%Y-%m-%d %H:%M')}")

    # Step 2: Fetch projects/subtasks for mapping
    print("Action: tools/call get_projects")
    projects = get_all_projects()
    print(f"Observation: Loaded {sum(len(c.get('projects', [])) for c in projects)} projects")

    # Extract auxiliary notes
    notes = []
    if "asmr" in text.lower() or "ASMR" in text:
        if "抖音" in text:
            notes.append("抖音听asmr睡着")
        else:
            notes.append("听asmr睡着")

    # Step 3: Determine actions
    # - If we have a pair of (睡觉 -> 起床), fill each 30-min slot as actual_subtask = 睡觉
    # - If we have '计划 ... agent/研究/后端开发', select best subtask and create planned entries around now
    sleeps = [dt for label, dt in events if label == "睡觉"]
    wakes = [dt for label, dt in events if label == "起床"]
    plans = [dt for label, dt in events if label == "计划"]

    # Find subtask ids
    sleep_match = best_match_subtask(projects, "睡觉")
    plan_match = None
    if any(k in text for k in ["agent", "智能体"]):
        plan_match = best_match_subtask(projects, "后端开发") or best_match_subtask(projects, "后端和数据库设计")
    else:
        plan_match = best_match_subtask(projects, "后端开发")

    # Step 4: Execute schedule writes
    if sleeps:
        # Pair sleeps to wake; if wake missing, default to next day morning 08:00
        for sdt in sleeps:
            edt = None
            cands = [w for w in wakes if w > sdt]
            if cands:
                edt = min(cands)
            else:
                # default end 08:00 next day
                edt = (sdt + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)

            date_cursor = sdt
            while date_cursor.date() <= edt.date():
                day_start = date_cursor
                day_end = edt if edt.date() == date_cursor.date() else date_cursor.replace(hour=23, minute=59)
                slots = generate_half_hour_slots(day_start, day_end)
                for slot in slots:
                    ds = day_start.strftime("%Y-%m-%d")
                    if dry_run:
                        print(f"Would create actual sleep slot: {ds} {slot} -> subtask={sleep_match}")
                    else:
                        sid = sleep_match[0] if sleep_match else None
                        note = "; ".join(notes) if notes else None
                        print(f"Action: tools/call create_schedule for sleep {ds} {slot}")
                        create_schedule_row(
                            schedule_date=ds,
                            time_slot=slot,
                            actual_subtask_id=sid,
                            actual_notes=note,
                        )
                date_cursor = (date_cursor + timedelta(days=1)).replace(hour=0, minute=0)

    if plans:
        # Create a small planned window starting next half-hour for 1 hour
        for pdt in plans:
            start = pdt
            minute = 0 if pdt.minute < 30 else 30
            start = pdt.replace(minute=minute, second=0, microsecond=0)
            end = start + timedelta(hours=1)
            slots = generate_half_hour_slots(start, end)
            for slot in slots:
                ds = start.strftime("%Y-%m-%d")
                if dry_run:
                    print(f"Would create planned slot: {ds} {slot} -> subtask={plan_match}")
                else:
                    pid = plan_match[0] if plan_match else None
                    note = "agent相关研究" if any(k in text for k in ["agent", "智能体"]) else "研究/开发"
                    print(f"Action: tools/call create_schedule for plan {ds} {slot}")
                    create_schedule_row(
                        schedule_date=ds,
                        time_slot=slot,
                        planned_subtask_id=pid,
                        planned_notes=note,
                    )

    # Report missing subtask creation capability
    if (not plan_match) and plans:
        print("Observation: 未找到合适的子任务用于计划。需要创建新子任务。")
        print("Note: 现有API未提供创建子任务接口，请在项目管理中先创建该子任务后再重试。")

    print("Thought: Done")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 assistant.py '<自然语言指令>' [--dry-run]")
        sys.exit(1)
    text = sys.argv[1]
    dry = "--dry-run" in sys.argv[2:]
    react_handle(text, dry_run=dry) 