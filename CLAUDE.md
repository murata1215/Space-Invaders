# Space Invaders 改修記録

## 概要
Pygameを使ったスペースインベーダーゲームのデザイン改善と残機システムの実装。

## 変更内容

### デザイン変更

#### プレイヤー（砲台）
- 単純な四角形から、クラシックなスペースインベーダー風の砲台デザインに変更
- 3段構造：ベース部分、中央部分、砲身
- アクセントライン付き

#### 敵キャラクター（カニ風）
- 楕円形の胴体
- 2つの目（白目と黒目）
- 左右のハサミ（アニメーション付き）
- 6本の脚（交互に動くアニメーション）
- ステージごとに色が変化

#### UFO
- ドーム型のデザイン
- 下部に3つの点滅するライト

#### 弾
- プレイヤーの弾：光る黄色い弾（グロー効果付き）
- 敵の弾：赤いジグザグ形状

### 残機システム

- 初期残機：3機
- 被弾時の動作：
  - 残機が1減少
  - 被弾効果音（下降音）を再生
  - 1.5秒間のリスポーン待機（プレイヤーが点滅）
  - リスポーン後、画面中央に復帰
  - 敵弾がクリアされる
- 残機0でゲームオーバー
- 画面上部中央に残機アイコン（ミニ砲台）を表示

### サウンド

- `player_hit`: プレイヤー被弾時の効果音（440Hz→220Hz→110Hzの下降音）

## 追加した定数

```python
PLAYER_ACCENT_COLOR = (60, 160, 90)
STAGE_ENEMY_ACCENT_COLORS = {1-5のアクセントカラー}
BULLET_GLOW_COLOR = (255, 255, 150)
ENEMY_BULLET_COLOR = (255, 100, 100)
UFO_ACCENT_COLOR = (180, 100, 200)
PLAYER_LIVES = 3
RESPAWN_DELAY = 1.5
```

## 追加した関数

- `draw_cannon()` - 砲台の描画
- `draw_crab_enemy()` - カニ風敵の描画（アニメーション付き）
- `draw_ufo()` - UFOの描画
- `draw_player_bullet()` - プレイヤー弾の描画
- `draw_enemy_bullet()` - 敵弾の描画
- `draw_lives()` - 残機表示

## ゲーム状態に追加したフィールド

- `lives` - 残機数
- `respawn_timer` - リスポーン待機時間
- `player_visible` - プレイヤー表示フラグ
- `animation_frame` - アニメーションフレーム
- `animation_timer` - アニメーションタイマー

## 操作方法

- Enter: ゲーム開始
- ←/→: 移動
- スペース: 発射
- ESC: 終了
- R: リスタート（ゲームオーバー/クリア後）

## 技術メモ

- pygame-ce（pygame community edition）を使用（Python 3.14対応）
- pygameの標準的なdraw関数（rect, ellipse, circle, polygon, line）で描画
