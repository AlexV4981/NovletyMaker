# Originality and appeal are two independent evaluations

## Style compliance (separate gate, before originality and appeal)

Select the rendering style once **before** any character design rolls. For `anime-2d`, require hand-drawn-looking anime linework, expressive stylized anime facial features and cel/painterly anime shading; reject photorealism, hyperrealistic facial texture, and realistic CGI appearance. Style is **not** a character theme or archetype, and should never contribute to role, clothing, hair, palette, motif, pose, or composition collision scores.

A wrong-style render must be retried with the **same locked character blueprint**. A repeated concept should instead be rejected by the existing originality firewall. Keep these failure reasons separate in notes and ratings.

## Originality gate (structural)

Check the rendered design, not merely the prompt:

1. **Concept / role:** not a previous job/archetype with a renamed character.
2. **Clothing architecture:** construction truly differs; color changes and accessory swaps do not count.
3. **Silhouette:** contour, volume, proportions, and clothing balance are distinct.
4. **Hair / face identity:** not the same hairstyle or identical expressions with recoloring.
5. **Palette / materials:** coherent, not just a recolored existing outfit.
6. **Motifs / props:** avoid combinations identical to previous work.
7. **Composition:** vary stance, camera direction, framing, and overall staging; don't treat one angle as mandatory.

Immediate rejection: obvious derivative of earlier generated character, even if attractive. If a generated image visibly conflicts with a locked blueprint, reject or regenerate rather than retroactively relabeling it as original. Keep a registry of rejected outputs too, to avoid recycling failures.

## Aesthetic translation

Calibrate to the **individual user's evidenced preferences**. Possible dimensions for evaluation, not universal goals:

- Face expression, eyes, hairstyle rendering, readability.
- Outfit cohesiveness, fit, structure, and visual hierarchy.
- Palette compatibility, contrast, materials, finish.
- Ornament distribution and motif intent (neither empty nor noisy unless the user likes that).
- Pose/camera/composition balance and artwork polish.

No fixed theme, palette, character type, or gender is inherently preferred. User ratings override agent predictions.

## Scores / feedback

Keep two independent fields per design: `originality_rating` and `appeal_rating`, 1–10, or null if not yet rated. Label `rated_by` as user vs. agent. Do not turn a 6–7/10 into a claim of success at 9–10/10. For mixed scores, improve process without becoming derivative:

- High originality / low appeal: keep the original concept architecture; refine *execution* or reroll a new concept rather than copying past winners.
- High appeal / low originality: reject as derivative, even if polished.
- High both: learn general quality cues and protect diversity.
- Low both: reject and reroll.

Suggested batch size: one character per generated image, optionally 2–3 consecutive characters per user request with a check after each. Distinguish "planned batch count" from "rendered sequentially"; scripts do not generate or inspect images by themselves.
