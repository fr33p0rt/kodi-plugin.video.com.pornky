#!/bin/bash

BAS=256

let "FS=BAS/4"
let "TS=BAS/6"

let "TSX=BAS*10/47"
let "TSY=BAS/5"

convert -background black -fill white \
          -font "Cantarell" -pointsize $FS label:PORN \
          -fill white -fuzz 95% -floodfill +$TSX+$TSY black \
          -fill black -font "DejaVu-Sans" -pointsize $TS -draw "text $TSX,$TSY '▸'" \
          -trim \
          icon-1.png

convert -background black -fill grey \
          -font "Cantarell" -pointsize $FS label:KY \
          -trim \
          icon-2.png

L1X=$(( $(identify -format '%w' icon-2.png) / 2 ))
L2X=$(( $(identify -format '%w' icon-1.png) / 2 ))

convert -size ${BAS}x${BAS} xc:black -gravity Center \
        icon-1.png -geometry -$L1X -composite \
        icon-2.png -geometry +$L2X -composite \
        ../plugin.video.com.pornky/icon.png

rm icon-1.png icon-2.png
