"""Extract every agent finding and verdict from the workflow journals into a
single durable markdown document.

Processes on disk: the journals total ~660 KB and must not be pulled into a
conversation. Only a summary is printed.
"""

import json
import os

HOME = os.path.expanduser("~")
# This path runs to ~290 characters, past Windows' 260-char MAX_PATH, so the
# directory is invisible to os.listdir without the extended-length prefix.
# That is why cygpath reports it as \\?\C:\... rather than C:\...
LONG = "\\\\?\\"
BASE = os.path.join(
    LONG + HOME, ".claude", "projects",
    "C--Users-lsire-AppData-Roaming-Claude-scratch-workspaces-"
    "436da4c5-e448-4522-8504-fb3dec3718e9-"
    "f86423bb-0f28-4bea-a1b5-a2b812363194-scratch-2026-09-06-5fc263",
    "0a85fa68-f6c3-4f8e-a777-5f0d403d4c58", "subagents", "workflows")

OUT = os.path.join(HOME, "autocad-mcp", "VILLA_CRITIQUE_FINDINGS.md")


def clean(s):
    return (str(s or "")
            .replace("’", "'").replace("—", "--")
            .replace("–", "-").replace("�", "-").strip())


def collect():
    findings, verdicts, seen = [], [], set()
    if not os.path.isdir(BASE):
        return findings, verdicts, []
    roots = [os.path.join(BASE, d) for d in os.listdir(BASE)]
    roots = [r for r in roots if os.path.isdir(r)]
    for root in roots:
        jp = os.path.join(root, "journal.jsonl")
        if not os.path.exists(jp):
            continue
        with open(jp, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    o = json.loads(line)
                except Exception:
                    continue
                if o.get("type") != "result":
                    continue
                r = o.get("result")
                if not isinstance(r, dict):
                    continue
                if isinstance(r.get("findings"), list):
                    for it in r["findings"]:
                        if not isinstance(it, dict):
                            continue
                        t = (it.get("title") or "").strip()
                        if t and t not in seen:
                            seen.add(t)
                            findings.append(it)
                elif "real" in r:
                    verdicts.append(r)
    return findings, verdicts, roots


def main():
    findings, verdicts, roots = collect()
    order = {"fatal": 0, "major": 1, "minor": 2}
    findings.sort(key=lambda x: order.get(str(x.get("severity", "")).lower(), 3))
    upheld = [v for v in verdicts if v.get("real")]
    refuted = [v for v in verdicts if not v.get("real")]

    L = []
    L.append("# Villa design critique - full agent findings\n")
    L.append("Extracted from the workflow journals of the six-lens adversarial")
    L.append("critique. Roughly **7.4M agent tokens** across two runs produced")
    L.append("this. Journals: " + ", ".join(os.path.basename(r) for r in roots) + "\n")
    L.append(f"- distinct findings raised: **{len(findings)}**")
    L.append(f"- verdicts returned: **{len(verdicts)}** "
             f"({len(upheld)} upheld, {len(refuted)} refuted)\n")
    L.append("> **Meta-lesson, worth more than the findings themselves:** nearly")
    L.append("> every item below is *mechanically detectable*. Room areas are")
    L.append("> arithmetic. Inner rooms and unreachable volumes are a reachability")
    L.append("> graph over door openings. Bathrooms-per-bedroom is counting. A")
    L.append("> validator finds these for free on every run, in milliseconds.")
    L.append("> Agents should be spent on judgement that cannot be computed --")
    L.append("> does the elevation read as architect-designed, is the concept")
    L.append("> actually delivered -- not on arithmetic.\n")

    L.append("\n---\n\n## Findings by severity\n")
    for i, f in enumerate(findings, 1):
        L.append(f"### {i}. {clean(f.get('title'))}\n")
        L.append(f"**Severity:** {clean(f.get('severity')).upper() or 'UNSTATED'}\n")
        if f.get("numbers"):
            L.append(f"**Numbers:** {clean(f.get('numbers'))}\n")
        L.append(f"**Evidence:** {clean(f.get('evidence'))}\n")
        L.append(f"**Proposed fix:** {clean(f.get('fix'))}\n")

    L.append("\n---\n\n## Verification verdicts\n")
    L.append("Each verifier was instructed to REFUTE its finding, defaulting to")
    L.append("`real=false` when uncertain or when the point was taste rather")
    L.append("than defect. Those below survived that test.\n")
    for i, v in enumerate(upheld, 1):
        L.append(f"### Upheld {i}\n")
        L.append(clean(v.get("reasoning"))[:6000] + "\n")
        if v.get("corrected_fix"):
            L.append("**Corrected fix:**\n")
            L.append(clean(v.get("corrected_fix"))[:6000] + "\n")
    if refuted:
        L.append("\n### Refuted (kept for the record)\n")
        for i, v in enumerate(refuted, 1):
            L.append(f"**{i}.** {clean(v.get('reasoning'))[:800]}\n")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))

    print(f"journals read : {len(roots)}")
    print(f"findings      : {len(findings)}")
    print(f"verdicts      : {len(verdicts)} "
          f"({len(upheld)} upheld / {len(refuted)} refuted)")
    print(f"written       : {OUT} ({os.path.getsize(OUT) // 1024} KB)")
    mix = {k: sum(1 for f in findings
                  if str(f.get("severity", "")).lower() == k)
           for k in ("fatal", "major", "minor")}
    print(f"severity      : {mix}")
    print("")
    for f in findings[:20]:
        print(f"  [{str(f.get('severity', '?')).upper():5s}] "
              f"{clean(f.get('title'))[:84]}")


if __name__ == "__main__":
    main()
