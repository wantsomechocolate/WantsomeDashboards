def coned_ra_elec(account_number):

    from selenium import webdriver

    ##account_number='494111110330006'

    ## Use phantom to run in background
    driver = webdriver.PhantomJS()

    ## Use ff to create and debug
    # driver = webdriver.Firefox()

    ## You must login if you are not logged in, I'm not sure how to check
    ## though.
    driver.get('https://apps.coned.com/retailaccess/default.asp')
    username_field=driver.find_element_by_name('passUID')
    username_field.send_keys('0')
    password_field=driver.find_element_by_name('passUCD')
    password_field.send_keys('V')
    submit_button=driver.find_element_by_name('Enter2')
    submit_button.click()

    ## After logging in, if you want to continue with the natural user flow
    ## You have to use the iframe construct
    ####driver.switch_to.frame('ramain')
    ####
    ####link = driver.find_element_by_xpath('//a[font[contains(.,"Billing")]]')
    ####
    ####link.click()
    ####
    ####driver.switch_to.frame('ramainbody')

    ## An alternative is to use the url that the iframe comes from directly
    driver.get('https://apps.coned.com/retailaccess/aiBillHist2.asp?passUID=0&passUCD=V')
    account_no_field=driver.find_element_by_name('AcctNo')
    account_no_field.send_keys(account_number)
    submit_button=driver.find_element_by_xpath("//tr[td[input[@name='AcctNo']]]//a")
    submit_button.click()

    ## We should now be on the page with the data
    ## Retrieve all tables tags that appear in the cell tag (td) of other tables
    all_tables = driver.find_elements_by_xpath('//tr/td[table]//table')

    ## Think of a more robust way of getting to this table, which contains the monthly data
    monthly_data_table=all_tables[-2]




    ## Loop through all the tds in the table you want and save them in the data variable

    ## This is the second time I have used an answer from unutbu, what a legend
    ## http://stackoverflow.com/questions/8143023/using-selenium-and-python-to-save-a-table

    header_map={
        "From Date":"start_date",
        "To Date":"end_date",
        "Use":"electric_usage_kwh",
        "Reading":"reading_type",
        "KVARS":"kvars",
        "Demand":"electric_demand_kw",
        "Bill Amt":"retail_access_amount_usd"
        }

    headers=monthly_data_table.find_elements_by_tag_name('th')
    header_list=[]
    for header in headers:
    ##	header_text = header.text
    ##	header_text = header_text.replace(' ','_')
    ##	header_text = header_text.lower()
            header_list.append(header.text)


    data=[]
    data_dict=dict()

    for tr in monthly_data_table.find_elements_by_tag_name('tr'):
        tds=tr.find_elements_by_tag_name('td')
        
        if tds: ## Thanks to my man unutbu for this check
            ##  data.append([td.text for td in tds])

            row_dict={
                'account_number':account_number,
                }
            
            for tds_index in range(len(tds)):
                ## This says for the column we are in, get the header name
                ## as given by the html, then convert that header name to
                ## the db field name using the map we have above.
                ## make that the key, and the text in the current cell the value
                row_dict[header_map[header_list[tds_index]]]=tds[tds_index].text

            data.append(row_dict)

    driver.close()

    return data

data=coned_ra_elec('494111110330006')






# Property	Name	Account Number	User Name
# 5209	DAVAL 36 ASSOCIATES	43-5121-5256-0000-2	520900002
# 5211	DAVAL 37 ASSOCIATES	44-2001-0422-0001-8	521100018
# 5215	WALBER 39 COMPANY L.P.	49-4122-3287-4000-1	521540001
# 5318	BBC 34 CO.	41-1037-8025-0000-4	531800004
# 5334	FORTUSA REALTY CORP	49-4053-6086-1000-4	533410004
# 5335	WALBER 419 CO & 419 PARK AVE.	49-4152-6240-1000-7	533510007
# 5341	18 EAST 41ST STREET	49-4192-4165-5002-6	534150026
# 5350	WALSAM TWENTY-NINE COMPANY	49-4102-3132-0000-5	5350200005
# 5350	WALSAM TWENTY-NINE COMPANY	49-4102-3133-0000-3	535000003
# 5500	500 EIGHTH AVE. L.L.C.	49-4112-3086-9300-7	550093007
# 5500	500 EIGHTH AVE. L.L.C.	49-4111-1103-3000-6	550030006
# 5500	500 EIGHTH AVE. L.L.C.	49-4112-3086-9100-1	550091001
# 5500	500 EIGHTH AVE. L.L.C.	49-4112-3086-9200-9	550092009
# 6210	36 LLC	49-4111-0228-0000-5	621000005
