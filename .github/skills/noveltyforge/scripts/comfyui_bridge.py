#!/usr/bin/env python3
"""Submit NoveltyForge's planned concepts to a LOCAL ComfyUI API.

This is a render adapter, NOT a visual evaluator or trained preference model.
No accepted/rejected history is written; use NoveltyForge 'record' after reviewing images.
Python 3.10+, standard library only.
"""
import argparse
import hashlib
import json
import secrets
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

def load(path):
    with Path(path).open(encoding="utf-8") as f:
        return json.load(f)

def save(path, data):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def api(base, route, data=None, timeout=60):
    body = None if data is None else json.dumps(data).encode("utf-8")
    req = Request(base + route, body, {"Content-Type": "application/json"} if body else {},
                  method="POST" if body else "GET")
    with urlopen(req, timeout=timeout) as resp:
        return json.load(resp)

def validate_base(url):
    parsed = urlparse(url)
    if parsed.scheme != "http" or parsed.hostname not in ("localhost", "127.0.0.1", "::1") or parsed.username:
        raise ValueError("Only local, unauthenticated HTTP ComfyUI endpoints are supported.")
    return url.rstrip("/")

def node(workflow, node_id, input_name):
    if not isinstance(workflow, dict) or node_id not in workflow:
        raise ValueError("Missing node ID " + str(node_id) + " in API workflow")
    current = workflow[node_id]
    if not isinstance(current, dict) or not isinstance(current.get("inputs"), dict):
        raise ValueError("Workflow must be ComfyUI API format, with node inputs")
    if input_name not in current["inputs"]:
        raise ValueError("Node " + node_id + " lacks input " + input_name)
    return current["inputs"]

def prepare(workflow, ids, positive, seed, negative=None):
    # Deep copy: each job independent even if an endpoint changes input values.
    prepared = json.loads(json.dumps(workflow))
    inputs = node(prepared, ids["positive_node"], "text")
    if not isinstance(inputs["text"], str):
        raise ValueError("Positive node text must be a literal string (CLIPTextEncode)")
    inputs["text"] = positive
    if ids.get("negative_node") is not None:
        neg = node(prepared, ids["negative_node"], "text")
        if not isinstance(neg["text"], str):
            raise ValueError("Negative node text must be a literal string")
        if negative is not None:
            neg["text"] = negative
    sampler = node(prepared, ids["sampler_node"], "seed")
    if not isinstance(sampler["seed"], int) or isinstance(sampler["seed"], bool):
        raise ValueError("Sampler seed must be an integer")
    sampler["seed"] = seed
    # Always force one latent per job to prevent multi-character contact sheets.
    if ids.get("latent_node"):
        latent = node(prepared, ids["latent_node"], "batch_size")
        latent["batch_size"] = 1
    return prepared

def prompt_for_file(path):
    text = Path(path).read_text(encoding="utf-8")
    # A local CLIP prompt should not blindly copy the very long agent instruction document.
    marker = "## Locked independent blueprint"
    if marker not in text:
        raise ValueError("Not a current NoveltyForge prompt: " + str(path))
    # Keep style, concept and taste constraints; remove markdown syntax to reduce token pressure.
    lines = [x.strip().lstrip("-#* ") for x in text.splitlines()]
    lines = [x for x in lines if x and not x.startswith("The user-selected rendering style")]
    return ", ".join(lines)[:4500]

def job_seed(master_seed, index):
    raw = f"noveltyforge-comfyui:{master_seed}:{index}".encode("utf-8")
    return int.from_bytes(hashlib.sha256(raw).digest()[:8], "big") % (2**63)

def validate_manifest(manifest, prompts, count):
    if manifest.get("render_style") not in ("anime-2d", "illustration-2d", "painterly-2d", "stylized-3d"):
        raise ValueError("Manifest missing current locked render style")
    designs = manifest.get("designs")
    if not isinstance(designs, list) or not designs:
        raise ValueError("Manifest has no designs")
    if count > len(designs):
        raise ValueError("Requested number exceeds planned NoveltyForge designs")
    for d in designs[:count]:
        if not isinstance(d.get("id"), str) or not (prompts / f"character-{d['number']:02d}.md").is_file():
            raise ValueError("Missing matching character prompt")
    return designs[:count]

