---
name: chinese-job-platforms
description: "Drive BOSS/智联/51Job/猎聘 via computer_use on Windows."
version: 1.0.0
platforms: [windows]
metadata:
  hermes:
    tags: [job-hunt, computer-use, browser, china, recruitment]
    category: productivity
    related_skills: [job-hunt, computer-use]
---

# Chinese Job Platform Navigation

Workflows for using `computer_use` to drive Chinese recruitment websites
(BOSS直聘 / 智联招聘 / 前程无忧 / 猎聘) on Windows Chrome in background mode.

## When to Use

用户说"帮我投简历"、"投几个实习"、"开始海投" — 需要手动用 computer_use
驱动浏览器投简历时。

**配合**: `job-hunt` skill (工具层), 本 skill 补充 per-site 操作流程。

## Prerequisites

- `computer_use` tool available (cua-driver installed)
- Chrome running with the target sites already open in tabs
- 用户作业指南(首次或操作前应先阅读): `E:/npe_get_jobs_backup/docx/` 各平台docx
- 已登录BOSS/智联/51Job/猎聘 并确认登录状态(右上角有用户名非"登录/注册")

## Windows Chrome Background Mode Caveats

- **`scroll` action doesn't work** on `Chrome_WidgetWin_1` windows.
  Use `key` with `keys="pagedown"` / `keys="pageup"` instead.
- **`set_value` on search box does NOT submit the search**. You must
  also click the "搜索" (search) button after setting the value.
- **Click by element index** (from SOM capture) is reliable; pixel
  coordinates are for fallback only.
- **`app="chrome.exe"`** (小写 .exe 后缀) 是唯一正确的 scope 写法。`app="Google Chrome"` 会匹配到 msedge.exe 的离屏渲染源(0x0 / 负坐标 -32196),即使 `list_apps` 显示 Chrome PID 存在,仍会失败。`app="chrome"`(无后缀)有时也 OK,但 `chrome.exe` 最稳。**先 `focus_app app="chrome.exe"` 拿到焦点,再 `capture app="chrome.exe"`** 才能稳定取到 1500+ 元素的真实窗口。

## ⛔ 第一步：读用户操作指南（每次开始前必须做）

