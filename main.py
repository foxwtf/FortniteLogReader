import os
import ctypes

from utils.reader import LogReader

def main():
    targetPath = r"%LOCALAPPDATA%\FortniteGame\Saved\Logs\FortniteGame.log"
    logReader = LogReader(targetPath)

    def consoleHandler(ctrlType):
        if ctrlType in (0, 2, 5, 6):
            logReader.openExplorer()
            return True
        return False

    handlerRoutine = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_uint)(consoleHandler)
    ctypes.windll.kernel32.SetConsoleCtrlHandler(handlerRoutine, 1)

    try:
        logReader.watch()
    except KeyboardInterrupt:
        pass
    finally:
        logReader.openExplorer()
        os._exit(0)

if __name__ == "__main__":
    main()