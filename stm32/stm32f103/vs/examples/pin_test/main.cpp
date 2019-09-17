#include "main.h"


int main() {
	
	sysStart();
	initUART(_UART1, 115200);
	
	initPin(C, 13, OUTPUTPP);
	

	initPin(B, 10, INPUTFL);

	delay(100);
	writeStrUART(_UART1, "\r\nStart\r\n");
	
	while (1) {
		 
		setPin(C, 13, readPin(B, 10));

	}
	
}
