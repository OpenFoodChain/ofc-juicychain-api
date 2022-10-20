import pytest
import requests
import random
import string
import os
import json
from datetime import date, timedelta

pytest.url = 'http://' + os.environ.get('JUICYCHAIN_API_HOST') + ':' + os.environ.get('JUICYCHAIN_API_PORT') + '/' + os.environ.get('JUICYCHAIN_API_VERSION_PATH')
pytest.today = (date.today()).isoformat()
pytest.next_week = (date.today() + timedelta(days=7)).isoformat()
pytest.date_prod_start = (date.today()).isoformat()
pytest.date_best_before = (date.today() + timedelta(days=7)).isoformat()
pytest.delivery_date = (date.today() + timedelta(days=14)).isoformat()
pytest.country = 'Amsterdam ' + str(random.randint(1, 200))

#print(pytest.url)

def randomize(length):
	random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
	return random_string

def random_int(length):
	random_int = str(random.randint(1, length))
	return random_int

def test_organization_get():
	response = requests.get(pytest.url + 'organization')
	assert response.status_code == 200

def test_organization_detail_get():
	response = requests.get(pytest.url + 'organization-detail')
	assert response.status_code == 200

def test_location_get():
	response = requests.get(pytest.url + 'location')
	assert response.status_code == 200

def test_certificate_get():
	response = requests.get(pytest.url + 'certificate')
	assert response.status_code == 200

def test_certificate_rule_get():
	response = requests.get(pytest.url + 'certificate-rule')
	assert response.status_code == 200

def test_batch_list_get():
	response = requests.get(pytest.url + 'batch')
	assert response.status_code == 200

def test_pool_wallet_get():
	response = requests.get(pytest.url + 'pool-wallet')
	assert response.status_code == 200

def test_organization_post():
	values = {"name": "Personal " + random_int(200), "pubkey": randomize(66), "raddress": randomize(34)}

	response = requests.post(pytest.url + 'organization/', data = values)
	assert response.status_code == 201

def test_organization_detail_post():
	response = requests.get(pytest.url + 'organization')
	data = json.loads(response.text)

	values = {
		"name": data[-1]['name'],
		"pool_wallet": [
			{
				"raddress": randomize(34),
				"pubkey": randomize(66),
				"name": "Pool Wallet Fix " + random_int(200)
			}
		],
		"location": [
			{
				"name": "Location Fix " + random_int(200),
				"txid_funding": randomize(20),
				"raddress": randomize(34),
				"pubkey": randomize(66)
			}
		],
		"certificate": [
			{
				"rule": [
					{
						"raddress": randomize(34),
						"pubkey": randomize(66),
						"name": "Certificate Rule Fix " + random_int(200),
						"condition": "active"
					}
				],
				"name": "Certificate Fix " + random_int(200),
				"raddress": randomize(34),
				"pubkey": randomize(66),
				"date_issue": pytest.today,
				"date_expiry": pytest.next_week,
				"issuer": "Certificate Issuer " + random_int(200),
				"identifier": "Certificate Identifier " + random_int(200),
				"txid_funding": randomize(20)
			}
		],
		"batch": [
			{
				"raddress": randomize(34),
				"pubkey": randomize(66),
				"identifier": "Identifier Fix " + random_int(200),
				"jds": random_int(200),
				"jde": random_int(200),
				"date_production_start": pytest.date_prod_start,
				"date_best_before": pytest.date_best_before,
				"delivery_date": pytest.delivery_date,
				"mass_balance": random_int(200),
				"origin_country": pytest.country
			}
		]
	}

	value = json.dumps(values)

	headers = {'Content-Type': 'application/json'}

	response = requests.post(pytest.url + 'organization-detail/', data = value, headers=headers)
	assert response.status_code == 201

def test_location_post():
	values = {
		"name": "Amsterdam" + random_int(50), 
		"pubkey": randomize(66), 
		"raddress": randomize(34), 
		"organization": "1", 
		"txid_funding": randomize(20)
	}

	response = requests.post(pytest.url + 'location/', data = values)
	assert response.status_code == 201

def test_certificate_post():
	values = {
		"name": "Personal Certificate " + random_int(200), 
		"date_issue": pytest.today, 
		"date_expiry": pytest.next_week, 
		"issuer": 'Personal Issuer ' + random_int(50), 
		"identifier": 'Personal Identifier ' + random_int(50), 
		"pubkey": randomize(66),
		"raddress": randomize(34),
		"txid_funding": randomize(20),
		"organization": 1
	}

	response = requests.post(pytest.url + 'certificate/', data=values)
	assert response.status_code == 201

def test_certificate_rule_post():
	condition = 'active'
	values = {"name": "Certificate Rule Personal" + random_int(200), "condition": condition, "pubkey": randomize(66), "raddress": randomize(34)}
	
	response = requests.post(pytest.url + 'certificate-rule/', data=values)
	assert response.status_code == 201

def test_batch_post():
	values = {
		"identifier": "Personal Identifier" + random_int(200),
		"jds": random_int(200),
		"jde": random_int(200),
		"date_production_start": pytest.date_prod_start,
		"date_best_before": pytest.date_best_before,
		"delivery_date": pytest.delivery_date,
		"origin_country": pytest.country,
		"mass_balance": random_int(200),
		"pubkey": randomize(66),
		"raddress": randomize(34),
		"organization": 1
	}

	response = requests.post(pytest.url + 'batch/', data=values)
	assert response.status_code == 201

def test_pool_wallet_post():
	values = {
		"name": "Personal Pool Wallet " + random_int(200),
		"pubkey": randomize(66),
		"raddress": randomize(34),
		"organization": 1
	}

	response = requests.post(pytest.url + 'pool-wallet/', data=values)
	assert response.status_code == 201

