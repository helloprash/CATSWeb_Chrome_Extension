import os, inspect
from pathlib import Path
from bs4 import BeautifulSoup as BS
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from tkinter import messagebox
from flask import Flask, render_template, request, jsonify
from time import sleep
import tkinter as tk
import urllib3
import uiautomation as automation
import steps

current_folder = os.getcwd()

def getUrl():
    sleep(3)
    control = automation.GetFocusedControl()
    controlList = []
    while control:
        controlList.insert(0, control)
        control = control.GetParentControl()
    if len(controlList) == 1:   
        control = controlList[0]
    else:
        control = controlList[1]
    address_control = automation.FindControl(control, lambda c, d: isinstance(c, automation.EditControl) and "Address and search bar" in c.Name)

    return (address_control.CurrentValue())

def checkCM(htmlSource):
    soup = BS(htmlSource, "lxml")
    bold = soup.find_all('b')
    for eachText in bold:
        if eachText.text.strip() == 'Complaint Manager Home Page':
            return True
    return False

def checkSession(htmlSource):
    soup = BS(htmlSource, "lxml")
    try:
        tables = soup.find_all('table',{'id':'TBLoginForm'})
        data = ''
        td = [tr.find_all('td', {'class':'msgerror'}) for tr in tables[0].find_all('tr')]
        for eachtd in td:
            if eachtd:
                data = eachtd[0].text.strip()
        return False, data

    except:
        return True, 'None'

def actionSubmit(browser,ID):
    browser.find_element_by_id('CTRLRECORDTYPE2').click() #Action Radio
    browser.find_element_by_xpath('//*[@id="CTRLRECORDIDTO"]').send_keys(ID) #CWID 
    browser.find_element_by_xpath('//*[@id="CTRLSubmitCommonPageTop"]').click() #Submit
    return browser
    
    
def getCFDetails(htmlSource):
    try:
        soup = BS(htmlSource, "lxml")
        #soup = BS(open(file_path), "lxml")
        center = soup.find_all('center')
        tables = soup.find_all('table',{'id':'TBCALogForm'})

        #Username
        td = [tr.find_all('td', {'id':'TDAssignedTo'}) for tr in tables[0].find_all('tr')]
        for eachtd in td:
            if eachtd:
                data = [each.find('br').next_sibling for each in eachtd]
        username = data[0].text.strip()

        #Medical event
        td = [tr.find_all('td', {'id':'TDStandardText069'}) for tr in tables[0].find_all('tr')]
        for eachtd in td:
            if eachtd:
                data = [each.find('font') for each in eachtd]
        medical_event = data[0].text.strip()

        #pRE
        pREflag = False
        p_tag = soup.find(text='pREs').parent
        font_tag = p_tag.parent
        center_tag = font_tag.parent
        next_center_tag = center_tag.findNext('center').findNext('center')
        pREtables = next_center_tag.find('table',{'id':'TBGenericRecs0'})
        pREtr = pREtables.find_all('tr')

        for i in range(1, len(pREtr)):
            pREtd = [eachtd for eachtd in pREtr[i].find_all('td')]
            data = [item.text.strip() for item in pREtd]
            for j in range(3,13):
                if data[j] == 'Yes':
                    pREflag = True
        
        print(pREflag)

        #RDPC
        td = [tr.find_all('td', {'id':'TDStandardMemo013'}) for tr in tables[0].find_all('tr')]
        for eachtd in td:
            if eachtd:
                data = [each.find('font') for each in eachtd]
        RDPC = data[0].text.strip()
        
        #Current step
        td = [tr.find_all('td', {'id':'TDStandardText003'}) for tr in tables[0].find_all('tr')]
        for eachtd in td:
            if eachtd:
                data = [each.find('font') for each in eachtd]
        step = data[0].text.strip()

        #Product
        p_tag = soup.find(text='Products').parent
        font_tag = p_tag.parent
        center_tag = font_tag.parent
        next_center_tag = center_tag.findNext('center').findNext('center')
        tables = next_center_tag.find_all('table',{'id':'TBGenericRecs0'})
        td = [tr.find_all('td', {'id':'TDRowItem16'}) for tr in tables[0].find_all('tr')]
        td1 = [tr.find_all('td', {'id':'TDRowItem14'}) for tr in tables[0].find_all('tr')]
        td2 = [tr.find_all('td', {'id':'TDRowItem19'}) for tr in tables[0].find_all('tr')]
        for eachtd, eachtd1, eachtd2 in zip(td,td1,td2):
            if (eachtd, eachtd1, eachtd2):
                data = [each.find('font') for each in eachtd]
                data1 = [each.find('font') for each in eachtd1]
                data2 = [each.find('font') for each in eachtd2]
        productFormula = data[0].text.strip()
        productType = data1[0].text.strip()
        serialNum = data2[0].text.strip()

        #Investigation report
        try:
            ir_tag = soup.find(text='Investigation Requests').parent
            font_tag = ir_tag.parent
            center_tag = font_tag.parent
            next_center_tag = center_tag.findNext('center').findNext('center')
            tables = next_center_tag.find_all('table',{'id':'TBGenericRecs0'})
            td = [tr.find_all('td', {'id':'TDRowItem11'}) for tr in tables[0].find_all('tr')]
            td1 = [tr.find_all('td', {'id':'TDRowItem13'}) for tr in tables[0].find_all('tr')]
            for eachtd, eachtd1 in zip(td,td1):
                if (eachtd,eachtd1):
                    data = [each.find('font') for each in eachtd]
                    data1 = [each.find('font') for each in eachtd1]
            IRnum = data[0].text.strip()
            IRstep = data1[0].text.strip()
            IR = True
        except AttributeError:
            IR = False
            IRstep = 'XX'
            IRnum = 'XXXX'
        
        return(True,username,RDPC,medical_event,pREflag,step,productType,productFormula,serialNum,IR,IRstep,IRnum)
    except Exception as err:
        print(err)
        return(False,'username','RDPC','medical_event','pREflag','step','productType','productFormula','serialNum','IR','IRstep','IRnum')


