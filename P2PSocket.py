import socket  # 导入模块
from threading import Thread
import time
import queue


class ServerThread(Thread):
    """服务线程，进行消息的接收"""
    def __init__(self, my_queue):  # 初始化线程
        super().__init__()
        self._ip_address_list = []   # 保存连接过的ip地址，便于下次连接
        self._ip_address = get_host_ip()
        self._sever = socket.socket()
        self._my_queue = my_queue

    def run(self):
        self._sever.bind((self._ip_address, 6310))
        self._sever.listen(512)
        print("本地" + self._ip_address + "正在监听等待连接。。。")
        while True:
            time.sleep(1)
            client, address = self._sever.accept()
            self._ip_address_list.append(address)
            message = client.recv(512).decode('utf-8')
            self._my_queue.put("来自" + address[0] + '：' + message)
            # print("来自" + address[0] + '：' + client.recv(512).decode('utf-8'))

    @property
    def ip_address(self):
        return self._ip_address

    @property
    def ip_address_list(self):
        return self._ip_address_list


class ClientThread(Thread):
    def __init__(self):
        super().__init__()
        self._ip_address = ''
        self._is_send = False
        self._message = ''

    def run(self):
        while True:
            if self._is_send:
                client = socket.socket()
                client.connect(self._ip_address)
                client.send(self._message.encode('utf-8'))
                self._is_send = False
                time.sleep(2)
                client.close()

    def send_message(self, ip_address, message):
        self._is_send = True
        self._ip_address = ip_address
        self._message = message


class MessageThread(Thread):
    def __init__(self, my_queue):
        super().__init__()
        self._queue = my_queue

    def run(self):
        while True:
            if not self._queue.empty():
                print('\n'+self._queue.get())


# noinspection PyTypeChecker,PyGlobalUndefined
def main():
    my_queue = queue.Queue()
    server_thread = ServerThread(my_queue)
    server_thread.setDaemon(True)
    server_thread.start()
    client_thread = ClientThread()
    client_thread.setDaemon(True)
    client_thread.start()
    message_thread = MessageThread(my_queue)
    message_thread.setDaemon(True)
    message_thread.start()
    running = True
    is_start = True
    ip_address = None
    while running:
        if is_start:
            order = int(input('1.查看聊天列表\n2.地址找聊天对象'))
            if order == 1:
                my_address = server_thread.ip_address_list
                for index, ip_address in enumerate(my_address):
                    print(str(index + 1) + '#' + str(ip_address))
                if len(my_address) > 0:
                    num = int(input('需要联系几号：'))
                    ip_address = my_address[num - 1]
                    # print(ip_address)
                    is_start = False
            elif order == 2:
                ip = input('请输入对方地址：')
                port = 6310
                ip_address = ip, port
                is_start = False
        else:
            if ip_address:
                message = input('quit()退出重选对象\n需要发送的消息：')
                if message == 'quit()':
                    is_start = True
                else:
                    client_thread.send_message(ip_address, message)


def get_host_ip():
    """
    查询本机ip地址
    :return: ip
    """
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.10.10.10', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


if __name__ == '__main__':
    main()
