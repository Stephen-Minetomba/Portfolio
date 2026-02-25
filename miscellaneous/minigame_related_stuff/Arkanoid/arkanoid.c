#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <termios.h>
#include <fcntl.h>
#include <sys/select.h>

#define WIDTH 40
#define HEIGHT 20
#define BRICK_ROWS 5
#define PADDLE_LEN 7
#define BRICK_WIDTH 4

int ballX, ballY;
int ballDirX = 1, ballDirY = -1;
int paddleX;
int bricks[BRICK_ROWS][WIDTH/BRICK_WIDTH];
int score = 0;
int lives = 3;
int speedDelay = 50000; // fixed speed

struct termios orig_termios;

void disableRawMode() { tcsetattr(STDIN_FILENO, TCSANOW, &orig_termios); }
void enableRawMode() {
    tcgetattr(STDIN_FILENO, &orig_termios);
    atexit(disableRawMode);
    struct termios raw = orig_termios;
    raw.c_lflag &= ~(ICANON | ECHO);
    raw.c_cc[VMIN] = 0;   // non-blocking read
    raw.c_cc[VTIME] = 0;
    tcsetattr(STDIN_FILENO, TCSANOW, &raw);
}

int kbhit() {
    struct timeval tv = {0L, 0L};
    fd_set fds;
    FD_ZERO(&fds);
    FD_SET(0, &fds);
    return select(1, &fds, NULL, NULL, &tv);
}

int getch() {
    unsigned char c;
    if (read(0, &c, sizeof(c)) < 0) return 0;
    return c;
}

void initialize() {
    ballX = WIDTH / 2;
    ballY = HEIGHT - 3;
    paddleX = WIDTH / 2 - PADDLE_LEN / 2;
    score = 0;
    lives = 3;
    speedDelay = 50000;

    for (int i = 0; i < BRICK_ROWS; i++)
        for (int j = 0; j < WIDTH/BRICK_WIDTH; j++)
            bricks[i][j] = 1;
}

void draw() {
    system("clear");

    // Score and lives
    printf("Score: %d   Lives: ", score);
    for (int i = 0; i < lives; i++) printf("\033[1;31m♥\033[0m ");
    printf("\n\n");

    // Top wall
    printf("\033[1;37m+");
    for (int i = 0; i < WIDTH; i++) printf("-");
    printf("+\033[0m\n");

    // Draw bricks
    const char* colors[] = {"\033[1;31m", "\033[1;33m", "\033[1;32m", "\033[1;36m", "\033[1;35m"};
    for (int i = 0; i < BRICK_ROWS; i++) {
        printf("\033[1;37m|\033[0m");
        for (int j = 0; j < WIDTH; j++) {
            int brick_index = j / BRICK_WIDTH;
            if (brick_index < WIDTH/BRICK_WIDTH && bricks[i][brick_index])
                printf("%s#\033[0m", colors[i % 5]);
            else
                printf(" ");
        }
        printf("\033[1;37m|\033[0m\n");
    }

    // Empty space + ball
    for (int i = BRICK_ROWS; i < HEIGHT-1; i++) {
        printf("\033[1;37m|\033[0m");
        for (int j = 0; j < WIDTH; j++) {
            if (i == ballY && j == ballX)
                printf("\033[1;33m●\033[0m");
            else
                printf(" ");
        }
        printf("\033[1;37m|\033[0m\n");
    }

    // Paddle
    printf("\033[1;37m|\033[0m");
    for (int j = 0; j < WIDTH; j++) {
        if (j >= paddleX && j < paddleX + PADDLE_LEN)
            printf("\033[1;34m█\033[0m");
        else
            printf(" ");
    }
    printf("\033[1;37m|\033[0m\n");

    // Bottom wall
    printf("\033[1;37m+");
    for (int i = 0; i < WIDTH; i++) printf("-");
    printf("+\033[0m\n");
}

void updateBall() {
    ballX += ballDirX;
    ballY += ballDirY;

    // Bounce off side walls
    if (ballX <= 0) { ballX = 0; ballDirX *= -1; }
    if (ballX >= WIDTH-1) { ballX = WIDTH-1; ballDirX *= -1; }

    // Bounce off top wall
    if (ballY < 0) { ballY = 0; ballDirY *= -1; }

    // Paddle collision with angle based on hit position
    if (ballY == HEIGHT-1) {
        if (ballX >= paddleX && ballX < paddleX + PADDLE_LEN) {
            int hitPos = ballX - paddleX;
            ballDirY = -1;
            if (hitPos < PADDLE_LEN/3) ballDirX = -1;      // left edge
            else if (hitPos >= 2*PADDLE_LEN/3) ballDirX = 1; // right edge
            // middle keeps current ballDirX
        }
    }

    // Brick collision
    if (ballY < BRICK_ROWS) {
        int brick_index = ballX / BRICK_WIDTH;
        if (brick_index < WIDTH/BRICK_WIDTH && bricks[ballY][brick_index]) {
            bricks[ballY][brick_index] = 0;
            ballDirY *= -1;
            score += 10;
        }
    }
}

void drawPauseMenu(int selected) {
    printf("\033[7;37m"); // reverse video
    int menuStart = HEIGHT/2 - 2;
    for (int i = 0; i < 5; i++) printf("\n");
    const char* options[] = {"Resume", "Reset", "Quit"};
    for (int i = 0; i < 3; i++) {
        if (i == selected)
            printf(" → %s ← \n", options[i]);
        else
            printf("   %s   \n", options[i]);
    }
    printf("\033[0m");
}

void pauseMenu() {
    int selected = 0; // 0=Resume, 1=Reset, 2=Quit
    while (1) {
        draw();                // redraw game state
        drawPauseMenu(selected);

        while (!kbhit()) usleep(10000);
        char c = getch();
        if (c == 27) { // escape sequence for arrow keys
            if (kbhit() && getch() == 91) {
                char dir = getch();
                if (dir == 'A' && selected > 0) selected--; // Up
                if (dir == 'B' && selected < 2) selected++; // Down
            }
        }
        if (c == '\n' || c == '\r') {
            if (selected == 0) break;       // Resume
            if (selected == 1) { initialize(); break; } // Reset
            if (selected == 2) { disableRawMode(); exit(0); } // Quit
        }
    }
}

int main() {
    enableRawMode();
    initialize();

    while (1) {
        draw();

        // Paddle movement - one step at a time
        if (kbhit()) {
            char c = getch();
            if (c == 'a' && paddleX > 0) paddleX -= PADDLE_LEN;
            if (c == 'd' && paddleX < WIDTH-PADDLE_LEN) paddleX += PADDLE_LEN;
            if (c == 'p') pauseMenu();          // Pause menu
            if (c == 'q') break;
        }

        updateBall();

        // Life lost only when hitting floor
        if (ballY >= HEIGHT) {
            lives--;
            if (lives == 0) {
                draw();
                printf("\n\033[1;31m💥 Game Over! Final Score: %d 💥\033[0m\n", score);
                break;
            } else {
                ballX = WIDTH/2; ballY = HEIGHT-3;
                ballDirX = 1; ballDirY = -1;
            }
        }

        // Win check
        int win = 1;
        for (int i = 0; i < BRICK_ROWS; i++)
            for (int j = 0; j < WIDTH/BRICK_WIDTH; j++)
                if (bricks[i][j]) win = 0;
        if (win) {
            draw();
            printf("\n\033[1;32m🎉 You Win! Final Score: %d 🎉\033[0m\n", score);
            break;
        }

        usleep(speedDelay);
    }

    disableRawMode();
    return 0;
}