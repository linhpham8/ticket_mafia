
from ast import arg
from asyncio.log import logger
import atexit
from time import sleep, time
# from py import builtin
from stf_appium_client import StfClient, AppiumServer, AdbServer
from stf_appium_client.Logger import Logger
from stf_appium_client.tools import parse_requirements
from robot.api.deco import keyword, not_keyword, library
from robot.libraries.BuiltIn import BuiltIn
from os import environ, times
from stf_client.api.user_api import UserApi
from stf_client.api_client import ApiClient, Configuration

STF_HOST = 'http://10.124.57.232'
STF_TOKEN = environ.get("STF_TOKEN")
@not_keyword
def as_seconds(minutes: int):
    return minutes * 60

ROBOT_LIBRARY_SCOPE = 'GLOBAL'


@library(scope='GLOBAL', auto_keywords=True) 
class RobotSTF(Logger):
    """ RobotFramework STF plugin """

    StfClient = StfClient

    @not_keyword
    def __init__(self):
        super().__init__()
        self._stf = self.StfClient.StfClient(STF_HOST)
        self._stf.connect(STF_TOKEN)
        self._devices = list()

        @atexit.register
        def exit_stf():
            nonlocal self
            self.exit_stf()
    @keyword("Lock device")
    def lock_device(self,
             requirements: str,
             wait_timeout=as_seconds(minutes=5),
             timeout_seconds: int = as_seconds(minutes=600),
             shuffle: bool = True):
        """ Allocate phone and return it's details 
        - ``requirements``: requirements={"version":"9"} or requirements={"serial":"123456"} or {"model":"SM-G960F"}
        - ``Return``: device_id or deviceName
        - ``${device_name}`` default variable    
        """
        if isinstance(requirements, str):
            requirements = parse_requirements(requirements)
        self.logger.info(f'Requirements: {requirements}')
        device = self._stf.find_wait_and_allocate(
            requirements=requirements,
            wait_timeout=wait_timeout,
            timeout_seconds=timeout_seconds,
            shuffle=shuffle)
        self._devices.append(device)
        BuiltIn().set_suite_variable("${deviceName}", device.get('serial'))
        return device

    @keyword("Disconnect and Lock device")
    def Disconnect_and_lock_device(self,
             requirements: str,
             wait_timeout=as_seconds(minutes=5),
             timeout_seconds: int = as_seconds(minutes=600),
             shuffle: bool = True,
             forced_stop: bool = True,
             device_farm: bool = True):
        """ Kích device đang bị chiếm quyền và sử dụng devices đó để chạy auto 
        - ``requirements``: Chỉ dùng với requirements={"serial":"123456"}
        - ``Return``: device_id or deviceName
        - ``${device_name}`` default variable  
        - ``${forced_stop}`` Dừng thiết bị
        """
        if device_farm:
            if isinstance(requirements, str):
                requirements = parse_requirements(requirements)        
                if forced_stop:
                    try:              
                        self._stf.release(requirements)
                    except Exception as error:
                        self.logger.warn(error)
                    
            self.logger.info(f'Requirements: {requirements}')
            device = self._stf.find_wait_and_allocate(
                requirements=requirements,
                wait_timeout=wait_timeout,
                timeout_seconds=timeout_seconds,
                shuffle=shuffle)
            
            self._devices.append(device)
            BuiltIn().set_suite_variable("${deviceName}", device.get('serial'))
            return device
        else:
            # requirements = parse_requirements(requirements) 
            return {"ready":device_farm}


    #@not_keyword
    @keyword("exit stf")
    def exit_stf(self):
        """ Thoát khỏi device farm 
        - ``Scope``: suite teardown
        """

        for device in self._devices:
            if device.get('owner') is not None:
                self.logger.warn(f"exit:Release device {device.get('serial')}")
                self.teardown_appium(device)
                try:
                    self.unlock_device(device)
                except Exception as error:
                    self.logger.warn(error)
                
    @keyword("Unlock device")
    def unlock_device(self, device: dict):
        assert device.get('owner'), 'device not locked'
        self._stf.release(device)

    @keyword("Setup appium")
    def setup_appium(self, device):
        if device['ready'] == True: 
            self.start_adb(device)
        self.start_appium(device)

    @keyword("Teardown appium")
    def teardown_appium(self, device: dict):
        try:
            self.stop_appium(device)
        except AssertionError:
            pass
        try:
            self.stop_adb(device)
        except AssertionError:
            pass

    @not_keyword
    def start_adb(self, device: dict):
        assert device, 'device not locked'
        assert not device.get('adb'), 'device adb is already running'
        adb_adr = self._stf.remote_connect(device)
        device['remote_adb_url'] = adb_adr
        adb = AdbServer.AdbServer(adb_adr)
        device['adb'] = adb
        device['adb_port'] = adb.port
        adb.connect()
        return adb.port

    @not_keyword
    def stop_adb(self, device: dict):
        assert device, 'device not locked'
        adb = device.get('adb')
        assert adb, 'device adb not running'
        adb.kill()
        self._stf.remote_disconnect(device)
        device['remote_adb_uri'] = None
        device['adb'] = None
        device['adb_port'] = None

    @keyword("start appium")
    def start_appium(self, device: dict):
        """
        '--base-path', '/wd/hub'
        """
        assert device, 'device not locked'
        assert not device.get('appium'), 'device appium is already running'
        appium = AppiumServer.AppiumServer(['--allow-insecure','chromedriver_autodownload,adb_shell','--base-path', '/wd/hub'])
        device['appium'] = appium
        """ Start appium in local host and return appium url """
        appium_uri = appium.start()
        sleep(3)
        device['appium_uri'] = appium_uri
        BuiltIn().set_suite_variable("${appium_remote}", appium_uri + "/wd/hub")
        # print(appium_uri + "/wd/hub")
        return appium_uri + "/wd/hub"

    @not_keyword
    def stop_appium(self, device: dict):
        assert device, 'device not locked'
        assert device.get('appium'), 'device appium is not running'
        appium = device.get('appium')
        appium.stop()
        device['appium'] = None
        device['appium_uri'] = None
  