from download_instagram_posts import InstagramDownloader
import sqlalchemy

def test_connect_engine(instagram_downloader: InstagramDownloader) -> object:

    instagram_test_tablename = "INSTAGRAM_TEST_TABLE"
    instagram_downloader.tablename = instagram_test_tablename
    lines_to_save = instagram_downloader.store_all_posts_in_db()

    # check if posts are all there
    testtable = sqlalchemy.Table(instagram_test_tablename)
    assert testtable.count == lines_to_save
