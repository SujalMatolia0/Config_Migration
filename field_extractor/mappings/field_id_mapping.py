"""
Field ID Mapping for OSVC Field Extractor Studio.

Maps workspace control field IDs (e.g. RefNo, CId, SeverityId, OrgId, ProdId)
to their corresponding OSVC REST API Metadata Catalog field keys
(e.g. referenceNumber, primaryContact.id, severity, organization.id, product.id).
"""

_INCIDENT_MAP = {
    "refno": "referencenumber",
    "cid": "primarycontact.id",
    "orgid": "organization.id",
    "prodid": "product.id",
    "catid": "category.id",
    "dispid": "disposition.id",
    "severityid": "severity",
    "queueid": "queue",
    "assigned": "assignedto",
    "status.id": "statuswithtype",
    "iid": "id",
    "subject": "subject",
    "created": "createdtime",
    "updated": "updatedtime",
    "closed": "closedtime",
    "initialsoln": "initialsolutiontime",
    "lastresp": "lastresponsetime",
    "reldue": "initialresponseduetime",
    "createdby": "createdbyaccount.id",
    "mailboxid": "mailbox.id",
    "chanid": "channel",
    "chatqueueid": "chatqueue",
    "interfaceid": "interface.id",
    "langid": "language",
    "assetid": "asset.id",
    "source": "source.id",
    "slaiid": "slainstance",
    "slarespdelta": "responseinterval",
    "slarslndelta": "resolutioninterval",
    "eicust": "smartsensecustomer",
    "eistaff": "smartsensestaff",
    "lastsurveyscore": "lastsurveyscore",
}

_CONTACT_MAP = {
    "cid": "id",
    "name.first": "name",
    "name.last": "name",
    "email": "emails",
    "phoffice": "phones",
    "orgid": "organization.id",
    "addr": "address",
    "login": "login",
    "title": "title",
    "disabled": "disabled",
    "ctypeid": "contacttype",
    "acquired": "createdtime",
    "created": "createdtime",
    "updated": "updatedtime",
    "source": "source.id",
    "salesacctid": "salessettings",
    "supersededbycid": "supersededby.id",
    "state": "address",
    "maoptin": "marketingsettings",
    "surveyoptin": "marketingsettings",
    "contactlists": "channelusernames",
    "smuser": "login",
}

_ORG_MAP = {
    "orgid": "id",
    "name": "name",
    "industryid": "industry",
    "oaddr": "addresses",
    "login": "login",
    "acquired": "createdtime",
    "created": "createdtime",
    "updated": "updatedtime",
    "salesacctid": "salessettings",
    "source": "source.id",
    "supersededbyorgid": "parent.id",
}

FIELD_ID_MAP = {
    "incident": _INCIDENT_MAP,
    "incidents": _INCIDENT_MAP,
    "contact": _CONTACT_MAP,
    "contacts": _CONTACT_MAP,
    "org": _ORG_MAP,
    "orgs": _ORG_MAP,
    "organization": _ORG_MAP,
    "organizations": _ORG_MAP,
    "organisation": _ORG_MAP,
    "organisations": _ORG_MAP,
}


def get_mapped_rest_key(object_name: str, field_id: str) -> str:
    """
    Translates a workspace field ID to its corresponding REST API metadata field key.
    If no mapping exists, returns the original field_id.
    """
    if not object_name or not field_id:
        return field_id or ""

    obj_key = str(object_name).strip().lower()
    fid_key = str(field_id).strip().lower()

    obj_mapping = FIELD_ID_MAP.get(obj_key, {})
    return obj_mapping.get(fid_key, field_id)
