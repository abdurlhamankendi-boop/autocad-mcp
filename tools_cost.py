"""Token use and list-price cost of a whole Claude Code session, by model and by agent.

    python tools_cost.py SESSION_JSONL [--since 2026-10-16T08:00] [--json OUT.json]

SESSION_JSONL is the main conversation's transcript,
~/.claude/projects/<cwd>/<session>.jsonl. Its subagents are read too:
<session>/subagents/agent-*.jsonl (Agent tool) and
<session>/subagents/workflows/wf_*/agent-*.jsonl (workflows). --since keeps
only API calls at or after that UTC timestamp prefix, so one demo run can be
costed inside a longer session. The per-call arithmetic (prices, the Haiku 5.5
100K-prompt tier, de-duplication by message id) is the benchmark's cost.py.
"""
from __future__ import annotations

import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "tests", "fixtures", "bench_2026-10-08"))
import cost as C  # noqa: E402


def calls(path, since=""):
    """[(model, usage)] of one transcript, one entry per API call."""
    seen = {}
    for line in open(C.long_path(path), encoding="utf-8"):
        try:
            o = json.loads(line)
        except ValueError:
            continue
        if since and (o.get("timestamp") or "") < since:
            continue
        m = o.get("message") or {}
        if m.get("role") == "assistant" and "usage" in m and m.get("model") \
                and not str(m.get("model")).startswith("<"):
            seen[m.get("id") or len(seen)] = (m["model"], m["usage"])
    return list(seen.values())


def price(model, u):
    cc = u.get("cache_creation") or {}
    w5 = cc.get("ephemeral_5m_input_tokens", 0 if cc else u.get("cache_creation_input_tokens", 0))
    w1 = cc.get("ephemeral_1h_input_tokens", 0)
    inp, rd, out = u.get("input_tokens", 0), u.get("cache_read_input_tokens", 0), u.get("output_tokens", 0)
    key = model + ">100k" if model == "claude-haiku-5-5" and inp + w5 + w1 + rd > 100_000 else model
    p = C.PRICE.get(key)
    if p is None:
        raise SystemExit(f"no price for {model}")
    return (inp * p[0] + w5 * p[1] + w1 * p[2] + rd * p[3] + out * p[4]) / 1e6, inp + w5 + w1 + rd, out


def main(argv):
    main_jsonl = os.path.abspath(argv[0])
    since = argv[argv.index("--since") + 1] if "--since" in argv else ""
    sess = main_jsonl[:-len(".jsonl")]
    files = [("main conversation", main_jsonl)]
    for meta in sorted(glob.glob(os.path.join(C.long_path(sess), "subagents", "**", "agent-*.meta.json"),
                                 recursive=True)):
        label = json.load(open(meta, encoding="utf-8")).get("description") or os.path.basename(meta)
        wf = os.path.basename(os.path.dirname(meta))
        files.append((f"{label} [{wf}]" if wf.startswith("wf_") else label,
                      meta.replace(".meta.json", ".jsonl")))
    by_agent, by_model = [], {}
    for label, path in files:
        if not os.path.exists(C.long_path(path)):
            continue
        usd = tin = tout = 0.0
        models = set()
        for model, u in calls(path, since):
            d, i, o = price(model, u)
            usd, tin, tout = usd + d, tin + i, tout + o
            models.add(model)
            m = by_model.setdefault(model, {"usd": 0.0, "input": 0, "output": 0, "calls": 0})
            m["usd"] += d
            m["input"] += i
            m["output"] += o
            m["calls"] += 1
        if models:
            by_agent.append({"agent": label, "models": sorted(models), "usd": round(usd, 4),
                             "input_tokens": int(tin), "output_tokens": int(tout)})
    total = sum(m["usd"] for m in by_model.values()) or 1e-9
    print(f"{'model':22s} {'calls':>6s} {'input tok':>12s} {'output tok':>11s} {'USD':>9s} {'share':>6s}")
    for model, m in sorted(by_model.items(), key=lambda kv: -kv[1]["usd"]):
        print(f"{model:22s} {m['calls']:6d} {m['input']:12,d} {m['output']:11,d} {m['usd']:9.2f} "
              f"{100 * m['usd'] / total:5.1f}%")
    print(f"{'TOTAL':22s} {'':6s} {'':12s} {'':11s} {total:9.2f}")
    print("\nby agent:")
    for a in sorted(by_agent, key=lambda a: -a["usd"]):
        print(f"  {a['usd']:8.3f}  {','.join(a['models'])[:20]:20s}  {a['agent'][:70]}")
    if "--json" in argv:
        json.dump({"since": since, "by_model": by_model, "by_agent": by_agent, "total_usd": total},
                  open(argv[argv.index("--json") + 1], "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1:])