**投递前必须先读 `E:\npe_get_jobs_usb\docx\` 下的5份docx文件**。这些是用户亲手写的操作流程，是所有操作的权威来源。不要凭记忆操作——每次会话都重新读一遍。

读完后再执行下面的步骤。

## 必须做的三件事（读完docx后检查）

### 0. 先确认简历方向（用户可能有多份简历）

用户可以有多份不同方向的简历（如Python实习 / 数据分析 / 运营等）。
**必须先问清楚今天投哪个方向**，再读取对应简历建立画像。

> 示例: "我有五份简历，今天只投Python实习生" → 用Python方向的简历提取画像。

### 1. 制作用户画像并匹配岗位

读用户简历 → 建立画像 → 投递前快速判断匹配度。

**用户画像关键字段**: 学校/专业/年级、技能栈、语言、城市、目标岗位类型、GPA/排名

**快速匹配检查表**（快速模式用）:

| 匹配项 | ✅ 通过 | ❌ 跳过 |
|--------|--------|--------|
| 岗位类型 | Python/数据/开发 相关 | 纯Java/C++/前端/运营 |
| 实习标签 | 含"实习"、"在校生"、"经验不限" | 无实习字样、月薪上万 |
| 学历 | 本科/学历不限/"大专"(本可投) | "硕士及以上" |
| 城市 | 广州 | 其他城市 |
| 经验 | 经验不限/应届(可) | 1年以上 |

**注意**: 用户是工商管理辅修大数据,非纯计算机。优先投写"专业不限""计算机相关""在校生"的,跳过明确要求纯计算机/软件工程专业的。

### 2. 选择模式

**默认快速模式 🏃,不需要问用户**。用户已明确表示总是使用快速模式:

- **快速模式** 🏃(默认): 只看岗位卡片(标题/薪资/城市/学历/经验),不进详情页读JD。快速扫投
- **深度模式** 🔍: 读完整职位描述,LLM分析匹配度再决定。仅在用户主动要求时使用

### 3. 遵守平台特定的返回方式

**这是三个关键中最容易犯错的地方**。每个平台的弹窗处理和返回方式都不一样,混用会丢失搜索结果。

详见下方各平台说明。

## 用户教程参考 (操作前必读)

用户操作指南在 `E:\npe_get_jobs_usb\docx\` (5 份 docx,**开始投递前必读**对应平台):
- `boss的主页面.docx` — BOSS直聘完整流程(含校招/校招应届区分)
- `快速模式详细以boss直聘为例.docx` — 快速模式筛选标准
- `智联招聘的登录界面.docx` — 智联流程(点 X 关弹窗 + 点左 tab 返回)
- `前程无忧的界面.docx` — 前程流程(点浏览器顶端返回箭头)
- `猎聘操作指南.docx` — 猎聘流程(两个"聊一聊"都可点)

**重要**: 路径是 `E:\npe_get_jobs_usb\docx\` 不是 `E:\npe_get_jobs_backup\docx\`(旧路径已不存在)。

### 提示词要求 (用户明确要求)
docx 中明确要求 LLM **必须写提示词给用户审查**,两类:
1. **文本匹配**(DeepSeek):输入岗位标题/公司/薪资/城市/学历/经验/JD,输出 `{match, score, reason, red_flags}` JSON
2. **图像识别**(多模态):输入岗位详情截图,识别红字警告/标签/薪资/学历/经验
3. 写好后**告诉用户审查**,用户确认后再开始投递。提示词模板见 `references/job-match-prompts.md`

### 快速模式硬性 PASS 规则(从 docx 提炼)
- 标题必须含"实习"/"实习生"
- 城市必须含"广州"
- 学历:本科/大专/不限/在校 → 跳过明确写"硕士/研究生/博士/应届"
- 薪资:元/天 或 K/月且K<7(实习档)→ 跳过 K>=8(正式岗)
- 经验:经验不限/应届/在校/1年以下 → 跳过 X>=1 年
- 岗位类型:Python/数据/AI/Agent/后端/开发/测试/运维 → 跳过纯运营/HR/财务/销售/客服
- 标题"校招/26届/2026 校招"无"实习"二字 → 跳过(校招正式岗)
- 智联/前程 搜"Python"会出现大量全职 → 必须搜"Python实习生 广州"

## 轮换规则

**每投5个岗位换一个网站**。循环顺序:
BOSS直聘 → 智联招聘 → 前程无忧 → 猎聘 → BOSS直聘(循环)

> ⚠️ 注意：前程无忧在猎聘之前，不是猎聘在前程之后。用户的实际轮换顺序是 BOSS→智联→前程→猎聘。

切换时在Chrome标签栏点目标网站标签。各平台标签页标签特征见"识别当前平台"章节。

投递计数更新到 `~/.hermes/job_hunter_history.json`，每次轮换前检查。

## General Workflow (All Platforms)

```
1. 制作用户画像 → 问模式 → 开始
2. 搜索 → 确认搜索词正确 → 检查结果是否为实习岗位
3. 点击投递按钮 → 处理成功弹窗 → 按正确方式返回搜索页
4. 重复或翻页
5. 每5个换一个网站（轮换）
```

**搜索检查是必要步骤**: 导航到平台后，先看搜索框里是什么词。
如果还在显示上次的搜索词，需要重新搜索。设了搜索框值后，必须**点击"搜索"按钮**才能触发搜索。
搜索后确认页面标题或搜索结果含"实习生"字样。

## Per-Platform Workflows

### BOSS直聘 (Zhipin.com) ✅ 已验证

```
流程: 搜"Python实习生" → 点击岗位 → 点"立即沟通" → 弹窗→点"留在此页" → 左边列表点下一个
```

**详细流程**:
1. 顶部搜索框输入"Python实习生"，点搜索按钮
2. 左侧列表显示岗位，每条含：岗位名、薪资、公司、城市
3. **快速模式**：看卡片关键字——有"实习"、薪资合理、城市匹配就投
4. 点击岗位 → 右侧显示详情和"立即沟通"按钮
5. 点"立即沟通" → 弹窗出现：
   - **"继续沟通"** → 发送默认消息进入聊天页
   - **"留在此页"** → 快速跳过留在搜索页（推荐）
6. 下一个岗位在左侧列表直接点，无需返回

关键:
- ✅ computer_use UIA 模式下推荐点"留在此页"快速跳过
- ⚠️ **CDP/cua-driver MCP 模式下"留在此页"会导航到聊天页**（偏离搜索流程）。CDP 下应改用 **Escape 键**关闭弹窗，留在当前页面
- ❌ **禁止**在BOSS使用 Ctrl+W
- 注意"在校"标签——只写"应届生"没"在校"的跳过
- 每天限投120个
- BOSS没有单独的"投递成功"页

**CDP 投递 BOSS 的推荐流程**:
1. 从搜索页获取所有岗位链接: `document.querySelectorAll(".job-card-wrap a")` → 提取 `href`
2. `window.location.href = jobUrl` 直接导航到岗位详情页（**不要用 card.click()，CDP 下不可靠**）
3. 等待页面加载 → 点击 `.btn-startchat`（不是 `.op-btn-chat`，后者在搜索页详情面板）
4. 弹窗出现"已向BOSS发送消息" → **按 Escape 关闭**（不要点"留在此页"）
5. 导航回搜索页或下一个岗位 URL

### 智联招聘 (Zhaopin.com) ✅ 已验证

```
流程: 搜"Python实习生" → 点"立即投递" → 弹窗→点叉叉(X)关闭 → 点左边的标签页回到搜索页
```

**详细流程**:
1. 先看右上角有无"登录/注册"（有则未登录）
2. 搜索框输入"Python实习生"，点搜索
3. 直接点岗位上的"立即投递"按钮
4. 弹窗出现 → **点击弹窗上的叉叉(X)**关闭
5. **关键**: 返回搜索页要**点顶部左边的标签页**（搜索页的标签），不是点浏览器返回按钮！

**替代方法**: 如果投递打开了新标签页，可以用 **Ctrl+W** 关闭当前标签页快速回到搜索页。

关键:
- ✅ **点叉叉(X)关弹窗**（不是浏览器返回）
- ✅ **点左边的标签页**回到搜索页（不是右边详情页标签）
- ✅ **Ctrl+W可以**用于关闭新标签页（BOSS不能用）
- 返回方式：左边标签页 > Ctrl+W > 浏览器返回
- 未登录特征：右上角有"登录/注册"文字

### 前程无忧 (51Job.com) ✅ 已验证

```
流程: 输搜索词 → 点"搜索"按钮 → 点"投递" → 弹窗"投递成功" → 点X关弹窗 → 重新输入搜索词 → 点搜索
⚠️ 每次投递后搜索框100%会被重置为无关词（如"会计师事务所""税务师事务所""经营分析"）！
⚠️ 点X关弹窗后，搜索框已被重置——必须重新 set_value + 点搜索！
```

**详细流程**:
1. 搜索框输入"Python实习生"，必须点搜索按钮
2. 可直接点"投递"按钮，或点文字进详情页
3. 弹窗"投递成功" → **点叉叉(X)**关闭（弹窗上的 X 按钮，通常在弹窗右上角）
4. **检查搜索框**：关闭弹窗后搜索框已变成无关词 → 重新 `set_value("Python实习生")` + 点搜索
5. 重复以上步骤

**⚠️ 关于"职位搜索"链接**：
- 页面上的"职位搜索"链接**可以**用来返回搜索列表页，但搜索词同样会被重置
- 浏览器返回箭头（←）会回到"投递成功"页面，不是搜索结果页
- **推荐流程**：直接点X关弹窗 → 重新输入搜索词 → 点搜索（最稳定，不依赖页面导航）

关键:
- ✅ 弹窗后**点X关弹窗**
- ✅ **关弹窗后必须重新输入搜索词**（100%会被重置）
- ❌ **浏览器返回箭头** → 回到"投递成功"页面，不是搜索结果
- ❌ **"职位搜索"链接** → 搜索词被重置
- 搜索结果可能混有全职，优先选标"实习"字样的

**CDP 投递 51Job 的验证选择器**:
- 岗位卡片: `.joblist-item`
- 投递按钮: `.btn.apply`（文字"投递"），已投递变为 `.btn.apply.active`（文字"已申请"）
- 获取所有岗位: `document.querySelectorAll(".joblist-item")` → 每个 card 的 `innerText` 含标题/薪资/城市

### 前程无忧特殊处理

### ⚠️ 批量点击会导致页面跳转
**错误做法**：一次性点击所有"投递"按钮
```javascript
// ❌ 错误：批量点击会触发导航到第三方网站
cards.forEach(c => c.querySelector(".btn.apply").click())
```

**正确做法**：逐个点击，每次等待确认
```javascript
// ✅ 正确：逐个点击 + 等待
for(var i=0; i<cards.length; i++) {
    var btn = cards[i].querySelector(".btn.apply");
    if(btn && btn.textContent.trim() === "投递") {
        btn.click();
        // 等待 1.5-2 秒再点下一个
    }
}
```

### ⚠️ 翻页必须用页面上的页码按钮
**错误做法**：手动修改 URL 的 page 参数
```javascript
// ❌ 错误：URL 翻页会丢失登录态或触发异常
window.location.href = "...&page=2"
```

**正确做法**：点击 Element UI 分页组件的页码
```javascript
// ✅ 正确：用 el-pager 翻页
var pager = document.querySelector(".el-pager");
var items = pager.querySelectorAll("li");
items[1].click();  // 点击第2页
// 等待 3 秒页面加载
```

**分页组件结构**：
- 容器：`.el-pagination.is-background`
- 页码列表：`.el-pager` > `li.number`
- 当前页：`li.number.active` 或 `li.is-active`
- 下一页按钮：`.btn-next`（如果有）

### 投递按钮点击后的行为
1. **成功**：按钮文字从"投递"变为"已申请"
2. **未登录**：弹出登录对话框（`.el-dialog`）
3. **跳转外部**：某些岗位会打开 yingjiesheng.com（第三方网站）

### 检查登录状态
```javascript
// 检查右上角是否显示"登录"
var header = document.querySelector("header");
header.innerText.includes("登录") ? "未登录" : "已登录"
```

### 投递成功确认
```javascript
// 检查按钮是否变为"已申请"
var btn = card.querySelector(".btn.apply");
btn.textContent.trim() === "已申请"  // true = 成功
```

## 猎聘 (Liepin.com) ✅ 已验证

```
流程: 搜"Python实习生" → 点岗位进详情 → 点"聊一聊" → 按钮变"继续聊" → 点左边标签页返回
```

**详细流程**:
1. 首次进入可能有弹窗广告→找叉叉关闭
2. 检查右上角登录状态
3. 搜索框输入"Python实习生"，点搜索
4. 点岗位进详情页
5. 看职位介绍是否匹配简历
6. 页面有**两个"聊一聊"入口**（顶部和HR信息旁），都可以点
7. 点后按钮变"继续聊" → 沟通已发起
8. **返回**：点上面标签栏左边的标签页回搜索结果
9. 如果搜不出结果（"非常抱歉！暂时没有合适的职位"），直接换下一个网站

**快速模式**：
- 先看"应届"和"大专"标签——写了"大专"而用户是本科→跳过
- 鼠标移到岗位卡片上才出现"聊一聊"
- 匹配就点"聊一聊"

关键:
- 用"聊一聊"而不是"立即投递"
- 两个"聊一聊"均可
- 猎聘Python实习岗较少 → **搜不到时换关键词**：试"AI实习""Python开发实习""数据分析实习""Java实习"等
- **返回搜索页**：点击顶部猎聘标签页（不是浏览器返回箭头，浏览器返回会停留在详情页）
- 猎聘要求"硕士"的岗位 → 用户是本科，跳过

## 轮换规则

每投5个岗位换一个网站，循环顺序:
BOSS直聘 → 智联招聘 → 前程无忧 → 猎聘 → BOSS直聘(循环)

切换时在Chrome标签栏点击目标网站的标签页。

## Quick Mode (快速模式)

当用户要求"快速"时使用，减少每次分析耗时：

1. **看岗位卡片**：岗位名、薪资、城市、学历、实习标签
2. **快速排除**：非实习跳过 / 薪资异常跳过 / 城市不匹配跳过 / 学历不符跳过
3. **翻页**：在左侧列表区域滚动或点下一页箭头（不要用scroll action→用PageDown键）
4. 可用分类筛选（如"技术"）

## Tab Management (标签页管理)

| 平台 | 返回搜索页方式 | Ctrl+W |
|------|-------------|--------|
| BOSS直聘 | 左边列表点下一个 | **禁止**使用 |
| 智联招聘 | 点左边标签页 或 Ctrl+W | **可以**使用 |
| 前程无忧 | 点X关弹窗 → 重新输入搜索词 → 点搜索 | 一般不用 |
| 猎聘 | 点猎聘标签页 | 一般不用 |

切换网站时在Chrome标签栏直接点目标站标签。

**CDP/cua-driver 模式下切换标签页**:
- UIA `click` 点击标签页坐标不可靠（坐标映射经常偏移）
- **推荐用 `hotkey` 发 Ctrl+N 切换到第 N 个标签**（Ctrl+1=第1个, Ctrl+2=第2个...）
- 切换后用 `document.title` 确认当前在哪个站
- 标签顺序从左到右，编号从1开始

## cua-driver MCP Direct Call (computer_use 工具连接断裂时的主要备选方案)

当 `computer_use` 返回空(0x0, 0 elements)但 cua-driver 守护进程仍在运行时，
**cua-driver MCP 的 `page execute_javascript` 是已验证的有效备选方案**（走 CDP 端口 9222）。
本会话中通过此方法成功投递了 100+ 个岗位。

### 诊断

```bash
# 确认 cua-driver 在跑
tasklist | grep cua

