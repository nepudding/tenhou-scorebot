# これは何？
極東麻雀界の対戦記録を取得して表示するBotです。

# 機能一覧
毎日25:00に自動的に昨日の記録を取ります。
# 利用方法

```せいせき```　
現在の成績を表示します。

```こうしん {date(YYYYmmdd)} {ROOM_ID}```　
指定した日の記録を取得して更新します

```ゆーざー {ニックネーム} {天鳳名}```　
指定した名前に登録できます。

```にゃーん```　にゃーん

# メモ欄
```
scores(
    date timestamp
    id int
    user_name varchar(16)
    rank int
    score numeric
    room_id char(5)
)
```