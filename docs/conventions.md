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

## ドメインモデリング（軽量DDD）

層状ディレクトリ（domain/application/infrastructure）は導入しない。以下の3原則だけを徹底する。

### 1. 命名をビジネス言語と一致させる

コード上の変数名・関数名・クラス名は、ルート `CONTEXT.md` のユビキタス言語表の用語をそのまま使う。
翻訳や省略（例：「注文」を`req`と略す）をしない。新しいドメイン概念が出てきたら、実装前に `CONTEXT.md` へ追記してから使う。

### 2. ドメインロジックをI/Oから分離する

「業務ルールの判断」と「ファイル/DB/API等の入出力」を同じ関数に混ぜない。

```python
# Bad: 判定とI/Oが混在
def process_order(order_id: str) -> None:
    order = fetch_from_db(order_id)      # I/O
    if order.total < 0:                   # ドメインルール
        raise ValueError("合計金額が負です")
    save_to_db(order)                     # I/O

# Good: 判定を独立した純粋関数に分離
def validate_order(order: Order) -> None:
    """ドメインルール：合計金額は0以上でなければならない"""
    if order.total < 0:
        raise ValueError(f"合計金額が負です: {order.total}")

def process_order(order_id: str) -> None:
    order = fetch_from_db(order_id)   # I/O
    validate_order(order)              # ドメインルール（純粋関数・単体テストしやすい）
    save_to_db(order)                  # I/O
```

### 3. 貧血ドメインモデルを避ける

データを持つだけのクラス（getter/setterしかない）にせず、
そのデータに関するビジネスルールはできるだけ同じ場所（同じモジュール）にまとめる。
「このデータに対して許される操作は何か」を常に問う。
