
class criteria:

    def __init__(self, rating_method, description, r1, r2, r3, r1_desc, r2_desc, r3_desc, instructions):
        
        self.rating_method = rating_method
        self.description = description
        self.r1 = r1
        self.r2 = r2
        self.r3 = r3
        self.r1_desc = r1_desc
        self.r2_desc = r2_desc
        self.r3_desc = r3_desc
        self.instructions = instructions

    def get_rating_method(self):
        return self.rating_method
    
    def get_instructions(self):
        return self.instructions



class relatedness(criteria):

    def __init__(self):

        rating_method = 'individual'

        description = 'relatedness refers to the degree of relevance between the question and the passage.'

        r1 = 'unrelated'
        r2 = 'somwhat related'
        r3 = 'closely related'

        r1_desc = 'the passage does not include the answer to the question'
        r2_desc = 'the passage states the indirect or half answer to the question, and the focuses of the question and the passage are slightly mismatched'
        r3_desc = 'the passage explicitly states the answer to the question, and the focuses of the question and the passage are identical'

        instructions = f'''
            Instructions:
            1. Read the passage carefully.
            2. Read through the questions.
            3. Assess the relatedness of each question to the passage content without assuming any information not explicitly stated.
            4. Rate the questions on a scale of 1 to 3, with 1 meaning "{r1}," 2 meaning "{r2}," and 3 meaning "{r3}."
            5. If {r1_desc}, the question should be deemed "{r1}".
            6. If {r2_desc}, the question should be deemed "{r2}".
            7. If {r3_desc}, the question should be deemed "{r3}".
            8. Explain your ratings, but only return the ratings as the final output.
        '''

        super().__init__(rating_method, description, r1, r2, r3, r1_desc, r2_desc, r3_desc, instructions)



class conciseness(criteria):

    def __init__(self):

        rating_method = 'individual'

        description = 'conciseness refers to the quality of the question being clear and brief.'

        r1 = 'unconcise'
        r2 = 'somwhat concise'
        r3 = 'concise'

        r1_desc = 'the question is unclear or contain unnecessary information'
        r2_desc = 'the question includes information that is not necessary, but it somewhat relates to the focus of the question'
        r3_desc = 'the question is clear and effective, and the focus'

        instructions = f'''
            Instructions:
            1. Read the passage carefully.
            2. Read through the questions.
            3. Assess the conciseness of each question to the passage content without assuming any information not explicitly stated.
            4. Rate the questions on a scale of 1 to 3, with 1 meaning "{r1}," 2 meaning "{r2}," and 3 meaning "{r3}."
            5. If {r1_desc}, the question should be a 1.
            6. If {r2_desc}, the question should be a 2.
            7. If {r3_desc}, the question should be a 3.
            8. Give a strict 1 if the question is a combination of at least two question.
            9. Explain your ratings, but only return the ratings as the final output
        '''

        super().__init__(rating_method, description, r1, r2, r3, r1_desc, r2_desc, r3_desc, instructions)



class completeness(criteria):

    def __init__(self):

        rating_method = 'set'

        description = 'completeness refers to whether the set of questions cover all the facts of the passage.'

        r1 = 'incomplete'
        r2 = 'somwhat complete'
        r3 = 'complete'

        r1_desc = 'the questions cover less than half of the information in the passage'
        r2_desc = 'the questions cover most of the information in the passage'
        r3_desc = 'the questions cover all of the information in the passage'

        instructions = f'''
            Instructions:
            1. Read the passage carefully. Identify the number of major aspects in the passage as "x", do not change "x".
            2. Read through the questions.
            3. Assess the completeness of the question set as a whole, meaning you are rating the question set as a collective, but not the questions individually.
            4. Note that each question in the set can cover only some aspect of the passage, the goal is to evaluate if all major aspects of the passage are covered.
            5. Note that the rating correlates with the number of questions. In most case, more questions = higher rating, fewer questions = lower rating.
            6. Questions do not need to cover unnecessary or extraneous detail, just the major aspects.
            7. Identify the number of major aspects covered by the questions as "y".
            8. If "x" = "y", give a 3. 
            9. If "y" is larger than or equal to half of "x", give a 2.
            10. If "y" is less than half of "x", give a 1.
            11. Show me "x" and "y" in json format.
        '''

        super().__init__(rating_method, description, r1, r2, r3, r1_desc, r2_desc, r3_desc, instructions)



prompt_config = {
    'relatedness' : relatedness(),
    'conciseness' : conciseness(),
    'completeness' : completeness(),
}
