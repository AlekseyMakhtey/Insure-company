import mysql.connector

mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    port='3306',
    database='python'
)

mycursor = mydb.cursor()

# Добавление значений в таблицу "user"
user_values = [
    ('John Doe', 'john@example.com', 'password123'),
    ('Jane Smith', 'jane@example.com', 'password456'),
    ('Mike Johnson', 'mike@example.com', 'password789')
]
user_query = "INSERT INTO user (name, email, password) VALUES (%s, %s, %s)"
mycursor.executemany(user_query, user_values)
mydb.commit()

# Добавление значений в таблицу "individual"
individual_values = [
    (1, 'John', 'Doe', '1990-01-01'),
    (2, 'Jane', 'Smith', '1985-05-10'),
    (3, 'Mike', 'Johnson', '1992-11-15')
]
individual_query = "INSERT INTO individual (polzovatel_id, name, surname, birth_date) VALUES (%s, %s, %s, %s)"
mycursor.executemany(individual_query, individual_values)
mydb.commit()

# Добавление значений в таблицу "entity"
entity_values = [
    (1, 'Company A', '1234567890'),
    (2, 'Company B', '0987654321'),
    (3, 'Company C', '5432109876')
]
entity_query = "INSERT INTO entity (polzovatel_id, name_company, inn) VALUES (%s, %s, %s)"
mycursor.executemany(entity_query, entity_values)
mydb.commit()

# Добавление значений в таблицу "branch"
branch_values = [
    (1, 'Branch X', '123 Main St'),
    (2, 'Branch Y', '456 Elm St'),
    (3, 'Branch Z', '789 Oak St')
]
branch_query = "INSERT INTO branch (polzovatel_id, name_branch, address) VALUES (%s, %s, %s)"
mycursor.executemany(branch_query, branch_values)
mydb.commit()

# Добавление значений в таблицу "manager"
manager_values = [
    (1, 1, 'Manager 1', 'Doe'),
    (2, 2, 'Manager 2', 'Smith'),
    (3, 3, 'Manager 3', 'Johnson')
]
manager_query = "INSERT INTO manager (polzovatel_id, branch_id, name, surname) VALUES (%s, %s, %s, %s)"
mycursor.executemany(manager_query, manager_values)
mydb.commit()

# Добавление значений в таблицу "tariff"
tariff_values = [
    (1, 'Tariff 1', 'Description 1'),
    (2, 'Tariff 2', 'Description 2'),
    (3, 'Tariff 3', 'Description 3')
]
tariff_query = "INSERT INTO tariff (manager_id, name_tariff, description) VALUES (%s, %s, %s)"
mycursor.executemany(tariff_query, tariff_values)
mydb.commit()

# Добавление значений в таблицу "report"
report_values = [
    (1, '2023-01-01', 100),
    (2, '2023-02-01', 200),
    (3, '2023-03-01', 300)
]
report_query = "INSERT INTO report (tariff_id, date, volume_of_sales) VALUES (%s, %s, %s)"
mycursor.executemany(report_query, report_values)
mydb.commit()

mycursor.execute('select * from user')

user = mycursor.fetchall()

for row in user:
    print(row)

# Закрытие подключения к базе данных
mycursor.close()
mydb.close()
