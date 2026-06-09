import requests
from robot.api.deco import keyword, library
from robot.libraries.BuiltIn import BuiltIn
from robot.api import logger


@library
class ExtendKeycloak:

    """Thư viện để tương tác với dịch vụ xác thực Keycloak.

       Thư viện này cung cấp các từ khóa để tương tác với Keycloak cho mục đích xác thực.
       Thư viện được thiết kế để lấy token truy cập bằng giao thức OpenID Connect.

    *Example:*
    | Get Token From Keycloak | ops-portal | qc-auto-test | mypassword |
    """

    @keyword('Get Token From Keycloak')
    def get_token_from_keycloak(self, page: str, user: str, password: str) -> str:
        """
        Lấy token truy cập từ Keycloak cho một trang cụ thể.

        Args:
            page (chuỗi): Mã định danh trang (ví dụ: 'ops-portal', 'member-portal').
            user (chuỗi): Tên người dùng để xác thực.
            password (chuỗi): Mật khẩu để xác thực.

        Returns:
            str: access_token -  cập nhận được từ Keycloak.

        Raises:
            ValueError: Nếu các đối số bắt buộc trống hoặc không hợp lệ.
            RuntimeError: Nếu yêu cầu Keycloak không thành công hoặc phản hồi không hợp lệ.

        Examples:
            | ${token}= | Get Token From Keycloak | ops-portal | qc-auto-test | mypassword |
            | Log       | Access Token: ${token}  |
        """
        if not all([page, user, password]):
            raise ValueError("Page, user, and password must not be empty")

        env = BuiltIn().get_variable_value('${ENV}', 'qc').lower()
        # env = "qc"

        url = f"https://keycloak-admin.ops.masterisegroup.dev/realms/real-{page}-{env}/protocol/openid-connect/token"

        # Prepare payload and headers
        payload = f'grant_type=password&client_id=portal-ops&username={user}&password={password}&scope=openid'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()

            response_data = response.json()
            if 'access_token' not in response_data:
                raise RuntimeError("Access token not found in Keycloak response")

            access_token = response_data['access_token']
            logger.info(f"Successfully retrieved access token for page '{page}' and user '{user}'")
            return access_token

        except requests.RequestException as e:
            logger.error(f"Failed to retrieve token from Keycloak: {str(e)}")
            raise RuntimeError(f"Keycloak request failed: {str(e)}")
        except ValueError as e:
            logger.error(f"Invalid response from Keycloak: {str(e)}")
            raise RuntimeError(f"Failed to parse Keycloak response: {str(e)}")
