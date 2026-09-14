from production_os.components import extract_components
from production_os.models import RepoEvidence


def evidence(source_documents):
    return RepoEvidence(
        name="demo",
        full_name="owner/demo",
        html_url="https://github.com/owner/demo",
        source_documents=source_documents,
    )


def test_extracts_python_components_and_dependencies():
    components = extract_components(
        evidence({
            "src/billing.py": (
                "import redis\n"
                "class BillingManager:\n"
                "    def acknowledge_purchase(self):\n"
                "        return redis.Redis()\n"
                "\n"
                "def public_helper():\n"
                "    return 1\n"
            )
        })
    )
    billing = next(item for item in components if item.name == "BillingManager")
    assert billing.language == "python"
    assert "redis" in billing.dependencies
    assert "android-play-billing" in billing.capability_hints


def test_extracts_kotlin_class_with_capability_hint():
    components = extract_components(
        evidence({
            "app/src/BillingManager.kt": (
                "import com.android.billingclient.api.BillingClient\n"
                "class BillingManager {\n"
                "  fun connect(client: BillingClient) = Unit\n"
                "}\n"
            )
        })
    )
    component = next(item for item in components if item.name == "BillingManager")
    assert component.language == "kotlin"
    assert "android-play-billing" in component.capability_hints
