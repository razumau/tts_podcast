import time

from ollama import generate

MODEL = 'gemma3:1b-it-qat'
# MODEL = 'gemma3:4b'


text = """
Then, in the 1980s and 1990s, US cities made additional zoning changes that reduced parking requirements in downtown areas, based on the principle of New Urbanism, in order to promote walking and public transportation. This once again enabled a single garage floor to provide enough parking for four floors of housing. This change coincided with the standardization of regional building codes into the International Building Code now used in all 50 states, setting the stage for the 5-over-1 design to spread nationwide.




          
            
              
                A 5-over-1 apartment at Dwight and Shattuck Avenue in Berkeley, CA. 
              
              
                Image
                
                  Source: Alfred Twu.
                
              
            
          
        



As urban living returned to popularity in the 21st century, this type of apartment building began to appear in large numbers in downtowns across the country. In the Midwest, for example, apartment buildings of 50 or more units (both mid-rises and high-rises) went from comprising less than 20 percent of all new apartments to over 60 percent between the early 2000s and the early 2020s. Such buildings made efficient use of land and offered many features that made them more desirable than older buildings or suburban houses, including on-site amenities like gyms, pools, and recreation rooms, secure on-site parking, and close proximity to retail and entertainment.
"""

text_without_images = """
Challenges and detractors



Despite their increasing popularity, however, 5-over-1s were not without their opponents. Outside of urban downtowns, their height – while significantly shorter than towers in the park – irritated locals, who complained to city councils that they would overshadow nearby two- and three-story houses. Some found fault with their design and with gentrification as a whole: since zoning had made residential areas off-limits to apartments, these buildings often replaced retail buildings, accelerating the changing character of neighborhoods’ main streets.



There are also more practical reasons for 5-over-1s’ unpopularity in some quarters. Because the buildings can’t grow taller – either due to building code limits on wood frame construction or zoning height limits to preserve residents’ views – growing demand has made these buildings ever wider. As a result, an increasing number of units can only face in one direction, which means that windowless rooms have become more common. Furthermore, the double-loaded corridor design, with apartments on both sides of a hallway, makes it harder to allow for three-bedroom or larger apartments except at the building’s outer corners. Inside corners pose an even bigger challenge, necessitating triangular units with a single tiny window. Some developers have gone one step further and designed units with windowless bedrooms.  
"""


start_time = time.time()
prompt = "In the following text, there might be paragraphs which describe a missing image or its source. Remove such paragraphs and output everything else without changes. Output only the updated text without any additional information."
response = generate(MODEL, f'{prompt}\n"{text}"')
print(response['response'])
print(f"total duration: {response['total_duration'] / 1_000_000} ms")
end_time = time.time()
print(f"This took {end_time - start_time:.2f} seconds")