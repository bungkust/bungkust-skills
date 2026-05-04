#!/usr/bin/env python3
"""
Hermes Cost Logger — inspired by CodeBurn concepts.
Tracks AI token costs, breakdown by model/source/activity, budget alerts.

Usage:
  python3 cost-logger.py                    # Summary report (today + all-time)
  python3 cost-logger.py today              # Today only
  python3 cost-logger.py week               # Last 7 days
  python3 cost-logger.py month              # This month
  python3 cost-logger.py report             # Full dashboard report
  python3 cost-logger.py report --json      # JSON export
  python3 cost-logger.py status             # One-liner status
  python3 cost-logger.py budget 50          # Set daily budget $50
  python3 cost-logger.py export csv         # Export to CSV
"""

import sqlite3
import json
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional

# === Config ===
DB_PATH = Path.home() / ".hermes" / "state.db"
CONFIG_PATH = Path.home() / ".hermes" / "cost-logger.json"

DEFAULT_CONFIG = {
    "daily_budget_usd": None,
    "monthly_budget_usd": None,
    "alert_threshold_pct": 80,
    "currency": "USD",
    "currency_rates": {},
}

# === Activity Classifier (CodeBurn-inspired) ===
ACTIVITY_KEYWORDS = {
    "Coding": ["edit", "write_file", "patch"],
    "Debugging": ["fix", "debug", "error", "bug"],
    "Feature Dev": ["create", "implement", "add", "build"],
    "Refactoring": ["refactor", "rename", "simplify", "clean"],
    "Testing": ["test", "pytest", "vitest", "jest"],
    "Exploration": ["read_file", "search_files", "browser", "web_search"],
    "Planning": ["plan", "writing-plans", "todo"],
    "Delegation": ["delegate_task"],
    "Git Ops": ["git", "commit", "push", "merge", "pr"],
    "Build/Deploy": ["deploy", "docker", "build", "install"],
    "Communication": ["send_message", "clarify", "text_to_speech"],
    "Data/Analysis": ["execute_code", "jupyter"],
    "General": [],
}

# === Token Cost Estimator (for free models) ===
# Reference pricing per 1M tokens (USD) — used to estimate "theoretical" cost
REFERENCE_PRICING = {
    # Model patterns -> (input_per_1M, output_per_1M)
    "mimo":        (0.00, 0.00),   # Free
    "gpt-4o":      (2.50, 10.00),
    "gpt-5":       (5.00, 15.00),
    "gpt-5.4":     (5.00, 15.00),
    "claude-sonnet": (3.00, 15.00),
    "claude-opus":  (15.00, 75.00),
    "claude-haiku": (0.25, 1.25),
    "gemini":      (0.00, 0.00),   # Varies, often free
    "glm":         (0.00, 0.00),   # Free tier
    "deepseek":    (0.14, 0.28),
    "llama":       (0.00, 0.00),   # Self-hosted
    "qwen":        (0.00, 0.00),   # Free tier
}

def estimate_cost_if_paid(model: str, input_tok: int, output_tok: int) -> float:
    """Estimate theoretical cost if model wasn't free."""
    model_lower = (model or "").lower()
    for pattern, (in_price, out_price) in REFERENCE_PRICING.items():
        if pattern in model_lower:
            return (input_tok / 1_000_000 * in_price) + (output_tok / 1_000_000 * out_price)
    # Default: assume GPT-4o pricing for unknown models
    return (input_tok / 1_000_000 * 2.50) + (output_tok / 1_000_000 * 10.00)

# === Helpers ===

def load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    return DEFAULT_CONFIG.copy()

def save_config(config: dict):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)

def get_db():
    if not DB_PATH.exists():
        print(f"❌ Database not found: {DB_PATH}")
        sys.exit(1)
    return sqlite3.connect(str(DB_PATH))

def classify_activity(tool_name: str) -> str:
    """Classify a tool call into an activity category."""
    tool_lower = tool_name.lower()
    for activity, keywords in ACTIVITY_KEYWORDS.items():
        if activity == "General":
            continue
        for kw in keywords:
            if kw in tool_lower:
                return activity
    return "General"

def fmt_usd(amount: float, currency: str = "USD") -> str:
    """Format currency."""
    if currency == "USD":
        return f"${amount:.4f}" if amount < 0.01 else f"${amount:.2f}"
    return f"{amount:.2f} {currency}"

