from types import SimpleNamespace

from app import ask


class FakeClient:
    def __init__(self, response, api_key):
        assert api_key == "test-key"
        self.response = response
        self.models = self

    def generate_content(self, *, model, contents):
        assert model == ask.MODEL
        assert contents == "質問"
        return self.response


def test_ask_prints_input_and_output_token_counts(monkeypatch, capsys):
    response = SimpleNamespace(
        text="回答",
        usage_metadata=SimpleNamespace(
            prompt_token_count=12,
            candidates_token_count=7,
        ),
    )
    monkeypatch.setattr(ask.genai, "Client", lambda api_key: FakeClient(response, api_key))
    monkeypatch.setattr(ask, "get_api_key", lambda: "test-key")
    times = iter([10.0, 12.5])
    monkeypatch.setattr(ask, "perf_counter", lambda: next(times))

    assert ask.ask("質問") == "回答"
    output = capsys.readouterr().out
    assert "[応答時間] API: 2.50秒" in output
    assert "[トークン] 入力: 12 / 出力: 7" in output


def test_ask_reports_missing_token_counts(monkeypatch, capsys):
    response = SimpleNamespace(text="回答", usage_metadata=None)
    monkeypatch.setattr(ask.genai, "Client", lambda api_key: FakeClient(response, api_key))
    monkeypatch.setattr(ask, "get_api_key", lambda: "test-key")

    ask.ask("質問")
    assert "[トークン] 入力: 不明 / 出力: 不明" in capsys.readouterr().out
