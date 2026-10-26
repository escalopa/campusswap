import pytest

from campusswap_bot.db import Database


@pytest.fixture
def db(tmp_path):
    d = Database(tmp_path / "t.db")
    d.upsert_user(1, "alice", "Alice")
    d.set_building(1, "Building 1")
    d.upsert_user(2, "bob", "Bob")
    d.set_building(2, "Building 2")
    d.upsert_user(3, None, "Carol")
    d.set_building(3, "Building 1")
    yield d
    d.close()


def item(db, owner, title="Desk lamp", kind="free", price=None, category="Lamps & electronics"):
    return db.create_item(owner, title, category, "Good", kind, price, "Lobby", ["Today 18:00", "Tomorrow 12:00"], None)


def test_item_roundtrip(db):
    it = item(db, 2, kind="sell", price=150)
    got = db.get_item(it.id)
    assert got.title == "Desk lamp" and got.price == 150 and got.slots == ["Today 18:00", "Tomorrow 12:00"]
    assert got.status == "active"


def test_browse_excludes_own_and_puts_my_building_first(db):
    item(db, 2, "Kettle")       # other building
    item(db, 3, "Hangers")      # same building as Alice
    item(db, 1, "Alice's own")  # own item
    titles = [i.title for i in db.browse_items(1, "Building 1", None, False)]
    assert titles == ["Hangers", "Kettle"]


def test_browse_filters(db):
    item(db, 2, "Kettle", kind="sell", price=100, category="Kitchen")
    item(db, 2, "Pan", category="Kitchen")
    item(db, 2, "Lamp")
    assert [i.title for i in db.browse_items(1, "Building 1", "Kitchen", False)] == ["Pan", "Kettle"]
    assert [i.title for i in db.browse_items(1, "Building 1", "Kitchen", True)] == ["Pan"]


def test_request_flow_and_stats(db):
    it = item(db, 2)
    req = db.create_request(it.id, 1, "Today 18:00")
    assert db.open_request(it.id, 1).id == req.id
    db.set_request_status(req.id, "accepted")
    db.set_item_status(it.id, "reserved")
    assert db.browse_items(3, "Building 1", None, False) == []  # reserved items are hidden
    db.set_request_status(req.id, "completed")
    db.set_item_status(it.id, "given")
    assert db.open_request(it.id, 1) is None
    assert db.add_rating(req.id, 1, 2, 5) is True
    assert db.add_rating(req.id, 1, 2, 4) is False  # one rating per person per exchange
    bob = db.stats(2)
    assert bob.rating == 5.0 and bob.rating_count == 1 and bob.given == 1
    assert db.stats(1).received == 1


def test_items_of_hides_removed(db):
    a = item(db, 2, "A")
    item(db, 2, "B")
    db.set_item_status(a.id, "removed")
    assert [i.title for i in db.items_of(2)] == ["B"]
