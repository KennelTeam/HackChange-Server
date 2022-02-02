# HackChange-Server

## API

access_token must be in each request (except register & login)

Each answer (except getAvatar) contains _ok_ parameter (_True / False_)

If not ok, error_code and error_desc (error_description) are returned

If ok, look at the table below to see what is returned

### Methods list

| Method               | Params                          | Response                                                                                                              |
| -------------------- | ------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| register             | nickname, password              | user_id, access_token                                                                                                 |
| login                | nickname, password              | user_id, access_token                                                                                                 |
| getProfile           | user_id                         | am_i_subscribed, subscribers_count(Count of subscribers on this page) info(user_id, nickname), posts by user[post_id] |
| setMyInfo            | nickname                        | --                                                                                                                    |
| getPost              | post_id                         | post_id, votes_count, timestamp, topic(topic_id, title), author(user_id, nickname), text(content)                     |
| allInstruments       | --                              | instruments[instrument_id, name(short title), details(description)]                                                   |
| addTopic             | instrument_id, title            | --                                                                                                                    |
| topicsByInstrument   | instrument_id                   | topics[topic_id, title]                                                                                               |
| postsByTopic         | topic_id                        | posts[votes_count, post_id, timestamp, author(user_id, nickname), topic(topic_id, title), text]                       |
| addPost              | topic_id, text(контент)         | --                                                                                                                    |
| addComment           | post_id, text                   | --                                                                                                                    |
| commentsByPost       | post_id                         | comments[comment_id, timestamp, commenter (user_id, nickname), text]                                                  |
| subscribe            | user_id                         | --                                                                                                                    |
| unsubscribe          | user_id                         | --                                                                                                                    |
| mySubscriptionsPosts | --                              | posts[votes_count, post_id, timestamp, author(user_id, nickname), topic(topic_id, title), text]                       |
| subscribersCount     | user_id                         | subs_count(subscribers count)                                                                                         |
| uploadAvatar         | file(bitmap image - JPG or PNG) | --                                                                                                                    |
| getAvatar            | user_id                         | avatar (the only result, without "ok" field!)                                                                         |
