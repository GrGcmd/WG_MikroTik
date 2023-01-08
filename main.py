from PyQt6 import uic
from PyQt6 import QtWidgets
from Forms import main  # Это наш конвертированный файл дизайна
from Forms import config  # Это наш конвертированный файл дизайна
from Forms import message  # Это наш конвертированный файл дизайна
from Forms import help  # Это наш конвертированный файл дизайна


import sys
import os
import paramiko
import os
from datetime import datetime
import cryptocode
password_crypto_key = 'ZfkuhhiyKg4dAYiZgB6Z'



#Функция получения полной даты
def date_update_full():
    time_date = datetime.now()
    time_date = time_date.strftime("%d-%m-%Y %H:%M")
    return time_date

#Функция записи логов
def write_log(text_log):
    print(text_log)
    file_address = os.getcwd() + '\\log\\other.log'
    # Подсчитаем количество строк в файле
    with open(file_address, encoding="utf-8") as f:
        line_count = 0
        for line in f:
            line_count += 1
    if line_count > 5000:
        i = 1
        while i != 0:
            if os.path.exists(file_address + str(i)):
                i += 1
            else:
                os.renames(file_address, file_address + str(i))
                # Запишем лог в файл
                f_log = open(file_address, 'a', encoding="utf-8")
                f_log.write(str(date_update_full()) + ' || ' + text_log + '\n')
                f_log.close()
                i = 0
    else:
        # Запишем лог в файл
        f_log = open(file_address, 'a', encoding="utf-8")
        f_log.write(str(date_update_full()) + ' || ' + text_log + '\n')
        f_log.close()

def check_license():
    return 0

#Функция подключения через SSH
def ssh_connect(host,user,secret,port,command_ex):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=user, password=secret, port=port)
    stdin, stdout, stderr = client.exec_command(command_ex)
    data = stdout.read() + stderr.read()
    client.close()
    return str(data);

