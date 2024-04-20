# Setup

This script requires:
- Python 
- Hyperdash, at the path specified by HYPERDASH_PATH (Change it if you are using the Steam version)
- Packages specified in requirements.txt. 

To install the packages specified in requirements.txt, run: 
```bash
pip install -r requirements.txt
```

# Running the Program

```bash
python follow.py
```

# Future Features
- Support for password-locked lobbies
- Persistant settings (players to follow, game install directory)
- Menu to change persistant settings
- Follow any players matching a specific team tag
- Follow the player through map changes
- Follow the player through different lobbies
- Multithreading to speed up image analysis