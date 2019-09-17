#include "Omnibot.h"

Servo dribbler;

void Omnibot::Init()
{
  Wire.ostanavites();
  Serial.begin(115200);
  Serial.println(F("start"));
  Serial.println(F("i2c"));
  Wire.begin();
  Serial.println(F("switch ls on"));
  pinMode(LS_STATE_PIN, OUTPUT);
  lsState = 1;
  switchLs();
  Serial.println("kick off");
  pinMode(KICKER_PIN, OUTPUT);
  digitalWrite(KICKER_PIN, 0);
  Serial.println("init buttons");
  DDRJ &= ~ _BV(PJ2);
  PORTJ |= _BV(PJ2);
  DDRJ &= ~ _BV(PJ3);
  PORTJ |= _BV(PJ3);
  Serial.println(F("//Serial"));
  Serial3.begin(115200);
  BT.begin(115200);
  Serial.println(F("motor drivers"));
  for (int i = 0; i < 8; i++)
  {
    pinMode(motor_pins[i], OUTPUT);
    digitalWrite(motor_pins[i], 0);
  }
  Serial.print("sp1 = ");
  Serial.print(sp[0]);
  Serial.print("; sp2 = ");
  Serial.print(sp[1]);
  Serial.print("; sp3 = ");
  Serial.print(sp[2]);
  Serial.print("; sp4 = ");
  Serial.println(sp[3]);
  pinMode(BAT_PIN, INPUT);
  pinMode(A8, INPUT);
  Serial.println(F("zero imu"));
  ZeroIMU();
  Serial.print(F("battery voltage: "));
  updBat();
  Serial.print(batVolt / 10), //Serial.print(F(".")), //Serial.println(batVolt % 10);
  ourGoal = EEPROM.read(1);
  Serial.print("Now our goals is ");
  if (ourGoal) Serial.println("blue!");
  else Serial.println("yellow!");
  Serial.print(F("robotNumber: "));
  robotNumber = EEPROM.read(0);
  //Serial.println(robotNumber);
  playingMode = robotNumber;
  delay(500);
  lsState = 0;
  switchLs();
  //Serial.println(F("start dribbler"));
  dribbler.attach(DRIBBLER_PIN);
  //for (int i = 0; i < 180; i++) setDribbler(i);
  setDribbler(0);
  //Serial.println(F("OK"));
  delay(500);
}

void Omnibot::updCOMport()
{
  if (Serial.available())
  {
    char c = Serial.read();
    switch (c) {
      case 's':
        runStopRobot();
        break;

      case 'l':
        lsState = ! lsState;
        switchLs();
        break;

      case 'y':
        calibLs();
        break;

      case 'b':
        //Serial.print(batVolt / 10.0);
        delay(2000);
        break;

      case'h':
        changePlayingMode();
        break;

      case 'k':
        //Serial.println(F("kick"));
        kick(KICK_TIME);
        break;

      case 'c':
        setRobotNumber();
        break;

      case 'o':
        changeGoals();
        break;

      case 'd':
        switchDribbler();
        //default: //Serial.println(F("unknown command")); break;
    }
  }
}

void Omnibot::checkBT()
{
  if (BT_EN && playing)
  {
    if (playingMode == 1)       //STRIKER
    {
      if (BT.available() && BT.read() == BT_OK) int bbb;//Serial.print("CHANGE"), changePlayingMode();
      else if (goalDist[0] < 65)
      {
        //Serial.print("V ZONE; ballAng = ");
        //Serial.print(ballAngle);
        //Serial.print("; ballDist = ");
        //Serial.print(ballDist);
        //Serial.print("; goalDist = ");
        //Serial.print(goalDist[0]);
        if (abs(ballAngle) > 110 && ballDist > 30) BT.write(BT_CHANGE);//, //Serial.println("   WANT BEHIND");  //ball behind and far from striker
        else {
          if (goalDist[0] < 50) {
            BT.write(goalDist[0]);//, //Serial.println("   WANT BLIZKO");        //vdrug blize chem keeper
          }
        }
        //else //Serial.println();
      }
    }

    else if (playingMode == 0)       //KEEPER
    {
      if (BT.available())
      {
        r = BT.read();/*
        if (r == BT_OK_1) //Serial.println("CHANGE"), changePlayingMode();
        if (r == BT_CHANGE) //Serial.println("OKEY"), BT.write(BT_OK), changePlayingMode();
        else if (goalDist[0] - r >= 5) //Serial.println("OKEY"), BT.write(BT_OK), changePlayingMode();
        else //Serial.println("NOT OKEY");*/
      }
    }

    /* if (playingMode == 0)       //KEEPER
      {
       if(abs(ballAngle) < 40)
      }
    */
  }
}

