from foxholewar import foxholewar
from influxdb import InfluxDBClient
import logging
import time
import sys

from discord.ext import tasks, commands

# Our db client running on the same host
db = InfluxDBClient(host='localhost', port=8086)
db.switch_database('foxy')


class Report:
    totalColonialCasualties = 0
    totalWardenCasualties = 0
    lastHourColonialCasualties = 0
    lastHourWardenCasualties = 0


class DataAccess(commands.Cog):

    def __init__(self):
        self.updateData.start()
        self.client = foxholewar.Client()

    @tasks.loop(seconds=30)
    async def updateData(self):
        start = time.process_time()
        totalColonialCasualties = 0
        totalWardenCasualties = 0
        totalEnlistments = 0

        maps = self.client.getMapList()
        for map in maps:
            report = self.client.getReport(map)
            totalColonialCasualties += report.colonialCasualties
            totalWardenCasualties += report.wardenCasualties
            totalEnlistments += report.totalEnlistments
            db.write_points([
                {
                    "measurement": map.rawName,
                    "fields": {
                            "colonialCasualties": report.colonialCasualties,
                            "wardenCasualties": report.wardenCasualties,
                            "dayOfWar": report.dayOfWar,
                            "totalEnlistments": report.totalEnlistments
                            }
                }
            ])

        db.write_points([
            {
                "measurement": "totals",
                "fields": {
                    "colonialCasualties": totalColonialCasualties,
                    "wardenCasualties": totalWardenCasualties,
                }
            }
        ])
        end = time.process_time()
        logging.log(logging.INFO, "War and map data updated, took " +
                    str(end - start) + " seconds")

    async def generateWarReport(self, map):
        start = time.process_time()
        if map in foxholewar.prettyMapNameToRaw:
            map = foxholewar.prettyMapNameToRaw[map]
        data = db.query(
            'SELECT "colonialCasualties", "wardenCasualties" FROM "foxy"."autogen"."' + map + '" WHERE time > now() - 1h')
        if not data:
            raise Exception('Faild to get data for map: ' + map)

        report = Report()
        minColonialCasualties = sys.maxsize
        minWardenCasualties = sys.maxsize
        for point in data.get_points():
            colonialCasualties = point["colonialCasualties"]
            wardenCasualties = point["wardenCasualties"]
            report.totalColonialCasualties = max(
                report.totalColonialCasualties, colonialCasualties)
            report.totalWardenCasualties = max(
                report.totalWardenCasualties, wardenCasualties)
            minColonialCasualties = min(
                minColonialCasualties, colonialCasualties)
            minWardenCasualties = min(minWardenCasualties, wardenCasualties)

        report.lastHourColonialCasualties = report.totalColonialCasualties - minColonialCasualties
        report.lastHourWardenCasualties = report.totalWardenCasualties - minWardenCasualties
        end = time.process_time()
        logging.log(logging.INFO, "Generated war report, took " +
                    str(end - start) + " seconds")
        return report
