import os
import json
import base64
import Source.Database.save_data as save
import Source.Database.export_data as export
import Source.FilesHandling.CreativeGroup.creative_group_handler as group_handler

from pathlib import Path
from colorama import Fore
from datetime import datetime
from Source.BrailleTool.error_enum import B_log
from Source.BrailleTool.handle_logs import print_debug, DEBUG
from Source.Database.error_log import errorLog
from Source.FilesHandling.files_update import saveCommit, getCommit, Version
from Source.FilesHandling.language_handler import LANGUAGE
from Source.Database.Web.creative_group_enum import Path
from Source.SoundHandling.fetch_data import FileFetch
from Source.FilesHandling.CreativeGroup.group_manager_factory import getQuizzPath, getQuizzesPath


Events = {}


def sync(socket_handler, data):
    print_debug(f"\t\t\t\t{Fore.CYAN}|_-_|{Fore.RESET} Websocket : Syncing...", DEBUG.WEB)

    try:
        group_handler.saveGroups(data["groups"])
    except Exception as e:
        errorLog(str(e), B_log.GROUP_CREATING)

    saveCommit(data["commit"])

    # Check if new files is available
    check_files(socket_handler, data["files"])

    # Check if there are quizzes to download
    check_quizzes(socket_handler, data["quizzes"])

    # Check if accounts pseudo are missing
    check_accounts(socket_handler, data["accounts"])

    # Check if tts are missing
    check_tts(socket_handler, data["tts"])

    # Send databases 
    send_databases(socket_handler)

    # Define all box credentials
    equipment = data["equipment"]

    if "wifis" in equipment:
        save.saveWifiNetworks(equipment["wifis"])

    socket_handler.dispatch("connected")

    syncQuizzes(socket_handler)


def send_databases(socket_handler):
    databases = export.get_all_data()  # TODO web : why don't we send all dates ? / why are there missing tokens / words

    for database in databases:
        socket_handler.emit("data", {
            "table": database,
            "data": databases[database]
        })


def check_tts(socket_handler, all_tts=[]):
    FileFetch().setDicPaths(retry=True)
    tts_missing = []

    for tts in all_tts:
        if not tts.isdigit() and None in [FileFetch().getFilePath(tts, lang=lang.value, retry=True) for lang in LANGUAGE]:
            tts_missing.append(tts)

    socket_handler.emit("download", {"name": "tts", "data": tts_missing})
    if len(tts_missing):
        print_debug(f"\t\t\t\t{Fore.CYAN}|_-_|{Fore.RESET} Websocket : {len(tts_missing)} TTS missing, downloading....")
    else:
        print_debug(f"\t\t\t\t{Fore.CYAN}|_-_|{Fore.RESET} Websocket : no TTS missing", DEBUG.WEB)


def check_accounts(socket_handler, accounts=[]):
    for account in accounts:
        pseudo = export.get_user_pseudo(account["id"], "breye_user_id")

        if pseudo != account["pseudo"] and account["pseudo"] != False:
            save.saveUserPseudo(account["pseudo"], account["id"], "breye_user_id")

        # Check if pseudo tts is missing
        if account["pseudo"] is not None:
            if not os.path.exists(f"{Path.API.value}{account['pseudo']}"):
                socket_handler.emit("download", {"name": "tts", "data": [f"{account['pseudo']}"]})


def check_files(socket_handler, files):
    without = []
    to_remove = []
    nb_del = 0

    for file in files:
        if file["status"] == "deleted":
            nb_del += 1
            to_remove.append(file["filename"])
            without.append(file["filename"])
        elif file["status"] == "renamed":
            to_remove.append(file["oldName"])
            without.append(file["oldName"])

        if file["hash"]:
            if group_handler.checkFile(file["filename"], file["hash"]):
                without.append(file["filename"])

    saveCommit({ 
        Version.TO_REMOVE.value: to_remove, 
        Version.NB_FILES.value : len(files) - nb_del,
    })

    if files:
        print_debug(f"\t\t\t\t{Fore.CYAN}|_-_|{Fore.RESET} Websocket : {len(files) - len(without)} files to download. {len(without)} files already up to date. {len(to_remove)} files to remove.")
        socket_handler.emit("update", {"name": "start", "without": without})
    else:
        print_debug(f"\t\t\t\t{Fore.CYAN}|_-_|{Fore.RESET} Websocket : no files to download or to remove. {len(without)} files already up to date.", DEBUG.WEB)


def check_quizzes(socket_handler, all_quizzes):
    for quizz_id, path in getQuizzesPath().items():
        try:
            date = os.path.getmtime(f"{path}/{quizz_id}.json")
        except:
            date = False

        if date:
            if any(str(d['id']) == str(quizz_id) for d in all_quizzes):
                quizz = next((d for d in all_quizzes if str(d["id"]) == str(quizz_id)), None)
                dt = datetime.fromtimestamp(quizz["updated_at"])

                if date == dt.timestamp():
                    all_quizzes.remove(quizz)
            else:
                print_debug(f"\t\t\t\t{Fore.CYAN}|_-_|{Fore.RESET} Websocket : Removing quizz... [{quizz_id}]")
                removeQuizz(quizz_id)

    if all_quizzes:
        socket_handler.emit("quizzes", list(map(lambda x: x["id"], all_quizzes)))


