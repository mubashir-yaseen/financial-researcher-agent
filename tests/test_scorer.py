import pytest
from scorer import CredibilityScorer

def test_credibility_scorer():
    assert CredibilityScorer.score_domain('https://psx.com.pk/report') == 0.95
    assert CredibilityScorer.score_domain('http://dawn.com/news') == 0.85
    assert CredibilityScorer.score_domain('https://randomblog.com') == 0.60
    assert CredibilityScorer.score_domain('https://twitter.com/user') == 0.40

def test_recency_scorer():
    # Based on our simple regex
    assert CredibilityScorer.score_recency('Something happened today') == 0.95
    assert CredibilityScorer.score_recency('This was reported 2 days ago') == 0.95
    assert CredibilityScorer.score_recency('An old report') == 0.70
