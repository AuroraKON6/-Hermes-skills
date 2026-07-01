---
name: job-hunt-complete-guide
description: "完整投递简历技能包：含配置、脚本、筛选逻辑、异常处理，可直接复用"
version: 2.0.0
platforms: [windows]
metadata:
  hermes:
    tags: [job-hunt, guide, 51job, BOSS, 智联, 猎聘, reusable]
    category: productivity
---

# 投递简历完整技能包

## 快速开始

### 1. 加载技能
```
加载技能: job-hunt-complete-guide
```

### 2. 修改配置
编辑 `references/config.py`，设置你的信息：
```python
USER_NAME = "你的名字"
GRADUATION_YEAR = 2028  # 毕业年份
TARGET_CITY = "广州"
SEARCH_KEYWORD = "Python实习生"
```

### 3. 运行投递
```python
from scripts.apply_all import JobHunter
hunter = JobHunter()
hunter.run(platform="51job", pages=5)
```

---

## 文件结构

```
job-hunt-complete-guide/
├── SKILL.md                 # 本文件（说明文档）
├── references/
│   ├── config.py            # 配置文件（用户信息）
│   ├── tools.py             # 基础工具函数
│   └── platforms/
│       ├── 51job.py         # 前程无忧专用
│       ├── boss.py          # BOSS直聘专用
│       ├── zhaopin.py       # 智联招聘专用
│       └── liepin.py        # 猎聘专用
├── scripts/
│   ├── apply_all.py         # 主入口脚本
│   ├── filter.py            # 岗位筛选逻辑
│   └── cleanup.py           # 标签页清理
└── examples/
    └── demo.py              # 使用示例
```

---

## 核心组件

### 1. 配置文件 (`references/config.py`)

```python
# 用户信息
USER_NAME = "朱瀚晖"
GRADUATION_YEAR = 2028  # 28届毕业
IS_FRESH_GRADUATE = False

# 投递目标
TARGET_CITY = "广州"
SEARCH_KEYWORD = "Python实习生"
DAILY_LIMITS = {
    "boss": 120,
    "51job": 100,
    "zhaopin": 999,
    "liepin": 999
}

# Chrome配置
CHROME_PID = 33280
WINDOW_ID = 3017106
CUA_DRIVER = r"C:\Users\K-ON的学习本\AppData\Local\Programs\Cua\cua-driver\bin\cua-driver.exe"

# 筛选规则
EXCLUDE_LABELS = ["校招", "社招"]
INCLUDE_LABELS = ["实习"]
EXCLUDE_KEYWORDS = ["应届生", "硕士", "博士", "全职"]
```

### 2. 基础工具 (`references/tools.py`)

```python
import subprocess, json, time

class CuaDriver:
    """cua-driver MCP 接口封装"""
    
    def __init__(self, pid, window_id, driver_path):
        self.pid = pid
        self.window_id = window_id
        self.driver_path = driver_path
    
    def run_js(self, js_code):
        """执行JavaScript"""
        payload = json.dumps({
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "page",
                "arguments": {
                    "pid": self.pid,
                    "window_id": self.window_id,
                    "action": "execute_javascript",
                    "javascript": js_code
                }
            },
            "id": 1
        })
        result = subprocess.run(
            [self.driver_path, "mcp"],
            input=payload, capture_output=True, text=True, timeout=15
        )
        return self._parse_result(result.stdout)
    
    def press_key(self, keys):
        """按键"""
        payload = json.dumps({
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "hotkey",
                "arguments": {
                    "pid": self.pid,
                    "window_id": self.window_id,
                    "keys": keys
                }
            },
            "id": 1
        })
        subprocess.run(
            [self.driver_path, "mcp"],
            input=payload, capture_output=True, text=True, timeout=15
        )
    
    def get_tab_count(self):
        """获取标签页数量"""
        payload = json.dumps({
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "get_window_state",
                "arguments": {"pid": self.pid, "window_id": self.window_id}
            },
            "id": 1
        })
        result = subprocess.run(
            [self.driver_path, "mcp"],
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
    
    def _parse_result(self, output):
        """解析MCP返回结果"""
        for line in output.strip().split('\n'):
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
```

