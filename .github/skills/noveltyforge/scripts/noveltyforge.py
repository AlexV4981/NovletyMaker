#!/usr/bin/env python3
"""NoveltyForge: preference-gated or explicitly forced unpersonalized concept planning.

Requires only Python 3.10+ stdlib. Produces prompts and manifests; does NOT call an
image model, inspect images, or control an image generator's sampling seed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# Broad combinatorial catalog; original work must still be visually evaluated.
CATALOG: dict[str, list[str]] = {
    "role": [
        "kinetic sculpture restorer", "moon-tide ferry conductor", "arcade-light illusion designer",
        "volcanic glass calligrapher", "royal sound engineer", "cathedral organ tuner",
        "sundial observatory locksmith", "luxury train mystery novelist", "bioluminescent ink cartographer",
        "floating library courier", "clockwork theatre choreographer", "ice-lake regatta navigator",
        "geometric perfume bottle architect", "desert aurora photographer", "mechanical butterfly conservator",
        "seabed porcelain sculptor", "holographic opera costume engineer", "storm-harvesting violin maker",
        "crystal mine safety inspector", "architectural kite artisan", "enchanted bakery sign painter",
        "lost-language tapestry translator", "meteorite jewelry engraver", "subterranean botanical mapmaker",
        "solar-sail shipwright", "fossil-harbor customs officer", "windmill clock maker",
        "gravity-defying circus conductor", "underground racing marshal", "dream-lens optician",
        "royal ice maze designer", "lighthouse prism technician", "festival puppet mechanical designer",
        "reef acoustic researcher", "electric eel aquarium curator", "antique clock auctioneer",
        "sky-garden irrigation architect", "mountain railway signal engineer", "night market projection artist",
        "aurora observatory pilot", "archaeological ceramic illustrator", "magnetic levitation dancer",
    ],
    "silhouette": [
        "dramatic inverted triangle with sharp architectural shoulders and a narrow ankle line",
        "flared umbrella silhouette with a clean fitted waist and rigid skirt supports",
        "long vertical column interrupted by one striking geometric volume",
        "athletic hourglass with a deliberately cropped upper volume",
        "high-waisted rounded balloon trousers beneath a fitted torso",
        "asymmetric trapezoid with one structured hip wing and a straight opposing side",
        "tall narrow silhouette with sculpted neckline and straight split skirt",
        "sculptural bell silhouette supported by layered stiff fabric panels",
        "compact layered silhouette with a strong waist and articulated boots",
        "streamlined uninterrupted bodysuit silhouette with precise cut lines",
        "strong A-line shape with crisp horizontal waist seam and full skirt",
        "diagonal silhouette defined by a single angular fabric panel",
        "short squared vest silhouette above gently tapered utility trousers",
        "slender fitted upper body above wide pleated palazzo trousers",
        "structured cocoon silhouette tapering decisively toward the ankles",
        "two-tier geometric skirt silhouette with negative space between sections",
        "tailored long coat-dress with symmetric, straight-edged vents (not a draped shawl)",
        "asymmetric short jacket and long narrow wrap skirt with sharp tailoring",
        "wide layered collar silhouette with otherwise minimalist body lines",
        "fitted jumpsuit accentuated by rigid semicircular waist harness",
    ],
    "garment_architecture": [
        "one-piece sculpted jumpsuit with sealed seams and detachable rigid shoulder plates",
        "tailored high-collar waistcoat with wide pleated culottes and ribbon-laced oxford boots",
        "architectural strapless gown with sculpted fan pleats and hidden stiffening",
        "short bolero with ribbed bodysuit and voluminous balloon trousers",
        "sleeveless brocade tunic and structured bifurcated overskirt over slim trousers",
        "asymmetrically fastened coat-dress with rigid mandarin collar and narrow waist belt",
        "fitted corset vest and dramatic high-waisted palazzo pants with flat side panels",
        "naval-inspired double-breasted cropped blazer with long pencil skirt and flat boots",
        "pleated suspender dress over a precision-cut high-neck top, with solid-heel boots",
        "geometric breastplate and ribbed stretch underlayer with articulated armored leggings",
        "minimalist high-fashion halter column dress with shaped shoulder jewelry",
        "box-pleated knee dress, clean leg warmers, and tailored fitted gloves",
        "modern cheongsam-inspired fitted dress with side vents and bold linear piping",
        "riding breeches with a fitted asymmetrical vest and polished high boots",
        "tailored shirtdress with broad structured belt and pleated collar insert",
        "short quilted flight vest over fitted coveralls with reinforced knee panels",
        "sculpted jacket with narrow lapels and a sharply pleated short bustle skirt",
        "fitted sleeveless utility tunic over wide-leg trousers, with a geometrically belted waist",
        "one-shoulder draped sash fixed over a *structured* corset and straight-legged trousers",
        "bubble-hem dress with seamed geometric bodice and uninterrupted tights",
        "formal fitted morning-coat and tapered trousers with asymmetrical lapel treatment",
        "reinforced sailor collar top and angular high-rise paneled skirt with low boots",
        "strapless structured peplum bustier over sleek floor-length straight skirt",
        "high-waist cropped trousers, cross-strap tailored top and oversize engineered gloves",
        "slim zip-front catsuit with floating rigid circular collar and low-profile boots",
        "stiff origami-fold mini dress over patterned leggings, with pointed flat boots",
        "sculpted sailor jumpsuit with precise shoulder cutouts and fastened utility belt",
        "fitted coat with modular panels over practical split-skirt trousers",
        "tiered tailored vest and segmented lantern-shaped skirt with attached structured sleeves",
        "sharp waistcoat with flared trumpet trousers and a patterned detachable neck piece",
        "short asymmetric capelet fixed to a tailored sheath dress with strong waist shaping",
        "articulated shell-panel torso armor over close-fitting performance textiles",
        "tall sculpted collar with crisscross sleeveless dress and radial hip pleats",
        "fitted apron-jumpsuit with architectural pockets, hidden closures and slim sleeves",
    ],
    "hair": [
        "cropped charcoal curls with geometric shaved line", "long jet-black microbraids in a fan-shaped bun",
        "blunt copper bob with a single sculpted wave", "short midnight-blue pixie cut with longer front fringe",
        "waist-length auburn rope braids tied into a high knot", "silver-gray short sculpted finger waves",
        "moss-green braided crown with short loose curls", "amber-brown ringlets arranged into a high asymmetric bun",
        "sleek deep-teal pageboy cut", "dark plum spiky short shag with side part",
        "warm chestnut twin looped braids with ribbon-free pins", "ink-black straight blunt shoulder-length cut",
        "pale rose-gold cropped geometric bob", "ochre coils stacked into a sculptural topknot",
        "midnight-blue undercut with thick braided side ponytail", "honey-blonde low chignon with wavy side tendrils",
        "deep violet chin-length layered cut", "cinnamon corkscrew curls swept to one side",
        "icy blue short wave-cut hair with shaved nape", "dark mahogany asymmetrical clavicle-length cut",
        "long ash-brown straight hair with tightly bound hair cuffs", "wine-red small locs in a crown-shaped updo",
        "blue-black hair in a woven basket braid", "golden copper shoulder-length curly shag",
        "sea-glass green short hair with blunt temple fringe", "coffee-brown coiled hair in a compact bun",
        "warm black ribbonless double twist buns", "flaxen blonde braided waterfall half-up hairstyle",
        "aubergine buzzcut with sculpted temple patterns", "smoky lavender braided bob with angular fringe",
    ],
    "palette": [
        "cobalt, soft white, polished bronze, graphite", "mahogany, cream, peridot, dark teal",
        "pearlescent white, ultramarine, shell pink, antique brass", "rust, sage green, deep navy, parchment",
        "obsidian, electric cyan, ice gray, bright vermilion", "peach, bottle green, chocolate brown, pearl",
        "lilac smoke, ecru, blackcurrant, silver", "orchid violet, warm amber, ivory, coffee",
        "amber, midnight indigo, coral, pale sand", "burgundy, muted mint, silver-gray, off-white",
        "citrus yellow, cobalt, white, slate", "petrol teal, copper, alabaster, indigo",
        "cerulean, terracotta, cream, brass", "soft jade, rosewood, midnight navy, nickel",
        "scarlet, graphite, ivory, cyan highlights", "sea-green, plum, pearl, gold foil",
        "blackberry, icy mint, pale gold, oatmeal", "sage, tobacco, stone gray, copper",
        "royal purple, honey amber, cream, soot", "dusty pink, graphite, pearlescent blue, bronze",
        "burnt orange, turquoise, off-white, black", "moonstone blue, cocoa, silver, cherry",
        "warm white, ink black, forest green, rose-gold", "mustard, aubergine, pale blue, espresso",
        "turquoise, orange-red, pearl, dark slate", "glacier blue, maroon, ivory, steel",
        "carmine, moss, clay, antique ivory", "deep olive, gold-leaf, lilac, charcoal",
        "pale yellow, lilac, cobalt, walnut", "smoked violet, copper, aqua, alabaster",
    ],
    "material": [
        "matte tailored wool, brushed gold, polished ceramic", "faceted resin, smooth velvet, silk piping",
        "laser-etched aluminum, technical mesh, matte rubber", "sturdy canvas, translucent glass, braided leather",
        "satin-faced cotton, lacquered wood, bronze inlay", "structured organza, soft twill, aged nickel",
        "hard enamel, crisp taffeta, textured suede", "fine leather, mother-of-pearl, polished steel",
        "embroidered brocade, smooth graphite textile, oxidized brass", "layered chiffon, opaque satin, cut crystal",
        "cool linen, silver thread, smoked glass", "ribbed knit, molded polymer, magnetic hinges",
        "porcelain buttons, heavy linen, silk velvet", "recycled sailcloth, resin trims, polished copper",
        "transparent acrylic, dark satin, hammered bronze", "quilted neoprene, reflective piping, matte ceramic",
        "engraved hardwood, velvet ribbon, pearl beads", "glazed leather, smooth technical fabric, frosted crystal",
        "embroidered denim, opaque resin, gold wire", "woven raffia, satin twill, brushed silver",
    ],
    "motif": [
        "architectural keystones and negative spaces", "abstract frost spirals and ruler marks",
        "measured sound waves and tuned chimes", "triangular solar sails and tension cables",
        "celestial railway signals and switch tracks", "interlocking hexagonal prism facets",
        "ink-splashed calligraphy strokes", "staircase shadows and repeating arch windows",
        "mathematical wave interference patterns", "seed-pod tessellations and radial veins",
        "geometric seashell spirals", "vintage theater ticket perforations",
        "tiny stylized paper cranes", "minimal enamel butterfly wing panels",
        "orbiting bead rings and mechanical hinges", "glacier fracture lines and ice-map contours",
        "origami fan ribs and folded corners", "star-chart grid lines without star symbols",
        "windmill blades and angular gearing", "glowing ink chromatography swatches",
        "abstract fish-scale interference geometry", "meteorite impact ripples and cut facets",
        "sculptural knot geometry", "tiny lighthouse Fresnel prism rays",
        "long ribbonlike signage typography", "interwoven braided rope patterns",
        "floating square lantern grids", "water droplet line graphs and echo ripples",
        "mid-century glass mosaic blocks", "radial compass needles with asymmetrical ticks",
    ],
    "prop": [
        "folding projection slate", "faceted translucent baton", "precision ring calipers",
        "folding enamel map case", "miniature mechanical theatre", "engraved acoustic tuning wheel",
        "portable prism spectrometer", "modular tool clutch", "articulated glassblower shears",
        "sealed message capsule", "filigree camera rig", "tiny kite spool",
        "magnetic loop compass", "transparent drafting tablet", "ornamental telescope with protective case",
        "woven field notebook", "mechanical wind chime tuner", "ceramic pigment tray",
        "luminous score sheet", "clockwork butterfly containment case", "refractive gem pendant analyzer",
        "folding parasol with rigid origami ribs", "compact floor-mapping projector", "glass sample rack",
        "engraved navigation semaphore", "mechanical lace gauge", "holographic cue board",
        "travel easel", "portable sonar ring", "iridescent enamel fan",
        "hour-marked brass gyroscope", "sealed resin specimen case",
    ],
    "personality": [
        "decisive and playful, but protective of personal secrets", "patient and observant with dry humor",
        "warmly theatrical and meticulous", "quiet, razor-sharp, and unshakably curious",
        "good-humored, bold, and impulsively generous", "restrained, disciplined, and privately sentimental",
        "inventive, competitive, and secretly shy", "poised, skeptical, and compassionate",
        "whimsical and socially fearless", "curious, solitary, and fiercely principled",
        "energetic and improvisational", "soft-spoken, proud, and stubborn",
        "pragmatic, mischievous, and inventive", "regal, precise, and unexpectedly kind",
        "calm, witty, and subtly defiant", "restless, thoughtful, and enthusiastic",
    ],
    "pose": [
        "seated side-saddle on a low sculptural step, looking toward the viewer",
        "full-body confident forward stride with one hand at waist",
        "weight shifted onto back foot, one arm lifted to demonstrate a prop",
        "three-quarter reclining pose balanced against a sturdy railing",
        "mid-turn pose showing outfit movement with arms held asymmetrically",
        "kneeling with precision equipment while glancing upward",
        "one knee braced on a platform, body twisting to the side",
        "leaning against a geometric column with crossed ankles",
        "hands clasped behind back, chin gently raised",
        "reaching to calibrate a suspended tool, dynamic diagonal line",
        "perched on a bench with both feet grounded and elbows resting forward",
        "walking away but looking over the shoulder",
        "standing in balanced contrapposto, a compact prop held close",
        "crouched to inspect an artifact with one hand supporting weight",
        "sitting on a low trunk, knees together, prop across lap",
        "spinning lightly on one foot with articulated clothing visible",
    ],
    "camera": [
        "eye-level full-body with generous negative space on the right",
        "slightly elevated three-quarter view, asymmetrically framed",
        "low three-quarter angle emphasizing sculptural clothing volumes",
        "side-profile dominant key art with orthographic views separate",
        "front-facing symmetrical portrait alongside asymmetrically arranged turnarounds",
        "full-body rear three-quarter hero view plus clear front orthographic inset",
        "eye-level candid medium shot with full-body turnaround occupying the main sheet",
        "low frontal shot with dynamic negative space above",
        "seated eye-level composition with torso rotated slightly away",
        "wide camera capturing the full silhouette, character placed off-center",
        "overhead-ish three-quarter angle emphasizing the constructed silhouette",
        "single sweeping diagonal composition balanced by rigid orthographic columns",
    ],
}

ASPECTS = tuple(CATALOG) + ("preference_influence",)
HARD_UNIQUE = ("role", "garment_architecture")
CHECK_FEATURES = ("role", "silhouette", "garment_architecture", "hair", "palette", "material", "motif", "prop")


class PreferenceError(ValueError):
    """The preference gate has not been satisfied."""


def load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError as exc:
        raise ValueError(f"Missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc


def quality_items(profile: dict, field: str, minimum: int) -> list[str]:
    raw = profile.get(field)
    if not isinstance(raw, list):
        raise PreferenceError(f"Preference gate FAIL: '{field}' must be a list.")
    cleaned = [x.strip() for x in raw if isinstance(x, str) and x.strip()]
    if len(set(x.casefold() for x in cleaned)) < minimum:
        raise PreferenceError(f"Preference gate FAIL: provide at least {minimum} distinct '{field}' entries.")
    for entry in cleaned:
        if "replace with" in entry.lower() or "placeholder" in entry.lower():
            raise PreferenceError(f"Preference gate FAIL: '{field}' still has template placeholders.")
    return cleaned


def validate_profile(profile: Any) -> dict:
    if not isinstance(profile, dict):
        raise PreferenceError("Preference gate FAIL: profile must be a JSON object.")
    if profile.get("status") != "confirmed" or profile.get("confirmed_by_user") is not True:
        raise PreferenceError("Preference gate FAIL: current user has not confirmed this preference profile.")
    evidence = profile.get("confirmation_evidence")
    if not isinstance(evidence, str) or len(evidence.strip()) < 10 or "replace with" in evidence.casefold():
        raise PreferenceError("Preference gate FAIL: provide confirmation_evidence describing where the current user's confirmation came from.")
    likes = quality_items(profile, "likes", 3)
    dislikes = quality_items(profile, "dislikes", 2)
    examples = profile.get("rated_examples", [])
    if not isinstance(examples, list):
        raise PreferenceError("Preference gate FAIL: 'rated_examples' must be a list.")
    valid_examples = 0
    for e in examples:
        if not isinstance(e, dict) or not isinstance(e.get("label"), str) or not e["label"].strip():
            raise PreferenceError("Preference gate FAIL: each rated example needs a nonblank label.")
        score = e.get("appeal")
        if isinstance(score, bool) or not isinstance(score, (int, float)) or not 1 <= score <= 10:
            raise PreferenceError("Preference gate FAIL: each rated example appeal must be a number 1–10.")
        valid_examples += 1
    if not valid_examples and profile.get("preference_summary_confirmed") is not True:
        raise PreferenceError("Preference gate FAIL: need a real rated example or an explicitly confirmed preference summary.")
    medium = profile.get("medium", "visual design")
    if not isinstance(medium, str) or not medium.strip():
        raise PreferenceError("Preference gate FAIL: 'medium' must be nonblank text.")
    return {**profile, "likes": likes, "dislikes": dislikes}


def profile_digest(profile: dict) -> str:
    data = json.dumps(profile, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()[:16]


def roll(master_seed: int, character_number: int, attempt: int, aspect: str) -> int:
    """Each aspect is independently determined by a stable keyed cryptographic hash."""
    keyed = f"NoveltyForge-v2|{master_seed}|{character_number}|{attempt}|{aspect}".encode("utf-8")
    stream_seed = int.from_bytes(hashlib.sha256(keyed).digest(), "big")
    return random.Random(stream_seed).randint(1, 1000)


def select_item(options: list[str], value: int) -> str:
    return options[((value - 1) * len(options)) // 1000]


def make_candidate(master_seed: int, number: int, attempt: int) -> dict:
    rolls = {a: roll(master_seed, number, attempt, a) for a in ASPECTS}
    selected = {a: select_item(CATALOG[a], rolls[a]) for a in CATALOG}
    influence = rolls["preference_influence"]
    strength = "subtle" if influence <= 300 else "balanced" if influence <= 750 else "strong"
    return {
        "number": number,
        "candidate_attempt": attempt,
        "rolls_1_to_1000": rolls,
        "preference_translation_strength": strength,
        "selected": selected,
    }


def normalize(s: str) -> str:
    return re.sub(r"[^\w]+", " ", s.casefold()).strip()


def features_of(entry: dict) -> dict[str, str]:
    observed = entry.get("observed_features")
    if isinstance(observed, dict) and observed:
        return {x: str(observed.get(x, entry.get("selected", {}).get(x, ""))) for x in CHECK_FEATURES}
    raw = entry.get("selected", entry.get("features", {}))
    return {x: str(raw.get(x, "")) for x in CHECK_FEATURES} if isinstance(raw, dict) else {}


def collision(candidate: dict, previous: list[dict]) -> str | None:
    c = features_of(candidate)
    for p in previous:
        f = features_of(p)
        for key in HARD_UNIQUE:
            if c.get(key) and f.get(key) and normalize(c[key]) == normalize(f[key]):
                return f"same {key} as previous concept"
        weighted = {"role": 4, "garment_architecture": 4, "silhouette": 3,
                    "motif": 2, "prop": 2, "hair": 1, "palette": 1, "material": 1}
        overlap = sum(w for k, w in weighted.items()
                      if c.get(k) and f.get(k) and normalize(c[k]) == normalize(f[k]))
        if overlap >= 5:
            return f"excessive combined overlap ({overlap})"
    return None


def load_history(path: Path) -> dict:
    if not path.exists():
        return {"history_version": "1.0", "entries": []}
    obj = load_json(path)
    if not isinstance(obj, dict) or not isinstance(obj.get("entries"), list):
        raise ValueError("History must be a JSON object with an 'entries' array.")
    return obj


def char_id(master_seed: int, number: int, attempt: int) -> str:
    source = f"{master_seed}:{number}:{attempt}"
    return "nf-" + hashlib.sha256(source.encode("utf-8")).hexdigest()[:12]


def make_prompt(item: dict, profile: dict, mode: str = "personalized") -> str:
    c = item["selected"]
    if mode == "personalized":
        likes = "\n".join(f"- {x}" for x in profile["likes"])
        dislikes = "\n".join(f"- {x}" for x in profile["dislikes"])
        preference_section = f"""## Preference translation: {item['preference_translation_strength']} emphasis

