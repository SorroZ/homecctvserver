#!/usr/bin/python

import subprocess
import time
import MySQLdb
import config # Config file for database connection

class CameraHandler:

    def __init__(self):
        self.location = '/home/daniel/cctv/'
        self.resolution = '640x480'
        self.skipframes = 2
        return

    def snap(self, identifier):
        name = self.currentTime() + '.jpg'
        subprocess.call(['fswebcam', '-r', self.resolution,
                         self.location + name, '-S', str(self.skipframes)])
        self.writeToDB(name, identifier)

    def currentTime(self):
        return time.strftime("%d_%m_%Y_%H_%M_%S")

    def writeToDB(self, name, t):
        db = self.connectToDB()
        cursor = db.cursor()
        sql = "INSERT INTO pictures (filename, type) \
            VALUES ('%s', '%s')" % \
            (name, t)
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()

        db.close()

    def connectToDB(self):
        return MySQLdb.connect(config.HOST, config.DATABASE, config.USER, config.PASSWORD)
