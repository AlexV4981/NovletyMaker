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
        "short quilte