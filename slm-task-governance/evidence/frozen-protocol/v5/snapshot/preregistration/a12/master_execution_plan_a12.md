# 預註冊契約與嚴格證據鏈實施規範 (Pre-Registration & Evidence Chain Contract v2.1)

> **狀態**：候選預註冊草案 (Candidate Pre-Registration Draft for Audit)  
> **制定日期**：2026-10-05  
> **目標治理核心**：`pdx-artifact-engine==0.3.0a12`  
> **官方 Wheel SHA-256**：`1ac34e04702029d8b0dd4819d579284a7660ea077fad8ad3489fb5e6b9211a77`  
> **全體矩陣規模**：1,444 唯一實驗列 (DRAFT REGISTRY)

---

## 1. 核心因果宣稱與局限界定 (Causal Claims & Boundary Definitions)

為確保科學發表之可信度，預先界定因果宣稱界限：

1. **Phase 0 介入束定義 (Bundle Intervention)**：
   > **Phase 0 estimates the effect of the governed isolated-dispatch bundle; it does not identify the isolated causal effect of Engine governance.**
   * `goldplan_react` 與 `goldplan_isolated` 同時改變了 context policy、prompting structure、step isolation 與 Engine governance。因此 Phase 0 評估的是「整套隔離治理方案組合」的效益，嚴禁單獨宣稱差異全由 Engine 引起。
2. **Phase 3 階乘歸因界定**：
   * `C0` (Naive) vs. `C2s` (Schema Governance) vs. `C2sf` (Schema + Scalar Contract) 僅歸因於兩條件間實際不同的 prompt / OpenAPI schema / 終端標量格式契約。
3. **統計用語界限**：
   * 嚴格禁止使用「100% zero drift」或「mathematical invariance」等未經形式化證明的用語。
   * 統一採用「Observed Deterministic Reproducibility」（觀測確定性重現），並限定在貪婪解碼下終端答案相同的欄位。

---

## 2. 合法失敗 vs. 基礎設施故障之精確劃分 (Failure Classification)

廢除「每列必須 `engine_execution_count > 0`」的錯誤門禁，消除選擇偏差：

| 執行情境 | 終端結果分類 | 是否為有效實驗列 | 處置方式 |
| :--- | :---: | :---: | :--- |
| 模型提出合法工具呼叫，Engine 執行成功 | `completed` | **有效列 (Valid Row)** | 依答案客觀計分 |
| 模型提出合法呼叫，但工具回傳業務錯誤 (如表達式語法錯) | `completed` | **有效失敗列 (Valid Failure)** | 計為 `success: false`，保留收據 |
| 模型提出不存在的工具、參數違反 Schema、或未授權工具 | `rejected` | **有效失敗列 (Valid Failure)** | **保留為治理拒絕實證，計為失敗** |
| 模型提出決策但 digest 不符被 Engine 攔截 | `rejected` | **有效失敗列 (Valid Failure)** | **保留為防篡改拒絕實證** |
| 模型直接給出最終答案，未提出工具呼叫 | `no_tool` | **有效列 (Valid Row)** | 依預註冊合約計分（標量或文字） |
| Kaggle 節點 GPU OOM、行程中斷、下載遺失 | `infra_error` | **無效列 (Invalid Row)** | **保留 Attempt 記錄，允許基礎設施重試** |
| 未安裝合法 Engine、Adapter 崩潰、證據未落盤 | `infra_error` | **無效列 (Invalid Row)** | 整批判定作廢，基礎設施重測 |

---

## 3. 實驗條件定義與控制組程序隔離 (Arm Definitions & Isolation)

