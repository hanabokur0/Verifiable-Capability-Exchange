from pathlib import Path
import yaml, json, hashlib, datetime

ROOT = Path(__file__).resolve().parents[1]
EX = ROOT / "examples"
OUT = ROOT / "receipts"

def h(obj):
    raw = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",",":"), default=str).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()

def load(name):
    return yaml.safe_load((EX/name).read_text(encoding="utf-8"))

def capability_from_raw(name):
    r = load(name)
    ts = r["timestamp"]
    if "additional_load_kw" in r:
        return [{
            "capability_id":"cap-tepco-power-001",
            "resource_type":"power",
            "provider":{"provider_id":r["provider"],"operator_name":None,"adapter_id":"adapter-tepco-mock","adapter_version":"0.1.0"},
            "location":{"region":r["area"],"zone":None,"site_id":None,"grid_area":r["area"],"jurisdiction":"JP"},
            "availability":{"state":r["status"],"quantity":r["additional_load_kw"],"unit":"kW","valid_from":ts,"valid_until":"2026-08-14T10:00:00+09:00","observed_at":ts},
            "semantics":{"capability":"additional_load_acceptable","availability_definition":"schedulable_now","interruptible":r["interruptible"],"deferrable":None,"movable":None,"latency_class":None,"confidence":1.0,"unknown_fields":[]},
            "constraints":{},
            "provenance":{"source_type":"simulated","source_id":name,"source_uri":None,"observed_by":"demo-adapter"},
            "verification":{"status":"simulated","evidence_refs":[name],"semantic_hash":None,"payload_hash":None,"signature":None}
        }]
    caps=[]
    if "gpu_available" in r:
        caps.append({
            "capability_id":f"cap-{r['provider'].lower()}-compute",
            "resource_type":"compute",
            "provider":{"provider_id":r["provider"],"operator_name":None,"adapter_id":"demo-adapter","adapter_version":"0.1.0"},
            "location":{"region":r["region"],"zone":None,"site_id":None,"grid_area":r["region"],"jurisdiction":"JP"},
            "availability":{"state":r["status"],"quantity":r["gpu_available"],"unit":"gpu","valid_from":ts,"valid_until":None,"observed_at":ts},
            "semantics":{"capability":"schedulable_gpu","availability_definition":"schedulable_now","interruptible":True,"deferrable":True,"movable":True,"latency_class":"low","confidence":1.0,"unknown_fields":[]},
            "constraints":{"gpu_model":r.get("gpu_model"),"network_gbps":r.get("network_gbps"),"latency_to_tokyo_ms":r.get("latency_to_tokyo_ms"),"carbon_intensity_gco2_kwh":r.get("carbon_intensity_gco2_kwh")},
            "provenance":{"source_type":"simulated","source_id":name,"source_uri":None,"observed_by":"demo-adapter"},
            "verification":{"status":"simulated","evidence_refs":[name],"semantic_hash":None,"payload_hash":None,"signature":None}
        })
    if "bess_available_kwh" in r:
        caps.append({
            "capability_id":f"cap-{r['provider'].lower()}-storage",
            "resource_type":"storage",
            "provider":{"provider_id":r["provider"],"operator_name":None,"adapter_id":"demo-adapter","adapter_version":"0.1.0"},
            "location":{"region":r["region"],"zone":None,"site_id":None,"grid_area":r["region"],"jurisdiction":"JP"},
            "availability":{"state":r["status"],"quantity":r["bess_available_kwh"],"unit":"kWh","valid_from":ts,"valid_until":None,"observed_at":ts},
            "semantics":{"capability":"discharge_available","availability_definition":"available_now","interruptible":True,"deferrable":True,"movable":False,"latency_class":None,"confidence":1.0,"unknown_fields":[]},
            "constraints":{},
            "provenance":{"source_type":"simulated","source_id":name,"source_uri":None,"observed_by":"demo-adapter"},
            "verification":{"status":"simulated","evidence_refs":[name],"semantic_hash":None,"payload_hash":None,"signature":None}
        })
    return caps

