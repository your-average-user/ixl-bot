from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException as NSE
from selenium.common.exceptions import StaleElementReferenceException as SER
from dotenv import load_dotenv
import openai
import os
import time 
import keyboard

load_dotenv()

open_ai_secret = os.getenv("OPEN_AI_SECRET")

# Getting to ixl
service = Service(executable_path='chromedriver.exe')  # Update with your chromedriver path
driver = webdriver.Chrome(service=service)

driver.get('https://clever.com/oauth/district-picker?channel=clever&client_id=4c63c1cf623dce82caac&confirmed=true&redirect_uri=https%3A%2F%2Fclever.com%2Fin%2Fauth_callback&response_type=code&state=a08e7ef61ae7b5fa4bc87d69203acae126ad6e09724854a5425b00a0fe3f6be3')

input_element = driver.find_element(By.ID, 'autosuggest-input-')
input_element.send_keys("s" + Keys.ENTER)

ignored_exceptions = (NSE, SER)
webdriver_wait = WebDriverWait(driver, 10, poll_frequency=0.2, ignored_exceptions=ignored_exceptions)
school_element = webdriver_wait.until(
    EC.element_to_be_clickable((By.ID, "react-autowhatever-1--item-0"))
)
school_element.click()

if school_element.click:
    active_directory = driver.find_element(By.CLASS_NAME, 'AuthMethod--container')
    active_directory.click()

if active_directory.click:
    time.sleep(2)
    username = driver.find_element(By.ID, 'userNameInput')
    username.send_keys('') # Replace with your username + domain
    password = driver.find_element(By.ID, 'passwordInput')
    password.send_keys('') # Replace with your password
    password.send_keys(Keys.ENTER)



