import openai
from model_config import model_config
from prompt_config import prompt_config



class QuestionRater:

    def __init__(self, key : str):
        openai.api_key = key
        self.model_config = model_config



    def __get_completion(self, prompt):
        messages = [{"role": "user", "content": prompt}]
        response = openai.ChatCompletion.create(
            messages = messages,
            model = self.model_config['model'],
            temperature = self.model_config['temperature'],
            n = self.model_config['n'],
        )
        return response.choices[0].message["content"]



    def __get_prompt(self, QA_dict : dict, criteria : str):

        prompt = f"""
                    You will be provided with a passage extracted from a {QA_dict['company']} car manual. \  

                    Instructions:
                    {prompt_config[criteria].get_instructions()}

                    Questions:
                    {QA_dict['questions']}
                    
                    Passage: {QA_dict['passage']} \ 

                    Return the ratings in json format.
                    Output the question as the key, and the rating as the value
                """
        
        return prompt



    def __get_qset_prompt(self, QA_dict : dict, criteria : str):

        prompt = f"""
                    You will be provided with a passage extracted from a {QA_dict['company']} car manual. \  

                    Instructions:
                    {prompt_config[criteria].get_instructions()}

                    Questions:
                    {QA_dict['questions']}
                    
                    Passage: {QA_dict['passage']} \ 

                    Return only one digit
                """
        
        return prompt



    def get_rating(self, QA_dict : dict, criteria : str):

        try:
            prompt = self.__get_prompt(QA_dict, criteria.lower())
            response = self.__get_completion(prompt)
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



    def get_qset_rating(self, QA_dict : dict, criteria : str):

        try:
            prompt = self.__get_qset_prompt(QA_dict, criteria.lower())
            response = self.__get_completion(prompt)
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
            response = self.__get_completion(prompt)
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

    

    def get_all_ratings(self, QA_dict : dict):

        try:

            rating_dict = {}

            for key, value in prompt_config.items():

                if value.get_rating_method() == 'individual':
                    new_dict = eval(self.get_rating(QA_dict, key))
                    if not rating_dict:
                        rating_dict = new_dict
                        for _key in rating_dict:
                            rating_dict[_key] = [rating_dict[_key]]
                    else:
                        for _key in new_dict:
                            if _key in rating_dict:
                                rating_dict[_key].append(new_dict[_key])

                elif value.get_rating_method() == 'set':
                    rating = int(self.get_qset_rating(QA_dict, key))
                    if not rating_dict:
                        for question in QA_dict['questions']:
                            rating_dict[question] = [rating]
                    else:
                        for _key in rating_dict:
                            rating_dict[_key].append(rating)

            return rating_dict
        
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