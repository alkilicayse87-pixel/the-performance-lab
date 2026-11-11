import pytest

from scripts import build_video_catalog


@pytest.fixture
def catalog_dependencies(monkeypatch, tmp_path):
    fetched = []
    deleted = []
    indexed = []

    def fake_fetch(video_id, languages):
        fetched.append(video_id)
        return {
            "video_id": video_id,
            "language": "English",
            "language_code": "en",
            "is_generated": False,
            "segments": [{"text": "Test transcript", "start": 0, "duration": 1}],
        }

    class FakeVectorStore:
        def delete(self, where):
            deleted.append(where["video_id"])

    def fake_add(video_id, chunks):
        indexed.append(video_id)
        return [f"{video_id}-chunk"]

    monkeypatch.setattr(build_video_catalog, "TRANSCRIPTS_DIR", tmp_path)
    monkeypatch.setattr(build_video_catalog, "fetch_youtube_transcript", fake_fetch)
    monkeypatch.setattr(build_video_catalog, "get_vector_store", FakeVectorStore)
    monkeypatch.setattr(build_video_catalog, "add_video_chunks", fake_add)
    return fetched, deleted, indexed, tmp_path


def test_selected_videos_leave_other_catalog_entries_untouched(catalog_dependencies):
    fetched, deleted, indexed, directory = catalog_dependencies
    selected = ["h2aWYjSA1Jc", "mLn2X2JSrbg", "RcGyVTAoXEU"]

    build_video_catalog.main(video_ids=selected)

    assert fetched == deleted == indexed == selected
    assert {path.stem for path in directory.glob("*.json")} == set(selected)


def test_unknown_video_is_rejected_before_updating_catalog(catalog_dependencies):
    fetched, deleted, indexed, _ = catalog_dependencies

    with pytest.raises(ValueError, match="Unknown video IDs"):
        build_video_catalog.main(video_ids=["unknown"])

    assert fetched == deleted == indexed == []


def test_default_build_still_refreshes_full_catalog(catalog_dependencies):
    fetched, deleted, indexed, _ = catalog_dependencies
    video_ids = [video["video_id"] for video in build_video_catalog.VIDEOS]

    build_video_catalog.main()

    assert fetched == indexed == video_ids
    assert deleted == [build_video_catalog.OLD_VIDEO_ID, *video_ids]


def test_transcript_fetch_failure_does_not_change_index(
    catalog_dependencies, monkeypatch
):
    _, deleted, indexed, _ = catalog_dependencies

    def fail_fetch(video_id, languages):
        raise RuntimeError("Transcript unavailable")

    monkeypatch.setattr(build_video_catalog, "fetch_youtube_transcript", fail_fetch)

    with pytest.raises(RuntimeError, match="Transcript unavailable"):
        build_video_catalog.main(video_ids=["h2aWYjSA1Jc"])

    assert deleted == indexed == []
