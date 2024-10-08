import json
import os
import struct
import subprocess
import sys

version = '1.0.4'
__version__ = version


def get_conda_envs_dir():
    # Conda helper
    json_output = subprocess.Popen(
        ["conda", "info", '--json'],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]

    if sys.version_info[0] >= 3:
        json_output = json_output.decode('utf-8')
    as_dict = json.loads(json_output)

    envs = as_dict['envs_dirs']

    if len(envs) != 1:
        base_workspace = os.path.normcase(os.path.dirname(os.path.abspath('.')))
        initial_base_workspace = base_workspace

        while base_workspace:
            new_envs = [env for env in envs if
                        os.path.normcase(os.path.abspath(env)).startswith(
                            base_workspace)]
            if len(new_envs) == 1:
                break
            new_workspace = os.path.dirname(base_workspace)
            if new_workspace == base_workspace:
                break
            base_workspace = new_workspace

        assert len(new_envs) == 1, 'Expected 1 env. Found: %s. Base: %s' % (
            envs, initial_base_workspace)

        envs = new_envs

    assert len(envs) == 1, 'Expected 1 env. Found: %s' % (envs,)
    conda_envs_dir = next(iter(envs))
    return conda_envs_dir


def get_python_exe_from_env(conda_envs_dir, env_name):
    # Conda helper
    env_dir = os.path.join(conda_envs_dir, env_name)
    if not os.path.exists(env_dir):
        raise RuntimeError('Env does not exist: %s' % (env_dir,))
    for exe_name in ('python.exe', 'python', 'python.bat'):
        py_exe = os.path.join(env_dir, exe_name)
        if os.path.exists(py_exe):
            return py_exe
        py_exe = os.path.join(env_dir, 'bin', exe_name)
        if os.path.exists(py_exe):
            return py_exe

    raise RuntimeError('Unable to find Python executable in %s' % (env_dir,))


def validate_pair(ob):
    try:
        if not (len(ob) == 2):
            sys.stderr.write("Unexpected result: %s" % (ob,))
            raise ValueError
    except:
        return False
    return True


def consume(it):
    try:
        while True:
            next(it)
    except StopIteration:
        pass


def get_environment_from_batch_command(env_cmd, initial=None):
    """
    Take a command (either a single command or list of arguments)
    and return the environment created after running that command.
    Note that if the command must be a batch file or .cmd file, or the
    changes to the environment will not be captured.

    If initial is supplied, it is used as the initial environment passed
    to the child process.
    """
    if not isinstance(env_cmd, (list, tuple)):
        env_cmd = [env_cmd]
    if not os.path.exists(env_cmd[0]):
        raise RuntimeError('Error: %s does not exist' % (env_cmd[0],))

    # construct the command that will alter the environment
    env_cmd = subprocess.list2cmdline(env_cmd)
    # create a tag so we can tell in the output when the proc is done
    tag = 'Done running command'
    # construct a cmd.exe command to do accomplish this
    cmd = 'cmd.exe /s /c "{env_cmd} && echo "{tag}" && set"'.format(**vars())
    # launch the process
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=initial)
    # parse the output sent to stdout
    lines = proc.stdout
    # consume whatever output occurs until the tag is reached
    for line in lines:
        line = line.decode('utf-8')
        if 'The specified configuration type is missing.' in line:
            raise AssertionError('Error executing %s. View http://blog.ionelmc.ro/2014/12/21/compiling-python-extensions-on-windows/ for details.' % (env_cmd))
        if tag in line:
            break
    if sys.version_info[0] > 2:
        # define a way to handle each KEY=VALUE line
        handle_line = lambda l: l.decode('utf-8').rstrip().split('=', 1)
    else:
        # define a way to handle each KEY=VALUE line
        handle_line = lambda l: l.rstrip().split('=', 1)
    # parse key/values into pairs
    pairs = map(handle_line, lines)
    # make sure the pairs are valid
    valid_pairs = filter(validate_pair, pairs)
    # construct a dictionary of the pairs
    result = dict(valid_pairs)
    # let the process finish
    proc.communicate()
    return result


def is_python_64bit():
    return (struct.calcsize('P') == 8)


def get_compile_env(py_executable=None):
    if py_executable is not None:
        json_output = subprocess.Popen([py_executable, __file__, '--json'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]
        import json
        try:
            ret = json.loads(json_output)
        except Exception:
            sys.stderr.write('Error getting env for\n%s.\nOutput:\n%s' % (py_executable, json_output.decode('utf-8')))
            raise
        if sys.version_info[0] <= 2:
            new_dict = {}
            for key, val in ret.items():
                if isinstance(key, unicode):
                    key = key.encode('utf-8')
                if isinstance(val, unicode):
                    val = val.encode('utf-8')
                new_dict[key] = val
            ret = new_dict
        return ret

    env = os.environ.copy()
    if sys.platform == 'win32' and os.getenv('WIN_COMPILE_HELPERS') != 'disable':
        # "C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\bin\vcvars64.bat"
        # set MSSdk=1
        # set DISTUTILS_USE_SDK=1
        # set VS100COMNTOOLS=C:\Program Files (x86)\Microsoft Visual Studio 9.0\Common7\Tools
        if sys.version_info[:2] in ((3, 6), (3, 7), (3, 8), (3, 9), (3, 10), (3, 11), (3, 12)):
            import setuptools  # We have to import it first for the compiler to be found
            from distutils import msvc9compiler

            vcvarsall = msvc9compiler.find_vcvarsall(14.0)
            if vcvarsall is None or not os.path.exists(vcvarsall):
                raise RuntimeError('Error finding vcvarsall.')

            if is_python_64bit():
                env.update(get_environment_from_batch_command(
                    [vcvarsall, 'amd64'],
                    initial=os.environ.copy()))
            else:
                env.update(get_environment_from_batch_command(
                    [vcvarsall, 'x86'],
                    initial=os.environ.copy()))

        elif sys.version_info[:2] in ((3, 3), (3, 4)):
            if is_python_64bit():
                env.update(get_environment_from_batch_command(
                    [r"C:\Program Files\Microsoft SDKs\Windows\v7.1\Bin\SetEnv.cmd", '/x64'],
                    initial=os.environ.copy()))
            else:
                env.update(get_environment_from_batch_command(
                    [r"C:\Program Files\Microsoft SDKs\Windows\v7.1\Bin\SetEnv.cmd", '/x86'],
                    initial=os.environ.copy()))

        else:
            raise AssertionError('Unable to setup environment for Python: %s' % (sys.version,))

        env['MSSdk'] = '1'
        env['DISTUTILS_USE_SDK'] = '1'

    return env


def print_env_as_json():
    env = get_compile_env()
    import json
    print(json.dumps(env, indent=4))


if __name__ == '__main__':
    if '--json' in sys.argv:
        print_env_as_json()
    else:
        sys.stderr.write('Error. Unexpected args: %s' % (sys.argv,))
