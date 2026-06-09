import subprocess,os,threading,datetime
from robot.api.deco import keyword;
from robot.libraries.BuiltIn import BuiltIn
from robot.libraries.Screenshot import Screenshot
import numpy as np
import sys
import time
from win32com.client.makepy import main

@keyword
def Sap_click_release_PO(element_id):

    self = BuiltIn().get_library_instance('SapGuiLibrary')
    self.session.findById(element_id).currentCellColumn = "FUNCTION"
    self.session.findById(element_id).clickCurrentCell()

@keyword
def Sap_select_Order_Type_By_Key(element_id, key_values):

    self = BuiltIn().get_library_instance('SapGuiLibrary')
    self.session.findById(element_id).key = key_values

@keyword
def Sap_close_window():

    self = BuiltIn().get_library_instance('SapGuiLibrary')
    self.session.findById("wnd[0]").close()

if __name__ == "__main__":
    Sap_click_release_PO()
