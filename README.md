# py_compile_win_helpers

Helpers to setup the environment to compile extensions for Python.

It's meant to be used in Python code to automate getting a library and building it without relying on the current env.

Example:

	def main():
		subprocess.check_call(['git', 'clone', 'some_repo'])
		import py_compile_win_helpers
		env = py_compile_win_helpers.get_compile_env()
		subprocess.check_call(['python', 'setup.py', 'build'], env=env, cwd=os.path.join('some_repo'))





