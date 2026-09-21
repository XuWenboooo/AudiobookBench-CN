"""Build an auditable, outcome-blind compression of the unresolved W7 P4 fields."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "research_assurance" / "topconf"
sys.path.insert(0, str(REPO / "src"))

from audiobookbench.topconf.w7_mechanism_spec import FAMILY_IDS, FIXED_FIELDS, P4_FIELDS  # noqa: E402


INVENTORY = ROOT / "W7_P4_EXACT_INVENTORY_V1.json"
CLASSIFICATION = ROOT / "W7_P4_CLASSIFICATION_AND_COMPRESSION_V1.json"
SHARED = ROOT / "W7_MECHANISM_SHARED_POLICIES_V1.json"
PROVENANCE = ROOT / "W7_MECHANISM_P4_RESOLUTION_PROVENANCE_V1.md"
DECISIONS = ROOT / "W7_MECHANISM_P4_MINIMAL_HUMAN_DECISIONS_V1.md"

SCIENTIFIC_FIELDS = {"reference_rule", "target_span_rule", "parameters"}
BINDING_FIELDS = {"implementation", "version", "parameter_set_id", "codec_path"}
SOURCES = [
    "MECHANISM_PARAMETER_EVIDENCE_MATRIX_V1.md",
    "w7_preparation/MECHANISM_CONFIG_CONTRACT_V1.md",
    "w7_preparation/MECHANISM_CONFIG_SCHEMA_V1.json",
    "w7_preparation/W7_PILOT_PROTOCOL_DRAFT_V1.md",
]


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    rows = []
    for family in FAMILY_IDS:
        for field in P4_FIELDS:
            classification = "SCIENTIFIC_CHOICE" if field in SCIENTIFIC_FIELDS else "IMPLEMENTATION_BINDING"
            rows.append(
                {
                    "p4_id": f"P4-{len(rows) + 1:03d}",
                    "family": family,
                    "field_name": field,
                    "field_type": "object" if field == "parameters" else "string",
                    "current_status": "P5_HUMAN_DECISION_REQUIRED",
                    "allowed_domain": "documented official implementation/configuration value; no outcome-guided selection",
                    "existing_sources": SOURCES,
                    "scientific_effect": "mechanism semantics or treatment binding" if classification == "SCIENTIFIC_CHOICE" else "binds frozen semantics to an implementation/API/version",
                    "implementation_dependency": "required before executable config hash and runner" ,
                    "classification": classification,
                    "resolution_level": "P5",
                    "outcome_information_used": False,
                }
            )

    inventory = {
        "schema_version": "topconf.w7.p4.exact_inventory.v1",
        "raw_p4_fields": len(rows),
        "families": list(FAMILY_IDS),
        "p4_fields": list(P4_FIELDS),
        "source_config": "W7_MECHANISM_EXECUTION_CONFIG_V1_PENDING_P4.json",
        "source_case_map_sha256": "8449E9ABFA7FF5E359F00BB9CBEA7D3E6889DF3474F411D7D7E6E4338F9528C9",
        "outcome_information_used": False,
        "records": rows,
    }
    write_json(INVENTORY, inventory)

    classification = {
        "schema_version": "topconf.w7.p4.classification_and_compression.v1",
        "raw_p4_fields": len(rows),
        "classification_counts": {
            "SCIENTIFIC_CHOICE": sum(r["classification"] == "SCIENTIFIC_CHOICE" for r in rows),
            "IMPLEMENTATION_BINDING": sum(r["classification"] == "IMPLEMENTATION_BINDING" for r in rows),
            "VALIDATION_POLICY": 0,
            "DERIVED": 0,
            "DUPLICATED_SHARED_POLICY": 0,
            "UNCLASSIFIED": 0,
        },
        "classification_rule": {
            "scientific": sorted(SCIENTIFIC_FIELDS),
            "implementation_binding": sorted(BINDING_FIELDS),
            "validation_policy": [],
            "derived": [],
            "duplicated_shared_policy": [],
        },
        "minimal_independent_scientific_decisions": 5,
        "decision_compression": "one complete, documented implementation/configuration bundle per mechanism family; each bundle resolves that family's seven P4 cells",
        "p5_field_count": len(rows),
        "p5_decision_ids": [f"DECISION-{i:02d}" for i in range(1, 6)],
        "candidate_complete": False,
        "candidate_status": "NOT_CREATED_P5_REMAINS",
        "outcome_information_used": False,
    }
    write_json(CLASSIFICATION, classification)

    shared = {
        "schema_version": "topconf.w7.mechanism_shared_policies.v1",
        "status": "FROZEN_PREEXISTING_POLICIES_ONLY",
        "policies": {
            "sample_rate_policy": {"value": FIXED_FIELDS["sample_rate"], "source": "W7_MECHANISM_EXECUTION_CONFIG_V1_PENDING_P4.json"},
            "seed_policy": {"value": FIXED_FIELDS["seed_policy"], "source": "W7_MECHANISM_EXECUTION_CONFIG_V1_PENDING_P4.json"},
            "quality_gate_policy": {"value": FIXED_FIELDS["quality_gate_policy"], "source": "W7_MECHANISM_EXECUTION_CONFIG_V1_PENDING_P4.json"},
            "failure_policy": {"value": FIXED_FIELDS["failure_policy"], "source": "W7_MECHANISM_EXECUTION_CONFIG_V1_PENDING_P4.json"},
        },
        "not_assumed": ["channel_policy", "normalization", "duration_policy", "codec_backend"],
        "raw_p4_fields_collapsed": 0,
        "outcome_information_used": False,
    }
    write_json(SHARED, shared)

    lines = [
        "# W7 mechanism P4 resolution provenance v1",
        "",
        "Status: `P5_HUMAN_DECISION_REQUIRED`; no candidate or executable configuration was created.",
        "",
        "The exact inventory accounts for all 35 raw fields (five families × seven fields). P1, P2, P3, and P4 resolution counts are all zero because the pinned evidence matrix explicitly marks implementation identity, parameter values, reference/span rules, and codec path as unspecified or non-unique. Therefore all 35 remain P5.",
        "",
        "Classification accounting: 15 `SCIENTIFIC_CHOICE` fields (reference rule, target-span rule, parameters), 20 `IMPLEMENTATION_BINDING` fields (implementation, version, parameter-set ID, codec path), zero validation-policy fields, zero derived fields, zero duplicated shared-policy fields, and zero unclassified fields.",
        "",
        "Compression: the 35 cells are represented by five independent human decisions, one complete documented implementation/configuration bundle per family. This is a decision grouping, not a value selection. The four already frozen shared policies are recorded separately and do not erase any raw P4 field.",
        "",
        "Evidence precedence was applied P1→P4 using the pinned matrix, mechanism contract/schema, and frozen protocol. No historical outcome, W7 output, Level-2 outcome, model score, expected gap, or trial-and-error information was used.",
        "",
        "The case-to-family map remains unchanged. Because P5 remains nonzero, Candidate A, candidate execution config, candidate hash, and human approval packet are intentionally not created. W7 remains unauthorized and unexecuted.",
        "",
        "## 35 → 35 accounting",
        "",
        "| resolution class | count | fate |",
        "|---|---:|---|",
        "| P1 | 0 | P5 remains |",
        "| P2 | 0 | P5 remains |",
        "| P3 | 0 | P5 remains |",
        "| P4 | 0 | P5 remains |",
        "| P5 | 35 | represented by five family-level decisions |",
        "",
        "All decisions are outcome-blind and pre-inference.",
    ]
    PROVENANCE.write_text("\n".join(lines) + "\n", encoding="utf-8")

    decision_lines = [
        "# W7 minimal human decisions v1",
        "",
        "`P4_CANDIDATE_COMPLETE = NO`; these are unresolved decision slots, not selected values.",
        "",
        "Five family-level decisions remain. Each decision must supply one complete, documented bundle for the seven fields: implementation, version, parameter_set_id, reference_rule, target_span_rule, codec_path, and parameters.",
        "",
    ]
    for i, family in enumerate(FAMILY_IDS, 1):
        decision_lines.extend([
            f"## DECISION-{i:02d}",
            f"- FAMILY = `{family}`",
            "- FIELD = complete seven-field implementation/configuration bundle",
            "- WHY_NOT_DERIVABLE = pinned pre-W7 evidence does not uniquely bind an implementation or parameterization",
            "- ALLOWED_VALUES = one reproducible value set documented by official implementation/configuration evidence; no outcome-guided alternatives",
            "- OFFICIAL_EVIDENCE = implementation repository/source revision, relevant file/config location, and canonical/default evaluation documentation",
            "- SCIENTIFIC_CONSEQUENCE = resolves the mechanism treatment binding for this family before inference",
            "",
        ])
    decision_lines.extend([
        "Do not use the 106,859 real W7 cases, model responses, waveform appearance, scores, or Level-2 data to fill these slots. After resolution, rebuild the candidate config and provenance, run deterministic synthetic/API/schema checks only, and request explicit human approval. Do not self-approve or execute W7.",
    ])
    DECISIONS.write_text("\n".join(decision_lines) + "\n", encoding="utf-8")
    print(json.dumps({"raw_p4_fields": len(rows), "minimal_independent_decisions": 5, "p5_count": len(rows)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
