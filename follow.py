import pyautogui
import pygetwindow as gw
import time
import subprocess
import requests
import json
from ctypes import windll
import win32gui

HYPERDASH_PATH = "C:/Program Files/Oculus/Software/Software/triangle-factory-hyper-dash/HyperDash.exe"
W_WIDTH = 800
W_HEIGHT = 600

def window_is_fullscreen():
    user32 = windll.user32
    full_screen_rect = (0, 0, user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))
    try:
        hWnd = user32.GetForegroundWindow()
        rect = win32gui.GetWindowRect(hWnd)
        return rect == full_screen_rect
    except:
        return False

def get_server_name(player_to_find):
    response = requests.get('https://dashlistapi.hyperdash.dev/')

    if response.status_code == 200:
        server_list = json.loads(response.text)
        for server in server_list.values():
            for player in server['players']:
                if player['name'].lower() == player_to_find.lower():
                    print(f"Found {player_to_find} in server {server['name']}")
                    return server['name']
    else:
        print("ERROR: UNABLE TO REACH dashlistapi.hyperdash.dev")
        return
    print(f"ERROR: Player {player_to_find} is not online.")

def wait_for_hyperdash_window():
    print("Waiting for HD window to appear")
    while True:
        for w in gw.getWindowsWithTitle("Hyper Dash"):
            print("FOUND", w)
            return w
        time.sleep(0.1)

def resize_hyperdash_window(window, width, height):
    if window_is_fullscreen():
        pyautogui.hotkey('Alt', 'Enter')
    print(f"Resizing to {width}x{height}")
    window.resizeTo(width, height)
    return window
    
def wait_for_black_alternation():
    print("Waiting for game to load")
    while (True):
        if(pyautogui.pixelMatchesColor(150, 150, (0,0,0))):
            while(True):
                if(not pyautogui.pixelMatchesColor(150, 150, (0,0,0))):
                    print("Game loaded")
                    return
                time.sleep(0.1)
        time.sleep(0.1)

server = None
while server == None:
    player_to_find = input("Please input the name of the player you want to find: ")
    server = get_server_name(player_to_find)

# Start Hyperdash
args = ["-vrmode", "None", "-novr"]
process = subprocess.Popen([HYPERDASH_PATH, *args], shell=True)

window = wait_for_hyperdash_window()
window = resize_hyperdash_window(window, W_WIDTH, W_HEIGHT)

#Window positional offset
x = window.left
y = window.top

wait_for_black_alternation()
print("Joining", server)

# Set FOV to 90 degrees
pyautogui.press('b')
pyautogui.click(729 + x, 264 + y)
pyautogui.press('b')

pyautogui.click(500 + x, 325 + y) #Server Browser
pyautogui.click(x=333 + x, y=366 + y) # Click Server Search box
pyautogui.typewrite(server) # Server search
time.sleep(0.5)
pyautogui.click(400 + x, 287 + y) # Click Server in list
pyautogui.click(465 + x, y=396 + y) # Click Join Game Button
pyautogui.hotkey('Alt', 'Enter') # Fullscreen
wait_for_black_alternation()
pyautogui.press('space') # Drone Mode --> follow mode
