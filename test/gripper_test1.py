from pymycobot import MyCobot280
import time

PORT = "/dev/ttyACM0"
BAUDRATE = 115200

mc = MyCobot280(PORT, BAUDRATE)

time.sleep(2)

print("=== Adaptive Gripper Value Test ===")

# 現在値
print("before =", mc.get_gripper_value(1))

# 最大側へ開く
print("OPEN : value = 100")
ret = mc.set_gripper_value(100, 80, 1)
print("return =", ret)

time.sleep(3)

print("after OPEN =", mc.get_gripper_value(1))

# 閉じる
print("CLOSE : value = 0")
ret = mc.set_gripper_value(0, 80, 1)
print("return =", ret)

time.sleep(3)

print("after CLOSE =", mc.get_gripper_value(1))

print("moving =", mc.is_gripper_moving())