#!/bin/bash

SRC="https://images.pexels.com/photos/3827430/pexels-photo-3827430.jpeg?crop=entropy&cs=srgb&dl=pexels-dainis-graveris-3827430.jpg&fit=crop&fm=jpg&h=3600&w=2400"
BRO="Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"

#WID=1920
#SIZ=${WID}x1080

WID=1280
SIZ=${WID}x720

wget -U "${BRO}" "${SRC}" -O fanart-src.jpg

convert fanart-src.jpg -quality 70 -thumbnail ${WID}x -gravity center -crop ${SIZ}+0+0 ../plugin.video.com.pornky/fanart.jpg

rm fanart-src.jpg