def fmt_tokens(n: int) -> str:
    """Format token count."""
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)

def bar(pct: float, width: int = 15) -> str:
    """Simple text progress bar."""
    filled = int(pct / 100 * width)
    return "█" * filled + "░" * (width - filled)

# === Core Queries ===

def query_sessions(conn, days: Optional[int] = None, source: Optional[str] = None):
    """Query sessions with optional filters."""
    query = """
        SELECT id, source, model, started_at, ended_at,
               message_count, tool_call_count,
               input_tokens, output_tokens, cache_read_tokens, cache_write_tokens, reasoning_tokens,
               estimated_cost_usd, actual_cost_usd, cost_status
        FROM sessions
        WHERE 1=1
    """
    params = []

    if days:
        cutoff = (datetime.now() - timedelta(days=days)).timestamp()
        query += " AND started_at >= ?"
        params.append(cutoff)

    if source:
        query += " AND source = ?"
        params.append(source)

    query += " ORDER BY started_at DESC"
    return conn.execute(query, params).fetchall()

def query_daily_breakdown(conn, days: int = 30):
    """Get daily cost breakdown."""
    cutoff = (datetime.now() - timedelta(days=days)).timestamp()
    rows = conn.execute("""
        SELECT
            date(started_at, 'unixepoch', 'localtime') as day,
            COUNT(*) as sessions,
            SUM(input_tokens) as input_tok,
            SUM(output_tokens) as output_tok,
            SUM(cache_read_tokens) as cache_read,
            SUM(cache_write_tokens) as cache_write,
            SUM(estimated_cost_usd) as cost
        FROM sessions
        WHERE started_at >= ?
        GROUP BY day
        ORDER BY day DESC
    """, [cutoff]).fetchall()
    return rows

def query_model_breakdown(conn, days: Optional[int] = None):
    """Get per-model breakdown."""
    query = """
        SELECT
            model,
            COUNT(*) as sessions,
            SUM(input_tokens) as input_tok,
            SUM(output_tokens) as output_tok,
            SUM(cache_read_tokens) as cache_read,
            SUM(estimated_cost_usd) as cost
        FROM sessions
        WHERE 1=1
    """
    params = []
    if days:
        cutoff = (datetime.now() - timedelta(days=days)).timestamp()
        query += " AND started_at >= ?"
        params.append(cutoff)

    query += " GROUP BY model ORDER BY cost DESC"
    return conn.execute(query, params).fetchall()

def query_source_breakdown(conn, days: Optional[int] = None):
    """Get per-source breakdown (cli, telegram, discord, cron)."""
    query = """
        SELECT
            source,
            COUNT(*) as sessions,
            SUM(tool_call_count) as tools,
            SUM(input_tokens + output_tokens) as total_tok,
            SUM(estimated_cost_usd) as cost
        FROM sessions
        WHERE 1=1
    """
    params = []
    if days:
        cutoff = (datetime.now() - timedelta(days=days)).timestamp()
        query += " AND started_at >= ?"
        params.append(cutoff)

    query += " GROUP BY source ORDER BY cost DESC"
    return conn.execute(query, params).fetchall()

def query_tool_usage(conn, days: Optional[int] = None):
    """Get tool usage breakdown from messages."""
    query = """
        SELECT tool_name, COUNT(*) as count
        FROM messages
        WHERE tool_name IS NOT NULL AND tool_name != ''
    """
    params = []
    if days:
        cutoff = (datetime.now() - timedelta(days=days)).timestamp()
        query += " AND timestamp >= ?"
        params.append(cutoff)

    query += " GROUP BY tool_name ORDER BY count DESC"
    return conn.execute(query, params).fetchall()

def query_activity_breakdown(conn, days: Optional[int] = None):
    """Classify tools into activity categories (CodeBurn style)."""
    tools = query_tool_usage(conn, days)
    activities = defaultdict(lambda: {"count": 0, "tools": {}})
    for tool_name, count in tools:
        category = classify_activity(tool_name)
        activities[category]["count"] += count
        activities[category]["tools"][tool_name] = count
    return dict(sorted(activities.items(), key=lambda x: x[1]["count"], reverse=True))