The current user confirmed these quality criteria. Improve execution without changing the independent concept.

Liked / desired qualities:
{likes}

Disliked / rejected patterns:
{dislikes}

Preference influence is **{item['preference_translation_strength']}**. Ratings alone do not prove which individual traits the user likes.
"""
    elif mode == "unpersonalized-forced":
        preference_section = """## UNPERSONALIZED FORCED MODE — DISCLAIMER

This prompt has **no confirmed user-preference profile**. A user explicitly chose to bypass calibration.
These results can be varied but **are NOT personalized to their taste**. Expect generic aesthetic decisions, weaker appeal consistency, and possible repetition. Do not claim to know the user's preferences.

Apply basic, nonpersonal design craft only: readable silhouettes, coherent material choices, expressive faces and deliberate outfit construction. Do not invent user likes or dislikes. Preference calibration and actual visual review are still recommended.
"""
    else:
        raise ValueError(f"Unknown generation mode: {mode}")
    return f"""# One original character sheet — {item['id']}

Generate **exactly one** original adult character as a polished, production-ready reference sheet. This request is for a **single character only**; no multi-character grid or collage, no second character concept, no variations of earlier AI-made characters.

## Locked independent blueprint

- Narrative role: {c['role']}
- Personality: {c['personality']}
- Silhouette: {c['silhouette']}
- Outfit construction: {c['garment_architecture']}
- Hair: {c['hair']}
- Color harmony: {c['palette']}
- Materials: {c['material']}
- Signature motif: {c['motif']}
- Character-specific prop: {c['prop']}

