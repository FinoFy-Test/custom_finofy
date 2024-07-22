# -*- coding: utf-8 -*-
# Copyright (c) 2020, GoElite and contributors
# For license information, please see license.txt
# Created By- Ashish Bankar

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
import binascii
from Crypto import Random
from Crypto.Cipher import AES
import base64
from binhex import binhex, hexbin
import string
import random
from frappe.utils.password import get_decrypted_password

#Lead Disposition API
@frappe.whitelist()
def lead_dispose(doctype, name, assign_count, sales_person, lead_owner, lead_status, login_user):
	person = ""
	owner = ""
	# store_cust = frappe.db.get_list('Customer',{'lead_name': name},'name')
	# if lead_status== 'Converted' or store_cust:
	# 	frappe.throw("This Lead can't be Dispose because Converted in Customer")
	# 	return "Not Dispose"

	# else:
	frappe.db.set_value('Lead', name, {
				'sales_person': person,
				'lead_owner': owner,
				'assign_count': assign_count,
				# 'assign_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
				'contact_date': "",
				'ends_on': "",
				'disposed_by': login_user
			})

	store_name = frappe.db.get_list('Opportunity',{'party_name': name},'name')
	for d in store_name:

		frappe.db.set_value('Opportunity',d.name, {
			'sales_person': ""
		})

		if not frappe.db.get_value('Opportunity', d.name, 'price_list'):
			frappe.db.set_value('Opportunity',d.name, {
			'price_list': "Monthly (INR)"
		})

	return "success"

#Do Not Disturb
@frappe.whitelist()
def mark_dnd_lead(doctype, name):
	person = ""
	owner = ""
	frappe.db.set_value('Lead', name, {
				'sales_person': person,
				'lead_owner': owner,
				'dnd': 1,
				# 'assign_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
				'contact_date': "",
				'ends_on': ""
			})
	return "success"

#Lead Transfer
@frappe.whitelist()
def update_customer_lead(doctype, name, sales_person, assign_count):
	print("doctype", doctype)
	store_opp = frappe.db.get_list('Opportunity',{'party_name': name},'name')
	if store_opp:
		for g in store_opp:
			frappe.db.set_value('Opportunity',g.name, {
			'sales_person': sales_person
		})

		store_cust = frappe.db.get_list('Customer',{'lead_name': name},'name')
		if store_cust:
			for d in store_cust:
				frappe.db.set_value('Customer',d.name, {
					'sales_person': sales_person,
					'assign_count': assign_count,
					'assign_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
				})

				store_py_entry = frappe.db.get_list('Payment Entry',{'party': d.name},'name')
				if store_py_entry:
					for e in store_py_entry: 
						frappe.db.set_value('Payment Entry',e.name, {
							'sales_person': sales_person
				
						})
				
				store_sales_inv = frappe.db.get_list('Sales Invoice',{'customer': d.name},'name')
				if store_sales_inv:
					for f in store_sales_inv:
						frappe.db.set_value('Sales Invoice',e.name, {
							'sales_person': sales_person
				
						})

#Delete Auto customer Creation
# @frappe.whitelist()
# def delete_auto_customer_creation(doctype, name):
# 	frappe.db.delete(doctype, {
#     	'name': name
# 	})

# 	return "Delete Success"


@frappe.whitelist(allow_guest=True)
def fee_request_consent(name, consent):
	store = frappe.db.exists("Fee Request", name, 'consent')
	if name and consent and store:
		opp_no = frappe.db.get_value("Fee Request", name, 'opportunity_number')
		cust_name = frappe.db.get_value("Opportunity", opp_no, 'customer_name')
		frappe.db.set_value('Fee Request', name, {
							'consent': consent,
							'approved_by': cust_name,
							'approved_on': datetime.now(),
							'ip' : frappe.local.request_ip
						})
		frappe.db.commit()
		# return "Thank You for your Consent"
		return frappe.redirect_to_message('Thank You',"Success Message")
	if not store:
		return frappe.redirect_to_message('Thank You',"Success Message")
		# "Your Consent already Store"
		

