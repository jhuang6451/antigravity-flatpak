# TODO

- [ ] **#7 上游自带更新器**：Antigravity 是 VS Code 分支，`/app` 只读，内置更新可能反复失败或提示。→ 真机实测；必要时在 `product.json` 或启动参数里关闭更新。结论写入 README“已知限制”。
- [ ] **确认 Actions 均运行在 Node 24**：`flatpak/flatpak-github-actions/flatpak-builder@v6` 尚未核实。
- [ ] **清理旧的 `gh-pages` 分支**：Pages 已改为 GitHub Actions 部署，该分支不再使用。
- [ ] **评估去掉 `--system-talk-name=org.freedesktop.login1` 与 `--allow=devel`**：目前保留，未测试去掉后的影响。
