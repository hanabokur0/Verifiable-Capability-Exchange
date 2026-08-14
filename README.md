# Verifiable Capability Exchange

**A reference protocol and pseudo-market for exchanging verifiable Power, Compute, Network, and Storage capabilities across organizational boundaries.**

LoPAS Capability Exchange demonstrates how heterogeneous infrastructure providers can publish semantically normalized capability claims, route workloads against those claims, and produce cryptographically verifiable evidence without exposing all underlying operational data.

> **Status:** Experimental reference implementation / PoC.  
> **Not affiliated with or endorsed by any company represented in the simulated examples.**

## Why this exists

Power-aware computing is increasingly split across different organizations:

- grid and power operators know energy availability,
- compute providers know GPU availability,
- carriers know network conditions,
- storage operators know battery flexibility,
- customers know workload constraints.

The hard part is not only moving workloads. It is exchanging **what is currently possible, what that claim means, who asserted it, why a route was chosen, and what evidence exists for later settlement**.

This project provides a minimal interoperability layer for that problem.

## Protocol flow

```text
Provider Raw Data
      ↓
Provider-specific Adapter
      ↓
Common Capability Schema
      ↓
Workload Request
      ↓
Reference Router
      ↓
Signed Capability Receipt
      ↓
Signed Routing Receipt
      ↓
Settlement Evidence
      ↓
Independent Verification
```

The core idea is:

```text
different source formats
        ↓
shared semantic capability
        ↓
verifiable claim
        ↓
auditable routing
        ↓
settlement-ready evidence
```

## What this is — and what it is not

This **is**:

- a common semantic schema for Power / Compute / Network / Storage capabilities,
- an adapter contract for provider-specific data,
- a workload-routing reference implementation,
- a signed Receipt format,
- an encrypted evidence envelope,
- a hash-chained audit trail,
- a Settlement Evidence format.

This is **not**:

- a blockchain,
- a power exchange,
- a GPU cloud,
- a payment system,
- a grid-control system,
- a Kubernetes replacement,
- production PKI or key management.

The protocol is intentionally designed so that existing systems remain in place and expose only the capability claims and evidence required for interoperability.

## Five core schemas

```text
capability.schema.yaml
        ↓
workload.schema.yaml
        ↓
route.schema.yaml
        ↓
receipt.schema.yaml
        ↓
settlement_evidence.schema.yaml
```

Additional interoperability and security profiles:

```text
adapter_contract.schema.yaml
security_profile.schema.yaml
```

## Semantic layer

A capability is not only a number.

For example, `8 GPUs available` can retain:

- what “available” means,
- when the observation was made,
- how long it remains valid,
- location and jurisdiction,
- constraints,
- provenance,
- verification state,
- unknown fields.

This allows values from different providers to be compared without discarding their meaning.

## Cryptographic evidence layer

v0.3 includes:

- deterministic canonical JSON profile,
- SHA-256 payload hashes,
- SHA-256 semantic hashes,
- Ed25519 signatures,
- AES-256-GCM encrypted evidence,
- Receipt hash chaining,
- independent verification,
- tamper-detection tests.

Sensitive raw evidence can remain encrypted while the public claim, signer, hashes, and chain relationship remain independently verifiable.

```text
Public:
  claim
  semantics
  payload hash
  semantic hash
  signer
  signature
  previous Receipt hash

Private / encrypted:
  meter readings
  internal telemetry
  detailed provider evidence
```

## Quick start

Requirements:

- Python 3.10+
- PyYAML
- cryptography

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the pseudo-market:

```bash
python src/simulate_market.py
python src/verify_receipts.py
python src/secure_market.py
python src/tamper_test.py
```

Expected security result:

```yaml
secure_chain: true
encrypted_evidence_roundtrip: true
tamper_detected: true
```

The demo creates simulated Power / Compute / Storage nodes, submits a workload, chooses an eligible route, emits signed Receipts, encrypts private evidence, and verifies that later modification is detected.

## Repository structure

```text
schemas/
  capability.schema.yaml
  workload.schema.yaml
  route.schema.yaml
  receipt.schema.yaml
  settlement_evidence.schema.yaml
  adapter_contract.schema.yaml
  security_profile.schema.yaml

examples/
  simulated provider feeds
  adapter examples
  workload example

src/
  simulate_market.py
  verify_receipts.py
  crypto_engine.py
  secure_market.py
  tamper_test.py

receipts/
  generated reference outputs
```

## Adapter model

Providers do not need to adopt the same internal data format.

```text
Provider A ─ Adapter A ┐
Provider B ─ Adapter B ├─→ Common Capability Schema
Provider C ─ Adapter C ┘
```

Only the adapter output contract is shared.

This makes the protocol suitable as an interoperability layer above existing APIs, telemetry systems, schedulers, energy-management systems, and data spaces.

## Settlement boundary

This project deliberately separates:

```text
Settlement Evidence
        ≠
Settlement Execution
```

A Receipt can prove what was claimed, routed, measured, and attested without this reference implementation moving money.

This keeps the protocol usable before a commercial or regulatory settlement mechanism is chosen.

## Security note

This repository is a reference security profile, not production key management.

Demo private signing keys and AES keys are generated locally at runtime and must not be committed.

Production deployments should use, as appropriate:

- KMS / HSM-backed signing keys,
- issuer identity and certificate policy,
- access-control policy,
- key rotation,
- independent attestors,
- trusted timestamping or transparency-log anchoring.

A blockchain or other external anchor can be added later without changing the five core market schemas.

## Simulated organizations

Names and identifiers in `examples/` are simulation fixtures only. They do not indicate participation, endorsement, interoperability testing, or affiliation with any real-world organization.

For public demonstrations, generic provider identifiers are recommended.

## Current scope

Implemented:

- semantic capability normalization,
- adapter contract,
- workload constraints,
- candidate routing,
- signed capability and routing Receipts,
- encrypted evidence,
- Receipt hash chain,
- Settlement Evidence,
- independent verification,
- tamper detection.

Not implemented:

- real utility or cloud APIs,
- actual grid control,
- actual GPU scheduling,
- payment execution,
- production PKI,
- zero-knowledge proofs,
- consensus or blockchain infrastructure.

## Next milestones

- Multi-Issuer signatures
- provider-neutral example fixtures
- external timestamp / transparency-log anchoring
- OpenADR / Kubernetes / carbon-data adapter examples
- schema validation in CI
- cross-provider route verification

## License

Apache-2.0
