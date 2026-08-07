"""
Centralized, unified tag and attribute registry for OSVC components.
Reconciles known XML tags and attributes across Workspaces, Business Rules,
Analytics Reports, CPM Event Procedures, Navigation Sets, and BUI Add-Ins.
"""

KNOWN_WORKSPACE_ATTRS = {
    "type", "uitype", "serverversion", "clientversion", "ismultiedit", "id", "name",
    "browsercompatibilitymode", "spellcheckallowcancel", "spellcheckonsave"
}

KNOWN_WORKSPACE_CHILDREN = {
    "table", "tabset", "recordtypes", "recordtype", "info", "infoitem", "rules", "rule",
    "triggers", "trigger", "conditions", "condition", "then", "else", "action", "field",
    "menu", "browser", "relationshipitem", "report", "addinitem", "titlebar",
    "spacer", "links", "linkitem", "flag", "quickaccesstoolbar", "ribbon", "tab", "property"
}

KNOWN_TABSET_ATTRS = {
    "id", "row", "column", "rowspan", "columnspan", "summarypanelheight", "summarypanelalignment",
    "canreordertabs", "wraptabs", "summarytab", "thresholdheight", "tabdisplaystyle", "margin", "tabindex"
}
KNOWN_TABSET_CHILDREN = {"tab"}

KNOWN_TAB_ATTRS = {"text", "textlabelname", "id", "row", "column", "textcolor"}
KNOWN_TAB_CHILDREN = {
    "table", "field", "relationshipitem", "report", "browser", "addinitem",
    "menu", "titlebar", "spacer", "tabset"
}

KNOWN_FIELD_ATTRS = {
    "objectid", "fieldid", "labeltext", "id", "row", "column", "defaultphonetype", "defaultvalue",
    "initialvalue", "value", "reportid", "readonlyoption", "hiddenoption", "requiredoption",
    "acceptsreturn", "booleanrenderview", "height", "layoutlabelalignment", "multiline",
    "requiredforsolved", "rowspan", "columnspan", "showparent", "spellcheck", "tabindex", "trimtextwhitespace",
    "disableemailicon"
}
KNOWN_FIELD_CHILDREN = set()

KNOWN_RELATIONSHIP_ATTRS = {
    "itemtype", "acid", "id", "row", "column", "executeonnew", "showreadtransactions",
    "defaultchannelfornote", "searchreportid", "cansendonsave", "canusesmartassistant",
    "defaultchannelforcustomerentry", "defaultthreadonnew", "statuschangeonresponse",
    "alwaysshowemailheader", "alwaysuseplaintext", "canaddbcc", "canaddcc", "canaddcustomerentry",
    "canaddnote", "canaddresponse", "canfollowincidentlinks", "canfollowlinks", "cansearchkb",
    "cantoggletoplaintext", "commitresponseonsave", "confirmresponse", "defaultthreadonedit",
    "defaulttoplaintext", "delayreportexecution", "font", "isusingdefaultemailfont", "margin",
    "padding", "reassignonresponse", "responsepanelcoupled", "sendresponsedefault", "showrowcount",
    "threadorientation", "thumbnailsenabled", "thumbnailsthreshold", "filteronprimarykeyonly",
    "refreshreportondatachange", "tabindex", "canusestandardtext", "hidereportcommands",
    "layoutlabelalignment", "layoutlabelposition", "readonlyoption"
}
KNOWN_RELATIONSHIP_CHILDREN = set()

KNOWN_BROWSER_ATTRS = {
    "url", "suppresserrors", "id", "height", "width", "row", "column", "delaypageload",
    "sendurlaspostdata", "setfixedheight", "childbrowsers", "tabindex", "httpmethod", "postdata"
}
KNOWN_BROWSER_CHILDREN = set()

KNOWN_ADDIN_ATTRS = {
    "itemtype", "addinname", "fileid", "buiextension", "id", "row", "column", "height",
    "width", "assemblyname", "assembly", "anchor", "autosize"
}
KNOWN_ADDIN_CHILDREN = set()

# Reconciled Business Rule schema (merged across workspace_parser and rule_parser)
KNOWN_RULE_ATTRS = {"name", "active", "id", "notes"}
KNOWN_RULE_CHILDREN = {"trigger", "triggers", "conditions", "condition", "then", "else", "action", "rule", "rules", "property"}

KNOWN_CONDITION_ATTRS = {"logicalexpression", "operator", "value", "type", "source", "property"}
KNOWN_CONDITION_CHILDREN = {"source", "operator", "value", "property", "condition", "conditions", "trigger", "triggers"}

KNOWN_ACTION_ATTRS = {"type", "scriptpath", "script"}
KNOWN_ACTION_CHILDREN = {"object", "operation", "value", "scriptpath", "property"}

# Navigation Set Schema
KNOWN_NAV_ATTRS = {"name", "id"}
KNOWN_NAV_CHILDREN = {"navitem", "item", "menuitem", "profile", "allowedprofile", "text", "label", "type", "workspace", "workspacename", "reportid", "acid", "navigationset"}

