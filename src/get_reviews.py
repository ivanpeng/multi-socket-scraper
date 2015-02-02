#takes prodsPath of ALL products, and gets all reviews

from __future__ import division
from random import randrange

import html as h
import zipfile

from time import sleep

import json 
import sys
from bs4 import BeautifulSoup
from PyQt4.QtGui import *  
from PyQt4.QtCore import *  
from PyQt4.QtWebKit import *  

class Render(QWebPage):  
  def __init__(self, url):  
    self.app = QApplication(sys.argv)  
    QWebPage.__init__(self)  
    self.loadFinished.connect(self._loadFinished)  
    self.mainFrame().load(QUrl(url))  
    self.app.exec_()  
  
  def _loadFinished(self, result):  
    self.frame = self.mainFrame()  
    self.app.quit()  
  

'''
This function is built similarly to CanadianTireReviews class. We want to get the product info along with all its ratings
On the MEC site, the data is all on one page. prodsPath and revsPath will be the same. 
The output will be the same, a file of product reviews, for input into the socket runner.
'''
class MECReviews():
    
    def __init__(self, *args, **kwargs):
        self.prodsPath = kwargs.get('prodsPath', '')
        self.revsPath = kwargs.get('revsPath', '')
        # We are really concerned with url for now. prodsPath and revsPath are going to be the same, and for text files.
        self.prodLink = "http://www.mec.ca/product/5030-258/mec-kindle-top-womens"
        #self.ghost = Ghost(wait_timeout=300, download_images=False)
        #page, resources = self.ghost.open(self.prodLink, headers={'User-Agent': 'Mozilla/4.0'})
        #self.html_text = page.content
        r = Render(self.prodLink)
        self.html_text = unicode(r.frame.toHtml())
        self.soup = BeautifulSoup(self.html_text)
        

    def get_product_info(self):
        product_info = {}
        # get product name, description, price, average rating
        name = self.soup.find('title').text
        print "Name: " + name
        desc = self.soup.find('div', id ='longdesc')
        if desc is not None:
            print "Description: " + desc.text
            product_info['description'] = desc 
        
        product_info['name'] = name
        # And so on, and so forth. Do so with price, average rating, categories, etc
        return product_info
        
    def get_product_reviews(self):
        # get all product reviews for a certain product
        reviews_str = self.soup.find('div', id='BVRRContainer')
        print "Reviews String: " + str(reviews_str)
        reviews_dict = {}
        # This is where you parse the objects; I print the objects out right now, but you can write it out. 
        return reviews_dict
    
    def write_reviews(self):
        # write to reviews file here. follow the format of Cdn Tire reviews.
        pass
    

