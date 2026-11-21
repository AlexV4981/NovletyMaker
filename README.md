# NoveltyForge

**Preference-Guided Original Creation — an agent skill to reduce repeated AI character designs without turning someone's taste into a rigid template.**

> **Important: this is not automatic personalization.** The user needs to **teach the AI their actual preferences** (likes, dislikes, ratings, examples, and feedback), *or* the AI must already have reliable access to that information. The Python tool cannot read chat history or AI memory by itself. Users can force an **unpersonalized** run with an explicit override and disclaimer. **NoveltyForge aims to reduce repetition, not guarantee it.**

## What it does—and what it does not

NoveltyForge is a **GitHub-compatible Agent Skill plus a standard-library Python prompt planner**, not an image generator or model fine-tune. It intentionally separates *what is designed* from *how it is aesthetically refined*:

1. **Preference gate:** Identify the current user's confirmed likes, dislikes, and examples. If the agent already knows these from authorized context, use that evidence rather than re-interviewing the user. Otherwise, the user must supply it. Never infer personal taste from a vague genre or from the skill author's taste.
2. **Independent design selection:** Use reproducible, separate 1–1000 rolls for concept, silhouette, outfit architecture, hairstyle, palette, materials, motifs, props, personality, and composition. This randomization changes **the prompt's content**, not the image model's internal sampling seed.
3. **Preference-translation layer:** Apply taste as execution criteria—shape language, faces, coordination, material/detail quality—**without cloning a previously liked design**.
4. **Originality firewall:** Check the current blueprint against known accepted and rejected designs. The script catches exact/weighted catalog collisions; the AI/human must still detect **semantic and visual** lookalikes.
5. **Sequential review:** One character per image call. Review the *rendered image* before moving on; discard derivative results rather than merely renaming or recoloring them.
6. **Ratings:** Track **originality and aesthetic appeal separately**. Learn from actual user feedback without treating one favored design as an archetype to repeat.

**Expected effect:** a more deliberate process that should **reduce the chance** of repetitive, derivative visual generations. **Not guaranteed:** 0 repeated designs, matching another model's image quality, automatic memory access, 8+/10 appeal, uniqueness relative to the whole internet, or perfect prompt compliance.

## Preference requirement (read before using)

To use **personalized mode**, the operator must fill a local, *user-confirmed* JSON profile containing:

- At least **three** specific liked qualities.
- At least **two** dislikes or failure patterns.
- At least **one** scored example **or** explicit confirmation of a preference summary.
- Evidence of where and how the user confirmed their profile.

**The user does the heavy lifting of communicating taste**. An agent can help conduct an image-rating survey, summarize the results, and ask the user to confirm—but cannot assume that unknown preferences magically exist. A rated design is evidence of **overall appeal**; it does not prove the user liked its hair, clothing, role, or palette unless they say so.

The script enforces field presence, but it cannot independently prove that the provided confirmation evidence is genuine. The operator is responsible for accuracy. Never commit a person's real preference profile to a public GitHub repo without consent.

### If you want to skip preference training

**Forced, unpersonalized mode** is available **only by explicit user choice**. The user should first see this warning:

> **Unpersonalized generation warning:** The AI doesn't have a confirmed profile of your personal aesthetic taste. It will rely on general design principles, so images might be generic, repeat familiar motifs, or miss your preferred look. NoveltyForge is designed to reduce repetition—not eliminate it—and it cannot guarantee originality, appeal, or image-model compliance. Supplying likes, dislikes, and ratings is the best way to make results preference-aware.

The program **requires both** `--force-unpersonalized` and `--acknowledge-disclaimer` to proceed without a profile. All manifests and prompts explicitly label the mode as unpersonalized. The AI must not quietly switch modes or advertise these results as calibrated to the user.

## Repository installation

Place the skill directory inside a GitHub repository:

```text
.github/
  skills/
    noveltyforge/
      SKILL.md
      scripts/noveltyforge.py
      references/profile-template.json
      references/history-template.json
      references/profile-guide.md
      references/originality-appeal-rubric.md
      tests/test_noveltyforge.py
```

Compatible GitHub Copilot agents that support repository Agent Skills can discover `SKILL.md`. Other agents must load the instructions according to their own skill system. The skill cannot compel an AI that does not support or follow skills.

## Preselect the art style — independent of originality

Choose the **rendering medium before planning characters**. Style is a fixed rendering contract, not a randomly sampled character archetype. It does not participate in novelty rolls, collision scoring, character IDs, role/silhouette/outfit selection, or preference-influence strength.

The default is `anime-2d`: **drawn 2D anime art only**, including stylized anime faces, clean linework and cel shading; **no hyperrealistic skin, photorealism, or CGI-looking characters**. This is a visual treatment and does **not** force gothic fashion, a standard anime costume, a repeated hairstyle, color palette, or a character archetype.

Choose explicitly with:

```bash
python .github/skills/noveltyforge/scripts/noveltyforge.py plan \
  --profile ./my-preferences.json --style anime-2d \
  --history ./noveltyforge-history.json --count 1 \
  --output ./noveltyforge-output
```

Available rendering contracts: `anime-2d` (default), `illustration-2d`, `painterly-2d`, `stylized-3d`. The manifest stores `render_style` and `render_style_contract`; every generated prompt puts the immutable style lock **before** the independently rolled design blueprint. When a renderer violates style, reject/regenerate the image **without** re-rolling an otherwise original design. Visual compliance must still be inspected; this is a prompt/planner constraint, not a guarantee that the image model will obey it.

## Quick start — personalized (recommended)

Copy `references/profile-template.json` to a **private/untracked** file, then fill it based on real user confirmation:

```bash
SKILL=.github/skills/noveltyforge
python "$SKILL/scripts/noveltyforge.py" validate-profile --profile ./my-preferences.json
python "$SKILL/scripts/noveltyforge.py" plan --profile ./my-preferences.json \
  --history ./noveltyforge-history.json --count 1 --output ./noveltyforge-output
```

Read `noveltyforge-output/prompts/character-01.md`, generate **one image**, inspect that actual image, then record the result:

```bash
python "$SKILL/scripts/noveltyforge.py" record \
  --manifest ./noveltyforge-output/manifest.json --index 1 \
  --history ./noveltyforge-history.json --status accepted --visual-check \
  --notes "Reviewed the rendered silhouette, garment construction, motifs, and prior history"
```

Repeat only after this visual review. A `--count 3` planning command creates three blueprints; it does **not** render or validate three images automatically.

## Quick start — forced without preferences

After the user explicitly agrees to the warning:

```bash
SKILL=.github/skills/noveltyforge
python "$SKILL/scripts/noveltyforge.py" plan \
  --force-unpersonalized --acknowledge-disclaimer \
  --history ./noveltyforge-history.json --count 1 \
  --output ./noveltyforge-output
```

Output manifest fields include `generation_mode: "unpersonalized-forced"`, `personalization_claimed: false`, and a disclaimer. Output prompts contain the same warning. **Do not claim these images match the user's preferences.**

## Test

```bash
python -m unittest discover -s .github/skills/noveltyforge/tests -v
```

The planner uses Python 3.10+ and no external Python dependencies.

## Boundaries

- The bundled catalog and prompt formatter specialize in **adult character reference sheets**. The broader process can be adapted to other creative media, but those modes are not implemented in the bundled code.
- Design-selection seeds are reproducible locally; **image-model internal seeds are not controlled**.
- Exact/weighted feature collision checks are only a first filter; visual similarity must be judged separately.
- User ratings reflect what they liked, not a transferable universal ideal; avoid turning favorites into templates.
- Preserve personal preference and history files privately unless the user explicitly authorizes publication.
- Results depend on the downstream agent, image model, and available history. **No numeric reduction in repetition has been validated.**

## License

MIT.
