from bs4 import BeautifulSoup as BS
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

def actionSubmit(browser,ID):
    browser.find_element_by_id('CTRLRECORDTYPE2').click() #Action Radio
    browser.find_element_by_xpath('//*[@id="CTRLRECORDIDTO"]').send_keys(ID) #CWID 
    browser.find_element_by_xpath('//*[@id="CTRLSubmitCommonPageTop"]').click() #Submit

def selectMultiple(browser, xpath, selectList):
    select = Select(browser.find_element_by_xpath(xpath))
    if select.is_multiple:
        select.deselect_all()
    for eachItem in selectList:
        select.select_by_value(eachItem)
    del select

def getpRE(htmlSource):
    soup = BS(htmlSource, "lxml")
    table = soup.find_all('table', {'id':'TBGenericRecs0'})
    tr = table[0].find_all('tr')
    links = tr[1].find_all('a');
    for link in links:
        print(link.text.strip())
        return link.text.strip()

def step90(browser,CFnum, RDPC = 'XXXX', productType = 'XXXX', productFormula = 'XXXX',serialNum='XXXX', username = 'XXXX',IR = False,IRnum = 'XXXX'):
    try:
        browser.find_element_by_xpath('//*[@id="TBTopTable"]/tbody/tr[3]/td/font/b/a[1]/font/b').click() #Edit 
        try:
            selectMultiple(browser,'//*[@id="CTRLStandardText028"]', ['Investigation Required - Service Completed']) #Workflow Decision
        except NoSuchElementException:
            selectMultiple(browser,'//*[@id="CTRLStandardText028"]', ['Investigation Requests Completed'])

        selectMultiple(browser,'//*[@id="CTRLStandardMemo015"]', ['']) #Next Action
        browser.find_element_by_xpath('//*[@id="CTRLStandardDate008"]').clear() #Next Action date
        browser.find_element_by_xpath('//*[@id="CTRLSUBMIT"]').click() #Submit
        pRE(browser,CFnum)
        step140(browser, CFnum, RDPC=RDPC, productType=productType, productFormula=productFormula, serialNum=serialNum, username=username,IR=IR,IRnum=IRnum)
    except Exception as e:
        return CFnum, e, False