### 3.1 控制組隔離規範
* **Phase 3 `C0_anchor` 與 Phase 0 `goldplan_react`**：
  - **程序隔離原則**：控制組執行路徑嚴格禁止調用或初始化 `GovernedDispatchSession`。若在同一 process 中，僅允許 import 模組（明確定義 import 不構成 treatment），但執行函式必須為純 Python `execute_control_tool`。
  - **帳本標記**：`governed_dynamic_dispatch: false`, `engine_version: null`, `engine_invocations: 0`, `engine_execution_count: 0`, `engine_rejection_count: 0`。
  - **零污染證明**：回傳之驗收包中不得產生任何針對控制組任務之 `.sqlite3` 資料庫或 Engine 收據。

### 3.2 治理組規範
* **Phase 3 `C2s_schema` / `C2sf_scalar` 與 Phase 0 `goldplan_isolated`**：
  - 工具調用**強制 100%** 經由 `GovernedRunnerAdapter` 調用 `pdx-artifact-engine==0.3.0a12` 之 Dynamic Dispatch Service。
  - 每個預期 dispatch step 都必須有可驗證的終端狀態：`completed` | `rejected` | `cancelled` | `failed`。

---

## 4. 三層法醫證據架構與規範雜湊 (3-Tier Forensic Evidence Architecture)

正式實驗回傳包結構：
```text
.eval/runs/<kernel_slug>/<timestamp>/
├── benchmark_ledger.jsonl          # 第一層：任務執行結果與收據摘要
├── engine_evidence.jsonl           # 第二層：RFC 8785 正規化收據投影
├── workflows/                      # 第三層：已完整關閉連線之實體 SQLite 資料庫
│   └── <task_id>_<hash>.sqlite3
├── run_manifest.json               # 批次 Manifest (動態彙總)
├── run_manifest.sha256             # Manifest 獨立 Sidecar 雜湊
└── source_snapshot.tar.gz          # 執行源碼快照
```

### 4.1 Manifest Self-Digest 與 Sidecar 規範
為避免自包含循環雜湊，Manifest 之 Self-Digest 定義為排它投影：
```python
manifest_self_digest = hashlib.sha256(
    rfc8785.dumps({k: v for k, v in manifest.items() if k != "manifest_self_digest"})
).hexdigest()
```
並同時在同目錄產出獨立 Sidecar 檔案 `run_manifest.sha256`，內容為完整 `run_manifest.json` 檔案之 SHA-256。

### 4.2 SQLite Bundle 規範排序雜湊 (Canonical Bundle Digest)
為確保 SQLite 二進位檔案集合具有可驗證確定性：
1. 確保所有 DB 連線已在 Python 退出前完整 `close()`。
2. 禁止殘留 `-wal`、`-shm`、`-journal` 暫存檔（若存在則合併納入）。
3. 取得所有 `.sqlite3` 檔案，以**相對 POSIX 路徑之 UTF-8 byte order** 進行字典排序。
4. 計算每一檔案之獨立 SHA-256。
5. 構造清單結構：`[{"path": rel_posix_path, "sha256": file_hash, "size_bytes": size}, ...]`。
6. 使用 RFC 8785 canonical JSON 序列化該清單，計算其 SHA-256 作為 `sqlite_bundle_sha256`。

---

## 5. 驗證器獨立性與 12 項負向反例測試 (Verifier 12 Negative Counterexamples)

