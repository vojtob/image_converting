import argparse
from pathlib import Path
import shutil

from convert import convert

def log(args, message):
    message_format = '{args.projectname}: {message}'
    if hasattr(args, 'file') and args.file is not None:
        message_format = message_format + ' for file {args.file}'
    print(message_format.format(args=args, message=message))

def __add_project(args):
    if not 'projectdir' in args:
        args.projectdir = Path.cwd().parent
        if args.projectdir.stem == 'utils':
            args.projectdir = args.projectdir.parent
        if args.projectdir.stem == 'img':
            args.projectdir = args.projectdir.parent
        if args.projectdir.stem == 'src_doc':
            args.projectdir = args.projectdir.parent
    else:
        args.projectdir = Path(args.projectdir)
    
    args.sourcedir = args.projectdir / 'src_doc' / 'img'
    args.destdir = args.projectdir / 'temp'

    args.svgdir = args.destdir / 'img_svg'
    args.alldir = args.destdir / 'img_all'
    args.pngdir = args.destdir / 'img_png'

    args.svgumletdir    = args.svgdir / 'umlet'
    args.svgplantumldir = args.svgdir / 'plantuml'
    args.svgsvgdir      = args.svgdir / 'svg'
    args.svgarchidir    = args.svgdir / 'archi'
    # args.svgdrawiodir    = args.svgdir / 'drawio'
	
    args.projectname = args.projectdir.stem
    args.icpath = Path(__file__).parent.parent
    args.problems = []

    if args.verbose:
        print('{args.projectname}: {args.projectdir}'.format(args=args))
    if args.debug:
        print('ic path: {0}'.format(args.icpath))

    return args

if __name__ == '__main__':
    print('image conversion: START\n')    
    
    parser = argparse.ArgumentParser(prog='ic', description='convert images from puml, umlet, mermaid, svg')
    # parser.add_argument('-pd', '--projectdir', help='set project explicitly')
    # parser.add_argument('command', choices=['all', 'clean', 'archi', 'svg', 'icons', 'areas', 'publish', 'umlet', 'mermaid'], help='what to do')
    parser.add_argument('-v', '--verbose', help='to be more verbose', action='store_true')
    parser.add_argument('-d', '--debug', help='add debug info, very low level', action='store_true')
    parser.add_argument('-p', '--poster', help='bigger dpi for posters, set scale e.g. 4', type=float)
    parser.add_argument('-f', '--file', help='process only this one file')
    subparsers = parser.add_subparsers(help='command help')

    parser_clean = subparsers.add_parser('clean', help='clean all generated files and folders')
    parser_clean.set_defaults(command='clean')

    parser_umlet = subparsers.add_parser('umlet', help='umlet -> svg -> png')
    parser_umlet.set_defaults(command='umlet')

    parser_plantuml = subparsers.add_parser('plantuml', help='plantUML images -> svg -> png')
    parser_plantuml.set_defaults(command='plantUML')

    parser_mermaid = subparsers.add_parser('mermaid', help='mermaid images -> png -> png')
    parser_mermaid.set_defaults(command='mermaid')

    parser_drawio = subparsers.add_parser('drawio', help='drawio images -> drawio -> png')
    parser_drawio.set_defaults(command='drawio')

    parser_svg = subparsers.add_parser('cppng', help='copy png in source to png in dest')
    parser_svg.set_defaults(command='cppng')

    parser_svg = subparsers.add_parser('svg', help='convert  svg in source to png in dest  -> png')
    parser_svg.set_defaults(command='svg')

    parser_svg = subparsers.add_parser('archi', help='svg/archi -> png')
    parser_svg.set_defaults(command='archi')

    args = parser.parse_args()
    if args.debug:
        args.verbose = True
    if args.verbose:
        print(args)
    args = __add_project(args)
    if args.debug:
        print(args)

    if not hasattr(args, 'command'):
        args.command = 'all'
    log(args, 'starts with the command ' + args.command)

    if args.command=='clean':
        log(args, 'start cleaning')

        for dirname in [args.svgumletdir, args.svgplantumldir, # args.svgdrawiodir, 
		args.svgsvgdir, args.pngdir]:
            p = args.projectdir / dirname
            if p.exists():
                shutil.rmtree(p)
                if args.verbose:
                    print('delete', p)
        log(args, 'done cleaning')

    if (args.command=='umlet') or (args.command=='all'):
        log(args, 'start umlet')
        # convert from uxf to png
        convert.convert_uml(args)
        convert.convert_svg(args, args.svgumletdir)
        log(args, 'done umlet')
    
    if (args.command=='plantUML') or (args.command=='all'):
        log(args, 'start plantUML conversion into SVG')
        # convert from mmd to png
        convert.convert_plantuml(args)
        convert.convert_svg(args, args.svgplantumldir)
        log(args, 'done plantUML conversion')

    if (args.command=='drawio') or (args.command=='all'):
        log(args, 'start conversion from drawio into png')
        # convert from drawio to png
        convert.convert_drawio(args)
        # convert.convert_svg(args, args.svgdrawiodir)
        log(args, 'done drawio conversion')

    if (args.command=='mermaid') or (args.command=='all'):
        log(args, 'start mermaid')
        # convert from mmd to svg -> png
        convert.convert_mmd(args)
        convert.convert_svg(args, args.svgplantumldir)
        log(args, 'done mermaid')

    if (args.command=='svg') or (args.command=='all'):
        log(args, 'start convert svg')
        convert.copy_svg(args)
        convert.convert_svg(args, args.svgsvgdir)
        log(args, 'done convert copy')

    if (args.command=='cppng') or (args.command=='all'):
        log(args, 'start copy png')
        convert.copy_png(args)
        log(args, 'done png copy')

    if (args.command=='archi') or (args.command=='all'):
        log(args, 'start svg/archi conversion')
        convert.convert_svg(args, args.svgarchidir)
        log(args, 'done svg conversion')

    if args.command !='clean':
        # publish images to img_all dir
        log(args, 'start merging images')
        args.alldir.mkdir(parents=True, exist_ok=True)
        # copy exported images
        convert.mycopy(args.pngdir, args.alldir, args)
        log(args, 'done merginf images')

    if args.problems:
        print('\nci: DONE ... with PROBLEMS !!')
        for p in args.problems:
            print('  ', p)
    else:
        print('\nci: DONE ... OK')