def main():
    OUT.mkdir(exist_ok=True)
    names=["tepco_power_raw.yaml","ntt_gpu_raw.yaml","hokkaido_gpu_bess_raw.yaml","kyushu_renewable_raw.yaml"]
    caps=[]
    for n in names:
        caps += capability_from_raw(n)
    for c in caps:
        c["verification"]["semantic_hash"]=h({"resource_type":c["resource_type"],"location":c["location"],"availability":c["availability"],"semantics":c["semantics"]})
        c["verification"]["payload_hash"]=h(c)

    wl=load("workload.yaml")
    candidates=[]
    for c in [x for x in caps if x["resource_type"]=="compute"]:
        qty=c["availability"]["quantity"] or 0
        model=c["constraints"].get("gpu_model")
        lat=c["constraints"].get("latency_to_tokyo_ms")
        if lat is None and c["location"]["region"]=="tokyo": lat=5
        carbon=c["constraints"].get("carbon_intensity_gco2_kwh")
        eligible=(qty >= wl["requirements"]["compute"]["gpu_count"] and model==wl["requirements"]["compute"]["gpu_model"] and (lat is None or lat <= wl["requirements"]["network"]["max_latency_ms"]))
        score=(qty - wl["requirements"]["compute"]["gpu_count"]) - (lat or 0)*0.2 - ((carbon or 250)/100)
        candidates.append({
            "node_id":c["provider"]["provider_id"],
            "capability_refs":[c["capability_id"]],
            "eligibility":"eligible" if eligible else "ineligible",
            "rejection_reasons":[] if eligible else ["compute_or_latency_constraint_failed"],
            "scores":{"composite":round(score,3)}
        })
    eligible=[x for x in candidates if x["eligibility"]=="eligible"]
    selected=max(eligible, key=lambda x:x["scores"]["composite"])
    route={
        "route_id":"route-001","workload_ref":wl["workload_id"],"observed_at":"2026-08-14T09:01:00+09:00",
        "candidates":candidates,
        "selected":{"node_id":selected["node_id"],"capability_refs":selected["capability_refs"]},
        "decision":{"status":"selected","reason":"highest_composite_score_under_constraints","policy_id":"demo-router","policy_version":"0.1.0","decided_by":"reference-router","human_approval":False,"confidence":0.95},
        "expected_impact":{"energy_kwh":450,"cost_jpy":None,"carbon_kg":None,"latency_ms":None},
        "validation":{"status":"simulated","evidence_refs":selected["capability_refs"],"decision_hash":None,"signature":None}
    }
    route["validation"]["decision_hash"]=h(route)

    receipt={
        "receipt_id":"receipt-route-001","receipt_type":"routing","issued_at":"2026-08-14T09:01:05+09:00",
        "subject":{"subject_id":"route-001","subject_type":"route"},
        "claim":{"statement":"workload_routed","value":{"workload_id":"wl-001","selected_node":selected["node_id"]},"unit":None,"semantics":{"reason":"constraint_satisfied_and_best_score"}},
        "evidence":{"evidence_refs":selected["capability_refs"],"encrypted":False,"encryption":{}},
        "integrity":{"canonicalization":"sorted-json-v1","semantic_hash":h({"statement":"workload_routed","selected_node":selected["node_id"]}),"payload_hash":"","previous_receipt_hash":None,"signer_id":"reference-router","signature_algorithm":None,"signature":None,"timestamp_proof":None},
        "verification":{"status":"simulated","verifier_id":"reference-verifier","verified_at":"2026-08-14T09:01:06+09:00","notes":"simulation only"}
    }
    receipt["integrity"]["payload_hash"]=h(receipt)

    settle={
        "settlement_evidence_id":"settle-001","workload_ref":"wl-001","route_ref":"route-001",
        "execution_receipt_refs":["receipt-route-001"],
        "usage":{"compute":{"gpu_seconds":16*90*60,"gpu_model":"H200"},"energy":{"kwh":438.0,"peak_kw":310.0},"storage":{"discharged_kwh":120.0,"charged_kwh":0.0},"network":{"transferred_gb":820.0,"average_latency_ms":18.4}},
        "impact":{"grid_contribution_kwh":120.0,"curtailed_or_shifted_kwh":438.0,"cost_before_jpy":None,"cost_after_jpy":None,"carbon_before_kg":None,"carbon_after_kg":None},
        "valuation":{"compute_value_jpy":None,"energy_value_jpy":None,"storage_value_jpy":None,"network_value_jpy":None,"grid_service_value_jpy":None,"carbon_value_jpy":None,"total_value_jpy":None},
        "evidence":{"evidence_refs":["receipt-route-001"],"measurement_window_start":"2026-08-14T09:05:00+09:00","measurement_window_end":"2026-08-14T10:35:00+09:00","attestors":["simulated-meter","simulated-gpu-monitor"]},
        "verification":{"status":"simulated","discrepancy":{},"settlement_ready":False,"verifier_id":"reference-verifier","evidence_hash":None}
    }
    settle["verification"]["evidence_hash"]=h(settle)

    docs={
        "capabilities.generated.yaml":caps,
        "route.generated.yaml":route,
        "routing_receipt.generated.yaml":receipt,
        "settlement_evidence.generated.yaml":settle
    }
    for fn,obj in docs.items():
        (OUT/fn).write_text(yaml.safe_dump(obj, allow_unicode=True, sort_keys=False),encoding="utf-8")

    print("Selected node:", selected["node_id"])
    print("Generated:")
    for fn in docs: print("-", OUT/fn)

if __name__=="__main__":
    main()
