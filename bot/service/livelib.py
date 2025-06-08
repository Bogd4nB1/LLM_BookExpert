import requests # type: ignore

url = "https://api.livelib.ru/api/ratingwidget?id=122729&api_key=340e933e5e76fe5ba05e751f042baf90"

response = requests.get(url)
data = response.json()

print(data)