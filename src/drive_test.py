from drive_api import DriveSetup
import os

os.chdir("..")

drive_client = DriveSetup()

drive_client.create_random_img()