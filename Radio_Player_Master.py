import sys
import webbrowser
import json
import os
import datetime

import vlc
from PyQt6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QSlider, QLCDNumber, QMessageBox, QDialog,
    QRadioButton, QHBoxLayout, QVBoxLayout, QSizePolicy
)
from PyQt6.QtGui import QFont, QKeySequence, QIcon
from PyQt6.QtCore import Qt, QSize, QTimer

class Radio(QWidget):
    def __init__(self):
        super().__init__()
        # Ensure native window decorations (min/max/close buttons) are enabled
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.Window)

        self._check_vlc_installation()

        # Set initial window size, will adapt due to layouts
        self.setGeometry(100, 100, 300, 360) 
        self.setStyleSheet('background-color: rgb(200, 150, 100)')
        self.setWindowTitle('Radio Player Master')

        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.player.audio_set_volume(50)

        # Connect to VLC's event manager to get metadata updates
        self.event_manager = self.player.event_manager()
        self.event_manager.event_attach(vlc.EventType.MediaPlayerMediaChanged, self.on_media_changed)
        self.event_manager.event_attach(vlc.EventType.MediaPlayerTitleChanged, self.on_title_changed)
        
        self.recorder_player = None
        self.is_recording = False
        self.recordings_folder = "Recordings" 
        
        if not os.path.exists(self.recordings_folder):
            os.makedirs(self.recordings_folder)

        self._load_radio_data()
        self._init_ui()
        

    def _check_vlc_installation(self):
        """Checks if VLC Python bindings can be imported. If not, prompts the user to install VLC Media Player."""
        try:
            import vlc
        except ImportError:
            msg = QMessageBox()
            msg.setWindowTitle('Warning!')
            msg.setText('To continue, you need to install VLC media player! Do you want to install this program?')
            msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            execute = msg.exec()

            if execute == QMessageBox.StandardButton.Yes:
                version_box = QDialog(self)
                version_box.setWindowTitle('Select Version')
                version_box.setGeometry(130, 150, 200, 90)

                self.win64_radio = QRadioButton("VLC media player win64", version_box)
                self.win64_radio.setChecked(True)
                self.win64_radio.move(5, 10)
                self.win32_radio = QRadioButton("VLC media player win32", version_box)
                self.win32_radio.move(5, 30)

                continue_button = QPushButton("Continue", version_box)
                continue_button.clicked.connect(self._open_vlc_download)
                continue_button.setGeometry(60, 60, 80, 20)
                version_box.exec()
            elif execute == QMessageBox.StandardButton.No:
                sys.exit()

    def _open_vlc_download(self):
        """Opens the VLC download page in a web browser based on the selected version."""
        if self.win64_radio.isChecked():
            try:
                webbrowser.open('https://mirror.rasanegar.com/videolan/vlc/3.0.16/win64/vlc-3.0.16-win64.exe')
            except Exception as e:
                QMessageBox.warning(self, 'Warning', f'Download failed! Please check your network connection.\nError: {e}')
        elif self.win32_radio.isChecked():
            try:
                webbrowser.open('https://mirror.rasanegar.com/videolan/vlc/3.0.16/win32/vlc-3.0.16-win32.exe')
            except Exception as e:
                QMessageBox.warning(self, 'Warning', f'Download failed! Please check your network connection.\nError: {e}')
        self.sender().parent().close()

    def _load_radio_data(self):
        """Loads radio names and links from a JSON file, or initializes them with defaults if not found or corrupted."""
        default_radio_names = ['Gooshkon Radio', 'Persian Radio']
        default_radio_links = ['https://r.gooshkon.ir:443/live.ogg', 'http://r.pgbu.ir:8000/live']
        self.radio_names = []
        self.radio_links = []
        
        self.db_file = 'radios.json'

        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.radio_names = data.get('names', default_radio_names)
                    self.radio_links = data.get('links', default_radio_links)
            except (json.JSONDecodeError, FileNotFoundError, Exception) as e:
                QMessageBox.warning(self, "Database Load Error", f"Error loading radios from '{self.db_file}': {e}. Re-initializing database.")
                self.radio_names = default_radio_names
                self.radio_links = default_radio_links
                self._save_radio_data()
        else:
            self.radio_names = default_radio_names
            self.radio_links = default_radio_links
            self._save_radio_data()

    def _save_radio_data(self):
        """Saves current radio names and links to the JSON file."""
        data_to_save = {
            'names': self.radio_names,
            'links': self.radio_links
        }
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=4, ensure_ascii=False)
        except Exception as e:
            QMessageBox.critical(self, "Database Save Error", f"Failed to save data to '{self.db_file}': {e}")

    def _init_ui(self):
        """Initializes the user interface elements and their layout."""
        radio_layout = QGridLayout()
        self.setLayout(radio_layout)

        self.lcd = QLCDNumber()
        self.lcd.setStyleSheet('background-color: rgb(60, 60, 60)')
        radio_layout.addWidget(self.lcd, 0, 0, 1, 3) 

        self.metadata_display = QLineEdit()
        self.metadata_display.setReadOnly(True)
        self.metadata_display.setFont(QFont('Arial', 10))
        self.metadata_display.setStyleSheet('background-color: rgb(60, 60, 60); color: white; padding: 5px;')
        self.metadata_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.metadata_display.setAccessibleName("Now Playing Information")
        self.metadata_display.hide()
        radio_layout.addWidget(self.metadata_display, 0, 0, 1, 3)

        navigation_and_volume_layout = QHBoxLayout()

        self.prev_button = QPushButton()
        self.prev_button.setShortcut(QKeySequence('Ctrl+Left'))
        self.prev_button.setIcon(QIcon('icons/prev.png'))
        self.prev_button.setIconSize(QSize(24, 24))
        self.prev_button.setStyleSheet('background-color: rgb(10, 10, 10);')
        self.prev_button.clicked.connect(self._go_to_previous_radio)
        self.prev_button.setAccessibleName('Previous Radio')
        navigation_and_volume_layout.addWidget(self.prev_button)

        self.radio_combo_box = QComboBox()
        self.radio_combo_box.setAccessibleName("Choose radio:")
        self.radio_combo_box.addItems(self.radio_names)
        self.radio_combo_box.activated.connect(self._on_radio_selected)
        self.radio_combo_box.setStyleSheet('background-color: rgb(10, 10, 10); color: white;')
        navigation_and_volume_layout.addWidget(self.radio_combo_box)

        self.next_button = QPushButton()
        self.next_button.setShortcut(QKeySequence('Ctrl+Right'))
        self.next_button.setIcon(QIcon('icons/next.png'))
        self.next_button.setIconSize(QSize(24, 24))
        self.next_button.setStyleSheet('background-color: rgb(10, 10, 10);')
        self.next_button.clicked.connect(self._go_to_next_radio)
        self.next_button.setAccessibleName('Next Radio')
        navigation_and_volume_layout.addWidget(self.next_button)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setAccessibleName('Volume control')
        self.volume_slider.setStyleSheet('background-color: rgb(10, 10, 10);')
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setSliderPosition(self.player.audio_get_volume())
        self.volume_slider.valueChanged.connect(self._set_volume)
        navigation_and_volume_layout.addWidget(self.volume_slider)

        radio_layout.addLayout(navigation_and_volume_layout, 1, 0, 1, 3)

        playback_controls_layout = QHBoxLayout()
        
        self.play_pause_button = QPushButton()
        self.play_pause_button.setShortcut(QKeySequence('Ctrl+P'))
        self.play_pause_button.setIcon(QIcon('icons/play.png'))
        self.play_pause_button.setIconSize(QSize(24, 24))
        self.play_pause_button.setStyleSheet('background-color: rgb(46, 200, 87);')
        self.play_pause_button.clicked.connect(self._toggle_play_pause)
        self.play_pause_button.setAccessibleName('Play/Pause')
        playback_controls_layout.addWidget(self.play_pause_button)

        self.stop_button = QPushButton()
        self.stop_button.setShortcut(QKeySequence('Ctrl+S'))
        self.stop_button.setIcon(QIcon('icons/stop.png'))
        self.stop_button.setIconSize(QSize(24, 24))
        self.stop_button.setStyleSheet('background-color: rgb(200, 87, 46);')
        self.stop_button.clicked.connect(self.stop_player)
        self.stop_button.setAccessibleName('Stop')
        playback_controls_layout.addWidget(self.stop_button)

        self.record_button = QPushButton()
        self.record_button.setShortcut(QKeySequence('Ctrl+R'))
        self.record_button.setIcon(QIcon('icons/record.png'))
        self.record_button.setIconSize(QSize(24, 24))
        self.record_button.setStyleSheet('background-color: rgb(170, 0, 0);')
        self.record_button.clicked.connect(self._toggle_record)
        self.record_button.setAccessibleName('Record')
        playback_controls_layout.addWidget(self.record_button)
        
        radio_layout.addLayout(playback_controls_layout, 2, 0, 1, 2)

        self.link_input = QLineEdit()
        self.link_input.setAccessibleName('Enter Link For Play')
        self.link_input.setPlaceholderText("Enter Direct Link")
        self.link_input.setStyleSheet('background-color: rgb(10, 10, 10); color: white;')
        radio_layout.addWidget(self.link_input, 2, 2, 1, 1)

        management_buttons_layout = QHBoxLayout()
        
        self.delete_btn = QPushButton()
        self.delete_btn.setText('Delete Radio')
        self.delete_btn.setAccessibleName('Delete Radio')
        self.delete_btn.setIcon(QIcon('icons/delete.png'))
        self.delete_btn.setIconSize(QSize(24, 24))
        self.delete_btn.clicked.connect(self._delete_radio)
        self.delete_btn.setShortcut(QKeySequence('Ctrl+D'))
        self.delete_btn.setStyleSheet('background-color: rgb(10, 10, 10); color: white;')
        management_buttons_layout.addWidget(self.delete_btn)

        add_btn = QPushButton()
        add_btn.setText('Add Radio')
        add_btn.setAccessibleName('Add New Radio')
        add_btn.setIcon(QIcon('icons/add.png'))
        add_btn.setIconSize(QSize(24, 24))
        add_btn.clicked.connect(self._show_add_radio_dialog)
        add_btn.setShortcut(QKeySequence('Ctrl+A'))
        add_btn.setStyleSheet('background-color: rgb(10, 10, 10); color: white;')
        management_buttons_layout.addWidget(add_btn)

        radio_layout.addLayout(management_buttons_layout, 3, 1, 1, 2)

        radio_layout.setColumnStretch(0, 1)
        radio_layout.setColumnStretch(1, 1)
        radio_layout.setColumnStretch(2, 1)
        
        radio_layout.setRowStretch(0, 3)
        radio_layout.setRowStretch(1, 1)
        radio_layout.setRowStretch(2, 1)
        radio_layout.setRowStretch(3, 1)

        if self.radio_names:
            self._on_radio_selected(play_on_select=False) 
        else:
            self.lcd.hide()
            self.metadata_display.show()
            self.metadata_display.setText("   No radios found. Add a new one!")

    def on_media_changed(self, event):
        """Handle VLC media change event. Triggered when a new stream is loaded."""
        # This will show 'Playing: Radio Name' until metadata is available
        self.metadata_display.show()
        self.metadata_display.setText(f"   Playing: {self.selected_radio_name}")
        self.lcd.hide()

    def on_title_changed(self, event):
        """Handle VLC title change event and update the display."""
        title = self.player.get_media().get_meta(vlc.Meta.Title)
        if title:
            artist = self.player.get_media().get_meta(vlc.Meta.Artist)
            if artist:
                self.metadata_display.setText(f"   Now Playing: {title} - {artist}")
            else:
                self.metadata_display.setText(f"   Now Playing: {title}")
        else:
            # If title is no longer available, revert to showing the radio name
            self.metadata_display.setText(f"   Playing: {self.selected_radio_name}")

    def _go_to_next_radio(self):
        """Navigates to the next radio in the list and plays it automatically."""
        if not self.radio_names:
            QMessageBox.information(self, "Navigation", "No radio stations to navigate.")
            return
        current_index = self.radio_combo_box.currentIndex()
        next_index = (current_index + 1) % len(self.radio_names)
        self.radio_combo_box.setCurrentIndex(next_index)
        self._on_radio_selected(play_on_select=True)

    def _go_to_previous_radio(self):
        """Navigates to the previous radio in the list and plays it automatically."""
        if not self.radio_names:
            QMessageBox.information(self, "Navigation", "No radio stations to navigate.")
            return
        current_index = self.radio_combo_box.currentIndex()
        prev_index = (current_index - 1 + len(self.radio_names)) % len(self.radio_names)
        self.radio_combo_box.setCurrentIndex(prev_index)
        self._on_radio_selected(play_on_select=True)

    def _show_add_radio_dialog(self):
        """Displays a dialog to allow the user to add a new radio station."""
        self.stop_player()
        self._stop_recording()

        self.add_dialog = QDialog(self)
        self.add_dialog.setWindowTitle('Add New Radio')
        self.add_dialog.setGeometry(130, 250, 250, 120)

        dialog_layout = QVBoxLayout()
        self.add_dialog.setLayout(dialog_layout)

        name_layout = QHBoxLayout()
        radio_name_label = QLabel('Radio Name:')
        self.new_radio_name_input = QLineEdit()
        self.new_radio_name_input.setPlaceholderText('Enter Radio Name')
        if self.radio_names:
            self.new_radio_name_input.setText(self.selected_radio_name)
        name_layout.addWidget(radio_name_label)
        name_layout.addWidget(self.new_radio_name_input)
        dialog_layout.addLayout(name_layout)

        link_layout = QHBoxLayout()
        link_label = QLabel('Radio Link:')
        self.new_radio_link_input = QLineEdit()
        self.new_radio_link_input.setPlaceholderText('Enter Radio Link (URL)')
        link_layout.addWidget(link_label)
        link_layout.addWidget(self.new_radio_link_input)
        dialog_layout.addLayout(link_layout)

        button_layout = QHBoxLayout()
        add_button = QPushButton("Add")
        add_button.clicked.connect(self._add_or_update_radio)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.add_dialog.reject)
        button_layout.addWidget(add_button)
        button_layout.addWidget(cancel_button)
        dialog_layout.addLayout(button_layout)

        self.add_dialog.exec()

    def _add_or_update_radio(self):
        """Adds a new radio or updates an existing one based on user input."""
        new_name = self.new_radio_name_input.text().strip()
        new_link = self.new_radio_link_input.text().strip()

        if not new_name:
            QMessageBox.warning(self, "Input Error", "Radio name must be provided.")
            return
        if not new_link:
            QMessageBox.warning(self, "Input Error", "Radio link must be provided.")
            return
        
        if not (new_link.startswith("http://") or new_link.startswith("https://")):
            QMessageBox.warning(self, "Input Error", "Radio link must be a valid URL starting with http:// or https://")
            return

        if new_name == self.selected_radio_name and new_name in self.radio_names:
            try:
                index_to_update = self.radio_names.index(new_name)
                self.radio_links[index_to_update] = new_link
                self._save_radio_data()
                QMessageBox.information(self, "Success", f"Link for '{new_name}' updated successfully.")
                self.add_dialog.accept()
                self._refresh_radio_list_and_selection(new_name)
                return
            except ValueError:
                QMessageBox.critical(self, "Error", "Selected radio not found during update (this shouldn't happen).")
                self.add_dialog.reject()
                return

        if new_name in self.radio_names:
            QMessageBox.warning(self, "Input Error", "A radio with this name already exists. Please choose a different name.")
            return

        self.radio_names.append(new_name)
        self.radio_links.append(new_link)
        self._save_radio_data()
        QMessageBox.information(self, "Success", f"'{new_name}' added successfully.")
        self.add_dialog.accept()
        self._refresh_radio_list_and_selection(new_name)

    def _refresh_radio_list_and_selection(self, selected_name):
        """Refreshes the combo box items and sets the selection based on the given name."""
        self.radio_combo_box.clear()
        self.radio_combo_box.addItems(self.radio_names)

        if selected_name in self.radio_names:
            self.radio_combo_box.setCurrentText(selected_name)
        else:
            if self.radio_names:
                self.radio_combo_box.setCurrentIndex(0)
            else:
                self.lcd.hide()
                self.metadata_display.show()
                self.metadata_display.setText("   No radios found. Add a new one!")
                self.current_link = ""
        self._on_radio_selected(play_on_select=False)

    def _on_radio_selected(self, play_on_select=False):
        """Updates the display and prepares the VLC player when a radio is selected from the ComboBox."""
        if not self.radio_names:
            self.selected_radio_name = ""
            self.selected_radio_index = -1
            self.lcd.hide()
            self.metadata_display.show()
            self.metadata_display.setText("   No radios available. Add a new one!")
            self.stop_player()
            self._stop_recording()
            return

        self.selected_radio_name = self.radio_combo_box.currentText()
        self.selected_radio_index = self.radio_combo_box.currentIndex()

        self.lcd.setNumDigits(len(str(self.selected_radio_index + 1)))
        self.lcd.display(self.selected_radio_index + 1)
        
        # New: Show radio name by default, will be overwritten by metadata
        self.metadata_display.show()
        self.metadata_display.setText(f"   Playing: {self.selected_radio_name}")
        self.lcd.hide()

        try:
            link_index = self.radio_names.index(self.selected_radio_name)
            self.current_link = self.radio_links[link_index]
            media = self.instance.media_new(self.current_link)
            self.player.set_media(media)
            self.player.audio_set_mute(0)
            
            if play_on_select:
                self.player.play()
                self.play_pause_button.setIcon(QIcon('icons/pause.png'))
                self.play_pause_button.setStyleSheet('background-color: rgb(255, 165, 0);')

        except ValueError:
            QMessageBox.critical(self, "Error", "Selected radio not found in internal list. Please check data integrity.")
            self.current_link = ""
            self.stop_player()
            self._stop_recording()
        except Exception as e:
            QMessageBox.critical(self, "VLC Error", f"Failed to prepare media: {e}")
            self.current_link = ""
            self.stop_player()
            self._stop_recording()

        if not play_on_select:
            self.play_pause_button.setIcon(QIcon('icons/play.png'))
            self.play_pause_button.setStyleSheet('background-color: rgb(46, 200, 87);')
            self.play_pause_button.setShortcut(QKeySequence('Ctrl+P'))

    def _toggle_play_pause(self):
        """Toggles between playing and pausing the radio based on the button text."""
        direct_link = self.link_input.text().strip()

        if self.player.is_playing():
            self.player.pause()
            self.play_pause_button.setIcon(QIcon('icons/play.png'))
            self.play_pause_button.setStyleSheet('background-color: rgb(46, 200, 87);')
            self.metadata_display.setText(f"   Paused: {self.selected_radio_name or direct_link}")
        else:
            self.play_pause_button.setIcon(QIcon('icons/pause.png'))
            self.play_pause_button.setStyleSheet('background-color: rgb(255, 165, 0);')

            if direct_link:
                try:
                    media = self.instance.media_new(direct_link)
                    self.player.set_media(media)
                    self.player.play()
                    self.metadata_display.setText(f"   Playing: {direct_link}")
                except Exception as e:
                    QMessageBox.warning(self, "Playback Error", f"Could not play direct link: {e}\nPlease check the link format or network connection.")
                    self.stop_player()
            else:
                if not self.radio_names or not self.current_link:
                    QMessageBox.warning(self, "Selection Error", "No radio stations available or selected.")
                    self.play_pause_button.setIcon(QIcon('icons/play.png'))
                    self.play_pause_button.setStyleSheet('background-color: rgb(46, 200, 87);')
                    return
                try:
                    self.player.play()
                except Exception as e:
                    QMessageBox.warning(self, "Playback Error", f"Could not play selected radio: {e}\nPlease check network connection.")
                    self.stop_player()
                    self.play_pause_button.setIcon(QIcon('icons/play.png'))
                    self.play_pause_button.setStyleSheet('background-color: rgb(46, 200, 87);')

            self.player.audio_set_mute(0)

    def stop_player(self):
        """Stops the VLC media player completely and resets the Play/Pause button state."""
        self.player.stop()
        self.play_pause_button.setIcon(QIcon('icons/play.png'))
        self.play_pause_button.setStyleSheet('background-color: rgb(46, 200, 87);')
        self.play_pause_button.setShortcut(QKeySequence('Ctrl+P'))
        self.metadata_display.hide()
        self.lcd.show()
        if self.link_input.text().strip():
            self.link_input.clear()
        self._stop_recording()

    def _toggle_record(self):
        """Toggles recording of the current stream."""
        if not self.player.is_playing() and not self.recorder_player:
            QMessageBox.warning(self, "Recording Error", "Please play a radio station or direct link before recording.")
            return

        if not self.is_recording:
            stream_link = self.link_input.text().strip() if self.link_input.text().strip() else self.current_link

            if not stream_link:
                QMessageBox.warning(self, "Recording Error", "No stream link available to record.")
                return

            now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name_base = "".join(c for c in self.selected_radio_name if c.isalnum() or c in (' ', '_')).strip()
            if not file_name_base:
                file_name_base = "DirectStream" if self.link_input.text().strip() else "Radio"
            file_name_base = file_name_base.replace(" ", "_")
            file_name = f"{file_name_base}_{now}.mp3"
            file_path = os.path.join(self.recordings_folder, file_name)

            record_options = f":sout=#transcode{{vcodec=none,acodec=mp3,ab=128,channels=2,samplerate=44100}}:std{{access=file,mux=mp3,dst='{file_path}'}}"

            try:
                record_media = self.instance.media_new(stream_link, record_options)
                self.recorder_player = self.instance.media_player_new()
                self.recorder_player.set_media(record_media)
                self.recorder_player.play()
                
                self.is_recording = True
                self.record_button.setText('Stop Recording')
                self.record_button.setIcon(QIcon('icons/record_active.png'))
                self.record_button.setStyleSheet('background-color: rgb(0, 100, 0); color: white;')
                self.metadata_display.show()
                self.metadata_display.setText(f"   Recording to: {file_name}")
                self.lcd.hide()

            except Exception as e:
                QMessageBox.critical(self, "Recording Error", f"Failed to start recording: {e}\nEnsure VLC is properly configured and the path '{self.recordings_folder}' is writable.")
                self._stop_recording()
        else:
            self._stop_recording()
            QMessageBox.information(self, "Recording Complete", f"Recording saved to '{self.recordings_folder}' folder.")

    def _stop_recording(self):
        """Stops the recording player if it's active and resets UI elements related to recording."""
        if self.is_recording and self.recorder_player:
            self.recorder_player.stop()
            self.recorder_player = None
            self.is_recording = False
            self.record_button.setText('Record')
            self.record_button.setIcon(QIcon('icons/record.png'))
            self.record_button.setStyleSheet('background-color: rgb(170, 0, 0);')
            if not self.player.is_playing():
                self.metadata_display.hide()
                self.lcd.show()

    def _set_volume(self, value):
        """Sets the volume of the VLC media player based on the slider value."""
        self.player.audio_set_volume(value)

    def _delete_radio(self):
        """Deletes the currently selected radio station from the lists and database."""
        self.stop_player()
        self._stop_recording()

        if not self.radio_names:
            QMessageBox.warning(self, "Warning!", "No radio stations to delete.")
            return

        if self.selected_radio_name in ['Gooshkon Radio', 'Persian Radio']:
            QMessageBox.warning(self, "Warning!", f"You cannot delete {self.selected_radio_name}.")
            return

        msg = QMessageBox()
        msg.setWindowTitle('Warning!')
        msg.setText(f'Do you really want to delete {self.selected_radio_name}?')
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        execute = msg.exec()

        if execute == QMessageBox.StandardButton.Yes:
            try:
                index_to_delete = self.radio_names.index(self.selected_radio_name)
                self.radio_names.pop(index_to_delete)
                self.radio_links.pop(index_to_delete)
                self._save_radio_data()

                next_selected_name = None
                if self.radio_names:
                    if index_to_delete < len(self.radio_names):
                        next_selected_name = self.radio_names[index_to_delete]
                    else:
                        next_selected_name = self.radio_names[0]
                
                self._refresh_radio_list_and_selection(next_selected_name)
                QMessageBox.information(self, "Success", f"'{self.selected_radio_name}' deleted successfully.")

            except ValueError:
                QMessageBox.critical(self, "Error", "Selected radio not found in list (this shouldn't happen).")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An unexpected error occurred during deletion: {e}")

# Main application entry point
if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Radio()
    w.show()
    sys.exit(app.exec())