# 确认 MCP 接口能响应
cd "C:/Users/<user>/AppData/Local/Programs/Cua/cua-driver/bin"
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"list_windows","arguments":{}},"id":1}' | ./cua-driver.exe mcp
```

### 可用工具列表

cua-driver MCP 支持的工具（通过 `list-tools` 查看）：

| 工具 | 用途 |
|------|------|
| `list_windows` | 列出所有窗口（pid, window_id, title, bounds） |
| `get_window_state` | 获取窗口的完整 UIA 树（元素 + 截图） |
| `click` | 在窗口内点击坐标（pid + window_id + x + y） |
| `hotkey` | 发送组合键（如 `["ctrl","5"]` 切到第5个标签） |
| `page` | 操控浏览器页面（需 CDP 端口 9222） |
| `get_screen_size` | 获取屏幕尺寸 |

### 典型工作流

```python
import subprocess, json

def cua_mcp(tool_name, arguments):
    """调用 cua-driver MCP 工具"""
    payload = json.dumps({
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments},
        "id": 1
    })
    result = subprocess.run(
        [r"C:\Users\<user>\AppData\Local\Programs\Cua\cua-driver\bin\cua-driver.exe", "mcp"],
        input=payload, capture_output=True, text=True, timeout=15
    )
    for line in result.stdout.strip().split('\n'):
        if line.startswith('{'):
            data = json.loads(line)
            return data.get('result', {}).get('content', [])
    return []

