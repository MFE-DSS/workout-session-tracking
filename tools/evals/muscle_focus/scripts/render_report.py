#!/usr/bin/env python3
"""Render the synthetic-review report set — GO C2 §13. Deterministic, offline, no-JS baseline.

Reads (from <ROOT>/08_synthetic_review/):
  results/synthetic_review_raw_results.json   (all judge outputs)
  results/synthetic_review_aggregate.json     (per-region deterministic aggregates)
  calibration/calibration_results.json
Writes into results/: report.html (self-contained, 360px + desktop), report_manifest.json,
disagreement_register.md, veto_register.md, agent_findings_<region>.md, martin_decision_form.md.

No preselected Martin decision. No hidden failed judgment. Professional review = NOT CLAIMED.
"""
from __future__ import annotations

import base64
import html
import json
import os
import pathlib
import shutil

ROOT = pathlib.Path(os.environ["AUREN_MUSCLE_FOCUS_REVIEW_ROOT"])
PKG = ROOT / "07_external_review/sb-asset-03b-2r-qualified-anatomical-review"
SYN = ROOT / "08_synthetic_review"
RES = SYN / "results"
REGIONS = ["chest", "shoulders", "posterior"]
CRIT = ["orientation_and_laterality", "source_structure_completeness", "anatomical_visual_consistency",
        "context_relationships", "occlusion_integrity", "silhouette_readability", "mobile_readability",
        "product_semantic_clarity", "provenance_honesty", "scope_and_claim_discipline"]


def data_uri(rel):
    p = PKG / rel
    if not p.is_file():
        return ""
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()


def esc(x):
    return html.escape(str(x))


def render_decision(d):
    """MARTIN OWNER DECISION section (owner internal product-risk acceptance). Never marks professional
    review complete; never hides disagreements (raw judge outputs and registers are untouched)."""
    if not d:
        return ""
    rows = []
    for region in REGIONS:
        rd = d["regions"][region]
        cons = "".join(f"<li><b>{esc(k)}</b> — {esc(v)}</li>" for k, v in rd["forward_constraints"].items())
        rows.append(
            f"<h3 style='font-size:13px'>{esc(region.capitalize())} — {esc(rd['owner_decision'])}</h3>"
            f"<div class='muted'>accepted: {esc(rd.get('accepted_product_geometry') or rd.get('accepted_geometry'))} · "
            f"Plan-B: {esc(rd['plan_b_status'])}"
            + (f" · partition: {esc(rd.get('partition_product_status',''))} ({esc(rd.get('diagnostic_partition',''))})"
               if region == "chest" else "") + "</div>"
            f"<ul>{cons}</ul>")
    g = d["gate_transitions"]
    gates = "".join(f"<span class='gate'>{esc(k)}: {esc(v)}</span>" for k, v in g.items())
    rr = d["owner_residual_risk_acceptance"]
    return f"""<section><h2>MARTIN OWNER DECISION</h2>
<div class="status stwarn">GLOBAL: {esc(d['global_decision'])}</div>
<div class="muted">Owner internal product-risk acceptance · {esc(d['decision_timestamp'])} · {esc(d['council_type'])}.
Professional anatomical review: <b>{esc(d['professional_anatomical_review'])}</b> ·
legal clearance: <b>{esc(d['professional_legal_clearance'])}</b> · medical validation: <b>{esc(d['medical_validation'])}</b>.</div>
{''.join(rows)}
<p class="muted"><b>Owner residual-risk acceptance: {esc(rr['status'])}</b> — scope: {esc(', '.join(rr['scope']))}.
Does NOT cover: {esc(', '.join(rr['does_not_cover']))}.</p>
<div>{gates}</div>
<p class="muted">Candidate hashes (frozen): chest <code>{esc(d['candidates']['chest'])}</code> · shoulders
<code>{esc(d['candidates']['shoulders'])}</code> · posterior <code>{esc(d['candidates']['posterior'])}</code>.
Raw judge outputs and disagreement/veto registers are unchanged; this section adds the owner decision only.</p>
</section>"""


