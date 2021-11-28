import requests

data = {
    2: [
        'Яндекс',
        'Сбер',
        'Тинькофф',
        'Apple',
    ],
    3: [
        'Облигация Российской Федерации'
    ],
    4: [
        'Доллар Американский',
        'Гривна',
        'Евро',
        'Фунт',
        'Рубль Российский',
        'Рубль Белорусский',
        'Динар',
        'Франк',
    ],
    5: [
        'Опцион XYZ'
    ],
    6: [
        'Золото',
        'Серебро',
    ],
    7: [
        'NASDAQ',
    ]
}

access_token = 'pnNQtZfjFDsKjlZAMgbKRwRxvVbqKZVNmXYhCNIBJKSiYIvlWXlTeYVCdUQYIwPa'

for instrument_id in data.keys():
    for title in data[instrument_id]:
        link = 'http://18.133.117.201:5000/addTopic?access_token=' + access_token + '&instrument_id=' + str(instrument_id) + '&title=' + title
        requests.get(link)
