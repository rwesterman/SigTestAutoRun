'''
#

TODO: embed flag based on speed; 
      don't compile datasets if single dir;  Combines from higher level multiples, or leaves alone in single lower layer
      add html /nf option to kill html output
      add /P option for preset test
      check sigtest path, check files path
      add test mode

# ver 0.93 adds use of a configuration file. This is not yet tested for dual-port datasets.
# ver 0.92 fixes bug that caused default template name to appear regardless of user selection. 	  
# ver 0.91 scans Program File (x86) for installed SigTest directories (crude and does not check for sigtest.exe)
#     added method to enter path for SigTest if not in Program Files (x86)...
#     runs help function if secondary input at command line, defaults to simple run
#     added defaults for all input variables except beginning of file input
# ver 0.9 allows Sigtest to be called from "Program Files (x86)" directory
#
# ver 0.8 add exclusionary segment (intended for chassis analysis to exclude slot1)
#
# ver 0.7b combine all the results at the top level when done, add time status
# ver 0.7a can find clocks in the subdirectory search.  However, can not autoswtich between Dual-Port and not 
#     since the actual template has to be dual port. NEED BETTER PROGRESS SYSTEM
# ver 0.7 searches all subdirectories for files to run and runs them all, breaks dual-port for now due to paths
#
# ver 0.6 matches clock to data waveform assuming common naming scheme with data-clock identifier
#     this version runs both dual port and data only
#
# ver 0.5 of dp version, based on ver 0.5 of base version.
#     attempt to add dual-port with auto clock search...
'''
import os, fnmatch
import datetime, fileinput
import subprocess, glob
#import msvcrt
from time import clock
from sys import argv


def run_sigtest (pairedList, filters, tmpltdir, tmplt, callsigtest, dpmethod=False, embedFlag=False, si=20):
#  dataFileList: List with data-clock pairs to process
#  filters:  a list of filters for identifing files
#  tmpltdir:  SigTest directory where tempalte is located
#  tmplt: SigTest anaylsis template
#  callsigtest:  the string used to call the sigtest application, without options
#  method:  flag for dual-port or data-only analysis
   timeStartSigtestBatch=clock()
   timeSingleFile=0
   timeToNow=0
   timeToGo=0
   paths=[]
   print '  SigTest processing using {0}\\{1}\n'.format(tmpltdir,tmplt)
   speed=filters[0]; dataid=filters[1]; clkid=filters[2]; prefix=filters[3]; suffix=filters[4]
   path=os.getcwd()
   logFile= prefix + "--" + tmplt.split('.')[0] + "--sigtest.tsv" 
   for counter, pair in enumerate(pairedList):                #Create Indexed loop for a progress counter of some kind...
      path = pair[0].rsplit('\\',1)[0]
      #print path #Debug
      if not(path in paths):
         paths.append(path)
      # add path and file for command line switches
      options=["/d",path,"/s",pair[0].rsplit('\\',1)[1]]
      # add clock file to options for dual-port analysis
      if dpmethod: 
         try:
            addClk="/cs" + pair[1].rsplit('\\',1)[1]
            options.extend(["/cs",pair[1].rsplit('\\',1)[1]])
         except:
            addClk=''
      else:
         addClk=''
      # add embed flag for > Gen2 analysis, currently not implemented for actual use
      if embedFlag:
         embed="/e"
      else:
         embed="/ne"
      options.append(embed)
      # add html output, header lines to skip, sample interval
      #  Need to have logfile and html tweaked for test mode
      #  Skip sample interval and header lines for .wfm (or native equipment data) files
      #options.extend(["/nf",  "/h", "10", "/si", str(si),"/o", logFile])
      options.append("/f")
      #  add custom log file name
      options.extend(["/o", logFile])
      template=tmpltdir+"\\"+tmplt
      options.extend(["/t",template])    
      updateString =( 'Processing ' + str(counter+1).zfill(len(str(len(pairedList)))) + ' of ' + str(len(pairedList)) + ',  TimeSoFar ' + str(datetime.timedelta(seconds=int(timeToNow))) +'  EstTimeRemaining '+str(datetime.timedelta(seconds=int(timeToGo))))
      print updateString,  #END COMMA NEEDED TO CONTINUE THE LINE FOR THE BACKSPACE
      addBkspc='\b'
      totalBkspc=addBkspc*(2+len(updateString))
      print totalBkspc,  #END COMMA NEEDED TO BACKSPACE
      fileStartTime=clock()
      try:
         if (dpmethod and addClk) or (not(dpmethod) and not(addClk)):
            #print callsigtest, options   #Debug
            #subprocess.call([callsigtest]) #Debug
            subprocess.call([callsigtest] + options)
         else:
            print "  Skipping {0}, no clk".format(pair[0].replace(path,''))
      except KeyboardInterrupt, e:
         exit('Ctrl-C, aborting')
      timeSingleFile=clock()-fileStartTime
      timeToNow=clock()-timeStartSigtestBatch
      filesUnprocessed=float(len(pairedList))-(counter+1)
      timeToGo=filesUnprocessed*timeToNow/(counter+1)
      if not((counter+1)==len(pairedList)):   
         pass
   if len(paths)>1:  #this only checks multiple paths.  Does not pull from from lower path, leave there
      combineOutputs(paths,logFile)
   timeTotalSigtestBatch=(clock()-timeStartSigtestBatch)
   #print '\n'
   print 'Batch Job Time: {0}'.format(str(datetime.timedelta(seconds=int(timeTotalSigtestBatch))))
   return(len(pairedList)) 

