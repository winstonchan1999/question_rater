import openai
from model_config import model_config
from prompt_config import prompt_config
import concurrent.futures


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



    def __get_completion_maxtoken(self, prompt, max_token):
        messages = [{"role": "user", "content": prompt}]
        response = openai.ChatCompletion.create(
            messages = messages,
            model = self.model_config['model'],
            temperature = self.model_config['temperature'],
            n = self.model_config['n'],
            max_tokens = max_token
        )
        return response.choices[0].message["content"]



    def __get_prompt(self, QA_dict : dict, criteria : list):

        prompt_list = []

        for c in criteria:
            prompt_list.append(prompt_config[c].get_instructions())

        instructions = '\n\n'.join(prompt_list)

        prompt = f"""
                    You will be provided with a passage extracted from a {QA_dict['company']} manual and its section title.

                    Instructions:
                    1. Read the passage carefully.
                    2. Read through the questions.

                    {instructions}

                    Questions:
                    {QA_dict['questions']}
                    
                    Title: {QA_dict['title']}

                    Passage: {QA_dict['passage']} 

                    Return the ratings in json format.
                    Output the question as the key, and the list of ratings as the value
                """
        
        return prompt



    def __get_qset_prompt(self, QA_dict : dict, criteria : str):

        prompt = f"""
                    You will be provided with a passage extracted from a {QA_dict['company']} manual and its section title.

                    Instructions:
                    {prompt_config[criteria].get_instructions()}

                    Questions:
                    {QA_dict['questions']}
                    
                    Title: {QA_dict['title']}

                    Passage: {QA_dict['passage']}
                """
        return prompt



    def __check_dict(self, dic : dict):
        required_keys = {'company', 'questions', 'passage', 'title'}

        if not required_keys.issubset(dic.keys()):
            raise ValueError("Missing required keys")
        
        for key, value in dic.items():
            if key == 'company':
                if not isinstance(value, str):
                    raise TypeError("Value for 'company' must be a string.")
            elif key == 'questions':
                if not isinstance(value, list):
                    raise TypeError("Value for 'questions' must be a list.")
            elif key == 'passage':
                if not isinstance(value, str):
                    raise TypeError("Value for 'passage' must be a string.")
            elif key == 'title':
                if not isinstance(value, str):
                    raise TypeError("Value for 'title' must be a string.")



    def get_rating(self, QA_dict : dict, criteria : str):

        if prompt_config[criteria].get_rating_method() != 'individual':
            raise ValueError(f"You cannot use get_rating() with criteria '{criteria}'")

        self.__check_dict(QA_dict)
        prompt = self.__get_prompt(QA_dict, [criteria.lower()])
        response = self.__get_completion(prompt)
        
        return eval(response)



    def get_qset_rating(self, QA_dict : dict, criteria : str):

        if prompt_config[criteria].get_rating_method() != 'set':
            raise ValueError(f"You cannot use get_qset_rating() with criteria '{criteria}'")

        self.__check_dict(QA_dict)
        prompt = self.__get_qset_prompt(QA_dict, criteria.lower())
        response = self.__get_completion(prompt)
        final_prompt = f'''
            Given {response},
            Compare x and y:
            If y = x, set "z" as 3
            If y >= x/2, set "z" as 2
            If y < x/2, set "z" as 1

            Return z only without telling me your explanation.
        '''

        final_response = self.__get_completion_maxtoken(final_prompt, 1)
        return int(final_response)



    def get_rating_with_custom_prompt(self, prompt : str):

        response = self.__get_completion(prompt)
        return response
    


    def get_all_ratings(self, QA_dict : dict):

        self.__check_dict(QA_dict)

        in_list = []
        set_list = []

        for key, value in prompt_config.items():
            if value.get_rating_method() == 'individual':
                in_list.append(key)
            elif value.get_rating_method() == 'set':
                set_list.append(key)
        
        prompt1 = self.__get_prompt(QA_dict, in_list)
        prompt2 = self.__get_qset_prompt(QA_dict, set_list[0])

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_1 = executor.submit(self.__get_completion, prompt1)
            future_2 = executor.submit(self.__get_completion, prompt2)
            
            completions_1 = future_1.result()
            completions_2 = future_2.result()

        final_prompt = f'''
            Given {completions_2},
            Compare x and y:
            If y = x, set "z" as 3
            If y >= x/2, set "z" as 2
            If y < x/2, set "z" as 1

            Return z only without telling me your explanation.
        '''

        final_response = self.__get_completion_maxtoken(final_prompt, 1)

        dict1 = eval(completions_1)
        int1 = int(final_response)

        return dict1, int1



    # def get_all_ratings_sequential(self, QA_dict : dict):

    #         try:

    #             self.__check_dict(QA_dict)

    #             rating_dict = {}

    #             for key, value in prompt_config.items():

    #                 if value.get_rating_method() == 'individual':
    #                     new_dict = self.get_rating(QA_dict, key)
    #                     if not rating_dict:
    #                         rating_dict = new_dict
    #                         for _key in rating_dict:
    #                             rating_dict[_key] = [rating_dict[_key]]
    #                     else:
    #                         for _key in new_dict:
    #                             if _key in rating_dict:
    #                                 rating_dict[_key].append(new_dict[_key])

    #                 elif value.get_rating_method() == 'set':
    #                     rating = self.get_qset_rating(QA_dict, key)
    #                     if not rating_dict:
    #                         for question in QA_dict['questions']:
    #                             rating_dict[question] = [rating]
    #                     else:
    #                         for _key in rating_dict:
    #                             rating_dict[_key].append(rating)

    #             return rating_dict
            
    #         except (
    #             openai.error.Timeout, 
    #             openai.error.APIError, 
    #             openai.error.APIConnectionError,
    #             openai.error.InvalidRequestError,
    #             openai.error.AuthenticationError,
    #             openai.error.PermissionError,
    #             openai.error.RateLimitError,
    #             Exception
    #         ) as e:
    #             print(f"Exception: {e}")
    #             pass