from xml.dom import minidom
import random

# ------- Global Variables -------
word_count = 0 #Stores the count of words from the training data corpus
flag_count = 0

def getTestEvalSentences(files):
    final_sentences = []  # Will store the final array of sentences - consisting of words only.
    for file in files:
        doc = minidom.parse(file)
        # Store each sentence <s></s> object in an array.
        doc_sentences = doc.getElementsByTagName('s')

        # Goes through each sentence DOM object and returns an array of words which is appended to final_sentences.
        for i, sentence in enumerate(doc_sentences):
            final_sentences.append(getWords(sentence))

    # Shuffles the final sentences and takes 80% for training and 20% for evaluation.
    random.shuffle(final_sentences)
    training_sentences = final_sentences[0:round(.8 * len(final_sentences))]
    evaluation_sentences = final_sentences[round(.8 * len(final_sentences)):len(final_sentences)]
    return training_sentences,evaluation_sentences

#A recursive functions that gets each word from the corpus sentences into an array of words and returns them.
def getWords(sentence):
    temp_sentence = []
    for word in sentence.childNodes:
        #If the current word is a sub-sentence, get the words within it (recursively) and merge it with the current snetence.
        if(word.tagName != "w" and word.tagName != "c"):
            words = getWords(word)
            temp_sentence = temp_sentence + words
        else:
            #Base case - add it to the current sentence.
            temp_sentence.append(word.firstChild.data.strip().lower())
    return temp_sentence

#A function the builds the N-Gram arrays and sets the word_count to the amount of words in the unigram.
def buildNGrams(sentences):
    # Stores the unigram,bigram and trigram and their probabilities.
    unigram, bigram, trigram = {}, {}, {}
    #Accessing each sentence.
    for sentence in sentences:
        #Skipping any empty sentences - in case they appear.
        if(len(sentence) != 0):
            #Accessing each word in the current sentence.
            for i,word in enumerate(sentence):
                # Keeping track of the number of words
                if(flag_count == 0):
                    global word_count
                    word_count += 1

                # ----- Unigram creation -----
                # If the word was already added, increment its frequency.
                if word in unigram.keys():
                    unigram[word] += 1
                # Else the word is appended to the unigram array and it's frequency is set to 1.
                else:
                    unigram[word] = 1

                # ----- Bigram creation -----
                # If the bigram word was already added, increment its frequency.
                if len(sentence) > i+1 and word + "|" + sentence[i+1] in bigram.keys():
                    bigram[word + "|" + sentence[i+1]] += 1
                # Else the bigram word is appended to the bigram array and it's frequency is set to 1.
                elif len(sentence) > i+1:
                    bigram[word + "|" + sentence[i + 1]] = 1
                # If there is no word after it's position (i+1), a bigram cannot be made.

                # ----- Trigram creation
                # If the trigram word was already added, increment its frequency.
                if len(sentence) > i+2 and word + sentence[i+1] + sentence[i+2] in trigram.keys():
                    trigram[word + "|" +  sentence[i+1] + "|" + sentence[i+2]] += 1
                # Else the trigram word is appended to the trigram array and it's frequency is set to 1.
                elif len(sentence) > i+2:
                    trigram[word + "|" +  sentence[i+1] + "|" +  sentence[i+2]] = 1
                # If there is no two word after it's position (i+2), a trigram cannot be made.
    return unigram,bigram,trigram

#A function that calculates the probabilities of each N-Gram model and returns them.
def calculateProb(unigram,bigram,trigram):
    unigram_prob = {}
    for word in unigram:
        # Formula = count(word)/word count
        word_prob = unigram[word]/word_count
        unigram_prob[word] = word_prob

    bigram_prob = {}
    for word in bigram:
        #Gets the frequency of the first word using the unigram arrays.
        freq = unigram[word.split("|",1)[0]]
        # Formula = count(bigram word)/count(first word)
        word_prob = bigram[word] / freq
        bigram_prob[word] = word_prob

    trigram_prob = {}
    for word in trigram:
        # Gets the frequency of the first two words using the bigram arrays.
        split = word.split("|",2)
        freq = bigram[split[0] + "|" + split[1]]
        # Formula = count(trigram word)/count(first two words)
        word_prob = trigram[word] / freq
        trigram_prob[word] = word_prob
    return unigram_prob,bigram_prob,trigram_prob

def addUNKwords(sentences,unigram):
    new_training_sentences = []
    #Go through each sentence
    for sentence in sentences:
        temp_training_sentence = []
        for word in sentence:
            #If a word has a frequency of 1, change it to <UNK>, otherwise append normal word.
            if(unigram[word] == 1):
                temp_training_sentence.append("<UNK>")
            else:
                temp_training_sentence.append(word)
        new_training_sentences.append(temp_training_sentence)
    #Returns UNK training sentences.
    return new_training_sentences

