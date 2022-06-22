#!/bin/bash

function GetLiveData { python GetLiveData.py; }
function Trendfollowing { python trendfollowing.py; }

while true; do case $1 in
	GetLiveData) GetLiveData;	shift	;;
	Trendfollowing) Trendfollowing;	shift	;;
	*) break;;
  esac
done
