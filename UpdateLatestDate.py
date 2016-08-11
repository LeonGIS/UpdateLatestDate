# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# UpdateLatestDate.py
# Created on: 2016-08-05

# Description: 
# Finds the max date for each ID in a table and updates a corresponding feature class

# Command Line Example: 
# UpdateLatestDate.py -f "C:\development\localhost.sde\\mygdb.DBO.FacilitiesStreets\\mygdb.DBO.Sign" -w "C:\development\localhost.sde" -t "C:\development\localhost.sde\\mygdb.DBO.MaintTable" -i "ACTDATE" -o "INSTALLDATE" -x "FACILITYID" -y "FACILITYID" -l "C:\development\SignDate.log" -q ""ACTION" = 'REPLACE'"
# Command Line Arguments
# -f: Feature class to update
# -w: Feature class workspace
# -t: Table to search
# -i: Table date field
# -o: Feature class date field
# -x: Table ID field
# -y: Feature class ID field
# -q: Optional query on Table to filter out certain records
# -l: Log file
#---------------------------------------------------------------------------


import arcpy
import logging
import sys, optparse
from optparse import OptionParser


def main(argv):
    print 'start'
    # Declare options
    parser = OptionParser()
    parser.add_option("-f", dest="featureclass", help="Feature class to update")
    parser.add_option("-w", dest="fcworkspace", help="Feature class workspace for editing")
    parser.add_option("-t", dest="table", help="Source table")
    parser.add_option("-i", dest="indatefield", help="Source table date field")
    parser.add_option("-o", dest="outdatefield", help="Feature class date field to update")
    parser.add_option("-x", dest="inidfield", help="Feature class date field to update")
    parser.add_option("-y", dest="outidfield", help="Feature class date field to update")
    parser.add_option("-l", dest="logfile", help="Log file")
    parser.add_option("-q", dest="subquery", help="Optional query on source table to filter records")
   
    # Test options
    (options, args) = parser.parse_args()

    if not options.featureclass:
      parser.error("Missing feature class")
    if not options.fcworkspace:
      parser.error("Missing workspace")
    if not options.table:
      parser.error("Missing source table")
    if not options.indatefield:
      parser.error("Missing table date field")
    if not options.outdatefield:
      parser.error("Missing feature class date field")
    if not options.inidfield:
      parser.error("Missing feature class ID field")
    if not options.outidfield:
      parser.error("Missing table id field")
    if not options.logfile:
      parser.error("Missing logfile")
    
    # Get optional sub query  -  -q ""ACTION" = 'REPLACE'"
    pSubQuery = None
    if options.subquery:
       pSubQuery = options.subquery

    print 'parse options'
           
    ## Set up logging
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=  options.logfile,
                        filemode='a')
    logging.info('Start ***********************')

    pfields = [options.inidfield, options.indatefield]
    pSort = "ORDER BY " +options.inidfield + "," + options.indatefield + " DESC"

    print options.table

    ## Make dictionary of IDs and dates from inpsection table (that meet subquery if applicable)
    dictIDs = dict()
    rows = arcpy.da.SearchCursor(in_table=options.table,field_names=pfields,sql_clause=(None,pSort),where_clause=pSubQuery)

    for row in rows:
      if len(dictIDs) == 0:
        dictIDs[row[0]] = row[1]
      else:
        if not row[0] in dictIDs:
          dictIDs[row[0]] = row[1]
     
    ## Update feature class...
    ## Hardcoded field for sign replacement program
    pOutfields = [options.outidfield, options.outdatefield, "REPLACESTATUS"]
    edit = arcpy.da.Editor(options.fcworkspace)
    
    edit.startEditing(False, True)
    edit.startOperation()

    for k, v in dictIDs.items():
      featid = k
      updatedate = v
      featwhereclause = arcpy.AddFieldDelimiters(options.featureclass, options.outidfield) +  ' = ''\'' + featid + '\''
      print featwhereclause

      with arcpy.da.UpdateCursor(in_table=options.featureclass, field_names=pOutfields, where_clause=featwhereclause) as fc_cursor:

        for fcrow in fc_cursor:
          if fcrow[1] != updatedate:
            fcrow[1] = updatedate
            ## Specific update for sign replacement program
            if fcrow[2] == "Scheduled":
              fcrow[2] = "Complete"
            fc_cursor.updateRow(fcrow)
            logging.info('Update ID ' + featid)
         

      fc_cursor.reset()
    edit.stopOperation()
    edit.stopEditing(True)
    logging.info('End ***********************')

  

            
if __name__ == "__main__":
   main(sys.argv[1:])
