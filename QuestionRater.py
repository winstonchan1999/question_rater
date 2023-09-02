import openai
from prompt_config import prompt_config
import concurrent.futures
import textwrap
import time
import tiktoken



max_retry_attempts = 5



class MaxRetriesExceededError(Exception):
    def __init__(self):
        super().__init__("MaxRetriesExceededError")



class QuestionRater:

    def __init__(self, key : str):
        openai.api_key = key



    def __get_completion(self, prompt, model):

        """
        Private method to get completion from OpenAI through the API.

        Args:
            prompt (string):    the prompt to submit to GPT.
            model (string):     what GPT model to get the completion from.
        
        Returns:
            response (string):  the response from GPT.
        """

        messages = [{"role": "user", "content": prompt}]
        response = openai.ChatCompletion.create(
            messages = messages,
            model = model,
            temperature = 0,
            n = 1,
        )
        return response.choices[0].message["content"]



    def __get_completion_maxtoken(self, prompt, max_token, model):

        """
        Private method to get completion from OpenAI through the API with specification of max_token.

        Args:
            prompt (string):    the prompt to submit to GPT.
            max_token (int):    max_token allowed for the response.
            model (string):     what GPT model to get the completion from.
        
        Returns:
            response (string):  the response from GPT.
        """

        messages = [{"role": "user", "content": prompt}]
        response = openai.ChatCompletion.create(
            messages = messages,
            model = model,
            temperature = 0,
            n = 1,
            max_tokens = max_token
        )
        return response.choices[0].message["content"]



    def __get_prompt(self, QA_dict : dict, criteria : list):

        """
        Private method to construct the prompt for individual ratings.

        Args:
            QA_dict (dict):     dictionary holding the information required for prompt construction (please refer to README).
            criteria (list):    a list of criteria to evaluate the questions on.
        
        Returns:
            prompt (string):    the dedented prompt.
        """

        prompt_list = [prompt_config[c].get_instructions() for c in criteria]

        instructions = '\n'.join(prompt_list)

        prompt = f"""
            You will be provided with a {QA_dict['language']} passage extracted from a {QA_dict['company']} manual and its section title.

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
        
        return textwrap.dedent(prompt)



    def __get_qset_prompt(self, QA_dict : dict, criteria : str):

        """
        Private method to construct the prompt for individual ratings.

        Args:
            QA_dict (dict):     dictionary holding the information required for prompt construction (please refer to README).
            criteria (str):     the criterion to evaluate the questions on.
        
        Returns:
            prompt (string):    the dedented prompt.
        """

        prompt = f"""
            You will be provided with a {QA_dict['language']} passage extracted from a {QA_dict['company']} manual and its section title.

            Instructions:
            {prompt_config[criteria].get_instructions()}

            Questions:
            {QA_dict['questions']}
            
            Title: {QA_dict['title']}

            Passage: {QA_dict['passage']}
        """
        return textwrap.dedent(prompt)



    def __get_qset_final_prompt(self, response: str):
        
        """
        Private method to construct the prompt for set ratings.

        Args:
            QA_dict (dict):     dictionary holding the information required for prompt construction (please refer to README).
            criteria (list):    a list of criteria to evaluate the questions on.
        
        Returns:
            prompt (string):    the dedented prompt.
        """

        final_prompt = f'''
            Given {response},
            Compare x and y:
            If y is larger than or equal to x, set "z" as 3
            Else if  y is larger than or equal to half of x, set "z" as 2
            Else, set "z" as 1

            Return z only without telling me your explanation.
        '''

        return textwrap.dedent(final_prompt)



    def __check_dict(self, dic : dict):
        
        """
        Private method to check that the QA_dict is valid.

        Args:
            dict (dict):        the QA_dict to be validated.
        
        Action:
            raise errors if necessary
        """

        required_keys = {'company', 'questions', 'passage', 'title', 'language'}

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
                if not isinstance(value, list):
                    raise TypeError("Value for 'title' must be a list.")
            elif key == 'language':
                if not isinstance(value, str):
                    raise TypeError("Value for 'language' must be a string.")



    def get_rating(self, QA_dict : dict, criteria : str):

        """
        Public method to get individual ratings for a set of questions.

        Args:
            QA_dict (dict):     the dictionary holding the required information.
            criteria (str):     the criterion to rate the questions on.
        
        Returns:
            output (dict):      a dictionary with questions as the keys, and their ratings as the values.
            alt_output (int):   returns 0 if max retried reached.
        """

        if prompt_config[criteria].get_rating_method() != 'individual':
            raise ValueError(f"You cannot use get_rating() with criteria '{criteria}'. Please use get_qset_rating() instead.") 

        self.__check_dict(QA_dict)

        retries = max_retry_attempts
        while retries > 0:
            try:
                prompt = self.__get_prompt(QA_dict, [criteria.lower()])

                ## counts the number of tokens of the prompt and use the appropriate model accordingly
                encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
                num_tokens = len(encoding.encode(prompt))
                q_string = '\n'.join(QA_dict['questions'])
                num_q_tokens = len(encoding.encode(q_string))

                if num_tokens + num_q_tokens > 3900:
                    response = self.__get_completion(prompt, 'gpt-3.5-turbo-16k')
                else:
                    response = self.__get_completion(prompt, 'gpt-3.5-turbo')
                
                final_output = eval(response)

                ## this is to check whether GPT is returning a correct format of dictionary
                ## sometimes it returns the ratings as a list of duplicated numbers, when we only need a single integer.
                for key in final_output:
                    if isinstance(final_output[key], list):
                        final_output[key] = final_output[key][0]

                return final_output
            except (
                openai.error.Timeout, 
                openai.error.APIError,
            ) as e:
                print(f"Retry attempt #{max_retry_attempts-retries+1}/{max_retry_attempts} - Sleeping for 5 seconds. (Error: {e})")
                retries -= 1
                if retries == 0:
                    print("Max retries exceeded - Returning 0.")
                    return 0
                time.sleep(5)



    def get_qset_rating(self, QA_dict : dict, criteria : str):

        """
        Public method to get set ratings for a set of questions.

        Args:
            QA_dict (dict):     the dictionary holding the required information.
            criteria (str):     the criterion to rate the questions on.
        
        Returns:
            output (int):       the final rating.
            alt_output (int):   returns 0 if max retried reached.
        """

        if prompt_config[criteria].get_rating_method() != 'set':
            raise ValueError(f"You cannot use get_qset_rating() with criteria '{criteria}'. Please use get_rating() instead.")

        self.__check_dict(QA_dict)

        retries = max_retry_attempts
        while retries > 0:
            try:
                prompt = self.__get_qset_prompt(QA_dict, criteria.lower())

                ## counts the number of tokens of the prompt and use the appropriate model accordingly
                encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
                num_tokens = len(encoding.encode(prompt))

                if num_tokens > 4000:
                    response = self.__get_completion(prompt, 'gpt-3.5-turbo-16k')
                else:
                    response = self.__get_completion(prompt, 'gpt-3.5-turbo')

                final_prompt = self.__get_qset_final_prompt(response)
                final_response = self.__get_completion_maxtoken(final_prompt, 1, 'gpt-3.5-turbo')
                return int(final_response)
            except (
                openai.error.Timeout, 
                openai.error.APIError,
            ) as e:
                print(f"Retry attempt #{max_retry_attempts-retries+1}/{max_retry_attempts} - Sleeping for 5 seconds. (Error: {e})")
                retries -= 1
                if retries == 0:
                    print("Max retries exceeded - Returning 0.")
                    return 0
                time.sleep(5)



    def get_rating_with_custom_prompt(self, prompt : str):

        """
        Public method to get a reponse with a custom prompt.

        Args:
            prompt (str):       the prompt you are giving to GPT.
        
        Returns:
            response (str):     the response from GPT.
            alt_output (int):   returns 0 if max retried reached.
        """

        retries = max_retry_attempts
        while retries > 0:
            try:
                ## counts the number of tokens of the prompt and use the appropriate model accordingly
                encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
                num_tokens = len(encoding.encode(prompt))
                if num_tokens > 3700:
                    response = self.__get_completion(prompt, 'gpt-3.5-turbo-16k')
                else:
                    response = self.__get_completion(prompt, 'gpt-3.5-turbo')
                return response
            except (
                openai.error.Timeout, 
                openai.error.APIError,
            ) as e:
                print(f"Retry attempt #{max_retry_attempts-retries+1}/{max_retry_attempts} - Sleeping for 5 seconds. (Error: {e})")
                retries -= 1
                if retries == 0:
                    print("Max retries exceeded - Returning 0.")
                    return 0
                time.sleep(5)



    def __get_ind(self, prompt : str, QA_dict : dict):

        """
        Private method to get individual ratings. Created separately to facilitate concurrent prompting.

        Args:
            prompt (str):       the prompt you are giving to GPT.
            QA_dict (dict):     the dictionary holding the required information.
        
        Returns:
            response (dict):     the response from GPT.
        """

        ## counts the number of tokens of the prompt and use the appropriate model accordingly
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        num_tokens = len(encoding.encode(prompt))
        q_string = '\n'.join(QA_dict['questions'])
        num_q_tokens = len(encoding.encode(q_string))

        if num_tokens + num_q_tokens > 3900:
            response = self.__get_completion(prompt, 'gpt-3.5-turbo-16k')
        else:
            response = self.__get_completion(prompt, 'gpt-3.5-turbo')
        return eval(response)



    def __get_qset(self, prompt : str):

        """
        Private method to get set ratings. Created separately to facilitate concurrent prompting.

        Args:
            prompt (str):       the prompt you are giving to GPT.
        
        Returns:
            response (int):     the response from GPT.
        """

        ## counts the number of tokens of the prompt and use the appropriate model accordingly
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        num_tokens = len(encoding.encode(prompt))
        if num_tokens > 3700:
            response = self.__get_completion(prompt, 'gpt-3.5-turbo-16k')
        else:
            response = self.__get_completion(prompt, 'gpt-3.5-turbo')
        final_prompt = self.__get_qset_final_prompt(response)
        final_response = self.__get_completion_maxtoken(final_prompt, 1, 'gpt-3.5-turbo')
        return int(final_response)



    def get_all_ratings(self, QA_dict : dict):

        """
        Public method to get all three ratings concurrently.

        Args:
            QA_dict (dict):         the dictionary holding the required information.
        
        Returns:
            ratings (dict, int):    the dictionary and integer holding the relatedness, conciseness, and completeness ratings.
            alt_output (int):       returns 0 for either of the outputs if max retried reached.
        """

        self.__check_dict(QA_dict)

        ## getting the list of individual and set rating criteria
        in_list = [key for key, value in prompt_config.items() if value.get_rating_method() == 'individual']
        set_list = [key for key, value in prompt_config.items() if value.get_rating_method() == 'set']
        
        ## prompt construction
        prompt1 = self.__get_prompt(QA_dict, in_list)
        prompt2 = self.__get_qset_prompt(QA_dict, set_list[0])

        dict1 = None
        int1 = None

        ## prompting concurrently
        with concurrent.futures.ThreadPoolExecutor() as executor:
                future_1 = executor.submit(self.__get_ind, prompt1, QA_dict)
                future_2 = executor.submit(self.__get_qset, prompt2)
                
                for future in concurrent.futures.as_completed([future_1, future_2]):
                    try:
                        result = future.result()

                        if isinstance(result, dict):
                            dict1 = result
                        elif isinstance(result, int):
                            int1 = result

                        if dict1 is not None and int1 is not None:
                            return dict1, int1
                    except (
                        openai.error.Timeout, 
                        openai.error.APIError,
                    ) as e:
                        
                        retries = max_retry_attempts
                        while retries > 0:
                            try:
                                print(f"Retry attempt #{max_retry_attempts-retries+1}/{max_retry_attempts} - Sleeping for 5 seconds. (Error: {e})")
                                time.sleep(5)
                                if future == future_1:
                                    future_1 = executor.submit(self.__get_ind, prompt1, QA_dict)
                                    result = future_1.result()
                                    dict1 = result
                                elif future == future_2:
                                    future_2 = executor.submit(self.__get_qset, prompt2)
                                    result = future_2.result()
                                    int1 = result

                                if dict1 is not None and int1 is not None:
                                    return dict1, int1

                                break
                            except (
                                openai.error.Timeout,
                                openai.error.APIError,
                            ) as e1:
                                retries -= 1
                                if retries == 0:
                                    d_r = "available"
                                    i_r = "available"
                                    if dict1 is None:
                                        dict1 = 0
                                        d_r = 'None'
                                    if int1 is None:
                                        int1 = 0
                                        i_r = 'None'
                                    
                                    print(f"Max retries exceeded. Returning available ratings. (relatedness & conciseness: {d_r}; completeness: {i_r})")
                                    return dict1, int1
