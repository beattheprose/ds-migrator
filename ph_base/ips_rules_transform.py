import os
import sys
import datetime
import time
import requests
import urllib3
import traceback
from functions.ListAllPolicy import ListAllPolicy
from functions.GetPolicy import GetPolicy
from functions.IPSConfig import IPSGet, IPSDescribe, IPSCustom, IPSReplace
from functions.IPSapptypeConfig import (
    IPSappGet,
    IPSappDescribe,
    IPSappCustom,
    IPSappReplace,
)
from functions.PortListGetT1CreateT2 import PortListGet, PortListCreate

OLD_API_KEY = os.environ.get("OLD_API_KEY")
OLD_HOST = os.environ.get("OLD_HOST")
NEW_API_KEY = os.environ.get("NEW_API_KEY")
NEW_HOST = os.environ.get("NEW_HOST")
cert = False

old_policy_name_enum, old_policy_id_list = ListAllPolicy(OLD_HOST, OLD_API_KEY)

antimalwareconfig, og_allofpolicy = GetPolicy(old_policy_id_list, OLD_HOST, OLD_API_KEY)

######## IPS STUFF
og_ipsruleid = IPSGet(og_allofpolicy)
og_ipsappid = IPSappGet(og_allofpolicy)

t1portlistall, t1portlistname, t1portlistid = PortListGet(OLD_HOST, OLD_API_KEY)
t2portlistid = PortListCreate(t1portlistall, t1portlistname, NEW_HOST, NEW_API_KEY)

allipsapp, allipsappidnew1, allipsappidold, allipscustomapp = IPSappDescribe(
    og_ipsappid,
    t1portlistid,
    t2portlistid,
    OLD_HOST,
    OLD_API_KEY,
    NEW_HOST,
    NEW_API_KEY,
)

allipsappidnew2 = IPSappCustom(allipsapp, allipscustomapp, NEW_HOST, NEW_API_KEY)

allipsrule, allipsruleidnew1, allipsruleidold, allipscustomrule = IPSDescribe(
    og_ipsruleid,
    og_ipsappid,
    allipsappidnew1,
    allipsappidnew2,
    allipsappidold,
    allipscustomapp,
    OLD_HOST,
    OLD_API_KEY,
    NEW_HOST,
    NEW_API_KEY,
)

allipsruleidnew2 = IPSCustom(allipsrule, allipscustomrule, NEW_HOST, NEW_API_KEY)


def ips_rules_transform(allofpolicy):
    # 1. Creates a rosetta of rule ids
    # 2. Transfers over custom rules
    # 3. outputs allofpolicy with the replacements
    aop_replace_ips_rules = IPSReplace(
        allofpolicy,
        allipsruleidnew1,
        allipsruleidnew2,
        og_ipsruleid,
        allipsruleidold,
        allipscustomrule,
    )
    aop_replace_ips_apps = IPSappReplace(
        aop_replace_ips_rules,
        allipsappidnew1,
        allipsappidnew2,
        og_ipsappid,
        allipsappidold,
        allipscustomapp,
    )
    final = aop_replace_ips_apps
    return final
