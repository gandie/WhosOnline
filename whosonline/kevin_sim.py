from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import random


driver = webdriver.Firefox()
driver.get("http://192.168.88.46:3006")

time.sleep(1)
login = driver.find_element_by_css_selector('input[value="Login"]')
login.click()
try:
    while True:
        buttons = driver.find_elements_by_class_name('btn')
        m_buttons = driver.find_elements_by_css_selector('button')
        m_buttons = [b for b in m_buttons if b.text != 'Logout' and b.get_attribute('disabled') != 'disabled']
        buttons += m_buttons
        inputs = driver.find_elements_by_css_selector('input')
        inputs += driver.find_elements_by_css_selector('textarea')
        inputs = [i for i in inputs if i.get_attribute('readonly') is None and i.get_attribute('type') != 'number']
        for input_field in inputs:
            if random.randint(0, 10) < 9:
                continue
            try:
                # input_field.clear()
                input_field.send_keys('Kevin war hier %s' % time.asctime()[7:])
            except Exception as e:
                print(e)
                break
        btn = random.choice(buttons)
        try:
            btn.click()
        except Exception as e:
            print(e)
            pass

except KeyboardInterrupt:
    print('done')

driver.close()
