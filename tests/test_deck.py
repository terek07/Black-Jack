from engine.deck import Deck


def test_deck_create_has_52_unique_cards():
    d = Deck()
    assert len(d.cards) == 52
    names = [c.name for c in d.cards]
    assert len(set(names)) == 52


def test_draw_reduces_count_and_returns_card():
    d = Deck()
    n = len(d.cards)
    card = d.draw()
    assert len(d.cards) == n - 1
    assert hasattr(card, "name") and hasattr(card, "value")


def test_all_expected_ranks_and_suits_present():
    d = Deck()
    names = [c.name for c in d.cards]
    # check suits
    assert any("Hearts" in n for n in names)
    assert any("Diamonds" in n for n in names)
    assert any("Clubs" in n for n in names)
    assert any("Spades" in n for n in names)
    # check a few ranks
    assert any("Ace" in n for n in names)
    assert any("King" in n for n in names)
    assert any("Queen" in n for n in names)
    assert any("Jack" in n for n in names)
    assert any("10 of" in n for n in names)

