#!/usr/bin/env python3
"""
PURE Ritual Language Interpreter
A visual esoteric programming language with graphics and system integration
Version: 0.2 (Security hardened)
"""

import os
import subprocess
import webbrowser
import time
import re
import sys
import ast
from typing import Dict, List, Any

try:
    import pygame
    from pygame import gfxdraw
except ImportError:
    print("Error: pygame not installed. Install with: pip install pygame")
    sys.exit(1)

# ---- GLOBAL STATE ----
cells = [0] * 10
ptr = 0
variables: Dict[str, Any] = {}
screen = None
clock = None
running = True

# ---- CONFIGURATION ----
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 400
MAX_LOOP_ITERATIONS = 1000
ALLOWED_SCHEMES = ['http', 'https']

# ---- Pygame Initialization ----
def init_display():
    """Initialize pygame display"""
    global screen, clock
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("PURE Ritual Visuals")
    clock = pygame.time.Clock()
    screen.fill((0, 0, 0))
    pygame.display.flip()
    print("[*] Display initialized")


def check_pygame_events():
    """Process pygame events to prevent freezing"""
    global running
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit(0)


# ---- SAFE EVALUATION ----
def safe_eval(expr: str) -> Any:
    """
    Safely evaluate mathematical expressions
    Only allows: numbers, basic operators, and defined variables
    """
    # Substitute variables
    for var_name, var_value in variables.items():
        expr = expr.replace(var_name, str(var_value))
    
    try:
        # Parse to AST
        node = ast.parse(expr, mode='eval')
        
        # Check for dangerous operations
        for child in ast.walk(node):
            if not isinstance(child, (
                ast.Expression, ast.Load, ast.BinOp, ast.UnaryOp,
                ast.Num, ast.Constant, ast.Add, ast.Sub, ast.Mult,
                ast.Div, ast.Mod, ast.Pow, ast.USub, ast.UAdd
            )):
                raise ValueError(f"Forbidden operation: {child.__class__.__name__}")
        
        # Evaluate safely
        result = eval(compile(node, '<string>', 'eval'), {"__builtins__": {}}, {})
        return result
    
    except Exception as e:
        print(f"[ERROR] Expression evaluation failed: {e}")
        return 0


def validate_int(value: str, min_val: int = 0, max_val: int = 1000) -> int:
    """Validate and clamp integer values"""
    try:
        num = int(float(value))
        return max(min_val, min(max_val, num))
    except ValueError:
        print(f"[ERROR] Invalid number: {value}")
        return min_val


def validate_color(r: str, g: str, b: str) -> tuple:
    """Validate RGB color values"""
    return (
        validate_int(r, 0, 255),
        validate_int(g, 0, 255),
        validate_int(b, 0, 255)
    )


# ---- COMMAND FUNCTIONS ----

def AMPLIFY():
    """Increment current cell"""
    global cells, ptr
    cells[ptr] = (cells[ptr] + 1) % 256
    print(f"[AMPLIFY] cell[{ptr}] = {cells[ptr]}")


def DIMINISH():
    """Decrement current cell"""
    global cells, ptr
    cells[ptr] = (cells[ptr] - 1) % 256
    print(f"[DIMINISH] cell[{ptr}] = {cells[ptr]}")


def SHIFT():
    """Move pointer right"""
    global ptr
    ptr = (ptr + 1) % len(cells)
    print(f"[SHIFT] ptr -> {ptr}")


def RETURN():
    """Move pointer left"""
    global ptr
    ptr = (ptr - 1) % len(cells)
    print(f"[RETURN] ptr -> {ptr}")


def CHIME():
    """System beep"""
    print("\a", end="", flush=True)
    print("[CHIME]")


def PAUSE(sec: str = "1"):
    """Pause execution"""
    duration = validate_int(sec, 0, 60)
    time.sleep(duration)
    print(f"[PAUSE] {duration}s")


