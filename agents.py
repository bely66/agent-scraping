import time
import json
import yaml
import io
import logging
import traceback
import os

from typing import Dict, List, Union

from openai import OpenAI
from openai import OpenAIError
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instantiate OpenAI with OPENAI_API_KEY.
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

"""Set up all the prompt variables."""

# Designated tokens.
BEGIN_FUNCTION_TOKEN = "BEGIN_FUNCTION"
END_FUNCTION_TOKEN = "END_FUNCTION"
RUN_FUNCTION_TOKEN = "RUN_FUNCTION"
INJECT_FUNCTION_TOKEN = "INJECT_FUNCTION"

# Suffixes to add to the base prompt.
STACK_TRACE_SUFFIX = "\n\nThe code above failed. See stack trace: "
RETRY_SUFFIX = "\n\nPlease try again keeping in mind the above stack trace. Only write code.\n\nOUTPUT: ```python"

# Prompts! The best part :).
BASE_PROMPT = """You have an instance `env` with methods:
- `env.driver`, the Selenium webdriver.
- `env.get(url)` goes to url.
- `env.find_elements(by='class name', value=None)` finds and returns list `WebElement`. The argument `by` is a string that specifies the locator strategy. The argument `value` is a string that specifies the locator value. Use `xpath` for `by` and the xpath of the element for `value`.
- `env.find_element(by='class name', value=None)` is like `env.find_elements()` but only returns the first element.
- `env.page_source` returns the HTML of the current page reference inside env.get(url)

Guidelines for using any element retrieved by `env.find_element()` or `env.find_elements()`:
- `element.get_attribute(attr)` returns the value of the attribute of the element. If the attribute does not exist, it returns ''.
- `element.find_elements(by='id', value=None)` is similar to `env.find_elements()` except that it only searches the children of the element and does not search iframes.
- `element.click()` clicks on the element.
- `element.send_keys(text)` sends text input to the element. to send enter use Keys.ENTER
- Ensure that actions such as `click` or `send_keys` are performed only if the element is interactable.

To check if an element is interactable:
- Use `element.is_displayed()` to check if the element is visible.
- Use `element.is_enabled()` to check if the element is enabled.

Use time.sleep(secs) # to wait

INSTRUCTIONS:
{instructions}

Your code must obey the following constraints:
- In xpaths, to get the text of an element, do NOT use `text()` (use `normalize-space()` instead), and don't use "normalize-space() = 'text'", use "contains(normalize-space(), 'text')" instead. For instance, the xpath for a button element that contains text is "//button[contains(normalize-space(), 'text')]".
- Don't use list comprehensions. They make it hard to debug.
- Only do what I instruct you to do.
- Only write code, no comments.
- Has correct indentation.
- Respect case sensitivity in the instructions.
- Does not call any functions besides those given above and those defined by the base language spec.
- You may not import any modules. You may not use any external libraries.
"""

HTML_PROMPT = """You'll be provided with Text extracted from an Amazon Order HTML. 
We want to extract the key order details from the Text, order number, total price, product names, quantities, prices, currency, delivery status and delivery date in JSON format
{json_shape}

HTML Text:
{html_text}

- Only reply with json, don't write anything else
- Use double quotes in JSON to be correctly parsed"""


FINDER_PROMPT = """You'll be provided with an HTML of a web page Below.
Your job is given this html, find the element that matches our query.
And return the xpath query to get that object. 
In xpaths, to get the text of an element, do NOT use `text()` (use `normalize-space()` instead), and don't use "normalize-space() = 'text'", use "contains(normalize-space(), 'text')" instead. For instance, the xpath for a button element that contains text is "//button[contains(normalize-space(), 'text')]"..
Example: "//button[contains(normalize-space(), 'Login')]" for a button with text "Login".
Example #2: "//a[contains(normalize-space(), 'Sign In')]" for a link with text "Sign In".
JSON Example for link with Sign In {json_shape} make sure the json is enclosed in double quotes.

HTML:
{html}

QUERY:
{query}
"""

