# TODO

图例：`[x]` 已完成；`[~]` 代码已完成，等待仓库设置 / 推送 / 文档；`[ ]` 未做。

来源：2026-10-31 仓库代码与构建结果审查（CI run 40612530120 / Release v2.28.0），对照 flatpak-claude-desktop 已完成的修复。

## 高

- [x] **#1 自动更新后不触发构建**：已提交的 `check-update.yml` 没有触发 build-and-deploy 的步骤，`GITHUB_TOKEN` 推送又不会触发其他工作流。master 上已有 2.28.1、2.28.2，线上仍是 2.28.0。本地工作区里已有修复（`actions: write` + `gh workflow run`），尚未提交。→ 先 pull，再提交该修复，手动触发一次构建。
- [x] **#2 OSTree 仓库提交进 git**：用 peaceiris 把整个 `deploy/`（含 `repo/objects`）推到 `gh-pages`，每次发布都让 git 历史变大，fetch 一次就是约 365MB，迟早碰到 Pages 1GB 上限。→ 移除 `peaceiris/actions-gh-pages`，改用 `upload-pages-artifact` + `deploy-pages`，Pages Source 切换为 GitHub Actions；之后可清理 `gh-pages` 分支。
- [x] **#3 软件源未 GPG 签名**（`gpg-verify=false`）。→ 移植 `scripts/sign-repo.sh`，CI 用仓库 secret 签名，公钥内嵌到 `.flatpakrepo` / `.flatpakref`，`gpg-verify=true`。
- [x] **#4 `antigravity.flatpakref` 缺少 `RuntimeRepo=`**：未配置 flathub 的用户无法解析 `org.freedesktop.Platform//25.08`。

## 中

- [ ] **#5 权限过宽**：`--filesystem=host`、`--device=all`、`--allow=devel`、`--system-talk-name=org.freedesktop.login1`，加上 `org.freedesktop.Flatpak`，沙箱基本形同虚设。→ 评估收窄到 `--filesystem=home` + `--device=dri`；无论是否收窄，README 都要逐项说明理由。
- [x] **#6 `.desktop` MimeType 注册了 `inode/directory` 与 `text/plain`**：部分桌面上可能抢走文件管理器和文本编辑器的默认关联。→ 去掉，或只保留 `x-scheme-handler/antigravity`。
- [ ] **#7 上游自带更新器**：Antigravity 是 VS Code 分支，`/app` 只读，内置更新可能反复失败或提示。→ 实测；必要时在 `product.json` 或启动参数里关闭更新。
- [x] **#8 “增量更新”不成立**：CI 每次从空 `repo` 构建，static delta 只有 from-scratch，`--prune` 无意义。→ 先拉取线上仓库再 commit，或修正 README / 主页描述。
- [x] **#9 版本提取硬编码回退 `2.24.0`**：提取失败会给新构建打旧 tag。→ 改为报错退出。
- [~] **#10 `update-checker.py`**：
  - [x] 直接取 `releases[0]`，依赖 API 返回顺序。→ 按版本比较取最大值。
  - [ ] 上游不提供校验和，SHA256 是 CI 下载后自己算的（首次使用即信任）。→ 在 README 里说明。
  - [x] metainfo 发布日期用的是脚本运行当天。→ 改取 tarball 的 `Last-Modified`，失败时回退当天。
- [x] **#11 工作流触发与并发**：`paths` 未包含 `scripts/**`、`web/**`、`antigravity.flatpakref`、`antigravity.flatpakrepo`；无 `concurrency`；同版本重新打包时 tag 不会移动；Release 未附 OSTree 归档（可选，与 Claude 仓库保持一致）。

## 低 / 文档与权限

- [x] **#12 `antigravity.sh`**：改为 `set -euo pipefail`；Wayland 检测补上 `XDG_SESSION_TYPE`；用户 flags 中的 `--enable-features` 应与默认值合并（Chromium 只认最后一个）；`TMPDIR` 改为 `$XDG_CACHE_HOME/tmp`。
- [x] **#13 清单**：仍复制并 `chmod +x` 了 `chrome-sandbox`，zypak 下用不到，可删除；`webm_encoder` 解释器补丁找不到目标字符串时静默跳过，应至少打印警告。
- [x] **#14 `.desktop`**：`Categories=Development;IDE;TextEditor;` 中 `TextEditor` 属于 Utility，主类别保持单一即可；Comment 去掉宣传语。
- [x] **#15 metainfo**：描述里的宣传语（“advanced”“seamless”）改成平实说明。
- [ ] **#16 README / 网页**：
  - 英文为默认语言，中文另存 `README.zh-CN.md` / `web/zh-CN.html`，用 Humanizer 改写，去掉 emoji 标题和“生产级”“极速”等用词。
  - README 增加“权限说明”与“已知限制”两节（含 #5、#7）。
  - 补一份 `PROJECT_CONTEXT.md`（上游分发方式、`webm_encoder` 补丁原因、构建要点）。
  - 网页只有深色主题、无手机端断点、无语言切换。
- [x] **#17 杂项**：`actions/cache` 与 flatpak-builder `cache: true` 重复缓存；工作流未安装 Runtime 依赖（Claude 仓库有这一步）；`build-local.sh` 生成 bundle 未加 `--runtime-repo`；Release 说明改为英文；Actions 升级到不再使用 Node 20 的版本。
