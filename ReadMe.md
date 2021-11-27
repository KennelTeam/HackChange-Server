# API

В каждом запросе есть параметр ok(True / False)

Если ок, см. возвращаемые поля в таблице методов

Если не ок, возвращается error_code и error_desc(Описание ошибки) 

## Список методов
| Метод      | Параметры | Ответ |
| --- | --- | --- |
| register | login, password | user_id, access_token |
| login | login, password | user_id, access_token |
| getProfile | profile_id | info(id, nickname, avatar_link), посты user'а[post_id] |
| setMyInfo | nickname or/and avatar_link(ссылка полученная от сервера после загрузки аватара) | -- |
| getPost | post_id | id, timestamp, topic(id, title), author(id, nickname, avatar_link), text(контент) |
| allInstruments | -- | instruments[id, name(короткое название), details(описание)] |
| addTopic | instrument_id, title(название) | -- |
| topicsByInstrument | instrument_id | topics[id, title(название)] |
| postsByTopic | topic_id | posts[id, timestamp, author(id, nickname, avatar_link), topic(id, title), text] |
| addPost | topic_id, text(контент) | -- |
| addComment | post_id, text | -- |
| commentsByPost | post_id | comments[timestamp, commenter (id, nickname, avatar_link), text] |
