#!/bin/bash
#SBATCH --nodes=1
#SBATCH --cpus-per-task=80
#SBATCH --time=30:00
#SBATCH --mem=180000mb
#SBATCH --export=ALL
#SBATCH -J del_fast
#SBATCH --array=0-0 #TODO 80
#SBATCH --partition=dev_single
#KommentarSBATCH --gres=gpu:4

python Create_Train_Test_FFB6D_File.py