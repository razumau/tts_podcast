import os
from dataclasses import dataclass
from datetime import datetime
import boto3
from feedgen.feed import FeedGenerator
import pytz
from botocore.exceptions import ClientError
import feedparser

from dotenv import load_dotenv

load_dotenv()


@dataclass
class PodcastInfo:
    title: str
    description: str
    author: str
    url: str
    language: str = "en"
    explicit: str = "no"
    category: str = "Technology"


@dataclass
class R2Settings:
    bucket_name: str
    account_id: str
    aws_access_key_id: str
    aws_secret_access_key: str
    url: str


class PodcastFeed:
    def __init__(self, r2_settings: R2Settings, podcast_info: PodcastInfo):
        self.r2 = r2_settings
        self.podcast_info = podcast_info
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=f"https://{self.r2.account_id}.r2.cloudflarestorage.com",
            aws_access_key_id=self.r2.aws_access_key_id,
            aws_secret_access_key=self.r2.aws_secret_access_key,
        )
        self.fg = FeedGenerator()
        self.setup_feed()
        self.load_existing_episodes()

    def setup_feed(self):
        self.fg.load_extension("podcast")
        self.fg.title(self.podcast_info.title)
        self.fg.description(self.podcast_info.description)
        self.fg.link(href=self.podcast_info.url, rel="alternate")
        self.fg.language(self.podcast_info.language)
        self.fg.author({"name": self.podcast_info.author})

        self.fg.podcast.itunes_author(self.podcast_info.author)
        self.fg.podcast.itunes_summary(self.podcast_info.description)
        self.fg.podcast.itunes_explicit(self.podcast_info.explicit)
        self.fg.podcast.itunes_category(self.podcast_info.category)

    def load_existing_episodes(self):
        try:
            self.s3_client.download_file(
                self.r2.bucket_name, "feed.xml", "existing_feed.xml"
            )
            existing_feed = feedparser.parse("existing_feed.xml")

            for entry in existing_feed.entries:
                fe = self.fg.add_entry()
                fe.id(entry.id)
                fe.title(entry.title)
                fe.description(
                    entry.description if "description" in entry else entry.title
                )

                if "enclosures" in entry and entry.enclosures:
                    enclosure = entry.enclosures[0]
                    fe.enclosure(enclosure.href, enclosure.length, enclosure.type)

                if "published_parsed" in entry:
                    published_date = datetime(
                        *entry.published_parsed[:6], tzinfo=pytz.UTC
                    )
                    fe.published(published_date)

            os.remove("existing_feed.xml")
        except ClientError:
            pass

    def list_audio_files(self):
        response = self.s3_client.list_objects_v2(
            Bucket=self.r2.bucket_name, Prefix="audio/"
        )

        audio_files = []
        if "Contents" in response:
            for obj in response["Contents"]:
                audio_files.append(
                    {
                        "key": obj["Key"],
                        "size": obj["Size"],
                        "last_modified": obj["LastModified"],
                    }
                )
        return audio_files

    @staticmethod
    def sanitize_filename(filename):
        base = os.path.splitext(filename)[0]
        ext = os.path.splitext(filename)[1]

        safe_name = base.lower()
        safe_name = "".join(c if c.isalnum() else "-" for c in safe_name)
        safe_name = "-".join(filter(None, safe_name.split("-")))

        return safe_name + ext

    def upload_audio(self, file_path):
        original_filename = os.path.basename(file_path)
        safe_filename = self.sanitize_filename(original_filename)

        self.s3_client.upload_file(
            file_path,
            self.r2.bucket_name,
            f"audio/{safe_filename}",
        )
        return f"{self.r2.url}/audio/{safe_filename}"

    def add_episode(self, audio_file, title, description=None):
        audio_url = self.upload_audio(audio_file)
        description = description or title
        file_size = os.path.getsize(audio_file)

        for entry in self.fg.entry():
            if entry.id() == audio_url:
                print(f"Episode {title} already exists in the feed")
                return

        fe = self.fg.add_entry()
        fe.id(audio_url)
        fe.title(title)
        fe.description(description)
        fe.enclosure(audio_url, str(file_size), "audio/mpeg")
        fe.published(datetime.now(pytz.UTC))

    def regenerate_feed(self, output_path="feed.xml"):
        self.fg.rss_file(output_path, pretty=True)

        self.s3_client.upload_file(output_path, self.r2.bucket_name, "feed.xml")


def add_episode(audio_file, title, description=None):
    podcast_info = PodcastInfo(
        title=os.getenv("PODCAST_TITLE"),
        description=os.getenv("PODCAST_DESCRIPTION"),
        author=os.getenv("PODCAST_AUTHOR"),
        url=os.getenv("PODCAST_URL"),
        language=os.getenv("PODCAST_LANGUAGE"),
        explicit=os.getenv("PODCAST_EXPLICIT", "no"),
        category=os.getenv("PODCAST_CATEGORY", "Technology"),
    )
    r2_settings = R2Settings(
        bucket_name=os.getenv("BUCKET_NAME"),
        account_id=os.getenv("R2_ACCOUNT_ID"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        url=os.getenv("R2_URL"),
    )

    feed = PodcastFeed(r2_settings, podcast_info)

    feed.add_episode(audio_file, title, description)
    feed.regenerate_feed()
