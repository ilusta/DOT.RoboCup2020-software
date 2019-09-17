#include <SparkFunMPU9250-DMP.h>
#include "config.h"
MPU9250_DMP imu;
unsigned short accelFSR = IMU_ACCEL_FSR;
unsigned short gyroFSR = IMU_GYRO_FSR;
unsigned short fifoRate = DMP_SAMPLE_RATE;

#define NO_MOOVE 100
int aX = 0, aY = 0, oldAx = 0, oldAy = 0, errX = 0, errY = 0;
int x = 0;
bool moove = 0;

void setup()
{
  delay(1000);
  LOG_PORT.println("init");
  delay(1000);
  initHardware();
  if (!initIMU()) while (true);
}

void loop()
{
  if (!imu.fifoAvailable() ) return;
  if (imu.dmpUpdateFifo() != INV_SUCCESS) return;
  if (imu.updateCompass() != INV_SUCCESS) return;
  logIMUData();
}

void logIMUData(void)
{
  imu.computeEulerAngles();
  x++;
  aX = int(imu.qx);
  aY = int(imu.qy);
  errX += aX - oldAx;
  errY += aY - oldAy;
  oldAx = aX;
  oldAy = aY;

  Serial1.write(int(imu.yaw) / 2);
  LOG_PORT.print(int(imu.yaw));
  LOG_PORT.print("; ");
  LOG_PORT.print(moove);

  if (x == 5)
  {
    x = 0;
    errX = abs(errX / 5);
    errY = abs(errY / 5);
    if (errX < NO_MOOVE && errY < NO_MOOVE) moove = 0;
    else moove = 1;

    LOG_PORT.print("; ");
    LOG_PORT.print(errX);
    LOG_PORT.print("; ");
    LOG_PORT.print(errY);
  }
  
  LOG_PORT.println("");
}

void initHardware(void)
{
  // Set up MPU-9250 interrupt input (active-low)
  pinMode(MPU9250_INT_PIN, INPUT_PULLUP);
  Serial1.begin(115200);
}

bool initIMU(void)
{
  if (imu.begin() != INV_SUCCESS) return false;
  // Set up MPU-9250 interrupt:
  imu.enableInterrupt(); // Enable interrupt output
  imu.setIntLevel(1);    // Set interrupt to active-low
  imu.setIntLatched(1);  // Latch interrupt output
  // Configure sensors:
  // Set gyro full-scale range: options are 250, 500, 1000, or 2000:
  imu.setGyroFSR(gyroFSR);
  // Set accel full-scale range: options are 2, 4, 8, or 16 g
  imu.setAccelFSR(accelFSR);
  // Set gyro/accel LPF: options are5, 10, 20, 42, 98, 188 Hz
  imu.setLPF(IMU_AG_LPF);
  // Set gyro/accel sample rate: must be between 4-1000Hz
  // (note: this value will be overridden by the DMP sample rate)
  imu.setSampleRate(IMU_AG_SAMPLE_RATE);
  // Set compass sample rate: between 4-100Hz
  imu.setCompassSampleRate(IMU_COMPASS_SAMPLE_RATE);
  // Configure digital motion processor. Use the FIFO to get
  // data from the DMP.
  unsigned short dmpFeatureMask = 0;
  if (ENABLE_GYRO_CALIBRATION)
  {
    // Gyro calibration re-calibrates the gyro after a set amount
    // of no motion detected
    dmpFeatureMask |= DMP_FEATURE_SEND_CAL_GYRO;
    dmpFeatureMask |= DMP_FEATURE_GYRO_CAL;
  }
  else
  {
    // Otherwise add raw gyro readings to the DMP
    dmpFeatureMask |= DMP_FEATURE_SEND_RAW_GYRO;
  }
  // Add accel and quaternion's to the DMP
  dmpFeatureMask |= DMP_FEATURE_SEND_RAW_ACCEL;
  dmpFeatureMask |= DMP_FEATURE_6X_LP_QUAT;

  // Initialize the DMP, and set the FIFO's update rate:
  imu.dmpBegin(dmpFeatureMask, fifoRate);

  return true; // Return success
}
