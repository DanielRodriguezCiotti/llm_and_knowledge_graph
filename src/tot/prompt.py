scoring_prompt = "\nthe question above needs to be answered based on an article. Give a score to each section where the higher the score the more likely the section contains the necessary informations ? \nexample: for a list of sections: 'section1', 'section2'... the ouput is:\n- section1: 9\n- section2: 3\nthe sections are the following: "

context = "You will help me answer a question based on a scientific article"

answering_prompt = "\nThe informations below were extracted from a scientific article. Answer the above question based on them.\n"