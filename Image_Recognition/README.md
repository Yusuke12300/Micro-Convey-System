# Image_Recognition

## 実装ノート

このRTCはYOLOやマーカーを使わず、RealSense D435の深度情報、対象物の実寸、カラー画像を組み合わせて識別します。RTCBuilderで生成したデータポート定義は変更していません。

| 方向 | ポート名 | データ型 | 内容 |
|---|---|---|---|
| InPort | `Target_In1` | `RTC::TimedString` | `t1`～`t4` または `[T1]`～`[T4]` の対象ID |
| OutPort | `Target_Coordinate_Out` | `RTC::TimedPoint3D` | 設定した座標系の対象物上面中心座標（m） |

処理は次の順序です。

1. D435の深度からRANSACでコンベヤまたはテーブル平面を推定します。
2. 平面より高い領域を物体候補として分離します。
3. 各候補の3次元寸法を、`config/geometry_targets.yaml` の対象物寸法と照合します。
4. カラー画像のHSV範囲と照合し、T1では白色領域の割合を判定します。
5. Cannyで得たカラーエッジと、隣接画素の距離差から得た深度エッジが候補の境界に沿うか判定します。
6. 寸法・色・両エッジの複合信頼度を計算し、12 mm以内に5回まとまった安定候補のうち最も高い座標を1回だけ出力します。
7. `config/T_arm_camera.yaml` の外部校正行列でカメラ座標からアーム基準座標へ変換します。

現在は `[T1]` に幅15 mm、長さ45 mm、高さ33 mmの直方体を設定しています。寸法が未提示のT2～T4は誤認識を防ぐため無効です。この方式では、対象物がほぼ平面上にあり、各対象物の寸法が十分に異なる必要があります。同寸法の物体を色や模様で区別する場合は、色特徴または学習モデルの追加が必要です。

### 実行前の準備

同じPython環境に依存パッケージを導入します。

```powershell
python -m pip install -r requirements.txt
```

現在は`config/geometry_targets.yaml`の`output_frame: arm`により、D435で検出した座標をMyCobot基準座標へ変換して出力します。カメラ基準ではXが画像右方向、Yが画像下方向、Zがカメラ前方です。RealSenseの深度値をdepth scaleでメートルへ変換し、内部計算、画面表示、`RTC::TimedPoint3D`への出力まで一貫してメートル単位を使用します。

`config/T_arm_camera.yaml`には、カメラ原点をMyCobot座標の`(0.2, 0.0, 0.55) m`、カメラ`+Y`をアーム`+X`、カメラ`+Z`をアーム`-Z`とする上向きZ軸の作業座標変換を設定しています。変換式は`x_arm=0.2+y_camera`、`y_arm=x_camera`、`z_arm=0.55-z_camera`です。RealSense Viewerはカメラを占有するため、RTCをActive化する前に閉じてください。

起動例：

```powershell
python Image_Recognition.py -f rtc.conf
```

入力メッセージ1件を1回の認識要求として扱います。同じIDを再送した場合も新しい要求です。4秒以内に信頼できる候補が得られない場合、誤座標は出力しません。

Active化中は`Image_Recognition - RealSense`ウィンドウに現在のカラー映像を表示します。認識中の対象IDが上部に表示され、対象物を検出すると検出領域を緑色の枠で囲み、中心位置にも緑色の印を付けます。暗い半透明パネル上の1列表示に、出力座標系、X・Y・Z座標（m）、白色一致率、カラーエッジ一致率、深度エッジ一致率、信頼度を1行ずつ5秒間表示します。`Q`または`Esc`で映像ウィンドウだけを閉じられます。

T1の白色条件は`config/geometry_targets.yaml`の`color`で調整できます。OpenCVのHSV表現を使用し、初期値では彩度90以下、明るさ130以上を白色候補とします。`min_ratio`は深度で切り出した物体領域のうち白色である必要がある割合、`confidence_weight`は最終信頼度に占める色判定の重みです。照明で白い箱が暗く写る場合は`hsv_lower`のV値を下げ、白以外を拾う場合はV値または`min_ratio`を上げます。

エッジ条件も同じYAMLの`detector`で調整できます。カラーエッジは`color_canny_low_threshold`と`color_canny_high_threshold`、深度エッジはメートル単位の`depth_edge_threshold_m`で生成します。両エッジは候補境界から`edge_search_radius_px`以内に存在する割合を評価し、それぞれの最小値を満たす候補だけを残します。

