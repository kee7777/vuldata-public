import requests

def check_url_alive(url, timeout=10):
    # Check if a website link is working
    try: 
        # First try a HEAD request (fast)
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        if response.status_code < 400:
            return True  # Website works

        # If HEAD did not work, try GET request
        response = requests.get(url, timeout=timeout, allow_redirects=True)
        return response.status_code < 400  # True if website works
    except requests.RequestException:
        # If there is an error, assume the website is not working
        return False
