from PyQt6.QtCore import QObject, QThread, pyqtSignal
import sys
import pathlib

class API():
    def __init__(self, guiObj):
        self.gui = guiObj
        self.worker = WorkerStdin()
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.worker.signal.connect(self.OnOpenFile)
        self.thread.started.connect(self.worker.stdin)
        self.thread.start()

    def OnOpenFile(self, path):
        self.gui.open_file(path)

class WorkerStdin(QObject):

    signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def stdin(self):
        print("[TRACE SELECTOR]", flush=True)
        while (line := sys.stdin.readline().strip("\n")) != "":
            args = line.split("\t")
            match args[0].lower():
                case "open":
                    if len(args) != 2:
                        print("[TRACESELECTOR] [SYNTAX_ERROR] open [path]", flush=True)
                        continue
                    path = args[1].strip("'").strip('"')
                    if not pathlib.Path(args[1]).exists():
                        print(f"[TRACESELECTOR] [FILE_NOT_EXISTS_ERROR] File {path} does not exists", flush=True)
                        continue
                    print(f"[TRACESELECTOR] [OPEN_FILE] Opening file {path}", flush=True)
                    self.signal.emit(path)
                case _:
                    print(f"[TRACESELECTOR] [UNKOWN_CMD_ERROR] Unknown command '{args[0]}'", flush=True)
        print("[TRACESELECTOR] [STOPED_API]", flush=True)