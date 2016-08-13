from random import random, uniform, randint
import logging
#logging.basicConfig(filename='suchpy_log.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

from supplychainpy.demand.forecast_demand import Forecast

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Verbose:
    def __init__(self, parents: list = None, standard_error: float = None, smoothing_level: float = None):
        print('inside __init__')
        self.arg1 = parents
        self.arg2 = standard_error
        self.arg3 = smoothing_level

    def __call__(self, f):
        print('Inside __call__')

        def annotate(*args):
            for i in args:
                print('inside methods {}'.format(i))
            f(*args)

        return annotate()


class Individual:
    _genome = 0

    def __init__(self, name: str = 'offspring', overide: bool = False, gene_count: int = 12):
        self._name = name
        self._gene_count = gene_count
        if not overide:
            self._genome = self.__genome_generator()

    def __repr__(self):
        return '{}: {}'.format(self._name, self._genome)

    @property
    def gene_count(self) -> int:
        return self.gene_count

    @gene_count.setter
    def gene_count(self, value: int):
        self._gene_count = value

    @property
    def genome(self):
        return self._genome

    @genome.setter
    def genome(self, val: tuple):
        self._genome = val

    @property
    def name(self):
        return self._name

    def __genome_generator(self):
        genome = tuple([uniform(0, 1) for i in range(0, self._gene_count)])
        return genome


class Population:
    """ Create a population of individuals to reproduce.

    """
    __slots__ = ['individuals', 'mutation_probability']
    _recombination_type = ('single_point', 'two_point', 'uniform')

    def __init__(self, individuals: list, mutation_probability: float = 0.2):
        self.individuals = individuals
        self.mutation_probability = mutation_probability

    def reproduce(self, recombination_type:str='single_point') -> list:
        log.debug('{} reproduction started'.format(recombination_type))
        if recombination_type == self._recombination_type[0]:
            yield [i for i in self._recombination()][0]

    def _recombination(self) -> object:

        genome_count = 0
        new_individual = {}
        new_individual_two = {}
        population = []
        mutation_count = 0
        population_allele_count = 0
        number_of_mutations_allowed = 0
        mutation_index = 0
        try:

            if len(self.individuals) > 1:
                for index, individual in enumerate(self.individuals):
                    for key, value in individual.items():
                        population_allele_count = len(self.individuals) * len(individual.items())
                        number_of_mutations_allowed = round(population_allele_count * self.mutation_probability)
                        mutation_index += 1
                        if (genome_count <= 5 and len(new_individual) < 12) or (
                                            12 < genome_count <= 18 and len(new_individual) < 12):

                            if mutation_index == number_of_mutations_allowed:
                                new_individual.update(self._mutation({key: value}))
                                genome_count += 1
                                mutation_index = 0
                                mutation_count += 1
                            else:
                                new_individual.update({key: value})
                                genome_count += 1

                        elif genome_count >= 6 and len(new_individual_two) < 12 or 18 < genome_count <= 24 and len(
                                new_individual) < 12:

                            if mutation_index == number_of_mutations_allowed:
                                new_individual_two.update(self._mutation({key: value}))
                                genome_count += 1
                                mutation_index = 0
                                mutation_count += 1
                            else:
                                new_individual.update({key: value})
                                genome_count += 1

                        else:
                            genome_count += 1

                        if genome_count == 24:
                            genome_count = 0
                            yield (new_individual)
                            yield (new_individual_two)

            else:
                raise ValueError()

        except ValueError:
            print('Population Size is too small for effective genetic recombination and reproduction of offspring')

            return

    @staticmethod
    def _mutation(gene: dict):

        original_gene = [[k, v] for k, v in gene.items()]

        def mutate():

            if original_gene[0][1] == 0:
                log.debug(
                    'A mutation occurred on gene {}. The result of the mutation is {}'.format({original_gene[0][0]: 0},
                                                                                              {original_gene[0][0]: 1}))
                return {original_gene[0][0]: 1}
            elif original_gene[0][1] == 1:
                log.debug(
                    'A mutation occurred on gene {}. The result of the mutation is {}'.format({original_gene[0][0]: 1},
                                                                                              {original_gene[0][0]: 0}))
                print('mutation')
                return {original_gene[0][0]: 0}
            else:
                return {original_gene[0][0]: original_gene[0][0]}

        return mutate()


class DiversifyPopulation(Population):
    def __init__(self, individuals: list):
        super().__init__(individuals)


