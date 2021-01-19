# これは何？
オンライン麻雀天鳳で身内大会を開いたときにレートを計算するBotです。

# 利用方法
毎日25:00に自動的に昨日の記録を取ります。
```こうしん {date(YYYYmmdd)} {ROOM_ID}```　で指定した日の記録を取得して更新します

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