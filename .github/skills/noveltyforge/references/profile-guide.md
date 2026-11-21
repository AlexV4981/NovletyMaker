# User preference training and forced-use guidance

## Teach the AI your taste; do not assume automatic learning

NoveltyForge does not know anyone's personal tastes and cannot access an agent's memory on its own. The user must supply confirmed likes/dislikes and preferably rated examples with explanations, **or** an authorized agent must already have accessible, reliable user statements. In the latter case, reuse actual evidence and avoid asking the user to repeat known preferences.

Minimum personalized CLI profile:
- `status: "confirmed"`, `confirmed_by_user: true`, and a non-placeholder `confirmation_evidence` describing genuine current-user approval.
- At least three specific likes / quality criteria.
- At least two specific dislikes / known repetitive patterns.
- One rated example with 1–10 appeal or `preference_summary_confirmed: true` reflecting an actual user confirmation.

These fields are a checkable declaration, not cryptographic proof of consent; the agent/human is responsible for truthfulness.

Useful minimal questions: "Which 2–3 examples do you like and dislike, and why?" and "Does this summary reflect your taste?" Collect actual observations and avoid turning the examples into clothing templates.

## If the user explicitly wants generation without teaching their preferences

Tell them: **This run will be unpersonalized.** The AI will use general design craft, not their tastes. Results may be attractive, but may also be generic, derivative, or aesthetically mismatched, and no reduction in repetition or level of originality is guaranteed. The force option skips preference calibration; it does not remove the need to inspect actual generated images.

Only after the user actively opts in, use:

`python scripts/noveltyforge.py plan --force-unpersonalized --acknowledge-disclaimer --count 1`

Never silently switch to this mode if a profile is missing, and never claim that the forced output matches the user's preferences.

## Ratings and feedback

A 7/10 overall appeal score indicates overall preference, not that every garment, hair choice, pose, palette, or motif was liked. Only attribute reasons the user explicitly gives. Track originality separately from aesthetic quality; preserve negative examples and derivative failures in history to avoid repeating them.

## Privacy and updates

Store user profiles locally or in authorized private storage. Do not add real user ratings, images, or profile files to public GitHub source control without consent. Update the profile when feedback arrives; the user's latest explicit feedback wins in case of conflict.
