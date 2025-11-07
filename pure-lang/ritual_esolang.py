#!/usr/bin/env python3
"""
Ritual esolang interpreter + visuals (PURE v0.1)
- Commands: AMPLIFY, DIMINISH, SHIFT, RETURN, CHIME, PAUSE, SUMMON, PORTAL, INSCRIBE, SCRIBE
            LIGHT, FLASH, SIGIL, ORB, CHANT, RIFT, ECHO, ARCANE
- Optional headless mode for testing or server execution
"""

import os
import subprocess
import webbrowser
import time
import re
import sys

# ---- Headless / Pygame setup ----
HEADLESS = "--nogui" in sys.argv
if not HEADLESS:
    import pygame
    from pygame import gfxdraw
    pygame.init()
    screen = pygame.display.set_mode((400, 400))
    pygame.display.set_caption("Ritual Visuals")
    clock = pygame.time.Clock()
    screen.fill((0, 0, 0))
    pygame.display.flip()

# ---- MEMORY / STATE ----
cells = [0] * 10
ptr = 0
variables = {}

# ---- COMMAND FUNCTIONS ----
def AMPLIFY(): 
    global cells, ptr
    cells[ptr] = (cells[ptr] + 1) % 256
    print(f"[AMPLIFY] cell[{ptr}]={cells[ptr]}")

def DIMINISH(): 
    global cells, ptr
    cells[ptr] = (cells[ptr] - 1) % 256
    print(f"[DIMINISH] cell[{ptr}]={cells[ptr]}")

def SHIFT(): 
    global ptr
    ptr = (ptr + 1) % len(cells)
    print(f"[PTR] {ptr}")

def RETURN(): 
    global ptr
    ptr = (ptr - 1) % len(cells)
    print(f"[PTR] {ptr}")

def CHIME(): 
    print("\a", end="", flush=True)
    print("[CHIME]")

def PAUSE(sec="1"): 
    time.sleep(float(sec))
    print(f"[PAUSE] {sec}s")

def SUMMON(app): 
    try:
        if os.path.exists(app):
            subprocess.Popen([app], shell=True)
        elif re.match(r"^https?://", app):
            webbrowser.open(app)
        else:
            subprocess.Popen(app, shell=True)
    except Exception as e:
        print(f"[SUMMON ERROR] {e}")
    print(f"[SUMMON] {app}")

def PORTAL(link): 
    webbrowser.open(link)
    print(f"[PORTAL] {link}")

def INSCRIBE(val): 
    print(f"[INSCRIBE] {val}")

def SCRIBE(var, val): 
    try:
        variables[var] = eval(val, {}, variables)
    except Exception:
        variables[var] = val
    print(f"[SCRIBE] {var} = {variables[var]}")

def LIGHT(r="255", g="255", b="255"): 
    if not HEADLESS:
        screen.fill((int(r), int(g), int(b)))
        pygame.display.flip()
    print(f"[LIGHT] {r},{g},{b}")

def FLASH(r="255", g="255", b="255", times="1"):
    if not HEADLESS:
        for _ in range(int(times)):
            screen.fill((int(r), int(g), int(b)))
            pygame.display.flip()
            time.sleep(0.2)
            screen.fill((0,0,0))
            pygame.display.flip()
            time.sleep(0.2)
    print(f"[FLASH] {r},{g},{b} x{times}")

def SIGIL(x="50", y="50", w="100", h="100", r="255", g="255", b="255"):
    if not HEADLESS:
        pygame.draw.rect(screen, (int(r), int(g), int(b)), (int(x), int(y), int(w), int(h)))
        pygame.display.flip()
    print(f"[SIGIL] at {x},{y} size {w}x{h}")

def ORB(x="200", y="200", rad="50", r="255", g="255", b="255"):
    if not HEADLESS:
        gfxdraw.filled_circle(screen, int(x), int(y), int(rad), (int(r), int(g), int(b)))
        pygame.display.flip()
    print(f"[ORB] at {x},{y} radius {rad}")

def CHANT(file): 
    try:
        subprocess.Popen(file, shell=True)
    except Exception as e:
        print(f"[CHANT ERROR] {e}")
    print(f"[CHANT] {file}")

def RIFT(app="blender"): 
    try:
        subprocess.Popen(app, shell=True)
    except Exception as e:
        print(f"[RIFT ERROR] {e}")
    print(f"[RIFT] {app}")

def ECHO(val): 
    print(f"[ECHO] {val}")

def ARCANE(script_file): 
    if os.path.exists(script_file):
        run_script(script_file)
    else:
        print(f"[ARCANE] File not found: {script_file}")

# ---- COMMAND REGISTRY ----
commands = {
    "AMPLIFY": AMPLIFY, "DIMINISH": DIMINISH, "SHIFT": SHIFT, "RETURN": RETURN,
    "CHIME": CHIME, "PAUSE": PAUSE, "SUMMON": SUMMON, "PORTAL": PORTAL,
    "INSCRIBE": INSCRIBE, "SCRIBE": SCRIBE, "LIGHT": LIGHT, "FLASH": FLASH,
    "SIGIL": SIGIL, "ORB": ORB, "CHANT": CHANT, "RIFT": RIFT, "ECHO": ECHO,
    "ARCANE": ARCANE
}

# ---- HELPER FUNCTIONS ----
def run_lines(lines):
    i = 0
    while i < len(lines):
        if not HEADLESS:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
        line = lines[i].strip()
        if not line or line.startswith("#"):
            i += 1
            continue
        parts = re.split(r'\s+', line)
        cmd = parts[0].upper()
        args = parts[1:]
        if cmd in commands:
            try:
                commands[cmd](*args)
            except Exception as e:
                print(f"[ERROR] {line} -> {e}")
        else:
            print(f"[UNKNOWN] {cmd}")
        i += 1

def run_script(file):
    file = os.path.expanduser(file)
    if not os.path.isfile(file):
        print(f"File not found: {file}")
        return
    with open(file, "r") as f:
        lines = f.readlines()
    run_lines(lines)

# ---- MAIN ENTRY ----
if __name__ == "__main__":
    args = [arg for arg in sys.argv[1:] if arg != "--nogui"]
    if args:
        run_script(args[0])
    else:
        fname = input("Enter script filename: ").strip()
        run_script(fname)
