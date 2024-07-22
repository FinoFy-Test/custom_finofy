from __future__ import unicode_literals
import frappe, json
# from frappe.utils import get_site_url, get_url_to_form, get_link_to_form
from werkzeug.wrappers import Response
from frappe.utils.response import build_response
from datetime import datetime, timedelta
import requests
import json
import time
import requests
import datetime
from urllib.parse import urlparse
from urllib.parse import parse_qs
from datetime import datetime, timedelta

@frappe.whitelist(allow_guest=True)
def lead_insertion():
    email = frappe.form_dict.get('email_id')
    mobile = frappe.form_dict.get('primary_mobile')
    trim_mob = mobile.replace(" ", "").lstrip('+')
    if frappe.form_dict.get('language') == "English":
        language = "en"
    else:
        language = frappe.form_dict.get('language')
        # return frappe.form_dict.get('language')
    
   
    check_in_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    lead_email = frappe.db.exists("Lead", {"email_id": email})
    lead_mob = frappe.db.exists("Lead", {"primary_mobile": trim_mob})
    old_count = frappe.db.sql("select check_in_count from `tabLead` where name = '{0}' or name = '{1}'".format(lead_email, lead_mob),as_dict = True)

    try:
        lead_from = frappe.form_dict.get('leadfrom')
        parsed_url = urlparse(lead_from)
        
        utm_content = parse_qs(parsed_url.query)['utm_content'][0]
        utm_source = parse_qs(parsed_url.query)['utm_source'][0]
        utm_medium = parse_qs(parsed_url.query)['utm_medium'][0]
        utm_campaign_date = parse_qs(parsed_url.query)['utm_campaign'][0]

    except:
        utm_content = ""
        utm_source = ""
        utm_medium = ""
        utm_campaign_date = ""

    if lead_mob:
        frappe.db.set_value('Lead', lead_mob, {
				'utm_source': utm_source,
				'utm_medium': utm_medium,
				'utm_campaign_date': utm_campaign_date,
				'assign_time': check_in_time,
				'utm_content': utm_content,
				'check_in_time': check_in_time,
				'check_in_count': old_count[0].check_in_count + 1,
                "lead_status": "Not Contacted"
			})
        frappe.db.commit()
        return "Check In Updated"

    else:
        LeadInsert = frappe.get_doc({
            "doctype": "Lead",
            "lead_name": frappe.form_dict.get('lead_name'),
            "last_name": frappe.form_dict.get('last_name') or "",
            "email_id": frappe.form_dict.get('email_id') or "",
            "primary_mobile": trim_mob or "",
            "grade": frappe.form_dict.get('grade'),
            "status": "Lead",
            "campaign_name": frappe.form_dict.get('campaign_name') or "",
            "country": frappe.form_dict.get('country') or "India",
            "assign_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "temperature": "Very Hot",
            "language": language,
            "lead_status": "Not Contacted",
            "ip_address": frappe.form_dict.get('ip_address') or "",
            "sales_person": frappe.form_dict.get('sales_person') or "",
            "lead_owner": frappe.form_dict.get('lead_owner') or "",
            "sms_otp_verified": 0,
            "utm_source": utm_source,
            "utm_medium": utm_medium,
            "utm_campaign_date": utm_campaign_date,
            "utm_content": utm_content,
            "lead_property": frappe.form_dict.get('demat_account') or "",
            "investment_type": frappe.form_dict.get('investment_type') or ""
        }).insert(ignore_permissions=True)
        LeadInsert.save()
        return "Success"