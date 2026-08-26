# myCobotRTC

myCobotはElephant Robotics社とM5Stack社が開発した卓上ロボットアームです。

このページでは、myCobot 280 M5の制御RTコンポーネントの概要、使用方法について説明します。


## コンポーネントの仕様

myCobotRTCの仕様は以下のようになっています。

<table>
<tr>
  <th>コンポーネント名</th>
  <th>myCobot</th>
</tr>
<tr>
  <th>実装言語</th>
  <td>Python</td>
</tr>
<tr>
  <th>アクティビティ</th>
  <td>onActivated</td>
</tr>
<tr>
  <th colspan=2>サービスポート</th>
</tr>
<tr>
  <td>ポート名</td>
  <td>middle</td>
</tr>
<tr>
  <td>インターフェース名</td>
  <td>JARA_ARM_ManipulatorCommonInterface_Middle</td>
</tr>
<tr>
  <td>方向</td>
  <td>Provided</td>
</tr>
<tr>
  <td>インターフェース型</td>
  <td>JARA_ARM::ManipulatorCommonInterface_Middle</td>
</tr>
<tr>
  <th colspan=2>サービスポート</th>
</tr>
<tr>
  <td>ポート名</td>
  <td>common</td>
</tr>
<tr>
  <td>インターフェース名</td>
  <td>JARA_ARM_ManipulatorCommonInterface_Common</td>
</tr>
<tr>
  <td>方向</td>
  <td>Provided</td>
</tr>
<tr>
  <td>インターフェース型</td>
  <td>JARA_ARM::ManipulatorCommonInterface_Common</td>
</tr>
<tr>
  <th colspan=2>コンフィギュレーションパラメータ</th>
</tr>
<tr>
  <td>パラメータ名</td>
  <td>com_port</td>
</tr>
<tr>
  <td>データ型</td>
  <td>string</td>
</tr>
<tr>
  <td>デフォルト値</td>
  <td>COM3</td>
</tr>
<tr>
  <td>Widget</td>
  <td>text</td>
</tr>
<tr>
  <th colspan=2>コンフィギュレーションパラメータ</th>
</tr>
<tr>
  <td>パラメータ名</td>
  <td>baudrate</td>
</tr>
<tr>
  <td>データ型</td>
  <td>int</td>
</tr>
<tr>
  <td>デフォルト値</td>
  <td>115200</td>
</tr>
<tr>
  <td>制約条件</td>
  <td>(1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200)</td>
</tr>
<tr>
  <td>Widget</td>
  <td>radio</td>
</tr>
<tr>
  <th colspan=2>コンフィギュレーションパラメータ</th>
</tr>
<tr>
  <td>パラメータ名</td>
  <td>solenoid_pin</td>
</tr>
<tr>
  <td>データ型</td>
  <td>int</td>
</tr>
<tr>
  <td>デフォルト値</td>
  <td>2</td>
</tr>
<tr>
  <td>Widget</td>
  <td>text</td>
</tr>
<tr>
  <th colspan=2>コンフィギュレーションパラメータ</th>
</tr>
<tr>
  <td>パラメータ名</td>
  <td>motor_pin</td>
</tr>
<tr>
  <td>データ型</td>
  <td>int</td>
</tr>
<tr>
  <td>デフォルト値</td>
  <td>5</td>
</tr>
<tr>
  <td>Widget</td>
  <td>text</td>
</tr>
</table>

