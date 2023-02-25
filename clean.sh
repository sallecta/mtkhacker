#!/usr/bin/env bash

path0="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"


fn_stoponerror ()
{
	# Usage:
	# fn_stoponerror $? $LINENO
	error_code=$1
	line=$2
	if [ $error_code -ne 0 ]; then
		printf "\n"$line": error ["$error_code"]\n\n"
		exit $error_code
	fi
}

fn_remove_cache ()
{
	path_to_binaries=$1
	echo $path_to_binaries
	if [[ ! -e $path_to_binaries ]]; then
		echo "path $path_to_binaries not exist."
		return 1
	fi
	
	echo "Removing pycache dirs..."
		find $path_to_binaries -name '__pycache__' -type d | while read line; do
			echo "Processing file $line"
			rm -rf $line
			fn_stoponerror $? $LINENO
		done
	echo "...done"

	echo "Removing pyc files..."
		find $path_to_binaries -name '*.pyc' | while read line; do
			echo "Processing file $line"
			rm -rf $line
			fn_stoponerror $? $LINENO
		done
	echo "...done"
}

fn_remove_cache "$path0/mtkclient"
fn_stoponerror $? $LINENO

fn_remove_cache "$path0/mtkhacker_modules"
fn_stoponerror $? $LINENO

