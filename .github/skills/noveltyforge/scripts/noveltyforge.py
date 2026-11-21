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
        "satin-faced cotton, lacquered wood, bronze inlay", "stru