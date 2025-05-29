vespa search compare
===

vespaを使った検索の精度評価を行うツールです。
vespaへのデータフィード、検索、評価をすべて行います。

## 使い方

### セットアップ

- 環境構築

```
uv sync
.venv/bin/activate
```

- 設定変更


### データのフィード

```
$ poe feed
```

### 検索

```
$ poe search -q テスト
```

### 評価

```
$ poe eval -m wand
```