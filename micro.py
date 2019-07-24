import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import *
import random

class Micro(sc2.BotAI):

    async def offensive_force_buildings(self):

        if self.units(SUPPLYDEPOT).ready.exists:
            cc = self.units(COMMANDCENTER).ready
            oc = self.units(ORBITALCOMMAND).ready
            loc = await self.find_placement(UnitTypeId.COMMANDCENTER, self.townhalls.random.position, placement_step=7)

            if cc.exists and len(self.units(BARRACKS)) <=1:
                if self.can_afford(BARRACKS) and not self.already_pending(BARRACKS):
                        await self.build(BARRACKS,loc)
            if self.units(BARRACKS).ready.exists and  len(self.units(FACTORY))<1:
                if self.can_afford(FACTORY) and not self.already_pending(FACTORY):
                        await self.build(FACTORY, loc)
            if self.units(FACTORY).ready.exists and len(self.units(STARPORT)) <2 :
                    if self.can_afford(STARPORT) and not self.already_pending(STARPORT):
                        await self.build(STARPORT, loc)

            for b in self.units(BARRACKS).ready:
                if b.has_add_on==False:
                    pass
                elif not self.units(BARRACKSTECHLAB).ready.exists:
                    if self.can_afford(BARRACKSTECHLAB) and not self.already_pending(BARRACKSTECHLAB):
                        await self.do(b.build(BARRACKSTECHLAB))
                elif self.units(BARRACKSTECHLAB).ready.exists:
                    if self.can_afford(BARRACKSREACTOR) and not self.already_pending(BARRACKSREACTOR):
                        await self.do(b.build(BARRACKSREACTOR))
                        #await self.do(b(AbilityId.BUILD_REACTOR_BARRACKS))
    async def build_offensive_force(self):
    #    fb =self.units(BARRACKS).ready.first
        techTags = []
        reactorTags = []
        for techlab in self.units(BARRACKSTECHLAB).ready:
            techTags.append(techlab.tag)
        for reactor in self.units(BARRACKSREACTOR).ready:
            reactorTags.append(reactor.tag)

        for gw in self.units(BARRACKS).ready:
            if gw.add_on_tag in techTags:
                if gw.noqueue:
                    if self.can_afford(MARAUDER):
                        await self.do(gw.train(MARAUDER))
            elif gw.add_on_tag in reactorTags:
                if self.can_afford(MARINE):
                    if len(gw.orders) < 2:
                        await self.do(gw.train(MARINE))

    async def attack(self):
        force = self.units(UnitTypeId.MARINE) | self.units(UnitTypeId.MARAUDER)
        #if self.units(m).amount > aggressive_units[m][0] and self.units(m).amount > aggressive_units[m][1]:
        kill =False
        aggressive_units = {MARINE: [10, 0],
                            MARAUDER: [5, 0],}
        for m in force:
            enemyGroundUnits = self.known_enemy_units.not_flying.closer_than(10, m)
            abilities = await self.get_available_abilities(m)
            if len(self.units(MARINE))> 10 or len(self.units(MARAUDER)) >5:
                await self.do(m.attack(self.enemy_start_locations[0]))

            if not m.has_buff(BuffId.STIMPACK) and m.health_percentage >= 44/45:
                if enemyGroundUnits:
                    if AbilityId.EFFECT_STIM_MARINE in abilities:
                        await self.do(m(AbilityId.EFFECT_STIM_MARINE))
                    if AbilityId.EFFECT_STIM_MARAUDER in abilities:
                        await self.do(m(AbilityId.EFFECT_STIM_MARAUDER))

            enemy = self.known_enemy_units.not_flying.closer_than(40, m) # hardcoded attackrange of 5
            if enemy:
                enemy = enemy.sorted(lambda x: x.distance_to(m))
                closestEnemy = enemy[0]
                await self.do(m.attack(closestEnemy))

    async def medic(self):
        for sg in self.units(STARPORT).ready.noqueue:
            if self.can_afford(MEDIVAC) and self.supply_left > 0:
                await self.do(sg.train(MEDIVAC))

        force = self.units(MARINE) | self.units(MARAUDER)
        if len(force)>3:
            pick = len(force) -1

        for mv in self.units(UnitTypeId.MEDIVAC):
            for unit in force:
                if unit.health_percentage < 99/100:
                    await self.do(mv.attack(unit))
                elif len(force)> 3:
                    await self.do(mv.attack(force[pick]))
