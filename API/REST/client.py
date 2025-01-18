import requests


class Client:
    def __init__(self):
        self.req = requests.Session()
        self.call_count = 0

    def reset_session(self):
        self.req.close()  # Close existing session
        self.req = requests.Session()

    def get(self, url, headers):
        try:
            if self.call_count % 100 == 0:
                self.reset_session()
            self.req.headers.update(headers)
            response = self.req.get(url)
            self.call_count += 1
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                print('Failed to retrieve data:', response.status_code)
        except Exception as e:
            print('Failed to retrieve data:', e)
