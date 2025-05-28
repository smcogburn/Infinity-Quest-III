import random

class DiceRoller:

    @staticmethod
    def d100():
        return random.randint(1, 100)
    
    @staticmethod
    def d20():
        return random.randint(1, 20)
    
    @staticmethod
    def d12():
        return random.randint(1, 12)
    
    @staticmethod
    def d10():
        return random.randint(1, 10)
    
    @staticmethod
    def d8():
        return random.randint(1, 8)
    
    @staticmethod
    def d6():
        return random.randint(1, 6)
    
    
    @staticmethod
    def chance(probability):
        """Return True with given probability (0-1)"""
        return random.random() < probability
    
    @staticmethod
    def weighted_choice(weights):
        """Select an index based on weighted probabilities
        
        Args:
            weights: List of numerical weights
            
        Returns:
            Index selected based on weights
        """
        total = sum(weights)
        r = random.uniform(0, total)
        running_sum = 0
        
        for i, weight in enumerate(weights):
            if running_sum + weight >= r:
                return i
            running_sum += weight
            
        return len(weights) - 1  # Fallback to last item

def wait_for_enter():
    input("\n...\n") 