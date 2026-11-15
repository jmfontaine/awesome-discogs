from tools.problems import Problem, emit


def test_annotation_keeps_a_multiline_message_on_one_line(capsys):
    emit(
        [Problem("decisions.yml", 2, "invalid YAML: 100%\n  in line 2")],
        annotations=True,
    )
    assert capsys.readouterr().out == (
        "::error file=decisions.yml,line=2::invalid YAML: 100%25%0A  in line 2\n"
    )
