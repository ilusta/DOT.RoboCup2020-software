#include "Omnibot.h"

void Omnibot::strikerNavigation()
{
  state = BALL_FOLLOWING;
  Rotation = 0;
  Heading = 0;
  Speed = 175;
  if (keeperKickFlag && keeperKickFlag_1) keeperKickTimer = millis(), keeperKickFlag = 0;
  else if (!keeperKickFlag_1) keeperKickTimer = millis();

  if (ballAngle != 400) Heading = ballAngle;

  if (abs(ballAngle) < 50 && ballDist < 40 && ballDist != 0 && DRIBBLER_EN) setDribbler(DR_SP - 5);
  else setDribbler(0);

  if ((haveBall || (millis() - ballTimer) < 200) && GO_TO_GOAL_EN)
  {
    state = GO_TO_GOAL;
    if (haveBall) ballTimer = millis();
  }
  else goToGoalTimer = millis();

  if (state == GO_TO_GOAL && (millis() - goToGoalTimer) > 3000 && (goalDist[0] > 60 || rotationState) && NBK_EN) state = NBK_TACTICS;      //NBK OF THE ENEMY
  else rotationTimer = millis();

  if ((lsAngle != 400 || millis() - lsTimer < 200) && state != GO_TO_GOAL && LINE_EN) //ON THE LINE
  {
    state = LINE;
    if (millis() - neLineTimer > 500) firstLineFlag = 1;
    if (firstLineFlag && millis() - lineTimer > 300) firstLineFlag = 0;
    if (lsAngle != 400) lsTimer = millis();
    neLineTimer = millis();
  }
  else lineTimer = millis();

  switch (state)                    //WHAT TO DO
  {
    case BALL_FOLLOWING:
      //Serial.println("Ball following");
      if (abs(Heading) > 45 && ballDist != 0) Heading += sgn(Heading) * 820 / ballDist;
      else if (ballDist != 0) Heading *= 1.7;
      else Heading = 0, Speed = 0;

      if (abs(goalDist[0]*cos(radians(goalAngle[0])))  <= 50 && abs(Heading) >= 90) Heading = 80 * sgn(Heading);
      adduction(Heading);
      break;

    case GO_TO_GOAL:
      //Serial.print("Go to goal: ");
      setDribbler(DR_SP);
      //IN FRONT OF GOAL:
      if (abs(goalAngle[1]) <= 50)
      {
        //Serial.println("middle;");
        Speed = 270;
        Rotation = goalAngle[1] * 0.8;
        Heading = goalAngle[1] * 1.5;
        if (goalDist[1] <= 40) setDribbler(0);
      }
      //FROM THE SIDE OF GATE:
      else
      {
        //Serial.println("corner;");
        Rotation = 0;
        Heading = goalAngle[1] * 2;
        Speed = 120;
      }
      adduction(Heading);
      break;

    case NBK_TACTICS:
      //Serial.println("NBK Tactics");
      Speed = 50;
      setDribbler(DR_SP + 10);
      if (rotationDirection == 0) rotationDirection = sgn((goalAngle[1] + goalAngle[0]) / 2);      //DIRECTION OF ROTATION
      //FIRST HALF:
      if (rotationState != 2)
      {
        Heading = 180;
        rotationState = 1;
        rotationAngle -= (millis() - rotationTimer) * 0.11 * rotationDirection;
        adduction(rotationAngle);
        if (sgn(rotationAngle) == rotationDirection) rotationState = 2;
      }
      //SECOND HALF:
      else if (sgn(rotationAngle) == rotationDirection)
      {
        Heading = 0;
        Speed = 80;
        rotationAngle -= (millis() - rotationTimer) * 0.15 * rotationDirection;
      }
      else                      //DONE
      {
        rotationState = 0;
        goToGoalTimer = millis();
        rotationAngle = 0;
        rotationDirection = 0;
        Speed = 150;
        Rotation = 0;
      }
      Rotation += rotationAngle;
      Heading += Rotation;
      rotationTimer = millis();
      break;

    case LINE:
      //Serial.print("Line: ");
      Speed = 150;
      lineAngle = (goalAngle[0] + goalAngle[1]) / 2;
      adduction(lineAngle);
      int _ballAngle = ballAngle + 90;
      adduction(_ballAngle);

      Heading = lineAngle;
      Speed = 300;
      /*if (firstLineFlag) //Serial.print("First ");

      if (abs(goalAngle[0]) > 100 && abs(goalAngle[1]) < 80 && sgn(ballAngle) != sgn(lineAngle))     //Middle when the ball is in aut
      {
        if (firstLineFlag) Heading = 90 * sgn(lineAngle), Speed = 360;
        else if (sgn(_ballAngle) > 0) Heading = sgn(lineAngle) * 20;
        else Heading = sgn(lineAngle) * 135;
        //Serial.println("middle;");
      }
      else if (abs(goalAngle[0]) > 120 && abs(goalAngle[1]) < 60)        //Middle when we can take the ball
      {
        //Serial.println("ball;");
        if (firstLineFlag) Heading = 90 * sgn(lineAngle), Speed = 360;
        else Heading = ballAngle, Rotation = -10 * sgn(lineAngle);
      }
      else if (abs(lineAngle) < 90)       //Our corner
      {
        Speed = 300;
        Heading = lineAngle * 0.8;
        if (firstLineFlag) Speed = 360;
        //Serial.println("corner;");
      }
      else         //Enemy corner
      {
        Speed = 300;
        Heading = lineAngle * 1.1;
        if (firstLineFlag) Speed = 360;
        else if (abs(ballAngle) < 70) Rotation = ballAngle * 0.5;
        //Serial.println("corner;");
      }*/
      break;
  }
  if (millis() - keeperKickTimer > 2000)
  {
    changePlayingMode();
    BT.write(BT_OK_1);
    keeperKickFlag_1 = 0;
    keeperBallTimer = millis();
    setDribbler(0);
  }
  adduction(Heading);
  moveLocal(Rotation, Speed, Heading, 200);
}


