#include "main.h"


int main() {
	
	sysStart();
	initUART(_UART1, 115200);
	initUART(_UART3, 115200, 8, 1, 0, 42);
	
	initPin(A, 6, OUTPUTPP);
	initPin(E, 3, INPUT, PU);
	initPin(E, 2, INPUT, PU);

	delay(100);
	writeStrUART(_UART1, "\r\nStart\r\n");
	
	while (!UARTAvailable(_UART3));
	while (UARTAvailable(_UART3)) 
		zeroYaw = readUART(_UART3) * 1.5;
	writeStrUART(_UART1, "zero imu\r\n");
	
	while (1) {
		 
		if (readPin(E, 3) == 0) {
			playing = !playing;
			delay(300);
		}
		
		if (readPin(E, 4) == 0) {
			ourGoal = !ourGoal;
			delay(300);
		}
		
		if (readUART(_UART1) == 's') 
			playing = !playing;
		
		setPin(A, 6, playing);
		
		
		while (UARTAvailable(_UART3))
			Yaw = readUART(_UART3) * 1.5 - zeroYaw;
		adduction(Yaw);
		
		if (millis() - sendToMonitorTimer > 15) {
			sendDataToMonitor();
			sendToMonitorTimer = millis();
		}
		
	}
	
}


void sendDataToMonitor() {
	char chrRotate = toByte(adductionVal(Yaw), -180, 180),
	chrSpeed = toByte(Speed, 0, 400),
	chrVolt = char(batVolt),
	chrHead = toByte(Heading, -180, 180),
	chrBallDist = char(ballDist),
	chrBallDir = toByte(ballAngle, -180, 180),
	chrLine = toByte(lineAngle, -180, 180),
	chrBits = playing | haveBall << 1 | ourGoal << 2;
  
	writeUART(_UART1, char(robotNumber));
	writeUART(_UART1, chrLine);
  
	writeUART(_UART1, chrBallDist);
	writeUART(_UART1, chrBallDir);
	writeUART(_UART1, chrSpeed);
  
	writeUART(_UART1, chrRotate);
	writeUART(_UART1, chrHead);
	writeUART(_UART1, char(90));
  
	writeUART(_UART1, char(30));
	writeUART(_UART1, char(20));
	writeUART(_UART1, char(35));
  
	writeUART(_UART1, chrVolt);

	writeUART(_UART1, chrBits);
	writeStrUART(_UART1, "\r\n");
}