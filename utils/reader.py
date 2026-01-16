import os
import time
import subprocess
import re
from datetime import datetime

from utils.logs import Logger

class LogReader:
    def __init__(self, filePath):
        self.filePath = os.path.expandvars(filePath)
        self.launcherSource = os.path.join(os.path.dirname(self.filePath), "FortniteLauncher.log")
        self.logFolder = "logs"
        self.outputFile = None
        self.launcherOutput = None
        self.launcherPointer = 0
        self.initialized = False
        self.hasLogged = False

    def getAccountId(self):
        if not os.path.exists(self.launcherSource):
            return None
        try:
            with open(self.launcherSource, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                match = re.search(r"-epicuserid=([a-f0-9]+)", content)
                if match:
                    return match.group(1)
        except Exception:
            pass
        return None

    def initializePaths(self, accountId):
        targetDir = os.path.join(self.logFolder, accountId)
        if not os.path.exists(targetDir):
            os.makedirs(targetDir)
            
        gameLogPath = os.path.join(targetDir, "FortniteGame.log")
        if os.path.exists(gameLogPath):
            creationTime = os.path.getmtime(gameLogPath)
            dateStamp = datetime.fromtimestamp(creationTime).strftime("%Y.%m.%d-%H.%M.%S")
            backupName = os.path.join(targetDir, f"FortniteGame-backup-{dateStamp}.log")
            try:
                os.rename(gameLogPath, backupName)
            except Exception:
                pass

        self.outputFile = gameLogPath
        self.launcherOutput = os.path.join(targetDir, "FortniteLauncher.log")
        self.initialized = True

    def openExplorer(self):
        pathToShow = self.outputFile if (self.outputFile and os.path.exists(self.outputFile)) else self.logFolder
        if os.path.exists(pathToShow):
            fullPath = os.path.abspath(pathToShow)
            subprocess.run(f'explorer /select,"{fullPath}"', shell=True)

    def writeToFile(self, targetFile, tag, msg, isChild):
        prefix = "      " if isChild else f"[LOG] [{tag}] "
        with open(targetFile, "a", encoding="utf-8") as fileHandle:
            fileHandle.write(f"{prefix}{msg}\n")

    def cleanText(self, text):
        if ":" in text:
            header, body = text.split(":", 1)
            return f"{header.strip()}: {body.strip()}"
        return text.strip()

    def processLine(self, rawLine, targetFile, silent=False):
        isChild = rawLine.startswith(("\t", "    "))
        cleanLine = " ".join(rawLine.split()).strip()
        if not cleanLine: return False

        if "][" in cleanLine:
            parts = cleanLine.split("]", 2)
            if len(parts) > 2: cleanLine = parts[2].strip()

        if not isChild and ":" not in cleanLine: return False
        
        if targetFile == self.outputFile and "Log file closed" in cleanLine: 
            return True

        self.hasLogged = True

        if "Error:" in cleanLine:
            msg = self.cleanText(cleanLine.replace("Error:", ""))
            if not silent: Logger.error(msg, isChild)
            self.writeToFile(targetFile, "ERROR", msg, isChild)
        elif "Warning:" in cleanLine:
            msg = self.cleanText(cleanLine.replace("Warning:", ""))
            if not silent: Logger.warning(msg, isChild)
            self.writeToFile(targetFile, "WARNING", msg, isChild)
        else:
            msg = self.cleanText(cleanLine)
            if not silent: Logger.info(msg, isChild)
            self.writeToFile(targetFile, "SUCCESS", msg, isChild)
        return False

    def updateLauncherLive(self):
        if not os.path.exists(self.launcherSource):
            return

        if not self.initialized:
            accountId = self.getAccountId()
            if accountId:
                self.initializePaths(accountId)
            else:
                return

        with open(self.launcherSource, "r", encoding="utf-8", errors="ignore") as f:
            f.seek(0, 2)
            if f.tell() < self.launcherPointer:
                self.launcherPointer = 0
            
            f.seek(self.launcherPointer)
            while True:
                line = f.readline()
                if not line: break
                self.processLine(line, self.launcherOutput, silent=True)
            self.launcherPointer = f.tell()

    def watch(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        Logger.status("Made by foxud")
        Logger.status("Waiting for log...")

        while True:
            self.updateLauncherLive()
            if os.path.exists(self.filePath) and self.initialized:
                break
            time.sleep(0.5)

        alreadyExists = os.path.exists(self.filePath)
        with open(self.filePath, "r", encoding="utf-8", errors="ignore") as gameStream:
            if alreadyExists:
                gameStream.seek(0, 2)
            else:
                gameStream.seek(0)
            
            firstLogDetected = False
            while True:
                self.updateLauncherLive()
                currentLine = gameStream.readline()
                if not currentLine:
                    if os.path.exists(self.filePath):
                        if os.path.getsize(self.filePath) < gameStream.tell():
                            gameStream.seek(0)
                    time.sleep(0.1)
                    continue
                
                if not firstLogDetected:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    firstLogDetected = True
                
                if self.processLine(currentLine, self.outputFile, silent=False):
                    return True