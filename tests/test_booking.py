from datetime import date, timedelta

import pytest
from playwright.sync_api import Page, expect


def test_successful_booking(page: Page, base_url: str):
    """Verify that booking is created successfully with valid form data."""
    booking_date = (date.today() + timedelta(days=1)).isoformat()

    response = page.goto(base_url, wait_until="domcontentloaded")
    assert response is not None and response.ok, "Demo page did not load successfully"

    page.locator("#room").select_option("small")
    page.locator("#date").fill(booking_date)
    page.locator("#start-time").fill("10:00")
    page.locator("#end-time").fill("11:00")
    page.locator("#participants").fill("2")
    page.locator("#name").fill("Ольга")
    page.locator("#email").fill("olga@example.com")

    page.get_by_role("button", name="Забронировать").click()

    status = page.locator("#form-status")
    expect(status).to_contain_text("Бронирование создано.")
    expect(status).to_contain_text(
        f"Малая, {booking_date}, 10:00–11:00 · Ольга"
    )


def test_invalid_booking(page: Page, base_url: str):
    """Verify that booking is rejected when number of participants exceed room capacity."""
    booking_date = (date.today() + timedelta(days=1)).isoformat()

    response = page.goto(base_url, wait_until="domcontentloaded")
    assert response is not None and response.ok, "Demo page did not load successfully"

    page.locator("#room").select_option("small")
    page.locator("#date").fill(booking_date)
    page.locator("#start-time").fill("10:00")
    page.locator("#end-time").fill("11:00")
    page.locator("#participants").fill("5")
    page.locator("#name").fill("Ольга")
    page.locator("#email").fill("olga@example.com")

    page.get_by_role("button", name="Забронировать").click()

    expect(page.locator('[data-error-for="participants"]')).to_have_text(
        "В комнате максимум 4 участника."
    )
    expect(page.locator("#participants")).to_have_css(
            "border-color", "rgb(186, 63, 63)"
        )
    expect(page.locator("#form-status")).to_have_text(
        "Проверьте, пожалуйста, заполнение формы."
    )
    expect(page.locator("#form-status")).not_to_contain_text("Бронирование создано.")


@pytest.mark.xfail(
    strict=True,
    reason="BUG-01: Booking longer than four hours is accepted",
    raises=AssertionError,
)
def test_discovered_defect(page: Page, base_url: str):
    """Verify that bookings longer than four hours are rejected."""
    booking_date = (date.today() + timedelta(days=1)).isoformat()

    response = page.goto(base_url, wait_until="domcontentloaded")
    assert response is not None and response.ok, "Demo page did not load successfully"

    page.locator("#room").select_option("medium")
    page.locator("#date").fill(booking_date)
    page.locator("#start-time").fill("10:30")
    page.locator("#end-time").fill("15:30")
    page.locator("#participants").fill("10")
    page.locator("#name").fill("Ольга")
    page.locator("#email").fill("olga@example.com")

    page.get_by_role("button", name="Забронировать").click()

    expect(page.locator('[data-error-for="endTime"]')).to_have_text(
        "Время окончания не может превышать время начала более чем на 4 часа."
    )
    expect(page.locator("#end-time")).to_have_css(
        "border-color", "rgb(186, 63, 63)"
    )
    expect(page.locator("#form-status")).to_have_text(
        "Проверьте, пожалуйста, заполнение формы."
    )
    expect(page.locator("#form-status")).not_to_contain_text("Бронирование создано.")
