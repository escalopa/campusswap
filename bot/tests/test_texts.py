from campusswap_bot import texts
from campusswap_bot.db import Item, Stats, User


def test_university_email():
    domains = ["uni.edu"]
    assert texts.valid_university_email("a.helaly@uni.edu", domains)
    assert texts.valid_university_email("x@mail.uni.edu", domains)
    assert not texts.valid_university_email("x@gmail.com", domains)
    assert not texts.valid_university_email("x@evil-uni.edu", domains)
    assert not texts.valid_university_email("not an email", domains)


def test_parse_slots():
    assert texts.parse_slots("Today 18:00, Tomorrow 12:00 ,", 4) == ["Today 18:00", "Tomorrow 12:00"]
    assert texts.parse_slots("", 4) is None
    assert texts.parse_slots("a,b,c,d,e", 4) is None
    assert texts.parse_slots("x" * 41, 4) is None


def test_parse_price():
    assert texts.parse_price("150") == 150
    assert texts.parse_price("1 500 ₽") == 1500
    assert texts.parse_price("0") is None
    assert texts.parse_price("abc") is None


def test_caption_escapes_html():
    it = Item(1, 2, "<b>Lamp</b>", "Lamps", "Good", "sell", 150, "Lobby & stairs", ["Today"], None, "active")
    owner = User(2, "bob", "Bob <3", "Building 2", None)
    text = texts.item_caption(it, owner, Stats(4.5, 2, 1, 0), position="1 of 3")
    assert "&lt;b&gt;Lamp&lt;/b&gt;" in text
    assert "Bob &lt;3" in text and "Lobby &amp; stairs" in text
    assert "150 ₽" in text and "⭐ 4.5 (2)" in text and "1 of 3" in text
