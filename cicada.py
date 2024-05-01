#
# Cicada simulation
#
# Bryan Clair 2024
#
import sys
import math
from collections import defaultdict
from numpy import random

class Ecosystem:
    def __init__(self,
                 genotype = [1],
                 larval_survival_rate = 1,
                 emergence_success_rate = 1,
                 clutch_rate = 1,
                 initial_size =  1000,
                 initial_saturated = True,
                 initial_random = False
                 ):
        """
        genotype is a number, the periodicity of emergence.
        for each genotype, maintain a list of how many individuals of each age.
        """
        self.counts = {}
        for g in genotype:
            self.counts[g] = [0]*g
            n = initial_size if not initial_random else math.floor(random.normal(initial_size,.05*initial_size))
            if initial_saturated:
                for i in range(g):
                    self.counts[g][i] = n/g
            else:
                self.counts[g][g-1] = n

        self.gen = 0

        self.larval_survival_rate = larval_survival_rate
        self.emergence_success_rate = emergence_success_rate
        self.clutch_rate = clutch_rate
        
    def __str__(self):
        out = 'Generation %d\n--------------\n' % self.gen
        for g in self.counts:
            out += "%2d: " % g
            for c in self.counts[g]:
                out += "%5d " % c
            out += '\n'
        return out

    def tick(self):
        """One year passes"""
        self.gen += 1
        emergent = []

        # underground action
        for g in self.counts:
            # the mature adults emerge (with some rate)
            e = math.floor(self.counts[g].pop(0) * self.emergence_success_rate)
            if e > 0:
                emergent.append((g,e))
            
            # everyone else gets a year older and some die
            for i in range(len(self.counts[g])):
                self.counts[g][i] = math.floor(self.counts[g][i] * self.larval_survival_rate)

        # breeding season!
        offspring = self.breed(emergent)
        for g in self.counts:
            #print(g,offspring[g])
            self.counts[g].append(offspring[g])

    def breed(self, emergent):
        """
        Take a dictionary of (g,e) pairs where g is the periodic genus
        and e is the number of emergent adults.
        Return a dictionary of (g,o) pairs where o is the number of offspring.
        """
        if self.__class__ == Ecosystem:
            raise NotImplementedError

class HybridModel(Ecosystem):
    """
    Yoshimura et al, 2008. Breeding pairs proportional to % of adult population.
    All pairs can breed, offspring have the smaller of the two parent periods.
    Clutch size proportional to period (of child).
    Best if used with larval survival rate below 1.
    """
    def breed(self, emergent):
        tot_emergent = 0
        for (g,n) in emergent:
            tot_emergent += n
            
        offspring = defaultdict(lambda:0,{})
        for (g1, n1) in emergent:
            for (g2, n2) in emergent:
                child_g = min(g1,g2)  # hybrids get smaller of two cycles
                breedpairs = n1*n2/tot_emergent
                offspring[child_g] += math.floor(breedpairs * self.clutch_rate * child_g)

        return offspring

class Proportional(Ecosystem):
    """
    Breeding pairs proportional to % of adult population.
    Only matched cicadas can breed - no hybrids.
    """
    def breed(self, emergent):
        tot_emergent = 0
        for (g,n) in emergent:
            tot_emergent += n 

        offspring = defaultdict(lambda:0,{})
        for (g, n) in emergent:
            offspring[g] += math.floor(n * (n / tot_emergent) * self.clutch_rate)

        return offspring

class RealSex(Ecosystem):
    """
    Emerging adults are randomly paired.
    Only adults with matching periods can breed.
    """
    def breed(self, emergent):
        adults = []
        for (g,n) in emergent:
            adults += [g]*n
        random.shuffle(adults)

        half = len(adults)//2
        
        offspring = defaultdict(lambda:0,{})
        for i in range(half):
            if adults[i] == adults[i+half]:
                offspring[adults[i]] += self.clutch_rate

        return offspring

if __name__ == '__main__':
    simlength = 100
    if len(sys.argv) > 1:
        simlength = int(sys.argv[1])

    # Couldn't get the Yashimoto model to reproduce (no pun intended)
    world1 = HybridModel(genotype = range(1,21),
                         initial_size = 1000,
                         larval_survival_rate = 0.99,
                         emergence_success_rate = 0.15,
                         clutch_rate = 5,
                         initial_saturated = True)

    # This produces prime periods
    world2 = Proportional(genotype = range(1,11),
                        initial_size = 10,
                        emergence_success_rate = .5,
                        clutch_rate = 3,
                        initial_saturated = False,
                          initial_random = True)
    
    #
    # This is a very simple model that produces prime periods consistently:
    #
    # All offspring survive their larval stage to emerge as adults.
    # Half of all adults are eaten by predators
    # Adults pair off randomly and only produce offspring if they have the same period.
    # Each pair of compatible adults produces 6 offspring.
    #
    world3 = RealSex(genotype = range(1,13),
                        initial_size = 12,
                        emergence_success_rate = .5,
                        clutch_rate = 6,
                        initial_saturated = False,
                        initial_random = False)

    world = world3

    for year in range(simlength):
        if (simlength <= 200):
            print(world)
        elif (year % 97 == 0):
            print(world)

        world.tick()

    print(world)
