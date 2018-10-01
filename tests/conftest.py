import pytest

from download_instagram_posts import InstagramDownloader


@pytest.fixture(scope='module')
def instagram_downloader() -> InstagramDownloader:
    return InstagramDownloader()
