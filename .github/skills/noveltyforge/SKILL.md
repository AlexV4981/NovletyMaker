---
name: noveltyforge
description: Preference-guided original visual generation. First establish the user's real likes and dislikes or explicitly enter a warned unpersonalized force mode. Randomize design architecture independently, translate taste into execution quality rather than a repeated template, and review results sequentially for repetition. Particularly useful for novel character sheets and multi-concept image requests.
---

# NoveltyForge — Preference-Guided Original Creation

> **READ THIS BEFORE GENERATING:** NoveltyForge does **not automatically know or learn anyone's taste**. A user must do the work of teaching the agent their preferences through confirmed likes, dislikes, examples, and feedback—unless the agent already has reliable, authorized access to those preferences. A person may explicitly **force generation without calibration**, but results are then **UNPERSONALIZED** and must be labeled as such. Neither mode guarantees originality or quality.

## What this skill actually does

NoveltyForge is an **agent instruction workflow plus an optional Python planning script**. It is **not** a replacement image model, a fine-tuning method, an image-generation engine, or a hidden sampling-seed controller. It aims to **reduce, not eliminate**, repeated characters, recolors, and familiar visual formulas.

It separates independent design choices from aesthetics:

1. **Preference discovery**: establish what *this user* likes/dislikes, using credible evidence.
2. **Design divergence**: independently roll fresh narrative, silhouette, garment architecture, hairstyle, palette, material, motifs, props, and composition for each design. The bundled planner uses reproducible per-aspect **1–1000** rolls; these are *planning* seeds, not an image model's seed.
3. **Translation, not copying**: use the user's confirmed preferences to improve craftsmanship (shape hierarchy, appealing face, detail balance, cohesive clothing, texture, etc.), without turning every concept into a variant of a previously liked image. Do not infer specific liked features from ratings without explanations.
4. **Novelty check**: compare the proposed design to the known archive, including *rejected* designs, to avoid renamed/recolored copies, repeated job+outfit combinations, and near-derivative silhouettes. Script checks are **exact/weighted feature matches only**; semantic and visual judgment remains the agent's responsibility.
5. **Sequential rendering and visual review**: one design in one image request, inspect the *actual result*, reject and redesign derivative outputs before proceeding to the next. If inspection isn't possible, disclose that visual validation was not performed.
6. **Feedback**: collect distinct originality and appeal ratings. Keep user scores separate from agent estimates; use feedback to improve preference criteria without cloning previous high scorers.

**Scope:** The bundled Python catalog and reference-sheet prompts currently focus on original **adult character designs**. The conceptual procedure can inform other creative media, but the provided script does not claim native creature, logo, animation, or arbitrary-style support.

## Mandatory mode selection

### Default: personalized mode (the intended workflow)

Before rolling designs or calling the image generator, use existing **verified, authorized** user preference context if accessible. Do not ask people to repeat information the agent can genuinely access and verify. If accessible evidence is incomplete, ask for missing feedback; do not silently manufacture it.

For script-based planning, the user-confirmed profile needs:
- At least **3** specific likes or desired qualities.
- At least **2** specific dislikes or repeated failure modes.
- At least **1** user-given appeal rating (1–10) **or** an explicitly confirmed preference summary.
- `status: "confirmed"`, `confirmed_by_user: true`, and real `confirmation_evidence` identifying where the user confirmed the information.

The flags are a **self-reported record**; the program cannot independently prove confirmation. The agent/operator must ensure they reflect actual user statements. Do not include a personal profile in a public skill repository without permission.

If the AI already knows the user's preferences, the operator still must **translate them into the profile** for the CLI; the script cannot read the agent's memory or conversations by itself.

```bash
SKILL=.github/skills/noveltyforge
python "$SKILL/scripts/noveltyforge.py" validate-profile --profile ./my-preferences.json
python "$SKILL/scripts/noveltyforge.py" plan \
  --profile ./my-preferences.json --history ./noveltyforge-history.json \
  --count 1 --output ./noveltyforge-output
```

See `references/profile-guide.md` and `references/profile-template.json`.

### Optional override: forced unpersonalized mode

**Only if the USER explicitly requests to proceed without teaching/confirming preferences**, explain this disclaimer in plain language **before generating**:

> **Unpersonalized generation warning:** I don't have a confirmed profile of your aesthetic preferences, so I will use general visual design principles rather than your personal taste. The result may still be original and appealing, but it may be generic, repeat familiar patterns, or miss your preferences. This skill reduces the risk of repetition; it cannot guarantee novelty, aesthetic quality, or adherence by the image model. You can improve results by sharing likes, dislikes, ratings, and reference feedback.

