#include "main.h"


int main() {
	
	sysStart();
	initUART(_UART1, 115200);
	initUART(_UART4, 115200, 8, 1, 0, 42);
	
	initPin(A, 6, OUTPUTPP);
	initPin(E, 3, INPUT, PU);

	delay(100);
	writeStrUART(_UART1, "\r\nStart\r\n");
		
	while (1) {
		 
		if (UARTAvailable(_UART4)) {
			printUART(_UART1, readUART(_UART4));
			writeStrUART(_UART1, "\r\n");
			setPin(A, 6, 0);
		}
		else if (UARTAvailable(_UART1)) {
			writeUART(_UART4, readUART(_UART1));
			writeStrUART(_UART4, "\r\n");
			setPin(A, 6, 0);
			delay(2000);
		}
		else if (!readPin(E, 3)) {
			writeStrUART(_UART1, "button\r\n");
			setPin(A, 6, 0);
			delay(200);
		}
		else 
			setPin(A, 6, 1);
		
	}
	
}
