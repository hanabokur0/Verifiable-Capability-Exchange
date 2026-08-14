from __future__ import annotations
import base64, hashlib, json, os
from pathlib import Path
from typing import Any, Dict

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey, Ed25519PublicKey
)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import serialization

def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(
        obj,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

def sha256_hex(obj: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(obj)).hexdigest()

def b64e(b: bytes) -> str:
    return base64.b64encode(b).decode("ascii")

def b64d(s: str) -> bytes:
    return base64.b64decode(s.encode("ascii"))

def generate_ed25519_keypair():
    private = Ed25519PrivateKey.generate()
    public = private.public_key()
    private_raw = private.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_raw = public.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return private_raw, public_raw

def save_demo_keys(keys_dir: Path):
    keys_dir.mkdir(parents=True, exist_ok=True)
    priv_path = keys_dir / "issuer_ed25519_private.key"
    pub_path = keys_dir / "issuer_ed25519_public.key"
    aes_path = keys_dir / "evidence_aes256.key"

    if not priv_path.exists() or not pub_path.exists():
        priv, pub = generate_ed25519_keypair()
        priv_path.write_text(b64e(priv), encoding="utf-8")
        pub_path.write_text(b64e(pub), encoding="utf-8")

    if not aes_path.exists():
        aes_path.write_text(b64e(AESGCM.generate_key(bit_length=256)), encoding="utf-8")

    return priv_path, pub_path, aes_path

def load_private(path: Path) -> Ed25519PrivateKey:
    return Ed25519PrivateKey.from_private_bytes(
        b64d(path.read_text(encoding="utf-8").strip())
    )

def load_public(path: Path) -> Ed25519PublicKey:
    return Ed25519PublicKey.from_public_bytes(
        b64d(path.read_text(encoding="utf-8").strip())
    )

def sign_bytes(data: bytes, private_key: Ed25519PrivateKey) -> str:
    return b64e(private_key.sign(data))

def verify_bytes(data: bytes, signature_b64: str, public_key: Ed25519PublicKey) -> bool:
    try:
        public_key.verify(b64d(signature_b64), data)
        return True
    except Exception:
        return False

def encrypt_evidence(obj: Any, aes_key: bytes, aad: bytes | None = None) -> Dict[str, str]:
    nonce = os.urandom(12)
    aes = AESGCM(aes_key)
    ciphertext = aes.encrypt(nonce, canonical_bytes(obj), aad)
    return {
        "algorithm": "AES-256-GCM",
        "nonce": b64e(nonce),
        "ciphertext": b64e(ciphertext),
        "aad": b64e(aad) if aad else None,
    }

def decrypt_evidence(envelope: Dict[str, str], aes_key: bytes) -> Any:
    aes = AESGCM(aes_key)
    aad = b64d(envelope["aad"]) if envelope.get("aad") else None
    plaintext = aes.decrypt(
        b64d(envelope["nonce"]),
        b64d(envelope["ciphertext"]),
        aad,
    )
    return json.loads(plaintext.decode("utf-8"))

def payload_view(receipt: dict) -> dict:
    """
    Stable view for payload hashing.
    Excludes fields whose values are derived from the payload itself.
    """
    clone = json.loads(json.dumps(receipt))
    integrity = clone.setdefault("integrity", {})
    integrity["payload_hash"] = None
    integrity["signature"] = None
    return clone

def signature_view(receipt: dict) -> dict:
    """
    Signature covers the finalized payload hash but excludes the signature itself.
    """
    clone = json.loads(json.dumps(receipt))
    clone.setdefault("integrity", {})["signature"] = None
    return clone

def sign_receipt(receipt: dict, private_key: Ed25519PrivateKey) -> dict:
    clone = json.loads(json.dumps(receipt))
    clone["integrity"]["signature_algorithm"] = "Ed25519"
    clone["integrity"]["signature"] = None
    clone["integrity"]["payload_hash"] = sha256_hex(payload_view(clone))
    clone["integrity"]["signature"] = sign_bytes(
        canonical_bytes(signature_view(clone)),
        private_key
    )
    return clone

def verify_receipt(receipt: dict, public_key: Ed25519PublicKey) -> dict:
    expected_hash = sha256_hex(payload_view(receipt))
    hash_ok = receipt.get("integrity", {}).get("payload_hash") == expected_hash
    sig = receipt.get("integrity", {}).get("signature")
    sig_ok = bool(sig) and verify_bytes(
        canonical_bytes(signature_view(receipt)),
        sig,
        public_key
    )
    return {
        "payload_hash_ok": hash_ok,
        "signature_ok": sig_ok,
        "ok": hash_ok and sig_ok,
    }
