import spacy
from spacy.lang.en import English
import networkx as nx
import matplotlib.pyplot as plt
from dataset import *

from openie import StanfordOpenIE
from graphviz import Digraph

import en_core_web_sm
nlp = en_core_web_sm.load()

def getSentences(text):
    nlp = English()
    nlp.add_pipe('sentencizer')
    document = nlp(text)
    return [sent.text.strip() for sent in document.sents]

def printToken(token):
    print(token.text, "->", token.dep_)

def appendChunk(original, chunk):
    return original + ' ' + chunk

def isRelationCandidate(token):
    deps = ["ROOT", "adj", "attr", "agent", "amod"]
    return any(subs in token.dep_ for subs in deps)

def isConstructionCandidate(token):
    deps = ["compound", "prep", "conj", "mod"]
    return any(subs in token.dep_ for subs in deps)

def processSubjectObjectPairs(tokens):
    subject = ''
    object = ''
    relation = ''
    subjectConstruction = ''
    objectConstruction = ''
    for token in tokens:
        printToken(token)
        if "punct" in token.dep_:
            continue
        if isRelationCandidate(token):
            relation = appendChunk(relation, token.lemma_)
        if isConstructionCandidate(token):
            if subjectConstruction:
                subjectConstruction = appendChunk(subjectConstruction, token.text)
            if objectConstruction:
                objectConstruction = appendChunk(objectConstruction, token.text)
        if "subj" in token.dep_:
            subject = appendChunk(subject, token.text)
            subject = appendChunk(subjectConstruction, subject)
            subjectConstruction = ''
        if "obj" in token.dep_:
            object = appendChunk(object, token.text)
            object = appendChunk(objectConstruction, object)
            objectConstruction = ''

#     print (subject.strip(), ",", relation.strip(), ",", object.strip())
    return (subject.strip(), relation.strip(), object.strip())

def processSentence(sentence):
    nlp_model = spacy.load('en_core_web_lg')
    tokens = nlp_model(sentence)
    return processSubjectObjectPairs(tokens)

def printGraph(triples):
    G = nx.Graph()
    for triple in triples:
        G.add_node(triple[0])
        G.add_node(triple[1])
        G.add_node(triple[2])
        G.add_edge(triple[0], triple[1])
        G.add_edge(triple[1], triple[2])

    pos = nx.spring_layout(G)
    plt.figure(figsize=(20,20))
    nx.draw(G, pos, edge_color='black', width=1, linewidths=1,
            node_size=500, node_color='seagreen', alpha=0.9,
            labels={node: node for node in G.nodes()})
    plt.axis('off')
    plt.savefig('visualizations/graph1.pdf', bbox_inches='tight')


def main():
	dataset = Dataset('data')
	dataset.create_dataset()
	dataset.group_texts_by_writer()

	text = dataset.texts_by_writer['Kayla Rivas'][0]

	sentences = getSentences(text)
	nlp_model = spacy.load('en_core_web_lg')

	# spacy

	triples = []

	for sentence in sentences:
	    # print(processSentence(sentence, nlp_model))
	    triples.append(processSentence(sentence))

	printGraph(triples)


	# standford openIE

	with StanfordOpenIE() as client:
	    # print('Text: %s.' % text)
	    ann = client.annotate(text, properties={'resolve_coref':'True'})

	G = nx.Graph()
	for triple in ann:
	    # print('|-', triple)
	    G.add_node(triple['subject'])
	    G.add_node(triple['relation'])
	    G.add_node(triple['object'])
	    G.add_edge(triple['subject'], triple['relation'])
	    G.add_edge(triple['relation'], triple['object'])

	pos = nx.spring_layout(G)
	plt.figure(figsize=(20,20))
	nx.draw(G, pos, edge_color='black', width=1, linewidths=1,
	        node_size=500, node_color='seagreen', alpha=0.9,
	        labels={node: node for node in G.nodes()})
	plt.axis('off')
	plt.savefig('visualizations/graph2.pdf', bbox_inches='tight')

if __name__ == '__main__':
    main()

