# Nitro V: NoveltyForge + local ComfyUI

This is an **optional downstream renderer** for NoveltyForge's existing planning skill. It does not replace the planner, style-lock rules, history firewall or preference gate. It requires Python 3.10+ and the Python standard library. It is designed for a Windows Nitro V / RTX 4050 6 GB VRAM and a **local** ComfyUI server.

## What's supported

- Generate separate NoveltyForge prompts using **existing** `noveltyforge.py` commands, with `--style anime-2d` (the current default).
- Submit 1–10 pre-planned characters *sequentially* as ComfyUI API jobs. One latent per call when `--latent-node` is supplied. The adapter never submits a panorama or a batch of multiple unrelated concepts.
- Use separate deterministic image seeds for distinct planned characters. This does not guarantee visual uniqueness.
- Keep a JSON job ledger recording seed, design ID, ComfyUI prompt ID and output references. Images remain in ComfyUI's output folder.
- **No automatic visual acceptance.** After rendering, review actual images; then explicitly call NoveltyForge `record` to save accepted/rejected history. Bulk candidate exploration is compatible with this requirement, but novelty claims require visual inspection.

### Before starting

1. Install ComfyUI Desktop (Windows, NVIDIA backend), launch it, and confirm one image works.
2. Install one **SDXL-compatible** anime checkpoint (e.g. Illustrious XL) into the checkpoint directory displayed by your ComfyUI install. In ComfyUI select that checkpoint. Start at 768×1152, batch 1; adjust steps and CFG based on the checkpoint.
3. Assemble a standard SDXL text-to-image graph: `CheckpointLoaderSimple → CLIPTextEncode` (positive and negative) → `KSampler` → `VAEDecode` → `SaveImage`. Add `EmptyLatentImage` with `batch_size: 1`.
4. **Export API-format workflow**, not the normal editor/workflow JSON. In ComfyUI enable developer options/API export if necessary, then save the resulting file as `workflow_api.json` in your clone. Confirm its top-level JSON keys are numeric node IDs and each value has `class_type` and `inputs`.
5. Determine node IDs in the API workflow: positive `CLIPTextEncode`, negative `CLIPTextEncode`, `KSampler`, `EmptyLatentImage`. These IDs are specific to YOUR workflow. The examples below use 6, 7, 3, 5 **only as placeholders**.
6. Keep ComfyUI open and available at `http://127.0.0.1:8188`. If ComfyUI uses another port, pass `--url`. This bridge deliberately refuses remote hosts.

### Preference profile

NoveltyForge does **not** automatically import chats, Pinterest archives or training ratings. Create a private `my-preferences.json` by copying `.github/skills/noveltyforge/references/profile-template.json`, and fill it with **your actually confirmed** likes/dislikes, scores and their evidence. Do not commit that file to a public repository.

To use image references in ComfyUI, add a compatible SDXL IP-Adapter node *manually* to your workflow and test the graph first. The adapter here changes only text/seed; it does not yet provide an image-ingestion or LoRA-training API. Start with the text-only checkpoint so you can attribute results correctly.

### Windows PowerShell commands

```powershell
git clone --branch feature/nitrov-comfyui-bridge https://github.com/AlexV4981/NovletyMaker.git
cd NovletyMaker

$skill = ".github/skills/noveltyforge"
Copy-Item "$skill/references/profile-template.json" "my-preferences.json"
notepad my-preferences.json
py -3 "$skill/scripts/noveltyforge.py" validate-profile --profile my-preferences.json

py -3 "$skill/scripts/noveltyforge.py" plan --profile my-preferences.json --style anime-2d --count 3 --output noveltyforge-output

# IMPORTANT: replace these example node IDs with YOUR own API workflow IDs
py -3 "$skill/scripts/comfyui_bridge.py" --manifest noveltyforge-output/manifest.json --workflow workflow_api.json --positive-node 6 --negative-node 7 --sampler-node 3 --latent-node 5 --count 3 --dry-run

# If dry-run passes AND ComfyUI is running, omit --dry-run:
py -3 "$skill/scripts/comfyui_bridge.py" --manifest noveltyforge-output/manifest.json --workflow workflow_api.json --positive-node 6 --negative-node 7 --sampler-node 3 --latent-node 5 --count 3
```

The planner hard-limits a batch to **10** designs. For 100 candidates, plan/render/review successive batches of up to ten, keeping a persistent history and job ledger. **Do not run `record --visual-check` automatically**: it is an attestation that the output was actually examined. A long run may be slower on a 6 GB GPU; leave laptop plugged in and ventilated, prevent sleep, and verify resource usage before overnight work.

### Record the result after inspecting images

```powershell
py -3 "$skill/scripts/noveltyforge.py" record --manifest noveltyforge-output/manifest.json --index 1 --history noveltyforge-history.json --status accepted --visual-check --notes "I inspected the output; silhouette and costume differ from my existing characters" --image-path "PATH-TO-YOUR-IMAGE"
```

For a rejection, add `--status rejected --reason "why the render failed"` instead of accepted. Appeal/originality scores are recorded separately; only use `--rated-by user` for scores actually given by the user.

### Troubleshooting

- **Missing node ID**: inspect `workflow_api.json` and use its actual node identifiers.
- **Not API-format workflow**: export from ComfyUI in API format, not the normal graph layout JSON.
- **Out of memory on RTX 4050**: lower resolution, use one latent, avoid large upscale workflows, or use low-VRAM ComfyUI options.
- **Output images not in ledger**: ensure your workflow includes `SaveImage`; the ledger references ComfyUI output names rather than copying image bytes.
- **Timeout**: a job may remain queued/running; inspect ComfyUI's queue/history before retrying to avoid duplication.
- **Model won't obey huge character-sheet prompt**: use shorter positive prompts or split character ideation and turnaround construction into distinct steps. A single diffusion pass is not guaranteed to produce consistent front/side/back views.
- **Long unattended queue**: this adapter checks job completion, NOT originality, appeal or style compliance. The human review gate still applies.

### Test

```powershell
py -3 -m unittest discover -s .github/skills/noveltyforge/tests -v
```

Nothing in this integration installs a model, trains a LoRA, rates images automatically, or secretly changes your primary PC.
