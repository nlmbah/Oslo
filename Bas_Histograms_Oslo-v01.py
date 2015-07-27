# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 14:18:29 2013

@author: VINL006347
"""

import urllib
import datetime
import time
import xml.etree.ElementTree
import os

# logging
import logging
import sys
LOG_FILENAME = 'L:\\Python_scripts\\BAS_Histograms_Oslo-v01_logging.txt'
logging.basicConfig(filename=LOG_FILENAME,
                    level=logging.DEBUG,
                    format='%(asctime)s ; %(levelname)-8s ; %(message)s',
                    filemode='w')

# Global variables
BasePath = 'L:\\Python_scripts'
WaitTime = 60
HistogramTime = {}
HistogramDate = {}

BAS_Dict = {'401':'http://195.69.6.170',
            '402':'http://195.69.6.171',
            '403':'http://195.69.6.172',
            '404':'http://195.69.6.173',
            '405':'http://195.69.6.174',
            '408':'http://195.69.6.175',
            '409':'http://195.69.6.176',
            '410':'http://195.69.6.177',
            '411':'http://195.69.6.178',
            '412':'http://195.69.6.179',
            '413':'http://195.69.6.180',
            '415':'http://195.69.6.181',
            '416':'http://195.69.6.182',
            '417':'http://195.69.6.183',
            '418':'http://195.69.6.184',
            '419':'http://195.69.6.185',
            '420':'http://195.69.6.186'}
#            '100':'http://195.69.6.190',
#            '200':'http://195.69.6.191',
#            '300':'http://195.69.6.192',
#            '421':'http://195.69.6.187',
#            '422':'http://195.69.6.188',
#            '350':'http://195.69.6.200',
#            '450':'http://195.69.6.140',
#            '455':'http://195.69.6.202'}


# Functions
def Date():
    yyyymmdd = datetime.datetime.now().date()
    return yyyymmdd

def Time():
    hhmmss = datetime.datetime.now().time()
    return hhmmss
	

def CreateHistogramsOnBas():
    # This function 'clicks' the Get Histograms button on each of the 20 the BASses.
    for BAS_Nr, BAS_Url in BAS_Dict.iteritems():
        CreateHistogramsLink = BAS_Url + '/cgi-bin/histograms.cgi?submit=Get histograms'
        logging.info('CreateHistogramsOnBas: Clicking Histograms button on BAS %s at %s' %(BAS_Nr, str(Time())))
        try:
            urllib.urlopen(CreateHistogramsLink)
        except IOError:
            logging.error('CreateHistogramsOnBas: CreateHistogramsOnBas urlopen for BAS_0%s' %(BAS_Nr) )


def DownloadHistogramsData():
    # This function download the "Show data files" page from the BAS en downloads the xml file
    # mentioned in the last link on this page.

    for BAS_Nr, BAS_Url in BAS_Dict.iteritems():
        # Download histogram overview page with links to Histrogram files
        GetHistogramsLink = BAS_Url + '/cgi-bin/showfiles.cgi?type=DATA'
        logging.info('DownloadHistogramsData:GetHistogramsLink=_%s_' %(GetHistogramsLink))
        HistogramLinksPage = BasePath + '\\BAS_' + BAS_Nr + '.xml'
        logging.info('DownloadHistogramsData:HistogramLinksPage=_%s_' %(HistogramLinksPage))

        try:
            logging.info('DownloadHistogramsData:urllib.urlretrieve(GetHistogramsLink,HistogramLinksPage)' %())
            urllib.urlretrieve(GetHistogramsLink, HistogramLinksPage)
        except IOError:
            logging.error('DownloadHistogramsData:urllib.urlretrieve(GetHistogramsLink,HistogramLinksPage) failed due to _%s_ ' %(error))

        # Get link to last histogram data file
        # http://195.69.6.175/symlinks/data/HISTOGRAMS_20150717_042838.xml
        HistogramFileLink = ''
        try:
            Page = open(HistogramLinksPage, 'r')
        except Exception as readerror:
            logging.error('Could not open %s, due to %' %(HistogramLinksPage, readerror))
        else:
            for line in Page:
                if line.find('/symlinks') > 0:
                    HistogramFileLink = BAS_Url + line.split('"')[5]
            Page.close()
        logging.info('DownloadHistogramsData: HistogramFileLink = %s' %(HistogramFileLink))

        if len(HistogramFileLink) > 0:
            # Download last histogram data file and save the file's timestamp
            HistogramData = BasePath + '\\HistogramData_Bas' + BAS_Nr + '.xml'
            try:
                urllib.urlretrieve(HistogramFileLink,HistogramData)
            except Exception as error:
                logging.error('DownloadHistogramsData: urllib.urlretrieve(HistogramFileLink,HistogramData) failed due to %s' %(error))
            else:
                FileDate = HistogramFileLink[-19:-11]
                HistogramDate[BAS_Nr] = FileDate[:4]+'-'+FileDate[4:6]+'-'+FileDate[6:]
                FileTime = HistogramFileLink[-10:-4]
                HistogramTime[BAS_Nr] = FileTime[:2]+':'+FileTime[2:4]+':'+FileTime[4:]
                logging.info('DownloadHistogramsData: Downloaded : %s' %(HistogramFileLink))
                os.remove(HistogramLinksPage)
        else:
            logging.info('DownloadHistogramsData: No HistogramData for %s' %(BAS_Nr))


def ConvertHistogramData():
    logging.info('Read HistogramData, write as CSV file')

    HistoDataCsv = str(Date())+'_BAS_Histograms.csv'

    try:
        CsvFile = open(HistoDataCsv, 'a+')
    except Exception as error:
        logging.error('ConvertHistogramData: Couldn\'t open %s for writing due to %s' %(CsvFile, error))
    else:
        for BAS_Nr, BAS_Url in BAS_Dict.iteritems():
            HistoDataXml = BasePath + '\\HistogramData_Bas' +BAS_Nr + '.xml'
    
            # Import xml data
            try:
                tree = xml.etree.ElementTree.parse(HistoDataXml)
                root = tree.getroot()
            except IOError:
                logging.error('Could not open xml.etree')
            else:
                # read ISC and MEC histogram values and write them to a file
                for device in root.iter('Isc'):
                    DeviceName = device.attrib['Name']
                    if DeviceName.find('BAS') == -1:
                        for histogram in device.iter('Histogram'):
                            HistogramId = histogram.get('id')
                            StringToPrint = HistogramDate[BAS_Nr]+' '+HistogramTime[BAS_Nr]+';'+DeviceName+';'+str(HistogramId)
                            for item in histogram.iter('Item'):
                                value = item.text
                                StringToPrint = StringToPrint + ';' + str(value)
                            #print StringToPrint
                            CsvFile.write(StringToPrint+'\n')
                os.remove(HistoDataXml)
        CsvFile.close()


def main():
    # Tell the BASes to create Histograms
    CreateHistogramsOnBas()

    # BAS needs some time to obtain the Histogram data
    print('Waiting %s seconds for the BAS to finish the Histrogram file' %(WaitTime))
    time.sleep(WaitTime)

    # Download the Histogram data from the BASes
    print('Starting DownloadHistogramsData()')
    DownloadHistogramsData()

    # Write the Histrogram info the CommaSeparatedValue files
    print('Starting ConvertHistogramData()')
    ConvertHistogramData()


if __name__ == '__main__':
    # Call main function
    main()
