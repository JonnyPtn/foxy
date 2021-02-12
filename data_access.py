from foxholewar import foxholewar
from influxdb import InfluxDBClient
import logging
import time
import sys

from dataclasses import dataclass
from discord.ext import tasks, commands

# Our db client running on the same host
db = InfluxDBClient(host='localhost', port=8086)
db.switch_database('foxy')

@dataclass
class Report:
    totalColonialCasualties: int = 0
    totalWardenCasualties: int = 0
    lastHourColonialCasualties: int = 0
    lastHourWardenCasualties: int = 0
    version: int = 0


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

        hasUpdated = False
        maps = self.client.fetchMapList()
        for map in maps:
            report = self.client.fetchReport(map)
            totalColonialCasualties += report.colonialCasualties
            totalWardenCasualties += report.wardenCasualties
            totalEnlistments += report.totalEnlistments
            currentReport = await self.generateWarReport(map.prettyName)
            if not currentReport or currentReport.version < report.version:
                hasUpdated = True
                db.write_points([
                    {
                        "measurement": map.rawName,
                        "fields": {
                                "colonialCasualties": report.colonialCasualties,
                                "wardenCasualties": report.wardenCasualties,
                                "dayOfWar": report.dayOfWar,
                                "totalEnlistments": report.totalEnlistments,
                                "version": report.version
                                }
                    }
                ])

        if hasUpdated:
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
            'SELECT "colonialCasualties", "wardenCasualties", "version" FROM "foxy"."autogen"."' + map + '" WHERE time > now() - 1h')
        if not data:
            logging.log(logging.ERROR, f"Failed to get war report from database for {map}")
            return None

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
            report.version = max(report.version, point["version"])

        report.lastHourColonialCasualties = report.totalColonialCasualties - minColonialCasualties
        report.lastHourWardenCasualties = report.totalWardenCasualties - minWardenCasualties
        end = time.process_time()
        logging.log(logging.INFO, "Generated war report, took " +
                    str(end - start) + " seconds")
        return report
