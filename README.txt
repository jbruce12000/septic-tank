Got a shitload of logs? Septic Tank might be the tool for you.

Septic Tank is a pipeline based data processor.  It is written in python, is fast, and has a low memory footprint. Each pipe in a pipeline has a very specific function.  Pipes may be put together in a pipeline in any way you like.  

Inputs

Inputs are used to get data into a pipeline.

Filters / Parsers

Filters and parsers are used to modify the data in the pipeline in some way.

Outputs

Outputs are used to put data into some system outside the pipeline.


WARNINGS
- never put the same pipe in two different pipelines
