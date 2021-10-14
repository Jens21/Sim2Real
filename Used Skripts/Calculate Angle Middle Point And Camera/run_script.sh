#!/bin/bash
#SBATCH --nodes=1
#SBATCH --cpus-per-task=80
#SBATCH --time=30:00
#SBATCH --mem=180000mb
#SBATCH --export=ALL
#SBATCH -J cal_angl
#SBATCH --array=0-0 #TODO 80
#SBATCH --partition=dev_single
#Kommentar SBATCH --gres=gpu:1

python calculate_angle_middle_point_and_camera.py
