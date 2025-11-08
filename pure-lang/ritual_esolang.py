import os
import subprocess
import webbrowser
import time
import re
import pygame
from pygame import gfxdraw

# ---- MEMORY / STATE ----
cells = [0] * 10
ptr = 0
variables = {}

# ---- Pygame setup ----
pygame.init()
screen = pygame.display.set_mode((400, 400))
pygame.display.set_caption("Ritual Visuals")
clock = pygame.time.Clock()
screen.fill((0,0,0))
pygame.display.flip()

# ---- COMMAND FUNCTIONS ----
def AMPLIFY(): global cells, ptr; cells[ptr]=(cells[ptr]+1)%256; print(f"[AMPLIFY] cell[{ptr}]={cells[ptr]}")
def DIMINISH(): global cells, ptr; cells[ptr]=(cells[ptr]-1)%256; print(f"[DIMINISH] cell[{ptr}]={cells[ptr]}")
def SHIFT(): global ptr; ptr=(ptr+1)%len(cells); print(f"[PTR] {ptr}")
def RETURN(): global ptr; ptr=(ptr-1)%len(cells); print(f"[PTR] {ptr}")
def CHIME(): print("\a", end="", flush=True); print("[CHIME]")
def PAUSE(sec="1"): time.sleep(float(sec)); print(f"[PAUSE] {sec}s")
def SUMMON(app): os.startfile(app) if os.path.exists(app) else subprocess.Popen(app, shell=True); print(f"[SUMMON] {app}")
def PORTAL(link): webbrowser.open(link); print(f"[PORTAL] {link}")
def INSCRIBE(val): print(f"[INSCRIBE] {val}")
def SCRIBE(var, val): variables[var] = eval(val); print(f"[SCRIBE] {var} = {variables[var]}")
def LIGHT(r="255", g="255", b="255"): screen.fill((int(r), int(g), int(b))); pygame.display.flip(); print(f"[LIGHT] {r},{g},{b}")
def FLASH(r="255", g="255", b="255", times="1"):
    for _ in range(int(times)):
        screen.fill((int(r), int(g), int(b))); pygame.display.flip(); time.sleep(0.2)
        screen.fill((0,0,0)); pygame.display.flip(); time.sleep(0.2)
    print(f"[FLASH] {r},{g},{b} x{times}")
def SIGIL(x="50", y="50", w="100", h="100", r="255", g="255", b="255"):
    pygame.draw.rect(screen, (int(r), int(g), int(b)), (int(x), int(y), int(w), int(h))); pygame.display.flip(); print(f"[SIGIL] at {x},{y} size {w}x{h}")
def ORB(x="200", y="200", rad="50", r="255", g="255", b="255"):
    gfxdraw.filled_circle(screen, int(x), int(y), int(rad), (int(r), int(g), int(b))); pygame.display.flip(); print(f"[ORB] at {x},{y} radius {rad}")
def CHANT(file): subprocess.Popen(file, shell=True); print(f"[CHANT] {file}")
def RIFT(app="blender"): subprocess.Popen(app, shell=True); print(f"[RIFT] {app}")
def ECHO(val): print(f"[ECHO] {val}")
def ARCANE(script_file): 
    if os.path.exists(script_file): run_script(script_file)
    else: print(f"[ARCANE] File not found: {script_file}")

# ---- COMMAND REGISTRY ----
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
    return eval(expr)

def run_lines(lines):
    i = 0
    while i < len(lines):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); return
        line = lines[i].strip()
        if not line or line.startswith("#"): i += 1; continue
        # Loops
        repeat_match = re.match(r"REPEAT (\d+) {", line)
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
        # Variables
        set_match = re.match(r"SET (\w+) (.+)", line)
        if set_match:
            var, expr = set_match.groups()
            variables[var] = evaluate_expr(expr)
            print(f"[SET] {var} = {variables[var]}")
            i += 1
            continue
        # Conditionals
        if_match = re.match(r"IF (.+) THEN (.+)", line)
        if if_match:
            cond, cmd = if_match.groups()
            if evaluate_expr(cond): run_lines([cmd])
            i += 1
            continue
        # Normal commands
        parts = line.split()
        cmd = parts[0].upper()
        args = parts[1:]
        if cmd in commands:
            try: commands[cmd](*args)
            except Exception as e: print(f"[ERROR] {line} -> {e}")
        else: print(f"[UNKNOWN] {cmd}")
        i += 1

def run_script(file):
    with open(file, "r") as f:
        lines = f.readlines()
    run_lines(lines)

# ---- MAIN ----
if __name__ == "__main__":
    script_file = input("Enter script filename (e.g., ritual.txt): ")
    if os.path.exists(script_file): run_script(script_file)
    else: print(f"File not found: {script_file}")