![image](https://user-images.githubusercontent.com/6216077/172277743-446c13f9-7bdb-4727-bd1f-ef8f2714f529.png)

## 使用方法

### 依存ソフトウェアのインストール

まず、RTCの利用には[pymycobot](https://github.com/elephantrobotics/pymycobot)、[math3d](https://pypi.org/project/math3d/)のインストールが必要です。

pymycobotをダウンロードして、以下のコマンドを実行します。

```
python setup.py install
```

次に以下のコマンドでmath3dをインストールします。

```
pip install math3d
```

以下のコマンドでnumpyをインストールします。

```
pip install numpy
```

### ハードウェア構成
使用するロボットアームは[myCobot 280 M5](https://www.switch-science.com/catalog/7141/)です。myCobot 280 Piには対応していません。

また、[吸引ポンプ](https://www.switch-science.com/catalog/7145/)を追加することもできます。

myCobot 280 M5と吸引ポンプの接続方法については、すでにいくつか参考になるサイトがあるようなのでそれを参考にしてください。

- [myCobot 入門 (5) - 吸引ポンプの使い方](https://note.com/npaka/n/nbffd7656e990)
- [8、Control suction pump](https://docs.elephantrobotics.com/docs/myCobot-en/1-introduction/6-raspberry_mycobot/pymycobot/8-control_suction_pump.html)
- [myCobot - Suction Pump](https://scrapbox.io/saitotetsuya/myCobot_-_Suction_Pump)


### 動作確認

以下にテスト用のコンポーネントを用意しました。

- [myCobotRTCTest](https://github.com/Nobu19800/myCobotRTCTest)



myCobot起動前に、デバイスマネージャでmyCobotを接続したポート名を調べてください。

次に`myCobot.conf`の以下の`COM8`をmyCobotを接続したポート名に修正してください。

```
conf.default.com_port: COM8
```

正常にmyConotを接続しているUSBシリアル変換器が認識されていない場合、以下のCP210x Windows Driversをインストールしてください。

- [CP210x USB to UART Bridge VCP Drivers](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers)


`myCobot.py`、`myCobotTest.py`を実行後、RTシステムエディタで以下のように接続してアクティブ化してください。

![image](https://user-images.githubusercontent.com/6216077/172281149-c46796c3-9718-4d9a-b147-cce1e349b87f.png)

`myCobotTest.py`を起動したウィンドウで`input command:`と表示されているので、そこにコマンドを入力するとロボットアームを操作できます。

※`run_rtc.bat`、`start.bat`を実行することで、上記の作業を自動的に実行します。ただし、ネームサーバーは起動しておく必要があります。終了する時は`exit.bat`を実行します。

### 

#### コマンド一覧

| コマンド名 | 内容 |
| ------------- | ------------- |
| moveAbs | 絶対値で指定された位置(x、y、z)[mm]へ手先を移動。入力例：`moveAbs 200 0 160` |
| moveRel | 相対値で指定された位置(x、y、z)[mm]へ手先を移動。入力例：`moveRel 20 0 10` |
| jointAbs | 絶対値で指定された角度(j0、j1、j2、j3、j4、j5)へ関節角度(degree)を制御。入力例：`jointAbs 10 0 -40 70 50 10` |
| JointRel | 相対値で指定された角度(j0、j1、j2、j3、j4、j5)へ関節角度(degree)を制御。入力例：`JointRel 0 0 -10 10 5 0` |
| pause | 一時停止 |
| resume | 動作再開 |
| stop | 停止 |
| setSpeed | 手先制御時の動作時の速度[%]を指定する。入力例：`setSpeed 20` |
| setSpeedJoint | 関節時の速度[%]を指定する。入力例：`setSpeedJoint 20` |
| setHome | 原点復帰時の関節角度[degree]を指定する。入力例：`setHome 0 0 -10 0 -10 0` |
| getHome | 原点復帰位置の関節角度[degree]を取得する。|
| goHome | 原点復帰位置へ移動する。|
| closeGripper | 吸引ポンプのソレノイドバルブを開いて、モータをオンにすることで吸引する。|
| openGripper | 吸引ポンプのソレノイドバルブを閉じて、モータをオフにすることで吸引をやめる。|
| servoOFF | サーボをオフにする |
| servoON | サーボをオンにする |

### myCobotRTCを使ったシステムの構築

myCobotを使って独自のRTシステムを開発する場合は、ロボットアーム共通インターフェースを用いる必要があります。

- [ロボットアーム制御機能共通インタフェース仕様書(SI単位系準拠 第1.0版).pdf](https://www.openrtm.org/openrtm/sites/default/files/project/5462/(SI%E5%8D%98%E4%BD%8D%E7%B3%BB%E6%BA%96%E6%8B%A0%20%E7%AC%AC1.0%E7%89%88).pdf)

myCobotRTCと接続可能なRTCを作成には、テスト用の`myCobotRTCTest`や以下のRTCが参考になります。

- https://github.com/Nobu19800/testOpenRTM-aist/blob/master/testServiceConsumer/src/testServiceConsumer.cpp

