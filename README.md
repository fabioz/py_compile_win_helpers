# py_compile_win_helpers

Helpers to setup the environment to compile extensions for Python.

It's meant to be used in Python code to automate getting a library and building 
it as an extension module without relying on the current env.

It should take care of env variables such as MSSdk, DISTUTILS_USE_SDK, finding 
the compiler and executing vcvarsall or SetEnv as needed.

Example:

	def main():
		subprocess.check_call(['git', 'clone', 'some_repo'])
		import py_compile_win_helpers
		env = py_compile_win_helpers.get_compile_env()
		subprocess.check_call(['python', 'setup.py', 'build'], env=env, cwd=os.path.join('some_repo'))


# Requisites

For Python 2.6 and 2.7, Microsoft Visual C++ Compiler for Python 2.7 is needed.
-- https://www.microsoft.com/en-us/download/details.aspx?id=44266

For Python 3.3 and 3.4, Visual Studio 2010 Express is needed.

For Python 3.5 and 3.6, Visual Studio 2015 is needed.

-- Note, older versions can be found at https://www.visualstudio.com/vs/older-downloads/
but you need to register with Microsoft (free) to be able to find downloads for older versions of Visual Studio
