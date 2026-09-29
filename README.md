# kean-canvas-sync（Claude 版）

> 这是 **Claude 版**，给 Claude Code / Claude 桌面 app 用。用 OpenAI Codex 的同学请看 **Codex 版**：[kean-canvas-sync-codex](https://github.com/Moonyear817/kean-canvas-sync-codex)。

一个 [Claude Code](https://claude.com/claude-code) skill：把 Kean / 温州肯恩大学（WKU）Canvas（`kean.instructure.com`）上**还没下载的课件**，自动下载并按「学期 / 课程代码」归档到本地文件夹。

```
学习/
└── 大二秋季/
    ├── ACCT2200/   Topic 1.pdf, Topic 1 Practice Questions.pdf …
    ├── MGS2150/    26SP2150 L1.pptx, Week 3 data/ …
    └── PHIL1100/   …
```

跟 Claude 说「同步 Canvas」「Canvas 上有没有新课件」就会触发。

## 它会做什么

- 扫描本学期所有在修课程的**「文件」页和「单元（Modules）」**，不会漏掉只挂在单元里的课件。
- 和本地比对：课程文件夹里任何子文件夹中已有同名文件的都跳过；zip 已经解压过的也跳过。
- 同一份课件同时有 pdf 和 pptx 时，只下 pptx。
- 超过 20 MB 的文件先问你要不要；你说不要的会记下来，以后不再问。
- 下载后核对文件大小，放进 `学期/课程代码/` 文件夹。新学期文件夹会自动建，比如 `大二春季`。zip 会解压成同名文件夹。
- 最后给出报告：新增了什么、跳过了什么、有什么下载失败。

## 为什么要用 Chrome

学校不给学生开 Canvas API 令牌，所以只能借用你已登录的浏览器会话。实测下来，唯一既稳定、又不需要每个文件都点确认的办法，是用 [Claude in Chrome](https://chromewebstore.google.com/detail/fcoeoabgfenejglbffodgkkbkcdhcgfn) 扩展在你自己的 Chrome 里打开下载链接。skill 里记录了其他试过但走不通的办法，Claude 不会再去重试。

**Claude 不会替你输入密码**，你需要自己在 Chrome 里登录 Canvas。

## 安装

需要：macOS、Claude Code 或 Claude 桌面 app、Chrome，以及已安装并登录的 Claude in Chrome 扩展。

```bash
git clone https://github.com/Moonyear817/kean-canvas-sync-claude.git ~/.claude/skills/canvas-sync
cd ~/.claude/skills/canvas-sync
cp config.example.json config.json
```

然后编辑 `config.json`：

| 字段 | 含义 |
|---|---|
| `root` | 课件根目录，学期文件夹会建在这里面 |
| `canvas_url` | Canvas 地址 |
| `entry_year` | 入学年份（秋季入学）。用来把 `2026FA` 换算成「大二秋季」 |
| `max_mb` | 超过这个大小的文件先问你 |

## 每天自动检查（可选）

在 Claude 桌面 app 里建一个每天运行的定时任务，内容大致是：用 canvas-sync skill 同步 Canvas；无人值守，不要确认，大文件只列出不下载。

定时任务运行时，Claude app 和 Chrome 都需要开着，并且 Chrome 已登录 Canvas。

## 文件说明

- `SKILL.md`：给 Claude 的操作流程
- `scripts/local_index.py`：列出本地已有的文件
- `scripts/canvas_scan.js`：在 Canvas 页面里运行，找出缺哪些文件
- `scripts/file_downloads.py`：把「下载」文件夹里的新文件挪进课程文件夹，按需解压
- `config.example.json`：示例配置

## 许可证

[MIT](LICENSE)