白色表面の光沢や赤外線反射で生じる小さな深度欠損を軽減するため、取得した深度フレームを視差へ変換し、空間フィルター、時間フィルター、深度への逆変換、近傍優先の穴埋めフィルターを適用してから、平面推定、寸法測定、深度エッジ抽出を行います。完全に深度が取得できない大きな反射領域はソフトウェアだけでは復元できないため、その場合はカメラまたは対象物を少し傾け、正反射を避けてください。

### 550 mm配置とMyCobotの除外

現在の初期値は、対象物上面とカメラのZ方向距離が550 mmとなる配置向けです。RTC全体では0.40～0.70 mだけを処理し、T1判定では0.47～0.63 mの外側を除外します。また、候補面積を80～2500画素、平面からの高さを15～70 mm、矩形度を0.65以上に限定し、15×45×33 mmとの寸法一致も厳しく判定します。

MyCobotについては、白い部位が色条件を通過する可能性があるため、色だけではなく、大きすぎる領域、対象寸法と異なる形状、移動により座標が安定しない領域を組み合わせて除外します。MyCobotが対象物を完全に隠す場合や、静止した部位が対象物と同じ寸法・距離に見える場合は画像特徴だけで確実に区別できないため、その場合はアーム姿勢から生成する除外マスク、または設置後に`roi_xyxy`で作業領域だけを指定してください。

### カメラ座標での動作確認

カメラ座標を再確認する必要がある場合だけ、一時的に`output_frame: camera`へ戻して次を確認します。

1. RTCをActive化します。
2. `Target_In1`へ`t1`または`[T1]`を送ります。
3. カメラ映像上と端末に、`camera`座標系のXYZが表示されることを確認します。
4. 対象物を画像の右へ動かすとXが増加、下へ動かすとYが増加、カメラから遠ざけるとZが増加することを確認します。
5. 同じ位置で数回測り、値のばらつきと実測距離を比較します。

この確認中の出力はアーム座標ではないため、アーム制御RTCへは接続しないでください。確認後は`output_frame: arm`へ戻します。

## Overview

ModuleDescription

## Description



### Input and Output



### Algorithm etc



### Basic Information

|  |  |
----|---- 
| Module Name | Image_Recognition |
| Description | ModuleDescription |
| Version | 1.0.0 |
| Vendor | VenderName |
| Category | Category |
| Comp. Type | STATIC |
| Act. Type | PERIODIC |
| Kind | DataFlowComponent |
| MAX Inst. | 1 |

### Activity definition

<table>
  <tr>
    <td rowspan="4">on_initialize</td>
    <td colspan="2">implemented</td>
    <tr>
      <td>Description</td>
      <td></td>
    </tr>
    <tr>
      <td>PreCondition</td>
      <td></td>
    </tr>
    <tr>
      <td>PostCondition</td>
      <td></td>
    </tr>
  </tr>
  <tr>
    <td rowspan="4">on_finalize</td>
    <td colspan="2">implemented</td>
    <tr>
      <td>Description</td>
      <td></td>
    </tr>
    <tr>
      <td>PreCondition</td>
      <td></td>
    </tr>
    <tr>
      <td>PostCondition</td>
      <td></td>
    </tr>
  </tr>
  <tr>
    <td>on_startup</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td>on_shutdown</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td rowspan="4">on_activated</td>
    <td colspan="2">implemented</td>
    <tr>
      <td>Description</td>
      <td></td>
    </tr>
    <tr>
      <td>PreCondition</td>
      <td></td>
    </tr>
    <tr>
      <td>PostCondition</td>
      <td></td>
    </tr>
  </tr>
  <tr>
    <td rowspan="4">on_deactivated</td>
    <td colspan="2">implemented</td>
    <tr>
      <td>Description</td>
      <td></td>
    </tr>
    <tr>
      <td>PreCondition</td>
      <td></td>
    </tr>
    <tr>
      <td>PostCondition</td>
      <td></td>
    </tr>
  </tr>
  <tr>
    <td rowspan="4">on_execute</td>
    <td colspan="2">implemented</td>
    <tr>
      <td>Description</td>
      <td></td>
    </tr>
    <tr>
      <td>PreCondition</td>
      <td></td>
    </tr>
    <tr>
      <td>PostCondition</td>
      <td></td>
    </tr>
  </tr>
  <tr>
    <td>on_aborting</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td>on_error</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td>on_reset</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td>on_state_update</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td>on_rate_changed</td>
    <td colspan="2"></td>
  </tr>
</table>

### InPorts definition

#### Target_In1



