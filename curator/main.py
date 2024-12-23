import json
import csv
import os
import yt_dlp
import concurrent.futures
from datetime import datetime, timezone


class YouTubeFetcher:
    def __init__(self):
        self.block_cookie = True
        self.cookie_path = "data/youtube_cookie.txt"

    def convert_cookie(self):
        if not os.path.exists(self.cookie_path):
            open(self.cookie_path, "w").close()
            return False

        with open(self.cookie_path, "r", encoding="utf-8") as f:
            cookie = f.readlines()
        if not cookie:
            return False

        netscape_cookie = ["# Netscape HTTP Cookie File\n"]
        for line in cookie:
            fields = line.split("\t")
            if len(fields) < 7:
                continue
            name = fields[0]
            value = fields[1]
            domain = fields[2] if fields[2].startswith(".") else f".{fields[2]}"
            path = fields[3]
            expires = (
                "0"
                if fields[4] == "Session"
                else str(
                    int(
                        datetime.fromisoformat(fields[4])
                        .replace(tzinfo=timezone.utc)
                        .timestamp()
                    )
                )
            )
            http_only = "TRUE" if fields[6] == "✓" else "FALSE"
            netscape_cookie.append(
                f"{domain}\tTRUE\t{path}\t{http_only}\t{expires}\t{name}\t{value}\n"
            )

        with open(self.cookie_path, "w", encoding="utf-8") as f:
            f.writelines(netscape_cookie)
        return True

    def select_metadata(self, metadata):
        return {
            "id": metadata.get("id"),
            "title": metadata.get("track", metadata.get("title")),
            "album": metadata.get("album"),
            "release_year": metadata.get("release_year"),
            "thumbnail": metadata.get("thumbnail"),
            "url": metadata.get("original_url", metadata.get("webpage_url")),
            "tags": metadata.get("tags"),
            "artists": metadata.get("artists", metadata.get("creators")),
            "channel": metadata.get("channel", metadata.get("uploader")),
            "channel_id": metadata.get("channel_id", metadata.get("uploader_id")),
            "channel_url": metadata.get("channel_url", metadata.get("uploader_url")),
            "duration": metadata.get("duration"),
            "duration_string": metadata.get("duration_string"),
        }

    def fetch_metadata(self, url):
        url = url.split("&si=")[0] if "&si=" in url else url
        ydl_opts = {
            "simulate": True,
            "skip_download": True,
            "cookiefile": None if self.block_cookie else self.cookie_path,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                metadata = ydl.extract_info(url, download=False)
        except:
            return None

        data = []
        music_flag = "music.youtube.com" in url
        entries = metadata["entries"] if "list=" in url else [metadata]
        for entry in entries:
            selected_metadata = self.select_metadata(entry)
            if music_flag:
                selected_metadata["url"] = selected_metadata["url"].replace(
                    "https://www.youtube.com/", "https://music.youtube.com/"
                )
                selected_metadata["channel_url"] = selected_metadata[
                    "channel_url"
                ].replace("https://www.youtube.com/", "https://music.youtube.com/")
            data.append(selected_metadata)
        return data


class Collection:
    def __init__(self):
        self.collection = []

    def add(self, entry, overwrite=False):
        entry_id = entry["id"]
        for existing_entry in self.collection:
            if existing_entry["id"] == entry_id:
                if overwrite:
                    existing_entry.update(entry)
                    return True
                return False
        self.collection.append(entry)
        return True

    def get(self, id):
        for entry in self.collection:
            if entry["id"] == id:
                return entry
        return None

    def remove(self, id):
        entry = self.get(id)
        if entry:
            self.collection.remove(entry)
            return True
        return False

    def stringify(self):
        return json.dumps(self.collection, indent=4)

    def load(self, data):
        self.collection = json.loads(data)

    def clear(self):
        self.collection.clear()


class Curator:
    def __init__(self):
        self.collection = Collection()
        self.youtube = YouTubeFetcher()
        self.collection_path = "data/collection.json"
        self.urls_path = "data/urls.txt"

    def save(self):
        with open(self.collection_path, "w", encoding="utf-8") as f:
            f.write(self.collection.stringify())
        return True

    def load(self):
        if not os.path.exists(self.collection_path):
            return False
        with open(self.collection_path, "r", encoding="utf-8") as f:
            self.collection.load(f.read())
        return True

    def fetch_urls(self):
        data = []
        failed = []
        youtube_urls = []

        if not os.path.exists(self.urls_path):
            open(self.urls_path, "w").close()
            return False
        
        with open(self.urls_path, "r", encoding="utf-8") as f:
            urls = f.readlines()
        urls = [url.strip() for url in urls]

        for url in urls:
            if "youtube.com" in url:
                youtube_urls.append(url)
            else:
                failed.append(url)

        if self.youtube.block_cookie:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_to_url = {
                    executor.submit(self.youtube.fetch_metadata, url): url
                    for url in youtube_urls
                }
                for future in concurrent.futures.as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        metadata = future.result()
                        if metadata:
                            data.extend(metadata)
                        else:
                            failed.append(url)
                    except Exception:
                        failed.append(url)
        else:
            for url in youtube_urls:
                metadata = self.youtube.fetch_metadata(url)
                if not metadata:
                    failed.append(url)
                else:
                    data.extend(metadata)

        for entry in data:
            self.collection.add(entry)
        with open(self.urls_path, "w", encoding="utf-8") as f:
            f.write("\n".join(failed))
        return True

    def extract_urls(self):
        urls = []
        for entry in self.collection.collection:
            urls.append(entry["url"])
        with open(self.urls_path, "a", encoding="utf-8") as f:
            f.write("\n".join(urls))