def main() -> int:
    raw = json.loads((RES / "synthetic_review_raw_results.json").read_text())
    agg = json.loads((RES / "synthetic_review_aggregate.json").read_text())
    calib = json.loads((SYN / "calibration/calibration_results.json").read_text())
    dpath = RES / "martin_final_decision.json"
    decision = json.loads(dpath.read_text()) if dpath.is_file() else None

    by_region = {r: [o for o in raw["outputs"] if o["region"] == r] for r in REGIONS}

    # ---- markdown registers ----
    veto_lines = ["# Veto Register\n"]
    dis_lines = ["# Disagreement Register\n",
                 "Per region: verdict spread across judges and score dispersion (stddev).\n"]
    for r in REGIONS:
        a = agg[r]
        veto_lines.append(f"## {r}")
        if a["confirmed_vetoes"]:
            for v in a["confirmed_vetoes"]:
                veto_lines.append(f"- **CONFIRMED** `{v['type']}` by {', '.join(v['confirmed_by'])} — {esc(v['rationale'])}")
        else:
            veto_lines.append("- no confirmed veto")
        verdicts = sorted({o["proposed_verdict"] for o in by_region[r]})
        dis_lines.append(f"## {r}\n- proposed verdicts present: {', '.join(verdicts)}\n"
                         f"- consensus: {a['consensus']}\n"
                         f"- composite dispersion visible in report.html\n"
                         f"- preserved disagreements: {a['arbiter'].get('preserved_disagreements') or 'none'}")
    (RES / "veto_register.md").write_text("\n".join(veto_lines) + "\n")
    (RES / "disagreement_register.md").write_text("\n".join(dis_lines) + "\n")

    # ---- per-region findings ----
    for r in REGIONS:
        fl = [f"# Agent Findings — {r}\n",
              f"Candidate SHA-256: `{agg[r]['candidate_sha256']}`  ·  status: **{agg[r]['status']}**  ·  "
              f"score {agg[r]['weighted_score']}  ·  consensus {agg[r]['consensus']}\n"]
        for o in sorted(by_region[r], key=lambda o: (o["judge_role"], o["run_id"])):
            for f in o.get("findings", []):
                fl.append(f"- [{f['severity']}] ({o['judge_role']}) **{esc(f['structure'])}** "
                          f"side={f['side']} view={f['view']} — {esc(f['rationale'])} "
                          f"→ _{esc(f['proposed_action'])}_ (conf {f['confidence']}; {esc(f['evidence'])})")
        if len(fl) == 2:
            fl.append("- no findings recorded")
        (RES / f"agent_findings_{r}.md").write_text("\n".join(fl) + "\n")

    # ---- Martin decision form (no preselection) ----
    (RES / "martin_decision_form.md").write_text(
        "# Martin Decision — Synthetic Multimodel Internal Review (Sb_ASSET_03B.2R-C2)\n\n"
        "**PROFESSIONAL ANATOMICAL REVIEW: NOT PERFORMED / NOT CLAIMED.**\n"
        "This is internal synthetic QA only. It does not equal a qualified professional anatomical review.\n\n"
        "Per-region synthetic status:\n"
        + "".join(f"- {r}: **{agg[r]['status']}** (score {agg[r]['weighted_score']}, consensus {agg[r]['consensus']}, "
                  f"vetoes {len(agg[r]['confirmed_vetoes'])}, major findings {agg[r]['major_findings_count']})\n"
                  for r in REGIONS)
        + "\nChoose exactly ONE (none preselected):\n"
        "- [ ] ACCEPT_SYNTHETIC_INTERNAL_REVIEW\n- [ ] ACCEPT_WITH_CONSTRAINTS\n"
        "- [ ] REQUEST_TARGETED_REVISION\n- [ ] REJECT\n\n"
        "Notes / residual-risk acceptance: ______________________________\n"
        "Signature (typed name = attributable): __________  Date (UTC): __________\n\n"
        "> Chest diagnostic partition stays REVIEW_PARTITION_UNRESOLVED / NOT ACCEPTED regardless of this decision.\n"
        "> This decision does not enact global acceptance, §5bis, asset intake, or runtime.\n")

    # ---- offline HTML ----
    css = """*{box-sizing:border-box}body{margin:0;background:#0f1318;color:#e6e6e6;font-family:ui-monospace,Menlo,monospace;line-height:1.5}
main{max-width:1100px;margin:0 auto;padding:16px}h1{font-size:19px}h2{font-size:15px;color:#f6c667;border-bottom:1px solid #2a3140;padding-bottom:4px;margin-top:26px}
table{border-collapse:collapse;width:100%;font-size:12px;margin:8px 0}td,th{border:1px solid #2a3140;padding:3px 6px;text-align:left}
.bad{color:#e08a5a}.ok{color:#6fbf73}.muted{color:#8a97a8}.gate{display:inline-block;border:1px solid #2a3140;border-radius:5px;padding:2px 8px;margin:2px;font-size:12px}
img{max-width:100%;height:auto;background:#0b0e12;border:1px solid #2a3140;border-radius:8px}
.status{font-weight:bold}.stwarn{color:#e08a5a}.stok{color:#6fbf73}
@media print{body{background:#fff;color:#000}}@media(max-width:400px){main{padding:10px}}"""

    def status_cls(s):
        return "stok" if s.startswith("SYNTHETIC_ACCEPTED") else "stwarn"

    sec = []
    for r in REGIONS:
        a = agg[r]
        rows = "".join(
            f"<tr><td>{esc(c)}</td><td>{a['criteria'][c]['median']}</td><td>{a['criteria'][c]['min']}</td>"
            f"<td>{a['criteria'][c]['max']}</td><td>{a['criteria'][c]['stddev']}</td></tr>" for c in CRIT)
        role_hdr = sorted({o["judge_role"] for o in by_region[r]})
        role_rows = ""
        for c in CRIT:
            cells = "".join(f"<td>{a['criteria'][c]['by_role_median'].get(role, '·')}</td>" for role in role_hdr)
            role_rows += f"<tr><td>{esc(c)}</td>{cells}</tr>"
        vetoes = "".join(f"<span class='gate bad'>VETO {esc(v['type'])}</span>" for v in a["confirmed_vetoes"]) or "<span class='gate ok'>no confirmed veto</span>"
        part = f"<div class='muted'>partition: {esc(a.get('partition_status',''))}</div>" if a.get("partition_status") else ""
        sec.append(f"""<section><h2>{esc(r.capitalize())}</h2>
<div class="status {status_cls(a['status'])}">{esc(a['status'])}</div>
<div>weighted score <b>{a['weighted_score']}</b> · consensus <b>{esc(a['consensus'])}</b> · judges {a['judge_output_count']} · major findings {a['major_findings_count']}</div>
<div>{vetoes}</div>{part}
<img alt="{esc(r)} candidate" src="{data_uri(f'02_PREVIEWS/{r}_preview_360.png')}">
<h3 style="font-size:13px">Criterion medians &amp; dispersion (0-100)</h3>
<table><thead><tr><th>criterion</th><th>median</th><th>min</th><th>max</th><th>stddev</th></tr></thead><tbody>{rows}</tbody></table>
<h3 style="font-size:13px">Median score by judge role</h3>
<table><thead><tr><th>criterion</th>{''.join(f'<th>{esc(x)}</th>' for x in role_hdr)}</tr></thead><tbody>{role_rows}</tbody></table>
<div class="muted">Full findings: agent_findings_{r}.md · disagreement_register.md · veto_register.md</div>
</section>""")

    calib_line = (f"critical {calib['critical_detected']}/{calib['critical_total']} · "
                  f"overall {calib['overall_detected']}/{calib['overall_total']} · result {calib['result']}")
    page = f"""<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Auren Muscle Focus — Synthetic Multimodel Review</title><style>{css}</style>
<main>
<h1>Auren Muscle Focus — Synthetic Multimodel Internal Review</h1>
<div class="muted">Sb_ASSET_03B.2R-C2 · run mode {esc(agg['chest']['run_mode'])} · internal QA only.</div>
<div style="margin-top:8px">
<span class="gate">PROFESSIONAL ANATOMICAL REVIEW: NOT PERFORMED / NOT CLAIMED</span>
<span class="gate">EXTERNAL DISPATCH: DEFERRED BY OWNER</span>
<span class="gate">RUNTIME: BLOCKED</span>
<span class="gate">§5BIS: NOT ENACTED</span>
<span class="gate">CALIBRATION: {esc(calib_line)}</span></div>
{''.join(sec)}
{render_decision(decision)}
<section><h2>Governance</h2>
<p class="muted">Synthetic multimodel review is reusable internal QA and does NOT equal a qualified professional
anatomical review. Martin may accept the residual risk for non-medical internal/product use. Professional
anatomical/legal accuracy remains unclaimed. The external review package is retained; dispatch deferred.
A future professional review may still supersede this synthetic verdict. Candidate SVGs unchanged.</p>
<p class="muted">Decide in <b>martin_decision_form.md</b> (no option preselected).</p>
</section></main></html>"""
    if decision and (RES / "report.html").is_file():
        arch = RES / "archive"
        arch.mkdir(exist_ok=True)
        shutil.copy(RES / "report.html", arch / "report_pre_owner_decision.html")
        if (RES / "report_manifest.json").is_file():
            shutil.copy(RES / "report_manifest.json", arch / "report_manifest_pre_owner_decision.json")
    (RES / "report.html").write_text(page)

    manifest = {
        "_schema": "synthetic review report manifest", "sprint": "Sb_ASSET_03B.2R-C2",
        "run_mode": agg["chest"]["run_mode"], "regions": {r: {
            "status": agg[r]["status"], "weighted_score": agg[r]["weighted_score"],
            "consensus": agg[r]["consensus"], "confirmed_vetoes": len(agg[r]["confirmed_vetoes"]),
            "major_findings": agg[r]["major_findings_count"], "candidate_sha256": agg[r]["candidate_sha256"]}
            for r in REGIONS},
        "calibration": {"critical": f"{calib['critical_detected']}/{calib['critical_total']}",
                        "overall": f"{calib['overall_detected']}/{calib['overall_total']}", "result": calib["result"]},
        "professional_anatomical_review": "NOT_PERFORMED_NOT_CLAIMED",
        "external_dispatch": "DEFERRED_BY_OWNER", "runtime": "BLOCKED",
        "martin_owner_decision": ({"global": decision["global_decision"],
                                   "decided_at": decision["decision_timestamp"],
                                   "regions": {r: decision["regions"][r]["owner_decision"] for r in REGIONS}}
                                  if decision else None),
        "files": sorted(p.name for p in RES.glob("*") if p.is_file()),
    }
    (RES / "report_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"report rendered: {RES/'report.html'}  ({len(page)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