驗證器 [`src/verify_evidence_chain.py`](file:///D:/Projects/Models/pdx-phase0-kaggle/src/verify_evidence_chain.py) 必須獨立實作，**嚴格禁止 import `src.engine_adapter`**，避免共用 digest 投影錯誤。

驗證器必須通過以下 12 類負向測試（`tests/test_verifier_counterexamples.py`）：
* **T1**：刪除任一筆 completed 呼叫的 terminal receipt $\to$ **FAIL** (Receipt missing)
* **T2**：修改工具輸出 CAS 檔案中的 1 個 byte $\to$ **FAIL** (CAS hash mismatch)
* **T3**：控制組 (C0) 篡改標記 `governed_dynamic_dispatch=true` $\to$ **FAIL** (Control contamination)
* **T4**：治理組繞過 Engine 直接呼叫原生執行器 $\to$ **FAIL** (No engine activation trace)
* **T5**：竄改 Manifest 中的 `total_invocations` (加減 1) $\to$ **FAIL** (Count mismatch)
* **T6**：竄改帳本中的 `engine_version_observed` 字串 $\to$ **FAIL** (Package version conflict)
* **T7**：離線 Wheel SHA-256 與官方公布之 a12 wheel 不符 $\to$ **FAIL** (Untrusted wheel binary)
* **T8**：Decision receipt digest 遭篡改 $\to$ **FAIL** (Fail-closed by Engine)
* **T9**：合法的模型拒絕呼叫 (Rejected Dispatch) $\to$ **PASS** (Preserved as valid failure)
* **T10**：出現重複的 `(model, condition, task_id)` $\to$ **FAIL** (Duplicate evaluation key)
* **T11**：缺少預註冊清單中的任一列 $\to$ **FAIL** (`BATCH INCOMPLETE`)
* **T12**：控制組 (C0) 回傳包中出現任何 `.sqlite3` 或 Engine receipt $\to$ **FAIL** (Control leak)

---

## 6. Apertus 准入門檻檢核 (Apertus Admission Gate)

為確保 `swiss-ai/Apertus-v1.5-8B` 符合正式發布標準，必須在雙 T4 上通過**獨立准入測試**，通過後方可納入正式 54 列。Smoke test 數據不計入正式結果：

1. **Model ID 凍結**：`swiss-ai/Apertus-v1.5-8B`。
2. **授權合規**：確認 Kaggle Secrets 之 `HF_TOKEN` 具有有效存取權限。
3. **專屬依賴鎖定**：使用 Swiss AI 官方 transformers 分支（支援 `apertus1p5` 與 xIELU）。
4. **硬體載入與顯存測量**：在 Dual Tesla T4 上無 OOM 完成固定 admission workload，記錄兩張 GPU 的 peak allocated/reserved memory。
5. **Thinking 模式鎖定**：傳遞 `enable_thinking=False`（關閉 thinking mode）。
6. **准入測試 1 (Control)**：1 題 C0 測試，確認純推論輸出正常。
7. **准入測試 2 (Valid Dispatch)**：1 題合法工具調用，產生完整 Terminal Receipt 與 CAS SHA-256。
8. **准入測試 3 (Schema Rejection)**：1 題故意提供非法參數，確認 Engine 產生正規拒絕收據且模型承擔失敗。
9. **准入測試 4 (收據檢驗)**：收據 100% 通過獨立驗證器檢驗。
10. **正式 Campaign 簽署**：由腳本自動生成 Apertus 准入核准標記（Admission Ticket），解鎖 54 列正式評估。

---

## 7. 全矩陣 1,444 列預註冊清單 (Pre-Registration Registry)

總規模：1,444 唯一實驗列
* **Phase 3 五大基準模型**：5 模型 × 3 條件 × 18 題 = 270 列
* **Phase 3 Apertus 主權模型**：1 模型 × 3 條件 × 18 題 = 54 列
* **Phase 0 跨五模型雙臂比較**：5 模型 × 2 條件 × 112 題 = 1,120 列
* **合計**：**1,444 列** (零重複、零缺失)

### 凍結超參數
* **解碼模式**：Greedy Decoding (`do_sample=False`, `temperature=0.0`)。
* **隨機種子**：`seed=42`。
* **Max Tokens**：單步 256 tokens，終端 512 tokens。
* **量化設定**：8-bit (`BitsAndBytesConfig(load_in_8bit=True, llm_int8_threshold=6.0)`)。
* **評分合約**：由 [`src/scoring.py`](file:///D:/Projects/Models/pdx-phase0-kaggle/src/scoring.py) 依 `task.expected_answer` 嚴格盲化計分，禁止人工介入改答案。