def combineOutputs(paths,filename):
#This combine all the subdirectory results into a single file from dir where script called from
   combinedFile=filename.split('--',1)[0]+'--combined--'+filename.split('--',1)[1]
   addfile=open(combinedFile,'w')
   for path in paths:
      #getFile=path+"\\"+'TESTING_'+filename.rsplit('.',1)[0]+'_test.'+filename.rsplit('.',1)[1] #debug
      getFile=path+"\\"+filename
      for line in fileinput.input(getFile):
         addfile.write(line)
   addfile.close()
   return() 

'''
def sigtest_run_multi(filelist, tmpltdir, tmplt,pref):
# THERE APPEAR TO BE ISSUES WITH RUNNING MULTIPLE INSTANCES OF SIGTEST DUE TO LABVIEW CVI
   for file in filelist:
      sigtest_run(file, tmpltdir, tmplt,pref)
      #print file
      #print callsigtest+options
   return()
'''

    
def getFiles(filters=['','','','','*.wfm','']):   
#Routine to expand files based on a prefix and suffix
#filters:  speed, dataid, clkid, prefix, suffix
   speed=filters[0]; dataid=filters[1]; clkid=filters[2]; prefix=filters[3]; suffix=filters[4]; exclude=filters[5]
   #suffix='csv'  #debug
   dataFileList=[]
   clockFileList=[]
   if (not(prefix) or prefix=='none'):
      prefix='*'
   else:
      prefix=prefix+'*'
   suffix='*.'+suffix  #only process after the final period
   dataidTemp='*'+dataid+'*'
   if clkid:
      clkidTemp='*'+clkid+'*'
   if speed:
      speedTemp='*'+speed+'*'
   else:
      speedTemp='*'
   if not(exclude):
      #print 'no exclude'
      exclude='qwerty'
   print '\n  Searching with: {0}, {1}, {2}, {3}, {4}, and !{5}\n'.format(prefix,suffix,speed,dataid,clkid, exclude)
   for (dir_current, subdirs, files) in os.walk('.'):
      for file in files:
         #if fnmatch.fnmatch(file, suffix) and file.startswith(prefix) and fnmatch.fnmatch(file, speedTemp) and(not(exclude in file)): 
         if fnmatch.fnmatch(file, suffix) and fnmatch.fnmatch(file, prefix) and fnmatch.fnmatch(file, speedTemp) and(not(exclude in file)): 
         #if fnmatch.fnmatch(file, suffix) and fnmatch.fnmatch(file, prefix) and fnmatch.fnmatch(file, speedTemp) and not(fnmatch.fnmatch(file,exclude)): 
            filepath1 = os.getcwd() + dir_current.lstrip(".") + "\\" + file
            if fnmatch.fnmatch(file, dataidTemp):
               dataFileList.append(filepath1)   
            elif fnmatch.fnmatch(file, clkidTemp):  
               clockFileList.append(filepath1)   
            else:
               pass  # for completeness
   matchedPairList=[]
   for dataFile in dataFileList:  #This is running after after both lists are complete.
      matchedPair=[]
      print dataFile.split(dataid)
      basenamed=dataFile.split(dataid)[0]    #before id
      acqdata=dataFile.split(dataid)[1]      #after id
      matchedPair.append(dataFile)
      for indx, clockFile in enumerate(clockFileList):
         if (clockFile.split(clkid)[0]==basenamed and clockFile.split(clkid)[1]==acqdata):
            matchedPair.append(clockFile); 
            clockFileList.pop(indx)
      if len(matchedPair)==1:  #wait until after the clock matching loop to see if something matched
         matchedPair.append('single')
      matchedPairList.append(matchedPair)
   print '  Completed getFiles with {0} pairs'.format(len(matchedPairList))  #DEBUG
   return(matchedPairList)


