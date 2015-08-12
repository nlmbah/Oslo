### This script retrieves the BAS GUI statistics (MEC and ISC sensor alarms) and
###  writes them to a file on the local harddrive with a date/time stamp.

#
# ToDo: 1] input values like a BAS config file. BASNR, ip-address/hostname
#       2] Determine if this python script is running on windows or unix
#       3] write logging to default user directory (win & unix)
#       4] cmd line output file

"""
@author: nlmbah
"""

import os.path
import urllib
import datetime
import xml.etree.ElementTree

# logging
import logging
import sys
LOG_FILENAME = 'D:\\Projecten\\Norway-Oslo\\2015_Summer_Standby\\10_Python_BAS-statistics\\BAS_Histograms_Oslo-v01_logging.txt'
logging.basicConfig(filename=LOG_FILENAME,
                    level=logging.DEBUG,
                    format='%(asctime)s ; %(levelname)-8s ; %(message)s',
                    filemode='w')

# Global variables
BasePath = 'D:\\Projecten\\Norway-Oslo\\2015_Summer_Standby\\10_Python_BAS-statistics\\'

# Variables

IpmStatistics_dict = {'00032':'Power resets',
                      '00250':'Communication fault.',
                      '00074':'Cart entered backwards',
                      '00075':'Cart lost from position control',
                      '00031':'Power off',
                      '00029':'Full power backwards',
                      '00030':'Full power forwards',
                      '00313':'Total number of carts (x1000)',
                      '00314':'Operational hours',
                      '00015':'Missing signals at entry sensor',
                      '00016':'Missing signals at exit sensor',
                      '00315':'Carts entered',
                      '00316':'Carts stopped',
                      '00317':'Carts exited',
                      '00318':'Exceptional carts'
                      }



IscStatistics_dict = {'00032':'Power resets',
                      '00250':'Communication fault.',
                      '00215':'Normal empty carts diverted into local area',
                      '00216':'Occupied carts diverted into local area',
                      '00217':'Normal loaded carts diverted into local area',
                      '00218':'Priority carts diverted into local area',
                      '00208':'Normal empty carts passed an area not available',
                      '00209':'Occupied carts passed an area not available',
                      '00210':'Normal loaded carts passed an area not available',
                      '00211':'Priority carts passed an area not available',
                      '00025':'Failed diverts',
                      '00002':'Reads OK',
                      '00005':'Corrected reads',
                      '00008':'Failed reads',
                      '00001':'Sensor alarms'
                     }


LioStatistics_dict = {'00032':'Power resets',
                      '00250':'Communication fault.'
                     }

MecStatistics_dict = {'00032':'Power resets',
                      '00250':'Communication fault.',
                      '00198':'Carts passed the area',
                      '00002':'Reads OK',
                      '00005':'Corrected reads',
                      '00008':'Failed reads',
                      '00001':'Sensor alarms'
                     }



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
            '420':'http://195.69.6.186',
            '100':'http://195.69.6.190',
            '200':'http://195.69.6.191',
            '300':'http://195.69.6.192',
            '421':'http://195.69.6.187',
            '422':'http://195.69.6.188',
            '350':'http://195.69.6.200',
            '450':'http://195.69.6.140',
            '455':'http://195.69.6.202'}

def Date():
    return str(datetime.datetime.now().date())


def Time():
    return str(datetime.datetime.now().time())


def GetStatistics(datafile):
    '''
    Retrieve Info from save statistics XML-file
    Import xml data
    '''
    tree = xml.etree.ElementTree.parse(datafile)
    root = tree.getroot()
    logging.info(root)
    Stats = []
    IscSensorError = ''
    MecSensorError = ''

    # Read ISC and MEC SensorAlarms values
    for device in root.iter('Isc'):

        DeviceName = device.attrib['Name']
        logging.info('DeviceName: %s' %(DeviceName))
        if DeviceName.find('ISC') != -1:
            Iscdict = {}
            Iscdict['Date'] = Date()
            Iscdict['Time'] = Time()
            for item in device.iter('Item'):
                Iscdict[item.attrib['id']] = item.text
            Stats.append(Iscdict)
    return Stats

def OGmain():
    '''
    Read ISC and MEC sensor errors from each BAS and write that to a file.
    '''
    SensorDataCsv = BasePath + Date() + '_BAS_SensorErrors.csv'
    CsvFile = open(SensorDataCsv, 'a+')

    logging.info('Getting BAS Statistics')
    logging.info(' Date     ; Time          ;BAS; ISC ; MEC')
    for BAS_Nr, BAS_Url in BAS_Dict.iteritems():
        BasStatisticsURL = BAS_Url + '/cgi-bin/statistics.cgi'
        BasStatisticsXML = BasePath + BAS_Nr + '_output.xml'

        try:
            urllib.urlretrieve(BasStatisticsURL, BasStatisticsXML)
            SensorErrors = GetStatistics(BasStatisticsXML)

            os.remove(BasStatisticsXML)
        except IOError:
            SensorErrors = str(Date()) + ';' + str(Time()) + ';' + BAS_Nr + ';;'

        print SensorErrors
        CsvFile.write(SensorErrors+'\n')


    CsvFile.close()


def main():
    XML_File = BasePath + 'BAS_Statistics.xml'
    InfoList = GetStatistics(XML_File)

    for item in InfoList:
        logging.info(type(item))
        for key, value in item.iteritems():
            print key, value


if __name__ == "__main__":
    main()
