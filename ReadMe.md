# API

В каждом запросе (кроме register и login) обязан быть access_token

В каждом ответе есть параметр ok(True / False)

Если ок, см. возвращаемые поля в таблице методов

Если не ок, возвращается error_code и error_desc(Описание ошибки) 

## Список методов
| Метод | Параметры | Ответ |
| --- | --- | --- |
| register | nickname, password | user_id, access_token |
| login | nickname, password | user_id, access_token |
| getProfile | user_id | info(user_id, nickname, avatar_link), посты user'а[post_id] |
| setMyInfo | nickname or/and avatar_link(ссылка полученная от сервера после загрузки аватара) | -- |
| getPost | post_id | post_id, timestamp, topic(topic_id, title), author(user_id, nickname, avatar_link), text(контент) |
| allInstruments | -- | instruments[instrument_id, name(короткое название), details(описание)] |
| addTopic | instrument_id, title(название) | -- |
| topicsByInstrument | instrument_id | topics[topic_id, title(название)] |
| postsByTopic | topic_id | posts[post_id, timestamp, author(user_id, nickname, avatar_link), topic(topic_id, title), text] |
| addPost | topic_id, text(контент) | -- |
| addComment | post_id, text | -- |
| commentsByPost | post_id | comments[comment_id, timestamp, commenter (user_id, nickname, avatar_link), text] |
| subscribe | user_id | -- |
| mySubscriptionsPosts| -- | posts[post_id, timestamp, author(user_id, nickname, avatar_link), topic(topic_id, title), text] |
| subscribersCount | user__id | subs_count(Количество подписчиков) |