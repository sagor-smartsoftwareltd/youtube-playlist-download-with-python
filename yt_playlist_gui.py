import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
import subprocess
from pathlib import Path
import re
import time
import json

class YouTubePlaylistDownloaderAdvanced:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Playlist Downloader (Best Quality)")
        self.root.geometry("750x480")

        self.download_path = Path.home() / "Downloads" / "downloads"

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

        ttk.Label(self.main_frame, text="Playlist URL:").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.playlist_url_entry = ttk.Entry(self.main_frame, width=60)
        self.playlist_url_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        self.fetch_button = ttk.Button(self.main_frame, text="Fetch Videos", command=self.fetch_playlist)
        self.fetch_button.grid(row=0, column=2, padx=5, pady=10)

        self.video_list_frame = ttk.LabelFrame(self.main_frame, text="Playlist Videos")
        self.video_list_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        self.video_listbox = tk.Listbox(self.video_list_frame, height=15)
        self.video_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ttk.Scrollbar(self.video_list_frame, orient="vertical", command=self.video_listbox.yview).pack(side=tk.RIGHT, fill="y")
        self.video_listbox.config(yscrollcommand=self.video_listbox.yview)

        self.download_frame = ttk.LabelFrame(self.main_frame, text="Download Controls")
        self.download_frame.grid(row=2, column=0, columnspan=3, padx=5, pady=10, sticky="ew")
        self.download_frame.columnconfigure(0, weight=1)

        self.download_all_button = ttk.Button(self.download_frame, text=f"Download All to {self.download_path}", command=self.download_all_videos)
        self.download_all_button.grid(row=0, column=0, pady=10, padx=10)
        self.progress_bar = ttk.Progressbar(self.download_frame, orient="horizontal", mode="determinate")
        self.progress_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        self.download_status_label = ttk.Label(self.download_frame, text="Ready. Fetch a playlist to begin.")
        self.download_status_label.grid(row=2, column=0, pady=5)

        self.playlist_videos = []

    def fetch_playlist(self):
        url = self.playlist_url_entry.get().strip()

        if not re.match(r"https?://(www\.)?youtube\.com/playlist\?list=[\w-]+", url):
            messagebox.showerror("Invalid URL", "Please enter a valid YouTube playlist URL.")
            return

        self.download_status_label.config(text="Fetching playlist videos...")
        self.root.update_idletasks()

        try:
            # Use yt-dlp to fetch playlist metadata
            result = subprocess.run([
                "yt-dlp",
                "--flat-playlist",
                "--dump-single-json",
                "--no-warnings",
                url
            ], capture_output=True, text=True, check=True)

            playlist_data = json.loads(result.stdout)
            entries = playlist_data.get("entries", [])

            self.video_listbox.delete(0, tk.END)
            self.playlist_videos = []

            for idx, entry in enumerate(entries, start=1):
                try:
                    title = entry.get("title", "[No Title]")
                    video_url = entry.get("url")
                    if not video_url:
                        raise ValueError("No URL found for video")
                    self.playlist_videos.append({"title": title, "url": video_url})
                    self.video_listbox.insert(tk.END, f"{idx}. {title}")
                except Exception as e:
                    print(f"Error processing video {idx}: {str(e)}")
                    self.playlist_videos.append(None)
                    self.video_listbox.insert(tk.END, f"{idx}. [Unavailable: {str(e)}]")
                time.sleep(2)  # Increased delay to avoid rate-limiting

            self.download_status_label.config(text=f"Found {len(self.playlist_videos)} videos.")
            self.fetch_button_state(True)
        except subprocess.CalledProcessError as e:
            error_output = e.stderr if e.stderr else "Unknown error"
            print(f"Error fetching playlist: {error_output}")
            messagebox.showerror("Error", f"Failed to fetch playlist: {error_output}")
            self.download_status_label.config(text="Failed to fetch playlist.")
        except Exception as e:
            print(f"Error fetching playlist: {str(e)}")
            messagebox.showerror("Error", f"Failed to fetch playlist: {str(e)}")
            self.download_status_label.config(text="Failed to fetch playlist.")

    def download_all_videos(self):
        if not any(self.playlist_videos):
            messagebox.showerror("No Videos", "No valid videos to download. Fetch a valid playlist first.")
            return

        try:
            os.makedirs(self.download_path, exist_ok=True)
        except PermissionError:
            messagebox.showerror("Permission Error", f"Cannot write to {self.download_path}. Choose another directory.")
            return

        self.download_all_button.config(state=tk.DISABLED)
        self.fetch_button_state(False)
        self.progress_bar["value"] = 0
        self.progress_bar["maximum"] = len(self.playlist_videos)
        threading.Thread(target=self._download_thread, daemon=True).start()

    def _download_thread(self):
        for i, video in enumerate(self.playlist_videos):
            if video is None:
                self.video_listbox.itemconfig(i, bg="#ff8080", fg="white")
                self.progress_bar["value"] += 1
                continue

            try:
                title = video["title"]
                url = video["url"]
                sanitized = "".join(c for c in title if c.isalnum() or c in (" ", ".", "_")).rstrip()
                out_fp = self.download_path / f"{sanitized}.mp4"
                self.update_status(f"({i+1}/{len(self.playlist_videos)}) Downloading: {title}")

                # Use yt-dlp to download the best video and audio
                subprocess.run([
                    "yt-dlp",
                    "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
                    "-o", str(out_fp),
                    url
                ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

                self.progress_bar["value"] += 1
                self.video_listbox.itemconfig(i, bg="#90EE90", fg="black")  # Mark successful download in green

            except subprocess.CalledProcessError as e:
                error_output = e.stderr.decode() if e.stderr else "Unknown error"
                self.video_listbox.itemconfig(i, bg="#ff8080", fg="white")
                print(f"Error on [{i+1}] '{title}': {error_output}")
                self.progress_bar["value"] += 1
            except Exception as e:
                self.video_listbox.itemconfig(i, bg="#ff8080", fg="white")
                print(f"Error on [{i+1}] '{title}': {str(e)}")
                self.progress_bar["value"] += 1

        self.update_status(f"Completed! Files are in {self.download_path}")
        self.download_all_button.config(state=tk.NORMAL)
        self.fetch_button_state(True)
        messagebox.showinfo("All Done", f"All download attempts completed — check {self.download_path}")

    def fetch_button_state(self, enabled: bool):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.fetch_button.config(state=state)

    def update_status(self, message: str):
        self.download_status_label["text"] = message
        self.root.update_idletasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubePlaylistDownloaderAdvanced(root)
    root.mainloop()