### 3. 岗位筛选 (`scripts/filter.py`)

```python
class JobFilter:
    """岗位筛选器"""
    
    def __init__(self, config):
        self.config = config
    
    def get_job_label(self, driver, job_index):
        """提取岗位的jobLabel标签"""
        result = driver.run_js(f"""
        var cards = document.querySelectorAll(".joblist-item");
        var card = cards[{job_index}];
        if(card) {{
            var html = card.innerHTML;
            var match = html.match(/jobLabel&quot;:&quot;([^&]*)&quot;/);
            return match ? match[1] : "";
        }}
        return "";
        """)
        return result or ""
    
    def should_apply(self, driver, job_index):
        """判断是否应该投递"""
        label = self.get_job_label(driver, job_index)
        
        # 排除校招/社招
        if label in self.config.EXCLUDE_LABELS:
            return False, f"exclude:{label}"
        
        # 投递实习
        if label in self.config.INCLUDE_LABELS:
            return True, f"include:{label}"
        
        # 无标签时根据标题判断
        result = driver.run_js(f"""
        var cards = document.querySelectorAll(".joblist-item");
        var card = cards[{job_index}];
        if(card) {{
            var title = card.innerText.split("\\n")[0] || "";
            var hasExclude = {json.dumps(self.config.EXCLUDE_KEYWORDS)}.some(k => title.includes(k));
            var hasInclude = {json.dumps(self.config.INCLUDE_KEYWORDS)}.some(k => title.includes(k));
            return hasExclude ? "exclude" : (hasInclude ? "include" : "none");
        }}
        return "none";
        """)
        
        if result == "exclude":
            return False, "exclude:关键词"
        elif result == "include":
            return True, "include:关键词"
        
        return False, "no_match"
```

### 4. 主入口 (`scripts/apply_all.py`)