void Omnibot::updInterface()
{
  /*for (int i = 0; i++; i < 2)
    {
    butValue[i] = !bitRead(PINJ, butPin[0]);
    if (butOldValue[i] && !butValue[i] && millis() - butTime[i] > 500) butOldValue[i] = butValue[i], butValue[i] = 1, butTime[i] = millis();
    else butOldValue[i] = butValue[i], butValue[i] = 0;
    }*/

  butValue[0] = !bitRead(PINJ, butPin[0]);
  if (butOldValue[0] && !butValue[0] && millis() - butTime[0] > 300) butOldValue[0] = butValue[0], butValue[0] = 1, butTime[0] = millis();
  else butOldValue[0] = butValue[0], butValue[0] = 0;

  butValue[1] = !bitRead(PINJ, butPin[1]);
  if (butOldValue[1] && !butValue[1] && millis() - butTime[1] > 300) butOldValue[1] = butValue[1], butValue[1] = 1, butTime[1] = millis();
  else butOldValue[1] = butValue[1], butValue[1] = 0;

  /*butValue[2] = !bitRead(PINJ, );
    if (butOldValue[2] && !butValue[2]) butOldValue[2] = butValue[2], butValue[2] = 1;
    else butOldValue[2] = butValue[2], butValue[2] = 0;*/

  bool flag = 0;
  if (!playing)
  {
    if (butValue[2]) scNum++, flag = 1;
    if (butValue[0]) scNum--, flag = 1;
  }
  if (scNum < 2) scNum = 4;
  if (scNum > 4) scNum = 2;
  if (flag) Serial.print("screen number: "), Serial.println(scNum);

  switch (scNum)
  {
    case SC_CHOOSE_COLOR:
      break;

    case SC_STARTSTOP:
      if (butValue[1]) runStopRobot();
      break;

    case SC_CHOOSEMODE:
      if (butValue[1]) changePlayingMode();
      break;

    case SC_KICK:
      if (butValue[1])
      {
        changeGoals();
      }
      break;
  }
}

void Omnibot::updBat()
{
  batVolt = map(analogRead(BAT_PIN), 784, 620, 126, 100) + 5;
  if (batVolt < 55) Serial.println(F("\n\rNO BATTERY")), playing = 0;
  else if (batVolt < 105) Serial.println(F("\n\rLOW VOLTAGE")), playing = 0;
  else if (batVolt < 113) Serial.print(F("\n\r                                         CHANGE BATTERY: ")), Serial.println(batVolt / 10.0);
}
void Omnibot::updIMU()
{
  while (Serial3.available()) Yaw = int(Serial3.read()) * 2 - yawZero;
  adduction(Yaw);
  ////Serial.print(" imu = ");
  ////Serial.println(Yaw);
}

void Omnibot::ZeroIMU()
{
  while (Serial3.available() > 2) Serial3.read();
  while (Serial3.available() == 0);
  //Serial.println("zero imu"); 
  if (Serial3.available()) yawZero = int(Serial3.read()) * 2;
  adduction(yawZero);
}

void Omnibot::switchLs()
{
  digitalWrite(LS_STATE_PIN, !lsState);
}

void Omnibot::updLs()
{
  Wire.requestFrom(LS_ADDR, 1);
  //delayMicroseconds(20);
  //while (!Wire.available());
  lsAngle = Wire.read() * 2;
  if (lsAngle == 0) lsAngle = 400;
  if (lsAngle != 400) lsAngle += -180, adduction(lsAngle);
  ////Serial.print(" ls = ");
  ////Serial.print(lsAngle);
}

void Omnibot::calibLs()
{
  //Serial.println(F("datchiks calibration"));
  lsState = 1;
  switchLs();
  delay(200);
  Wire.beginTransmission(LS_ADDR);
  Wire.write(CALIB_LS);
  Wire.endTransmission();
  setMotors(40, 40, 40, 40);
  for (int i = 0; i < 4; i++) writeMotor(i, sp[i]);
  while (Serial.available()) //Serial.read();
  while (!Serial.available()) delay(1);
  while (Serial.available()) //Serial.read();
  Wire.beginTransmission(LS_ADDR);
  Wire.write(CALIB_LS);
  Wire.endTransmission();
  setMotors(0, 0, 0, 0);
  for (int i = 0; i < 4; i++) writeMotor(i, sp[i]);
  delay(200);
  lsState = 0;
  switchLs();
}

