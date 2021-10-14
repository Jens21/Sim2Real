#!/bin/bash
#SBATCH --nodes=1
#KommentarSBATCH --cpus-per-task=40
#SBATCH --time=30:00
#KommentarSBATCH --mem=752000mb   
#SBATCH --export=ALL
#SBATCH -J TrainSim2Real
#SBATCH --partition=dev_gpu_4
#SBATCH --gres=gpu:1

python CalculateMiddleMinMaxDistanceOfObjectToCamera.py
