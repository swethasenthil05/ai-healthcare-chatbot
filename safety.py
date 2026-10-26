
import re

SAFETY_NOTICE = (
    "This chatbot provides general health information, not a diagnosis. "
    "It cannot rule out emergencies. If you have severe or sudden symptoms, "
    "seek urgent professional help. In India, call 112 for an emergency."
)

EMERGENCY_PATTERNS = {
    "Severe difficulty breathing": [
        r"\bcan't breathe\b",
        r"\bcannot breathe\b",
        r"\btrouble breathing\b",
        r"\bdifficulty breathing\b",
        r"\bshortness of breath\b",
        r"\bsevere breathlessness\b",
        r"\bgasping for air\b",
        r"\bstruggling to breathe\b",
        r"\bunable to breathe\b",
    ],
    "Possible heart attack or other serious chest emergency": [
        r"\bchest pain\b",
        r"\bchest pressure\b",
        r"\bchest tightness\b",
        r"\bcrushing chest\b",
        r"\bchest feels heavy\b",
        r"\bchest hurts\b",
        r"\bpressure in my chest\b",
    ],
    "Possible stroke symptoms": [
        r"\bface droop(?:ing)?\b",
        r"\bfacial droop(?:ing)?\b",
        r"\bone[- ]sided weakness\b",
        r"\bweakness on (?:my )?(?:left|right) side\b",
        r"\barm weakness\b",
        r"\bslurred speech\b",
        r"\bsudden trouble speaking\b",
        r"\bsudden difficulty speaking\b",
        r"\bsudden loss of vision\b",
        r"\bsudden vision loss\b",
        r"\bsudden confusion\b",
        r"\bsudden trouble walking\b",
    ],
    "Loss of consciousness or severe confusion": [
        r"\bunconscious\b",
        r"\bpassed out\b",
        r"\bfainted\b",
        r"\bnot waking\b",
        r"\bcan't wake\b",
        r"\bcannot wake\b",
        r"\bsevere confusion\b",
    ],
    "Severe bleeding": [
        r"\bsevere bleeding\b",
        r"\buncontrolled bleeding\b",
        r"\bbleeding will not stop\b",
        r"\bbleeding won't stop\b",
        r"\bbleeding heavily\b",
    ],
    "Possible severe allergic reaction": [
        r"\bthroat closing\b",
        r"\bthroat is closing\b",
        r"\bthroat swelling\b",
        r"\bswollen throat\b",
        r"\btongue swelling\b",
        r"\bswollen tongue\b",
        r"\blips swelling\b",
        r"\bswollen lips\b",
        r"\ballergic reaction.{0,50}(?:breathing|throat|tongue|collapse)\b",
    ],
    "Possible serious abdominal emergency": [
        r"\bsudden severe abdominal pain\b",
        r"\bsudden severe stomach pain\b",
        r"\bsevere abdominal pain\b",
        r"\bsevere stomach pain\b",
        r"\bvomiting blood\b",
        r"\bblood in vomit\b",
    ],
}


def emergency_screen(text):
    """Return (is_emergency_flagged, matching_emergency_labels)."""
    text = (text or "").lower()
    matches = []

    for label, patterns in EMERGENCY_PATTERNS.items():
        if any(re.search(pattern, text) for pattern in patterns):
            matches.append(label)

    return bool(matches), matches


def emergency_response(matches):
    """Build a clear warning when emergency patterns are detected."""
    details = "; ".join(matches)

    return (
        "⚠️ POSSIBLE MEDICAL EMERGENCY\n\n"
        f"Warning signs detected: {details}.\n\n"
        "Please seek urgent professional medical help now. "
        "In India, call 112; elsewhere, call your local emergency number. "
        "Do not wait for this chatbot to assess the symptoms further. "
        "This alert is not a diagnosis."
    )
