# Overall rover system status from ESP32 motor controller
# State machine: 0=boot, 1=ready, 2=armed, 3=driving, 4=estop, 5=error
uint8 STATE_BOOT=0
uint8 STATE_READY=1
uint8 STATE_ARMED=2
uint8 STATE_DRIVING=3
uint8 STATE_ESTOP=4
uint8 STATE_ERROR=5

uint8 state
float32 battery_v
uint8 battery_pct
float32 temperature
uint32 uptime_s
string error_msg
