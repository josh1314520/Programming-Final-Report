# 主線任務系統 路由設計 (ROUTES.md)

本文件規劃 Flask 控制器的路由與對應的前端視圖。

## 1. 路由總覽表格

| 功能 | HTTP 方法 | URL 路徑 | 對應視圖/模板 | 說明 |
| :--- | :--- | :--- | :--- | :--- |
| 主控台首頁 | GET | `/` | `templates/index.html` | 顯示角色狀態、進行中任務、已完成任務與任務建立器 |
| 取得冒險者資訊 | GET | `/api/adventurer` | — | 以 JSON 傳回當前登入冒險者的等級、經驗與金幣等資訊 |
| 取得主線任務清單 | GET | `/api/quests` | — | 傳回所有任務定義、玩家接取狀態及子目標 |
| 簽訂契約（接取任務）| POST | `/api/quests/<int:quest_id>/accept`| — | 點擊接取後更新狀態為 `active`，傳回成功訊息 |
| 提交開戶任務表單 | POST | `/api/quests/1/submit` | — | 接收並驗證開戶表單，派發 +100 金幣, +150 EXP，解鎖後續任務 |
| 提交保單分析表單 | POST | `/api/quests/2/submit` | — | 接收並驗證保單表單，派發 +250 金幣, +300 EXP，更新冒險者狀態 |
| 建立自訂主線任務 | POST | `/api/quests/create` | — | 提供管理員/使用者自由擴展全新主線任務（含子目標與前置解鎖） |

---

## 2. 關鍵 API 詳細規格說明

### 2.1 取得主線任務清單 (`GET /api/quests`)
- **回應內容 (200 OK)**:
```json
{
  "quests": [
    {
      "id": 1,
      "title": "契約之印 (開戶任務)",
      "description": "與冒險者公會簽訂神聖的黃金契約，開啟個人專屬的冒險者金庫保險箱。",
      "story_intro": "新手冒險者，歡迎來到金庫公會。在這裡，唯有刻下『契約之印』，你的財富才能受到魔法結界的終身庇護。請簽下你的真名與抉擇！",
      "reward_gold": 100,
      "reward_exp": 150,
      "prerequisite_quest_id": null,
      "status": "available",
      "objectives": [
        {
          "id": 1,
          "description": "登記您的冒險者真實姓名",
          "code_identifier": "real_name"
        },
        {
          "id": 2,
          "description": "選擇您的守護冒險職業",
          "code_identifier": "character_class"
        },
        {
          "id": 3,
          "description": "設定六位數以上的金庫安全密碼",
          "code_identifier": "vault_password"
        },
        {
          "id": 4,
          "description": "輸入冒險執照編號 (格式: ADV-XXXXX)",
          "code_identifier": "license_number"
        }
      ]
    }
  ]
}
```

### 2.2 提交開戶表單 (`POST /api/quests/1/submit`)
- **請求參數 (JSON)**:
```json
{
  "real_name": "林克",
  "character_class": "Warrior",
  "vault_password": "supersecretpassword123",
  "license_number": "ADV-98765"
}
```
- **回應內容 - 成功 (200 OK)**:
```json
{
  "success": true,
  "message": "契約之印簽訂成功！冒險金庫已啟用！",
  "rewards": {
    "gold": 100,
    "exp": 150
  },
  "new_stats": {
    "level": 1,
    "exp": 150,
    "gold": 600,
    "title": "正式冒險者",
    "is_level_up": false
  }
}
```
- **回應內容 - 失敗 (400 Bad Request)**:
```json
{
  "success": false,
  "error": "冒險執照編號格式錯誤！正確格式應為 'ADV-' 後接 5 碼數字，例如 ADV-12345。"
}
```

### 2.3 提交保單分析表單 (`POST /api/quests/2/submit`)
- **請求參數 (JSON)**:
```json
{
  "risk_level": "medium",
  "coverage_amount": 150000,
  "insurance_types": [" casualty", "inventory"]
}
```
- **回應內容 - 成功 (200 OK)**:
```json
{
  "success": true,
  "message": "命運之御防禦矩陣布署完畢！保單分析已生效！",
  "rewards": {
    "gold": 250,
    "exp": 300
  },
  "new_stats": {
    "level": 3,
    "exp": 100,
    "gold": 850,
    "title": "精銳冒險者 (Level Up!)",
    "is_level_up": true,
    "level_ups": 2
  }
}
```
