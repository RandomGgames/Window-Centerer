from PIL import Image, ImageDraw
from pystray import Icon, MenuItem, Menu
from screeninfo import get_monitors
import datetime
import keyboard
import logging
import os
import pathlib
import pyautogui
import socket
import sys
import threading
import time
import typing

import logging
logger = logging.getLogger(__name__)

"""
Center Window Script.py

This script, when ctrl, shift, alt, and c are all pressed at the same time, moves the active window to the center of the screen.
"""

def get_monitor_for_window(window):
    """
    Determine which monitor the window is primarily located in by using its center point.
    """
    monitors = get_monitors()
    monitor_for_window = monitors[0]
    for monitor in monitors:
        if monitor.x <= window.centerx < monitor.x + monitor.width and monitor.y <= window.centery < monitor.y + monitor.height:
            monitor_for_window = monitor
            break
    logger.debug(f'Monitor: "{monitor_for_window.name[4:]}" {monitor_for_window.width} x {monitor_for_window.height}')
    return monitor_for_window

def get_active_window():
    """
    Gets the active window
    """
    window = pyautogui.getActiveWindow()
    if window:
        if window.isActive:
            logger.debug(f'Title: "{window.title}"')
            logger.debug(f'Window Center: ({window.centerx}, {window.centery})')
            logger.debug(f'Width x Height = {window.width} x {window.height}')
            return window
    logger.warning(f'Could not retrieve active window.')
    return None

def calculate_new_window_position(window, monitor):
    """
    Calculates the position a window needs to be moved to to be in the center of the monitor
    """
    window_width, window_height = window.size
    new_x = monitor.x + (monitor.width - window_width) // 2
    new_y = monitor.y + (monitor.height - window_height) // 2
    logger.debug(f'New X Y screen position: ({new_x}, {new_y})')
    return new_x, new_y

def move_window(window, x, y):
    """
    Moves a window to the specified X Y coordinates
    """
    window.moveTo(x, y)
    logger.debug(f'Moved window "{window.title}" to ({x}, {y})')

def center_window():
    window = get_active_window()
    if window is None: return
    
    monitor = get_monitor_for_window(window)
    new_x, new_y = calculate_new_window_position(window, monitor)
    move_window(window, new_x, new_y)
    logger.info(f'Centered window.')

def keyboard_event(event):
    if event.event_type == 'down':
        if all(keyboard.is_pressed(key) for key in ['ctrl', 'shift', 'alt', 'c']):
            logger.debug(f'Hotkeys pressed.')
            try:
                center_window()
            except Exception as e:
                logger.debug(f'An error occured while attempting to center the active window: {repr(e)}')

def create_image() -> Image:
    logger.debug(f'Creating system tray icon image')
    # Create an image for the icon (you can customize it)
    image = Image.new('RGB', (64, 64), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 64, 64), fill=(0, 0, 0))  # A simple black square
    return image

def load_image(path) -> Image:
    image = Image.open(path)
    logger.debug(f'Loaded image at path "{path}"')
    return image

def on_exit(icon, item):
    icon.stop()
    logger.debug('System tray icon stopped.')

def setup_tray_icon():
    logger.debug(f'Starting up system tray icon')
    image = load_image('system_tray_icon.png')
    menu = Menu(MenuItem('Exit', on_exit))
    icon = Icon('CenterWindowScript', image, menu=menu)
    logger.debug(f'Started system tray icon')
    icon.run()
    global exit_flag
    exit_flag = True
    logger.debug('Exit flag flagged')

def main():
    logger.info(f'Starting new session.')
    
    tray_thread = threading.Thread(target=setup_tray_icon, daemon=True)
    tray_thread.start()
    
    keyboard.hook(keyboard_event)
    global exit_flag
    exit_flag = False
    while not exit_flag:
        time.sleep(1)
    
def setup_logging(
        logger: logging.Logger,
        log_file_path: typing.Union[str, os.fspath],
        number_of_logs_to_keep: typing.Union[int, None] = None,
        console_logging_level = logging.DEBUG,
        file_logging_level = logging.DEBUG,
        log_message_format = '%(asctime)s.%(msecs)03d %(levelname)s [%(funcName)s]: %(message)s',
        date_format = '%Y-%m-%d %H:%M:%S'):
    # Initialize logs folder
    log_dir = os.path.dirname(log_file_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir) # Create logs dir if it does not exist
    
    # Limit # of logs in logs folder
    if number_of_logs_to_keep is not None:
        log_files = sorted([f for f in os.listdir(log_dir) if f.endswith('.log')], key=lambda f: os.path.getmtime(os.path.join(log_dir, f)))
        if len(log_files) >= number_of_logs_to_keep:
            for file in log_files[:len(log_files) - number_of_logs_to_keep + 1]:
                os.remove(os.path.join(log_dir, file))
    
    logger.setLevel(file_logging_level)  # Set the overall logging level
    
    # File Handler for date-based log file
    file_handler_date = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler_date.setLevel(file_logging_level)
    file_handler_date.setFormatter(logging.Formatter(log_message_format))
    logger.addHandler(file_handler_date)
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_logging_level)
    console_handler.setFormatter(logging.Formatter(log_message_format, datefmt=date_format))
    logger.addHandler(console_handler)
    
    # Set specific logging levels
    #logging.getLogger('requests').setLevel(logging.INFO)
    #logging.getLogger('sys').setLevel(logging.CRITICAL)
    #logging.getLogger('urllib3').setLevel(logging.INFO)

if __name__ == "__main__":
    pc_name = socket.gethostname()
    script_name = pathlib.Path(os.path.basename(__file__)).stem
    log_dir = pathlib.Path(f"{script_name} Logs")
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_file_name = pathlib.Path(f'{timestamp}_{pc_name}.log')
    log_file_path = os.path.join(log_dir, log_file_name)
    setup_logging(logger, log_file_path, number_of_logs_to_keep=10)
    
    error = 0
    try:
        main()
    except Exception as e:
        logger.warning(f'A fatal error has occurred due to {repr(e)}')
        error = 1
    finally:
        exit(error)