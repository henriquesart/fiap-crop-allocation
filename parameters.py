import json

class Culture:
    def __init__(self, name: str, area: float, cost: float, profit: float, time: int):
        self.name = name
        self.area = area
        self.cost = cost
        self.profit = profit
        self.time = time

class GenerationStats:
    def __init__(self, generation: int, best_fitness: float, average_fitness: float):
        self.generation = generation
        self.best_fitness = best_fitness
        self.average_fitness = average_fitness

class CropAllocation:
    def __init__(self, crop1_index: int, crop2_index: int, crop1_hct: float, crop2_hct: float):
        self.crop1_index = crop1_index
        self.crop2_index = crop2_index
        self.crop1_hct = crop1_hct
        self.crop2_hct = crop2_hct

    def is_valid(self) -> bool:
        return self.crop1_index != self.crop2_index

    def get_normalized_key(self) -> str:
        crops = [
            {"index": self.crop1_index, "hct": self.crop1_hct},
            {"index": self.crop2_index, "hct": self.crop2_hct},
        ]
        crops.sort(key=lambda crop: crop["index"])
        return json.dumps({
            "crops": [crops[0]["index"], crops[1]["index"]],
            "hct": [crops[0]["hct"], crops[1]["hct"]],
        })

info = [
    Culture(name="Milho", area=1, cost=150, profit=400, time=120),
    Culture(name="Soja", area=1, cost=100, profit=300, time=120),
    Culture(name="Arroz", area=1, cost=180, profit=500, time=150),
    Culture(name="Batata", area=0.5, cost=80, profit=200, time=90),
    Culture(name="Tomate", area=0.5, cost=100, profit=300, time=90),
    Culture(name="Cenoura", area=0.25, cost=60, profit=150, time=60),
    Culture(name="Pepino", area=0.25, cost=80, profit=200, time=60),
    Culture(name="Pimentão", area=0.5, cost=120, profit=250, time=90),
    Culture(name="Cebola", area=0.25, cost=60, profit=150, time=60),
    Culture(name="Trigo", area=1, cost=120, profit=250, time=90),
]