void Omnibot::keeperNavigation()
{
  double Rotation = 0, Speed = 70, Heading = 0, err = 0, u = 0, p = 0, d = 0, kP = 3, kD = 20, kI = 0.05, kBall = 3;
  double goalX = 0, goalY = 0, ballX = 0, ballY = 0, errX = 0, errY = 0;
  static double i = 0, err_old = 0;
  static bool keeperState = 1;
  setDribbler(0);

  goalX = sin(radians(goalAngle[0])) * goalDist[0];
  goalY = cos(radians(180 - abs(goalAngle[0]))) * goalDist[0];
  ballX = sin(radians(ballAngle)) * ballDist;
  ballY = cos(radians(ballAngle)) * ballDist;

  if (ballDist != 0 && ballDist <= 50)       //If we see the ball
  {
    //Serial.print("Ball: ");
    errX = ballX * kBall;
    if (ballDist < 25) errY = ballY * kBall - 20;       //If the ball is close go to the ball
    else errY = 0;      //If the ball is far away line up at the ball
    if (abs(goalAngle[0]) <= 110 && abs(ballAngle) >= 90) errY = 20;//, //Serial.println("corner;");              //If we stay in corner
//    else //Serial.println("middle;");
    if ((goalY >= 40 || (goalY >= 35 && ballDist > 30)) && abs(ballAngle) <= 80) errY = 42 - goalY;//, //Serial.println(" far;");
    if (millis() - keeperBallTimer > 2000)           //Become a striker if the ball remains in place for a long time
    {
      keeperKickFlag = 1;
      keeperKickFlag_1 = 1;
      changePlayingMode();
      BT.write(BT_OK);
      i = 0;
    }
    if (abs(goalX) >= 34 && sgn(errX) != sgn(goalX)) errX = goalX - 35 * sgn(goalX);//, //Serial.println(" line;");          //Line
    if (abs(errX) >= 10 || abs(ballAngle) > 90) keeperBallTimer = millis();
    err = sqrt(errX * errX + errY * errY);
    if (keeperState == 1 || err <= 9) i = 0;
    keeperState = 0;
  }
  else    //If we do not see the ball, line up on goal
  {
    keeperBallTimer = millis();
    //Serial.print("Goal: ");
    errX = goalX * 1.7;
    errY = KEEPER_STANDART_DIST - goalY;
    if (abs(goalAngle[0]) <= 110)     //If we in corner
    {
      //Serial.println("corner;");
      errX *= 0.2;
      errY = 50;
    }
    else if (goalDist[0] > 45)       //If we are far away
    {
      errX = goalX;
      errY = - goalY;
      //Serial.println("middle far;");
    }
    else //Serial.println("middle;");    //If all is ok
    err = sqrt(errX * errX + errY * errY);
    if (keeperState == 0 || err <= 3) i = 0;
    keeperState = 1;
  }

  Heading = degrees(atan2(errX, errY));
  i += err * kI;
  if (abs(i) > 60) i = sgn(i) * 60;
  p = err * kP;
  d = (err - err_old) * kD;
  err_old = err;
  u = p + d + i;

  if (u < 35) u = 0;
  if (u > 330) u = 330;
  Speed = u;

  adduction(Heading);
  moveLocal(Rotation, Speed, Heading, 170);
}
