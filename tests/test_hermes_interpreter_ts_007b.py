from app.mcp.tools.hermes_interpreter import interpret_findings


def test_interpretation_human_readable():
    findings = [
        {
            "entity_type": "precio",
            "severity": "ALTO",
            "difference": 300,
            "suggested_action": "revisar proveedor"
        }
    ]

    messages = interpret_findings(findings)

    assert len(messages) == 1
    msg = messages[0]

    assert "precio" in msg
    assert "300" in msg
    assert "ALTO" in msg
    assert "revisar proveedor" in msg


def test_no_technical_noise():
    findings = [
        {
            "entity_type": "stock",
            "severity": "CRITICO",
            "difference": -5,
            "suggested_action": "reponer"
        }
    ]

    msg = interpret_findings(findings)[0]

    assert "_id" not in msg
    assert "{" not in msg
    assert "}" not in msg
