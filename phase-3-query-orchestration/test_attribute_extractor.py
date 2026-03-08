from attribute_extractor import _extract_expense_ratio
from retriever import RetrievedChunk


def make_chunk(text: str) -> RetrievedChunk:
    return RetrievedChunk(
        text=text,
        scheme_id="dummy",
        scheme_name="Dummy Scheme",
        attribute_type="expense_ratio",
        source_url="https://example.com",
        score=1.0,
    )


def test_expense_ratio_variations():
    # Various formats to ensure regex captures correctly
    cases = [
        ("Expense Ratio: 1.23%", "expense ratio is 1.23%"),
        ("Expense Ratio - 2.5%", "expense ratio is 2.5%"),
        ("Expense Ratio of 0.75%", "expense ratio is 0.75%"),
        ("Expense Ratio 3%", "expense ratio is 3%"),
        ("Expense Ratio: 4.0", "expense ratio is 4.0%"),
    ]
    for text, expected in cases:
        chunk = make_chunk(text)
        result = _extract_expense_ratio([chunk])
        assert result == expected, f"Failed for {text}: got {result}"