def rouletteWheel(options):
    #Get the sum of all probability values.
    total = sum(options.values())
    #Pick a random float between zero and the sum.
    random_pick = random.uniform(0,total)
    current = 0
    #Iterate through the options and append values of each key until the current is > the picked value.
    for key in options:
        current += options[key]
        if current > random_pick:
            return key

def linearInterpolation(unigram,bigram,trigram):
    unigram_prob, bigram_prob,trigram_prob=  {}, {},{}
    w1, w2, w3 = 0.1, 0.3, 0.6
    for word in unigram:
        # Formula = count(unigram word)/count(all words)
        word_prob = unigram[word]/word_count
        unigram_prob[word] = word_prob
    for word in bigram:
        split = word.split("|",1) #Splitting the word.
        freq = unigram[split[0]] #Frequency of the first word.
        # Formula = count(bigram word)/count(first word)
        word_prob = bigram[word] / freq
        bigram_prob[word] = word_prob
    for word in trigram:
        split = word.split("|",2) #Splitting the word.
        freq = bigram[split[0] + "|" + split[1]] #Frequency of the first two words.
        # Linear Interpolation - (0.6*trigram probability)+(0.3*bigram probability of last two words)+(0.1*unigram probability of last word)
        word_prob = (w3 * (trigram[word] / freq)) + (w2 *(bigram_prob[split[1] + "|" + split[2]])) + (w1*(unigram_prob[split[2]]))
        trigram_prob[word] = word_prob
    return unigram_prob,bigram_prob,trigram_prob

#Returns all bigrams with the same first word as search.
def getChoices(search, dictionary):
    choices = {}
    for word in dictionary:
        split = word.split("|", 1)
        first_word = split[0]
        # If the first word matches, add it to the choices dictionary.
        if(first_word == search):
            choices[split[1]] = dictionary[word]
    return choices

#Returns all trigrams with the same first word as search and same second word as search2.
def getChoices2(search, search2, dictionary):
    choices = {}
    for word in dictionary:
        split = word.split("|", 2)
        first_word = split[0]
        second_word = split[1]
        #If the first word and second word match, add it to the choices dictionary.
        if (first_word == search and second_word == search2):
            choices[split[2]] = dictionary[word]
    return choices

#Generates a unigram, bigram and trigram sentence with a randomly chosen first word.
def generate_model(unigram_prob, bigram_prob, trigram_prob):
    #Chooses a random first word to start sentence with from unigram model using the rouletteWheel function.
    first_word = rouletteWheel(unigram_prob)

    #Generating a unigram sentence
    print("\nGenerating Unigram Sentence.... ")
    chosen = ''
    sentence = first_word
    #Generate a unigram sentence until a full stop is reached.
    while chosen != '.':
        #Choose a random next word based on weights and add it to the sentence.
        chosen = rouletteWheel(unigram_prob)
        sentence += " " + chosen
    print(sentence)

    #Generate a bigram sentence
    print("\nGenerating Bigram Sentence...")
    chosen = first_word
    sentence = first_word
    while chosen != '.':
        #Get a dictionary of bigrams that have the same first word as the previously chosen one.
        choices = getChoices(chosen,bigram_prob)
        if len(choices) == 0: break
        #Choose a random next word based on weights from the choices dictionary and add it to the sentence.
        chosen = rouletteWheel(choices)
        sentence += " " + chosen
    print(sentence)

    #Generating a trigram sentence
    print("\nGenerating Trigram Sentence...")
    sentence = first_word
    #First generate a bigram using the first word.
    choices = getChoices(first_word,bigram_prob)
    chosen = rouletteWheel(choices)
    sentence += " " + chosen
    #Generate trigrams using the previous two chosen words until a full stop is reached.
    while chosen != '.':
        # Get a dictionary of trigram options that have the same first word and second word as the previously chosen ones.
        choices = getChoices2(first_word,chosen,trigram_prob)
        if len(choices) == 0: break
        first_word = chosen
        # Choose a random next word based on weights from the trigrams choices dictionary and add it to the sentence.
        chosen = rouletteWheel(choices)
        sentence += " " + chosen.strip()
    print(sentence)

#Checks each word in the trigram sentence, if one is not found in the unigram, it is replaced with <UNK>
def ifUNK(word1,word2,word3,unigram):
    new_word1,new_word2,new_word3 = word1,word2,word3
    #If word is not found in the UNK unigram model, replace it with <UNK>
    if not(word1 in unigram):
        new_word1 = "<UNK>"
    if not(word2 in unigram):
        new_word2 = "<UNK>"
    if not(word3 in unigram):
        new_word3 = "<UNK>"
    return new_word1 + "|" + new_word2 + "|" + new_word3

