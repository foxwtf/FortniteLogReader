class Logger:
    cyan = "\033[1;96m"
    yellow = "\033[1;93m"
    red = "\033[1;91m"
    green = "\033[1;92m"
    reset = "\033[0m"

    @staticmethod
    def info(msg, isChild=False):
        if isChild:
            print(f"      {msg}")
        else:
            print(f"[{Logger.cyan}LOG{Logger.reset}] [{Logger.green}SUCCESS{Logger.reset}] {msg}")

    @staticmethod
    def warning(msg, isChild=False):
        if isChild:
            print(f"      {msg}")
        else:
            print(f"[{Logger.cyan}LOG{Logger.reset}] [{Logger.yellow}WARNING{Logger.reset}] {msg}")

    @staticmethod
    def error(msg, isChild=False):
        if isChild:
            print(f"      {msg}")
        else:
            print(f"[{Logger.cyan}LOG{Logger.reset}] [{Logger.red}ERROR{Logger.reset}] {msg}")

    @staticmethod
    def status(msg):
        print(f"[{Logger.cyan}LOG{Logger.reset}] {msg}")