from pathlib import Path
import json, yaml, sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
OUT = ROOT / "receipts"
KEYS = ROOT / "crypto" / "keys"

sys.path.insert(0, str(SRC))

from crypto_engine import (
    save_demo_keys, load_private, load_public, b64d,
    encrypt_evidence, decrypt_evidence,
    sha256_hex, sign_receipt, verify_receipt
)

def load_yaml(path):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))

def dump_yaml(path, obj):
    Path(path).write_text(
        yaml.safe_dump(obj, allow_unicode=True, sort_keys=False),
        encoding="utf-8"
    )

def main():
    priv_path, pub_path, aes_path = save_demo_keys(KEYS)
    private_key = load_private(priv_path)
    public_key = load_public(pub_path)
    aes_key = b64d(aes_path.read_text(encoding="utf-8").strip())

    # Reuse v0.2 generated market outputs.
    route = load_yaml(OUT / "route.generated.yaml")
    settlement = load_yaml(OUT / "settlement_evidence.generated.yaml")

    raw_private_evidence = {
        "meter_reading": {
            "source": "simulated-meter",
            "energy_kwh": 438.0,
            "peak_kw": 310.0
        },
        "gpu_monitor": {
            "source": "simulated-gpu-monitor",
            "gpu_model": "H200",
            "gpu_seconds": 86400
        },
        "internal_note": "demo confidential evidence"
    }

    encrypted = encrypt_evidence(
        raw_private_evidence,
        aes_key,
        aad=b"lopas-receipt-route-001"
    )

    receipt1 = {
        "receipt_id": "receipt-capability-proof-001",
        "receipt_type": "capability",
        "issued_at": "2026-08-14T09:00:30+09:00",
        "subject": {
            "subject_id": route["selected"]["node_id"],
            "subject_type": "compute_node"
        },
        "claim": {
            "statement": "selected_node_capability_was_available",
            "value": True,
            "unit": None,
            "semantics": {
                "capability_refs": route["selected"]["capability_refs"]
            }
        },
        "evidence": {
            "evidence_refs": route["selected"]["capability_refs"],
            "encrypted": True,
            "encryption": encrypted
        },
        "integrity": {
            "canonicalization": "canonical-json-sorted-v1",
            "semantic_hash": sha256_hex({
                "statement": "selected_node_capability_was_available",
                "value": True,
                "capability_refs": route["selected"]["capability_refs"]
            }),
            "payload_hash": "",
            "previous_receipt_hash": None,
            "signer_id": "demo-issuer-01",
            "signature_algorithm": "Ed25519",
            "signature": None,
            "timestamp_proof": None
        },
        "verification": {
            "status": "simulated",
            "verifier_id": "independent-verifier-01",
            "verified_at": None,
            "notes": "encrypted evidence; signed public claim"
        }
    }
    receipt1 = sign_receipt(receipt1, private_key)

    receipt2 = {
        "receipt_id": "receipt-routing-proof-002",
        "receipt_type": "routing",
        "issued_at": "2026-08-14T09:01:05+09:00",
        "subject": {
            "subject_id": route["route_id"],
            "subject_type": "route"
        },
        "claim": {
            "statement": "workload_routed",
            "value": {
                "workload_id": route["workload_ref"],
                "selected_node": route["selected"]["node_id"]
            },
            "unit": None,
            "semantics": {
                "decision_reason": route["decision"]["reason"]
            }
        },
        "evidence": {
            "evidence_refs": [receipt1["receipt_id"]],
            "encrypted": False,
            "encryption": {}
        },
        "integrity": {
            "canonicalization": "canonical-json-sorted-v1",
            "semantic_hash": sha256_hex({
                "statement": "workload_routed",
                "selected_node": route["selected"]["node_id"]
            }),
            "payload_hash": "",
            "previous_receipt_hash": receipt1["integrity"]["payload_hash"],
            "signer_id": "demo-router-01",
            "signature_algorithm": "Ed25519",
            "signature": None,
            "timestamp_proof": None
        },
        "verification": {
            "status": "simulated",
            "verifier_id": "independent-verifier-01",
            "verified_at": None,
            "notes": "hash chained to capability proof"
        }
    }
    receipt2 = sign_receipt(receipt2, private_key)

    receipt3 = {
        "receipt_id": "receipt-settlement-evidence-003",
        "receipt_type": "settlement",
        "issued_at": "2026-08-14T10:36:00+09:00",
        "subject": {
            "subject_id": settlement["settlement_evidence_id"],
            "subject_type": "settlement_evidence"
        },
        "claim": {
            "statement": "settlement_evidence_generated",
            "value": {
                "workload_ref": settlement["workload_ref"],
                "route_ref": settlement["route_ref"],
                "settlement_ready": settlement["verification"]["settlement_ready"]
            },
            "unit": None,
            "semantics": {
                "execution_only": False,
                "payment_executed": False
            }
        },
        "evidence": {
            "evidence_refs": [receipt2["receipt_id"]],
            "encrypted": False,
            "encryption": {}
        },
        "integrity": {
            "canonicalization": "canonical-json-sorted-v1",
            "semantic_hash": sha256_hex(settlement),
            "payload_hash": "",
            "previous_receipt_hash": receipt2["integrity"]["payload_hash"],
            "signer_id": "demo-settlement-attestor-01",
            "signature_algorithm": "Ed25519",
            "signature": None,
            "timestamp_proof": None
        },
        "verification": {
            "status": "simulated",
            "verifier_id": "independent-verifier-01",
            "verified_at": None,
            "notes": "settlement evidence only; no payment"
        }
    }
    receipt3 = sign_receipt(receipt3, private_key)

    chain = [receipt1, receipt2, receipt3]

    checks = []
    previous = None
    for i, rec in enumerate(chain):
        vr = verify_receipt(rec, public_key)
        link_ok = rec["integrity"]["previous_receipt_hash"] == previous
        checks.append({
            "receipt_id": rec["receipt_id"],
            **vr,
            "chain_link_ok": link_ok,
            "ok": vr["ok"] and link_ok
        })
        previous = rec["integrity"]["payload_hash"]

    decrypted = decrypt_evidence(
        receipt1["evidence"]["encryption"],
        aes_key
    )

    dump_yaml(OUT / "secure_receipt_chain.generated.yaml", chain)
    dump_yaml(OUT / "secure_verification.generated.yaml", {
        "ok": all(c["ok"] for c in checks),
        "checks": checks,
        "encrypted_evidence_roundtrip_ok": decrypted == raw_private_evidence,
        "public_key_file": str(pub_path.relative_to(ROOT)),
        "security_profile": "lopas-security-v0.3"
    })

    print("Secure chain OK:", all(c["ok"] for c in checks))
    print("Encrypted evidence roundtrip OK:", decrypted == raw_private_evidence)
    for c in checks:
        print("-", c["receipt_id"], "signature=", c["signature_ok"], "hash=", c["payload_hash_ok"], "chain=", c["chain_link_ok"])

if __name__ == "__main__":
    main()
