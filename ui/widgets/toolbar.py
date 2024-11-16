from PyQt6.QtWidgets import QToolBar, QPushButton, QSlider
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from core_functions.Reciters import RecitersManager
from utils.audio_player import AudioPlayer
from utils.const import data_folder

class AudioPlayerThread(QThread):
    audio_status_changed = pyqtSignal(str)

    def __init__(self, player, reciters, parent=None):
        super().__init__(parent)
        self.player = player
        self.reciters = reciters
        self.url = None

    def run(self):
        if self.url:
            if self.player.source != self.url or self.player.is_stopped():
                self.player.load_audio(self.url)
            self.player.play()
            self.audio_status_changed.emit("إيقاف مؤقت")
        
    def pause_audio(self):
        self.player.pause()
        self.audio_status_changed.emit("استماع الآية الحالية")

    def stop_audio(self):
        self.player.stop()
        self.audio_status_changed.emit("استماع الآية الحالية")

    def set_audio_url(self, url):
        self.url = url

class AudioToolBar(QToolBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.player = AudioPlayer()
        self.reciters = RecitersManager(data_folder / "quran" / "reciters.db")
        
        self.play_pause_button = self.create_button("استماع الآية الحالية", self.toggle_play_pause)
        self.stop_button = self.create_button("إقاف", self.stop_audio)

        self.volume_slider = self.create_slider(0, 100, 50, self.change_volume)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_audio_status)
        self.timer.start(500)

        self.audio_thread = AudioPlayerThread(self.player, self.reciters)
        self.audio_thread.audio_status_changed.connect(self.update_play_pause_button_text)

    def create_button(self, text, callback):
        button = QPushButton(text)
        button.clicked.connect(callback)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.addWidget(button)
        return button

    def create_slider(self, min_value, max_value, default_value, callback):
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_value, max_value)
        slider.setValue(default_value)
        slider.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        slider.valueChanged.connect(callback)
        self.addWidget(slider)
        return slider

    def toggle_play_pause(self):
        if self.player.is_playing():
            self.audio_thread.pause_audio()
        else:                
            ayah_info = self.parent.get_current_ayah_info()
            url = self.reciters.get_url(68, ayah_info[0], ayah_info[3])
            self.audio_thread.set_audio_url(url)
            self.audio_thread.start()

        self.update_play_pause_button_text()

    def stop_audio(self):
        self.audio_thread.stop_audio()

    def change_volume(self, value):
        self.player.set_volume(value / 100)

    def check_audio_status(self):
        self.update_play_pause_button_text()

    def update_play_pause_button_text(self):
        label = "إيقاف مؤقت" if self.player.is_playing() else "استماع الآية الحالية"
        self.play_pause_button.setText(label)
        if hasattr(self.parent, "menu_bar"):
            self.parent.menu_bar.play_pause_action.setText(label)
