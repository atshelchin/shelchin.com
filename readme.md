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