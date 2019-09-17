#pragma once
#include <Arduino.h>
#include <Wire.h>
#include <BasicLinearAlgebra.h>
#include <EEPROM.h>
#include <Servo.h>
#include "Useful.h"

#define HAVE_BALL_EN 1
#define DRIBBLER_EN 1
#define GO_TO_GOAL_EN 1
#define LINE_EN 1
#define NBK_EN 1
#define BT_EN 0
#define MOTOR_EN 1

#define LS_ADDR 0x80
#define TB_ADDR 0x30
#define CAM_ADDR 0x12

#define BAT_PIN A11
#define LS_STATE_PIN 61
#define KICKER_PIN 38
#define DRIBBLER_PIN A9

#define SP_STEP 0.05
#define KICK_TIME 5000
#define DR_SP 70

#define BALL_FOLLOWING 0
#define GO_TO_GOAL 1
#define NBK_TACTICS 2
#define KICK 3
#define LINE 4

#define SC_CHOOSE_COLOR 0
#define SC_STARTSTOP 2
#define SC_CHOOSEMODE 3
#define SC_KICK 4

#define KEEPER_STANDART_DIST 30

#define CALIB_LS 239

#define BT Serial1

#define BT_CHANGE 253
#define BT_OK 222
#define BT_OK_1 223

class Omnibot
{
  public:
    void Init();
    void updBat();
    void updIMU();
    void ZeroIMU();
    void switchLs();
    void updLs();
    void calibLs();
    void updBall();
    void updGoals();
    void kick(int kickTime);
    void updCOMport();
    void checkBT();
    void updInterface();
    void strikerNavigation();
    void keeperNavigation();
    void runStopRobot();
    void changePlayingMode();
    void changeGoals();
    void setRobotNumber();
    void switchDribbler();
    void setDribbler(unsigned int _sp);
    void moveLocal(double _rotation, double _speed, double _heading, double max_turn_speed);
    void setMotors(double _speed1, double _speed2, double _speed3, double _speed4, double max_sp = 255.0);
    void writeMotor(int mot, double _sp, double max_sp = 255);
    void calculatePosition();
    void sendDataToMonitor();
    int batVolt = 0;
    int Yaw = 0, yawZero = 0, lsAngle = 400, state, stateOld, lineAngle = 400, ballAngle = 0, ballDist = 0;
    int goalAngle[2] = {0, 0};
    int goalDist[2] = {0, 0};
    long long int lsTimer = 0, lineTimer = 0, neLineTimer = 0, kickerTimer = 0, drTimer = 0, dRot = 0, ballTimer = 0, rotationTimer = 0, goToGoalTimer = 0, keeperBallTimer = 0, keeperKickTimer = 0;
    bool playing = 0, playingMode = 1, lsState = 0, haveBall = 0, ourGoal = 0, dr = 0, keeperKickFlag = 0, keeperKickFlag_1 = 0, firstLineFlag = 0;
    int rotationState = 0, rotationDirection = 0;
    double Rotation = 0, Speed = 100, Heading = 0;
    double sp[4] = {0.0, 0.0, 0.0, 0.0};
    int drSpeed = DR_SP;
    byte robotNumber;
    double rotationAngle = 0;
    double value1 = 174;
    int xPosition = 0, yPosition = 0;


  private:

    int motor_pins[8] = {8, 7, 9, 10, 2, 3, 5, 4};
    byte butPin[3] = {3, 2, 5};
    bool butValue[3] = {0, 0, 0};
    bool butOldValue[3] = {0, 0, 0};
    long long int butTime[3] = {0, 0, 0};
    int scNum = 2;
    double spOld[4] = {0, 0, 0, 0}, spTime, spDelta[4], spK[4],  maxDelta, max_speed;
    int maxDeltaN;

    long int btTimer, btFlag = 0, r = 0;
};

