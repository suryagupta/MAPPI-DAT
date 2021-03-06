__author__ = 'surya'

import os
import subprocess
from datetime import datetime
from Error_handle import ErrorHandling
from Filter_Analysis import Processing, CalculatingPositives, MergingAndFinalFiltration
from GeneralMethods import GetRPath
from Plotting_graph import PlottingDist

""" the input of the data will be 1 xml file
containing the number of files, each corresponds to different prey set but all together will be for one bait
So the input should be a folder containing:
1. xml file
2. all protein annotation file
3. one text file explaning which subfile corresponds to which protein annotation file
and if multiple baits are present than it should also refer bait in first column
and the name of the file should be

        filelinkage.txt                 """

""" Bait    file    proteinAnnotationfile"""


###################################################################################################################################################
## data processing#
## handling linkage file

def processAnalysisNormalization(LinkageFile,FolderPath,xmlfile,analy,cut,gen,ns_list,s_list,QuartFil,allprocessedFile,
                            apecific_file,aspecificPresent,PCpresent,PCthreshold,Reprocessing):
    print "Started with Processing................"
    start= datetime.now()
    print start
    #######################################
    ## handling with the list provided by the ns_list and s_list through gui
    nslist=ns_list.split(",")
    slist=s_list.split(",")

    ######################################
    ## get R path
    Rpath= GetRPath.RPathname()
    # print Rpath
    # print Rpath

###################################################################################################
###########define columns for each Quantification parameter#########################################

    if allprocessedFile:  ## this is the option if says yes that means process all the files else just process the integral intensity file
        colDic = {11: "Particle_Count", 12: "MeanArea", 13: "GrayValue", 14: "MeanGrayValue", 15: "MeanIntegralInt",
                  16: "AreaFraction", 17: "IntegralIntensity"}  ## defines the column name for each paprametr
    else:
        colDic = {17: "IntegralIntensity", 11: "Particle_Count",
                  18: "Residuals"}  ## if not all but atleast 3 files will be processed




################# steps which are common to both the analysis
    linkageDic, plate2subfolder, plate_tfileDic, bait2PlateList = Processing.linkageDic(LinkageFile)  ## create dic for linkage file

    """where:
    linkageDic = {subfolder: [bait,proteinfile,[plate1,plate2....]]}
    plate2subfolder= (plate:subfolder)
    bait2PlateList= bait1:[palte1plate2...];bait2:[p1,p2,p3...]"""

    path = Processing.FolderCreationOnlyBait(FolderPath,bait2PlateList)  ## create folder specific to each bait e.g link +"/MAPPIDAT_OutPut"
    AspecificDic = {}
    Pannotation = {}
    Positive_count=0
    #################################################################################################################
####### if first time handling data
##############################################################################################
    if not Reprocessing:

###################################################################################
## parsing the linkageFile and creating folders for each of the bait and the subfolders.
###################################################################################
        if aspecificPresent:
            AspecificDic=Processing.GetAspecifics(apecific_file)
        else:
            AspecificDic={}




#####################################################################################################################################################
##################################### Parsing XML FILE ##################################################################################
#####################################################################################################################################################

        pplot=[]
        work = []
        ln=[]
        count=0
        for line in open(xmlfile):
            sp = line.split()
            if sp[0] == "<Worksheet":
                if len(work) != 0:
                    wrt.writelines(ln)
                    count+=1
                    wrt.close()
                    TfileName=os.path.basename(linkageDic[plate2subfolder[platename]][1])
                    if TfileName not in Pannotation:
                        Pannotation[TfileName]=linkageDic[plate2subfolder[platename]][1]
                    PDic= Processing.proteinDic(linkageDic[plate2subfolder[platename]][1]) ## making protein dic for each bait plate
                    name= Processing.AddProteinName(outName,PDic,AspecificDic,MergeFileNames) ## adding protein unique id to each protin interaction using the protein dic define above and merge in one file
                platename=sp[1].split("=")[1].strip(">").strip('""')
                MergeFileNames=[path+"/"+linkageDic[plate2subfolder[platename]][0]+"/Processing/AllPlatesOnlyControl.txt",
                                path+"/"+linkageDic[plate2subfolder[platename]][0]+"/Processing/AllPlatesWithoutControl.txt",
                                path+"/"+linkageDic[plate2subfolder[platename]][0]+"/Processing/AllPlatesWithControl.txt"]
                outName= path+"/"+linkageDic[plate2subfolder[platename]][0]+"/Processing/"+platename.strip('""') ## c//..../dataprocessig/bait/Processing/file(wot.txt)
                fileName=outName+".txt"
                work.append(outName)
                wrt = open(fileName, 'w')
                ln = []
            elif sp[0] == "<Row>":
                    ln.append("\n")
                    wrt.writelines(ln)
                    count+=1
                    ln = []
            elif sp[0] == "<Data" or sp[0]== "<Cell><Data":
                    ln.append(sp[1].split(">")[1].split("<")[0])
                    ln.append("\t")
        # if count==0:
        #     ErrorHandling.IO_prob("This is not a valid file.. please enter XML file only..")
        #
        wrt.writelines(ln)
        wrt.close()

    ## to also create plate file with protein name and merge them in main file
        if len(work)!=0:
            TfileName=os.path.basename(linkageDic[plate2subfolder[platename]][1])
            if TfileName not in Pannotation:
                Pannotation[TfileName]=linkageDic[plate2subfolder[platename]][1] ## T1: path to T plate
            PDic= Processing.proteinDic(linkageDic[plate2subfolder[platename]][1])
            name= Processing.AddProteinName(outName,PDic,AspecificDic,MergeFileNames) ## make a file without control and

