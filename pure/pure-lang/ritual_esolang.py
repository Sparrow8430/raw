#!/usr/bin/env python3
# pure/pure-lang/ritual_esolang.py
import os
import subprocess
import webbrowser
import time
import re
import pygame
from pygame import gfxdraw
import shlex
import ast
import sys

# ---- MEMORY / STATE ----
cells = [0] * 16
ptr = 0
variables = {}

# ---- Pygame setup ----
pygame.init()
SCREEN_W, SCREEN_H = 600, 600
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Ritual Visuals")
clock = pygame.time.Clock()
screen.fill((0, 0, 0))
pygame.display.flip()

# ---- COMMAND FUNCTIONS ----
def AMPLIFY(): global cells, ptr; cells[ptr]=(cells[ptr]+1)%256; print(f"[AMPLIFY] cell[{ptr}]={cells[ptr]}")
def DIMINISH(): global cells, ptr; cells[ptr]=(cells[ptr]-1)%256; print(f"[DIMINISH] cell[{ptr}]={cells[ptr]}")
def SHIFT(): global ptr; ptr=(ptr+1)%len(cells); print(f"[PTR] {ptr}")
def RETURN(): global ptr; ptr=(ptr-1)%len(cells); print(f"[PTR] {ptr}")
def CHIME(): print("\a", end="", flush=True); print("[CHIME]")
def PAUSE(sec="1"): time.sleep(float(sec)); print(f"[PAUSE] {sec}s")
def SUMMON(app):
    # cross-platform: try open with xdg-open or run the command
    try:
        if os.path.exists(app):
            if sys.platform.startswith("win"):
                os.startfile(app)
            else:
                subprocess.Popen(shlex.split(app))
        else:
            # try opening as a shell command
            subprocess.Popen(app, shell=True)
    except Exception as e:
        print("[SUMMON ERR]", e)
    print(f"[SUMMON] {app}")

def PORTAL(link): 
    try:
        webbrowser.open(link)
    except Exception as e:
        print("[PORTAL ERR]", e)
    print(f"[PORTAL] {link}")

def INSCRIBE(val): print(f"[INSCRIBE] {val}")
def SCRIBE(var, val):
    try:
        variables[var] = ast.literal_eval(val)
    except Exception:
        # fallback: store raw string
        variables[var] = val
    print(f"[SCRIBE] {var} = {variables[var]}")

def LIGHT(r="255", g="255", b="255"):
    screen.fill((int(r), int(g), int(b))); pygame.display.flip()
    print(f"[LIGHT] {r},{g},{b}")

def FLASH(r="255", g="255", b="255", times="1"):
    for _ in range(int(times)):
        screen.fill((int(r), int(g), int(b))); pygame.display.flip(); time.sleep(0.18)
        screen.fill((0,0,0)); pygame.display.flip(); time.sleep(0.12)
    print(f"[FLASH] {r},{g},{b} x{times}")

def SIGIL(x="50", y="50", w="100", h="100", r="255", g="255", b="255"):
    pygame.draw.rect(screen, (int(r), int(g), int(b)), (int(x), int(y), int(w), int(h))); pygame.display.flip()
    print(f"[SIGIL] at {x},{y} size {w}x{h}")

def ORB(x="200", y="200", rad="50", r="255", g="255", b="255"):
    gfxdraw.filled_circle(screen, int(x), int(y), int(rad), (int(r), int(g), int(b))); pygame.display.flip()
    print(f"[ORB] at {x},{y} radius {rad}")

def CHANT(file): 
    try:
        subprocess.Popen(shlex.split(file))
    except Exception:
        subprocess.Popen(file, shell=True)
    print(f"[CHANT] {file}")

def RIFT(app="blender"): 
    try:
        subprocess.Popen(shlex.split(app))
    except Exception:
        subprocess.Popen(app, shell=True)
    print(f"[RIFT] {app}")

def ECHO(val): print(f"[ECHO] {val}")

def ARCANE(script_file):
    if os.path.exists(script_file): run_script(script_file)
    else: print(f"[ARCANE] File not found: {script_file}")

commands = {
    "AMPLIFY": AMPLIFY, "DIMINISH": DIMINISH, "SHIFT": SHIFT, "RETURN": RETURN,
    "CHIME": CHIME, "PAUSE": PAUSE, "SUMMON": SUMMON, "PORTAL": PORTAL,
    "INSCRIBE": INSCRIBE, "SCRIBE": SCRIBE, "LIGHT": LIGHT, "FLASH": FLASH,
    "SIGIL": SIGIL, "ORB": ORB, "CHANT": CHANT, "RIFT": RIFT, "ECHO": ECHO,
    "ARCANE": ARCANE
}

# ---- Helper functions ----
def evaluate_expr(expr):
    for var in variables:
        expr = expr.replace(var, str(variables[var]))
    try:
        return eval(expr, {"__builtins__": None}, {})
    except Exception:
        return expr

def run_lines(lines, stop_on_close=False):
    i = 0
    running = True
    while i < len(lines) and running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                if stop_on_close:
                    return "QUIT"
        line = lines[i].strip()
        if not line or line.startswith("#"):
            i += 1; continue

        # Loops: REPEAT N { ... }
        repeat_match = re.match(r"REPEAT (\d+) {", line, re.I)
        if repeat_match:
            count = int(repeat_match.group(1))
            block = []
            depth = 1
            i += 1
            while i < len(lines) and depth > 0:
                l = lines[i].strip()
                if l.endswith("{"): depth += 1
                if l == "}": depth -= 1
                if depth > 0: block.append(l)
                i += 1
            for _ in range(count): run_lines(block)
            continue

        # Variables SET var expr
        set_match = re.match(r"SET (\w+) (.+)", line, re.I)
        if set_match:
            var, expr = set_match.groups()
            variables[var] = evaluate_expr(expr)
            print(f"[SET] {var} = {variables[var]}")
            i += 1
            continue

        # IF cond THEN command
        if_match = re.match(r"IF (.+) THEN (.+)", line, re.I)
        if if_match:
            cond, cmd = if_match.groups()
            try:
                if eval(cond, {"__builtins__": None}, variables):
                    run_lines([cmd])
            except Exception as e:
                print("[IF ERR]", e)
            i += 1
            continue

        # Normal commands
        parts = line.split()
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
        clock.tick(60)  # keep pygame responsive
    return "DONE"

def run_script(file):
    with open(file, "r") as f:
        lines = f.readlines()
    return run_lines(lines, stop_on_close=True)

# ---- MAIN ----
if __name__ == "__main__":
    if len(sys.argv) > 1:
        script_file = sys.argv[1]
    else:
        script_file = input("Enter script filename (e.g., ritual.txt): ")
    if os.path.exists(script_file):
        print(run_script(script_file))
    else:
        print(f"File not found: {script_file}")
