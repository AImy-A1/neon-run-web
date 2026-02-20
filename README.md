# Neon Run (Web)

`Neon Run` はブラウザで動くシンプルなアクションゲームです。

## 操作
- Move: `WASD` / `Arrow Keys`
- Dash: `Space`
- Pause: `Esc`
- Restart (Game Over): `R`

## GitHub Pagesで公開する
1. GitHubで空のリポジトリを作成（例: `neon-run-web`）
2. このフォルダで以下を実行

```powershell
powershell -ExecutionPolicy Bypass -File .\setup_github_pages.ps1 -RepoUrl https://github.com/<YOUR_NAME>/<YOUR_REPO>.git
```

3. GitHubの `Settings > Pages` で `Source` を `GitHub Actions` に設定
4. Actionsの `Deploy to GitHub Pages` が成功したら公開完了

公開URL:
`https://<YOUR_NAME>.github.io/<YOUR_REPO>/`

## 補足
- ハイスコアはブラウザの `localStorage` に保存されます。
- Python / BAT は不要です。
