from src.domain.models.media_item import MediaItem

def test_media_item_creation():
    item = MediaItem(id="1", title="Inception", overview="Test", media_type="movie")
    assert item.title == "Inception"
