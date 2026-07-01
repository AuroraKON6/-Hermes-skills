# Platform DOM Selectors (for CDP / execute_javascript)

When using `cua-driver page execute_javascript` or CDP directly,
use these selectors to interact with job listings.

## 前程无忧 (51Job)

```javascript
// Job cards
document.querySelectorAll(".joblist-item")

// Apply button inside a card
card.querySelector(".btn.apply")

// Button text states
// "投递" = can apply (class: "btn apply")
// "已申请" = already applied (class: "btn apply active")

// 获取所有岗位信息
var cards = document.querySelectorAll(".joblist-item");
var r = [];
for (var i = 0; i < cards.length; i++) {
    var c = cards[i];
    var lines = c.innerText.split("\n").filter(x => x.trim());
    var t = lines.slice(0, 3).join(" | ");
    var btn = c.querySelector(".btn.apply");
    r.push({i: i, t: t.slice(0, 80), b: btn ? btn.textContent.trim() : ""});
}
JSON.stringify(r);

// 批量投递：找到第一个可投的岗位并点击
var cards = document.querySelectorAll(".joblist-item");
for (var i = 0; i < cards.length; i++) {
    var btn = cards[i].querySelector(".btn.apply");
    if (btn && btn.textContent.trim() === "投递") {
        btn.click();
        break;  // 一次只投一个，投完后搜索框会被重置
    }
}
```

**⚠️ CDP 模式下的关键差异**:
- 点击"投递"按钮后，页面**不会弹出对话框**，而是**直接导航到成功页面**（URL 变为 `job-applied?number=...`）
- 页面标题变为"投递成功 - 智联招聘"或类似
- **不要尝试查找关闭弹窗的按钮**（不存在）
- **投递后必须重新导航回搜索页**：`window.location.href = "https://we.51job.com/pc/search?keyword=Python实习生广州&searchType=2&sortType=0"`
- 检查投递是否成功：`document.title.includes("投递成功")` 或检查按钮状态 `btn.textContent.trim() === "已申请"`
- **批量投递循环**：导航到搜索页 → 点击投递 → 等待自动导航到成功页 → 重新导航回搜索页 → 点击下一个

## 猎聘 (Liepin)

```javascript
// Job cards (multiple selector patterns)
document.querySelectorAll("[class*=job-card]")
document.querySelectorAll("[class*=job-card-box]")
document.querySelectorAll(".job-list-item")

// Click card to navigate to detail page
var card = cards[index];
var link = card.querySelector("a");
if (link) link.click();

// "聊一聊" button on detail page
var all = document.querySelectorAll("a, button, span, div");
var chatBtn = Array.from(all).find(el => el.textContent.trim() === "聊一聊");
if (chatBtn) chatBtn.click();
```

## BOSS直聘 (Zhipin)

**⚠️ CDP 模式下不要用 card.click() 点击岗位卡片——不可靠，详情面板可能不更新。**
**推荐: 直接导航到岗位 URL。**

```javascript
// 获取搜索页所有岗位链接（可靠方式）
var cards = document.querySelectorAll(".job-card-wrap");
var urls = [];
for (var i = 0; i < cards.length; i++) {
    var link = cards[i].querySelector("a[href*='job_detail']");
    var name = cards[i].innerText.split("\n")[0];
    if (link) urls.push({i: i, name: name.slice(0, 40), href: link.href});
}
JSON.stringify(urls);

// 导航到岗位详情页
window.location.href = "https://www.zhipin.com/job_detail/xxxxx.html";

// 岗位详情页的"立即沟通"按钮（注意：搜索页详情面板用 .op-btn-chat，详情页用 .btn-startchat）
var chatBtn = document.querySelector(".btn-startchat");
if (chatBtn) chatBtn.click();

// 弹窗出现后，CDP 下用 Escape 关闭（不要点"留在此页"——CDP 点击会导航到聊天页）
// keyboard: Escape

// 如果必须在搜索页操作（不推荐），详情面板的按钮：
var chatBtn = document.querySelector(".op-btn-chat");
```

## 智联招聘 (Zhaopin)

```javascript
// Job cards on search results
document.querySelectorAll(".joblist-box__item, .joblist-item")

// "立即投递" button
var applyBtn = card.querySelector("[class*=apply], button");
// or find by text:
var btns = document.querySelectorAll("button");
var applyBtn = Array.from(btns).find(el => el.textContent.includes("立即投递"));
if (applyBtn) applyBtn.click();
```

