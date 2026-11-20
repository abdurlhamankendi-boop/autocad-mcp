"""Token use and list-price cost per agent, read from workflow transcripts.

    python cost.py WORKFLOW_TRANSCRIPT_DIR [--json OUT.json]

One API call can appear on several transcript lines (one per content block),
so calls are de-duplicated by message id, keeping the last usage record.
Prices: platform.claude.com/docs/en/about-claude/pricing, read 2026-10-08
($/MTok: input, 5m cache write, 1h cache write, cache read, output). Haiku 5.5
is priced by prompt length: above 100,000 prompt tokens the second row applies.
"""
import glob
import json
import os
import sys

PRICE = {
    "claude-fable-5-1": (10, 12.5, 20, 0.25, 50),
    "claude-opus-5-5": (4, 5, 8, 0.20, 20),
    "claude-sonnet-5-5": (2, 2.5, 4, 0.10, 10),
    "claude-haiku-5-5": (0.10, 0.125, 0.20, 0.01, 0.50),
    "claude-haiku-5-5>100k": (0.50, 0.625, 1.0, 0.05, 2.50),
    "claude-haiku-4-5-20251001": (1, 1.25, 2, 0.10, 5),
}


def long_path(p):
    p = os.path.abspath(p)
    return p if p.startswith("\\\\?\\") else "\\\\?\\" + p


def agent_cost(path):
    calls = {}
    for line in open(long_path(path), encoding="utf-8"):
        try:
            o = json.loads(line)
        except ValueError:
            continue
        m = o.get("message") or {}
        if m.get("role") != "assistant" or "usage" not in m:
            continue
        calls[m.get("id") or len(calls)] = (m.get("model"), m["usage"])
    tot = {"calls": 0, "input": 0, "cache_write_5m": 0, "cache_write_1h": 0, "cache_read": 0,
           "output": 0, "max_prompt": 0, "calls_over_100k": 0, "usd": 0.0}
    models = set()
    for model, u in calls.values():
        if not model or model.startswith("<"):
            continue
        models.add(model)
        cc = u.get("cache_creation") or {}
        w5 = cc.get("ephemeral_5m_input_tokens", u.get("cache_creation_input_tokens", 0) if not cc else 0)
        w1 = cc.get("ephemeral_1h_input_tokens", 0)
        inp, rd, out = u.get("input_tokens", 0), u.get("cache_read_input_tokens", 0), u.get("output_tokens", 0)
        prompt = inp + w5 + w1 + rd
        key = model
        if model == "claude-haiku-5-5" and prompt > 100_000:
            key = model + ">100k"
            tot["calls_over_100k"] += 1
        p = PRICE.get(key)
        if p is None:
            raise SystemExit(f"no price for {model}")
        tot["usd"] += (inp * p[0] + w5 * p[1] + w1 * p[2] + rd * p[3] + out * p[4]) / 1e6
        tot["calls"] += 1
        tot["input"] += inp
        tot["cache_write_5m"] += w5
        tot["cache_write_1h"] += w1
        tot["cache_read"] += rd
        tot["output"] += out
        tot["max_prompt"] = max(tot["max_prompt"], prompt)
    tot["models"] = sorted(models)
    return tot


def main(argv):
    d = argv[0]
    rows = []
    for meta in sorted(glob.glob(os.path.join(long_path(d), "agent-*.meta.json"))):
        m = json.load(open(meta, encoding="utf-8"))
        c = agent_cost(meta.replace(".meta.json", ".jsonl"))
        rows.append({"label": m.get("description"), **c})
    rows.sort(key=lambda r: r["label"] or "")
    print(f"{'agent':28s} {'model':20s} {'calls':>5s} {'output':>8s} {'max prompt':>10s} {'>100k':>5s} {'USD':>8s}")
    for r in rows:
        print(f"{(r['label'] or '')[:28]:28s} {','.join(r['models'])[:20]:20s} {r['calls']:5d} "
              f"{r['output']:8d} {r['max_prompt']:10d} {r['calls_over_100k']:5d} {r['usd']:8.3f}")
    print(f"{'TOTAL':28s} {'':20s} {sum(r['calls'] for r in rows):5d} {sum(r['output'] for r in rows):8d} "
          f"{'':10s} {'':5s} {sum(r['usd'] for r in rows):8.3f}")
    if "--json" in argv:
        json.dump(rows, open(argv[argv.index("--json") + 1], "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1:])
