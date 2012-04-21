import porter
import string
import shutil,os

#from twisted.lore.lint import tags
#from symbol import term

#Global Variables 
totaldocuments=0
totalwords =0
stopwords = []
itemid =0
storeterms=dict()
uniquewords=1    

def IndexMyTerms():
    global stopwords

    docid=""
    content =""
   
    os.mkdir("temp")
    clearfilecontents("docInfo.txt")
    clearfilecontents("collectionInfo.txt");
    clearfilecontents("invertedIndex.txt");
    clearfilecontents("termInfo.txt");
    
    ignoretags = [".B",".X",".N",".C"]
    contenttags = [".T" ,".A" ,".W" , ".K"]
    tags = [".T" ,".A" ,".W" , ".K",".B",".X",".N",".C",".I"]
     
    stopwords = getstopwords()
    
    records = open('cacm.txt').readlines()
    cnt =0
    totallines = (len(records))
    while cnt < totallines-1:
        if records[cnt][0:2] ==".I" :
            getContent(docid,content)
            docid = int(records[cnt].split()[1])
            content = ""
            cnt = cnt+1
            continue
        if records[cnt][0:2] in contenttags :
            while cnt < len(records)-1:
                cnt = cnt + 1                
                if records[cnt][0:2] in tags:
                    break
                content = content + records[cnt]
        if records[cnt][0:2] in ignoretags:
            while cnt < len(records)-1:
                cnt = cnt + 1              
                if records[cnt][0:2] in tags:
                    break 
    getContent(docid,content)
    writecollectioninfo()
    mergetoinvertedindex()
    shutil.rmtree("temp")  



def writecollectioninfo():
    global totalwords
    global storeterms
    global totaldocuments
    
    avg_doc_len = totalwords/totaldocuments
    collectionfile = open("collectionInfo.txt","a")
    #wordcount, #uniquewords, #totaldoc, #avg_doc_len
    collectionfile.write(str(uniquewords)+" "+str(totalwords)+" "+str(totaldocuments)+" "+str(avg_doc_len)+" \n")
    collectionfile.close()
    
def mergetoinvertedindex():
    global totalwords
    global storeterms
    global totaldocuments
    global stopwords
    
    invertedindex = open("invertedIndex.txt","w")
    terminfo = open("termInfo.txt","w")
    linecnt=0;
    for term in storeterms.keys():
        # word word_id ctf df 
        terminfo.write(str(term) +" "+ str(storeterms[term][0])+" "+str(storeterms[term][1])+" "+str(storeterms[term][2])+" "+ str(linecnt) +"\n")
        linecnt=linecnt+1
        filepath = "temp/" + str(storeterms[term][0]) +".txt"
        termlines = open(filepath,"r").readlines()
        text = str(storeterms[term][0])
        for line in termlines:
            text =  text +" "+ str(line[:-1]) 
        text = text + "\n"
        invertedindex.write(text)
    terminfo.close()
    invertedindex.close()
        
    
#Process the content part of the file
def getContent(docid,content): 
    global totalwords
    global storeterms
    global totaldocuments
    global stopwords
    
    if ((docid =="") or (content =="") ):
        return
    else : 
        totaldocuments += 1   
        content = content.lower()  
        tempwords= content.replace("-"," ");   
        tempwords = removePunctuation(tempwords)
        tempwords = tempwords.split()
        termcounts = stopnstemndocfile(tempwords,docid)
        createtermfiles(termcounts,docid)      

 
#remove stop words first, then apply stemming  using Porter stemmer. 
#Simultaneously create a term frequency dictionary. 
   
def stopnstemndocfile(words, docid):
    global totalwords
    global storeterms
    global totaldocuments
    global stopwords

    termcounts = dict()
    for word in words:
        if word in stopwords:
            continue
        #elif len(word) ==1:
            #continue
        else:
            word=porter.stem(word)
            if termcounts.has_key(word):
                termcounts[word] += 1
            else:
                termcounts[word] = 1
    docwordcount = 0
    for key in termcounts.keys():        
        docwordcount = docwordcount +  termcounts[key]
    createdocfile(docid, termcounts,docwordcount)
    return termcounts

# Create a document information file  storing the docid, unique word count , document lenght
def createdocfile(docid, termcount,docwordcount):
    docfile = open("docInfo.txt","a")
    docfile.write(str(docid)+" "+str(len(termcount.keys()))+" "+str(docwordcount)+"\n")
    docfile.close()
    

#create file for each term and store document id and document-term frequency for that term            
def createtermfiles(termcounts,docid):
    global totalwords
    global storeterms
    global totaldocuments
    global stopwords
    global uniquewords
    
    for key in termcounts.keys() :
        
        if storeterms.has_key(key):
            #term_id, ctf,df, pos
            storeterms[key]=[storeterms[key][0],storeterms[key][1]+termcounts[key], storeterms[key][2]+ 1]            
        else:
            uniquewords=uniquewords+1
            storeterms[key]=[uniquewords,termcounts[key], 1 ]
        totalwords = totalwords + termcounts[key]
            
        filepath = "temp/" +str(storeterms[key][0]) + ".txt"
        termfile = open(filepath,"a")
        #doc_id tf
        termfile.write( str(docid)+" "+str(termcounts[key])+" ")
        termfile.close()
   
#remove any punctuation marks
def removePunctuation(contentstring):
    out = contentstring.translate(string.maketrans("",""), string.punctuation)
    return out
    
    

#open and close the file in write mode, to delete all contents of the file    
def clearfilecontents(filename):
    clearfile = open(filename, "w")
    clearfile.close()
  
#get all teh stop words from teh file to a dictionary      
def getstopwords() :
    global stopwords
    
    text = open('/MyData/IR/Project/SearchEngine/common_words.txt').readlines()
    records = [s.replace('\n', '') for s in text]
    
    stopwords = dict()
    for record in records:
        stopwords[record] = 0
    return stopwords    

IndexMyTerms()