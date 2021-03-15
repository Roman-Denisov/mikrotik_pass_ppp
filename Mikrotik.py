import routeros_api
import csv
import random
import string


def pass_gen():

    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits + string.punctuation
    size = random.randrange(11, 12)
    return ''.join(random.choice(chars) for x in range(size))


def oldpass():

    list_secrets = api.get_resource('/ppp/secret/')  # запрос на вывод всех секретов (профилей) PPP
    list_secrets.get()  # выполнение запроса
    with open(f, mode='w', encoding='UTF-8') as file:    # открываем файл для рассылки

        fields = ["login", "password", "mail", "newpassword"]    # пишем заголовки в рассылке
        file_writer = csv.DictWriter(file, delimiter=";", lineterminator='\n', fieldnames=fields)   # параметры csv
        file_writer.writeheader()   # пишем заголовки в рассылке

        for secret in list_secrets.get():    # парсим миркотик РРР. Выбираем профили поштучно из запроса
            password = pass_gen()   # генерируем рандомный пароль с каждым заходом в цикл
            file_writer.writerow({"login": secret.get('name'), "password": secret.get('password'),
                                  "newpassword": password})    # пишем файл и сразу заполняем столбцы "логин" и т.п.


def newpass():

    list_secrets = api.get_resource('/ppp/secret/')  # запрос на вывод всех секретов (профилей) PPP
    list_secrets.get()  # выполнение запроса
    set_password = api.get_resource('/ppp/secret/') # запрос на вывод всех секретов (профилей) PPP (для смены)
    with open(f, encoding='utf-8') as file2:    # открываем файл, который указали в начале

        file_reader = csv.DictReader(file2, delimiter=";")  # считываем его

        for row in file_reader:     # проходим по строкам в файле

            for secret in list_secrets.get():   # проходим по профилям PPP в микротике
                profile_id = secret.get('id')  # присваиваем переменной значение идентификатора
                profile_name = secret.get('name')  # присваиваем переменной значение логина VPN

                if row['login'] == profile_name:       # если строка Login в файле и Login на микротике совпали то:

                    if secret.get('name') == 'name_you_do_not_need_to_change' or \
                            secret.get('name') == 'another_name_should_not_be_changed'    # исправьте на имя профиля

                        profile_id = secret.get('id')
                        new_password = secret.get('password')
                        print(f'пароль не изменился для {secret.get("name")} - {new_password}. Его ID {profile_id}')

                    else:

                        print(f'пароль для {secret.get("name")}: {row["newpassword"]}. Его ID {profile_id}')
                        set_password.set(id=profile_id, password=row["newpassword"])    # внос изменений в MikroTik


while True:
    try:

        ip_address = input('ip-адрес Микротика: ')
        username = input('Пользователь: ')
        password = input('Пароль: ')

        connection = routeros_api.RouterOsApiPool(ip_address,
                                                  username=username,
                                                  password=password,
                                                  port=8728,
                                                  use_ssl=False,
                                                  plaintext_login=True)
        api = connection.get_api()
        break

    except routeros_api.exceptions.RouterOsApiCommunicationError:
        print('Неверные данные авторизации')
        continue

    except routeros_api.exceptions.RouterOsApiConnectionError:
        print('Устройство не найдено, проверьте IP')
        continue


print('\n Если у вас нет файла для рассылки, программа может его сформировать. \n'
      'Вы можете сразу указать файл, откуда будут браться пароли, но он должен быть правильно отформатирован. \n'
      'Укажите ПОЛНЫЙ (название и расширение тоже) путь до файла. \n ')

f = input('Файл для рассылки (пример.csv): ')  # файл для будущей рассылки

while True:  # программа в цикле, чтобы не приходилось заново подключать

    try:

        a = int(input('Выгрузить в файл и создать пароли - 1;\n'
                      'Обновить на микротике - 2;\n'
                      'Выход - 0: \n'))
        if a == 1:
            try:
                oldpass()
            except PermissionError:
                print(' Ошибка! Закройте файл!')
            except FileNotFoundError:
                print('Проверьте путь до файла')
        elif a == 2:
            newpass()
        elif a == 0:
            break
        else:
            print('Неправильно.')

    except ValueError:
        print('Нужно ввести цифру!')


