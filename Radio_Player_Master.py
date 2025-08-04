import sys
import webbrowser
import json
import os

import vlc
from PyQt6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QSlider, QLCDNumber, QMessageBox, QDialog,
    QRadioButton
)
from PyQt6.QtGui import QFont, QKeySequence

class Radio(QWidget):
    def __init__(self):
        super().__init__()
        self._check_vlc_installation()

        self.setGeometry(100, 100, 260, 320)
        self.setStyleSheet('background-color: rgb(200, 150, 100)')
        self.setWindowTitle('Radio Player Master')

        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.player.audio_set_volume(50)

        self._load_radio_data()
        self._init_ui()

    def _check_vlc_installation(self):
        """Checks if VLC is installed and prompts for installation if not."""
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
        """Opens the VLC download page based on selected version."""
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
        default_radio_links = ['http://r.gooshkon.ir:8000/live.ogg', 'http://r.pgbu.ir:8000/live']
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
        self.lcd.setGeometry(5, 10, 250, 140)
        self.lcd.setStyleSheet('background-color: rgb(60, 60, 60)')
        radio_layout.addWidget(self.lcd, 0, 0, 1, 3)

        self.info_display = QLineEdit()
        self.info_display.setGeometry(5, 10, 250, 140)
        self.info_display.setFont(QFont('Arial', 10))
        self.info_display.setStyleSheet('background-color: rgb(60, 60, 60)')
        self.info_display.setReadOnly(True)
        self.info_display.hide()
        radio_layout.addWidget(self.info_display, 0, 0, 1, 3)

        self.radio_combo_box = QComboBox()
        self.radio_combo_box.setAccessibleName("Choose radio:")
        self.radio_combo_box.addItems(self.radio_names)
        self.radio_combo_box.activated.connect(self._on_radio_selected)
        self.radio_combo_box.setGeometry(20, 190, 100, 20)
        self.radio_combo_box.setStyleSheet('background-color: rgb(10, 10, 10)')
        radio_layout.addWidget(self.radio_combo_box, 1, 0, 1, 1)

        self.volume_slider = QSlider()
        self.volume_slider.setAccessibleName('Volume control')
        self.volume_slider.setGeometry(130, 190, 100, 20)
        self.volume_slider.setStyleSheet('background-color: rgb(10, 10, 10)')
        self.volume_slider.setSliderPosition(self.player.audio_get_volume())
        self.volume_slider.valueChanged.connect(self._set_volume)
        radio_layout.addWidget(self.volume_slider, 1, 1, 1, 2)

        self.play_button = QPushButton('Play')
        self.play_button.setShortcut(QKeySequence('Ctrl+P'))
        self.play_button.setGeometry(20, 230, 50, 25)
        self.play_button.setStyleSheet('background-color: rgb(46, 200, 87)')
        self.play_button.clicked.connect(self._toggle_play_stop)
        radio_layout.addWidget(self.play_button, 2, 0)

        self.link_input = QLineEdit()
        self.link_input.setAccessibleName('Enter Link For Play')
        self.link_input.setGeometry(80, 230, 150, 20)
        self.link_input.setStyleSheet('background-color: rgb(10, 10, 10)')
        radio_layout.addWidget(self.link_input, 2, 1, 1, 2)

        add_btn = QPushButton('Add Radio')
        add_btn.setAccessibleName('Add New Radio')
        add_btn.setGeometry(175, 290, 80, 25)
        add_btn.setStyleSheet('background-color: rgb(10, 10, 10)')
        add_btn.clicked.connect(self._show_add_radio_dialog)
        add_btn.setShortcut(QKeySequence('Ctrl+A'))
        radio_layout.addWidget(add_btn, 3, 2)

        delete_btn = QPushButton('Delete Radio')
        delete_btn.setAccessibleName('Delete Radio')
        delete_btn.clicked.connect(self._delete_radio)
        delete_btn.setShortcut(QKeySequence('Ctrl+D'))
        delete_btn.setGeometry(90, 290, 80, 25)
        delete_btn.setStyleSheet('background-color: rgb(10, 10, 10)')
        radio_layout.addWidget(delete_btn, 3, 1)

        if self.radio_names:
            self._on_radio_selected()
        else:
            self.lcd.hide()
            self.info_display.show()
            self.info_display.setText("   No radios found. Add a new one!")

    def _show_add_radio_dialog(self):
        """Displays a dialog to allow the user to add a new radio station,
        pre-filling the name field with the currently selected radio's name.
        """
        self.stop_player()

        self.add_dialog = QDialog(self)
        self.add_dialog.setWindowTitle('Add New Radio')
        self.add_dialog.setGeometry(130, 250, 200, 100)

        radio_name_label = QLabel('Radio Name:', self.add_dialog)
        radio_name_label.setGeometry(5, 10, 70, 20)
        link_label = QLabel('Radio Link:', self.add_dialog)
        link_label.setGeometry(5, 40, 70, 20)

        self.new_radio_name_input = QLineEdit(self.add_dialog)
        self.new_radio_name_input.setGeometry(75, 10, 110, 20)
        self.new_radio_name_input.setPlaceholderText('Enter Radio Name')
        
        # --- NEW FEATURE: Pre-fill radio name ---
        if self.radio_names: # Only pre-fill if there are radios in the list
            self.new_radio_name_input.setText(self.selected_radio_name)
        # ----------------------------------------

        self.new_radio_link_input = QLineEdit(self.add_dialog)
        self.new_radio_link_input.setGeometry(75, 40, 110, 20)
        self.new_radio_link_input.setPlaceholderText('Enter Radio Link')

        add_button = QPushButton("Add", self.add_dialog)
        add_button.clicked.connect(self._add_or_update_radio) # Changed this connection
        add_button.setGeometry(45, 70, 50, 20)

        cancel_button = QPushButton("Cancel", self.add_dialog)
        cancel_button.clicked.connect(self.add_dialog.reject)
        cancel_button.setGeometry(105, 70, 50, 20)

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

        # Check if the name already exists AND is the currently selected radio's name
        # This indicates an attempt to update the current radio's link
        if new_name == self.selected_radio_name and new_name in self.radio_names:
            try:
                index_to_update = self.radio_names.index(new_name)
                # --- NEW FEATURE: Update existing link ---
                self.radio_links[index_to_update] = new_link
                self._save_radio_data()
                QMessageBox.information(self, "Success", f"Link for '{new_name}' updated successfully.")
                self.add_dialog.accept()
                self._refresh_radio_list_and_selection(new_name) # Refresh and re-select
                return
                # ------------------------------------------
            except ValueError:
                # This case should ideally not happen if new_name == self.selected_radio_name
                QMessageBox.critical(self, "Error", "Selected radio not found during update (this shouldn't happen).")
                self.add_dialog.reject()
                return

        # If name is new, or existing but not the currently selected one, add as new
        if new_name in self.radio_names:
            QMessageBox.warning(self, "Input Error", "A radio with this name already exists. Please choose a different name.")
            return

        # --- EXISTING FEATURE: Add new radio ---
        self.radio_names.append(new_name)
        self.radio_links.append(new_link)
        self._save_radio_data()
        QMessageBox.information(self, "Success", f"'{new_name}' added successfully.")
        self.add_dialog.accept()
        self._refresh_radio_list_and_selection(new_name) # Refresh and select the new radio
        # ---------------------------------------

    def _refresh_radio_list_and_selection(self, selected_name):
        """Refreshes the combo box items and sets the selection."""
        self.radio_combo_box.clear()
        self.radio_combo_box.addItems(self.radio_names)
        if selected_name in self.radio_names:
            self.radio_combo_box.setCurrentText(selected_name)
        else: # Fallback to first item if the desired one isn't found (e.g. after deleting)
            if self.radio_names:
                self.radio_combo_box.setCurrentIndex(0)
            else:
                self.lcd.hide()
                self.info_display.show()
                self.info_display.setText("   No radios found. Add a new one!")
                self.current_link = ""
        self._on_radio_selected() # Call this to update player media and display

    def _on_radio_selected(self):
        """Updates the display and prepares the VLC player when a radio is selected from the ComboBox."""
        if not self.radio_names: # Handle case where list is empty
            self.selected_radio_name = ""
            self.selected_radio_index = -1
            self.lcd.hide()
            self.info_display.show()
            self.info_display.setText("   No radios available. Add a new one!")
            self.current_link = ""
            self.stop_player()
            return

        self.selected_radio_name = self.radio_combo_box.currentText()
        self.selected_radio_index = self.radio_combo_box.currentIndex()

        self.lcd.setNumDigits(len(str(self.selected_radio_index + 1)))
        self.lcd.display(self.selected_radio_index + 1)
        self.info_display.hide()
        self.lcd.show()

        try:
            link_index = self.radio_names.index(self.selected_radio_name)
            self.current_link = self.radio_links[link_index]
            media = self.instance.media_new(self.current_link)
            self.player.set_media(media)
            self.player.audio_set_mute(0)
        except ValueError:
            QMessageBox.critical(self, "Error", "Selected radio not found in internal list. Please check data integrity.")
            self.current_link = ""
            self.stop_player()
        except Exception as e:
            QMessageBox.critical(self, "VLC Error", f"Failed to prepare media: {e}")
            self.current_link = ""
            self.stop_player()

        self.play_button.setText('Play')
        self.play_button.setStyleSheet('background-color: rgb(46, 200, 87)')
        self.play_button.setShortcut(QKeySequence('Ctrl+P'))

    def _toggle_play_stop(self):
        """Toggles between playing and stopping the radio based on button text.
        Prioritizes the direct link input if text is present.
        """
        direct_link = self.link_input.text().strip()

        if self.play_button.text() == 'Play':
            if direct_link:
                try:
                    media = self.instance.media_new(direct_link)
                    self.player.set_media(media)
                    self.player.play()
                    self.info_display.show()
                    self.lcd.hide()
                    self.info_display.setText(f"   Playing: {direct_link}")
                except Exception as e:
                    QMessageBox.warning(self, "Playback Error", f"Could not play direct link: {e}\nPlease check the link format or network connection.")
                    self.stop_player()
                    return
            else:
                if not self.radio_names:
                    QMessageBox.warning(self, "Selection Error", "No radio stations available. Please add a new one or select from the list.")
                    return
                if not self.current_link:
                    QMessageBox.warning(self, "Selection Error", "Please select a radio station first.")
                    return
                try:
                    self.player.play()
                    self.info_display.show()
                    self.lcd.hide()
                    self.info_display.setText(f"   You are listening to {self.selected_radio_name}")
                except Exception as e:
                    QMessageBox.warning(self, "Playback Error", f"Could not play selected radio: {e}\nPlease check network connection.")
                    self.stop_player()
                    return

            self.player.audio_set_mute(0)
            self.play_button.setText('Stop')
            self.play_button.setStyleSheet('background-color: rgb(200, 87, 46);')
            self.play_button.setShortcut(QKeySequence('Ctrl+S'))
        else:
            self.stop_player()
            if direct_link:
                self.link_input.clear()
            self.info_display.hide()
            self.lcd.show()

    def stop_player(self):
        """Stops the VLC media player and resets the play button state."""
        self.player.stop()
        self.play_button.setText('Play')
        self.play_button.setStyleSheet('background-color: rgb(46, 200, 87);')
        self.play_button.setShortcut(QKeySequence('Ctrl+P'))

    def _set_volume(self, value):
        """Sets the volume of the VLC media player based on the slider value."""
        self.player.audio_set_volume(value)

    def _delete_radio(self):
        """Deletes the currently selected radio station from the lists and database.
        Prevents deletion of default radios.
        """
        self.stop_player()

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

                # Determine which radio to select after deletion
                next_selected_name = None
                if self.radio_names:
                    # Try to select the same index if possible, otherwise the first
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Radio()
    w.show()
    sys.exit(app.exec())