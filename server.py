from Server_socket import Socket
import sqlite3
from time import time, sleep


class Server(Socket):
    def __init__(self):
        super(Server, self).__init__()
        self.users = []  # сокеты клиентов
        self.addresses = []  # ip, port клиентов
        self.teams_count = 0  # количество команд
        self.timer_secs = 0  # timer стоит на нуле
        self.current_task = 1  # Текущий номер задания (по умолчанию 1)
        self.admin_sock = []

        # Массивы сокетов каждой команды
        self.socket_team1 = []
        self.socket_team2 = []
        self.socket_team3 = []
        self.socket_team4 = []
        self.socket_team5 = []
        self.socket_team6 = []

        self.team1_queue = 0
        self.team2_queue = 0
        self.team3_queue = 0
        self.team4_queue = 0
        self.team5_queue = 0
        self.team6_queue = 0

        self.team1_current_turn = 0
        self.team2_current_turn = 0
        self.team3_current_turn = 0
        self.team4_current_turn = 0
        self.team5_current_turn = 0
        self.team6_current_turn = 0

    def set_up(self):
        self.socket.bind(("127.0.0.1", 9669))
        self.socket.listen(50)
        self.socket.setblocking(False)
        print("Server is running and listening!")
        cur.execute("SELECT COUNT(*) FROM teams")
        self.teams_count = cur.fetchall()[0][0]  # запись количества существующих команд
        cur.execute("DELETE FROM users")
        con.commit()

    async def listen_socket(self, listened_socket=None):
        if not listened_socket:
            return 0
        while True:
            try:
                data = await self.main_loop.sock_recv(listened_socket, 4096)
                data.decode("utf-8")
                await distributor(data, listened_socket)
            except ConnectionResetError:
                print("__________________________")
                addr = self.addresses[self.users.index(listened_socket)]

                # _________________________________________________________________________________________________
                ip, port = addr[0], addr[1]
                cur.execute("SELECT team FROM users WHERE ip=? AND port=?", (ip, port))
                team_index = cur.fetchall()[0][0]  # Ищется индекс команды

                if team_index == 1:
                    self.socket_team1.remove(listened_socket)
                elif team_index == 2:
                    self.socket_team2.remove(listened_socket)
                elif team_index == 3:
                    self.socket_team3.remove(listened_socket)
                elif team_index == 4:
                    self.socket_team4.remove(listened_socket)
                elif team_index == 5:
                    self.socket_team5.remove(listened_socket)
                elif team_index == 6:
                    self.socket_team6.remove(listened_socket)
                cur.execute("DELETE FROM users WHERE ip=? AND port=?", (str(addr[0]), str(addr[1])))
                con.commit()
                self.addresses.remove(addr)
                try:
                    if self.admin_sock[0] == listened_socket:
                        self.admin_sock.remove(listened_socket)
                finally:
                    self.users.remove(listened_socket)
                    print('User disconnected!')
                    return 0

    async def accept_sockets(self):
        while True:
            user_socket, address = await self.main_loop.sock_accept(self.socket)

            self.users.append(user_socket)
            self.addresses.append(address)
            cur.execute("INSERT INTO users VALUES (?, ?, NULL, NULL)", (str(address[0]), str(address[1])))
            con.commit()
            self.main_loop.create_task(self.listen_socket(user_socket))

    async def main(self):
        await self.main_loop.create_task(self.accept_sockets())


