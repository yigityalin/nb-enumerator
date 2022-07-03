from argparse import ArgumentParser
from json import JSONDecodeError
from pathlib import Path
from tqdm import tqdm
import json

IPYNB_SUFFIX = '.ipynb'


def get_confirmation(message: str) -> bool:
    message = '\n' + message + ' [y/N]: '
    confirmation = input(message).lower()
    while confirmation and confirmation not in {'y', 'n'}:
        confirmation = input(message).lower()
    return confirmation and confirmation == 'y'


def enumerate_cells(path: Path, output_path: Path, save: bool = True) -> None:
    with open(path, encoding='UTF-8') as file:
        nb = json.load(file)

    cells = list(filter(lambda cell: cell['cell_type'] == 'code', nb.get('cells')))

    for execution_count, cell in tqdm(enumerate(cells, start=1), total=len(cells), desc='Enumerating cells'):
        cell['execution_count'] = execution_count
        for output in cell.get('outputs', []):
            output['execution_count'] = execution_count

    if save:
        with open(output_path, 'w+') as file:
            json.dump(nb, file, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    parser = ArgumentParser(description='Enumerates the code cells starting from 1.')
    parser.add_argument('file', help='The notebook file to be enumerated.')
    parser.add_argument('-o', '--out', help='The enumerated file. Overwrites the input file if not specified.',
                        required=False, dest='out')
    args = parser.parse_args()

    filepath = Path(args.file)

    confirmed = True
    if not filepath.is_file():
        raise ValueError('No such file exists')
    elif filepath.suffix != IPYNB_SUFFIX:
        confirmed = confirmed and get_confirmation(
            f'The specified file has suffix {filepath.suffix}. This might not work as intended. Are you sure?'
        )

    if not args.out:
        out_filepath = filepath
        confirmed = confirmed and get_confirmation(
            'No output file is specified. The input file will be overwritten. Are you sure?'
        )
    else:
        out_filepath = Path(args.out)
        if out_filepath.exists():
            confirmed = confirmed and get_confirmation(
                'There is already a file with given path. The file will be overwritten. Are you sure?'
            )
        if not out_filepath.suffix:
            confirmed = confirmed and get_confirmation(
                'The output file has no suffix. Are you sure?'
            )
        elif out_filepath.suffix != IPYNB_SUFFIX:
            confirmed = confirmed and get_confirmation(
                f'The output file has suffix other than {IPYNB_SUFFIX}. Are you sure?'
            )

    if confirmed:
        try:
            enumerate_cells(filepath, out_filepath)
            print(f'The file has been saved.')
        except JSONDecodeError:
            print('The file has to have json file format. No changes were made.')
        except Exception:
            print('An unknown error occurred. No changes were made.')
    else:
        print("Terminating...")
