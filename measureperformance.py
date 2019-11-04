#!/bin/python3

####################################
# SMB vs NFS File Performance Test #
# Made by Ivar Slotboom aka f13rce #
# Made for Large Systems - OS3/SNE #
####################################

# Imports
import time
import os
import argparse
#import subprocess
import shutil

# Globals
startTime = time.asctime(time.localtime(time.time())).replace(" ", "_").replace(":", ".")
resultsFileName = "results_FILESTORAGE_{}.csv".format(startTime)
fileStorages = ["SMB", "NFS"]

fileSizes  = ["1KB", "10KB", "100KB", "1MB", "10MB", "25MB"]
fileCounts = [100,   25,     10,      10,    5,      2     ]
#fileCounts = [10000, 2500,   1000,    100,   50,     25,]
ddCommand = "dd if=/dev/urandom of=PATH/FILESIZE/file_INDEX bs=FILESIZE count=1 2>&1" # Macros will be replaced
fileDirectory = "files"

# Logging
def Log(aText):
	#curTime = str(time.asctime(time.localtime(time.time())))
	#print("LOG [{}]: {}".format(curTime, aText))
	print("LOG: {}".format(aText))

# Funcs
def GetTime():
	return int(round(time.time() * 1000))

def PerformTest(aFileSize, aDestinationPath, aTestID, aFileStorage):
	cmd = "cp {}/{}/file_{} {}/file_{}".format(fileDirectory, aFileSize, aTestID, aDestinationPath, aTestID)
	start = GetTime()
	os.system(cmd)
	end = GetTime()
	StoreResult(start, end, aTestID, aFileStorage)
	return (end - start)

def StoreResult(aStartTime, aEndTime, aIndex, aFileStorage):
	with open(resultsFileName.format("FILESTORAGE", aFileStorage), "a") as f:
		f.write("{}, {}, {}, {}\n".format(aIndex, aEndTime - aStartTime, aStartTime, aEndTime))

# Main
def main():
	# Parse arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("-n", "--nfsoutput", help="Path where to store the files for NFS")
	parser.add_argument("-s", "--smboutput", help="Path where to store the files for SMB")
	parser.add_argument("-c", "--create", help="Create the files")

	args = parser.parse_args()
	Log("Found args: {}".format((repr(args))))

	if not args.nfsoutput or not args.smboutput:
		Log("Error: One or more required arguments are missing. Ask for --help for info.")
		return 1

	# Start with clean log files
	for fileStorage in fileStorages:
		with open(resultsFileName.format("FILESTORAGE", fileStorage), "w") as f:
			f.truncate()
			f.write("Test ID, File size, Start time, End Time\n")

	# Log our intentions
	Log("Filesizes that will be tested: {}".format(repr(fileSizes)))

	# Create the files if necessary
	if args.create != None:
		# Ensure the directories exist
		try:
			for i in range(len(fileSizes)):
				directory = "{}/{}".format(fileDirectory, fileSizes[i])

				# Cleaning up previous tests
				#Log("Cleaning up directory \"{}\" if it exists...".format(directory))
				if os.path.exists(directory):
					shutil.rmtree(directory)
				os.makedirs(directory)

				# Create the files
				#Log("Creating {} files of {} in {}...".format(fileCounts[i], fileSizes[i], directory))
				for j in range(fileCounts[i]):
					cmd = ddCommand
					cmd = cmd.replace("PATH", "{}".format(fileDirectory))
					cmd = cmd.replace("FILESIZE", "{}".format(fileSizes[i]))
					cmd = cmd.replace("INDEX", "{}".format(j))
					#Log("Command to create this file: {}".format(cmd))
					os.system(cmd)
		except:
			Log("Detected keyboard or something went wrong - will quit.")
			return

	for fileStorage in fileStorages:
		# Hacky solution :(
		dest = args.nfsoutput
		if fileStorage == "SMB":
			dest = args.smboutput

		# Run test
		Log("-----------------------------------------------")
		Log("Testing performance of {}...".format(fileStorage))
		Log("-----------------------------------------------")

		for i in range(len(fileSizes)):
			Log("Performing tests for {} by copying {} {} files...".format(fileStorage, fileCounts[i], fileSizes[i]))
			total = 0
			for j in range(fileCounts[i] - 1):
				total += PerformTest(fileSizes[i], dest, (j+1), fileStorage)
			Log("Total time elapsed for {} with {} {} files: {}ms".format(fileStorage, fileCounts[i], fileSizes[i], total))
		Log("All done with the tests! Results have been saved to \"{}\"".format(resultsFileName.replace("FILESTORAGE", fileStorage)))

	return 0

if __name__ == "__main__":
    main()
