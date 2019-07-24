import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import *
import random

class Macro(sc2.BotAI):
    def __init__(self):
        self.ITERATIONS_PER_MINUTE = 165
        self.MAX_WORKERS = 70
        self.combinedActions = []
        self.cc_count = 4
        self.upgrades = 0
        self.timer = 0
        self.barracks=0

    async def engineering_bay(self):
        #Engineering Bay
        loc = await self.find_placement(UnitTypeId.BARRACKS, self.townhalls.random.position, placement_step=7)
        if not self.units(ENGINEERINGBAY).exists and self.units(BARRACKS).ready.exists:
            if self.can_afford(ENGINEERINGBAY) and not self.already_pending(ENGINEERINGBAY):
                await self.build(ENGINEERINGBAY, near=loc)
        elif self.units(ENGINEERINGBAY).exists and self.can_afford(ENGINEERINGBAYRESEARCH_TERRANINFANTRYWEAPONSLEVEL1):
            if self.upgrades == 3:
                self.upgrades =4
                eb = self.units(ENGINEERINGBAY).ready.first
                await self.do(eb(ENGINEERINGBAYRESEARCH_TERRANINFANTRYWEAPONSLEVEL1))

    async def build_workers(self):
        a =self.units(COMMANDCENTER).ready.noqueue
        b= self.units(ORBITALCOMMAND).ready.noqueue
        try:
            if  len(self.units(SCV)) <= self.MAX_WORKERS and self.can_afford((SCV)):
                if len(self.units(SCV)) <= self.MAX_WORKERS:
                    if not self.units(BARRACKS).ready.exists:
                        for cc in a:
                            await self.do(cc.train(SCV))
                    elif self.units(BARRACKS).ready.exists:
                        for oc in b:
                            await self.do(oc.train(SCV))
        except:
            pass
    async def build_supplydepo(self):
        loc = await self.find_placement(UnitTypeId.SUPPLYDEPOT, self.townhalls.random.position, placement_step=2)

        if (self.supply_left < 10  and not self.already_pending(SUPPLYDEPOT) and self.can_afford(UnitTypeId.SUPPLYDEPOT)):
            cc = self.units(COMMANDCENTER).ready
            oc = self.units(ORBITALCOMMAND).ready
            if self.can_afford(SUPPLYDEPOT):
                await self.build(SUPPLYDEPOT, near=loc)

            for depot in self.units(UnitTypeId.SUPPLYDEPOT).ready:
                await self.do(depot(AbilityId.MORPH_SUPPLYDEPOT_LOWER))

    async def build_refineries(self):

        a =self.units(COMMANDCENTER).ready | self.units(ORBITALCOMMAND).ready
        for oc in a:
            vaspenes = self.state.vespene_geyser.closer_than(15.0, oc)
            for vaspene in vaspenes:
                if len(self.units(SUPPLYDEPOT))> 0 and len(self.units(REFINERY))<(self.iteration / self.ITERATIONS_PER_MINUTE)/2:
                    if not self.can_afford(REFINERY):
                        break
                    worker = self.select_build_worker(vaspene.position)
                    if worker is None:
                        break
                    if not self.units(REFINERY).closer_than(1.0, vaspene).exists:
                        await self.do(worker.build(REFINERY, vaspene))

    async def expand(self):
        if self.can_afford(COMMANDCENTER) and len(self.units(ORBITALCOMMAND))*22 <= len(self.units(SCV)) and len(self.units(ORBITALCOMMAND))<(self.iteration / self.ITERATIONS_PER_MINUTE)/2 :
            if not self.already_pending(COMMANDCENTER):
                cc = self.units(COMMANDCENTER).ready
                oc = self.units(ORBITALCOMMAND).ready
                if oc.exists and len(self.units(COMMANDCENTER))<1:
                    await self.expand_now()
                if len(self.units(ORBITALCOMMAND))<=self.cc_count:
                    await self.expand_now()
    async def orbital(self):

        if self.units(UnitTypeId.BARRACKS).ready.exists and self.can_afford(UnitTypeId.ORBITALCOMMAND) : # check if orbital is affordable
            if self.units(UnitTypeId.COMMANDCENTER).ready.exists and not self.already_pending(ORBITALCOMMAND) :
                for comcen in self.units(UnitTypeId.COMMANDCENTER).idle: # .idle filters idle command centers
                    abilities = await self.get_available_abilities(comcen)
                    if AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND in abilities:
                        await self.do(comcen(AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND))
            for oc in self.units(ORBITALCOMMAND).filter(lambda x: x.energy >= 50):
                mfs = self.state.mineral_field.closer_than(10, oc)
                if mfs:
                    mf = max(mfs, key=lambda x:x.mineral_contents)
                    await self.do(oc(AbilityId.CALLDOWNMULE_CALLDOWNMULE, mf))

    async def research(self):
        if self.units(BARRACKSTECHLAB).exists:
            for i in self.units(BARRACKSTECHLAB):
                abilities = await self.get_available_abilities(i)

                if self.can_afford(BARRACKSTECHLABRESEARCH_STIMPACK) and  self.upgrades == 0:
                    await self.do(i(BARRACKSTECHLABRESEARCH_STIMPACK))
                    self.upgrades =1

                elif self.can_afford(RESEARCH_COMBATSHIELD) and  self.upgrades == 1:
                    if self.already_pending_upgrade(UpgradeId.STIMPACK) == 1:
                        await self.do(i(RESEARCH_COMBATSHIELD))
                        self.upgrades =2
                elif self.can_afford(RESEARCH_CONCUSSIVESHELLS) and self.upgrades == 2:
                    await self.do(i(RESEARCH_CONCUSSIVESHELLS))
                    self.upgrades =3
