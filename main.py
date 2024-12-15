import math
import random
import asyncio
from parameters import Culture, GenerationStats, CropAllocation, info

class Index:
    def __init__(self, population_size: int = 100, mutation_rate: float = 0.2, info: list[Culture] = info, plot_size: int = 100, growth_time: int = 150):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.total_hct = plot_size
        self.max_growth_time = growth_time
        self.days_per_year = 365
        self.info = info
        self.generation_stats: list[GenerationStats] = []

    async def default(self, generations: int = 150, on_generation_complete = None) -> dict:
        population = self.generate_population()
        best_ever: CropAllocation | None = None
        best_ever_fitness = float('-inf')
        self.generation_stats = []

        for generation in range(generations):
            fitness_scores = [self.calculate_fitness(ind) for ind in population]
            current_best_idx = fitness_scores.index(max(fitness_scores))
            average_fitness = sum(fitness_scores) / len(fitness_scores)

            stats = GenerationStats(generation, max(fitness_scores), average_fitness)
            self.generation_stats.append(stats)

            if on_generation_complete:
                on_generation_complete(stats)

            if fitness_scores[current_best_idx] > best_ever_fitness:
                best_ever = population[current_best_idx]
                best_ever_fitness = fitness_scores[current_best_idx]

            new_population = [best_ever] if best_ever else []

            while len(new_population) < self.population_size:
                parent1 = self.best_index(population, fitness_scores)
                parent2 = self.best_index(population, fitness_scores)
                child = self.crossover(parent1, parent2)
                mutated_child = self.mutate(child)
                if mutated_child.is_valid():
                    new_population.append(mutated_child)

            population = new_population
            await asyncio.sleep(0)

        final_fitness_scores = [self.calculate_fitness(ind) for ind in population]
        population_with_fitness = list(zip(population, final_fitness_scores))
        population_with_fitness.sort(key=lambda item: item[1], reverse=True)

        solutions = []
        fitness_scores = []
        seen_keys = set()

        for allocation, fitness in population_with_fitness:
            key = allocation.get_normalized_key()
            if key not in seen_keys:
                seen_keys.add(key)
                solutions.append(allocation)
                fitness_scores.append(fitness)
            if len(solutions) >= 10:
                break

        return {"solutions": solutions, "fitnessScores": fitness_scores}

    def generate_population(self) -> list[CropAllocation]:
        population = []
        while len(population) < self.population_size:
            crop1_index, crop2_index = self.generate_valid_pair()

            min_hct_crop1 = 1
            max_hct_crop1 = self.total_hct - 1
            crop1_hct = math.floor(random.random() * (max_hct_crop1 - min_hct_crop1 + 1)) + min_hct_crop1
            crop2_hct = self.total_hct - crop1_hct

            allocation = CropAllocation(crop1_index, crop2_index, crop1_hct, crop2_hct)
            if allocation.is_valid():
                population.append(allocation)
        return population
    
    def generate_valid_pair(self) -> tuple[int, int]:
        crop1_index = math.floor(random.random() * len(self.info))
        while True:
            crop2_index = math.floor(random.random() * len(self.info))
            if crop2_index != crop1_index:
                break
        return crop1_index, crop2_index

    def calculate_fitness(self, allocation: CropAllocation) -> float:
        if not allocation.is_valid():
            return 0

        crop1 = self.info[allocation.crop1_index]
        crop2 = self.info[allocation.crop2_index]

        harvests_per_year_crop1 = math.floor(self.days_per_year / crop1.time)
        harvests_per_year_crop2 = math.floor(self.days_per_year / crop2.time)

        units_crop1 = math.floor(allocation.crop1_hct / crop1.area)
        units_crop2 = math.floor(allocation.crop2_hct / crop2.area)

        revenue_crop1 = units_crop1 * crop1.profit * harvests_per_year_crop1
        revenue_crop2 = units_crop2 * crop2.profit * harvests_per_year_crop2

        costs_crop1 = units_crop1 * crop1.cost * harvests_per_year_crop1
        costs_crop2 = units_crop2 * crop2.cost * harvests_per_year_crop2

        total_profit = revenue_crop1 + revenue_crop2 - costs_crop1 - costs_crop2

        return max(0, total_profit)

    def best_index(self, population: list[CropAllocation], fitness_scores: list[float], tournament_size: int = 5) -> CropAllocation:
        season_indices = [math.floor(random.random() * len(population)) for _ in range(tournament_size)]
        best_index = season_indices[0]
        best_fitness = fitness_scores[best_index]
        for idx in season_indices:
            if fitness_scores[idx] > best_fitness:
                best_index = idx
                best_fitness = fitness_scores[idx]
        return population[best_index]

    def crossover(self, parent1: CropAllocation, parent2: CropAllocation) -> CropAllocation:
        if random.random() < 0.5:
            return CropAllocation(
                parent1.crop1_index,
                parent1.crop2_index,
                parent2.crop1_hct,
                parent2.crop2_hct
            )
        else:
            crop1_index = parent1.crop1_index if random.random() < 0.5 else parent2.crop1_index
            other_crops = [i for i in range(len(self.info)) if i != crop1_index]
            crop2_index = other_crops[math.floor(random.random() * len(other_crops))]

            base_hct = math.floor((parent1.crop1_hct + parent2.crop1_hct) / 2)
            variation = math.floor(random.random() * 3) - 1
            crop1_hct = max(1, min(self.total_hct - 1, base_hct + variation))
            crop2_hct = self.total_hct - crop1_hct

            return CropAllocation(crop1_index, crop2_index, crop1_hct, crop2_hct)

    def mutate(self, allocation: CropAllocation) -> CropAllocation:
        if random.random() < self.mutation_rate:
            mutation_type = math.floor(random.random() * 3)

            if mutation_type == 0:
                available_crops = [i for i in range(len(self.info)) if i != allocation.crop2_index]
                allocation.crop1_index = available_crops[math.floor(random.random() * len(available_crops))]
            elif mutation_type == 1:
                available_crops = [i for i in range(len(self.info)) if i != allocation.crop1_index]
                allocation.crop2_index = available_crops[math.floor(random.random() * len(available_crops))]
            else:
                shift = math.floor(random.random() * 5) - 2
                allocation.crop1_hct = max(1, min(self.total_hct - 1, allocation.crop1_hct + shift))
                allocation.crop2_hct = self.total_hct - allocation.crop1_hct
        return allocation

def return_string(allocation: CropAllocation, fitness: float, info: list[Culture]) -> str:
    crop1 = info[allocation.crop1_index]
    crop2 = info[allocation.crop2_index]
    harvests1 = math.floor(365 / crop1.time)
    harvests2 = math.floor(365 / crop2.time)

    return (
        f"{crop1.name} e {crop2.name} ({harvests1} e {harvests2} colheitas/ano),\n   {allocation.crop1_hct} e {allocation.crop2_hct} hectares,\n   {math.floor(fitness)} lucro/ano.\n"
    )

if __name__ == '__main__':
    async def main():
        index = Index(population_size=100, mutation_rate=0.2, plot_size=100, growth_time=150)
        result = await index.default(generations=150)
        count = 0
        print("\nTop 10 Combinações de Culturas:\n")
        for i, solution in enumerate(result['solutions']):
            count += 1
            print(f"{count}. " + return_string(solution, result['fitnessScores'][i], info))

    asyncio.run(main())
