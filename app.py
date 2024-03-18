from datetime import datetime
from docx import Document
from flask import Flask, render_template, request, session, json, redirect, url_for
import mysql.connector
from flask_mail import Mail, Message
from flask_bcrypt import Bcrypt
from matplotlib.dates import DateFormatter
from flask import send_from_directory
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.lib import fonts
from io import BytesIO
from docx import Document
from flask import Flask, render_template, make_response
import mysql.connector
from mysql.connector import Error
import openpyxl

from fpdf import FPDF

from flask_session import Session
import re
from SendCheck import SendCheck
from twilio.rest import Client
import random
import os
import json
import matplotlib.pyplot as plt

app = Flask(__name__)
app.secret_key = 'your_secret_key'
bcrypt = Bcrypt(app)

app.config['SECRET_KEY'] = 'anuta_lazyta'  # Замените на ваш секретный ключ
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)


def export_to_excel():
    try:
        # Подключение к базе данных MySQL
        connection = create_connection()

        # Создание объекта курсора
        cursor = connection.cursor()

        # Выполнение SQL-запроса для извлечения данных
        query = "SELECT * FROM insure_car_green_card"
        cursor.execute(query)

        # Получение всех данных из результата запроса
        rows = cursor.fetchall()

        # Путь к папке на диске D
        save_path = 'D:/'

        # Создание нового документа Excel
        workbook = openpyxl.Workbook()
        sheet = workbook.active

        # Запись данных в документ Excel
        for row_index, row in enumerate(rows, start=1):
            for column_index, value in enumerate(row, start=1):
                sheet.cell(row=row_index, column=column_index, value=str(value))

        # Полный путь к файлу
        file_path = os.path.join(save_path, 'data.xlsx')

        # Сохранение файла Excel на диске D
        workbook.save(file_path)

        # Закрытие соединения с базой данных
        cursor.close()
        connection.close()

        # Возвращение пути к файлу
        return file_path

    except Error as e:
        print("Ошибка при работе с MySQL", e)


# Функция для подключения к базе данных
def create_connection():
    mydb = None
    mydb = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        port='3306',
        database='python'
    )
    print('Соединение с базой данных успешно установлено')
    return mydb


def check_password(password):
    if len(password) < 9:
        message = "Длина пароля должна быть не менее 8 символов"
        return render_template('sign_in.html', message=message)

    if re.match("^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d]+$", password):
        print("Пароль содержит английские буквы и цифры.")
    else:
        message = "Используйте символы a-Z и цифры для ввода пароля"
        return render_template('sign_in.html', message=message)


def sending_sms_phone(text='Hello', receiver='+375297720598'):
    try:
        account_sid = 'ACc26b30394353ab0226308952f2cb47d0'
        auth_token = '68cc20b9934827f02622118960b0dbd8'
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=text,
            from_='+12055286667',
            to=receiver
        )
        print(receiver)
        return 'OK'
    except:
        return 'not OK'


def generate_code():
    random_number = random.randint(100000, 999999)
    return random_number


def check_insure(phone_number, enter_code):
    random_number = random.randint(1000, 9999)
    print(random_number)
    sending_sms_phone(text=str(random_number), receiver=phone_number)
    if enter_code == random_number:
        return 1
    else:
        return 0


@app.route("/index")
@app.route("/")
def index():
    return render_template('index.html')


