import openai
from model_config import model_config
from prompt_config import prompt_config



class QuestionRater:

    def __init__(self, key : str):
        openai.api_key = key
        self.model_config = model_config



    def get_completion(self, prompt):
        messages = [{"role": "user", "content": prompt}]
        response = openai.ChatCompletion.create(
            messages = messages,
            model = self.model_config['model'],
            temperature = self.model_config['temperature'],
            n = self.model_config['n'],
        )
        return response.choices[0].message["content"]



    def get_prompt(self, QA_dict : dict, criteria : str):
        prompt = f"""
                    You will be provided with a passage extracted from a {QA_dict['company']} car manual. \  

                    Instructions:
                    {prompt_config[criteria]}

                    Questions:
                    {QA_dict['questions']}
                    
                    Passage: {QA_dict['passage']} \ 

                    Return the ratings in json format.
                    Output the question as the key, and the rating as the value
                """
        
        return prompt


    def get_rating(self, QA_dict : dict, criteria : str):
        try:
            prompt = self.get_prompt(QA_dict, criteria.lower())
            response = self.get_completion(prompt)
            return response
        
        except (
            openai.error.Timeout, 
            openai.error.APIError, 
            openai.error.APIConnectionError,
            openai.error.InvalidRequestError,
            openai.error.AuthenticationError,
            openai.error.PermissionError,
            openai.error.RateLimitError,
            Exception
        ) as e:
            print(f"Exception: {e}")
            pass



    def get_rating_with_custom_prompt(self, prompt : str):
        try:
            response = self.get_completion(prompt)
            return response
        
        except (
            openai.error.Timeout, 
            openai.error.APIError, 
            openai.error.APIConnectionError,
            openai.error.InvalidRequestError,
            openai.error.AuthenticationError,
            openai.error.PermissionError,
            openai.error.RateLimitError,
            Exception
        ) as e:
            print(f"Exception: {e}")
            pass