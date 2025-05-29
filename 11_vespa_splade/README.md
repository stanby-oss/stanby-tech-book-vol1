vespa-splade
===

これは「VespaでSPLADEを試す」記事のサンプルコードを置いているリポジトリです。

## 使い方

### コンテナの起動
- devcontainer環境を用意します
  - devcontainerを使えない場合は、以下でdockerを起動してください

```
$ docker compose up -d
```

### Vespaの設定反映
- vscodeのdevcontainerで起動した場合は、`postCreateCommand`で実行済みなのでこのステップは不要です
- workspaceコンテナ上で以下を実行し、vespaの設定を反映します

```
$ vespa deploy vespa-config
```

### Vespaのカスタムコンポーネントの追加方法
- すでにコンパイル済みのものを`vespa-config/components`においてありますが、変更する場合は再度コンパイルしてjarをコピーしてください

```
$ cd vespa-components/japanese-analyzer
$ mvn clean install
$ cp target/japanese-analyzer-bundle-1.0.0-deploy.jar ../../vespa-config/components/
```

- 反映にはvespaへの再デプロイが必要です

### 検索を試す
- vespa_search_compareのREADE.mdを参照してください