from flask import Flask, request, render_template
import pandas as pd
import numpy as np
from itertools import product
from sklearn.metrics import confusion_matrix

app = Flask(__name__)

def replace_empty_string_with_passed(string_):
    if string_ == '':
        return 'Passed'
    else:
        return string_


@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        #Pull data from page
        ao = request.form['ao']
        pc = request.form['pc']
        po = request.form['po']
        pf = request.form['pf']
        bg = request.form['bg']
        error = request.form['error']
        prob = request.form['prob']

        df = pd.read_excel(request.files.get('file'))

        #Capiltilise words and remove rogue spaces to try and clean data
        df = df.applymap(lambda s:s.capitalize().strip() if type(s) == str else s)
        df = df.sort_values(by=[pf])

        classes = df[pf].unique()
        classes = classes[~pd.isnull(classes)]


        #Calculate all initial metrics
        tn = []
        fp = []
        fn = []
        tp = []
        tpr = []
        tnr = []
        fpr = []
        fnr = []
        ppv = []
        ppc = []
        ppnc = []

        for class_ in classes:
            tmp = df[df[pf] == class_]

            tn1, fp1, fn1, tp1 = confusion_matrix(tmp[ao],tmp[po]).ravel()
            tn.append(tn1)
            fp.append(fp1)
            fn.append(fn1)
            tp.append(tp1)

            tpr.append( np.round( tp1/(tp1+fn1),2 ) )
            tnr.append( np.round( tn1/(fp1+tn1),2 ) )
            fpr.append( np.round( fp1/(fp1+tn1),2 ) )
            fnr.append( np.round( fn1/(tp1+fn1),2 ) )
            ppv.append( np.round( tp1/(tp1+fp1),2 ) )
            if prob != '':
                tmp2 = tmp[tmp[ao] == pc]
                ppc.append(np.round(np.mean(tmp2[prob]),2))

                tmp3 = tmp[tmp[ao] != pc]
                ppnc.append(np.round(np.mean(tmp3[prob]),2))
        #Determine pass/fail status of all tests
        bg_index = list(classes).index(bg)

        eop = ''
        fperb = ''
        eod = ''
        ppp = ''
        pcb = ''
        ncb = ''
        te = ''

        for i in range(len(classes)):
            if i == bg_index:
                pass
            else:
                if abs(tnr[i] - tnr[bg_index]) > int(error)/100:
                    eop += 'Failed due to '+ str(np.round(abs(tnr[i] - tnr[bg_index])*100,2))+ '% TNR rate difference between '+ classes[bg_index] + ' and ' + classes[i] + '. '

                if abs(fpr[i] - fpr[bg_index]) > int(error)/100:
                    fperb += 'Failed due to '+ str(np.round(abs(fpr[i] - fpr[bg_index])*100,2))+ '% FPR rate difference between '+ classes[bg_index] + ' and ' + classes[i] + '. '

                if eop != '' or fperb != '':
                    eod = 'Failed as this requires both Equal Opportunity and False positive error rate balance to pass.'

                if abs(ppv[i] - ppv[bg_index]) > int(error)/100:
                    ppp += 'Failed due to '+ str(np.round(abs(ppv[i] - ppv[bg_index])*100,2))+ '% PPV rate difference between '+ classes[bg_index] + ' and ' + classes[i] + '. '

                if prob != '':
                    if abs(ppc[i] - ppc[bg_index]) > int(error)/100:
                        pcb += 'Failed due to '+ str(np.round(abs(ppc[i] - ppc[bg_index])*100,2))+ '% average probability of positive class difference between '+ classes[bg_index] + ' and ' + classes[i] + '. '
                    
                    if abs(ppnc[i] - ppnc[bg_index]) > int(error)/100:
                        ncb += 'Failed due to '+ str(np.round(abs(ppnc[i] - ppnc[bg_index])*100,2))+ '% average probability of negative class difference between '+ classes[bg_index] + ' and ' + classes[i] + '. '
                else:
                    pcb = 'N/A'
                    ncb = 'N/A'

                if abs(fn[i]/fp[i] - fn[bg_index]/fp[bg_index]) > int(error)/100:
                    te += 'Failed due to '+ str(np.round(abs(fn[i]/fp[i] - fn[bg_index]/fp[bg_index])*100,2))+ '% FN/FP ratio difference between '+ classes[bg_index] + ' and ' + classes[i] + '. '

        eop = replace_empty_string_with_passed(eop)
        fperb = replace_empty_string_with_passed(fperb)
        eod = replace_empty_string_with_passed(eod)
        ppp = replace_empty_string_with_passed(ppp)    
        pcb = replace_empty_string_with_passed(pcb) 
        ncb = replace_empty_string_with_passed(ncb)
        te = replace_empty_string_with_passed(te)

        return render_template('upload.html', shape=df.shape, error=error, classes=classes, fn=fn,tn=tn,tp=tp,fp=fp,tpr=tpr,tnr=tnr,fpr=fpr,fnr=fnr,ppv=ppv,eop=eop,fperb=fperb,eod=eod,ppp=ppp,ppc=ppc,ppnc=ppnc,pcb=pcb,ncb=ncb,te=te)
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)