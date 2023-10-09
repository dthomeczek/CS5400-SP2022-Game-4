#!/bin/bash

# DO NOT MODIFY THIS SCRIPT

# This script is to help you test your AI and for grading purposes. Your code will be compiled and ran by this script.

LANG=$1
SESSION=$2

cd $LANG
make
./testRun ${@:2}  &
./testRun ${@:2}  > /dev/null &

# DO NOT MODIFY THIS SCRIPT
