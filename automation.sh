#!/bin/bash

function GetLiveData { python GetLiveData.py; }


while true; do case $1 in
	GetLiveData) GetLiveData;	shift	;;
	*) break;;
  esac
done
