# Kitty spinner 特殊渲染调查

> 范围：仅调查 Kitty 上游的 issue、PR、commit、changelog 与当前源码；不做通用 Unicode 字符选型。\
> 上游源码快照：`master`，commit [`40bbbf68e9c9c4005252e021b0a4ae45d42a05ba`](https://github.com/kovidgoyal/kitty/commit/40bbbf68e9c9c4005252e021b0a4ae45d42a05ba)，2026-07-13。最近发布版为 [`v0.47.4`](https://github.com/kovidgoyal/kitty/releases/tag/v0.47.4)。

## 结论摘要

1. **Kitty 默认会绕过字体，软件渲染 Braille 和一批 box/block/arc 字符。** 当前 `kitty/fonts.c` 将 `U+2800–U+28FF`、`U+EE00–U+EE0B` 以及若干 Unicode box/arc 范围分类为 `BOX_FONT`；`allow_use_of_box_fonts` 默认值是 `true`。[源码](https://github.com/kovidgoyal/kitty/blob/master/kitty/fonts.c#L708-L755)
2. **`symbol_map` 无法覆盖这些字符（默认情况下）。** `font_for_cell()` 先在 switch 中返回 `BOX_FONT`，只有落入 `default` 后才调用 `in_symbol_maps()`；因此对上述范围配置 `symbol_map` 不会进入指定字体路径。[源码](https://github.com/kovidgoyal/kitty/blob/master/kitty/fonts.c#L725-L755)
3. **没有发现可在 `kitty.conf` 中关闭内部 box-font 渲染的官方配置项。** `set_allow_use_of_box_fonts(False)` 确实存在，但它是 `fast_data_types` 的源码接口，当前只在字体测试中使用，不是配置定义中的选项；将其设为 `False` 需要修改/调用 Kitty 内部代码。[接口与测试](https://github.com/kovidgoyal/kitty/blob/master/kitty/fonts.c#L2418-L2455)、[测试用法](https://github.com/kovidgoyal/kitty/blob/master/kitty_tests/fonts.py#L347-L355)、[当前配置定义](https://github.com/kovidgoyal/kitty/blob/master/kitty/options/definition.py#L78-L90)
4. **上游设计意图明确反对让用户覆盖 Braille/box drawing 字符的字体。** Kovid 在 #5910 说这些字符“不用字体渲染”，并表示不会改变；在拒绝 PR #7120 时说明，若允许覆盖，TUI 程序就不能依赖这些字符的固定外观。[#5910 评论](https://github.com/kovidgoyal/kitty/issues/5910#issuecomment-1399153380)、[#5910 设计理由](https://github.com/kovidgoyal/kitty/issues/5910#issuecomment-1399199833)、[PR #7120 评论](https://github.com/kovidgoyal/kitty/pull/7120#issuecomment-1937718983)
5. **已知的两类实际渲染问题都已有上游修复：** Braille 的垂直间隙/点间距问题是 #4499；Fira Code spinner 半径过小及粗线条上下裁剪是 #9032 / PR #9041。当前检索没有发现仍开放的 spinner 专项 issue 或 PR；唯一匹配的开放 issue 是范围很大的 Unicode 文本处理 RFC #8533，并非 spinner 内部渲染问题。[开放 issue 搜索结果](https://github.com/kovidgoyal/kitty/issues/8533)

## 当前源码事实

### 1. `BOX_FONT` 的分类和 `symbol_map` 的执行顺序

当前 `font_for_cell()` 的特殊范围包括：

- `U+2800–U+28FF`：Braille Patterns；
- `U+EE00–U+EE0B`：源码注释标为 “fira code progress bar/spinner”；
- `U+25CB`、`U+25C9`、`U+25CF`、`U+25DC–U+25E5` 等也在同一个内部渲染分类中；其中这些范围正好包含 `○`、`◉`、`●` 及四分之一/半圆 spinner 常用字符；
- 另外还有 Unicode box drawing、Powerline box drawing、legacy computing、octant、branch drawing 等范围。

当 `allow_use_of_box_fonts` 为真时，这些字符直接返回 `BOX_FONT`；`symbol_map` 的查找位于后面的 `default` 分支，因此不能覆盖它们。[`font_for_cell()`](https://github.com/kovidgoyal/kitty/blob/master/kitty/fonts.c#L725-L755)

`BOX_FONT` 的渲染路径不使用字体 face，而是调用 `render_box_cell()`，最终调用 `render_box_char(ch, ..., width, height, dpi_x, dpi_y, scale)`。[渲染路径](https://github.com/kovidgoyal/kitty/blob/master/kitty/fonts.c#L1042-L1104)、[`render_box_char` 接口](https://github.com/kovidgoyal/kitty/blob/master/kitty/fonts.c#L2432-L2441)

`box_glyph_id()` 也把 `U+EE00–U+EE0B` 所在的 PUA 区间纳入 box glyph ID 映射，并把 Braille 单独映射到内部 glyph ID。[源码](https://github.com/kovidgoyal/kitty/blob/master/kitty/fonts.c#L773-L785)

### 2. Braille 的实际内部绘制

`render_box_char()` 当前直接把 `U+2800–U+28FF` 分派到 `braille()`；`braille()` 根据八个 bit 选择两列四行的点。[源码](https://github.com/kovidgoyal/kitty/blob/master/kitty/decorations.c#L1513-L1541)、[分派表](https://github.com/kovidgoyal/kitty/blob/master/kitty/decorations.c#L2168-L2174)

当前 `braille_dot()` 使用 `distribute_dots()` 把 cell 的宽高余数分配到 gap，避免把不能整除的剩余像素全部堆到下方。[实现](https://github.com/kovidgoyal/kitty/blob/master/kitty/decorations.c#L79-L99)、[`braille_dot()`](https://github.com/kovidgoyal/kitty/blob/master/kitty/decorations.c#L1513-L1527)

### 3. `U+EE00–U+EE0B` 的 progress/spinner 映射

当前 C 源码中的映射是：

| 范围 | 当前 Kitty 内部意义 | 源码事实 |
|---|---|---|
| `U+EE00–U+EE02` | 未填充 progress bar 的左/中/右片段 | [`decorations.c`](https://github.com/kovidgoyal/kitty/blob/master/kitty/decorations.c#L1893-L1895) |
| `U+EE03–U+EE05` | 填充 progress bar 的左/中/右片段 | [`decorations.c`](https://github.com/kovidgoyal/kitty/blob/master/kitty/decorations.c#L1896-L1898) |
| `U+EE06–U+EE0B` | 六个 Fira Code spinner 弧段 | [`decorations.c`](https://github.com/kovidgoyal/kitty/blob/master/kitty/decorations.c#L1900-L1905) |

这不是字体设计上的偶然 fallback，而是 Kitty 专门实现的 PUA box drawing。上游 changelog 明确写作 “Specialize rendering for the Fira Code progress bar/spinner glyphs”。[changelog](https://github.com/kovidgoyal/kitty/blob/master/docs/changelog.rst#L1505-L1509)

相关历史 commit：

- [`36c79f3d`](https://github.com/kovidgoyal/kitty/commit/36c79f3d50a84240e73b1b2522e44184d6af5b05) — `Implement box drawing for Fira Code progress bar glyphs in PUA`；把 `U+EE00–U+EE05` 加入 `BOX_FONT`，并实现 progress bar。
- [`7d787e6c`](https://github.com/kovidgoyal/kitty/commit/7d787e6c22728ebedcc715421c6006af61b1930a) — `Implement box drawing for Fira Code spinner glyphs`；把 `U+EE06–U+EE0B` 加入并实现 spinner 弧段。

这两个 commit 的 commit message/patch 本身没有 `Fixes #...` 关联；本次检索未找到它们对应的独立 issue/PR 讨论。

### 4. 标准 Unicode spinner 字符也有内部渲染

当前 `decorations.c` 不只实现 PUA spinner，也把这些字符分派到 `spinner()`：

- `U+25CB` `○`：完整圆，level 0；
- `U+25DC–U+25E5`：四分之一/半圆弧；
- `U+25CF` `●`：填充圆；
- `U+25C9` `◉`：fish-eye。

映射见 [`decorations.c`](https://github.com/kovidgoyal/kitty/blob/master/kitty/decorations.c#L1900-L1914)；这些 codepoint 在 `font_for_cell()` 中也被纳入内部 box-font 分类。[分类源码](https://github.com/kovidgoyal/kitty/blob/master/kitty/fonts.c#L730-L738)

### 5. spinner 的几何、垂直对齐和 baseline

当前 `spinner()` 的几何是 cell 内部几何，不是字体 baseline 几何：

- `x = width / 2.0`、`y = height / 2.0`；
- 半径取 `min(x, y)` 减去实际线宽的一半（至少按 0.5px 计算）；
- 使用 `ClipRect` 防止高线宽时顶部/底部被裁切。[当前实现](https://github.com/kovidgoyal/kitty/blob/master/kitty/decorations.c#L873-L884)

`modify_font baseline` 的文档语义是调整字体 glyph 在 cell 内的位置；字体路径会把 `scaled_metrics.baseline` 传给 `render_glyphs_in_cells()`。[baseline 文档](https://github.com/kovidgoyal/kitty/blob/master/kitty/options/definition.py#L190-L202)、[字体 glyph 路径](https://github.com/kovidgoyal/kitty/blob/master/kitty/fonts.c#L1218-L1226)

而 `BOX_FONT` 路径调用 `render_box_char()` 时传入的是 cell 宽高、DPI 和 scale，没有 baseline 参数。[`render_box_cell()`](https://github.com/kovidgoyal/kitty/blob/master/kitty/fonts.c#L1071-L1097)

因此，从源码可以确认：**`modify_font baseline` 不是控制 Kitty 内部 spinner 垂直位置的开关**。box glyph 的 subscale/multicell 提取阶段另有 `calculate_regions_for_line()`，只有在 `rf.subscale_n && rf.subscale_d` 时才根据 top/bottom/center 做垂直区域处理；这不是字体 baseline 调整。[源码](https://github.com/kovidgoyal/kitty/blob/master/kitty/fonts.c#L921-L945)

`box_drawing_scale` 可以改变 box drawing 线宽（默认 `0.001, 1, 1.5, 2`），但文档没有提供禁用内部绘制的含义。[配置文档/定义](https://github.com/kovidgoyal/kitty/blob/master/kitty/options/definition.py#L204-L212)

## Issue / PR / commit 清单

### Braille 与 font-independent rendering

| 类型 | 状态 | 结论 |
|---|---|---|
| [Issue #4499 — Vertical gap between braille characters](https://github.com/kovidgoyal/kitty/issues/4499) | **CLOSED**（2022-01-12；2023 有追加评论） | 细胞高度不是 8 的整倍数时，旧算法把余数造成的间隙集中在底部；Kovid 解释了这个原因，并接受将余数分配到 gaps 的修复。issue 后来有人要求可关闭内部渲染，但没有得到配置开关。 |
| [Commit `7b816bb9`](https://github.com/kovidgoyal/kitty/commit/7b816bb96fde7c9eeb8710af1db9e602bddf06ef) | **commit 已进入主线历史**（2020-10-25；非 PR 状态） | 首次加入 font-independent Braille rendering；changelog 的官方描述是保证在所有字号正确对齐。[changelog](https://github.com/kovidgoyal/kitty/blob/master/docs/changelog.rst#L3207-L3212) |
| [Commit `19e6f706`](https://github.com/kovidgoyal/kitty/commit/19e6f70655cc092746fa2483607157009e030440) | **commit 已进入主线历史**（2022-01-12；非 PR 状态） | `Fixes #4499`；把 `braille_dot` 改成按可用空间分配点间 gap。[changelog](https://github.com/kovidgoyal/kitty/blob/master/docs/changelog.rst#L2420-L2424) |
| [Issue #5910 — Kitty still renders braille glyphs with the wrong font](https://github.com/kovidgoyal/kitty/issues/5910) | **CLOSED**（2023-01-21） | Kovid 明确说 Braille 和 box drawing 不用字体渲染，“That is not going to change”；随后解释这是为了固定外观，让终端程序可依赖其用途。 |
| [Issue #6031 — Kitty renders characters incorrectly](https://github.com/kovidgoyal/kitty/issues/6031) | **CLOSED**（2023-02-17） | 被 Kovid 标为 #5910 的 duplicate；问题同样是 unscii 等字体中的 Braille/box glyph 被 Kitty 内绘覆盖。 |
| [Issue #6776 — Allow braille characters to be rendered by font](https://github.com/kovidgoyal/kitty/issues/6776) | **CLOSED**（2023-11-01；2025 有追加评论） | 请求 toggle；Kovid 的结论是 “This has been asked and answered.” 没有新增配置。 |
| [Issue #9153 — Render Braille Unicode characters as connected vector shapes](https://github.com/kovidgoyal/kitty/issues/9153) | **CLOSED**（2025-10-26） | 请求将 Braille 变成连接的 vector shape；Kovid 再次说明这些字符有定义的外观，建议需要自定义外观时使用 Nerd Fonts 的 PUA，而不是改变 Braille 的内部语义。 |

#4499 的关键官方评论：

- Kovid 说明 Braille “are rendered independent of fonts, based on their shapes from the unicode standard”。[评论](https://github.com/kovidgoyal/kitty/issues/4499#issuecomment-1011198842)
- 对垂直 gap 的解释是：如果 cell height 不是 8 的整倍数，8 行 Braille 的剩余像素会造成底部 gap；可以修改 `braille_dot` 分配余数。[评论](https://github.com/kovidgoyal/kitty/issues/4499#issuecomment-1011241223)
- 后续要求在 kitty.conf 关闭这种覆盖的评论存在，但没有对应 option 或修复承诺。[评论](https://github.com/kovidgoyal/kitty/issues/4499#issuecomment-1399199408)

### Fira Code progress/spinner 与半径/裁剪

| 类型 | 状态 | 结论 |
|---|---|---|
| [Commit `36c79f3d`](https://github.com/kovidgoyal/kitty/commit/36c79f3d50a84240e73b1b2522e44184d6af5b05) | **commit 已进入主线历史**（2024-03-10；非 PR 状态） | 为 `U+EE00–U+EE05` 实现内部 progress bar；改动 `fonts.c` 和旧的 `fonts/box_drawing.py`。 |
| [Commit `7d787e6c`](https://github.com/kovidgoyal/kitty/commit/7d787e6c22728ebedcc715421c6006af61b1930a) | **commit 已进入主线历史**（2024-03-10；非 PR 状态） | 为 `U+EE06–U+EE0B` 实现内部 spinner 弧段。 |
| [Issue #9032 — spinner radius is smaller in 0.43](https://github.com/kovidgoyal/kitty/issues/9032) | **CLOSED**（2025-09-29） | 0.43 的新 path-fill 改动后，用户报告 `○` 与相邻 box line 不能完全接触；讨论还涉及低分辨率抗锯齿和不同线宽。 |
| [Commit `2f983c17`](https://github.com/kovidgoyal/kitty/commit/2f983c178f9d2fffb5c6fdc639e89106ec0b66bf) | **commit 已进入主线历史**（2025-09-23；非 PR 状态） | 新 path-fill 版本给 spinner 半径额外减 1px，并增加 clip；随后 #9032 暴露了半径在较粗线宽/低分辨率下过小的问题。 |
| [PR #9041 — decorations: improve spinner rendering](https://github.com/kovidgoyal/kitty/pull/9041) | **MERGED**（2025-09-29，Kovid 合并） | `Fixes #9032`；移除固定的 1px 半径缩减、将实际半线宽下限按 0.5px 处理，并把线宽纳入 `ClipRect`，修复半径偏小和上下裁切。 |
| [Commit `8abdff10`](https://github.com/kovidgoyal/kitty/commit/8abdff10f7f15c64c7ea699ca8b16f4d58ee2637) | **commit 已进入主线**（PR #9041 的 commit） | 与 PR 相同的实际修复内容；当前 `spinner()` 源码包含该算法。 |

#9032 / #9041 是目前找到的 Kitty 专项 spinner 几何 bug 修复；没有看到后续仍开放的 spinner 半径、baseline 或垂直对齐 issue。

### 相关但不是 spinner 专项

- [PR #7120 — Add support for using main font for box drawing](https://github.com/kovidgoyal/kitty/pull/7120)：**CLOSED、未合并**（2024-02-11）。作者实现了“优先用主字体”的选项；Kovid 拒绝，理由是 TUI 不能再依赖 box drawing 的固定外观。[PR 评论](https://github.com/kovidgoyal/kitty/pull/7120#issuecomment-1937718983)
- [Issue #7167 — Box drawing char misalign](https://github.com/kovidgoyal/kitty/issues/7167)：**CLOSED**（2024-02-28）。Kovid 对截图的判断是“那就是它们应有的样子”，不是一个被接受的 spinner 对齐回归。[评论](https://github.com/kovidgoyal/kitty/issues/7167#issuecomment-1969091155)
- [Issue #4700 — which characters are rendered by kitty rather than from the font?](https://github.com/kovidgoyal/kitty/issues/4700)：**CLOSED**（2022-02-14）。Kovid 当时回答由 `box_drawing.py` 的 `box_chars` 决定；当前实现已经迁移为 C 的 `fonts.c`/`decorations.c`，所以应以当前源码为准。[评论](https://github.com/kovidgoyal/kitty/issues/4700#issuecomment-1037689830)
- [Issue #8533 — RFC: Specifying how terminals process Unicode text](https://github.com/kovidgoyal/kitty/issues/8533)：**OPEN**（最后更新 2025-08-29）。这是终端 Unicode 文本分割/宽度协议的广泛 RFC，不是内部 box/spinner 渲染 issue；不能据此推断 Kitty 会改变上述范围的字体覆盖策略。

## 是否有配置可以关闭或覆盖？

### `symbol_map`

官方配置文档把 `symbol_map` 描述为把指定 codepoint 映射到某个字体，示例是 Powerline；但它没有声明能覆盖 Kitty 的 `BOX_FONT` 特殊范围。[文档定义](https://github.com/kovidgoyal/kitty/blob/master/kitty/options/definition.py#L78-L90)

在当前实现中，事实更强：对于 `U+2800–U+28FF`、`U+EE00–U+EE0B` 和同一 switch 中的 box/spinner 范围，`symbol_map` 不会被查询，因为 `BOX_FONT` 分支在它之前返回。[`font_for_cell()`](https://github.com/kovidgoyal/kitty/blob/master/kitty/fonts.c#L725-L755)

### `set_allow_use_of_box_fonts`

源码有：

```c
static bool allow_use_of_box_fonts = true;
```

并导出 `set_allow_use_of_box_fonts(val)`，把全局变量改为 Python truth value。[实现](https://github.com/kovidgoyal/kitty/blob/master/kitty/fonts.c#L708-L708)、[setter](https://github.com/kovidgoyal/kitty/blob/master/kitty/fonts.c#L2418-L2422)

它只出现在源码测试调用中，用来让测试临时走“font rendering”路径；当前 `kitty/options/definition.py` 没有对应 `opt('allow_use_of_box_fonts', ...)`，文档也没有 kitty.conf 选项。因此结论是：

- **有源码级/测试级关闭机制；**
- **没有官方的 kitty.conf 配置关闭机制；**
- **在默认 Kitty 二进制中不能靠 `symbol_map`、`modify_font baseline` 或 `box_drawing_scale` 关闭。**

`box_drawing_scale` 只控制线宽；其文档明确是四个 thin/normal/thick/very-thick 的线宽值。[定义](https://github.com/kovidgoyal/kitty/blob/master/kitty/options/definition.py#L204-L212)

## 对本项目 spinner 字符范围的 Kitty-specific 影响

1. **不要把需要 Kitty 使用字体 glyph 的 spinner 放在 `U+2800–U+28FF`。** Kitty 会把整个 Braille block 当 `BOX_FONT`，不会尊重主字体或 `symbol_map`；这是设计意图，不是尚未解决的 fallback bug。
2. **不要把需要 Kitty 使用字体 glyph 的 spinner 放在 `U+EE00–U+EE0B`。** 这 12 个 PUA codepoint 已被 Kitty 专门占用：`EE00–EE05` 是 Fira Code progress bar，`EE06–EE0B` 是 Fira Code spinner，均由软件绘制。
3. **标准 spinner 常见字符也不能假定由字体控制。** 当前 Kitty 对 `U+25CB`、`U+25C9`、`U+25CF`、`U+25DC–U+25E5` 走内部 spinner/box 绘制；因此 `symbol_map` 也不能使这些字符变成自定义字体 glyph。
4. **若目标是“在 Kitty 中验证字体本身的 spinner glyph”，候选范围必须避开 Kitty 当前 `font_for_cell()` 特殊范围。** 当前项目 AGENTS 里预留的 `U+F800–U+F83F` 不落在 Kitty 当前列出的内部范围（Kitty 另有 `U+F5D0–U+F60D` branch drawing 特殊范围，但与 `F800–F83F` 不重叠）；这是仅基于 Kitty 当前源码的观察，不是对通用 Unicode 选型的建议。[当前特殊范围](https://github.com/kovidgoyal/kitty/blob/master/kitty/fonts.c#L730-L746)
5. **不要用 `modify_font baseline` 作为内部 spinner 的对齐方案。** Kitty 内部 spinner 以 cell 的几何中心绘制；baseline 只传给字体 glyph 渲染。若改变 cell 高度/字号，内部 spinner 的实际像素几何仍应按当前 Kitty 的 cell 尺寸和 `box_drawing_scale` 重新观察；#4499 与 #9032 说明低分辨率、余数分配、线宽和抗锯齿确实曾造成视觉差异。
6. **若产品必须支持 Kitty 的默认渲染语义，`U+EE06–U+EE0B` 是可利用的 Kitty/Fira Code 专用 spinner 方案；若产品必须展示字体自定义轮廓，则它们不是合适的 Kitty codepoint。** 这里仅陈述 Kitty 的两条行为路径，不替代其他 agent 的跨终端/Unicode 选型。

## 最终状态判断

- **已解决：** Braille 点间距/垂直余数分配（#4499、`19e6f706`）；Fira/标准 spinner 的半径偏小和粗线条上下裁切（#9032、PR #9041、`8abdff10`）。
- **按设计拒绝：** 让字体或 `symbol_map` 覆盖 Braille/box drawing（#5910、#6776、PR #7120；#6031 是重复问题）。
- **没有官方关闭配置：** `set_allow_use_of_box_fonts(False)` 是内部源码/测试 hook，不是 `kitty.conf` 选项。
- **当前未解决但不针对 spinner：** #8533 是开放的广泛 Unicode 文本协议 RFC；不能当作 spinner 特殊渲染待解决 issue。
- **对字体项目最重要的 Kitty 风险：** 使用标准 Braille、`U+EE00–U+EE0B` 或 Kitty 已列出的 `U+25CB/U+25C9/U+25CF/U+25DC–U+25E5`，会得到 Kitty 的内部几何，而不是项目字体中同 codepoint 的 glyph；`symbol_map` 和 baseline 都无法改变这一点。
