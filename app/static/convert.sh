#!/bin/bash
for file in *.raw; do
	F="`basename $file .raw`.wav"
	sox -r 8000 -e signed-integer -b 16 $file $F
done