<table>
  <tr>
    <td>DataType</td>
    <td>RTC::TimedString</td>
    <td></td>
  </tr>
  <tr>
    <td>IDL file</td>
    <td colspan="2">BasicDataType.idl</td>
  </tr>
  <tr>
    <td>Number of Data</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td>Semantics</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td>Unit</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td>Occirrence frecency Period</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td>Operational frecency Period</td>
    <td colspan="2"></td>
  </tr>
</table>


### OutPorts definition

#### Target_Coordinate_Out



<table>
  <tr>
    <td>DataType</td>
    <td>RTC::TimedPoint3D</td>
    <td></td>
  </tr>
  <tr>
    <td>IDL file</td>
    <td colspan="2">ExtendedDataTypes.idl</td>
  </tr>
  <tr>
    <td>Number of Data</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td>Semantics</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td>Unit</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td>Occirrence frecency Period</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td>Operational frecency Period</td>
    <td colspan="2"></td>
  </tr>
</table>


### Service Port definition


### Configuration definition

#### camera_serial




<table>
  <tr>
    <td>DataType</td>
    <td colspan="2">String</td>
  </tr>
  <tr>
    <td>DefaultValue</td>
    <td>827112070187</td>
    <td></td>
  </tr>
  <tr>
    <td>Unit</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>Widget</td>
    <td colspan="2">text</td>
  </tr>
  <tr>
    <td>Step</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td>Constraint</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>Range</td>
    <td colspan="2"></td>
  </tr>
</table>

#### color_width




<table>
  <tr>
    <td>DataType</td>
    <td colspan="2">int</td>
  </tr>
  <tr>
    <td>DefaultValue</td>
    <td>640</td>
    <td></td>
  </tr>
  <tr>
    <td>Unit</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>Widget</td>
    <td colspan="2">text</td>
  </tr>
  <tr>
    <td>Step</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td>Constraint</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>Range</td>
    <td colspan="2"></td>
  </tr>
</table>

#### color_height




<table>
  <tr>
    <td>DataType</td>
    <td colspan="2">int</td>
  </tr>
  <tr>
    <td>DefaultValue</td>
    <td>480</td>
    <td></td>
  </tr>
  <tr>
    <td>Unit</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>Widget</td>
    <td colspan="2">text</td>
  </tr>
  <tr>
    <td>Step</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td>Constraint</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>Range</td>
    <td colspan="2"></td>
  </tr>
</table>

#### depth_width




<table>
  <tr>
    <td>DataType</td>
    <td colspan="2">int</td>
  </tr>
  <tr>
    <td>DefaultValue</td>
    <td>848</td>
    <td></td>
  </tr>
  <tr>
    <td>Unit</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>Widget</td>
    <td colspan="2">text</td>
  </tr>
  <tr>
    <td>Step</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td>Constraint</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>Range</td>
    <td colspan="2"></td>
  </tr>
</table>

#### depth_height




<table>
  <tr>
    <td>DataType</td>
    <td colspan="2">int</td>
  </tr>
  <tr>
    <td>DefaultValue</td>
    <td>480</td>
    <td></td>
  </tr>
  <tr>
    <td>Unit</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>Widget</td>
    <td colspan="2">text</td>
  </tr>
  <tr>
    <td>Step</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td>Constraint</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>Range</td>
    <td colspan="2"></td>
  </tr>
</table>

#### camera_fps




<table>
  <tr>
    <td>DataType</td>
    <td colspan="2">int</td>
  </tr>
  <tr>
    <td>DefaultValue</td>
    <td>30</td>
    <td></td>
  </tr>
  <tr>
    <td>Unit</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>Widget</td>
    <td colspan="2">text</td>
  </tr>
  <tr>
    <td>Step</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td>Constraint</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>Range</td>
    <td colspan="2"></td>
  </tr>
</table>

#### buffer_size




<table>
  <tr>
    <td>DataType</td>
    <td colspan="2">int</td>
  </tr>
  <tr>
    <td>DefaultValue</td>
    <td>8</td>
    <td></td>
  </tr>
  <tr>
    <td>Unit</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>Widget</td>
    <td colspan="2">spin</td>
  </tr>
  <tr>
    <td>Step</td>
    <td colspan="2">1</td>
  </tr>
  <tr>
    <td>Constraint</td>
    <td>1<=x<=30</td>
    <td></td>
  </tr>
  <tr>
    <td>Range</td>
    <td colspan="2"></td>
  </tr>
</table>

#### min_detection_count




