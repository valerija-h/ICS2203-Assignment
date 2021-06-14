To run the file:
- Run the runner.py file using Linux commands or a Python IDE such as Pycharm.

Improvements I made to Task 1:
- I have now stored the frequencies of the unigram, bigram, trigrams in dictionaries. As well as their probabilities.
- I have fixed the frequency count of words - before I accidentally made it the count of unique words rather than all words in the training set.
- I created a function getTestEvalSentences() that returns the training and test sentences to reduce the main function.
- The getTestEvalSentences() function also loops through a given array of file names instead of one and adds their sentences together.
- Store each word stripped and lowercase - to avoid doing it during future comparisons.
- The word keys in the dictionaries for unigram and trigram models are seperated by "|". Eg. For the bigram frequency model a sample key value pair would be {"This|Is":2}.

Task 2 Additions:
The MAIN function now executes the in the following manner:
	- Get the training sentences and evaluation sentences from the corpus using the getTestEvalSentences() function.
	- Get the vanilla unigram,bigram,trigram models using the buildNGrams() function.
	- Get the training sentences and replace words with a frequency of 1 with the key "<UNK>" and return a UNK training set.
	- Create a unigram, bigram and trigram frequency model using the UNK training set using the buildNGrams() function.
	- Create a vanilla unigram, bigram and trigram probability model using the calculateProb() function.
	- Get a UNK trigram probability model using the linearInterpolation() function.
	- Generate sentences using the vanilla unigram, bigram and trigram probability models then output their results to the console using the generate_model() function.
	- Pass each evaluation sentence using the vanilla and UNK models with the check_model() function and output their probabilities into a text file.

Output of Task 2:
The console will first display generated sentences using the Vanilla models.
Then it will display the probabilities of the testing sentences using the Vanilla and UNK probability models in the file "probabilities.txt".

Description of how I did task 2:
1. Changing the test data to <UNK> tokens - this was done through the addUNKwords() function.
It worked by passing through each word in training sentences and checking their frequency using the vanilla unigram model.
If a word had a frequency of 1 it was set to <UNK>. 

2. Building the UNK N-gram models - this was done using the same function as in Task 1 - buildNgrams().

3. I built the UNK probability models in the same method as for the Vanilla models, except in this case, the trigram is built with linear interpolation in the LinearInterpolation() function.
The unigram and bigram probabilities were calculated the same method which was used in the Vanilla porbability models (Task 1).
The trigram probabilities were calculated by going through each word in the trigram UNK model and implementing the linear inteprolation formula and creating a new dictionary with the trigram word as a key and it's probability as a value.

4. I generated the sentences using the vanilla unigram, bigram and trigram probability models in the generate_model() function.
The function uses a weighted selection (rouletteWheel() function) to choose a unigram and build sentences using the three different models.
- It builds the unigram model by picking the next best word using the weight selection until a full stop is chosen.
- It builds the bigram sentences by getting a dictionary of bigram possibilities (which have the same first word as the last chosen word) and using the weighted selection until a full stop is chosen.
- It builds the trigram by first building a bigram on the first word chosen using the same method as described in the sentence above then by getting a dictionary of trigram possibilities and using the weighted sleection function until a full stop is reached.

5. The probability of the test sentences were calculated by looping through each test sentence and checking their probability using the Vanilla and UNK models using the generate_model() function.
It works by looping through each word in a given test sentence and for each word:
- It's unigram probability estimate using the Vanilla model is calculated by finding the word in the Vanilla unigram model and if it's not found, multiplying by 0.
- It's unigram probability estimate using the UNK model is calculated by finding the word in the UNK unigram model and if it's not found, multyping by the <UNK> probability.
- It's bigram probability estimate using the Vanilla model is calculated by finding the word and the word proceeding it in the Vanilla bigram model and if it's not found, multiplying by 0.
- It's bigram probability estimate using the UNK model is calculated by replacing any unknown occurences (based on the unigram model) of the word and proceeding word with <UNK> and checking if they are present in the UNK bigram model and if they're not found, multiplying by 0.
- It's trigram probability estimate using the Vanilla model is calculated by finding the word and the two words proceeding it in the Vanilla trigram model and if it's not found, multiplying by 0.
- It's trigram probability estimate using the UNK model is calculated by replacing any unknown occurences (based on the unigram model) of the word and proceeding two words with <UNK> and checking if they are present in UNK trigram model and they're not found, multiplying by 0.
Please note that the unknown words were replaced using the ifUNK() (for trigrams) and ifUNK2() (for bigrams) functions. These check whether each word is stored in a given unigram, and if it's not, it replaces it with <UNK>. It returns an entire bigram/trigram word.
The probabilities of each sentence is outputted to the "probabilities.txt" file.
