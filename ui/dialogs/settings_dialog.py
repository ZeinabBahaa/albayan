from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
QLabel,
    QListWidget,
    QHBoxLayout,
    QListWidgetItem,
    QCheckBox,
    QPushButton,
    QGroupBox,
    QMessageBox,
    QSlider,
    QSpacerItem,
    QSizePolicy
)
from PyQt6.QtGui import QKeySequence
from PyQt6.QtCore import Qt
from utils.settings import SettingsManager

class SettingsDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("الإعدادات")
        self.resize(500, 400)
        self.init_ui()
        self.set_current_settings()

    def init_ui(self):
        main_layout = QVBoxLayout()
        taps_layout = QHBoxLayout()

        list_widget = QListWidget()
        general_item = QListWidgetItem("الإعدادات العامة")
        audio_item = QListWidgetItem("الصوت")
        search_item = QListWidgetItem("البحث")
        list_widget.addItem(general_item)
        list_widget.addItem(audio_item)
        list_widget.addItem(search_item)
        list_widget.currentItemChanged.connect(self.change_category)
        taps_layout.addWidget(list_widget, stretch=1)

        self.group_general = QGroupBox("الإعدادات العامة")
        self.group_general_layout = QVBoxLayout()
        self.run_in_background_checkbox = QCheckBox("تشغيل البرنامج في الخلفية")
        self.auto_save_position_checkbox = QCheckBox("حفظ الموضع الحالي تلقائيًا عند إغلاق البرنامج")
        self.update_checkbox = QCheckBox("التحقق من التحديثات")
        self.log_checkbox = QCheckBox("تمكين تسجيل الأخطاء")
        self.reset_button = QPushButton("استعادة الإعدادات الافتراضية")
        self.reset_button.clicked.connect(self.OnReset)
        

        self.group_general_layout.addWidget(self.run_in_background_checkbox)
        self.group_general_layout.addWidget(self.auto_save_position_checkbox)
        self.group_general_layout.addWidget(self.update_checkbox)
        self.group_general_layout.addWidget(self.log_checkbox)
        self.group_general_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))  # Spacer item
        self.group_general_layout.addWidget(self.reset_button)
        self.group_general.setLayout(self.group_general_layout)
        self.group_general.setVisible(False)
        taps_layout.addWidget(self.group_general, stretch=2)



        self.group_audio = QGroupBox("الصوت")
        self.group_audio_layout = QVBoxLayout()
        self.sound_checkbox = QCheckBox("تفعيل المؤثرات الصوتية")
        self.basmala_checkbox = QCheckBox("تشغيل المؤثرات الصوتية مع فتح البرنامج")
        self.speech_checkbox = QCheckBox("نطق الإجرائات")
        self.volume_label = QLabel("مستوى الصوت")
        self.volume = QSlider(Qt.Orientation.Horizontal)
        self.volume.setRange(0, 100)
        self.volume.setAccessibleName("مستوى الصوت")
        self.volume.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.athkar_volume_label = QLabel("مستوى صوت الأذكار")
        self.athkar_volume = QSlider(Qt.Orientation.Horizontal)
        self.athkar_volume.setRange(0, 100)
        self.athkar_volume.setAccessibleName("مستوى صوت الأذكار")
        self.athkar_volume.setLayoutDirection(Qt.LayoutDirection.LeftToRight)


        self.group_audio_layout.addWidget(self.sound_checkbox)
        self.group_audio_layout.addWidget(self.basmala_checkbox)
        self.group_audio_layout.addWidget(self.speech_checkbox)
        
        self.group_audio_layout.addWidget(self.volume_label)
        self.group_audio_layout.addWidget(self.volume)
        self.group_audio_layout.addWidget(self.athkar_volume_label)
        self.group_audio_layout.addWidget(self.athkar_volume)



        # Add a spacer for layout consistency
        self.group_audio_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.group_audio.setLayout(self.group_audio_layout)
        self.group_audio.setVisible(False)
        taps_layout.addWidget(self.group_audio, stretch=2)


        self.group_search = QGroupBox("إعدادات البحث")
        self.group_search_layout = QVBoxLayout()
        self.ignore_tashkeel_checkbox = QCheckBox("تجاهل التشكيل")
        self.ignore_hamza_checkbox = QCheckBox("تجاهل الهمزات")
        self.match_whole_word_checkbox = QCheckBox("تطابق الكلمة بأكملها")

        self.group_search_layout.addWidget(self.ignore_tashkeel_checkbox)
        self.group_search_layout.addWidget(self.ignore_hamza_checkbox)
        self.group_search_layout.addWidget(self.match_whole_word_checkbox)
        self.group_search_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))  # Spacer item
        self.group_search.setLayout(self.group_search_layout)
        self.group_search.setVisible(False)
        taps_layout.addWidget(self.group_search, stretch=2)

        main_layout.addLayout(taps_layout)

        buttons_layout = QHBoxLayout()
        save_button = QPushButton("حفظ")
        save_button.clicked.connect(self.save_settings)
        save_button.setDefault(True)
        close_button = QPushButton("إغلاق")
        close_button.setShortcut(QKeySequence("Ctrl+W"))
        close_button.clicked.connect(self.close)

        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(close_button)

        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)

    def change_category(self, current, previous):
        if current is None:
            return
        if current.text() == "الإعدادات العامة":
            self.group_general.setVisible(True)
            self.group_audio.setVisible(False)
            self.group_search.setVisible(False)
        elif current.text == "الصوت":
            self.group_general.setVisible(False)
            self.group_audio.setVisible(True)
            self.group_search.setVisible(False)
        elif current.text() == "البحث":
            self.group_general.setVisible(False)
            self.group_audio.setVisible(False)
            self.group_search.setVisible(True)

    def save_settings(self):
        # Implement save settings logic here
        pass

    def set_current_settings(self):
        # Implement logic to set current settings here
        pass

    def OnReset(self):
        reply = QMessageBox.question(self, 'رسالة', "هل تريد استعادة الإعدادات الافتراضية؟", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.sound_checkbox.setChecked(False)
            self.speech_checkbox.setChecked(False)
            self.update_checkbox.setChecked(False)
            self.log_checkbox.setChecked(False)
            self.ignore_tashkeel_checkbox.setChecked(False)
            self.ignore_hamza_checkbox.setChecked(False)






    def change_category(self, current, previous):
        if current:
            if current.text() == "الإعدادات العامة":
                self.group_general.setVisible(True)
                self.group_audio.setVisible(False)
                self.group_search.setVisible(False)
            elif current.text() == "الصوت":
                self.group_general.setVisible(False)
                self.group_audio.setVisible(True)
                self.group_search.setVisible(False)
            elif current.text() == "البحث":
                self.group_general.setVisible(False)
                self.group_audio.setVisible(False)
                self.group_search.setVisible(True)

    def save_settings(self):

        # Collect general settings
        general_settings = {
            "run_in_background_enabled": self.run_in_background_checkbox.isChecked(),
            "auto_save_position_enabled": self.auto_save_position_checkbox.isChecked(),
            "check_update_enabled": self.update_checkbox.isChecked(),
            "logging_enabled": self.log_checkbox.isChecked()
        }


        # Collect audio settings
        audio_settings = {
            "sound_effect_enabled": self.sound_checkbox.isChecked(),
            "start_with_basmala_enabled": self.basmala_checkbox.isChecked(),
            "speak_actions_enabled": self.speech_checkbox.isChecked(),
            "volume_level": self.volume.value(),
            "athkar_volume_level": self.athkar_volume.value()
        }

    
        # Collect search settings
        search_settings = {
            "ignore_tashkeel": self.ignore_tashkeel_checkbox.isChecked(),
            "ignore_hamza": self.ignore_hamza_checkbox.isChecked(),
            "match_whole_word": self.match_whole_word_checkbox.isChecked()
        }

        # Update the current settings
        SettingsManager.write_settings({
            "general": general_settings,
            "audio": audio_settings,
            "search": search_settings
        })
        self.accept()

    def OnReset(self):

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("تحذير")
        msg_box.setText("هل أنت متأكد من إعادة تعيين الإعدادات إلى الإعدادات الافتراضية؟")
        msg_box.setIcon(QMessageBox.Icon.Warning)
        yes_button = msg_box.addButton("نعم", QMessageBox.ButtonRole.YesRole)
        no_button = msg_box.addButton("لا", QMessageBox.ButtonRole.NoRole)
        msg_box.exec()

        if msg_box.clickedButton() == yes_button:
            SettingsManager.reset_settings()
            self.set_current_settings()

    def set_current_settings(self):
        current_settings = SettingsManager.current_settings    
        self.sound_checkbox.setChecked(current_settings["audio"]["sound_effect_enabled"])
        self.basmala_checkbox.setChecked(current_settings["audio"]["start_with_basmala_enabled"])
        self.speech_checkbox.setChecked(current_settings["audio"]["speak_actions_enabled"])
        self.volume.setValue(current_settings["audio"]["volume_level"])
        self.athkar_volume.setValue(current_settings["audio"]["athkar_volume_level"])
        self.run_in_background_checkbox.setChecked(current_settings["general"]["run_in_background_enabled"])
        self.auto_save_position_checkbox.setChecked(current_settings["general"]["auto_save_position_enabled"])
        self.update_checkbox.setChecked(current_settings["general"]["check_update_enabled"])
        self.log_checkbox.setChecked(current_settings["general"]["logging_enabled"])
        self.ignore_tashkeel_checkbox.setChecked(current_settings["search"]["ignore_tashkeel"])
        self.ignore_hamza_checkbox.setChecked(current_settings["search"]["ignore_hamza"])
        self.match_whole_word_checkbox.setChecked(current_settings["search"]["match_whole_word"])