**⚠️ CDP 模式下的关键差异**:
- 点击"立即投递"后，页面**可能直接导航到成功页面**（与 UIA 模式下弹窗不同）
- 成功页面标题为"投递成功 - 智联招聘"，URL 包含 `job-applied?number=...`
- **不要尝试查找关闭弹窗的按钮**（如果页面已导航，弹窗不存在）
- **投递后必须重新导航回搜索页**：`window.location.href = "https://sou.zhaopin.com/?jl=763&kw=Python实习生&srccode=401801"`
- 检查投递是否成功：`document.title.includes("投递成功")`
- **批量投递循环**：导航到搜索页 → 点击投递 → 等待自动导航 → 重新导航回搜索页 → 点击下一个
- **注意**：有时投递不会导航（按钮直接变为"已申请"），此时无需重新导航

## Batch Status Check Pattern

```javascript
// Check which jobs have been applied to
var cards = document.querySelectorAll(".joblist-item");  // adjust selector per platform
var results = [];
for (var i = 0; i < cards.length; i++) {
    var card = cards[i];
    var title = card.innerText.split("\n").filter(x => x.trim())[0];
    var btn = card.querySelector(".btn.apply");
    var status = btn ? btn.textContent.trim() : "no button";
    results.push({i: i, title: title ? title.slice(0, 60) : "?", status: status});
}
JSON.stringify(results);
```

## BOSS直聘批量投递工作流 (CDP推荐)

在 CDP 模式下投递 BOSS 直聘的最高效方式是**直接导航到每个岗位的 URL**：

```python
# 1. 从搜索页提取所有岗位链接
result = run_js("""
var cards = document.querySelectorAll(".job-card-wrap");
var r = [];
for(var i=0;i<cards.length;i++){
    var c = cards[i];
    var link = c.querySelector("a");
    var href = link ? link.href : "";
    var text = c.innerText.split("\\n")[0];
    r.push({i:i, name:text.slice(0,40), href:href});
}
JSON.stringify(r)
""")
jobs = json.loads(result)

# 2. 逐个导航到岗位详情页并投递
for j in jobs:
    if not j['href']:
        continue
    # 导航到岗位详情
    run_js(f'window.location.href = "{j["href"]}"; "ok"')
    time.sleep(3)
    # 点击"立即沟通"
    run_js('var btn = document.querySelector(".btn-startchat"); if(btn) btn.click(); "ok"')
    time.sleep(2)
    # 按 Escape 关闭弹窗（不要点"留在此页"）
    press_escape()
    time.sleep(1)
```

**关键点**：
- 不要用 `card.click()`（CDP 下不可靠，详情面板可能不更新）
- 直接用 `window.location.href = jobUrl` 导航
- 详情页用 `.btn-startchat`，搜索页详情面板用 `.op-btn-chat`
- Escape 关闭弹窗，不要点"留在此页"（CDP 下会导航到聊天页）

## cua-driver MCP 输出解析 (Python)

```python
import subprocess, json

def run_js(js_code, pid=33280, window_id=3017106):
    """通过 cua-driver MCP 执行 JavaScript 并解析返回值"""
    payload = json.dumps({
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "page",
            "arguments": {
                "pid": pid, "window_id": window_id,
                "action": "execute_javascript",
                "javascript": js_code
            }
        },
        "id": 1
    })
    result = subprocess.run(
        [r"C:\Users\<user>\AppData\Local\Programs\Cua\cua-driver\bin\cua-driver.exe", "mcp"],
        input=payload, capture_output=True, text=True, timeout=15
    )
    for line in result.stdout.strip().split('\n'):
        if line.startswith('{'):
            data = json.loads(line)
            content = data.get('result', {}).get('content', [])
            for c in content:
                if c.get('type') == 'text':
                    text = c['text']
                    if 'user_gesture:' in text:
                        # 双重转义: MCP JSON → 字符串内的 JSON
                        after = text.split('user_gesture: ')[1]
                        inner = json.loads(after)  # 第一层: 得到 JSON 字符串
                        return json.loads(inner)   # 第二层: 得到实际数据
    return None
```
