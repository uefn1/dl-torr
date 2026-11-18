# Internet Archive to GitHub Release Uploader

GitHub Actionsワークフローを使用して、Internet Archiveからファイルをダウンロードし、GitHub Releaseにアップロードするツールです。

## 機能

### プロセス1: ストレージ確保
- `jlumbroso/free-disk-space` を利用して不要なファイルを削除
- GitHub Actionsランナーのディスク容量を確保

### プロセス2: パッケージインストール
- 必要なパッケージを自動インストール
  - `wget`, `curl`, `zip`, `unzip`, `p7zip-full`, `jq`, `file`

### プロセス3: ダウンロード
- Internet Archive URLからファイルをダウンロード
- サポートする形式:
  - archive.org/details/xxx (詳細ページ)
  - 直接ファイルURL (.zip, .7z, .tar, .gz, .exe, .iso など)
  - 一般的なURL
- 圧縮ファイルを自動展開

### プロセス4: フォルダ構造の処理
- GitHub Releaseではフォルダのアップロードが出来ないため
- フォルダ内のファイルを `/` 区切りのファイル名にリネーム
- 例: `games/i.txt`, `games/test.exe`

### プロセス5: 大容量ファイルの分割
- GitHub Releaseでは1ファイル2.0GiB未満のファイルのみアップロード可能
- 1.9GiB以上のファイルは自動的に分割
- zip形式または7z形式で1.9GiBごとに分割

### プロセス6: Release作成
- GitHub Releaseを自動作成
- タグ名とリリース名はカスタマイズ可能

### プロセス7: ファイルアップロード
- 処理済みのファイルをGitHub Releaseにアップロード
- 自動リトライ機能付き

### プロセス8: クリーンアップ
- 一時ファイルを削除
- ワークフローを終了

## 使い方

### 1. ワークフローファイルを設定

リポジトリに `.github/workflows/download-archive.yml` ファイルが自動的に作成されます。

### 2. ワークフローを実行

1. GitHubリポジトリの **Actions** タブを開く
2. **Download from Internet Archive and Upload to Release** ワークフローを選択
3. **Run workflow** ボタンをクリック
4. 次のパラメータを入力:
   - `archive_url`: Internet ArchiveのURL (必須)
   - `release_name`: リリース名 (任意)
   - `release_tag`: リリースタグ (任意)
5. **Run workflow** をクリック

### 例: Internet Archiveからダウンロード

```
archive_url: https://archive.org/details/msdos_Emperor_of_the_Fading_Suns_1996
```

### 例: 直接ファイルをダウンロード

```
archive_url: https://archive.org/download/some-file.zip/some-file.zip
```

## 制限事項

- GitHub Releaseのファイルサイズ制限: 2.0GB以下
- 1.9GB以上のファイルは自動的に分割されます
- 分割されたファイルは `.z01`, `.z02` などの拡張子で保存されます
- 7z形式で分割された場合は `.7z.001`, `.7z.002` など

## 必要条件

- GitHubリポジトリに書き込み権限が必要
- `contents: write` パーミッションが自動的に付与されます
- GitHub Actionsの実行環境 (ubuntu-latest)

## トラブルシューティング

### ダウンロードに失敗する
- URLが正しいことを確認してください
- Internet ArchiveのURL形式を確認してください
- 直接ファイルURLの場合、拡張子を確認してください

### ファイルが分割されない
- ファイルサイズが正確に計算されていることを確認
- `du -h filename` コマンドでサイズを確認

### アップロードに失敗する
- GitHub Tokenの権限を確認
- ファイル名に無効な文字が含まれていないか確認
- 2.0GB以上のファイルが含まれていないか確認

## ライセンス

MIT License
