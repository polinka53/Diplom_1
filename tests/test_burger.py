from unittest.mock import Mock

import pytest

from praktikum.bun import Bun
from praktikum.burger import Burger
from praktikum.ingredient import Ingredient
from praktikum.ingredient_types import (
    INGREDIENT_TYPE_SAUCE,
    INGREDIENT_TYPE_FILLING,
)


def create_sample_burger() -> Burger:
    burger = Burger()
    bun = Bun("white bun", 200)
    burger.set_buns(bun)

    sauce = Ingredient(INGREDIENT_TYPE_SAUCE, "hot sauce", 50)
    filling = Ingredient(INGREDIENT_TYPE_FILLING, "cutlet", 80)

    burger.add_ingredient(sauce)
    burger.add_ingredient(filling)

    return burger


def test_burger_initial_state():
    burger = Burger()

    assert burger.bun is None
    assert burger.ingredients == []


def test_set_buns_sets_bun():
    burger = Burger()
    bun = Bun("black bun", 100)

    burger.set_buns(bun)

    assert burger.bun is bun


def test_add_ingredient_appends_to_list():
    burger = Burger()
    burger.set_buns(Bun("black bun", 100))
    ingredient = Ingredient(INGREDIENT_TYPE_SAUCE, "hot sauce", 50)

    burger.add_ingredient(ingredient)

    assert burger.ingredients == [ingredient]


def test_remove_ingredient_by_index():
    burger = create_sample_burger()
    assert len(burger.ingredients) == 2

    burger.remove_ingredient(0)

    assert len(burger.ingredients) == 1
    assert burger.ingredients[0].get_name() == "cutlet"


def test_move_ingredient_changes_order():
    burger = create_sample_burger()
    names_before = [i.get_name() for i in burger.ingredients]
    assert names_before == ["hot sauce", "cutlet"]

    burger.move_ingredient(0, 1)

    names_after = [i.get_name() for i in burger.ingredients]
    assert names_after == ["cutlet", "hot sauce"]


@pytest.mark.parametrize(
    "bun_price, ingredient_prices, expected_total",
    [
        (100, [], 200),
        (100, [50], 250),
        (100, [50, 20], 270),
        (150, [10, 15], 325),
    ],
)
def test_get_price_calculates_sum(bun_price, ingredient_prices, expected_total):
    burger = Burger()
    bun = Bun("test bun", bun_price)
    burger.set_buns(bun)

    for idx, price in enumerate(ingredient_prices):
        ingredient = Ingredient(INGREDIENT_TYPE_SAUCE, f"sauce-{idx}", price)
        burger.add_ingredient(ingredient)

    assert burger.get_price() == expected_total


def test_get_price_uses_mocks_for_bun_and_ingredients():
    burger = Burger()

    bun_mock = Mock()
    bun_mock.get_price.return_value = 100
    burger.set_buns(bun_mock)

    ingredient1 = Mock()
    ingredient1.get_price.return_value = 20
    ingredient2 = Mock()
    ingredient2.get_price.return_value = 30

    burger.add_ingredient(ingredient1)
    burger.add_ingredient(ingredient2)

    total = burger.get_price()

    assert total == 100 * 2 + 20 + 30
    assert bun_mock.get_price.call_count >= 1
    assert ingredient1.get_price.called
    assert ingredient2.get_price.called


def test_get_receipt_has_correct_format_and_data():
    burger = create_sample_burger()

    receipt = burger.get_receipt()
    lines = receipt.split("\n")

    assert lines[0] == "(==== white bun ====)"

    assert lines[1] == "= sauce hot sauce ="
    assert lines[2] == "= filling cutlet ="

    assert lines[3] == "(==== white bun ====)"

    price_line = [line for line in lines if line][-1]
    assert price_line.startswith("Price: ")

    price_in_receipt = float(price_line.split("Price: ")[1])
    assert price_in_receipt == burger.get_price()


def test_get_receipt_uses_mocks_for_text_generation():
    burger = Burger()

    bun_mock = Mock()
    bun_mock.get_name.return_value = "mock bun"
    bun_mock.get_price.return_value = 50
    burger.set_buns(bun_mock)

    ingredient_mock = Mock()
    ingredient_mock.get_type.return_value = INGREDIENT_TYPE_FILLING
    ingredient_mock.get_name.return_value = "mock filling"
    ingredient_mock.get_price.return_value = 25

    burger.add_ingredient(ingredient_mock)

    receipt = burger.get_receipt()

    assert "(==== mock bun ====)" in receipt
    assert "= filling mock filling =" in receipt
    assert "Price: " in receipt

    bun_mock.get_name.assert_called()
    ingredient_mock.get_type.assert_called()
    ingredient_mock.get_name.assert_called()