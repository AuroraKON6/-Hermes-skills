"""
前程无忧自动投递脚本（含标签页即时清理）
每次投递后立即检查并关闭多余标签，标签数始终保持4个
"""
import subprocess, json, time

# Chrome 配置
CHROME_PID = 33280
WINDOW_ID = 3017106
CUA_DRIVER = r"C:\Users\K-ON的学习本\AppData\Local\Programs\Cua\cua-driver\bin\cua-driver.exe"
EXPECTED_TABS = 4  # 期望保持的标签数（BOSS+前程+智联+猎聘）

def run_js(js_code):
    """通过 cua-driver MCP 执行 JavaScript"""
    payload = json.dumps({
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "page",
            "arguments": {
                "pid": CHROME_PID,
                "window_id": WINDOW_ID,
                "action": "execute_javascript",
                "javascript": js_code
            }
        },
        "id": 1
    })
    result = subprocess.run(
        [CUA_DRIVER, "mcp"],
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
                            return json.loads(after)
                        except:
                            return after
    return None

def press_key(keys):
    """按键操作"""
    payload = json.dumps({
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "hotkey",
            "arguments": {
                "pid": CHROME_PID,
                "window_id": WINDOW_ID,
                "keys": keys
            }
        },
        "id": 1
    })
    subprocess.run(
        [CUA_DRIVER, "mcp"],
        input=payload, capture_output=True, text=True, timeout=15
    )

def get_tab_count():
    """获取当前标签页数量"""
    payload = json.dumps({
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "get_window_state",
            "arguments": {"pid": CHROME_PID, "window_id": WINDOW_ID}
        },
        "id": 1
    })
    result = subprocess.run(
        [CUA_DRIVER, "mcp"],
        input=payload, capture_output=True, text=True, timeout=15
    )
    
    for line in result.stdout.strip().split('\n'):
        if line.startswith('{'):
            data = json.loads(line)
            content = data.get('result', {}).get('content', [])
            for c in content:
                if c.get('type') == 'text':
                    return c['text'].count('TabItem')
    return 0

def cleanup_if_needed():
    """如果标签数超过预期，从最右边开始关闭多余标签"""
    current = get_tab_count()
    if current > EXPECTED_TABS:
        for _ in range(current - EXPECTED_TABS):
            press_key(["ctrl", "9"])  # 切到最后一个标签
            time.sleep(0.2)
            press_key(["ctrl", "w"])  # 关闭它
            time.sleep(0.2)
        press_key(["ctrl", "1"])  # 切回第1个标签
        time.sleep(0.3)
        return current - EXPECTED_TABS
    return 0

def apply_with_cleanup(job_index):
    """投递单个岗位，投递后立即清理多余标签"""
    # 点击投递按钮
    result = run_js(f"""
    var cards = document.querySelectorAll(".joblist-item");
    var card = cards[{job_index}];
    if(card) {{
        var btn = card.querySelector(".btn.apply");
        if(btn && btn.textContent.trim() === "投递") {{
            btn.click();
            "clicked";
        }} else {{
            "skip";
        }}
    }} else {{
        "no card";
    }}
    """)
    
    # 等待新标签可能打开
    time.sleep(1.5)
    
    # 立即清理多余标签
    closed = cleanup_if_needed()
    
    return "clicked" in str(result), closed

def go_to_page(page_num):
    """翻页到指定页码"""
    run_js(f"""
    var pager = document.querySelector(".el-pager");
    var items = pager.querySelectorAll("li");
    if(items[{page_num - 1}]) items[{page_num - 1}].click();
    "clicked page {page_num}"
    """)
    time.sleep(3)

def check_login():
    """检查前程无忧登录状态"""
    result = run_js('document.querySelector("header").innerText.includes("登录") ? "未登录" : "已登录"')
    return "已登录" in str(result)

# 主程序
if __name__ == "__main__":
    print("=== 前程无忧自动投递（含即时清理）===\n")
    
    # 1. 导航到搜索页
    run_js('window.location.href = "https://we.51job.com/pc/search?keyword=Python%E5%AE%9E%E4%B9%A0%E7%94%9F%E5%B9%BF%E5%B7%9E&searchType=2&sortType=0"; "ok"')
    time.sleep(4)
    
    # 2. 检查登录状态
    if not check_login():
        print("⚠️ 请先登录前程无忧！")
        exit(1)
    print("✅ 已登录\n")
    
    # 3. 投递5页
    total_applied = 0
    for page in range(1, 6):
        print(f"=== 第{page}页 ===")
        if page > 1:
            go_to_page(page)
        
        page_applied = 0
        for i in range(20):
            success, closed = apply_with_cleanup(i)
            if success:
                page_applied += 1
                total_applied += 1
            
            clean_info = f" [清理{closed}个标签]" if closed > 0 else ""
            status = "✅" if success else "⏭️"
            print(f"  [{i:2d}] {status}{clean_info}")
            
            time.sleep(1.5)
        
        print(f"  本页投递: {page_applied} 个\n")
    
    # 4. 最终统计
    final_tabs = get_tab_count()
    print(f"=== 完成 ===")
    print(f"总投递: {total_applied} 个")
    print(f"最终标签数: {final_tabs} (应为{EXPECTED_TABS})")