# 1. 找到 Chrome 窗口
windows = cua_mcp("list_windows", {})
# → 找到 pid=33280, window_id=3017106, title="我的智联 - Google Chrome"

# 2. 切换标签页（用 hotkey 比点击更可靠）
# Ctrl+1=第1个标签, Ctrl+2=第2个... Ctrl+9=第9个
cua_mcp("hotkey", {"pid": 33280, "window_id": 3017106, "keys": ["ctrl", "5"]})

# 3. 通过 CDP 执行 JavaScript 操控页面
cua_mcp("page", {
    "pid": 33280, "window_id": 3017106,
    "action": "execute_javascript",
    "javascript": "document.title"
})
```

### 与 CDP Python 脚本的区别

MCP 输出格式详见 `references/cua-driver-mcp-output.md`（双重 JSON 转义、structuredContent 解析等）。

| 方式 | 优点 | 缺点 |
|------|------|------|
| cua-driver MCP | 不需要额外 Python 依赖，通过 terminal 直接调用 | 输出是 MCP JSON 格式，需要解析 |
| CDP Python (websockets) | 更灵活，可写复杂逻辑 | 需要 websockets 依赖，需处理连接管理 |

**推荐顺序**：`computer_use` → cua-driver MCP → CDP Python 脚本

## DOM Selectors (CDP / execute_javascript)

当使用 cua-driver MCP 的 `page execute_javascript` 或 CDP 直接操控页面时，
各平台的 DOM 选择器见 `references/dom-selectors.md`。

## Batch Apply Pattern (CDP/cua-driver MCP)

当 `computer_use` 不可用时，通过 cua-driver MCP 的 `page execute_javascript` 批量投递。

### 前程无忧批量投递
```javascript
// ⛔ 错误：一次性点击所有按钮会触发页面跳转
// ✅ 正确：逐个点击，每次等待确认
// 1. 导航到搜索页（直接用URL最可靠）
window.location.href = "https://we.51job.com/pc/search?keyword=Python%E5%AE%9E%E4%B9%A0%E7%94%9F%E5%B9%BF%E5%B7%9E&searchType=2&sortType=0";