class Window_main(QtWidgets.QMainWindow, main.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # 
        self.pushButton.clicked.connect(self.exit)
        self.pushButton_2.clicked.connect(self.wg_add_user)
        self.pushButton_7.clicked.connect(self.goto_window_config)
        self.pushButton_6.clicked.connect(self.wg_remove_user)
        self.pushButton_9.clicked.connect(self.open_folder_config)
        self.pushButton_10.clicked.connect(self.wg_enable_user)
        self.pushButton_11.clicked.connect(self.wg_disable_user)
        self.pushButton_12.clicked.connect(self.wg_get_users)
        self.pushButton_13.clicked.connect(self.open_folder_users_excel)
        self.pushButton_8.clicked.connect(self.goto_window_help)

    def wg_add_user(self):
        # ---------------------------------------
        # Проверим лицензию
        if  check_license() == 1:
            self.Window_message = Window_message()
            self.Window_message.label.setText('Ошибка чтения файла с лицензией. Обратитесь к разработчику.')
            self.Window_message.show()
            return
        elif check_license() == 2:
            self.Window_message = Window_message()
            self.Window_message.label.setText('Срок лицензии истёк. Обратитесь к разработчику.')
            self.Window_message.show()
            return
        # ---------------------------------------
        # Проверим заполнено ли поле
        if self.lineEdit.text() == '':
            self.Window_message = Window_message()
            self.Window_message.label.setText('Имя пользователя обязательно к заполнению!')
            self.Window_message.show()
            return
        # ---------------------------------------
        username = str(self.lineEdit.text())

        # Прочитаем конфигурацию
        try:
            file_address = os.getcwd() + '\\wg_pre_config.conf'
            f_conf = open(file_address, 'r', encoding="utf-8")
            split_result = str(f_conf.readline()).split(':')
            server_ip = cryptocode.decrypt(split_result[0], password_crypto_key)
            server_login = cryptocode.decrypt(split_result[1], password_crypto_key)
            server_password = cryptocode.decrypt(split_result[2], password_crypto_key)
            server_port = split_result[3]
            wg_ip = split_result[4]
            wg_port = split_result[5]
            wg_pool_ip_start = split_result[6]
            wg_pool_ip_end = split_result[7]
            wg_interface_name_server = split_result[8]
            wg_server_ip_into_vpn = split_result[9]
            wg_dns = split_result[10]
            wg_routers = split_result[11]
            f_conf.close()
            write_log('Конфигурационный файл перед подготовкой формирования конфига клиента прочитан успешно.')
        except:
            write_log('Ошибка чтения конфигурационного файла wg_pre_config.conf перед подготовкой генерации конфига клиента. Возможно его нет')
            self.Window_message = Window_message()
            self.Window_message.label.setText('Предварительная конфигурация не настроена.')
            self.Window_message.show()
            return

        # Удалим интерфейс wireguard test если он есть
        try:
            ssh_connect(server_ip, server_login, server_password,server_port,'/interface/wireguard/remove [find name=test]')
        except:
            write_log('Ошибка подключения к MikroTik. Проверьте настройки.')
            self.Window_message = Window_message()
            self.Window_message.label.setText('Ошибка подключения. Проверьте настройки.')
            self.Window_message.show()
            return


        # Определим существование пользователя
        try:
            result = ssh_connect(server_ip, server_login, server_password,server_port,'/interface/wireguard/peers print from=[find comment=' + username + ']')
            result_index = result.find(username)
            if result_index != -1:
                write_log('WG Пользователь ' + username + ' уже существует. Нового с таким же именем создать нельзя.')
                self.Window_message = Window_message()
                self.Window_message.label.setText('Пользователь ' + username + ' уже существует.')
                self.Window_message.show()
                return
        except:
            write_log('Ошибка подключения к серверу. Проверьте настройки.')
            self.Window_message = Window_message()
            self.Window_message.label.setText('Ошибка подключения. Проверьте настройки.')
            self.Window_message.show()
            return

            # ------------------------------------
        # Определим Next IP адрес для клиента
        try:
            result_index = 0
            split_result = wg_pool_ip_start.split('.')
            ip_address_1_octed_start = int(split_result[0])
            ip_address_2_octed_start = int(split_result[1])
            ip_address_3_octed_start = int(split_result[2])
            ip_address_4_octed_start = int(split_result[3])-1

            split_result = wg_pool_ip_end.split('.')
            ip_address_3_octed_end = int(split_result[2])
            ip_address_4_octed_end = int(split_result[3])

            result = ssh_connect(server_ip, server_login, server_password,server_port, '/interface/wireguard/peers export')

            while result_index != -1:
                ip_address_4_octed_start += 1
                ip_address = str(ip_address_1_octed_start) + '.' + str(ip_address_2_octed_start) + '.' + str(ip_address_3_octed_start) + '.' + str(ip_address_4_octed_start)
                if ip_address == wg_server_ip_into_vpn:
                    ip_address_4_octed_start += 1
                if ip_address_4_octed_start == ip_address_4_octed_end:
                    if ip_address_3_octed_start < ip_address_3_octed_end:
                        ip_address_3_octed_start += 1
                        ip_address_4_octed_start = 1
                        ip_address = str(ip_address_1_octed_start) + '.' + str(ip_address_2_octed_start) + '.' + str(ip_address_3_octed_start) + '.' + str(ip_address_4_octed_start)
                    else:
                        write_log('WG Попытка создания пользователя ' + username + '. Превышено максимальное количество пользователей на сервере')
                        self.Window_message = Window_message()
                        self.Window_message.label.setText('Превышено максимальное количество клиентов.')
                        self.Window_message.show()
                        return
                result_index = result.find(str(ip_address))

            user_ip_address = ip_address + '/32'
        except:
            write_log('Ошибка вычисления свободного IP. Проверьте настройки или обратитесь к администратору.')
            self.Window_message = Window_message()
            self.Window_message.label.setText('Ошибка вычисления свободного IP')
            self.Window_message.show()
            return

        # ------------------------------------
        # Определим public ключ от сервера WG
        try:
            result = ssh_connect(server_ip, server_login, server_password,server_port,'/interface/wireguard/print from=[find name='+wg_interface_name_server+'] proplist=public-key')
            split_result = result.split('"')
            peer_public_key = split_result[1]
            if peer_public_key == '':
                write_log('Ошибка-прерывание определения public ключа от сервера WG. Возможно имя интерфейса задано неверно')
                self.Window_message = Window_message()
                self.Window_message.label.setText('Ошибка определения public ключа от сервера WG')
                self.Window_message.show()
                return
        except:
            write_log('Ошибка определения public ключа от сервера WG. Возможно имя интерфейса задано неверно')
            self.Window_message = Window_message()
            self.Window_message.label.setText('Ошибка определения public ключа от сервера WG')
            self.Window_message.show()
            return

        # ------------------------------------
        # Определим private public ключ для интерфейса клиента
        try:
            ssh_connect(server_ip, server_login, server_password,server_port, '/interface/wireguard/add name=test disabled=yes')
            result = ssh_connect(server_ip, server_login, server_password,server_port,'/interface/wireguard/print from=[find name=test] proplist=private-key,public-key')
            split_result = result.split('"')
            interface_private_key = split_result[1]
            interface_public_key = split_result[3]
            ssh_connect(server_ip, server_login, server_password,server_port, '/interface/wireguard/remove [find name=test]')
        except:
            write_log('Ошибка определения private public ключей для интерфейса клиента')
            self.Window_message = Window_message()
            self.Window_message.label.setText('Ошибка определения ключей для интерфейса клиента.')
            self.Window_message.show()
            return

        # Определим  Preshared key
        preshared_key = 'oKgSEPEArSw/98BW4zzOGiNhPuPjIpAtknHE45dq7Gc='

        try:
            # ------------------------------------
            # Выполним основную комманду для создания пользователя на сервере
            command_ex = '/interface/wireguard/peers add interface='+wg_interface_name_server+' public-key="' + interface_public_key + '" allowed-address=' + user_ip_address + ' comment=' + username + ' preshared-key="' + preshared_key + '"'
            if ssh_connect(server_ip, server_login, server_password,server_port, command_ex) == "b''":
                write_log('WG Пользователь ' + username + ' создан на сервере ' + server_ip + '.')
            else:
                write_log('WG Ошибка создания пользователя на сервере ' + server_ip + '. Имя: ' + username + '. Что то пошло не так.')
                self.Window_message = Window_message()
                self.Window_message.label.setText('Ошибка создания пользователя на сервере.')
                self.Window_message.show()
                return
        except:
            write_log('Ошибка создания пользователя на сервере. Что то пошло не так.')
            self.Window_message = Window_message()
            self.Window_message.label.setText('Ошибка создания пользователя на сервере.')
            self.Window_message.show()
            return

        # ------------------------------------
        # Сформируем конфигурационный файл для WireGuard и покажем его
        try:
            file_address = os.getcwd() + '\\vpn\\wg\\' + username + '_wg.conf'
            f_conf = open(file_address, 'w+', encoding="utf-8")
            f_conf.write('[Interface]\n')
            f_conf.write('PrivateKey = ' + interface_private_key + '\n')
            f_conf.write('ListenPort = 13231\n')
            f_conf.write('Address = ' + user_ip_address + '\n')
            f_conf.write('DNS = ' + wg_dns + '\n')
            f_conf.write('\n')
            f_conf.write('[Peer]\n')
            f_conf.write('PublicKey = ' + peer_public_key + '\n')
            f_conf.write('PresharedKey = ' + preshared_key + '\n')
            f_conf.write('AllowedIPs = ' + wg_routers + '\n')
            f_conf.write('Endpoint = ' + wg_ip + ':' + wg_port + '\n')
            f_conf.write('\n')
            f_conf.close()
            write_log('WG Конфигурационный файл для ' + username + ' создан успешно.')
        except:
            write_log('WG Ошибка создания файла конфигурации для пользователя ' + username)
            return

        write_log('WG Создание пользователя ' + username + ' прошло успешно.')
        self.Window_message = Window_message()
        self.Window_message.label.setText('Пользователь ' + username + ' создан.')
        self.Window_message.show()
        return 1

    def wg_remove_user(self):
        # ---------------------------------------
        # Проверим лицензию
        if check_license() == 1:
            self.Window_message = Window_message()
            self.Window_message.label.setText('Ошибка чтения файла с лицензией. Обратитесь к разработчику.')
            self.Window_message.show()
            return
        elif check_license() == 2:
            self.Window_message = Window_message()
            self.Window_message.label.setText('Срок лицензии истёк. Обратитесь к разработчику.')
            self.Window_message.show()
            return
        # ---------------------------------------
        # Проверим заполнено ли поле
        if self.lineEdit.text() == '':
            self.Window_message = Window_message()
            self.Window_message.label.setText('Имя пользователя обязательно к заполнению!')
            self.Window_message.show()
            return
        # -------------
        # Прочитаем конфигурацию
        try:
            file_address = os.getcwd() + '\\wg_pre_config.conf'
            f_conf = open(file_address, 'r', encoding="utf-8")
            split_result = str(f_conf.readline()).split(':')
            server_ip = cryptocode.decrypt(split_result[0], password_crypto_key)
            server_login = cryptocode.decrypt(split_result[1], password_crypto_key)
            server_password = cryptocode.decrypt(split_result[2], password_crypto_key)
            server_port = split_result[3]
            f_conf.close()
            write_log('Конфигурационный файл перед подготовкой формирования конфига клиента прочитан успешно.')
        except:
            write_log('Ошибка чтения конфигурационного файла wg_pre_config.conf перед подготовкой генерации конфига клиента. Возможно его нет')
            self.Window_message = Window_message()
            self.Window_message.label.setText('Предварительная конфигурация не настроена.')
            self.Window_message.show()
            return

        username = str(self.lineEdit.text())
        # ------------------------------------
        # Определим существование пользователя и удалим если он есть
        try:
            result = ssh_connect(server_ip, server_login, server_password, server_port,'/interface/wireguard/peers print from=[find comment=' + username + ']')
            result_index = result.find(username)
            if result_index != -1:
                ssh_connect(server_ip, server_login, server_password,server_port, '/interface/wireguard/peers remove [find comment=' + username + ']')
                write_log('WG Пользователь ' + username + ' удалён успешно.')
                self.Window_message = Window_message()
                self.Window_message.label.setText('Пользователь ' + username + ' удалён успешно.')
                self.Window_message.show()
            else:
                write_log('WG Пользователь ' + username + ' не существует на сервере.' + server_ip)
                self.Window_message = Window_message()
                self.Window_message.label.setText('Пользователь ' + username + ' не существует на сервере.')
                self.Window_message.show()
        except:
            write_log('Ошибка удаления пользователя. Что то пошло не так.')
            self.Window_message = Window_message()
            self.Window_message.label.setText('Ошибка удаления пользователя. Проверьте настройки.')
            self.Window_message.show()

        # ------------------------------------
        # Попытаемся удалить конфиг если он есть
        try:
            file_address = os.getcwd() + '\\vpn\\wg\\' + username + '_wg.conf'
            os.remove(file_address)
            write_log('WG Конфигурационный файл для ' + username + ' удалён успешно.')
        except:
            write_log('WG Конфигурационный файл для ' + username + ' удалён ранее или не существует.')

    def wg_enable_user(self):
        # ---------------------------------------
        # Проверим лицензию
        if check_license() == 1:
            self.Window_message = Window_message()
            self.Window_message.label.setText('Ошибка чтения файла с лицензией. Обратитесь к разработчику.')
            self.Window_message.show()
            return
        elif check_license() == 2:
            self.Window_message = Window_message()
            self.Window_message.label.setText('Срок лицензии истёк. Обратитесь к разработчику.')
            self.Window_message.show()
            return
        # ---------------------------------------
        # Проверим заполнено ли поле
        if self.lineEdit.text() == '':
            self.Window_message = Window_message()
            self.Window_message.label.setText('Имя пользователя обязательно к заполнению!')
            self.Window_message.show()
            return
        # -------------
        # Прочитаем конфигурацию
        try:
            file_address = os.getcwd() + '\\wg_pre_config.conf'
            f_conf = open(file_address, 'r', encoding="utf-8")
            split_result = str(f_conf.readline()).split(':')
            server_ip = cryptocode.decrypt(split_result[0], password_crypto_key)
            server_login = cryptocode.decrypt(split_result[1], password_crypto_key)
            server_password = cryptocode.decrypt(split_result[2], password_crypto_key)
            server_port = split_result[3]
            f_conf.close()
            write_log('Конфигурационный файл перед подготовкой формирования конфига клиента прочитан успешно.')
        except:
            write_log(
                'Ошибка чтения конфигурационного файла wg_pre_config.conf перед подготовкой генерации конфига клиента. Возможно его нет')
            self.Window_message = Window_message()
            self.Window_message.label.setText('Предварительная конфигурация не настроена.')
            self.Window_message.show()
            return

        username = str(self.lineEdit.text())
        # ------------------------------------
        # Определим существование пользователя и включим его
        try:
            result = ssh_connect(server_ip, server_login, server_password, server_port,'/interface/wireguard/peers print from=[find comment=' + username + ']')
            result_index = result.find(username)
            if result_index != -1:
                ssh_connect(server_ip, server_login, server_password, server_port,'/interface/wireguard/peers enable [find comment=' + username + ']')
                write_log('WG Пользователь ' + username + ' включен успешно.')
                self.Window_message = Window_message()
                self.Window_message.label.setText('Пользователь ' + username + ' включен успешно.')
                self.Window_message.show()
            else:
                write_log('WG Пользователь ' + username + ' не существует на сервере.' + server_ip)
                self.Window_message = Window_message()
                self.Window_message.label.setText('Пользователь ' + username + ' не существует на сервере.')
                self.Window_message.show()
        except:
            write_log('Ошибка включения пользователя. Что то пошло не так.')
            self.Window_message = Window_message()
            self.Window_message.label.setText('Ошибка включения пользователя. Проверьте настройки.')
            self.Window_message.show()

    def wg_disable_user(self):
        # ---------------------------------------
        # Проверим лицензию
        if check_license() == 1:
            self.Window_message = Window_message()
            self.Window_message.label.setText('Ошибка чтения файла с лицензией. Обратитесь к разработчику.')
            self.Window_message.show()
            return
        elif check_license() == 2:
            self.Window_message = Window_message()
            self.Window_message.label.setText('Срок лицензии истёк. Обратитесь к разработчику.')
            self.Window_message.show()
            return
        # ---------------------------------------
        # Проверим заполнено ли поле
        if self.lineEdit.text() == '':
            self.Window_message = Window_message()
            self.Window_message.label.setText('Имя пользователя обязательно к заполнению!')
            self.Window_message.show()
            return
        # -------------
        # Прочитаем конфигурацию
        try:
            file_address = os.getcwd() + '\\wg_pre_config.conf'
            f_conf = open(file_address, 'r', encoding="utf-8")
            split_result = str(f_conf.readline()).split(':')
            server_ip = cryptocode.decrypt(split_result[0], password_crypto_key)
            server_login = cryptocode.decrypt(split_result[1], password_crypto_key)
            server_password = cryptocode.decrypt(split_result[2], password_crypto_key)
            server_port = split_result[3]
            f_conf.close()
            write_log('Конфигурационный файл перед подготовкой формирования конфига клиента прочитан успешно.')
        except:
            write_log('Ошибка чтения конфигурационного файла wg_pre_config.conf перед подготовкой генерации конфига клиента. Возможно его нет')
            self.Window_message = Window_message()
            self.Window_message.label.setText('Предварительная конфигурация не настроена.')
            self.Window_message.show()
            return

        username = str(self.lineEdit.text())
        # ------------------------------------
        # Определим существование пользователя и отключим его
        try:
            result = ssh_connect(server_ip, server_login, server_password, server_port,'/interface/wireguard/peers print from=[find comment=' + username + ']')
            result_index = result.find(username)
            if result_index != -1:
                ssh_connect(server_ip, server_login, server_password, server_port,'/interface/wireguard/peers disable [find comment=' + username + ']')
                write_log('WG Пользователь ' + username + ' отключен успешно.')
                self.Window_message = Window_message()
                self.Window_message.label.setText('Пользователь ' + username + ' отключен успешно.')
                self.Window_message.show()
            else:
                write_log('WG Пользователь ' + username + ' не существует на сервере.' + server_ip)
                self.Window_message = Window_message()
                self.Window_message.label.setText('Пользователь ' + username + ' не существует на сервере.')
                self.Window_message.show()
        except:
            write_log('Ошибка отключения пользователя. Что то пошло не так.')
            self.Window_message = Window_message()
            self.Window_message.label.setText('Ошибка отключения пользователя. Проверьте настройки.')
            self.Window_message.show()

    def open_folder_config(self):
        file_address = os.getcwd() + '\\vpn\\wg\\'
        os.system(r'explorer.exe ' + file_address)

    def goto_window_config(self):
        self.close()
        self.Window_config = Window_config()
        self.Window_config.show()

    def goto_window_help(self):
        #self.close()
        self.Window_help = Window_help()
        self.Window_help.show()

    def wg_get_users(self):
        # ---------------------------------------
        # Проверим лицензию
        if check_license() == 1:
            self.Window_message = Window_message()
            self.Window_message.label.setText('Ошибка чтения файла с лицензией. Обратитесь к разработчику.')
            self.Window_message.show()
            return
        elif check_license() == 2:
            self.Window_message = Window_message()
            self.Window_message.label.setText('Срок лицензии истёк. Обратитесь к разработчику.')
            self.Window_message.show()
            return
        # Прочитаем конфигурацию
        try:
            file_address = os.getcwd() + '\\wg_pre_config.conf'
            f_conf = open(file_address, 'r', encoding="utf-8")
            split_result = str(f_conf.readline()).split(':')
            server_ip = cryptocode.decrypt(split_result[0], password_crypto_key)
            server_login = cryptocode.decrypt(split_result[1], password_crypto_key)
            server_password = cryptocode.decrypt(split_result[2], password_crypto_key)
            server_port = split_result[3]
            f_conf.close()
            write_log('Конфигурационный файл перед подготовкой формирования конфига клиента прочитан успешно.')
        except:
            write_log('Ошибка чтения конфигурационного файла wg_pre_config.conf перед подготовкой генерации конфига клиента. Возможно его нет')
            self.Window_message = Window_message()
            self.Window_message.label.setText('Предварительная конфигурация не настроена.')
            self.Window_message.show()
            return

        # Получим данные имён пользователей
        try:
            text = ssh_connect(server_ip, server_login, server_password, server_port,'/interface/wireguard/peers/print proplist=comment,current-endpoint-address,last-handshake')
            split_text_result = text.split('\\r\\n')
        except:
            write_log('Ошибка получения данных от сервера')
            return


        file_address = os.getcwd() + '\\vpn\\users.txt'

        # ------------------------------------
        # Сформируем отчёт
        try:
            f_conf = open(file_address, 'w+', encoding="utf-8")
            i = 1
            while i < len(split_text_result):
                f_conf.write(split_text_result[i]+'\n')
                i += 1
            f_conf.close()
            write_log('Отчёт сформирован')
            self.Window_message = Window_message()
            self.Window_message.label.setText('Файл со списком пользователей сформирован.')
            self.Window_message.show()
        except:
            write_log('Ошибка записи в файл users')
            return

    def open_folder_users_excel(self):
        file_address = os.getcwd() + '\\vpn\\'
        os.system(r'explorer.exe ' + file_address)

    def exit(self):
        raise SystemExit(0)

class Window_config(QtWidgets.QMainWindow, config.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # 
        self.pushButton.clicked.connect(self.goto_window_main)
        self.pushButton_2.clicked.connect(self.save_config_to_file)

        # ---------------------------------------
        # Прочитаем конфигурацию, если она существует
        try:
            file_address = os.getcwd() + '\\wg_pre_config.conf'
            f_conf = open(file_address, 'r', encoding="utf-8")
            split_result = str(f_conf.readline()).split(':')
            server_ip = cryptocode.decrypt(split_result[0], password_crypto_key)
            server_login = cryptocode.decrypt(split_result[1], password_crypto_key)
            server_password = cryptocode.decrypt(split_result[2], password_crypto_key)
            server_port = split_result[3]
            wg_ip = split_result[4]
            wg_port = split_result[5]
            wg_pool_ip_start = split_result[6]
            wg_pool_ip_end = split_result[7]
            wg_interface_name_server = split_result[8]
            wg_server_ip_into_vpn = split_result[9]
            wg_dns = split_result[10]
            wg_routers = split_result[11]
            f_conf.close()
            write_log('Конфигурационный файл прочитан успешно.')
        except:
            write_log('Ошибка чтения конфигурационного файла wg_pre_config.conf. Возможно его нет')
            return
        # ---------------------------------------
        # Разместим на форме полученные данные
        try:
            self.lineEdit_11.setText(server_ip)
            self.lineEdit.setText(server_login)
            self.lineEdit_2.setText(server_password)
            self.lineEdit_3.setText(server_port)
            self.lineEdit_4.setText(wg_ip)
            self.lineEdit_6.setText(wg_port)
            self.lineEdit_7.setText(wg_pool_ip_start)
            self.lineEdit_10.setText(wg_pool_ip_end)
            self.lineEdit_14.setText(wg_interface_name_server)
            self.lineEdit_8.setText(wg_server_ip_into_vpn)
            self.lineEdit_5.setText(wg_dns)
            self.lineEdit_9.setText(wg_routers)
            write_log('Данные из конфигурационного файла размещены на форме успешно.')
        except:
            write_log('Ошибка размещения данных из конфигурационного файла на форме')
            return

    def goto_window_main(self):
        self.close()
        self.Window_main = Window_main()
        self.Window_main.show()

    def save_config_to_file(self):

        # ---------------------------------------
        # Проверим корректность ввода IP
        try:
            def check_ip(ip):
                split_result = ip.split('.')
                if int(split_result[0]) > 254 or int(split_result[0]) < 0 or int(split_result[1]) > 254 or int(
                        split_result[1]) < 0 or int(split_result[2]) > 254 or int(split_result[2]) < 0 or int(
                    split_result[3]) > 254 or int(split_result[3]) < 0:
                    return 1
                else:
                    return 0

            if check_ip(self.lineEdit_11.text()) == 1 or check_ip(self.lineEdit_4.text()) == 1 or check_ip(
                    self.lineEdit_7.text()) == 1 or check_ip(self.lineEdit_10.text()) == 1 or check_ip(
                self.lineEdit_8.text()) == 1:
                write_log('Неверный формат записи IP адреса.')
                self.Window_message = Window_message()
                self.Window_message.label.setText('Неверный формат записи IP адреса.')
                self.Window_message.show()
                return
        except:
            write_log('Ошибка проверки корректности IP адресов. Возможно они не заполнены.')

        server_ip = cryptocode.encrypt(str(self.lineEdit_11.text()), password_crypto_key)
        server_login = cryptocode.encrypt(str(self.lineEdit.text()), password_crypto_key)
        server_password = cryptocode.encrypt(str(self.lineEdit_2.text()), password_crypto_key)
        server_port = str(self.lineEdit_3.text())
        wg_ip = str(self.lineEdit_4.text())
        wg_port = str(self.lineEdit_6.text())
        wg_pool_ip_start = str(self.lineEdit_7.text())
        wg_pool_ip_end = str(self.lineEdit_10.text())
        wg_interface_name_server = str(self.lineEdit_14.text())
        wg_server_ip_into_vpn = str(self.lineEdit_8.text())
        wg_dns = str(self.lineEdit_5.text())
        wg_routers = str(self.lineEdit_9.text())

        # ---------------------------------------
        # Проверим заполнены ли поля
        if server_ip == '' or server_login == '' or server_port == '' or server_password == '' or server_port == '' or wg_ip == '' or wg_port == '' or wg_pool_ip_start == '' or wg_pool_ip_end == '' or wg_interface_name_server == '' or wg_server_ip_into_vpn == '' or wg_dns == '' or wg_routers == '':
            self.Window_message = Window_message()
            self.Window_message.label.setText('Заполнить нужно все поля!')
            self.Window_message.show()
            return

        # ---------------------------------------
        # Сформируем конфигурационный файл конфигурации
        try:
            file_address = os.getcwd() + '\\wg_pre_config.conf'
            f_conf = open(file_address, 'w+', encoding="utf-8")
            f_conf.write(server_ip + ':' + server_login + ':' + server_password + ':' + server_port + ':' + wg_ip + ':' + wg_port + ':' + wg_pool_ip_start + ':' + wg_pool_ip_end + ':' + wg_interface_name_server + ':' + wg_server_ip_into_vpn + ':' + wg_dns + ':' + wg_routers)
            f_conf.close()
            write_log('Конфигурационный файл для настроек сохранён успешно.')
            self.Window_message = Window_message()
            self.Window_message.label.setText('Успешно сохранено.')
            self.Window_message.show()
        except:
            write_log('Конфигурационный файл для настроек ошибка сохранения.')
            self.Window_message = Window_message()
            self.Window_message.label.setText('Ошибка. Возможно нет прав доступа.')
            self.Window_message.show()
            return

class Window_message(QtWidgets.QMainWindow, message.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # 
        self.pushButton.clicked.connect(self.ok)

    def ok (self):
        self.close()

class Window_help(QtWidgets.QMainWindow, help.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # 
        self.pushButton_1.clicked.connect(self.close_window)

    def close_window(self):
        self.close()


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = Window_main()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec()

