#!/bin/bash
#Kommentar SBATCH --nodes=1
#SBATCH --cpus-per-task=80
#SBATCH --time=30:00
#Kommentar SBATCH --mem=180000mb
#SBATCH --export=ALL
#SBATCH -J c_new
#SBATCH --array=0-0	#TODO 10
#SBATCH --partition=dev_single
#Kommentar SBATCH --gres=gpu:1

#distractor within parts in air has START_AT_IMAGE_NUMBER 0
#distractor within parts on floor 0 has START_AT_IMAGE_NUMBER 100000
#distractor within parts on floor 30 has START_AT_IMAGE_NUMBER 200000
#distractor within parts on floor 60 has START_AT_IMAGE_NUMBER 300000
#distractor within parts on floor 70 has START_AT_IMAGE_NUMBER 400000
#distractor within parts on floor 80 has START_AT_IMAGE_NUMBER 500000
#distractor within parts on top of another has START_AT_IMAGE_NUMBER 600000

PRE_LABELING="New"
NUMBER_OF_IMAGES=10	#TODO 10000
START_AT_IMAGE_NUMBER="$((SLURM_ARRAY_TASK_ID*NUMBER_OF_IMAGES+0))"
THREAD_LIMIT=1	#TODO 80
DIR_INPUT="../Amira/OutputTrain/"
DIR_OUTPUT="OutputTrain/"
DIR_BACKGROUND_TEXTURES="../Amira/Textures/"

python3 script.py -- --START_AT_IMAGE_NUMBER="$START_AT_IMAGE_NUMBER" --PRE_LABELING="$PRE_LABELING" --NUMBER_OF_IMAGES="$NUMBER_OF_IMAGES" --THREAD_LIMIT="$THREAD_LIMIT" --DIR_INPUT="$DIR_INPUT" --DIR_OUTPUT="$DIR_OUTPUT" --DIR_BACKGROUND_TEXTURES="$DIR_BACKGROUND_TEXTURES"