async def distributor(data, sock):
    data = data.decode("utf-8")
    sleep(.1)

    # BUTTON 4
    if data.find("button4") != -1:
        print("Student try to get in to team")
        name_of_user = data[data.find("|") + 1:len(data) - 2]
        choose_team = int(data[len(data) - 1:]) + 1
        print(f"Name of user is {name_of_user} and he choose team number {choose_team}")
        cur.execute("SELECT capacity FROM teams WHERE id=?", (str(choose_team),))
        team_capacity = cur.fetchall()[0][0]
        print(f"Team capacity = {team_capacity}")
        cur.execute("SELECT COUNT(*) FROM users WHERE team=?", (str(choose_team),))
        in_team_users = cur.fetchall()[0][0]
        print(f"Already users in team = {in_team_users}")
        try:
            if team_capacity - in_team_users <= 0:
                sock.send("button4|0".encode("utf-8"))
            else:
                addr = server.addresses[server.users.index(sock)]
                ip, port = addr[0], addr[1]
                cur.execute("UPDATE users SET name=?, team=? WHERE ip=? AND port=?", (name_of_user, str(choose_team),
                                                                                      ip, port))
                con.commit()
                sock.send("button4|1".encode("utf-8"))
            return 0
        except:
            print("Error to add client to team")
            return -1

    elif data.find("admin_rights_permission_3223") != -1:
        addr = server.addresses[server.users.index(sock)]
        ip, port = addr[0], addr[1]
        cur.execute("UPDATE users SET name=? WHERE ip=? AND port=?", ("admin", ip, port))
        con.commit()
        server.admin_sock.append(sock)
        return 0

    # BUTTON ADMIN 4
    elif data.find("admin_b4") != -1:
        print("Admin try to add new team")
        team_name = data[data.find("|") + 1:len(data)]
        print(team_name)
        server.teams_count += 1
        if server.teams_count > 6:
            print("Maximum of teams already reached!")
            sock.send("admin_b4|0".encode("utf-8"))
            return -1
        try:
            cur.execute("INSERT INTO teams VALUES (?, ?, 0, NULL)", (server.teams_count, team_name))
            con.commit()

            cur.execute("SELECT name FROM teams")
            team_names = cur.fetchall()
            data = "b29|"
            for name in team_names:
                data += str(name[0]) + "|"
            print("_______________" + data)
            for sockets in server.users:
                sockets.send(data.encode("utf-8"))
            return 0
        except:
            print("Error to add new team")
            return -1

    # BUTTON 29
    elif data.find("b29|") != -1:
        cur.execute("SELECT name FROM teams")
        team_names = cur.fetchall()
        data = "b29|"
        for name in team_names:
            data += str(name[0]) + "|"
        try:
            sock.send(data.encode("utf-8"))
            return 0
        except:
            print("Ошибка Update list of teams for admin")
            return -1

    # BUTTON 13
    elif data.find("admin_b13") != -1:
        row = int(data[data.find("|") + 1:]) + 1
        print(row)
        cur.execute("DELETE FROM teams WHERE id=?;", (str(row),))
        con.commit()
        cur.execute("SELECT COUNT(*) FROM teams")
        teams_count = cur.fetchall()[0][0]
        server.teams_count = teams_count
        for i in range(row, teams_count + 1):
            cur.execute("UPDATE teams SET id=? WHERE id=?", (i, i + 1))
            con.commit()

        # Send to client updated version
        cur.execute("SELECT name FROM teams")
        team_names = cur.fetchall()
        data = "b29|"
        for name in team_names:
            data += str(name[0]) + "|"
        print("_______________" + data)
        try:
            for sockets in server.users:
                sockets.send(data.encode("utf-8"))
            return 0
        except:
            print("Ошибка Update list of teams for admin")
            return -1

    # BUTTON 4 Continue - Обновление списка имен игроков в лобби ожидания при входе/выходе в команду
    elif data.find("b4con") != -1:
        addr = server.addresses[server.users.index(sock)]
        ip, port = addr[0], addr[1]
        cur.execute("SELECT team FROM users WHERE ip=? AND port=?", (ip, port))
        team_index = cur.fetchall()[0][0]  # Ищется индекс команды
        print(type(team_index), "________", team_index)
        cur.execute("SELECT name FROM users WHERE team=?", (str(team_index),))
        usernames_in_team = cur.fetchall()  # Все имена в команде добавляются в список и отправляются
        data = "b4con|"
        for name in usernames_in_team:
            data += str(name[0]) + "|"
        print(f"NAMES = {data}")
        cur.execute("SELECT ip, port FROM users WHERE team=?", (str(team_index),))
        ip_port = cur.fetchall()
        print(ip_port)
        print()

        if team_index == 1:
            server.socket_team1.append(sock)
        elif team_index == 2:
            server.socket_team2.append(sock)
        elif team_index == 3:
            server.socket_team3.append(sock)
        elif team_index == 4:
            server.socket_team4.append(sock)
        elif team_index == 5:
            server.socket_team5.append(sock)
        elif team_index == 6:
            server.socket_team6.append(sock)

        for ips_ports in ip_port:
            addr = (ips_ports[0], ips_ports[1])
            for i in range(len(server.users)):
                if addr == server.addresses[i]:
                    server.users[i].send(data.encode("utf-8"))

    # BUTTON 5 from client - leave team
    elif data.find("button5c|") != -1:
        addr = server.addresses[server.users.index(sock)]
        ip, port = addr[0], addr[1]
        cur.execute("SELECT team FROM users WHERE ip=? AND port=?", (ip, port))
        team_index = cur.fetchall()[0][0]  # Ищется индекс команды
        # Delete user from team
        cur.execute("UPDATE users SET name=NULL, team=NULL WHERE ip=? AND port=?", (ip, port))
        con.commit()
        # Copy ↓↓↓
        cur.execute("SELECT name FROM users WHERE team=?", (str(team_index),))
        usernames_in_team = cur.fetchall()  # Все имена в команде добавляются в список и отправляются
        data = "b4con|"

        if team_index == 1:
            server.socket_team1.remove(sock)
        elif team_index == 2:
            server.socket_team2.remove(sock)
        elif team_index == 3:
            server.socket_team3.remove(sock)
        elif team_index == 4:
            server.socket_team4.remove(sock)
        elif team_index == 5:
            server.socket_team5.remove(sock)
        elif team_index == 6:
            server.socket_team6.remove(sock)

        for name in usernames_in_team:
            data += str(name[0]) + "|"
        print(f"NAMES = {data}")
        cur.execute("SELECT ip, port FROM users WHERE team=?", (str(team_index),))
        ip_port = cur.fetchall()
        print(ip_port)
        print()
        for ips_ports in ip_port:
            addr = (ips_ports[0], ips_ports[1])
            for i in range(len(server.users)):
                if addr == server.addresses[i]:
                    server.users[i].send(data.encode("utf-8"))

    # BUTTON 5 from admin to change team capacity
    elif data.find("admin_b5|") != -1:
        capacity_team = data[data.find("|") + 1:]
        cur.execute("UPDATE teams SET capacity=?", (capacity_team,))
        con.commit()

    # BUTTON 6 from admin to change timer
    elif data.find("admin_b6|") != -1:
        server.timer_secs = int(data[data.find("|") + 1:])
        for user in server.users:
            data = "button_6admin|" + str(server.timer_secs)
            user.send(data.encode("utf-8"))

    # BUTTON 7 change current task
    elif data.find("admin_b7|") != -1:
        server.current_task = int(data[data.find("|") + 1:])
        print(f'Current task = {server.current_task}')
        data = "admin_b7_update|" + str(server.current_task)
        for user in server.users:
            user.send(data.encode("utf-8"))

    elif data.find("admin_starts|") != -1:
        data = "admin_started"
        for user in server.users:
            user.send(data.encode("utf-8"))
        sleep(1)
        data = "your_turn"
        if len(server.socket_team1) != 0:
            server.socket_team1[server.team1_queue].send(data.encode("utf-8"))
        if len(server.socket_team2) != 0:
            server.socket_team2[server.team2_queue].send(data.encode("utf-8"))
        if len(server.socket_team3) != 0:
            server.socket_team3[server.team3_queue].send(data.encode("utf-8"))
        if len(server.socket_team4) != 0:
            server.socket_team4[server.team4_queue].send(data.encode("utf-8"))
        if len(server.socket_team5) != 0:
            server.socket_team5[server.team5_queue].send(data.encode("utf-8"))
        if len(server.socket_team6) != 0:
            server.socket_team6[server.team6_queue].send(data.encode("utf-8"))

    elif data.find("push_button_1|") != -1:
        if server.socket_team1.count(sock) != 0:
            server.team1_queue += 1
            if server.team1_queue >= len(server.socket_team1):
                server.team1_queue = 0
            server.socket_team1[server.team1_queue].send("your_turn".encode("utf-8"))
            sleep(1)
            for socks in server.socket_team1:
                socks.send(data.encode("utf-8"))

            # --------------------------------------------------------------------------------
            text = data[data.find("|") + 1:data.rfind("|")]
            stroke_index = int(data[data.rfind("|") + 1:])
            print(f"stroke index = {stroke_index} and text = {text}")

            data = "result_final|"+str(server.team1_current_turn)+"|"
            server.team1_current_turn += 1
            addr = server.addresses[server.users.index(sock)]
            ip, port = addr[0], addr[1]
            cur.execute("SELECT name FROM users WHERE ip=? AND port=?", (ip, port))
            name = str(cur.fetchall()[0][0])  # Ищется индекс команды
            data += name + "|"
            data += str(stroke_index+1) + "|"
            data += text + "|1"
            # data - result_final|curr turn|name|stroke index|text

            server.admin_sock[0].send(data.encode("utf-8"))
            # --------------------------------------------------------------------------------
        elif server.socket_team2.count(sock) != 0:
            server.team2_queue += 1
            if server.team2_queue >= len(server.socket_team2):
                server.team2_queue = 0
            server.socket_team2[server.team2_queue].send("your_turn".encode("utf-8"))
            sleep(1)
            for socks in server.socket_team2:
                socks.send(data.encode("utf-8"))
            # --------------------------------------------------------------------------------
            text = data[data.find("|") + 1:data.rfind("|")]
            stroke_index = int(data[data.rfind("|") + 1:])
            print(f"stroke index = {stroke_index} and text = {text}")

            data = "result_final|" + str(server.team2_current_turn) + "|"
            server.team2_current_turn += 1
            addr = server.addresses[server.users.index(sock)]
            ip, port = addr[0], addr[1]
            cur.execute("SELECT name FROM users WHERE ip=? AND port=?", (ip, port))
            name = str(cur.fetchall()[0][0])  # Ищется индекс команды
            data += name + "|"
            data += str(stroke_index + 1) + "|"
            data += text + "|2"
            # data - result_final|curr turn|name|stroke index|text

            server.admin_sock[0].send(data.encode("utf-8"))
            # --------------------------------------------------------------------------------

        elif server.socket_team3.count(sock) != 0:
            server.team3_queue += 1
            if server.team3_queue >= len(server.socket_team3):
                server.team3_queue = 0
            server.socket_team3[server.team3_queue].send("your_turn".encode("utf-8"))
            sleep(1)
            for socks in server.socket_team3:
                socks.send(data.encode("utf-8"))
            print()
            # --------------------------------------------------------------------------------
            text = data[data.find("|") + 1:data.rfind("|")]
            stroke_index = int(data[data.rfind("|") + 1:])
            print(f"stroke index = {stroke_index} and text = {text}")

            data = "result_final|" + str(server.team3_current_turn) + "|"
            server.team3_current_turn += 1
            addr = server.addresses[server.users.index(sock)]
            ip, port = addr[0], addr[1]
            cur.execute("SELECT name FROM users WHERE ip=? AND port=?", (ip, port))
            name = str(cur.fetchall()[0][0])  # Ищется индекс команды
            data += name + "|"
            data += str(stroke_index + 1) + "|"
            data += text + "|3"
            # data - result_final|curr turn|name|stroke index|text

            server.admin_sock[0].send(data.encode("utf-8"))
            # --------------------------------------------------------------------------------
        elif server.socket_team4.count(sock) != 0:
            server.team4_queue += 1
            if server.team4_queue >= len(server.socket_team4):
                server.team4_queue = 0
            server.socket_team4[server.team4_queue].send("your_turn".encode("utf-8"))
            sleep(1)
            for socks in server.socket_team4:
                socks.send(data.encode("utf-8"))
            print()
            # --------------------------------------------------------------------------------
            text = data[data.find("|") + 1:data.rfind("|")]
            stroke_index = int(data[data.rfind("|") + 1:])
            print(f"stroke index = {stroke_index} and text = {text}")

            data = "result_final|" + str(server.team4_current_turn) + "|"
            server.team4_current_turn += 1
            addr = server.addresses[server.users.index(sock)]
            ip, port = addr[0], addr[1]
            cur.execute("SELECT name FROM users WHERE ip=? AND port=?", (ip, port))
            name = str(cur.fetchall()[0][0])  # Ищется индекс команды
            data += name + "|"
            data += str(stroke_index + 1) + "|"
            data += text + "|4"
            # data - result_final|curr turn|name|stroke index|text

            server.admin_sock[0].send(data.encode("utf-8"))
            # --------------------------------------------------------------------------------
        elif server.socket_team5.count(sock) != 0:
            server.team5_queue += 1
            if server.team5_queue >= len(server.socket_team5):
                server.team5_queue = 0
            server.socket_team5[server.team5_queue].send("your_turn".encode("utf-8"))
            sleep(1)
            for socks in server.socket_team5:
                socks.send(data.encode("utf-8"))
            print()
            # --------------------------------------------------------------------------------
            text = data[data.find("|") + 1:data.rfind("|")]
            stroke_index = int(data[data.rfind("|") + 1:])
            print(f"stroke index = {stroke_index} and text = {text}")

            data = "result_final|" + str(server.team5_current_turn) + "|"
            server.team5_current_turn += 1
            addr = server.addresses[server.users.index(sock)]
            ip, port = addr[0], addr[1]
            cur.execute("SELECT name FROM users WHERE ip=? AND port=?", (ip, port))
            name = str(cur.fetchall()[0][0])  # Ищется индекс команды
            data += name + "|"
            data += str(stroke_index + 1) + "|"
            data += text + "|5"
            # data - result_final|curr turn|name|stroke index|text

            server.admin_sock[0].send(data.encode("utf-8"))
            # --------------------------------------------------------------------------------
        elif server.socket_team6.count(sock) != 0:
            server.team6_queue += 1
            if server.team6_queue >= len(server.socket_team6):
                server.team6_queue = 0
            server.socket_team6[server.team6_queue].send("your_turn".encode("utf-8"))
            sleep(1)
            for socks in server.socket_team6:
                socks.send(data.encode("utf-8"))
            print()
            # --------------------------------------------------------------------------------
            text = data[data.find("|") + 1:data.rfind("|")]
            stroke_index = int(data[data.rfind("|") + 1:])
            print(f"stroke index = {stroke_index} and text = {text}")

            data = "result_final|" + str(server.team6_current_turn) + "|"
            server.team6_current_turn += 1
            addr = server.addresses[server.users.index(sock)]
            ip, port = addr[0], addr[1]
            cur.execute("SELECT name FROM users WHERE ip=? AND port=?", (ip, port))
            name = str(cur.fetchall()[0][0])  # Ищется индекс команды
            data += name + "|"
            data += str(stroke_index + 1) + "|"
            data += text + "|6"
            # data - result_final|curr turn|name|stroke index|text

            server.admin_sock[0].send(data.encode("utf-8"))
            # --------------------------------------------------------------------------------

    elif data.find("push_button_2|") != -1:
        if server.socket_team1.count(sock) != 0:
            server.team1_queue += 1
            if server.team1_queue >= len(server.socket_team1):
                server.team1_queue = 0
            server.socket_team1[server.team1_queue].send("your_turn".encode("utf-8"))
            sleep(1)
            for socks in server.socket_team1:
                socks.send(data.encode("utf-8"))

            # --------------------------------------------------------------------------------
            text = data[data.find("|") + 1:data.rfind("|")]
            stroke_index = int(data[data.rfind("|") + 1:])
            print(f"stroke index = {stroke_index} and text = {text}")

            data = "result_final|"+str(server.team1_current_turn)+"|"
            server.team1_current_turn += 1
            addr = server.addresses[server.users.index(sock)]
            ip, port = addr[0], addr[1]
            cur.execute("SELECT name FROM users WHERE ip=? AND port=?", (ip, port))
            name = str(cur.fetchall()[0][0])  # Ищется индекс команды
            data += name + "|"
            data += str(stroke_index+1) + "|"
            data += text + "|1"
            # data - result_final|curr turn|name|stroke index|text

            server.admin_sock[0].send(data.encode("utf-8"))
            # --------------------------------------------------------------------------------
        elif server.socket_team2.count(sock) != 0:
            server.team2_queue += 1
            if server.team2_queue >= len(server.socket_team2):
                server.team2_queue = 0
            server.socket_team2[server.team2_queue].send("your_turn".encode("utf-8"))
            sleep(1)
            for socks in server.socket_team2:
                socks.send(data.encode("utf-8"))
            # --------------------------------------------------------------------------------
            text = data[data.find("|") + 1:data.rfind("|")]
            stroke_index = int(data[data.rfind("|") + 1:])
            print(f"stroke index = {stroke_index} and text = {text}")

            data = "result_final|" + str(server.team2_current_turn) + "|"
            server.team2_current_turn += 1
            addr = server.addresses[server.users.index(sock)]
            ip, port = addr[0], addr[1]
            cur.execute("SELECT name FROM users WHERE ip=? AND port=?", (ip, port))
            name = str(cur.fetchall()[0][0])  # Ищется индекс команды
            data += name + "|"
            data += str(stroke_index + 1) + "|"
            data += text + "|2"
            # data - result_final|curr turn|name|stroke index|text

            server.admin_sock[0].send(data.encode("utf-8"))
            # --------------------------------------------------------------------------------

        elif server.socket_team3.count(sock) != 0:
            server.team3_queue += 1
            if server.team3_queue >= len(server.socket_team3):
                server.team3_queue = 0
            server.socket_team3[server.team3_queue].send("your_turn".encode("utf-8"))
            sleep(1)
            for socks in server.socket_team3:
                socks.send(data.encode("utf-8"))
            print()
            # --------------------------------------------------------------------------------
            text = data[data.find("|") + 1:data.rfind("|")]
            stroke_index = int(data[data.rfind("|") + 1:])
            print(f"stroke index = {stroke_index} and text = {text}")

            data = "result_final|" + str(server.team3_current_turn) + "|"
            server.team3_current_turn += 1
            addr = server.addresses[server.users.index(sock)]
            ip, port = addr[0], addr[1]
            cur.execute("SELECT name FROM users WHERE ip=? AND port=?", (ip, port))
            name = str(cur.fetchall()[0][0])  # Ищется индекс команды
            data += name + "|"
            data += str(stroke_index + 1) + "|"
            data += text + "|3"
            # data - result_final|curr turn|name|stroke index|text

            server.admin_sock[0].send(data.encode("utf-8"))
            # --------------------------------------------------------------------------------
        elif server.socket_team4.count(sock) != 0:
            server.team4_queue += 1
            if server.team4_queue >= len(server.socket_team4):
                server.team4_queue = 0
            server.socket_team4[server.team4_queue].send("your_turn".encode("utf-8"))
            sleep(1)
            for socks in server.socket_team4:
                socks.send(data.encode("utf-8"))
            print()
            # --------------------------------------------------------------------------------
            text = data[data.find("|") + 1:data.rfind("|")]
            stroke_index = int(data[data.rfind("|") + 1:])
            print(f"stroke index = {stroke_index} and text = {text}")

            data = "result_final|" + str(server.team4_current_turn) + "|"
            server.team4_current_turn += 1
            addr = server.addresses[server.users.index(sock)]
            ip, port = addr[0], addr[1]
            cur.execute("SELECT name FROM users WHERE ip=? AND port=?", (ip, port))
            name = str(cur.fetchall()[0][0])  # Ищется индекс команды
            data += name + "|"
            data += str(stroke_index + 1) + "|"
            data += text + "|4"
            # data - result_final|curr turn|name|stroke index|text

            server.admin_sock[0].send(data.encode("utf-8"))
            # --------------------------------------------------------------------------------
        elif server.socket_team5.count(sock) != 0:
            server.team5_queue += 1
            if server.team5_queue >= len(server.socket_team5):
                server.team5_queue = 0
            server.socket_team5[server.team5_queue].send("your_turn".encode("utf-8"))
            sleep(1)
            for socks in server.socket_team5:
                socks.send(data.encode("utf-8"))
            print()
            # --------------------------------------------------------------------------------
            text = data[data.find("|") + 1:data.rfind("|")]
            stroke_index = int(data[data.rfind("|") + 1:])
            print(f"stroke index = {stroke_index} and text = {text}")

            data = "result_final|" + str(server.team5_current_turn) + "|"
            server.team5_current_turn += 1
            addr = server.addresses[server.users.index(sock)]
            ip, port = addr[0], addr[1]
            cur.execute("SELECT name FROM users WHERE ip=? AND port=?", (ip, port))
            name = str(cur.fetchall()[0][0])  # Ищется индекс команды
            data += name + "|"
            data += str(stroke_index + 1) + "|"
            data += text + "|5"
            # data - result_final|curr turn|name|stroke index|text

            server.admin_sock[0].send(data.encode("utf-8"))
            # --------------------------------------------------------------------------------
        elif server.socket_team6.count(sock) != 0:
            server.team6_queue += 1
            if server.team6_queue >= len(server.socket_team6):
                server.team6_queue = 0
            server.socket_team6[server.team6_queue].send("your_turn".encode("utf-8"))
            sleep(1)
            for socks in server.socket_team6:
                socks.send(data.encode("utf-8"))
            print()
            # --------------------------------------------------------------------------------
            text = data[data.find("|") + 1:data.rfind("|")]
            stroke_index = int(data[data.rfind("|") + 1:])
            print(f"stroke index = {stroke_index} and text = {text}")

            data = "result_final|" + str(server.team6_current_turn) + "|"
            server.team6_current_turn += 1
            addr = server.addresses[server.users.index(sock)]
            ip, port = addr[0], addr[1]
            cur.execute("SELECT name FROM users WHERE ip=? AND port=?", (ip, port))
            name = str(cur.fetchall()[0][0])  # Ищется индекс команды
            data += name + "|"
            data += str(stroke_index + 1) + "|"
            data += text + "|6"
            # data - result_final|curr turn|name|stroke index|text

            server.admin_sock[0].send(data.encode("utf-8"))
            # --------------------------------------------------------------------------------
    elif data.find("pushbutton3|") != -1:
        if server.socket_team1.count(sock) != 0:
            for socks in server.socket_team1:
                data += "|1"
                socks.send(data.encode("utf-8"))
            try:
                server.admin_sock[0].send(data.encode("utf-8"))
            except:
                print("No data send to Admin")
        elif server.socket_team2.count(sock) != 0:
            for socks in server.socket_team2:
                data += "|2"
                socks.send(data.encode("utf-8"))
            try:
                server.admin_sock[0].send(data.encode("utf-8"))
            except:
                print("No data send to Admin")
        elif server.socket_team3.count(sock) != 0:
            for socks in server.socket_team3:
                data += "|3"
                socks.send(data.encode("utf-8"))
            try:
                server.admin_sock[0].send(data.encode("utf-8"))
            except:
                print("No data send to Admin")
        elif server.socket_team4.count(sock) != 0:
            for socks in server.socket_team4:
                data += "|4"
                socks.send(data.encode("utf-8"))
            try:
                server.admin_sock[0].send(data.encode("utf-8"))
            except:
                print("No data send to Admin")
        elif server.socket_team5.count(sock) != 0:
            for socks in server.socket_team5:
                data += "|5"
                socks.send(data.encode("utf-8"))
            try:
                server.admin_sock[0].send(data.encode("utf-8"))
            except:
                print("No data send to Admin")
        elif server.socket_team6.count(sock) != 0:
            for socks in server.socket_team6:
                data += "|6"
                socks.send(data.encode("utf-8"))
            try:
                server.admin_sock[0].send(data.encode("utf-8"))
            except:
                print("No data send to Admin")

    elif data.find("STOP_RESET") != -1:
        for socks in server.users:
            socks.send(data.encode("utf-8"))
        server.team1_queue = 0
        server.team2_queue = 0
        server.team3_queue = 0
        server.team4_queue = 0
        server.team5_queue = 0
        server.team6_queue = 0
        server.team1_current_turn = 0
        server.team2_current_turn = 0
        server.team3_current_turn = 0
        server.team4_current_turn = 0
        server.team5_current_turn = 0
        server.team6_current_turn = 0


if __name__ == "__main__":
    server = Server()
    con = sqlite3.connect('main_database.db')
    cur = con.cursor()
    server.set_up()
    server.start()
