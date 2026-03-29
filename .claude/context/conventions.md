# コード規約

> このファイルはコードを書く・レビューする作業時のみ読み込む。

## 命名規則

| 対象 | 規則 | 例 |
|------|------|-----|
| 変数・関数 | snake_case | `input_path`, `load_config` |
| クラス | PascalCase | `DataProcessor` |
| 定数 | UPPER_SNAKE | `MAX_RETRIES` |
| テスト関数 | `test_<日本語説明>` | `test_外れ値が除去される` |

## 型ヒント

- 全ての関数に型ヒントをつける（引数・戻り値）
- `Optional[X]` より `X | None` を使う（Python 3.10+）

```python
# Good
def process(df: pd.DataFrame, column: str) -> pd.DataFrame:

# Bad
def process(df, column):
```

## 設定値の扱い

- `src/` のコードに値をハードコードしない
- 設定値は `config/*.yaml` から `load_config()` 経由で取得する
- APIキー等の機密情報は `os.environ` から取得する

## エラーハンドリング

- システム境界（外部入力・外部API）でのみバリデーションする
- 内部コードの保証は信頼する（防御的すぎない）
- エラーメッセージは具体的に（何が・なぜ・どうすればよいかを含める）

```python
# Good
raise ValueError(f"カラム '{column}' がDataFrameに存在しません。利用可能: {list(df.columns)}")

# Bad
raise ValueError("Invalid column")
```

## テスト

- テスト関数名は日本語で「何をテストしているか」を表現する
- 正常系・異常系・境界値を分けて書く
- 1テスト1アサーション（原則）
