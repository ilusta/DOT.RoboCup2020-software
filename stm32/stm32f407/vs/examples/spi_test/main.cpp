// SPI2 (master) connected to SPI3 (slave)

#include "main.h"


#define SPI3_TX_DATA 148

int main() {
	
	sysStart();
	initUART(_UART1, 115200);
	
	initPin(B, 12, OUTPUTPP); 			//slave select
	initSPI(_SPI2, MASTER, 8, 2);
	initSPI(_SPI3, SLAVE, 8);
	
	delay(100);
	writeStrUART(_UART1, "\r\nStart\r\n");
	
	while (1) {
		
		//update slave tx buffer
		writeTxBufSPI(_SPI3, SPI3_TX_DATA); 
		
		//master
		if(UARTAvailable(_UART1)) {	
			char c = readUART(_UART1);
			writeStrUART(_UART1, "MASTER write ");
			printUART(_UART1, c);
			writeStrUART(_UART1, ", MASTER read: ");
			setPin(B, 12, 0);
			printUART(_UART1, writeSPI(_SPI2, c));
			setPin(B, 12, 1);
			writeStrUART(_UART1, "\r\n");
		}
		
		//slave
		if(SPIAvailable(_SPI3)) {													
			writeStrUART(_UART1, "SLAVE read: ");
			printUART(_UART1, readRxBufSPI(_SPI3));
			writeStrUART(_UART1, "\r\n");
		}
		
	}
	
}
