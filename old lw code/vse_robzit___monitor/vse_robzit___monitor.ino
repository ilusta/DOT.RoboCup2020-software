#include "Omnibot.h"

Omnibot omnibot;

void setup()
{
  omnibot.Init();
}

void loop()
{
  omnibot.updInterface();
  omnibot.updBat();
  omnibot.updCOMport();
  omnibot.updBall();
  omnibot.updGoals();
  omnibot.updIMU();
  omnibot.updLs();
  omnibot.checkBT();

  if (omnibot.playing)
  {
    if (omnibot.playingMode) omnibot.strikerNavigation();
    else omnibot.keeperNavigation();
  }
  else omnibot.setMotors(0, 0, 0, 0);
  if(MOTOR_EN) for (int i = 0; i < 4; i++) omnibot.writeMotor(i, omnibot.sp[i]);

  omnibot.calculatePosition();
  omnibot.sendDataToMonitor();
}
