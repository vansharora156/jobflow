from app.sources.rss_source import RSSJobSource


def test_parse_title_with_colon():
    company, title = RSSJobSource._parse_title("PlanetScale: Developer Educator")
    assert company == "PlanetScale"
    assert title == "Developer Educator"


def test_parse_title_without_colon():
    company, title = RSSJobSource._parse_title("Software Engineer")
    assert company == "Unknown"
    assert title == "Software Engineer"


def test_clean_html():
    html_text = "<p><strong>Headquarters:</strong> San Francisco</p>"
    cleaned = RSSJobSource._clean_html(html_text)
    assert "<p>" not in cleaned
    assert "San Francisco" in cleaned


def test_parse_date():
    date_str = "Wed, 19 Aug 2026 08:00:00 +0000"
    dt = RSSJobSource._parse_date(date_str)
    assert dt is not None
    assert dt.year == 2026
    assert dt.month == 8
    assert dt.day == 19