def run(args):
    base = validate_base(args.url)
    if args.count < 1 or args.count > 10:
        raise ValueError("count must be 1..10; plan another batch after review")
    manifest = load(args.manifest)
    prompt_dir = Path(args.manifest).parent / "prompts"
    designs = validate_manifest(manifest, prompt_dir, args.count)
    wf = load(args.workflow)
    if not isinstance(wf, dict) or not wf or not all(isinstance(v, dict) and "class_type" in v for v in wf.values()):
        raise ValueError("Expected exported ComfyUI API workflow, not the editor workflow JSON")
    ids = dict(positive_node=str(args.positive_node), negative_node=str(args.negative_node)
               if args.negative_node else None, sampler_node=str(args.sampler_node),
               latent_node=str(args.latent_node) if args.latent_node else None)
    # Validate mapping before submission.
    prepare(wf, ids, "test", 1, args.negative)
    ledger_path = Path(args.ledger)
    ledger = load(ledger_path) if ledger_path.exists() else {"jobs": []}
    completed = {j["design_id"] for j in ledger["jobs"] if j.get("state") == "completed"}
    for i, d in enumerate(designs, 1):
        if d["id"] in completed:
            print("Skipping previously completed", d["id"])
            continue
        seed = job_seed(manifest["master_seed"], d["number"])
        pos = prompt_for_file(prompt_dir / f"character-{d['number']:02d}.md")
        job = prepare(wf, ids, pos, seed, args.negative)
        print(f"[{i}/{len(designs)}] {d['id']} | seed {seed} | style {manifest['render_style']}")
        if args.dry_run:
            continue
        data = api(base, "/prompt", {"prompt": job, "client_id": "noveltyforge-local"})
        pid = data.get("prompt_id")
        if not pid:
            raise RuntimeError("ComfyUI did not return prompt_id: " + repr(data))
        record = {"design_id": d["id"], "index": d["number"], "prompt_id": pid,
                  "seed": seed, "style": manifest["render_style"], "state": "submitted",
                  "workflow": str(args.workflow), "reviewed": False}
        ledger["jobs"].append(record)
        save(ledger_path, ledger)
        end = time.monotonic() + args.timeout
        while time.monotonic() < end:
            history = api(base, "/history/" + pid)
            if pid in history:
                result = history[pid]
                status = result.get("status", {})
                if status.get("status_str") == "error":
                    record["state"] = "error"
                    save(ledger_path, ledger)
                    raise RuntimeError("ComfyUI failed: " + str(status)[:1000])
                if status.get("completed") is True or result.get("outputs"):
                    outputs = []
                    for value in result.get("outputs", {}).values():
                        outputs.extend(value.get("images", []))
                    record["state"] = "completed"
                    record["images"] = outputs
                    save(ledger_path, ledger)
                    print("  completed; image references recorded in", ledger_path)
                    break
            time.sleep(args.poll)
        else:
            record["state"] = "timeout"
            save(ledger_path, ledger)
            raise TimeoutError("Timed out; inspect ComfyUI history before retrying (job may still be running)")
    if args.dry_run:
        print("Dry run OK; no jobs submitted.")
    else:
        print("Candidates rendered. No visual originality/appeal review has been performed.")

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", default="noveltyforge-output/manifest.json")
    p.add_argument("--workflow", required=True, help="ComfyUI API-format exported workflow")
    p.add_argument("--positive-node", required=True, help="CLIPTextEncode positive node ID")
    p.add_argument("--negative-node", help="Optional negative CLIPTextEncode node ID")
    p.add_argument("--sampler-node", required=True, help="KSampler node ID")
    p.add_argument("--latent-node", help="Optional EmptyLatentImage node ID; enforces batch_size=1")
    p.add_argument("--negative", default=None, help="Optional negative text to override workflow's negative")
    p.add_argument("--count", type=int, default=1)
    p.add_argument("--ledger", default="noveltyforge-render-jobs.json")
    p.add_argument("--url", default="http://127.0.0.1:8188")
    p.add_argument("--timeout", type=int, default=3600)
    p.add_argument("--poll", type=float, default=3.0)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)
    try:
        if args.timeout <= 0 or args.poll <= 0:
            raise ValueError("timeout and poll must be positive")
        run(args)
        return 0
    except (ValueError, OSError, KeyError, TypeError, RuntimeError, TimeoutError, HTTPError, URLError) as e:
        print("ERROR:", e, file=sys.stderr)
        return 2

if __name__ == "__main__":
    sys.exit(main())
