import selenium
from selenium import webdriver as wb
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from nltk import FreqDist
import matplotlib.pyplot as plt

def scrape(job,loc):
    webd=wb.Chrome("chromedriver.exe")
    webd.get("https://www.naukri.com")
    webd.find_element_by_xpath('//*[@id="qsb-keyword-sugg"]').send_keys(job)
    webd.find_element_by_xpath('//*[@id="qsb-location-sugg"]').send_keys(loc)
    webd.find_element_by_xpath('//*[@id="root"]/div[3]/div[2]/section/div/form/div[3]/button').click()
    alljobd,alljobskill,alllink,allcompany=[],[],[],[]
    for i in range(0,3):
        print("stated scraping")
        element = WebDriverWait(webd,15).until(EC.presence_of_element_located((By.CLASS_NAME,"jobTupleHeader")))
        jd,link,company,skills=[],[],[],[]
        alldata=webd.find_elements_by_tag_name("article")
        for alld in alldata:
            results=alld.get_attribute("innerHTML")
            soup = BeautifulSoup(results,'html.parser')
            details=soup.find_all("a")
            jobd=details[0].text
            ln=details[0].get("href")
            comp=details[1].text
            l=soup.find(class_="tags has-description").find_all("li")
            sk=[i.text for i in l]
            jd.append(jobd)
            link.append(ln)
            company.append(comp)
            skills.append(sk)
        target = None
        while target == None:
            try:
                target = webd.find_element_by_link_text("Next")
            except:
                pass
        alljobd.extend(jd)
        alljobskill.extend(skills)
        alllink.extend(link)
        allcompany.extend(company)
        actions = ActionChains(webd)
        actions.move_to_element(target)
        actions.perform()
        target.click()
        print("first page ended")
    webd.close()
    flatter=[item.lower() for sublist in alljobskill for item in sublist]
    mostcommon = FreqDist(flatter).most_common(25)
    zipped = list(mostcommon)
    res = sorted(zipped,key = lambda x:x[1])
    p,q = zip(*res)
    plt.figure(figsize=(50,40))
    plt.barh(p,q)
    plt.xticks(fontsize=40)
    plt.yticks(fontsize=40)
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='JPEG')
    bytes_image.seek(0)
    encoded_img=base64.b64encode(bytes_image.getvalue()).decode("utf-8")
    bytes_image.close()
    data=list(zip(alljobd,alljobskill,allcompany,alllink))
    return encoded_img,data




from flask import Flask,render_template,redirect,request,send_file
import io
import base64
import os

app = Flask(__name__)

@app.route("/")
@app.route("/home.html")
def home():
    return render_template("home.html")

@app.route("/disp.html",methods=['POST'])
def disp():
    job=request.form.get("jobname")
    loc=request.form.get("opt")
    print(job,loc)
    encoded_img,data=scrape(job,loc)
    return render_template("disp.html",img_data=encoded_img,data=data,zip=zip,job=job,loc=loc,column_names=["alljobd","alljobskill","allcompany","alllink"],link="alllink")


if __name__ == "__main__":
    app.run(debug=True)