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
from PyQt6.QtGui import QFont, QKeySequence
from PyQt6.QtCore import Qt # For alignment

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

        # Initialize VLC instance and player for playback
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.player.audio_set_volume(50) # Set initial volume

        # Initialize VLC player for recording
        self.recorder_player = None
        self.is_recording = False
        self.recordings_folder = "Recordings" 
        
        # Ensure recordings folder exists
        if not os.path.exists(self.recordings_folder):
            os.makedirs(self.recordings_folder)

        # Load radio data from JSON or use defaults
        self._load_radio_data()
        # Initialize the user interface
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
                sys.exit() # Exit application if user chooses not to install VLC

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
        self.sender().parent().close() # Close the version selection dialog

    def _load_radio_data(self):
        """Loads radio names and links from a JSON file, or initializes them with defaults if not found or corrupted."""
        # Default radio stations, used if radios.json is not found or corrupted
        default_radio_names = ['Gooshkon Radio', 'Persian Radio']
        default_radio_links = ['http://r.gooshkon.ir:8000/live.ogg', 'http://r.pgbu.ir:8000/live']
        self.radio_names = []
        self.radio_links = []
        
        self.db_file = 'radios.json' # The JSON file name

        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.radio_names = data.get('names', default_radio_names)
                    self.radio_links = data.get('links', default_radio_links)
            except (json.JSONDecodeError, FileNotFoundError, Exception) as e:
                # If file is corrupted or an error occurs during loading, re-initialize with defaults
                QMessageBox.warning(self, "Database Load Error", f"Error loading radios from '{self.db_file}': {e}. Re-initializing database.")
                self.radio_names = default_radio_names
                self.radio_links = default_radio_links
                self._save_radio_data() # Save the re-initialized data
        else:
            # If radios.json does not exist, initialize with defaults and save
            self.radio_names = default_radio_names
            self.radio_links = default_radio_links
            self._save_radio_data() # Save the initial default data

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

        # Row 0: Display (LCD or Info) - Spans 3 columns
        self.lcd = QLCDNumber()
        self.lcd.setStyleSheet('background-color: rgb(60, 60, 60)')
        radio_layout.addWidget(self.lcd, 0, 0, 1, 3) 

        self.info_display = QLineEdit()
        self.info_display.setFont(QFont('Arial', 10))
        self.info_display.setStyleSheet('background-color: rgb(60, 60, 60)')
        self.info_display.setReadOnly(True)
        self.info_display.hide() # Initially hidden, LCD is shown
        radio_layout.addWidget(self.info_display, 0, 0, 1, 3)

        # Row 1: Navigation Buttons, Radio ComboBox and Volume Slider
        navigation_and_volume_layout = QHBoxLayout() # A horizontal layout for this row

        # Previous Button
        self.prev_button = QPushButton('<< Prev')
        self.prev_button.setShortcut(QKeySequence('Ctrl+Left'))
        self.prev_button.setStyleSheet('background-color: rgb(10, 10, 10); color: white;')
        self.prev_button.clicked.connect(self._go_to_previous_radio)
        navigation_and_volume_layout.addWidget(self.prev_button)

        # Radio ComboBox (main selection)
        self.radio_combo_box = QComboBox()
        self.radio_combo_box.setAccessibleName("Choose radio:")
        self.radio_combo_box.addItems(self.radio_names)
        self.radio_combo_box.activated.connect(self._on_radio_selected)
        self.radio_combo_box.setStyleSheet('background-color: rgb(10, 10, 10); color: white;')
        navigation_and_volume_layout.addWidget(self.radio_combo_box)

        # Next Button
        self.next_button = QPushButton('Next >>')
        self.next_button.setShortcut(QKeySequence('Ctrl+Right'))
        self.next_button.setStyleSheet('background-color: rgb(10, 10, 10); color: white;')
        self.next_button.clicked.connect(self._go_to_next_radio)
        navigation_and_volume_layout.addWidget(self.next_button)

        # Volume Slider
        self.volume_slider = QSlider(Qt.Orientation.Horizontal) # Explicitly Horizontal
        self.volume_slider.setAccessibleName('Volume control')
        self.volume_slider.setStyleSheet('background-color: rgb(10, 10, 10); color: white;')
        self.volume_slider.setRange(0, 100) # VLC volume is 0-100
        self.volume_slider.setSliderPosition(self.player.audio_get_volume())
        self.volume_slider.valueChanged.connect(self._set_volume)
        navigation_and_volume_layout.addWidget(self.volume_slider)

        radio_layout.addLayout(navigation_and_volume_layout, 1, 0, 1, 3) # Row 1, Col 0, Spans 1 row, 3 columns

        # Row 2: Playback Controls and Link Input
        playback_controls_layout = QHBoxLayout()
        
        self.play_pause_button = QPushButton('Play')
        self.play_pause_button.setShortcut(QKeySequence('Ctrl+P'))
        self.play_pause_button.setStyleSheet('background-color: rgb(46, 200, 87); color: white;') # Green for Play
        self.play_pause_button.clicked.connect(self._toggle_play_pause)
        playback_controls_layout.addWidget(self.play_pause_button)

        self.stop_button = QPushButton('Stop')
        self.stop_button.setShortcut(QKeySequence('Ctrl+S'))
        self.stop_button.setStyleSheet('background-color: rgb(200, 87, 46); color: white;') # Red for Stop
        self.stop_button.clicked.connect(self.stop_player)
        playback_controls_layout.addWidget(self.stop_button)

        self.record_button = QPushButton('Record')
        self.record_button.setShortcut(QKeySequence('Ctrl+R'))
        self.record_button.setStyleSheet('background-color: rgb(170, 0, 0); color: white;') # Dark Red for Record
        self.record_button.clicked.connect(self._toggle_record)
        playback_controls_layout.addWidget(self.record_button)
        
        radio_layout.addLayout(playback_controls_layout, 2, 0, 1, 2) # Row 2, Col 0, Spans 1 row, 2 cols

        self.link_input = QLineEdit()
        self.link_input.setAccessibleName('Enter Link For Play')
        self.link_input.setPlaceholderText("Enter Direct Link")
        self.link_input.setStyleSheet('background-color: rgb(10, 10, 10); color: white;')
        radio_layout.addWidget(self.link_input, 2, 2, 1, 1) # Row 2, Col 2, Spans 1 col

        # Row 3: Management Buttons (Add/Delete) - Spans 2 columns
        management_buttons_layout = QHBoxLayout()
        
        self.delete_btn = QPushButton('Delete Radio')
        self.delete_btn.setAccessibleName('Delete Radio')
        self.delete_btn.clicked.connect(self._delete_radio)
        self.delete_btn.setShortcut(QKeySequence('Ctrl+D'))
        self.delete_btn.setStyleSheet('background-color: rgb(10, 10, 10); color: white;')
        management_buttons_layout.addWidget(self.delete_btn)

        add_btn = QPushButton('Add Radio')
        add_btn.setAccessibleName('Add New Radio')
        add_btn.clicked.connect(self._show_add_radio_dialog)
        add_btn.setShortcut(QKeySequence('Ctrl+A'))
        add_btn.setStyleSheet('background-color: rgb(10, 10, 10); color: white;')
        management_buttons_layout.addWidget(add_btn)

        radio_layout.addLayout(management_buttons_layout, 3, 1, 1, 2) # Row 3, Col 1, Spans 1 row, 2 cols

        # Set column stretch factors for responsiveness
        radio_layout.setColumnStretch(0, 1)
        radio_layout.setColumnStretch(1, 1)
        radio_layout.setColumnStretch(2, 1)
        
        # Set row stretch factors for responsiveness
        radio_layout.setRowStretch(0, 3) # Display area larger
        radio_layout.setRowStretch(1, 1)
        radio_layout.setRowStretch(2, 1)
        radio_layout.setRowStretch(3, 1)


        # Initial selection and display update
        if self.radio_names:
            self._on_radio_selected(play_on_select=False) # Don't auto-play on initial load
        else:
            self.lcd.hide()
            self.info_display.show()
            self.info_display.setText("   No radios found. Add a new one!")


    def _go_to_next_radio(self):
        """Navigates to the next radio in the list (cycles back to start if at end) and plays it automatically."""
        if not self.radio_names:
            QMessageBox.information(self, "Navigation", "No radio stations to navigate.")
            return
        current_index = self.radio_combo_box.currentIndex()
        next_index = (current_index + 1) % len(self.radio_names) # Cyclic navigation
        self.radio_combo_box.setCurrentIndex(next_index)
        self._on_radio_selected(play_on_select=True) # Play the new radio automatically

    def _go_to_previous_radio(self):
        """Navigates to the previous radio in the list (cycles to end if at start) and plays it automatically."""
        if not self.radio_names:
            QMessageBox.information(self, "Navigation", "No radio stations to navigate.")
            return
        current_index = self.radio_combo_box.currentIndex()
        # Add len(self.radio_names) to handle negative result of -1 % N correctly
        prev_index = (current_index - 1 + len(self.radio_names)) % len(self.radio_names) # Cyclic navigation
        self.radio_combo_box.setCurrentIndex(prev_index)
        self._on_radio_selected(play_on_select=True) # Play the new radio automatically



    def _show_add_radio_dialog(self):
        """Displays a dialog to allow the user to add a new radio station,
        pre-filling the name field with the currently selected radio's name.
        """
        self.stop_player() # Stop current playback
        self._stop_recording() # Ensure recording is stopped

        self.add_dialog = QDialog(self)
        self.add_dialog.setWindowTitle('Add New Radio')
        self.add_dialog.setGeometry(130, 250, 250, 120) # Slightly larger dialog

        dialog_layout = QVBoxLayout() # Use QVBoxLayout for the dialog contents
        self.add_dialog.setLayout(dialog_layout)

        name_layout = QHBoxLayout()
        radio_name_label = QLabel('Radio Name:')
        self.new_radio_name_input = QLineEdit()
        self.new_radio_name_input.setPlaceholderText('Enter Radio Name')
        if self.radio_names: # Pre-fill only if there are radios in the list
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

        self.add_dialog.exec() # Show the dialog as modal

    def _add_or_update_radio(self):
        """Adds a new radio or updates an existing one based on user input.
        Validates input and handles duplicate names.
        """
        new_name = self.new_radio_name_input.text().strip()
        new_link = self.new_radio_link_input.text().strip()

        if not new_name:
            QMessageBox.warning(self, "Input Error", "Radio name must be provided.")
            return
        if not new_link:
            QMessageBox.warning(self, "Input Error", "Radio link must be provided.")
            return
        
        # Basic URL validation
        if not (new_link.startswith("http://") or new_link.startswith("https://")):
            QMessageBox.warning(self, "Input Error", "Radio link must be a valid URL starting with http:// or https://")
            return

        # Check if the name exists and is the currently selected radio's name
        # This condition is for updating the link of an existing radio
        if new_name == self.selected_radio_name and new_name in self.radio_names:
            try:
                index_to_update = self.radio_names.index(new_name)
                self.radio_links[index_to_update] = new_link
                self._save_radio_data()
                QMessageBox.information(self, "Success", f"Link for '{new_name}' updated successfully.")
                self.add_dialog.accept() # Close the dialog
                self._refresh_radio_list_and_selection(new_name) # Refresh and re-select the updated radio
                return
            except ValueError:
                # Should not happen if new_name == self.selected_radio_name and it's in radio_names
                QMessageBox.critical(self, "Error", "Selected radio not found during update (this shouldn't happen).")
                self.add_dialog.reject()
                return

        # If name is new, or existing but not the currently selected one, add as a new radio
        if new_name in self.radio_names:
            QMessageBox.warning(self, "Input Error", "A radio with this name already exists. Please choose a different name.")
            return

        # Add new radio
        self.radio_names.append(new_name)
        self.radio_links.append(new_link)
        self._save_radio_data()
        QMessageBox.information(self, "Success", f"'{new_name}' added successfully.")
        self.add_dialog.accept() # Close the dialog
        self._refresh_radio_list_and_selection(new_name) # Refresh and select the new radio

    def _refresh_radio_list_and_selection(self, selected_name):
        """Refreshes the combo box items and sets the selection based on the given name.
        Handles cases where the list becomes empty.
        """
        self.radio_combo_box.clear() # Clear existing items
        self.radio_combo_box.addItems(self.radio_names) # Add all current radios

        if selected_name in self.radio_names:
            self.radio_combo_box.setCurrentText(selected_name) # Select the specified radio
        else:
            if self.radio_names: # If list is not empty, select the first item
                self.radio_combo_box.setCurrentIndex(0)
            else: # If list is empty, update display to "No radios found"
                self.lcd.hide()
                self.info_display.show()
                self.info_display.setText("   No radios found. Add a new one!")
                self.current_link = "" # No current link if list is empty
        self._on_radio_selected() # Trigger update for player media and display

    def _on_radio_selected(self):
        """Updates the display and prepares the VLC player when a radio is selected from the ComboBox."""
        if not self.radio_names: # Handle case where list becomes empty
            self.selected_radio_name = ""
            self.selected_radio_index = -1
            self.lcd.hide()
            self.info_display.show()
            self.info_display.setText("   No radios available. Add a new one!")
            self.stop_player() # Ensure player is stopped and button is "Play"
            self._stop_recording() # Ensure recording is stopped
            return

        self.selected_radio_name = self.radio_combo_box.currentText()
        self.selected_radio_index = self.radio_combo_box.currentIndex()

        # Update display: show index on LCD, hide info display
        self.lcd.setNumDigits(len(str(self.selected_radio_index + 1)))
        self.lcd.display(self.selected_radio_index + 1)
        self.info_display.hide()
        self.lcd.show()

        try:
            link_index = self.radio_names.index(self.selected_radio_name)
            self.current_link = self.radio_links[link_index]
            media = self.instance.media_new(self.current_link)
            self.player.set_media(media)
            self.player.audio_set_mute(0) # Ensure not muted
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

        # Reset Play/Pause button to 'Play' when a new radio is selected/prepared
        self.play_pause_button.setText('Play')
        self.play_pause_button.setStyleSheet('background-color: rgb(46, 200, 87); color: white;')
        self.play_pause_button.setShortcut(QKeySequence('Ctrl+P'))

    def _toggle_play_pause(self):
        """Toggles between playing and pausing the radio based on the button text.
        Prioritizes the direct link input if text is present.
        """
        direct_link = self.link_input.text().strip()

        if self.play_pause_button.text() == 'Play':
            # Handle playing
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
                if not self.radio_names: # No radios in the list
                    QMessageBox.warning(self, "Selection Error", "No radio stations available. Please add a new one or select from the list.")
                    return
                if not self.current_link: # No selected link to play
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

            self.player.audio_set_mute(0) # Ensure audio is not muted
            self.play_pause_button.setText('Pause')
            self.play_pause_button.setStyleSheet('background-color: rgb(255, 165, 0); color: white;') # Orange for Pause
            self.play_pause_button.setShortcut(QKeySequence('Ctrl+P')) # Shortcut remains for toggle

        elif self.play_pause_button.text() == 'Pause':
            # Handle pausing
            self.player.pause()
            self.info_display.show()
            self.info_display.setText(f"   Paused: {self.selected_radio_name or direct_link}")
            self.play_pause_button.setText('Play')
            self.play_pause_button.setStyleSheet('background-color: rgb(46, 200, 87); color: white;') # Green for Play
            self.play_pause_button.setShortcut(QKeySequence('Ctrl+P'))

    def stop_player(self):
        """Stops the VLC media player completely and resets the Play/Pause button state.
        Also stops any active recording.
        """
        self.player.stop()
        self.play_pause_button.setText('Play')
        self.play_pause_button.setStyleSheet('background-color: rgb(46, 200, 87); color: white;') # Green for Play
        self.play_pause_button.setShortcut(QKeySequence('Ctrl+P'))
        self.info_display.hide() # Hide info display
        self.lcd.show() # Show LCD display
        if self.link_input.text().strip(): # Clear direct link input if it was used
            self.link_input.clear()
        self._stop_recording() # Ensure recording is stopped

    def _toggle_record(self):
        """Toggles recording of the current stream.
        Recording can only start if a stream is currently playing.
        """
        # Check if anything is playing or if the recorder player is already active
        if not self.player.is_playing() and not self.recorder_player:
            QMessageBox.warning(self, "Recording Error", "Please play a radio station or direct link before recording.")
            return

        if not self.is_recording:
            # Start recording
            # Determine which link to record (direct link input has priority, then selected radio link)
            stream_link = self.link_input.text().strip() if self.link_input.text().strip() else self.current_link

            if not stream_link:
                QMessageBox.warning(self, "Recording Error", "No stream link available to record.")
                return

            # Generate a unique filename based on current time and selected radio name
            now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            # Clean selected_radio_name for use in filename
            file_name_base = "".join(c for c in self.selected_radio_name if c.isalnum() or c in (' ', '_')).strip()
            if not file_name_base: # Fallback if name is empty or unparseable
                file_name_base = "DirectStream" if self.link_input.text().strip() else "Radio"
            file_name_base = file_name_base.replace(" ", "_") # Replace spaces with underscores
            file_name = f"{file_name_base}_{now}.mp3"
            file_path = os.path.join(self.recordings_folder, file_name)

            # VLC options for recording (transcoding to MP3)
            # This option actively transcodes the audio to MP3 and saves it to the specified file path.
            record_options = f":sout=#transcode{{vcodec=none,acodec=mp3,ab=128,channels=2,samplerate=44100}}:std{{access=file,mux=mp3,dst='{file_path}'}}"

            try:
                # Create a new media object specifically for recording from the stream link
                record_media = self.instance.media_new(stream_link, record_options)
                # Create a new player instance for recording
                self.recorder_player = self.instance.media_player_new()
                self.recorder_player.set_media(record_media)
                self.recorder_player.play() # Start the recording stream

                # Update UI state to reflect recording
                self.is_recording = True
                self.record_button.setText('Stop Recording')
                self.record_button.setStyleSheet('background-color: rgb(0, 100, 0); color: white;') # Dark green when recording
                self.info_display.show()
                self.info_display.setText(f"   Recording to: {file_name}")
                self.lcd.hide()

            except Exception as e:
                QMessageBox.critical(self, "Recording Error", f"Failed to start recording: {e}\nEnsure VLC is properly configured and the path '{self.recordings_folder}' is writable.")
                self._stop_recording() # Reset state if an error occurs
        else:
            # Stop recording if currently active
            self._stop_recording()
            QMessageBox.information(self, "Recording Complete", f"Recording saved to '{self.recordings_folder}' folder.")


    def _stop_recording(self):
        """Stops the recording player if it's active and resets UI elements related to recording."""
        if self.is_recording and self.recorder_player:
            self.recorder_player.stop() # Stop the VLC recording player
            self.recorder_player = None # Clear the player instance
            self.is_recording = False
            self.record_button.setText('Record') # Reset button text
            self.record_button.setStyleSheet('background-color: rgb(170, 0, 0); color: white;') # Reset button color
            # Only revert info/LCD display if main player is not active (to avoid conflicting messages)
            if not self.player.is_playing():
                self.info_display.hide()
                self.lcd.show()


    def _set_volume(self, value):
        """Sets the volume of the VLC media player based on the slider value."""
        self.player.audio_set_volume(value)

    def _delete_radio(self):
        """Deletes the currently selected radio station from the lists and database.
        Prevents deletion of default radios ("Gooshkon Radio", "Persian Radio").
        """
        self.stop_player() # Ensure playback and recording are stopped before deletion
        self._stop_recording()

        if not self.radio_names:
            QMessageBox.warning(self, "Warning!", "No radio stations to delete.")
            return

        # Prevent deletion of default radios
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
                self._save_radio_data() # Save updated lists

                # Determine which radio to select after deletion
                next_selected_name = None
                if self.radio_names: # If there are still radios left
                    if index_to_delete < len(self.radio_names):
                        next_selected_name = self.radio_names[index_to_delete] # Try to select the next one in sequence
                    else:
                        next_selected_name = self.radio_names[0] # If deleted last, select the first
                
                self._refresh_radio_list_and_selection(next_selected_name) # Refresh UI and select next
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