class ElementFinder:
    def __init__(
        self,
        base_prompt=FINDER_PROMPT,
        finder_model="gpt-3.5-turbo",
    ):
        self.model = finder_model
        logger.info(f"Using model {self.model}.")
        self.base_prompt = base_prompt

    def find_json_re(self, model_response):
        import re
        # Find the json response in the model response
        json_re = re.compile(r"\{.*\}")
        json_match = json_re.search(model_response)
        if json_match:
            return json_match.group()
        return None
    def get_element(self, html, query):
        json_shape = {"xpath_query": "//a[contains(normalize-space(), 'Sign In')]"}
        prompt = self.base_prompt.format(html=html, query=query, json_shape=json_shape)
        completion = self.get_completion(prompt).strip()
        print("completion", completion)
        json_resp = json.loads(self.find_json_re(completion))["xpath_query"]
        return json_resp

    
    def get_completion(
        self, prompt, model=None, temperature=0, max_tokens=1024, stop=["```"]
    ):
        print("Getting completion")
        """Wrapper over OpenAI's completion API."""
       
        if model is None:
            model = self.model
        print("model", model)
        # Check if it's in the cache already.

        try:
            if "gpt-4o-mini" in model:
                print("Using gpt-4o-mini")
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                    temperature=temperature,
                )
                text = response.choices[0].message.content
                print("text", text)

            elif "gpt-3.5-turbo" in model or "gpt-4" in model:

                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                    temperature=temperature,
                    stop=stop,
                )
                text = response.choices[0].message.content
            else:
                response = client.completions.create(
                    model=model,
                    prompt=prompt,
                    max_tokens=max_tokens,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                    best_of=1,
                    temperature=temperature,
                    stop=stop,
                )
                text = response.choices[0].text
        except OpenAIError as exc:
            logger.info(
                "OpenAI error. Likely a rate limit error, API error, or timeout: {exc}. Sleeping for a few seconds.".format(
                    exc=str(exc)
                )
            )
            time.sleep(5)
            text = self.get_completion(
                prompt, temperature=temperature, max_tokens=max_tokens, model=model
            )
        except Exception:
            traceback.print_exc()

        return text
        
