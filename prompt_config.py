


relatedness_config = {
    'description' : 'relatedness refers to the degree of relevance between the question and the passage.',

    'r1' : 'unrelated',
    'r2' : 'somwhat related',
    'r3' : 'closely related',

    'r1_desc' : 'the passage does not include the answer to the question',
    'r2_desc' : 'the passage states the indirect or half answer to the question, and the focuses of the question and the passage are slightly mismatched',
    'r3_desc' : 'the passage explicitly states the answer to the question, and the focuses of the question and the passage are identical',             
}

relatedness_instructions = f'''
    Instructions:
    1. Read the passage carefully.
    2. Read through the questions.
    3. Assess the relatedness of each question to the passage content without assuming any information not explicitly stated.
    4. Rate the questions on a scale of 1 to 3, with 1 meaning "{relatedness_config['r1']}," 2 meaning "{relatedness_config['r2']}," and 3 meaning "{relatedness_config['r3']}."
    5. If {relatedness_config['r1_desc']}, the question should be deemed "{relatedness_config['r1']}".
    6. If {relatedness_config['r2_desc']}, the question should be deemed "{relatedness_config['r2']}".
    7. If {relatedness_config['r3_desc']}, the question should be deemed "{relatedness_config['r3']}".
    8. Explain your ratings, but only return the ratings as the final output.
'''



conciseness_config = {
    'description' : 'conciseness refers to the quality of the question being clear and brief.',

    'r1' : 'unconcise',
    'r2' : 'somwhat concise',
    'r3' : 'concise',

    'r1_desc' : 'the question is unclear or contain unnecessary information',
    'r2_desc' : 'the question includes information that is not necessary, but it somewhat relates to the focus of the question',
    'r3_desc' : 'the question is clear and effective, and the focus',
}

conciseness_instructions = f'''
    Instructions:
    1. Read the passage carefully.
    2. Read through the questions.
    3. Assess the conciseness of each question to the passage content without assuming any information not explicitly stated.
    4. Rate the questions on a scale of 1 to 3, with 1 meaning "{conciseness_config['r1']}," 2 meaning "{conciseness_config['r2']}," and 3 meaning "{conciseness_config['r3']}."
    5. If {conciseness_config['r1_desc']}, the question should be a 1.
    6. If {conciseness_config['r2_desc']}, the question should be a 2.
    7. If {conciseness_config['r3_desc']}, the question should be a 3.
    8. Give a strict 1 if the question is a combination of at least two question.
    9. Explain your ratings, but only return the ratings as the final output
'''



completeness_config = {
    'description' : 'completeness refers to whether the set of questions cover all the facts of the passage.',

    'r1' : 'incomplete',
    'r2' : 'somwhat complete',
    'r3' : 'complete',

    'r1_desc' : 'the questions cover less than half of the information in the passage',
    'r2_desc' : 'the questions cover most of the information in the passage',
    'r3_desc' : 'the questions cover all of the information in the passage',
}

completeness_instructions = f'''
    Instructions:
    1. Read the passage carefully.
    2. Read through the questions.
    3. Assess the completeness of all the questions as a whole, meaning that for a list of questions, you must only return one rating.
    4. Rate the set of questions on a scale of 1 to 3, with 1 meaning "{completeness_config['r1']}," 2 meaning "{completeness_config['r2']}," and 3 meaning "{completeness_config['r3']}."
    5. If {completeness_config['r1_desc']}, the question should be deemed "{completeness_config['r1']}".
    6. If {completeness_config['r2_desc']}, the question should be deemed "{completeness_config['r2']}".
    7. If {completeness_config['r3_desc']}, the question should be deemed "{completeness_config['r3']}".
    8. Explain your ratings, but only return the ratings as the final output.
'''



prompt_config = {
        'relatedness' : relatedness_instructions,
        'conciseness' : conciseness_instructions,
        'completeness' : completeness_instructions,
    }
