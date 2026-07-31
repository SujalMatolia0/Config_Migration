import os
from lxml import etree

from src.parsers.known_tags_registry import is_known_tag, is_known_attr

def capture_unknown(elem, known_attrs=None, known_children=None, context_name=""):
    """
    Captures any unknown attributes and child tags from an XML element.
    Cross-checks local sets and the global tag registry superset.
    Returns a dictionary containing unknown_attrs, unknown_children, and context.
    """
    if known_attrs is None:
        known_attrs = set()
    if known_children is None:
        known_children = set()

    known_attrs_lower = {a.lower() for a in known_attrs}
    known_children_lower = {c.lower() for c in known_children}

    unknown = {}

    # 1. Unknown attributes (locally unknown)
    unk_attrs = {}
    for k, v in elem.attrib.items():
        if k.lower() not in known_attrs_lower:
            unk_attrs[k] = {
                "value": str(v),
                "recognized_in_other_component": is_known_attr(k)
            }
    if unk_attrs:
        unknown["unknown_attrs"] = unk_attrs

    # 2. Unknown child elements (locally unknown)
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
                "raw": raw_xml,
                "recognized_in_other_component": is_known_tag(tag)
            })

    if unk_children:
        unknown["unknown_children"] = unk_children

    if context_name and (unk_attrs or unk_children):
        unknown["context"] = context_name

    return unknown

def capture_unknown_recursive(root, known_tags_full_set=None, known_attrs_full_set=None, context_name=""):
    """
    Recursively walks the entire XML tree under root, inspecting every element and attribute.
    Records ancestor path (e.g. 'nodes > node_item > cols > cols_item') for each unknown item.
    Returns a dictionary containing unknown_attrs, unknown_children, and context.
    """
    if known_tags_full_set is None:
        known_tags_full_set = set()
    if known_attrs_full_set is None:
        known_attrs_full_set = set()

    known_tags_lower = {t.lower() for t in known_tags_full_set}
    known_attrs_lower = {a.lower() for a in known_attrs_full_set}

    unknown = {}
    unk_attrs = {}
    unk_children = []

    def get_path(elem):
        path_parts = []
        curr = elem
        while curr is not None:
            if isinstance(curr.tag, str):
                path_parts.append(curr.tag.split("}")[-1])
            curr = curr.getparent()
        return " > ".join(reversed(path_parts))

    # Single pass iteration over full tree
    for elem in root.iter():
        if not isinstance(elem.tag, str):
            continue

        tag = elem.tag.split("}")[-1]
        elem_path = get_path(elem)

        # Check attributes of current element
        for k, v in elem.attrib.items():
            attr_name = k.split("}")[-1] if "}" in k else k
            if attr_name.lower() not in known_attrs_lower:
                attr_key = f"{elem_path} @ {attr_name}"
                unk_attrs[attr_key] = {
                    "attribute": attr_name,
                    "value": str(v),
                    "path": elem_path,
                    "recognized_in_other_component": is_known_attr(attr_name)
                }

        # Check element tag (except root element itself if root tag is known)
        if elem is not root and tag.lower() not in known_tags_lower:
            raw_xml = ""
            try:
                raw_xml = etree.tostring(elem, encoding="unicode").strip()
                if len(raw_xml) > 300:
                    raw_xml = raw_xml[:300] + "... [truncated]"
            except Exception:
                pass

            unk_children.append({
                "tag": tag,
                "path": elem_path,
                "attrs": dict(elem.attrib),
                "text": elem.text.strip() if elem.text else None,
                "raw": raw_xml,
                "recognized_in_other_component": is_known_tag(tag)
            })

    if unk_attrs:
        unknown["unknown_attrs"] = unk_attrs
    if unk_children:
        unknown["unknown_children"] = unk_children
    if context_name and (unk_attrs or unk_children):
        unknown["context"] = context_name

    return unknown
