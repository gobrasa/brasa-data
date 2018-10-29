from download_instagram_posts import InstagramDownloader
import sqlalchemy
import json

def test_connect_engine(instagram_downloader: InstagramDownloader) -> object:

    instagram_test_tablename = "INSTAGRAM_POSTS"
    instagram_downloader.tablename = instagram_test_tablename
    list_posts = x = json.load(open('outputfile.json'))
    lines_to_save = instagram_downloader.store_all_posts_in_db(list_posts)

    # check if posts are all there
    testtable = sqlalchemy.Table(instagram_test_tablename)
    assert testtable.count == lines_to_save
