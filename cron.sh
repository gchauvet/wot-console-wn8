#!/usr/bin/env bash



cd "${0%/*}"



#Print starting time.
CURRENT_TIME=`date "+%Y-%m-%d %H:%M:%S"`
echo $CURRENT_TIME" STARTED" >> log.txt



#Run script.
./run.sh 1>> log.txt 2> err.txt



#Do something if err.txt is not empty.
if [ -s err.txt ]
then
    #errors
    bash notify.sh "Error: wot-console-wn8"
    cat err.txt >> log.txt
    echo "There were errors." >> log.txt
else
    #no errors
    bash notify.sh "Success: wot-console-wn8"
    echo "No errors." >> log.txt
fi



#Print time of the finish.
CURRENT_TIME=`date "+%Y-%m-%d %H:%M:%S"`
printf "$CURRENT_TIME FINISHED\n\n\n\n" >> log.txt



#Truncate log.
tail -2000 log.txt > temp
cat temp > log.txt
rm temp
