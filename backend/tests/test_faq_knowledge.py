"""
Tests for the FAQ knowledge base keyword matching service.
"""
from services.faq_knowledge import faq_knowledge


def test_matches_restroom_query():
    context = faq_knowledge.get_relevant_context("where is the restroom")
    assert "Restrooms" in context


def test_matches_parking_query():
    context = faq_knowledge.get_relevant_context("where can I park")
    assert "Parking" in context or "No specific FAQ match" in context


def test_no_match_returns_generic_fallback():
    context = faq_knowledge.get_relevant_context("what is the meaning of life")
    assert "No specific FAQ match" in context


def test_matches_multiple_keywords():
    context = faq_knowledge.get_relevant_context("food and wifi info please")
    assert "Concessions" in context
    assert "Wi-Fi" in context
