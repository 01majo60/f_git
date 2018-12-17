def dict_parse(word):
    word1 = "{'"
    for i in word:
        if i == ',':
            word1 += "','"
        elif i == ' ':
            pass
        else:
            word1 += i
    word1 += "'}"
    return word1        

