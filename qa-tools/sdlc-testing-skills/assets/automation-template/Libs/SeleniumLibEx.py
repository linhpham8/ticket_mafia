from robot.libraries.BuiltIn import BuiltIn, RobotNotRunningError
from robot.api.deco import keyword

class SeleniumLibEx:
    def __init__(self):
        try:
            # Lấy instance SeleniumLibrary khi Robot Framework đang chạy
            self.driver = BuiltIn().get_library_instance('SeleniumLibrary')
        except RobotNotRunningError:
            # Nếu Robot Framework không chạy, driver sẽ được đặt là None
            BuiltIn().fail("Lỗi lấy instance SeleniumLibrary")

    def __capture_and_fail(self, exception: Exception):
        """Chụp ảnh màn hình và báo cáo lỗi."""
        if self.driver:
            # Nếu driver được khởi tạo, chụp ảnh màn hình và báo lỗi
            self.driver.capture_page_screenshot("EMBED")
            BuiltIn().fail(exception)
        else:
            # Nếu Robot Framework không chạy, in thông báo lỗi
            BuiltIn().log_to_console("Không thể chụp ảnh màn hình: Robot Framework không đang chạy.")
            raise exception

    def highlight_element(self, locator: str):
        """Làm nổi bật phần tử được xác định bởi `locator` với viền màu đỏ."""
        if self.driver:
            # Tìm phần tử và thực thi JavaScript để làm nổi bật nó
            element = self.driver.find_element(locator)
            if element:
                script = """
                    var original_style = arguments[0].getAttribute('style');
                    arguments[0].setAttribute('style', original_style + ";box-shadow: inset 0 0 0 2px red;");
                    setTimeout(function(){
                        arguments[0].setAttribute('style', original_style);
                    }, 500);
                """
                self.driver.driver.execute_script(script, element)
        else:
            # Nếu SeleniumLibrary không được khởi tạo, báo lỗi
            raise RuntimeError("SeleniumLibrary chưa được khởi tạo.")

    @keyword("wait_and_highlight_element_visible")
    def wait_and_highlight_element_visible(self, locator: str):
        """Chờ phần tử hiển thị và làm nổi bật phần tử đó."""
        if self.driver:
            try:
                # Chờ cho phần tử hiển thị và làm nổi bật nó
                self.driver.wait_until_element_is_visible(locator)
                self.highlight_element(locator)
            except Exception as e:
                # Báo lỗi và chụp ảnh màn hình nếu có ngoại lệ
                self.__capture_and_fail(e)
        else:
            # Nếu SeleniumLibrary chưa được khởi tạo, báo lỗi
            raise RuntimeError("SeleniumLibrary chưa được khởi tạo.")
        
    @keyword("annotate_element_keyword")
    def annotate_element_keyword(self, locator: str, message: str):
            """Ghi chú phần tử với thông điệp trên trang web."""
            element = self.driver.find_element(locator)
            if element:
                script = """
                    var element = arguments[0];
                    var message = arguments[1];
                    var rect = element.getBoundingClientRect();
                    var annotation = document.createElement('div');
                    annotation.innerText = message;
                    annotation.style.position = 'absolute';
                    annotation.style.left = rect.left + 'px';
                    annotation.style.top = (rect.top - 20) + 'px';
                    annotation.style.backgroundColor = 'yellow';
                    annotation.style.color = 'black';
                    annotation.style.padding = '5px';
                    annotation.style.border = '1px solid black';
                    annotation.style.zIndex = 1000;
                    document.body.appendChild(annotation);
                """
                self.driver.driver.execute_script(script, element, message)
            else:
                raise RuntimeError("Không tìm thấy phần tử.")