// 2. 逐个点击投递按钮（每次间隔2秒）
var cards = document.querySelectorAll(".joblist-item");
for(var i=0; i<cards.length; i++){
    var b = cards[i].querySelector(".btn.apply");
    if(b && b.textContent.trim() === "投递") {
        b.click();
        // 等待2秒后检查状态
    }
}
```
- **逐个点击 + 2秒间隔**是唯一可靠的方式，批量forEach点击会触发跳转到 yingjiesheng.com
- 点击后检查按钮状态：`btn.textContent.trim() === "已申请"` 表示成功
- 如果页面跳转到第三方站：`window.location.href = "搜索页URL"` 强制返回
- 翻页：`window.location.href = "搜索页URL&page=N"`
- **前程无忧搜索URL模板**: `https://we.51job.com/pc/search?keyword=Python%E5%AE%9E%E4%B9%A0%E7%94%9F%E5%B9%BF%E5%B7%9E&searchType=2&sortType=0`（加 `&page=N` 翻页）
- **前程无忧 CDP下无弹窗**: 点击"投递"后按钮直接变成"已申请"，不弹"投递成功"对话框

### BOSS直聘批量投递
```javascript
// 1. 获取所有岗位链接（从搜索页）
var cards = document.querySelectorAll(".job-card-wrap");
var urls = [];
cards.forEach(function(c){
    var link = c.querySelector("a[href*='job_detail']");
    if(link) urls.push(link.href);
});

// 2. 逐个导航投递（不要用 card.click()，CDP下不可靠）
for(var i=0; i<urls.length; i++){
    window.location.href = urls[i];
    // 等3秒页面加载
    // 点击 .btn-startchat（不是 .op-btn-chat）
    // 弹窗出现后按 Escape 关闭
    // 继续下一个
}
```
- 用 `window.location.href` 导航（**不要用 `card.click()`，CDP 下不可靠**，详情面板可能不更新）
- 详情页按钮选择器：`.btn-startchat`（不是 `.op-btn-chat`，后者在搜索页详情面板）
- 关闭弹窗用 **Escape 键**（**不要点"留在此页"**，CDP下会导航到聊天页）
- Escape 通过 cua-driver MCP 的 `hotkey` action 发送：`{"keys": ["Escape"]}`

### 智联招聘批量投递
```javascript
// 点击所有"立即投递"按钮
var btns = document.querySelectorAll("[class*=apply], button");
var applyBtns = [];
btns.forEach(function(b) {
    if (b.textContent.trim() === "立即投递") applyBtns.push(b);
});
applyBtns.forEach(function(b) { b.click(); });
```
- 部分投递会触发"投递成功"弹窗，用 Escape 关闭
- 部分会直接跳转到成功页面

## computer_use 故障时的替代方案：cua-driver MCP

当 `computer_use` 返回空（0x0, 0 elements）但 Chrome 在运行时，**直接用 cua-driver MCP 接口**操控：

```python
import subprocess, json

def run_cua_mcp(tool_name, arguments):
    payload = json.dumps({
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments},
        "id": 1
    })
    result = subprocess.run(
        [r"C:\Users\K-ON的学习本\AppData\Local\Programs\Cua\cua-driver\bin\cua-driver.exe", "mcp"],
        input=payload, capture_output=True, text=True, timeout=15
    )
    for line in result.stdout.strip().split('\n'):
        if line.startswith('{'):
            data = json.loads(line)
            content = data.get('result', {}).get('content', [])
            for c in content:
                if c.get('type') == 'text':
                    return c['text']
    return None

# 关键工具：
# - get_window_state: 获取 UIA 元素树（需要 pid + window_id）
# - page > execute_javascript: 执行 JS（需要 pid + window_id）
# - hotkey: 按键（keys 是数组，如 ["ctrl","5"]）
# - click: 点击坐标（x,y 是逻辑坐标）
```

**获取 Chrome 窗口信息**：
```python
# list_windows 获取所有窗口
result = run_cua_mcp("list_windows", {})
# 找到 chrome.exe 的 pid 和 window_id
```

**在 Chrome 标签页间切换**：
```python
# 用 hotkey 切换标签：Ctrl+1=第1个, Ctrl+2=第2个, etc.
run_cua_mcp("hotkey", {"pid": 33280, "window_id": 3017106, "keys": ["ctrl", "5"]})
```

## CDP+MCP 方式（推荐）

当 `computer_use` 工具不可用时，使用 cua-driver MCP 接口直接操控 Chrome：

### 获取窗口信息
```python
# 列出所有窗口
payload = json.dumps({"jsonrpc":"2.0","method":"tools/call","params":{"name":"list_windows","arguments":{}},"id":1})
# 找到 chrome.exe 的 pid 和 window_id

# 获取窗口UIA树
payload = json.dumps({"jsonrpc":"2.0","method":"tools/call","params":{"name":"get_window_state","arguments":{"pid":PID,"window_id":WINDOW_ID}},"id":1})
```

