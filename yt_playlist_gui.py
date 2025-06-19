import tkinter as tk
from tkinter import ttk, messagebox
import threading
from pathlib import Path
import re
from yt_dlp import YoutubeDL

class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader (Playlist & Single Video)")
        self.root.geometry("800x550")

        self.download_path = Path.home() / "Downloads" / "downloads"
        self.download_path.mkdir(parents=True, exist_ok=True)

        self.playlist_videos = []

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Playlist URL:").grid(row=0, column=0, sticky="w")
        self.playlist_url_entry = ttk.Entry(frame, width=80)
        self.playlist_url_entry.grid(row=0, column=1, padx=5)
        ttk.Button(frame, text="Fetch Playlist", command=self.fetch_playlist).grid(row=0, column=2)

        self.video_listbox = tk.Listbox(frame, height=12)
        self.video_listbox.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=5)
        frame.rowconfigure(1, weight=1)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.video_listbox.yview)
        scrollbar.grid(row=1, column=3, sticky="ns")
        self.video_listbox.config(yscrollcommand=scrollbar.set)

        ttk.Button(frame, text="Download Playlist", command=self.download_all_videos).grid(row=2, column=0, columnspan=3, pady=5)

        ttk.Separator(frame).grid(row=3, column=0, columnspan=4, sticky="ew", pady=10)

        ttk.Label(frame, text="Single Video URL:").grid(row=4, column=0, sticky="w")
        self.single_url_entry = ttk.Entry(frame, width=80)
        self.single_url_entry.grid(row=4, column=1, padx=5)
        ttk.Button(frame, text="Download Video", command=self.download_single_video).grid(row=4, column=2)

        self.progress_bar = ttk.Progressbar(frame, orient=tk.HORIZONTAL, mode="determinate")
        self.progress_bar.grid(row=5, column=0, columnspan=3, sticky="ew", pady=10)

        self.status_label = ttk.Label(frame, text="Ready")
        self.status_label.grid(row=6, column=0, columnspan=3, sticky="w")

    def fetch_playlist(self):
        url = self.playlist_url_entry.get().strip()

        if not re.match(r"https?://(www\.)?youtube\.com/playlist\?list=[\w-]+", url):
            messagebox.showerror("Invalid URL", "Please enter a valid YouTube playlist URL.")
            return

        self.status_label.config(text="Fetching playlist...")
        self.video_listbox.delete(0, tk.END)
        self.playlist_videos.clear()

        def worker():
            ydl_opts = {
                "quiet": True,
                "skip_download": True,
                "ignoreerrors": True,
                "extract_flat": True,
            }
            with YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(url, download=False)
                    entries = info.get("entries", [])
                    for idx, video in enumerate(entries, 1):
                        if not video:
                            self.video_listbox.insert(tk.END, f"{idx}. [Unavailable video]")
                            self.playlist_videos.append(None)
                            continue
                        title = video.get("title", f"Video {idx}")
                        video_url = f"https://www.youtube.com/watch?v={video.get('id')}"
                        self.playlist_videos.append({"title": title, "url": video_url})
                        self.video_listbox.insert(tk.END, f"{idx}. {title}")
                    self.status_label.config(text=f"Fetched {len(self.playlist_videos)} videos.")
                except Exception as e:
                    self.status_label.config(text="Failed to fetch playlist")
                    messagebox.showerror("Error", str(e))

        threading.Thread(target=worker, daemon=True).start()

    def sanitize_filename(self, s):
        # Only allow letters, numbers, space, dot, dash, underscore
        return "".join(c for c in s if c.isalnum() or c in " ._-").rstrip()

    def download_all_videos(self):
        if not self.playlist_videos:
            messagebox.showerror("No videos", "Fetch the playlist first.")
            return

        self.progress_bar["value"] = 0
        self.progress_bar["maximum"] = len(self.playlist_videos)
        self.status_label.config(text="Starting playlist download...")

        def worker():
            ydl_opts = {
                "outtmpl": str(self.download_path / "%(title).200s.%(ext)s"),
                "format": "bestvideo+bestaudio/best",
                "ignoreerrors": True,
                "no_warnings": True,
                "noprogress": False,  # Show progress in console for debugging
                "restrictfilenames": True,  # Sanitize filenames automatically
                "merge_output_format": "mp4",  # Make sure merged files are mp4
            }

            with YoutubeDL(ydl_opts) as ydl:
                for idx, video in enumerate(self.playlist_videos):
                    if video is None:
                        self.video_listbox.itemconfig(idx, bg="#ff6666", fg="white")
                        self.progress_bar["value"] += 1
                        continue

                    title = video["title"]
                    url = video["url"]

                    self.status_label.config(text=f"Downloading ({idx+1}/{len(self.playlist_videos)}): {title}")
                    self.root.update_idletasks()

                    try:
                        ydl.download([url])
                        self.video_listbox.itemconfig(idx, bg="#90ee90", fg="black")
                    except Exception as e:
                        self.video_listbox.itemconfig(idx, bg="#ff6666", fg="white")
                        print(f"Failed: {title}: {e}")

                    self.progress_bar["value"] += 1

                self.status_label.config(text="Playlist download complete.")

        threading.Thread(target=worker, daemon=True).start()

    def download_single_video(self):
        url = self.single_url_entry.get().strip()
        if not url.startswith("http"):
            messagebox.showerror("Invalid URL", "Please enter a valid video URL.")
            return

        self.status_label.config(text="Downloading single video...")

        def worker():
            ydl_opts = {
                "outtmpl": str(self.download_path / "%(title).200s.%(ext)s"),
                "format": "bestvideo+bestaudio/best",
                "ignoreerrors": True,
                "no_warnings": True,
                "noprogress": False,
                "restrictfilenames": True,
                "merge_output_format": "mp4",
            }
            with YoutubeDL(ydl_opts) as ydl:
                try:
                    ydl.download([url])
                    self.status_label.config(text="Single video download complete.")
                    messagebox.showinfo("Success", "Video downloaded successfully.")
                except Exception as e:
                    self.status_label.config(text="Download failed.")
                    messagebox.showerror("Error", str(e))

        threading.Thread(target=worker, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()
