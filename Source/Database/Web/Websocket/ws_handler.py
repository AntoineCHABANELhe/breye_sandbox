import socketio

from Source.BrailleTool.handle_logs import print_debug, DEBUG
from Source.Database.Web.Websocket.ws_events import Events
from colorama import Fore
from Resources.unit_test import inUnittest
from Source.FilesHandling.files_update import getCommit, Version
from Source.Database.Web.creative_group_enum import Url
import Source.Database.export_data as export
from Source.Database.handle_database import HandleDB


class SocketHandler:
    instance = None

    def __init__(self):
        if not SocketHandler.instance:
            SocketHandler.instance = SocketHandler.__SocketHandler()
            HandleDB().setEmit(self.emit)

    def __getattr__(self, name):
        return getattr(self.instance, name)

    class __SocketHandler:
        def __init__(self) -> None:
            self.downloadedTTS = 0
            self.downloadedFiles = 0
            self.events = {}
            
            sio = socketio.Client(reconnection=True,
                                  reconnection_attempts=5,
                                  reconnection_delay_max=10,
                                  reconnection_delay=2)

            @sio.event
            def connect():
                print_debug(f"\t\t\t\t{Fore.CYAN}|_-_|{Fore.RESET} Websocket : Socket connected.", DEBUG.WEB)

            @sio.on('*')
            def catch_all(event, *args):
                if not self.sio.connected:
                    return

                if event in Events:
                    Events[event](self, *args)  # todo web : TypeError: removeQuizz() takes 1 positional arg but 2 were given
                else:
                    print_debug(f"\t\t\t\t{Fore.CYAN}|_-_|{Fore.RESET} Websocket : Unknown event [{event}]")

            @sio.event
            def connect_error(data):
                print_debug(f"\t\t\t\t{Fore.CYAN}|_-_|{Fore.RESET} Websocket : Connection failed. [start]", DEBUG.WEB)
                print_debug(data)
                print_debug(f"\t\t\t\t{Fore.CYAN}|_-_|{Fore.RESET} Websocket : Connection failed. [end]", DEBUG.WEB)

            @sio.event
            def disconnect():
                print_debug(f"\t\t\t\t{Fore.RED}|_-_|{Fore.RESET} Websocket : Disconnected.", DEBUG.WEB)

            self.sio = sio

        def start(self):
            if self.isConnected():
                return
            
            try:
                self.sio.connect(f"{Url.WS.value}?mac={export.get_mac()}"
                                 f"&{Version.CURRENT_COMMIT.value}={getCommit()[Version.CURRENT_COMMIT.value]}")
                print_debug(f"\t\t\t\t{Fore.CYAN}|_-_|{Fore.RESET} Websocket : Connection started.", DEBUG.WEB)
            except Exception as e:
                if not inUnittest():
                    print_debug(f"\t\t\t\t{Fore.CYAN}|_-_|{Fore.RESET} Websocket : Connection failed. [{e}]", DEBUG.WEB)

        def isConnected(self):
            return self.sio.connected

        def disconnect(self):
            if not self.sio.connected:
                print_debug(f"\t\t\t\t{Fore.CYAN}|_-_|{Fore.RESET} Websocket : Socket already disconnected.", DEBUG.WEB)
                return
            
            self.sio.disconnect()

            print_debug(f"\t\t\t\t{Fore.RED}|_-_|{Fore.RESET} Websocket : Disconnected. [Forced].", DEBUG.WEB)

        def emit(self, event, data):
            if not self.sio.connected:
                print_debug(f"\t\t\t\t{Fore.CYAN}|_-_|{Fore.RESET} Websocket : Socket not connected. [{event}]", DEBUG.WEB)
                return

            try:
                self.sio.emit(event, data)
            except Exception as e:
                if not inUnittest():
                    print_debug(f"\t\t\t\t{Fore.CYAN}|_-_|{Fore.RESET} Websocket : emit error [{e}] [{event}]")

        def on(self, event, callback):
            self.events[event] = self.events[event] if event in self.events else []
            self.events[event].append(callback)

        def dispatch(self, event, *args):
            if event in self.events:
                for callback in self.events[event]:
                    callback(*args)
