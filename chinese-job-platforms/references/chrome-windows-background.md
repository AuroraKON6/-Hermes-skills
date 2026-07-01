# Chrome Background Mode Reference (Windows)

Driving Chrome via `computer_use` on Windows in background mode has specific
quirks that differ from macOS or foreground-mode operation.

## Scrolling

**DO NOT use `scroll` action on Chrome.** On Windows, the `Chrome_WidgetWin_1`
window class silently drops `PostMessage WM_VSCROLL/HSCROLL` events from
background mode. The tool returns ok:true but nothing moves on screen.

**Use `key` with `keys="pagedown"` or `keys="pageup"` instead.** One tap
advances roughly one viewport height. Multiple taps can accumulate; scroll
amount is visual, not tick-based.

The `focus_app` + foreground-scroll workaround (bringing Chrome to front)
requires `raise_window=true` which the user has not authorized.

## Search Verification (Critical)

**Before clicking ANY "投递" button, verify what you searched for.**

1. Check the search box element's label/value in the AX tree
2. Check the page Document title — after a correct search, the tab/browser title changes
3. Check whether results show intern-level salaries (100-280元/天) or full-time salaries (8千-2万+)

A common mistake: the search box still shows a previous search term (e.g. "实施工程师")
even though you typed a new one. `set_value` fills the field but does NOT trigger a search.
You must also click the "搜索" / "Search" button.

**When results are wrong:**
- Search box shows old term → re-set value + click search button
- Results show full-time salaries → search term is wrong (e.g. "Python" not "Python实习生")
- Page shows platform homepage → accidentally clicked browser back button

## 前程无忧 Specific: Popup Workflow

The correct sequence after clicking "投递" on 51Job:

```
投递成功弹窗出现 → 找到X按钮(约1839,415) → 点击X → 继续投下一个
```

❌ WRONG: 点击浏览器返回按钮 — 这会回到首页，丢失搜索结果
❌ WRONG: 使用Ctrl+W — 前程无忧用的是页面内弹窗，不是新标签页
✅ CORRECT: 点击弹窗右上角的X按钮

## Tab Navigation

Clicking TabItem elements by index works reliably. When switching between
platforms:
1. Capture with `app="chrome.exe"` to get all tab elements
2. Find the TabItem whose label matches the target site
3. Click it

Tab indices shift as tabs open/close. Re-capture before clicking.

## CDP / DevTools Protocol on Chrome 149+ (Windows)

**`--remote-debugging-port` 默认被拒绝**——Chrome 149+ 要求
`--user-data-dir` **不能是默认 User Data 目录**，否则 devtools
不会监听端口，stderr 会写：

```
DevTools remote debugging requires a non-default data directory.
Specify this using --user-data-dir.
```

**绕路：复制默认 profile 到临时目录**

```bash
# PowerShell (避开 bash 转义)
$src = "$env:LOCALAPPDATA\Google\Chrome\User Data"
$dst = "$env:TEMP\chrome-cdp-profile"
if (Test-Path $dst) { Remove-Item $dst -Recurse -Force }
Copy-Item $src $dst -Recurse
```

启动 Chrome：

```python
chrome_dir = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
subprocess.Popen([
    chrome_dir,
    "--remote-debugging-port=9222",
    f"--user-data-dir={dst}",       # 必须非默认
    "--no-first-run",
    "--no-default-browser-check",
    "https://www.51job.com",
])
```

验证 CDP：

```bash
curl -s http://127.0.0.1:9222/json/version
# 期望: {"Browser": "Chrome/...", "Protocol-Version": "1.3", ...}
```

**登录态保留情况**：
- localStorage（搜索历史/页面偏好）：✅ 复制后保留
- Cookies（登录 token）：⚠️ 在加密的 SQLite，Chrome 会用 DPAPI 解密，
  通常能保留；但如果 Chrome 检测到 profile "from another machine"
  可能清掉一部分。**最稳的登录保留是用正在用的 Chrome 实例**，
  必要时重新登录一次。

**注意 Chrome 启动后不要 `Stop-Process` 误伤**：复制 profile 后启动的
Chrome 实例可能在某些时机被 sandbox / update service 干掉，需看
`netstat -ano | findstr 9222` 验证 LISTEN 仍在。

## cua-driver `page` action 的 CDP 依赖

`cua-driver call page ...` 的子 action：

| Action | CDP 依赖 | 说明 |
|---|---|---|
| `execute_javascript` | **强依赖** | 走 CDP Runtime.evaluate |
| `query_dom` | **强依赖** | 走 CDP DOM.querySelectorAll |
| `click_element` | 部分 | 优先 UIA Invoke，没找到 fallback 到坐标 |
| `get_text` | **不依赖** | 走 UIA 文本提取（fallback 实现） |