def get_cmdline_file_input():
   fileSuffix='wfm'               #default, will not handle other file formats...
   filePrefix=raw_input('Enter the beginning of the file name to match: ')
   if not(filePrefix):
      print'  No Prefix provided'
   return(filePrefix,fileSuffix)

def get_config_file():
   """Get one line script from file entered by user. File template will have header line"""

   usrFileDir=raw_input('Enter full path to configuration file, including filename: ')
   with open(usrFileDir, 'r') as f:
      f.readline()
      config = f.readlines()
      #print config
      return config

def get_cmdline_template():
   # set up some defaults
   reqTempDir='PCIE_3_0_CARD'
   reqTemp='PCIE_3_8GB_CEM.dat'
   usrTempDir=raw_input('Enter the SigTest technology directory: ')
   usrTemp=raw_input('Enter the SigTest template to use: ')
   if usrTempDir:
      reqTempDir=usrTempDir
   if usrTemp:
      reqTemp=usrTemp
   tmp=raw_input('Does template use embedding? y/n  ')  #needed becuase of the "memory" feature
   if tmp=='y':
      embed=True
   else:
      embed=False
   #print reqTempDir, reqTemp
   return(reqTempDir,reqTemp,embed)


def get_filters_cmdline(method):
   filters=[]
#filters:  speed, dataid, clkid, prefix, suffix
#used the append method, this is not the best and must be carefully tracked.
#better would be  filters=[null]*6, or something similiar (fixed size, modify the location)
   speedID=raw_input('Enter the speed file identifer: ')
   if not(speedID):
      print'  No data identifier provided, assuming \'g3\''
      speedID='_g3_'
   filters.append(speedID)
   dataID=raw_input('Enter the data file identifer: ')
   if not(dataID):
      dataID=speedID
      print'  No data identifier provided, assuming {0}'.format(speedID)
   filters.append(dataID)
   if method:              #Dual port mode selected
      clckID=raw_input('Enter the clock file identifer: ')
      if not(clckID):
         clckID='Math2'
         print'  No data identifier provided, assuming {0}'.format(clckID)
   else:
      clckID='none'
   filters.append(clckID)
   fileSuffix='wfm'               #default, will not handle other file formats...
   filePrefix=raw_input('Enter the beginning of the file name to match: ')
   if not(filePrefix):
      print'  No Prefix provided'
      filePrefix='none'
   filters.append(filePrefix)
   filters.append(fileSuffix)
   exclude=raw_input('Enter an exclusion filter: ')
   if not(exclude):
      print'  No exclusion identifier provided, assuming none'
      exclude=''
   filters.append(exclude)
   #print 'Filter List: num',len(filters), filters[3], filters[4], filters[0], filters[1], filters[2]   #DEBUG
   return(filters)


def get_cmdline_method(sigtestlocal):
   method=False
   userinput=raw_input('Anaylize with Dual-Port?  (y/n) ')
   if userinput=='y':
      method=True
   return(method)

