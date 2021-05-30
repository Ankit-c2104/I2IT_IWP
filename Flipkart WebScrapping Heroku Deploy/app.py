#http://127.0.0.1:8000/


from flask import Flask, render_template, request,jsonify
#from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo

app = Flask(__name__)  # initialising the flask app with the name 'app'

@app.route('/',methods=['GET'])
def homepage():
        return render_template('index.html')

@app.route('/scrap', methods=['POST'])
def index():
    if request.method == 'POST':
        search_string = request.form['content'].replace(" ","")
        try:
            dbconn = pymongo.MongoClient("mongodb://localhost:27017/")#connecting to mongodb
            db = dbconn['Flipkart'] # connecting to the database called Flipkart/I2IT
            reviews = db[search_string].find({})
            if reviews.count() > 0:
                 return render_template('results.html', reviews=reviews)  # show the results to user
            else:
                flipkart_url = "https://www.flipkart.com/search?q=" + search_string
                req_web = uReq(flipkart_url) # requesting the webpage from the internet
                flipkart_page = req_web.read() #reading the webpage
                req_web.close() #closing the connection to the web page

                flipkart_html = bs(flipkart_page,'html.parser') #using beautiful soup to convert the page
                                                            # in bytes to a structred html format

                outer_box = flipkart_html.find_all('div',{"class" : "bhgxx2 col-12-12"})
                del outer_box[0:3]
                box = outer_box[0]
                product_link = "https://www.flipkart.com" + box.div.div.div.a['href']
                prodRes = requests.get(product_link)  # getting the product page from server
                prod_html = bs(prodRes.text, "html.parser")  # using beautiful soup,parsing the product page as HTML
                commentboxes = prod_html.find_all("div", {"class": "_3nrCtb"})

                #table = db[search_string]

                # for product name
                p_name = prod_html.find_all('span', {'class': "_35KyD6"})[0].text


                reviews = []

                # For overall rating of the product
                overall_rating = prod_html.find_all('div', {'class' : "hGSR34"})[0].text

                #for total reviews
                total_reviews = prod_html.find_all('span', {'class' : "_38sUEc"})[0].text

                #price
                price = prod_html.find_all('div', {'class' : "_1vC4OE _3qQ9m1"})[0].text
                """
                #try
                images = []
                #prod_img = prod_html.find_all("div", {"class": "_2_AcLJ"})
                prod_img = prod_html.find_all("li", {"class": "_4f8Q22 _2y_FdK"})
                for x in prod_img:
                    try:
                        img = x.div.div.attrs['style']

                        s1 = img.split('url')
                        spl = s1[1].split('(')
                        s2 = spl[1].split(")")
                        res = s2[0]
                        final = res.replace('/128', '/200')
                        new_dic = {"prod_img" : final}
                        images.append(new_dic)
                    except:
                        img1 = 'No image'
                #got the images, but couldn't load it inthe html page properly
                # end try"""
                for x in commentboxes:
                    try:
                        name = x.div.div.find_all('p', {'class': '_3LYOAd _3sxSiS'})[0].text
                    except:
                        name = 'No Name'

                    try:
                        rating = x.div.div.div.div.text
                    except:
                        rating = 'No Ratings'

                    try:
                        commentHead = x.div.div.div.p.text
                    except:
                        commentHead = 'No Comment Heading'

                    try:
                        comtag = x.div.div.find_all('div', {'class': ''})
                        custComment = comtag[0].div.text
                    except:
                        custComment = 'No Customer Comment'

                    # try block

                    """mydict = {"Product" : p_name, "Name" : name, "Rating" : rating,
                              "CommentHead" : commentHead, "Comment" : custComment, "OverallRating" : overall_rating,
                               "totalReviews" : total_reviews, "ProductPrice" : price}#change"""

                    mydict = {"Product": p_name, "Name": name, "Rating": rating,
                              "CommentHead": commentHead, "Comment": custComment,}
                    #ins = table.insert_one(mydict)
                    reviews.append(mydict)
                return render_template('results.html', reviews=reviews)#, images = images)  # showing the review to the user

        except:
            return 'something is wrong'

    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(port=8000,debug=True) # running the app on the local machine on port 8000