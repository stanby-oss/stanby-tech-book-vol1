# Vespa Language Server を Neovim で動かしてみた

> [!NOTE]
> 2025年5月開催の技術書典に記載しているサンプルコードになります。

## Neovim の組み込み LSP 機能を使いマニュアルでセットアップする

下記のコマンドを実行すると、 Neovim が起動してサンプルの `.sd` ファイルを編集することができます。

```bash
docker run -w /workspace \
-v "$PWD:/workspace" \
-e XDG_CONFIG_HOME=/workspace/sample1 \
-it --rm ubuntu:22.04 bash -c '
apt update &&
apt install -y curl unzip openjdk-17-jre software-properties-common &&
add-apt-repository -y ppa:neovim-ppa/unstable &&
apt update &&
apt install -y neovim &&
curl -Lo /root/vespa-language-server.jar https://github.com/vespa-engine
/vespa/releases/download/lsp-v2.4.1/vespa-language-server_2.4.1.jar &&
nvim schemas/blog.sd
'
```

## nvim-lspconfig で設定する

下記のコマンドを実行すると、 Neovim が起動してサンプルの `.sd` ファイルを編集することができます。

```bash
docker run -w /workspace \
  -v "$PWD:/workspace" \
  -e XDG_CONFIG_HOME=/workspace/sample2 \
  -it --rm ubuntu:22.04 bash -c '
    apt update &&
    apt install -y curl unzip openjdk-17-jre software-properties-common git &&
    add-apt-repository -y ppa:neovim-ppa/unstable &&
    apt update &&
    apt install -y neovim &&
    curl -Lo /root/vespa-language-server.jar https://github.com/vespa-engine/vespa/releases/download/lsp-v2.4.1/vespa-language-server_2.4.1.jar &&
    git clone https://github.com/neovim/nvim-lspconfig /workspace/sample2/nvim/pack/nvim/start/nvim-lspconfig &&
    nvim schemas/blog.sd
'
```
