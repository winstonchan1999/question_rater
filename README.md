# Question Rater

This repository is the implementation of a question rater that calls the GPT API to rate the quality of questions.

## Class QuestionRater

For initialization, the class QuestionRater takes two parameters:

- key: the OpenAI API key
- config: a dictionary containing the chat completion configurations. Keys required are - 'model', 'temperature', and 'n'.

An example of the config dictionary:

```config
config_dict = {
    'model' : "gpt-3.5-turbo",
    'temperature' : 0,
    'n' : 1
}
```

### Method get_rating()

The method get_rating() mainly takes two parameters:

- QA_dict: a dictionary containing the question to be evaluated, and the corresponding answer
- criteria: the string of the criteria to evaluate the questions on

Note that QA_dict and criteria are used to create the prompt. An example of QA_dict and criteria:

```
criteria = 'relatedness'

QA_dict = {
    'question' : 'What is 2 + 2?',
    'answer' : '2 + 2 equals 4.'
}
```
### Method get_rating_with_custom_prompt()

The method get_rating_with_custom_prompt() takes a custom prompt as the sole parameter, and returns the response.

### Method get_prompt()

The method get_prompt() returns the prompt.

## criteria_descriptions.py

The Python file criteria_descriptions.py keeps a list of criteria and their corresponding descriptions. It is used by get_prompt() to build the prompt.

## Example Usage

Please refer to [example.ipynb](example.ipynb).
