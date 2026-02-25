#include <SDL2/SDL.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

// Controls:
// - WASD for movement
// - Up arrow and down arrow for looking up and down
// - R key to reset up/down heading
// - Q key to quit

// Display settings
#define SCREEN_W 900
#define SCREEN_H 600
#define TITLE "Raycast Engine"

// Camera settings
#define INVERT_CAMERA 0
#define VERTICAL_CAMERA_SENSITIVITY 0.05
#define HORIZONTAL_CAMERA_SENSITIVITY 0.05

// Movement settings
#define SPEED 0.1

// Render settings
#define WALL_DENSITY 1

// Map settings
#define MINI_MAP_SCALE 8
#define MAP_W 24
#define MAP_H 24
int worldMap[MAP_H][MAP_W] = {
  {01,01,01,01,01,01,01,01,01,01,01,01,01,01,01,01,01,01,01,01,01,01,01,01},
  {01,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,01},
  {01,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,01},
  {01,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,01},
  {01,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,01},
  {01,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,01},
  {01,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,01},
  {01,00,00,00,00,00,00,01,01,01,01,01,01,00,00,00,00,00,00,00,00,00,00,01},
  {01,00,00,00,00,00,00,01,00,00,00,00,01,00,00,00,00,00,00,00,00,00,00,01},
  {01,00,00,00,00,00,00,01,00,00,00,00,01,00,00,00,00,00,00,00,00,00,00,01},
  {01,00,00,00,00,00,00,01,00,00,00,00,01,00,00,00,00,00,00,00,00,00,00,01},
  {01,00,00,00,00,00,00,01,02,00,00,02,01,00,00,00,00,00,00,00,00,00,00,01},
  {01,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,01},
  {01,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,01},
  {01,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,01},
  {01,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,01},
  {01,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,01},
  {01,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,01},
  {01,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,01},
  {01,01,01,01,01,01,01,01,01,00,00,00,00,00,01,01,01,01,01,01,01,01,01,01},
  {01,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,01},
  {01,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,01},
  {01,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,01},
  {01,01,01,01,01,01,01,01,01,01,01,01,01,01,01,01,01,01,01,01,01,01,01,01}
};

// Wall type definition
typedef struct {
    Uint8 r, g, b;  // RGB color
    int opacity;    // 0-100
    bool passthrough; // true if you can pass through
} WallType;

// Wall color table
WallType wallTypes[] = {
    {0,0,0,0,false},          // 00 air
    {255,255,255,100,false},  // 01 white
    {128,128,128,100,false},  // 02 gray
    {0,0,0,100,false},        // 03 black
    {139,69,19,100,false},    // 04 brown
    {0,255,255,100,false},    // 05 cyan
    {0,0,255,100,false},      // 06 blue
    {255,0,0,100,false},      // 07 red
    {0,128,0,100,false},      // 08 green
    {255,255,0,100,false},    // 09 yellow
    {255,165,0,100,false},    // 10 orange
    {128,0,128,100,false},    // 11 purple
    {255,192,203,100,false},  // 12 pink
    {255,0,255,100,false}     // 13 magenta
};

typedef struct { float x, y; float dirX, dirY; float planeX, planeY; } Player;

void drawMiniMap(SDL_Renderer *ren, Player p) {
    for(int y=0;y<MAP_H;y++){
        for(int x=0;x<MAP_W;x++){
            int type = worldMap[y][x];
            if(type < 0 || type > 13) type = 0;
            WallType w = wallTypes[type];
            SDL_SetRenderDrawColor(ren, w.r, w.g, w.b, (Uint8)(w.opacity*2.55));
            SDL_Rect r = {x*MINI_MAP_SCALE, y*MINI_MAP_SCALE, MINI_MAP_SCALE, MINI_MAP_SCALE};
            SDL_RenderFillRect(ren,&r);
        }
    }
    SDL_SetRenderDrawColor(ren,0,255,0,255); // Player
    SDL_Rect r = {p.x*MINI_MAP_SCALE-2, p.y*MINI_MAP_SCALE-2, 4,4};
    SDL_RenderFillRect(ren,&r);
}

