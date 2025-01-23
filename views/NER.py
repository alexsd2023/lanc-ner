import streamlit as st
import spacy
from spacy.lang.es.examples import sentences 
from spacy.lang.es.stop_words import STOP_WORDS
from spacy import displacy
from spacy.tokens import Span
import streamlit.components.v1 as components
import tempfile
from pathlib import Path
import tensorflow as tf
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO

from annotated_text import annotated_text, parameters
from annotated_text import annotation

parameters.SHOW_LABEL_SEPARATOR= False
parameters.BORDER_RADIUS= 0
parameters.PADDING= "0 0.25rem"

def read_htmlfile(html):
    file = open(html, "r")
    content = file.read()
    soup=BeautifulSoup(content)
    file.close()
    return soup.get_text()

def run():
    if 'index' in st.session_state.keys():
        index= st.session_state['index']
    else:
        index= 0  
    modelname = st.radio(
         "Select a model",
        ["Spacy Ruler (Sentences)", "DECM annotations with Paragraphs"],
         index=0,
    )
    if modelname == 'Spacy Ruler (Sentences)':
        st.session_state['index']= 0
        trained_nlp= spacy.load("./models/model_entities_ruler/model-last/")
    elif modelname == 'DECM annotations with Paragraphs':
        trained_nlp= spacy.load("./models/model_toponyms_patterns/model-last/")
        st.session_state['index']= 1

    uploaded_file= st.file_uploader("Choose a raw data file", type=['html', 'htm', 'txt', 'text'],  accept_multiple_files= False)
    texto= ""
    
    
    #if uploaded_file.type=='text/plain':   
    if uploaded_file is not None: 
        st.session_state['uploaded_file']= uploaded_file 
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            #st.markdown("# Original text file")
            fp = Path(tmp_file.name)
            fp.write_bytes(uploaded_file.getvalue())
            #print(fp)
        
        with open(fp,'r') as file:
            if Path(uploaded_file.name).suffix in ['.txt', '.text']:
                texto = " ".join(line for line in file)
            else:
                texto= read_htmlfile(fp)
    elif 'uploaded_file' in st.session_state.keys():
        uploaded_file= st.session_state['uploaded_file'] 
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            #st.markdown("# Original text file")
            fp = Path(tmp_file.name)
            fp.write_bytes(uploaded_file.getvalue())
            #print(fp)
        data= []
        with open(fp,'r') as file:
            if Path(uploaded_file.name).suffix in ['.txt', '.text']:
                texto = " ".join(line for line in file) 
                for line in file:
                    data.append(line)
            else:
                texto= read_htmlfile(fp) 
        
        # with open(fp, encoding='utf8') as file:
        #with open(fp,'r') as file:
        #    print(Path(uploaded_file.name).suffix)
        #    if Path(uploaded_file.name).suffix in ['.txt', '.text']:
        #        #texto = " ".join(line for line in file)
        #        with open(fp) as f:
        #            texto = f.readlines()
        #    else:  
        #        texto= read_htmlfile(fp)    
    

    doc= trained_nlp(texto)

    #st.text_area("Annotated text", value= texto,  key= "text", height=520)
    data= []
    for ent in doc.ents:
        #print (ent.text, ent.label_, ent.start_char, ent.end_char)
        data.append([ent.text, ent.label_, ent.start_char, ent.end_char])
    df_entities= pd.DataFrame(data, columns= ['Text', 'Label', 'Start char', 'End char'])
    st.session_state['df_entities']= df_entities

    #colors= {'Location': 'red', 'Person': 'blue', 'Measurement': 'green'}
    #options= {"ents": ['Location', 'Person', 'Measurement'], "colors": colors}
    #ent_html= displacy.render(doc, style="ent", jupyter= False, options= options)
    #ent_html= displacy.render(doc, style="ent", options= options)
    #st.markdown(ent_html, unsafe_allow_html= True)

    def map_entities(doc):
        plain_text = doc.text
        entities = doc.ents
        return resamble(plain_text, entities)
    
       

    def resamble(plain_text, entities):
        """ Resamble the entities to fit the text_annotate style."""
        tuplas = tuple()
        #print(plain_text)
        prev_ent_end = 0
        texto= ""
        label=""
        start=0
        end= -1
        for ent in entities:

            texto= ent.text
            label= ent.label_
            start= ent.start_char
            end= ent.end_char

            #st.write(start)
            #st.write(end)
            
            if len(tuplas)==0:
                segmento= (plain_text[:start],)
                tuplas= tuplas + segmento
                segmento= (plain_text[:start]),
                tuplas= tuplas + segmento
            else:
                segmento= (plain_text[prev_ent_end:start],)
                tuplas= tuplas + segmento
                segmento= (plain_text[start:end], label),
                tuplas= tuplas + segmento

            prev_ent_end= end
            #print(tuplas)
            #continue

        segmento= (plain_text[end:],)
        tuplas= tuplas + segmento
             
        return tuplas

    sents_plus_ents = map_entities(doc)
    #st.write(sents_plus_ents)

    annotated_text(*sents_plus_ents)
    #annotated_text("this", ("is", "Verb"),"asdfsa", ("aother", "Verb"),  ("is", "Noun"))
    #st.write(df_entities)
    #st.write(data)
