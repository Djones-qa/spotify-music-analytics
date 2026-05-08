"""Smoke tests for query helpers."""
import os
import sys
import pytest

# Make src importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from generate_data import generate_database
from queries import (
    streams_by_genre,
    top_tracks,
    audio_features_by_genre,
    mood_distribution,
    release_trend,
    platform_stats,
    top_artists,
    kpi_summary,
)

DB = os.path.join(os.path.dirname(__file__), '..', 'data', 'test_spotify.db')


@pytest.fixture(scope='module', autouse=True)
def db():
    generate_database(DB, n_tracks=200)
    yield
    if os.path.exists(DB):
        os.remove(DB)


def test_streams_by_genre():
    df = streams_by_genre(DB)
    assert not df.empty
    assert 'genre' in df.columns
    assert 'total_streams_m' in df.columns


def test_top_tracks():
    df = top_tracks(DB, limit=5)
    assert len(df) <= 5
    assert 'title' in df.columns


def test_audio_features_by_genre():
    df = audio_features_by_genre(DB)
    assert not df.empty
    for col in ['danceability', 'energy', 'valence']:
        assert col in df.columns


def test_mood_distribution():
    df = mood_distribution(DB)
    assert not df.empty
    assert 'mood' in df.columns


def test_release_trend():
    df = release_trend(DB)
    assert not df.empty
    assert 'year' in df.columns


def test_platform_stats():
    df = platform_stats(DB)
    assert not df.empty
    assert 'platform' in df.columns


def test_top_artists():
    df = top_artists(DB, limit=5)
    assert len(df) <= 5
    assert 'name' in df.columns


def test_kpi_summary():
    k = kpi_summary(DB)
    assert k['total_tracks'] > 0
    assert k['total_streams_b'] > 0
    assert k['total_artists'] > 0
    assert 0 <= k['avg_danceability'] <= 1
    assert 0 <= k['avg_energy'] <= 1
    assert 0 <= k['explicit_pct'] <= 100
