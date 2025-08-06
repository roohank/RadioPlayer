import sys
import webbrowser
import json
import os
import datetime

import vlc
from PyQt6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QSlider, QLCDNumber, QMessageBox, QDialog,
    QRadioButton, QHBoxLayout, QVBoxLayout, QSizePolicy, QListWidget, QListWidgetItem
)
from PyQt6.QtGui import QFont, QKeySequence, QIcon
from PyQt6.QtCore import Qt, QSize, QTimer

class Radio(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.Window)

        self.vlc_options = "--network-caching=0"
        self._check_vlc_installation()

        self.setGeometry(100, 100, 600, 360)
        self.setStyleSheet('background-color: rgb(200, 150, 100)')
        self.setWindowTitle('Radio Player Master')

        self.instance = vlc.Instance(self.vlc_options)
        self.player = self.instance.media_player_new()
        self.player.audio_set_volume(50)

        self.metadata_timer = QTimer(self)
        self.metadata_timer.setInterval(1000)
        self.metadata_timer.timeout.connect(self._check_and_update_metadata)
        self.last_metadata = ""

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
                version_box.setGeometry(130, 250, 200, 90)

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
        """Initializes the user interface elements and their layout with a new two-column design."""
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # Left side: QListWidget and management buttons
        left_layout = QVBoxLayout()
        self.radio_list_widget = QListWidget()
        self.radio_list_widget.setStyleSheet('background-color: rgb(10, 10, 10); color: white; border: 1px solid gray;')
        self.radio_list_widget.addItems(self.radio_names)
        self.radio_list_widget.itemClicked.connect(self._on_list_item_clicked)
        self.radio_list_widget.itemDoubleClicked.connect(self._on_list_item_double_clicked)
        self.radio_list_widget.setAccessibleName("Radio Stations List")

        # Connect Enter key press event to the ListWidget
        self.radio_list_widget.keyPressEvent = self._list_widget_key_press_event
        left_layout.addWidget(self.radio_list_widget)

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

        # New: Next/Previous buttons for list navigation
        self.prev_radio_button = QPushButton('<< Prev')
        self.prev_radio_button.setAccessibleName('Previous Radio Station')
        self.prev_radio_button.clicked.connect(self._go_to_previous_radio)
        self.next_radio_button = QPushButton('Next >>')
        self.next_radio_button.setAccessibleName('Next Radio Station')
        self.next_radio_button.clicked.connect(self._go_to_next_radio)
        
        management_buttons_layout.addWidget(self.prev_radio_button)
        management_buttons_layout.addWidget(self.next_radio_button)
        
        left_layout.addLayout(management_buttons_layout)
        
        main_layout.addLayout(left_layout)

        # Right side: Main player controls
        right_layout = QVBoxLayout()

        display_container = QWidget()
        display_layout = QVBoxLayout()
        display_container.setLayout(display_layout)
        display_layout.setContentsMargins(0, 0, 0, 0)
        display_layout.setSpacing(0)

        self.lcd = QLCDNumber()
        self.lcd.setStyleSheet('background-color: rgb(60, 60, 60); border: none;')
        display_layout.addWidget(self.lcd)

        self.metadata_display = QLabel()
        self.metadata_display.setFont(QFont('Arial', 10, QFont.Weight.Bold))
        self.metadata_display.setStyleSheet('background-color: rgb(60, 60, 60); color: white; padding: 5px; border: none;')
        self.metadata_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.metadata_display.setWordWrap(True)
        self.metadata_display.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.metadata_display.hide()
        display_layout.addWidget(self.metadata_display)
        right_layout.addWidget(display_container)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setAccessibleName('Volume control')
        self.volume_slider.setStyleSheet('background-color: rgb(10, 10, 10);')
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setSliderPosition(self.player.audio_get_volume())
        self.volume_slider.valueChanged.connect(self._set_volume)
        right_layout.addWidget(self.volume_slider)

        playback_and_seek_layout = QHBoxLayout()
        
        self.rewind_button = QPushButton()
        self.rewind_button.setShortcut(QKeySequence('Left'))
        self.rewind_button.setIcon(QIcon('icons/rewind.png'))
        self.rewind_button.setIconSize(QSize(24, 24))
        self.rewind_button.setStyleSheet('background-color: rgb(10, 10, 10);')
        self.rewind_button.clicked.connect(self._go_backward)
        self.rewind_button.setAccessibleName('Go Backward')
        playback_and_seek_layout.addWidget(self.rewind_button)

        self.play_pause_button = QPushButton()
        self.play_pause_button.setShortcut(QKeySequence('Ctrl+P'))
        self.play_pause_button.setIcon(QIcon('icons/play.png'))
        self.play_pause_button.setIconSize(QSize(24, 24))
        self.play_pause_button.setStyleSheet('background-color: rgb(46, 200, 87);')
        self.play_pause_button.clicked.connect(self._toggle_play_pause)
        self.play_pause_button.setAccessibleName('Play/Pause')
        playback_and_seek_layout.addWidget(self.play_pause_button)
        
        self.stop_button = QPushButton()
        self.stop_button.setShortcut(QKeySequence('Ctrl+S'))
        self.stop_button.setIcon(QIcon('icons/stop.png'))
        self.stop_button.setIconSize(QSize(24, 24))
        self.stop_button.setStyleSheet('background-color: rgb(200, 87, 46);')
        self.stop_button.clicked.connect(self.stop_player)
        self.stop_button.setAccessibleName('Stop')
        playback_and_seek_layout.addWidget(self.stop_button)

        self.forward_button = QPushButton()
        self.forward_button.setShortcut(QKeySequence('Right'))
        self.forward_button.setIcon(QIcon('icons/forward.png'))
        self.forward_button.setIconSize(QSize(24, 24))
        self.forward_button.setStyleSheet('background-color: rgb(10, 10, 10);')
        self.forward_button.clicked.connect(self._go_forward)
        self.forward_button.setAccessibleName('Go Forward')
        playback_and_seek_layout.addWidget(self.forward_button)

        self.record_button = QPushButton()
        self.record_button.setShortcut(QKeySequence('Ctrl+R'))
        self.record_button.setIcon(QIcon('icons/record.png'))
        self.record_button.setIconSize(QSize(24, 24))
        self.record_button.setStyleSheet('background-color: rgb(170, 0, 0);')
        self.record_button.clicked.connect(self._toggle_record)
        self.record_button.setAccessibleName('Record')
        playback_and_seek_layout.addWidget(self.record_button)
        
        right_layout.addLayout(playback_and_seek_layout)

        self.link_input = QLineEdit()
        self.link_input.setAccessibleName('Enter Link For Play')
        self.link_input.setPlaceholderText("Enter Direct Link")
        self.link_input.setStyleSheet('background-color: rgb(10, 10, 10); color: white;')
        right_layout.addWidget(self.link_input)
        
        main_layout.addLayout(right_layout)

        if self.radio_names:
            self.radio_list_widget.setCurrentRow(0)
            self._on_list_item_changed(0)
        else:
            self.lcd.hide()
            self.metadata_display.show()
            self.metadata_display.setText("   No radios found. Add a new one!")
            self.metadata_display.setAccessibleName("   No radios found. Add a new one!")

    def _list_widget_key_press_event(self, event):
        """Custom key press event handler for the list widget."""
        if event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return):
            current_row = self.radio_list_widget.currentRow()
            if current_row >= 0:
                self._on_list_item_double_clicked(self.radio_list_widget.currentItem())
        else:
            QListWidget.keyPressEvent(self.radio_list_widget, event)
            # When an item is selected by keyboard, just change the metadata display
            current_row = self.radio_list_widget.currentRow()
            if current_row >= 0:
                self.selected_radio_name = self.radio_names[current_row]
                self.metadata_display.setText(self.selected_radio_name)
                self.metadata_display.setAccessibleName(self.selected_radio_name)

    def _on_list_item_double_clicked(self, item):
        """Handle double-click event on a list item to start playback."""
        row = self.radio_list_widget.row(item)
        self._on_list_item_changed(row, play_on_select=True)
    
    def _on_list_item_clicked(self, item):
        """Handle single-click event on a list item to select it without playing."""
        row = self.radio_list_widget.row(item)
        self._on_list_item_changed(row, play_on_select=False)
        
    def _on_list_item_changed(self, row, play_on_select=False):
        """Updates the display and prepares the VLC player based on the list selection."""
        if row < 0 or row >= len(self.radio_names):
            return

        self.selected_radio_name = self.radio_names[row]
        self.selected_radio_index = row

        self.lcd.setNumDigits(len(str(self.selected_radio_index + 1)))
        self.lcd.display(self.selected_radio_index + 1)
        
        self.metadata_display.setText(self.selected_radio_name)
        self.metadata_display.setAccessibleName(self.selected_radio_name)
        self.metadata_display.show()
        self.lcd.hide()

        self.metadata_timer.stop()
        self.last_metadata = ""

        try:
            self.current_link = self.radio_links[row]
            media = self.instance.media_new(self.current_link)
            self.player.set_media(media)
            self.player.audio_set_mute(0)
            
            if play_on_select:
                self.player.play()
                self.play_pause_button.setIcon(QIcon('icons/pause.png'))
                self.play_pause_button.setStyleSheet('background-color: rgb(255, 165, 0);')
                self.metadata_timer.start()

        except Exception as e:
            QMessageBox.critical(self, "VLC Error", f"Failed to prepare media: {e}")
            self.current_link = ""
            self.stop_player()
            self._stop_recording()

        if not play_on_select:
            self.play_pause_button.setIcon(QIcon('icons/play.png'))
            self.play_pause_button.setStyleSheet('background-color: rgb(46, 200, 87);')

    def _check_and_update_metadata(self):
        """Checks for new metadata and updates the display if it has changed."""
        media = self.player.get_media()
        if not media:
            return

        title = media.get_meta(vlc.Meta.Title)
        artist = media.get_meta(vlc.Meta.Artist)

        current_metadata_text = self.selected_radio_name
        if title:
            current_metadata_text += f" - {title}"
            if artist:
                current_metadata_text += f" ({artist})"
        
        if self.last_metadata != current_metadata_text:
            self.metadata_display.setText(current_metadata_text)
            self.last_metadata = current_metadata_text
            self.metadata_display.show()
            self.metadata_display.setAccessibleName(current_metadata_text)
            self.lcd.hide()

    def _go_to_previous_radio(self):
        """Navigates to the previous radio in the list and plays it automatically."""
        if not self.radio_names:
            QMessageBox.information(self, "Navigation", "No radio stations to navigate.")
            return
        current_index = self.radio_list_widget.currentRow()
        prev_index = (current_index - 1 + len(self.radio_names)) % len(self.radio_names)
        self.radio_list_widget.setCurrentRow(prev_index)
        self.play_pause_button.clicked.emit()

    def _go_to_next_radio(self):
        """Navigates to the next radio in the list and plays it automatically."""
        if not self.radio_names:
            QMessageBox.information(self, "Navigation", "No radio stations to navigate.")
            return
        current_index = self.radio_list_widget.currentRow()
        next_index = (current_index + 1) % len(self.radio_names)
        self.radio_list_widget.setCurrentRow(next_index)
        self.play_pause_button.clicked.emit()

    def _go_backward(self):
        """Goes backward in the stream by 10 seconds."""
        if self.player.is_playing() and self.player.is_seekable():
            current_time = self.player.get_time()
            self.player.set_time(current_time - 10000)

    def _go_forward(self):
        """Goes forward in the stream by 10 seconds."""
        if self.player.is_playing() and self.player.is_seekable():
            current_time = self.player.get_time()
            self.player.set_time(current_time + 10000)

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
        if self.radio_list_widget.currentRow() >= 0:
            self.new_radio_name_input.setText(self.radio_list_widget.currentItem().text())
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

        selected_item_text = self.radio_list_widget.currentItem().text() if self.radio_list_widget.currentItem() else ""
        if new_name == selected_item_text and new_name in self.radio_names:
            try:
                index_to_update = self.radio_names.index(new_name)
                self.radio_links[index_to_update] = new_link
                self._save_radio_data()
                QMessageBox.information(self, "Success", f"Link for '{new_name}' updated successfully.")
                self.add_dialog.accept()
                self._refresh_radio_list(new_name)
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
        self._refresh_radio_list(new_name)

    def _refresh_radio_list(self, selected_name):
        """Refreshes the list widget items and sets the selection based on the given name."""
        self.radio_list_widget.clear()
        self.radio_list_widget.addItems(self.radio_names)
        
        if selected_name in self.radio_names:
            index = self.radio_names.index(selected_name)
            self.radio_list_widget.setCurrentRow(index)
        else:
            if self.radio_names:
                self.radio_list_widget.setCurrentRow(0)
            else:
                self.metadata_display.setText("   No radios found. Add a new one!")
                self.metadata_display.setAccessibleName("   No radios found. Add a new one!")
                self.stop_player()

    def _on_radio_selected(self, play_on_select=False):
        """Updates the display and prepares the VLC player when a radio is selected from the list."""
        if not self.radio_names:
            self.selected_radio_name = ""
            self.selected_radio_index = -1
            self.lcd.hide()
            self.metadata_display.show()
            self.metadata_display.setText("   No radios available. Add a new one!")
            self.metadata_display.setAccessibleName("   No radios available. Add a new one!")
            self.stop_player()
            self._stop_recording()
            return

        current_row = self.radio_list_widget.currentRow()
        if current_row < 0:
            return

        self.selected_radio_name = self.radio_names[current_row]
        self.selected_radio_index = current_row

        self.lcd.setNumDigits(len(str(self.selected_radio_index + 1)))
        self.lcd.display(self.selected_radio_index + 1)
        self.metadata_display.setText(self.selected_radio_name)
        self.metadata_display.setAccessibleName(self.selected_radio_name)
        self.metadata_display.show()
        self.lcd.hide()

        self.metadata_timer.stop()
        self.last_metadata = ""

        try:
            self.current_link = self.radio_links[current_row]
            media = self.instance.media_new(self.current_link)
            self.player.set_media(media)
            self.player.audio_set_mute(0)
            
            if play_on_select:
                self.player.play()
                self.play_pause_button.setIcon(QIcon('icons/pause.png'))
                self.play_pause_button.setStyleSheet('background-color: rgb(255, 165, 0);')
                self.metadata_timer.start()

        except Exception as e:
            QMessageBox.critical(self, "VLC Error", f"Failed to prepare media: {e}")
            self.current_link = ""
            self.stop_player()
            self._stop_recording()

        if not play_on_select:
            self.play_pause_button.setIcon(QIcon('icons/play.png'))
            self.play_pause_button.setStyleSheet('background-color: rgb(46, 200, 87);')

    def _toggle_play_pause(self):
        """Toggles between playing and pausing the radio."""
        direct_link = self.link_input.text().strip()

        if self.player.is_playing():
            self.player.pause()
            self.play_pause_button.setIcon(QIcon('icons/play.png'))
            self.play_pause_button.setStyleSheet('background-color: rgb(46, 200, 87);')
            
            paused_text = f"Paused: {self.selected_radio_name or direct_link}"
            self.metadata_display.setText(paused_text)
            self.metadata_display.setAccessibleName(paused_text)
            
            self.metadata_timer.stop()
        else:
            self.play_pause_button.setIcon(QIcon('icons/pause.png'))
            self.play_pause_button.setStyleSheet('background-color: rgb(255, 165, 0);')

            if direct_link:
                try:
                    media = self.instance.media_new(direct_link)
                    self.player.set_media(media)
                    self.player.play()
                    
                    playing_text = f"Playing: {direct_link}"
                    self.metadata_display.setText(playing_text)
                    self.metadata_display.setAccessibleName(playing_text)
                    self.metadata_timer.start()
                    self.link_input.clear()
                except Exception as e:
                    QMessageBox.warning(self, "Playback Error", f"Could not play direct link: {e}\nPlease check the link format or network connection.")
                    self.stop_player()
            else:
                if not self.radio_names or self.radio_list_widget.currentRow() < 0:
                    QMessageBox.warning(self, "Selection Error", "No radio stations available or selected.")
                    self.play_pause_button.setIcon(QIcon('icons/play.png'))
                    self.play_pause_button.setStyleSheet('background-color: rgb(46, 200, 87);')
                    return
                try:
                    self._on_radio_selected(play_on_select=True)
                except Exception as e:
                    QMessageBox.warning(self, "Playback Error", f"Could not play selected radio: {e}\nPlease check network connection.")
                    self.stop_player()
                    self.play_pause_button.setIcon(QIcon('icons/play.png'))
                    self.play_pause_button.setStyleSheet('background-color: rgb(46, 200, 87);')

            self.player.audio_set_mute(0)

    def stop_player(self):
        """Stops the VLC media player completely and resets the Play/Pause button state.
        Also stops any active recording.
        """
        self.metadata_timer.stop()
        QTimer.singleShot(100, self._perform_stop_actions)

    def _perform_stop_actions(self):
        """Helper method to perform stop actions after a brief delay."""
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
                self.metadata_display.setAccessibleName(f"   Recording to: {file_name}")
                self.lcd.hide()
                self.metadata_timer.stop()

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
            if self.player.is_playing():
                self.metadata_timer.start()
            else:
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

        selected_name = self.radio_list_widget.currentItem().text()
        if selected_name in ['Gooshkon Radio', 'Persian Radio']:
            QMessageBox.warning(self, "Warning!", f"You cannot delete {selected_name}.")
            return

        msg = QMessageBox()
        msg.setWindowTitle('Warning!')
        msg.setText(f'Do you really want to delete {selected_name}?')
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        execute = msg.exec()

        if execute == QMessageBox.StandardButton.Yes:
            try:
                index_to_delete = self.radio_names.index(selected_name)
                self.radio_names.pop(index_to_delete)
                self.radio_links.pop(index_to_delete)
                self._save_radio_data()

                next_selected_name = None
                if self.radio_names:
                    if index_to_delete < len(self.radio_names):
                        next_selected_name = self.radio_names[index_to_delete]
                    else:
                        next_selected_name = self.radio_names[0]
                
                self._refresh_radio_list(next_selected_name)
                QMessageBox.information(self, "Success", f"'{selected_name}' deleted successfully.")

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