@app.route("/profile", methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        session['email'] = None
        # Другие действия, связанные с выходом из профиля
        return redirect(url_for('sign_in'))
    email = session.get('email')
    mydb = create_connection()

    cursor = mydb.cursor()
    cursor.execute("SELECT name, email FROM user WHERE email = %s", (email,))
    user = cursor.fetchone()
    # Получаем данные пользователя из результата запроса
    cursor.close()

    cursor = mydb.cursor()
    cursor.execute("SELECT vehicle_make, vehicle_model, vehicle_year, countries_str, start_date, end_date "
                   "FROM insure_car_green_card WHERE email = %s", (email,))
    green_card = cursor.fetchone()
    # Получаем данные пользователя из результата запроса
    cursor.close()

    cursor = mydb.cursor()
    cursor.execute(
        "SELECT start_date, end_date, car_brand, car_model, car_year, car_registration_number, insurance_cost "
        "FROM insure_car_osgo_vn WHERE (email = %s and insurance_cost>0)  LIMIT 1", (email,))
    osgo_vn = cursor.fetchone()
    # Получаем данные пользователя из результата запроса
    cursor.close()

    cursor = mydb.cursor()
    cursor.execute("SELECT start_date, end_date, full_name, passport_data, insurance_cost "
                   "FROM insure_health_personal WHERE (email = %s and insurance_cost>0)  LIMIT 1", (email,))
    health_personal = cursor.fetchone()
    # Получаем данные пользователя из результата запроса
    cursor.close()
    if user:
        name = user[0]
        email = user[1]

        vehicle_make = green_card[0] if osgo_vn else None
        vehicle_model = green_card[1] if osgo_vn else None
        vehicle_year = green_card[2] if osgo_vn else None
        countries_str = green_card[3] if osgo_vn else None
        start_date_green_card = green_card[4] if osgo_vn else None
        end_date_green_card = green_card[5] if osgo_vn else None

        start_date_osgo = osgo_vn[0] if osgo_vn else None
        end_date_osgo = osgo_vn[1] if osgo_vn else None
        car_brand = osgo_vn[2] if osgo_vn else None
        car_model = osgo_vn[3] if osgo_vn else None
        car_year = osgo_vn[4] if osgo_vn else None
        car_registration_number = osgo_vn[5] if osgo_vn else None
        insurance_cost = osgo_vn[6] if osgo_vn else None

        start_date_personal = health_personal[0] if health_personal else None
        end_date_personal = health_personal[1] if health_personal else None
        full_name = health_personal[2] if health_personal else None
        passport_data = health_personal[3] if health_personal else None
        insurance_cost_personal = health_personal[4] if health_personal else None

        return render_template('profile.html', name=name, email=email,
                               start_date_green_card=start_date_green_card, end_date_green_card=end_date_green_card,
                               vehicle_make=vehicle_make, vehicle_model=vehicle_model, vehicle_year=vehicle_year,
                               countries_str=countries_str,
                               start_date_osgo=start_date_osgo, end_date_osgo=end_date_osgo, car_brand=car_brand,
                               car_model=car_model, car_year=car_year, car_registration_number=car_registration_number,
                               insurance_cost=insurance_cost,
                               start_date_personal=start_date_personal, end_date_personal=end_date_personal,
                               full_name=full_name, passport_data=passport_data,
                               insurance_cost_personal=insurance_cost_personal)
    else:
        return render_template('profile.html', email=email)


@app.route("/about")
def about():
    email = session.get('email')
    return render_template('about.html', email=email)


@app.route("/admin")
def admin():
    # Подключение к базе данных MySQL
    connection = create_connection()
    file_path = export_to_excel()
    print("Файл сохранен по пути:", file_path)  # Создание курсора для выполнения SQL-запросов
    cursor = connection.cursor()

    # Выполнение SQL-запроса для получения данных
    query = "SELECT DATE(start_date) AS day, SUM(insurance_cost) AS total_cost FROM insure_health GROUP BY day"
    cursor.execute(query)

    # Извлечение результатов запроса
    data = cursor.fetchall()
    dayss = []
    total_costs = []
    for row in data:
        dayss.append(row[0])
        total_costs.append(row[1])

    # Закрытие соединения с базой данных
    cursor.close()
    connection.close()

    # Построение графика для суммы
    plt.figure(figsize=(6, 5))
    plt.bar(dayss, total_costs)

    # plt.xlabel('Дата')
    plt.ylabel('Страховая сумма')
    plt.title('График страховой суммы по дням')
    plt.xticks(rotation=25)
    plt.tight_layout()

    # Форматирование оси x для отображения дат
    date_formatter = DateFormatter("%Y-%m-%d")
    plt.gca().xaxis.set_major_formatter(date_formatter)

    # Сохранение графика в файл
    graph_file_cost = 'static/image/graph.png'
    try:
        plt.savefig(graph_file_cost)
        print("Файл graph.png сохранен успешно.")
    except Exception as e:
        print("Ошибка сохранения файла graph.png:", str(e))

    db = create_connection()
    # Получение данных из таблиц и подсчет суммы id по start_date
    table_names = [
        "insure_credit_card",
        "insure_house",
        "insure_health",
        "insure_health_personal",
        "insure_car_osgo_vn",
        "insure_car_green_card"
    ]

    data = {}

    for table_name in table_names:
        cursor = db.cursor()
        query = f"SELECT start_date, SUM(id) FROM {table_name} GROUP BY start_date"
        cursor.execute(query)
        result = cursor.fetchall()
        data[table_name] = result

    # Создание гистограммы
    plt.figure(figsize=(6, 5))

    for table_name, result in data.items():
        dates = [row[0] for row in result]
        sums = [row[1] for row in result]
        plt.bar(dates, sums, label=table_name)

    # plt.xlabel("Дата")
    plt.ylabel("Количество страхований")
    plt.title("Количество страхований в зависимости от дня")
    plt.legend()
    plt.xticks(rotation=25)
    plt.tight_layout()

    # Сохранение гистограммы в файл
    plt.savefig("static/image/histogram.png")
    graph_file_amount = 'static/image/histogram.png'
    # Отображение HTML-шаблона с вставленным графиком
    return render_template('admin.html', graph_file_cost=graph_file_cost, graph_file_amount=graph_file_amount)


@app.route("/jsonchik", methods=['POST', 'GET'])
def jsonchik():
    if request.method == 'POST':
        path = request.form.get('path')  # Получаем выбранный путь сохранения
        # database_json = {}

        conn = create_connection()
        cursor = conn.cursor()

        # Получение данных из таблицы "user"
        cursor.execute('SELECT * FROM user')
        users = cursor.fetchall()

        # Получение данных из таблицы "insure_credit_card"
        cursor.execute('SELECT * FROM insure_credit_card')
        insure_credit_card = cursor.fetchall()

        # Получение данных из таблицы "insure_house"
        cursor.execute('SELECT * FROM insure_house')
        insure_house = cursor.fetchall()

        # Получение данных из таблицы "insure_health"
        cursor.execute('SELECT * FROM insure_health')
        insure_health = cursor.fetchall()

        # Получение данных из таблицы "insure_health_personal"
        cursor.execute('SELECT * FROM insure_health_personal')
        insure_health_personal = cursor.fetchall()

        # Получение данных из таблицы "tariff"
        cursor.execute('SELECT * FROM insure_car_osgo_vn')
        insure_car_osgo_vn = cursor.fetchall()

        # Получение данных из таблицы "tariff"
        cursor.execute('SELECT * FROM insure_car_green_card')
        insure_car_green_card = cursor.fetchall()

        # Получение данных из таблицы "question"
        cursor.execute('SELECT * FROM question')
        question = cursor.fetchall()

        # Соединение всех данных в один словарь
        data = {
            'users': users,
            'insure_credit_card': insure_credit_card,
            'insure_house': insure_house,
            'insure_health': insure_health,
            'insure_health_personal': insure_health_personal,
            'insure_car_osgo_vn': insure_car_osgo_vn,
            'insure_car_green_card': insure_car_green_card,
            'question': question
        }

        # Сохраняем JSON-объект в файл
        with open(path, 'w') as file:
            json.dump(data, file)
        print(f'База данных успешно экспортирована в формате JSON и сохранена по пути: {path}')
        return render_template('jsonchik.html')
    return render_template('jsonchik.html')


@app.route("/import_json", methods=['POST', 'GET'])
def import_json():
    cnx = create_connection()
    cursor = cnx.cursor()
    if request.method == 'POST':

        try:
            # Получение файла JSON из запроса
            file = request.files['file']
            data = json.load(file)

            # Импорт данных в таблицу "user"
            for user in data['user']:
                query = "INSERT INTO user (name, email, password) VALUES (%s, %s, %s)"
                values = (user['name'], user['email'], user['password'])
                cursor.execute(query, values)

                # Импорт данных в таблицу "question"
            for question in data['question']:
                query = "INSERT INTO question (email, phone, question) VALUES (%s, %s, %s)"
                values = (question['email'], question['phone'], question['question'])
                cursor.execute(query, values)

                # Импорт данных в таблицу "insure_credit_card"
            for insure_credit_card in data['insure_credit_card']:
                query = (
                    "INSERT INTO insure_credit_card (email, start_date, end_date, srok_strax, insure_sum, type_card, "
                    "bank_emitment, pay_system, number_card, phone_number, srok_deystv, fio, p2225, p2243) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
                values = (
                    insure_credit_card['email'],
                    insure_credit_card['start_date'],
                    insure_credit_card['end_date'],
                    insure_credit_card['srok_strax'],
                    insure_credit_card['insure_sum'],
                    insure_credit_card['type_card'],
                    insure_credit_card['bank_emitment'],
                    insure_credit_card['pay_system'],
                    insure_credit_card['number_card'],
                    insure_credit_card['phone_number'],
                    insure_credit_card['srok_deystv'],
                    insure_credit_card['fio'],
                    insure_credit_card['p2225'],
                    insure_credit_card['p2243']
                )
                cursor.execute(query, values)

            # Импорт данных в таблицу "insure_house"
            for item in data['insure_house']:
                query = """
                    INSERT INTO insure_house (email, phone_number, start_date, end_date, property_type, address, area, insure_sum, duration, owner_name, all_cost)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (
                    item['email'],
                    item['phone_number'],
                    item['start_date'],
                    item['end_date'],
                    item['property_type'],
                    item['address'],
                    item['area'],
                    item['insure_sum'],
                    item['duration'],
                    item['owner_name'],
                    item['all_cost']
                )
                cursor.execute(query, values)

            # Импорт данных в таблицу "insure_health"
            for item in data['insure_health']:
                query = """
                    INSERT INTO insure_health (email, phone_number, start_date, end_date, insurance_option, number_of_seats, driver_insurance_sum, passenger_insurance_sum, total_insurance_sum, driver_name, passenger_names, driver_birthdate, passenger_birthdates, insurance_cost)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (
                    item['email'],
                    item['phone_number'],
                    item['start_date'],
                    item['end_date'],
                    item['insurance_option'],
                    item['number_of_seats'],
                    item['driver_insurance_sum'],
                    item['passenger_insurance_sum'],
                    item['total_insurance_sum'],
                    item['driver_name'],
                    item['passenger_names'],
                    item['driver_birthdate'],
                    item['passenger_birthdates'],
                    item['insurance_cost']
                )
                cursor.execute(query, values)

            # Импорт данных в таблицу "insure_health_personal"
            for item in data['insure_health_personal']:
                query = """
                    INSERT INTO insure_health_personal (email, phone_number, start_date, end_date, full_name, passport_data, age, coverage_amount, duration, additional_option_ticks, additional_option_diseases, insurance_cost)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (
                    item['email'],
                    item['phone_number'],
                    item['start_date'],
                    item['end_date'],
                    item['full_name'],
                    item['passport_data'],
                    item['age'],
                    item['coverage_amount'],
                    item['duration'],
                    item['additional_option_ticks'],
                    item['additional_option_diseases'],
                    item['insurance_cost']
                )
                cursor.execute(query, values)

            # Импорт данных в таблицу "insure_car_osgo_vn"
            for item in data['insure_car_osgo_vn']:
                query = """
                    INSERT INTO insure_car_osgo_vn (email, phone_number, start_date, end_date, full_name, passport_data, age, coverage_amount, duration, additional_option_theft, additional_option_damage, car_brand, car_model, car_year, car_registration_number, insurance_cost)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (
                    item['email'],
                    item['phone_number'],
                    item['start_date'],
                    item['end_date'],
                    item['full_name'],
                    item['passport_data'],
                    item['age'],
                    item['coverage_amount'],
                    item['duration'],
                    item['additional_option_theft'],
                    item['additional_option_damage'],
                    item['car_brand'],
                    item['car_model'],
                    item['car_year'],
                    item['car_registration_number'],
                    item['insurance_cost']
                )
                cursor.execute(query, values)

            # Импорт данных в таблицу "insure_car_green_card"
            for item in data['insure_car_green_card']:
                query = """
                    INSERT INTO insure_car_green_card (email, phone_number, start_date, end_date, insurance_term, insure_sum, vehicle_type, vehicle_make, vehicle_model, vehicle_year, registration_number, owner_name, countries_str, insurance_cost)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (
                    item['email'],
                    item['phone_number'],
                    item['start_date'],
                    item['end_date'],
                    item['insurance_term'],
                    item['insure_sum'],
                    item['vehicle_type'],
                    item['vehicle_make'],
                    item['vehicle_model'],
                    item['vehicle_year'],
                    item['registration_number'],
                    item['owner_name'],
                    item['countries_str'],
                    item['insurance_cost']
                )
                cursor.execute(query, values)
            # Сохранение изменений
            cnx.commit()
            message = 'Успех'

            return render_template('import_json.html', message=message)
        except Exception as e:
            print(str(e))
            message = f'Ошибка {str(e)} попробуйте снова'
            return render_template('import_json.html', message=message)
        finally:
            # Закрытие соединения
            cursor.close()
            cnx.close()
    return render_template('import_json.html')


@app.route('/poisk_sort_vst', methods=['GET', 'POST'])
def poisk_sort_vst():
    cnx = create_connection()
    if request.method == 'POST':
        sort_option = request.form.get('sort_option')

        if sort_option == 'id':
            query = "SELECT * FROM question ORDER BY id"
        elif sort_option == 'question':
            query = "SELECT * FROM question ORDER BY question"
        else:
            query = "SELECT * FROM question"
    else:
        query = "SELECT * FROM question"

    # Выполняем запрос к базе данных
    cursor = cnx.cursor()
    cursor.execute(query)
    questions = cursor.fetchall()

    return render_template('poisk_sort_vst.html', questions=questions)


@app.route('/delete_question/<int:question_id>', methods=['POST'])
def delete_question(question_id):
    query = "DELETE FROM question WHERE id = %s"
    values = (question_id,)
    cnx = create_connection()
    # Выполняем запрос на удаление вопроса
    cursor = cnx.cursor()
    cursor.execute(query, values)
    cnx.commit()

    return redirect(url_for('poisk_sort_vst'))


@app.route("/strax", methods=['GET', 'POST'])
def strax():
    mydb = create_connection()
    # Получаем значение vehicle_make из параметров запроса
    vehicle_make = request.args.get('vehicle_make', '')

    # Создаем курсор для выполнения SQL-запросов
    cursor = mydb.cursor(dictionary=True)

    # Выполняем SQL-запрос с фильтром по полю vehicle_make
    query = "SELECT * FROM insure_car_green_card WHERE vehicle_make LIKE %s"
    cursor.execute(query, (f"%{vehicle_make}%",))

    # Получаем результаты запроса
    insurances = cursor.fetchall()

    return render_template('strax.html', insurances=insurances, vehicle_make=vehicle_make)


@app.route('/main', methods=['GET', 'POST'])
def main():
    db = create_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM insure_house")
    data = cursor.fetchall()
    return render_template('main.html', data=data)


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    db = create_connection()
    if request.method == 'POST':
        id = request.form['id']
        email = request.form['email']
        phone_number = request.form['phone_number']
        start_date = request.form['start_date']
        property_type = request.form['property_type']
        address = request.form['address']
        area = request.form['area']
        insure_sum = request.form['insure_sum']
        duration = request.form['duration']
        owner_name = request.form['owner_name']
        all_cost = request.form['all_cost']

        cursor = db.cursor()
        cursor.execute("""
            UPDATE insure_house SET
            email = %s,
            phone_number = %s,
            start_date = %s,
            property_type = %s,
            address = %s,
            area = %s,
            insure_sum = %s,
            duration = %s,
            owner_name = %s,
            all_cost = %s
            WHERE id = %s
        """, (
        email, phone_number, start_date, property_type, address, area, insure_sum, duration, owner_name, all_cost, id))

        db.commit()
        return redirect(url_for('main'))
    else:
        id = request.args.get('id')

        cursor = db.cursor()
        cursor.execute("SELECT * FROM insure_house WHERE id = %s", (id,))
        data = cursor.fetchone()
        if data:
            return render_template('edit.html', data=data)
        else:
            return 'Record not found.'


@app.route("/sign_in", methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        # Получение значений из формы
        email = request.form['email']
        password = request.form['password']

        # Подключение к базе данных MySQL
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            port='3306',
            database='python'
        )

        # Создание объекта "курсор" для выполнения SQL-запросов
        cursor = mydb.cursor()

        # Проверка наличия пользователя с таким же email в базе данных
        cursor.execute("SELECT id, password FROM user WHERE email = %s", (email,))
        user_data = cursor.fetchall()

        for row in user_data:
            print(row)

        if user_data and bcrypt.check_password_hash(user_data[0][1], password):
            cursor.close()
            mydb.close()
            message = "User successfully logged in."
            session['email'] = email
            return render_template('personal.html', email=email, message=message)

        elif password == 'admin1234' and email == 'admin@mail.ru':
            print(password, email)
            return redirect(url_for('admin'))
        else:
            # Пользователь с таким email и password не существует
            message = "User with this email and password does not exist."
            return render_template('sign_in.html', message=message)

    return render_template('sign_in.html')


# Страница для ввода нового пароля
@app.route('/user_new_password', methods=['GET', 'POST'])
def user_new_password():
    if request.method == 'POST':
        email = request.form['email']
        generate = generate_code()
        generate_cod = str(generate)
        print(generate_cod)
        session['email'] = email
        session['generate_cod'] = generate_cod

        # Отправка сообщения email
        ver = SendCheck(email)
        ver.sendCheck(body=generate_cod)

        sending_sms_phone(generate_cod, )

        return render_template('enter_code.html')
    return render_template('user_new_password.html')


@app.route('/enter_code', methods=['GET', 'POST'])
def enter_code():
    if 'email' not in session or 'generate_cod' not in session:
        return render_template('user_new_password.html')

    if request.method == 'POST':
        code = request.form['code']
        print(code)
        if str(code) == session['generate_cod']:
            return render_template('reset_password.html')
        else:
            return 'Invalid code. Please try again.'

    return render_template('enter_code.html', email=session['email'])


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if 'email' not in session or 'generate_cod' not in session:
        return render_template('user_new_password.html')

    if request.method == 'POST':
        new_password = request.form['new_password']
        email = session.get('email')
        update_password(email, new_password)
        session.pop('email')
        session.pop('generate_cod')
        return redirect('sign_in')

    return render_template('sign_in.html')


def update_password(email, new_password):
    # Ваш код для обновления пароля пользователя в базе данных

    # Предположим, что вы используете MySQL как базу данных
    # Установите соединение с базой данных
    connection = create_connection()

    # Создайте объект "курсор" для выполнения SQL-запросов
    cursor = connection.cursor()
    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')

    # Выполните SQL-запрос для обновления пароля пользователя
    sql = "UPDATE user SET password = %s WHERE email = %s"
    values = (hashed_password, email)
    cursor.execute(sql, values)

    # Подтвердите изменения
    connection.commit()

    # Закройте соединение и курсор
    cursor.close()
    connection.close()


@app.route("/registration", methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        if 'agree' in request.form:
            # Получение значений из формы
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']

            if len(password) < 9:
                message = "Длина пароля должна быть не менее 8 символов"
                return render_template('registration.html', message=message, name=name, email=email)

            if re.match("^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d]+$", password):
                print("Пароль содержит английские буквы и цифры.")
            else:
                message = "Используйте символы a-Z и цифры для ввода пароля"
                return render_template('registration.html', message=message, name=name, email=email)

            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            # Подключение к базе данных MySQL
            mydb = create_connection()

            # Создание объекта "курсор" для выполнения SQL-запросов
            cursor = mydb.cursor()

            # Проверка наличия пользователя с таким же email в базе данных
            sql = "SELECT * FROM user WHERE email = %s"
            val = (email,)
            cursor.execute(sql, val)
            existing_user = cursor.fetchone()

            if existing_user:
                # Пользователь с таким email уже существует
                message = "User with this email already exists."
            else:
                # SQL-запрос для вставки данных в таблицу
                sql = "INSERT INTO user (name, email, password) VALUES (%s, %s, %s)"
                val = (name, email, hashed_password)
                # Выполнение SQL-запроса
                cursor.execute(sql, val)

                # Отправка сообщения
                ver = SendCheck(email)
                ver.sendCheck(body='Congratulations, you have successfully registration!')

                # Подтверждение изменений в базе данных
                mydb.commit()

                message = "Data successfully saved in the database."

                # Закрытие соединения с базой данных
                mydb.close()

        else:
            # Чекбокс "I agree to the terms and conditions" не был выбран
            message = "The 'I agree to the terms and conditions' checkbox was not selected."

        return render_template('registration.html', message=message)

    return render_template('registration.html', message=None)


@app.route("/create")
def create():
    return render_template('create.html')


@app.route("/personal")
def personal():
    email = session.get('email')
    return render_template('personal.html', email=email)


@app.route("/personal_transport")
def personal_transport():
    email = session.get('email')
    return render_template('personal_transport.html', email=email)


@app.route("/osgo_vn")
def osgo_vn():
    email = session.get('email')
    return render_template('osgo_vn.html', email=email)


@app.route("/osgo_komp")
def osgo_komp():
    email = session.get('email')
    return render_template('osgo_komp.html', email=email)


@app.route("/green_card")
def green_card():
    email = session.get('email')
    return render_template('green_card.html', email=email)


@app.route("/kasko")
def kasko():
    email = session.get('email')
    return render_template('kasko.html', email=email)


@app.route("/personal_health")
def personal_health():
    email = session.get('email')
    return render_template('personal_health.html', email=email)


@app.route("/passangers_voditel")
def passangers_voditel():
    email = session.get('email')
    return render_template('passangers_voditel.html', email=email)


@app.route("/neschastnyu")
def neschastnyu():
    email = session.get('email')
    return render_template('neschastnyu.html', email=email)


@app.route("/personal_imushestvo")
def personal_imushestvo():
    email = session.get('email')
    return render_template('personal_imushestvo.html', email=email)


@app.route("/living_house")
def living_house():
    email = session.get('email')
    return render_template('living_house.html', email=email)


@app.route("/credit_card")
def credit_card():
    email = session.get('email')
    return render_template('credit_card.html', email=email)


@app.route("/personal_insure")
def personal_insure():
    email = session.get('email')
    return render_template('personal_insure.html', email=email)


@app.route("/insure_credit_card", methods=['POST', 'GET'])
def insure_credit_card():
    email = session.get('email')
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        insurance_term = request.form.get('srok_strax')
        insure_sum = request.form.get('insure_sum')
        type_card = request.form.get('type_card')
        bank_emitment = request.form.get('bank_emitment')
        pay_system = request.form.get('pay_system')
        card_number = request.form.get('number_card')
        card_expiration = request.form.get('srok_deystv')
        card_holder = request.form.get('fio')
        p2225 = request.form.get('p2225')
        p2243 = request.form.get('p2243')
        phone_number = request.form.get('phone_number')

        # Вывод значений в консоль
        print('Start Date:', start_date)
        print('End Date:', end_date)
        print('Insurance Term:', insurance_term)
        print('Insure Sum:', insure_sum)
        print('Type Card:', type_card)
        print('Bank Emitment:', bank_emitment)
        print('Pay System:', pay_system)
        print('Card Number:', card_number)
        print('Card Expiration:', card_expiration)
        print('Card Holder:', card_holder)
        print('P2225:', p2225)
        print('P2243:', p2243)
        print('phone_number:', phone_number)

        generate_pdf(email, start_date, end_date, 'credit_card')
        # Отправка сообщения email
        ver = SendCheck(email)
        ver.sendCheck(body='Congratulations, you have successfully insured your credit card!')
        ver.sendFile(file_path='static/documents/Заявление-на-страховани.docx')

        # Отправка сообщения телефон
        sending_sms_phone(text='Congratulations, you have successfully insured your credit card!',
                          receiver=phone_number)

        mydb = create_connection()
        cursor = mydb.cursor()
        # Выполнение запроса на вставку данных в таблицу insure_credit_card
        insert_query = """
                    INSERT INTO insure_credit_card (email, start_date, end_date, srok_strax, insure_sum, type_card, 
                    bank_emitment, pay_system, number_card, phone_number, srok_deystv, fio, p2225, p2243)
                    VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
        data = (
            email, start_date, end_date, insurance_term, insure_sum, type_card, bank_emitment, pay_system, card_number,
            phone_number, card_expiration, card_holder, p2225, p2243)
        cursor.execute(insert_query, data)
        mydb.commit()
        cursor.close()
        mydb.close()
        print('Успешно вставили в insure_credit_card')
        return render_template('oplata.html', cost=insure_sum, email=email)
    else:
        email = session.get('email')
        return render_template('insure_credit_card.html', email=email)


@app.route("/insure_house", methods=['POST', 'GET'])
def insure_house():
    email = session.get('email')
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        property_type = request.form.get('property_type')
        address = request.form.get('address')
        area = request.form.get('area')
        insure_sum = request.form.get('insure_sum')
        duration = request.form.get('duration')
        owner_name = request.form.get('owner_name')
        all_cost = request.form.get('all_cost')
        phone_number = request.form.get('phone_number')

        # Вывод значений в консоль
        print('Start Date:', start_date)
        print('End Date:', end_date)
        print('Property Type:', property_type)
        print('Address:', address)
        print('Area:', area)
        print('Insure Sum:', insure_sum)
        print('Duration:', duration)
        print('Owner Name:', owner_name)
        print('All Cost:', all_cost)

        generate_pdf(email, start_date, end_date, name_doc='house')

        # Отправка сообщения email
        ver = SendCheck(email)
        ver.sendCheck(body='Congratulations, you have successfully insured your house!')
        ver.sendFile(file_path='static/documents/Заявление-на-страховани.docx')

        # Отправка сообщения телефон
        sending_sms_phone(text='Congratulations, you have successfully insured your house!', receiver=phone_number)

        mydb = create_connection()
        cursor = mydb.cursor()
        # Выполнение запроса на вставку данных в таблицу insure_house
        insert_query = """
            INSERT INTO insure_house (email, phone_number, start_date, end_date, property_type, address, area, insure_sum, duration, owner_name, all_cost)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        data = (
            email, phone_number, start_date, end_date, property_type, address, area, insure_sum, duration, owner_name,
            all_cost)
        cursor.execute(insert_query, data)
        mydb.commit()
        cursor.close()
        mydb.close()
        print('Успешно вставили в insure_house')
        return render_template('oplata.html', cost=all_cost, email=email)
    else:
        email = session.get('email')
        return render_template('insure_house.html', email=email)


@app.route("/insure_health", methods=['POST', 'GET'])
def insure_health():
    email = session.get('email')
    if request.method == 'POST':
        insurance_option = request.form.get('insurance_option')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        number_of_seats = request.form.get('number_of_seats')
        driver_insurance_sum = request.form.get('driver_insurance_sum')
        passenger_insurance_sum = request.form.get('passenger_insurance_sum')
        total_insurance_sum = request.form.get('total_insurance_sum')
        driver_name = request.form.get('driver_name')
        passenger_names = request.form.get('passenger_names')
        driver_birthdate = request.form.get('driver_birthdate')
        passenger_birthdates = request.form.get('passenger_birthdates')
        phone_number = request.form.get('phone_number')
        insurance_cost = request.form.get('insurance_cost')

        # Вывод значений в консоль
        print('Insurance Option:', insurance_option)
        print('Start Date:', start_date)
        print('End Date:', end_date)
        print('Number of Seats:', number_of_seats)
        print('Driver Insurance Sum:', driver_insurance_sum)
        print('Passenger Insurance Sum:', passenger_insurance_sum)
        print('Total Insurance Sum:', total_insurance_sum)
        print('Driver Name:', driver_name)
        print('Passenger Names:', passenger_names)
        print('Driver Birthdate:', driver_birthdate)
        print('Passenger Birthdates:', passenger_birthdates)
        print('Phone Number:', phone_number)
        print('Insurance Cost:', insurance_cost)

        generate_pdf(email, start_date, end_date, name_doc='health')

        # Отправка сообщения email
        ver = SendCheck(email)
        ver.sendCheck(body='Congratulations, you have successfully insured your health!')
        ver.sendFile(file_path='static/documents/Заявление-на-страховани.docx')

        # Отправка сообщения телефон
        sending_sms_phone(text='Congratulations, you have successfully insured your health!', receiver=phone_number)
        if insurance_option == 'system_places':
            mydb = create_connection()
            cursor = mydb.cursor()
            # Выполнение запроса на вставку данных в таблицу insure_health
            insert_query = """
                        INSERT INTO insure_health (email, phone_number, start_date, end_date, insurance_option, number_of_seats, 
                        driver_insurance_sum, passenger_insurance_sum, driver_name, passenger_names, driver_birthdate, 
                        passenger_birthdates, insurance_cost)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
            data = (
                email, phone_number, start_date, end_date, insurance_option, number_of_seats, driver_insurance_sum,
                passenger_insurance_sum, driver_name, passenger_names, driver_birthdate, passenger_birthdates,
                insurance_cost)
            cursor.execute(insert_query, data)
            mydb.commit()
            cursor.close()
            mydb.close()
            print('Успешно вставили в insure_house')
            return render_template('oplata.html', cost=insurance_cost, email=email)

        elif insurance_option == 'flat_system':
            mydb = create_connection()
            cursor = mydb.cursor()
            # Выполнение запроса на вставку данных в таблицу insure_health
            insert_query = """
                INSERT INTO insure_health (email, phone_number, start_date, end_date, insurance_option, number_of_seats, 
                total_insurance_sum, driver_name, passenger_names, driver_birthdate, passenger_birthdates, insurance_cost)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                           """
            data = (
                email, phone_number, start_date, end_date, insurance_option, number_of_seats, total_insurance_sum,
                driver_name, passenger_names, driver_birthdate, passenger_birthdates, insurance_cost)
            cursor.execute(insert_query, data)
            mydb.commit()
            cursor.close()
            mydb.close()
            print('Успешно вставили в insure_house')
            return render_template('oplata.html', cost=insurance_cost, email=email)
    else:
        return render_template('insure_health.html', email=email)


@app.route("/insure_health_personal", methods=['POST', 'GET'])
def insure_health_personal():
    email = session.get('email')
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        full_name = request.form.get('full_name')
        passport_data = request.form.get('passport_data')
        age = request.form.get('age')
        coverage_amount = request.form.get('coverage_amount')
        duration = request.form.get('duration')
        additional_option_ticks = request.form.get('additional_option_ticks')
        additional_option_diseases = request.form.get('additional_option_diseases')
        insurance_cost = request.form.get('insurance_cost')
        phone_number = request.form.get('phone_number')

        print('Phone Number:', phone_number)
        print('Insurance Cost:', insurance_cost)
        print('email:', email)

        generate_pdf(email, start_date, end_date, name_doc='health_personal')

        # Отправка сообщения email
        ver = SendCheck(email)
        ver.sendCheck(body='Congratulations, you have successfully insured your health!')
        ver.sendFile(file_path='static/documents/Заявление-на-страховани.docx')

        # Отправка сообщения телефон
        sending_sms_phone(text='Congratulations, you have successfully insured your health!', receiver=phone_number)

        mydb = create_connection()
        cursor = mydb.cursor()
        # Выполнение запроса на вставку данных в таблицу insure_health
        insert_query = """
                    INSERT INTO insure_health_personal (email, phone_number, start_date, end_date, full_name, passport_data, 
                    age, coverage_amount, duration, additional_option_ticks, additional_option_diseases, insurance_cost)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
        data = (
            email, phone_number, start_date, end_date, full_name, passport_data, age, coverage_amount, duration,
            additional_option_ticks, additional_option_diseases, insurance_cost)
        cursor.execute(insert_query, data)
        mydb.commit()
        cursor.close()
        mydb.close()
        print('Успешно вставили в insure_house_personal')
        return render_template('oplata.html', cost=insurance_cost, email=email)

    else:
        return render_template('insure_health_personal.html', email=email)


@app.route("/insure_car_osgo_vn", methods=['POST', 'GET'])
def insure_car_osgo_vn():
    email = session.get('email')
    if request.method == 'POST':
        phone_number = request.form.get('phone_number')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        full_name = request.form.get('full_name')
        passport_data = request.form.get('passport_data')
        age = request.form.get('age')
        coverage_amount = request.form.get('coverage_amount')
        duration = request.form.get('duration')
        additional_option_theft = request.form.get('additional_option_theft')
        additional_option_damage = request.form.get('additional_option_damage')
        car_brand = request.form.get('car_brand')
        car_model = request.form.get('car_model')
        car_year = request.form.get('car_year')
        car_registration_number = request.form.get('car_registration_number')
        insurance_cost = request.form.get('insurance_cost')

        print('Phone Number:', phone_number)
        print('Insurance Cost:', insurance_cost)
        print('email:', email)

        generate_pdf(email, start_date, end_date, name_doc='car_osgo')

        # Отправка сообщения email
        ver = SendCheck(email)
        ver.sendCheck(body='Congratulations, you have successfully insured your car!')
        ver.sendFile(file_path='static/documents/Заявление-на-страховани.docx')

        # Отправка сообщения телефон
        sending_sms_phone(text='Congratulations, you have successfully insured your car!', receiver=phone_number)

        mydb = create_connection()
        cursor = mydb.cursor()
        # Выполнение запроса на вставку данных в таблицу insure_health
        insert_query = """
                    INSERT INTO insure_car_osgo_vn (email, phone_number, start_date, end_date, full_name, passport_data,
                    age, coverage_amount, duration, additional_option_theft, additional_option_damage, car_brand,
                    car_model, car_year, car_registration_number, insurance_cost)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s  )
                    """
        data = (
            email, phone_number, start_date, end_date, full_name, passport_data,
            age, coverage_amount, duration, additional_option_theft, additional_option_damage, car_brand,
            car_model, car_year, car_registration_number, insurance_cost)
        cursor.execute(insert_query, data)
        mydb.commit()
        cursor.close()
        mydb.close()
        print('Успешно вставили в insure_car_osgo_vn')
        return render_template('oplata.html', cost=insurance_cost, email=email)

    else:
        return render_template('insure_car_osgo_vn.html', email=email)


@app.route("/insure_car_green_card", methods=['POST', 'GET'])
def insure_car_green_card():
    email = session.get('email')
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        insurance_term = request.form.get('insurance_term')
        insure_sum = request.form.get('insure_sum')
        phone_number = request.form.get('phone_number')
        vehicle_type = request.form.get('vehicle_type')
        vehicle_make = request.form.get('vehicle_make')
        vehicle_model = request.form.get('vehicle_model')
        vehicle_year = request.form.get('vehicle_year')
        registration_number = request.form.get('registration_number')
        owner_name = request.form.get('owner_name')
        countries = request.form.getlist('countries[]')
        insurance_cost = request.form.get('insurance_cost')

        # Объединение выбранных стран в строку
        countries_str = ', '.join(countries)

        print('insurance_cost:', insurance_cost)
        print('Countries to Visit:', countries_str)

        generate_pdf(email, start_date, end_date, name_doc='green_card')

        # Отправка сообщения email
        ver = SendCheck(email)
        ver.sendCheck(body='Congratulations, you have successfully insured your green card!')
        ver.sendFile(file_path='static/documents/Заявление-на-страховани.docx')

        # Отправка сообщения телефон
        sending_sms_phone(text='Congratulations, you have successfully insured your green card!', receiver=phone_number)

        mydb = create_connection()
        cursor = mydb.cursor()
        # Выполнение запроса на вставку данных в таблицу insure_health
        insert_query = """
                       INSERT INTO insure_car_green_card (email, phone_number, start_date, end_date, insurance_term, insure_sum,
                       vehicle_type, vehicle_make, vehicle_model, vehicle_year, registration_number, owner_name,
                       countries_str, insurance_cost)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                       """
        data = (
            email, phone_number, start_date, end_date, insurance_term, insure_sum,
            vehicle_type, vehicle_make, vehicle_model, vehicle_year, registration_number, owner_name,
            countries_str, insurance_cost)
        cursor.execute(insert_query, data)
        mydb.commit()
        cursor.close()
        mydb.close()
        print('Успешно вставили в insure_car_green_card')
        return render_template('oplata.html', cost=insurance_cost, email=email)

    else:
        return render_template('insure_car_green_card.html', email=email)
    return render_template('insure_car_green_card.html', email=email)


@app.route("/organization")
def organization():
    email = session.get('email')
    return render_template('organization.html', email=email)


@app.route('/insure', methods=['POST', 'GET'])
def insure():
    if request.method == 'POST':
        email = session.get('email')
        mydb = create_connection()
        cursor = mydb.cursor()

        user_type = request.form.get('user-type')

        if user_type == 'physical':
            surname = request.form['surname']
            name = request.form['name']
            fathername = request.form['fathername']
            passport = request.form['pasport']
            phone = request.form['phone']
            birth_date = request.form['year'] + '-' + request.form['month'] + '-' + request.form['day']

            # Выполнение запроса на вставку данных в таблицу physical_users
            insert_query = """
            INSERT INTO physical_users (polzovatel_id, email, name, surname, fathername, passport, phone, birth_date)
            VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)
            """

            data = (email, name, surname, fathername, passport, phone, birth_date)
            cursor.execute(insert_query, data)
            mydb.commit()


        elif user_type == 'legal':
            company = request.form['company']
            address = request.form['address_yr_face']
            inn = request.form['inn']
            field_of_activity = request.form['field_of_activity']
            phone = request.form['phone']
            document = request.form['document']
            # Дополнительная обработка файла документов юридического лица

            # Выполнение запроса на вставку данных в таблицу legal_users
            insert_query = """
            INSERT INTO legal_users (polzovatel_id, email, company, address, inn, field_of_activity, phone, document)
            VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)
            """

            data = (email, company, address, inn, field_of_activity, phone, document)
            cursor.execute(insert_query, data)
            mydb.commit()

        cursor.close()
        mydb.close()

        return render_template('insure.html', email=email)
    else:
        email = session.get('email')
        return render_template('insure.html', email=email)


@app.route("/online_zayavka", methods=['POST', 'GET'])
def online_zayavka():
    if request.method == 'POST':
        mydb = create_connection()
        cursor = mydb.cursor()

        email = session.get('email')
        phone = request.form['phone']
        question = request.form['question']

        # Выполнение запроса на вставку данных в таблицу question
        insert_query = """
                    INSERT INTO question (email, phone, question)
                    VALUES (%s, %s, %s)
                    """
        data = (email, phone, question)
        cursor.execute(insert_query, data)
        mydb.commit()
        print('вопрос пришёл')
        cursor.close()
        mydb.close()

        return render_template('online_zayavka.html', email=email)
    else:
        email = session.get('email')
        return render_template('online_zayavka.html', email=email)


@app.route("/oplata", methods=['POST', 'GET'])
def oplata():
    email = session.get('email')
    if request.method == 'POST':
        email = session.get('email')
        return render_template('personal.html', email=email)
    return render_template('oplata.html', email=email)


if __name__ == "__main__":
    app.run(debug=True)
