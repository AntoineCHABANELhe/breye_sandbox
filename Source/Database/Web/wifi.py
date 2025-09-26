import requests
from time import sleep
from colorama import Fore
from threading import Thread

from Source.BrailleTool.handle_logs import print_debug
from Source.Database.Web.Websocket.ws_handler import SocketHandler


def onConnected():
    print_debug(f"\t\t\t\t{Fore.CYAN}|_-_|{Fore.RESET} Web Socket : {Fore.GREEN}Connected{Fore.RESET}")
    SocketHandler().start()


def onDisconnected():
    print_debug(f"\t\t\t\t{Fore.CYAN}|_-_|{Fore.RESET} Web Socket : {Fore.RED}Disconnected{Fore.RESET}")
    SocketHandler().disconnect()


class Wifi:
    instance = None

    def __init__(self):
        if not Wifi.instance:
            Wifi.instance = Wifi.__Wifi()

    def __getattr__(self, name):
        return getattr(self.instance, name)

    class __Wifi:
        def __init__(self):
            self.thread = Thread(target=Wifi.check, args=[self], daemon=True)
            self.delay = 5
            self.checking = False
            self.connected = False

    def check(self):
        while self.checking:
            connected = False

            try:
                requests.head('https://www.google.com/', timeout=1).status_code
                connected = True
            except:
                pass

            if self.connected != connected:
                if connected:
                    onConnected()
                else:
                    onDisconnected()
            elif connected and not SocketHandler().isConnected():
                SocketHandler().start()

            self.connected = connected
            sleep(self.delay)

    def isConnected(self):
        return self.connected

    def close(self):
        self.instance.checking = False
        self.instance.connected = False
        self.thread.join()
    
    def start(self):
        self.instance.checking = True
        self.instance.connected = False
        self.thread.start()