class CanadianTireReviews():

    def __init__(self, *args, **kwargs):
        #self.catPath = r'C:\Users\Amanda\Eclipse_ws\RevCT\catList.txt'
        self.prodsPath = kwargs['prodsPath']
        self.revsPath = kwargs['revsPath']
        #self.folder = r'C:\Users\Amanda\Eclipse_ws\RevCT'
        
        # url = 'http://reviews.canadiantire.ca/9045-en/0388002P/no-super-eco-fuel-saver-reviews/reviews.htm'
        # soup = h.getSoup(url)
        # shop = 'http://www.canadiantire.ca/redirect/redirect.jsp?pageid=prd&CMKF=0&prdid=0388002P&cid=BV_SV_0388002_Auto_AutoChemicalsFluids&utm_campaign=bazaarvoice&utm_medium=SearchVoice&utm_source=RatingsAndReviews&utm_content=Default'
        # shopSoup = h.getSoup(shop)
        #print shopSoup

    def getShopPage(self,prodSoup):
        shop = prodSoup.find_all('div',class_='BVRRSExternalSubjectImage')[-1]  #last one corresponds to avg of product
        shopLink = shop.find('a')['href']
        return shopLink
    
    def getAvgRating(self,prodSoup):
        avg = prodSoup.find_all('div',class_='BVRRSReviewsSummaryRatingImage')  #last one corresponds to avg of product
        if not avg:
            return 'avgRateERROR'
        avgGet = avg[-1]
        avgRate = avgGet.find('img')['alt'].split()[0]     # '1.23 out of 5' only want the 1.23
        if not avgRate:
            return 'avgRateERROR'
        return avgRate
        
    def getNumRev(self,prodSoup):
        num = prodSoup.find('span',itemprop='reviewCount')
        if not num:
            return 'numERROR'
        num = num.string
        if not num:
            return 'numERROR'
        return num

    def getRevList(self, prodSoup):
        #max 20 revs per page
        revList = []
        revs = prodSoup.find_all('div',class_='BVRRReviewTextContainer')
        for r in revs:
            revText = r.find_all('span',class_='BVRRReviewText')
            partList = []
            for ind,revPart in enumerate(revText):            
                #get rid of <\br> tags (new paragraph formatting)
                for part in revPart.contents:
                    if part == prodSoup.br: part = ' '
                    if ind >= 1: part = ' '+part
                    partList.append(part)
                partAdd = ''.join(partList)
                    
            revList.append(str(partAdd))
        if not revList:
            return ['revTextERROR']
        return revList
    
    def getTitleList(self,prodSoup):
        #list of all review titles for curr page of product (up to 20)
        titList = []
        titles = prodSoup.find_all('span',class_='BVRRValue BVRRReviewTitle')
        if not titles:
            return ['titListERROR']
        for t in titles:
            if not t.string:
                tstring = 'titleERROR'
            else:
                tstring = t.string
            titList.append(tstring)
        if not titList:
            return ['titListERROR']
        return titList
    
    def getDateList(self, prodSoup):
        #list of all review dates for curr page of product (up to 20)
        dateList = []
        dates = prodSoup.find_all('meta',itemprop='datePublished')
        for d in dates:
            dateList.append(str(d['content']))
        if not dateList:
            return ['dateListERROR']
        return dateList
    
    def getStarsList(self, prodSoup):
        #list of all overall ratings (Durability, Performance, Quality sub-ratings no longer applicable, so omitted); up to 20 per page
        starsList = []
        stars = prodSoup.find_all('div',id='BVRRRatingOverall_Review_Display')
        for s in stars:
            starsList.append(str(s.find('img')['alt'].split()[0]))
        if not starsList:
            return ['starsListERROR']
        return starsList
                            
    def getProdCode(self, prodSoup):
        code = prodSoup.find('div',class_='BVRRSModuleBody BVRRSCategoryShoppingBody')
        if not code:
            return 'codeERROR'
        getCode = code.find('a')['onclick'].rsplit('/')[-1][:-2]
        if not getCode:
            return 'codeERROR'
        return getCode
    #     code = prodSoup.find('div',id='BVRRSDisplayContentHeaderID')
    #     if not code:
    #         return 'codeERROR'
    #     getCode = code.find('option')
    #     if not getCode:
    #         return 'codeERROR'
    #     prodCode = getCode['value'].split('/')[4]
    #     if not prodCode:
    #         return 'codeERROR'        
    #     return prodCode
    
    def getProdName(self, prodSoup):
        name = prodSoup.find('span',id='BVRRSExternalSubjectTitleProductNameID')
        if name:
            prodName = name.string
        else:
            prodName = 'nameERROR'
        return prodName
    def getDescript(self, prodSoup):
        dscrip = prodSoup.find('div',id='BVRRSExternalSubjectDescriptionID')
        if dscrip:
            prodDescript = dscrip.string.strip()
        else:
            prodDescript = 'descriptionERROR'
        return prodDescript
    
    #### functions below pertain to info grabbed from shop page (not review site)
    def getPrice(self, shopSoup):
        price = shopSoup.find('div',class_='product_detail clearfix')
        if not price:
            return ('priceERROR')
        priceGet = price['data-pdp-page-params']
        j= json.loads(priceGet)
        if not j:
            return 'priceERROR'
        return j['minRegPrice']
    def getCats(self, shopSoup):
        #3-tuple of categories, ordered broadest to narrowest (Department, Category, subCategory)
        cat = shopSoup.find('div',class_='product_detail clearfix')
        if not cat:
            return ('depERROR','catERROR','subCatERROR')
        catGet = cat['data-pdp-page-params']
        j= json.loads(catGet)
        if not j:
            return ('depERROR','catERROR','subCatERROR')
        return (j['departmentName'],j['categoryName'],j['subCategoryName'])
    
    def writeRevs(self, prodLink):
        #given link to prod page, output below for writing to file:
        #===========================================================================
    
        #===========================================================================\
            #with zipfile.ZipFile(revsZip, 'a') as z:
        soup = h.getSoup(prodLink)
        #delay so don't get other soup right away
        randNum = float(1 + randrange(0,150)/31)
        sleep(randNum)        
        shopSoup = h.getSoup(self.getShopPage(soup))
        
        prodCode = self.getProdCode(soup)     
        prodName = self.getProdName(soup)
        print prodLink
        # Need to have unique name for file before we zip it.
        with open("/home/ivan/temp/" + prodCode,'a') as f:    
            soup = h.getSoup(prodLink)
            #delay so don't get soup right away
            randNum = float(1 + randrange(0,200)/31)
            sleep(randNum)
            
            shopSoup = h.getSoup(self.getShopPage(soup))     
            s = True
            #go through reviews, checking for all pages
            pg = 0
            while (s):
                
                #print 'page',pg+1
                starList = self.getStarsList(soup)
                #print 'starLength',len(starList)
                dateList = self.getDateList(soup)
                #print 'dateLength', len(dateList)
                titleList = self.getTitleList(soup)
                #print 'titleLength',len(titleList)
                revList = self.getRevList(soup)
                catsTup = self.getCats(shopSoup)
                #print 'catsTup',catsTup
                price = self.getPrice(shopSoup)
                #print 'price',price
                
                for ind, _ in enumerate(titleList):
                    f.write('Product Code:\t' + self.getProdCode(soup) + '\n')            
                    f.write('Product Name:\t' + self.getProdName(soup) + '\n')
                    f.write('Description:\t' + self.getDescript(soup) + '\n')
                    f.write('Avg Rating:\t' + self.getAvgRating(soup) + '\n')
                    f.write('Num Reviews:\t' + self.getNumRev(soup) + '\n')
                    f.write('Department:\t' + catsTup[0] + '\n')
                    f.write('Category:\t' + catsTup[1] + '\n')
                    f.write('Subcategory:\t' + catsTup[2] + '\n')
                    f.write('Price:\t' + price + '\n')
                    f.write('Stars:\t' + starList[ind] + '\n')            
                    f.write('Date:\t' + dateList[ind] + '\n')
                    f.write('Title:\t' + titleList[ind] + '\n')    
                    f.write('Text:\t' + revList[ind] + '\n') 
                            
                more = soup.find('span',class_='BVRRPageLink BVRRNextPage')
                
                #check if more pages of reviews for this product
                if more:
                    pg += 1
                    #delay
                    randNum = float(1 + randrange(0,200)/31)
                    sleep(randNum)
                    
                    nextPg = more.find('a')
                    nextLink = nextPg.get('href')
                    soup = h.getSoup(nextLink)
                else:
                    s = False
            z = zipfile.ZipFile("reviewsParsed.zip", 'a')
            z.write(f.name)
            z.close()

    def callMaster(self):
        with open(self.prodsPath,'rU') as prodFile:
            prodInd = 0
            for line in prodFile:
                    prodLink = line.strip()  #category link
                    prodInd += 1
                    self.writeRevs(prodLink,prodInd)
                       
                    #random delay
                    randNum = float(11 + randrange(0,200)/31)
                    sleep(randNum)

if __name__ == '__main__':
    m = MECReviews()
    # Need to comment out these two.
    info = m.get_product_info()
    reviews = m.get_product_reviews()
    # THis is the proper thing to call.
    m.write_reviews()