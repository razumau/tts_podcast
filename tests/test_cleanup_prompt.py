import time
import unittest

from ollama import generate

MODEL = 'gemma3:1b-it-qat'
PROMPT = ("In the following text, there might be paragraphs which describe a missing image or its source. Remove such "
          "paragraphs and output everything else without changes. Output only the updated text without any additional "
          "information.")


text = """
Then, in the 1980s and 1990s, US cities made additional zoning changes that reduced parking requirements in downtown areas, based on the principle of New Urbanism, in order to promote walking and public transportation. This once again enabled a single garage floor to provide enough parking for four floors of housing. This change coincided with the standardization of regional building codes into the International Building Code now used in all 50 states, setting the stage for the 5-over-1 design to spread nationwide.

                A 5-over-1 apartment at Dwight and Shattuck Avenue in Berkeley, CA. 

                Image

                  Source: Alfred Twu.

As urban living returned to popularity in the 21st century, this type of apartment building began to appear in large numbers in downtowns across the country. In the Midwest, for example, apartment buildings of 50 or more units (both mid-rises and high-rises) went from comprising less than 20 percent of all new apartments to over 60 percent between the early 2000s and the early 2020s. Such buildings made efficient use of land and offered many features that made them more desirable than older buildings or suburban houses, including on-site amenities like gyms, pools, and recreation rooms, secure on-site parking, and close proximity to retail and entertainment.
"""

class TestCleanupPrompt(unittest.TestCase):
    def test_cleanup_prompt(self):
        start_time = time.time()
        response = generate(MODEL, f'{PROMPT}\n"{text}"')
        result = response['response']
        self.assertNotIn('A 5-over-1 apartment at Dwight and Shattuck Avenue in Berkeley, CA', result)
        self.assertNotIn('Alfred Twu', result)
        self.assertIn('US cities made additional zoning changes that reduced parking requirements', result)
        self.assertIn('As urban living returned to popularity in the 21st century', result)
        print(f"total duration: {response['total_duration'] / 1_000_000} ms")
        end_time = time.time()
        print(f"This took {end_time - start_time:.2f} seconds")

