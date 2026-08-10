"""
OSVC Workspace and Object XML Parsers
"""
from .workspace_parser import parse_workspace_xml
from .object_parser import parse_object_xml

__all__ = ["parse_workspace_xml", "parse_object_xml"]