Treat these as **different, deliberately selected design variables**, not a menu of aesthetics to fuse into a conventional anime costume. Reconcile the details into a coherent and appealing design while preserving the outfit architecture and silhouette. Do not substitute an unplanned generic coat, decorative harness, repeated hair ornament, or previously seen character template.

{preference_section}
## Required reference sheet

- One dominant polished hero illustration: {c['pose']}.
- Hero framing / camera: {c['camera']}.
- Clear front, side, back and optional three-quarter **consistent** full-body views of this same character.
- A small grid of distinctive expressions and eye/face details.
- Exploded garment construction: identifiable separate pieces and fabric/material closeups.
- Props, motif closeups and palette swatches.
- Clean light backdrop, professional panel grid, crisp readability, nothing cropped.
- Varied composition and outfit shape, not a standing, identical three-quarter portrait as a default.

## Final checks

{('Prioritize originality and confirmed user-fit independently.' if mode == 'personalized' else 'Prioritize concept diversity and general craft only; personal user-fit is UNKNOWN in forced mode.')} Do not reuse previous characters' job+outfit+palette+prop clusters, even if they were rated highly. No copied copyrighted franchise character. If the image doesn't obey the spec, flag it for rejection rather than renaming it.
"""


def create_plan(profile: dict, history: dict, count: int, seed: int, mode: str = "personalized") -> dict:
    previous = list(history["entries"])
    designs = []
    for number in range(1, count + 1):
        for attempt in range(1, 5001):
            candidate = make_candidate(seed, number, attempt)
            if not collision(candidate, previous):
                candidate["id"] = char_id(seed, number, attempt)
                designs.append(candidate)
                previous.append(candidate)
                break
        else:
            raise ValueError("Cannot find enough distinct concepts with this history/catalog; expand the catalog or change constraints.")
    return {
        "schema_version": "1.0",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "master_seed": seed,
        "seed_scope": "Local design choices ONLY; not the image generator's seed",
        "generation_mode": mode,
        "personalization_claimed": mode == "personalized",
        "profile_digest": profile_digest(profile) if mode == "personalized" else None,
        "disclaimer": None if mode == "personalized" else (
            "Forced without confirmed preferences: designs are NOT personalized; "
            "originality and quality are NOT guaranteed; visual review is necessary."),
        "count": len(designs),
        "designs": designs,
        "render_protocol": "Generate one image per design, inspect and record after each; never send a collage prompt.",
    }


def atomic_json_write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def plan_cmd(args: argparse.Namespace) -> None:
    if args.force_unpersonalized:
        if not args.acknowledge_disclaimer:
            raise PreferenceError("Forced mode requires --acknowledge-disclaimer. "
                                  "The result is NOT personalized; repetition/quality are not guaranteed.")
        # Deliberately ignore any partial/unverified profile: do not launder guesses as user taste.
        profile = {"status": "unpersonalized", "likes": [], "dislikes": [], "medium": "character reference sheets"}
        mode = "unpersonalized-forced"
    else:
        if args.acknowledge_disclaimer:
            raise PreferenceError("--acknowledge-disclaimer requires --force-unpersonalized.")
        if args.profile is None:
            raise PreferenceError("A user-confirmed --profile is REQUIRED; alternatively, "
                                  "explicitly opt in with --force-unpersonalized --acknowledge-disclaimer.")
        profile = validate_profile(load_json(args.profile))
        mode = "personalized"
    history = load_history(args.history)
    if not 1 <= args.count <= 10:
        raise ValueError("--count must be between 1 and 10; recommend 1 for sequential review.")
    seed = args.seed if args.seed is not None else secrets.randbits(63)
    if seed < 0:
        raise ValueError("--seed must be nonnegative.")
    manifest = create_plan(profile, history, args.count, seed, mode=mode)
    output = args.output
    (output / "prompts").mkdir(parents=True, exist_ok=True)
    atomic_json_write(output / "manifest.json", manifest)
    for item in manifest["designs"]:
        prompt = make_prompt(item, profile, mode=mode)
        (output / "prompts" / f"character-{item['number']:02}.md").write_text(prompt, encoding="utf-8")
    if mode == "personalized":
        print(f"PASS: confirmed preferences used; planned {args.count} distinct blueprint(s).")
    else:
        print("WARNING: FORCED UNPERSONALIZED MODE. No taste calibration was performed.")
        print("WARNING: Results are NOT preference-tailored. Neither originality nor image quality is guaranteed.")
        print(f"Planned {args.count} diverse blueprint(s) using generic design principles.")
    print(f"Master seed: {seed} (local planner ONLY, not the image model)")
    print(f"Saved: {output / 'manifest.json'}")
    print(f"NEXT: generate exactly one prompt/image at a time; VISUALLY inspect, record, then continue.")


def validate_cmd(args: argparse.Namespace) -> None:
    p = validate_profile(load_json(args.profile))
    print(f"PASS: user-confirmed preference gate satisfied for {p['medium']}.")
    print(f"Evidence: {len(p['likes'])} likes,