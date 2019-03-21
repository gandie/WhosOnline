# WhosOnline

Interactive network monitoring shell.

Also contains other fun stuff.

## Installation

Packages (Ubuntu 18)

```bash
apt install net-tools nmap
```

Python3:
```bash
cd path/to/this/repo
pip install -r requirements.txt
python setup.py install
```

## Usage

```
usage: whosonline [-h] [-n NETWORK] [--no-dns] [-i INTERFACE]

optional arguments:
  -h, --help            show this help message and exit
  -n NETWORK, --network NETWORK
                        Network address to be scanned
  --no-dns              Do not rely on dns, scan by ip
  -i INTERFACE, --interface INTERFACE
                        Fallback interface, may be used if interface cannot be
                        detected
```
