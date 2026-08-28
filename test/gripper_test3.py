from pymycobot import MyCobot280
import time

PORT = "/dev/ttyUSB0"
BAUDRATE = 115200

SPEED = 80
GRIPPER_TYPE = 1   # Adaptive Gripper

# myCobotと接続
mc = MyCobot280(PORT, BAUDRATE)

time.sleep(2)

print("================================")
print(" Adaptive Gripper 開度実験")
print("================================")
print("0 ～ 100 の値を入力してください")
print("100 : 開く側")
print("0   : 閉じる側")
print("q   : 終了")
print("--------------------------------")

while True:

    command = input("gripper value > ")

    # 終了
    if command.lower() == "q":
        print("実験を終了します")
        break

    try:
        value = int(command)

        # 範囲チェック
        if value < 0 or value > 100:
            print("0～100の範囲で入力してください")
            continue

        print(f"\n指令値 = {value}")

        # グリッパを指定位置へ移動
        ret = mc.set_gripper_value(
            value,
            SPEED,
            GRIPPER_TYPE
        )

        print("return =", ret)

        # 動作を待つ
        time.sleep(2)

        # 実際の開度を取得
        actual = mc.get_gripper_value(GRIPPER_TYPE)

        print("actual =", actual)

        # 動作中か確認
        moving = mc.is_gripper_moving()

        print("moving =", moving)
        print("--------------------------------")

    except ValueError:
        print("数字または q を入力してください")