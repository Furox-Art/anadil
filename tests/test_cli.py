import os
import runpy
import subprocess
import sys
from pathlib import Path

import pytest

from polyglot_python.cli import _configure_console, main

TR_PROGRAM = (
    "fonksiyon topla(a, b):\n"
    "    döndür a + b\n"
    "\n"
    "print(topla(2, 3))\n"
)


def _write(tmp_path, name, text):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def test_run_uses_suffix(tmp_path, capsys):
    path = _write(tmp_path, "program.tr", TR_PROGRAM)
    assert main(["run", str(path)]) == 0
    assert capsys.readouterr().out.strip() == "5"


def test_run_explicit_lang_before_file(tmp_path, capsys):
    path = _write(tmp_path, "program.txt", TR_PROGRAM)
    assert main(["run", "--lang", "tr", str(path)]) == 0
    assert capsys.readouterr().out.strip() == "5"


def test_run_reads_directive(tmp_path, capsys):
    path = _write(tmp_path, "program.txt", "# polyglot-python: tr\n" + TR_PROGRAM)
    assert main(["run", str(path)]) == 0
    assert capsys.readouterr().out.strip() == "5"


def test_run_passes_program_arguments(tmp_path, capsys):
    source = "içe_aktar sys\nprint(sys.argv[1])\n"
    path = _write(tmp_path, "args.tr", source)
    assert main(["run", str(path), "merhaba"]) == 0
    assert capsys.readouterr().out.strip() == "merhaba"


def test_run_propagates_exit_code(tmp_path):
    source = "içe_aktar sys\nsys.exit(3)\n"
    path = _write(tmp_path, "exit.tr", source)
    assert main(["run", str(path)]) == 3


def test_run_syntax_error_is_localized(tmp_path, capsys):
    path = _write(tmp_path, "broken.tr", "eğer Doğru\n    geç\n")
    assert main(["run", str(path)]) == 1
    error = capsys.readouterr().err
    assert "Sözdizimi hatası" in error
    assert "broken.tr:1:" in error


def test_run_runtime_error_is_localized(tmp_path, capsys):
    path = _write(tmp_path, "boom.tr", "print(1 / 0)\n")
    assert main(["run", str(path)]) == 1
    error = capsys.readouterr().err
    assert "Çalışma zamanı hatası" in error
    assert "ZeroDivisionError" in error


def test_unknown_locale(tmp_path, capsys):
    path = _write(tmp_path, "program.txt", "print(1)\n")
    assert main(["run", "--lang", "xx", str(path)]) == 1
    assert "unknown locale" in capsys.readouterr().err


def test_missing_file(capsys):
    assert main(["run", "does-not-exist.tr"]) == 1
    assert "cannot read" in capsys.readouterr().err


def test_translate_to_stdout(tmp_path, capsys):
    path = _write(tmp_path, "program.tr", TR_PROGRAM)
    assert main(["translate", "--lang", "tr", str(path)]) == 0
    assert capsys.readouterr().out == (
        "def topla(a, b):\n"
        "    return a + b\n"
        "\n"
        "print(topla(2, 3))\n"
    )


def test_translate_to_file(tmp_path):
    path = _write(tmp_path, "program.tr", TR_PROGRAM)
    output = tmp_path / "program.py"
    assert main(["translate", str(path), "-o", str(output)]) == 0
    assert output.read_text(encoding="utf-8") == (
        "def topla(a, b):\n"
        "    return a + b\n"
        "\n"
        "print(topla(2, 3))\n"
    )


def test_locales_lists_all_codes(capsys):
    assert main(["locales"]) == 0
    output = capsys.readouterr().out
    for code in ("tr", "es", "pt", "de", "fr", "zh", "hi", "ar"):
        assert code in output


def test_version(capsys):
    with pytest.raises(SystemExit) as caught:
        main(["--version"])
    assert caught.value.code == 0
    assert "polyglot-python 0.1.0" in capsys.readouterr().out


def test_run_token_error_is_localized(tmp_path, capsys):
    path = _write(tmp_path, "unterminated.tr", 'metin = """açık\n')
    assert main(["run", str(path)]) == 1
    error = capsys.readouterr().err
    assert "Belirteç hatası" in error
    assert "unterminated.tr:" in error


def test_invalid_utf8_rejected(tmp_path, capsys):
    path = tmp_path / "bad.tr"
    path.write_bytes(b"print(1)\n\xff\n")
    assert main(["run", str(path)]) == 1
    assert "cannot decode" in capsys.readouterr().err


def test_translate_write_failure(tmp_path, capsys):
    path = _write(tmp_path, "program.tr", TR_PROGRAM)
    target = tmp_path / "missing-dir" / "out.py"
    assert main(["translate", str(path), "-o", str(target)]) == 1
    assert "cannot write" in capsys.readouterr().err


def test_run_exit_none(tmp_path):
    path = _write(tmp_path, "exit-none.tr", "içe_aktar sys\nsys.exit()\n")
    assert main(["run", str(path)]) == 0


def test_run_exit_string(tmp_path, capsys):
    path = _write(tmp_path, "exit-str.tr", 'içe_aktar sys\nsys.exit("dur")\n')
    assert main(["run", str(path)]) == 1
    assert "dur" in capsys.readouterr().err


def test_run_keyboard_interrupt_propagates(tmp_path):
    path = _write(tmp_path, "interrupt.tr", "raise KeyboardInterrupt\n")
    with pytest.raises(KeyboardInterrupt):
        main(["run", str(path)])


def test_module_entrypoint():
    root = Path(__file__).resolve().parents[1]
    env = dict(os.environ)
    env["PYTHONPATH"] = str(root / "src")
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(
        [sys.executable, "-m", "polyglot_python", "locales"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        check=False,
    )
    assert result.returncode == 0
    assert "tr" in result.stdout


def test_translate_missing_file(capsys):
    assert main(["translate", "does-not-exist.tr"]) == 1
    assert "cannot read" in capsys.readouterr().err


def test_errors_fall_back_to_english_without_locale(tmp_path, capsys):
    syntax = _write(tmp_path, "broken.py", "if True\n    pass\n")
    assert main(["run", str(syntax)]) == 1
    assert "Syntax error" in capsys.readouterr().err

    runtime = _write(tmp_path, "boom.py", "print(1 / 0)\n")
    assert main(["run", str(runtime)]) == 1
    assert "Runtime error" in capsys.readouterr().err


def test_configure_console_handles_streams(monkeypatch):
    calls = []

    class Missing:
        pass

    class Failing:
        def reconfigure(self, **kwargs):
            calls.append(kwargs)
            raise OSError("cannot reconfigure")

    monkeypatch.setattr(sys, "stdout", Missing())
    monkeypatch.setattr(sys, "stderr", Failing())
    _configure_console()
    assert calls == [{"encoding": "utf-8", "newline": "\n"}]


def test_cli_module_guard(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["polyglot-python", "locales"])
    with pytest.warns(RuntimeWarning):
        with pytest.raises(SystemExit) as caught:
            runpy.run_module("polyglot_python.cli", run_name="__main__")
    assert caught.value.code == 0


def test_package_module_guard(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["polyglot-python", "locales"])
    with pytest.raises(SystemExit) as caught:
        runpy.run_module("polyglot_python", run_name="__main__")
    assert caught.value.code == 0
    assert "tr" in capsys.readouterr().out
