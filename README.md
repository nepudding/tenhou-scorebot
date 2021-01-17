# これは何？
オンライン麻雀天鳳で身内大会を開いたときにレートを計算するBotです。

# 利用方法
毎日00:10に自動的に昨日の記録を取ります。
```こうしん {ROOM_ID}```　で今日の記録を取得して更新します

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