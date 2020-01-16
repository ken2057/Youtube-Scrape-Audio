from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

from src import Main

if __name__ == '__main__':
    main = Main()
    main._running()