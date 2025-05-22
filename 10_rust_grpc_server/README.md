# RustでgRPCサーバーを実装する

> [!NOTE]
> 2025年5月開催の技術書典に記載しているサンプルコードになります。

サンプルコードでサーバーを起動させる際は、以下の手順を実施する必要があります。

## 起動準備

- [task](https://taskfile.dev/installation/)をインストールします
- [Rust](https://www.rust-lang.org/tools/install)（via rustup）をインストールします
- cargo-watchをインストールします（cargo install cargo-watch）

## 起動

下記のコマンドを実行する

```sh
task up
```
実行時のログは `./.tmp/rust-grpc-server.log` で確認できます。

停止する際は

```sh
task down
```
