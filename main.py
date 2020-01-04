from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

from src import Main
# ------------------------------------------------------------------------------
# TEMP
# ------------------------------------------------------------------------------
URL = 'https://www.youtube.com/watch?v=dCdxj-3IrWM'
URL_PLAYLIST = 'https://www.youtube.com/watch?v=qz7tCZE_3wA&list=RDqz7tCZE_3wA&start_radio=1'
QUERY_URL = 'https://www.youtube.com/results?search_query=y%C3%AAu+ch%C3%A2u+d%C6%B0%C6%A1ng'


if __name__ == '__main__':
    main = Main()
    main._running()