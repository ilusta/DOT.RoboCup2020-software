#include "main.h"


int main() {
	
	sysStart();
	initUART(_UART1, 115200);
	
	initI2C(_I2C1, SLOW, BIT_7);
	initI2C(_I2C2, 23, SLOW, BIT_7);
	initI2C(_I2C2, 23, 47, SLOW, BIT_7); //dual addressing capability 
	initPin(C, 13, OUTPUTPP);
	
	delay(100);
	writeStrUART(_UART1, "\r\nStart\r\n");
	
	while (1) {
		
	}
	
}
