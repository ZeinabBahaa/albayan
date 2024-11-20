import time
from typing import Optional
from PyQt6.QtWidgets import QToolBar, QPushButton, QSlider
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from core_functions.Reciters import RecitersManager
from utils.audio_player import AudioPlayer
from utils.settings import SettingsManager
from utils.const import data_folder


class AudioPlayerThread(QThread):
    statusChanged = pyqtSignal()
    waiting_to_load = pyqtSignal(bool)
    playback_finished = pyqtSignal()
    
    def __init__(self, player: AudioPlayer, parent: Optional[object] = None):
        super().__init__(parent)
        self.player = player
        self.url = None    
        self.manually_stopped = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_playback_status)

    def run(self):
        if self.url:
            if self.player.source != self.url or self.player.is_stopped():
                self.waiting_to_load.emit(False)
                self.player.load_audio(self.url)
            self.player.play()
            self.manually_stopped = False
            self.statusChanged.emit()
            self.waiting_to_load.emit(True)

    def check_playback_status(self):
        if not self.player.is_playing():
            self.timer.stop()
            self.statusChanged.emit()
            print(self.manually_stopped)
            if not self.player.is_paused() and not self.manually_stopped:
                self.playback_finished.emit()

    def set_audio_url(self, url: str):
        self.url = url
        self.quit()
        self.wait()
        


class AudioToolBar(QToolBar):
    def __init__(self, parent: Optional[object] = None):
        super().__init__(parent)
        self.parent = parent
        self.player = AudioPlayer()
        self.reciters = RecitersManager(data_folder / "quran" / "reciters.db")
        self.current_surah = None
        self.current_ayah = None
        self.next_status = True
        self.previous_status = False

        self.play_pause_button = self.create_button(
            "استماع الآية الحالية", self.toggle_play_pause)
        self.stop_button = self.create_button("إيقاف", self.stop_audio)
        self.previous_button = self.create_button(
            "الآية السابقة", self.OnPlayPrevious)
        self.next_button = self.create_button("الآية التالية", self.OnPlayNext)
        self.set_buttons_status()
        self.volume_slider = self.create_slider(0, 100, 50, self.change_volume)

        self.audio_thread = AudioPlayerThread(self.player, self.parent)
        self.audio_thread.statusChanged.connect(
            self.update_play_pause_button_text)
        self.audio_thread.waiting_to_load.connect(self.set_buttons_status)
        self.audio_thread.playback_finished.connect(
            self.OnActionAfterListening)

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
            self.player.pause()
        else:
            reciter_id = SettingsManager.current_settings["listening"]["reciter"]
            ayah_info = self.parent.get_current_ayah_info()
            self.current_surah = ayah_info[0]
            self.current_ayah = ayah_info[3]
            url = self.reciters.get_url(
                reciter_id, self.current_surah, self.current_ayah)
            self.audio_thread.set_audio_url(url)
            self.audio_thread.start()

    def stop_audio(self):
        self.audio_thread.manually_stopped = True
        self.player.stop()

    def navigate_ayah(self, direction: str) -> bool:

        aya_range = self.parent.quran.ayah_data.get_ayah_range()
        if self.current_surah not in aya_range:
            self.current_surah = None
            self.current_ayah = None

        if self.current_surah is None:
            self.current_surah = min(
                aya_range.keys()) if direction == "next" else max(aya_range.keys())
        if self.current_ayah is None:
            self.current_ayah = aya_range[self.current_surah]["min_ayah"] - \
                1 if direction == "next" else aya_range[self.current_surah]["max_ayah"]

        self.current_ayah += 1 if direction == "next" else -1

        if direction == "next":
            if self.current_ayah > aya_range[self.current_surah]["max_ayah"]:
                surah_keys = list(aya_range.keys())
                current_index = surah_keys.index(self.current_surah)
                if current_index < len(surah_keys) - 1:
                    self.current_surah = surah_keys[current_index + 1]
                    self.current_ayah = aya_range[self.current_surah]["min_ayah"]
                else:
                    print("End of Quran reached")
                    return False
        elif direction == "previous":
            if self.current_ayah < aya_range[self.current_surah]["min_ayah"]:
                surah_keys = list(aya_range.keys())
                current_index = surah_keys.index(self.current_surah)
                if current_index > 0:
                    self.current_surah = surah_keys[current_index - 1]
                    self.current_ayah = aya_range[self.current_surah]["max_ayah"]
                else:
                    print("Start of Quran reached")
                    return False

        self.next_status = not (self.current_surah + 1 > max(list(aya_range.keys()))
                                and self.current_ayah + 1 > aya_range[self.current_surah]["max_ayah"])
        self.previous_status = not (self.current_surah - 1 < min(list(aya_range.keys(
        ))) and self.current_ayah - 1 < aya_range[self.current_surah]["min_ayah"])
        self.set_buttons_status()

        return True

    def play_ayah(self):
        self.stop_audio()
        reciter_id = SettingsManager.current_settings["listening"]["reciter"]
        url = self.reciters.get_url(reciter_id, self.current_surah, self.current_ayah)
        self.audio_thread.set_audio_url(url)
        self.audio_thread.start()

    def OnPlayNext(self) -> None:
        if self.navigate_ayah("next"):
            self.play_ayah()

    def OnPlayPrevious(self) -> None:
        if self.navigate_ayah("previous"):
            self.play_ayah()

    def OnActionAfterListening(self):
        action_after_listening = SettingsManager.current_settings["listening"]["action_after_listening"]
        if action_after_listening == 1:
            self.play_ayah()
        elif action_after_listening == 2:
            self.OnPlayNext()

    def change_volume(self, value: int) -> None:
        self.player.set_volume(value / 100)

    def reset_current_ayah(self) -> None:
        self.current_ayah = None
        self.current_surah = None

    def update_play_pause_button_text(self):
        label = "إيقاف مؤقت" if self.player.is_playing() else "استماع الآية الحالية"
        self.play_pause_button.setText(label)
        if hasattr(self.parent, "menu_bar"):
            self.parent.menu_bar.play_pause_action.setText(label)

    def set_buttons_status(self, status: bool = 2) -> None:
        next_status = self.next_status if status else False
        previous_status = self.previous_status if status else False
        self.next_button.setEnabled(next_status)
        self.previous_button.setEnabled(previous_status)
        self.play_pause_button.setEnabled(status)
        if hasattr(self.parent, "menu_bar"):
            self.parent.menu_bar.play_next_action.setEnabled(next_status)
            self.parent.menu_bar.play_previous_action.setEnabled(previous_status)
            self.parent.menu_bar.play_pause_action.setEnabled(status)
            if  status == True:
                self.audio_thread.timer.start(100)