def syncQuizzes(socket_handler):
    all_quizzes = []

    for quizz, path in getQuizzesPath().items():
        try:
            date = os.path.getmtime(f"{path}/{quizz}.json")
            all_quizzes.append({"id": quizz, "updated_at": date})
        except:
            pass

    socket_handler.emit("sync:quizzes", all_quizzes)
    print_debug(f"\t\t\t\t{Fore.CYAN}|_-_|{Fore.RESET} Websocket : Quizzes synced : {len(all_quizzes)}", DEBUG.WEB)


def download(socket_handler, data):
    if data["name"] == "tts":
        download_tts(socket_handler, data)

    socket_handler.emit("download", {"name": data["name"], "data": data["remaining"]})


def download_tts(socket_handler, data):
    filename = data["file"]
    socket_handler.downloadedTTS += 1

    with open(f"{Path.API.value}{filename}", "wb") as file:
        bytes = base64.b64decode(data["bytes"])

        if bytes and len(bytes) > 0:
            file.write(bytes)
            file.close()

    if not data["remaining"]:
        print_debug(f"\t\t\t\t{Fore.CYAN}|_-_|{Fore.RESET} Websocket : {socket_handler.downloadedTTS} TTS downloaded.")
        socket_handler.downloadedTTS = 0


def quizzes(socket_handler, data):
    _id = f"{data['id']}.json"
    content = data["data"]

    print_debug(f"\t\t\t\t{Fore.CYAN}|_-_|{Fore.RESET} Websocket : Downloading quizzes... [{_id}]")

    path = getQuizzPath(data["id"])

    with open(path, 'w+', encoding="utf-8") as file:
        quizz = content
        file.write(json.dumps(quizz, indent=4))
        file.close()
        os.utime(path, (quizz["updated_at"], quizz["updated_at"]))

    if data["tts"]:
        socket_handler.emit("download", {"name": "tts", "data": data["tts"]})

    save.tellUpdateQuizz(data['id'])  # todo web: Tell it only when all of the audios (tts) are downloaded ! call : self.setDicPaths(retry=True)

    if data["remaining"]:
        socket_handler.emit("quizzes", data["remaining"])
    else:
        print_debug(f"\t\t\t\t{Fore.CYAN}|_-_|{Fore.RESET} Websocket : Quizzes downloaded!", DEBUG.WEB)
        syncQuizzes(socket_handler)


def updateQuizz(socket_handler, data):
    print_debug(f"\t\t\t\t{Fore.CYAN}|_-_|{Fore.RESET} Websocket : Updating quizz... [{data['id']}]...")
    
    path = getQuizzPath(data["id"])

    try:
        os.remove(path)
    except:
        pass
    socket_handler.emit("quizzes", [data["id"]])


def removeQuizz(quizz_id):  # TODO web:  get 2 arguments ?
    try:
        os.remove(getQuizzPath(quizz_id))
    except Exception as e:
        errorLog(str(e), B_log.REMOVE_QUIZZ)
    save.tellUpdateQuizz(quizz_id)


def updatePseudo(data):
    _id = data["id"]
    if data["pseudo"] is None:
        return
        
    print_debug(f"\t\t\t\t{Fore.CYAN}|_-_|{Fore.RESET} Websocket : Updating pseudo... [{_id}]")
    save.saveUserPseudo(data["pseudo"], _id)


def updateEquipment(data):
    print_debug(f"\t\t\t\t{Fore.CYAN}|_-_|{Fore.RESET} Websocket : Updating equipment... [{data}]")
    save.saveWifiNetworks(data["wifis"])


def updateCommit(data):
    print_debug(f"\t\t\t\t{Fore.CYAN}|_-_|{Fore.RESET} Websocket : Updating commit... [{data}]")
    # save.saveCommit(data["commit"])


def update(socket_handler, data):
    if data["name"] == "download":
        updateDownload(socket_handler, data)

    if data["name"] == "finish":
        print_debug(f"\t\t\t\t{Fore.CYAN}|_-_|{Fore.RESET} Websocket : Update done, next commit: {getCommit()[Version.NEXT_COMMIT.value]}")
        print_debug(f"\t\t\t\t{Fore.CYAN}|_-_|{Fore.RESET} Websocket : Downloaded file : {socket_handler.downloadedFiles}")


def updateDownload(socket_handler, data):
    file = data["file"]
    filename = file["filename"]
    socket_handler.downloadedFiles += 1

    os.makedirs(os.path.dirname(f"new/{filename}"), exist_ok=True)

    with open(f"new/{filename}", "wb") as file:
        bytes = base64.b64decode(data["bytes"])

        if bytes and len(bytes) > 0:
            file.write(bytes)

    socket_handler.emit("update", {"name": "download"})


Events["sync"] = sync
Events["download"] = download
Events["quizzes"] = quizzes
Events["update"] = update
Events["remove:quizz"] = removeQuizz
Events["update:quizz"] = updateQuizz
Events["update:pseudo"] = updatePseudo
Events["update:equipment"] = updateEquipment
Events["update:commit"] = updateCommit
