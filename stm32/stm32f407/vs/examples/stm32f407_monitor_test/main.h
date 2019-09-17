#include "stm32f4xx.h"
#include "stdbool.h"
#include "math.h"

#include "useful.h"

/********************************* periph lib *********************************/

#include "stm32f407_sysFunc.h"
#include "stm32f407_pin.h"
#include "stm32f407_UART.h"

/********************************* code *********************************/


int Yaw = 0, zeroYaw = 0;
bool playing = 0, playingMode = 1, haveBall = 0, ourGoal = 0;
int lineAngle = 400, ballAngle = 0, ballDist = 100;
int batVolt = 124;
double Rotation = 0, Speed = 100, Heading = 0;
char robotNumber = 0;
long int sendToMonitorTimer;

void sendDataToMonitor();