#Simple Bioinformatic Tools
## Abstract
**Simbiont** aims to be a collections of small, but not necessary simple,
tools to handle bioinformatic data, either by acting as a translator between
different tasks in pipelines or doing one specific task really good. The idea
behind **Simbiont** is to try an implementation of the *Unix Philosophy* in
bioinformatics by using specific libraries for specific tasks. While several
tools and libraries exists to perform more complex biological analysis, e.g.
[biopython](http://biopython.org), they can sometimes be an overkill for
data preparation. Data preparation, e.g. filtering or parsing, is something of
a household chore and everybody uses mostly own tools to accomplish such tasks.
**Simbiont** facilitates the implementation of such tools by using (hopefully)
easy-to-use libraries and offers ready-to-use tools for the most common tasks,
e.g. parse BLAST outputs. In addition, numerous tools and packages to analyze
biological data exist, so why not add one more.

Simbiont is being develped by me, currently a postdoc in Prof. Edward C. Holmes'
[virus evolution group](http://sydney.edu.au/science/biology/viralevolution/index.shtml) at the University of Sydney.

### Dependencies
- **Simbiont** is written in Python 3. Some tools work under Python 2.x
by adding `import __future__`. However, you are on your own when using
Python 2.x
- **Simbiont** uses dependencies to parse program arguments and read specific
file formats, but most of them should present in your default Python
installation:

  - [argparse](https://docs.python.org/3/library/argparse.html#module-argparse)
  - [The ElementTree XML API](https://docs.python.org/3.3/library/xml.etree.elementtree.html)
  - [json](https://docs.python.org/3/library/json.html)
  - [numpy](http://www.numpy.org/)
  - [math](https://docs.python.org/3/library/math.html)

### Installation
1. Clone the repository:
    * `git clone https://github.com/janpb/simbiont.git`

    You should get two directories:

    * `lib`: contains the libraries

    * `tools`: contains tools for common tasks and serve as example how to use
    the libraries

2. Adjust two lines on the tools in the `tools` directory if you plan to use
   them:
    - The shebang (`#!`)on line 1 should match your python installation
    - The path to the libraries is relative. If a problem  occurs concerning
      missing simbiont modules/packages, adjust following line as  necessary :
      `sys.path.insert(1, os.path.join(sys.path[0], "/path/to/simbiont/lib/")`

###Examples
Tool usages:

- `simbiont/tools/ncbi/ncbi.fetch.py --uids AM503046.1 M55470 -db nucleotide | /simbiont/tools/ncbi/ncbi.tinyseq2fasta.py`

- `echo "AM503046.1 M55470" | simbiont/tools/ncbi/ncbi.fetch.py -db nucleotide`

- `simbiont/tools/ncbi/ncbi.fetch.py -h`

If not specified otherwise, input is usually `STDIN` and output `STDOUT`.

###Remarks
- **Simbiont** is under active development and therefore will change from time
   to time.

- Serious lack of documentation. Most tools have an USAGE which can be
  invoked using `-h`, but that's all.

- Bugs, so be aware and check results after first usage.
