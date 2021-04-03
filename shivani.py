# THis bot uses wikipedia to search the web at requests and also has a knowledge base to answer questions specific to Greek Gods and Goddesses.

import nltk
import random
import re, string, unicodedata
import wikipedia as wk
import warnings
from nltk.corpus import wordnet as wn
from nltk.stem.wordnet import WordNetLemmatizer
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity, linear_kernel
warnings.filterwarnings("ignore")


# read in the text file
corpus = open('kb.txt', 'r', errors ='ignore')
raw = corpus.read().lower()
#raw = raw.lower()

# tokenize the text
sent_tokens = nltk.sent_tokenize(raw)


def processText(text):
    remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)
    # word tokenization
    word_token = nltk.word_tokenize(text.lower().translate(remove_punct_dict))

    # remove ascii
    new_words = []
    for word in word_token:
        new_word = unicodedata.normalize('NFKD', word).encode('ascii', 'ignore').decode('utf-8', 'ignore')
        new_words.append(new_word)

    # Remove tags
    rmv = []
    for w in new_words:
        text = re.sub("&lt;/?.*?&gt;", "&lt;&gt;", w)
        rmv.append(text)

    # pos tagging and lemmatization
    tag_map = defaultdict(lambda: wn.NOUN)
    tag_map['J'] = wn.ADJ
    tag_map['V'] = wn.VERB
    tag_map['R'] = wn.ADV
    lmtzr = WordNetLemmatizer()
    lemma_list = []
    rmv = [i for i in rmv if i]
    for token, tag in nltk.pos_tag(rmv):
        lemma = lmtzr.lemmatize(token, tag_map[tag[0]])
        lemma_list.append(lemma)
    return lemma_list

welcome_input = ("hello", "hi", "greetings", "sup", "what's up","hey",)
welcome_response = ["hi", "hey", "*nods*", "hi there", "hello", "I am glad! You are talking to me"]
def welcome(user_response):
    for word in user_response.split():
        if word.lower() in welcome_input:
            return random.choice(welcome_response)

def generateResponse(user_response):
    robo_response=''
    sent_tokens.append(user_response)
    TfidfVec = TfidfVectorizer(tokenizer=processText, stop_words='english')
    tfidf = TfidfVec.fit_transform(sent_tokens)
    vals = cosine_similarity(tfidf[-1], tfidf)
    #vals = linear_kernel(tfidf[-1], tfidf)
    idx=vals.argsort()[0][-2]
    flat = vals.flatten()
    flat.sort()
    req_tfidf = flat[-2]
    if(req_tfidf==0) or "tell me about" in user_response:
        print("I'm thinking...........")
        if user_response:
            robo_response = wikipedia_data(user_response)
            return robo_response
    else:
        robo_response = robo_response+sent_tokens[idx]
        return robo_response#wikipedia search

def wikipedia_data(input):
    reg_ex = re.search('tell me about (.*)', input)
    try:
        if reg_ex:
            topic = reg_ex.group(1)
            sent = ptopic(topic)
            print(sent + topic)
            wiki = wk.summary(topic, sentences = 3)
            return wiki
    except Exception as e:
            print("No content has been found")

def ptopic(topic):
    responses = ["Wow I've always wanted to learn more about ", "Hmm, let me see what I can find ", "Here is what I found on ", "This is information on ", "Oh wow, let me see what I can dig up ", "I'm searching my brain for "]
    return random.choice(responses)

flag=True
print("My name is Chatterbot and I'm a chatbot. If you want to exit, type Bye!")
print("What is your name")
name = input()
file = open(name+".txt", "a")
print("Hi " + name + " ask me anything")

while(flag==True):
    user_response = input()
    user_response=user_response.lower()
    file.write(user_response + "\n")
    if(user_response not in ['bye','shutdown','exit', 'quit']):
        if(user_response=='thanks' or user_response=='thank you' ):
            flag=False
            print("Chatterbot : You are welcome..")
        else:
            if(welcome(user_response)!=None):
                print("Chatterbot : "+welcome(user_response)+ " " + name)
            else:
                print("Chatterbot : ",end="")
                print(generateResponse(user_response))
                sent_tokens.remove(user_response)
    else:
        flag=False
        print("Chatterbot : Bye!!! ")