#!/bin/bash
#SBATCH --nodes=1
#SBATCH --cpus-per-task=80
#SBATCH --time=30:00
#SBATCH --mem=180000mb
#SBATCH --export=ALL
#SBATCH -J count_num
#SBATCH --array=0-0 #TODO 80
#SBATCH --partition=dev_single
#KommentarSBATCH --gres=gpu:4

python Count_Number_Of_Uses_Per_Object.py