# attempt to choose sigtest version
def find_sigtest():
   initLoc=os.getcwd()
   os.chdir(r"C:\Program Files (x86)")
   #os.chdir(r"C:\Program Files")
   progFiles=os.getcwd()
   progDirs=glob.glob('*/')
   os.chdir(initLoc) #get back as soon as possible to prevent messing up directories...
   #help()
   vers=[]
   for dir in progDirs:
      #if "SigTest" in dir:
      if dir.startswith("SigTest"):
         vers.append(dir)
   numVers=len(vers)
   if numVers>1:  #need to selecte
      print "Mulitple SigTest versions installed"
      for idx,ver in enumerate(vers):
         print idx, " -> ", ver.split()[1].strip('\\')
      sigSelect=raw_input("Choose a version: ")
      #test to see if input is an integer
      try:  
         sigSelect=int(sigSelect)
      except:
         exit("I'm Sorry Dave, I'm afraid I can't do that.\nGood-bye")
      #check to see if selection is within range
      if sigSelect<(numVers):
         CallSigTest=progFiles+'\\'+vers[sigSelect]+'SigTest.exe'
      else:
         exit("Invalid Selection, exiting")
   elif numVers==1:  #only one version
      sigSelect=0
      CallSigTest=progFiles+'\\'+vers[sigSelect]+'SigTest.exe'
   else:    #didn't find a version installed
      #exit('No SigTest installation detected in Program Files (x86)')
      CallSigTest=raw_input('Input the path to SigTest.exe: ')
      CallSigTest+=('\\SigTest.exe')
   return(CallSigTest)

#def help(sigtestlocal):  #NEED TO ADD
def help():  #NEED TO ADD
   print'\nThis command line based utlity will batch-process waveform files in the local directory: {0}'.format(os.getcwd())
   print'It works with either Data-Only or Dual-Port modes.'  #does not support both in a single file, SE files
   print"You'll need several things to start a run:"
   print"Sigtest Technology directory & Template File, \nIf it's a Dual-Port template, and if it does embedding (faster than Gen2).\n",
   print"For Dual-Port analysis, the data and clock files must be name the same \nexcept for the Data vs. Clock file identifier.",
   print"An example would be Project_Slot##_Speed_Lane##_D_Sample#.wfm & \nProject_Slot##_Speed_Lane##_C_Sample#.wfm",
   print"When entering the data, clock, and speed filters, it's recommended to \ninclude the separators on boths sides,",
   print"such as _D_ or _Data_, _Clk_ or _Gen3_, etc.  This makes the parsing simpler."
   print"To use Tektronix automated naming, _Math1 and _Math2 can be used as data and clock file identifiers.\n\n"
   print"This has been tested to work on Win7 and Win8. It fails on Win10 after some updates have been applied."
   #exit()
   return()


def run_me():
#add some flags for testing...  -t use filters default, possibly periph, controller, etc defaults
   #inputFlags=parseInput();
   printVerString='sigtest.py version 0.92';
   callSigTest=find_sigtest() #find normally installed versions
   print printVerString
   print callSigTest
   method=get_cmdline_method(callSigTest)                     #Get analysis method

   usrFileTest = raw_input("Are you using a config file? (y/n): ")
   if usrFileTest == 'y':
      config = get_config_file()
      for line in range(len(config)):
         print config[line]
         params = config[line].split(',')
         print params
         tmpltdir = params[0]
         tmplt = params[1]
         if (params[2] == 'y' or params [2] == 'Y'):
            embed = True
         else:
            embed = False
         filters = params[3:]

         dataFileList = getFiles(filters)
         numFiles = run_sigtest(dataFileList, filters, tmpltdir, tmplt, callSigTest, method, embed)
         if line == len(config):
            return()

      #Setup Filters and template directories here
   else:
      tmpltdir,tmplt,embed=get_cmdline_template()           #Get user input for the template
      print tmpltdir, tmplt
      filters = get_filters_cmdline(method)

   #Need to assign config settings for each element in the array (minus element 0, because it is expected to be a header)

      dataFileList = getFiles(filters)                #Get the files to process in a matched list
      numFiles=run_sigtest(dataFileList, filters, tmpltdir, tmplt, callSigTest, method,embed)
      return()





if (__name__=="__main__"):
   global tmpltdir,tmplt,test
   if len(argv)<2:
      help()
   test=False
   #raw_input("Press Enter key to continue")
   #msvcrt.getch()
   run_me()
   exit('  Done.')