### 执行JavaScript
```python
payload = json.dumps({"jsonrpc":"2.0","method":"tools/call","params":{"name":"page","arguments":{"pid":PID,"window_id":WINDOW_ID,"action":"execute_javascript","javascript":"JS_CODE"}},"id":1})
```

### 按键操作
```python
# Escape键
payload = json.dumps({"jsonrpc":"2.0","method":"tools/call","params":{"name":"hotkey","arguments":{"pid":PID,"window_id":WINDOW_ID,"keys":["Escape"]}},"id":1})

# PageDown翻页
keys = ["PageDown"]

# 浏览器后退
keys = ["alt", "Left"]
```

### ⚠️ 防止跳转到外部网站

前程无忧的"投递"按钮有时会跳转到应届生求职网（yingjiesheng.com）。**必须检测并阻止**：

```python
def safe_apply(job_index):
    """安全投递：点击后检查是否跳转，跳转则立即返回"""
    # 1. 记录当前URL
    url_before = run_js('window.location.href')
    
    # 2. 点击投递按钮
    run_js('... btn.click() ...')
    time.sleep(1)
    
    # 3. 检查是否跳转
    url_after = run_js('window.location.href')
    
    # 4. 如果跳转到其他网站，立即关闭并返回
    if "51job" not in str(url_after):
        press_key(["ctrl", "w"])  # 关闭跳转的标签
        press_key(["ctrl", "1"])  # 切回51job标签
        return "跳转已修复"
    
    # 5. 检查按钮是否变成"已申请"
    return "✅成功" if "已申请" in str(result_btn) else "⏭️跳过"
```

### ⚠️ 登录状态检查

点击"投递"前必须确认已登录：
```javascript
document.querySelector("header").innerText.includes("登录") ? "未登录" : "已登录"
```
未登录时点击"投递"会弹出登录弹窗，不会真正投递！

### ⚠️ 逐个点击，不要批量

批量点击会导致页面跳转到第三方网站！必须逐个点击并等待1.5秒：
```python
for i in range(20):
    safe_apply(i)  # 使用安全投递函数
    time.sleep(1.5)
```

### ⚠️ 翻页使用页码按钮

不要修改URL翻页！使用 el-pager 的页码按钮：
```javascript
var pager = document.querySelector(".el-pager");
var items = pager.querySelectorAll("li");
if(items[1]) items[1].click();  // 点击第2页
```
## 标签页即时清理（推荐）

投递过程中会自动打开新标签，**每次投递后立即清理**，标签数始终保持4个。

### 核心逻辑
```python
def apply_with_cleanup(job_index):
    """投递单个岗位，投递后立即清理多余标签"""
    # 1. 记录当前标签数
    tabs_before = get_tab_count()
    
    # 2. 点击投递按钮
    run_js(f'... btn.click() ...')
    time.sleep(1.5)  # 等待新标签可能打开
    
    # 3. 检查并清理（无论点击成功与否）
    cleanup_if_needed(expected_tabs=4)
    
    return success

def cleanup_if_needed(expected_tabs=4):
    """如果标签数超过预期，从最右边开始关闭"""
    current = get_tab_count()
    if current > expected_tabs:
        for _ in range(current - expected_tabs):
            press_key(["ctrl", "9"])  # 切到最后
            press_key(["ctrl", "w"])  # 关闭
        press_key(["ctrl", "1"])  # 切回第1个标签
```

### 优势
- **标签数始终稳定**：不会堆积
- **无额外开销**：每次投递只多检查一次
- **无需手动清理**：全自动

### 完整投递脚本
见 `scripts/apply_51job.py`（含即时清理）

## CDP Fallback (computer_use 崩溃时)

当 `computer_use` 返回空(0x0, 0 elements)但 cua-driver CLI 正常工作时，是 Hermes 与 cua-driver 守护进程的连接断了。**不要反复 kill/restart cua-driver**——守护进程以 SYSTEM 权限运行，杀不掉，且重启不会修复 Hermes 工具连接。唯一修复：**重启整个 Hermes 会话**。

**⚠️ 用户偏好：`computer_use` 是首选方案。** 当 `computer_use` 返回空（0x0, 0 elements）时，优先尝试 cua-driver MCP 的 `page execute_javascript`（走 CDP），这是已验证的有效备选方案。只有 cua-driver MCP 也完全不可用时，才建议重启 Hermes 会话。

### 替代方案：CDP (Chrome DevTools Protocol)

Chrome 的 `--remote-debugging-port=9222` 端口可直接用 WebSocket 执行 JavaScript 操控 DOM，比 UIA 更稳定。

### Chrome 窗口恢复（负 UIA 坐标修复）

如果 `computer_use capture` 返回的元素坐标全是负数(~-32000)，是 Chrome 窗口在多显示器/缩放场景下 UIA 空间丢失。点 Chrome 窗口的**恢复按钮**（通常是 element index 1）即可恢复正常坐标。

## User Preferences (此用户的偏好)

- **投递模式**: 用户总是选择 **快速模式** 🏃。不要问选深度还是快速。
- **投递上限**: 用户要求 **投到每日上限为止**（BOSS 120 / 前程无忧 100 / 智联和猎聘投到没有新岗位为止）。不要问"要不要继续"，直接继续直到达到上限或没有新岗位。
- **轮换顺序**: BOSS→智联→前程→猎聘→循环。不要跳过前程无忧直接去猎聘。
- **会话过长重启**: 用户接受了这个模式来保持效率。保存进度后，重启后说"继续投简历"即可恢复。