class InstructionCompiler:
    def __init__(
        self,
        instructions=None,
        base_prompt=BASE_PROMPT,
        model="gpt-3.5-turbo",
    ):
        """Initialize the compiler. The compiler handles the sequencing of
        each set of instructions which are injected into the base prompt.

        The primary entrypoint is step(). At each step, the compiler will take
        the current instruction and inject it into the base prompt, asking
        the language model to get the next action. Once it has the next action,
        it will inject the action into the base prompt, asking the language
        model to get the output for that action.

        It returns a dict containing the instruction, action, and action output.

        Args:
            instructions (str): Instructions to compile.
            base_prompt (str): The base prompt to use. Defaults to BASE_PROMPT.
        """
        # Assert that none of the parameters are None and that the
        # instructions are either of type string
        assert instructions is not None
        assert base_prompt is not None
        assert (
            isinstance(instructions, str)
        ), f"Instructions must be of type str, not {type(instructions)}."

        # Instance variables.
        self.model = model
        logger.info(f"Using model {self.model}.")
        self.base_prompt = BASE_PROMPT
        # self.prompt_to_find_element = PROMPT_TO_FIND_ELEMENT
        self.api_cache = {}  # Instruction string to API response.
        self.functions = {}  # Set in _parse_instructions_into_queue.
        self.finished_instructions = []
        self.history = []  # Keep track of the history of actions.

        # Set the instructions.
        self.instructions = instructions  # Overriden in set_instructions.
        self.compiled_instructions = []  # Overriden if available.
        self.instructions_queue = []  # Overriden in set_instructions.
        self.set_instructions(instructions)

    def set_instructions(self, instructions: Union[str, dict, io.TextIOWrapper]):
        self.instructions = self._load_instructions(instructions)
        if isinstance(self.instructions, str):
            instructions_str = self.instructions
        else:
            raise ValueError("Instructions must be a string")

        self.instructions_queue = [instructions_str]
    def _load_instructions(
        self, instructions: Union[str, io.TextIOWrapper]
    ) -> Union[Dict, str]:
        """Load the instructions. If it ends with .yaml or .json, load that."""
        # If it's a string, just return it.
        if isinstance(instructions, str):
            return instructions

    def get_completion(
        self, prompt, model=None, temperature=0, max_tokens=1024, stop=["```"], use_cache=False
    ):
        print("Getting completion")
        """Wrapper over OpenAI's completion API."""
       
        if model is None:
            model = self.model
        print("model", model)
        # Check if it's in the cache already.
        if use_cache and prompt in self.api_cache:
            logger.info("Found prompt in API cache. Saving you money...")
            text = self.api_cache[prompt]
            return text

        try:
            if "gpt-4o-mini" in model:
                print("Using gpt-4o-mini")
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                    temperature=temperature,
                )
                text = response.choices[0].message.content
                print("text", text)

            elif "gpt-3.5-turbo" in model or "gpt-4" in model:

                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                    temperature=temperature,
                    stop=stop,
                )
                text = response.choices[0].message.content
            else:
                response = client.completions.create(
                    model=model,
                    prompt=prompt,
                    max_tokens=max_tokens,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                    best_of=1,
                    temperature=temperature,
                    stop=stop,
                )
                text = response.choices[0].text
        except OpenAIError as exc:
            logger.info(
                "OpenAI error. Likely a rate limit error, API error, or timeout: {exc}. Sleeping for a few seconds.".format(
                    exc=str(exc)
                )
            )
            time.sleep(5)
            text = self.get_completion(
                prompt, temperature=temperature, max_tokens=max_tokens, model=model
            )
        except Exception:
            traceback.print_exc()

        # Add to cache.
        self.api_cache[prompt] = text

        return text

    def get_action_output(self, instructions):
        """Get the action output for the given instructions."""
        prompt = self.base_prompt.format(instructions=instructions)
        completion = self.get_completion(prompt).strip()
        action_output = completion.strip()
        lines = [line for line in action_output.split("\n") if not line.startswith("import ")]
        action_output = "\n".join(lines)
        return {
            "instruction": instructions,
            "action_output": action_output,
        }

    def step(self):
        """Run the compiler."""
        # For each instruction, give the base prompt the current instruction.
        # Then, get the completion for that instruction.
        instructions = self.instructions_queue.pop(0)
        if instructions.strip():
            instructions = instructions.strip()
            action_info = self.get_action_output(instructions)
            self.history.append(action_info)

            # Optimistically count the instruction as finished.
            self.finished_instructions.append(instructions)
            return action_info

    def retry(self, stack_trace_str):
        """Revert the compiler to the previous state and run the instruction again."""
        logger.info("Retrying...")
        # Pop off the last instruction and add it back to the queue.
        last_instructions = self.finished_instructions.pop()

        # Get the last action to append to the prompt.
        last_action = self.history.pop()

        # Append the failure suffixes to the prompt.
        prompt = self.base_prompt.format(instructions=last_instructions)
        prompt = prompt + "\n" + last_action["action_output"]
        prompt = prompt + STACK_TRACE_SUFFIX + " " + stack_trace_str
        prompt = prompt + RETRY_SUFFIX

        # Get the action output.
        action_info = self.get_action_output(prompt)
        self.history.append(action_info)

        # Optimistically count the instruction as finished.
        self.finished_instructions.append(last_instructions)
        return action_info
    

