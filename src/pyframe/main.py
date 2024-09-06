import os
import shutil
import subprocess
import sys


def collect_variables() -> dict[str, str | int]:
    vars = {}
    vars['name'] = input('Project name: ')
    while vars['name'] == '':
        print('Invalid name!')
        vars['name'] = input('Project name: ')
    vars['desc'] = input('Project description: ')
    ver = input('Initial version (0.0.1): ')
    vars['version'] = '0.0.1' if not ver else ver
    is_cli = input('Is this a CLI tool? (y/N): ').lower() == 'y'
    vars['is_cli'] = is_cli
    if is_cli:
        cli_name = input(f'Command name ({vars['name']}): ')
        vars['cli_name'] = vars['name'] if cli_name == '' else cli_name
    else:
        vars['cli_name'] = vars['name']
    return vars


def project_scaffold(vars: dict[str, str | int]):
    parent_folder = input('Parent folder (~/dev/git): ')
    parent_folder = os.path.expanduser('~/dev/git' if parent_folder == '' else parent_folder)
    while not os.path.isdir(parent_folder):
        print(f'ERROR: {parent_folder} is not a directory.')
        parent_folder = input('Parent folder (~/dev/git): ')
        parent_folder = os.path.expanduser('~/dev/git' if parent_folder == '' else parent_folder)
    base_folder = os.path.join(parent_folder, vars['name'])
    # Build project folder and src folder structure
    os.makedirs(os.path.join(base_folder, 'src', vars['name']))
    open(os.path.join(base_folder, 'src', '__init__.py'), 'w').close()
    open(os.path.join(base_folder, 'src', vars['name'], '__init__.py'), 'w').close()
    with open(os.path.join(base_folder, 'src', vars['name'], 'main.py'), 'w') as f:
        f.write(
            f"""def {vars['cli_name']}() -> None:
    pass


if __name__ == '__main__':
    print('Hello {vars['cli_name']}!')
"""
        )
    res_path = os.path.join(os.path.sep.join(os.path.realpath(__file__).split(os.path.sep)[:-2]), 'resources')
    for f in ['.pre-commit-config.yaml', 'LICENSE', '.gitignore']:
        shutil.copyfile(os.path.join(res_path, f), os.path.join(base_folder, f))
    with open(os.path.join(res_path, 'pyproject.txt'), 'r') as inf, open(
        os.path.join(base_folder, 'pyproject.toml'), 'w'
    ) as outf:
        vars['cli_script'] = ''
        if vars['is_cli']:
            vars['cli_script'] = '''

[project.scripts]
{cli_name} = "{cli_name}.main:{cli_name}"'''.format(**vars)
        data = inf.read().format(**vars)
        outf.write(data)
    with open(os.path.join(base_folder, 'README.md'), 'w') as rmf:
        rmf.write(f"# {vars['cli_name']}\n\n*{vars['desc']}*")
    setup_commands(base_folder)


def setup_commands(base_folder: str) -> None:
    old_dir = os.getcwd()
    os.chdir(base_folder)
    print('Setting up virtual env...', end='', flush=True)
    subprocess.check_call([sys.executable, '-m', 'venv', 'venv'])
    subprocess.call('source venv/bin/activate', shell=True)
    print('Done!')
    print('Installing pip-tools...', end='', flush=True)
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', 'pip-tools'])
    print('Done!')
    print('Compiling and installing dev requirements...', end='', flush=True)
    subprocess.check_call(['pip-compile', '-q', '--no-strip-extras', '--extra=dev', '-o', 'dev-requirements.txt'])
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-qr', 'dev-requirements.txt'])
    print('Done!')
    os.chdir(old_dir)


def pyframe():
    vars = collect_variables()
    try:
        project_scaffold(vars)
    except FileExistsError:
        print(f'ERROR:  Invalid file path\n    {vars=}\n\nExiting...')


if __name__ == '__main__':
    pyframe()
