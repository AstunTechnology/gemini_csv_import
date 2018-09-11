# coding=utf-8

'''
@author: Brian O'Hare
'''
import os
import sys
import unittest
from unittest import skip
import csv
import uuid
import xml
import xml.dom.minidom as minidom
import owslib
from owslib.iso import *
import pyproj
from decimal import *
import logging
import arrow


class TestMetadataImport(unittest.TestCase):

    def setUp(self):
        # remove existing output files
        for file in os.listdir('../output/'):
            os.remove('../output/' + file)

        logging.basicConfig(filename='error.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    
    def testMetadataImport(self):
        raw_data = []
        numrows = 2
        with open('../input/metadata.csv') as csvfile:
            reader = csv.reader(csvfile, dialect='excel')
            for columns in reader:
                raw_data.append(columns)
                """
                        title = columns[0]
                        alt_title = columns[1]
                        creation_date = columns[2]
                        revsion_date = columns[3]
                        abstract = columns[4]
                        pointofcontact_name = columns[5]
                        pointofcontact_email = columns[6]
                        pointofcontact_address = columns[7]
                        pointofcontact_org = columns[8]
                        pointofcontact_position = columns[9]
                        keyword = columns[10]
                        use_limitation = columns[11]
                        licence_constraints = columns[12]
                        copyright_constraints = columns[13]
                        topic_category = columns[14]
                        west_bc = columns[15]
                        east_bc = columns[16]
                        north_bc = columns[17]
                        south_bc = columns[18]
                        extent = columns[19]
                        temp_extent = columns[20]
                        data_format = columns[21]
                        data_version = columns [22]
                        transfer_protocol = columns[23]
                        transfer_url = columns[24]
                        data_quality = columns[25]
                        lineage = columns[26]
                        update_freq = columns[27]
                        inspire_keyword = columns[28]
                        denomitator = columns[29]
                
                print "title: " + title
                """
        # compare the number of rows in the csv (eg 1112) with the number of entries in the list
        self.assertEqual(numrows, len(raw_data), 'Wrong number of rows')

        with open('dataset_empty.xml') as gemini:
            doc = minidom.parseString(gemini.read().encode( "utf-8" ))

        # create metadata from the first csv entry to begin with
        # data = raw_data[1]
        for data in raw_data[1:]:
            try:
                # create a new record from the template
                record = doc.cloneNode(doc)

                # pull out the gemini top-level elements
                fileIdentifier = record.getElementsByTagName('gmd:fileIdentifier')
                language = record.getElementsByTagName('gmd:language')[0]
                hierarchyLevel = record.getElementsByTagName('gmd:hierarchyLevel')            
                contact = record.getElementsByTagName('gmd:contact')
                dateStamp = record.getElementsByTagName('gmd:dateStamp')
                referenceSystemInfo = record.getElementsByTagName('gmd:referenceSystemInfo')
                identificationInfo = record.getElementsByTagName('gmd:identificationInfo')
                distributionInfo = record.getElementsByTagName('gmd:distributionInfo')
                dataQualityInfo = record.getElementsByTagName('gmd:dataQualityInfo')
                metadataMaintenance = record.getElementsByTagName('gmd:metadataMaintenance')

                # generate and add the fileId
                fileId = str(uuid.uuid4())
                fileIdentifier[0].childNodes[1].appendChild(record.createTextNode(fileId))
                identifierElement = identificationInfo[0].getElementsByTagName('gmd:code')[0]
                identifierNode = record.createTextNode(fileId)
                identifierElement.childNodes[1].appendChild(identifierNode)

                # add the title
                title = data[0]
                titleElement = identificationInfo[0].getElementsByTagName('gmd:title')[0]
                titleNode = record.createTextNode(title)
                titleElement.childNodes[1].appendChild(titleNode)
                print "Title:" + title

                # add alternative title
                altTitle = data[1]
                altTitleElement = identificationInfo[0].getElementsByTagName('gmd:alternateTitle')[0]
                altTitleNode = record.createTextNode(altTitle)
                altTitleElement.childNodes[1].appendChild(altTitleNode)
                print "Alt Title:" + altTitle

                # add abstract
                abstract = data[4]
                abstractElement = identificationInfo[0].getElementsByTagName('gmd:abstract')[0] 
                abstractNode = record.createTextNode(abstract)
                abstractElement.childNodes[1].appendChild(abstractNode)
                # print "Abstract" + abstract

                # add topics from comma-separated list
                topics = data[14].split(', ')
                topicElement = identificationInfo[0].getElementsByTagName('gmd:topicCategory')[0]
                for i, t in enumerate(topics):
                    print "Topic: " + t
                    newtopicElement = record.createElement('gmd:MD_TopicCategoryCode')
                    newtopicNode = record.createTextNode(t)
                    newtopicElement.appendChild(newtopicNode)
                    topicElement.appendChild(newtopicElement)

                # add inspire keyword
                inspireKeyword = data[28]
                inspireKeywordElement = identificationInfo[0].getElementsByTagName('gmd:keyword')[0]
                inspireKeywordNode = record.createTextNode(inspireKeyword)
                inspireKeywordElement.childNodes[1].appendChild(inspireKeywordNode)
                print "Inspire Keyword: " + inspireKeyword


                # add free text keywords from comma-separated list
                keywords = data[10].split(', ')
                keywordElement = identificationInfo[0].getElementsByTagName('gmd:MD_Keywords')[1]
                for i, k in enumerate(keywords):
                    print k
                    newkeywordElement = record.createElement('gmd:keyword')
                    newkeywordStringElement = record.createElement('gco:CharacterString')
                    newkeywordNode = record.createTextNode(k)
                    newkeywordStringElement.appendChild(newkeywordNode)
                    newkeywordElement.appendChild(newkeywordStringElement)
                    keywordElement.appendChild(newkeywordElement)

                # add lineage
                lineage = data[26]
                lineageElement = dataQualityInfo[0].getElementsByTagName('gmd:lineage')[0]
                lineageNode = record.createTextNode(lineage)
                lineageElement.childNodes[1].childNodes[1].childNodes[1].appendChild(lineageNode)
                print "lineage: " + lineage

                # add temporal extent
                dates = data[20].split(',')
                beginDate, endDate = '', ''
                if len(dates) == 2:
                    if '/' in data[20]:

                        beginDate = arrow.get(dates[0],'DD/MM/YYYY').format('YYYY-MM-DD')
                        endDate = arrow.get(dates[1],'DD/MM/YYYY').format('YYYY-MM-DD')
                    elif '-' in data[20]:
                        beginDate = dates[0]
                        endDate = dates[1]
                    else:
                        print "Temp extent dates in wrong format"
                    
                    print "Beginning date: " + beginDate
                    print "End date: " + endDate
                else:
                    beginDate = dates[0]
                    print "Beginning date: " + beginDate
                temporalElement = identificationInfo[0].getElementsByTagName('gmd:temporalElement')[0]
                beginDateNode = record.createTextNode(beginDate)
                endDateNode = record.createTextNode(endDate)
                temporalElement.childNodes[1].childNodes[1].childNodes[1].childNodes[1].appendChild(beginDateNode)
                temporalElement.childNodes[1].childNodes[1].childNodes[1].childNodes[3].appendChild(endDateNode)

                # update gml:TimePeriod id attribute
                gmlId = '_' + str(uuid.uuid4())
                timePeriodElement = identificationInfo[0].getElementsByTagName('gml:TimePeriod')[0]
                timePeriodElement.setAttributeNS('http://www.opengis.net/gml/3.2', 'gml:id', gmlId)

                # add distribution format, version, transfer options
                distFormats = data[21].split(',')
                versions = data[22].split(',')
                print "Formats: " + str(distFormats)
                print "Versions: " + str(versions)
                nameElement = distributionInfo[0].getElementsByTagName('gmd:MD_Distribution')[0]

                for i, k in zip(distFormats, versions):
                    newDistroFormatNode = record.createElement('gmd:distributionFormat')
                    newMDFormatNode = record.createElement('gmd:MD_Format')
                    
                    newDistFormatElement = record.createElement('gmd:name')
                    newDistFormatStringElement = record.createElement('gco:CharacterString')
                    newDistFormatNode=record.createTextNode(i)
                    newDistFormatStringElement.appendChild(newDistFormatNode)
                    newDistFormatElement.appendChild(newDistFormatStringElement)

                    newMDFormatNode.appendChild(newDistFormatElement)
                    newDistroFormatNode.appendChild(newMDFormatNode)

                    newVersionElement = record.createElement('gmd:version')
                    newVersionStringElement = record.createElement('gco:CharacterString')
                    newVersionNode=record.createTextNode(k)
                    newVersionStringElement.appendChild(newVersionNode)
                    newVersionElement.appendChild(newVersionStringElement)

                    newMDFormatNode.appendChild(newVersionElement)
                    newDistroFormatNode.appendChild(newMDFormatNode)

                    # must be inserted before the transferoptions node
                    nameElement.insertBefore(newDistroFormatNode, distributionInfo[0].getElementsByTagName('gmd:transferOptions')[0])
                    
                    print "Distribution format: " + i + " Version: " + k


                # add transfer url
                transferURL = data[24]
                transferURLElement = distributionInfo[0].getElementsByTagName('gmd:URL')[0]
                transferURLNode = record.createTextNode(transferURL)
                transferURLElement.appendChild(transferURLNode)
                print "URL: " + transferURL

                # add transfer protocol
                transferProtocol = data[22]
                transferProtocolElement = distributionInfo[0].getElementsByTagName('gmd:protocol')[0]
                transferProtocolNode = record.createTextNode(transferProtocol)
                transferProtocolElement.childNodes[1].appendChild(transferProtocolNode)
                print "Protocol: " + transferProtocol

                # add transfer description
                # transferDesc = data[38]
                # transferDescElement = distributionInfo[0].getElementsByTagName('gmd:description')[0]
                # transferDescNode = record.createTextNode(transferDesc)
                # transferDescElement.childNodes[1].appendChild(transferDescNode)

                # add data quality and repeat it in the level description
                dataQuality = data[25]
                dataQualityElement = dataQualityInfo[0].getElementsByTagName('gmd:MD_ScopeCode')[0]
                dataQualityDescElement = dataQualityInfo[0].getElementsByTagName('gmd:other')[0]
                dataQualityNode = record.createTextNode(dataQuality)
                dataQualityDescNode = record.createTextNode(dataQuality)
                dataQualityElement.setAttribute("codeListValue", dataQuality)
                dataQualityElement.appendChild(dataQualityNode)
                dataQualityDescElement.childNodes[1].appendChild(dataQualityDescNode)
                print "dataquality: " + dataQuality
                
                # add geographic extents - no need to transform as it's in wgs84
                bng = pyproj.Proj(init='epsg:27700')
                wgs84 = pyproj.Proj(init='epsg:4326')
                try:
                    west, east, north, south = data[15], data[16], data[17], data[18]
                    westNode = record.createTextNode(west)
                    eastNode = record.createTextNode(east)
                    northNode = record.createTextNode(north)
                    southNode = record.createTextNode(south)
                    print "BBox: %s,%s,%s,%s" % (west,east,south,north)
                    geoBoundingBoxElement = identificationInfo[0].getElementsByTagName('gmd:EX_GeographicBoundingBox')[0]
                    geoBoundingBoxElement.childNodes[3].childNodes[1].appendChild(westNode)
                    geoBoundingBoxElement.childNodes[5].childNodes[1].appendChild(eastNode)
                    geoBoundingBoxElement.childNodes[7].childNodes[1].appendChild(southNode)
                    geoBoundingBoxElement.childNodes[9].childNodes[1].appendChild(northNode)
                except:
                    # create a metadata record even if there's no extent given
                    pass

                # # add extent (geographic description)
                extent = data[19]
                extentElement = identificationInfo[0].getElementsByTagName('gmd:code')[1]
                extentNode = record.createTextNode(extent)
                extentElement.childNodes[1].appendChild(extentNode)
                print "Extent: " + extent

                # Usage Constraints
                useLimitation = data[11]
                useLimitationElement = identificationInfo[0].getElementsByTagName('gmd:useLimitation')[0]
                useLimitationNode = record.createTextNode(useLimitation)
                useLimitationElement.childNodes[1].appendChild(useLimitationNode)
                print "Use Limitation: " + useLimitation

                # Resource Constraints
                licenceConstraint = data[12]
                copyrightConstraint = data[13]
                licenceconstraintsElement = identificationInfo[0].getElementsByTagName('gmd:otherConstraints')[0]
                copyrightconstraintsElement = identificationInfo[0].getElementsByTagName('gmd:otherConstraints')[1]
                licenceConstraintNode = record.createTextNode(licenceConstraint)
                copyrightConstraintNode = record.createTextNode(copyrightConstraint)
                licenceconstraintsElement.childNodes[1].appendChild(licenceConstraintNode)
                copyrightconstraintsElement.childNodes[1].appendChild(copyrightConstraintNode)
                print "License Constraint: " + licenceConstraint
                print "Copyright Contraint: " + copyrightConstraint

                # Points of Contact
                # TODO copy to top-level gmd:contact too
                contactName = data[5]
                contactEmail = data[6]
                contactAddress = data[7]
                contactOrg = data[8]
                contactPosition = data[9]

                ## Identification Info Point of Contact
                contactNameElement = identificationInfo[0].getElementsByTagName('gmd:individualName')[0]
                contactOrgElement = identificationInfo[0].getElementsByTagName('gmd:organisationName')[0]
                contactPosElement = identificationInfo[0].getElementsByTagName('gmd:positionName')[0]               
                contactAddElement = identificationInfo[0].getElementsByTagName('gmd:deliveryPoint')[0]
                contactEmailElement = identificationInfo[0].getElementsByTagName('gmd:electronicMailAddress')[0]
                
                contactNameNode = record.createTextNode(contactName)
                contactOrgNode = record.createTextNode(contactOrg)
                contactPositionNode = record.createTextNode(contactPosition)
                contactAddressNode = record.createTextNode(contactAddress)
                contactEmailNode = record.createTextNode(contactEmail)
                contactNameElement.childNodes[1].appendChild(contactNameNode)
                contactEmailElement.childNodes[1].appendChild(contactEmailNode)
                contactOrgElement.childNodes[1].appendChild(contactOrgNode)
                contactPosElement.childNodes[1].appendChild(contactPositionNode)
                contactAddElement.childNodes[1].appendChild(contactAddressNode)

                ## Metadata Point of Contact
                metadatacontactNameElement = contact[0].getElementsByTagName('gmd:individualName')[0]
                metadatacontactOrgElement = contact[0].getElementsByTagName('gmd:organisationName')[0]
                metadatacontactPosElement = contact[0].getElementsByTagName('gmd:positionName')[0]               
                metadatacontactAddElement = contact[0].getElementsByTagName('gmd:deliveryPoint')[0]
                metadatacontactEmailElement = contact[0].getElementsByTagName('gmd:electronicMailAddress')[0]
                
                metadatacontactNameNode = record.createTextNode(contactName)
                metadatacontactOrgNode = record.createTextNode(contactOrg)
                metadatacontactPositionNode = record.createTextNode(contactPosition)
                metadatacontactAddressNode = record.createTextNode(contactAddress)
                metadatacontactEmailNode = record.createTextNode(contactEmail)
                metadatacontactNameElement.childNodes[1].appendChild(metadatacontactNameNode)
                metadatacontactEmailElement.childNodes[1].appendChild(metadatacontactEmailNode)
                metadatacontactOrgElement.childNodes[1].appendChild(metadatacontactOrgNode)
                metadatacontactPosElement.childNodes[1].appendChild(metadatacontactPositionNode)
                metadatacontactAddElement.childNodes[1].appendChild(metadatacontactAddressNode)
                print "Name: " + contactName
                print "Email: " + contactEmail
                print "Address: " + contactAddress
                print "Organisation: " + contactOrg
                print "Position: " + contactPosition

               
                # add dataset reference dates 
                if '/' in data[2]:
                    creationDate = arrow.get(data[2],'DD/MM/YYYY').format('YYYY-MM-DD')
                elif '-' in data[2]:
                    creationDate = data[2]
                else:
                    print "creationdate in wrong format"
                creationDateElement = identificationInfo[0].getElementsByTagName('gmd:date')[0]
                creationDateNode = record.createTextNode(creationDate)
                creationDateElement.childNodes[1].childNodes[1].childNodes[1].appendChild(creationDateNode)
                print "Creation date:" + creationDate

                if '/' in data[3]:
                    revisionDate = arrow.get(data[3],'DD/MM/YYYY').format('YYYY-MM-DD')
                elif '-' in data[3]:
                    revisionDate = data[3]
                else:
                    print "revisiondate in wrong format"
                revisionDateElement = identificationInfo[0].getElementsByTagName('gmd:date')[2]
                revisionDateNode = record.createTextNode(revisionDate)
                revisionDateElement.childNodes[1].childNodes[1].childNodes[1].appendChild(revisionDateNode)
                print "Revision Date: " + revisionDate

                # update frequency
                updateFrequency = data[27]
                updateFrequencyElement = identificationInfo[0].getElementsByTagName('gmd:MD_MaintenanceFrequencyCode')[0]
                updateFrequencyNode = record.createTextNode(updateFrequency)
                updateFrequencyElement.setAttribute("codeListValue", updateFrequency)
                updateFrequencyElement.appendChild(updateFrequencyNode)
                print "Update Frequency: " + updateFrequency    

                # denominator
                denominator = data[29]
                denominatorElement=identificationInfo[0].getElementsByTagName('gmd:denominator')[0]
                denominatorNode = record.createTextNode(denominator)
                denominatorElement.childNodes[1].appendChild(denominatorNode)
                print "Scale: " + denominator



                # write out the gemini record
                filename = '../output/%s.xml' % fileId
                with open(filename,'w') as test_xml:
                    test_xml.write(record.toprettyxml(newl="", encoding="utf-8"))
            except:
                e = sys.exc_info()[1]
                logging.debug("Import failed for entry %s" % data[0])
                logging.debug("Specific error: %s" % e)
    
    @skip('')
    def testOWSMetadataImport(self):
        raw_data = []
        with open('../input/metadata.csv') as csvfile:
            reader = csv.reader(csvfile, dialect='excel')
            for columns in reader:
                raw_data.append(columns)   
        
        md = MD_Metadata(etree.parse('gemini-template.xml'))
        md.identification.topiccategory = ['farming','environment']
        print md.identification.topiccategory
        outfile = open('mdtest.xml','w')
        # crap, can't update the model and write back out - this is badly needed!!
        outfile.write(md.xml) 
        

if __name__ == "__main__":
    unittest.main()