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
  - `archive.org/details/identifier` (詳細ページ) - **推奨**
  - 直接ファイルURL (`.zip`, `.7z`, `.tar`, `.gz`, `.exe`, `.iso` など)
  - 一般的なURL (自動で解析を試みます)
- 圧縮ファイルを自動展開
- **重要**: 2KBのHTMLファイルを自動的にフィルタリングし、削除します

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

### 例

#### Internet Archive詳細ページからダウンロード (推奨)
```
archive_url: https://archive.org/details/msdos_Emperor_of_the_Fading_Suns_1996
```

#### 直接ファイルをダウンロード
```
archive_url: https://archive.org/download/some-file.zip/some-file.zip
```

#### 一般的なURL
```
archive_url: https://archive.org/any/page
```

## トラブルシューティング

### 2KBのHTMLファイルがダウンロードされる
**原因**: Internet ArchiveのAPIが失敗した場合、wgetがHTMLページをダウンロードしてしまいます。

**解決**: 
- 正しいInternet Archiveの詳細ページURL (`https://archive.org/details/identifier`) を使用してください
- 直接ファイルURLを使用する場合は、拡張子を含む完全なURLを指定してください
- ワークフローは自動的に2KB以下のHTMLファイルをフィルタリングします

### APIからファイルが見つからない
**原因**: 
- Identifierが間違っている
- アーカイブが非公開または削除されている
- APIのレスポンス形式が変更された

**解決**:
- URLを確認してください
- ブラウザでURLにアクセスし、ファイルが存在することを確認してください
- 直接ファイルURLを使用してください

### ダウンロードが遅い
**原因**: 大容量ファイルのダウンロードには時間がかかります

**解決**:
- 小さいファイルからテストしてください
- GitHub Actionsのタイムアウトは6時間です

### ファイルが分割されない
**原因**: 
- ファイルサイズが1.9GB以下
- 分割ツールのエラー

**解決**:
- `du -h filename` でファイルサイズを確認してください
- 1.9GB以上のファイルは自動的に分割されます

## 制限事項

- GitHub Releaseのファイルサイズ制限: 2.0GB以下
- 1.9GB以上のファイルは自動的に分割されます
- 分割されたファイルは `.z01`, `.z02` などの拡張子で保存されます
- 7z形式で分割された場合は `.7z.001`, `.7z.002` など
- GitHub Actionsの実行時間制限: 6時間
- GitHub Releaseのストレージ制限: 2GB以下のファイルのみ

## 必要条件

- GitHubリポジトリに書き込み権限が必要
- `contents: write` パーミッションが自動的に付与されます
- GitHub Actionsの実行環境 (ubuntu-latest)

## テスト

小さいファイルでテストすることをお勧めします:
```
archive_url: https://archive.org/details/test-file-123
```

## ライセンス

MIT License
