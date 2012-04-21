import string, urllib, re, math, operator, collections, porter

stopwords=[]

docdict = dict()
worddict = dict()
parsedqueries = dict()

okapi = []

avgdoclen =0
avgquerylen = 0
noofuniqueterms=0
totalwords=0


def intiliazeData():
    global avgdoclen,avgquerylen
    global totalwords
    global docdict
    global worddict 
    global parsedqueries
    global okapi, noofuniqueterms
    
    parsedqueries = getParsedQuery()
    
    #open and close a file to clear its contents
    clearfilecontents("op5.txt")
    
    #average query length
    numberofqueries = len(parsedqueries.keys())
    
    querylen=0
    for query in parsedqueries.values():
        querylen = querylen + len(query)
        
    avgquerylen = len(parsedqueries)/numberofqueries
    
    #calculate okapi
    for query in parsedqueries.values():
        okapi.append(float(1.0/(1.0 + 0.5 + (1.5 * len(query)/avgquerylen))))
    
    #average documents' length       
    collectionfile = open("collectionInfo.txt")
    
    line = collectionfile.readline()
    data = line.split()
    noofuniqueterms = float(data[0])
    totalwords = float(data[1])
    avgdoclen = float(data[3])
    
    #create worddict
    #TERMFILE HAS -  word word_id ctf df ptrtoinvertedindex
    wordfile = open("termInfo.txt")
    wordsdata = wordfile.readlines()
    for worddata in wordsdata:
        words = worddata[:-1].split()
        worddict[words[0]] = words[1:]        
    
    #create docdict
    # DOCFILE HAS  - docid noofuniqueterms, doclength(after removing stop words)
    docfile = open("docInfo.txt")
    lines = docfile.readlines()
    for line in lines:
        elements =line[:-1].split()
        #store docid and corresponding uniquetermcount & doclen
        docdict[elements[0]] = [int(elements[1]), int(elements[2])]                        

def bm25():
    global parsedqueries
    
    intiliazeData()
    
    for query_id in sorted(parsedqueries.keys()):
        BM25(query_id)

def intiliazeInvertedIndexdict(querynum):
    global avgdoclen
    global avgquerylen 
    global docdict
    global worddict 
    global parsedqueries
    global okapi
    
    lemur = []
    
    querywords = parsedqueries[querynum]
    
    #INVERTEDINDEXFILE HAS - term_id doc_id tf doc_id tf ... 
    invertedindexfile = open("invertedindex.txt")
    indexlines = invertedindexfile.readlines()
    for queryword in querywords:
        if worddict.has_key(queryword):
            #TERMFILE HAS -  word word_id ctf df ptrtoinvertedindex
            ctf = int(worddict[queryword][1])
            df = int(worddict[queryword][2])
            #get the last element which is ptr in the inverted index file 
            ptr = int(worddict[queryword][3])
            lemur.append(ctf)
            lemur.append(df)
            indexvalues = indexlines[ptr][:-1].split()
                
            valuelen = df*2+1
            i=1
            while i < valuelen:
                lemur.append(int(indexvalues[i]))
                #doc_id = 
                doc_len = int(docdict[indexvalues[i]][1])
                lemur.append(doc_len)
                lemur.append(int(indexvalues[i+1]))
                i = i + 2
        else:
            lemur.append(0)
            lemur.append(0)
    return lemur     


def BM25(query_id):
    global avgdoclen,avgquerylen
    global totalwords
    global docdict
    global worddict 
    global parsedqueries
    global okapi, noofuniqueterms
    
    totalterms = len(parsedqueries[query_id])    
    lemur = intiliazeInvertedIndexdict(query_id)

    finalvalues = dict()

    count = 0
    termcnt = 0
    k1 = 1.5
    k2 = 100
    b = 0.6

    while termcnt < totalterms:
        ctf = float(lemur[count])
        df = int(lemur[count + 1])
        i = count + 2
        maxlength = df * 3 + 2 + count
        while i < maxlength:
            doc_id = int(lemur[i])
            doc_len = int(lemur[i + 1])
            tf = int(lemur[i + 2])
            
            firstTerm = math.log(1.0 / ((float(df) + 0.5)/(84678.0 - float(df) + 0.5)))
            K = k1 * ((1.0 - b) + b * ((float(lemur[i + 1]))/avgdoclen))
            secondTerm = ((k1 + 1.0) * tf)/(K + tf)
            bm25= firstTerm * secondTerm

            if finalvalues.has_key(doc_id):
                finalvalue = finalvalues.get(doc_id)
                finalvalue.append([termcnt, bm25])
            else:
                finalvalues[doc_id] = [[termcnt, bm25]]
            i = i + 3
        count = count + df * 3 + 2

        termcnt = termcnt + 1    

    for doc_id in finalvalues.keys():
        val = 0
        for wordinfo in finalvalues[doc_id]:
            val = val + wordinfo[1]
        finalvalues[doc_id] = val

    writeouputtofile(query_id,finalvalues)
    
    

def writeouputtofile(query_id,finalvalues):
    
    outputfile = open("op5.txt", "a")
        
    sortedValues = sorted(finalvalues.iteritems(), key=operator.itemgetter(1), reverse=True)[0:1000]
      
    cnt = 1
    for item in sortedValues:
        doc_id = str(item[0])
        value = str(item[1])
        outputstring = str(query_id) + " Q0 " + "CACM-" + doc_id + " " + str(cnt) + " " +  value + " Exp\n"
        outputfile.write(outputstring)
        cnt = cnt + 1
    outputfile.close()   


#open and close the file in write mode, to delete all contents of the file    
def clearfilecontents(filename):
    clearfile = open(filename, "w")
    clearfile.close()


def getParsedQuery():
    
    queryid = ""
    content=""
    
    tags = [".T" ,".A" ,".W" , ".K",".B",".X",".N",".C",".I"]
    
    records = open('query.text').readlines()
    cnt =0
    tempQuerylist = dict()  
    totallines = (len(records))
    while cnt < totallines-1:
        if records[cnt][0:2] ==".I" :
            if(queryid!="" or content!=""):
                parsedquery = stopnstem(queryid,content)
                tempQuerylist[queryid] = parsedquery
            queryid = int(records[cnt].split()[1])
            content = ""
            cnt = cnt+1
            continue
        if records[cnt][0:2] in tags :
            while cnt < len(records)-1:
                cnt = cnt + 1                
                if records[cnt][0:2] in tags:
                    break
                content = content + records[cnt]
    parsedquery = stopnstem(queryid,content)
    tempQuerylist[queryid] = parsedquery 
    return tempQuerylist
    
def stopnstem(queryid,query):
    
        global stopwords
    
        getstopwords()
        content = query.lower()
        tempwords= content.replace("-"," ");
        tempwords = removePunctuation(tempwords)
        tempwords = tempwords.split()
        termcounts = dict()
        for word in tempwords:
            if word in stopwords:
                continue
            else:
                word=porter.stem(word)
                if termcounts.has_key(word):
                    termcounts[word] += 1
                else:
                    termcounts[word] = 1
                    
        return termcounts
        
#get all teh stop words from teh file to a dictionary      
def getstopwords() :
    global stopwords

    text = open('common_words.txt').readlines()
    records = [s.replace('\n', '') for s in text]
    
    stopwords = dict()
    for record in records:
        stopwords[record] = 0
    return stopwords   

#remove any punctuation marks
def removePunctuation(contentstring):
    out = contentstring.translate(string.maketrans("",""), string.punctuation)
    return out

bm25()