def SUMMON(app: str):
    """
    Launch an application (RESTRICTED)
    Only allows specific safe applications
    """
    # Whitelist of allowed applications
    allowed_apps = {
        'notepad': ['notepad.exe'] if os.name == 'nt' else ['gedit'],
        'calculator': ['calc.exe'] if os.name == 'nt' else ['gnome-calculator'],
        'terminal': ['cmd.exe'] if os.name == 'nt' else ['gnome-terminal'],
    }
    
    if app.lower() in allowed_apps:
        try:
            subprocess.Popen(allowed_apps[app.lower()])
            print(f"[SUMMON] Launched {app}")
        except Exception as e:
            print(f"[ERROR] Failed to summon {app}: {e}")
    else:
        print(f"[ERROR] Application '{app}' not in whitelist")


def PORTAL(link: str):
    """Open a URL in browser (RESTRICTED)"""
    # Basic URL validation
    if not any(link.startswith(f"{scheme}://") for scheme in ALLOWED_SCHEMES):
        print(f"[ERROR] Invalid URL scheme. Must be http:// or https://")
        return
    
    # Prevent javascript: and data: schemes
    if link.startswith(('javascript:', 'data:', 'file:')):
        print(f"[ERROR] Forbidden URL scheme")
        return
    
    try:
        webbrowser.open(link)
        print(f"[PORTAL] Opened {link}")
    except Exception as e:
        print(f"[ERROR] Failed to open portal: {e}")


def INSCRIBE(val: str):
    """Print a value"""
    print(f"[INSCRIBE] {val}")


def SCRIBE(var: str, val: str):
    """Set a variable (SAFE)"""
    result = safe_eval(val)
    variables[var] = result
    print(f"[SCRIBE] {var} = {result}")


def LIGHT(r: str = "255", g: str = "255", b: str = "255"):
    """Fill screen with color"""
    check_pygame_events()
    color = validate_color(r, g, b)
    screen.fill(color)
    pygame.display.flip()
    print(f"[LIGHT] RGB{color}")


def FLASH(r: str = "255", g: str = "255", b: str = "255", times: str = "1"):
    """Flash screen with color"""
    check_pygame_events()
    color = validate_color(r, g, b)
    count = validate_int(times, 1, 10)
    
    for _ in range(count):
        screen.fill(color)
        pygame.display.flip()
        time.sleep(0.2)
        screen.fill((0, 0, 0))
        pygame.display.flip()
        time.sleep(0.2)
    
    print(f"[FLASH] RGB{color} x{count}")


def SIGIL(x: str = "50", y: str = "50", w: str = "100", h: str = "100",
          r: str = "255", g: str = "255", b: str = "255"):
    """Draw a rectangle"""
    check_pygame_events()
    pos_x = validate_int(x, 0, SCREEN_WIDTH)
    pos_y = validate_int(y, 0, SCREEN_HEIGHT)
    width = validate_int(w, 1, SCREEN_WIDTH)
    height = validate_int(h, 1, SCREEN_HEIGHT)
    color = validate_color(r, g, b)
    
    pygame.draw.rect(screen, color, (pos_x, pos_y, width, height))
    pygame.display.flip()
    print(f"[SIGIL] at ({pos_x},{pos_y}) size {width}x{height} RGB{color}")


def ORB(x: str = "200", y: str = "200", rad: str = "50",
        r: str = "255", g: str = "255", b: str = "255"):
    """Draw a filled circle"""
    check_pygame_events()
    pos_x = validate_int(x, 0, SCREEN_WIDTH)
    pos_y = validate_int(y, 0, SCREEN_HEIGHT)
    radius = validate_int(rad, 1, 200)
    color = validate_color(r, g, b)
    
    gfxdraw.filled_circle(screen, pos_x, pos_y, radius, color)
    pygame.display.flip()
    print(f"[ORB] at ({pos_x},{pos_y}) radius {radius} RGB{color}")


def ECHO(val: str):
    """Echo a value"""
    print(f"[ECHO] {val}")


def ARCANE(script_file: str):
    """Execute another ritual script"""
    if not os.path.exists(script_file):
        print(f"[ERROR] Script not found: {script_file}")
        return
    
    # Prevent path traversal
    if ".." in script_file or script_file.startswith("/"):
        print(f"[ERROR] Invalid script path")
        return
    
    print(f"[ARCANE] Executing {script_file}")
    run_script(script_file)


