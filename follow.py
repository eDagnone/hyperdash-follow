import pyautogui
import pygetwindow as gw
import time
import subprocess
import pytesseract
import requests
import json
from pathlib import Path

HYPERDASH_PATH = "C:/Program Files/Oculus/Software/Software/triangle-factory-hyper-dash/HyperDash.exe"

pyautogui.PAUSE = 0.5
pytesseract.pytesseract.tesseract_cmd = 'Tesseract-OCR/tesseract.exe'

def wait_for_hyperdash_window()-> gw.Win32Window:
    print("Waiting for HD window to appear")
    while True:
        for w in gw.getWindowsWithTitle("Hyper Dash"):
            print("FOUND", w)
            w.activate()
            return w
        time.sleep(0.1)

def resize_hyperdash_window(window: gw.Win32Window, width: int, height: int):
    while window.size.width != width or window.size.height != height:
        pyautogui.hotkey('Alt', 'Enter')
        time.sleep(0.1)
        print(f"Resizing to {width}x{height}")
        window.resizeTo(width, height)
        print("Size is now", window.size)
    return window
    
def wait_for_black_alternation(x_offset: int, y_offset: int):
    print("Waiting for game to load")
    while (True):
        if(pyautogui.pixelMatchesColor(150+ x_offset, 150 + y_offset, (0,0,0))):
            while(True):
                if(not pyautogui.pixelMatchesColor(150+ x_offset, 150 + y_offset, (0,0,0))):
                    print("Game loaded")
                    return
                time.sleep(0.1)
        time.sleep(0.1)

def get_player_index(region:list[tuple[int,  int, int, int]], player_to_follow: str):
    print("Capturing Images")
    for _ in range(5): #Retry 5x if needed
        for i, region in enumerate(slot_regions, start=1):
            image = pyautogui.screenshot(region=region)
            image = image.convert('L', dither=None)   # Convert to grayscale
            text = pytesseract.image_to_string(image, config=r'--psm 11 --oem 1 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789?!.,$\'\" ').strip()
            Path("images").mkdir(exist_ok=True)
            image.save(f"images/slot{i}.png")
            print(f"Slot {i%10}:\t{text}")  # Debugging purposes
            for j in[4,3,2,0]: #account for clan tags
                if(text[j:13] == player_to_follow.replace(" ",  "")[:13-j].strip()): #TODO: Add fuzzy matching
                    print("FOUND at ", i%10)
                    return i%10
        time.sleep(2)

def get_server_list():
    response = requests.get('https://dashlistapi.hyperdash.dev/')
    if response.status_code == 200:
        return json.loads(response.text).values()
    else:
        print("ERROR: UNABLE TO REACH dashlistapi.hyperdash.dev")
def get_server_by_player(server_list, player_to_find):
    for server in server_list:
        player = get_player_details(server, player_to_find)
        if(player is not None):
            print(f"Found {player_to_find} in lobby {server['name']}")
            return server
    print(f"ERROR: Player {player_to_find} is not online.")

def get_player_details(server, player_to_find):
    for player in server['players']:
        if player['name'].lower() == player_to_find.lower():
            return player

server = None
server_list = get_server_list()
while server == None:
    player_to_find = input("Please input the name of the player to spectate: ")
    server = get_server_by_player(server_list, player_to_find)
    if server is not None:
        if server['password']:
            print("Sorry, password-locked servers are not supported yet.")
            server = None
        else:
            player = get_player_details(server, player_to_find)
            if player['tag'] != '':
                player_to_find = player['tag'] + " " + player['name']
    
    #No support for password locked servers yet.



    
# Start Hyperdash
args = ["-vrmode", "None", "-novr"]
process = subprocess.Popen([HYPERDASH_PATH, *args], shell=True)

window = wait_for_hyperdash_window()
pyautogui.hotkey('Alt', 'Enter') # Un-Fullscreen
window = resize_hyperdash_window(window, 800, 600)

#Window positional offset
x = window.left
y = window.top

wait_for_black_alternation(x,y)
print("Joining", server['name'])

# Set FOV to 90 degrees
pyautogui.hotkey('Alt', 'Enter') # Un-Fullscreen
time.sleep(0.1)
window = resize_hyperdash_window(window, 800, 600)
time.sleep(0.1)
pyautogui.press('b')
time.sleep(0.1)
pyautogui.click(729 + x, 264 + y)
time.sleep(0.5)
pyautogui.press('b')

pyautogui.click(500 + x, 325 + y) #Server Browser
pyautogui.click(x=333 + x, y=366 + y) # Click Server Search box
pyautogui.typewrite(server['name']) # Server search
time.sleep(0.5)
pyautogui.click(400 + x, 287 + y) # Click Server in list
pyautogui.click(465 + x, y=396 + y) # Click Join Game Button
wait_for_black_alternation(x,y) #Load into lobby

#Get index of player and press key
window = resize_hyperdash_window(window, 1366,1550)
x = window.left
y = window.top
slot_regions  = [#x,y,w,h
    (58 + x, 76 + y, 182, 31),
    (256 + x, 76 + y, 182, 31),
    (58 + x, 206 + y, 182, 31),
    (256 + x, 206 + y, 182, 31),
    (58 + x, 333 + y, 182, 31),
    #Team 2 is not shuffled properly (HD spectator bug)
    (1129 + x, 333 + y, 182, 31),
    (929 + x, 206 + y, 182, 31),
    (1129 + x, 206 + y, 182, 31),
    (929 + x, 76 + y, 182, 31),
    (1129 + x, 76 + y, 182, 31),
]
time.sleep(5)
player_index = get_player_index(slot_regions, player_to_find)
if(player_index is not None):
    pyautogui.press(str(player_index))
else:
    print(f"Could not find {player_to_find}. Player may have left.")
pyautogui.hotkey('Alt', 'Enter') # Fullscreen
