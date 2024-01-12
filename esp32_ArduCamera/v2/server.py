import ujson, gc, uos
import urequests

def csv_maker(some):
    print("some: ", some)
    try:
        gc.collect()
        with open(some, 'r') as file:
            csv_content = file.readlines()
        con = [i for i in csv_content]
        payload = {'csv_content': con}
        json_payload = ujson.dumps(payload)
        print("JSON Sent")
        uploader(json_payload)
        gc.collect()
    except Exception as e:
        print(f"Error: {e}")


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

def upload_photo(path):
    try:
        with open(path, 'r') as file:
            image_content = file.read()

        url = "https://531f5ac0-9df0-4a8c-a737-cf2c52891552-00-2z6iom5vem0nf.sisko.replit.dev/upload_image"
        content_type = "image/jpeg"
        headers = {'Content-Type': 'multipart/form-data; boundary=my_boundary'}
        data = (b'--my_boundary\r\n' +
                b'Content-Disposition: form-data; name="file"; filename="' + path.encode('utf-8') + b'"\r\n' +
                b'Content-Type: ' + content_type.encode('utf-8') + b'\r\n\r\n' +
                image_content + b'\r\n' + b'--my_boundary--\r\n')

        response = urequests.post(url, data=data, headers=headers)
        if response.status_code == 200:
            print("Image uploaded successfully and Deleted")
            #uos.remove(path)
            return True
        else:
            print("Error uploading image. Status code:", response.status_code)

    except OSError as e:
        print(f"Error accessing or reading file: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False