class OptimiseSmoothingLevelGeneticAlgorithm:
    __generation = 0

    def __init__(self, orders: list, **kwargs):
        self.__orders = orders
        self.__average_order = kwargs['average_order']
        self.__population_size = kwargs['population_size']
        self.__standard_error = kwargs['standard_error']
        self.__smoothing_level = kwargs['smoothing_level']
        self.__initial_population = self.initialise_smoothing_level_evolutionary_algorithm_population()

    @property
    def initial_population(self):
        return self.__initial_population

    @property
    def population_size(self):
        return self.__population_size

    @population_size.setter
    def population_size(self, population_size):
        self.__population_size = population_size

    def initialise_smoothing_level_evolutionary_algorithm_population(self):
        """ Starts the process for creating the population. The number of parents is specified during the
         initialisation of the class. """

        parents = []
        parents_population = []

        while len(parents_population) < self.__population_size:
            for i in range(0, self.__population_size):
                parent = Individual(name='parent')
                log.debug('Initial parent created {}'.format(parent))
                parents.append(parent)

            populations_genome = [i for i in self.generate_smoothing_level_genome(population=parents)]
            log.debug('Population with genome {}'.format(populations_genome))
            populations_traits = [i for i in self.express_smoothing_level_genome(individuals_genome=populations_genome,
                                                                                 standard_error=self.__standard_error)]

            fit_population = [i for i in self._population_fitness(population=populations_traits)]
            log.debug('Fit population {}'.format(fit_population))
            parents_population += fit_population

        create_offspring = Population(individuals=parents_population)

        # population reproduce
        new_population = [i for i in create_offspring.reproduce()]

        if new_population is None:
            return 0

        parent_offspring_population = []
        new_individuals = []
        while len(new_population) < self.__population_size * 10:
            for po in new_population:
                pke = po.keys()
                parent_offspring_population.append(tuple(pke))

            for genome in parent_offspring_population:
                new_individual = Individual(overide=True)
                new_individual.genome = genome
                new_individuals.append(new_individual)

            # while population allele boundary ie 50 70 95 is less than specified number.
            new_population_genome = [i for i in self.generate_smoothing_level_genome(population=new_individuals)]

            new_populations_traits = [i for i in
                                      self.express_smoothing_level_genome(individuals_genome=new_population_genome,
                                                                          standard_error=self.__standard_error)]

            new_fit_population = [i for i in self._population_fitness(population=new_populations_traits)]
            new_population = new_fit_population

        new_individuals.clear()

        new_individuals = [i for i in self.create_individuals(new_population)]

        final_error = [i for i in self.generate_smoothing_level_genome(population=new_individuals)]

        minimum_smoothing_level = min(zip(final_error[0].values(), final_error[0].keys()))

        return minimum_smoothing_level

    @staticmethod
    def create_individuals(new_population: list) -> list:
        """Create individuals using class from genomes striped during processing fitness.

        Args:
            new_population (list):  new population of individual genomes.
        """
        parent_offspring_population = []

        for po in new_population:
            pke = po.keys()
            parent_offspring_population.append(tuple(pke))

        for genome in parent_offspring_population:
            new_individual = Individual(overide=True)
            new_individual.genome = genome
            yield new_individual

    @staticmethod
    def _population_fitness(population: list) -> list:
        """ Assess the population for fitness before crossover and creating next generation. Positive traits
        should be reflected by more than 70% of the genes in the genome.

        Args:
            population (list): A population with expressed traits (phenotypes). The standard_errors representing
            the genome of the individual have been calculated and expressed as one or zero if below or above
            the original standard error respectively.

        Returns:
            fit_population (list):  A population of individuals with a probability of procreating above 50%.

        """

        for individual in population:
            procreation_probability = sum(individual.values()) / len(individual.values())

            if procreation_probability >= 0.7:
                yield individual

    def generate_smoothing_level_genome(self, population: list):

        # stack parents and offspring into a list for next steps
        for parent in population:
            individuals_genome = self._run_exponential_smoothing_forecast(parent.genome)
            # print(individuals_genome)
            # individuals_traits = self._express_trait(standard_error, smoothing_level, individuals_genome)

            yield individuals_genome

    def express_smoothing_level_genome(self, individuals_genome: list, standard_error):

        # stack parents and offspring into a list for next steps
        for genome in individuals_genome:
            individuals_traits = self._express_trait(standard_error, genome)
            yield individuals_traits

    def _run_exponential_smoothing_forecast(self, individual: tuple) -> dict:

        f = Forecast(self.__orders, self.__average_order)
        simple_expo_smoothing = []
        for sm_lvl in individual:
            p = [i for i in f.simple_exponential_smoothing(sm_lvl)]
            # print(p)
            simple_expo_smoothing.append(p)

        appraised_individual = {}
        for smoothing_level in individual:
            sum_squared_error = f.sum_squared_errors_indi(simple_expo_smoothing, smoothing_level)
            standard_error = f.standard_error(sum_squared_error, len(self.__orders), smoothing_level)
            appraised_individual.update({smoothing_level: standard_error})
        # print('The standard error as a trait has been calculated {}'.format(appraised_individual))
        return appraised_individual

    def _express_trait(self, original_standard_error: float, appraised_individual: dict):
        # fitness test? over 50% of the alleles must be positive traits. give percentage score
        # print(original_standard_error)
        for key in appraised_individual:
            if appraised_individual[key] < original_standard_error:
                appraised_individual[key] = 1
            else:
                appraised_individual[key] = 0
        # print('The traits have been verified {}'.format(appraised_individual))
        # check fitness of individual to procreate. 50% of traits need to be better smoothing_levels than the original
        return appraised_individual

    def _selection_population(self, individuals_fitness: dict, appraised_individual: list):
        pass