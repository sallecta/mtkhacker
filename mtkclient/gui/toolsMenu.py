from PySide6.QtCore import Slot, QObject, Signal
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem


from mtkh_modules.mtkh_vars import MTKH_vars as vars
from mtkclient.gui.toolkit import trap_exc_during_debug, asyncThread, FDialog
from mtkh_modules.da.mtkh_da import MTKH_DA
import os
import sys
import json
sys.excepthook = trap_exc_during_debug

class UnlockMenu(QObject):
    enableButtonsSignal = Signal()
    disableButtonsSignal = Signal()

    def __init__(self, arg_ui, arg_parent, arg_download_agent, arg_sendToLog):  # def __init__(self, *args, **kwargs):
        super(UnlockMenu, self).__init__(parent)
        self.parent = arg_parent
        self.ui = arg_ui
        self.fdialog = FDialog(parent)
        self.mtkClass = arg_download_agent.mtk
        self.sendToLog = arg_sendToLog
        self.download_agent = arg_download_agent

    @Slot()
    def updateLock(self):
        self.enableButtonsSignal.emit()
        result = self.parent.Status['result'][1]
        self.ui.partProgressText.setText(result)
        self.sendToLogSignal.emit(self.tr(result))

    def unlock(self, unlockflag):
        self.disableButtonsSignal.emit()
        self.ui.partProgressText.setText(self.tr("Generating..."))
        thread = asyncThread(self.parent, 0, self.UnlockAsync, [unlockflag])
        thread.sendToLogSignal.connect(self.sendToLog)
        thread.sendUpdateSignal.connect(self.updateLock)
        thread.start()
        thread.wait()
        self.enableButtonsSignal.emit()

    def UnlockAsync(self, toolkit, parameters):
        self.sendToLogSignal = toolkit.sendToLogSignal
        self.sendUpdateSignal = toolkit.sendUpdateSignal
        toolkit.sendToLogSignal.emit(self.tr("Bootloader: ")+parameters[0])
        self.parent.Status["result"] = self.mtkClass.daloader.seccfg(parameters[0])
        self.parent.Status["done"] = True
        self.sendUpdateSignal.emit()


class generateKeysMenu(QObject):
    enableButtonsSignal = Signal()
    disableButtonsSignal = Signal()

    def __init__(self, arg_ui, arg_parent, arg_download_agent, arg_sendToLog):  # def __init__(self, *args, **kwargs):
        super(generateKeysMenu, self).__init__(parent)
        self.parent = arg_parent
        self.ui = arg_ui
        self.fdialog = FDialog(arg_parent)
        self.mtkClass = arg_download_agent.mtk
        self.sendToLog = arg_sendToLog
        self.download_agent = arg_download_agent

    @Slot()
    def updateKeys(self):
        self.ui.keystatuslabel.setText(self.tr(f"Keys saved to {vars.path.hwparamfile}."))
        keycount = len(self.parent.Status['result'])
        self.ui.keytable.setRowCount(keycount)
        self.ui.keytable.setColumnCount(2)

        column = 0
        for key in self.parent.Status['result']:
            skey = self.parent.Status['result'][key]
            if skey is not None:
                self.ui.keytable.setItem(column, 0, QTableWidgetItem(key))
                self.ui.keytable.setItem(column, 1, QTableWidgetItem(skey))
                column+=1
        self.sendToLogSignal.emit(self.tr("Keys generated!"))
        self.enableButtonsSignal.emit()

    def generateKeys(self):
        self.ui.keystatuslabel.setText(self.tr("Generating keys..."))
        thread = asyncThread(self.parent, 0, self.generateKeysAsync, [])
        thread.sendToLogSignal.connect(self.sendToLog)
        thread.sendUpdateSignal.connect(self.updateKeys)
        thread.start()
        self.disableButtonsSignal.emit()

    def generateKeysAsync(self, toolkit, parameters):
        self.sendToLogSignal = toolkit.sendToLogSignal
        self.sendUpdateSignal = toolkit.sendUpdateSignal
        toolkit.sendToLogSignal.emit(self.tr("Generating keys"))
        res = self.mtkClass.daloader.keys()
        if res:
            with open(vars.path.hwparamfile,"w") as wf:
                wf.write(json.dumps(res))
        self.parent.Status["result"] = res
        self.parent.Status["done"] = True
        self.sendUpdateSignal.emit()