# Analytics Core Report Schema
# Full-Tree Vocabulary Sets (derived from scanning real OSVC export packages at all depths)
KNOWN_REPORT_ALL_TAGS = {
    "ac_id", "ac_public", "ac_type", "alias", "analytics_core", "applies_to", "aux",
    "branch_col_link_idx", "branch_tbl_idx", "branch_type", "calc_units", "cdate_offset",
    "charts", "co_version", "col_id", "col_rf", "cols", "cols_item", "comp_opts", "created",
    "data_type", "display_order", "excepts", "exit_code", "file_id", "filter_item", "filters",
    "fltr_expr", "fltr_id", "folder_id", "group_by_col_idx", "group_order", "group_type",
    "having_expr", "having_filters", "header_code", "image", "init_code", "interface_id",
    "items", "join_def_enum", "join_def_idx", "join_filters", "join_fltr_expr", "join_to_tbl_idx",
    "join_type", "label", "lang_id", "lbl_item", "max_len", "min_vuse", "n_id", "node_item",
    "nodes", "notes", "oper", "optl_id", "opts", "owner_acct_id", "params", "parent_node_idx",
    "perm_item", "perms", "php_version", "process_code", "profile_id", "revision", "row_limit",
    "rpt", "rpt_links", "run_vals", "schedules", "script_item", "scripts", "sort_direction",
    "sort_order", "starting_level", "style_id", "table_item", "tables", "tbl", "tbl_id",
    "time_zone", "trend_opts", "type", "updated", "val", "val1", "val1_attrs", "val1_col_refs",
    "val2", "val2_col_refs", "val2_original", "val_attrs", "val_col_refs", "version",
    "xml_data", "xml_report", "report", "reportid", "reportname", "column", "heading", "source"
}

KNOWN_REPORT_ALL_ATTRS = {
    "nil", "id", "name", "acid", "objecttype", "type"
}

KNOWN_CPM_ALL_TAGS = {
    "class", "classmapping", "classmappings", "classes", "mapping", "mappings",
    "objectprocedure", "suppressflagmapping", "content"
}

KNOWN_CPM_ALL_ATTRS = {
    "classname", "content", "displayname", "executeasynchronously", "id", "interface",
    "name", "operation", "operations", "phpversion", "procedure", "version"
}

KNOWN_OBJECT_ALL_TAGS = {
    "customobject", "field", "fields", "interfacelabel", "interfacelabels", "key",
    "keys", "notes", "package", "relationship"
}

KNOWN_OBJECT_ALL_ATTRS = {
    "allowsspmsuppression", "childcardinality", "childclassid", "childkeyid", "coaction",
    "colabel", "datatype", "datatypename", "description", "designerdata", "hasdescription",
    "hasfileattachment", "haslabels", "hasnotes", "hassequence", "hasusertransactions", "id",
    "isagentvisible", "isanalyticsvisible", "isautoupdate", "iscoreadonly", "islist",
    "islogtransactionsenabled", "islookup", "ismainparent", "ismenu", "ismenuonlyclass",
    "isnullable", "issequence", "issubclass", "issystem", "issystemfield", "keytype",
    "label", "language", "maxlength", "name", "optlistid", "packageid", "packagename",
    "parentcardinality", "parentclassid", "pattern", "predefinedparenttbl", "relationshiptype",
    "serverdefaultvalue", "usage"
}

def get_global_known_tags():
    return (
        KNOWN_WORKSPACE_CHILDREN | KNOWN_TABSET_CHILDREN | KNOWN_TAB_CHILDREN |
        KNOWN_RULE_CHILDREN | KNOWN_CONDITION_CHILDREN | KNOWN_ACTION_CHILDREN |
        KNOWN_NAV_CHILDREN | KNOWN_REPORT_ALL_TAGS | KNOWN_CPM_ALL_TAGS | KNOWN_OBJECT_ALL_TAGS |
        {"property"}
    )

def get_global_known_attrs():
    return (
        KNOWN_WORKSPACE_ATTRS | KNOWN_TABSET_ATTRS | KNOWN_TAB_ATTRS |
        KNOWN_FIELD_ATTRS | KNOWN_RELATIONSHIP_ATTRS | KNOWN_BROWSER_ATTRS |
        KNOWN_ADDIN_ATTRS | KNOWN_RULE_ATTRS | KNOWN_CONDITION_ATTRS |
        KNOWN_ACTION_ATTRS | KNOWN_NAV_ATTRS | KNOWN_REPORT_ALL_ATTRS |
        KNOWN_CPM_ALL_ATTRS | KNOWN_OBJECT_ALL_ATTRS
    )

def is_known_tag(tag):
    if not tag:
        return False
    clean_tag = tag.split("}")[-1].lower()
    return clean_tag in get_global_known_tags()

def is_known_attr(attr):
    if not attr:
        return False
    clean_attr = attr.split("}")[-1].lower()
    return clean_attr in get_global_known_attrs()
