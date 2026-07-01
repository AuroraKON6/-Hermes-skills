# cua-driver MCP Output Format

## Response Structure

cua-driver MCP responses are JSON-RPC 2.0. The actual data is in `result.content[0].text`.

### For `page execute_javascript`:
```
cdp.runtime.evaluate.user_gesture: "<actual JSON string>"
```

**Parsing**: Double JSON decode required:
```python
import json
# 1. Parse MCP response
mcp_data = json.loads(mcp_stdout)
text = mcp_data['result']['content'][0]['text']
# 2. Extract the JS return value (it's a JSON string wrapped in quotes)
inner = json.loads(text.split('user_gesture: ')[1])
# 3. Parse the actual data
data = json.loads(inner)  # if inner is a JSON string
```

### For `get_window_state`:
Returns both `content` (markdown tree + screenshot) AND `structuredContent` (machine-readable).

Key fields in `structuredContent`:
- `elements[]` — array of UIA elements with:
  - `element_index` — 1-based index for clicking
  - `element_token` — unique token like `s00c7:45`
  - `role` — UIA role (Button, Text, Hyperlink, TabItem, etc.)
  - `label` — visible text
  - `frame` — `{x, y, w, h}` bounds in logical pixels
  - `actions` — available actions like `[invoke]`, `[select]`, `[set_value,text]`
- `screenshot_width`, `screenshot_height` — screenshot dimensions

### For `list_windows`:
Returns `structuredContent.windows[]` with:
- `pid`, `window_id`, `title`
- `bounds` — `{x, y, width, height}`
- `is_on_screen`, `z_index`

## Common Gotchas

1. **Double escaping**: MCP returns JSON inside JSON. Always `json.loads()` twice.
2. **Tab indices change**: Element indices from `get_window_state` change when tabs switch or page scrolls. Re-capture after any navigation.
3. **UIA coordinate mapping**: `click` action reports different coordinates than requested due to display scaling. The actual click lands correctly despite the log showing different numbers.
4. **`page` action requires CDP port 9222**: If Chrome wasn't started with `--remote-debugging-port=9222`, the `page` action fails with "Cannot connect to CDP".
5. **Tab switching**: UIA `click` on tab elements is unreliable (coordinates often wrong). Use `hotkey` with `keys: ["ctrl", "N"]` where N is the tab position (1-indexed from left). Verify with `document.title` after switching.
6. **前程无忧 batch click → external site navigation**: Clicking multiple `.btn.apply` buttons in a forEach loop without delays triggers navigation to `q.yingjiesheng.com`. Must click one-by-one with 2-second delays.
7. **前程无忧 CDP no popup**: Unlike UIA mode (which shows "投递成功" dialog), CDP mode silently changes button text from "投递" to "已申请". No dialog to close.
8. **BOSS CDP "留在此页" navigates to chat**: Clicking "留在此页" via CDP navigates to `/web/geek/chat`. Use Escape key instead.

## Recommended execute_javascript Helper Pattern

```python
import subprocess, json

def run_js(js_code, pid, window_id):
    """Execute JS on Chrome via cua-driver MCP and return parsed result."""
    payload = json.dumps({
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "page",
            "arguments": {
                "pid": pid,
                "window_id": window_id,
                "action": "execute_javascript",
                "javascript": js_code
            }
        },
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
                    text = c['text']
                    if 'user_gesture:' in text:
                        after = text.split('user_gesture: ')[1]
                        try:
                            inner = json.loads(after)
                            return inner
                        except:
                            return after
    return None
```
