import json
import logging
from typing import Union
from robot.api.deco import keyword, library
from robot.api import logger
from jsonpath_ng.ext import parse as parse_jsonpath
from extend_pss_oracle import _instances as pss_instances
from extend_nextid_oracle import _instances as nextid_instances
from extend_nsp_postgresql import _instances as nsp_instances

import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@library
class DatabaseOutput:
    """Library for outputting Oracle database query results using JSONPath"""
    ROBOT_LIBRARY_SCOPE = "TEST CASE"

    def __init__(self) -> None:
        logger.debug("Initializing DatabaseOutput")
        self.pss_instances = pss_instances
        self.nextid_instances = nextid_instances
        self.nsp_instances = nsp_instances

        logger.debug(f"PSS instances ref: {self.pss_instances}")
        logger.debug(f"NEXTID instances ref: {self.nextid_instances}")
        logger.debug(f"NSP instances ref: {self.nsp_instances}")

    def _log_json(self, json_data, message="", sort_keys=False, also_console=True):
        """Custom JSON logging function"""
        logger.debug(f"Called _log_json with data: {json_data}, message: {message}")
        try:
            formatted_json = json.dumps(json_data, sort_keys=sort_keys, indent=4, ensure_ascii=False)
            if also_console:
                logger.info(f"{message}\n{formatted_json}")
            logger.info(f"{message}\n{formatted_json}")
        except (TypeError, ValueError) as e:
            logger.info(f"Failed to log JSON: {e}")
            logger.info(f"{message}\n{str(json_data)}")

    @keyword('Output Database')
    def output_database(self, json_path: str, file_path: Union[str, None] = None, append: bool = False, sort_keys: bool = False, also_console: bool = True):
        """
        Query the latest Oracle database result using JSONPath and log or save to file.

        Args:
            json_path: Biểu thức JSONPath (ví dụ: $..trace_no)
            file_path: Đường dẫn để lưu kết quả (tùy chọn)
            append: Nếu là True thì thêm vào cuối file, mặc định là False
            sort_keys: Nếu là True thì sắp xếp các khóa JSON, mặc định là False
            also_console: Nếu là True thì cũng ghi log ra console, mặc định là True
        Returns:
            Queried JSON result
        """

    # Lấy instance cuối cùng của mỗi loại
        candidates = []
        if self.pss_instances:
            candidates.append(self.pss_instances[-1])
        if self.nextid_instances:
            candidates.append(self.nextid_instances[-1])
        if self.nsp_instances:
            candidates.append(self.nsp_instances[-1])

        if not candidates:
            logger.error("No instances available")
            raise RuntimeError("No instances: No queries executed.")

        # Chọn instance mới nhất theo timestamp
        instance = max(candidates, key=lambda x: x["ts"])
        json_data = instance["response"]["body"]
        logger.debug(f"JSON data for Output Database: {json_data}, type={instance['type']}")

        try:
            query = parse_jsonpath(json_path)
            matches = [m.value for m in query.find(json_data)]

            if not matches:
                raise ValueError(f"JSONPath query '{json_path}' did not match anything")

            result = matches[0] if len(matches) == 1 else matches

            self._log_json(result, sort_keys=sort_keys, also_console=also_console)

            if file_path:
                try:
                    content = json.dumps(result, ensure_ascii=False, indent=4, sort_keys=sort_keys)
                    write_mode = "a" if append else "w"
                    with open(file_path, write_mode, encoding="utf-8") as f:
                        f.write(content)
                except OSError as e:
                    raise RuntimeError(f"Error writing to file '{file_path}': {e}")

            return result

        except Exception as e:
            logger.error(f"Error in Output Database: {e}")
            raise ValueError(f"Invalid JSONPath query '{json_path}': {e}")
