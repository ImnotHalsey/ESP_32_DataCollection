import ujson, gc, uos,urequests

def uploader(json_data):
    response = None  
    try:
        api_url = "https://531f5ac0-9df0-4a8c-a737-cf2c52891552-00-2z6iom5vem0nf.sisko.replit.dev/get_data"
        print("Posting...")
        response = urequests.post(api_url, data=json_data, headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            print(response.text)
            return True
        else:
            print(f"API call failed with status code: {response.status_code}")
    except OSError as e:
        print(f"Network error: {str(e)}")
    except ValueError as e:
        print(f"JSON encoding error: {str(e)}")
    finally:
        if response:
            response.close()