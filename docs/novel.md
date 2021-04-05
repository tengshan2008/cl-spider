# Novel

**小说**的数据字典

| Field       | Type     | Void | Default | Description             |
| ----------- | -------- | ---- | ------- | ----------------------- |
| id          | Number   | No   |         | primary key (auto inc)  |
| origin_id   | String   | No   |         | novel's origin id       |
| title       | String   | No   | UNKNOW  | novel's title           |
| author      | String   | Yes  |         | novel's author          |
| public_date | Datetime | Yes  |         | novel's public date     |
| category    | String   | Yes  |         | novel's category        |
| link        | String   | Yes  |         | novel's link            |
| size        | Number   | No   | 0       | novel's content size    |
| status      | Number   | No   | 0       | 0: exist, 1: deleted    |
| path        | String   | Yes  |         | novel's store path      |
| share       | String   | Yes  |         | novel's share link      |
| created_at  | Datetime | No   |         | record created datetime |
| updated_at  | Datetime | No   |         | record updated datetime |
| deleted_at  | Datetime | Yes  |         | record deleted datetime |
