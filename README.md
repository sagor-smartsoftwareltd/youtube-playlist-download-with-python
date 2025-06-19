# 🎵 YouTube Playlist Downloader

A Python GUI application for downloading YouTube playlists in the best available quality using `yt-dlp`. Fetch playlist metadata, view video titles, and download videos with real-time progress tracking—all in a responsive, cross-platform interface built with Tkinter.

---

## ✨ Features

- 🎬 **Fetch Playlist Metadata**: Retrieve video titles and URLs by entering a YouTube playlist link.
- 📥 **Best Quality Downloads**: Downloads MP4 videos with the best available video and audio using `yt-dlp`.
- 📊 **Progress Tracking**: Real-time progress bar and status updates.
- ✅ **Success/Failure Indicators**: Videos marked green for success and red for failure.
- 🔄 **Threaded Downloads**: Background threading keeps the GUI responsive.
- 💻 **Cross-Platform**: Works on Windows, macOS, and Linux (with dependencies installed).

---

## 🧰 Prerequisites

- **Python 3.6+**
- **yt-dlp**
- **FFmpeg** (used by `yt-dlp` to merge audio and video)
- **Tkinter** (comes pre-installed with most Python versions)

---

## 🧪 Installation of Dependencies

### 🔵 Windows

```bash
pip install yt-dlp
```

- Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/) and add it to your system PATH.

### 🍎 macOS (using Homebrew)

```bash
brew install yt-dlp ffmpeg
```

### 🐧 Linux

#### Debian/Ubuntu

```bash
sudo apt-get install yt-dlp ffmpeg python3-tk
```

#### Fedora

```bash
sudo dnf install yt-dlp ffmpeg python3-tkinter
```

---

## 🚀 Installation

```bash
git clone https://github.com/your-username/youtube-playlist-downloader.git
cd youtube-playlist-downloader
```

---

## ▶️ Usage

```bash
python youtube_playlist_downloader.py
```

1. Launch the application.
2. Paste your playlist URL (e.g., `https://www.youtube.com/playlist?list=PL...`) into the **Playlist URL** field.
3. Click **Fetch Videos** to load the video list.
4. Click **Download All** to begin downloading to `~/Downloads/downloads`.
5. Monitor download progress through the GUI.

📁 **Downloads Folder**: Videos are saved in `~/Downloads/downloads`.

✅ Successful downloads: **Green**  
❌ Failed downloads: **Red**

---

## 📸 Screenshots

<!-- Add screenshots here -->

---

## ⚠️ Notes

- Ensure write permissions for `~/Downloads/downloads`.
- Downloads are subject to YouTube's rate limits. A delay is included to mitigate this.
- Only videos with valid metadata will be downloaded.
- The application uses threading—avoid forcefully closing during active downloads.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙏 Acknowledgments

- [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) – Powerful tool for video downloading.
- [`Tkinter`](https://docs.python.org/3/library/tkinter.html) – GUI framework included with Python.

---

## 🤝 Contributing

Pull requests and issues are welcome! Feel free to fork and improve the project.
