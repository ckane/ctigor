from random import randint
from typing import Annotated
from semantic_kernel.functions import kernel_function

class RandomNumberPlugin:
    """Generates a Random Number"""

    @kernel_function(
      name='gen_random',
      description="Generate a random number given a low and high bound"
    )
    async def gen_random(
      self,
      low: Annotated[int, "Lower bound of the random number"],
      high: Annotated[int, "Upper bound of the random number"]
    ) -> Annotated[int, "Generated random number within the bounds"]:
        print(f"Running gen_random with low={low}, high={high}")
        return randint(low, high)