int main(int argc, char **argv){
    SDL_Init(SDL_INIT_VIDEO);
    SDL_Window *win = SDL_CreateWindow(TITLE,SDL_WINDOWPOS_CENTERED,SDL_WINDOWPOS_CENTERED,SCREEN_W,SCREEN_H,0);
    SDL_Renderer *ren = SDL_CreateRenderer(win,-1,SDL_RENDERER_ACCELERATED);

    Player p = {22,12,-1,0,0,0.66};
    int quit=0;
    SDL_Event e;
    float cameraHeight=0;

    while(!quit){
        while(SDL_PollEvent(&e)){
            if(e.type==SDL_QUIT) quit=1;
        }
        const Uint8 *state = SDL_GetKeyboardState(NULL);

        // Movement
        if(state[SDL_SCANCODE_W]){
            int nx=(int)(p.x+p.dirX*SPEED);
            int ny=(int)(p.y+p.dirY*SPEED);
            if(worldMap[ny][(int)p.x]==0) p.y+=p.dirY*SPEED;
            if(worldMap[(int)p.y][nx]==0) p.x+=p.dirX*SPEED;
        }
        if(state[SDL_SCANCODE_S]){
            int nx=(int)(p.x-p.dirX*SPEED);
            int ny=(int)(p.y-p.dirY*SPEED);
            if(worldMap[ny][(int)p.x]==0) p.y-=p.dirY*SPEED;
            if(worldMap[(int)p.y][nx]==0) p.x-=p.dirX*SPEED;
        }

        // Rotation
        if(state[SDL_SCANCODE_A]){
            float oldDirX=p.dirX;
            p.dirX=p.dirX*cos(HORIZONTAL_CAMERA_SENSITIVITY)-p.dirY*sin(HORIZONTAL_CAMERA_SENSITIVITY);
            p.dirY=oldDirX*sin(HORIZONTAL_CAMERA_SENSITIVITY)+p.dirY*cos(HORIZONTAL_CAMERA_SENSITIVITY);
            float oldPlaneX=p.planeX;
            p.planeX=p.planeX*cos(HORIZONTAL_CAMERA_SENSITIVITY)-p.planeY*sin(HORIZONTAL_CAMERA_SENSITIVITY);
            p.planeY=oldPlaneX*sin(HORIZONTAL_CAMERA_SENSITIVITY)+p.planeY*cos(HORIZONTAL_CAMERA_SENSITIVITY);
        }
        if(state[SDL_SCANCODE_D]){
            float oldDirX=p.dirX;
            p.dirX=p.dirX*cos(-HORIZONTAL_CAMERA_SENSITIVITY)-p.dirY*sin(-HORIZONTAL_CAMERA_SENSITIVITY);
            p.dirY=oldDirX*sin(-HORIZONTAL_CAMERA_SENSITIVITY)+p.dirY*cos(-HORIZONTAL_CAMERA_SENSITIVITY);
            float oldPlaneX=p.planeX;
            p.planeX=p.planeX*cos(-HORIZONTAL_CAMERA_SENSITIVITY)-p.planeY*sin(-HORIZONTAL_CAMERA_SENSITIVITY);
            p.planeY=oldPlaneX*sin(-HORIZONTAL_CAMERA_SENSITIVITY)+p.planeY*cos(-HORIZONTAL_CAMERA_SENSITIVITY);
        }

        // Look up/down
        if(INVERT_CAMERA==0){
            if(state[SDL_SCANCODE_DOWN]) cameraHeight-=VERTICAL_CAMERA_SENSITIVITY;
            if(state[SDL_SCANCODE_UP]) cameraHeight+=VERTICAL_CAMERA_SENSITIVITY;
        } else {
            if(state[SDL_SCANCODE_UP]) cameraHeight-=VERTICAL_CAMERA_SENSITIVITY;
            if(state[SDL_SCANCODE_DOWN]) cameraHeight+=VERTICAL_CAMERA_SENSITIVITY;
        }

        // Reset camera vertical heading
        if (state[SDL_SCANCODE_R]) {
            cameraHeight = 0;
        }

        // Exit program
        if (state[SDL_SCANCODE_Q]) {
            break;
        }

        // Floor/ceiling
        SDL_SetRenderDrawColor(ren,135,206,235,255); // ceiling
        SDL_Rect ceilingRect={0,0,SCREEN_W,SCREEN_H/2};
        ceilingRect.y+=(int)(cameraHeight*SCREEN_H);
        SDL_RenderFillRect(ren,&ceilingRect);

        SDL_SetRenderDrawColor(ren,100,100,100,255); // floor
        SDL_Rect floorRect={0,SCREEN_H/2,SCREEN_W,SCREEN_H/2};
        floorRect.y+=(int)(cameraHeight*SCREEN_H);
        SDL_RenderFillRect(ren,&floorRect);

        // Raycasting
        for(int x=0;x<SCREEN_W;x++){
            float cameraX=2*x/(float)SCREEN_W-1;
            float rayDirX=p.dirX+p.planeX*cameraX;
            float rayDirY=p.dirY+p.planeY*cameraX;

            int mapX=(int)p.x;
            int mapY=(int)p.y;

            float sideDistX, sideDistY;
            float deltaDistX=fabs(1/rayDirX);
            float deltaDistY=fabs(1/rayDirY);
            int stepX, stepY;
            int hit=0, side;

            if(rayDirX<0){ stepX=-1; sideDistX=(p.x-mapX)*deltaDistX; }
            else{ stepX=1; sideDistX=(mapX+1.0-p.x)*deltaDistX; }
            if(rayDirY<0){ stepY=-1; sideDistY=(p.y-mapY)*deltaDistY; }
            else{ stepY=1; sideDistY=(mapY+1.0-p.y)*deltaDistY; }

            while(hit==0){
                if(sideDistX<sideDistY){ sideDistX+=deltaDistX; mapX+=stepX; side=0; }
                else{ sideDistY+=deltaDistY; mapY+=stepY; side=1; }
                if(worldMap[mapY][mapX]>0) hit=1;
            }

            float perpWallDist;
            if(side==0) perpWallDist=(mapX-p.x+(1-stepX)/2)/rayDirX;
            else perpWallDist=(mapY-p.y+(1-stepY)/2)/rayDirY;

            int lineHeight=(int)((SCREEN_H/perpWallDist)*WALL_DENSITY);
            int drawStart=-lineHeight/2+SCREEN_H/2+(int)(cameraHeight*SCREEN_H);
            int drawEnd=lineHeight/2+SCREEN_H/2+(int)(cameraHeight*SCREEN_H);
            if(drawStart<0) drawStart=0;
            if(drawEnd>=SCREEN_H) drawEnd=SCREEN_H-1;

            int type=worldMap[mapY][mapX];
            if(type<1 || type>13) type=1;
            WallType w=wallTypes[type];
            Uint8 alpha=(Uint8)(w.opacity*2.55);
            if(side==1) SDL_SetRenderDrawColor(ren,w.r/2,w.g/2,w.b/2,alpha);
            else SDL_SetRenderDrawColor(ren,w.r,w.g,w.b,alpha);

            SDL_RenderDrawLine(ren,x,drawStart,x,drawEnd);
        }

        drawMiniMap(ren,p);

        SDL_RenderPresent(ren);
        SDL_Delay(10);
    }

    SDL_DestroyRenderer(ren);
    SDL_DestroyWindow(win);
    SDL_Quit();
    return 0;
}