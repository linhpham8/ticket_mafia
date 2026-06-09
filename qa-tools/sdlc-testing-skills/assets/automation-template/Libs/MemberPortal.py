import requests
import os

def member_portal_upload_file(url, file_path: str, token: str):
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Authorization": f"Bearer {token}"
    }

    filename = os.path.basename(file_path)

    with open(file_path, "rb") as f:
        files = {"files": (filename, f, "application/octet-stream")}
        response = requests.post(url, headers=headers, files=files)

    print("STATUS:", response.status_code)
    print("URL:", url)
    print("FILE:", file_path)

    try:
        resp_json = response.json()
        print("JSON:", resp_json)

        if resp_json.get("meta", {}).get("code") == "200":
            data = resp_json.get("data", [])
            if isinstance(data, list) and data:
                return data[0].get("code")
        return None

    except Exception as e:
        print(f"Lỗi parse JSON: {e}")
        print("Raw Response:", response.text)
        return None


# def member_portal_upload_file(url, file_path: str, token: str):
#     """
#     Upload một file lên API upload-multiple-files và trả về mã code của file.
#     Args:
#         file_path (str): Đường dẫn tuyệt đối tới file cần upload.
#         token (str): Chuỗi Bearer Token để xác thực.
#     Returns:
#         str | None: Giá trị 'code' của file được upload, hoặc None nếu thất bại.
#     """
#     url = f"{url}"
#     # url = f"https://member-pss-{env}.nexa.mobi/api/bff-common/upload-multiple-files"
#     headers = {
#         "Accept": "application/json, text/plain, */*",
#         "Authorization": f"Bearer {token}"
#     }
#     with open(file_path, "rb") as f:
#         files = {"files": (file_path.split("/")[-1], f, "application/octet-stream")}
#         response = requests.post(url, headers=headers, files=files)
#     # Xử lý phản hồi
#     print("STATUS:", response.status_code)
#     print("RESPONSE TEXT:", response.text)
#     try:
#         resp_json = response.json()
#         if resp_json.get("meta", {}).get("code") == "200":
#             data = resp_json.get("data", [])
#             if data and isinstance(data, list):
#                 return data[0].get("code")  # Trả về code của file đầu tiên
#         return None
#     except Exception as e:
#         print(f"Lỗi khi đọc phản hồi: {e}")
#         print("Phản hồi raw:", response.text)
#         return None
    
def ops_portal_upload_file(url, file_path: str, token: str, member_code: str):
    """
    Upload một file lên API upload-multiple-files và trả về mã code của file.
    Args:
        file_path (str): Đường dẫn tuyệt đối tới file cần upload.
        token (str): Chuỗi Bearer Token để xác thực.
    Returns:
        str | None: Giá trị 'code' của file được upload, hoặc None nếu thất bại.
    """
    # url = f"https://ops-pss-{env}.ops.nexa.mobi/api/bff-common/v2/upload-multiple-files?memberCode=ICBVVNVX"
    # 1. Cập nhật URL với f-string và thêm memberCode vào query parameter    
    url = f"{url}?memberCode={member_code}"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Authorization": f"Bearer {token}"
    }
    with open(file_path, "rb") as f:
        files = {"files": (file_path.split("/")[-1], f, "application/octet-stream")}
        response = requests.post(url, headers=headers, files=files)
    # Xử lý phản hồi
    try:
        resp_json = response.json()
        if resp_json.get("meta", {}).get("code") == "200":
            data = resp_json.get("data", [])
            if data and isinstance(data, list):
                return data[0].get("code")  # Trả về code của file đầu tiên
        return None
    except Exception as e:
        print(f"Lỗi khi đọc phản hồi: {e}")
        print("Phản hồi raw:", response.text)
        return None
