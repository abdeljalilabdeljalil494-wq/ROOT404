"""Execute only these trusted test programs on the test host. NOT isolation tests."""
import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location('runner_common', Path(__file__).resolve().parents[2] / 'judge_sandbox/runners/common.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


@pytest.mark.parametrize('language,name,source', [
    ('c', 'main.c', '#include <stdio.h>\nint main(void){puts("42");return 0;}'),
    ('cpp', 'main.cpp', '#include <iostream>\nint main(){std::cout << "42\\n";}'),
    ('python', 'main.py', 'print(42)'),
    ('javascript', 'main.js', 'console.log(42)'),
])
def test_actual_valid_programs(tmp_path, language, name, source):
    (tmp_path / name).write_text(source)
    result = runner.execute(tmp_path, language)
    assert result['status'] == 'success', result
    assert result['output'] == '42\n' and result['exit_code'] == 0


@pytest.mark.parametrize('language,name,source,expected', [
    ('c', 'main.c', 'not valid C;', 'compilation_error'),
    ('cpp', 'main.cpp', 'not valid C++;', 'compilation_error'),
    ('python', 'main.py', 'raise RuntimeError("failure")', 'runtime_error'),
    ('javascript', 'main.js', 'throw new Error("failure")', 'runtime_error'),
])
def test_actual_invalid_programs(tmp_path, language, name, source, expected):
    (tmp_path / name).write_text(source)
    result = runner.execute(tmp_path, language)
    assert result['status'] == expected and result['exit_code'] != 0


def test_execution_timeout(tmp_path):
    (tmp_path / 'main.py').write_text('while True: pass')
    assert runner.execute(tmp_path, 'python', timeout=1)['status'] == 'timeout'


def test_output_limit(tmp_path):
    (tmp_path / 'main.py').write_text('print("x" * 200000)')
    result = runner.execute(tmp_path, 'python')
    assert result['status'] == 'output_limit' and len(result['output']) <= 65536


@pytest.mark.parametrize('language,name,source', [
    ('c', 'main.c', 'int main(void){for(;;){}return 0;}'),
    ('cpp', 'main.cpp', 'int main(){for(;;){}}'),
    ('python', 'main.py', 'while True: pass'),
    ('javascript', 'main.js', 'while(true){}'),
])
def test_each_language_infinite_loop_is_terminated(tmp_path, language, name, source):
    (tmp_path/name).write_text(source)
    assert runner.execute(tmp_path, language, timeout=1)['status'] == 'timeout'


def test_trusted_python_allocation_cannot_exceed_address_space_limit(tmp_path):
    (tmp_path/'main.py').write_text('bytearray(600 * 1024 * 1024)')
    result = runner.execute(tmp_path, 'python', timeout=2)
    assert result['status'] == 'runtime_error'
    assert 'MemoryError' in result['error']
    # Local RLIMIT_AS evidence only, NOT Docker/cgroup OOM isolation evidence.


def test_compiler_binary_size_is_not_confused_with_small_output_limit(tmp_path):
    (tmp_path/'main.c').write_text('#include <stdio.h>\nint main(void){puts("42");return 0;}')
    result=runner.execute(tmp_path,'c',output_limit=1024)
    assert result['status']=='success',result
    assert result['output']=='42\n'
