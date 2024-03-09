from flask import Flask, render_template, request as req
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import certifi
import ssl

context = ssl._create_unverified_context()

app = Flask(__name__)

@app.route("/", methods=["GET"])
def homePage():
    return render_template('index.html')

@app.route("/review", methods=["POST", "GET"])
def index():
    if req.method == 'POST':
        try:
            searchString = req.form['content'].replace(" ", "")
            flipkartURL = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkartURL, context=ssl.create_default_context(cafile=certifi.where()))
            flipkartPage = uClient.read()
            uClient.close()
            flipkartHTML = bs(flipkartPage, "html.parser")
            bigBox = flipkartHTML.findAll("div", {"class": "_1AtVbE col-12-12"})
            del bigBox[0:3]
            reviews = []
            for i in bigBox:
                productLink = None
                try:
                    productLink = "https://www.flipkart.com" + i.div.div.div.a['href']
                except Exception as e:
                    pass
                if productLink:
                    try:
                        prodRes = requests.get(productLink)
                        prodRes.encoding = 'utf-8'
                        prod_html = bs(prodRes.text, "html.parser")
                        commentBoxes = prod_html.findAll("div", {"class": "_16PBlm"})
                        for commentBox in commentBoxes:
                            try:
                                name = commentBox.div.div.findAll("p", {"class": "_2sc7ZR _2V5EHH"})[0].text
                            except Exception as e:
                                pass

                            try:
                                rating = commentBox.div.div.div.div.text
                            except Exception as e:
                                pass

                            try:
                                commentHead = commentBox.div.div.div.p.text
                            except Exception as e:
                                pass

                            try:
                                comtag = commentBox.div.div.findAll("div", {"class": ""})
                                custComment = comtag[0].div.text
                            except Exception as e:
                                pass

                            mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead, "Comment": custComment}
                            reviews.append(mydict)
                    except Exception as e:
                        pass
            return render_template('result.html', reviews=reviews[0:len(reviews) - 1])
        except Exception as e:
            pass
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0")
