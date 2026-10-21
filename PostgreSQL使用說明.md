# PostgreSQL 環境設定使用說明

> 本文件記錄本機 PostgreSQL 的安裝、設定與連線方式。
> 建立日期：2026-10-21

---

## 一、環境資訊

| 項目 | 內容 |
|------|------|
| PostgreSQL 版本 | 18.6（64-bit Windows） |
| 安裝位置 | `C:\Program Files\PostgreSQL\18` |
| 服務名稱 | `postgresql-x64-18` |
| 連接埠 | `5432` |
| 主機 | `localhost` |
| 管理帳號 | `postgres` |
| 密碼 | `12345678` |

---

## 二、已完成的設定

### 1. PATH 環境變數（使用者層級）

已將 PostgreSQL 的執行檔目錄加入使用者 PATH：

```
C:\Program Files\PostgreSQL\18\bin
```

**效果**：在任何終端機都能直接使用 `psql`、`pg_dump` 等指令，不必輸入完整路徑。

> ⚠️ 設定後需**重新開啟終端機視窗**才會生效。

### 2. 密碼自動填入檔案（pgpass）

| 項目 | 內容 |
|------|------|
| 檔案位置 | `C:\Users\user\Desktop\pgpass.conf` |
| 環境變數 | `PGPASSFILE` = `C:\Users\user\Desktop\pgpass.conf` |
| 檔案內容 | `localhost:5432:*:postgres:12345678` |

**檔案格式說明**：

```
主機:連接埠:資料庫:使用者:密碼
localhost:5432:*:postgres:12345678
```

其中 `*` 代表「任何資料庫」都適用。

**效果**：連線時**不需要手動輸入密碼**，PostgreSQL 會自動從此檔案讀取。

---

## 三、資料庫清單

| 資料庫名稱 | 用途 |
|-----------|------|
| `AILearn` | 主要使用資料庫（**注意大小寫**） |
| `my_first_db` | 測試用資料庫 |
| `postgres` | 系統預設管理資料庫（請勿刪除） |
| `template0` | 系統樣板（請勿刪除） |
| `template1` | 系統樣板（請勿刪除） |

---

## 四、如何連線

### 基本連線指令

```powershell
psql -U postgres -d AILearn -h localhost
```

- `-U postgres`：指定使用者（U 為**大寫**）
- `-d AILearn`：指定資料庫名稱
- `-h localhost`：指定主機

連線成功後會看到提示字元：

```
AILearn=#
```

### ⚠️ `AILearn` 的大小寫問題

因為此資料庫名稱**包含大寫字母**，PostgreSQL 會區分大小寫，所以使用時**一定要加引號**：

**PowerShell 寫法**（外層單引號、內層雙引號）：

```powershell
psql -U postgres -d '"AILearn"'
```

**CMD（命令提示字元）寫法**：

```cmd
psql -U postgres -d "AILearn"
```

> 若只寫 `-d AILearn`，PostgreSQL 會當成小寫的 `ailearn`，將找不到資料庫。

### 如何離開

在 `psql` 提示字元下輸入：

```
\q
```

---

## 五、常用指令速查

進到 `psql` 之後（提示字元為 `資料庫名稱=#`）：

| 指令 | 功能 |
|------|------|
| `\l` | 列出所有資料庫 |
| `\dt` | 列出目前資料庫的所有資料表 |
| `\d 資料表名稱` | 查看資料表結構 |
| `\du` | 列出所有使用者 |
| `\c 資料庫名稱` | 切換資料庫 |
| `\q` | 離開 psql |

### 實用 SQL 範例

```sql
-- 查詢目前使用者與資料庫
SELECT current_user, current_database();

-- 查詢 PostgreSQL 版本
SELECT version();
```

---

## 六、常見問題排除

### ❌ 錯誤：`無法辨識 'psql' 這個詞彙`

**原因**：PATH 尚未生效。

**解法**：關閉終端機，**重新開啟一個新視窗**。

---

### ❌ 錯誤：`password authentication failed for user "user"`

**原因**：沒有指定 `-U postgres`，系統改用了你 Windows 的登入帳號（`user`）去連線。

**解法**：指令務必加上 `-U postgres`。

```powershell
psql -U postgres -d AILearn -h localhost
```

---

### ❌ 錯誤：`資料庫 "ailearn" 不存在`

**原因**：資料庫名稱含大寫，但指令用了小寫。

**解法**：使用引號包住正確大小寫的名稱。

```powershell
psql -U postgres -d '"AILearn"'
```

---

### ❌ 輸入密碼時畫面毫無反應？

這是**正常現象**。基於安全考量，終端機在輸入密碼時**不會顯示任何字元**（連 `*` 都不會顯示）。直接輸入密碼後按 Enter 即可。

若已設定 `pgpass.conf`，則不會再出現密碼提示。

---

## 七、注意事項與建議

1. **密碼檔案安全性**
   `pgpass.conf` 內的密碼是**明文儲存**。目前密碼為簡單密碼風險較低，但若日後改為重要密碼，建議考慮更安全的做法。

2. **密碼強度建議**
   目前的 `12345678` 較容易猜測，建議未來改為較複雜的密碼。

3. **定期備份**
   若資料庫開始存放重要資料，建議定期備份：

   ```powershell
   pg_dump -U postgres -d AILearn -f "備份路徑\AILearn_backup.sql"
   ```

   還原備份：

   ```powershell
   psql -U postgres -d AILearn -f "備份路徑\AILearn_backup.sql"
   ```

4. **服務管理**
   PostgreSQL 服務名稱：`postgresql-x64-18`

   檢查服務狀態：

   ```powershell
   Get-Service postgresql-x64-18
   ```

   啟動 / 停止服務（需管理員權限）：

   ```powershell
   Start-Service postgresql-x64-18
   Stop-Service postgresql-x64-18
   ```

---

## 八、設定摘要（快速回顧）

| 設定項目 | 值 |
|---------|-----|
| psql 路徑 | `C:\Program Files\PostgreSQL\18\bin\psql.exe` |
| PATH 加入項目 | `C:\Program Files\PostgreSQL\18\bin` |
| 密碼檔 | `C:\Users\user\Desktop\pgpass.conf` |
| 環境變數 | `PGPASSFILE` = `C:\Users\user\Desktop\pgpass.conf` |
| 主要資料庫 | `AILearn` |
| 連線指令 | `psql -U postgres -d '"AILearn"'` |
