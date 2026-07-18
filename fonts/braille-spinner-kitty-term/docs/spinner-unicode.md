# 终端 spinner 的 Unicode 字符范围研究

**结论先行（Unicode 17.0.0；不判断 Kitty 的具体实现）：**

- **最难产生问题的是 ASCII**：`|/-\\`（U+007C、U+002F、U+002D、U+005C）。四者都是 East_Asian_Width=Na（Narrow），无 Emoji 属性，几乎所有终端字体都有；代价是只有 4 帧，且 `-`、`|`、斜线的视觉重心并不完全一致。
- **最稳妥的非 ASCII 4 帧选择**是几何图形的窄子集 **U+25F4–U+25F7**：`◴◷◶◵`。这四个码点均为 EAW=N、没有 Emoji/Emoji_Presentation，图形是居中的圆形象限，视觉上比 Block Elements 更像固定中心 spinner。
- 若希望沿用 Block Elements，**不要把整个 U+2580–U+259F 当作单 cell 范围**：其中 U+2580–U+258F、U+2592–U+2595 是 EAW=A。应限制到 **U+2596–U+259F**（全为 EAW=N）；推荐四帧 `▖▘▝▗`（U+2596、U+2598、U+259D、U+2597），但墨迹会在 cell 的四个象限移动，中心感较弱。
- **Braille 是 4–10 帧“固定位图”最好的 Unicode 方案**：U+2800–U+28FF 全为 EAW=N，且无 Emoji 属性；常用 10 帧 `⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏`（U+280B、U+2819、U+2839、U+2838、U+283C、U+2834、U+2826、U+2827、U+2807、U+280F）。但这不能保证字体轮廓会被使用；在已观察到 Kitty 对 Braille 有特殊渲染的环境中，应把它排在 ASCII/普通几何图形之后。

## 按本项目目标的排序

这是把“跨平台、固定单 cell、无 emoji、少字体维护”，并把用户已观察到的 Kitty Braille 特殊行为作为环境约束后的排序；不是说 Unicode 为终端规定了特殊渲染规则。

1. **ASCII U+002D/U+002F/U+005C/U+007C**：跨平台和字体覆盖最佳；4 帧。
2. **Geometric Shapes 的安全子集 U+25F4–U+25F7**：单 cell 属性和视觉中心最好；4 帧；普通 Unicode 字体即可，但仍不能保证每个极简字体有字形。
3. **Block Elements 的安全子集 U+2596–U+259F**：常见、无 emoji、EAW=N；4 帧容易，扩到 8 帧可以但旋转不够均匀。
4. **Braille U+2800–U+28FF**：EAW=N、2×3/2×4 点阵、最适合 8–10 帧；当前环境的终端特殊路径和字体覆盖使其不再是“最少问题”选择。
5. **完整 Geometric Shapes U+25A0–U+25FF**：混有 A/W，并包含 Emoji 码点；只能选安全子集。
6. **Miscellaneous Symbols U+2600–U+26FF**：EAW=N/A/W 混杂且 Emoji 很多；不适合作为范围级策略。
7. **Nerd/Fira progress U+EE00–U+EE0B**：U+EE06–U+EE0B 确实是 6 个 spinner 帧，但它们属于 PUA，只在约定的字体中有意义。
8. **PUA alias（例如 U+F800–U+F83F）**：可以在自有字体中精确做成固定网格，但没有 Unicode 语义、默认宽度也是 A，且需要维护字体和发送端映射；这是受控环境 workaround，不是便携字符范围。

## 候选比较

| 候选 | 固定单 cell / EAW | Emoji presentation | 字体覆盖与终端风险 | 中心/动画适配 |
|---|---|---|---|---|
| ASCII `|/-\\` | 四个码点均 Na；仍以实际字体 advance 为准 | 无 | 覆盖近乎普遍；无 Unicode 特殊路径 | 4 帧；cell 固定但视觉重心不齐 |
| Block Elements U+2580–U+259F | **混合**：U+2580–258F=A，U+2590–2591=N，U+2592–2595=A，U+2596–259F=N | `emoji-data.txt` 无此范围 | 标准字形，通常容易找到；实现可能使用专门的 block/box 字形，但这不是 Unicode 保证 | 安全子集可做四象限；墨迹偏离中心 |
| Geometric Shapes U+25A0–U+25FF | **混合** A/N/W；安全的 U+25F4–25F7 为 N | U+25AA–U+25AB、U+25B6、U+25C0、U+25FB–U+25FE 是 Emoji；U+25FD–U+25FE 还是 Emoji_Presentation | 安全子集是普通符号，终端特殊风险低；完整范围会触发宽度/emoji 差异 | U+25F4–U+25F7 为居中圆形象限，最适合 4 帧 |
| Misc Symbols U+2600–U+26FF | N/A/W 混合；例如 U+2614–2615、U+2630–2637、U+2648–2653 为 W | 大量 Emoji；不少码点默认 Emoji_Presentation | 常依赖符号/emoji fallback，彩色或双宽风险高 | 不建议用于固定网格或 4–10 帧 |
| Braille U+2800–U+28FF | **全范围 N**；每码点是 Braille Pattern（So） | 无 Emoji 条目 | 需字体含 Braille；终端可能有自己的点阵/字体路径；本项目环境已有观察 | 2×3/2×4 点阵，最适合 8–10 帧 |
| Nerd/Fira progress U+EE00–U+EE0B | PUA，UCD 默认 EAW=A；不是 Unicode 单 cell 保证 | 无标准 Emoji，但私有字体可以任意定义外观 | 仅 Fira Code/Nerd-patched 等约定字体可靠；Nerd Fonts 还区分 mono、double、proportional glyph 版本 | U+EE06–U+EE0B 是专门的 6 帧 spinner |
| PUA alias U+F800–U+F83F | PUA，默认 EAW=A；需自定义 advance 才能固定一格 | 无标准 Emoji | 无自定义字体即 tofu/fallback；语义、映射、字体轮廓都需一起维护 | 可做任意 4–10 帧，但只适合完全受控环境 |

