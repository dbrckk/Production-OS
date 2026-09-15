from production_os.signers import PemSigner, coerce_signer
from production_os.signing import generate_keypair, verify_payload
from production_os.supply_chain import sign_slsa_statement_with_signer
from production_os.witness import sign_checkpoint_with_signer


def test_pem_signer_signs_without_exposing_key_to_callers():
    private_key,public_key=generate_keypair()
    signer=PemSigner(private_key)
    payload={"release_id":"release-1"}
    signature=signer.sign(payload)
    assert signer.key_id==signature["key_id"]
    assert verify_payload(public_key,payload,signature) is True


def test_coerce_signer_preserves_explicit_signer():
    private_key,_=generate_keypair()
    signer=PemSigner(private_key)
    assert coerce_signer(signer=signer) is signer


def test_slsa_and_witness_accept_signer_interface():
    private_key,_=generate_keypair()
    signer=PemSigner(private_key)
    statement={
        "predicate":{
            "runDetails":{
                "metadata":{"finishedOn":"2026-09-15T10:00:00+00:00"}
            }
        }
    }
    slsa=sign_slsa_statement_with_signer(
        statement=statement,
        signer=signer,
    )
    witness=sign_checkpoint_with_signer(
        {"root_hash":"a"*64},
        signer=signer,
    )
    assert slsa["signature"]["key_id"]==signer.key_id
    assert witness["signature"]["key_id"]==signer.key_id
