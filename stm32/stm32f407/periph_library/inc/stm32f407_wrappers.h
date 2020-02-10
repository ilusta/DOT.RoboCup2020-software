#ifndef STM32F407_WRAPPERS
#define STM32F407_WRAPPERS

#include "stm32f407_pin.h"
#include "stm32f407_UART.h"



#define ERROR(msg) writeStrUART(_UART1, msg);writeStrUART(_UART1, "\r\n")

inline void pinMode(uint16_t pin, uint8_t mode) { // Wrapper for initPin function
	if (pin < 16) initPin(A, pin % 16, mode);
	else if (pin < 32) initPin(B, pin % 16, mode);
	else if (pin < 48) initPin(C, pin % 16, mode);
	else if (pin < 64) initPin(D, pin % 16, mode);
	else initPin(E, pin % 16, mode);
}

#endif
