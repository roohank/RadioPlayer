# Radio Player Master

Radio Player Master is a simple desktop application built with PyQt6 and VLC, allowing you to listen to online radio stations. You can play pre-defined stations, add new ones, delete existing ones, and even play direct radio stream links.

## Features

* **Play Online Radio:** Listen to your favorite online radio stations.
* **Add/Update Radios:** Easily add new radio stations by providing their name and stream URL. You can also update the link of an existing radio by entering its current name and a new link.
* **Delete Radios:** Remove unwanted radio stations from your list (default stations are protected).
* **Direct Link Playback:** Play any direct audio stream link.
* **Volume Control:** Adjust the playback volume using a slider.
* **VLC Integration:** Utilizes VLC Media Player for robust audio streaming.
* **Persistent Data:** Radio station lists are saved using **JSON** in a `radios.json` file.

## Requirements

* Python 3.x
* PyQt6 (`pip install PyQt6`)
* python-vlc (`pip install python-vlc`)
* **VLC Media Player (Desktop Application):** You must have VLC Media Player installed on your system. If not, the application will prompt you to download it upon first run if `python-vlc` import fails.

## Installation

1.  **Clone the repository (or download the source code):**
    ```bash
    git clone [https://github.com/your-username/radio-player-master.git](https://github.com/your-username/radio-player-master.git)
    cd radio-player-master
    ```
    (Replace `your-username/radio-player-master` with your actual repository link)

2.  **Install Python dependencies:**
    ```bash
    pip install PyQt6 python-vlc
    ```
    *(Note: `semidbm` is no longer required.)*

3.  **Install VLC Media Player:**
    If you don't have VLC Media Player installed on your system, please download it from the official VLC website: [https://www.videolan.org/vlc/](https://www.videolan.org/vlc/). The application will also guide you if it detects VLC is missing.

## Usage

1.  **Run the application:**
    ```bash
    python main_radio_app.py
    ```
    (Assuming your main application file is named `main_radio_app.py`)

2.  **Select a Radio:** Use the dropdown (combo box) to select a pre-defined radio station.
3.  **Play/Stop:** Click the "Play" button to start listening. It will change to "Stop" while playing.
4.  **Direct Link:** Enter an audio stream URL into the "Enter Link For Play" field and click "Play" to listen to it directly.
5.  **Add/Update Radio:** Click the "Add Radio" button.
    * To **add a new radio**, enter a new name and its stream link.
    * To **update an existing radio's link**, ensure the name field contains the exact name of an existing radio, and then enter the new stream link.
6.  **Delete Radio:** Select a radio from the dropdown and click "Delete Radio" to remove it. (Default radios cannot be deleted).
7.  **Volume Control:** Use the slider to adjust the volume.

---

# مدیریت رادیو پلیر

مدیریت رادیو پلیر یک برنامه دسکتاپ ساده است که با استفاده از PyQt6 و VLC ساخته شده است و به شما امکان می‌دهد به ایستگاه‌های رادیویی آنلاین گوش دهید. شما می‌توانید ایستگاه‌های از پیش تعریف‌شده را پخش کنید، ایستگاه‌های جدید اضافه کنید، ایستگاه‌های موجود را حذف کنید و حتی لینک‌های مستقیم پخش رادیو را پخش کنید.

## ویژگی‌ها

* **پخش رادیو آنلاین:** به ایستگاه‌های رادیویی آنلاین مورد علاقه خود گوش دهید.
* **افزودن/به‌روزرسانی رادیوها:** به راحتی ایستگاه‌های رادیویی جدید را با ارائه نام و URL پخش آنها اضافه کنید. همچنین می‌توانید با وارد کردن نام فعلی یک رادیوی موجود و یک لینک جدید، لینک آن را به‌روزرسانی کنید.
* **حذف رادیوها:** ایستگاه‌های رادیویی ناخواسته را از لیست خود حذف کنید (ایستگاه‌های پیش‌فرض محافظت شده‌اند).
* **پخش لینک مستقیم:** هر لینک مستقیم پخش صوتی را پخش کنید.
* **کنترل صدا:** میزان صدا را با استفاده از یک اسلایدر تنظیم کنید.
* **ادغام VLC:** از VLC Media Player برای پخش جریانی صوتی قدرتمند استفاده می‌کند.
* **داده‌های پایدار:** لیست ایستگاه‌های رادیویی با استفاده از **JSON** در یک فایل `radios.json` ذخیره می‌شوند.

## نیازمندی‌ها

* پایتون 3.x
* PyQt6 (`pip install PyQt6`)
* python-vlc (`pip install python-vlc`)
* **VLC Media Player (برنامه دسکتاپ):** باید VLC Media Player را روی سیستم خود نصب داشته باشید. در غیر این صورت، برنامه در اولین اجرا در صورت عدم موفقیت در وارد کردن `python-vlc`، از شما درخواست دانلود آن را می‌دهد.

## نصب

1.  **کلون کردن مخزن (یا دانلود کد منبع):**
    ```bash
    git clone [https://github.com/your-username/radio-player-master.git](https://github.com/your-username/radio-player-master.git)
    cd radio-player-master
    ```
    (لطفاً `your-username/radio-player-master` را با لینک مخزن واقعی خود جایگزین کنید)

2.  **نصب وابستگی‌های پایتون:**
    ```bash
    pip install PyQt6 python-vlc
    ```
    *(توجه: `semidbm` دیگر مورد نیاز نیست.)*

3.  **نصب VLC Media Player:**
    اگر VLC Media Player روی سیستم شما نصب نیست، لطفاً آن را از وب‌سایت رسمی VLC دانلود کنید: [https://www.videolan.org/vlc/](https://www.videolan.org/vlc/). برنامه همچنین در صورت تشخیص عدم وجود VLC، شما را راهنمایی خواهد کرد.

## نحوه استفاده

1.  **اجرای برنامه:**
    ```bash
    python main_radio_app.py
    ```
    (با فرض اینکه فایل اصلی برنامه شما `main_radio_app.py` نام دارد)

2.  **انتخاب رادیو:** از منوی کشویی (combo box) برای انتخاب یک ایستگاه رادیویی از پیش تعریف شده استفاده کنید.
3.  **پخش/توقف:** برای شروع گوش دادن روی دکمه "Play" کلیک کنید. در حین پخش به "Stop" تغییر خواهد کرد.
4.  **لینک مستقیم:** یک URL پخش صوتی را در فیلد "Enter Link For Play" وارد کرده و برای گوش دادن مستقیم روی "Play" کلیک کنید.
5.  **افزودن/به‌روزرسانی رادیو:** روی دکمه "Add Radio" کلیک کنید.
    * برای **افزودن رادیوی جدید**، یک نام جدید و لینک پخش آن را وارد کنید.
    * برای **به‌روزرسانی لینک یک رادیوی موجود**، اطمینان حاصل کنید که نام رادیو دقیقاً با نام رادیوی موجود مطابقت دارد و سپس لینک پخش جدید را وارد کنید.
6.  **حذف رادیو:** یک رادیو را از منوی کشویی انتخاب کرده و برای حذف آن روی "Delete Radio" کلیک کنید. (رادیوهای پیش‌فرض قابل حذف نیستند).
7.  **کنترل صدا:** از اسلایدر برای تنظیم صدا استفاده کنید.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## لایسنس

این پروژه تحت لایسنس MIT منتشر شده است - برای جزئیات بیشتر به فایل [LICENSE](LICENSE) مراجعه کنید.