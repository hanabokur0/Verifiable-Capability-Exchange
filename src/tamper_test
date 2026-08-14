from pathlib import Path
import copy, yaml, sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from crypto_engine import load_public, verify_receipt

chain = yaml.safe_load((ROOT/"receipts"/"secure_receipt_chain.generated.yaml").read_text(encoding="utf-8"))
pub = load_public(ROOT/"crypto"/"keys"/"issuer_ed25519_public.key")

original = chain[1]
tampered = copy.deepcopy(original)
tampered["claim"]["value"]["selected_node"] = "ATTACKER-NODE"

original_check = verify_receipt(original, pub)
tampered_check = verify_receipt(tampered, pub)

result = {
    "original_valid": original_check["ok"],
    "tampered_valid": tampered_check["ok"],
    "tamper_detected": original_check["ok"] and not tampered_check["ok"],
}
(ROOT/"receipts"/"tamper_test.generated.yaml").write_text(
    yaml.safe_dump(result, sort_keys=False),
    encoding="utf-8"
)
print(yaml.safe_dump(result, sort_keys=False))
sys.exit(0 if result["tamper_detected"] else 1)