<table>
  <tr>
    <td>DataType</td>
    <td colspan="2">int</td>
  </tr>
  <tr>
    <td>DefaultValue</td>
    <td>5</td>
    <td></td>
  </tr>
  <tr>
    <td>Unit</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>Widget</td>
    <td colspan="2">spin</td>
  </tr>
  <tr>
    <td>Step</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td>Constraint</td>
    <td>1<=x<=30</td>
    <td></td>
  </tr>
  <tr>
    <td>Range</td>
    <td colspan="2"></td>
  </tr>
</table>

#### confidence_threshold




<table>
  <tr>
    <td>DataType</td>
    <td colspan="2">double</td>
  </tr>
  <tr>
    <td>DefaultValue</td>
    <td>0.65</td>
    <td></td>
  </tr>
  <tr>
    <td>Unit</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>Widget</td>
    <td colspan="2">slider</td>
  </tr>
  <tr>
    <td>Step</td>
    <td colspan="2">0.05</td>
  </tr>
  <tr>
    <td>Constraint</td>
    <td>0.0<=x<=1.0</td>
    <td></td>
  </tr>
  <tr>
    <td>Range</td>
    <td colspan="2"></td>
  </tr>
</table>

#### detection_window_sec




<table>
  <tr>
    <td>DataType</td>
    <td colspan="2">double</td>
  </tr>
  <tr>
    <td>DefaultValue</td>
    <td>1.0</td>
    <td></td>
  </tr>
  <tr>
    <td>Unit</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>Widget</td>
    <td colspan="2">spin</td>
  </tr>
  <tr>
    <td>Step</td>
    <td colspan="2">0.1</td>
  </tr>
  <tr>
    <td>Constraint</td>
    <td>0.1<=x<=5.0</td>
    <td></td>
  </tr>
  <tr>
    <td>Range</td>
    <td colspan="2"></td>
  </tr>
</table>

#### depth_roi_radius




<table>
  <tr>
    <td>DataType</td>
    <td colspan="2">int</td>
  </tr>
  <tr>
    <td>DefaultValue</td>
    <td>2</td>
    <td></td>
  </tr>
  <tr>
    <td>Unit</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>Widget</td>
    <td colspan="2">spin</td>
  </tr>
  <tr>
    <td>Step</td>
    <td colspan="2">1</td>
  </tr>
  <tr>
    <td>Constraint</td>
    <td>0<=x<=10</td>
    <td></td>
  </tr>
  <tr>
    <td>Range</td>
    <td colspan="2"></td>
  </tr>
</table>

#### min_depth_m




<table>
  <tr>
    <td>DataType</td>
    <td colspan="2">double</td>
  </tr>
  <tr>
    <td>DefaultValue</td>
    <td>0.4</td>
    <td></td>
  </tr>
  <tr>
    <td>Unit</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>Widget</td>
    <td colspan="2">spin</td>
  </tr>
  <tr>
    <td>Step</td>
    <td colspan="2">0.1</td>
  </tr>
  <tr>
    <td>Constraint</td>
    <td>0.0<x<=10.0</td>
    <td></td>
  </tr>
  <tr>
    <td>Range</td>
    <td colspan="2"></td>
  </tr>
</table>

#### max_depth_m




<table>
  <tr>
    <td>DataType</td>
    <td colspan="2">double</td>
  </tr>
  <tr>
    <td>DefaultValue</td>
    <td>0.7</td>
    <td></td>
  </tr>
  <tr>
    <td>Unit</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>Widget</td>
    <td colspan="2">spin</td>
  </tr>
  <tr>
    <td>Step</td>
    <td colspan="2">0.1</td>
  </tr>
  <tr>
    <td>Constraint</td>
    <td>0.0<x<=10.0</td>
    <td></td>
  </tr>
  <tr>
    <td>Range</td>
    <td colspan="2"></td>
  </tr>
</table>

#### arm_camera_transform_file




<table>
  <tr>
    <td>DataType</td>
    <td colspan="2">String</td>
  </tr>
  <tr>
    <td>DefaultValue</td>
    <td>config/T_arm_camera.yaml</td>
    <td></td>
  </tr>
  <tr>
    <td>Unit</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>Widget</td>
    <td colspan="2">text</td>
  </tr>
  <tr>
    <td>Step</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td>Constraint</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>Range</td>
    <td colspan="2"></td>
  </tr>
</table>


## Demo

## Requirement

## Setup

### Windows

### Ubuntu

## Usage

## Running the tests

## LICENCE




## References




## Author


