import datetime
import os
from typing import List
import pandas as pd
from InstagramAPI import InstagramAPI
from dotenv import load_dotenv
import tenacity
import logging
import sqlalchemy
from typing import NamedTuple


InstagramCrawled = NamedTuple('InstagramCrawled', [('taken_at', datetime.datetime),
                                                   ('comment_count', int),
                                                   ('url_main', str),
                                                   ('url_small', str),
                                                   ('longitude', float),
                                                   ('latitude', float),
                                                   ('caption_text', str),
                                                   ('like_count', int),
                                                   ('top_likers', str),
                                                   ('boosted_status', bool),
                                                   ('organic_tracking_token', str),
                                                   ('media_id', str),
                                                    ])

class NotLoggedInException(Exception):
    pass

class InstagramDownloader(object):

    def __init__(self):

        self.logger = logging.getLogger(__name__)
        self.tablename = "INSTAGRAM_POSTS"

        if os.environ.get('brasa_instagram_login') is None or os.environ.get('brasa_instagram_password') is None:
            # Read locally
            load_dotenv() # loads env files from .env

            self.logger.info("Brasa login {}".format(os.environ.get('brasa_instagram_login')))
            self.api = InstagramAPI(os.environ['brasa_instagram_login'], os.environ['brasa_instagram_password'])
            self.login()
            self.engine = None

    @tenacity.retry(wait=tenacity.wait_fixed(10),
                    stop=tenacity.stop_after_delay(60),
                    retry=(tenacity.retry_if_exception_type(NotLoggedInException)))
    def login(self) -> bool:

        self.api.login()
        if not self.api.isLoggedIn:
            raise NotLoggedInException('User not logged in! Retrying...')

        return True


    def get_total_posts(self) -> int:
        self.api.getUsernameInfo(self.api.username_id)
        n_media = self.api.LastJson['user']['media_count']
        return n_media

    def get_all_posts(self) -> List:

        self.api.getSelfUserFeed(maxid="")
        list_posts = self.api.LastJson['items']

        while self.api.LastJson['more_available']:
            self.api.getSelfUserFeed(maxid=self.api.LastJson['next_max_id'])
            list_posts.extend(self.api.LastJson['items'])

        return list_posts

    def store_all_posts_in_db(self):

        posts_df = []
        list_posts = self.get_all_posts()
        for j in list_posts:
            posts_df.append(self.build_df(j))

        df = pd.DataFrame.from_records(posts_df)
        self.logger.info("Data frame has {} rows".format(df.shape[0]))

        self.store_df_in_postgres(df)
        self.logger.info("Stored data frame in db")

        return df.shape[0]

    def get_likers_media(self):
        pass

    def build_df(self, item: dict) -> InstagramCrawled:

        crawled_dict = {
            'taken_at':datetime.datetime.fromtimestamp(item['taken_at']),
            'comment_count': item['comment_count'],
            'url_main': item['image_versions2']['candidates'][0]['url'],
            'url_small':item['image_versions2']['candidates'][1]['url'],
            'longitude': item['location']['lng'],
            'latitude':item['location']['lat'],
            'caption_text':item['caption']['text'],
            'like_count': item['like_count'],
            'top_likers': item['top_likers'],
            'boosted_status':item['boosted_status'],
            'organic_tracking_token':item['organic_tracking_token'],
            'media_id': item['caption']['media_id']
        }

        return crawled_dict

    def get_all_comments_from_media(self, media_id):
        pass

    def build_engine_if_not_present(self):

        if self.engine is None:
            self.engine = sqlalchemy.create_engine(os.environ.get('DATABASE_URL'))

    def store_df_in_postgres(self, df):
        """
        Crawls all data from Instagram and stores everything into table (replaces entire table).
        :param df:
        :param engine:
        :return:
        """

        self.build_engine_if_not_present()

        with self.engine.connect() as con:
            df.to_sql(InstagramDownloader.instagram_tablename, index=False, con=con, if_exists='replace')