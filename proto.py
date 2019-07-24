import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import *
import random
from micro import Micro
from macro import Macro
from sc2.ids.ability_id import AbilityId


class SentdeBot(sc2.BotAI):
    def __init__(self):
        self.ITERATIONS_PER_MINUTE = 165
        self.MAX_WORKERS = 70
        self.combinedActions = []
        self.cc_count = 4
        self.upgrades = 0
        self.timer = 0
        self.barracks=0

    async def on_step(self, iteration):
        self.iteration = iteration
        await self.distribute_workers()
        await self.build_workers()
        await self.build_supplydepo()
        await self.build_refineries()
        await self.expand()
        await self.offensive_force_buildings()
        await self.build_offensive_force()
        await self.attack()
        await self.orbital()
        await self.engineering_bay()
        await self.medic()
        await self.research()


    async def engineering_bay(self):
        #Engineering Bay
        await Macro.engineering_bay(self)
    async def build_workers(self):

        await Macro.build_workers(self)

    async def build_supplydepo(self):
        await Macro.build_supplydepo(self)

    async def build_refineries(self):
        await Macro.build_refineries(self)

    async def expand(self):
        await Macro.expand(self)

    async def offensive_force_buildings(self):
        await Micro.offensive_force_buildings(self)

    async def build_offensive_force(self):
        await Micro.build_offensive_force(self)

    async def orbital(self):
        await Macro.orbital(self)

    async def attack(self):
        await Micro.attack(self)

    async def medic(self):
        await Micro.medic(self)

    async def research(self):
        await Macro.research(self)

run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Terran, SentdeBot()),
    Computer(Race.Terran, Difficulty.Easy)
    ], realtime=False )
