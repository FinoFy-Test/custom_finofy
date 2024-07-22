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
def lead_routing():
	campaign_name = frappe.form_dict.get('campaign_name')
	email = frappe.form_dict.get('email_id')
	mobile = frappe.form_dict.get('primary_mobile')
	check_in_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	lead_rule = frappe.db.sql(""" select name, lead_length, lead_counter from `tabLead Rules` where new_campaign = '{0}';""".format(campaign_name), as_dict= True)
	csm_list = frappe.db.sql(""" select user.sales_person, user.user_id from `tabUser Rule`user where user.parent = '{0}';""".format(lead_rule[0].name), as_dict= True)
	
	counter = int(lead_rule[0].lead_counter)
	lenght = int(lead_rule[0].lead_length)
	# return lead_rule[0].lead_length
	# for d in lenght:
	trim_mob = mobile.replace(" ", "").lstrip('+')
	lead_mob = frappe.db.exists("Lead", {"primary_mobile": trim_mob})
	lead_email = frappe.db.exists("Lead", {"email_id": email})
	old_count = frappe.db.sql("select check_in_count from `tabLead` where name = '{0}' or name = '{1}'".format(lead_email, trim_mob),as_dict = True)
	if frappe.form_dict.get('language') == "English":
		language = "en"
	else:
		language = frappe.form_dict.get('language')

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
		if counter < lenght:
			sales_person = csm_list[counter].sales_person
			lead_owner = csm_list[counter].user_id
			frappe.db.set_value('Lead Rules', lead_rule[0].name, {
				'lead_counter': counter + 1
				})
			frappe.db.commit()
		else:
			sales_person = csm_list[0].sales_person
			lead_owner = csm_list[0].user_id
			frappe.db.set_value('Lead Rules', lead_rule[0].name, {
				'lead_counter': 1
				})
			frappe.db.commit()

		LeadInsert = frappe.get_doc({
			"doctype": "Lead",
			"lead_name": frappe.form_dict.get('lead_name'),
			"last_name": frappe.form_dict.get('last_name') or "",
			"email_id": frappe.form_dict.get('email_id'),
			"primary_mobile": trim_mob,
			"grade": frappe.form_dict.get('grade'),
			"status": "Lead",
			"campaign_name": frappe.form_dict.get('campaign_name'),
			"country": frappe.form_dict.get('country') or "India",
			"assign_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
			"temperature": "Very Hot",
			"language": language,
			"lead_status": "Not Contacted",
			"ip_address": frappe.form_dict.get('ip_address') or "",
			"sales_person": sales_person,
			"lead_owner": lead_owner,
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


@frappe.whitelist(allow_guest=True)
def dispose_lead_routing(lead, campaign, assign_count):
	lead_rule = frappe.db.sql(""" select name, lead_length, lead_counter from `tabLead Rules` where new_campaign = '{0}';""".format(campaign), as_dict= True)
	count =  int(assign_count) + 1
	csm_list = frappe.db.sql(""" select user.sales_person, user.user_id from `tabUser Rule`user where user.parent = '{0}';""".format(lead_rule[0].name), as_dict= True)

	counter = int(lead_rule[0].lead_counter)
	lenght = int(lead_rule[0].lead_length)

	if counter < lenght:
		sales_person = csm_list[counter].sales_person
		lead_owner = csm_list[counter].user_id
		frappe.db.set_value('Lead Rules', lead_rule[0].name, {
			'lead_counter': counter + 1
			})
		frappe.db.commit()
	else:
		sales_person = csm_list[0].sales_person
		lead_owner = csm_list[0].user_id
		frappe.db.set_value('Lead Rules', lead_rule[0].name, {
			'lead_counter': 1
			})
		frappe.db.commit()

	frappe.db.set_value('Lead', lead, {
		'lead_owner': lead_owner,
		'sales_person': sales_person,
		'assign_count': count
		})
	frappe.db.commit()
	return "Lead Assigned"



@frappe.whitelist(allow_guest=True)
def qssd():
	frappe.db.delete("Quality Support System")
	return 'uooo'