## 关键规范事实

1. **EAW 不是字体宽度的绝对承诺。** UAX #11 明确说 East_Asian_Width 是默认分类；实际 glyph 的显示宽度由字体给出，还可能由 layout 调整。`A`（Ambiguous）需要按上下文解析为窄或宽；Private-Use 字符默认就是 A。因此不能把整个 Block、Geometric、Misc 或任何 PUA 范围直接当作单 cell。
2. **避免 Emoji 属性比追加 VS15/VS16 更可靠。** UTS #51 定义 U+FE0E（VS15）请求文本呈现、U+FE0F（VS16）请求 emoji 呈现，但它们是给 emoji 字符的 presentation sequence；选择本身没有 Emoji 属性的 U+25F4–U+25F7、U+2596–U+259F 或 Braille 更简单稳定。
3. **PUA 没有跨字体含义。** Unicode 标准说明 PUA 的解释由私下协议决定、没有标准图表，也没有预定义的语义交换格式；U+EE00–U+EE0B 和 U+F800–U+F83F 都落在 BMP PUA U+E000–U+F8FF 内。Unicode 还明确允许实现只支持部分字符/字体，所以 fallback 不是异常，而是允许的实现选择。
4. **Fira Code 自己也把 U+EE00–U+EE0B 定义为字体约定。** 官方 `script/progress.clj` 使用 U+EE06–U+EE0B 作为六帧 spinner；官方 README 明确说程序无法检测字体是否有这些 progress glyph，只能通过类似环境变量的启发式判断。这正是其跨平台风险。

## 建议序列

- **默认、最少维护：** `|/-\\` — U+007C U+002F U+002D U+005C。
- **需要 Unicode 且重视视觉中心（4 帧）：** `◴◷◶◵` — U+25F4 U+25F7 U+25F6 U+25F5。
- **需要 Block Elements（4 帧）：** `▖▘▝▗` — U+2596 U+2598 U+259D U+2597；只使用 U+2596–U+259F 的 EAW=N 子集。
- **需要 8–10 帧并且终端明确不特判 Braille：** `⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏` — U+280B U+2819 U+2839 U+2838 U+283C U+2834 U+2826 U+2827 U+2807 U+280F。
- **不要把 U+EE00–U+EE0B 或 U+F800–U+F83F 当作通用 Unicode spinner。** 它们只有在发送端、字体、字体 fallback 和终端环境全部受控时才适合。

## 官方来源

- Unicode UCD `EastAsianWidth.txt`（U+002D/U+002F/U+005C/U+007C、Block、Geometric、Misc、Braille、PUA 的 EAW）：<https://www.unicode.org/Public/17.0.0/ucd/EastAsianWidth.txt>
- Unicode UCD `emoji-data.txt`（Emoji 与 Emoji_Presentation）：<https://www.unicode.org/Public/17.0.0/ucd/emoji/emoji-data.txt>
- Unicode UCD `Blocks.txt`（Block Elements、Geometric Shapes、Miscellaneous Symbols、Braille Patterns 的范围）：<https://www.unicode.org/Public/17.0.0/ucd/Blocks.txt>
- Unicode code charts：<https://www.unicode.org/charts/PDF/U2500.pdf>、<https://www.unicode.org/charts/PDF/U2600.pdf>、<https://www.unicode.org/charts/PDF/U2800.pdf>
- UAX #11: East Asian Width（A 的解析和“实际宽度由字体/layout 给出”）：<https://www.unicode.org/reports/tr11/>
- UTS #51: Unicode Emoji（文本/emoji presentation 与 VS15/VS16）：<https://www.unicode.org/reports/tr51/>
- Unicode Standard Chapter 2 §2.14.4（实现可只支持字符子集）：<https://www.unicode.org/versions/latest/core-spec/chapter-2/#G1750>
- Unicode Standard Chapter 23 §23.5（PUA 语义由私下协议决定）：<https://www.unicode.org/versions/latest/core-spec/chapter-23/#G19184>
- Fira Code 官方 progress glyph 说明与兼容性警告：<https://github.com/tonsky/FiraCode/blob/master/README.md>、<https://github.com/tonsky/FiraCode/blob/master/script/progress.clj>
- Nerd Fonts 官方 glyph 映射（`extra-progress_*` U+EE00–U+EE0B）及宽度变体说明：<https://github.com/ryanoasis/nerd-fonts/blob/v3.4.0/glyphnames.json>、<https://github.com/ryanoasis/nerd-fonts/blob/v3.4.0/README.md#features>
