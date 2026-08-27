# Image_Recognition

## 実装ノート

このRTCはYOLOやマーカーを使わず、RealSense D435の深度情報、対象物の実寸、カラー画像を組み合わせて識別します。出力ポートは`Startup_Generation_Before`の入力に合わせています。

| 方向 | ポート名 | データ型 | 内容 |
|---|---|---|---|
| InPort | `Target_In1` | `RTC::TimedString` | `t1`～`t4` または `[T1]`～`[T4]` の対象ID |
| OutPort | `target_point` | `RTC::TimedPoint3D` | 設定した座標系の対象物上面中心座標（m） |

処理は次の順序です。

1. D435の深度からRANSACでコンベヤまたはテーブル平面を推定します。
2. 平面より高い領域を物体候補として分離します。
3. 各候補の3次元寸法を、`config/geometry_targets.yaml` の対象物寸法と照合します。
4. カラー画像のHSV範囲と照合し、T1では黒色領域の割合を判定します。
5. Cannyで得たカラーエッジと、隣接画素の距離差から得た深度エッジが候補の境界に沿うか判定します。
6. 深度が欠けて通常検出できない場合は、HSV色領域の45×33 mm形状を照合し、既知の対象面距離0.455 mで3次元中心を求めます。
7. 寸法・色・エッジの複合信頼度を計算し、20 mm以内に5回まとまった安定候補のうち最も高い座標を1回だけ出力します。
8. `config/T_arm_camera.yaml` の外部校正行列でカメラ座標からアーム基準座標へ変換します。
9. アーム基準座標のX–Y平面距離がMyCobotの到達限界280 mm以上なら、`target_point`へは出力しません。

現在は、`[T1]`に黒色、`[T2]`に赤色の15×45×33 mmの直方体を設定しています。画像のように45×33 mm面を白い地面へ置くため、真下向きカメラから見える面も45×33 mm、地面からの高さは15 mmです。対象面を点群の主平面として測定し、その3次元中心を出力します。同じ外形寸法のT1・T2はHSV色特徴で区別し、T1は低明度、T2の赤色はOpenCVの色相境界をまたぐ2範囲を組み合わせて判定します。寸法が未提示のT3・T4は誤認識を防ぐため無効です。

候補点群へもう一度RANSACを適用し、白い地面ではなく対象物の水平な上面だけを抽出して測定します。これはRealSense2ToPCと同様に深度画素をXYZ点群として扱う方法で、画像上の見かけ寸法ではなく3次元の実寸で照合します。

### 実行前の準備

同じPython環境に依存パッケージを導入します。

```powershell
python -m pip install -r requirements.txt
```

現在は`config/geometry_targets.yaml`の`output_frame: arm`により、D435で検出した座標をMyCobot基準座標へ変換して出力します。カメラ基準ではXが画像右方向、Yが画像下方向、Zがカメラ前方です。RealSenseの深度値をdepth scaleでメートルへ変換し、内部計算、画面表示、`RTC::TimedPoint3D`への出力まで一貫してメートル単位を使用します。

`config/T_arm_camera.yaml`には、横から見た配置図に従い、カメラ原点をMyCobot座標の`(-0.30, 0.0, 0.47) m`、カメラの`+Z`光軸をMyCobotの`-Z`方向へ向けた真下向きの変換を設定しています。カメラ`+Y`はMyCobot`-X`、右手系を保つためカメラ`+X`はMyCobot`-Y`に対応します。変換式は`x_arm=-y_camera-0.30`、`y_arm=-x_camera`、`z_arm=0.47-z_camera`です。変換後の座標は画面、端末ログ、`target_point`へメートル単位で出力されます。RealSense Viewerはカメラを占有するため、RTCをActive化する前に閉じてください。

起動例：

```powershell
python Image_Recognition.py -f rtc.conf
```

入力メッセージ1件を1回の認識要求として扱います。同じIDを再送した場合も新しい要求です。画像処理が重い環境でも5回の安定判定を完了できるよう、認識要求は最大15秒待機します。15秒以内に信頼できる候補が得られない場合、誤座標は出力しません。`target_point`のXYZは、変換後のメートル単位の値を小数点以下3桁（0.001 m単位）に丸めて送信します。アーム基準座標では、この丸め後のX・Yから求めた平面距離が280 mm以上の場合も送信せず、その認識要求を完了します。

`Startup_Generation_Before`へ送る場合は、RTSystemEditorで`Image_Recognition0.target_point`から`Startup_Generation_Before0.target_point`へ接続してください。両ポートとも`RTC::TimedPoint3D`です。未接続または書き込み失敗時は認識結果を直ちに破棄せず、現在の認識要求が有効な間は再送し、プレビューへ`Output not connected; retrying`、端末へ接続先を表示します。

