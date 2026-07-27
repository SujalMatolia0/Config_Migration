import os
from lxml import etree

def capture_unknown(elem, known_attrs=None, known_children=None, context_name=""):
    """
    Captures any unknown attributes and child tags from an XML element.
    Returns a dictionary containing unknown_attrs, unknown_children, and context.
    """
    if known_attrs is None:
        known_attrs = set()
    if known_children is None:
        known_children = set()

    # Case-insensitive attribute matching support for known attrs
    known_attrs_lower = {a.lower() for a in known_attrs}

    unknown = {}

    # 1. Unknown attributes
    unk_attrs = {k: v for k, v in elem.attrib.items() if k.lower() not in known_attrs_lower}
    if unk_attrs:
        unknown["unknown_attrs"] = unk_attrs

    # 2. Unknown child elements
    known_children_lower = {c.lower() for c in known_children}
    unk_children = []
    for child in elem:
        tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        if tag.lower() not in known_children_lower:
            raw_xml = ""
            try:
                raw_xml = etree.tostring(child, encoding="unicode").strip()
                if len(raw_xml) > 300:
                    raw_xml = raw_xml[:300] + "... [truncated]"
            except Exception:
                pass

            unk_children.append({
                "tag": tag,
                "attrs": dict(child.attrib),
                "text": child.text.strip() if child.text else None,
                "raw": raw_xml
            })

    if unk_children:
        unknown["unknown_children"] = unk_children

    if context_name and (unk_attrs or unk_children):
        unknown["context"] = context_name

    return unknown
