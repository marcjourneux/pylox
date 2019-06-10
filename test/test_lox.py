from lox.lox import Lox
import os
import argparse
import traceback


def run_test(filename):
    # Run the lox compiler with a file
    lox = Lox()
    # <-- absolute dir the script is in
    script_dir = os.path.dirname(__file__)
    filepath = os.path.join(script_dir, filename)
    print(filepath)
    try:
        with open(filepath, 'r') as f:
            errors = []
            source = f.read()
            lox.run(source, errors)
    except Exception as err:
        print("Error during compilation of {0}. Error is {1}\n{2}".
              format(filepath, str(err), traceback.format_exc()))


# Main routine for compiling Lox language
#
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Name of test file')
    parser.add_argument('files', nargs='*',
                        help='lox source file')
    args = parser.parse_args()
    if len(args.files) > 0:
        for file in args.files:
            try:
                print("Testing file: ", file)
                run_test(file)
            except:
                print("cannot read file {}".format(file))
