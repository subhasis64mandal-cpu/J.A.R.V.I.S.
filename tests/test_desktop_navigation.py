from jarvis.desktop import APPROVED_SITES, list_approved_sites, open_approved_site, search_google


def test_approved_sites_are_fixed_endpoints() -> None:
    assert set(APPROVED_SITES) == {"github", "google", "wikipedia", "youtube"}
    assert all(site.url.startswith("https://") for site in APPROVED_SITES.values())


def test_list_approved_sites() -> None:
    assert list_approved_sites() == "github, google, wikipedia, youtube"


def test_invalid_site_is_rejected_before_launch() -> None:
    try:
        open_approved_site("example.com")
    except ValueError as exc:
        assert "allowlisted" in str(exc)
    else:
        raise AssertionError("Unapproved site should be rejected")


def test_empty_google_query_is_rejected() -> None:
    try:
        search_google("   ")
    except ValueError as exc:
        assert "cannot be empty" in str(exc)
    else:
        raise AssertionError("Empty Google query should be rejected")