**没 CDP 端口时**：`execute_javascript` / `query_dom` 报错
`Cannot connect to CDP on port 9222: 由于目标计算机积极拒绝 (os error 10061)`，
但 `get_text` 仍能工作——能 extract 整页纯文本做只读分析。

## cua-driver MCP Direct Call (当 computer_use 工具断裂时)

`computer_use` 工具返回空但 cua-driver 守护进程仍在运行时，直接通过 terminal 调用 MCP：

```bash
# 列出窗口
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"list_windows","arguments":{}},"id":1}' | cua-driver.exe mcp

# 切换标签页（比点击 TabItem 更可靠）
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"hotkey","arguments":{"pid":PID,"window_id":WID,"keys":["ctrl","5"]}},"id":1}' | cua-driver.exe mcp

# 执行 JavaScript（需 CDP 端口）
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"page","arguments":{"pid":PID,"window_id":WID,"action":"execute_javascript","javascript":"document.title"}},"id":1}' | cua-driver.exe mcp
```

**关键点**：
- `hotkey` 的 `keys` 参数是数组：`["ctrl","5"]` 不是 `"ctrl+5"`
- `get_window_state` 需要同时传 `pid` 和 `window_id`
- 输出是 MCP JSON 格式，需要解析 `result.content[0].text`
- tab 索引会随标签页开关变化，每次操作前重新 `list_windows` 获取最新索引

## Identifying the Current Platform

The current active tab is shown by the `window_title` field in capture
results (can be empty in some cases). The Document element shows the
page content domain. Common labels:
- 前程无忧: "【python,广州招聘，求职】-前程无忧" or "【Python实习生,..."
- 智联招聘: "【python招聘 2026年广州python招聘信息】-智联招聘"
- BOSS直聘: "「广州招聘」-2026年广州人才招聘信息 - BOSS直聘"
- 猎聘: "招聘信息_人才网招聘信息-猎聘"

## Popup/Overlay Handling (前程无忧)

After clicking "投递" on 前程无忧, a modal overlay appears on the same page
with:
- "投递成功" text at roughly (1425, 488)
- X close button at roughly (1839, 415), 30x31px, no AX label

The close button has role `Button` and empty label. To find it in captures:
look for a small Button element at roughly (1839, 415, 30, 31) that only
appears when "投递成功" is also visible.

After clicking X, the overlay disappears and the search results page is
visible underneath — you can immediately click the next "投递" button.

## Tab-Based Success Handling (智联招聘)

After clicking "立即投递" on 智联招聘, a popup with "投递成功" appears
ON THE SAME PAGE — it is NOT a new browser tab.

**Correct workflow**: Click the X (close button) on the popup, then click
the **LEFT browser tab** (the search-results tab) to return to the list.
The left tab is the previous page; the right tab is the success page.

**Ctrl+W** closes the page/tab and should be used AFTER the popup is closed,
to return to the search results from the success/detail page if needed.

**Why NOT click the browser back button**: Clicking back (←) may navigate you
out of the search entirely, back to the platform homepage, losing the search
term and results.

**Why NOT click the tab bar's X**: With many tabs open (BOSS, 猎聘, 前程, etc.),
clicking the wrong tab's X button can close the wrong platform tab.
Use the TabItem elements from the SOM capture to navigate between tabs reliably.

## 智联招聘 Search Navigation

After each successful application on 智联招聘:
1. ✅ Point X (close button) on the "投递成功" popup
2. ✅ Click the LEFT TabItem (search results tab) from the capture elements
3. ❌ Do NOT use browser back (←) — this can exit the search page entirely
4. ❌ Do NOT blindly click TabItems without checking their labels first

To scroll on 智联招聘: use `key` with `keys="pagedown"` — the scroll action
doesn't work on Chrome in background mode.

To go to the next page: look for the "下一页" link/button at the bottom and
click it by element index.

## 智联 vs BOSS vs 前程无忧: Close Method Rules

| Platform | Close Method | Why |
|---|---|---|
| 智联招聘 | ✅ Ctrl+W (关标签页) | 成功页在新标签页打开 |
| BOSS直聘 | ❌ 什么都不用 | BOSS没有成功弹窗/标签页 |
| 前程无忧 | ✅ 点X (关弹窗) | 成功是页面内弹窗，不是新标签页 |
| 前程无忧 | ❌ 不要点浏览器返回 | 会丢失搜索结果，回到首页 |
| 前程无忧 | ❌ 不要用Ctrl+W | 弹窗不是新标签页 |
| 猎聘 | ❓ 待测试 | 猎聘用"聊一聊"机制不同 |
