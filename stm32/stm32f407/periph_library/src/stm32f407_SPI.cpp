#include "stm32f407_SPI.h"


uint16_t _RxData[_SPIQ];
bool _available[_SPIQ];


void initSPI(unsigned int num, bool mode, uint8_t dataFrameFormat, uint16_t clkPrescaler){
	
	//clear buffers
	_RxData[num] = 0;														
	_available[num] = 0;
	
	SPI_TypeDef * spi;
	GPIO_TypeDef * prt, * prt2;
	uint8_t nss, sck, miso, mosi;
	uint8_t afNumber = 20;
	
	//select SPI register name
	switch(num){																
		case _SPI1:
			spi = SPI1;
			RCC->APB2ENR |= RCC_APB2ENR_SPI1EN;					//enable clk
			prt = A, prt2 = A, nss = 4, sck = 5, miso = 6, mosi = 7; 		//choose pins
			afNumber = 5;
			if(mode == SLAVE) NVIC_EnableIRQ(SPI1_IRQn);		//enable interrupt
			break;
		
		case _SPI2:
			spi = SPI2;
			RCC->APB1ENR |= RCC_APB1ENR_SPI2EN;
			prt = B, prt2 = B, nss = 12, sck = 13, miso = 14, mosi = 15;
			afNumber = 5;
			if(mode == SLAVE) NVIC_EnableIRQ(SPI2_IRQn);
			break;
		
		case _SPI3:
			spi = SPI3;
			RCC->APB1ENR |= RCC_APB1ENR_SPI3EN;
			prt2 = A, nss = 15, prt = C, sck = 10, miso = 11, mosi = 12;
			afNumber = 6;
			if (mode == SLAVE) NVIC_EnableIRQ(SPI3_IRQn);
			break;
	}
	
	
	if(mode == MASTER){							//for master:
		
		//set baud rate
		spi->CR1 &= ~SPI_CR1_BR;					
		switch(clkPrescaler){
			case 4: spi->CR1 |= SPI_CR1_BR_0; break;
			case 8: spi->CR1 |= SPI_CR1_BR_1; break;
			case 16: spi->CR1 |= SPI_CR1_BR_1 | SPI_CR1_BR_0; break;
			case 32: spi->CR1 |= SPI_CR1_BR_2; break;
			case 64: spi->CR1 |= SPI_CR1_BR_2 | SPI_CR1_BR_0; break;
			case 128: spi->CR1 |= SPI_CR1_BR_2 | SPI_CR1_BR_1; break;
			case 256: spi->CR1 |= SPI_CR1_BR; break;
		}		
		
		//software slave select
		spi->CR1 |= SPI_CR1_SSM;
		spi->CR1 |= SPI_CR1_SSI;
		
		initPin(prt, sck, AFPP, 0, afNumber);		//SCK pin
		initPin(prt, miso, AFPP, 0, afNumber); 		//MISO pin
		initPin(prt, mosi, AFPP, 0, afNumber); 		//MOSI pin
		
	}
	else {														//for slave:
		initPin(prt, sck, AFPP, 0, afNumber); 		//SCK pin
		initPin(prt, miso, AFPP, 0, afNumber); 		//MISO pin
		initPin(prt, mosi, AFPP, 0, afNumber); 		//MOSI pin
		
		if(prt == prt2) 
			initPin(prt, nss, AFPP, 0, afNumber); 	//NSS pin
		else 
			initPin(prt2, nss, AFPP, 0, afNumber);
		
		
	}
	
	
	//set data frame format (8 or 16 bit)
	if(dataFrameFormat == 16) spi->CR1 |= SPI_CR1_DFF;		
	else spi->CR1 &= ~SPI_CR1_DFF;
	
	//set clock polarity & clock phase
	spi->CR1 &= ~SPI_CR1_CPOL;						
	spi->CR1 &= ~SPI_CR1_CPHA;
	
	//most significant bit transmitted first
	spi->CR1 &= ~SPI_CR1_LSBFIRST;				
	
	//enable Rx interrupt
	if(mode == SLAVE)spi->CR2 |= SPI_CR2_RXNEIE;				
	
	//select mode (master or slave)
	if(mode == MASTER)spi->CR1 |= SPI_CR1_MSTR;		
	else spi->CR1 &= ~SPI_CR1_MSTR;
	
	//enable SPI
	spi->CR1 |= SPI_CR1_SPE;					
	
}


uint16_t writeSPI(unsigned int num, uint16_t TxData){						//for master
	
	//select SPI register name
	SPI_TypeDef * spi;								
	switch(num){
		case _SPI1: spi = SPI1; break;
		case _SPI2: spi = SPI2; break;
		case _SPI3: spi = SPI3; break;
	}
	
	//write data
	while(!(spi->SR & SPI_SR_TXE));		
	spi->DR = TxData;
	
	//read data
	while(!(spi->SR & SPI_SR_RXNE));
	return spi->DR;		
	
}

void writeTxBufSPI(unsigned int num, uint16_t TxData){					//for slave
	
	//select SPI register name
	SPI_TypeDef * spi;								
	switch(num){
		case _SPI1: spi = SPI1; break;
		case _SPI2: spi = SPI2; break;
		case _SPI3: spi = SPI3; break;
	}
	
	spi->DR = TxData;
	
}


uint16_t readRxBufSPI(unsigned int num){
	
	_available[num] = 0;
	return _RxData[num];
	
}

bool SPIAvailable(unsigned int num){
		return _available[num];
}

void SPIInterruptHandler(unsigned int num){					//actual interrupt handler
	
	//select SPI register name
	SPI_TypeDef * spi;								
	switch(num){
		case _SPI1: spi = SPI1; break;
		case _SPI2: spi = SPI2; break;
		case _SPI3: spi = SPI3; break;
	}
	
	if(spi->SR & SPI_SR_RXNE){
		_RxData[num] = spi->DR;
		_available[num] = 1;
	}
	
}



/************************************ interrupt handlers ************************************/


#ifdef __cplusplus
extern "C"{
#endif

void SPI1_IRQHandler(void){
	SPIInterruptHandler(_SPI1);
}

void SPI2_IRQHandler(void){
	SPIInterruptHandler(_SPI2);
}
	
void SPI3_IRQHandler(void) {
	SPIInterruptHandler(_SPI3);
}

#ifdef __cplusplus
}
#endif
