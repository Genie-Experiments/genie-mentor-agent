import math

import requests


class GoogleSearch:
    def __init__(self, api_key, cx):
        self.api_key = api_key
        self.cx = cx

    def _make_search_call(self, query, max_results):
        search_url = "https://www.googleapis.com/customsearch/v1"
        results = []
        per_request_results = 10
        num_pages = math.ceil(max_results / per_request_results)

        for i in range(num_pages):
            start = i * per_request_results + 1
            params = {
                "q": query,
                "key": self.api_key,
                "cx": self.cx,
                "num": min(per_request_results, max_results - len(results)),
                "start": start,
            }

            try:
                response = requests.get(search_url, params=params)
                response.raise_for_status()
                result_data = response.json()

                items = result_data.get("items", [])
                if not items:
                    break

                for item in items:
                    title = item.get("title")
                    url = item.get("link")
                    description = item.get("snippet", "")
                    image_url = None
                    if "pagemap" in item and "cse_image" in item["pagemap"]:
                        image_data = item["pagemap"]["cse_image"]
                        if image_data and isinstance(image_data, list):
                            image_url = image_data[0].get("src")
                    # if self._is_url_accessible(url):
                    results.append(
                        {
                            "title": title,
                            "url": url,
                            "image_url": image_url,
                            "description": description,
                        }
                    )
            except requests.RequestException as e:
                print(f"Google Search API call failed: {e}")
                return results

        return results

    def search(
        self, query, max_general_results, max_video_results, include_videos=False
    ):
        results = []
        general_results = self._make_search_call(query, 15)
        for item in general_results:
            results.append(
                {
                    "title": item["title"],
                    "url": item["url"],
                    "description": item["description"],
                    "image_url": item["image_url"],
                    "type": "general",
                }
            )

        if include_videos:
            video_results = self._make_search_call(
                f"{query} site:youtube.com", max_video_results
            )
            for item in video_results:
                results.append(
                    {
                        "title": item["title"],
                        "url": item["url"],
                        "image_url": item["image_url"],
                        "type": "video",
                    }
                )

        return list({result["url"]: result for result in results}.values())

    def _is_url_accessible(self, url, timeout=10):
        try:
            response = requests.head(url, timeout=timeout, allow_redirects=True)
            return response.status_code == 200
        except requests.RequestException:
            return False
