import pygame
from dataclasses import dataclass
from typing import Optional

# ===== CONFIG =====
CELL_SIZE = 40
ROWS = 20
COLS = 40
FPS = 10

# Directions
DIRS = {
    "N": (-1, 0),
    "S": (1, 0),
    "W": (0, -1),
    "E": (0, 1),
}

OPPOSITE = {
    "N": "S",
    "S": "N",
    "W": "E",
    "E": "W",
}

# ===== CELL =====
@dataclass
class Cell:
    type: str
    facing: Optional[str]
    on: bool = False

# ===== AUTOMATON =====
class RedZone:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = [[None for _ in range(cols)] for _ in range(rows)]

    def in_bounds(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols

    def is_powered(self, r, c):
        # Check immediate neighbours (original logic)
        for d, (dr, dc) in DIRS.items():
            nr, nc = r + dr, c + dc

            if not self.in_bounds(nr, nc):
                continue

            me = self.grid[r][c]
            neighbor = self.grid[nr][nc]
            if not neighbor or not neighbor.on:
                continue

            if neighbor.facing and OPPOSITE[neighbor.facing] == d:
                return True

            # Intended bug (do not fix): B powers every cell around it, including those that do not face opposite from B.
            if neighbor.type == "B":
                if me.facing != d:
                    return True
                continue

        # --- Skipper (type F) check: power from 3 cells away ---
        for d, (dr, dc) in DIRS.items():
            sr, sc = r - 3*dr, c - 3*dc          # cell that would be 3 steps behind us in direction d
            if self.in_bounds(sr, sc):
                skipper = self.grid[sr][sc]
                if skipper and skipper.type == "F" and skipper.on and skipper.facing == d:
                    return True

        return False

    def step(self):
        next_states = [[False for _ in range(self.cols)] for _ in range(self.rows)]

        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if not cell:
                    continue

                powered = self.is_powered(r, c)

                if cell.type in ["A", "B", "E", "F"]:   # added "F" here
                    next_states[r][c] = powered

                elif cell.type == "C":
                    next_states[r][c] = not powered

                elif cell.type == "D":
                    next_states[r][c] = cell.on

        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c]:
                    self.grid[r][c].on = next_states[r][c]

# ===== GUI =====
pygame.init()
screen = pygame.display.set_mode((COLS * CELL_SIZE, ROWS * CELL_SIZE))
pygame.display.set_caption("RedZone Automaton")
clock = pygame.time.Clock()

rz = RedZone(ROWS, COLS)

selected_type = "A"
selected_facing = "E"
running = False

font = pygame.font.SysFont(None, 18)

def draw_arrow(surface, r, c, direction):
    center_x = c * CELL_SIZE + CELL_SIZE // 2
    center_y = r * CELL_SIZE + CELL_SIZE // 2

    if direction == "N":
        pygame.draw.line(surface, (0,0,0), (center_x, center_y), (center_x, center_y-10), 2)
    elif direction == "S":
        pygame.draw.line(surface, (0,0,0), (center_x, center_y), (center_x, center_y+10), 2)
    elif direction == "W":
        pygame.draw.line(surface, (0,0,0), (center_x, center_y), (center_x-10, center_y), 2)
    elif direction == "E":
        pygame.draw.line(surface, (0,0,0), (center_x, center_y), (center_x+10, center_y), 2)

def draw():
    screen.fill((220, 220, 220))

    for r in range(ROWS):
        for c in range(COLS):
            rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, (180, 180, 180), rect, 1)

            cell = rz.grid[r][c]
            if cell:
                color = (0, 200, 0) if cell.on else (200, 0, 0)
                pygame.draw.rect(screen, color, rect.inflate(-4, -4))

                label = font.render(cell.type, True, (255,255,255))
                screen.blit(label, (c*CELL_SIZE+5, r*CELL_SIZE+5))

                if cell.facing:
                    draw_arrow(screen, r, c, cell.facing)

    pygame.display.flip()

# ===== MAIN LOOP =====
while True:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1: selected_type = "A"
            if event.key == pygame.K_2: selected_type = "B"
            if event.key == pygame.K_3: selected_type = "C"
            if event.key == pygame.K_4: selected_type = "D"
            if event.key == pygame.K_5: selected_type = "E"
            if event.key == pygame.K_6: selected_type = "F"   # added skipper

            if event.key == pygame.K_UP: selected_facing = "N"
            if event.key == pygame.K_DOWN: selected_facing = "S"
            if event.key == pygame.K_LEFT: selected_facing = "W"
            if event.key == pygame.K_RIGHT: selected_facing = "E"

            if event.key == pygame.K_SPACE:
                rz.step()

            if event.key == pygame.K_RETURN:
                running = not running

            if event.key == pygame.K_c:
                rz = RedZone(ROWS, COLS)

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            c = x // CELL_SIZE
            r = y // CELL_SIZE

            if rz.in_bounds(r, c):
                cell = rz.grid[r][c]

                if event.button == 1:
                    if cell and cell.type == "D":
                        cell.on = not cell.on
                    else:
                        rz.grid[r][c] = Cell(selected_type,
                                             None if selected_type in ["B", "E"] else selected_facing,
                                             False)

                if event.button == 3:
                    rz.grid[r][c] = None

    if running:
        rz.step()

    draw()