def query_cache_hit_rate(conn, days: Optional[int] = None):
    """Calculate cache hit rate."""
    query = """
        SELECT
            SUM(cache_read_tokens) as cache_read,
            SUM(input_tokens) as input_tok,
            SUM(cache_read_tokens + cache_write_tokens + input_tokens) as total_input
        FROM sessions
        WHERE 1=1
    """
    params = []
    if days:
        cutoff = (datetime.now() - timedelta(days=days)).timestamp()
        query += " AND started_at >= ?"
        params.append(cutoff)

    row = conn.execute(query, params).fetchone()
    cache_read = row[0] or 0
    total_input = row[2] or 1
    return (cache_read / total_input * 100) if total_input > 0 else 0

def query_expensive_sessions(conn, limit: int = 5, days: Optional[int] = None):
    """Get most expensive sessions."""
    query = """
        SELECT id, source, model, message_count, tool_call_count,
               estimated_cost_usd, started_at
        FROM sessions
        WHERE estimated_cost_usd > 0
    """
    params = []
    if days:
        cutoff = (datetime.now() - timedelta(days=days)).timestamp()
        query += " AND started_at >= ?"
        params.append(cutoff)

    query += " ORDER BY estimated_cost_usd DESC LIMIT ?"
    params.append(limit)
    return conn.execute(query, params).fetchall()

def get_totals(conn, days: Optional[int] = None):
    """Get total stats."""
    query = """
        SELECT
            COUNT(*) as sessions,
            SUM(message_count) as messages,
            SUM(tool_call_count) as tools,
            SUM(input_tokens) as input_tok,
            SUM(output_tokens) as output_tok,
            SUM(cache_read_tokens) as cache_read,
            SUM(cache_write_tokens) as cache_write,
            SUM(reasoning_tokens) as reasoning,
            SUM(estimated_cost_usd) as cost
        FROM sessions
        WHERE 1=1
    """
    params = []
    if days:
        cutoff = (datetime.now() - timedelta(days=days)).timestamp()
        query += " AND started_at >= ?"
        params.append(cutoff)

    return conn.execute(query, params).fetchone()

# === Report Generators ===

def report_summary(conn, days_label: str = "All-time", days: Optional[int] = None):
    """Generate summary report."""
    config = load_config()
    totals = get_totals(conn, days)
    cache_rate = query_cache_hit_rate(conn, days)

    sessions, messages, tools = totals[0], totals[1] or 0, totals[2] or 0
    input_tok, output_tok = totals[3] or 0, totals[4] or 0
    cache_read, cache_write = totals[5] or 0, totals[6] or 0
    reasoning = totals[7] or 0
    cost = totals[8] or 0

    total_tokens = input_tok + output_tok + cache_read + cache_write + reasoning

    lines = []
    lines.append(f"💰 **COST LOGGER** — {days_label}")
    lines.append(f"   {datetime.now().strftime('%Y-%m-%d %H:%M')} WIB")
    lines.append("")

    # Overview
    lines.append(f"📊 **Overview:**")
    lines.append(f"   Sessions: {sessions} · Messages: {messages:,} · Tools: {tools:,}")
    lines.append(f"   Total cost: {fmt_usd(cost)}")
    if cost == 0 and total_tokens > 0:
        lines.append(f"   ⚠️ Cost $0 (free model) — token consumption still matters!")
    lines.append("")

    # Token breakdown
    lines.append(f"🔤 **Tokens:**")
    lines.append(f"   Input: {fmt_tokens(input_tok)} · Output: {fmt_tokens(output_tok)}")
    lines.append(f"   Cache Read: {fmt_tokens(cache_read)} · Cache Write: {fmt_tokens(cache_write)}")
    lines.append(f"   Reasoning: {fmt_tokens(reasoning)}")
    lines.append(f"   Total: {fmt_tokens(total_tokens)}")
    lines.append(f"   Cache hit: {cache_rate:.1f}% {bar(cache_rate)}")
    lines.append("")

    # Model breakdown
    models = query_model_breakdown(conn, days)
    if models:
        lines.append(f"🤖 **Models:**")
        total_cost = sum(m[5] or 0 for m in models)
        total_theoretical = 0
        for m in models[:5]:
            model_name = m[0] or "unknown"
            m_sessions = m[1]
            m_cost = m[5] or 0
            m_input = m[2] or 0
            m_output = m[3] or 0
            pct = (m_cost / total_cost * 100) if total_cost > 0 else 0
            theoretical = estimate_cost_if_paid(model_name, m_input, m_output)
            total_theoretical += theoretical
            if m_cost == 0 and theoretical > 0:
                lines.append(f"   {model_name}: {fmt_usd(m_cost)} actual · ~{fmt_usd(theoretical)} if paid ({m_sessions}x)")
            else:
                lines.append(f"   {model_name}: {fmt_usd(m_cost)} ({m_sessions}x, {pct:.0f}%)")
        if total_cost == 0 and total_theoretical > 0:
            lines.append(f"   💡 Theoretical cost if paid: ~{fmt_usd(total_theoretical)}")
        lines.append("")

    # Source breakdown
    sources = query_source_breakdown(conn, days)
    if sources:
        lines.append(f"📡 **Sources:**")
        source_emoji = {"cli": "🖥️", "telegram": "📱", "discord": "💬", "cron": "⏰"}
        for s in sources:
            src = s[0] or "unknown"
            emoji = source_emoji.get(src, "❓")
            lines.append(f"   {emoji} {src}: {s[1]} sessions · {s[2] or 0} tools · {fmt_usd(s[4] or 0)}")
        lines.append("")

    # Activity breakdown (CodeBurn style)
    activities = query_activity_breakdown(conn, days)
    if activities:
        lines.append(f"🎯 **Activities (CodeBurn style):**")
        total_tools = sum(a["count"] for a in activities.values())
        for act, data in list(activities.items())[:8]:
            pct = (data["count"] / total_tools * 100) if total_tools > 0 else 0
            top_tool = max(data["tools"].items(), key=lambda x: x[1])[0] if data["tools"] else "-"
            lines.append(f"   {act}: {data['count']}x ({pct:.0f}%) — top: {top_tool}")
        lines.append("")

    # Budget check
    budget = config.get("daily_budget_usd")
    if budget and days and days <= 1:
        pct = (cost / budget * 100) if budget > 0 else 0
        status = "🔴 OVER" if pct > 100 else "🟡 HIGH" if pct > config["alert_threshold_pct"] else "🟢 OK"
        lines.append(f"💵 **Budget:** {fmt_usd(cost)} / {fmt_usd(budget)} ({pct:.0f}%) {status}")
        lines.append(f"   {bar(pct)}")
        lines.append("")

    return "\n".join(lines)

