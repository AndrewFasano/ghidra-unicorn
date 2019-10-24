Ghidra Unicorn
------
This is a work in progress, possibly worse than Ghidra's built in emulator and certainly full of issues.

In the future, I'd like to get Unicorn and Capstone installed within Ghidra's jython environment, but for now this script
will export a pickle file from Ghidra and then a seperate python3 script will import the data and run unicorn

## Installation
Copy `export_unicorn.py` into your ghidra scripts directory. You should then see `UnicornExport` under the tools menu.
Then install dependencies with `pip3 install -r requirements.txt`

## Usage
1. Open an ARM program in Ghidra
2. Run autoanalysis
3. Export the binary with `Tools->UnicornExport`
4. Select a location to the output pickle file to
5. Configure your START and END variables in `import_unicorn.py` to control what code you'll run
6. From an environment with a real Python3 shell, run `import_unicorn.py [path_to_your_generated_pickle_file]`
7. Modify `import_unicorn.py`'s `hook_code` function to do useful things


