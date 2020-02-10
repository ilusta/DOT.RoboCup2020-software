#include "main.h"

/* Pins */


int main(){
	
	sysStart();
	initUART(_UART1, 115200);	
	delay(1000);
	
	PL_ADC ADC_1 = *(new PL_ADC(ADC1));
	ADC_1.init();
	ADC_1.add(PA4);
	ADC_1.start();
	
	writeStrUART(_UART1, "\r\nStart\r\n");
	delay(300);
	
	while(1) {
		printUART(_UART1, ADC_1.read(PA4));
		writeStrUART(_UART1, "\r\n");
		
		delay(300);
	}
}
