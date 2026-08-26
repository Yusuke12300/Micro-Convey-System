from pymycobot import MyCobot280
import time

PORT = "/dev/ttyACM0"
BAUDRATE = 115200

mc = MyCobot280(PORT, BAUDRATE)

time.sleep(2)

print("=== Gripper test ===")

# Adaptive Gripperを明示的に指定
print("OPEN")
ret = mc.set_gripper_state(0, 80, 1)
print("return =", ret)
time.sleep(3)

# 初回が効かない場合があるためもう一度
print("OPEN again")
ret = mc.set_gripper_state(0, 80, 1)
print("return =", ret)
time.sleep(3)

print("CLOSE")
ret = mc.set_gripper_state(1, 80, 1)
print("return =", ret)
time.sleep(3)

print("CLOSE again")
ret = mc.set_gripper_state(1, 80, 1)
print("return =", ret)
time.sleep(3)

print("gripper value =", mc.get_gripper_value(1))
print("gripper moving =", mc.is_gripper_moving())