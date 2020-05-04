import random
from base_of_data import DataBase_for_bot


class Video_Corona:

    base = DataBase_for_bot()

    def __init__(self):
        self.video_base = self.base.video_collection

    @staticmethod
    def download_videos_from_file() -> list:
        with open("link_to_corona_video.txt") as videos:
            return videos.readlines()

    def find_the_videos(self) -> list:
        my_list = []
        for entry in self.base.finding():
            if "corona_videos" in entry.keys():
                return my_list + entry["corona_videos"]
        return my_list

    def check_sameness_videos(self) -> list:
        return self.download_videos_from_file() + self.find_the_videos()

    def replace_base_of_videos(self):
        self.base.dropping()
        self.base.inserting({"corona_videos": self.check_sameness_videos()})

    def take_video(self) -> str:
        corona_videos = self.find_the_videos()
        return corona_videos[random.randint(0, len(corona_videos) - 1)]

    def show_me_video(self):
        return self.take_video()