@frappe.whitelist(allow_guest=True)
def risk_profile_consent(name, consent):
	store = frappe.db.exists("Risk Profile", name, 'consent')
	if name and consent == "Yes, I Agree" and store:
		frappe.db.set_value('Risk Profile', name, {
							'consent': consent,
							'consent_time': datetime.now(),
							'ip_address' : frappe.local.request_ip,
							'workflow_state': "Consented"
						})
		frappe.db.commit()
		return frappe.redirect_to_message('Thank You',"Success Message")

	if name and consent == "Need Modification!" and store:
		frappe.db.set_value('Risk Profile', name, {
							'consent': consent,
							'consent_time': datetime.now(),
							'ip_address' : frappe.local.request_ip,
							'workflow_state': "No Consent"
						})
		frappe.db.commit()
		return frappe.redirect_to_message('Thank You',"Success Message")

	if not store:
		return frappe.redirect_to_message('Thank You',"Your Consent already Store")



@frappe.whitelist(allow_guest=True)
def outsider_employee_login(emp, time, log):
	request_url = 'https://geolocation-db.com/jsonp/' + frappe.local.request_ip
	response = requests.get(request_url)
	result = response.content.decode()
	result = result.split("(")[1].strip(")")
	result  = json.loads(result)
	
	checkin = frappe.get_doc({
		"doctype": "Employee Checkin",
		"employee": emp,
		"time": datetime.now(),
		'log_type': log,
		'ip_address': frappe.local.request_ip,
		'location': result['city']
	}).insert()
	frappe.db.commit()
	
	return 200

@frappe.whitelist(allow_guest=True)
def contact_email_mapping(name, email):
	si_list = frappe.db.get_list('Sales Invoice',
		filters={
			'customer': name,
			'contact_email': '' 
		},
		fields=['name']
	)
	for d in si_list:
		# raise frappe.PermissionError(name)
		# doc = frappe.db.set_value('sales Invoice', d.name, {
		# 		'contact_email': email})
		# doc.insert()
		frappe.db.sql("UPDATE `tabSales Invoice` SET contact_email = '{0}' WHERE customer = '{1}';".format(email, name))
		frappe.db.commit()
	return 200

# @frappe.whitelist(allow_guest=True)
# def sms_delivery_status():
# 	qStatus, qMobile, qMsgRef, qNotes = frappe.form_dict.get('qStatus'), 
# 		frappe.form_dict.get('qMobile'), frappe.form_dict.get('qMsgRefqS'),frappe.form_dict.get('qNotes'),

def decode_pipes(req_type, data):
        if req_type == "COLLECTION":
            data_list = data.split("|")
            return data_list[1], data_list[3], data_list[4], data_list[12]
        elif req_type == "CALLBACK":
            data_list = data.split("|")
            return data_list[0], data_list[1], data_list[2], data_list[4], data_list[8]
        elif req_type == "COLLECTION_POLLING":
            data_list = data.split("|")
            return data_list[0], data_list[1], data_list[2], data_list[4]

@frappe.whitelist(allow_guest=True)
def initiate_payment():
	mcc = "8999"
	# merchant_id = "HDFC000005853569"
	# merchant_key = "d87822929aa83119f76cf6b762b87b0e"
	merchant_id = "HDFC000016346138"
	merchant_key = "a745817448954c1dae0e38ad0747a27a"
	vpa = "capitalvia@hdfcbank"
	CHECK_VPA_URL = "https://upi.hdfcbank.com/upi/checkMeVirtualAddress"
	COLLECT_TRAN_URL = "https://upi.hdfcbank.com/upi/meTransCollectSvc"
	CHECK_COLLECT_REQ = "https://upi.hdfcbank.com/upi/transactionStatusQuery"


	vpa_address, amount, upi_link, fee_request = frappe.form_dict.get(
	'vpa_address'), frappe.form_dict.get('amount'), frappe.form_dict.get('upiLink'), frappe.form_dict.get('fee_request')

# payobj = UPIPayment()
# data = payobj.initiate_payment(
#     vpa_address, amount, upi_link, fee_request, fcm_token)
	if upi_link:
