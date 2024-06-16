import pyautogui
import keyboard
import logging
import os
import sys
logger = logging.getLogger(__name__)

__version__ = '1.0.0'

def keyboard_event(event):
    if event.event_type == 'down':
        if all(keyboard.is_pressed(key) for key in ['ctrl', 'shift', 'alt', 'c']):
            center_window()

def center_window():
    logger.debug(f'Centering window...')
    
    screen_width, screen_height = pyautogui.size()
    logger.debug(f'{screen_width = }')
    logger.debug(f'{screen_height = }')
    
    window = pyautogui.getActiveWindow()
    window_width, window_height = window.size
    logger.debug(f'{window_width = }')
    logger.debug(f'{window_height = }')
    
    new_x = (screen_width - window_width) // 2
    new_y = (screen_height - window_height) // 2
    logger.debug(f'{new_x = }')
    logger.debug(f'{new_y = }')
    
    pyautogui.getActiveWindow().moveTo(new_x, new_y)
    logger.info(f'Centered window "{window.title}".')

def main():
    keyboard.hook(keyboard_event)
    keyboard.wait()

if __name__ == "__main__":
    if os.path.exists('latest.log'):
        open('latest.log', 'w').close()
    
    logger.setLevel(logging.DEBUG)
    
    file_handler = logging.FileHandler('latest.log', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    logger.addHandler(file_handler)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    logger.addHandler(console_handler)
    
    try:
        main()
    except Exception as e:
        logger.exception(f'The script could no longer continue due to {repr(e)}.')
        exit(1)