## Pitfalls
CDP 可执行任何 JS（选元素、点击、读文本），完全不受 UIA 限制。详细见 skill `computer-use-job-hunt` 的 `references/cdp-spa-apply.md`。

### Chrome 窗口恢复（负 UIA 坐标修复）

如果 `computer_use capture` 返回的元素坐标全是负数(~-32000)，是 Chrome 窗口在多显示器/缩放场景下 UIA 空间丢失。点 Chrome 窗口的**恢复按钮**（通常是 element index 1, role="Button" label="恢复"）即可恢复正常坐标。

1. **搜索没生效**: 设了搜索框值后必须点"搜索"按钮，否则页面仍显示旧结果
2. **搜索词检查**: 每次进平台先看搜索框里是什么词。如果有上次残留的词，要先改过来
3. **实习生 vs 全职**: 搜"Python"可能搜到大量全职，必须搜"Python实习生"
4. **标签页迷路**: 多个平台开在多个标签页时，从SOM确认当前标签页标题再操作
5. **前程无忧弹窗**: ❌ 不要点"职位搜索"链接（会重置搜索词） → ✅ 点X关弹窗 → ✅ 关弹窗后重新输入搜索词 + 点搜索（浏览器返回箭头会回到"投递成功"页面）
6. **智联招聘**: ✅ 弹窗关X → ✅ 点左边标签页返回 → 浏览器返回不可用
7. **BOSS直聘**: ❌ 不要用Ctrl+W → ✅ 点"留在此页"跳过弹窗 → ❌ 不要点"继续沟通"(会跳到 chat page,虽然消息已发但偏离 docx 流程)
8. **翻页**: ❌ scroll action(Chrome背景模式无效) → ✅ PageDown键
9. **5个换一站**: 每投5个岗位换一个网站，不要在一个网站投太多。顺序：BOSS→智联→前程→猎聘→循环
10. **搜索确认**: 投之前先看搜索框里的词。必须点"搜索"按钮才能触发搜索
11. **标签页确认**: 切换平台后先看当前Document的标题确认在哪个站
12. **结果检查**: 如果搜"Python实习生"但结果全是月薪上万——说明搜错了，重新搜
13. **猎聘没结果**: 直接换下一个网站，不用纠结
14. **参考教程**: 用户教程在 `E:\\npe_get_jobs_usb\\docx\\`，操作前应先阅读对应平台docx（路径已更正，旧路径 `E:\\npe_get_jobs_backup\\docx\\` 已不存在）\n\n15. **BOSS搜索中断导致显示错误岗位**: 切换到其他标签页（前程/智联）再切回BOSS页面后，搜索框可能保留了上次的搜索词但**搜索结果已退化为首页推荐**（显示"运营/视频号"等无关岗位）。点击搜索按钮不一定恢复——需要重新 `set_value("Python实习生")` + 点击搜索按钮。确认左侧列表岗位名含"实习"、"Python"等关键字再开始投。

16. **51job 求职意向要先改**: 默认求职意向是上次留的（可能是错的，如"广州·财务经理"），跟当前要投方向不符。改法：进"我的51job"→简历→求职意向→改关键词。或直接搜索 `https://we.51job.com/jobs?keyword=...&workcity=0201`（0201=广州）绕过求职意向。改完再投，否则推荐岗位全是无关的。

17. **51job 搜索框每次投递后会被重置**: 前程无忧点击"投递"按钮后，搜索框**100%会**自动变成无关词（如"会计师事务所"、"税务师事务所"、"经营分析"）。**每次投递后必须重新检查搜索框内容**，如果不是"Python实习生"，需要重新 `set_value("Python实习生")` + 点击搜索按钮。不要假设搜索词会保留。关闭弹窗后搜索框已被重置——不需要额外操作来"触发"重置，它在投递时就已经重置了。

18. **51job 返回方式**: 前程无忧投递成功后，点X关闭弹窗。**不要点浏览器返回箭头**（会回到"投递成功"页面）。**不要点"职位搜索"链接**（搜索词被重置）。**推荐方式**：关弹窗 → 重新输入搜索词 → 点搜索按钮（最稳定）。

16. **cua-driver `page` action 强依赖 CDP 端口 9222**: `execute_javascript` 和 `query_dom` 都走 CDP。没 CDP 端口会报 `Cannot connect to CDP on port 9222: 由于目标计算机积极拒绝 (os error 10061)`。**但 `get_text` 走 UIA 不依赖 CDP**——能 extract 页面纯文本，可作为 CDP 不可用时的 fallback 提取层（只能读不能写）。

17. **Chrome 149+ `--remote-debugging-port` 需要非默认 `--user-data-dir`**: 用默认 `%LOCALAPPDATA%\\Google\\Chrome\\User Data` 启动 Chrome，CDP 端口不会监听（stderr 有明文 `DevTools remote debugging requires a non-default data directory`）。修复：把默认 profile 复制到临时目录，启动时指定 `--user-data-dir=<临时>`。复制 profile 后登录态（cookies 在加密的 SQLite，需 Chrome 自己解密）可能丢失——localStorage 会带过去。要保登录态就复制整个 User Data 后用 `chrome-cdp-profile` 之类名字启动。