# ---- COMMAND REGISTRY ----
COMMANDS = {
    "AMPLIFY": AMPLIFY,
    "DIMINISH": DIMINISH,
    "SHIFT": SHIFT,
    "RETURN": RETURN,
    "CHIME": CHIME,
    "PAUSE": PAUSE,
    "SUMMON": SUMMON,
    "PORTAL": PORTAL,
    "INSCRIBE": INSCRIBE,
    "SCRIBE": SCRIBE,
    "LIGHT": LIGHT,
    "FLASH": FLASH,
    "SIGIL": SIGIL,
    "ORB": ORB,
    "ECHO": ECHO,
    "ARCANE": ARCANE
}


# ---- SCRIPT EXECUTION ----

def run_lines(lines: List[str]):
    """Execute a list of script lines"""
    global running
    i = 0
    loop_counter = 0
    
    while i < len(lines) and running:
        check_pygame_events()
        
        line = lines[i].strip()
        
        # Skip empty lines and comments
        if not line or line.startswith("#"):
            i += 1
            continue
        
        # Handle REPEAT loops
        repeat_match = re.match(r"REPEAT\s+(\d+)\s+{", line)
        if repeat_match:
            count = min(int(repeat_match.group(1)), MAX_LOOP_ITERATIONS)
            block = []
            depth = 1
            i += 1
            
            # Extract loop body
            while i < len(lines) and depth > 0:
                l = lines[i].strip()
                if l.endswith("{"):
                    depth += 1
                if l == "}":
                    depth -= 1
                if depth > 0:
                    block.append(l)
                i += 1
            
            # Execute loop
            for _ in range(count):
                if not running:
                    break
                run_lines(block)
                loop_counter += 1
                if loop_counter > MAX_LOOP_ITERATIONS:
                    print(f"[ERROR] Loop iteration limit reached")
                    break
            
            continue
        
        # Handle SET (variable assignment)
        set_match = re.match(r"SET\s+(\w+)\s+(.+)", line)
        if set_match:
            var, expr = set_match.groups()
            result = safe_eval(expr)
            variables[var] = result
            print(f"[SET] {var} = {result}")
            i += 1
            continue
        
        # Handle IF conditionals
        if_match = re.match(r"IF\s+(.+?)\s+THEN\s+(.+)", line)
        if if_match:
            condition, command = if_match.groups()
            result = safe_eval(condition)
            if result:
                run_lines([command])
            i += 1
            continue
        
        # Execute normal commands
        parts = line.split(maxsplit=1)
        cmd = parts[0].upper()
        args = parts[1].split() if len(parts) > 1 else []
        
        if cmd in COMMANDS:
            try:
                COMMANDS[cmd](*args)
            except TypeError as e:
                print(f"[ERROR] {line} -> Wrong number of arguments")
            except Exception as e:
                print(f"[ERROR] {line} -> {e}")
        else:
            print(f"[UNKNOWN] {cmd}")
        
        i += 1
        
        # Frame rate limiting
        if clock:
            clock.tick(60)


def run_script(filepath: str):
    """Load and execute a ritual script"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        print(f"\n[*] Executing ritual: {filepath}")
        print("=" * 40)
        run_lines(lines)
        print("=" * 40)
        print("[*] Ritual complete\n")
    
    except FileNotFoundError:
        print(f"[ERROR] File not found: {filepath}")
    except Exception as e:
        print(f"[ERROR] Failed to execute ritual: {e}")


# ---- MAIN ----

def main():
    """Main entry point"""
    global running
    
    print("=" * 50)
    print("  PURE Ritual Language Interpreter v0.2")
    print("=" * 50)
    
    init_display()
    
    if len(sys.argv) > 1:
        script_file = sys.argv[1]
    else:
        script_file = input("Enter script filename (e.g., ritual.txt): ").strip()
    
    if not script_file:
        print("[ERROR] No script specified")
        sys.exit(1)
    
    if not os.path.exists(script_file):
        print(f"[ERROR] File not found: {script_file}")
        sys.exit(1)
    
    run_script(script_file)
    
    # Keep window open
    print("\n[*] Press ESC or close window to exit")
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
        clock.tick(30)
    
    pygame.quit()


if __name__ == "__main__":
    main()