Active化中は`Image_Recognition - RealSense`ウィンドウに現在のカラー映像を表示します。認識中の対象IDが上部に表示され、対象物を検出すると検出領域を緑色の枠で囲み、中心位置にも緑色の印を付けます。緑枠は候補検出を表し、座標送信完了を表すものではありません。安定判定中は`Not sent: checking stability`、送信成功時は`Sent to target_point`、タイムアウト時は`Not sent: ... timed out`を表示します。X–Y平面距離が280 mm以上なら座標を送信せず、赤字で`Not sent: outside 280 mm XY reach`と5秒間表示します。暗い半透明パネル上の1列表示に、出力座標系、小数点以下3桁のX・Y・Z座標（m）、色一致率、カラーエッジ一致率、深度エッジ一致率、信頼度を1行ずつ5秒間表示します。カラー映像を深度解像度へ拡大すると生じる黒点を避けるため、現在はネイティブの640×480カラー画像を基準に深度画像を位置合わせしています。通常は`Target_In1`へ`t1`/`t2`を送って認識を開始します。単体確認では映像ウィンドウを選択して数字キー`1`（黒T1）または`2`（赤T2）を押しても開始できます。キー操作でも座標出力まで行うため、実機を動かさない確認時は下流RTCまたはMyCobotを停止してください。`Q`または`Esc`で映像ウィンドウだけを閉じられます。

T1の黒色条件は`config/geometry_targets.yaml`の`color`で調整できます。OpenCVのHSV表現を使用し、初期値では明度Vが80以下の画素を黒色候補とし、候補領域の45%以上が黒色であることを要求します。`min_ratio`は深度で切り出した物体領域のうち黒色である必要がある割合、`confidence_weight`は最終信頼度に占める色判定の重みです。照明で黒い対象が明るく写る場合は`hsv_upper`のV値を少し上げ、影や暗い異物を拾う場合はV値を下げるか`min_ratio`を上げます。

T2の赤色条件は、色相0～12と168～179、彩度100以上、明るさ70以上です。`Target_In1`へ`t2`または`[T2]`を送ると、同寸法の候補から赤色領域だけを対象として認識します。

エッジ条件も同じYAMLの`detector`で調整できます。カラー画像を5×5で平滑化してからCannyエッジを生成し、細かい撮像ノイズを抑えます。深度エッジはメートル単位の`depth_edge_threshold_m`で生成します。エッジ画像は認識の内部評価だけに使用し、表示用カラー画像へは合成しません。

白背景は黒いT1との明度差が大きいため、RGBの黒色割合とカラーエッジの判定では有利です。一方、影、黒い配線、MyCobotの暗い部品も黒色候補になるため、照明を拡散させ、背景へ強い影が落ちないようにしてください。また、黒い材質や光沢面ではRealSenseの深度が大きく欠ける場合があります。起動時に対応機種の赤外線エミッター、自動露出、`High Density`プリセットを有効化し、小さな欠損には視差変換、空間・時間フィルター、穴埋めを適用します。通常の深度検出が成立しない場合は、色・見かけ寸法・カラーエッジを検証したうえで`color_fixed_depth_fallback.camera_distance_m: 0.455`を使用します。このフォールバックはカメラと対象面の高さが固定されていることを前提とします。

RealSenseの時間フィルターは過去の深度を内部に保持するため、対象物やMyCobotを移動した後も古い輪郭が残る場合があります。このRTCでは認識要求を開始するたびに時間フィルターを作り直し、現在の画像を3フレーム蓄積してから検出を開始します。これにより、繰り返し認識したときの履歴蓄積による精度低下を防ぎます。

### 真下向き配置とMyCobotの除外

現在の初期値は、白い地面までの距離が470 mmで、カメラを真下へ向け、対象物を45×33 mmの面を下にして置く配置用です。このとき高さは15 mm、カメラから見える面までの基準距離は455 mmです。対象物を画面内の様々な位置へ配置できるように、T1・T2の期待距離を`0.455±0.080 m`（0.375～0.535 m）、RTC全体の処理範囲を0.35～0.55 m、平面からの高さ候補を7～25 mmに設定しています。候補面積は50～5000画素、矩形度は0.45以上です。見える45×33 mm面と3D外形の15×45×33 mmを照合します。初期ROIの`[80, 25, 510, 330]`は640×480画像上の白い台紙を囲み、手前のMyCobot・コンベヤー部品と台紙外の床を検出対象から外します。カメラまたは台紙を動かした場合は、このROIを再調整してください。

`T_arm_camera.yaml`の現在の回転行列は、カメラ位置がMyCobot原点からX方向へ`-0.30 m`、Z方向へ`+0.47 m`で、光軸が鉛直下向きの場合に対応します。設置位置、カメラの水平回転、または光軸の傾きを変更した場合は、実測値に合わせて同ファイルを再校正してください。

MyCobotについては、黒い配線や暗い関節部がT1の色条件を通過する可能性があるため、白い台紙内へ固定したROI、対象物の高さ・寸法、領域の大きさ、座標の安定性を組み合わせて除外します。MyCobotが台紙内へ入り対象物を完全に隠す場合や、静止した部位が対象物と同じ寸法・距離に見える場合は、画像特徴だけでは確実に区別できません。

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

#### target_point



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
    <td>0.60</td>
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
    <td>0.3</td>
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
    <td>0.9</td>
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