18. **BOSS 已投岗位不可重复投**: BOSS 列表中已投过的岗位（同一team同一JD）再次点击会显示"继续沟通"而不是"立即沟通"。如果看到的是"继续沟通"，说明已经投过，在右侧详情确认公司/岗位名后跳过，点下一个。

19. **前程无忧登录态持久**: 之前认为每次重启需重新登录，但实际 session cookies 在 Chrome 保持打开时可持续多天。切换标签页回来检查右上角是否有用户名即可确认。不要默认"需要登录"。

20. **前程无忧批量点击导致跳转**: ❌ 绝对不要用 `forEach` 批量点击所有"投递"按钮！会导致页面跳转到第三方网站（yingjiesheng.com）。✅ 必须逐个点击，每次等待2秒。

21. **前程无忧翻页方式**: ❌ 不要修改URL参数翻页（`&page=2`），会丢失状态。✅ 使用 `el-pager` 的页码按钮点击翻页。

22. **前程无忧未登录投递**: 点击"投递"前检查右上角是否显示"登录"。未登录时点击会弹出登录弹窗，不会真正投递。用户说"登录了"但页面显示"登录"→需要用户手动登录。

23. **cua-driver MCP 调用方式**: 通过 `execute_code` 调用 cua-driver.exe 的 MCP 协议，可执行 JavaScript、按键、获取窗口状态。路径：`C:\Users\K-ON的学习本\AppData\Local\Programs\Cua\cua-driver\bin\cua-driver.exe`

20. **前程无忧翻页必须用页面页码按钮**: ❌ 不要用 URL 参数 `&page=2` 翻页（会丢失登录态或触发异常）。✅ 点击 `.el-pager li.number` 页码按钮翻页，等待 3 秒加载。

21. **前程无忧批量点击会跳转外部网站**: ❌ 不要一次性点击所有"投递"按钮（会导航到 yingjiesheng.com）。✅ 逐个点击 + 间隔 1.5-2 秒等待。

22. **computer_use 失效时用 cua-driver MCP**: 当 `computer_use` 返回空（0x0）但 Chrome 在运行，直接用 cua-driver 的 MCP 接口（`execute_javascript`、`hotkey`、`click`）操控。需要 pid 和 window_id（从 `list_windows` 获取）。

23. **cua-driver hotkey 的 keys 是数组**: ❌ `{"keys": "ctrl+5"}` 会报错。✅ `{"keys": ["ctrl", "5"]}`。

24. **UIA 坐标可能映射异常**: cua-driver 的 click 坐标在多显示器/缩放场景下可能出现负值（-28742）。此时改用 `execute_javascript` 点击更可靠。

25. **前程无忧"投递"按钮行为（CDP vs UIA 差异）**:
    - **CDP `btn.click()` 逐个投递有效**: 通过 `document.querySelectorAll(".joblist-item")` 遍历卡片，对每个 `.btn.apply` 执行 `click()`，按钮会从"投递"变为"已申请"。**不需要逐个导航到详情页**。
    - **⛔ 批量点击（循环内无延迟）会触发页面跳转到 `q.yingjiesheng.com` 等第三方站**。**安全做法**: 必须逐个点击，每次点击后等待 2-3 秒，检查按钮状态和页面 URL。
    - **CDP下无弹窗**: 与UIA模式不同，CDP点击"投递"后**不会弹出"投递成功"弹窗**，按钮直接变成"已申请"。

26. **BOSS CDP: "留在此页"点击会导航到聊天页**: 通过 CDP 点击"留在此页"按钮时，浏览器会导航到 `/web/geek/chat` 页面。**CDP 下关闭 BOSS 弹窗用 Escape 键**。

27. **BOSS CDP: 岗位卡片 click() 不可靠**: CDP 下 `.jobcard-wrap.click()` 可能不更新详情面板。**CDP 下投递 BOSS 的可靠方式是直接导航到岗位 URL**。

28. **BOSS CDP: 详情页"立即沟通"选择器不同**: 搜索页详情面板用 `.op-btn-chat`，独立岗位详情页用 `.btn-startchat`。

29. **CDP 解析 MCP 输出的双重转义**: cua-driver MCP 的 `page execute_javascript` 返回值经过两层 JSON 转义。解析时需要 `json.loads(text.split('user_gesture: ')[1])` 得到字符串，再 `json.loads()` 得到实际数据。

30. **标签页爆炸问题**: 每次导航到新URL或点击链接可能打开新标签页，导致标签页数量激增（曾从4个涨到42个）。**定期检查标签页数量**，每个平台只保留1个标签页。清理方法：`Ctrl+9` 切到最后一个标签 → `Ctrl+W` 关闭 → 重复直到只剩4个。然后用 `Ctrl+1/2/3/4` 切到各平台标签，用 `Ctrl+T` 重新打开需要的页面。

31. **前程无忧CDP投递成功确认**: CDP模式下点击"投递"后**不会弹出"投递成功"弹窗**，按钮直接从"投递"变为"已申请"。如果点击后按钮仍显示"投递"，说明投递失败（可能是未登录或网络问题）。


## Verification

- Run a test: navigate to a site, search, click one "投递", verify success popup, close it
- Check `~/.hermes/job_hunter_history.json` for record after each submission
