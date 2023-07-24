'''Copyright © Ayush Kumar Bar. All rights reserved.
     
    This content, including but not limited to text, images, audio, and video, is the intellectual property of Ayush Kumar Bar. It is protected by copyright laws and international treaties. 
    Unauthorized reproduction, distribution, or modification of this content, in part or in whole, is strictly prohibited. 
    For inquiries or permissions, please contact ayushbar143@gmail.com.
'''

from PIL import Image, ImageTk
from concurrent.futures import ThreadPoolExecutor
from pytube import YouTube, Playlist
from tkinter import filedialog
import tkinter as tk
from threading import Thread
import os,sys


def download_video(url, folder):
    try:
        def on_progress(stream, chunk, bytes_remaining):
            file_size = stream.filesize
            bytes_downloaded = file_size - bytes_remaining
            percentage = (bytes_downloaded / file_size) * 100
            progress_label.config(text=f"Downloading: {percentage:.2f}%")

        yt = YouTube(url, on_progress_callback=on_progress)

        ultra_hd_streams = yt.streams.filter(
            progressive=True, file_extension='mp4', resolution='2160p').order_by('resolution').desc()
        if ultra_hd_streams:
            stream = ultra_hd_streams.first()
        else:
            hd_streams = yt.streams.filter(
                progressive=True, file_extension='mp4', resolution='1080p').order_by('resolution').desc()
            if hd_streams:
                stream = hd_streams.first()
            else:
                stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by(
                    'resolution').desc().first()

        download_path = os.path.join(folder, yt.title + '.mp4')

        status_label.config(text="Downloading...")
        stream.download(folder)

        url_entry.delete(0, tk.END)
        status_label.config(text="Download Completed!")
    except Exception as e:
        status_label.config(text="Error: " + str(e))


def download_playlist(playlist_url, folder):
    try:
        playlist = Playlist(playlist_url)
        playlist_title = playlist.title

        # Create a subfolder for the playlist
        playlist_folder = os.path.join(folder, playlist_title)
        os.makedirs(playlist_folder, exist_ok=True)

        playlist_name.config(text=f"Downloading: {playlist_title}")

        # Divide the playlist video URLs into four equal segments
        num_threads = 4
        videos_per_thread = len(playlist.video_urls) // num_threads
        video_segments = [playlist.video_urls[i:i + videos_per_thread]
                          for i in range(0, len(playlist.video_urls), videos_per_thread)]

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            for segment in video_segments:
                for url in segment:
                    executor.submit(download_video, url, playlist_folder)

        status_label.config(text="Playlist Download Completed!")
    except Exception as e:
        status_label.config(text="Error: " + str(e))


def set_video_option():
    playlist_option_var.set(0)


def set_playlist_option():
    playlist_option_var.set(1)

# start download


def start_download():
    url = url_entry.get()
    folder = folder_path.get()

    if not url or not folder:
        status_label.config(
            text="Please enter a valid URL and select a folder.")
        return

    if url.startswith("https://www.youtube.com/playlist?"):
        download_thread = Thread(target=download_playlist, args=(url, folder))
    else:
        download_thread = Thread(target=download_video, args=(url, folder))

    download_thread.start()


def select_folder():
    folder_selected = filedialog.askdirectory()
    folder_path.set(folder_selected)


# Gets all the files
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


root = tk.Tk()
root.title("YouTube Downloader")
root.geometry("400x310")
root.resizable(False, False)
logo_path = resource_path("logo.ico")
root.iconbitmap(logo_path)


# Load and resize the YouTube logo
logo_img = Image.open(logo_path)
logo_img = logo_img.resize((40, 40), Image.ANTIALIAS)
youtube_logo = ImageTk.PhotoImage(logo_img)

# YouTube logo Label and Header side by side
logo_header_frame = tk.Frame(root)
logo_header_frame.pack()
# YouTube logo Label
youtube_logo_label = tk.Label(logo_header_frame, image=youtube_logo)
youtube_logo_label.pack(side="left", padx=2, pady=10)

# Header
header_label = tk.Label(
    logo_header_frame, text="YouTube Downloader", font=("Helvetica", 16, "bold"))
header_label.pack(side="left", padx=2, pady=10)


# Playlist Option
playlist_option_var = tk.IntVar()
playlist_option_var.set(0)  # Default to single video download

playlist_option_label = tk.Label(root, text="Select Download Type:", fg="red",
                                 font=("Helvetica", 11))
playlist_option_label.pack(pady=5)

# Place radio buttons side by side horizontally
radio_frame = tk.Frame(root)
radio_frame.pack()

single_video_radio = tk.Radiobutton(
    radio_frame, text="Single Video", variable=playlist_option_var, value=0, fg="blue",
    font=("Helvetica", 10))
single_video_radio.pack(side="left", padx=10)
playlist_radio = tk.Radiobutton(
    radio_frame, text="Playlist", variable=playlist_option_var, value=1, fg="green",
    font=("Helvetica", 10))
playlist_radio.pack(side="left", padx=10)

# URL Entry
url_label = tk.Label(root, text="Enter YouTube URL:", fg="black",
                     font=("Helvetica", 10))
url_label.pack()
url_entry = tk.Entry(root, width=50, font=("Helvetica", 10))
url_entry.pack(pady=5)

# Folder Selection and Download Button side by side
folder_download_frame = tk.Frame(root)
folder_download_frame.pack()

# Folder Selection
folder_path = tk.StringVar()
folder_button = tk.Button(folder_download_frame, text="Select Folder", command=select_folder,
                          bg="gray", fg="white", font=("Helvetica", 12, "bold"))
folder_button.pack(side="left", pady=7, padx=10)

# Download Button
download_button = tk.Button(folder_download_frame, text="  Download  ", command=start_download,
                            bg="green", fg="white", font=("Helvetica", 12, "bold"))
download_button.pack(side="left", pady=7, padx=10)

# # Status Label
playlist_name = tk.Label(root, text="", fg="green",
                         font=("Helvetica", 10))
playlist_name.pack(pady=5, expand=True)

# Progress Label
progress_label = tk.Label(root, text="", fg="green",
                          font=("Helvetica", 12, "italic"))
progress_label.pack()

# Status Label
status_label = tk.Label(root, text="", fg="blue",
                        font=("Helvetica", 12, "bold"))
status_label.pack(pady=5)

root.mainloop()
