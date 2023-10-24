import json


values = """
{
	"data": {
		"attributes": {
			"registerUser": false
		},
		"relationships": {
			"bookingRequests": {
				"data": [
					{
						"attributes": {
							"count": "1",
							"note": "",
							"price": "0",
							"requestType": "appointment",
							"source": "Booking Page 3.11.2",
							"start": "2023-02-13T08:40:00+03:00"
						},
						"relationships": {
							"business": {
								"data": {
									"id": "09250556-2450-437f-aede-82e78712f114",
									"type": "business"
								}
							},
							"client": {
								"data": {
									"attributes": {
										"email": "stalklifeday@gmail.com",
										"marketingNotificationsAcceptedAt": null,
										"name": "Antonio",
										"phone": "+79652638442",
										"privacyPolicyAcceptedAt": "2023-01-20T14:22:33+01:00"
									},
									"type": "client"
								}
							},
							"service": {
								"data": {
									"id": "8e13743d-076d-4aa0-b0c2-c8d3c2b64de2",
									"type": "service"
								}
							}
						},
						"type": "bookingRequest"
					}
				]
			},
			"user": {
				"data": {
					"attributes": {
						"confirmationLink": "",
						"email": "stalklifeday@gmail.com",
						"firstName": "Antonio",
						"language": "ru",
						"lastName": "",
						"marketingNotificationsAcceptedAt": null,
						"password": "",
						"phone": "+79652638442",
						"privacyPolicyAcceptedAt": "2023-01-20T14:22:33+01:00",
						"registrationSource": "",
						"timezone": ""
					},
					"type": "user"
				}
			}
		},
		"type": "bookingFormRequest"
	}
}
"""
def manifest(time_start, utc_time_now, email, name, phone, service_id):
	# Гурзим манифест, меняем старт дату
	total = json.loads(values)
	data = total["data"]["relationships"]["bookingRequests"]["data"]
	attributes = data[0]
	attributes["attributes"]['start']=time_start
	# меняем клиента
	client = data[0]
	client["relationships"]["client"]["data"]['attributes']['email']=email
	client["relationships"]["client"]["data"]['attributes']['name']=name
	client["relationships"]["client"]["data"]['attributes']['phone']=phone
	client["relationships"]["client"]["data"]['attributes']['privacyPolicyAcceptedAt']=utc_time_now
	# меняем сервис
	service = data[0]
	service["relationships"]["service"]['data']['id']=service_id
	# меняем юзер
	user = total["data"]["relationships"]["user"]["data"]['attributes']
	user['email']=email
	user["firstName"]=name
	user["phone"]=phone
	user["privacyPolicyAcceptedAt"]=utc_time_now
	print("Манифест создан")
	# print(total)
	result = json.dumps(total)
	return result

# total = manifest('старт', "настоящие время", "эмайл", "имя мое", "телефон", "СЕРВИС НОМЕР 1")
# print(total)