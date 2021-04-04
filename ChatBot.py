# Partners: Shivani Gandhi and Aashish Sharma
# HW7: This bot uses wikipedia to search the web at requests and also has a knowledge base to answer questions specific to Greek Gods and Goddesses.

import nltk
import random
import re,unicodedata
import wikipedia as wk
import warnings
from collections import defaultdict
from nltk.corpus import wordnet as wn
from nltk import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
warnings.filterwarnings("ignore")

# list of phrases the bot will use to end the program or greet the user
quit_list = ['bye','shutdown','exit', 'quit']
thanks_list = ['thanks', 'thank you', 'thanks Percy']
welcome_input = ("hey", "hi", "hello", "hey there", "what's up", "hello there",)
welcome_response = ["why hello there ", "hey ", "*nods* ", "hi there ", "hello ", "Oh, hi there. Fancy meeting you here "]

# read in the text file and tokenize
corpus = open('kb.txt', 'r', errors ='ignore')
raw = corpus.read().lower()
sent_tokens = nltk.sent_tokenize(raw)

def remove_non_ascii(words):
    """Remove non-ASCII characters from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = unicodedata.normalize('NFKD', word).encode('ascii', 'ignore').decode('utf-8', 'ignore')
        new_words.append(new_word)
    return new_words

def processText(raw_text):
    """ process the raw text of the knowledge base by:
        - removing punctuation and digits
        - tokenizing the processed text
        - removing non-ascii characters from the tokens
        - applying POS tagging and lemmatization
        and returns the list of lemmas
    """
    text = re.sub(r'[<>{}.?!,:;()\-\n\d]', ' ', raw_text.lower())
    word_token = word_tokenize(text)
    clean_text = remove_non_ascii(word_token)

    # pos tagging and lemmatization
    tag_map = defaultdict(lambda: wn.NOUN)
    tag_map['J'] = wn.ADJ
    tag_map['V'] = wn.VERB
    tag_map['R'] = wn.ADV
    lemmatizer = WordNetLemmatizer()
    lemma_list = []
    clean_text = [i for i in clean_text if i]
    for token, tag in nltk.pos_tag(clean_text):
        lemma = lemmatizer.lemmatize(token, tag_map[tag[0]])
        lemma_list.append(lemma)

    return lemma_list

def welcomeMessage(user_response):
    """ takes the users response and gives a welcome greeting if appropriate"""
    for word in user_response.split():
        if word.lower() in welcome_input:
            return random.choice(welcome_response)

def botResponse(user_input):
    """ generates a response most similar to the users requests based on cosine similarity
        - if no content is found in the knowledge base, the wiki api is used to search wiki
    """

    #tfidf vectorization and cosine similarity
    sent_tokens.append(user_input)
    TfidfVector = TfidfVectorizer(tokenizer=processText, stop_words='english')
    tfidf = TfidfVector.fit_transform(sent_tokens)
    vals = cosine_similarity(tfidf[-1], tfidf)
    index = vals.argsort()[0][-2]
    flat = vals.flatten()
    flat.sort()
    req_tfidf = flat[-2]

    bot_response=''
    # can't understand user input or need to wiki search
    if(req_tfidf == 0) or "tell me about" in user_input:
        print("I'm thinking...........")
        if user_input:
            bot_response = search_wiki(user_input)
            return bot_response
    # found in knowledge base
    else:
        bot_response = bot_response+sent_tokens[index]
        responses = ["You just really know what questions to ask don't you!", "Hmm, let me see what I can find on that ",
                     "Great question!", "Oh wow, let me see what I can dig up for you ",
                     "Give me a second.. I need to think on that one."]
        print(random.choice(responses))
        return bot_response

def search_wiki(input):
    '''Given the user's input, search wikipedia on the topic and generate 5 sentences'''
    reg_ex = re.search('tell me about (.*)', input)
    try:
        if reg_ex:
            topic = reg_ex.group(1)
            sent = print_topic()
            print(sent + topic)
            wiki = wk.summary(topic, sentences = 5)
            return wiki

    except Exception as e:
            print("Hmm there doesn't seem to be much on " + topic)

def print_topic():
    """ generate a personalized statement as a response to the user asking a question """
    responses = ["Wow I've always wanted to learn more about ", "Hmm, let me see what I can find ", "Here is what I found on ", "This is information on ", "Oh wow, let me see what I can dig up ", "I'm searching my brain for "]
    return random.choice(responses)



# instructions displayed to the user on how to chat with the bot
print("Here are some tips: \nAsk me questions about Greek Mythology like this: "
      "Who is the god of war?.......Who did Hera marry?... Who is the youngest god? \nIf you want to know more on a specific topic or aren't getting the answers you want, try asking me about the topic in this way: \'Tell me about _____\' \nIf you want to exit, type Bye, or thanks!")

welcome = input("\n\nHi! My name is Percy and I'm a chatbot with data on Greek Gods and Goddesses. psst...say hi to me.. I like to feel acknowledged :) \n")
print(welcomeMessage(welcome))
# get user's name and validate the name
name = input("What is your name?\n").capitalize()
while name in quit_list or name in welcome_input or len(name.split()) > 2:
    name = input("Are you sure that's your name... try again\n").capitalize()

# create a file for each unique user and append their information to the file
file = open(name + ".txt", "a")
file.write("User Profile: " + name)

# an infinite loop to continue the conversation until the user ends the program
continue_flag=True
print("Hi " + name + " what would you like to ask me?")
while(continue_flag == True):
    user_response = input().lower()

    # write user's questions to their file
    file.write(user_response + "\n")

    # ensure user is not ending the program
    if(user_response not in quit_list):
        if(user_response in thanks_list ):
            continue_flag  = False
            print("Percy: You are welcome " + name + ".")

        # generate responses to the user's input
        else:
            if(welcomeMessage(user_response)!= None):
                print("Percy: " + welcomeMessage(user_response) + " " + name)
            else:
                print("Percy: ", end="")
                print(botResponse(user_response))
                sent_tokens.remove(user_response)

    # end the program
    else:
        continue_flag = False
        print("Percy: See you soon " + name + " ! I hope you learned something new.")
