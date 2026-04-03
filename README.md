# TAPD 团队日历钉钉告警页面

这个项目提供了一个简单页面和后端接口，用来：

1. 拉取 TAPD 团队日历接口数据。
2. 识别“未来 2 天内没有工作安排”的开发人员。
3. 通过钉钉群机器人发送告警消息。

## 运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

浏览器访问 `http://localhost:8080`。

## TAPD 返回数据格式（示例）

```json
{
  "members": [
    {
      "name": "Alice",
      "assignments": [
        {"date": "2026-04-03"},
        {"date": "2026-04-04"}
      ]
    },
    {
      "name": "Bob",
      "assignments": []
    }
  ]
}
```

## 告警规则

- 检查区间：`今天` 到 `今天+2天`（含边界）。
- 若开发同学在该区间没有任何安排，则触发钉钉告警。
