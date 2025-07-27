import requests

def fetch_data_from_indianapi(ticker):
    API_KEY = "sk-live-wxdmCeEuPdvhKpfITkpzMNgxzMv35RN5oKRizRsh"  # Replace with your API key
    BASE_URL = "https://stock.indianapi.in/stock"
    url = f"{BASE_URL}?name={ticker.upper()}"
    headers = {
        "X-API-Key": API_KEY
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error: {response.status_code} - {response.text}")