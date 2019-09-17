#include "stm32f4xx.h"
#include "stdbool.h"
#include "math.h"


#define stp(x, val) (x > val ? val : (x < -val ? -val : x))

inline void adduction(auto &x)
{
	while (x > 180) x -= 360;
	while (x < -180) x += 360;
}

inline float adductionVal(auto x)
{
	while (x > 180) x -= 360;
	while (x < -180) x += 360;
	return x;
}

inline int sgn(double x)
{
	if (x > 0) return 1;
	else if (x < 0) return -1;
	else return 0;
}

inline char toByte(auto x, int32_t start, int32_t fin)
{
	if (x > fin) x = fin;
	if (x < start) x = start;
	return char(255.0 * (float(x - start) / float(fin - start)));
}
