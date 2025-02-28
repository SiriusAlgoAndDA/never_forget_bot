import argparse

from tools import gen, open_sqlalchemy


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        'tool_name',
        help='Tool name',
        type=str,
    )
    # arguments to pass to tools
    arg_parser.add_argument(
        'tool_args',
        help='Tool arguments',
        type=str,
        nargs='*',
    )
    args = arg_parser.parse_args()
    match args.tool_name:
        case 'gen':
            gen.main(*args.tool_args)
        case 'sqlalchemy':
            open_sqlalchemy.main(*args.tool_args)
        case _:
            raise ValueError(f'Unknown tool: {args.tool_name}')