def report_status(conn):
    """One-liner status."""
    today = get_totals(conn, days=1)
    month = get_totals(conn, days=30)

    today_cost = today[8] or 0
    month_cost = month[8] or 0
    today_sessions = today[0]
    month_sessions = month[0]

    config = load_config()
    budget_str = ""
    if config.get("daily_budget_usd"):
        pct = (today_cost / config["daily_budget_usd"] * 100) if config["daily_budget_usd"] > 0 else 0
        budget_str = f" / {fmt_usd(config['daily_budget_usd'])} budget ({pct:.0f}%)"

    return f"💰 Today: {fmt_usd(today_cost)} ({today_sessions}x) · Month: {fmt_usd(month_cost)} ({month_sessions}x){budget_str}"

def report_json(conn, days: Optional[int] = None):
    """Full JSON export."""
    totals = get_totals(conn, days)
    models = query_model_breakdown(conn, days)
    sources = query_source_breakdown(conn, days)
    daily = query_daily_breakdown(conn, days or 30)
    activities = query_activity_breakdown(conn, days)
    expensive = query_expensive_sessions(conn, days=days)
    cache_rate = query_cache_hit_rate(conn, days)

    data = {
        "generated_at": datetime.now().isoformat(),
        "period_days": days,
        "overview": {
            "sessions": totals[0],
            "messages": totals[1] or 0,
            "tool_calls": totals[2] or 0,
            "total_cost_usd": round(totals[8] or 0, 4),
            "cache_hit_pct": round(cache_rate, 1),
        },
        "tokens": {
            "input": totals[3] or 0,
            "output": totals[4] or 0,
            "cache_read": totals[5] or 0,
            "cache_write": totals[6] or 0,
            "reasoning": totals[7] or 0,
        },
        "models": [
            {"name": m[0], "sessions": m[1], "input": m[2] or 0, "output": m[3] or 0,
             "cache_read": m[4] or 0, "cost": round(m[5] or 0, 4)}
            for m in models
        ],
        "sources": [
            {"name": s[0], "sessions": s[1], "tools": s[2] or 0, "tokens": s[3] or 0,
             "cost": round(s[4] or 0, 4)}
            for s in sources
        ],
        "daily": [
            {"date": d[0], "sessions": d[1], "input": d[2] or 0, "output": d[3] or 0,
             "cache_read": d[4] or 0, "cost": round(d[5] or 0, 4)}
            for d in daily
        ],
        "activities": {
            k: {"count": v["count"], "top_tool": max(v["tools"].items(), key=lambda x: x[1])[0] if v["tools"] else None}
            for k, v in activities.items()
        },
        "expensive_sessions": [
            {"id": e[0], "source": e[1], "model": e[2], "messages": e[3], "tools": e[4],
             "cost": round(e[5] or 0, 4), "started": e[6]}
            for e in expensive
        ],
    }
    return json.dumps(data, indent=2)

