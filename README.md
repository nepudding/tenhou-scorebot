# これは何？
オンライン麻雀天鳳で身内大会を開いたときにレートを計算するBotです。

# 利用方法
未定

# メモ欄
```
DELETE FROM scores WHERE date BETWEEN '20210116' AND '20210116 24:00';
CREATE TABLE scores(
date timestamp,
id int,
user_name varchar(16),
rank int,
score numeric,
room_id char(5));

```