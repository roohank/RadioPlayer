Radio Player Master
Radio Player Master is a simple desktop application built with PyQt6 and VLC, allowing you to listen to online radio stations. You can play pre-defined stations, add new ones, delete existing ones, play direct radio stream links, and even record your favorite broadcasts.
Features
• 
Play Online Radio: Listen to your favorite online radio stations.
• 
Play/Pause Functionality: A single button to toggle between playing and pausing your current broadcast.
• 
Dedicated Stop Button: A separate button to completely stop the playback.
• 
Record Live Streams: Record the currently playing radio stream to an MP3 file, saved in a dedicated "Recordings" folder.
• 
Add/Update Radios: Easily add new radio stations by providing their name and stream URL. You can also update the link of an existing radio by entering its current name and a new link.
• 
Import from M3U: Import multiple radio stations at once from a local .m3u playlist file.
• 
Delete Radios: Remove unwanted radio stations from your list (default stations are protected).
• 
Direct Link Playback: Play any direct audio stream link.
• 
Volume Control: Adjust the playback volume using a slider.
• 
VLC Integration: Utilizes VLC Media Player for robust audio streaming.
• 
Persistent Data: Radio station lists are saved using JSON in a radios.json file.
• 
Next/Previous Buttons: Navigate between radio stations in your list with dedicated "Next" and "Previous" buttons.
• 
Rewind/Forward Buttons: Seek backward or forward in the stream by 10 seconds.
Requirements
• 
Python 3.x
• 
PyQt6 (pip install PyQt6)
• 
python-vlc (pip install python-vlc)
• 
VLC Media Player (Desktop Application): You must have VLC Media Player installed on your system. If not, the application will prompt you to download it upon first run if python-vlc import fails.
Installation
. 1
Clone the repository (or download the source code):
Bash
Copy code
git clone [https://github.com/your-username/radio-player-master.git](https://github.com/your-username/radio-player-master.git)
cd radio-player-master
(Replace your-username/radio-player-master with your actual repository link)
. 2
Install Python dependencies:
Bash
Copy code
pip install PyQt6 python-vlc
(Note: semidbm is no longer required.)
. 3
Install VLC Media Player:
If you don't have VLC Media Player installed on your system, please download it from the official VLC website: https://www.videolan.org/vlc/. The application will also guide you if it detects VLC is missing.
Usage
. 1
Run the application:
Bash
Copy code
python main_radio_app.py
(Assuming your main application file is named main_radio_app.py)
. 2
Select a Radio: Use the list widget on the left to select a radio station. You can also use the "Next >>" and "<< Prev" buttons to navigate the list.
. 3
Play/Pause: Click the "Play" button to start listening. While playing, this button will change to "Pause". Click it again to pause playback.
. 4
Stop Playback: Click the separate "Stop" button to completely stop the current broadcast.
. 5
Record Stream: Click the "Record" button while a station is playing to start recording. The button will change to "Stop Recording". Click it again to stop and save the recording to the Recordings folder.
. 6
Direct Link: Enter an audio stream URL into the "Enter Direct Link" field and click "Play" to listen to it directly.
. 7
Import from M3U: Click the "Import from m3u" button to select a playlist file from your computer. The application will parse the file and add all valid radio stations to your list.
. 8
Add/Update Radio: Click the "Add Radio" button.
• 
To add a new radio, enter a new name and its stream link.
• 
To update an existing radio's link, ensure the name field contains the exact name of an existing radio, and then enter the new stream link.
. 9
Delete Radio: Select a radio from the list and click "Delete Radio" to remove it. (Default radios cannot be deleted).
. 10
Volume Control: Use the slider to adjust the volume.
 
مدیریت رادیو پلیر
مدیریت رادیو پلیر یک برنامه دسکتاپ ساده است که با استفاده از PyQt6 و VLC ساخته شده است و به شما امکان می‌دهد به ایستگاه‌های رادیویی آنلاین گوش دهید. شما می‌توانید ایستگاه‌های از پیش تعریف‌شده را پخش کنید، ایستگاه‌های جدید اضافه کنید، ایستگاه‌های موجود را حذف کنید، لینک‌های مستقیم پخش رادیو را پخش کنید، و حتی پخش‌های مورد علاقه خود را ضبط کنید.
ویژگی‌ها
• 
پخش رادیو آنلاین: به ایستگاه‌های رادیویی آنلاین مورد علاقه خود گوش دهید.
• 
عملکرد پخش/مکث: یک دکمه واحد برای جابجایی بین پخش و مکث برنامه در حال اجرا.
• 
دکمه توقف اختصاصی: یک دکمه جداگانه برای متوقف کردن کامل پخش.
• 
ضبط پخش زنده: جریان رادیویی در حال پخش را در قالب یک فایل MP3 ضبط کنید که در پوشه اختصاصی "Recordings" ذخیره می‌شود.
• 
افزودن/به‌روزرسانی رادیوها: به راحتی ایستگاه‌های رادیویی جدید را با ارائه نام و URL پخش آنها اضافه کنید. همچنین می‌توانید با وارد کردن نام فعلی یک رادیوی موجود و یک لینک جدید، لینک آن را به‌روزرسانی کنید.
• 
ورود از فایل M3U: چندین ایستگاه رادیویی را به صورت یکجا از یک فایل لیست پخش .m3u محلی وارد کنید.
• 
حذف رادیوها: ایستگاه‌های رادیویی ناخواسته را از لیست خود حذف کنید (ایستگاه‌های پیش‌فرض محافظت شده‌اند).
• 
پخش لینک مستقیم: هر لینک مستقیم پخش صوتی را پخش کنید.
• 
کنترل صدا: میزان صدا را با استفاده از یک اسلایدر تنظیم کنید.
• 
ادغام VLC: از VLC Media Player برای پخش جریانی صوتی قدرتمند استفاده می‌کند.
• 
داده‌های پایدار: لیست ایستگاه‌های رادیویی با استفاده از JSON در یک فایل radios.json ذخیره می‌شوند.
• 
دکمه‌های بعدی/قبلی: با دکمه‌های اختصاصی "Next" و "Previous" در بین ایستگاه‌های رادیویی در لیست خود جابجا شوید.
• 
دکمه‌های جلو و عقب بردن: پخش را ۱۰ ثانیه به عقب یا جلو ببرید.
نیازمندی‌ها
• 
پایتون 3.x
• 
PyQt6 (pip install PyQt6)
• 
python-vlc (pip install python-vlc)
• 
VLC Media Player (برنامه دسکتاپ): باید VLC Media Player را روی سیستم خود نصب داشته باشید. در غیر این صورت، برنامه در اولین اجرا در صورت عدم موفقیت در وارد کردن python-vlc، از شما درخواست دانلود آن را می‌دهد.
نصب
. 1
کلون کردن مخزن (یا دانلود کد منبع):
Bash
Copy code
git clone [https://github.com/your-username/radio-player-master.git](https://github.com/your-username/radio-player-master.git)
cd radio-player-master
(لطفاً your-username/radio-player-master را با لینک مخزن واقعی خود جایگزین کنید)
. 2
نصب وابستگی‌های پایتون:
Bash
Copy code
pip install PyQt6 python-vlc
(توجه: semidbm دیگر مورد نیاز نیست.)
. 3
نصب VLC Media Player:
اگر VLC Media Player روی سیستم شما نصب نیست، لطفاً آن را از وب‌سایت رسمی VLC دانلود کنید: https://www.videolan.org/vlc/. برنامه همچنین در صورت تشخیص عدم وجود VLC، شما را راهنمایی خواهد کرد.
نحوه استفاده
. 1
اجرای برنامه:
Bash
Copy code
python main_radio_app.py
(با فرض اینکه فایل اصلی برنامه شما main_radio_app.py نام دارد)
. 2
انتخاب رادیو: از لیست موجود در سمت چپ برای انتخاب یک ایستگاه رادیویی استفاده کنید. همچنین می‌توانید از دکمه‌های "Next >>" و "<< Prev" برای جابجایی بین ایستگاه‌ها استفاده کنید.
. 3
پخش/مکث: برای شروع گوش دادن روی دکمه "Play" کلیک کنید. در حین پخش، این دکمه به "Pause" تغییر خواهد کرد. دوباره روی آن کلیک کنید تا پخش مکث شود.
. 4
توقف پخش: برای متوقف کردن کامل پخش جاری، روی دکمه جداگانه "Stop" کلیک کنید.
. 5
ضبط جریان: در حالی که یک ایستگاه در حال پخش است، روی دکمه "Record" کلیک کنید تا ضبط شروع شود. دکمه به "Stop Recording" تغییر خواهد کرد. برای توقف و ذخیره ضبط، دوباره روی آن کلیک کنید. فایل‌های ضبط شده در پوشه Recordings ذخیره می‌شوند.
. 6
لینک مستقیم: یک URL پخش صوتی را در فیلد "Enter Direct Link" وارد کرده و برای گوش دادن مستقیم روی "Play" کلیک کنید.
. 7
ورود از فایل M3U: روی دکمه "Import from m3u" کلیک کنید تا یک فایل لیست پخش را از کامپیوتر خود انتخاب کنید. برنامه فایل را تجزیه کرده و تمام ایستگاه‌های رادیویی معتبر را به لیست شما اضافه می‌کند.
. 8
افزودن/به‌روزرسانی رادیو: روی دکمه "Add Radio" کلیک کنید.
• 
برای افزودن رادیوی جدید، یک نام جدید و لینک پخش آن را وارد کنید.
• 
برای به‌روزرسانی لینک یک رادیوی موجود، اطمینان حاصل کنید که نام رادیو دقیقاً با نام رادیوی موجود مطابقت دارد و سپس لینک پخش جدید را وارد کنید.
. 9
حذف رادیو: یک رادیو را از لیست انتخاب کرده و برای حذف آن روی "Delete Radio" کلیک کنید. (رادیوهای پیش‌فرض قابل حذف نیستند).
. 10
کنترل صدا: از اسلایدر برای تنظیم صدا استفاده کنید.
 
License
This project is licensed under the MIT License - see the LICENSE file for details.
 
لایسنس
این پروژه تحت لایسنس MIT منتشر شده است - برای جزئیات بیشتر به فایل LICENSE مراجعه کنید.