#!/bin/bash
#
# **************************** LICENSE START ***********************************
#
# Copyright 2021 ECMWF. This software is distributed under the terms
# of the Apache License version 2.0. In applying this license, ECMWF does not
# waive the privileges and immunities granted to it by virtue of its status as
# an Intergovernmental Organization or submit itself to any jurisdiction.
#
# ***************************** LICENSE END ************************************
#
# mars_ectrans      USER SERVICES  NOVEMBER 2021 - ECMWF
#
#
#       This shell-script:
#
#          - executes an advanced MARS request (to calculate
#            total precipitation)
#          - sends the data to a remote site using ectrans
#
#       This shell script produces the standard output file
#
#         mars_ectrans.<JOB_ID>.out
#
#       in the working directory, containing the log of the job execution.   
#
#       ATTENTION:  To run this script it is recommended to have an  
#       ==========  ECaccess gateway installed at the remote site!
#                   Alternatively you could use ecaccess.ecmwf.int.
#                   You also need to modify the ectrans command at the
#                   end of the script to use the user-id you have
#                   created/associated at the remote site.
#
#       For more information on ECaccess see
#
#       https://confluence.ecmwf.int/display/ECAC/ECaccess+Home
#
#
#-------------------------------
# setting options for SLURM
#-------------------------------
# Options that are specified within the script file should precede the
# first executable shell command in the file.
# All options, which are case sensitive, are preceded by #SBATCH.
# These lines become active only when the script is submitted
# using the "sbatch" command.
# All job output is written to the workdir directory, by default.
 
 
#SBATCH --qos=ef
 
        # Specifies that your job will run in the queue (Quality Of
        # Service) "nf".
 
#SBATCH --job-name=mars_ectrans
 
        # Assigns the specified name to the request
 
#SBATCH --output=mars_ectrans.%j.out
 
        # Specifies the name and location of STDOUT where %j is the job-id
        # The file will be # written in the workdir directory if it is a
        # relative path. If not given, the default is slurm-%j.out in the
        # workdir.
 
#SBATCH --error=mars_ectrans.%j.out
 
        # Specifies the name and location of STDERR where %j is the job-id
        # The file will be # written in the workdir directory if it is a
        # relative path. If not given, the default is slurm-%j.outin the
        # workdir.
 
#SBATCH --chdir=/scratch/...
 
        # Sets the working directory of the batch script before it is
        # executed.
 
#SBATCH --mail-type=FAIL
         
        # Specifies that an email should be sent in case the job fails.
        # Other options include BEGIN, END, REQUEUE and ALL (any state
        # change).
 
#SBATCH --time=00:30:00
 
        # Specifies that your job my run up to HH:MM:SS of wall clock
        # time. The job will be killed if it exceeds this limit. If
        # time is not defined, the default limit for the queue (qos)
        # will be used.
 
 
#-------------------------------
# setting environment variables
#-------------------------------
 
#export PATH=$PATH:.             # Allows you to run any of your programs or
                                # scripts held in the current directory (not
                                # required if already done in your .user_profile
                                # or .user_kshrc)
set -ev
 
 
module load eclib               # make ATOS utilities available (includes dateincr)
#-------------------------------
# commands to be executed
#-------------------------------
 
#cd $SCRATCHDIR              # All the files created in this directory will be
                                # deleted when the job terminates.
 
 
#--------------------
# MARS  request
#--------------------
#export TRGF=C2024.grib         # define target file
 
#export TMPDIR=$SCRATCHDIR       # set TMPDIR, where the MARS fieldsets are
                                # hold to (the much larger) SCRATCHDIR
 
# The following request retrieves the total precipitation for the 24
# hour period between 6UTC on DATE-1 to 6UTC on DATE. To avoid
# problems linked to model spin-up effects, the fields are retrieved
# from the 12 UTC forecast at DATE-2:
 
#export DATE=20130501            # set DATE
 
#export FCDATE=$(dateincr -d $DATE -2)  
                                # set FCDATE to DATE -2 by using the
                                # dateincr command
 
# Could use:
 
#export FCDATE=$(date -d "${DATE} -2 days" +%Y%m%d)
 
# cat is used to read the MARS request from the input stream and to
# write it to the unique file 'request_$$'.  cat reads line by line
# until it reaches a line which starts with EOF. 
 
# cat >request_$$ <<EOF        
# retrieve,                   # retrieve large scale precipitation 12h+18
#     class    = od,
#     type     = fc,
#     levtype  = sfc,
#     param    = 142,
#     date     = $FCDATE,
#     time     = 12,
#     step     = 18,
#     grid     = 2.5/2.5,
#     area     = 75/-27.5/32.5/45,
#     fieldset = lsr18
# retrieve,                   # retrieve convective precipitation 12h+18
#     param    = 143,
#     fieldset = cvr18
# retrieve,                   # retrieve large scale precipitation 12h+42
#     step     = 42,
#     param    = 142,
#     fieldset = lsr42
# retrieve,                   # retrieve convective precipitation 12h+42
#     param    = 143,
#     fieldset = cvr42
# compute,                    # compute the total precipation
#     formula  = "(lsr42+cvr42)-(lsr18+cvr18)",
#     fieldset = totr6to6
# write,                      # write the result to target file
#     fieldset = totr6to6,
#     target   = "$TRGF"
# EOF
 
# mars request_$$
 
cat >request_$$ <<EOF        
retrieve,
class=od,
date=20230101/to/20231231,
domain=g,
expver=1,
param=234.140/237.140/238.140/245.140/249.140,
step=12/to/36/by/3,
stream=wave,
time=00:00:00,
type=fc,
accuracy=ac,
area=43.84/-4.51/43.46/-3.16,
grid=0.125/0.125, 
target=prueba.grib
EOF
 
mars request_$$

if [ $? != 0 ]                          # Check MARS exit code.
then
      echo " The MARS request failed."
      exit 1
fi
 
ls -l $TRGF
 
#----------------------------------------------------------------
#
#                           W A R N I N G
#
# Before executing this job: 
# 
#       a) make sure your remote host is running a local ECaccess
#          gateway (or use the ECMWF gateway ecaccess.ecmwf.int)
#       b) make sure your ECMWF user-id is associated with a local
#          (Member State) user-id; this can be done using your
#          gateway's web-interface
#       c) change the following in the 'ectrans' line below:
#
#   ms_uid             to be your user id on your local (Member
#                      State) host
#
#   your_gateway       to be your local ECaccess gateway
#
#   and uncomment the lines below with the ectrans command
#
# To get a command summary, type: ectrans -help
#-----------------------------------------------------------------
 
#module load ecaccess        # Makes ectrans available in the $PATH
 
# Uncomment the following lines after setting your_gateway and ms_uid
#ectrans -gateway boaccess.ecmwf.int  -remote esp8164@genericFtp \
#        -source $TRGF -verbose -onfailure
 
 
#-------------------------------
# tidy up by deleting unwanted files
#-------------------------------
# This is done automatically when using $SCRATCHDIR.
 
exit 0
 
# End of example job 'mars_ectrans'
