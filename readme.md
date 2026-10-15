```shell
git submodule update --init --remote themes/serene
zola serve
```

## 创作方式标注

每篇文章标题下方会显示创作方式徽章，默认为「🤖 AI 辅助创作 · AI-assisted」，无需任何配置。

如果某篇文章是纯人工创作，在该文章 frontmatter 的 `[extra]` 中声明：

```toml
[extra]
authorship = "human"
```

即显示「✍️ 纯人工创作 · Human-written」。实现位于 `themes/serene-copy/templates/post.html` 与 `themes/serene-copy/sass/main.scss`（`#authorship`）。

文章列表页（各板块和标签页）顶部可以按创作方式筛选：All（混排）、Human-written、AI-assisted，人工手写的文章标题后会有 ✍︎ 标记。选择会存在浏览器里，全站列表页共用；也可以用网址参数直接打开某个视图，例如 `/posts/?by=human`。实现位于 `themes/serene-copy/templates/_authorship_filter.html`，样式在 `main.scss` 末尾。

## 评论（giscus）

文章底部的评论用 [giscus](https://giscus.app)：读者用 GitHub 登录后评论，评论存在本仓库 Discussions 的 Comments 分类里，一篇文章对应一个讨论帖（按网址路径对应，改标题不影响，改 slug 会断开）。删评论、锁帖子都在 GitHub 的 Discussions 里操作。

- 开关：各板块 `_index.md` 的 `[extra]` 里 `comment = true / false`；单篇文章可以在 frontmatter 的 `[extra]` 里写 `comment = false` 关掉。目前除 novel 外都开着。
- 配置（仓库、分类 ID、语言等）：`themes/serene-copy/templates/_giscus_script.html`。
- 配色：`static/giscus_light.css`、`static/giscus_dark.css`，取自 `sass/typography.scss`，改配色时一起改。
- 只在 shelchin.com 上加载：giscus 加载时会在仓库里建讨论帖，本地预览加载会建出带 localhost 链接的帖子，所以本地只显示一行提示。仓库根目录的 `giscus.json` 也只允许 shelchin.com 嵌入，要推到 GitHub 才生效。
- 前提：仓库开着 Discussions，并且装了 giscus 这个 GitHub App。

## 订阅（/reading）

`/reading` 列出订阅源里的文章标题、作者和日期，可以按语言、来源筛选，点标题打开原文。只保存标题和链接，不转载正文。页面上的文字都用英文。

- 增删订阅源：编辑 `data/feeds.toml`，语言名称也在这个文件里定义。name、author 请写英文。
- 手动更新：在仓库根目录运行 `python3 scripts/update_reading.py`（Python 3.11+，无需安装依赖），会生成 `data/reading.json`。`zola serve` 不监听 `data/` 目录，还会缓存读到的数据，所以本地预览时要重启 `zola serve` 才能看到新数据。
- 自动更新：`.github/workflows/update-reading.yml` 每 6 小时运行一次，有新文章时提交 `data/reading.json`，Cloudflare Pages 随之重新构建。也可以在 GitHub 的 Actions 页面手动触发。
- 页面模板：`templates/reading.html`。