class HTMLParser:
    def __init__(
        self,
        base_prompt=HTML_PROMPT,
        parser_model="gpt-3.5-turbo",
    ):
        self.model = parser_model
        logger.info(f"Using model {self.model}.")
        self.base_prompt = base_prompt

    def find_json_re(self, model_response):
        import re
        # Find the json response in the model response
        json_pattern = re.compile(r'\{.*\}', re.DOTALL)

        # Search for the JSON part in the input string
        json_match = json_pattern.search(model_response)
        if json_match:
            return json_match.group()
        return None
    def get_order_details(self, html_text):
        json_shape = "{'order_number':  122112, etc..}"
        prompt = self.base_prompt.format(html_text=html_text, json_shape=json_shape)
        completion = self.get_completion(prompt).strip()
        cleaned_json = self.find_json_re(completion)
        print("cleaned_json", cleaned_json)
        json_resp = json.loads(cleaned_json)
        return json_resp

    
    def get_completion(
        self, prompt, model=None, temperature=0, max_tokens=1024, stop=["```"]
    ):
        print("Getting completion")
        """Wrapper over OpenAI's completion API."""
       
        if model is None:
            model = self.model
        print("model", model)
        # Check if it's in the cache already.

        try:
            if "gpt-4o-mini" in model:
                print("Using gpt-4o-mini")
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                    temperature=temperature,
                )
                text = response.choices[0].message.content
                print("text", text)

            elif "gpt-3.5-turbo" in model or "gpt-4" in model:

                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                    temperature=temperature,
                    stop=stop,
                )
                text = response.choices[0].message.content
            else:
                response = client.completions.create(
                    model=model,
                    prompt=prompt,
                    max_tokens=max_tokens,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                    best_of=1,
                    temperature=temperature,
                    stop=stop,
                )
                text = response.choices[0].text
        except OpenAIError as exc:
            logger.info(
                "OpenAI error. Likely a rate limit error, API error, or timeout: {exc}. Sleeping for a few seconds.".format(
                    exc=str(exc)
                )
            )
            time.sleep(5)
            text = self.get_completion(
                prompt, temperature=temperature, max_tokens=max_tokens, model=model
            )
        except Exception:
            traceback.print_exc()

        return text

if __name__ == "__main__":
    # import pprint

    # pp = pprint.PrettyPrinter(indent=4)

    # with open("manual_plan.txt", "r") as f:
    #     instructions = f.read()

    # compiler = InstructionCompiler(instructions=instructions, model='gpt-4o-mini')

    # while compiler.instructions_queue:
    #     action_info = compiler.step()
    #     pp.pprint(action_info)

    # test parser
    html_text = """Your Account›Your Orders›Order Details
Order Details
                Ordered on 29 June 2024
                
                Order#
                171-8229869-3714749
                Invoice 1
            
                Request invoice
            
                Printable Order Summary
            
Invoice
    Invoice 1
    Request invoice
    Printable Order Summary
        Shipping Address
    
Mohamed Nabil Mohamed
مدينة المهندسين
عمارة ١٨ الدور التاني شقة باب حديد اسود على الشمال
Alexandria, Qesm Borg Al Arab, Madinet Borg Al Arab
Egypt
Payment Methods Mastercardending in 5603
    Order Summary
            Item(s) Subtotal: 
        
        EGP 435.33
    
            Shipping & Handling:
        
        EGP 0.00
    
            Total before VAT:
        
        EGP 435.33
    
            Estimated VAT:
        
        EGP 38.83
    
            Total:
        
        EGP 474.16
    
            Grand Total:
        
        EGP 474.16
    
    Delivered Jun 30, 2024
                Your package was delivered. It was handed directly to a resident.
            
            Track package
        
        2ool Ameme Wala3a Card Game
    
    Sold by: 
        Amazon.eg
Return window closed on Jul 15, 2024
    EGP 195.07
                Buy it again
            
        SCREW 60 CART
    
    Sold by: 
        Amazon.eg
Return window closed on Jul 15, 2024
    EGP 121.09
                Buy it again
            
        Nilco speechless
    
    Sold by: 
        
Top Toys EG
Return window closed on Jul 15, 2024
    EGP 69.00
                Buy it again
            
            Leave seller feedback
        
            Write a product review
        
    Delivered Jun 30, 2024
                Your package was delivered. It was handed directly to a resident.
            
            Track package
        
        UNO Flip Play Card Game party game
    
    Sold by: 
        
Alaa-Eldin
Return window closed on Jul 15, 2024
    EGP 89.00
                Buy it again
            
            Leave seller feedback
        """
    parser = HTMLParser(parser_model='gpt-4o-mini')
    print(parser.get_order_details(html_text))
