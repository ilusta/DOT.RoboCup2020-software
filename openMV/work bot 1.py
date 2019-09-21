# eto bot 111111111111111111111111111111111111111111111111111111111111111111111111111111
import sensor, image, time, math, pyb, ustruct

def dot(x, y, color=(255, 0, 0), sz = 5): # Set dot on point coordinate
    x -= sz / 2
    y -= sz / 2
    for i in range(sz * sz):
        img.set_pixel(int(x) + (i % sz) - 1, int(y) + int(i / sz) - 1, color)

bus = pyb.I2C(2, pyb.I2C.SLAVE, addr=0x12)
bus.deinit() # Fully reset I2C device...
bus = pyb.I2C(2, pyb.I2C.SLAVE, addr=0x12)

# 11111111111111111111111111111111111111111111111111111111111111111111111111111111111111
thresholds = [(61, 100, -12, 35, 16, 62), #yellow goals -> index is 0 so code == (1 << 0)
             (23, 63, -10, 28, -62, -17)] #blue goals -> index is 2 so code == (1 << 2)

# 11111111111111111111111111111111111111111111111111111111111111111111111111111111111111

cX = 157  # bot 111111111111111111111111111111111111111111111111111111111111111111111111
cY = 114  # bot 111111111111111111111111111111111111111111111111111111111111111111111111
yX = 0
yY = 0
bX = 0
bY = 0

SMax=0
yAngle = 0
yDist = 0
bAngle = 0
bDist = 0
EXPOSURE_TIME_SCALE = 6.0


sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 1000)
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_exposure(False)
sensor.set_auto_whitebal(False) # must be turned off for color tracking
sensor.skip_frames(time = 500)
current_exposure_time_in_microseconds=  sensor.get_exposure_us()
sensor.set_auto_exposure(False, \
    exposure_us = int(current_exposure_time_in_microseconds* EXPOSURE_TIME_SCALE))
sensor.set_auto_whitebal(False)

sensor.skip_frames(time = 1000)
#sensor.set_auto_gain(False) # must be turned off for color tracking
#sensor.set_auto_exposure(False)
sensor.set_auto_whitebal(False) # must be turned off for color tracking
#sensor.skip_frames(time = 500)
#sensor.set_gainceiling();
clock = time.clock()
# Only blobs that with more pixels than "pixel_threshold" and more area than "area_threshold" are
# returned by "find_blobs" below. Change "pixels_threshold" and "area_threshold" if you change the
# camera resolution. "merge=True" must be set to merge overlapping color blobs for color codes.

while(True):
    clock.tick()
    img = sensor.snapshot()
    yS=0
    bS=0
    ySMax=0
    bSMax=0

    for blob in img.find_blobs(thresholds, pixels_threshold=50, area_threshold=50, merge=True):
        if blob.code() == 1: # yellow goal
            img.draw_rectangle(blob.rect(), color=(255,255,0), fill=1)
            #img.draw_cross(blob.cx(), blob.cy())
            yS=blob.w()*blob.h()
            if yS > ySMax:
                ySMax=yS
                yY = cY - blob.y() - blob.h() / 2
                yX = cX - blob.x() - blob.w() / 2
            #img.draw_string(blob.x() + 2, blob.y() + 2, "yellow goal")
        if blob.code() == 2: # blue goal
            img.draw_rectangle(blob.rect(), color=(50,50,255), fill=1)
            #img.draw_cross(blob.cx(), blob.cy())
            bS=blob.w()*blob.h()
            if bS > bSMax:
                bSMax=bS
                bY = cY - blob.y() - blob.h() / 2
                bX = cX - blob.x() - blob.w() / 2
#            img.draw_string(blob.x() + 2, blob.y() + 2, "blue goal")

    dot(cX, cY, color = (0,255,0), sz = 10)
#    img.draw_cross(cY - yY, cX - yX, color=(255,255,0), size = 8, thickness=3)
    dot(cX - yX, cY - yY)
#    img.draw_cross(cY - bY, cX - bX, color=(50,50,255), size = 8, thickness=3)
    dot(cX - bX, cY - bY)

    yAngle = int(math.atan2(yX, yY) / 3.14 * 180 + 180)
    yDist = int(math.sqrt(yX*yX + yY*yY))
    bAngle = int(math.atan2(bX, bY) / 3.14 * 180 + 180)
    bDist = int(math.sqrt(bX*bX + bY*bY))

    print(clock.fps(), "yellow angle:", yAngle, "dist:", yDist, "blue angle:", bAngle, "dist:", bDist)
#    print(clock.fps())
    try:
        bus.send(ustruct.pack("<4h", yAngle, yDist, bAngle, bDist), timeout=1000)

    except OSError as err:
        pass
# 11111111111111111111111111111111111111111111111111111111111111111111111111111111111111
