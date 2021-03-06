septic tank
===========
Got a shitload of logs? Septic Tank might be the tool for you.

Septic Tank is a pipeline based data processor.  It is written in python, is fast, and has a low memory footprint. Each pipe in a pipeline has a very specific function.  Pipes may be put together in a pipeline in any way you like.  

Getting Started
---------------
::

  git clone git://github.com/jbruce12000/septic-tank.git
  cd septic-tank
  virtualenv vseptic_tank
  source vseptic_tank/bin/activate
  pip install -r requirements.txt
  cd septic_tank/
  ./make_sample_log.py | ./parse_sample_log.py |more


Inputs
------
Inputs are used to get data into a pipeline::

  stdin
  file
  zeromq
  dirwatcher


Filters / Parsers
-----------------
Filters and parsers are used to modify the data in the pipeline in some way::

  regular expression parser 
  date filter
  grep / reverse grep filter
  remove field filter
  lowercase filter
  add fields filter


Outputs
-------
Outputs are used to put data into some system outside the pipeline::

  stdout
  json
  zeromq
  solr


Warnings
--------
never put the same pipe in two different pipelines


Tests
-----
to run all tests::

  export PYTHONPATH=~/septic_tank/septic_tank/
  cd ~/septic_tank/septic_tank/tests/
  python -m unittest discover
