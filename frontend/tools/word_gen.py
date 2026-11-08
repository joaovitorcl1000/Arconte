import random
from typing import List, Dict

class PhonologyEngine:
    def __init__(
        self,
        consonants: List[str],
        vowels: List[str],
        consonant_weights: List[float] = None,
        vowel_weights: List[float] = None,
        syllable_pattern: str = "CVC"
    ):
        self.consonants = consonants
        self.vowels = vowels
        self.consonant_weights = consonant_weights
        self.vowel_weights = vowel_weights
        self.syllable_pattern = syllable_pattern

    def generate_syllable(self) -> str:
        syllable = []
        for char in self.syllable_pattern:
            if char == "C":
                syllable.append(random.choices(self.consonants, weights=self.consonant_weights)[0])
            elif char == "V":
                syllable.append(random.choices(self.vowels, weights=self.vowel_weights)[0])
            elif char == "(C)" and random.random() > 0.5:
                syllable.append(random.choices(self.consonants, weights=self.consonant_weights)[0])
        return "".join(syllable)

    def generate_word(self, min_syllables: int = 1, max_syllables: int = 3) -> str:
        num_syllables = random.randint(min_syllables, max_syllables)
        return "".join(self.generate_syllable() for _ in range(num_syllables))


if __name__ == "__main__":
    # Teste de inventário básico
    cons = ["m", "n", "p", "t", "k", "s", "r", "l", "d"]
    vows = ["a", "e", "i", "o", "u"]
    # 'a' e 'e' com frequência natural mais alta
    v_weights = [0.35, 0.25, 0.15, 0.15, 0.10]

    engine = PhonologyEngine(consonants=cons, vowels=vows, vowel_weights=v_weights, syllable_pattern="CVC")
    
    # Gerar 10 palavras únicas de teste
    lexicon = set()
    while len(lexicon) < 10:
        lexicon.add(engine.generate_word(min_syllables=1, max_syllables=2))

    print("Palavras geradas:", list(lexicon))