#return generate_link()
		return 1
	else:
		"""
			PGMerchantId|OrderNo|PayerVA|Amount|Remarks|expValue|MCC Code|1|2|3|4|5|6|7|8|NA|NA = 17 Nos.
			Request is valid till 5 minutes
		"""
		transaction_no = frappe.generate_hash("UPI Payment", 10)
		remark = "Payment of {} from {}".format(amount, frappe.session.user)
		req = "{}|{}|{}|{}|{}|{}||||||||||NA|NA".format(merchant_id, transaction_no, vpa_address, amount, "CapitalVia Payment", 5)
		payload = {'requestMsg': _encrypt(req, merchant_key), 'pgMerchantId': merchant_id}
		headers = {
			'content-type': "application/json",
			}
		r = requests.request("POST", COLLECT_TRAN_URL, data=json.dumps(payload), headers=headers)
		frappe.log_error(r.content)
		rd = _decrypt(r.content, merchant_key)
		frappe.log_error(_decrypt(r.content, merchant_key))
		request_started = int(time.time())
		upi_ref_id, status, tran_status, field_6 = decode_pipes("COLLECTION", _decrypt(r.content, merchant_key))
		
		fee_request_amount = frappe.db.get_value(
			"Fee Request", fee_request, "amount")
		if status == "SUCCESS":
			paydoc = frappe.new_doc("UPI Payment")
			paydoc.transaction_number = transaction_no
			paydoc.vpa_address = vpa_address
			paydoc.amount = fee_request_amount
			paydoc.remark = remark
			paydoc.upi_transaction_reference_id = upi_ref_id
			paydoc.collection_request_status = status
			paydoc.transaction_status = tran_status
			paydoc.fee_request = fee_request
			# paydoc.fcm_token = fcm_token if fcm_token else ""
			paydoc.insert()
			paydoc.submit()
			frappe.db.commit()
			return transaction_no, "SUCCESS"
		else:
			return transaction_no, "FAILED"
		# """
		# PGMerchantId|Merchant Ref No|VPA|Status|1|2|3|4|5|6|7|8|NA|NA = 14 Nos
		# """
		# transaction_no = frappe.generate_hash("UPI Payment", 10)
		# #return transaction_no
		# req = "{}|{}|{}|T|||||||||NA|NA".format(
		# merchant_id, transaction_no, vpa_address)
		# #return req
		
		# # frappe.log_error(req)
		# a=_encrypt(req, merchant_key)

		# payload = {'requestMsg': a, 'pgMerchantId': merchant_id}
		# headers = {
		# 'content-type': "application/json",
		# }
		# r = requests.request(
		# "POST", CHECK_VPA_URL, data=json.dumps(payload), headers=headers)


		# rd = _decrypt(r.content, merchant_key)
		# return rd


def _encrypt(data, passphrase):
#raise frappe.PermissionError(data)
	try:
		key = binascii.unhexlify(passphrase)

		def pad(s): return s+chr(16-len(s) % 16)*(16-len(s) % 16)
		iv = Random.get_random_bytes(16)
		cipher = AES.new(key, AES.MODE_ECB)

		# cipher = AES.new(key, AES.MODE_CBC)
		# obj = AES.new('This is a key123'.encode("utf8"), AES.MODE_CBC, 'This is an IV456'.encode("utf8"))

		encrypted_64 = base64.b16encode(
		cipher.encrypt(pad(data).encode("utf8"))).decode('ascii')
		clean = encrypted_64

	except Exception as e:
		print("Cannot encrypt datas...")
		print(e)

	# raise frappe.PermissionError(str(clean))
	return str(clean)

def _decrypt(data, passphrase):
	try:
		def unpad(s): return s[:-s[-1]]
		key = binascii.unhexlify(passphrase)
		encrypted_data = base64.b16decode(data)
		cipher = AES.new(key, AES.MODE_ECB)
		decrypted = cipher.decrypt(encrypted_data)
		clean = unpad(decrypted).decode('ascii').rstrip()
		raise frappe.PermissionError(clean)
	except Exception as e:
		print("Cannot decrypt datas...")
		print(e)
	return clean
