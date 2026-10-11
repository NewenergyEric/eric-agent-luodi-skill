"""Authorized synthetic demonstration; each run gets a fresh project-local directory."""
from pathlib import Path
import json
import uuid

import client_setup as cs


def main():
    root = cs.safe(cs.ROOT, f".demo-runs/{uuid.uuid4().hex[:12]}")
    root.mkdir(parents=True)
    public_files = ["sources.lock.json"] + [f"recipes/{v}.json" for v in cs.VERSIONS]
    public_files += [f"packages/{v}/{p}" for v in cs.VERSIONS for p in cs.PAYLOADS]
    for name in public_files:
        cs.put(cs.safe(root, name), cs.read(cs.safe(cs.ROOT, name)))
    cs.put(cs.safe(root, "customers/demo/overrides.json"), cs.encode(
        {"currency": "CNY", "minimum_total": 20, "credential_refs": ["env:DEMO_REFERENCE_ONLY"]}))
    engine = cs.Engine(root)
    install = engine.preview("configure", "demo", "local", "1.0.0")
    print("Synthetic demo plan:", install["plan_id"], flush=True)
    receipt_v1 = engine.apply("configure", "demo", "local", "1.0.0", install["plan_id"])
    target = engine.target("demo", "local")
    before = {name: (cs.read(cs.safe(target, name)), cs.safe(target, name).stat().st_mtime_ns) for name in cs.TRANSACTION_FILES}
    replay = engine.apply("configure", "demo", "local", "1.0.0", install["plan_id"])
    after = {name: (cs.read(cs.safe(target, name)), cs.safe(target, name).stat().st_mtime_ns) for name in cs.TRANSACTION_FILES}
    if not replay.get("replayed") or before != after:
        raise AssertionError("idempotence_failed")
    update = engine.preview("update", "demo", "local", "1.1.0")
    print("Synthetic update plan:", update["plan_id"], flush=True)
    engine.fail_at = "file-2"
    try:
        engine.apply("update", "demo", "local", "1.1.0", update["plan_id"])
    except RuntimeError:
        pass
    else:
        raise AssertionError("failure_injection_not_reached")
    engine = cs.Engine(root)
    interrupted = engine.check("demo", "local")
    if interrupted["status"] != "recovery_required":
        raise AssertionError("recovery_not_detected")
    receipt_v2 = engine.apply("update", "demo", "local", "1.1.0", update["plan_id"])
    result = {"status": "passed", "root": str(root), "install_plan": install, "install_receipt": receipt_v1,
              "idempotence": "passed_no_managed_file_rewrite", "update_plan": update,
              "injected_interruption": interrupted, "recovery": "passed", "update_receipt": receipt_v2,
              "final_check": engine.check("demo", "local"),
              "receipt_path": str(cs.safe(root, ".control/latest/demo--local.json"))}
    cs.put(cs.safe(root, "run.json"), cs.encode(result))
    cs.put(cs.safe(cs.ROOT, "DEMO-LATEST.json"), cs.encode({"status": "passed", "root": str(root), "result": str(root / "run.json")}))
    print(json.dumps({"status": result["status"], "root": str(root), "result": str(root / "run.json"),
                      "acceptance": receipt_v2["acceptance"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
