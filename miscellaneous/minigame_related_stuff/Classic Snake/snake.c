#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>
#include <termios.h>
#include <fcntl.h>

#define WIDTH 20
#define HEIGHT 10

int kbhit(void) {
    struct termios oldt, newt;
    int ch;
    int oldf;
    
    tcgetattr(STDIN_FILENO, &oldt);
    newt = oldt;
    newt.c_lflag &= ~(ICANON | ECHO);
    tcsetattr(STDIN_FILENO, TCSANOW, &newt);
    oldf = fcntl(STDIN_FILENO, F_GETFL, 0);
    fcntl(STDIN_FILENO, F_SETFL, oldf | O_NONBLOCK);
    
    ch = getchar();
    
    tcsetattr(STDIN_FILENO, TCSANOW, &oldt);
    fcntl(STDIN_FILENO, F_SETFL, oldf);
    
    if(ch != EOF){
        ungetc(ch, stdin);
        return 1;
    }
    
    return 0;
}

typedef struct {
    int x, y;
} Point;

typedef struct {
    Point body[100];
    int length;
    char direction;
} Snake;

Point food;
Snake snake;

void generate_food() {
    food.x = rand() % WIDTH;
    food.y = rand() % HEIGHT;
}

void init() {
    srand(time(NULL));
    snake.length = 3;
    snake.direction = 'r';
    snake.body[0].x = WIDTH / 2;
    snake.body[0].y = HEIGHT / 2;
    snake.body[1].x = snake.body[0].x - 1;
    snake.body[1].y = snake.body[0].y;
    snake.body[2].x = snake.body[1].x - 1;
    snake.body[2].y = snake.body[1].y;
    generate_food();
}

void draw() {
    system("clear"); // use "cls" on Windows
    for(int y = 0; y < HEIGHT; y++) {
        for(int x = 0; x < WIDTH; x++) {
            int printed = 0;
            if(x == food.x && y == food.y) {
                printf("F");
                printed = 1;
            } else {
                for(int i = 0; i < snake.length; i++) {
                    if(snake.body[i].x == x && snake.body[i].y == y) {
                        printf("O");
                        printed = 1;
                        break;
                    }
                }
            }
            if(!printed) printf(".");
        }
        printf("\n");
    }
}

void update() {
    Point new_head = snake.body[0];
    
    if(snake.direction == 'u') new_head.y--;
    else if(snake.direction == 'd') new_head.y++;
    else if(snake.direction == 'l') new_head.x--;
    else if(snake.direction == 'r') new_head.x++;
    
    // Check collisions
    if(new_head.x < 0 || new_head.x >= WIDTH || new_head.y < 0 || new_head.y >= HEIGHT) {
        printf("Game Over! Hit wall.\n");
        exit(0);
    }
    for(int i = 0; i < snake.length; i++) {
        if(new_head.x == snake.body[i].x && new_head.y == snake.body[i].y) {
            printf("Game Over! Hit yourself.\n");
            exit(0);
        }
    }
    
    // Move snake
    for(int i = snake.length; i > 0; i--) {
        snake.body[i] = snake.body[i-1];
    }
    snake.body[0] = new_head;
    
    // Check food
    if(new_head.x == food.x && new_head.y == food.y) {
        snake.length++;
        generate_food();
    }
}

void input() {
    if(kbhit()) {
        char c = getchar();
        if(c == 'w' && snake.direction != 'd') snake.direction = 'u';
        else if(c == 's' && snake.direction != 'u') snake.direction = 'd';
        else if(c == 'a' && snake.direction != 'r') snake.direction = 'l';
        else if(c == 'd' && snake.direction != 'l') snake.direction = 'r';
    }
}

int main() {
    init();
    while(1) {
        draw();
        input();
        update();
        usleep(200000); // delay 0.2 seconds
    }
    return 0;
}
