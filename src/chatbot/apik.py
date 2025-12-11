import requests

API = "6f9da219fbfb94771f4f10aa27c92360"
city = "Casablanca"

url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric"
res = requests.get(url)
print(res.status_code, res.text)
