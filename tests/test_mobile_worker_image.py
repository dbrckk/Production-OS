from pathlib import Path


def test_mobile_worker_image_pins_flutter_android_runtime_and_avd():
    payload = Path("Dockerfile.mobile-worker").read_text(encoding="utf-8")

    assert "instrumentisto/flutter:3.41.6-androidsdk36-r0" in payload
    assert '"emulator"' in payload
    assert '"platform-tools"' in payload
    assert '"platforms;android-35"' in payload
    assert '"build-tools;35.0.0"' in payload
    assert '"system-images;android-35;google_apis;x86_64"' in payload
    assert "avdmanager create avd" in payload
    assert "production-os-api35" in payload
    assert "ANDROID_AVD_HOME=/opt/android-avd" in payload
