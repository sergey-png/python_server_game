from threading import *
from time import time, sleep
import socket
import sys, os
from admin_ui import *
from PyQt5 import QtCore, QtGui, QtWidgets
import re


class MyWin(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.time_setup = time()
        self.stop_timer = 0
        self.timer_min = 0  # Timer
        self.timer_sec = 0  # Timer
        self.current_task = 1  # Current task for students
        # Здесь прописываем событие нажатия на кнопку
        self.ui.button_1.clicked.connect(self.connect_to_server)
        self.ui.button_4.clicked.connect(self.button_add_team)
        self.ui.button_3.clicked.connect(self.button_3)
        self.ui.button_13.clicked.connect(self.button_13)
        self.ui.button_5.clicked.connect(self.button_5)
        self.ui.button_6.clicked.connect(self.button_6)
        self.ui.button_7.clicked.connect(self.init_task)
        self.ui.button_8.clicked.connect(self.open_tasks_pdf)
        # --------------------------------------------------------
        self.ui.button_11.clicked.connect(self.team_spectating_1)
        self.ui.button_12.clicked.connect(self.back_to_edit_server)
        self.ui.button_17.clicked.connect(self.back_to_edit_server)
        self.ui.button_18.clicked.connect(self.back_to_edit_server)
        self.ui.button_21.clicked.connect(self.back_to_edit_server)
        self.ui.button_24.clicked.connect(self.back_to_edit_server)
        self.ui.button_27.clicked.connect(self.back_to_edit_server)
        self.ui.button_14.clicked.connect(self.team_spectating_2)
        self.ui.button_15.clicked.connect(self.team_spectating_1)
        self.ui.button_16.clicked.connect(self.team_spectating_3)
        self.ui.button_19.clicked.connect(self.team_spectating_2)
        self.ui.button_20.clicked.connect(self.team_spectating_4)
        self.ui.button_22.clicked.connect(self.team_spectating_3)
        self.ui.button_23.clicked.connect(self.team_spectating_5)
        self.ui.button_25.clicked.connect(self.team_spectating_4)
        self.ui.button_26.clicked.connect(self.team_spectating_6)
        self.ui.button_28.clicked.connect(self.team_spectating_5)
        # --------------------------------------------------------
        self.ui.button_9.clicked.connect(self.start_competition)
        self.ui.button_10.clicked.connect(self.stop_competition)

    # Функции которые выполняются при нажатии на кнопки

    # BUTTON 1 - Sign in to server
    def connect_to_server(self):
        con = server_online_check()
        if con == 0:
            try:
                connect()
            except ConnectionRefusedError:
                print("Не удалось подключиться")
                QtWidgets.QMessageBox.critical(self, "Error", "Connection Refused Error")
                return 0
        con = server_online_check()
        if con == 1:
            try:
                client.send("admin_rights_permission_3223".encode("utf-8"))
                self.ui.window.setCurrentIndex(1)
                sleep(1)
                self.update_b29()
                print("Ok")
            except:
                QtWidgets.QMessageBox.critical(self, "Error", "Не получилось подключиться к консоли")
            finally:
                return 0

    # BUTTON 4 - Add new team
    def button_add_team(self):
        # ########################### АНТИ-СПАМ ############################
        global x_start
        # print(f"\n delay is = {x_start - self.time_setup}\n")
        if x_start - self.time_setup <= 0.9:
            QtWidgets.QMessageBox.critical(self, "Error", "Интервал нажатия на кнопку слишком быстрый")
            return -1
        else:
            self.time_setup = x_start
        # ########################### АНТИ-СПАМ ############################
        con = server_online_check()
        if con != 0:
            text = self.ui.lineEdit.text()
            self.ui.lineEdit.setText('')
            if re.search(r'[^a-z A-Z0-9]', text):
                QtWidgets.QMessageBox.critical(self, "Error", "Используйте латинские буквы в названии команды")
                return -1
            elif text == "":
                QtWidgets.QMessageBox.critical(self, "Error", "Пустое имя для команды")
                return -1
            else:
                data = "admin_b4|" + text
                try:
                    client.send(data.encode("utf-8"))
                except:
                    QtWidgets.QMessageBox.critical(self, "Error", "Не получилось отправить данные на сервер")
                    return -1

    # BUTTON 3 - Back to main menu
    def button_3(self):
        self.ui.window.setCurrentIndex(0)

    # ONLY Updates list of teams
    def update_b29(self):
        con = server_online_check()
        if con != 0:
            data = "b29|"
            try:
                client.send(data.encode("utf-8"))
                return 1
            except:
                QtWidgets.QMessageBox.critical(self, "Error", "Не получилось обновить данные с сервера")

    # BUTTON 13 - Delete selected team
    def button_13(self):
        # ########################### АНТИ-СПАМ ############################
        global x_start
        # print(f"\n delay is = {x_start - self.time_setup}\n")
        if x_start - self.time_setup <= 0.9:
            QtWidgets.QMessageBox.critical(self, "Error", "Интервал нажатия на кнопку слишком быстрый")
            return -1
        else:
            self.time_setup = x_start
        # ########################### АНТИ-СПАМ ############################
        row = self.ui.listWidget.currentRow()
        if row == -1:
            QtWidgets.QMessageBox.critical(self, "Error", "Сначала выберите команду для удаления")
            return -1
        con = server_online_check()
        if con != 0:
            data = "admin_b13|" + str(row)
            try:
                client.send(data.encode("utf-8"))
                return 1
            except:
                QtWidgets.QMessageBox.critical(self, "Error", "Не получилось удалить команду")

    # BUTTON 5 - Change team capacity
    def button_5(self):
        # ########################### АНТИ-СПАМ ############################
        global x_start
        # print(f"\n delay is = {x_start - self.time_setup}\n")
        if x_start - self.time_setup <= 0.9:
            QtWidgets.QMessageBox.critical(self, "Error", "Интервал нажатия на кнопку слишком быстрый")
            return -1
        else:
            self.time_setup = x_start
        # ########################### АНТИ-СПАМ ############################

        con = server_online_check()
        if con != 0:
            text = self.ui.lineEdit_2.text()
            if re.search(r'[^0-9]', text):
                QtWidgets.QMessageBox.critical(self, "Error", "Вводится только целое число")
                return -1
            elif text == "":
                QtWidgets.QMessageBox.critical(self, "Error", "Пустой ввод")
                return -1
            else:
                data = "admin_b5|" + text
                client.send(data.encode("utf-8"))
                return 1

    # BUTTON 6 - CHANGE TIMER
    def button_6(self):
        # ########################### АНТИ-СПАМ ############################
        global x_start
        # print(f"\n delay is = {x_start - self.time_setup}\n")
        if x_start - self.time_setup <= 0.9:
            QtWidgets.QMessageBox.critical(self, "Error", "Интервал нажатия на кнопку слишком быстрый")
            return -1
        else:
            self.time_setup = x_start
        # ########################### АНТИ-СПАМ ############################
        con = server_online_check()
        if con != 0:
            text = self.ui.lineEdit_3.text()
            if re.search(r'[^0-9]', text):
                QtWidgets.QMessageBox.critical(self, "Error", "Вводится только целое число")
                return -1
            elif text == "":
                QtWidgets.QMessageBox.critical(self, "Error", "Пустой ввод")
                return -1
            else:
                text = int(text)
                text *= 60
                data = "admin_b6|" + str(text)
                client.send(data.encode("utf-8"))

    # Простая функция, отображающая введенное админом время на таймере
    def init_timer(self):
        self.ui.timer_min.display(self.timer_min)
        self.ui.timer_sec.display(self.timer_sec)

    # Функция записи текущего номера задания
    def init_task(self):
        # ########################### АНТИ-СПАМ ############################
        global x_start
        # print(f"\n delay is = {x_start - self.time_setup}\n")
        if x_start - self.time_setup <= 0.9:
            QtWidgets.QMessageBox.critical(self, "Error", "Интервал нажатия на кнопку слишком быстрый")
            return -1
        else:
            self.time_setup = x_start
        # ########################### АНТИ-СПАМ ############################
        con = server_online_check()
        if con != 0:
            text = self.ui.lineEdit_4.text()
            if re.search(r'[^0-9]', text):
                QtWidgets.QMessageBox.critical(self, "Error", "Вводится только целое число")
                return -1
            elif text == "":
                QtWidgets.QMessageBox.critical(self, "Error", "Пустой ввод")
                return -1
            else:
                data = "admin_b7|" + str(text)
                client.send(data.encode("utf-8"))

    # Простая функция для обновления текущего номера задания на экране
    def change_current_task(self):
        self.ui.label_10.setText(str(self.current_task))
        return 1

    # Функция открытия PDF файла с задачами
    def open_tasks_pdf(self):
        # ########################### АНТИ-СПАМ ############################
        global x_start
        # print(f"\n delay is = {x_start - self.time_setup}\n")
        if x_start - self.time_setup <= 0.9:
            QtWidgets.QMessageBox.critical(self, "Error", "Интервал нажатия на кнопку слишком быстрый")
            return -1
        else:
            self.time_setup = x_start
        # ########################### АНТИ-СПАМ ############################
        os.startfile("Tasks.pdf")
        return 0

    # ------------------------------------------------------------------------------------------------------------
    def team_spectating_1(self):
        teams_count = self.ui.listWidget.count()
        if teams_count == 0:
            QtWidgets.QMessageBox.critical(self, "Error", "Нет команд")
        else:
            self.ui.window.setCurrentIndex(2)

    def back_to_edit_server(self):
        self.ui.window.setCurrentIndex(1)

    def team_spectating_2(self):
        teams_count = self.ui.listWidget.count()
        if teams_count < 2:
            QtWidgets.QMessageBox.critical(self, "Error", f"Всего 1 команда")
        else:
            self.ui.window.setCurrentIndex(3)

    def team_spectating_3(self):
        teams_count = self.ui.listWidget.count()
        if teams_count < 3:
            QtWidgets.QMessageBox.critical(self, "Error", f"Всего 2 команды")
        else:
            self.ui.window.setCurrentIndex(4)

    def team_spectating_4(self):
        teams_count = self.ui.listWidget.count()
        if teams_count < 4:
            QtWidgets.QMessageBox.critical(self, "Error", f"Всего 3 команды")
        else:
            self.ui.window.setCurrentIndex(5)

    def team_spectating_5(self):
        teams_count = self.ui.listWidget.count()
        if teams_count < 5:
            QtWidgets.QMessageBox.critical(self, "Error", f"Всего 4 команды")
        else:
            self.ui.window.setCurrentIndex(6)

    def team_spectating_6(self):
        teams_count = self.ui.listWidget.count()
        if teams_count < 6:
            QtWidgets.QMessageBox.critical(self, "Error", f"Всего 5 команд")
        else:
            self.ui.window.setCurrentIndex(7)

    # ------------------------------------------------------------------------------------------------------------

    def start_competition(self):
        # ########################### АНТИ-СПАМ ############################
        global x_start
        # print(f"\n delay is = {x_start - self.time_setup}\n")
        if x_start - self.time_setup <= 0.9:
            QtWidgets.QMessageBox.critical(self, "Error", "Интервал нажатия на кнопку слишком быстрый")
            return -1
        else:
            self.time_setup = x_start
        # ########################### АНТИ-СПАМ ############################
        con = server_online_check()
        if con != 0:
            data = "admin_starts|"
            client.send(data.encode("utf-8"))
            self.stop_timer = 0
            started_timer()
            self.ui.label_12.setText("ONLINE")

    def stop_competition(self):
        self.ui.tableWidget.setRowCount(0)
        self.ui.tableWidget_2.setRowCount(0)
        self.ui.tableWidget_3.setRowCount(0)
        self.ui.tableWidget_4.setRowCount(0)
        self.ui.tableWidget_5.setRowCount(0)
        self.ui.tableWidget_6.setRowCount(0)
        self.ui.label_26.setText("...")
        self.ui.label_27.setText("...")
        self.ui.label_28.setText("...")
        self.ui.label_29.setText("...")
        self.ui.label_30.setText("...")
        self.ui.label_31.setText("...")
        self.ui.label_12.setText("OFFLINE")
        data = "STOP_RESET"
        client.send(data.encode("utf-8"))


# Проверка на то, что сервер отвечает (вызывается только один раз при вызове функции)
def server_online_check():
    try:
        client.send("".encode("utf-8"))
        # print("Connection established!")
        return 1
    except OSError:
        # print("Where IP?")
        return 0


# Функция работает как ТРЕД и принимает сообщения от сервера каждую секунду
def server_receive_msg():
    global client
    while True:
        try:
            data = client.recv(4096)
            data = data.decode("utf-8")
            distributor(data)
        except OSError:
            print("No data")
        finally:
            sleep(1)


# Распеределитель (работает в треде отдельно)
def distributor(data):
    print(data)

    # BUTTON 4
    if data.find("admin_b4|0") != -1:
        print("No more to add new team")
        return -1

    # BUTTON 29 teams update
    elif data.find("b29|") != -1:
        print("Ready to update list")
        listed = list(data.split("|"))
        listed.remove('')
        listed.remove('b29')
        my_app.ui.listWidget.clear()
        i = 1
        for names in listed:
            my_app.ui.listWidget.addItem(names)
            if i == 1:
                my_app.ui.label_15.setText(names)
            elif i == 2:
                my_app.ui.label_16.setText(names)
            elif i == 3:
                my_app.ui.label_18.setText(names)
            elif i == 4:
                my_app.ui.label_20.setText(names)
            elif i == 5:
                my_app.ui.label_22.setText(names)
            elif i == 6:
                my_app.ui.label_24.setText(names)
            i += 1

    # TIMER CHANGE INFO UPDATE
    elif data.find("button_6admin|") != -1:
        timer = int(data[data.find("|") + 1:])
        my_app.timer_min = timer // 60
        my_app.timer_sec = timer - my_app.timer_min * 60
        my_app.init_timer()
    # Update current task value
    elif data.find("admin_b7_update|") != -1:
        my_app.current_task = int(data[data.find("|") + 1:])
        my_app.change_current_task()

    elif data.find("result_final") != -1:
        listed = list(data.split("|"))
        listed.remove('result_final')
        print(listed)
        # curr turn | name | stroke index | text | team number
        if listed[4] == "1":
            my_app.ui.tableWidget.insertRow(int(listed[0]))
            my_app.ui.tableWidget.setItem(int(listed[0]), 0, QtWidgets.QTableWidgetItem(str(int(listed[0]) + 1)))
            my_app.ui.tableWidget.setItem(int(listed[0]), 1, QtWidgets.QTableWidgetItem(listed[1]))
            times = str(my_app.timer_min) + ":" + str(my_app.timer_sec)
            my_app.ui.tableWidget.setItem(int(listed[0]), 2, QtWidgets.QTableWidgetItem(times))
            my_app.ui.tableWidget.setItem(int(listed[0]), 3, QtWidgets.QTableWidgetItem(listed[2]))
            my_app.ui.tableWidget.setItem(int(listed[0]), 4, QtWidgets.QTableWidgetItem(listed[3]))
        if listed[4] == "2":
            my_app.ui.tableWidget_2.insertRow(int(listed[0]))
            my_app.ui.tableWidget_2.setItem(int(listed[0]), 0, QtWidgets.QTableWidgetItem(str(int(listed[0]) + 1)))
            my_app.ui.tableWidget_2.setItem(int(listed[0]), 1, QtWidgets.QTableWidgetItem(listed[1]))
            times = str(my_app.timer_min) + ":" + str(my_app.timer_sec)
            my_app.ui.tableWidget_2.setItem(int(listed[0]), 2, QtWidgets.QTableWidgetItem(times))
            my_app.ui.tableWidget_2.setItem(int(listed[0]), 3, QtWidgets.QTableWidgetItem(listed[2]))
            my_app.ui.tableWidget_2.setItem(int(listed[0]), 4, QtWidgets.QTableWidgetItem(listed[3]))
        if listed[4] == "3":
            my_app.ui.tableWidget_3.insertRow(int(listed[0]))
            my_app.ui.tableWidget_3.setItem(int(listed[0]), 0, QtWidgets.QTableWidgetItem(str(int(listed[0]) + 1)))
            my_app.ui.tableWidget_3.setItem(int(listed[0]), 1, QtWidgets.QTableWidgetItem(listed[1]))
            times = str(my_app.timer_min) + ":" + str(my_app.timer_sec)
            my_app.ui.tableWidget_3.setItem(int(listed[0]), 2, QtWidgets.QTableWidgetItem(times))
            my_app.ui.tableWidget_3.setItem(int(listed[0]), 3, QtWidgets.QTableWidgetItem(listed[2]))
            my_app.ui.tableWidget_3.setItem(int(listed[0]), 4, QtWidgets.QTableWidgetItem(listed[3]))
        if listed[4] == "4":
            my_app.ui.tableWidget_4.insertRow(int(listed[0]))
            my_app.ui.tableWidget_4.setItem(int(listed[0]), 0, QtWidgets.QTableWidgetItem(str(int(listed[0]) + 1)))
            my_app.ui.tableWidget_4.setItem(int(listed[0]), 1, QtWidgets.QTableWidgetItem(listed[1]))
            times = str(my_app.timer_min) + ":" + str(my_app.timer_sec)
            my_app.ui.tableWidget_4.setItem(int(listed[0]), 2, QtWidgets.QTableWidgetItem(times))
            my_app.ui.tableWidget_4.setItem(int(listed[0]), 3, QtWidgets.QTableWidgetItem(listed[2]))
            my_app.ui.tableWidget_4.setItem(int(listed[0]), 4, QtWidgets.QTableWidgetItem(listed[3]))
        if listed[4] == "5":
            my_app.ui.tableWidget_5.insertRow(int(listed[0]))
            my_app.ui.tableWidget_5.setItem(int(listed[0]), 0, QtWidgets.QTableWidgetItem(str(int(listed[0]) + 1)))
            my_app.ui.tableWidget_5.setItem(int(listed[0]), 1, QtWidgets.QTableWidgetItem(listed[1]))
            times = str(my_app.timer_min) + ":" + str(my_app.timer_sec)
            my_app.ui.tableWidget_5.setItem(int(listed[0]), 2, QtWidgets.QTableWidgetItem(times))
            my_app.ui.tableWidget_5.setItem(int(listed[0]), 3, QtWidgets.QTableWidgetItem(listed[2]))
            my_app.ui.tableWidget_5.setItem(int(listed[0]), 4, QtWidgets.QTableWidgetItem(listed[3]))
        if listed[4] == "6":
            my_app.ui.tableWidget_6.insertRow(int(listed[0]))
            my_app.ui.tableWidget_6.setItem(int(listed[0]), 0, QtWidgets.QTableWidgetItem(str(int(listed[0]) + 1)))
            my_app.ui.tableWidget_6.setItem(int(listed[0]), 1, QtWidgets.QTableWidgetItem(listed[1]))
            times = str(my_app.timer_min) + ":" + str(my_app.timer_sec)
            my_app.ui.tableWidget_6.setItem(int(listed[0]), 2, QtWidgets.QTableWidgetItem(times))
            my_app.ui.tableWidget_6.setItem(int(listed[0]), 3, QtWidgets.QTableWidgetItem(listed[2]))
            my_app.ui.tableWidget_6.setItem(int(listed[0]), 4, QtWidgets.QTableWidgetItem(listed[3]))

    elif data.find("pushbutton3|") != -1:
        listed = list(data.split("|"))
        listed.remove('pushbutton3')
        print(f" LIST = {listed}")
        if listed[2] == "1":
            my_app.ui.label_26.setText(f"Тестов: {listed[0]} из {listed[1]}")
        elif listed[2] == "2":
            my_app.ui.label_27.setText(f"Тестов: {listed[0]} из {listed[1]}")
        elif listed[2] == "3":
            my_app.ui.label_28.setText(f"Тестов: {listed[0]} из {listed[1]}")
        elif listed[2] == "4":
            my_app.ui.label_29.setText(f"Тестов: {listed[0]} из {listed[1]}")
        elif listed[2] == "5":
            my_app.ui.label_30.setText(f"Тестов: {listed[0]} из {listed[1]}")
        elif listed[2] == "6":
            my_app.ui.label_31.setText(f"Тестов: {listed[0]} из {listed[1]}")

    elif data.find("STOP_RESET") != -1:
        my_app.stop_timer = 1


# Функция работает как ТРЕД и чекает подключение к серверу каждые 6 секунд
def server_check():
    while True:
        try:
            client.send("check u here".encode("utf-8"))
            # print("Connection established!")
        except OSError:
            # print("Where IP to check connection??")
            if my_app.ui.window.currentIndex() != 0:
                my_app.ui.window.setCurrentIndex(0)
        finally:
            # print("Function complete!")
            sleep(5)


def connect():
    global client
    client = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )
    client.settimeout(15)
    client.connect(("127.0.0.1", 9669))


client = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)
connection = 0

# ------------------------ THREAD ----------------------------


x_start = time()


def time_delay():
    global x_start
    while True:
        sleep(1)
        x_start = time()


# ------------------------ THREAD ----------------------------

def started_timer():
    print("I Am here")
    t4 = Thread(target=started_timer2)
    t4.daemon = True
    t4.start()


def started_timer2():
    seconds = my_app.timer_min * 60 + my_app.timer_sec
    while seconds > 0:
        if my_app.stop_timer == 1:
            my_app.stop_timer = 0
            return 0
        if my_app.timer_sec == 0:
            my_app.timer_min -= 1
            my_app.timer_sec = 59
        else:
            my_app.timer_sec -= 1
        # print(f"Current time - {my_app.timer_min}:{my_app.timer_sec}")
        my_app.init_timer()
        seconds -= 1
        sleep(1)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    my_app = MyWin()
    my_app.show()

    t1 = Thread(target=server_check)
    t2 = Thread(target=server_receive_msg)
    t3 = Thread(target=time_delay)

    t1.daemon = True
    t2.daemon = True
    t3.daemon = True
    t1.start()
    t2.start()
    t3.start()

    sys.exit(app.exec_())