def export_csv(conn, days: int = 30):
    """Export daily breakdown to CSV."""
    daily = query_daily_breakdown(conn, days)
    lines = ["date,sessions,input_tokens,output_tokens,cache_read,cache_write,cost_usd"]
    for d in daily:
        lines.append(f"{d[0]},{d[1]},{d[2] or 0},{d[3] or 0},{d[4] or 0},{d[5] or 0},{d[6] or 0:.4f}")
    return "\n".join(lines)

# === CLI ===

def main():
    args = sys.argv[1:]
    conn = get_db()

    if not args:
        print(report_summary(conn, "All-time"))

    elif args[0] == "today":
        print(report_summary(conn, "Today", days=1))

    elif args[0] == "week":
        print(report_summary(conn, "Last 7 days", days=7))

    elif args[0] == "month":
        print(report_summary(conn, "This month", days=30))

    elif args[0] == "report":
        days = 7
        if "--json" in args:
            print(report_json(conn, days))
        else:
            print(report_summary(conn, f"Report ({days}d)", days=days))

    elif args[0] == "status":
        print(report_status(conn))

    elif args[0] == "budget":
        if len(args) < 2:
            config = load_config()
            print(f"Daily budget: {config.get('daily_budget_usd', 'not set')}")
            print(f"Monthly budget: {config.get('monthly_budget_usd', 'not set')}")
        else:
            config = load_config()
            config["daily_budget_usd"] = float(args[1])
            save_config(config)
            print(f"✅ Daily budget set to {fmt_usd(float(args[1]))}")

    elif args[0] == "export":
        fmt = args[1] if len(args) > 1 else "csv"
        if fmt == "json":
            print(report_json(conn, days=30))
        else:
            print(export_csv(conn, days=30))

    elif args[0] == "optimize":
        print("🔍 **Optimize Scan** (CodeBurn-inspired)")
        print()
        # Cache hit analysis
        cache_rate = query_cache_hit_rate(conn, days=7)
        if cache_rate < 80:
            print(f"⚠️ Cache hit rate: {cache_rate:.1f}% (target: >80%)")
            print("   → System prompt or context may not be stable")
            print()
        else:
            print(f"✅ Cache hit rate: {cache_rate:.1f}%")
            print()

        # Most expensive sessions
        expensive = query_expensive_sessions(conn, limit=3, days=7)
        if expensive:
            print("💸 Most expensive sessions (7d):")
            for e in expensive:
                dt = datetime.fromtimestamp(e[6]).strftime("%m/%d %H:%M") if e[6] else "?"
                print(f"   {e[0][:16]}... {fmt_usd(e[5] or 0)} · {e[2]} · {e[3]} msgs · {dt}")
            print()

        # Model cost efficiency
        models = query_model_breakdown(conn, days=7)
        if len(models) > 1:
            print("🤖 Model cost efficiency:")
            for m in models[:5]:
                m_cost = m[5] or 0
                m_sessions = m[1]
                avg = m_cost / m_sessions if m_sessions > 0 else 0
                print(f"   {m[0]}: {fmt_usd(avg)}/session ({m_sessions} sessions)")
            print()

        # Activity insight
        activities = query_activity_breakdown(conn, days=7)
        total_tools = sum(a["count"] for a in activities.values())
        general_pct = (activities.get("General", {}).get("count", 0) / total_tools * 100) if total_tools > 0 else 0
        if general_pct > 30:
            print(f"⚠️ {general_pct:.0f}% tools uncategorized — may indicate idle/low-value calls")
            print()

    else:
        print(__doc__)

    conn.close()

if __name__ == "__main__":
    main()