########################################################################################################################################################
## ##################### if reprocessing the data ################################################
    else:

        pplot = []
        #get Aspecifc from the main file
        AspecificDic=Processing.GetAspecificFromReprocessedData(xmlfile)
        # create a protein annotation file
        for subfolder in linkageDic:
            tFileName=os.path.basename(linkageDic[subfolder][1])
            if tFileName not in Pannotation:
                Pannotation[tFileName]=linkageDic[subfolder][1] # dic which have t-file name "T1cum": path to file
        # path=Processing.FolderCreation(FolderPath,xmlfile)
        baitName=bait2PlateList.keys()[0]
        Processing.copyRawFile2MappiDatFolder(FolderPath,baitName,xmlfile)
        # bait2PlateList=["Bait"]
    print "Finished Preprocessing .............."
    print "Normalization Started ...................."

#####################################################################################################################################################
##################################### Normalization ##################################################################################
#####################################################################################################################################################



    for eachBait in bait2PlateList:
        print " Started with bait ",eachBait
        # merge the control File
        nsrep=len(nslist)
        srep=len(slist)
        mainPath=path+"/"+eachBait
        Processing.MergeFiles(mainPath+"/Processing/AllPlatesOnlyControl",{17: "IntegralIntensity"},nslist,slist) ## this will merge all intensity,for controls together

        InputFileName=mainPath+"/Processing/"
        Outputfilename=mainPath+"/Analysis/AllPlatesWithoutControlNormalized.txt"
        # print Outputfilename
        fileRP= Rpath+" --vanilla NormalizationWithaov.R --InputFile="+ InputFileName\
                +" --OutputFile="+Outputfilename+" --nsrep="+str(nsrep)+" --srep="+str(srep)+" > OutputRP1 2> ErrorRp1" #+" cutoff="+str(cut)+" gene="+str(gen)+\
        # fileRP= '\"'+ fileRP +'\"'
#        print fileRP
        os.system(fileRP)
        print "Finished Normalization.."
        ##################################################################################################
        # now merge the files for each bait
        File2BMerge=mainPath+"/Analysis/AllPlatesWithoutControlNormalized"
        Processing.MergeFiles(File2BMerge,colDic,nslist,slist) ## this will merge all intensity,PC and residual files together

        print "Analysis started...."
        pplot.append(PlottingDist.plot(File2BMerge,len(nslist),len(slist)))
        ###################################################################################################
        if analy:
            # namer="\'"+File2BMerge+"\'"
            fileRP= Rpath+" --vanilla NewAnalysisMappiDat.R --file="+File2BMerge \
                    +" --nsrep="+str(nsrep)+" --srep="+str(srep)+" > OutputRP2 2> ErrorRp2" #+" cutoff="+str(cut)+" gene="+str(gen)+\

            # fileRP= '\"'+ fileRP +'\"'
#            print fileRP
            os.system(fileRP)
            ## apply particle count filtration
            if not PCpresent:
                pcfilterOutliers=[]
            else:
                pcfilterOutliers=CalculatingPositives.PCLabelledOutLiers(File2BMerge,nsrep,srep,PCthreshold)
            ## if asked than apply quartile filtration
            if not QuartFil:
                QuartFilOutliers=[]
            else:
                QuartFilOutliers= CalculatingPositives.analysis_quartile(File2BMerge,nsrep,srep,nslist,slist)  ## apply one more filtration on the basis of the quartile method
            print "total quartile outlier found are : ",len(QuartFilOutliers)
            ## separate each col from the merged ID and intensity,residual,PC
            Positive_count,finalFilteredFileName=MergingAndFinalFiltration.ApplyFiltrationAddRawData(File2BMerge,cut,gen,nsrep,srep,QuartFilOutliers,pcfilterOutliers) ##

            ## SOFTWARE FILE :    also create one more file as a input for the software but all of them for each bait.
            MergingAndFinalFiltration.CreateSoftwareInputFile(File2BMerge)
            ###################################################################################################

    print " Analysis Done !! "
    end1=datetime.now()-start
    print "time taken till now is ", end1
    return (path,Positive_count,pplot,Pannotation,bait2PlateList,plate2subfolder,AspecificDic,linkageDic,plate_tfileDic)
