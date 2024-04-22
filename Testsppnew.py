from flask import Flask, request, jsonify
import psycopg2
import json

app = Flask(__name__)

# Вместо token вписать токен доступа к Bitrix24
access_token = "access_token"

# Вместо domain вписать домен вашего Bitrix24
domain = "domain"

# Вместо id вписать идентификатор пользователя, создавшего вебхук
id = "id"

# Вместо s_code вписать секретный код, полученный при создании вебхук
s_code = "s_code"

# Вписать вместо Webhook_URL URL вебхука
webhook_url = "webhook_url"

# Установить конечную точку API
url = f"https://{domain}/rest/{id}/{s_code}/crm.contact.list.json"
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
}

# Установить параметры запроса API
params = {
    "filter": {"ID": ">0"},  # Запрос контактов
    "select": ["ID", "NAME"],  # Вывести ID и NAME
}

# Делаем запрос через request.get для получения контактных данных
response = request.get(url, headers=headers, params=params)

if response.status_code == 200:
    # Извлекаем контактные данные
    contacts = response.json()["result"]

    # Проверяем каждый контакт и отправляем в Webhook
    for contact in contacts:
        data = {"ID": contact["ID"], "Name": contact["NAME"]}
        response = request.post(webhook_url, json=data)
        print(f"Sent contact {contact['ID']} to Webhook")
else:
    print("Error retrieving contact data")

# Заходим в базу данных
conn = psycopg2.connect(
    dbname="names",
    user="postgres",
    password="password1",
    host="localhost",
    port="5432",
)


def bitrix24_webhook(data):
    contact_name = data["fields"]["NAME"]
    contact_id = data["fields"]["ID"]

    # Проверяем имя коонтакта в name_man
    cursor = conn.cursor()
    query = f"SELECT gender FROM name_man WHERE name = '{contact_name}';"
    cursor.execute(query)
    result = cursor.fetchone()
    if result:
        gender = result[0]
        update_contact_gender(contact_id, gender)

    # Проверяем имя коонтакта в names_woman
    cursor = conn.cursor()
    query = f"SELECT gender FROM names_woman WHERE name = '{contact_name}';"
    cursor.execute(query)
    result = cursor.fetchone()
    if result:
        gender = result[0]
        update_contact_gender(contact_id, gender)

    conn.commit()


# Добавляем значение пола в контакты Bitrix24
def update_contact_gender(contact_id, gender):
    url = "https://b24-hl15pk.bitrix24.ru/rest/1/rlmk7wo6i5olqomb/profile.json"
    data = {"fields": {"ID": contact_id, "GENDER": gender}}
    response = request.post(url, json=data)


# Фызываем функцию
bitrix24_webhook(data)

if __name__ == "__main__":
    app.run(debug=True)
