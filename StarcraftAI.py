import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import *
from sc2.constants import COMBATSHIELD
import random

class SentdeBot(sc2.BotAI):
    def __init__(self):
        self.ITERATIONS_PER_MINUTE = 165
        self.MAX_WORKERS = 70
        self.combinedActions = []
        self.cc_count = 4

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


    async def build_workers(self):
        comcen = self.units(COMMANDCENTER).ready
        orbcom = self.units(ORBITALCOMMAND).ready
        if self.units(UnitTypeId.BARRACKS).ready.exists and self.can_afford(UnitTypeId.ORBITALCOMMAND) and not self.already_pending(ORBITALCOMMAND): # check if orbital is affordable
            for comcent in self.units(UnitTypeId.COMMANDCENTER).ready.noqueue: # .idle filters idle command centers
                await self.do(comcent(AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND))
        try:
            if  len(self.units(SCV)) <= self.MAX_WORKERS and self.can_afford((SCV)):
                if comcen.exists:
                    for cc in self.units(COMMANDCENTER).ready.noqueue:
                        await self.do(cc.train(SCV))
                if orbcom.exists and len(self.units(SCV)) <= self.MAX_WORKERS:
                    for oc in self.units(ORBITALCOMMAND).ready.noqueue:
                        await self.do(oc.train(SCV))
        except:
            pass
    async def build_supplydepo(self):
        if (self.supply_left < 10  and not self.already_pending(SUPPLYDEPOT) and self.can_afford(UnitTypeId.SUPPLYDEPOT)):
            cc = self.units(COMMANDCENTER).ready
            oc = self.units(ORBITALCOMMAND).ready
            if self.can_afford(SUPPLYDEPOT):
                if cc.exists:
                    await self.build(SUPPLYDEPOT, near=cc.first)
                if oc.exists:
                    await self.build(SUPPLYDEPOT, near=oc.first)

            for depot in self.units(UnitTypeId.SUPPLYDEPOT).ready:
                await self.do(depot(AbilityId.MORPH_SUPPLYDEPOT_LOWER))

    async def build_refineries(self):
        cc = self.units(COMMANDCENTER).ready
        oc = self.units(ORBITALCOMMAND).ready
        if cc.exists:
            a =self.units(COMMANDCENTER).ready
        if oc.exists:
            a=self.units(ORBITALCOMMAND).ready
            
        for oc in self.units(COMMANDCENTER).ready:
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
                
    async def offensive_force_buildings(self):

        #print(self.iteration / self.ITERATIONS_PER_MINUTE)        
        if self.units(SUPPLYDEPOT).ready.exists:

            cc = self.units(COMMANDCENTER).ready
            oc = self.units(ORBITALCOMMAND).ready
            loc = await self.find_placement(UnitTypeId.BARRACKS, self.townhalls.random.position, placement_step=7)

            b = self.units(BARRACKS).ready

            if cc.exists:
                if len(self.units(BARRACKS)) < ((self.iteration / self.ITERATIONS_PER_MINUTE)/2) and len(self.units(BARRACKS)) <=4 :
                    if self.can_afford(BARRACKS) and not self.already_pending(BARRACKS):
                            await self.build(BARRACKS, loc)
            if oc.exists:
                if len(self.units(BARRACKS)) == ((self.iteration / self.ITERATIONS_PER_MINUTE)) and len(self.units(BARRACKSTECHLAB)) <=4:
                    if self.can_afford(BARRACKS) and not self.already_pending(BARRACKS):
                            await self.build(BARRACKS,loc)
                if self.units(BARRACKS).ready.exists and not self.units(FACTORY):
                    if self.can_afford(FACTORY) and not self.already_pending(FACTORY):
                            await self.build(FACTORY, loc)

                if self.units(BARRACKS).ready.exists:
                    for tech in self.units(BARRACKS).ready.noqueue:
                            if self.can_afford(BARRACKSTECHLAB) and  not self.already_pending(BARRACKSTECHLAB):
                                await self.do(tech.build(BARRACKSTECHLAB))
                        
                if self.units(FACTORY).ready.exists:
                    if len(self.units(STARPORT)) < ((self.iteration / self.ITERATIONS_PER_MINUTE)/2) and len(self.units(STARPORT)) <1 :
                        if self.can_afford(STARPORT) and not self.already_pending(STARPORT):
                            await self.build(STARPORT, loc)

    async def build_offensive_force(self):
        for gw in self.units(BARRACKS).ready.noqueue:
            if  self.supply_left > 0 and self.units(BARRACKSTECHLAB).ready.exists:
                if self.can_afford(MARAUDER):
                    await self.do(gw.train(MARAUDER))
                
        for sg in self.units(STARPORT).ready.noqueue:
            if self.can_afford(MEDIVAC) and self.supply_left > 0:
                await self.do(sg.train(MEDIVAC))

    def find_target(self, state):
        if len(self.known_enemy_units) > 0:
            return random.choice(self.known_enemy_units)
        elif len(self.known_enemy_structures) > 0:
            return random.choice(self.known_enemy_structures)
        else:
            return self.enemy_start_locations[0]

    async def attack(self):
        # {UNIT: [n to fight, n to defend]}
        aggressive_units = {MARINE: [15, 0],
                            MARAUDER: [15, 0],}
                    
        for UNIT in aggressive_units:
            if self.units(UNIT).amount > aggressive_units[UNIT][0] and self.units(UNIT).amount > aggressive_units[UNIT][1]:
                for s in self.units(UNIT).idle:
                    await self.do(s.attack(self.find_target(self.state)))

        for mv in self.units(UnitTypeId.MEDIVAC):
            m = self.units(MARAUDER).random
            await self.do(mv.attack(m))
                
        for m in self.units(UnitTypeId.MARAUDER):
            enemyGroundUnits = self.known_enemy_units.not_flying.closer_than(20, m) # hardcoded attackrange of 5
            if enemyGroundUnits:
                enemyGroundUnits = enemyGroundUnits.sorted(lambda x: x.distance_to(m))
                closestEnemy = enemyGroundUnits[0]
                await self.do(m.attack(closestEnemy))
         
    async def orbital(self):
        
        if self.units(UnitTypeId.BARRACKS).ready.exists and self.can_afford(UnitTypeId.ORBITALCOMMAND) : # check if orbital is affordable
            if self.units(UnitTypeId.COMMANDCENTER).ready.exists and not self.already_pending(ORBITALCOMMAND) :
                for comcen in self.units(UnitTypeId.COMMANDCENTER).noqueue: # .idle filters idle command centers
                    await self.do(comcen(AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND))
            for oc in self.units(UnitTypeId.ORBITALCOMMAND).filter(lambda x: x.energy >= 50):
                mfs = self.state.mineral_field.closer_than(10, oc)
                if mfs:
                    mf = max(mfs, key=lambda x:x.mineral_contents)
                    await self.do(oc(AbilityId.CALLDOWNMULE_CALLDOWNMULE, mf))
            


run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Terran, SentdeBot()),
    Computer(Race.Zerg, Difficulty.Medium)
    ], realtime=False )

 
