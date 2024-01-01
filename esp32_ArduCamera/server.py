import urequests, uos, ujson

def upload_photo(path):
    try:
        with open(path, 'rb') as file:
            image_content = file.read()

        url = "https://testdatacollection.chaithanyasaipo.repl.co/upload_image"
        content_type = "image/jpeg"
        headers = {'Content-Type': 'multipart/form-data; boundary=my_boundary'}
        data = (b'--my_boundary\r\n' +
                b'Content-Disposition: form-data; name="file"; filename="' + path.encode('utf-8') + b'"\r\n' +
                b'Content-Type: ' + content_type.encode('utf-8') + b'\r\n\r\n' +
                image_content + b'\r\n' + b'--my_boundary--\r\n')

        response = urequests.post(url, data=data, headers=headers)
        if response.status_code == 200:
            print("Image uploaded successfully and Deleted")
            uos.remove(path)
            return True
        else:
            print("Error uploading image. Status code:", response.status_code)

    except OSError as e:
        print(f"Error accessing or reading file: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False
