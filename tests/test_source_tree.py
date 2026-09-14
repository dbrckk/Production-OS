from production_os.source_tree import is_candidate_file, path_priority


def test_candidate_source_filter():
    assert is_candidate_file("app/src/main/Foo.kt")
    assert is_candidate_file("backend/app.py")
    assert not is_candidate_file("node_modules/pkg/index.js")
    assert not is_candidate_file("build/app.apk")


def test_priority_prefers_source_dirs():
    assert path_priority("src/main.py") < path_priority("docs/notes.md")
