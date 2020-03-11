import re
from nltk import ngrams
from collections import Counter
import html2text
import pickle

class Ngram:

    def __init__(self, filename,n): 
        self.__n = n
        self.__model = {}
        self.__s = Syllables()
        self.__data = self.__s.syllables(self.__readfile(filename))
        self.__create_ngram_probability()
        
    def __readfile(self,filename):
        
        print("Reading {} file...".format(filename))
        
        f = open(filename,"r",encoding="utf8",errors='ignore')
        #f = open(filename,"r")
        data = f.read()
        data = html2text.html2text(data)
        data = data.lower()
        data = re.sub(r'[^a-zçğıöşü ]', '', data)
        
        f.close()
        return data

    def __create_ngram_probability(self):

        print("n-gram model creating...")

        for i in range(1,self.__n+1):

            ngram = ngrams(self.__data, i)
            counter = Counter(ngram)
            t_gram = Counter(ngrams(self.__data, i-1))

            if i == 1:
                for key in counter.keys():
                    self.__model[key] = counter.get(key) / len(counter.keys())
            else:   
                for key in counter.keys():
                    self.__model[key] = counter.get(key) / t_gram.get(key[0:-1])
    
    def get_possibility(self,syl):
        
        if len(syl) <= self.__n:
            return self.__model.get(tuple(syl)) if self.__model.get(tuple(syl)) != None else 0
        
        p = 1
        for i in range(len(syl) - self.__n +1):
            p = p * self.get_possibility(syl[i:i+self.__n])

        return p

    def save_model(self,name):
        print("n-gram model saving...")
        with open(name + '.pickle', 'wb') as handle:
            pickle.dump(self, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def load_model(self,name):
        with open(name + '.pickle', 'rb') as handle:
            return pickle.load(handle)

class Syllables:    

    def syllables(self,word,text=True):
        
        syllables = []
        if text:
            print("Syllable in progress...")
        
        bits = ''.join(['1' if l in 'aeıioöuü' else '0' for l in word])

        seperators = (
            ('101', 1),
            ('1001', 2),
            ('10001', 3)
        )

        index, cut_start_pos = 0, 0

        while index < len(bits):

            for seperator_pattern, seperator_cut_pos in seperators:
                if bits[index:].startswith(seperator_pattern):

                    if (' ' in word[cut_start_pos:index + seperator_cut_pos]):

                        if word[cut_start_pos:index + seperator_cut_pos][0] == ' ':
                            syllables.append(' ')
                            syllables.append(word[cut_start_pos +1 :index + seperator_cut_pos])
                        else:
                            syllables.append(word[cut_start_pos:index + seperator_cut_pos - 1])
                            syllables.append(' ')
                    else:
                        syllables.append(word[cut_start_pos:index + seperator_cut_pos])

                    index += seperator_cut_pos
                    cut_start_pos = index
                    break

            index += 1

        syllables.append(word[cut_start_pos:])
        if text:
            print("syllables is completed")
        return syllables

class ConvertLetter:

    def __init__(self,filename):
        f = open(filename,"r")
        self.sentences = self.__readfile(filename).split()
        self.syllable = Syllables()

    def __readfile(self,filename):
        
        f = open(filename,"r")
        data = f.read()
        data = data.lower()
        f.close()
        return data

    def load_ngram_model(self,filename):
        self.ngram_model = Ngram.load_model(Ngram,filename)
    
    def create_ngram_model(self,filename,n):
        self.ngram_model = Ngram(filename,n)

    def convert(self):
        result = []
        for sentence in self.sentences:
            possibles = self.all_possible_sentence(sentence)
            temp = ""
            temp_possibility = 0
            for s in possibles:
                p = self.ngram_model.get_possibility(self.syllable.syllables(s,False))
                if p != None and p > temp_possibility:
                    temp = s
                    temp_possibility = p
            if len(temp) == 0:
                result.append(sentence)
            else :
                result.append(temp)
        return ' '.join(result)

    def all_possible_sentence(self,sentence):

        result = []
        result.append(sentence)
        rule = str.maketrans("iouscg", "ıöüşçğ")
        eng_letters = "iouscg"

        for i in range(len(sentence)):
            if sentence[i] in eng_letters:
                res2 = []
                for element in result:
                    l = list(element)
                    l[i] = str(sentence[i]).translate(rule)
                    res2.append(l)
                for l in res2:
                    str1 = ''.join(l)
                    result.append(str1)
        return result


cl = ConvertLetter("text")
cl.load_ngram_model("5gram")
print(cl.convert())