If the user opts in, run the explicit bypass (never silently enable it):

```bash
SKILL=.github/skills/noveltyforge
python "$SKILL/scripts/noveltyforge.py" plan \
  --force-unpersonalized --acknowledge-disclaimer \
  --history ./noveltyforge-history.json --count 1 \
  --output ./noveltyforge-output
```

The CLI requires **both flags**, prints a warning, marks the manifest `generation_mode: "unpersonalized-forced"` and `personalization_claimed: false`, and includes the warning in image prompts. **Do not call these results tailored or preference-calibrated.** Never auto-bypass just because gathering preferences seems inconvenient.

## Implementation protocol

**Stage 1 — Independent blueprint.** Once a mode is established, use fresh independent random streams for role, silhouette, clothing construction, hair, palette, materials, motifs, props, personality, pose, camera, and preference influence. Save the manifest. Do not default all concepts to one genre, coat shape, face, or palette. Random selection alone does not guarantee visual difference.

**Stage 2 — Pre-render originality gate.** Check against *known, accessible* prior designs. Reject conceptual derivatives before prompt writing, especially if multiple dimensions repeat. No name swaps, recolors, familiar draped jackets, recycled symbols/props, or slight changes of pose as a substitute for novelty. A previously liked example is not a template.

**Stage 3 — Taste translation.** In personalized mode, apply supported aesthetic preferences to **execution quality** (facial expressiveness, detail coherence, material rendering, proportions, color relationships), without overriding the randomly locked identity. In forced mode, only use general craft principles—**do not claim to know the user's tastes**.

**Stage 4 — One image per design.** Prepare a reference sheet prompt for **one character**. Ask for consistent orthographic turnarounds, expression studies, construction notes, hero illustration, and component callouts when the user requests a sheet. Do not pass multiple separate character briefs in a single image call. A `--count 3` plan prepares three *concepts* but never constitutes three sequential *renders*.

**Stage 5 — Visual inspection.** Inspect actual images *after each render*. Reject collages and repeated outfits/visual clusters. Generate a truly different design blueprint for retries, not a relabel or recolor. Inspect and record the rejection in history too. If unavailable, label visual inspection as **not completed**.

**Stage 6 — Ratings.** Record originality and aesthetic quality separately. Use user-given scores and any reasoning. Never invent a rating or promise 8+/10 quality. When history is incomplete, disclose it; nothing here tests novelty against all existing artwork.

## Strict sequential commands

```bash
SKILL=.github/skills/noveltyforge
python "$SKILL/scripts/noveltyforge.py" plan --profile ./my-preferences.json \
  --history ./noveltyforge-history.json --count 1 --output ./noveltyforge-output

# Read noveltyforge-output/prompts/character-01.md.
# Render ONE image. Inspect the actual image, then record accepted or rejected.
python "$SKILL/scripts/noveltyforge.py" record \
  --manifest ./noveltyforge-output/manifest.json --index 1 \
  --history ./noveltyforge-history.json --status accepted --visual-check \
  --notes "Compared real rendered outfit and silhouette with the history"

# Re-plan and render the next design only AFTER recording the prior result.
```

The `--visual-check` flag is an operator **attestation**, not automatic computer vision. Do not set it when nobody has inspected the rendered image.

## Preflight: never skip

- [ ] User preference mode or explicitly **user-approved** forced mode has been determined.
- [ ] If personalized: likes/dislikes and rating or user-approved summary exist; do not hallucinate profile evidence.
- [ ] If forced: warning shown first, acknowledgement obtained, manifest and prompts marked **UNPERSONALIZED**.
- [ ] Distinct per-aspect rolls are recorded or any unverified manual process is disclosed.
- [ ] Novel concept checked against available accepted **and rejected** history.
- [ ] Preferences inform quality but do not mandate particular recurring clothing, props, hairstyle, pose, or composition.
- [ ] Exactly one character per image request. Evaluate visible result before moving to the next.
- [ ] Clearly distinguish planned originality controls from *proven* visual originality.

## Limits and safety of claims

A skill file cannot force a model to load or follow it, directly manipulate the image generator, or guarantee a lower repetition rate numerically. The planner can catch exact/weighted catalog overlaps; it cannot detect every semantic or visual near-copy without an inspecting agent. Originality means **novelty relative to the available comparison set**, not proof of absolute originality. A person who hasn't trained the agent on their preferences should expect **non-personalized** results unless they provide that information. The whole point is **reduced repetition with transparent limitations**, not magical automatic preference learning.