def findQuestion():  
    # if(driver.find_element(By.CLASS_NAME, 'start-button')):
    #     driver.find_element(By.CLASS_NAME, 'start-button').click()
    # else:
    #     return
        
    answer_string=[]
    question = ''
    
    main_panel = driver.find_element(By.CLASS_NAME, 'question-and-submission-view')
    smart_score = driver.find_element(By.CLASS_NAME, 'smartscore-text')
    question_finder = main_panel.find_element(By.CLASS_NAME, "practice-audio-wrapper")
    expression_finder = main_panel.find_element(By.CLASS_NAME, 'secContentPiece')
    answer_finder = main_panel.find_elements(By.CLASS_NAME, "SelectableTile")
    wait_to_display = [main_panel, smart_score, question_finder]
    answer_input = main_panel.find_element(By.CSS_SELECTOR, '.proxy-input[data-testid="testing-fill-in"]')
    fractions = main_panel.find_elements(By.CLASS_NAME, 'vFrac')

    for e in wait_to_display:
        webdriver_wait.until(lambda _ : e.is_displayed)
    for e in answer_finder:
        webdriver_wait.until(lambda _ : e.is_displayed)
    
    #if len(answer_finder) == 0:
    exponent = question_finder.find_elements(By.CSS_SELECTOR, "div.expression.typicalBinaryOperand[data-last-child='true']")
    #fraction = question_finder.find_elements(By.CSS_SELECTOR, "div.vFrac[data-testid='QMVerticalFraction']")
    
    #wait for special characters
    for e in exponent:
        webdriver_wait.until(lambda _ : e.is_displayed)
        #print("These are the exponeents" +e.text)
    
    # if expression_finder.find_element(By.CSS_SELECTOR, 'input'):
    #     print("EXPRESSION FINDER",expression_finder.text)

    def finalExpression():
        
        def fixExponent(text):
            for i in range(len(text)):
                if text[i].isalpha() and text[i + 1].isdigit():
                    fixed_expo = text.replace(text[i] + text[i + 1],text[i] + '^' + text[i + 1])
                    print('FIXED EXPO',fixed_expo)

                    if i != len(fixed_expo):
                        fixExponent(fixed_expo)
                        
                    return fixed_expo
                elif i == len(text):
                    print('POTENTIALLY FIXED EXPO',text)
                    return text
        def fixFraction(text):
            print("PASSED EXPRESDSION", text)
            for i in range(len(text)):
                if text[i] == '\n' and text[i+1].isalnum() and text[i-1].isalnum():
                    fixed_frac = text[0:i] + text[i].replace('\n', ')/') + text[i:len(text)]
                    fixed_frac = fixed_frac.replace('=', '= (')
                    print('FIXED FRAC',fixed_frac)
                    return fixed_frac
            
        def fixSpacing(text):
            for i in range(len(text)):
                if text[i] == '\n':
                    fixed_space = text.replace('\n', '')
                    print('FIXED SPACE',fixed_space)
                    fixSpacing(fixed_space)
                    return fixed_space
                else:
                    return text
        final_expression = fixSpacing(fixFraction(fixExponent(question_finder.text)))
        print("NEW EXPRESSION", final_expression)
        #remove any new lines
        #replace new lines with / when necessary
        #replace new lines with ^ when necessary

        return final_expression
    question += finalExpression()

    def get_chatgpt_response(prompt_text):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt_text}
        ]

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # Or other available models like "gpt-4"
            messages=messages,
            max_tokens=150,
            temperature=0.7 
        )
        if(len(answer_finder) == 0):
            print("prompt(Text box): ", prompt_text, "Response: " + response.choices[0].message.content)
        else:
            print("prompt: ",prompt_text , "response " + response.choices[0].message.content)
        return response.choices[0].message.content
    
    #print(exponent[0].text)
    result_string=', '
    for e in range(len(answer_finder)):
        answer_string.append(answer_finder[e].text)
    
    
    mc_chat_response = get_chatgpt_response(question + ' which answer is correct? restate only the correct answer exactly, no explanation, or extra punctuation' + result_string.join(answer_string))
    tb_chat_response = get_chatgpt_response(question + ' enter the answer exactly as I should enter it into the text box after the equal sign, please do NOT give "f(x) = " before the answer, only enter the answer after that, and simplify the answer into mixed fractions when possible. ')
    
    def answerQuestion():
        time.sleep(1.3)
        if(question == ''):
            findQuestion()
        og_score = smart_score.text
        if(len(answer_finder) ==0 ):
            if(expression_finder.text[0:8] in tb_chat_response or 'f\'(x) = ' in tb_chat_response):
                changed_expression = expression_finder.text.replace('\n', '', 1)
                answer_input.send_keys(changed_expression)
                answer_input.send_keys(Keys.ENTER)
                print('clicked')


            answer_input.send_keys(tb_chat_response)
            answer_input.send_keys(Keys.ENTER)        
            print('clicked2')

        #multiple choice
        else:
            for e in range(len(answer_string)):
                if answer_finder[e].text == mc_chat_response:
                    answer_finder[e].click()
                    answer_finder[e].send_keys(Keys.ENTER)
                    print('clicked')
        time.sleep(1)
        if smart_score.text < og_score:
            
            questionWrong()
        if smart_score.text > og_score:
            findQuestion()

    def questionWrong():
        print("wrojng")
        next_button = driver.find_element(By.CSS_SELECTOR, 'div.next-problem > button.crisp-button')
        webdriver_wait.until(lambda _ : next_button.is_displayed)
        next_button.click()
        findQuestion()

    answerQuestion()
        
if password.send_keys:
    time.sleep(2)
    driver.get('https://clever.com/oauth/authorize?channel=clever-portal&client_id=3513be842ce24d16f779&confirmed=true&district_id=5238c83b5cd6af6a6300156a&redirect_uri=https%3A%2F%2Fwww.ixl.com%2Fclever%2Fsignin&response_type=code')
    access_assignment = driver.get('https://www.ixl.com/math/calculus/find-derivatives-of-rational-functions')
    findQuestion()


while True:
    if keyboard.is_pressed('q'):
        print("Exiting...")
        driver.quit()
        break