void Omnibot::kick(int kickTime)
{
  if (millis() - kickerTimer > 3000) {
    digitalWrite(KICKER_PIN, 1);
    delayMicroseconds(kickTime);
    digitalWrite(KICKER_PIN, 0);
    kickerTimer = millis();
  }
}

void Omnibot::updBall()
{
  int oldAngle = ballAngle;
  Wire.requestFrom(TB_ADDR, 2);
  //delayMicroseconds(10);
  while (!Wire.available());
  ballAngle = Wire.read() * (2) + 180;
  if (ballAngle == 400) ballAngle = oldAngle;
  while (!Wire.available());
  ballDist = Wire.read();
  if (ballDist == 0) ballAngle = oldAngle;
  if (analogRead(A8) < 95 && robotNumber == 0 && HAVE_BALL_EN) haveBall = 1;
  else if (analogRead(A8) < 750 && robotNumber == 1 && HAVE_BALL_EN) haveBall = 1;
  else haveBall = 0;
  adduction(ballAngle);
  ////Serial.print(" ballAngle = ");
  ////Serial.print(ballAngle);
  ////Serial.print("; ballDist = ");
  ////Serial.print(ballDist);
  ////Serial.print("; haveBall = ");
  ////Serial.println(analogRead(A8));
}

void Omnibot::updGoals()
{
  Wire.requestFrom(CAM_ADDR, 8);
  delayMicroseconds(10);
  if (Wire.available())
  {
    goalAngle[ourGoal] = (Wire.read() | (Wire.read() << 8)) - 180 + Yaw;
    goalDist[ourGoal] = Wire.read() | (Wire.read() << 8);
    goalAngle[!ourGoal] = (Wire.read() | (Wire.read() << 8)) - 180 + Yaw;
    goalDist[!ourGoal] = Wire.read() | (Wire.read() << 8);
  }
  adduction(goalAngle[0]);
  adduction(goalAngle[1]);

  /*//Serial.print(" openMV: ");
    //Serial.print(goalAngle[0]),   //Serial.print("  ");
    //Serial.print(goalDist[0]),   //Serial.print("  ");
    //Serial.print(goalAngle[1]),   //Serial.print("  ");
    //Serial.println(goalDist[1]);*/
}

void Omnibot::moveLocal(double _rotation, double _speed, double _heading, double max_turn_speed)
{
  double w = 0, err = 0, p = 0, d = 0, P_C = 2.3, D_C = 8, I_C = 0.1, _sp[4], lim;  //2
  int max_index = 0;
  static double ic = 0, err_old = 0;
  err = -_rotation + Yaw;
  adduction(err);
  p = err * P_C;
  d = (err - err_old) * D_C; err_old = err;
  ic += err * I_C;
  if (abs(ic) > 70) ic = sgn(ic) * 70;
  if (abs(err) <= 4) ic = 0;
  w = p + d + ic;
  if (abs(w) <= 5) w = 0;
  if (abs(w) > max_turn_speed) w = sgn(w) * max_turn_speed;
  _sp[0] = sin((-_heading + _rotation + 45) * PI / 180.0) * _speed + w;
  _sp[1] = sin((-_heading + _rotation + 135) * PI / 180.0) * _speed + w;
  _sp[2] = sin((-_heading + _rotation - 135) * PI / 180.0) * _speed + w;
  _sp[3] = sin((-_heading + _rotation - 45) * PI / 180.0) * _speed + w;
  setMotors(_sp[0], _sp[1], _sp[2], _sp[3]);
}

void Omnibot::setMotors(double _speed1, double _speed2, double _speed3, double _speed4, double maxSp = 255.0)
{
  double _sp[4] = {_speed1, _speed2, _speed3, _speed4};
  double _maxSp = 0;
  maxDelta = 0;

  for (int i = 0; i < 4; i++) if (abs(_sp[i]) > maxSp && abs(_sp[i]) > _maxSp) _maxSp = abs(_sp[i]);
  if (_maxSp != 0)
  {
    for (int i = 0; i < 4; i++)
    {
      _sp[i] = _sp[i] / _maxSp * maxSp;
    }
  }

  for (int i = 0; i < 4; i++)
  {
    spDelta[i] = _sp[i] - spOld[i];
    if (abs(spDelta[i]) > abs(maxDelta) && _sp[i] != 0) maxDelta = spDelta[i], maxDeltaN = i;
  }

  for (int i = 0; i < 4; i++)
  {
    if (maxDelta != 0) sp[i] = (spOld[maxDeltaN] + maxDelta * SP_STEP * (millis() - spTime)) * _sp[i] / _sp[maxDeltaN];
    else if (_sp[i] == 0) sp[i] = 0;
    else sp[i] = spOld[i];
    if (sgn(_sp[i] - spOld[i]) != sgn(_sp[i]) - sp[i]) sp[i] = _sp[i];
  }

  for (int i = 0; i < 4; i++) spOld[i] = sp[i];
  spTime = millis();
}