#Checks each word in the bigram sentence, if one is not found in the unigram, it is replaced with <UNK>
def ifUNK2(word1,word2,unigram):
    new_word1, new_word2 = word1, word2
    # If word is not found in the UNK unigram model, replace it with <UNK>
    if not (word1 in unigram):
        new_word1 = "<UNK>"
    if not (word2 in unigram):
        new_word2 = "<UNK>"
    return new_word1 + "|" + new_word2


def check_sentence(sentence,unigram,bigram,trigram,unk_unigram,unk_bigram,unk_trigram,f):
    vanilla_3_probability, vanilla_1_probability, vanilla_2_probability = 1,1,1
    unk_3_probability, unk_2_probability, unk_1_probability = 1,1,1
    for i,word in enumerate(sentence):
        # If the word is in the unigram probability model, mulitply by it's probability, otherwise multiply by 0.
        if(word in unigram):
            vanilla_1_probability*= unigram[word]
        else:
            vanilla_1_probability*= 0
        # If the word is found in the UNK unigram, multiply it's probability, otherwise multiply the probabiliy of a <UNK> token.
        if(word in unk_unigram):
            unk_1_probability *= unk_unigram[word]
        else:
            unk_1_probability *= unk_unigram["<UNK>"]

        # Ignore if last letter of the bigram is the same as the number of words in the sentence.
        if(i+1 < len(sentence)):
            # Make a bigram sentence using the current word and next word.
            check = sentence[i] + "|" + sentence[i+1]
            # If the sentence is in the bigram probability model, mulitply by it's probability, otherwise multiply by 0.
            if(check in bigram):
                vanilla_2_probability *= bigram[check]
            else:
                vanilla_2_probability *= 0
            # Replaces unknown words in the sentence with <UNK>
            new_sentence = ifUNK2(sentence[i],sentence[i+1],unk_unigram)
            # If the sentence is found in the UNK bigram probability model, multiply by it's value, else multiply by 0.
            if(new_sentence in unk_bigram):
                unk_2_probability *= unk_bigram[new_sentence]
            else:
                unk_2_probability *= 0

        #Ignore if last letter of the trigram is the same as the number of words in the sentence.
        if(i+2 < len(sentence)):
            #Make a trigram sentence using the current word and next two words.
            check = sentence[i] + "|" + sentence[i+1] + "|" + sentence[i+2]
            #If the sentence is in the trigram probability model, mulitply by it's probability, otherwise multiply by 0.
            if(check in trigram):
                vanilla_3_probability *= trigram[check]
            else:
                vanilla_3_probability *= 0
            #Replaces unknown words in the sentence with <UNK>
            new_sentence = ifUNK(sentence[i],sentence[i+1],sentence[i+2],unk_unigram)
            #If the sentence is found in the UNK trigram probability model, multiply by it's value, else multiply by 0.
            if(new_sentence in unk_trigram):
                unk_3_probability *= unk_trigram[new_sentence]
            else:
                unk_3_probability *= 0
    #Write probabilties to a text file.
    f.write("\n\nProbability generated for the sentence " + str(sentence))
    f.write("\nUsing the Vanilla Trigram model:" + str(vanilla_3_probability))
    f.write("\nUsing the UNK Trigram model:" + str(unk_3_probability))
    f.write("\nUsing the Vanilla Bigram model:" + str(vanilla_2_probability))
    f.write("\nUsing the UNK Bigram model:" + str(unk_2_probability))
    f.write("\nUsing the Vanilla Unigram model:" + str(vanilla_1_probability))
    f.write("\nUsing the UNK Unigram model:" + str(unk_1_probability))

def main():
    training_sentences, evaluation_sentences = getTestEvalSentences(['A6U.xml','ACJ.xml'])
    #Populates the N Grams with the training sentences.
    unigram, bigram, trigram = buildNGrams(training_sentences)
    global flag_count #So that the words aren't counted twice in the buildNGrams() function
    flag_count = 1

    #Change training sentences into UNK sentences.
    unk_training_sentences = addUNKwords(training_sentences,unigram)
    #Builds UNK models using UNK sentences.
    unk_unigram, unk_bigram, unk_trigram = buildNGrams(unk_training_sentences)

    #Calculates the Vanilla N-Gram probabilities and returns them
    unigram_prob, bigram_prob, trigram_prob = calculateProb(unigram, bigram, trigram)
    #Calculates the UNK model probabilities
    unk_unigram_prob, unk_bigram_prob, unk_trigram_prob = linearInterpolation(unk_unigram,unk_bigram,unk_trigram)
    #Generates a sentence using a randomly chosen weight unigram word
    generate_model(unigram_prob,bigram_prob,trigram_prob)

    f = open("probabilities.txt", "w+",encoding='utf-8')
    #Goes through each test sentence and caclulates its probability based on the UNK and Vanilla models.
    for sentence in evaluation_sentences:
        check_sentence(sentence,unigram_prob,bigram_prob,trigram_prob,unk_unigram_prob,unk_bigram_prob,unk_trigram_prob,f)
    f.close()

main()

