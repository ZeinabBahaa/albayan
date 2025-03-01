import sys
import os
from multiprocessing import freeze_support
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer, Qt, QSharedMemory
from PyQt6.QtNetwork import QLocalServer, QLocalSocket
from ui.quran_interface import QuranInterface
from core_functions.athkar.athkar_scheduler import AthkarScheduler
from utils.update import UpdateManager
from utils.settings import SettingsManager
from utils.const import program_name, program_icon, user_db_path
from utils.logger import Logger
from utils.sound_Manager import BasmalaManager

class SingleInstanceApplication(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setApplicationName(program_name)
        self.server_name = "Albayan"
        self.local_server = QLocalServer(self)

        self.shared_memory = QSharedMemory("Albayan")
        self.is_running = self.shared_memory.attach()

        if not self.is_running:
            if not self.shared_memory.create(1):
                Logger.error(f"Failed to create shared memory segment: {self.shared_memory.errorString()}")
                sys.exit(1)
            self.setup_local_server()
        else:
            self.notify_existing_instance()
            sys.exit(0)

    def setup_local_server(self):
        if not self.local_server.listen(self.server_name):
            Logger.error(f"Failed to start local server: {self.local_server.errorString()}")
            sys.exit(1)
        self.local_server.newConnection.connect(self.handle_new_connection)

    def notify_existing_instance(self):
        socket = QLocalSocket()
        socket.connectToServer(self.server_name)
        if socket.waitForConnected(1000):
            socket.write(b"SHOW")
            socket.flush()
            socket.waitForBytesWritten(1000)
            socket.disconnectFromServer()
        else:
            Logger.error("Failed to connect to existing instance.")

    def handle_new_connection(self):
        socket = self.local_server.nextPendingConnection()
        if socket:
            socket.readyRead.connect(lambda: self.read_message(socket))

    def read_message(self, socket):
        message = socket.readAll().data().decode()
        if message == "SHOW" and hasattr(self, 'main_window'):
                self.main_window.show()
                self.main_window.raise_()
                self.main_window.activateWindow()
                socket.disconnectFromServer()

    def set_main_window(self, main_window):
        self.main_window = main_window


def call_after_starting(parent: QuranInterface) -> None:
        
    basmala_manager = BasmalaManager("Audio/basmala")
    basmala_manager.play()

    check_update_enabled = SettingsManager.current_settings["general"].get("check_update_enabled", False)
    update_manager = UpdateManager(parent, check_update_enabled)
    update_manager.check_auto_update()

    parent.setFocus()
    QTimer.singleShot(500, parent.quran_view.setFocus)
    

def main():
    try:
        app = SingleInstanceApplication(sys.argv)
        app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        main_window = QuranInterface(program_name)
        app.set_main_window(main_window)
        main_window.show()
        call_after_starting(main_window)
        sys.exit(app.exec())
    except Exception as e:
        print(e)
        Logger.error(str(e))
        QMessageBox.critical(None, "Error", "حدث خطأ. يرجى الاتصال بالدعم للحصول على المساعدة.")
        
if __name__ == "__main__":    
    freeze_support()
    main()