app = Flask(__name__)
 
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/complaint/', methods=['POST'])
def initialization():
    root = tk.Tk()
    root.withdraw()
    CFnum = int(request.form.get('number', 0))
    url = 'http://' + getUrl()
    print(url)
    pjs_file = '\\\\'.join(os.path.join(current_folder,"phantomjs.exe").split('\\'))

    fileFlag = True
    my_file = Path(pjs_file)
    if not my_file.is_file():
        fileFlag = False
        print('fileError')
        data = {'newData': 'phantomjs.exe file not found'}
        data = jsonify(data)
        messagebox.showinfo('Error!','phantomjs.exe file not found')
        return data

    '''
    chrome_options = Options()
    #chrome_options.add_argument("--headless")
    #chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("disable-extensions")      
    browser = webdriver.Chrome(pjs_file, chrome_options=chrome_options)
    '''

    browser = webdriver.PhantomJS(executable_path = pjs_file, desired_capabilities = {'phantomjs.page.settings.resourceTimeout': '5000'})
    browser.implicitly_wait(3)
    browser.set_page_load_timeout(100)

    while True:
        try:
            print('Here 1')
            browser.get(url)
            browser.get('http://cwqa/CATSWebNET/')

            print('Here 2')

            
            sessionFlag, returnMsg = checkSession(browser.page_source)
            if not sessionFlag:
                if returnMsg == 'Your CATSWeb V7 session does not exist.  Please enter your login information:':
                    return False, CFnum, 'session expired!', False, fileFlag
           
            print(browser.current_url)


            CM = checkCM(browser.page_source)
            if CM:
                browser.find_element_by_xpath('//*[@id="TDDisplayPart004"]/font/a/font').click()
            

            browser = actionSubmit(browser,CFnum)
                
            (flag, username,RDPC,medical_event,pREflag,current_step,productType,productFormula,serialNum,IR,IRstep,IRnum) = getCFDetails(browser.page_source)
            print(flag, username,RDPC,medical_event,pREflag,current_step,productType,productFormula,serialNum,IR,IRstep,IRnum)
            break

        except (urllib3.exceptions.TimeoutError, urllib3.exceptions.ReadTimeoutError):
            print('Read Timeout Error')
            browser.quit()
            continue

        except NoSuchElementException as allError:
            browser.quit()
            print(allError)
            data = {'newData': 'Object not found'}
            data = jsonify(data)
            messagebox.showinfo('Error!','Object not found')
            return data

        except:
            continue
                
    process_steps = {
                        '050':steps.step90,
                        '090':steps.step140,
                        '140':steps.step999
                    }

    if not flag:
        data = {'newData': 'This is not a valid complaint folder number'}
        data = jsonify(data)
        print('This is not a valid complaint folder number')
        messagebox.showinfo('Error!','This is not a valid complaint folder number')
        browser.quit()
        return data

    elif medical_event == 'Yes':
        data = {'newData': 'Medical event is Yes. Cannot process'}
        data = jsonify(data)
        print('Medical event is Yes. Cannot process')
        messagebox.showinfo('Error!','Medical event is Yes. Cannot process')
        browser.quit()
        return data


    elif pREflag:
        data = {'newData': 'pRE is YES. Cannot close'}
        data = jsonify(data)
        print('pRE is YES. Cannot close')
        messagebox.showinfo('Error!','pRE is YES. Cannot close')
        browser.quit()
        return data


    elif current_step == '999':
        data = {'newData': 'Complaint folder already closed - step {}'.format(current_step)}
        data = jsonify(data)
        print('Complaint folder already closed - step {}'.format(current_step))
        messagebox.showinfo('Error!','Complaint folder already closed - step {}'.format(current_step))
        browser.quit()
        return data

    elif IR and IRstep != '999':
        data = {'newData': 'IR still open in step {}'.format(IRstep)}
        data = jsonify(data)
        browser.quit()
        messagebox.showinfo('Error!','IR still open in step {}'.format(IRstep))
        return data
        print('IR still open in step {}'.format(IRstep))

    elif len(username) == 0 or len(RDPC) == 0  or len(productFormula) == 0:
        data = {'newData': 'Complaint folder not processable. Kindly check RDPC or product records.'}
        data = jsonify(data)
        browser.quit()
        messagebox.showinfo('Error!','Complaint folder not processable. Kindly check RDPC or product records.')
        return data
        print('Complaint folder not processable. Kindly check RDPC or product records.')

    else:
        try:
            if not IR and (productType == 'Patient Interface') and (RDPC == 'Suction - lack prior to laser fire'):
                if (serialNum[0] != '6'):
                    if current_step == '140':
                        CFnum, statusMsg, statusFlag = process_steps[current_step](browser, CFnum, RDPC=RDPC, productType=productType, productFormula=productFormula, serialNum=serialNum, username=username,IR=IR,IRnum=IRnum)
                    else:
                        CFnum, statusMsg, statusFlag = process_steps['090'](browser, CFnum, RDPC=RDPC, productType=productType, productFormula=productFormula, serialNum=serialNum, username=username,IR=IR,IRnum=IRnum)
                    
                    if statusFlag:
                        messagebox.showinfo('Success!',statusMs)
                    browser.quit()
                    return (True, CFnum, statusMsg, statusFlag, fileFlag)
                else:
                    browser.quit()
                    return (True, CFnum, 'Error! LOT number starts with 6 for PI return', False, fileFlag)   
            
            elif not IR and (RDPC == 'Failure to Capture' or RDPC == 'Loss of Capture') and (productFormula == 'LOI' or productFormula == '0180-1201' or productFormula == '0180-1401') \
            or ((RDPC == 'Fluid Catchment Filled') and (productFormula == 'LOI')):
                if current_step == '140':
                    CFnum, statusMsg, statusFlag = process_steps[current_step](browser, CFnum, RDPC=RDPC, productType=productType, productFormula=productFormula, serialNum=serialNum, username=username,IR=IR,IRnum=IRnum)
                else:
                    CFnum, statusMsg, statusFlag = process_steps['090'](browser, CFnum, RDPC=RDPC, productType=productType, productFormula=productFormula, serialNum=serialNum, username=username,IR=IR,IRnum=IRnum)
                
                browser.quit()
                return (True, CFnum, statusMsg, statusFlag, fileFlag) 
            else:
                print('Inside else part')
                CFnum, statusMsg, statusFlag = process_steps[current_step](browser, CFnum, RDPC=RDPC, productType=productType, productFormula=productFormula, serialNum=serialNum, username=username,IR=IR,IRnum=IRnum)
                browser.quit()
                return (True, CFnum, statusMsg, False, fileFlag)
        except KeyError:
            data = {'newData': 'The current step is {}'.format(current_step)}
            data = jsonify(data)
            browser.quit()
            print('Error! The current step is {}'.format(current_step))
            messagebox.showinfo('Error!','The current step is {}'.format(current_step))
            return data

          
        
 
if __name__ == '__main__':
    app.run(debug=True)





    



    


