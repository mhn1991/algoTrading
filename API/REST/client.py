import requests


class Client:
    def __init__(self):
        self.req = requests.Session()

    def get(self, url, headers):
        self.req.headers.update(headers)
        response = self.req.get(url)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print('Failed to retrieve data:', response.status_code)
