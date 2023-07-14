# Question Rater

This repository is the implementation of a question rater that calls the GPT API to rate the quality of questions.



## Class **QuestionRater**

For initialization, the class `QuestionRater` takes the string of the OpenAI API key as the parameter.

### Method `get_rating()`

The method `get_rating()` is used to get ratings for each individual question in the question list. It takes two parameters:

- `QA_dict`: a dictionary containing three keys - 'company', 'questions', and 'passage'
- `criteria`: the string of the criterion to evaluate the questions on

It returns the ratings as a Python dictionary (questions as keys; ratings as values). An example of the output dictionary:
```
{
  "How do I close the window?": 3,
  "How do I use my phone to access my Model 3?": 3,
  "What do I need to do to authenticate my phone as a key for my Model 3?": 3,
  "Can I use any phone to access my Model 3?": 2,
  "What is the process for tapping my key card against the Model 3 card reader?": 3,
  "Is it necessary to keep my phone's Bluetooth on at all times to access my Model 3?": 3,
  "Is it necessary to keep my phone's Bluetooth on at all times to access my Model 3?": 3,
  "When should I secure cargo in the rear trunk? How should I secure cargo in the rear trunk?": 1,
  "How do I get my car into a car wash?": 3,
  "What is Sport steering mode?": 3,
  "How do I open the door? How do I close the door": 1
}
```
Note that `QA_dict` and `criteria` are used to create the prompt. An example of `QA_dict` and `criteria`:

```
criteria = 'relatedness'

QA_dict = {
    'company' : 'Tesla',                         ## company of the OEM

    'questions' : [
        When is model 3 released?,               ## list of questions to be evaluated, must be a Python list !
        Can I use my phone as the key?,
        ...
    ],

    'passage' : 'Tesla model 3 is...'            ## the context passage from which the questions are generated
}
```

### Method `get_qset_rating()`

The method `get_qset_rating()` is used to get a single rating for a list of questions. It takes two parameters:

- `QA_dict`: a dictionary containing three keys - 'company', 'questions', and 'passage'
- `criteria`: the string of the criterion to evaluate the questions on

For each call to this method, it returns a single digit integer of the rating.

### Method `get_rating_with_custom_prompt()`

The method `get_rating_with_custom_prompt()` takes a custom prompt as the sole parameter and returns the string of the response.

### Method `get_all_ratings()`

The method `get_all_ratings()` is used to get the ratings on all criteria for a list of questions. It takes one parameter:

- `QA_dict`: a dictionary containing three keys - 'company', 'questions', and 'passage'

The ratings are returned as a Python dictionary.

## prompt_config.py

For each criterion, [prompt_config.py](prompt_config.py) stores:
- the instruction string used to construct the final prompt;
- the config dictionary that contains the necessary data to construct the instructions

`prompt_config` is a dictionary holding the instructions for all criteria.

## model_config.py

The `model_config` dictionary in [model_config.py](model_config.py) stores the OpenAI chat completion method configurations. An example of the model_config dictionary:

```config
config_dict = {
    'model' : "gpt-3.5-turbo",
    'temperature' : 0,
    'n' : 1
}
```

## Example Usage

Please refer to [example.ipynb](example.ipynb).
