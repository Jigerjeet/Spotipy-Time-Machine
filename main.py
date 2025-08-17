from tkinter import font
from selenium import webdriver
import time
from bs4 import BeautifulSoup
import re
from AppOpener import open
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import tkinter as tk

def update_status(message, color="white"):
    status_label.config(text=message, fg=color)
    root.update_idletasks()

def check():
    global input_user
    input_user=entry1.get()
    pattern = r"^[0-9]{4}-(((0[13578]|(10|12))-(0[1-9]|[1-2][0-9]|3[0-1]))|(02-(0[1-9]|[1-2][0-9]))|((0[469]|11)-(0[1-9]|[1-2][0-9]|30)))$"
    if re.match(pattern, input_user):
        update_status("Fetching Billboard data...", "yellow")
        entry1.delete(0,tk.END)
        billboard(input_user)
    else:
        update_status("❌ Invalid date format. Use YYYY-MM-DD.", "red")
        print("invalid input ")


def billboard(x):
    chrome_option = webdriver.ChromeOptions()
    chrome_option.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_option)
    driver.get("https://www.billboard.com/charts/hot-100/"+x)
    time.sleep(10)
    html = driver.page_source
    soup = BeautifulSoup(html,'html.parser')
    song_names_spans = soup.select("li ul li h3")
    songs=[song.getText().strip() for song in song_names_spans]
    if songs:
        update_status(f"Found {len(songs)} songs. Creating playlist...", "yellow")
        spotify(songs)
    else:
        update_status("⚠️ No songs found on Billboard for that date.", "red")


def spotify(x):
    client_id = "3bc5647679b344c0a99ed1abc9f3016f"
    client_secret = "f4ea658ac3334cefaa5bf6ed135b99f1"

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret,
                                                   redirect_uri="https://open.spotify.com/",
                                                   scope="playlist-modify-private"))


    user_id = sp.current_user()["id"]
    song_name = x
    song_uris = []
    for song in song_name:
        result = sp.search(q=f"track:{song} ", type="track")
        print(result)
        try:
            uri = result["tracks"]["items"][0]["uri"]
            song_uris.append(uri)
        except IndexError:
            print(f"{song} doesn't exist in Spotify. Skipped.")
    if not song_uris:
        print("No songs found on Spotify. Playlist not created.")
        return  # Exit early to avoid error

    playlist = sp.user_playlist_create(user=user_id, name=f"{input_user} songs", public=False)
    # print(playlist)

    sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)
    update_status("✅ Playlist created successfully!", "lightgreen")


root = tk.Tk()
root.title("🎶 Spotipy Time Machine")
root.geometry('400x350')
root.configure(bg="#1DB954")  # Spotify green

# Fonts
title_font = font.Font(family="Helvetica", size=16, weight="bold")
label_font = font.Font(family="Helvetica", size=12)
button_font = font.Font(family="Helvetica", size=10, weight="bold")

# Title Label
label1 = tk.Label(root, text="🎵 Welcome to Spotipy", bg="#1DB954", fg="white", font=title_font)
label1.pack(pady=(20, 5))

label_sub = tk.Label(root, text="Travel back in time with music!", bg="#1DB954", fg="white", font=label_font)
label_sub.pack(pady=(0, 15))

# Input Frame
input_frame = tk.Frame(root, bg="#1DB954")
input_frame.pack()

label2 = tk.Label(input_frame, text="Enter a date (YYYY-MM-DD):", bg="#1DB954", fg="white", font=label_font)
label2.pack()

entry1 = tk.Entry(input_frame, font=label_font, width=20, justify='center')
entry1.pack(pady=5)

# Button Frame
button_frame = tk.Frame(root, bg="#1DB954")
button_frame.pack(pady=20)

button1 = tk.Button(button_frame, text="🔍 Search Billboard", command=check, bg="white", fg="#1DB954", font=button_font, width=20)
button1.pack(pady=5)

button2 = tk.Button(button_frame, text="🎧 Open Spotify", command=lambda :open("Spotify"), bg="white", fg="#1DB954", font=button_font, width=20)
button2.pack(pady=5)

button3 = tk.Button(button_frame, text="❌ Exit", command=root.destroy, bg="white", fg="#1DB954", font=button_font, width=20)
button3.pack(pady=5)

# Status Label
status_label = tk.Label(root, text="", bg="#1DB954", fg="white", font=label_font)
status_label.pack(pady=(10, 0))


root.mainloop()