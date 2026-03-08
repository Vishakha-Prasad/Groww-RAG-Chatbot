import pytest
from attribute_extractor import (
    _extract_expense_ratio,
    _extract_exit_load,
    _extract_min_sip,
    _extract_min_lumpsum,
    _extract_lock_in,
    _extract_riskometer,
    _extract_benchmark,
    _extract_statement_download,
)
from retriever import RetrievedChunk


def make_chunk(text):
    return RetrievedChunk(
        text=text,
        scheme_id="dummy",
        scheme_name="Dummy Scheme",
        attribute_type="",
        source_url="https://example.com",
        score=1.0,
    )


def test_exit_load_variations():
    cases = [
        ("Exit Load: 0.5%", "Exit Load: 0.5%"),
        ("Exit Load - 1%", "Exit Load - 1%"),
        ("Exit Load 2%", "Exit Load 2%"),
    ]
    for txt, expected in cases:
        assert _extract_exit_load([make_chunk(txt)]) == expected


def test_min_sip_variations():
    cases = [
        ("Minimum SIP Investment is set to ₹100", "minimum SIP investment is ₹100."),
        ("Min. for SIP ₹200", "minimum SIP investment is ₹200."),
        ("SIP ₹300", "minimum SIP investment is ₹300."),
    ]
    for txt, expected in cases:
        assert _extract_min_sip([make_chunk(txt)]) == expected


def test_min_lumpsum_variations():
    cases = [
        ("Minimum Lumpsum Investment is set to ₹500", "minimum lumpsum investment is ₹500."),
        ("Min. for 1st investment ₹600", "minimum lumpsum investment is ₹600."),
        ("Lumpsum ₹700", "minimum lumpsum investment is ₹700."),
    ]
    for txt, expected in cases:
        assert _extract_min_lumpsum([make_chunk(txt)]) == expected


def test_lock_in_variations():
    cases = [
        ("5Y Lock-in", "5Y Lock-in"),
        ("Lock-in period: 3Y", "Lock-in period: 3Y"),
        ("lock-in 2Y", "lock-in 2Y"),
    ]
    for txt, expected in cases:
        assert _extract_lock_in([make_chunk(txt)]) == expected


def test_riskometer_variations():
    cases = [
        ("Very High Risk", "riskometer rating is Very High Risk."),
        ("Medium risk", "riskometer rating is Medium Risk."),
    ]
    for txt, expected in cases:
        assert _extract_riskometer([make_chunk(txt)]) == expected


def test_benchmark_variations():
    cases = [
        ("Benchmark Nifty 1D Rate TRI", "Benchmark Nifty 1D Rate TRI"),
        ("Fund benchmark NIFTY 50 Total Return Index", "Fund benchmark NIFTY 50 Total Return Index"),
        ("Benchmark: NIFTY 100", "NIFTY 100"),
    ]
    for txt, expected in cases:
        assert _extract_benchmark([make_chunk(txt)]) == expected


def test_statement_download():
    txt = "You can download statements from Groww via the app."
    result = _extract_statement_download([make_chunk(txt)])
    assert result is not None
    assert "statement" in result.lower() or "reports" in result.lower()


def test_statement_download_with_steps():
    txt = (
        "How to Download Mutual Fund Statements on Groww:\n"
        "1. Log in to your Groww account.\n"
        "2. Go to the 'You' (Profile) section.\n"
        "3. Click on 'Reports' or 'SIP & Reports'.\n"
        "4. For Transaction History: Choose 'Groww Balance Statement'."
    )
    result = _extract_statement_download([make_chunk(txt)])
    assert result is not None
    assert "Log in" in result
    assert "Profile" in result
