    
def aws_get_table(table_name):
    import boto.dynamodb2
    from boto.dynamodb2.table import Table
    import os
    	# from datetime import datetime

    conn=boto.dynamodb2.connect_to_region(
        'us-east-1',
        aws_access_key_id=os.environ['AWS_DYNAMO_KEY'],
        aws_secret_access_key=os.environ['AWS_DYNAMO_SECRET']
        )

    table = Table(table_name,connection=conn)

    return table


def coned_ra_elec(account_number):

    from selenium import webdriver

    #account_number='494111110330006'

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
    ##  header_text = header.text
    ##  header_text = header_text.replace(' ','_')
    ##  header_text = header_text.lower()
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

#data=coned_ra_elec('494111110330006')