void Omnibot::writeMotor(int mot, double _sp, double maxSp = 255)   //SP_STEP = sp (от -255 до 255) / время разгона (в секундах)
{
  bool dir = false;
  if (_sp > 0) dir = !dir;
  if (abs(_sp) > maxSp) _sp = maxSp;
  if (dir)
  {
    digitalWrite(motor_pins[mot * 2 + 1], HIGH);
    analogWrite(motor_pins[mot * 2], maxSp - abs(_sp));
  }
  else
  {
    analogWrite(motor_pins[mot * 2 + 1], maxSp - abs(_sp));
    digitalWrite(motor_pins[mot * 2], HIGH);
  }
}

void Omnibot::runStopRobot()
{
  if (BT_EN && playing && playingMode == 0) //Serial.println("striker -> keeper"), BT.write(BT_OK);
  setDribbler(0);
  Wire.ostanavites();
  r = 0, btFlag = 0, rotationTimer = millis();
  for (int i = 0; i < 4; i++) spOld[i] = 0;
  setMotors(0, 0, 0, 0);
  for (int i = 0; i < 4; i++) writeMotor(i, sp[i]);
  playing = !playing;
  //Serial.print(F("playing: ")); //Serial.println(playing);
  lsState = playing;
  switchLs();
  Wire.begin();
}

void Omnibot::changePlayingMode()
{
  playingMode = !playingMode;
  r = 0, btFlag = 0, rotationTimer = millis();
//  if (playingMode)//Serial.println(F("playing as striker"));
//  else //Serial.println(F("playing as keeper"));
}

void Omnibot::changeGoals()
{
  ourGoal = !ourGoal;
  EEPROM.write(1, ourGoal);
  //Serial.print("Now our goals is ");
//  if (ourGoal) //Serial.println("blue!");
//  else //Serial.println("yellow!");
}

void Omnibot::setRobotNumber()
{
  //Serial.print(F("enter robot number: "));
  while (1) {
    char number;
    if (Serial.available()) number = Serial.read();
    //Serial.println(number);
    if (number == '0')
    {
      EEPROM.write(0, 0);
      break;
    }
    if (number == '1')
    {
      EEPROM.write(0, 1);
      break;
    }
    //else //Serial.println(F("invalid robot number"));
 }
}

void Omnibot::switchDribbler()
{
  dr = !dr;
  if (dr) setDribbler(drSpeed);
  else setDribbler(0);
}

void Omnibot::setDribbler(unsigned int _sp)
{
  dr = sgn(_sp);
  dribbler.write(_sp);
}


void Omnibot::calculatePosition(){
   xPosition = (sin(radians(goalAngle[1])) * goalDist[1] + sin(radians(goalAngle[0])) * goalDist[0]) / -2;
   yPosition = (70 - cos(radians(goalAngle[1])) * goalDist[1] - cos(radians(goalAngle[0])) * goalDist[0]) / 2;
}



void Omnibot::sendDataToMonitor() {
  char chrRotate = toByte(adductionVal(Yaw), -180, 180),
  chrSpeed = toByte(Speed, 0, 400),
  chrVolt = char(batVolt),
  chrHead = toByte(Heading, -180, 180),
  chrBallDist = char(ballDist),
  chrBallDir = toByte(ballAngle, -180, 180),
  chrLine = toByte(lineAngle, -180, 180),
  chrBits = playing | haveBall << 1 | ourGoal << 2 | playingMode << 3,
  //chrXPosition = toByte(xPosition, -50, 50),
  //chrYPosition = toByte(yPosition, -22, 22),
  chrXPosition = xPosition + 128,
  chrYPosition = yPosition + 128,
  chrValue1 = toByte(value1, 0, 255);
  
  Serial.print(char(robotNumber));
  Serial.print(chrLine);
  
  Serial.print(chrBallDist);
  Serial.print(chrBallDir);
  Serial.print(chrSpeed);
  
  Serial.print(chrRotate);
  Serial.print(chrHead);
  
  Serial.print(char(90));
  Serial.print(char(30));
  Serial.print(char(20));
  Serial.print(char(35));
  
  Serial.print(chrVolt);

  Serial.print(chrBits);

  Serial.print(chrXPosition);
  Serial.print(chrYPosition);


  Serial.println(chrValue1);
  
}


