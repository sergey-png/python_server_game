from threading import *
from time import time, sleep
import socket
import sys, os, subprocess
from client_ui import *
from PyQt5 import QtCore, QtGui, QtWidgets
import re


class MyWin(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_mainWindow()
        self.ui.setupUi(self)
        self.time_setup = time()
        self.timer_min = 0  # Timer
        self.timer_sec = 0  # Timer
        self.current_task = 1
        self.program_text = [""] * 14
        self.index_of_stroke = 0
        self.stop_timer = 0
        self.path = os.getcwd()

        # Здесь прописываем событие нажатия на кнопку
        self.ui.button_1.clicked.connect(self.connect_to_server)
        self.ui.button_4.clicked.connect(self.chose_command)
        self.ui.button_3.clicked.connect(self.button_3)
        self.ui.button_5.clicked.connect(self.button_5)
        self.ui.pushButton.clicked.connect(self.push_button_1)
        self.ui.pushButton_2.clicked.connect(self.push_button_2)
        self.ui.pushButton_3.clicked.connect(self.push_button_3)
        self.ui.pushButton_4.clicked.connect(self.push_button_4)
        self.ui.button_6.clicked.connect(self.button_6)

    # Функции которые выполняются при нажатии на кнопки
    # BUTTON 1 - Sign to server
    def connect_to_server(self):
        con = server_online_check()
        if con == 0:
            try:
                connect()
            except ConnectionRefusedError:
                print("Не удалось подключиться")
                QtWidgets.QMessageBox.critical(self, "Error", "Connection Refused Error")
                return
        con = server_online_check()
        if con == 1:
            self.ui.window.setCurrentIndex(1)
            sleep(1)
            self.button_7()
            return

    # BUTTON 4 - Записаться в команду
    def chose_command(self):
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
            row = str(self.ui.listWidget.currentRow())

            if re.search(r'[^a-z A-Z]', text):
                QtWidgets.QMessageBox.critical(self, "Error", "Используйте латинские буквы при вводе ФИО")
            elif text == "":
                QtWidgets.QMessageBox.critical(self, "Error", "Сначала введите свои данные")
            elif row == "-1":
                QtWidgets.QMessageBox.critical(self, "Error", "Теперь выберите команду")
            else:
                data = "button4|" + text + "|" + row
                print("____________________________")
                print(data)
                print("____________________________")
                try:
                    client.send(data.encode("utf-8"))
                    return 1
                except:
                    QtWidgets.QMessageBox.critical(self, "Error", "Не получилось отправить данные на сервер")

    # BUTTON 3 - Back to Main Window
    def button_3(self):
        self.ui.window.setCurrentIndex(0)

    # ONLY Updates list of teams on clicked Play Button
    def button_7(self):
        con = server_online_check()
        if con != 0:
            data = "b29|"
            try:
                client.send(data.encode("utf-8"))
                sleep(0.2)
                return 1
            except:
                QtWidgets.QMessageBox.critical(self, "Error", "Не получилось обновить данные с сервера")

    # After server send "True" message to register in team, this func allows to Update names in team list in w8ing lobby
    def button_4_continue(self):
        con = server_online_check()
        if con != 0:
            data = "b4con"
            try:
                client.send(data.encode("utf-8"))
                sleep(0.2)
                return 1
            except:
                QtWidgets.QMessageBox.critical(self, "Error", "Не получилось обновить данные с сервера")

    # Leave team and update info in team users list
    def button_5(self):
        self.ui.window.setCurrentIndex(1)
        con = server_online_check()
        if con != 0:
            data = "button5c|"
            try:
                client.send(data.encode("utf-8"))
                sleep(0.2)
                return 1
            except:
                QtWidgets.QMessageBox.critical(self, "Error", "Не получилось обновить данные с сервера")

    # Простая функция, отображающая введенное админом время на таймере
    def init_timer(self):
        self.ui.timer_min.display(self.timer_min)
        self.ui.timer_sec.display(self.timer_sec)

    def change_current_task(self):
        self.ui.label_27.setText(str(self.current_task))
        return 1

    def started_competition(self):
        os.chdir("tasks")
        os.startfile(f"task_{self.current_task}.PNG")
        os.chdir(self.path)
        self.stop_timer = 0
        started_timer()

    # ЗАПИСЬ НОВОЙ СТРОКИ
    def push_button_1(self):
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
            if self.index_of_stroke == 14:
                QtWidgets.QMessageBox.critical(self, "Error", "Больше 14 строк записать нельзя!")
                return -1
            text = self.ui.lineEdit_2.text()
            if text == "":
                QtWidgets.QMessageBox.critical(self, "Error", "Пустая строка!")
            data = f"push_button_1|{text}|{self.index_of_stroke}"
            client.send(data.encode("utf-8"))
            self.ui.label_18.setStyleSheet("color: red;")
            self.ui.label_18.setText("Ваш ход: Нет")
            self.ui.pushButton.setEnabled(False)
            self.ui.pushButton_2.setEnabled(False)
            self.ui.pushButton_3.setEnabled(False)
            self.ui.pushButton_4.setEnabled(False)

    def push_button_2(self):
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
            num = self.ui.lineEdit_4.text()
            text = self.ui.lineEdit_3.text()
            if re.search(r'[^0-9]', num):
                QtWidgets.QMessageBox.critical(self, "Error", "Вводится только целое число")
                return -1
            elif num == "" or text == "":
                QtWidgets.QMessageBox.critical(self, "Error", "Пустой ввод")
                return -1
            else:
                num = int(num) - 1
                if num >= self.index_of_stroke:
                    QtWidgets.QMessageBox.critical(self, "Error", "Нельзя изменить несущестующую строку")
                    return -1
                data = f"push_button_2|{text}|{num}"
                client.send(data.encode("utf-8"))
                self.ui.label_18.setStyleSheet("color: red;")
                self.ui.label_18.setText("Ваш ход: Нет")
                self.ui.pushButton.setEnabled(False)
                self.ui.pushButton_2.setEnabled(False)
                self.ui.pushButton_3.setEnabled(False)
                self.ui.pushButton_4.setEnabled(False)

    def push_button_3(self):
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
            os.chdir("tester")
            file = open(f"solution{self.current_task}.py", "w")
            for i in range(len(self.program_text)):
                if self.program_text[i] == "":
                    print("Writing is done")
                    break
                file.write(self.program_text[i] + "\n")
            file.close()
            try:
                subprocess.run(['python', 'tester.py', f'solution{self.current_task}.py', f'task{self.current_task}'])
            except:
                QtWidgets.QMessageBox.critical(self, "Error", "Не получилось проверить программу")
            file = open(f"solution{self.current_task}.py_result.txt", "r")
            results = file.read()
            file.close()
            results = list(results.split("\n"))
            results.remove('')
            os.chdir(self.path)
            # Server send
            data = f"pushbutton3|{int(results[0])}|{int(results[1])}"
            try:
                client.send(data.encode("utf-8"))
            except:
                QtWidgets.QMessageBox.critical(self, "Error", "Не получилось отправить данные на сервер")
            finally:
                return 0

    def push_button_4(self):
        # ########################### АНТИ-СПАМ ############################
        global x_start
        # print(f"\n delay is = {x_start - self.time_setup}\n")
        if x_start - self.time_setup <= 0.9:
            QtWidgets.QMessageBox.critical(self, "Error", "Интервал нажатия на кнопку слишком быстрый")
            return -1
        else:
            self.time_setup = x_start
        # ########################### АНТИ-СПАМ ############################
        os.chdir("tester")
        file = open(f"solution{self.current_task}.py", "w")
        for i in range(len(self.program_text)):
            if self.program_text[i] == "":
                print("Writing is done")
                break
            file.write(self.program_text[i] + "\n")
        file.close()
        try:
            subprocess.run(['python', 'tester.py', f'solution{self.current_task}.py', f'task{self.current_task}'])
        except:
            QtWidgets.QMessageBox.critical(self, "Error", "Не получилось проверить программу")
        file = open(f"solution{self.current_task}.py_result.txt", "r")
        results = file.read()
        file.close()
        results = list(results.split("\n"))
        results.remove('')
        os.chdir(self.path)
        if results[0] == "0":
            QtWidgets.QMessageBox.critical(self, "Error", "Программа не прошла ни одного теста")
        else:
            QtWidgets.QMessageBox.critical(self, "Good", "Можно завершить тестирование")
        return 0

    def button_6(self):
        self.ui.window.setCurrentIndex(2)
        self.timer_min = 0  # Timer
        self.timer_sec = 0  # Timer
        self.current_task = 1
        self.program_text = [""] * 14
        self.index_of_stroke = 0
        self.stop_timer = 0
        self.ui.str_1.setText("")
        self.ui.str_2.setText("")
        self.ui.str_3.setText("")
        self.ui.str_4.setText("")
        self.ui.str_5.setText("")
        self.ui.str_6.setText("")
        self.ui.str_7.setText("")
        self.ui.str_8.setText("")
        self.ui.str_9.setText("")
        self.ui.str_10.setText("")
        self.ui.str_11.setText("")
        self.ui.str_12.setText("")
        self.ui.str_13.setText("")
        self.ui.str_14.setText("")
        return 0


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
    print(f"From server: {data}")

    # BUTTON 4
    if data.find("button4") != -1:
        if data.find("|1") != -1:
            my_app.ui.window.setCurrentIndex(2)
            my_app.button_4_continue()
        else:
            print("Не получилось записаться. Возможно команда заполнена.")
            return 0

    # BUTTON 29
    elif data.find("b29|") != -1:
        print("Ready to update list")
        listed = list(data.split("|"))
        listed.remove('')
        listed.remove('b29')
        my_app.ui.listWidget.clear()
        for names in listed:
            my_app.ui.listWidget.addItem(names)
        return 0

    # BUTTON 4 Continue
    elif data.find("b4con|") != -1:
        print("Ready to update list of users in team")
        listed = list(data.split("|"))
        listed.remove('')
        listed.remove('b4con')
        print(listed)
        my_app.ui.listWidget_2.clear()
        for names in listed:
            print(f"Add item = {names}")
            my_app.ui.listWidget_2.addItem(names)
        return 0

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

    elif data.find("admin_started") != -1:
        if my_app.ui.window.currentIndex() == 2:
            my_app.ui.window.setCurrentIndex(3)
            my_app.started_competition()

    elif data.find("your_turn") != -1:
        my_app.ui.label_18.setStyleSheet("color: green;")
        my_app.ui.label_18.setText("Ваш ход: Да")
        my_app.ui.pushButton.setEnabled(True)
        my_app.ui.pushButton_2.setEnabled(True)
        my_app.ui.pushButton_3.setEnabled(True)
        my_app.ui.pushButton_4.setEnabled(True)

    elif data.find("push_button_1|") != -1:
        text = data[data.find("|") + 1:data.rfind("|")]
        stroke_index = int(data[data.rfind("|") + 1:])
        print(f"stroke index = {stroke_index} and text = {text}")
        my_app.index_of_stroke += 1
        my_app.program_text[stroke_index] = text
        print(f"____________ {my_app.program_text}")
        if stroke_index == 0:
            my_app.ui.str_1.setText(text)
        elif stroke_index == 1:
            my_app.ui.str_2.setText(text)
        elif stroke_index == 2:
            my_app.ui.str_3.setText(text)
        elif stroke_index == 3:
            my_app.ui.str_4.setText(text)
        elif stroke_index == 4:
            my_app.ui.str_5.setText(text)
        elif stroke_index == 5:
            my_app.ui.str_6.setText(text)
        elif stroke_index == 6:
            my_app.ui.str_7.setText(text)
        elif stroke_index == 7:
            my_app.ui.str_8.setText(text)
        elif stroke_index == 8:
            my_app.ui.str_9.setText(text)
        elif stroke_index == 9:
            my_app.ui.str_10.setText(text)
        elif stroke_index == 10:
            my_app.ui.str_11.setText(text)
        elif stroke_index == 11:
            my_app.ui.str_12.setText(text)
        elif stroke_index == 12:
            my_app.ui.str_13.setText(text)
        elif stroke_index == 13:
            my_app.ui.str_14.setText(text)

    elif data.find("push_button_2|") != -1:
        text = data[data.find("|") + 1:data.rfind("|")]
        stroke_index = int(data[data.rfind("|") + 1:])
        print(f"stroke index = {stroke_index} and text = {text}")
        my_app.program_text[stroke_index] = text
        print(f"____________ {my_app.program_text}")
        if stroke_index == 0:
            my_app.ui.str_1.setText(text)
        elif stroke_index == 1:
            my_app.ui.str_2.setText(text)
        elif stroke_index == 2:
            my_app.ui.str_3.setText(text)
        elif stroke_index == 3:
            my_app.ui.str_4.setText(text)
        elif stroke_index == 4:
            my_app.ui.str_5.setText(text)
        elif stroke_index == 5:
            my_app.ui.str_6.setText(text)
        elif stroke_index == 6:
            my_app.ui.str_7.setText(text)
        elif stroke_index == 7:
            my_app.ui.str_8.setText(text)
        elif stroke_index == 8:
            my_app.ui.str_9.setText(text)
        elif stroke_index == 9:
            my_app.ui.str_10.setText(text)
        elif stroke_index == 10:
            my_app.ui.str_11.setText(text)
        elif stroke_index == 11:
            my_app.ui.str_12.setText(text)
        elif stroke_index == 12:
            my_app.ui.str_13.setText(text)
        elif stroke_index == 13:
            my_app.ui.str_14.setText(text)

    elif data.find("pushbutton3|") != -1:
        listed = list(data.split("|"))
        listed.remove('pushbutton3')
        print(f" LIST = {listed}")
        my_app.ui.window.setCurrentIndex(4)
        sleep(0.5)
        my_app.ui.label_res.setText(f"{listed[0]} из {listed[1]}")

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
            sleep(6)


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
    t4 = Thread(target=started_timer2)
    t4.daemon = True
    t4.start()


def started_timer2():
    seconds = my_app.timer_min * 60 + my_app.timer_sec
    while seconds > 0:
        if my_app.stop_timer == 1:
            my_app.stop_timer = 0
            if my_app.ui.window.currentIndex() == 3:
                my_app.push_button_3()
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
    my_app.stop_timer = 0
    if my_app.ui.window.currentIndex() == 3:
        my_app.push_button_3()
    return 0


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
