from pathlib import Path
import yaml, json, hashlib, sys

ROOT=Path(__file__).resolve().parents[1]
REC=ROOT/"receipts"

def h(obj):
    raw=json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
    return "sha256:"+hashlib.sha256(raw).hexdigest()

def main():
    route=yaml.safe_load((REC/"route.generated.yaml").read_text(encoding="utf-8"))
    receipt=yaml.safe_load((REC/"routing_receipt.generated.yaml").read_text(encoding="utf-8"))
    settlement=yaml.safe_load((REC/"settlement_evidence.generated.yaml").read_text(encoding="utf-8"))
    checks={
      "route_hash_present": bool(route["validation"].get("decision_hash")),
      "receipt_payload_hash_present": bool(receipt["integrity"].get("payload_hash")),
      "receipt_semantic_hash_present": bool(receipt["integrity"].get("semantic_hash")),
      "settlement_evidence_hash_present": bool(settlement["verification"].get("evidence_hash")),
      "settlement_not_executed": settlement["verification"].get("settlement_ready") is False
    }
    ok=all(checks.values())
    print(yaml.safe_dump({"ok":ok,"checks":checks},sort_keys=False))
    sys.exit(0 if ok else 1)

if __name__=="__main__":
    main()