def step140(browser,CFnum, RDPC = 'XXXX', productType = 'XXXX', productFormula = 'XXXX',serialNum='XXXX', username = 'XXXX',IR = False,IRnum = 'XXXX'):
    try:
        #Step 140
        pRE(browser,CFnum)
        browser.find_element_by_xpath('//*[@id="TBTopTable"]/tbody/tr[3]/td/font/b/a[1]/font/b').click() #Edit
        
        summary = 'This complaint meets the criteria for no further investigation per Johnson &Johnson Vision Complaint Handling procedures. There is no indication of injury, and this event has been assessed as not being reportable. These types of complaints will continue to be monitored through tracking and trending.'
        Product_Deficiency_Identified = 'No'
        Complaint_trend_similar = 'Yes'
        Internal_CAPA_requested = 'No'
        Reason_for_no_CAPA = 'Product Deficiency not identified'
        
        if (not IR and (RDPC == 'Failure to Capture' or RDPC == 'Loss of Capture') and (productFormula == 'LOI' or productFormula == '0180-1201' or productFormula == '0180-1401')) \
        or (not IR and (RDPC == 'Fluid Catchment Filled') and (productFormula == 'LOI')):
            if not IR:
                selectMultiple(browser,'//*[@id="CTRLStandardText028"]', ['Investigation Not Required']) #Workflow decision
                selectMultiple(browser,'//*[@id="CTRLStandardText022"]',['Per SOP']) #Reason Code
            else:
                selectMultiple(browser,'//*[@id="CTRLStandardText028"]', ['Request Review of Resolved Complaint']) #Workflow decision
                
            Reason_for_no_CAPA = 'Other, describe in CAPA Comments'
            no_CAPA_comments = 'Previously Investigated Complaint per LIB90002'
            browser.find_element_by_xpath("//textarea[@id='CTRLStandardMemo014']").clear() #Other(Reason for no CAPA comments)
            browser.find_element_by_xpath("//textarea[@id='CTRLStandardMemo014']").send_keys(no_CAPA_comments)

            
        elif not IR and RDPC == 'Suction - lack prior to laser fire' and (productFamily == 'Patient Interface') and (serialNum[0] != '6'):
            selectMultiple(browser,'//*[@id="CTRLStandardText028"]', ['Request Review of Resolved Complaint']) #Workflow decision
            Complaint_trend_similar = 'Other (explain in comments)'
            complaint_trend_comments = 'Due to an increase in PI complaints, NR-0099700 was opened to address this issue.'
            precedent_CAPA = 'NR-0099700'
            browser.find_element_by_xpath("//textarea[@id='CTRLStandardMemo016']").clear() #Complaint trend comments
            browser.find_element_by_xpath("//textarea[@id='CTRLStandardMemo016']").send_keys(complaint_trend_comments)
            browser.find_element_by_xpath("//input[@id='CTRLStandardText059']").clear() #precedent CAPA
            browser.find_element_by_xpath("//input[@id='CTRLStandardText059']").send_keys(precedent_CAPA)

        elif IR:
            selectMultiple(browser,'//*[@id="CTRLStandardText028"]', ['Request Review of Resolved Complaint']) #Workflow decision
            initial_report = '''SUMMARY OF REPORTED EVENT:
    It was reported that the there was a {}. No patient contact was reported.
    '''.format(RDPC)

            summary = '''EVENT DESCRIPTION:
    Refer to ‘Summary of Reported Event’ within the Initial Report

    INVESTIGATION RESULTS:
    Refer to CATSWeb Investigation Request # {0}

    CONCLUSION:
    Refer to CATSWeb Investigation Request # {0}
    '''.format(IRnum)
            browser.find_element_by_xpath("//textarea[contains(@id,'CTRLStandardMemo001')]").send_keys(initial_report) #initial report

        else:
            selectMultiple(browser,'//*[@id="CTRLStandardText028"]', ['Request Review of Resolved Complaint']) #Workflow decision
            
        browser.find_element_by_xpath('//*[@id="CTRLStandardMemo004"]').clear() #Final/Summary Report
        browser.find_element_by_xpath('//*[@id="CTRLStandardMemo004"]').send_keys(summary)
        selectMultiple(browser,'//*[@id="CTRLStandardText002"]',[Product_Deficiency_Identified]) #Product Deficiency Identified?
        selectMultiple(browser,'//*[@id="CTRLStandardText018"]', [Complaint_trend_similar]) #Complaint trend similar?
        selectMultiple(browser,'//*[@id="CTRLStandardText054"]', [Internal_CAPA_requested]) #Internal CAPA requested
        selectMultiple(browser,'//*[@id="CTRLStandardText058"]', [Reason_for_no_CAPA]) #Reason for no CAPA
        
        checkbox = browser.find_element_by_xpath('//*[@id="CTRLStandardYesNo020"]') #Complaint ready for closing
        if checkbox.is_selected():
            pass
        else:
            checkbox.click()
                
        selectMultiple(browser,'//*[@id="CTRLStandardText049"]', [username])
        browser.find_element_by_xpath('//*[@id="CTRLReasonForEdit"]').clear() #Reason for edit
        browser.find_element_by_xpath('//*[@id="CTRLReasonForEdit"]').send_keys('RTC')
        selectMultiple(browser,'//*[@id="CTRLStandardMemo015"]', ['Closer Review in Process']) #Next Action
        browser.find_element_by_xpath('//*[@id="CTRLStandardDate008"]').clear() #Next Action date
        browser.find_element_by_xpath('//*[@id="CTRLSUBMIT"]').click() #Submit
        step999(browser, CFnum, RDPC=RDPC, productType=productType, productFormula=productFormula, serialNum=serialNum, username=username,IR=IR,IRnum=IRnum)
    except Exception as e:
        return CFnum, e, False

def step999(browser,CFnum, RDPC = 'XXXX', productType = 'XXXX', productFormula = 'XXXX',serialNum='XXXX', username = 'XXXX',IR = False,IRnum = 'XXXX'):
    try:
        pRE(browser,CFnum)
        browser.find_element_by_xpath('//*[@id="TBTopTable"]/tbody/tr[3]/td/font/b/a[1]/font/b').click() #Edit
        selectMultiple(browser,'//*[@id="CTRLStandardText028"]', ['Close Complaint']) #Workflow Decision
        selectMultiple(browser,'//*[@id="CTRLStandardMemo015"]', ['']) #Next Action
        browser.find_element_by_xpath('//*[@id="CTRLStandardDate008"]').clear() #Next Action date
        browser.find_element_by_xpath('//*[@id="CTRLSUBMIT"]').click() #Submit
        return CFnum, 'Closed', True
    except Exception as e:
        return CFnum, e, False
    

def pRE(browser,CFnum):
    pREID = getpRE(browser.page_source)
    if pREID:
        actionSubmit(browser,pREID)
        browser.find_element_by_xpath('//*[@id="TBTopTable"]/tbody/tr[3]/td/font/b/a[1]/font/b').click() #Edit 
    
        #Select all dropdown ,'009','017','018','019','020'
        xpathList = ['021','006','007','008']
        for eachXpath in xpathList:
            xpath = '//*[@id="CTRLStandardText{}"]'.format(eachXpath)
            selectMultiple(browser,xpath, ['No'])
        
        comments = 'With the information available at the time of this assessment, there is no indication that the event associated with this pRE is considered potentially reportable.'
        browser.find_element_by_xpath('//*[@id="CTRLStandardMemo003"]').clear()
        browser.find_element_by_xpath('//*[@id="CTRLStandardMemo003"]').send_keys(comments)
        browser.find_element_by_xpath('//*[@id="CTRLReasonForEdit"]').clear()
        browser.find_element_by_xpath('//*[@id="CTRLReasonForEdit"]').send_keys('pRE')
        browser.find_element_by_xpath('//*[@id="CTRLSUBMIT"]').click() #Submit
        actionSubmit(browser,CFnum)