```python
from references.config import *
from references.tools import CuaDriver
from scripts.filter import JobFilter

class JobHunter:
    """投递猎手 - 主控制器"""
    
    def __init__(self):
        self.driver = CuaDriver(CHROME_PID, WINDOW_ID, CUA_DRIVER)
        self.filter = JobFilter(self)
        self.applied_count = 0
        self.skipped_count = 0
    
    def run(self, platform="51job", pages=5):
        """运行投递"""
        print(f"=== 开始投递 {platform} ===\n")
        
        # 导航到搜索页
        self.navigate(platform)
        
        # 检查登录
        if not self.check_login(platform):
            print("⚠️ 请先登录！")
            return
        
        # 投递多页
        for page in range(1, pages + 1):
            print(f"\n--- 第{page}页 ---")
            if page > 1:
                self.go_to_page(page)
            
            applied, skipped = self.apply_page()
            self.applied_count += applied
            self.skipped_count += skipped
        
        # 清理标签
        self.cleanup_tabs()
        
        # 统计
        print(f"\n=== 完成 ===")
        print(f"投递: {self.applied_count}个")
        print(f"跳过: {self.skipped_count}个")
    
    def navigate(self, platform):
        """导航到搜索页"""
        urls = {
            "51job": f"https://we.51job.com/pc/search?keyword={SEARCH_KEYWORD}{TARGET_CITY}&searchType=2&sortType=0",
            "boss": f"https://www.zhipin.com/web/geek/job?query={SEARCH_KEYWORD}&city=101280100",
            "zhaopin": f"https://sou.zhaopin.com/?jl=763&kw={SEARCH_KEYWORD}&srccode=401801",
            "liepin": f"https://www.liepin.com/zhaopin/?key={SEARCH_KEYWORD}&city=050020"
        }
        self.driver.run_js(f'window.location.href = "{urls[platform]}"; "ok"')
        time.sleep(4)
    
    def check_login(self, platform):
        """检查登录状态"""
        if platform == "51job":
            result = self.driver.run_js('document.querySelector("header").innerText.includes("登录") ? "no" : "yes"')
            return "yes" in str(result)
        return True  # 其他平台暂时返回True
    
    def apply_page(self):
        """投递当前页"""
        applied = 0
        skipped = 0
        
        for i in range(20):
            should, reason = self.filter.should_apply(self.driver, i)
            
            if not should:
                print(f"  [{i:2d}] ❌ {reason}")
                skipped += 1
                continue
            
            result = self.apply_with_check(i)
            print(f"  [{i:2d}] {result}")
            
            if result == "成功":
                applied += 1
            
            time.sleep(1.5)
        
        self.cleanup_tabs()
        return applied, skipped
    
    def apply_with_check(self, job_index):
        """投递并检查跳转"""
        url_before = self.driver.run_js('window.location.href')
        
        self.driver.run_js(f"""
        var cards = document.querySelectorAll(".joblist-item");
        var card = cards[{job_index}];
        if(card) {{
            var btn = card.querySelector(".btn.apply");
            if(btn && btn.textContent.trim() === "投递") btn.click();
        }}
        """)
        
        time.sleep(1.5)
        
        url_after = self.driver.run_js('window.location.href')
        
        if "51job" not in str(url_after):
            self.driver.press_key(["ctrl", "w"])
            time.sleep(0.3)
            self.driver.press_key(["ctrl", "1"])
            return "跳转已修复"
        
        btn = self.driver.run_js(f"""
        var cards = document.querySelectorAll(".joblist-item");
        var card = cards[{job_index}];
        if(card) {{
            var btn = card.querySelector(".btn.apply");
            return btn ? btn.textContent.trim() : "none";
        }}
        return "no card";
        """)
        
        return "成功" if "已申请" in str(btn) else "失败"
    
    def go_to_page(self, page_num):
        """翻页"""
        self.driver.run_js(f"""
        var pager = document.querySelector(".el-pager");
        var items = pager.querySelectorAll("li");
        if(items[{page_num - 1}]) items[{page_num - 1}].click();
        """)
        time.sleep(3)
    
    def cleanup_tabs(self):
        """清理多余标签"""
        current = self.driver.get_tab_count()
        if current > 4:
            for _ in range(current - 4):
                self.driver.press_key(["ctrl", "9"])
                time.sleep(0.2)
                self.driver.press_key(["ctrl", "w"])
                time.sleep(0.2)
            self.driver.press_key(["ctrl", "1"])
            time.sleep(0.3)

# 使用示例
if __name__ == "__main__":
    hunter = JobHunter()
    hunter.run(platform="51job", pages=5)
```

---

## 使用方法

### 方法1: 直接运行脚本
```python
from scripts.apply_all import JobHunter
hunter = JobHunter()
hunter.run(platform="51job", pages=5)
```

### 方法2: 分步执行
```python
from references.tools import CuaDriver
from scripts.filter import JobFilter

driver = CuaDriver(33280, 3017106, "...")
filter = JobFilter(config)

# 单独投递
for i in range(20):
    should, reason = filter.should_apply(driver, i)
    if should:
        # 执行投递
        pass
```

### 方法3: 自定义配置
```python
# 修改 references/config.py
USER_NAME = "你的名字"
GRADUATION_YEAR = 2028
SEARCH_KEYWORD = "Java实习生"
```

---

## 异常处理

| 问题 | 原因 | 解决方案 |
|:-----|:-----|:---------|
| 跳转到yingjiesheng.com | 校招岗位跳转 | `Ctrl+W` 关闭 + `Ctrl+1` 切回 |
| 登录弹窗 | 未登录 | 提示用户登录 |
| 标签页堆积 | 多次跳转 | 每次投递后 `cleanup_tabs()` |
| 按钮无反应 | 网络延迟 | 增加等待时间 |

---

## 验证清单

投递前：
- [ ] Chrome已打开
- [ ] 已登录目标平台
- [ ] 标签页数量正常（≤4个）
- [ ] 搜索结果正确

投递后：
- [ ] 按钮变成"已申请"
- [ ] 没有跳转到外部网站
- [ ] 标签页数量正常
- [ ] 投递记录已保存

